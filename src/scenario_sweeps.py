"""Scenario Sweeps — M8 Orchestrator

Runs multiple parameter-sweep scenarios in deterministic-only mode
(no LLM calls) and evaluates the resulting end-states against the
CIB consistency matrix.

Usage:
    python src/scenario_sweeps.py                    # all sweeps in configs/sweeps/
    python src/scenario_sweeps.py --ticks 10000      # benchmark: 10k ticks
    python src/scenario_sweeps.py --sweep co2_delayed.json  # single sweep
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Fix Windows cp1252 encoding for Unicode output
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

SWEEPS_DIR = REPO_ROOT / "configs" / "sweeps"
SWEEP_OUTPUT_DIR = REPO_ROOT / "outputs" / "sweeps"


# ---------------------------------------------------------------------------
# Sweep Config Loading
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# State Override Application
# ---------------------------------------------------------------------------

def apply_sweep_overrides(state: Any, sweep: SweepConfig) -> Any:
    """Apply sweep overrides to an initial SimulationState.

    Modifies the state in-place:
    - Adjusts system property trajectories (baseline + rules)
    - Overrides initial factor states
    - Sets max_ticks from sweep config
    """
    # Override max_ticks
    state.clock.max_ticks = sweep.max_ticks

    # Build lookup for system properties
    prop_lookup: dict[str, Any] = {}
    for prop in state.properties.system_properties:
        prop_lookup[prop.id] = prop

    # Apply property overrides
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
                # Rebuild rules from the override data
                from src.models.property_models import TrajectoryRule
                new_rules = []
                for rule_data in override.rules:
                    new_rules.append(TrajectoryRule.model_validate(rule_data))
                traj.rules = new_rules

    # Apply factor overrides
    for factor_override in sweep.factor_overrides:
        factor = state.environment.factors.get(factor_override.factor_id)
        if factor is not None and factor_override.initial_state in factor.possible_states:
            factor.current_state = factor_override.initial_state

    return state


# ---------------------------------------------------------------------------
# Milestone Evaluation
# ---------------------------------------------------------------------------

def evaluate_milestones(
    state: Any,
    milestones: list[MilestoneCheck],
    tick: int,
) -> list[dict[str, Any]]:
    """Evaluate milestones that are due at this tick."""
    results: list[dict[str, Any]] = []

    for ms in milestones:
        if ms.tick != tick:
            continue

        result: dict[str, Any] = {
            "tick": ms.tick,
            "description": ms.description,
            "passed": False,
            "actual_value": None,
        }

        if ms.check_property:
            # Find property value in market_metrics or resolved properties
            actual = state.market_metrics.get(ms.check_property)
            if actual is None:
                # Try to find in properties timeseries
                for ts_row in reversed(state.property_timeseries):
                    if ms.check_property in ts_row:
                        actual = ts_row[ms.check_property]
                        break

            result["actual_value"] = actual
            if ms.expected_value is not None and actual is not None:
                result["passed"] = abs(float(actual) - float(ms.expected_value)) < 0.01
            elif actual is not None:
                result["passed"] = True  # Just checking existence

        if ms.check_factor:
            factor = state.environment.factors.get(ms.check_factor)
            if factor is not None:
                result["actual_value"] = factor.current_state
                result["passed"] = True  # Record the factor state

        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Single Sweep Execution
# ---------------------------------------------------------------------------

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
    final_state = runner.run(
        state,
        seed=42,
        run_id=f"sweep-{sweep.id}",
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

    # Evaluate milestones across all ticks
    # Since we don't have per-tick access in the final state, we evaluate
    # milestones against the final state only (for check_factor especially)
    milestone_results: list[dict[str, Any]] = []

    # For property-based milestones, we can check the property_timeseries
    for ms in sweep.milestones:
        result: dict[str, Any] = {
            "tick": ms.tick,
            "description": ms.description,
            "passed": False,
            "actual_value": None,
        }

        if ms.check_property:
            # Search timeseries for the value at the milestone tick
            for ts_row in final_state.property_timeseries:
                ts_tick = ts_row.get("tick")
                if ts_tick == ms.tick and ms.check_property in ts_row:
                    result["actual_value"] = ts_row[ms.check_property]
                    if ms.expected_value is not None:
                        result["passed"] = abs(
                            float(ts_row[ms.check_property]) - float(ms.expected_value)
                        ) < 0.5
                    else:
                        result["passed"] = True
                    break

        if ms.check_factor:
            # For factor milestones, check factor_timeseries
            for ts_row in final_state.factor_timeseries:
                ts_tick = ts_row.get("tick")
                if ts_tick == ms.tick and ms.check_factor in ts_row:
                    result["actual_value"] = ts_row[ms.check_factor]
                    result["passed"] = True
                    break

        milestone_results.append(result)

    # CIB Consistency Scoring
    cib_matrix = load_cib_frozen()
    checker = ConsistencyChecker(cib_matrix)
    scenario = ScenarioDescriptor(factor_states=final_factors)
    consistency_score = checker.compute_consistency_score(scenario)
    stability_index = checker.compute_stability_index(scenario)
    check_result = checker.check_scenario(scenario)

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


# ---------------------------------------------------------------------------
# Batch Execution
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

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
