"""Wie lange der Lauf ungefähr dauert — aus gemessenen Läufen (P1.9-W4.3).

Das Paket sah vor, die Schätzung aus `run_metadata.json` zu ziehen. **Die Daten
gab es nicht:** Das Artefakt hielt einen Zeitstempel fest (*wann* die Metadaten
geschrieben wurden), aber keine Dauer. Es war also nichts zu schätzen, sondern
zuerst etwas zu messen — `SimulationRunner.run` schreibt seit W4.3
`elapsed_seconds` in den Zustand, und `save_run_metadata` hält sie fest.

**Daraus folgt eine Eigenschaft, die man kennen muss:** Die Schätzung erscheint
erst, wenn Läufe mit diesem Codestand vorliegen. Bis dahin steht hier nichts —
und das ist die richtige Antwort. Eine erfundene Zahl vor einem Lauf ist genau
das, was Invariante 1 verbietet; das Handbuch nennt seine groben Angaben
ausdrücklich «geschätzt», und daran ändert eine Oberfläche nichts, indem sie sie
präzise aussehen lässt.

**Vergleichbar heißt: derselbe Rechenmodus.** Ein Lauf «Nur Zahlen» und einer
«Mit Sprachmodell» unterscheiden sich um Größenordnungen — sie zu mitteln ergäbe
eine Zahl, die für keinen von beiden stimmt.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dashboard.web import components as ui

#: Wie viele vergangene Läufe höchstens herangezogen werden. Mehr macht die
#: Schätzung nicht besser, aber das Einlesen langsamer — und ältere Läufe
#: stammen eher von einem anderen Codestand.
FENSTER = 20

#: Unter so vielen Messwerten wird nichts angezeigt. Aus **einem** Lauf eine
#: Schätzung abzuleiten hieße, eine Einzelmessung als Erwartung auszugeben.
MINDESTENS = 2


def _modus(metadaten: dict) -> str:
    """Der Rechenmodus eines vergangenen Laufs, so grob wie die Schätzung."""

    if metadaten.get("deterministic_only"):
        return "numbers"
    return "mock" if metadaten.get("mock_llm") else "llm"


def _entwurfsmodus(draft: dict) -> str:
    if draft.get("deterministic_only"):
        return "numbers"
    return "mock" if draft.get("mock_llm", True) else "llm"


def _jungste_laeufe(basis: Path, anzahl: int) -> list[Path]:
    """Die `anzahl` jüngsten Laufordner mit Metadaten — ohne den Rest anzusehen.

    **Gelesen wird der Ordner, nicht der Baum** (P7.11-U11.2, 2026-09-12). Bis
    dahin stand hier `sorted(basis.glob("*/run_metadata.json"), reverse=True)`,
    und das ist ein Unterschied, den man erst unter Last merkt: `glob` sieht
    **jeden** Laufordner an, bevor `[:FENSTER]` zwanzig davon behält. Gemessen
    am 2026-09-12 bei 698 Ordnern (137 davon mit Metadaten): 6950 `lstat`-
    Aufrufe und **44 ms**, und weil `live_state` je Klick zweimal läuft, hing
    fast ein Fünftel der Klickdauer an der Zahl vergangener Läufe — eine Größe,
    die mit jedem Lauf wächst und auf einem frischen Checkout null ist. Der
    Wächter aus P3.16 maß damit die Vorgeschichte der Maschine mit.

    `os.scandir` liefert die Ordnereigenschaft aus dem Verzeichniseintrag, ohne
    je Eintrag nachzufragen; abgebrochen wird, sobald `anzahl` Läufe mit
    Metadaten zusammen sind. Die Auswahl bleibt dieselbe: die
    lexikografisch größten Ordnernamen, also die jüngsten Zeitstempel.
    """

    with os.scandir(basis) as eintraege:
        namen = sorted((e.name for e in eintraege if e.is_dir()), reverse=True)

    gefunden: list[Path] = []
    for name in namen:
        pfad = basis / name / "run_metadata.json"
        if pfad.is_file():
            gefunden.append(pfad)
            if len(gefunden) >= anzahl:
                break
    return gefunden


def messwerte(modus: str, *, wurzel: Path | None = None) -> list[float]:
    """Sekunden je Tick aus vergangenen Läufen desselben Rechenmodus.

    **Je Tick und nicht je Lauf**: Ein Lauf über 50 Ticks sagt nichts über einen
    über 10, wohl aber über das Tempo. Die Länge kommt aus dem Entwurf.
    """

    basis = wurzel or Path("outputs")
    if not basis.is_dir():
        return []

    werte: list[float] = []
    for pfad in _jungste_laeufe(basis, FENSTER):
        try:
            daten = json.loads(pfad.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - ein kaputtes Artefakt ist kein Grund zu scheitern
            continue
        dauer = daten.get("elapsed_seconds")
        ticks = daten.get("ticks_completed") or 0
        if not dauer or ticks < 1 or _modus(daten) != modus:
            continue
        werte.append(float(dauer) / int(ticks))
    return werte


def spanne(sekunden: float) -> str:
    """Sekunden als Wort — **die** Formulierung, an zwei Orten dieselbe.

    Öffentlich, weil der Ladebildschirm dieselbe Sprache sprechen muss: Wer im
    Prüfschritt «etwa 3 Minuten» liest und während des Laufs «noch 180 s», hält
    das für zwei verschiedene Größen.
    """

    # Einzahl mitgeführt. Vor W4.3 fiel das nicht auf: Die Schätzung im
    # Prüfschritt beschreibt einen ganzen Lauf und landet praktisch nie bei
    # eins. Die Restzeit während des Laufs tut es in jedem letzten Tick — am
    # laufenden System stand dort «noch etwa 1 Sekunden bis 2 Sekunden».
    if sekunden < 90:
        zahl = round(sekunden)
        return f"{zahl} {'Sekunde' if zahl == 1 else 'Sekunden'}"
    if sekunden < 5400:
        zahl = round(sekunden / 60)
        return f"{zahl} {'Minute' if zahl == 1 else 'Minuten'}"
    return f"{sekunden / 3600:.1f} Stunden"


def schaetzung(draft: dict, *, wurzel: Path | None = None) -> str | None:
    """Ein Satz — oder `None`, wenn es nichts zu sagen gibt."""

    werte = messwerte(_entwurfsmodus(draft), wurzel=wurzel)
    if len(werte) < MINDESTENS:
        return None

    ticks = int(draft.get("rounds") or 0)
    if ticks < 1:
        return None

    # **Spanne statt Punktwert.** Ein Mittelwert sähe genauer aus, als die
    # Messung ist; das Kleinste und das Größte sagen, womit zu rechnen ist.
    kurz, lang = min(werte) * ticks, max(werte) * ticks
    quelle = f"aus {len(werte)} vergleichbaren Läufen"
    if round(kurz) == round(lang):
        return f"Etwa **{spanne(kurz)}** ({quelle})."
    return f"Etwa **{spanne(kurz)} bis {spanne(lang)}** ({quelle})."


def hinweis(draft: dict, *, wurzel: Path | None = None) -> object:
    """Die Schätzung als Zeile — oder nichts."""

    satz = schaetzung(draft, wurzel=wurzel)
    if satz is None:
        return None
    return ui.note(satz, icon_name="schedule")
