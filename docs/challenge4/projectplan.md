# Project Plan – Challenge 4

C4 Aufgabenstellung:

- Dynamisierung der Einflussfaktoren (z. B. CO2-Steuer erst ab Tick N)
- Wechselwirkungen im System (Faktoren, Markt, Population, Agenten)
- Explorationsmöglichkeiten des Simulationsstands (z. B. Chat über Checkpoint/Protokoll)

## Ausgangslage: Feedback aus C3


| Thema          | Problem in C3                                      | Ziel in C4                                                |
| -------------- | -------------------------------------------------- | --------------------------------------------------------- |
| CIB            | 182 Zellen per LLM pro Runde                       | Kein LLM für CIB; Matrix fix aus C3-Kopie, aktiv im Lauf  |
| Agenten        | Freie Zahlen, `impact_assessment`, Halluzinationen | Rechnung in Funktionen; LLM nur für 3 Rollen, kurzes JSON |
| Population     | 3 Segmente, nur `normal`, kaum genutzt             | N Individuen, Mischverteilung, schiefe Attribute          |
| Orchestrierung | Redebedarf, sequentiell                            | Default: parallel, je Agent einmal pro Tick               |
| Zeitmodell     | Quartale überall                                   | Ein Tick ist ein Tick                                     |
| Pipeline       | Runner und LangGraph getrennt                      | Ein Pfad: LangGraph ruft Runner-Logik auf                 |
| Projektstruktur | C1–C3-Schichten, doppelte Pipelines, Legacy im Repo | Klare Ordner, eine Orchestrierung, Archiv statt Müll im Root |


Bewertung als Orientierung: Challenge 1 (9/10), Challenge 2 (15/20), Challenge 3 schwächer mit Kritik an der Logik (LLM für Berechnungen, CIB, fehlende Statistik).

## Designentscheidungen

### LLM-Grenze

- **Mit LLM:** die drei Rollen-Agenten (`consumer`, `provider`, `regulator`) für narrative Begründung und Aktionen im JSON-Schema.
- **Ohne LLM:** CIB-Zellen, Preis, Steuer, SAF, Nachfrage, Populations-Mengen, Szenario-Enumeration (Mathematik in Python/numpy).
- **Optional:** Chat-Explorer liest nur aus State/Protokoll und erfindet keine Zahlen.

Temperature für Agenten: 0,3 bis 0,5. Emergenz entsteht durch Policy-Schocks, Faktorübergänge und Population, nicht durch hohe LLM-Temperature.

### CIB: aktiv, Inhalt fix (bis Coaching)

Die bestehende CIB aus C3 bleibt im System nutzbar (State, Export, Szenarioableitung, Visualisierung). Der Inhalt wird vorerst nicht geändert: keine Neubefüllung, kein `CIBExtractorNode` pro Tick, kein `cib_engine` bis nach dem Coaching (Meilenstein M2b).

Technik:

1. Bester C3-Lauf mit aktuellem Export neu erzeugen → `CIBMatrix`-JSON (`cells`, Deskriptor-IDs F1.1–F7.2, vgl. `docs/challenge3/cib_format.md`). Daraus `configs/cib_frozen.json` (14×14, −3..+3).
2. Beim Start in `config_loader` laden, `state.cib_matrix` setzen.
3. Pro Tick kein LLM-Update (`CIBExtractorNode` aus Runden-Loop in `simulation_runner.py` und `langgraph_workflow.py`); am Ende `outputs/<run_id>/cib_matrix.json` exportieren (unveränderte Kopie der geladenen Matrix).
4. `impact_assessment` entfernen (siehe M0): Agenten liefern keine CIB-Zellwerte mehr.

Nach dem Coaching (M2b): `configs/cib_baseline.json`, `docs/challenge4/cib_rationale.md`, `src/cib_engine.py` (deterministische Updates, weiterhin kein LLM für Zellen).

### Tick-Modell

`current_tick` / `max_ticks` in Config, CLI und Protokoll. Keine Quartals-Rhetorik in der Doku; Anzeige neutral als „Tick N“.

### Orchestrierung

Default pro Tick: Orchestrator erhöht Tick, dann parallel ein LLM-Aufruf je Agent (`asyncio.gather`). Redebedarf bleibt im Code, nur mit Flag `--redebedarf` (Vergleich zu C3).

