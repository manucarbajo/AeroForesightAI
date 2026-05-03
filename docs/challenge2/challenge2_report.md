# Challenge 2 – Abschlussbericht

## Projektübersicht

| Attribut | Wert |
|----------|------|
| **Projekt** | Prototypische Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr |
| **Challenge** | C2 – Technische Operationalisierung |
| **Domäne** | System Flugverkehr (2025–2035) |
| **Technischer Stack** | Python, LangGraph, Ollama (llama3.2:3b) |
| **Simulationsrunden** | 10 |
| **Stand** | MVP vollständig implementiert und getestet |

---

## 1. Zielsetzung

Ziel von Challenge 2 war die technische Operationalisierung der in Challenge 1 definierten Domänenrepräsentation. Es wurde ein lauffähiger MVP-Prototyp in Python implementiert, der:

- die 3 MVP-Akteure (Konsument, Anbieter, Regulatorien) als LLM-gesteuerte Agenten modelliert
- heterogene Konsumentenpopulationen über Segmente mit stochastischen Verteilungen abbildet
- konfigurierbare Szenarioparameter als steuerbare Inputs bereitstellt
- die 7 Einflussfaktoren (F1–F7) und ihre Zustände im State verwaltet
- über 10 Simulationsrunden läuft
- ein vollständiges Event-Log erzeugt
- den Umweltzustand aktualisiert
- Ergebnisse lokal speichert
- eine prototypische CIB-Nachverarbeitung ermöglicht

---

## 2. Technische Umsetzung

### 2.1 Architektur

Der Simulationsloop folgt einer festen Node-Reihenfolge pro Runde:
```
Orchestrator → Consumer → Provider → Regulator → Market → Environment
                                                              ↓
                                                    (nächste Runde)
                                                              ↓
                                                    CIBExtractorNode
                                                              ↓
                                                    Ergebnisse speichern
```


Jeder Node empfängt den vollständigen `SimulationState`, modifiziert ihn und gibt ihn weiter. Der State ist die einzige Wahrheitsquelle im System.

### 2.2 Implementierte Komponenten

| Komponente | Beschreibung | Datei |
|------------|--------------|-------|
| `SimulationState` | Zentraler State (Pydantic BaseModel) | `src/models/state_models.py` |
| `AgentNode` | Parametrisierter LLM-Agent | `src/nodes/agent_node.py` |
| `EnvironmentNode` | Faktoraktualisierung + Rundensummary | `src/nodes/environment_node.py` |
| `MarketNode` | Preisbildung aus Event-Log | `src/nodes/market_node.py` |
| `OrchestratorNode` | Rundensteuerung | `src/nodes/orchestrator_node.py` |
| `CIBExtractorNode` | CIB-Extraktion aus Event-Log | `src/nodes/cib_extractor_node.py` |
| `output_writer` | Speicherroutinen für alle Outputs | `src/output_writer.py` |
| `config_loader` | JSON-Konfiguration laden | `src/config_loader.py` |
| `validation` | Validierungslogik | `src/validation.py` |

### 2.3 Datenmodell

Das Datenmodell aus Challenge 1 wurde weitgehend wie spezifiziert umgesetzt. Abweichungen:

| C1 Spezifikation | C2 Umsetzung | Begründung |
|------------------|--------------|------------|
| `TypedDict` für SimulationState | Pydantic `BaseModel` | Validierung + `.model_dump()` |
| `decisions` in AgentResponse | `actions` | Präziserer Begriff |
| `factor_assessments` in AgentResponse | `state_changes` | Klarer für vorgeschlagene Faktoränderungen |
| Irreversible Faktor-Wechsel | Reversible Wechsel möglich | Flexiblere Simulation |

### 2.4 Populationsmodell

Der Consumer-Agent wurde mit einem heterogenen Populationsmodell ausgestattet:

- Konsumentensegmente mit individuellen Eigenschaften (Preiselastizität, Einkommensniveau, Umweltbewusstsein)
- Stochastische Verteilungen (Normal, Uniform) pro Segment
- Segmentspezifische Analyse in jeder Consumer-Response
- Segment-Kontext wird als strukturierter Prompt-Block an den LLM übergeben

---

## 3. Outputs

Nach jedem Simulationslauf werden folgende Dateien in `outputs/` gespeichert:

| Datei | Inhalt |
|-------|--------|
| `event_log.json` | Alle Events aller Agenten pro Runde |
| `price_history.json` | Preisentwicklung über alle Runden |
| `round_history.json` | Vollständige Rundenhistorie |
| `segment_analysis.json` | Segmentspezifische Reaktionen pro Runde |
| `cib_matrix.json` | Cross-Impact-Bilanz aus dem Event-Log |
| `final_narrative.md` | Lesbare Markdown-Zusammenfassung |
| `run_metadata.json` | Metadaten des Simulationslaufs |

---

## 4. Testergebnisse

Die Testabdeckung umfasst 41 Tests in 6 Testdateien:

| Testdatei | Tests | Fokus |
|-----------|-------|-------|
| `test_config_loader.py` | 6 | Konfiguration laden, State aufbauen |
| `test_population_config.py` | 7 | Segmentanteile, Verteilungsparameter |
| `test_agent_parsing.py` | 8 | AgentResponse, StateChange, Parsing |
| `test_environment_updates.py` | 4 | Faktoraktualisierung, RoundResult |
| `test_end_to_end.py` | 4 | Vollständiger Simulationslauf ohne LLM |
| `test_agent_node.py` | 12 | Prompting, Parsing, Segment-Analyse |
| **Gesamt** | **41** | **alle passing** |

