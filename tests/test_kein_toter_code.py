"""Kein Name in `src/` lebt nur von seiner Definition oder von einem Test (P5.1, 2026-09-11).

**Das Fertig-Kriterium von P5.1, als Messung.** Die Befundliste des Pakets war
abgearbeitet, und die Nachmessung über alle 500 Top-Level-Namen fand **elf
weitere** — keiner stand in der Liste. Sieben hatten keinen einzigen Verweis,
vier hielt nur ein Test am Leben. Dieselbe Lehre wie in Phase 4: Eine Liste
findet, was jemand aufgeschrieben hat.

**Gesucht wird, nicht aufgezählt:** jede Funktion und Klasse auf Modulebene in
`src/`. Sie braucht einen Verweis außerhalb ihrer eigenen Definition — im
eigenen Modul, in einem anderen Modul von `src/`, in `dashboard/`, `scripts/`,
`langgraph_studio/` oder in `pyproject.toml`. **Tests zählen nicht:** Ein Test,
der eine Funktion prüft, die niemand aufruft, sichert nichts ab.

**Die Grenze der Prüfung, ausdrücklich:** Ein Verweis ist ein Bezeichner gleichen
Namens (Name, Attribut, Import, eine Zeichenkette in Bezeichnerform). Das ist
großzügig — gleichnamige Attribute zählen mit —, aber es übersieht nichts, was
über den Namen erreicht wird. Was nur dynamisch erreichbar ist, gehört mit
Begründung in `AUSNAHMEN`; und eine Ausnahme, die keine mehr braucht, wird
gemeldet.
"""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEBENDE_ORTE = ("dashboard", "scripts", "langgraph_studio")

#: (Modul, Name) -> warum er leben darf, obwohl ihn nur Tests benutzen.
AUSNAHMEN: dict[tuple[str, str], str] = {
    ("src/agents/agent_permissions.py", "factor_permission_entry"): (
        "Die Schreibseite der Berechtigungs-Grammatik, Gegenstück zu "
        "`parse_factor_permission`. Das Produkt liest Berechtigungen nur aus "
        "`configs/agent_profiles.json`; schreiben tun sie allein Tests. Ohne "
        "diese Funktion stünde das Präfix `factor_state ` dort ein zweites Mal — "
        "genau die Stelle, die das Modul seit P0.5 abgeschafft hat."
    ),
}


def _bezeichner(baum: ast.AST) -> Counter[str]:
    zaehler: Counter[str] = Counter()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Name):
            zaehler[knoten.id] += 1
        elif isinstance(knoten, ast.Attribute):
            zaehler[knoten.attr] += 1
        elif isinstance(knoten, ast.alias):
            zaehler[knoten.name.split(".")[-1]] += 1
            if knoten.asname:
                zaehler[knoten.asname] += 1
        elif (
            isinstance(knoten, ast.Constant)
            and isinstance(knoten.value, str)
            and knoten.value.isidentifier()
        ):
            zaehler[knoten.value] += 1
    return zaehler


def unbenutzte_namen(
    src: dict[str, str], lebende: dict[str, str], zusatztext: str = ""
) -> list[tuple[str, str]]:
    """(Modul, Name) aller Top-Level-Namen in *src* ohne Verweis außerhalb ihrer Definition."""

    baeume = {pfad: ast.parse(quelle) for pfad, quelle in src.items()}
    je_modul = {pfad: _bezeichner(baum) for pfad, baum in baeume.items()}
    ausserhalb: Counter[str] = Counter()
    for quelle in lebende.values():
        ausserhalb.update(_bezeichner(ast.parse(quelle)))

    befunde = []
    for pfad, baum in baeume.items():
        for knoten in baum.body:
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            name = knoten.name
            if name.startswith("__"):
                continue
            verweise = sum(z[name] for z in je_modul.values()) + ausserhalb[name]
            if verweise == 0 and name not in zusatztext:
                befunde.append((pfad, name))
    return sorted(befunde)


def _quellen(ordner: str) -> dict[str, str]:
    return {
        p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted((ROOT / ordner).rglob("*.py"))
        if "egg-info" not in p.parts
    }


def _heute() -> list[tuple[str, str]]:
    lebende: dict[str, str] = {}
    for ordner in LEBENDE_ORTE:
        lebende.update(_quellen(ordner))
    return unbenutzte_namen(
        _quellen("src"), lebende, zusatztext=(ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )


def test_die_suche_findet_ueberhaupt_namen():
    """Ohne diesen Test wäre der nächste leer und damit grün."""

    anzahl = sum(
        isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for quelle in _quellen("src").values()
        for k in ast.parse(quelle).body
    )

    assert anzahl >= 400, anzahl


def test_kein_name_lebt_nur_von_seiner_definition_oder_einem_test():
    befunde = [befund for befund in _heute() if befund not in AUSNAHMEN]

    assert befunde == [], (
        "Diese Namen ruft außerhalb von Tests niemand auf — entfernen, anschließen "
        "oder mit Grund in AUSNAHMEN: " + "; ".join(f"{m}: {n}" for m, n in befunde)
    )


def test_jede_ausnahme_wird_noch_gebraucht():
    """Eine Ausnahme, deren Name inzwischen benutzt wird oder verschwunden ist, gehört gestrichen."""

    heute = set(_heute())

    veraltet = [schluessel for schluessel in AUSNAHMEN if schluessel not in heute]

    assert veraltet == [], f"Ausnahmen ohne Anlass: {veraltet}"


def test_gegenprobe_ein_toter_name_faellt_auf():
    src = {
        "src/a.py": "def benutzt(): ...\ndef nur_im_test(): ...\nclass Tot: ...\n",
        "src/b.py": "from src.a import benutzt\nbenutzt()\n",
    }
    lebende = {"dashboard/c.py": "x = 1\n"}

    assert unbenutzte_namen(src, lebende) == [("src/a.py", "Tot"), ("src/a.py", "nur_im_test")]
