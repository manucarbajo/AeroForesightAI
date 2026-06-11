# Traceability-Tabelle: Challenge 1 → Challenge 2

## Akteure

| C1 Konzept | C1 Quelle | C2 Umsetzung | Datei/Klasse |
|------------|-----------|--------------|--------------|
| MVP-Akteur: Konsumenten | Abschnitt 1.2.1 | `AgentConfig(id="consumer")` | `configs/agents.json` |
| MVP-Akteur: Anbieter | Abschnitt 1.2.1 | `AgentConfig(id="provider")` | `configs/agents.json` |
| MVP-Akteur: Regulatorien | Abschnitt 1.2.1 | `AgentConfig(id="regulator")` | `configs/agents.json` |
| Sub-Agenten: Private/Geschäftspassagiere | Abschnitt 1.2.3 | `ConsumerSegment` (leisure_price_sensitive, business_traveler) | `src/models/population_models.py` |
| Agenten-Ziele & Constraints | Glossar 2.2 | `AgentConfig.goals`, `AgentConfig.constraints` | `src/models/agent_models.py` |
| Agenten-Typ Enum | Klassendiagramm 5.2 | `AgentType(CONSUMER, PROVIDER, REGULATOR)` | `src/models/enums.py` |

---

## Einflussfaktoren

| C1 Konzept | C1 Quelle | C2 Umsetzung | Datei/Klasse |
|------------|-----------|--------------|--------------|
| F1: Mobilitätsbedürfnis / Nachfrage | Abschnitt 1.3, 1.4 | `FactorState(id="F1")` | `configs/factors.json` |
| F2: Regulatorische Strenge | Abschnitt 1.3, 1.4 | `FactorState(id="F2")` | `configs/factors.json` |
| F3: Technologische Reife | Abschnitt 1.3, 1.4 | `FactorState(id="F3")` | `configs/factors.json` |
| F4: Wirtschaftliche Entwicklung | Abschnitt 1.3, 1.4 | `FactorState(id="F4")` | `configs/factors.json` |
| F5: Verfügbarkeit von Alternativen | Abschnitt 1.3, 1.4 | `FactorState(id="F5")` | `configs/factors.json` |
| F6: Gesellschaftlicher Wertewandel | Abschnitt 1.3, 1.4 | `FactorState(id="F6")` | `configs/factors.json` |
| F7: Geopolitische Stabilität | Abschnitt 1.3, 1.4 | `FactorState(id="F7")` | `configs/factors.json` |
| 2 Zustände pro Faktor (Kontinuität/Transformation) | Abschnitt 1.4 | `FactorState.possible_states` (F1.1/F1.2 etc.) | `configs/factors.json` |
| Faktor-Zustand als einzige Wahrheitsquelle im EnvironmentState | Klassendiagramm 5.2 | `EnvironmentState.factors` | `src/models/state_models.py` |

---

## Datenmodell & State

| C1 Konzept | C1 Quelle | C2 Umsetzung | Datei/Klasse |
|------------|-----------|--------------|--------------|
| `SimulationState` als TypedDict | Klassendiagramm 5.2 | `SimulationState` (Pydantic BaseModel) | `src/models/state_models.py` |
| `SimulationConfig` | Klassendiagramm 5.2 | `SimulationConfig` | `src/models/state_models.py` |
| `EnvironmentState` | Klassendiagramm 5.2 | `EnvironmentState` | `src/models/state_models.py` |
| `AgentResponse` mit reasoning, decisions, factor_assessments | Klassendiagramm 5.2 | `AgentResponse` mit reasoning, actions, state_changes, segment_analysis | `src/models/agent_models.py` |
| `RoundResult` mit responses + env_state | Klassendiagramm 5.2 | `RoundResult` mit agent_responses, events, environment_snapshot, summary | `src/models/event_models.py` |
| `CIBMatrix` + `CIBEntry` | Klassendiagramm 5.2 | `CIBMatrix`, `CIBEntry` | `src/models/cib_models.py` |
| `FactorState` mit possible_states | Klassendiagramm 5.2 | `FactorState` | `src/models/state_models.py` |
| Zeitlicher Horizont 2025–2035 | Abschnitt 1.1 | `SimulationClock(year_start=2025, years_per_round=1)` | `configs/simulation_config.json` |
| 10 Simulationsrunden | Abschnitt 1.1 | `SimulationClock(max_rounds=10)` | `configs/simulation_config.json` |
| Szenarioparameter konfigurierbar | US-A1, NFA-03 | `ScenarioParameter` | `src/models/population_models.py` |
| Populationsmodell / Konsumentensegmente | Abschnitt 1.2.3 | `PopulationConfig`, `ConsumerSegment`, `DistributionConfig` | `src/models/population_models.py` |
| Preiselastizität differenziert nach Segmenten | Abschnitt 1.3 | `ConsumerSegment.price_elasticity` | `src/models/population_models.py` |

