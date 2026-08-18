from __future__ import annotations

from src.config_loader import load_properties_config
from src.models.population_models import PopulationConfig
from src.models.property_models import ShiftRule
from src.models.state_models import FactorState
from src.population.population_sampler import (
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


def test_individuals_can_have_multiple_labels():
    """Boolean traits are independent — one person may belong to several segments."""
    properties = load_properties_config()
    individuals = initialize_population(properties, _minimal_population_config(), seed=1)

    multi_label = [person for person in individuals if sum(person.labels.values()) > 1]
    assert len(multi_label) > 0


def test_exclusive_group_optional_for_persona_segments():
    """exclusive_group is opt-in when segments must be mutually exclusive personas."""
    from src.models.property_models import IndividualProperty, PropertiesConfig, SaturationConfig

    properties = PropertiesConfig(
        individual_properties=[
            IndividualProperty(
                id="type_a", type="boolean", prevalence=0.5, exclusive_group="persona"
            ),
            IndividualProperty(
                id="type_b", type="boolean", prevalence=0.5, exclusive_group="persona"
            ),
        ],
        saturation=SaturationConfig(),
    )
    individuals = initialize_population(properties, _minimal_population_config(), seed=3)
    for person in individuals:
        assert person.labels.get("type_a") != person.labels.get("type_b")


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
        [
            ShiftRule(
                when={"factor": "F6", "state": "F6.2"},
                effect={"property": "environmental_awareness", "delta": 0.02},
            )
        ],
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
# P2.1 — Sättigungseffekt (Saturation utility model)
# ---------------------------------------------------------------------------


def test_saturation_increases_on_booking():
    """P2.1: Booking a flight increases saturation_level."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=200)
    individuals = initialize_population(properties, config, seed=7)

    # Tick 1: book at low price
    booked_t1, stats_t1 = evaluate_booking(
        individuals, ticket_price=80.0, carbon_tax=30.0, properties=properties
    )
    for person in booked_t1:
        if person.booked:
            assert person.saturation_level >= 0.6
        else:
            assert person.saturation_level == 0.0


def test_saturation_decays_per_tick():
    """P2.1: Saturation level decays in run_population_tick."""
    from src.population.population_sampler import run_population_tick

    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=100)
    individuals = initialize_population(properties, config, seed=7)

    # Manually set high saturation
    individuals = [person.model_copy(update={"saturation_level": 0.8}) for person in individuals]

    individuals_t2, _ = run_population_tick(
        properties,
        config,
        individuals,
        ticket_price=1000.0,
        carbon_tax=50.0,
        factors={},
        system_properties={},
        current_tick=2,
    )

    for person in individuals_t2:
        assert person.saturation_level < 0.8


def test_saturation_config_drives_booking_increase():
    """P2.1: booking_increase comes from properties.saturation."""
    from src.models.property_models import SaturationConfig

    properties = load_properties_config()
    properties = properties.model_copy(
        update={"saturation": SaturationConfig(booking_increase=0.4, utility_penalty_factor=1.0)}
    )
    config = PopulationConfig(segments=[], total_population=200)
    individuals = initialize_population(properties, config, seed=7)

    booked, _ = evaluate_booking(
        individuals, ticket_price=80.0, carbon_tax=30.0, properties=properties
    )
    for person in booked:
        if person.booked:
            assert person.saturation_level >= 0.4
        else:
            assert person.saturation_level == 0.0


def test_high_saturation_reduces_booking_probability():
    """P2.1: High saturation level reduces the probability of booking."""
    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=7)

    # Base case (saturation = 0)
    _, stats_base = evaluate_booking(individuals, ticket_price=100.0, carbon_tax=50.0)

    # Saturated case (saturation = 1.0)
    saturated_individuals = []
    for person in individuals:
        saturated_individuals.append(person.model_copy(update={"saturation_level": 1.0}))

    _, stats_saturated = evaluate_booking(
        saturated_individuals, ticket_price=100.0, carbon_tax=50.0
    )

    assert stats_saturated.total_demand < stats_base.total_demand


# ---------------------------------------------------------------------------
# P2.2 — Segmente SSOT: dynamische Segment-Keys
# ---------------------------------------------------------------------------


def test_segment_keys_match_boolean_individual_properties():
    """P2.2: aggregate_population_stats derives segment keys from boolean individual_properties."""
    from src.population.population_sampler import aggregate_population_stats

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
    from src.population.population_sampler import aggregate_population_stats

    properties = load_properties_config()
    config = PopulationConfig(segments=[], total_population=500)
    individuals = initialize_population(properties, config, seed=99)
    booked, _ = evaluate_booking(individuals, ticket_price=110.0, carbon_tax=50.0)
    stats = aggregate_population_stats(booked, properties=properties)
    for seg_id, seg in stats.segments.items():
        assert (
            0.0 <= seg.booking_rate <= 1.0
        ), f"{seg_id} booking_rate out of range: {seg.booking_rate}"
