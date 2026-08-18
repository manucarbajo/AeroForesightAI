# AeroForesight AI

Hybride Multi-Agenten-Simulationsplattform für strategische Zukunftsplanung im europäischen Luftverkehr. Deterministische Massensimulation (Logit-Modelle für Mikro-Kaufentscheidungen, CIB-Konsistenzfilter nach Weimer-Jehle) liefert die Zahlen, generative KI liefert ausschließlich die narrative Ausdeutung. Drei Akteure — Consumer, Provider, Regulator — interagieren über einen tick-basierten LangGraph-Zustandsgraphen; jeder Lauf erzeugt ein Tripleset aus Trendfortsetzung, Strukturwende und Krisenkonflikt.

Details und Quickstart: [README.md](README.md).

## Architektur-Map

- `src/` — Kern-Engine (Paketname bewusst `src`, nicht umbenennen)
  - `nodes/` — LangGraph-Knoten (Agent, Market, Environment, Orchestrator, Scheduler, …)
  - `models/` — Pydantic-Datenmodelle (State, Events, Agenten, Population, Properties, CIB)
  - `prompts/` — Prompt-Templates pro Agent (`consumer.md`, `provider.md`, `regulator.md`)
  - `legacy/` — abgelöste Komponenten (z. B. `CIBExtractorNode`), nicht Teil der aktiven Pipeline
  - übrige Module: Orchestrierung, Checkpointing, Output-Writer, Figures, State Explorer, Szenario-Sweeps
- `dashboard/` — Streamlit-UI (Simulation starten, Ergebnisse ansehen, Chat-Abfrage)
- `langgraph_studio/` — interaktive Graph-Entwicklung (LangGraph Studio)
- `configs/` — Simulationskonfiguration (`simulation_config.json`, `properties.json`, `agents.json`, `agent_profiles.json`, `cib_frozen.json`, `sweeps/`)
- `tests/` — pytest-Suite (~270 Tests)
- `docs/` — technische Doku (CIB-Methodik, Agent-Profile, Szenario-Workflow); `docs/research/` — Fachliteratur

## Domain-Glossar

- **Tick** — kleinste Simulationseinheit, hat **keine** Kalenderbedeutung (kein Quartal/Jahr). Uhr: `current_tick` / `max_ticks`.
- **CIB-Matrix** (Cross-Impact-Balance, Weimer-Jehle) — eingefrorene Referenzmatrix (`configs/cib_frozen.json`), bewertet die interne Konsistenz von Faktor-Konstellationen. Details: [`docs/cib_role.md`](docs/cib_role.md), [`docs/cib_rationale.md`](docs/cib_rationale.md).
- **Faktoren F1–F7** — Zustandsvariablen des soziotechnischen Systems (Mobilitätsnachfrage, Regulierung, Technologie/SAF, Wirtschaft, Alternativen, Gesellschaft, Marktstruktur), je zwei Zustände (z. B. F1.1/F1.2).
- **Logit-Modell** — deterministisches mikroökonomisches Modell für Kaufentscheidungen der simulierten Population.
- **Agent-Profile** (Consumer, Provider, Regulator) — informationsbeschränkte LLM-Agenten; erlaubte Beobachtungen/Outputs pro Rolle in `configs/agent_profiles.json`. Details: [`docs/agent_profiles.md`](docs/agent_profiles.md).
- **State Explorer** — grounded Q&A ausschließlich über abgeschlossene Run-Daten (`tick_mechanics.json`, `price_history.json`, `event_log.json`) — keine erfundenen Zahlen.

## Harte Architektur-Invarianten

Diese Prinzipien sind der eigentliche USP des Produkts (Schutz vor LLM-Halluzination) und dürfen nie aufgeweicht werden:

1. **Zahlen kommen immer aus Python, nie vom LLM.** Preise, Booking-Raten, Faktorzustände etc. werden deterministisch berechnet (`simulation_functions.py`, `market_rules.py`, `factor_dynamics.py`). LLM-Agenten liefern ausschließlich Narrative/Events, nie Kennzahlen.
2. **Agenten dürfen nur vorschlagen, was ihr Profil erlaubt.** Regulator darf F2/F6 vorschlagen (Python-validiert über `AGENT_FACTOR_PERMISSIONS`), Provider/Consumer nur Events. Nicht ohne Rücksprache erweitern.
3. **Die CIB-Matrix ist bewusst eingefroren** (`"frozen": true`). Sie darf sich nicht aus Simulationsläufen ableiten — sonst wird der Maßstab aus dem Messobjekt gewonnen (zirkulär).
4. **Pydantic-Typisierung an allen Agenten-Grenzen** — jede Cross-Boundary-Datenstruktur ist ein typisiertes Modell in `src/models/`, keine rohen Dicts.
5. **Ein Tick ist ein Tick** — keine Kalender-/Datumssemantik in Configs, Checkpoints oder Outputs einführen.

## Dev-Workflow

```powershell
pip install -e ".[dev]"

pytest                    # volle Test-Suite
ruff check .               # Linting
black --check .            # Formatierung prüfen (black . zum Formatieren)

python -m src.run_simulation --mock-llm --rounds 1 --quiet   # Smoke-Test ohne Ollama
python -m streamlit run dashboard/app.py                      # Dashboard
```

`black` + `ruff` vor jedem Commit laufen lassen (CI in `.github/workflows/tests.yml` prüft beides plus Tests). Bekannte, umgebungsbedingte Testfehler ohne lokalen Ollama: `test_run_single_sweep_short`, `test_sweep_base_price_override_raises_ticket_price`. Ein echter (vorbestehender) Bug: `test_market_rules_resolve_marginal_cost_fraction`.

Import-Reihenfolge in `src/models/__init__.py` ist bewusst nicht alphabetisch (löst einen circular import zwischen `state_models` und `event_models`) — Kommentar dort beachten, nicht von Formattern umsortieren lassen.

## Team

- **Manuel Carbajo** — Workflow-Orchestrierung, LangGraph-Pipelines, Dashboard, Datenanbindung.
- **Haiko Wiedenberg** — mathematische Modellierung, Logit-Stochastik, Pydantic-Guardrails, CIB-Algorithmik.

Bei Änderungen in `src/nodes/`, `src/langgraph_*` oder `dashboard/` eher Manuel, bei `src/models/`, `factor_dynamics.py`, `scenario_consistency.py`, `population_sampler.py` eher Haiko als Reviewer im Kopf haben.

## Deployment-Ziel

Hetzner Cloud Server mit lokal laufendem Ollama (Datenhoheit, keine externen LLM-Calls für sensible B2B-Daten). `Dockerfile`/`docker-compose.yml` sind ein Ausgangspunkt, noch nicht produktionsscharf.

## Bekannte Backlog-Punkte (nicht ungefragt anfassen)

- `output_writer.py` (~1150 Zeilen) und `run_scenario_generator.py` (~1550 Zeilen) sind Refactoring-Kandidaten (zu groß) — größere Umbauten hier vorher absprechen.
- Kein API-Layer für Multi-Tenant-B2B-Nutzung vorhanden.
