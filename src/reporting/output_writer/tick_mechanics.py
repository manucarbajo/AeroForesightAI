"""Per-tick ground-truth mechanics record: booking/price deltas and causal notes."""

import json
from pathlib import Path

from src.market.property_engine import scheduled_property_events
from src.reporting.namen import einheit_kurz, groesse_name, prozent, zahl
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def _wert_mit_einheit(value: object, unit: str) -> str:
    """Ein Wert einer Systemgröße mit Einheit — ein Anteil als Prozent."""

    if not isinstance(value, (int, float)):
        return str(value)
    if unit == "fraction":
        return prozent(float(value), 0)
    einheit = einheit_kurz(unit)
    return f"{zahl(float(value))} {einheit}".strip()


def format_property_event_line(event: dict[str, object]) -> str:
    """Eine geplante Änderung als Satz: «Tick 24: CO₂-Steuer springt auf 200 €/t».

    Deutsch, mit Namen und Dezimalkomma (Befund 13 der Abnahme vom 2026-09-30):
    Hier stand «`carbon_tax_level` set → 200.0 eur_per_tonne».
    """

    tick = event["tick"]
    name = groesse_name(str(event["property_id"]))
    effect_type = event["effect_type"]
    wert = _wert_mit_einheit(event["value"], str(event.get("unit") or ""))

    if effect_type == "set":
        detail = f"springt auf {wert}"
    elif effect_type == "ramp":
        duration = event.get("duration_ticks", 1)
        detail = f"geht über {duration} Ticks auf {wert}"
    else:
        detail = f"auf {wert}"

    description = event.get("description")
    desc_suffix = f" ({description})" if description else ""
    return f"- **Tick {tick}:** {name} {detail}{desc_suffix}"


def prior_population_stats(state, round_number: int) -> dict | None:
    for entry in reversed(state.population_stats):
        tick = entry.get("round_number")
        if tick is not None and tick < round_number:
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
            "Die Buchung stieg, obwohl der **Endpreis** dieses Ticks stieg: Gebucht wurde "
            f"zum Preis des Vorticks, **{zahl(ref_price, 2)} €**. Der Anstieg auf "
            f"**{zahl(post_price, 2)} €** ist **Folge** der Buchung (Markt-Feedback), "
            "nicht deren Ursache."
        )

    if (
        isinstance(br_delta, (int, float))
        and br_delta < -0.02
        and isinstance(price_delta, (int, float))
        and price_delta < -1.0
    ):
        notes.append(
            "Die Buchung fiel, während der Endpreis sank: Das Markt-Feedback senkt den Preis "
            "bei schwacher Buchung — beides hängt am selben Regelkreis."
        )

    shocks = record.get("scheduled_shocks") or []
    shock_ids = {str(s.get("property_id")) for s in shocks if isinstance(s, dict)}

    if "carbon_tax_level" in shock_ids and isinstance(br_delta, (int, float)) and br_delta >= -0.01:
        notes.append(
            "Die CO₂-Steuer stieg, die Buchung blieb stabil oder stieg: Gebucht wird zum "
            "Preis des Vorticks — der höhere Kostendruck erreicht den Ticketpreis erst über "
            "das Markt-Feedback."
        )

    if "income_index" in shock_ids and isinstance(br_delta, (int, float)) and br_delta > 0.02:
        notes.append(
            "Der Einkommensindex stieg — höhere Zahlungsbereitschaft erklärt den "
            "Buchungsanstieg unabhängig vom späteren Preis-Feedback."
        )

    if isinstance(pop_delta, int) and pop_delta > 0:
        notes.append(
            f"Die Bevölkerung wuchs um **{pop_delta}** Personen. Sie werden neu gezogen "
            "und gehen direkt in die Buchungsrate ein."
        )

    cost_pressure = record.get("cost_pressure_eur")
    if (
        isinstance(post_price, (int, float))
        and isinstance(cost_pressure, (int, float))
        and post_price < cost_pressure - 5
    ):
        notes.append(
            f"Der Ticketpreis ({zahl(post_price, 2)} €) liegt unter dem Kostendruck "
            f"({zahl(cost_pressure, 2)} €) — der Anbieter verkauft unter Kosten; "
            "Markt-Feedback und Aufschlag entkoppeln Preis und Kosten."
        )

    return notes


def build_tick_mechanics_record(
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
    prior_stats = prior_population_stats(state, round_number)
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


def format_shock_short(shock: dict[str, object]) -> str:
    """Eine Vorgabe dieses Ticks, knapp: «Kapazitätsindex 1,06», «SAF-Mandat 5 %»."""

    prop_id = str(shock.get("property_id", ""))
    value = shock.get("value")
    name = groesse_name(prop_id)
    if isinstance(value, (int, float)):
        return f"{name} {_wert_mit_einheit(value, str(shock.get('unit') or ''))}"
    return name


def save_tick_mechanics(
    state,
    filename: str = "tick_mechanics.json",
    *,
    run_dir: Path | None = None,
) -> str:
    """Structured per-tick mechanics for narratives and future state explorer (M9)."""

    ensure_output_dir()
    filepath = resolve_output_path(filename, run_dir=run_dir)

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
            build_tick_mechanics_record(
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
