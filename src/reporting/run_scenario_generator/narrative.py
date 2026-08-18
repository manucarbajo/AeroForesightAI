"""Factual run narrative and per-scenario tick grounding text."""

from __future__ import annotations

from typing import Any

from src.reporting.run_scenario_generator.agent_digest import _sample_delta_events
from src.reporting.run_scenario_generator.context import (
    RunScenarioContext,
    _booking_trend,
    _price_trend,
)
from src.reporting.run_scenario_generator.factors import (
    FACTOR_IDS,
    _format_factor_compact,
    _format_factor_labels_short,
    _load_factor_catalog,
)


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


def _observed_run_brief(context: RunScenarioContext, factor_profile: dict[str, Any]) -> str:
    return build_run_narrative(context, factor_profile)
