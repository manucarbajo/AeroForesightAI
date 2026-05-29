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
