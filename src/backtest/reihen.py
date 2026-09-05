"""Die historischen Reihen laden — und die Kalenderzuordnung, die nur hier lebt."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATEN = REPO_ROOT / "configs" / "backtest"

#: Erster und letzter Monat des Fensters. Steht auch in `quellen.json`; hier ist
#: es die Rechengrundlage, dort die Dokumentation des Abrufs.
FENSTER = ("2015-01", "2024-12")

#: Jahre, die **mitgerechnet, aber nicht bewertet** werden (Entscheidung vom
#: 2026-08-30). Der Einbruch 2020 war keine Preiswirkung, sondern Folge von
#: Reisebeschränkungen; das Modell hat dafür keinen Mechanismus. Ihn über
#: `demand_growth_rate` einzuspeisen hieße, dem Backtest die Antwort zu geben —
#: er bestätigte dann eine Eingabe statt einer Rechnung.
UNBEWERTET = frozenset({"2020", "2021"})


@dataclass(frozen=True)
class Reihe:
    """Eine Monatsreihe über das Fenster, samt ihrer Herkunft."""

    name: str
    spalte: str
    werte: dict[str, float]
    quelle: dict[str, object]

    @property
    def monate(self) -> list[str]:
        return sorted(self.werte)

    @property
    def luecken(self) -> list[str]:
        """Monate des Fensters ohne Wert.

        Sie werden **benannt und nicht gefüllt**. Beim EUA-Preis ist das kein
        Datenfehler: Im Januar 2021 fand keine gemeinsame EU-Auktion statt (der
        Auktionskalender der vierten Handelsperiode begann im Februar). Ein
        Monat ohne Auktion ist kein Monat mit dem Preis null.
        """

        return [m for m in alle_monate() if m not in self.werte]

    def fortgeschrieben(self) -> dict[str, float]:
        """Die Reihe mit fortgeschriebenen Lücken — für die **Eingabe** in den Lauf.

        Eine Lücke im Preispfad muss gefüllt werden, sonst spränge die Größe im
        Modell auf ihren Ausgangswert zurück. Fortgeschrieben und nicht
        interpoliert: Der zuletzt beobachtete Preis ist das, was am Markt galt,
        solange nicht neu versteigert wurde. Eine Interpolation erfände einen
        Verlauf zwischen zwei Beobachtungen.

        **Für die Auswertung wird `werte` genommen, nicht diese Fassung** — sonst
        ginge ein erfundener Wert in eine Kennzahl ein.
        """

        gefuellt: dict[str, float] = {}
        letzter: float | None = None
        for monat in alle_monate():
            if monat in self.werte:
                letzter = self.werte[monat]
            if letzter is not None:
                gefuellt[monat] = letzter
        return gefuellt


def alle_monate() -> list[str]:
    """Alle Monate des Fensters als ``YYYY-MM``."""

    von, bis = FENSTER
    jahre = range(int(von[:4]), int(bis[:4]) + 1)
    return [f"{j}-{m:02d}" for j in jahre for m in range(1, 13)]


def tick_je_monat() -> dict[str, int]:
    """**Die Kalenderzuordnung — und sie lebt nur hier.**

    Invariante 5 sagt: Ein Tick hat keine Kalenderbedeutung, und es kommt kein
    Datum in Config, Checkpoint oder Ausgabe. Der Backtest braucht trotzdem
    eines, also bringt er seine eigene Übersetzungstabelle mit und lässt den
    Tick im Modell ein Tick sein. Tick 1 ist der erste Monat des Fensters.
    """

    return {monat: i for i, monat in enumerate(alle_monate(), start=1)}


def monat_je_tick() -> dict[int, str]:
    return {t: m for m, t in tick_je_monat().items()}


def ist_bewertet(monat: str) -> bool:
    return monat[:4] not in UNBEWERTET


def laden(name: str, *, wurzel: Path | None = None) -> Reihe:
    """Eine Reihe samt Herkunftsangabe aus `configs/backtest/` lesen."""

    basis = wurzel or DATEN
    quellen = json.loads((basis / "quellen.json").read_text(encoding="utf-8"))
    eintrag = next((q for q in quellen["reihen"] if q["datei"] == f"{name}.csv"), None)
    if eintrag is None:
        raise KeyError(
            f"`{name}` steht nicht in quellen.json. Reihen ohne Herkunftsangabe "
            "gibt es hier nicht — sie zu laden hieße, eine Zahl ohne Quelle in "
            "eine Auswertung zu tragen."
        )

    von, bis = FENSTER
    werte: dict[str, float] = {}
    with (basis / f"{name}.csv").open(encoding="utf-8") as datei:
        for zeile in csv.DictReader(datei):
            monat = zeile["monat"]
            if von <= monat <= bis:
                werte[monat] = float(zeile[eintrag["spalte"]])

    return Reihe(name=name, spalte=str(eintrag["spalte"]), werte=werte, quelle=eintrag)
