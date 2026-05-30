"""Environment Agent Node für Challenge 3 mit Bevölkerungsänderungen

Dieser Node entscheidet pro Runde die Populationsverschiebungen basierend auf:
- Faktor-Zustände
- CIB-Matrix
- Bisherige Bevölkerungsentwicklung
- LLM-basierte Begründung

Beschränkungen:
- Maximal 5% Verschiebung pro Segment pro Runde (MAX_SHARE_CHANGE_PER_ROUND)
- Segmente können überlappen
- Änderungen werden geloggt
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from pydantic import BaseModel, Field

from src.models.cib_models import CIBMatrix
from src.models.population_models import ConsumerSegment, PopulationConfig
from src.models.state_models import SimulationState

logger = logging.getLogger(__name__)

# Max. Verschiebung pro Segment pro Runde
MAX_SHARE_CHANGE_PER_ROUND = 0.05  # 5%
MIN_SEGMENT_SHARE = 0.0
MAX_SEGMENT_SHARE = 1.0


class LLMCallable(Protocol):
    """Protocol für LLM-Clients"""

    def call(self, prompt: str) -> str: ...


class PopulationShift(BaseModel):
    """Bevölkerungsverschiebung je Segment"""
    segment_id: str
    segment_name: str
    old_share: float
    new_share: float
    shift_amount: float
    reasoning: str
    clamped: bool = False  #War die Verschiebung durch Max-Constraint begrenzt?


class PopulationUpdateResult(BaseModel):
    """Ergebnis einer Veränderung der Bevölkerung"""
    round_number: int
    shifts: list[PopulationShift] = Field(default_factory=list)
    total_reasoning: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

# Prompts
POPULATION_UPDATE_SYSTEM_PROMPT = """Du bist ein Experte für Bevölkerungsdynamik und Marktentwicklung im Flugverkehr.

Deine Aufgabe: Prognostiziere die Verschiebung der Konsumenten-Segmente für die nächste Runde.

Input:
- Aktuelle Segment-Anteile
- Aktuelle Faktor-Zustände (Mobilitätsbedürfnis, Regulierung, Technologie, etc.)
- CIB-Matrix (wie Faktoren sich gegenseitig beeinflussen)
- Bisherige Bevölkerungstrends

Output:
- Neue Segment-Anteile (prozentual)
- Begründung für jede Verschiebung
- Max. 5% Verschiebung pro Segment pro Runde

Wichtig:
- Begründe mit Faktoren-Zuständen und CIB-Wechselwirkungen
- Segmente können überlappen (ein Passenger kann mehrere Labels haben)
- Alle Anteile müssen zusammen ≤ 100% ergeben (erlaubt Überlappung)
"""

POPULATION_UPDATE_USER_PROMPT_TEMPLATE = """Runde: {round_number}

Aktuelle Segment-Anteile:
{segments_json}

Aktuelle Faktor-Zustände:
{factors_json}

CIB-Matrix Zusammenfassung (Top 10 Wechselwirkungen):
{cib_summary}

Bisherige Verschiebungen (letzte 3 Runden):
{historical_shifts}

Prognostiziere die neuen Segment-Anteile und begründe jede Verschiebung.

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

