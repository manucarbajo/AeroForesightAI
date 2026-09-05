"""Erstellt `graph.json` aus der aktuellen Studio-Graph-Topologie."""

from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

# **Nach dem `sys.path`-Eingriff, nicht davor.** Dieses Skript wird auch aus
# einem fremden Arbeitsverzeichnis gestartet; oben stehend scheitert der Import
# dort mit `ModuleNotFoundError: No module named 'src'`. Beim ersten Anlauf von
# P3.10 ist genau das passiert.
from src.logging_setup import stdio_auf_utf8  # noqa: E402


def build_static_graph() -> dict:
    """Die statische Topologie — aber erst, wenn der echte Graph baut (P3.3).

    **Das `except Exception: pass` hier verschluckte den Fehler, den der Block
    zwei Zeilen darüber absichtlich re-raist.** Ein kaputter Graph-Build endete
    damit in einem geschriebenen `graph.json` und einem `Wrote …` auf stdout:
    ein Erfolg, der keiner war, und eine Datei, die eine Topologie behauptet, die
    so nicht baut. Wer sie danach in Studio öffnet, sucht den Fehler an der
    falschen Stelle.

    **Ein fehlendes `langgraph` ist etwas anderes als ein kaputter Graph**, und
    nur der zweite Fall ist ein Befund. Ohne das Paket lässt sich die statische
    Topologie trotzdem aufschreiben — sie ist eine Beschreibung, keine
    Ausführung.
    """

    try:
        import langgraph_studio.graph as pg  # type: ignore
    except ImportError as exc:
        # Kein Grund abzubrechen: Die Topologie unten steht als Daten da und
        # braucht das Paket nicht. Gesagt wird es trotzdem -- eine Datei, die
        # ohne Gegenprobe entstanden ist, soll das nicht verschweigen.
        print(f"Hinweis: Graph-Modul nicht importierbar ({exc}) — Topologie ungeprüft.")
    else:
        if getattr(pg, "graph", None) is None and callable(getattr(pg, "get_build_error", None)):
            error = pg.get_build_error()
            if error is not None:
                raise error

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
    """Schreibt `graph.json` — oder bricht sichtbar ab (P3.3).

    Der Build-Fehler wird **nicht** gefangen: Er soll den Aufruf mit einem
    Exit-Code ungleich 0 beenden, damit weder eine Datei entsteht noch ein
    `Wrote …` erscheint. Ein Traceback ist hier die richtige Ausgabe — dieses
    Skript ruft niemand versehentlich auf, und wer es ruft, will wissen, *warum*
    der Graph nicht baut.
    """

    out = ROOT / "graph.json"
    payload = build_static_graph()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    raise SystemExit(main())
