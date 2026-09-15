"""Der Schritt «Verläufe»: wie sich die Welt im Lauf verändert (P7.13-U13.1 Teil 2).

**Von Haiko entschieden am 2026-09-15:** ein eigener, optionaler Schritt direkt
nach der Wahl des Szenarios; links die Systemgrößen, rechts ihre Kurve über die
Lauflänge. Offen stehen die Größen, die mindestens ein Rahmenszenario verändert,
die übrigen hinter «Weitere Größen zeigen» — dasselbe Muster wie «Stresstests
zeigen» in Schritt 1: **ein** Auswahlfeld, dessen Optionen ein Knopf erweitert,
statt zweier Auswahlfelder für eine Wahl.

**Die Auswahl der Größe ist kein Konfigurationsfeld** (`controls.CFG`) und
schreibt nichts in den Entwurf. **Startwert und Stützpunkte schon** (Teil 2b):
Sie tragen eigene Musterkennungen, `_sync` liest sie und übersetzt sie mit
`eingaben_anwenden` in `ConfigDraft.abweichungen` — nie in `property_edits`, die
dem Bereich «Modell» gehören.

**Die Kurve rechnet wie der Lauf**: Sie kommt aus
`config_catalog.verlaeufe_je_tick`, nicht aus einer eigenen Verlaufsrechnung.
"""

from __future__ import annotations

from dataclasses import asdict

import plotly.graph_objects as go
from dash import dcc, html

from dashboard.config_catalog import (
    EINHEITEN,
    PROPERTY_LABELS,
    abweichungen_bereinigen,
    exogene_groessen,
    load_properties_config,
    szenario_preisstrategie,
    szenario_verlauf,
    verlaeufe_je_tick,
    von_rahmen_veraendert,
)
from dashboard.web import components as ui
from dashboard.web import theme
from src.models.property_models import STRATEGIEN

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

#: Der Startwert einer Größe.
START = "verlaeufe-start"
#: Ein Feld eines Stützpunkts: `key` ist `tick`, `art`, `wert` oder `dauer`.
PUNKT = "verlaeufe-punkt"
#: Die Kurve selbst — ihre Figur zieht ein Callback mit dem Entwurf nach.
FIGUR = "verlaeufe-figur"

#: Die Arten eines Stützpunkts, in der Sprache der Oberfläche.
ARTEN = [
    {"label": "springt auf den Wert", "value": "set"},
    {"label": "fährt hoch auf den Wert", "value": "ramp"},
]

#: Warum die Felder gesperrt sind, wenn «Eigene Werte anwenden» aus ist. Eine
#: Abweichung liegt unter demselben Schalter wie die eigenen Werte
#: (`config_catalog.prepare_simulation_state`); ohne ihn nähme das Feld eine
#: Eingabe an, die kein Lauf mitrechnet.
SPERRGRUND = (
    "Wirkt nur mit «Eigene Werte anwenden» — der Schalter steht hinter der "
    "Feinabstimmung des ersten Schritts."
)


#: «Stützpunkt hinzufügen» je Größe.
NEU = "verlaeufe-neu"
#: «Entfernen» je Zeile.
WEG = "verlaeufe-weg"
#: Der Wirt der Zeilen — neu gezeichnet, wenn eine Zeile dazukommt oder wegfällt.
ZEILEN = "verlaeufe-zeilen"


#: Die Zeilenzahl im Wirt der Zeilen — ein Eingang von `_sync`, siehe `zeilen`.
STAND = "verlaeufe-stand"

#: Die Auswahl der Preisstrategie (Teil 2b-3).
STRATEGIE = "verlaeufe-strategie"

#: Was eine Strategie tut, in der Sprache der Oberfläche — nicht ihr Name im Modell.
#: `tests/test_web_verlaeufe.py` hält die Schlüssel gegen `STRATEGIEN`, damit eine
#: neue Strategie nicht als Kennung auf dem Schirm landet.
STRATEGIE_TEXTE = {
    "auslastung": "Plätze füllen — der Preis sinkt, bis die Plätze gefüllt sind",
    "marge": "Aufschlag halten — die Auslastung schwankt",
}


def strategie_id() -> dict:
    return {"type": STRATEGIE, "slot": SLOT}


def stand_id(groesse: str) -> dict:
    return {"type": STAND, "groesse": groesse}


def neu_id(groesse: str) -> dict:
    return {"type": NEU, "groesse": groesse}


def weg_id(groesse: str, index: int) -> dict:
    return {"type": WEG, "groesse": groesse, "index": index}


def zeilen_id(groesse: str) -> dict:
    return {"type": ZEILEN, "groesse": groesse}


def start_id(groesse: str) -> dict:
    return {"type": START, "groesse": groesse}


