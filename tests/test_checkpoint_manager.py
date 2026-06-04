from __future__ import annotations

import json
import tempfile
import shutil
from pathlib import Path

from src.checkpoint_manager import CheckpointManager
from src.config_loader import build_initial_state


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
