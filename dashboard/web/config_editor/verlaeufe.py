"""Der Schritt «Verläufe»: wie sich die Welt im Lauf verändert (P7.13-U13.1 Teil 2a).

**Von Haiko entschieden am 2026-09-15:** ein eigener, optionaler Schritt direkt
nach der Wahl des Szenarios; links die Systemgrößen, rechts ihre Kurve über die
Lauflänge. Offen stehen die Größen, die mindestens ein Rahmenszenario verändert,
die übrigen hinter «Weitere Größen zeigen» — dasselbe Muster wie «Stresstests
zeigen» in Schritt 1: **ein** Auswahlfeld, dessen Optionen ein Knopf erweitert,
statt zweier Auswahlfelder für eine Wahl.

**Noch ohne Eingabe.** Die Kurve zeigt, was das gewählte Szenario vorgibt;
Stützpunkte und Preisstrategie folgen mit Teil 2b. Die Auswahl ist deshalb kein
Konfigurationsfeld (`controls.CFG`) und schreibt nichts in den Entwurf.

**Die Kurve rechnet wie der Lauf**: Sie kommt aus
`config_catalog.verlaeufe_je_tick`, nicht aus einer eigenen Verlaufsrechnung.
"""

from __future__ import annotations

import plotly.graph_objects as go
from dash import dcc, html

from dashboard.config_catalog import (
    EINHEITEN,
    PROPERTY_LABELS,
    exogene_groessen,
    load_properties_config,
    verlaeufe_je_tick,
    von_rahmen_veraendert,
)
from dashboard.web import components as ui
from dashboard.web import theme

#: Das Auswahlfeld der Größen. **Keine Konfigurationskennung**, siehe Modul-Docstring.
AUSWAHL = "verlaeufe-auswahl"
#: Der Wirt der Auswahl — neu gezeichnet, wenn «Weitere Größen» umschaltet.
LISTE = "verlaeufe-liste"
#: Der Knopf «Weitere Größen zeigen». Außerhalb des Wirts, sonst verlöre er
#: beim Neuzeichnen seinen Klickzähler.
WEITERE = "verlaeufe-weitere"
#: Der Wirt rechts: Name, Kurve.
KURVE = "verlaeufe-kurve"

SLOT = "verlaeufe"


def auswahl_id() -> dict:
    return {"type": AUSWAHL, "slot": SLOT}


def liste_id() -> dict:
    return {"type": LISTE, "slot": SLOT}


def weitere_id() -> dict:
    return {"type": WEITERE, "slot": SLOT}


def kurve_id() -> dict:
    return {"type": KURVE, "slot": SLOT}


def gruppen() -> tuple[list[str], list[str]]:
    """Offen und «weitere» — in Dateireihenfolge, abgeleitet statt aufgezählt."""

    alle = exogene_groessen()
    offen = von_rahmen_veraendert()
    return [g for g in alle if g in offen], [g for g in alle if g not in offen]


def name(groesse: str) -> str:
    return PROPERTY_LABELS.get(groesse, groesse)


def knopftext(gezeigt: bool) -> str:
    """Was der Knopf sagt — was ein Klick als Nächstes tut."""

    return "Weitere Größen verbergen" if gezeigt else f"Weitere Größen zeigen ({len(gruppen()[1])})"


def vorgabe(gewaehlt: str | None = None) -> str:
    """Welche Größe offen ist: die gewählte, sonst die erste offene."""

    offen, weitere = gruppen()
    if gewaehlt in offen or gewaehlt in weitere:
        return str(gewaehlt)
    return (offen or weitere)[0]


