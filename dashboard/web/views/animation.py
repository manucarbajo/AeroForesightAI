"""Tab «Animation»: die Population über die Ticks hinweg.

Vier aufeinander aufbauende Sichten auf dieselbe `individuals_history.csv` —
erst jeder einzelne Agent, dann nach Altersgruppen, nach Segmenten und
schließlich Buchungs- gegen Populationsanteil. Die Aggregationen sind
unverändert aus der Streamlit-Variante übernommen; neu sind nur Farbgebung
und Rahmen.
"""

from __future__ import annotations

import json
from pathlib import Path

from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web import theme

#: Grundspalten der History-Datei. Alles, was darüber hinaus in der CSV steht,
#: ist ein Segment-Label aus der Population-Konfiguration.
_BASE_COLUMNS = {
    "id",
    "tick",
    "age",
    "wtp_eur",
    "environmental_awareness",
    "price_sensitivity",
    "substitution_readiness",
    "booked",
    "ticket_price",
    "Segment",
    "Gebucht",
    "Altersgruppe",
    "booked_num",
}

_AGE_BINS = [0, 18, 26, 36, 51, 66, 120]
_AGE_LABELS = ["<18", "18-25", "26-35", "36-50", "51-65", ">65"]


def _graph(fig, *, mode: str = theme.LIGHT) -> dcc.Graph:
    theme.slow_animation(fig)
    fig.update_layout(template=theme.template_for(mode), height=520, margin=dict(t=64, b=64))
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def _block(title: str, caption: str, graph) -> html.Div:
    return html.Div(
        [
            html.H3(title, className=ui.H3),
            html.P(caption, className=f"{ui.CAPTION} mt-1 mb-3"),
            ui.card(graph, pad=False, class_name="p-2"),
        ],
        className="mb-10",
    )


def load_history(run_dir: Path):
    """Die Individuen-History mit den abgeleiteten Spalten.

    Öffentlich, weil die Szene im Viewport dieselbe Aufbereitung braucht —
    zweimal `pd.read_csv` mit leicht verschiedenen Ableitungen wäre genau die
    Sorte Doppelung, aus der Divergenz entsteht.
    """

    import pandas as pd

    frame = pd.read_csv(run_dir / "individuals_history.csv")
    if frame.empty:
        return frame

    price_file = run_dir / "price_history.json"
    if price_file.is_file():
        payload = json.loads(price_file.read_text(encoding="utf-8"))
        price_map = {item["round_number"]: item["price"] for item in payload}
        frame["ticket_price"] = frame["tick"].map(price_map)
    else:
        frame["ticket_price"] = 0

    frame["Segment"] = frame.apply(
        lambda row: "Business" if str(row.get("business", False)).lower() == "true" else "Leisure",
        axis=1,
    )
    frame["Gebucht"] = frame["booked"].astype(str)
    frame["booked_num"] = frame["booked"].astype(bool).astype(int)
    frame["Altersgruppe"] = pd.cut(frame["age"], bins=_AGE_BINS, labels=_AGE_LABELS, right=False)
    return frame


def _population_figure(frame, mode: str = theme.LIGHT):
    tone = theme.palette(mode)
    import plotly.express as px

    fig = px.scatter(
        frame,
        x="wtp_eur",
        y="environmental_awareness",
        animation_frame="tick",
        animation_group="id",
        color="Gebucht",
        symbol="Segment",
        hover_name="id",
        hover_data=["age", "substitution_readiness", "price_sensitivity"],
        title="Population über Zeit",
        labels={
            "wtp_eur": "Zahlungsbereitschaft (WTP) in €",
            "environmental_awareness": "Umweltbewusstsein (Awareness)",
            "tick": "Tick",
        },
        color_discrete_map={"True": tone["positive"], "False": tone["negative"]},
        range_x=[
            frame["wtp_eur"].quantile(0.01) * 0.9,
            frame["wtp_eur"].quantile(0.99) * 1.1,
        ],
        range_y=[-0.1, 1.1],
    )
    fig.update_traces(marker=dict(size=4, opacity=0.45, line=dict(width=0)))
    return fig


def _age_figure(frame):
    import pandas as pd
    import plotly.express as px

    aggregated = (
        frame.groupby(["tick", "Altersgruppe"], observed=False)
        .agg(
            total_agenten=("id", "count"),
            gebucht=("booked_num", "sum"),
            avg_wtp=("wtp_eur", "mean"),
            ticket_price=("ticket_price", "mean"),
            avg_awareness=("environmental_awareness", "mean"),
        )
        .reset_index()
    )
    aggregated["Buchungsrate"] = (
        aggregated["gebucht"] / aggregated["total_agenten"].replace(0, pd.NA)
    ).fillna(0)
    aggregated = aggregated[aggregated["total_agenten"] > 0]
    if aggregated.empty:
        return None

    return px.scatter(
        aggregated,
        x="Buchungsrate",
        y="avg_wtp",
        size="gebucht",
        color="Altersgruppe",
        animation_frame="tick",
        animation_group="Altersgruppe",
        hover_name="Altersgruppe",
        hover_data={
            "gebucht": True,
            "total_agenten": True,
            "avg_wtp": ":.2f",
            "ticket_price": ":.2f",
        },
        title="Buchungsverhalten nach Altersgruppen",
        labels={
            "Buchungsrate": "Buchungsrate (0–1)",
            "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
            "gebucht": "Anzahl Buchungen",
        },
        size_max=50,
        range_x=[-0.1, 1.1],
        range_y=[aggregated["avg_wtp"].min() * 0.8, aggregated["avg_wtp"].max() * 1.2],
    )


