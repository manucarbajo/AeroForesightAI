"""Die Konsole eines Laufs ist deutsch, und das Dashboard liest sie trotzdem.

Befund 13 der Abnahme vom 2026-09-30: Die Konsole zeigte englische Zeilen des
Rechenkerns («[tick 14/40] 0.14s — price=…», «Sweep: …», «Completed 120 ticks»,
«Final factors», «Milestones») und Umlaute als «?», weil ein Rest aus der Zeit
vor P3.10 jede Beschreibung durch `encode("ascii", "replace")` schickte.

Die tragende Zusage ist das **Paar**: Jede Zeile, die der Rechenkern schreibt,
liest das Dashboard mit dem Muster, das neben ihrem Erzeuger steht — gemessen an
einem echten Lauf, nicht an abgeschriebenen Zeilen.
"""

from __future__ import annotations

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.orchestration import konsole
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner


def test_jede_zeile_liest_sich_mit_ihrem_muster():
    zeile = konsole.tick_zeile(
        14, 40, sekunden=0.137, je_sekunde=7.12, preis=140.58, buchungsrate=0.479
    )
    treffer = konsole.TICK_ZEILE.search(zeile)

    assert zeile == "[Tick  14/40] 0,14 s (7,1 Ticks/s) — Preis 140,58 €, Buchungsrate 47,9 %"
    assert treffer and treffer.group(1, 2) == ("14", "40")
    assert konsole.tick_sekunden(treffer) == 0.14

    kopf = konsole.SZENARIO_KOPF.match(konsole.szenario_kopf("Business as Usual (A1+B1)"))
    assert kopf and kopf.group(1) == "Business as Usual (A1+B1)"
    assert konsole.SZENARIO_ENDE.match("  " + konsole.szenario_ende(120, 3.2))


def test_eine_zeile_ohne_dauer_behaelt_ihren_tick():
    treffer = konsole.TICK_ZEILE.search("[Tick   7/25] unterwegs")

    assert treffer and treffer.group(1) == "7"
    assert konsole.tick_sekunden(treffer) is None


def test_ein_echter_lauf_schreibt_was_das_dashboard_liest():
    from dashboard.web import runner as web_runner

    zeilen: list[str] = []
    zustand = build_initial_state()
    zustand.clock.max_ticks = 2
    SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            verbose_ticks=True,
            checkpoint_interval=10_000,
            tick_progress_callback=zeilen.append,
        ),
    ).run(zustand)

    assert len(zeilen) == 2
    for zeile in zeilen:
        treffer = web_runner._TICK_LINE.search(zeile)
        assert treffer, zeile
        assert konsole.tick_sekunden(treffer) is not None, zeile
        assert "price" not in zeile and "booking" not in zeile, zeile
