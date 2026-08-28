"""Die untere Zone: der Tick als Zeitachse, mit Abspielsteuerung.

Ein Tick ist **keine** Kalenderzeit (Invariante 5) — die Leiste zeigt deshalb
Tick-Nummern, keine Daten, und die Geschwindigkeit steht in Millisekunden je
Tick, nicht als «Zeitraffer».

Die Leiste ist die **einzige** Zeitachse der Oberfläche: Szene, Kennzahlen und
Verläufe lesen alle `tick-store`. Vor dem Leitstand brachte jede Plotly-
Animation ihre eigenen Abspielknöpfe mit, und zwei Zeitachsen nebeneinander
sagen nie dasselbe.
"""

from __future__ import annotations

from typing import Any

from dash import Input, Output, State, ctx, dcc, html, no_update

from dashboard.web import components as ui
from dashboard.web.run_data import RunData

#: Der Tick, den alle drei Zonen zeigen.
TICK_STORE = "tick-store"
#: Ob gerade abgespielt wird.
PLAY_STORE = "timeline-play-store"

HOST = "timeline-host"
INTERVAL = "timeline-interval"
SLIDER = "timeline-slider"
READOUT = "timeline-readout"
SPEED = "timeline-speed"

PLAY = "timeline-play"
STOP = "timeline-stop"
STEP_BACK = "timeline-step-back"
STEP_FORWARD = "timeline-step-forward"
TO_START = "timeline-to-start"
TO_END = "timeline-to-end"

#: Millisekunden je Tick. Der mittlere Wert ist die Voreinstellung: schnell
#: genug, um eine Entwicklung zu sehen, langsam genug, um sie zu lesen.
SPEEDS = [
    {"label": "0,25×", "value": 2000},
    {"label": "0,5×", "value": 1000},
    {"label": "1×", "value": 500},
    {"label": "2×", "value": 250},
    {"label": "4×", "value": 125},
]
DEFAULT_SPEED = 500


def _marks(max_tick: int) -> dict:
    """Beschriftungen der Leiste — höchstens sieben, sonst überlagern sie sich."""

    if max_tick <= 1:
        return {1: "1"}
    schritt = max(1, round(max_tick / 6))
    marks = {tick: str(tick) for tick in range(1, max_tick + 1, schritt)}
    marks[max_tick] = str(max_tick)
    return marks


def event_strip(data: RunData) -> html.Div:
    """Wo im Lauf etwas passiert ist — als Streifen unter der Leiste.

    Ohne den Streifen müsste man den Lauf durchscrubben, um zu finden, wo eine
    Politikänderung greift. Warnungen und Fehler stechen hervor, der
    Normalbetrieb bleibt leise.
    """

    max_tick = data.max_tick
    if max_tick <= 0 or not data.events:
        return html.Div(className="af-timeline__events")

    stufen: dict[int, str] = {}
    for event in data.events:
        try:
            tick = int(event.get("round_number") or 0)
        except (TypeError, ValueError):
            continue
        if tick <= 0:
            continue
        art = str(event.get("event_type") or "")
        quelle = str(event.get("source_agent") or "")
        if "policy" in art or quelle == "regulator":
            stufen[tick] = "warning"
        else:
            stufen.setdefault(tick, "")

    marker = [
        html.Span(
            className=(
                f"af-timeline__event af-timeline__event--{stufe}" if stufe else "af-timeline__event"
            ),
            style={"left": f"{(tick - 1) / max(max_tick - 1, 1) * 100:.3f}%"},
            title=f"Tick {tick}",
        )
        for tick, stufe in sorted(stufen.items())
    ]
    return html.Div(marker, className="af-timeline__events")


def readout(tick: int, max_tick: int) -> str:
    return f"Tick {tick} / {max_tick or '?'}"


