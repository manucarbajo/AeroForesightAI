from __future__ import annotations

from uuid import uuid4

from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.models.state_models import SimulationState
from src.simulation_functions import compute_market_metrics


class MarketNode:
    def __init__(self, base_price: float = 100.0) -> None:
        self.base_price = base_price

    def invoke(self, state: SimulationState) -> SimulationState:
        tick = state.clock.current_tick
        last_price = state.price_history[-1].price if state.price_history else self.base_price
        last_demand = state.price_history[-1].demand_level if state.price_history else 1.0

        metrics = compute_market_metrics(
            tick,
            state.config.policy_schedule,
            state.config.runtime_parameter_map(),
            previous_price=last_price,
            base_price=self.base_price,
            previous_demand=last_demand,
        )
        state.market_metrics = metrics

        price = metrics["ticket_price"]
        demand_level = metrics["demand_level"]

        state.price_history.append(
            PriceHistoryEntry(
                round_number=tick,
                agent_id="market",
                price=price,
                demand_level=demand_level,
                load_factor=0.0,
            )
        )

        state.event_log.append(
            EventLogEntry(
                id=str(uuid4()),
                round_number=tick,
                source_agent="market",
                event_type=EventType.MARKET_EVENT,
                description=(
                    f"Market update (deterministic): price={price:.2f}, "
                    f"demand_level={demand_level:.2f}, "
                    f"oil_index={metrics['oil_price_index']:.2f}, "
                    f"carbon_tax={metrics['carbon_tax_level']:.2f}"
                ),
                affected_factors=[],
                timestamp="",
            )
        )

        return state
