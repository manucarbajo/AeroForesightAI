from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config_loader import build_initial_state
from src.models.agent_models import AgentConfig
from src.models.cib_models import CIBMatrixHistory
from src.models.enums import AgentType
from src.models.state_models import SimulationState
from src.nodes.agent_node import AgentNode, LLMCallable
from src.nodes.cib_extractor_node import CIBExtractorNode
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.validation import validate_state


@dataclass(frozen=True)
class RunnerOptions:
    enable_market: bool = True
    enable_cib: bool = True


class SimulationRunner:
    def __init__(self, llm: LLMCallable, options: RunnerOptions | None = None) -> None:
        self.llm = llm
        self.options = options or RunnerOptions()

    def build_graph(self, agents: list[AgentConfig]) -> Callable[[SimulationState], SimulationState]:
        # LangGraph ist optional; wenn nicht vorhanden, liefern wir einen deterministischen Runner-Fallback.
        try:
            from langgraph.graph import END, StateGraph  # type: ignore
        except Exception:
            return self._build_sequential_runner(agents)

        orchestrator = OrchestratorNode(agents)
        agent_nodes = self._build_agent_nodes(agents)
        market_node = MarketNode()
        environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
        cib_extractor = CIBExtractorNode(llm=self.llm) if self.options.enable_cib else None

        # LangGraph arbeitet intern mit dict-State; wir halten die Public-API als SimulationState.
        def _wrap(node_fn: Callable[[SimulationState], SimulationState]) -> Callable[[dict], dict]:
            def _inner(payload: dict) -> dict:
                state_in = SimulationState(**payload)
                state_out = node_fn(state_in)
                return state_out.model_dump()

            return _inner

        graph = StateGraph(dict)
        graph.add_node("orchestrator", _wrap(orchestrator.invoke))
        graph.add_node("consumer", _wrap(agent_nodes["consumer"].invoke))
        graph.add_node("provider", _wrap(agent_nodes["provider"].invoke))
        graph.add_node("regulator", _wrap(agent_nodes["regulator"].invoke))
        if self.options.enable_market:
            graph.add_node("market", _wrap(market_node.invoke))
        graph.add_node("environment", _wrap(environment_node.invoke))
        if cib_extractor is not None:
            graph.add_node("cib_extractor", _wrap(cib_extractor.invoke))

        graph.set_entry_point("orchestrator")

        graph.add_edge("orchestrator", "consumer")
        graph.add_edge("consumer", "provider")
        graph.add_edge("provider", "regulator")
        if self.options.enable_market:
            graph.add_edge("regulator", "market")
            graph.add_edge("market", "environment")
        else:
            graph.add_edge("regulator", "environment")

        if cib_extractor is not None:
            graph.add_edge("environment", "cib_extractor")

            def _should_continue(payload: dict) -> str:
                state = SimulationState(**payload)
                return "orchestrator" if state.clock.current_round < state.clock.max_rounds else END

            graph.add_conditional_edges("cib_extractor", _should_continue)
        else:
            def _should_continue(payload: dict) -> str:
                state = SimulationState(**payload)
                return "orchestrator" if state.clock.current_round < state.clock.max_rounds else END

            graph.add_conditional_edges("environment", _should_continue)

        compiled = graph.compile()

        def _run(state: SimulationState) -> SimulationState:
            out = compiled.invoke(state.model_dump())
            return SimulationState(**out)

        return _run

    def run(self) -> SimulationState:
        state = build_initial_state()
        validate_state(state)

        run_graph = self.build_graph(state.agents)
        state = run_graph(state)
        validate_state(state)
        return state

    def _build_agent_nodes(self, agents: list[AgentConfig]) -> dict[str, AgentNode]:
        by_type: dict[AgentType, AgentConfig] = {a.agent_type: a for a in agents}

        # Der MVP erwartet genau diese drei Agenten.
        consumer = AgentNode(by_type[AgentType.CONSUMER], llm=self.llm)
        provider = AgentNode(by_type[AgentType.PROVIDER], llm=self.llm)
        regulator = AgentNode(by_type[AgentType.REGULATOR], llm=self.llm)

        return {
            "consumer": consumer,
            "provider": provider,
            "regulator": regulator,
        }

    def _build_sequential_runner(self, agents: list[AgentConfig]) -> Callable[[SimulationState], SimulationState]:
        orchestrator = OrchestratorNode(agents)
        agent_nodes = self._build_agent_nodes(agents)
        market_node = MarketNode()
        environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
        cib_extractor = CIBExtractorNode(llm=self.llm) if self.options.enable_cib else None

        def _run(state: SimulationState) -> SimulationState:
            if state.cib_history is None:
                state.cib_history = CIBMatrixHistory()

            while state.clock.current_round < state.clock.max_rounds:
                state = orchestrator.invoke(state)
                state = agent_nodes["consumer"].invoke(state)
                state = agent_nodes["provider"].invoke(state)
                state = agent_nodes["regulator"].invoke(state)
                if self.options.enable_market:
                    state = market_node.invoke(state)
                state = environment_node.invoke(state)
                if cib_extractor is not None:
                    state = cib_extractor.invoke(state)
            return state

        return _run

