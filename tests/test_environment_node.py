from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from src.models.cib_models import CIBMatrix
from src.models.agent_models import AgentConfig
from src.models.enums import AgentType
from src.models.population_models import PopulationConfig, ConsumerSegment, DistributionConfig
from src.config_loader import load_properties_config
from src.models.state_models import SimulationState, SimulationClock, EnvironmentState, FactorState, SimulationConfig, \
    LLMConfig
from src.nodes.environment_node import (
    EnvironmentAgentNode,
    PopulationShift,
    PopulationUpdateResult,
    MAX_SHARE_CHANGE_PER_ROUND,
)


@pytest.fixture
def sample_population_config() -> PopulationConfig:
    """Erstelle eine Test-Population-Config."""
    return PopulationConfig(
        segments=[
            ConsumerSegment(
                id="business",
                name="Geschäftsreisende",
                share=0.3,
                description="Häufige Flieger, unelastisch"
            ),
            ConsumerSegment(
                id="leisure",
                name="Freizeit",
                share=0.5,
                description="Preissensibl, elastisch"
            ),
            ConsumerSegment(
                id="eco_conscious",
                name="Umweltbewusst",
                share=0.2,
                description="Flight Shaming Anhänger"
            ),
        ],
        total_population=1000,
    )


@pytest.fixture
def sample_state(sample_population_config: PopulationConfig) -> SimulationState:
    """Erstelle einen Test-SimulationState."""
    config = SimulationConfig(
        name="Test",
        description="Test simulation",
        llm=LLMConfig(),
    )
    clock = SimulationClock(current_tick=1, max_ticks=10)

    environment = EnvironmentState(
        factors={
            "F1": FactorState(
                id="F1",
                name="Mobilitätsbedürfnis",
                description="Nachfrage nach Mobilität",
                current_state="F1.1",
                possible_states={"F1.1": "Boom", "F1.2": "Stagnation"}
            )
        }
    )

    # Consumer Agent mit Population Config
    consumer_agent = AgentConfig(
        id="consumer",
        name="Consumer",
        agent_type=AgentType.CONSUMER,
        description="Consumer agent",
        goals=[],
        population_config=sample_population_config,
    )

    state = SimulationState(
        config=config,
        properties=load_properties_config(),
        clock=clock,
        environment=environment,
        agents=[consumer_agent],
        cib_matrix=None,
    )

    return state


class TestEnvironmentAgentNode:
    """Tests für EnvironmentAgentNode."""

    def test_creation_without_llm(self):
        """Erstelle einen Node ohne LLM."""
        node = EnvironmentAgentNode(llm=None)
        assert node.llm is None

    def test_creation_with_llm(self):
        """Erstelle einen Node mit LLM."""
        mock_llm = MagicMock()
        node = EnvironmentAgentNode(llm=mock_llm)
        assert node.llm is mock_llm

    def test_extract_population_config(self, sample_state: SimulationState):
        """Extrahiere Population Config aus State."""
        node = EnvironmentAgentNode()
        pop_config = node._extract_population_config(sample_state)
        assert pop_config is not None
        assert len(pop_config.segments) == 3

    def test_invoke_without_llm(self, sample_state: SimulationState):
        """Invoke mit Fallback (ohne LLM)."""
        node = EnvironmentAgentNode(llm=None)
        new_state = node.invoke(sample_state)

        # State sollte zurückgegeben werden
        assert new_state is not None
        # Ohne LLM sollten keine Änderungen sein
        pop_config = node._extract_population_config(new_state)
        assert pop_config is not None

    def test_population_shift_constraints(self, sample_population_config: PopulationConfig):
        """Teste Constraint-Anwendung auf Shifts."""
        node = EnvironmentAgentNode()

        # Versuche großen Shift (sollte begrenzt werden)
        shift = PopulationShift(
            segment_id="business",
            segment_name="Geschäftsreisende",
            old_share=0.3,
            new_share=0.5,  # 20% Shift
            shift_amount=0.2,
            reasoning="Large shift"
        )

        constrained = node._apply_shift_constraints(shift, sample_population_config)

        # Max shift sollte angewendet sein
        assert constrained.clamped is True or constrained.shift_amount <= MAX_SHARE_CHANGE_PER_ROUND

    def test_parse_llm_response(self):
        """Teste LLM Response Parsing."""
        node = EnvironmentAgentNode()

        response = """
        Folgende Verschiebungen erwarten wir:
        {
            "segments": [
                {"id": "business", "new_share": 0.32, "reasoning": "Wachstum"}
            ],
            "overall_reasoning": "Positive trends"
        }
        """

        result = node._parse_llm_response(response)
        assert result["segments"] is not None
        assert result["overall_reasoning"] is not None


class TestPopulationShift:
    """Tests für PopulationShift Model."""

    def test_create_shift(self):
        """Erstelle einen Shift."""
        shift = PopulationShift(
            segment_id="test",
            segment_name="Test Segment",
            old_share=0.3,
            new_share=0.35,
            shift_amount=0.05,
            reasoning="Test reason"
        )

        assert shift.segment_id == "test"
        assert shift.shift_amount == 0.05
        assert shift.clamped is False


class TestPopulationUpdateResult:
    """Tests für PopulationUpdateResult Model."""

    def test_empty_result(self):
        """Erstelle leeres Result."""
        result = PopulationUpdateResult(round_number=1)
        assert result.round_number == 1
        assert len(result.shifts) == 0

    def test_result_with_shifts(self):
        """Erstelle Result mit Shifts."""
        shift = PopulationShift(
            segment_id="test",
            segment_name="Test",
            old_share=0.3,
            new_share=0.35,
            shift_amount=0.05,
            reasoning="Test"
        )

        result = PopulationUpdateResult(
            round_number=2,
            shifts=[shift]
        )

        assert len(result.shifts) == 1
        assert result.shifts[0].segment_id == "test"