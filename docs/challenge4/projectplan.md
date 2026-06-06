# Project Plan – Challenge 4

C4 Aufgabenstellung:

- Dynamisierung der Einflussfaktoren (z. B. CO2-Steuer erst ab Tick N)
- Wechselwirkungen im System (Faktoren, Markt, Population, Agenten)
- Explorationsmöglichkeiten des Simulationsstands (z. B. Chat über Checkpoint/Protokoll)

## Ausgangslage: Feedback aus C3


| Thema           | Problem in C3                                       | Ziel in C4                                                   |
| --------------- | --------------------------------------------------- | ------------------------------------------------------------ |
| CIB             | 182 Zellen per LLM pro Runde                        | Kein LLM für CIB; Matrix fix aus C3-Kopie, aktiv im Lauf     |
| Agenten         | Freie Zahlen, `impact_assessment`, Halluzinationen  | Rechnung in Funktionen; LLM nur für 3 Rollen, kurzes JSON    |
| Population      | 3 Segmente, nur `normal`, kaum genutzt              | N persistente Individuen, SFO-Typologien (Multi-Label), lognormal/beta, Alter×Segment-Auswertung, Wertewandel über Ticks |
| Orchestrierung  | Redebedarf-Score, sequentiell, mehrfach pro Agent/Tick | Default: Orchestrator → drei Agenten **parallel**, je **einmal** pro Tick; Redebedarf nur mit `--redebedarf` **(M3c erledigt)** |
| Zeitmodell      | Quartale überall                                    | Ein Tick ist ein Tick                                        |
| Pipeline        | Runner und LangGraph getrennt                       | Batch (`ParallelRoundNode` Default) + Studio; ein CLI-Einstieg `--studio` **(M3c erledigt)** |
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

**Default (C4):** Pro Tick läuft die Pipeline **ohne Redebedarf-Scheduler**:

```
OrchestratorNode (Tick +1)
  → ParallelRoundNode: asyncio.gather — consumer, provider, regulator je **1×** LLM-Aufruf
  → MarketNode
  → EnvironmentNode
```

- Kein `RedebedarfScheduler`, kein Score-Loop, keine mehrfachen Beiträge desselben Agents pro Tick.
- Pro Tick genau **ein** `RoundResult` mit **drei** `agent_responses` (Reihenfolge egal, parallel).
- Protokoll: **kein** `redebedarf_score` / `redebedarf_reasons` im Default-Lauf.

**Legacy-Modus (`--redebedarf`):** C3-Verhalten zum Vergleich — `RoundExecutionNode` + `RedebedarfScheduler`, sequentiell nach Score, mehrere Rundenbeiträge pro Agent möglich, `redebedarf_score` im Protokoll. Nur für Studio/Batch wenn Flag gesetzt; nicht Default.

| Modus | Knoten | Agenten/Tick | Protokoll |
| ----- | ------ | ------------ | --------- |
| Default | `ParallelRoundNode` | 3× parallel, je 1× | reasoning, actions, events, segment_analysis |
| `--redebedarf` | `RoundExecutionNode` | sequentiell, Score-gesteuert | zusätzlich redebedarf_score, mehrere Zeilen pro Agent möglich |

**Ist (Code, M3c):** Batch und Studio nutzen standardmäßig `ParallelRoundNode` (3× je Agent/Tick, kein Redebedarf im Protokoll). `RoundExecutionNode` + Scheduler nur mit `--redebedarf` bzw. `SIMULATION_REDEBEDARF=1` (Studio).

Implementierung: `RunnerOptions.enable_redebedarf`, CLI `--redebedarf`, gleiche Logik in `langgraph_workflow.py` / Studio-Graph **(erledigt)**.

### Population und Statistik

Kernantwort auf C3-Feedback: **keine drei Punktwerte**, sondern **N = 1000 persistente Individuen** mit statistischen Verteilungen, deterministischer Buchungslogik und strukturierten Auswertungen für Präsentation und Report.

#### Segmentmodell: SFO Principles of Reach (Multi-Label)

Referenz: SFO Passenger-Typologien — **Leisure, Business, Family, Assisted, Unique** (überlappend; ein Passenger kann mehrere Labels haben).

| Typologie | Kurz | Kalibrierung (Orientierung) |
| --------- | ---- | --------------------------- |
| `leisure` | Freizeit, preissensitiv bis luxury | ~40 % Prevalence (SFO-Survey 2012) |
| `business` | Termindruck, geringe Preissensitivität | ~33 % |
| `family` | Gruppe, Stress, Schulferien | ~15–20 % (Schätzung) |
| `assisted` | Barrierefreiheit, Assistenzbedarf | ~5–8 % |
| `unique` | VIP, Angstflieger, Sprachbarriere | ~3–5 % |

**Designentscheidung (bindend für M3):**

