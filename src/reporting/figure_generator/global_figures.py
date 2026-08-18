"""Global/batch figure generation across sweeps + a deterministic reference run."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.orchestration.scenario_sweeps import SWEEP_OUTPUT_DIR, load_all_sweep_configs
from src.reporting.figure_generator.plots import (
    _ensure_dir,
    plot_age_segments,
    plot_cib_scores,
    plot_factor_states,
    plot_policy_shock,
    plot_price_vs_booking,
    plot_scenario_comparison,
    plot_segment_booking,
    plot_system_dynamics,
)
from src.reporting.figure_generator.series import (
    RunSeries,
    extract_series_from_run_dir,
    run_deterministic_reference,
    run_sweep_series,
)
from src.reporting.figure_generator.sweeps_doc import (
    _save_sweep_timeseries,
    write_scenario_runs_doc,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
# Was docs/challenge4/figures/ before the docs cleanup; that directory no longer
# exists, and its parent (docs/) now holds the hand-maintained scenario_runs.md
# this function's write_scenario_runs_doc() would otherwise overwrite. Runtime
# artifacts belong under outputs/, not docs/.
DEFAULT_FIGURES_DIR = REPO_ROOT / "outputs" / "figures"


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
