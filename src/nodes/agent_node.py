from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from pydantic import ValidationError

from src.models.agent_models import AgentConfig, AgentResponse, StateChange
from src.models.enums import AgentType, EventType
from src.models.event_models import EventLogEntry, RoundResult
from src.models.state_models import SimulationState

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
    def call(self, prompt: str) -> str:
        ...


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
            # Best-effort fallback to Studio mock LLM to avoid aborting the whole run
            try:
                from src.studio_helpers import get_llm

                print(f"LLM call failed for agent {self.config.id}: {exc}. Falling back to mock LLM.")
                fallback = get_llm()
                raw_output = fallback.call(prompt)
            except Exception:
                # Last-resort: produce a default NO-OP payload
                print(f"Fallback LLM also failed for agent {self.config.id}: {exc}. Using default NO_OP.")
                raw_output = json.dumps({
                    "reasoning": "fallback",
                    "actions": ["NO_OP"],
                    "state_changes": [],
                    "events": [],
                    "segment_analysis": {},
                }, ensure_ascii=False)

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

    def _build_prompt(self, state: SimulationState) -> str:
        template = self._load_prompt_template()
        factors_block = self._format_factors(state)
        recent_events_block = self._format_recent_events(state)
        scenario_block = self._format_scenario_parameters(state)
        population_context = self._build_population_context()
        consumer_segment_analysis = self._format_consumer_segment_analysis(state)
        goals = "\n".join(f"- {goal}" for goal in self.config.goals) or "- Keine Ziele konfiguriert"
        constraints = (
            "\n".join(f"- {constraint}" for constraint in self.config.constraints)
            if self.config.constraints
            else "- Keine Constraints konfiguriert"
        )

        return self._render_template(
            template,
            {
                "agent_id": self.config.id,
                "agent_name": self.config.name,
                "agent_description": self.config.description,
                "round_number": state.clock.current_tick,
                "global_context": state.environment.global_context
                or "Kein globaler Kontext gesetzt.",
                "goals": goals,
                "constraints": constraints,
                "scenario_block": scenario_block,
                "factors_block": factors_block,
                "recent_events_block": recent_events_block,
                "population_context": population_context,
                "consumer_segment_analysis": consumer_segment_analysis,
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
                actions=[str(action) for action in payload.get("actions", []) if str(action).strip()],
                state_changes=self._parse_state_changes(payload.get("state_changes", []), state=state),
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
                    description=str(raw_event.get("description", "")).strip() or "Ohne Beschreibung",
                    affected_factors=self._filter_factor_ids(
                        raw_event.get("affected_factors", []), state
                    ),
                    timestamp=datetime.now(UTC).isoformat(),
                )
            )

        return created

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
        lines: list[str] = []
        for factor in state.environment.factors.values():
            options = ", ".join(
                f"{sid}={desc}" for sid, desc in factor.possible_states.items()
            )
            lines.append(
                f"- {factor.id} | {factor.name} | current={factor.current_state} | options: {options}"
            )
        return "\n".join(lines)

    def _format_recent_events(self, state: SimulationState) -> str:
        if not state.event_log:
            return "- Keine vorherigen Events vorhanden."

        selected = state.event_log[-self.recent_event_limit :]
        lines = []
        for event in selected:
            factors = ", ".join(event.affected_factors) if event.affected_factors else "-"
            lines.append(
                f"- round={event.round_number} source={event.source_agent} "
                f"type={event.event_type.value} factors={factors} :: {event.description}"
            )
        return "\n".join(lines)

    def _format_scenario_parameters(self, state: SimulationState) -> str:
        lines: list[str] = []

        if state.market_metrics:
            lines.append("Deterministische Marktmetriken (Python, nicht vom Agenten zu setzen):")
            for metric_id in sorted(state.market_metrics.keys()):
                lines.append(f"- {metric_id}: {state.market_metrics[metric_id]}")
            lines.append("")

        if not state.config.scenario_parameters:
            if not lines:
                return "- Keine Szenarioparameter konfiguriert."
            return "\n".join(lines).rstrip()

        for param in state.config.scenario_parameters:
            if state.market_metrics and param.id in state.market_metrics:
                continue
            desc = f" :: {param.description}" if param.description else ""
            unit = f" {param.unit}" if param.unit else ""
            lines.append(
                f"- {param.id} ({param.name}): value={param.value}{unit}{desc}"
            )
        return "\n".join(lines)

    def _build_population_context(self) -> str:
        pop = self.config.population_config
        if not pop or not pop.segments:
            return "- Kein Populationskontext für dieses Agent."

        lines: list[str] = [f"- total_population={pop.total_population}, default={pop.default_distribution.value}"]
        for seg in pop.segments:
            lines.append(
                f"- segment {seg.id} ({seg.name}) share={seg.share} :: {seg.description or '-'}"
            )

            lines.append(
                "  - price_elasticity: "
                + self._format_distribution_config(seg.price_elasticity)
            )
            lines.append(
                "  - income_level: "
                + self._format_distribution_config(seg.income_level)
            )
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
        # Provider/Regulator sollen (im MVP) die Consumer-segmentspezifische Analyse sehen.
        round_number = state.clock.current_tick
        for rr in reversed(state.round_results):
            if rr.round_number != round_number:
                continue
            for agent_response in rr.agent_responses:
                if agent_response.agent_id != "consumer":
                    continue
                if isinstance(agent_response.segment_analysis, dict) and agent_response.segment_analysis:
                    return json.dumps(agent_response.segment_analysis, ensure_ascii=True, indent=2)
                return "{}"

        return "{}"

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
        return [factor_id for factor_id in value if isinstance(factor_id, str) and factor_id in valid_ids]
