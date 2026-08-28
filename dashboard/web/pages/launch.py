"""Seite «Simulation starten»: geführter Ablauf, Start mit Live-Log, Editor dahinter.

Die Reihenfolge ist die Aussage der Seite (P1.1): Erst die drei Entscheidungen,
die bis zum Start genügen, dann der Start selbst, und erst danach — zugeklappt —
die rund sechzig Felder für den Fall, dass eine bestimmte Annahme geprüft werden
soll. Bis P1.1 stand der Editor vorn und der Start am Ende einer langen Seite.
"""

from __future__ import annotations

from dash import Input, Output, State, dcc, html, no_update

from dashboard.config_catalog import validate_draft
from dashboard.web import components as ui
from dashboard.web import config_editor, runner
from dashboard.web.state import STORE_ID, draft_from_dict, initial_draft_dict

#: Abstand, in dem das Log nachgezogen wird. Kürzer wirkt hektisch und erzeugt
#: nur Last; länger lässt den Lauf tot wirken.
POLL_INTERVAL_MS = 1000


def _summary(draft: dict) -> str:
    runs = int(draft.get("run_count") or 1)
    run_label = f"{runs} Läufe" if runs > 1 else "1 Lauf"
    if draft.get("run_all_sweeps"):
        run_label = "alle Szenario-Presets"
    return (
        f"Szenario: {draft.get('scenario_mode', 'basis')} · "
        f"Ticks: {draft.get('rounds', '?')} · {run_label}"
    )


def layout(draft: dict | None = None) -> html.Div:
    draft = draft or initial_draft_dict()
    return html.Div(
        [
            ui.page_heading(
                "Simulation starten",
                "Drei Entscheidungen genügen: was gerechnet wird, wie weit, und womit.",
            ),
            dcc.Store(id="cfg-editor-refresh", data=0),
            dcc.Store(id="run-job-store"),
            dcc.Interval(id="run-poll", interval=POLL_INTERVAL_MS, disabled=True),
            config_editor.start_layout(draft),
            html.Div(
                [
                    ui.button("Start", id="run-start", icon_name="play_arrow"),
                    html.P(_summary(draft), id="run-summary", className=ui.CAPTION),
                ],
                className="flex items-center gap-4 flex-wrap mb-4",
            ),
            html.Div(id="run-status"),
            html.Div(id="run-log-host", className="mt-4"),
            ui.divider("my-8"),
            ui.accordion(
                "Alle Einstellungen",
                config_editor.layout(draft),
                badge=f"{len(config_editor.TABS)} Bereiche",
            ),
        ]
    )


def _log_view(lines: list[str]) -> html.Div:
    return html.Div(
        [
            html.P("Fortschritt", className=f"{ui.CAPTION} mb-2"),
            html.Pre("\n".join(lines) or "Starte …", className="af-log"),
        ]
    )


def _result_message(result) -> html.Div:
    """Die drei Ausgänge eines Laufs: Sweep-Batch, Multi-Run, Einzellauf."""

    if result.sweep_batch:
        children = [ui.alert("Szenario-Vergleich abgeschlossen.", "success")]
        if result.sweep_summary_path:
            children.append(
                html.P(
                    ["Summary: ", html.Code(str(result.sweep_summary_path))],
                    className=f"{ui.CAPTION} mt-2",
                )
            )
        if result.child_run_ids:
            children.append(
                ui.alert(
                    "Einzelne Sweep-Runs unter **Ergebnisse ansehen** wählen: "
                    + ", ".join(f"`{run_id}`" for run_id in result.child_run_ids),
                    "info",
                    class_name="mt-2",
                )
            )
        else:
            children.append(ui.json_view(result.artifacts))
        return html.Div(children)

    if result.multi_run_batch:
        return html.Div(
            [
                ui.alert(
                    f"Multi-Run `{result.batch_id}` — {len(result.child_run_ids)} Läufe, "
                    f"je {result.ticks_completed} Ticks, {result.total_events} Events gesamt.",
                    "success",
                ),
                html.P(
                    "Einzelne Läufe unter «Ergebnisse ansehen»: "
                    + ", ".join(str(run_id) for run_id in result.child_run_ids),
                    className=f"{ui.CAPTION} mt-2",
                ),
            ]
        )

    return html.Div(
        [
            ui.alert(
                f"Run `{result.run_id}` — {result.ticks_completed} Ticks, "
                f"{result.total_events} Events.",
                "success",
            ),
            html.P(
                "Tab «Szenario» unter «Ergebnisse ansehen» — erste Lesart nach dem Lauf.",
                className=f"{ui.CAPTION} mt-2",
            ),
        ]
    )


def register_callbacks(app) -> None:
    config_editor.register_callbacks(app)

    @app.callback(
        Output("run-summary", "children"),
        Input(STORE_ID, "data"),
    )
    def _update_summary(draft: dict | None):
        return _summary(draft or {})

    @app.callback(
        Output("run-job-store", "data"),
        Output("run-poll", "disabled"),
        Output("run-status", "children"),
        Output("run-log-host", "children"),
        Output("run-start", "disabled"),
        Input("run-start", "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _start(n_clicks: int | None, draft: dict | None):
        if not n_clicks:
            return no_update, no_update, no_update, no_update, no_update

        # Vor dem Start prüfen, nicht danach: Ohne das läuft eine kaputte Config
        # an und scheitert irgendwo im ersten Tick — ein negativer Seed etwa mit
        # «expected non-negative integer» aus numpy, ohne Bezug zum Seed.
        config_errors = validate_draft(draft_from_dict(draft or {}))
        if config_errors:
            return (
                no_update,
                no_update,
                ui.alert(
                    "**Lauf nicht gestartet — die Konfiguration hat Fehler:**\n\n"
                    + "\n".join(f"- {error}" for error in config_errors),
                    "error",
                ),
                no_update,
                False,
            )

        try:
            job_id = runner.start(draft or {})
        except Exception as exc:  # noqa: BLE001 - «läuft schon» ist ein normaler Fall
            return no_update, no_update, ui.alert(str(exc), "warning"), no_update, False
        return job_id, False, ui.alert("Lauf aktiv …", "info"), _log_view([]), True

    @app.callback(
        Output("run-status", "children", allow_duplicate=True),
        Output("run-log-host", "children", allow_duplicate=True),
        Output("run-poll", "disabled", allow_duplicate=True),
        Output("run-start", "disabled", allow_duplicate=True),
        Output("last-launched-run-store", "data"),
        Input("run-poll", "n_intervals"),
        State("run-job-store", "data"),
        prevent_initial_call=True,
    )
    def _poll(_n_intervals: int, job_id: str | None):
        job = runner.poll(job_id)
        if job is None:
            return no_update, no_update, True, False, no_update

        log = _log_view(job.lines)
        if not job.done:
            return no_update, log, False, True, no_update

        runner.forget(job_id)
        if job.error:
            return (
                ui.alert(f"Lauf fehlgeschlagen: {job.error}", "error"),
                log,
                True,
                False,
                no_update,
            )

        result = job.result
        selected = (
            result.child_run_ids[0]
            if result.sweep_batch and result.child_run_ids
            else result.run_id
        )
        return _result_message(result), log, True, False, selected
