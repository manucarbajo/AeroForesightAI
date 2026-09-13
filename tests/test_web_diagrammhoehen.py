"""Zwei Höhenstufen für Diagramme (P7.1-U1.5, von Haiko entschieden am 2026-09-13).

**Der Befund:** Die Höhe eines Diagramms stand als Zahl an seiner Aufrufstelle —
420 px für die Aussagen, 320 px in der Übersicht, 520 px in der Animation. Drei
Werte für zwei Aufgaben, und die Animation war höher als jede Aussage, ohne
dass es dafür einen Grund gab.

**Was gilt:** `theme.HOEHE_AUSSAGE` (420 px) für Diagramme, die eine Frage
beantworten, `theme.HOEHE_KOMPAKT` (320 px) für Übersichten. **Gesucht, nicht
aufgezählt:** Der Syntaxbaum jeder Ansicht und von `theme.py` wird nach jeder
Höhenangabe durchsucht — als Argument (`height=`) und als Standardwert eines
Parameters `height`. Erlaubt sind die beiden Konstanten und die benannten Formen
in `EIGENE_FORMEN`, je mit Grund.
"""

from __future__ import annotations

import ast
from pathlib import Path

from dashboard.web import theme

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Die zwei Stufen, wie sie im Quelltext heißen.
STUFEN = {"theme.HOEHE_AUSSAGE", "theme.HOEHE_KOMPAKT", "HOEHE_AUSSAGE", "HOEHE_KOMPAKT"}

#: Formen, die keine Stufe sind — (Datei, Wert im Quelltext) → Grund.
EIGENE_FORMEN = {
    ("views/telemetry.py", "110"): (
        "Kennlinie in der rechten Zone: eine Verlaufslinie über einer Kennzahl, kein "
        "Diagramm mit Achsen und Legende"
    ),
    ("views/scene.py", "None"): (
        "Die Szene füllt den Viewport; ihre Höhe setzt der Rahmen (`clamp` im Stil), "
        "nicht die Figur"
    ),
}


def _hoehen(quelle: str) -> list[tuple[int, str]]:
    """(Zeile, Wert) jeder Höhenangabe: `height=` in einem Aufruf oder als Standardwert."""

    funde: list[tuple[int, str]] = []
    for knoten in ast.walk(ast.parse(quelle)):
        if isinstance(knoten, ast.Call):
            for wort in knoten.keywords:
                # **Durchreichen ist keine Angabe:** `height=height` gibt einen
                # Parameter weiter, dessen Standardwert unten geprüft wird.
                durchgereicht = isinstance(wort.value, ast.Name) and wort.value.id == "height"
                if wort.arg == "height" and not durchgereicht:
                    funde.append((wort.value.lineno, ast.unparse(wort.value)))
        elif isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
            argumente = knoten.args.args + knoten.args.kwonlyargs
            standards = [None] * (len(knoten.args.args) - len(knoten.args.defaults)) + list(
                knoten.args.defaults
            )
            standards += list(knoten.args.kw_defaults)
            for argument, standard in zip(argumente, standards):
                if argument.arg == "height" and standard is not None:
                    funde.append((standard.lineno, ast.unparse(standard)))
    return funde


def _befunde(quelle: str, datei: str) -> list[str]:
    return [
        f"{datei}:{zeile}: Höhe `{wert}` ist keine Stufe"
        for zeile, wert in _hoehen(quelle)
        if wert not in STUFEN and (datei, wert) not in EIGENE_FORMEN
    ]


def _dateien() -> list[Path]:
    return sorted((WEB_ROOT / "views").glob("*.py")) + [WEB_ROOT / "theme.py"]


class TestZweiHoehenstufen:
    def test_the_two_steps_are_what_was_decided(self):
        assert (theme.HOEHE_AUSSAGE, theme.HOEHE_KOMPAKT) == (420, 320)

    def test_every_chart_height_is_a_step_or_a_named_form(self):
        befunde: list[str] = []
        for pfad in _dateien():
            befunde += _befunde(
                pfad.read_text(encoding="utf-8"), pfad.relative_to(WEB_ROOT).as_posix()
            )

        assert not befunde, "\n  ".join(
            [
                "Diese Diagramme setzen ihre Höhe selbst:",
                *befunde,
                "Eine Aussage nimmt `theme.HOEHE_AUSSAGE`, eine Übersicht "
                "`theme.HOEHE_KOMPAKT`. Ist es wirklich eine eigene Form, gehört sie mit "
                "Grund in `EIGENE_FORMEN`.",
            ]
        )

    def test_the_search_finds_something(self):
        """Gegen die eigene Blindheit: Die heutigen Aufrufstellen werden gefunden."""

        gefunden = sum(len(_hoehen(p.read_text(encoding="utf-8"))) for p in _dateien())

        assert gefunden >= 5, f"Nur {gefunden} Höhenangaben gefunden — sucht der Wächter noch?"

    def test_every_named_form_still_exists_and_has_a_reason(self):
        vorhanden = {
            (p.relative_to(WEB_ROOT).as_posix(), wert)
            for p in _dateien()
            for _, wert in _hoehen(p.read_text(encoding="utf-8"))
        }

        for form, grund in EIGENE_FORMEN.items():
            assert form in vorhanden, f"Ausnahme ohne Stelle dahinter: {form}"
            assert len(grund) >= 30, f"Ausnahme ohne Grund: {form}"

    def test_the_guard_would_notice_a_relapse(self):
        probe = (
            "fig.update_layout(height=520)\n"
            "def _graph(fig, height: int = 420): pass\n"
            "fig.update_layout(height=theme.HOEHE_AUSSAGE)\n"
            "theme.style_figure(fig, height=height)\n"
            "style={'height': '12rem'}\n"
        )

        # Die Menge, nicht die Reihenfolge: `ast.walk` geht in die Breite.
        assert sorted(wert for _, wert in _hoehen(probe)) == ["420", "520", "theme.HOEHE_AUSSAGE"]
        assert len(_befunde(probe, "views/probe.py")) == 2