- **Multi-Label:** Jede Person hat `primary_typology` (für LLM-`segment_analysis`) plus `tags: list[str]` (Bernoulli-Prevalence pro Typ; Anteile summieren sich **nicht** auf 100 %).
- **Keine disjunkte Partition** mehr (Ist: `share`-Summe = 1.0 im Sampler — wird ersetzt).
- Environment-Prompt und `validation.py` angleichen: Prevalence ≤ 1 pro Typ, Summe der Prevalences darf > 1 sein.

Legacy-Mapping (Migration aus C3-Config): `business` → `business`; `leisure_price_sensitive` / `leisure_eco_conscious` → `leisure` (+ optional `eco`-Tag oder höhere Awareness-Parameter).

#### Attribute pro Individuum

| Attribut | Verteilung | Schiefe | Rolle | Wo konfiguriert |
| -------- | ---------- | ------- | ----- | ---------------- |
| `age` | Buckets (18–24 … 75+) oder stückweise Uniform | keine Glockenkurve nötig | Kreuzauswertung, Typ-Prior | `configs/agents.json` → `age_distribution` |
| `income_eur` / `wtp_eur` | **lognormal** (EUR) | **rechtsschief** | Budget / Zahlungsbereitschaft (WTP) | pro Typologie in `agents.json` |
| `environmental_awareness` | **beta(α, β)** (0–1) | links/rechts steuerbar | CO₂-/Green-Penalty | pro Typologie |
| `price_sensitivity` | abgeleitet oder beta (0–1) | typologieabhängig | Preisreaktion in Utility | abgeleitet aus Einkommen + Typ-Basis |

**WTP vs. Preiselastizität (fachlich trennen, im Report definieren):**

- **WTP (Zahlungsbereitschaft):** maximal akzeptierter Ticketpreis — lognormal, rechtsschief; hohes Einkommen → hohe WTP.
- **Preiselastizität / `price_sensitivity`:** Stärke der Reaktion auf Preisänderungen — im Code als kalibrierter Index 0–1 in der Logit-Utility; im Report optional als ε = (%Δ Buchungen)/(%Δ Preis) aus Sweeps ableiten.
- Ableitung (Vorschlag): `price_sensitivity = clip(typology_base + k × (1 − normalized_income), 0, 1)` — reiche zahlen weniger preissensitiv.

**Gesamtpopulation:** Mischverteilung über Typologien → aggregiert oft **bimodal** (z. B. Business-WTP hoch + Leisure-WTP niedrig). Schiefe in Auswertung über Median, Mittelwert, q10/q50/q90 — nicht als separates „skew“-Parameter.

#### Buchungslogik (deterministisch, kein LLM)

1. Beim Simulationsstart: `initialize_population()` — N Individuen mit festem Seed sampeln, in `state.population_individuals` persistieren.
2. Pro Tick: `evaluate_booking(individuals, ticket_price, carbon_tax, factors)` — Logit-Utility mit WTP-Gate, Preis- und Eco-Penalty; optional F5-Substitutionsterm (Alternativen).
3. Aggregation: `booking_rate` gesamt und pro Typologie/Tag; Alter×Typologie-Kreuztabelle.
4. Consumer-Agent: nur **Text-Zusammenfassung** aus Aggregaten (Median WTP, Quantile, Raten je Typ) — **keine freien Zahlen** im JSON.

Utility (Zielformel, in `population_sampler.py` / Report dokumentieren):

```
book if ticket_price <= wtp_eur × (1 + green_premium × awareness)
     AND logit(base_utility − price_sensitivity × normalized_price − eco_penalty) > threshold
```

#### Dynamik: gesellschaftlicher Wertewandel

**Dieselben 1000 IDs über alle Ticks** — Attribute und Typ-Prevalence verschieben sich regelbasiert (nicht jeden Tick neu sampeln):

| Treiber | Wirkung | Wo |
| ------- | ------- | --- |
| F6 (gesellschaftlicher Wandel) | `awareness += δ` pro Tick (geclippt) | `population_sampler.apply_factor_shifts()` |
| CO₂-Steuer / hoher Preis | höhere `price_sensitivity` bei Leisure; optional Typ-Migration | gleich + `environment_node` Prevalence-Shifts |
| F5 (Alternativen) | Substitutions-Term in Utility | `population_sampler` |
| Typ-Prevalence | ±5 % pro Tick max. (Bernoulli-p je Typ) | `environment_node` + Validierung |

LLM (Environment Population-Update): verschiebt **Prevalence**, erfindet **keine** Individuen-Attribute.

#### Parameter: Config + Kalibrierung, nicht LLM

- Verteilungsparameter, SFO-Prevalence, Utility-Koeffizienten: `configs/agents.json` + `docs/challenge4/calibration_agents.md` (Quellen, Plausibilität).
- Sweeps (M4): Sensitivität Elastizität ±20 %, CO₂ ab Tick 15.
- LLM: nur narrative `segment_analysis` passend zu vorgegebenen Aggregaten.

