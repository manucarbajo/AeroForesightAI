from __future__ import annotations

import logging

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
from src.agents.redebedarf_scheduler import FactorChangeObservation, RedebedarfScheduler
from src.models.event_models import RoundResult
from src.models.state_models import SimulationState, SpeechCandidateState, SpeechPlanState

logger = logging.getLogger(__name__)


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
        # **`logging` statt `print`** (P3.5). Diese acht Zeilen liefen in *jedem*
        # Tick unbedingt mit, ohne Level und ohne Abschaltmöglichkeit. Der
        # Unterschied ist nicht nur der Kanal, sondern die Einteilung: Was
        # Fortschritt ist, bleibt `info` und steht damit weiter im
        # Fortschrittsfenster des Dashboards (es hängt seit P0.1 über
        # `progress_logging` an `logging`); der Rest ist `debug` und schweigt in
        # einem normalen Lauf.
        logger.debug(
            "Scheduler, Tick %s/%s — bereits gesprochen: %s",
            state.clock.current_tick,
            state.clock.max_ticks,
            state.current_round_spoken_agents,
        )

        round_number = state.clock.current_tick
        if round_number < 1:
            state.current_speech_order = []
            state.current_speech_candidates = []
            state.redebedarf_scores = {}
            state.speech_plan = None
            logger.debug("Tick %s liegt vor dem ersten — keine Reihenfolge", round_number)
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
            # **Als Warnung, nicht als Debugzeile.** Diese Grenze greift nur,
            # wenn in einem Tick mehr als zehn Beiträge gefallen sind, und dass
            # der Rest des Ticks danach übersprungen wird, gehört zu den Dingen,
            # die jemand sehen soll — bis P3.5 stand sie zwischen sieben anderen
            # `print`-Zeilen und war damit praktisch unsichtbar.
            logger.warning(
                "Tick %s: Sicherheitsgrenze von 10 Beiträgen erreicht (%s Sprecher) — "
                "der Rest des Ticks geht direkt an den Markt.",
                round_number,
                len(spoken_agents_this_round),
            )
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
        logger.debug("Redebedarf-Punkte: %s", state.redebedarf_scores)
        state.speech_plan = SpeechPlanState(
            round_number=round_number,
            order=list(state.current_speech_order),
            candidates=list(state.current_speech_candidates),
            scores=dict(state.redebedarf_scores),
        )
        # **Die eine Zeile, die Fortschritt ist**, und deshalb `info`: Sie sagt,
        # wer in diesem Tick spricht. Das Fortschrittsfenster des Dashboards
        # zeigt damit weiter, was es vorher zeigte — nur ohne die sieben
        # Debugzeilen darum herum.
        logger.info(
            "Tick %s: Redebedarf-Reihenfolge %s",
            round_number,
            state.current_speech_order or "keine",
        )
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
