"""Writers for every artifact a simulation run produces under outputs/<run_id>/."""

from src.reporting.output_writer.cib import save_cib_matrix
from src.reporting.output_writer.events import save_event_log
from src.reporting.output_writer.llm_incidents import save_llm_incidents
from src.reporting.output_writer.metadata import save_run_metadata
from src.reporting.output_writer.narrative import save_final_narrative
from src.reporting.output_writer.paths import (
    OUTPUT_DIR,
    create_run_id,
    ensure_output_dir,
    resolve_run_output_dir,
)
from src.reporting.output_writer.protocol import save_protocol, save_protocol_markdown
from src.reporting.output_writer.scenarios import save_scenarios, save_scenarios_markdown
from src.reporting.output_writer.tick_mechanics import save_tick_mechanics
from src.reporting.output_writer.timeseries import (
    append_individuals_history,
    save_age_property_csv,
    save_factors_timeseries,
    save_population_individuals,
    save_population_timeseries,
    save_price_history,
    save_properties_timeseries,
    save_round_history,
    save_segment_analysis,
)

__all__ = [
    "OUTPUT_DIR",
    "create_run_id",
    "ensure_output_dir",
    "resolve_run_output_dir",
    "save_event_log",
    "save_llm_incidents",
    "save_population_timeseries",
    "save_population_individuals",
    "append_individuals_history",
    "save_factors_timeseries",
    "save_properties_timeseries",
    "save_price_history",
    "save_round_history",
    "save_run_metadata",
    "save_segment_analysis",
    "save_age_property_csv",
    "save_tick_mechanics",
    "save_final_narrative",
    "save_cib_matrix",
    "save_protocol",
    "save_protocol_markdown",
    "save_scenarios",
    "save_scenarios_markdown",
]
