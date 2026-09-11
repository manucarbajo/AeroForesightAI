from src.agents.agent_node import AgentNode
from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse
from src.models.event_models import RoundResult


class MockLLM:
    def __init__(self, output: str):
        self.output = output
        self.last_prompt: str | None = None

    def call(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.output


def test_parse_valid_json_output() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
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
            """)
    node = AgentNode(config=consumer, llm=llm)

    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.agent_id == "consumer"
    assert response.actions[0] == "Weniger Freizeitfluege buchen"
    assert len(response.state_changes) == 0
    assert updated.event_log[-1].event_type.value == "demand_shift"


def test_extract_json_from_markdown_codeblock() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
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
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.reasoning == "Nachfrage verschiebt sich."
    assert "business" in response.segment_analysis


def test_extract_json_from_freetext_embedded_object() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
            Hier ist das Ergebnis: {"reasoning":"Freitext Test","actions":["X"],"state_changes":[],"events":[], "segment_analysis":{"business":"OK"}} Danke!
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.reasoning == "Freitext Test"
    assert "business" in response.segment_analysis


def test_actions_missing_normalized_to_no_op() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
            {
              "reasoning": "Aktion nicht angegeben",
              "state_changes": [],
              "events": []
            }
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.actions == ["NO_OP"]


def test_parse_segment_analysis() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
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
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]
    assert "business" in response.segment_analysis
    assert "leisure_price_sensitive" in response.segment_analysis


def test_consumer_segment_analysis_unknown_keys_filtered() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    llm = MockLLM("""
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
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert "business" in response.segment_analysis
    assert "unknown_seg" not in response.segment_analysis


def test_provider_segment_analysis_forced_empty() -> None:
    state = build_initial_state()
    provider = next(agent for agent in state.agents if agent.id == "provider")
    llm = MockLLM("""
            {
              "reasoning": "Provider liefert irrtuemlich segment_analysis",
              "actions": ["A"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {
                "business": "Falsch fuer Provider"
              }
            }
            """)
    node = AgentNode(config=provider, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.segment_analysis == {}


def test_consumer_prompt_and_output_segment_analysis() -> None:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")

    llm = MockLLM("""
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
            """)
    node = AgentNode(config=consumer, llm=llm)
    updated = node.invoke(state)

    response = updated.round_results[-1].agent_responses[0]
    assert "business" in response.segment_analysis
    assert "leisure_price_sensitive" in response.segment_analysis

    # Prompt-Kontext: ConsumerPrompt muss PopulationConfig und Marktmetriken (properties.json) enthalten.
    assert llm.last_prompt is not None
    assert "demand_growth_rate" in llm.last_prompt
    assert "segment business" in llm.last_prompt
    assert "price_elasticity" in llm.last_prompt


def test_provider_uses_consumer_segment_analysis_in_prompt() -> None:
    state = build_initial_state()
    provider = next(agent for agent in state.agents if agent.id == "provider")

    # Falscher, aber sinnvoller AP3-ähnlicher Zustand: Consumer hat im gleichen Round segment_analysis erzeugt.
    consumer_response = AgentResponse(
        agent_id="consumer",
        round_number=state.clock.current_tick,
        reasoning="Consumer-Analyse",
        actions=["dummy"],
        state_changes=[],
        segment_analysis={"business": "Geschaeftsreisende reagieren wenig preissensitiv."},
        raw_output="{}",
    )
    state.round_results.append(
        RoundResult(
            round_number=state.clock.current_tick,
            agent_responses=[consumer_response],
            events=[],
            environment_snapshot=state.environment,
            summary="",
        )
    )

    llm = MockLLM("""
            {
              "reasoning": "Provider reagiert auf segmentierte Nachfragereaktion.",
              "actions": ["Preise anpassen"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {}
            }
            """)
    node = AgentNode(config=provider, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    # Output prüfen (Provider soll {} liefern; zumindest parsebar und als dict landen).
    assert isinstance(response.segment_analysis, dict)
    assert response.segment_analysis == {}

    # Prompt-Kontext prüfen: Provider-Prompt muss die Consumer segment_analysis enthalten.
    assert llm.last_prompt is not None
    assert "Geschaeftsreisende reagieren wenig preissensitiv" in llm.last_prompt
    assert "demand_growth_rate" in llm.last_prompt


def test_state_change_validation_filters_unknown_factor_and_invalid_state() -> None:
    state = build_initial_state()
    regulator = next(agent for agent in state.agents if agent.id == "regulator")

    llm = MockLLM("""
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
            """)
    node = AgentNode(config=regulator, llm=llm)
    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert len(response.state_changes) == 1
    assert response.state_changes[0].factor_id == "F2"


def test_event_type_invalid_defaults_by_agent() -> None:
    state = build_initial_state()
    provider = next(agent for agent in state.agents if agent.id == "provider")
    llm = MockLLM("""
            {
              "reasoning": "Events enthalten einen falschen event_type",
              "actions": ["A"],
              "state_changes": [],
              "events": [
                {"event_type":"not_valid","description":"D","affected_factors":["F1"]}
              ],
              "segment_analysis": {}
            }
            """)
    node = AgentNode(config=provider, llm=llm)
    updated = node.invoke(state)
    event = updated.event_log[-1]

    assert event.event_type.value == "price_change"
    assert event.affected_factors == ["F1"]


def test_parse_fallback_on_invalid_json() -> None:
    state = build_initial_state()
    provider = next(agent for agent in state.agents if agent.id == "provider")
    llm = MockLLM("Kein JSON sondern Freitext.")
    node = AgentNode(config=provider, llm=llm)

    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]
    event = updated.event_log[-1]

    assert response.actions == ["NO_OP_PARSE_FALLBACK"]
    assert event.event_type.value == "price_change"


def test_provider_prior_booking_block_in_prompt() -> None:
    state = build_initial_state()
    state.clock.current_tick = 3
    state.population_stats = [
        {
            "round_number": 1,
            "total_demand": 0.52,
            "total_booked": 520,
            "total_population": 1000,
            "segments": {
                "business": {
                    "booking_rate": 0.675,
                    "booked_individuals": 214,
                    "total_individuals": 317,
                }
            },
        },
        {
            "round_number": 2,
            "total_demand": 0.775,
            "total_booked": 775,
            "total_population": 1000,
            "segments": {
                "business": {
                    "booking_rate": 0.899,
                    "booked_individuals": 285,
                    "total_individuals": 317,
                }
            },
        },
    ]
    provider = next(agent for agent in state.agents if agent.id == "provider")
    llm = MockLLM("""
            {
              "reasoning": "Stable demand",
              "actions": ["NO_OP"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {}
            }
            """)
    node = AgentNode(config=provider, llm=llm)
    node.invoke(state)

    assert llm.last_prompt is not None
    assert "prior_tick: 2" in llm.last_prompt
    assert "booking_rate: 0.775" in llm.last_prompt
    assert "booking_rate_delta_vs_prior: +0.255" in llm.last_prompt
    assert "NO_OP" in llm.last_prompt


def test_explicit_no_op_skips_event_fallback() -> None:
    state = build_initial_state()
    provider = next(agent for agent in state.agents if agent.id == "provider")
    events_before = len(state.event_log)
    llm = MockLLM("""
            {
              "reasoning": "Stable demand, no new developments.",
              "actions": ["NO_OP"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {}
            }
            """)
    node = AgentNode(config=provider, llm=llm)
    updated = node.invoke(state)

    assert updated.round_results[-1].agent_responses[0].actions == ["NO_OP"]
    assert len(updated.event_log) == events_before


def test_regulator_prior_booking_block_first_tick() -> None:
    state = build_initial_state()
    state.clock.current_tick = 1
    regulator = next(agent for agent in state.agents if agent.id == "regulator")
    llm = MockLLM("""
            {
              "reasoning": "First tick policy",
              "actions": ["NO_OP"],
              "state_changes": [],
              "events": [],
              "segment_analysis": {}
            }
            """)
    node = AgentNode(config=regulator, llm=llm)
    node.invoke(state)

    assert llm.last_prompt is not None
    assert "No prior booking data (first tick)" in llm.last_prompt
    assert "scheduled_property_changes_this_tick:" in llm.last_prompt
