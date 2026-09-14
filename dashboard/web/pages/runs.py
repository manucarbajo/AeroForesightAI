"""Der Viewport im Bereich «Ergebnisse»: die sieben Ansichten eines Laufs.

Die Seite hält nur den Rahmen; jede Ansicht liegt als eigenes Modul unter
`dashboard/web/views/`. Der zuerst sichtbare Tab wird schon beim Aufbau
gerendert — dadurch braucht kein Callback beim ersten Laden zu feuern, und
keiner zeigt auf eine Komponente, die es noch nicht gibt.

**Was der Leitstand geändert hat:** Die Lauf-Auswahl steht nicht mehr hier,
sondern in der Kopfzeile (`shell.RUN_SELECT`) — sie gilt für alle drei Zonen,
nicht nur für diesen Bereich. Aus der Tab-Leiste ist eine Werkzeugleiste
geworden, die beim Scrollen des Viewports stehen bleibt.
"""

from __future__ import annotations

import re
from pathlib import Path

from dash import ALL, Input, Output, State, ctx, dcc, html, no_update

from dashboard.config_catalog import load_config_file
from dashboard.run_browser import RunSummary, list_runs
from dashboard.web import components as ui
from dashboard.web import formate, theme
from dashboard.web.views import (
    animation,
    explorer,
    figures,
    files,
    narrative,
    overview,
    scenario,
)
from src.reporting.output_writer.provenance import COMPUTE_MODE_LABELS

TABS = [
    ("Szenario", "scenario"),
    ("Übersicht", "overview"),
    ("Animation", "animation"),
    ("Diagramme", "figures"),
    ("Bericht", "narrative"),
    ("Abfrage", "explorer"),
    ("Dateien", "files"),
]

DEFAULT_TAB = "scenario"

TAB_STORE = "runs-tab-store"

_RENDERERS = {
    "scenario": scenario.render,
    "overview": overview.render,
    "animation": animation.render,
    "figures": figures.render,
    "narrative": narrative.render,
    "files": files.render,
}

#: Welche Ansichten ihre Farben aus dem Theme beziehen und deshalb neu gebaut
#: werden müssen, wenn jemand umschaltet. Der Rest ist reiner Text und Markup;
#: dessen Farben kommen aus dem Stylesheet und folgen von selbst.
_THEMED = {"overview", "figures", "animation", "files", "scenario"}


#: Wie ein Lauf ohne festgehaltenen Rahmen heißt — derselbe Wortlaut wie in der
#: Übersicht, damit Auswahl und Ansicht dasselbe sagen.
OHNE_RAHMEN = "Rahmen nicht festgehalten"

#: Eine Wiederholung eines Mehrfach-Laufs: `batch_…/run_002`.
_WIEDERHOLUNG = re.compile("^batch_[^/]+/run_0*([0-9]+)$")


def _vorgabename() -> str:
    """Der Name, mit dem der Assistent jeden Entwurf vorbelegt — kein vergebener."""

    return str(load_config_file("simulation_config.json").get("name", ""))


def lauf_bezeichnung(summary: RunSummary, *, vorgabe: str | None = None) -> str:
    """Wie ein Lauf in der Auswahl heißt: **Name · Rahmen · Datum** (D6, P7.3-U3.3).

    **Die Kennung steht nicht darin** — sie ist ein Ablageort und steht unter
    «Technische Details» der Übersicht. Bis dahin hieß ein Lauf «Kennung — Titel»,
    und 179 von 190 Läufen trugen denselben Titel «Trend-Fortsetzung».

    **Der Vorgabename zählt nicht als Name:** Der Assistent belegt jeden Entwurf
    damit vor, und `run_metadata.json` hält ihn fest — vorn stünde sonst bei
    jedem Lauf dasselbe Wort. Dieselbe Regel wie in
    `config_catalog.build_custom_sweep_from_draft`. **Wiederholungen eines
    Mehrfach-Laufs** entstehen zur selben Minute und tragen deshalb ihre Nummer.
    """

    vorgabe = _vorgabename() if vorgabe is None else vorgabe
    teile = []
    if summary.simulation_name and summary.simulation_name != vorgabe:
        teile.append(summary.simulation_name)
    teile.append(summary.rahmen_name or OHNE_RAHMEN)
    teile.append(formate.zeitpunkt(summary.timestamp))
    wiederholung = _WIEDERHOLUNG.match(summary.run_id)
    if wiederholung:
        teile.append(f"Wiederholung {int(wiederholung.group(1))}")
    return " · ".join(teile)


def run_options() -> tuple[list[dict], dict[str, RunSummary]]:
    """Einträge der Lauf-Auswahl plus Nachschlagetabelle `run_id → RunSummary`."""

    runs = list_runs()
    vorgabe = _vorgabename()
    options = [
        {"label": lauf_bezeichnung(run, vorgabe=vorgabe), "value": run.run_id} for run in runs
    ]
    return options, {run.run_id: run for run in runs}


