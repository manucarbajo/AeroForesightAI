"""Kein Klassenname ist in `src/` mehr als einmal definiert (P5.1, 2026-09-11).

**Anlass:** `LLMCallable` stand in sieben Modulen, jedes Mal dasselbe Protokoll.
Das ging gut, weil Protokolle strukturell verglichen werden — und genau deshalb
hätte niemand gemerkt, wenn eine Kopie auseinandergelaufen wäre. Dieselbe Klasse
wie `MockLLM` in P4.1: ein Name für mehrere Dinge.

**Gesucht wird, nicht aufgezählt:** jede Klassendefinition auf Modulebene in
`src/`. Beim Einführen gab es 127 Klassennamen und genau einen doppelten.
Verschachtelte Klassen (etwa `Config` in einem Modell) zählen nicht mit — sie
gehören zu ihrer äußeren Klasse, nicht zum Modul.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def doppelte_klassennamen(module: dict[str, str]) -> dict[str, list[str]]:
    """Modulpfad -> Quelltext rein, Klassenname -> Module raus, wo er mehr als einmal steht."""

    orte: dict[str, list[str]] = defaultdict(list)
    for pfad, quelltext in module.items():
        for knoten in ast.parse(quelltext).body:
            if isinstance(knoten, ast.ClassDef):
                orte[knoten.name].append(pfad)
    return {name: sorted(pfade) for name, pfade in orte.items() if len(pfade) > 1}


def _src() -> dict[str, str]:
    return {
        str(p.relative_to(SRC.parent)): p.read_text(encoding="utf-8")
        for p in sorted(SRC.rglob("*.py"))
    }


def test_die_suche_findet_ueberhaupt_klassen():
    """Ohne diesen Test wäre der nächste leer und damit grün."""

    anzahl = sum(isinstance(k, ast.ClassDef) for q in _src().values() for k in ast.parse(q).body)

    assert anzahl >= 100, anzahl


def test_kein_klassenname_steht_zweimal():
    doppelt = doppelte_klassennamen(_src())

    assert doppelt == {}, (
        "Diese Klassennamen sind in mehreren Modulen definiert — eine Quelle, "
        "und die anderen importieren sie: "
        + "; ".join(f"{name}: {', '.join(orte)}" for name, orte in doppelt.items())
    )


def test_gegenprobe_ein_doppelter_name_faellt_auf():
    module = {
        "a.py": "class Einmal: ...\nclass Zweimal: ...\n",
        "b.py": "class Zweimal: ...\nclass Aussen:\n    class Einmal: ...\n",
    }

    assert doppelte_klassennamen(module) == {"Zweimal": ["a.py", "b.py"]}
