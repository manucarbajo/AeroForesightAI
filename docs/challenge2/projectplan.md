# Project Plan – Challenge 2
## Prototypische Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr

## Ziel von Challenge 2
Ziel ist die technische Operationalisierung der in Challenge 1 definierten Domänenrepräsentation.  
Dafür wird ein lauffähiger MVP-Prototyp in Python mit LangGraph und Ollama umgesetzt, der:

- die 3 MVP-Akteure (Konsumenten, Anbieter, Regulatorien) als Agenten modelliert,
- heterogene Konsumentenpopulationen über Segmente mit stochastischen Verteilungen (Preiselastizität, Einkommen, Umweltbewusstsein) abbildet,
- konfigurierbare Szenarioparameter (Nachfragewachstum, Preisveränderungen) als steuerbare Inputs bereitstellt,
- die 7 Einflussfaktoren und ihre Zustände im State verwaltet,
- über mehrere Simulationsrunden läuft,
- ein Event-Log erzeugt,
- den Umweltzustand aktualisiert,
- Ergebnisse lokal speichert,
- und eine prototypische CIB-Nachverarbeitung ermöglicht.

---

## Teamstruktur
Das Projekt wird in 4 weitgehend entkoppelte Arbeitspakete aufgeteilt.  
Ziel der Aufteilung ist, gegenseitige Blockaden zu minimieren.

| Person | Arbeitspaket | Fokus |
|---|---|---|
| Person A | AP1 – Datenmodell & Konfiguration | Struktur, Klassen, JSON/Schema |
| Person B | AP2 – Agentenlogik & Prompting | Prompts, LLM-Output, Parsing |
| Person C | AP3 – Simulationsgraph & State-Flow | LangGraph, Rundenlogik, Environment |
| Person D | AP4 – Output, CIB, Testing & Dokumentation | Speicherung, Auswertung, Tests, Nachweis |

---

## Gemeinsame Arbeitsprinzipien

### 1. Klare Schnittstellen vor Implementierung
Vor dem Coden werden diese Interfaces gemeinsam festgelegt:
- Format von `SimulationState`
- Format von `AgentResponse`
- Format von `EventLogEntry`
- Format der Konfigurationsdateien
- Benennung von Faktoren, Zuständen und Agent-IDs

### 2. Feature-Branches
Jede Person arbeitet in einem eigenen Branch:
- `feature/ap1-config-state`
- `feature/ap2-agent-prompts`
- `feature/ap3-graph-environment`
- `feature/ap4-output-cib-docs`

### 3. Integration über Mock-Daten
Damit niemand blockiert wird, arbeitet jedes Paket zunächst mit Dummy-Inputs:
- AP2 nutzt Dummy-State
- AP3 nutzt Dummy-AgentResponses
- AP4 nutzt Dummy-EventLogs
- AP1 liefert früh JSON- und Datenmodell-Templates

### 4. Feste Merge-Punkte
Es gibt nur wenige geplante Integrationspunkte:
- M1: Datenformate eingefroren
- M2: Agenten liefern parsebare Outputs
- M3: Simulationsloop läuft end-to-end
- M4: Output + CIB + Doku vollständig

---

# Arbeitspakete im Detail

---

## AP1 – Datenmodell & Konfiguration
**Verantwortung:** Person A

### Ziel
Definition und Implementierung aller zentralen Datenstrukturen und Konfigurationsdateien.

### Aufgaben
- Python-Datenklassen / TypedDicts anlegen:
  - `SimulationConfig`
  - `SimulationClock`
  - `EnvironmentState`
  - `FactorState`
  - `AgentConfig`
  - `AgentResponse`
  - `EventLogEntry`
  - `PriceHistoryEntry`
  - `RoundResult`
  - `CIBEntry`
  - `CIBMatrix`
  - `SimulationState`
  - `PopulationConfig`
  - `ConsumerSegment`
  - `DistributionConfig`
  - `ScenarioParameter`
- Enums anlegen:
  - `AgentType`
  - `EventType`
  - `DistributionType`
- Konfigurationsdateien erstellen:
  - `simulation_config.json` (inkl. `scenario_parameters`)
  - `agents.json` (Consumer-Agent inkl. `population_config` mit Segmenten und Verteilungen)
  - `factors.json`
- Loader-Funktionen schreiben:
  - `load_simulation_config()`
  - `load_agents()`
  - `load_factors()`
  - `load_population_config()`
  - `build_initial_state()`
- Validierungslogik ergänzen:
  - Pflichtfelder prüfen
  - Faktor-IDs prüfen
  - Initialzustände prüfen
  - Segmentanteile prüfen (Summe = 1.0)
  - Verteilungsparameter validieren (gültige Typen, Parameterbereiche)
  - Szenarioparameter auf Pflichtfelder prüfen
