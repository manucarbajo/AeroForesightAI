from __future__ import annotations

from dataclasses import dataclass

from src.agent_dependencies import resolve_parallel_agent_order
from src.models.agent_models import AgentConfig
from src.models.event_models import EventLogEntry, RoundResult
from src.models.state_models import SimulationState
from src.nodes.agent_node import AgentNode, LLMCallable
from src.nodes.orchestrator_node import OrchestratorNode


@dataclass
class ParallelRoundNode:
    """Run provider then regulator once per tick (depends_on order).

    Consumer runs after environment booking (see SimulationRunner) so narrative
    and events align with observed ``booking_rate``.
    """
    agents: list[AgentConfig]
    llm: LLMCallable

    def __post_init__(self) -> None:
        self._agent_nodes: dict[str, AgentNode] = {
            agent.id: AgentNode(agent, llm=self.llm) for agent in self.agents
        }
        self._agent_order = OrchestratorNode(self.agents).ordered_agent_ids()

    def invoke(self, state: SimulationState) -> SimulationState:
        if not self._agent_order:
            return state

        round_number = state.clock.current_tick
        if round_number < 1:
            return state

        parallel_ids = [
            agent_id
            for agent_id in resolve_parallel_agent_order(self.agents)
            if agent_id in self._agent_nodes
        ]
        if not parallel_ids:
            return state

        for agent_id in parallel_ids:
            new_round_results, new_events = self._invoke_agent_isolated(agent_id, state)
            state.round_results.extend(new_round_results)
            state.event_log.extend(new_events)

        state.current_speech_order = list(self._agent_order)
        state.current_round_spoken_agents = list(self._agent_order)
        state.redebedarf_scores = {}
        state.current_speech_candidates = []
        state.speech_plan = None

        return state

    def _invoke_agent_isolated(
        self,
        agent_id: str,
        base_state: SimulationState,
    ) -> tuple[list[RoundResult], list[EventLogEntry]]:
        node = self._agent_nodes.get(agent_id)
        if node is None:
            return [], []

        snapshot = base_state.model_copy(deep=True)
        round_results_before = len(snapshot.round_results)
        events_before = len(snapshot.event_log)

        updated = node.invoke(snapshot)
        new_round_results = updated.round_results[round_results_before:]
        new_events = updated.event_log[events_before:]
        return new_round_results, new_events
