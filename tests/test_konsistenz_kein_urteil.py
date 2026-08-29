"""P2.0 — der CIB-Score verlässt den Lauf nicht mehr als Werturteil.

Bis zum 2026-08-29 übersetzte `_plausibility_from_score` den Score in
«hoch / mittel / niedrig» und schrieb das Ergebnis als `plausibility` in
`run_scenario.json` — **und in den Prompt des Sprachmodells**, das daraufhin
Narrative über die «plausibelste» Zukunft schrieb.

Gemessen misst der Score aber Polarität (`test_cib_einachsigkeit.py`). Das
Etikett «hoch» lag damit auf dem vollständig gleichpoligen Zustand — der Welt,
in der sich nichts widerspricht, weil sich nichts bewegt —, und «niedrig» auf
der realen europäischen Mischlage aus starker Nachfrage und strenger
Regulierung. In einem echten Artefakt (`run_20260827T181422Z`) las sich das so:
Rang 1, alle sieben Faktoren auf `.1`, `plausibility: hoch`.

Diese Tests halten drei Zusagen fest:

1. Kein Codepfad in `src/` schreibt oder liest noch ein `plausibility`-Feld.
2. Das Band benennt die **gemessene** Größe, und ohne Score gibt es kein Band —
   der frühere Rückfall auf den Präsentationsrang machte aus einer Reihenfolge
   eine Aussage über die Welt.
3. Die Bedeutung reist **mit dem Artefakt und mit dem Prompt**. Der State
   Explorer und das Sprachmodell lesen die Zahl ohne die Doku daneben.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src.reporting.run_scenario_generator.candidates import (
    KONSISTENZ_BEDEUTUNG,
    _konsistenz_band,
    _score_constellations,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
PROMPT_TEMPLATE = SRC / "prompts" / "run_scenario.md"


class TestDasWortIstWeg:
    """Zusage 1 — `plausibility` kommt in der Engine nicht mehr vor."""

    def test_kein_modul_unter_src_nennt_das_feld(self) -> None:
        # Geprüft wird der **Code**, nicht der Text: Docstrings und Kommentare
        # dürfen das alte Wort nennen — sie erklären ja gerade, warum es weg
        # ist. Ein AST-Durchlauf trennt beides, ein Grep könnte es nicht.
        echte: list[str] = []
        for pfad in SRC.rglob("*.py"):
            if "legacy" in pfad.parts:
                continue
            echte += [
                f"{pfad.relative_to(REPO_ROOT)}:{zeile}: {was}"
                for zeile, was in _plausibility_im_code(pfad.read_text(encoding="utf-8"))
            ]

        assert not echte, (
            "Das Feld `plausibility` ist zurück in der Engine:\n  "
            + "\n  ".join(echte)
            + "\nDer CIB-Score misst Polarität, nicht Plausibilität — siehe "
            "test_cib_einachsigkeit.py und docs/entscheidung_szenarienschicht_2026-08-29.md."
        )

    def test_der_prompt_verbietet_die_wahrscheinlichkeitsaussage(self) -> None:
        """Das Modell bekam die Anweisung, aus dem Score eine Chance abzuleiten."""

        text = PROMPT_TEMPLATE.read_text(encoding="utf-8")
        assert "keine Wahrscheinlichkeit" in text, (
            "Die Prompt-Vorlage sagt dem Modell nicht mehr, dass der Score keine "
            "Wahrscheinlichkeit ist. Ohne diesen Satz schreibt es wieder "
            "«der plausibelste Pfad» — so sind die Artefakte vom 2026-08-27 entstanden."
        )
        assert "Bewertung von Wahrscheinlichkeit" not in text, (
            "Die alte Anweisung ist zurück: Sie verlangte vom Modell eine "
            "Wahrscheinlichkeitsaussage auf Basis des consistency_score."
        )


class TestDasBandBenenntWasEsMisst:
    """Zusage 2 — die Bänder sagen «widerspruchsfrei», nicht «hoch»."""

    @pytest.mark.parametrize(
        ("score", "erwartet"),
        [
            (0.97, "widerspruchsfrei"),
            (0.70, "widerspruchsfrei"),
            (0.66, "gemischt"),
            (0.40, "gemischt"),
            (0.31, "spannungsreich"),
        ],
    )
    def test_die_baender(self, score: float, erwartet: str) -> None:
        assert _konsistenz_band(score) == erwartet

    def test_ohne_score_gibt_es_kein_band(self) -> None:
        """Der frühere Rückfall machte aus dem Rang eine Weltaussage."""

        assert _konsistenz_band(None) is None

    def test_kein_band_traegt_eine_wertung(self) -> None:
        wertende = {"hoch", "mittel", "niedrig", "gering", "stark", "schwach"}
        gemessen = {_konsistenz_band(s) for s in (0.97, 0.66, 0.31)}
        assert not (
            gemessen & wertende
        ), f"Ein Band klingt wieder nach Rangfolge statt nach Messung: {gemessen}"


class TestDieBedeutungReistMit:
    """Zusage 3 — die Zahl verlässt den Lauf nicht ohne ihre Lesart."""

    def test_jede_konstellation_traegt_die_bedeutung(self) -> None:
        klass = type("Ctx", (), {"cib_matrix": None})
        szenarien = [{"rank": 1, "factor_constellation": {}}]
        _score_constellations(klass(), szenarien)

        assert szenarien[0]["konsistenz_bedeutung"] == KONSISTENZ_BEDEUTUNG
        assert szenarien[0]["konsistenz_band"] is None, "ohne Matrix kein Band"

    def test_die_bedeutung_nennt_beide_haelften(self) -> None:
        """Sagen, was der Score misst, reicht nicht — er wird ja falsch *gelesen*."""

        assert "nicht Wahrscheinlichkeit" in KONSISTENZ_BEDEUTUNG
        assert "gemischt" in KONSISTENZ_BEDEUTUNG.lower()
        assert "nicht unwahrscheinlicher" in KONSISTENZ_BEDEUTUNG

    def test_der_prompt_traegt_die_bedeutung_in_den_kontext(self) -> None:
        """Nicht nur ins Artefakt — das Modell liest den Kontextblock, nicht die Doku."""

        quelle = (SRC / "reporting" / "run_scenario_generator" / "prompt.py").read_text(
            encoding="utf-8"
        )
        assert "cib_consistency_bedeutung" in quelle
        assert "KONSISTENZ_BEDEUTUNG" in quelle


def _plausibility_im_code(quelle: str) -> list[tuple[int, str]]:
    """Jede Stelle, an der `plausibility` als **Code** vorkommt.

    Vier Formen, und jede kam in der alten Fassung vor: der Dict-Schlüssel
    (`sc["plausibility"]`), die Funktionsdefinition (`_plausibility_from_score`),
    ihr Aufruf (ein `Name`) und der Import als Attribut. Ein Grep über die Datei
    fände auch die Docstrings, die gerade erklären, warum es weg ist.
    """

    baum = ast.parse(quelle)
    docstrings = {
        id(eltern.body[0].value)
        for eltern in ast.walk(baum)
        if isinstance(eltern, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and getattr(eltern, "body", None)
        and isinstance(eltern.body[0], ast.Expr)
        and isinstance(eltern.body[0].value, ast.Constant)
    }

    treffer: list[tuple[int, str]] = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str):
            if id(knoten) in docstrings:
                continue
            if "plausibility" in knoten.value:
                treffer.append((knoten.lineno, f'"{knoten.value}"'))
        elif isinstance(knoten, ast.Name) and "plausibility" in knoten.id:
            treffer.append((knoten.lineno, knoten.id))
        elif isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if "plausibility" in knoten.name:
                treffer.append((knoten.lineno, f"def {knoten.name}"))
        elif isinstance(knoten, ast.Attribute) and "plausibility" in knoten.attr:
            treffer.append((knoten.lineno, knoten.attr))
        elif isinstance(knoten, ast.alias) and "plausibility" in knoten.name:
            treffer.append((getattr(knoten, "lineno", 0), f"import {knoten.name}"))
    return treffer


def test_der_waechter_wuerde_einen_rueckfall_bemerken() -> None:
    """Vier Formen des Rückfalls, und ein Docstring, der keiner ist."""

    rueckfaelle = [
        'def f(sc):\n    sc["plausibility"] = "hoch"\n',
        "def _plausibility_from_score(s):\n    return s\n",
        "def g(s):\n    return _plausibility_for_rank(s)\n",
        "from src.x import _plausibility_for_rank\n",
    ]
    for quelle in rueckfaelle:
        assert _plausibility_im_code(quelle), f"nicht bemerkt: {quelle!r}"

    harmlos = '"""Hieß bis P2.0 plausibility und ist es nicht mehr."""\n'
    assert not _plausibility_im_code(harmlos), "ein Docstring hat einen Fehlalarm ausgelöst"


def test_ein_echtes_altes_artefakt_zeigt_den_befund() -> None:
    """Der Beleg, warum das kein theoretisches Problem war.

    Läuft nur, wenn das Artefakt vom 2026-08-27 noch lokal liegt; in der CI und
    auf frischen Klonen gibt es `outputs/` nicht.
    """

    pfad = REPO_ROOT / "outputs" / "run_20260827T181422Z" / "run_scenario.json"
    if not pfad.exists():
        pytest.skip("kein historisches Artefakt vorhanden")

    daten = json.loads(pfad.read_text(encoding="utf-8"))
    szenarien = daten.get("scenarios") or []
    if not szenarien:
        pytest.skip("Artefakt ohne Szenarien")

    erstes = szenarien[0]
    zustaende = set((erstes.get("factor_constellation") or {}).values())
    if not zustaende:
        pytest.skip("Artefakt ohne Faktorkonstellation")

    # Rang 1 war der vollstaendig gleichpolige Zustand -- und trug «hoch».
    assert erstes.get("plausibility") == "hoch"
    assert all(
        z.endswith(".1") for z in zustaende
    ), "Der Befund lebt davon, dass Rang 1 der vollständig gleichpolige Zustand war."
