"""Shared bookkeeping helpers for the sequential and graph-native Redebedarf schedulers.

Used by both redebedarf_node.py (sequential execution) and scheduler_node.py
(LangGraph-native execution) - previously duplicated verbatim in both files.
"""

from __future__ import annotations

from src.agents.redebedarf_scheduler import RedebedarfScheduler
from src.models.event_models import RoundResult
from src.models.state_models import SimulationState


def round_contribution_counts(state: SimulationState, round_number: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rr in state.round_results:
        if rr.round_number != round_number:
            continue
        for response in rr.agent_responses:
            counts[response.agent_id] = counts.get(response.agent_id, 0) + 1
    return counts


def last_spoken_rounds(state: SimulationState) -> dict[str, int]:
    last_spoken: dict[str, int] = {}
    for rr in state.round_results:
        for response in rr.agent_responses:
            last_spoken[response.agent_id] = max(
                last_spoken.get(response.agent_id, 0), rr.round_number
            )
    return last_spoken


def initial_score_ledger(
    state: SimulationState, scheduler: RedebedarfScheduler, round_number: int
) -> dict[str, int]:
    if state.redebedarf_scores:
        return {
            agent_id: int(state.redebedarf_scores.get(agent_id, 0))
            for agent_id in scheduler.agent_ids
        }
    if round_number == 1:
        return {agent_id: scheduler.threshold for agent_id in scheduler.agent_ids}
    return {agent_id: 0 for agent_id in scheduler.agent_ids}


def latest_round_result(state: SimulationState, round_number: int) -> RoundResult | None:
    for rr in reversed(state.round_results):
        if rr.round_number == round_number:
            return rr
    return None
