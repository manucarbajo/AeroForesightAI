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

Studio: `build_options` & `default_payload`
-----------------------------------------
Das Projekt exportiert in `graph.py` zusätzlich zwei Hilfs-Objekte, die LangGraph Studio das Konfigurieren erleichtern:

- `default_payload`: Ein vollständiges Start-`SimulationState` JSON, das beim Start in Studio vorausgefüllt wird. Du findest es in `haiko_playground/langgraph.json`.
- `build_options`: Ein kompaktes Objekt mit häufig genutzten Feldern (z.B. `max_rounds`, `llm_model`, `llm_temperature`, `scenario_parameters`, `agents`). Studio zeigt `default_payload` im Run-Input an; `build_options` kann als Orientierung oder zur schnellen UI-Integration genutzt werden.

Wie nutze ich das in Studio?

1. Öffne `langgraph dev` im `haiko_playground`-Ordner.
2. Im Studio-Fenster siehst du links das Run-Input JSON (voreingestellt mit `default_payload`).
3. Zum schnellen Ändern der Rundenzahl kannst du entweder das JSON-Feld editieren:

```json
{ "clock": { "max_rounds": 5 } }
```

oder die Kurzform verwenden:

```json
{ "max_rounds": 5 }
```

4. Willst du Szenarioparameter oder Agenteneigenschaften ändern, editiere `default_payload.config.scenario_parameters` oder den entsprechenden `agents`-Block direkt im Run-Input.

5. Starte den Run — am Ende des Laufs wird `cib_matrix` berechnet und im Result-JSON unter `cib_matrix` erscheinen (sofern Events vorhanden sind).

Tipp: Wenn `cib_matrix` weiterhin `null` ist, prüfe, ob während der konfigurierten Runden Events im `event_log` erzeugt wurden; ohne Events kann die CIB-Extraktion keine Einträge ableiten.
