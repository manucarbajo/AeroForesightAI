# AeroForesight AI

Hybride Multi-Agenten-Simulationsplattform für strategische Zukunftsplanung im europäischen Luftverkehr. Deterministische Massensimulation (Logit-Modelle für Mikro-Kaufentscheidungen, CIB-Konsistenzfilter nach Weimer-Jehle) liefert die Zahlen, generative KI liefert ausschließlich die narrative Ausdeutung. Drei Akteure — Consumer, Provider, Regulator — interagieren über einen tick-basierten LangGraph-Zustandsgraphen; jeder Lauf erzeugt ein Tripleset aus Trendfortsetzung, Strukturwende und Krisenkonflikt.

Details und Quickstart: [README.md](README.md).

## Architektur-Map

`src/` ist die Kern-Engine (Paketname bewusst `src`, nicht umbenennen), nach fachlichen Paketen sortiert statt nach technischem Typ:

- `src/agents/` — wer spricht wann, in welcher Reihenfolge, mit welchen Rechten (Agent-Node, Orchestrator, Scheduler, Redebedarf-Logik)
- `src/market/` — Preis-/Kosten-/Nachfrage-Mathematik und Faktor-Regeln (`market_rules.py`, `simulation_functions.py`, `property_engine.py`, `factor_dynamics.py`, Market-Node)
- `src/population/` — Bevölkerungs-Sampling und Buchungs-Logit-Modell
- `src/cib/` — CIB-Konsistenzbewertung (`scenario_consistency.py`) plus die darauf aufbauende LLM-Szenario-Narrative-Schicht
- `src/orchestration/` — Tick-Loop, LangGraph-Wiring, Checkpointing, Szenario-Sweeps (`simulation_runner.py`, `langgraph_workflow.py`, `scenario_sweeps.py`, Environment-Node)
- `src/reporting/` — alles, was nach/während eines Laufs geschrieben oder dargestellt wird: `output_writer/`, `run_scenario_generator/`, `figure_generator/` (jeweils eigene Unterpakete), plus `protocol_generator.py`, `state_explorer.py`, `cib_visualizer.py`
- `src/llm/` — LLM-Backend-Auswahl und Ollama-Client
- `src/models/` — Pydantic-Datenmodelle (State, Events, Agenten, Population, Properties, CIB) — bewusst eine gemeinsame Schicht, nicht weiter aufgeteilt (fragile Import-Reihenfolge, siehe unten)
- `src/prompts/` — Prompt-Templates pro Agent (`consumer.md`, `provider.md`, `regulator.md`)
- `src/legacy/` — abgelöste Komponenten (z. B. `CIBExtractorNode`), nicht Teil der aktiven Pipeline
- `src/run_simulation.py`, `src/config_loader.py`, `src/validation.py` — bleiben bewusst Top-Level (CLI-Einstieg bzw. von mehreren Paketen genutzt)

Jedes Paket hat ein `__init__.py`, das die öffentliche API re-exportiert.

- `dashboard/` — Präsentations-UI. Der oberflächenfreie Service-Layer liegt direkt darin (`config_catalog.py`, `run_browser.py`, `run_launcher.py`, `consistency_report.py`) und wird von beiden Oberflächen geteilt:
  - `dashboard/web/` — **aktive** Plotly-Dash-App im Design der Landingpage. `app.py` (Rahmen/Routing), `theme.py` (Design-Tokens + Plotly-Template), `components.py`, `state.py` (`ConfigDraft` ⇄ `dcc.Store`), `runner.py` (Lauf im Hintergrund-Thread), `pages/` (inkl. `docs.py` — Handbuch mit Kapitelregistry und Suche), `views/` (die sieben Run-Tabs), `config_editor/` (die sechs Editor-Tabs, Erklärtexte gebündelt in `glossary.py`)
  - `dashboard/legacy_streamlit/` — abgelöste Streamlit-UI, nur noch zum Vergleich lauffähig; **keine neuen Funktionen dort einbauen**
