from __future__ import annotations

from uuid import uuid4

from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.models.enums import EventType
from src.models.state_models import SimulationState
from src.simulation_functions import compute_market_metrics, derive_demand_level, derive_ticket_price


class MarketNode:
    def __init__(self, base_price: float = 100.0) -> None:
        self.base_price = base_price

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_tick
        schedule = state.config.policy_schedule

        previous_metrics = dict(state.market_metrics)
        metrics = compute_market_metrics(
            round_number,
            schedule,
            previous_metrics=previous_metrics or None,
        )
        state.market_metrics = metrics

        last_price = state.price_history[-1].price if state.price_history else self.base_price
        last_demand = state.price_history[-1].demand_level if state.price_history else 1.0

        price = derive_ticket_price(
            round_number,
            schedule,
            previous_price=last_price,
            base_price=self.base_price,
            previous_metrics=previous_metrics or None,
        )
        demand_level = derive_demand_level(
            round_number,
            schedule,
            previous_level=last_demand,
        )

        state.price_history.append(
            PriceHistoryEntry(
                round_number=round_number,
                agent_id="market",
                price=price,
                demand_level=demand_level,
                load_factor=0.0,
            )
        )

        state.event_log.append(
            EventLogEntry(
                id=str(uuid4()),
                round_number=round_number,
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