def punkt_id(groesse: str, index: int, key: str) -> dict:
    return {"type": PUNKT, "groesse": groesse, "index": index, "key": key}


def figur_id(groesse: str) -> dict:
    return {"type": FIGUR, "groesse": groesse}


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


def verlauf_im_entwurf(draft: dict, groesse: str) -> dict:
    """Was der Editor zeigt: die eigene Abweichung, sonst das gewählte Szenario."""

    eigen = (draft.get("abweichungen") or {}).get(groesse)
    if eigen:
        return dict(eigen)
    from dashboard.web.state import draft_from_dict

    return asdict(szenario_verlauf(draft_from_dict(draft), groesse))


def _zahl(groesse: str, index: int, key: str, wert, gesperrt: bool, schritt=None):
    return dcc.Input(
        id=punkt_id(groesse, index, key),
        type="number",
        value=wert,
        step=schritt,
        className="af-input",
        debounce=True,
        disabled=gesperrt,
    )


#: Die Felder eines Stützpunkts, in der Reihenfolge der Zeile.
FELDER = ("tick", "art", "wert", "dauer")


def felder_aus_regel(regel: dict) -> dict:
    """Die Felder einer Zeile aus einer Regel des Entwurfs oder des Szenarios."""

    effekt = regel.get("effect") or {}
    return {
        "tick": regel.get("active_from_tick"),
        "art": effekt.get("type"),
        "wert": effekt.get("value"),
        "dauer": effekt.get("duration_ticks"),
    }


def felder_aus_eingaben(punkte: list, groesse: str) -> list[dict]:
    """Die Zeilen einer Größe, wie sie gerade in den Feldern stehen — nach Index."""

    zeilen: dict[int, dict] = {}
    for eintrag in punkte or []:
        kennung = eintrag.get("id") or {}
        if kennung.get("groesse") != groesse:
            continue
        zeilen.setdefault(int(kennung["index"]), {})[kennung["key"]] = eintrag.get("value")
    return [{k: zeilen[i].get(k) for k in FELDER} for i in sorted(zeilen)]


def stuetzpunkte_aendern(felder: list[dict], ausloeser: dict) -> list[dict]:
    """Eine leere Zeile dazu oder die angeklickte weg (P7.13-U13.1 Teil 2b-2).

    **Eine neue Zeile ist leer**: Ein vorbelegter Tick oder Wert wäre eine Zahl
    aus dem Quelltext, und ein vollständiger Stützpunkt rechnete sofort mit, ohne
    dass jemand ihn eingetragen hat (Regel 2).
    """

    if ausloeser.get("type") == NEU:
        return [*felder, {k: None for k in FELDER}]
    if ausloeser.get("type") == WEG:
        weg = int(ausloeser["index"])
        return [f for i, f in enumerate(felder) if i != weg]
    return felder


def _zeile(groesse: str, index: int, felder: dict, gesperrt: bool) -> html.Div:
    """Ein Stützpunkt: Kopfzeile mit «Entfernen», darunter vier Felder in zwei Spalten.

    **«Entfernen» steht in der Kopfzeile**, im Browser zweimal anders gesehen am
    2026-09-15: Als fünfte Rasterzelle stand der Knopf allein in einer Zeile, und
    der Hinweis «nur beim Hochfahren» kostete eine weitere; neben die Dauer
    gestellt, drückte er deren Feld zusammen und ihre Beschriftung auf drei
    Zeilen. Die Kopfzeile ersetzt die Hinweiszeile.
    """

    kopf = html.Div(
        [
            html.Span(f"Stützpunkt {index + 1}", className=f"{ui.BESCHRIFTUNG} af-text-muted"),
            ui.button(
                "Entfernen",
                id=weg_id(groesse, index),
                variant="ghost",
                icon_name="delete",
                disabled=gesperrt,
            ),
        ],
        className="flex items-center justify-between",
    )
    return html.Div(
        [kopf, _felder_raster(groesse, index, felder, gesperrt)],
        className="mt-3",
    )


def _felder_raster(groesse: str, index: int, felder: dict, gesperrt: bool) -> html.Div:
    return html.Div(
        ui.grid(
            ui.field("ab Tick", _zahl(groesse, index, "tick", felder.get("tick"), gesperrt, 1)),
            ui.field(
                "Art",
                dcc.Dropdown(
                    id=punkt_id(groesse, index, "art"),
                    options=ARTEN,
                    value=felder.get("art"),
                    clearable=False,
                    placeholder="Art wählen",
                    disabled=gesperrt,
                    className="af-dropdown",
                ),
            ),
            ui.field("Wert", _zahl(groesse, index, "wert", felder.get("wert"), gesperrt)),
            ui.field(
                "Dauer (Ticks)",
                _zahl(groesse, index, "dauer", felder.get("dauer"), gesperrt, 1),
            ),
            # **Zwei Spalten, nicht vier**: Das Raster folgt der Fensterbreite, der
            # Editor steht aber in der rechten Spalte. Bei 1440 × 900 schnitten vier
            # Spalten die Art auf «spri…» ab (im Browser gesehen am 2026-09-15).
            cols="sm:grid-cols-2",
            gap="gap-3",
        ),
        className="mt-3",
    )


