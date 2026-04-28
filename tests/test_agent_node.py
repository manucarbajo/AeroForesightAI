import unittest

from src.config_loader import build_initial_state
from src.nodes.agent_node import AgentNode

#Test generated with Gemini 3.2
class MockLLM:
    def __init__(self, output: str):
        self.output = output

    def call(self, prompt: str) -> str:
        return self.output


class AgentNodeTests(unittest.TestCase):
    def test_parse_valid_json_output(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            {
              "reasoning": "Nachfrage sinkt durch hohe Preise.",
              "actions": ["Weniger Freizeitfluege buchen"],
              "state_changes": [
                {"factor_id": "F1", "proposed_state": "F1.2", "reasoning": "Substitution steigt."}
              ],
              "events": [
                {
                  "event_type": "demand_shift",
                  "description": "Freizeitsegment reduziert Flugnachfrage.",
                  "affected_factors": ["F1", "F5"]
                }
              ]
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)

        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertEqual(response.agent_id, "consumer")
        self.assertEqual(response.actions[0], "Weniger Freizeitfluege buchen")
        self.assertEqual(len(response.state_changes), 1)
        self.assertEqual(updated.event_log[-1].event_type.value, "demand_shift")

    def test_parse_fallback_on_invalid_json(self) -> None:
        state = build_initial_state()
        provider = next(agent for agent in state.agents if agent.id == "provider")
        llm = MockLLM("Kein JSON sondern Freitext.")
        node = AgentNode(config=provider, llm=llm)

        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]
        event = updated.event_log[-1]

        self.assertEqual(response.actions, ["NO_OP_PARSE_FALLBACK"])
        self.assertEqual(event.event_type.value, "price_change")


if __name__ == "__main__":
    unittest.main()
