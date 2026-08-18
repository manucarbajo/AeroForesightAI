#!/usr/bin/env python
"""
Test für output_writer.py über mehrere Runden
Simuliert 5 Runden mit kumulativen Events und Preis-Daten
"""

import json
from pathlib import Path

from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.output_writer import save_event_log, save_price_history

print("=" * 70)
print("TEST: SIMULIERE 5 RUNDEN MIT EVENT-LOGS UND PREIS-HISTORIEN")
print("=" * 70)

all_events = []
all_prices = []

# Simuliere 5 Runden
for round_num in range(1, 6):
    print(f"\nRUNDE {round_num}")
    print("-" * 70)

    round_events = [
        EventLogEntry(
            id=f"evt_{round_num:02d}_001",
            round_number=round_num,
            source_agent="consumer",
            event_type=EventType.DEMAND_SHIFT if round_num % 2 == 0 else EventType.PRICE_CHANGE,
            description=f"Event in Runde {round_num}: Consumer-Aktion",
            affected_factors=["demand", "market_price"],
        ),
        EventLogEntry(
            id=f"evt_{round_num:02d}_002",
            round_number=round_num,
            source_agent="provider",
            event_type=EventType.PRICE_CHANGE if round_num % 2 == 0 else EventType.DEMAND_SHIFT,
            description=f"Event in Runde {round_num}: Provider-Aktion",
            affected_factors=["supply", "pricing"],
        ),
    ]

    round_prices = [
        PriceHistoryEntry(
            round_number=round_num,
            agent_id="agent_a",
            price=100.0 + (round_num * 5),
            demand_level=0.9 - (round_num * 0.05),
            load_factor=0.85 + (round_num * 0.03),
        ),
        PriceHistoryEntry(
            round_number=round_num,
            agent_id="agent_b",
            price=95.0 + (round_num * 4),
            demand_level=0.88 - (round_num * 0.04),
            load_factor=0.80 + (round_num * 0.04),
        ),
    ]

    # Akkumuliere die Daten
    all_events.extend(round_events)
    all_prices.extend(round_prices)

    print(f"   [OK] {len(round_events)} Events erstellt")
    print(f"   [OK] {len(round_prices)} Preis-Einträge erstellt")
    print(f"   [OK] Kumulativ: {len(all_events)} Events, {len(all_prices)} Preis-Einträge")

# Speichere alle Daten
print("\n" + "=" * 70)
print("SPEICHERE ALLE DATEN")
print("=" * 70)

event_path = save_event_log(all_events)
price_path = save_price_history(all_prices)

print(f"\n[OK] Event-Log gespeichert: {event_path}")
print(f"[OK] Preis-Historie gespeichert: {price_path}")

# Überprüfe die Dateien
print("\n" + "=" * 70)
print("ÜBERPRÜFE GESPEICHERTE DATEIEN")
print("=" * 70)

if Path(event_path).exists():
    with open(event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)
    print("\n[OK] Event-Log:")
    print(f"   Anzahl Events: {len(event_data)}")
    print(
        f"   Runden abgedeckt: {min(e['round_number'] for e in event_data)}-{max(e['round_number'] for e in event_data)}"
    )
    print(f"   Dateigröße: {Path(event_path).stat().st_size} bytes")
    print("\n   Erste 2 Events:")
    for i, event in enumerate(event_data[:2], 1):
        print(f"   {i}. {event['id']} (Runde {event['round_number']}): {event['event_type']}")
    print("\n   Letzte 2 Events:")
    for i, event in enumerate(event_data[-2:], 1):
        print(f"   {i}. {event['id']} (Runde {event['round_number']}): {event['event_type']}")
else:
    print("[ERROR] Event-Log nicht gefunden!")

if Path(price_path).exists():
    with open(price_path, "r", encoding="utf-8") as f:
        price_data = json.load(f)
    print("\n[OK] Preis-Historie:")
    print(f"   Anzahl Einträge: {len(price_data)}")
    print(
        f"   Runden abgedeckt: {min(p['round_number'] for p in price_data)}-{max(p['round_number'] for p in price_data)}"
    )
    print(f"   Dateigröße: {Path(price_path).stat().st_size} bytes")
    print("\n   Agent_A Preis-Entwicklung:")
    agent_a_prices = [p for p in price_data if p["agent_id"] == "agent_a"]
    for p in agent_a_prices:
        print(
            f"      Runde {p['round_number']}: EUR {p['price']:.2f} (Demand: {p['demand_level']:.2f})"
        )
    print("\n   Agent_B Preis-Entwicklung:")
    agent_b_prices = [p for p in price_data if p["agent_id"] == "agent_b"]
    for p in agent_b_prices:
        print(
            f"      Runde {p['round_number']}: EUR {p['price']:.2f} (Demand: {p['demand_level']:.2f})"
        )
else:
    print("[ERROR] Preis-Historie nicht gefunden!")

print("\n" + "=" * 70)
print("TEST ABGESCHLOSSEN")
print("=" * 70)
print("\nDateien im outputs/ Ordner:")
import os

for file in sorted(os.listdir("outputs")):
    if not file.startswith("."):
        filepath = os.path.join("outputs", file)
        size = os.path.getsize(filepath)
        print(f"   - {file} ({size} bytes)")
