"""Scenario sweeps: runs parameter-sweep scenarios in deterministic mode
and evaluates end-states against the CIB consistency matrix.

CLI usage:
    python src/scenario_sweeps.py                           # all sweeps in configs/sweeps/
    python src/scenario_sweeps.py --ticks 10000             # 10k-tick benchmark
    python src/scenario_sweeps.py --sweep co2_delayed.json  # single sweep
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config_loader import build_initial_state, load_cib_frozen
from src.models.sweep_models import (
    MilestoneCheck,
    SweepConfig,
    SweepResult,
    SweepSummary,
)
from src.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
from src.simulation_runner import RunnerOptions, SimulationRunner
from src.output_writer import (
    resolve_run_output_dir,
    save_cib_matrix,
    save_event_log,
    save_final_narrative,
    save_tick_mechanics,
    save_properties_timeseries,
    save_population_timeseries,
    save_factors_timeseries,
    save_round_history,
    save_run_metadata,
    save_price_history,
    save_segment_analysis,
)
from src.run_scenario_generator import generate_and_save_run_scenario
from src.llm_client import OllamaClient, OllamaConfig

SWEEPS_DIR = REPO_ROOT / "configs" / "sweeps"
SWEEP_OUTPUT_DIR = REPO_ROOT / "outputs" / "sweeps"




def load_sweep_config(path: Path) -> SweepConfig:
    """Load a single sweep configuration from a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return SweepConfig.model_validate(data)


def load_all_sweep_configs(directory: Path | None = None) -> list[SweepConfig]:
    """Load all sweep configs from a directory."""
    directory = directory or SWEEPS_DIR
    configs: list[SweepConfig] = []
    for path in sorted(directory.glob("*.json")):
        configs.append(load_sweep_config(path))
    return configs




def apply_sweep_overrides(state: Any, sweep: SweepConfig) -> Any:
    """Apply sweep overrides to an initial SimulationState.

    Modifies the state in-place:
    - Adjusts system property trajectories (baseline + rules)
    - Overrides initial factor states
    - Sets max_ticks from sweep config
    """
    state.clock.max_ticks = sweep.max_ticks

    prop_lookup: dict[str, Any] = {}
    for prop in state.properties.system_properties:
        prop_lookup[prop.id] = prop

    for override in sweep.property_overrides:
        prop = prop_lookup.get(override.property_id)
        if prop is None:
            continue
        traj = prop.trajectory
        if traj is None:
            continue

        if override.baseline is not None:
            if hasattr(traj, "baseline"):
                traj.baseline = override.baseline

        if override.rules is not None:
            if hasattr(traj, "rules"):
                from src.models.property_models import TrajectoryRule
                new_rules = []
                for rule_data in override.rules:
                    new_rules.append(TrajectoryRule.model_validate(rule_data))
                traj.rules = new_rules

    for factor_override in sweep.factor_overrides:
        factor = state.environment.factors.get(factor_override.factor_id)
        if factor is not None and factor_override.initial_state in factor.possible_states:
            factor.current_state = factor_override.initial_state

    if sweep.base_price is not None:
        state.properties.price_model.base_price = sweep.base_price

    return state




def _property_at_tick(state: Any, tick: int, property_id: str) -> Any:
    for ts_row in state.property_timeseries:
        if ts_row.get("tick") == tick and property_id in ts_row:
            return ts_row[property_id]
    return state.market_metrics.get(property_id)


def _factor_at_tick(state: Any, tick: int, factor_id: str) -> str | None:
    for ts_row in state.factor_timeseries:
        if ts_row.get("tick") == tick and factor_id in ts_row:
            return str(ts_row[factor_id])
    factor = state.environment.factors.get(factor_id)
    if factor is not None and state.clock.current_tick == tick:
        return factor.current_state
    return None


def evaluate_milestone_on_state(state: Any, ms: MilestoneCheck) -> dict[str, Any]:
    """Evaluate one milestone against a completed simulation state."""
    result: dict[str, Any] = {
        "tick": ms.tick,
        "description": ms.description,
        "passed": False,
        "actual_value": None,
    }

    if ms.check_property:
        actual = _property_at_tick(state, ms.tick, ms.check_property)
        result["actual_value"] = actual
        if actual is not None:
            if ms.expected_value is not None:
                tolerance = 0.5 if ms.check_property == "income_index" else 0.01
                result["passed"] = abs(float(actual) - float(ms.expected_value)) <= tolerance
            else:
                result["passed"] = True

    if ms.check_factor:
        actual = _factor_at_tick(state, ms.tick, ms.check_factor)
        result["actual_value"] = actual
        if actual is not None:
            if ms.expected_factor_state is not None:
                result["passed"] = actual == ms.expected_factor_state
            else:
                result["passed"] = True

    return result


