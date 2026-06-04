"""Checkpoint persistence for AP3.

The checkpoint layer stores the full simulation state after each completed round.
It does not persist agent memory. A resumed run continues from the serialized
state at exactly the same round boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.models.state_models import SimulationState


@dataclass(frozen=True)
class CheckpointMetadata:
    """Lightweight metadata stored alongside each checkpoint."""

    run_id: str
    tick_number: int
    saved_at: str
    checkpoint_version: int = 2


class CheckpointManager:
    """Persist and restore simulation states for AP3 resume support."""

    def __init__(self, checkpoint_dir: Path | str | None = None) -> None:
        self.checkpoint_dir = Path(checkpoint_dir or Path("outputs") / "checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.last_saved_path: Path | None = None

    def save(self, state: SimulationState, *, run_id: str, round_number: int) -> Path:
        """Save a checkpoint after a completed tick and return the file path."""

        run_dir = self.checkpoint_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        tick_number = round_number
        checkpoint_path = run_dir / f"tick_{tick_number:04d}.json"
        payload = {
            "metadata": CheckpointMetadata(
                run_id=run_id,
                tick_number=tick_number,
                saved_at=datetime.now(UTC).isoformat(),
            ).__dict__,
            "state": state.model_dump(mode="json"),
        }

        tmp_path = checkpoint_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_path.replace(checkpoint_path)

        self.last_saved_path = checkpoint_path
        return checkpoint_path

    def load(self, reference: str | Path) -> SimulationState:
        """Load a checkpoint from a file path or from the latest checkpoint of a run."""

        checkpoint_path = self._resolve_reference(reference)
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        state_data: dict[str, Any] = payload["state"]
        return SimulationState.model_validate(state_data)

    def latest_checkpoint(self, run_id: str) -> Path | None:
        """Return the most recent checkpoint file for a given run id."""

        run_dir = self.checkpoint_dir / run_id
        if not run_dir.exists():
            return None

        checkpoints = sorted(run_dir.glob("tick_*.json"))
        if not checkpoints:
            checkpoints = sorted(run_dir.glob("round_*.json"))
        return checkpoints[-1] if checkpoints else None

    def list_checkpoints(self, run_id: str) -> list[Path]:
        """Return all checkpoint files for a given run id in chronological order."""

        run_dir = self.checkpoint_dir / run_id
        if not run_dir.exists():
            return []

        checkpoints = sorted(run_dir.glob("tick_*.json"))
        if checkpoints:
            return checkpoints
        return sorted(run_dir.glob("round_*.json"))

    def _resolve_reference(self, reference: str | Path) -> Path:
        """Resolve a checkpoint reference to an existing file path."""

        path = Path(reference)
        if path.exists():
            return path

        latest = self.latest_checkpoint(str(reference))
        if latest is not None:
            return latest

        raise FileNotFoundError(f"No checkpoint found for reference: {reference}")