def auswahl(*, weitere: bool, gewaehlt: str | None = None) -> object:
    """Das eine Auswahlfeld — mit oder ohne die weiteren Größen.

    **Eine gewählte weitere Größe bleibt sichtbar**, wie ein gewählter Stresstest
    in Schritt 1: sonst stünde eine Auswahl da, die niemand sieht.
    """

    offen, rest = gruppen()
    wert = vorgabe(gewaehlt)
    zeigen = offen + [g for g in rest if weitere or g == wert]
    return ui.radio(
        [{"label": name(g), "value": g} for g in zeigen],
        value=wert,
        id=auswahl_id(),
        cards=True,
        legend="Welche Größe? Ihr Verlauf steht daneben.",
    )


def _einheit(groesse: str) -> str:
    from dashboard.config_catalog import CONFIGS_DIR

    properties = load_properties_config(CONFIGS_DIR / "properties.json")
    prop = properties.get_system_property(groesse)
    einheit = str(getattr(prop, "unit", "") or "")
    return EINHEITEN.get(einheit, (einheit, einheit))[0]


def figur(draft: dict, groesse: str, *, mode: str | None = theme.LIGHT) -> go.Figure:
    """Die Kurve der Größe über die Lauflänge.

    **Eine Linie, solange nichts abweicht.** Die gestrichelte Linie des Szenarios
    kommt erst dazu, wenn die eigene Fassung davon abweicht — zwei deckungsgleiche
    Linien sähen aus wie eine, und die Legende behauptete einen Unterschied.
    """

    from dashboard.web.state import draft_from_dict

    szenario, eigen = verlaeufe_je_tick(draft_from_dict(draft), groesse)
    ticks = list(range(len(eigen)))
    farben = theme.palette(mode)
    fig = go.Figure()
    if szenario != eigen:
        fig.add_trace(
            go.Scatter(
                x=ticks,
                y=szenario,
                name="Szenario",
                line=dict(color=farben["text-faint"], dash="dash", width=2),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=ticks,
            y=eigen,
            name="Dieser Lauf" if szenario != eigen else "Szenario",
            line=dict(color=farben["accent"], width=2.5),
        )
    )
    theme.style_figure(
        fig,
        mode=mode,
        height=theme.HOEHE_KOMPAKT,
        showlegend=szenario != eigen,
        xaxis_title="Tick",
        yaxis_title=_einheit(groesse),
    )
    werte = szenario + eigen
    if min(werte) == max(werte):
        fig.update_yaxes(range=_spanne_um(werte[0]))
    return fig


def _spanne_um(wert: float) -> list[float]:
    """Die Achse um einen konstanten Wert — **so, dass er abzulesen ist**.

    Plotly legt eine flache Reihe auf die Spanne ±1 um ihren Wert. Am 2026-09-15
    im Browser gesehen: Das Nachfragewachstum von 0,0025 je Tick stand dort auf
    der Linie «0», zwischen −1 und 1 — die Kurve sagte «kein Wachstum». Die Hälfte
    des Betrags nach beiden Seiten hält den Wert in der Mitte und seine
    Größenordnung auf den Achsenmarken; nur die Null bekommt ±1.
    """

    breite = abs(wert) * 0.5 or 1.0
    return [wert - breite, wert + breite]


def detail(draft: dict, groesse: str, *, mode: str | None = theme.LIGHT) -> html.Div:
    return html.Div(
        [
            html.H3(name(groesse), className=ui.H3),
            dcc.Graph(
                figure=figur(draft, groesse, mode=mode),
                config={**theme.GRAPH_CONFIG, "displayModeBar": False},
            ),
        ]
    )


def layout(draft: dict) -> object:
    """Links die Größen, rechts die Kurve. Die Kurve zeichnet ein Callback nach,
    weil nur er den Farbmodus kennt."""

    return ui.card(
        html.Div(
            [
                html.Div(
                    [
                        html.Div(auswahl(weitere=False), id=liste_id()),
                        ui.button(
                            knopftext(False),
                            id=weitere_id(),
                            variant="ghost",
                            className="mt-2",
                        ),
                    ]
                ),
                html.Div(id=kurve_id()),
            ],
            className="af-szenariowahl af-verlaeufe",
        )
    )