def controls(playing: bool, *, disabled: bool = False) -> html.Div:
    return html.Div(
        [
            ui.icon_button("first_page", "An den Anfang", id=TO_START, disabled=disabled),
            ui.icon_button("chevron_left", "Ein Tick zurück", id=STEP_BACK, disabled=disabled),
            ui.icon_button(
                "pause" if playing else "play_arrow",
                "Pause" if playing else "Abspielen",
                id=PLAY,
                active=playing,
                disabled=disabled,
            ),
            ui.icon_button("stop", "Anhalten und zurücksetzen", id=STOP, disabled=disabled),
            ui.icon_button("chevron_right", "Ein Tick vor", id=STEP_FORWARD, disabled=disabled),
            ui.icon_button("last_page", "Ans Ende", id=TO_END, disabled=disabled),
        ],
        className="af-timeline__controls",
    )


def layout(data: RunData, tick: int = 1, *, playing: bool = False) -> html.Div:
    """Die Leiste für einen bestimmten Lauf.

    Wird beim Wechsel des Laufs als Ganzes ersetzt: Der Wertebereich hängt am
    Lauf, und ein Schieberegler, dessen Maximum sich unter der Hand ändert, ist
    schwerer zu verstehen als einer, der neu erscheint.
    """

    max_tick = data.max_tick
    leer = max_tick <= 0

    return html.Div(
        [
            html.Div(
                [
                    controls(playing, disabled=leer),
                    html.Div(
                        [
                            dcc.Slider(
                                id=SLIDER,
                                min=1,
                                max=max(max_tick, 1),
                                step=1,
                                value=min(max(tick, 1), max(max_tick, 1)),
                                marks=_marks(max(max_tick, 1)),
                                included=True,
                                disabled=leer,
                                tooltip={"placement": "top", "always_visible": False},
                                className="af-slider",
                            ),
                            event_strip(data),
                        ],
                        className="af-timeline__track",
                    ),
                    html.Span(
                        readout(tick, max_tick),
                        id=READOUT,
                        className="af-timeline__readout",
                    ),
                    dcc.Dropdown(
                        id=SPEED,
                        options=SPEEDS,
                        value=DEFAULT_SPEED,
                        clearable=False,
                        searchable=False,
                        className="af-dropdown w-24 shrink-0",
                    ),
                ],
                className="af-timeline",
            ),
            dcc.Interval(id=INTERVAL, interval=DEFAULT_SPEED, disabled=True),
        ]
    )


def _clamp(tick: Any, max_tick: int) -> int:
    try:
        value = int(tick)
    except (TypeError, ValueError):
        value = 1
    return max(1, min(value, max(max_tick, 1)))


