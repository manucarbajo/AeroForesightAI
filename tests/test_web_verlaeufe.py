"""Der Schritt «Verläufe» (P7.13-U13.1 Teil 2a).

Was er zusagt, solange er nur zeigt:

1. **Er steht direkt nach der Wahl des Szenarios, optional**, und die Abkürzung
   zum Start erscheint trotzdem erst nach den drei Entscheidungen aus P1.1.
2. **Offen stehen die Größen, die ein Rahmen verändert**, die übrigen hinter
   einem Knopf — ein Auswahlfeld, kein zweites.
3. **Die Kurve ist der Wert des Laufs**, nicht eine eigene Rechnung.
4. **Er schreibt nichts** in den Entwurf.
"""

from __future__ import annotations

import pytest
from dash import dcc, html

from dashboard.config_catalog import exogene_groessen, verlaeufe_je_tick, von_rahmen_veraendert
from dashboard.web import theme
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor import verlaeufe, wizard
from dashboard.web.state import draft_from_dict, initial_draft_dict


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


def _radio(node) -> dcc.RadioItems:
    return next(k for k in _walk(node) if isinstance(k, dcc.RadioItems))


class TestDerSchrittStehtNachDemSzenario:
    def test_directly_after_the_scenario_and_optional(self):
        index = wizard.schritt("verlaeufe")

        assert index == wizard.schritt("szenario") + 1
        assert wizard.STEPS[index].required is False

    def test_the_shortcut_still_waits_for_the_three_decisions(self):
        """Die Abkürzung hängt an der letzten Pflichtentscheidung, nicht an Position 2."""

        assert wizard.LAST_REQUIRED == wizard.schritt("modus")
        assert sum(1 for s in wizard.STEPS[: wizard.LAST_REQUIRED + 1] if s.required) == 3


class TestOffenStehtWasEinRahmenVeraendert:
    def test_the_list_shows_the_open_ones(self, draft):
        optionen = [o["value"] for o in _radio(verlaeufe.layout(draft)).options]

        assert set(optionen) == von_rahmen_veraendert()
        assert optionen, "Gegen Blindheit: ohne offene Größe prüfte das nichts"

    def test_the_button_shows_all_fourteen(self):
        """Erst die offenen, dann die weiteren — zusammen jede exogene Größe genau einmal."""

        optionen = [o["value"] for o in _radio(verlaeufe.auswahl(weitere=True)).options]
        offen, weitere = verlaeufe.gruppen()

        assert optionen == offen + weitere
        assert sorted(optionen) == sorted(exogene_groessen())
        assert len(optionen) == len(set(optionen))

    def test_a_chosen_further_size_stays_visible(self):
        weitere = verlaeufe.gruppen()[1][0]

        optionen = [
            o["value"] for o in _radio(verlaeufe.auswahl(weitere=False, gewaehlt=weitere)).options
        ]

        assert weitere in optionen
        assert _radio(verlaeufe.auswahl(weitere=False, gewaehlt=weitere)).value == weitere

    def test_one_selection_field(self, draft):
        radios = [k for k in _walk(verlaeufe.layout(draft)) if isinstance(k, dcc.RadioItems)]

        assert len(radios) == 1

    def test_the_button_says_how_many(self):
        assert f"({len(verlaeufe.gruppen()[1])})" in verlaeufe.knopftext(False)


class TestDieKurveIstDerWertDesLaufs:
    def test_it_draws_the_run_value(self, draft):
        fig = verlaeufe.figur(draft, "carbon_tax_level")
        _, eigen = verlaeufe_je_tick(draft_from_dict(draft), "carbon_tax_level")

        assert list(fig.data[-1].y) == eigen

    def test_one_line_while_nothing_deviates(self, draft):
        """Zwei deckungsgleiche Linien sähen aus wie eine."""

        assert len(verlaeufe.figur(draft, "carbon_tax_level").data) == 1

    def test_the_dashed_scenario_line_appears_with_a_deviation(self, draft):
        draft["abweichungen"] = {
            "carbon_tax_level": {"property_id": "carbon_tax_level", "baseline": 77.0, "rules": []}
        }
        draft["apply_custom_overrides"] = True

        fig = verlaeufe.figur(draft, "carbon_tax_level")

        assert len(fig.data) == 2
        assert fig.data[0].line.dash == "dash"
        assert fig.data[-1].y[0] == 77.0

    def test_colours_come_from_the_palette(self, draft):
        for mode in theme.MODES:
            linie = verlaeufe.figur(draft, "carbon_tax_level", mode=mode).data[-1].line.color
            assert linie == theme.palette(mode)["accent"]


class TestDerSchrittSchreibtNichts:
    def test_no_configuration_field(self, draft):
        """Eine Auswahl, die nichts im Entwurf trägt, ist kein Feld (Regel 2)."""

        felder = [
            k
            for k in _walk(verlaeufe.layout(draft))
            if isinstance(getattr(k, "id", None), dict) and k.id.get("type") in {c.CFG, c.CFG_BOOL}
        ]

        assert felder == []

    def test_the_right_side_waits_for_the_callback(self, draft):
        """Nur der Callback kennt den Farbmodus — beim Zeichnen bleibt der Wirt leer."""

        wirt = next(
            k
            for k in _walk(verlaeufe.layout(draft))
            if isinstance(k, html.Div) and getattr(k, "id", None) == verlaeufe.kurve_id()
        )

        assert not wirt.children
