from __future__ import annotations

from src.config_loader import build_initial_state, load_properties_config
from src.market_rules import initial_provider_markup, resolve_market_feedback_config
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.property_engine import resolve_exogenous_system_properties
from src.simulation_functions import (
    apply_market_feedback,
    clip_price_change,
    compute_cost_pressure,
    compute_ticket_price,
    sync_demand_level,
    update_cost_index,
)


def _count_direction_changes(values: list[float]) -> int:
    if len(values) < 3:
        return 0
    changes = 0
    for i in range(2, len(values)):
        prev_delta = values[i - 1] - values[i - 2]
        curr_delta = values[i] - values[i - 1]
        if prev_delta * curr_delta < 0:
            changes += 1
    return changes


def _run_m4_tick(state, tick: int):
    state.clock.current_tick = tick
    state = EnvironmentNode().invoke(state)
    return MarketNode().invoke(state)


class TestComputeCostPressure:
    def test_compound_fuel_raises_cost_over_ticks(self):
        properties = load_properties_config()
        index = 1.0
        costs: list[float] = []
        for tick in range(1, 11):
            index = update_cost_index(index, 0.02)
            costs.append(compute_cost_pressure(tick, properties, cost_index=index))
        assert costs[-1] > costs[0]

    def test_carbon_tax_increases_cost(self):
        properties = load_properties_config()
        low = compute_cost_pressure(1, properties)
        high = compute_cost_pressure(15, properties)
        assert high > low


class TestM413ConfigurablePrice:
    def test_coefficients_drive_cost_formula(self):
        properties = load_properties_config()
        low = compute_ticket_price(100.0, carbon_tax=50.0, fuel_price_change=0.0, oil_index=1.0, saf_share=0.0, efuel_subsidy=0.0)
        high = compute_ticket_price(
            100.0,
            carbon_tax=50.0,
            fuel_price_change=0.0,
            oil_index=1.0,
            saf_share=0.0,
            efuel_subsidy=0.0,
            coefficients=properties.price_model.coefficients.model_copy(update={"carbon_per_tonne": 0.01}),
        )
        assert high > low

    def test_market_rules_resolve_to_feedback_config(self):
        properties = load_properties_config()
        config = resolve_market_feedback_config(properties)
        assert config.enabled is True
        assert config.target_booking_rate == 0.37

    def test_runtime_properties_excluded_from_exogenous_resolve(self):
        properties = load_properties_config()
        resolved = resolve_exogenous_system_properties(1, properties)
        assert "provider_markup" not in resolved
        assert "ticket_price" not in resolved
        assert "carbon_tax_level" in resolved

    def test_initial_provider_markup_from_system_property(self):
        properties = load_properties_config()
        assert initial_provider_markup(properties) == 28.0

    def test_market_rules_resolve_marginal_cost_fraction(self):
        properties = load_properties_config()
        config = resolve_market_feedback_config(properties)
        assert config.marginal_cost_fraction == 0.33


class TestApplyMarketFeedback:
    def test_low_booking_reduces_price(self):
        properties = load_properties_config()
        config = resolve_market_feedback_config(properties)
        coeffs = properties.price_model.coefficients
        cost = 110.0
        price_high, _ = apply_market_feedback(cost, 0.9, 10.0, 120.0, config, coefficients=coeffs)
        price_low, _ = apply_market_feedback(cost, 0.3, 10.0, 120.0, config, coefficients=coeffs)
        assert price_low < price_high

    def test_clipping_limits_large_drop(self):
        clipped = clip_price_change(50.0, 100.0, 0.05)
        assert clipped == 95.0


class TestSyncDemandLevel:
    def test_higher_booking_raises_demand(self):
        low = sync_demand_level(0.3, 1.0, 0.03, booking_weight=0.6)
        high = sync_demand_level(0.9, 1.0, 0.03, booking_weight=0.6)
        assert high > low


