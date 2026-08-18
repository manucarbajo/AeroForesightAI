"""Tests for M6 income dynamics (income_index × base_income_factor)."""

from __future__ import annotations

from src.config_loader import build_initial_state, load_properties_config
from src.models.population_models import Individual, PopulationConfig
from src.models.state_models import FactorState
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner
from src.population.population_sampler import (
    initialize_population,
    run_population_tick,
    update_income_factors,
)


def _minimal_population_config() -> PopulationConfig:
    return PopulationConfig(segments=[], total_population=200)


def test_update_income_factors_scales_base_not_overwrites():
    people = [
        Individual(
            id=0,
            age=30,
            wtp_eur=120.0,
            environmental_awareness=0.5,
            price_sensitivity=0.4,
            base_income_factor=1.2,
            income_factor=1.2,
        ),
        Individual(
            id=1,
            age=40,
            wtp_eur=90.0,
            environmental_awareness=0.5,
            price_sensitivity=0.8,
            base_income_factor=0.8,
            income_factor=0.8,
        ),
    ]
    updated = update_income_factors(people, income_index=0.9)

    assert updated[0].income_factor == round(1.2 * 0.9, 4)
    assert updated[1].income_factor == round(0.8 * 0.9, 4)
    assert updated[0].base_income_factor == 1.2
    assert updated[1].base_income_factor == 0.8


def test_shift_rules_modify_base_before_index_scaling():
    properties = load_properties_config()
    config = _minimal_population_config()
    individuals = initialize_population(properties, config, seed=11)

    factors = {
        "F4": FactorState(
            id="F4",
            name="F4",
            description="",
            current_state="F4.2",
            possible_states={"F4.2": "Recession"},
        )
    }
    _, stats_default = run_population_tick(
        properties,
        config,
        individuals,
        ticket_price=150.0,
        carbon_tax=50.0,
        factors=factors,
        system_properties={"income_index": 1.0, "carbon_tax_level": 50.0},
        seed=11,
    )
    avg_with_shift = stats_default.avg_income_factor

    _, stats_no_shift = run_population_tick(
        properties,
        config,
        individuals,
        ticket_price=150.0,
        carbon_tax=50.0,
        factors={
            "F4": FactorState(
                id="F4",
                name="F4",
                description="",
                current_state="F4.1",
                possible_states={"F4.1": "Stable"},
            )
        },
        system_properties={"income_index": 1.0, "carbon_tax_level": 50.0},
        seed=11,
    )

    assert avg_with_shift < stats_no_shift.avg_income_factor


def test_falling_income_index_reduces_booking_more_for_price_sensitive():
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=5000)
    individuals = initialize_population(properties, config, seed=42)

    factors = {
        "F4": FactorState(
            id="F4",
            name="F4",
            description="",
            current_state="F4.2",
            possible_states={"F4.2": "Recession"},
        )
    }
    _, high_income_stats = run_population_tick(
        properties,
        config,
        individuals,
        ticket_price=140.0,
        carbon_tax=50.0,
        factors=factors,
        system_properties={"income_index": 1.0, "carbon_tax_level": 50.0},
        seed=42,
    )
    _, low_income_stats = run_population_tick(
        properties,
        config,
        individuals,
        ticket_price=140.0,
        carbon_tax=50.0,
        factors=factors,
        system_properties={"income_index": 0.85, "carbon_tax_level": 50.0},
        seed=42,
    )

    business_high = high_income_stats.segments["business"].booking_rate
    business_low = low_income_stats.segments["business"].booking_rate
    ps_high = high_income_stats.segments["price_sensitive"].booking_rate
    ps_low = low_income_stats.segments["price_sensitive"].booking_rate

    business_drop = business_high - business_low
    ps_drop = ps_high - ps_low
    ps_rel_drop = ps_drop / max(ps_high, 0.01)
    business_rel_drop = business_drop / max(business_high, 0.01)

    assert low_income_stats.total_demand < high_income_stats.total_demand
    assert ps_rel_drop > business_rel_drop


def test_income_index_exported_in_property_timeseries():
    state = build_initial_state(load_cib=False)
    state.clock.max_ticks = 12

    runner = SimulationRunner(
        llm=lambda prompt: "{}",
        options=RunnerOptions(
            enable_market=True,
            deterministic_only=True,
            checkpoint_interval=0,
        ),
    )
    final_state = runner.run(state, seed=42, run_id="income-export-test")

    tick_10_rows = [row for row in final_state.property_timeseries if row.get("tick") == 10]
    assert tick_10_rows, "expected property_timeseries row for tick 10"
    assert "income_index" in tick_10_rows[0]
    assert tick_10_rows[0]["income_index"] > 0
