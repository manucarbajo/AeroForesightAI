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
