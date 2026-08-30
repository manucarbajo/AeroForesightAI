"""Was an der Landingpage stimmen muss.

Sie ist handgeschriebenes HTML ohne Build-Schritt — ein Klassenname, den es
nicht gibt, fällt niemandem auf, weil nichts fehlschlägt. Genau das ist
passiert: `rounded-DEFAULT` stand an 32 Stellen, Tailwind erzeugt für den
Schlüssel `DEFAULT` aber nur `.rounded`. Alle Schaltflächen waren dadurch
eckig, entgegen dem eigenen Design-System.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from dashboard.web.landing_route import LANDING_DIR

TOKENS = LANDING_DIR / "design" / "color-tokens.json"

SEITEN = sorted(LANDING_DIR.glob("*.html"))


def _lies(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_the_pages_are_all_there():
    namen = {path.name for path in SEITEN}

    assert namen == {
        "index.html",
        "demo-anfragen.html",
        "impressum.html",
        "datenschutz.html",
        "agb.html",
    }


# --- Klassennamen ----------------------------------------------------------


@pytest.mark.parametrize("path", SEITEN, ids=lambda p: p.name)
def test_no_class_that_tailwind_does_not_generate(path):
    """`rounded-DEFAULT` erzeugt keinen Radius, sondern gar nichts."""

    assert "rounded-DEFAULT" not in _lies(path), (
        "Für den Schlüssel `DEFAULT` erzeugt Tailwind nur `.rounded`. "
        "Die Klasse mit Suffix bleibt wirkungslos."
    )


def test_the_buttons_ask_for_a_radius():
    """Ohne diese Prüfung wäre der Test oben auch dann grün, wenn die Klasse
    ersatzlos gestrichen würde."""

    index = _lies(LANDING_DIR / "index.html")
    buttons = re.findall(r'<a[^>]*role="button"[^>]*>', index)

    assert buttons, "keine Schaltflächen gefunden"
    ohne = [b for b in buttons if not re.search(r'class="[^"]*\brounded\b', b)]
    assert not ohne, f"Schaltflächen ohne Radius: {len(ohne)}"


def test_the_radius_matches_the_design_tokens():
    """Der Radius der Seite und der des Dashboards kommen aus derselben Quelle.

    **Diese Quelle ist seit P1.4 `tailwind.config.js`.** Vorher stand dieselbe
    Konfiguration inline in jeder der fünf Seiten *und* in `app.py` — sechs
    Kopien, die früher oder später auseinanderlaufen. Der Test prüfte sie
    einzeln; jetzt prüft er die eine.
    """

    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    erwartet = tokens["roundness"]["css"]

    konfig = Path("tailwind.config.js").read_text(encoding="utf-8")
    treffer = re.search(r"DEFAULT:\s*\"([^\"]+)\"", konfig)

    assert treffer, "keine borderRadius-Konfiguration in tailwind.config.js"
    assert treffer.group(1) == erwartet, f"{treffer.group(1)} statt {erwartet}"


@pytest.mark.parametrize("path", SEITEN, ids=lambda p: p.name)
def test_no_page_carries_its_own_tailwind_config(path):
    """Keine Seite bringt eine zweite Fassung der Konfiguration mit (P1.4).

    Das war der Zustand bis zum 2026-08-30: fünf Seiten mit je einer eigenen
    Navy-Skala, dazu eine sechste in `app.py`. Und alle sechs wurden von einem
    CDN-Skript zur Laufzeit ausgewertet — jeder Seitenaufruf meldete damit die
    IP des Betrachters an einen fremden Host.
    """

    text = _lies(path)

    assert "tailwind.config" not in text, "Die Seite trägt eine eigene Tailwind-Konfiguration"
    assert "cdn.tailwindcss.com" not in text, "Die Seite lädt Tailwind von einem fremden Host"


# --- Verweise --------------------------------------------------------------


@pytest.mark.parametrize("path", SEITEN, ids=lambda p: p.name)
def test_no_hardcoded_address(path):
    """Alles Interne relativ, sonst bricht es unter jeder anderen Domain."""

    text = _lies(path)

    assert "localhost" not in text
    assert "127.0.0.1" not in text
