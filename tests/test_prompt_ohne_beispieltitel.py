"""Der Prompt des Abschlusstexts gibt keinen Titel vor (P8, 2026-10-01).

**Der Befund:** Der Prompt nannte für die Szenario-Titel das Beispiel
«Nachhaltigkeitskrise bei hohem Wachstum». `llama3.2` übernahm es in **allen
sieben** Abschlusstexten des Vorführbestands als Gesamttitel — und «hohes
Wachstum» zog «Nachfrage steigt» nach sich, wo die Nachfrage gerechnet sinkt.
Ein erster Anlauf schrieb die Anweisung als Wert ins JSON-Schema
(`"title": "kurzer Gesamttitel …, der … sagt"`); das Modell übernahm **sie**
wörtlich. Was im Prompt als Text steht, wird abgeschrieben; ein Platzhalter in
eckigen Klammern nicht.

Gemessen an je neun Antworten (Pitch-Fall, Referenz, Transformationskonflikt):
Titel mit «Wachstum» 9 → 0, markierte Widersprüche insgesamt 16 → 9; Texte mit
mindestens einem Widerspruch 5 → 5. Die Wirkung auf das Modell misst der
Prüfsatz; hier steht, was sich ohne Modell prüfen lässt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROMPT = Path(__file__).resolve().parents[1] / "src" / "prompts" / "run_scenario.md"


def _text() -> str:
    return PROMPT.read_text(encoding="utf-8")


def _schema() -> dict:
    text = _text()
    anfang = text.index("{\n")
    tiefe = 0
    for i, zeichen in enumerate(text[anfang:], start=anfang):
        tiefe += {"{": 1, "}": -1}.get(zeichen, 0)
        if tiefe == 0:
            return json.loads(text[anfang : i + 1])
    raise AssertionError("Kein JSON-Schema im Prompt gefunden")


def test_keine_zeile_ueber_einen_titel_nennt_ein_beispiel():
    zeilen = [z for z in _text().splitlines() if "title" in z.lower() or "titel" in z.lower()]

    assert zeilen, "Misst der Test ins Leere?"
    assert not [z for z in zeilen if re.search(r"z\.\s?B\.", z)], zeilen


def test_die_titel_im_schema_sind_platzhalter():
    schema = _schema()
    titel = [schema["title"], *(s["title"] for s in schema["scenarios"])]

    assert all(t.startswith("[") and t.endswith("]") for t in titel), titel


def test_das_alte_beispiel_steht_nirgends_mehr():
    assert "Nachhaltigkeitskrise bei hohem Wachstum" not in _text()
    assert "starkes Wachstum vs. radikale Verbote" not in _text()
