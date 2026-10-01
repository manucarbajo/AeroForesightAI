"""Wie die Oberfläche Zeit und Zahlen schreibt (P7.2-U2.6, Zahlen seit P8-V6).

**Eine Stelle, weil die Frage an vielen Orten gestellt wird.** Der Zeitstempel
eines Laufs stand in der Kopfzeile der Ergebnisse und in der Übersicht roh aus
`run_metadata.json` — «2026-09-07T18:25:55.248822+00:00», Mikrosekunden und
Zeitzone eingeschlossen.

**In den Daten bleibt er, wie er ist:** ISO 8601 mit Zeitzone ist das richtige
Format für ein Artefakt, das man maschinell liest und über Zeitzonen hinweg
vergleicht. Umgewandelt wird erst beim Anzeigen.

**Und die Modellzeit neben einer Tick-Zahl** (von Haiko entschieden am
2026-09-13): Seit P3.8 ist ein Tick ein Monat, und «40 Ticks» ohne «rund 3
Jahre» liest man leicht als strategischen Horizont. **Sie ist Anzeige, kein
Datum** — Invariante 5 betrifft Daten, und in Config, Checkpoint und Ausgabe
steht weiterhin keines.
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


#: Seit P3.8: ein Tick ist ein Monat. Gemessen an der Kalenderzuordnung des
#: Backtests, nicht gesetzt (`tests/test_web_formate.py`).
TICKS_JE_JAHR = 12


def modellzeit(ticks: object) -> str:
    """Wie lang eine Tick-Zahl in Modellzeit ist — «rund 3 Jahre», «10 Jahre», «6 Monate».

    Unter einem Jahr in Monaten. Glatte Jahre ohne «rund», alles andere auf
    ganze Jahre gerundet **mit** «rund», damit niemand «3 Jahre» für genau 36
    Monate hält. Was keine Zahl ist («?»), ergibt eine leere Zeichenkette: Eine
    unbekannte Länge hat keine Modellzeit.
    """

    try:
        anzahl = int(ticks)  # type: ignore[call-overload]
    except (TypeError, ValueError):
        return ""
    if anzahl <= 0:
        return ""
    if anzahl < TICKS_JE_JAHR:
        return "1 Monat" if anzahl == 1 else f"{anzahl} Monate"
    jahre, rest = divmod(anzahl, TICKS_JE_JAHR)
    if rest == 0:
        return "1 Jahr" if jahre == 1 else f"{jahre} Jahre"
    gerundet = int(anzahl / TICKS_JE_JAHR + 0.5)
    return "rund 1 Jahr" if gerundet == 1 else f"rund {gerundet} Jahre"


def ticks_mit_modellzeit(ticks: object) -> str:
    """«40 Ticks · rund 3 Jahre» — die eine Form für Kacheln, Zeilen und Sätze."""

    zeit = modellzeit(ticks)
    return f"{ticks} Ticks · {zeit}" if zeit else f"{ticks} Ticks"


_DEUTSCH = str.maketrans({",": ".", ".": ","})


def zahl(wert: float, stellen: int = 2) -> str:
    """Eine Zahl, wie man sie auf Deutsch schreibt — «131,94», «1.027,50».

    **Seit dem 2026-10-01.** Bis dahin standen im Leitstand «37.4%» und
    «131.94 €» — englischer Dezimalpunkt in einer deutschen Oberfläche, und
    genau dieses Bild trug eine Folie des Pitches. In den Daten bleibt die Zahl,
    wie sie ist; umgewandelt wird erst beim Anzeigen, wie beim Zeitstempel.
    """

    # Komma und Punkt tauschen die Rollen: aus «1,027.50» wird «1.027,50».
    return f"{wert:,.{stellen}f}".translate(_DEUTSCH)


def euro(wert: float, stellen: int = 2) -> str:
    """Ein Geldbetrag — «131,94 €»."""

    return f"{zahl(wert, stellen)} €"


def prozent(anteil: float, stellen: int = 1) -> str:
    """Ein Anteil zwischen 0 und 1 in Prozent — «37,4 %», mit Leerzeichen nach DIN 5008."""

    return f"{zahl(anteil * 100, stellen)} %"
