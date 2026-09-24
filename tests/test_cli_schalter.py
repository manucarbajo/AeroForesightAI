"""Jeder Schalter einer CLI in `src/` wird von seinem Modul auch gelesen (P5.1, 2026-09-11).

**Anlass:** `run_simulation` deklarierte `--sweep` mit der Hilfe «Overrides
simulation parameters with sweep settings» und las `args.sweep` nirgends. Ein
Aufruf mit `--sweep` rechnete stumm den Standardlauf, mit Exit-Code 0 — ein
Startpfad, der etwas verwirft, ohne es zu sagen (Invariante 7). Der Schalter ist
entfernt; ein einzelnes Szenario rechnet
`python -m src.orchestration.scenario_sweeps --sweep <id>`.

**Gesucht wird, nicht aufgezählt:** jedes `add_argument` in `src/`, und sein Ziel
muss im selben Modul gelesen werden — als Attribut (`args.ziel`) oder über
`getattr(..., "ziel")`. Beim Einführen waren es 44 Optionen in sechs Modulen, und
genau eine war ungelesen: `--sweep`.

**Die Grenze der Prüfung, ausdrücklich:** Sie verlangt einen Lesezugriff unter
dem Namen des Ziels, nicht einen auf genau dieses Objekt. Liest das Modul
`self.quiet`, gilt `--quiet` als gelesen. Das ist Absicht — eine Datenflussanalyse
wäre eine zweite Behauptung, und der Befund, gegen den der Wächter antritt, war
ein Name, der **nirgends** vorkam.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"


def _ziel(aufruf: ast.Call) -> str | None:
    for kw in aufruf.keywords:
        if kw.arg == "dest" and isinstance(kw.value, ast.Constant):
            return str(kw.value.value)
    namen = [
        a.value for a in aufruf.args if isinstance(a, ast.Constant) and isinstance(a.value, str)
    ]
    lang = [n for n in namen if n.startswith("--")]
    if lang:
        return lang[0][2:].replace("-", "_")
    positional = [n for n in namen if not n.startswith("-")]
    return positional[0] if positional else None


def ungelesene_optionen(quelltext: str) -> tuple[dict[str, int], dict[str, int]]:
    """(alle Optionen, davon ungelesene) eines Moduls, je Ziel mit Zeilennummer."""

    baum = ast.parse(quelltext)
    optionen: dict[str, int] = {}
    gelesen: set[str] = set()
    for knoten in ast.walk(baum):
        if (
            isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Attribute)
            and knoten.func.attr == "add_argument"
        ):
            ziel = _ziel(knoten)
            if ziel:
                optionen[ziel] = knoten.lineno
        elif isinstance(knoten, ast.Attribute):
            gelesen.add(knoten.attr)
        if (
            isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id == "getattr"
            and len(knoten.args) >= 2
            and isinstance(knoten.args[1], ast.Constant)
        ):
            gelesen.add(str(knoten.args[1].value))
    return optionen, {z: n for z, n in optionen.items() if z not in gelesen}


def _alle_clis() -> dict[Path, tuple[dict[str, int], dict[str, int]]]:
    ergebnis = {}
    for pfad in sorted(SRC.rglob("*.py")):
        optionen, ungelesen = ungelesene_optionen(pfad.read_text(encoding="utf-8"))
        if optionen:
            ergebnis[pfad] = (optionen, ungelesen)
    return ergebnis


class TestJederSchalterWirdGelesen:
    def test_die_suche_findet_ueberhaupt_clis(self):
        """Ohne diesen Test wäre der nächste leer und damit grün."""

        clis = _alle_clis()

        assert any(p.name == "run_simulation.py" for p in clis), sorted(p.name for p in clis)
        assert sum(len(optionen) for optionen, _ in clis.values()) >= 20

    def test_keine_option_bleibt_ungelesen(self):
        befunde = [
            f"{pfad.relative_to(SRC.parent)}:{zeile} --{ziel.replace('_', '-')}"
            for pfad, (_, ungelesen) in _alle_clis().items()
            for ziel, zeile in ungelesen.items()
        ]

        assert befunde == [], (
            "Diese Schalter nimmt eine CLI an und liest sie nie — ein Aufruf damit "
            "rechnet stumm etwas anderes (Invariante 7): " + "; ".join(befunde)
        )

    def test_gegenprobe_eine_ungelesene_option_faellt_auf(self):
        quelle = (
            "import argparse\n"
            "p = argparse.ArgumentParser()\n"
            "p.add_argument('--gelesen')\n"
            "p.add_argument('--vergessen-worden', type=str)\n"
            "args = p.parse_args()\n"
            "print(args.gelesen)\n"
        )

        optionen, ungelesen = ungelesene_optionen(quelle)

        assert set(optionen) == {"gelesen", "vergessen_worden"}
        assert ungelesen == {"vergessen_worden": 4}


def test_run_simulation_weist_sweep_ab(monkeypatch, capsys):
    """Die Wirkung, nicht nur die Quelle: `--sweep` scheitert jetzt laut an argparse."""

    from src.run_simulation import _parse_args

    monkeypatch.setattr(sys, "argv", ["run_simulation", "--mock-llm", "--sweep", "co2_delayed"])

    with pytest.raises(SystemExit) as abbruch:
        _parse_args()

    assert abbruch.value.code == 2
    assert "--sweep" in capsys.readouterr().err
