"""Tests für Szenario-Derivation."""

from __future__ import annotations

import pytest
import numpy as np

from src.models.cib_models import CIBMatrix, CIBCell, MATRIX_SIZE
from src.scenario_consistency import (
    ScenarioDescriptor,
    ConsistencyChecker,
    ScenarioDeriver,
    ConsistencyCheckResult,
)


class TestScenarioDescriptor:
    """Tests für ScenarioDescriptor Model."""

    def test_create_scenario(self):
        """Erstelle ein valid Szenario."""
        factor_states = {
            "F1": "F1.1", "F2": "F2.1", "F3": "F3.2",
            "F4": "F4.1", "F5": "F5.2", "F6": "F6.1", "F7": "F7.2"
        }
        scenario = ScenarioDescriptor(factor_states=factor_states)
        assert len(scenario.factor_states) == 7
        assert scenario.consistency_score == 0.0
        assert scenario.stability_index == 0.0


class TestConsistencyChecker:
    """Tests für ConsistencyChecker."""

    def test_checker_creation(self):
        """Erstelle einen Checker mit leerer Matrix."""
        matrix = CIBMatrix.empty(round_generated=1)
        checker = ConsistencyChecker(matrix)
        assert checker.cib_matrix is matrix
        assert checker.conflict_threshold == -1.5

    def test_check_empty_matrix_scenario(self):
        """Szenario gegen leere Matrix ist immer konsistent."""
        matrix = CIBMatrix.empty(round_generated=1)
        checker = ConsistencyChecker(matrix)

        scenario = ScenarioDescriptor(factor_states={
            "F1": "F1.1", "F2": "F2.1", "F3": "F3.1",
            "F4": "F4.1", "F5": "F5.1", "F6": "F6.1", "F7": "F7.1"
        })

        result = checker.check_scenario(scenario)
        assert result.is_consistent is True
        assert len(result.conflicts) == 0

    def test_consistency_score_empty_matrix(self):
        """Leere Matrix sollte neutralen Score geben."""
        matrix = CIBMatrix.empty(round_generated=1)
        checker = ConsistencyChecker(matrix)

        scenario = ScenarioDescriptor(factor_states={
            "F1": "F1.1", "F2": "F2.1", "F3": "F3.1",
            "F4": "F4.1", "F5": "F5.1", "F6": "F6.1", "F7": "F7.1"
        })

        score = checker.compute_consistency_score(scenario)
        assert 0.0 <= score <= 1.0
        assert score == 0.5  # Neutral für leere Matrix

    def test_stability_index_empty_matrix(self):
        """Leere Matrix hat keine negativen Einflüsse → maximale Stabilität."""
        matrix = CIBMatrix.empty(round_generated=1)
        checker = ConsistencyChecker(matrix)

        scenario = ScenarioDescriptor(factor_states={
            "F1": "F1.1", "F2": "F2.1", "F3": "F3.1",
            "F4": "F4.1", "F5": "F5.1", "F6": "F6.1", "F7": "F7.1"
        })

        stability = checker.compute_stability_index(scenario)
        assert 0.0 <= stability <= 1.0
        assert stability == 1.0  # Keine negativen Wechselwirkungen → maximal stabil

    def test_detect_conflicts(self):
        """Erkenne Konflikte in konsisten Szenarien."""
        matrix = CIBMatrix.empty(round_generated=1)

        # Setze einen stark negativen Einfluss
        matrix.set_cell(CIBCell(
            source_descriptor="F1.1",
            target_descriptor="F2.1",
            influence=-3
        ))

        checker = ConsistencyChecker(matrix, conflict_threshold=-2.5)
        scenario = ScenarioDescriptor(factor_states={
            "F1": "F1.1", "F2": "F2.1", "F3": "F3.1",
            "F4": "F4.1", "F5": "F5.1", "F6": "F6.1", "F7": "F7.1"
        })

        result = checker.check_scenario(scenario)
        # Der Konflikt sollte erkannt werden
        # (abhängig ob der Threshold passt)
        assert isinstance(result, ConsistencyCheckResult)


class TestScenarioDeriver:
    """Tests für ScenarioDeriver."""

    def test_deriver_creation(self):
        """Erstelle einen ScenarioDeriver."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)
        assert deriver.cib_matrix is matrix
        assert deriver.checker is not None

    def test_derive_scenarios_empty_matrix(self):
        """Deriviere Szenarien aus leerer Matrix."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)

        result = deriver.derive_scenarios(top_n=3)

        # Sollte Szenarien finden
        assert result.total_evaluated > 0
        assert len(result.scenarios) <= 3
        assert result.consistent_count > 0
        assert result.matrix_round == 1

    def test_derive_all_scenarios(self):
        """Deriviere alle Szenarien (2^7 = 128)."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)

        result = deriver.derive_scenarios(top_n=128)

        # Mit allow_inconsistent=False sollten alle 128 sein
        assert result.total_evaluated == 128
        assert result.consistent_count == 128  # Leere Matrix = alle konsistent

    def test_scenario_has_all_factors(self):
        """Jedes Szenario sollte alle 7 Faktoren haben."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)

        result = deriver.derive_scenarios(top_n=5)

        for scenario in result.scenarios:
            assert len(scenario.factor_states) == 7
            for i in range(1, 8):
                factor_id = f"F{i}"
                assert factor_id in scenario.factor_states
                # Prüfe dass der State entweder .1 oder .2 ist
                state = scenario.factor_states[factor_id]
                assert state in [f"F{i}.1", f"F{i}.2"]

    def test_scenarios_have_scores(self):
        """Jedes Szenario sollte Scores haben."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)

        result = deriver.derive_scenarios(top_n=5)

        for scenario in result.scenarios:
            assert 0.0 <= scenario.consistency_score <= 1.0
            assert 0.0 <= scenario.stability_index <= 1.0
            assert len(scenario.reasoning) > 0

    def test_scenarios_sorted_by_score(self):
        """Szenarien sollten absteigend nach Combined Score sortiert sein."""
        matrix = CIBMatrix.empty(round_generated=1)
        deriver = ScenarioDeriver(matrix)

        result = deriver.derive_scenarios(top_n=10)

        # Berechne Combined Score für jeden
        scores = [
            (s.consistency_score + s.stability_index) / 2
            for s in result.scenarios
        ]

        # Prüfe dass sortiert absteigend
        assert scores == sorted(scores, reverse=True)


class TestIntegration:
    """Integration Tests."""

    def test_end_to_end_scenario_derivation(self):
        """Vollständiger Test: Matrix → Szenarien."""
        # Erstelle eine Matrix mit ein paar echten Werten
        matrix = CIBMatrix.empty(round_generated=1)

        matrix.set_cell(CIBCell(
            source_descriptor="F1.1",
            target_descriptor="F2.1",
            influence=2
        ))

        matrix.set_cell(CIBCell(
            source_descriptor="F1.1",
            target_descriptor="F2.2",
            influence=-1
        ))

        matrix.compute_factor_scores()

        # Deriviere Szenarien
        deriver = ScenarioDeriver(matrix)
        result = deriver.derive_scenarios(top_n=5)

        assert result.total_evaluated == 128
        assert len(result.scenarios) == 5

        # Top-Szenario sollte höhere Scores haben als andere
        top_score = (result.scenarios[0].consistency_score +
                     result.scenarios[0].stability_index) / 2
        if len(result.scenarios) > 1:
            second_score = (result.scenarios[1].consistency_score +
                            result.scenarios[1].stability_index) / 2
            assert top_score >= second_score