### Population und Statistik

Drei Segmente in `configs/agents.json` bleiben. Heterogenität über N gesampelte Individuen (z. B. 1000), nicht über drei Punktwerte. Gesamtdarstellung = Mischverteilung der Segmente (dort entsteht Schiefe, oft bimodal).

Attribute (wenige, entscheidungsrelevant):

- `income`: lognormal (EUR)
- `environmental_awareness`: beta (0–1)
- `price_elasticity`: aus Einkommen und Segment abgeleitet

Ablauf: `population_sampler.py` zieht Individuen, Choice-Funktion (Logit) für Buchung, Aggregation (Median, Quantile, Anteile). Der Consumer-Agent bekommt nur die Text-Zusammenfassung, keine freien Zahlen im JSON.

Dynamik regelbasiert: z. B. CO2-Steuer + F6 verschiebt Segment-Anteile (max. ±5 % pro Tick), F5 verschiebt Awareness-Mittel.

### Prompts

Englisch in `src/prompts/*.md`, knappe Ausgabe. Validierung in `validation.py`: erlaubte `factor_id`, `proposed_state`, Whitelist für `action_id`; keine Zahlenfelder von Agenten.

## Verzeichnisstruktur

### Code und Config (im Repo)

```
configs/
  simulation_config.json    policy_schedule, max_ticks
  agents.json               Segmente, Verteilungen
  factors.json              7 Faktoren F1–F7
  cib_frozen.json           M0: fixe C3-Matrix
  cib_baseline.json         M2b nach Coaching
  sweeps/
    co2_delayed.yaml

src/
  simulation_functions.py   M2
  population_sampler.py     M3
  scenario_sweeps.py        M4
  state_explorer.py         M5
  cib_engine.py             M2b
  simulation_runner.py
  langgraph_workflow.py     an Runner angebunden
  config_loader.py
  output_writer.py
  nodes/ ...
  prompts/ ...

docs/challenge4/
  projectplan.md
  cib_coaching_questions.md   M0
  cib_rationale.md              M2b
  challenge4_report.md          M5

docs/archive/                 M5: challenge1–3, drafts (optional schon M1 anlegen)
docs/presentation/
  outline.md
  figures/

tests/
  test_policy_schedule.py
  test_population_sampler.py
  test_parallel_round.py
  test_scenario_sweeps.py
  test_cib_engine.py            M2b
```

### Laufzeit-Outputs (`outputs/`, gitignored)

Jeder Lauf in `outputs/<run_id>/` mit `run_id` z. B. `run_<UTC-Timestamp>`:

```
outputs/<run_id>/
  run_metadata.json
  event_log.json
  price_history.json
  round_history.json
  segment_analysis.json
  cib_matrix.json
  protocol.json
  protocol.md
  scenarios.json
  scenarios.md
  final_narrative.md
  timeseries/
    factors.csv
    parameters.csv
    population.csv
  checkpoints/
    tick_0001.json
    ...

outputs/sweeps/<sweep_name>/
  run_001/ ...
  sweep_summary.json
```

Konvention: nie flach in `outputs/` schreiben. Abgabe-Plots nach `docs/presentation/figures/`. Alte Challenge-Docs nach `docs/archive/` (M5, optional schon in M1).

### Aufräumen: Ist-Zustand und Zuordnung zu Meilensteinen

**Gehört nicht zu M0.** M0 ist CIB-Logik (fixe Matrix, kein `impact_assessment`). Struktur-Aufräumen startet in **M1** (Pipeline, Outputs, Legacy-Code) und zieht sich bis **M5** (Doku-Archiv, Abgabe).

**Kernproblem:** drei parallele Einstiege statt einer Pipeline:

| Weg | Dateien | Problem |
| --- | ------- | ------- |
| CLI | `run_simulation.py` → `simulation_runner.py` | Standard; nutzt `RoundExecutionNode` (Redebedarf) |
| Playground-Graph | `langgraph_workflow.py` | Anderer Graph: `SchedulerNode` + Agent-Nodes einzeln |
| Studio-Adapter | `haiko_playground/` | Extra-Schicht; teils erneuter Aufruf von `run_simulation` |

**Weitere Baustellen:**

