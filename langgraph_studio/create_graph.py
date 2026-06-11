"""Erstellt `graph.json` aus der aktuellen Studio-Graph-Topologie."""
from __future__ import annotations

from pathlib import Path
import json
import datetime
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))


def build_static_graph() -> dict:
    try:
        import langgraph_studio.graph as pg  # type: ignore

        if getattr(pg, "graph", None) is None and callable(getattr(pg, "get_build_error", None)):
            error = pg.get_build_error()
            if error is not None:
                raise error
    except Exception:
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
        {"id": "scenario_agent", "label": "Scenario Agent"},
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
        {"from": "environment", "to": "scenario_agent", "condition": "end"},
        {"from": "scenario_agent", "to": "END"},
    ]

    meta = {
        "description": "Studio graph with explicit agent nodes (consumer, provider, regulator).",
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
