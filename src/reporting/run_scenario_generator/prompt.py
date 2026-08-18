"""LLM scenario prompt construction and grounding validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.reporting.run_scenario_generator.candidates import build_candidate_constellations
from src.reporting.run_scenario_generator.context import (
    RunScenarioContext,
    _booking_trend,
    _cib_score,
    _price_trend,
    _safe_float,
)
from src.reporting.run_scenario_generator.factors import _load_factor_catalog, build_factor_profile

RUN_SCENARIO_MARKER = "RUN_SCENARIO_GENERATOR"


def build_scenario_prompt(context: RunScenarioContext) -> str:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    candidates = build_candidate_constellations(context, factor_profile, catalog)

    # Expose the candidate constellations the LLM may select from. The LLM picks
    # by candidate_id; factor states stay Python-owned (grounding/reproducibility).
    clean_candidates = []
    for sc in candidates:
        clean_candidates.append(
            {
                "candidate_id": sc.get("candidate_id"),
                "scenario_kind": sc.get("scenario_kind"),
                "consistency_score": sc.get("consistency_score"),
                "plausibility": sc.get("plausibility"),
                "factor_constellation": sc.get("factor_constellation"),
                "delta_from_end": sc.get("delta_from_end"),
                "tick_grounding": sc.get("tick_grounding"),
            }
        )

    payload = {
        "run_id": context.run_id,
        "metadata": context.metadata,
        "summary_metrics": context.summary_metrics,
        "factor_profile": factor_profile,
        "phase_ticks": context.phase_ticks,
        "events_sample": context.event_log[-12:],
        "segment_booking_end": context.summary_metrics.get("segment_booking_end"),
        "cib_consistency_score": _cib_score(context),
        "booking_trend": _booking_trend(context.summary_metrics),
        "price_trend": _price_trend(context.summary_metrics),
        "candidate_scenarios": clean_candidates,
        "agent_digest": context.agent_digest,
    }

    prompt_path = Path("src/prompts/run_scenario.md")
    if prompt_path.exists():
        prompt_template = prompt_path.read_text(encoding="utf-8")
    else:
        # Fallback if file is missing
        prompt_template = "Bitte erstelle 3 Szenarien. Lese die Daten aus RUN CONTEXT.\n"

    return f"{RUN_SCENARIO_MARKER}\n\nRUN CONTEXT (Ground Truth):\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```\n\n{prompt_template}\n"


def _extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None

    def _clean_json(s: str) -> str:
        return re.sub(r",\s*([\]}])", r"\1", s)

    try:
        parsed = json.loads(_clean_json(text))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(_clean_json(match.group(0)))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _walk_numbers(obj: Any):
    if isinstance(obj, (int, float)):
        yield float(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _walk_numbers(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_numbers(item)


def _number_tokens(value: float) -> set[str]:
    tokens = {f"{value}", f"{value:.1f}", f"{value:.2f}", f"{value:.3f}", f"{value:.4f}"}
    if 0 < abs(value) < 1:
        tokens.add(f"{value:.1%}".replace("%", ""))
        tokens.add(f"{value * 100:.1f}")
    return tokens


def _allowed_number_tokens(context: RunScenarioContext) -> set[str]:
    allowed: set[str] = set()
    for value in _walk_numbers(context.summary_metrics):
        allowed.update(_number_tokens(value))
    for row in context.phase_ticks:
        for value in _walk_numbers(row):
            allowed.update(_number_tokens(value))
    for row in context.population_segments[-20:]:
        for key in ("booking_rate", "avg_income_factor"):
            value = _safe_float(row.get(key))
            if value is not None:
                allowed.update(_number_tokens(value))
    if context.metadata.get("ticks_completed") is not None:
        allowed.add(str(int(context.metadata["ticks_completed"])))
    for row in context.phase_ticks:
        if row.get("tick") is not None:
            allowed.add(str(int(row["tick"])))

    # Allow scenario ranks and CIB scores
    allowed.update({"1", "2", "3"})
    cib_score = _cib_score(context)
    if cib_score is not None:
        allowed.update(_number_tokens(cib_score))

    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    for sc in build_candidate_constellations(context, factor_profile, catalog):
        score = sc.get("consistency_score")
        if score is not None:
            allowed.update(_number_tokens(float(score)))

    return allowed


def validate_scenario_narrative(payload: dict[str, Any], context: RunScenarioContext) -> list[str]:
    allowed = _allowed_number_tokens(context)
    warnings: list[str] = []
    text_parts = [
        str(payload.get("summary", "")),
        str(payload.get("run_narrative", "")),
        str(payload.get("observed_run", "")),
        str(payload.get("starting_conditions", "")),
        str(payload.get("limitations", "")),
    ]
    for scenario in payload.get("scenarios") or []:
        if not isinstance(scenario, dict):
            continue
        text_parts.append(str(scenario.get("story", "")))
        text_parts.append(str(scenario.get("what_could_happen", "")))
    for item in payload.get("timeline") or []:
        if isinstance(item, dict):
            text_parts.append(str(item.get("narrative", "")))

    joined = " ".join(text_parts)
    for match in re.finditer(r"(?<!\w)(\d+[.,]\d+|\d+)(?!\w)", joined):
        token = match.group(1).replace(",", ".")
        if token in allowed:
            continue
        if re.search(rf"(?:Tick|tick)\s*{re.escape(token)}\b", joined):
            continue
        warnings.append(token)
    return warnings


def build_ground_truth_block(context: RunScenarioContext) -> dict[str, Any]:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    block = dict(context.summary_metrics)
    block["run_id"] = context.run_id
    block["cib_consistency_score"] = _cib_score(context)
    block["factor_profile"] = factor_profile
    return block
