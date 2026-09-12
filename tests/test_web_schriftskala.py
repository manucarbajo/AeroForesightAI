"""Jede Schriftgröße kommt aus der Skala (P7.0-U0.2, P7.1-U1.1).

**Der Befund (Q2 des UI/UX-Audits, nachgemessen am 2026-09-12):** Dreizehn
verschiedene Schriftgrößen standen gleichzeitig in der Oberfläche, in **23**
Kombinationen aus Größe und Gewicht; je Bereich sieben bis elf. In Schritt 1
allein acht. Und der Hinweis unter einem Feld war größer als dessen
Beschriftung — dieselbe Kaskadenkollision, die P7.1-U1.1 vorab behoben hat.

**Die Ursache waren drei unabhängige Quellen**, und das ist der Grund, warum
dieser Wächter drei Dinge prüft statt einer: 60 `font-size`-Regeln im
Stylesheet mit 14 verschiedenen Werten, sieben Tailwind-Textklassen im
Python-Code und sechs Rollenkonstanten in `components.py`, die selbst wieder
Tailwind zusammensetzten. Jede Quelle war für sich plausibel; widersprochen
haben sie sich erst zusammen.

**Entschieden am 2026-09-12** (D1/E1,
`docs/entscheidung_gestaltungssystem_2026-09-12.md`): sechs Größen — 24, 20,
16, 15, 14, 12 px.

**Zwei Ausnahmen, und beide sind benannt statt geduldet:**

* **Symbolgrößen.** `ui.icon` setzt über `text-base`, `text-lg` … die Größe
  eines Glyphs. Eine Ikone ist keine Schriftrolle; ihre Größe richtet sich nach
  dem Element, neben dem sie steht. Gesucht wird deshalb nur, was **Text**
  bemaßt — geprüft am Aufruf, nicht am Klassennamen.
* **Die Landingpage.** Sie hat ihre eigenen Tokens
  (`aeroforesight-ai-landing-page/design/color-tokens.json`) und gilt als
  fertig; `landing_route.py` liefert ihr HTML aus und ist ausgenommen.

**Warum «Mono» keine Größe ist**, und das ist gemessen: Die erste Fassung der
Skala gab ihr 13 px. Die Konsole wäre damit von 11 auf 13 px gegangen — 18 %
mehr Zeilenhöhe —, und Inline-Code in einem 12-px-Hinweis wäre **größer**
geworden als der Satz, in dem er steht (`0.95em` macht ihn heute bewusst
kleiner). Festbreitenschrift nimmt dieselben Größen wie alles andere.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from dashboard.web import components as ui
from dashboard.web import theme

WEB = Path(__file__).resolve().parents[1] / "dashboard" / "web"
CSS = WEB / "assets" / "dashboard.css"

#: Die Rollen der Skala — Name, Token, Klasse, Größe in px.
ROLLEN = {
    "titel": 24,
    "ueberschrift": 20,
    "abschnitt": 16,
    "text": 15,
    "beschriftung": 14,
    "klein": 12,
}

#: Dateien, die ihre Schriftgrößen nicht aus dieser Skala nehmen — je Eintrag
#: der Grund. Eine Ausnahme ohne Grund wäre eine stille Freigabe.
AUSNAHMEN = {
    "landing_route.py": (
        "Liefert das HTML der Landingpage aus. Die hat ihre eigenen Tokens "
        "(`design/color-tokens.json`) und gilt als fertig — sie ist ausdrücklich "
        "nicht Teil von Phase 7."
    ),
}

_TAILWIND_GROESSE = re.compile(r"\btext-(xs|sm|base|lg|xl|[2-9]xl)\b")


def _ohne_kommentare(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


# --- Das Stylesheet ----------------------------------------------------------


def test_the_stylesheet_declares_exactly_these_sizes():
    """Die Tokens stehen da, und zwar genau diese sechs."""

    css = _ohne_kommentare(CSS.read_text(encoding="utf-8"))
    gefunden = {
        name: wert
        for name, wert in re.findall(r"--schrift-([\w-]+)\s*:\s*([^;]+);", css)
        if not name.endswith("-hoehe")
    }

    assert set(gefunden) == set(ROLLEN), (
        f"Die Skala nennt {sorted(gefunden)}, erwartet sind {sorted(ROLLEN)}. "
        "Wer eine Rolle hinzufügt oder streicht, ändert die Entscheidung D1/E1 — "
        "dann gehört sie dort nachgetragen."
    )
    for name, px in ROLLEN.items():
        wert = gefunden[name].strip()
        rem = float(wert.removesuffix("rem"))
        assert wert.endswith("rem"), f"`--schrift-{name}` steht in {wert}, erwartet ist `rem`."
        assert rem * 16 == pytest.approx(
            px
        ), f"`--schrift-{name}` ist {rem * 16:.1f} px, entschieden sind {px} px."


def test_no_rule_sets_a_size_outside_the_scale():
    """**Die tragende Zusage.** Jede `font-size` benutzt ein Token.

    Gesucht wird der Mechanismus und nicht die bekannte Stelle: Wer morgen eine
    Regel mit `font-size: 0.8125rem` hinzufügt, bekommt Bescheid, ohne dass ihn
    jemand hier einträgt.
    """

    css = _ohne_kommentare(CSS.read_text(encoding="utf-8"))
    # Der Tokenblock selbst definiert die Werte — er darf es.
    ab_tokens = css[css.index("--schrift-titel") :]
    literale = [
        wert.strip()
        for wert in re.findall(r"font-size:\s*([^;]+)", ab_tokens)
        if not wert.strip().startswith("var(--schrift-")
    ]

    assert not literale, "Diese Regeln setzen eine Schriftgröße ohne Token: " + ", ".join(literale)


def test_no_rule_sizes_text_relative_to_its_parent():
    """`em` ist keine Größe, sondern ein Anteil — und der hängt am Wirt.

    Zwei Regeln rechneten so: `.af-hint code { 0.95em }` und `.af-md code
    { 0.8125em }`. Gerendert ergab die zweite **9,75 px in einer
    Bildunterschrift und 12,2 px im Fließtext** — dieselbe Regel, zwei Größen,
    keine davon auf einer Skala. Eine Größe gehört zu ihrer Rolle.
    """

    css = _ohne_kommentare(CSS.read_text(encoding="utf-8"))
    relativ = re.findall(r"font-size:\s*([\d.]+\s*em)", css)

    assert not relativ, "Diese Regeln bemaßen Text relativ zum Elternelement: " + ", ".join(relativ)


# --- Der Python-Code ---------------------------------------------------------


def _tailwind_am_text(pfad: Path) -> list[str]:
    """Tailwind-Größenklassen, die **Text** bemaßen — Symbolgrößen ausgenommen.

    Entschieden wird am **Aufruf**: Was als Argument von `icon`/`ui.icon`
    dasteht, ist eine Glyphengröße; alles andere ist Text. Ein Wächter über den
    Klassennamen allein könnte das nicht unterscheiden — `text-lg` steht in
    beiden Fällen da.
    """

    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    ikonen: set[int] = set()

    def merken(knoten) -> None:
        for teil in ast.walk(knoten):
            ikonen.add(id(teil))

    for knoten in ast.walk(baum):
        # Was an `icon(...)` übergeben wird.
        if isinstance(knoten, ast.Call):
            name = knoten.func
            gerufen = (
                name.attr
                if isinstance(name, ast.Attribute)
                else name.id if isinstance(name, ast.Name) else ""
            )
            if gerufen == "icon":
                for arg in list(knoten.args) + [k.value for k in knoten.keywords]:
                    merken(arg)
        # **Und der Vorgabewert von `icon` selbst.** Er stand beim ersten
        # Durchlauf als einziger Fund da: `def icon(name, class_name="text-base")`
        # ist dieselbe Glyphengröße, nur an der Definition statt am Aufruf.
        if isinstance(knoten, ast.FunctionDef) and knoten.name == "icon":
            for vorgabe in knoten.args.defaults + [d for d in knoten.args.kw_defaults if d]:
                merken(vorgabe)

    funde: list[str] = []
    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Constant) or not isinstance(knoten.value, str):
            continue
        if id(knoten) in ikonen:
            continue
        for treffer in _TAILWIND_GROESSE.findall(knoten.value):
            funde.append(f"Zeile {knoten.lineno}: text-{treffer}")
    return funde


PY_DATEIEN = sorted(WEB.rglob("*.py"))


@pytest.mark.parametrize("pfad", PY_DATEIEN, ids=lambda p: p.name)
def test_no_module_sizes_text_with_tailwind(pfad):
    """Text bekommt eine Rolle, keine Tailwind-Klasse.

    Der Grund ist keine Geschmacksfrage: Solange beide Wege offenstehen, gibt
    es zwei Quellen für dieselbe Größe, und die widersprechen sich. Gemessen
    waren es 64 Tailwind-Größenklassen neben 60 Regeln im Stylesheet.
    """

    funde = _tailwind_am_text(pfad)
    if pfad.name in AUSNAHMEN:
        pytest.skip(f"benannte Ausnahme: {AUSNAHMEN[pfad.name]}")

    assert not funde, (
        f"`{pfad.name}` bemaßt Text mit Tailwind statt mit einer Rolle:\n  "
        + "\n  ".join(funde)
        + f"\n\nZur Verfügung stehen: {', '.join(sorted(ROLLEN))} "
        "(`ui.TITEL`, `ui.UEBERSCHRIFT`, `ui.ABSCHNITT`, `ui.TEXT`, "
        "`ui.BESCHRIFTUNG`, `ui.KLEIN`)."
    )


def test_no_exception_outlives_its_reason():
    """Eine Ausnahme für eine Datei, die es nicht mehr gibt, ist eine Freigabe."""

    tot = [name for name in AUSNAHMEN if not any(p.name == name for p in PY_DATEIEN)]

    assert not tot, f"Diese Ausnahmen nennen Dateien, die es nicht gibt: {tot}"


def test_the_role_constants_name_the_classes():
    """`components.py` führt die Rollen, und zwar genau die sechs."""

    konstanten = {
        "TITEL": "titel",
        "UEBERSCHRIFT": "ueberschrift",
        "ABSCHNITT": "abschnitt",
        "TEXT": "text",
        "BESCHRIFTUNG": "beschriftung",
        "KLEIN": "klein",
    }
    for name, rolle in konstanten.items():
        assert getattr(ui, name) == f"af-schrift-{rolle}", (
            f"`ui.{name}` heißt {getattr(ui, name)!r}, erwartet ist " f"«af-schrift-{rolle}»."
        )


def test_the_inline_sizes_match_the_tokens():
    """Wo keine Klasse hinkommt, stehen dieselben Zahlen.

    Dashs `DataTable` bekommt seine Zellenstile als Python-Dict; das Stylesheet
    erreicht sie nicht. Bis zum 2026-09-12 standen dort `"13px"` und `"12px"`
    als Literale — zwei Größen neben der Skala, und 13 px gibt es darin nicht.
    """

    assert theme.SCHRIFT_PX == ROLLEN, (
        f"`theme.SCHRIFT_PX` und die Skala laufen auseinander: "
        f"{theme.SCHRIFT_PX} gegen {ROLLEN}."
    )
    quelle = (WEB / "views" / "files.py").read_text(encoding="utf-8")
    literale = re.findall(r'"fontSize":\s*"(\d+)px"', quelle)

    assert not literale, (
        f"`files.py` setzt Schriftgrößen als Literal: {literale}. "
        "Sie gehören über `theme.SCHRIFT_PX` an die Skala."
    )


# --- Der Wächter über sich selbst --------------------------------------------


def test_the_guard_would_notice_a_relapse(tmp_path):
    """Nachgestellt sind beide Wege: Text mit Tailwind, und ein Symbol daneben.

    Die zweite Hälfte ist die wichtigere — ein Wächter, der Symbolgrößen
    mitmeldet, produziert 23 Fehlalarme und wird abgeschaltet.
    """

    modul = tmp_path / "probe.py"
    modul.write_text(
        "from dashboard.web import components as ui\n"
        'html.P("x", className="font-body text-sm")\n'
        'ui.icon("chevron_right", "text-lg")\n'
        'icon("x", "af-acc__chevron text-base af-text-faint")\n',
        encoding="utf-8",
    )

    funde = _tailwind_am_text(modul)

    assert funde == [
        "Zeile 2: text-sm"
    ], f"Erwartet war genau der Textfund, gemeldet wurde: {funde}"
