import pytest
from unittest.mock import MagicMock
from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse, StateChange
from src.models.event_models import EventLogEntry, RoundResult
from src.models.enums import EventType
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.nodes.cib_extractor_node import CIBExtractorNode
from src.nodes.agent_node import AgentNode
from src.validation import validate_state
from uuid import uuid4


def _make_mock_response(agent_id: str, round_number: int, state) -> AgentResponse:
    """Erstellt eine Mock-AgentResponse ohne LLM."""
    factor_id = list(state.environment.factors.keys())[0]
    factor = state.environment.factors[factor_id]
    new_state = list(factor.possible_states.keys())[0]

    return AgentResponse(
        agent_id=agent_id,
        round_number=round_number,
        reasoning=f"Mock reasoning von {agent_id}",
        actions=[f"mock_action_{agent_id}"],
        state_changes=[
            StateChange(
                factor_id=factor_id,
                proposed_state=new_state,
                reasoning="Mock state change"
            )
        ],
        segment_analysis={"mock_segment": "mock reaction"} if agent_id == "consumer" else {},
    )


def _make_mock_event(agent_id: str, round_number: int) -> EventLogEntry:
    return EventLogEntry(
        id=str(uuid4()),
        round_number=round_number,
        source_agent=agent_id,
        event_type=EventType.DEMAND_SHIFT,
        description=f"Mock event von {agent_id} in Runde {round_number}",
        affected_factors=["F1", "F2"],
    )


def test_end_to_end_single_round():
    """Testet einen vollständigen Simulationslauf mit einer Runde ohne LLM."""
    state = build_initial_state()
    state.clock.max_rounds = 1

    validate_state(state)

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode(prefer_agent_order=["regulator", "provider", "consumer"])

    while state.clock.current_round < state.clock.max_rounds:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_round

        # Mock-Responses statt LLM
        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(RoundResult(
                round_number=round_number,
                agent_responses=[response],
                events=[event],
                environment_snapshot=state.environment,
            ))

        state = market.invoke(state)
        state = environment.invoke(state)

    validate_state(state)

    assert state.clock.current_round == 1
    assert len(state.event_log) > 0
    assert len(state.price_history) == 1
    assert len(state.round_results) > 0


def test_end_to_end_multiple_rounds():
    """Testet einen vollständigen Simulationslauf mit mehreren Runden ohne LLM."""
    state = build_initial_state()
    state.clock.max_rounds = 3

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode(prefer_agent_order=["regulator", "provider", "consumer"])

    while state.clock.current_round < state.clock.max_rounds:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_round

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(RoundResult(
                round_number=round_number,
                agent_responses=[response],
                events=[event],
                environment_snapshot=state.environment,
            ))

        state = market.invoke(state)
        state = environment.invoke(state)

    assert state.clock.current_round == 3
    assert len(state.price_history) == 3


def test_end_to_end_cib_extraction():
    """Testet ob CIBExtractorNode nach der Simulation eine Matrix erstellt."""
    state = build_initial_state()
    state.clock.max_rounds = 2

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode()
    cib_extractor = CIBExtractorNode()

    while state.clock.current_round < state.clock.max_rounds:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_round

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(RoundResult(
                round_number=round_number,
                agent_responses=[response],
                events=[event],
                environment_snapshot=state.environment,
            ))

        state = market.invoke(state)
        state = environment.invoke(state)

    state = cib_extractor.invoke(state)

    assert state.cib_matrix is not None
    assert len(state.cib_matrix.entries) > 0
    assert state.cib_matrix.round_generated == 2


def test_end_to_end_output_files(tmp_path):
    """Testet ob alle Output-Dateien korrekt geschrieben werden."""
    import json
    from src.output_writer import (
        save_event_log,
        save_price_history,
        save_round_history,
        save_segment_analysis,
        save_cib_matrix,
    )
    from src.nodes.cib_extractor_node import CIBExtractorNode

    state = build_initial_state()
    state.clock.max_rounds = 1

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode()

    while state.clock.current_round < state.clock.max_rounds:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_round

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(RoundResult(
                round_number=round_number,
                agent_responses=[response],
                events=[event],
                environment_snapshot=state.environment,
            ))

        state = market.invoke(state)
        state = environment.invoke(state)

    state = CIBExtractorNode().invoke(state)

    # In tmp_path speichern
    save_event_log(state.event_log, filename=str(tmp_path / "event_log.json"))
    save_price_history(state.price_history, filename=str(tmp_path / "price_history.json"))
    save_round_history(state.round_results, filename=str(tmp_path / "round_history.json"))
    save_segment_analysis(state.round_results, filename=str(tmp_path / "segment_analysis.json"))
    save_cib_matrix(state, filename=str(tmp_path / "cib_matrix.json"))

    # Prüfe ob Dateien existieren und valides JSON enthalten
    for filename in ["event_log.json", "price_history.json", "round_history.json", "segment_analysis.json", "cib_matrix.json"]:
        filepath = tmp_path / filename
        assert filepath.exists(), f"{filename} wurde nicht erstellt"
        with open(filepath) as f:
            data = json.load(f)
        assert data is not None, f"{filename} ist leer"