"""Event log persistence and narrative-ordering helpers."""

import json
from pathlib import Path
from typing import List

from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path

NARRATIVE_AGENT_ORDER = ("provider", "regulator", "consumer")


def agent_responses_for_round(state, round_number: int):
    """Merge agent responses from all round_results for one tick."""

    by_agent: dict[str, object] = {}
    for round_result in state.round_results:
        if round_result.round_number != round_number:
            continue
        for response in round_result.agent_responses:
            by_agent[response.agent_id] = response

    ordered = [by_agent[agent_id] for agent_id in NARRATIVE_AGENT_ORDER if agent_id in by_agent]
    for agent_id in sorted(by_agent.keys()):
        if agent_id not in NARRATIVE_AGENT_ORDER:
            ordered.append(by_agent[agent_id])
    return ordered


def narrative_events_for_round(state, round_number: int) -> list[EventLogEntry]:
    """Agent events for narrative display (excludes deterministic market updates)."""

    events = [
        event
        for event in state.event_log
        if event.round_number == round_number and event.event_type != EventType.MARKET_EVENT
    ]
    order_index = {agent_id: index for index, agent_id in enumerate(NARRATIVE_AGENT_ORDER)}
    return sorted(
        events,
        key=lambda event: (
            order_index.get(event.source_agent, len(NARRATIVE_AGENT_ORDER)),
            event.timestamp or "",
            event.id,
        ),
    )


def save_event_log(
    events: List[EventLogEntry],
    filename: str = "event_log.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die Event-Log-Einträge als JSON.
        Liste von EventLogEntry-Objekten
        Default Name der Ausgabedatei: event_log.json
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)
    events_data = [event.model_dump() for event in events]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)
    return filepath
