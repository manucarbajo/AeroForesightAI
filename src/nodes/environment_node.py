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
    """Protocol für LLM-Clients."""

    def call(self, prompt: str) -> str: ...