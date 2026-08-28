"""Die Live-Szene im Viewport: die Population zu **einem** Tick.

Der Hauptbereich eines Leitstands zeigt das, worum es geht. In dieser Domäne ist
das keine Geometrie und keine Karte — es sind einige hundert Individuen mit
einer Zahlungsbereitschaft und einem Umweltbewusstsein, und sieben
Faktorzustände, die den Rahmen setzen, in dem sie entscheiden.

Der Unterschied zum Tab «Animation»: Dort läuft eine Plotly-Animation über alle
Ticks und bringt ihre eigenen Abspielknöpfe mit. Hier bestimmt die Zeitleiste
unten den Tick, und die Szene zeigt genau diesen einen. Damit gehören
Abspielsteuerung und Bild zusammen, statt zwei Zeitachsen nebeneinander zu
führen — die eine im Diagramm, die andere in der Oberfläche.

Die Aufbereitung der History kommt aus `views.animation.load_history`; zwei
eigene `read_csv` mit leicht verschiedenen Ableitungen wären genau die Sorte
Doppelung, aus der Divergenz entsteht.
"""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from dash import dcc, html

from dashboard.config_catalog import factor_options_from_file
from dashboard.web import components as ui
from dashboard.web import theme
from dashboard.web.run_data import RunData

#: Zoomstufen des Viewports, als Anteil des vollen Wertebereichs. Kleiner heißt
#: näher dran. Die Liste ist die einzige Quelle — die Schaltflächen laufen
#: darüber, das Overlay liest daraus seinen Prozentwert.
ZOOM_STEPS = (1.0, 0.75, 0.55, 0.4, 0.28)
DEFAULT_ZOOM = 0

ZOOM_IN = "scene-zoom-in"
ZOOM_OUT = "scene-zoom-out"
ZOOM_STORE = "scene-zoom-store"


def zoom_factor(index: int | None) -> float:
    step = ZOOM_STEPS[max(0, min(int(index or 0), len(ZOOM_STEPS) - 1))]
    return step


def zoom_label(index: int | None) -> str:
    """Der Zoom als Prozentangabe — 100 % ist der volle Wertebereich."""

    return f"{1.0 / zoom_factor(index):.0%}"


# --- Faktorstreifen --------------------------------------------------------


def _factor_labels() -> dict[str, dict[str, str]]:
    """Zustandsbeschreibungen aus `configs/factors.json`.

    Fällt die Datei aus, bleibt der Streifen bei den reinen Kürzeln — «F2.2»
    ohne Beschriftung ist mager, aber es ist wahr. Einen Text zu erfinden wäre
    schlimmer als keiner.
    """

    try:
        return factor_options_from_file()
    except Exception:  # noqa: BLE001 - eine fehlende Config darf die Szene nicht killen
        return {}


def factor_strip(states: dict[str, str]) -> html.Div:
    """Die sieben Deskriptoren als Zeile über der Szene."""

    if not states:
        return html.Div(
            ui.alert(
                "Keine Faktor-Zeitreihe in diesem Lauf (`timeseries/factors.csv` fehlt).",
                "info",
            ),
            className="mb-3",
        )

    labels = _factor_labels()
    chips = []
    for factor_id in sorted(states):
        state = states[factor_id]
        # Der zweite Zustand ist in allen sieben Faktoren die Abweichung vom
        # Ausgangsbild — er wird hervorgehoben, damit eine Strukturwende im
        # Streifen sofort ablesbar ist.
        gekippt = state.endswith(".2")
        beschreibung = (labels.get(factor_id) or {}).get(state, state)
        chips.append(
            html.Div(
                [
                    html.Span(state, className="af-factor__id"),
                    html.Span(beschreibung, className="af-factor__state", title=beschreibung),
                ],
                className="af-factor af-factor--active" if gekippt else "af-factor",
            )
        )
    return html.Div(
        chips,
        className="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-7 gap-2 mb-4",
    )


# --- Die Szene selbst ------------------------------------------------------


def _empty(message: str, hint: str) -> html.Div:
    return html.Div(ui.empty_state(message, hint=hint, icon_name="scatter_plot"), className="p-6")


def _ranges(frame, zoom: float) -> tuple[list[float], list[float]]:
    """Achsenbereiche über **alle** Ticks, nicht nur den gezeigten.

    Sonst atmet der Ausschnitt bei jedem Schritt der Zeitleiste, und eine
    Bewegung im Bild hieße nicht mehr «die Population verschiebt sich», sondern
    «die Achse hat sich angepasst». Genau das darf ein Leitstand nicht tun.
    """

    unten = float(frame["wtp_eur"].quantile(0.01))
    oben = float(frame["wtp_eur"].quantile(0.99))
    mitte = (unten + oben) / 2.0
    spanne = max((oben - unten) / 2.0, 1.0) * zoom
    return [mitte - spanne, mitte + spanne], [-0.05, 1.05]


