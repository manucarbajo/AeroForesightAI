from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from src.models.agent_models import AgentConfig
from src.models.event_models import EventLogEntry, RoundResult
from src.models.state_models import SimulationState
from src.nodes.agent_node import AgentNode, LLMCallable
from src.nodes.orchestrator_node import OrchestratorNode


@dataclass
class ParallelRoundNode:
    """Run each role agent once per tick (default C4 orchestration).

    Consumer runs first so provider/regulator prompts can include consumer
    segment_analysis from the same tick. Provider and regulator LLM calls
    run concurrently after consumer completes.
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

        primary_id = self._agent_order[0]
        parallel_ids = self._agent_order[1:]

        primary_node = self._agent_nodes.get(primary_id)
        if primary_node is not None:
            state = primary_node.invoke(state)

        if parallel_ids:
            with ThreadPoolExecutor(max_workers=len(parallel_ids)) as pool:
                parallel_results = list(pool.map(self._invoke_agent_isolated, parallel_ids, [state] * len(parallel_ids)))

            for new_round_results, new_events in parallel_results:
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
