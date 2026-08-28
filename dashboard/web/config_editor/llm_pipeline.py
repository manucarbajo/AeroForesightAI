"""Tab «Technik»: Sprachmodell-Feinheiten, Zwischenstände, Ausgaben.

Nichts hier ändert die berechneten Zahlen. Die Auswahl des Rechenmodus und der
Zufallsstartwert — die beiden Dinge, die man vor einem Lauf wirklich wissen
muss — stehen seit P1.1 im geführten Ablauf oben auf der Seite; hier bleiben
die Werte dahinter: welches Modell unter welcher Adresse, wie oft ein
Zwischenstand geschrieben wird, und was am Ende ausgegeben wird.
"""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

_PIPELINE_SWITCHES = ["no_market", "redebedarf", "no_protocol", "no_scenarios"]


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            ui.section(
                "Sprachmodell",
                ui.lede(
                    "Die Agenten deuten den Lauf — sie rechnen nicht. **Ob** ein Sprachmodell "
                    "beteiligt ist, entscheidet der Rechenmodus oben; hier steht, mit welchem."
                ),
                ui.card(
                    ui.note(
                        "**Kennzahlen bleiben unberührt.** Preise, Buchungsraten und "
                        "Faktorzustände entstehen deterministisch im Rechenmodell. Das "
                        "Sprachmodell liefert ausschließlich Text.",
                        icon_name="shield",
                    ),
                    html.Div(
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
                        className="mt-5",
                    ),
                ),
                actions=ui.doc_link("zahlen-und-sprache"),
            ),
            ui.section(
                "Zwischenstände",
                ui.lede(
                    "Zwischenstände sind die Voraussetzung dafür, einen Lauf fortzusetzen "
                    "und ihn später auf einzelne Runden hin zu befragen."
                ),
                ui.card(
                    c.number(
                        "checkpoint_interval",
                        int(draft.get("checkpoint_interval", 5)),
                        min=0,
                        step=1,
                        detail=True,
                        class_name="max-w-xs",
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