def evaluate_milestones(
    state: Any,
    milestones: list[MilestoneCheck],
    tick: int,
) -> list[dict[str, Any]]:
    """Evaluate milestones that are due at this tick."""
    return [
        evaluate_milestone_on_state(state, ms)
        for ms in milestones
        if ms.tick == tick
    ]




def run_single_sweep(
    sweep: SweepConfig,
    *,
    ticks_override: int | None = None,
    verbose: bool = True,
) -> SweepResult:
    """Execute a single sweep in deterministic-only mode."""

    if verbose:
        print(f"\n{'='*60}")
        print(f"Sweep: {sweep.name} ({sweep.id})")
        print(f"  {sweep.description[:80]}...")
        print(f"{'='*60}")

    effective_ticks = ticks_override or sweep.max_ticks

    # Build initial state
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = effective_ticks

    # Apply sweep overrides
    state = apply_sweep_overrides(state, sweep)
    if ticks_override:
        state.clock.max_ticks = ticks_override

    # Create a dummy LLM (never called in deterministic mode)
    dummy_llm = lambda prompt: "{}"

    runner = SimulationRunner(
        llm=dummy_llm,
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,  # no checkpoints for sweeps
            verbose_ticks=False,
        ),
    )

    start_time = time.time()
    run_id_str = f"sweeps/sweep_{sweep.id}"
    final_state = runner.run(
        state,
        seed=42,
        run_id=run_id_str,
    )
    elapsed = time.time() - start_time

    # Collect final factor states
    final_factors = {
        fid: factor.current_state
        for fid, factor in final_state.environment.factors.items()
    }

    # Collect final property values
    final_props: dict[str, float] = {}
    for key, value in final_state.market_metrics.items():
        if isinstance(value, (int, float)):
            final_props[key] = float(value)

    milestone_results = [
        evaluate_milestone_on_state(final_state, ms) for ms in sweep.milestones
    ]

    # CIB Consistency Scoring
    cib_matrix = load_cib_frozen()
    checker = ConsistencyChecker(cib_matrix)
    scenario = ScenarioDescriptor(factor_states=final_factors)
    consistency_score = checker.compute_consistency_score(scenario)
    stability_index = checker.compute_stability_index(scenario)
    check_result = checker.check_scenario(scenario)
    
    # Save artifacts like a normal run
    run_dir_path = resolve_run_output_dir(run_id_str)
    
    # We need a dummy args namespace for save_run_metadata
    from types import SimpleNamespace
    dummy_args = SimpleNamespace(
        sweep=sweep.id, 
        deterministic_only=True, 
        seed=42,
        model="dummy_for_sweeps",
        base_url="dummy",
        temperature=0.0,
        max_tokens=0,
        no_market=False
    )
    
    save_run_metadata(final_state, dummy_args, run_dir=run_dir_path, run_id=run_id_str)
    save_event_log(final_state.event_log, run_dir=run_dir_path)
    save_tick_mechanics(final_state, run_dir=run_dir_path)
    save_properties_timeseries(final_state.property_timeseries, run_dir=run_dir_path)
    save_population_timeseries(final_state.population_stats, run_dir=run_dir_path)
    save_factors_timeseries(final_state.factor_timeseries, run_dir=run_dir_path)
    save_round_history(final_state.round_results, run_dir=run_dir_path)
    save_price_history(final_state.price_history, run_dir=run_dir_path)
    save_segment_analysis(final_state.round_results, run_dir=run_dir_path)
    save_final_narrative(final_state, run_dir=run_dir_path)
    
    if final_state.cib_matrix is not None:
        if final_state.cib_matrix.metadata is None:
            final_state.cib_matrix.metadata = {}
        final_state.cib_matrix.metadata["consistency_score"] = consistency_score
    save_cib_matrix(final_state, run_dir=run_dir_path)

    # Generate LLM Scenario
    llm = OllamaClient(OllamaConfig())
    generate_and_save_run_scenario(
        run_id_str,
        llm,
        run_dir=run_dir_path,
        prefer_llm=True, # Always prefer LLM for the final scenario text
    )

    try:
        from src.figure_generator import generate_run_figures

        generate_run_figures(run_dir_path)
        if verbose:
            print(f"  Figures saved under {run_dir_path / 'figures'}")
    except Exception as exc:
        if verbose:
            print(f"  Warning: figure generation failed: {exc}")

    if verbose:
        ticks_done = final_state.clock.current_tick
        print(f"  Completed {ticks_done} ticks in {elapsed:.2f}s "
              f"({ticks_done / elapsed:.0f} ticks/sec)")
        print(f"  Final factors: {final_factors}")
        print(f"  CIB consistency: {consistency_score:.3f}, stability: {stability_index:.3f}")
        if check_result.conflicts:
            print(f"  Conflicts ({len(check_result.conflicts)}):")
            for c in check_result.conflicts[:5]:
                print(f"    - {c.encode('ascii', 'replace').decode()}")
        ms_passed = sum(1 for m in milestone_results if m["passed"])
        print(f"  Milestones: {ms_passed}/{len(milestone_results)} passed")
        for m in milestone_results:
            status = "OK" if m["passed"] else "FAIL"
            desc = m["description"].encode("ascii", "replace").decode()
            print(f"    [{status}] Tick {m['tick']}: {desc} "
                  f"(actual={m['actual_value']})")

    return SweepResult(
        sweep_id=sweep.id,
        sweep_name=sweep.name,
        ticks_completed=final_state.clock.current_tick,
        final_factor_states=final_factors,
        final_properties=final_props,
        consistency_score=consistency_score,
        stability_index=stability_index,
        conflicts=check_result.conflicts,
        milestone_results=milestone_results,
    )




