"""Die linke Zone: der geführte Ablauf aus P1.1, jetzt als Parameterspalte.

Die Reihenfolge ist die Aussage der Spalte (P1.1): Erst die drei
Entscheidungen, die bis zum Start genügen, dann der Start selbst, und erst
danach — zugeklappt — die rund sechzig Felder für den Fall, dass eine bestimmte
Annahme geprüft werden soll.

**Was der Leitstand daran ändert, ist der Ort, nicht der Ablauf.** Vorher stand
dieser Block auf einer eigenen Seite; wer etwas änderte und die Wirkung sehen
wollte, wechselte den Bereich. Jetzt steht er dauerhaft links neben Szene und
Telemetrie. `start_flow.layout()` selbst ist unverändert — daran hängen die
Zusicherungen aus `tests/test_web_start_flow.py`: höchstens drei Entscheidungen,
kein Feld doppelt.

Zwei Dinge sind gewandert:

* Die Tab-Leiste der vier Editor-Bereiche läuft in der schmalen Spalte
  kompakt und zweizeilig (`af-tabs--rail`). Sie bleibt eine Tab-Leiste: Der
  Wechsel hängt an `cfg-tabs` → `cfg-tab-content`, und den umzubauen hieße,
  die Callback-Kette des Editors anzufassen, ohne dass jemand etwas davon
  hätte.
* Das Fortschritts-Log steht nicht mehr unter dem Startknopf, sondern in der
  Konsole der Telemetrie — zusammen mit den Ereignissen und den Vorfällen, zu
  denen es gehört. Es fließt über `run-progress-store` dorthin.
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

#: Die Fortschrittszeilen des laufenden Jobs. Als Store statt als gerenderte
#: Liste, weil die Konsole in einer anderen Zone steht als der Startknopf.
PROGRESS_STORE = "run-progress-store"

#: Ob gerade ein Lauf rechnet — die Kopfzeile liest das für ihren Zustand.
RUNNING_STORE = "run-running-store"


def _summary(draft: dict) -> str:
    runs = int(draft.get("run_count") or 1)
    run_label = f"{runs} Läufe" if runs > 1 else "1 Lauf"
    if draft.get("run_all_sweeps"):
        run_label = "alle Szenario-Presets"
    return (
        f"Szenario: {draft.get('scenario_mode', 'basis')} · "
        f"Ticks: {draft.get('rounds', '?')} · {run_label}"
    )


def rail(draft: dict | None = None) -> html.Div:
    """Der Inhalt der linken Zone."""

    draft = draft or initial_draft_dict()
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Simulation starten", className=ui.H2),
                    html.P(
                        "Drei Entscheidungen genügen: was gerechnet wird, wie weit, und womit.",
                        className=f"{ui.CAPTION} mt-1",
                    ),
                ],
                className="af-pane__sticky",
            ),
            dcc.Store(id="cfg-editor-refresh", data=0),
            dcc.Store(id="run-job-store"),
            dcc.Store(id=PROGRESS_STORE, data=[]),
            dcc.Store(id=RUNNING_STORE, data=False),
            dcc.Interval(id="run-poll", interval=POLL_INTERVAL_MS, disabled=True),
            config_editor.start_layout(draft),
            html.Div(
                [
                    ui.button(
                        "Start",
                        id="run-start",
                        icon_name="play_arrow",
                        className="w-full",
                    ),
                    html.P(_summary(draft), id="run-summary", className=f"{ui.CAPTION} mt-2"),
                ],
                className="mb-4",
            ),
            html.Div(id="run-status", className="mb-4"),
            ui.divider("my-6"),
            html.Div(
                [
                    html.P(
                        "Alle Einstellungen",
                        className="font-body text-sm font-medium af-text mb-3",
                    ),
                    config_editor.layout(draft),
                ]
            ),
        ],
        className="af-pane",
    )


#: Alter Name, damit Aufrufer und Tests, die die Seite als Ganzes bauen,
#: unverändert weiterlaufen.
layout = rail


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
                    "Einzelne Sweep-Runs oben in der Lauf-Auswahl wählen: "
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
                    "Einzelne Läufe oben in der Lauf-Auswahl: "
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
                "Die Szene und die Telemetrie zeigen ihn ab jetzt.",
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
        Output(PROGRESS_STORE, "data"),
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
        return job_id, False, ui.alert("Lauf aktiv …", "info"), [], True

    @app.callback(
        Output("run-status", "children", allow_duplicate=True),
        Output(PROGRESS_STORE, "data", allow_duplicate=True),
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

        if not job.done:
            return no_update, list(job.lines), False, True, no_update

        runner.forget(job_id)
        if job.error:
            return (
                ui.alert(f"Lauf fehlgeschlagen: {job.error}", "error"),
                list(job.lines),
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
        return _result_message(result), list(job.lines), True, False, selected

    @app.callback(
        Output(RUNNING_STORE, "data"),
        Input("run-poll", "disabled"),
        Input("run-start", "disabled"),
    )
    def _running(poll_disabled: bool | None, start_disabled: bool | None):
        """Ob gerade gerechnet wird — für die Zustandsanzeige der Kopfzeile.

        Abgeleitet aus den beiden Schaltern, die der Lauf ohnehin setzt, statt
        aus `runner.is_running()`: Der Serverzustand gälte für alle Sitzungen,
        die Anzeige gehört aber zu dieser einen.
        """

        return bool(start_disabled) and not bool(poll_disabled)
