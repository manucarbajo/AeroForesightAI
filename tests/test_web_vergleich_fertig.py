"""Was nach einem Szenario-Vergleich gewählt ist und gemeldet wird (P8-V6, Befund 9).

**Der Befund vom 2026-09-30:** Nach dem Vergleich blieb der vorige Lauf gewählt,
und die Fertigmeldung — wo sie ankam — nannte den Pfad der Zusammenfassung und
die Kennung **jedes** Ordners unter `sweeps/`, rückwärts sortiert. Gewählt worden
wäre danach, was im Alphabet hinten lag, auch ein alter Prüflauf.
"""

from __future__ import annotations

import json
from pathlib import Path

from dashboard import run_launcher
from dashboard.run_launcher import RunLaunchConfig, launch_simulation
from dashboard.web.pages import launch as launch_page
from src.models.sweep_models import SweepResult, SweepSummary
from src.orchestration import scenario_sweeps

GERECHNET = (("business_as_usual", "Business as Usual (A1+B1)"), ("co2_delayed", "CO₂-Verzögerung"))


def _vergleich(monkeypatch, tmp_path: Path):
    ausgabe = tmp_path / "sweeps"
    for kennung in ("business_as_usual", "co2_delayed", "zzz_test_short"):
        (ausgabe / f"sweep_{kennung}").mkdir(parents=True)
        (ausgabe / f"sweep_{kennung}" / "run_metadata.json").write_text(
            json.dumps({}), encoding="utf-8"
        )

    def _gerechnet(**_kwargs) -> SweepSummary:
        return SweepSummary(
            total_sweeps=len(GERECHNET),
            results=[
                SweepResult(
                    sweep_id=kennung,
                    sweep_name=name,
                    ticks_completed=3,
                    final_factor_states={},
                    final_properties={},
                )
                for kennung, name in GERECHNET
            ],
        )

    monkeypatch.setattr(scenario_sweeps, "run_all_sweeps", _gerechnet)
    monkeypatch.setattr(scenario_sweeps, "SWEEP_OUTPUT_DIR", ausgabe)
    monkeypatch.setattr(run_launcher, "generate_figures_for_run", lambda *_a, **_k: None)
    return launch_simulation(RunLaunchConfig(run_all_sweeps=True), repo_root=tmp_path)


class TestNurDieLaeufeDiesesVergleichs:
    def test_ein_alter_pruef_lauf_gehoert_nicht_dazu(self, monkeypatch, tmp_path):
        ergebnis = _vergleich(monkeypatch, tmp_path)

        assert ergebnis.child_run_ids == (
            "sweeps/sweep_business_as_usual",
            "sweeps/sweep_co2_delayed",
        )
        assert ergebnis.child_names == tuple(name for _k, name in GERECHNET)

    def test_gewaehlt_wird_der_erste_rahmen(self, monkeypatch, tmp_path):
        ergebnis = _vergleich(monkeypatch, tmp_path)

        assert ergebnis.run_id == "sweeps/sweep_business_as_usual"


class TestDieMeldung:
    def test_sie_nennt_die_rahmen_und_die_wahl(self, monkeypatch, tmp_path):
        text = str(launch_page._result_message(_vergleich(monkeypatch, tmp_path)))

        assert "2 Rahmenszenarien gerechnet" in text
        assert "Gewählt ist «Business as Usual (A1+B1)»" in text
        assert "Ergebnisse ansehen" in text

    def test_sie_nennt_keinen_pfad_und_keine_kennung(self, monkeypatch, tmp_path):
        text = str(launch_page._result_message(_vergleich(monkeypatch, tmp_path)))

        assert "sweeps/" not in text and "sweep_summary" not in text
        assert "zzz_test_short" not in text
