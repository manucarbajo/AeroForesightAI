import json
import os
from pathlib import Path
from typing import List
from datetime import datetime

from src.models.event_models import EventLogEntry, PriceHistoryEntry

# Projekt-Root relativ zu dieser Datei (…/src/output_writer.py → Repo-Root)
_REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = str(_REPO_ROOT / "outputs")


def ensure_output_dir():
    """Stellt sicher, dass der Output-Ordner existiert."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _resolve_output_path(filename: str, output_subdir: str | Path | None = None) -> str:
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
) -> str:
    """
    Speichert die Event-Log-Einträge als JSON.
        Liste von EventLogEntry-Objekten
        Default Name der Ausgabedatei: event_log.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    
    # Konvertiere alle Events zu Dictionaries für JSON
    events_data = [event.model_dump() for event in events]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def save_price_history(
    price_entries: List[PriceHistoryEntry],
    filename: str = "price_history.json",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """
    Speichert die Preis-Historie als JSON.
        price_entries: Liste von PriceHistoryEntry-Objekten
        Default Name der Ausgabedatei: price_history.json
    
    Returns:
        Pfad zur gespeicherten Datei
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    
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
) -> str:
    """
    Speichert die Rundenhistorie als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: round_history.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)

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
) -> str:
    """
    Speichert Metadaten des Simulationslaufs als JSON.
        state: finaler SimulationState
        args: geparste CLI-Argumente
        Default Name der Ausgabedatei: run_metadata.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "rounds_completed": state.clock.current_round,
        "rounds_max": state.clock.max_rounds,
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
) -> str:
    """
    Speichert die segmentspezifischen Analysen aller Agenten als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: segment_analysis.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)

    # Gruppiere nach Rundennummer
    rounds: dict = {}
    for round_result in round_results:
        round_number = round_result.round_number
        if round_number not in rounds:
            rounds[round_number] = {
                "round": round_number,
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

def save_final_narrative(
    state,
    filename: str = "final_narrative.md",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """
    Speichert eine lesbare Markdown-Zusammenfassung der Simulation.
        state: finaler SimulationState
        Default Name der Ausgabedatei: final_narrative.md
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)

    lines = []

    # Titel
    lines.append(f"# Simulationsbericht: {state.config.name}")
    lines.append(f"\n{state.config.description}\n")

    # Überblick
    lines.append("## Überblick")
    lines.append(f"- **Simulierte Runden:** {state.clock.current_round}")
    lines.append(f"- **Simulierte Jahre:** {state.clock.year_start} – {state.clock.year_start + state.clock.current_round * state.clock.years_per_round}")
    lines.append(f"- **Gesamte Events:** {len(state.event_log)}")
    lines.append(f"- **Preis Start:** {state.price_history[0].price:.2f} €" if state.price_history else "- **Preis Start:** n/a")
    lines.append(f"- **Preis Ende:** {state.price_history[-1].price:.2f} €" if state.price_history else "- **Preis Ende:** n/a")

    # Rundenübersicht
    lines.append("\n## Rundenübersicht")
    best_per_round: dict = {}
    for rr in state.round_results:
        best_per_round[rr.round_number] = rr

    for round_number in sorted(best_per_round.keys()):
        rr = best_per_round[round_number]
        sim_year = state.clock.year_start + (round_number * state.clock.years_per_round)
        lines.append(f"\n### Runde {round_number} – Jahr {sim_year}")

        # Reasoning pro Agent
        for resp in rr.agent_responses:
            first_line = resp.reasoning.strip().splitlines()[0] if resp.reasoning else "kein Reasoning"
            lines.append(f"- **{resp.agent_id}:** {first_line}")

        # Events der Runde
        if rr.events:
            lines.append(f"\n**Events ({len(rr.events)}):**")
            for e in rr.events:
                lines.append(f"- {e.source_agent}: {e.description}")

    # Finaler Umweltzustand
    lines.append("\n## Finaler Umweltzustand")
    for factor_id, factor in state.environment.factors.items():
        state_label = factor.possible_states.get(factor.current_state, factor.current_state)
        lines.append(f"- **{factor.name}:** {factor.current_state} – {state_label}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath

def save_cib_matrix(
    state,
    filename: str = "cib_matrix.json",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """
    Speichert die CIB-Matrix als JSON.
        state: finaler SimulationState
        Default Name der Ausgabedatei: cib_matrix.json
    """
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)

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
) -> str:
    """Save structured conversation protocol as JSON."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(protocol_payload, f, indent=2, ensure_ascii=False)
    return filepath


def save_protocol_markdown(
    markdown: str,
    filename: str = "protocol.md",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """Save conversation protocol as Markdown."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    return filepath


def save_scenarios(
    payload: dict,
    filename: str = "scenarios.json",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """Save derived scenarios as JSON."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return filepath


def save_scenarios_markdown(
    markdown: str,
    filename: str = "scenarios.md",
    *,
    output_subdir: str | Path | None = None,
) -> str:
    """Save derived scenarios as Markdown."""
    ensure_output_dir()
    filepath = _resolve_output_path(filename, output_subdir)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    return filepath