"""Die Oberfläche nennt die Dinge so wie ihr Glossar (P7.2-U2.4).

**Der Befund (Q6 des UI/UX-Audits):** «Figures», «Events», «Run-ID», «Ground
Truth», «Mock» neben deutschen Beschriftungen; «Tick» überall, aber «ab
Runde», «über … Runden» und «je Runde» im Regel-Editor des Modells. Wer
dasselbe Ding unter zwei Namen liest, sucht nach zwei Dingen.

**Was gilt** (von Haiko entschieden am 2026-09-13): Tick statt Runde, Lauf
statt Run, Kennung statt Run-ID, Diagramme statt Figures, Ereignisse statt
Events, «Kennzahlen aus der Rechnung» statt Ground Truth, «ohne Sprachmodell»
statt Mock. **Code bleibt Code:** Was in Backticks steht — ein Dateiname, ein
Feldname, eine Option wie `--mock-llm` —, ist ausgenommen, weil es genau so
heißt.

**Gesucht, nicht aufgezählt:** jede Zeichenkette unter `dashboard/web/`, die
kein Docstring ist, dazu die Beschriftungen, die die Oberfläche aus `src/`
übernimmt (`COMPUTE_MODE_LABELS`). Groß- und Kleinschreibung zählen:
`figures-tabs` ist eine Kennung, «Figures» eine Beschriftung.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from src.reporting.output_writer.provenance import COMPUTE_MODE_LABELS

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Variante → das Wort aus dem Glossar.
VARIANTEN = {
    r"\bRunden?\b": "Tick",
    r"\bRuns?\b": "Lauf",
    r"\bRun-ID\b": "Kennung",
    r"\bFigures?\b": "Diagramme",
    r"\bEvents?\b": "Ereignisse",
    r"\bGround Truth\b": "Kennzahlen aus der Rechnung",
    r"\bMock\b": "ohne Sprachmodell",
}

#: Wie viele sichtbare Zeichenketten die Suche mindestens liest — gegen die
#: eigene Blindheit.
TEXTE_MIN = 1000

_CODE = re.compile(r"`[^`\n]*`")


def _texte(quelle: str) -> list[tuple[int, str]]:
    """Jede Zeichenkette eines Moduls, die kein Docstring ist — (Zeile, Text)."""

    baum = ast.parse(quelle)
    docstrings = {
        id(knoten.body[0].value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and knoten.body
        and isinstance(knoten.body[0], ast.Expr)
        and isinstance(knoten.body[0].value, ast.Constant)
    }
    return [
        (knoten.lineno, knoten.value)
        for knoten in ast.walk(baum)
        if isinstance(knoten, ast.Constant)
        and isinstance(knoten.value, str)
        and id(knoten) not in docstrings
    ]


def _befunde(texte: list[tuple[str, str]]) -> list[str]:
    befunde: list[str] = []
    for ort, text in texte:
        ohne_code = _CODE.sub("", text)
        for muster, wort in VARIANTEN.items():
            treffer = re.search(muster, ohne_code)
            if treffer:
                befunde.append(f"{ort}: «{treffer.group(0)}» statt «{wort}» — {text[:80]!r}")
    return befunde


def _alle_texte() -> list[tuple[str, str]]:
    texte: list[tuple[str, str]] = []
    for pfad in sorted(WEB_ROOT.rglob("*.py")):
        ort = pfad.relative_to(WEB_ROOT).as_posix()
        texte += [(f"{ort}:{z}", t) for z, t in _texte(pfad.read_text(encoding="utf-8"))]
    texte += [(f"COMPUTE_MODE_LABELS[{k!r}]", v) for k, v in COMPUTE_MODE_LABELS.items()]
    return texte


class TestDieOberflaecheSprichtIhrGlossar:
    def test_no_visible_text_uses_a_variant(self):
        befunde = _befunde(_alle_texte())

        assert not befunde, "\n  ".join(
            [
                "Diese Texte nennen ein Ding anders als das Glossar:",
                *befunde,
                "Code in Backticks ist ausgenommen; eine Beschriftung ist es nicht.",
            ]
        )

    def test_the_search_reads_the_whole_surface(self):
        gelesen = len(_alle_texte())

        assert gelesen >= TEXTE_MIN, f"Nur {gelesen} Zeichenketten gelesen — sucht er noch?"

    def test_the_search_would_notice_a_relapse(self):
        quelle = (
            '"""Ein Docstring darf von Runs erzählen."""\n'
            'A = "Noch keine Runs vorhanden."\n'
            'B = "Ansicht Figures, Tab «Events»"\n'
            'C = "`run_scenario.md` fehlt, Option `--mock-llm`"\n'
            'D = "figures-tabs"\n'
            'E = "ab Runde"\n'
        )
        befunde = _befunde([(f"probe:{z}", t) for z, t in _texte(quelle)])

        assert [b.split(":")[1] for b in befunde] == ["2", "3", "3", "6"], befunde
