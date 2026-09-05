"""Launching a simulation run (single, multi-run, or sweep batch) from the UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

from dashboard.config_catalog import (
    ConfigDraft,
    PropertyEditState,
    llm_config_from_draft,
    prepare_simulation_state,
)
from dashboard.run_browser import generate_figures_for_run
from src.llm import MockLLM, OllamaClient, OllamaConfig
from src.llm.defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
)
from src.logging_setup import configure_logging, progress_logging
from src.orchestration.checkpoint_manager import CheckpointManager
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner
from src.reporting.output_writer import create_run_id, resolve_run_output_dir

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class RunLaunchConfig:
    rounds: int = 10
    seed: int | None = None
    scenario_mode: str = "basis"
    sweep_id: str | None = None
    simulation_config_file: str = "simulation_config.json"
    properties_file: str = "properties.json"
    agents_file: str = "agents.json"
    factors_file: str = "factors.json"
    cib_file: str = "cib_frozen.json"
    simulation_name: str | None = None
    simulation_description: str | None = None
    apply_custom_overrides: bool = False
    property_edits: dict[str, PropertyEditState] | None = None
    # `factor_states` ist mit P2.0-C entfallen: Die Faktorlage wird nicht
    # mehr vorgegeben, sie entsteht im Lauf aus den exogenen Systemgrößen.
    mock_llm: bool = True
    deterministic_only: bool = False
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    no_market: bool = False
    redebedarf: bool = False
    checkpoint_interval: int = 5
    no_protocol: bool = False
    no_scenarios: bool = False
    run_id: str | None = None
    resume_from: str | None = None
    run_all_sweeps: bool = False
    runs: int = 1
    generate_figures: bool = True
    quiet: bool = True
    #: Startpreis, falls im Assistenten gesetzt (P1.9-W1.5). **Dieses Feld hat
    #: gefehlt**, und weil `launch_from_draft` den Entwurf durch diese
    #: Datenklasse schickt (`draft_to_launch_config` → `launch_config_to_draft`),
    #: fiel der Wert dabei lautlos heraus: `build_custom_sweep_from_draft` wertet
    #: ihn korrekt aus, er kam dort nur nie an. «Startpreis selbst festlegen» war
    #: über das Dashboard wirkungslos, über die CLI nicht.
    base_price: float | None = None


@dataclass(frozen=True)
class RunLaunchResult:
    run_id: str
    run_dir: Path
    ticks_completed: int
    total_events: int
    artifacts: dict[str, str | None]
    sweep_batch: bool = False
    sweep_summary_path: str | None = None
    multi_run_batch: bool = False
    batch_id: str | None = None
    child_run_ids: tuple[str, ...] = ()


def launch_config_to_draft(config: RunLaunchConfig) -> ConfigDraft:
    from dashboard.config_catalog import default_config_draft

    draft = default_config_draft()
    draft.rounds = config.rounds
    draft.seed = config.seed
    draft.use_seed = config.seed is not None
    draft.scenario_mode = config.scenario_mode
    draft.sweep_id = config.sweep_id
    draft.simulation_config_file = config.simulation_config_file
    draft.properties_file = config.properties_file
    draft.agents_file = config.agents_file
    draft.factors_file = config.factors_file
    draft.cib_file = config.cib_file
    draft.simulation_name = config.simulation_name or ""
    draft.simulation_description = config.simulation_description or ""
    draft.apply_custom_overrides = config.apply_custom_overrides
    if config.property_edits:
        draft.property_edits = dict(config.property_edits)
    draft.mock_llm = config.mock_llm
    draft.deterministic_only = config.deterministic_only
    draft.model = config.model
    draft.base_url = config.base_url
    draft.temperature = config.temperature
    draft.max_tokens = config.max_tokens
    draft.no_market = config.no_market
    draft.redebedarf = config.redebedarf
    draft.checkpoint_interval = config.checkpoint_interval
    draft.no_protocol = config.no_protocol
    draft.no_scenarios = config.no_scenarios
    draft.resume_from = config.resume_from or ""
    draft.run_all_sweeps = config.run_all_sweeps
    draft.run_count = max(1, int(config.runs))
    draft.generate_figures = config.generate_figures
    draft.base_price = config.base_price
    return draft


def draft_to_launch_config(draft: ConfigDraft) -> RunLaunchConfig:
    return RunLaunchConfig(
        rounds=int(draft.rounds),
        seed=int(draft.seed) if draft.use_seed else None,
        scenario_mode=draft.scenario_mode,
        sweep_id=draft.sweep_id,
        simulation_config_file=draft.simulation_config_file,
        properties_file=draft.properties_file,
        agents_file=draft.agents_file,
        factors_file=draft.factors_file,
        cib_file=draft.cib_file,
        simulation_name=draft.simulation_name or None,
        simulation_description=draft.simulation_description or None,
        apply_custom_overrides=draft.apply_custom_overrides or draft.scenario_mode == "custom",
        property_edits=draft.property_edits,
        mock_llm=draft.mock_llm,
        deterministic_only=draft.deterministic_only,
        model=draft.model.strip() or DEFAULT_MODEL,
        base_url=draft.base_url.strip(),
        temperature=float(draft.temperature),
        max_tokens=int(draft.max_tokens),
        no_market=draft.no_market,
        redebedarf=draft.redebedarf,
        checkpoint_interval=int(draft.checkpoint_interval),
        no_protocol=draft.no_protocol,
        no_scenarios=draft.no_scenarios,
        resume_from=draft.resume_from.strip() or None,
        run_all_sweeps=draft.run_all_sweeps,
        runs=max(1, int(draft.run_count)),
        generate_figures=draft.generate_figures,
        quiet=False,
        base_price=draft.base_price,
    )


def launch_from_draft(
    draft: ConfigDraft,
    *,
    repo_root: Path | None = None,
    on_progress: Callable[[str], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> RunLaunchResult:
    return launch_simulation(
        draft_to_launch_config(draft),
        repo_root=repo_root,
        on_progress=on_progress,
        should_stop=should_stop,
    )


def launch_simulation(
    config: RunLaunchConfig,
    *,
    repo_root: Path | None = None,
    on_progress: Callable[[str], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> RunLaunchResult:
    """Run one simulation, multi-run batch, or sweep batch and persist outputs."""

    import contextlib
    import sys

    from src.orchestration.scenario_sweeps import SWEEP_OUTPUT_DIR, run_all_sweeps
    from src.run_simulation import build_run_args, save_run_outputs, write_multi_run_summary

    def _maybe_generate_figures(run_directory: Path) -> None:
        if not config.generate_figures:
            return
        try:
            generate_figures_for_run(run_directory)
            print(f"Figures saved under {run_directory / 'figures'}")
        except Exception as exc:
            print(f"Warning: figure generation failed for {run_directory.name}: {exc}")

    def _build_llm():
        """Der Client aus **derselben** Ableitung, die auch den Zustand füllt (P3.4).

        `llm_config_from_draft` ist die eine Regel; `prepare_simulation_state`
        legt ihr Ergebnis in `state.config.llm` ab, hier wird der Client daraus
        gebaut. Vorher las `state.config.llm` niemand, und dieser Client entstand
        direkt aus `RunLaunchConfig` — im Zustand stand damit etwas anderes als
        im Lauf.
        """

        llm_config = llm_config_from_draft(launch_config_to_draft(config))
        if llm_config is None:
            # `MockLLM` statt `get_llm()`: letzteres liefert `LocalOllama`, sobald
            # OLLAMA_MODEL gesetzt ist. Seit P0.1 heisst «Ohne Sprachmodell
            # rechnen» genau das, unabhaengig von der Umgebung.
            return MockLLM()
        return OllamaClient(
            OllamaConfig(
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
            )
        )

    def _build_runner():
        return SimulationRunner(
            llm=_build_llm(),
            options=RunnerOptions(
                enable_market=not config.no_market,
                enable_redebedarf=config.redebedarf,
                deterministic_only=config.deterministic_only,
                checkpoint_interval=max(0, int(config.checkpoint_interval)),
                verbose_ticks=True,
                # **Der Abbruch reicht bis in die Tick-Schleife** (P1.9-W4.5).
                # Der Sweep-Pfad bekommt ihn nicht: `run_all_sweeps` baut seinen
                # Runner selbst, und ihn dafür zu öffnen wäre eine Änderung an
                # seinem Vertrag (W1.1) — das gehört in ein eigenes Paket.
                should_stop=should_stop,
            ),
        )

    def _run_body() -> RunLaunchResult:
        if config.run_all_sweeps:
            run_all_sweeps(
                # **Kein `ticks_override` mehr vom Dashboard aus** (P1.9-W1.2).
                #
                # Hier stand `int(config.rounds) if config.rounds else None`, und
                # `rounds` hat immer einen Wert — jedes Szenario lief also mit der
                # Länge des Entwurfs statt mit seiner eigenen `max_ticks`. Schritt 1
                # des Assistenten warnt wörtlich davor («Angelegt ist es auf N
                # Ticks»), und der Weg «Szenario-Vergleich starten» springt an
                # dieser Frage vorbei: Man sah sie nie und bekam trotzdem ihre
                # Wirkung.
                #
                # Woran erkennt man «bewusst gewählt»? Der Entwurf hat kein solches
                # Signal — 40 ist ein Vorgabewert, kein Wunsch. Die CLI hat es:
                # `--ticks` steht auf `None`, bis jemand es angibt. Sie behält den
                # Übersteuerungsweg deshalb; das Dashboard gibt ihn auf. Ein
                # Vergleich rechnet jedes Szenario so lang, wie es angelegt ist.
                ticks_override=None,
                sweep_filter=None,
                verbose=True,
            )
            summary_path = SWEEP_OUTPUT_DIR / "sweep_summary.json"
            child_run_ids: list[str] = []
            if config.generate_figures:
                for sweep_dir in sorted(SWEEP_OUTPUT_DIR.glob("sweep_*")):
                    if sweep_dir.is_dir() and (sweep_dir / "run_metadata.json").is_file():
                        _maybe_generate_figures(sweep_dir)
            for sweep_dir in sorted(SWEEP_OUTPUT_DIR.glob("sweep_*"), reverse=True):
                if sweep_dir.is_dir() and (sweep_dir / "run_metadata.json").is_file():
                    child_run_ids.append(f"sweeps/{sweep_dir.name}")
            return RunLaunchResult(
                run_id=child_run_ids[0] if child_run_ids else "sweep-batch",
                run_dir=(
                    SWEEP_OUTPUT_DIR / child_run_ids[0].split("/", 1)[1]
                    if child_run_ids
                    else SWEEP_OUTPUT_DIR
                ),
                ticks_completed=config.rounds,
                total_events=0,
                artifacts={"sweep_summary": str(summary_path)},
                sweep_batch=True,
                sweep_summary_path=str(summary_path),
                child_run_ids=tuple(child_run_ids),
            )

        runs = max(1, int(config.runs))
        if runs > 1 and config.resume_from:
            raise ValueError("Mehrfach-Lauf kann nicht mit Resume kombiniert werden.")

        llm = _build_llm()
        runner = _build_runner()

        if runs > 1:
            batch_id = config.run_id or create_run_id("batch")
            batch_dir = resolve_run_output_dir(batch_id)
            ck_path = batch_dir / "checkpoints"
            checkpoint_manager = CheckpointManager(ck_path)

            draft = launch_config_to_draft(config)
            base_state = prepare_simulation_state(draft)
            if config.seed is not None:
                base_state.config.seed = int(config.seed)

            print(
                f"Starting multi-run: runs={runs}, ticks={base_state.clock.max_ticks}, batch_id={batch_id}"
            )
            multi_result = runner.run_multi(
                runs,
                base_state=base_state,
                checkpoint_store=checkpoint_manager,
            )

            args = SimpleNamespace(
                model=config.model,
                base_url=config.base_url,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                no_market=config.no_market,
                redebedarf=config.redebedarf,
                no_protocol=config.no_protocol,
                no_scenarios=config.no_scenarios,
                deterministic_only=config.deterministic_only,
                # **`mock_llm` gehört hierher** — es fehlte, und
                # `save_run_metadata` fällt bei einem fehlenden Feld auf `False`
                # zurück. Jeder Dashboard-Lauf «Ohne Sprachmodell» wurde damit
                # als vollwertiger LLM-Lauf protokolliert.
                mock_llm=config.mock_llm,
                # **Ausgeschrieben statt ausgelassen.** Dieser Pfad erzeugt nie
                # den Hybridmodus: `generate_and_save_run_scenario` bekommt
                # `prefer_llm=not deterministic_only`, ein reiner Zahlenlauf also
                # gar kein Modell. `False` ist damit richtig — aber es steht hier,
                # weil ein weggelassenes Feld von einem abgeschalteten nicht zu
                # unterscheiden ist.
                llm_narrative=False,
                quiet=False,
                run_id=batch_id,
                checkpoint_dir=str(ck_path),
            )

            all_artifacts: list[dict[str, str | None]] = []
            child_run_ids: list[str] = []
            total_events = 0
            for index, run_result in enumerate(multi_result.runs, start=1):
                sub_run_id = f"run_{index:03d}"
                run_dir = batch_dir / sub_run_id
                run_dir.mkdir(parents=True, exist_ok=True)
                run_args = build_run_args(args, run_index=index, seed=run_result.seed)
                artifacts = save_run_outputs(
                    run_result.final_state,
                    run_args,
                    llm,
                    run_dir=run_dir,
                    run_id=sub_run_id,
                )
                all_artifacts.append(artifacts)
                child_run_ids.append(f"{batch_id}/{sub_run_id}")
                total_events += len(run_result.final_state.event_log)
                _maybe_generate_figures(run_dir)
                print(
                    f"Run {index:03d}: {sub_run_id} seed={run_result.seed} "
                    f"ticks={run_result.ticks_completed} events={len(run_result.final_state.event_log)}"
                )

            summary_path = batch_dir / "multi_run_summary.json"
            write_multi_run_summary(
                summary_path=summary_path,
                result=multi_result,
                run_artifacts=all_artifacts,
            )

            return RunLaunchResult(
                run_id=child_run_ids[0] if child_run_ids else batch_id,
                run_dir=(
                    (batch_dir / child_run_ids[0].split("/", 1)[1]) if child_run_ids else batch_dir
                ),
                ticks_completed=multi_result.runs[-1].ticks_completed if multi_result.runs else 0,
                total_events=total_events,
                artifacts={
                    "multi_run_summary": str(summary_path),
                    **(all_artifacts[0] if all_artifacts else {}),
                },
                multi_run_batch=True,
                batch_id=batch_id,
                child_run_ids=tuple(child_run_ids),
            )

        run_id = config.run_id or create_run_id()
        run_dir = resolve_run_output_dir(run_id)
        ck_path = run_dir / "checkpoints"
        checkpoint_manager = CheckpointManager(ck_path)

        args = SimpleNamespace(
            model=config.model,
            base_url=config.base_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            no_market=config.no_market,
            redebedarf=config.redebedarf,
            no_protocol=config.no_protocol,
            no_scenarios=config.no_scenarios,
            deterministic_only=config.deterministic_only,
            # Siehe oben: ohne dieses Feld behauptet das Artefakt einen Lauf mit
            # Sprachmodell, während der Mock gerechnet hat.
            mock_llm=config.mock_llm,
            # Siehe oben: eine Aussage statt einer Auslassung.
            llm_narrative=False,
            quiet=False,
            run_id=run_id,
            checkpoint_dir=str(ck_path),
            simulation_name=config.simulation_name,
            simulation_description=config.simulation_description,
        )

        if config.resume_from:
            final_state = runner.run(
                None,
                checkpoint_store=checkpoint_manager,
                resume_from=config.resume_from,
                run_id=run_id,
            )
            seed = final_state.config.seed
        else:
            draft = launch_config_to_draft(config)
            state = prepare_simulation_state(draft)
            final_state = runner.run(
                state,
                seed=config.seed,
                checkpoint_store=checkpoint_manager,
                run_id=run_id,
            )
            # Nicht `config.seed`: Das ist der *angeforderte* Wert und bleibt
            # leer, wenn niemand einen genannt hat. Der Runner hat ihn da schon
            # aufgelöst — der State trägt den tatsächlich benutzten.
            #
            # Heute ist das eine Gürtel-und-Hosenträger-Zeile und **kein** Test
            # kann sie decken: `save_run_metadata` liest den Seed ohnehin
            # zuerst aus `state.config.seed` und greift auf diesen Wert nur
            # zurück, wenn dort keiner steht — was nach einem Runner-Lauf nicht
            # vorkommt. Sie steht trotzdem hier, weil sie load-bearing würde,
            # sobald jemand diese Reihenfolge umdreht. Festgestellt bei der
            # Mutationsprüfung am 2026-08-27.
            seed = final_state.config.seed

        artifacts = save_run_outputs(
            final_state,
            build_run_args(args, run_index=1, seed=seed),
            llm,
            run_dir=run_dir,
            run_id=run_id,
        )
        _maybe_generate_figures(run_dir)

        return RunLaunchResult(
            run_id=run_id,
            run_dir=run_dir,
            ticks_completed=final_state.clock.current_tick,
            total_events=len(final_state.event_log),
            artifacts=artifacts,
        )

    # Ohne Handler faellt jede Logzeile unterhalb von WARNING auf den Boden;
    # der Aufruf hier bindet den Konsolen-Handler an das *echte* stdout, bevor
    # der Tee unten `sys.stdout` umbiegt. Sonst liefe jede Zeile zweimal durch
    # das Fortschrittsfenster.
    configure_logging()

    if on_progress is None:
        return _run_body()

    stdout = sys.stdout

    class _StdoutTee:
        def write(self, data: str) -> None:
            stdout.write(data)
            for line in data.splitlines():
                stripped = line.strip()
                if stripped:
                    on_progress(stripped)

        def flush(self) -> None:
            stdout.flush()

    # Zwei Kanaele: `print` ueber den Tee, `logging` ueber den Handler. Beide
    # landen im selben Fortschrittsfenster, keiner doppelt.
    with contextlib.redirect_stdout(_StdoutTee()), progress_logging(on_progress):
        return _run_body()