| Bereich | Ist | Soll / Aktion | Meilenstein |
| ------- | --- | ------------- | ----------- |
| Environment | `environment_node.py` + `environment_node_c2.py`; `nodes/__init__.py` exportiert C2 | C2-Node löschen, Tests migrieren | **M1** |
| Redebedarf | `redebedarf_node.py` + `scheduler_node.py` (duplizierte Helfer) | Default parallel (M3); Redebedarf nur `--redebedarf`; Doppelcode zusammenführen | **M3** |
| CIB-Extractor | `cib_extractor_node.py` (LLM, ~17 KB) | Nicht im Loop (M0 ✅); Code für M2b behalten, ggf. `src/legacy/` | **M2b** |
| Sample-Outputs | `test_output/` im Root (Legacy) | Entfernt; Lauf-Outputs nur unter `outputs/<run_id>/` | **M1** ✅ |
| Root-Müll | `tmp_ollama_payload.json`, `package-lock.json` ohne `package.json` | Löschen | **M1** |
| IDE | `.idea/` versioniert | `.gitignore` | **M1** |
| Doku | `README.md` = C2; `docs/drafts/`, doppelte `literature_fundamentals.md`, `docs/agent_node.py` (Python in docs/) | README C4; Entwürfe archivieren oder löschen | **M1** (README), **M5** (Archiv) |
| Playgrounds | `manu_playground/`, großteils `haiko_playground/` | Nur behalten, wenn Studio genutzt wird; sonst `experiments/` + gitignore | **M5** (Entscheidung) |
| Referenzen | `docs/references/` (PDFs) | Behalten (Thesis); nicht anfassen ohne Absprache | — |

**C4-Kern** (alles andere optional oder Legacy):

```
configs/          agents, factors, simulation_config, cib_frozen
src/              config_loader, simulation_runner, run_simulation, nodes/, models/, prompts/
                  scenario_consistency, protocol_generator, output_writer
tests/            pytest + fixtures/
docs/challenge4/  Plan, Report, Coaching
outputs/<run_id>/ Laufzeit (gitignored)
```

## Meilensteine (zeitliche Reihenfolge)

Reihenfolge: M0 → M1 → M2 → M3 → M4 → M5. M2b nach Coaching

```
M0 → M1 → M2 → M3 → M4 → M5
                    Coaching → M2b
```

### M0 – CIB aktiv, Inhalt fix

Ziel: CIB im Lauf nutzbar, Matrix unverändert, kein LLM-CIB pro Tick. Agenten liefern keine freien CIB-Zellwerte mehr.

**Ist-Zustand (Code):**

- `CIBExtractorNode` läuft **pro Runde** nach `EnvironmentNode` (LLM, ~182 Zellen/Runde)
- Agent-Prompts und `agent_node.py` verlangen/parsen `impact_assessment`
- `protocol_generator.py` und `redebedarf_scheduler.py` werten `impact_assessment` aus
- Kein Laden einer fixen Matrix in `config_loader` (M0: erledigt)

Aufgaben:

1. **Matrix einfrieren:** Bester C3-Lauf mit aktuellem Export neu erzeugen; daraus `configs/cib_frozen.json` im `CIBMatrix`-Format ablegen
2. **Laden:** `load_cib_frozen()` in `src/config_loader.py` → `state.cib_matrix` in `build_initial_state()`
3. **Kein LLM-CIB pro Tick:** `CIBExtractorNode` aus Runden-Loop entfernen in `src/simulation_runner.py` und `src/langgraph_workflow.py`; `enable_cib` = frozen Matrix aktiv (Standard), nicht Extractor
4. **`impact_assessment` entfernen** (nur dieses JSON-Feld — **Protokoll und Redebedarf bleiben**):
   - Prompts: `src/prompts/consumer.md`, `provider.md`, `regulator.md`
   - Parsing: `src/nodes/agent_node.py`, Feld in `src/models/agent_models.py`
   - Protokoll: Abschnitt `impact.impact_assessment` und Markdown-Zeilen dazu in `src/protocol_generator.py` streichen; `reasoning`, `actions`, `state_changes`, `events`, `segment_analysis`, `redebedarf_score` bleiben
   - Redebedarf: CIB-Widerspruchs-Signale aus Agent-`impact_assessment` in `src/protocol_generator.py` / `src/redebedarf_scheduler.py` entfallen; übrige Trigger (Faktorwechsel, widersprüchliche `state_changes`, Erwähnungen im Text) bleiben
