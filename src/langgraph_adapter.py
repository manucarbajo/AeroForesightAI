from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable

from pydantic import BaseModel

from src.config_loader import build_initial_state
from src.models.state_models import SimulationState
from typing import Any


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, appending unique items to lists."""
    merged = dict(base)
    for key, value in override.items():
        if value is None and key in {"config", "clock", "environment", "agents"}:
            continue
        if isinstance(value, list) and isinstance(merged.get(key), list):
            combined = list(merged[key])
            for item in value:
                if item not in combined:
                    combined.append(item)
            merged[key] = combined
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def payload_to_dict(payload: Any | None) -> dict[str, Any]:
    """Extract a dictionary from a generic payload."""
    if payload is None:
        return {}
    if isinstance(payload, BaseModel):
        return payload.model_dump()
    if isinstance(payload, Mapping):
        return dict(payload)
    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, Mapping):
            return dict(dumped)
    return {}


def coerce_payload(payload: Any | None) -> dict[str, Any]:
    """Merge an incoming Studio payload against the default initial state."""
    base_payload = build_initial_state().model_dump()
    payload_dict = payload_to_dict(payload)
    if not payload_dict:
        return base_payload

    if isinstance(payload_dict.get("max_ticks"), int) or isinstance(payload_dict.get("max_rounds"), int) or isinstance(payload_dict.get("rounds"), int):
        ticks = payload_dict.get("max_ticks") or payload_dict.get("max_rounds") or payload_dict.get("rounds")
        base_payload.setdefault("clock", {})
        if isinstance(base_payload.get("clock"), dict):
            base_payload["clock"]["max_ticks"] = int(ticks)

    if payload_dict.get("seed") is not None:
        base_payload.setdefault("config", {})
        if isinstance(base_payload.get("config"), dict):
            base_payload["config"]["seed"] = payload_dict["seed"]

    if any(key in payload_dict for key in ("llm_model", "llm_temperature", "llm_max_tokens")):
        base_payload.setdefault("config", {})
        base_payload["config"].setdefault("llm", {})
        if isinstance(base_payload["config"].get("llm"), dict):
            if payload_dict.get("llm_model") is not None:
                base_payload["config"]["llm"]["model"] = payload_dict["llm_model"]
            if payload_dict.get("llm_temperature") is not None:
                base_payload["config"]["llm"]["temperature"] = payload_dict["llm_temperature"]
            if payload_dict.get("llm_max_tokens") is not None:
                base_payload["config"]["llm"]["max_tokens"] = payload_dict["llm_max_tokens"]

    if payload_dict.get("policy_schedule") is not None:
        base_payload.setdefault("config", {})
        if isinstance(base_payload.get("config"), dict):
            base_payload["config"]["policy_schedule"] = payload_dict["policy_schedule"]

    return deep_merge(base_payload, payload_dict)


def to_state(payload: Any) -> SimulationState:
    """Convert an arbitrary incoming payload into a strictly typed SimulationState."""
    return SimulationState(**coerce_payload(payload))


def wrap_node(
    node_fn: Callable[[SimulationState], SimulationState],
    *,
    on_enter: Callable[[SimulationState], None] | None = None,
    on_exit: Callable[[SimulationState], dict[str, Any] | None] | None = None,
) -> Callable[[Any], dict[str, Any]]:
    """Wrap a typed Node `invoke` function for LangGraph dict-in/dict-out execution."""

    def _inner(payload: Any) -> dict[str, Any]:
        state_in = to_state(payload)
        if callable(on_enter):
            on_enter(state_in)
            
        state_out = node_fn(state_in)
        
        if callable(on_exit):
            update = on_exit(state_out)
            if isinstance(update, Mapping):
                merged_state = deep_merge(state_out.model_dump(), payload_to_dict(update))
                state_out = SimulationState(**merged_state)
                
        return state_out.model_dump()

    return _inner


def initialize_state(payload: Any) -> dict[str, Any]:
    """Adapter helper: coerce incoming payload into serialisable state dict."""
    return to_state(payload).model_dump()


def reset_round_buffer(payload: Any) -> dict[str, Any]:
    """Adapter helper: reset per-round spoken agent buffer."""
    state = to_state(payload)
    state.current_round_spoken_agents = []
    return state.model_dump()


def append_spoken_agent(state: SimulationState, agent_id: str) -> dict[str, list[str]]:
    """Ensure `agent_id` is recorded in the per-round spoken list and
    return a minimal update dict suitable for LangGraph on_exit hooks.
    """
    if agent_id not in state.current_round_spoken_agents:
        state.current_round_spoken_agents.append(agent_id)
    return {"current_round_spoken_agents": [agent_id]}


def _make_build_options() -> dict:
    """Return a compact description of editable run options for Studio UI.

    Kept here so the minimal ``langgraph_studio`` adapter can import a ready-made
    build-options payload without owning inspection logic.
    """
    try:
        state = build_initial_state()
    except Exception:
        return {
            "max_ticks": {"type": "int", "default": 2, "description": "Maximal number of ticks"},
            "enable_market": {"type": "bool", "default": True, "description": "Enable MarketNode"},
            "llm_model": {"type": "str", "default": "llama3", "description": "LLM model name"},
            "llm_temperature": {"type": "float", "default": 0.7, "description": "LLM temperature"},
            "presets": {
                "type": "object",
                "default": {
                    "quick_test": {"max_ticks": 4, "seed": 42, "llm_model": "llama3"},
                    "full_ap3": {"max_ticks": 40, "seed": 42, "llm_model": "llama3.2"},
                },
                "description": "Helpful AP3 starter presets for Studio and playground runs",
            },
        }

    return {
        "max_ticks": {"type": "int", "default": state.clock.max_ticks, "description": "Maximal number of ticks"},
        "enable_market": {"type": "bool", "default": True, "description": "Enable MarketNode"},
        "llm_model": {"type": "str", "default": state.config.llm.model, "description": "LLM model name"},
        "llm_temperature": {"type": "float", "default": state.config.llm.temperature, "description": "LLM temperature"},
        "presets": {
            "type": "object",
            "default": {
                    "quick_test": {"max_ticks": 4, "seed": 42, "llm_model": state.config.llm.model},
                "full_ap3": {
                    "max_ticks": state.clock.max_ticks,
                    "seed": state.config.seed,
                    "llm_model": state.config.llm.model,
                },
            },
            "description": "Helpful AP3 starter presets for Studio and playground runs",
        },
        "policy_schedule": state.config.policy_schedule.model_dump()
        if state.config.policy_schedule is not None
        else None,
        "agents": [{"id": a.id, "name": a.name, "type": a.agent_type.value} for a in state.agents],
    }


def get_build_options() -> dict:
    """Public accessor used by the playground adapter.

    Wrapped so callers don't need to import implementation-names starting with
    an underscore.
    """
    try:
        return _make_build_options()
    except Exception:
        return {"max_ticks": {"type": "int", "default": 2}}

