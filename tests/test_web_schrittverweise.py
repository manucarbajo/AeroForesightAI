"""Ein Text, der auf einen Schritt verweist, nimmt ihn aus `wizard.STEPS` (P7.2-U2.2).

**Der Befund (UI/UX-Audit vom 2026-09-11):** Die Karte «Eigene Einstellungen»
beschrieb sich mit «Was Sie in den **Schritten 4 bis 7** selbst eingestellt
haben» — die Schrittfolge hat seit P2.0-C sechs Schritte, und eigene Werte
entstehen seit P1.9-W3.1 im Bereich «Modell». Der Modell-Bereich schickte zum
Einschalten eigener Werte in den Schritt **«Ausgangslage»**, den es seit P2.0-C
nicht mehr gibt. Beide Texte waren beim Schreiben richtig; die Schrittfolge hat
sich dreimal geändert, die Texte nie.

**Warum ein Wächter und nicht nur die Korrektur:** Die Schrittfolge wird sich
wieder ändern. Ein Literal wie «Schritt 2» oder «Schritt «Technik»» weiß davon
nichts. Der Wächter liest deshalb jede sichtbare Zeichenkette unter
`dashboard/web/` und meldet

* jeden **Schrittnamen** in Guillemets, den `wizard.STEPS` nicht kennt, und
* jede **Schrittnummer** als Literal — eine Nummer gehört aus der Position in
  `STEPS` berechnet, nicht hingeschrieben.

Docstrings und Kommentare sind ausgenommen: Dort steht Geschichte («auf Schritt
8 kam»), und die soll stehen bleiben.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from dashboard.web.config_editor import wizard

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

SCHRITTNAME = re.compile(r"Schritt(?:e|en|s)?\s+«([^»]+)»")
SCHRITTNUMMER = re.compile(r"Schritt(?:e|en|s)?\s+\d")


def _docstrings(baum: ast.AST) -> set[int]:
    """Die Knoten, die Docstrings sind — sie tragen Geschichte, keinen Bildschirmtext."""

    kennungen: set[int] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            erster = knoten.body[0] if knoten.body else None
            if (
                isinstance(erster, ast.Expr)
                and isinstance(erster.value, ast.Constant)
                and isinstance(erster.value.value, str)
            ):
                kennungen.add(id(erster.value))
    return kennungen


def _sichtbare_texte() -> list[tuple[str, int, str]]:
    texte: list[tuple[str, int, str]] = []
    for datei in sorted(WEB_ROOT.rglob("*.py")):
        baum = ast.parse(datei.read_text(encoding="utf-8"))
        ausgenommen = _docstrings(baum)
        for knoten in ast.walk(baum):
            if (
                isinstance(knoten, ast.Constant)
                and isinstance(knoten.value, str)
                and id(knoten) not in ausgenommen
            ):
                ort = str(datei.relative_to(WEB_ROOT.parent.parent))
                texte.append((ort, knoten.lineno, knoten.value))
    return texte


def funde(texte: list[tuple[str, int, str]], titel: set[str]) -> list[str]:
    ergebnis: list[str] = []
    for ort, zeile, text in texte:
        for name in SCHRITTNAME.findall(text):
            if name not in titel:
                ergebnis.append(f"{ort}:{zeile}: Schritt «{name}» gibt es nicht")
        if SCHRITTNUMMER.search(text):
            ergebnis.append(f"{ort}:{zeile}: Schrittnummer als Literal — {text[:70]!r}")
    return ergebnis


def test_every_step_reference_comes_from_the_step_list():
    titel = {step.title for step in wizard.STEPS}
    gefunden = funde(_sichtbare_texte(), titel)

    assert not gefunden, (
        "Ein sichtbarer Text verweist auf einen Schritt, den `wizard.STEPS` so nicht "
        "kennt:\n  " + "\n  ".join(gefunden)
    )


def test_the_guard_would_notice_a_relapse():
    """Beide Formen, die es gegeben hat, und eine berechnete, die durchgehen muss."""

    texte = [
        ("a.py", 1, "Was Sie in den Schritten 4 bis 7 selbst eingestellt haben."),
        ("b.py", 2, "Einschalten im Schritt «Ausgangslage»."),
        ("c.py", 3, "Einschalten im Schritt «Technik»."),
    ]

    gefunden = funde(texte, {"Technik"})

    assert len(gefunden) == 2
    assert gefunden[0].startswith("a.py:1") and gefunden[1].startswith("b.py:2")


#: Eine Schrittposition in Worten — «im zweiten Schritt». Im Handbuch stand sie an
#: sechs Stellen und war seit P7.13 an allen falsch (Befund N4 der Gegenprüfung
#: vom 2026-09-21): Der zweite Schritt heißt seither «Verläufe».
#: «Im ersten Schritt» bleibt erlaubt: Der erste Schritt ist der, von dem
#: «Zurück» auf den Einstieg führt — das ist eine Aussage über die Position.
SCHRITTPOSITION = re.compile(
    r"\b(?:zweiten|dritten|vierten|fünften|sechsten|siebten|achten)\s+Schritt",
    re.IGNORECASE,
)
HANDBUCH = WEB_ROOT.parent.parent / "docs" / "handbuch"


def test_das_handbuch_nennt_schritte_beim_namen():
    """Nur die Position in Worten, nicht Nummer und Name wie oben.

    Eine Nummer steht im Handbuch an Stellen, an denen sie stimmt: als eigene
    Zählung der ersten Simulation («Schritt 1: Was soll gerechnet werden?»), als
    Beispiel der Ansage («Schritt 6 von 8») und als Geschichte («Der Schritt
    «Ausgangslage» ist entfallen»). Eine Position in Worten war an allen sechs
    Fundstellen ein Ortsverweis — und an allen falsch.
    """

    funde_handbuch = []
    for datei in sorted(HANDBUCH.glob("*.md")):
        flach = " ".join(datei.read_text(encoding="utf-8").split())
        for treffer in SCHRITTPOSITION.finditer(flach):
            funde_handbuch.append(f"{datei.name}: {flach[treffer.start() : treffer.end() + 40]!r}")

    assert not funde_handbuch, "\n".join(funde_handbuch)
