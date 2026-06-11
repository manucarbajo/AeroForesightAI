"""Deterministic simulation functions for market and policy metrics (M2/M4).

All numeric values for price, tax, SAF, and demand are computed here —
never parsed from LLM output.
"""

from __future__ import annotations

from src.market_rules import initial_provider_markup, resolve_market_feedback_config
from src.models.property_models import (
    MarketFeedbackConfig,
    PriceCoefficientsConfig,
    PriceModelConfig,
    PropertiesConfig,
)
from src.property_engine import MARKET_PROPERTY_IDS, resolve_exogenous_system_properties

METRIC_IDS = MARKET_PROPERTY_IDS


def active_parameters(tick: int, properties: PropertiesConfig) -> dict[str, float]:
    """Return active exogenous system property values for one tick."""

    return resolve_exogenous_system_properties(tick, properties)


def compose_ticket_price(cost_pressure: float, provider_markup: float) -> float:
    """M4.13: published ticket price from cost layer + runtime margin property."""

    return cost_pressure + max(0.0, provider_markup)


def compute_ticket_price(
    base_price: float,
    carbon_tax: float,
    fuel_price_change: float,
    oil_index: float,
    saf_share: float,
    efuel_subsidy: float,
    *,
    coefficients: PriceCoefficientsConfig | None = None,
) -> float:
    """Compute ticket cost from base price and policy parameters (coefficients from config)."""

    coeffs = coefficients or PriceCoefficientsConfig()
    fuel_factor = 1.0 + fuel_price_change
    oil_factor = oil_index
    carbon_surcharge = carbon_tax * coeffs.carbon_per_tonne
    saf_premium = saf_share * coeffs.saf_premium_factor
    subsidy_offset = efuel_subsidy * saf_share
    price = base_price * fuel_factor * oil_factor + carbon_surcharge + saf_premium - subsidy_offset
    return max(coeffs.min_ticket_price, price)


def update_cost_index(previous_index: float, fuel_price_change: float) -> float:
    """M4: accumulate fuel inflation on cost layer (not on prior ticket price)."""

    return max(0.1, previous_index * (1.0 + fuel_price_change))


def compute_cost_pressure(
    tick: int,
    properties: PropertiesConfig,
    *,
    price_model: PriceModelConfig | None = None,
    cost_index: float = 1.0,
) -> float:
    """M4: cost component from ``price_model.base_price``, not previous ticket price."""

    model = price_model or properties.price_model
    params = active_parameters(tick, properties)
    effective_base = model.base_price * cost_index
    fuel_change = 0.0 if model.compound_fuel_on_cost else params.get("fuel_price_change", 0.0)
    return compute_ticket_price(
        base_price=effective_base,
        carbon_tax=params.get("carbon_tax_level", 0.0),
        fuel_price_change=fuel_change,
        oil_index=params.get("oil_price_index", 1.0),
        saf_share=params.get("saf_mandate_share", 0.0),
        efuel_subsidy=params.get("efuel_subsidy", 0.0),
        coefficients=model.coefficients,
    )


def clip_price_change(
    new_price: float,
    previous_price: float,
    max_fraction: float,
) -> float:
    """M4: limit per-tick price delta (numerical stability)."""

    if previous_price <= 0:
        return max(1.0, new_price)
    max_delta = previous_price * max_fraction
    delta = new_price - previous_price
    if abs(delta) <= max_delta:
        return max(1.0, new_price)
    return max(1.0, previous_price + max(-max_delta, min(max_delta, delta)))


def apply_market_feedback(
    cost_pressure: float,
    booking_rate: float,
    previous_markup: float,
    previous_ticket_price: float,
    config: MarketFeedbackConfig,
    *,
    coefficients: PriceCoefficientsConfig | None = None,
) -> tuple[float, float]:
    """M4: adjust provider_markup from observed booking rate vs target."""

    coeffs = coefficients or PriceCoefficientsConfig()

    if not config.enabled:
        markup = max(0.0, previous_markup)
        price = clip_price_change(
            compose_ticket_price(cost_pressure, markup),
            previous_ticket_price,
            config.max_price_change_fraction,
        )
        return price, max(0.0, price - cost_pressure)

    gap = booking_rate - config.target_booking_rate
    anchor = previous_ticket_price if previous_ticket_price > 0 else compose_ticket_price(cost_pressure, previous_markup)
    scale = max(cost_pressure, 1.0)
    markup_delta = (
        config.damping
        * gap
        * config.markup_adjustment_per_tick
        * max(previous_markup, scale * coeffs.margin_reference_fraction)
    )
    markup_path_price = compose_ticket_price(cost_pressure, max(0.0, previous_markup + markup_delta))
    yield_multiplier = 1.0 + config.damping * gap * config.markup_adjustment_per_tick
    yield_path_price = anchor * yield_multiplier
    raw_price = min(markup_path_price, yield_path_price) if gap < 0 else max(markup_path_price, yield_path_price)
    if booking_rate >= config.target_booking_rate * coeffs.target_booking_tolerance:
        target_margin = max(coeffs.margin_floor_fraction, previous_markup / scale) if scale > 0 else coeffs.margin_reference_fraction
        raw_price = max(raw_price, cost_pressure * (1.0 + target_margin))
    new_price = clip_price_change(raw_price, anchor, config.max_price_change_fraction)
    new_markup = max(0.0, new_price - cost_pressure)
    return new_price, new_markup


