"""Resolve system properties from trajectory config (M2).

All tick-based global values (carbon tax, SAF share, oil index, …) are
resolved here — never from LLM output.
"""

from __future__ import annotations

from src.models.property_models import (
    BaselineTrajectory,
    PropertiesConfig,
    RampEffect,
    SetEffect,
    StepFunctionTrajectory,
    SystemProperty,
    TrajectoryRule,
)

MARKET_PROPERTY_IDS = (
    "carbon_tax_level",
    "fuel_price_change",
    "oil_price_index",
    "saf_mandate_share",
    "efuel_subsidy",
    "demand_growth_rate",
)


def _clamp(value: float, prop: SystemProperty) -> float:
    if prop.min_value is not None:
        value = max(prop.min_value, value)
    if prop.max_value is not None:
        value = min(prop.max_value, value)
    return value


def _resolve_step_function(trajectory: StepFunctionTrajectory, tick: int) -> float:
    if not trajectory.points:
        return 0.0
    sorted_points = sorted(trajectory.points, key=lambda point: point.tick)
    value = sorted_points[0].value
    for point in sorted_points:
        if point.tick <= tick:
            value = point.value
        else:
            break
    return value


def _apply_set_rule(value: float, effect: SetEffect) -> float:
    return effect.value


def _resolve_with_rules(
    baseline: float,
    rules: list[TrajectoryRule],
    tick: int,
) -> float:
    sorted_rules = sorted(rules, key=lambda rule: rule.active_from_tick)
    value = baseline

    for index, rule in enumerate(sorted_rules):
        if rule.active_from_tick > tick:
            continue
        if isinstance(rule.effect, SetEffect):
            value = _apply_set_rule(value, rule.effect)
            continue

        effect = rule.effect
        duration = max(1, effect.duration_ticks)
        if tick >= rule.active_from_tick + duration:
            value = effect.value
            continue

        prior_rules = sorted_rules[:index]
        start_value = _resolve_with_rules(baseline, prior_rules, rule.active_from_tick - 1)
        progress = (tick - rule.active_from_tick + 1) / duration
        value = start_value + (effect.value - start_value) * progress

    return value


def _resolve_baseline_trajectory(trajectory: BaselineTrajectory, tick: int) -> float:
    return _resolve_with_rules(trajectory.baseline, trajectory.rules, tick)


def resolve_trajectory(
    trajectory: BaselineTrajectory | StepFunctionTrajectory,
    tick: int,
) -> float:
    if isinstance(trajectory, StepFunctionTrajectory):
        return _resolve_step_function(trajectory, tick)
    return _resolve_baseline_trajectory(trajectory, tick)


def resolve_property(
    prop_id: str,
    tick: int,
    properties: PropertiesConfig,
) -> float:
    prop = properties.get_system_property(prop_id)
    if prop is None:
        raise KeyError(f"Unknown system property: {prop_id}")
    value = resolve_trajectory(prop.trajectory, tick)
    return _clamp(value, prop)


def is_exogenous_property(prop: SystemProperty) -> bool:
    """Trajectory-driven inputs; runtime/computed props are updated by the simulation loop."""

    return prop.source == "trajectory"


def resolve_exogenous_system_properties(
    tick: int,
    properties: PropertiesConfig,
) -> dict[str, float]:
    """Resolve trajectory-driven system properties for one tick (M4.13)."""

    return {
        prop.id: resolve_property(prop.id, tick, properties)
        for prop in properties.system_properties
        if is_exogenous_property(prop)
    }


def resolve_system_properties(
    tick: int,
    properties: PropertiesConfig,
) -> dict[str, float]:
    """Resolve all system properties for one tick (runtime/computed use trajectory baseline)."""

    return {
        prop.id: resolve_property(prop.id, tick, properties)
        for prop in properties.system_properties
    }


def scheduled_property_events(properties: PropertiesConfig) -> list[dict[str, object]]:
    """List tick-scheduled system property changes from trajectory config."""

    events: list[dict[str, object]] = []

    for prop in properties.system_properties:
        trajectory = prop.trajectory
        if isinstance(trajectory, BaselineTrajectory):
            for rule in trajectory.rules:
                effect = rule.effect
                if isinstance(effect, SetEffect):
                    events.append(
                        {
                            "tick": rule.active_from_tick,
                            "property_id": prop.id,
                            "effect_type": "set",
                            "value": effect.value,
                            "unit": prop.unit,
                            "description": prop.description,
                        }
                    )
                elif isinstance(effect, RampEffect):
                    events.append(
                        {
                            "tick": rule.active_from_tick,
                            "property_id": prop.id,
                            "effect_type": "ramp",
                            "value": effect.value,
                            "duration_ticks": effect.duration_ticks,
                            "unit": prop.unit,
                            "description": prop.description,
                        }
                    )
            continue

        for point in trajectory.points:
            events.append(
                {
                    "tick": point.tick,
                    "property_id": prop.id,
                    "effect_type": "step_function",
                    "value": point.value,
                    "unit": prop.unit,
                    "description": prop.description,
                }
            )

    return sorted(events, key=lambda entry: (int(entry["tick"]), str(entry["property_id"])))


def property_value_changes_at_tick(
    timeseries: list[dict[str, object]],
    tick: int,
) -> list[tuple[str, float, float]]:
    """Return (property_id, old_value, new_value) for changes at ``tick``."""

    current = next((row for row in timeseries if row.get("tick") == tick), None)
    if current is None:
        return []

    previous = next((row for row in timeseries if row.get("tick") == tick - 1), None)
    changes: list[tuple[str, float, float]] = []

    for key, new_value in current.items():
        if key == "tick":
            continue
        new_float = float(new_value)
        old_float = float(previous.get(key, new_float)) if previous else new_float
        if previous is None or old_float != new_float:
            if previous is not None:
                changes.append((str(key), old_float, new_float))

    return changes
