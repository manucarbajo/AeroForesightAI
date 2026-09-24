from __future__ import annotations

from dataclasses import dataclass

from src.agents._scheduling_helpers import (
    initial_score_ledger as _initial_score_ledger,
)
from src.agents._scheduling_helpers import (
    last_spoken_rounds as _last_spoken_rounds,
)
from src.agents._scheduling_helpers import (
    latest_round_result as _latest_round_result,
)
from src.agents._scheduling_helpers import (
    round_contribution_counts as _round_contribution_counts,
)
from src.agents.agent_node import AgentNode
from src.agents.redebedarf_scheduler import FactorChangeObservation, RedebedarfScheduler
from src.llm import LLMCallable
from src.models.agent_models import AgentConfig
from src.models.state_models import SimulationState, SpeechCandidateState, SpeechPlanState


def _attach_redebedarf_metadata(
    state: SimulationState,
    *,
    agent_id: str,
    score: int,
    reasons: list[str],
) -> None:
    """Persist the scheduler score that triggered a contribution."""

    if not state.round_results:
        return

    latest_rr = state.round_results[-1]
    if not latest_rr.agent_responses:
        return

    latest_response = latest_rr.agent_responses[-1]
    if latest_response.agent_id != agent_id:
        return

    patched_response = latest_response.model_copy(
        update={
            "redebedarf_score": int(score),
            "redebedarf_reasons": list(reasons),
        }
    )
    state.round_results[-1] = latest_rr.model_copy(
        update={
            "agent_responses": latest_rr.agent_responses[:-1] + [patched_response],
        }
    )


@dataclass
class RoundExecutionNode:
    """Compute speech demand and execute agents in the scheduler-dictated order."""

    agents: list[AgentConfig]
    llm: LLMCallable
    fallback_to_all_agents: bool = True

    def __post_init__(self) -> None:
        self._agent_nodes: dict[str, AgentNode] = {
            agent.id: AgentNode(agent, llm=self.llm) for agent in self.agents
        }

    def invoke(self, state: SimulationState) -> SimulationState:
        scheduler = RedebedarfScheduler.from_simulation_state(state, apply_score_deltas=False)
        round_number = max(1, state.clock.current_tick)
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

        # If there is a latest partial result in this round, apply its deltas
        latest_round_result = _latest_round_result(state, round_number)
        if latest_round_result is not None and latest_round_result.agent_responses:
            latest_response = latest_round_result.agent_responses[-1]
            observed_factor_ids = {change.factor_id for change in latest_response.state_changes}
            observed_factor_ids.update(
                factor_id
                for event in latest_round_result.events
                for factor_id in event.affected_factors
            )
            for factor_id in sorted(observed_factor_ids):
                scheduler.register_factor_change(
                    FactorChangeObservation(
                        factor_id=factor_id,
                        source_agent=latest_response.agent_id,
                    )
                )
            # Do not count this as a contribution for the current round preview
            scheduler.mark_spoken(
                latest_response.agent_id,
                round_number=latest_round_result.round_number,
                count_contribution=False,
            )

        # Iterative scheduling loop: recompute candidates after each agent invocation
        safety_limit = max(
            100, len(scheduler.agent_ids) * scheduler.max_contributions_per_agent * 4
        )
        ops = 0
        executed_order: list[str] = []

        while True:
            ops += 1
            if ops > safety_limit:
                # safety bail-out
                break

            candidates = scheduler.build_speech_candidates()
            if not candidates:
                # fallback: if nothing eligible and fallback is enabled, run one pass over all agents once
                if not executed_order and self.fallback_to_all_agents:
                    scores = scheduler.snapshot_scores()
                    fallback_order = sorted(
                        scores.keys(), key=lambda agent_id: (-scores.get(agent_id, 0), agent_id)
                    )
                    for agent_id in fallback_order:
                        agent_node = self._agent_nodes.get(agent_id)
                        if agent_node is None:
                            continue
                        score_at_speak = int(scheduler.snapshot_scores().get(agent_id, 0))
                        reasons_at_speak = list(scheduler.snapshot_reasons().get(agent_id, ()))
                        state = agent_node.invoke(state)
                        _attach_redebedarf_metadata(
                            state,
                            agent_id=agent_id,
                            score=score_at_speak,
                            reasons=reasons_at_speak,
                        )
                        # after invoke, reset and count contribution
                        scheduler.mark_spoken(agent_id, round_number=round_number)
                        state.redebedarf_scores = scheduler.snapshot_scores()
                        executed_order.append(agent_id)
                break

            # take the highest-ranked candidate
            candidate = candidates[0]
            agent_id = candidate.agent_id
            agent_node = self._agent_nodes.get(agent_id)
            if agent_node is None:
                # still mark spoken to avoid endless eligibility
                scheduler.mark_spoken(agent_id, round_number=round_number)
                continue

            score_at_speak = candidate.score
            reasons_at_speak = list(candidate.reasons)

            # invoke agent; AgentNode will append a RoundResult for this single agent
            state = agent_node.invoke(state)
            _attach_redebedarf_metadata(
                state,
                agent_id=agent_id,
                score=score_at_speak,
                reasons=reasons_at_speak,
            )

            # after the agent ran, apply deltas observed in their produced RoundResult
            latest_rr = None
            if state.round_results:
                latest_rr = state.round_results[-1]

            if latest_rr is not None and latest_rr.agent_responses:
                latest_response = latest_rr.agent_responses[-1]
                observed_factor_ids = {change.factor_id for change in latest_response.state_changes}
                observed_factor_ids.update(
                    factor_id for event in latest_rr.events for factor_id in event.affected_factors
                )
                for factor_id in sorted(observed_factor_ids):
                    scheduler.register_factor_change(
                        FactorChangeObservation(
                            factor_id=factor_id,
                            source_agent=latest_response.agent_id,
                        )
                    )

            # count this contribution and reset speaker score
            scheduler.mark_spoken(agent_id, round_number=round_number)
            state.redebedarf_scores = scheduler.snapshot_scores()

            # record executed order and continue loop to allow newly eligible agents to speak
            executed_order.append(agent_id)

        # finalize speech plan + state fields
        state.current_speech_order = executed_order
        state.current_speech_candidates = [
            SpeechCandidateState(
                agent_id=a,
                score=state.redebedarf_scores.get(a, 0),
                reasons=[],
                contributions_this_round=0,
            )
            for a in executed_order
        ]
        state.speech_plan = SpeechPlanState(
            round_number=round_number,
            order=list(state.current_speech_order),
            candidates=list(state.current_speech_candidates),
            scores=dict(state.redebedarf_scores),
        )

        return state
