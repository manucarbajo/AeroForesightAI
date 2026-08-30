"""Tab «Figures»: wissenschaftliche Auswertungen des Laufs.

Sechs thematische Ansichten auf die Zeitreihen unter `timeseries/` plus die
exportierten PNGs aus `figures/`. Die sechs Live-Ansichten stammen aus der
Forschungs-Variante, der PNG-Export aus der Ops-Variante der alten App — hier
liegen sie erstmals nebeneinander.
"""

from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html, no_update
from plotly.subplots import make_subplots

from dashboard import run_browser
from dashboard.run_browser import generate_figures_for_run, list_run_figures
from dashboard.web import components as ui
from dashboard.web import theme
from dashboard.web.files_route import run_file_url

TABS = [
    ("1 · Yield & Markt", "yield"),
    ("2 · Segmente & Alter", "segments"),
    ("3 · Policies & Steuern", "policies"),
    ("4 · Makro-Wirtschaft", "macro"),
    ("5 · Airline-Kosten", "costs"),
    ("6 · CIB-Faktoren", "cib"),
    ("PNG-Export", "png"),
]

POLICY_COLUMNS = ["carbon_tax_level", "saf_mandate_share", "efuel_subsidy", "airport_fee"]
ABSOLUTE_POLICY_COLUMNS = {"carbon_tax_level", "airport_fee"}
MACRO_COLUMNS = [
    "income_index",
    "bevoelkerungsentwicklung",
    "demand_growth_rate",
    "oil_price_index",
]
COST_COLUMNS = ["maintenance_cost_index", "staff_cost_index", "fuel_price_change"]


# --- Datenzugriff ----------------------------------------------------------


def _read_csv(path: Path):
    import pandas as pd

    if not path.is_file():
        return None
    try:
        return pd.read_csv(path)
    except Exception:  # noqa: BLE001 - fehlerhafte Datei = keine Daten
        return None


def _read_ticks(run_dir: Path):
    import pandas as pd

    path = run_dir / "tick_mechanics.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rows = payload.get("ticks")
    return pd.DataFrame(rows) if rows else None


def _graph(fig, height: int = 420, *, mode: str = theme.LIGHT) -> dcc.Graph:
    theme.style_figure(fig, height=height, mode=mode)
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def _panel(*children) -> html.Div:
    return html.Div(list(children))


# --- Einzelansichten -------------------------------------------------------


def _view_yield(run_dir: Path, mode: str = theme.LIGHT):
    ticks = _read_ticks(run_dir)
    if ticks is None:
        return ui.alert("Keine Marktdaten verfügbar.", "info")

    price = ticks.get("market_price_after_feedback_eur")
    if price is None:
        price = ticks.get("ticket_price")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=ticks["tick"],
            y=price,
            name="Ticketpreis (EUR)",
            line=dict(color=theme.PRICE, width=2.5),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=ticks["tick"],
            y=ticks["booking_rate"],
            name="Buchungsrate",
            line=dict(color=theme.BOOKING, dash="dot", width=2.5),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Ticketpreis (EUR)", secondary_y=False)
    fig.update_yaxes(title_text="Buchungsrate (0–1)", range=[0, 1.05], secondary_y=True)
    fig.update_xaxes(title_text="Tick")
    blocks = [
        html.H3("Angebot vs. Nachfrage", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(
                theme.style_figure(fig, mode=mode, title="Markt-Rückkopplung (Yield Management)"),
                mode=mode,
            ),
            pad=False,
            class_name="p-2 mb-6",
        ),
    ]

    if "cost_pressure" in ticks.columns and "provider_markup" in ticks.columns:
        margin = go.Figure()
        margin.add_trace(
            go.Bar(
                x=ticks["tick"],
                y=ticks["cost_pressure"],
                name="Kostendruck (Base)",
                marker_color=theme.NAVY[800],
            )
        )
        margin.add_trace(
            go.Bar(
                x=ticks["tick"],
                y=ticks["provider_markup"],
                name="Airline-Marge (Markup)",
                marker_color=theme.NAVY[300],
            )
        )
        margin.update_xaxes(title_text="Tick")
        blocks.append(
            ui.card(
                _graph(
                    theme.style_figure(
                        margin, mode=mode, barmode="stack", title="Preis-Zusammensetzung"
                    ),
                    mode=mode,
                ),
                pad=False,
                class_name="p-2",
            )
        )
    return _panel(*blocks)


def _booking_rate_lines(frame, group_column: str, title: str, mode: str = theme.LIGHT):
    fig = go.Figure()
    for value in frame[group_column].unique():
        subset = frame[frame[group_column] == value]
        fig.add_trace(
            go.Scatter(
                x=subset["tick"],
                y=subset["booking_rate"],
                mode="lines+markers",
                name=str(value).replace("_", " ").title(),
            )
        )
    theme.style_figure(
        fig,
        mode=mode,
        title=title,
        xaxis_title="Tick",
        yaxis_title="Buchungsrate",
        yaxis_range=[0, 1.05],
    )
    return fig


