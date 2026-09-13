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
from dashboard.web import formate, theme
from src.reporting.output_writer.provenance import (
    COMPUTE_MODE_LABELS,
    MODES_WITHOUT_ANY_LLM,
    MODES_WITHOUT_LLM_TICKS,
)


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
    xs: list,
    ys: list,
    *,
    title: str,
    y_title: str,
    color: str,
    y_range: list | None = None,
    mode: str = theme.LIGHT,
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
        mode=mode,
        title=title,
        showlegend=False,
        height=theme.HOEHE_KOMPAKT,
        xaxis_title="Tick",
        yaxis_title=y_title,
    )
    if y_range:
        fig.update_yaxes(range=y_range)
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def _model_label(metadata: dict) -> str:
    """Der Modellname — aber nur, wenn überhaupt eines beteiligt war.

    Die Argumente tragen den Modellnamen auch dann, wenn gar nicht gefragt
    wurde. «Modell llama3.2» neben «Rechenmodus: Ohne Sprachmodell» ist genau
    der Widerspruch, den P0.6 abstellen soll: Ein Lauf ohne Sprachmodell darf
    nicht wie ein vollwertiger aussehen.
    """

    if metadata.get("compute_mode") in MODES_WITHOUT_ANY_LLM:
        return "keins"
    return metadata.get("model") or "—"


def _provenance(metadata: dict) -> html.Div:
    """Seed und Rechenmodus (P0.6).

    Ein Lauf ohne Sprachmodell darf nicht wie ein vollwertiger aussehen. Vor
    P0.6 stand beides in keinem Artefakt — man konnte einem fertigen Lauf nicht
    ansehen, ob überhaupt ein Modell beteiligt war.

    Ältere Läufe kennen die Felder nicht. Dann steht hier ein ehrliches
    «nicht festgehalten» statt einer erfundenen Angabe.
    """

    mode = metadata.get("compute_mode")
    mode_label = COMPUTE_MODE_LABELS.get(mode, "nicht festgehalten")

    seed = metadata.get("seed")
    seed_label = str(seed) if seed is not None else "nicht festgehalten"

    code = metadata.get("code_version") or {}
    commit = code.get("commit")
    if commit:
        code_label = commit[:8] + (" + Änderungen" if code.get("dirty") else "")
    else:
        code_label = "nicht festgehalten"

    # **Der Rahmen steht vorn** (P2.0-B). Er ist die zentrale Eingabe eines
    # Laufs: Bis dahin sagte kein Artefakt, welches Szenario zugrunde lag —
    # der Fingerabdruck unterschied die Rahmen zwar, aber nur als Hash.
    rahmen = metadata.get("rahmen") or {}
    rahmen_label = str(rahmen.get("name") or "") or "nicht festgehalten"

    tiles = [
        ui.kachel(
            "Rahmenszenario",
            rahmen_label,
            hint="Die Außenwelt, aus der die Zahlen entstanden sind",
        ),
        ui.kachel("Rechenmodus", mode_label),
        ui.kachel("Seed", seed_label, hint="Gleicher Seed, gleiche Ziehung"),
    ]

    children: list = [html.Div(ui.grid(*tiles, cols="sm:grid-cols-2"), className="mt-4")]

    if mode in MODES_WITHOUT_ANY_LLM:
        children.append(
            ui.hinweis(
                "Dieser Lauf ist ohne Sprachmodell entstanden. Die Zahlen sind vollwertig — "
                "die Texte der Akteure stammen aus Platzhaltern, nicht aus einem Modell.",
                "info",
                class_name="mt-4",
            )
        )
    elif mode in MODES_WITHOUT_LLM_TICKS:
        children.append(
            ui.hinweis(
                "Die Zahlen dieses Laufs sind rein deterministisch entstanden, ohne Agenten-"
                "Dialog. Ein Sprachmodell war nur am Abschlusstext beteiligt.",
                "info",
                class_name="mt-4",
            )
        )

    # **Codestand und Fingerabdruck stehen hinter einer Klappe** (P7.2-U2.3).
    # Beides sind Hashes: Sie beantworten «ist das derselbe Lauf wie damals»
    # und keine Frage, die man beim Lesen der Ergebnisse stellt. Weg sind sie
    # damit nicht — ein Lauf ohne nachvollziehbare Herkunft wäre der Befund,
    # den P0.6 abgeräumt hat.
    fingerprint = metadata.get("config_fingerprint") or {}
    angaben = [html.P(["Codestand: ", html.Code(code_label)], className=ui.CAPTION)]
    if fingerprint:
        parts = ", ".join(
            f"{name}: {value}" for name, value in sorted(fingerprint.items()) if value
        )
        angaben.append(
            html.P(
                f"Konfigurations-Fingerabdruck — {parts}",
                className=f"{ui.CAPTION} break-all",
            )
        )
    children.append(
        ui.expert(
            *angaben,
            count=len(angaben),
            title="Technische Details",
            einheit=("Angabe", "Angaben"),
        )
    )

    return html.Div(children)


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    tone = theme.palette(mode)
    children: list = []
    metadata = _metadata(run_dir)

    if metadata:
        children.append(
            ui.grid(
                ui.kachel(
                    "Ticks",
                    f"{metadata.get('ticks_completed', '?')} / {metadata.get('ticks_max', '?')}",
                    formate.modellzeit(metadata.get("ticks_completed")) or None,
                ),
                ui.kachel("Ereignisse", metadata.get("total_events", "?")),
                ui.kachel("Modell", _model_label(metadata)),
                ui.kachel("Markt", "an" if metadata.get("market_enabled", True) else "aus"),
                cols="sm:grid-cols-2 lg:grid-cols-4",
            )
        )
        children.append(_provenance(metadata))
        children.append(
            html.P(
                [
                    "Kennung: ",
                    html.Code(run_id, className="af-text-muted"),
                    f" · erstellt {formate.zeitpunkt(metadata.get('timestamp'))}",
                ],
                className=f"{ui.CAPTION} mt-3",
            )
        )

    ticks = load_tick_mechanics(run_dir)
    prices = load_price_series(run_dir)
    if not ticks and not prices:
        children.append(ui.hinweis("Keine Zeitreihen-Daten vorhanden.", "info", class_name="mt-6"))
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
                    color=tone["booking"],
                    y_range=[0, 1],
                    mode=mode,
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
                    y_title="Preis (€)",
                    color=tone["price"],
                    mode=mode,
                ),
                pad=False,
                class_name="p-2",
            )
        )

    children.append(html.Div(ui.grid(*charts, cols="xl:grid-cols-2"), className="mt-6"))
    return html.Div(children)
