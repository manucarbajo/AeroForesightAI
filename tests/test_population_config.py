import pytest
from src.config_loader import load_agents, load_population_config
from src.models.population_models import PopulationConfig, ConsumerSegment
from src.validation import validate_population_config, validate_segments, validate_distribution


def test_population_config_exists():
    agents = load_agents()
    pop_config = load_population_config(agents)
    assert pop_config is not None
    assert isinstance(pop_config, PopulationConfig)


def test_segment_shares_sum_to_one():
    agents = load_agents()
    pop_config = load_population_config(agents)
    total_share = sum(seg.share for seg in pop_config.segments)
    assert abs(total_share - 1.0) < 1e-6


def test_segment_ids_unique():
    agents = load_agents()
    pop_config = load_population_config(agents)
    ids = [seg.id for seg in pop_config.segments]
    assert len(ids) == len(set(ids))


def test_segment_shares_valid():
    agents = load_agents()
    pop_config = load_population_config(agents)
    for seg in pop_config.segments:
        assert 0 < seg.share <= 1.0


def test_segment_distributions_valid():
    agents = load_agents()
    pop_config = load_population_config(agents)
    for seg in pop_config.segments:
        assert seg.price_elasticity.min_value < seg.price_elasticity.max_value
        assert seg.income_level.min_value < seg.income_level.max_value
        assert seg.environmental_awareness.min_value < seg.environmental_awareness.max_value


def test_validate_population_config_no_errors():
    agents = load_agents()
    pop_config = load_population_config(agents)
    errors = validate_population_config(pop_config)
    assert errors == []


def test_invalid_segment_shares():
    agents = load_agents()
    pop_config = load_population_config(agents)
    # Manipuliere einen Share so dass die Summe nicht 1.0 ergibt
    pop_config.segments[0].share = 0.99
    errors = validate_segments(pop_config.segments)
    assert any("summieren" in e for e in errors)