def _segment_frame(frame):
    """Je Tick und Segment-Label auszählen, wie viele Agenten gebucht haben."""

    import pandas as pd

    # `business` bleibt bewusst drin: es ist ein Label wie jedes andere und
    # erscheint in dieser Auswertung als eigenes Segment.
    segment_columns = [c for c in frame.columns if c not in _BASE_COLUMNS]
    if not segment_columns:
        return None

    records: list[dict] = []
    for tick in sorted(frame["tick"].unique()):
        frame_tick = frame[frame["tick"] == tick]
        for column in segment_columns:
            in_segment = frame_tick[frame_tick[column].astype(str).str.lower() == "true"]
            total = len(in_segment)
            if not total:
                continue
            booked = in_segment["booked_num"].sum()
            records.append(
                {
                    "tick": tick,
                    "Segment": column.replace("_", " ").title(),
                    "total_agenten": total,
                    "gebucht": booked,
                    "Buchungsrate": booked / total,
                    "ticket_price": in_segment["ticket_price"].mean(),
                    "avg_wtp": in_segment["wtp_eur"].mean(),
                    "avg_awareness": in_segment["environmental_awareness"].mean(),
                }
            )
    if not records:
        return None
    return pd.DataFrame(records)


def _segment_figure(segments):
    import plotly.express as px

    return px.scatter(
        segments,
        x="Buchungsrate",
        y="avg_wtp",
        size="gebucht",
        color="Segment",
        animation_frame="tick",
        animation_group="Segment",
        hover_name="Segment",
        hover_data={
            "gebucht": True,
            "total_agenten": True,
            "avg_wtp": ":.2f",
            "ticket_price": ":.2f",
        },
        title="Buchungsverhalten nach Segmenten",
        labels={
            "Buchungsrate": "Buchungsrate (0–1)",
            "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
            "gebucht": "Anzahl Buchungen",
        },
        size_max=50,
        range_x=[-0.1, 1.1],
        range_y=[segments["avg_wtp"].min() * 0.8, segments["avg_wtp"].max() * 1.2],
    )


def _efficiency_figure(frame, segments, mode: str = theme.LIGHT):
    import plotly.express as px

    totals_agents = frame.groupby("tick")["id"].count().to_dict()
    totals_booked = frame.groupby("tick")["booked_num"].sum().to_dict()

    segments = segments.copy()
    segments["pop_share"] = segments.apply(
        lambda row: row["total_agenten"] / totals_agents.get(row["tick"], 1), axis=1
    )
    segments["booking_share"] = segments.apply(
        lambda row: row["gebucht"] / max(totals_booked.get(row["tick"], 1), 1), axis=1
    )

    fig = px.scatter(
        segments,
        x="pop_share",
        y="booking_share",
        size="gebucht",
        color="Segment",
        animation_frame="tick",
        animation_group="Segment",
        hover_name="Segment",
        hover_data={
            "gebucht": True,
            "total_agenten": True,
            "pop_share": ":.1%",
            "booking_share": ":.1%",
        },
        title="Marktanteil vs. Populationsanteil",
        labels={
            "pop_share": "Anteil an Gesamtpopulation (0–1)",
            "booking_share": "Anteil an Gesamtbuchungen (0–1)",
            "gebucht": "Anzahl Buchungen",
        },
        size_max=50,
        range_x=[-0.05, 1.05],
        range_y=[-0.05, 1.05],
    )
    fig.add_shape(
        type="line",
        line=dict(dash="dash", color=theme.palette(mode)["text-faint"]),
        x0=0,
        y0=0,
        x1=1,
        y1=1,
    )
    return fig


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    history_file = run_dir / "individuals_history.csv"
    if not history_file.is_file():
        return ui.empty_state(
            "Keine Agenten-History in diesem Run.",
            hint="`individuals_history.csv` fehlt. Starten Sie eine neue Simulation, "
            "um die Agenten-History aufzuzeichnen.",
            icon_name="animation",
        )

    try:
        frame = load_history(run_dir)
    except Exception as exc:  # noqa: BLE001 - defekte History soll die Seite nicht sprengen
        return ui.alert(f"Fehler beim Lesen der History: {exc}", "error")

    if frame.empty:
        return ui.alert("History-Datei ist leer.", "warning")

    blocks: list = [
        _block(
            "Animierter Population-Scatter-Plot",
            "Verfolgen Sie die Agenten über die Ticks hinweg.",
            _graph(_population_figure(frame, mode), mode=mode),
        )
    ]

    age_figure = _age_figure(frame)
    if age_figure is not None:
        blocks.append(
            _block(
                "Aggregation nach Altersgruppen",
                "Buchungsraten und -mengen pro Altersgruppe über die Ticks.",
                _graph(age_figure, mode=mode),
            )
        )

    segments = _segment_frame(frame)
    if segments is None:
        blocks.append(
            ui.alert(
                "Keine Segmente (Labels) in der Population definiert.", "info", class_name="mb-6"
            )
        )
        return html.Div(blocks)

    blocks.append(
        _block(
            "Aggregation nach Segmenten",
            "Buchungsraten und -mengen pro Segment über die Ticks.",
            _graph(_segment_figure(segments), mode=mode),
        )
    )
    blocks.append(
        _block(
            "Segment-Effizienz (Buchungsanteil vs. Populationsanteil)",
            "Liegt eine Bubble oberhalb der Diagonalen, bucht dieses Segment "
            "überdurchschnittlich oft in Relation zu seiner Größe.",
            _graph(_efficiency_figure(frame, segments, mode), mode=mode),
        )
    )
    return html.Div(blocks)
