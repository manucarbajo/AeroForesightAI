#!/usr/bin/env python
"""Manueller Test für output_writer.py - zum schnellen Testen der Speicherfunktionen"""

from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.models.enums import EventType
from src.output_writer import save_event_log, save_price_history
import json
from pathlib import Path

# Erstelle Test-Events
test_events = [
    EventLogEntry(
        id="evt_001",
        round_number=1,
        source_agent="agent_a",
        event_type=EventType.PRICE_CHANGE,
        description="Agent A erhöht Preis",
        affected_factors=["market_price", "demand"]
    ),
    EventLogEntry(
        id="evt_002",
        round_number=1,
        source_agent="agent_b",
        event_type=EventType.DEMAND_SHIFT,
        description="Nachfrage steigt",
        affected_factors=["demand", "consumer_behavior"]
    ),
]

# Erstelle Test-Preis-Historie
test_prices = [
    PriceHistoryEntry(
        round_number=1,
        agent_id="agent_a",
        price=150.0,
        demand_level=0.8,
        load_factor=0.95
    ),
    PriceHistoryEntry(
        round_number=1,
        agent_id="agent_b",
        price=145.0,
        demand_level=0.85,
        load_factor=0.92
    ),
]

print("Teste save_event_log()...")
event_path = save_event_log(test_events)
print(f"Events gespeichert unter: {event_path}")

# Überprüfe, dass Datei existiert
if Path(event_path).exists():
    with open(event_path, "r") as f:
        data = json.load(f)
    print(f"{len(data)} Events in JSON geschrieben")
    print(f"Beispiel: {data[0]}")
else:
    print(f"Fehler: Datei nicht gefunden!")

print("\nTeste save_price_history()...")
price_path = save_price_history(test_prices)
print(f"Preise gespeichert unter: {price_path}")

# Überprüfe, dass Datei existiert
if Path(price_path).exists():
    with open(price_path, "r") as f:
        data = json.load(f)
    print(f"{len(data)} Preis-Einträge in JSON geschrieben")
    print(f"Beispiel: {data[0]}")
else:
    print(f"Fehler: Datei nicht gefunden!")

print("\nTest abgeschlossen! Überprüfe den outputs/ Ordner.")

