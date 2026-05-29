"""Szenario-Konsistenzprüfung
ConsistencyChecker: Prüft ob Zustandskombinationen konsistent sind
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


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class ScenarioDescriptor:
    """Ein Szenario: eine vollständige Zustandskombination aller 7 Faktoren.

    Struktur: factor_states = {"F1": "F1.1", "F2": "F2.2", ..., "F7": "F7.1"}
    """
    factor_states: dict[str, str]  # Factor ID -> Descriptor ID (z.B. "F1" -> "F1.1")
    consistency_score: float = 0.0  # 0-1: wie konsistent ist dieses Szenario?
    stability_index: float = 0.0    # 0-1: wie stabil unter den gegeben Wechselwirkungen?
    reasoning: str = ""              # Kurze Erklärung warum dieses Szenario plausibel ist


class ConsistencyCheckResult(BaseModel):
    """Ergebnis einer Konsistenzprüfung."""
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


# ---------------------------------------------------------------------------
# Core Consistency Checker
# ---------------------------------------------------------------------------


class ConsistencyChecker:
    """Prüft ob Zustandskombinationen konsistent sind.

    Ein Szenario ist konsistent, wenn die Wechselwirkungen zwischen den
    Faktor-Zuständen keine starken gegenseitigen Widersprüche erzeugen.
    """

    def __init__(self, cib_matrix: CIBMatrix, conflict_threshold: float = -1.5):
        """
        Args:
            cib_matrix: Die CIB-Matrix zur Konsistenzprüfung
            conflict_threshold: Ab wann gilt eine Wechselwirkung als Konflikt?
                                (Default: -1.5, also ≤ -2 ist ein Konflikt)
        """
        self.cib_matrix = cib_matrix
        self.conflict_threshold = conflict_threshold
        self.matrix_array = cib_matrix.to_numpy()

    def check_scenario(self, scenario: ScenarioDescriptor) -> ConsistencyCheckResult:
        """Prüft ob ein Szenario intern konsistent ist.

        Algorithmus:
        1. Für jedes Faktor-Paar im Szenario: hole die Wechselwirkung
        2. Wenn eine Wechselwirkung ≤ conflict_threshold: merke als Konflikt
        3. Summiere alle Konflikt-Stärken

        Returns:
            ConsistencyCheckResult mit Details der Konflikte
        """
        result = ConsistencyCheckResult()
        conflicts = []
        conflict_sum = 0.0

        # Hole die Descriptor IDs für dieses Szenario
        descriptors = [scenario.factor_states[fid] for fid in FACTOR_IDS]

        # Prüfe alle Wechselwirkungen innerhalb dieses Szenarios
        for i, src_desc in enumerate(descriptors):
            for j, tgt_desc in enumerate(descriptors):
                if i == j:
                    continue  # Kein Selbst-Einfluss

                influence = self.cib_matrix.get_influence(src_desc, tgt_desc)

                # Ist das ein Konflikt?
                if influence <= self.conflict_threshold:
                    conflict_msg = (
                        f"{src_desc} → {tgt_desc}: influence={influence} "
                        f"(conflict threshold: {self.conflict_threshold})"
                    )
                    conflicts.append(conflict_msg)
                    conflict_sum += abs(influence)  # Summiere absolute Stärke

        result.is_consistent = len(conflicts) == 0
        result.conflicts = conflicts
        result.total_conflict_strength = conflict_sum
        result.details = {
            "num_conflicts": len(conflicts),
            "scenario": scenario.factor_states,
        }

        return result

    def compute_consistency_score(self, scenario: ScenarioDescriptor) -> float:
        """Berechnet einen Konsistenz-Score (0-1) für ein Szenario.

        Nutzt die Wechselwirkungsstärken um zu bewerten wie "harmonisch"
        ein Szenario ist. Positive Wechselwirkungen erhöhen den Score,
        negative verminderin ihn.

        Returns:
            Float zwischen 0 (sehr inkonsistent) und 1 (sehr konsistent)
        """
        descriptors = [scenario.factor_states[fid] for fid in FACTOR_IDS]

        total_strength = 0.0
        positive_sum = 0.0
        negative_sum = 0.0

        for i, src_desc in enumerate(descriptors):
            for j, tgt_desc in enumerate(descriptors):
                if i == j:
                    continue
                influence = self.cib_matrix.get_influence(src_desc, tgt_desc)
                total_strength += abs(influence)
                if influence > 0:
                    positive_sum += influence
                else:
                    negative_sum += abs(influence)

        if total_strength == 0:
            return 0.5  # Neutral

        # Score = (positive - negative) / total normalisiert auf 0-1
        raw_score = (positive_sum - negative_sum) / total_strength
        normalized_score = (raw_score + 1) / 2  # Skaliere auf [0, 1]
        return max(0.0, min(1.0, normalized_score))

    def compute_stability_index(self, scenario: ScenarioDescriptor) -> float:
        """Berechnet einen Stabilitäts-Index (0-1).

        Misst wie stabil ein Szenario unter den Wechselwirkungen ist.
        Ein stabiles Szenario hat wenige starke negative Einflüsse.

        Returns:
            Float zwischen 0 (sehr instabil) und 1 (sehr stabil)
        """
        descriptors = [scenario.factor_states[fid] for fid in FACTOR_IDS]

        # Zähle stark negative Wechselwirkungen
        strong_negative_count = 0
        total_interactions = 0

        for i, src_desc in enumerate(descriptors):
            for j, tgt_desc in enumerate(descriptors):
                if i == j:
                    continue
                influence = self.cib_matrix.get_influence(src_desc, tgt_desc)
                total_interactions += 1
                if influence <= -2:
                    strong_negative_count += 1

        if total_interactions == 0:
            return 0.5

        # Stabilität = 1 - (starke negative / gesamt)
        stability = 1.0 - (strong_negative_count / total_interactions)
        return max(0.0, min(1.0, stability))


# ---------------------------------------------------------------------------
# Scenario Generator
# ---------------------------------------------------------------------------


class ScenarioDeriver:
    """Generiert konsistente Szenarien aus einer CIB-Matrix."""

    def __init__(self, cib_matrix: CIBMatrix, conflict_threshold: float = -1.5):
        self.cib_matrix = cib_matrix
        self.checker = ConsistencyChecker(cib_matrix, conflict_threshold)

    def derive_scenarios(
        self,
        top_n: int = 3,
        allow_inconsistent: bool = False,
    ) -> ScenarioDerivationResult:
        """Leitet die Top-N konsistentesten Szenarien ab.

        Brute-Force-Ansatz: Generiere alle 2^7 = 128 möglichen
        Zustandskombinationen, prüfe Konsistenz, und sortiere nach Score.

        Args:
            top_n: Wie viele Top-Szenarien sollen zurück gegeben werden?
            allow_inconsistent: Auch inkonsistente Szenarien einbeziehen?

        Returns:
            ScenarioDerivationResult mit bis zu top_n besten Szenarien
        """
        result = ScenarioDerivationResult(matrix_round=self.cib_matrix.round_generated)

        # Generiere alle möglichen Szenarien
        all_scenarios = []

        # Für jeden Faktor: wähle einen der beiden Zustände
        for state_combo in product(range(STATES_PER_FACTOR), repeat=NUM_FACTORS):
            # state_combo = (0, 1, 0, 1, 0, 0, 1) bedeutet:
            # F1.1, F2.2, F3.1, F4.2, F5.1, F6.1, F7.2
            factor_states = {}
            for factor_idx, state_idx in enumerate(state_combo):
                factor_id = f"F{factor_idx + 1}"
                descriptor_id = f"F{factor_idx + 1}.{state_idx + 1}"
                factor_states[factor_id] = descriptor_id

            scenario = ScenarioDescriptor(factor_states=factor_states)

            # Berechne Scores
            consistency = self.checker.compute_consistency_score(scenario)
            stability = self.checker.compute_stability_index(scenario)
            scenario.consistency_score = consistency
            scenario.stability_index = stability

            # Prüfe ob konsistent
            check = self.checker.check_scenario(scenario)
            is_consistent = check.is_consistent

            # Entscheide ob einzubeziehen
            if is_consistent or allow_inconsistent:
                all_scenarios.append({
                    "scenario": scenario,
                    "is_consistent": is_consistent,
                    "combined_score": (consistency + stability) / 2,
                })

        result.total_evaluated = len(all_scenarios)
        result.consistent_count = sum(1 for s in all_scenarios if s["is_consistent"])

        # Sortiere nach kombiniertem Score (absteigend)
        all_scenarios.sort(key=lambda x: x["combined_score"], reverse=True)

        # Nehme Top-N
        for item in all_scenarios[:top_n]:
            scenario = item["scenario"]
            scenario.reasoning = self._build_reasoning(scenario, item["is_consistent"])
            result.scenarios.append(scenario)

        result.metadata = {
            "conflict_threshold": self.checker.conflict_threshold,
            "allow_inconsistent": allow_inconsistent,
            "total_possible": 2 ** NUM_FACTORS,
        }

        return result

    def _build_reasoning(self, scenario: ScenarioDescriptor, is_consistent: bool) -> str:
        """Generiert eine kurze Textbegründung für ein Szenario."""
        check = self.checker.check_scenario(scenario)

        lines = []
        lines.append(
            f"Consistency: {scenario.consistency_score:.2f} | "
            f"Stability: {scenario.stability_index:.2f} | "
            f"Status: {'✓ Konsistent' if is_consistent else '⚠ Konflikte'}"
        )

        if check.conflicts:
            lines.append(f"Konflikte ({len(check.conflicts)}):")
            for conflict in check.conflicts[:3]:  # Zeige erste 3
                lines.append(f"  - {conflict}")
            if len(check.conflicts) > 3:
                lines.append(f"  ... und {len(check.conflicts) - 3} weitere")

        return " | ".join(lines)


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


def scenarios_to_dict(result: ScenarioDerivationResult) -> dict[str, Any]:
    """Konvertiert ScenarioDerivationResult zu JSON-serialisierbar Dict."""
    return {
        "matrix_round": result.matrix_round,
        "total_evaluated": result.total_evaluated,
        "consistent_count": result.consistent_count,
        "scenarios": [
            {
                "factor_states": s.factor_states,
                "consistency_score": s.consistency_score,
                "stability_index": s.stability_index,
                "reasoning": s.reasoning,
            }
            for s in result.scenarios
        ],
        "metadata": result.metadata,
    }