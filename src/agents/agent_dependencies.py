"""Agent dependency resolution for M7 profile enforcement."""

from __future__ import annotations

from src.models.agent_models import AgentConfig, AgentProfile
from src.models.state_models import SimulationState


def resolve_parallel_agent_order(agents: list[AgentConfig]) -> list[str]:
    """Return provider/regulator agent ids in depends_on-safe execution order."""

    by_id = {agent.id: agent for agent in agents}
    candidates = [agent_id for agent_id in ("provider", "regulator") if agent_id in by_id]
    if len(candidates) <= 1:
        return candidates

    provider = by_id.get("provider")
    regulator = by_id.get("regulator")
    if provider is None or regulator is None:
        return candidates

    regulator_deps = regulator.profile.depends_on if regulator.profile else []
    if "provider.events" in regulator_deps:
        return ["provider", "regulator"]
    return candidates


def check_depends_on(
    state: SimulationState, profile: AgentProfile | None, agent_id: str
) -> list[str]:
    """Return unresolved dependency labels for this tick (empty if all satisfied)."""

    if profile is None or not profile.depends_on:
        return []

    current_tick = state.clock.current_tick
    missing: list[str] = []

    for dependency in profile.depends_on:
        if dependency == "provider.events":
            if not _has_agent_events(state, "provider", current_tick):
                missing.append(dependency)
        elif dependency == "regulator.proposed_state":
            if not _has_factor_proposals(state, "regulator", current_tick):
                missing.append(dependency)
        elif dependency == "consumer.booking_rate":
            if not _has_prior_booking(state, current_tick):
                missing.append(dependency)
        elif dependency == "regulatory_influences":
            if not state.resolved_properties().regulatory_influences:
                missing.append(dependency)
        else:
            missing.append(dependency)

    return missing


def format_depends_on_block(
    state: SimulationState,
    profile: AgentProfile | None,
    agent_id: str,
) -> str:
    """Summarise dependency inputs available to the agent this tick."""

    if profile is None or not profile.depends_on:
        return "- No profile dependencies configured."

    current_tick = state.clock.current_tick
    lines = ["Profile dependencies (must be reflected in your reasoning):"]

    for dependency in profile.depends_on:
        if dependency == "provider.events":
            events = _agent_events(state, "provider", current_tick)
            if events:
                lines.append(f"- provider.events: {events[0].description}")
            else:
                lines.append("- provider.events: not yet available this tick")
        elif dependency == "regulator.proposed_state":
            proposals = _factor_proposals(state, "regulator", current_tick)
            if proposals:
                lines.append(f"- regulator.proposed_state: {', '.join(proposals)}")
            else:
                lines.append("- regulator.proposed_state: no factor proposals this tick")
        elif dependency == "consumer.booking_rate":
            prior = _prior_booking_stats(state, current_tick)
            if prior is None:
                lines.append("- consumer.booking_rate: no prior tick (first tick)")
            else:
                lines.append(
                    f"- consumer.booking_rate: {prior.get('total_demand')} "
                    f"(tick {prior.get('round_number')})"
                )
        elif dependency == "regulatory_influences":
            influences = state.resolved_properties().regulatory_influences
            if influences:
                names = ", ".join(item.id for item in influences[:6])
                lines.append(f"- regulatory_influences: {names}")
            else:
                lines.append("- regulatory_influences: none configured")
        else:
            lines.append(f"- {dependency}: (unmapped dependency)")

    missing = check_depends_on(state, profile, agent_id)
    if missing:
        lines.append(
            "WARNING: unresolved dependencies this tick: "
            + ", ".join(missing)
            + " — use NO_OP if you cannot ground a response."
        )

    return "\n".join(lines)


def _has_agent_events(state: SimulationState, agent_id: str, tick: int) -> bool:
    return bool(_agent_events(state, agent_id, tick))


def _agent_events(state: SimulationState, agent_id: str, tick: int):
    return [
        event
        for event in state.event_log
        if event.round_number == tick and event.source_agent == agent_id
    ]


def _has_factor_proposals(state: SimulationState, agent_id: str, tick: int) -> bool:
    return bool(_factor_proposals(state, agent_id, tick))


def _factor_proposals(state: SimulationState, agent_id: str, tick: int) -> list[str]:
    proposals: list[str] = []
    for round_result in state.round_results:
        if round_result.round_number != tick:
            continue
        for response in round_result.agent_responses:
            if response.agent_id != agent_id:
                continue
            for change in response.state_changes:
                proposals.append(f"{change.factor_id}→{change.proposed_state}")
    return proposals


def _has_prior_booking(state: SimulationState, current_tick: int) -> bool:
    return _prior_booking_stats(state, current_tick) is not None


def _prior_booking_stats(state: SimulationState, current_tick: int) -> dict | None:
    for entry in reversed(state.population_stats):
        round_number = entry.get("round_number")
        if round_number is not None and round_number < current_tick:
            return entry
    return None
