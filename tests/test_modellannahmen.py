"""Modellannahmen je Lauf (P7.13-U13.5 Teil 1): die Rechnung, ohne Oberfläche.

Preisbildung, Sättigung und Bevölkerung lassen sich für einen einzelnen Lauf
ändern, ohne das Modell zu speichern — auf demselben Weg wie die Verläufe. Die
Zusagen, jede gegen einen möglichen stillen Fehler:

1. **Der Wert kommt dort an, wo die Engine liest** — bei der Preisbildung in der
   Marktregel, nicht nur in `market_feedback`.
2. **Das Artefakt nennt ihn** («abgeleitet», mit Namen).
3. **Der Schalter «Eigene Werte anwenden» schaltet ihn aus.**
4. **Was nicht existiert, scheitert laut.**
5. **Was dem Szenario gleicht, ist keine Annahme.**
6. **Gesichert und gestartet geht nichts verloren.**
"""

from __future__ import annotations

import pytest

from dashboard.config_catalog import (
    abweichungen_bereinigen,
    default_config_draft,
    prepare_simulation_state,
    szenario_zum_sichern,
)
from dashboard.run_launcher import draft_to_launch_config, launch_config_to_draft
from src.market.market_feedback import resolve_market_feedback_config
from src.models.sweep_models import SweepConfig


def _entwurf(**felder):
    draft = default_config_draft()
    draft.scenario_mode = "sweep"
    draft.sweep_id = "business_as_usual"
    for feld, wert in felder.items():
        setattr(draft, feld, wert)
    return draft


def _segment(state) -> str:
    return next(p.id for p in state.properties.individual_properties if p.type == "boolean")


MARKT = {"market_feedback": {"target_booking_rate": 0.45}}


class TestModellannahmenKommenImLaufAn:
    def test_pricing_arrives_where_the_engine_reads_it(self):
        """Die Engine liest die Marktregel — `market_feedback` allein wäre still wirkungslos."""

        ohne = resolve_market_feedback_config(prepare_simulation_state(_entwurf()).properties)
        assert (
            ohne.target_booking_rate != 0.45
        ), "Gegen Blindheit: der Vergleichswert ist schon 0,45"

        state = prepare_simulation_state(_entwurf(modellannahmen=MARKT))

        assert resolve_market_feedback_config(state.properties).target_booking_rate == 0.45
        assert state.properties.market_feedback.target_booking_rate == 0.45

    def test_saturation_arrives(self):
        state = prepare_simulation_state(
            _entwurf(modellannahmen={"saturation": {"booking_increase": 0.11}})
        )

        assert state.properties.saturation.booking_increase == 0.11

    def test_a_segment_arrives(self):
        segment = _segment(prepare_simulation_state(_entwurf()))

        state = prepare_simulation_state(
            _entwurf(modellannahmen={"population": {segment: {"prevalence": 0.9}}})
        )

        wert = next(p for p in state.properties.individual_properties if p.id == segment)
        assert wert.prevalence == 0.9

    def test_the_artifact_names_them(self):
        segment = _segment(prepare_simulation_state(_entwurf()))
        annahmen = {**MARKT, "population": {segment: {"prevalence": 0.9}}}

        state = prepare_simulation_state(_entwurf(modellannahmen=annahmen))

        assert state.rahmen.quelle == "abgeleitet"
        assert "market_feedback.target_booking_rate" in state.rahmen.abweichungen
        assert f"population.{segment}.prevalence" in state.rahmen.abweichungen

    def test_the_switch_turns_them_off(self):
        ohne = resolve_market_feedback_config(prepare_simulation_state(_entwurf()).properties)

        state = prepare_simulation_state(
            _entwurf(modellannahmen=MARKT, apply_custom_overrides=False)
        )

        assert resolve_market_feedback_config(state.properties).target_booking_rate == (
            ohne.target_booking_rate
        )


class TestWasNichtExistiertScheitertLaut:
    def test_an_unknown_section(self):
        with pytest.raises(ValueError, match="gibt_es_nicht"):
            SweepConfig(id="x", name="x", description="x", modellannahmen={"gibt_es_nicht": {}})

    def test_an_unknown_value(self):
        with pytest.raises(ValueError, match="gibt_es_nicht"):
            prepare_simulation_state(
                _entwurf(modellannahmen={"market_feedback": {"gibt_es_nicht": 1.0}})
            )

    def test_an_unknown_segment(self):
        with pytest.raises(ValueError, match="gibt_es_nicht"):
            prepare_simulation_state(
                _entwurf(modellannahmen={"population": {"gibt_es_nicht": {"prevalence": 0.5}}})
            )


class TestWasDemSzenarioGleichtIstKeineAnnahme:
    def test_an_equal_value_falls_away(self):
        ist = resolve_market_feedback_config(prepare_simulation_state(_entwurf()).properties)
        gleich = {"market_feedback": {"target_booking_rate": ist.target_booking_rate}}

        assert abweichungen_bereinigen(_entwurf(modellannahmen=gleich)).modellannahmen == {}

    def test_a_changed_value_stays(self):
        assert abweichungen_bereinigen(_entwurf(modellannahmen=MARKT)).modellannahmen == MARKT


class TestGesichertUndGestartetGehtNichtsVerloren:
    def test_the_saved_scenario_carries_them_and_computes_the_same(self):
        entwurf = _entwurf(modellannahmen=MARKT)

        sweep = szenario_zum_sichern(entwurf, "probe_modellannahmen")

        assert sweep.modellannahmen == MARKT
        gesichert = default_config_draft()
        gesichert.scenario_mode = "sweep"
        gesichert.sweep_id = "business_as_usual"
        from src.orchestration.scenario_sweeps import apply_sweep_overrides

        state = apply_sweep_overrides(prepare_simulation_state(gesichert), sweep)
        assert resolve_market_feedback_config(state.properties).target_booking_rate == 0.45

    def test_the_launch_round_trip_keeps_them(self):
        entwurf = _entwurf(modellannahmen=MARKT)

        zurueck = launch_config_to_draft(draft_to_launch_config(entwurf))

        assert zurueck.modellannahmen == MARKT
