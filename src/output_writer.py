import json
import os
from pathlib import Path
from typing import List
from datetime import UTC, datetime

from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.property_engine import property_value_changes_at_tick, scheduled_property_events

_NARRATIVE_AGENT_ORDER = ("provider", "regulator", "consumer")


def _agent_responses_for_round(state, round_number: int):
    """Merge agent responses from all round_results for one tick."""

    by_agent: dict[str, object] = {}
    for round_result in state.round_results:
        if round_result.round_number != round_number:
            continue
        for response in round_result.agent_responses:
            by_agent[response.agent_id] = response

    ordered = [by_agent[agent_id] for agent_id in _NARRATIVE_AGENT_ORDER if agent_id in by_agent]
    for agent_id in sorted(by_agent.keys()):
        if agent_id not in _NARRATIVE_AGENT_ORDER:
            ordered.append(by_agent[agent_id])
    return ordered


def _narrative_events_for_round(state, round_number: int) -> list[EventLogEntry]:
    """Agent events for narrative display (excludes deterministic market updates)."""

    events = [
        event
        for event in state.event_log
        if event.round_number == round_number and event.event_type != EventType.MARKET_EVENT
    ]
    order_index = {agent_id: index for index, agent_id in enumerate(_NARRATIVE_AGENT_ORDER)}
    return sorted(
        events,
        key=lambda event: (
            order_index.get(event.source_agent, len(_NARRATIVE_AGENT_ORDER)),
            event.timestamp or "",
            event.id,
        ),
    )

# Projekt-Root relativ zu dieser Datei (…/src/output_writer.py → Repo-Root)
_REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = str(_REPO_ROOT / "outputs")


def create_run_id(prefix: str = "run") -> str:
    """Create a unique run directory name, e.g. ``run_20260603T143022Z``."""

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{timestamp}"


