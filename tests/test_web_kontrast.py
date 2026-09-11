"""Kontrast von Texten, die das Stylesheet einfärbt — gerechnet, nicht geschätzt.

**Anlass (P7.9-U9.1, vorgezogen am 2026-09-11):** Das Wort «optional» in der
Schrittliste stand in 11 px auf `--text-faint`. Gemessen im laufenden Browser,
dunkles Design: **3,77** auf dem Grund, **2,87** auf der markierten Zeile.
WCAG 2.2 AA verlangt für diese Größe 4,5.

**Gerechnet wird aus den Tokens**, nicht am Bildschirm: Welche Farbe eine Regel
benutzt, steht in `assets/dashboard.css`; welchen Wert der Token hat, in
`theme.PALETTE` — und `tests/test_web_theme.py` hält beide deckungsgleich. So
läuft die Prüfung in jeder CI und nicht nur im opt-in-Browser-Wächter.

**Die Liste ist klein und soll wachsen.** Sie ist kein Ersatz für den
Kontrastwächter über alle Textknoten (P7.0-U0.4), sondern hält die Stellen, die
schon einmal zu blass waren. Jeder Fall nennt den Grund, auf dem der Text
tatsächlich steht.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dashboard.web import theme

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"

#: WCAG 2.2 AA für normalen Text. «Groß» (ab 18,66 px oder 14 px fett) bekäme
#: 3,0 — keiner der Fälle hier ist groß.
MINDESTENS = 4.5

#: Selektor der Regel, die die Textfarbe setzt — und der Grund darunter.
FAELLE = [
    pytest.param(".af-step__tag", "canvas", id="optional-auf-dem-grund"),
    pytest.param(".af-step__tag", "surface-hover", id="optional-beim-zeigen"),
    pytest.param(
        ".af-step--current .af-step__tag", "accent-soft", id="optional-auf-der-markierten-zeile"
    ),
]


def _farbtoken(selektor: str) -> str:
    """Welchen Token die Regel für *selektor* als `color` setzt.

    Gesucht wird die **letzte** Regel mit genau diesem Selektor, außerhalb von
    `@media` — dieselbe Reihenfolge, in der der Browser sie anwendet.
    """

    text = CSS.read_text(encoding="utf-8")
    muster = re.compile(r"(?:^|\})\s*" + re.escape(selektor) + r"\s*\{([^}]*)\}", re.MULTILINE)
    token = None
    for regel in muster.finditer(text):
        farbe = re.search(r"(?:^|;)\s*color\s*:\s*var\(--([\w-]+)\)", regel.group(1))
        if farbe:
            token = farbe.group(1)
    assert token, f"Keine Regel `{selektor} {{ color: var(--…) }}` im Stylesheet."
    return token


def _leuchtdichte(hexwert: str) -> float:
    wert = hexwert.lstrip("#")
    kanaele = [int(wert[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4 for k in kanaele]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def kontrast(vorne: str, hinten: str) -> float:
    hell, dunkel = sorted((_leuchtdichte(vorne), _leuchtdichte(hinten)), reverse=True)
    return (hell + 0.05) / (dunkel + 0.05)


@pytest.mark.parametrize("modus", [theme.LIGHT, theme.DARK])
@pytest.mark.parametrize(("selektor", "grund"), FAELLE)
def test_the_text_is_readable_on_its_ground(selektor, grund, modus):
    palette = theme.PALETTE[modus]
    token = _farbtoken(selektor)
    wert = kontrast(palette[token], palette[grund])

    assert wert >= MINDESTENS, (
        f"`{selektor}` steht in `--{token}` auf `--{grund}` ({modus}): "
        f"Kontrast {wert:.2f}, verlangt {MINDESTENS}."
    )


def test_the_contrast_formula_matches_known_values():
    """Die Formel selbst — sonst wäre jeder Fall oben aus dem falschen Grund grün."""

    assert kontrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert kontrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)
