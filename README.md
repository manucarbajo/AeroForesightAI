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

Ein **Tick ist ein Tick**, keine Kalenderzuordnung (keine Quartale/Jahre in Config, Checkpoints oder Summaries). Die Simulationsuhr nutzt `current_tick` / `max_ticks`; in Outputs und Doku wird neutral „Tick N“ verwendet.

## Policy-Schedule (M2)

Preis, Steuer, SAF und Makro-Nachfrage werden **deterministisch** in `src/simulation_functions.py` berechnet — nicht vom LLM und nicht aus Event-Text geparst.

Konfiguration: `configs/simulation_config.json`:

- **`scenario_parameters`**: Default-Werte der sechs Parameter (z. B. `fuel_price_change: 0.02` = 2 %/Tick als Dezimalbruch)
- **`policy_schedule`**: zeitgesteuerte Overrides ab Tick N (`{ "tick": 15, "parameter": "carbon_tax_level", "value": 120.0 }`)

| Parameter | Bedeutung |
| --- | --- |
| `carbon_tax_level` | CO₂-Steuer (EUR/t) |
| `fuel_price_change` | Treibstoffpreis-Trend (Dezimalbruch/Tick) |
| `oil_price_index` | Ölpreis-Index (1.0 = Basisjahr) |
| `saf_mandate_share` | SAF-Pflichtanteil (0–1) |
| `efuel_subsidy` | E-Fuel-Subvention (0–1) |
| `demand_growth_rate` | Nachfragewachstum (Dezimalbruch/Tick) → `demand_level` |

Pro Tick im Output:

- **`demand_level`** — Makro-Nachfrage-Index aus `policy_schedule` (M2)
- **`booking_rate`** — gebuchte Anteile aus Population-Sampler (M3, optional)

### Policy-Shocks testen

**Automatisiert (empfohlen):**

```powershell
python -m pytest tests/test_policy_schedule.py -v
```

**Manuell — Mock-Lauf mit Demo-Shocks** (CO₂ ab Tick 1/15/30, SAF ab Tick 8/16):

```powershell
python src/run_simulation.py --mock-llm --rounds 8 --quiet
```

Danach im Output-Verzeichnis prüfen:

- `outputs/<run_id>/price_history.json` — `price`, `demand_level`, `booking_rate` pro Tick
- `outputs/<run_id>/protocol.md` — pro Tick Zeile **Markt:** mit `price`, `demand_level`, `booking_rate`
- `outputs/<run_id>/protocol.json` — Feld `market` je Runde + `policy_schedule`

Eigene Shocks: `configs/simulation_config.json` → `policy_schedule` anpassen, dann erneut laufen lassen.

## Meilensteine

Siehe `docs/challenge4/projectplan.md`.
