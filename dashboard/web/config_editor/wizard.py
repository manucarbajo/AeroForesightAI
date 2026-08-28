"""Einrichten als Schrittfolge — ein Schritt, eine Frage (P1.7-C).

Vorher war das Einrichten eine Bildlaufstrecke: bei 1280 px **7,3 Bildschirme**,
und die vier Editor-Reiter lagen unten hinter einer Trennlinie. Reiter unterhalb
des Falzes sind keine Gliederung — man findet sie nur, wenn man ohnehin schon
weiß, dass es sie gibt. Wer zum ersten Mal hier stand, sah eine Wand und wusste
nicht, was als Nächstes zu tun ist.

Jetzt steht **eine** Frage auf dem Schirm, links die Liste aller Schritte mit
dem Stand, unten «Zurück» und «Weiter». Der Bildschirm sagt damit von selbst,
wo man ist, was noch kommt, und was der nächste Griff ist.

**Die Zusage aus P1.1 bleibt gültig: drei Entscheidungen genügen.** Die Schritte
vier bis sieben sind ausdrücklich als *optional* gekennzeichnet, jeder ist
überspringbar, und ab Schritt drei führt ein Weg direkt zum Schluss. Eine
Schrittfolge, die acht Stationen erzwingt, wäre ein Rückschritt gegenüber dem,
was P1.1 erreicht hat.

Zwei Regeln, die hier leicht zu brechen wären:

* **Nur der sichtbare Schritt steht im DOM.** Sonst stünden Felder doppelt, und
  eine doppelte Dash-ID ist ein Laufzeitfehler im Browser.
* **Ein Schrittwechsel schreibt nichts zurück.** Er tauscht nur, was zu sehen
  ist; gespeichert wird weiterhin ausschließlich vom Feld in den Store
  (Einbahnstraße aus P1.1). Ein Schritt, der beim Verlassen Werte setzte, führte
  dieselbe Zahl an zwei Stellen — genau der Fehler, den P1.1 bei der Lauflänge
  gemacht und wieder ausgebaut hat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dash import ALL, Input, Output, State, ctx, html, no_update

from dashboard.web import components as ui
from dashboard.web.config_editor import experiment, llm_pipeline, macro, micro, start_flow
from dashboard.web.state import STORE_ID

#: Welcher Schritt gerade offen ist. Als Store und nicht als Adresse, weil ein
#: halb ausgefülltes Formular kein Ort ist, den man verlinken oder mit dem
#: Zurück-Knopf des Browsers ansteuern will.
STEP_STORE = "wizard-step-store"

CONTENT = "wizard-content"
RAIL = "wizard-rail"
BACK = "wizard-back"
NEXT = "wizard-next"
SKIP = "wizard-skip"
#: Zweiter Auslöser für den Start — **nicht** ein zweiter Startpfad. Er hängt am
#: selben Callback wie der Knopf im Bedienfeld, mit derselben Prüfung und
#: demselben `runner.start`.
START = "wizard-start"
#: Ebenso für das Sichern als Szenario.
SAVE = "wizard-save"

#: Sprungziel je Schritt der Schrittliste.
JUMP = "wizard-jump"


@dataclass(frozen=True)
class Step:
    """Ein Schritt: Was gefragt wird, und ob er beantwortet werden muss."""

    key: str
    title: str
    lede: str
    body: Callable[[dict], object] | None = None
    #: `False` heißt: darf übersprungen werden, ohne dass etwas fehlt.
    required: bool = True


STEPS: list[Step] = [
    Step(
        "szenario",
        "Was soll gerechnet werden?",
        "Die Annahmenwelt, von der der Lauf ausgeht.",
        lambda draft: start_flow.scenario_step(draft, number=None),
    ),
    Step(
        "umfang",
        "Wie weit reicht der Lauf?",
        "Wie viele Modellrunden gerechnet werden.",
        lambda draft: start_flow.scope_step(draft, number=None),
    ),
    Step(
        "modus",
        "Womit wird gerechnet?",
        "Ob und wie die Agenten den Lauf in Worte fassen.",
        lambda draft: start_flow.mode_step(draft, number=None),
    ),
    Step(
        "rahmen",
        "Rahmenbedingungen",
        "Faktorlage und Systemgrößen — bereits sinnvoll vorbelegt.",
        macro.layout,
        required=False,
    ),
    Step(
        "nachfrage",
        "Nachfrage & Preisbildung",
        "Wie die Bevölkerung entscheidet und wie der Preis entsteht.",
        micro.layout,
        required=False,
    ),
    Step(
        "ablage",
        "Lauf & Ablage",
        "Name, Beschreibung und was am Ende geschrieben wird.",
        experiment.layout,
        required=False,
    ),
    Step(
        "technik",
        "Technik",
        "Sprachmodell, Adresse, Zeitgrenzen.",
        llm_pipeline.layout,
        required=False,
    ),
    Step(
        "start",
        "Prüfen & Starten",
        "Der letzte Blick — und dann los.",
        None,
    ),
]

#: Ab hier ist alles Feinjustierung. Nach Schritt 3 sind die drei Entscheidungen
#: aus P1.1 getroffen, und der Weg zum Start steht offen.
LAST_REQUIRED = 2
FINAL = len(STEPS) - 1


def clamp(step) -> int:
    try:
        value = int(step)
    except (TypeError, ValueError):
        return 0
    return max(0, min(value, FINAL))


# --- Die Schrittliste ------------------------------------------------------


def _rail_entry(index: int, step: Step, current: int) -> html.Button:
    if index < current:
        zustand, symbol = "done", "check"
    elif index == current:
        zustand, symbol = "current", "radio_button_checked"
    else:
        zustand, symbol = "todo", "radio_button_unchecked"

    return html.Button(
        [
            ui.icon(symbol, "af-step__icon text-base"),
            html.Span(
                [
                    html.Span(step.title, className="af-step__title"),
                    (
                        html.Span("optional", className="af-step__tag")
                        if not step.required
                        else None
                    ),
                ],
                className="af-step__text",
            ),
        ],
        id={"type": JUMP, "index": index},
        className=f"af-step af-step--{zustand}",
        n_clicks=0,
        title=f"Zu Schritt {index + 1}: {step.title}",
    )


def rail(current: int) -> html.Div:
    """Alle Schritte auf einen Blick — wo man ist und was noch kommt."""

    return html.Div(
        [
            html.P("Ihre Schritte", className="af-step__heading"),
            html.Div(
                [_rail_entry(i, step, current) for i, step in enumerate(STEPS)],
                className="af-steps",
            ),
        ],
        id=RAIL,
        className="af-wizard__rail",
    )


# --- Der Schritt selbst ----------------------------------------------------


def _final_step(draft: dict) -> html.Div:
    """Der letzte Blick vor dem Start.

    Die beiden Ausgänge — starten und sichern — stehen **nicht** hier, sondern
    in der Navigationsleiste: Dort sitzt auf jedem Schritt der nächste Griff,
    und der letzte Schritt soll keine Ausnahme sein. Technisch kommt dazu, dass
    die Leiste immer im DOM liegt; ein Knopf, den es nur auf einem Schritt gibt,
    legte jeden Callback lahm, der ihn als Eingang führt.
    """

    return html.Div(
        [
            start_flow.preflight(draft, start_flow.errors_for(draft), slot="wizard"),
            html.P(
                "«Als Szenario speichern» legt die Einstellungen unter `configs/sweeps/` ab. "
                "Sie stehen danach im ersten Schritt zur Auswahl.",
                className=f"{ui.CAPTION} mt-4",
            ),
        ]
    )


def content(draft: dict, current: int) -> html.Div:
    """Der offene Schritt — und **nur** er.

    Alle anderen bleiben aus dem DOM: Ihre Felder tragen dieselben Pattern-IDs,
    und zweimal dieselbe ID ist für Dash ein Laufzeitfehler.
    """

    step = STEPS[current]
    koerper = _final_step(draft) if step.body is None else step.body(draft)

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        f"Schritt {current + 1} von {len(STEPS)}",
                        className="af-wizard__counter",
                    ),
                    html.H2(step.title, className=ui.H2),
                    html.P(step.lede, className=f"{ui.CAPTION} mt-1"),
                ],
                className="mb-6",
            ),
            html.Div(koerper, id="wizard-body"),
        ],
        id=CONTENT,
        className="af-wizard__content",
    )


def navigation(current: int) -> html.Div:
    """«Zurück» und «Weiter» — und der Weg am Feinschliff vorbei.

    Der Abkürzungsknopf steht ab Schritt drei: Dort sind die drei Entscheidungen
    aus P1.1 getroffen, und alles Weitere ist mit sinnvollen Werten vorbelegt.
    Ohne ihn erzwänge die Schrittfolge acht Stationen für einen Lauf, der mit
    drei auskommt.
    """

    letzter = current >= FINAL
    # **Alle drei Knöpfe bleiben im DOM**, auch wo sie nichts zu tun haben — sie
    # werden nur ausgeblendet. Dash führt einen Callback gar nicht erst aus,
    # wenn auch nur *ein* Eingang fehlt: Auf Schritt 1 gab es «Direkt zum Start»
    # nicht, und damit war die ganze Navigation tot, «Weiter» eingeschlossen. Am
    # laufenden System aufgefallen — der Zähler blieb bei «Schritt 1 von 8», und
    # der Browser meldete «A nonexistent object was used in an Input».
    #
    # Dasselbe Muster wie bei den vier Viewport-Bereichen in `app.py`: im Layout
    # bleiben, Sichtbarkeit umschalten.
    return html.Div(
        [
            ui.button(
                "Zurück",
                id=BACK,
                variant="ghost",
                disabled=current <= 0,
                style=None if current > 0 else {"visibility": "hidden"},
            ),
            html.Div(
                [
                    ui.button(
                        "Direkt zum Start",
                        id=SKIP,
                        variant="secondary",
                        icon_name="fast_forward",
                        style=None if LAST_REQUIRED <= current < FINAL else {"display": "none"},
                    ),
                    ui.button(
                        "Weiter",
                        id=NEXT,
                        icon_name="arrow_forward",
                        style=None if not letzter else {"display": "none"},
                    ),
                    ui.button(
                        "Als Szenario speichern",
                        id=SAVE,
                        variant="secondary",
                        icon_name="save",
                        style=None if letzter else {"display": "none"},
                    ),
                    ui.button(
                        "Lauf starten",
                        id=START,
                        icon_name="play_arrow",
                        style=None if letzter else {"display": "none"},
                    ),
                ],
                className="flex items-center gap-3",
            ),
        ],
        className="af-wizard__nav",
    )


def layout(draft: dict, current: int = 0) -> html.Div:
    current = clamp(current)
    return html.Div(
        [
            ui.page_heading(
                "Lauf einrichten",
                "Beantworten Sie eine Frage nach der anderen. Drei genügen — der Rest ist "
                "mit sinnvollen Werten vorbelegt und darf übersprungen werden.",
            ),
            html.Div(id="cfg-status", className="mb-4"),
            html.Div(
                [
                    html.Div(rail(current), id="wizard-rail-host"),
                    html.Div(
                        [
                            html.Div(content(draft, current), id="wizard-content-host"),
                            # Das Kleben sitzt am **Wirt**, nicht an der
                            # Navigation darin: Ein klebendes Element bewegt
                            # sich nur innerhalb seines Elternkastens, und der
                            # Wirt ist exakt so hoch wie sein Inhalt -- damit
                            # gaebe es null Spielraum. Am laufenden System
                            # gemessen: «Weiter» lag trotz `sticky` bei y=1361.
                            html.Div(
                                navigation(current),
                                id="wizard-nav-host",
                                className="af-wizard__navhost",
                            ),
                        ],
                        className="af-wizard__main",
                    ),
                ],
                className="af-wizard",
            ),
        ],
        className="af-pane af-pane--focus",
    )


# --- Callbacks -------------------------------------------------------------


def register_callbacks(app) -> None:
    @app.callback(
        Output(STEP_STORE, "data"),
        Input(BACK, "n_clicks"),
        Input(NEXT, "n_clicks"),
        Input(SKIP, "n_clicks"),
        Input({"type": JUMP, "index": ALL}, "n_clicks"),
        State(STEP_STORE, "data"),
        prevent_initial_call=True,
    )
    def _navigate(_back, _next, _skip, _jump, current):
        """Alle Wege durch die Schrittfolge in einem Callback.

        Getrennte Callbacks müssten sich denselben Ausgang teilen und würden
        sich beim gleichzeitigen Feuern überschreiben — dieselbe Begründung wie
        bei den sechs Knöpfen der Zeitleiste.
        """

        jetzt = clamp(current)
        ausgeloest = ctx.triggered_id

        if isinstance(ausgeloest, dict) and ausgeloest.get("type") == JUMP:
            # Nur ein wirklich gedrückter Knopf zählt: Beim Neuaufbau der Liste
            # feuert Dash alle Pattern-Eingänge mit `None`.
            if not any(eintrag["value"] for eintrag in ctx.triggered if eintrag["value"]):
                return no_update
            return clamp(ausgeloest.get("index"))
        if ausgeloest == BACK:
            return max(0, jetzt - 1)
        if ausgeloest == NEXT:
            return min(FINAL, jetzt + 1)
        if ausgeloest == SKIP:
            return FINAL
        return no_update

    @app.callback(
        Output("wizard-content-host", "children"),
        Output("wizard-rail-host", "children"),
        Output("wizard-nav-host", "children"),
        Input(STEP_STORE, "data"),
        Input("cfg-editor-refresh", "data"),
        State(STORE_ID, "data"),
    )
    def _render(step, _refresh, draft: dict | None):
        """Den offenen Schritt zeichnen — Inhalt, Liste und Fußzeile in einem Zug.

        In **einem** Callback, weil alle drei denselben Stand zeigen: Getrennt
        könnten sie für einen Moment auseinanderlaufen und die Liste einen
        anderen Schritt hervorheben als den, der zu sehen ist.

        Nicht am Entwurf hängend: Der Schritt enthält Eingabefelder, und die
        dürfen nicht unter den Fingern ausgetauscht werden. Was sich laufend
        ändert, steht in den Slots, die `_live` füllt.
        """

        jetzt = clamp(step)
        data = draft or {}
        return content(data, jetzt), rail(jetzt), navigation(jetzt)