#### Ist-Zustand vs. Soll (Stand Implementierung, Jun 2026)

| Thema | Ist (Code) | Soll (M3) |
| ----- | ---------- | --------- |
| Verteilungen | `normal` in Config; `_sample_distribution()` mit lognormal-String-Pfad, beta fällt auf normal zurück | lognormal + beta in `_sample_distribution()` |
| Segmente | 3 disjunkte Legacy-Segmente (`share` Summe = 1), engl. Text in `agents.json` | 5 SFO-Typologien, Multi-Label |
| `income` / WTP | `income_level` gesampelt, **nicht** in Utility / Buchung | WTP in Buchungsentscheidung |
| Alter | fehlt | `age` + Buckets in Export |
| Persistenz | jeden Tick neu sampeln (`run_population_sampling`) | `state.population_individuals` über Ticks |
| Validierung | `validate_segments`: Summe = 1.0 | Prevalence-Modell |
| Export | `segment_analysis.json`, `population_stats` in State/Narrative | + `population.csv` mit Alter×Typ, Quantilen |
| Orchestrierung | **ParallelRoundNode** Default, `--redebedarf` Legacy **(M3c erledigt)** | wie Soll |
| Prompts | Englisch (`src/prompts/*.md`, `agents.json`) **(erledigt)** | Englisch |

### Prompts

Englisch in `src/prompts/*.md` und `configs/agents.json` **(erledigt)**; knappe Ausgabe. Validierung in `validation.py`: erlaubte `factor_id`, `proposed_state`, Whitelist für `action_id`; keine Zahlenfelder von Agenten.

## Verzeichnisstruktur

### Code und Config (im Repo)

```
configs/
  simulation_config.json    policy_schedule, max_ticks
  agents.json               Typologien, Verteilungen, Prevalence, Alter
  factors.json              7 Faktoren F1–F7
  cib_frozen.json           M0: fixe C3-Matrix
  cib_baseline.json         M2b nach Coaching
  sweeps/
    co2_delayed.yaml

src/
  simulation_functions.py   M2
  population_sampler.py     M3: Sampling, Utility, Aggregation, Factor-Shifts
  scenario_sweeps.py        M4
  state_explorer.py         M5
  cib_engine.py             M2b
  simulation_runner.py      Batch-CLI; Default ParallelRoundNode (M3c erledigt)
  langgraph_workflow.py     Studio-Graph (Agent-Knoten sichtbar)
  run_simulation.py         Batch + --studio + --redebedarf
  config_loader.py
  output_writer.py          M3: population.csv, erweiterte segment_analysis
  studio_helpers.py
  models/
    population_models.py    M3: Individual, TypologyConfig, DistributionConfig
    enums.py                M3: DistributionType (+ beta, lognormal)
  nodes/
    parallel_round_node.py  M3c: Default — Orchestrator → 3 Agenten parallel (erledigt)
    redebedarf_node.py      M3c: nur --redebedarf / RoundExecutionNode (erledigt)
    environment_node.py     M3: Prevalence-Shifts, Population-Sampling
    agent_node.py           M3: Populationskontext-Aggregate an Consumer
  prompts/ ...

langgraph_studio/           M1: Studio-Adapter (.env, langgraph.json, graph.py)
  README.langgraph.md

docs/challenge4/
  projectplan.md
  calibration_agents.md       M3: SFO-Prevalence, Verteilungen, Literatur
  cib_coaching_questions.md   M0
  cib_rationale.md              M2b
  challenge4_report.md          M5: C3-Feedback Population, Grenzen Multi-Label

docs/archive/                 M5: challenge1–3, drafts (optional schon M1 anlegen)
docs/presentation/
  outline.md
  figures/

tests/
  test_policy_schedule.py
  test_population_config.py       M3: erweitern (Prevalence, beta)
  test_parallel_round.py          M3d (erledigt)
  test_population_sampler.py      M3d (offen)
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
    population.csv          M3: tick, typology, age_bucket, booking_rate, wtp_median, q90, ...
  checkpoints/
    tick_0001.json            enthält population_individuals (M3)
    ...

outputs/sweeps/<sweep_name>/
  run_001/ ...
  sweep_summary.json
```

Konvention: nie flach in `outputs/` schreiben. Plots für Präsentation nach `docs/presentation/figures/`. Alte Challenge-Docs nach `docs/archive/` (M5, optional schon in M1).

### Aufräumen: Ist-Zustand und Zuordnung zu Meilensteinen

**Gehört nicht zu M0.** M0 ist CIB-Logik (fixe Matrix, kein `impact_assessment`). Struktur-Aufräumen startet in **M1** (Pipeline, Outputs, Legacy-Code) und zieht sich bis **M5** (Doku-Archiv, Report, Präsentation).

