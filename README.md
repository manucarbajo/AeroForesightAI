# AeroForesight AI

Hybride Multi-Agenten-Simulationsplattform für strategische Zukunftsplanung im europäischen Luftverkehr. Deterministische Massensimulation (Logit-Modelle, CIB-Konsistenzfilter nach Weimer-Jehle) liefert die Zahlen, generative KI liefert die narrative Ausdeutung — reproduzierbare Zukunftskorridore statt Glaskugel.

**Kernprinzip:** Zahlen kommen aus Python (`tick_mechanics`, `price_history`, Population) — LLM-Agenten liefern qualitative Narrative und Events. Der **State Explorer** antwortet ausschließlich aus diesen Run-Daten.

Drei Akteure (Consumer, Provider, Regulator) interagieren über einen tick-basierten LangGraph-Zustandsgraphen; jeder Lauf erzeugt automatisch ein Tripleset aus Trendfortsetzung, Strukturwende und Krisenkonflikt.

## Setup

Immer in einem venv arbeiten, und zwar in `.venv` im Repo-Wurzelverzeichnis — `.claude/launch.json` startet das Dashboard über genau diesen Pfad:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Alle weiteren Befehle in dieser Datei setzen ein aktiviertes venv voraus.

Für Formatierung/Linting vor jedem Commit:

```powershell
black .
ruff check --fix .
```

## Schnellstart

### Batch-Lauf (CLI)

```powershell
python src/run_simulation.py --mock-llm --rounds 10 --quiet
python src/run_simulation.py --rounds 30 --model llama3.2 --temperature 0.7
```

Outputs landen unter `outputs/<run_id>/` (z. B. `outputs/run_20260614T112808Z/`). Checkpoints: `outputs/<run_id>/checkpoints/<run_id>/tick_0005.json`, …

### Dashboard

Web-Oberfläche zum Konfigurieren von Läufen, Ansehen von Ergebnissen und **Abfrage per Chat** — liegt bewusst getrennt unter `dashboard/`:

```powershell
python -m dashboard.web.app --port 8511
```

Browser: `http://localhost:8511` — dort steht die **Landingpage**, der Login-Button
führt ins Dashboard unter `/app/`.

Gebaut mit Plotly Dash. Landingpage und Dashboard teilen sich Server und
Design-Tokens. Die abgelöste Streamlit-Oberfläche liegt zum Vergleich unter
`dashboard/legacy_streamlit/` und wird nach der Abnahme entfernt.

Details: [`dashboard/README.md`](dashboard/README.md)

### State Explorer (CLI)

Grounded Q&A über abgeschlossene Runs — keine erfundenen Zahlen:

```powershell
python -m src.reporting.state_explorer --run-id run_20260614T112808Z --tick 15 --question "Warum fiel booking?"
python -m src.reporting.state_explorer --run-id run_20260614T112808Z   # interaktiv
python -m src.reporting.state_explorer --run-id run_20260614T112808Z --mock-llm --question "Test"
```

Kontext: `tick_mechanics.json`, `price_history.json`, `event_log.json`, optional Checkpoints. Gleiche Logik im Dashboard-Tab **Abfrage**.

### Szenario-Sweeps

Vier Foresight-Presets deterministisch vergleichen:

```powershell
python -m src.orchestration.scenario_sweeps
python -m src.orchestration.scenario_sweeps --sweep transformation_conflict
python -m src.orchestration.scenario_sweeps --ticks 10000 --quiet
```

Outputs: `outputs/sweeps/sweep_summary.json`, `scenario_scores.json`. Details: [`docs/scenario_runs.md`](docs/scenario_runs.md)

### LangGraph Studio (interaktiv)

```powershell
python src/run_simulation.py --studio
```

Weitere Hinweise: [`langgraph_studio/README.langgraph.md`](langgraph_studio/README.langgraph.md)

## Umgebung (.env) einrichten

Die CLI lädt beim Start automatisch `langgraph_studio/.env` (siehe `src/llm/studio_helpers.load_env`). Diese Datei ist **gitignored** — Secrets gehören nicht ins Repository. Vorlage: `langgraph_studio/.env.example` kopieren und anpassen.

### Schritt 1: `.env` anlegen

```powershell
cp langgraph_studio/.env.example langgraph_studio/.env
```

Minimalbeispiel für Ollama:

```
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
| **Mock ohne Ollama** | Batch mit `--mock-llm`; Studio und Dashboard nutzen den Mock, wenn keine Ollama-Variablen gesetzt sind |
| **HTTP-LLM** | `LLAMA_HTTP_URL=http://…` |
| **Transformers lokal** | `LLAMA_TRANSFORMERS_MODEL=…` |

Backend-Auswahl in Code: `src/llm/studio_helpers.get_llm()` (Priorität: Ollama → HTTP → Transformers → Mock).

