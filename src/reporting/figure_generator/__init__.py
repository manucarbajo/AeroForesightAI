"""Matplotlib figure generation for simulation runs and sweeps."""

from src.reporting.figure_generator.global_figures import (
    DEFAULT_FIGURES_DIR,
    FigureGenerationResult,
    generate_all_figures,
)
from src.reporting.figure_generator.plots import (
    plot_age_segments,
    plot_cib_scores,
    plot_factor_states,
    plot_policy_shock,
    plot_population_distribution,
    plot_price_vs_booking,
    plot_scenario_comparison,
    plot_segment_booking,
    plot_system_dynamics,
)
from src.reporting.figure_generator.run_figures import (
    RunFigureGenerationResult,
    generate_run_figures,
)
from src.reporting.figure_generator.series import (
    RunSeries,
    extract_series_from_run_dir,
    extract_series_from_state,
    run_deterministic_reference,
    run_sweep_series,
)

__all__ = [
    "DEFAULT_FIGURES_DIR",
    "FigureGenerationResult",
    "generate_all_figures",
    "plot_age_segments",
    "plot_cib_scores",
    "plot_factor_states",
    "plot_policy_shock",
    "plot_population_distribution",
    "plot_price_vs_booking",
    "plot_scenario_comparison",
    "plot_segment_booking",
    "plot_system_dynamics",
    "RunFigureGenerationResult",
    "generate_run_figures",
    "RunSeries",
    "extract_series_from_run_dir",
    "extract_series_from_state",
    "run_deterministic_reference",
    "run_sweep_series",
]
