"""P7.2-U2.1: Ein Szenario-Vergleich wird überall gleich gezählt (2026-09-11).

**Der Befund war eine Behauptung der Oberfläche, die der Lauf nicht einlöst.**
Der Einstieg sagte «Alle 8 hinterlegten Szenarien», das Bedienfeld
«Vergleich · 8 Szenarien», die Kachel im Prüfschritt «Szenarien 8» — und der
Satz direkt darüber «alle 4 Rahmenszenarien». Gerechnet werden die vier: Seit
P2.2 vergleicht ein Vergleich nur Rahmen, die Stresstests der Engine bleiben
draußen. Drei der vier Stellen zählten `list_sweep_presets()`, also den ganzen
Ordner, eine zählte `rahmenszenarien()`.

Dieselbe Klasse wie A1 des Audits vom 2026-08-28: Die Oberfläche beschreibt
einen Lauf, der so nicht stattfindet — dort am Rechenmodus, hier an der Zahl.

**Gemessen wird am gerenderten Text, nicht an der Aufrufstelle.** Ein Wächter,
der nur prüft, welche Funktion aufgerufen wird, fände die nächste Stelle nicht,
die eine eigene Zählung hinschreibt.
"""

from __future__ import annotations

import re

import pytest

from dashboard.config_catalog import list_sweep_presets, rahmenszenarien
from dashboard.web.config_editor import start_flow, wizard
from dashboard.web.pages import launch as launch_page
from dashboard.web.state import initial_draft_dict


def _text(node) -> str:
    """Den sichtbaren Text eines Komponentenbaums, Kinder mit Leerzeichen getrennt."""

    if node is None:
        return ""
    if isinstance(node, (str, int, float)):
        return str(node)
    if isinstance(node, (list, tuple)):
        return " ".join(_text(kind) for kind in node)
    return _text(getattr(node, "children", None))


@pytest.fixture
def vergleich() -> dict:
    draft = initial_draft_dict()
    draft["run_all_sweeps"] = True
    return draft


@pytest.fixture
def rahmen() -> int:
    return len(rahmenszenarien())


def test_the_shipped_configs_can_tell_the_two_counts_apart():
    """Vorbedingung: Ohne Stresstests im Ordner prüfte diese Datei nichts.

    Stimmen beide Zählungen überein, wäre jeder Test unten auch mit der falschen
    Funktion grün — genau der Zustand, in dem der Befund entstanden ist.
    """

    assert len(list_sweep_presets()) > len(rahmenszenarien()) > 0


def test_the_entry_counts_the_frameworks(vergleich, rahmen):
    text = _text(wizard.entry(vergleich))
    treffer = re.search(r"Alle (\d+) ", text)

    assert treffer, f"Der Einstieg nennt keine Zahl mehr: {text!r}"
    assert int(treffer.group(1)) == rahmen


#: Eine Zahl vor «Szenarien» oder «Rahmenszenarien». Bewusst beide Wörter: Der
#: Wächter soll an der **Zahl** scheitern, nicht an einer Umformulierung.
ZAHL_VOR_SZENARIEN = r"(\d+) (?:Rahmens|S)zenarien"


def test_the_rail_summary_counts_the_frameworks(vergleich, rahmen):
    zeile = launch_page._summary(vergleich)

    assert re.findall(ZAHL_VOR_SZENARIEN, zeile) == [str(rahmen)], zeile


def test_the_rail_rows_count_the_frameworks(vergleich, rahmen):
    text = _text(launch_page.summary_rows(vergleich))

    assert re.findall(ZAHL_VOR_SZENARIEN, text) == [str(rahmen)], text


def test_the_review_tiles_count_the_frameworks(rahmen):
    text = _text(start_flow._vergleich_tiles())
    treffer = re.search(r"(?:RAHMEN)?SZENARIEN (\d+)", text)

    assert treffer, f"Die Kachel nennt keine Zahl mehr: {text!r}"
    assert int(treffer.group(1)) == rahmen


def test_the_review_length_is_the_length_of_the_frameworks():
    """Die Längenspanne darf nicht aus den Stresstests kommen."""

    laengen = sorted({p.max_ticks for p in rahmenszenarien()})
    erwartet = f"{laengen[0]} Ticks" if len(laengen) == 1 else f"{laengen[0]}–{laengen[-1]} Ticks"
    # **Der ganze Wert, nicht ein Teil davon.** «120 Ticks» steckt auch in
    # «40–120 Ticks» — die erste Fassung dieses Tests war deshalb vor dem Fix
    # grün, obwohl die Spanne aus den Stresstests kam.
    treffer = re.search(r"LÄNGE ([\d–]+ Ticks)", _text(start_flow._vergleich_tiles()))

    assert treffer and treffer.group(1) == erwartet


def test_the_sentence_counts_the_frameworks(rahmen):
    satz = start_flow._vergleich_satz()

    assert re.findall(r"alle (\d+) Rahmenszenarien", satz) == [str(rahmen)], satz