- Gemeinsame Interface-Dokumentation erstellen

### Deliverables
- `src/models/`
- `src/models/population_models.py`
- `src/config_loader.py`
- `configs/simulation_config.json`
- `configs/agents.json`
- `configs/factors.json`
- `docs/interfaces.md`

### Abhängigkeiten
- Keine harte Abhängigkeit zu anderen Paketen
- Muss früh fertig werden, damit alle anderen dieselben Formate nutzen

### Wichtigster Output für andere
- stabile Klassennamen
- stabile JSON-Struktur
- Beispiel-Initial-State
- Populations- und Segmentkonfiguration als Referenz für AP2 (Prompt-Anreicherung)

---

## AP2 – Agentenlogik & Prompting
**Verantwortung:** Person B

### Ziel
Umsetzung der drei MVP-Agenten mit konsistenten Prompts und parserfreundlichem Ausgabeformat.

### Aufgaben
- Prompt-Strategie definieren:
  - System Prompt
  - Task Prompt
  - Output-Anweisung
- Prompts für folgende Agenten schreiben:
  - Konsumenten (inkl. segmentspezifischer Populationskontext)
  - Anbieter (inkl. Segment-Analyse der Consumer-Runde als Input)
  - Regulator
- Consumer-Prompt-Template mit Populationskontext:
  - Segmentdaten (Preiselastizität, Einkommensniveau, Umweltbewusstsein, Marktanteil) als strukturierten Kontext aufbereiten
  - LLM argumentiert segmentspezifisch über Reaktionen verschiedener Nachfragergruppen
  - `_build_population_context()` implementieren
- JSON-Ausgabeformat definieren (inkl. optionalem `segment_analysis`-Feld)
- Parsing-Logik implementieren:
  - rohe LLM-Antwort → `AgentResponse`
  - Extraktion von `EventLogEntry`-Rohdaten
  - Extraktion von `segment_analysis` (Consumer-Agent)
- Fehlerbehandlung definieren:
  - Parse-Fallback
  - Default-Response bei fehlerhaftem JSON
- `AgentNode` implementieren:
  - `_build_prompt()`
  - `_build_population_context()`
  - `_parse_response()`
  - `_create_event_entries()`
- Mit Mock-State testen (inkl. Populations-Kontext)
- Beispielantworten dokumentieren (inkl. segmentspezifische Consumer-Argumentation)

### Deliverables
- `src/nodes/agent_node.py`
- `src/prompts/consumer.md` (inkl. Segment-Kontext-Template)
- `src/prompts/provider.md`
- `src/prompts/regulator.md`
- `docs/agent_output_schema.md`

### Abhängigkeiten
- Nutzt Datenmodell aus AP1 (inkl. `PopulationConfig`, `ConsumerSegment`)
- Kann initial mit Mock-State arbeiten
- Muss nicht auf vollständigen Graph warten

### Wichtigster Output für andere
- Agenten liefern zuverlässig parsebare `AgentResponse`
- Consumer-Agent liefert segmentspezifische Analyse als Teil der Response
- definierte Event-Struktur für das Event-Log
- definierte Event-Struktur für das Event-Log

---

## AP3 – Simulationsgraph, Orchestrierung & Environment
**Verantwortung:** Person C

### Ziel
Aufbau des ausführbaren LangGraph-Workflows inklusive Rundenlogik, Simulationsuhr und Umweltaktualisierung.

### Aufgaben
- `OrchestratorNode` implementieren
- LangGraph-StateFlow aufbauen
- Node-Reihenfolge definieren:
  - Orchestrator
  - Consumer (mit Populationskontext)
  - Provider
  - Regulator
  - optional Market
  - Environment
- Abbruchbedingung implementieren
- Simulationsuhr integrieren
- Populations-Konfiguration in Setup-Phase laden und im State bereitstellen
- Szenarioparameter im State verwalten und als Prompt-Kontext verfügbar machen
- Consumer-Agent-Node: Populationsdaten und Szenarioparameter in Prompt-Kontext integrieren
- `EnvironmentNode` implementieren:
  - Events aggregieren
  - Rundensummary erzeugen (inkl. segmentspezifischer Reaktionen)
  - Faktorenzustände aktualisieren (unter Berücksichtigung heterogener Segmentreaktionen)
  - Uhr weiterschalten
  - `RoundResult` schreiben
- Faktor-Update-Regeln für MVP definieren
- Optional: `MarketAgentNode` minimal umsetzen
- `SimulationRunner` bauen
- End-to-end-Lauf mit Mock-Agenten testen (inkl. Populations-Kontext)

### Deliverables
- `src/nodes/orchestrator_node.py`
- `src/nodes/environment_node.py`
- `src/nodes/market_node.py` (optional/minimal)
- `src/simulation_runner.py`
- `docs/simulation_flow.md`

