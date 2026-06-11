from __future__ import annotations

from src.config_loader import build_initial_state
from src.factor_dynamics import (
    apply_factor_rules,
    apply_factor_rules_at_tick_start,
    build_runtime_metrics,
    record_factor_timeseries,
    validate_factor_proposals,
)
from src.models.agent_models import StateChange
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.simulation_functions import compute_cost_pressure


def _run_deterministic_tick(state, tick: int):
    state.clock.current_tick = tick
    state = apply_factor_rules_at_tick_start(state)
    state = EnvironmentNode().invoke(state)
    state = MarketNode().invoke(state)
    return record_factor_timeseries(state)


class TestFactorRules:
    def test_high_carbon_tax_sets_f2_and_f6(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 15
        state.market_metrics = {"cost_pressure": compute_cost_pressure(15, state.resolved_properties())}

        applications = apply_factor_rules(state)

        assert state.environment.factors["F2"].current_state == "F2.2"
        assert state.environment.factors["F6"].current_state == "F6.2"
        applied_ids = {item.rule_id for item in applications}
        assert "f2_high_carbon_policy" in applied_ids
        assert "f6_flight_shaming_high_tax" in applied_ids

    def test_low_booking_sets_f1_substitution(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 30
        state.population_stats.append(
            {
                "round_number": 29,
                "total_demand": 0.40,
                "total_booked": 400,
                "total_population": 1000,
                "segments": {},
            }
        )
        state.market_metrics = {
            "booking_rate": 0.40,
            "cost_pressure": 150.0,
        }

        apply_factor_rules(state)

        assert state.environment.factors["F1"].current_state == "F1.2"

    def test_validate_rejects_unauthorized_agent(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 15
        state.market_metrics = {"cost_pressure": compute_cost_pressure(15, state.resolved_properties())}
        apply_factor_rules(state)

        proposal = StateChange(factor_id="F2", proposed_state="F2.2", reasoning="provider attempt")
        validated = validate_factor_proposals(state, [proposal], agent_id="provider")
        assert validated == []

    def test_validate_accepts_regulator_when_rule_allows(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 15
        state.market_metrics = {"cost_pressure": compute_cost_pressure(15, state.resolved_properties())}
        apply_factor_rules(state)
        state.environment.factors["F2"].current_state = "F2.1"

        proposal = StateChange(factor_id="F2", proposed_state="F2.2", reasoning="regulator aligns")
        validated = validate_factor_proposals(state, [proposal], agent_id="regulator")
        assert len(validated) == 1
        assert validated[0].proposed_state == "F2.2"

    def test_factor_transitions_without_llm_over_30_ticks(self) -> None:
        state = build_initial_state()
        seen_states: set[str] = set()

        for tick in range(1, 31):
            state = _run_deterministic_tick(state, tick)
            seen_states.add(state.environment.factors["F2"].current_state)

        assert "F2.2" in seen_states
        assert len(state.factor_timeseries) == 30

    def test_build_runtime_metrics_uses_prior_booking(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 10
        state.population_stats.append(
            {
                "round_number": 9,
                "total_demand": 0.61,
                "total_booked": 610,
                "total_population": 1000,
                "segments": {},
            }
        )

        metrics = build_runtime_metrics(state)

        assert metrics.prior_booking_rate == 0.61
        assert metrics.booking_rate == 0.61