def register_callbacks(app) -> None:
    @app.callback(
        Output(PLAY_STORE, "data"),
        Output(TICK_STORE, "data", allow_duplicate=True),
        Input(PLAY, "n_clicks"),
        Input(STOP, "n_clicks"),
        Input(STEP_BACK, "n_clicks"),
        Input(STEP_FORWARD, "n_clicks"),
        Input(TO_START, "n_clicks"),
        Input(TO_END, "n_clicks"),
        State(PLAY_STORE, "data"),
        State(TICK_STORE, "data"),
        State(SLIDER, "max"),
        prevent_initial_call=True,
    )
    def _controls(_p, _s, _b, _f, _a, _e, playing: bool | None, tick, max_tick):
        """Die sechs Knöpfe in einem Callback.

        Sie verändern beide dasselbe Paar (läuft es? welcher Tick?); getrennte
        Callbacks müssten sich denselben Ausgang teilen und würden sich beim
        gleichzeitigen Feuern gegenseitig überschreiben.
        """

        obergrenze = int(max_tick or 1)
        aktuell = _clamp(tick, obergrenze)
        ausgeloest = ctx.triggered_id

        if ausgeloest == PLAY:
            # Am Ende erneut auf «Abspielen» heißt: von vorn. Sonst passierte
            # sichtbar nichts, und der Knopf wirkte kaputt.
            if not playing and aktuell >= obergrenze:
                return True, 1
            return not bool(playing), no_update
        if ausgeloest == STOP:
            return False, 1
        if ausgeloest == STEP_BACK:
            return False, max(1, aktuell - 1)
        if ausgeloest == STEP_FORWARD:
            return False, min(obergrenze, aktuell + 1)
        if ausgeloest == TO_START:
            return False, 1
        if ausgeloest == TO_END:
            return False, obergrenze
        return no_update, no_update

    @app.callback(
        Output(INTERVAL, "disabled"),
        Output(INTERVAL, "interval"),
        Output(PLAY, "children"),
        Output(PLAY, "title"),
        Output(PLAY, "className"),
        Input(PLAY_STORE, "data"),
        Input(SPEED, "value"),
    )
    def _transport(playing: bool | None, speed):
        laeuft = bool(playing)
        return (
            not laeuft,
            int(speed or DEFAULT_SPEED),
            ui.icon("pause" if laeuft else "play_arrow", "text-lg"),
            "Pause" if laeuft else "Abspielen",
            "af-icon-btn af-icon-btn--active" if laeuft else "af-icon-btn",
        )

    @app.callback(
        Output(TICK_STORE, "data", allow_duplicate=True),
        Output(PLAY_STORE, "data", allow_duplicate=True),
        Input(INTERVAL, "n_intervals"),
        State(PLAY_STORE, "data"),
        State(TICK_STORE, "data"),
        State(SLIDER, "max"),
        prevent_initial_call=True,
    )
    def _advance(_n, playing: bool | None, tick, max_tick):
        """Einen Tick weiter — und am Ende von selbst anhalten.

        Zu wiederholen wäre die bequemere Wahl und die falsche: Ein Lauf hat
        ein Ende, und eine Schleife würde vortäuschen, es ginge weiter.

        **Der Abspielzustand wird geprüft, nicht vorausgesetzt.** Auf
        `Interval.disabled` allein ist kein Verlass: Wird die Leiste beim
        Wechsel des Laufs neu aufgebaut, ist das `dcc.Interval` für Dash ein
        *neuer* Eingang und feuert einmal, bevor `_transport` es abschalten
        kann — `prevent_initial_call` deckt nur den ersten Seitenaufbau, nicht
        eine nachträglich eingefügte Komponente. Ohne diese Zeile stand nach
        jedem Wechsel des Laufs Tick 2 statt Tick 1, sichtbar in Regler,
        Kennzahlen und Szene. Am laufenden System gefunden.
        """

        if not playing:
            return no_update, no_update

        obergrenze = int(max_tick or 1)
        naechster = _clamp(tick, obergrenze) + 1
        if naechster > obergrenze:
            return obergrenze, False
        return naechster, no_update

    @app.callback(
        Output(TICK_STORE, "data", allow_duplicate=True),
        Input(SLIDER, "value"),
        prevent_initial_call=True,
    )
    def _scrub(value):
        try:
            return max(1, int(value))
        except (TypeError, ValueError):
            return no_update

    @app.callback(
        Output(SLIDER, "value"),
        Output(READOUT, "children"),
        Input(TICK_STORE, "data"),
        State(SLIDER, "max"),
    )
    def _reflect(tick, max_tick):
        """Der Regler folgt dem Store — auch wenn ein Knopf ihn bewegt hat.

        Der Rückweg ist erlaubt, weil der Regler keine Eingabe *speichert*: Er
        stellt den Store dar und schreibt ihn beim Ziehen. Die Einbahnstraße aus
        P1.1 gilt für Konfigurationsfelder, deren Wert in den Lauf geht — hier
        gibt es keinen zweiten Ort, an dem dieselbe Zahl gehalten würde.
        """

        obergrenze = int(max_tick or 1)
        aktuell = _clamp(tick, obergrenze)
        return aktuell, readout(aktuell, obergrenze)
