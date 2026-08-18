"""P4.5 — CIB-Konsistenz-Ranking der drei Sweep-Archetypen.

Empirische Scores aus der korrigierten cib_frozen.json (v2, domänenkorrekter Werte):

  - BAU      (F1.1,F2.1,F3.1,F4.1,F5.1,F6.1,F7.1): consistency=0.973, conflicts=0
  - Konflikt (F1.2,F2.2,F3.1,F4.2,F5.2,F6.2,F7.2): consistency=0.867, conflicts=2
  - Wende    (F1.2,F2.2,F3.2,F4.1,F5.2,F6.2,F7.1): consistency=0.603, conflicts=8

P4.3-Kernnachweis: BAU > Konflikt (Consistency-Score). ✓

Interpretation:
  BAU ist das am stärksten selbstverstärkende Szenario (0 Konflikte) — alle Faktoren
  unterstützen sich gegenseitig (F6.1↔F1.1, F4.1↔F2.1 etc.). Entspricht der Folien-
  aussage: "hochstabiles Szenario".

  Transformationskonflikt hat trotz des Namens nur 2 Kern-Konflikte (F2.2+F3.1:
  strenge Regulierung ohne Technologiedurchbruch; F4.2+F2.2: Rezession untergräbt
  Regulierung). Die anderen 5 Faktorkombinationen verstärken sich gegenseitig
  (F1.2↔F2.2, F6.2↔F5.2 etc.).

  Freiwillige Wende hat den niedrigsten Score, weil das Szenario selbst-untergrabendes
  Verhalten zeigt: F3.2 (SAF-Durchbruch) untergräbt F2.2 (−2) und F6.2 (−3); die
  Kombination stabiler Wirtschaft (F4.1) + offener Märkte (F7.1) mit strenger
  Regulierung (F2.2) erzeugt weitere Spannungen.

Methodische Grundlagen:
  Weimer-Jehle, W. (2023). Einfuehrung in die Cross-Impact-Bilanzanalyse (CIB).
  Gausemeier, J. et al. (1998). Szenario-Management.
  Vgl. scenario_consistency.py (F-CIB1, F-CIB2, F-CIB3).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
from src.models.cib_models import CIBMatrix

REPO_ROOT = Path(__file__).resolve().parents[1]
CIB_PATH = REPO_ROOT / "configs" / "cib_frozen.json"

# ---------------------------------------------------------------------------
# Faktor-Endzustaende der drei Sweep-Archetypen
# ---------------------------------------------------------------------------

BAU_END_STATES = {
    "F1": "F1.1",
    "F2": "F2.1",
    "F3": "F3.1",
    "F4": "F4.1",
    "F5": "F5.1",
    "F6": "F6.1",
    "F7": "F7.1",
}

WENDE_END_STATES = {
    "F1": "F1.2",
    "F2": "F2.2",
    "F3": "F3.2",
    "F4": "F4.1",
    "F5": "F5.2",
    "F6": "F6.2",
    "F7": "F7.1",
}

KONFLIKT_END_STATES = {
    "F1": "F1.2",
    "F2": "F2.2",
    "F3": "F3.1",
    "F4": "F4.2",
    "F5": "F5.2",
    "F6": "F6.2",
    "F7": "F7.2",
}

# Empirische Referenzwerte nach Matrix-Korrektur (v2)
EXPECTED = {
    "BAU": {"consistency": 0.973, "stability": 1.000, "conflicts": 0},
    "Wende": {"consistency": 0.603, "stability": 0.810, "conflicts": 8},
    "Konflikt": {"consistency": 0.867, "stability": 0.952, "conflicts": 2},
}
TOLERANCE = 0.02


@pytest.fixture(scope="module")
def checker() -> ConsistencyChecker:
    raw = json.loads(CIB_PATH.read_text(encoding="utf-8"))
    matrix = CIBMatrix.model_validate(raw)
    return ConsistencyChecker(matrix)


class TestCIBRankingBAUvsKonflikt:
    """P4.3 / P4.5 — Kernnachweis: BAU konsistenter als Transformationskonflikt."""

    def test_bau_score_higher_than_konflikt(self, checker: ConsistencyChecker) -> None:
        """BAU (A1+B1) muss hoeheren CIB-Konsistenz-Score haben als der Transformationskonflikt.
        Empirisch: BAU=0.973, Konflikt=0.867."""
        bau = checker.compute_consistency_score(ScenarioDescriptor(factor_states=BAU_END_STATES))
        konflikt = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)
        )
        assert bau > konflikt, (
            f"BAU ({bau:.3f}) soll > Konflikt ({konflikt:.3f}) sein. "
            "BAU ist laut Vorlesungsfolien 'hochstabiles Szenario'."
        )

    def test_bau_consistency_score_value(self, checker: ConsistencyChecker) -> None:
        """BAU liegt nahe am Referenzwert 0.973 (Toleranz +/-0.02)."""
        score = checker.compute_consistency_score(ScenarioDescriptor(factor_states=BAU_END_STATES))
        expected = EXPECTED["BAU"]["consistency"]
        assert (
            abs(score - expected) <= TOLERANCE
        ), f"BAU consistency {score:.4f} weicht zu stark von {expected} ab."

    def test_konflikt_consistency_score_value(self, checker: ConsistencyChecker) -> None:
        """Transformationskonflikt liegt nahe am Referenzwert 0.867."""
        score = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)
        )
        expected = EXPECTED["Konflikt"]["consistency"]
        assert (
            abs(score - expected) <= TOLERANCE
        ), f"Konflikt consistency {score:.4f} weicht zu stark von {expected} ab."

    def test_bau_has_zero_conflicts(self, checker: ConsistencyChecker) -> None:
        """BAU soll 0 CIB-Konflikte haben — alle Faktoren unterstuetzen sich gegenseitig.
        Dies bestaetigt die Folie: 'hochstabiles Szenario'."""
        result = checker.check_scenario(ScenarioDescriptor(factor_states=BAU_END_STATES))
        assert (
            result.is_consistent
        ), f"BAU soll keine CIB-Konflikte haben, gefunden: {result.conflicts}"
        assert len(result.conflicts) == 0

    def test_konflikt_has_exactly_core_conflicts(self, checker: ConsistencyChecker) -> None:
        """Transformationskonflikt hat genau die erwarteten Kern-Konflikte:
        F2.2+F3.1 (strenge Regulierung ohne SAF-Durchbruch) und
        F4.2+F2.2 (Rezession untergraebt strenge Regulierung)."""
        result = checker.check_scenario(ScenarioDescriptor(factor_states=KONFLIKT_END_STATES))
        assert not result.is_consistent
        assert len(result.conflicts) == EXPECTED["Konflikt"]["conflicts"], (
            f"Konflikt sollte {EXPECTED['Konflikt']['conflicts']} Konflikte haben, "
            f"gefunden: {len(result.conflicts)}: {result.conflicts}"
        )


class TestCIBRankingAllThreeArchetypes:
    """Vollstaendiges empirisches Ranking aller drei Sweep-Archetypen."""

    def test_all_scores_in_valid_range(self, checker: ConsistencyChecker) -> None:
        for name, states in [
            ("BAU", BAU_END_STATES),
            ("Wende", WENDE_END_STATES),
            ("Konflikt", KONFLIKT_END_STATES),
        ]:
            score = checker.compute_consistency_score(ScenarioDescriptor(factor_states=states))
            assert 0.0 <= score <= 1.0, f"{name} score {score:.3f} ausserhalb [0,1]"

    def test_bau_highest_consistency(self, checker: ConsistencyChecker) -> None:
        """BAU hat den hoechsten Consistency-Score aller drei Archetypen."""
        bau = checker.compute_consistency_score(ScenarioDescriptor(factor_states=BAU_END_STATES))
        wende = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=WENDE_END_STATES)
        )
        konflikt = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)
        )
        assert bau > wende and bau > konflikt, (
            f"BAU ({bau:.3f}) soll groesser sein als Wende ({wende:.3f}) "
            f"und Konflikt ({konflikt:.3f})."
        )

    def test_wende_lowest_consistency(self, checker: ConsistencyChecker) -> None:
        """Freiwillige Wende hat den niedrigsten Consistency-Score (0.603).
        Begruendung: SAF-Durchbruch (F3.2) untergraebt F2.2 (-2) und F6.2 (-3);
        F4.1 und F7.1 sind in Spannung mit F2.2 (-2 je)."""
        wende = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=WENDE_END_STATES)
        )
        bau = checker.compute_consistency_score(ScenarioDescriptor(factor_states=BAU_END_STATES))
        konflikt = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)
        )
        assert wende < bau and wende < konflikt, (
            f"Wende ({wende:.3f}) soll niedrigsten Score haben "
            f"(BAU={bau:.3f}, Konflikt={konflikt:.3f})."
        )

    def test_wende_score_value(self, checker: ConsistencyChecker) -> None:
        """Freiwillige Wende liegt nahe am Referenzwert 0.603."""
        score = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=WENDE_END_STATES)
        )
        expected = EXPECTED["Wende"]["consistency"]
        assert (
            abs(score - expected) <= TOLERANCE
        ), f"Wende score {score:.4f} weicht zu stark von {expected} ab."

    def test_conflict_count_ranking(self, checker: ConsistencyChecker) -> None:
        """Konflikt-Anzahl folgt Ranking: BAU(0) < Konflikt(2) < Wende(8).
        BAU hat null Konflikte (perfekt konsistentes Szenario).
        Wende hat die meisten Konflikte durch selbst-untergrabendes Verhalten."""
        bau_n = len(
            checker.check_scenario(ScenarioDescriptor(factor_states=BAU_END_STATES)).conflicts
        )
        wende_n = len(
            checker.check_scenario(ScenarioDescriptor(factor_states=WENDE_END_STATES)).conflicts
        )
        konflikt_n = len(
            checker.check_scenario(ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)).conflicts
        )
        assert (
            bau_n < konflikt_n < wende_n
        ), f"Erwartetes Ranking: BAU({bau_n}) < Konflikt({konflikt_n}) < Wende({wende_n})."

    def test_stability_index_ranking(self, checker: ConsistencyChecker) -> None:
        """Stability-Index folgt demselben Ranking: BAU(1.0) > Konflikt(0.952) > Wende(0.810)."""
        bau = checker.compute_stability_index(ScenarioDescriptor(factor_states=BAU_END_STATES))
        wende = checker.compute_stability_index(ScenarioDescriptor(factor_states=WENDE_END_STATES))
        konflikt = checker.compute_stability_index(
            ScenarioDescriptor(factor_states=KONFLIKT_END_STATES)
        )
        assert (
            bau > konflikt > wende
        ), f"Stability-Index Ranking: BAU({bau:.3f}) > Konflikt({konflikt:.3f}) > Wende({wende:.3f})."

    def test_bau_perfect_stability(self, checker: ConsistencyChecker) -> None:
        """BAU hat Stability-Index = 1.0 (kein einziger starker Negativkante im Szenario)."""
        si = checker.compute_stability_index(ScenarioDescriptor(factor_states=BAU_END_STATES))
        assert si == 1.0, f"BAU Stability-Index {si:.4f} sollte 1.0 (perfekt) sein."
