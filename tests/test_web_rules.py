"""Zeitliche Verläufe von Systemgrößen.

Die Regelzeilen im Editor werden zu Einträgen der Form «ab Runde X setze/rampe
auf Wert Y». Das ist die einzige Stelle des Editors, an der aus mehreren
Eingabefeldern eine verschachtelte Struktur entsteht — und die einzige mit
dynamischer Zeilenzahl. Beides zusammen macht sie zur wahrscheinlichsten
Fehlerquelle.
"""

from __future__ import annotations

import pytest

from dashboard.web.config_editor import _rule_entries, _rules_from_entries, macro
from dashboard.web.state import draft_from_dict, initial_draft_dict


def _feld(prop: str, index: int, key: str, value) -> dict:
    """Ein Eintrag, wie ihn Dash in `ctx.inputs_list` liefert."""

    return {"id": macro.rule_id(prop, index, key), "value": value}


# --- Einsammeln ------------------------------------------------------------


def test_fields_are_grouped_by_property_and_row():
    entries = _rule_entries(
        [
            _feld("carbon_tax_level", 0, "tick", 5),
            _feld("carbon_tax_level", 0, "value", 120.0),
            _feld("carbon_tax_level", 1, "tick", 10),
            _feld("oil_price_index", 0, "tick", 3),
        ]
    )

    assert set(entries) == {"carbon_tax_level", "oil_price_index"}
    assert set(entries["carbon_tax_level"]) == {0, 1}
    assert entries["carbon_tax_level"][0]["value"] == 120.0


def test_incomplete_entries_are_ignored():
    """Ohne Property, Zeile oder Feldname lässt sich nichts zuordnen."""

    entries = _rule_entries([{"id": {}, "value": 1}, {"id": {"prop": "x"}, "value": 2}])

    assert entries == {}


def test_no_fields_means_no_rules():
    assert _rule_entries([]) == {}
    assert _rules_from_entries({}) == []


# --- Zusammenbauen ---------------------------------------------------------


def test_a_set_rule_jumps_to_its_value():
    rules = _rules_from_entries({0: {"tick": 5, "kind": "set", "value": 120.0}})

    assert rules == [{"active_from_tick": 5, "effect": {"type": "set", "value": 120.0}}]


def test_a_ramp_rule_carries_its_duration():
    rules = _rules_from_entries({0: {"tick": 5, "kind": "ramp", "value": 200.0, "duration": 8}})

    assert rules[0]["effect"] == {"type": "ramp", "value": 200.0, "duration_ticks": 8}


def test_a_set_rule_has_no_duration():
    """Sonst schleppt die Konfiguration einen Wert mit, der nichts bedeutet."""

    rules = _rules_from_entries({0: {"tick": 1, "kind": "set", "value": 1.0, "duration": 9}})

    assert "duration_ticks" not in rules[0]["effect"]


def test_rules_keep_their_order():
    rules = _rules_from_entries(
        {
            2: {"tick": 30, "kind": "set", "value": 3.0},
            0: {"tick": 10, "kind": "set", "value": 1.0},
            1: {"tick": 20, "kind": "set", "value": 2.0},
        }
    )

    assert [rule["active_from_tick"] for rule in rules] == [10, 20, 30]


@pytest.mark.parametrize("fehlend", [{}, {"tick": None}, {"value": None, "kind": None}])
def test_missing_values_fall_back_instead_of_crashing(fehlend):
    """Ein leer gelassenes Feld darf den Lauf nicht verhindern."""

    rules = _rules_from_entries({0: fehlend})

    assert rules[0]["active_from_tick"] == 1
    assert rules[0]["effect"]["type"] == "set"


# --- Darstellung -----------------------------------------------------------


def test_the_number_of_rows_follows_the_count():
    rows = macro.rule_rows("carbon_tax_level", [], count=3, baseline=50.0)

    assert len(rows) == 3


def test_a_ramp_row_offers_the_duration_field():
    rules = [{"active_from_tick": 1, "effect": {"type": "ramp", "value": 2.0, "duration_ticks": 4}}]

    ramp = str(macro.rule_rows("x", rules, count=1, baseline=0.0))
    gesetzt = str(macro.rule_rows("x", [{"effect": {"type": "set"}}], count=1, baseline=0.0))

    assert "'key': 'duration'" in ramp
    assert "'key': 'duration'" not in gesetzt


def test_new_rows_start_at_the_baseline():
    """Eine frisch angelegte Regel soll nichts verändern, bis man sie anfasst."""

    assert "42.0" in str(macro.rule_rows("x", [], count=1, baseline=42.0))


# --- Durchstich ------------------------------------------------------------


def test_rules_survive_the_round_trip_into_the_draft():
    draft = initial_draft_dict()
    prop = next(iter(draft["property_edits"]))
    draft["property_edits"][prop]["rules"] = _rules_from_entries(
        {
            0: {"tick": 5, "kind": "set", "value": 120.0},
            1: {"tick": 12, "kind": "ramp", "value": 200.0, "duration": 6},
        }
    )

    restored = draft_from_dict(draft)

    rules = restored.property_edits[prop].rules
    assert len(rules) == 2
    assert rules[1]["effect"]["duration_ticks"] == 6
