"""Derive deterministic event_log entries from tick-to-tick state deltas (M9)."""

from __future__ import annotations

from uuid import uuid4

from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.models.state_models import SimulationState

_DELTA_SOURCE = "system"

_TRACKED_PROPERTIES: tuple[str, ...] = (
    "carbon_tax_level",
    "income_index",
    "saf_mandate_share",
    "fuel_price_change",
    "oil_price_index",
    "efuel_subsidy",
    "bevoelkerungsentwicklung",
    "maintenance_cost_index",
    "staff_cost_index",
    "provider_markup",
    "cost_pressure",
    "booking_rate",
)

_PROPERTY_LABELS: dict[str, str] = {
    "carbon_tax_level": "CO₂ tax",
    "income_index": "income index",
    "saf_mandate_share": "SAF mandate",
    "fuel_price_change": "fuel price change",
    "oil_price_index": "oil price index",
    "efuel_subsidy": "e-fuel subsidy",
    "bevoelkerungsentwicklung": "population trajectory",
    "maintenance_cost_index": "maintenance cost index",
    "staff_cost_index": "staff cost index",
    "provider_markup": "provider markup",
    "cost_pressure": "cost pressure",
    "booking_rate": "booking rate",
}


def _row_for_tick(rows: list[dict[str, object]], tick: int) -> dict[str, object] | None:
    for row in rows:
        if row.get("tick") == tick:
            return row
    return None


def _has_delta_event(state: SimulationState, tick: int, marker: str) -> bool:
    prefix = f"[delta:{marker}]"
    for event in state.event_log:
        if event.round_number != tick or event.source_agent != _DELTA_SOURCE:
            continue
        if event.description.startswith(prefix):
            return True
    return False


def _append_delta_event(
    state: SimulationState,
    *,
    tick: int,
    marker: str,
    event_type: EventType,
    description: str,
    affected_factors: list[str] | None = None,
) -> None:
    if _has_delta_event(state, tick, marker):
        return
    state.event_log.append(
        EventLogEntry(
            id=str(uuid4()),
            round_number=tick,
            source_agent=_DELTA_SOURCE,
            event_type=event_type,
            description=f"[delta:{marker}] {description}",
            affected_factors=affected_factors or [],
            timestamp="",
        )
    )


def _format_numeric_delta(label: str, previous: float, current: float) -> str:
    delta = current - previous
    if label == "booking rate":
        return f"{label} {previous:.1%} → {current:.1%} " f"({delta * 100:+.1f} pp, Python delta)"
    if label == "SAF mandate":
        return (
            f"{label} {previous:.1%} → {current:.1%} "
            f"({(current - previous) * 100:+.1f} pp, Python delta)"
        )
    return f"{label} {previous:g} → {current:g} ({delta:+.4g}, Python delta)"


def write_events_from_deltas(state: SimulationState) -> SimulationState:
    """Append system events derived from factor/property/booking deltas for the current tick."""

    tick = state.clock.current_tick
    if tick < 1:
        return state

    prior_tick = tick - 1

    prior_factors = _row_for_tick(state.factor_timeseries, prior_tick)
    current_factors = _row_for_tick(state.factor_timeseries, tick)
    if prior_factors and current_factors:
        for key in sorted(current_factors.keys()):
            if key == "tick":
                continue
            previous = prior_factors.get(key)
            current = current_factors.get(key)
            if previous is None or current is None or previous == current:
                continue
            factor_id = str(key)
            _append_delta_event(
                state,
                tick=tick,
                marker=f"factor:{factor_id}",
                event_type=EventType.POLICY_CHANGE,
                description=(
                    f"Factor {factor_id} state {previous} → {current} "
                    f"(factor_rules, Python delta)"
                ),
                affected_factors=[factor_id],
            )

    prior_props = _row_for_tick(state.property_timeseries, prior_tick)
    current_props = _row_for_tick(state.property_timeseries, tick)
    if prior_props and current_props:
        for prop_id in _TRACKED_PROPERTIES:
            previous = prior_props.get(prop_id)
            current = current_props.get(prop_id)
            if previous is None or current is None:
                continue
            if not isinstance(previous, (int, float)) or not isinstance(current, (int, float)):
                continue
            if float(previous) == float(current):
                continue
            label = _PROPERTY_LABELS.get(prop_id, prop_id)
            _append_delta_event(
                state,
                tick=tick,
                marker=f"property:{prop_id}",
                event_type=EventType.MARKET_EVENT,
                description=_format_numeric_delta(label, float(previous), float(current)),
            )

    prior_stats = next(
        (row for row in state.population_stats if row.get("round_number") == prior_tick),
        None,
    )
    current_stats = next(
        (row for row in state.population_stats if row.get("round_number") == tick),
        None,
    )
    if prior_stats and current_stats:
        prior_booking = prior_stats.get("total_demand")
        current_booking = current_stats.get("total_demand")
        if (
            isinstance(prior_booking, (int, float))
            and isinstance(current_booking, (int, float))
            and float(prior_booking) != float(current_booking)
        ):
            _append_delta_event(
                state,
                tick=tick,
                marker="booking:population",
                event_type=EventType.DEMAND_SHIFT,
                description=_format_numeric_delta(
                    "booking rate",
                    float(prior_booking),
                    float(current_booking),
                ),
            )

    return state
