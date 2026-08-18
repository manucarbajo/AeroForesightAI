LangGraph Studio (`langgraph_studio/`)

Ziel: interaktive Graph-Visualisierung und Debugging — dieselbe Pipeline wie `src/run_simulation.py`.

## Starten

**Empfohlen (ein Einstieg über die CLI):**

```powershell
python src/run_simulation.py --studio
```

**Alternativ direkt im Studio-Ordner:**

```powershell
cd langgraph_studio
langgraph dev
```

## Konfiguration

Minimale `.env` für Ollama:
```
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_API_KEY=YourKeyHere123456789
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

Die CLI lädt diese `.env` automatisch mit (`src/studio_helpers.py`).

## Batch-Lauf vs. Studio

| Modus | Befehl | Zweck |
| --- | --- | --- |
| Batch | `python src/run_simulation.py --mock-llm --rounds 2` | Vollständiger Lauf, Outputs unter `outputs/<run_id>/` |
| Studio | `python src/run_simulation.py --studio` | Interaktiv, Tick für Tick im Graph |

Beide nutzen dieselben Agenten und Nodes; Studio zeigt **consumer / provider / regulator** als eigene Graph-Knoten (Redebedarf-Routing über `determine_next_speaker`). Die Batch-CLI fasst die Agenten in `RoundExecutionNode` zusammen.

## Fehlerdiagnose

```powershell
python -c "import langgraph_studio.graph as g; print(getattr(g, 'get_build_error')())"
```

### `HTTP 404: Thread or assistant not found`

Das passiert meist nach einem **Server-Neustart** oder **Graph-Umbau** — der Browser zeigt noch einen alten Thread.

1. Studio stoppen (Ctrl+C)
2. Cache löschen:
   ```powershell
   Remove-Item -Recurse -Force langgraph_studio\.langgraph_api
   ```
3. Neu starten: `python src/run_simulation.py --studio`
4. Im Browser: **neuen Thread** starten (nicht alten Tab/Link öffnen), Seite hart neu laden (Ctrl+F5)

Optional in `langgraph_studio/.env`:
```
LANGCHAIN_TRACING_V2=false
```
