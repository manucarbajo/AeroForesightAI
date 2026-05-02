import json
import os
from pathlib import Path
from typing import List
from datetime import datetime

from src.models.event_models import EventLogEntry, PriceHistoryEntry

OUTPUT_DIR = "/Users/jonas/Documents/Studium/Studium/Master/2. Semester/Technology Lab/outputs"


def ensure_output_dir():
    """Stellt sicher, dass der Output-Ordner existiert."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_event_log(events: List[EventLogEntry], filename: str = "event_log.json") -> str:
    """
    Speichert die Event-Log-Einträge als JSON.
        Liste von EventLogEntry-Objekten
        Default Name der Ausgabedatei: event_log.json
    """
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Konvertiere alle Events zu Dictionaries für JSON
    events_data = [event.model_dump() for event in events]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def save_price_history(price_entries: List[PriceHistoryEntry], filename: str = "price_history.json") -> str:
    """
    Speichert die Preis-Historie als JSON.
        price_entries: Liste von PriceHistoryEntry-Objekten
        Default Name der Ausgabedatei: price_history.json
    
    Returns:
        Pfad zur gespeicherten Datei
    """
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Konvertiere alle Einträge zu Dictionaries für JSON
    price_data = [entry.model_dump() for entry in price_entries]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(price_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def save_round_history(round_results: List, filename: str = "round_history.json") -> str:
    """
    Speichert die Rundenhistorie als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: round_history.json
    """
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)

    round_data = [round_result.model_dump() for round_result in round_results]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(round_data, f, indent=2, ensure_ascii=False)

    return filepath

def save_run_metadata(state, args, filename: str = "run_metadata.json") -> str:
    """
    Speichert Metadaten des Simulationslaufs als JSON.
        state: finaler SimulationState
        args: geparste CLI-Argumente
        Default Name der Ausgabedatei: run_metadata.json
    """
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)

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

def save_segment_analysis(round_results: List, filename: str = "segment_analysis.json") -> str:
    """
    Speichert die segmentspezifischen Analysen aus den Rundenergebnissen als JSON.
        round_results: Liste von RoundResult-Objekten
        Default Name der Ausgabedatei: segment_analysis.json
    """
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)

    segment_data = []
    for round_result in round_results:
        # Suche segment_analysis in den agent_responses
        segment_analysis = {}
        for response in round_result.agent_responses:
            if hasattr(response, "segment_analysis") and response.segment_analysis:
                segment_analysis = response.segment_analysis

        round_entry = {
            "round": round_result.round_number,
            "segment_analysis": segment_analysis,
        }
        segment_data.append(round_entry)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(segment_data, f, indent=2, ensure_ascii=False)

    return filepath