# Environment Agent Node
class EnvironmentAgentNode:

    def __init__(self, llm: LLMCallable | None = None):
                self.llm = llm

    def invoke(self, state: SimulationState) -> SimulationState:

        round_number = state.clock.current_round

        # Hole Population-Config aus Consumer-Agent
        pop_config = self._extract_population_config(state)
        if pop_config is None:
            logger.warning("No population config found, skipping population update")
            return state

        # Berechne neue Segment-Anteile
        result = self._update_population(
            state=state,
            pop_config=pop_config,
            round_number=round_number
        )

        # Wende Änderungen an
        state = self._apply_population_changes(state, result, pop_config)

        # Logge Änderungen
        if result.shifts:
            logger.info(
                f"Round {round_number}: Population update - "
                f"{len(result.shifts)} segments shifted"
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
            round_number: int
    ) -> PopulationUpdateResult:
        result = PopulationUpdateResult(round_number=round_number)

        if self.llm:
            result = self._update_with_llm(state, pop_config, round_number)
        else:
            result = self._update_with_heuristic(state, pop_config, round_number)

        return result

    def _update_with_llm(
            self,
            state: SimulationState,
            pop_config: PopulationConfig,
            round_number: int
    ) -> PopulationUpdateResult:
        """LLM-basiertes Update."""
        # Baue Prompts zusammen
        segments_json = json.dumps(
            [s.model_dump() for s in pop_config.segments],
            indent=2
        )

        factors_json = json.dumps(
            {fid: f.current_state for fid, f in state.environment.factors.items()},
            indent=2
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

        # Rufe LLM auf
        try:
            response = self.llm.call(user_prompt)
            llm_output = self._parse_llm_response(response)
        except Exception as e:
            logger.error(f"LLM call failed: {e}, falling back to heuristic")
            return self._update_with_heuristic(state, pop_config, round_number)

        # Baue PopulationUpdateResult
        result = PopulationUpdateResult(
            round_number=round_number,
            total_reasoning=llm_output.get("overall_reasoning", "")
        )

        for segment in pop_config.segments:
            seg_update = next(
                (s for s in llm_output.get("segments", []) if s.get("id") == segment.id),
                None
            )

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

            # Prüfe Constraints
            shift = self._apply_shift_constraints(shift, pop_config)
            result.shifts.append(shift)

        return result

    def _update_with_heuristic(
            self,
            state: SimulationState,
            pop_config: PopulationConfig,
            round_number: int
    ) -> PopulationUpdateResult:
        """Fallback: Einfache Heuristik für Tests."""
        result = PopulationUpdateResult(round_number=round_number)

        for segment in pop_config.segments:
            # Sehr einfache Heuristik: kleine zufällige Shifts
            shift = PopulationShift(
                segment_id=segment.id,
                segment_name=segment.name,
                old_share=segment.share,
                new_share=segment.share,  # Keine Änderung
                shift_amount=0.0,
                reasoning="Heuristic: No change (waiting for LLM)",
            )
            result.shifts.append(shift)

        result.total_reasoning = "Fallback heuristic - no population changes"
        return result

    def _apply_population_changes(
            self,
            state: SimulationState,
            result: PopulationUpdateResult,
            pop_config: PopulationConfig
    ) -> SimulationState:
        """Wende Segment-Änderungen auf State an."""
        for shift in result.shifts:
            # Finde Segment in Population-Config
            segment = next(
                (s for s in pop_config.segments if s.id == shift.segment_id),
                None
            )
            if segment:
                segment.share = shift.new_share

        # Speichere Result im State (für Audit-Trail)
        if not hasattr(state, "_population_updates"):
            state._population_updates = []  # type: ignore
        state._population_updates.append(result)  # type: ignore

        return state

    def _apply_shift_constraints(
            self,
            shift: PopulationShift,
            pop_config: PopulationConfig
    ) -> PopulationShift:
        # Maximal eine Veränderung von 5% pro Segment
        max_shift = pop_config.segments[0].share * MAX_SHARE_CHANGE_PER_ROUND

        if abs(shift.shift_amount) > max_shift:
            clamped_shift = max_shift if shift.shift_amount > 0 else -max_shift
            shift.new_share = shift.old_share + clamped_shift
            shift.shift_amount = clamped_shift
            shift.clamped = True

        # Clamp auf [0, 1]
        shift.new_share = max(MIN_SEGMENT_SHARE, min(MAX_SEGMENT_SHARE, shift.new_share))

        return shift

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        try:
            # Versuche JSON zu extrahieren
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")

        return {"segments": [], "overall_reasoning": "Parse failed"}

    def _build_cib_summary(self, cib_matrix: CIBMatrix | None) -> str:
        #Baue eine kurze Zusammenfassung der CIB-Matrix
        if cib_matrix is None:
            return "No CIB matrix available"

        # Hole Top-10 stärkste Wechselwirkungen
        influences = []
        for cell in list(cib_matrix.cells.values())[:10]:
            if cell.influence != 0:
                influences.append(
                    f"{cell.source_descriptor} → {cell.target_descriptor}: {cell.influence:+d}"
                )

        return "\n".join(influences) if influences else "No strong influences"

    def _build_historical_shifts(self, state: SimulationState, pop_config: PopulationConfig) -> str:
        #Baue eine Zusammenfassung der bisherigen Verschiebungen
        updates = getattr(state, "_population_updates", [])[-3:]

        if not updates:
            return "No historical shifts yet"

        lines = []
        for update in updates:
            lines.append(f"Round {update.round_number}:")
            for shift in update.shifts:
                lines.append(
                    f"  {shift.segment_id}: {shift.old_share:.1%} → {shift.new_share:.1%} "
                    f"({shift.shift_amount:+.1%})"
                )

        return "\n".join(lines)