def run_all_sweeps(
    *,
    ticks_override: int | None = None,
    sweep_filter: str | None = None,
    verbose: bool = True,
) -> SweepSummary:
    """Run all sweep configs and produce a summary."""

    configs = load_all_sweep_configs()
    if sweep_filter:
        configs = [c for c in configs if c.id == sweep_filter or sweep_filter in c.id]

    if not configs:
        print("No sweep configs found.")
        return SweepSummary()

    results: list[SweepResult] = []
    total_start = time.time()

    for config in configs:
        result = run_single_sweep(
            config,
            ticks_override=ticks_override,
            verbose=verbose,
        )
        results.append(result)

    total_elapsed = time.time() - total_start

    summary = SweepSummary(
        total_sweeps=len(results),
        results=results,
        metadata={
            "total_elapsed_seconds": round(total_elapsed, 2),
            "ticks_override": ticks_override,
            "sweep_ids": [r.sweep_id for r in results],
        },
    )

    # Save outputs
    _save_sweep_outputs(summary)

    if verbose:
        print(f"\n{'='*60}")
        print(f"SWEEP SUMMARY")
        print(f"{'='*60}")
        print(f"Total sweeps: {len(results)}")
        print(f"Total time: {total_elapsed:.2f}s")
        print(f"\nConsistency ranking:")
        for r in sorted(results, key=lambda x: x.consistency_score, reverse=True):
            print(f"  {r.sweep_name:40s}  "
                  f"consistency={r.consistency_score:.3f}  "
                  f"stability={r.stability_index:.3f}  "
                  f"conflicts={len(r.conflicts)}")

    return summary


def _save_sweep_outputs(summary: SweepSummary) -> None:
    """Save sweep results to JSON files."""
    SWEEP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # sweep_summary.json
    summary_path = SWEEP_OUTPUT_DIR / "sweep_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2, ensure_ascii=False, default=str)
    print(f"\nSaved: {summary_path}")

    # scenario_scores.json — focused view on CIB scores
    scores = []
    for r in summary.results:
        scores.append({
            "sweep_id": r.sweep_id,
            "sweep_name": r.sweep_name,
            "ticks_completed": r.ticks_completed,
            "final_factor_states": r.final_factor_states,
            "consistency_score": r.consistency_score,
            "stability_index": r.stability_index,
            "num_conflicts": len(r.conflicts),
            "conflicts": r.conflicts,
        })
    scores_path = SWEEP_OUTPUT_DIR / "scenario_scores.json"
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {scores_path}")




def main() -> None:
    parser = argparse.ArgumentParser(description="Run parameter-sweep scenarios (M8)")
    parser.add_argument(
        "--ticks", type=int, default=None,
        help="Override tick count for all sweeps (e.g. 10000 for benchmark).",
    )
    parser.add_argument(
        "--sweep", type=str, default=None,
        help="Run only the sweep with this ID (e.g. 'co2_delayed').",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Reduce output.",
    )
    args = parser.parse_args()

    summary = run_all_sweeps(
        ticks_override=args.ticks,
        sweep_filter=args.sweep,
        verbose=not args.quiet,
    )

    if not summary.results:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
