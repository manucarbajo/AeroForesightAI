"""Environment nodes for AP3/AP4 simulation flows."""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from pydantic import BaseModel, Field

from src.models.agent_models import AgentResponse, StateChange
from src.models.cib_models import CIBMatrix
from src.models.event_models import EventLogEntry, RoundResult
from src.models.population_models import PopulationConfig
from src.models.state_models import SimulationState
from src.simulation_functions import compute_market_metrics

logger = logging.getLogger(__name__)

MAX_SHARE_CHANGE_PER_ROUND = 0.05  # 5%
MIN_SEGMENT_SHARE = 0.0
MAX_SEGMENT_SHARE = 1.0


class LLMCallable(Protocol):
    """Protocol for LLM clients."""

    def call(self, prompt: str) -> str: ...


class PopulationShift(BaseModel):
    """Population shift for one segment."""

    segment_id: str
    segment_name: str
    old_share: float
    new_share: float
    shift_amount: float
    reasoning: str
    clamped: bool = False


class PopulationUpdateResult(BaseModel):
    """Result of a population update."""

    round_number: int
    shifts: list[PopulationShift] = Field(default_factory=list)
    total_reasoning: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


POPULATION_UPDATE_SYSTEM_PROMPT = """Du bist ein Experte fuer Bevoelkerungsdynamik und Marktentwicklung im Flugverkehr.

Deine Aufgabe: Prognostiziere die Verschiebung der Konsumenten-Segmente fuer die naechste Runde.

Input:
- Aktuelle Segment-Anteile
- Aktuelle Faktor-Zustaende (Mobilitaetsbeduerfnis, Regulierung, Technologie, etc.)
- CIB-Matrix (wie Faktoren sich gegenseitig beeinflussen)
- Bisherige Bevoelkerungstrends

Output:
- Neue Segment-Anteile (prozentual)
- Begruendung fuer jede Verschiebung
- Max. 5% Verschiebung pro Segment pro Runde

Wichtig:
- Begruende mit Faktoren-Zustaenden und CIB-Wechselwirkungen
- Segmente koennen ueberlappen (ein Passenger kann mehrere Labels haben)
- Alle Anteile muessen zusammen <= 100% ergeben (erlaubt Ueberlappung)
"""


POPULATION_UPDATE_USER_PROMPT_TEMPLATE = """Runde: {round_number}

Aktuelle Segment-Anteile:
{segments_json}

Aktuelle Faktor-Zustaende:
{factors_json}

CIB-Matrix Zusammenfassung (Top 10 Wechselwirkungen):
{cib_summary}

Bisherige Verschiebungen (letzte 3 Runden):
{historical_shifts}

Prognostiziere die neuen Segment-Anteile und begruende jede Verschiebung.

Format JSON:
{{
  "segments": [
    {{
      "id": "segment_id",
      "new_share": 0.25,
      "reasoning": "Kurze Begründung mit Faktoren-Bezug"
    }}
  ],
  "overall_reasoning": "Gesamttrends und Wechselwirkungen"
}}
"""


