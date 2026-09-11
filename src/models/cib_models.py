"""CIB (Cross-Impact Balance) matrix data models.

Implements a 14×14 cross-impact matrix for 7 factors with 2 states each.
Scale: -3 (strongly inhibiting) to +3 (strongly promoting), 0 = no influence.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_INFLUENCE = -3
MAX_INFLUENCE = 3
NUM_FACTORS = 7
STATES_PER_FACTOR = 2
MATRIX_SIZE = NUM_FACTORS * STATES_PER_FACTOR  # 14

FACTOR_IDS = [f"F{i}" for i in range(1, NUM_FACTORS + 1)]
DESCRIPTOR_IDS = [
    f"F{f}.{s}" for f in range(1, NUM_FACTORS + 1) for s in range(1, STATES_PER_FACTOR + 1)
]


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------


class CIBCell(BaseModel):
    """A single cell in the CIB matrix representing the influence of one descriptor on another."""

    source_descriptor: str = Field(description="Source descriptor ID, e.g. 'F1.1'")
    target_descriptor: str = Field(description="Target descriptor ID, e.g. 'F2.2'")
    influence: int = Field(description="Influence score (-3 to +3)")
    reasoning: str = Field(default="", description="LLM reasoning for this assessment")

    @field_validator("influence", mode="before")
    @classmethod
    def clamp_influence(cls, v: int) -> int:
        return max(MIN_INFLUENCE, min(MAX_INFLUENCE, int(v)))


class FactorScore(BaseModel):
    """Active and passive scores for a single factor."""

    factor_id: str
    active_score: int = Field(
        default=0, description="Row sum: how strongly this factor influences others"
    )
    passive_score: int = Field(
        default=0, description="Column sum: how strongly this factor is influenced"
    )

    @property
    def activity_ratio(self) -> float:
        """Ratio > 1 means the factor is more active than passive."""
        if self.passive_score == 0:
            return float(self.active_score) if self.active_score != 0 else 0.0
        return self.active_score / self.passive_score


class CIBMatrix(BaseModel):
    """Full 14×14 CIB cross-impact matrix."""

    cells: dict[str, CIBCell] = Field(
        default_factory=dict,
        description="Mapping of 'source|target' keys to CIBCell values",
    )
    entries: list[CIBEntry] = Field(
        default_factory=list,
        description="Deprecated: flat entry list for backward compatibility with C2 code",
    )
    round_generated: int = Field(description="Simulation round in which this matrix was generated")
    factor_scores: list[FactorScore] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def cell_key(source: str, target: str) -> str:
        return f"{source}|{target}"

    def get_cell(self, source: str, target: str) -> CIBCell | None:
        return self.cells.get(self.cell_key(source, target))

    def set_cell(self, cell: CIBCell) -> None:
        self.cells[self.cell_key(cell.source_descriptor, cell.target_descriptor)] = cell

    def get_influence(self, source: str, target: str) -> int:
        cell = self.get_cell(source, target)
        return cell.influence if cell else 0

    def compute_factor_scores(self) -> list[FactorScore]:
        """Compute active/passive scores per factor from the matrix cells."""
        scores: dict[str, FactorScore] = {fid: FactorScore(factor_id=fid) for fid in FACTOR_IDS}

        for cell in self.cells.values():
            source_factor = cell.source_descriptor.split(".")[0]
            target_factor = cell.target_descriptor.split(".")[0]

            if source_factor in scores:
                scores[source_factor].active_score += abs(cell.influence)
            if target_factor in scores:
                scores[target_factor].passive_score += abs(cell.influence)

        self.factor_scores = list(scores.values())
        return self.factor_scores

    def to_numpy(self) -> np.ndarray:
        """Convert to a 14×14 numpy array ordered by DESCRIPTOR_IDS."""
        matrix = np.zeros((MATRIX_SIZE, MATRIX_SIZE), dtype=int)
        for i, src in enumerate(DESCRIPTOR_IDS):
            for j, tgt in enumerate(DESCRIPTOR_IDS):
                cell = self.get_cell(src, tgt)
                if cell:
                    matrix[i, j] = cell.influence
        return matrix

    @classmethod
    def from_numpy(
        cls, matrix: np.ndarray, round_generated: int, reasoning_map: dict[str, str] | None = None
    ) -> CIBMatrix:
        """Create a CIBMatrix from a 14×14 numpy array."""
        reasoning_map = reasoning_map or {}
        cells: dict[str, CIBCell] = {}
        for i, src in enumerate(DESCRIPTOR_IDS):
            for j, tgt in enumerate(DESCRIPTOR_IDS):
                if src.split(".")[0] == tgt.split(".")[0]:
                    continue  # skip same-factor cells
                key = cls.cell_key(src, tgt)
                cells[key] = CIBCell(
                    source_descriptor=src,
                    target_descriptor=tgt,
                    influence=int(matrix[i, j]),
                    reasoning=reasoning_map.get(key, ""),
                )
        instance = cls(cells=cells, round_generated=round_generated)
        instance.compute_factor_scores()
        return instance

    @classmethod
    def empty(cls, round_generated: int = 0) -> CIBMatrix:
        """Create an empty matrix with all influences set to 0."""
        return cls.from_numpy(
            np.zeros((MATRIX_SIZE, MATRIX_SIZE), dtype=int),
            round_generated=round_generated,
        )

    @property
    def is_complete(self) -> bool:
        """Check if all cross-factor cells are filled."""
        expected = MATRIX_SIZE * MATRIX_SIZE - NUM_FACTORS * (STATES_PER_FACTOR**2)
        return len(self.cells) >= expected


# ---------------------------------------------------------------------------
# Deprecated aliases (backward compatibility with C2 code)
# ---------------------------------------------------------------------------


class CIBEntry(BaseModel):
    """Deprecated: Use CIBCell instead. Kept for backward compatibility."""

    source_factor: str
    target_factor: str
    influence_score: float
    reasoning: str = ""
