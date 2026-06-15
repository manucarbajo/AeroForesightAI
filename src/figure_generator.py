"""Generate Challenge-4 scenario figures from simulation runs and sweeps."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config_loader import build_initial_state
from src.models.sweep_models import SweepConfig
from src.output_writer import OUTPUT_DIR
from src.scenario_sweeps import (
    SWEEP_OUTPUT_DIR,
    apply_sweep_overrides,
    load_all_sweep_configs,
)
from src.simulation_runner import RunnerOptions, SimulationRunner

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIGURES_DIR = REPO_ROOT / "docs" / "challenge4" / "figures"

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
            series.factor_values.setdefault(str(key), []).append(_factor_state_to_numeric(str(value)))

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
            series.ticket_price.append(float(row.get("market_price_after_feedback_eur", float("nan"))))
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
    return extract_series_from_state(final_state, label="Referenz (Standard-Config)", run_id="reference")


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

    from src.config_loader import load_cib_frozen
    from src.scenario_consistency import ConsistencyChecker, ScenarioDescriptor

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


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    _ensure_dir(path.parent)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_scenario_comparison(series_list: list[RunSeries], output_path: Path, *, metric: str) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    for series in series_list:
        if metric == "booking":
            y = series.booking_rate
            ylabel = "Booking Rate"
            title = "Szenario-Vergleich: Booking Rate"
        else:
            y = series.ticket_price
            ylabel = "Ticketpreis (EUR)"
            title = "Szenario-Vergleich: Ticketpreis"
        ax.plot(series.ticks, y, marker=".", linewidth=1.8, label=series.label)
    ax.set_xlabel("Tick")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    return _save_figure(fig, output_path)


def plot_age_segments(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if series.age_booking:
        for group, rates in series.age_booking.items():
            ax.plot(series.age_ticks[: len(rates)], rates, label=group, marker="o")
    ax.set_title(f"Buchungsrate nach Altersgruppe: {series.label}")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Buchungsrate")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    return _save_figure(fig, output_path)

def plot_segment_booking(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if series.segment_booking:
        for group, rates in series.segment_booking.items():
            ax.plot(series.segment_ticks[: len(rates)], rates, label=group.replace("_", " ").title(), marker="s")
    ax.set_title(f"Buchungsrate nach Segment: {series.label}")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Buchungsrate")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    return _save_figure(fig, output_path)


def plot_cib_scores(scores: list[dict[str, Any]], output_path: Path) -> Path:
    names = [row["sweep_name"] for row in scores]
    values = [float(row["consistency_score"]) for row in scores]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(names, values, color="#2563eb")
    ax.set_xlabel("CIB Consistency Score")
    ax.set_title("Szenario-Plausibilität (CIB Consistency)")
    ax.set_xlim(0, max(values) * 1.15 if values else 1)
    for bar, value in zip(bars, values):
        ax.text(value + 0.005, bar.get_y() + bar.get_height() / 2, f"{value:.3f}", va="center", fontsize=8)
    ax.grid(True, axis="x", alpha=0.3)
    return _save_figure(fig, output_path)


def plot_price_vs_booking(series: RunSeries, output_path: Path) -> Path:
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(series.ticks, series.ticket_price, color="#059669", marker="o", label="Ticketpreis")
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Ticketpreis (EUR)", color="#059669")
    ax1.tick_params(axis="y", labelcolor="#059669")
    ax2 = ax1.twinx()
    ax2.plot(series.ticks, series.booking_rate, color="#2563eb", marker="s", label="Booking Rate")
    ax2.set_ylabel("Booking Rate", color="#2563eb")
    ax2.tick_params(axis="y", labelcolor="#2563eb")
    ax2.set_ylim(0, 1)
    ax1.set_title(f"Markt-Rückkopplung: Preis und Booking ({series.label})")
    ax1.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_policy_shock(series: RunSeries, output_path: Path, shock_ticks: tuple[int, ...] = (15, 30)) -> Path:
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(series.ticks, series.carbon_tax, color="#dc2626", marker="o", label="CO₂-Steuer")
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("CO₂-Steuer (EUR/t)", color="#dc2626")
    ax1.tick_params(axis="y", labelcolor="#dc2626")
    for tick in shock_ticks:
        ax1.axvline(tick, color="#dc2626", linestyle="--", alpha=0.45, linewidth=1)
    ax2 = ax1.twinx()
    ax2.plot(series.ticks, series.booking_rate, color="#2563eb", marker="s", label="Booking Rate")
    ax2.set_ylabel("Booking Rate", color="#2563eb")
    ax2.tick_params(axis="y", labelcolor="#2563eb")
    ax2.set_ylim(0, 1)
    ax1.set_title(f"Policy-Shock: CO₂-Steuer und Booking ({series.label})")
    ax1.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_system_dynamics(series: RunSeries, output_path: Path) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    axes[0].plot(series.ticks, series.booking_rate, color="#2563eb", marker="o", label="Booking Rate")
    axes[0].set_ylabel("Booking Rate")
    axes[0].set_ylim(0, 1)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(f"Systemdynamik: Booking und Properties ({series.label})")

    axes[1].plot(series.ticks, series.carbon_tax, label="CO₂-Steuer", linewidth=1.8)
    if any(v == v for v in series.income_index):
        axes[1].plot(series.ticks, series.income_index, label="Einkommensindex", linewidth=1.8)
    if series.saf_mandate and any(v == v for v in series.saf_mandate):
        axes[1].plot(series.ticks, series.saf_mandate, label="SAF-Mandat", linewidth=1.8)
    axes[1].set_xlabel("Tick")
    axes[1].set_ylabel("Property-Wert")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_age_segments(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if not series.age_booking:
        ax.text(0.5, 0.5, "Keine Alterssegment-Daten", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    for group, values in sorted(series.age_booking.items()):
        ticks = series.age_ticks[: len(values)]
        ax.plot(ticks, values, marker="o", linewidth=1.5, label=group)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Booking Rate")
    ax.set_ylim(0, 1)
    ax.set_title(f"Booking nach Altersgruppe ({series.label})")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_factor_states(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if not series.factor_values:
        ax.text(0.5, 0.5, "Keine Faktor-Zeitreihen", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    for factor_id, values in sorted(series.factor_values.items()):
        ticks = series.factor_ticks[: len(values)]
        ax.step(ticks, values, where="post", linewidth=1.8, label=factor_id)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Faktor-Zustand (numerisch)")
    ax.set_title(f"Faktor-Zustände über Zeit ({series.label})")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def _save_sweep_timeseries(series: RunSeries, output_dir: Path) -> Path:
    payload = {
        "sweep_id": series.run_id,
        "label": series.label,
        "ticks": series.ticks,
        "booking_rate": series.booking_rate,
        "ticket_price": series.ticket_price,
        "carbon_tax": series.carbon_tax,
    }
    path = output_dir / f"{series.run_id}_timeseries.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_scenario_runs_doc(
    *,
    output_path: Path,
    figure_paths: dict[str, Path],
    sweep_series: list[RunSeries],
    reference: RunSeries,
    scores: list[dict[str, Any]],
) -> Path:
    lines = [
        "# Szenario-Läufe und Figures (M10)",
        "",
        "Automatisch erzeugte Visualisierungen für Strategic Foresight / Challenge 4.",
        "",
        "## Foresight-Szenarien (deterministisch, 50 Ticks)",
        "",
        "| Szenario | ID | Consistency |",
        "| --- | --- | --- |",
    ]
    score_by_id = {row["sweep_id"]: row for row in scores}
    for series in sweep_series:
        score = score_by_id.get(series.run_id, {})
        consistency = score.get("consistency_score", "—")
        if isinstance(consistency, float):
            consistency = f"{consistency:.3f}"
        lines.append(f"| {series.label} | `{series.run_id}` | {consistency} |")

    lines.extend(
        [
            "",
            f"## Referenzlauf ({reference.label})",
            "",
            f"- Ticks: {len(reference.ticks)}",
            f"- Booking: {reference.booking_rate[0]:.1%} → {reference.booking_rate[-1]:.1%}"
            if reference.booking_rate
            else "- Booking: —",
            "",
            "## Figures",
            "",
        ]
    )
    for title, path in figure_paths.items():
        rel = path.relative_to(output_path.parent) if path.is_relative_to(output_path.parent) else path.name
        lines.append(f"- **{title}:** `{rel}`")

    lines.extend(
        [
            "",
            "## Erzeugung",
            "",
            "```powershell",
            "python -m src.figure_generator",
            "```",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


@dataclass(frozen=True)
class RunFigureGenerationResult:
    figure_paths: dict[str, Path]
    run_dir: Path


def _detect_policy_shock_ticks(series: RunSeries) -> tuple[int, ...]:
    shocks: list[int] = []
    previous: float | None = None
    for tick, value in zip(series.ticks, series.carbon_tax, strict=False):
        if previous is not None and value == value and value != previous:
            shocks.append(int(tick))
        previous = value
    return tuple(shocks) if shocks else (15, 30)


def plot_population_distribution(run_path: Path, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))
    pop_csv = run_path / "population.csv"
    if not pop_csv.is_file():
        ax.text(0.5, 0.5, "Keine Populationsdaten", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    try:
        import pandas as pd
        df = pd.read_csv(pop_csv)
        
        # Color by segment
        if "business" in df.columns:
            # Pandas might read booleans as strings depending on format
            is_business = df["business"].astype(str).str.lower().isin(["true", "1"])
            colors = is_business.map({True: "#1f77b4", False: "#ff7f0e"}) # Blue/Orange
            # Create dummy lines for legend
            ax.scatter([], [], c="#1f77b4", label="Business")
            ax.scatter([], [], c="#ff7f0e", label="Leisure")
            ax.legend()
        else:
            colors = "#1f77b4"
            
        # Optional: scale marker size by income
        sizes = 20
        if "income_factor" in df.columns:
            sizes = df["income_factor"].astype(float) * 20

        ax.scatter(df["wtp_eur"], df["environmental_awareness"], c=colors, s=sizes, alpha=0.6, edgecolors="none")
        ax.set_xlabel("Zahlungsbereitschaft (WTP in €)")
        ax.set_ylabel("Umweltbewusstsein (0-1)")
        ax.set_title("Agenten-Verteilung: Umweltbewusstsein vs. WTP")
        ax.grid(True, alpha=0.3)
    except Exception as e:
        ax.text(0.5, 0.5, f"Fehler:\n{str(e)}", ha="center", va="center")
        ax.set_axis_off()
        
    return _save_figure(fig, output_path)


def generate_run_figures(run_dir: Path | str) -> RunFigureGenerationResult:
    """Generate per-run PNG figures under ``outputs/<run_id>/figures/``."""

    run_path = Path(run_dir)
    if not run_path.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_path}")

    series = extract_series_from_run_dir(run_path)
    figures_dir = _ensure_dir(run_path / "figures")
    shock_ticks = _detect_policy_shock_ticks(series)

    figure_paths: dict[str, Path] = {
        "Preis vs. Booking": plot_price_vs_booking(series, figures_dir / "price_vs_booking.png"),
        "CO₂-Policy-Shock": plot_policy_shock(
            series, figures_dir / "policy_shock_co2_booking.png", shock_ticks=shock_ticks
        ),
        "Systemdynamik": plot_system_dynamics(series, figures_dir / "system_dynamics.png"),
        "Faktor-Zustände": plot_factor_states(series, figures_dir / "factor_states.png"),
        "Alterssegmente": plot_age_segments(series, figures_dir / "age_segment_booking.png"),
        "Populationsverteilung": plot_population_distribution(run_path, figures_dir / "population_distribution.png"),
    }

    manifest = {
        "run_id": run_path.name,
        "figures": {title: path.name for title, path in figure_paths.items()},
    }
    (figures_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return RunFigureGenerationResult(figure_paths=figure_paths, run_dir=run_path)


@dataclass(frozen=True)
class FigureGenerationResult:
    figure_paths: dict[str, Path]
    sweep_series: list[RunSeries]
    reference_series: RunSeries
    scenario_scores: list[dict[str, Any]]


def generate_all_figures(
    *,
    output_dir: Path | str | None = None,
    reference_run_dir: Path | str | None = None,
    reference_ticks: int = 40,
    sweep_ticks: int = 50,
    run_sweeps: bool = True,
) -> FigureGenerationResult:
    figures_dir = _ensure_dir(Path(output_dir or DEFAULT_FIGURES_DIR))
    sweep_out = _ensure_dir(SWEEP_OUTPUT_DIR)

    if reference_run_dir:
        reference = extract_series_from_run_dir(Path(reference_run_dir))
    else:
        reference = run_deterministic_reference(ticks=reference_ticks)

    sweep_series: list[RunSeries] = []
    scores: list[dict[str, Any]] = []

    if run_sweeps:
        for sweep in load_all_sweep_configs():
            series, score_row = run_sweep_series(sweep, ticks=sweep_ticks)
            sweep_series.append(series)
            scores.append(score_row)
            _save_sweep_timeseries(series, sweep_out)
        scores_path = sweep_out / "scenario_scores.json"
        scores_path.write_text(json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8")

    figure_paths: dict[str, Path] = {}

    if sweep_series:
        figure_paths["Szenario-Vergleich Booking"] = plot_scenario_comparison(
            sweep_series, figures_dir / "scenario_comparison_booking.png", metric="booking"
        )
        figure_paths["Szenario-Vergleich Preis"] = plot_scenario_comparison(
            sweep_series, figures_dir / "scenario_comparison_price.png", metric="price"
        )
    if scores:
        figure_paths["CIB Consistency Scores"] = plot_cib_scores(
            scores, figures_dir / "scenario_cib_scores.png"
        )

    figure_paths["Preis vs. Booking"] = plot_price_vs_booking(
        reference, figures_dir / "price_vs_booking.png"
    )
    figure_paths["CO₂-Policy-Shock"] = plot_policy_shock(
        reference, figures_dir / "policy_shock_co2_booking.png"
    )
    figure_paths["Systemdynamik"] = plot_system_dynamics(
        reference, figures_dir / "system_dynamics.png"
    )
    figure_paths["Faktor-Zustände"] = plot_factor_states(
        reference, figures_dir / "factor_states.png"
    )
    figure_paths["Alterssegmente"] = plot_age_segments(
        reference, figures_dir / "age_segment_booking.png"
    )
    figure_paths["Buchung nach Segment"] = plot_segment_booking(
        reference, figures_dir / "market_segment_booking.png"
    )

    write_scenario_runs_doc(
        output_path=figures_dir.parent / "scenario_runs.md",
        figure_paths=figure_paths,
        sweep_series=sweep_series,
        reference=reference,
        scores=scores,
    )

    return FigureGenerationResult(
        figure_paths=figure_paths,
        sweep_series=sweep_series,
        reference_series=reference,
        scenario_scores=scores,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Challenge-4 scenario figures (M10).")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_FIGURES_DIR),
        help="Directory for PNG outputs.",
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        default=None,
        help="Use an existing outputs/<run_id>/ directory as reference run.",
    )
    parser.add_argument("--reference-ticks", type=int, default=40, help="Ticks for synthetic reference run.")
    parser.add_argument("--sweep-ticks", type=int, default=50, help="Ticks per Foresight sweep.")
    parser.add_argument(
        "--run-only",
        type=str,
        default=None,
        metavar="RUN_DIR",
        help="Only generate per-run figures into outputs/<run_id>/figures/ (no global sweep batch).",
    )
    parser.add_argument(
        "--skip-sweeps",
        action="store_true",
        help="Skip sweep re-run (use only reference run figures).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.run_only:
        run_dir = args.run_only
        if not Path(run_dir).is_absolute():
            candidate = Path(OUTPUT_DIR) / run_dir
            run_dir = str(candidate if candidate.is_dir() else Path(run_dir))
        result = generate_run_figures(run_dir)
        print(f"Generated {len(result.figure_paths)} run figures in {result.run_dir / 'figures'}")
        for title, path in result.figure_paths.items():
            print(f"  - {title}: {path}")
        return 0

    run_dir = args.run_dir
    if run_dir and not Path(run_dir).is_absolute():
        candidate = Path(OUTPUT_DIR) / run_dir
        run_dir = str(candidate if candidate.is_dir() else Path(run_dir))

    result = generate_all_figures(
        output_dir=args.output_dir,
        reference_run_dir=run_dir,
        reference_ticks=args.reference_ticks,
        sweep_ticks=args.sweep_ticks,
        run_sweeps=not args.skip_sweeps,
    )
    print(f"Generated {len(result.figure_paths)} figures in {args.output_dir}")
    for title, path in result.figure_paths.items():
        print(f"  - {title}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
