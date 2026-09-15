"""Startwerte und Verläufe aus dem Bereich «Modell» wirken nur gespeichert (P7.13-U13.3).

**Von Haiko entschieden am 2026-09-15**, statt sie dort zu entfernen: Im Modell
ändert man die ausgelieferten Verläufe, gespeichert hinter `controls.write_action`.
Bis dahin gab es keinen Schreibweg in `properties.json` — die Werte gingen in
`property_edits`, wirkten nur unter der Standard-Ausgangslage mit «Eigene Werte
anwenden» und unter einem Rahmenszenario still gar nicht. Für einen einzelnen Lauf
ist der Schritt «Verläufe» der Ort.

Dass ein **ungespeicherter** Wert keinen Lauf erreicht, misst der Wirkungstest
(`TestModellwerteWirkenNurGespeichert`). Hier stehen die Zusagen über das Speichern
selbst. Gespeichert wird in eine **Kopie** von `configs/`.
"""

from __future__ import annotations

import json
import shutil

import pytest

from dashboard import config_catalog
from dashboard.config_catalog import (
    default_config_draft,
    extract_property_edits_from_file,
    prepare_simulation_state,
    save_property_edits_to_file,
)
from src.market.property_engine import resolve_property


@pytest.fixture
def kopie(monkeypatch, tmp_path):
    ziel = tmp_path / "configs"
    shutil.copytree(config_catalog.CONFIGS_DIR, ziel, ignore=shutil.ignore_patterns("backtest"))
    monkeypatch.setattr(config_catalog, "CONFIGS_DIR", ziel)
    return ziel / "properties.json"


def _zustand():
    draft = default_config_draft()
    draft.scenario_mode = "basis"
    draft.apply_custom_overrides = False
    return prepare_simulation_state(draft)


def _kurve(state, groesse: str, ticks: int = 130) -> list[float]:
    return [resolve_property(groesse, t, state.properties) for t in range(ticks)]


def test_unchanged_values_write_nothing(kopie):
    """Wer ohne Änderung speichert, fasst die Datei nicht an — kein Byte."""

    vorher = kopie.read_bytes()

    assert save_property_edits_to_file(extract_property_edits_from_file()) == []
    assert kopie.read_bytes() == vorher


def test_a_saved_start_value_reaches_the_run(kopie):
    edits = extract_property_edits_from_file()
    regeln = list(edits["carbon_tax_level"].rules)
    edits["carbon_tax_level"].baseline = 99.0

    assert save_property_edits_to_file(edits) == ["carbon_tax_level"]

    co2 = next(p for p in _zustand().properties.system_properties if p.id == "carbon_tax_level")
    assert co2.trajectory.baseline == 99.0
    assert [r.model_dump(mode="json") for r in co2.trajectory.rules] == regeln


def test_the_rest_of_the_file_stays_as_it_was(kopie):
    """Nur der Verlauf der geänderten Größe — Marktregeln, Bevölkerung, alle anderen Größen bleiben."""

    vorher = json.loads(kopie.read_text(encoding="utf-8"))
    edits = extract_property_edits_from_file()
    edits["carbon_tax_level"].baseline = 99.0

    save_property_edits_to_file(edits)

    nachher = json.loads(kopie.read_text(encoding="utf-8"))
    for eintrag in vorher["system_properties"]:
        if eintrag.get("id") == "carbon_tax_level":
            eintrag["trajectory"] = {**eintrag["trajectory"], "baseline": 99.0}
    assert nachher == vorher


def test_a_step_function_keeps_its_curve_when_one_point_changes(kopie):
    """`bevoelkerungsentwicklung` steht als Stufenfunktion in der Datei.

    Der Editor liest sie als Startwert plus «set»-Regeln; gespeichert wird in dieser
    Form. Die Kurve muss dabei bis auf den geänderten Stützpunkt dieselbe bleiben —
    sonst schriebe das Speichern einen anderen Verlauf, als der Editor zeigt.
    """

    groesse = "bevoelkerungsentwicklung"
    vorher = _kurve(_zustand(), groesse)
    edits = extract_property_edits_from_file()
    letzte = edits[groesse].rules[-1]
    ab_tick = int(letzte["active_from_tick"])
    letzte["effect"]["value"] = float(letzte["effect"]["value"]) + 1.0

    assert save_property_edits_to_file(edits) == [groesse]

    nachher = _kurve(_zustand(), groesse)
    assert nachher[:ab_tick] == vorher[:ab_tick]
    assert nachher[ab_tick:] == pytest.approx([wert + 1.0 for wert in vorher[ab_tick:]])


def test_an_inactive_property_is_saved_as_zero_without_rules(kopie):
    """Von Haiko entschieden: genau das, womit ein Lauf sie bisher gerechnet hat."""

    edits = extract_property_edits_from_file()
    edits["carbon_tax_level"].is_active = False

    save_property_edits_to_file(edits)

    eintrag = next(
        p
        for p in json.loads(kopie.read_text(encoding="utf-8"))["system_properties"]
        if p.get("id") == "carbon_tax_level"
    )
    assert eintrag["trajectory"] == {"baseline": 0.0, "rules": []}


def test_the_action_saves_and_shows_what_the_file_now_holds(kopie):
    from dashboard.web.config_editor import _handle_action
    from dashboard.web.state import draft_to_dict

    data = draft_to_dict(default_config_draft())
    data["property_edits"]["carbon_tax_level"]["baseline"] = 77.0

    neu, meldung, ton = _handle_action({"type": "cfg-write", "action": "save-properties"}, data, [])

    assert ton == "erfolg", meldung
    assert extract_property_edits_from_file()["carbon_tax_level"].baseline == 77.0
    assert neu["property_edits"]["carbon_tax_level"]["baseline"] == 77.0


def test_the_model_area_offers_the_save(kopie):
    """Den Knopf gibt es — dass er hinter einer Rückfrage steht, prüft
    `TestNurDasModellSchreibtInsModell::test_every_writing_control_asks_first`."""

    from dashboard.web.pages import model_editor
    from dashboard.web.state import draft_to_dict

    rumpf = str(model_editor.rumpf_fuer("/app/modell", draft_to_dict(default_config_draft())))

    assert "'action': 'save-properties'" in rumpf