def ensure_output_dir():
    """Stellt sicher, dass der Output-Ordner existiert."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def resolve_run_output_dir(run_id: str | None = None) -> Path:
    """Return ``outputs/<run_id>/``, creating the directory when needed."""

    ensure_output_dir()
    resolved_run_id = run_id or create_run_id()
    run_dir = Path(OUTPUT_DIR) / resolved_run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _resolve_output_path(
    filename: str,
    output_subdir: str | Path | None = None,
    *,
    run_dir: Path | None = None,
) -> str:
    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        return str(run_dir / filename)

    ensure_output_dir()
    if output_subdir is None:
        target_dir = Path(OUTPUT_DIR)
    else:
        subdir_path = Path(output_subdir)
        target_dir = subdir_path if subdir_path.is_absolute() else Path(OUTPUT_DIR) / subdir_path
        target_dir.mkdir(parents=True, exist_ok=True)
    return str(target_dir / filename)


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
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    
    # Konvertiere alle Events zu Dictionaries für JSON
    events_data = [event.model_dump() for event in events]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def save_population_timeseries(
    population_stats: list[dict],
    filename: str = "timeseries/population.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick segment booking rates derived from population_stats."""

    if not population_stats:
        return None

    rows: list[dict] = []
    for tick_stats in population_stats:
        tick = tick_stats.get("round_number")
        for segment_id, segment in tick_stats.get("segments", {}).items():
            rows.append(
                {
                    "tick": tick,
                    "segment_id": segment_id,
                    "total_individuals": segment.get("total_individuals", 0),
                    "booked_individuals": segment.get("booked_individuals", 0),
                    "booking_rate": segment.get("booking_rate", 0.0),
                    "avg_income_factor": segment.get("avg_income_factor", 1.0),
                }
            )

    if not rows:
        return None

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(_resolve_output_path(filename, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return str(target_path)


def save_population_individuals(
    individuals: list,
    filename: str = "population.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save final persistent individuals (age, labels, WTP, booking)."""

    if not individuals:
        return None

    rows: list[dict] = []
    for person in individuals:
        data = person.model_dump() if hasattr(person, "model_dump") else person
        row = {
            "id": data.get("id"),
            "age": data.get("age"),
            "wtp_eur": data.get("wtp_eur"),
            "environmental_awareness": data.get("environmental_awareness"),
            "price_sensitivity": data.get("price_sensitivity"),
            "income_factor": data.get("income_factor", 1.0),
            "booked": data.get("booked"),
        }
        for label_id, active in (data.get("labels") or {}).items():
            row[label_id] = active
        rows.append(row)

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(_resolve_output_path(filename, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return str(target_path)


def save_factors_timeseries(
    rows: list[dict],
    filename: str = "timeseries/factors.csv",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick factor descriptor states as CSV (M5)."""

    if not rows:
        return None

    ensure_output_dir()
    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(_resolve_output_path(filename, output_subdir, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return str(target_path)


def save_properties_timeseries(
    rows: list[dict],
    filename: str = "timeseries/properties.csv",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick system property values as CSV."""

    if not rows:
        return None

    ensure_output_dir()
    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(_resolve_output_path(filename, output_subdir, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return str(target_path)


def save_price_history(
    price_entries: List[PriceHistoryEntry],
    filename: str = "price_history.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die Preis-Historie als JSON.
        price_entries: Liste von PriceHistoryEntry-Objekten
        Default Name der Ausgabedatei: price_history.json
    
    Returns:
        Pfad zur gespeicherten Datei
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    
    # Konvertiere alle Einträge zu Dictionaries für JSON
    price_data = [entry.model_dump() for entry in price_entries]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def save_round_history(
    round_results: List,
    filename: str = "round_history.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die Rundenhistorie als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: round_history.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)

    round_data = [round_result.model_dump() for round_result in round_results]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(round_data, f, indent=2, ensure_ascii=False)

    return filepath

def save_run_metadata(
    state,
    args,
    filename: str = "run_metadata.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
    run_id: str | None = None,
) -> str:
    """
    Speichert Metadaten des Simulationslaufs als JSON.
        state: finaler SimulationState
        args: geparste CLI-Argumente
        Default Name der Ausgabedatei: run_metadata.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)

    metadata = {
        "timestamp": datetime.now(UTC).isoformat(),
        "run_id": run_id or (run_dir.name if run_dir is not None else None),
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "ticks_completed": state.clock.current_tick,
        "ticks_max": state.clock.max_ticks,
        "tick_unit": state.clock.tick_unit,
        "market_enabled": not args.no_market,
        "total_events": len(state.event_log),
        "total_round_results": len(state.round_results),
        "total_price_history": len(state.price_history),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return filepath

def save_segment_analysis(
    round_results: List,
    filename: str = "segment_analysis.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die segmentspezifischen Analysen aller Agenten als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: segment_analysis.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)

    # Gruppiere nach Rundennummer
    rounds: dict = {}
    for round_result in round_results:
        round_number = round_result.round_number
        if round_number not in rounds:
            rounds[round_number] = {
                "tick": round_number,
                "agents": {}
            }
        # Alle Agenten speichern
        for response in round_result.agent_responses:
            rounds[round_number]["agents"][response.agent_id] = {
                "reasoning": response.reasoning,
                "actions": response.actions,
                "segment_analysis": response.segment_analysis,
            }

    segment_data = list(rounds.values())

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(segment_data, f, indent=2, ensure_ascii=False)

    return filepath

def _format_property_event_line(event: dict[str, object]) -> str:
    tick = event["tick"]
    prop_id = event["property_id"]
    effect_type = event["effect_type"]
    value = event["value"]
    unit = event.get("unit") or ""

    if effect_type == "set":
        detail = f"set → {value}"
    elif effect_type == "ramp":
        duration = event.get("duration_ticks", 1)
        detail = f"ramp → {value} über {duration} Tick(s)"
    else:
        detail = f"step_function → {value}"

    unit_suffix = f" {unit}" if unit else ""
    description = event.get("description")
    desc_suffix = f" ({description})" if description else ""
    return f"- **Tick {tick}:** `{prop_id}` {detail}{unit_suffix}{desc_suffix}"


def _format_property_change_line(prop_id: str, old_value: float, new_value: float) -> str:
    return f"- `{prop_id}`: {old_value:g} → {new_value:g}"


def save_final_narrative(
    state,
    filename: str = "final_narrative.md",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert eine lesbare Markdown-Zusammenfassung der Simulation.
        state: finaler SimulationState
        Default Name der Ausgabedatei: final_narrative.md
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)

    lines = []

    start_tick = 1 if state.clock.current_tick >= 1 else None
    end_tick = state.clock.current_tick if state.clock.current_tick >= 1 else None

    # Titel
    lines.append(f"# Simulationsbericht: {state.config.name}")
    lines.append(f"\n{state.config.description}\n")

    # Überblick
    lines.append("## Überblick")
    lines.append(f"- **Simulierte Ticks:** {state.clock.current_tick} / {state.clock.max_ticks}")
    if start_tick is not None and end_tick is not None:
        lines.append(f"- **Tick-Bereich:** Tick {start_tick} – Tick {end_tick}")
    lines.append(f"- **Gesamte Events:** {len(state.event_log)}")
    lines.append(f"- **Preis Start:** {state.price_history[0].price:.2f} €" if state.price_history else "- **Preis Start:** n/a")
    lines.append(f"- **Preis Ende:** {state.price_history[-1].price:.2f} €" if state.price_history else "- **Preis Ende:** n/a")

    properties = state.resolved_properties()
    schedule = scheduled_property_events(properties)
    if schedule:
        lines.append("\n## Property-Zeitplan (Config)")
        lines.append("Geplante System-Property-Änderungen aus `properties.json`:")
        for event in schedule:
            lines.append(_format_property_event_line(event))

    shift_rules = properties.shift_rules
    if shift_rules:
        lines.append("\nDynamische Populations-Shift-Regeln:")
        for rule in shift_rules:
            when = rule.when
            effect = rule.effect
            when_parts = []
            if "factor" in when:
                when_parts.append(f"Faktor {when['factor']} = {when.get('state', '?')}")
            if "system_property" in when:
                prop = when["system_property"]
                if "above" in when:
                    when_parts.append(f"`{prop}` > {when['above']}")
                elif "below" in when:
                    when_parts.append(f"`{prop}` < {when['below']}")
                else:
                    when_parts.append(f"`{prop}`")
            when_label = ", ".join(when_parts) if when_parts else "immer"
            effect_label = (
                f"`{effect.get('property', '?')}` "
                f"{effect.get('delta', 0):+g}"
            )
            lines.append(f"- Wenn {when_label}: {effect_label}")

    scheduled_by_tick: dict[int, list[dict[str, object]]] = {}
    for event in schedule:
        tick = int(event["tick"])
        scheduled_by_tick.setdefault(tick, []).append(event)

    # Tick-Übersicht
    lines.append("\n## Tick-Übersicht")
    round_numbers = sorted(
        {
            rr.round_number
            for rr in state.round_results
            if rr.round_number >= 1
        }
        | {
            event.round_number
            for event in state.event_log
            if event.round_number >= 1
        }
    )

    for round_number in round_numbers:
        tick_label = state.clock.tick_label(round_number)
        lines.append(f"\n### {tick_label}")

        tick_events = scheduled_by_tick.get(round_number, [])
        if tick_events:
            lines.append("\n**Geplante Property-Shocks (dieser Tick):**")
            for event in tick_events:
                lines.append(_format_property_event_line(event))

        value_changes = property_value_changes_at_tick(state.property_timeseries, round_number)
        if value_changes:
            lines.append("\n**Wirksame Property-Änderungen (Markt):**")
            for prop_id, old_value, new_value in value_changes:
                lines.append(_format_property_change_line(prop_id, old_value, new_value))

        agent_responses = _agent_responses_for_round(state, round_number)
        for resp in agent_responses:
            first_line = resp.reasoning.strip().splitlines()[0] if resp.reasoning else "kein Reasoning"
            lines.append(f"- **{resp.agent_id}:** {first_line}")

        # Markt-Kennzahlen der Runde (M2 demand_level + M3 booking_rate)
        price_entry = next((entry for entry in state.price_history if entry.round_number == round_number), None)
        if price_entry is not None:
            market_line = (
                f"- **Markt:** Preis {price_entry.price:.2f} €, "
                f"demand_level {price_entry.demand_level:.3f}"
            )
            if price_entry.booking_rate is not None:
                market_line += f", booking_rate {price_entry.booking_rate:.1%}"
            lines.append(f"\n{market_line}")

        narrative_events = _narrative_events_for_round(state, round_number)
        if narrative_events:
            lines.append(f"\n**Events ({len(narrative_events)}):**")
            for event in narrative_events:
                lines.append(f"- {event.source_agent}: {event.description}")

        # Population Stats der Runde
        if hasattr(state, "population_stats") and state.population_stats:
            stats_for_round = next((s for s in state.population_stats if s.get("round_number") == round_number), None)
            if stats_for_round:
                lines.append(f"\n**Populations-Statistik:**")
                lines.append(f"- **Total Demand:** {stats_for_round['total_demand']:.1%} ({stats_for_round['total_booked']} von {stats_for_round['total_population']} gebucht)")
                for seg_id, seg_data in stats_for_round["segments"].items():
                    lines.append(f"  - {seg_id}: {seg_data['booked_individuals']}/{seg_data['total_individuals']} (Rate: {seg_data['booking_rate']:.1%})")

    # Finaler Umweltzustand
    lines.append("\n## Finaler Umweltzustand")
    for factor_id, factor in state.environment.factors.items():
        state_label = factor.possible_states.get(factor.current_state, factor.current_state)
        lines.append(f"- **{factor.name}:** {factor.current_state} – {state_label}")

    # Population Stats
    if hasattr(state, "population_stats") and state.population_stats:
        last_stats = state.population_stats[-1]
        lines.append("\n## Populations-Statistik (Aktueller Stand)")
        lines.append(f"- **Total Demand:** {last_stats['total_demand']:.1%} ({last_stats['total_booked']} von {last_stats['total_population']} gebucht)")
        lines.append("- **Segment-Details:**")
        for seg_id, seg_data in last_stats["segments"].items():
            lines.append(f"  - **{seg_id}** (Anteil: {seg_data['share']:.1%}): {seg_data['booked_individuals']} gebucht / {seg_data['total_individuals']} gesamt (Rate: {seg_data['booking_rate']:.1%})")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath

def save_cib_matrix(
    state,
    filename: str = "cib_matrix.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die CIB-Matrix als JSON.
        state: finaler SimulationState
        Default Name der Ausgabedatei: cib_matrix.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)

    if state.cib_matrix is None:
        cib_data = {"entries": [], "round_generated": 0, "metadata": {}}
    else:
        cib_data = state.cib_matrix.model_dump()

        # Faktornamen direkt in source_factor und target_factor einbetten
        enriched_entries = []
        for entry in cib_data["entries"]:
            source_id = entry["source_factor"]
            target_id = entry["target_factor"]

            source_factor = state.environment.factors.get(source_id)
            target_factor = state.environment.factors.get(target_id)

            entry["source_factor"] = f"{source_id} - {source_factor.name}" if source_factor else source_id
            entry["target_factor"] = f"{target_id} - {target_factor.name}" if target_factor else target_id

            enriched_entries.append(entry)

        cib_data["entries"] = enriched_entries

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cib_data, f, indent=2, ensure_ascii=False)

    return filepath


def save_protocol(
    protocol_payload: dict,
    filename: str = "protocol.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save structured conversation protocol as JSON."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(protocol_payload, f, indent=2, ensure_ascii=False)
    return filepath


def save_protocol_markdown(
    markdown: str,
    filename: str = "protocol.md",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save conversation protocol as Markdown."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    return filepath


def save_scenarios(
    payload: dict,
    filename: str = "scenarios.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save derived scenarios as JSON."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return filepath


def save_scenarios_markdown(
    markdown: str,
    filename: str = "scenarios.md",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save derived scenarios as Markdown."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    return filepath

def save_age_property_csv(
    population_stats: list[dict],
    filename: str = "timeseries/age_property.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Save per-tick age group stats."""

    if not population_stats:
        return None

    rows: list[dict] = []
    for tick_stats in population_stats:
        tick = tick_stats.get("round_number")
        for age_group, group_stats in tick_stats.get("age_groups", {}).items():
            rows.append(
                {
                    "tick": tick,
                    "age_group": age_group,
                    "total_individuals": group_stats.get("total_individuals", 0),
                    "booked_individuals": group_stats.get("booked_individuals", 0),
                    "booking_rate": group_stats.get("booking_rate", 0.0),
                    "avg_wtp": group_stats.get("avg_wtp", 0.0),
                    "avg_income_factor": group_stats.get("avg_income_factor", 1.0),
                    "avg_awareness": group_stats.get("avg_awareness", 0.0),
                }
            )

    if not rows:
        return None

    if run_dir is not None:
        target_path = run_dir / filename
    else:
        target_path = Path(_resolve_output_path(filename, run_dir=run_dir))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return str(target_path)
