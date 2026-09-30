"""Markdown rendering, run summary, and the deterministic template scenario."""

from __future__ import annotations

from typing import Any

from src.reporting.run_scenario_generator.agent_digest import render_agent_perspectives_markdown
from src.reporting.run_scenario_generator.candidates import build_explorative_scenarios
from src.reporting.run_scenario_generator.context import RunScenarioContext, lauf_name
from src.reporting.run_scenario_generator.factors import (
    _format_factor_compact,
    _load_factor_catalog,
    build_factor_profile,
)
from src.reporting.run_scenario_generator.narrative import build_run_narrative


def build_run_summary(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    scenarios: list[dict[str, Any]],
) -> str:
    """Kurze sachliche Einordnung — ohne Wiederholung des Lauf-Narrativs."""
    metrics = context.summary_metrics
    sim_name = lauf_name(context)
    ticks = metrics.get("ticks_completed") or metrics.get("ticks_max") or "?"
    catalog = _load_factor_catalog()
    end_by_id = factor_profile.get("end_by_id") or {}
    titles = ", ".join(item.get("title", "?") for item in scenarios[:3]) if scenarios else "—"

    return (
        f"Simulationslauf «{sim_name}» ({ticks} Ticks): drei explorative Szenarien "
        f"aus der Faktor-Endlage ({_format_factor_compact(catalog, end_by_id)}). "
        f"Pfade: {titles}. Sachlich, keine Prognose."
    )


def build_template_scenario(context: RunScenarioContext) -> dict[str, Any]:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    run_narrative = build_run_narrative(context, factor_profile)
    scenarios = build_explorative_scenarios(context, factor_profile, catalog)
    sim_name = lauf_name(context)

    title = f"Szenarien zum Lauf {sim_name}"
    summary = build_run_summary(
        context,
        factor_profile,
        scenarios,
    )

    return {
        "title": title,
        "summary": summary,
        "run_narrative": run_narrative,
        "observed_run": run_narrative,
        "factor_profile": factor_profile,
        "agent_digest": context.agent_digest,
        "scenarios": scenarios,
        "limitations": (
            "Explorative Szenarien, sachlich aus dem Lauf abgeleitet — keine Prognose, keine Fiktion."
        ),
        "source": "template",
    }


def render_run_scenario_markdown(
    payload: dict[str, Any],
    ground_truth: dict[str, Any],
    *,
    agent_digest: dict[str, Any] | None = None,
) -> str:
    digest = (
        agent_digest
        or payload.get("agent_digest")
        or (payload.get("narrative") or {}).get("agent_digest")
        or {}
    )
    lines = [
        f"# {payload.get('title', 'Run-Szenarien')}",
        "",
        "## Zusammenfassung",
        str(payload.get("summary", "")),
        "",
        "## Lauf-Narrativ",
        str(payload.get("run_narrative", payload.get("observed_run", ""))),
        "",
    ]

    # Direkt unter dem Text, über den sie etwas sagen — nicht am Ende (P8-V3).
    widerspruch = payload.get("widersprueche") or []
    if widerspruch:
        lines.append(
            "> **Widerspricht der Rechnung.** Das Sprachmodell hat hier etwas anderes "
            "geschrieben, als der Lauf gerechnet hat:"
        )
        lines.append(">")
        lines.extend(f"> - {eintrag.get('zeile', '')}" for eintrag in widerspruch)
        lines.append("")

    selection_reasoning = str(payload.get("selection_reasoning", "")).strip()
    if selection_reasoning:
        lines.extend(["## Auswahl der Szenarien", selection_reasoning, ""])

    lines.extend(
        [
            "## Akteur-Perspektiven",
            "",
            render_agent_perspectives_markdown(digest),
            "",
            "## Szenarien",
            "",
        ]
    )

    scenarios = payload.get("scenarios") or []
    if not scenarios:
        lines.append("_Keine Szenarien generiert._")
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        rank = scenario.get("rank", "?")
        sid = scenario.get("id", "")
        title = scenario.get("title", "Szenario")
        lines.append(f"### {rank}. {sid} — {title}")
        lines.append("")
        lines.append("#### Anhaltspunkte aus dem Lauf (Ticks)")
        lines.append(str(scenario.get("tick_grounding", "")))
        lines.append("")
        lines.append("#### Szenario-Beschreibung")
        lines.append(str(scenario.get("story") or scenario.get("what_could_happen", "")))
        lines.append("")

    if payload.get("limitations"):
        lines.extend(
            [
                "## Hinweis",
                str(payload.get("limitations", "")),
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"
