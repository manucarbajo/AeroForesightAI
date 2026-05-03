haiko_playground
===============

Ziel: Minimaler Workspace, mit dem du die Node-Topologie der Simulation lokal erzeugen und im Browser betrachten kannst (z.B. in LangGraph Studio oder einem beliebigen Graph-Importer).

Dateien:
- `create_graph.py` — erzeugt `graph.json` mit einer einfachen Node/Edge-Definition.
- `graph.json` — Beispielgraph (Orchestrator → Consumer → Provider → Regulator → Market → Environment).
- `serve_graph.py` — kleines Flask-Beispiel, das `graph.json` unter `/graph` ausliefert.

Schnellstart:
1) Repo-Root öffnen und virtuelle Umgebung aktivieren (PowerShell):

```powershell
& .\.venv\Scripts\Activate.ps1
```

2) `create_graph.py` ausführen (erzeugt/überschreibt `graph.json`):

```powershell
python haiko_playground\create_graph.py
```

3a) LangGraph Studio (wenn möglich):
- Öffne LangGraph Studio im Browser.
- Prüfe, ob Studio einen Import für JSON-Graphen anbietet (oder "Open from URL").
- Wenn ja, importiere `haiko_playground/graph.json` oder nutze `http://localhost:5000/graph` nach Schritt 3b.

3b) Alternativ: lokalen HTTP-Server starten und die URL in Studio/anderen Tools laden:

```powershell
pip install flask
python haiko_playground\serve_graph.py
# öffne http://127.0.0.1:5000/graph im Browser oder importiere die URL in LangGraph Studio
```

Hinweise:
- Dieses Beispiel ist absichtlich generisch — LangGraph Studio hat eigene Importformate; passe `create_graph.py` ggf. an, falls ein spezifisches Format benötigt wird.
- Wenn du mir sagst, wie du LangGraph Studio genau verwendest (z.B. welche Import-Funktion oder API), passe ich `graph.json` an das benötigte Format an.