`--mock-llm` geht seit P0.1 **an dieser Auswahl vorbei** und liefert immer das
Mock-Backend. Vorher hing der Schalter an der Umgebung: war `OLLAMA_MODEL`
gesetzt, versuchte auch ein „Mock"-Lauf, Ollama zu erreichen. Fällt ein echtes
Backend aus, wird das jetzt gemeldet und im Lauf festgehalten, statt still durch
eine erfundene Antwort ersetzt zu werden — siehe
[Fehlerbilder](docs/handbuch/fehlerbilder.md).

### Schritt 3: LangSmith (optional)

```
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=<dein-key>
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Tracing abschalten: `LANGCHAIN_TRACING_V2=false`.

### Schritt 4: Prüfen

```powershell
python src/run_simulation.py --mock-llm --rounds 1 --quiet
python -m dashboard.web.app --port 8511
python src/run_simulation.py --studio
```

## Deployment

Zielumgebung: Hetzner Cloud Server mit lokal laufendem Ollama. `Dockerfile` und `docker-compose.yml` sind ein Ausgangspunkt (Dashboard + Ollama als Services) — noch nicht produktionsfertig verkabelt (kein TLS/Reverse Proxy, keine Persistenzstrategie für `outputs/`).

## Projektstruktur

`src/` ist nach fachlichen Paketen sortiert, nicht nach technischem Typ. Details zu jedem Paket: [CLAUDE.md](CLAUDE.md#architektur-map).

```text
├── configs/                        # simulation_config, properties, agents, sweeps
├── dashboard/                       # Präsentations-UI
│   ├── config_catalog.py            # ConfigDraft, Presets, Config-Persistenz
│   ├── run_launcher.py              # Lauf starten/orchestrieren
│   ├── run_browser.py               # Run-Liste, Artefakte laden
│   ├── consistency_report.py        # Konsistenz-Checks
│   ├── web/                         # Plotly-Dash-Oberfläche (aktiv)
│   ├── legacy_streamlit/            # abgelöste Streamlit-UI (nur Vergleich)
│   └── README.md
├── docs/                            # Technische Doku (CIB-Methodik, Agent-Profile, Workflow)
│   └── research/                    # Fachliteratur, Studien
├── langgraph_studio/                # Studio (.env.example, langgraph.json)
├── src/
│   ├── run_simulation.py            # CLI: Batch, Resume, --studio
│   ├── config_loader.py / validation.py
│   ├── agents/                      # Agent-Node, Orchestrator, Scheduler, Redebedarf-Logik
│   ├── market/                      # Preis-/Kosten-/Nachfrage-Mathematik, Market-Node
│   ├── population/                  # Bevölkerungs-Sampling, Buchungs-Logit-Modell
│   ├── cib/                         # CIB-Konsistenzbewertung + Szenario-Narrative
│   ├── orchestration/                # Tick-Loop, LangGraph-Wiring, Checkpointing, Sweeps
│   ├── reporting/                   # output_writer/, run_scenario_generator/, figure_generator/, protocol_generator.py, state_explorer.py
│   ├── llm/                          # LLM-Backend-Auswahl, Ollama-Client
│   ├── models/                       # Pydantic-Datenmodelle (State, Events, Agenten, …)
│   ├── prompts/                      # Prompt-Templates pro Agent
│   └── legacy/                       # Abgelöste Komponenten (z. B. CIBExtractorNode)
├── tests/
└── outputs/<run_id>/                # Laufzeit-Artefakte (gitignored)
    ├── final_narrative.md           # Lesbarer Simulationsbericht
    ├── tick_mechanics.json          # Ground Truth pro Tick
    ├── event_log.json               # inkl. [delta:…]-Events
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
| `run_scenario.md` / `run_scenario.json` | **Exploratives Szenario**: LLM wählt 3 CIB-Kandidaten, schreibt Narrativ |
| `tick_mechanics.json` | **Ground Truth** pro Tick: Booking, Preis vor/nach Feedback, Shocks |
| `event_log.json` | Agenten-Events + Python-Deltas (`[delta:…]`, source=system/provider/market) |
| `price_history.json` | Preis, demand_level, booking_rate pro Tick |
| `protocol.md` / `.json` | Vollständiges Protokoll |
| `timeseries/*.csv` | Properties, Population, Faktoren F1–F7 |
| `figures/` | 6 PNGs + `manifest.json` (pro Run, siehe unten) |
| `checkpoints/` | State pro Tick (Resume + Explorer) |
| `run_metadata.json` | Ticks, Modell, Degradations-Marker — **und die Herkunft des Laufs**: `seed`, `compute_mode`, `config_fingerprint`, `code_version` |
| `llm_incidents.json` | Nur bei Ausfällen: Tick, Aufrufer, Fehler |

