from pathlib import Path

from src.config_loader import build_initial_state
from src.market.market_node import MarketNode
from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.orchestration.environment_node import EnvironmentNode
from src.reporting.output_writer import (
    OUTPUT_DIR,
    create_run_id,
    resolve_run_output_dir,
    save_event_log,
    save_final_narrative,
)


def test_create_run_id_format():
    run_id = create_run_id()
    assert run_id.startswith("run_")
    assert len(run_id) > len("run_")


def test_resolve_run_output_dir_creates_subdirectory():
    run_id = create_run_id("test")
    run_dir = resolve_run_output_dir(run_id)
    assert run_dir.is_dir()
    assert run_dir.parent == Path(OUTPUT_DIR)
    assert run_dir.name == run_id


def test_save_event_log_writes_into_run_dir():
    run_id = create_run_id("test")
    run_dir = resolve_run_output_dir(run_id)
    events = [
        EventLogEntry(
            id="evt_001",
            round_number=1,
            source_agent="consumer",
            event_type=EventType.DEMAND_SHIFT,
            description="Test event",
            affected_factors=["F1"],
        )
    ]
    path = save_event_log(events, run_dir=run_dir)
    assert Path(path).parent == run_dir
    assert Path(path).exists()


def test_final_narrative_includes_property_schedule(tmp_path):
    state = build_initial_state()
    state.config.seed = 1
    for tick in range(1, 9):
        state.clock.current_tick = tick
        state = MarketNode().invoke(state)
        state = EnvironmentNode().invoke(state)

    run_dir = tmp_path / "run_test"
    run_dir.mkdir()
    path = save_final_narrative(state, run_dir=run_dir)
    content = Path(path).read_text(encoding="utf-8")

    assert "## Property-Zeitplan (Config)" in content
    assert "Tick 8" in content
    assert "saf_mandate_share" in content
    assert "Leseschlüssel" in content
    assert "gebucht (" in content
