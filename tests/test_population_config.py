"""Die Bevölkerungskonfiguration, wie ein Lauf sie findet.

**Seit P5.1 (2026-09-11) über denselben Weg wie der Lauf.** Bis dahin gingen
diese Tests über `config_loader.load_population_config` — eine Funktion, die
kein Laufzeitpfad aufrief und den Konsumenten **anders** fand: über
`agent_type`, während `environment_node` den Agenten mit der ID `consumer`
nimmt. Die Tests prüften also eine Auswahl, die der Lauf nie trifft.
"""

import pytest

from src.config_loader import load_agents
from src.models.population_models import PopulationConfig
from src.validation import validate_population_config, validate_segments


@pytest.fixture
def pop_config() -> PopulationConfig:
    """Gefunden wie in `EnvironmentNode._run_population_tick`: der Agent mit der ID `consumer`."""

    consumer = next((agent for agent in load_agents() if agent.id == "consumer"), None)
    assert consumer is not None and consumer.population_config is not None
    return consumer.population_config


def test_population_config_exists(pop_config):
    assert pop_config is not None
    assert isinstance(pop_config, PopulationConfig)


def test_segment_shares_sum_to_one(pop_config):
    total_share = sum(seg.share for seg in pop_config.segments)
    assert abs(total_share - 1.0) < 1e-6


def test_segment_ids_unique(pop_config):
    ids = [seg.id for seg in pop_config.segments]
    assert len(ids) == len(set(ids))


def test_segment_shares_valid(pop_config):
    for seg in pop_config.segments:
        assert 0 < seg.share <= 1.0


def test_segment_distributions_valid(pop_config):
    for seg in pop_config.segments:
        assert seg.price_elasticity.min_value < seg.price_elasticity.max_value
        assert seg.income_level.min_value < seg.income_level.max_value
        assert seg.environmental_awareness.min_value < seg.environmental_awareness.max_value


def test_validate_population_config_no_errors(pop_config):
    errors = validate_population_config(pop_config)
    assert errors == []


def test_invalid_segment_shares(pop_config):
    # Manipuliere einen Share so dass die Summe nicht 1.0 ergibt
    pop_config.segments[0].share = 0.99
    errors = validate_segments(pop_config.segments)
    assert any("summieren" in e for e in errors)
