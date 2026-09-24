"""`individuals_history.csv` trägt die Erschwinglichkeitsgrenze je Person (P5.2, 2026-09-11).

Die Dash-App zeigt im «Surplus Pulse», wie weit der Ticketpreis von dieser Grenze
entfernt ist. **Die Zahl kommt aus dem Modell**, nicht aus einer zweiten Formel im
Dashboard: Die abgelöste Streamlit-Ansicht hatte sie selbst gerechnet und den
Grün-Aufschlag vergessen. Geprüft wird deshalb nicht nur, dass die Spalte da ist,
sondern dass sie **die Schranke** ist, gegen die gebucht wird.
"""

from __future__ import annotations

import csv
import io

import pytest

from src.config_loader import build_initial_state, load_properties_config
from src.models.population_models import PopulationConfig
from src.orchestration import simulation_runner
from src.population.population_sampler import (
    booking_probability,
    erschwinglichkeitsgrenze,
    initialize_population,
)
from src.reporting.output_writer import append_individuals_history, save_population_individuals

SPALTE = "erschwinglichkeitsgrenze_eur"


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


@pytest.fixture(scope="module")
def leute(properties):
    return initialize_population(
        properties, PopulationConfig(segments=[], total_population=40), seed=7
    )


def _zeilen(pfad) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(pfad.read_text(encoding="utf-8"))))


def test_die_spalte_ist_fuer_jede_person_die_grenze_des_modells(tmp_path, leute, properties):
    koeffizienten = properties.booking_model
    append_individuals_history(1, leute, koeffizienten=koeffizienten, run_dir=tmp_path)

    zeilen = _zeilen(tmp_path / "individuals_history.csv")

    assert len(zeilen) == len(leute)
    for person, zeile in zip(leute, zeilen, strict=True):
        assert float(zeile[SPALTE]) == round(
            erschwinglichkeitsgrenze(person, koeffizienten=koeffizienten), 2
        )


def test_der_geschriebene_wert_ist_die_schranke(tmp_path, leute, properties):
    """Knapp über dem geschriebenen Wert bucht die Person nicht, knapp darunter vielleicht."""

    koeffizienten = properties.booking_model
    append_individuals_history(1, leute, koeffizienten=koeffizienten, run_dir=tmp_path)
    zeilen = {int(z["id"]): z for z in _zeilen(tmp_path / "individuals_history.csv")}
    person = max(leute, key=lambda p: p.environmental_awareness)
    assert person.environmental_awareness > 0.3, "Keine umweltbewusste Person gezogen"
    grenze = float(zeilen[person.id][SPALTE])

    def p(preis: float) -> float:
        return booking_probability(
            person,
            ticket_price=preis,
            carbon_tax=50.0,
            koeffizienten=koeffizienten,
            verfuegbarkeit=1.0,
        )

    assert p(grenze + 0.02) == 0.0
    assert p(grenze - 0.02) > 0.0


def test_ein_lauf_schreibt_die_spalte(tmp_path, monkeypatch):
    monkeypatch.setattr(simulation_runner, "resolve_run_output_dir", lambda run_id: tmp_path)
    zustand = build_initial_state()
    zustand.clock.max_ticks = 2

    simulation_runner.SimulationRunner(
        llm=None,  # type: ignore[arg-type]
        options=simulation_runner.RunnerOptions(
            deterministic_only=True, checkpoint_interval=0, verbose_ticks=False
        ),
    ).run(zustand, seed=42, run_id="historie")

    zeilen = _zeilen(tmp_path / "individuals_history.csv")
    assert zeilen, "Der Lauf hat keine Personen-Historie geschrieben"
    assert SPALTE in zeilen[0]
    assert all(float(z[SPALTE]) > 0 for z in zeilen)


@pytest.mark.parametrize("datei", ["individuals_history.csv", "population.csv"])
def test_keine_spalte_bleibt_fuer_jede_person_leer(tmp_path, leute, properties, datei):
    """Eine Spalte ohne einen einzigen Wert behauptet ein Merkmal, das es nicht gibt.

    Bis zum 2026-09-11 schrieben beide Schreiber `last_booked_tick` — ein Feld, das
    `Individual` nicht hat; die Spalte stand in jeder Zeile leer, und gelesen hat
    sie nur die abgelöste Streamlit-Ansicht. **Gesucht wird die leere Spalte, nicht
    dieser Name** — die nächste fällt ebenso auf.
    """

    if datei == "individuals_history.csv":
        append_individuals_history(
            1, leute, koeffizienten=properties.booking_model, run_dir=tmp_path
        )
    else:
        save_population_individuals(leute, run_dir=tmp_path)

    zeilen = _zeilen(tmp_path / datei)
    assert len(zeilen) == len(leute)
    leer = [s for s in zeilen[0] if all(z[s].strip() in ("", "None") for z in zeilen)]
    assert not leer, f"In {datei} trägt keine Person einen Wert in: {leer}"
