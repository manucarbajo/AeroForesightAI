"""Echte Anfragen an den Server, nicht nur gebaute Layouts.

Die übrigen Tests bauen Komponenten und prüfen deren Inhalt. Damit bleibt
alles unentdeckt, was erst beim Ausliefern schiefgeht: ein falsch gesetztes
Präfix, eine nicht angemeldete Route, ein Pfad, der aus seinem Ordner
herausführt. Hier läuft deshalb der Flask-Testclient gegen die fertige App.
"""

from __future__ import annotations

import json

import pytest

from dashboard.run_browser import outputs_root
from dashboard.web import app as web_app


@pytest.fixture(scope="module")
def client():
    web_app.app.server.config.update(TESTING=True)
    return web_app.app.server.test_client()


# --- Landingpage -----------------------------------------------------------


def test_the_root_serves_the_landing_page(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "AeroForesight AI" in body
    assert 'id="problem"' in body, "Landingpage statt Dashboard erwartet"


def test_the_landing_page_links_into_the_app(client):
    body = client.get("/").get_data(as_text=True)

    assert 'href="/app/"' in body
    assert "localhost:8511" not in body, "keine feste Adresse mehr"


@pytest.mark.parametrize(
    "page", ["demo-anfragen.html", "impressum.html", "datenschutz.html", "agb.html"]
)
def test_the_other_landing_pages_are_served(client, page):
    assert client.get(f"/{page}").status_code == 200


def test_an_unknown_page_is_not_found(client):
    assert client.get("/gibt-es-nicht.html").status_code == 404


def test_no_file_outside_the_landing_folder_is_served(client):
    """Der Ordner darf keine Tür zum übrigen Dateisystem sein."""

    for versuch in ("/../pyproject.toml", "/..%2fpyproject.toml", "/....//pyproject.toml"):
        assert client.get(versuch).status_code in (301, 308, 400, 404)


# --- Dashboard -------------------------------------------------------------


def test_the_app_is_served_under_its_prefix(client):
    response = client.get("/app/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "AeroForesight AI" in body
    assert "react-entry-point" in body, "Dash-Grundgerüst erwartet"


def test_deep_links_into_the_app_work(client):
    """`/app/doku/cib` muss direkt aufrufbar sein, nicht nur per Klick."""

    for path in ("/app/runs", "/app/doku", "/app/doku/cib"):
        assert client.get(path).status_code == 200, path


def test_the_layout_is_delivered(client):
    response = client.get("/app/_dash-layout")

    assert response.status_code == 200
    payload = json.loads(response.get_data(as_text=True))
    assert payload, "leeres Layout"


def test_the_callbacks_are_registered(client):
    response = client.get("/app/_dash-dependencies")

    assert response.status_code == 200
    payload = json.loads(response.get_data(as_text=True))
    assert len(payload) > 10, "zu wenige Callbacks angemeldet"


def test_the_stylesheet_is_served(client):
    """Ohne das eigene CSS sieht die Anwendung aus wie rohes HTML."""

    body = client.get("/app/").get_data(as_text=True)

    assert "dashboard.css" in body


# --- Run-Dateien -----------------------------------------------------------


def test_run_files_outside_the_outputs_folder_are_refused(client):
    response = client.get("/run-file/../pyproject.toml")

    assert response.status_code in (301, 308, 400, 403, 404)


def test_a_missing_run_file_is_not_found(client):
    assert client.get("/run-file/gibt-es-nicht/datei.png").status_code == 404


def test_an_existing_run_file_is_delivered(client):
    """Eine Datei unter `outputs/` muss auch wirklich herauskommen."""

    root = outputs_root()
    root.mkdir(parents=True, exist_ok=True)
    probe = root / "test_web_server_probe.txt"
    probe.write_text("hallo", encoding="utf-8")
    try:
        response = client.get("/run-file/test_web_server_probe.txt")
        status, inhalt = response.status_code, response.get_data(as_text=True)
        # Unter Windows haelt `send_file` die Datei offen, bis die Antwort
        # geschlossen ist — sonst scheitert das Aufraeumen.
        response.close()

        assert status == 200
        assert inhalt == "hallo"
    finally:
        probe.unlink(missing_ok=True)
