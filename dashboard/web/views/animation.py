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
from functools import lru_cache
from pathlib import Path

from dash import MATCH, Input, Output, State, ctx, dcc, html, no_update

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

#: Wie viele Personen die Punktwolke «Die Bevölkerung über die Ticks» zeigt
#: (P8-V11). Bis zum 2026-10-01 waren es alle — bei 120 Ticks 8,15 MiB für ein
#: einziges Diagramm, mit 300 noch 2,62 MiB; mit 200 bleibt es unter 2 MB. Mehr als
#: die Einzelsichten, weil sie die ganze Wolke zeigen soll.
STICHPROBE_BEVOELKERUNG = 200


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


#: Die Knöpfe «Diagramm zeigen» und die Wirte, in die das Diagramm gezeichnet wird
#: (P8-V11). **Musterkennungen**, weil es je Lauf verschieden viele Blöcke gibt
#: und `MATCH` null Treffer verträgt (Regel 6).
ZEIGEN = "animation-zeigen"
WIRT = "animation-wirt"


def _kopf(run_dir: Path) -> list[str]:
    """Die Spalten des Personenverlaufs — gelesen wird nur die erste Zeile."""

    import pandas as pd

    return list(pd.read_csv(run_dir / "individuals_history.csv", nrows=0).columns)


@lru_cache(maxsize=2)
def _verlauf(laufordner: str, stand: float):
    """`load_history` je Lauf **einmal** — *stand* ist die Änderungszeit der Datei.

    Neun Diagramme lesen dieselbe Datei; ohne Zwischenspeicher läse jeder Klick
    sie neu (bei 120 Ticks rund 1,4 s). Die Änderungszeit im Schlüssel sorgt
    dafür, dass ein neu gerechneter Lauf nicht den alten Stand zeigt.
    """

    return load_history(Path(laufordner))


def _bloecke(run_dir: Path) -> list[tuple[str, str, str]]:
    """Welche Diagramme dieser Lauf hergibt: (Kennung, Titel, Erklärung).

    Entschieden wird aus dem **Kopf** der Datei — die Daten selbst liest erst der
    Klick. Ein Hinweis statt eines Diagramms trägt die Kennung `""`.
    """

    spalten = set(_kopf(run_dir))
    eintraege: list[tuple[str, str, str]] = [
        (
            "bevoelkerung",
            "Die Bevölkerung über die Ticks",
            f"Eine feste Stichprobe von {STICHPROBE_BEVOELKERUNG} Personen nach "
            "Zahlungsbereitschaft und Umweltbewusstsein, über die Ticks.",
        )
    ]
    if "erschwinglichkeitsgrenze_eur" in spalten and (run_dir / "price_history.json").is_file():
        eintraege.append(
            (
                "spielraum",
                "Wer sich den Flug leisten kann: Spielraum bis zur Erschwinglichkeitsgrenze",
                f"Eine feste Stichprobe von {STICHPROBE} Personen. Waagrecht der höchste "
                "Preis, den eine Person überhaupt bezahlen kann, senkrecht der Abstand zum "
                "Ticketpreis des Ticks. Unter der gestrichelten Linie bucht sie nicht; "
                "darüber entscheidet die Wahrscheinlichkeit.",
            )
        )
    else:
        eintraege.append(
            (
                "",
                "",
                "Das Diagramm «Wer sich den Flug leisten kann» braucht die Spalte "
                "`erschwinglichkeitsgrenze_eur` und den Preisverlauf. Läufe vor dem "
                "11. September 2026 schreiben die Spalte nicht — ein neuer Lauf zeigt ihn.",
            )
        )
    if "saturation_level" in spalten:
        eintraege.append(
            (
                "saettigung",
                "Sättigung: Reisebedarf und Wiederkehr",
                f"Dieselbe Stichprobe von {STICHPROBE} Personen. Waagrecht die "
                "Zahlungsbereitschaft, senkrecht der Reisebedarf: eins minus die Sättigung. "
                "Wer bucht, wird gesättigt und fällt nach unten; danach klingt die Sättigung "
                "Tick für Tick ab, und der Punkt steigt wieder — je nach Segment "
                "verschieden schnell.",
            )
        )
    else:
        eintraege.append(
            (
                "",
                "",
                "Das Diagramm «Sättigung» braucht die Spalte `saturation_level` — dieser Lauf "
                "schreibt sie nicht.",
            )
        )
    for nummer, sicht in enumerate(MERKMALSICHTEN):
        if sicht.x in spalten and sicht.y in spalten:
            eintraege.append(
                (
                    f"merkmal-{nummer}",
                    sicht.titel,
                    f"Dieselbe Stichprobe von {STICHPROBE} Personen. {sicht.lesehilfe}",
                )
            )
        else:
            eintraege.append(
                (
                    "",
                    "",
                    f"«{sicht.titel}» braucht die Spalten `{sicht.x}` und `{sicht.y}` — "
                    "dieser Lauf schreibt sie nicht.",
                )
            )
    eintraege.append(
        (
            "alter",
            "Aggregation nach Altersgruppen",
            "Buchungsraten und -mengen pro Altersgruppe über die Ticks.",
        )
    )
    if not [c for c in spalten if c not in _BASE_COLUMNS]:
        eintraege.append(("", "", "Keine Segmente (Labels) in der Population definiert."))
        return eintraege
    eintraege.append(
        (
            "segmente",
            "Aggregation nach Segmenten",
            "Buchungsraten und -mengen pro Segment über die Ticks.",
        )
    )
    eintraege.append(
        (
            "effizienz",
            "Segment-Effizienz (Buchungsanteil vs. Populationsanteil)",
            "Liegt eine Bubble oberhalb der Diagonalen, bucht dieses Segment "
            "überdurchschnittlich oft in Relation zu seiner Größe.",
        )
    )
    return eintraege


