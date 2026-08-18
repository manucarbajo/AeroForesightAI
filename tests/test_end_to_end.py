from uuid import uuid4

from src.agents.orchestrator_node import OrchestratorNode
from src.config_loader import build_initial_state
from src.market.market_node import MarketNode
from src.models.agent_models import AgentResponse, StateChange
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, RoundResult
from src.orchestration.environment_node import EnvironmentNode
from src.validation import validate_state


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
                factor_id=factor_id, proposed_state=new_state, reasoning="Mock state change"
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
    state.clock.max_ticks = 1

    validate_state(state)

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode(prefer_agent_order=["regulator", "provider", "consumer"])

    while state.clock.current_tick < state.clock.max_ticks:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_tick

        # Mock-Responses statt LLM
        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(
                RoundResult(
                    round_number=round_number,
                    agent_responses=[response],
                    events=[event],
                    environment_snapshot=state.environment,
                )
            )

        state = market.invoke(state)
        state = environment.invoke(state)

    validate_state(state)

    assert state.clock.current_tick == 1
    assert len(state.event_log) > 0
    assert len(state.price_history) == 1
    assert len(state.round_results) > 0


def test_end_to_end_multiple_rounds():
    """Testet einen vollständigen Simulationslauf mit mehreren Runden ohne LLM."""
    state = build_initial_state()
    state.clock.max_ticks = 3

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode(prefer_agent_order=["regulator", "provider", "consumer"])

    while state.clock.current_tick < state.clock.max_ticks:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_tick

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(
                RoundResult(
                    round_number=round_number,
                    agent_responses=[response],
                    events=[event],
                    environment_snapshot=state.environment,
                )
            )

        state = market.invoke(state)
        state = environment.invoke(state)

    assert state.clock.current_tick == 3
    assert len(state.price_history) == 3


def test_end_to_end_frozen_cib_loaded():
    """Frozen CIB matrix is available from build_initial_state without LLM extraction."""
    state = build_initial_state()
    assert state.cib_matrix is not None
    assert state.cib_matrix.is_complete
    assert len(state.cib_matrix.cells) == 168


def test_end_to_end_cib_unchanged_after_rounds():
    """Simulation rounds must not mutate the frozen CIB matrix."""
    state = build_initial_state()
    state.clock.max_ticks = 2
    original_dump = state.cib_matrix.model_dump() if state.cib_matrix else None

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode()

    while state.clock.current_tick < state.clock.max_ticks:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_tick

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(
                RoundResult(
                    round_number=round_number,
                    agent_responses=[response],
                    events=[event],
                    environment_snapshot=state.environment,
                )
            )

        state = market.invoke(state)
        state = environment.invoke(state)

    assert state.cib_matrix is not None
    assert state.cib_matrix.model_dump() == original_dump


def test_end_to_end_output_files(tmp_path):
    """Testet ob alle Output-Dateien korrekt geschrieben werden."""
    import json

    from src.output_writer import (
        save_cib_matrix,
        save_event_log,
        save_price_history,
        save_round_history,
        save_segment_analysis,
    )

    state = build_initial_state()
    state.clock.max_ticks = 1

    orchestrator = OrchestratorNode(state.agents)
    market = MarketNode()
    environment = EnvironmentNode()

    while state.clock.current_tick < state.clock.max_ticks:
        state = orchestrator.invoke(state)
        round_number = state.clock.current_tick

        for agent_id in ["consumer", "provider", "regulator"]:
            response = _make_mock_response(agent_id, round_number, state)
            event = _make_mock_event(agent_id, round_number)
            state.event_log.append(event)
            state.round_results.append(
                RoundResult(
                    round_number=round_number,
                    agent_responses=[response],
                    events=[event],
                    environment_snapshot=state.environment,
                )
            )

        state = market.invoke(state)
        state = environment.invoke(state)

    # In tmp_path speichern
    save_event_log(state.event_log, filename=str(tmp_path / "event_log.json"))
    save_price_history(state.price_history, filename=str(tmp_path / "price_history.json"))
    save_round_history(state.round_results, filename=str(tmp_path / "round_history.json"))
    save_segment_analysis(state.round_results, filename=str(tmp_path / "segment_analysis.json"))
    save_cib_matrix(state, filename=str(tmp_path / "cib_matrix.json"))

    # Prüfe ob Dateien existieren und valides JSON enthalten
    for filename in [
        "event_log.json",
        "price_history.json",
        "round_history.json",
        "segment_analysis.json",
        "cib_matrix.json",
    ]:
        filepath = tmp_path / filename
        assert filepath.exists(), f"{filename} wurde nicht erstellt"
        with open(filepath) as f:
            data = json.load(f)
        assert data is not None, f"{filename} ist leer"
