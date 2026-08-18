"""Per-run figure generation: outputs/<run_id>/figures/ + manifest.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.reporting.figure_generator.plots import (
    _ensure_dir,
    plot_age_segments,
    plot_factor_states,
    plot_policy_shock,
    plot_population_distribution,
    plot_price_vs_booking,
    plot_system_dynamics,
)
from src.reporting.figure_generator.series import RunSeries, extract_series_from_run_dir


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
        "Populationsverteilung": plot_population_distribution(
            run_path, figures_dir / "population_distribution.png"
        ),
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
