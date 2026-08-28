"""Die linke Zone: das Bedienfeld — was eingestellt ist, und der Start.

**Sie ist kein Formular.** Bis P1.6 stand hier der vollständige geführte Ablauf
samt Editor; am laufenden System gemessen waren das 10,7 Bildschirme, 752
Wörter und 122 Eingabefelder in einer 336 px breiten Spalte, mit dem
Start-Knopf 6,1 Bildschirme tief. Beide Abnahmekriterien der Vorgängerpakete
waren dabei erfüllt — P1.1 zählt Entscheidungen (drei), P1.5 prüft Mechanik
(fünf Zonen, kein Seiten-Scroll). Ein Kriterium, das die Anzahl misst, sagt
nichts über die Erreichbarkeit.

Seit P1.6 trägt die Spalte drei Dinge, und nur diese:

1. **Was eingestellt ist**, in drei Zeilen — Szenario, Länge, Rechenmodus. Jede
   Zeile führt in den Bereich «Einrichten». Es sind **Texte, keine
   Eingabefelder**: Dieselbe Feld-ID zweimal im DOM ist für Dash ein
   Laufzeitfehler, und der Bereich «Einrichten» liegt gleichzeitig darin.
   `tests/test_web_rail.py` hält das fest.
2. **Den Preflight** — er gehört neben den Knopf, den er absichert.
3. **Den Start-Knopf**, in einem klebenden Fuß, damit er sichtbar bleibt, egal
   wie lang die Warnungen darüber werden.

Das Fortschritts-Log steht nicht hier, sondern in der Konsole der Telemetrie —
zusammen mit den Ereignissen und den Vorfällen, zu denen es gehört. Es fließt
über `run-progress-store` dorthin.
"""

from __future__ import annotations

from dash import Input, Output, State, dcc, html, no_update

from dashboard.config_catalog import list_sweep_presets, validate_draft
from dashboard.web import components as ui
from dashboard.web import config_editor, routing, runner
from dashboard.web.config_editor import compute_mode, start_flow
from dashboard.web.state import STORE_ID, draft_from_dict, initial_draft_dict

#: Abstand, in dem das Log nachgezogen wird. Kürzer wirkt hektisch und erzeugt
#: nur Last; länger lässt den Lauf tot wirken.
POLL_INTERVAL_MS = 1000

#: Die Fortschrittszeilen des laufenden Jobs. Als Store statt als gerenderte
#: Liste, weil die Konsole in einer anderen Zone steht als der Startknopf.
PROGRESS_STORE = "run-progress-store"

#: Ob gerade ein Lauf rechnet — die Kopfzeile liest das für ihren Zustand.
RUNNING_STORE = "run-running-store"

#: Takt, in dem **jede** Sitzung den Serverzustand nachfragt — auch die, die
#: den Lauf nicht gestartet hat.
#:
#: `run-poll` läuft nur in der Sitzung, die auf «Start» gedrückt hat. Wer die
#: Seite währenddessen neu lädt oder in einem zweiten Tab öffnet, hatte damit
#: keinen einzigen Eingang, der ihm von dem Lauf erzählt: Die Kopfzeile sagte
#: «System bereit», und «Start» stand aktiv da, obwohl `runner.start` jeden
#: zweiten Lauf ablehnt. Der Takt ist bewusst träge — die Abfrage ist ein
#: Wörterbuch-Durchlauf unter einem Lock, und der Zustand ändert sich zweimal
#: je Lauf.
HEARTBEAT = "run-heartbeat"
HEARTBEAT_INTERVAL_MS = 2000

#: Der Wirt für die drei Stand-Zeilen. Sie ändern sich mit dem Entwurf und
#: werden deshalb nachgefüllt, statt die Spalte neu zu bauen.
SUMMARY_HOST = "rail-summary"


def _summary(draft: dict) -> str:
    runs = int(draft.get("run_count") or 1)
    run_label = f"{runs} Läufe" if runs > 1 else "1 Lauf"
    if draft.get("run_all_sweeps"):
        run_label = "alle Szenario-Presets"
    return (
        f"Szenario: {draft.get('scenario_mode', 'basis')} · "
        f"Ticks: {draft.get('rounds', '?')} · {run_label}"
    )


# --- Was eingestellt ist ---------------------------------------------------


def _scenario_name(draft: dict) -> str:
    """Der gewählte Ausgangspunkt, so benannt wie im Einrichten."""

    choice = start_flow.of(draft)
    if choice == start_flow.STANDARD:
        return "Standard-Ausgangslage"
    if choice == start_flow.CUSTOM:
        return "Eigene Einstellungen"
    preset = next((s for s in list_sweep_presets() if s.id == choice), None)
    return preset.name if preset is not None else str(choice)


def _length(draft: dict) -> str:
    ticks = draft.get("rounds", "?")
    if draft.get("run_all_sweeps"):
        return f"{ticks} Ticks · alle Szenarien"
    runs = int(draft.get("run_count") or 1)
    return f"{ticks} Ticks" if runs == 1 else f"{ticks} Ticks · {runs}×"


