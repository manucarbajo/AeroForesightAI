from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from pydantic import ValidationError

from src.agents.agent_dependencies import format_depends_on_block
from src.market.property_engine import scheduled_property_events
from src.models.agent_models import AgentConfig, AgentResponse, StateChange
from src.models.enums import AgentType, EventType
from src.models.event_models import EventLogEntry, RoundResult
from src.models.llm_models import LLMIncident
from src.models.state_models import SimulationState

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROMPT_FILES: dict[AgentType, str] = {
    AgentType.CONSUMER: "consumer.md",
    AgentType.PROVIDER: "provider.md",
    AgentType.REGULATOR: "regulator.md",
}

DEFAULT_EVENT_TYPE_BY_AGENT: dict[AgentType, EventType] = {
    AgentType.CONSUMER: EventType.DEMAND_SHIFT,
    AgentType.PROVIDER: EventType.PRICE_CHANGE,
    AgentType.REGULATOR: EventType.POLICY_CHANGE,
}


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str: ...


class AgentNode:
    def __init__(
        self,
        config: AgentConfig,
        llm: LLMCallable,
        prompts_dir: Path | None = None,
        recent_event_limit: int = 8,
    ) -> None:
        self.config = config
        self.llm = llm
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.recent_event_limit = recent_event_limit

    def invoke(self, state: SimulationState) -> SimulationState:
        prompt = self._build_prompt(state)
        try:
            raw_output = self.llm.call(prompt)
        except Exception as exc:
            # Der Lauf stirbt nicht an einem einzelnen Aussetzer — er verschweigt
            # ihn aber auch nicht mehr. Bis P0.1 lag hier ein zweiter Versuch über
            # `get_llm()`: war OLLAMA_MODEL gesetzt, lieferte der eine erfundene
            # Mock-Antwort, die im Output von einer echten nicht zu unterscheiden
            # war. Genau dieser Zweig ist weg. Was bleibt, ist ein sichtbarer
            # Leerzug plus Eintrag in `state.llm_incidents`.
            raw_output = self._record_llm_failure(state, exc)

        response, raw_event_entries = self._parse_response(
            raw_output, state.clock.current_tick, state=state
        )
        events = self._create_event_entries(state, response, raw_event_entries)

        state.round_results.append(
            RoundResult(
                round_number=state.clock.current_tick,
                agent_responses=[response],
                events=events,
                environment_snapshot=state.environment,
                summary=f"Agent run: {self.config.id}",
            )
        )
        state.event_log.extend(events)
        return state

    def _record_llm_failure(self, state: SimulationState, exc: Exception) -> str:
        """Ausfall protokollieren und den Leerzug liefern, den der Agent stattdessen tut."""

        logger.warning(
            "LLM-Aufruf für Agent %s in Tick %s fehlgeschlagen: %s. Der Agent setzt aus; "
            "der Lauf wird als beeinträchtigt markiert.",
            self.config.id,
            state.clock.current_tick,
            exc,
        )
        state.llm_incidents.append(
            LLMIncident(
                tick=state.clock.current_tick,
                caller=f"agent:{self.config.id}",
                kind="no_op_emitted",
                error=f"{type(exc).__name__}: {exc}",
            )
        )
        return json.dumps(
            {
                "reasoning": "llm_unavailable",
                "actions": ["NO_OP"],
                "state_changes": [],
                "events": [],
                "segment_analysis": {},
            },
            ensure_ascii=False,
        )

    def _build_prompt(self, state: SimulationState) -> str:
        template = self._load_prompt_template()
        factors_block = self._format_factors(state)
        recent_events_block = self._format_recent_events(state)
        scenario_block = self._format_market_metrics(state)
        population_context = self._build_population_context()
        consumer_segment_analysis = self._format_consumer_segment_analysis(state)
        observed_booking_block = self._format_observed_booking_block(state)
        prior_booking_block = self._format_prior_booking_block(state)
        depends_on_block = format_depends_on_block(state, self.config.profile, self.config.id)
        goals = "\n".join(f"- {goal}" for goal in self.config.goals) or "- No goals configured"
        constraints_list = list(self.config.constraints) if self.config.constraints else []
        if self.config.profile:
            p = self.config.profile
            if p.must_not_output:
                constraints_list.append(f"MUST NOT OUTPUT: {', '.join(p.must_not_output)}")
            if p.may_propose:
                constraints_list.append(f"MAY PROPOSE ONLY: {', '.join(p.may_propose)}")
            elif p.may_propose == []:
                constraints_list.append("MAY PROPOSE ONLY: (nothing — state_changes must be empty)")

        constraints = (
            "\n".join(f"- {constraint}" for constraint in constraints_list)
            if constraints_list
            else "- No constraints configured"
        )

        return self._render_template(
            template,
            {
                "agent_id": self.config.id,
                "agent_name": self.config.name,
                "agent_description": self.config.description,
                "round_number": state.clock.current_tick,
                "global_context": state.environment.global_context or "No global context set.",
                "goals": goals,
                "constraints": constraints,
                "scenario_block": scenario_block,
                "factors_block": factors_block,
                "recent_events_block": recent_events_block,
                "population_context": population_context,
                "consumer_segment_analysis": consumer_segment_analysis,
                "observed_booking_block": observed_booking_block,
                "prior_booking_block": prior_booking_block,
                "depends_on_block": depends_on_block,
            },
        )

    def _parse_response(
        self, raw_output: str, round_number: int, state: SimulationState
    ) -> tuple[AgentResponse, list[dict[str, Any]]]:
        payload = self._extract_json_payload(raw_output)
        if payload is None:
            return self._default_response(raw_output, round_number), []

        raw_event_entries = payload.get("events", [])
        if not isinstance(raw_event_entries, list):
            raw_event_entries = []

        try:
            segment_analysis_raw = payload.get("segment_analysis", {})
            if self.config.agent_type != AgentType.CONSUMER:
                segment_analysis: dict[str, Any] = {}
            elif isinstance(segment_analysis_raw, dict):
                # Consumer: erlauben nur bekannte Segment-IDs aus dem Populationskontext.
                known_segment_ids: set[str] = set()
                if self.config.population_config and self.config.population_config.segments:
                    known_segment_ids = {seg.id for seg in self.config.population_config.segments}

                segment_analysis = {}
                for key, value in segment_analysis_raw.items():
                    if not isinstance(key, str):
                        continue
                    if known_segment_ids and key not in known_segment_ids:
                        continue
                    if isinstance(value, str):
                        cleaned = value.strip()
                        if cleaned:
                            segment_analysis[key] = cleaned
            else:
                segment_analysis = {}

            response = AgentResponse(
                agent_id=self.config.id,
                round_number=round_number,
                reasoning=str(payload.get("reasoning", "")).strip() or "Kein Reasoning geliefert.",
                actions=[
                    str(action) for action in payload.get("actions", []) if str(action).strip()
                ],
                state_changes=self._parse_state_changes(
                    payload.get("state_changes", []), state=state
                ),
                segment_analysis=segment_analysis,
                raw_output=raw_output,
            )
            if not response.actions:
                response.actions = ["NO_OP"]
            return response, [entry for entry in raw_event_entries if isinstance(entry, dict)]
        except ValidationError:
            return self._default_response(raw_output, round_number), []

    def _create_event_entries(
        self,
        state: SimulationState,
        response: AgentResponse,
        raw_event_entries: list[dict[str, Any]],
    ) -> list[EventLogEntry]:
        if not raw_event_entries:
            if self._is_explicit_no_op(response):
                return []
            raw_event_entries = [
                {
                    "event_type": DEFAULT_EVENT_TYPE_BY_AGENT[self.config.agent_type].value,
                    "description": "Fallback event generated from parsed actions.",
                    "affected_factors": [change.factor_id for change in response.state_changes],
                }
            ]

        created: list[EventLogEntry] = []
        for raw_event in raw_event_entries:
            event_type = self._parse_event_type(raw_event.get("event_type"))
            if event_type == EventType.MARKET_EVENT:
                continue

            created.append(
                EventLogEntry(
                    id=str(uuid4()),
                    round_number=state.clock.current_tick,
                    source_agent=self.config.id,
                    event_type=event_type,
                    description=str(raw_event.get("description", "")).strip()
                    or "Ohne Beschreibung",
                    affected_factors=self._filter_factor_ids(
                        raw_event.get("affected_factors", []), state
                    ),
                    timestamp=datetime.now(UTC).isoformat(),
                )
            )

        return created

    @staticmethod
    def _is_explicit_no_op(response: AgentResponse) -> bool:
        if not response.actions:
            return False
        normalized = {
            str(action).strip().upper() for action in response.actions if str(action).strip()
        }
        return normalized == {"NO_OP"}

    def _load_prompt_template(self) -> str:
        prompt_file = PROMPT_FILES[self.config.agent_type]
        prompt_path = self.prompts_dir / prompt_file
        return prompt_path.read_text(encoding="utf-8")

    def _render_template(self, template: str, values: dict[str, Any]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace(f"{{{key}}}", str(value))
        return rendered

    def _format_factors(self, state: SimulationState) -> str:
        if self.config.profile and "factors F1,F5,F6" not in self.config.profile.observes:
            pass  # We should dynamically check observed_factors

        allowed_factors = None
        if self.config.profile:
            allowed_factors = self.config.profile.observed_factors
            if not allowed_factors:
                return "- No factors observed by this agent."

        lines: list[str] = []
        for factor in state.environment.factors.values():
            if allowed_factors is not None and factor.id not in allowed_factors:
                continue
            options = ", ".join(f"{sid}={desc}" for sid, desc in factor.possible_states.items())
            lines.append(
                f"- {factor.id} | {factor.name} | current={factor.current_state} | options: {options}"
            )

        if not lines:
            return "- No observed factors."
        return "\n".join(lines)

    def _format_recent_events(self, state: SimulationState) -> str:
        if self.config.profile and "event_log_recent" not in self.config.profile.observes:
            return "- Event log not observed by this agent."

        if not state.event_log:
            return "- No prior events."

        selected = state.event_log[-self.recent_event_limit :]
        lines = []
        for event in selected:
            factors = ", ".join(event.affected_factors) if event.affected_factors else "-"
            lines.append(
                f"- round={event.round_number} source={event.source_agent} "
                f"type={event.event_type.value} factors={factors} :: {event.description}"
            )
        return "\n".join(lines)

    def _format_market_metrics(self, state: SimulationState) -> str:
        """Format policy-driven market metrics for the agent prompt (M2)."""
        if self.config.profile:
            obs = self.config.profile.observes
            if (
                "market_metrics" not in obs
                and "cost_pressure" not in obs
                and "booking_rate" not in obs
            ):
                return "- Market metrics not observed by this agent."

        metrics = state.market_metrics
        header = "Deterministic market metrics (Python; not set by the agent):"

        if not metrics and state.resolved_properties().system_properties:
            from src.market.simulation_functions import compute_market_metrics

            tick = max(1, state.clock.current_tick)
            last_price = state.price_history[-1].price if state.price_history else 100.0
            last_demand = state.price_history[-1].demand_level if state.price_history else 1.0
            metrics = compute_market_metrics(
                tick,
                state.resolved_properties(),
                previous_price=last_price,
                previous_demand=last_demand,
            )
            header = (
                "Deterministic market metrics (Python; preview from properties.json; "
                "not set by the agent):"
            )

        if not metrics:
            return "- No market metrics available (properties.json / MarketNode)."

        lines = [header]
        for metric_id in sorted(metrics.keys()):
            if self.config.profile:
                obs = self.config.profile.observes
                if "market_metrics" not in obs and metric_id not in obs:
                    continue
            lines.append(f"- {metric_id}: {metrics[metric_id]}")
        return "\n".join(lines)

    def _build_population_context(self) -> str:
        if self.config.profile and "population_stats" not in self.config.profile.observes:
            return "- Population stats not observed by this agent."

        pop = self.config.population_config
        if not pop or not pop.segments:
            return "- No population context for this agent."

        lines: list[str] = [
            f"- total_population={pop.total_population}, default={pop.default_distribution.value}"
        ]
        for seg in pop.segments:
            lines.append(
                f"- segment {seg.id} ({seg.name}) share={seg.share} :: {seg.description or '-'}"
            )

            lines.append(
                "  - price_elasticity: " + self._format_distribution_config(seg.price_elasticity)
            )
            lines.append("  - income_level: " + self._format_distribution_config(seg.income_level))
            lines.append(
                "  - environmental_awareness: "
                + self._format_distribution_config(seg.environmental_awareness)
            )

        return "\n".join(lines)

    def _format_distribution_config(self, dist: Any) -> str:
        # Dist-Model ist in AP1 als pydantic-Modell definiert; wir formatieren generisch.
        dist_type = getattr(dist, "type", None)
        type_value = dist_type.value if hasattr(dist_type, "value") else str(dist_type)

        return (
            f"type={type_value}, mean={dist.mean}, std_dev={dist.std_dev}, "
            f"min_value={dist.min_value}, max_value={dist.max_value}"
        )

    def _format_consumer_segment_analysis(self, state: SimulationState) -> str:
        # Provider/Regulator: latest Python segment booking (prior tick or same tick after consumer).
        round_number = state.clock.current_tick
        for rr in reversed(state.round_results):
            if rr.round_number != round_number:
                continue
            for agent_response in rr.agent_responses:
                if agent_response.agent_id != "consumer":
                    continue
                if (
                    isinstance(agent_response.segment_analysis, dict)
                    and agent_response.segment_analysis
                ):
                    return json.dumps(agent_response.segment_analysis, ensure_ascii=True, indent=2)

        if state.population_stats:
            latest = state.population_stats[-1]
            segments = latest.get("segments", {})
            if segments:
                summary = {
                    segment_id: {
                        "booking_rate": stats.get("booking_rate"),
                        "booked": stats.get("booked_individuals"),
                        "total": stats.get("total_individuals"),
                    }
                    for segment_id, stats in segments.items()
                    if isinstance(stats, dict)
                }
                return json.dumps(summary, ensure_ascii=True, indent=2)

        return "{}"

    def _format_observed_booking_block(self, state: SimulationState) -> str:
        if self.config.agent_type != AgentType.CONSUMER:
            return "- Not applicable for this agent role."

        metrics = state.market_metrics
        if not metrics.get("booking_evaluated"):
            return "- Booking for this tick not yet evaluated."

        lines = [
            "Observed population booking (Python, this tick — ground truth for your narrative):",
            f"- booking_rate: {metrics.get('booking_rate')}",
            f"- ticket_price (provisional, pre-market-feedback): {metrics.get('ticket_price')}",
            f"- carbon_tax_level: {metrics.get('carbon_tax_level')}",
        ]
        if state.population_stats:
            latest = state.population_stats[-1]
            if latest.get("round_number") == state.clock.current_tick:
                lines.append(
                    f"- total_booked: {latest.get('total_booked')}/{latest.get('total_population')}"
                )
                for segment_id, stats in latest.get("segments", {}).items():
                    if isinstance(stats, dict):
                        lines.append(
                            f"- segment {segment_id}: booking_rate={stats.get('booking_rate')}, "
                            f"booked={stats.get('booked_individuals')}/{stats.get('total_individuals')}"
                        )
        lines.append(
            "- Events MUST match observed booking_rate (high booking → demand/booking, not mass exit)."
        )
        return "\n".join(lines)

    def _format_prior_booking_block(self, state: SimulationState) -> str:
        if self.config.agent_type not in {AgentType.PROVIDER, AgentType.REGULATOR}:
            return "- Not applicable for this agent role."

        current_tick = state.clock.current_tick
        prior_stats: dict[str, Any] | None = None
        prior_prior_stats: dict[str, Any] | None = None

        for entry in reversed(state.population_stats):
            round_number = entry.get("round_number")
            if round_number is None or round_number >= current_tick:
                continue
            if prior_stats is None:
                prior_stats = entry
            elif prior_prior_stats is None:
                prior_prior_stats = entry
                break

        lines = [
            "Observed population booking from the PRIOR completed tick "
            "(Python ground truth — react to this; do not invent demand):",
        ]

        if prior_stats is None:
            lines.append(
                "- No prior booking data (first tick). "
                "Base decisions on market metrics and scheduled policy changes only."
            )
        else:
            prior_tick = prior_stats.get("round_number")
            booking_rate = prior_stats.get("total_demand")
            lines.append(f"- prior_tick: {prior_tick}")
            lines.append(f"- booking_rate: {booking_rate}")
            lines.append(
                f"- total_booked: {prior_stats.get('total_booked')}/"
                f"{prior_stats.get('total_population')}"
            )
            for segment_id, stats in prior_stats.get("segments", {}).items():
                if isinstance(stats, dict):
                    lines.append(
                        f"- segment {segment_id}: booking_rate={stats.get('booking_rate')}, "
                        f"booked={stats.get('booked_individuals')}/"
                        f"{stats.get('total_individuals')}"
                    )
            if prior_prior_stats is not None:
                prev_rate = prior_prior_stats.get("total_demand")
                if prev_rate is not None and booking_rate is not None:
                    delta = float(booking_rate) - float(prev_rate)
                    lines.append(f"- booking_rate_delta_vs_prior: {delta:+.3f}")

        shocks = [
            event
            for event in scheduled_property_events(state.resolved_properties())
            if int(event["tick"]) == current_tick
        ]
        if shocks:
            lines.append("- scheduled_property_changes_this_tick:")
            for shock in shocks:
                lines.append(
                    f"  - {shock['property_id']} {shock['effect_type']} -> "
                    f"{shock['value']} ({shock.get('unit', '')})"
                )
        else:
            lines.append("- scheduled_property_changes_this_tick: none")

        lines.extend(
            [
                "- demand_level in market metrics is NOT booking_rate; use values above only.",
                "- Formulate exactly 1 event per tick that reflects your decision for this period.",
                "- On scheduled_property_changes_this_tick: event must react to the shock (new angle).",
                "- If prior booking_rate >= 0.5, do NOT describe mass exit to trains/buses/carriers.",
                '- Use actions=["NO_OP"] and events=[] ONLY when demand is stable '
                "(|booking_rate_delta| < 0.05), no property shock, and Recent events already cover the topic.",
                "- NEVER copy wording from Recent events; paraphrase or choose NO_OP.",
            ]
        )
        return "\n".join(lines)

    def _extract_json_payload(self, raw_output: str) -> dict[str, Any] | None:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1).strip()

        direct = self._try_decode_json(cleaned)
        if isinstance(direct, dict):
            return direct

        decoder = json.JSONDecoder()
        for index, char in enumerate(cleaned):
            if char != "{":
                continue
            try:
                obj, _ = decoder.raw_decode(cleaned[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                return obj
        return None

    def _try_decode_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _default_response(self, raw_output: str, round_number: int) -> AgentResponse:
        return AgentResponse(
            agent_id=self.config.id,
            round_number=round_number,
            reasoning="Fallback: Parsing der LLM-Antwort fehlgeschlagen.",
            actions=["NO_OP_PARSE_FALLBACK"],
            state_changes=[],
            raw_output=raw_output,
        )

    def _parse_state_changes(self, payload: Any, state: SimulationState) -> list[StateChange]:
        if not isinstance(payload, list):
            return []

        parsed: list[StateChange] = []
        valid_factors = state.environment.factors
        for item in payload:
            if not isinstance(item, dict):
                continue

            factor_id = str(item.get("factor_id", "")).strip()
            proposed_state = str(item.get("proposed_state", "")).strip()
            reasoning = str(item.get("reasoning", "")).strip() or "Keine Begruendung"

            if not factor_id or not proposed_state:
                continue
            if factor_id not in valid_factors:
                continue

            if self.config.profile and self.config.profile.may_propose is not None:
                allowed = self.config.profile.may_propose
                if f"factor_state {factor_id}" not in allowed:
                    continue

            factor = valid_factors[factor_id]
            if proposed_state not in factor.possible_states:
                continue

            parsed.append(
                StateChange(
                    factor_id=factor_id,
                    proposed_state=proposed_state,
                    reasoning=reasoning,
                )
            )

        return parsed

    def _parse_event_type(self, value: Any) -> EventType:
        if isinstance(value, str):
            for event_type in EventType:
                if event_type.value == value:
                    return event_type
        return DEFAULT_EVENT_TYPE_BY_AGENT[self.config.agent_type]

    def _filter_factor_ids(self, value: Any, state: SimulationState) -> list[str]:
        if not isinstance(value, list):
            return []
        valid_ids = set(state.environment.factors.keys())
        return [
            factor_id
            for factor_id in value
            if isinstance(factor_id, str) and factor_id in valid_ids
        ]
