"""Deterministic simulation functions for market and policy metrics (M2).

All numeric values for price, tax, SAF, and demand are computed here —
never parsed from LLM output.
"""

from __future__ import annotations

from src.models.state_models import PolicyEntry

METRIC_IDS = (
    "carbon_tax_level",
    "fuel_price_change",
    "oil_price_index",
    "saf_mandate_share",
    "efuel_subsidy",
    "demand_growth_rate",
)


def resolve_policy(tick: int, schedule: list[PolicyEntry]) -> dict[str, float]:
    """Return active parameter values for the given tick by applying schedule entries in order."""

    active: dict[str, float] = {}
    for entry in schedule:
        if entry.tick <= tick:
            active[entry.parameter] = entry.value
    return active


def active_parameters(
    tick: int,
    schedule: list[PolicyEntry],
    runtime_params: dict[str, float],
) -> dict[str, float]:
    """Merge scenario-parameter defaults with policy_schedule overrides for one tick."""

    params = dict(runtime_params)
    params.update(resolve_policy(tick, schedule))
    return params


def compute_ticket_price(
    base_price: float,
    carbon_tax: float,
    fuel_price_change: float,
    oil_index: float,
    saf_share: float,
    efuel_subsidy: float,
) -> float:
    """Compute ticket price from base price and current policy parameters."""

    fuel_factor = 1.0 + fuel_price_change
    oil_factor = oil_index
    carbon_surcharge = carbon_tax * 0.001
    saf_premium = saf_share * 0.5
    subsidy_offset = efuel_subsidy * saf_share
    price = base_price * fuel_factor * oil_factor + carbon_surcharge + saf_premium - subsidy_offset
    return max(1.0, price)


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


def compute_market_metrics(
    tick: int,
    schedule: list[PolicyEntry],
    runtime_params: dict[str, float],
    *,
    previous_price: float,
    base_price: float = 100.0,
    previous_demand: float = 1.0,
    price_elasticity: float = 0.5,
) -> dict[str, float]:
    """Compute all deterministic market metrics for one tick."""

    params = active_parameters(tick, schedule, runtime_params)
    anchor_price = previous_price if previous_price > 0 else base_price

    price = compute_ticket_price(
        base_price=anchor_price,
        carbon_tax=params.get("carbon_tax_level", 0.0),
        fuel_price_change=params.get("fuel_price_change", 0.0),
        oil_index=params.get("oil_price_index", 1.0),
        saf_share=params.get("saf_mandate_share", 0.0),
        efuel_subsidy=params.get("efuel_subsidy", 0.0),
    )
    price_delta = (price - anchor_price) / anchor_price if anchor_price > 0 else 0.0
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
        "demand_level": demand_level,
        "ticket_price": price,
    }
