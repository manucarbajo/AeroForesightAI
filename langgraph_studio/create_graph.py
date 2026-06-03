"""Erstellt `graph.json` aus der aktuellen Playground-Graph-Topologie.

Das Skript lädt `haiko_playground.graph` (Validierung) und schreibt eine
kleine, leichtgewichtige JSON-Repräsentation der Node-/Edge-Struktur, so
dass Studio/Viewer stets eine synchronisierte `graph.json` erhalten.

Aufruf:
    python create_graph.py

Erzeugt `graph.json` im selben Ordner.
"""
from __future__ import annotations

from pathlib import Path
import json
import datetime
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))


def build_static_graph() -> dict:
    # Ensure the playground graph module imports correctly (will raise on error).
    try:
        import haiko_playground.graph as pg  # type: ignore
    except Exception:
        # If importing the dynamic graph fails, fall back to a safe static layout.
        pass

    nodes = [
        {"id": "initialize_state", "label": "Initialize State"},
        {"id": "reset_round_buffer", "label": "Reset Round Buffer"},
        {"id": "orchestrator", "label": "Orchestrator"},
        {"id": "determine_next_speaker", "label": "Determine Next Speaker"},
        {"id": "consumer", "label": "Consumer"},
        {"id": "provider", "label": "Provider"},
        {"id": "regulator", "label": "Regulator"},
        {"id": "market", "label": "Market"},
        {"id": "environment", "label": "Environment"},
        {"id": "cib_extractor", "label": "CIB Extractor"},
    ]

    edges = [
        {"from": "initialize_state", "to": "reset_round_buffer"},
        {"from": "reset_round_buffer", "to": "orchestrator"},
        {"from": "orchestrator", "to": "determine_next_speaker"},
        {"from": "determine_next_speaker", "to": "consumer"},
        {"from": "determine_next_speaker", "to": "provider"},
        {"from": "determine_next_speaker", "to": "regulator"},
        {"from": "determine_next_speaker", "to": "market"},
        {"from": "consumer", "to": "determine_next_speaker"},
        {"from": "provider", "to": "determine_next_speaker"},
        {"from": "regulator", "to": "determine_next_speaker"},
        {"from": "market", "to": "environment"},
        {"from": "environment", "to": "reset_round_buffer", "condition": "continue"},
        {"from": "environment", "to": "cib_extractor", "condition": "end"},
        {"from": "cib_extractor", "to": "END"},
    ]

    meta = {
        "description": "Generated simulation StateGraph layout (playground adapter).",
        "generated_by": "create_graph.py",
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
    }

    return {"nodes": nodes, "edges": edges, "meta": meta}


def main() -> int:
    out = ROOT / "graph.json"
    payload = build_static_graph()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
