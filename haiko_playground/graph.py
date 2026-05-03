"""LangGraph project entry for the Simulation (haiko_playground)

This file constructs a StateGraph (if langgraph installed) that wraps the
existing simulation nodes in `src/` and exposes a compiled graph suitable for
`langgraph dev` to pick up in many setups.

Usage (from haiko_playground):
    langgraph dev

The graph uses the LLM implementation returned by `llm_adapter.get_llm()`.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ensure project root is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# load local .env and prompt for secrets if needed (LANGSMITH_API_KEY etc.)
try:
    from .env_utils import load_env as _load_env
except Exception:
    # try absolute import fallback
    try:
        from haiko_playground.env_utils import load_env as _load_env
    except Exception:
        _load_env = None

if _load_env:
    _load_env()

from src.config_loader import build_initial_state
from src.models.agent_models import AgentConfig
from src.models.enums import AgentType
from src.nodes.agent_node import AgentNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.cib_extractor_node import CIBExtractorNode

try:
    from .llm_adapter import get_llm
except Exception:
    from llm_adapter import get_llm


def build_stategraph():
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
    except Exception:
        raise RuntimeError("langgraph package not available in this environment")

    state = build_initial_state()
    agents = state.agents

    orchestrator = OrchestratorNode(agents)
    llm = get_llm()

    # build AgentNode instances
    by_type: dict[AgentType, AgentNode] = {a.agent_type: a for a in agents}
    agent_nodes: dict[str, AgentNode] = {}
    for atype in (AgentType.CONSUMER, AgentType.PROVIDER, AgentType.REGULATOR):
        cfg = by_type.get(atype)
        if cfg:
            agent_nodes[atype.value] = AgentNode(cfg, llm=llm)

    market_node = MarketNode()
    environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
    cib_node = CIBExtractorNode()

    def _deep_merge(base: dict, override: dict) -> dict:
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _coerce_payload(payload: dict | None) -> dict:
        # Studio often starts runs with {}. In that case, start from default config/state.
        base_payload = build_initial_state().model_dump()
        if not payload:
            return base_payload
        # Allow a convenient top-level shorthand: {"max_rounds": 5} or {"rounds": 5}
        if isinstance(payload.get("max_rounds"), int) or isinstance(payload.get("rounds"), int):
            rounds = payload.get("max_rounds") or payload.get("rounds")
            try:
                base_payload.setdefault("clock", {})
                # ensure clock exists in nested config shape
                if isinstance(base_payload.get("clock"), dict):
                    base_payload["clock"]["max_rounds"] = int(rounds)
            except Exception:
                pass

        return _deep_merge(base_payload, payload)

    def _wrap(node_fn):
        def _inner(payload: dict) -> dict:
            from src.models.state_models import SimulationState

            state_in = SimulationState(**_coerce_payload(payload))
            state_out = node_fn(state_in)
            return state_out.model_dump()

        return _inner

    graph = StateGraph(dict)
    graph.add_node("orchestrator", _wrap(orchestrator.invoke))

    # Add nodes if present
    for key in ("consumer", "provider", "regulator"):
        if key in agent_nodes:
            graph.add_node(key, _wrap(agent_nodes[key].invoke))

    graph.add_node("market", _wrap(market_node.invoke))
    graph.add_node("environment", _wrap(environment_node.invoke))
    graph.add_node("cib_extractor", _wrap(cib_node.invoke))

    graph.set_entry_point("orchestrator")

    graph.add_edge("orchestrator", "consumer")
    graph.add_edge("consumer", "provider")
    graph.add_edge("provider", "regulator")
    graph.add_edge("regulator", "market")
    graph.add_edge("market", "environment")

    def _should_continue(payload: dict) -> str:
        from src.models.state_models import SimulationState

        state = SimulationState(**_coerce_payload(payload))
        # Continue rounds until max_rounds; when finished, route to 'cib_extractor'
        return "orchestrator" if state.clock.current_round < state.clock.max_rounds else "cib_extractor"

    graph.add_conditional_edges("environment", _should_continue)
    # After CIB extraction, end the run
    graph.add_edge("cib_extractor", END)

    compiled = graph.compile()

    def runner(state_obj: dict) -> dict:
        return compiled.invoke(state_obj)

    # Export a simple dict for langgraph to use
    return compiled


def _make_build_options() -> dict:
    """Return a compact description of editable run options for Studio UI."""
    try:
        state = build_initial_state()
    except Exception:
        # fallback defaults
        return {
            "max_rounds": {"type": "int", "default": 2, "description": "Maximal number of rounds"},
            "enable_market": {"type": "bool", "default": True, "description": "Enable MarketNode"},
            "llm_model": {"type": "str", "default": "llama3", "description": "LLM model name"},
            "llm_temperature": {"type": "float", "default": 0.7, "description": "LLM temperature"},
        }

    opts = {
        "max_rounds": {"type": "int", "default": state.clock.max_rounds, "description": "Maximal number of rounds"},
        "enable_market": {"type": "bool", "default": True, "description": "Enable MarketNode"},
        "llm_model": {"type": "str", "default": state.config.llm.model, "description": "LLM model name"},
        "llm_temperature": {"type": "float", "default": state.config.llm.temperature, "description": "LLM temperature"},
        "scenario_parameters": [
            {"id": p.id, "name": p.name, "default": p.value, "unit": getattr(p, "unit", None)}
            for p in state.config.scenario_parameters
        ],
        "agents": [{"id": a.id, "name": a.name, "type": a.agent_type.value} for a in state.agents],
    }
    return opts


# Export UI-friendly options for LangGraph Studio to display
try:
    build_options = _make_build_options()
except Exception:
    build_options = {"max_rounds": {"type": "int", "default": 2}}


# Export `graph` symbol (some langgraph setups expect this)
try:
    graph = build_stategraph()
except Exception as e:
    # if langgraph not installed or a setup error occurs, expose error in module
    graph = None
    _build_error = e


def get_build_error():
    return globals().get("_build_error")
