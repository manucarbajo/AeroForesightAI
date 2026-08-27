"""P0.3: Eine kaputte Konfiguration soll auffallen, bevor der Lauf anfängt.

Bis dahin gab `validate_config` bedingungslos `[]` zurück. Der teuerste Fall war
ein negativer Seed: Er kam durch alle Prüfungen und riss den Lauf erst im ersten
Tick mit `ValueError: expected non-negative integer` aus numpy ab — ohne jeden
Bezug zum Seed.
"""

from __future__ import annotations

import shutil
from pathlib import Path

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
    errors = validate_config(_config(llm=LLMConfig(model="")))

    assert "Modellname" in _messages(errors)
    assert "config.llm" in _messages(errors)


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


def test_an_agent_without_a_profile_is_rejected():
    """Bis P0.5 hieß dieser Test "…is_fine" — und das stimmte damals auch.

    Ohne Profil ließ der Parser alles durch, die Durchsetzung nahm die Rechte
    aus dem hartcodierten `AGENT_FACTOR_PERMISSIONS`, und der Lauf verhielt
    sich richtig. P0.5 hat das Dict entfernt und `agent_profiles.json` zur
    einzigen Quelle gemacht: Seitdem heißt "kein Profil" **nichts erlaubt**.

    Damit ist ein fehlendes Profil kein harmloser Sonderfall mehr, sondern
    schaltet still ab, was Invariante 2 durchsetzen soll. Nachgestellt am
    2026-08-27: `configs/agent_profiles.json` weggeschoben, und der Lauf
    rechnet klaglos zu Ende — kein Agent kann noch einen Faktor vorschlagen,
    keine Meldung sagt es. `config_loader` vergibt nämlich schlicht kein
    Profil, wenn die Datei fehlt oder den Agenten nicht kennt.
    """

    state = build_initial_state()
    agent = state.agents[0]
    agent.profile = None

    errors = validate_agent(agent, set(state.environment.factors))
    assert "kein Profil" in _messages(errors)


def test_a_missing_profiles_file_does_not_pass_silently(tmp_path, monkeypatch):
    """Der Weg dorthin, nicht nur die Funktion: Fehlt die Datei, muss die
    Prüfung anschlagen — vorher lief der Lauf ohne jede Berechtigung durch."""

    import src.config_loader as config_loader

    monkeypatch.setattr(config_loader, "CONFIGS_DIR", tmp_path)
    for name in ("simulation_config.json", "agents.json", "properties.json", "factors.json"):
        shutil.copy(Path("configs") / name, tmp_path / name)
    # agent_profiles.json bewusst nicht mitkopiert.

    state = config_loader.build_initial_state(load_cib=False)
    fehler = collect_state_errors(state)

    ohne_profil = [message for message in fehler if "kein Profil" in message]
    assert len(ohne_profil) == len(state.agents)


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


def test_the_dashboard_checks_the_llm_values_it_actually_uses():
    """Die Lücke, die der erste Anlauf von P0.3 offen ließ.

    `prepare_simulation_state` überträgt vom Draft nur den Seed; Modellname,
    Temperatur und Antwortlänge gehen über `RunLaunchConfig` direkt an den
    Client. Geprüft wurde vorher `state.config.llm` — ein Feld, das kein
    Laufpfad liest. Ein Draft mit diesen Werten galt deshalb als fehlerfrei.
    """

    from dashboard.config_catalog import ConfigDraft, validate_draft

    errors = validate_draft(
        ConfigDraft(rounds=2, mock_llm=False, temperature=5.0, max_tokens=0, model="")
    )

    assert len(errors) == 3
    assert "temperature" in _messages(errors)
    assert "max_tokens" in _messages(errors)
    assert "Modellname" in _messages(errors)


def test_a_run_without_a_language_model_is_not_blocked_by_ollama_settings():
    """Die Prüfung darf keine Tür verriegeln, durch die niemand geht.

    Beide unteren Rechenmodi («Ohne Sprachmodell» und «Nur Zahlen») setzen
    `mock_llm`, und dann liefert `_build_llm()` ein `MockLLM` — Modellname,
    Temperatur und Antwortlänge werden nie angefasst. Ein leeres Modellfeld darf
    dort also keinen Lauf verhindern.
    """

    from dashboard.config_catalog import ConfigDraft, validate_draft

    ohne_sprachmodell = ConfigDraft(rounds=2, mock_llm=True, model="", max_tokens=0)
    nur_zahlen = ConfigDraft(
        rounds=2, mock_llm=True, deterministic_only=True, model="", temperature=9.0
    )

    assert validate_draft(ohne_sprachmodell) == []
    assert validate_draft(nur_zahlen) == []


def test_with_a_language_model_the_settings_are_checked():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    errors = validate_draft(ConfigDraft(rounds=2, mock_llm=False, temperature=5.0))

    assert "temperature" in _messages(errors)


# --- Eine Regelquelle für drei Herkunftsorte -------------------------------


def test_llm_rules_live_in_one_place():
    """Config, Draft und CLI müssen denselben Wert gleich beurteilen."""

    from dashboard.config_catalog import ConfigDraft, validate_draft
    from src.validation import validate_llm_settings

    direct = validate_llm_settings("llama3.2", 5.0, 2048, context="X")
    from_draft = validate_draft(ConfigDraft(rounds=2, mock_llm=False, temperature=5.0))
    from_config = validate_config(_config(llm=LLMConfig(temperature=5.0)))

    assert len(direct) == 1
    # Gleicher Befund, nur mit dem jeweiligen Herkunftsort davor.
    for errors in (direct, from_draft, from_config):
        assert "temperature (5.0) muss zwischen 0.0 und 2.0 liegen" in _messages(errors)


@pytest.mark.parametrize(
    "context,expected",
    [("config.llm", "config.llm:"), ("Technik", "Technik:"), ("CLI", "CLI:")],
)
def test_the_message_names_where_the_value_came_from(context, expected):
    from src.validation import validate_llm_settings

    errors = validate_llm_settings("m", 9.0, 1, context=context)

    assert _messages(errors).startswith(expected)


def test_an_unreadable_config_file_becomes_a_finding_not_a_crash():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    draft = ConfigDraft(rounds=2, factors_file="gibt-es-nicht.json")

    errors = validate_draft(draft)

    assert errors
    assert "geladen werden" in _messages(errors)
