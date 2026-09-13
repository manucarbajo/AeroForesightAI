"""Tab «Figures»: **vier Aussagen**, die ein Lauf beantwortet (P1.2).

Bis zum 2026-08-30 waren es sechs thematische Ansichten plus PNG-Export, nach
Datenherkunft geschnitten: «Yield & Markt», «Segmente & Alter», «Policies &
Steuern», «Makro-Wirtschaft», «Airline-Kosten», «CIB-Faktoren». Das ist eine
Gliederung der *Zeitreihen*, keine Gliederung der *Fragen* — wer sie durchsah,
bekam sechs Sammlungen von Kurven und keine Auskunft.

Der Schnitt verläuft jetzt entlang der **Wirkungskette**:

1. **Preis und Nachfrage** — wie stark reagiert die Nachfrage auf den Preis?
2. **Was die Politik bewirkt** — was machen die Instrumente mit den Kosten?
3. **Wer noch fliegt** — wer bleibt zuerst weg?
4. **Die Szenarien nebeneinander** — worin unterscheiden sie sich?

**Zwei Ansichten sind dabei weggefallen, und beide aus demselben Grund:** Sie
zeigten Eingänge statt Ergebnisse. «Makro-Wirtschaft» (Einkommensindex,
Ölpreis, Bevölkerung) ist das, was man dem Lauf vorgibt; «CIB-Faktoren» waren
sieben Treppenlinien, die für sich genommen keine Frage beantworten — sie sind
jetzt Kontext an Aussage 4, wo sie etwas erklären: In welcher Weltlage endet
dieses Szenario, und in welcher jenes.

Der PNG-Export bleibt daneben — er ist eine **Ausgabeform**, keine Aussage.
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
    ("1 · Preis und Nachfrage", "nachfrage"),
    ("2 · Was die Politik bewirkt", "politik"),
    ("3 · Wer noch fliegt", "wer"),
    ("4 · Die Szenarien nebeneinander", "szenarien"),
    ("PNG-Export", "png"),
]

POLICY_COLUMNS = ["carbon_tax_level", "saf_mandate_share", "efuel_subsidy", "airport_fee"]
ABSOLUTE_POLICY_COLUMNS = {"carbon_tax_level", "airport_fee"}
COST_COLUMNS = ["maintenance_cost_index", "staff_cost_index", "fuel_price_change"]


def _reihenname(spalte: str) -> str:
    """Der Name einer Systemgröße für Legende und Hover — nie die Kennung (P7.1-U1.5)."""

    from dashboard.config_catalog import PROPERTY_LABELS

    return PROPERTY_LABELS.get(spalte, spalte.replace("_", " "))


def _achse(wort: str, spalten: list[str]) -> str:
    """Ein Achsentitel mit den Einheiten der Reihen, **die wirklich auf ihr liegen**.

    Bis zum 2026-09-13 stand an der linken Achse von «Die Instrumente»
    «Betrag (EUR/t o. ä.)» — eine geratene Einheit für zwei verschiedene Größen
    (CO₂-Steuer in EUR/t, Flughafengebühr in EUR). Jetzt steht dort, was es ist.
    """

    from dashboard.config_catalog import property_einheit

    einheiten: list[str] = []
    for spalte in spalten:
        einheit = property_einheit(spalte)
        if einheit and einheit not in einheiten:
            einheiten.append(einheit)
    return f"{wort} ({' · '.join(einheiten)})" if einheiten else wort


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


def _graph(fig, height: int = theme.HOEHE_AUSSAGE, *, mode: str = theme.LIGHT) -> dcc.Graph:
    theme.style_figure(fig, height=height, mode=mode)
    return dcc.Graph(figure=fig, config=theme.GRAPH_CONFIG)


def _panel(*children) -> html.Div:
    return html.Div(list(children))


# --- Einzelansichten -------------------------------------------------------


#: Welche Modellgröße in welcher Spur ihr Band bekommt. Dieselben zwei Reihen,
#: die `simulation_runner.ENSEMBLE_REIHEN` auswertet — mehr gibt es nicht, und
#: eine dritte hier einzutragen zeichnete ein Band ohne Daten dahinter.
BANDREIHEN = {
    "ticket_price": ("price", False),
    "booking_rate": ("booking", True),
}


def _baender(run_dir: Path) -> dict | None:
    """Die Perzentilbänder eines Ensembles — oder `None` für einen Einzellauf.

    **Der Fundort ist eine Ebene über dem Lauf.** Ein Ensemble schreibt seine
    Läufe als Unterverzeichnisse eines Batch-Ordners und die Zusammenfassung
    daneben (`multi_run_summary.json`). Ein Einzellauf hat keinen solchen
    Nachbarn, und dann bleibt es bei der Linie — das ist kein Fehlerfall,
    sondern der Normalfall.
    """

    if run_dir is None or run_dir.parent == run_dir:
        return None

    pfad = run_dir.parent / "multi_run_summary.json"
    if not pfad.is_file():
        return None
    try:
        inhalt = json.loads(pfad.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    baender = (inhalt.get("aggregate") or {}).get("baender") or {}
    reihen = baender.get("reihen") or {}
    if not reihen or int(baender.get("laeufe") or 0) < 2:
        # Ein einzelner Lauf lässt alle Perzentile zusammenfallen. Das als Band
        # zu zeichnen wäre eine Fläche der Breite null — sichtbar als nichts,
        # aber mit einer Legende, die Streuung behauptet.
        return None
    return baender


def _band_spuren(fig, baender: dict, ticks, mode: str) -> bool:
    """Für jede Reihe p10–p90 als Fläche hinter die Linie legen.

    **Erst die Fläche, dann die Linie** — Plotly zeichnet in Reihenfolge, und
    eine Fläche über der Linie verschleierte gerade den Median.

    Gezeichnet wird nur, so weit das Band trägt (`ticks`): Es ist so lang wie
    der **kürzeste** Lauf des Ensembles. Die Linie darüber darf länger sein.
    """

    gezeichnet = False
    breite = int(baender.get("ticks") or 0)
    achse = list(ticks[:breite])

    for name, (rolle, zweite_achse) in BANDREIHEN.items():
        reihe = (baender.get("reihen") or {}).get(name) or {}
        unten, oben = reihe.get("p10"), reihe.get("p90")
        if not unten or not oben:
            continue

        fig.add_trace(
            go.Scatter(
                x=achse + achse[::-1],
                y=list(oben[:breite]) + list(unten[:breite])[::-1],
                fill="toself",
                fillcolor=theme.band_fill(rolle, mode),
                line=dict(width=0),
                hoverinfo="skip",
                # **Kurz, und das ist gemessen:** Die Legende steht waagerecht
                # über der Zeichenfläche (`theme`, `y=1.02`). Mit den langen
                # Namen «Ticketpreis: 80 % der Läufe» brach sie auf zwei Zeilen
                # um und überlappte den Titel — im Browser nachgemessen, 58 px
                # Legende gegen 21 px Titel auf derselben Höhe.
                name=f"{'Buchung' if zweite_achse else 'Preis'}: 80 %",
                legendgroup=name,
            ),
            secondary_y=zweite_achse,
        )
        gezeichnet = True
    return gezeichnet


def _view_nachfrage(run_dir: Path, mode: str = theme.LIGHT):
    """**Aussage 1: Preis und Nachfrage.**

    Die Kopplung *ist* das Thema dieser Ansicht, nicht ein Nebenprodukt der
    Marktmechanik: Wie stark antwortet die Buchungsrate auf den Ticketpreis, und
    woraus setzt der Preis sich zusammen.
    """

    ticks = _read_ticks(run_dir)
    if ticks is None:
        return ui.hinweis("Keine Marktdaten verfügbar.", "info")

    price = ticks.get("market_price_after_feedback_eur")
    if price is None:
        price = ticks.get("ticket_price")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # **Das Band zuerst** (P2.6): Es gehört hinter die Linien, und Plotly
    # zeichnet in der Reihenfolge des Hinzufügens.
    baender = _baender(run_dir)
    hat_band = bool(baender) and _band_spuren(fig, baender, list(ticks["tick"]), mode)

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
    # Der Titel bleibt kurz, **auch mit Band**: Die Zahl der Läufe steht in der
    # Notiz darüber, und ein Titel, der sie wiederholt, wächst nur in die
    # Legende hinein.
    titel = "Wie die Nachfrage auf den Preis antwortet"

    blocks = [
        html.H3("Preis und Nachfrage", className=f"{ui.H3} mb-3"),
        ui.card(
            _graph(
                theme.style_figure(fig, mode=mode, title=titel),
                mode=mode,
            ),
            pad=False,
            class_name="p-2 mb-6",
        ),
    ]

    if hat_band:
        blocks.insert(
            1,
            ui.hinweis(
                f"Die Linien zeigen **diesen einen** Lauf. Die getönten Flächen zeigen, "
                f"wo **80 Prozent der {int(baender['laeufe'])} Wiederholungen** dieses "
                "Szenarios lagen — zwischen dem 10. und dem 90. Perzentil je Tick. "
                "**Nicht Minimum und Maximum:** Deren Ränder wandern mit jeder weiteren "
                "Wiederholung nach außen, ein solches Band sähe bei fünfzig Läufen "
                "breiter aus als bei zehn, ohne dass sich am Modell etwas geändert "
                f"hätte. Das Band reicht so weit wie der kürzeste Lauf (Tick "
                f"{int(baender.get('ticks') or 0)}).",
                "kontext",
            ),
        )

    if "cost_pressure" in ticks.columns and "provider_markup" in ticks.columns:
        margin = go.Figure()
        margin.add_trace(
            go.Bar(
                x=ticks["tick"],
                y=ticks["cost_pressure"],
                name="Kostendruck",
                marker_color=theme.NAVY[800],
            )
        )
        margin.add_trace(
            go.Bar(
                x=ticks["tick"],
                y=ticks["provider_markup"],
                name="Anbieter-Marge",
                marker_color=theme.NAVY[300],
            )
        )
        margin.update_xaxes(title_text="Tick")
        blocks.append(
            ui.card(
                _graph(
                    theme.style_figure(
                        margin,
                        mode=mode,
                        barmode="stack",
                        title="Woraus der Preis sich zusammensetzt",
                        yaxis_title="Betrag (EUR)",
                    ),
                    mode=mode,
                ),
                pad=False,
                class_name="p-2",
            )
        )
    return _panel(*blocks)


def _booking_rate_lines(frame, group_column: str, title: str, mode: str = theme.LIGHT):
    from dashboard.config_catalog import segment_name

    fig = go.Figure()
    for value in frame[group_column].unique():
        subset = frame[frame[group_column] == value]
        fig.add_trace(
            go.Scatter(
                x=subset["tick"],
                y=subset["booking_rate"],
                mode="lines+markers",
                # Segmente heißen nach ihrem Namen (P7.1-U1.5), Altersgruppen
                # sind schon eine Spanne und bleiben, wie sie sind.
                name=segment_name(str(value)) if group_column == "segment_id" else str(value),
            )
        )
    theme.style_figure(
        fig,
        mode=mode,
        title=title,
        xaxis_title="Tick",
        yaxis_title="Buchungsrate (0–1)",
        yaxis_range=[0, 1.05],
    )
    return fig


def _view_politik(run_dir: Path, mode: str = theme.LIGHT):
    """**Aussage 2: Was die Politik bewirkt.**

    Die politischen Instrumente und der Kostendruck, den sie erzeugen, standen
    bis zum 2026-08-30 in zwei getrennten Reitern («Policies & Steuern»,
    «Airline-Kosten»). Sie beantworten aber **eine** Frage, und zwar nur
    zusammen: Ein Verlauf der CO₂-Abgabe ohne die Kosten daneben sagt, dass
    etwas eingeführt wurde — nicht, ob es etwas bewirkt hat.
    """

    properties = _read_csv(run_dir / "timeseries" / "properties.csv")
    if properties is None:
        return ui.hinweis("Keine Property-Zeitreihen vorhanden.", "info")

    blocks: list = [html.H3("Was die Politik bewirkt", className=f"{ui.H3} mb-3")]

    instrumente = [c for c in properties.columns if c in POLICY_COLUMNS]
    if instrumente:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for column in instrumente:
            fig.add_trace(
                go.Scatter(x=properties["tick"], y=properties[column], name=_reihenname(column)),
                secondary_y=column not in ABSOLUTE_POLICY_COLUMNS,
            )
        betraege = [c for c in instrumente if c in ABSOLUTE_POLICY_COLUMNS]
        anteile = [c for c in instrumente if c not in ABSOLUTE_POLICY_COLUMNS]
        fig.update_yaxes(title_text=_achse("Betrag", betraege), secondary_y=False)
        fig.update_yaxes(title_text=_achse("Anteil", anteile), secondary_y=True)
        fig.update_xaxes(title_text="Tick")
        blocks.append(
            ui.card(
                _graph(
                    theme.style_figure(fig, mode=mode, title="Die Instrumente"),
                    mode=mode,
                ),
                pad=False,
                class_name="p-2 mb-6",
            )
        )
    else:
        blocks.append(ui.hinweis("Keine Policy-Properties gefunden.", "info"))

    kosten = [c for c in properties.columns if c in COST_COLUMNS]
    if kosten:
        fig = go.Figure()
        for column in kosten:
            fig.add_trace(
                go.Scatter(x=properties["tick"], y=properties[column], name=_reihenname(column))
            )
        fig.update_xaxes(title_text="Tick")
        fig.update_yaxes(title_text=_achse("Wert", kosten))
        blocks.append(
            ui.card(
                _graph(
                    theme.style_figure(fig, mode=mode, title="Was sie bei den Anbietern auslösen"),
                    mode=mode,
                ),
                pad=False,
                class_name="p-2",
            )
        )
    return _panel(*blocks)


def _view_wer(run_dir: Path, mode: str = theme.LIGHT):
    """**Aussage 3: Wer noch fliegt.**

    Nicht «wie viel weniger», sondern **wer** zuerst wegbleibt. Das ist die
    Frage, an der eine Strategieabteilung ihre Antwort aufhängt.
    """

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
        else ui.hinweis("Keine Profil-Segment-Daten.", "info")
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
        else ui.hinweis("Keine Altersgruppen-Daten.", "info")
    )
    return _panel(
        html.H3("Wer noch fliegt", className=f"{ui.H3} mb-3"),
        ui.grid(left, right, cols="xl:grid-cols-2"),
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


def sweep_geschwister(run_dir: Path) -> list[Path]:
    """Die anderen Szenario-Läufe neben diesem — oder keine.

    Ein Szenario-Vergleich schreibt nach `outputs/sweeps/sweep_<id>/`.
    Geschwister sind deshalb die übrigen `sweep_*`-Verzeichnisse im selben
    Ordner. Ein einzelner Lauf hat keine, **und das ist eine Auskunft, kein
    Fehler**: Ein Vergleich braucht mehr als einen Lauf.
    """

    if run_dir.parent.name != "sweeps" or not run_dir.parent.is_dir():
        return []
    return sorted(p for p in run_dir.parent.iterdir() if p.is_dir() and p.name.startswith("sweep_"))


def _szenario_name(run_dir: Path) -> str:
    """Der Name des Rahmens, unter dem ein Lauf stand — nicht der seines Ordners.

    **Der Lauf nennt ihn selbst** (`run_metadata.json` → `rahmen.name`, seit
    P2.0-B). Bis zum 2026-09-13 entstand der Name aus dem Verzeichnis: «Co2
    Delayed» statt «CO₂-Verzögerung». Nur ein Lauf ohne diese Angabe fällt auf
    den Ordner zurück.
    """

    try:
        metadaten = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
        name = (metadaten.get("rahmen") or {}).get("name")
    except (OSError, ValueError, AttributeError):
        name = None
    return str(name) if name else run_dir.name.removeprefix("sweep_").replace("_", " ")


def _endlage(run_dir: Path) -> str:
    """Die Faktorlage am Ende eines Laufs, als Text.

    **Die Faktoren sind hier Kontext, kein eigener Reiter mehr.** Als
    «CIB-Faktoren F1–F7» standen sie bis zum 2026-08-30 gleichberechtigt neben
    Preis und Nachfrage — sieben Treppenlinien, die für sich genommen keine
    Frage beantworten. Woran sie etwas erklären, ist der Vergleich: In welcher
    Weltlage endet dieses Szenario, und in welcher jenes.
    """

    factors = _read_csv(run_dir / "timeseries" / "factors.csv")
    if factors is None or factors.empty:
        return "—"
    letzte = factors.iloc[-1]
    return ", ".join(
        str(letzte[c]) for c in factors.columns if c != "tick" and isinstance(letzte[c], str)
    )


def _vergleichskurven(geschwister: list[Path], spalte: str, titel: str, achse: str, mode: str):
    fig = go.Figure()
    gezeichnet = 0
    for pfad in geschwister:
        ticks = _read_ticks(pfad)
        if ticks is None or spalte not in ticks.columns:
            continue
        fig.add_trace(
            go.Scatter(
                x=ticks["tick"],
                y=ticks[spalte],
                mode="lines",
                name=_szenario_name(pfad),
            )
        )
        gezeichnet += 1
    if not gezeichnet:
        return None
    theme.style_figure(fig, mode=mode, title=titel, xaxis_title="Tick", yaxis_title=achse)
    return fig


def _view_szenarien(run_dir: Path, mode: str = theme.LIGHT):
    """**Aussage 4: Die Szenarien nebeneinander.**

    Bis zum 2026-08-30 lagen die Szenarien in getrennten Ansichten — man konnte
    sie nacheinander ansehen, nicht vergleichen. Ein Vergleich, bei dem man sich
    die andere Kurve merken muss, ist keiner.
    """

    geschwister = sweep_geschwister(run_dir)
    if len(geschwister) < 2:
        return _panel(
            html.H3("Die Szenarien nebeneinander", className=f"{ui.H3} mb-3"),
            ui.hinweis(
                "Dieser Lauf steht allein — ein Vergleich braucht mehr als einen. "
                "Über «Einrichten → Szenario-Vergleich starten» werden alle "
                "hinterlegten Szenarien nacheinander gerechnet und landen hier "
                "nebeneinander.",
                "info",
            ),
            ui.card(
                html.Div(
                    [
                        html.P(
                            "Faktorlage am Ende dieses Laufs",
                            className=f"{ui.CAPTION} mb-1",
                        ),
                        html.P(
                            _endlage(run_dir), className=f"font-body {ui.BESCHRIFTUNG} af-text-body"
                        ),
                    ]
                ),
                class_name="mt-4",
            ),
        )

    blocks: list = [html.H3("Die Szenarien nebeneinander", className=f"{ui.H3} mb-3")]
    for spalte, titel, achse in (
        ("booking_rate", "Buchungsrate je Szenario", "Buchungsrate (0–1)"),
        ("market_price_after_feedback_eur", "Ticketpreis je Szenario", "Ticketpreis (EUR)"),
    ):
        fig = _vergleichskurven(geschwister, spalte, titel, achse, mode)
        if fig is not None:
            blocks.append(
                ui.card(_graph(fig, mode=mode), pad=False, class_name="p-2 mb-6"),
            )

    blocks.append(
        ui.card(
            html.Div(
                [
                    html.P("Faktorlage am Ende", className=f"{ui.CAPTION} mb-2"),
                    html.Table(
                        [
                            html.Tbody(
                                [
                                    html.Tr(
                                        [
                                            html.Td(
                                                _szenario_name(p),
                                                className=f"pr-4 py-1 font-body {ui.BESCHRIFTUNG} "
                                                "af-text font-semibold align-top",
                                            ),
                                            html.Td(
                                                _endlage(p),
                                                className=f"py-1 font-body {ui.BESCHRIFTUNG} af-text-body",
                                            ),
                                        ]
                                    )
                                    for p in geschwister
                                ]
                            )
                        ],
                        className="w-full",
                    ),
                ]
            )
        )
    )
    blocks.append(
        html.P(
            f"Verglichen werden alle {len(geschwister)} Szenario-Läufe unter "
            "aus einem Szenario-Vergleich — auch aus früheren Durchläufen.",
            className=f"{ui.CAPTION} mt-3",
        )
    )
    return _panel(*blocks)


def _satz_hinweis(figures) -> object:
    """Was an diesem Bildersatz nicht stimmt — oder nichts (P1.2).

    Zwei Zustände sahen bis zum 2026-08-30 aus wie ein vollständiger Satz: einer
    **ohne Manifest**, dessen Titel aus Dateinamen geraten sind, und einer, in
    dem das Manifest Dateien nennt, die es nicht gibt — die wurden still
    übersprungen. Beide bekommen jetzt einen Satz darüber.
    """

    if figures.herkunft == run_browser.GERATEN:
        return ui.hinweis(
            "Zu diesen Bildern gibt es kein Manifest. Die Titel sind aus den "
            "Dateinamen abgeleitet, und ob der Satz vollständig ist, lässt sich "
            "nicht sagen. «Figures neu erzeugen» stellt einen benannten Satz her.",
            "warnung",
        )
    if figures.fehlend:
        fehlt = ", ".join(figures.fehlend)
        return ui.hinweis(
            f"Das Manifest nennt {len(figures.fehlend)} Bild(er), die nicht "
            f"vorliegen: {fehlt}. Der Satz ist unvollständig.",
            "warnung",
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
                    else ui.hinweis("Datei liegt außerhalb des Outputs-Verzeichnisses.", "warnung")
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
    "nachfrage": _view_nachfrage,
    "politik": _view_politik,
    "wer": _view_wer,
    "szenarien": _view_szenarien,
    "png": _view_png,
}


DEFAULT_TAB = "nachfrage"


def _render_view(tab: str | None, run_dir: Path, mode: str = theme.LIGHT):
    view = _VIEWS.get(tab or DEFAULT_TAB, _view_nachfrage)
    try:
        return view(run_dir, mode)
    except Exception as exc:  # noqa: BLE001 - unvollständige Runs kommen vor
        return ui.hinweis(f"Auswertung fehlgeschlagen: {exc}", "fehler")


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
            return no_update, ui.hinweis(f"Figure-Erzeugung fehlgeschlagen: {exc}", "fehler")
        return png_gallery(run_dir), ui.hinweis(f"{len(figures)} Figures erzeugt.", "erfolg")