def editor(draft: dict, groesse: str) -> html.Div:
    """Startwert und Stützpunkte der gewählten Größe.

    **Gesperrt mit Grund**, wenn «Eigene Werte anwenden» aus ist — dasselbe
    Muster wie die Felder ohne Wirkung aus P7.4: lieber sagen, warum nichts geht,
    als eine Eingabe annehmen, die kein Lauf mitrechnet.
    """

    verlauf = verlauf_im_entwurf(draft, groesse)
    gesperrt = not draft.get("apply_custom_overrides")
    return html.Div(
        [
            ui.field(
                f"Startwert ({_einheit(groesse)})",
                dcc.Input(
                    id=start_id(groesse),
                    type="number",
                    value=verlauf.get("baseline"),
                    className="af-input",
                    debounce=True,
                    disabled=gesperrt,
                ),
                hint=SPERRGRUND if gesperrt else None,
                breite="feld-klein",
            ),
            html.Div(
                zeilen(
                    groesse,
                    [felder_aus_regel(r) for r in verlauf.get("rules") or []],
                    gesperrt,
                ),
                id=zeilen_id(groesse),
            ),
            # **Außerhalb des Zeilen-Wirts**, wie «Stresstests zeigen»: Neu
            # gezeichnet setzte er seinen Klickzähler zurück.
            ui.button(
                "Stützpunkt hinzufügen",
                id=neu_id(groesse),
                variant="ghost",
                icon_name="add",
                disabled=gesperrt,
                className="mt-3",
            ),
        ],
        className="mt-4",
    )


def zeilen(groesse: str, felder: list[dict], gesperrt: bool) -> list:
    """Die Zeilen **und ein Zähler**, der `_sync` auch ohne Felder auslöst.

    `_sync` schreibt den Entwurf, sobald neue Felder eingefügt werden. Nach dem
    Entfernen der letzten Zeile gibt es keines — der `dcc.Store` mit der
    Zeilenzahl wird trotzdem neu eingefügt und ist ein Eingang von `_sync`.
    """

    return [
        *[_zeile(groesse, index, f, gesperrt) for index, f in enumerate(felder)],
        dcc.Store(id=stand_id(groesse), data=len(felder)),
    ]


def strategie(draft: dict) -> html.Div:
    """Die Preisstrategie des Laufs (P7.13-U13.1 Teil 2b-3).

    **Links unter der Liste der Größen** (von Haiko entschieden am 2026-09-15,
    nach einer Messung): Rechts unter dem Editor, wie zuerst entschieden, wurde
    der Schritt bei 1440 × 900 1,12 Schirme hoch statt 1,00 und bei 1280 px 1,27
    statt 1,13; links nutzt sie den freien Platz der Spalte, und beide Zahlen
    bleiben. Sie gehört zu keiner einzelnen Größe, ist aber wie die Verläufe eine
    Annahme des Szenarios über die Welt.
    Vorbelegt mit der eigenen Wahl, sonst mit der Strategie des Szenarios; was ihr
    gleicht, zählt nicht als Abweichung (`abweichungen_bereinigen`).
    """

    from dashboard.web.state import draft_from_dict

    wert = draft.get("preisstrategie") or szenario_preisstrategie(draft_from_dict(draft))
    gesperrt = not draft.get("apply_custom_overrides")
    return html.Div(
        [
            html.H3("Preisstrategie", className=ui.H3),
            ui.radio(
                [
                    {"label": STRATEGIE_TEXTE.get(s, s), "value": s, "disabled": gesperrt}
                    for s in STRATEGIEN
                ],
                value=wert,
                id=strategie_id(),
                legend="Preisstrategie: wie der Anbieter in diesem Lauf preist.",
            ),
        ],
        className="mt-6",
    )


def detail(draft: dict, groesse: str, *, mode: str | None = theme.LIGHT) -> html.Div:
    return html.Div(
        [
            html.H3(name(groesse), className=ui.H3),
            dcc.Graph(
                id=figur_id(groesse),
                figure=figur(draft, groesse, mode=mode),
                config={**theme.GRAPH_CONFIG, "displayModeBar": False},
            ),
            editor(draft, groesse),
        ]
    )


