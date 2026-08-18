from __future__ import annotations

from src.models.event_models import RoundResult
from src.models.state_models import SimulationState, SpeechCandidateState, SpeechPlanState
from src.redebedarf_scheduler import FactorChangeObservation, RedebedarfScheduler


def _round_contribution_counts(state: SimulationState, round_number: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rr in state.round_results:
        if rr.round_number != round_number:
            continue
        for response in rr.agent_responses:
            counts[response.agent_id] = counts.get(response.agent_id, 0) + 1
    return counts


def _last_spoken_rounds(state: SimulationState) -> dict[str, int]:
    last_spoken: dict[str, int] = {}
    for rr in state.round_results:
        for response in rr.agent_responses:
            last_spoken[response.agent_id] = max(
                last_spoken.get(response.agent_id, 0), rr.round_number
            )
    return last_spoken


def _latest_round_result(state: SimulationState, round_number: int) -> RoundResult | None:
    for rr in reversed(state.round_results):
        if rr.round_number == round_number:
            return rr
    return None


def _initial_score_ledger(
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


def _apply_latest_turn_deltas(
    scheduler: RedebedarfScheduler,
    round_result: RoundResult,
) -> None:
    if not round_result.agent_responses:
        return

    latest_response = round_result.agent_responses[-1]
    observed_factor_ids = {change.factor_id for change in latest_response.state_changes}
    observed_factor_ids.update(
        factor_id for event in round_result.events for factor_id in event.affected_factors
    )

    for factor_id in sorted(observed_factor_ids):
        scheduler.register_factor_change(
            FactorChangeObservation(
                factor_id=factor_id,
                source_agent=latest_response.agent_id,
            )
        )

    scheduler.mark_spoken(
        latest_response.agent_id,
        round_number=round_result.round_number,
        count_contribution=False,
    )


class SchedulerNode:
    """Computes the speaking order via RedebedarfScheduler and manages speech plans."""

    def invoke(self, state: SimulationState) -> SimulationState:
        print("\n--- SCHEDULER DEBUG ---")
        print(f"Round: {state.clock.current_tick}/{state.clock.max_ticks}")
        print(f"Spoken so far: {state.current_round_spoken_agents}")

        round_number = state.clock.current_tick
        if round_number < 1:
            state.current_speech_order = []
            state.current_speech_candidates = []
            state.redebedarf_scores = {}
            state.speech_plan = None
            print("Next speaker order: []\n")
            return state

        scheduler = RedebedarfScheduler.from_simulation_state(state, apply_score_deltas=False)
        scheduler._score_by_agent = _initial_score_ledger(state, scheduler, round_number)
        last_spoken_rounds = _last_spoken_rounds(state)
        scheduler._last_spoken_round = {
            agent_id: last_spoken_rounds.get(agent_id, 0) for agent_id in scheduler.agent_ids
        }
        scheduler.start_round(round_number)
        contribution_counts = _round_contribution_counts(state, round_number)
        scheduler._contributions_this_round = {
            agent_id: contribution_counts.get(agent_id, 0) for agent_id in scheduler.agent_ids
        }

        latest_round_result = _latest_round_result(state, round_number)
        if latest_round_result is not None:
            _apply_latest_turn_deltas(scheduler, latest_round_result)

        spoken_agents_this_round = list(dict.fromkeys(state.current_round_spoken_agents))
        if len(spoken_agents_this_round) > 10:
            state.current_speech_candidates = []
            state.current_speech_order = []
            state.redebedarf_scores = scheduler.snapshot_scores()
            state.speech_plan = SpeechPlanState(
                round_number=round_number,
                order=[],
                candidates=[],
                scores=dict(state.redebedarf_scores),
            )
            print("Next speaker order: []")
            print("Safety limit reached, routing to market.\n")
            return state

        candidates = scheduler.build_speech_candidates()

        state.current_speech_candidates = [
            SpeechCandidateState(
                agent_id=candidate.agent_id,
                score=candidate.score,
                reasons=list(candidate.reasons),
                contributions_this_round=candidate.contributions_this_round,
            )
            for candidate in candidates
        ]
        state.current_speech_order = [candidate.agent_id for candidate in candidates]
        state.redebedarf_scores = scheduler.snapshot_scores()
        print(f"Scores: {state.redebedarf_scores}")
        state.speech_plan = SpeechPlanState(
            round_number=round_number,
            order=list(state.current_speech_order),
            candidates=list(state.current_speech_candidates),
            scores=dict(state.redebedarf_scores),
        )
        print(f"Next speaker order: {state.current_speech_order}\n")
        return state

    @staticmethod
    def route_from_scheduler(state: SimulationState) -> str:
        """Determines the next agent to run or routes to the market."""
        speech_plan = state.speech_plan.model_dump() if state.speech_plan is not None else {}
        if speech_plan.get("aborted"):
            return "market"
        if not state.current_speech_order:
            return "market"
        next_agent = state.current_speech_order[0]
        if next_agent in {"consumer", "provider", "regulator"}:
            return next_agent
        return "market"
