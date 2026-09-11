"""Environment node: applies agent responses, runs population booking, and builds tick summary."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.llm import LLMCallable
from src.market.factor_dynamics import build_runtime_metrics, validate_factor_proposals
from src.market.market_feedback import initial_provider_markup
from src.market.property_engine import resolve_system_properties
from src.market.simulation_functions import (
    active_parameters,
    compose_ticket_price,
    compute_cost_pressure,
    update_cost_index,
)
from src.models.agent_models import AgentResponse, StateChange
from src.models.event_models import EventLogEntry, RoundResult
from src.models.state_models import DEFAULT_SEED, SimulationState
from src.population.population_sampler import run_population_tick

logger = logging.getLogger(__name__)


class EnvironmentNode:
    def __init__(
        self, prefer_agent_order: list[str] | None = None, llm: LLMCallable | None = None
    ) -> None:
        self.prefer_agent_order = prefer_agent_order or ["regulator", "provider", "consumer"]
        self.llm = llm

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_tick

        responses = self._collect_round_responses(state, round_number)
        round_events = [event for event in state.event_log if event.round_number == round_number]

        applied_changes = self._apply_state_changes(state, responses)

        # Booking must happen before market feedback so the feedback uses current booking rate
        state = self._run_population_tick(state, round_number)

        summary = self._build_round_summary(state, responses, round_events, applied_changes)

        state.environment.global_context = summary
        state.round_results.append(
            RoundResult(
                round_number=round_number,
                agent_responses=[],
                events=round_events,
                # Eine Kopie: Pydantic übernimmt die Instanz, und ohne Kopie trüge
                # jede Runde am Ende den Endzustand des Laufs (P5.1).
                environment_snapshot=state.environment.model_copy(deep=True),
                summary=summary,
            )
        )

        return state

    def apply_consumer_factor_updates(self, state: SimulationState) -> SimulationState:
        """Apply consumer ``state_changes`` after the consumer runs post-booking."""

        round_number = state.clock.current_tick
        consumer_responses = [
            response
            for round_result in state.round_results
            if round_result.round_number == round_number
            for response in round_result.agent_responses
            if response.agent_id == "consumer"
        ]
        if consumer_responses:
            self._apply_state_changes(state, consumer_responses)
        return state

    def _run_population_tick(self, state: SimulationState, round_number: int) -> SimulationState:
        consumer_agent = next((agent for agent in state.agents if agent.id == "consumer"), None)
        if consumer_agent is None or consumer_agent.population_config is None:
            return state

        properties = state.resolved_properties()
        price_model = properties.price_model
        last_price = (
            state.price_history[-1].price if state.price_history else price_model.base_price
        )
        previous_markup = state.market_metrics.get(
            "provider_markup",
            state.market_metrics.get(
                "markup", initial_provider_markup(properties, tick=round_number)
            ),
        )
        previous_cost_index = state.market_metrics.get("cost_index", 1.0)

        params = active_parameters(round_number, properties)
        fuel_change = params.get("fuel_price_change", 0.0)
        if price_model.compound_fuel_on_cost:
            cost_index = update_cost_index(previous_cost_index, fuel_change)
        else:
            cost_index = previous_cost_index
        # P0.7: Faktoren und Systemgrößen mitgeben. Bis dahin ging dieser Aufruf
        # ohne beides — die bedingten regulatorischen Kostentreiber konnten hier
        # also nie greifen, während derselbe Aufruf im Market-Node sie kannte.
        # Der Wert von hier landet als `cost_pressure` in `state.market_metrics`
        # und ist genau die Größe, gegen die `f4_high_cost_pressure` und
        # `f4_stable_growth` schwellen: Die F4-Übergänge urteilten über einen
        # Kostendruck ohne Regulierungskosten, während die Kundschaft den vollen
        # Preis zahlte.
        system_properties = resolve_system_properties(round_number, properties)
        cost_pressure = compute_cost_pressure(
            round_number,
            properties,
            cost_index=cost_index,
            factors=state.environment.factors,
            system_properties=system_properties,
        )
        if state.price_history:
            provisional_price = last_price
        else:
            provisional_price = compose_ticket_price(
                cost_pressure,
                initial_provider_markup(properties, tick=round_number),
                properties=properties,
                tick=round_number,
            )
            from src.models.event_models import PriceHistoryEntry

            state.price_history.append(
                PriceHistoryEntry(
                    round_number=0,
                    agent_id="system",
                    price=provisional_price,
                    demand_level=1.0,
                    booking_rate=0.0,
                )
            )
            state.property_timeseries.append(
                {
                    "tick": 0,
                    "ticket_price": provisional_price,
                    "cost_pressure": cost_pressure,
                    "cost_index": cost_index,
                    "provider_markup": initial_provider_markup(properties, tick=round_number),
                    "markup": initial_provider_markup(properties, tick=round_number),
                    **params,
                }
            )

        state.market_metrics = {
            **params,
            "cost_pressure": cost_pressure,
            "cost_index": cost_index,
            "provider_markup": previous_markup,
            "markup": previous_markup,
            "ticket_price_pre_feedback": provisional_price,
            "ticket_price": provisional_price,
        }

        carbon_tax = params.get("carbon_tax_level", 0.0)
        # `SimulationRunner.run` löst den Seed auf, bevor ein Tick läuft;
        # hier steht er also normalerweise schon. Der Rückfall bleibt für
        # die Aufrufer, die den Node ohne Runner benutzen (Studio, Tests) —
        # aber mit derselben Konstante, nicht mehr mit einer eigenen 42.
        seed = state.config.seed if state.config.seed is not None else DEFAULT_SEED

        # Kontext für die Shift-Regeln (P0.4): dieselbe Momentaufnahme, gegen die
        # auch die Faktor-Regeln geprüft werden. `booking_rate` steht hier noch
        # nicht — sie entsteht erst aus diesem Aufruf. `build_runtime_metrics`
        # fällt deshalb auf die Rate des Vorticks zurück, und genau das ist die
        # gewollte Lesart: Eine Regel, die auf die Buchungsrate reagiert, reagiert
        # auf die zuletzt beobachtete.
        metrics = build_runtime_metrics(state).as_mapping()

        individuals, pop_stats = run_population_tick(
            state.resolved_properties(),
            consumer_agent.population_config,
            state.population_individuals or None,
            ticket_price=provisional_price,
            carbon_tax=carbon_tax,
            factors=state.environment.factors,
            system_properties=system_properties,
            seed=seed,
            current_tick=round_number,
            metrics=metrics,
        )
        state.population_individuals = individuals

        state.market_metrics["booking_rate"] = pop_stats.total_demand
        state.market_metrics["booking_evaluated"] = True

        state.population_stats.append(
            {
                "round_number": round_number,
                "total_demand": pop_stats.total_demand,
                "total_booked": pop_stats.total_booked,
                "total_population": pop_stats.total_population,
                "avg_income_factor": pop_stats.avg_income_factor,
                "segments": {key: value.model_dump() for key, value in pop_stats.segments.items()},
                "age_groups": {
                    key: value.model_dump() for key, value in pop_stats.age_groups.items()
                },
            }
        )
        return state

    def _collect_round_responses(
        self, state: SimulationState, round_number: int
    ) -> list[AgentResponse]:
        by_agent: dict[str, AgentResponse] = {}
        for round_result in state.round_results:
            if round_result.round_number != round_number:
                continue
            for response in round_result.agent_responses:
                by_agent[response.agent_id] = response

        preferred_order = (
            list(state.current_speech_order)
            if getattr(state, "current_speech_order", None)
            else list(self.prefer_agent_order)
        )

        ordered: list[str] = []
        for agent_id in preferred_order:
            if agent_id in by_agent:
                ordered.append(agent_id)
        for agent_id in sorted(by_agent.keys()):
            if agent_id not in ordered:
                ordered.append(agent_id)

        return [by_agent[agent_id] for agent_id in ordered]

    def _apply_state_changes(
        self, state: SimulationState, responses: list[AgentResponse]
    ) -> dict[str, str]:
        changes_by_factor: dict[str, StateChange] = {}
        for response in responses:
            gated_changes = validate_factor_proposals(
                state,
                response.state_changes,
                agent_id=response.agent_id,
            )
            for change in gated_changes:
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

        lines.append(f"Tick {state.clock.current_tick}/{state.clock.max_ticks}")

        if getattr(state, "current_speech_order", None):
            lines.append("Speech order:")
            lines.append("- " + ", ".join(state.current_speech_order))

        if getattr(state, "redebedarf_scores", None):
            lines.append("Redebedarf scores:")
            lines.append(
                "- "
                + ", ".join(
                    f"{agent_id}={score}"
                    for agent_id, score in sorted(state.redebedarf_scores.items())
                )
            )

        if applied_changes:
            lines.append("Applied factor updates:")
            for factor_id in sorted(applied_changes.keys()):
                factor = state.environment.factors[factor_id]
                desc = factor.possible_states.get(factor.current_state, "")
                lines.append(f"- {factor_id} -> {factor.current_state} :: {desc}")
        else:
            lines.append("Applied factor updates: -")

        if state.market_metrics:
            lines.append("Market metrics (deterministic):")
            for metric_id in sorted(state.market_metrics.keys()):
                lines.append(f"- {metric_id}={state.market_metrics[metric_id]}")

        if events:
            lines.append("Events:")
            for event in events:
                affected = ", ".join(event.affected_factors) if event.affected_factors else "-"
                lines.append(
                    f"- source={event.source_agent} type={event.event_type.value} factors={affected} :: {event.description}"
                )
        else:
            lines.append("Events: -")

        segment_analysis = self._collect_segment_analysis(responses)
        if segment_analysis:
            lines.append("Consumer segment_analysis:")
            lines.append(json.dumps(segment_analysis, ensure_ascii=True, indent=2))

        lines.append("Agent summaries:")
        for response in responses:
            actions = ", ".join(response.actions) if response.actions else "-"
            lines.append(f"- {response.agent_id}: actions={actions} :: {response.reasoning}")

        return "\n".join(lines).strip() + "\n"

    def _collect_segment_analysis(self, responses: list[AgentResponse]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for response in responses:
            if response.agent_id != "consumer":
                continue
            if isinstance(response.segment_analysis, dict):
                merged.update(response.segment_analysis)
        return merged
