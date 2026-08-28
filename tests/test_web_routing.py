"""Landingpage auf `/`, Dashboard auf `/app/` — aus einem Server.

Das Präfix zieht sich durch Navigation, Handbuch-Links und die Querverweise
in den Markdown-Kapiteln. Geht es an einer Stelle verloren, landet man auf
einer toten Adresse, ohne dass etwas abstürzt — deshalb hier festgehalten.
"""

from __future__ import annotations

import pytest

from dashboard.web import app as web_app  # noqa: F401  - baut die App und damit alle Routen
from dashboard.web import landing_route, routing, shell
from dashboard.web.pages import docs

# --- Pfade -----------------------------------------------------------------


def test_url_prefixes_internal_paths():
    assert routing.url() == "/app/"
    assert routing.url("runs") == "/app/runs"
    assert routing.url("/runs") == "/app/runs"
    assert routing.url("doku/cib") == "/app/doku/cib"


@pytest.mark.parametrize(
    ("pathname", "expected"),
    [
        ("/app/", ""),
        ("/app", ""),
        ("/app/runs", "runs"),
        ("/app/doku/cib", "doku/cib"),
        ("/app/doku/cib/", "doku/cib"),
        (None, ""),
        ("/", ""),
    ],
)
def test_relative_strips_the_prefix(pathname, expected):
    assert routing.relative(pathname) == expected


def test_landing_stays_at_the_root():
    """Der Verweis zurueck auf die Landingpage sitzt jetzt in der Kopfzeile.

    Mit dem Leitstand-Rahmen (P1.5) baut `shell` die Kopfzeile; `LANDING_URL`
    ist damit von `app` dorthin gewandert. Geprueft wird weiterhin dasselbe:
    dass der Verweis relativ bleibt und auf die Wurzel zeigt.
    """

    assert routing.LANDING_PATH == "/"
    assert shell.LANDING_URL == "/"


# --- Landingpage -----------------------------------------------------------


def test_the_landing_pages_are_present():
    pages = landing_route.available_pages()

    assert "index.html" in pages
    assert {"impressum.html", "datenschutz.html", "agb.html"} <= pages


def test_login_links_point_into_the_app():
    """Die Landingpage darf keine feste Portnummer mehr enthalten."""

    treffer = 0
    for path in sorted(landing_route.LANDING_DIR.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        assert "localhost:8511" not in text, f"feste Adresse in {path.name}"
        treffer += text.count('href="/app/"')

    assert treffer >= 5, "jede Seite sollte ins Dashboard verlinken"


# --- Handbuch --------------------------------------------------------------


def test_chapter_links_carry_the_prefix():
    assert docs.BY_SLUG["cib"].href == "/app/doku/cib"


def test_chapter_paths_are_understood_with_the_prefix():
    assert docs.slug_from_path("/app/doku/grenzen") == "grenzen"
    assert docs.slug_from_path("/app/doku/gibt-es-nicht") == docs.DEFAULT_SLUG


def test_cross_references_in_the_text_get_the_prefix():
    """In der Markdown-Datei steht `/doku/...`, im Browser muss `/app/doku/...` stehen."""

    rewritten = docs.with_prefix("Siehe [Grenzen](/doku/grenzen) und `/doku/` im Fließtext.")

    assert "](/app/doku/grenzen)" in rewritten
    # Nur Links werden umgeschrieben, kein beliebiger Text.
    assert "`/doku/` im Fließtext" in rewritten


def test_every_rendered_chapter_keeps_its_links_reachable():
    for chapter in docs.CHAPTERS:
        for target in docs.with_prefix(chapter.source()).split("](")[1:]:
            href = target.split(")")[0]
            if not href.startswith("/app/doku/"):
                continue
            assert href[len("/app/doku/") :] in docs.BY_SLUG, f"{chapter.slug} -> {href}"


# --- App -------------------------------------------------------------------


def test_dash_is_mounted_under_the_prefix():
    assert web_app.app.config.routes_pathname_prefix == "/app/"


def test_the_server_answers_on_both_paths():
    rules = {str(rule) for rule in web_app.app.server.url_map.iter_rules()}

    assert "/" in rules, "Landingpage"
    assert "/<page>.html" in rules, "Rechtsseiten der Landingpage"
    assert "/app/" in rules, "Dashboard"