- `aeroforesight-ai-landing-page/` — statische Landingpage. Wird von der Dash-App selbst ausgeliefert: Landingpage auf `/`, Dashboard auf `/app/` (`dashboard/web/landing_route.py`, Pfade in `dashboard/web/routing.py`). Ihre Design-Tokens (`design/color-tokens.json`) sind die Quelle für das Dashboard-Theme
- `langgraph_studio/` — interaktive Graph-Entwicklung (LangGraph Studio)
- `configs/` — Simulationskonfiguration (`simulation_config.json`, `properties.json`, `agents.json`, `agent_profiles.json`, `cib_frozen.json`, `sweeps/`)
- `tests/` — pytest-Suite (~330 Tests); `test_dashboard_service.py` deckt den Service-Layer ab, `test_web_state.py` die Draft-Serialisierung, `test_web_layout.py` jede Ansicht der Dash-App (auch mit unvollständigen Run-Verzeichnissen)
- `docs/handbuch/` — die geschriebenen Kapitel des Dashboard-Handbuchs (Markdown, vom Dashboard unter `/doku` gerendert); Referenzkapitel entstehen zur Laufzeit aus `configs/`
- `docs/` — technische Doku (CIB-Methodik, Agent-Profile, Szenario-Workflow) und `docs/audit_findings.md` (bekannte Bugs/Inkonsistenzen, bewusst nicht gefixt — bitte durchgehen und priorisieren); `docs/research/` — Fachliteratur

## Domain-Glossar

- **Tick** — kleinste Simulationseinheit, hat **keine** Kalenderbedeutung (kein Quartal/Jahr). Uhr: `current_tick` / `max_ticks`.
- **CIB-Matrix** (Cross-Impact-Balance, Weimer-Jehle) — eingefrorene Referenzmatrix (`configs/cib_frozen.json`), bewertet die interne Konsistenz von Faktor-Konstellationen. Details: [`docs/cib_role.md`](docs/cib_role.md), [`docs/cib_rationale.md`](docs/cib_rationale.md).
- **Faktoren F1–F7** — Zustandsvariablen des soziotechnischen Systems (Mobilitätsnachfrage, Regulierung, Technologie/SAF, Wirtschaft, Alternativen, Gesellschaft, Marktstruktur), je zwei Zustände (z. B. F1.1/F1.2).
- **Logit-Modell** — deterministisches mikroökonomisches Modell für Kaufentscheidungen der simulierten Population.
- **Agent-Profile** (Consumer, Provider, Regulator) — informationsbeschränkte LLM-Agenten; erlaubte Beobachtungen/Outputs pro Rolle in `configs/agent_profiles.json`. Details: [`docs/agent_profiles.md`](docs/agent_profiles.md).
- **State Explorer** — grounded Q&A ausschließlich über abgeschlossene Run-Daten (`tick_mechanics.json`, `price_history.json`, `event_log.json`) — keine erfundenen Zahlen.

## Harte Architektur-Invarianten

Diese Prinzipien sind der eigentliche USP des Produkts (Schutz vor LLM-Halluzination) und dürfen nie aufgeweicht werden:

1. **Zahlen kommen immer aus Python, nie vom LLM.** Preise, Booking-Raten, Faktorzustände etc. werden deterministisch berechnet (`src/market/simulation_functions.py`, `src/market/market_rules.py`, `src/market/factor_dynamics.py`). LLM-Agenten liefern ausschließlich Narrative/Events, nie Kennzahlen.
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
python -m dashboard.web.app --port 8511                       # Landingpage auf /, Dashboard auf /app/
python -m streamlit run dashboard/legacy_streamlit/app_researcher.py --server.port=8512   # Legacy-Vergleich
```

`black` + `ruff` vor jedem Commit laufen lassen (CI in `.github/workflows/tests.yml` prüft beides plus Tests). Bekannte, umgebungsbedingte Testfehler ohne lokalen Ollama: `test_run_single_sweep_short`, `test_sweep_base_price_override_raises_ticket_price`. Ein echter (vorbestehender) Bug: `test_market_rules_resolve_marginal_cost_fraction`.

Import-Reihenfolge in `src/models/__init__.py` ist bewusst nicht alphabetisch (löst einen circular import zwischen `state_models` und `event_models`) — Kommentar dort beachten, nicht von Formattern umsortieren lassen.

## Deployment-Ziel

Hetzner Cloud Server mit lokal laufendem Ollama (Datenhoheit, keine externen LLM-Calls für sensible B2B-Daten). `Dockerfile`/`docker-compose.yml` sind ein Ausgangspunkt, noch nicht produktionsscharf.

## Bekannte Backlog-Punkte (nicht ungefragt anfassen)

- `docs/audit_findings.md` enthält ~30 gefundene Bugs/Inkonsistenzen (u. a. zwei divergierende Ollama-Clients, zwei auseinandergelaufene Rule-Evaluatoren, ein `validate_config`-Stub, der immer `[]` zurückgibt) — bewusst nicht gefixt, Priorisierung steht noch aus.
- Kein API-Layer für Multi-Tenant-B2B-Nutzung vorhanden.
