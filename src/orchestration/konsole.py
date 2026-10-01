"""Wie der Rechenkern seinen Fortschritt schreibt — und wie man ihn wieder liest.

Das Dashboard zeigt die Ausgabe eines Laufs in seiner Konsole und liest daraus,
wie weit er ist: den Tick, die Dauer je Tick, beim Szenario-Vergleich Anfang und
Ende jedes Szenarios. Bis zum 2026-10-01 schrieb der Rechenkern diese Zeilen
englisch («[tick 14/40] 0.14s — price=…, booking=…», «Sweep: …», «Completed
120 ticks») und das Dashboard las sie mit eigenen Mustern in
`dashboard/web/runner.py` — zwei Stellen, die dasselbe Format kennen mussten,
ohne dass eine die andere sah (Befund 13 der Abnahme vom 2026-09-30).

**Hier stehen Erzeuger und Muster nebeneinander.** Wer eine Zeile ändert, ändert
das Muster im selben Atemzug; `tests/test_konsole.py` hält beide zusammen,
indem es jede erzeugte Zeile mit ihrem Muster liest.

Zahlen stehen in deutscher Schreibweise (Komma), wie überall in der Oberfläche.
"""

from __future__ import annotations

import re


def zahl(wert: float, stellen: int) -> str:
    """Eine Zahl mit Dezimalkomma: `zahl(0.137, 2)` → `"0,14"`."""

    return f"{wert:.{stellen}f}".replace(".", ",")


def tick_zeile(
    tick: int,
    max_ticks: int,
    *,
    sekunden: float,
    je_sekunde: float,
    preis: float | None,
    buchungsrate: float | None,
) -> str:
    """Die Fortschrittszeile eines Ticks: `[Tick  14/40] 0,14 s (7,1 Ticks/s) — …`."""

    preis_text = f"{zahl(preis, 2)} €" if isinstance(preis, (int, float)) else "nicht bekannt"
    rate_text = (
        f"{zahl(buchungsrate * 100, 1)} %"
        if isinstance(buchungsrate, (int, float))
        else "nicht bekannt"
    )
    return (
        f"[Tick {tick:>3}/{max_ticks}] {zahl(sekunden, 2)} s "
        f"({zahl(je_sekunde, 1)} Ticks/s) — Preis {preis_text}, Buchungsrate {rate_text}"
    )


#: Liest `tick_zeile`. **Die Sekundenzahl ist optional** (P1.9-W4.3): Verlangte das
#: Muster sie, ginge bei einer Zeile ohne Dauer auch der Tick verloren.
TICK_ZEILE = re.compile(r"\[Tick\s+(\d+)\s*/\s*(\d+)\](?:\s+(\d+(?:,\d+)?) s)?")


def tick_sekunden(treffer: re.Match[str]) -> float | None:
    """Die Dauer des Ticks aus einem Treffer von `TICK_ZEILE` — oder nichts."""

    roh = treffer.group(3)
    return float(roh.replace(",", ".")) if roh is not None else None


def szenario_kopf(name: str) -> str:
    """Der Kopf, mit dem der Szenario-Vergleich ein Szenario beginnt."""

    return f"Szenario «{name}»"


#: Liest `szenario_kopf`. Der Name steht in Guillemets, weil Szenarionamen selbst
#: Klammern tragen («Business as Usual (A1+B1)») — ein Muster, das eine Kennung
#: in Klammern am Ende abschnitt, hätte einen solchen Namen gekürzt.
SZENARIO_KOPF = re.compile(r"^Szenario «(.+)»$")


def szenario_ende(ticks: int, sekunden: float) -> str:
    """Die Zeile, mit der der Szenario-Vergleich ein Szenario beendet."""

    je_sekunde = ticks / sekunden if sekunden > 0 else 0.0
    return f"{ticks} Ticks gerechnet in {zahl(sekunden, 1)} s ({zahl(je_sekunde, 0)} Ticks/s)"


#: Liest `szenario_ende` — eingerückt oder nicht.
SZENARIO_ENDE = re.compile(r"^\s*\d+ Ticks gerechnet\b")
