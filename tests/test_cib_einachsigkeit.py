"""Die Grundlage der Entscheidung vom 2026-08-29 — als Messung, nicht als Prosa.

Die Entscheidung «Rahmen statt Richter» (`docs/entscheidung_szenarienschicht_2026-08-29.md`)
steht auf vier Zahlen über die ausgelieferte Matrix. Steht eine davon woanders,
ist die Entscheidung neu zu treffen — und nicht stillschweigend weiterzutragen.
Deshalb misst dieser Test sie, statt sie zu behaupten:

1. Der Konsistenz-Score misst **Polarität**, nicht Plausibilität: über alle 128
   Systemzustände steigt er monoton mit der Zahl gleichpolig gesetzter Faktoren.
2. Unter dem **echten** Impact-Balance-Kriterium nach Weimer-Jehle erfüllen
   genau **zwei** der 128 Zustände die Gleichgewichtsbedingung — das
   Produktversprechen «Tripleset» ist daraus nicht bedienbar. Das beantwortet
   die Frage, die P2.2 im Projektplan offengelassen hatte.
3. Von den 84 gleichpoligen Zellen tragen nur **12** Spannung; die Matrix ist im
   Kern eine einzige Achse.
4. Vier Zellen verneinen die Rückkopplung, die gemischte Szenarien überhaupt
   erst erzeugt: Nachfrage- und Wirtschaftswachstum **hemmen** dort strenge
   Regulierung, Flugscham und Schienenausbau.

**Das Impact-Balance-Kriterium ist hier nachimplementiert, nicht importiert.**
Im Code steht es nicht — genau das ist der Befund von P2.2. Wer es in `src/`
umsetzt, ersetzt `_impact_balance_konsistent` durch den Aufruf der echten
Funktion; die erwarteten Zahlen bleiben dieselben.

**Wird ein Test hier rot, ist das kein Fehler, sondern eine Nachricht:** Jemand
hat die Matrix angefasst. Dann gehört die Entscheidung noch einmal auf den
Tisch, bevor die Zahlen hier nachgezogen werden.
"""

from __future__ import annotations

import itertools
import json
import statistics
from pathlib import Path

import pytest

from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
from src.models.cib_models import FACTOR_IDS, STATES_PER_FACTOR, CIBMatrix

REPO_ROOT = Path(__file__).resolve().parents[1]
CIB_PATH = REPO_ROOT / "configs" / "cib_frozen.json"

ZUSTAENDE = range(1, STATES_PER_FACTOR + 1)

#: Die vier Zellen aus Befund 4, je mit dem Klartext ihrer Wirkungsrichtung.
VERNEINTE_RUECKKOPPLUNG = {
    ("F1.1", "F2.2"): "Nachfrageboom hemmt strenge Regulierung",
    ("F1.1", "F6.2"): "Nachfrageboom hemmt Flugscham",
    ("F1.1", "F5.2"): "Nachfrageboom hemmt Schienenausbau",
    ("F4.1", "F2.2"): "Wirtschaftswachstum hemmt strenge Regulierung",
}


