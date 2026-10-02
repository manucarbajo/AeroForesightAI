"""Der Bericht eines Laufs in Markdown (`final_narrative.md`, Reiter «Bericht»).

**Deutsch, mit Dezimalkomma und den Namen der Oberfläche** (P7.6, 2026-10-01).
Bis dahin stand hier, was der Rechenkern intern sagt: «price_sensitive»,
«Δ -11.4% pp», «Shocks: kapazitaet_index 1.06», «Total Demand», und unter
«Öffentliche Events» jede Delta-Meldung des Systems auf Englisch
(«[delta:booking:population] booking rate 23.3% → 12.0% (-11.4 pp, Python
delta)») — dieselben Zahlen, die die Kennzahlenzeile darüber schon nennt. Die
Namen kommen aus `src.reporting.namen`, derselben Quelle wie im Dashboard.
Gehalten von `tests/test_bericht.py`.
"""

from pathlib import Path

from src.market.property_engine import scheduled_property_events
from src.reporting.aussagen_pruefung import pruefe_bis
from src.reporting.namen import (
    FAKTOR_KURZNAMEN,
    MERKMAL_NAMEN,
    PROPERTY_LABELS,
    groesse_name,
    prozent,
    prozentpunkte,
    segment_name,
    zahl,
)
from src.reporting.output_writer.events import agent_responses_for_round, narrative_events_for_round
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path
from src.reporting.output_writer.tick_mechanics import (
    build_tick_mechanics_record,
    format_property_event_line,
    format_shock_short,
    prior_population_stats,
)
from src.rule_engine import describe_when

_AGENT_LABELS = {
    "provider": "Provider",
    "regulator": "Regulator",
    "consumer": "Consumer",
}

#: Was ein Akteur liefert, wenn das Modell keine Begründung schreibt. Der erste
#: Wert ist der Text, den `agent_node` bis zum 2026-10-01 einsetzte; Läufe von
#: davor tragen ihn in ihren Daten. «mock» ist die Antwort des Platzhalters
#: (`MockLLM`) in einem Lauf ohne Sprachmodell.
_OHNE_BEGRUENDUNG = ("Kein Reasoning geliefert.", "Keine Begründung geliefert.", "mock")


def _veraenderung_wichtig(delta: object) -> bool:
    return isinstance(delta, (int, float)) and abs(float(delta)) >= 0.001


def _format_tick_summary_markdown(record: dict[str, object]) -> list[str]:
    """Eine Kennzahlenzeile je Tick; eine Deutung nur, wenn etwas überrascht."""

    chunks: list[str] = []
    br = record.get("booking_rate")
    booked = record.get("booked")
    pop = record.get("population")
    br_delta = record.get("booking_rate_delta")
    ref = record.get("booking_reference_price_eur")
    post = record.get("market_price_after_feedback_eur")

    if br is not None and booked is not None and pop is not None:
        booking_part = f"**{prozent(float(br))}** gebucht ({booked} von {pop})"
        if _veraenderung_wichtig(br_delta):
            booking_part += f", {prozentpunkte(float(br_delta))}"
        chunks.append(booking_part)

    if isinstance(ref, (int, float)) and isinstance(post, (int, float)):
        delta = float(post) - float(ref)
        vorzeichen = "+" if delta >= 0 else "−"
        chunks.append(
            f"Preis {zahl(float(ref), 2)} → {zahl(float(post), 2)} € "
            f"({vorzeichen}{zahl(abs(delta), 2)} €)"
        )

    shocks = record.get("scheduled_shocks") or []
    if isinstance(shocks, list) and shocks:
        shock_text = ", ".join(
            part
            for shock in shocks
            if isinstance(shock, dict) and shock.get("property_id") != "carbon_tax_level"
            for part in [format_shock_short(shock)]
            if part
        )
        if shock_text:
            chunks.append(f"Vorgaben: {shock_text}")

    lines: list[str] = []
    if chunks:
        lines.append("")
        lines.append(" · ".join(chunks))

    interpretations = record.get("interpretation") or []
    if isinstance(interpretations, list) and interpretations:
        # Nur die erste Deutung — genug, wenn etwas widersprüchlich aussieht.
        note = str(interpretations[0]).replace("**", "")
        lines.append(f"\n→ *{note}*")

    return lines


def _format_faktorwechsel(state, round_number: int) -> list[str]:
    """Welche Faktoren in diesem Tick ihren Zustand gewechselt haben.

    Aus `factor_timeseries` gelesen — derselben Reihe, aus der die englischen
    Delta-Meldungen im Ereignisprotokoll entstehen, statt diese zu zerlegen.
    """

    zeilen = {row.get("tick"): row for row in state.factor_timeseries}
    vorher, jetzt = zeilen.get(round_number - 1), zeilen.get(round_number)
    if not vorher or not jetzt:
        return []
    wechsel = [
        f"{FAKTOR_KURZNAMEN.get(str(fid), str(fid))} {vorher[fid]} → {jetzt[fid]}"
        for fid in sorted(jetzt)
        if fid != "tick" and vorher.get(fid) is not None and vorher.get(fid) != jetzt[fid]
    ]
    return ["", f"**Faktorwechsel:** {', '.join(wechsel)}"] if wechsel else []


