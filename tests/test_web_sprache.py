"""Die Oberfläche spricht Produktsprache, nicht Entwicklersprache (P7.0-U0.6).

**Der Befund (Q6 des UI/UX-Audits vom 2026-09-11):** Im sichtbaren Text standen
Paketkennungen dieses Projektplans. Unter «Ergebnisse › Szenario» leitete ein
Satz mit «P3 —» ein, und in der Szenario-Auswahl des Assistenten hieß ein
Eintrag «P5.7» — ein im Dashboard gesichertes Experiment, dessen eigene
Begründung sagt, dass es kein begründetes Weltbild ist. Beides ist die Tonlage
des Projektplans, nicht die eines Produkts: Wer «P5.7» liest, sucht danach und
findet nichts, weil die Kennung nur intern etwas bedeutet.

**Der zweite Befund: Pfade des Servers.** Die Ansicht «Dateien» stellte über
jede Datei deren absoluten Pfad («F:\\AeroForesight\\…\\cib_matrix.json»), fünf
Sätze im Assistenten nannten `configs/` oder `outputs/sweeps/` als Ort, an dem
etwas landet, und in der Begründung dreier Rahmenszenarien stand
«configs/backtest/quellen.json» dort, wo ein **Werk** hingehört. Ein Pfad
beantwortet die Frage «wo finde ich das» mit der Sprache des Servers; das
Produkt kann sie besser beantworten — «danach im ersten Schritt zur Auswahl».

**Was dieser Wächter heute hält, und was noch nicht.** U0.6 verspricht drei
Dinge über den sichtbaren Text: keine Paketkennungen, keine Pfade unter
`configs/` und `outputs/`, keine `snake_case`-Bezeichner außerhalb von
Code-Elementen. **Hier stehen die ersten beiden.** Der dritte fehlt, und das
ist Absicht statt Vergessen: `snake_case` kollidiert mit den Namen der
Symbolschrift, die als Text im Baum stehen (`chevron_right`; siehe
`tests/test_symbolschrift.py`), und mit den Feldnamen des Modells, die erst mit
P7.2-U2.3 Glossarnamen bekommen. Ein Wächter, der diese Fälle pauschal
ausnimmt, wäre eine Aufgabenliste in Testform. **U0.6 ist also nicht fertig,
solange dieser Docstring diesen Absatz trägt.**

**Das Handbuch ist nicht dabei, und zwar begründet.** Dort *ist* die Datei der
Gegenstand: Das Referenzkapitel sagt, welches Feld in welcher Datei unter
`configs/` steht, und genau das braucht jemand, der eine Konfiguration von Hand
schreibt. Eine Regel, die den Ort verbietet, wo er die Information ist, wäre
keine Produktsprache, sondern eine Lücke in der Dokumentation.

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
from dashboard.web.pages import model_editor, muster
from dashboard.web.state import initial_draft_dict
from dashboard.web.views import animation, explorer, figures, files, narrative, overview, scenario

#: Kennungen der Arbeitspakete dieses Projekts. Herleitung im Modul-Docstring —
#: `F` fehlt bewusst, das sind die Faktorzustände des Modells.
KENNUNG = re.compile(r"\bP\d+(?:\.\d+)?\b|\b[UWQ]\d+\.\d+\b")

#: Pfade, die dem Leser nichts sagen: die Verzeichnisse der Installation und
#: jeder absolute Pfad der Maschine, auf der der Server läuft.
#:
#: **`docs/` fehlt bewusst.** Die Quellenangaben der Rahmenszenarien nennen
#: heute Dateien unter `docs/research/` statt der Werke, die darin liegen — ein
#: echter Befund, aber ein anderer: Dort ist die **Zitierweise** falsch, nicht
#: der Ort. Er gehört zu P7.2-U2.3 und braucht für jede Quelle die
#: bibliografische Angabe, die aus einem Dateinamen nicht zu erfinden ist.
#: **Der Laufwerksbuchstabe braucht seine Wortgrenze.** Ohne `\b` traf das
#: Muster das «p:» in «http://127.0.0.1:11434» und meldete jede
#: Adresszeile — gefunden beim ersten scharfen Durchlauf.
PFAD = re.compile(
    r"\b(?:configs|outputs)[/\\][\w/\\.-]*"  # die Verzeichnisse der Installation
    r"|\b[A-Za-z]:[\\/][^\s`'\"]+"  # C:\… und F:\…
    r"|/(?:home|Users|var|tmp)/[^\s`'\"]+"  # /home/…, /Users/…
)

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


def sichtbarer_text(knoten, *, ohne_code: bool = True) -> list[str]:
    """Jede Zeichenkette, die im Browser zu lesen ist.

    Mitgenommen werden auch `options` (Auswahlkarten tragen ihren Text dort,
    nicht in den Kindern) sowie `placeholder` und `title` — ein Platzhalter
    steht im Feld, ein `title` im Tooltip, beides liest jemand.

    `ohne_code=False` nimmt auch den Inhalt von `html.Code` und `html.Pre` mit.
    Gebraucht wird das bei den Pfaden: Eine Kennung in Code-Auszeichnung ist
    der Gegenstand, ein Pfad in Code-Auszeichnung ist derselbe Pfad.
    """

    def gehe(teil, in_code: bool) -> list[str]:
        if teil is None:
            return []
        if isinstance(teil, str):
            return [] if in_code else [teil]
        if isinstance(teil, (list, tuple)):
            return [text for kind in teil for text in gehe(kind, in_code)]

        in_code = in_code or (ohne_code and isinstance(teil, CODE))
        texte = gehe(getattr(teil, "children", None), in_code)
        for option in getattr(teil, "options", None) or []:
            if isinstance(option, dict):
                texte += gehe(option.get("label"), in_code)
        if not in_code:
            for feld in ("placeholder", "title"):
                wert = getattr(teil, feld, None)
                if isinstance(wert, str):
                    texte.append(wert)
        return texte

    return gehe(knoten, False)


def _funde(knoten, muster: re.Pattern[str], *, ohne_code: bool = True) -> list[str]:
    """Wo das Muster im sichtbaren Text zutrifft — je Text mit seinem Satz."""

    funde: list[str] = []
    for text in sichtbarer_text(knoten, ohne_code=ohne_code):
        if text.strip() in AUSNAHMEN:
            continue
        treffer = muster.search(text)
        if treffer:
            funde.append(f"«{treffer.group(0)}» in: {' '.join(text.split())[:100]}")
    return funde


def _kennungen(knoten) -> list[str]:
    """Welche Paketkennungen im sichtbaren Text stehen — mit ihrem Satz."""

    return _funde(knoten, KENNUNG)


def _pfade(knoten) -> list[str]:
    """Welche Pfade im sichtbaren Text stehen — mit ihrem Satz.

    **Ein Codeblock schützt, Backticks in einem Satz nicht**, und die Grenze
    ist gemessen statt gesetzt: Schritt «Lauf & Ablage» zeigt die *effektive
    Konfiguration* als rohes JSON in einem `html.Pre` — dort sind Pfade der
    **Inhalt der Datei** und nicht die Sprache der Oberfläche. «Legt den Stand
    unter `configs/sweeps/` ab» ist der umgekehrte Fall: Die Backticks machen
    aus einem Serverpfad einen ordentlich gesetzten Serverpfad.

    Beim ersten Anlauf stand hier `ohne_code=False` mit der Begründung,
    Backticks dürften nicht schützen. Die Messung hat das widerlegt — sie
    meldete die beiden JSON-Vorschauen mit.
    """

    return _funde(knoten, PFAD)


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
    pytest.param(muster.body, id="musterseite"),
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


@pytest.mark.parametrize("bauen", EINRICHTEN)
def test_no_server_path_is_visible_while_setting_up(bauen):
    funde = _pfade(bauen())

    assert not funde, (
        "Ein Pfad des Servers steht im sichtbaren Text:\n  "
        + "\n  ".join(funde)
        + "\n\nWo etwas landet, sagt man im Produkt («danach im ersten Schritt zur "
        "Auswahl»), nicht im Dateisystem."
    )


@pytest.mark.parametrize("ansicht", ANSICHTEN, ids=lambda v: v.__name__.rsplit(".", 1)[-1])
def test_no_package_id_is_visible_in_the_results(ansicht, lauf):
    funde = _kennungen(ansicht.render(lauf, lauf.name))

    assert (
        not funde
    ), "Eine Paketkennung dieses Projektplans steht im sichtbaren Text:\n  " + "\n  ".join(funde)


@pytest.mark.parametrize("ansicht", ANSICHTEN, ids=lambda v: v.__name__.rsplit(".", 1)[-1])
def test_no_server_path_is_visible_in_the_results(ansicht, lauf):
    """**Die Ansicht «Dateien» ist der Anlass**, und sie ist kein Sonderfall.

    Sie zeigte über jeder Datei deren absoluten Pfad. Daran ist für den Leser
    genau ein Teil brauchbar, der Name der Datei; der Rest beschreibt die
    Maschine, auf der der Server läuft, und gehört in einem Mehrbenutzerbetrieb
    ohnehin niemandem außer ihr.
    """

    funde = _pfade(ansicht.render(lauf, lauf.name))

    assert not funde, "Ein Pfad des Servers steht im sichtbaren Text:\n  " + "\n  ".join(funde)


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


def test_the_path_guard_would_notice_a_relapse():
    """Nachgestellt sind die drei Formen, die vorkamen.

    Der absolute Pfad über einer Datei («Dateien»), das Verzeichnis in einem
    erklärenden Satz (fünf Stellen im Assistenten) und der Pfad als
    Quellenangabe — «configs/backtest/quellen.json» stand in der Begründung
    dreier Rahmenszenarien dort, wo ein Werk hingehört.
    """

    absolut = html.P(r"F:\AeroForesight\outputs\run_20260907\cib_matrix.json")
    im_satz = html.P("Legt den aktuellen Stand unter `configs/sweeps/` ab.")
    als_quelle = html.Li("configs/backtest/quellen.json — EEX-Auktionspreise und Brent")

    assert _pfade(absolut), "der absolute Pfad fällt nicht auf"
    assert _pfade(im_satz), "das Verzeichnis im Satz fällt nicht auf"
    assert _pfade(als_quelle), "der Pfad als Quellenangabe fällt nicht auf"


def test_a_file_preview_may_contain_paths():
    """**Die eine bewusste Ausnahme, und sie ist gemessen.**

    Schritt «Lauf & Ablage» zeigt die effektive Konfiguration als rohes JSON.
    Was dort an Pfaden steht, ist der **Inhalt der Datei** — ihn zu melden
    hieße, dem Wächter beizubringen, dass eine Dateivorschau keine Dateien
    zeigen darf. Der erste Anlauf dieses Wächters tat genau das und meldete
    zwei JSON-Vorschauen.

    Die Grenze verläuft zwischen Codeblock und Satz: `html.Pre` und `html.Code`
    sind geschützt, Backticks in einem Satz nicht.
    """

    vorschau = html.Pre('{ "sweeps": "configs/sweeps/business_as_usual.json" }')
    satz = html.P("Der Lauf liest die Dateien unter `configs/`.")

    assert _pfade(vorschau) == []
    assert _pfade(satz), "ein Satz mit Backticks ist kein Codeblock"


def test_a_url_is_not_a_windows_path():
    """`http://127.0.0.1:11434` hat kein Laufwerk — der erste Anlauf sah eines.

    Ohne Wortgrenze traf das Muster für «C:\\…» das «p:» in «http:» und meldete
    jede Adresszeile der Technik-Einstellungen.
    """

    assert _pfade(html.P("Adresse: http://127.0.0.1:11434")) == []
    assert _pfade(html.P(r"Datei: C:\Users\Haiko\run.json")), "ein echtes Laufwerk fehlt"


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
