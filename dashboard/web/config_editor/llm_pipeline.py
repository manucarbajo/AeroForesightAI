"""Tab «Technik»: Sprachmodell, Reproduzierbarkeit, Ausgaben.

Nichts hier ändert die berechneten Zahlen — mit einer Ausnahme, dem
Zufallsstartwert. Alles andere betrifft, wie viel erzählt, protokolliert und
ausgegeben wird.
"""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import compute_mode
from dashboard.web.config_editor import controls as c

_PIPELINE_SWITCHES = ["no_market", "redebedarf", "no_protocol", "no_scenarios"]


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            ui.section(
                "Sprachmodell",
                ui.lede(
                    "Die Agenten deuten den Lauf — sie rechnen nicht. Ob und mit welchem "
                    "Modell sie das tun, steht hier."
                ),
                ui.card(
                    ui.note(
                        "**Kennzahlen bleiben unberührt.** Preise, Buchungsraten und "
                        "Faktorzustände entstehen deterministisch im Rechenmodell. Das "
                        "Sprachmodell liefert ausschließlich Text.",
                        icon_name="shield",
                    ),
                    html.Div(
                        ui.radio(
                            compute_mode.OPTIONS,
                            value=compute_mode.of(draft),
                            id=compute_mode.FIELD_ID,
                        ),
                        className="mt-5",
                    ),
                    html.Div(
                        compute_mode.availability(draft),
                        className="mt-5 pt-4 border-t border-slate-100",
                    ),
                    ui.expert(
                        ui.grid(
                            c.text("model", draft.get("model", "llama3.2")),
                            c.text("base_url", draft.get("base_url", "http://localhost:11434")),
                            c.slider(
                                "temperature",
                                float(draft.get("temperature", 0.7)),
                                min=0.0,
                                max=1.5,
                                step=0.05,
                            ),
                            c.number(
                                "max_tokens",
                                int(draft.get("max_tokens", 2048)),
                                min=256,
                                max=8192,
                                step=1,
                            ),
                            cols="md:grid-cols-2",
                        ),
                        count=4,
                        names="Modell, Adresse, Kreativität, Antwortlänge",
                    ),
                ),
                actions=ui.doc_link("zahlen-und-sprache"),
            ),
            ui.section(
                "Reproduzierbarkeit",
                ui.lede(
                    "Damit zwei Läufe vergleichbar sind, muss der Zufall festgelegt sein — "
                    "sonst lässt sich ein Unterschied nicht der geänderten Annahme zuordnen."
                ),
                ui.card(
                    ui.grid(
                        c.check("use_seed", draft.get("use_seed", False)),
                        c.number(
                            "seed",
                            int(draft.get("seed") if draft.get("seed") is not None else 42),
                            min=0,
                            step=1,
                        ),
                        cols="sm:grid-cols-2",
                    ),
                    html.Div(
                        c.number(
                            "checkpoint_interval",
                            int(draft.get("checkpoint_interval", 5)),
                            min=0,
                            step=1,
                            class_name="max-w-xs",
                        ),
                        className="mt-5",
                    ),
                ),
                actions=ui.doc_link("vergleiche"),
            ),
            ui.section(
                "Ausgaben",
                ui.card(
                    c.check("generate_figures", draft.get("generate_figures", True)),
                    ui.expert(
                        html.Div(
                            [c.check(name, draft.get(name, False)) for name in _PIPELINE_SWITCHES],
                            className="space-y-3",
                        ),
                        html.Div(
                            c.text(
                                "resume_from",
                                draft.get("resume_from", ""),
                                class_name="max-w-lg",
                            ),
                            className="mt-5",
                        ),
                        count=len(_PIPELINE_SWITCHES) + 1,
                        title="Teile der Pipeline abschalten",
                        names="Markt, Redebedarf, Protokoll, Szenarien, Fortsetzen",
                    ),
                ),
            ),
        ]
    )
