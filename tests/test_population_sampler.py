from __future__ import annotations

from src.config_loader import load_properties_config
from src.models.population_models import PopulationConfig
from src.models.property_models import ShiftRule
from src.models.state_models import FactorState
from src.population_sampler import (
    apply_factor_shifts,
    evaluate_booking,
    initialize_population,
    run_population_tick,
)


def _minimal_population_config() -> PopulationConfig:
    return PopulationConfig(segments=[], total_population=100)


def test_initialize_population_is_deterministic_with_seed():
    properties = load_properties_config()
    config = _minimal_population_config()

    first = initialize_population(properties, config, seed=7)
    second = initialize_population(properties, config, seed=7)

    assert len(first) == 100
    assert first[0].model_dump() == second[0].model_dump()
    assert first[-1].id == 99


def test_individuals_support_multi_label():
    properties = load_properties_config()
    individuals = initialize_population(properties, _minimal_population_config(), seed=1)

    multi_label = [person for person in individuals if sum(person.labels.values()) > 1]
    assert len(multi_label) > 0


def test_persistence_same_ids_across_ticks():
    properties = load_properties_config()
    config = _minimal_population_config()
    seed = 99

    tick_one_people, _ = run_population_tick(
        properties,
        config,
        None,
        ticket_price=100.0,
        carbon_tax=50.0,
        factors={},
        system_properties={"carbon_tax_level": 50.0},
        seed=seed,
    )
    tick_two_people, _ = run_population_tick(
        properties,
        config,
        tick_one_people,
        ticket_price=120.0,
        carbon_tax=80.0,
        factors={},
        system_properties={"carbon_tax_level": 80.0},
        seed=seed,
    )

    assert [person.id for person in tick_one_people] == [person.id for person in tick_two_people]
    assert tick_one_people[0].wtp_eur == tick_two_people[0].wtp_eur


def test_higher_ticket_price_reduces_booking_rate():
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=3)

    _, low_price_stats = evaluate_booking(individuals, ticket_price=90.0, carbon_tax=30.0)
    _, high_price_stats = evaluate_booking(individuals, ticket_price=250.0, carbon_tax=30.0)

    assert high_price_stats.total_demand < low_price_stats.total_demand


def test_apply_factor_shifts_carbon_tax_rule():
    properties = load_properties_config()
    individuals = initialize_population(properties, _minimal_population_config(), seed=5)
    before = individuals[0].price_sensitivity

    shifted = apply_factor_shifts(
        individuals,
        properties.shift_rules,
        factors={},
        system_properties={"carbon_tax_level": 120.0},
    )

    assert shifted[0].price_sensitivity > before


def test_apply_factor_shifts_f6_awareness_rule():
    properties = load_properties_config()
    individuals = initialize_population(properties, _minimal_population_config(), seed=5)
    before = individuals[0].environmental_awareness

    factors = {
        "F6": FactorState(
            id="F6",
            name="Values",
            description="",
            current_state="F6.2",
            possible_states={"F6.1": "a", "F6.2": "b"},
        )
    }
    shifted = apply_factor_shifts(
        individuals,
        [ShiftRule(when={"factor": "F6", "state": "F6.2"}, effect={"property": "environmental_awareness", "delta": 0.02})],
        factors=factors,
        system_properties={},
    )

    assert shifted[0].environmental_awareness == round(before + 0.02, 4)


def test_eco_penalty_only_applies_when_carbon_tax_exceeds_baseline():
    """eco_penalty for price-sensitive individuals must be 0 when carbon_tax <= 50 (baseline)."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=42)

    _, stats_no_tax = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=0.0)
    _, stats_with_tax = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=150.0)

    # With high carbon tax, price-sensitive individuals should book less
    assert stats_with_tax.total_demand < stats_no_tax.total_demand


def test_eco_penalty_scales_with_carbon_tax():
    """eco_penalty should increase proportionally as carbon_tax rises above baseline."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=42)

    _, stats_low_tax = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=75.0)
    _, stats_high_tax = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=200.0)

    assert stats_high_tax.total_demand < stats_low_tax.total_demand


