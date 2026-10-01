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


def test_jede_auswahlliste_spricht_deutsch():
    """Dash 4 schreibt «Search» in das Suchfeld einer Auswahlliste — im Schritt
    «Verläufe» gefunden. Jeder Aufruf von `dcc.Dropdown` bekommt deshalb
    `labels=ui.AUSWAHL_TEXTE`; gesucht wird der Aufruf, nicht eine Liste."""

    ohne = []
    aufrufe = 0
    for pfad in sorted(WEB.rglob("*.py")):
        for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
            if (
                isinstance(knoten, ast.Call)
                and isinstance(knoten.func, ast.Attribute)
                and knoten.func.attr == "Dropdown"
            ):
                aufrufe += 1
                if not any(k.arg == "labels" for k in knoten.keywords):
                    ohne.append(f"{pfad.relative_to(WEB)}:{knoten.lineno}")

    assert aufrufe, "Misst der Test ins Leere?"
    assert not ohne, f"Auswahlliste ohne deutsche Texte: {ohne}"


def test_die_texte_sind_gueltige_schluessel():
    from dash import dcc

    from dashboard.web import components as ui

    dcc.Dropdown(options=[], labels=ui.AUSWAHL_TEXTE)
    assert "Search" not in ui.AUSWAHL_TEXTE.values()


def test_der_png_export_nennt_keinen_pfad_des_rechners(tmp_path):
    """Befund 13: «Speicherort:» mit dem vollen Ordner des Rechners stand über den Bildern."""

    from dashboard.web.views import figures

    lauf = tmp_path / "run_x"
    (lauf / "figures").mkdir(parents=True)

    text = str(figures._view_png(lauf))

    assert str(tmp_path) not in text and "Speicherort" not in text


#: Die Bildbeschriftungen des PNG-Exports (matplotlib) — englische Reste aus dem
#: Abnahme-Durchgang: «Preis und Booking», Achse «Booking Rate», «EUR».
VERBOTEN_IN_BILDERN = ("Booking", "EUR", "Property", "Policy", "Consistency")


def test_die_bilder_des_png_exports_sind_deutsch_beschriftet():
    quelle = Path(__file__).resolve().parents[1] / "src" / "reporting" / "figure_generator"
    funde = [
        f"{pfad.name}:{zeile}: {text!r}"
        for name in ("plots.py", "global_figures.py")
        for pfad in [quelle / name]
        for zeile, text in _texte(pfad)
        for wort in VERBOTEN_IN_BILDERN
        if wort in text
    ]

    assert not funde, "\n".join(funde)
