# Technology Lab – Challenge 4

Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr. Challenge 4 fokussiert auf deterministische Kernlogik, fixe CIB-Matrix, Tick-basiertes Zeitmodell und eine einheitliche Pipeline.

## Schnellstart

**Batch-Lauf (Outputs, Protokoll, Checkpoints):**

```bash
pip install -r requirements.txt
python src/run_simulation.py --mock-llm --rounds 2 --quiet
python src/run_simulation.py --rounds 3 --runs 2 --model llama3.2 --temperature 0.7
```

**LangGraph Studio (interaktiv, gleiche Pipeline):**

```bash
python src/run_simulation.py --studio
```

Outputs landen unter `outputs/<run_id>/` (z. B. `outputs/run_20260603T143022Z/`). Checkpoints: `outputs/<run_id>/checkpoints/tick_0001.json`, …

## Umgebung (.env) einrichten

Die CLI lädt beim Start automatisch `langgraph_studio/.env` (siehe `src/studio_helpers.load_env`). Diese Datei ist **gitignored** — Secrets gehören nicht ins Repository.

### Schritt 1: `.env` prüfen

Die CLI lädt `langgraph_studio/.env` beim Start automatisch. Wenn die Datei noch nicht existiert, lege sie einfach neu an. Passe sie danach an, wenn du ein anderes Backend, eine andere URL oder eigene Tracing-Werte verwenden willst.

Minimalbeispiel für Ollama:

```powershell
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=<dein-key>
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### Schritt 2: LLM-Backend wählen

| Ziel | Variablen in `.env` |
| --- | --- |
| **Ollama lokal** (Standard) | `OLLAMA_MODEL=llama3.2`, `OLLAMA_BASE_URL=http://127.0.0.1:11434` — Modell vorher starten: `ollama run llama3.2` |
| **Mock ohne Ollama** | Keine Ollama-Variablen setzen; Batch mit `--mock-llm`, Studio nutzt dann `MockLLM` |
| **HTTP-LLM** | `LLAMA_HTTP_URL=http://…` |
| **Transformers lokal** | `LLAMA_TRANSFORMERS_MODEL=…` |

Backend-Auswahl in Code: `src/studio_helpers.get_llm()` (Priorität: Ollama → HTTP → Transformers → Mock).

### Schritt 3: LangSmith (optional)

Für Tracing im Studio:

```
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=<dein-key>
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Tracing abschalten: `LANGCHAIN_TRACING_V2=false` (Default in `.env.example`).

### Schritt 4: Prüfen

```powershell
# Batch mit Mock
python src/run_simulation.py --mock-llm --rounds 1 --quiet

# Studio (Browser-URL erscheint in der Konsole)
python src/run_simulation.py --studio
```

Weitere Studio-Hinweise (404 nach Neustart, Cache löschen): `langgraph_studio/README.langgraph.md`.

## Projektstruktur

```text
Technology-Lab/
├── configs/
├── docs/challenge4/               # Projektplan, Calibration, CIB-Coaching
├── langgraph_studio/              # Studio (.env, langgraph.json, .env.example)
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

## Zeitmodell

Ein **Tick ist ein Tick**, keine Kalenderzuordnung (keine Quartale/Jahre in Config, Checkpoints oder Summaries). Intern heißt das Feld weiterhin `current_tick` (1-basierter Tick-Index); in Outputs und Doku wird neutral „Tick N“ verwendet.

## Meilensteine

Siehe `docs/challenge4/projectplan.md`.
