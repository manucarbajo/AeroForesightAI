"""Backend für das Präsentations-Dashboard — liest `outputs/` und startet Simulationen via `src/`."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Literal

from dashboard.config_catalog import (
    ConfigDraft,
    PropertyEditState,
    prepare_simulation_state,
)
from src.checkpoint_manager import CheckpointManager
from src.llm_client import OllamaClient, OllamaConfig
from src.output_writer import OUTPUT_DIR, create_run_id, resolve_run_output_dir
from src.simulation_runner import RunnerOptions, SimulationRunner
from src.studio_helpers import get_llm

CheckStatus = Literal["ok", "warn", "fail"]

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    run_dir: Path
    ticks_completed: int | None
    ticks_max: int | None
    total_events: int | None
    model: str | None
    timestamp: str | None
    has_narrative: bool
    has_tick_mechanics: bool
    has_run_scenario: bool
    scenario_title: str | None
    scenario_summary: str | None


@dataclass(frozen=True)
class RunFileEntry:
    relative_path: str
    absolute_path: Path
    size_bytes: int
    kind: str


@dataclass(frozen=True)
class ConsistencyCheck:
    check_id: str
    title: str
    status: CheckStatus
    detail: str


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
    factor_states: dict[str, str] | None = None
    mock_llm: bool = True
    deterministic_only: bool = False
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2048
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
    if config.factor_states:
        draft.factor_states = dict(config.factor_states)
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
        factor_states=draft.factor_states,
        mock_llm=draft.mock_llm,
        deterministic_only=draft.deterministic_only,
        model=draft.model.strip() or "llama3.2",
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
    )


def launch_from_draft(
    draft: ConfigDraft,
    *,
    repo_root: Path | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> RunLaunchResult:
    return launch_simulation(
        draft_to_launch_config(draft),
        repo_root=repo_root,
        on_progress=on_progress,
    )


def outputs_root(path: Path | str | None = None) -> Path:
    return Path(path or OUTPUT_DIR)


def _load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_run_scenario_preview(run_dir: Path) -> tuple[bool, str | None, str | None]:
    scenario_path = run_dir / "run_scenario.json"
    if not scenario_path.is_file():
        return False, None, None
    payload = _load_json(scenario_path)
    if not isinstance(payload, dict):
        return True, None, None
    title = payload.get("title")
    summary = payload.get("summary")
    scenarios = payload.get("scenarios")
    if isinstance(scenarios, list) and scenarios:
        first = scenarios[0] if isinstance(scenarios[0], dict) else {}
        preview_title = first.get("title")
        archetypes = ", ".join(
            str(item.get("archetype"))
            for item in scenarios[:3]
            if isinstance(item, dict) and item.get("archetype")
        )
        if summary and archetypes:
            preview_summary = f"{summary} · Top-3: {archetypes}"
        elif archetypes:
            preview_summary = f"Top-3: {archetypes}"
        else:
            preview_summary = summary
        return (
            True,
            str(preview_title or title) if (preview_title or title) else None,
            str(preview_summary) if preview_summary else None,
        )
    return (
        True,
        str(title) if title else None,
        str(summary) if summary else None,
    )


def load_run_scenario(run_dir: Path | str) -> dict[str, Any] | None:
    payload = _load_json(Path(run_dir) / "run_scenario.json")
    return payload if isinstance(payload, dict) else None


def regenerate_run_scenario(
    run_id: str,
    *,
    run_dir: Path | str | None = None,
    mock_llm: bool = True,
    deterministic_only: bool = False,
    model: str = "llama3.2",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    from src.run_scenario_generator import generate_and_save_run_scenario

    directory = Path(run_dir) if run_dir is not None else resolve_run_output_dir(run_id)
    if mock_llm:
        llm = get_llm()
    else:
        llm = OllamaClient(
            OllamaConfig(
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    return generate_and_save_run_scenario(
        run_id,
        llm,
        run_dir=directory,
        prefer_llm=not deterministic_only,
    )


def list_runs(root: Path | str | None = None) -> list[RunSummary]:
    base = outputs_root(root)
    if not base.is_dir():
        return []

    summaries: list[RunSummary] = []

    def _append_run(run_dir: Path, run_id: str) -> None:
        metadata = _load_json(run_dir / "run_metadata.json")
        meta_dict = metadata if isinstance(metadata, dict) else {}
        has_scenario, scenario_title, scenario_summary = _read_run_scenario_preview(run_dir)
        summaries.append(
            RunSummary(
                run_id=run_id,
                run_dir=run_dir,
                ticks_completed=meta_dict.get("ticks_completed"),
                ticks_max=meta_dict.get("ticks_max"),
                total_events=meta_dict.get("total_events"),
                model=meta_dict.get("model"),
                timestamp=meta_dict.get("timestamp"),
                has_narrative=(run_dir / "final_narrative.md").is_file(),
                has_tick_mechanics=(run_dir / "tick_mechanics.json").is_file(),
                has_run_scenario=has_scenario,
                scenario_title=scenario_title,
                scenario_summary=scenario_summary,
            )
        )

    for entry in sorted(base.iterdir(), reverse=True):
        if not entry.is_dir():
            continue
        if entry.name.startswith("run_"):
            _append_run(entry, entry.name)
            continue
        if entry.name.startswith("batch_"):
            child_dirs = sorted(
                (child for child in entry.iterdir() if child.is_dir() and child.name.startswith("run_")),
                reverse=True,
            )
            for child_dir in child_dirs:
                if (child_dir / "run_metadata.json").is_file():
                    _append_run(child_dir, f"{entry.name}/{child_dir.name}")

    return summaries


@dataclass(frozen=True)
class RunFigureEntry:
    title: str
    relative_path: str
    absolute_path: Path


def list_run_figures(run_dir: Path | str) -> list[RunFigureEntry]:
    base = Path(run_dir) / "figures"
    if not base.is_dir():
        return []

    manifest_path = base / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        title_map = manifest.get("figures") or {}
        entries: list[RunFigureEntry] = []
        for title, filename in title_map.items():
            path = base / filename
            if path.is_file():
                entries.append(
                    RunFigureEntry(
                        title=str(title),
                        relative_path=f"figures/{filename}",
                        absolute_path=path,
                    )
                )
        if entries:
            return entries

    entries = []
    for path in sorted(base.glob("*.png")):
        entries.append(
            RunFigureEntry(
                title=path.stem.replace("_", " ").title(),
                relative_path=f"figures/{path.name}",
                absolute_path=path,
            )
        )
    return entries


def generate_figures_for_run(run_dir: Path | str) -> list[RunFigureEntry]:
    from src.figure_generator import generate_run_figures

    result = generate_run_figures(run_dir)
    return list_run_figures(result.run_dir)


def list_run_files(run_dir: Path | str) -> list[RunFileEntry]:
    base = Path(run_dir)
    if not base.is_dir():
        return []

    entries: list[RunFileEntry] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".json", ".md", ".csv", ".txt"}:
            kind = suffix.lstrip(".")
        elif suffix == ".png":
            kind = "png"
        else:
            kind = "other"
        entries.append(
            RunFileEntry(
                relative_path=str(path.relative_to(base)).replace("\\", "/"),
                absolute_path=path,
                size_bytes=path.stat().st_size,
                kind=kind,
            )
        )
    return entries


def read_run_file(path: Path | str, *, max_chars: int = 250_000) -> str:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n… [gekürzt, {len(text) - max_chars} Zeichen ausgeblendet]"
    return text


def load_price_series(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "price_history.json")
    return payload if isinstance(payload, list) else []


def load_tick_mechanics(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "tick_mechanics.json")
    if isinstance(payload, dict):
        ticks = payload.get("ticks")
        return ticks if isinstance(ticks, list) else []
    return []


def load_event_log(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "event_log.json")
    return payload if isinstance(payload, list) else []


def run_consistency_checks(run_dir: Path | str) -> list[ConsistencyCheck]:
    """Cross-check generated artefacts for presentation and debugging."""

    base = Path(run_dir)
    checks: list[ConsistencyCheck] = []

    required_files = [
        "run_metadata.json",
        "event_log.json",
        "price_history.json",
        "tick_mechanics.json",
        "final_narrative.md",
    ]
    missing = [name for name in required_files if not (base / name).is_file()]
    checks.append(
        ConsistencyCheck(
            check_id="required_files",
            title="Pflicht-Artefakte vorhanden",
            status="fail" if missing else "ok",
            detail="Fehlt: " + ", ".join(missing) if missing else "Alle Kern-Dateien liegen im Run-Ordner.",
        )
    )

    ticks = load_tick_mechanics(base)
    prices = load_price_series(base)
    events = load_event_log(base)

    price_by_tick = {
        int(row["round_number"]): float(row["price"])
        for row in prices
        if row.get("round_number") is not None and row.get("price") is not None
    }

    price_mismatches: list[str] = []
    for row in ticks:
        tick = int(row.get("tick", -1))
        expected = row.get("market_price_after_feedback_eur")
        actual = price_by_tick.get(tick)
        if expected is None or actual is None:
            continue
        if abs(float(expected) - float(actual)) > 0.05:
            price_mismatches.append(f"Tick {tick}: mechanics={expected:.2f}, price_history={actual:.2f}")

    checks.append(
        ConsistencyCheck(
            check_id="price_alignment",
            title="Ticketpreis: tick_mechanics ↔ price_history",
            status="fail" if price_mismatches else "ok",
            detail="; ".join(price_mismatches[:5]) if price_mismatches else "Preise stimmen überein.",
        )
    )

    delta_events = [event for event in events if "[delta:" in str(event.get("description", ""))]
    checks.append(
        ConsistencyCheck(
            check_id="delta_events",
            title="Python-Delta-Events im event_log",
            status="ok" if delta_events else "warn",
            detail=(
                f"{len(delta_events)} Delta-Events gefunden (source=system/provider/market)."
                if delta_events
                else "Keine [delta:…]-Events — Run evtl. ohne Delta-Events oder ohne Markt-Feedback."
            ),
        )
    )

    booking_delta_ticks = [
        int(row["tick"])
        for row in ticks
        if row.get("booking_rate_delta") not in (None, 0, 0.0)
    ]
    missing_booking_deltas = []
    for tick in booking_delta_ticks:
        has_delta = any(
            event.get("round_number") == tick
            and "[delta:" in str(event.get("description", ""))
            and "booking" in str(event.get("description", "")).lower()
            for event in events
        )
        if not has_delta:
            missing_booking_deltas.append(tick)

    checks.append(
        ConsistencyCheck(
            check_id="booking_delta_events",
            title="Booking-Deltas protokolliert",
            status="warn" if missing_booking_deltas else "ok",
            detail=(
                "Ticks ohne Booking-Delta-Event: " + ", ".join(map(str, missing_booking_deltas[:8]))
                if missing_booking_deltas
                else "Booking-Änderungen sind als Delta-Events sichtbar."
            ),
        )
    )

    checkpoint_dir = base / "checkpoints"
    checkpoint_files = list(checkpoint_dir.rglob("tick_*.json")) if checkpoint_dir.is_dir() else []
    checks.append(
        ConsistencyCheck(
            check_id="checkpoints",
            title="Checkpoints für State Explorer",
            status="ok" if checkpoint_files else "warn",
            detail=(
                f"{len(checkpoint_files)} Checkpoint-Dateien unter checkpoints/."
                if checkpoint_files
                else "Keine Checkpoints — Explorer nutzt nur CSV/JSON-Artefakte."
            ),
        )
    )

    return checks


def launch_simulation(
    config: RunLaunchConfig,
    *,
    repo_root: Path | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> RunLaunchResult:
    """Run one simulation, multi-run batch, or sweep batch and persist outputs."""

    import contextlib
    import sys

    from src.run_simulation import _build_run_args, _save_run_outputs, _write_multi_run_summary
    from src.scenario_sweeps import SWEEP_OUTPUT_DIR, run_all_sweeps

    repo = repo_root or REPO_ROOT

    def _maybe_generate_figures(run_directory: Path) -> None:
        if not config.generate_figures:
            return
        try:
            generate_figures_for_run(run_directory)
            print(f"Figures saved under {run_directory / 'figures'}")
        except Exception as exc:
            print(f"Warning: figure generation failed for {run_directory.name}: {exc}")

    def _build_llm():
        if config.mock_llm:
            return get_llm()
        return OllamaClient(
            OllamaConfig(
                base_url=config.base_url,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
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
            ),
        )

    def _run_body() -> RunLaunchResult:
        if config.run_all_sweeps:
            run_all_sweeps(
                ticks_override=int(config.rounds) if config.rounds else None,
                sweep_filter=config.sweep_id,
                verbose=True,
            )
            summary_path = SWEEP_OUTPUT_DIR / "sweep_summary.json"
            return RunLaunchResult(
                run_id="sweep-batch",
                run_dir=SWEEP_OUTPUT_DIR,
                ticks_completed=config.rounds,
                total_events=0,
                artifacts={"sweep_summary": str(summary_path)},
                sweep_batch=True,
                sweep_summary_path=str(summary_path),
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

            print(f"Starting multi-run: runs={runs}, ticks={base_state.clock.max_ticks}, batch_id={batch_id}")
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
                run_args = _build_run_args(args, run_index=index, seed=run_result.seed)
                artifacts = _save_run_outputs(
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
            _write_multi_run_summary(
                summary_path=summary_path,
                result=multi_result,
                run_artifacts=all_artifacts,
            )

            return RunLaunchResult(
                run_id=child_run_ids[0] if child_run_ids else batch_id,
                run_dir=(batch_dir / child_run_ids[0].split("/", 1)[1]) if child_run_ids else batch_dir,
                ticks_completed=multi_result.runs[-1].ticks_completed if multi_result.runs else 0,
                total_events=total_events,
                artifacts={"multi_run_summary": str(summary_path), **(all_artifacts[0] if all_artifacts else {})},
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
            quiet=False,
            run_id=run_id,
            checkpoint_dir=str(ck_path),
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
            seed = config.seed

        artifacts = _save_run_outputs(
            final_state,
            _build_run_args(args, run_index=1, seed=seed),
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

    with contextlib.redirect_stdout(_StdoutTee()):
        return _run_body()
