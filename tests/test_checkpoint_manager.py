from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.orchestration.checkpoint_manager import (
    CHECKPOINT_VERSION,
    CheckpointManager,
    CheckpointVersionError,
)
from src.orchestration.environment_node import EnvironmentNode

#: Unterscheidet «Metadatenblock fehlt ganz» von «Block ist leer» — `None` wäre
#: als Wert selbst ein Fall, den der Test prüfen will.
_FEHLT = object()


def test_checkpoint_save_and_load_round_boundary(tmp_path):
    state = build_initial_state()
    state.clock.current_tick = 2
    state.clock.max_ticks = 3

    manager = CheckpointManager(checkpoint_dir=tmp_path)
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


def test_checkpoint_serializes_population_individuals(tmp_path):
    state = build_initial_state()
    state.clock.current_tick = 1
    state.config.seed = 42
    state = EnvironmentNode().invoke(state)

    assert len(state.population_individuals) > 0

    manager = CheckpointManager(checkpoint_dir=tmp_path)
    path = manager.save(state, run_id="run-pop", round_number=1)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert len(payload["state"]["population_individuals"]) == len(state.population_individuals)
    assert isinstance(payload["state"]["population_individuals"][0]["booked"], bool)


class TestDieVersionWirdWirklichGeprueft:
    """P3.2 (2026-09-05) — **das Feld täuschte eine Prüfung vor, die es nicht gab.**

    `checkpoint_version` stand seit AP3 in jedem Checkpoint-Metadatum, und
    `load` las `payload["metadata"]` überhaupt nicht. Ein Checkpoint aus einem
    fremden Format lief damit direkt in `SimulationState.model_validate` — dort
    entweder ein Pydantic-Fehler ohne jeden Bezug zur Version oder, schlimmer,
    stille Vorgabewerte für die Felder, die es im alten Schema noch nicht gab.

    **Eine Migration gibt es bewusst nicht.** Solange es eine Version gibt, wäre
    sie Code ohne Fall. Was es gibt, ist eine Meldung, die den Weg nennt.
    """

    @staticmethod
    def _schreibe(tmp_path: Path, metadata: object) -> Path:
        """Ein Checkpoint mit beliebigem Metadatenblock, sonst gültig."""

        state = build_initial_state()
        pfad = tmp_path / "tick_0001.json"
        nutzlast: dict = {"state": state.model_dump(mode="json")}
        if metadata is not _FEHLT:
            nutzlast["metadata"] = metadata
        pfad.write_text(json.dumps(nutzlast, ensure_ascii=False), encoding="utf-8")
        return pfad

    def test_der_eigene_checkpoint_laedt(self, tmp_path):
        """Die Prüfung wäre wertlos, wenn sie den eigenen Schreiber abweist."""

        manager = CheckpointManager(checkpoint_dir=tmp_path)
        pfad = manager.save(build_initial_state(), run_id="run-gut", round_number=1)

        assert manager.load(pfad).clock.max_ticks > 0

    def test_eine_fremde_version_wird_abgewiesen(self, tmp_path):
        manager = CheckpointManager(checkpoint_dir=tmp_path)
        pfad = self._schreibe(tmp_path, {"run_id": "alt", "checkpoint_version": 1})

        with pytest.raises(CheckpointVersionError) as fehler:
            manager.load(pfad)

        text = str(fehler.value)
        assert "Version 1" in text and f"Version {CHECKPOINT_VERSION}" in text
        assert "tick_0001.json" in text, "Die Meldung nennt nicht, welche Datei es war"

    def test_eine_zukuenftige_version_ebenso(self, tmp_path):
        """Nicht «älter als meine», sondern «nicht meine»."""

        manager = CheckpointManager(checkpoint_dir=tmp_path)
        pfad = self._schreibe(tmp_path, {"checkpoint_version": CHECKPOINT_VERSION + 1})

        with pytest.raises(CheckpointVersionError):
            manager.load(pfad)

    def test_ein_checkpoint_ohne_metadaten_ist_eine_fremde_version(self, tmp_path):
        """**Der Fall, den ein `.get(..., CHECKPOINT_VERSION)` verschluckt hätte.**

        Die Metadaten gibt es erst seit Version 2. Ein Checkpoint ohne sie stammt
        von davor — `latest_checkpoint` findet solche `round_*.json` noch — und
        trägt ein anderes Zustandsschema. Ihn als aktuell zu behandeln wäre genau
        die stille Annahme, gegen die dieses Paket antritt.
        """

        manager = CheckpointManager(checkpoint_dir=tmp_path)

        for metadata in (_FEHLT, {}, {"run_id": "ohne_version"}, "kein Block"):
            pfad = self._schreibe(tmp_path, metadata)
            with pytest.raises(CheckpointVersionError, match="keine Angabe"):
                manager.load(pfad)

    def test_die_zahl_steht_an_einer_stelle(self, tmp_path):
        """Schreiber und Leser dürfen nicht auseinanderlaufen.

        Genau das war der Zustand vorher: `save` schrieb eine 2, und kein Leser
        hätte gemerkt, wenn dort eine 3 gestanden hätte.
        """

        manager = CheckpointManager(checkpoint_dir=tmp_path)
        pfad = manager.save(build_initial_state(), run_id="run-zahl", round_number=1)
        geschrieben = json.loads(pfad.read_text(encoding="utf-8"))

        assert geschrieben["metadata"]["checkpoint_version"] == CHECKPOINT_VERSION
