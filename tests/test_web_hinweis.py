"""Ein Hinweisbaustein statt zwei (P7.1-U1.4, Entscheidung E5).

**Der Befund:** Für dieselbe Aufgabe gab es zwei Bausteine — `ui.note` für
erklärenden Text neben einer Entscheidung und `ui.alert` mit fünf Tönen für
Meldungen. Welcher gemeint war, entschied der **Name des Aufrufs** statt des
Tons; und `alert` fiel bei einem unbekannten Ton still auf «info» zurück, ein
Tippfehler in «warning» machte aus einer Warnung eine Auskunft.

**Was gilt:** Es gibt `ui.hinweis(text, ton)` mit sechs Tönen
(`ui.HINWEIS_TOENE`). Gehalten wird es **über den Syntaxbaum**, nicht über eine
Liste von Fundstellen: Jeder Aufruf nennt einen Ton, den es gibt — und wo der
Ton aus einer Variable kommt, wird die Funktion gelesen, die ihn liefert.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from dashboard.web import components as ui

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Aufrufe, deren Ton aus einer Variable kommt: (Datei, Ausdruck) → die
#: Funktion in derselben Datei, deren Rückgaben den Ton liefern.
TON_AUS_VARIABLE = {
    ("config_editor/__init__.py", "kind"): "_handle_action",
}

#: Wie viele Rückgaben mit Ton die Quelle mindestens tragen muss — gegen die
#: eigene Blindheit. Gemessen am 2026-09-13: 17.
QUELLE_TOENE_MIN = 10


def _ist_ui(knoten: ast.AST, *namen: str) -> bool:
    return (
        isinstance(knoten, ast.Call)
        and isinstance(knoten.func, ast.Attribute)
        and isinstance(knoten.func.value, ast.Name)
        and knoten.func.value.id == "ui"
        and knoten.func.attr in namen
    )


def _ton(aufruf: ast.Call) -> ast.AST | None:
    if len(aufruf.args) > 1:
        return aufruf.args[1]
    for wort in aufruf.keywords:
        if wort.arg == "ton":
            return wort.value
    return None


def _befunde(quelle: str, datei: str) -> list[str]:
    """Jeder Aufruf eines alten Bausteins und jeder Ton, den es nicht gibt."""

    befunde: list[str] = []
    for k in ast.walk(ast.parse(quelle)):
        if _ist_ui(k, "alert", "note"):
            befunde.append(
                f"{datei}:{k.lineno}: `ui.{k.func.attr}` gibt es nicht mehr — `ui.hinweis(text, ton)`"
            )
            continue
        if not _ist_ui(k, "hinweis"):
            continue
        ton = _ton(k)
        if ton is None:
            continue
        if isinstance(ton, ast.Constant):
            if ton.value not in ui.HINWEIS_TOENE:
                befunde.append(f"{datei}:{k.lineno}: unbekannter Ton {ton.value!r}")
        elif (datei, ast.unparse(ton)) not in TON_AUS_VARIABLE:
            befunde.append(
                f"{datei}:{k.lineno}: Ton aus `{ast.unparse(ton)}` — ohne Eintrag in "
                "`TON_AUS_VARIABLE`, also ungeprüft"
            )
    return befunde


def _toene_der_quelle(quelle: str, funktion: str) -> list[object]:
    """Das letzte Element jeder Tupel-Rückgabe einer Funktion."""

    for k in ast.walk(ast.parse(quelle)):
        if isinstance(k, ast.FunctionDef) and k.name == funktion:
            return [
                r.value.elts[-1].value
                for r in ast.walk(k)
                if isinstance(r, ast.Return)
                and isinstance(r.value, ast.Tuple)
                and isinstance(r.value.elts[-1], ast.Constant)
            ]
    raise AssertionError(f"Funktion {funktion} nicht gefunden")


class TestEinHinweisbaustein:
    def test_the_two_old_components_are_gone(self):
        assert not hasattr(ui, "alert"), "`ui.alert` ist zurück — es gibt nur `ui.hinweis`"
        assert not hasattr(ui, "note"), "`ui.note` ist zurück — es gibt nur `ui.hinweis`"

    def test_every_call_names_a_tone_that_exists(self):
        befunde: list[str] = []
        for pfad in sorted(WEB_ROOT.rglob("*.py")):
            datei = pfad.relative_to(WEB_ROOT).as_posix()
            befunde += _befunde(pfad.read_text(encoding="utf-8"), datei)

        assert not befunde, "\n  ".join(["Hinweise ohne gültigen Ton:", *befunde])

    @pytest.mark.parametrize("ort", sorted(TON_AUS_VARIABLE))
    def test_a_tone_from_a_variable_comes_from_known_literals(self, ort):
        datei, _ = ort
        funktion = TON_AUS_VARIABLE[ort]
        toene = _toene_der_quelle((WEB_ROOT / datei).read_text(encoding="utf-8"), funktion)

        assert len(toene) >= QUELLE_TOENE_MIN, (
            f"`{funktion}` liefert nur {len(toene)} Töne — liest der Wächter noch die "
            "richtige Funktion?"
        )
        fremd = sorted({t for t in toene if t not in ui.HINWEIS_TOENE})
        assert not fremd, f"`{funktion}` in {datei} liefert Töne, die es nicht gibt: {fremd}"

    def test_an_unknown_tone_fails_loudly(self):
        with pytest.raises(ValueError, match="warning"):
            ui.hinweis("Ein Tippfehler im Ton", "warning")

    def test_context_does_not_look_like_a_message(self):
        """Kontext ist keine Meldung — und trägt deshalb keine Meldungsklasse."""

        assert "af-alert" not in str(ui.hinweis("Kontext", "kontext"))
        for ton in set(ui.HINWEIS_TOENE) - {"kontext"}:
            assert "af-alert" in str(ui.hinweis("Meldung", ton)), ton

    def test_the_guard_would_notice_a_relapse(self):
        probe = (
            'ui.alert("x", "warning")\n'
            'ui.note("x")\n'
            'ui.hinweis("x", "warning")\n'
            'ui.hinweis("x", ton=gewaehlt)\n'
            'ui.hinweis("x", "warnung")\n'
        )

        befunde = _befunde(probe, "probe.py")

        assert len(befunde) == 4, befunde
        assert _toene_der_quelle('def q():\n    return 1, "x", "fehler"\n', "q") == ["fehler"]
