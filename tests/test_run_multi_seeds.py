"""Wiederholungen: woher ihre Vielfalt kommt und womit sie beginnen.

`run_multi` ist die Grundlage einer **dokumentierten Arbeitsweise** — das
Handbuch empfiehlt in `fragestellungen.md` und `vergleiche.md`, die natürliche
Streuung über mehrere Wiederholungen mit freiem Startwert zu messen. Bis zum
2026-08-27 hatte diese Funktion trotzdem keinen einzigen Test.

Aufgefallen ist das über eine Pfadabhängigkeit: `base_seed` war
`base_state.config.seed or 0`, während ein Einzellauf ohne genannten Seed mit
`DEFAULT_SEED` rechnet. Derselbe Aufbau lieferte je nach Pfad andere Zahlen,
ohne dass irgendwo stand, warum. Angeglichen — und hier festgehalten.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

from src.config_loader import build_initial_state
from src.models.state_models import DEFAULT_SEED
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner


class _StummesLLM:
    def call(self, prompt: str) -> str:
        return (
            '{"reasoning": "", "actions": [], "state_changes": [], '
            '"events": [], "segment_analysis": {}}'
        )


def _runner() -> SimulationRunner:
    return SimulationRunner(
        llm=_StummesLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=False,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )


def _basis(ticks: int = 2):
    state = build_initial_state(load_cib=False)
    state.clock.max_ticks = ticks
    return state


class TestDerStartwertDerFolge:
    def test_without_a_configured_seed_it_starts_at_the_default(self) -> None:
        """Der Kern der Angleichung: derselbe Standard wie im Einzellauf."""

        ergebnis = _runner().run_multi(3, base_state=_basis())

        assert [r.seed for r in ergebnis.runs] == [
            DEFAULT_SEED,
            DEFAULT_SEED + 1,
            DEFAULT_SEED + 2,
        ]

    def test_a_configured_seed_still_wins(self) -> None:
        state = _basis()
        state.config.seed = 100
        ergebnis = _runner().run_multi(2, base_state=state)

        assert [r.seed for r in ergebnis.runs] == [100, 101]

    def test_an_explicit_zero_is_a_value_not_a_gap(self) -> None:
        """Vorher stand hier `or 0` — das kann eine gesetzte 0 nicht von einem
        fehlenden Wert unterscheiden. Heute stimmt das Ergebnis zufällig
        überein; die Unterscheidung ist trotzdem die richtige."""

        state = _basis()
        state.config.seed = 0
        ergebnis = _runner().run_multi(2, base_state=state)

        assert [r.seed for r in ergebnis.runs] == [0, 1]

    def test_explicit_seeds_override_the_sequence(self) -> None:
        ergebnis = _runner().run_multi(2, base_state=_basis(), seeds=[7, 9])

        assert [r.seed for r in ergebnis.runs] == [7, 9]


class TestWorausDieVielfaltKommt:
    """Die Sorge beim Angleichen war, die Wiederholungen könnten ihre
    Unterschiedlichkeit verlieren. Sie kommt aus `base_seed + index`, nicht aus
    dem fehlenden Seed — diese beiden Tests halten das fest, damit die Frage
    nicht noch einmal gestellt werden muss."""

    def test_repetitions_still_draw_different_populations(self) -> None:
        ergebnis = _runner().run_multi(3, base_state=_basis())

        seeds = [r.seed for r in ergebnis.runs]
        assert len(set(seeds)) == len(seeds), "Wiederholungen teilen sich einen Seed"

    def test_the_first_repetition_equals_a_single_run(self) -> None:
        """Die Eigenschaft, die das Angleichen einbringt: Ein Einzellauf ist
        die erste Wiederholung, nicht ein vierter, unerklärter Fall."""

        einzeln = _runner().run(_basis(), run_id="einzeln")
        mehrfach = _runner().run_multi(2, base_state=_basis())

        assert mehrfach.runs[0].seed == einzeln.config.seed == DEFAULT_SEED


class TestDieAngabeImArtefakt:
    def test_every_repetition_records_its_own_seed(self, tmp_path) -> None:
        """Ohne diese Zusage wäre die Angleichung nicht nachprüfbar."""

        from src.reporting.output_writer.metadata import save_run_metadata
        from src.run_simulation import _build_run_args

        ergebnis = _runner().run_multi(2, base_state=_basis())

        gelesen = []
        for index, lauf in enumerate(ergebnis.runs, start=1):
            args = _build_run_args(
                SimpleNamespace(
                    model="m",
                    base_url="u",
                    temperature=0.1,
                    max_tokens=1,
                    no_market=False,
                    mock_llm=True,
                    deterministic_only=True,
                    simulation_name=None,
                    simulation_description=None,
                ),
                run_index=index,
                seed=lauf.seed,
            )
            ziel = tmp_path / f"run-{index}"
            ziel.mkdir()
            save_run_metadata(lauf.final_state, args, run_dir=ziel, run_id=f"run-{index}")
            gelesen.append(json.loads((ziel / "run_metadata.json").read_text(encoding="utf-8")))

        assert [m["seed"] for m in gelesen] == [DEFAULT_SEED, DEFAULT_SEED + 1]
