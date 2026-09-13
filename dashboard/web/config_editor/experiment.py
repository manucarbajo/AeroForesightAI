"""Tab «Lauf & Ablage»: Benennung, Sichern, Datengrundlage, Rohdaten.

Die drei Entscheidungen, die einen Lauf prägen — Annahmenwelt, Umfang,
Rechenmodus —, stehen seit P1.1 im geführten Ablauf oben auf der Seite und
nicht mehr hier. Übrig bleibt, was zur Organisation eines Laufs gehört: wie er
heißt, wie er sich als eigenes Szenario sichern lässt, aus welchen Dateien er
liest, und was am Ende tatsächlich an die Simulation übergeben wird.
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.config_catalog import (
    CONFIG_FILE_OPTIONS,
    effective_config_summary,
    load_config_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.state import draft_from_dict

_FILE_FIELDS = [
    ("Simulation", "simulation_config_file", "Uhr, Name und LLM-Voreinstellungen."),
    ("Systemgrößen", "properties_file", "Politik, Kosten, Bevölkerung, Marktregeln."),
    ("Agenten", "agents_file", "Rollen und Rechte von Consumer, Provider, Regulator."),
    ("Faktoren", "factors_file", "Die sieben Faktoren und ihre möglichen Zustände."),
    ("Einflussmatrix", "cib_file", "Die eingefrorene CIB-Matrix zur Konsistenzprüfung."),
]


def _file_options() -> list[dict]:
    return [{"label": label, "value": name} for name, label in CONFIG_FILE_OPTIONS.items()]


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

    return html.Div(
        [
            ui.expert(ui.json_view(summary, max_height="30rem"), title="Effektive Konfiguration"),
            ui.expert(ui.json_view(simulation, max_height="30rem"), title="simulation_config.json"),
            ui.expert(ui.json_view(excerpt, max_height="30rem"), title="properties.json (Auszug)"),
        ]
    )


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            ui.section(
                "Fragestellung",
                ui.lede(
                    "Wozu dieser Lauf gerechnet wird. Erscheint im Bericht und macht später "
                    "nachvollziehbar, was Sie wissen wollten. Der **Name** steht im letzten "
                    "Schritt, direkt vor dem Start."
                ),
                # **Der Name steht seit P1.9-W4.1 im letzten Schritt.** Dieser
                # hier ist optional, und drei von vier Wegen kommen nie an ihm
                # vorbei: «Szenario-Vergleich», «Weiterverwenden» und «Direkt
                # zum Start» führen unmittelbar auf «Prüfen & Starten». Alle
                # Läufe hießen deshalb gleich, und die Run-Liste war nach
                # kurzer Zeit unbrauchbar — genau das, was der Text daneben
                # vorhersagt. Die **Fragestellung** bleibt hier: Sie ist
                # ausführlich, gehört zur Dokumentation des Laufs und nicht auf
                # den Bildschirm, auf dem gestartet wird.
                ui.card(
                    c.textarea(
                        "simulation_description",
                        draft.get("simulation_description", ""),
                        breite="feld-weit",
                    ),
                ),
            ),
            # **Drei Abschnitte werden zu Klappen** (P1.9-W3.5). «Als Szenario
            # sichern» (226 px), «Datengrundlage» (128 px) und «Rohdaten»
            # (250 px) trugen je Überschrift, Einleitung und Doku-Verweis —
            # zusammen 604 px für Dinge, die man selten braucht, neben 411 px
            # für die Benennung, um die es in diesem Schritt geht.
            ui.expert(
                ui.lede(
                    "Legt den aktuellen Stand als Szenario ab. Danach lässt er sich im "
                    "ersten Schritt wieder auswählen."
                ),
                ui.card(
                    html.Div(
                        [
                            ui.field(
                                "Dateiname",
                                dcc.Input(
                                    id=c.free_id("preset-name"),
                                    type="text",
                                    value="mein_szenario",
                                    className="af-input",
                                ),
                                class_name="flex-1 min-w-[16rem]",
                            ),
                            html.Div(
                                ui.button(
                                    "Szenario sichern",
                                    id=c.action_id("save-preset"),
                                    variant="secondary",
                                    icon_name="save",
                                ),
                                className="af-neben-feld",
                            ),
                        ],
                        className="flex items-start gap-4 flex-wrap",
                    )
                ),
                count=1,
                title="Als Szenario sichern",
                names="Dateiname",
            ),
            ui.expert(
                ui.lede(
                    "Welche hinterlegten Dateien der Lauf liest. Für den Normalfall bleibt "
                    "hier alles auf Standard."
                ),
                html.Div(
                    ui.grid(
                        *[
                            c.select(
                                field,
                                draft.get(field),
                                _file_options(),
                                label=label,
                                hint=hint,
                            )
                            for label, field, hint in _FILE_FIELDS
                        ],
                        cols="lg:grid-cols-2",
                    ),
                ),
                count=len(_FILE_FIELDS),
                title="Konfigurationsdateien wechseln",
            ),
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
