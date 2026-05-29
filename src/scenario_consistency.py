"""Szenario-Konsistenzprüfung
ConsistencyChecker: Prüft ob Zustandskombinationen konsistent sind
ScenarioDeriver: Generiert Top-N konsistente Szenarien
Scoring-Funktionen: Bewertet Szenarien nach Stabilität und Konsistenz
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from src.models.cib_models import (
    CIBMatrix,
    DESCRIPTOR_IDS,
    FACTOR_IDS,
    NUM_FACTORS,
    STATES_PER_FACTOR,
)

logger = logging.getLogger(__name__)

# Data Models
@dataclass
class ScenarioDescriptor:
    """vollständige Zustandskombination aller 7 Faktoren.
        Struktur: factor_states = {"F1": "F1.1", "F2": "F2.2", ..., "F7": "F7.1"}
    """
    factor_states: dict[str, str]  # Factor ID -> Descriptor ID (z.B. "F1" -> "F1.1")
    consistency_score: float = 0.0  # 0-1: wie konsistent ist dieses Szenario?
    stability_index: float = 0.0    # 0-1: wie stabil unter den gegeben Wechselwirkungen?
    reasoning: str = ""              # Kurze Erklärung warum dieses Szenario plausibel ist

class ConsistencyCheckResult(BaseModel):
    """Ergebnis der Konsistenzprüfung."""
    is_consistent: bool = True
    conflicts: list[str] = Field(default_factory=list)
    total_conflict_strength: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)

class ScenarioDerivationResult(BaseModel):
    """Ergebnis der Szenario-Ableitung."""
    scenarios: list[ScenarioDescriptor] = Field(default_factory=list)
    total_evaluated: int = 0
    consistent_count: int = 0
    matrix_round: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
