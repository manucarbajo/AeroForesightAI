from __future__ import annotations

from src.config_loader import build_initial_state
from src.market.factor_dynamics import (
    apply_factor_rules,
    apply_factor_rules_at_tick_start,
    build_runtime_metrics,
    record_factor_timeseries,
    validate_factor_proposals,
)
from src.market.market_node import MarketNode
from src.market.simulation_functions import compute_cost_pressure
from src.models.agent_models import StateChange
from src.nodes.environment_node import EnvironmentNode


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
        state.market_metrics = {
            "cost_pressure": compute_cost_pressure(15, state.resolved_properties())
        }

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
        state.market_metrics = {
            "cost_pressure": compute_cost_pressure(15, state.resolved_properties())
        }
        apply_factor_rules(state)

        proposal = StateChange(factor_id="F2", proposed_state="F2.2", reasoning="provider attempt")
        validated = validate_factor_proposals(state, [proposal], agent_id="provider")
        assert validated == []

    def test_validate_accepts_regulator_when_rule_allows(self) -> None:
        state = build_initial_state()
        state.clock.current_tick = 15
        state.market_metrics = {
            "cost_pressure": compute_cost_pressure(15, state.resolved_properties())
        }
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


# ---------------------------------------------------------------------------
# P2.4 — Neue CIB-gestützte Factor-Rules: F4→F1, F5→F1, F3→F6
# ---------------------------------------------------------------------------


class TestNewFactorRules:
    def test_recession_f4_drives_f1_to_stagnation(self) -> None:
        """P2.4: F4.2 (recession) should trigger F1 → F1.2 via f1_recession_demand_drop."""
        state = build_initial_state()
        state.clock.current_tick = 5
        state.environment.factors["F4"].current_state = "F4.2"
        state.environment.factors["F1"].current_state = "F1.1"
        state.market_metrics = {"cost_pressure": 100.0, "booking_rate": 0.55}

        applications = apply_factor_rules(state)
        applied_ids = {item.rule_id for item in applications}

        assert (
            state.environment.factors["F1"].current_state == "F1.2"
        ), "F4.2 (recession) should push F1 to F1.2 (demand stagnation)"
        assert "f1_recession_demand_drop" in applied_ids

    def test_strong_alternatives_f5_drives_f1_to_substitution(self) -> None:
        """P2.4: F5.2 (strong alternatives) should trigger F1 → F1.2."""
        state = build_initial_state()
        state.clock.current_tick = 5
        state.environment.factors["F5"].current_state = "F5.2"
        state.environment.factors["F1"].current_state = "F1.1"
        # Make sure F4 is NOT F4.2 so f1_recession_demand_drop doesn't fire simultaneously
        state.environment.factors["F4"].current_state = "F4.1"
        state.market_metrics = {"cost_pressure": 100.0, "booking_rate": 0.60}

        applications = apply_factor_rules(state)
        applied_ids = {item.rule_id for item in applications}

        assert state.environment.factors["F1"].current_state == "F1.2"
        assert "f1_alternatives_substitution" in applied_ids

    def test_saf_breakthrough_f3_drives_f6_to_accepted(self) -> None:
        """P2.4: F3.2 (SAF breakthrough) should trigger F6 → F6.1 (flying accepted)."""
        state = build_initial_state()
        state.clock.current_tick = 5
        state.environment.factors["F3"].current_state = "F3.2"
        state.environment.factors["F6"].current_state = "F6.2"
        # carbon_tax must be < 60 so f6_accepted_flying can fire, and < 80 so f6_flight_shaming doesn't override
        state.market_metrics = {"cost_pressure": 100.0, "booking_rate": 0.60}
        # Override carbon_tax property to below 60 so high-priority rules don't override
        for prop in state.properties.system_properties:
            if prop.id == "carbon_tax_level":
                from src.models.property_models import BaselineTrajectory

                prop.trajectory = BaselineTrajectory(baseline=50.0, rules=[])
                break

        applications = apply_factor_rules(state)
        applied_ids = {item.rule_id for item in applications}

        assert (
            state.environment.factors["F6"].current_state == "F6.1"
        ), "F3.2 (SAF breakthrough) should signal F6 = F6.1 (flying accepted)"
        assert (
            "f6_tech_breakthrough_acceptance" in applied_ids or "f6_accepted_flying" in applied_ids
        )  # either rule may fire
