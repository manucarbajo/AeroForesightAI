import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import List

from src.market.property_engine import scheduled_property_events
from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry

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
            "substitution_readiness": data.get("substitution_readiness"),
            "price_sensitivity": data.get("price_sensitivity"),
            "income_factor": data.get("income_factor", 1.0),
            "saturation_level": data.get("saturation_level", 0.0),
            "booked": data.get("booked"),
            "last_booked_tick": data.get("last_booked_tick"),
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


def append_individuals_history(
    tick: int,
    individuals: list,
    filename: str = "individuals_history.csv",
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Append individual states for a single tick to the history CSV."""
    if not individuals:
        return None

    rows: list[dict] = []
    for person in individuals:
        data = person.model_dump() if hasattr(person, "model_dump") else person
        row = {
            "tick": tick,
            "id": data.get("id"),
            "age": data.get("age"),
            "wtp_eur": data.get("wtp_eur"),
            "environmental_awareness": data.get("environmental_awareness"),
            "substitution_readiness": data.get("substitution_readiness"),
            "price_sensitivity": data.get("price_sensitivity"),
            "income_factor": data.get("income_factor", 1.0),
            "saturation_level": data.get("saturation_level", 0.0),
            "booked": data.get("booked"),
            "last_booked_tick": data.get("last_booked_tick"),
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

    file_exists = target_path.is_file()
    lines = []
    if not file_exists:
        lines.append(",".join(columns))

    for row in rows:
        lines.append(",".join(str(row.get(column, "")) for column in columns))

    with open(target_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

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
        "simulation_name": getattr(args, "simulation_name", None),
        "simulation_description": getattr(args, "simulation_description", None),
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

    rounds: dict = {}
    for round_result in round_results:
        round_number = round_result.round_number
        if round_number not in rounds:
            rounds[round_number] = {"tick": round_number, "agents": {}}
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


def _prior_population_stats(state, round_number: int) -> dict | None:
    for entry in reversed(state.population_stats):
        tick = entry.get("round_number")
        if tick is not None and tick < round_number:
            return entry
    return None


def _prior_price_entry(state, round_number: int) -> PriceHistoryEntry | None:
    for entry in reversed(state.price_history):
        if 1 <= entry.round_number < round_number:
            return entry
    return None


def _scheduled_shocks_for_tick(
    scheduled_by_tick: dict[int, list[dict[str, object]]],
    round_number: int,
) -> list[dict[str, object]]:
    return [
        {
            "property_id": event["property_id"],
            "effect_type": event["effect_type"],
            "value": event["value"],
            "unit": event.get("unit"),
        }
        for event in scheduled_by_tick.get(round_number, [])
    ]


def _interpret_tick_mechanics(record: dict[str, object]) -> list[str]:
    """Generate short causal explanations for counter-intuitive tick patterns."""

    notes: list[str] = []
    br_delta = record.get("booking_rate_delta")
    price_delta = record.get("market_price_delta_eur")
    ref_price = record.get("booking_reference_price_eur")
    post_price = record.get("market_price_after_feedback_eur")
    pop_delta = record.get("population_delta")

    if (
        isinstance(br_delta, (int, float))
        and br_delta > 0.02
        and isinstance(price_delta, (int, float))
        and price_delta > 1.0
        and isinstance(ref_price, (int, float))
        and isinstance(post_price, (int, float))
    ):
        notes.append(
            "Buchung stieg, obwohl der **Endpreis** dieses Ticks stieg: Die Entscheidung "
            f"fiel bei Referenzpreis **{ref_price:.2f} €** (Vortick-Marktpreis). "
            f"Der Anstieg auf **{post_price:.2f} €** ist **Folge** der Buchung (Markt-Feedback), "
            "nicht deren Ursache."
        )

    if (
        isinstance(br_delta, (int, float))
        and br_delta < -0.02
        and isinstance(price_delta, (int, float))
        and price_delta < -1.0
    ):
        notes.append(
            "Buchung fiel, während der Endpreis sank: Markt-Feedback senkt den Preis bei "
            "schwacher Buchung — beides hängt am selben Regelkreis."
        )

    shocks = record.get("scheduled_shocks") or []
    shock_ids = {str(s.get("property_id")) for s in shocks if isinstance(s, dict)}

    if "carbon_tax_level" in shock_ids and isinstance(br_delta, (int, float)) and br_delta >= -0.01:
        notes.append(
            "CO₂-Steuer stieg, Buchung blieb stabil oder stieg: Die Steuer wirkt schwach in "
            "der Kostenformel (`carbon_per_tonne` sehr klein). Für die Buchung zählt der "
            "Referenz-Ticketpreis (Vortick), nicht der neue `cost_pressure`. Zusätzlich kann "
            "Markt-Feedback den Verkaufspreis **senken**, obwohl Kosten steigen."
        )

    if "income_index" in shock_ids and isinstance(br_delta, (int, float)) and br_delta > 0.02:
        notes.append(
            "Einkommensindex stieg — höhere Zahlungsbereitschaft aller Individuen "
            "erklärt den Buchungsanstieg unabhängig vom späteren Preis-Feedback."
        )

    if isinstance(pop_delta, int) and pop_delta > 0:
        notes.append(
            f"Population wuchs um **+{pop_delta}** Personen. Neue Individuen werden frisch "
            "gesampelt und fließen direkt in die Buchungsrate ein."
        )

    cost_pressure = record.get("cost_pressure_eur")
    if (
        isinstance(post_price, (int, float))
        and isinstance(cost_pressure, (int, float))
        and post_price < cost_pressure - 5
    ):
        notes.append(
            f"Verkaufspreis ({post_price:.2f} €) liegt unter `cost_pressure` "
            f"({cost_pressure:.2f} €) — der Anbieter verkauft unter Kosten; "
            "Markt-Feedback und Markup-Regeln entkoppeln Preis und Kosten."
        )

    return notes


def _build_tick_mechanics_record(
    state,
    round_number: int,
    *,
    scheduled_by_tick: dict[int, list[dict[str, object]]],
) -> dict[str, object]:
    ts_row = next(
        (row for row in state.property_timeseries if row.get("tick") == round_number),
        None,
    )
    stats = next(
        (s for s in state.population_stats if s.get("round_number") == round_number),
        None,
    )
    prior_stats = _prior_population_stats(state, round_number)
    price_entry = next(
        (entry for entry in state.price_history if entry.round_number == round_number),
        None,
    )

    ref_price = None
    post_price = None
    if ts_row is not None:
        ref_price = ts_row.get("ticket_price_pre_feedback", ts_row.get("ticket_price"))
        post_price = ts_row.get("ticket_price")

    booking_rate = stats.get("total_demand") if stats else None
    prior_booking = prior_stats.get("total_demand") if prior_stats else None
    br_delta = (
        float(booking_rate) - float(prior_booking)
        if booking_rate is not None and prior_booking is not None
        else None
    )

    pop = stats.get("total_population") if stats else None
    prior_pop = prior_stats.get("total_population") if prior_stats else None
    pop_delta = int(pop) - int(prior_pop) if pop is not None and prior_pop is not None else None

    price_delta = (
        float(post_price) - float(ref_price)
        if ref_price is not None and post_price is not None
        else None
    )

    record: dict[str, object] = {
        "tick": round_number,
        "pipeline_order": [
            "apply_factor_rules",
            "agent_round (provider/regulator)",
            "population_booking (uses prior tick market price as reference)",
            "consumer_narrative",
            "market_feedback (sets final ticket price)",
        ],
        "scheduled_shocks": _scheduled_shocks_for_tick(scheduled_by_tick, round_number),
        "booking_reference_price_eur": ref_price,
        "market_price_after_feedback_eur": post_price,
        "market_price_delta_eur": price_delta,
        "booking_rate": booking_rate,
        "prior_booking_rate": prior_booking,
        "booking_rate_delta": br_delta,
        "population": pop,
        "population_delta": pop_delta,
        "booked": stats.get("total_booked") if stats else None,
        "carbon_tax_level": ts_row.get("carbon_tax_level") if ts_row else None,
        "income_index": ts_row.get("income_index") if ts_row else None,
        "cost_pressure_eur": ts_row.get("cost_pressure") if ts_row else None,
        "demand_level": price_entry.demand_level if price_entry else None,
        "interpretation": [],
    }
    record["interpretation"] = _interpret_tick_mechanics(record)
    return record


def _format_shock_short(shock: dict[str, object]) -> str:
    prop_id = str(shock.get("property_id", ""))
    value = shock.get("value")
    labels = {
        "carbon_tax_level": "CO₂-Steuer",
        "saf_mandate_share": "SAF-Mandat",
        "income_index": "Einkommen",
        "bevoelkerungsentwicklung": "Population",
        "fuel_price_change": "Treibstoff",
        "oil_price_index": "Ölpreis",
    }
    label = labels.get(prop_id, prop_id)
    if prop_id == "saf_mandate_share" and isinstance(value, (int, float)):
        return f"{label} {float(value):.0%}"
    if isinstance(value, (int, float)) and prop_id != "bevoelkerungsentwicklung":
        return f"{label} {value:g}"
    if isinstance(value, (int, float)):
        return f"{label} {int(value)}"
    return label


def _format_tick_summary_markdown(record: dict[str, object]) -> list[str]:
    """One compact ground-truth line per tick; interpretation only when surprising."""

    chunks: list[str] = []
    br = record.get("booking_rate")
    booked = record.get("booked")
    pop = record.get("population")
    br_delta = record.get("booking_rate_delta")
    ref = record.get("booking_reference_price_eur")
    post = record.get("market_price_after_feedback_eur")

    if br is not None and booked is not None and pop is not None:
        booking_part = f"**{float(br):.1%}** gebucht ({booked}/{pop})"
        if isinstance(br_delta, (int, float)) and abs(float(br_delta)) >= 0.001:
            booking_part += f", Δ {float(br_delta):+.1%} pp"
        chunks.append(booking_part)

    if isinstance(ref, (int, float)) and isinstance(post, (int, float)):
        delta = float(post) - float(ref)
        chunks.append(f"Preis {float(ref):.2f} → {float(post):.2f} € ({delta:+.2f} €)")

    shocks = record.get("scheduled_shocks") or []
    if shocks:
        shock_text = ", ".join(
            part
            for shock in shocks
            if isinstance(shock, dict) and shock.get("property_id") != "carbon_tax_level"
            for part in [_format_shock_short(shock)]
            if part
        )
        if shock_text:
            chunks.append(f"Shocks: {shock_text}")

    lines: list[str] = []
    if chunks:
        lines.append("")
        lines.append(" · ".join(chunks))

    interpretations = record.get("interpretation") or []
    if interpretations:
        # Only surface the first note — enough when something looks paradoxical.
        note = str(interpretations[0]).replace("**", "")
        lines.append(f"\n→ *{note}*")

    return lines


_SEGMENT_LABELS = {
    "business": "Business",
    "leisure_price_sensitive": "Preissensitiv",
    "leisure_eco_conscious": "Öko-bewusst",
}

_AGENT_LABELS = {
    "provider": "Provider",
    "regulator": "Regulator",
    "consumer": "Consumer",
}


def _format_segment_booking_block(
    stats_for_round: dict,
    prior_stats: dict | None,
) -> list[str]:
    """Per-segment booking with booked/total, rate, and delta vs prior tick."""

    segments = stats_for_round.get("segments") or {}
    if not segments:
        return []

    prior_segments = (prior_stats or {}).get("segments") or {}
    lines = ["", "#### Segment-Buchung", ""]

    for seg_id, seg_data in segments.items():
        if not isinstance(seg_data, dict):
            continue
        booked = seg_data.get("booked_individuals")
        total = seg_data.get("total_individuals")
        rate = seg_data.get("booking_rate")
        label = _SEGMENT_LABELS.get(seg_id, seg_id)
        if booked is None or total is None or rate is None:
            continue

        line = f"- **{label}:** {booked}/{total} gebucht ({float(rate):.1%})"
        prior_seg = prior_segments.get(seg_id)
        if isinstance(prior_seg, dict) and prior_seg.get("booking_rate") is not None:
            delta = float(rate) - float(prior_seg["booking_rate"])
            if abs(delta) >= 0.001:
                line += f", Δ {delta:+.1%} pp"
        lines.append(line)

    return lines


def _format_agent_reasoning_block(agent_responses) -> list[str]:
    if not agent_responses:
        return []

    lines = ["", "#### Agenten-Begründungen & Handlungen", ""]
    for resp in agent_responses:
        label = _AGENT_LABELS.get(resp.agent_id, resp.agent_id)

        lines.append(f"**{label}**")

        if resp.reasoning:
            reasoning_formatted = "\n".join(
                [f"> {line}" for line in resp.reasoning.strip().splitlines()]
            )
            lines.append(reasoning_formatted)
        else:
            lines.append("> *(Keine Begründung angegeben)*")

        actions_line = []
        if hasattr(resp, "actions") and resp.actions:
            actions_list = [a for a in resp.actions if a.upper() != "NO_OP"]
            if actions_list:
                actions_line.append(f"**Aktionen:** {', '.join(actions_list)}")

        if hasattr(resp, "state_changes") and resp.state_changes:
            changes_list = []
            for sc in resp.state_changes:
                if isinstance(sc, dict):
                    f_id = sc.get("factor_id")
                    s_id = sc.get("proposed_state")
                    changes_list.append(f"`{f_id}→{s_id}`")
                elif hasattr(sc, "factor_id"):
                    changes_list.append(f"`{sc.factor_id}→{sc.proposed_state}`")
            if changes_list:
                actions_line.append(f"**Faktor-Vorschläge:** {', '.join(changes_list)}")

        if actions_line:
            lines.append("\n" + " | ".join(actions_line))

        lines.append("")
    return lines


def _format_agent_events_block(events) -> list[str]:
    if not events:
        return []

    lines = ["", "#### Öffentliche Events & Markteffekte", ""]
    for event in events:
        label = _AGENT_LABELS.get(event.source_agent, event.source_agent)
        lines.append(f"- **[{label}]** {event.description}")
    return lines


def save_tick_mechanics(
    state,
    filename: str = "tick_mechanics.json",
    *,
    run_dir: Path | None = None,
) -> str:
    """Structured per-tick mechanics for narratives and future state explorer (M9)."""

    ensure_output_dir()
    filepath = _resolve_output_path(filename, run_dir=run_dir)

    properties = state.resolved_properties()
    schedule = scheduled_property_events(properties)
    scheduled_by_tick: dict[int, list[dict[str, object]]] = {}
    for event in schedule:
        tick = int(event["tick"])
        scheduled_by_tick.setdefault(tick, []).append(event)

    round_numbers = sorted(
        {rr.round_number for rr in state.round_results if rr.round_number >= 1}
        | {event.round_number for event in state.event_log if event.round_number >= 1}
        | {s.get("round_number") for s in state.population_stats if s.get("round_number")}
    )

    payload = {
        "run_id": getattr(state.config, "run_id", None),
        "reading_guide": (
            "Booking decisions use the prior tick's market price as reference. "
            "Final ticket price is set after booking via market feedback. "
            "Agent narratives may contradict these numbers — trust this file."
        ),
        "ticks": [
            _build_tick_mechanics_record(
                state,
                round_number,
                scheduled_by_tick=scheduled_by_tick,
            )
            for round_number in round_numbers
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return filepath


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

    lines.append(f"# Simulationsbericht: {state.config.name}")
    lines.append(f"\n{state.config.description}\n")

    lines.append("## Überblick")
    lines.append(f"- **Simulierte Ticks:** {state.clock.current_tick} / {state.clock.max_ticks}")
    if start_tick is not None and end_tick is not None:
        lines.append(f"- **Tick-Bereich:** Tick {start_tick} – Tick {end_tick}")
    lines.append(f"- **Gesamte Events:** {len(state.event_log)}")
    lines.append(
        f"- **Preis Start:** {state.price_history[0].price:.2f} €"
        if state.price_history
        else "- **Preis Start:** n/a"
    )
    lines.append(
        f"- **Preis Ende:** {state.price_history[-1].price:.2f} €"
        if state.price_history
        else "- **Preis Ende:** n/a"
    )

    lines.append("\n## Leseschlüssel")
    lines.append(
        "Pro Tick bucht die Population **zuerst** (Referenzpreis = Endpreis des Vorticks), "
        "der Markt setzt **danach** den neuen Endpreis. Die Kennzahlen-Zeile ist Python-Ground-Truth."
    )
    lines.append(
        "Pro Tick drei Blöcke: **Segment-Buchung** (wer bucht) → **Agenten-Einschätzung** "
        "(LLM-Begründung) → **Agenten-Events** (eine Meldung/Aktion pro Rolle — nicht doppelt, "
        "sondern Reasoning vs. öffentliches Event). Maschinenlesbar: `tick_mechanics.json`."
    )

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
            effect_label = f"`{effect.get('property', '?')}` " f"{effect.get('delta', 0):+g}"
            lines.append(f"- Wenn {when_label}: {effect_label}")

    scheduled_by_tick: dict[int, list[dict[str, object]]] = {}
    for event in schedule:
        tick = int(event["tick"])
        scheduled_by_tick.setdefault(tick, []).append(event)

    lines.append("\n## Tick-Übersicht")
    round_numbers = sorted(
        {rr.round_number for rr in state.round_results if rr.round_number >= 1}
        | {event.round_number for event in state.event_log if event.round_number >= 1}
    )

    for round_number in round_numbers:
        tick_label = state.clock.tick_label(round_number)
        lines.append(f"\n### {tick_label}")

        mechanics = _build_tick_mechanics_record(
            state,
            round_number,
            scheduled_by_tick=scheduled_by_tick,
        )
        lines.extend(_format_tick_summary_markdown(mechanics))

        stats_for_round = next(
            (s for s in state.population_stats if s.get("round_number") == round_number),
            None,
        )
        if stats_for_round:
            prior_stats = _prior_population_stats(state, round_number)
            lines.extend(_format_segment_booking_block(stats_for_round, prior_stats))

        agent_responses = _agent_responses_for_round(state, round_number)
        lines.extend(_format_agent_reasoning_block(agent_responses))

        narrative_events = _narrative_events_for_round(state, round_number)
        lines.extend(_format_agent_events_block(narrative_events))

    lines.append("\n## Finaler Umweltzustand")
    for factor_id, factor in state.environment.factors.items():
        state_label = factor.possible_states.get(factor.current_state, factor.current_state)
        lines.append(f"- **{factor.name}:** {factor.current_state} – {state_label}")

    if hasattr(state, "population_stats") and state.population_stats:
        last_stats = state.population_stats[-1]
        lines.append("\n## Populations-Statistik (Aktueller Stand)")
        lines.append(
            f"- **Total Demand:** {last_stats['total_demand']:.1%} ({last_stats['total_booked']} von {last_stats['total_population']} gebucht)"
        )
        lines.append("- **Segment-Details:**")
        for seg_id, seg_data in last_stats["segments"].items():
            lines.append(
                f"  - **{seg_id}** (Anteil: {seg_data['share']:.1%}): {seg_data['booked_individuals']} gebucht / {seg_data['total_individuals']} gesamt (Rate: {seg_data['booking_rate']:.1%})"
            )

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

            entry["source_factor"] = (
                f"{source_id} - {source_factor.name}" if source_factor else source_id
            )
            entry["target_factor"] = (
                f"{target_id} - {target_factor.name}" if target_factor else target_id
            )

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
