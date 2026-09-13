"""Wie die Oberfläche Zeit schreibt (P7.2-U2.6).

**Eine Stelle, weil die Frage an vielen Orten gestellt wird.** Der Zeitstempel
eines Laufs stand in der Kopfzeile der Ergebnisse und in der Übersicht roh aus
`run_metadata.json` — «2026-09-07T18:25:55.248822+00:00», Mikrosekunden und
Zeitzone eingeschlossen.

**In den Daten bleibt er, wie er ist:** ISO 8601 mit Zeitzone ist das richtige
Format für ein Artefakt, das man maschinell liest und über Zeitzonen hinweg
vergleicht. Umgewandelt wird erst beim Anzeigen.
"""

from __future__ import annotations

from datetime import datetime


def zeitpunkt(wert: object) -> str:
    """Ein Zeitstempel lesbar und in der Ortszeit — «13.09.2026, 18:29».

    Die Läufe schreiben ISO 8601 mit Zeitzone (`+00:00`, ältere Testdaten `Z`).
    **Was sich nicht lesen lässt, bleibt, wie es ist:** Lieber ein roher Wert
    als ein erfundener. Fehlt er ganz, steht ein Strich.
    """

    if not isinstance(wert, str) or not wert.strip():
        return "—"
    try:
        moment = datetime.fromisoformat(wert.strip())
    except ValueError:
        return wert
    if moment.tzinfo is not None:
        moment = moment.astimezone()
    return moment.strftime("%d.%m.%Y, %H:%M")
