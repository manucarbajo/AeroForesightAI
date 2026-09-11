"""Tests für EnvironmentNode (M3 Population Pipeline) und PopulationShift-Modelle.

Hinweis: EnvironmentAgentNode (LLM-gestützte Segment-Verschiebung) wurde mit M3.5
         entfernt. Population-Shifts erfolgen nun ausschließlich deterministisch über
         apply_factor_shifts() in population_sampler.py (shift_rules aus properties.json).
"""

from __future__ import annotations

from src.models.population_models import (
    PopulationShift,
    PopulationUpdateResult,
)


class TestPopulationShift:
    """Tests für PopulationShift Model."""

    def test_create_shift(self):
        """Erstelle einen Shift."""
        shift = PopulationShift(
            segment_id="test",
            segment_name="Test Segment",
            old_share=0.3,
            new_share=0.35,
            shift_amount=0.05,
            reasoning="Test reason",
        )

        assert shift.segment_id == "test"
        assert shift.shift_amount == 0.05
        assert shift.clamped is False

    def test_shift_defaults(self):
        """Clamped-Flag ist standardmäßig False."""
        shift = PopulationShift(
            segment_id="eco",
            segment_name="Eco Segment",
            old_share=0.2,
            new_share=0.22,
            shift_amount=0.02,
            reasoning="Slight increase",
        )
        assert shift.clamped is False

    def test_shift_negative(self):
        """Negative Shifts sind erlaubt."""
        shift = PopulationShift(
            segment_id="business",
            segment_name="Business",
            old_share=0.3,
            new_share=0.25,
            shift_amount=-0.05,
            reasoning="Decline",
        )
        assert shift.shift_amount < 0


class TestPopulationUpdateResult:
    """Tests für PopulationUpdateResult Model."""

    def test_empty_result(self):
        """Erstelle leeres Result."""
        result = PopulationUpdateResult(round_number=1)
        assert result.round_number == 1
        assert len(result.shifts) == 0

    def test_result_with_shifts(self):
        """Erstelle Result mit Shifts."""
        shift = PopulationShift(
            segment_id="test",
            segment_name="Test",
            old_share=0.3,
            new_share=0.35,
            shift_amount=0.05,
            reasoning="Test",
        )

        result = PopulationUpdateResult(
            round_number=2,
            shifts=[shift],
        )

        assert len(result.shifts) == 1
        assert result.shifts[0].segment_id == "test"

    def test_result_reasoning(self):
        """Total-Reasoning wird korrekt gespeichert."""
        result = PopulationUpdateResult(
            round_number=3,
            total_reasoning="High carbon tax drove eco-awareness up.",
        )
        assert "carbon" in result.total_reasoning
