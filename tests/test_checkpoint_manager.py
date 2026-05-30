from __future__ import annotations

import tempfile
import shutil
from pathlib import Path

from src.checkpoint_manager import CheckpointManager
from src.config_loader import build_initial_state


def test_checkpoint_save_and_load_round_boundary():
    state = build_initial_state()
    state.clock.current_round = 2

    tmpdir = Path(tempfile.mkdtemp(prefix="cp_test_"))
    try:
        manager = CheckpointManager(checkpoint_dir=tmpdir)
        path = manager.save(state, run_id="run-test", round_number=state.clock.current_round)
        assert path.exists()

        loaded = manager.load(path)
        assert loaded.clock.current_round == state.clock.current_round
        # basic fields preserved
        assert loaded.config.name == state.config.name
    finally:
        shutil.rmtree(tmpdir)
