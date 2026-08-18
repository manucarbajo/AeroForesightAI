from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse, StateChange
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, RoundResult
from src.orchestration.environment_node import EnvironmentNode


def _make_response(agent_id: str, state_changes: list[StateChange] = None) -> AgentResponse:
    return AgentResponse(
        agent_id=agent_id,
        round_number=1,
        reasoning="Test reasoning",
        actions=["test_action"],
        state_changes=state_changes or [],
    )


def _make_event(
    agent_id: str, event_type: EventType, affected_factors: list[str] = None
) -> EventLogEntry:
    from uuid import uuid4

    return EventLogEntry(
        id=str(uuid4()),
        round_number=1,
        source_agent=agent_id,
        event_type=event_type,
        description="Test event",
        affected_factors=affected_factors or [],
    )


def test_environment_node_applies_valid_state_change():
    state = build_initial_state()
    state.clock.current_tick = 15
    state.market_metrics = {"cost_pressure": 120.0}

    response = _make_response(
        agent_id="regulator",
        state_changes=[StateChange(factor_id="F2", proposed_state="F2.2", reasoning="Test")],
    )

    # RoundResult mit Response hinzufügen
    state.round_results.append(
        RoundResult(
            round_number=15,
            agent_responses=[response],
            events=[],
            environment_snapshot=state.environment,
        )
    )

    environment = EnvironmentNode()
    state = environment.invoke(state)

    assert state.environment.factors["F2"].current_state == "F2.2"


def test_environment_node_ignores_invalid_state_change():
    state = build_initial_state()
    state.clock.current_tick = 1

    factor_id = list(state.environment.factors.keys())[0]
    original_state = state.environment.factors[factor_id].current_state

    response = _make_response(
        agent_id="regulator",
        state_changes=[
            StateChange(factor_id=factor_id, proposed_state="INVALID_STATE", reasoning="Test")
        ],
    )

    state.round_results.append(
        RoundResult(
            round_number=1,
            agent_responses=[response],
            events=[],
            environment_snapshot=state.environment,
        )
    )

    environment = EnvironmentNode()
    state = environment.invoke(state)

    # Zustand sollte unverändert sein
    assert state.environment.factors[factor_id].current_state == original_state


def test_environment_node_writes_round_result():
    state = build_initial_state()
    state.clock.current_tick = 1

    response = _make_response(agent_id="consumer")
    state.round_results.append(
        RoundResult(
            round_number=1,
            agent_responses=[response],
            events=[],
            environment_snapshot=state.environment,
        )
    )

    environment = EnvironmentNode()
    state = environment.invoke(state)

    assert len(state.round_results) >= 1
    last = state.round_results[-1]
    assert last.round_number == 1
    assert last.summary != ""


def test_environment_node_summary_contains_round_info():
    state = build_initial_state()
    state.clock.current_tick = 1

    response = _make_response(agent_id="consumer")
    state.round_results.append(
        RoundResult(
            round_number=1,
            agent_responses=[response],
            events=[],
            environment_snapshot=state.environment,
        )
    )

    environment = EnvironmentNode()
    state = environment.invoke(state)

    last_summary = state.round_results[-1].summary
    assert "Tick 1" in last_summary
