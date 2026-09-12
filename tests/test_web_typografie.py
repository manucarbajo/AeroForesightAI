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
from dashboard.web import theme
from tests.test_web_drawers import _sieger

#: Die Rollen der Skala als rem — seit P7.1-U1.1 stehen die Größen als Tokens
#: im Stylesheet, und eine Regel sagt `var(--schrift-klein)` statt `0.75rem`.
#: **Die Zusage hier ist dieselbe geblieben**, nur die Auflösung ist neu: Wer
#: eine Größe vergleichen will, muss den Token erst nachschlagen. Die Zahlen
#: kommen aus `theme.SCHRIFT_PX`, damit sie nicht ein zweites Mal hier stehen.
ROLLEN_REM = {f"--schrift-{name}": px / 16 for name, px in theme.SCHRIFT_PX.items()}


def _rem(wert: str) -> float:
    """Eine Größenangabe des Stylesheets in rem — Token oder Literal.

    Vor P7.1-U1.1 stand in jeder Regel ein Literal; seither ein Token. Beides
    aufzulösen ist kein Zugeständnis, sondern nötig: Tailwind liefert weiterhin
    Literale (`text-sm`), und `components.LABEL` benutzt eine Rolle.
    """

    wert = wert.strip()
    if wert.startswith("var(--schrift-"):
        token = wert[len("var(") : wert.index(")")]
        assert token in ROLLEN_REM, f"Unbekanntes Schrift-Token {token!r}."
        return ROLLEN_REM[token]
    assert wert.endswith("rem"), f"Erwartet rem oder ein Schrift-Token, gefunden {wert!r}."
    return float(wert.removesuffix("rem"))


def _klassen_des_hinweises() -> set[str]:
    hinweis = ui.hint_text("Ein Hinweis.")
    return set(hinweis.className.split())


def test_the_hint_class_set_is_what_the_component_renders():
    """Vorbedingung: Geprüft wird das Element, das `hint_text` wirklich baut."""

    assert {"af-hint", "af-md"} <= _klassen_des_hinweises()


def test_a_hint_is_smaller_than_its_label():
    """Die Zusage von 2026-09-11, jetzt gegen die Skala gerechnet.

    Die Beschriftung trägt seit P7.1-U1.1 eine **Rolle** statt einer
    Tailwind-Klasse; nachgeschlagen wird sie deshalb genauso wie der Hinweis.
    """

    selektor, groesse = _sieger(_klassen_des_hinweises(), "font-size")
    rolle = next(k for k in ui.LABEL.split() if k.startswith("af-schrift-"))
    beschriftung = ROLLEN_REM["--schrift-" + rolle.removeprefix("af-schrift-")]

    assert _rem(groesse) < beschriftung, (
        f"Der Feldhinweis bekommt {groesse} aus `{selektor}` — die Beschriftung "
        f"darüber {beschriftung}rem. Der Hinweis darf nicht lauter sein als das Feld."
    )


#: Markdown in fremder Größe (P7.1-U1.4, vorgezogen am 2026-09-11): Klassen des
#: Bausteins und die Größe des Absatzes, den er ersetzt hat. Ohne die Rolle
#: bekäme jeder dieser Texte die 15 px von `.af-md` — der Fix gegen roh
#: gezeigtes Markdown hätte sonst genau die Kaskade zurückgebracht, die der
#: Feldhinweis gerade losgeworden ist.
ROLLEN = {
    "af-md--caption": 12,
    "af-md--betont": 14,
}


def test_markdown_in_a_role_keeps_the_size_of_its_paragraph():
    for rolle, erwartet_px in ROLLEN.items():
        selektor, groesse = _sieger({"af-md", "af-md--tight", rolle}, "font-size")

        assert _rem(groesse) * 16 == erwartet_px, (
            f"Markdown mit `{rolle}` bekommt {groesse} aus `{selektor}`, erwartet "
            f"{erwartet_px} px."
        )


class TestEineLedeIstFliesstext:
    """Die Einleitung eines Schritts ist der erste Satz, nicht die Fußnote.

    **Der Befund vom 2026-09-12, gemessen im Browser:** Die Lede unter jeder
    Schritt-Überschrift stand in `ui.CAPTION` — der Rolle einer
    Bildunterschrift, 12 px. Sie war damit der schmalste Fließtext des
    Bildschirms: 409 px von 760, also 53,8 %, und zwar **nicht** wegen eines zu
    engen Deckels, sondern weil 12-px-Prosa für 75 Zeichen nur 416 px braucht.
    Auf ihren 409 px trug sie schon 72 Zeichen.

    **Zwei Lede-Begriffe gab es außerdem**, die eines Schritts (12 px) und die
    eines Blocks (`af-md--lede`, 14 px) — beide kleiner als der Text, den sie
    einleiten. Es ist jetzt eine Rolle in einer Größe.

    Gemessen wird die **Kaskade**, nicht die Klasse: `ui.LEDE` könnte jederzeit
    von einer späteren Regel überschrieben werden, und genau diese Falle hat
    den Feldhinweis im Kopf dieser Datei erwischt.
    """

    def test_the_step_lede_is_set_in_body_size(self):
        selektor, groesse = _sieger(set(ui.LEDE.split()), "font-size")

        assert _rem(groesse) == ROLLEN_REM["--schrift-text"], (
            f"Die Lede eines Schritts bekommt {groesse} aus `{selektor}`, "
            f"erwartet {ROLLEN_REM['--schrift-text']}rem — die Größe des "
            "Fließtextes, den sie einleitet."
        )

    def test_the_block_lede_is_set_in_body_size(self):
        selektor, groesse = _sieger(set(ui.lede("Ein Satz.").className.split()), "font-size")

        assert _rem(groesse) == ROLLEN_REM["--schrift-text"], (
            f"Die Lede eines Blocks bekommt {groesse} aus `{selektor}`, erwartet "
            f"{ROLLEN_REM['--schrift-text']}rem."
        )

    def test_the_promise_could_fail_at_all(self):
        """Vorbedingung: Fließtext und Bildunterschrift sind zwei Größen.

        Wären sie gleich, wären die beiden Zusagen darüber auch für eine Lede
        in `ui.CAPTION` grün — und diese Datei hätte den Befund nicht gefunden,
        sondern nur eine Tautologie gehalten.
        """

        assert ROLLEN_REM["--schrift-text"] > ROLLEN_REM["--schrift-klein"]
        assert _rem(_sieger(set(ui.CAPTION.split()), "font-size")[1]) == (
            ROLLEN_REM["--schrift-klein"]
        )


def test_a_hint_keeps_its_muted_colour():
    """Dieselbe Kaskade nahm dem Hinweis auch seine Farbe: `.af-md` setzt den Fließtext."""

    selektor, farbe = _sieger(_klassen_des_hinweises(), "color")

    assert (
        farbe == "var(--text-muted)"
    ), f"Der Feldhinweis bekommt {farbe} aus `{selektor}` statt der gedämpften Hinweisfarbe."
