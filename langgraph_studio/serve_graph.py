"""Ein kleines Flask-Server-Beispiel, das `graph.json` unter `/graph` liefert.

Installation (falls Flask fehlt):
    pip install flask

Start:
    python serve_graph.py

Dann im Browser öffnen: http://127.0.0.1:5000/graph
"""

import sys
from pathlib import Path

from flask import Flask, abort, send_file

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "graph.json"

# **Nach dem `sys.path`-Eingriff, nicht davor** — dieselbe Reihenfolge wie in
# `create_graph.py` und `test_run.py`. Dieses Skript wird aus einem beliebigen
# Arbeitsverzeichnis gestartet (der Docstring sagt `python serve_graph.py`), und
# `src` liegt dort nicht auf dem Pfad. Beim ersten Anlauf von P3.10 stand der
# Import oben und riss den Start mit `ModuleNotFoundError: No module named 'src'`
# ab.
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from src.logging_setup import stdio_auf_utf8  # noqa: E402


@app.route("/graph")
def graph():
    if GRAPH.exists():
        return send_file(GRAPH)
    abort(404)


if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    app.run(debug=True)
