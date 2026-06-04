from __future__ import annotations

from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse, StateChange
from src.models.event_models import RoundResult
from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.protocol_generator import build_protocol_payload, _replay_redebedarf_by_contribution


def _append_contribution(
    state,
    *,
    round_number: int,
    agent_id: str,
    factor_id: str,
    redebedarf_score: int | None = None,
) -> None:
    response = AgentResponse(
        agent_id=agent_id,
        round_number=round_number,
        reasoning=f"{agent_id} speaks",
        actions=["SPEAK"],
        state_changes=[StateChange(factor_id=factor_id, proposed_state=f"{factor_id}.2", reasoning="test")],
        redebedarf_score=redebedarf_score,
        redebedarf_reasons=["test-reason"] if redebedarf_score is not None else [],
    )
    event = EventLogEntry(
        id=f"{agent_id}-{round_number}",
        round_number=round_number,
        source_agent=agent_id,
        event_type=EventType.DEMAND_SHIFT,
        description="test event",
        affected_factors=[factor_id],
        timestamp="",
    )
    state.round_results.append(
        RoundResult(
            round_number=round_number,
            agent_responses=[response],
            events=[event],
            environment_snapshot=state.environment,
            summary=f"{agent_id} contribution",
        )
    )
    state.event_log.append(event)


def test_protocol_uses_stored_redebedarf_scores():
    state = build_initial_state()
    state.clock.current_tick = 1
    _append_contribution(state, round_number=1, agent_id="consumer", factor_id="F1", redebedarf_score=3)

    payload = build_protocol_payload(state)
    contribution = payload["rounds"][0]["contributions"][0]

    assert contribution["redebedarf_score"] == 3
    assert contribution["redebedarf_reasons"] == ["test-reason"]


def test_protocol_replays_redebedarf_when_missing():
    state = build_initial_state()
    state.clock.current_tick = 1
    _append_contribution(state, round_number=1, agent_id="consumer", factor_id="F1")
    _append_contribution(state, round_number=1, agent_id="provider", factor_id="F4")

    replayed = _replay_redebedarf_by_contribution(state)
    assert replayed[(1, 0)]["redebedarf_score"] >= 3
    assert replayed[(1, 1)]["redebedarf_score"] >= 0

    payload = build_protocol_payload(state)
    contributions = payload["rounds"][0]["contributions"]
    assert contributions[0]["redebedarf_score"] is not None
    assert contributions[1]["redebedarf_score"] is not None
