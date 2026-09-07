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

#: Das Format, das dieser Code schreibt **und** liest (P3.2).
#:
#: Die Zahl stand bis zum 2026-09-05 nur in der Datei: `save` schrieb sie, `load`
#: las `payload["metadata"]` überhaupt nicht. Damit täuschte das Feld eine
#: Versionsprüfung vor, die es nicht gab — ein Checkpoint aus einem fremden
#: Format wäre in `SimulationState.model_validate` gelaufen und hätte dort
#: entweder einen Pydantic-Fehler ohne Bezug zur Version geworfen oder, viel
#: schlimmer, mit stillen Vorgabewerten für die fehlenden Felder durchgekommen.
#:
#: **Wer das Zustandsschema bricht, erhöht diese Zahl.** Eine Migration gibt es
#: bewusst nicht: Solange es nur eine Version gibt, wäre sie Code ohne Fall.
CHECKPOINT_VERSION = 2


class CheckpointVersionError(Exception):
    """Ein Checkpoint aus einem Format, das dieser Code nicht liest (P3.2)."""


@dataclass(frozen=True)
class CheckpointMetadata:
    """Lightweight metadata stored alongside each checkpoint."""

    run_id: str
    tick_number: int
    saved_at: str
    checkpoint_version: int = CHECKPOINT_VERSION


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
        """Load a checkpoint from a file path or from the latest checkpoint of a run.

        Prüft zuerst die Version (P3.2). Ein Checkpoint aus einem fremden Format
        wird abgewiesen, statt in `model_validate` zu laufen — dort wären die
        fehlenden Felder entweder ein Pydantic-Fehler ohne Bezug zur Version oder
        stille Vorgabewerte.
        """

        checkpoint_path = self._resolve_reference(reference)
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        self._pruefe_version(payload, checkpoint_path)
        state_data: dict[str, Any] = payload["state"]
        return SimulationState.model_validate(state_data)

    @staticmethod
    def _pruefe_version(payload: dict[str, Any], pfad: Path) -> None:
        """Die Version des Checkpoints gegen die dieses Codes.

        **Ein fehlendes Feld ist eine fremde Version, keine passende.** Die
        Metadaten gibt es seit Version 2; ein Checkpoint ohne sie stammt von
        davor (die alten `round_*.json`, die `latest_checkpoint` noch findet) und
        trägt ein anderes Zustandsschema. Ihn als aktuell zu behandeln wäre
        genau die stille Annahme, gegen die dieses Paket antritt.
        """

        metadata = payload.get("metadata")
        version = metadata.get("checkpoint_version") if isinstance(metadata, dict) else None

        if version == CHECKPOINT_VERSION:
            return

        gefunden = "keine Angabe" if version is None else repr(version)
        raise CheckpointVersionError(
            f"Checkpoint '{pfad.name}' hat Version {gefunden}, dieser Code liest "
            f"Version {CHECKPOINT_VERSION}. Ein Lauf lässt sich daraus nicht "
            "fortsetzen — das Zustandsschema kann sich seither geändert haben. "
            "Den Lauf neu starten oder den Checkpoint mit der Fassung öffnen, "
            "die ihn geschrieben hat."
        )

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