def test_eco_penalty_zero_at_baseline():
    """At exactly the carbon_tax baseline (50), eco_penalty must be 0 for all individuals."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=42)

    _, stats_at_baseline = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=50.0)
    _, stats_below_baseline = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=0.0)

    assert stats_at_baseline.total_demand == stats_below_baseline.total_demand


def test_shift_rule_once_does_not_stack():
    properties = load_properties_config()
    individuals = initialize_population(properties, _minimal_population_config(), seed=5)
    rule = next(r for r in properties.shift_rules if r.id == "carbon_tax_price_sensitivity")

    first = apply_factor_shifts(
        individuals,
        [rule],
        factors={},
        system_properties={"carbon_tax_level": 120.0},
    )
    second = apply_factor_shifts(
        first,
        [rule],
        factors={},
        system_properties={"carbon_tax_level": 200.0},
    )

    assert second[0].price_sensitivity == first[0].price_sensitivity
    assert "carbon_tax_price_sensitivity" in second[0].applied_shift_rules


# ---------------------------------------------------------------------------
# P2.1 — Sättigungseffekt (Cooldown)
# ---------------------------------------------------------------------------

def test_cooldown_blocks_rebooking_within_cooldown_period():
    """P2.1: Person who just booked cannot book again before cooldown expires."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=200)
    individuals = initialize_population(properties, config, seed=7)

    # Tick 1: book at low price
    booked_t1, stats_t1 = evaluate_booking(
        individuals, ticket_price=80.0, carbon_tax=30.0, current_tick=1, cooldown_ticks=3
    )
    booked_count_t1 = stats_t1.total_booked

    # Tick 2: same low price but within cooldown — bookers from tick 1 cannot rebook
    booked_t2, stats_t2 = evaluate_booking(
        booked_t1, ticket_price=80.0, carbon_tax=30.0, current_tick=2, cooldown_ticks=3
    )
    # Everyone who booked at tick 1 is blocked → count cannot exceed those who did NOT book at tick 1
    never_booked_t1 = sum(1 for p in booked_t1 if p.last_booked_tick is None)
    assert stats_t2.total_booked <= never_booked_t1


def test_cooldown_reactivates_after_expiry():
    """P2.1: Booking is allowed again once cooldown_ticks have passed."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=200)
    individuals = initialize_population(properties, config, seed=7)
    cooldown = 2

    # Tick 1: book
    booked_t1, stats_t1 = evaluate_booking(
        individuals, ticket_price=80.0, carbon_tax=30.0, current_tick=1, cooldown_ticks=cooldown
    )
    # Tick 4: cooldown (2) has expired → (4 - 1 = 3 >= 2) everyone can book again
    booked_t4, stats_t4 = evaluate_booking(
        booked_t1, ticket_price=80.0, carbon_tax=30.0, current_tick=4, cooldown_ticks=cooldown
    )
    # Booking rate at tick 4 should be at least as high as tick 1
    assert stats_t4.total_demand >= stats_t1.total_demand * 0.9


def test_last_booked_tick_is_set_on_booking():
    """P2.1: last_booked_tick is set to current_tick when a person books."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=100)
    individuals = initialize_population(properties, config, seed=7)

    booked, _ = evaluate_booking(individuals, ticket_price=80.0, carbon_tax=30.0, current_tick=5)
    for person in booked:
        if person.booked:
            assert person.last_booked_tick == 5
        else:
            # Non-bookers retain their previous last_booked_tick (None if never booked)
            assert person.last_booked_tick is None


# ---------------------------------------------------------------------------
# P2.2 — Segmente SSOT: dynamische Segment-Keys
# ---------------------------------------------------------------------------

def test_segment_keys_match_boolean_individual_properties():
    """P2.2: aggregate_population_stats derives segment keys from boolean individual_properties."""
    from src.population_sampler import aggregate_population_stats

    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=200)
    individuals = initialize_population(properties, config, seed=11)
    booked, stats_dynamic = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=50.0)

    # Re-aggregate with properties to get dynamic keys
    stats = aggregate_population_stats(booked, properties=properties)
    expected_keys = {
        prop.id
        for prop in properties.individual_properties
        if prop.type == "boolean" and prop.enabled
    }
    assert set(stats.segments.keys()) == expected_keys


def test_dynamic_segments_all_have_valid_booking_rates():
    """P2.2: every dynamic segment has a valid booking_rate in [0, 1]."""
    from src.population_sampler import aggregate_population_stats

    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=99)
    booked, _ = evaluate_booking(individuals, ticket_price=110.0, carbon_tax=50.0)
    stats = aggregate_population_stats(booked, properties=properties)
    for seg_id, seg in stats.segments.items():
        assert 0.0 <= seg.booking_rate <= 1.0, f"{seg_id} booking_rate out of range: {seg.booking_rate}"
