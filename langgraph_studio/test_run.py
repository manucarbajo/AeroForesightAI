"""Deprecated wrapper — use ``python src/run_simulation.py --studio`` instead."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Nach dem `sys.path`-Eingriff — siehe `create_graph.py`.
from src.logging_setup import stdio_auf_utf8  # noqa: E402

if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    print("Deprecated: use `python src/run_simulation.py --studio` instead.", file=sys.stderr)
    from src.run_simulation import main

    previous_argv = sys.argv[:]
    try:
        sys.argv = ["run_simulation", "--studio"]
        raise SystemExit(main())
    finally:
        sys.argv = previous_argv
