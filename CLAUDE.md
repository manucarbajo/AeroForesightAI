# AeroForesight AI

Hybride Multi-Agenten-Simulationsplattform für strategische Zukunftsplanung im europäischen Luftverkehr. Deterministische Massensimulation (Logit-Modelle für Mikro-Kaufentscheidungen, CIB-Konsistenzfilter nach Weimer-Jehle) liefert die Zahlen, generative KI liefert ausschließlich die narrative Ausdeutung. Drei Akteure — Consumer, Provider, Regulator — interagieren über einen tick-basierten LangGraph-Zustandsgraphen; jeder Lauf erzeugt ein Tripleset aus Trendfortsetzung, Strukturwende und Krisenkonflikt.

Details und Quickstart: [README.md](README.md). Was als Nächstes ansteht und in welcher Reihenfolge: [docs/projektplan.md](docs/projektplan.md).

## Doku-Pflicht

**Gilt für alle im Team und für jede Claude-Session.** Code ohne mitgezogene Doku gilt als nicht fertig. Ein `UserPromptSubmit`-Hook in [`.claude/settings.json`](.claude/settings.json) blendet diese Regel bei jedem Prompt ein, damit sie niemand überliest.

Im selben Commit mitpflegen:

| Wenn die Änderung … | … dann anpassen |
| --- | --- |
| Paketstruktur, Modulzuschnitt oder Datenfluss ändert | **CLAUDE.md** (Architektur-Map) |
| eine Invariante, Konvention oder ein Dev-Kommando betrifft | **CLAUDE.md** (Invarianten bzw. Dev-Workflow) |
| einen Begriff neu einführt oder seine Bedeutung verschiebt | **CLAUDE.md** (Domain-Glossar) + `docs/handbuch/glossar.md` |
| sichtbares Verhalten von Dashboard oder CLI ändert | passende Kapitel in `docs/handbuch/`, bei CLI zusätzlich `README.md` |
| Config-Felder oder Run-Artefakte ändert | `docs/handbuch/ref-config.md`, `docs/handbuch/ref-ausgaben.md` |
| ein Arbeitspaket aus dem Projektplan abschließt oder verschiebt | **`docs/projektplan.md`** (Stand-Zeile mitziehen) |
| einen Bug aus `docs/audit_findings.md` behebt | Finding dort entfernen, nicht abhaken |
| eine neue Schwachstelle findet, die nicht sofort gefixt wird | Finding in `docs/audit_findings.md` ergänzen |

Zwei Regeln dazu: Was der Code nicht tut, darf die Doku nicht behaupten — lieber die Formulierung abschwächen als eine Aussage stehen lassen, die ein Fachprüfer widerlegt. Und wenn eine Änderung eine dieser Zeilen auslöst, aber die Doku bewusst unverändert bleibt, gehört der Grund in die Commit-Message.

## Architektur-Map

`src/` ist die Kern-Engine (Paketname bewusst `src`, nicht umbenennen), nach fachlichen Paketen sortiert statt nach technischem Typ:

