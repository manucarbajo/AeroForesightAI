import pytest
from uuid import uuid4

from src.models.agent_models import AgentConfig, AgentProfile
from src.models.enums import AgentType
from src.models.state_models import SimulationState, SimulationClock, EnvironmentState, FactorState
from src.models.state_models import SimulationState, SimulationClock, EnvironmentState, FactorState, SimulationConfig
from src.models.event_models import EventLogEntry, EventType
from src.nodes.agent_node import AgentNode


@pytest.fixture
def base_state():
    return SimulationState(
        run_id="test_run",
        config=SimulationConfig(run_id="test_run", name="test", description="test"),
        agents=[],
        clock=SimulationClock(current_tick=1, max_ticks=5),
        environment=EnvironmentState(
            factors={
                "F1": FactorState(id="F1", name="F1", description="desc", current_state="F1.1", possible_states={"F1.1": "A", "F1.2": "B"}),
                "F2": FactorState(id="F2", name="F2", description="desc", current_state="F2.1", possible_states={"F2.1": "A", "F2.2": "B"}),
                "F3": FactorState(id="F3", name="F3", description="desc", current_state="F3.1", possible_states={"F3.1": "A", "F3.2": "B"})
            }
        ),
        market_metrics={"ticket_price": 100.0, "cost_pressure": 110.0},
        event_log=[
            EventLogEntry(
                id=str(uuid4()),
                round_number=0,
                source_agent="regulator",
                event_type=EventType.POLICY_CHANGE,
                description="Test event"
            )
        ]
    )


def test_agent_node_filters_factors_by_profile(base_state):
    config = AgentConfig(
        id="test_agent",
        name="Test",
        agent_type=AgentType.CONSUMER,
        description="Test",
        goals=[],
        profile=AgentProfile(
            observes=["factors F1,F3"]
        )
    )
    node = AgentNode(config, llm=lambda x: "{}")
    factors_str = node._format_factors(base_state)
    assert "F1 |" in factors_str
    assert "F3 |" in factors_str
    assert "F2 |" not in factors_str


def test_agent_node_filters_market_metrics_by_profile(base_state):
    config = AgentConfig(
        id="test_agent",
        name="Test",
        agent_type=AgentType.PROVIDER,
        description="Test",
        goals=[],
        profile=AgentProfile(
            observes=["cost_pressure"]
        )
    )
    node = AgentNode(config, llm=lambda x: "{}")
    metrics_str = node._format_market_metrics(base_state)
    assert "cost_pressure" in metrics_str
    assert "ticket_price" not in metrics_str


def test_agent_node_filters_event_log_by_profile(base_state):
    config = AgentConfig(
        id="test_agent",
        name="Test",
        agent_type=AgentType.REGULATOR,
        description="Test",
        goals=[],
        profile=AgentProfile(
            observes=["factors F1"]
        ) # event_log_recent is missing
    )
    node = AgentNode(config, llm=lambda x: "{}")
    events_str = node._format_recent_events(base_state)
    assert "Event log not observed" in events_str
    assert "Test event" not in events_str


def test_agent_node_adds_must_not_output_to_constraints(base_state):
    config = AgentConfig(
        id="test_agent",
        name="Test",
        agent_type=AgentType.CONSUMER,
        description="Test",
        goals=[],
        constraints=["Be nice"],
        profile=AgentProfile(
            must_not_output=["ticket_price", "booking_rate"],
            may_propose=["events"]
        )
    )
    # Using a dummy prompt file approach would require mocking _load_prompt_template
    # We can just test the internal prompt generation wrapper if we mock the template
    node = AgentNode(config, llm=lambda x: "{}")
    
    # Temporarily monkeypatch to test formatting
    original_load = node._load_prompt_template
    node._load_prompt_template = lambda: "{constraints}"
    prompt = node._build_prompt(base_state)
    node._load_prompt_template = original_load
    
    assert "Be nice" in prompt
    assert "MUST NOT OUTPUT: ticket_price, booking_rate" in prompt
    assert "MAY PROPOSE ONLY: events" in prompt

def test_agent_node_enforces_may_propose_state_changes(base_state):
    config = AgentConfig(
        id="test_regulator",
        name="Regulator",
        agent_type=AgentType.REGULATOR,
        description="Test",
        goals=[],
        profile=AgentProfile(
            may_propose=["factor_state F2"]
        )
    )
    node = AgentNode(config, llm=lambda x: "{}")
    payload = [
        {"factor_id": "F2", "proposed_state": "F2.2", "reasoning": "Valid"},
        {"factor_id": "F1", "proposed_state": "F1.2", "reasoning": "Invalid"}
    ]
    changes = node._parse_state_changes(payload, base_state)
    assert len(changes) == 1
    assert changes[0].factor_id == "F2"


def test_agent_node_includes_depends_on_block(base_state):
    config = AgentConfig(
        id="regulator",
        name="Regulator",
        agent_type=AgentType.REGULATOR,
        description="Test",
        goals=[],
        profile=AgentProfile(
            observes=["factors F2", "event_log_recent"],
            depends_on=["provider.events", "consumer.booking_rate"],
        ),
    )
    node = AgentNode(config, llm=lambda x: "{}")
    original_load = node._load_prompt_template
    node._load_prompt_template = lambda: "{depends_on_block}"
    prompt = node._build_prompt(base_state)
    node._load_prompt_template = original_load

    assert "Profile dependencies" in prompt
    assert "provider.events" in prompt
    assert "consumer.booking_rate" in prompt
