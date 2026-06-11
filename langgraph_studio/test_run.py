"""Deprecated wrapper — use ``python src/run_simulation.py --studio`` instead."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    print("Deprecated: use `python src/run_simulation.py --studio` instead.", file=sys.stderr)
    from src.run_simulation import main

    previous_argv = sys.argv[:]
    try:
        sys.argv = ["run_simulation", "--studio"]
        raise SystemExit(main())
    finally:
        sys.argv = previous_argv
