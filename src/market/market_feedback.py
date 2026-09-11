"""Baselines für Markup und Ticketpreis plus die Auflösung der Marktrückkopplung.

Hieß bis P0.4 ``market_rules.py``. Der Name versprach die generische
Regelauswertung, die inzwischen in :mod:`src.rule_engine` liegt — dieses Modul
behandelt genau **einen** Regeltyp (``booking_yield_feedback``) und löst im
Übrigen Startwerte aus ``properties.json`` auf. Der Config-Schlüssel heißt
weiterhin ``market_rules``; umbenannt wurde nur das Modul (M4.13).
"""

from __future__ import annotations

from src.market.property_engine import resolve_trajectory
from src.models.property_models import MarketFeedbackConfig, MarketRule, PropertiesConfig

BOOKING_YIELD_FEEDBACK = "booking_yield_feedback"


def initial_provider_markup(properties: PropertiesConfig, *, tick: int) -> float:
    """Baseline for runtime ``provider_markup`` from system_properties.

    *tick* ist **Pflicht** (P0.7-Regel). Der Default ``0`` löste die Trajektorie
    vor ihrem ersten definierten Tick auf, und alle sechs Aufrufer hatten ihn
    genommen. Heute folgenlos, weil `provider_markup` im ausgelieferten Config
    eine flache Baseline ist — still falsch ab dem Tag, an dem jemand ihr im
    Editor Regeln oder eine Stufenfunktion gibt. Genau die Klasse Fehler, die
    P0.7 abgeräumt hat, nur noch nicht eingetreten.
    """

    prop = properties.get_system_property("provider_markup")
    if prop is not None:
        return resolve_trajectory(prop.trajectory, tick)
    return properties.price_model.initial_markup


def initial_ticket_price(properties: PropertiesConfig, *, tick: int) -> float:
    """Baseline for computed ``ticket_price`` from system_properties."""

    prop = properties.get_system_property("ticket_price")
    if prop is not None:
        return resolve_trajectory(prop.trajectory, tick)
    return properties.price_model.base_price + initial_provider_markup(properties, tick=tick)


def zielauslastung(
    config: MarketFeedbackConfig,
    system_properties: dict[str, float],
) -> float:
    """Wie voll der Anbieter fahren will — **Kapazität mal Sollauslastung** (P2.8).

    **Was sich damit ändert, und warum es der Kern von P2.8 ist:** Bis dahin war
    `target_booking_rate` eine feste Zahl (0,37 ohne Quelle), und der Anbieter
    steuerte den Preis, bis die Nachfrage sie traf. Damit war die
    *Nachfragehöhe* eine Konfigurationskonstante — gemessen bewegte ein
    Einkommensschock von +40 % die Buchungsrate um 4,6 %, während dieselbe
    Konstante sie verdoppelte. Der Anbieter war die Nachfrageseite.

    `kapazitaet_index` skaliert diesen Sollwert jetzt. Wächst die Kapazität, darf
    die Nachfrage mitwachsen, ohne dass der Preis sie wegdrückt — genau die
    Kombination, die real das Jahrzehnt 2015–2019 geprägt hat (+26 % Verkehr bei
    flachen Realpreisen) und die das Modell vorher **nicht darstellen konnte**.

    **Der Standard 1,0 lässt alles wie es war.** Ohne Verlauf ist das Verhalten
    identisch mit dem Stand vor P2.8; die Aussage «die Kapazität bleibt gleich»
    ist damit ausgesprochen statt unterstellt.

    **Was das nicht ist:** eine Kapazitätsschranke im engeren Sinn. Der Anbieter
    kann seinen Preis weiterhin beliebig senken; er zielt nur auf ein anderes
    Füllniveau. Eine harte Grenze («mehr Sitze gibt es nicht») wäre der nächste
    Schritt und ist in
    `docs/entscheidung_angebotsseite_2026-08-31.md` als Weg B/C beschrieben.
    """

    index = float(system_properties.get("kapazitaet_index", 1.0) or 1.0)
    return config.target_booking_rate * index


def kapazitaetsschranke(
    properties: PropertiesConfig,
    system_properties: dict[str, float],
) -> float | None:
    """Wie viele Menschen der Anbieter höchstens befördern kann — als Anteil.

    **Nur unter der Marge-Strategie eine Schranke.** Unter `auslastung` steuert
    der Anbieter den Preis auf dieses Niveau *zu*; dort ist es ein Ziel, keine
    Grenze, und die Nachfrage erreicht es ohnehin. `None` heißt «keine
    Schranke» — die Buchungen sind dann so frei wie vor P2.8.

    **Warum es die Schranke überhaupt braucht:** Ohne sie täte die Kapazität
    unter `marge` *nichts*. Der Anbieter hält seinen Aufschlag, die Nachfrage
    ergibt sich aus der Bevölkerung, und ob zehn oder tausend Sitze da sind,
    stünde nirgends in der Rechnung. Erst als Grenze wird «mehr Plätze» zu
    einer Aussage.
    """

    config = resolve_market_feedback_config(properties)
    if config.strategie != "marge":
        return None
    return zielauslastung(config, system_properties)


#: Welche Felder eine ``booking_yield_feedback``-Regel setzen darf — und wie ihr
#: Wert zu lesen ist. **Was hier nicht steht, kommt aus dem Modell**, nicht aus
#: einer zweiten Zahl an dieser Stelle (P2.11).
_FELDER: dict[str, type] = {
    "strategie": str,
    "target_booking_rate": float,
    "markup_adjustment_per_tick": float,
    "max_price_change_fraction": float,
    "damping": float,
    "booking_weight": float,
    "marginal_cost_fraction": float,
}


def resolve_market_feedback_config(properties: PropertiesConfig) -> MarketFeedbackConfig:
    """Build feedback config from ``market_rules``; fall back to ``market_feedback``.

    **Kein Rückfall auf eigene Zahlen** (P2.11, 2026-09-03). Bis dahin standen
    hier sieben Literale — ``0.37``, ``0.08``, ``0.08``, ``0.85``, ``0.6``,
    ``0.33`` und seit P2.8-B ``"auslastung"`` — neben denselben Vorgabewerten in
    :class:`MarketFeedbackConfig`. Zwei Quellen für denselben Wert, und sie waren
    bereits auseinandergelaufen: Der Rückfall hier sagte ``0.33``, die
    ausgelieferte Config ``0.25``.

    Dieselbe Klasse, die P1.9-W5.1 im Dashboard und P2.1 in
    ``booking_probability`` abgeräumt haben: *Ein Wert ohne Angabe kommt aus dem
    Modell, nicht aus einer erfundenen Zahl an der Verwendungsstelle.* Gesetzt
    wird deshalb nur, was die Regel wirklich nennt; alles andere füllt Pydantic
    aus :class:`MarketFeedbackConfig`.
    """

    for rule in properties.market_rules:
        effect = rule.effect
        if effect.get("type") != BOOKING_YIELD_FEEDBACK:
            continue
        gesetzt = {
            name: wandeln(effect[name]) for name, wandeln in _FELDER.items() if name in effect
        }
        return MarketFeedbackConfig(enabled=bool(rule.when.get("enabled", True)), **gesetzt)
    return properties.market_feedback


def active_market_rule(properties: PropertiesConfig) -> MarketRule | None:
    for rule in properties.market_rules:
        if rule.effect.get("type") == BOOKING_YIELD_FEEDBACK:
            return rule
    return None