5. **Szenarioableitung** mit fixer Matrix unverändert nutzen (`src/scenario_consistency.py`, `ScenarioAgentNode`)
6. **Coaching-Vorbereitung:** `docs/challenge4/cib_coaching_questions.md` anlegen
7. **Export:** `outputs/<run_id>/cib_matrix.json` am Laufende (gleiche Matrix wie beim Start; Output-Pfad-Ziel laut Konvention — volle `output_writer`-Umstellung kann mit M1 zusammenfallen)
8. **Tests:** Erwartungen ohne LLM-CIB anpassen (`tests/test_end_to_end.py`, ggf. `tests/test_cib_matrix.py`)

**Offen nach M0-Implementierung (bewusst an M1 delegiert):** echter C3-Re-Export in `cib_frozen.json` (statt Seed-Platzhalter); Export-Pfad `outputs/<run_id>/` (noch flaches `outputs/`).

Ergebnis:


| Was             | Pfad                                        |
| --------------- | ------------------------------------------- |
| Fixe Matrix     | `configs/cib_frozen.json`                   |
| Coaching-Fragen | `docs/challenge4/cib_coaching_questions.md` |
| Export pro Lauf | `outputs/<run_id>/cib_matrix.json`          |


### M1 – Fundament

Ziel: eine Pipeline, Tick-Modell, ein Output-Ort. **Erster Aufräum-Meilenstein** (siehe Abschnitt „Aufräumen“).

Aufgaben:

**Pipeline & Outputs**

- `src/langgraph_workflow.py` an `src/simulation_runner.py` anbinden (ein Graph, kein paralleler `SchedulerNode`-Pfad als zweite Wahrheit)
- Tick in `configs/simulation_config.json`, `src/output_writer.py`, Protokoll
- `src/output_writer.py` + `run_simulation.py`: Ausgabe nach `outputs/<run_id>/` (nicht flach in `outputs/`)
- `README.md` auf C4 aktualisieren

**Legacy-Code**

- C2-Legacy: `src/nodes/environment_node_c2.py` entfernen; Tests (`test_end_to_end.py`, `test_environment_updates.py`) auf `environment_node.py` migrieren
- `src/nodes/__init__.py`: Export auf C3-`EnvironmentNode` korrigieren

**Repo-Hygiene (klein, wenig Risiko)**

- `test_output/` entfernt (kein Ersatz nötig)
- Root-Artefakte entfernen: `tmp_ollama_payload.json`, `package-lock.json` (ohne `package.json`)
- `.idea/` in `.gitignore`
- `configs/calibration_agents.md` → `docs/challenge4/` (falls behalten)
- `docs/agent_node.py` entfernen oder nach `docs/archive/` verschieben

Ergebnis:


| Was                | Pfad                                                    |
| ------------------ | ------------------------------------------------------- |
| Runner / LangGraph | `src/simulation_runner.py`, `src/langgraph_workflow.py` |
| Config             | `configs/simulation_config.json`                        |
| Doku               | `README.md`                                             |
| Lauf-Outputs       | `outputs/<run_id>/`                                     |


### M2 – Deterministischer Kern (ohne CIB-Inhalt)

Ziel: Preis, Steuer, SAF, Nachfrage nur über Funktionen.

Aufgaben:

- `policy_schedule` in `configs/simulation_config.json` (z. B. CO2-Steuer ab Tick 15)
- `src/simulation_functions.py` neu
- `src/nodes/market_node.py` und `src/nodes/environment_node.py` nutzen Funktionen statt Text-Parsing

Policy-Parameter:


| ID                   | Bedeutung             | Einheit    |
| -------------------- | --------------------- | ---------- |
| `carbon_tax_level`   | CO2-Steuer            | EUR/t      |
| `fuel_price_change`  | Treibstoffpreis-Trend | %/Tick     |
| `oil_price_index`    | Ölpreis               | Index      |
| `saf_mandate_share`  | SAF-Pflichtanteil     | 0–1        |
| `efuel_subsidy`      | E-Fuel-Förderung      | EUR oder % |
| `demand_growth_rate` | Nachfrage             | %          |


Ergebnis:


