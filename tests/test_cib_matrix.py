"""Unit tests for the CIB matrix models and visualizer."""

from __future__ import annotations

import numpy as np

from src.models.cib_models import (
    MATRIX_SIZE,
    MAX_INFLUENCE,
    MIN_INFLUENCE,
    CIBCell,
    CIBEntry,
    CIBMatrix,
)

# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------


class TestCIBCell:
    def test_valid_cell(self):
        cell = CIBCell(
            source_descriptor="F1.1", target_descriptor="F2.1", influence=2, reasoning="test"
        )
        assert cell.influence == 2
        assert cell.source_descriptor == "F1.1"

    def test_influence_clamped_high(self):
        cell = CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=5)
        assert cell.influence == MAX_INFLUENCE

    def test_influence_clamped_low(self):
        cell = CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=-5)
        assert cell.influence == MIN_INFLUENCE

    def test_influence_boundaries(self):
        for val in range(MIN_INFLUENCE, MAX_INFLUENCE + 1):
            cell = CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=val)
            assert cell.influence == val


class TestCIBMatrix:
    def test_empty_matrix(self):
        m = CIBMatrix.empty(round_generated=0)
        assert m.round_generated == 0
        # 14*14 - 7*(2*2) = 196 - 28 = 168 cross-factor cells
        assert len(m.cells) == 168
        assert m.is_complete

    def test_set_and_get_cell(self):
        m = CIBMatrix.empty(round_generated=1)
        cell = CIBCell(
            source_descriptor="F1.1", target_descriptor="F3.2", influence=-2, reasoning="test"
        )
        m.set_cell(cell)
        retrieved = m.get_cell("F1.1", "F3.2")
        assert retrieved is not None
        assert retrieved.influence == -2

    def test_get_influence(self):
        m = CIBMatrix.empty(round_generated=0)
        assert m.get_influence("F1.1", "F2.1") == 0
        assert m.get_influence("F1.1", "INVALID") == 0

    def test_cell_key_format(self):
        key = CIBMatrix.cell_key("F1.1", "F2.2")
        assert key == "F1.1|F2.2"

    def test_to_numpy_shape(self):
        m = CIBMatrix.empty(round_generated=0)
        arr = m.to_numpy()
        assert arr.shape == (MATRIX_SIZE, MATRIX_SIZE)
        assert arr.dtype == int

    def test_from_numpy_roundtrip(self):
        rng = np.random.default_rng(123)
        data = rng.integers(-3, 4, size=(MATRIX_SIZE, MATRIX_SIZE))
        # Zero same-factor blocks
        for i in range(7):
            data[i * 2 : i * 2 + 2, i * 2 : i * 2 + 2] = 0

        m = CIBMatrix.from_numpy(data, round_generated=5)
        arr = m.to_numpy()
        np.testing.assert_array_equal(data, arr)
        assert m.round_generated == 5

    def test_compute_factor_scores(self):
        m = CIBMatrix.empty(round_generated=0)
        # Set some cells for F1
        m.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=3))
        m.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F3.1", influence=-2))
        m.set_cell(CIBCell(source_descriptor="F2.1", target_descriptor="F1.1", influence=1))

        scores = m.compute_factor_scores()
        f1 = next(s for s in scores if s.factor_id == "F1")
        assert f1.active_score == 5  # |3| + |-2|
        assert f1.passive_score == 1  # |1|

    def test_is_complete(self):
        m = CIBMatrix(cells={}, round_generated=0)
        assert not m.is_complete

        m2 = CIBMatrix.empty(round_generated=0)
        assert m2.is_complete

    def test_serialization_roundtrip(self):
        m = CIBMatrix.empty(round_generated=2)
        m.set_cell(
            CIBCell(
                source_descriptor="F1.1", target_descriptor="F2.1", influence=2, reasoning="test"
            )
        )
        m.compute_factor_scores()

        data = m.model_dump()
        restored = CIBMatrix(**data)
        assert restored.round_generated == 2
        cell = restored.get_cell("F1.1", "F2.1")
        assert cell is not None
        assert cell.influence == 2

    def test_json_roundtrip(self):
        m = CIBMatrix.empty(round_generated=1)
        m.set_cell(
            CIBCell(
                source_descriptor="F3.1",
                target_descriptor="F5.2",
                influence=-3,
                reasoning="hemmend",
            )
        )

        json_str = m.model_dump_json()
        restored = CIBMatrix.model_validate_json(json_str)
        cell = restored.get_cell("F3.1", "F5.2")
        assert cell is not None
        assert cell.influence == -3


# ---------------------------------------------------------------------------
# Visualizer Smoke Tests
# ---------------------------------------------------------------------------


class TestCIBVisualizer:
    def test_heatmap_creates_file(self, tmp_path):
        from src.reporting.cib_visualizer import render_heatmap

        m = CIBMatrix.empty(round_generated=0)
        m.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=2))
        out = tmp_path / "heatmap.png"
        render_heatmap(m, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_network_creates_file(self, tmp_path):
        from src.reporting.cib_visualizer import render_network

        rng = np.random.default_rng(42)
        data = rng.integers(-2, 3, size=(MATRIX_SIZE, MATRIX_SIZE))
        for i in range(7):
            data[i * 2 : i * 2 + 2, i * 2 : i * 2 + 2] = 0
        m = CIBMatrix.from_numpy(data, round_generated=1)

        out = tmp_path / "network.png"
        render_network(m, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_bar_chart_creates_file(self, tmp_path):
        from src.reporting.cib_visualizer import render_active_passive_bar

        m = CIBMatrix.empty(round_generated=0)
        m.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=3))
        m.set_cell(CIBCell(source_descriptor="F3.1", target_descriptor="F1.2", influence=-2))
        m.compute_factor_scores()

        out = tmp_path / "scores.png"
        render_active_passive_bar(m, out)
        assert out.exists()
        assert out.stat().st_size > 0


# ---------------------------------------------------------------------------
# Backward Compatibility Tests
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    def test_cib_entry_still_works(self):
        entry = CIBEntry(
            source_factor="F1", target_factor="F2", influence_score=0.75, reasoning="test"
        )
        assert entry.influence_score == 0.75

    def test_old_style_matrix_construction(self):
        entries = [
            CIBEntry(source_factor="F1", target_factor="F2", influence_score=1.0, reasoning="test"),
        ]
        m = CIBMatrix(entries=entries, round_generated=1, metadata={"test": True})
        assert len(m.entries) == 1
        assert m.round_generated == 1
