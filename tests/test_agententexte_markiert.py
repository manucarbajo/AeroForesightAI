"""Was ein Agent schreibt und der Rechnung bis zu seinem Tick widerspricht, ist markiert (2026-10-02).

Der Prüfsatz vom 2026-09-29 zählte fünf Agententexte der Form «die gestiegene
Nachfrage», unmarkiert — gehalten gegen den **ganzen** Lauf, obwohl ein Agent über
seinen Tick spricht. Seither hält `pruefe_bis` den Text gegen den Stand bis zu
seinem Tick, und Bericht und Konsole des Leitstands markieren, was übrig bleibt.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.models.enums import EventType
from src.models.event_models import EventLogEntry
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner
from src.reporting.aussagen_pruefung import pruefe_bis
from src.reporting.output_writer import save_final_narrative

FALLEND = [{"tick": i, "booking_rate": r} for i, r in enumerate([0.40, 0.38, 0.35, 0.30, 0.31], 1)]


class TestDiePruefungKenntDenTick:
    def test_gegen_den_stand_bis_zum_tick(self):
        assert pruefe_bis("Die Nachfrage ist gestiegen.", FALLEND, 5)
        assert not pruefe_bis("Die Nachfrage ist gesunken.", FALLEND, 5)

    def test_was_bis_dahin_stieg_ist_kein_widerspruch(self):
        """Der Fehlalarm des alten Prüfsatzes: gegen den ganzen Lauf gehalten."""

        steigt_dann_faellt = [
            {"tick": i, "booking_rate": r} for i, r in enumerate([0.30, 0.34, 0.38, 0.20, 0.15], 1)
        ]

        assert not pruefe_bis("Die Nachfrage ist gestiegen.", steigt_dann_faellt, 3)
        assert pruefe_bis("Die Nachfrage ist gestiegen.", steigt_dann_faellt, 5)

    def test_etwa_gleich_ist_kein_widerspruch(self):
        flach = [{"tick": i, "booking_rate": 0.30 + i * 0.001} for i in range(1, 6)]

        assert not pruefe_bis("Die Nachfrage sinkt.", flach, 5)

    def test_datum_und_englisch_bleiben_befunde(self):
        arten = {b.art for b in pruefe_bis("Im Jahr 2030 the demand is for the airline.", [], 1)}

        assert arten == {"datum", "englisch"}


@pytest.fixture(scope="module")
def lauf():
    zustand = build_initial_state()
    zustand.clock.max_ticks = 12
    ergebnis = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(enable_market=True, checkpoint_interval=10_000),
    ).run(zustand)
    return getattr(ergebnis, "state", ergebnis)


def _meldung(tick: int, text: str, nummer: int) -> EventLogEntry:
    return EventLogEntry(
        id=f"probe-{nummer}",
        round_number=tick,
        source_agent="consumer",
        event_type=EventType.DEMAND_SHIFT,
        description=text,
        affected_factors=[],
        timestamp="",
    )


def test_der_bericht_markiert_den_widerspruch(lauf, tmp_path):
    raten = {s["round_number"]: s["total_demand"] for s in lauf.population_stats}
    assert raten[12] < raten[1] * 0.95, f"Vorbedingung: die Buchungsrate sinkt ({raten})"

    zustand = lauf.model_copy(deep=True)
    zustand.event_log += [
        _meldung(12, "Die Nachfrage ist deutlich gestiegen.", 1),
        _meldung(12, "Die Nachfrage ist gesunken.", 2),
    ]
    text = Path(save_final_narrative(zustand, run_dir=tmp_path)).read_text(encoding="utf-8")

    assert text.count("⚠ *Widerspricht der Rechnung:*") == 1
    assert "Nachfrage: im Text «steigt», gerechnet bis Tick 12 «sinkt»" in text


def test_die_konsole_macht_ihn_zur_warnung(lauf):
    from dashboard.web.run_data import RunData
    from dashboard.web.views import telemetry
    from src.reporting.output_writer.tick_mechanics import build_tick_mechanics_record

    ticks = [
        build_tick_mechanics_record(lauf, t, scheduled_by_tick={})
        for t in range(1, lauf.clock.max_ticks + 1)
    ]
    daten = RunData(
        run_id="probe",
        run_dir=None,
        ticks=ticks,
        events=[
            {"source_agent": "consumer", "round_number": 12, "description": "Die Nachfrage stieg."},
            {"source_agent": "consumer", "round_number": 12, "description": "Die Nachfrage sank."},
        ],
    )

    zeilen = [str(z) for z in telemetry.console_lines(daten)]
    markiert = [z for z in zeilen if "widerspricht der Rechnung" in z]

    assert len(markiert) == 1 and "stieg" in markiert[0]
