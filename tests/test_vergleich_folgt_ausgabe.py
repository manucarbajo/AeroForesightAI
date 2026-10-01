"""Ein Vergleich schreibt seine Zusammenfassung dorthin, wo seine Läufe liegen.

Audit-Befund vom 2026-09-30 (P8-Nachtrag): `SWEEP_OUTPUT_DIR` stand fest auf
`outputs/sweeps` im Repository und las `AF_AUSGABE` nicht — wer die Variable
setzte, um einen Bestand zu schonen, überschrieb dessen `sweep_summary.json`
trotzdem. Gemessen in einem Unterprozess, weil die Suite selbst die
Modulvariable umleitet und den Fehler deshalb nie sähe.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_die_zusammenfassung_folgt_af_ausgabe(tmp_path):
    umgebung = {**os.environ, "AF_AUSGABE": str(tmp_path)}
    ergebnis = subprocess.run(
        [
            sys.executable,
            "-c",
            "from src.orchestration.scenario_sweeps import SWEEP_OUTPUT_DIR; "
            "from src.reporting.output_writer import OUTPUT_DIR; "
            "print(SWEEP_OUTPUT_DIR); print(OUTPUT_DIR)",
        ],
        capture_output=True,
        text=True,
        env=umgebung,
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )
    sweeps, laeufe = ergebnis.stdout.strip().splitlines()

    assert Path(laeufe) == tmp_path
    assert Path(sweeps) == tmp_path / "sweeps"
