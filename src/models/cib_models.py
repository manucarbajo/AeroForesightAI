"""CIB (Cross-Impact Balance) matrix data models.

Implements a 14×14 cross-impact matrix for 7 factors with 2 states each.
Scale: -3 (strongly inhibiting) to +3 (strongly promoting), 0 = no influence.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator


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
    active_score: int = Field(default=0, description="Row sum: how strongly this factor influences others")
    passive_score: int = Field(default=0, description="Column sum: how strongly this factor is influenced")

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
        scores: dict[str, FactorScore] = {
            fid: FactorScore(factor_id=fid) for fid in FACTOR_IDS
        }

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
    def from_numpy(cls, matrix: np.ndarray, round_generated: int, reasoning_map: dict[str, str] | None = None) -> CIBMatrix:
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
        expected = MATRIX_SIZE * MATRIX_SIZE - NUM_FACTORS * (STATES_PER_FACTOR ** 2)
        return len(self.cells) >= expected


class CIBMatrixHistory(BaseModel):
    """Tracks the CIB matrix evolution across simulation rounds."""

    matrices: list[CIBMatrix] = Field(default_factory=list)

    @property
    def latest(self) -> CIBMatrix | None:
        return self.matrices[-1] if self.matrices else None

    @property
    def num_rounds(self) -> int:
        return len(self.matrices)

    def add(self, matrix: CIBMatrix) -> None:
        self.matrices.append(matrix)

    def get_delta(self, round_a: int, round_b: int) -> np.ndarray | None:
        """Compute the difference matrix between two rounds."""
        mat_a = next((m for m in self.matrices if m.round_generated == round_a), None)
        mat_b = next((m for m in self.matrices if m.round_generated == round_b), None)
        if mat_a is None or mat_b is None:
            return None
        return mat_b.to_numpy() - mat_a.to_numpy()


def apply_delta_constraint(previous: CIBMatrix, proposed: CIBMatrix) -> CIBMatrix:
    """Enforce max ±1 change per cell per round.

    Returns a new matrix where no cell differs from the previous by more than 1.
    Cells present in previous but missing from proposed are preserved unchanged.
    """
    constrained_cells: dict[str, CIBCell] = {}

    for key, proposed_cell in proposed.cells.items():
        prev_cell = previous.cells.get(key)
        if prev_cell is None:
            constrained_cells[key] = proposed_cell
            continue

        delta = proposed_cell.influence - prev_cell.influence
        clamped_delta = max(-1, min(1, delta))
        new_influence = prev_cell.influence + clamped_delta
        new_influence = max(MIN_INFLUENCE, min(MAX_INFLUENCE, new_influence))

        constrained_cells[key] = CIBCell(
            source_descriptor=proposed_cell.source_descriptor,
            target_descriptor=proposed_cell.target_descriptor,
            influence=new_influence,
            reasoning=proposed_cell.reasoning,
        )

    # Preserve cells from previous that weren't re-evaluated
    for key, prev_cell in previous.cells.items():
        if key not in constrained_cells:
            constrained_cells[key] = prev_cell

    result = CIBMatrix(
        cells=constrained_cells,
        round_generated=proposed.round_generated,
        metadata=proposed.metadata,
    )
    result.compute_factor_scores()
    return result


# ---------------------------------------------------------------------------
# Deprecated aliases (backward compatibility with C2 code)
# ---------------------------------------------------------------------------


class CIBEntry(BaseModel):
    """Deprecated: Use CIBCell instead. Kept for backward compatibility."""

    source_factor: str
    target_factor: str
    influence_score: float
    reasoning: str = ""
