from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from src.config_loader import build_initial_state
from src.orchestration.checkpoint_manager import CheckpointManager
from src.orchestration.environment_node import EnvironmentNode


def test_checkpoint_save_and_load_round_boundary():
    state = build_initial_state()
    state.clock.current_tick = 2
    state.clock.max_ticks = 3

    tmpdir = Path(tempfile.mkdtemp(prefix="cp_test_"))
    try:
        manager = CheckpointManager(checkpoint_dir=tmpdir)
        path = manager.save(state, run_id="run-test", round_number=state.clock.current_tick)
        assert path.name == "tick_0002.json"
        assert path.exists()

        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "clock" not in payload["state"]["config"]
        assert payload["state"]["clock"]["current_tick"] == 2
        assert payload["state"]["clock"]["max_ticks"] == 3
        assert payload["metadata"]["tick_number"] == 2

        loaded = manager.load(path)
        assert loaded.clock.current_tick == state.clock.current_tick
        assert loaded.clock.max_ticks == 3
        # basic fields preserved
        assert loaded.config.name == state.config.name
    finally:
        shutil.rmtree(tmpdir)


def test_checkpoint_serializes_population_individuals():
    state = build_initial_state()
    state.clock.current_tick = 1
    state.config.seed = 42
    state = EnvironmentNode().invoke(state)

    assert len(state.population_individuals) > 0

    tmpdir = Path(tempfile.mkdtemp(prefix="cp_pop_test_"))
    try:
        manager = CheckpointManager(checkpoint_dir=tmpdir)
        path = manager.save(state, run_id="run-pop", round_number=1)
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert len(payload["state"]["population_individuals"]) == len(state.population_individuals)
        assert isinstance(payload["state"]["population_individuals"][0]["booked"], bool)
    finally:
        shutil.rmtree(tmpdir)
