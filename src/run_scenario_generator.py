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
AGENT_IDS = ("consumer", "provider", "regulator")
AGENT_LABELS = {
    "consumer": "Passagiere (Consumer)",
    "provider": "Airlines (Provider)",
    "regulator": "Politik (Regulator)",
}
_EMPTY_AGENT_REASONING = frozenset(
    {"mock", "noop", "fallback", "kein reasoning geliefert.", "kein reasoning geliefert"}
)


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
    agent_digest: dict[str, Any]


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
        summary["factor_states_end"] = {key: value for key, value in last.items() if key != "tick"}
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


def _truncate_text(text: str, *, max_len: int = 320) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 1].rstrip() + "…"


def _is_meaningful_agent_payload(agent_data: dict[str, Any]) -> bool:
    reasoning = str(agent_data.get("reasoning") or "").strip().lower()
    if reasoning and reasoning not in _EMPTY_AGENT_REASONING:
        return True
    actions = [
        str(action).strip().upper()
        for action in (agent_data.get("actions") or [])
        if str(action).strip()
    ]
    if actions and actions != ["NO_OP"]:
        return True
    segment_analysis = agent_data.get("segment_analysis")
    return isinstance(segment_analysis, dict) and bool(segment_analysis)


def _load_segment_analysis_rounds(run_dir: Path) -> list[dict[str, Any]]:
    raw = _load_json(run_dir / "segment_analysis.json", [])
    return raw if isinstance(raw, list) else []


def _phase_tick_numbers(phase_ticks: list[dict[str, Any]]) -> list[int]:
    ticks: list[int] = []
    for row in phase_ticks:
        tick = row.get("tick")
        if tick is not None:
            ticks.append(int(tick))
    return ticks