---

## 5. Simulationsergebnisse

### 5.1 Beobachtetes Endszenario

Bei wiederholten Simulationsläufen mit `llama3.2:3b` über 10 Runden zeigt sich ein konsistentes Muster im Endzustand der Einflussfaktoren:

| Faktor | Häufigster Endzustand | Bewertung |
|--------|----------------------|-----------|
| F1 – Mobilitätsbedürfnis | F1.2 – Stagnation und Verzicht, Substitution | Konsistent |
| F2 – Regulatorische Strenge | F2.2 – Radikale Dekarbonisierung, Verbote | Konsistent |
| F3 – Technologische Reife | F3.2 – Durchbruch bei SAF/E-Fuels/H2 | Konsistent |
| F4 – Wirtschaftliche Entwicklung | F4.1 oder F4.2 | **Variabel** |
| F5 – Verfügbarkeit von Alternativen | F5.2 – Massiver Schienenausbau, Intermodalität | Konsistent |
| F6 – Gesellschaftlicher Wertewandel | F6.2 – Starkes Klimabewusstsein, Flight Shaming | Konsistent |
| F7 – Geopolitische Stabilität | F7.1 – Offene Märkte, Kooperation | Konsistent |

### 5.2 Interpretation

Das emergente Endszenario beschreibt eine **Transformationswelt**:

- Gesellschaftlicher Wertewandel (F6.2) treibt strengere Regulierung (F2.2)
- Regulierung fördert technologischen Durchbruch (F3.2)
- Verfügbare Alternativen (F5.2) und Wertewandel reduzieren Nachfrage (F1.2)
- Geopolitische Stabilität (F7.1) ermöglicht internationale Kooperation bei Dekarbonisierung

Diese Kausalkette ist inhaltlich plausibel und deckt sich mit realen Zukunftsszenarien für den Flugverkehr.

### 5.3 Variabilität der Wirtschaftlichen Entwicklung (F4)

F4 zeigte als einziger Faktor keine konsistente Tendenz. Mögliche Erklärungen:

- F4 wird von mehreren Faktoren beeinflusst (F7, Energiepreise) → höhere Unsicherheit
- `llama3.2:3b` argumentiert bei wirtschaftlichen Zusammenhängen weniger konsistent
- F4 ist der einzige Faktor ohne klare normative Präferenz im Modell

### 5.4 Preisentwicklung

Der Marktpreis entwickelt sich dynamisch über die Runden, abhängig von Provider-Events mit Prozentangaben. Die Preisrichtung (Erhöhung/Senkung) wird korrekt aus der Event-Beschreibung abgeleitet.

---

## 6. Bekannte Limitationen

| Limitation                     | Beschreibung                                                           | Geplante Adressierung                      |
|--------------------------------|------------------------------------------------------------------------|--------------------------------------------|
| Sequentieller Informationsbias | Consumer hat keinen Kontext der aktuellen Runde, Regulator sieht alles | Fan-Out/Fan-In in späterer Iteration       |
| Modellabhängigkeit             | `llama3.2:3b` neigt zu repetitiven Antworten bei vielen Runden         | Größere Modelle testen                     |
| Nicht-deterministisch          | Bei Temperature > 0 variieren Ergebnisse                               | Temperature = 0 für Reproduzierbarkeit     |
| Context-Window                 | Lokale Modelle haben begrenzte Kontextlänge                            | Round-Summaries statt Rohdaten als Kontext |
| Fallback-Events                | Bei Parse-Fehlern entstehen generische Events ohne Prozentangaben      | Prompt-Optimierung, robusteres Parsing     |

---

## 7. Nächste Schritte

| Priorität  | Maßnahme                                            | Begründung                                |
|------------|-----------------------------------------------------|-------------------------------------------|
| Hoch       | Weitere Modelle testen (llama3.1:8b, mistral, qwen) | F4-Variabilität und Konsistenz beobachten |
| Hoch       | Temperature = 0 Vergleichsläufe                     | Reproduzierbarkeit prüfen (NFA-02)        |
| Mittel     | Fan-Out/Fan-In für Agenten                          | Informationsbias reduzieren               |
| Mittel     | CIB-Extraktion mit LLM                              | Qualitativere Wechselwirkungsbewertung    |
| Niedrig    | Mehr als 2 Zustände pro Faktor                      | Granularere Szenarioentwicklung           |
| Niedrig    | Reversibilitätsschwellen für Faktorwechsel          | Oszillationen abbilden                    |

---

## 8. Fazit

Challenge 2 liefert einen funktionsfähigen MVP-Prototypen, der alle definierten Anforderungen aus Challenge 1 umsetzt. Die Simulation erzeugt inhaltlich plausible, konsistente Szenarien für den Flugverkehr 2025–2035. Das Endszenario ist methodisch nachvollziehbar und deckt sich mit realen Expertenmeinungen zur Zukunft des Flugverkehrs.

Der nächste Schritt ist das systematische Testen verschiedener LLM-Modelle, um die Robustheit der Ergebnisse zu validieren und die Variabilität bei F4 besser zu verstehen.
