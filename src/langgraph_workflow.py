from __future__ import annotations

try:
    from haiko_playground.env_utils import load_env as _load_env
except Exception:
    _load_env = None

if _load_env is not None:
    _load_env()

from typing import Any

from src.config_loader import build_initial_state
from src.langgraph_adapter import (
    append_spoken_agent,
    initialize_state,
    reset_round_buffer,
    to_state,
    wrap_node,
)
from src.models.enums import AgentType
from src.models.state_models import InputState, PlaygroundState
from src.nodes.agent_node import AgentNode
from src.nodes.cib_extractor_node import CIBExtractorNode
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.nodes.scheduler_node import SchedulerNode
from src.nodes.scenario_agent_node import ScenarioAgentNode
from src.studio_helpers import get_llm


def build_playground_stategraph(llm: Any | None = None):
    """Build and compile the LangGraph stategraph for AP3 playground runs.

    All simulation flow logic lives in `src` so `haiko_playground` remains a
    thin LangGraph Studio adapter.
    """

    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception as exc:
        raise RuntimeError("langgraph package not available in this environment") from exc

    if llm is None:
        llm = get_llm()

    initial_state = build_initial_state()
    agents = initial_state.agents

    orchestrator = OrchestratorNode(agents)
    scheduler_node = SchedulerNode()
    market_node = MarketNode()
    environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
    cib_node = CIBExtractorNode(llm=llm)
    scenario_node = ScenarioAgentNode(llm=llm)

    by_type = {agent.agent_type: agent for agent in agents}
    agent_nodes: dict[str, AgentNode] = {
        "consumer": AgentNode(by_type[AgentType.CONSUMER], llm=llm),
        "provider": AgentNode(by_type[AgentType.PROVIDER], llm=llm),
        "regulator": AgentNode(by_type[AgentType.REGULATOR], llm=llm),
    }

    workflow = StateGraph(PlaygroundState, input_schema=InputState)
    workflow.add_node("initialize_state", initialize_state)
    workflow.add_node("reset_round_buffer", reset_round_buffer)
    workflow.add_node("orchestrator", wrap_node(orchestrator.invoke))
    workflow.add_node("determine_next_speaker", wrap_node(scheduler_node.invoke))
    workflow.add_node(
        "consumer",
        wrap_node(
            agent_nodes["consumer"].invoke,
            on_exit=lambda state: append_spoken_agent(state, "consumer"),
        ),
    )
    workflow.add_node(
        "provider",
        wrap_node(
            agent_nodes["provider"].invoke,
            on_exit=lambda state: append_spoken_agent(state, "provider"),
        ),
    )
    workflow.add_node(
        "regulator",
        wrap_node(
            agent_nodes["regulator"].invoke,
            on_exit=lambda state: append_spoken_agent(state, "regulator"),
        ),
    )
    workflow.add_node("market", wrap_node(market_node.invoke))
    workflow.add_node("environment", wrap_node(environment_node.invoke))
    workflow.add_node("cib_extractor", wrap_node(cib_node.invoke))
    workflow.add_node("scenario_agent", wrap_node(scenario_node.invoke))

    workflow.set_entry_point("initialize_state")
    workflow.add_edge("initialize_state", "reset_round_buffer")
    workflow.add_edge("reset_round_buffer", "orchestrator")
    workflow.add_edge("orchestrator", "determine_next_speaker")

    workflow.add_conditional_edges(
        "determine_next_speaker",
        lambda payload: SchedulerNode.route_from_scheduler(to_state(payload)),
        {
            "consumer": "consumer",
            "provider": "provider",
            "regulator": "regulator",
            "market": "market",
        },
    )

    workflow.add_edge("consumer", "determine_next_speaker")
    workflow.add_edge("provider", "determine_next_speaker")
    workflow.add_edge("regulator", "determine_next_speaker")
    workflow.add_edge("market", "environment")

    # CIB runs once at the end of the simulation run.
    def _route_after_environment(payload: Any) -> str:
        state = to_state(payload)
        return "reset_round_buffer" if state.clock.current_round < state.clock.max_rounds else "cib_extractor"

    workflow.add_conditional_edges("environment", _route_after_environment)
    workflow.add_edge("cib_extractor", "scenario_agent")
    workflow.add_edge("scenario_agent", END)

    return workflow.compile()
