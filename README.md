# Technology Lab – Challenge 4

Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr. Challenge 4 fokussiert auf deterministische Kernlogik, fixe CIB-Matrix, Tick-basiertes Zeitmodell und eine einheitliche Pipeline.

## Schnellstart

**Batch-Lauf (Outputs, Protokoll, Checkpoints):**

```bash
pip install -r requirements.txt
python src/run_simulation.py --mock-llm --rounds 2 --quiet
```

**LangGraph Studio (interaktiv, gleiche Pipeline):**

```bash
python src/run_simulation.py --studio
```

Outputs landen unter `outputs/<run_id>/` (z. B. `outputs/run_20260603T143022Z/`).

## Projektstruktur

```text
Technology-Lab/
├── configs/
├── langgraph_studio/              # LangGraph Studio (.env, langgraph.json)
├── src/
│   ├── run_simulation.py          # CLI: Batch oder --studio
│   ├── simulation_runner.py       # Orchestrierung
│   ├── langgraph_workflow.py      # Studio-Graph (gleiche Pipeline)
│   └── ...
├── tests/
└── outputs/<run_id>/              # Laufzeit-Artefakte (gitignored)
```

## CLI

| Option | Beschreibung |
| --- | --- |
| `--studio` | LangGraph Studio starten statt Batch-Lauf |
| `--rounds N` | Max. Ticks überschreiben |
| `--run-id ID` | Output-Verzeichnis `outputs/<run_id>/` |
| `--mock-llm` | Mock-LLM ohne Ollama |
| `--no-market` | MarketNode deaktivieren |
| `--runs N` | Mehrere unabhängige Läufe (Batch unter `outputs/batch_<timestamp>/`) |

Checkpoints: `outputs/<run_id>/checkpoints/`  
Studio-Konfiguration: `langgraph_studio/.env` (wird von der CLI automatisch geladen)

## Meilensteine

Siehe `docs/challenge4/projectplan.md`.
