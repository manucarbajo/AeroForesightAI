"""Der Abschlusstext eines Laufs liest die Daten **dieses** Laufs (P8-V4).

Der Szenario-Generator (`run_scenario_generator`) liest seine Grundlage von der
Platte — richtig, denn «Szenarien neu erzeugen» im Dashboard arbeitet
nachträglich auf denselben Dateien. Bis zum 2026-09-29 lief er aber **vor**
`save_run_metadata`, in beiden Startpfaden:

- im Einzellauf (`run_simulation.save_run_outputs`) fand er noch keine
  `run_metadata.json` und schrieb «? Ticks» über jeden Lauf;
- im Szenario-Vergleich (`scenario_sweeps.run_single_sweep`), der in feste
  Ordner schreibt, las er die Metadaten des **vorigen** Durchlaufs — gemessen
  «50 Ticks» über einen Lauf mit 120.

Dazu blieb eine `llm_incidents.json` eines früheren Laufs liegen, weil ohne
Vorfall nichts geschrieben wurde; die Telemetrie im Leitstand liest genau diese
Datei und zeigte einen Ausfall, den es im neuen Lauf nicht gab.

**Die Tests bilden die echte Schreibreihenfolge ab**, nicht eine vorab angelegte
Datei — genau daran war der Befund vorbeigegangen: `test_run_scenario_generator.py`
legt `run_metadata.json` per Fixture an, bevor der Generator läuft.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.models.llm_models import LLMIncident
from src.models.sweep_models import SweepConfig
from src.orchestration.scenario_sweeps import run_single_sweep
from src.reporting.output_writer import save_llm_incidents
from src.reporting.output_writer.paths import resolve_run_output_dir

REPO = Path(__file__).resolve().parents[1]


def _veraltet_anlegen(ordner: Path, ticks: int) -> None:
    """Artefakte eines früheren Laufs mit anderer Länge und einem Ausfall."""

    ordner.mkdir(parents=True, exist_ok=True)
    (ordner / "run_metadata.json").write_text(
        json.dumps({"ticks_completed": ticks, "ticks_max": ticks}), encoding="utf-8"
    )
    save_llm_incidents(
        [LLMIncident(tick=ticks, caller="run_scenario_generator", kind="call_failed", error="alt")],
        run_dir=ordner,
    )


class TestDerSzenarioVergleichLiestSeinenLauf:
    """Ein zweiter Durchlauf in denselben Ordner — der Fall vom 2026-09-29."""

    def _sweep(self) -> SweepConfig:
        return SweepConfig(
            id="liest_seinen_lauf", name="Liest seinen Lauf", description="", max_ticks=4
        )

    def test_der_abschlusstext_nennt_die_gerechneten_ticks(self):
        ordner = resolve_run_output_dir("sweeps/sweep_liest_seinen_lauf")
        _veraltet_anlegen(ordner, ticks=50)

        run_single_sweep(self._sweep(), verbose=False, llm_narrative=False)

        text = (ordner / "run_scenario.md").read_text(encoding="utf-8")
        assert "(4 Ticks)" in text, text[:400]
        assert "(50 Ticks)" not in text

    def test_kein_ausfall_eines_frueheren_laufs_bleibt_liegen(self):
        ordner = resolve_run_output_dir("sweeps/sweep_liest_seinen_lauf")
        _veraltet_anlegen(ordner, ticks=50)

        run_single_sweep(self._sweep(), verbose=False, llm_narrative=False)

        metadaten = json.loads((ordner / "run_metadata.json").read_text(encoding="utf-8"))
        assert metadaten["degraded"] is False
        assert not (ordner / "llm_incidents.json").exists()


class TestDerEinzellaufLiestSeinenLauf:
    """Die CLI als eigener Prozess — der gemeinsame Pfad von CLI und Dashboard."""

    def test_der_abschlusstext_nennt_die_gerechneten_ticks(self, ausgabe_im_temp):
        run_id = "liest_seinen_lauf_einzeln"
        ergebnis = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.run_simulation",
                "--mock-llm",
                "--rounds",
                "2",
                "--run-id",
                run_id,
                "--quiet",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO,
            timeout=300,
        )
        assert ergebnis.returncode == 0, ergebnis.stderr[-2000:]

        text = (Path(ausgabe_im_temp) / run_id / "run_scenario.md").read_text(encoding="utf-8")
        assert "(2 Ticks)" in text, text[:400]
        assert "? Ticks" not in text


class TestOhneVorfallBleibtKeineDatei:
    def test_eine_alte_datei_im_laufordner_wird_abgeraeumt(self, tmp_path):
        _veraltet_anlegen(tmp_path, ticks=50)
        assert (tmp_path / "llm_incidents.json").exists()

        assert save_llm_incidents([], run_dir=tmp_path) is None
        assert not (tmp_path / "llm_incidents.json").exists()

    def test_ohne_laufordner_wird_nichts_angefasst(self, ausgabe_im_temp):
        """Abgeräumt wird nur in einem benannten Laufordner, nie in der Ausgabewurzel."""

        wurzel = Path(ausgabe_im_temp) / "llm_incidents.json"
        wurzel.write_text("[]", encoding="utf-8")
        try:
            assert save_llm_incidents([]) is None
            assert wurzel.exists()
        finally:
            wurzel.unlink()
