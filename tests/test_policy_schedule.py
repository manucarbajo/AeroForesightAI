from __future__ import annotations

import pytest

from src.config_loader import build_initial_state, load_simulation_config
from src.models.state_models import PolicyEntry
from src.nodes.market_node import MarketNode
from src.simulation_functions import (
    compute_demand,
    compute_market_metrics,
    compute_ticket_price,
    resolve_policy,
)


class TestResolvePolicy:
    def test_empty_schedule(self):
        assert resolve_policy(5, []) == {}

    def test_entry_before_tick_not_applied(self):
        schedule = [PolicyEntry(tick=10, parameter="carbon_tax_level", value=100.0)]
        assert resolve_policy(5, schedule) == {}

    def test_entry_at_tick_applied(self):
        schedule = [PolicyEntry(tick=5, parameter="carbon_tax_level", value=100.0)]
        assert resolve_policy(5, schedule) == {"carbon_tax_level": 100.0}

    def test_later_entry_overrides_earlier(self):
        schedule = [
            PolicyEntry(tick=1, parameter="carbon_tax_level", value=50.0),
            PolicyEntry(tick=8, parameter="carbon_tax_level", value=75.0),
        ]
        result = resolve_policy(10, schedule)
        assert result["carbon_tax_level"] == 75.0

    def test_multiple_parameters(self):
        schedule = [
            PolicyEntry(tick=1, parameter="carbon_tax_level", value=50.0),
            PolicyEntry(tick=1, parameter="saf_mandate_share", value=0.02),
        ]
        result = resolve_policy(1, schedule)
        assert result == {"carbon_tax_level": 50.0, "saf_mandate_share": 0.02}

    def test_tick_zero_applies_nothing(self):
        schedule = [PolicyEntry(tick=1, parameter="carbon_tax_level", value=50.0)]
        assert resolve_policy(0, schedule) == {}


class TestComputeTicketPrice:
    def test_base_case_no_effects(self):
        price = compute_ticket_price(
            base_price=100.0,
            carbon_tax=0.0,
            fuel_price_change=0.0,
            oil_index=1.0,
            saf_share=0.0,
            efuel_subsidy=0.0,
        )
        assert price == 100.0

    def test_carbon_tax_increases_price(self):
        price = compute_ticket_price(
            base_price=100.0,
            carbon_tax=100.0,
            fuel_price_change=0.0,
            oil_index=1.0,
            saf_share=0.0,
            efuel_subsidy=0.0,
        )
        assert price > 100.0

    def test_minimum_price_floor(self):
        price = compute_ticket_price(
            base_price=1.0,
            carbon_tax=0.0,
            fuel_price_change=-0.99,
            oil_index=0.01,
            saf_share=0.0,
            efuel_subsidy=0.0,
        )
        assert price >= 1.0

    def test_subsidy_reduces_price(self):
        price_no_subsidy = compute_ticket_price(
            base_price=100.0,
            carbon_tax=0.0,
            fuel_price_change=0.0,
            oil_index=1.0,
            saf_share=0.1,
            efuel_subsidy=0.0,
        )
        price_with_subsidy = compute_ticket_price(
            base_price=100.0,
            carbon_tax=0.0,
            fuel_price_change=0.0,
            oil_index=1.0,
            saf_share=0.1,
            efuel_subsidy=1.0,
        )
        assert price_with_subsidy < price_no_subsidy


class TestComputeDemand:
    def test_base_case_no_effects(self):
        demand = compute_demand(
            base_demand=1.0,
            growth_rate=0.0,
            price_elasticity=0.5,
            price_delta=0.0,
        )
        assert demand == 1.0

    def test_growth_increases_demand(self):
        demand = compute_demand(
            base_demand=1.0,
            growth_rate=0.03,
            price_elasticity=0.0,
            price_delta=0.0,
        )
        assert demand > 1.0

    def test_price_increase_decreases_demand(self):
        demand = compute_demand(
            base_demand=1.0,
            growth_rate=0.0,
            price_elasticity=0.5,
            price_delta=0.1,
        )
        assert demand < 1.0

    def test_demand_clamped_at_zero(self):
        demand = compute_demand(
            base_demand=1.0,
            growth_rate=0.0,
            price_elasticity=0.5,
            price_delta=5.0,
        )
        assert demand == 0.0

    def test_demand_clamped_at_two(self):
        demand = compute_demand(
            base_demand=2.0,
            growth_rate=1.0,
            price_elasticity=0.0,
            price_delta=0.0,
        )
        assert demand == 2.0


def test_load_policy_schedule_from_config():
    config = load_simulation_config()
    assert len(config.policy_schedule) >= 1
    assert config.policy_schedule[0].parameter == "carbon_tax_level"
    assert len(config.scenario_parameters) == 6


def test_carbon_tax_delayed_until_tick_15():
    schedule = [PolicyEntry(tick=15, parameter="carbon_tax_level", value=120.0)]
    runtime = {"carbon_tax_level": 0.0}

    metrics_14 = compute_market_metrics(
        14,
        schedule,
        runtime,
        previous_price=100.0,
        previous_demand=1.0,
    )
    metrics_15 = compute_market_metrics(
        15,
        schedule,
        runtime,
        previous_price=100.0,
        previous_demand=1.0,
    )

    assert metrics_14["carbon_tax_level"] == 0.0
    assert metrics_15["carbon_tax_level"] == 120.0


def test_compute_market_metrics_returns_all_metric_keys():
    config = load_simulation_config()
    metrics = compute_market_metrics(
        1,
        config.policy_schedule,
        config.runtime_parameter_map(),
        previous_price=100.0,
        previous_demand=1.0,
    )

    expected = {
        "carbon_tax_level",
        "fuel_price_change",
        "oil_price_index",
        "saf_mandate_share",
        "efuel_subsidy",
        "demand_growth_rate",
        "demand_level",
        "ticket_price",
    }
    assert set(metrics.keys()) == expected


def _run_market_for_tick(state, tick: int):
    state.clock.current_tick = tick
    return MarketNode().invoke(state)


def test_market_node_applies_carbon_tax_from_tick_1():
    state = build_initial_state()
    state = _run_market_for_tick(state, 1)
    assert state.market_metrics["carbon_tax_level"] == 50.0
    assert state.price_history[-1].price > 100.0


def test_market_node_carbon_tax_jumps_at_tick_15():
    state = build_initial_state()
    for tick in range(1, 15):
        state = _run_market_for_tick(state, tick)

    assert state.market_metrics["carbon_tax_level"] == 50.0
    state = _run_market_for_tick(state, 15)
    assert state.market_metrics["carbon_tax_level"] == 120.0
    assert state.price_history[-1].price > state.price_history[-2].price


def test_market_node_saf_mandate_from_tick_8():
    state = build_initial_state()
    for tick in range(1, 8):
        state = _run_market_for_tick(state, tick)

    assert state.market_metrics["saf_mandate_share"] == 0.0
    state = _run_market_for_tick(state, 8)
    assert state.market_metrics["saf_mandate_share"] == 0.02