class EnvironmentNode:
    def __init__(self, prefer_agent_order: list[str] | None = None, llm: LLMCallable | None = None) -> None:
        self.prefer_agent_order = prefer_agent_order or ["regulator", "provider", "consumer"]
        self.llm = llm

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_tick

        responses = self._collect_round_responses(state, round_number)
        round_events = [event for event in state.event_log if event.round_number == round_number]

        applied_changes = self._apply_state_changes(state, responses)
        
        # Only compute market metrics if MarketNode has not already computed them for this round
        market_already_computed = False
        if state.price_history and state.price_history[-1].round_number == round_number:
            market_already_computed = True
            
        if not market_already_computed:
            last_price = state.price_history[-1].price if state.price_history else 100.0
            last_demand = state.price_history[-1].demand_level if state.price_history else 1.0
            state.market_metrics = compute_market_metrics(
                round_number,
                state.config.policy_schedule,
                state.config.runtime_parameter_map(),
                previous_price=last_price,
                previous_demand=last_demand,
            )
            
        # Population Update
        pop_node = EnvironmentAgentNode(llm=self.llm)
        state = pop_node.invoke(state)
        
        # M3 Population Sampling
        consumer_agent = next((a for a in state.agents if a.id == "consumer"), None)
        if consumer_agent and consumer_agent.population_config:
            from src.population_sampler import run_population_sampling
            
            # Fetch ticket price from history
            current_ticket_price = 100.0
            if state.price_history and state.price_history[-1].round_number == round_number:
                current_ticket_price = state.price_history[-1].price
            elif len(state.price_history) > 1:
                current_ticket_price = state.price_history[-2].price
                
            carbon_tax = state.market_metrics.get("carbon_tax_level", 0.0)
            
            pop_stats = run_population_sampling(
                config=consumer_agent.population_config, 
                ticket_price=current_ticket_price, 
                carbon_tax=carbon_tax
            )
            
            # M3: booking_rate from population sample; demand_level stays deterministic (M2)
            state.market_metrics["booking_rate"] = pop_stats.total_demand
            if state.price_history and state.price_history[-1].round_number == round_number:
                state.price_history[-1].booking_rate = pop_stats.total_demand
            
            # Save stats
            if not hasattr(state, "population_stats"):
                state.population_stats = []
            state.population_stats.append({
                "round_number": round_number,
                "total_demand": pop_stats.total_demand,
                "total_booked": pop_stats.total_booked,
                "total_population": pop_stats.total_population,
                "segments": {
                    k: v.model_dump() for k, v in pop_stats.segments.items()
                }
            })

        summary = self._build_round_summary(state, responses, round_events, applied_changes)

        state.environment.global_context = summary
        state.round_results.append(
            RoundResult(
                round_number=round_number,
                agent_responses=[],
                events=round_events,
                environment_snapshot=state.environment,
                summary=summary,
            )
        )

        return state

    def _collect_round_responses(self, state: SimulationState, round_number: int) -> list[AgentResponse]:
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

    def _apply_state_changes(self, state: SimulationState, responses: list[AgentResponse]) -> dict[str, str]:
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

        lines.append(f"Tick {state.clock.current_tick}/{state.clock.max_ticks}")

        if getattr(state, "current_speech_order", None):
            lines.append("Speech order:")
            lines.append("- " + ", ".join(state.current_speech_order))

        if getattr(state, "redebedarf_scores", None):
            lines.append("Redebedarf scores:")
            lines.append(
                "- "
                + ", ".join(
                    f"{agent_id}={score}" for agent_id, score in sorted(state.redebedarf_scores.items())
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

        if hasattr(state, "_population_updates") and state._population_updates:
            last_update = state._population_updates[-1]
            if last_update.round_number == state.clock.current_tick and last_update.shifts:
                lines.append("Population shifts:")
                for shift in last_update.shifts:
                    lines.append(f"- {shift.segment_id}: {shift.old_share:.3f} -> {shift.new_share:.3f} ({shift.shift_amount:+.3f})")
                lines.append(f"  Reasoning: {last_update.total_reasoning}")

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


class EnvironmentAgentNode:
    def __init__(self, llm: LLMCallable | None = None):
        self.llm = llm

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_tick

        pop_config = self._extract_population_config(state)
        if pop_config is None:
            logger.warning("No population config found, skipping population update")
            return state

        result = self._update_population(state=state, pop_config=pop_config, round_number=round_number)
        state = self._apply_population_changes(state, result, pop_config)

        if result.shifts:
            logger.info(
                f"Round {round_number}: Population update - {len(result.shifts)} segments shifted"
            )

        return state

    def _extract_population_config(self, state: SimulationState) -> PopulationConfig | None:
        for agent in state.agents:
            if agent.id == "consumer" and agent.population_config:
                return agent.population_config
        return None

    def _update_population(
        self,
        state: SimulationState,
        pop_config: PopulationConfig,
        round_number: int,
    ) -> PopulationUpdateResult:
        if self.llm:
            return self._update_with_llm(state, pop_config, round_number)
        return self._update_with_heuristic(state, pop_config, round_number)

    def _update_with_llm(
        self,
        state: SimulationState,
        pop_config: PopulationConfig,
        round_number: int,
    ) -> PopulationUpdateResult:
        segments_json = json.dumps([segment.model_dump() for segment in pop_config.segments], indent=2)
        factors_json = json.dumps(
            {factor_id: factor.current_state for factor_id, factor in state.environment.factors.items()},
            indent=2,
        )

        cib_summary = self._build_cib_summary(state.cib_matrix) if state.cib_matrix else "N/A"
        historical_shifts = self._build_historical_shifts(state, pop_config)

        user_prompt = POPULATION_UPDATE_USER_PROMPT_TEMPLATE.format(
            round_number=round_number,
            segments_json=segments_json,
            factors_json=factors_json,
            cib_summary=cib_summary,
            historical_shifts=historical_shifts,
        )

        try:
            response = self.llm.call(user_prompt)
            llm_output = self._parse_llm_response(response)
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}, falling back to heuristic")
            return self._update_with_heuristic(state, pop_config, round_number)

        result = PopulationUpdateResult(
            round_number=round_number,
            total_reasoning=llm_output.get("overall_reasoning", ""),
        )

        for segment in pop_config.segments:
            seg_update = next((item for item in llm_output.get("segments", []) if item.get("id") == segment.id), None)
            if seg_update is None:
                continue

            new_share = seg_update.get("new_share", segment.share)
            shift = PopulationShift(
                segment_id=segment.id,
                segment_name=segment.name,
                old_share=segment.share,
                new_share=new_share,
                shift_amount=new_share - segment.share,
                reasoning=seg_update.get("reasoning", ""),
            )
            result.shifts.append(self._apply_shift_constraints(shift, pop_config))

        return result

    def _update_with_heuristic(
        self,
        state: SimulationState,
        pop_config: PopulationConfig,
        round_number: int,
    ) -> PopulationUpdateResult:
        result = PopulationUpdateResult(round_number=round_number)

        for segment in pop_config.segments:
            result.shifts.append(
                PopulationShift(
                    segment_id=segment.id,
                    segment_name=segment.name,
                    old_share=segment.share,
                    new_share=segment.share,
                    shift_amount=0.0,
                    reasoning="Heuristic: No change (waiting for LLM)",
                )
            )

        result.total_reasoning = "Fallback heuristic - no population changes"
        return result

    def _apply_population_changes(
        self,
        state: SimulationState,
        result: PopulationUpdateResult,
        pop_config: PopulationConfig,
    ) -> SimulationState:
        for shift in result.shifts:
            segment = next((item for item in pop_config.segments if item.id == shift.segment_id), None)
            if segment is not None:
                segment.share = shift.new_share

        # Normalize to ensure sum is 1.0 to pass validation
        total_share = sum(seg.share for seg in pop_config.segments)
        if total_share > 0 and abs(total_share - 1.0) > 1e-6:
            for seg in pop_config.segments:
                seg.share = seg.share / total_share

        if not hasattr(state, "_population_updates"):
            state._population_updates = []  # type: ignore[attr-defined]
        state._population_updates.append(result)  # type: ignore[attr-defined]

        return state

    def _apply_shift_constraints(self, shift: PopulationShift, pop_config: PopulationConfig) -> PopulationShift:
        if not pop_config.segments:
            return shift

        max_shift = pop_config.segments[0].share * MAX_SHARE_CHANGE_PER_ROUND
        if abs(shift.shift_amount) > max_shift:
            clamped_shift = max_shift if shift.shift_amount > 0 else -max_shift
            shift.new_share = shift.old_share + clamped_shift
            shift.shift_amount = clamped_shift
            shift.clamped = True

        shift.new_share = max(MIN_SEGMENT_SHARE, min(MAX_SEGMENT_SHARE, shift.new_share))
        return shift

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception as exc:
            logger.error(f"Failed to parse LLM response: {exc}")

        return {"segments": [], "overall_reasoning": "Parse failed"}

    def _build_cib_summary(self, cib_matrix: CIBMatrix | None) -> str:
        if cib_matrix is None:
            return "No CIB matrix available"

        influences: list[str] = []
        for cell in list(cib_matrix.cells.values())[:10]:
            if cell.influence != 0:
                influences.append(f"{cell.source_descriptor} -> {cell.target_descriptor}: {cell.influence:+d}")

        return "\n".join(influences) if influences else "No strong influences"

    def _build_historical_shifts(self, state: SimulationState, pop_config: PopulationConfig) -> str:
        updates = getattr(state, "_population_updates", [])[-3:]
        if not updates:
            return "No historical shifts yet"

        lines: list[str] = []
        for update in updates:
            lines.append(f"Round {update.round_number}:")
            for shift in update.shifts:
                lines.append(
                    f"  {shift.segment_id}: {shift.old_share:.1%} -> {shift.new_share:.1%} ({shift.shift_amount:+.1%})"
                )

        return "\n".join(lines)