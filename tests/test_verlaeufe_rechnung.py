"""Die Rechnung hinter dem Schritt «Verläufe» (P7.13-U13.1 Teil 1).

Der Schritt zeigt je Systemgröße zwei Kurven — das gewählte Szenario und die eigene
Fassung — und schreibt nur, was davon abweicht. Drei Zusagen tragen das:

1. **Die Kurve rechnet wie der Lauf.** Sie kommt aus dem Zustand, den
   `prepare_simulation_state` baut, nicht aus einer zweiten Verlaufsrechnung.
2. **Was dem Szenario gleicht, ist keine Abweichung.** Sonst stünde jede angesehene
   Größe als «abgeleitet» im Artefakt.
3. **Welche Größen offen stehen, folgt aus den Rahmen**, nicht aus einer Liste.
"""

from __future__ import annotations

from dashboard.config_catalog import (
    PropertyEditState,
    abweichungen_bereinigen,
    default_config_draft,
    exogene_groessen,
    list_sweep_presets,
    prepare_simulation_state,
    szenario_preisstrategie,
    szenario_verlauf,
    verlaeufe_je_tick,
    von_rahmen_veraendert,
)
from src.models.sweep_models import PropertyOverride, SweepConfig
from src.orchestration.scenario_sweeps import SWEEPS_DIR, load_sweep_config

SZENARIO = "business_as_usual"


def _entwurf(**felder):
    draft = default_config_draft()
    draft.scenario_mode = "sweep"
    draft.sweep_id = SZENARIO
    for feld, wert in felder.items():
        setattr(draft, feld, wert)
    return draft


def _co2(baseline: float) -> dict:
    return {
        "carbon_tax_level": PropertyEditState(property_id="carbon_tax_level", baseline=baseline)
    }


class TestWelcheGroessenImSchrittStehen:
    def test_only_trajectories_not_what_the_run_computes(self):
        groessen = exogene_groessen()

        assert "provider_markup" not in groessen
        assert "ticket_price" not in groessen
        assert "carbon_tax_level" in groessen
        assert "bevoelkerungsentwicklung" in groessen

    def test_the_open_ones_come_from_the_frames(self):
        offen = von_rahmen_veraendert()
        erwartet = {
            o.property_id
            for pfad in SWEEPS_DIR.glob("*.json")
            if (s := load_sweep_config(pfad)).art == "rahmen"
            for o in s.property_overrides
        }

        assert offen == erwartet
        assert offen <= set(exogene_groessen())
        assert offen, "Gegen Blindheit: ohne einen Rahmen, der etwas verändert, prüfte das nichts"

    def test_an_own_scenario_does_not_open_anything(self, monkeypatch):
        """Nur Rahmen zählen — ein gesichertes Experiment ist kein Weltbild (P2.2)."""

        from dashboard import config_catalog

        eigenes = SweepConfig(
            id="mein_versuch",
            name="Mein Versuch",
            description="gesichert",
            max_ticks=40,
            herkunft="eigen",
            property_overrides=[PropertyOverride(property_id="altersmittel_jahre", baseline=60.0)],
        )
        vorher = von_rahmen_veraendert()
        assert "altersmittel_jahre" not in vorher, "Gegen Blindheit: die Größe muss sonst zu sein"
        monkeypatch.setattr(
            config_catalog, "list_sweep_presets", lambda: [*list_sweep_presets(), eigenes]
        )

        assert von_rahmen_veraendert() == vorher


class TestDerEditorStartetBeimSzenario:
    def test_it_shows_the_values_of_the_chosen_scenario(self):
        bau = load_sweep_config(SWEEPS_DIR / f"{SZENARIO}.json")
        override = next(o for o in bau.property_overrides if o.property_id == "carbon_tax_level")

        verlauf = szenario_verlauf(_entwurf(), "carbon_tax_level")

        assert verlauf.baseline == override.baseline
        assert len(verlauf.rules) == len(override.rules or [])

    def test_a_deviation_does_not_move_the_starting_point(self):
        mit = szenario_verlauf(_entwurf(abweichungen=_co2(77.0)), "carbon_tax_level")

        assert mit == szenario_verlauf(_entwurf(), "carbon_tax_level")

    def test_the_price_strategy_of_the_scenario(self):
        bau = load_sweep_config(SWEEPS_DIR / f"{SZENARIO}.json")

        assert szenario_preisstrategie(_entwurf(preisstrategie="marge")) == bau.preisstrategie


class TestDieKurveRechnetWieDerLauf:
    def test_without_deviation_both_curves_are_one(self):
        szenario, eigen = verlaeufe_je_tick(_entwurf(), "carbon_tax_level")

        assert szenario == eigen
        assert len(szenario) == _entwurf().rounds + 1

    def test_a_deviation_moves_only_the_own_curve(self):
        szenario, eigen = verlaeufe_je_tick(_entwurf(abweichungen=_co2(77.0)), "carbon_tax_level")

        assert eigen[0] == 77.0
        assert szenario[0] != 77.0

    def test_it_is_the_value_the_run_gets(self):
        """Nicht nachgerechnet, sondern verglichen: derselbe Zustand, derselbe Wert."""

        from src.market.property_engine import resolve_property

        entwurf = _entwurf(abweichungen=_co2(77.0))
        _, eigen = verlaeufe_je_tick(entwurf, "carbon_tax_level")
        state = prepare_simulation_state(entwurf)

        assert eigen == [
            resolve_property("carbon_tax_level", tick, state.properties)
            for tick in range(entwurf.rounds + 1)
        ]


class TestWasDemSzenarioGleichtIstKeineAbweichung:
    def test_an_unchanged_value_falls_away(self):
        gleich = {"carbon_tax_level": szenario_verlauf(_entwurf(), "carbon_tax_level")}

        assert abweichungen_bereinigen(_entwurf(abweichungen=gleich)).abweichungen == {}

    def test_a_changed_value_stays(self):
        assert set(abweichungen_bereinigen(_entwurf(abweichungen=_co2(77.0))).abweichungen) == {
            "carbon_tax_level"
        }

    def test_the_step_function_too(self):
        """Die Bevölkerung ist eine Stufenfunktion; der Editor trägt sie als Regeln."""

        gleich = {
            "bevoelkerungsentwicklung": szenario_verlauf(_entwurf(), "bevoelkerungsentwicklung")
        }

        assert abweichungen_bereinigen(_entwurf(abweichungen=gleich)).abweichungen == {}

    def test_the_scenarios_own_strategy_is_no_deviation(self):
        eigene = szenario_preisstrategie(_entwurf())

        assert abweichungen_bereinigen(_entwurf(preisstrategie=eigene)).preisstrategie is None
        andere = "marge" if eigene == "auslastung" else "auslastung"
        assert abweichungen_bereinigen(_entwurf(preisstrategie=andere)).preisstrategie == andere

    def test_a_cleaned_draft_computes_the_same(self):
        """Die Bereinigung ändert nur das Etikett, nie die Rechnung."""

        gleich = {"carbon_tax_level": szenario_verlauf(_entwurf(), "carbon_tax_level")}
        roh = _entwurf(abweichungen=gleich)

        vorher = prepare_simulation_state(roh).properties.model_dump()
        nachher = prepare_simulation_state(abweichungen_bereinigen(roh)).properties.model_dump()
        assert nachher == vorher
