"""Schriftgrößen, die sich gegenseitig schlagen (P7.1-U1.1, vorgezogen am 2026-09-11).

**Der Befund:** Der Kurzhinweis unter einem Eingabefeld war gemessen **15 px**,
die Beschriftung darüber **14 px** — das lauteste Element eines Feldes war der
Satz, der es erklärt. `ui.hint_text` rendert als `dcc.Markdown` mit den Klassen
`af-hint af-md`. Beide Regeln tragen eine Klasse, und `.af-md { font-size:
0.9375rem }` steht im Stylesheet **nach** `.af-hint { font-size: 0.75rem }`: Bei
gleicher Spezifität gewinnt die spätere.

**Gemessen wird die Kaskade, nicht die Regel.** Dass `.af-hint` 0,75 rem sagt,
stand die ganze Zeit richtig da — falsch war, welche Regel am Ende gewinnt.
Dieselbe Falle wie beim Schubladen-Knopf aus der Gegenprobe zu P1.5, und
deshalb derselbe Nachrechner (`tests/test_web_drawers._sieger`).
"""

from __future__ import annotations

from dashboard.web import components as ui
from tests.test_web_drawers import _sieger

#: Tailwinds Schriftgrößen, wie `components.LABEL` sie benutzt.
TAILWIND_TEXT = {"text-xs": 0.75, "text-sm": 0.875, "text-base": 1.0, "text-lg": 1.125}


def _rem(wert: str) -> float:
    assert wert.endswith("rem"), f"Erwartet eine Angabe in rem, gefunden {wert!r}."
    return float(wert.removesuffix("rem"))


def _klassen_des_hinweises() -> set[str]:
    hinweis = ui.hint_text("Ein Hinweis.")
    return set(hinweis.className.split())


def test_the_hint_class_set_is_what_the_component_renders():
    """Vorbedingung: Geprüft wird das Element, das `hint_text` wirklich baut."""

    assert {"af-hint", "af-md"} <= _klassen_des_hinweises()


def test_a_hint_is_smaller_than_its_label():
    selektor, groesse = _sieger(_klassen_des_hinweises(), "font-size")
    beschriftung = next(rem for klasse, rem in TAILWIND_TEXT.items() if klasse in ui.LABEL.split())

    assert _rem(groesse) < beschriftung, (
        f"Der Feldhinweis bekommt {groesse} aus `{selektor}` — die Beschriftung "
        f"darüber {beschriftung}rem. Der Hinweis darf nicht lauter sein als das Feld."
    )


def test_a_hint_keeps_its_muted_colour():
    """Dieselbe Kaskade nahm dem Hinweis auch seine Farbe: `.af-md` setzt den Fließtext."""

    selektor, farbe = _sieger(_klassen_des_hinweises(), "color")

    assert (
        farbe == "var(--text-muted)"
    ), f"Der Feldhinweis bekommt {farbe} aus `{selektor}` statt der gedämpften Hinweisfarbe."
