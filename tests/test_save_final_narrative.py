import json
from pathlib import Path

from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult
from src.reporting.output_writer import save_final_narrative, save_tick_mechanics


def test_includes_all_agent_events_per_tick(tmp_path) -> None:
    state = build_initial_state()
    state.clock.current_tick = 1
    state.price_history.append(
        PriceHistoryEntry(
            round_number=1,
            agent_id="market",
            price=100.0,
            demand_level=0.9,
            load_factor=0.0,
            booking_rate=0.52,
        )
    )

    provider_response = AgentResponse(
        agent_id="provider",
        round_number=1,
        reasoning="Provider invests in SAF.",
        actions=["invest_in_SAF"],
        state_changes=[],
        raw_output="{}",
    )
    regulator_response = AgentResponse(
        agent_id="regulator",
        round_number=1,
        reasoning="Regulator launches awareness campaign.",
        actions=["campaign"],
        state_changes=[],
        raw_output="{}",
    )
    consumer_response = AgentResponse(
        agent_id="consumer",
        round_number=1,
        reasoning="Consumer books eco-conscious flights.",
        actions=["book"],
        state_changes=[],
        raw_output="{}",
    )

    state.round_results.extend(
        [
            RoundResult(
                round_number=1,
                agent_responses=[provider_response],
                events=[],
                environment_snapshot=state.environment,
                summary="provider",
            ),
            RoundResult(
                round_number=1,
                agent_responses=[regulator_response],
                events=[],
                environment_snapshot=state.environment,
                summary="regulator",
            ),
            RoundResult(
                round_number=1,
                agent_responses=[consumer_response],
                events=[],
                environment_snapshot=state.environment,
                summary="consumer",
            ),
        ]
    )
    state.population_stats = [
        {
            "round_number": 1,
            "total_demand": 0.52,
            "total_booked": 520,
            "total_population": 1000,
            "segments": {
                "business": {
                    "booked_individuals": 220,
                    "total_individuals": 300,
                    "booking_rate": 0.733,
                    "share": 0.3,
                },
                "leisure_price_sensitive": {
                    "booked_individuals": 200,
                    "total_individuals": 500,
                    "booking_rate": 0.4,
                    "share": 0.5,
                },
            },
        }
    ]
    state.event_log.extend(
        [
            EventLogEntry(
                id="evt-provider",
                round_number=1,
                source_agent="provider",
                event_type=EventType.PRICE_CHANGE,
                description="Airline expands SAF logistics.",
                affected_factors=["F3"],
                timestamp="",
            ),
            EventLogEntry(
                id="evt-regulator",
                round_number=1,
                source_agent="regulator",
                event_type=EventType.POLICY_CHANGE,
                description="Commission launches SAF awareness campaign.",
                affected_factors=["F2"],
                timestamp="",
            ),
            EventLogEntry(
                id="evt-consumer",
                round_number=1,
                source_agent="consumer",
                event_type=EventType.DEMAND_SHIFT,
                description="Consumers increase eco-conscious bookings.",
                affected_factors=["F6"],
                timestamp="",
            ),
            EventLogEntry(
                id="evt-market",
                round_number=1,
                source_agent="market",
                event_type=EventType.MARKET_EVENT,
                description="Market update (M4): price=100.00",
                affected_factors=[],
                timestamp="",
            ),
        ]
    )

    run_dir = tmp_path
    narrative_path = save_final_narrative(state, run_dir=run_dir)
    content = Path(narrative_path).read_text(encoding="utf-8")

    # Agent reasoning is rendered as a blockquote under the reasoning block (P3.6)
    assert "> Provider invests in SAF." in content
    assert "> Regulator launches awareness campaign." in content
    assert "> Consumer books eco-conscious flights." in content
    # Public events are rendered as a bullet list with a role tag
    assert "**Provider:** Airline expands SAF logistics." in content
    assert "**Regulator:** Commission launches SAF awareness campaign." in content
    assert "**Consumer:** Consumers increase eco-conscious bookings." in content
    assert "market: Market update" not in content
    assert "Leseschlüssel" in content
    assert "#### Wer bucht" in content
    assert "#### Begründungen der Akteure" in content
    assert "#### Meldungen" in content
    assert "220 von 300 gebucht" in content


def test_tick_mechanics_json_structure(tmp_path) -> None:
    state = build_initial_state()
    state.clock.current_tick = 1
    state.price_history.append(
        PriceHistoryEntry(
            round_number=1,
            agent_id="market",
            price=100.0,
            demand_level=0.9,
            load_factor=0.0,
            booking_rate=0.52,
        )
    )
    state.property_timeseries.append(
        {
            "tick": 1,
            "ticket_price": 100.0,
            "ticket_price_pre_feedback": 99.0,
            "carbon_tax_level": 50.0,
            "income_index": 1.0,
            "cost_pressure": 110.0,
        }
    )
    state.population_stats.append(
        {
            "round_number": 1,
            "total_demand": 0.52,
            "total_booked": 520,
            "total_population": 1000,
            "segments": {},
        }
    )

    run_dir = tmp_path
    mechanics_path = save_tick_mechanics(state, run_dir=run_dir)
    payload = json.loads(Path(mechanics_path).read_text(encoding="utf-8"))

    assert "reading_guide" in payload
    assert len(payload["ticks"]) == 1
    assert payload["ticks"][0]["booking_reference_price_eur"] == 99.0