- `src/agents/` — wer spricht wann, in welcher Reihenfolge, mit welchen Rechten (Agent-Node, Orchestrator, Scheduler, Redebedarf-Logik)
- `src/market/` — Preis-/Kosten-/Nachfrage-Mathematik und Faktor-Regeln (`market_rules.py`, `simulation_functions.py`, `property_engine.py`, `factor_dynamics.py`, Market-Node)
- `src/population/` — Bevölkerungs-Sampling und Buchungs-Logit-Modell
- `src/cib/` — CIB-Konsistenzbewertung (`scenario_consistency.py`) plus die darauf aufbauende LLM-Szenario-Narrative-Schicht
- `src/orchestration/` — Tick-Loop, LangGraph-Wiring, Checkpointing, Szenario-Sweeps (`simulation_runner.py`, `langgraph_workflow.py`, `scenario_sweeps.py`, Environment-Node)
- `src/reporting/` — alles, was nach/während eines Laufs geschrieben oder dargestellt wird: `output_writer/`, `run_scenario_generator/`, `figure_generator/` (jeweils eigene Unterpakete), plus `protocol_generator.py`, `state_explorer.py`, `cib_visualizer.py`
- `src/llm/` — LLM-Backend-Auswahl und **der eine** Ollama-Client (`llm_client.OllamaClient`: Retry mit Backoff, dann `RuntimeError`). `studio_helpers.LocalOllama` ist nur noch die Env-Übersetzung davor; einen zweiten, still mockenden Client gibt es seit P0.1 nicht mehr
- `src/models/` — Pydantic-Datenmodelle (State, Events, Agenten, Population, Properties, CIB) — bewusst eine gemeinsame Schicht, nicht weiter aufgeteilt (fragile Import-Reihenfolge, siehe unten)
- `src/prompts/` — Prompt-Templates pro Agent (`consumer.md`, `provider.md`, `regulator.md`)
- `src/legacy/` — abgelöste Komponenten (z. B. `CIBExtractorNode`), nicht Teil der aktiven Pipeline
- `src/run_simulation.py`, `src/config_loader.py`, `src/validation.py`, `src/logging_setup.py` — bleiben bewusst Top-Level (CLI-Einstieg bzw. von mehreren Paketen genutzt)

Jedes Paket hat ein `__init__.py`, das die öffentliche API re-exportiert.

- `dashboard/` — Präsentations-UI. Der oberflächenfreie Service-Layer liegt direkt darin (`config_catalog.py`, `run_browser.py`, `run_launcher.py`, `consistency_report.py`) und wird von beiden Oberflächen geteilt:
  - `dashboard/web/` — **aktive** Plotly-Dash-App im Design der Landingpage. `app.py` (Rahmen/Routing), `theme.py` (Design-Tokens + Plotly-Template), `components.py`, `state.py` (`ConfigDraft` ⇄ `dcc.Store`), `runner.py` (Lauf im Hintergrund-Thread), `pages/` (inkl. `docs.py` — Handbuch mit Kapitelregistry und Suche), `views/` (die sieben Run-Tabs), `config_editor/` (die sechs Editor-Tabs, Erklärtexte gebündelt in `glossary.py`)
  - `dashboard/legacy_streamlit/` — abgelöste Streamlit-UI, nur noch zum Vergleich lauffähig; **keine neuen Funktionen dort einbauen**
- `aeroforesight-ai-landing-page/` — statische Landingpage. Wird von der Dash-App selbst ausgeliefert: Landingpage auf `/`, Dashboard auf `/app/` (`dashboard/web/landing_route.py`, Pfade in `dashboard/web/routing.py`). Ihre Design-Tokens (`design/color-tokens.json`) sind die Quelle für das Dashboard-Theme
- `langgraph_studio/` — interaktive Graph-Entwicklung (LangGraph Studio)
- `configs/` — Simulationskonfiguration (`simulation_config.json`, `properties.json`, `agents.json`, `agent_profiles.json`, `cib_frozen.json`, `sweeps/`)
- `tests/` — pytest-Suite (über 500 Tests; die genaue Zahl liefert `pytest --collect-only -q`, sie gehört bewusst nicht als feste Zahl in die Doku — siehe P4.3); `test_dashboard_service.py` deckt den Service-Layer ab, `test_web_state.py` die Draft-Serialisierung, `test_web_layout.py` jede Ansicht der Dash-App (auch mit unvollständigen Run-Verzeichnissen)
- `docs/handbuch/` — die geschriebenen Kapitel des Dashboard-Handbuchs (Markdown, vom Dashboard unter `/doku` gerendert); Referenzkapitel entstehen zur Laufzeit aus `configs/`
- `docs/` — technische Doku (CIB-Methodik, Agent-Profile, Szenario-Workflow) und `docs/audit_findings.md` (bekannte Bugs/Inkonsistenzen, bewusst nicht gefixt — bitte durchgehen und priorisieren); `docs/research/` — Fachliteratur