def sync_demand_level(
    booking_rate: float,
    previous_demand: float,
    growth_rate: float,
    *,
    target_booking_rate: float = 0.75,
    booking_weight: float = 0.6,
) -> float:
    """M4: couple macro demand index to observed micro booking rate."""

    macro = previous_demand * (1.0 + growth_rate)
    if target_booking_rate > 0:
        booking_component = (booking_rate / target_booking_rate)
    else:
        booking_component = booking_rate
    booking_component = max(0.0, min(2.0, booking_component))
    demand = (1.0 - booking_weight) * macro + booking_weight * booking_component
    return max(0.0, min(2.0, demand))


def compute_demand(
    base_demand: float,
    growth_rate: float,
    price_elasticity: float,
    price_delta: float,
) -> float:
    """Compute demand level from base demand, growth, and price effect."""

    growth_factor = 1.0 + growth_rate
    price_effect = 1.0 - price_elasticity * price_delta
    demand = base_demand * growth_factor * price_effect
    return max(0.0, min(2.0, demand))


def _runtime_markup(properties: PropertiesConfig, previous_markup: float | None) -> float:
    if previous_markup is not None:
        return previous_markup
    return initial_provider_markup(properties)


def compute_market_metrics(
    tick: int,
    properties: PropertiesConfig,
    *,
    previous_price: float,
    base_price: float = 100.0,
    previous_demand: float = 1.0,
    previous_markup: float | None = None,
    previous_cost_index: float = 1.0,
    booking_rate: float | None = None,
    price_elasticity: float = 0.5,
) -> dict[str, float]:
    """Compute deterministic market metrics for one tick (M4-aware)."""

    params = active_parameters(tick, properties)
    price_model = properties.price_model
    feedback = resolve_market_feedback_config(properties)
    coefficients = price_model.coefficients

    anchor_price = previous_price if previous_price > 0 else base_price
    provider_markup = _runtime_markup(properties, previous_markup)
    fuel_change = params.get("fuel_price_change", 0.0)
    if price_model.compound_fuel_on_cost:
        cost_index = update_cost_index(previous_cost_index, fuel_change)
    else:
        cost_index = previous_cost_index
    cost_pressure = compute_cost_pressure(tick, properties, cost_index=cost_index)

    if booking_rate is not None and feedback.enabled:
        ticket_price, provider_markup = apply_market_feedback(
            cost_pressure,
            booking_rate,
            provider_markup,
            anchor_price,
            feedback,
            coefficients=coefficients,
        )
        demand_level = sync_demand_level(
            booking_rate,
            previous_demand,
            params.get("demand_growth_rate", 0.0),
            target_booking_rate=feedback.target_booking_rate,
            booking_weight=feedback.booking_weight,
        )
    else:
        ticket_price = compose_ticket_price(cost_pressure, provider_markup)
        ticket_price = clip_price_change(ticket_price, anchor_price, feedback.max_price_change_fraction)
        provider_markup = max(0.0, ticket_price - cost_pressure)
        price_delta = (ticket_price - anchor_price) / anchor_price if anchor_price > 0 else 0.0
        demand_level = compute_demand(
            base_demand=previous_demand,
            growth_rate=params.get("demand_growth_rate", 0.0),
            price_elasticity=price_elasticity,
            price_delta=price_delta,
        )

    return {
        "carbon_tax_level": params.get("carbon_tax_level", 0.0),
        "fuel_price_change": params.get("fuel_price_change", 0.0),
        "oil_price_index": params.get("oil_price_index", 1.0),
        "saf_mandate_share": params.get("saf_mandate_share", 0.0),
        "efuel_subsidy": params.get("efuel_subsidy", 0.0),
        "demand_growth_rate": params.get("demand_growth_rate", 0.0),
        "cost_pressure": cost_pressure,
        "cost_index": cost_index,
        "provider_markup": provider_markup,
        "markup": provider_markup,
        "demand_level": demand_level,
        "ticket_price": ticket_price,
        **({"booking_rate": booking_rate} if booking_rate is not None else {}),
    }
