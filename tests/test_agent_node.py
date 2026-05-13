import unittest

from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse
from src.nodes.agent_node import AgentNode
from src.models.event_models import RoundResult

class MockLLM:
    def __init__(self, output: str):
        self.output = output
        self.last_prompt: str | None = None

    def call(self, prompt: str) -> str:
        self.last_prompt = prompt
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

    def test_extract_json_from_markdown_codeblock(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            ```json
            {
              "reasoning": "Nachfrage verschiebt sich.",
              "actions": ["Buchen"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "business": "Geschaeftsreisende reagieren weniger preissensitiv."
              }
            }
            ```
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertEqual(response.reasoning, "Nachfrage verschiebt sich.")
        self.assertIn("business", response.segment_analysis)

    def test_extract_json_from_freetext_embedded_object(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            Hier ist das Ergebnis: {"reasoning":"Freitext Test","actions":["X"],"state_changes":[],"events":[], "segment_analysis":{"business":"OK"}} Danke!
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertEqual(response.reasoning, "Freitext Test")
        self.assertIn("business", response.segment_analysis)

    def test_actions_missing_normalized_to_no_op(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            {
              "reasoning": "Aktion nicht angegeben",
              "state_changes": [],
              "events": []
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertEqual(response.actions, ["NO_OP"])

    def test_parse_segment_analysis(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            {
              "reasoning": "Unterschiedliche Preissensitivitaet verschiebt Nachfrage je Segment.",
              "actions": ["Segmentiert buchen"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "business": "Geschaeftsreisende reagieren wenig preissensitiv.",
                "leisure_price_sensitive": "Preiserhoehungen fuehren zu Verzicht/Umstieg."
              }
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]
        self.assertIn("business", response.segment_analysis)
        self.assertIn("leisure_price_sensitive", response.segment_analysis)

    def test_consumer_segment_analysis_unknown_keys_filtered(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")
        llm = MockLLM(
            """
            {
              "reasoning": "Analyse mit unbekanntem Segment",
              "actions": ["X"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "unknown_seg": "Sollte rausgefiltert werden",
                "business": "OK"
              }
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertIn("business", response.segment_analysis)
        self.assertNotIn("unknown_seg", response.segment_analysis)

    def test_provider_segment_analysis_forced_empty(self) -> None:
        state = build_initial_state()
        provider = next(agent for agent in state.agents if agent.id == "provider")
        llm = MockLLM(
            """
            {
              "reasoning": "Provider liefert irrtuemlich segment_analysis",
              "actions": ["A"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "business": "Falsch fuer Provider"
              }
            }
            """
        )
        node = AgentNode(config=provider, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        self.assertEqual(response.segment_analysis, {})

    def test_consumer_prompt_and_output_segment_analysis(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")

        llm = MockLLM(
            """
            {
              "reasoning": "Unterschiedliche Segmente reagieren verschieden auf Preis aenderungen.",
              "actions": ["Segmentiert buchen"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "business": "Geringere Preissensitivitaet.",
                "leisure_price_sensitive": "Starke Preissensitivitaet."
              }
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)

        response = updated.round_results[-1].agent_responses[0]
        self.assertIn("business", response.segment_analysis)
        self.assertIn("leisure_price_sensitive", response.segment_analysis)

        # Prompt-Kontext (ohne AP3): ConsumerPrompt muss PopulationConfig und Szenarioparameter enthalten.
        self.assertIsNotNone(llm.last_prompt)
        self.assertIn("demand_growth_rate", llm.last_prompt)
        self.assertIn("segment business", llm.last_prompt)
        self.assertIn("price_elasticity", llm.last_prompt)

    def test_provider_uses_consumer_segment_analysis_in_prompt(self) -> None:
        state = build_initial_state()
        provider = next(agent for agent in state.agents if agent.id == "provider")

        # Falscher, aber sinnvoller AP3-ähnlicher Zustand: Consumer hat im gleichen Round segment_analysis erzeugt.
        consumer_response = AgentResponse(
            agent_id="consumer",
            round_number=state.clock.current_round,
            reasoning="Consumer-Analyse",
            actions=["dummy"],
            state_changes=[],
            segment_analysis={"business": "Geschaeftsreisende reagieren wenig preissensitiv."},
            raw_output="{}",
        )
        state.round_results.append(
            RoundResult(
                round_number=state.clock.current_round,
                agent_responses=[consumer_response],
                events=[],
                environment_snapshot=state.environment,
                summary="",
            )
        )

        llm = MockLLM(
            """
            {
              "reasoning": "Provider reagiert auf segmentierte Nachfragereaktion.",
              "actions": ["Preise anpassen"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {}
            }
            """
        )
        node = AgentNode(config=provider, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]

        # Output prüfen (Provider soll {} liefern; zumindest parsebar und als dict landen).
        self.assertIsInstance(response.segment_analysis, dict)
        self.assertEqual(response.segment_analysis, {})

        # Prompt-Kontext prüfen: Provider-Prompt muss die Consumer segment_analysis enthalten.
        self.assertIsNotNone(llm.last_prompt)
        self.assertIn("Geschaeftsreisende reagieren wenig preissensitiv", llm.last_prompt)
        self.assertIn("demand_growth_rate", llm.last_prompt)

    def test_state_change_validation_filters_unknown_factor_and_invalid_state(self) -> None:
        state = build_initial_state()
        consumer = next(agent for agent in state.agents if agent.id == "consumer")

        # Nur der letzte StateChange ist valide (F2.2 existiert in configs/factors.json).
        llm = MockLLM(
            """
            {
              "reasoning": "Gemischte state_changes",
              "actions": ["X"],
              "state_changes": [
                {"factor_id":"F999","proposed_state":"F999.1","reasoning":"unbekannt"},
                {"factor_id":"F1","proposed_state":"F1.999","reasoning":"unbekannter ProposedState"},
                {"factor_id":"F2","proposed_state":"F2.2","reasoning":"ok"}
              ],
              "events": []
            }
            """
        )
        node = AgentNode(config=consumer, llm=llm)
        updated = node.invoke(state)
        response = updated.round_results[-1].agent_responses[0]
        event = updated.event_log[-1]

        self.assertEqual(len(response.state_changes), 1)
        self.assertEqual(response.state_changes[0].factor_id, "F2")
        self.assertEqual(event.event_type.value, "demand_shift")
        self.assertEqual(event.affected_factors, ["F2"])

    def test_event_type_invalid_defaults_by_agent(self) -> None:
        state = build_initial_state()
        provider = next(agent for agent in state.agents if agent.id == "provider")
        llm = MockLLM(
            """
            {
              "reasoning": "Events enthalten einen falschen event_type",
              "actions": ["A"],
              "state_changes": [],
              "events": [
                {"event_type":"not_valid","description":"D","affected_factors":["F1"]}
              ],
              "segment_analysis": {}
            }
            """
        )
        node = AgentNode(config=provider, llm=llm)
        updated = node.invoke(state)
        event = updated.event_log[-1]

        self.assertEqual(event.event_type.value, "price_change")
        self.assertEqual(event.affected_factors, ["F1"])

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
