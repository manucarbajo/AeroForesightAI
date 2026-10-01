"""Der Bericht eines Laufs spricht Deutsch und wiederholt sich nicht (P7.6, 2026-10-01).

Bis dahin stand in `final_narrative.md` (Reiter «Bericht»), was der Rechenkern
intern sagt: Segmentkennungen («price_sensitive»), «Δ -11.4% pp», «Shocks:
kapazitaet_index 1.06», «Total Demand», je Tick die englischen Delta-Meldungen
des Systems — und in einem Lauf ohne Sprachmodell je Tick dreimal «> mock».
Gemessen an einem echten Lauf, nicht an einem nachgebauten Zustand.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner
from src.reporting.namen import SEGMENT_NAMEN
from src.reporting.output_writer import save_final_narrative

TICKS = 20


@pytest.fixture(scope="module")
def bericht(tmp_path_factory) -> str:
    zustand = build_initial_state()
    zustand.clock.max_ticks = TICKS
    ergebnis = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(enable_market=True, enable_cib=True, checkpoint_interval=10_000),
    ).run(zustand)
    ende = getattr(ergebnis, "state", ergebnis)
    ordner = tmp_path_factory.mktemp("bericht")
    return Path(save_final_narrative(ende, run_dir=ordner)).read_text(encoding="utf-8")


def _ohne_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def test_segmente_heissen_wie_in_der_oberflaeche(bericht):
    for kennung, name in SEGMENT_NAMEN.items():
        assert f"**{name}:**" in bericht, name
        assert f"**{kennung}" not in bericht, kennung


def test_zahlen_stehen_mit_komma(bericht):
    """Ein Dezimalpunkt zwischen Ziffern — außer in Faktorzuständen (F1.2) und Code."""

    funde = [
        treffer.group(0) for treffer in re.finditer(r"(?<![F\d])\d+\.\d+", _ohne_code(bericht))
    ]
    assert not funde, funde[:10]


def test_kein_entwicklerwort(bericht):
    for wort in (
        "pp",
        "Shocks",
        "Total Demand",
        "[delta:",
        "Python delta",
        "booking rate",
        "> mock",
        "Populations-Statistik",
        "Umweltzustand",
        "set →",
    ):
        assert not re.search(rf"(?<!\w){re.escape(wort)}(?!\w)", _ohne_code(bericht)), wort


def test_ein_faktorwechsel_steht_als_satz(bericht):
    """Aus `factor_timeseries`, nicht aus der englischen Delta-Meldung zerlegt."""

    assert re.search(r"\*\*Faktorwechsel:\*\* \w+ F\d\.\d → F\d\.\d", bericht)


def test_ohne_sprachmodell_keine_leeren_begruendungen(bericht):
    assert "#### Begründungen der Akteure" not in bericht
    assert "fehlen die beiden letzten" in bericht


def test_veraenderungen_in_prozentpunkten(bericht):
    assert re.search(r"[+−]\d+,\d Prozentpunkte", bericht)
