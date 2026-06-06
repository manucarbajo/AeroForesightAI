from __future__ import annotations

import pytest

from src.config_loader import build_initial_state, load_simulation_config
from src.models.state_models import PolicyEffect, PolicyRule, PolicySchedule
from src.nodes.market_node import MarketNode
from src.simulation_functions import (
    carbon_tax_level,
    compute_market_metrics,
    demand_growth_rate,
    derive_demand_level,
    derive_ticket_price,
    fuel_price_change,
)


def test_load_policy_schedule_from_config():
    config = load_simulation_config()
    assert config.policy_schedule is not None
    assert config.policy_schedule.baseline["carbon_tax_level"] == 0.0
    assert len(config.policy_schedule.rules) >= 1


def test_carbon_tax_delayed_until_tick_15():
    schedule = PolicySchedule(
        baseline={"carbon_tax_level": 0.0},
        rules=[
            PolicyRule(
                id="carbon_tax_delayed_activation",
                parameter="carbon_tax_level",
                active_from_tick=15,
                effect=PolicyEffect(type="set", value=50.0),
            )
        ],
    )

    assert carbon_tax_level(14, schedule) == 0.0
    assert carbon_tax_level(15, schedule) == 50.0
    assert carbon_tax_level(20, schedule) == 50.0


def test_compute_market_metrics_returns_all_metric_keys():
    schedule = load_simulation_config().policy_schedule
    metrics = compute_market_metrics(1, schedule)

    expected = {
        "carbon_tax_level",
        "fuel_price_change",
        "oil_price_index",
        "saf_mandate_share",
        "efuel_subsidy",
        "demand_growth_rate",
        "demand_level",
    }
    assert set(metrics.keys()) == expected


def test_derive_demand_level_compounds_with_percent_points():
    schedule = PolicySchedule(baseline={"demand_growth_rate": 3.0})
    level_1 = derive_demand_level(1, schedule, previous_level=1.0)
    level_2 = derive_demand_level(2, schedule, previous_level=level_1)

    assert level_1 == 1.0
    assert level_2 == pytest.approx(1.03)


def test_derive_ticket_price_increases_with_fuel_trend():
    schedule = PolicySchedule(baseline={"fuel_price_change": 2.0, "carbon_tax_level": 0.0})
    price_1 = derive_ticket_price(1, schedule, previous_price=0.0, base_price=100.0)
    price_2 = derive_ticket_price(2, schedule, previous_price=price_1)

    assert price_1 == 100.0
    assert price_2 > price_1


def _run_market_for_tick(state, tick: int):
    state.clock.current_tick = tick
    return MarketNode().invoke(state)


def test_market_node_fuel_shock_increases_price_at_tick_2():
    state = build_initial_state()
    state = _run_market_for_tick(state, 1)
    price_tick_1 = state.price_history[-1].price

    state = _run_market_for_tick(state, 2)
    price_tick_2 = state.price_history[-1].price

    assert fuel_price_change(2, state.config.policy_schedule) == 10.0
    assert price_tick_2 > price_tick_1 * 1.05


def test_market_node_carbon_tax_applies_from_tick_5():
    state = build_initial_state()
    for tick in range(1, 5):
        state = _run_market_for_tick(state, tick)

    assert carbon_tax_level(4, state.config.policy_schedule) == 0.0
    state = _run_market_for_tick(state, 5)
    assert state.market_metrics["carbon_tax_level"] == 85.0


def test_market_node_demand_shock_reduces_demand_level_at_tick_7():
    state = build_initial_state()
    for tick in range(1, 7):
        state = _run_market_for_tick(state, tick)

    demand_before_shock = state.market_metrics["demand_level"]
    assert demand_growth_rate(6, state.config.policy_schedule) == 3.0

    state = _run_market_for_tick(state, 7)
    assert demand_growth_rate(7, state.config.policy_schedule) == -4.0
    assert state.market_metrics["demand_level"] < demand_before_shock
    assert state.price_history[-1].demand_level == state.market_metrics["demand_level"]
