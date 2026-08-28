"""Tab «Abfrage»: grounded Q&A über die abgeschlossenen Run-Daten.

Der `StateExplorer` beantwortet ausschließlich aus `tick_mechanics.json`,
`price_history.json` und `event_log.json` — keine erfundenen Zahlen. Die
Oberfläche macht sichtbar, was dabei übergeben wird: der Datenkontext und die
Artefakt-Checks lassen sich jederzeit einblenden.
"""

from __future__ import annotations

from dash import Input, Output, State, dcc, html, no_update

from dashboard.consistency_report import run_consistency_checks
from dashboard.web import components as ui
from dashboard.web import theme
from src.reporting.state_explorer import (
    StateExplorer,
    build_grounded_context_block,
    load_run_context,
    parse_tick_hint,
)

_STATUS_ICONS = {"ok": "check_circle", "warn": "warning", "fail": "cancel"}
_STATUS_COLORS = {
    "ok": "af-text-positive",
    "warn": "af-text-warning",
    "fail": "af-text-negative",
}


class _MockLLM:
    """Antwortet ohne Ollama — für Vorführungen ohne laufendes Modell."""

    def __init__(self, focus_tick: int | None) -> None:
        self._focus_tick = focus_tick

    def call(self, prompt: str) -> str:
        scope = f"Tick {self._focus_tick}" if self._focus_tick else "dem gesamten Lauf"
        return (
            f"Demo-Antwort: Die Frage bezieht sich auf {scope}. "
            "Deaktivieren Sie «Demo ohne Ollama», wenn Ollama für echte Antworten laufen soll."
        )


def _resolve_focus_tick(manual_tick: int | None, question: str) -> int | None:
    """Manuelle Eingabe schlägt den Tick-Hinweis aus der Frage."""

    if manual_tick and int(manual_tick) > 0:
        return int(manual_tick)
    return parse_tick_hint(question)


def _message_bubble(role: str, content: str) -> html.Div:
    if role == "user":
        return html.Div(
            ui.markdown(content),
            className="af-chat-user rounded-lg px-4 py-3 max-w-3xl ml-auto mb-3",
        )
    return html.Div(
        ui.markdown(content),
        className="af-surface af-bordered rounded-lg px-4 py-3 max-w-3xl mb-3",
    )


def _history(messages: list) -> html.Div:
    if not messages:
        return html.Div(
            ui.empty_state(
                "Noch keine Fragen zu diesem Lauf.",
                hint="Stellen Sie unten eine Frage — die Antwort stützt sich ausschließlich "
                "auf die Artefakte dieses Runs.",
                icon_name="forum",
            ),
            className="mb-4",
        )
    return html.Div([_message_bubble(role, content) for role, content in messages])


def _checks_panel(run_dir) -> html.Div:
    checks = run_consistency_checks(run_dir)
    rows = [
        html.Div(
            [
                ui.icon(
                    _STATUS_ICONS.get(check.status, "circle"),
                    f"text-base shrink-0 mt-0.5 {_STATUS_COLORS.get(check.status, 'af-text-faint')}",
                ),
                html.Div(
                    [
                        html.Span(check.title, className="font-body text-sm font-medium af-text"),
                        html.Span(f" — {check.detail}", className="font-body text-sm af-text-body"),
                    ]
                ),
            ],
            className="flex items-start gap-2 py-1.5",
        )
        for check in checks
    ]
    return ui.accordion("Konsistenz-Checks (Ground Truth)", html.Div(rows), open=True)


def render(
    run_dir, run_id: str, *, messages: list | None = None, mode: str = theme.LIGHT
) -> html.Div:
    return html.Div(
        [
            html.P(
                "Fragen Sie den gesamten Lauf ab — z. B. Verlauf über alle Ticks, Vergleiche "
                "oder einzelne Perioden. Optional: Tick-Nummer eingeben oder in der Frage "
                "nennen (z. B. «Was passierte bei Tick 15?»).",
                className="font-body text-sm af-text-body mb-5 max-w-3xl",
            ),
            ui.card(
                ui.grid(
                    ui.field(
                        "Tick einschränken (0 = gesamter Lauf)",
                        dcc.Input(
                            id="explorer-tick",
                            type="number",
                            min=0,
                            max=500,
                            step=1,
                            value=0,
                            className="af-input",
                        ),
                    ),
                    html.Div(
                        [
                            ui.checkbox(
                                "Demo ohne Ollama (Mock)",
                                value=False,
                                id="explorer-mock",
                                hint="Deaktivieren für echte Antworten via Ollama (Modell in .env).",
                            ),
                            ui.checkbox(
                                "Datenkontext anzeigen", value=False, id="explorer-show-context"
                            ),
                            ui.checkbox(
                                "Artefakt-Checks anzeigen", value=False, id="explorer-show-checks"
                            ),
                        ],
                        className="space-y-1",
                    ),
                    cols="md:grid-cols-2",
                ),
                class_name="mb-5",
            ),
            html.Div(id="explorer-panels", className="mb-5"),
            dcc.Loading(
                html.Div(_history(messages or []), id="explorer-history"),
                type="dot",
                color=theme.palette(mode)["accent"],
            ),
            html.Div(
                [
                    dcc.Input(
                        id="explorer-question",
                        type="text",
                        placeholder="Frage zur Simulation …",
                        debounce=False,
                        className="af-input flex-1",
                        n_submit=0,
                    ),
                    ui.button("Fragen", id="explorer-send", icon_name="send"),
                ],
                className="flex items-center gap-3 sticky bottom-0 af-surface pt-3",
            ),
        ]
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("explorer-panels", "children"),
        Input("explorer-show-context", "value"),
        Input("explorer-show-checks", "value"),
        Input("explorer-tick", "value"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _panels(show_context, show_checks, manual_tick, selected):
        if not selected:
            return no_update
        panels: list = []
        focus_tick = _resolve_focus_tick(manual_tick, "")
        if show_checks:
            panels.append(_checks_panel(selected["run_dir"]))
        if show_context:
            context = load_run_context(selected["run_id"], focus_tick=focus_tick)
            panels.append(
                ui.accordion(
                    "Daten, die an die Abfrage übergeben werden",
                    ui.code_block(build_grounded_context_block(context), max_height="28rem"),
                    open=True,
                )
            )
        return panels

    @app.callback(
        Output("explorer-history", "children"),
        Output("explorer-messages-store", "data"),
        Output("explorer-question", "value"),
        Input("explorer-send", "n_clicks"),
        Input("explorer-question", "n_submit"),
        State("explorer-question", "value"),
        State("explorer-tick", "value"),
        State("explorer-mock", "value"),
        State("explorer-messages-store", "data"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _ask(n_clicks, n_submit, question, manual_tick, use_mock, store, selected):
        store = dict(store or {})
        if not selected or not question or not str(question).strip():
            return no_update, no_update, no_update

        run_id = selected["run_id"]
        messages = list(store.get(run_id) or [])
        question = str(question).strip()
        focus_tick = _resolve_focus_tick(manual_tick, question)
        messages.append(["user", question])

        try:
            context = load_run_context(run_id, focus_tick=focus_tick)
            explorer = (
                StateExplorer(context, llm=_MockLLM(focus_tick))
                if use_mock
                else StateExplorer(context)
            )
            answer = explorer.ask(question)
        except Exception as exc:  # noqa: BLE001 - Ollama offline ist ein Normalfall
            answer = f"Abfrage fehlgeschlagen: {exc}"

        messages.append(["assistant", answer])
        store[run_id] = messages
        return _history(messages), store, ""
