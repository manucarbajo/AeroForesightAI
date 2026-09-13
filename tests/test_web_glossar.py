"""Oberfläche und Handbuch nennen die Dinge so wie ihr Glossar (P7.2-U2.4).

**Der Befund (Q6 des UI/UX-Audits):** «Figures», «Events», «Run-ID», «Ground
Truth», «Mock» neben deutschen Beschriftungen; «Tick» überall, aber «ab
Runde», «über … Runden» und «je Runde» im Regel-Editor des Modells. Wer
dasselbe Ding unter zwei Namen liest, sucht nach zwei Dingen.

**Was gilt** (von Haiko entschieden am 2026-09-13): Tick statt Runde, Lauf
statt Run, Kennung statt Run-ID, Diagramme statt Figures, Ereignisse statt
Events, «Kennzahlen aus der Rechnung» statt Ground Truth, «ohne Sprachmodell»
statt Mock — **auf der Oberfläche und im Handbuch**. **Code bleibt Code:** Was
in Backticks oder einem Codeblock steht — ein Dateiname, ein Feldname, eine
Option wie `--mock-llm` —, ist ausgenommen, weil es genau so heißt.

**Gesucht, nicht aufgezählt:** jede Zeichenkette unter `dashboard/web/`, die
kein Docstring ist, die Beschriftungen, die die Oberfläche aus `src/`
übernimmt (`COMPUTE_MODE_LABELS`), und jede Zeile jedes Handbuchkapitels.
Groß- und Kleinschreibung zählen: `figures-tabs` ist eine Kennung, «Figures»
eine Beschriftung.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from src.reporting.output_writer.provenance import COMPUTE_MODE_LABELS

WURZEL = Path(__file__).resolve().parents[1]
WEB_ROOT = WURZEL / "dashboard" / "web"
HANDBUCH = WURZEL / "docs" / "handbuch"

#: Variante → das Wort aus dem Glossar.
VARIANTEN = {
    r"\bRunden?\b": "Tick",
    r"[Mm]odellrunden?\b": "Tick",
    r"\bRuns?\b": "Lauf",
    r"\bRun-ID\b": "Kennung",
    r"\bFigures?\b": "Diagramme",
    r"\bEvents?\b": "Ereignisse",
    r"\bGround Truth\b": "Kennzahlen aus der Rechnung",
    r"\bMock\b": "ohne Sprachmodell",
    # Die Diagramme der Animation (U2.4 Teil 2): deutsche Titel, Fachbegriffe
    # nur mit deutscher Erklärung.
    r"\bSurplus\b|\bSwarm\b|\bPulse\b|\bBehavioral\b|\bIncome\b": "deutscher Diagrammtitel",
    r"\bWTP\b": "Zahlungsbereitschaft",
    r"\bScatter": "Streudiagramm",
    r"\bHistory\b": "Personenverlauf",
    # Geld heißt «€» (U2.6, von Haiko entschieden am 2026-09-13). Der
    # Einheitsschlüssel `EUR` in `configs/` ist ein Datenwert und steht in
    # Backticks, wo das Handbuch ihn nennt.
    r"\bEUR\b": "€",
}

#: (Ort ohne Zeile, Ausschnitt des Textes) → Grund. Eine Variante, die hier
#: steht, **erklärt** ein Wort, statt etwas zu beschriften.
AUSNAHMEN = {
    ("docs/handbuch/glossar.md", "Im Englischen WTP, willingness to pay."): (
        "Der Glossareintrag «Zahlungsbereitschaft» nennt die englische Entsprechung, "
        "damit man sie in der Fachliteratur wiederfindet"
    ),
}

#: Wie viele sichtbare Zeichenketten und Handbuchzeilen die Suche mindestens
#: liest — gegen die eigene Blindheit.
TEXTE_MIN = 1000
HANDBUCHZEILEN_MIN = 3000

_CODE = re.compile(r"`[^`\n]*`")
_CODEBLOCK = re.compile(r"```.*?```", re.S)


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


def _zeilen(markdown: str) -> list[tuple[int, str]]:
    """Jede Zeile eines Kapitels — ein Codeblock bleibt als Leerzeilen stehen."""

    ohne_bloecke = _CODEBLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), markdown)
    return list(enumerate(ohne_bloecke.splitlines(), 1))


def _ausgenommen(ort: str, text: str) -> bool:
    datei = ort.rsplit(":", 1)[0]
    return any(datei == a_datei and ausschnitt in text for a_datei, ausschnitt in AUSNAHMEN)


def _befunde(texte: list[tuple[str, str]]) -> list[str]:
    befunde: list[str] = []
    for ort, text in texte:
        if _ausgenommen(ort, text):
            continue
        ohne_code = _CODE.sub("", text)
        for muster, wort in VARIANTEN.items():
            treffer = re.search(muster, ohne_code)
            if treffer:
                befunde.append(f"{ort}: «{treffer.group(0)}» statt «{wort}» — {text[:80]!r}")
    return befunde


def _oberflaeche() -> list[tuple[str, str]]:
    texte: list[tuple[str, str]] = []
    for pfad in sorted(WEB_ROOT.rglob("*.py")):
        ort = pfad.relative_to(WEB_ROOT).as_posix()
        texte += [(f"{ort}:{z}", t) for z, t in _texte(pfad.read_text(encoding="utf-8"))]
    texte += [(f"COMPUTE_MODE_LABELS[{k!r}]", v) for k, v in COMPUTE_MODE_LABELS.items()]
    return texte


def _handbuch() -> list[tuple[str, str]]:
    texte: list[tuple[str, str]] = []
    for pfad in sorted(HANDBUCH.glob("*.md")):
        ort = pfad.relative_to(WURZEL).as_posix()
        texte += [(f"{ort}:{z}", t) for z, t in _zeilen(pfad.read_text(encoding="utf-8"))]
    return texte


class TestDieOberflaecheSprichtIhrGlossar:
    def test_no_visible_text_uses_a_variant(self):
        befunde = _befunde(_oberflaeche())

        assert not befunde, "\n  ".join(
            [
                "Diese Texte nennen ein Ding anders als das Glossar:",
                *befunde,
                "Code in Backticks ist ausgenommen; eine Beschriftung ist es nicht.",
            ]
        )

    def test_the_search_reads_the_whole_surface(self):
        gelesen = len(_oberflaeche())

        assert gelesen >= TEXTE_MIN, f"Nur {gelesen} Zeichenketten gelesen — sucht er noch?"

    def test_the_search_would_notice_a_relapse(self):
        quelle = (
            '"""Ein Docstring darf von Runs erzählen."""\n'
            'A = "Noch keine Runs vorhanden."\n'
            'B = "Ansicht Figures, Tab «Events»"\n'
            'C = "`run_scenario.md` fehlt, Option `--mock-llm`"\n'
            'D = "figures-tabs"\n'
            'E = "ab Runde"\n'
            'F = "Surplus Pulse: Zahlungsbereitschaft (WTP) in €"\n'
        )
        befunde = _befunde([(f"probe:{z}", t) for z, t in _texte(quelle)])

        assert [b.split(":")[1] for b in befunde] == ["2", "3", "3", "6", "7", "7"], befunde


class TestNamenUndEinheitenAusDemKatalog:
    """U2.6: Die Namen und Einheiten der Systemgrößen kommen aus `config_catalog`.

    Dieser Wächter liest sonst nur `dashboard/web/` — die Achsentitel der
    Diagramme und die Felder des Modell-Bereichs nehmen ihre Beschriftung aber
    aus `PROPERTY_LABELS` und `EINHEITEN`. **Geprüft werden die angezeigten
    Werte, nicht die Schlüssel:** `"EUR"` als Schlüssel ist die Einheit, die in
    `configs/properties.json` steht.
    """

    def test_every_label_and_unit_speaks_the_glossary(self):
        from dashboard import config_catalog

        texte = [(f"PROPERTY_LABELS[{k!r}]", v) for k, v in config_catalog.PROPERTY_LABELS.items()]
        texte += [
            (f"EINHEITEN[{k!r}]", text)
            for k, (kurz, lang) in config_catalog.EINHEITEN.items()
            for text in (kurz, lang)
        ]

        befunde = _befunde(texte)

        assert not befunde, "\n  ".join(["Namen und Einheiten im Katalog:", *befunde])

    def test_the_catalog_really_names_money(self):
        """Gegen die eigene Blindheit: Mindestens ein Name trägt eine Geldeinheit."""

        from dashboard import config_catalog

        assert any("€" in name for name in config_catalog.PROPERTY_LABELS.values())


class TestDasHandbuchSprichtDasselbeGlossar:
    """U2.4 Teil 3: Das Handbuch sagte 155-mal «Runde», während der Bildschirm «Tick» sagt."""

    def test_no_chapter_uses_a_variant(self):
        befunde = _befunde(_handbuch())

        assert not befunde, "\n  ".join(
            [
                "Diese Handbuchzeilen nennen ein Ding anders als das Glossar:",
                *befunde,
                "Code in Backticks oder Codeblöcken ist ausgenommen. Eine Erklärung "
                "eines Wortes gehört mit Grund in `AUSNAHMEN`.",
            ]
        )

    def test_the_search_reads_the_whole_handbook(self):
        gelesen = len(_handbuch())

        assert gelesen >= HANDBUCHZEILEN_MIN, f"Nur {gelesen} Handbuchzeilen gelesen."

    def test_every_exception_still_has_its_place_and_a_reason(self):
        texte = _handbuch() + _oberflaeche()

        for (datei, ausschnitt), grund in AUSNAHMEN.items():
            assert any(
                ort.rsplit(":", 1)[0] == datei and ausschnitt in text for ort, text in texte
            ), f"Ausnahme ohne Stelle dahinter: {datei} — {ausschnitt!r}"
            assert len(grund) >= 30, f"Ausnahme ohne Grund: {datei}"

    def test_code_blocks_and_rounded_words_are_not_findings(self):
        kapitel = (
            "In jedem Tick bucht, wer buchen will.\n"
            "```\npython -m src.run_simulation --rounds 40  # Runde\n```\n"
            "Gerundete Werte und eine Planungsrunde sind keine Runde.\n"
            "Ein Tick ist eine Modellrunde.\n"
        )
        befunde = _befunde([(f"probe.md:{z}", t) for z, t in _zeilen(kapitel)])

        assert [b.split(":")[1] for b in befunde] == ["5", "6"], befunde
