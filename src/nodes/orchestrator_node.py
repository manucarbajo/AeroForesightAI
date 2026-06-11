from __future__ import annotations

from src.models.agent_models import AgentConfig
from src.models.enums import AgentType
from src.models.state_models import SimulationState


class OrchestratorNode:
    def __init__(self, agents: list[AgentConfig]) -> None:
        self._agents_by_type: dict[AgentType, AgentConfig] = {a.agent_type: a for a in agents}

    def invoke(self, state: SimulationState) -> SimulationState:
        # Start einer neuen Runde: Runde inkrementieren, aber niemals ueber max_rounds hinaus.
        if state.clock.current_tick >= state.clock.max_ticks:
            return state
        state.clock.current_tick += 1
        return state

    def ordered_agent_ids(self) -> list[str]:
        # MVP: feste Reihenfolge, entspricht dem Projektplan (Consumer -> Provider -> Regulator).
        ordered: list[AgentType] = [
            AgentType.CONSUMER,
            AgentType.PROVIDER,
            AgentType.REGULATOR,
        ]
        ids: list[str] = []
        for agent_type in ordered:
            config = self._agents_by_type.get(agent_type)
            if config:
                ids.append(config.id)
        return ids

