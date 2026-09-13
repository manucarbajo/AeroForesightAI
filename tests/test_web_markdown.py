"""Kein Markdown steht roh in der Oberfläche (P7.0-U0.3, vorgezogen am 2026-09-11).

**Der Befund:** Im Browser standen `**Name**` (Schritt 4), `**Ob**` (Schritt 5)
und `**nicht**` samt einem fett gemeinten Satz in der Kohärenzbegründung
(Schritt 1) wörtlich da, mit Sternchen. Die Texte sind als Markdown geschrieben,
gerendert wurden sie als `html.P` — **ob Markdown gerendert wird, entschied der
Aufrufer, nicht der Text.** So kehrt der Fehler mit jedem neuen Baustein zurück.

**Zwei Wächter, weil es zwei Wege hinein gibt:**

* **Im Quelltext** — ein Textbaustein (`html.P`, `html.Span`, …), dem ein
  Literal mit `**` oder einem Backtick-Paar übergeben wird. Er sagt *wo*.
* **Im gerenderten Baum** — Text aus Daten, etwa die Kohärenzbegründung aus
  `configs/`, landet über eine Variable im Baustein; das sieht kein
  Syntaxbaum. Dieser Wächter rendert die Bereiche, in denen solche Texte
  auftauchen, und sucht Markdown-Zeichen außerhalb von `dcc.Markdown`,
  `html.Code` und `html.Pre`. Er sagt *dass*.

Ein Vollbild im Browser über alle Ansichten bleibt P7.0-U0.3 vorbehalten; hier
laufen die Bereiche, die ohne Lauf und ohne Browser zu bauen sind.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest
from dash import dcc, html

from dashboard.config_catalog import list_sweep_presets
from dashboard.web.config_editor import start_flow, wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Bausteine, die ihren Text **wörtlich** zeigen.
TEXTBAUSTEINE = {"P", "Span", "Div", "Li", "H1", "H2", "H3", "H4", "Label", "Small", "Strong"}

#: Bausteine, in denen Markdown-Zeichen gewollt oder wirkungslos sind.
GESCHUETZT = (dcc.Markdown, html.Code, html.Pre)

_FETT = "**"
_CODE = re.compile(r"`[^`\n]+`")


def _roh(text: str) -> bool:
    return _FETT in text or bool(_CODE.search(text))


# --- Im Quelltext ------------------------------------------------------------


def _literal(knoten: ast.AST) -> str | None:
    """Der wörtliche Anteil eines Arguments — Zeichenkette oder f-String."""

    if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str):
        return knoten.value
    if isinstance(knoten, ast.JoinedStr):
        return "".join(
            teil.value
            for teil in knoten.values
            if isinstance(teil, ast.Constant) and isinstance(teil.value, str)
        )
    return None


def _funde_im_quelltext() -> list[str]:
    funde: list[str] = []
    for datei in sorted(WEB_ROOT.rglob("*.py")):
        baum = ast.parse(datei.read_text(encoding="utf-8"))
        for knoten in ast.walk(baum):
            if not (
                isinstance(knoten, ast.Call)
                and isinstance(knoten.func, ast.Attribute)
                and isinstance(knoten.func.value, ast.Name)
                and knoten.func.value.id == "html"
                and knoten.func.attr in TEXTBAUSTEINE
            ):
                continue
            argumente = list(knoten.args[:1]) + [
                k.value for k in knoten.keywords if k.arg == "children"
            ]
            for argument in argumente:
                text = _literal(argument)
                if text is not None and _roh(text):
                    ort = datei.relative_to(WEB_ROOT.parent.parent)
                    funde.append(f"{ort}:{knoten.lineno}: html.{knoten.func.attr}({text[:60]!r}…)")
    return funde


def test_no_text_block_is_handed_markdown_in_the_source():
    funde = _funde_im_quelltext()

    assert not funde, (
        "Markdown in einem Baustein, der seinen Text wörtlich zeigt — die Zeichen "
        "stehen dann sichtbar da:\n  "
        + "\n  ".join(funde)
        + "\n\nText mit Auszeichnung gehört in `ui.markdown`, `ui.lede` oder `ui.hinweis`."
    )


# --- Im gerenderten Baum -----------------------------------------------------


def _roher_text(knoten, geschuetzt: bool = False) -> list[str]:
    """Jeder sichtbare Text mit Markdown-Zeichen, der nicht als Markdown gerendert wird."""

    if knoten is None:
        return []
    if isinstance(knoten, str):
        return [knoten[:80]] if not geschuetzt and _roh(knoten) else []
    if isinstance(knoten, (list, tuple)):
        return [fund for kind in knoten for fund in _roher_text(kind, geschuetzt)]

    geschuetzt = geschuetzt or isinstance(knoten, GESCHUETZT)
    funde = _roher_text(getattr(knoten, "children", None), geschuetzt)
    # Auswahlkarten tragen ihren Text in den Optionen, nicht in den Kindern.
    for option in getattr(knoten, "options", None) or []:
        if isinstance(option, dict):
            funde += _roher_text(option.get("label"), geschuetzt)
    return funde


def _mit_auswahl(auswahl: str) -> dict:
    return start_flow.apply(initial_draft_dict(), auswahl)


BEREICHE = [
    pytest.param(lambda: wizard.entry(initial_draft_dict()), id="einstieg"),
    *[
        pytest.param(lambda i=i: wizard.content(initial_draft_dict(), i), id=f"schritt-{step.key}")
        for i, step in enumerate(wizard.STEPS)
    ],
    pytest.param(
        lambda: start_flow.scenario_details(_mit_auswahl(start_flow.STANDARD)), id="standard"
    ),
    pytest.param(lambda: start_flow.scenario_details(_mit_auswahl(start_flow.CUSTOM)), id="eigene"),
    *[
        pytest.param(
            lambda preset_id=preset.id: start_flow.scenario_details(_mit_auswahl(preset_id)),
            id=f"szenario-{preset.id}",
        )
        for preset in list_sweep_presets()
    ],
    pytest.param(lambda: model_editor.body(initial_draft_dict()), id="modell"),
    pytest.param(lambda: launch_page.rail(initial_draft_dict()), id="bedienfeld"),
]


@pytest.mark.parametrize("bauen", BEREICHE)
def test_no_markdown_is_shown_raw(bauen):
    funde = _roher_text(bauen())

    assert not funde, "Markdown steht roh im gerenderten Text:\n  " + "\n  ".join(funde)


def test_the_tree_guard_would_notice_a_relapse():
    """Die Mutationsprobe im Test selbst: roh gezeigtes Markdown wird gefunden."""

    roh = html.Div([html.P("Der **Name** steht unten."), dcc.Markdown("Hier **darf** es.")])

    assert _roher_text(roh) == ["Der **Name** steht unten."]


# --- Jeder Textbaustein entscheidet selbst (P7.1-U1.4) -----------------------

from dashboard.web import components as ui  # noqa: E402

#: Parameter, die Text tragen. Gesucht wird über ihren Namen in jeder
#: öffentlichen Funktion von `components.py` — ein neuer Baustein mit einem
#: Parameter `hint` fällt auf, ohne dass ihn jemand einträgt.
TEXTPARAMETER = {"text", "hint", "subtitle"}

_PROBE = "Ein **fetter** Satz mit `Code`."

#: Jeder Textparameter, der selbst entscheidet — mit einem Aufruf, der ihn füllt.
ENTSCHEIDET_SELBST = {
    ("section", "subtitle"): lambda t: ui.section("Titel", subtitle=t),
    ("page_heading", "subtitle"): lambda t: ui.page_heading("Titel", t),
    ("empty_state", "text"): lambda t: ui.empty_state(t),
    ("empty_state", "hint"): lambda t: ui.empty_state("Leer", hint=t),
    ("kachel", "hint"): lambda t: html.Div(
        [
            ui.kachel("Länge", 40, t),
            ui.kachel("Szenario", "Standard", t, variante="text"),
            ui.kachel("Rate", "0,26", t, variante="kompakt"),
        ]
    ),
    ("status_dot", "hint"): lambda t: ui.status_dot(True, "Bereit", hint=t),
    ("hinweis", "text"): lambda t: ui.hinweis(t, "info"),
    ("lede", "text"): lambda t: ui.lede(t),
    ("explainer", "text"): lambda t: ui.explainer(t),
    ("hint_text", "hint"): lambda t: ui.hint_text(t),
    ("field", "hint"): lambda t: ui.field("Feld", html.Div(), hint=t),
    ("checkbox", "hint"): lambda t: ui.checkbox("Kästchen", value=False, hint=t),
    ("toggle", "hint"): lambda t: ui.toggle("Schalter", value=False, hint=t),
    ("markdown", "text"): lambda t: ui.markdown(t),
    ("satz", "text"): lambda t: ui.satz(t),
}

#: Textparameter, die bewusst **wörtlich** bleiben — je mit Grund.
WOERTLICH = {
    ("log_line", "text"): "Eine Protokollzeile zeigt, was der Lauf geschrieben hat — wörtlich.",
    ("code_block", "text"): "Code wird gezeigt, wie er ist; ein Stern darin ist ein Stern.",
    ("badge", "text"): "Eine Marke aus wenigen Wörtern; Auszeichnung hat darin keinen Platz.",
    ("status_indicator", "text"): "Der Zustand der Anlage kommt aus `status.py`, nie aus Daten.",
    ("status_indicator", "hint"): "Steht im `title`-Attribut, das kein Markdown darstellen kann.",
    ("status_dot", "text"): "Kurzbeschriftung neben einem Zustandspunkt, aus festen Wörtern.",
}

#: Bausteine, die ihren Text bis zum 2026-09-13 wörtlich setzten — für sie gilt
#: zusätzlich: Schlichter Text bleibt das Element, das dort immer stand.
BIS_DAHIN_WOERTLICH = [
    ("section", "subtitle"),
    ("page_heading", "subtitle"),
    ("empty_state", "text"),
    ("empty_state", "hint"),
    ("kachel", "hint"),
    ("status_dot", "hint"),
]


def _textparameter() -> set[tuple[str, str]]:
    gefunden = set()
    for name, funktion in inspect.getmembers(ui, inspect.isfunction):
        if name.startswith("_") or funktion.__module__ != ui.__name__:
            continue
        for parameter in inspect.signature(funktion).parameters:
            if parameter in TEXTPARAMETER:
                gefunden.add((name, parameter))
    return gefunden


class TestJederTextbausteinEntscheidetSelbst:
    """Markdown ist eine Eigenschaft des Textes, nicht die Wahl des Aufrufers (P7.1-U1.4)."""

    def test_every_text_parameter_is_accounted_for(self):
        gefunden = _textparameter()
        eingetragen = set(ENTSCHEIDET_SELBST) | set(WOERTLICH)

        fehlt = sorted(gefunden - eingetragen)
        verwaist = sorted(eingetragen - gefunden)
        assert not fehlt, (
            f"Diese Textparameter sind nirgends eingetragen: {fehlt}. Ein Text entscheidet "
            "selbst (`ui.satz`) — oder bleibt mit Grund in `WOERTLICH`."
        )
        assert not verwaist, f"Eingetragen, aber nicht mehr vorhanden: {verwaist}"

    @pytest.mark.parametrize("ort", sorted(ENTSCHEIDET_SELBST), ids=lambda o: ".".join(o))
    def test_marked_up_text_is_rendered_not_shown(self, ort):
        funde = _roher_text(ENTSCHEIDET_SELBST[ort](_PROBE))

        assert not funde, f"`ui.{ort[0]}({ort[1]}=…)` zeigt Markdown roh: {funde}"

    @pytest.mark.parametrize("ort", BIS_DAHIN_WOERTLICH, ids=lambda o: ".".join(o))
    def test_plain_text_stays_the_element_it_was(self, ort):
        gerendert = str(ENTSCHEIDET_SELBST[ort]("Ein schlichter Satz."))

        assert "Markdown(" not in gerendert, (
            f"`ui.{ort[0]}` macht aus schlichtem Text Markdown — der Baum soll sich "
            "nur ändern, wo der Text es verlangt."
        )

    def test_every_literal_exception_carries_a_reason(self):
        ohne = [ort for ort, grund in WOERTLICH.items() if len(grund.strip()) < 30]

        assert not ohne, f"Ohne Grund: {ohne}"

    def test_the_decision_would_notice_a_relapse(self):
        assert isinstance(ui.satz(_PROBE), dcc.Markdown)
        assert isinstance(ui.satz("Ein [Verweis](https://example.org)."), dcc.Markdown)
        assert isinstance(ui.satz("- Punkt eins\n- Punkt zwei"), dcc.Markdown)
        assert isinstance(ui.satz("Kosten * Menge, ohne Auszeichnung."), html.P)
        assert _roher_text(html.Div(html.P(_PROBE)))
