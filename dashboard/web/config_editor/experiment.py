"""Tab «Experiment & Datenbasis».

Szenario-Modus, Ticks, Mehrfachläufe, Benennung — und die Auswahl der
Config-Dateien, die es bisher nur in der Ops-Variante gab.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import CONFIG_FILE_OPTIONS, list_sweep_presets, load_config_file
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

MODE_OPTIONS = [
    {"label": "Standard (configs/)", "value": "basis"},
    {"label": "Szenario-Preset", "value": "sweep"},
    {"label": "Eigene Parameter", "value": "custom"},
]

_FILE_FIELDS = [
    ("Simulation", "simulation_config_file"),
    ("Properties", "properties_file"),
    ("Agents", "agents_file"),
    ("Factors", "factors_file"),
    ("Einflussmatrix", "cib_file"),
]


def _file_options() -> list[dict]:
    return [{"label": label, "value": name} for name, label in CONFIG_FILE_OPTIONS.items()]


def _mode_block(draft: dict) -> html.Div:
    mode = draft.get("scenario_mode", "basis")
    sweeps = list_sweep_presets()
    children: list = [
        c.select(
            "Modus",
            "scenario_mode",
            mode,
            MODE_OPTIONS,
            hint="Standard nutzt die Dateien unter `configs/`. «Szenario-Preset» lädt einen "
            "vorbereiteten Sweep, «Eigene Parameter» startet von den aktuellen Einstellungen.",
            class_name="max-w-sm",
        )
    ]

    if mode == "sweep" and sweeps:
        sweep_id = draft.get("sweep_id") or sweeps[0].id
        sweep = next((s for s in sweeps if s.id == sweep_id), sweeps[0])
        children.append(
            c.select(
                "Szenario-Preset",
                "sweep_id",
                sweep.id,
                [{"label": s.name, "value": s.id} for s in sweeps],
                class_name="max-w-lg mt-4",
            )
        )
        children.append(ui.alert(sweep.description, "info", class_name="mt-4"))
        if sweep.rationale:
            children.append(
                ui.accordion(
                    "Hintergrund zum Szenario",
                    ui.markdown(sweep.rationale),
                    open=False,
                )
            )
        children.append(
            html.Div(
                ui.button(
                    "Szenario-Parameter übernehmen",
                    id=c.action_id("apply-sweep"),
                    variant="secondary",
                    icon_name="download",
                ),
                className="mt-3",
            )
        )
        children.append(
            c.number(
                "Anzahl Ticks",
                "rounds",
                int(draft.get("rounds") or sweep.max_ticks),
                min=1,
                max=500,
                step=1,
                class_name="max-w-xs mt-4",
            )
        )
    elif mode == "custom":
        children.append(
            html.P(
                "Properties und Faktoren in den nächsten Tabs anpassen.",
                className=f"{ui.CAPTION} mt-3",
            )
        )
        children.append(
            c.number(
                "Ticks",
                "rounds",
                int(draft.get("rounds") or 40),
                min=1,
                max=500,
                step=1,
                class_name="max-w-xs mt-4",
            )
        )
    else:
        simulation = load_config_file(draft.get("simulation_config_file", "simulation_config.json"))
        default_ticks = int(simulation.get("clock", {}).get("max_ticks", draft.get("rounds") or 40))
        children.append(
            c.number(
                "Ticks",
                "rounds",
                default_ticks,
                min=1,
                max=500,
                step=1,
                class_name="max-w-xs mt-4",
            )
        )

    return html.Div(children)


def layout(draft: dict) -> html.Div:
    run_all = bool(draft.get("run_all_sweeps"))
    return html.Div(
        [
            ui.section(
                "Experiment & Datenbasis",
                ui.card(_mode_block(draft)),
                subtitle="Grundlegende Einstellungen für den Lauf. Die JSON-Basisdateien "
                "werden aus dem Ordner `configs/` geladen.",
            ),
            ui.section(
                "Mehrfachläufe",
                ui.card(
                    c.check(
                        "Alle Szenario-Presets nacheinander (schnell, ohne Agenten-Dialog)",
                        "run_all_sweeps",
                        run_all,
                        hint="Ergebnis unter `outputs/sweeps/`.",
                    ),
                    html.Div(
                        (
                            c.number(
                                "Anzahl Läufe (Multi-Run)",
                                "run_count",
                                int(draft.get("run_count") or 1),
                                min=1,
                                max=20,
                                step=1,
                                hint="Mehrere unabhängige Läufe mit gleicher Config; Seeds werden "
                                "hochgezählt. Ergebnis unter `outputs/batch_<Zeitstempel>/run_001`.",
                                class_name="max-w-xs",
                            )
                            if not run_all
                            else None
                        ),
                        className="mt-4",
                    ),
                ),
            ),
            ui.section(
                "Benennung",
                ui.card(
                    c.text(
                        "Run-Name (optional)",
                        "simulation_name",
                        draft.get("simulation_name", ""),
                        class_name="max-w-lg",
                    ),
                    html.Div(
                        c.textarea(
                            "Run-Beschreibung (optional)",
                            "simulation_description",
                            draft.get("simulation_description", ""),
                            class_name="max-w-2xl",
                        ),
                        className="mt-4",
                    ),
                ),
            ),
            ui.section(
                "Config-Dateien",
                ui.card(
                    ui.grid(
                        *[
                            c.select(label, field, draft.get(field), _file_options())
                            for label, field in _FILE_FIELDS
                        ],
                        cols="lg:grid-cols-2",
                    )
                ),
                subtitle="Standard liegt unter `configs/` — alternative Dateien für Experimente.",
            ),
        ]
    )
