"""Der Draft muss verlustfrei durch den `dcc.Store` und zurück.

Streamlit hielt `ConfigDraft` als lebendes Objekt im Serverprozess; die
Dash-App legt ihn als JSON im Browser ab. Diese Umwandlung ist die Stelle, an
der stillschweigend Einstellungen verloren gehen könnten — deshalb hier
festgenagelt.
"""

from __future__ import annotations

from dataclasses import fields

import pytest

from dashboard.config_catalog import (
    ConfigDraft,
    PopulationEditState,
    PropertyEditState,
    default_config_draft,
    prepare_simulation_state,
)
from dashboard.web.config_editor import controls
from dashboard.web.state import (
    draft_from_dict,
    draft_to_dict,
    initial_draft_dict,
    patch,
)


def _rich_draft() -> ConfigDraft:
    """Ein Draft, in dem jedes verschachtelte Feld belegt ist."""

    draft = default_config_draft()
    draft.scenario_mode = "custom"
    draft.rounds = 13
    draft.seed = 4711
    draft.use_seed = True
    draft.simulation_name = "Testlauf"
    draft.simulation_description = "Beschreibung mit Umlauten: Grün, Größe, Fuß"
    draft.base_price = 123.5
    draft.run_count = 3
    draft.property_edits = {
        "carbon_tax_level": PropertyEditState(
            property_id="carbon_tax_level",
            baseline=42.0,
            rules=[
                {"active_from_tick": 3, "effect": {"type": "set", "value": 90.0}},
                {
                    "active_from_tick": 7,
                    "effect": {"type": "ramp", "value": 150.0, "duration_ticks": 4},
                },
            ],
            is_active=True,
        )
    }
    draft.population_edits = [
        PopulationEditState(
            id="frequent_flyer",
            type="boolean",
            prevalence=0.25,
            saturation_decay=0.4,
            modifiers={"wtp_multiplier": 1.3, "base_income_delta": 0.2},
        ),
        PopulationEditState(
            id="wtp_eur",
            type="distribution",
            distribution="beta",
            alpha=2.5,
            beta=6.0,
            min_value=20.0,
            max_value=400.0,
        ),
    ]
    draft.saturation_edit.booking_increase = 0.75
    draft.market_feedback_edit.damping = 0.42
    draft.market_feedback_edit.enabled = False
    return draft


def test_round_trip_preserves_every_field():
    original = _rich_draft()

    restored = draft_from_dict(draft_to_dict(original))

    for field in fields(ConfigDraft):
        assert getattr(restored, field.name) == getattr(original, field.name), field.name


def test_round_trip_rebuilds_nested_dataclasses():
    restored = draft_from_dict(draft_to_dict(_rich_draft()))

    assert isinstance(restored.property_edits["carbon_tax_level"], PropertyEditState)
    assert all(isinstance(item, PopulationEditState) for item in restored.population_edits)
    assert restored.saturation_edit.booking_increase == pytest.approx(0.75)
    assert restored.market_feedback_edit.enabled is False
    assert restored.property_edits["carbon_tax_level"].rules[1]["effect"]["duration_ticks"] == 4


def test_restored_draft_still_builds_a_simulation_state():
    """Die eigentliche Probe: Läuft der zurückgebaute Draft durch die Engine?"""

    restored = draft_from_dict(draft_to_dict(default_config_draft()))

    state = prepare_simulation_state(restored)

    assert state.clock.max_ticks == restored.rounds


def test_unknown_keys_from_an_older_version_are_ignored():
    """Ein Browser-Tab kann einen Draft aus einer früheren Version halten."""

    payload = initial_draft_dict()
    payload["feld_das_es_nicht_mehr_gibt"] = 1
    payload["property_edits"] = {"x": {"property_id": "x", "baseline": 1.0, "veraltet": True}}

    restored = draft_from_dict(payload)

    assert not hasattr(restored, "feld_das_es_nicht_mehr_gibt")
    assert restored.property_edits["x"].baseline == 1.0


def test_empty_payload_falls_back_to_the_default_draft():
    assert draft_from_dict(None) == default_config_draft()
    assert draft_from_dict({}) == default_config_draft()


def test_patch_updates_without_rebuilding():
    data = patch(initial_draft_dict(), rounds=99)

    assert data["rounds"] == 99
    assert draft_from_dict(data).rounds == 99


# --- Pfad-Zugriff der Eingabefelder ---------------------------------------


def test_get_path_reaches_into_dicts_and_lists():
    data = draft_to_dict(_rich_draft())

    assert controls.get_path(data, "market_feedback_edit.damping") == pytest.approx(0.42)
    assert controls.get_path(data, "population_edits.0.modifiers.wtp_multiplier") == 1.3
    assert controls.get_path(data, "gibt.es.nicht", "fallback") == "fallback"


def test_set_path_writes_into_dicts_and_lists():
    data = draft_to_dict(_rich_draft())

    controls.set_path(data, "market_feedback_edit.damping", 0.9)
    controls.set_path(data, "population_edits.0.prevalence", 0.8)

    restored = draft_from_dict(data)
    assert restored.market_feedback_edit.damping == pytest.approx(0.9)
    assert restored.population_edits[0].prevalence == pytest.approx(0.8)


def test_apply_inputs_converts_checkbox_lists_to_booleans():
    data = draft_to_dict(default_config_draft())

    updated = controls.apply_inputs(
        data,
        [
            ({"type": controls.CFG_BOOL, "field": "use_seed"}, ["on"]),
            ({"type": controls.CFG_BOOL, "field": "no_market"}, []),
            ({"type": controls.CFG, "field": "rounds"}, 21),
        ],
    )

    restored = draft_from_dict(updated)
    assert restored.use_seed is True
    assert restored.no_market is False
    assert restored.rounds == 21
