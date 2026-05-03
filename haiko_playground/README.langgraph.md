LangGraph Integration (haiko_playground)

Ziel: `langgraph dev` im `haiko_playground`-Ordner soll das interaktive Projekt starten.

Vorbedingungen:
- `langgraph` CLI v0.4.24 installiert
- Python-Umgebung aktiviert
- Für echte LLM-Integration: dein lokaler Llama-HTTP-Server erreichbar oder `transformers` installiert

Konfiguration für dein lokales `llama3.2`:
- **Empfohlen (Ollama direkt):**
  - `OLLAMA_MODEL` -> z.B. `llama3.2`
  - optional `OLLAMA_BASE_URL` -> default ist `http://127.0.0.1:11434`
- Wenn du einen HTTP-Endpoint verwendest (z.B. `llama.cpp`-server, oder eigenes Frontend), setze:
  - `LLAMA_HTTP_URL` → z.B. `http://127.0.0.1:8080/generate`
- Wenn du `transformers`-based local model verwendest, setze:
  - `LLAMA_TRANSFORMERS_MODEL` → Pfad/zName des lokalen Modells

Starten:
1) Wechsle in den Playground-Ordner:
```powershell
cd haiko_playground
```
2) Starte LangGraph Dev:
```powershell
langgraph dev
```

Hinweis:
- `graph.py` exportiert ein kompiliertes `StateGraph`-Objekt. LangGraph CLI sollte dieses in den meisten Setups laden — falls CLI in deiner Version ein anderes Entry-Pattern erwartet, sag Bescheid, dann passe ich `pyproject`/`langgraph`-Manifest an.
- Wenn langgraph beim Importieren von `haiko_playground.graph` einen Fehler meldet, kannst du die Fehlerursache mit:
```python
python -c "import haiko_playground.graph as g; print(getattr(g, 'get_build_error')() )"
```
- Wenn du möchtest, passe ich die Integration so an, dass `langgraph dev` direkt aus dem Repo-Root funktioniert.

Environment file
----------------
Erstelle eine Datei `.env` im Ordner `haiko_playground` (oder kopiere `.env.template`) mit deiner Konfiguration:

```
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=       # wenn leer, wird bei langgraph dev interaktiv (versteckt) abgefragt
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com

# Wähle EINE der folgenden Optionen für dein lokales Llama-Modell:
OLLAMA_MODEL=llama3.2
# optional:
OLLAMA_BASE_URL=http://127.0.0.1:11434

# oder
LLAMA_HTTP_URL=http://127.0.0.1:8080/generate
# oder
LLAMA_TRANSFORMERS_MODEL=/path/to/llama3.2-model
```

**Hinweise:**
- `LANGSMITH_API_KEY` wird **nur** abgefragt, wenn leer/nicht gesetzt. Die Eingabe wird versteckt (getpass).
- `OLLAMA_MODEL`, `LLAMA_HTTP_URL` und `LLAMA_TRANSFORMERS_MODEL` werden **nicht** abgefragt — diese laden Sie direkt aus `.env` oder setzen sie lokal. Falls nichts gesetzt ist, nutzt der Graph einen Mock-LLM.
- Committe niemals dein echtes `.env` (mit echten API-Keys) in das Repository.