def _select_segment_rows_for_phases(
    rounds: list[dict[str, Any]],
    phase_ticks: list[int],
) -> list[dict[str, Any]]:
    by_tick = {int(row["tick"]): row for row in rounds if row.get("tick") is not None}
    selected = [by_tick[tick] for tick in phase_ticks if tick in by_tick]
    if selected or not rounds:
        return selected

    indices = [0, len(rounds) // 2, len(rounds) - 1]
    seen: set[int] = set()
    fallback: list[dict[str, Any]] = []
    for index in indices:
        if index in seen:
            continue
        seen.add(index)
        fallback.append(rounds[index])
    return fallback


def _compact_agent_entry(agent_data: dict[str, Any]) -> dict[str, Any]:
    actions = [
        str(action)
        for action in (agent_data.get("actions") or [])
        if str(action).strip() and str(action).strip().upper() != "NO_OP"
    ]
    entry: dict[str, Any] = {
        "reasoning": _truncate_text(str(agent_data.get("reasoning") or ""), max_len=400),
        "actions": actions[:4],
    }
    segment_analysis = agent_data.get("segment_analysis")
    if isinstance(segment_analysis, dict) and segment_analysis:
        entry["segment_analysis"] = {
            str(segment_id): _truncate_text(str(text), max_len=200)
            for segment_id, text in list(segment_analysis.items())[:6]
            if text
        }
    return entry


def _aggregate_agent_themes(segment_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    themes: dict[str, list[str]] = {}
    for row in segment_rows:
        agents = row.get("agents") or {}
        consumer = agents.get("consumer") or {}
        segment_analysis = consumer.get("segment_analysis") or {}
        if not isinstance(segment_analysis, dict):
            continue
        for segment_id, text in segment_analysis.items():
            if not text:
                continue
            key = str(segment_id)
            snippet = _truncate_text(str(text), max_len=160)
            bucket = themes.setdefault(key, [])
            if snippet not in bucket:
                bucket.append(snippet)
            if len(bucket) >= 2:
                break
    return themes


def _sample_agent_narrative_events(
    event_log: list[dict[str, Any]],
    *,
    limit: int = 6,
) -> list[dict[str, Any]]:
    agent_ids = set(AGENT_IDS)
    items: list[dict[str, Any]] = []
    for event in reversed(event_log):
        source = str(event.get("source_agent") or "")
        if source not in agent_ids:
            continue
        description = str(event.get("description") or "")
        if "[delta:" in description or not description.strip():
            continue
        items.append(
            {
                "tick": event.get("round_number"),
                "agent_id": source,
                "event_type": event.get("event_type"),
                "description": _truncate_text(description, max_len=220),
            }
        )
        if len(items) >= limit:
            break
    return list(reversed(items))


def _rollup_by_agent(segment_rows: list[dict[str, Any]]) -> dict[str, str]:
    rollups: dict[str, list[str]] = {agent_id: [] for agent_id in AGENT_IDS}
    for row in segment_rows:
        tick = row.get("tick")
        agents = row.get("agents") or {}
        for agent_id in AGENT_IDS:
            data = agents.get(agent_id)
            if not isinstance(data, dict) or not _is_meaningful_agent_payload(data):
                continue
            reasoning = _truncate_text(str(data.get("reasoning") or ""), max_len=180)
            if reasoning.lower() in _EMPTY_AGENT_REASONING:
                continue
            rollups[agent_id].append(f"Tick {tick}: {reasoning}")

    return {
        agent_id: _truncate_text(" | ".join(snippets[:3]), max_len=500)
        for agent_id, snippets in rollups.items()
        if snippets
    }


def build_agent_digest(
    *,
    run_dir: Path,
    phase_ticks: list[dict[str, Any]],
    event_log: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate tick-level agent narratives for P3 scenario synthesis (Option B)."""

    rounds = _load_segment_analysis_rounds(run_dir)
    phase_numbers = _phase_tick_numbers(phase_ticks)
    phase_rows = _select_segment_rows_for_phases(rounds, phase_numbers)

    phase_highlights: list[dict[str, Any]] = []
    for index, row in enumerate(phase_rows):
        tick = row.get("tick")
        agents = row.get("agents") or {}
        agents_block: dict[str, Any] = {}
        for agent_id in AGENT_IDS:
            data = agents.get(agent_id)
            if not isinstance(data, dict) or not _is_meaningful_agent_payload(data):
                continue
            agents_block[agent_id] = _compact_agent_entry(data)
        if agents_block:
            phase_highlights.append(
                {
                    "tick": tick,
                    "phase": _phase_label(min(index, 2)),
                    "agents": agents_block,
                }
            )

    summary_by_agent = _rollup_by_agent(phase_rows if phase_rows else rounds[:3])
    segment_themes = _aggregate_agent_themes(rounds)
    agent_events = _sample_agent_narrative_events(event_log)
    has_content = bool(phase_highlights or summary_by_agent or segment_themes or agent_events)

    return {
        "has_agent_content": has_content,
        "reading_note": (
            "Agent texts are interpretive perspectives from the tick protocol "
            "(segment_analysis.json / event_log). Numeric ground truth in "
            "summary_metrics and phase_ticks takes precedence."
        ),
        "summary_by_agent": summary_by_agent,
        "phase_highlights": phase_highlights,
        "segment_themes": segment_themes,
        "agent_events_sample": agent_events,
    }


def render_agent_perspectives_markdown(agent_digest: dict[str, Any]) -> str:
    if not agent_digest.get("has_agent_content"):
        return (
            "_Keine Agenten-Perspektiven im Lauf protokolliert "
            "(Mock-Lauf oder leere Antworten)._"
        )

    lines: list[str] = []
    summary = agent_digest.get("summary_by_agent") or {}
    if summary:
        lines.extend(["### Rollenüberblick", ""])
        for agent_id in AGENT_IDS:
            text = summary.get(agent_id)
            if text:
                lines.append(f"- **{AGENT_LABELS[agent_id]}:** {text}")
        lines.append("")

    for block in agent_digest.get("phase_highlights") or []:
        if not lines or lines[-1] != "### Phasen-Highlights":
            lines.extend(["### Phasen-Highlights", ""])
        lines.append(f"#### Tick {block.get('tick')} — {block.get('phase', '')}")
        for agent_id, data in (block.get("agents") or {}).items():
            label = AGENT_LABELS.get(str(agent_id), str(agent_id))
            reasoning = data.get("reasoning") or ""
            actions = data.get("actions") or []
            lines.append(f"- **{label}:** {reasoning}")
            if actions:
                lines.append(f"  - Aktionen: {', '.join(actions)}")
            for segment_id, segment_text in (data.get("segment_analysis") or {}).items():
                lines.append(f"  - Segment `{segment_id}`: {segment_text}")
        lines.append("")

    themes = agent_digest.get("segment_themes") or {}
    if themes:
        lines.extend(["### Segment-Themen (Consumer)", ""])
        for segment_id, snippets in themes.items():
            lines.append(f"- **{segment_id}:** {' / '.join(snippets[:2])}")
        lines.append("")

    events = agent_digest.get("agent_events_sample") or []
    if events:
        lines.extend(["### Agenten-Events (Auswahl)", ""])
        for event in events:
            label = AGENT_LABELS.get(str(event.get("agent_id")), str(event.get("agent_id")))
            lines.append(f"- Tick {event.get('tick')} **{label}:** {event.get('description')}")

    return "\n".join(lines).strip()


def _agent_perspective_clause(agent_digest: dict[str, Any]) -> str:
    if not agent_digest.get("has_agent_content"):
        return ""
    parts: list[str] = []
    for agent_id in AGENT_IDS:
        text = (agent_digest.get("summary_by_agent") or {}).get(agent_id)
        if text:
            parts.append(f"{AGENT_LABELS[agent_id]} ({text})")
    if not parts:
        return ""
    return " Laut Tick-Protokoll: " + "; ".join(parts[:3]) + "."


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


def _format_factor_labels_short(
    catalog: dict[str, Any], states: dict[str, str], *, max_items: int = 4
) -> str:
    bits: list[str] = []
    for factor_id in FACTOR_IDS:
        state_id = states.get(factor_id)
        if not state_id:
            continue
        bits.append(f"{factor_id} {_factor_state_label(catalog, factor_id, state_id)}")
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

    lines = [f"Lauf «{sim_name}», {ticks} Ticks: Nachfrage {booking}, Ticketpreis {price}."]

    transitions = factor_profile.get("transitions") or []
    if transitions:
        shown = transitions[:4]
        change_bits = [
            f"Tick {item['tick']} {item['factor_id']} {item['from_state']}→{item['to_state']}"
            for item in shown
        ]
        extra = (
            f" (+{len(transitions) - len(shown)} weitere)" if len(transitions) > len(shown) else ""
        )
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
            f"{factor_id} {end_by_id.get(factor_id)}→{states.get(factor_id)}" for factor_id in diffs
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
    agent_digest: dict[str, Any] | None = None,
) -> str:
    """Sachliche Szenario-Beschreibung — aus Faktoren, Lauf und Agenten-Perspektiven."""
    agent_digest = agent_digest or context.agent_digest
    agent_clause = _agent_perspective_clause(agent_digest)
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
            f"die gesellschaftliche Akzeptanz von Flugreisen.{agent_clause}"
        )

    if scenario_kind == "alternative":
        return (
            f"«{slide_title}»: Gegenüber der Lauf-Endlage weicht mindestens ein Faktor ab "
            f"(siehe oben). Typisch: Verschiebungen bei {f1} und {f2}. {f5} und {f6} "
            f"können Modal Shift verstärken oder dämpfen. Explorative Konstellation, keine Prognose."
            f"{agent_clause}"
        )

    return (
        f"«{slide_title}»: Widersprüchliche Faktortrends ({f1} vs. {f2}). "
        f"Anpassungsdruck auf Politik, Anbieter und Nachfrage. {f6} kann Spannungen verstärken."
        f"{agent_clause}"
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

    tick_grounding = build_scenario_tick_grounding(context, factor_profile, catalog, states)
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


def _pick_alternative_constellation(
    end_states: dict[str, str], transitions: list[dict[str, Any]]
) -> dict[str, str]:
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
    _score_constellations(context, scenarios)
    return scenarios


def _plausibility_from_score(score: float | None, *, rank: int | None = None) -> str:
    """Map a CIB consistency score to a qualitative plausibility band.

    Plausibility is thereby grounded in the CIB matrix instead of the mere
    presentation rank. Falls back to rank-based bands when no score exists.
    """
    if score is None:
        return _plausibility_for_rank(rank) if rank is not None else "mittel"
    if score >= 0.7:
        return "hoch"
    if score >= 0.4:
        return "mittel"
    return "niedrig"


def _score_constellations(
    context: RunScenarioContext,
    scenarios: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach the CIB consistency_score and score-based plausibility in place."""
    if isinstance(context.cib_matrix, dict):
        try:
            from src.models.cib_models import CIBMatrix
            from src.scenario_consistency import ConsistencyChecker, ScenarioDescriptor

            matrix_obj = CIBMatrix.model_validate(context.cib_matrix)
            checker = ConsistencyChecker(matrix_obj)
            for sc in scenarios:
                desc = ScenarioDescriptor(factor_states=sc["factor_constellation"])
                sc["consistency_score"] = round(checker.compute_consistency_score(desc), 3)
        except Exception:
            for sc in scenarios:
                sc["consistency_score"] = None
    else:
        for sc in scenarios:
            sc["consistency_score"] = None

    for sc in scenarios:
        sc["plausibility"] = _plausibility_from_score(
            sc.get("consistency_score"), rank=sc.get("rank")
        )
    return scenarios


def _delta_from_end(end_states: dict[str, str], states: dict[str, str]) -> list[str]:
    """Human-readable factor differences of a constellation vs. the run end state."""
    diffs: list[str] = []
    for factor_id in FACTOR_IDS:
        target = states.get(factor_id)
        base = end_states.get(factor_id)
        if target and base and target != base:
            diffs.append(f"{factor_id} {base}→{target}")
    return diffs


def build_candidate_constellations(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Deterministic set of CIB-scored future constellations for LLM *selection*.

    Python derives every candidate (continuation, single-factor alternatives,
    cross-impact tension) from the run end state and scores each with the CIB
    matrix. The LLM later selects and justifies three of them — it never invents
    factor states, which keeps the scenario space reproducible and grounded.
    """
    end_states = dict(factor_profile.get("end_by_id") or {})
    if not end_states:
        end_states = {f"F{i}": f"F{i}.1" for i in range(1, 8)}

    transitions = factor_profile.get("transitions") or []
    raw: list[tuple[str, dict[str, str]]] = [("fortsetzung", dict(end_states))]

    pivots: list[str] = []
    for item in transitions:
        fid = str(item.get("factor_id") or "")
        if fid and fid not in pivots:
            pivots.append(fid)
    for fid in ("F1", "F2", "F3", "F5", "F6"):
        if fid not in pivots:
            pivots.append(fid)
    for fid in pivots:
        if fid not in end_states:
            continue
        alt = dict(end_states)
        alt[fid] = _flip_state(str(alt[fid]))
        raw.append(("alternative", alt))

    raw.append(("spannung", _pick_tension_constellation(end_states)))

    seen: set[frozenset] = set()
    candidates: list[dict[str, Any]] = []
    for kind, states in raw:
        key = frozenset(states.items())
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "scenario_kind": kind,
                "factor_constellation": dict(states),
                "tick_grounding": build_scenario_tick_grounding(
                    context, factor_profile, catalog, states
                ),
                "delta_from_end": _delta_from_end(end_states, states),
            }
        )

    _score_constellations(context, candidates)

    def _sort_key(item: dict[str, Any]) -> tuple[int, float]:
        kind_rank = 0 if item.get("scenario_kind") == "fortsetzung" else 1
        score = item.get("consistency_score")
        score = float(score) if isinstance(score, (int, float)) else -1.0
        return (kind_rank, -score)

    candidates.sort(key=_sort_key)
    candidates = candidates[:7]
    for index, item in enumerate(candidates, start=1):
        item["candidate_id"] = f"C{index}"
    return candidates


def _select_phase_ticks(
    ticks: list[dict[str, Any]], *, max_phases: int = 3
) -> list[dict[str, Any]]:
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
    phase_ticks = _select_phase_ticks(ticks)
    event_log = _load_json(directory / "event_log.json", [])
    event_log = event_log if isinstance(event_log, list) else []
    return RunScenarioContext(
        run_id=run_id,
        run_dir=directory,
        metadata=metadata if isinstance(metadata, dict) else {},
        tick_mechanics=tick_mechanics if isinstance(tick_mechanics, dict) else {"ticks": []},
        event_log=event_log,
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
        phase_ticks=phase_ticks,
        agent_digest=build_agent_digest(
            run_dir=directory,
            phase_ticks=phase_ticks,
            event_log=event_log,
        ),
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


SCENARIO_MIN_STORY_LEN = 200


def _fallback_story_for_candidate(
    candidate: dict[str, Any],
    *,
    context: RunScenarioContext,
    catalog: dict[str, Any],
) -> str:
    """Deterministic story used when the LLM story is missing or too thin."""
    return _build_scenario_description(
        scenario_kind=candidate.get("scenario_kind", "explorativ"),
        slide_title=_slide_scenario_title(candidate.get("scenario_kind", "")),
        context=context,
        catalog=catalog,
        states=candidate.get("factor_constellation", {}),
    )


def _normalize_scenarios(
    raw: Any,
    *,
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Map the LLM's candidate *selection* back to Python-owned constellations.

    The LLM only contributes title + story and chooses which candidate to use
    via ``candidate_id``. Factor states, CIB score and tick grounding are taken
    verbatim from the deterministic candidate so nothing numeric is invented.
    """
    candidates = build_candidate_constellations(context, factor_profile, catalog)
    candidates_by_id = {c["candidate_id"]: c for c in candidates}
    canonical = build_explorative_scenarios(context, factor_profile, catalog)

    selected: list[dict[str, Any]] = []
    used_keys: set[frozenset] = set()

    if isinstance(raw, list):
        for index, item in enumerate(raw):
            if len(selected) >= 3 or not isinstance(item, dict):
                continue
            cand_id = str(item.get("candidate_id") or "").strip().upper()
            candidate = candidates_by_id.get(cand_id)
            if candidate is None and index < len(candidates):
                candidate = candidates[index]
            if candidate is None:
                continue
            key = frozenset(candidate["factor_constellation"].items())
            if key in used_keys:
                continue
            used_keys.add(key)

            story = str(
                item.get("story") or item.get("what_could_happen") or item.get("narrative") or ""
            ).strip()
            if len(story) < SCENARIO_MIN_STORY_LEN:
                story = _fallback_story_for_candidate(candidate, context=context, catalog=catalog)

            scenario_kind = candidate.get("scenario_kind", "explorativ")
            selected.append(
                {
                    "title": str(item.get("title") or _slide_scenario_title(scenario_kind)),
                    "scenario_kind": scenario_kind,
                    "consistency_score": candidate.get("consistency_score"),
                    "factor_constellation": dict(candidate.get("factor_constellation", {})),
                    "tick_grounding": candidate.get("tick_grounding", ""),
                    "candidate_id": candidate.get("candidate_id"),
                    "story": story,
                    "what_could_happen": story,
                }
            )

    # Guarantee three distinct paths: fill from the canonical fortsetzung/
    # alternative/spannung defaults if the LLM selected fewer.
    if len(selected) < 3:
        for fallback in canonical:
            key = frozenset((fallback.get("factor_constellation") or {}).items())
            if key in used_keys:
                continue
            used_keys.add(key)
            selected.append(dict(fallback))
            if len(selected) >= 3:
                break

    selected = selected[:3]
    for index, item in enumerate(selected, start=1):
        item["rank"] = index
        item["id"] = f"S{index}"
        item["plausibility"] = _plausibility_from_score(item.get("consistency_score"), rank=index)
    return selected


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
        "agent_digest": context.agent_digest,
        "scenarios": scenarios,
        "limitations": (
            "Explorative Szenarien, sachlich aus dem Lauf abgeleitet — keine Prognose, keine Fiktion."
        ),
        "source": "template",
    }


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
    parser = argparse.ArgumentParser(
        description="Generate run_scenario.md/json for a completed run."
    )
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
