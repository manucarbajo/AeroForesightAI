# Simulation Flow (AP3)

## Ziel
Dieses Dokument beschreibt den MVP-Simulationsablauf (LangGraph-StateFlow) fuer Challenge 2.
Es definiert die Node-Reihenfolge, den State-Fluss und die MVP-Regeln fuer Environment-Updates.

---

## Node-Reihenfolge (MVP)
Reihenfolge innerhalb einer Runde:

1. `OrchestratorNode`
2. `AgentNode` (Consumer)
3. `AgentNode` (Provider)
4. `AgentNode` (Regulator)
5. `MarketNode` (optional/minimal)
6. `EnvironmentNode`

Abbruchbedingung:
- Simulation endet, wenn `state.clock.current_round >= state.clock.max_rounds`.

---

## State-Fluss
Top-Level-State ist `SimulationState` (Pydantic v2 `BaseModel`).
Die Nodes reichern den State an und geben ihn weiter.

Wichtige Felder:
- `state.clock.current_round`: aktuelle Runde (wird im `OrchestratorNode` inkrementiert)
- `state.event_log`: akkumuliertes, unverändertes Log aller Events (Append-only)
- `state.environment.factors`: aktuelle Faktor-Zustaende (`current_state`)
- `state.round_results`: Rundenergebnisse (AP2 schreibt pro Agent bereits Eintraege; AP3 aggregiert pro Runde zusaetzlich)
- `state.price_history`: minimaler Preisverlauf (optional ueber `MarketNode`)

---

## OrchestratorNode
Aufgabe:
- Start einer neuen Runde (`current_round += 1`), solange `current_round < max_rounds`.

MVP-Design:
- feste Reihenfolge der Agenten (`consumer -> provider -> regulator`)
- keine dynamische Routing-Logik

---

## AgentNode (Consumer/Provider/Regulator)
Aufgabe:
- Prompt bauen (inkl. Faktoren, letzte Events, Szenarioparameter)
- LLM aufrufen
- Output parsen zu `AgentResponse` + `EventLogEntry[]`
- Events ans `event_log` anhaengen

Hinweis:
- Der Consumer kann optional `segment_analysis` liefern (siehe `docs/challenge2/agent_output_schema.md`).

---

## MarketNode (optional/minimal)
Aufgabe (MVP-Heuristik):
- liest Runde-Events und aktualisiert einen einfachen Preis- und Nachfrageindikator
- schreibt `PriceHistoryEntry` und ein `market_event` ins `event_log`

---

## EnvironmentNode
Aufgabe:
- aggregiert AgentResponses und Events der aktuellen Runde
- aktualisiert Faktor-Zustaende im `EnvironmentState`
- erzeugt ein textuelles Rundensummary (inkl. `segment_analysis`, falls vorhanden)
- schreibt ein aggregiertes `RoundResult`

MVP-Regel fuer Faktor-Updates:
- `state_changes` aus den AgentResponses werden auf gueltige Faktor-IDs/Zustaende gefiltert
- pro Faktor wird der erste gueltige Vorschlag angewendet (Prioritaet: `regulator` vor `provider` vor `consumer`)

---

## Verweise
- Datenmodelle: `docs/interfaces.md`
- Agent Output Schema: `docs/challenge2/agent_output_schema.md`
- Nodes: `src/nodes/`
- Runner: `src/simulation_runner.py`

