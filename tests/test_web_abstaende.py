"""Abstände aus einer Skala — Teil A: eine Einzugsstufe (P7.1-U1.3, P7.0-U0.1).

**Der Befund, gemessen am 2026-09-12:** Nachdem Fließtext seinen Rahmen füllte,
stand die Treppe aus dem ersten Screenshot des UI/UX-Audits immer noch da — nur
nicht mehr in den Breiten, sondern in den **Einrückungen**. Für «eine Stufe
tiefer» gab es fünf Werte: 16 px (Hinweis- und Meldungskasten), 20 px
(Glossar-Erklärung), 22 px (Markdown-Liste), 24 px (Karte, «Feinabstimmung») und
26 px (Hinweis unter einem Kästchen). In Schritt 1 begannen Texte an x = 0, 25,
42, 49, 69, 71 und 75.

**Dieser Wächter ist statisch** und hält die Kopplungen im Stylesheet. Ob jede
Textspalte wirklich auf dem Raster beginnt, misst Teil 7b von
`tests/test_web_overflow.py` im Browser. Teil B von U1.3 — die übrigen Abstände
auf der 8-Stufen-Skala — erweitert diese Datei.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_web_drawers import _sieger

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"

#: Eine Stufe tiefer, in px. Entschieden mit E4 (4-px-Raster, acht Stufen);
#: 24 ist die Stufe, die Karte und «Feinabstimmung» schon hatten.
EINZUG_PX = 24


def _css() -> str:
    return re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)


def _token_px(name: str, text: str | None = None) -> float:
    quelle = _css() if text is None else text
    treffer = re.search(r"--" + re.escape(name) + r"\s*:\s*([\d.]+)rem\s*;", quelle)
    assert treffer, f"Token `--{name}` fehlt oder steht nicht in rem."
    return float(treffer.group(1)) * 16


def _regel(selektor: str) -> str:
    """Der Rumpf der Regel, deren Selektorliste genau so beginnt."""

    treffer = re.search(re.escape(selektor) + r"\s*\{([^}]*)\}", _css())
    assert treffer, f"Keine Regel für `{selektor}`."
    return treffer.group(1)


def _alle_rumpfe(selektor: str) -> list[str]:
    """Alle Regelrümpfe mit genau dieser Selektorliste — es kann mehrere geben.

    `.af-switch label` steht zweimal im Stylesheet (Ausrichtung; Anordnung und
    Abstand), `.af-md ul, .af-md ol` ebenso (Rand; Einzug). Der erste Anlauf
    dieser Datei nahm nur die erste Fundstelle und meldete einen fehlenden
    Abstand, der zwei Regeln weiter stand.
    """

    gesucht = " ".join(selektor.split())
    rumpfe = []
    for stueck in _css().split("}"):
        if "{" not in stueck:
            continue
        kopf, rumpf = stueck.split("{", 1)
        if " ".join(kopf.split()) == gesucht:
            rumpfe.append(rumpf)
    assert rumpfe, f"Keine Regel für `{selektor}`."
    return rumpfe


def _eine_stufe(einzug: float, kaestchen: float, abstand: float) -> bool:
    return abs((kaestchen + abstand) - einzug) < 0.01


def test_one_indent_step_is_24px():
    assert _token_px("einzug") == EINZUG_PX


def test_box_and_gap_make_exactly_one_step():
    """**Die tragende Kopplung.** Der Hinweis unter einem Kästchen steht bündig
    unter der Beschriftung — also Kästchen plus Abstand. Nur wenn das genau
    eine Stufe ergibt, liegt er auf dem Raster. Wer eine der drei Zahlen allein
    ändert, bekommt hier Bescheid statt einer Kante mehr im Browser.
    """

    einzug, kaestchen, abstand = (
        _token_px("einzug"),
        _token_px("kaestchen"),
        _token_px("kaestchen-abstand"),
    )

    assert _eine_stufe(einzug, kaestchen, abstand), (
        f"Kästchen {kaestchen:g} px + Abstand {abstand:g} px = "
        f"{kaestchen + abstand:g} px, eine Stufe ist {einzug:g} px."
    )


def test_the_checkbox_is_as_wide_as_its_token():
    rumpf = _regel('.af-check input[type="checkbox"],\n.af-radio input[type="radio"]')

    assert "width: var(--kaestchen)" in rumpf and "height: var(--kaestchen)" in rumpf, (
        "Das Kästchen hat eine eigene Breite — dann stimmt die Rechnung des "
        f"Hinweises nicht mehr: {rumpf.strip()!r}"
    )


def test_the_label_gap_is_its_token():
    for selektor in (".af-check label, .af-radio label", ".af-switch label"):
        mit_abstand = [r for r in _alle_rumpfe(selektor) if "gap:" in r]
        assert mit_abstand, f"`{selektor}` setzt keinen Abstand."
        assert all("gap: var(--kaestchen-abstand)" in r for r in mit_abstand), (
            f"`{selektor}` setzt einen eigenen Abstand statt des Tokens: "
            f"{[r.strip() for r in mit_abstand]!r}"
        )


def test_a_checkbox_hint_lands_on_the_grid_through_the_cascade():
    """Gemessen wird die Kaskade — die Klassen, die `hint_text` wirklich baut."""

    selektor, wert = _sieger({"af-hint", "af-md", "af-md--tight", "af-check__hint"}, "margin-left")

    assert (
        wert.strip() == "calc(var(--kaestchen) + var(--kaestchen-abstand))"
    ), f"Der Hinweis unter einem Kästchen bekommt {wert!r} aus `{selektor}`."


def test_a_radio_hint_uses_the_same_derivation():
    rumpf = _regel(".af-radio + .af-hint")

    assert "margin-left: calc(var(--kaestchen) + var(--kaestchen-abstand))" in rumpf


def test_a_list_indents_by_one_step():
    mit_einzug = [r for r in _alle_rumpfe(".af-md ul, .af-md ol") if "padding-left" in r]
    assert mit_einzug, "Die Markdown-Liste setzt keinen Einzug."
    assert all(
        "padding-left: var(--einzug)" in r for r in mit_einzug
    ), f"Die Markdown-Liste rückt mit einem eigenen Wert ein: {[r.strip() for r in mit_einzug]!r}"


def test_the_step_check_would_notice_a_relapse():
    """Selbsttest: die Kopplung von vorher — 16 + 10 — muss durchfallen."""

    assert _eine_stufe(24, 16, 8)
    assert not _eine_stufe(24, 16, 10)


# --- Teil B: jede übrige Abstandsangabe auf der Skala (2026-09-13) -----------
#
# **Entschieden von Haiko am 2026-09-13:** Ein Wert zwischen zwei Stufen geht
# auf die nächste, ein Gleichstand wird **abgerundet** — die Oberfläche ist dicht,
# und die Schritthöhe trägt eine Zusage. **Knöpfe weichen ab** und bekommen
# senkrecht 12 px (`py-3`), also rund 44 px Höhe: die übliche Mindestgröße einer
# Trefferfläche.
#
# **Beide Zusagen unten sind Suchläufe, keine Listen von Fundstellen.** Die
# Bestandsaufnahme vom 2026-09-13 fand 47 Deklarationen und 48 Tailwind-Klassen
# neben der Skala, mit neun verschiedenen Werten ab 4 px — und die erste
# Zählung hatte die Tailwind-Seite ganz übersehen.

#: Die Skala aus E4, in px — dazu 0.
SKALA_PX = {0.0, 4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0}

#: Tailwind-Abstandsstufen auf der Skala (Stufe mal 4 px). `0.5` ist der
#: Haarabstand (2 px) — dieselbe Zahl wie `--haarabstand` im Stylesheet.
TAILWIND_STUFEN = {"0", "0.5", "1", "2", "3", "4", "6", "8", "12", "16"}

#: Werte, die **keine Abstände** sind und deshalb nicht der Rundung folgen —
#: je (Selektor, Eigenschaft) mit Grund. Eine Ausnahme ohne Grund ist in sechs
#: Monaten eine Regel.
GEOMETRIE = {
    ('.af-check input[type="checkbox"], .af-radio input[type="radio"]', "margin-top"): (
        "Optische Ausrichtung des Kästchens an der Grundlinie der ersten Textzeile "
        "(Zeilenhöhe minus Kästchen, halbiert)"
    ),
    ('.af-check input[type="checkbox"]:checked::after', "margin"): (
        "Zeichnung des Hakens im Kästchen — ein Glyph, kein Abstand"
    ),
    (".af-md code", "padding"): (
        "Innenabstand von Inline-Code in em: wächst absichtlich mit der Code-Schrift"
    ),
    (".af-tabs .af-tabs__list .af-tab", "margin-bottom"): (
        "−1 px: Der aktive Reiter überdeckt die Linie der Reiterleiste"
    ),
    (".af-docs__link", "margin-left"): (
        "−1 px: Die Markierung des Handbuch-Links überdeckt die Linie daneben"
    ),
    (".af-nur-vorlesen", "margin"): (
        "−1 px: Beschnitt für Vorlesesoftware, das bekannte Muster für versteckten Text"
    ),
    (".af-step__text, .af-step__heading, .af-btn--symbol-schmal .af-btn__label", "margin"): (
        "−1 px: Beschnitt der Beschriftungen auf schmaler Breite (W5.5)"
    ),
}

_ABSTAND = re.compile(
    r"^\s*(margin(?:-top|-right|-bottom|-left|-inline|-block)?|"
    r"padding(?:-top|-right|-bottom|-left|-inline|-block)?|gap|row-gap|column-gap)"
    r"\s*:\s*([^;]+);",
    re.M,
)
_LAENGE = re.compile(r"(-?[\d.]+)(rem|px|em)\b")
_TAILWIND = re.compile(
    r"(?<![\w.:-])-?(?:[mp][trblxy]?|gap(?:-[xy])?|space-[xy])-(\[[^\]\s]+\]|[\d.]+)(?![\w.])"
)


def _blattregeln(text: str) -> list[tuple[str, str]]:
    """(Selektor, Rumpf) jeder Regel ohne Unterregeln — auch innerhalb von `@media`.

    Ein `split("}")` wie in `_alle_rumpfe` reicht hier nicht: In einer
    `@media`-Umgebung stehen zwei Klammerebenen, und der Selektor der inneren
    Regel landete im Rumpf der äußeren.
    """

    stapel: list[tuple[str, int]] = []
    start = 0
    regeln: list[tuple[str, str]] = []
    for m in re.finditer(r"[{}]", text):
        if m.group() == "{":
            kopf = re.split(r"[;}]", text[start : m.start()])[-1]
            stapel.append((" ".join(kopf.split()), m.end()))
        elif stapel:
            kopf, anfang = stapel.pop()
            rumpf = text[anfang : m.start()]
            if "{" not in rumpf:
                regeln.append((kopf, rumpf))
        start = m.end()
    return regeln


def _neben_der_skala(text: str) -> list[str]:
    befunde = []
    for selektor, rumpf in _blattregeln(text):
        for eigenschaft, wert in _ABSTAND.findall(rumpf):
            if "var(" in wert:
                continue
            if (selektor, eigenschaft) in GEOMETRIE:
                continue
            for zahl, einheit in _LAENGE.findall(wert):
                px = abs(float(zahl)) * (16.0 if einheit in ("rem", "em") else 1.0)
                if px not in SKALA_PX:
                    befunde.append(f"{selektor} → {eigenschaft}: {wert.strip()}")
                    break
    return befunde


def _tailwind_neben_der_skala(text: str) -> list[str]:
    return [stufe for stufe in _TAILWIND.findall(text) if stufe not in TAILWIND_STUFEN]


class TestJederAbstandLiegtAufDerSkala:
    """U1.3 Teil B — gesucht, nicht aufgezählt."""

    def test_every_spacing_declaration_is_on_the_scale(self):
        befunde = _neben_der_skala(_css())

        assert not befunde, (
            "Diese Abstände liegen neben der Skala (4, 8, 12, 16, 24, 32, 48, 64 px):\n  "
            + "\n  ".join(befunde)
            + "\n\nEin Abstand nimmt eine Stufe (Gleichstand abgerundet), ein Token "
            "oder `calc` über Tokens. Ist der Wert Geometrie statt Abstand, gehört er "
            "mit Grund in `GEOMETRIE`. Unter 4 px gibt es nur `var(--haarabstand)`."
        )

    def test_every_tailwind_spacing_step_is_on_the_scale(self):
        from tests.test_web_breiten import WEB_ROOT, _literale, _python_dateien

        befunde = []
        for pfad in _python_dateien():
            if pfad.name == "landing_route.py":  # vom UI/UX-Audit ausgenommen
                continue
            for text in _literale(pfad):
                for stufe in _tailwind_neben_der_skala(text):
                    befunde.append(f"{pfad.relative_to(WEB_ROOT)}: Stufe {stufe} in {text[:50]!r}")

        assert not befunde, "Tailwind-Abstände neben der Skala:\n  " + "\n  ".join(befunde)

    def test_every_geometry_exception_carries_a_reason(self):
        ohne = [f"{s} / {e}" for (s, e), grund in GEOMETRIE.items() if len(grund.strip()) < 30]

        assert not ohne, f"Diese Ausnahmen nennen keinen Grund: {ohne}"

    def test_every_geometry_exception_still_exists(self):
        """In beide Richtungen: eine Ausnahme ohne Regel dahinter gehört ausgetragen."""

        vorhanden = {
            (selektor, eigenschaft)
            for selektor, rumpf in _blattregeln(_css())
            for eigenschaft, _ in _ABSTAND.findall(rumpf)
        }
        verwaist = sorted(f"{s} / {e}" for s, e in GEOMETRIE if (s, e) not in vorhanden)

        assert not verwaist, f"Ausnahmen ohne Regel im Stylesheet: {verwaist}"

    def test_the_hairline_is_a_token_of_two_pixels(self):
        assert _token_px("haarabstand") == 2

    def test_a_button_is_tall_enough_to_hit(self):
        """**Die eine entschiedene Abweichung von der Abrundung** (2026-09-13).

        Rund 40 px hoch wären abgerundet 36 px geworden. Knöpfe bekommen
        senkrecht 12 px Polsterung: Beschriftung (14 px × 1,45) plus 2 × 12 ergibt
        rund 44 px — die übliche Mindestgröße einer Trefferfläche.
        """

        from dashboard.web import components as ui

        klassen = ui._BUTTON_BASE.split()
        assert "py-3" in klassen, f"Knöpfe haben nicht `py-3`: {ui._BUTTON_BASE!r}"
        assert "af-schrift-beschriftung" in klassen or ui.BESCHRIFTUNG in klassen

    def test_beside_a_field_is_computed_from_the_label(self):
        """`af-neben-feld` hängt an Beschriftungsgröße, Zeilenhöhe und Abstand.

        Bis zum 2026-09-13 stand dafür fünfmal `pt-7` — gerundet aus 20,3 + 6 px.
        Mit dem Beschriftungsabstand von 4 px trifft keine Rasterstufe mehr.
        """

        from dashboard.web import components as ui

        rumpf = "".join(_alle_rumpfe(".af-neben-feld"))
        assert "var(--schrift-beschriftung)" in rumpf and "var(--zeilenhoehe-beschriftung)" in rumpf
        assert (
            "+ 0.25rem" in rumpf
        ), f"Der Abstand der Beschriftung fehlt in der Rechnung: {rumpf!r}"
        assert "mb-1" in ui.LABEL.split(), (
            "`components.LABEL` hat nicht mehr `mb-1` — dann stimmt die Rechnung "
            f"von `.af-neben-feld` nicht mehr: {ui.LABEL!r}"
        )
        zeile = "".join(_alle_rumpfe(".af-schrift-beschriftung"))
        assert "line-height: var(--zeilenhoehe-beschriftung)" in zeile

    def test_the_pane_bleed_undoes_its_padding(self):
        """`.af-pane__sticky` hebt die Polsterung von `.af-pane` auf — ein Token für beide."""

        assert "padding: var(--pane-polster)" in "".join(_alle_rumpfe(".af-pane"))
        assert "calc(-1 * var(--pane-polster))" in "".join(_alle_rumpfe(".af-pane__sticky"))


class TestDerAbstandsWaechterWuerdeEinenRueckfallBemerken:
    def test_an_off_scale_declaration_is_found(self):
        probe = ".af-x {\n    padding: 0.375rem 0.75rem;\n}\n@media (min-width: 1px) {\n    .af-y {\n        gap: 1.75rem;\n    }\n}\n"

        befunde = _neben_der_skala(probe)

        assert any(".af-x" in b for b in befunde), befunde
        assert any(
            ".af-y" in b for b in befunde
        ), f"Eine Regel in `@media` wird übersehen: {befunde}"

    def test_tokens_and_hairline_pass(self):
        probe = ".af-x {\n    margin: var(--haarabstand) 0 0;\n    padding: 0.5rem 1.5rem;\n}\n"

        assert _neben_der_skala(probe) == []

    def test_tailwind_search_tells_steps_from_lookalikes(self):
        assert _tailwind_neben_der_skala("mt-5 px-4 gap-2.5") == ["5", "2.5"]
        assert _tailwind_neben_der_skala("scroll-mt-24 mt-0.5 sm:p-6 min-w-[18rem]") == []
