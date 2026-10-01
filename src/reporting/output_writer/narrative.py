"""Human-readable Markdown run report (final_narrative.md)."""

from pathlib import Path

from src.market.property_engine import scheduled_property_events
from src.reporting.output_writer.events import agent_responses_for_round, narrative_events_for_round
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path
from src.reporting.output_writer.tick_mechanics import (
    build_tick_mechanics_record,
    format_property_event_line,
    format_shock_short,
    prior_population_stats,
)
from src.rule_engine import describe_when

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
            for part in [format_shock_short(shock)]
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
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)

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
        "der Markt setzt **danach** den neuen Endpreis. Die Kennzahlen-Zeile kommt aus der "
        "Rechnung, nicht vom Sprachmodell."
    )
    lines.append(
        "Pro Tick drei Blöcke: **Segment-Buchung** (wer bucht) → **Agenten-Einschätzung** "
        "(die Begründung des Sprachmodells) → **Öffentliche Meldungen** (eine je Rolle — "
        "nicht doppelt: dort die Begründung, hier die Meldung nach außen). "
        "Maschinenlesbar: `tick_mechanics.json`."
    )

    properties = state.resolved_properties()
    schedule = scheduled_property_events(properties)
    # **Nur, was in diesem Lauf geschieht, und ohne die Konfigurationsprosa**
    # (Befund 13 der Abnahme vom 2026-09-30): Hier standen in einem Lauf über 40
    # Ticks die Stützpunkte bis Tick 120, jeder mit der vollen Beschreibung aus
    # `properties.json` samt Paketkennungen («EIN TICK IST EIN MONAT (P3.8 …)»).
    im_lauf = [event for event in schedule if int(event["tick"]) <= state.clock.max_ticks]
    if im_lauf:
        lines.append("\n## Geplante Änderungen der Systemgrößen")
        lines.append("Vorgegeben vom Szenario, in diesem Lauf:")
        for event in im_lauf:
            lines.append(format_property_event_line({**event, "description": None}))

    shift_rules = properties.shift_rules
    if shift_rules:
        lines.append("\nDynamische Populations-Shift-Regeln:")
        for rule in shift_rules:
            effect = rule.effect
            # Beschreibung und Auswertung kommen seit P0.4 aus derselben Quelle.
            # Vorher stand hier eine eigene, ärmere Lesart: `metric` und
            # `at_least` fehlten, und eine Regel ohne Bedingung wurde als
            # "immer" beschrieben, obwohl der Code sie nie greifen ließ.
            when_label = describe_when(rule.when)
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

        mechanics = build_tick_mechanics_record(
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
            prior_stats = prior_population_stats(state, round_number)
            lines.extend(_format_segment_booking_block(stats_for_round, prior_stats))

        agent_responses = agent_responses_for_round(state, round_number)
        lines.extend(_format_agent_reasoning_block(agent_responses))

        narrative_events = narrative_events_for_round(state, round_number)
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
