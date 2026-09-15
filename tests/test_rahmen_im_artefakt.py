"""P2.0-B — ein Lauf sagt, unter welchem Rahmen er stand.

Mit der Umdrehung ist das Rahmenszenario die **zentrale Eingabe**: Es setzt die
exogenen Verläufe, aus denen der Lauf Nachfrage, Preise und Faktorlage erzeugt.
Bis zum 2026-08-30 hielt kein Artefakt fest, welches es war.

Ganz unsichtbar war es nicht — `config_fingerprint` unterscheidet die neun
Rahmen, jeder trägt einen eigenen `properties`-Hash. Aber eben nur als
undurchsichtige Zeichenkette: Man sah *dass* ein anderer Rahmen lief, nicht
*welcher*. Für die Frage «unter welcher Außenwelt ist diese Zahl entstanden» —
der Frage, um die es beim Verkaufen geht — war das keine Antwort.

Drei Zusagen hängen hier:

1. **Jeder Startpfad setzt ihn.** Preset, eigene Werte und die ausgelieferten
   Dateien — auch letztere sind ein Rahmen, nur ein unbenannter.
2. **Er steht im Artefakt**, gelesen aus dem Zustand statt am Ende erraten. Am
   Ende erraten ginge auch gar nicht: Ein Sweep legt seine Werte in den Zustand,
   und aus den Zahlen allein lässt sich der Name nicht zurückgewinnen.
3. **Ein Lauf ohne Angabe bekommt keine erfundene.** Ältere Artefakte tragen das
   Feld nicht; dann steht in der Oberfläche «nicht festgehalten».
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard.config_catalog import default_config_draft, prepare_simulation_state
from src.models.run_models import RunArgs
from src.models.state_models import Rahmenszenario
from src.orchestration.scenario_sweeps import SWEEPS_DIR, load_sweep_config

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestJederStartpfadSetztIhn:
    """Zusage 1 — kein Weg in den Lauf lässt die Frage offen."""

    def test_die_ausgelieferten_dateien_sind_auch_ein_rahmen(self):
        draft = default_config_draft()
        draft.scenario_mode = "basis"
        draft.apply_custom_overrides = False

        state = prepare_simulation_state(draft)

        assert state.rahmen is not None, (
            "Ein Lauf ohne Preset trägt keinen Rahmen — dann sieht es aus, als "
            "liefe er «ohne Szenario». Er läuft unter den ausgelieferten Verläufen."
        )
        assert state.rahmen.quelle == "standard"

    def test_ein_preset_traegt_seinen_namen(self):
        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = "business_as_usual"

        state = prepare_simulation_state(draft)

        assert state.rahmen is not None
        assert state.rahmen.id == "business_as_usual"
        assert state.rahmen.quelle == "preset"
        assert state.rahmen.name, "Der Name fehlt — die Kennung allein liest niemand"

    def test_eigene_werte_heissen_eigene_werte(self):
        draft = default_config_draft()
        draft.scenario_mode = "custom"

        state = prepare_simulation_state(draft)

        assert state.rahmen is not None
        assert state.rahmen.quelle == "eigen"

    def test_geaenderte_standardwerte_heissen_eigen(self):
        """Gemessen am 2026-09-15: CO₂-Start 99 im Modell, der Lauf rechnete damit —
        und stand im Artefakt als «Standard-Ausgangslage»."""

        draft = default_config_draft()
        draft.scenario_mode = "basis"
        draft.apply_custom_overrides = True
        draft.property_edits["carbon_tax_level"].baseline = 99.0

        state = prepare_simulation_state(draft)

        co2 = next(p for p in state.properties.system_properties if p.id == "carbon_tax_level")
        assert co2.trajectory.baseline == 99.0, "Vorbedingung: der geänderte Wert kommt an"
        assert state.rahmen is not None
        assert state.rahmen.quelle == "eigen"

    def test_ohne_aenderung_bleibt_der_standard_der_standard(self):
        """Der Schalter ist per Vorgabe an — er allein macht keinen eigenen Rahmen."""

        draft = default_config_draft()
        draft.scenario_mode = "basis"
        draft.apply_custom_overrides = True

        state = prepare_simulation_state(draft)

        assert state.rahmen is not None
        assert state.rahmen.quelle == "standard"

    def test_jedes_ausgelieferte_preset_kommt_durch(self):
        """Nicht eines von acht, sondern alle — ein fehlender Name fiele sonst
        erst dem auf, der genau dieses Szenario rechnet."""

        ohne_namen = []
        for pfad in sorted(SWEEPS_DIR.glob("*.json")):
            draft = default_config_draft()
            draft.scenario_mode = "sweep"
            draft.sweep_id = pfad.stem
            state = prepare_simulation_state(draft)
            if state.rahmen is None or not state.rahmen.name:
                ohne_namen.append(pfad.stem)

        assert not ohne_namen, f"Diese Szenarien tragen keinen lesbaren Rahmen: {ohne_namen}"

    def test_ein_abgeleiteter_lauf_nennt_szenario_und_abweichungen(self):
        """P7.13-U13.2 — ein geändertes Szenario steht nicht als unverändertes da."""

        from dashboard.config_catalog import PropertyEditState

        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = "business_as_usual"
        draft.abweichungen = {
            "carbon_tax_level": PropertyEditState(property_id="carbon_tax_level", baseline=77.0)
        }
        draft.preisstrategie = "marge"

        state = prepare_simulation_state(draft)

        assert state.rahmen is not None
        assert state.rahmen.id == "business_as_usual"
        assert state.rahmen.quelle == "abgeleitet"
        assert state.rahmen.abweichungen == ["carbon_tax_level", "preisstrategie"]
        # **Und der Wert selbst**, nicht nur das Etikett: Ein Rahmen, der
        # «abgeleitet» heißt, ohne dass die Abweichung gelegt wurde, wäre die
        # nächste stille Falschaussage.
        co2 = next(p for p in state.properties.system_properties if p.id == "carbon_tax_level")
        assert co2.trajectory.baseline == 77.0
        feedback = next(
            r
            for r in state.properties.market_rules
            if r.effect.get("type") == "booking_yield_feedback"
        )
        assert feedback.effect.get("strategie") == "marge"

    def test_eine_unbekannte_abweichung_scheitert_laut(self):
        """Still übersprungen wäre sie eine Abweichung, die nicht ankommt."""

        from dashboard.config_catalog import PropertyEditState

        draft = default_config_draft()
        draft.abweichungen = {
            "gibt_es_nicht": PropertyEditState(property_id="gibt_es_nicht", baseline=1.0)
        }

        with pytest.raises(ValueError, match="gibt_es_nicht"):
            prepare_simulation_state(draft)

    def test_die_kennung_stimmt_mit_der_datei_ueberein(self):
        """Sonst zeigte das Artefakt auf ein Szenario, das es nicht gibt."""

        pfad = SWEEPS_DIR / "co2_delayed.json"
        sweep = load_sweep_config(pfad)

        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = "co2_delayed"
        state = prepare_simulation_state(draft)

        assert state.rahmen is not None
        assert state.rahmen.id == sweep.id
        assert state.rahmen.name == sweep.name


class TestErStehtImArtefakt:
    """Zusage 2 — gelesen aus dem Zustand, nicht am Ende erraten."""

    def test_save_run_metadata_nimmt_ihn_aus_dem_zustand(self, tmp_path):
        from src.reporting.output_writer.metadata import save_run_metadata

        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = "business_as_usual"
        state = prepare_simulation_state(draft)

        args = RunArgs(
            model="x",
            base_url="y",
            temperature=0.0,
            max_tokens=1,
            no_market=False,
            seed=None,
            mock_llm=False,
            deterministic_only=False,
            llm_narrative=False,
            simulation_name=None,
            simulation_description=None,
        )
        pfad = save_run_metadata(state, args, run_dir=tmp_path)
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))

        assert daten["rahmen"]["id"] == "business_as_usual"
        assert daten["rahmen"]["quelle"] == "preset"

    def test_ohne_rahmen_steht_dort_nichts_erfundenes(self, tmp_path):
        """Ältere Läufe kennen das Feld nicht — `None` und keine Vermutung."""

        from src.reporting.output_writer.metadata import save_run_metadata

        draft = default_config_draft()
        state = prepare_simulation_state(draft)
        state.rahmen = None

        args = RunArgs(
            model="x",
            base_url="y",
            temperature=0.0,
            max_tokens=1,
            no_market=False,
            seed=None,
            mock_llm=False,
            deterministic_only=False,
            llm_narrative=False,
            simulation_name=None,
            simulation_description=None,
        )
        pfad = save_run_metadata(state, args, run_dir=tmp_path)
        daten = json.loads(Path(pfad).read_text(encoding="utf-8"))

        assert daten["rahmen"] is None


class TestDieOberflaecheZeigtIhn:
    """Zusage 3 — und sagt «nicht festgehalten», wo nichts steht."""

    @pytest.mark.parametrize(
        ("metadaten", "erwartet"),
        [
            ({"rahmen": {"id": "co2_delayed", "name": "CO₂-Verzögerung"}}, "CO₂-Verzögerung"),
            ({"rahmen": None}, "nicht festgehalten"),
            ({}, "nicht festgehalten"),
        ],
    )
    def test_der_name_steht_in_der_uebersicht(self, metadaten, erwartet):
        from dashboard.web.views import overview

        # Kleingeschrieben verglichen: Die Kachelbeschriftung steht in
        # Versalien, und der Test soll die Auskunft prüfen, nicht die Typografie.
        gezeigt = str(overview._provenance(metadaten)).lower()

        assert "rahmenszenario" in gezeigt
        assert erwartet.lower() in gezeigt


def test_der_fingerabdruck_allein_haette_nicht_gereicht():
    """Warum das Feld nötig war — als Messung, nicht als Behauptung.

    Der Fingerabdruck *unterscheidet* die Rahmen (das ist gut und bleibt so),
    aber er benennt sie nicht. Wäre er umkehrbar, bräuchte es dieses Feld nicht.
    """

    from src.reporting.output_writer.provenance import config_fingerprint

    abdruecke = {}
    for pfad in sorted(SWEEPS_DIR.glob("*.json")):
        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = pfad.stem
        abdruecke[pfad.stem] = config_fingerprint(prepare_simulation_state(draft)).properties

    assert len(set(abdruecke.values())) == len(abdruecke), (
        "Zwei Rahmen teilen sich einen Fingerabdruck — dann unterscheidet er sie "
        f"nicht mehr: {abdruecke}"
    )
    assert not any(name in abdruck for name, abdruck in abdruecke.items()), (
        "Der Fingerabdruck trägt den Namen des Szenarios — dann wäre er lesbar "
        "und das eigene Feld überflüssig."
    )


def test_das_modell_haelt_die_drei_quellen_auseinander():
    for quelle in ("preset", "eigen", "standard"):
        assert Rahmenszenario(id="x", name="X", quelle=quelle).quelle == quelle
