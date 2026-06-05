from __future__ import annotations

from src.config_loader import load_simulation_config
from src.models.state_models import PolicyEffect, PolicyRule, PolicySchedule
from src.simulation_functions import (
    carbon_tax_level,
    compute_market_metrics,
    demand_growth_rate,
    derive_demand_level,
    derive_ticket_price,
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


def test_compute_market_metrics_returns_all_six_keys():
    schedule = load_simulation_config().policy_schedule
    metrics = compute_market_metrics(1, schedule)

    expected = {
        "carbon_tax_level",
        "fuel_price_change",
        "oil_price_index",
        "saf_mandate_share",
        "efuel_subsidy",
        "demand_growth_rate",
    }
    assert set(metrics.keys()) == expected


def test_derive_demand_level_compounds():
    schedule = PolicySchedule(baseline={"demand_growth_rate": 0.03})
    level_1 = derive_demand_level(1, schedule, previous_level=1.0)
    level_2 = derive_demand_level(2, schedule, previous_level=level_1)

    assert level_1 == 1.0
    assert level_2 > level_1


def test_derive_ticket_price_increases_with_fuel_trend():
    schedule = PolicySchedule(baseline={"fuel_price_change": 2.0, "carbon_tax_level": 0.0})
    price_1 = derive_ticket_price(1, schedule, previous_price=0.0, base_price=100.0)
    price_2 = derive_ticket_price(2, schedule, previous_price=price_1)

    assert price_1 == 100.0
    assert price_2 > price_1
