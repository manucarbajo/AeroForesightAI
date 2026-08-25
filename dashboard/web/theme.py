"""Design-Tokens der Landingpage plus das daraus abgeleitete Plotly-Template.

Einzige Quelle für Farben und Schriften der Dash-App. Die Werte stammen aus
`aeroforesight-ai-landing-page/design/color-tokens.json` — wird die Landingpage
neu eingefärbt, ändert sich hier eine Konstante und Charts wie UI ziehen mit.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# --- Farbskalen ------------------------------------------------------------
# Navy ist die Markenfarbe; Slate liefert die neutralen Grau-Töne, die die
# Landingpage über Tailwind bezieht (text-slate-600, border-slate-200, …).

NAVY = {
    50: "#f0f4f9",
    100: "#e0eaf3",
    200: "#c2d5e7",
    300: "#94b8d7",
    400: "#6094c1",
    500: "#3e76a6",
    600: "#2d5e8a",
    700: "#244b70",
    800: "#1E3A5F",  # Primary
    900: "#1c3453",
    950: "#122238",
}

SLATE = {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
}

PRIMARY = NAVY[800]
RADIUS = "0.5rem"

FONT_HEADLINE = "Plus Jakarta Sans, sans-serif"
FONT_BODY = "Inter, sans-serif"

# --- Semantische Rollen ----------------------------------------------------
# Ersetzt die Ad-hoc-Farben der Streamlit-Variante (#2563eb, #059669,
# "green"/"red"). Gedeckte Töne statt Signalfarben — die Zahlen sollen
# wissenschaftlich wirken, nicht alarmieren.

POSITIVE = "#0f766e"  # teal-700  — gebucht, Erfolg
NEGATIVE = "#9f1239"  # rose-800  — nicht gebucht, Fehler
WARNING = "#b45309"  # amber-700 — Hinweis
PRICE = "#0f766e"
BOOKING = NAVY[500]
NEUTRAL = SLATE[500]

#: Kategorien-Reihenfolge für Serien ohne eigene Bedeutung. Alle Töne sind
#: gedeckt und tragen denselben Helligkeitseindruck, damit keine Serie
#: unabsichtlich hervorsticht.
COLORWAY = [
    NAVY[800],
    "#0f766e",
    "#b45309",
    NAVY[400],
    "#9f1239",
    "#4d7c0f",
    NAVY[600],
    SLATE[500],
    "#7c3aed",
    NAVY[300],
]

TEMPLATE_NAME = "aeroforesight"


def _build_template() -> go.layout.Template:
    axis = dict(
        gridcolor=SLATE[200],
        linecolor=SLATE[300],
        zerolinecolor=SLATE[200],
        tickfont=dict(family=FONT_BODY, size=12, color=SLATE[500]),
        title=dict(font=dict(family=FONT_BODY, size=12, color=SLATE[600])),
        showline=False,
        ticks="outside",
        tickcolor=SLATE[200],
        ticklen=4,
    )
    return go.layout.Template(
        layout=go.Layout(
            colorway=COLORWAY,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(family=FONT_BODY, size=13, color=SLATE[700]),
            title=dict(
                font=dict(family=FONT_HEADLINE, size=16, color=SLATE[900]),
                x=0,
                xanchor="left",
                pad=dict(b=12),
            ),
            margin=dict(l=56, r=24, t=56, b=48),
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=SLATE[200],
                font=dict(family=FONT_BODY, size=12, color=SLATE[800]),
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(family=FONT_BODY, size=12, color=SLATE[600]),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            xaxis=axis,
            yaxis=axis,
            colorscale=dict(sequential=[[0.0, NAVY[50]], [1.0, NAVY[800]]]),
        )
    )


def register_template() -> None:
    """Template registrieren und als Standard setzen (idempotent)."""

    if TEMPLATE_NAME not in pio.templates:
        pio.templates[TEMPLATE_NAME] = _build_template()
    pio.templates.default = TEMPLATE_NAME


def style_figure(fig: go.Figure, **layout: object) -> go.Figure:
    """Template anwenden und die üblichen Layout-Vorgaben setzen.

    Charts, die über ``plotly.express`` entstehen, tragen das Default-Template
    bereits; dieser Helfer vereinheitlicht zusätzlich Hover-Modus und Höhe und
    nimmt beliebige Layout-Overrides entgegen.
    """

    fig.update_layout(template=TEMPLATE_NAME, hovermode="x unified", **layout)
    return fig


def slow_animation(fig: go.Figure, duration: int = 500) -> go.Figure:
    """Play-Button einer Animation auf ruhige, gleichmäßige Übergänge stellen.

    Übernimmt das Verhalten aus der Streamlit-Variante: 500 ms pro Frame,
    lineares Easing, kein Redraw — sonst ruckelt der Scatter sichtbar.
    """

    if not fig.layout.updatemenus:
        return fig
    args = fig.layout.updatemenus[0].buttons[0].args[1]
    args["frame"]["duration"] = duration
    args["frame"]["redraw"] = False
    args["transition"]["duration"] = duration
    args["transition"]["easing"] = "linear"
    return fig


#: Modebar-Konfiguration für alle ``dcc.Graph``. Die Logo-Schaltfläche und die
#: Auswahl-Werkzeuge stören im Präsentationsbetrieb mehr als sie nutzen.
GRAPH_CONFIG = {
    "displaylogo": False,
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "responsive": True,
}
