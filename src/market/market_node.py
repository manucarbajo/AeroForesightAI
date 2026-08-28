from __future__ import annotations

from uuid import uuid4

from src.market.market_feedback import initial_provider_markup
from src.market.simulation_functions import compute_market_metrics
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.models.state_models import SimulationState


class MarketNode:
    def __init__(self, base_price: float = 100.0) -> None:
        self.base_price = base_price

    def invoke(self, state: SimulationState) -> SimulationState:
        tick = state.clock.current_tick
        properties = state.resolved_properties()
        price_model = properties.price_model

        last_price = (
            state.price_history[-1].price if state.price_history else price_model.base_price
        )
        last_demand = state.price_history[-1].demand_level if state.price_history else 1.0
        previous_markup = state.market_metrics.get(
            "provider_markup",
            state.market_metrics.get("markup", initial_provider_markup(properties, tick=tick)),
        )
        previous_cost_index = state.market_metrics.get("cost_index", 1.0)

        booking_rate = (
            state.market_metrics.get("booking_rate")
            if state.market_metrics.get("booking_evaluated")
            else None
        )

        from src.market.property_engine import (
            resolve_exogenous_system_properties,
            resolve_system_properties,
        )

        system_properties = resolve_system_properties(tick, properties)
        exogenous = resolve_exogenous_system_properties(tick, properties)
        factors = state.environment.factors

        pre_feedback_price = state.market_metrics.get("ticket_price_pre_feedback")
        if pre_feedback_price is None:
            pre_feedback_price = state.market_metrics.get("ticket_price")

        metrics = compute_market_metrics(
            tick,
            properties,
            previous_price=last_price,
            base_price=price_model.base_price,
            previous_demand=last_demand,
            previous_markup=previous_markup,
            previous_cost_index=previous_cost_index,
            booking_rate=booking_rate,
            factors=factors,
            system_properties=system_properties,
        )
        state.market_metrics = metrics

        property_row: dict[str, float | int] = {
            "tick": tick,
            "ticket_price": metrics["ticket_price"],
        }
        if pre_feedback_price is not None:
            property_row["ticket_price_pre_feedback"] = float(pre_feedback_price)
        for prop_id in (
            "carbon_tax_level",
            "fuel_price_change",
            "oil_price_index",
            "saf_mandate_share",
            "efuel_subsidy",
            "demand_growth_rate",
            "income_index",
            "bevoelkerungsentwicklung",
            "maintenance_cost_index",
            "staff_cost_index",
            "cost_pressure",
            "cost_index",
            "provider_markup",
            "markup",
        ):
            if prop_id in metrics:
                property_row[prop_id] = metrics[prop_id]
            elif prop_id in exogenous:
                property_row[prop_id] = exogenous[prop_id]
        booking_rate = metrics.get("booking_rate")
        if booking_rate is not None:
            property_row["booking_rate"] = booking_rate
        state.property_timeseries.append(property_row)

        price = metrics["ticket_price"]
        demand_level = metrics["demand_level"]

        state.price_history.append(
            PriceHistoryEntry(
                round_number=tick,
                agent_id="market",
                price=price,
                demand_level=demand_level,
                load_factor=0.0,
                booking_rate=booking_rate,
            )
        )

        prev_price = last_price
        price_delta_pct = ((price - prev_price) / prev_price * 100.0) if prev_price > 0 else 0.0
        booking_note = ""
        if booking_rate is not None:
            booking_note = f", booking_rate={booking_rate:.1%}, feedback applied"

        state.event_log.append(
            EventLogEntry(
                id=str(uuid4()),
                round_number=tick,
                source_agent="market",
                event_type=EventType.MARKET_EVENT,
                description=(
                    f"Market update (M4): price={price:.2f} ({price_delta_pct:+.1f}%), "
                    f"cost={metrics.get('cost_pressure', 0):.2f}, markup={metrics.get('markup', 0):.2f}, "
                    f"demand_level={demand_level:.2f}{booking_note}"
                ),
                affected_factors=[],
                timestamp="",
            )
        )

        price_delta_abs = abs(price - prev_price)
        if prev_price > 0 and (price_delta_abs >= 0.5 or abs(price_delta_pct) >= 0.5):
            markup = metrics.get("markup", metrics.get("provider_markup", 0.0))
            booking_part = f"{float(booking_rate):.1%}" if booking_rate is not None else "n/a"
            state.event_log.append(
                EventLogEntry(
                    id=str(uuid4()),
                    round_number=tick,
                    source_agent="provider",
                    event_type=EventType.PRICE_CHANGE,
                    description=(
                        f"[delta:price] Provider yield feedback: ticket price "
                        f"{prev_price:.2f} → {price:.2f} ({price_delta_pct:+.1f}%), "
                        f"markup={float(markup):.2f}, booking_rate={booking_part} "
                        f"(Python, market_rules aus properties.json)"
                    ),
                    affected_factors=[],
                    timestamp="",
                )
            )

        return state