def diagramm(kennung: str, run_dir: Path, mode: str = theme.LIGHT):
    """Das eine Diagramm hinter einem Knopf «Diagramm zeigen» — oder ein Hinweis."""

    datei = run_dir / "individuals_history.csv"
    frame = _verlauf(str(run_dir), datei.stat().st_mtime)
    if kennung == "bevoelkerung":
        return _graph(
            _population_figure(stichprobe(frame, STICHPROBE_BEVOELKERUNG), mode), mode=mode
        )
    if kennung == "spielraum":
        surplus = surplus_frame(frame)
        if surplus is not None:
            return _graph(_surplus_figure(stichprobe(surplus), mode), mode=mode)
    if kennung == "saettigung":
        bedarf = bedarf_frame(frame)
        if bedarf is not None:
            return _graph(_swarm_figure(stichprobe(bedarf), mode), mode=mode)
    if kennung.startswith("merkmal-"):
        sicht = MERKMALSICHTEN[int(kennung.removeprefix("merkmal-"))]
        return _graph(_merkmal_figure(stichprobe(frame), sicht, mode), mode=mode)
    if kennung == "alter":
        figur = _age_figure(frame)
        if figur is not None:
            return _graph(figur, mode=mode)
    if kennung in ("segmente", "effizienz"):
        segments = _segment_frame(frame)
        if segments is not None:
            if kennung == "segmente":
                return _graph(_segment_figure(segments), mode=mode)
            return _graph(_efficiency_figure(frame, segments, mode), mode=mode)
    return ui.hinweis("Für dieses Diagramm enthält der Lauf keine Daten.", "info")


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    """Die Ansicht — **ohne ein einziges Diagramm** (P8-V11, 2026-10-01).

    Bis dahin zeichnete sie neun animierte Diagramme auf einmal: gemessen 7,6 s
    und 5,05 MiB für den Pitch-Fall über 40 Ticks, 20,5 s und 14,84 MiB für
    einen Rahmen über 120 Ticks. Jedes Diagramm kostet für sich 1 bis 3 s; ein
    Bruchteil davon lässt sich sparen, die Summe nicht. Deshalb rechnet jedes
    erst, wenn jemand es sehen will — so sah es P7.6-U6.2 vor.
    """

    history_file = run_dir / "individuals_history.csv"
    if not history_file.is_file():
        return ui.empty_state(
            "Kein Personenverlauf in diesem Lauf.",
            hint="`individuals_history.csv` fehlt. Starten Sie eine neue Simulation, "
            "um den Personenverlauf aufzuzeichnen.",
            icon_name="animation",
        )

    try:
        eintraege = _bloecke(run_dir)
    except Exception as exc:  # noqa: BLE001 - defekte History soll die Seite nicht sprengen
        return ui.hinweis(f"Der Personenverlauf ließ sich nicht lesen: {exc}", "fehler")

    blocks: list = [
        ui.satz(
            "Jedes Diagramm rechnet erst, wenn Sie es öffnen — je nach Länge des Laufs "
            "dauert das einige Sekunden.",
            class_name=f"{ui.CAPTION} mb-6",
        )
    ]
    for kennung, titel, erklaerung in eintraege:
        if not kennung:
            blocks.append(ui.hinweis(erklaerung, "info", class_name="mb-6"))
            continue
        blocks.append(
            _block(
                titel,
                erklaerung,
                html.Div(
                    [
                        ui.button(
                            "Diagramm zeigen",
                            id={"type": ZEIGEN, "diagramm": kennung},
                            variant="secondary",
                            icon_name="play_arrow",
                        ),
                        dcc.Loading(
                            html.Div(id={"type": WIRT, "diagramm": kennung}),
                            type="dot",
                            className="af-ladeanzeige",
                            delay_show=ui.LADEANZEIGE_NACH_MS,
                        ),
                    ]
                ),
            )
        )
    return html.Div(blocks)


def register_callbacks(app) -> None:
    @app.callback(
        Output({"type": WIRT, "diagramm": MATCH}, "children"),
        Output({"type": ZEIGEN, "diagramm": MATCH}, "style"),
        Input({"type": ZEIGEN, "diagramm": MATCH}, "n_clicks"),
        State("selected-run-store", "data"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def _zeigen(n_clicks, selected, mode):
        """Ein Diagramm auf Klick — und der Knopf geht, wenn es da ist.

        Dash ruft einen Callback mit Musterkennung auch, wenn der Knopf neu
        gezeichnet wird; dann ist `n_clicks` leer, und es geschieht nichts.
        """

        if not n_clicks or not selected:
            return no_update, no_update
        kennung = ctx.triggered_id["diagramm"]
        try:
            inhalt = diagramm(kennung, Path(selected["run_dir"]), theme.normalise(mode))
        except Exception as exc:  # noqa: BLE001 - ein Diagramm soll die Seite nicht sprengen
            return (
                ui.hinweis(f"Das Diagramm ließ sich nicht zeichnen: {exc}", "fehler"),
                no_update,
            )
        return inhalt, {"display": "none"}