def default_selection() -> dict | None:
    """Vorauswahl für den Store: der jüngste Run, sofern es einen gibt."""

    runs = list_runs()
    if not runs:
        return None
    return {"run_id": runs[0].run_id, "run_dir": str(runs[0].run_dir)}


#: Der Wirt des Lauf-Kopfs im Leitstand. Er steht in `app.py`, gefüllt wird er
#: hier — vom selben Callback wie der Kopf unter «Ergebnisse».
LAUF_KOPF_LEITSTAND = "leitstand-lauf-kopf"


def lauf_kopf(summary: RunSummary) -> html.Div:
    """Der Kopf eines Laufs — **einmal, kompakt**, im Leitstand und in «Ergebnisse» (P7.3-U3.2).

    Eine Zeile sagt, welcher Lauf das ist und womit er gerechnet wurde: Name ·
    Rahmen · Datum, dann Rechenmodus und Ticks. Bis dahin standen unter
    «Ergebnisse» Datum, Ticks und Modell über einem Warnbanner und der
    Zusammenfassung des Szenarios — über jeder der sieben Ansichten, und die
    Zusammenfassung stand in «Szenario» ein zweites Mal (R1). Im Leitstand stand
    der Name des gezeigten Laufs nirgends (Q5).

    **Ein beeinträchtigter Lauf bleibt auf den ersten Blick einer** (Invariante 1):
    Die Warnung steht sichtbar darunter; nur die Erklärung, was sie heißt, liegt in
    einer Klappe — zweitrangig ist die Erklärung, nicht die Warnung. Das Banner
    stand bewusst über allen Ansichten und nicht in einer: Wer direkt in
    «Diagramme» einsteigt, soll es genauso sehen wie jemand, der bei «Szenario»
    anfängt. Das gilt für den Kopf weiter.
    """

    modus = COMPUTE_MODE_LABELS.get(summary.compute_mode or "", "Rechenmodus nicht festgehalten")
    teile = [lauf_bezeichnung(summary), modus]
    if summary.ticks_completed is not None:
        teile.append(formate.ticks_mit_modellzeit(summary.ticks_completed))
    kinder: list = [html.P(" · ".join(teile), className=f"{ui.BESCHRIFTUNG} af-text-muted")]
    if summary.degraded:
        count = summary.llm_incident_count
        calls = "ein Aufruf" if count == 1 else f"{count} Aufrufe"
        kinder.append(
            ui.hinweis(
                f"**Dieser Lauf ist beeinträchtigt:** {calls} an das Sprachmodell blieben "
                "unbeantwortet.",
                "warnung",
                class_name="mt-2",
            )
        )
        kinder.append(
            ui.expert(
                ui.satz(
                    "Die Zahlen sind unberührt — sie kommen aus Python. Fehlen können "
                    "Beiträge der Akteure und Teile der Deutung; Einzelheiten in "
                    "`llm_incidents.json` unter «Dateien»."
                ),
                title="Was das heißt",
            )
        )
    return html.Div(kinder)


def viewbar(active: str) -> html.Div:
    """Die Werkzeugleiste über dem Viewport.

    Keine `dcc.Tabs`: Die bringt einen eigenen Rahmen mit, den sie beim Scrollen
    nicht behält. Hier sind es Schaltflächen plus ein Store — dieselbe Wirkung,
    aber die Leiste bleibt oben stehen, während der Inhalt darunter läuft.
    """

    return html.Div(
        [
            html.Button(
                label,
                id={"type": "runs-viewbar", "tab": value},
                className=(
                    "af-viewbar__item af-viewbar__item--active"
                    if value == active
                    else "af-viewbar__item"
                ),
                n_clicks=0,
            )
            for label, value in TABS
        ],
        className="af-viewbar",
        id="runs-viewbar",
    )


def render_tab(tab: str, selected: dict, messages: dict | None = None, mode: str = theme.LIGHT):
    """Eine Ansicht rendern. Wird beim Seitenaufbau und im Callback genutzt."""

    run_dir = Path(selected["run_dir"])
    run_id = selected["run_id"]
    if not run_dir.is_dir():
        return ui.hinweis(f"Laufverzeichnis fehlt: {run_dir}", "fehler")
    try:
        if tab == "explorer":
            history = (messages or {}).get(run_id) or []
            return explorer.render(run_dir, run_id, messages=history, mode=mode)
        renderer = _RENDERERS.get(tab, scenario.render)
        if tab in _THEMED:
            return renderer(run_dir, run_id, mode=mode)
        return renderer(run_dir, run_id)
    except Exception as exc:  # noqa: BLE001 - unvollständige Runs dürfen die Seite nicht killen
        return ui.hinweis(f"Ansicht konnte nicht gerendert werden: {exc}", "fehler")


