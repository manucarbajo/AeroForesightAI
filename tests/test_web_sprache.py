"""Die Oberfläche spricht Produktsprache, nicht Entwicklersprache (P7.0-U0.6).

**Der Befund (Q6 des UI/UX-Audits vom 2026-09-11):** Im sichtbaren Text standen
Paketkennungen dieses Projektplans. Unter «Ergebnisse › Szenario» leitete ein
Satz mit «P3 —» ein, und in der Szenario-Auswahl des Assistenten hieß ein
Eintrag «P5.7» — ein im Dashboard gesichertes Experiment, dessen eigene
Begründung sagt, dass es kein begründetes Weltbild ist. Beides ist die Tonlage
des Projektplans, nicht die eines Produkts: Wer «P5.7» liest, sucht danach und
findet nichts, weil die Kennung nur intern etwas bedeutet.

**Was dieser Wächter heute hält, und was noch nicht.** U0.6 verspricht drei
Dinge über den sichtbaren Text: keine Paketkennungen, keine Pfade unter
`configs/` und `outputs/`, keine `snake_case`-Bezeichner außerhalb von
Code-Elementen. **Hier stehen die Paketkennungen.** Die beiden anderen fehlen
noch, und das ist Absicht statt Vergessen: Beide brauchen eigene Ausnahmen, die
erst zu begründen sind — `snake_case` kollidiert mit den Namen der
Symbolschrift, die als Text im Baum stehen (`chevron_right`; siehe
`tests/test_symbolschrift.py`), und mit den Feldnamen des Modells, die erst mit
P7.2-U2.3 Glossarnamen bekommen. Ein Wächter, der diese Fälle pauschal
ausnimmt, wäre eine Aufgabenliste in Testform. **U0.6 ist also nicht fertig,
solange dieser Docstring diesen Absatz trägt.**

**Gemessen wird der gerenderte Baum, nicht der Quelltext.** Eine Kennung kommt
auch aus `configs/` — genau dort saß «P5.7» —, und das sieht kein Syntaxbaum.

**Warum die Muster so schmal sind.** Ein breiteres Muster für «Buchstabe plus
Zahl» würde die Faktorzustände treffen (`F1.1`, `F2.2`), die im Produkt
**richtig** sind, und dazu jede Kabinenklasse oder Segmentkennung, die morgen
«A1» heißt. Gehalten sind deshalb die Formen, die dieses Projekt für seine
eigenen Pakete wirklich benutzt: `P<n>` und `P<n>.<m>` sowie `U`, `W` und `Q`
mit zwei Zahlen. Die Auslassung ist benannt, nicht übersehen: Ein Befund, der
als «B4» oder «K5» in den sichtbaren Text gerät, fällt hier nicht auf.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from dash import dcc, html

from dashboard.config_catalog import list_sweep_presets
from dashboard.web import theme
from dashboard.web.config_editor import start_flow, wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict
from dashboard.web.views import animation, explorer, figures, files, narrative, overview, scenario

#: Kennungen der Arbeitspakete dieses Projekts. Herleitung im Modul-Docstring —
#: `F` fehlt bewusst, das sind die Faktorzustände des Modells.
KENNUNG = re.compile(r"\bP\d+(?:\.\d+)?\b|\b[UWQ]\d+\.\d+\b")

#: Sichtbarer Text, der eine Kennung tragen darf — je Eintrag der Grund.
#:
#: **Leer, und das ist die Aussage.** Eine Ausnahme hier wäre ein Text, in dem
#: die Kennung dem Leser etwas sagt; bisher gibt es keinen. Verfallene Einträge
#: meldet `test_no_exception_outlives_its_reason` — eine Ausnahmeliste, die
#: niemand aufräumt, wächst zur Freigabe für alles.
AUSNAHMEN: dict[str, str] = {}


# --- Sichtbarer Text eines gerenderten Baums ---------------------------------

#: Bausteine, deren Inhalt Code **ist** — dort ist eine Kennung kein Versehen,
#: sondern der Gegenstand.
CODE = (html.Code, html.Pre)


def sichtbarer_text(knoten, in_code: bool = False) -> list[str]:
    """Jede Zeichenkette, die im Browser zu lesen ist.

    Mitgenommen werden auch `options` (Auswahlkarten tragen ihren Text dort,
    nicht in den Kindern) sowie `placeholder` und `title` — ein Platzhalter
    steht im Feld, ein `title` im Tooltip, beides liest jemand.
    """

    if knoten is None:
        return []
    if isinstance(knoten, str):
        return [] if in_code else [knoten]
    if isinstance(knoten, (list, tuple)):
        return [text for kind in knoten for text in sichtbarer_text(kind, in_code)]

    in_code = in_code or isinstance(knoten, CODE)
    texte = sichtbarer_text(getattr(knoten, "children", None), in_code)
    for option in getattr(knoten, "options", None) or []:
        if isinstance(option, dict):
            texte += sichtbarer_text(option.get("label"), in_code)
    if not in_code:
        for feld in ("placeholder", "title"):
            wert = getattr(knoten, feld, None)
            if isinstance(wert, str):
                texte.append(wert)
    return texte


def _kennungen(knoten) -> list[str]:
    """Welche Paketkennungen im sichtbaren Text stehen — mit ihrem Satz."""

    funde: list[str] = []
    for text in sichtbarer_text(knoten):
        if text.strip() in AUSNAHMEN:
            continue
        for treffer in KENNUNG.findall(text):
            # `findall` liefert bei einer Gruppe deren Inhalt — gebraucht ist
            # der ganze Treffer, also noch einmal gezielt suchen.
            gefunden = KENNUNG.search(text)
            marke = gefunden.group(0) if gefunden else treffer
            funde.append(f"«{marke}» in: {' '.join(text.split())[:100]}")
            break
    return funde


# --- Die Bereiche ------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def plotly_vorlagen():
    """Ohne die Vorlagen wirft jede Ansicht mit einem Diagramm."""

    theme.register_template()


@pytest.fixture(scope="module")
def lauf(tmp_path_factory) -> Path:
    """Ein Lauf mit genug Artefakten, dass jede Ansicht ihren Text zeigt."""

    ordner = tmp_path_factory.mktemp("sprache") / "run_sprache"
    (ordner / "timeseries").mkdir(parents=True)
    (ordner / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": 3,
                "ticks_max": 3,
                "total_events": 5,
                "model": "llama3.2",
                "market_enabled": True,
                "timestamp": "2026-09-07T18:25:55.248822+00:00",
                "compute_mode": "llm",
            }
        ),
        encoding="utf-8",
    )
    (ordner / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {"tick": t, "booking_rate": 0.4, "ticket_price": 100.0 + t} for t in (1, 2, 3)
                ]
            }
        ),
        encoding="utf-8",
    )
    (ordner / "price_history.json").write_text(
        json.dumps([{"round_number": t, "price": 100.0 + t} for t in (1, 2, 3)]), encoding="utf-8"
    )
    (ordner / "final_narrative.md").write_text("# Bericht\n\nInhalt.", encoding="utf-8")
    (ordner / "timeseries" / "properties.csv").write_text(
        "tick,carbon_tax_level,income_index\n1,50,1.0\n2,60,1.1\n", encoding="utf-8"
    )
    (ordner / "timeseries" / "factors.csv").write_text(
        "tick,F1,F2\n1,F1.1,F2.1\n2,F1.2,F2.1\n", encoding="utf-8"
    )
    return ordner


def _mit_auswahl(auswahl: str) -> dict:
    return start_flow.apply(initial_draft_dict(), auswahl)


#: Alles, was ohne Browser und ohne echten Lauf zu bauen ist. Die Presets
#: kommen aus `configs/` — ein neues Szenario mit einer Kennung im Namen fällt
#: damit auf, ohne dass es hier einzutragen wäre.
EINRICHTEN = [
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

ANSICHTEN = [overview, scenario, narrative, animation, figures, files, explorer]


@pytest.mark.parametrize("bauen", EINRICHTEN)
def test_no_package_id_is_visible_while_setting_up(bauen):
    funde = _kennungen(bauen())

    assert not funde, (
        "Eine Paketkennung dieses Projektplans steht im sichtbaren Text:\n  "
        + "\n  ".join(funde)
        + "\n\nSie sagt dem Leser nichts — er sucht danach und findet nichts."
    )


@pytest.mark.parametrize("ansicht", ANSICHTEN, ids=lambda v: v.__name__.rsplit(".", 1)[-1])
def test_no_package_id_is_visible_in_the_results(ansicht, lauf):
    funde = _kennungen(ansicht.render(lauf, lauf.name))

    assert (
        not funde
    ), "Eine Paketkennung dieses Projektplans steht im sichtbaren Text:\n  " + "\n  ".join(funde)


# --- Der Wächter über sich selbst --------------------------------------------


def test_the_guard_would_notice_a_relapse():
    """**Ein Wächter, der nie etwas sieht, könnte auch blind sein.**

    Nachgestellt sind beide Wege, auf denen die Kennung hereinkam: als Literal
    in einem Baustein (so stand «P3 —» in der Szenario-Ansicht) und als Wert
    aus einer Datei, der über eine Variable in eine Auswahlkarte gerät (so
    stand «P5.7» in der Szenario-Auswahl).
    """

    aus_dem_quelltext = html.Div(html.P("P3 — Szenarien aus dem Lauf."))
    aus_einer_datei = dcc.RadioItems(options=[{"label": "P5.7", "value": "p5.7"}])

    assert _kennungen(aus_dem_quelltext) == ["«P3» in: P3 — Szenarien aus dem Lauf."]
    assert _kennungen(aus_einer_datei) == ["«P5.7» in: P5.7"]


def test_a_factor_state_is_not_a_package_id():
    """`F1.1` ist ein Zustand des Modells und gehört in die Oberfläche.

    Ohne diese Zusage wäre das naheliegende, breitere Muster «Buchstabe plus
    Zahl Punkt Zahl» verlockend — und es würde die halbe Ergebnis-Ansicht
    melden.
    """

    echt = html.Div([html.P("Faktor F1 steht auf F1.1."), html.Span("F2.2 ab Tick 12")])

    assert _kennungen(echt) == []


def test_code_may_name_a_package():
    """In `html.Code` ist eine Kennung der Gegenstand, nicht ein Versehen."""

    assert _kennungen(html.Code("P7.0-U0.6")) == []


def test_no_exception_outlives_its_reason():
    """Eine Ausnahme, deren Text es nicht mehr gibt, ist eine stille Freigabe.

    Geprüft wird gegen **allen** sichtbaren Text des Einrichtens: Steht der
    ausgenommene Satz nirgends mehr, ist der Eintrag zu löschen. Die
    Mutationsprobe dazu steht in
    `test_the_staleness_check_would_notice_a_dead_exception`.
    """

    vorhanden = {
        " ".join(text.split())
        for param in EINRICHTEN
        for text in sichtbarer_text(param.values[0]())
    }
    tot = [satz for satz in AUSNAHMEN if " ".join(satz.split()) not in vorhanden]

    assert not tot, "Diese Ausnahmen beschreiben Text, den es nicht mehr gibt:\n  " + "\n  ".join(
        f"{satz!r} — {AUSNAHMEN[satz]}" for satz in tot
    )


def test_the_staleness_check_would_notice_a_dead_exception(monkeypatch):
    """Ohne diese Probe wäre die Prüfung über eine leere Liste bedeutungslos."""

    monkeypatch.setitem(AUSNAHMEN, "Diesen Satz zeigt niemand.", "erfunden, für die Probe")

    with pytest.raises(AssertionError, match="Text, den es nicht mehr gibt"):
        test_no_exception_outlives_its_reason()