def _format_segment_booking_block(
    stats_for_round: dict,
    prior_stats: dict | None,
) -> list[str]:
    """Je Segment: wie viele gebucht haben, zu welchem Anteil, und die Veränderung."""

    segments = stats_for_round.get("segments") or {}
    if not segments:
        return []

    prior_segments = (prior_stats or {}).get("segments") or {}
    lines = ["", "#### Wer bucht", ""]

    for seg_id, seg_data in segments.items():
        if not isinstance(seg_data, dict):
            continue
        booked = seg_data.get("booked_individuals")
        total = seg_data.get("total_individuals")
        rate = seg_data.get("booking_rate")
        if booked is None or total is None or rate is None:
            continue

        line = (
            f"- **{segment_name(seg_id)}:** {booked} von {total} gebucht ({prozent(float(rate))})"
        )
        prior_seg = prior_segments.get(seg_id)
        if isinstance(prior_seg, dict) and prior_seg.get("booking_rate") is not None:
            delta = float(rate) - float(prior_seg["booking_rate"])
            if _veraenderung_wichtig(delta):
                line += f", {prozentpunkte(delta)}"
        lines.append(line)

    return lines


def _widerspruch(text: str, ticks: list[dict], tick: int) -> list[str]:
    """Was an einem Agententext der Rechnung bis zu seinem Tick widerspricht (2026-10-02).

    Markiert, nicht gestrichen — dieselbe Entscheidung wie beim Abschlusstext.
    """

    return [
        f"⚠ *Widerspricht der Rechnung:* {befund.erklaerung}"
        for befund in pruefe_bis(text, ticks, tick)
    ]


def _hat_inhalt(resp) -> bool:
    """Ob ein Akteur etwas gesagt hat — eine Begründung, eine Aktion, einen Vorschlag."""

    begruendung = (resp.reasoning or "").strip()
    aktionen = [a for a in (getattr(resp, "actions", None) or []) if a.upper() != "NO_OP"]
    return (
        bool(begruendung and begruendung not in _OHNE_BEGRUENDUNG)
        or bool(aktionen)
        or bool(getattr(resp, "state_changes", None))
    )


def _format_agent_reasoning_block(
    agent_responses, ticks: list[dict] | None = None, tick: int = 0
) -> list[str]:
    """Die Begründungen der Akteure — **weggelassen, wenn keiner etwas gesagt hat**.

    In einem Lauf ohne Sprachmodell stand hier je Tick dreimal «> mock».
    """

    if not any(_hat_inhalt(resp) for resp in agent_responses or []):
        return []

    lines = ["", "#### Begründungen der Akteure", ""]
    for resp in agent_responses:
        label = _AGENT_LABELS.get(resp.agent_id, resp.agent_id)

        lines.append(f"**{label}**")

        begruendung = (resp.reasoning or "").strip()
        if begruendung and begruendung not in _OHNE_BEGRUENDUNG:
            lines.append("\n".join(f"> {line}" for line in begruendung.splitlines()))
            for warnung in _widerspruch(begruendung, ticks or [], tick):
                lines.append(f">\n> {warnung}")
        else:
            lines.append("> *(keine Begründung)*")

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
                    changes_list.append(f"{f_id} → {s_id}")
                elif hasattr(sc, "factor_id"):
                    changes_list.append(f"{sc.factor_id} → {sc.proposed_state}")
            if changes_list:
                actions_line.append(f"**Vorgeschlagen:** {', '.join(changes_list)}")

        if actions_line:
            lines.append("\n" + " | ".join(actions_line))

        lines.append("")
    return lines


def _format_agent_events_block(events, ticks: list[dict] | None = None, tick: int = 0) -> list[str]:
    """Die Meldungen der Akteure nach außen.

    **Ohne die Delta-Meldungen des Systems** und ohne die Preismeldung des
    Markts: Sie wiederholen auf Englisch, was die Kennzahlenzeile und der
    Faktorwechsel darüber schon sagen. Im Ereignisprotokoll bleiben sie stehen.
    """

    meldungen = [
        event
        for event in events
        if event.source_agent in _AGENT_LABELS and not event.description.startswith("[delta:")
    ]
    if not meldungen:
        return []

    lines = ["", "#### Meldungen", ""]
    for event in meldungen:
        lines.append(f"- **{_AGENT_LABELS[event.source_agent]}:** {event.description}")
        for warnung in _widerspruch(event.description, ticks or [], tick):
            lines.append(f"  - {warnung}")
    return lines


