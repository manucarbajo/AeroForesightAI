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

import ast
import re
from pathlib import Path

import pytest
from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web.config_editor import delta, start_flow, wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor, muster
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
        klassen = getattr(knoten, "className", None) or ""
        if not (isinstance(knoten, html.Details) and "af-expert" in klassen):
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
    pytest.param(muster.body, id="musterseite"),
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


# --- Die Regel zum Aufklappen (E5 Punkt 3) ------------------------------------

#: Die drei Arten aufzuklappen, nach Rang (E5 Punkt 3): ein **Akkordeon** für
#: gleichrangige Abschnitte, eine **Klappe** (`expert`) für Zweitrangiges
#: innerhalb eines Abschnitts, **«Mehr dazu»** (`explainer`) nur direkt an einem
#: Feld. **In etwas Aufgeklapptem steht nur Niedrigeres** — sonst klappt man
#: zweimal auf, um an Gleichrangiges zu kommen. So stand es bis zum 2026-09-13
#: in «Rohdaten ansehen»: drei Klappen in einer Klappe.
RANG = {"akkordeon": 3, "klappe": 2, "mehr": 1}

#: Wie viele aufklappbare Blöcke die Messung mindestens findet — gegen die
#: eigene Blindheit.
AUFKLAPPBAR_MIN = 30

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"


def _art(knoten) -> str | None:
    if not isinstance(knoten, html.Details):
        return None
    klassen = (getattr(knoten, "className", None) or "").split()
    if "af-acc" not in klassen:
        return "von Hand"
    if "af-expert" in klassen:
        return "klappe"
    if "af-card" in klassen:
        return "akkordeon"
    return "mehr"


def _beschriftet(knoten) -> bool:
    """Was ein Feld beschriftet: eine `html.Label` — oder ein Kästchen und eine Auswahl.

    `ui.checkbox`, `ui.toggle` und `ui.radio` tragen ihre Beschriftung in den
    Optionen, nicht in einer Label. Der zweite Messanlauf kannte nur die Label
    und meldete drei Kästchen-Felder als feldlos.
    """

    return isinstance(knoten, (html.Label, dcc.Checklist, dcc.RadioItems))


def _regelbrueche(baum) -> tuple[list[str], int]:
    befunde: list[str] = []
    gesehen = 0

    def gang(knoten, elemente: list, huellen: list[tuple[str, str]]) -> None:
        nonlocal gesehen
        if isinstance(knoten, str) or knoten is None:
            return
        art = _art(knoten)
        if art is not None:
            gesehen += 1
            kinder = _kinder(knoten)
            titel = _text(kinder[0])[:60] if kinder else ""
            if art == "von Hand":
                befunde.append(f"«{titel}»: aufklappbar ohne Baustein (`html.Details` von Hand)")
            else:
                if huellen and huellen[-1][0] in RANG and RANG[art] >= RANG[huellen[-1][0]]:
                    befunde.append(
                        f"«{titel}» ({art}) steht in «{huellen[-1][1]}» ({huellen[-1][0]})"
                    )
                if art == "mehr":
                    feld = elemente[-2] if len(elemente) >= 2 else None
                    if feld is None or not any(_beschriftet(k) for k in _kinder(feld)):
                        befunde.append(f"«{titel}» steht nicht an einem Feld")
            huellen = huellen + [(art, titel)]
        for kind in _kinder(knoten):
            gang(kind, elemente + [knoten], huellen)

    gang(baum, [], [])
    return befunde, gesehen


def _ist_ui_aufruf(knoten, *namen: str) -> bool:
    return (
        isinstance(knoten, ast.Call)
        and isinstance(knoten.func, ast.Attribute)
        and isinstance(knoten.func.value, ast.Name)
        and knoten.func.value.id == "ui"
        and knoten.func.attr in namen
    )