class TestM4Pipeline:
    def test_price_can_fall_with_feedback(self):
        state = build_initial_state()
        prices: list[float] = []
        for tick in range(1, 16):
            state = _run_m4_tick(state, tick)
            prices.append(state.price_history[-1].price)

        assert any(prices[i] > prices[i + 1] for i in range(len(prices) - 1))

    def test_demand_tracks_booking_when_feedback_on(self):
        state = build_initial_state()
        for tick in range(1, 6):
            state = _run_m4_tick(state, tick)

        booking = state.market_metrics.get("booking_rate")
        demand = state.market_metrics.get("demand_level")
        assert booking is not None
        assert demand is not None
        if booking < 0.5:
            assert demand < 1.2
        if booking > 0.8:
            assert demand > 0.8

    def test_markup_stored_in_metrics(self):
        state = build_initial_state()
        state = _run_m4_tick(state, 1)
        assert "provider_markup" in state.market_metrics
        assert "markup" in state.market_metrics
        assert "cost_pressure" in state.market_metrics
        assert state.property_timeseries[-1]["provider_markup"] == state.market_metrics["provider_markup"]
        assert state.property_timeseries[-1]["ticket_price"] == state.market_metrics["ticket_price"]

    def test_tick_one_has_booking_rate(self):
        state = build_initial_state()
        state = _run_m4_tick(state, 1)
        assert state.price_history[-1].booking_rate is not None

    def test_m4_emergence_over_30_ticks(self):
        """M4 Abnahme: sichtbare Rückkopplung, nicht Thermostat-Drift."""
        state = build_initial_state()
        prices: list[float] = []
        bookings: list[float] = []
        margins: list[float] = []
        for tick in range(1, 31):
            state = _run_m4_tick(state, tick)
            prices.append(state.price_history[-1].price)
            bookings.append(state.market_metrics["booking_rate"])
            margins.append(
                state.market_metrics["ticket_price"] - state.market_metrics["cost_pressure"]
            )

        price_mean = sum(prices) / len(prices)
        price_range_pct = (max(prices) - min(prices)) / price_mean * 100.0
        booking_range = max(bookings) - min(bookings)
        margin_range = max(margins) - min(margins)
        direction_changes = _count_direction_changes(prices)

        assert price_range_pct >= 5.0, f"price range {price_range_pct:.1f}% too narrow"
        assert direction_changes >= 1, f"only {direction_changes} direction changes"
        assert booking_range >= 0.10, f"booking range {booking_range:.3f} too flat"
        assert margin_range >= 4.0, f"margin range {margin_range:.1f} too flat"
        assert any(prices[i] > prices[i + 1] for i in range(len(prices) - 1))
        assert any(prices[i] < prices[i + 1] for i in range(len(prices) - 1))


# ---------------------------------------------------------------------------
# P2.5 — Emergenz ohne exogene CO₂-Schocks
# ---------------------------------------------------------------------------

class TestEmergenceWithoutCO2Shock:
    def test_price_reversal_from_yield_feedback_only(self):
        """P2.5: Price direction change must occur from internal coupling alone (no CO₂ shock)."""
        from src.models.property_models import BaselineTrajectory
        from src.property_engine import resolve_trajectory

        state = build_initial_state()

        flat_ids = (
            "carbon_tax_level",
            "saf_mandate_share",
            "oil_price_index",
            "demand_growth_rate",
            "fuel_price_change",
            "income_index",
        )
        for prop in state.properties.system_properties:
            if prop.id in flat_ids:
                current_val = resolve_trajectory(prop.trajectory, tick=1)
                prop.trajectory = BaselineTrajectory(baseline=current_val, rules=[])

        prices: list[float] = []
        bookings: list[float] = []
        for tick in range(1, 31):
            state = _run_m4_tick(state, tick)
            prices.append(state.price_history[-1].price)
            bookings.append(state.market_metrics.get("booking_rate", 0.0))

        direction_changes = _count_direction_changes(prices)
        price_range = max(prices) - min(prices)
        booking_range = max(bookings) - min(bookings)

        assert direction_changes >= 1, (
            f"No price reversals in 30 ticks without CO₂ shock — "
            f"Yield-Feedback emergence not working. Prices: {[round(p,1) for p in prices]}"
        )
        assert price_range >= 3.0, f"Price range too flat: {price_range:.2f}€"
        assert booking_range >= 0.05, f"Booking range too flat: {booking_range:.3f}"
