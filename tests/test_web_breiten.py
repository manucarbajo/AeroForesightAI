"""Fließtext füllt seinen Rahmen; gedeckelt werden Kästen (P7.1-U1.2).

**Der Befund (Q1 des UI/UX-Audits vom 2026-09-11)** — und der Anlass für das
ganze Audit: In Schritt 1 standen bei 1440 px **sechs Textbreiten** und **elf
verschiedene rechte Kanten**, während die Zusage aus P1.9-W5.4 (höchstens 75
Zeichen je Zeile) an jeder einzelnen Stelle erfüllt war. Der Screenshot, mit dem
alles anfing, zeigte einen Text auf knapp der halben Spalte: 363 px in 760 px.

**Drei Anläufe, und die Reihenfolge ist die Lehre.**

1. **Die Einheit war falsch.** `.af-mass { max-width: 48ch }` rechnet in `ch`,
   dem Ziffernvorschub der Schrift **des jeweiligen Elements** — dieselbe Regel
   ergab 454 px an einem 15-px-Absatz, 424 px an einem 14-px-Text und 363 px an
   einer 12-px-Bildunterschrift; verschachtelt kamen 341 px dazu.
2. **U1.2 machte daraus zwei Tokens in `rem`, am Block statt am Element.** Zwei
   Breiten statt sechs, eine Einheit statt drei, und die Texte eines Blocks
   endeten an einer Kante. Der Weg dorthin waren drei eigene Fehlschläge: ein
   Wert für alles riss die Zeichenzusage (608 px tragen bei 12 px 106 Zeichen);
   die Zeichen je Zeile zurückzurechnen lag um 24 % daneben, weil der Umbruch an
   Wortgrenzen hängt; und 34 rem waren eine Punktlandung, die mit 76 Zeichen um
   eins verfehlte.
3. **Und der Befund stand trotzdem noch da.** Nachgemessen in einer 760 px
   breiten Spalte: der breiteste Fließtext 509 px (67,0 %), die Lede 409 px
   (53,8 %). **Der Deckel war nicht zu eng, sondern ausgereizt** — die Lede trug
   auf ihren 409 px schon 72 der 75 erlaubten Zeichen.

**Die Rechnung, die E3 zurückgenommen hat** (2026-09-12, zweiter Nachtrag in
`docs/entscheidung_gestaltungssystem_2026-09-12.md`): gemessen 7,17 px je Zeichen
bei 15 px Schrift. Um 760 px mit höchstens 75 Zeichen zu füllen, müsste
Fließtext rund **21 px** groß sein. «Text füllt seine Spalte» und «höchstens 75
Zeichen je Zeile» sind bei dieser Spaltenbreite nicht gleichzeitig erfüllbar.
E1 hat die Schriftgröße entschieden, also fiel die andere Zusage.

**Was hier geprüft wird und was nicht.** Dieser Wächter ist statisch und läuft in
jeder CI: Er hält die Skala, und er hält fest, dass es **kein Maß für Fließtext
mehr gibt** — weder als `af-*`-Klasse noch als Tailwind-Deckel. Die eigentliche
Zusage — *kein Prosablock wird schmaler gesetzt als der Platz, den er hat* —
braucht Layout und steht in Teil 7 von `tests/test_web_overflow.py`. Beide
zusammen decken U1.2 ab.
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

import pytest

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"
CSS = WEB_ROOT / "assets" / "dashboard.css"

#: Die Breiten der Skala, in px. **Beide deckeln keinen Satz:** `formular` ist
#: die Breite eines kurzen Formulars, `inhalt` der Rahmen der Seite.
BREITEN = {
    "formular": 480,  # 30 rem
    "inhalt": 1088,  # 68 rem
}

#: Namen, unter denen das Lesemaß gelebt hat. Sie dürfen nicht zurückkommen —
#: nicht als Token, nicht als Klasse, nicht an einer Aufrufstelle.
ABGESCHAFFT = ("--breite-lesen", "af-mass", "af-breite-lesen")

#: **Sperrklinke über Tailwinds Deckel** (`max-w-*`), je Datei und Klasse mit
#: Grund. Sie hält den Ist-Stand und schlägt in **beide** Richtungen an: Ein
#: neuer Deckel fällt auf, ein weggeräumter auch.
#:
#: **Warum es diese Liste überhaupt gibt.** U1.2 hat die `af-*`-Deckel
#: vereinheitlicht und die Tailwind-Deckel **übersehen** — `max-w-md`,
#: `max-w-2xl` (3×), `max-w-3xl` (4×) und `max-w-4xl` standen weiter an Prosa,
#: während das Paket «zwei Textbreiten» meldete. Sie sind mit der Rücknahme von
#: E3 gefallen; was bleibt, steht hier, und jede Zeile sagt, warum sie kein
#: Fließtext ist.
#:
#: **Dass sie eine Liste ist, ist ihr Mangel.** Eine Breite gehört wie Farbe und
#: Schrift in ein Token (Regel 4) — dann ersetzt ein Suchlauf diese Aufzählung.
#: Das ist der nächste Schritt und ausdrücklich nicht dieser Commit.
KASTENBREITEN: dict[str, dict[str, tuple[int, str]]] = {
    "config_editor/experiment.py": {
        "max-w-2xl": (1, "Textfeld für die Fragestellung — ein Bedienelement"),
    },
    "config_editor/llm_pipeline.py": {
        "max-w-xs": (1, "Zahlenfeld «Checkpoint-Intervall»"),
        "max-w-lg": (1, "Textfeld «Lauf fortsetzen» — nimmt eine Run-ID auf"),
    },
    "config_editor/macro.py": {
        "max-w-[10rem]": (1, "Zahlenfeld für die Anzahl der Regelzeilen"),
        "max-w-xs": (1, "Zahlenfeld «Startwert» einer Systemgröße"),
    },
    "config_editor/micro.py": {
        "max-w-sm": (3, "Zahlenfelder des Buchungs- und Sättigungsmodells"),
        "max-w-xs": (1, "Auswahlfeld «Verteilung»"),
    },
    "config_editor/start_flow.py": {
        "max-w-xs": (1, "Zahlenfeld «Ticks» — die Lauflänge ist eine dreistellige Zahl"),
    },
    "landing_route.py": {
        "max-w-xl": (1, "Die Landingpage ist vom UI/UX-Audit ausdrücklich ausgenommen"),
    },
    "views/explorer.py": {
        "max-w-3xl": (
            2,
            "Sprechblasen: Die Breite trägt hier Bedeutung — wer spricht. "
            "Zusammen mit `ml-auto` unterscheidet sie Frage von Antwort; "
            "füllten beide den Rahmen, wäre die Ausrichtung sinnlos",
        ),
    },
}

_MAX_W = re.compile(r"\bmax-w-(?:\[[^\]\s]+\]|[\w.]+)")


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


def _python_dateien() -> list[Path]:
    return sorted(p for p in WEB_ROOT.rglob("*.py") if "__pycache__" not in p.parts)


def _literale(pfad: Path) -> list[str]:
    """Jede Zeichenkette einer Datei — auch die in einem Funktionsrumpf.

    Über den Syntaxbaum und nicht über die Zeilen, weil eine Klassenliste
    mehrzeilig zusammengesetzt sein kann.

    **Docstrings fallen heraus, und das ist beim ersten Durchlauf gemessen
    worden.** Der erste Anlauf nahm sie mit — mit dem Argument, ein Fehlalarm
    koste nur eine Formulierung. Er kostete mehr: Die Docstrings von `alert`,
    `explainer` und `note` *erzählen* vom abgeschafften Lesemaß, weil genau
    diese Geschichte der Grund ist, aus dem es niemand wieder einbaut. Ein
    Wächter, der die Begründung seiner eigenen Zusage verbietet, erzwingt, dass
    sie gelöscht wird. Zeilenkommentare (`#`) stehen ohnehin nicht im
    Syntaxbaum — diese Auswahl stellt Docstrings mit ihnen gleich.
    """

    baum = ast.parse(pfad.read_text(encoding="utf-8"))
    docs = {
        id(knoten.body[0].value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and knoten.body
        and isinstance(knoten.body[0], ast.Expr)
        and isinstance(knoten.body[0].value, ast.Constant)
        and isinstance(knoten.body[0].value.value, str)
    }
    return [
        knoten.value
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.Constant)
        and isinstance(knoten.value, str)
        and id(knoten) not in docs
    ]


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
    """Jeder Deckel im Stylesheet benutzt ein Token.

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
    je Schriftgröße eine andere Breite. Sie darf auch nicht zurückkommen, wenn
    jemand das Lesemaß wiederbelebt — dann wäre der Befund Q1 zurück.
    """

    in_zeichen = re.findall(r"max-width:\s*[\d.]+ch", _css())

    assert not in_zeichen, f"Deckel in `ch`: {in_zeichen}"


# --- Es gibt kein Maß für Fließtext mehr -------------------------------------


class TestFliesstextHatKeinenDeckel:
    """**Die tragende statische Zusage.** Das Lesemaß ist weg, in jeder Schreibweise.

    Gemessen wird es zweimal, weil es zwei Wege zurück gibt: als Regel im
    Stylesheet und als Klasse an einer Aufrufstelle. Die *Wirkung* — dass ein
    Absatz seinen Rahmen wirklich füllt — kann ohne Layout niemand prüfen; das
    ist Teil 7 des Browser-Wächters.
    """

    @pytest.mark.parametrize("name", ABGESCHAFFT)
    def test_the_stylesheet_has_no_reading_measure(self, name):
        css = CSS.read_text(encoding="utf-8")
        # Kommentare dürfen davon erzählen — die Geschichte ist der Grund,
        # warum niemand es wieder einbaut.
        assert name not in _nur_deklarationen(css), (
            f"`{name}` steht wieder im Stylesheet. Fließtext bekommt keinen "
            "Deckel mehr (Rücknahme von E3 am 2026-09-12)."
        )

    @pytest.mark.parametrize("name", ABGESCHAFFT)
    def test_no_module_uses_the_reading_measure(self, name):
        befunde = [
            f"{pfad.relative_to(WEB_ROOT)}: {text[:60]!r}"
            for pfad in _python_dateien()
            for text in _literale(pfad)
            if re.search(rf"\b{re.escape(name)}\b", text)
        ]

        assert not befunde, f"`{name}` an einer Aufrufstelle:\n  " + "\n  ".join(befunde)

    def test_tailwind_has_no_second_reading_measure(self):
        """`max-w-prose` ist Tailwinds eigenes Lesemaß — 65ch, gemessen 88 Zeichen.

        Die Zusage kommt aus P3.17 und gilt weiter, nur mit anderer Begründung:
        Damals war es ein **zweites, ungeeichtes** Maß neben `af-mass`; heute
        gibt es überhaupt keins, und ein Name, der wie ein Lesemaß aussieht,
        bringt es am leichtesten zurück.
        """

        befunde = [
            f"{pfad.relative_to(WEB_ROOT)}: {text[:60]!r}"
            for pfad in _python_dateien()
            for text in _literale(pfad)
            if "max-w-prose" in text
        ]

        assert not befunde, "`max-w-prose` unter `dashboard/web/`:\n  " + "\n  ".join(befunde)


class TestJederKastendeckelSagtWarum:
    """Sperrklinke über `max-w-*`: Was bleibt, ist ein Bedienelement.

    **Sie schlägt in beide Richtungen an.** Ein neuer Deckel ist zu begründen;
    ein weggeräumter gehört ausgetragen, sonst schwebt die Liste über dem
    Ist-Stand und ist aus dem falschen Grund grün — dieselbe Mechanik wie beim
    Höhenwächter.
    """

    def test_every_tailwind_cap_is_registered(self):
        gefunden: dict[str, Counter[str]] = {}
        for pfad in _python_dateien():
            zaehler: Counter[str] = Counter()
            for text in _literale(pfad):
                zaehler.update(_MAX_W.findall(text))
            if zaehler:
                gefunden[pfad.relative_to(WEB_ROOT).as_posix()] = zaehler

        erwartet = {
            datei: Counter({klasse: anzahl for klasse, (anzahl, _) in eintraege.items()})
            for datei, eintraege in KASTENBREITEN.items()
        }

        assert gefunden == erwartet, (
            "Die Deckel in `max-w-*` weichen von der Sperrklinke ab.\n"
            f"  gefunden:  {gefunden}\n"
            f"  erwartet:  {erwartet}\n\n"
            "Ein neuer Deckel an einem **Bedienelement** gehört mit Grund in "
            "`KASTENBREITEN`. Ein Deckel an **Fließtext** gehört weg: Text "
            "füllt seinen Rahmen (Rücknahme von E3). Ein weggeräumter Deckel "
            "gehört ausgetragen."
        )

    def test_every_entry_carries_a_reason(self):
        ohne = [
            f"{datei} → {klasse}"
            for datei, eintraege in KASTENBREITEN.items()
            for klasse, (_, grund) in eintraege.items()
            if len(grund.strip()) < 20
        ]

        assert not ohne, (
            "Diese Einträge nennen keinen Grund: "
            + ", ".join(ohne)
            + "\n\nEine Ausnahme ohne Grund ist in sechs Monaten eine Regel."
        )


# --- Der Wächter über sich selbst --------------------------------------------


class TestDerWaechterWuerdeEinenRueckfallBemerken:
    """**Ein Wächter, der nie etwas sieht, könnte auch blind sein.**

    Geprüft werden die Suchen selbst und nicht das Stylesheet — sonst müsste
    jeder dieser Tests erst etwas kaputt machen.
    """

    def test_a_literal_cap_is_found(self):
        """Der Rückfall, der vor U1.2 dreimal passiert ist: ein Deckel als Literal."""

        erfunden = ".af-irgendwas {\n    max-width: 46rem;\n}"
        literale = [
            wert.strip()
            for wert in re.findall(r"max-width:\s*([^;{]+)", erfunden)
            if not wert.strip().startswith("var(--breite") and wert.strip() != "none"
        ]

        assert literale == ["46rem"], f"Die Suche findet den Rückfall nicht: {literale}"

    def test_a_returning_reading_measure_is_found(self):
        erfunden = ".af-mass {\n    max-width: var(--breite-lesen);\n}"

        for name in ABGESCHAFFT:
            if name == "af-breite-lesen":
                continue
            assert name in _nur_deklarationen(erfunden), f"`{name}` wird nicht gefunden"

    def test_a_new_tailwind_cap_is_found(self):
        """Und die Sperrklinke: Ein zusätzlicher Deckel muss auffallen.

        Gemessen an der Klasse, die U1.2 übersehen hat — und an der Schreibweise
        mit Klammern, die ein Muster für Wortzeichen allein nicht fasst.
        """

        assert _MAX_W.findall('x = "font-body max-w-3xl mb-2"') == ["max-w-3xl"]
        assert _MAX_W.findall('x = "max-w-[42rem]"') == ["max-w-[42rem]"]