def _view_segments(run_dir: Path, mode: str = theme.LIGHT):
    population = _read_csv(run_dir / "timeseries" / "population.csv")
    ages = _read_csv(run_dir / "timeseries" / "age_property.csv")

    left = (
        ui.card(
            _graph(
                _booking_rate_lines(
                    population, "segment_id", "Buchungsrate nach Profil-Segment", mode
                ),
                mode=mode,
            ),
            pad=False,
            class_name="p-2",
        )
        if population is not None and not population.empty
        else ui.alert("Keine Profil-Segment-Daten.", "info")
    )
    right = (
        ui.card(
            _graph(
                _booking_rate_lines(ages, "age_group", "Buchungsrate nach Altersgruppe", mode),
                mode=mode,
            ),
            pad=False,
            class_name="p-2",
        )
        if ages is not None and not ages.empty
        else ui.alert("Keine Altersgruppen-Daten.", "info")
    )
    return _panel(
        html.H3("Mikro-Verhalten", className=f"{ui.H3} mb-3"),
        ui.grid(left, right, cols="xl:grid-cols-2"),
    )


def _view_policies(run_dir: Path, mode: str = theme.LIGHT):
    properties = _read_csv(run_dir / "timeseries" / "properties.csv")
    if properties is None:
        return ui.alert("Keine Property-Zeitreihen vorhanden.", "info")

    columns = [c for c in properties.columns if c in POLICY_COLUMNS]
    if not columns:
        return ui.alert("Keine Policy-Properties gefunden.", "info")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for column in columns:
        fig.add_trace(
            go.Scatter(x=properties["tick"], y=properties[column], name=column),
            secondary_y=column not in ABSOLUTE_POLICY_COLUMNS,
        )
    fig.update_yaxes(title_text="Betrag (EUR/t o. ä.)", secondary_y=False)
    fig.update_yaxes(title_text="Anteil (0–1)", secondary_y=True)
    fig.update_xaxes(title_text="Tick")
    return _panel(
        html.H3("Politik & Steuern (exogen)", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(theme.style_figure(fig, mode=mode, title="Politische Instrumente"), mode=mode),
            pad=False,
            class_name="p-2",
        ),
    )


def _view_macro(run_dir: Path, mode: str = theme.LIGHT):
    properties = _read_csv(run_dir / "timeseries" / "properties.csv")
    if properties is None:
        return ui.alert("Keine Property-Zeitreihen vorhanden.", "info")

    columns = [c for c in properties.columns if c in MACRO_COLUMNS]
    if not columns:
        return ui.alert("Keine makroökonomischen Properties gefunden.", "info")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for column in columns:
        fig.add_trace(
            go.Scatter(x=properties["tick"], y=properties[column], name=column),
            secondary_y=column == "bevoelkerungsentwicklung",
        )
    fig.update_yaxes(title_text="Index (1.0 = Basis)", secondary_y=False)
    fig.update_yaxes(title_text="Population", secondary_y=True)
    fig.update_xaxes(title_text="Tick")
    return _panel(
        html.H3("Makroökonomische Indizes", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(theme.style_figure(fig, mode=mode, title="Wirtschaft & Demographie"), mode=mode),
            pad=False,
            class_name="p-2",
        ),
    )


def _view_costs(run_dir: Path, mode: str = theme.LIGHT):
    properties = _read_csv(run_dir / "timeseries" / "properties.csv")
    if properties is None:
        return ui.alert("Keine Property-Zeitreihen vorhanden.", "info")

    columns = [c for c in properties.columns if c in COST_COLUMNS]
    if not columns:
        return ui.alert("Keine Kosten-Properties gefunden.", "info")

    fig = go.Figure()
    for column in columns:
        fig.add_trace(go.Scatter(x=properties["tick"], y=properties[column], name=column))
    fig.update_xaxes(title_text="Tick")
    return _panel(
        html.H3("Kostenstruktur der Anbieter", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(theme.style_figure(fig, mode=mode, title="Airline-Kosten-Indizes"), mode=mode),
            pad=False,
            class_name="p-2",
        ),
    )


def _factor_to_number(value) -> float:
    """«F3.2» → 3.2, damit sich Zustandswechsel als Treppenlinie zeichnen lassen."""

    if isinstance(value, str) and value.startswith("F"):
        try:
            major, minor = value[1:].split(".")
            return float(major) + float(minor) * 0.1
        except (ValueError, IndexError):
            pass
    return 0.0


def _view_cib(run_dir: Path, mode: str = theme.LIGHT):
    factors = _read_csv(run_dir / "timeseries" / "factors.csv")
    if factors is None or factors.empty:
        return ui.alert("Keine Faktoren-Daten verfügbar.", "info")

    numeric = factors.copy()
    for column in numeric.columns:
        if column != "tick":
            numeric[column] = numeric[column].apply(_factor_to_number)

    fig = go.Figure()
    for column in [c for c in numeric.columns if c != "tick"]:
        fig.add_trace(
            go.Scatter(
                x=numeric["tick"],
                y=numeric[column],
                mode="lines",
                name=column,
                line_shape="hv",
            )
        )
    fig.update_xaxes(title_text="Tick")
    fig.update_yaxes(title_text="Faktor-Zustand")
    return _panel(
        html.H3("CIB-Faktoren F1–F7", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(
                theme.style_figure(fig, mode=mode, title="Faktoren (Zustands-Trajektorien)"),
                mode=mode,
            ),
            pad=False,
            class_name="p-2",
        ),
    )


