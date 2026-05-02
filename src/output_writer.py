import json
import os
from pathlib import Path
from typing import List

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