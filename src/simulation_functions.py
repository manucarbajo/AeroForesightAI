"""Deterministic simulation functions for market and policy metrics.

All numeric values for price, tax, SAF, and demand are computed here,
never parsed from LLM output.
"""

from __future__ import annotations

from src.market_rules import initial_provider_markup, resolve_market_feedback_config

from src.models.state_models import FactorState
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


def compose_ticket_price(
    cost_pressure: float,
    provider_markup: float,
    *,
    properties: PropertiesConfig | None = None,
    tick: int = 0,
) -> float:
    """published ticket price from cost layer + runtime margin property.

    Custom taxes (percentage on base) and fees (absolute surcharges) defined
    via ``price_component_type`` on system properties are applied here:
        final = (base) * (1 + sum_of_tax_rates) + sum_of_absolute_fees
    """
    base = cost_pressure + max(0.0, provider_markup)

    if properties is None:
        return base

    params = active_parameters(tick, properties)
    total_tax_rate = 0.0
    total_fees = 0.0
    for sp in properties.system_properties:
        if sp.price_component_type == "tax":
            total_tax_rate += params.get(sp.id, 0.0)
        elif sp.price_component_type == "fee":
            total_fees += params.get(sp.id, 0.0)

    return base * (1.0 + total_tax_rate) + total_fees


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

    """accumulate fuel inflation on cost layer (not on prior ticket price)."""
    return max(0.1, previous_index * (1.0 + fuel_price_change))


def compute_cost_pressure(
    tick: int,
    properties: PropertiesConfig,
    *,
    price_model: PriceModelConfig | None = None,
    cost_index: float = 1.0,
    factors: dict[str, FactorState] | None = None,
    system_properties: dict[str, float] | None = None,

) -> float:

    """cost component from ``price_model.base_price``, not previous ticket price."""
    model = price_model or properties.price_model

    params = active_parameters(tick, properties)

    effective_base = model.base_price * cost_index

    fuel_change = 0.0 if model.compound_fuel_on_cost else params.get("fuel_price_change", 0.0)

    base_cost = compute_ticket_price(
        base_price=effective_base,
        carbon_tax=params.get("carbon_tax_level", 0.0),
        fuel_price_change=fuel_change,
        oil_index=params.get("oil_price_index", 1.0),
        saf_share=params.get("saf_mandate_share", 0.0),
        efuel_subsidy=params.get("efuel_subsidy", 0.0),
        coefficients=model.coefficients,
    )

    regulatory_cost = 0.0
    factors_dict = factors or {}
    sys_props = system_properties or {}

    for reg in properties.regulatory_influences:
        active = True
        when = reg.when
        if when:
            if "factor" in when:
                factor_id = str(when["factor"])
                expected_state = str(when.get("state", ""))
                factor = factors_dict.get(factor_id)
                if factor is None or factor.current_state != expected_state:
                    active = False
            if "system_property" in when and active:
                prop_id = str(when["system_property"])
                value = sys_props.get(prop_id)
                if value is None:
                    active = False
                elif "above" in when and value <= float(when["above"]):
                    active = False
                elif "below" in when and value >= float(when["below"]):
                    active = False
        if active:
            from src.property_engine import resolve_trajectory
            traj_val = resolve_trajectory(reg.trajectory, tick)
            regulatory_cost += reg.cost_contribution + traj_val

    maintenance_idx = sys_props.get("maintenance_cost_index", 1.0)
    staff_idx = sys_props.get("staff_cost_index", 1.0)
    adjusted_base_cost = base_cost * maintenance_idx * staff_idx
    return adjusted_base_cost + regulatory_cost