**Einen Lauf nachstellen:** `run_metadata.json` sagt, mit welchem Seed und in
welchem Rechenmodus gerechnet wurde — der Seed steht auch dann dort, wenn die
Konfiguration keinen nennt, dann als der benutzte Standardwert. Der
`config_fingerprint` beschreibt die tatsächlich benutzte Konfiguration, beim
Start des Laufs genommen — nicht die Dateien, die gerade in `configs/` liegen,
denn ein Lauf aus dem Dashboard arbeitet mit einem Entwurf. Zwei Läufe mit
gleichem Fingerabdruck und gleichem Seed sind derselbe Lauf.

**Pipeline pro Tick:** Faktoren → Agenten (Provider/Regulator) → Booking (Referenzpreis = Vortick-Marktpreis) → Consumer → Markt-Feedback (finaler Ticketpreis) → Delta-Events → Export.

## CLI (`run_simulation.py`)

| Option | Beschreibung |
| --- | --- |
| `--studio` | LangGraph Studio starten statt Batch-Lauf |
| `--rounds N` | Max. Ticks überschreiben |
| `--run-id ID` | Output-Verzeichnis `outputs/<run_id>/` |
| `--mock-llm` | Mock-LLM ohne Ollama, unabhängig von den Umgebungsvariablen |
| `--deterministic-only` | Ohne Agenten-LLM (reine Python-Pipeline) |
| `--resume ID/Pfad` | Von Checkpoint fortsetzen |
| `--checkpoint-interval N` | Checkpoint alle N Ticks (Default: 5) |
| `--no-market` | MarketNode deaktivieren |
| `--runs N` | Mehrere unabhängige Läufe (Batch unter `outputs/batch_<timestamp>/`) |

### Figures

**Pro Run** (Hauptweg): `outputs/<run_id>/figures/` — 6 PNGs + `manifest.json`

- Automatisch im Dashboard (Checkbox «Figures nach Lauf erzeugen», Standard: an)
- Oder manuell: `python -m src.reporting.figure_generator.cli --run-only <run_id>`
- Im Dashboard: Tab **Figures** unter «Ergebnisse ansehen»

Workflow und Sweep-Läufe: [`docs/scenario_runs.md`](docs/scenario_runs.md)

Sweep-Runs liegen unter `outputs/sweeps/sweep_<preset>/` mit derselben Struktur.

## Agent-Profile

Informationsgrenzen pro Agent (`observes`, `may_propose`, `must_not_output`, `depends_on`):

- Config: `configs/agent_profiles.json`
- Doku: [`docs/agent_profiles.md`](docs/agent_profiles.md)

Regulator darf F2/F6 vorschlagen (Python-validiert); Provider/Consumer nur Events.

## Emergenz

Nicht-triviale Verläufe entstehen aus **gekoppelten Python-Mechanismen** — nicht aus freier LLM-Interpretation:

- Property-Shocks (CO₂, SAF) → Kosten → Booking → Markt-Feedback
- `factor_rules` (F1–F7) → Population-`shift_rules` → Segmentreaktionen
- Szenario-Unterschiede über Sweeps (`business_as_usual` … `transformation_conflict`)

CIB als **Referenz** (`cib_frozen.json`), Lauf-Dynamik über Regeln: [`docs/cib_rationale.md`](docs/cib_rationale.md)

## Zeitmodell

Ein **Tick ist ein Tick**, keine Kalenderzuordnung (keine Quartale/Jahre in Config, Checkpoints oder Summaries). Die Simulationsuhr nutzt `current_tick` / `max_ticks`; in Outputs und Doku wird neutral „Tick N" verwendet.

## System-Properties

Preis, Steuer, SAF und Makro-Nachfrage werden **deterministisch** in `src/market/simulation_functions.py` berechnet — nicht vom LLM und nicht aus Event-Text geparst.

Konfiguration: `configs/properties.json` — `system_properties` mit `baseline` und `rules` (`set`, `ramp`) oder `step_function`.

| Parameter | Bedeutung |
| --- | --- |
| `carbon_tax_level` | CO₂-Steuer (EUR/t) |
| `fuel_price_change` | Treibstoffpreis-Trend (Dezimalbruch/Tick) |
| `oil_price_index` | Ölpreis-Index (1.0 = Basisjahr) |
| `saf_mandate_share` | SAF-Pflichtanteil (0–1) |
| `efuel_subsidy` | E-Fuel-Subvention (0–1) |
| `demand_growth_rate` | Nachfragewachstum (Dezimalbruch/Tick) → `demand_level` |
| `income_index` | Einkommensindex |

Pro Tick im Output:

- **`demand_level`** — Makro-Nachfrage-Index aus `properties.json`
- **`booking_rate`** — gebuchte Anteile aus Population-Sampler

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
pytest
```

Relevante Suites u. a. `test_state_explorer.py`, `test_dashboard_service.py`, `test_income_dynamics.py`, `test_market_feedback.py`.
