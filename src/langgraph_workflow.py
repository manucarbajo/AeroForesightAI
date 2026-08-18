from __future__ import annotations

import os
from typing import Any

from src.agents.agent_node import AgentNode
from src.agents.orchestrator_node import OrchestratorNode
from src.agents.parallel_round_node import ParallelRoundNode
from src.agents.scheduler_node import SchedulerNode
from src.config_loader import build_initial_state
from src.factor_dynamics import apply_factor_rules_at_tick_start, record_factor_timeseries
from src.langgraph_adapter import (
    append_spoken_agent,
    initialize_state,
    reset_round_buffer,
    to_state,
    wrap_node,
)
from src.llm import get_llm
from src.models.enums import AgentType
from src.models.state_models import InputState, PlaygroundState
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.scenario_agent_node import ScenarioAgentNode
from src.simulation_runner import RunnerOptions


def build_playground_stategraph(
    llm: Any | None = None,
    *,
    options: RunnerOptions | None = None,
):
    """Build and compile the LangGraph stategraph for Studio runs.

    Default (C4/M4): orchestrator → parallel_round → environment → consumer → market — no
    Redebedarf scheduler. With ``enable_redebedarf`` (CLI ``--redebedarf`` or
    env ``SIMULATION_REDEBEDARF=1``): legacy scheduler loop with separate
    consumer / provider / regulator nodes.
    """

    try:
        pass  # type: ignore
    except Exception as exc:
        raise RuntimeError("langgraph package not available in this environment") from exc

    runner_options = options or _runner_options_from_env()
    if llm is None:
        llm = get_llm()

    if runner_options.enable_redebedarf:
        return _build_redebedarf_stategraph(llm, runner_options=runner_options)
    return _build_parallel_stategraph(llm, runner_options=runner_options)


def _runner_options_from_env() -> RunnerOptions:
    redebedarf = os.environ.get("SIMULATION_REDEBEDARF", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    no_market = os.environ.get("SIMULATION_NO_MARKET", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    return RunnerOptions(enable_market=not no_market, enable_redebedarf=redebedarf)


def _build_parallel_stategraph(
    llm: Any,
    *,
    runner_options: RunnerOptions,
):
    from langgraph.graph import END, StateGraph  # type: ignore

    initial_state = build_initial_state(load_cib=runner_options.enable_cib)
    agents = initial_state.agents

    orchestrator = OrchestratorNode(agents)
    parallel_round = ParallelRoundNode(agents, llm=llm)
    market_node = MarketNode()
    environment_node = EnvironmentNode(
        prefer_agent_order=orchestrator.ordered_agent_ids()[::-1],
        llm=llm,
    )
    consumer_config = next((agent for agent in agents if agent.id == "consumer"), None)
    consumer_node = AgentNode(consumer_config, llm=llm) if consumer_config is not None else None
    scenario_node = ScenarioAgentNode(llm=llm)

    workflow = StateGraph(PlaygroundState, input_schema=InputState)
    workflow.add_node("initialize_state", initialize_state)
    workflow.add_node("reset_round_buffer", reset_round_buffer)
    workflow.add_node("orchestrator", wrap_node(orchestrator.invoke))
    workflow.add_node("factor_rules", wrap_node(apply_factor_rules_at_tick_start))
    workflow.add_node("parallel_round", wrap_node(parallel_round.invoke))
    workflow.add_node("environment", wrap_node(environment_node.invoke))
    if consumer_node is not None:

        def _consumer_after_booking(payload: Any) -> Any:
            state = to_state(payload)
            state = consumer_node.invoke(state)
            state = environment_node.apply_consumer_factor_updates(state)
            return state.model_dump()

        workflow.add_node("consumer", _consumer_after_booking)
    if runner_options.enable_market:

        def _market_with_factor_timeseries(payload: Any) -> Any:
            state = to_state(payload)
            state = market_node.invoke(state)
            state = record_factor_timeseries(state)
            return state.model_dump()

        workflow.add_node("market", _market_with_factor_timeseries)
    workflow.add_node("scenario_agent", wrap_node(scenario_node.invoke))

    workflow.set_entry_point("initialize_state")
    workflow.add_edge("initialize_state", "reset_round_buffer")
    workflow.add_edge("reset_round_buffer", "orchestrator")
    workflow.add_edge("orchestrator", "factor_rules")
    workflow.add_edge("factor_rules", "parallel_round")
    workflow.add_edge("parallel_round", "environment")
    if consumer_node is not None:
        workflow.add_edge("environment", "consumer")
        if runner_options.enable_market:
            workflow.add_edge("consumer", "market")
    elif runner_options.enable_market:
        workflow.add_edge("environment", "market")

    def _route_after_tick(payload: Any) -> str:
        state = to_state(payload)
        return (
            "reset_round_buffer"
            if state.clock.current_tick < state.clock.max_ticks
            else "scenario_agent"
        )

    if runner_options.enable_market:
        tick_end_node = "market"
    elif consumer_node is not None:
        tick_end_node = "consumer"
    else:
        tick_end_node = "environment"
    workflow.add_conditional_edges(
        tick_end_node,
        _route_after_tick,
        {
            "reset_round_buffer": "reset_round_buffer",
            "scenario_agent": "scenario_agent",
        },
    )
    workflow.add_edge("scenario_agent", END)

    return workflow.compile()


def _build_redebedarf_stategraph(
    llm: Any,
    *,
    runner_options: RunnerOptions,
):
    from langgraph.graph import END, StateGraph  # type: ignore

    initial_state = build_initial_state(load_cib=runner_options.enable_cib)
    agents = initial_state.agents

    orchestrator = OrchestratorNode(agents)
    scheduler_node = SchedulerNode()
    market_node = MarketNode()
    environment_node = EnvironmentNode(
        prefer_agent_order=orchestrator.ordered_agent_ids()[::-1],
        llm=llm,
    )
    scenario_node = ScenarioAgentNode(llm=llm)

    by_type = {agent.agent_type: agent for agent in agents}
    agent_nodes: dict[str, AgentNode] = {
        "consumer": AgentNode(by_type[AgentType.CONSUMER], llm=llm),
        "provider": AgentNode(by_type[AgentType.PROVIDER], llm=llm),
        "regulator": AgentNode(by_type[AgentType.REGULATOR], llm=llm),
    }

    post_round_target = "environment"

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
        if target == "market":
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
        workflow.add_edge("environment", "market")

    def _route_after_tick_redebedarf(payload: Any) -> str:
        state = to_state(payload)
        return (
            "reset_round_buffer"
            if state.clock.current_tick < state.clock.max_ticks
            else "scenario_agent"
        )

    tick_end_node = "market" if runner_options.enable_market else "environment"
    workflow.add_conditional_edges(
        tick_end_node,
        _route_after_tick_redebedarf,
        {
            "reset_round_buffer": "reset_round_buffer",
            "scenario_agent": "scenario_agent",
        },
    )
    workflow.add_edge("scenario_agent", END)

    return workflow.compile()
