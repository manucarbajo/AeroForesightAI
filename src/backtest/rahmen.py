"""Die historischen Reihen als Rahmenszenario — die Umdrehung aus P2.0 im Einsatz.

Der Backtest ist der erste Anwender, für den «Rahmen statt Richter» nicht nur
eine Aufräumaktion ist: Er speist eine **historische Außenwelt** ein und lässt
den Lauf Nachfrage und Preise daraus erzeugen. Vor P2.0 ging das nicht, ohne
zugleich den Endzustand vorzugeben — der Backtest wäre zirkulär gewesen. Genau
deshalb steht P2.7 im Plan hinter P2.0.
"""

from __future__ import annotations

from statistics import mean

from src.backtest.reihen import Reihe, tick_je_monat
from src.models.sweep_models import PropertyOverride, SweepConfig

#: Welche Modellgröße welche Reihe bekommt — und wie sie umgerechnet wird.
#:
#: `carbon_tax_level` steht in EUR je Tonne, der EUA-Auktionspreis auch: keine
#: Umrechnung. `oil_price_index` ist dagegen ein **Index** mit Ausgangswert 1,0,
#: Brent steht in USD je Barrel. Die Reihe wird deshalb auf ihr Mittel des
#: **ersten Jahres** normiert — dieselbe Basis wie die Zielreihe (2015 = 100).
#: Ein roher Dollarpreis an dieser Stelle hieße Ölpreisindex 52 statt 1,0.
ZUORDNUNG = {
    "eua_auktionspreis": ("carbon_tax_level", "direkt"),
    "brent_rohoel": ("oil_price_index", "index_auf_erstes_jahr"),
}


def _normieren(reihe: dict[str, float], art: str) -> dict[str, float]:
    if art == "direkt":
        return dict(reihe)
    if art != "index_auf_erstes_jahr":
        raise ValueError(f"Unbekannte Umrechnung: {art}")

    erstes_jahr = min(reihe)[:4]
    basis = mean(w for m, w in reihe.items() if m.startswith(erstes_jahr))
    if basis == 0:
        raise ValueError("Basis des ersten Jahres ist null — Index nicht bildbar")
    return {m: w / basis for m, w in reihe.items()}


def historischer_rahmen(
    reihen: dict[str, Reihe], *, name: str = "Backtest 2015–2024"
) -> SweepConfig:
    """Ein Rahmenszenario aus historischen Monatsreihen.

    Jeder Monat wird zu einer Regel «ab Tick n gilt Wert x». Das ist derselbe
    Mechanismus, den die ausgelieferten Szenarien benutzen — der Backtest bekommt
    keinen Sonderweg in die Engine, sondern benutzt den vorhandenen.

    **Lücken werden fortgeschrieben** (`Reihe.fortgeschrieben`), sonst spränge die
    Größe im Modell auf ihren Ausgangswert zurück. Für die *Auswertung* gelten
    weiterhin die beobachteten Werte.
    """

    ticks = tick_je_monat()
    overrides: list[PropertyOverride] = []

    for reihen_name, (property_id, art) in ZUORDNUNG.items():
        reihe = reihen.get(reihen_name)
        if reihe is None:
            raise KeyError(
                f"Der Rahmen braucht die Reihe `{reihen_name}` für `{property_id}`. "
                "Sie zu überspringen hieße, das Modell mit seinem ausgelieferten "
                "Verlauf rechnen zu lassen und das Ergebnis historisch zu nennen."
            )
        werte = _normieren(reihe.fortgeschrieben(), art)
        overrides.append(
            PropertyOverride(
                property_id=property_id,
                baseline=werte[min(werte)],
                rules=[
                    {
                        "active_from_tick": ticks[monat],
                        "effect": {"type": "set", "value": round(wert, 6)},
                    }
                    for monat, wert in sorted(werte.items())
                ],
            )
        )

    return SweepConfig(
        id="backtest_2015_2024",
        name=name,
        description=(
            "Historische Außenwelt 2015–2024: EUA-Auktionspreis (EEX) und "
            "Brent-Rohölpreis, monatlich. Alle übrigen Größen bleiben auf ihrem "
            "ausgelieferten Verlauf."
        ),
        max_ticks=len(ticks),
        property_overrides=overrides,
        milestones=[],
    )
