"""Der Schritt «Modellannahmen» (P7.13-U13.5 Teil 2).

Was er zusagt:

1. **Er steht direkt nach «Verläufe», optional**, und die Abkürzung zum Start
   wartet weiter auf die drei Entscheidungen.
2. **Das Zeichnen schreibt nichts** — die Felder melden ihre Werte, die Bereinigung
   verwirft, was dem Szenario gleicht.
3. **Eine Änderung kommt im Lauf an**, dort, wo die Engine liest.
4. **Was der Schritt nicht zeigt, bleibt stehen.**
5. **Ohne «Eigene Werte anwenden» gesperrt, mit Grund.**
6. **«Prüfen & Starten» nennt sie**, und `_sync` liest die Felder.
"""

from __future__ import annotations

import pytest
from dash import dcc

from dashboard.config_catalog import prepare_simulation_state
from dashboard.web import app as web_app
from dashboard.web.config_editor import delta, modellannahmen, wizard
from dashboard.web.config_editor.verlaeufe import SPERRGRUND
from dashboard.web.state import draft_from_dict, initial_draft_dict
from src.market.market_feedback import resolve_market_feedback_config


@pytest.fixture
def draft() -> dict:
    data = initial_draft_dict()
    data["scenario_mode"] = "sweep"
    data["sweep_id"] = "business_as_usual"
    return data


def _walk(node):
    yield node
    kinder = getattr(node, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, (str, int, float)):
        yield from _walk(kinder)


def _felder(baum) -> list[dcc.Input]:
    return [
        k
        for k in _walk(baum)
        if isinstance(getattr(k, "id", None), dict) and k.id.get("type") == modellannahmen.ANNAHME
    ]


def _eintraege(baum, **aenderungen) -> list[dict]:
    eintraege = []
    for feld in _felder(baum):
        wert = aenderungen.get(feld.id["pfad"], feld.value)
        eintraege.append({"id": feld.id, "value": wert})
    return eintraege


class TestDerSchrittStehtNachVerlaeufe:
    def test_directly_after_verlaeufe_and_optional(self):
        index = wizard.schritt("modellannahmen")

        assert index == wizard.schritt("verlaeufe") + 1
        assert wizard.STEPS[index].required is False
        assert wizard.LAST_REQUIRED == wizard.schritt("modus")


class TestDasZeichnenSchreibtNichts:
    def test_drawing_and_reading_back_changes_nothing(self, draft):
        baum = modellannahmen.layout(draft)
        assert len(_felder(baum)) >= 8, "Gegen Blindheit: Preisbildung und Sättigung fehlen"

        danach = modellannahmen.eintraege_anwenden(draft, _eintraege(baum))

        assert danach["modellannahmen"] == {}
        assert danach["abweichungen"] == {}

    def test_prefilled_with_the_scenario(self, draft):
        vorlage = resolve_market_feedback_config(
            prepare_simulation_state(draft_from_dict(draft)).properties
        )
        feld = next(
            f
            for f in _felder(modellannahmen.layout(draft))
            if f.id["pfad"] == "market_feedback.target_booking_rate"
        )

        assert feld.value == vorlage.target_booking_rate


class TestEineAenderungKommtAn:
    def test_a_changed_target_reaches_the_run(self, draft):
        baum = modellannahmen.layout(draft)

        danach = modellannahmen.eintraege_anwenden(
            draft, _eintraege(baum, **{"market_feedback.target_booking_rate": 0.45})
        )
        state = prepare_simulation_state(draft_from_dict(danach))

        assert danach["modellannahmen"] == {"market_feedback": {"target_booking_rate": 0.45}}
        assert resolve_market_feedback_config(state.properties).target_booking_rate == 0.45
        assert "market_feedback.target_booking_rate" in state.rahmen.abweichungen

    def test_a_segment_share_reaches_the_run(self, draft):
        baum = modellannahmen.layout(draft)
        pfad = next(f.id["pfad"] for f in _felder(baum) if f.id["pfad"].endswith(".prevalence"))

        danach = modellannahmen.eintraege_anwenden(draft, _eintraege(baum, **{pfad: 0.9}))

        _, segment, _ = pfad.split(".")
        assert danach["modellannahmen"]["population"][segment]["prevalence"] == 0.9

    def test_the_shown_value_is_the_own_assumption(self, draft):
        draft["modellannahmen"] = {"market_feedback": {"target_booking_rate": 0.45}}

        feld = next(
            f
            for f in _felder(modellannahmen.layout(draft))
            if f.id["pfad"] == "market_feedback.target_booking_rate"
        )

        assert feld.value == 0.45


class TestWasDerSchrittNichtZeigtBleibt:
    def test_a_hidden_field_of_a_scenario_survives_drawing(self, draft):
        baum = modellannahmen.layout(draft)
        segment = next(
            f.id["pfad"].split(".")[1]
            for f in _felder(baum)
            if f.id["pfad"].endswith(".prevalence")
        )
        draft["modellannahmen"] = {"population": {segment: {"saturation_decay": 0.123}}}

        danach = modellannahmen.eintraege_anwenden(draft, _eintraege(modellannahmen.layout(draft)))

        assert danach["modellannahmen"]["population"][segment] == {"saturation_decay": 0.123}

    def test_an_empty_field_invents_nothing(self, draft):
        draft["modellannahmen"] = {"market_feedback": {"target_booking_rate": 0.45}}
        baum = modellannahmen.layout(draft)

        danach = modellannahmen.eintraege_anwenden(
            draft, _eintraege(baum, **{"market_feedback.target_booking_rate": None})
        )

        assert danach["modellannahmen"]["market_feedback"]["target_booking_rate"] == 0.45


class TestGesperrtMitGrund:
    def test_locked_without_the_switch(self, draft):
        draft["apply_custom_overrides"] = False
        baum = modellannahmen.layout(draft)

        assert _felder(baum) and all(f.disabled for f in _felder(baum))
        assert SPERRGRUND in str(baum)


class TestSieIstSichtbarUndVerdrahtet:
    def test_the_review_step_names_them(self, draft):
        """Beim Namen, nicht bei der Kennung.

        Die erste Fassung prüfte nur, dass eine Zeile für das Feld erscheint — und blieb
        in der Gegenprobe grün, als der Eintrag in `delta.VERSCHACHTELT` fehlte: Die
        Zeile erschien dann trotzdem, aber als `modellannahmen`.
        """

        draft["modellannahmen"] = {"market_feedback": {"target_booking_rate": 0.45}}

        zeile = next(a for a in delta.unterschiede(draft) if a.feld == "modellannahmen")
        assert zeile.was == "Modellannahmen"

    def test_the_sync_callback_reads_the_fields(self):
        sync = [
            schluessel
            for schluessel, eintrag in web_app.app.callback_map.items()
            if any(
                f'"type":"{modellannahmen.ANNAHME}"' in e.get("id", "")
                for e in eintrag.get("inputs", [])
            )
        ]

        assert len(sync) == 1
        assert "config-draft-store.data" in sync[0]
