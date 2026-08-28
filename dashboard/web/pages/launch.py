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
from dashboard.web.config_editor import compute_mode, start_flow, wizard
from dashboard.web.state import STORE_ID, draft_from_dict, initial_draft_dict
from dashboard.web.views import running

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
    if start_flow.ist_vergleich(draft):
        return f"Szenario-Vergleich · {len(list_sweep_presets())} Szenarien · je eigene Länge"
    runs = int(draft.get("run_count") or 1)
    run_label = f"{runs} Läufe" if runs > 1 else "1 Lauf"
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
    # Kein Sonderfall für den Vergleich mehr: Dort ruft `summary_rows` diese
    # Funktion gar nicht erst auf. Sie stand hier mit «{ticks} Ticks · alle
    # Szenarien» und nannte damit eine Länge, die der Vergleich seit W1.2 nicht
    # verwendet.
    ticks = draft.get("rounds", "?")
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
    """Szenario, Länge, Rechenmodus — der Entwurf auf drei Zeilen.

    **Beim Szenario-Vergleich stehen hier andere drei** (P1.9-W1.3). Er nimmt
    vom Entwurf nichts entgegen: Szenario, Länge und Rechenmodus kommen dann aus
    den Presets bzw. aus dem Vertrag des Sweeps. Die Zeilen des Entwurfs
    anzuzeigen hieße, drei Werte zu behaupten, mit denen nicht gerechnet wird —
    derselbe Fehler wie im Preflight, nur in der Nachbarzone.
    """

    if start_flow.ist_vergleich(draft):
        return html.Div(
            [
                _row("Lauf", f"Vergleich · {len(list_sweep_presets())} Szenarien"),
                _row("Länge", "je Szenario"),
                _row("Rechenmodus", "Nur Zahlen (vorgegeben)"),
            ],
            className="af-rail-rows",
        )

    return html.Div(
        [
            _row("Szenario", _scenario_name(draft)),
            _row("Länge", _length(draft)),
            _row("Rechenmodus", compute_mode.short_label(draft)),
        ],
        className="af-rail-rows",
    )