def _regel_satz(rule) -> str:
    """Eine Regel, die die Bevölkerung verschiebt, als Satz mit Namen statt Kennungen."""

    effect = rule.effect
    # Beschreibung und Auswertung kommen seit P0.4 aus derselben Quelle.
    # Vorher stand hier eine eigene, ärmere Lesart: `metric` und `at_least`
    # fehlten, und eine Regel ohne Bedingung wurde als "immer" beschrieben,
    # obwohl der Code sie nie greifen ließ.
    when_label = describe_when(rule.when)
    for property_id in PROPERTY_LABELS:
        when_label = when_label.replace(f"`{property_id}`", groesse_name(property_id))
    merkmal = str(effect.get("property", "?"))
    delta = float(effect.get("delta", 0))
    vorzeichen = "+" if delta >= 0 else "−"
    return (
        f"- Wenn {when_label}: {MERKMAL_NAMEN.get(merkmal, merkmal)} "
        f"{vorzeichen}{zahl(abs(delta))}"
    )


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
    lines.append(f"- **Gerechnete Ticks:** {state.clock.current_tick} von {state.clock.max_ticks}")
    if start_tick is not None and end_tick is not None:
        lines.append(f"- **Ticks:** {start_tick} bis {end_tick}")
    lines.append(f"- **Ereignisse:** {len(state.event_log)}")
    lines.append(
        f"- **Preis am Anfang:** {zahl(state.price_history[0].price, 2)} €"
        if state.price_history
        else "- **Preis am Anfang:** nicht bekannt"
    )
    lines.append(
        f"- **Preis am Ende:** {zahl(state.price_history[-1].price, 2)} €"
        if state.price_history
        else "- **Preis am Ende:** nicht bekannt"
    )

    lines.append("\n## Leseschlüssel")
    lines.append(
        "Je Tick bucht die Bevölkerung **zuerst**, zum Preis des Vorticks; der Markt setzt "
        "**danach** den neuen Preis. Die Kennzahlenzeile kommt aus der Rechnung, nicht vom "
        "Sprachmodell."
    )
    lines.append(
        "Je Tick folgen: **Wer bucht** (nach Segment) → **Begründungen der Akteure** (was das "
        "Sprachmodell als Grund nennt) → **Meldungen** (was die Akteure nach außen sagen). "
        "In einem Lauf ohne Sprachmodell fehlen die beiden letzten. Was ein Akteur "
        "sagt und der Rechnung bis zu seinem Tick widerspricht, ist mit ⚠ markiert. "
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
        lines.append("\nRegeln, die die Bevölkerung verschieben:")
        for rule in shift_rules:
            lines.append(_regel_satz(rule))

    scheduled_by_tick: dict[int, list[dict[str, object]]] = {}
    for event in schedule:
        tick = int(event["tick"])
        scheduled_by_tick.setdefault(tick, []).append(event)

    lines.append("\n## Tick für Tick")
    round_numbers = sorted(
        {rr.round_number for rr in state.round_results if rr.round_number >= 1}
        | {event.round_number for event in state.event_log if event.round_number >= 1}
    )

    # Alle Ticks vorab: Ein Agententext wird gegen den Stand bis zu seinem Tick
    # gehalten, und den kennt erst, wer die Ticks davor schon hat.
    mechaniken = {
        rn: build_tick_mechanics_record(state, rn, scheduled_by_tick=scheduled_by_tick)
        for rn in round_numbers
    }
    alle_ticks = list(mechaniken.values())

    for round_number in round_numbers:
        tick_label = state.clock.tick_label(round_number)
        lines.append(f"\n### {tick_label}")

        mechanics = mechaniken[round_number]
        lines.extend(_format_tick_summary_markdown(mechanics))
        lines.extend(_format_faktorwechsel(state, round_number))

        stats_for_round = next(
            (s for s in state.population_stats if s.get("round_number") == round_number),
            None,
        )
        if stats_for_round:
            prior_stats = prior_population_stats(state, round_number)
            lines.extend(_format_segment_booking_block(stats_for_round, prior_stats))

        agent_responses = agent_responses_for_round(state, round_number)
        lines.extend(_format_agent_reasoning_block(agent_responses, alle_ticks, round_number))

        narrative_events = narrative_events_for_round(state, round_number)
        lines.extend(_format_agent_events_block(narrative_events, alle_ticks, round_number))

    lines.append("\n## Faktorlage am Ende")
    for factor_id, factor in state.environment.factors.items():
        state_label = factor.possible_states.get(factor.current_state, factor.current_state)
        name = FAKTOR_KURZNAMEN.get(factor_id, factor.name)
        lines.append(f"- **{name}:** {factor.current_state} – {state_label}")

    if hasattr(state, "population_stats") and state.population_stats:
        last_stats = state.population_stats[-1]
        lines.append("\n## Bevölkerung am Ende")
        lines.append(
            f"- **Buchungsrate:** {prozent(last_stats['total_demand'])} "
            f"({last_stats['total_booked']} von {last_stats['total_population']} gebucht)"
        )
        lines.append("- **Je Segment:**")
        for seg_id, seg_data in last_stats["segments"].items():
            lines.append(
                f"  - **{segment_name(seg_id)}** (Anteil {prozent(seg_data['share'])}): "
                f"{seg_data['booked_individuals']} von {seg_data['total_individuals']} gebucht "
                f"({prozent(seg_data['booking_rate'])})"
            )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return filepath
