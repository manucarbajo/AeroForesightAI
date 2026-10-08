"""Derive deterministic event_log entries from tick-to-tick state deltas (M9)."""

from __future__ import annotations

from uuid import uuid4

from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.models.state_models import SimulationState
from src.reporting.namen import (
    FAKTOR_KURZNAMEN,
    groesse_name,
    prozent,
    prozentpunkte,
    zahl,
)

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

#: Die Namen der Größen, die keine Systemgröße mit Eintrag in `PROPERTY_LABELS`
#: sind. Alle übrigen kommen aus `src.reporting.namen` — bis zum 2026-10-02 stand
#: hier eine zweite, englische Tabelle («CO₂ tax», «population trajectory»).
_EIGENE_NAMEN: dict[str, str] = {
    "cost_pressure": "Kostendruck",
    "booking_rate": "Buchungsrate",
}

#: Größen, die ein Anteil sind und als Prozent geschrieben werden.
_ANTEILE = ("saf_mandate_share", "booking_rate")


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


def _name(prop_id: str) -> str:
    return _EIGENE_NAMEN.get(prop_id) or groesse_name(prop_id)


def _format_numeric_delta(prop_id: str, previous: float, current: float) -> str:
    """Eine Veränderung als deutscher Satzteil (2026-10-02).

    Bis dahin «booking rate 23.3% → 12.0% (-11.4 pp, Python delta)» — sichtbar in der
    Konsole, unter «Dateien» und im Kontext der Abfrage.
    """

    delta = current - previous
    vorzeichen = "+" if delta >= 0 else "−"
    if prop_id in _ANTEILE:
        return (
            f"{_name(prop_id)} {prozent(previous)} → {prozent(current)} "
            f"({prozentpunkte(delta)}, gerechnet)"
        )
    return (
        f"{_name(prop_id)} {zahl(round(previous, 2))} → {zahl(round(current, 2))} "
        f"({vorzeichen}{zahl(round(abs(delta), 2))}, gerechnet)"
    )


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
                    f"Faktor {FAKTOR_KURZNAMEN.get(factor_id, factor_id)} ({factor_id}): "
                    f"{previous} → {current} (Faktorregeln, gerechnet)"
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
            _append_delta_event(
                state,
                tick=tick,
                marker=f"property:{prop_id}",
                event_type=EventType.MARKET_EVENT,
                description=_format_numeric_delta(prop_id, float(previous), float(current)),
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
                    "booking_rate",
                    float(prior_booking),
                    float(current_booking),
                ),
            )

    return state
