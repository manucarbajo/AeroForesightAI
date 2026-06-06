from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config_loader import build_initial_state
from src.protocol_generator import ProtocolOptions, build_protocol_payload
from src.simulation_runner import RunnerOptions, SimulationRunner


class MockLLM:
    def call(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "`consumer`" in prompt_lower or "consumer" in prompt_lower[:200]:
            return """{
  "reasoning": "Consumer reacts to price.",
  "actions": ["Adjust demand"],
  "state_changes": [{"factor_id": "F1", "proposed_state": "F1.2", "reasoning": "test"}],
  "events": [{"event_type": "demand_shift", "description": "Demand shift", "affected_factors": ["F1"]}],
  "segment_analysis": {"leisure": "Sensitive"}
}"""
        if "`provider`" in prompt_lower or "provider" in prompt_lower[:200]:
            return """{
  "reasoning": "Provider adjusts pricing.",
  "actions": ["Update fares"],
  "state_changes": [],
  "events": [{"event_type": "price_change", "description": "Fare update", "affected_factors": ["F1"]}],
  "segment_analysis": {}
}"""
        if "`regulator`" in prompt_lower or "regulator" in prompt_lower[:200]:
            return """{
  "reasoning": "Regulator updates policy.",
  "actions": ["Policy change"],
  "state_changes": [{"factor_id": "F2", "proposed_state": "F2.2", "reasoning": "test"}],
  "events": [],
  "segment_analysis": {}
}"""
        return '{"reasoning": "noop", "actions": [], "state_changes": [], "events": [], "segment_analysis": {}}'


def test_parallel_round_runs_each_agent_once_per_tick():
    state = build_initial_state()
    state.clock.max_ticks = 1

    runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=False))
    final = runner._build_sequential_runner(state.agents)(state)

    tick_one = [rr for rr in final.round_results if rr.round_number == 1]
    agent_ids = [resp.agent_id for rr in tick_one for resp in rr.agent_responses]

    assert len(agent_ids) == 3
    assert set(agent_ids) == {"consumer", "provider", "regulator"}
    assert final.redebedarf_scores == {}


def test_parallel_protocol_has_no_redebedarf_scores():
    state = build_initial_state()
    state.clock.max_ticks = 1

    runner = SimulationRunner(llm=MockLLM(), options=RunnerOptions(enable_market=False))
    final = runner._build_sequential_runner(state.agents)(state)

    payload = build_protocol_payload(final, ProtocolOptions(include_redebedarf=False))
    contributions = payload["rounds"][0]["contributions"]

    assert len(contributions) == 3
    assert all(contrib.get("redebedarf_score") is None for contrib in contributions)


def test_redebedarf_mode_can_include_scores_in_protocol():
    state = build_initial_state()
    state.clock.max_ticks = 1

    runner = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(enable_market=False, enable_redebedarf=True),
    )
    final = runner._build_sequential_runner(state.agents)(state)

    payload = build_protocol_payload(final, ProtocolOptions(include_redebedarf=True))
    contributions = payload["rounds"][0]["contributions"]

    assert len(contributions) >= 3
    assert any(contrib.get("redebedarf_score") is not None for contrib in contributions)
