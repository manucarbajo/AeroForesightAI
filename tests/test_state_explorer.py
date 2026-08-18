from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.event_deltas import write_events_from_deltas
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.state_explorer import (
    EXPLORER_INSTRUCTIONS,
    StateExplorer,
    build_grounded_context_block,
    load_run_context,
    parse_tick_hint,
)


class _RecordingLLM:
    def __init__(self) -> None:
        self.last_prompt = ""

    def call(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "Antwort aus Mock-LLM."


def _run_deterministic_tick(state, tick: int):
    state.clock.current_tick = tick
    state = EnvironmentNode().invoke(state)
    state = MarketNode().invoke(state)
    from src.factor_dynamics import record_factor_timeseries

    state = record_factor_timeseries(state)
    return write_events_from_deltas(state)


class TestWriteEventsFromDeltas:
    def test_appends_property_and_booking_delta_events(self):
        state = build_initial_state()
        state = _run_deterministic_tick(state, 1)
        events_before = len(state.event_log)

        state = _run_deterministic_tick(state, 2)
        delta_events = [
            event
            for event in state.event_log
            if event.source_agent == "system" and "[delta:" in event.description
        ]
        assert len(state.event_log) > events_before
        assert delta_events

    def test_idempotent_for_same_tick(self):
        state = build_initial_state()
        state = _run_deterministic_tick(state, 1)
        count_after_first = len(state.event_log)
        state = write_events_from_deltas(state)
        assert len(state.event_log) == count_after_first


class TestMarketProviderPriceEvent:
    def test_provider_price_change_event_on_significant_move(self):
        state = build_initial_state()
        state = _run_deterministic_tick(state, 1)
        provider_events = [
            event
            for event in state.event_log
            if event.source_agent == "provider" and "[delta:price]" in event.description
        ]
        assert provider_events
        assert provider_events[0].event_type.value == "price_change"


def _write_sample_run(run_dir: Path, run_id: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    tick_mechanics = {
        "run_id": run_id,
        "reading_guide": "Booking uses prior tick price.",
        "ticks": [
            {
                "tick": 15,
                "booking_rate": 0.62,
                "prior_booking_rate": 0.65,
                "booking_rate_delta": -0.03,
                "market_price_after_feedback_eur": 132.5,
                "carbon_tax_level": 100,
            }
        ],
    }
    event_log = [
        {
            "round_number": 15,
            "source_agent": "system",
            "event_type": "market_event",
            "description": "[delta:property:carbon_tax_level] CO₂ tax 50 → 100 (+50, Python delta)",
        },
        {
            "round_number": 15,
            "source_agent": "provider",
            "event_type": "price_change",
            "description": "[delta:price] Provider yield feedback: ticket price 128.00 → 132.50 (+3.5%)",
        },
    ]
    (run_dir / "tick_mechanics.json").write_text(json.dumps(tick_mechanics), encoding="utf-8")
    (run_dir / "event_log.json").write_text(json.dumps(event_log), encoding="utf-8")
    (run_dir / "price_history.json").write_text(
        json.dumps([{"round_number": 15, "price": 132.5, "demand_level": 0.62}]),
        encoding="utf-8",
    )
    (run_dir / "run_metadata.json").write_text(
        json.dumps({"simulation_name": "Test Run"}),
        encoding="utf-8",
    )
    (run_dir / "run_scenario.json").write_text(
        json.dumps(
            {
                "title": "Lauf-Narrativ",
                "summary": "Faktorbasierter Lauf.",
                "run_narrative": "F1 wechselt im Verlauf.",
                "factor_profile": {
                    "end": [
                        {
                            "factor_id": "F1",
                            "factor_name": "Nachfrage",
                            "state_id": "F1.1",
                            "state_label": "Boom",
                        }
                    ]
                },
                "scenarios": [
                    {
                        "rank": 1,
                        "title": "Fortsetzung: Business as usual",
                        "what_could_happen": "Der Markt bleibt auf vertrautem Pfad.",
                    }
                ],
                "ground_truth": {"booking_rate_end": 0.62},
            }
        ),
        encoding="utf-8",
    )


class TestStateExplorer:
    def test_parse_tick_hint(self):
        assert parse_tick_hint("Was passierte bei Tick 15?") == 15
        assert parse_tick_hint("Verlauf über alle ticks") is None

    def test_load_run_context(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="explorer_test_"))
        try:
            run_id = "run_test_explorer"
            _write_sample_run(tmpdir / run_id, run_id)
            context = load_run_context(run_id, focus_tick=15, outputs_root=tmpdir)
            assert context.run_id == run_id
            assert context.focus_tick == 15
            assert len(context.tick_mechanics["ticks"]) == 1
        finally:
            shutil.rmtree(tmpdir)

    def test_load_factors_from_csv(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="explorer_factors_"))
        try:
            run_id = "run_factors_csv"
            run_dir = tmpdir / run_id
            _write_sample_run(run_dir, run_id)
            ts_dir = run_dir / "timeseries"
            ts_dir.mkdir(parents=True, exist_ok=True)
            (ts_dir / "factors.csv").write_text(
                "tick,F1,F2\n15,F1.1,F2.2\n",
                encoding="utf-8",
            )
            context = load_run_context(run_id, focus_tick=15, outputs_root=tmpdir)
            assert len(context.factors_timeseries) == 1
            assert context.factors_timeseries[0]["F2"] == "F2.2"
            block = build_grounded_context_block(context)
            assert "factors_timeseries" in block
            assert "F2.2" in block
        finally:
            shutil.rmtree(tmpdir)

    def test_grounded_context_contains_tick_and_delta_events(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="explorer_ctx_"))
        try:
            run_id = "run_test_explorer"
            _write_sample_run(tmpdir / run_id, run_id)
            context = load_run_context(run_id, focus_tick=15, outputs_root=tmpdir)
            block = build_grounded_context_block(context)
            assert "tick_mechanics" in block
            assert "booking_rate" in block
            assert "[delta:property:carbon_tax_level]" in block
            assert "[delta:price]" in block
        finally:
            shutil.rmtree(tmpdir)

    def test_explorer_prompt_is_grounded(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="explorer_prompt_"))
        try:
            run_id = "run_test_explorer"
            _write_sample_run(tmpdir / run_id, run_id)
            context = load_run_context(run_id, focus_tick=15, outputs_root=tmpdir)
            llm = _RecordingLLM()
            explorer = StateExplorer(context, llm=llm)
            explorer.ask("Warum fiel booking bei Tick 15?")

            assert EXPLORER_INSTRUCTIONS in llm.last_prompt
            assert "Never invent numbers" in llm.last_prompt
            assert "booking_rate" in llm.last_prompt
            assert "132.5" in llm.last_prompt
        finally:
            shutil.rmtree(tmpdir)

    def test_grounded_context_contains_run_scenario(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="explorer_scenario_"))
        try:
            run_id = "run_test_explorer"
            _write_sample_run(tmpdir / run_id, run_id)
            context = load_run_context(run_id, outputs_root=tmpdir)
            assert context.run_scenario is not None
            block = build_grounded_context_block(context)
            assert "run_scenario" in block
            assert "F1" in block
        finally:
            shutil.rmtree(tmpdir)

    def test_missing_run_raises(self):
        with pytest.raises(FileNotFoundError):
            load_run_context("run_does_not_exist_12345", outputs_root=tempfile.gettempdir())
