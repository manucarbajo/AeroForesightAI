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
                    html.Div(
                        ui.grid(
                            c.text("model", draft.get("model")),
                            c.text("base_url", draft.get("base_url")),
                            c.slider(
                                "temperature",
                                draft.get("temperature"),
                                min=0.0,
                                max=1.5,
                                step=0.05,
                            ),
                            c.number(
                                "max_tokens",
                                draft.get("max_tokens"),
                                min=256,
                                max=8192,
                                step=1,
                            ),
                            cols="md:grid-cols-2",
                        ),
                    ),
                ),
                actions=ui.doc_link("zahlen-und-sprache"),
            ),
            # **Ein Abschnitt statt dreier** (P1.9-W3.5). «Zwischenstände» kostete
            # 307 px für **ein** Zahlenfeld — Überschrift, Einleitung, Karte und
            # Doku-Verweis drumherum. «Ausgaben» weitere 218 px. Zusammen mehr
            # als der eigentliche Inhalt des Schritts.
            #
            # Eine Gliederungsebene innerhalb eines Schritts wiederholt, was der
            # Schritt schon ist: eine Frage mit einer Überschrift. Was selten
            # gebraucht wird, gehört nicht unter eine eigene Überschrift, sondern
            # hinter eine Klappe — dasselbe Muster wie «Feinabstimmung».
            ui.expert(
                c.number(
                    "checkpoint_interval",
                    draft.get("checkpoint_interval"),
                    min=0,
                    step=1,
                    detail=True,
                    breite="feld",
                ),
                html.Div(
                    c.check("generate_figures", draft.get("generate_figures")),
                    className="mt-5",
                ),
                html.Div(
                    [c.check(name, draft.get(name)) for name in _PIPELINE_SWITCHES],
                    className="space-y-3 mt-3",
                ),
                html.Div(
                    c.text("resume_from", draft.get("resume_from"), breite="feld-weit"),
                    className="mt-5",
                ),
                count=len(_PIPELINE_SWITCHES) + 3,
                title="Zwischenstände und Ausgaben",
                names="Checkpoints, Bilder, Markt, Redebedarf, Protokoll, Szenarien, Fortsetzen",
            ),
        ]
    )
