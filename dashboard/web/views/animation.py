"""Tab «Animation»: die Population über die Ticks hinweg.

Sichten auf dieselbe `individuals_history.csv`: jeder einzelne Agent, nach
Altersgruppen, nach Segmenten und Buchungs- gegen Populationsanteil — diese
vier stammen aus der Ops-Variante der abgelösten Streamlit-UI.

**Seit P5.2 (2026-09-11) dazu die Einzelsichten der Researcher-Variante**, auf
eine feste Stichprobe von Personen. Übernommen ist, *was* sie zeigen, nicht
*wie* sie rechneten: Die Erschwinglichkeitsgrenze im Diagramm «Wer sich den Flug leisten kann» schreibt
der Lauf mit, statt dass sie hier ein zweites Mal entsteht — die Legacy-Ansicht
hatte dabei den Grün-Aufschlag vergessen.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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
    "erschwinglichkeitsgrenze_eur",
    "spielraum_eur",
    "reisebedarf",
}

#: Wie viele Personen die Einzelsichten zeigen. Die Aggregationen rechnen mit
#: allen; eine Punktwolke aus tausend Personen über hundert Ticks wäre unlesbar
#: und bremst den Browser. Fest gezogen, damit von Tick zu Tick dieselben
#: Personen zu sehen sind — so hielt es die Researcher-Variante (P5.2).
STICHPROBE = 150
_STICHPROBEN_SEED = 42


@dataclass(frozen=True)
class Merkmalsicht:
    """Eine Streuung zweier Personenmerkmale über die Ticks."""

    titel: str
    x: str
    y: str
    x_achse: str
    y_achse: str
    x_bereich: tuple[float, float] | None
    y_bereich: tuple[float, float] | None
    lesehilfe: str


#: Die drei Merkmals-Streuungen der Researcher-Variante (P5.2). Die Lesehilfen
#: sagen, was im Modell passiert — nicht, was die Legacy-Texte versprachen.
MERKMALSICHTEN = (
    Merkmalsicht(
        titel="Verhalten nach Gruppe: Preisempfindlichkeit gegen Bahnbereitschaft",
        x="price_sensitivity",
        y="substitution_readiness",
        x_achse="Preisempfindlichkeit",
        y_achse="Bahnbereitschaft",
        x_bereich=(-0.05, 1.05),
        y_bereich=(-0.05, 1.05),
        lesehilfe="Beide Merkmale entstehen beim Ziehen einer Person. Die "
        "Preisempfindlichkeit kann eine einmalige Regel später anheben, die "
        "Bahnbereitschaft nicht.",
    ),
    Merkmalsicht(
        titel="Alter und Umweltbewusstsein: wie das Alter die Person prägt",
        x="age",
        y="environmental_awareness",
        x_achse="Alter",
        y_achse="Umweltbewusstsein",
        x_bereich=(15.0, 95.0),
        y_bereich=(-0.05, 1.05),
        lesehilfe="Das Alter prägt beim Ziehen, wie umweltbewusst eine Person ist; "
        "eine einmalige Regel kann das Umweltbewusstsein später anheben.",
    ),
    Merkmalsicht(
        titel="Einkommen und Zahlungsbereitschaft: Einkommensfaktor gegen Zahlungsbereitschaft",
        x="income_factor",
        y="wtp_eur",
        x_achse="Einkommensfaktor",
        y_achse="Zahlungsbereitschaft in €",
        x_bereich=None,
        y_bereich=None,
        lesehilfe="Der Einkommensfaktor folgt dem Einkommensindex des Laufs; wandert "
        "er, verschiebt sich die Wolke waagrecht.",
    ),
)

_AGE_BINS = [0, 18, 26, 36, 51, 66, 120]
_AGE_LABELS = ["<18", "18-25", "26-35", "36-50", "51-65", ">65"]


def _graph(fig, *, mode: str = theme.LIGHT) -> dcc.Graph:
    theme.slow_animation(fig)
    fig.update_layout(
        template=theme.template_for(mode), height=theme.HOEHE_AUSSAGE, margin=dict(t=64, b=64)
    )
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def _block(title: str, caption: str, graph) -> html.Div:
    return html.Div(
        [
            html.H3(title, className=ui.H3),
            html.P(caption, className=f"{ui.CAPTION} mt-1 mb-3"),
            ui.card(graph, pad=False, class_name="p-2"),
        ],
        className="mb-8",
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


def stichprobe(frame, anzahl: int = STICHPROBE):
    """Dieselben höchstens *anzahl* Personen in jedem Tick — fest gezogen."""

    import numpy as np

    ids = frame["id"].unique()
    if len(ids) <= anzahl:
        return frame
    gewaehlt = np.random.default_rng(_STICHPROBEN_SEED).choice(ids, size=anzahl, replace=False)
    return frame[frame["id"].isin(gewaehlt)]


def surplus_frame(frame):
    """Der Spielraum je Person und Tick: Erschwinglichkeitsgrenze minus Ticketpreis.

    `None`, wenn der Lauf die Grenze nicht mitschreibt (vor P5.2) oder kein
    Preisverlauf vorliegt — dann gäbe es nur eine Zahl, die aussieht wie ein
    Spielraum. Die Grenze kommt aus der Historie und nicht aus einer Formel hier.
    """

    if "erschwinglichkeitsgrenze_eur" not in frame.columns or "ticket_price" not in frame.columns:
        return None
    if (frame["ticket_price"] == 0).all():
        return None
    frame = frame.copy()
    frame["spielraum_eur"] = frame["erschwinglichkeitsgrenze_eur"] - frame["ticket_price"]
    return frame


def _surplus_figure(frame, mode: str = theme.LIGHT):
    tone = theme.palette(mode)
    import plotly.express as px

    hover = [
        spalte
        for spalte in ("ticket_price", "wtp_eur", "income_factor", "environmental_awareness")
        if spalte in frame.columns
    ]
    fig = px.scatter(
        frame,
        x="erschwinglichkeitsgrenze_eur",
        y="spielraum_eur",
        animation_frame="tick",
        animation_group="id",
        color="Gebucht",
        symbol="Segment",
        hover_name="id",
        hover_data=hover,
        title="Wer sich den Flug leisten kann",
        labels={
            "erschwinglichkeitsgrenze_eur": "Höchster bezahlbarer Preis (€)",
            "spielraum_eur": "Spielraum bis zur Grenze (€)",
            "ticket_price": "Ticketpreis (€)",
            "tick": "Tick",
        },
        color_discrete_map={"True": tone["positive"], "False": tone["negative"]},
        range_x=[0, frame["erschwinglichkeitsgrenze_eur"].max() * 1.1],
        range_y=[frame["spielraum_eur"].min() - 10, frame["spielraum_eur"].max() + 10],
    )
    fig.update_traces(marker=dict(size=6, opacity=0.6, line=dict(width=0)))
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=tone["text-faint"],
        annotation_text="Grenze: darunter bucht niemand",
    )
    return fig


def bedarf_frame(frame):
    """Der Reisebedarf je Person und Tick: eins minus die Sättigung — oder `None`.

    Die Sättigung steigt bei einer Buchung um `booking_increase` (gedeckelt bei
    1,0) und sinkt danach je Tick um die Abklingrate des Segments. Die Zahl kommt
    aus der Historie; hier wird nur umgedreht, damit «oben» «will reisen» heißt.
    """

    if "saturation_level" not in frame.columns:
        return None
    frame = frame.copy()
    frame["reisebedarf"] = 1.0 - frame["saturation_level"]
    return frame


def _swarm_figure(frame, mode: str = theme.LIGHT):
    tone = theme.palette(mode)
    import plotly.express as px

    fig = px.scatter(
        frame,
        x="wtp_eur",
        y="reisebedarf",
        animation_frame="tick",
        animation_group="id",
        color="Gebucht",
        symbol="Segment",
        hover_name="id",
        hover_data=["saturation_level"],
        title="Sättigung",
        labels={
            "wtp_eur": "Zahlungsbereitschaft in €",
            "reisebedarf": "Reisebedarf (1 − Sättigung)",
            "saturation_level": "Sättigung",
            "tick": "Tick",
        },
        color_discrete_map={"True": tone["positive"], "False": tone["negative"]},
        range_x=[0, frame["wtp_eur"].max() * 1.1],
        range_y=[-0.05, 1.05],
    )
    fig.update_traces(marker=dict(size=6, opacity=0.6, line=dict(width=0)))
    return fig


def _merkmal_figure(frame, sicht: Merkmalsicht, mode: str = theme.LIGHT):
    tone = theme.palette(mode)
    import plotly.express as px

    fig = px.scatter(
        frame,
        x=sicht.x,
        y=sicht.y,
        animation_frame="tick",
        animation_group="id",
        color="Gebucht",
        symbol="Segment",
        hover_name="id",
        title=sicht.titel.split(":")[0],
        labels={sicht.x: sicht.x_achse, sicht.y: sicht.y_achse, "tick": "Tick"},
        color_discrete_map={"True": tone["positive"], "False": tone["negative"]},
        range_x=list(sicht.x_bereich) if sicht.x_bereich else None,
        range_y=list(sicht.y_bereich) if sicht.y_bereich else None,
    )
    fig.update_traces(marker=dict(size=6, opacity=0.6, line=dict(width=0)))
    return fig


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
            "wtp_eur": "Zahlungsbereitschaft in €",
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
            "avg_wtp": "Ø Zahlungsbereitschaft in €",
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
            "avg_wtp": "Ø Zahlungsbereitschaft in €",
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
            "Kein Personenverlauf in diesem Lauf.",
            hint="`individuals_history.csv` fehlt. Starten Sie eine neue Simulation, "
            "um den Personenverlauf aufzuzeichnen.",
            icon_name="animation",
        )

    try:
        frame = load_history(run_dir)
    except Exception as exc:  # noqa: BLE001 - defekte History soll die Seite nicht sprengen
        return ui.hinweis(f"Der Personenverlauf ließ sich nicht lesen: {exc}", "fehler")

    if frame.empty:
        return ui.hinweis("Der Personenverlauf ist leer.", "warnung")

    blocks: list = [
        _block(
            "Die Bevölkerung über die Ticks",
            "Jede Person nach Zahlungsbereitschaft und Umweltbewusstsein, über die Ticks.",
            _graph(_population_figure(frame, mode), mode=mode),
        )
    ]

    surplus = surplus_frame(frame)
    if surplus is None:
        blocks.append(
            ui.hinweis(
                "Das Diagramm «Wer sich den Flug leisten kann» braucht die Spalte `erschwinglichkeitsgrenze_eur` und den "
                "Preisverlauf. Läufe vor dem 11. September 2026 schreiben die Spalte nicht — "
                "ein neuer Lauf zeigt ihn.",
                "info",
                class_name="mb-6",
            )
        )
    else:
        blocks.append(
            _block(
                "Wer sich den Flug leisten kann: Spielraum bis zur Erschwinglichkeitsgrenze",
                f"Eine feste Stichprobe von {STICHPROBE} Personen. Waagrecht der höchste Preis, "
                "den eine Person überhaupt bezahlen kann, senkrecht der Abstand zum Ticketpreis "
                "des Ticks. Unter der gestrichelten Linie bucht sie nicht; darüber entscheidet "
                "die Wahrscheinlichkeit.",
                _graph(_surplus_figure(stichprobe(surplus), mode), mode=mode),
            )
        )

    bedarf = bedarf_frame(frame)
    if bedarf is None:
        blocks.append(
            ui.hinweis(
                "Das Diagramm «Sättigung» braucht die Spalte `saturation_level` — dieser Lauf "
                "schreibt sie nicht.",
                "info",
                class_name="mb-6",
            )
        )
    else:
        blocks.append(
            _block(
                "Sättigung: Reisebedarf und Wiederkehr",
                f"Dieselbe Stichprobe von {STICHPROBE} Personen. Waagrecht die "
                "Zahlungsbereitschaft, senkrecht der Reisebedarf: eins minus die Sättigung. "
                "Wer bucht, wird gesättigt und fällt nach unten; danach klingt die Sättigung "
                "Tick für Tick ab, und der Punkt steigt wieder — je nach Segment "
                "verschieden schnell.",
                _graph(_swarm_figure(stichprobe(bedarf), mode), mode=mode),
            )
        )

    for sicht in MERKMALSICHTEN:
        if sicht.x not in frame.columns or sicht.y not in frame.columns:
            blocks.append(
                ui.hinweis(
                    f"«{sicht.titel}» braucht die Spalten `{sicht.x}` und `{sicht.y}` — "
                    "dieser Lauf schreibt sie nicht.",
                    "info",
                    class_name="mb-6",
                )
            )
            continue
        blocks.append(
            _block(
                sicht.titel,
                f"Dieselbe Stichprobe von {STICHPROBE} Personen. {sicht.lesehilfe}",
                _graph(_merkmal_figure(stichprobe(frame), sicht, mode), mode=mode),
            )
        )

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
            ui.hinweis(
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
