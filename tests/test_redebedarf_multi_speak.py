from __future__ import annotations

from src.config_loader import build_initial_state, load_agents
from src.models.agent_models import AgentResponse, StateChange
from src.models.event_models import RoundResult, EventLogEntry
from src.nodes.redebedarf_node import RoundExecutionNode
from src.redebedarf_scheduler import RedebedarfScheduler
from src.models.enums import EventType


class DummyAgentNode:
    def __init__(self, agent_id: str, response: AgentResponse | None = None):
        self.agent_id = agent_id
        self.response = response

    def invoke(self, state):
        # append a RoundResult with the configured AgentResponse
        if self.response is None:
            return state

        rr = RoundResult(
            round_number=state.clock.current_tick,
            agent_responses=[self.response],
            events=[EventLogEntry(id=self.agent_id, round_number=state.clock.current_tick, source_agent=self.agent_id, event_type=EventType.DEMAND_SHIFT, description="test", affected_factors=[c.factor_id for c in self.response.state_changes], timestamp="" )],
            environment_snapshot=state.environment,
            summary=f"test {self.agent_id}",
        )
        state.round_results.append(rr)
        state.event_log.extend(rr.events)
        return state


def test_multi_speak_triggers_provider():
    # Prepare state and agents
    state = build_initial_state()
    state.clock.current_tick = 1
    agents = load_agents()
    agent_ids = [a.id for a in agents]

    # Build a scheduler that maps factor 'F1' to 'provider' so that provider gets points
    scheduler = RedebedarfScheduler(agent_ids, factor_relevance_map={"F1": {"provider": 3}})

    # Monkeypatch the classmethod used by the node to return our prepared scheduler
    original_from_state = RedebedarfScheduler.from_simulation_state
    RedebedarfScheduler.from_simulation_state = classmethod(lambda cls, state, apply_score_deltas=True: scheduler)

    try:
        node = RoundExecutionNode(agents, llm=None)

        # Consumer will propose a change affecting F1 -> this should give provider points
        consumer_response = AgentResponse(
            agent_id="consumer",
            round_number=1,
            reasoning="trigger",
            actions=["SPEAK"],
            state_changes=[StateChange(factor_id="F1", proposed_state="F1.2", reasoning="test")],
            raw_output="",
        )
        provider_response = AgentResponse(
            agent_id="provider",
            round_number=1,
            reasoning="reply",
            actions=["SPEAK"],
            state_changes=[],
            raw_output="",
        )

        node._agent_nodes = {
            "consumer": DummyAgentNode("consumer", consumer_response),
            "provider": DummyAgentNode("provider", provider_response),
            "regulator": DummyAgentNode("regulator", None),
        }

        out_state = node.invoke(state)

        # Expect that provider also spoke in same round after consumer triggered F1
        assert "consumer" in out_state.current_speech_order
        assert "provider" in out_state.current_speech_order
        # consumer should precede provider
        assert out_state.current_speech_order.index("consumer") < out_state.current_speech_order.index("provider")
    finally:
        RedebedarfScheduler.from_simulation_state = original_from_state
