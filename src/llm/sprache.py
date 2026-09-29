"""Alles, was das Sprachmodell schreibt, ist deutsch — eine Anweisung, an einer Stelle (P8-V2).

**Der Befund:** Am 2026-09-29 waren 15 von 17 Texten der Agenten englisch
(«Implement a pilot program for SAF-powered flights …»), unter einer deutschen
Oberfläche. Die Prompts der Agenten sind englisch und legten keine
Ausgabesprache fest; der Abschlusstext und die Abfrage verlangten Deutsch, jeder
auf seine Weise, die Szenario-Node gar nicht.

**Die Anweisung steht deshalb hier und nur hier**, und jeder Aufrufer hängt sie
über :func:`auf_deutsch` an seinen Prompt. **Ans Ende**, direkt vor die
Antwort: Dort steht sie dem Schreiben am nächsten, bei Prompts von mehreren
Tausend Zeichen und einem kleinen Modell wie `llama3.2`. Ob das reicht, misst der
Prüfsatz (`pruefsatz_sprachmodell`, Spalte «englisch»). Gehalten von
`tests/test_ausgabesprache.py`, der jeden Aufruf ``.call(`` in ``src/`` **sucht**
und verlangt, dass sein Prompt durch diese Funktion geht.

**Was englisch bleibt, und warum:** JSON-Schlüssel, die Werte von
``event_type`` und Kennungen wie ``F1.1``, ``C1`` oder ``NO_OP``. Der Code liest
sie wörtlich (``agent_node`` erkennt ``NO_OP`` am genauen Wort); übersetzt das
Modell sie, bricht das Einlesen und nicht die Sprache.
"""

from __future__ import annotations

#: Die Sprachanweisung, deutsch und — für Prompts, die englisch geschrieben sind —
#: noch einmal englisch, damit das Modell sie in beiden Lesarten findet.
AUSGABESPRACHE = (
    "## Sprache der Antwort (verbindlich)\n"
    "Schreibe jeden freien Text deiner Antwort auf Deutsch: Begründungen, Aktionen, "
    "Beschreibungen von Ereignissen, Titel, Zusammenfassungen und Erzählungen. "
    "JSON-Schlüssel, die Werte von event_type und Kennungen wie F1.1, C1 oder NO_OP "
    "bleiben genau so, wie sie vorgegeben sind.\n"
    "Language: write every free-text value in German. Keep JSON keys, event_type values "
    "and identifiers such as F1.1, C1 or NO_OP exactly as specified."
)


def auf_deutsch(prompt: str, *, schluss: str = "") -> str:
    """Den Prompt mit der Sprachanweisung am Ende — vor einem ``schluss`` wie «ANSWER:».

    ``schluss`` gibt es für Prompts, deren letzte Zeile das Modell zum Antworten
    auffordert: Die Anweisung gehört davor, nicht dahinter.
    """

    return f"{prompt.rstrip()}\n\n{AUSGABESPRACHE}{schluss}"
