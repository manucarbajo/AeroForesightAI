"""P0.3: Eine kaputte Konfiguration soll auffallen, bevor der Lauf anfängt.

Bis dahin gab `validate_config` bedingungslos `[]` zurück. Der teuerste Fall war
ein negativer Seed: Er kam durch alle Prüfungen und riss den Lauf erst im ersten
Tick mit `ValueError: expected non-negative integer` aus numpy ab — ohne jeden
Bezug zum Seed.
"""

from __future__ import annotations

import pytest

from src.config_loader import build_initial_state
from src.models.state_models import LLMConfig, SimulationConfig
from src.validation import (
    ValidationError,
    collect_state_errors,
    validate_agent,
    validate_config,
    validate_state,
)


def _config(**overrides) -> SimulationConfig:
    fields = dict(name="Testlauf", description="Beschreibung", llm=LLMConfig(), seed=None)
    fields.update(overrides)
    return SimulationConfig(**fields)


def _messages(errors: list[str]) -> str:
    return " | ".join(errors)


# --- Die ausgelieferte Konfiguration muss sauber sein ----------------------


def test_shipped_configuration_has_no_errors():
    """Wenn das hier rot wird, ist entweder `configs/` kaputt oder eine Regel zu streng."""

    assert collect_state_errors(build_initial_state()) == []


def test_a_healthy_config_passes():
    assert validate_config(_config()) == []


# --- Wertebereiche ----------------------------------------------------------


@pytest.mark.parametrize("seed", [0, 1, 42, None])
def test_valid_seeds_pass(seed):
    assert validate_config(_config(seed=seed)) == []


def test_negative_seed_is_rejected():
    """Der Fall, der heute erst tief in numpy auffällt."""

    errors = validate_config(_config(seed=-1))

    assert len(errors) == 1
    assert "seed" in _messages(errors)


def test_temperature_outside_the_allowed_range_is_rejected():
    assert "temperature" in _messages(validate_config(_config(llm=LLMConfig(temperature=3.0))))
    assert "temperature" in _messages(validate_config(_config(llm=LLMConfig(temperature=-0.1))))


@pytest.mark.parametrize("temperature", [0.0, 0.7, 2.0])
def test_temperature_at_the_edges_passes(temperature):
    assert validate_config(_config(llm=LLMConfig(temperature=temperature))) == []


def test_max_tokens_below_one_is_rejected():
    assert "max_tokens" in _messages(validate_config(_config(llm=LLMConfig(max_tokens=0))))


def test_empty_name_is_rejected():
    assert "name" in _messages(validate_config(_config(name="   ")))


def test_empty_model_is_rejected():
    assert "llm.model" in _messages(validate_config(_config(llm=LLMConfig(model=""))))


def test_empty_description_is_allowed():
    """Eine fehlende Beschreibung macht keinen Lauf falsch — sie blockiert also nicht."""

    assert validate_config(_config(description="")) == []


# --- Referenz-Integrität der Agentenprofile --------------------------------


def _regulator():
    state = build_initial_state()
    return state, next(agent for agent in state.agents if agent.id == "regulator")


def test_observes_pointing_at_an_unknown_factor_is_rejected():
    state, regulator = _regulator()
    regulator.profile.observes = ["market_metrics", "factors F2,F9"]

    errors = validate_agent(regulator, set(state.environment.factors))

    assert "F9" in _messages(errors)
    assert "regulator" in _messages(errors)


def test_may_propose_pointing_at_an_unknown_factor_is_rejected():
    state, regulator = _regulator()
    regulator.profile.may_propose = ["factor_state F42"]

    assert "F42" in _messages(validate_agent(regulator, set(state.environment.factors)))


def test_an_unknown_dependency_is_rejected():
    """Unbekannte `depends_on`-Werte gelten in jedem Tick als unerfüllt — lautlos."""

    state, regulator = _regulator()
    regulator.profile.depends_on = ["consumer.bookingrate"]

    errors = validate_agent(regulator, set(state.environment.factors))

    assert "depends_on" in _messages(errors)
    assert "consumer.bookingrate" in _messages(errors)


def test_the_shipped_profiles_reference_only_existing_factors():
    state = build_initial_state()
    factor_ids = set(state.environment.factors)

    for agent in state.agents:
        assert validate_agent(agent, factor_ids) == [], f"agent {agent.id}"


def test_an_agent_without_a_profile_is_fine():
    state = build_initial_state()
    agent = state.agents[0]
    agent.profile = None

    assert validate_agent(agent, set(state.environment.factors)) == []


# --- Der Vertrag: sammeln vs. werfen ---------------------------------------


def test_collect_reports_every_error_at_once():
    """Wer eine Config repariert, will alle Befunde sehen — nicht einen pro Anlauf."""

    state = build_initial_state()
    state.config.seed = -1
    state.config.name = ""
    state.config.llm.max_tokens = 0

    errors = collect_state_errors(state)

    assert len(errors) == 3


def test_collect_does_not_raise():
    state = build_initial_state()
    state.config.seed = -1

    assert collect_state_errors(state)  # keine Exception


def test_validate_state_still_raises():
    state = build_initial_state()
    state.config.seed = -1

    with pytest.raises(ValidationError) as excinfo:
        validate_state(state)

    assert "seed" in str(excinfo.value)


def test_validate_state_returns_empty_for_a_healthy_state():
    assert validate_state(build_initial_state()) == []


# --- Der Weg durch das Dashboard -------------------------------------------


def test_the_dashboard_reports_a_broken_draft():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    draft = ConfigDraft(rounds=2, use_seed=True, seed=-1)

    assert "seed" in _messages(validate_draft(draft))


def test_the_dashboard_reports_nothing_for_a_healthy_draft():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    assert validate_draft(ConfigDraft(rounds=2)) == []


def test_an_unreadable_config_file_becomes_a_finding_not_a_crash():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    draft = ConfigDraft(rounds=2, factors_file="gibt-es-nicht.json")

    errors = validate_draft(draft)

    assert errors
    assert "geladen werden" in _messages(errors)
