import pytest
from pathlib import Path
from src.config_loader import (
    load_simulation_config,
    load_simulation_clock,
    load_agents,
    load_factors,
    load_population_config,
    load_cib_frozen,
    load_properties_config,
    build_initial_state,
)
from src.models.state_models import SimulationState, SimulationConfig, FactorState
from src.models.agent_models import AgentConfig


def test_load_simulation_config():
    config = load_simulation_config()
    assert isinstance(config, SimulationConfig)
    assert config.name != ""


def test_load_simulation_clock():
    clock = load_simulation_clock()
    assert clock.max_ticks >= 1
    assert clock.tick_unit == "tick"
    assert clock.current_tick == 0


def test_load_agents():
    agents = load_agents()
    assert isinstance(agents, list)
    assert len(agents) > 0
    for agent in agents:
        assert isinstance(agent, AgentConfig)
        assert agent.id != ""
        assert agent.goals != []


def test_load_factors():
    factors = load_factors()
    assert isinstance(factors, dict)
    assert len(factors) > 0
    for factor_id, factor in factors.items():
        assert isinstance(factor, FactorState)
        assert factor.current_state in factor.possible_states


def test_load_population_config():
    agents = load_agents()
    pop_config = load_population_config(agents)
    # Consumer-Agent sollte eine PopulationConfig haben
    assert pop_config is not None
    assert pop_config.total_population >= 1
    assert len(pop_config.segments) > 0


def test_load_properties_config():
    properties = load_properties_config()
    assert len(properties.system_properties) >= 8
    assert "carbon_tax_level" in properties.system_property_ids()


def test_build_initial_state():
    state = build_initial_state()
    assert isinstance(state, SimulationState)
    assert state.clock.current_tick == 0
    assert len(state.agents) > 0
    assert len(state.environment.factors) > 0
    assert state.properties is not None
    assert len(state.resolved_properties().system_properties) >= 8
    assert state.event_log == []
    assert state.price_history == []
    assert state.round_results == []


def test_build_initial_state_agent_ids():
    state = build_initial_state()
    agent_ids = [a.id for a in state.agents]
    assert "consumer" in agent_ids
    assert "provider" in agent_ids
    assert "regulator" in agent_ids


def test_load_cib_frozen():
    matrix = load_cib_frozen()
    assert matrix.is_complete
    assert matrix.round_generated == 0
    assert matrix.metadata.get("frozen") is True


def test_build_initial_state_loads_frozen_cib():
    state = build_initial_state()
    assert state.cib_matrix is not None
    assert state.cib_matrix.is_complete
    assert len(state.cib_matrix.cells) == 168


def test_build_initial_state_without_cib():
    state = build_initial_state(load_cib=False)
    assert state.cib_matrix is None