---

## Simulationslogik & Nodes

| C1 Konzept | C1 Quelle | C2 Umsetzung | Datei/Klasse |
|------------|-----------|--------------|--------------|
| Sequentielle Agenten-Reihenfolge (Consumer → Provider → Regulator) | Klassendiagramm 5.2, Ablaufdiagramm 5.3 | `EnvironmentNode(prefer_agent_order=["regulator","provider","consumer"])` | `src/nodes/environment_node.py` |
| `AgentNode` parametrisiert statt Subklassen | Klassendiagramm 5.2 | `AgentNode(config, llm)` – eine Klasse, drei Instanzen | `src/nodes/agent_node.py` |
| `EnvironmentNode`: Faktoren aktualisieren + Narrativ | Ablaufdiagramm 5.3 | `EnvironmentNode._apply_state_changes()`, `_build_round_summary()` | `src/nodes/environment_node.py` |
| Rundenloop: `round < total_rounds` | Ablaufdiagramm 5.3 | `while state.clock.current_round < state.clock.max_rounds` | `src/run_simulation.py` |
| `CIBExtractorNode` post-hoc aus History | Ablaufdiagramm 5.3 | `CIBExtractorNode.invoke()` | `src/nodes/cib_extractor_node.py` |
| JSON-Output-Schema für LLM-Parsing | Klassendiagramm 5.2 | Prompt-Templates mit JSON-Schema-Vorgabe | `src/prompts/consumer.md`, `provider.md`, `regulator.md` |
| Fallback bei Parse-Fehler | Klassendiagramm 5.2 | `AgentNode._default_response()` | `src/nodes/agent_node.py` |
| Prompt-Bau per Template | Klassendiagramm 5.2 | `AgentNode._build_prompt()` | `src/nodes/agent_node.py` |
| Markt-Preisbildung (Nachfrageelastizität) | Abschnitt 1.3 | `MarketNode._derive_price()`, `_derive_demand_level()` | `src/nodes/market_node.py` |

---

## Output & Anforderungen

| C1 Konzept | C1 Quelle | C2 Umsetzung | Datei/Klasse |
|------------|-----------|--------------|--------------|
| Gesprächsprotokoll speichern (US-A6) | US-A6 | `save_event_log()`, `save_round_history()` | `src/output_writer.py` |
| CIB-Matrix lokal speichern (US-A6) | US-A6, US-A5 | `save_cib_matrix()` | `src/output_writer.py` |
| Narrativ-Zusammenfassung | Ablaufdiagramm 5.3 | `save_final_narrative()` | `src/output_writer.py` |
| Preishistorie | Abschnitt 1.3 | `save_price_history()` | `src/output_writer.py` |
| Segmentanalyse | Abschnitt 1.2.3 | `save_segment_analysis()` | `src/output_writer.py` |
| Run-Metadaten | US-D1 | `save_run_metadata()` | `src/output_writer.py` |
| Konfigurierbarkeit über JSON (NFA-03) | NFA-03 | `configs/simulation_config.json`, `agents.json`, `factors.json` | `configs/` |
| Vollständig lokal lauffähig (NFA-04) | NFA-04 | Ollama + lokales LLM | `src/llm_client.py` |
| Validierung der Konfiguration | NFA-01 | `validate_state()`, `validate_population_config()` | `src/validation.py` |
| Modularität (NFA-06) | NFA-06 | Getrennte Nodes, Models, Config-Loader | `src/nodes/`, `src/models/` |

---

## Bekannte Abweichungen von C1

| C1 Konzept | C1 Erwartung | C2 Realität | Begründung |
|------------|-------------|-------------|------------|
| `SimulationState` als TypedDict | Klassendiagramm 5.2 | Pydantic `BaseModel` statt TypedDict | Pydantic bietet Validierung und `.model_dump()` – besser geeignet für MVP |
| Irreversible Faktor-Wechsel | Limitation Ablaufdiagramm 5.3 | Faktoren können in beide Richtungen wechseln | Flexiblere Simulation, LLM entscheidet pro Runde |
| CIB regelbasiert aus History | Ablaufdiagramm 5.3 | Heuristikbasiert aus Event-Log (ohne LLM) | MVP-Vereinfachung: Robuster ohne LLM-Abhängigkeit im Extractor |
| `AgentResponse.decisions` | Klassendiagramm 5.2 | `AgentResponse.actions` | Sprachliche Vereinfachung, gleiche Semantik |
| `AgentResponse.factor_assessments` | Klassendiagramm 5.2 | `AgentResponse.state_changes` | Präziserer Begriff für vorgeschlagene Faktoränderungen |