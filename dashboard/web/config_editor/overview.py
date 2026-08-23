"""Tab «Überblick» — der Einstieg.

Hier stehen die wenigen Entscheidungen, die einen Lauf tatsächlich prägen:
welche Annahmenwelt, wie lange, wie oft, und ob mit oder ohne Sprachmodell.
Wer nichts weiter anfasst, bekommt damit einen sinnvollen Lauf. Die übrigen
Tabs sind für den Fall, dass eine bestimmte Annahme geprüft werden soll.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import list_sweep_presets
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

#: Der Klartext-Satz steht auf derselben Seite wie die Felder, die ihn
#: verändern — er muss also beim Tippen mitlaufen, nicht erst beim
#: Tab-Wechsel. Pattern-Matching-ID, weil das Ziel je nach Tab fehlen darf.
SUMMARY = "cfg-summary"


def summary_id(slot: str) -> dict:
    return {"type": SUMMARY, "slot": slot}


MODE_OPTIONS = [
    {"label": "Standard — die hinterlegte Ausgangslage", "value": "basis"},
    {"label": "Szenario-Preset — eine vorbereitete Annahmenwelt", "value": "sweep"},
    {"label": "Eigene Parameter — von meinen Einstellungen aus", "value": "custom"},
]

_MODE_PLAIN = {
    "basis": "der Standard-Ausgangslage aus `configs/`",
    "sweep": "einem vorbereiteten Szenario",
    "custom": "Ihren eigenen Einstellungen",
}


def summary_sentence(draft: dict) -> str:
    """Was gleich passiert — in einem Satz, ohne Fachbegriffe."""

    if draft.get("run_all_sweeps"):
        count = len(list_sweep_presets())
        scope = f"**alle {count} hinterlegten Szenarien** nacheinander"
    else:
        runs = int(draft.get("run_count") or 1)
        scope = f"**{runs} Läufe**" if runs > 1 else "**einen Lauf**"

    basis = _MODE_PLAIN.get(draft.get("scenario_mode", "basis"), "der Standard-Ausgangslage")
    ticks = draft.get("rounds", "?")

    if draft.get("deterministic_only"):
        mode = "ohne Agenten-Dialog — nur die berechneten Kennzahlen"
    elif draft.get("mock_llm"):
        mode = "ohne Ollama; die Zahlen stimmen, die Agenten-Texte sind Platzhalter"
    else:
        mode = f"mit dem Sprachmodell «{draft.get('model', '?')}» für die Agenten-Narrative"

    return f"Sie starten {scope} über **{ticks} Ticks**, ausgehend von {basis}, {mode}."


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
        else:
            children.append(
                ui.alert(
                    "Keine Presets unter `configs/sweeps/` gefunden.", "warning", class_name="mt-4"
                )
            )

    return ui.card(*children)


def _scope_card(draft: dict) -> html.Div:
    return ui.card(
        ui.grid(
            c.number("rounds", int(draft.get("rounds") or 40), min=1, max=500, step=1),
            c.number("run_count", int(draft.get("run_count") or 1), min=1, max=20, step=1),
            cols="md:grid-cols-2",
        )
    )


def _mode_card(draft: dict) -> html.Div:
    return ui.card(
        ui.note(
            "**Die Zahlen kommen immer aus dem Rechenmodell, nie aus dem Sprachmodell.** "
            "Preise, Buchungsraten und Faktorzustände werden deterministisch berechnet. "
            "Die Agenten liefern ausschließlich die Deutung dazu — die Einstellung hier "
            "ändert also, wie viel *erzählt* wird, nicht was herauskommt.",
            icon_name="shield",
        ),
        html.Div(
            [
                c.check("mock_llm", draft.get("mock_llm", True)),
                c.check("deterministic_only", draft.get("deterministic_only", False)),
            ],
            className="space-y-3 mt-5",
        ),
    )


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            ui.section(
                "Annahmenwelt",
                ui.lede(
                    "Wovon der Lauf ausgeht. Ein Preset ist der schnellste Einstieg — "
                    "Sie können danach in den anderen Tabs einzelne Annahmen verändern."
                ),
                _scenario_card(draft),
                actions=ui.doc_link("presets"),
            ),
            ui.section(
                "Umfang",
                ui.lede(
                    "Wie weit der Lauf reicht und wie oft er wiederholt wird. "
                    "Mehrere Wiederholungen zeigen, ob ein Ergebnis trägt oder Zufall war."
                ),
                _scope_card(draft),
                actions=ui.doc_link("tick-und-lauf"),
            ),
            ui.section(
                "Rechenmodus",
                _mode_card(draft),
            ),
            ui.section(
                "Das ist eingestellt",
                ui.card(
                    html.Div(ui.markdown(summary_sentence(draft)), id=summary_id("overview")),
                    html.P(
                        "Alles Weitere — Politik, Kosten, Bevölkerung, Preisverhalten — "
                        "steht in den übrigen Tabs und ist mit sinnvollen Werten vorbelegt.",
                        className=f"{ui.CAPTION} mt-3",
                    ),
                ),
            ),
        ]
    )
