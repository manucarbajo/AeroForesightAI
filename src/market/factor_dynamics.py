"""Deterministic factor transitions and gated LLM factor proposals."""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.agent_permissions import may_propose_factor
from src.market.property_engine import resolve_system_properties
from src.market.simulation_functions import active_parameters
from src.models.agent_models import StateChange
from src.models.property_models import FactorRule, PropertiesConfig
from src.models.state_models import SimulationState
from src.rule_engine import RuleContext, RuntimeMetrics, rule_matches


@dataclass
class FactorRuleApplication:
    rule_id: str
    factor_id: str
    from_state: str
    to_state: str
    reasoning: str


def build_runtime_metrics(state: SimulationState) -> RuntimeMetrics:
    tick = state.clock.current_tick
    properties = state.resolved_properties()
    params = active_parameters(max(1, tick), properties)
    metrics = dict(state.market_metrics)

    prior_booking_rate: float | None = None
    for entry in reversed(state.population_stats):
        entry_tick = entry.get("round_number")
        if entry_tick is None or entry_tick >= tick:
            continue
        prior_booking_rate = entry.get("total_demand")
        break

    booking_rate = metrics.get("booking_rate")
    if booking_rate is None:
        booking_rate = prior_booking_rate

    demand_level = metrics.get("demand_level")
    if demand_level is None and state.price_history:
        demand_level = state.price_history[-1].demand_level

    return RuntimeMetrics(
        tick=tick,
        booking_rate=booking_rate,
        prior_booking_rate=prior_booking_rate,
        cost_pressure=metrics.get("cost_pressure"),
        cost_index=metrics.get("cost_index"),
        ticket_price=metrics.get("ticket_price"),
        demand_level=demand_level,
        carbon_tax_level=params.get("carbon_tax_level"),
        saf_mandate_share=params.get("saf_mandate_share"),
        fuel_price_change=params.get("fuel_price_change"),
        oil_price_index=params.get("oil_price_index"),
    )


def _sorted_rules(rules: list[FactorRule]) -> list[FactorRule]:
    return sorted(rules, key=lambda rule: (-rule.priority, rule.id))


def allowed_factor_targets(
    state: SimulationState,
    *,
    properties: PropertiesConfig | None = None,
) -> dict[str, set[str]]:
    """States each factor may take this tick (current + rule-backed targets)."""

    properties = properties or state.resolved_properties()
    factors = state.environment.factors
    metrics = build_runtime_metrics(state)
    system_properties = resolve_system_properties(max(1, metrics.tick), properties)
    applied_ids = set(state.applied_factor_rule_ids)

    allowed: dict[str, set[str]] = {
        factor_id: {factor.current_state} for factor_id, factor in factors.items()
    }

    context = RuleContext.from_metrics(
        metrics, factors=factors, system_properties=system_properties
    )

    for rule in _sorted_rules(properties.factor_rules):
        factor = factors.get(rule.factor_id)
        if factor is None:
            continue
        if rule.effect.set_state not in factor.possible_states:
            continue
        if rule.once and rule.id in applied_ids:
            continue
        if not rule_matches(rule.when, context, rule_id=rule.id):
            continue
        allowed.setdefault(rule.factor_id, set()).add(rule.effect.set_state)

    return allowed


def apply_factor_rules(state: SimulationState) -> list[FactorRuleApplication]:
    """Apply M5 ``factor_rules`` at tick start (Python only)."""

    properties = state.resolved_properties()
    if not properties.factor_rules:
        return []

    factors = state.environment.factors
    metrics = build_runtime_metrics(state)
    system_properties = resolve_system_properties(max(1, metrics.tick), properties)
    applied_ids = set(state.applied_factor_rule_ids)
    updated_factors: set[str] = set()
    applications: list[FactorRuleApplication] = []
    context = RuleContext.from_metrics(
        metrics, factors=factors, system_properties=system_properties
    )

    for rule in _sorted_rules(properties.factor_rules):
        if rule.factor_id in updated_factors:
            continue
        factor = factors.get(rule.factor_id)
        if factor is None:
            continue
        target_state = rule.effect.set_state
        if target_state not in factor.possible_states:
            continue
        # `once` ist keine Bedingung der Klausel und wird deshalb hier geführt,
        # nicht im Evaluator (P0.4).
        if rule.once and rule.id in applied_ids:
            continue
        if not rule_matches(rule.when, context, rule_id=rule.id):
            continue

        previous_state = factor.current_state
        if previous_state == target_state:
            if rule.once and rule.id not in state.applied_factor_rule_ids:
                state.applied_factor_rule_ids.append(rule.id)
            continue

        factor.current_state = target_state
        updated_factors.add(rule.factor_id)
        if rule.once and rule.id not in state.applied_factor_rule_ids:
            state.applied_factor_rule_ids.append(rule.id)
        applications.append(
            FactorRuleApplication(
                rule_id=rule.id,
                factor_id=rule.factor_id,
                from_state=previous_state,
                to_state=target_state,
                reasoning=f"factor_rule {rule.id}",
            )
        )

    return applications


def validate_factor_proposals(
    state: SimulationState,
    proposals: list[StateChange],
    *,
    agent_id: str,
) -> list[StateChange]:
    """Gate LLM ``state_changes`` against ``factor_rules`` and agent permissions."""

    if not proposals:
        return []

    allowed_targets = allowed_factor_targets(state)
    # Die Berechtigung kommt seit P0.5 ausschließlich aus `agent_profiles.json`
    # und wird von derselben Funktion geprüft, die auch der Parser benutzt.
    profile = next(
        (agent.profile for agent in state.agents if agent.id == agent_id),
        None,
    )
    validated: list[StateChange] = []

    for change in proposals:
        factor = state.environment.factors.get(change.factor_id)
        if factor is None:
            continue
        if change.proposed_state not in factor.possible_states:
            continue
        if change.proposed_state == factor.current_state:
            continue
        if not may_propose_factor(profile, change.factor_id):
            continue
        if change.proposed_state not in allowed_targets.get(change.factor_id, set()):
            continue
        validated.append(change)

    return validated


def record_factor_timeseries(state: SimulationState) -> SimulationState:
    """Append one row of factor descriptor states for the current tick."""

    tick = state.clock.current_tick
    if tick < 1:
        return state

    row: dict[str, object] = {"tick": tick}
    for factor_id in sorted(state.environment.factors.keys()):
        row[factor_id] = state.environment.factors[factor_id].current_state

    if state.factor_timeseries and state.factor_timeseries[-1].get("tick") == tick:
        state.factor_timeseries[-1] = row
    else:
        state.factor_timeseries.append(row)
    return state


def apply_factor_rules_at_tick_start(state: SimulationState) -> SimulationState:
    """Tick hook: run Python factor rules before agent LLM calls."""

    if state.clock.current_tick < 1:
        return state
    apply_factor_rules(state)
    return state
