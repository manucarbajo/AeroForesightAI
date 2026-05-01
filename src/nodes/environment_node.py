from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from src.models.agent_models import AgentResponse, StateChange
from src.models.event_models import EventLogEntry, RoundResult
from src.models.enums import AgentType
from src.models.state_models import SimulationState


class EnvironmentNode:
    def __init__(self, prefer_agent_order: list[str] | None = None) -> None:
        self.prefer_agent_order = prefer_agent_order or ["regulator", "provider", "consumer"]

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_round

        responses = self._collect_round_responses(state, round_number)
        round_events = [e for e in state.event_log if e.round_number == round_number]

        applied_changes = self._apply_state_changes(state, responses)
        summary = self._build_round_summary(state, responses, round_events, applied_changes)

        state.environment.global_context = summary
        state.round_results.append(
            RoundResult(
                round_number=round_number,
                agent_responses=responses,
                events=round_events,
                environment_snapshot=state.environment,
                summary=summary,
            )
        )

        return state

    def _collect_round_responses(self, state: SimulationState, round_number: int) -> list[AgentResponse]:
        # AP2 schreibt pro Agent-Invoke ein RoundResult; wir aggregieren hier pro Runde.
        by_agent: dict[str, AgentResponse] = {}
        for rr in state.round_results:
            if rr.round_number != round_number:
                continue
            for resp in rr.agent_responses:
                by_agent[resp.agent_id] = resp

        ordered: list[str] = []
        for agent_id in self.prefer_agent_order:
            if agent_id in by_agent:
                ordered.append(agent_id)
        for agent_id in sorted(by_agent.keys()):
            if agent_id not in ordered:
                ordered.append(agent_id)

        return [by_agent[agent_id] for agent_id in ordered]

    def _apply_state_changes(
        self, state: SimulationState, responses: list[AgentResponse]
    ) -> dict[str, str]:
        # MVP-Regel: pro Faktor gilt der erste gueltige Vorschlag in prefer_agent_order.
        changes_by_factor: dict[str, StateChange] = {}
        for response in responses:
            for change in response.state_changes:
                if change.factor_id not in state.environment.factors:
                    continue
                factor = state.environment.factors[change.factor_id]
                if change.proposed_state not in factor.possible_states:
                    continue
                if change.factor_id in changes_by_factor:
                    continue
                changes_by_factor[change.factor_id] = change

        applied: dict[str, str] = {}
        for factor_id, change in changes_by_factor.items():
            state.environment.factors[factor_id].current_state = change.proposed_state
            applied[factor_id] = change.proposed_state
        return applied

    def _build_round_summary(
        self,
        state: SimulationState,
        responses: list[AgentResponse],
        events: list[EventLogEntry],
        applied_changes: dict[str, str],
    ) -> str:
        lines: list[str] = []

        sim_year = state.clock.year_start + (state.clock.current_round * state.clock.years_per_round)
        lines.append(
            f"Round {state.clock.current_round}/{state.clock.max_rounds} (simulated_year={sim_year})"
        )

        if applied_changes:
            lines.append("Applied factor updates:")
            for factor_id in sorted(applied_changes.keys()):
                factor = state.environment.factors[factor_id]
                desc = factor.possible_states.get(factor.current_state, "")
                lines.append(f"- {factor_id} -> {factor.current_state} :: {desc}")
        else:
            lines.append("Applied factor updates: -")

        if events:
            lines.append("Events:")
            for e in events:
                affected = ", ".join(e.affected_factors) if e.affected_factors else "-"
                lines.append(
                    f"- source={e.source_agent} type={e.event_type.value} factors={affected} :: {e.description}"
                )
        else:
            lines.append("Events: -")

        segment_analysis = self._collect_segment_analysis(responses)
        if segment_analysis:
            lines.append("Consumer segment_analysis:")
            lines.append(json.dumps(segment_analysis, ensure_ascii=True, indent=2))

        lines.append("Agent summaries:")
        for resp in responses:
            actions = ", ".join(resp.actions) if resp.actions else "-"
            lines.append(f"- {resp.agent_id}: actions={actions} :: {resp.reasoning}")

        return "\n".join(lines).strip() + "\n"

    def _collect_segment_analysis(self, responses: list[AgentResponse]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for resp in responses:
            if resp.agent_id != "consumer":
                continue
            if isinstance(resp.segment_analysis, dict):
                merged.update(resp.segment_analysis)
        return merged

