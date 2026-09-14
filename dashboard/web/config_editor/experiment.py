"""Schritt «Lauf & Ablage»: Fragestellung, Rohdaten, Zurücksetzen.

Die drei Entscheidungen, die einen Lauf prägen — Annahmenwelt, Umfang,
Rechenmodus —, stehen seit P1.1 im geführten Ablauf oben auf der Seite und
nicht mehr hier. Übrig bleibt, was zur Organisation eines Laufs gehört: wozu er
gerechnet wird und was am Ende tatsächlich an die Simulation übergeben wird.

**Aus welchen Dateien der Lauf liest, fragt dieser Schritt nicht mehr**
(P7.13-U13.4). Fünf Auswahlfelder boten je dieselben sechs Dateien an — die
Einflussmatrix ließ sich als «Systemgrößen» wählen —, und je Art gibt es nur
eine. Die Felder im Entwurf bleiben: Die Rundreise zum Start, die Validierung
und der Wirkungstest lesen sie.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import (
    effective_config_summary,
    load_config_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.state import draft_from_dict


def _raw_data(draft: dict) -> html.Div:
    simulation = load_config_file(draft.get("simulation_config_file", "simulation_config.json"))
    properties = load_config_file(draft.get("properties_file", "properties.json"))
    excerpt = {
        "system_properties": properties.get("system_properties", [])[:3],
        "...": "gekürzt",
    }

    try:
        summary = effective_config_summary(draft_from_dict(draft))
    except (
        Exception
    ) as exc:  # noqa: BLE001 - eine kaputte Config soll erklärt, nicht verschluckt werden
        summary = {"Fehler": str(exc)}

    # **Offen untereinander, nicht als Klappen in der Klappe** (P7.1-U1.4,
    # von Haiko entschieden am 2026-09-13). Die drei Vorschauen standen je in
    # einer eigenen Klappe innerhalb von «Rohdaten ansehen» — man klappte
    # zweimal auf, um an Gleichrangiges zu kommen. In etwas Aufgeklapptem
    # steht nur Niedrigeres; `tests/test_web_klappen.py` hält die Regel.
    vorschauen = [
        ("Effektive Konfiguration", summary),
        ("simulation_config.json", simulation),
        ("properties.json (Auszug)", excerpt),
    ]
    return html.Div(
        [
            html.Div(
                [
                    # **Eine Beschriftung, keine Überschrift** (P7.4-U4.3): Die drei
                    # Titel benennen je eine Vorschau in der Klappe «Rohdaten ansehen»;
                    # als `h4` waren sie eine zweite Überschriftebene unter dem Schritt.
                    html.P(
                        titel, className=f"font-body {ui.BESCHRIFTUNG} font-medium af-text mb-1"
                    ),
                    ui.json_view(inhalt, max_height="30rem"),
                ],
                className="mt-4" if index else None,
            )
            for index, (titel, inhalt) in enumerate(vorschauen)
        ]
    )


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            # **Eine Überschriftebene** (P7.4-U4.3). Hier stand ein Abschnitt
            # «Fragestellung» mit eigener Einleitung über einem Feld, das ebenfalls
            # «Fragestellung» heißt und dessen Hinweis dasselbe sagte — dreimal
            # dasselbe Wort unter dem Schritttitel, der schon die Überschrift ist.
            # **Der Name steht seit P1.9-W4.1 im letzten Schritt**: Drei von vier
            # Wegen kommen nie hierher, und alle Läufe hießen sonst gleich. Die
            # Fragestellung bleibt hier; sie gehört zur Dokumentation des Laufs.
            ui.card(
                c.textarea(
                    "simulation_description",
                    draft.get("simulation_description", ""),
                    breite="feld-weit",
                    detail=True,
                ),
            ),
            # **Drei Abschnitte wurden zu Klappen** (P1.9-W3.5). «Als Szenario
            # sichern» (226 px), «Datengrundlage» (128 px) und «Rohdaten»
            # (250 px) trugen je Überschrift, Einleitung und Doku-Verweis —
            # zusammen 604 px für Dinge, die man selten braucht, neben 411 px
            # für die Benennung, um die es in diesem Schritt geht. **Das Sichern
            # ist seit P7.4-U4.5 ganz fort**: Es war einer von vier Speicherwegen
            # und hat jetzt einen einzigen, den Dialog aus der Kopfzeile. **Die
            # Dateiauswahl ist seit P7.13-U13.4 fort**, siehe Modul-Docstring.
            ui.expert(
                ui.lede(
                    "Für den Fall, dass Sie genau nachsehen wollen, was an die Simulation "
                    "übergeben wird."
                ),
                _raw_data(draft),
                count=3,
                einheit=("Ansicht", "Ansichten"),
                title="Rohdaten ansehen",
                names="Effektive Konfiguration, simulation_config.json, properties.json",
            ),
            # Seit P1.7 steht der Rücksetz-Knopf hier statt über den Reitern:
            # Diesen Ort «über allen Einstellungen» gibt es in einer
            # Schrittfolge nicht mehr, und «Lauf & Ablage» ist der Schritt, in
            # dem man ohnehin über den Lauf als Ganzes nachdenkt.
            _reset(),
        ]
    )


def _reset():
    from dashboard.web.config_editor import reset_button

    return reset_button()
