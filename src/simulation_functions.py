"""Deterministic simulation functions for market and policy metrics (M2).

All numeric values for price, tax, SAF, and demand are computed here —
never parsed from LLM output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.state_models import PolicySchedule

METRIC_IDS = (
    "carbon_tax_level",
    "fuel_price_change",
    "oil_price_index",
    "saf_mandate_share",
    "efuel_subsidy",
    "demand_growth_rate",
)

DEFAULT_BASELINE: dict[str, float] = {
    "carbon_tax_level": 0.0,
    "fuel_price_change": 0.02,
    "oil_price_index": 100.0,
    "saf_mandate_share": 0.0,
    "efuel_subsidy": 0.0,
    "demand_growth_rate": 0.03,
}


def _baseline_value(schedule: PolicySchedule | None, parameter_id: str) -> float:
    if schedule is None:
        return DEFAULT_BASELINE.get(parameter_id, 0.0)
    return schedule.baseline.get(parameter_id, DEFAULT_BASELINE.get(parameter_id, 0.0))


def _resolve_parameter(tick: int, parameter_id: str, schedule: PolicySchedule | None) -> float:
    """Apply policy_schedule rules for one parameter at the given tick."""

    value = _baseline_value(schedule, parameter_id)
    if schedule is None:
        return value

    for rule in schedule.rules:
        if rule.parameter != parameter_id:
            continue
        if tick < rule.active_from_tick:
            continue
        if rule.active_until_tick is not None and tick > rule.active_until_tick:
            continue

        effect = rule.effect
        if effect.type == "set":
            value = effect.value
        elif effect.type == "increment":
            value += effect.value
        elif effect.type == "ramp":
            ticks_active = tick - rule.active_from_tick + 1
            per_tick = effect.per_tick if effect.per_tick is not None else 0.0
            value = effect.value + per_tick * max(0, ticks_active - 1)

    return value


def carbon_tax_level(tick: int, schedule: PolicySchedule | None = None) -> float:
    """CO2 tax in EUR per tonne."""

    return max(0.0, _resolve_parameter(tick, "carbon_tax_level", schedule))


def fuel_price_change(tick: int, schedule: PolicySchedule | None = None) -> float:
    """Fuel price trend in percent per tick."""

    return _resolve_parameter(tick, "fuel_price_change", schedule)


def oil_price_index(
    tick: int,
    schedule: PolicySchedule | None = None,
    *,
    previous_index: float | None = None,
) -> float:
    """Oil price index; compounds by fuel_price_change each tick after tick 1."""

    if tick <= 1 or previous_index is None:
        return max(1.0, _baseline_value(schedule, "oil_price_index"))

    pct = fuel_price_change(tick, schedule)
    return max(1.0, previous_index * (1.0 + pct / 100.0))


def saf_mandate_share(tick: int, schedule: PolicySchedule | None = None) -> float:
    """Mandatory SAF share (0–1)."""

    value = _resolve_parameter(tick, "saf_mandate_share", schedule)
    return max(0.0, min(1.0, value))


def efuel_subsidy(tick: int, schedule: PolicySchedule | None = None) -> float:
    """E-fuel subsidy in EUR per litre (placeholder baseline)."""

    return max(0.0, _resolve_parameter(tick, "efuel_subsidy", schedule))


def demand_growth_rate(tick: int, schedule: PolicySchedule | None = None) -> float:
    """Demand growth rate in percent per tick."""

    return _resolve_parameter(tick, "demand_growth_rate", schedule)


def compute_market_metrics(
    tick: int,
    schedule: PolicySchedule | None = None,
    *,
    previous_metrics: dict[str, float] | None = None,
) -> dict[str, float]:
    """Compute all six deterministic market metrics for one tick."""

    prev = previous_metrics or {}
    prev_oil = prev.get("oil_price_index")

    return {
        "carbon_tax_level": carbon_tax_level(tick, schedule),
        "fuel_price_change": fuel_price_change(tick, schedule),
        "oil_price_index": oil_price_index(tick, schedule, previous_index=prev_oil),
        "saf_mandate_share": saf_mandate_share(tick, schedule),
        "efuel_subsidy": efuel_subsidy(tick, schedule),
        "demand_growth_rate": demand_growth_rate(tick, schedule),
    }


def derive_ticket_price(
    tick: int,
    schedule: PolicySchedule | None,
    *,
    previous_price: float,
    base_price: float = 100.0,
    previous_metrics: dict[str, float] | None = None,
) -> float:
    """Derive ticket price from per-tick fuel trend and carbon tax (deterministic)."""

    if tick <= 1 and previous_price <= 0:
        return base_price

    metrics = compute_market_metrics(tick, schedule, previous_metrics=previous_metrics)
    fuel_pct = metrics["fuel_price_change"]
    tax = metrics["carbon_tax_level"]
    saf = metrics["saf_mandate_share"]
    subsidy = metrics["efuel_subsidy"]

    # 1. CO2 tax pass-through
    tax_pass_through = tax / 10000.0

    # 2. SAF premium logic: SAF is more expensive. Subsidy dampens the premium.
    saf_premium = max(0.0, 1.0 - (subsidy * 0.1))
    saf_cost_increase = saf * saf_premium

    anchor = previous_price if previous_price > 0 else base_price
    return max(1.0, anchor * (1.0 + (fuel_pct / 100.0) + tax_pass_through + saf_cost_increase))


def derive_demand_level(
    tick: int,
    schedule: PolicySchedule | None,
    *,
    previous_level: float = 1.0,
) -> float:
    """Derive demand level from demand_growth_rate (deterministic compounding)."""

    if tick <= 1:
        return max(0.0, min(2.0, previous_level))

    growth_pct = demand_growth_rate(tick, schedule)
    level = previous_level * (1.0 + growth_pct / 100.0)
    return max(0.0, min(2.0, level))
