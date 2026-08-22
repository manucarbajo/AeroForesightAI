"""Tab «Übersicht»: Kennzahlen des Laufs plus Buchungsrate und Ticketpreis.

Ersetzt die matplotlib-Grafik der Streamlit-Variante durch zwei native
Plotly-Charts — gleicher Inhalt, aber mit Hover-Werten und im Markendesign.
"""

from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go
from dash import dcc, html

from dashboard.run_browser import load_price_series, load_tick_mechanics
from dashboard.web import components as ui
from dashboard.web import theme


def _metadata(run_dir: Path) -> dict:
    path = run_dir / "run_metadata.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _series(rows: list[dict], x_key: str, y_key: str) -> tuple[list, list]:
    xs: list = []
    ys: list = []
    for row in rows:
        if row.get(x_key) is None or row.get(y_key) is None:
            continue
        try:
            xs.append(int(row[x_key]))
            ys.append(float(row[y_key]))
        except (TypeError, ValueError):
            continue
    return xs, ys


def _line_chart(
    xs: list, ys: list, *, title: str, y_title: str, color: str, y_range: list | None = None
) -> dcc.Graph:
    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            name=y_title,
            hovertemplate="Tick %{x}<br>%{y:.3f}<extra></extra>",
        )
    )
    theme.style_figure(
        fig,
        title=title,
        showlegend=False,
        height=320,
        xaxis_title="Tick",
        yaxis_title=y_title,
    )
    if y_range:
        fig.update_yaxes(range=y_range)
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def render(run_dir: Path, run_id: str) -> html.Div:
    children: list = []
    metadata = _metadata(run_dir)

    if metadata:
        children.append(
            ui.grid(
                ui.metric_tile(
                    "Ticks",
                    f"{metadata.get('ticks_completed', '?')} / {metadata.get('ticks_max', '?')}",
                ),
                ui.metric_tile("Events", metadata.get("total_events", "?")),
                ui.metric_tile("Modell", metadata.get("model", "—")),
                ui.metric_tile("Markt", "an" if metadata.get("market_enabled", True) else "aus"),
                cols="sm:grid-cols-2 lg:grid-cols-4",
            )
        )
        children.append(
            html.P(
                [
                    "Run-ID: ",
                    html.Code(run_id, className="text-slate-600"),
                    f" · erstellt {metadata.get('timestamp', '—')}",
                ],
                className=f"{ui.CAPTION} mt-3",
            )
        )

    ticks = load_tick_mechanics(run_dir)
    prices = load_price_series(run_dir)
    if not ticks and not prices:
        children.append(ui.alert("Keine Zeitreihen-Daten vorhanden.", "info", class_name="mt-6"))
        return html.Div(children)

    charts: list = []
    booking_x, booking_y = _series(ticks, "tick", "booking_rate")
    if booking_x:
        charts.append(
            ui.card(
                _line_chart(
                    booking_x,
                    booking_y,
                    title="Buchungsrate",
                    y_title="Buchungsrate (0–1)",
                    color=theme.BOOKING,
                    y_range=[0, 1],
                ),
                pad=False,
                class_name="p-2",
            )
        )

    price_x, price_y = _series(prices, "round_number", "price")
    if price_x:
        charts.append(
            ui.card(
                _line_chart(
                    price_x,
                    price_y,
                    title="Ticketpreis",
                    y_title="Preis (EUR)",
                    color=theme.PRICE,
                ),
                pad=False,
                class_name="p-2",
            )
        )

    children.append(html.Div(ui.grid(*charts, cols="xl:grid-cols-2"), className="mt-6"))
    return html.Div(children)
