import tempfile
import unittest
from pathlib import Path

from src.config_loader import build_initial_state
from src.models.agent_models import AgentResponse
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult
from src.output_writer import save_final_narrative


class SaveFinalNarrativeTests(unittest.TestCase):
    def test_includes_all_agent_events_per_tick(self) -> None:
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

        with tempfile.TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir)
            narrative_path = save_final_narrative(state, run_dir=run_dir)
            content = Path(narrative_path).read_text(encoding="utf-8")

        self.assertIn("**provider:** Provider invests in SAF.", content)
        self.assertIn("**regulator:** Regulator launches awareness campaign.", content)
        self.assertIn("**consumer:** Consumer books eco-conscious flights.", content)
        self.assertIn("provider: Airline expands SAF logistics.", content)
        self.assertIn("regulator: Commission launches SAF awareness campaign.", content)
        self.assertIn("consumer: Consumers increase eco-conscious bookings.", content)
        self.assertNotIn("market: Market update", content)
        self.assertIn("**Events (3):**", content)


if __name__ == "__main__":
    unittest.main()