def clip_price_change(
    new_price: float,
    previous_price: float,
    max_fraction: float,
) -> float:

    """limit per-tick price delta (numerical stability)."""
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
    properties: PropertiesConfig | None = None,
    tick: int = 0,

) -> tuple[float, float]:

    """adjust provider_markup from observed booking rate vs target."""
    coeffs = coefficients or PriceCoefficientsConfig()

    if not config.enabled:

        markup = max(0.0, previous_markup)

        price = clip_price_change(
            compose_ticket_price(cost_pressure, markup, properties=properties, tick=tick),
            previous_ticket_price,
            config.max_price_change_fraction,
        )

        return price, max(0.0, price - cost_pressure)

    gap = booking_rate - config.target_booking_rate

    anchor = previous_ticket_price if previous_ticket_price > 0 else compose_ticket_price(cost_pressure, previous_markup, properties=properties, tick=tick)

    scale = max(cost_pressure, 1.0)

    markup_delta = (
        config.damping

        * gap

        * config.markup_adjustment_per_tick

        * max(previous_markup, scale * coeffs.margin_reference_fraction)

    )

    markup_path_price = compose_ticket_price(cost_pressure, max(0.0, previous_markup + markup_delta), properties=properties, tick=tick)

    yield_multiplier = 1.0 + config.damping * gap * config.markup_adjustment_per_tick

    yield_path_price = anchor * yield_multiplier

    raw_price = min(markup_path_price, yield_path_price) if gap < 0 else max(markup_path_price, yield_path_price)

    if booking_rate >= config.target_booking_rate * coeffs.target_booking_tolerance:

        target_margin = max(coeffs.margin_floor_fraction, previous_markup / scale) if scale > 0 else coeffs.margin_reference_fraction

        raw_price = max(raw_price, cost_pressure * (1.0 + target_margin))

    # Hard Floor (Die Rote Linie): Der Preis darf niemals unter die Grenzkosten + Steuern + Gebühren fallen.
    # Das erlaubt Loss-Leading zur Deckung von Fixkosten, verbietet aber Dumping unter die echten Grenzkosten.
    marginal_cost = cost_pressure * config.marginal_cost_fraction
    floor_price = compose_ticket_price(marginal_cost, 0.0, properties=properties, tick=tick)
    raw_price = max(raw_price, floor_price)

    new_price = clip_price_change(raw_price, anchor, config.max_price_change_fraction)

    params = active_parameters(tick, properties) if properties else {}
    total_tax_rate = sum(params.get(sp.id, 0.0) for sp in properties.system_properties if sp.price_component_type == "tax") if properties else 0.0
    total_fees = sum(params.get(sp.id, 0.0) for sp in properties.system_properties if sp.price_component_type == "fee") if properties else 0.0

    base_price_no_tax = (new_price - total_fees) / max(1e-6, 1.0 + total_tax_rate)
    new_markup = max(0.0, base_price_no_tax - cost_pressure)

    return new_price, new_markup


def sync_demand_level(
    booking_rate: float,
    previous_demand: float,
    growth_rate: float,
    *,
    target_booking_rate: float = 0.75,
    booking_weight: float = 0.6,

) -> float:

    """couple macro demand index to observed micro booking rate."""
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
    factors: dict[str, FactorState] | None = None,
    system_properties: dict[str, float] | None = None,

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

    cost_pressure = compute_cost_pressure(tick, properties, cost_index=cost_index, factors=factors, system_properties=system_properties)

    if booking_rate is not None and feedback.enabled:

        ticket_price, provider_markup = apply_market_feedback(
            cost_pressure,
            booking_rate,
            provider_markup,
            anchor_price,
            feedback,
            coefficients=coefficients,
            properties=properties,
            tick=tick,
        )

        demand_level = sync_demand_level(
            booking_rate,
            previous_demand,
            params.get("demand_growth_rate", 0.0),
            target_booking_rate=feedback.target_booking_rate,
            booking_weight=feedback.booking_weight,
        )

    else:

        ticket_price = compose_ticket_price(cost_pressure, provider_markup, properties=properties, tick=tick)

        ticket_price = clip_price_change(ticket_price, anchor_price, feedback.max_price_change_fraction)

        total_tax_rate = sum(params.get(sp.id, 0.0) for sp in properties.system_properties if sp.price_component_type == "tax") if properties else 0.0
        total_fees = sum(params.get(sp.id, 0.0) for sp in properties.system_properties if sp.price_component_type == "fee") if properties else 0.0
        base_price_no_tax = (ticket_price - total_fees) / max(1e-6, 1.0 + total_tax_rate)

        provider_markup = max(0.0, base_price_no_tax - cost_pressure)

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

