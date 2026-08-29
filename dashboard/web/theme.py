"""Design-Tokens der Landingpage plus die daraus abgeleiteten Plotly-Templates.

Einzige Quelle für Farben und Schriften der Dash-App. Die Rohpaletten stammen
aus `aeroforesight-ai-landing-page/design/color-tokens.json` — wird die
Landingpage neu eingefärbt, ändert sich hier eine Konstante und Charts wie UI
ziehen mit.

**Zwei Ebenen, und nur die obere wird benutzt.** Unten die Rohpaletten (`NAVY`,
`SLATE`, `INK`) — eine Sammlung von Farbwerten ohne Bedeutung. Darüber die
semantische Ebene (`PALETTE`): `surface`, `border`, `text_muted`, `accent` …,
je einmal für `light` und für `dark`. Wer eine Farbe braucht, nimmt einen
semantischen Namen; wer eine Rohfarbe direkt greift, baut den nächsten
Dark-Mode-Bruch ein, weil `SLATE[200]` auf dunklem Grund nichts Sinnvolles
bedeutet.

Dieselben Namen stehen als CSS-Variablen in `assets/dashboard.css` — dort für
alles, was sich nur per Stylesheet erreichen lässt (Dash-eigene Komponenten),
hier für alles, was Python einfärbt (Plotly, `DataTable`-Inline-Styles).
`tests/test_web_theme.py` hält beide Seiten deckungsgleich.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# --- Rohpaletten -----------------------------------------------------------
# Navy ist die Markenfarbe; Slate liefert die neutralen Grau-Töne der
# Landingpage. Ink ist die dunkle Entsprechung: tiefe Blautöne statt neutraler
# Grautöne, damit der Leitstand im Dark Mode dieselbe Markenfamilie trägt.

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

#: Die dunkle Grundfläche. Bewusst kein invertiertes Slate: reine Grautöne
#: wirken bei stundenlangem Blick auf Zeitreihen flau, ein leichter Blaustich
#: hält den Zusammenhang zur Marke und senkt den Kontrastschock am Rand.
INK = {
    950: "#080d16",  # Grundfläche der Anwendung
    900: "#0e1723",  # Karten, Panele
    850: "#13202f",  # Eingabefelder, angehobene Flächen
    800: "#1a2b3d",  # Hover, eingelassene Flächen
    700: "#23384d",  # Rahmen
    600: "#31485f",  # betonter Rahmen
    500: "#54708c",
    400: "#8ba0b7",  # gedämpfter Text
    300: "#b8c7d7",
    200: "#d5dfea",
    100: "#e8eff6",  # Fließtext
    50: "#f4f8fc",  # Überschriften
}

PRIMARY = NAVY[800]
RADIUS = "0.5rem"

FONT_HEADLINE = "Plus Jakarta Sans, sans-serif"
FONT_BODY = "Inter, sans-serif"
FONT_MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'

LIGHT = "light"
DARK = "dark"
MODES = (LIGHT, DARK)

# --- Semantische Ebene -----------------------------------------------------
# Gedeckte Töne statt Signalfarben — die Zahlen sollen wissenschaftlich wirken,
# nicht alarmieren. Im Dark Mode sind dieselben Rollen heller angesetzt: die
# hellen Töne (teal-700, rose-800) verschwinden auf dunklem Grund.

PALETTE: dict[str, dict[str, str]] = {
    LIGHT: {
        # Flächen
        "canvas": SLATE[50],
        "surface": "#ffffff",
        "surface-raised": "#ffffff",
        "surface-sunken": SLATE[50],
        "surface-inset": SLATE[100],
        "surface-hover": SLATE[50],
        "overlay": "rgba(255, 255, 255, 0.88)",
        "scrim": "rgba(15, 23, 42, 0.35)",
        # Rahmen
        "border": SLATE[200],
        "border-subtle": SLATE[100],
        "border-strong": SLATE[300],
        # Schrift
        "text": SLATE[900],
        "text-body": SLATE[700],
        "text-muted": SLATE[500],
        "text-faint": SLATE[400],
        "text-inverted": "#ffffff",
        # Marke
        "accent": NAVY[800],
        "accent-hover": NAVY[700],
        "accent-soft": NAVY[50],
        "accent-border": NAVY[200],
        "accent-text": NAVY[900],
        "focus-ring": "rgba(62, 118, 166, 0.25)",
        # Rollen
        "positive": "#0f766e",
        "positive-soft": "#f0fdfa",
        "positive-border": "#99f6e4",
        "positive-text": "#115e59",
        "negative": "#9f1239",
        "negative-soft": "#fff1f2",
        "negative-border": "#fecdd3",
        "negative-text": "#9f1239",
        "warning": "#b45309",
        "warning-soft": "#fffbeb",
        "warning-border": "#fde68a",
        "warning-text": "#92400e",
        # Der Demo-Datensatz trägt eine eigene Farbe, die sonst nirgends
        # vorkommt — Platzhalter dürfen mit nichts verwechselbar sein.
        "demo": "#7c3aed",
        "demo-soft": "#f5f3ff",
        "demo-border": "#ddd6fe",
        "demo-text": "#5b21b6",
        # Diagramme
        "grid": SLATE[200],
        "axis": SLATE[300],
        "plot-bg": "#ffffff",
        "paper-bg": "#ffffff",
        "price": "#0f766e",
        "booking": NAVY[500],
        "neutral": SLATE[500],
        # Konsole. Sie ist in **beiden** Modi dunkel — eine Konsole auf weiss
        # ist keine. Deshalb tragen ihre Stufen hier dieselben hellen Toene wie
        # im Dark Mode: `warning` in der hellen Fassung (#b45309) kaeme auf
        # Navy-950 nur auf ein Kontrastverhaeltnis von 3,2 und waere zu lesen
        # muehsam. Am laufenden System nachgemessen.
        "console-bg": NAVY[950],
        "console-text": NAVY[100],
        "console-info": NAVY[300],
        "console-warning": "#fbbf24",
        "console-error": "#fb7185",
    },
    DARK: {
        "canvas": INK[950],
        "surface": INK[900],
        "surface-raised": INK[850],
        "surface-sunken": INK[950],
        "surface-inset": INK[800],
        "surface-hover": INK[800],
        "overlay": "rgba(14, 23, 35, 0.88)",
        "scrim": "rgba(0, 0, 0, 0.55)",
        "border": INK[700],
        "border-subtle": INK[800],
        "border-strong": INK[600],
        "text": INK[50],
        "text-body": INK[100],
        "text-muted": INK[400],
        "text-faint": INK[500],
        "text-inverted": INK[950],
        "accent": NAVY[300],
        "accent-hover": NAVY[200],
        "accent-soft": "#15293f",
        "accent-border": NAVY[600],
        "accent-text": NAVY[100],
        "focus-ring": "rgba(148, 184, 215, 0.28)",
        "positive": "#2dd4bf",
        "positive-soft": "#0c2b2b",
        "positive-border": "#1d5450",
        "positive-text": "#7ff0e0",
        "negative": "#fb7185",
        "negative-soft": "#2e1520",
        "negative-border": "#66273a",
        "negative-text": "#fda4b0",
        "warning": "#fbbf24",
        "warning-soft": "#2c2110",
        "warning-border": "#5c4517",
        "warning-text": "#fcd34d",
        "demo": "#a78bfa",
        "demo-soft": "#231a3c",
        "demo-border": "#4c3a80",
        "demo-text": "#c9b8fd",
        "grid": INK[800],
        "axis": INK[700],
        "plot-bg": INK[900],
        "paper-bg": INK[900],
        "price": "#2dd4bf",
        "booking": NAVY[300],
        "neutral": INK[400],
        "console-bg": INK[950],
        "console-text": INK[200],
        "console-info": NAVY[300],
        "console-warning": "#fbbf24",
        "console-error": "#fb7185",
    },
}


def normalise(mode: str | None) -> str:
    """Ein beliebiger Eingabewert wird zu genau einem der beiden Modi.

    Der Wert kommt aus einem `dcc.Store`, den ein Skript im Browser füllt —
    also aus einer Quelle, die auch `None` oder Unsinn liefern kann. Statt an
    jeder Aufrufstelle zu prüfen, prüft diese Funktion.
    """

    return DARK if str(mode or "").lower() == DARK else LIGHT


def palette(mode: str | None = LIGHT) -> dict[str, str]:
    """Die semantischen Farben eines Modus."""

    return PALETTE[normalise(mode)]


def color(name: str, mode: str | None = LIGHT) -> str:
    """Eine einzelne semantische Farbe."""

    return palette(mode)[name]


# --- Rückwärtskompatible Kurznamen -----------------------------------------
# Die Light-Werte der wichtigsten Rollen. Neuer Code nimmt `palette(mode)`;
# diese Namen bleiben, damit bestehende Aufrufer nicht in einem Zug mitziehen
# müssen — sie sind per Definition der helle Fall.

POSITIVE = PALETTE[LIGHT]["positive"]
NEGATIVE = PALETTE[LIGHT]["negative"]
WARNING = PALETTE[LIGHT]["warning"]
PRICE = PALETTE[LIGHT]["price"]
BOOKING = PALETTE[LIGHT]["booking"]
NEUTRAL = PALETTE[LIGHT]["neutral"]

#: Kategorien-Reihenfolge für Serien ohne eigene Bedeutung. Alle Töne tragen
#: denselben Helligkeitseindruck, damit keine Serie unabsichtlich hervorsticht.
COLORWAYS = {
    LIGHT: [
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
    ],
    DARK: [
        NAVY[300],
        "#2dd4bf",
        "#fbbf24",
        "#93c5fd",
        "#fb7185",
        "#a3e635",
        NAVY[400],
        INK[400],
        "#a78bfa",
        "#e0eaf3",
    ],
}
COLORWAY = COLORWAYS[LIGHT]

TEMPLATE_NAMES = {LIGHT: "aeroforesight", DARK: "aeroforesight_dark"}
TEMPLATE_NAME = TEMPLATE_NAMES[LIGHT]


def template_for(mode: str | None = LIGHT) -> str:
    """Der Name des Plotly-Templates für einen Modus."""

    return TEMPLATE_NAMES[normalise(mode)]


def _build_template(mode: str) -> go.layout.Template:
    tone = PALETTE[mode]
    axis = dict(
        gridcolor=tone["grid"],
        linecolor=tone["axis"],
        zerolinecolor=tone["grid"],
        tickfont=dict(family=FONT_BODY, size=12, color=tone["text-muted"]),
        title=dict(font=dict(family=FONT_BODY, size=12, color=tone["text-body"])),
        showline=False,
        ticks="outside",
        tickcolor=tone["grid"],
        ticklen=4,
    )
    return go.layout.Template(
        layout=go.Layout(
            colorway=COLORWAYS[mode],
            paper_bgcolor=tone["paper-bg"],
            plot_bgcolor=tone["plot-bg"],
            font=dict(family=FONT_BODY, size=13, color=tone["text-body"]),
            title=dict(
                font=dict(family=FONT_HEADLINE, size=16, color=tone["text"]),
                x=0,
                xanchor="left",
                pad=dict(b=12),
            ),
            margin=dict(l=56, r=24, t=56, b=48),
            hoverlabel=dict(
                bgcolor=tone["surface-raised"],
                bordercolor=tone["border"],
                font=dict(family=FONT_BODY, size=12, color=tone["text"]),
            ),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(family=FONT_BODY, size=12, color=tone["text-muted"]),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            xaxis=axis,
            yaxis=axis,
            colorscale=dict(
                sequential=(
                    [[0.0, NAVY[50]], [1.0, NAVY[800]]]
                    if mode == LIGHT
                    else [[0.0, INK[850]], [1.0, NAVY[300]]]
                )
            ),
        )
    )


def register_template() -> None:
    """Beide Templates registrieren und das helle als Standard setzen (idempotent).

    Der Standard bleibt hell, weil serverseitig erzeugte Figuren ohne
    ausdrückliche Angabe irgendwo landen müssen — welcher Modus im Browser
    gilt, weiß erst der Callback, der `style_figure(..., mode=…)` ruft.
    """

    for mode, name in TEMPLATE_NAMES.items():
        if name not in pio.templates:
            pio.templates[name] = _build_template(mode)
    pio.templates.default = TEMPLATE_NAMES[LIGHT]


def style_figure(fig: go.Figure, *, mode: str | None = LIGHT, **layout: object) -> go.Figure:
    """Template anwenden und die üblichen Layout-Vorgaben setzen.

    Charts, die über ``plotly.express`` entstehen, tragen das Default-Template
    bereits; dieser Helfer vereinheitlicht zusätzlich Hover-Modus und Höhe und
    nimmt beliebige Layout-Overrides entgegen.
    """

    layout.setdefault("hovermode", "x unified")
    fig.update_layout(template=template_for(mode), **layout)
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


def css_variables(mode: str) -> str:
    """Die semantische Ebene als CSS-Variablenblock.

    Wird von `tests/test_web_theme.py` gegen `assets/dashboard.css` gehalten:
    Python und Stylesheet färben dieselben Flächen, und sie dürfen nicht
    auseinanderlaufen. Der Test vergleicht die Namen, nicht die Formatierung.
    """

    return "\n".join(f"    --{name}: {value};" for name, value in PALETTE[mode].items())
