"""Der Schritt «Modellannahmen»: Preisbildung, Sättigung, Bevölkerung für diesen Lauf.

**Von Haiko entschieden am 2026-09-15** (P7.13-U13.5): Diese Werte lassen sich für
einen einzelnen Lauf ändern, ohne das Modell zu speichern — in einem eigenen,
optionalen Schritt direkt nach «Verläufe». Der Bereich «Modell» bleibt der Ort
für dauerhafte Standardwerte; was dort nur eingetragen wird, erreicht keinen Lauf.

**Vorbelegt mit dem gewählten Szenario**, nicht mit dem Entwurf des Modells: Die
Werte kommen aus dem Zustand, den der Lauf ohne eigene Modellannahmen bekäme.
Eingaben tragen eigene Musterkennungen (`ANNAHME`), `_sync` übersetzt sie mit
`eintraege_anwenden` in `ConfigDraft.modellannahmen` und bereinigt — das Zeichnen
des Schritts allein schreibt nichts.

**Nicht im Schritt**, bewusst: die selteneren Felder eines Segments (Modifikatoren,
Erholung, Grenzen, Verteilungstyp). Sie bleiben im Bereich «Modell»; ein Szenario,
das sie trägt, behält sie, weil `eintraege_anwenden` nur überschreibt, was der
Schritt zeigt.
"""

from __future__ import annotations

from dataclasses import asdict, replace

from dash import dcc, html