**Kernproblem (gelöst in M1):** drei parallele Einstiege — jetzt klar getrennt, gleiche Agenten-Logik:


| Weg            | Dateien                                              | Umsetzung                                                                     |
| -------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------- |
| Batch-CLI      | `run_simulation.py` → `simulation_runner.py`         | Standard: `ParallelRoundNode`; Legacy `--redebedarf`; Outputs unter `outputs/<run_id>/` **(M3c erledigt)** |
| Studio-Graph   | `langgraph_workflow.py` → `langgraph_studio/graph.py` | Eigene Knoten **consumer / provider / regulator**; Redebedarf via `SchedulerNode` |
| Studio-Start   | `run_simulation.py --studio`                         | Startet `langgraph dev`; `.env` aus `langgraph_studio/`; Dep: `langgraph-cli[inmem]` |


**Weitere Baustellen:**


| Bereich        | Ist                                                                                                             | Soll / Aktion                                                                   | Meilenstein                      |
| -------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------- |
| Environment    | `environment_node_c2.py` entfernt; Tests auf `environment_node.py` | Erledigt | **M1** (erledigt) |
| Redebedarf     | Default: `ParallelRoundNode`, 1× je Agent; Scheduler nur `--redebedarf` | Erledigt (M3c) |
| Population     | MVP-Sampler (`run_population_sampling`), 3 Legacy-Segmente, kein Alter/WTP/Persistenz | SFO Multi-Label, lognormal/beta, persistente Individuen, Alter×Typ-Export (M3a/b offen) |
| CIB-Extractor  | `cib_extractor_node.py` (LLM, ~17 KB)                                  | Nicht im Loop (M0); Code für M2b behalten, ggf. `src/legacy/` | **M2b** |
| Sample-Outputs | `test_output/` im Root (Legacy)                                      | Entfernt; Lauf-Outputs nur unter `outputs/<run_id>/` | **M1** (erledigt) |
| Root-Müll      | `tmp_ollama_payload.json`, `package-lock.json` ohne `package.json`   | Gelöscht | **M1** (erledigt) |
| IDE            | `.idea/` versioniert                                                   | `.gitignore` | **M1** (erledigt) |
| Doku           | `README.md` = C2; `docs/drafts/`, `docs/agent_node.py`               | README C4; `agent_node.py` → `docs/archive/` | **M1** (erledigt) (README/Archiv), **M5** (restl. Drafts) |
| Playgrounds    | `haiko_playground/` → `langgraph_studio/`; `manu_playground/`        | Studio behalten; `manu_playground/` optional archivieren | **M1** (erledigt) (Studio), **M5** (manu_playground) |
| Referenzen     | `docs/references/` (PDFs)                                                                                       | Behalten (Thesis); nicht anfassen ohne Absprache                                | —                                |


**C4-Kern** (alles andere optional oder Legacy):

