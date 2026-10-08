"""Ein Lauf mit verändertem Szenario heißt nicht wie der unveränderte (P8-V6).

Im Abnahme-Durchgang am 2026-09-30 stand der Ablauf aus dem Pitch — «Business as
Usual» wählen, die CO₂-Abgabe anheben, starten — in Lauf-Kopf, Lauf-Browser und
Übersicht als «Business as Usual (A1+B1)», genau wie der unveränderte Rahmen. Die
Metadaten wussten es (`rahmen.quelle: abgeleitet`), die Oberfläche zeigte es nicht.
"""

from __future__ import annotations

import json
from pathlib import Path

from dashboard.config_catalog import abweichungen_benannt
from dashboard.run_browser import list_runs
from dashboard.web.pages.runs import lauf_bezeichnung
from dashboard.web.views import overview


def _lauf(wurzel: Path, name: str, rahmen: dict) -> Path:
    run_dir = wurzel / name
    run_dir.mkdir(parents=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps({"timestamp": "2026-09-30T10:00:00+00:00", "rahmen": rahmen}), encoding="utf-8"
    )
    return run_dir


BAU = {"id": "business_as_usual", "name": "Business as Usual (A1+B1)", "quelle": "preset"}
ABGELEITET = {**BAU, "quelle": "abgeleitet", "abweichungen": ["carbon_tax_level"]}


def test_die_auswahl_unterscheidet_die_beiden_laeufe(tmp_path: Path):
    _lauf(tmp_path, "run_a", BAU)
    _lauf(tmp_path, "run_b", ABGELEITET)

    namen = {lauf.run_id: lauf_bezeichnung(lauf, vorgabe="") for lauf in list_runs(tmp_path)}

    assert namen["run_a"].startswith("Business as Usual (A1+B1) · ")
    assert namen["run_b"].startswith("Business as Usual (A1+B1), verändert · ")


def test_die_uebersicht_nennt_was_geaendert_wurde(tmp_path: Path):
    text = str(overview.render(_lauf(tmp_path, "run_b", ABGELEITET), "run_b"))

    assert "Business as Usual (A1+B1), verändert" in text
    assert (
        "Gegenüber dem Szenario geändert: " + abweichungen_benannt(["carbon_tax_level"])[0] in text
    )


def test_ein_unveraenderter_rahmen_bleibt_wie_er_heisst(tmp_path: Path):
    text = str(overview.render(_lauf(tmp_path, "run_a", BAU), "run_a"))

    assert "verändert" not in text


def test_die_kennung_bekommt_den_namen_der_oberflaeche():
    assert abweichungen_benannt(["carbon_tax_level", "preisstrategie", "unbekannt.x"])[1:] == [
        "Preisstrategie",
        "unbekannt.x",
    ]
    assert "CO" in abweichungen_benannt(["carbon_tax_level"])[0]
