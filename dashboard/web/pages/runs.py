"""Seite «Ergebnisse ansehen»: Run auswählen und durch die sieben Tabs gehen.

Die Seite hält nur die Auswahl und den Rahmen; jeder Tab liegt als eigenes
Modul unter `dashboard/web/views/`. Der zuerst sichtbare Tab wird schon beim
Aufbau der Seite gerendert — dadurch braucht kein Callback beim ersten Laden
zu feuern, und keiner zeigt auf eine Komponente, die es noch nicht gibt.
"""

from __future__ import annotations

from pathlib import Path

from dash import Input, Output, State, dcc, html, no_update

from dashboard.run_browser import RunSummary, list_runs
from dashboard.web import components as ui
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
    ("Figures", "figures"),
    ("Bericht", "narrative"),
    ("Abfrage", "explorer"),
    ("Dateien", "files"),
]

DEFAULT_TAB = "scenario"

_HIDDEN = {"display": "none"}
#: Leer statt "block": die Auswahlzeile bezieht ihr `display` aus der
#: Tailwind-Klasse `flex` — ein Inline-Wert würde sie überschreiben.
_VISIBLE: dict = {}

_RENDERERS = {
    "scenario": scenario.render,
    "overview": overview.render,
    "animation": animation.render,
    "figures": figures.render,
    "narrative": narrative.render,
    "files": files.render,
}


def run_options() -> tuple[list[dict], dict[str, RunSummary]]:
    """Dropdown-Einträge plus Nachschlagetabelle `run_id → RunSummary`."""

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


def _degraded_banner(summary: RunSummary) -> html.Div | None:
    """Warnung über allen Tabs, wenn das Sprachmodell während des Laufs ausfiel.

    Steht bewusst hier und nicht in einer der sieben Ansichten: Die Einschränkung
    betrifft jede von ihnen, und wer direkt in «Figures» einsteigt, soll sie
    genauso sehen wie jemand, der bei «Szenario» anfängt.
    """

    if not summary.degraded:
        return None

    count = summary.llm_incident_count
    calls = "ein Aufruf" if count == 1 else f"{count} Aufrufe"
    return ui.alert(
        f"**Dieser Lauf ist beeinträchtigt.** {calls} an das Sprachmodell blieben "
        "unbeantwortet. Die gerechneten Zahlen sind davon unberührt — Preise, "
        "Buchungsraten und Faktorzustände kommen aus Python. Fehlen können "
        "Beiträge der Akteure und Teile der Deutung. Einzelheiten in "
        "`llm_incidents.json` unter «Dateien».",
        "warning",
        class_name="mb-3",
    )


def _meta(summary: RunSummary) -> html.Div:
    preview = summary.scenario_summary or "Kein Szenario-Preview — Run ohne `run_scenario.json`."
    return html.Div(
        [
            html.P(
                f"{summary.timestamp or '—'} · "
                f"{summary.ticks_completed or '?'} Ticks · "
                f"Modell {summary.model or '—'}",
                className=f"{ui.CAPTION} mb-2",
            ),
            _degraded_banner(summary),
            ui.alert(preview, "info"),
        ]
    )


def render_tab(tab: str, selected: dict, messages: dict | None = None):
    """Einen Tab rendern. Wird sowohl beim Seitenaufbau als auch im Callback genutzt."""

    run_dir = Path(selected["run_dir"])
    run_id = selected["run_id"]
    if not run_dir.is_dir():
        return ui.alert(f"Run-Verzeichnis fehlt: {run_dir}", "error")
    try:
        if tab == "explorer":
            history = (messages or {}).get(run_id) or []
            return explorer.render(run_dir, run_id, messages=history)
        return _RENDERERS.get(tab, scenario.render)(run_dir, run_id)
    except Exception as exc:  # noqa: BLE001 - unvollständige Runs dürfen die Seite nicht killen
        return ui.alert(f"Ansicht konnte nicht gerendert werden: {exc}", "error")


