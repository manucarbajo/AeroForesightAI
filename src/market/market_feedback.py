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


def resolve_market_feedback_config(properties: PropertiesConfig) -> MarketFeedbackConfig:
    """Build feedback config from ``market_rules``; fall back to ``market_feedback``."""

    for rule in properties.market_rules:
        effect = rule.effect
        if effect.get("type") != BOOKING_YIELD_FEEDBACK:
            continue
        when = rule.when
        enabled = when.get("enabled", True)
        return MarketFeedbackConfig(
            enabled=bool(enabled),
            target_booking_rate=float(effect.get("target_booking_rate", 0.37)),
            markup_adjustment_per_tick=float(effect.get("markup_adjustment_per_tick", 0.08)),
            max_price_change_fraction=float(effect.get("max_price_change_fraction", 0.08)),
            damping=float(effect.get("damping", 0.85)),
            booking_weight=float(effect.get("booking_weight", 0.6)),
            marginal_cost_fraction=float(effect.get("marginal_cost_fraction", 0.33)),
        )
    return properties.market_feedback


def active_market_rule(properties: PropertiesConfig) -> MarketRule | None:
    for rule in properties.market_rules:
        if rule.effect.get("type") == BOOKING_YIELD_FEEDBACK:
            return rule
    return None
