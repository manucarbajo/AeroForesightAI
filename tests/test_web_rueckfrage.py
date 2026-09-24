"""Die Rückfrage vor einem Schreibzugriff ist ein gestalteter Dialog (P7.1-U1.4, D7).

**Der Befund:** Jede Handlung, die dauerhaft ins Modell schreibt, fragte über
`dcc.ConfirmDialogProvider` nach — also mit dem Dialog des Browsers: nicht aus
den Farbtokens, im dunklen Design ein heller Kasten, und mit einem «OK», das
nicht sagt, was es tut. **Von Haiko entschieden am 2026-09-13:** ein
gestalteter Dialog mit demselben Inhalt, ohne Änderungsvorschau.

**Was gilt:** Kein `ConfirmDialogProvider` mehr in `dashboard/web/` — das
Abnahmekriterium von P7.1. Jede Rückfrage ist ein `<dialog>` mit der Klasse
`af-rueckfrage`, ein Knopf öffnet sie, Abbrechen und Bestätigen stehen in einem
`form method="dialog"` (sie schließen ihn ohne Skript), «Abbrechen» ist der
erste Knopf (ihn fokussiert der Browser beim Öffnen), die Bestätigung trägt die
ID der Aktion, und die Reichweite steht darin. **Wie sich der Dialog verhält**
— modal, Fokus, Escape — misst Teil 11 von `tests/test_web_overflow.py`.
"""

from __future__ import annotations

import ast
from pathlib import Path

from dash import html

from dashboard.web.config_editor import controls as c
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Wie viele Rückfragen der Modell-Bereich mindestens trägt — gegen die eigene
#: Blindheit: Eine Suche, die keinen Dialog erkennt, erfüllt jede Zusage.
RUECKFRAGEN_MIN = 4


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None:
        yield from _walk(kinder)


def _texte(knoten) -> str:
    return " ".join(k for k in _walk(knoten) if isinstance(k, str))


def _props(knoten) -> dict:
    return knoten.to_plotly_json()["props"]


def _befunde(baum) -> tuple[list[str], int]:
    """Jede Rückfrage, die kein vollständiger gestalteter Dialog ist."""

    befunde: list[str] = []
    oeffner = {
        k.id["key"]
        for k in _walk(baum)
        if isinstance(getattr(k, "id", None), dict) and k.id.get("type") == c.ASK
    }
    dialoge = [k for k in _walk(baum) if isinstance(k, html.Dialog)]
    schluessel = [_props(d).get("data-rueckfrage") for d in dialoge]

    doppelt = sorted({s for s in schluessel if schluessel.count(s) > 1})
    if doppelt:
        befunde.append(f"Rückfragen mit demselben Schlüssel: {doppelt}")

    for dialog, name in zip(dialoge, schluessel):
        props = _props(dialog)
        wer = props.get("aria-label") or name
        if "af-rueckfrage" not in (props.get("className") or ""):
            befunde.append(f"«{wer}»: ohne `af-rueckfrage` — nicht aus den Tokens gestaltet")
        if name not in oeffner:
            befunde.append(f"«{wer}»: kein Knopf öffnet sie")
        formulare = [k for k in _walk(dialog) if isinstance(k, html.Form)]
        if not formulare or _props(formulare[0]).get("method") != "dialog":
            befunde.append(f'«{wer}»: ohne `form method="dialog"` — die Knöpfe schlössen sie nicht')
        knoepfe = [k for k in _walk(dialog) if isinstance(k, html.Button)]
        if not knoepfe or "Abbrechen" not in _texte(knoepfe[0]):
            befunde.append(
                f"«{wer}»: «Abbrechen» ist nicht der erste Knopf — ihn fokussiert der "
                "Browser beim Öffnen"
            )
        if not any(
            isinstance(getattr(k, "id", None), dict) and k.id.get("type") != c.ASK for k in knoepfe
        ):
            befunde.append(f"«{wer}»: keine Bestätigung mit der ID der Aktion darin")
        if c.REICHWEITE not in _texte(dialog):
            befunde.append(f"«{wer}»: nennt die Reichweite nicht")

    for name in sorted(oeffner - set(schluessel)):
        befunde.append(f"Ein Knopf öffnet eine Rückfrage, die es nicht gibt: {name}")
    return befunde, len(dialoge)


def _browser_dialoge(quelle: str, datei: str) -> list[str]:
    return [
        f"{datei}:{k.lineno}"
        for k in ast.walk(ast.parse(quelle))
        if (isinstance(k, ast.Attribute) and k.attr == "ConfirmDialogProvider")
        or (isinstance(k, ast.Name) and k.id == "ConfirmDialogProvider")
    ]


class TestDieRueckfrageIstEinGestalteterDialog:
    def test_no_browser_dialog_remains(self):
        """Das Abnahmekriterium von P7.1, gesucht über den Syntaxbaum."""

        funde: list[str] = []
        for pfad in sorted(WEB_ROOT.rglob("*.py")):
            funde += _browser_dialoge(
                pfad.read_text(encoding="utf-8"), pfad.relative_to(WEB_ROOT).as_posix()
            )

        assert not funde, f"`dcc.ConfirmDialogProvider` ist zurück: {funde}"

    def test_every_confirmation_in_the_model_is_complete(self):
        befunde, anzahl = _befunde(model_editor.body(initial_draft_dict()))

        assert not befunde, "\n  ".join(["Rückfragen im Modell-Bereich:", *befunde])
        assert anzahl >= RUECKFRAGEN_MIN, (
            f"Nur {anzahl} Rückfragen gefunden, erwartet mindestens {RUECKFRAGEN_MIN} — "
            "erkennt die Suche die Dialoge noch?"
        )

    def test_a_write_action_builds_exactly_one(self):
        befunde, anzahl = _befunde(
            c.write_action("probe", "Probe speichern", frage="Die Probe wird geschrieben.")
        )

        assert befunde == [] and anzahl == 1, befunde

    def test_the_guard_would_notice_a_relapse(self):
        from dashboard.web import components as ui

        kaputt = html.Div(
            [
                ui.button("Öffnen", id=c.ask_id({"type": c.WRITE, "action": "a"})),
                html.Dialog(
                    html.Div(
                        [
                            ui.button("Speichern", id={"type": c.WRITE, "action": "a"}),
                            ui.button("Abbrechen"),
                        ]
                    ),
                    **{"data-rueckfrage": "type=cfg-write|action=b"},
                ),
            ]
        )

        befunde, _ = _befunde(kaputt)

        # Klasse, Öffner, Formular, Reihenfolge, Reichweite, verwaister Öffner
        assert len(befunde) == 6, befunde
        assert _browser_dialoge("dcc.ConfirmDialogProvider(children=x)\n", "probe.py")