def _satz_hinweis(figures) -> object:
    """Was an diesem Bildersatz nicht stimmt — oder nichts (P1.2).

    Zwei Zustände sahen bis zum 2026-08-30 aus wie ein vollständiger Satz: einer
    **ohne Manifest**, dessen Titel aus Dateinamen geraten sind, und einer, in
    dem das Manifest Dateien nennt, die es nicht gibt — die wurden still
    übersprungen. Beide bekommen jetzt einen Satz darüber.
    """

    if figures.herkunft == run_browser.GERATEN:
        return ui.alert(
            "Zu diesen Bildern gibt es kein Manifest. Die Titel sind aus den "
            "Dateinamen abgeleitet, und ob der Satz vollständig ist, lässt sich "
            "nicht sagen. «Figures neu erzeugen» stellt einen benannten Satz her.",
            "warning",
        )
    if figures.fehlend:
        fehlt = ", ".join(figures.fehlend)
        return ui.alert(
            f"Das Manifest nennt {len(figures.fehlend)} Bild(er), die nicht "
            f"vorliegen: {fehlt}. Der Satz ist unvollständig.",
            "warning",
        )
    return None


def png_gallery(run_dir: Path) -> html.Div:
    figures = list_run_figures(run_dir)
    if not figures:
        return ui.empty_state(
            "Noch keine PNG-Figures für diesen Run.",
            hint="Aktivieren Sie «Figures nach Lauf erzeugen» beim Start oder klicken Sie "
            "oben auf «Figures neu erzeugen».",
            icon_name="image",
        )

    cards = []
    hinweis = _satz_hinweis(figures)
    if hinweis is not None:
        cards.append(html.Div(hinweis, className="mb-4"))
    for figure in figures:
        url = run_file_url(figure.absolute_path)
        cards.append(
            ui.card(
                html.H3(figure.title, className=f"{ui.H3} mb-3"),
                (
                    html.Div(html.Img(src=url, className="w-full rounded"), className="af-paper")
                    if url
                    else ui.alert("Datei liegt außerhalb des Outputs-Verzeichnisses.", "warning")
                ),
                class_name="mb-4",
            )
        )
    return html.Div(cards)


def _view_png(run_dir: Path, mode: str = theme.LIGHT):
    return _panel(
        html.Div(
            [
                html.P(
                    ["Speicherort: ", html.Code(str(run_dir / "figures"))],
                    className=f"{ui.CAPTION} break-all",
                ),
                ui.button(
                    "Figures neu erzeugen",
                    id="figures-regenerate-btn",
                    variant="secondary",
                    icon_name="refresh",
                ),
            ],
            className="flex items-center justify-between gap-4 flex-wrap mb-4",
        ),
        html.Div(id="figures-png-status"),
        dcc.Loading(
            html.Div(png_gallery(run_dir), id="figures-png-gallery"),
            type="dot",
            color=theme.palette(mode)["accent"],
        ),
    )


_VIEWS = {
    "yield": _view_yield,
    "segments": _view_segments,
    "policies": _view_policies,
    "macro": _view_macro,
    "costs": _view_costs,
    "cib": _view_cib,
    "png": _view_png,
}


DEFAULT_TAB = "yield"


def _render_view(tab: str | None, run_dir: Path, mode: str = theme.LIGHT):
    view = _VIEWS.get(tab or DEFAULT_TAB, _view_yield)
    try:
        return view(run_dir, mode)
    except Exception as exc:  # noqa: BLE001 - unvollständige Runs kommen vor
        return ui.alert(f"Auswertung fehlgeschlagen: {exc}", "error")


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    return html.Div(
        [
            ui.tabs("figures-tabs", TABS, value=DEFAULT_TAB),
            html.Div(_render_view(DEFAULT_TAB, run_dir, mode), id="figures-tab-content"),
        ],
        className="af-tabs--sub",
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("figures-tab-content", "children"),
        Input("figures-tabs", "value"),
        State("selected-run-store", "data"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def _render_tab(tab: str | None, selected: dict | None, mode: str | None):
        if not selected:
            return no_update
        return _render_view(tab, Path(selected["run_dir"]), theme.normalise(mode))

    @app.callback(
        Output("figures-png-gallery", "children"),
        Output("figures-png-status", "children"),
        Input("figures-regenerate-btn", "n_clicks"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _regenerate(n_clicks: int | None, selected: dict | None):
        if not n_clicks or not selected:
            return no_update, no_update
        run_dir = Path(selected["run_dir"])
        try:
            figures = generate_figures_for_run(run_dir)
        except Exception as exc:  # noqa: BLE001 - matplotlib-Fehler gehören in die UI
            return no_update, ui.alert(f"Figure-Erzeugung fehlgeschlagen: {exc}", "error")
        return png_gallery(run_dir), ui.alert(f"{len(figures)} Figures erzeugt.", "success")