| Was        | Pfad                             |
| ---------- | -------------------------------- |
| Schedule   | `configs/simulation_config.json` |
| Funktionen | `src/simulation_functions.py`    |


### M2b – CIB nach Coaching

Ziel: Methodik mit Professoren geklärt, dann deterministische CIB-Updates.

Aufgaben:

- `docs/challenge4/cib_rationale.md`
- `configs/cib_baseline.json` (14×14, −3 bis +3)
- `src/cib_engine.py`, `CIBExtractorNode` ruft nur Engine auf
- `tests/test_cib_engine.py`
- Optional: `outputs/<run_id>/cib_baseline_snapshot.json`

Ergebnis:


| Was          | Pfad                               |
| ------------ | ---------------------------------- |
| Baseline     | `configs/cib_baseline.json`        |
| Engine       | `src/cib_engine.py`                |
| Begründungen | `docs/challenge4/cib_rationale.md` |


### M3 – Agenten parallel und Population

Ziel: drei parallele Agenten pro Tick, halluzinationssichere Prompts, statistische Population.

Aufgaben:

- Parallel in `src/simulation_runner.py`, `--redebedarf` in `src/run_simulation.py`
- Redebedarf-Doppelcode: `scheduler_node.py` vs. `redebedarf_node.py` — gemeinsame Helfer extrahieren oder einen Pfad deprecaten (Playground-Graph dann über Runner)
- Strikte Validierung in `src/validation.py`
- Englische Prompts in `src/prompts/`
- `src/population_sampler.py`, erweiterte Verteilungen in `src/models/enums.py`
- `configs/agents.json` mit lognormal/beta

Ergebnis:


| Was                | Pfad                                                                  |
| ------------------ | --------------------------------------------------------------------- |
| Sampler            | `src/population_sampler.py`                                           |
| Segmente           | `configs/agents.json`                                                 |
| Statistik pro Lauf | `outputs/<run_id>/segment_analysis.json`, `timeseries/population.csv` |


### M4 – Dynamik sichtbar machen

Ziel: Sweeps und Zeitreihen für Emergenz-Demos.

Aufgaben:

- `src/scenario_sweeps.py` (for-loop über Configs, kein LLM)
- `configs/sweeps/co2_delayed.yaml` und weitere
- CLI: `python src/run_simulation.py --sweep configs/sweeps/co2_delayed.yaml`
- CSV-Export pro Tick unter `timeseries/`
- Szenarien aus fixer CIB + Sweeps

Ergebnis:


| Was        | Pfad                                                |
| ---------- | --------------------------------------------------- |
| Sweeps     | `outputs/sweeps/<name>/run_*`, `sweep_summary.json` |
| Zeitreihen | `outputs/<run_id>/timeseries/*.csv`                 |
| Szenarien  | `outputs/<run_id>/scenarios.json`, `scenarios.md`   |


### M5 – Abgabe

Ziel: Chat, Tests, Präsentation, Bericht.

Aufgaben:

- `src/state_explorer.py` (grounded Chat über Checkpoint/Protokoll)
- Tests ohne Ollama (`MockLLM`)
- `docs/presentation/outline.md` und Figures
- `docs/challenge4/challenge4_report.md` (Feedback → Umsetzung)
- **Doku aufräumen:** `docs/challenge1/` … `docs/challenge3/`, `docs/drafts/` → `docs/archive/`; `interfaces.md` prüfen/aktualisieren
- **Playgrounds:** Entscheidung `manu_playground/`, `haiko_playground/` — behalten (Studio) oder aus Repo / unter `experiments/` + gitignore

Präsentation (Gliederung in `docs/presentation/outline.md`):

1. C3-Learnings und C4-Ziele
2. Architektur
3. Emergenz-Demo (z. B. CO2-Steuer Tick 0 vs. 15)
4. CIB-Heatmap (fixe C3-Matrix, aktiv genutzt)
5. Verteilungen und Zeitreihen
6. Chat-Demo
7. Offene CIB-Fragen (Coaching / M2b)
8. Literatur und Grenzen

Ergebnis:


| Was       | Pfad                                   |
| --------- | -------------------------------------- |
| Explorer  | `src/state_explorer.py`                |
| Report    | `docs/challenge4/challenge4_report.md` |
| Demo-Lauf | `outputs/<run_id>/`                    |