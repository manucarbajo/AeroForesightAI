# Technology Lab – Challenge 4

Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr. Challenge 4 fokussiert auf deterministische Kernlogik, fixe CIB-Matrix, Tick-basiertes Zeitmodell und eine einheitliche Pipeline.

**Kernprinzip:** Zahlen kommen aus Python (`tick_mechanics`, `price_history`, Population) — LLM-Agenten liefern qualitative Narrative und Events. Der **State Explorer** (M9) antwortet nur aus diesen Run-Daten.

**Dokumentation C4:** [`docs/challenge4/challenge4_report.md`](docs/challenge4/challenge4_report.md) · [Projektplan](docs/challenge4/projectplan.md) · [Traceability C1–C4](docs/challenge4/traceability_c1_c4.md)

## Schnellstart

### Batch-Lauf (CLI)

```powershell
pip install -r requirements.txt
python src/run_simulation.py --mock-llm --rounds 10 --quiet
python src/run_simulation.py --rounds 30 --model llama3.2 --temperature 0.7
```

Outputs landen unter `outputs/<run_id>/` (z. B. `outputs/run_20260614T112808Z/`). Checkpoints: `outputs/<run_id>/checkpoints/<run_id>/tick_0005.json`, …

### Präsentations-Dashboard (M9 UI)

Web-Oberfläche zum Konfigurieren von Läufen, Ansehen von Ergebnissen und **Abfrage per Chat** — liegt bewusst getrennt unter `dashboard/`:

```powershell
python -m pip install streamlit
.\dashboard\start.ps1
```

Alternativ:

```powershell
python -m streamlit run dashboard/app.py
```

Browser: `http://localhost:8501`

> Unter Windows oft **`python -m streamlit`** statt `streamlit` direkt (Scripts-Ordner nicht im PATH).

Details: [`dashboard/README.md`](dashboard/README.md)

### State Explorer (CLI)

Grounded Q&A über abgeschlossene Runs — keine erfundenen Zahlen:

```powershell
python -m src.state_explorer --run-id run_20260614T112808Z --tick 15 --question "Warum fiel booking?"
python -m src.state_explorer --run-id run_20260614T112808Z   # interaktiv
python -m src.state_explorer --run-id run_20260614T112808Z --mock-llm --question "Test"
```

Kontext: `tick_mechanics.json`, `price_history.json`, `event_log.json`, optional Checkpoints. Gleiche Logik im Dashboard-Tab **Abfrage**.

### Szenario-Sweeps (M8)

Vier Foresight-Presets deterministisch vergleichen:

```powershell
python -m src.scenario_sweeps
python -m src.scenario_sweeps --sweep transformation_conflict
python -m src.scenario_sweeps --ticks 10000 --quiet
```

Outputs: `outputs/sweeps/sweep_summary.json`, `scenario_scores.json`. Details: [`docs/challenge4/scenario_runs.md`](docs/challenge4/scenario_runs.md)

### LangGraph Studio (interaktiv)

```powershell
python src/run_simulation.py --studio
```

Weitere Hinweise: [`langgraph_studio/README.langgraph.md`](langgraph_studio/README.langgraph.md)

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
| **Mock ohne Ollama** | Keine Ollama-Variablen setzen; Batch mit `--mock-llm`, Studio/Dashboard nutzen dann Mock-LLM |
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

# Dashboard (Browser)
python -m streamlit run dashboard/app.py

