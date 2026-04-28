# Interface-Dokumentation – AP1

## Übersicht

Dieses Dokument beschreibt die zentralen Datenstrukturen und Schnittstellen,
die in AP1 definiert wurden. Alle anderen Arbeitspakete (AP2–AP4) nutzen diese Modelle.

Alle Modelle basieren auf Pydantic v2 `BaseModel`.

---

## Enums (`src/models/enums.py`)

### AgentType
| Wert | Beschreibung |
|------|-------------|
| `consumer` | Konsumenten (Privat- & Geschäftsreisende) |
| `provider` | Anbieter (Fluggesellschaften) |
| `regulator` | Regulatorien (EU-Kommission, Regierungen) |

### EventType
| Wert | Beschreibung |
|------|-------------|
| `price_change` | Preisänderung durch Anbieter |
| `regulation` | Regulatorische Maßnahme |
| `demand_shift` | Nachfrageverschiebung |
| `investment` | Investitionsentscheidung |
| `policy_change` | Politikänderung |
| `market_event` | Marktereignis |
| `technology_shift` | Technologischer Wandel |

---

## State Models (`src/models/state_models.py`)

### FactorState
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | `str` | Faktor-ID (z.B. `F1`) |
| `name` | `str` | Name des Faktors |
| `description` | `str` | Kurzbeschreibung |
| `current_state` | `str` | Aktueller Zustand (z.B. `F1.1`) |
| `possible_states` | `dict[str, str]` | Mögliche Zustände mit Beschreibung |

### EnvironmentState
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `factors` | `dict[str, FactorState]` | Alle Faktoren nach ID |
| `global_context` | `str` | Optionaler globaler Kontext |

### SimulationClock
| Feld | Typ | Default | Beschreibung |
|------|-----|---------|-------------|
| `current_round` | `int` | `0` | Aktuelle Runde |
| `max_rounds` | `int` | `10` | Maximale Rundenanzahl |
| `year_start` | `int` | `2025` | Startjahr |
| `years_per_round` | `int` | `1` | Jahre pro Runde |

### LLMConfig
| Feld | Typ | Default | Beschreibung |
|------|-----|---------|-------------|
| `model` | `str` | `llama3` | LLM-Modellname |
| `temperature` | `float` | `0.7` | Sampling Temperature |
| `max_tokens` | `int` | `2048` | Maximale Tokenzahl |

### SimulationConfig
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `name` | `str` | Simulationsname |
| `description` | `str` | Beschreibung |
| `clock` | `SimulationClock` | Zeitkonfiguration |
| `llm` | `LLMConfig` | LLM-Einstellungen |
| `seed` | `int \| None` | Optionaler Seed |

---

## Agent Models (`src/models/agent_models.py`)

### AgentConfig
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | `str` | Agent-ID (z.B. `consumer`) |
| `name` | `str` | Anzeigename |
| `agent_type` | `AgentType` | Typ des Agenten |
| `description` | `str` | Rollenbeschreibung |
| `goals` | `list[str]` | Ziele des Agenten |
| `constraints` | `list[str]` | Einschränkungen |

### StateChange
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `factor_id` | `str` | Betroffener Faktor |
| `proposed_state` | `str` | Vorgeschlagener neuer Zustand |
| `reasoning` | `str` | Begründung |

### AgentResponse
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `agent_id` | `str` | ID des antwortenden Agenten |
| `round_number` | `int` | Rundennummer |
| `reasoning` | `str` | Begründung/Analyse des Agenten |
| `actions` | `list[str]` | Durchgeführte Aktionen |
| `state_changes` | `list[StateChange]` | Vorgeschlagene Zustandsänderungen |
| `raw_output` | `str` | Roher LLM-Output |

---

## Event Models (`src/models/event_models.py`)

### EventLogEntry
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `id` | `str` | Eindeutige Event-ID |
| `round_number` | `int` | Runde des Events |
| `source_agent` | `str` | Auslösender Agent |
| `event_type` | `EventType` | Art des Events |
| `description` | `str` | Beschreibung |
| `affected_factors` | `list[str]` | Betroffene Faktor-IDs |
| `timestamp` | `str` | Zeitstempel |

### PriceHistoryEntry
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `round_number` | `int` | Rundennummer |
| `agent_id` | `str` | Agent-ID |
| `price` | `float` | Preis |
| `demand_level` | `float` | Nachfrageniveau |
| `load_factor` | `float` | Auslastung |

### RoundResult
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `round_number` | `int` | Rundennummer |
| `agent_responses` | `list[AgentResponse]` | Antworten der Agenten |
| `events` | `list[EventLogEntry]` | Events der Runde |
| `environment_snapshot` | `EnvironmentState` | Umweltzustand nach der Runde |
| `summary` | `str` | Zusammenfassung |

---

## CIB Models (`src/models/cib_models.py`)

### CIBEntry
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `source_factor` | `str` | Quell-Faktor |
| `target_factor` | `str` | Ziel-Faktor |
| `influence_score` | `float` | Einflussstärke |
| `reasoning` | `str` | Begründung |

### CIBMatrix
| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `entries` | `list[CIBEntry]` | Einträge der Matrix |
| `round_generated` | `int` | Runde der Erzeugung |
| `metadata` | `dict` | Zusätzliche Metadaten |

---

## SimulationState (`src/models/state_models.py`)

Top-Level-Container für den gesamten Simulationszustand.

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `config` | `SimulationConfig` | Simulationskonfiguration |
| `clock` | `SimulationClock` | Simulationsuhr |
| `environment` | `EnvironmentState` | Umweltzustand |
| `agents` | `list[AgentConfig]` | Agentenkonfigurationen |
| `event_log` | `list[EventLogEntry]` | Event-Log |
| `price_history` | `list[PriceHistoryEntry]` | Preisverlauf |
| `round_results` | `list[RoundResult]` | Rundenergebnisse |
| `cib_matrix` | `CIBMatrix \| None` | CIB-Matrix |

---

## Config Loader (`src/config_loader.py`)

| Funktion | Return | Beschreibung |
|----------|--------|-------------|
| `load_simulation_config(path?)` | `SimulationConfig` | Lädt `simulation_config.json` |
| `load_agents(path?)` | `list[AgentConfig]` | Lädt `agents.json` |
| `load_factors(path?)` | `dict[str, FactorState]` | Lädt `factors.json` |
| `build_initial_state(...)` | `SimulationState` | Baut den initialen Simulationszustand |

---

## Konfigurationsdateien

| Datei | Beschreibung |
|-------|-------------|
| `configs/simulation_config.json` | Simulationsname, Runden, LLM-Config |
| `configs/agents.json` | 3 MVP-Agenten mit Goals & Constraints |
| `configs/factors.json` | 7 Einflussfaktoren (F1–F7) mit je 2 Zuständen |

---

## Validierung (`src/validation.py`)

| Funktion | Beschreibung |
|----------|-------------|
| `validate_factor(factor)` | Prüft ob current_state in possible_states liegt |
| `validate_agent(agent, factor_ids)` | Prüft ob Goals definiert sind |
| `validate_config(config)` | Prüft Clock-Parameter |
| `validate_state(state)` | Validiert gesamten State, wirft `ValidationError` |

---

## Beispiel: Initial State laden

```python
from src.config_loader import build_initial_state
from src.validation import validate_state

state = build_initial_state()
validate_state(state)

print(state.config.name)
print([a.id for a in state.agents])
print(list(state.environment.factors.keys()))
```
