from __future__ import annotations

from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner


class _DummyLLM:
    def call(self, prompt: str) -> str:
        return "{}"


def test_checkpoint_interval_every_fifth_tick():
    runner = SimulationRunner(_DummyLLM(), options=RunnerOptions(checkpoint_interval=5))
    assert runner._should_save_checkpoint(5, 40) is True
    assert runner._should_save_checkpoint(10, 40) is True
    assert runner._should_save_checkpoint(7, 40) is False
    assert runner._should_save_checkpoint(40, 40) is True
