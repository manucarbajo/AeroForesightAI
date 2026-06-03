from __future__ import annotations

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
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.nodes.scheduler_node import SchedulerNode
from src.nodes.scenario_agent_node import ScenarioAgentNode
from src.simulation_runner import RunnerOptions
from src.studio_helpers import get_llm


def build_playground_stategraph(
    llm: Any | None = None,
    *,
    options: RunnerOptions | None = None,
):
    """Build and compile the LangGraph stategraph for Studio runs.

    Studio exposes consumer, provider and regulator as separate graph nodes
    (via ``SchedulerNode`` / Redebedarf routing). The CLI batch runner still
    uses ``RoundExecutionNode`` in ``simulation_runner.py`` — same agents,
    same logic, different graph layout for visibility.
    """

    try:
        from langgraph.graph import END, StateGraph  # type: ignore
    except Exception as exc:
        raise RuntimeError("langgraph package not available in this environment") from exc

    runner_options = options or RunnerOptions()
    if llm is None:
        llm = get_llm()

    initial_state = build_initial_state(load_cib=runner_options.enable_cib)
    agents = initial_state.agents

    orchestrator = OrchestratorNode(agents)
    scheduler_node = SchedulerNode()
    market_node = MarketNode()
    environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
    scenario_node = ScenarioAgentNode(llm=llm)

    by_type = {agent.agent_type: agent for agent in agents}
    agent_nodes: dict[str, AgentNode] = {
        "consumer": AgentNode(by_type[AgentType.CONSUMER], llm=llm),
        "provider": AgentNode(by_type[AgentType.PROVIDER], llm=llm),
        "regulator": AgentNode(by_type[AgentType.REGULATOR], llm=llm),
    }

    post_round_target = "market" if runner_options.enable_market else "environment"

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
    if runner_options.enable_market:
        workflow.add_node("market", wrap_node(market_node.invoke))
    workflow.add_node("environment", wrap_node(environment_node.invoke))
    workflow.add_node("scenario_agent", wrap_node(scenario_node.invoke))

    workflow.set_entry_point("initialize_state")
    workflow.add_edge("initialize_state", "reset_round_buffer")
    workflow.add_edge("reset_round_buffer", "orchestrator")
    workflow.add_edge("orchestrator", "determine_next_speaker")

    route_targets = {
        "consumer": "consumer",
        "provider": "provider",
        "regulator": "regulator",
        post_round_target: post_round_target,
    }

    def _route_from_scheduler(payload: Any) -> str:
        state = to_state(payload)
        target = SchedulerNode.route_from_scheduler(state)
        if target == "market" and not runner_options.enable_market:
            return "environment"
        return target

    workflow.add_conditional_edges(
        "determine_next_speaker",
        _route_from_scheduler,
        route_targets,
    )

    workflow.add_edge("consumer", "determine_next_speaker")
    workflow.add_edge("provider", "determine_next_speaker")
    workflow.add_edge("regulator", "determine_next_speaker")
    if runner_options.enable_market:
        workflow.add_edge("market", "environment")

    def _route_after_environment(payload: Any) -> str:
        state = to_state(payload)
        return "reset_round_buffer" if state.clock.current_round < state.clock.max_rounds else "scenario_agent"

    workflow.add_conditional_edges(
        "environment",
        _route_after_environment,
        {
            "reset_round_buffer": "reset_round_buffer",
            "scenario_agent": "scenario_agent",
        },
    )
    workflow.add_edge("scenario_agent", END)

    return workflow.compile()
