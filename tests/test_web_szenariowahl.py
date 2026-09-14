"""Schritt 1: eine Liste, die Einzelheiten daneben, Stresstests auf Wunsch (P7.4-U4.1).

Von Haiko entschieden am 2026-09-14, nach einer Messung bei 1440 × 900: Das Raster
aus zehn Karten stand 539 px hoch, die Einzelheiten darunter 317 px, und der Schritt
brauchte 1,60 Bildschirme. Vier der zehn Karten waren Stresstests.

**Warum ein Knopf und keine zwei Gruppen:** Rahmen und Stresstests als zwei Gruppen,
die zweite zugeklappt, hieße, dasselbe Auswahlfeld zweimal zu zeichnen — das
verbietet Regel 1. Ein Knopf blendet die Stresstests ins **eine** Feld ein; er
trägt keine Konfigurationskennung und ist damit keine vierte Entscheidung
(`tests/test_web_start_flow.py::TestDreiEntscheidungen`).
"""

from __future__ import annotations

import json

from dash import html

from dashboard.config_catalog import list_sweep_presets
from dashboard.web import app as web_app
from dashboard.web.config_editor import controls, start_flow
from dashboard.web.state import initial_draft_dict


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


def _werte(optionen: list[dict]) -> set[str]:
    return {option["value"] for option in optionen}


def _stresstests() -> set[str]:
    return {preset.id for preset in list_sweep_presets() if preset.art != "rahmen"}


def _rahmen() -> set[str]:
    return {preset.id for preset in list_sweep_presets() if preset.art == "rahmen"}


class TestStresstestsTretenZurueck:
    def test_there_is_something_to_hide(self):
        """Gegen die eigene Blindheit: Ohne Stresstest in `configs/sweeps/` prüfte nichts."""

        assert _stresstests()

    def test_frames_are_always_offered(self):
        werte = _werte(start_flow.choice_options())

        assert _rahmen() <= werte
        assert {start_flow.STANDARD, start_flow.CUSTOM} <= werte

    def test_stress_tests_are_hidden_until_asked_for(self):
        assert not _stresstests() & _werte(start_flow.choice_options())
        assert _stresstests() <= _werte(start_flow.choice_options(stresstests=True))

    def test_a_chosen_stress_test_stays_visible(self):
        gewaehlt = sorted(_stresstests())[0]

        assert gewaehlt in _werte(start_flow.choice_options(gewaehlt=gewaehlt))

    def test_the_button_is_no_field(self):
        """Regel 1 und P1.1: Der Knopf schreibt nichts in den Entwurf."""

        knopf = next(
            k
            for k in _walk(start_flow.scenario_step(initial_draft_dict(), number=None))
            if getattr(k, "id", None) == start_flow.stress_toggle_id("scenario")
        )

        assert knopf.id["type"] not in {controls.CFG, controls.CFG_BOOL}
        assert str(len(_stresstests())) in str(knopf)

    def test_the_button_says_what_happens_next(self):
        assert "zeigen" in start_flow.stresstest_knopftext(False)
        assert "verbergen" in start_flow.stresstest_knopftext(True)

    def test_the_app_redraws_the_list_on_click(self):
        assert any(
            start_flow.LISTE in schluessel
            and start_flow.STRESS_TOGGLE in json.dumps(eintrag["inputs"])
            for schluessel, eintrag in web_app.app.callback_map.items()
        )


class TestEineListeUndDieEinzelheitenDaneben:
    def test_no_card_carries_a_clamped_sentence(self):
        """«Kachel ohne gekürzten Satz»: Die Beschreibung steht nur noch in den Einzelheiten."""

        schritt = start_flow.scenario_step(initial_draft_dict(), number=None)
        liste = next(
            k for k in _walk(schritt) if getattr(k, "id", None) == start_flow.liste_id("scenario")
        )

        assert "af-choice__text" not in str(schritt)
        for preset in list_sweep_presets():
            assert preset.description not in str(liste), preset.id

    def test_the_details_stand_beside_the_list(self):
        schritt = start_flow.scenario_step(initial_draft_dict(), number=None)
        wahl = next(
            k
            for k in _walk(schritt)
            if isinstance(k, html.Div)
            and "af-szenariowahl" in (getattr(k, "className", None) or "").split()
        )
        links, rechts = wahl.children

        assert start_flow.liste_id("scenario") in [getattr(k, "id", None) for k in _walk(links)]
        assert start_flow.slot_id("scenario") in [getattr(k, "id", None) for k in _walk(rechts)]

    def test_the_fine_print_stands_under_the_list(self):
        """Gemessen: Unter beiden Spalten kostete die Feinabstimmung die letzte Zeile über dem Ziel."""

        schritt = start_flow.scenario_step(initial_draft_dict(), number=None)
        wahl = next(
            k
            for k in _walk(schritt)
            if isinstance(k, html.Div)
            and "af-szenariowahl" in (getattr(k, "className", None) or "").split()
        )

        assert any(isinstance(k, html.Details) for k in _walk(wahl.children[0]))

    def test_the_full_description_is_still_there(self):
        preset = next(p for p in list_sweep_presets() if p.art == "rahmen")
        entwurf = start_flow.apply(initial_draft_dict(), preset.id)

        assert preset.description in str(start_flow.scenario_details(entwurf))
