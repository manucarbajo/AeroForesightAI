"""Eine Klappe zählt, was sie enthält (P7.1-U1.4, Entscheidung E5 Punkt 4).

**Der Befund:** `ui.expert` hängte an jede Zahl das Wort «Parameter» — auch an
«Rohdaten ansehen», eine Klappe mit drei Vorschauen und keiner einzigen Eingabe.
Das Audit nannte diese eine Stelle. **Die Messung über alle gerenderten Klappen
fand am 2026-09-13 zwei weitere**: die Herkunftsangaben in «Prüfen & Starten»
(«2 Parameter» an Codestand und Fingerabdruck) und die Liste der Abweichungen
von der Auslieferung. Der Baustein zählte, was man ihm gab, und nannte es
Parameter.

**Was gilt:** Eine Klappe, die «N Parameter» sagt, enthält genau N Eingaben —
gemessen im **gerenderten Baum**, nicht an einer Liste von Aufrufen: Die
Abweichungsliste wird im Standardentwurf gar nicht gezeichnet, und eine Zählung
über den Quelltext wüsste nicht, was in den Kindern steckt. Wer etwas anderes
zählt, sagt es (`einheit=`).
"""

from __future__ import annotations

import re

import pytest
from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web.config_editor import delta, start_flow, wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict

#: Was als Eingabe zählt. Knöpfe nicht — «Szenario sichern» neben einem
#: Dateinamen ist eine Handlung, kein Parameter.
EINGABEN = (
    dcc.Input,
    dcc.Dropdown,
    dcc.Checklist,
    dcc.RadioItems,
    dcc.Slider,
    dcc.RangeSlider,
    dcc.Textarea,
)

#: Wie viele «N Parameter»-Klappen die Messung mindestens findet — gegen die
#: eigene Blindheit: Eine Suche, die keine Klappe mehr erkennt, erfüllt jede
#: Zusage.
GEZAEHLTE_MIN = 8

_PARAMETER = re.compile(r"\((\d+) Parameter\)")


def _kinder(knoten) -> list:
    kinder = getattr(knoten, "children", None)
    if kinder is None:
        return []
    return list(kinder) if isinstance(kinder, (list, tuple)) else [kinder]


def _text(knoten) -> str:
    if isinstance(knoten, str):
        return knoten
    return "".join(_text(k) for k in _kinder(knoten))


def _eingaben(knoten) -> int:
    if isinstance(knoten, str) or knoten is None:
        return 0
    eigen = 1 if isinstance(knoten, EINGABEN) else 0
    return eigen + sum(_eingaben(k) for k in _kinder(knoten))


def _befunde(baum) -> tuple[list[str], int]:
    """Jede «N Parameter»-Klappe, deren Rumpf nicht N Eingaben trägt."""

    befunde: list[str] = []
    gezaehlt = 0
    stapel = [baum]
    while stapel:
        knoten = stapel.pop()
        if isinstance(knoten, str) or knoten is None:
            continue
        stapel.extend(_kinder(knoten))
        if not (isinstance(knoten, html.Details) and "af-expert" in (knoten.className or "")):
            continue
        kopf, *rumpf = _kinder(knoten)
        treffer = _PARAMETER.search(_text(kopf))
        if not treffer:
            continue
        gezaehlt += 1
        genannt = int(treffer.group(1))
        gefunden = sum(_eingaben(teil) for teil in rumpf)
        if genannt != gefunden:
            befunde.append(
                f"«{_text(kopf)[:70]}» nennt {genannt} Parameter und enthält {gefunden} Eingaben"
            )
    return befunde, gezaehlt


def _mit_abweichung() -> dict:
    entwurf = initial_draft_dict()
    entwurf["rounds"] = int(entwurf.get("rounds") or 40) + 7
    return entwurf


BAEUME = [
    pytest.param(lambda: wizard.entry(initial_draft_dict()), id="einstieg"),
    *[
        pytest.param(lambda i=i: wizard.content(initial_draft_dict(), i), id=f"schritt-{s.key}")
        for i, s in enumerate(wizard.STEPS)
    ],
    pytest.param(
        lambda: start_flow.scenario_details(
            start_flow.apply(initial_draft_dict(), start_flow.STANDARD)
        ),
        id="standard",
    ),
    pytest.param(lambda: model_editor.body(initial_draft_dict()), id="modell"),
    pytest.param(lambda: launch_page.rail(initial_draft_dict()), id="bedienfeld"),
    pytest.param(lambda: delta.layout(_mit_abweichung()), id="abweichungen"),
]


class TestEineKlappeZaehltWasSieEnthaelt:
    def test_every_parameter_count_matches_its_inputs(self):
        befunde: list[str] = []
        gezaehlt = 0
        for eintrag in BAEUME:
            funde, anzahl = _befunde(eintrag.values[0]())
            befunde += [f"{eintrag.id}: {f}" for f in funde]
            gezaehlt += anzahl

        assert not befunde, "\n  ".join(
            [
                "Diese Klappen zählen etwas anderes als Parameter:",
                *befunde,
                "Wer Dateien, Angaben oder Abweichungen zählt, sagt es mit `einheit=`.",
            ]
        )
        assert gezaehlt >= GEZAEHLTE_MIN, (
            f"Nur {gezaehlt} «N Parameter»-Klappen gefunden, erwartet mindestens "
            f"{GEZAEHLTE_MIN} — erkennt die Suche die Klappen noch?"
        )

    def test_the_deviation_list_is_really_measured(self):
        """Vorbedingung: Mit einer Abweichung ist die Liste eine Klappe, kein Satz."""

        liste = delta.layout(_mit_abweichung())

        assert isinstance(
            liste, html.Details
        ), "Keine Abweichung erkannt — misst der Test ins Leere"
        assert "(1 Abweichung)" in _text(liste)

    def test_a_block_names_what_it_counts(self):
        assert "(2 Parameter)" in _text(ui.expert(html.Div(), count=2, title="A"))
        assert "(1 Angabe)" in _text(
            ui.expert(html.Div(), count=1, title="A", einheit=("Angabe", "Angaben"))
        )
        assert "(3 Angaben)" in _text(
            ui.expert(html.Div(), count=3, title="A", einheit=("Angabe", "Angaben"))
        )

    def test_the_guard_would_notice_a_relapse(self):
        falsch = ui.expert(html.Div("drei Vorschauen"), count=3, title="Rohdaten ansehen")
        richtig = ui.expert(dcc.Input(), html.Div(dcc.Dropdown()), count=2, title="Zwei")

        assert _befunde(html.Div([falsch, richtig])) == (
            [
                "«chevron_rightRohdaten ansehen (3 Parameter)» nennt 3 Parameter und enthält 0 Eingaben"
            ],
            2,
        )
