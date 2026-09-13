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

from pathlib import Path

from dash import ALL, Input, Output, State, ctx, dcc, html, no_update

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


def run_options() -> tuple[list[dict], dict[str, RunSummary]]:
    """Einträge der Lauf-Auswahl plus Nachschlagetabelle `run_id → RunSummary`."""

    runs = list_runs()
    options = [
        {
            "label": f"{run.run_id} — {run.scenario_title}" if run.scenario_title else run.run_id,
            "value": run.run_id,
        }
        for run in runs
    ]
    return options, {run.run_id: run for run in runs}


def default_selection() -> dict | None:
    """Vorauswahl für den Store: der jüngste Run, sofern es einen gibt."""

    runs = list_runs()
    if not runs:
        return None
    return {"run_id": runs[0].run_id, "run_dir": str(runs[0].run_dir)}


def degraded_banner(summary: RunSummary) -> html.Div | None:
    """Warnung über allen Ansichten, wenn das Sprachmodell während des Laufs ausfiel.

    Steht bewusst hier und nicht in einer der sieben Ansichten: Die Einschränkung
    betrifft jede von ihnen, und wer direkt in «Figures» einsteigt, soll sie
    genauso sehen wie jemand, der bei «Szenario» anfängt.
    """

    if not summary.degraded:
        return None

    count = summary.llm_incident_count
    calls = "ein Aufruf" if count == 1 else f"{count} Aufrufe"
    return ui.hinweis(
        f"**Dieser Lauf ist beeinträchtigt.** {calls} an das Sprachmodell blieben "
        "unbeantwortet. Die gerechneten Zahlen sind davon unberührt — Preise, "
        "Buchungsraten und Faktorzustände kommen aus Python. Fehlen können "
        "Beiträge der Akteure und Teile der Deutung. Einzelheiten in "
        "`llm_incidents.json` unter «Dateien».",
        "warnung",
        class_name="mb-3",
    )


#: Alter Name, von `test_web_layout.py` benutzt.
_degraded_banner = degraded_banner


def _meta(summary: RunSummary) -> html.Div:
    preview = (
        summary.scenario_summary
        or "Keine Szenario-Vorschau — der Lauf hat keine `run_scenario.json`."
    )
    return html.Div(
        [
            html.P(
                f"{formate.zeitpunkt(summary.timestamp)} · "
                f"{summary.ticks_completed or '?'} Ticks · "
                f"Modell {summary.model or '—'}",
                className=f"{ui.CAPTION} mb-2",
            ),
            degraded_banner(summary),
            ui.hinweis(preview, "info"),
        ]
    )


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
                    html.Div(_meta(summary) if summary else None, id="runs-meta", className="mb-4"),
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
        Input("selected-run-store", "data"),
    )
    def _meta_for(selected: dict | None):
        if not selected:
            return None
        _, by_id = run_options()
        summary = by_id.get(selected.get("run_id"))
        if summary is None:
            return ui.hinweis("Lauf nicht mehr vorhanden.", "warnung")
        return _meta(summary)

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
