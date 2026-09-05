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
#:
#: **`income_index` kam mit P2.8 dazu**, und zwar aus einem Befund: Der erste
#: Backtest ließ die Nachfrage fallen, wo real die Fluggastzahlen stiegen —
#: nicht ungenau, sondern verkehrt herum. Nachgemessen war die Ursache, dass das
#: Modell praktisch **einen einzigen** Nachfragekanal hat, den Preis, und der
#: lief unopponiert. `income_index` existierte als Systemgröße, stand auf 1,0
#: und wurde von niemandem gespeist.
#:
#: Er ist ebenfalls ein Index mit Ausgangswert 1,0 — also dieselbe Normierung
#: wie beim Ölpreis.
#:
#: **`kapazitaet_index` kam mit P2.8 dazu** (2026-08-31), und es ist die
#: Angebotsseite: Ohne sie war die Nachfragehöhe eine Konfigurationskonstante —
#: der Anbieter steuerte den Preis auf eine feste Zielauslastung, und jeder
#: Nachfrageimpuls wurde dort weggedrückt. Real wuchs der europäische Luftverkehr
#: 2015–2019 um 26 % bei flachen Realpreisen; das geht nur mit wachsendem
#: Angebot, und diese Kombination konnte das Modell vorher **nicht darstellen**.
#:
#: Die Reihe zählt **Flüge**, nicht Sitzplätze — Eurostat veröffentlicht auf
#: dieser Ebene keine Sitzplatzreihe. Sie unterschätzt das Kapazitätswachstum
#: deshalb systematisch (Flüge +14,5 % bis 2019, Passagiere +26,3 %; die
#: Differenz sind größere Flugzeuge und höhere Auslastung). Gezählt statt
#: gerechnet, und darum einem gebastelten Sitzplatzindex vorgezogen.
ZUORDNUNG = {
    "eua_auktionspreis": ("carbon_tax_level", "direkt"),
    "brent_rohoel": ("oil_price_index", "index_auf_erstes_jahr"),
    "bip_real": ("income_index", "index_auf_erstes_jahr"),
    "fluege": ("kapazitaet_index", "index_saisonbereinigt"),
}


def _gleitendes_jahresmittel(reihe: dict[str, float]) -> dict[str, float]:
    """Zwölf Monate zentriert mitteln — die Saison heraus, der Trend bleibt.

    **Warum das sein muss, und warum es keine Anpassung an den Backtest ist:**
    Die Flugzahlen schwanken saisonal um **57 Indexpunkte** im Jahr; das reale
    BIP daneben um 3, weil Eurostat es saisonbereinigt liefert. Das Modell kennt
    **keine Saison** — P2.7 hat das gemessen und deshalb auf Jahresmitteln
    verglichen. Einen Eingang mit voller Saison in ein Modell ohne Saison zu
    speisen ist derselbe Kategorienfehler, nur an der anderen Seite: Der
    Anbieter jagte einem Sollwert hinterher, der sich zwölfmal im Jahr um ein
    Drittel bewegt, und sein Regler ist auf Trends ausgelegt.

    **Kapazität ist ohnehin eine strukturelle Größe.** «Wie viel kann die
    Branche befördern» meint die Flotte und das Streckennetz, nicht die Zahl der
    Flüge im Februar.

    An den Rändern schrumpft das Fenster auf die vorhandenen Monate, statt sie
    wegzulassen: Ein Rahmen, der erst im siebten Monat beginnt, ließe den Lauf
    ein halbes Jahr auf dem Startwert stehen.
    """

    monate = sorted(reihe)
    geglaettet: dict[str, float] = {}
    for i, monat in enumerate(monate):
        fenster = monate[max(0, i - 6) : min(len(monate), i + 7)]
        geglaettet[monat] = mean(reihe[m] for m in fenster)
    return geglaettet


def _normieren(reihe: dict[str, float], art: str) -> dict[str, float]:
    if art == "direkt":
        return dict(reihe)
    if art == "index_saisonbereinigt":
        reihe = _gleitendes_jahresmittel(reihe)
    elif art != "index_auf_erstes_jahr":
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
            "Historische Außenwelt 2015–2024: EUA-Auktionspreis (EEX), "
            "Brent-Rohölpreis, reales BIP der EU-27 und die Zahl der "
            "Passagierflüge als Kapazitätsnäherung, monatlich. Alle übrigen "
            "Größen bleiben auf ihrem ausgelieferten Verlauf."
        ),
        max_ticks=len(ticks),
        property_overrides=overrides,
        milestones=[],
    )
