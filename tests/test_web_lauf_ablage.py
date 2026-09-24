"""Das Einrichten fragt nicht, aus welchen Dateien der Lauf liest (P7.13-U13.4).

In «Lauf & Ablage» standen hinter «Konfigurationsdateien wechseln» fünf
Auswahlfelder — Simulation, Systemgrößen, Agenten, Faktoren, Einflussmatrix —,
und jedes bot dieselben sechs Dateien an: Die Einflussmatrix ließ sich als
«Systemgrößen» wählen. Je Art gab es nur eine Datei. Ein Entwicklerwerkzeug im
Assistenten.

**Gesucht wird in jedem Schritt, nicht in einem Modul**, und die Namen der
Dateifelder kommen aus `ConfigDraft`: Wer die Auswahl an einer anderen Stelle
wieder einbaut, fällt hier auf. Die Felder im Entwurf bleiben erlaubt — die
Rundreise zum Start, die Validierung und der Wirkungstest lesen sie.
"""

from __future__ import annotations

from dataclasses import fields

from dashboard.config_catalog import ConfigDraft
from dashboard.web.config_editor import wizard
from dashboard.web.state import initial_draft_dict

DATEIFELDER = {feld.name for feld in fields(ConfigDraft) if feld.name.endswith("_file")}


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None:
        yield from _walk(kinder)


def _felder(baum) -> set[str]:
    return {
        knoten.id["field"]
        for knoten in _walk(baum)
        if isinstance(getattr(knoten, "id", None), dict) and "field" in knoten.id
    }


def _schritte(draft: dict) -> dict[str, object]:
    baeume = {step.title: step.body(draft) for step in wizard.STEPS if step.body is not None}
    baeume["Prüfen & Starten"] = wizard._final_step(draft)
    return baeume


class TestDasEinrichtenFragtKeineDateien:
    def test_no_step_offers_a_file_choice(self):
        gefunden = {
            titel: sorted(_felder(baum) & DATEIFELDER)
            for titel, baum in _schritte(initial_draft_dict()).items()
            if _felder(baum) & DATEIFELDER
        }

        assert not gefunden, f"Hier wählt ein Feld eine Konfigurationsdatei: {gefunden}"

    def test_the_draft_still_knows_the_files(self):
        """Gegen Blindheit: Ohne Dateifelder im Entwurf prüfte die Suche nichts."""

        assert len(DATEIFELDER) >= 5, DATEIFELDER

    def test_the_search_sees_the_fields_of_the_step(self):
        """Gegen Blindheit: «Lauf & Ablage» trägt weiter ein Feld, und die Suche findet es."""

        baum = _schritte(initial_draft_dict())["Lauf & Ablage"]

        assert "simulation_description" in _felder(baum)