def szenario_name(wahl: str) -> str:
    """Wie ein Szenario in einer Meldung heißt — sein Name, nicht seine Kennung."""

    from dashboard.web.config_editor import start_flow

    if wahl == start_flow.STANDARD:
        return "Standard-Ausgangslage"
    from dashboard.config_catalog import list_sweep_presets

    return next((p.name for p in list_sweep_presets() if p.id == wahl), wahl)


def nach_szenariowechsel(vorher: dict, nachher: dict) -> tuple[dict, bool]:
    """Ein Wechsel des Szenarios verwirft die Abweichungen (P7.13-U13.2 Teil 2).

    **Von Haiko entschieden am 2026-09-14:** Eine Abweichung ist der Unterschied
    zu **einem** Szenario. Auf ein anderes gelegt, hieße «CO₂-Abgabe ab Tick 19
    auf 120» dort etwas anderes — und der Lauf stünde als «abgeleitet» von einem
    Szenario im Artefakt, dessen Verläufe niemand angesehen hat. **Mit
    «Rückgängig»**, weil ein Klick in der Liste sonst Arbeit ohne Weg zurück
    verwirft.

    Liefert den Entwurf nach dem Wechsel und ob etwas verworfen wurde. Ohne
    Abweichungen oder ohne Wechsel bleibt der Entwurf, wie er ist.
    """

    from dashboard.web.config_editor import start_flow

    if start_flow.of(vorher) == start_flow.of(nachher):
        return nachher, False
    if not (vorher.get("abweichungen") or vorher.get("preisstrategie")):
        return nachher, False
    return {**nachher, "abweichungen": {}, "preisstrategie": None}, True


def _regel(felder: dict) -> dict | None:
    """Ein Stützpunkt aus seinen Feldern — **oder keiner**, solange etwas fehlt.

    Ein leeres Feld wird nicht mit einer erfundenen Zahl gefüllt (Regel 2 aus
    P1.9-W5.1): Ein Stützpunkt ohne Tick oder Wert rechnet nicht mit, bis er
    vollständig ist.
    """

    tick, art, wert = felder.get("tick"), felder.get("art"), felder.get("wert")
    if tick is None or art not in {"set", "ramp"} or wert is None:
        return None
    effekt: dict = {"type": art, "value": float(wert)}
    if art == "ramp":
        if felder.get("dauer") is None:
            return None
        effekt["duration_ticks"] = int(felder["dauer"])
    return {"active_from_tick": int(tick), "effect": effekt}


def eingaben_anwenden(
    draft: dict, starts: list, punkte: list, strategien: list | None = None
) -> dict:
    """Startwert und Stützpunkte aus dem Schritt in `abweichungen` — und bereinigt.

    **Bereinigt, weil das Zeichnen allein schreibt**: Sobald der Schritt steht,
    melden seine Felder ihre unveränderten Werte, und `_sync` ruft diese Funktion.
    Ohne `abweichungen_bereinigen` stünde danach jede angesehene Größe als
    «abgeleitet» im Artefakt.
    """

    zeilen: dict[str, dict[int, dict]] = {}
    for eintrag in punkte or []:
        kennung = eintrag.get("id") or {}
        zeilen.setdefault(kennung["groesse"], {}).setdefault(int(kennung["index"]), {})[
            kennung["key"]
        ] = eintrag.get("value")
    startwerte = {(e.get("id") or {})["groesse"]: e.get("value") for e in starts or []}
    groessen = set(startwerte) | set(zeilen)
    if not groessen and not strategien:
        return draft

    abweichungen = {k: dict(v) for k, v in (draft.get("abweichungen") or {}).items()}
    for groesse in groessen:
        basis = startwerte.get(groesse)
        if basis is None:
            continue
        regeln = [_regel(felder) for _, felder in sorted(zeilen.get(groesse, {}).items())]
        abweichungen[groesse] = {
            "property_id": groesse,
            "baseline": float(basis),
            "rules": [r for r in regeln if r is not None],
            "is_active": True,
        }

    from dashboard.web.state import draft_from_dict

    neu = {**draft, "abweichungen": abweichungen}
    for eintrag in strategien or []:
        neu["preisstrategie"] = eintrag.get("value")
    bereinigt = abweichungen_bereinigen(draft_from_dict(neu))
    neu["abweichungen"] = {k: asdict(v) for k, v in bereinigt.abweichungen.items()}
    neu["preisstrategie"] = bereinigt.preisstrategie
    return neu


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
                        strategie(draft),
                    ]
                ),
                html.Div(id=kurve_id()),
            ],
            className="af-szenariowahl af-verlaeufe",
        )
    )
