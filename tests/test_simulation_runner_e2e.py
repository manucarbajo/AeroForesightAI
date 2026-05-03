import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import unittest

from src.config_loader import build_initial_state
from src.simulation_runner import SimulationRunner, RunnerOptions


class MockLLM:
    def call(self, prompt: str) -> str:
        p = prompt.lower()
        if "`consumer`" in p:
            return '''{
  "reasoning": "Consumer reduces demand in price-sensitive segments.",
  "actions": ["Reduce bookings"],
  "state_changes": [
    {"factor_id": "F1", "proposed_state": "F1.2", "reasoning": "Substitution & lower demand"}
  ],
  "events": [
    {"event_type": "demand_shift", "description": "Leisure segments reduce flights.", "affected_factors": ["F1"]}
  ],
  "segment_analysis": {"business": "Stable demand", "leisure_price_sensitive": "Strong reduction"}
}'''
        if "`provider`" in p:
            return '''{
  "reasoning": "Provider increases price by 10% due to costs.",
  "actions": ["Raise prices"],
  "state_changes": [],
  "events": [
    {"event_type": "price_change", "description": "Price increase by 10%", "affected_factors": ["F1"]}
  ],
  "segment_analysis": {}
}'''
        if "`regulator`" in p:
            return '''{
  "reasoning": "Regulator tightens policy",
  "actions": ["Implement stricter CO2 rules"],
  "state_changes": [
    {"factor_id": "F2", "proposed_state": "F2.2", "reasoning": "Policy shift towards decarbonisation"}
  ],
  "events": [],
  "segment_analysis": {}
}'''

        # default fallback
        return "{\n  \"reasoning\": \"noop\",\n  \"actions\": [],\n  \"state_changes\": [],\n  \"events\": [],\n  \"segment_analysis\": {}\n}"


class SimulationRunnerE2ETest(unittest.TestCase):
    def test_run_with_mock_agents_applies_factor_updates_and_runs(self) -> None:
        state = build_initial_state()
        # keep the run short for tests
        state.clock.max_rounds = 1

        runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=True))

        # Use the deterministic sequential runner to avoid external langgraph differences
        run_graph = runner._build_sequential_runner(state.agents)
        final = run_graph(state)

        # Clock should have advanced to 1 (one round)
        self.assertEqual(final.clock.current_round, 1)

        # Environment factors: F1 should have been proposed by consumer and applied,
        # F2 proposed by regulator and should be applied (regulator has priority)
        self.assertIn("F1", final.environment.factors)
        self.assertIn("F2", final.environment.factors)
        self.assertEqual(final.environment.factors["F1"].current_state, "F1.2")
        self.assertEqual(final.environment.factors["F2"].current_state, "F2.2")

        # RoundResults should contain at least one RoundResult for the round
        rounds = [rr for rr in final.round_results if rr.round_number == 1]
        self.assertTrue(len(rounds) >= 1)

        # Price history should have an entry because market is enabled
        self.assertTrue(len(final.price_history) >= 1)


if __name__ == "__main__":
    unittest.main()
