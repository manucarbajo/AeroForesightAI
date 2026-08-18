"""Aggregate tick-level agent narratives for scenario synthesis (Option B)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.reporting.run_scenario_generator.context import _load_json

AGENT_IDS = ("consumer", "provider", "regulator")
AGENT_LABELS = {
    "consumer": "Passagiere (Consumer)",
    "provider": "Airlines (Provider)",
    "regulator": "Politik (Regulator)",
}
_EMPTY_AGENT_REASONING = frozenset(
    {"mock", "noop", "fallback", "kein reasoning geliefert.", "kein reasoning geliefert"}
)


def _phase_label(index: int) -> str:
    return ["Frühphase", "Mittelphase", "Spätphase"][min(index, 2)]


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
