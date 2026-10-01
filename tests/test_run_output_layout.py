import re
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

    assert "## Geplante Änderungen der Systemgrößen" in content
    assert "Tick 8" in content
    assert "saf_mandate_share" in content
    assert "Leseschlüssel" in content
    assert "gebucht (" in content


def test_der_bericht_nennt_nur_den_lauf_und_spricht_deutsch(tmp_path):
    """Befund 13 der Abnahme vom 2026-09-30: Der Bericht eines 40-Tick-Laufs
    listete Stützpunkte bis Tick 120, jeden mit der vollen Beschreibung aus
    `properties.json` samt Paketkennungen, dazu «Python-Ground-Truth» und
    «set →» / «step_function →»."""

    state = build_initial_state()
    state.config.seed = 1
    state.clock.max_ticks = 8
    state.clock.current_tick = 1
    state = MarketNode().invoke(state)

    run_dir = tmp_path / "run_test"
    run_dir.mkdir()
    content = Path(save_final_narrative(state, run_dir=run_dir)).read_text(encoding="utf-8")
    plan = content.split("## Geplante Änderungen der Systemgrößen", 1)[1].split("\n\n", 1)[0]

    ticks = [int(t) for t in re.findall(r"\*\*Tick (\d+):\*\*", plan)]
    assert ticks and max(ticks) <= 8, ticks
    for wort in ("Python-Ground-Truth", "set →", "step_function →", "(P3.8", "LLM-Begründung"):
        assert wort not in content, wort
