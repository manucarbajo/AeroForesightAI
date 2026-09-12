"""Jede Breite kommt aus der Skala, und jede passt zu ihrer Textgröße (P7.1-U1.2).

**Der Befund (Q1 des UI/UX-Audits vom 2026-09-11)** — und der Anlass für das
ganze Audit: In Schritt 1 standen bei 1440 px **sechs Textbreiten** und **elf
verschiedene rechte Kanten**, während die Zusage aus P1.9-W5.4 (höchstens 75
Zeichen je Zeile) an jeder einzelnen Stelle erfüllt war (42 bis 59). Der
Screenshot, mit dem alles anfing, zeigte einen Text auf knapp der halben
Spalte: 363 px in 760 px.

**Die Ursache war die Einheit.** `.af-mass { max-width: 48ch }` rechnet in `ch`,
dem Ziffernvorschub der Schrift **des jeweiligen Elements**. Dieselbe Regel
ergab 454 px an einem 15-px-Absatz, 424 px an einem 14-px-Text und 363 px an
einer 12-px-Bildunterschrift; verschachtelt kamen 341 px dazu.

**Warum dieser Wächter so aussieht, wie er aussieht: Ich bin dreimal in dieselbe
Sorte Falle gelaufen, und jede hat eine Zusage hier.**

1. **Ein Wert für alles.** 38 rem am Container gaben eine Breite — und rissen
   die Zeichenzusage: 608 px tragen bei 14 px 88 und bei 12 px 106 Zeichen. Ein
   Deckel in Pixeln und eine Zusage über Zeichen sind nur vereinbar, wenn der
   Deckel zur Textgröße passt. Seither gibt es einen je Prosagröße.
2. **Zurückgerechnet statt gezählt.** Aus 454 px und 49 Zeichen ergaben sich
   scheinbar 9,27 px je Zeichen, also 66 für 608 px. Der Browser-Wächter zählt
   die längste wirklich gesetzte Zeile und kam auf **82**. Genau davor warnt
   Teil 7 von `test_web_overflow.py` in seinem Docstring.
3. **Punktlandung.** 34 rem ergaben gemessen 76 Zeichen — eins zu viel, weil
   der Umbruch an Wortgrenzen hängt und die Beziehung nicht linear ist.
   Gewählt sind 32 rem mit Abstand.

**Was hier geprüft wird und was nicht.** Dieser Wächter ist statisch: Er hält
die Skala und die Zuordnung von Deckel zu Textrolle, und er läuft in jeder CI.
Die Zusage über **Zeichen je Zeile** kann er nicht halten — die braucht Layout,
und dafür ist Teil 7 des Browser-Wächters da. Beide zusammen decken U1.2 ab.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.test_web_drawers import _sieger

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"

#: Die Breiten der Skala, in px. Entschieden am 2026-09-12 (D1/E3), die beiden
#: Prosawerte gemessen statt gesetzt — Herleitung im Modul-Docstring.
BREITEN = {
    "lesen": 512,  # 32 rem, ~72 Zeichen bei 15 px
    "lesen-klein": 416,  # 26 rem, ~72 Zeichen bei 12 px
    "formular": 480,  # 30 rem
    "inhalt": 1088,  # 68 rem
}

#: Textrollen, deren Prosa den engeren Deckel braucht — und die Größe, wegen
#: der das so ist.
KLEINE_ROLLEN = {
    "af-md--caption": 12,
    "af-hint": 12,
    "af-schrift-klein": 12,
}


def _ohne_kommentare(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def _nur_deklarationen(text: str) -> str:
    """Das Stylesheet ohne Kommentare **und ohne `@media`-Bedingungen**.

    `@media (max-width: 1023px)` ist eine **Bedingung**, kein Deckel — der
    erste Anlauf dieser Suche meldete neun davon und wäre damit für immer rot
    gewesen. Sie stehen vor der öffnenden Klammer und nicht in einer
    Deklaration; hier fallen sie deshalb vorher heraus.
    """

    return re.sub(r"@media[^{]*", "", _ohne_kommentare(text))


def _css() -> str:
    return _nur_deklarationen(CSS.read_text(encoding="utf-8"))


# --- Die Skala ---------------------------------------------------------------


def test_the_stylesheet_declares_exactly_these_widths():
    gefunden = dict(re.findall(r"--breite-([\w-]+)\s*:\s*([^;]+);", _css()))

    assert set(gefunden) == set(BREITEN), (
        f"Die Skala nennt {sorted(gefunden)}, erwartet sind {sorted(BREITEN)}. "
        "Wer eine Breite hinzufügt oder streicht, ändert die Entscheidung D1/E3."
    )
    for name, px in BREITEN.items():
        wert = gefunden[name].strip()
        assert wert.endswith("rem"), (
            f"`--breite-{name}` steht in {wert}. **In `rem`, nicht in `ch`** — "
            "`ch` hängt an der Schrift des Elements und ist unter Linux zusätzlich "
            "auf ganze Pixel quantisiert (P3.17)."
        )
        assert float(wert.removesuffix("rem")) * 16 == pytest.approx(px), (
            f"`--breite-{name}` ist {float(wert.removesuffix('rem')) * 16:.0f} px, "
            f"eingetragen sind {px}."
        )


def test_no_rule_caps_a_width_outside_the_scale():
    """**Die tragende Zusage.** Jeder Deckel benutzt ein Token.

    Gesucht wird der Mechanismus, nicht die bekannte Stelle: Wer morgen
    `max-width: 46rem` hinzufügt, bekommt Bescheid, ohne dass ihn jemand hier
    einträgt. Ausgenommen sind `none` und die Haltepunkte in `@media`, die keine
    Deckel sind, sondern Bedingungen.
    """

    literale = [
        wert.strip()
        for wert in re.findall(r"max-width:\s*([^;{]+)", _css())
        if not wert.strip().startswith("var(--breite") and wert.strip() != "none"
    ]

    assert not literale, "Diese Regeln deckeln eine Breite ohne Token: " + ", ".join(literale)


def test_no_width_is_measured_in_characters():
    """`ch` ist die Einheit, an der Q1 hängt — und P3.17 auf Linux.

    Sie ist nicht falsch, sie ist nur **elementabhängig**: Dieselbe Zahl ergibt
    je Schriftgröße eine andere Breite. Die Zusage über Zeichen hält seither der
    Browser-Wächter, der zählt.
    """

    in_zeichen = re.findall(r"max-width:\s*[\d.]+ch", _css())

    assert not in_zeichen, f"Deckel in `ch`: {in_zeichen}"


# --- Deckel und Textgröße gehören zusammen -----------------------------------


@pytest.mark.parametrize("rolle", sorted(KLEINE_ROLLEN))
def test_small_prose_gets_the_narrow_cap(rolle):
    """**Der Fehler aus dem ersten Anlauf, als Zusage.**

    Ein Element mit `af-mass` und einer kleinen Textrolle muss den engeren
    Deckel bekommen. Ohne diese Unterscheidung trug ein 12-px-Hinweis bei 608 px
    **106** Zeichen je Zeile — zugesagt sind 75.

    Nachgerechnet wird mit dem Kaskaden-Nachrechner: Die Regel mit zwei Klassen
    gewinnt ordnungsunabhängig gegen die mit einer, und genau darauf beruht die
    Zuordnung.
    """

    _, wert = _sieger({"af-mass", rolle}, "max-width")

    assert wert.strip() == "var(--breite-lesen-klein)", (
        f"`af-mass` an einem Element mit `{rolle}` ({KLEINE_ROLLEN[rolle]} px) "
        f"bekommt {wert.strip()} statt des engeren Deckels. Bei "
        f"{BREITEN['lesen']} px trägt {KLEINE_ROLLEN[rolle]}-px-Text rund "
        f"{round(72 * BREITEN['lesen'] / BREITEN['lesen-klein'])} Zeichen je Zeile."
    )


def test_body_prose_gets_the_reading_cap():
    """Und umgekehrt: Fließtext bekommt den weiteren Deckel."""

    _, wert = _sieger({"af-mass", "af-md"}, "max-width")

    assert (
        wert.strip() == "var(--breite-lesen)"
    ), f"Fließtext mit `af-mass` bekommt {wert.strip()} statt des Lesemaßes."


def test_a_cap_does_not_nest():
    """Ein Lesemaß in einem Lesemaß verengte den inneren Text ein zweites Mal.

    Gemessen: Die Quellenliste der Kohärenzbegründung stand bei 341 px statt bei
    363. Der äußere Deckel gilt, der innere gibt auf.
    """

    css = _css()
    paare = [
        (".af-breite-lesen .af-breite-lesen", "verschachtelte Container"),
        (".af-breite-lesen .af-mass", "Element in einem Container"),
        (".af-mass .af-mass", "Element in einem Element"),
    ]
    for selektor, was in paare:
        muster = re.escape(selektor) + r"[^{]*\{([^}]*)\}"
        treffer = re.search(muster, css)
        assert treffer, f"Keine Regel für {was} (`{selektor}`)."
        assert "max-width: none" in treffer.group(1), (
            f"`{selektor}` hebt den inneren Deckel nicht auf — {was} verengt " "damit zweimal."
        )


# --- Der Wächter über sich selbst --------------------------------------------


def test_the_guard_would_notice_a_relapse():
    """**Ein Wächter, der nie etwas sieht, könnte auch blind sein.**

    Nachgestellt ist der Rückfall, der dreimal passiert ist: ein Deckel als
    Literal. Geprüft wird die Suche selbst, nicht das Stylesheet — sonst müsste
    dieser Test es kaputt machen.
    """

    erfunden = ".af-irgendwas {\n    max-width: 46rem;\n}"
    literale = [
        wert.strip()
        for wert in re.findall(r"max-width:\s*([^;{]+)", erfunden)
        if not wert.strip().startswith("var(--breite") and wert.strip() != "none"
    ]

    assert literale == ["46rem"], f"Die Suche findet den Rückfall nicht: {literale}"


def test_the_media_breakpoints_are_not_mistaken_for_caps():
    """`@media (max-width: 1023px)` ist eine Bedingung, kein Deckel.

    Der erste Anlauf dieser Suche meldete neun davon und wäre damit für immer
    rot gewesen. **Geprüft wird, dass es sie noch gibt** — verschwänden sie aus
    dem Stylesheet, wäre `_nur_deklarationen` wirkungslos, und niemand merkte
    es, bis jemand einen Haltepunkt hinzufügt.
    """

    roh = _ohne_kommentare(CSS.read_text(encoding="utf-8"))
    bedingungen = re.findall(r"@media\s*\([^)]*max-width:\s*\d+px\)", roh)

    assert bedingungen, "Keine Haltepunkte gefunden — dann prüft dieser Test nichts."
    assert "@media" not in _css(), (
        "`_nur_deklarationen` lässt `@media` stehen — dann zählt die Suche nach "
        "Deckeln die Haltepunkte mit."
    )
