from __future__ import annotations

import pytest

from src.config_loader import load_properties_config
from src.market.property_engine import (
    property_value_changes_at_tick,
    resolve_property,
    resolve_system_properties,
    resolve_trajectory,
    scheduled_property_events,
)
from src.market.simulation_functions import compute_market_metrics
from src.models.property_models import (
    BaselineTrajectory,
    RampEffect,
    SetEffect,
    StepFunctionTrajectory,
    StepPoint,
    TrajectoryRule,
)


class TestResolveTrajectory:
    def test_baseline_without_rules(self):
        trajectory = BaselineTrajectory(baseline=0.03, rules=[])
        assert resolve_trajectory(trajectory, 10) == 0.03

    def test_set_rule_from_tick(self):
        trajectory = BaselineTrajectory(
            baseline=0.0,
            rules=[TrajectoryRule(active_from_tick=15, effect=SetEffect(value=120.0))],
        )
        assert resolve_trajectory(trajectory, 14) == 0.0
        assert resolve_trajectory(trajectory, 15) == 120.0

    def test_later_set_overrides_earlier(self):
        trajectory = BaselineTrajectory(
            baseline=50.0,
            rules=[
                TrajectoryRule(active_from_tick=1, effect=SetEffect(value=50.0)),
                TrajectoryRule(active_from_tick=15, effect=SetEffect(value=120.0)),
            ],
        )
        assert resolve_trajectory(trajectory, 10) == 50.0
        assert resolve_trajectory(trajectory, 20) == 120.0

    def test_step_function(self):
        trajectory = StepFunctionTrajectory(
            points=[
                StepPoint(tick=0, value=83_000_000),
                StepPoint(tick=4, value=90_000_000),
            ]
        )
        assert resolve_trajectory(trajectory, 0) == 83_000_000
        assert resolve_trajectory(trajectory, 3) == 83_000_000
        assert resolve_trajectory(trajectory, 4) == 90_000_000

    def test_ramp_interpolates(self):
        trajectory = BaselineTrajectory(
            baseline=0.0,
            rules=[
                TrajectoryRule(
                    active_from_tick=8,
                    effect=RampEffect(value=0.04, duration_ticks=4),
                )
            ],
        )
        assert resolve_trajectory(trajectory, 7) == 0.0
        assert resolve_trajectory(trajectory, 8) == pytest.approx(0.01)
        assert resolve_trajectory(trajectory, 10) == pytest.approx(0.03)
        assert resolve_trajectory(trajectory, 11) == 0.04


class TestPropertiesConfig:
    def test_load_properties_json(self):
        properties = load_properties_config()
        assert len(properties.system_properties) >= 8
        assert "carbon_tax_level" in properties.system_property_ids()

    def test_carbon_tax_delayed_until_tick_15(self):
        properties = load_properties_config()
        assert resolve_property("carbon_tax_level", 14, properties) == 50.0
        assert resolve_property("carbon_tax_level", 15, properties) == 120.0
        assert resolve_property("carbon_tax_level", 30, properties) == 200.0

    def test_compute_market_metrics_uses_properties(self):
        properties = load_properties_config()

        metrics_14 = compute_market_metrics(
            14,
            properties,
            previous_price=100.0,
            previous_demand=1.0,
            factors={},
            system_properties={},
        )
        metrics_15 = compute_market_metrics(
            15,
            properties,
            previous_price=100.0,
            previous_demand=1.0,
            factors={},
            system_properties={},
        )

        assert metrics_14["carbon_tax_level"] == 50.0
        assert metrics_15["carbon_tax_level"] == 120.0

    def test_resolve_system_properties_returns_all_ids(self):
        properties = load_properties_config()
        resolved = resolve_system_properties(1, properties)
        assert set(resolved.keys()) == set(properties.system_property_ids())

    def test_scheduled_property_events_includes_co2_and_saf(self):
        properties = load_properties_config()
        events = scheduled_property_events(properties)
        ticks = {
            int(event["tick"]) for event in events if event["property_id"] == "carbon_tax_level"
        }
        assert 15 in ticks
        saf_ticks = {
            int(event["tick"]) for event in events if event["property_id"] == "saf_mandate_share"
        }
        assert 8 in saf_ticks

    def test_property_value_changes_at_tick(self):
        timeseries = [
            {"tick": 7, "carbon_tax_level": 50.0, "saf_mandate_share": 0.0},
            {"tick": 8, "carbon_tax_level": 50.0, "saf_mandate_share": 0.02},
        ]
        changes = property_value_changes_at_tick(timeseries, 8)
        assert changes == [("saf_mandate_share", 0.0, 0.02)]