## Domain-Glossar

- **Tick** — kleinste Simulationseinheit, hat **keine** Kalenderbedeutung (kein Quartal/Jahr). Uhr: `current_tick` / `max_ticks`.
- **CIB-Matrix** (Cross-Impact-Balance, Weimer-Jehle) — eingefrorene Referenzmatrix (`configs/cib_frozen.json`), bewertet die interne Konsistenz von Faktor-Konstellationen. **Stand heute** prüft `scenario_consistency.py` einzelne Zellen gegen einen Schwellwert und summiert Konflikte — das ist eine eigene Heuristik, nicht das Impact-Balance-Kriterium der Methode. Bis [P2.2](docs/projektplan.md) umgesetzt ist, nicht als "Algorithmus nach Weimer-Jehle" bezeichnen. Details: [`docs/cib_role.md`](docs/cib_role.md), [`docs/cib_rationale.md`](docs/cib_rationale.md).
- **Faktoren F1–F7** — Zustandsvariablen des soziotechnischen Systems (Mobilitätsnachfrage, Regulierung, Technologie/SAF, Wirtschaft, Alternativen, Gesellschaft, Geopolitik), je zwei Zustände (z. B. F1.1/F1.2). **Achtung F7-Drift — offene Entscheidung:** `configs/factors.json` führt F7 als "Geopolitische Stabilitaet", `configs/cib_frozen.json` wurde für "Marktstruktur" bewertet — offener Widerspruch, seit dem ersten Commit. Bis die Lesart entschieden ist, F7 in keiner Aussage nach außen verwenden. **Haiko hat sich für "Geopolitische Stabilität" ausgesprochen, Manus Entscheidung steht aus** — sie ist der einzige Blocker für [P0.2](docs/projektplan.md#p02--f7-drift-auflösen); dort liegen die Auswertung beider Lesarten und zwei fertig ausgearbeitete Umsetzungswege.
- **Logit-Modell** — mikroökonomisches Nutzenmodell für Kaufentscheidungen der simulierten Population. **Stand heute** ist es keine Logit-Ziehung: `_booking_probability` rechnet die Sigmoid und vergleicht sie gegen 0.5, was einer deterministischen Schwelle auf dem Nutzen entspricht (`src/population/population_sampler.py:355`). Die Formulierung nach außen entsprechend vorsichtig halten, bis [P2.1](docs/projektplan.md) umgesetzt ist.
- **Agent-Profile** (Consumer, Provider, Regulator) — informationsbeschränkte LLM-Agenten; erlaubte Beobachtungen/Outputs pro Rolle in `configs/agent_profiles.json`. Details: [`docs/agent_profiles.md`](docs/agent_profiles.md).
- **State Explorer** — Q&A über abgeschlossene Run-Daten (`tick_mechanics.json`, `price_history.json`, `event_log.json`). Das Modell bekommt ausschließlich diese Daten als Kontext. **Stand heute** wird die Antwort danach *nicht* gegen den Kontext geprüft — die Zusage "keine erfundenen Zahlen" ist eine Prompt-Anweisung, keine Schranke. Bis [P2.5](docs/projektplan.md) umgesetzt ist, entsprechend vorsichtig formulieren.

## Harte Architektur-Invarianten

Diese Prinzipien sind der eigentliche USP des Produkts (Schutz vor LLM-Halluzination) und dürfen nie aufgeweicht werden:

1. **Zahlen kommen immer aus Python, nie vom LLM.** Preise, Booking-Raten, Faktorzustände etc. werden deterministisch berechnet (`src/market/simulation_functions.py`, `src/market/market_rules.py`, `src/market/factor_dynamics.py`). LLM-Agenten liefern ausschließlich Narrative/Events, nie Kennzahlen.
   **Und ein Ausfall ist sichtbar.** Kein Codepfad darf eine erfundene Antwort an die Stelle einer echten setzen, ohne das festzuhalten. Fällt ein LLM-Aufruf aus, wird er über `logging` gemeldet, landet als `LLMIncident` in `state.llm_incidents`, wird nach `llm_incidents.json` geschrieben und markiert den Lauf in `run_metadata.json` als `degraded` — das Dashboard zeigt ihn dann mit Warnbanner. Ein bewusster Mock-Lauf (`--mock-llm`) ist **kein** Ausfall und wird nicht so markiert. Wer einen neuen LLM-Aufrufer baut, hängt ihn an diese Kette an.
2. **Agenten dürfen nur vorschlagen, was ihr Profil erlaubt.** Regulator darf F2/F6 vorschlagen (Python-validiert über `AGENT_FACTOR_PERMISSIONS`), Provider/Consumer nur Events. Nicht ohne Rücksprache erweitern.
3. **Die CIB-Matrix ist bewusst eingefroren** (`"frozen": true`). Sie darf sich nicht aus Simulationsläufen ableiten — sonst wird der Maßstab aus dem Messobjekt gewonnen (zirkulär).
4. **Pydantic-Typisierung an allen Agenten-Grenzen** — jede Cross-Boundary-Datenstruktur ist ein typisiertes Modell in `src/models/`, keine rohen Dicts.
5. **Ein Tick ist ein Tick** — keine Kalender-/Datumssemantik in Configs, Checkpoints oder Outputs einführen.

## Dev-Workflow

**Immer im venv arbeiten — und zwar in `.venv` im Repo-Wurzelverzeichnis.** Kein globales Python, kein anders benanntes Verzeichnis. Der Ordner ist in `.gitignore`, jede und jeder legt ihn lokal selbst an:

```powershell
py -3.12 -m venv .venv          # oder eine neuere 3.x; pyproject verlangt >= 3.11
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Alle folgenden Befehle setzen ein **aktiviertes** venv voraus:

```powershell
pytest                    # volle Test-Suite
ruff check .               # Linting
black --check .            # Formatierung prüfen (black . zum Formatieren)

python -m src.run_simulation --mock-llm --rounds 1 --quiet   # Smoke-Test ohne Ollama
python -m dashboard.web.app --port 8511                       # Landingpage auf /, Dashboard auf /app/
python -m streamlit run dashboard/legacy_streamlit/app_researcher.py --server.port=8512   # Legacy-Vergleich
```

Ohne Aktivierung liegen `pytest`, `ruff` und `black` nicht auf dem PATH — dann entweder aktivieren oder direkt aufrufen: `.\.venv\Scripts\ruff.exe check .`. Ein `python`, das nicht aus `.venv` kommt, findet das Paket `src` nicht, weil `pip install -e` nur ins venv geschrieben hat.

**Warum das eine Konvention und keine Empfehlung ist:** [`.claude/launch.json`](.claude/launch.json) startet das Dashboard über `.venv/Scripts/python.exe`. Diese relative Angabe funktioniert auf jedem Rechner — aber nur, wenn das venv wirklich `.venv` heißt und dort liegt. Bis 2026-08-26 stand dort ein absoluter Pfad in ein fremdes Benutzerverzeichnis; das Dashboard ließ sich damit auf keinem anderen Rechner starten. Die Datei bleibt deshalb bewusst **versioniert** und gehört nicht in `.gitignore`: eine relative Angabe ist für alle richtig, eine ignorierte Datei müsste jede und jeder neu erfinden.

`black` + `ruff` vor jedem Commit laufen lassen (CI in `.github/workflows/tests.yml` prüft beides plus Tests).

Drei Tests brauchen Aufmerksamkeit (Stand 2026-08-26, verifiziert). **Alle drei sind in [`.github/workflows/tests.yml`](.github/workflows/tests.yml) per `--deselect` ausgeklammert** — die CI ist deshalb grün, ein lokaler `pytest`-Lauf ohne Ollama ist es nicht. Die drei Zeilen fallen mit [P4.2](docs/projektplan.md):

- `test_run_single_sweep_short` und `test_sweep_base_price_override_raises_ticket_price` (`tests/test_scenario_sweeps.py`) **hängen** ohne lokalen Ollama minutenlang, statt sauber zu skippen — nicht einfach "bekannte Fehler". Behebung in P4.2.
- `test_market_rules_resolve_marginal_cost_fraction` (`tests/test_market_feedback.py::TestM413ConfigurablePrice`) ist **kein Code-Bug**: der Test erwartet den Default `0.33`, `configs/properties.json` liefert `0.25`, die Auflösung in `market_rules.py:45` arbeitet korrekt. Zu klären ist nur, welcher Wert fachlich stimmt — dann Test oder Config nachziehen.

Import-Reihenfolge in `src/models/__init__.py` ist bewusst nicht alphabetisch (löst einen circular import zwischen `state_models` und `event_models`) — Kommentar dort beachten, nicht von Formattern umsortieren lassen.

## Deployment-Ziel

Hetzner Cloud Server mit lokal laufendem Ollama (Datenhoheit, keine externen LLM-Calls für sensible B2B-Daten). `Dockerfile`/`docker-compose.yml` sind ein Ausgangspunkt, noch nicht produktionsscharf.

## Backlog

**[docs/projektplan.md](docs/projektplan.md) ist die verbindliche Reihenfolge** — dort steht, was wann drankommt, mit Fundstelle und Abnahmekriterium pro Paket. Nichts davon ungefragt vorziehen, aber auch nichts mehr als "bekannt und bewusst offen" abtun: seit 2026-08-25 ist **jedes** Finding aus `docs/audit_findings.md` einem Arbeitspaket zugeordnet (Zuordnungstabelle am Ende des Plans).

- **Phase 0** — Vertrauens-Blocker vor dem nächsten Demo: sichtbarer LLM-Ausfall (P0.1 ✅), F7-Drift, `validate_config`, die zwei auseinandergelaufenen Rule-Evaluatoren, Faktor-Berechtigungen aus einer Quelle, und ein Run-Artefakt, das Seed und Rechenmodus überhaupt festhält.
  **⏳ Hier wartet etwas auf eine Person, nicht auf Arbeit:** P0.2 braucht von **Manu** einen Satz dazu, ob F7 "Geopolitische Stabilität" oder "Marktstruktur" bedeutet. Haiko ist für Geopolitische Stabilität, die Auswertung im Plan empfiehlt dasselbe. Sobald die Antwort da ist, ist P0.2 sofort umsetzbar — beide Wege sind dort Datei für Datei ausgeschrieben.
- **Phase 1** — aktueller Schwerpunkt: Start-Flow, Ergebnisdarstellung, Szenariogestaltung, Landingpage produktionsreif.
- **Phase 2** — Modellsubstanz: echte Ziehung im Buchungsmodell, Impact-Balance, Matrix-Provenienz, Alterung der Population, Grounding des State Explorers.
- **Phasen 3–5** — Engine-Härtung, Testfundament, Altlasten (inkl. Entfernen von `dashboard/legacy_streamlit/`).
- **Phase 6** — API-Layer und Multi-Tenant-B2B: bewusst noch nicht im Scope. Das Tor dorthin ist in Phase 6 des Plans benannt; es hängt an vier abgehakten Phase-1-Paketen, nicht an einem Gefühl.

Drei Fallstricke aus der Gegenprobe vom 2026-08-26, die beim Anfassen der betroffenen Pakete zuerst zu lesen sind: **P3.5 nicht vor P0.1** (das Fortschritts-Log des Dashboards hängt an `print()`), **P2.1 braucht einen Zufallsstrom pro Tick** (sonst buchen in jedem Tick dieselben Individuen), und **P2.2 braucht vorher eine Entscheidung**, was gilt, wenn die Impact Balance weniger als drei konsistente Szenarien liefert.

`docs/audit_findings.md` bleibt die Detailliste (Befund, Auswirkung, Fundstelle). Behobene Findings dort **entfernen**, neu gefundene ergänzen und im Projektplan einplanen.
