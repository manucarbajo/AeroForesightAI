"""Erstellt eine einfache Graph-Definition (JSON) mit den Nodes aus der Simulation.

Aufruf:
    python create_graph.py

Erzeugt `graph.json` im selben Ordner.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

GRAPH = {
    "nodes": [
        {"id": "orchestrator", "label": "Orchestrator"},
        {"id": "consumer", "label": "Consumer"},
        {"id": "provider", "label": "Provider"},
        {"id": "regulator", "label": "Regulator"},
        {"id": "market", "label": "Market"},
        {"id": "environment", "label": "Environment"},
    ],
    "edges": [
        {"from": "orchestrator", "to": "consumer"},
        {"from": "consumer", "to": "provider"},
        {"from": "provider", "to": "regulator"},
        {"from": "regulator", "to": "market"},
        {"from": "market", "to": "environment"},
    ],
    "meta": {
        "description": "Simple simulation flow: Orchestrator -> Consumer -> Provider -> Regulator -> Market -> Environment",
        "generated_by": "create_graph.py",
    },
}

OUT = ROOT / "graph.json"
with OUT.open("w", encoding="utf-8") as f:
    json.dump(GRAPH, f, indent=2, ensure_ascii=False)

print(f"Wrote {OUT}")