@pytest.fixture(scope="module")
def matrix() -> CIBMatrix:
    return CIBMatrix.model_validate(json.loads(CIB_PATH.read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def checker(matrix: CIBMatrix) -> ConsistencyChecker:
    return ConsistencyChecker(matrix)


def _alle_zustaende() -> list[dict[str, str]]:
    """Alle 2^7 = 128 Konstellationen als ``{"F1": "F1.1", …}``."""

    return [
        {fid: f"{fid}.{s}" for fid, s in zip(FACTOR_IDS, combo)}
        for combo in itertools.product(ZUSTAENDE, repeat=len(FACTOR_IDS))
    ]


def _reinheit(states: dict[str, str]) -> int:
    """Wie viele der sieben Faktoren stehen gleichpolig? (4 bis 7)"""

    endziffern = [s[-1] for s in states.values()]
    return max(endziffern.count("1"), endziffern.count("2"))


def _impact_balance_konsistent(matrix: CIBMatrix, states: dict[str, str]) -> bool:
    """Weimer-Jehles Gleichgewichtsbedingung, hier nachimplementiert.

    Konsistent heißt: Für **jeden** Deskriptor maximiert der gewählte Zustand
    die Summe der von den übrigen Faktoren eingehenden Einflüsse.
    """

    for fid in FACTOR_IDS:
        bilanz = {
            s: sum(
                matrix.get_influence(states[other], f"{fid}.{s}")
                for other in FACTOR_IDS
                if other != fid
            )
            for s in ZUSTAENDE
        }
        gewaehlt = int(states[fid].rsplit(".", 1)[1])
        if bilanz[gewaehlt] < max(bilanz.values()):
            return False
    return True


class TestDerScoreMisstPolaritaet:
    """Befund 1 — der Rang sagt, wie einheitlich gepolt ein Weltbild ist."""

    def test_score_steigt_monoton_mit_der_reinheit(self, checker: ConsistencyChecker) -> None:
        gruppen: dict[int, list[float]] = {}
        for states in _alle_zustaende():
            score = checker.compute_consistency_score(ScenarioDescriptor(factor_states=states))
            gruppen.setdefault(_reinheit(states), []).append(score)

        mittel = {rein: statistics.mean(werte) for rein, werte in sorted(gruppen.items())}
        assert list(mittel) == [4, 5, 6, 7], f"unerwartete Gruppen: {list(mittel)}"

        stufen = list(mittel.values())
        assert stufen == sorted(stufen), (
            "Der Score steigt nicht mehr monoton mit der Polaritäts-Reinheit — "
            f"gemessen: {mittel}. Die Entscheidung vom 2026-08-29 stand genau "
            "darauf, dass er es tut."
        )
        assert (
            stufen[-1] - stufen[0] > 0.3
        ), f"Der Abstand zwischen gemischt und rein ist geschrumpft: {mittel}"

    def test_die_gemischte_lage_wird_bestraft(self, checker: ConsistencyChecker) -> None:
        """Strenge Regulierung *bei* starker Nachfrage ist die reale europäische
        Lage — und landet unter dem heutigen Score unter dem reinen Pol."""

        gemischt = {
            "F1": "F1.1",  # Reiseboom
            "F2": "F2.2",  # radikale Dekarbonisierung
            "F3": "F3.1",
            "F4": "F4.1",
            "F5": "F5.2",
            "F6": "F6.2",
            "F7": "F7.1",
        }
        rein = {fid: f"{fid}.1" for fid in FACTOR_IDS}

        score_gemischt = checker.compute_consistency_score(
            ScenarioDescriptor(factor_states=gemischt)
        )
        score_rein = checker.compute_consistency_score(ScenarioDescriptor(factor_states=rein))

        assert (
            score_gemischt < score_rein
        ), f"gemischt {score_gemischt:.3f} soll unter rein {score_rein:.3f} liegen"


class TestImpactBalanceLiefertZweiSzenarien:
    """Befund 2 — die Antwort auf die offene Frage aus P2.2, als Zahl."""

    def test_genau_zwei_von_128_zustaenden_sind_konsistent(self, matrix: CIBMatrix) -> None:
        konsistent = [s for s in _alle_zustaende() if _impact_balance_konsistent(matrix, s)]
        assert len(konsistent) == 2, (
            f"Erwartet 2 konsistente Zustände, gemessen {len(konsistent)}: {konsistent}. "
            "Die Zahl ist die Grundlage der Entscheidung vom 2026-08-29 — bewegt sie "
            "sich, gehört die Szenarienschicht neu entschieden."
        )

    def test_das_tripleset_ist_daraus_nicht_bedienbar(self, matrix: CIBMatrix) -> None:
        """Das Produkt verspricht drei Szenarien. Das Kriterium liefert zwei."""

        konsistent = [s for s in _alle_zustaende() if _impact_balance_konsistent(matrix, s)]
        assert len(konsistent) < 3, (
            "Wenn das echte Kriterium plötzlich drei Szenarien trägt, ist der "
            "Fallstrick von P2.2 aufgelöst — dann gehört dieser Test entfernt."
        )


class TestDieMatrixIstEineAchse:
    """Befund 3 und 4 — warum nur zwei Pole übrig bleiben."""

    def test_nur_zwoelf_der_gleichpoligen_zellen_tragen_spannung(self, matrix: CIBMatrix) -> None:
        gleichpolig = [
            cell
            for cell in matrix.cells.values()
            if cell.source_descriptor[:2] != cell.target_descriptor[:2]
            and cell.source_descriptor[-1] == cell.target_descriptor[-1]
        ]
        assert len(gleichpolig) == 84
        negativ = [c for c in gleichpolig if c.influence < 0]
        assert len(negativ) == 12, (
            f"Erwartet 12 gleichpolige Zellen mit Spannung, gemessen {len(negativ)}: "
            f"{sorted(f'{c.source_descriptor}->{c.target_descriptor}' for c in negativ)}. "
            "Mehr Spannung wäre eine gute Nachricht — und der Anlass, die "
            "Einachsigkeit neu zu vermessen."
        )

    def test_die_zentrale_rueckkopplung_steht_verneint(self, matrix: CIBMatrix) -> None:
        verneint = {
            f"{src}->{tgt}": matrix.get_influence(src, tgt)
            for (src, tgt) in VERNEINTE_RUECKKOPPLUNG
        }
        assert all(wert < 0 for wert in verneint.values()), (
            f"Eine der vier Zellen ist nicht mehr negativ: {verneint}. "
            "Falls jemand sie korrigiert hat: Befund in docs/audit_findings.md "
            "entfernen und diesen Test mit ihm."
        )

    def test_keine_der_vier_zellen_traegt_eine_begruendung(self) -> None:
        """Sie stehen in der Gruppe, die `frozen: true` ohne einen Satz Herleitung trägt."""

        roh = json.loads(CIB_PATH.read_text(encoding="utf-8"))
        for (src, tgt), klartext in VERNEINTE_RUECKKOPPLUNG.items():
            zelle = roh["cells"][f"{src}|{tgt}"]
            assert not zelle.get("reasoning", "").strip(), (
                f"{src}->{tgt} ({klartext}) hat jetzt eine Begründung — "
                "dann ist P2.3 für diese Zelle erledigt und der Test nachzuziehen."
            )