def layout(selection: dict | None = None) -> html.Div:
    """Rahmen des Bereichs — auch dann vollständig, wenn es noch keinen Run gibt.

    Der leere Zustand behält die Werkzeugleiste bei (nur ohne Inhalt), damit der
    erste fertige Lauf sie per Callback füllen kann. Würde der Bereich im
    Leerfall abgekürzt, zeigten diese Callbacks auf Komponenten, die es nicht
    gibt.
    """

    options, by_id = run_options()
    selection = selection or default_selection()
    run_id = (selection or {}).get("run_id") or (options[0]["value"] if options else None)
    summary = by_id.get(run_id) if run_id else None

    empty = ui.empty_state(
        "Noch keine Läufe vorhanden.",
        hint="Richten Sie unter «Einrichten» einen Lauf ein — nach dem Start erscheint er hier.",
        icon_name="science",
    )

    return html.Div(
        [
            viewbar(DEFAULT_TAB),
            html.Div(
                [
                    html.Div(
                        lauf_kopf(summary) if summary else None, id="runs-meta", className="mb-4"
                    ),
                    # **Der Wirt liegt in einer Ladeanzeige** (P7.0-U0.5).
                    # Ohne sie stand beim Wechsel der Ansicht bis zu acht
                    # Sekunden der Inhalt der *vorigen* unter dem bereits
                    # markierten Reiter — gemessen an «Animation», die auf einem
                    # echten Lauf 8,5 s braucht und 9,1 MiB schickt, während
                    # jede andere Ansicht unter 90 ms bleibt.
                    #
                    # **Sie muss hier stehen und nicht in der Ansicht.**
                    # `dcc.Loading` zeigt sich, solange ein Callback etwas
                    # *innerhalb* von ihm füllt; der Wirt bleibt beim Wechsel
                    # im Baum, die Ansicht darin wird ausgetauscht. In eine
                    # Ansicht gelegt käme die Anzeige erst mit der Antwort, auf
                    # die sie warten soll. Drei Ansichten haben zusätzlich eine
                    # eigene für ihre inneren Callbacks (Szenario, Abfrage,
                    # PNG-Galerie) — die bleiben, sie beantworten eine andere
                    # Frage.
                    # **Ohne `color=`, anders als die drei Ansichten mit
                    # eigener Anzeige.** Die färben ihren Punkt über
                    # `theme.palette(mode)["accent"]` und werden bei jedem
                    # Themenwechsel neu gezeichnet; `layout()` läuft einmal beim
                    # Start. Ein Farbwert von hier wäre für immer der des
                    # Startdesigns — im dunklen Modus das dunkle Navy auf
                    # dunklem Grund. Die Farbe kommt deshalb aus dem
                    # Stylesheet (`.af-ladeanzeige`, Regel 4).
                    dcc.Loading(
                        html.Div(
                            render_tab(DEFAULT_TAB, selection) if selection else empty,
                            id="runs-tab-content",
                        ),
                        type="dot",
                        className="af-ladeanzeige",
                        delay_show=ui.LADEANZEIGE_NACH_MS,
                    ),
                ],
                className="af-pane",
            ),
        ]
    )


def register_callbacks(app) -> None:
    scenario.register_callbacks(app)
    figures.register_callbacks(app)
    files.register_callbacks(app)
    explorer.register_callbacks(app)

    @app.callback(
        Output("runs-meta", "children"),
        Output(LAUF_KOPF_LEITSTAND, "children"),
        Input("selected-run-store", "data"),
    )
    def _lauf_kopf_fuer(selected: dict | None):
        # **Ein Callback für beide Köpfe** (P7.3-U3.2): derselbe Auslöser, dieselbe
        # Rechnung — ein zweiter Callback wäre ein zweiter Rundlauf je Laufwechsel (P7.11).
        if not selected:
            return None, None
        _, by_id = run_options()
        summary = by_id.get(selected.get("run_id"))
        if summary is None:
            return (ui.hinweis("Lauf nicht mehr vorhanden.", "warnung"),) * 2
        return lauf_kopf(summary), lauf_kopf(summary)

    @app.callback(
        Output(TAB_STORE, "data"),
        Output("runs-viewbar", "children"),
        Input({"type": "runs-viewbar", "tab": ALL}, "n_clicks"),
        State(TAB_STORE, "data"),
        prevent_initial_call=True,
    )
    def _switch(_clicks, current: str | None):
        trigger = ctx.triggered_id
        if not isinstance(trigger, dict):
            return no_update, no_update
        tab = str(trigger.get("tab") or DEFAULT_TAB)
        if tab == (current or DEFAULT_TAB):
            return no_update, no_update
        return tab, viewbar(tab).children

    @app.callback(
        Output("runs-tab-content", "children"),
        Input("selected-run-store", "data"),
        Input(TAB_STORE, "data"),
        Input("theme-store", "data"),
        State("explorer-messages-store", "data"),
    )
    def _render_tab(
        selected: dict | None, tab: str | None, mode: str | None, messages: dict | None
    ):
        if not selected:
            return no_update
        return render_tab(tab or DEFAULT_TAB, selected, messages, theme.normalise(mode))
