from pathlib import Path

import pytest

from src.output_writer import OUTPUT_DIR, create_run_id, resolve_run_output_dir, save_event_log
from src.models.event_models import EventLogEntry
from src.models.enums import EventType


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
