"""Kein Entwicklerbegriff in einem Text, den die Oberfläche zeigt (Befund 13, 2026-10-01).

Der Abnahme-Durchgang vom 2026-09-30 fand unter anderem «Modell in .env» in der
Abfrage, «Markt-Feedback gespeichert» für den Abschnitt «Preisverhalten der
Airline» und «Property-ID (Python-Bezeichner)» im Modell-Bereich. Gesucht wird
in **jeder** Zeichenkette unter `dashboard/web/`, die kein Docstring ist — nicht
in einer Liste der Fundstellen, damit die nächste auffällt.
"""

from __future__ import annotations

import ast
from pathlib import Path

WEB = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Begriffe, die ein Nutzer nicht lesen soll. Klein gehalten: Jeder steht hier,
#: weil er im sichtbaren Text gefunden wurde.
VERBOTEN = (
    ".env",
    "Python-Bezeichner",
    "Property-ID",
    "Property «",
    "Markt-Feedback gespeichert",
    "Population und Sättigung gespeichert",
)


def _texte(pfad: Path) -> list[tuple[int, str]]:
    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    docstrings = {
        id(knoten.body[0].value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
        and knoten.body
        and isinstance(knoten.body[0], ast.Expr)
        and isinstance(knoten.body[0].value, ast.Constant)
    }
    return [
        (knoten.lineno, knoten.value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.Constant)
        and isinstance(knoten.value, str)
        and id(knoten) not in docstrings
    ]


def test_kein_entwicklerbegriff_im_sichtbaren_text():
    funde = [
        f"{pfad.relative_to(WEB)}:{zeile}: {wort!r} in {text[:80]!r}"
        for pfad in sorted(WEB.rglob("*.py"))
        for zeile, text in _texte(pfad)
        for wort in VERBOTEN
        if wort in text
    ]

    assert not funde, "\n".join(funde)


def test_die_suche_findet_einen_rueckfall(tmp_path):
    probe = tmp_path / "probe.py"
    probe.write_text(
        'def f():\n    """.env im Docstring zählt nicht."""\n    return "Modell in .env"\n',
        encoding="utf-8",
    )

    assert [text for _z, text in _texte(probe) if ".env" in text] == ["Modell in .env"]
