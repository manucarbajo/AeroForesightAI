"""Auslieferung von Run-Artefakten (PNG-Figures, Downloads) über Flask.

Dash serviert nur den `assets/`-Ordner. Die Run-Ausgaben liegen aber unter
`outputs/` und entstehen zur Laufzeit — dafür braucht es eine eigene Route.
Jeder angefragte Pfad wird gegen das Outputs-Verzeichnis geprüft, damit von
außen nichts anderes aus dem Dateisystem gelesen werden kann.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from flask import Flask, abort, send_file

from dashboard.run_browser import outputs_root

ROUTE_PREFIX = "/run-file"


def resolve_within_outputs(relative_path: str) -> Path:
    """Relativen Pfad auflösen und sicherstellen, dass er unter `outputs/` bleibt."""

    root = outputs_root().resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Pfad liegt außerhalb von {root}: {relative_path}")
    return candidate


def run_file_url(absolute_path: Path | str, *, download: bool = False) -> str:
    """URL für eine Datei unterhalb von `outputs/` bauen.

    Liegt die Datei außerhalb, wird ein leerer String zurückgegeben — der
    Aufrufer zeigt dann einen Hinweis statt eines toten Links.
    """

    root = outputs_root().resolve()
    path = Path(absolute_path).resolve()
    if not path.is_relative_to(root):
        return ""
    relative = path.relative_to(root).as_posix()
    url = f"{ROUTE_PREFIX}/{quote(relative)}"
    return f"{url}?download=1" if download else url


def register(server: Flask) -> None:
    """Route am Flask-Server der Dash-App anmelden."""

    @server.route(f"{ROUTE_PREFIX}/<path:relative_path>")
    def serve_run_file(relative_path: str):  # pragma: no cover - dünner Flask-Wrapper
        from flask import request

        try:
            target = resolve_within_outputs(relative_path)
        except ValueError:
            abort(403)
        if not target.is_file():
            abort(404)
        return send_file(
            target,
            as_attachment=request.args.get("download") == "1",
            download_name=target.name,
            max_age=0,
        )
