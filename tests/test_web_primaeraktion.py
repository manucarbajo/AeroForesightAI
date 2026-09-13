"""Höchstens eine Primäraktion je Fläche (P7.1-U1.4, Entscheidung E5).

**Der Befund:** Ein Primärknopf sagt «hier geht es weiter». Der Bereich «Modell»
trug drei davon auf einer Fläche — «Größe anlegen», «Segment anlegen» und
«Bevölkerung als Standard speichern» —, während «Als Standard speichern» für das
Preisverhalten zwei Abschnitte darüber sekundär war. Welche Handlung
hervorgehoben war, hing am Aufruf, nicht an einer Regel. **Und `primary` ist die
Vorgabe von `ui.button`:** Die Entscheidungsvorlage zählte drei ausdrückliche
Primärknöpfe und übersah die vier, die ihn still bekommen.

**Was gilt:** Keine Fläche zeigt mehr als eine Primäraktion — gemessen im
**gerenderten Baum**, damit die stillen mitzählen. Versteckte Knöpfe
(`display: none`, Regel 6) zählen nicht: «Weiter» und «Lauf starten» stehen
beide in der Fußleiste, aber nie gleichzeitig. Ein Knopf in einer
zugeklappten Klappe zählt dagegen — wer aufklappt, sieht ihn neben dem Rest.
Für Ansichten, die ohne Lauf nicht zu zeichnen sind, zählt der Syntaxbaum je
Datei.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from dash import html

from dashboard.web.config_editor import wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

PRIMAER_MAX = 1

#: Wie viele sichtbare Primäraktionen die Messung über alle Flächen mindestens
#: findet — gegen die eigene Blindheit. Gemessen am 2026-09-13: sieben (sechs
#: Schritte und das Bedienfeld), der Modell-Bereich nicht mitgezählt.
PRIMAER_GESAMT_MIN = 5


def _kinder(knoten) -> list:
    kinder = getattr(knoten, "children", None)
    if kinder is None:
        return []
    return list(kinder) if isinstance(kinder, (list, tuple)) else [kinder]


def _text(knoten) -> str:
    if isinstance(knoten, str):
        return knoten
    return "".join(_text(k) for k in _kinder(knoten))


def _primaer(knoten, versteckt: bool = False) -> list[str]:
    """Die Beschriftung jeder sichtbaren Primäraktion im Baum."""

    if isinstance(knoten, str) or knoten is None:
        return []
    stil = getattr(knoten, "style", None) or {}
    versteckt = versteckt or stil.get("display") == "none"
    eigen: list[str] = []
    klassen = getattr(knoten, "className", None) or ""
    if isinstance(knoten, html.Button) and "af-btn--primary" in klassen and not versteckt:
        eigen = [_text(knoten)]
    return eigen + [t for kind in _kinder(knoten) for t in _primaer(kind, versteckt)]


def _flaechen() -> list[tuple[str, object]]:
    entwurf = initial_draft_dict()
    flaechen: list[tuple[str, object]] = [
        ("Einstieg", html.Div([wizard.entry(entwurf), wizard.navigation(wizard.ENTRY)]))
    ]
    flaechen += [
        (step.title, html.Div([wizard.content(entwurf, i), wizard.navigation(i)]))
        for i, step in enumerate(wizard.STEPS)
    ]
    flaechen += [
        ("Modell", model_editor.body(entwurf)),
        ("Bedienfeld", launch_page.rail(entwurf)),
    ]
    return flaechen


def _primaer_im_quelltext(quelle: str) -> list[int]:
    """Zeilen, an denen eine Primäraktion entsteht — ausdrücklich oder still."""

    zeilen: list[int] = []
    for k in ast.walk(ast.parse(quelle)):
        if not (isinstance(k, ast.Call) and isinstance(k.func, ast.Attribute)):
            continue
        variante = next((w.value for w in k.keywords if w.arg == "variant"), None)
        wert = variante.value if isinstance(variante, ast.Constant) else None
        if k.func.attr == "button" and (variante is None or wert == "primary"):
            zeilen.append(k.lineno)
        elif k.func.attr == "write_action" and wert == "primary":
            zeilen.append(k.lineno)
    return zeilen


class TestHoechstensEinePrimaeraktionJeFlaeche:
    def test_no_surface_shows_more_than_one(self):
        zu_viele = []
        gesamt = 0
        for name, baum in _flaechen():
            knoepfe = _primaer(baum)
            gesamt += len(knoepfe)
            if len(knoepfe) > PRIMAER_MAX:
                zu_viele.append(f"{name}: {len(knoepfe)} — {knoepfe}")

        assert not zu_viele, "\n  ".join(
            [
                "Diese Flächen heben mehr als eine Handlung hervor:",
                *zu_viele,
                "Eine Primäraktion sagt «hier geht es weiter». Die übrigen tragen "
                '`variant="secondary"` — und `primary` ist die Vorgabe von `ui.button`.',
            ]
        )
        assert gesamt >= PRIMAER_GESAMT_MIN, (
            f"Nur {gesamt} Primäraktionen gefunden, erwartet mindestens {PRIMAER_GESAMT_MIN} "
            "— erkennt die Messung die Knöpfe noch?"
        )

    @pytest.mark.parametrize(
        "pfad", sorted((WEB_ROOT / "views").glob("*.py")), ids=lambda p: p.name
    )
    def test_a_result_view_creates_at_most_one_in_its_source(self, pfad):
        zeilen = _primaer_im_quelltext(pfad.read_text(encoding="utf-8"))

        assert len(zeilen) <= PRIMAER_MAX, (
            f"views/{pfad.name} erzeugt {len(zeilen)} Primäraktionen (Zeilen {zeilen}) — "
            "eine Ergebnis-Ansicht ist eine Fläche."
        )

    def test_the_guard_would_notice_a_relapse(self):
        from dashboard.web import components as ui

        zwei = html.Div([ui.button("Anlegen"), ui.button("Speichern")])
        eine_versteckt = html.Div(
            [ui.button("Weiter"), ui.button("Lauf starten", style={"display": "none"})]
        )

        assert len(_primaer(zwei)) == 2
        assert len(_primaer(eine_versteckt)) == 1
        assert _primaer_im_quelltext(
            'ui.button("a")\nui.button("b", variant="secondary")\n'
            'c.write_action("x", "y", frage="z", variant="primary")\n'
        ) == [1, 3]
