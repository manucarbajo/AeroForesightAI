# Challenge 2 – Multi-Agenten-Simulation Flugverkehr

Prototypische Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr (2025–2035).  
Drei LLM-gesteuerte Agenten (Konsument, Anbieter, Regulatorien) simulieren Marktdynamiken über mehrere Runden.

---

## Voraussetzungen

| Tool | Version | Beschreibung |
|------|---------|--------------|
| Python | ≥ 3.11 | Programmiersprache |
| Ollama | aktuell | Lokaler LLM-Server |
| llama3.2 | – | Empfohlenes Modell |

### Ollama installieren & Modell laden

```bash
# Ollama installieren (macOS)
brew install ollama

# Modell herunterladen
ollama pull llama3.2

# Ollama starten
ollama serve

```

## Installation
### Repository klonen
git clone <repo-url>
cd "Technology Lab"

### Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

### Abhängigkeiten installieren
pip install -r requirements.txt

## Simulation starten
### Standardlauf (10 Runden, llama3.2)
python src/run_simulation.py

### Mit eigenen Parametern
python src/run_simulation.py --rounds 5 --model llama3.2 --temperature 0.7

### Ohne Markt-Node
python src/run_simulation.py --rounds 5 --no-market

### Reduzierte Konsolenausgabe
python src/run_simulation.py --rounds 5 --quiet


## Parameterliste
| Parameter       | Default                       | Beschreibung               |
|-----------------|-------------------------------|----------------------------|
| --model         | llama3.2                      | Ollama Modellname          |
| --base-url      | http://localhost:11434        | Ollama Server URL          |
| --temperature.2 | 0.7                           | LLM Temperatur (0.0–1.0)   |
| --max-tokens    | 2048                          | Max. Tokens pro Antwort    |
| --rounds        | aus simulation_config.json    | Anzahl Simulationsrunden)  |
| --no-market     | False                         | MarketNode deaktivieren    |
| --quiet         | False                         | Weniger Konsolenausgabe    |

## Ausgabe
| Parameter             | Inhalt                                  |
|-----------------------|-----------------------------------------|
| event_log.json        | Alle Events aller Agenten pro Runde     |
| price_history.json    | Preisentwicklung über alle Runden       |
| round_history.json    | Vollständige Rundenhistorie             |
| segment_analysis.json | Segmentspezifische Reaktionen pro Runde |
| cib_matrix.json       | Cross-Impact-Bilanz aus dem Event-Log   |
| final_narrative.md    | Lesbare Markdown-Zusammenfassung        |
| run_metadata.json     | Metadaten des Simulationslaufs          |

## Konfiguration
Alle Parameter sind über JSON-Dateien in configs/ steuerbar:

| Datei                  | Inhalt                                                      |
|------------------------|-------------------------------------------------------------|
| simulation_config.json | Rundenzahl, Zeitraum, LLM-Einstellungen, Szenarioparameter  |
| agents.json            | Agenten-Definitionen, Ziele, Constraints, Populationsmodell |
| factors.json           | 7 Einflussfaktoren mit Zuständen                            |

## Projektstruktur
```
project/
├── configs/
│   ├── simulation_config.json
│   ├── agents.json
│   └── factors.json
├── docs/
│   ├── interfaces.md
│   ├── simulation_flow.md
│   ├── agent_output_schema.md
│   ├── challenge2_report.md
│   └── traceability_c1_c2.md
├── outputs/ # wird automatisch erstellt
├── src/
│   ├── models/
│   ├── nodes/
│   ├── prompts/
│   ├── config_loader.py
│   ├── output_writer.py
│   ├── validation.py
│   └── run_simulation.py
├── tests/
└── README.md
```

## Simulationsablauf
```
Orchestrator → Consumer → Provider → Regulator → Market → Environment
                                                              ↓
                                                    (nächste Runde)
                                                              ↓
                                                    CIBExtractorNode
                                                              ↓
                                                    Ergebnisse speichern
```

## Bekannte Limitationen im aktuellen Stand
## Ausgabe
| Limitation                     | Beschreibung                                                           |
|--------------------------------|------------------------------------------------------------------------|
| Sequentieller Informationsbias | Consumer hat keinen Kontext der aktuellen Runde, Regulator sieht alles |
| LLM-Abhängigkeit               | Qualität der Simulation hängt vom verwendeten Modell ab                |