### Abhängigkeiten
- braucht Datenmodell aus AP1 (inkl. `PopulationConfig`, `ScenarioParameter`)
- kann Agenten zunächst mocken
- später Integration mit echter AgentNode aus AP2

### Wichtigster Output für andere
- laufender Simulationsloop
- definierter State-Fluss (inkl. Populationsdaten)
- Faktorupdate-Mechanik
- Szenarioparameter-Verwaltung

---

## AP4 – Output, CIB, Testing & Dokumentation
**Verantwortung:** Person D

### Ziel
Speicherung, Auswertung, Nachvollziehbarkeit und Abschlussdokumentation der Challenge 2.

### Aufgaben
- Output-Ordnerstruktur definieren
- Speicherroutinen implementieren:
  - `event_log.json`
  - `price_history.json`
  - `round_history.json`
  - `cib_matrix.json`
  - `segment_analysis.json`
  - `final_narrative.md`
  - `run_metadata.json`
- `CIBExtractorNode` implementieren
- MVP-CIB-Extraktion aus Event-Log / Round-Summary bauen
- Testfälle definieren:
  - Config-Laden (inkl. Populations-Konfiguration und Szenarioparameter)
  - State-Aufbau (inkl. Populationsdaten im State)
  - Segmentanteile-Validierung (Summe = 1.0)
  - Verteilungsparameter-Validierung (gültige Typen und Wertebereiche)
  - Agent-Output parsebar (inkl. segment_analysis)
  - mindestens 1 vollständiger Simulationslauf
- Traceability-Tabelle C1 → C2 erstellen
- Abschlussdokumentation für Challenge 2 verfassen (inkl. Populationsmodell und Preiselastizitäts-Konzepte)
- README/Run-Anleitung schreiben

### Deliverables
- `src/nodes/cib_extractor_node.py`
- `src/output_writer.py`
- `tests/`
- `docs/challenge2_report.md`
- `README.md`

### Abhängigkeiten
- kann mit Mock-Event-Logs starten
- braucht für finalen Test den integrierten Run aus AP3
- nutzt Datenmodell aus AP1 (inkl. Populationsmodelle)

### Wichtigster Output für andere
- Nachweis, dass das System funktioniert
- auswertbare Artefakte (inkl. segmentspezifische Analyse)
- Challenge-2-Dokumentation

---

# Minimierung von Blockaden

## Was muss ganz am Anfang gemeinsam entschieden werden?
Diese Punkte müssen am ersten Arbeitstag abgestimmt und danach nicht mehr ständig geändert werden:

### Freeze 1: Gemeinsame IDs
- Agenten-IDs
- Faktor-IDs
- Zustands-IDs
- EventType-Werte
- Segment-IDs
- DistributionType-Werte
- ScenarioParameter-IDs

### Freeze 2: Gemeinsame Datenformate
- `SimulationState`
- `AgentResponse` (inkl. `segment_analysis`)
- `EventLogEntry`
- `PopulationConfig` / `ConsumerSegment`
- `ScenarioParameter`

### Freeze 3: MVP-Umfang
- Markt-Agent drin oder nur minimal?
- wie viele Runden?
- welche Faktorwechsel sind im MVP erlaubt?
- CIB regelbasiert oder LLM-basiert?
- welche Konsumenten-Segmente und Verteilungen im MVP?
- welche Szenarioparameter konfigurierbar?

Wenn diese 3 Dinge früh feststehen, könnt ihr fast parallel arbeiten.

---

# Empfohlene Projektstruktur

```text
project/
│
├── configs/
│   ├── simulation_config.json
│   ├── agents.json
│   └── factors.json
│
├── docs/
│   ├── interfaces.md
│   ├── simulation_flow.md
│   ├── agent_output_schema.md
│   └── challenge2_report.md
│
├── src/
│   ├── models/
│   │   ├── state_models.py
│   │   ├── population_models.py
│   │   ├── enums.py
│   │   └── __init__.py
│   │
│   ├── nodes/
│   │   ├── orchestrator_node.py
│   │   ├── agent_node.py
│   │   ├── market_node.py
│   │   ├── environment_node.py
│   │   ├── cib_extractor_node.py
│   │   └── __init__.py
│   │
│   ├── prompts/
│   │   ├── consumer.md
│   │   ├── provider.md
│   │   └── regulator.md
│   │
│   ├── config_loader.py
│   ├── output_writer.py
│   ├── simulation_runner.py
│   └── llm_client.py
│
├── tests/
│   ├── test_config_loader.py
│   ├── test_agent_parsing.py
│   ├── test_population_config.py
│   ├── test_environment_updates.py
│   └── test_end_to_end.py
│
└── README.md