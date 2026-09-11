"""Unit tests for the CIB matrix models, extractor, and visualizer."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import numpy as np

from src.config_loader import build_initial_state
from src.legacy.cib_extractor_node import CIBExtractorNode, _parse_cib_response
from src.models.cib_models import (
    MATRIX_SIZE,
    MAX_INFLUENCE,
    MIN_INFLUENCE,
    CIBCell,
    CIBEntry,
    CIBMatrix,
    CIBMatrixHistory,
    apply_delta_constraint,
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


class TestCIBMatrixHistory:
    def test_empty_history(self):
        h = CIBMatrixHistory()
        assert h.latest is None
        assert h.num_rounds == 0

    def test_add_and_latest(self):
        h = CIBMatrixHistory()
        m1 = CIBMatrix.empty(round_generated=1)
        m2 = CIBMatrix.empty(round_generated=2)
        h.add(m1)
        h.add(m2)
        assert h.num_rounds == 2
        assert h.latest.round_generated == 2

    def test_get_delta(self):
        h = CIBMatrixHistory()
        m1 = CIBMatrix.empty(round_generated=1)
        m1.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=1))

        m2 = CIBMatrix.empty(round_generated=2)
        m2.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=2))

        h.add(m1)
        h.add(m2)

        delta = h.get_delta(1, 2)
        assert delta is not None
        # F1.1 is index 0, F2.1 is index 2 (F1.1=0, F1.2=1, F2.1=2)
        assert delta[0, 2] == 1  # 2 - 1

    def test_get_delta_missing_round(self):
        h = CIBMatrixHistory()
        h.add(CIBMatrix.empty(round_generated=1))
        assert h.get_delta(1, 99) is None


# ---------------------------------------------------------------------------
# Delta Constraint Tests
# ---------------------------------------------------------------------------


class TestDeltaConstraint:
    def test_no_change(self):
        prev = CIBMatrix.empty(round_generated=1)
        proposed = CIBMatrix.empty(round_generated=2)
        result = apply_delta_constraint(prev, proposed)
        arr = result.to_numpy()
        np.testing.assert_array_equal(arr, np.zeros((MATRIX_SIZE, MATRIX_SIZE)))

    def test_clamps_positive_delta(self):
        prev = CIBMatrix.empty(round_generated=1)
        proposed = CIBMatrix.empty(round_generated=2)
        proposed.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=3))
        result = apply_delta_constraint(prev, proposed)
        assert result.get_influence("F1.1", "F2.1") == 1

    def test_clamps_negative_delta(self):
        prev = CIBMatrix.empty(round_generated=1)
        proposed = CIBMatrix.empty(round_generated=2)
        proposed.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=-3))
        result = apply_delta_constraint(prev, proposed)
        assert result.get_influence("F1.1", "F2.1") == -1

    def test_allows_delta_of_one(self):
        prev = CIBMatrix.empty(round_generated=1)
        prev.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=1))
        proposed = CIBMatrix.empty(round_generated=2)
        proposed.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=2))
        result = apply_delta_constraint(prev, proposed)
        assert result.get_influence("F1.1", "F2.1") == 2

    def test_respects_max_boundary(self):
        prev = CIBMatrix.empty(round_generated=1)
        prev.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=3))
        proposed = CIBMatrix.empty(round_generated=2)
        proposed.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=3))
        result = apply_delta_constraint(prev, proposed)
        assert result.get_influence("F1.1", "F2.1") == 3

    def test_factor_scores_computed(self):
        prev = CIBMatrix.empty(round_generated=1)
        proposed = CIBMatrix.empty(round_generated=2)
        proposed.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=2))
        result = apply_delta_constraint(prev, proposed)
        assert len(result.factor_scores) == 7

    def test_preserves_cells_missing_from_proposed(self):
        """Cells in previous but not in proposed must be preserved (LLM partial response)."""
        prev = CIBMatrix.empty(round_generated=1)
        prev.set_cell(CIBCell(source_descriptor="F1.1", target_descriptor="F2.1", influence=2))
        prev.set_cell(CIBCell(source_descriptor="F3.1", target_descriptor="F4.1", influence=-1))

        # Proposed only has one cell — F3.1|F4.1 is "missing" (LLM didn't return it)
        proposed = CIBMatrix(
            cells={
                CIBMatrix.cell_key("F1.1", "F2.1"): CIBCell(
                    source_descriptor="F1.1", target_descriptor="F2.1", influence=3
                ),
            },
            round_generated=2,
        )

        result = apply_delta_constraint(prev, proposed)
        # F1.1→F2.1: delta 2→3 = +1, allowed
        assert result.get_influence("F1.1", "F2.1") == 3
        # F3.1→F4.1: preserved from previous
        assert result.get_influence("F3.1", "F4.1") == -1


# ---------------------------------------------------------------------------
# CIB Extractor Tests
# ---------------------------------------------------------------------------


class TestCIBExtractorHeuristic:
    """Test the heuristic fallback (no LLM)."""

    def test_invoke_without_llm(self):
        state = build_initial_state(load_cib=False)
        state.clock.current_tick = 1
        extractor = CIBExtractorNode(llm=None)
        result = extractor.invoke(state)
        # No events = empty CIB
        assert result.cib_matrix is not None
        assert result.cib_matrix.round_generated == 1


class TestCIBExtractorLLM:
    """Test the LLM-based extractor with a mock."""

    def _make_mock_llm(self, response: str) -> MagicMock:
        mock = MagicMock()
        mock.call.return_value = response
        return mock

    def test_successful_extraction(self):
        mock_response = json.dumps(
            [
                {
                    "source": "F1.1",
                    "target": "F2.1",
                    "influence": 2,
                    "reasoning": "Boom fördert Regulierung",
                },
                {
                    "source": "F1.1",
                    "target": "F3.2",
                    "influence": 1,
                    "reasoning": "Nachfrage treibt Innovation",
                },
            ]
        )
        llm = self._make_mock_llm(mock_response)

        state = build_initial_state(load_cib=False)
        state.clock.current_tick = 1
        extractor = CIBExtractorNode(llm=llm)
        result = extractor.invoke(state)

        assert result.cib_matrix is not None
        cell = result.cib_matrix.get_cell("F1.1", "F2.1")
        assert cell is not None
        assert cell.influence == 2

    def test_fallback_on_invalid_response(self):
        llm = self._make_mock_llm("This is not valid JSON at all")

        state = build_initial_state(load_cib=False)
        state.clock.current_tick = 1
        extractor = CIBExtractorNode(llm=llm)
        result = extractor.invoke(state)

        # Should still return a matrix (empty)
        assert result.cib_matrix is not None

    def test_delta_constraint_applied_on_second_round(self):
        # First round: big values
        round1_response = json.dumps(
            [
                {"source": "F1.1", "target": "F2.1", "influence": 3, "reasoning": "strong"},
            ]
        )
        # Second round: same big values
        round2_response = json.dumps(
            [
                {"source": "F1.1", "target": "F2.1", "influence": -3, "reasoning": "reversed"},
            ]
        )

        call_count = [0]
        mock = MagicMock()

        def side_effect(prompt):
            call_count[0] += 1
            if call_count[0] <= 4:  # first round has 4 batches
                return round1_response
            return round2_response

        mock.call.side_effect = side_effect

        state = build_initial_state(load_cib=False)
        state.clock.current_tick = 1
        extractor = CIBExtractorNode(llm=mock)

        # Round 1
        state = extractor.invoke(state)
        r1_value = state.cib_matrix.get_influence("F1.1", "F2.1")
        assert r1_value == 3  # no constraint on round 1

        # Round 2
        state.clock.current_tick = 2
        state = extractor.invoke(state)
        r2_value = state.cib_matrix.get_influence("F1.1", "F2.1")
        # delta from 3 to -3 = -6, clamped to -1, so 3 + (-1) = 2
        assert r2_value == 2


class TestParseResponse:
    def test_valid_json_array(self):
        raw = '[{"source": "F1.1", "target": "F2.1", "influence": 1, "reasoning": "ok"}]'
        result = _parse_cib_response(raw)
        assert len(result) == 1
        assert result[0]["influence"] == 1

    def test_json_in_code_block(self):
        raw = '```json\n[{"source": "F1.1", "target": "F2.1", "influence": 2}]\n```'
        result = _parse_cib_response(raw)
        assert len(result) == 1

    def test_json_with_preamble(self):
        raw = 'Here is the evaluation:\n[{"source": "F1.1", "target": "F2.1", "influence": -1}]\nDone.'
        result = _parse_cib_response(raw)
        assert len(result) == 1

    def test_invalid_json(self):
        result = _parse_cib_response("Not JSON at all")
        assert result == []


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
