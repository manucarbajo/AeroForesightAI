"""Event-Log und Preis-Historie überstehen fünf Ticks und den Weg über die Platte.

**Bis zum 2026-09-14 war diese Datei kein Test**, sondern ein Skript auf
Modulebene: Es lief beim Einsammeln, schrieb nach `outputs/` und meldete einen
Fehler mit `print("[ERROR] …")` — ohne eine einzige Zusicherung, also ohne je
scheitern zu können. Gehalten wird jetzt, was es ausgab: Anzahl, abgedeckte
Ticks, Reihenfolge und die Preisentwicklung je Anbieter.
"""

from __future__ import annotations

import json

import pytest

from src.models.enums import EventType
from src.models.event_models import EventLogEntry, PriceHistoryEntry
from src.reporting.output_writer import save_event_log, save_price_history

TICKS = range(1, 6)


def _ereignisse() -> list[EventLogEntry]:
    ereignisse = []
    for tick in TICKS:
        gerade = tick % 2 == 0
        ereignisse += [
            EventLogEntry(
                id=f"evt_{tick:02d}_001",
                round_number=tick,
                source_agent="consumer",
                event_type=EventType.DEMAND_SHIFT if gerade else EventType.PRICE_CHANGE,
                description=f"Ereignis in Tick {tick}: Consumer",
                affected_factors=["demand", "market_price"],
            ),
            EventLogEntry(
                id=f"evt_{tick:02d}_002",
                round_number=tick,
                source_agent="provider",
                event_type=EventType.PRICE_CHANGE if gerade else EventType.DEMAND_SHIFT,
                description=f"Ereignis in Tick {tick}: Provider",
                affected_factors=["supply", "pricing"],
            ),
        ]
    return ereignisse


def _preise() -> list[PriceHistoryEntry]:
    preise = []
    for tick in TICKS:
        preise += [
            PriceHistoryEntry(
                round_number=tick,
                agent_id="agent_a",
                price=100.0 + tick * 5,
                demand_level=0.9 - tick * 0.05,
                load_factor=0.85 + tick * 0.03,
            ),
            PriceHistoryEntry(
                round_number=tick,
                agent_id="agent_b",
                price=95.0 + tick * 4,
                demand_level=0.88 - tick * 0.04,
                load_factor=0.80 + tick * 0.04,
            ),
        ]
    return preise


class TestDasEventLogUebersteht:
    def test_every_event_arrives_in_order(self, tmp_path):
        pfad = save_event_log(_ereignisse(), run_dir=tmp_path)

        daten = json.loads((tmp_path / "event_log.json").read_text(encoding="utf-8"))

        assert str(tmp_path) in pfad
        assert len(daten) == 10
        assert [e["id"] for e in daten[:2]] == ["evt_01_001", "evt_01_002"]
        assert [e["id"] for e in daten[-2:]] == ["evt_05_001", "evt_05_002"]
        assert {e["round_number"] for e in daten} == set(TICKS)

    def test_the_event_type_survives(self, tmp_path):
        save_event_log(_ereignisse(), run_dir=tmp_path)

        daten = json.loads((tmp_path / "event_log.json").read_text(encoding="utf-8"))

        assert daten[0]["event_type"] == EventType.PRICE_CHANGE.value
        assert daten[2]["event_type"] == EventType.DEMAND_SHIFT.value


class TestDiePreisHistorieUebersteht:
    def test_every_entry_arrives(self, tmp_path):
        save_price_history(_preise(), run_dir=tmp_path)

        daten = json.loads((tmp_path / "price_history.json").read_text(encoding="utf-8"))

        assert len(daten) == 10
        assert {p["round_number"] for p in daten} == set(TICKS)

    @pytest.mark.parametrize(
        ("anbieter", "erwartet"),
        [
            ("agent_a", [105.0, 110.0, 115.0, 120.0, 125.0]),
            ("agent_b", [99.0, 103.0, 107.0, 111.0, 115.0]),
        ],
    )
    def test_the_price_path_per_provider_survives(self, tmp_path, anbieter, erwartet):
        save_price_history(_preise(), run_dir=tmp_path)

        daten = json.loads((tmp_path / "price_history.json").read_text(encoding="utf-8"))

        assert [p["price"] for p in daten if p["agent_id"] == anbieter] == pytest.approx(erwartet)
