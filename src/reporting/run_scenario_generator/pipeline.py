"""End-to-end scenario generation: load context, prompt/parse, render, persist."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.llm import LLMCallable, auf_deutsch
from src.reporting.run_scenario_generator.candidates import _normalize_scenarios
from src.reporting.run_scenario_generator.context import load_run_scenario_context
from src.reporting.run_scenario_generator.factors import _load_factor_catalog, build_factor_profile
from src.reporting.run_scenario_generator.prompt import (
    _extract_json_object,
    build_ground_truth_block,
    build_scenario_prompt,
    validate_scenario_narrative,
)
from src.reporting.run_scenario_generator.rendering import (
    build_template_scenario,
    render_run_scenario_markdown,
)

logger = logging.getLogger(__name__)


def generate_run_scenario(
    run_id: str,
    llm: LLMCallable | None = None,
    *,
    run_dir: Path | None = None,
    prefer_llm: bool = True,
) -> dict[str, Any]:
    context = load_run_scenario_context(run_id, run_dir=run_dir)
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    ground_truth = build_ground_truth_block(context)

    narrative: dict[str, Any] | None = None
    grounding_warnings: list[str] = []
    llm_error: str | None = None

    if prefer_llm and llm is not None:
        # Fällt der Aufruf aus, greift weiter unten `build_template_scenario` —
        # ein deterministisches Narrativ ohne Sprachmodell. Ohne dieses `except`
        # riss der Ausfall den ganzen Lauf mit, und zwar *nachdem* er gerechnet
        # war: es gäbe dann kein `run_metadata.json`, keinen Warnbanner, keinen
        # Lauf in der Liste — die Degradation wäre unsichtbar, weil gar nichts
        # ankommt. Der Fehler geht als `llm_error` an den Aufrufer zurück, der
        # ihn als Vorfall protokolliert.
        try:
            raw = llm.call(auf_deutsch(build_scenario_prompt(context)))
        except Exception as exc:  # noqa: BLE001 - jeder Backend-Fehler endet im Template
            logger.warning(
                "Lauf-Szenario konnte nicht vom Sprachmodell erzeugt werden: %s. "
                "Es wird das deterministische Template verwendet.",
                exc,
            )
            llm_error = f"{type(exc).__name__}: {exc}"
            raw = ""
        parsed = _extract_json_object(raw)
        scenarios_raw = parsed.get("scenarios") if isinstance(parsed, dict) else None
        if (
            isinstance(parsed, dict)
            and parsed.get("title")
            and (parsed.get("run_narrative") or parsed.get("observed_run"))
            and isinstance(scenarios_raw, list)
            and len(scenarios_raw) >= 2
        ):
            parsed["factor_profile"] = factor_profile
            parsed["agent_digest"] = context.agent_digest
            if not parsed.get("run_narrative"):
                parsed["run_narrative"] = parsed.get("observed_run", "")
            parsed["observed_run"] = parsed.get("run_narrative", "")
            parsed["scenarios"] = _normalize_scenarios(
                scenarios_raw,
                context=context,
                factor_profile=factor_profile,
                catalog=catalog,
            )
            grounding_warnings = validate_scenario_narrative(parsed, context)
            narrative = parsed
            narrative["source"] = "llm"
            if grounding_warnings:
                narrative["grounding_warnings"] = grounding_warnings

    if narrative is None:
        narrative = build_template_scenario(context)
    else:
        narrative.setdefault("agent_digest", context.agent_digest)
        if len(str(narrative.get("summary") or "")) < 200:
            template = build_template_scenario(context)
            narrative["summary"] = template["summary"]

    scenarios = narrative.get("scenarios") or _normalize_scenarios(
        [],
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    markdown = render_run_scenario_markdown(
        narrative,
        ground_truth,
        agent_digest=context.agent_digest,
    )
    return {
        "run_id": context.run_id,
        "title": narrative.get("title", ""),
        "summary": narrative.get("summary", ""),
        "scenarios": scenarios,
        "source": narrative.get("source", "template"),
        "grounding_warnings": grounding_warnings,
        "llm_error": llm_error,
        "agent_digest": context.agent_digest,
        "narrative": narrative,
        "ground_truth": ground_truth,
        "markdown": markdown,
    }


def save_run_scenario_artifacts(
    run_dir: Path | str,
    result: dict[str, Any],
) -> tuple[Path, Path]:
    directory = Path(run_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "run_scenario.json"
    md_path = directory / "run_scenario.md"

    json_payload = {
        "run_id": result.get("run_id"),
        "title": result.get("title"),
        "summary": result.get("summary"),
        "selection_reasoning": (result.get("narrative") or {}).get("selection_reasoning"),
        "run_narrative": (result.get("narrative") or {}).get("run_narrative"),
        "factor_profile": (result.get("narrative") or {}).get("factor_profile")
        or result.get("ground_truth", {}).get("factor_profile"),
        "scenarios": result.get("scenarios") or (result.get("narrative") or {}).get("scenarios"),
        "source": result.get("source"),
        "grounding_warnings": result.get("grounding_warnings", []),
        "agent_digest": result.get("agent_digest")
        or (result.get("narrative") or {}).get("agent_digest"),
        "narrative": result.get("narrative"),
        "ground_truth": result.get("ground_truth"),
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(str(result.get("markdown", "")), encoding="utf-8")
    return md_path, json_path


def generate_and_save_run_scenario(
    run_id: str,
    llm: LLMCallable | None = None,
    *,
    run_dir: Path | None = None,
    prefer_llm: bool = True,
) -> dict[str, Any]:
    from src.reporting.state_explorer import resolve_run_dir

    directory = run_dir or resolve_run_dir(run_id)
    result = generate_run_scenario(
        run_id,
        llm,
        run_dir=directory,
        prefer_llm=prefer_llm,
    )
    md_path, json_path = save_run_scenario_artifacts(directory, result)
    result["paths"] = {"markdown": str(md_path), "json": str(json_path)}
    return result
