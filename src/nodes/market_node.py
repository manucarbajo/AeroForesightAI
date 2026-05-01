from __future__ import annotations

import re
from uuid import uuid4

from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.models.enums import EventType
from src.models.state_models import SimulationState


class MarketNode:
    def __init__(self, base_price: float = 100.0) -> None:
        self.base_price = base_price

    def invoke(self, state: SimulationState) -> SimulationState:
        round_number = state.clock.current_round

        recent_events = [e for e in state.event_log if e.round_number == round_number]
        price = self._derive_price(state, recent_events)
        demand_level = self._derive_demand_level(state, recent_events)

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
                description=f"Market update: price={price:.2f}, demand_level={demand_level:.2f}",
                affected_factors=[],
                timestamp="",
            )
        )

        return state

    def _derive_price(self, state: SimulationState, events: list[EventLogEntry]) -> float:
        last_price = state.price_history[-1].price if state.price_history else self.base_price

        # MVP-Heuristik: suche pro Runde nach einer Prozentangabe in Provider-PRICE_CHANGE-Events.
        pct = 0.0
        for e in events:
            if e.source_agent != "provider":
                continue
            if e.event_type != EventType.PRICE_CHANGE:
                continue
            pct = self._extract_percent(e.description) or pct

        return max(1.0, last_price * (1.0 + pct / 100.0))

    def _derive_demand_level(self, state: SimulationState, events: list[EventLogEntry]) -> float:
        # MVP: baseline=1.0, Consumer-DEMAND_SHIFT kann +/- durch Text-Hinweis beeinflussen.
        level = 1.0
        for e in events:
            if e.source_agent != "consumer":
                continue
            if e.event_type != EventType.DEMAND_SHIFT:
                continue
            text = e.description.lower()
            if "reduz" in text or "sink" in text or "rueck" in text or "rück" in text:
                level -= 0.05
            if "steiger" in text or "wachst" in text:
                level += 0.05
        return max(0.0, min(2.0, level))

    def _extract_percent(self, text: str) -> float | None:
        match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", text)
        if not match:
            return None
        try:
            return float(match.group(1))
        except ValueError:
            return None