def _row(label: str, value: str) -> dcc.Link:
    """Eine Stand-Zeile: Beschriftung, Wert, und der Weg dorthin.

    Ein Verweis und kein Eingabefeld — geändert wird im Bereich «Einrichten».
    """

    return dcc.Link(
        [
            html.Span(label, className="af-rail-row__label"),
            html.Span(value, className="af-rail-row__value", title=value),
            ui.icon("chevron_right", "af-rail-row__chevron text-base"),
        ],
        # Seit P1.7 liegt das Einrichten auf dem leeren Pfad — dort fängt man an.
        href=routing.url(""),
        className="af-rail-row",
    )


def summary_rows(draft: dict) -> html.Div:
    """Szenario, Länge, Rechenmodus — der Entwurf auf drei Zeilen."""

    return html.Div(
        [
            _row("Szenario", _scenario_name(draft)),
            _row("Länge", _length(draft)),
            _row("Rechenmodus", compute_mode.short_label(draft)),
        ],
        className="af-rail-rows",
    )


# --- Die Zone als Ganzes ---------------------------------------------------


def rail(draft: dict | None = None) -> html.Div:
    """Der Inhalt der linken Zone."""

    draft = draft or initial_draft_dict()
    # Der Serverzustand gilt schon beim ersten Zeichnen: Wer die Seite während
    # eines fremden Laufs öffnet, soll den Knopf gar nicht erst aktiv sehen.
    laeuft = runner.is_running()
    return html.Div(
        [
            # Nur die Überschrift. Bis P1.7 stand hier ein Knopf «Einrichten» —
            # er führte dorthin, wo der Navigationspunkt zwei Zentimeter darüber
            # auch hinführt, und die drei Stand-Zeilen darunter tun es ebenfalls.
            html.Div(
                html.H1("Lauf", className=ui.H3),
                className="af-pane__sticky",
            ),
            dcc.Store(id="cfg-editor-refresh", data=0),
            dcc.Store(id="run-job-store"),
            dcc.Store(id=PROGRESS_STORE, data=[]),
            dcc.Store(id=RUNNING_STORE, data=laeuft),
            dcc.Interval(id="run-poll", interval=POLL_INTERVAL_MS, disabled=True),
            dcc.Interval(id=HEARTBEAT, interval=HEARTBEAT_INTERVAL_MS),
            html.Div(summary_rows(draft), id=SUMMARY_HOST, className="mb-5"),
            # Der Preflight wird von `_live` nachgefüllt — er haengt an der
            # Konfigurationspruefung, die bei jeder Aenderung einmal laeuft.
            html.Div(
                start_flow.preflight(
                    draft, start_flow.errors_for(draft), slot="rail", compact=True
                ),
                id=start_flow.slot_id("preflight"),
            ),
            html.Div(id="run-status", className="mt-4"),
            html.Div(
                [
                    ui.button(
                        "Start",
                        id="run-start",
                        icon_name="play_arrow",
                        className="w-full",
                        disabled=laeuft,
                    ),
                    html.P(_summary(draft), id="run-summary", className=f"{ui.CAPTION} mt-2"),
                ],
                className="af-rail-footer",
            ),
        ],
        className="af-pane af-rail",
    )


#: Alter Name, damit Aufrufer und Tests, die die Zone als Ganzes bauen,
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
        Output(SUMMARY_HOST, "children"),
        Input(STORE_ID, "data"),
    )
    def _update_summary(draft: dict | None):
        data = draft or {}
        return _summary(data), summary_rows(data)

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
        Output("run-start", "disabled", allow_duplicate=True),
        Input(HEARTBEAT, "n_intervals"),
        Input("run-poll", "disabled"),
        State(RUNNING_STORE, "data"),
        prevent_initial_call=True,
    )
    def _running(_beat, poll_disabled: bool | None, bisher: bool | None):
        """Ob gerade gerechnet wird — für Kopfzeile und Start-Knopf.

        **Der Serverzustand entscheidet, nicht der Zustand dieser Sitzung.**
        Die frühere Fassung las nur die beiden Schalter, die der eigene Lauf
        setzt, mit der Begründung, die Anzeige gehöre zu dieser einen Sitzung.
        Das trifft für die Anzeige zu, aber nicht für die Sache dahinter:
        `runner` lässt **einen** Lauf im ganzen Prozess zu (`launch_simulation`
        leitet `stdout` um, zwei Läufe schnitten sich die Ausgabe ab). Wer die
        Seite während eines Laufs neu lud, sah deshalb «System bereit» und
        einen aktiven «Start», der beim Drücken mit «Es läuft bereits eine
        Simulation» abwies — am laufenden System nachgestellt.

        `run-poll` bleibt als zweite Quelle daneben, weil er sofort umschlägt:
        Der Takt allein ließe den eigenen Start bis zu zwei Sekunden lang
        unbestätigt.

        Geschrieben wird nur bei echter Änderung — sonst stieße der Takt alle
        zwei Sekunden die Kopfzeile samt Neuladen der Laufdaten an.
        """

        laeuft = (not bool(poll_disabled)) or runner.is_running()
        if bool(bisher) == laeuft:
            return no_update, no_update
        return laeuft, laeuft
