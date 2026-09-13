"""Die rechte Zone: Kennzahlen, Verläufe und Konsole.

Drei Ebenen derselben Sache, von grob nach fein. Oben die Kennzahlen des
gescrubbten Ticks — was gerade gilt. Darunter die Verläufe mit einer Marke an
derselben Stelle — wo das im Lauf liegt. Unten die Konsole — was währenddessen
passiert ist.

**Alle drei folgen der Zeitleiste.** Eine Kennzahl, die den letzten Tick zeigt,
während die Szene den fünfzehnten zeigt, wäre schlimmer als keine: Man würde
sie lesen und zusammenrechnen.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web import theme
from dashboard.web.run_data import RunData

#: Wie viele Konsolenzeilen höchstens dargestellt werden. Bei 300 lagen bei
#: einem 40-Tick-Lauf schon 254 Zeilen gleichzeitig im DOM einer Seitenspalte —
#: gemessen, nicht geschätzt. Die Konsole ist ein Nachschlagewerk; wer weiter
#: zurück muss, nimmt `event_log.json` unter «Dateien».
MAX_CONSOLE_LINES = 80

#: Welche Ereignisquelle welche Stufe trägt. Der Regulator setzt Politik, das
#: ist die einzige Quelle, die im Normalbetrieb hervorstechen soll.
_EVENT_LEVELS = {
    "market": "muted",
    "regulator": "info",
    "provider": "info",
    "consumer": "info",
}


# --- Kennzahlen ------------------------------------------------------------


def _delta(value: Any, *, digits: int = 2, suffix: str = "") -> tuple[str | None, str | None]:
    """Veränderung als Text und Richtung — oder zweimal `None`.

    Die Richtung färbt nur die Veränderung, nicht den Wert: Ob ein steigender
    Preis gut oder schlecht ist, entscheidet die Fragestellung.
    """

    if value is None:
        return None, None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, None
    if abs(number) < 10**-digits / 2:
        return f"±0{suffix}", None
    zeichen = "+" if number > 0 else "−"
    return f"{zeichen}{abs(number):.{digits}f}{suffix}", ("up" if number > 0 else "down")


def _number(row: dict, key: str) -> float | None:
    try:
        value = row.get(key)
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def kpi_row(data: RunData, tick: int) -> html.Div:
    """Die vier Kennzahlen des gewählten Ticks."""

    row = data.tick_row(tick)
    if not row:
        return ui.hinweis(
            "Für diesen Tick liegen keine Kennzahlen vor (`tick_mechanics.json` fehlt "
            "oder reicht nicht so weit).",
            "info",
        )

    rate = _number(row, "booking_rate")
    preis = _number(row, "market_price_after_feedback_eur")
    kosten = _number(row, "cost_pressure_eur")
    nachfrage = _number(row, "demand_level")

    raten_delta, raten_richtung = _delta(row.get("booking_rate_delta"), digits=3)
    preis_delta, preis_richtung = _delta(row.get("market_price_delta_eur"), suffix=" €")

    return ui.grid(
        ui.kachel(
            "Buchungsrate",
            "—" if rate is None else f"{rate:.1%}",
            variante="kompakt",
            delta=raten_delta,
            direction=raten_richtung,
            hint=None if row.get("booked") is None else f"{row['booked']} Buchungen",
        ),
        ui.kachel(
            "Ticketpreis",
            "—" if preis is None else f"{preis:.2f} €",
            variante="kompakt",
            delta=preis_delta,
            direction=preis_richtung,
        ),
        ui.kachel(
            "Kostendruck",
            "—" if kosten is None else f"{kosten:.2f} €",
            variante="kompakt",
            hint=(
                None
                if row.get("carbon_tax_level") is None
                else f"CO₂-Abgabe {float(row['carbon_tax_level']):.0f} €/t"
            ),
        ),
        ui.kachel(
            "Nachfrageniveau",
            "—" if nachfrage is None else f"{nachfrage:.2f}",
            variante="kompakt",
            hint=None if row.get("population") is None else f"{row['population']} Personen",
        ),
        # Einspaltig: In einer rund 20 rem breiten Zone blieben je Karte 146 px,
        # und die Zahl — das Einzige, was hier zählt — wurde zur Nebensache.
        cols="grid-cols-1",
        gap="gap-2",
    )


# --- Verläufe --------------------------------------------------------------


def _sparkline(
    xs: list, ys: list, tick: int, *, title: str, color: str, mode: str, percent: bool = False
) -> dcc.Graph:
    """Ein Verlauf auf kleiner Fläche, mit Marke am aktuellen Tick.

    Bewusst ohne Achsentitel und Legende: Auf 20 rem Breite kostet jede
    Beschriftung mehr Platz, als sie an Auskunft bringt. Die Zahl selbst steht
    darüber in der Kennzahlenkarte.
    """

    tone = theme.palette(mode)
    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=("Tick %{x}<br>%{y:.1%}" if percent else "Tick %{x}<br>%{y:.2f}")
            + "<extra></extra>",
        )
    )
    if tick in xs:
        index = xs.index(tick)
        fig.add_trace(
            go.Scatter(
                x=[tick],
                y=[ys[index]],
                mode="markers",
                marker=dict(size=8, color=color, line=dict(width=2, color=tone["surface"])),
                hoverinfo="skip",
            )
        )
        fig.add_vline(x=tick, line=dict(color=tone["border-strong"], width=1, dash="dot"))

    theme.style_figure(
        fig,
        mode=mode,
        title=dict(text=title, font=dict(size=12)),
        height=110,
        showlegend=False,
        margin=dict(l=36, r=8, t=28, b=20),
        hovermode="x",
    )
    fig.update_xaxes(showgrid=False, title_text=None)
    fig.update_yaxes(title_text=None, tickformat=".0%" if percent else None, nticks=3)
    return dcc.Graph(figure=fig, config={**theme.GRAPH_CONFIG, "displayModeBar": False})


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


def charts(data: RunData, tick: int, *, mode: str = theme.LIGHT) -> html.Div:
    tone = theme.palette(mode)
    blocks: list = []

    booking_x, booking_y = _series(data.ticks, "tick", "booking_rate")
    if booking_x:
        blocks.append(
            _sparkline(
                booking_x,
                booking_y,
                tick,
                title="Buchungsrate",
                color=tone["booking"],
                mode=mode,
                percent=True,
            )
        )

    price_x, price_y = _series(data.prices, "round_number", "price")
    if price_x:
        blocks.append(
            _sparkline(
                price_x, price_y, tick, title="Ticketpreis (€)", color=tone["price"], mode=mode
            )
        )

    cost_x, cost_y = _series(data.ticks, "tick", "cost_pressure_eur")
    if cost_x:
        blocks.append(
            _sparkline(
                cost_x, cost_y, tick, title="Kostendruck (€)", color=tone["warning"], mode=mode
            )
        )

    if not blocks:
        return ui.hinweis("Keine Zeitreihen in diesem Lauf.", "info")
    return html.Div(blocks, className="space-y-1")


# --- Konsole ---------------------------------------------------------------


def _incidents(data: RunData) -> list[dict[str, Any]]:
    """Ausgefallene LLM-Aufrufe aus `llm_incidents.json` (P0.1)."""

    if data.run_dir is None:
        return []
    path: Path = data.run_dir / "llm_incidents.json"
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return payload if isinstance(payload, list) else []


def console_lines(
    data: RunData, *, progress: list[str] | None = None, error: str | None = None
) -> list[Any]:
    """Was in der Konsole steht — Fortschritt zuoberst, dann Vorfälle, dann Ereignisse.

    Die Reihenfolge ist Dringlichkeit, nicht Chronologie: Ein Lauffehler und ein
    ausgefallenes Sprachmodell sind das, wonach jemand sucht, der die Konsole
    aufklappt. Die Ereigniszeilen sind der Normalbetrieb darunter.
    """

    zeilen: list[Any] = []

    if error:
        zeilen.append(ui.log_line("error", f"Lauf fehlgeschlagen: {error}"))

    for incident in _incidents(data):
        beschreibung = str(incident.get("error") or "").split("\n")[0][:160]
        zeilen.append(
            ui.log_line(
                "warning",
                f"{incident.get('caller', '?')} — {incident.get('kind', '?')}: {beschreibung}",
                tick=incident.get("tick"),
            )
        )

    for line in reversed(progress or []):
        zeilen.append(ui.log_line("muted", line))

    for event in reversed(data.events):
        quelle = str(event.get("source_agent") or "?")
        zeilen.append(
            ui.log_line(
                _EVENT_LEVELS.get(quelle, "info"),
                f"{quelle}: {event.get('description', '')}",
                tick=event.get("round_number"),
            )
        )

    return zeilen[:MAX_CONSOLE_LINES]


def console(
    data: RunData,
    *,
    progress: list[str] | None = None,
    error: str | None = None,
    open: bool = False,
) -> html.Details:
    """Die Konsole — seit P1.6 zugeklappt.

    Sie ist ein Nachschlagewerk, kein Dauerbild: Offen nahm sie den unteren
    Drittel der Zone ein und schob die Verläufe aus dem Blick. Die Zahl im
    Abzeichen sagt, ob es etwas zu sehen gibt.
    """

    zeilen = console_lines(data, progress=progress, error=error)
    return ui.accordion(
        "Konsole",
        ui.console(zeilen, empty="Noch keine Meldungen."),
        open=open,
        badge=str(len(zeilen)) if zeilen else None,
    )


# --- Die Zone als Ganzes ---------------------------------------------------


def render(
    data: RunData,
    tick: int,
    *,
    mode: str = theme.LIGHT,
    progress: list[str] | None = None,
    error: str | None = None,
) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H3("Telemetrie", className=ui.H3),
                    html.P(
                        f"Tick {tick} von {data.max_tick or '?'}",
                        className=f"{ui.CAPTION} mt-0.5 af-num",
                    ),
                ],
                className="mb-3",
            ),
            kpi_row(data, tick),
            html.Div(charts(data, tick, mode=mode), className="mt-4"),
            html.Div(console(data, progress=progress, error=error), className="mt-4"),
        ],
        className="af-pane",
    )
