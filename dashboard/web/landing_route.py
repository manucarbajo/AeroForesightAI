"""Die Landingpage aus derselben Anwendung ausliefern.

Sie ist bewusst statisches HTML geblieben und wird nicht in Dash-Komponenten
übersetzt: Es sind fünf fertige Seiten ohne lokale Dateien — Schriften und
Tailwind kommen vom CDN, alle Illustrationen sind Inline-SVG. Sie hier
einzubinden heißt deshalb nur, sie zu servieren.

Der Gewinn ist der Einstieg: `python -m dashboard.web.app` startet einen
Server, und wer die Adresse öffnet, landet auf der Landingpage und kommt von
dort ins Dashboard. Kein zweiter Dienst, keine fest verdrahtete Portnummer.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, send_from_directory

LANDING_DIR = Path(__file__).resolve().parents[2] / "aeroforesight-ai-landing-page"


def available_pages() -> set[str]:
    """Welche Seiten es gibt — Grundlage der Zugriffsprüfung."""

    if not LANDING_DIR.is_dir():
        return set()
    return {path.name for path in LANDING_DIR.glob("*.html")}


def register(server: Flask) -> None:
    """Landingpage auf `/` und ihre Unterseiten anmelden."""

    @server.route("/")
    def landing_index():  # pragma: no cover - dünner Flask-Wrapper
        if "index.html" not in available_pages():
            abort(404)
        return send_from_directory(LANDING_DIR, "index.html")

    @server.route("/<page>.html")
    def landing_page(page: str):  # pragma: no cover - dünner Flask-Wrapper
        # Gegen die tatsächlich vorhandenen Dateien prüfen statt gegen ein
        # Muster: So kann kein Pfad nach außerhalb des Ordners zeigen.
        name = f"{page}.html"
        if name not in available_pages():
            abort(404)
        return send_from_directory(LANDING_DIR, name)
