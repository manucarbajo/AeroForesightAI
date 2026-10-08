"""LLM run-scenario synthesis from completed run artefacts (grounded)."""

from src.reporting.run_scenario_generator.candidates import build_candidate_constellations
from src.reporting.run_scenario_generator.context import (
    RunScenarioContext,
    load_run_scenario_context,
)
from src.reporting.run_scenario_generator.factors import build_factor_profile
from src.reporting.run_scenario_generator.narrative import build_run_narrative
from src.reporting.run_scenario_generator.pipeline import (
    generate_and_save_run_scenario,
    generate_run_scenario,
    save_run_scenario_artifacts,
    szenario_vorfall,
)
from src.reporting.run_scenario_generator.prompt import (
    build_ground_truth_block,
    build_scenario_prompt,
    validate_scenario_narrative,
)
from src.reporting.run_scenario_generator.rendering import (
    build_run_summary,
    build_template_scenario,
    render_run_scenario_markdown,
)

__all__ = [
    "RunScenarioContext",
    "load_run_scenario_context",
    "build_candidate_constellations",
    "build_factor_profile",
    "build_run_narrative",
    "generate_and_save_run_scenario",
    "generate_run_scenario",
    "save_run_scenario_artifacts",
    "szenario_vorfall",
    "build_ground_truth_block",
    "build_scenario_prompt",
    "validate_scenario_narrative",
    "build_run_summary",
    "build_template_scenario",
    "render_run_scenario_markdown",
]
