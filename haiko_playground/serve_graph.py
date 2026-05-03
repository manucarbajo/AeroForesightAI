"""Ein kleines Flask-Server-Beispiel, das `graph.json` unter `/graph` liefert.

Installation (falls Flask fehlt):
    pip install flask

Start:
    python serve_graph.py

Dann im Browser öffnen: http://127.0.0.1:5000/graph
"""
from pathlib import Path
from flask import Flask, send_file, abort

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
GRAPH = ROOT / "graph.json"

@app.route("/graph")
def graph():
    if GRAPH.exists():
        return send_file(GRAPH)
    abort(404)

if __name__ == "__main__":
    app.run(debug=True)
