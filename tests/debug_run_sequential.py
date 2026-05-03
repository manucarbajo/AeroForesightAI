import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

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

        return "{\n  \"reasoning\": \"noop\",\n  \"actions\": [],\n  \"state_changes\": [],\n  \"events\": [],\n  \"segment_analysis\": {}\n}"


def main():
    state = build_initial_state()
    state.clock.max_rounds = 1
    runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=True))
    run_graph = runner._build_sequential_runner(state.agents)
    final = run_graph(state)

    print("Current round:", final.clock.current_round)
    print("Environment factors:")
    for fid, f in final.environment.factors.items():
        print(f" - {fid}: {f.current_state}")

    print("RoundResults:")
    for rr in final.round_results:
        print(f" Round {rr.round_number} summary={rr.summary}")
        for ar in rr.agent_responses:
            print(f"  AgentResponse: agent_id={ar.agent_id} actions={ar.actions} state_changes={[ (c.factor_id,c.proposed_state) for c in ar.state_changes ]}")


if __name__ == '__main__':
    main()