def _quelltext_befunde(quelle: str, datei: str) -> list[str]:
    """Direkte Verschachtelung im Quelltext und `html.Details` außerhalb der Bausteine.

    Der gerenderte Baum braucht einen Lauf für die Ergebnis-Ansichten; der
    Syntaxbaum nicht. Er sieht nur, was in **einem** Aufruf steht — eine
    Verschachtelung über eine Hilfsfunktion findet die Messung oben.
    """

    befunde: list[str] = []
    for k in ast.walk(ast.parse(quelle)):
        if (
            datei != "components.py"
            and isinstance(k, ast.Call)
            and isinstance(k.func, ast.Attribute)
            and k.func.attr == "Details"
        ):
            befunde.append(f"{datei}:{k.lineno}: `html.Details` von Hand statt eines Bausteins")
        for huelle, verboten in (
            ("expert", ("expert", "accordion")),
            ("explainer", ("expert", "accordion", "explainer")),
            ("accordion", ("accordion",)),
        ):
            if not _ist_ui_aufruf(k, huelle):
                continue
            for innen in ast.walk(k):
                if innen is not k and _ist_ui_aufruf(innen, *verboten):
                    befunde.append(
                        f"{datei}:{innen.lineno}: `ui.{innen.func.attr}` in `ui.{huelle}`"
                    )
    return befunde


class TestDieRegelZumAufklappen:
    def test_inside_a_disclosure_stands_only_something_lower(self):
        befunde: list[str] = []
        gesehen = 0
        for eintrag in BAEUME:
            funde, anzahl = _regelbrueche(eintrag.values[0]())
            befunde += [f"{eintrag.id}: {f}" for f in funde]
            gesehen += anzahl

        assert not befunde, "\n  ".join(
            [
                "Diese aufklappbaren Blöcke brechen die Regel aus E5:",
                *befunde,
                "Akkordeon für gleichrangige Abschnitte, Klappe für Zweitrangiges, «Mehr "
                "dazu» nur am Feld — und in etwas Aufgeklapptem steht nur Niedrigeres.",
            ]
        )
        assert gesehen >= AUFKLAPPBAR_MIN, (
            f"Nur {gesehen} aufklappbare Blöcke gefunden, erwartet mindestens "
            f"{AUFKLAPPBAR_MIN} — erkennt die Suche sie noch?"
        )

    def test_the_source_nests_nothing_and_builds_no_disclosure_by_hand(self):
        befunde: list[str] = []
        for pfad in sorted(WEB_ROOT.rglob("*.py")):
            befunde += _quelltext_befunde(
                pfad.read_text(encoding="utf-8"), pfad.relative_to(WEB_ROOT).as_posix()
            )

        assert not befunde, "\n  ".join(["Im Quelltext:", *befunde])

    def test_the_rule_guard_would_notice_a_relapse(self):
        feld = html.Div(
            [html.Label("Ticks"), dcc.Input(), html.Div([html.Div(), ui.explainer("Lang.")])]
        )
        kaestchen = html.Div(
            [
                dcc.Checklist(options=[{"label": "Alle Szenarien", "value": "on"}], value=[]),
                html.Div([html.Div(), ui.explainer("Lang.")]),
            ]
        )
        erlaubt = ui.accordion("Abschnitt", ui.expert(feld, kaestchen, title="Feinabstimmung"))
        verboten = html.Div(
            [
                ui.expert(ui.expert(html.Div(), title="Innen"), title="Außen"),
                ui.expert(ui.accordion("Abschnitt"), title="Klappe"),
                html.Div(ui.explainer("Ohne Feld.")),
                html.Details([html.Summary("Von Hand")]),
            ]
        )

        assert _regelbrueche(erlaubt)[0] == []
        assert len(_regelbrueche(verboten)[0]) == 4, _regelbrueche(verboten)[0]
        assert (
            len(
                _quelltext_befunde(
                    "ui.expert(ui.expert(x))\nui.accordion(ui.accordion(x))\nhtml.Details([])\n",
                    "probe.py",
                )
            )
            == 3
        )
