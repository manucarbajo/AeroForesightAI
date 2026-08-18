import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import unittest

from src.config_loader import build_initial_state
from src.simulation_runner import RunnerOptions, SimulationRunner


class MockLLM:
    def call(self, prompt: str) -> str:
        p = prompt.lower()
        if "`consumer`" in p:
            return """{
  "reasoning": "Consumer reduces demand in price-sensitive segments.",
  "actions": ["Reduce bookings"],
  "state_changes": [
    {"factor_id": "F1", "proposed_state": "F1.2", "reasoning": "Substitution & lower demand"}
  ],
  "events": [
    {"event_type": "demand_shift", "description": "Leisure segments reduce flights.", "affected_factors": ["F1"]}
  ],
  "segment_analysis": {"business": "Stable demand", "leisure_price_sensitive": "Strong reduction"}
}"""
        if "`provider`" in p:
            return """{
  "reasoning": "Provider increases price by 10% due to costs.",
  "actions": ["Raise prices"],
  "state_changes": [],
  "events": [
    {"event_type": "price_change", "description": "Price increase by 10%", "affected_factors": ["F1"]}
  ],
  "segment_analysis": {}
}"""
        if "`regulator`" in p:
            return """{
  "reasoning": "Regulator tightens policy",
  "actions": ["Implement stricter CO2 rules"],
  "state_changes": [
    {"factor_id": "F2", "proposed_state": "F2.2", "reasoning": "Policy shift towards decarbonisation"}
  ],
  "events": [],
  "segment_analysis": {}
}"""

        return '{\n  "reasoning": "noop",\n  "actions": [],\n  "state_changes": [],\n  "events": [],\n  "segment_analysis": {}\n}'


class SimulationRunnerE2ETest(unittest.TestCase):
    def test_run_with_mock_agents_blocks_ungated_llm_factor_changes(self) -> None:
        state = build_initial_state()
        state.clock.max_ticks = 1

        runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=True))
        run_graph = runner._build_sequential_runner(state.agents)
        final = run_graph(state)

        self.assertEqual(final.clock.current_tick, 1)
        self.assertEqual(final.environment.factors["F1"].current_state, "F1.1")
        self.assertEqual(final.environment.factors["F2"].current_state, "F2.1")
        self.assertEqual(len(final.factor_timeseries), 1)

        rounds = [rr for rr in final.round_results if rr.round_number == 1]
        self.assertTrue(len(rounds) >= 1)
        self.assertTrue(len(final.price_history) >= 1)

    def test_factor_rules_apply_at_carbon_shock_tick(self) -> None:
        state = build_initial_state()
        state.clock.max_ticks = 15

        runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=True))
        run_graph = runner._build_sequential_runner(state.agents)
        final = run_graph(state)

        self.assertEqual(final.clock.current_tick, 15)
        self.assertEqual(final.environment.factors["F2"].current_state, "F2.2")
        self.assertEqual(final.environment.factors["F6"].current_state, "F6.2")
        self.assertEqual(len(final.factor_timeseries), 15)


if __name__ == "__main__":
    unittest.main()