# Studio (Browser-URL erscheint in der Konsole)
python src/run_simulation.py --studio
```

## Projektstruktur

```text
Technology-Lab/
├── configs/                       # simulation_config, properties, agents, sweeps
├── dashboard/                     # Präsentations-UI (Streamlit, M9)
│   ├── app.py                     # Einstieg: Simulation starten, Ergebnisse ansehen
│   ├── service.py                 # Run-Liste, Lauf starten, Artefakte laden
│   ├── start.ps1                  # Windows-Starter
│   └── README.md
├── docs/challenge4/               # Projektplan, Report, Traceability, Profile
│   ├── challenge4_report.md       # Abschlussbericht C4 (M11)
│   ├── traceability_c1_c4.md
│   ├── agent_profiles.md
│   ├── cib_rationale.md
│   └── scenario_runs.md
├── langgraph_studio/              # Studio (.env, langgraph.json)
├── src/
│   ├── run_simulation.py          # CLI: Batch, Resume, --studio
│   ├── simulation_runner.py       # Orchestrierung + Checkpoints
│   ├── state_explorer.py          # Grounded Q&A (M9)
│   ├── event_deltas.py            # Delta-Events aus Python (M9)
│   ├── scenario_sweeps.py         # Szenario-Sweeps (M8)
│   ├── figure_generator.py        # Figures global + pro Run (M10)
│   ├── output_writer.py           # final_narrative, tick_mechanics, …
│   ├── legacy/                    # Challenge 2/3 Legacy (CIBExtractorNode)
│   └── nodes/                     # Agent, Market, Environment, …
├── tests/
└── outputs/<run_id>/              # Laufzeit-Artefakte (gitignored)
    ├── final_narrative.md         # Lesbarer Simulationsbericht
    ├── tick_mechanics.json        # Ground Truth pro Tick (M9)
    ├── event_log.json             # inkl. [delta:…]-Events
    ├── price_history.json
    ├── run_metadata.json
    ├── checkpoints/
    └── timeseries/*.csv
```

## Run-Artefakte

Nach jedem Lauf unter `outputs/<run_id>/`:

| Datei | Inhalt |
| --- | --- |
| `final_narrative.md` | Lesbarer Bericht (Kennzahlen, Segment-Buchung, Agenten) |
| `tick_mechanics.json` | **Ground Truth** pro Tick: Booking, Preis vor/nach Feedback, Shocks |
| `event_log.json` | Agenten-Events + Python-Deltas (`[delta:…]`, source=system/provider/market) |
| `price_history.json` | Preis, demand_level, booking_rate pro Tick |
| `protocol.md` / `.json` | Vollständiges Protokoll |
| `timeseries/*.csv` | Properties, Population, Faktoren |
| `checkpoints/` | State pro Tick (Resume + Explorer) |

**Pipeline pro Tick:** Faktoren → Agenten (Provider/Regulator) → Booking (Referenzpreis = Vortick-Marktpreis) → Consumer → Markt-Feedback (finaler Ticketpreis) → Delta-Events → Export.

## CLI (`run_simulation.py`)

| Option | Beschreibung |
| --- | --- |
| `--studio` | LangGraph Studio starten statt Batch-Lauf |
| `--rounds N` | Max. Ticks überschreiben |
| `--run-id ID` | Output-Verzeichnis `outputs/<run_id>/` |
| `--mock-llm` | Mock-LLM ohne Ollama |
| `--deterministic-only` | Ohne Agenten-LLM (reine Python-Pipeline) |
| `--resume ID/Pfad` | Von Checkpoint fortsetzen |
| `--checkpoint-interval N` | Checkpoint alle N Ticks (Default: 5) |
| `--no-market` | MarketNode deaktivieren |
| `--runs N` | Mehrere unabhängige Läufe (Batch unter `outputs/batch_<timestamp>/`) |

### Figures (M10)

Zwei Ebenen:

- **Global** (Foresight-Szenario-Vergleich): [`docs/challenge4/scenario_runs.md`](docs/challenge4/scenario_runs.md) — `python -m src.figure_generator`
- **Pro Run** (nach Simulation): `outputs/<run_id>/figures/` — automatisch im Dashboard (Checkbox «Figures nach Lauf erzeugen») oder:

```powershell
python -m src.figure_generator --run-only run_20260614T112808Z
```

Im Dashboard: Tab **Figures** unter «Ergebnisse ansehen».

## Agent-Profile (M7)

Informationsgrenzen pro Agent (`observes`, `may_propose`, `must_not_output`, `depends_on`):

- Config: `configs/agent_profiles.json`
- Doku: [`docs/challenge4/agent_profiles.md`](docs/challenge4/agent_profiles.md)

Regulator darf F2/F6 vorschlagen (Python-validiert); Provider/Consumer nur Events.

## Emergenz

Nicht-triviale Verläufe entstehen aus **gekoppelten Python-Mechanismen** — nicht aus freier LLM-Interpretation:

- Property-Shocks (CO₂, SAF) → Kosten → Booking → Markt-Feedback
- `factor_rules` (F1–F7) → Population-`shift_rules` → Segmentreaktionen
- Szenario-Unterschiede über Sweeps (`business_as_usual` … `transformation_conflict`)

CIB als **Referenz** (`cib_frozen.json`), Lauf-Dynamik über Regeln: [`docs/challenge4/cib_rationale.md`](docs/challenge4/cib_rationale.md)

## Dashboard

| Bereich | Funktion |
| --- | --- |
| **Simulation starten** | Szenario, Parameter, Lauf mit Live-Fortschritt, optional Figures |
| **Ergebnisse ansehen** | Übersicht, **Figures**, Bericht, Abfrage, Dateien |

## Zeitmodell

Ein **Tick ist ein Tick**, keine Kalenderzuordnung (keine Quartale/Jahre in Config, Checkpoints oder Summaries). Die Simulationsuhr nutzt `current_tick` / `max_ticks`; in Outputs und Doku wird neutral „Tick N“ verwendet.

## System-Properties (M2)

Preis, Steuer, SAF und Makro-Nachfrage werden **deterministisch** in `src/simulation_functions.py` berechnet — nicht vom LLM und nicht aus Event-Text geparst.

Konfiguration: `configs/properties.json` — `system_properties` mit `baseline` und `rules` (`set`, `ramp`) oder `step_function`.

| Parameter | Bedeutung |
| --- | --- |
| `carbon_tax_level` | CO₂-Steuer (EUR/t) |
| `fuel_price_change` | Treibstoffpreis-Trend (Dezimalbruch/Tick) |
| `oil_price_index` | Ölpreis-Index (1.0 = Basisjahr) |
| `saf_mandate_share` | SAF-Pflichtanteil (0–1) |
| `efuel_subsidy` | E-Fuel-Subvention (0–1) |
| `demand_growth_rate` | Nachfragewachstum (Dezimalbruch/Tick) → `demand_level` |
| `income_index` | Einkommensindex (M6) |

Pro Tick im Output:

- **`demand_level`** — Makro-Nachfrage-Index aus `properties.json` (M2)
- **`booking_rate`** — gebuchte Anteile aus Population-Sampler (M3)

### Policy-Shocks testen

**Automatisiert (empfohlen):**

```powershell
python -m pytest tests/test_policy_schedule.py -v
```

**Manuell — Mock-Lauf mit Demo-Shocks** (CO₂ ab Tick 1/15/30, SAF ab Tick 8/16):

```powershell
python src/run_simulation.py --mock-llm --rounds 8 --quiet
```

Danach prüfen — per Dashboard, Explorer oder direkt im Ordner:

- `outputs/<run_id>/tick_mechanics.json` — Ground Truth pro Tick
- `outputs/<run_id>/final_narrative.md` — lesbarer Bericht
- `outputs/<run_id>/price_history.json` — Preis, demand_level, booking_rate
- `outputs/<run_id>/event_log.json` — inkl. `[delta:…]`-Einträge
- `outputs/<run_id>/timeseries/properties.csv` — System-Properties pro Tick

Eigene Shocks: `configs/properties.json` → `rules` anpassen (z. B. CO₂ ab Tick 15), dann erneut laufen lassen.

## Tests

```powershell
python -m pytest
```

Relevante Suites u. a. `test_state_explorer.py`, `test_dashboard_service.py`, `test_income_dynamics.py`, `test_market_feedback.py`.

## Meilensteine

Aktueller Stand und Abnahmekriterien: [`docs/challenge4/projectplan.md`](docs/challenge4/projectplan.md). Abschlussbericht: [`docs/challenge4/challenge4_report.md`](docs/challenge4/challenge4_report.md).
