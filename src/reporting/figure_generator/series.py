"""Tick-aligned time series extraction from live state, run dirs, and fresh sweep runs."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config_loader import build_initial_state
from src.models.sweep_models import SweepConfig
from src.orchestration.scenario_sweeps import apply_sweep_overrides
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

FACTOR_STATE_PATTERN = re.compile(r"F(\d+)\.(\d+)")


@dataclass
class RunSeries:
    """Tick-aligned time series extracted from a run or sweep."""

    label: str
    run_id: str = ""
    ticks: list[int] = field(default_factory=list)
    booking_rate: list[float] = field(default_factory=list)
    ticket_price: list[float] = field(default_factory=list)
    carbon_tax: list[float] = field(default_factory=list)
    income_index: list[float] = field(default_factory=list)
    saf_mandate: list[float] = field(default_factory=list)
    factor_ticks: list[int] = field(default_factory=list)
    factor_values: dict[str, list[float]] = field(default_factory=dict)
    age_ticks: list[int] = field(default_factory=list)
    age_booking: dict[str, list[float]] = field(default_factory=dict)
    segment_ticks: list[int] = field(default_factory=list)
    segment_booking: dict[str, list[float]] = field(default_factory=dict)


def _factor_state_to_numeric(state_label: str) -> float:
    match = FACTOR_STATE_PATTERN.match(str(state_label))
    if not match:
        return 0.0
    return float(match.group(1)) + float(match.group(2)) * 0.1


def extract_series_from_state(state: Any, *, label: str, run_id: str = "") -> RunSeries:
    series = RunSeries(label=label, run_id=run_id)

    prop_by_tick: dict[int, dict[str, float]] = {}
    for row in state.property_timeseries or []:
        tick = row.get("tick")
        if tick is None:
            continue
        prop_by_tick[int(tick)] = {
            key: float(value)
            for key, value in row.items()
            if key != "tick" and isinstance(value, (int, float))
        }

    for entry in state.price_history or []:
        tick = int(entry.round_number)
        if tick < 1:
            continue
        series.ticks.append(tick)
        if entry.price is not None:
            series.ticket_price.append(float(entry.price))
        booking = entry.booking_rate
        if booking is None:
            booking = entry.demand_level
        if booking is None:
            for stats in state.population_stats or []:
                if stats.get("round_number") == tick:
                    booking = stats.get("total_demand")
                    break
        series.booking_rate.append(float(booking) if booking is not None else float("nan"))

        props = prop_by_tick.get(tick, {})
        series.carbon_tax.append(float(props.get("carbon_tax_level", float("nan"))))
        series.income_index.append(float(props.get("income_index", float("nan"))))
        series.saf_mandate.append(float(props.get("saf_mandate_share", float("nan"))))

    for row in state.factor_timeseries or []:
        tick = row.get("tick")
        if tick is None:
            continue
        tick_int = int(tick)
        if tick_int not in series.factor_ticks:
            series.factor_ticks.append(tick_int)
        for key, value in row.items():
            if key == "tick":
                continue
            series.factor_values.setdefault(str(key), []).append(
                _factor_state_to_numeric(str(value))
            )

    for stats in state.population_stats or []:
        tick = stats.get("round_number")
        if tick is None:
            continue
        tick_int = int(tick)
        if tick_int not in series.age_ticks:
            series.age_ticks.append(tick_int)
        for group, group_stats in (stats.get("age_groups") or {}).items():
            booking = group_stats.get("booking_rate") if isinstance(group_stats, dict) else None
            if booking is None:
                continue
            series.age_booking.setdefault(str(group), []).append(float(booking))

        if tick_int not in series.segment_ticks:
            series.segment_ticks.append(tick_int)
        for group, group_stats in (stats.get("segments") or {}).items():
            booking = group_stats.get("booking_rate") if isinstance(group_stats, dict) else None
            if booking is None:
                continue
            series.segment_booking.setdefault(str(group), []).append(float(booking))

    return series


def extract_series_from_run_dir(run_dir: Path, *, label: str | None = None) -> RunSeries:
    run_dir = Path(run_dir)
    run_id = run_dir.name
    meta_path = run_dir / "run_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    series = RunSeries(label=label or str(meta.get("simulation_name") or run_id), run_id=run_id)

    mechanics_path = run_dir / "tick_mechanics.json"
    if mechanics_path.is_file():
        mechanics = json.loads(mechanics_path.read_text(encoding="utf-8"))
        for row in mechanics.get("ticks") or []:
            tick = int(row["tick"])
            series.ticks.append(tick)
            series.booking_rate.append(float(row.get("booking_rate", float("nan"))))
            series.ticket_price.append(
                float(row.get("market_price_after_feedback_eur", float("nan")))
            )
            series.carbon_tax.append(float(row.get("carbon_tax_level", float("nan"))))
            series.income_index.append(float(row.get("income_index", float("nan"))))

    props_path = run_dir / "timeseries" / "properties.csv"
    if props_path.is_file():
        saf_by_tick: dict[int, float] = {}
        with props_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                saf_by_tick[int(row["tick"])] = float(row.get("saf_mandate_share", float("nan")))
        series.saf_mandate = [saf_by_tick.get(tick, float("nan")) for tick in series.ticks]

    factors_path = run_dir / "timeseries" / "factors.csv"
    if factors_path.is_file():
        with factors_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                tick = int(row["tick"])
                series.factor_ticks.append(tick)
                for key, value in row.items():
                    if key == "tick":
                        continue
                    series.factor_values.setdefault(key, []).append(_factor_state_to_numeric(value))

    age_path = run_dir / "timeseries" / "age_property.csv"
    if age_path.is_file():
        with age_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                tick = int(row["tick"])
                group = str(row["age_group"])
                if tick not in series.age_ticks:
                    series.age_ticks.append(tick)
                series.age_booking.setdefault(group, []).append(float(row["booking_rate"]))

    population_path = run_dir / "timeseries" / "population.csv"
    if population_path.is_file():
        with population_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                tick = int(row["tick"])
                group = str(row["segment_id"])
                if tick not in series.segment_ticks:
                    series.segment_ticks.append(tick)
                series.segment_booking.setdefault(group, []).append(float(row["booking_rate"]))

    return series


def run_deterministic_reference(*, ticks: int = 40, seed: int = 42) -> RunSeries:
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = ticks
    runner = SimulationRunner(
        llm=lambda prompt: "{}",
        options=RunnerOptions(
            enable_market=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )
    final_state = runner.run(state, seed=seed, run_id="figure-reference")
    return extract_series_from_state(
        final_state, label="Referenz (Standard-Config)", run_id="reference"
    )


def run_sweep_series(
    sweep: SweepConfig,
    *,
    ticks: int | None = None,
    seed: int = 42,
) -> tuple[RunSeries, dict[str, Any]]:
    effective_ticks = ticks or sweep.max_ticks
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = effective_ticks
    state = apply_sweep_overrides(state, sweep)
    runner = SimulationRunner(
        llm=lambda prompt: "{}",
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )
    final_state = runner.run(state, seed=seed, run_id=f"sweep-{sweep.id}")
    series = extract_series_from_state(final_state, label=sweep.name, run_id=sweep.id)

    from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
    from src.config_loader import load_cib_frozen

    final_factors = {
        fid: factor.current_state for fid, factor in final_state.environment.factors.items()
    }
    checker = ConsistencyChecker(load_cib_frozen())
    scenario = ScenarioDescriptor(factor_states=final_factors)
    score_row = {
        "sweep_id": sweep.id,
        "sweep_name": sweep.name,
        "ticks_completed": final_state.clock.current_tick,
        "final_factor_states": final_factors,
        "consistency_score": checker.compute_consistency_score(scenario),
        "stability_index": checker.compute_stability_index(scenario),
        "num_conflicts": len(checker.check_scenario(scenario).conflicts),
    }
    return series, score_row
