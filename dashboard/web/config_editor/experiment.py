"""Tab «Lauf & Ablage»: Benennung, Mehrfachläufe, Datengrundlage.

Die grundlegenden Entscheidungen (Annahmenwelt, Länge, Rechenmodus) stehen
im Tab «Überblick». Hier steht, was darüber hinaus zur Organisation eines
Laufs gehört — und die Dateiauswahl für den Fall, dass mit alternativen
Konfigurationen experimentiert wird.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import CONFIG_FILE_OPTIONS, list_sweep_presets
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor.overview import MODE_OPTIONS

_FILE_FIELDS = [
    ("Simulation", "simulation_config_file", "Uhr, Name und LLM-Voreinstellungen."),
    ("Systemgrößen", "properties_file", "Politik, Kosten, Bevölkerung, Marktregeln."),
    ("Agenten", "agents_file", "Rollen und Rechte von Consumer, Provider, Regulator."),
    ("Faktoren", "factors_file", "Die sieben Faktoren und ihre möglichen Zustände."),
    ("Einflussmatrix", "cib_file", "Die eingefrorene CIB-Matrix zur Konsistenzprüfung."),
]


def _file_options() -> list[dict]:
    return [{"label": label, "value": name} for name, label in CONFIG_FILE_OPTIONS.items()]


def _scenario_card(draft: dict) -> html.Div:
    mode = draft.get("scenario_mode", "basis")
    children: list = [c.select("scenario_mode", mode, MODE_OPTIONS, class_name="max-w-xl")]

    if mode == "sweep":
        presets = list_sweep_presets()
        if presets:
            sweep_id = draft.get("sweep_id") or presets[0].id
            sweep = next((s for s in presets if s.id == sweep_id), presets[0])
            children.append(
                html.Div(
                    c.select(
                        "sweep_id",
                        sweep.id,
                        [{"label": s.name, "value": s.id} for s in presets],
                        class_name="max-w-xl",
                    ),
                    className="mt-5",
                )
            )
            children.append(html.Div(ui.note(sweep.description), className="mt-4"))
            if sweep.rationale:
                children.append(
                    ui.expert(
                        ui.markdown(sweep.rationale),
                        title="Warum dieses Szenario so aufgebaut ist",
                    )
                )
            children.append(
                html.Div(
                    ui.button(
                        "Werte dieses Szenarios übernehmen",
                        id=c.action_id("apply-sweep"),
                        variant="secondary",
                        icon_name="download",
                    ),
                    className="mt-5",
                )
            )
    return ui.card(*children)


def layout(draft: dict) -> html.Div:
    run_all = bool(draft.get("run_all_sweeps"))

    return html.Div(
        [
            ui.section(
                "Benennung",
                ui.lede(
                    "Name und Fragestellung erscheinen im Bericht und in der Run-Liste. "
                    "Ohne sie sind mehrere Läufe später kaum auseinanderzuhalten."
                ),
                ui.card(
                    c.text(
                        "simulation_name", draft.get("simulation_name", ""), class_name="max-w-lg"
                    ),
                    html.Div(
                        c.textarea(
                            "simulation_description",
                            draft.get("simulation_description", ""),
                            class_name="max-w-2xl",
                        ),
                        className="mt-5",
                    ),
                ),
            ),
            ui.section(
                "Annahmenwelt",
                ui.lede(
                    "Dieselbe Auswahl wie im Überblick, hier mit Begründung und der "
                    "Möglichkeit, die Werte eines Presets als Ausgangspunkt zu übernehmen."
                ),
                _scenario_card(draft),
            ),
            ui.section(
                "Mehrere Läufe",
                ui.lede(
                    "Ein einzelner Lauf zeigt einen möglichen Verlauf. Erst mehrere zeigen, "
                    "was daran belastbar ist."
                ),
                ui.card(
                    c.check("run_all_sweeps", run_all),
                    html.Div(
                        (
                            c.number(
                                "run_count",
                                int(draft.get("run_count") or 1),
                                min=1,
                                max=20,
                                step=1,
                                class_name="max-w-xs",
                            )
                            if not run_all
                            else None
                        ),
                        className="mt-5",
                    ),
                ),
            ),
            ui.section(
                "Datengrundlage",
                ui.lede(
                    "Welche Dateien unter `configs/` gelesen werden. Für den Normalfall "
                    "bleibt hier alles auf Standard."
                ),
                ui.expert(
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
                    count=len(_FILE_FIELDS),
                    title="Konfigurationsdateien wechseln",
                ),
            ),
        ]
    )
