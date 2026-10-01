"""Jede Tabellenzeile im Handbuch gehört zu einer Tabelle.

Befund N9 der Gegenprüfung vom 2026-09-21: In `ref-config.md` standen zwei
Zeilen der Dateitabelle dreißig Zeilen weiter unten, ohne Kopf, direkt unter
einem Absatz — gerendert als Fließtext mit sichtbaren Pipe-Zeichen. Markdown
macht daraus keinen Fehler, nur einen Absatz.

Gesucht wird eine Zeile, die mit `|` beginnt, deren Vorgängerzeile weder
selbst eine Tabellenzeile noch leer ist (dann klebt sie an einem Absatz), oder
die nach einer Leerzeile beginnt, ohne dass die nächste Zeile die Trennlinie
`|---|` ist (dann fehlt ihr der Kopf). Codeblöcke sind ausgenommen.
"""

from __future__ import annotations

import re
from pathlib import Path

HANDBUCH = Path(__file__).resolve().parents[1] / "docs" / "handbuch"
TRENNLINIE = re.compile(r"^\|\s*:?-{3,}")


def verwaiste_zeilen(text: str) -> list[int]:
    funde: list[int] = []
    zeilen = text.splitlines()
    im_code = False
    for nummer, zeile in enumerate(zeilen):
        if zeile.lstrip().startswith("```"):
            im_code = not im_code
            continue
        if im_code or not zeile.startswith("|"):
            continue
        davor = zeilen[nummer - 1] if nummer else ""
        if davor.startswith("|"):
            continue
        danach = zeilen[nummer + 1] if nummer + 1 < len(zeilen) else ""
        if davor.strip() or not TRENNLINIE.match(danach):
            funde.append(nummer + 1)
    return funde


def test_keine_tabellenzeile_ohne_tabelle():
    funde = [
        f"{datei.name}:{zeile}"
        for datei in sorted(HANDBUCH.glob("*.md"))
        for zeile in verwaiste_zeilen(datei.read_text(encoding="utf-8"))
    ]

    assert not funde, "Tabellenzeilen ohne Tabelle: " + ", ".join(funde)


def test_der_waechter_saehe_den_befund():
    befund = "Absatz davor.\n| `agents.json` | Akteure |\n| `x.json` | y |\n"
    richtig = "\n| Datei | Inhalt |\n|---|---|\n| `agents.json` | Akteure |\n"

    assert verwaiste_zeilen(befund) == [2]
    assert verwaiste_zeilen("\n" + befund.split("\n", 1)[1]) == [2]
    assert verwaiste_zeilen(richtig) == []