from dashboard.config_catalog import (
    abweichungen_bereinigen,
    prepare_simulation_state,
    segment_name,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import glossary
from dashboard.web.config_editor.micro import VERTEILUNG_NAMEN
from dashboard.web.config_editor.verlaeufe import SPERRGRUND

#: Ein Feld des Schritts; `pfad` ist `abschnitt.wert` oder `population.segment.wert`.
ANNAHME = "modell-annahme"

#: Die Feinabstimmung der Preisbildung: Wert, Minimum, Maximum, Schrittweite —
#: dieselben Grenzen wie im Bereich «Modell».
PREIS_FEIN = [
    ("marginal_cost_fraction", 0.05, 1.0, 0.01),
    ("markup_adjustment_per_tick", 0.01, 0.5, 0.01),
    ("damping", 0.1, 1.0, 0.05),
    ("max_price_change_fraction", 0.01, 0.5, 0.01),
    ("booking_weight", 0.0, 1.0, 0.05),
]


def annahme_id(pfad: str) -> dict:
    return {"type": ANNAHME, "pfad": pfad}


def _vorlage(draft: dict):
    """Die Modellannahmen des gewählten Szenarios — der Lauf ohne eigene."""

    from dashboard.web.state import draft_from_dict

    entwurf = replace(draft_from_dict(draft), modellannahmen={}, apply_custom_overrides=True)
    return prepare_simulation_state(entwurf).properties


def _wert(draft: dict, pfad: str, vorlage_wert):
    """Was im Feld steht: die eigene Annahme, sonst der Wert des Szenarios."""

    teile = pfad.split(".")
    eigene = draft.get("modellannahmen") or {}
    if teile[0] == "population":
        return ((eigene.get("population") or {}).get(teile[1]) or {}).get(teile[2], vorlage_wert)
    return (eigene.get(teile[0]) or {}).get(teile[1], vorlage_wert)


def _feld(pfad, label, wert, gesperrt, minimum, maximum, schritt, *, hint=None, breite=None):
    return ui.field(
        label,
        dcc.Input(
            id=annahme_id(pfad),
            type="number",
            value=wert,
            min=minimum,
            max=maximum,
            step=schritt,
            className="af-input",
            debounce=True,
            disabled=gesperrt,
        ),
        hint=hint,
        breite=breite,
    )


def _name(schluessel: str) -> str:
    param = glossary.get(schluessel)
    return param.full_label() if param else schluessel


def layout(draft: dict) -> object:
    from src.market.market_feedback import resolve_market_feedback_config

    vorlage = _vorlage(draft)
    preis = resolve_market_feedback_config(vorlage)
    gesperrt = not draft.get("apply_custom_overrides")

    def f(pfad, schluessel, ist, minimum, maximum, schritt, **extra):
        return _feld(
            pfad,
            _name(schluessel),
            _wert(draft, pfad, ist),
            gesperrt,
            minimum,
            maximum,
            schritt,
            **extra,
        )

    preisbildung = ui.card(
        html.H3("Preisbildung", className=ui.H3),
        f(
            "market_feedback.target_booking_rate",
            "market_feedback_edit.target_booking_rate",
            preis.target_booking_rate,
            0.05,
            1.0,
            0.01,
            breite="feld",
        ),
        ui.expert(
            ui.grid(
                *[
                    f(
                        f"market_feedback.{name}",
                        f"market_feedback_edit.{name}",
                        getattr(preis, name),
                        low,
                        high,
                        step,
                    )
                    for name, low, high, step in PREIS_FEIN
                ],
                cols="md:grid-cols-2",
            ),
            count=len(PREIS_FEIN),
            names="Preisuntergrenze, Reaktionsstärke, Dämpfung, Preisdeckel, Kopplung",
        ),
    )

    saettigung = ui.card(
        html.H3("Sättigung", className=ui.H3),
        f(
            "saturation.booking_increase",
            "saturation_edit.booking_increase",
            vorlage.saturation.booking_increase,
            0.0,
            1.0,
            0.05,
            breite="feld",
        ),
        ui.expert(
            f(
                "saturation.utility_penalty_factor",
                "saturation_edit.utility_penalty_factor",
                vorlage.saturation.utility_penalty_factor,
                0.0,
                3.0,
                0.1,
                breite="feld",
            ),
            count=1,
            names="Wirkung auf die Buchungsneigung",
        ),
    )

    segmente = [p for p in vorlage.individual_properties if p.type == "boolean"]
    verteilungen = [p for p in vorlage.individual_properties if p.type == "distribution"]
    bevoelkerung = ui.card(
        html.H3("Bevölkerung", className=ui.H3),
        ui.grid(
            *[
                _feld(
                    f"population.{s.id}.prevalence",
                    f"{segment_name(s.id)}: {_name('segment.prevalence')}",
                    _wert(draft, f"population.{s.id}.prevalence", s.prevalence),
                    gesperrt,
                    0.0,
                    1.0,
                    0.01,
                )
                for s in segmente
            ],
            cols="md:grid-cols-2 lg:grid-cols-3",
        ),
        (
            ui.expert(
                ui.grid(
                    *[
                        _feld(
                            f"population.{v.id}.{wert}",
                            f"{VERTEILUNG_NAMEN.get(v.id, v.id)}: {beschriftung}",
                            _wert(draft, f"population.{v.id}.{wert}", getattr(v, wert)),
                            gesperrt,
                            None,
                            None,
                            None,
                        )
                        for v in verteilungen
                        for wert, beschriftung in (("mean", "Mittelwert"), ("std_dev", "Streuung"))
                    ],
                    cols="md:grid-cols-2",
                ),
                count=2 * len(verteilungen),
                title="Streuung der Eigenschaften",
            )
            if verteilungen
            else None
        ),
    )

    return html.Div(
        [
            ui.hinweis(SPERRGRUND, "info", class_name="mb-4") if gesperrt else None,
            # **Preisbildung und Sättigung nebeneinander** (gemessen am 2026-09-15): Drei
            # Karten untereinander brauchten bei 1440 × 900 1,23 Schirme und bei
            # 1280 px 1,39.
            ui.grid(preisbildung, saettigung, cols="lg:grid-cols-2"),
            html.Div(bevoelkerung, className="mt-4"),
        ],
        className="af-modellannahmen",
    )


def eintraege_anwenden(draft: dict, eintraege: list) -> dict:
    """Die Felder des Schritts in `modellannahmen` — und bereinigt (P7.13-U13.5).

    **Beginnt bei den vorhandenen Annahmen**: Ein Szenario kann Felder tragen, die
    der Schritt nicht zeigt (etwa die Erholung eines Segments); sie blieben sonst
    beim ersten Zeichnen auf der Strecke. **Ein leeres Feld erfindet nichts** — es
    lässt stehen, was da ist. **Bereinigt**, weil die Felder beim Zeichnen ihre
    unveränderten Werte melden: Was dem Szenario gleicht, fällt weg.
    """

    from dashboard.web.state import draft_from_dict

    annahmen = {
        abschnitt: (
            {seg: dict(felder) for seg, felder in werte.items()}
            if abschnitt == "population"
            else dict(werte)
        )
        for abschnitt, werte in (draft.get("modellannahmen") or {}).items()
    }
    for eintrag in eintraege or []:
        pfad, wert = (eintrag.get("id") or {}).get("pfad"), eintrag.get("value")
        if not pfad or wert is None:
            continue
        teile = pfad.split(".")
        if teile[0] == "population":
            annahmen.setdefault("population", {}).setdefault(teile[1], {})[teile[2]] = float(wert)
        else:
            annahmen.setdefault(teile[0], {})[teile[1]] = float(wert)

    neu = {**draft, "modellannahmen": annahmen}
    bereinigt = abweichungen_bereinigen(draft_from_dict(neu))
    neu["modellannahmen"] = bereinigt.modellannahmen
    neu["abweichungen"] = {k: asdict(v) for k, v in bereinigt.abweichungen.items()}
    neu["preisstrategie"] = bereinigt.preisstrategie
    return neu
