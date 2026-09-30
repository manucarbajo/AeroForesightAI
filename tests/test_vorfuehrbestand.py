"""Der Vorführbestand — was er verschiebt, was er rechnet, woran er einen Lauf misst (P8-V5).

Rechnen mit dem Sprachmodell kann dieser Test nicht; er hält fest, **was**
gerechnet wird (die Konfigurationen tragen den Pitch-Fall wirklich), **wohin**
verschoben wird (nichts wird gelöscht, nichts landet in ``outputs/``) und **woran**
ein fertiger Lauf gemessen wird.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard.config_catalog import prepare_simulation_state
from dashboard.run_launcher import launch_config_to_draft
from dashboard.vorfuehrbestand import (
    BEHALTEN,
    PITCH_STRATEGIE,
    archivieren,
    bestand,
    pruefen,
)
from src.market.property_engine import resolve_property
from src.orchestration.scenario_sweeps import rahmenszenarien


class TestArchivieren:
    def _ausgabe(self, tmp_path: Path) -> Path:
        ausgabe = tmp_path / "outputs"
        (ausgabe / "run_20260101T000000Z").mkdir(parents=True)
        (ausgabe / "run_20260101T000000Z" / "run_metadata.json").write_text("{}", encoding="utf-8")
        (ausgabe / "sweeps" / "sweep_x").mkdir(parents=True)
        (ausgabe / "event_log.json").write_text("[]", encoding="utf-8")
        for name in BEHALTEN:
            (ausgabe / name).write_text("bleibt", encoding="utf-8")
        return ausgabe

    def test_alles_ausser_dem_behaltenen_wandert_ins_archiv(self, tmp_path: Path):
        ausgabe = self._ausgabe(tmp_path)

        ziel = archivieren(ausgabe, tmp_path / "archiv")

        assert ziel is not None and ziel.parent == (tmp_path / "archiv").resolve()
        assert sorted(p.name for p in ausgabe.iterdir()) == sorted(BEHALTEN)
        assert (
            ziel / "run_20260101T000000Z" / "run_metadata.json"
        ).is_file(), "verschoben, nicht gelöscht"
        assert (ziel / "sweeps" / "sweep_x").is_dir()
        assert (ziel / "event_log.json").is_file()

    def test_ohne_inhalt_entsteht_kein_leerer_archivordner(self, tmp_path: Path):
        ausgabe = tmp_path / "outputs"
        ausgabe.mkdir()
        (ausgabe / ".gitkeep").write_text("", encoding="utf-8")

        assert archivieren(ausgabe, tmp_path / "archiv") is None
        assert not (tmp_path / "archiv").exists()

    def test_ein_archiv_in_outputs_wird_abgewiesen(self, tmp_path: Path):
        """Der Lauf-Browser läse es weiter — der Zweck wäre verfehlt."""

        ausgabe = self._ausgabe(tmp_path)

        with pytest.raises(ValueError):
            archivieren(ausgabe, ausgabe / "archiv")
        assert (ausgabe / "run_20260101T000000Z").is_dir(), "Nichts darf verschoben sein"


def laeufe_kennungen() -> list[str]:
    return [lauf.kennung for lauf in bestand()]


def _zustand(kennung: str):
    lauf = next(lauf for lauf in bestand() if lauf.kennung == kennung)
    return prepare_simulation_state(launch_config_to_draft(lauf.konfiguration))


class TestDerBestandRechnetDenPitchFall:
    def test_der_vergleich_prueft_jeden_rahmen(self):
        vergleich = next(lauf for lauf in bestand() if lauf.kennung == "vergleich")

        assert vergleich.ordner == tuple(f"sweeps/sweep_{r.id}" for r in rahmenszenarien())

    def test_business_as_usual_laeuft_unveraendert(self):
        zustand = _zustand("vorfuehrung_bau")

        assert zustand.clock.max_ticks == 40
        assert zustand.rahmen.quelle == "preset"
        assert resolve_property("carbon_tax_level", 30, zustand.properties) == 50.0

    def test_der_pitch_fall_hebt_die_co2_abgabe_ab_tick_24(self):
        zustand = _zustand("vorfuehrung_co2")

        assert zustand.rahmen.quelle == "abgeleitet"
        assert zustand.rahmen.abweichungen == ["carbon_tax_level", "preisstrategie"]
        assert resolve_property("carbon_tax_level", 23, zustand.properties) == 50.0
        assert resolve_property("carbon_tax_level", 24, zustand.properties) == 200.0

    def test_der_pitch_fall_und_seine_referenz_unterscheiden_sich_nur_in_der_abgabe(self):
        """**Befund 8 der Abnahme vom 2026-09-30.** Unter «Plätze füllen» sank der
        Preis nach dem Sprung der Abgabe; der Pitch-Fall rechnet deshalb mit
        «Aufschlag halten» — und seine Referenz ebenso, sonst vergliche man zwei
        Änderungen auf einmal."""

        laeufe = {lauf.kennung: lauf.konfiguration for lauf in bestand()}
        referenz, fall = laeufe["vorfuehrung_bau_marge"], laeufe["vorfuehrung_co2"]

        assert referenz.preisstrategie == fall.preisstrategie == PITCH_STRATEGIE == "marge"
        assert referenz.abweichungen is None and set(fall.abweichungen) == {"carbon_tax_level"}
        assert (referenz.rounds, referenz.sweep_id) == (fall.rounds, fall.sweep_id)
        assert _zustand("vorfuehrung_bau_marge").rahmen.abweichungen == ["preisstrategie"]

    def test_der_unveraenderte_rahmen_bleibt_im_bestand(self):
        assert laeufe_kennungen()[:2] == ["vergleich", "vorfuehrung_bau"]

    def test_jeder_einzellauf_rechnet_mit_dem_sprachmodell(self):
        for lauf in bestand():
            assert not lauf.konfiguration.mock_llm and not lauf.konfiguration.deterministic_only

    def test_der_pitch_fall_ist_der_juengste(self):
        """Er wird zuletzt gerechnet und steht im Lauf-Browser oben."""

        assert bestand()[-1].kennung == "vorfuehrung_co2"


class TestPruefen:
    def _lauf(self, tmp_path: Path, *, metadaten: dict | None = None, **szenario) -> Path:
        run_dir = tmp_path / "lauf"
        run_dir.mkdir()
        meta = {"compute_mode": "llm", "degraded": False, "ticks_completed": 40, "ticks_max": 40}
        meta.update(metadaten or {})
        (run_dir / "run_metadata.json").write_text(json.dumps(meta), encoding="utf-8")
        inhalt = {"source": "llm", "widersprueche": []}
        inhalt.update(szenario)
        (run_dir / "run_scenario.json").write_text(json.dumps(inhalt), encoding="utf-8")
        (run_dir / "event_log.json").write_text(
            json.dumps(
                [
                    {"event_type": "market_event", "description": "The market price is set."},
                    {"description": "[delta:booking] booking rate changed (Python delta)"},
                    {"event_type": "policy_change", "description": "Die Abgabe wird angehoben."},
                ]
            ),
            encoding="utf-8",
        )
        return run_dir

    def test_ein_vollstaendiger_lauf_besteht(self, tmp_path: Path):
        assert pruefen(self._lauf(tmp_path), "llm") == ([], [])

    @pytest.mark.parametrize(
        ("metadaten", "szenario", "erwartet"),
        [
            ({"degraded": True}, {}, "ausgefallen"),
            ({"compute_mode": "mock_llm"}, {}, "Rechenmodus"),
            ({"ticks_completed": 12}, {}, "12 von 40"),
            ({}, {"source": "template"}, "Vorlage"),
        ],
    )
    def test_was_die_vorfuehrung_bricht_ist_hart(self, tmp_path, metadaten, szenario, erwartet):
        hart, _ = pruefen(self._lauf(tmp_path, metadaten=metadaten, **szenario), "llm")

        assert any(erwartet in zeile for zeile in hart), hart

    def test_ein_englischer_agententext_ist_hart(self, tmp_path: Path):
        run_dir = self._lauf(tmp_path)
        (run_dir / "event_log.json").write_text(
            json.dumps(
                [{"description": "Implement a pilot program for the fleet and the routes."}]
            ),
            encoding="utf-8",
        )

        hart, _ = pruefen(run_dir, "llm")

        assert any("englische" in zeile for zeile in hart)

    def test_ein_markierter_widerspruch_ist_ein_hinweis(self, tmp_path: Path):
        widerspruch = [{"zeile": "Nachfrage: im Text «steigt», gerechnet «sinkt»."}]

        hart, hinweise = pruefen(self._lauf(tmp_path, widersprueche=widerspruch), "llm")

        assert hart == [] and len(hinweise) == 1


class TestDerLaufBrowserZeigtDenBestand:
    def test_jeder_lauf_des_bestands_steht_in_der_liste(self, tmp_path: Path):
        """**Der erste Bestand am 2026-09-30 war zur Hälfte unsichtbar.** Die Einzelläufe
        hießen `vorfuehrung_bau` und `vorfuehrung_co2`, und `list_runs` nimmt nur
        Ordner auf, die mit `run_` beginnen — ausgerechnet der Pitch-Fall fehlte."""

        from dashboard.run_browser import list_runs

        erwartet = [ordner for lauf in bestand() for ordner in lauf.ordner]
        for ordner in erwartet:
            (tmp_path / ordner).mkdir(parents=True)
            (tmp_path / ordner / "run_metadata.json").write_text(
                json.dumps({"timestamp": "2026-09-30T10:00:00+00:00"}), encoding="utf-8"
            )

        gefunden = {lauf.run_id for lauf in list_runs(tmp_path)}

        assert set(erwartet) <= gefunden, set(erwartet) - gefunden


class TestEinEinzelnerLaufNeu:
    def test_nur_seine_ordner_wandern(self, tmp_path: Path):
        ausgabe = tmp_path / "outputs"
        for ordner in ("sweeps/sweep_a", "sweeps/sweep_b", "run_vorfuehrung_bau"):
            (ausgabe / ordner).mkdir(parents=True)
            (ausgabe / ordner / "run_metadata.json").write_text("{}", encoding="utf-8")

        ziel = archivieren(ausgabe, tmp_path / "archiv", nur=("sweeps/sweep_a", "fehlt"))

        assert ziel is not None
        assert (ziel / "sweeps" / "sweep_a" / "run_metadata.json").is_file()
        assert not (ausgabe / "sweeps" / "sweep_a").exists()
        assert (ausgabe / "sweeps" / "sweep_b").is_dir() and (
            ausgabe / "run_vorfuehrung_bau"
        ).is_dir()

    def test_ohne_vorhandenen_ordner_passiert_nichts(self, tmp_path: Path):
        ausgabe = tmp_path / "outputs"
        ausgabe.mkdir()

        assert archivieren(ausgabe, tmp_path / "archiv", nur=("run_vorfuehrung_bau",)) is None