def layout(selection: dict | None = None) -> html.Div:
    """Rahmen der Seite — auch dann vollständig, wenn es noch keinen Run gibt.

    Der leere Zustand behält Auswahlfeld und Tab-Leiste bei (nur ohne
    Einträge), damit der erste fertige Lauf die Liste per Callback nachziehen
    kann. Würde die Seite im Leerfall abgekürzt, zeigte dieser Callback auf
    Komponenten, die es nicht gibt.
    """

    options, by_id = run_options()
    selection = selection or default_selection()
    run_id = (selection or {}).get("run_id") or (options[0]["value"] if options else None)
    summary = by_id.get(run_id) if run_id else None

    empty = ui.empty_state(
        "Noch keine Runs vorhanden.",
        hint="Starten Sie unter «Simulation starten» einen Lauf — danach erscheint er hier.",
        icon_name="science",
    )

    return html.Div(
        [
            ui.page_heading("Ergebnisse ansehen"),
            html.Div(
                [
                    ui.field(
                        "Run",
                        dcc.Dropdown(
                            id="runs-select",
                            options=options,
                            value=run_id,
                            clearable=False,
                            className="af-dropdown",
                        ),
                        class_name="flex-1 min-w-[20rem]",
                    ),
                    html.Div(
                        ui.button(
                            "Liste neu laden",
                            id="runs-reload",
                            variant="secondary",
                            icon_name="refresh",
                        ),
                        className="pt-7",
                    ),
                ],
                className="flex items-start gap-4 flex-wrap mb-4",
                id="runs-select-row",
                style=_VISIBLE if options else _HIDDEN,
            ),
            html.Div(_meta(summary) if summary else None, id="runs-meta", className="mb-6"),
            html.Div(
                ui.tabs("runs-tabs", TABS, value=DEFAULT_TAB),
                id="runs-tabs-host",
                style=_VISIBLE if options else _HIDDEN,
            ),
            dcc.Loading(
                html.Div(
                    render_tab(DEFAULT_TAB, selection) if selection else empty,
                    id="runs-tab-content",
                ),
                type="dot",
                color="#1E3A5F",
                className="af-spinner-host",
            ),
        ]
    )


def register_callbacks(app) -> None:
    scenario.register_callbacks(app)
    figures.register_callbacks(app)
    files.register_callbacks(app)
    explorer.register_callbacks(app)

    @app.callback(
        Output("runs-select", "options"),
        Output("runs-select", "value"),
        Output("runs-select-row", "style"),
        Output("runs-tabs-host", "style"),
        Input("runs-reload", "n_clicks"),
        Input("last-launched-run-store", "data"),
        State("runs-select", "value"),
        prevent_initial_call=True,
    )
    def _reload(n_clicks: int | None, last_launched: str | None, current: str | None):
        """Liste aktualisieren — manuell oder nachdem ein Lauf fertig geworden ist."""

        from dash import ctx

        options, _ = run_options()
        values = [option["value"] for option in options]
        style = _VISIBLE if values else _HIDDEN

        if ctx.triggered_id == "last-launched-run-store" and last_launched in values:
            return options, last_launched, style, style
        chosen = current if current in values else (values[0] if values else None)
        return options, chosen, style, style

    @app.callback(
        Output("selected-run-store", "data"),
        Output("runs-meta", "children"),
        Input("runs-select", "value"),
        prevent_initial_call=True,
    )
    def _select_run(run_id: str | None):
        if not run_id:
            return no_update, no_update
        _, by_id = run_options()
        summary = by_id.get(run_id)
        if summary is None:
            return no_update, ui.alert("Run nicht mehr vorhanden.", "warning")
        return {"run_id": run_id, "run_dir": str(summary.run_dir)}, _meta(summary)

    @app.callback(
        Output("runs-tab-content", "children"),
        Input("selected-run-store", "data"),
        Input("runs-tabs", "value"),
        State("explorer-messages-store", "data"),
        prevent_initial_call=True,
    )
    def _render_tab(selected: dict | None, tab: str | None, messages: dict | None):
        if not selected:
            return no_update
        return render_tab(tab or DEFAULT_TAB, selected, messages)