def _figure(frame, tick: int, zoom: float, mode: str) -> go.Figure:
    tone = theme.palette(mode)
    ausschnitt = frame[frame["tick"] == tick]
    x_range, y_range = _ranges(frame, zoom)

    fig = go.Figure()
    for gebucht, farbe, name in (
        (False, tone["neutral"], "nicht gebucht"),
        (True, tone["positive"], "gebucht"),
    ):
        teil = ausschnitt[ausschnitt["booked"].astype(bool) == gebucht]
        fig.add_trace(
            go.Scattergl(
                x=teil["wtp_eur"],
                y=teil["environmental_awareness"],
                mode="markers",
                name=name,
                marker=dict(
                    size=7,
                    color=farbe,
                    opacity=0.62 if gebucht else 0.42,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "Zahlungsbereitschaft %{x:.0f} €<br>"
                    "Umweltbewusstsein %{y:.2f}<extra>" + name + "</extra>"
                ),
            )
        )

    theme.style_figure(
        fig,
        mode=mode,
        hovermode="closest",
        height=None,
        margin=dict(l=64, r=24, t=16, b=52),
        xaxis_title="Zahlungsbereitschaft (WTP) in €",
        yaxis_title="Umweltbewusstsein",
        legend=dict(orientation="h", y=1.04, x=0),
        uirevision="scene",
    )
    fig.update_xaxes(range=x_range)
    fig.update_yaxes(range=y_range)
    return fig


def overlay(tick: int, max_tick: int, count: int, zoom_index: int | None) -> html.Dl:
    """Die Einblendung im Viewport.

    Die Vorgabe nannte hier eine Framerate. Es wird nichts fortlaufend
    gerendert, das eine hätte — eine erfundene Zahl wäre genau die Art Zierrat,
    die dieses Produkt sich nicht leisten kann. An ihrer Stelle stehen die drei
    Angaben, die beim Betrachten der Szene wirklich fehlen: welcher Tick, wie
    viele Individuen, welcher Ausschnitt.
    """

    return html.Dl(
        [
            html.Div([html.Dt("Tick"), html.Dd(f"{tick} / {max_tick}")]),
            html.Div([html.Dt("Individuen"), html.Dd(f"{count:,}".replace(",", "."))]),
            html.Div([html.Dt("Zoom"), html.Dd(zoom_label(zoom_index))]),
        ],
        className="af-scene__overlay",
    )


def controls(zoom_index: int | None) -> html.Div:
    index = int(zoom_index or 0)
    return html.Div(
        [
            ui.icon_button(
                "zoom_out",
                "Ausschnitt vergrößern",
                id=ZOOM_OUT,
                disabled=index <= 0,
            ),
            ui.icon_button(
                "zoom_in",
                "Näher heranzoomen",
                id=ZOOM_IN,
                disabled=index >= len(ZOOM_STEPS) - 1,
            ),
        ],
        className="flex items-center gap-1",
    )


def render(
    data: RunData,
    tick: int,
    *,
    mode: str = theme.LIGHT,
    zoom_index: int | None = DEFAULT_ZOOM,
) -> html.Div:
    """Die Szene für einen Tick."""

    frame = _population(data)
    kopf = html.Div(
        [
            html.Div(
                [
                    html.H2("Population im Tick", className=ui.H2),
                    html.P(
                        "Jeder Punkt ist ein Individuum. Rechts oben liegen die, die viel "
                        "zahlen würden und umweltbewusst sind — der Konflikt, um den es geht.",
                        className=f"{ui.CAPTION} mt-1",
                    ),
                ]
            ),
            controls(zoom_index),
        ],
        className="flex items-start justify-between gap-4 mb-4",
    )

    if frame is None or frame.empty:
        return html.Div(
            [
                kopf,
                factor_strip(data.factors_at(tick)),
                _empty(
                    "Keine Agenten-History in diesem Lauf.",
                    "`individuals_history.csv` fehlt. Starten Sie links einen Lauf — "
                    "dann zeichnet die Simulation die Population je Tick auf.",
                ),
            ],
            className="p-5",
        )

    ausschnitt = frame[frame["tick"] == tick]
    figur = _figure(frame, tick, zoom_factor(zoom_index), mode)

    return html.Div(
        [
            kopf,
            factor_strip(data.factors_at(tick)),
            html.Div(
                [
                    dcc.Graph(
                        figure=figur,
                        config=theme.GRAPH_CONFIG,
                        style={"height": "clamp(22rem, 52vh, 40rem)"},
                    ),
                    overlay(tick, data.max_tick, len(ausschnitt), zoom_index),
                ],
                className="af-scene af-card p-2",
            ),
        ],
        className="p-5",
    )


def _population(data: RunData) -> Any:
    from dashboard.web import run_data

    return run_data.population(data)