def progress_payload() -> dict | None:
    """Der Fortschritt des aktiven Laufs als einfache Zuordnung — oder `None`.

    Eine Zuordnung und kein Objekt, weil der Wert durch den Browser läuft.
    Sie steht schon beim **ersten** Zeichnen im Store: Sonst zeigte der
    Leitstand nach jedem Laden erst die Szene und wechselte zwei Sekunden
    später zum Ladebildschirm, wenn der Takt zum ersten Mal feuert. Dasselbe
    Prinzip wie beim Laufzustand — der Server weiß es sofort, also sagt er es
    sofort.
    """

    aktuell = runner.progress()
    if aktuell is None:
        return None
    return {
        "job_id": aktuell.job_id,
        "tick": aktuell.tick,
        "total": aktuell.total,
        "line": aktuell.line,
        "lines": list(aktuell.lines),
    }


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
            dcc.Store(id=PROGRESS_STORE, data=progress_payload()),
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

    from dashboard.web.views import running

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
            # Der Weg weiter gehört an die Fertigmeldung: Hier endet der
            # Ablauf «Einrichten → Rechnen → Auswerten», und der letzte
            # Schritt soll nicht gesucht werden müssen.
            running.finished_link(),
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
        Output(PROGRESS_STORE, "data", allow_duplicate=True),
        Output("run-start", "disabled"),
        # **Der sechste Ausgang steht bewusst am Ende.** Die Reihenfolge der
        # ersten fünf ist in `tests/test_web_runner.py` festgenagelt (Status an
        # Index 2, Knopf an Index 4); ein Einschub dazwischen ließe die Meldung
        # in der falschen Komponente landen, ohne dass etwas rot wird.
        Output("url", "pathname", allow_duplicate=True),
        Input("run-start", "n_clicks"),
        # Der Knopf am Ende der Schrittfolge (P1.7). Zwei Ausloeser, **ein**
        # Startpfad: dieselbe Pruefung, dasselbe `runner.start`. Der Einwand
        # aus P1.6 galt einer zweiten Startlogik, nicht einem zweiten Knopf.
        Input(wizard.START, "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _start(n_clicks: int | None, wizard_clicks: int | None, draft: dict | None):
        """Einen Lauf starten — und den Bildschirm dorthin führen, wo er zu sehen ist.

        **Der Wechsel gehört zum Start.** P1.7 Stufe B hat zugesagt: «Ein Start
        wechselt sichtbar den Bildschirm; während des Laufs ist von der
        Einrichtung nichts mehr zu sehen.» Das stimmte, solange der einzige
        Knopf im Bedienfeld stand — dort ist man bereits auf dem Leitstand.
        Stufe C hat danach den Knopf am Ende der Schrittfolge ergänzt und damit
        den Hauptweg dorthin verlegt; von dort aus blieb der Bildschirm auf dem
        Formular stehen, und statt des versprochenen Wechsels erschien nur das
        Fortschrittsfenster. Am laufenden System nachgestellt.
        """

        if not (n_clicks or wizard_clicks):
            return no_update, no_update, no_update, no_update, no_update, no_update

        # Vor dem Start prüfen, nicht danach: Ohne das läuft eine kaputte Config
        # an und scheitert irgendwo im ersten Tick — ein negativer Seed etwa mit
        # «expected non-negative integer» aus numpy, ohne Bezug zum Seed.
        config_errors = validate_draft(draft_from_dict(draft or {}))
        if config_errors:
            # Kein Wechsel: Wer die Meldung lesen soll, bleibt bei den Feldern,
            # an denen sie hängt.
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
                no_update,
            )

        try:
            job_id = runner.start(draft or {})
        except Exception as exc:  # noqa: BLE001 - «läuft schon» ist ein normaler Fall
            return no_update, no_update, ui.alert(str(exc), "warning"), no_update, False, no_update
        # Der Fortschritt wird geleert, nicht stehen gelassen: Sonst zeigte der
        # Ladebildschirm eine Sekunde lang den Stand des vorigen Laufs, bis der
        # Takt ihn ersetzt. Die Zieladresse kommt aus der Bereichsliste und
        # nicht als Zeichenkette — sie ist mit P1.7 schon einmal umgezogen.
        return (
            job_id,
            False,
            ui.alert("Lauf aktiv …", "info"),
            None,
            True,
            routing.url(running.leitstand_route()),
        )

    @app.callback(
        Output("run-status", "children", allow_duplicate=True),
        Output("run-poll", "disabled", allow_duplicate=True),
        Output("run-start", "disabled", allow_duplicate=True),
        Output("last-launched-run-store", "data"),
        Input("run-poll", "n_intervals"),
        State("run-job-store", "data"),
        prevent_initial_call=True,
    )
    def _poll(_n_intervals: int, job_id: str | None):
        """Der Ausgang des **eigenen** Laufs — Ergebnis, Fehler, Freigabe.

        Die Fortschrittszeilen holt seit P1.7 nicht mehr dieser Callback,
        sondern der Takt: Sie gehören dem Server, nicht dem Job-Besitzer, und
        eine fremde Sitzung sah sonst einen leeren Balken. Was hier bleibt, ist
        das, was wirklich nur den Besitzer angeht — die Erfolgsmeldung mit der
        Run-Kennung und das Aufräumen des Jobs.
        """

        job = runner.poll(job_id)
        if job is None:
            return no_update, True, False, no_update

        if not job.done:
            return no_update, False, True, no_update

        runner.forget(job_id)
        if job.error:
            return ui.alert(f"Lauf fehlgeschlagen: {job.error}", "error"), True, False, no_update

        result = job.result
        selected = (
            result.child_run_ids[0]
            if result.sweep_batch and result.child_run_ids
            else result.run_id
        )
        return _result_message(result), True, False, selected

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

    @app.callback(
        Output(PROGRESS_STORE, "data"),
        Input(HEARTBEAT, "n_intervals"),
        State(PROGRESS_STORE, "data"),
        prevent_initial_call=True,
    )
    def _progress(_beat, bisher: dict | None):
        """Der Fortschritt des aktiven Laufs — für **jede** Sitzung.

        Bis P1.7 füllte `_poll` diesen Store, und `run-poll` läuft nur in der
        Sitzung, die gestartet hat. Ein zweiter Tab und eine neu geladene Seite
        sahen deshalb nichts. Jetzt liest der Takt `runner.progress()`, und das
        ist eine Auskunft über den Server, nicht über diese Sitzung.

        Wie beim Laufzustand wird nur bei echter Änderung geschrieben: Der Store
        speist Ladebildschirm, Fortschrittsfenster und Konsole, und die sollen
        sich bewegen, wenn sich etwas bewegt hat — nicht im Takt.
        """

        neu = progress_payload()
        if neu is None:
            return None if bisher else no_update
        return no_update if neu == bisher else neu
