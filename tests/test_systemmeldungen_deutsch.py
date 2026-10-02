"""Was der Rechenkern ins Ereignisprotokoll schreibt, ist deutsch (2026-10-02).

Die Meldungen von Markt und System stehen in der Konsole des Leitstands, unter
«Dateien» und im Kontext der Abfrage. Bis dahin lauteten sie «Market update (M4):
price=140.58 (+0.7%), cost=…», «[delta:booking:population] booking rate 47.9% →
41.2% (-6.7 pp, Python delta)» und «Factor F6 state F6.1 → F6.2 (factor_rules,
Python delta)». **Die Kennung `[delta:…]` bleibt**: Die Prüfungen der Dateien
und der Bericht erkennen die Meldungen daran.
"""

from __future__ import annotations

import re

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

ENGLISCH = re.compile(
    r"\b(?:price|booking|markup|cost|demand_level|Factor|state|Market update|Python delta|"
    r"feedback|tax|index|trajectory)\b"
)


@pytest.fixture(scope="module")
def meldungen() -> list:
    zustand = build_initial_state()
    zustand.clock.max_ticks = 20
    ergebnis = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(enable_market=True, enable_cib=True, checkpoint_interval=10_000),
    ).run(zustand)
    ende = getattr(ergebnis, "state", ergebnis)
    return [
        e
        for e in ende.event_log
        if e.source_agent in ("system", "market") or e.description.startswith("[delta:")
    ]


def _ohne_kennung(text: str) -> str:
    return re.sub(r"^\[delta:[^\]]*\]\s*", "", text)


def test_es_gibt_alle_arten(meldungen):
    kennungen = {m.description.split("]")[0] for m in meldungen if m.description.startswith("[")}

    assert "[delta:price" in kennungen
    assert "[delta:booking:population" in kennungen
    assert any(k.startswith("[delta:factor:") for k in kennungen), kennungen
    assert any(m.source_agent == "market" for m in meldungen)


def test_kein_englisches_wort(meldungen):
    funde = [m.description for m in meldungen if ENGLISCH.search(_ohne_kennung(m.description))]

    assert not funde, funde[:5]


def test_zahlen_mit_komma(meldungen):
    funde = [
        m.description
        for m in meldungen
        if re.search(r"(?<![F\d])\d+\.\d+", _ohne_kennung(m.description))
    ]

    assert not funde, funde[:5]
