"""Resolve market feedback config and runtime property baselines from properties.json (M4.13)."""

from __future__ import annotations

from src.models.property_models import MarketFeedbackConfig, MarketRule, PropertiesConfig
from src.property_engine import resolve_trajectory

BOOKING_YIELD_FEEDBACK = "booking_yield_feedback"


def initial_provider_markup(properties: PropertiesConfig, *, tick: int = 0) -> float:
    """Baseline for runtime ``provider_markup`` from system_properties."""

    prop = properties.get_system_property("provider_markup")
    if prop is not None:
        return resolve_trajectory(prop.trajectory, tick)
    return properties.price_model.initial_markup


def initial_ticket_price(properties: PropertiesConfig, *, tick: int = 0) -> float:
    """Baseline for computed ``ticket_price`` from system_properties."""

    prop = properties.get_system_property("ticket_price")
    if prop is not None:
        return resolve_trajectory(prop.trajectory, tick)
    return properties.price_model.base_price + initial_provider_markup(properties, tick=tick)


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
            target_booking_rate=float(effect.get("target_booking_rate", 0.75)),
            markup_adjustment_per_tick=float(effect.get("markup_adjustment_per_tick", 0.06)),
            max_price_change_fraction=float(effect.get("max_price_change_fraction", 0.08)),
            damping=float(effect.get("damping", 0.85)),
            booking_weight=float(effect.get("booking_weight", 0.6)),
        )
    return properties.market_feedback


def active_market_rule(properties: PropertiesConfig) -> MarketRule | None:
    for rule in properties.market_rules:
        if rule.effect.get("type") == BOOKING_YIELD_FEEDBACK:
            return rule
    return None
