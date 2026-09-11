"""`round_history.json` zeigt den Zustand jeder Runde — nicht überall den Endzustand (P5.1).

Bis zum 2026-09-11 übergaben beide Stellen, die ein `RoundResult` bauen,
`state.environment` selbst. Pydantic übernimmt eine übergebene Modellinstanz,
ohne sie zu kopieren: Jede Runde hielt dieselbe Referenz, und beim Schreiben stand
in allen der letzte Stand — in einem Lauf über 120 Ticks in Runde 1 wörtlich
«Tick 120/120». Gelesen wird der Schnappschuss von keiner Auswertung; die Zahlen
eines Laufs hat das nie bewegt, das Artefakt aber zeigte eine Entwicklung, wo keine
stand.
"""

from __future__ import annotations

import ast
from pathlib import Path

from src.config_loader import build_initial_state
from src.orchestration import simulation_runner

ROOT = Path(__file__).resolve().parent.parent


def _lauf(tmp_path, monkeypatch, ticks: int):
    monkeypatch.setattr(simulation_runner, "resolve_run_output_dir", lambda run_id: tmp_path)
    zustand = build_initial_state()
    zustand.clock.max_ticks = ticks
    return simulation_runner.SimulationRunner(
        llm=None,  # type: ignore[arg-type]
        options=simulation_runner.RunnerOptions(
            deterministic_only=True, checkpoint_interval=0, verbose_ticks=False
        ),
    ).run(zustand, seed=42, run_id="rundenhistorie")


def test_jede_runde_traegt_ihren_eigenen_zustand(tmp_path, monkeypatch):
    """Die Umwelt-Runde setzt `global_context` direkt vor dem Speichern auf ihre Zusammenfassung.

    Der Schnappschuss einer Runde muss deshalb genau diese Zusammenfassung tragen
    («Tick N/M …»). Mit der geteilten Referenz trugen alle die der letzten Runde.
    """

    ende = _lauf(tmp_path, monkeypatch, ticks=4)
    runden = [r for r in ende.round_results if not r.agent_responses]
    assert (
        len({r.summary for r in runden}) >= 3
    ), "Vorbedingung: Die Runden unterscheiden sich nicht."

    falsch = [
        (r.round_number, r.environment_snapshot.global_context.splitlines()[:1])
        for r in runden
        if r.environment_snapshot.global_context != r.summary
    ]
    assert not falsch, f"Diese Runden tragen nicht ihren eigenen Zustand: {falsch}"


def test_kein_schnappschuss_uebergibt_den_lebenden_zustand():
    """Gesucht wird **jedes** `environment_snapshot=` in `src/`, nicht die zwei heutigen Stellen.

    Das deckt auch `agent_node`, den ein Lauf ohne Sprachmodell nie erreicht.
    Heuristisch: Verlangt wird ein Aufruf (heute `model_copy(deep=True)`), kein
    bloßer Name oder Attributzugriff auf den laufenden Zustand.
    """

    gefunden = 0
    befunde: list[str] = []
    for pfad in sorted((ROOT / "src").rglob("*.py")):
        for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
            if isinstance(knoten, ast.keyword) and knoten.arg == "environment_snapshot":
                gefunden += 1
                if not isinstance(knoten.value, ast.Call):
                    befunde.append(f"{pfad.relative_to(ROOT)}:{knoten.value.lineno}")

    assert gefunden >= 1, "Kein `environment_snapshot=` gefunden — dann misst dieser Test nichts."
    assert not befunde, (
        "Diese Stellen legen den lebenden Zustand in eine Runde, statt eine Kopie:\n  "
        + "\n  ".join(befunde)
        + "\n\nJede Runde hielte dann dieselbe Referenz, und round_history.json zeigte "
        "überall den Endzustand."
    )
