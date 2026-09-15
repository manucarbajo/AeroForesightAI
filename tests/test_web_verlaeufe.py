"""Der Schritt «Verläufe» (P7.13-U13.1 Teil 2).

Was er zusagt:

1. **Er steht direkt nach der Wahl des Szenarios, optional**, und die Abkürzung
   zum Start erscheint trotzdem erst nach den drei Entscheidungen aus P1.1.
2. **Offen stehen die Größen, die ein Rahmen verändert**, die übrigen hinter
   einem Knopf — ein Auswahlfeld, kein zweites.
3. **Die Kurve ist der Wert des Laufs**, nicht eine eigene Rechnung.
4. **Die Auswahl der Größe schreibt nichts**; Startwert, Stützpunkte und
   Preisstrategie schreiben nur, was vom Szenario abweicht (Teil 2b).
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
        """Eine Auswahl für die Größe — die zweite im Schritt ist die Preisstrategie."""

        radios = [
            k
            for k in _walk(verlaeufe.layout(draft))
            if isinstance(k, dcc.RadioItems) and k.id == verlaeufe.auswahl_id()
        ]

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

    def test_a_flat_small_value_is_readable(self, draft):
        """0,0025 je Tick stand im Browser auf der Linie «0» einer Achse von −1 bis 1."""

        fig = verlaeufe.figur(draft, "demand_growth_rate")
        wert = fig.data[-1].y[0]
        unten, oben = fig.layout.yaxis.range

        assert wert != 0, "Gegen Blindheit: ohne Wert ungleich null prüfte das nichts"
        assert unten < wert < oben
        assert oben - unten <= abs(wert) * 2, "Die Achse ist breiter als der Wert selbst"

    def test_a_curve_that_moves_keeps_its_own_range(self, draft):
        draft["abweichungen"] = {
            "carbon_tax_level": {
                "property_id": "carbon_tax_level",
                "baseline": 50.0,
                "rules": [{"active_from_tick": 10, "effect": {"type": "set", "value": 120.0}}],
            }
        }
        draft["apply_custom_overrides"] = True

        assert verlaeufe.figur(draft, "carbon_tax_level").layout.yaxis.range is None

    def test_colours_come_from_the_palette(self, draft):
        for mode in theme.MODES:
            linie = verlaeufe.figur(draft, "carbon_tax_level", mode=mode).data[-1].line.color
            assert linie == theme.palette(mode)["accent"]


def _eingaben(baum) -> tuple[list, list]:
    """Was `_sync` aus dem gezeichneten Editor liest — Kennung und Wert je Feld."""

    starts, punkte = [], []
    for k in _walk(baum):
        kennung = getattr(k, "id", None)
        if not isinstance(kennung, dict):
            continue
        if kennung.get("type") == verlaeufe.START:
            starts.append({"id": kennung, "value": k.value})
        elif kennung.get("type") == verlaeufe.PUNKT:
            punkte.append({"id": kennung, "value": k.value})
    return starts, punkte


def _geaendert(starts, punkte, groesse, key, wert, index=None):
    ziel = starts if key == "start" else punkte
    for e in ziel:
        passt = e["id"]["groesse"] == groesse and (key == "start" or e["id"]["key"] == key)
        if passt and (index is None or e["id"].get("index") == index):
            e["value"] = wert
            return
    raise AssertionError(f"Kein Feld {key} für {groesse}")


class TestDerEditorSchreibtNurWasAbweicht:
    """Teil 2b: Startwert und Stützpunkte gehen in `abweichungen`, und nur, was abweicht."""

    @pytest.mark.parametrize("groesse", ["carbon_tax_level", "bevoelkerungsentwicklung"])
    def test_drawing_and_reading_back_changes_nothing(self, draft, groesse):
        """Die Felder melden beim Zeichnen ihre Werte — daraus darf keine Abweichung werden.

        Die Bevölkerung ist die Stufenfunktion; der Editor zeigt sie als Regeln.
        """

        starts, punkte = _eingaben(verlaeufe.editor(draft, groesse))
        assert starts, "Gegen Blindheit: der Editor hat kein Feld"

        danach = verlaeufe.eingaben_anwenden(draft, starts, punkte)

        assert danach["abweichungen"] == {}
        assert danach["preisstrategie"] is None

    def test_a_changed_start_value_arrives_in_draft_and_curve(self, draft):
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        _geaendert(starts, punkte, "carbon_tax_level", "start", 77)

        danach = verlaeufe.eingaben_anwenden(draft, starts, punkte)

        assert danach["abweichungen"]["carbon_tax_level"]["baseline"] == 77.0
        assert verlaeufe.figur(danach, "carbon_tax_level").data[-1].y[0] == 77.0

    def test_a_changed_rule_arrives(self, draft):
        verlauf = verlaeufe.verlauf_im_entwurf(draft, "carbon_tax_level")
        assert verlauf["rules"], "Gegen Blindheit: das Szenario braucht einen Stützpunkt"
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        _geaendert(starts, punkte, "carbon_tax_level", "wert", 999, index=0)

        danach = verlaeufe.eingaben_anwenden(draft, starts, punkte)

        regel = danach["abweichungen"]["carbon_tax_level"]["rules"][0]
        assert regel["effect"]["value"] == 999.0

    def test_an_incomplete_row_invents_nothing(self, draft):
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        vorher = len(verlaeufe.verlauf_im_entwurf(draft, "carbon_tax_level")["rules"])
        _geaendert(starts, punkte, "carbon_tax_level", "tick", None, index=0)

        danach = verlaeufe.eingaben_anwenden(draft, starts, punkte)

        regeln = danach["abweichungen"]["carbon_tax_level"]["rules"]
        assert len(regeln) == vorher - 1

    def test_the_editor_shows_the_deviation(self, draft):
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        _geaendert(starts, punkte, "carbon_tax_level", "start", 77)
        danach = verlaeufe.eingaben_anwenden(draft, starts, punkte)

        wieder, _ = _eingaben(verlaeufe.editor(danach, "carbon_tax_level"))

        assert wieder[0]["value"] == 77.0

    def test_locked_with_reason_without_the_switch(self, draft):
        draft["apply_custom_overrides"] = False
        baum = verlaeufe.editor(draft, "carbon_tax_level")

        felder = [
            k
            for k in _walk(baum)
            if isinstance(getattr(k, "id", None), dict)
            and k.id.get("type") in {verlaeufe.START, verlaeufe.PUNKT}
        ]

        assert felder and all(k.disabled for k in felder)
        assert verlaeufe.SPERRGRUND in str(baum)


def _knoepfe(baum, typ) -> list:
    return [
        k
        for k in _walk(baum)
        if isinstance(getattr(k, "id", None), dict) and k.id.get("type") == typ
    ]


class TestStuetzpunkteKommenUndGehen:
    """Teil 2b-2: eine leere Zeile dazu, eine Zeile weg — und der Entwurf folgt."""

    def test_the_editor_offers_both_actions(self, draft):
        baum = verlaeufe.editor(draft, "carbon_tax_level")
        regeln = verlaeufe.verlauf_im_entwurf(draft, "carbon_tax_level")["rules"]

        assert len(_knoepfe(baum, verlaeufe.NEU)) == 1
        assert len(_knoepfe(baum, verlaeufe.WEG)) == len(regeln) > 0

    def test_a_new_row_is_empty_and_invents_nothing(self, draft):
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        felder = verlaeufe.stuetzpunkte_aendern(
            verlaeufe.felder_aus_eingaben(punkte, "carbon_tax_level"),
            verlaeufe.neu_id("carbon_tax_level"),
        )

        assert felder[-1] == {k: None for k in verlaeufe.FELDER}
        _, neue = _eingaben(html.Div(verlaeufe.zeilen("carbon_tax_level", felder, False)))
        danach = verlaeufe.eingaben_anwenden(draft, starts, neue)
        assert danach["abweichungen"] == {}, "Eine leere Zeile ist keine Abweichung"

    def test_removing_a_scenario_rule_is_a_deviation(self, draft):
        starts, punkte = _eingaben(verlaeufe.editor(draft, "carbon_tax_level"))
        vorher = verlaeufe.felder_aus_eingaben(punkte, "carbon_tax_level")
        felder = verlaeufe.stuetzpunkte_aendern(vorher, verlaeufe.weg_id("carbon_tax_level", 0))
        _, neue = _eingaben(html.Div(verlaeufe.zeilen("carbon_tax_level", felder, False)))

        danach = verlaeufe.eingaben_anwenden(draft, starts, neue)

        assert len(felder) == len(vorher) - 1
        assert len(danach["abweichungen"]["carbon_tax_level"]["rules"]) == len(vorher) - 1

    def test_the_rows_renumber_after_removal(self):
        felder = [
            {"tick": 1, "art": "set", "wert": 1.0, "dauer": None},
            {"tick": 2, "art": "set", "wert": 2.0, "dauer": None},
            {"tick": 3, "art": "set", "wert": 3.0, "dauer": None},
        ]
        rest = verlaeufe.stuetzpunkte_aendern(felder, verlaeufe.weg_id("x", 1))
        _, neue = _eingaben(html.Div(verlaeufe.zeilen("x", rest, False)))

        assert [f["tick"] for f in verlaeufe.felder_aus_eingaben(neue, "x")] == [1, 3]
        assert sorted({e["id"]["index"] for e in neue}) == [0, 1]

    @pytest.mark.parametrize("anzahl", [0, 2])
    def test_the_rows_carry_a_counter_even_when_empty(self, anzahl):
        """Nach dem Entfernen der letzten Zeile muss `_sync` trotzdem feuern.

        Der Zähler ist ein Eingang von `_sync` und wird mit den Zeilen neu
        eingefügt — auch wenn es keine Felder mehr gibt, die das auslösen könnten.
        """

        felder = [{"tick": 1, "art": "set", "wert": 1.0, "dauer": None}] * anzahl
        zaehler = _knoepfe(html.Div(verlaeufe.zeilen("x", felder, False)), verlaeufe.STAND)

        assert len(zaehler) == 1
        assert zaehler[0].data == anzahl

    def test_both_actions_are_locked_without_the_switch(self, draft):
        draft["apply_custom_overrides"] = False
        baum = verlaeufe.editor(draft, "carbon_tax_level")

        knoepfe = _knoepfe(baum, verlaeufe.NEU) + _knoepfe(baum, verlaeufe.WEG)

        assert knoepfe and all(k.disabled for k in knoepfe)


class TestDiePreisstrategieIstEineWahl:
    """Teil 2b-3: die Preisstrategie im Schritt, vorbelegt mit dem Szenario."""

    def _auswahl(self, draft) -> dcc.RadioItems:
        return _radio(verlaeufe.strategie(draft))

    def _eintraege(self, wert) -> list:
        return [{"id": verlaeufe.strategie_id(), "value": wert}]

    def test_every_strategy_has_words_not_a_name(self):
        from src.models.property_models import STRATEGIEN

        assert set(verlaeufe.STRATEGIE_TEXTE) == set(STRATEGIEN)

    def test_preselected_with_the_scenario_strategy(self, draft):
        from dashboard.config_catalog import szenario_preisstrategie

        assert self._auswahl(draft).value == szenario_preisstrategie(draft_from_dict(draft))

    def test_reading_back_unchanged_is_no_deviation(self, draft):
        wert = self._auswahl(draft).value

        danach = verlaeufe.eingaben_anwenden(draft, [], [], self._eintraege(wert))

        assert danach["preisstrategie"] is None
        assert danach["abweichungen"] == {}

    def test_the_other_strategy_arrives_in_the_run(self, draft):
        from dashboard.config_catalog import prepare_simulation_state

        andere = next(
            o["value"]
            for o in self._auswahl(draft).options
            if o["value"] != self._auswahl(draft).value
        )

        danach = verlaeufe.eingaben_anwenden(draft, [], [], self._eintraege(andere))
        state = prepare_simulation_state(draft_from_dict(danach))

        assert danach["preisstrategie"] == andere
        effekte = [r.effect for r in state.properties.market_rules]
        assert any(e.get("strategie") == andere for e in effekte)
        assert state.rahmen.quelle == "abgeleitet"
        assert "preisstrategie" in state.rahmen.abweichungen

    def test_locked_without_the_switch(self, draft):
        draft["apply_custom_overrides"] = False

        assert all(o["disabled"] for o in self._auswahl(draft).options)

    def test_it_stands_left_under_the_list_once(self, draft):
        """Links unter der Liste, nicht im rechten Wirt (Haiko, 2026-09-15, nach Messung).

        Im rechten Wirt stünde sie zweimal im Baum, sobald er neu gezeichnet wird,
        und der Schritt passte bei 1440 × 900 nicht mehr auf einen Schirm.
        """

        links = [getattr(k, "id", None) for k in _walk(verlaeufe.layout(draft))]
        rechts = [
            getattr(k, "id", None) for k in _walk(verlaeufe.detail(draft, "carbon_tax_level"))
        ]

        assert links.count(verlaeufe.strategie_id()) == 1
        assert verlaeufe.strategie_id() not in rechts


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
