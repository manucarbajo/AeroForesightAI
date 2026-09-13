"""Eine Kachel in drei Varianten statt zweier Bausteine (P7.1-U1.4, Entscheidung E5).

**Der Befund:** Eine Kennzahl kam aus `ui.metric_tile` (mit einem Schalter
`prose` für Text) oder aus `ui.kpi_card` (für die Telemetrie). Welche Gestalt
sie bekam, hing daran, welcher Baustein an der Stelle benutzt wurde — nicht
daran, was der Wert ist.

**Was gilt:** `ui.kachel(label, wert, variante=…)` mit den Varianten aus
`ui.KACHEL_VARIANTEN`. Gehalten über den Syntaxbaum: Die alten Bausteine gibt es
nicht mehr, jeder Aufruf nennt eine Variante, die es gibt, und eine
Veränderung (`delta`) steht nur an einer kompakten Kachel.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from dashboard.web import components as ui

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"


def _befunde(quelle: str, datei: str) -> list[str]:
    befunde: list[str] = []
    for k in ast.walk(ast.parse(quelle)):
        if not (
            isinstance(k, ast.Call)
            and isinstance(k.func, ast.Attribute)
            and isinstance(k.func.value, ast.Name)
            and k.func.value.id == "ui"
        ):
            continue
        if k.func.attr in ("metric_tile", "kpi_card"):
            befunde.append(
                f"{datei}:{k.lineno}: `ui.{k.func.attr}` gibt es nicht mehr — `ui.kachel`"
            )
            continue
        if k.func.attr != "kachel":
            continue
        worte = {w.arg: w.value for w in k.keywords}
        variante = worte.get("variante")
        name = "zahl"
        if variante is not None:
            if not isinstance(variante, ast.Constant):
                befunde.append(
                    f"{datei}:{k.lineno}: Variante aus `{ast.unparse(variante)}` — ungeprüft"
                )
                continue
            name = variante.value
            if name not in ui.KACHEL_VARIANTEN:
                befunde.append(f"{datei}:{k.lineno}: unbekannte Variante {name!r}")
                continue
        if name != "kompakt" and ({"delta", "direction"} & set(worte)):
            befunde.append(f"{datei}:{k.lineno}: Veränderung an einer Kachel «{name}»")
    return befunde


class TestEineKachel:
    def test_the_two_old_components_are_gone(self):
        assert not hasattr(ui, "metric_tile"), "`ui.metric_tile` ist zurück — es gibt `ui.kachel`"
        assert not hasattr(ui, "kpi_card"), "`ui.kpi_card` ist zurück — es gibt `ui.kachel`"

    def test_every_call_names_a_variant_that_exists(self):
        befunde: list[str] = []
        for pfad in sorted(WEB_ROOT.rglob("*.py")):
            befunde += _befunde(
                pfad.read_text(encoding="utf-8"), pfad.relative_to(WEB_ROOT).as_posix()
            )

        assert not befunde, "\n  ".join(["Kacheln ohne gültige Variante:", *befunde])

    def test_an_unknown_variant_fails_loudly(self):
        with pytest.raises(ValueError, match="prose"):
            ui.kachel("Szenario", "Standard-Ausgangslage", variante="prose")

    def test_a_change_belongs_to_the_compact_variant_only(self):
        """Eine Veränderung an einer großen Kachel verschwände sonst still."""

        with pytest.raises(ValueError, match="kompakt"):
            ui.kachel("Preis", "120 EUR", delta="+1 %")
        assert "+1 %" in str(ui.kachel("Preis", "120 EUR", variante="kompakt", delta="+1 %"))

    def test_the_three_variants_look_different(self):
        zahl = str(ui.kachel("Länge", 40))
        text = str(ui.kachel("Szenario", "Standard-Ausgangslage", variante="text"))
        kompakt = str(ui.kachel("Rate", "0,26", variante="kompakt"))

        assert ui.TITEL in zahl and ui.TITEL not in text
        assert ui.ABSCHNITT in text
        assert "af-kpi" in kompakt and "af-kpi" not in zahl + text

    def test_the_guard_would_notice_a_relapse(self):
        probe = (
            'ui.metric_tile("a", 1)\n'
            'ui.kpi_card("a", 1)\n'
            'ui.kachel("a", 1, variante="prose")\n'
            'ui.kachel("a", 1, delta="+1")\n'
            'ui.kachel("a", 1, variante=art)\n'
            'ui.kachel("a", 1, variante="kompakt", delta="+1")\n'
        )

        assert len(_befunde(probe, "probe.py")) == 5, _befunde(probe, "probe.py")