```
configs/              agents, factors, simulation_config, cib_frozen
src/                  config_loader, simulation_runner, run_simulation, nodes/, models/, prompts/
                      scenario_consistency, protocol_generator, output_writer, studio_helpers
langgraph_studio/     langgraph.json, graph.py, .env (gitignored)
tests/                pytest + fixtures/
docs/challenge4/      Plan, Report, Coaching, calibration_agents.md
outputs/<run_id>/     Laufzeit (gitignored)
requirements.txt      inkl. langgraph-cli[inmem] für Studio
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
4. `**impact_assessment` entfernen** (nur dieses JSON-Feld — **Protokoll und Redebedarf bleiben**):
  - Prompts: `src/prompts/consumer.md`, `provider.md`, `regulator.md`
  - Parsing: `src/nodes/agent_node.py`, Feld in `src/models/agent_models.py`
  - Protokoll: Abschnitt `impact.impact_assessment` und Markdown-Zeilen dazu in `src/protocol_generator.py` streichen; `reasoning`, `actions`, `state_changes`, `events`, `segment_analysis` bleiben; `redebedarf_score` nur im Modus `--redebedarf`
  - Redebedarf: CIB-Widerspruchs-Signale aus Agent-`impact_assessment` in `src/protocol_generator.py` / `src/redebedarf_scheduler.py` entfallen; übrige Trigger (Faktorwechsel, widersprüchliche `state_changes`, Erwähnungen im Text) bleiben
5. **Szenarioableitung** mit fixer Matrix unverändert nutzen (`src/scenario_consistency.py`, `ScenarioAgentNode`)
6. **Coaching-Vorbereitung:** `docs/challenge4/cib_coaching_questions.md` anlegen
7. **Export:** `outputs/<run_id>/cib_matrix.json` am Laufende (gleiche Matrix wie beim Start; Output-Pfad-Ziel laut Konvention — volle `output_writer`-Umstellung kann mit M1 zusammenfallen)
8. **Tests:** Erwartungen ohne LLM-CIB anpassen (`tests/test_end_to_end.py`, ggf. `tests/test_cib_matrix.py`)

**Offen nach M0 (an M1 delegiert, M1 erledigt):** echter C3-Re-Export in `cib_frozen.json` (statt Seed-Platzhalter) — weiterhin offen; Export-Pfad `outputs/<run_id>/` (erledigt)

Ergebnis:


| Was             | Pfad                                        |
| --------------- | ------------------------------------------- |
| Fixe Matrix     | `configs/cib_frozen.json`                   |
| Coaching-Fragen | `docs/challenge4/cib_coaching_questions.md` |
| Export pro Lauf | `outputs/<run_id>/cib_matrix.json`          |


### M1 – Fundament (erledigt)

Ziel: eine Pipeline, Tick-Modell, ein Output-Ort, LangGraph Studio integriert.

Aufgaben:

**Pipeline & Outputs**

- Batch: `simulation_runner.py` mit `ParallelRoundNode` Default; `RoundExecutionNode` nur `--redebedarf` **(M3c erledigt)**
- Studio: `langgraph_workflow.py` mit **eigenen Agent-Knoten** (consumer / provider / regulator) und `SchedulerNode` — gleiche Agenten, andere Graph-Darstellung für Debugging (erledigt)
- Tick in `configs/simulation_config.json` (`tick_unit: tick`), `output_writer.py`, Protokoll (erledigt)
- Ausgabe nach `outputs/<run_id>/`; Checkpoints unter `outputs/<run_id>/checkpoints/` (erledigt)
- `README.md` auf C4 aktualisiert (erledigt)

**LangGraph Studio**

- `haiko_playground/` → `langgraph_studio/` umbenannt (erledigt)
- Ein CLI-Einstieg: `python src/run_simulation.py --studio` (startet `python -m langgraph_cli dev`) (erledigt)
- Abhängigkeit: `langgraph-cli[inmem]>=0.2` in `requirements.txt` (erledigt)
- `.env` in `langgraph_studio/`; CLI lädt sie über `studio_helpers.load_env` (kein blockierender Import im Graph) (erledigt)
- Studio-Troubleshooting dokumentiert in `langgraph_studio/README.langgraph.md` (404 → `.langgraph_api` löschen, neuer Thread) (erledigt)

**Legacy-Code**

- C2-Legacy: `environment_node_c2.py` entfernt; Tests auf `environment_node.py` migriert (erledigt)
- `src/nodes/__init__.py`: Export auf C3-`EnvironmentNode` korrigiert (erledigt)

**Repo-Hygiene**

- `test_output/` entfernt (erledigt)
- Root-Artefakte entfernt: `tmp_ollama_payload.json`, `package-lock.json` (erledigt)
- `.idea/` in `.gitignore` (erledigt)
- `configs/calibration_agents.md` → `docs/challenge4/calibration_agents.md` (erledigt)
- `docs/agent_node.py` → `docs/archive/agent_node.py` (erledigt)
- `tests/test_run_output_layout.py` für Output-Konvention (erledigt)

Ergebnis:


| Was                | Pfad                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| Batch-Runner       | `src/simulation_runner.py`, `src/run_simulation.py`                  |
| Studio-Graph       | `src/langgraph_workflow.py`, `langgraph_studio/graph.py`             |
| Studio-Start       | `python src/run_simulation.py --studio`                              |
| Config             | `configs/simulation_config.json`                                     |
| Doku               | `README.md`, `langgraph_studio/README.langgraph.md`                  |
| Lauf-Outputs       | `outputs/<run_id>/`                                                  |
| Studio-Deps        | `requirements.txt` → `langgraph-cli[inmem]`                           |


### M2 / M2a – Deterministischer Kern (ohne CIB-Inhalt)

Ziel: Preis, Steuer, SAF, Nachfrage nur über Funktionen.

**Status:** Kern umgesetzt (M2a fachlich erfüllt). Offene Punkte siehe unten.

Aufgaben:

- `policy_schedule` in `configs/simulation_config.json` (z. B. CO2-Steuer ab Tick 15) (erledigt)
- `src/simulation_functions.py` neu (erledigt)
- `src/nodes/market_node.py` und `src/nodes/environment_node.py` nutzen Funktionen statt Text-Parsing (erledigt)
- Legacy `scenario_parameters` entfernt; einzige Quelle: `policy_schedule` (erledigt)
- `tests/test_policy_schedule.py` inkl. Integration (Fuel/Tax/Demand-Shocks) (erledigt)
- `validate_policy_schedule()` in `validation.py` (erledigt)
- Agent-Prompts: Marktmetriken aus `policy_schedule`, keine freien Zahlen (erledigt)
- Output: `price_history.json`, `protocol.json`/`protocol.md` mit `demand_level` + `booking_rate` (erledigt)
- Studio: `langgraph.json` + `langgraph_adapter` mit `policy_schedule` (erledigt)
- `README.md` Abschnitt Policy-Schedule + Testanleitung (erledigt)

Policy-Parameter:


| ID                   | Bedeutung             | Einheit    | Implementiert |
| -------------------- | --------------------- | ---------- | ------------- |
| `carbon_tax_level`   | CO2-Steuer            | EUR/t      | ja (erledigt) |
| `fuel_price_change`  | Treibstoffpreis-Trend | %/Tick     | ja (erledigt) |
| `oil_price_index`    | Ölpreis               | Index      | ja (Metrik; siehe Offen) |
| `saf_mandate_share`  | SAF-Pflichtanteil     | 0–1        | ja (erledigt) |
| `efuel_subsidy`      | E-Fuel-Förderung      | EUR oder % | ja (Platzhalter; erledigt) |
| `demand_growth_rate` | Nachfrage             | %/Tick     | ja (erledigt) |

**Offen nach M2a (nicht blockierend für M3):**

1. **`oil_price_index` in Preisformel:** Index wird berechnet und geloggt, fließt aber noch nicht in `derive_ticket_price()` ein (nur `fuel_price_change`).
2. **`derive_ticket_price` Kalibrierung:** CO₂-Durchschlag (`tax/10000`) und SAF-Aufschlag sind MVP-Heuristiken — später mit Literatur/Teamwerten hinterlegen.
3. **Policy-Shocks in Config:** Demo-Werte (Tick 2/4/5/7) für Tests; **Ziel-Szenario:** CO₂ ab Tick 15 in `simulation_config.json` + Sweep `co2_delayed.yaml` (M4).
4. **`--no-market` Randpfad:** Ohne `MarketNode` berechnet `EnvironmentNode` Metriken, schreibt aber keinen `price_history`-Eintrag — selten genutzt, Tests fehlen.
5. **Tests optional:** SAF-Ramp (Tick 4) auf Preis; Protokoll-`market`-Block nach vollem E2E-Lauf; `--no-market`-Pfad.
6. **`booking_rate`:** kommt aus M3 (`population_sampler`); bewusst getrennt von M2-`demand_level` — fachliche Verzahnung in M3 (WTP/Utility), Auswertung je SFO-Typologie.

Ergebnis:


| Was        | Pfad                             |
| ---------- | -------------------------------- |
| Schedule   | `configs/simulation_config.json` |
| Funktionen | `src/simulation_functions.py`    |
| Tests      | `tests/test_policy_schedule.py`  |
| Doku       | `README.md` (Abschnitt Policy-Schedule) |


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

Ziel: C3-Feedback „fehlende Statistik“ vollständig adressieren — parallele Agenten, halluzinationssichere Prompts, **statistische Population mit SFO-Typologien**, persistenter Wertewandel, exportierbare Auswertungen für M4/M5.

**Status (Jun 2026):** **M3c (Orchestrierung, Prompts EN) erledigt.** **M3a/b (Population/SFO) größtenteils offen** — MVP-Sampler mit Logit-Utility und `booking_rate` existiert, aber ohne persistente Individuen, SFO-Typologien, WTP/Alter und CSV-Export.

**Priorität (bei Zeitdruck):** (1) Verteilungen lognormal/beta + Plots → (2) SFO Multi-Label → (3) Alter×Typ-Export → (4) Persistenz + F5/F6-Shifts → (5) Parallel/Orchestrierung **(5 erledigt)**.

#### M3a – Datenmodell und Config

| Aufgabe | Datei(en) | Status |
| ------- | --------- | ------ |
| `Individual`-Modell: `id`, `age`, `wtp_eur`, `awareness`, `price_sensitivity`, `primary_typology`, `tags` | `src/models/population_models.py` | offen |
| `TypologyConfig`: `id`, `prevalence`, Verteilungen pro Attribut (lognormal/beta) | `src/models/population_models.py` | offen (Legacy: `ConsumerSegment` + `share`) |
| `DistributionType`: `normal`, `lognormal`, `beta`, `uniform`, `triangular` | `src/models/enums.py` | teilweise (`normal`, `uniform`, `triangular`; `lognormal`/`beta` fehlen im Enum) |
| SFO-Typologien + Prevalence + Alter-Buckets | `configs/agents.json` | offen (3 Legacy-Segmente; Text EN) |
| Kalibrierung dokumentieren (SFO 40 % Leisure, Elastizität pro Typ, Quellen) | `docs/challenge4/calibration_agents.md` | offen |
| Validierung: Prevalence-Modell (keine Summe = 1.0 Pflicht); beta-Parameter | `src/validation.py` | offen (noch `validate_segments` mit Summe = 1.0) |
| Laden neuer Config-Struktur | `src/config_loader.py` | teilweise (lädt Legacy-`PopulationConfig`) |

#### M3b – Sampler und Buchungslogik

| Aufgabe | Datei(en) | Status |
| ------- | --------- | ------ |
| `initialize_population(seed)` — einmalig N Individuen | `src/population_sampler.py` | offen |
| `_sample_distribution()` — lognormal, beta korrekt (nicht als normal) | `src/population_sampler.py` | teilweise (lognormal per String; beta → normal-Fallback) |
| Multi-Label: Bernoulli-Tags + `primary_typology` conditional on age/weights | `src/population_sampler.py` | offen |
| WTP in Utility; `price_sensitivity` aus Einkommen/Typ | `src/population_sampler.py` | offen |
| `apply_factor_shifts(individuals, factors)` — Awareness, optional F5 | `src/population_sampler.py` | offen |
| `run_population_sampling()` → Aggregat inkl. **Alter×Typologie**, Quantile | `src/population_sampler.py` | teilweise (Segment-Aggregate + `booking_rate`; kein Alter×Typ, keine Quantile) |
| Persistenz: `state.population_individuals` über Ticks; Checkpoint serialisieren | `src/nodes/environment_node.py`, State-Modell | offen |
| Prevalence-Shifts ±5 %/Tick; Prompt/Validierung angleichen (Multi-Label) | `src/nodes/environment_node.py` | teilweise (Share-Shifts ±5 %/Tick für disjunkte Segmente; Env-Prompt noch DE) |

#### M3c – Agenten, Orchestrierung, Outputs

| Aufgabe | Datei(en) | Status |
| ------- | --------- | ------ |
| **`ParallelRoundNode`:** consumer, provider, regulator je 1× LLM-Aufruf (parallel) | `src/nodes/parallel_round_node.py` | erledigt (Consumer sequentiell, Provider/Regulator parallel via `ThreadPoolExecutor`) |
| Default-Pipeline: Orchestrator → **ParallelRoundNode** → Market → Environment | `src/simulation_runner.py`, `langgraph_workflow.py` | erledigt |
| `RunnerOptions.enable_redebedarf` + CLI `--redebedarf` | `src/simulation_runner.py`, `src/run_simulation.py` | erledigt |
| Mit Flag: bestehende `RoundExecutionNode` + `RedebedarfScheduler` (C3-Pfad) | `src/nodes/redebedarf_node.py` | erledigt |
| Protokoll: `redebedarf_score` / Mehrfach-Zeilen **nur** bei `--redebedarf` | `src/protocol_generator.py`, `output_writer.py` | erledigt |
| Studio: Default parallel; Redebedarf via `SchedulerNode` nur mit Flag | `langgraph_workflow.py`, `scheduler_node.py` | erledigt (`SIMULATION_REDEBEDARF=1`) |
| Redebedarf-Doppelcode zusammenführen | `scheduler_node.py`, `redebedarf_node.py` | offen |
| Consumer-Prompt: Aggregat-Statistik (keine freien Zahlen) | `src/prompts/consumer.md`, `agent_node.py` | offen (Populationskontext = Segment-Config, keine Aggregat-Quantile) |
| `segment_analysis`-Keys = Typologie-IDs aus Config | `validation.py`, `agent_node.py` | teilweise (Filter unbekannter Keys in `agent_node.py`) |
| `timeseries/population.csv` pro Tick | `src/output_writer.py` | offen |
| Erweiterte `segment_analysis.json` (strukturiert + LLM-Text) | `src/output_writer.py`, `protocol_generator.py` | teilweise (LLM-Text in `segment_analysis.json`; keine strukturierten Aggregat-Stats) |
| Englische Prompts | `src/prompts/`, `configs/agents.json` | erledigt |

**Akzeptanz Default-Lauf:** Pro Tick exakt 3 Agent-Responses, kein `redebedarf_score`, Protokoll ohne Wiederholungs-Blöcke pro Agent **(erledigt, vgl. `tests/test_parallel_round.py`)**.

#### M3d – Tests

| Aufgabe | Datei(en) | Status |
| ------- | --------- | ------ |
| Feste Seeds: Verteilungsform (Median < Mean bei lognormal) | `tests/test_population_sampler.py` | offen (Datei fehlt) |
| Multi-Label: Person kann mehrere Tags haben | `tests/test_population_sampler.py` | offen |
| Persistenz: gleiche IDs Tick 1 vs. Tick 2 nach Shift | `tests/test_population_sampler.py` | offen |
| Config-Validierung Prevalence | `tests/test_population_config.py` | teilweise (Share-Summe = 1.0, nicht Prevalence) |
| Parallel-Runde: 3 Responses, kein redebedarf_score | `tests/test_parallel_round.py` | erledigt |
| Redebedarf-Pfad optional: Score im Protokoll nur mit Flag | `tests/test_parallel_round.py` | erledigt |

Ergebnis:


| Was | Pfad | Status |
| --- | ---- | ------ |
| Parallel-Orchestrierung (Default) | `src/nodes/parallel_round_node.py`, `src/simulation_runner.py` | erledigt |
| Redebedarf (Legacy, Flag) | `src/nodes/redebedarf_node.py`, `src/redebedarf_scheduler.py` | erledigt |
| Sampler + Shifts | `src/population_sampler.py` | teilweise (MVP ohne Persistenz/Shifts) |
| Individuen-Modell | `src/models/population_models.py` | offen |
| Typologien + Verteilungen | `configs/agents.json` | offen (Legacy-Segmente) |
| Kalibrierung | `docs/challenge4/calibration_agents.md` | offen |
| Statistik pro Lauf | `outputs/<run_id>/segment_analysis.json`, `timeseries/population.csv` | teilweise (`segment_analysis.json` ja; `population.csv` nein) |
| Checkpoints mit Population | `outputs/<run_id>/checkpoints/tick_*.json` | offen |

**Figures (M5, Daten aus M3):** Histogramm WTP/Awareness gesamt; booking_rate je SFO-Typ; Kreuztabelle Alter×Typ; Vor/Nach CO₂ (Tick 15) → `docs/presentation/figures/`


### M4 – Dynamik sichtbar machen

Ziel: Sweeps und Zeitreihen für Emergenz-Demos — **Populationseffekte** (booking_rate je SFO-Typ, Alter-Buckets) neben Marktmetriken.

Aufgaben:

- `src/scenario_sweeps.py` (for-loop über Configs, kein LLM)
- `configs/sweeps/co2_delayed.yaml` — **CO₂ ab Tick 15** (Vergleich Tick 0 vs. 15)
- Weitere Sweeps: Elastizität ±20 %, Awareness-Shift (F6)
- CLI: `python src/run_simulation.py --sweep configs/sweeps/co2_delayed.yaml`
- CSV-Export pro Tick unter `timeseries/` inkl. `population.csv`-Spalten aus M3
- Szenarien aus fixer CIB + Sweeps
- `sweep_summary.json`: booking_rate-Delta je Typologie, gesamt

Ergebnis:


| Was        | Pfad                                                |
| ---------- | --------------------------------------------------- |
| Sweeps     | `outputs/sweeps/<name>/run_*`, `sweep_summary.json` |
| Zeitreihen | `outputs/<run_id>/timeseries/*.csv`                 |
| Szenarien  | `outputs/<run_id>/scenarios.json`, `scenarios.md`   |


### M5 – Abgabe

Ziel: Chat, Tests, Präsentation, Bericht — Population und Statistik als Antwort auf C3-Feedback dokumentieren.

Aufgaben:

- `src/state_explorer.py` (grounded Chat über Checkpoint/Protokoll — inkl. Populations-CSV)
- Tests ohne Ollama (`MockLLM`)
- `docs/presentation/outline.md` und Figures (aus M3/M4-Daten)
- `docs/challenge4/challenge4_report.md`:
  - C3-Feedback → Umsetzung (Population, LLM-Grenze, CIB)
  - Abschnitt **Population**: SFO Multi-Label, WTP vs. Elastizität, Verteilungen, Wertewandel
  - Abschnitt **Grenzen**: vereinfachtes Utility, keine echten Passagier-Microdaten
- `docs/challenge4/calibration_agents.md` finalisieren (Quellen)
- **Doku aufräumen:** `docs/challenge1/` … `docs/challenge3/`, `docs/drafts/` → `docs/archive/`; `interfaces.md` prüfen/aktualisieren
- **Playgrounds:** Entscheidung `manu_playground/` — archivieren oder unter `experiments/` + gitignore; `langgraph_studio/` ist der Studio-Adapter (Einstieg: `run_simulation.py --studio`)

Präsentation (Gliederung in `docs/presentation/outline.md`):

1. C3-Learnings und C4-Ziele
2. Architektur (LLM vs. deterministische Kernrechnung)
3. Emergenz-Demo (CO₂-Steuer Tick 0 vs. 15 — booking_rate je SFO-Typ)
4. CIB-Heatmap (fixe C3-Matrix, aktiv genutzt)
5. **Verteilungen und Zeitreihen** (WTP/Awareness histograms, Alter×Typ, bimodal durch Mixture)
6. Chat-Demo
7. Offene CIB-Fragen (Coaching / M2b)
8. Literatur, Kalibrierung und Grenzen

Ergebnis:


| Was       | Pfad                                   |
| --------- | -------------------------------------- |
| Explorer  | `src/state_explorer.py`                |
| Report    | `docs/challenge4/challenge4_report.md` |
| Demo-Lauf | `outputs/<run_id>/`                    |


