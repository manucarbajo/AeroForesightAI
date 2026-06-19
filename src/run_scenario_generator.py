"""P3 — LLM run scenario synthesis from completed run artefacts (grounded)."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from src.output_writer import OUTPUT_DIR
from src.state_explorer import resolve_run_dir

RUN_SCENARIO_MARKER = "RUN_SCENARIO_GENERATOR"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FACTOR_CATALOG = REPO_ROOT / "configs" / "factors.json"
FACTOR_IDS = tuple(f"F{i}" for i in range(1, 8))


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class RunScenarioContext:
    run_id: str
    run_dir: Path
    metadata: dict[str, Any]
    tick_mechanics: dict[str, Any]
    event_log: list[dict[str, Any]]
    price_history: list[dict[str, Any]]
    population_segments: list[dict[str, Any]]
    factors: list[dict[str, Any]]
    cib_matrix: dict[str, Any] | None
    summary_metrics: dict[str, Any]
    phase_ticks: list[dict[str, Any]]


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _compute_summary_metrics(
    ticks: list[dict[str, Any]],
    population_segments: list[dict[str, str]],
    factors: list[dict[str, str]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "ticks_completed": metadata.get("ticks_completed"),
        "ticks_max": metadata.get("ticks_max"),
        "simulation_name": metadata.get("simulation_name") or metadata.get("name"),
    }
    if ticks:
        bookings = [_safe_float(row.get("booking_rate")) for row in ticks]
        bookings = [value for value in bookings if value is not None]
        prices = [_safe_float(row.get("market_price_after_feedback_eur")) for row in ticks]
        prices = [value for value in prices if value is not None]
        if bookings:
            summary["booking_rate_start"] = round(bookings[0], 4)
            summary["booking_rate_end"] = round(bookings[-1], 4)
            summary["booking_rate_min"] = round(min(bookings), 4)
            summary["booking_rate_max"] = round(max(bookings), 4)
        if prices:
            summary["ticket_price_start_eur"] = round(prices[0], 2)
            summary["ticket_price_end_eur"] = round(prices[-1], 2)
            summary["ticket_price_min_eur"] = round(min(prices), 2)
            summary["ticket_price_max_eur"] = round(max(prices), 2)

    if population_segments:
        last_tick = max(int(row["tick"]) for row in population_segments if row.get("tick"))
        end_rows = [row for row in population_segments if int(row["tick"]) == last_tick]
        summary["segment_booking_end"] = {
            row["segment_id"]: round(float(row["booking_rate"]), 4)
            for row in end_rows
            if row.get("segment_id") and row.get("booking_rate")
        }

    if factors:
        last = factors[-1]
        first = factors[0]
        summary["factor_states_end"] = {
            key: value for key, value in last.items() if key != "tick"
        }
        summary["factor_states_start"] = {
            key: value for key, value in first.items() if key != "tick"
        }
        summary["factor_transitions"] = _extract_factor_transitions(factors)

    return summary


def _extract_factor_transitions(factors: list[dict[str, str]]) -> list[dict[str, Any]]:
    if len(factors) < 2:
        return []
    factor_ids = sorted(key for key in factors[0] if key != "tick")
    transitions: list[dict[str, Any]] = []
    previous = {factor_id: factors[0].get(factor_id) for factor_id in factor_ids}
    for row in factors[1:]:
        tick = int(row.get("tick") or 0)
        for factor_id in factor_ids:
            current = row.get(factor_id)
            if current and current != previous.get(factor_id):
                transitions.append(
                    {
                        "tick": tick,
                        "factor_id": factor_id,
                        "from_state": previous.get(factor_id),
                        "to_state": current,
                    }
                )
            previous[factor_id] = current
    return transitions


def _load_factor_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_FACTOR_CATALOG
    if not catalog_path.is_file():
        return {}
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _factor_state_label(catalog: dict[str, Any], factor_id: str, state_id: str | None) -> str:
    if not state_id:
        return "unbekannt"
    factor = catalog.get(factor_id) or {}
    states = factor.get("possible_states") or {}
    return str(states.get(state_id) or state_id)


def _factor_name(catalog: dict[str, Any], factor_id: str) -> str:
    factor = catalog.get(factor_id) or {}
    return str(factor.get("name") or factor_id)


def build_factor_profile(
    context: RunScenarioContext,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = catalog or _load_factor_catalog()
    metrics = context.summary_metrics
    start_states = dict(metrics.get("factor_states_start") or {})
    end_states = dict(metrics.get("factor_states_end") or {})
    if not end_states and context.factors:
        last = context.factors[-1]
        end_states = {key: value for key, value in last.items() if key != "tick"}
    if not start_states and context.factors:
        first = context.factors[0]
        start_states = {key: value for key, value in first.items() if key != "tick"}

    def _enrich(states: dict[str, Any]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for factor_id in FACTOR_IDS:
            state_id = states.get(factor_id)
            if not state_id:
                continue
            rows.append(
                {
                    "factor_id": factor_id,
                    "factor_name": _factor_name(catalog, factor_id),
                    "state_id": str(state_id),
                    "state_label": _factor_state_label(catalog, factor_id, str(state_id)),
                }
            )
        return rows

    transitions: list[dict[str, Any]] = []
    for item in metrics.get("factor_transitions") or []:
        if not isinstance(item, dict):
            continue
        factor_id = str(item.get("factor_id") or "")
        from_state = str(item.get("from_state") or "")
        to_state = str(item.get("to_state") or "")
        transitions.append(
            {
                "tick": item.get("tick"),
                "factor_id": factor_id,
                "factor_name": _factor_name(catalog, factor_id),
                "from_state": from_state,
                "from_label": _factor_state_label(catalog, factor_id, from_state),
                "to_state": to_state,
                "to_label": _factor_state_label(catalog, factor_id, to_state),
            }
        )

    return {
        "start": _enrich(start_states),
        "end": _enrich(end_states),
        "transitions": transitions,
        "end_by_id": {row["factor_id"]: row["state_id"] for row in _enrich(end_states)},
    }


def _sample_delta_events(event_log: list[dict[str, Any]], *, limit: int = 6) -> list[str]:
    lines: list[str] = []
    for event in reversed(event_log):
        description = str(event.get("description") or "")
        if "[delta:" not in description:
            continue
        tick = event.get("round_number")
        prefix = f"Tick {tick}: " if tick is not None else ""
        lines.append(prefix + description)
        if len(lines) >= limit:
            break
    return list(reversed(lines))


def _format_factor_compact(catalog: dict[str, Any], states: dict[str, str]) -> str:
    parts: list[str] = []
    for factor_id in FACTOR_IDS:
        state_id = states.get(factor_id)
        if state_id:
            parts.append(f"{factor_id}={state_id}")
    return ", ".join(parts)


def _format_factor_labels_short(catalog: dict[str, Any], states: dict[str, str], *, max_items: int = 4) -> str:
    bits: list[str] = []
    for factor_id in FACTOR_IDS:
        state_id = states.get(factor_id)
        if not state_id:
            continue
        bits.append(
            f"{factor_id} {_factor_state_label(catalog, factor_id, state_id)}"
        )
        if len(bits) >= max_items:
            break
    suffix = " …" if len(bits) < len([f for f in FACTOR_IDS if states.get(f)]) else ""
    return "; ".join(bits) + suffix


def build_run_narrative(context: RunScenarioContext, factor_profile: dict[str, Any]) -> str:
    """Kompakte sachliche Beschreibung des Laufverlaufs."""
    metrics = context.summary_metrics
    sim_name = metrics.get("simulation_name") or context.run_id
    ticks = metrics.get("ticks_completed") or metrics.get("ticks_max") or "?"
    booking = _booking_trend(metrics)
    price = _price_trend(metrics)

    lines = [
        (
            f"Lauf «{sim_name}», {ticks} Ticks: Nachfrage {booking}, Ticketpreis {price}."
        )
    ]

    transitions = factor_profile.get("transitions") or []
    if transitions:
        shown = transitions[:4]
        change_bits = [
            f"Tick {item['tick']} {item['factor_id']} {item['from_state']}→{item['to_state']}"
            for item in shown
        ]
        extra = f" (+{len(transitions) - len(shown)} weitere)" if len(transitions) > len(shown) else ""
        lines.append("Faktorwechsel: " + ", ".join(change_bits) + extra + ".")
    else:
        lines.append("Faktoren F1–F7 ohne Deskriptor-Wechsel im Lauf.")

    catalog = _load_factor_catalog()
    end_by_id = factor_profile.get("end_by_id") or {}
    if end_by_id:
        lines.append(
            "Endlage: " + _format_factor_labels_short(catalog, end_by_id, max_items=7) + "."
        )

    events = _sample_delta_events(context.event_log, limit=2)
    if events:
        lines.append("Ereignisse: " + " | ".join(events) + ".")

    return " ".join(lines)


def _flip_state(state_id: str) -> str:
    if not state_id or "." not in state_id:
        return state_id
    factor_id, suffix = state_id.split(".", 1)
    flipped = "2" if suffix == "1" else "1"
    return f"{factor_id}.{flipped}"


def _slide_scenario_title(scenario_kind: str) -> str:
    if scenario_kind == "fortsetzung":
        return "Trend-Fortsetzung"
    if scenario_kind == "alternative":
        return "Alternativ-Szenario"
    if scenario_kind == "spannung":
        return "Spannungs-Szenario"
    return "Exploratives Szenario"


def _phase_label(index: int) -> str:
    return ["Frühphase", "Mittelphase", "Spätphase"][min(index, 2)]


def build_scenario_tick_grounding(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
    states: dict[str, str],
) -> str:
    """Kurze Tick- und Faktor-Anhaltspunkte aus dem Lauf."""
    lines: list[str] = []

    for row in context.phase_ticks:
        tick = row.get("tick")
        bits: list[str] = [f"Tick {tick}"]
        booking = row.get("booking_rate")
        price = row.get("market_price_after_feedback_eur")
        if booking is not None:
            bits.append(f"BR {float(booking):.1%}")
        if price is not None:
            bits.append(f"Preis {float(price):.0f} €")
        lines.append("- " + ", ".join(bits))

    end_by_id = factor_profile.get("end_by_id") or {}
    lines.append("Szenario-Faktoren: " + _format_factor_compact(catalog, states) + ".")
    diffs = [
        factor_id
        for factor_id in FACTOR_IDS
        if states.get(factor_id) and end_by_id.get(factor_id) != states.get(factor_id)
    ]
    if diffs:
        diff_bits = [
            f"{factor_id} {end_by_id.get(factor_id)}→{states.get(factor_id)}"
            for factor_id in diffs
        ]
        lines.append("Abweichung zur Lauf-Endlage: " + ", ".join(diff_bits) + ".")
    elif end_by_id:
        lines.append("Entspricht der Faktor-Endlage des Laufs.")

    return "\n".join(lines)


def _build_scenario_description(
    *,
    scenario_kind: str,
    slide_title: str,
    context: RunScenarioContext,
    catalog: dict[str, Any],
    states: dict[str, str],
) -> str:
    """Sachliche Szenario-Beschreibung — nur aus Faktoren und Lauf ableiten."""
    f1 = _factor_state_label(catalog, "F1", states.get("F1", ""))
    f2 = _factor_state_label(catalog, "F2", states.get("F2", ""))
    f3 = _factor_state_label(catalog, "F3", states.get("F3", ""))
    f5 = _factor_state_label(catalog, "F5", states.get("F5", ""))
    f6 = _factor_state_label(catalog, "F6", states.get("F6", ""))
    booking = _booking_trend(context.summary_metrics)

    if scenario_kind == "fortsetzung":
        return (
            f"«{slide_title}»: Die im Lauf erreichte Faktorlage setzt sich fort "
            f"({f1}; {f2}). Nachfrage und Preis würden den im Lauf {booking}en Trend "
            f"plausibel fortsetzen. {f3} und {f5} bleiben Rahmenbedingungen. {f6} prägt "
            f"die gesellschaftliche Akzeptanz von Flugreisen."
        )

    if scenario_kind == "alternative":
        return (
            f"«{slide_title}»: Gegenüber der Lauf-Endlage weicht mindestens ein Faktor ab "
            f"(siehe oben). Typisch: Verschiebungen bei {f1} und {f2}. {f5} und {f6} "
            f"können Modal Shift verstärken oder dämpfen. Explorative Konstellation, keine Prognose."
        )

    return (
        f"«{slide_title}»: Widersprüchliche Faktortrends ({f1} vs. {f2}). "
        f"Anpassungsdruck auf Politik, Anbieter und Nachfrage. {f6} kann Spannungen verstärken."
    )


def _build_constellation_scenario(
    *,
    rank: int,
    scenario_kind: str,
    states: dict[str, str],
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    slide_title = _slide_scenario_title(scenario_kind)
    title = slide_title

    tick_grounding = build_scenario_tick_grounding(
        context, factor_profile, catalog, states
    )
    story = _build_scenario_description(
        scenario_kind=scenario_kind,
        slide_title=slide_title,
        context=context,
        catalog=catalog,
        states=states,
    )

    return {
        "rank": rank,
        "id": f"S{rank}",
        "title": title,
        "scenario_kind": scenario_kind,
        "plausibility": _plausibility_for_rank(rank),
        "factor_constellation": dict(states),
        "tick_grounding": tick_grounding,
        "story": story,
        "what_could_happen": story,
    }


def _pick_alternative_constellation(end_states: dict[str, str], transitions: list[dict[str, Any]]) -> dict[str, str]:
    states = dict(end_states)
    if transitions:
        pivot = transitions[0]["factor_id"]
        states[pivot] = _flip_state(str(states.get(pivot, "")))
        return states
    for pivot in ("F6", "F3", "F5", "F4"):
        if pivot in states:
            states[pivot] = _flip_state(str(states[pivot]))
            return states
    return states


def _pick_tension_constellation(end_states: dict[str, str]) -> dict[str, str]:
    states = dict(end_states)
    f1 = str(states.get("F1", "F1.1"))
    f2 = str(states.get("F2", "F2.1"))
    if f1.endswith(".1") and f2.endswith(".1"):
        states["F2"] = _flip_state(f2)
    elif f1.endswith(".2") and f2.endswith(".2"):
        states["F1"] = _flip_state(f1)
    else:
        states["F1"] = "F1.1"
        states["F2"] = "F2.2"
    return states


def build_explorative_scenarios(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    end_states = dict(factor_profile.get("end_by_id") or {})
    if not end_states:
        end_states = {f"F{i}": f"F{i}.1" for i in range(1, 8)}

    transitions = factor_profile.get("transitions") or []
    continuation = _build_constellation_scenario(
        rank=1,
        scenario_kind="fortsetzung",
        states=end_states,
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    alternative = _build_constellation_scenario(
        rank=2,
        scenario_kind="alternative",
        states=_pick_alternative_constellation(end_states, transitions),
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    tension = _build_constellation_scenario(
        rank=3,
        scenario_kind="spannung",
        states=_pick_tension_constellation(end_states),
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    
    scenarios = [continuation, alternative, tension]
    
    # Calculate CIB Consistency Scores
    if isinstance(context.cib_matrix, dict):
        try:
            from src.models.cib_models import CIBMatrix
            from src.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
            
            matrix_obj = CIBMatrix.model_validate(context.cib_matrix)
            checker = ConsistencyChecker(matrix_obj)
            
            for sc in scenarios:
                desc = ScenarioDescriptor(factor_states=sc["factor_constellation"])
                score = checker.compute_consistency_score(desc)
                sc["consistency_score"] = round(score, 3)
        except Exception as e:
            # Fallback if matrix validation fails
            for sc in scenarios:
                sc["consistency_score"] = None
    else:
        for sc in scenarios:
            sc["consistency_score"] = None

    return scenarios


def _select_phase_ticks(ticks: list[dict[str, Any]], *, max_phases: int = 3) -> list[dict[str, Any]]:
    if not ticks:
        return []
    if len(ticks) <= max_phases:
        return ticks
    indices = [0, len(ticks) // 2, len(ticks) - 1]
    selected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index in indices:
        if index in seen:
            continue
        seen.add(index)
        selected.append(ticks[index])
    return selected


def load_run_scenario_context(
    run_id: str,
    *,
    run_dir: Path | None = None,
    outputs_root: Path | str | None = None,
) -> RunScenarioContext:
    directory = run_dir or resolve_run_dir(run_id, outputs_root=outputs_root)
    metadata = _load_json(directory / "run_metadata.json", {})
    tick_mechanics = _load_json(directory / "tick_mechanics.json", {"ticks": []})
    ticks = list(tick_mechanics.get("ticks") or [])
    population_segments = _load_csv(directory / "timeseries" / "population.csv")
    factors = _load_csv(directory / "timeseries" / "factors.csv")
    return RunScenarioContext(
        run_id=run_id,
        run_dir=directory,
        metadata=metadata if isinstance(metadata, dict) else {},
        tick_mechanics=tick_mechanics if isinstance(tick_mechanics, dict) else {"ticks": []},
        event_log=_load_json(directory / "event_log.json", []),
        price_history=_load_json(directory / "price_history.json", []),
        population_segments=population_segments,
        factors=factors,
        cib_matrix=_load_json(directory / "cib_matrix.json", None),
        summary_metrics=_compute_summary_metrics(
            ticks,
            population_segments,
            factors,
            metadata if isinstance(metadata, dict) else {},
        ),
        phase_ticks=_select_phase_ticks(ticks),
    )


# _infer_scenario_alignment and _rank_archetypes removed to decouple from lecture archetypes.


def _cib_score(context: RunScenarioContext) -> float | None:
    matrix = context.cib_matrix
    if not isinstance(matrix, dict):
        return None
    meta = matrix.get("metadata") or {}
    if isinstance(meta, dict) and meta.get("consistency_score") is not None:
        return float(meta["consistency_score"])
    scores = matrix.get("factor_scores") or []
    if isinstance(scores, list) and scores:
        active = [
            float(item.get("active_score", 0))
            for item in scores
            if isinstance(item, dict) and item.get("active_score") is not None
        ]
        if active:
            return round(sum(active) / len(active), 3)
    return None


def _booking_trend(metrics: dict[str, Any]) -> str:
    start = metrics.get("booking_rate_start")
    end = metrics.get("booking_rate_end")
    if start is None or end is None:
        return "stabil"
    delta = float(end) - float(start)
    if delta > 0.05:
        return "steigend"
    if delta < -0.05:
        return "fallend"
    return "stabil"


def _price_trend(metrics: dict[str, Any]) -> str:
    start = metrics.get("ticket_price_start_eur")
    end = metrics.get("ticket_price_end_eur")
    if start is None or end is None:
        return "stabil"
    delta = float(end) - float(start)
    if delta > 5:
        return "steigend"
    if delta < -5:
        return "fallend"
    return "stabil"





def _plausibility_for_rank(rank: int) -> str:
    return {1: "hoch", 2: "mittel", 3: "niedrig"}[rank]


def _observed_run_brief(context: RunScenarioContext, factor_profile: dict[str, Any]) -> str:
    return build_run_narrative(context, factor_profile)


def _normalize_scenarios(raw: Any, *, context: RunScenarioContext, factor_profile: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    template_scenarios = build_explorative_scenarios(context, factor_profile, catalog)
    
    if not isinstance(raw, list):
        return template_scenarios

    scenarios: list[dict[str, Any]] = []
    for index, item in enumerate(raw[:3]):
        if not isinstance(item, dict):
            continue
        
        # Match with our precalculated scenario by rank/index
        rank_val = int(item.get("rank") or index + 1)
        template_match = next((t for t in template_scenarios if t["rank"] == rank_val), template_scenarios[index] if index < len(template_scenarios) else template_scenarios[-1])

        constellation = template_match.get("factor_constellation", {})
        tick_grounding = template_match.get("tick_grounding", "")
        consistency_score = template_match.get("consistency_score")
        scenario_kind = template_match.get("scenario_kind", "explorativ")

        story = str(item.get("story") or item.get("what_could_happen") or item.get("narrative") or "").strip()
        
        scenarios.append(
            {
                "rank": rank_val,
                "id": f"S{rank_val}",
                "title": str(item.get("title") or template_match.get("title")),
                "scenario_kind": scenario_kind,
                "plausibility": str(item.get("plausibility") or _plausibility_for_rank(rank_val)),
                "consistency_score": consistency_score,
                "factor_constellation": dict(constellation),
                "tick_grounding": tick_grounding,
                "story": story,
                "what_could_happen": story,
            }
        )

    # Fill up if LLM returned fewer than 3
    if len(scenarios) < 3:
        existing_ranks = {item["rank"] for item in scenarios}
        for item in template_scenarios:
            if item["rank"] in existing_ranks:
                continue
            scenarios.append(item)
            if len(scenarios) >= 3:
                break

    scenarios.sort(key=lambda item: int(item.get("rank") or 99))
    for index, item in enumerate(scenarios[:3], start=1):
        item["rank"] = index
        item["id"] = f"S{index}"
        item["plausibility"] = _plausibility_for_rank(index)
    return scenarios[:3]


def build_run_summary(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    scenarios: list[dict[str, Any]],
) -> str:
    """Kurze sachliche Einordnung — ohne Wiederholung des Lauf-Narrativs."""
    metrics = context.summary_metrics
    sim_name = metrics.get("simulation_name") or context.run_id
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
    metrics = context.summary_metrics
    sim_name = metrics.get("simulation_name") or context.run_id

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
        "scenarios": scenarios,
        "limitations": (
            "Explorative Szenarien, sachlich aus dem Lauf abgeleitet — keine Prognose, keine Fiktion."
        ),
        "source": "template",
    }


def build_scenario_prompt(context: RunScenarioContext) -> str:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    precalculated_scenarios = build_explorative_scenarios(context, factor_profile, catalog)
    
    # Clean up the output to avoid deeply nested huge objects in the prompt if we don't need them
    clean_scenarios = []
    for sc in precalculated_scenarios:
        clean_scenarios.append({
            "rank": sc.get("rank"),
            "scenario_kind": sc.get("scenario_kind"),
            "consistency_score": sc.get("consistency_score"),
            "factor_constellation": sc.get("factor_constellation"),
            "tick_grounding": sc.get("tick_grounding")
        })

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
        "precalculated_scenarios": clean_scenarios,
    }
    
    prompt_path = Path("src/prompts/run_scenario.md")
    if prompt_path.exists():
        prompt_template = prompt_path.read_text(encoding="utf-8")
    else:
        # Fallback if file is missing
        prompt_template = f"Bitte erstelle 3 Szenarien. Lese die Daten aus RUN CONTEXT.\n"
        
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
    precalc = build_explorative_scenarios(context, factor_profile, catalog)
    for sc in precalc:
        score = sc.get("consistency_score")
        if score is not None:
            allowed.update(_number_tokens(float(score)))
            
    return allowed


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


def render_run_scenario_markdown(payload: dict[str, Any], ground_truth: dict[str, Any]) -> str:
    lines = [
        f"# {payload.get('title', 'Run-Szenarien')}",
        "",
        "## Zusammenfassung",
        str(payload.get("summary", "")),
        "",
        "## Lauf-Narrativ",
        str(payload.get("run_narrative", payload.get("observed_run", ""))),
        "",
        "## Szenarien",
        "",
    ]

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

    if prefer_llm and llm is not None:
        raw = llm.call(build_scenario_prompt(context))
        print("RAW LLM OUTPUT:\n", raw)
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
    elif len(str(narrative.get("summary") or "")) < 200:
        template = build_template_scenario(context)
        narrative["summary"] = template["summary"]

    scenarios = narrative.get("scenarios") or _normalize_scenarios(
        [],
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    markdown = render_run_scenario_markdown(narrative, ground_truth)
    return {
        "run_id": context.run_id,
        "title": narrative.get("title", ""),
        "summary": narrative.get("summary", ""),
        "scenarios": scenarios,
        "source": narrative.get("source", "template"),
        "grounding_warnings": grounding_warnings,
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
        "run_narrative": (result.get("narrative") or {}).get("run_narrative"),
        "factor_profile": (result.get("narrative") or {}).get("factor_profile")
        or result.get("ground_truth", {}).get("factor_profile"),
        "scenarios": result.get("scenarios") or (result.get("narrative") or {}).get("scenarios"),
        "source": result.get("source"),
        "grounding_warnings": result.get("grounding_warnings", []),
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate run_scenario.md/json for a completed run.")
    parser.add_argument("--run-id", required=True, help="Existing outputs/<run_id>/ directory")
    parser.add_argument(
        "--outputs-root",
        default=str(OUTPUT_DIR),
        help="Outputs root (default: outputs/)",
    )
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Skip LLM and use deterministic template narrative.",
    )
    args = parser.parse_args(argv)

    llm = None
    if not args.template_only:
        from src.studio_helpers import get_llm

        llm = get_llm()

    result = generate_and_save_run_scenario(
        args.run_id,
        llm,
        run_dir=resolve_run_dir(args.run_id, outputs_root=args.outputs_root),
        prefer_llm=not args.template_only,
    )
    print(result["paths"]["markdown"])
    print(result["paths"]["json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
