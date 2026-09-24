"""Ein Text der Oberfläche hat ein Budget (P7.2-U2.5, aus D3).

**Der Befund (Q6, Q8 des UI/UX-Audits):** Die Oberfläche erklärt viel und an
manchen Stellen zu viel — ein Hinweis von 451 Zeichen über einem Diagramm, ein
Kachelhinweis, der die Kachel überragt. Wer alles liest, liest nichts.

**Was gilt** (Entscheidung D3, Werte aus dem Audit): ein **Vorspann** höchstens
200 Zeichen, ein **Hinweis** 280, ein **Kachelhinweis** 80. Das sind Budgets für
geschriebenen Text, keine Aussage über Wichtigkeit: Was mehr braucht, gehört
eine Ebene tiefer — hinter eine Klappe, ins Handbuch oder in die Erklärung am
Feld.

**Gemessen wird, was jemand geschrieben hat.** Ein Platzhalter (`{…}`) zählt mit
drei Zeichen, weil seine Länge erst im Lauf feststeht; die Zusage gilt der
Textmenge, die im Quelltext steht. Gesucht wird über den Syntaxbaum, nicht über
eine Liste der bekannten Stellen.
"""

from __future__ import annotations

import ast
from pathlib import Path

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Baustein → (welches Argument den Text trägt, Budget in Zeichen).
BUDGETS = {
    "hinweis": ("text", 280),
    "lede": ("text", 200),
    "kachel": ("hint", 80),
}

#: Wie viele Texte die Suche mindestens findet — gegen die eigene Blindheit.
TEXTE_MIN = 60

#: Ein Platzhalter in einem f-String, so lang gezählt, wie er im Quelltext steht.
PLATZHALTER = "{…}"


def _wortlaut(knoten: ast.AST) -> str | None:
    """Der geschriebene Text eines Arguments — oder `None`, wenn es keiner ist."""

    if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str):
        return knoten.value
    if isinstance(knoten, ast.JoinedStr):
        return "".join(
            teil.value if isinstance(teil, ast.Constant) else PLATZHALTER for teil in knoten.values
        )
    return None


def _texte(quelle: str) -> list[tuple[str, int, int]]:
    """(Baustein, Zeile, Länge) jedes Textes, für den ein Budget gilt."""

    gefunden: list[tuple[str, int, int]] = []
    for knoten in ast.walk(ast.parse(quelle)):
        if not isinstance(knoten, ast.Call):
            continue
        name = getattr(knoten.func, "attr", None)
        if name not in BUDGETS:
            continue
        argument, _ = BUDGETS[name]
        kandidaten: list[ast.AST] = []
        if argument == "text" and knoten.args:
            kandidaten.append(knoten.args[0])
        if argument == "hint":
            if len(knoten.args) >= 3:
                kandidaten.append(knoten.args[2])
            kandidaten += [w.value for w in knoten.keywords if w.arg == "hint"]
        for kandidat in kandidaten:
            wortlaut = _wortlaut(kandidat)
            if wortlaut:
                gefunden.append((name, knoten.lineno, len(wortlaut)))
    return gefunden


def _befunde() -> list[str]:
    befunde: list[str] = []
    for pfad in sorted(WEB_ROOT.rglob("*.py")):
        ort = pfad.relative_to(WEB_ROOT).as_posix()
        for name, zeile, laenge in _texte(pfad.read_text(encoding="utf-8")):
            budget = BUDGETS[name][1]
            if laenge > budget:
                befunde.append(f"{ort}:{zeile}: ui.{name} — {laenge} Zeichen, Budget {budget}")
    return befunde


def _alle_texte() -> list[tuple[str, int, int]]:
    return [
        eintrag
        for pfad in sorted(WEB_ROOT.rglob("*.py"))
        for eintrag in _texte(pfad.read_text(encoding="utf-8"))
    ]


class TestJederTextHatSeinBudget:
    def test_no_text_exceeds_its_budget(self):
        befunde = _befunde()

        assert not befunde, "\n  ".join(
            [
                "Diese Texte sprengen ihr Budget:",
                *befunde,
                "Was mehr braucht, gehört eine Ebene tiefer — hinter eine Klappe, ins "
                "Handbuch oder in die Erklärung am Feld.",
            ]
        )

    def test_the_search_reads_the_whole_surface(self):
        gefunden = _alle_texte()

        assert len(gefunden) >= TEXTE_MIN, f"Nur {len(gefunden)} Texte gefunden — sucht er noch?"
        assert {name for name, _, _ in gefunden} == set(BUDGETS), (
            "Nicht jeder Baustein mit Budget kommt in der Oberfläche vor: "
            f"{sorted({name for name, _, _ in gefunden})}"
        )

    def test_the_search_would_notice_a_relapse(self):
        quelle = (
            'ui.hinweis("x" * 281, "info")\n'
            'ui.hinweis("kurz", "info")\n'
            'ui.lede("y" * 201)\n'
            'ui.kachel("Titel", "Wert", "z" * 81)\n'
            'ui.kachel("Titel", "Wert", hint="z" * 81)\n'
            'ui.kachel("Titel", "Wert")\n'
        )

        # Der Multiplikator steht im Syntaxbaum, nicht sein Ergebnis: Gemessen
        # werden deshalb die Zeilen mit wörtlichem Text.
        gemessen = _texte('ui.hinweis("' + "x" * 281 + '", "info")\nui.lede("kurz")\n')

        assert [(name, laenge) for name, _, laenge in gemessen] == [("hinweis", 281), ("lede", 4)]
        assert _texte(quelle) == [("hinweis", 2, 4)]
