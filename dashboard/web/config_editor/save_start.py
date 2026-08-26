"""Tab «Kontrolle»: nachsehen, was gleich gerechnet wird — und sichern.

Letzter Blick vor dem Start. Oben in Klartext, darunter im Detail, ganz unten
die Rohdaten für alle, die es genau wissen wollen.
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.config_catalog import effective_config_summary, load_config_file, validate_draft
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor.overview import summary_id, summary_sentence
from dashboard.web.state import draft_from_dict


def _highlights(draft: dict) -> list:
    """Die Einstellungen, die man vor dem Start noch einmal gesehen haben will."""

    feedback = draft.get("market_feedback_edit") or {}
    segments = [s for s in (draft.get("population_edits") or []) if s.get("type") == "boolean"]
    active_properties = [
        key
        for key, edit in (draft.get("property_edits") or {}).items()
        if isinstance(edit, dict) and edit.get("is_active", True)
    ]

    tiles = [
        ui.metric_tile("Länge", f"{draft.get('rounds', '?')} Ticks"),
        ui.metric_tile(
            "Wiederholungen",
            "alle Szenarien" if draft.get("run_all_sweeps") else draft.get("run_count", 1),
        ),
        ui.metric_tile(
            "Ziel-Auslastung",
            (
                f"{float(feedback.get('target_booking_rate', 0.37)):.0%}"
                if feedback.get("enabled", True)
                else "Preis fix"
            ),
        ),
        ui.metric_tile("Segmente", len(segments)),
        ui.metric_tile("Aktive Systemgrößen", len(active_properties)),
        ui.metric_tile(
            "Zufallsstartwert",
            draft.get("seed", "—") if draft.get("use_seed") else "frei",
            hint="Ohne festen Startwert weichen Wiederholungen voneinander ab.",
        ),
    ]
    return tiles


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

    # Fehler zuerst und sichtbar abgesetzt: Die Hinweise darunter sind Ratschläge,
    # das hier verhindert den Start. Beides in einem Topf zu zeigen, würde genau
    # die Unterscheidung verwischen, auf die es ankommt.
    warnings = []
    config_errors = validate_draft(draft_from_dict(draft))
    if config_errors:
        warnings.append(
            ui.alert(
                "**Der Lauf kann so nicht starten.** "
                + " · ".join(f"`{error}`" for error in config_errors),
                "error",
            )
        )

    if not draft.get("use_seed") and int(draft.get("run_count") or 1) > 1:
        warnings.append(
            ui.alert(
                "Mehrere Wiederholungen ohne festen Zufallsstartwert: Die Läufe werden sich "
                "unterscheiden. Das ist gewollt, wenn Sie die Streuung sehen wollen — für "
                "einen sauberen A/B-Vergleich setzen Sie den Startwert unter «Technik».",
                "info",
            )
        )
    if draft.get("no_scenarios"):
        warnings.append(
            ui.alert(
                "«Keine Szenarien erzeugen» ist aktiv — der Tab «Szenario» bleibt nach dem "
                "Lauf leer, obwohl er die Hauptansicht ist.",
                "warning",
            )
        )
    if not (draft.get("apply_custom_overrides") or draft.get("scenario_mode") == "custom"):
        warnings.append(
            ui.alert(
                "«Eigene Werte anwenden» ist aus — Änderungen an Faktoren und Systemgrößen "
                "wirken in diesem Lauf nicht.",
                "warning",
            )
        )

    return html.Div(
        [
            ui.section(
                "Das passiert beim Start",
                ui.card(html.Div(ui.markdown(summary_sentence(draft)), id=summary_id("control"))),
                html.Div(warnings, className="space-y-2 mt-4") if warnings else None,
            ),
            ui.section(
                "Auf einen Blick",
                ui.grid(*_highlights(draft), cols="sm:grid-cols-2 lg:grid-cols-3"),
            ),
            ui.section(
                "Als Szenario sichern",
                ui.lede(
                    "Legt den aktuellen Stand unter `configs/sweeps/` ab. Danach lässt er "
                    "sich im Überblick als Preset wieder auswählen."
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
                                className="pt-7",
                            ),
                        ],
                        className="flex items-start gap-4 flex-wrap",
                    )
                ),
            ),
            ui.section(
                "Rohdaten",
                ui.lede(
                    "Für den Fall, dass Sie genau nachsehen wollen, was an die Simulation "
                    "übergeben wird."
                ),
                ui.expert(
                    ui.json_view(summary, max_height="30rem"),
                    title="Effektive Konfiguration",
                ),
                ui.expert(
                    ui.json_view(simulation, max_height="30rem"),
                    title="simulation_config.json",
                ),
                ui.expert(
                    ui.json_view(excerpt, max_height="30rem"),
                    title="properties.json (Auszug)",
                ),
            ),
        ]
    )
