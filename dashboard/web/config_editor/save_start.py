"""Tab «Speichern & Starten»: JSON-Vorschauen, Preset sichern, effektive Config."""

from __future__ import annotations

from dash import dcc, html

from dashboard.config_catalog import effective_config_summary, load_config_file
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c  # noqa: F401  (Symmetrie zu den anderen Tabs)
from dashboard.web.state import draft_from_dict


def layout(draft: dict) -> html.Div:
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
            ui.section(
                "JSON-Vorschau",
                ui.accordion(
                    "simulation_config.json", ui.json_view(simulation, max_height="30rem")
                ),
                ui.accordion("properties.json (Auszug)", ui.json_view(excerpt, max_height="30rem")),
            ),
            ui.section(
                "Als Szenario speichern",
                ui.card(
                    html.Div(
                        [
                            ui.field(
                                "Dateiname (configs/sweeps/)",
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
                                    "Szenario speichern",
                                    id=c.action_id("save-preset"),
                                    variant="secondary",
                                    icon_name="save",
                                ),
                                className="pt-7",
                            ),
                        ],
                        className="flex items-start gap-4 flex-wrap",
                    )
                ),
                subtitle="Legt den aktuellen Entwurf als wiederverwendbares Preset ab.",
            ),
            ui.section(
                "Effektive Konfiguration",
                ui.json_view(summary, max_height="36rem"),
                subtitle="Das, was beim Start tatsächlich in die Simulation geht.",
            ),
        ]
    )
