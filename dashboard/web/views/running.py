"""Der Lauf, während er rechnet — als eigener Bildschirm (P1.7).

Bis hierher war der Start kein Ereignis: Man drückte «Start», und die Seite sah
aus wie vorher. Dass etwas passierte, stand in einem Punkt in der Kopfzeile und
in einer zugeklappten Konsole; das Auffälligste am Bildschirm blieb das
Einrichtungsformular — also genau das, was gerade vorbei war.

Während gerechnet wird, gibt es genau **eine** Auskunft, auf die es ankommt: wie
weit. Dieser Bildschirm zeigt sie groß, sagt daneben, was gerade gerechnet wird,
und stellt die Konsole **aufgeklappt** darunter — hier ist sie kein
Nachschlagewerk, sondern das Einzige, was sich bewegt.

Zwei Fassungen desselben Zustands leben in diesem Modul:

* `render()` — der volle Bildschirm, im Viewport des Leitstands.
* `dock()` — das Fortschrittsfenster unten rechts, für alle anderen Bereiche.
  Wer während eines Laufs einen älteren Lauf ansehen will, soll das können, ohne
  den laufenden aus den Augen zu verlieren.

**Der Balken lügt nicht.** `Progress.fraction` ist `None`, solange keine
Tick-Zeile vorliegt; dann läuft ein unbestimmter Balken statt einer erfundenen
Prozentzahl (Invariante 1).
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web import routing
from dashboard.web.config_editor import compute_mode
from dashboard.web.runner import Progress

#: Wie viele Konsolenzeilen der Ladebildschirm zeigt. Mehr als hier passt nicht
#: auf den Schirm, und die vollständige Ausgabe steht später in den Artefakten.
CONSOLE_LINES = 60

DOCK_HOST = "run-dock"
DOCK_TOGGLE = "run-dock-toggle"


#: Der Abbruch-Knopf und sein Meldungsplatz. Beide stehen **immer** im Layout
#: des Ladebildschirms; dass es sie nur während eines Laufs zu sehen gibt, ist
#: eine Frage der Sichtbarkeit — ein fehlender `Input` legt in Dash den ganzen
#: Callback lahm (Regel 6 der Architektur-Map).
CANCEL = "run-cancel"
CANCEL_STATUS = "run-cancel-status"


def _bar(progress: Progress, *, compact: bool = False) -> html.Div:
    """Der Fortschrittsbalken — bestimmt oder unbestimmt."""

    anteil = progress.fraction
    klassen = "af-progress" + (" af-progress--compact" if compact else "")
    if anteil is None:
        return html.Div(
            html.Div(className="af-progress__fill af-progress__fill--unknown"),
            className=klassen,
            title="Noch keine Tick-Meldung — der Fortschritt ist unbekannt.",
        )
    return html.Div(
        html.Div(
            className="af-progress__fill",
            style={"width": f"{anteil * 100:.1f}%"},
        ),
        className=klassen,
    )


def _readout(progress: Progress) -> str:
    if progress.tick and progress.total:
        return f"Tick {progress.tick} von {progress.total}"
    return "Lauf wird vorbereitet …"


def _percent(progress: Progress) -> str:
    anteil = progress.fraction
    return "—" if anteil is None else f"{anteil:.0%}"


def _what(draft: dict) -> html.Div:
    """Was gerade gerechnet wird — dieselben drei Angaben wie im Bedienfeld."""

    from dashboard.web.pages.launch import _length, _scenario_name

    # `prose=True`, weil hier **Text** steht und keine Zahl: Im Zahlensatz
    # sprengten «Standard-Ausgangslage» und «Ohne Sprachmodell» ihre Karten.
    return ui.grid(
        ui.metric_tile("Szenario", _scenario_name(draft), prose=True),
        ui.metric_tile("Umfang", _length(draft), prose=True),
        ui.metric_tile("Rechenmodus", compute_mode.short_label(draft), prose=True),
        cols="sm:grid-cols-3",
        gap="gap-3",
    )


def render(progress: Progress, draft: dict) -> html.Div:
    """Der volle Ladebildschirm."""

    zeilen = [ui.log_line("muted", line) for line in reversed(progress.lines[-CONSOLE_LINES:])]

    return html.Div(
        [
            html.Div(
                [
                    ui.badge("Simulation läuft", variant="info", icon_name="autorenew"),
                    html.H1("Der Lauf rechnet", className=f"{ui.H1} mt-3"),
                    html.P(
                        "Die Zahlen entstehen jetzt in Python. Sie können in der Zwischenzeit "
                        "unter «Ergebnisse» einen früheren Lauf ansehen — der Fortschritt "
                        "bleibt dann unten rechts sichtbar.",
                        className=f"{ui.CAPTION} mt-2 max-w-2xl",
                    ),
                ],
                className="mb-6",
            ),
            ui.card(
                html.Div(
                    [
                        html.Span(_readout(progress), className="af-run__readout"),
                        html.Span(_percent(progress), className="af-run__percent af-num"),
                    ],
                    className="flex items-baseline justify-between gap-4 mb-3",
                ),
                _bar(progress),
                html.P(progress.line or "…", className=f"{ui.CAPTION} mt-3 font-mono truncate"),
            ),
            html.Div(_what(draft), className="mt-5"),
            # **Abbrechen** (P1.9-W4.5). Bis dahin lief ein Lauf bis zum Ende
            # oder bis der Prozess starb: Wer versehentlich 500 Ticks mit
            # Sprachmodell startete, konnte nur warten oder den Server neu
            # starten. Der Satz daneben sagt, was «abbrechen» hier heißt — der
            # Lauf endet nach dem laufenden Tick, nicht sofort.
            html.Div(
                [
                    ui.button(
                        "Lauf abbrechen",
                        id=CANCEL,
                        variant="danger",
                        icon_name="stop_circle",
                    ),
                    html.P(
                        "Der Lauf endet nach dem laufenden Tick. Was bis dahin gerechnet "
                        "wurde, bleibt erhalten — der Lauf steht danach in der Auswahl, "
                        "mit weniger Ticks als geplant.",
                        className=f"{ui.CAPTION} mt-2 max-w-2xl",
                    ),
                    html.Div(
                        id=CANCEL_STATUS,
                        className="mt-2",
                        **{"aria-live": "polite"},
                    ),
                ],
                className="mt-6",
            ),
            html.Div(
                [
                    html.H2("Konsole", className=f"{ui.H3} mb-2"),
                    ui.console(zeilen, empty="Noch keine Ausgabe."),
                ],
                className="mt-6",
            ),
        ],
        className="af-pane p-5",
    )


def dock(progress: Progress) -> html.Div:
    """Das Fortschrittsfenster unten rechts.

    Es bricht den Lauf **nicht** ab — der gehört nicht diesem Fenster, und in
    einer Sitzung, die ihn nicht gestartet hat, wäre ein Abbruchknopf eine
    Zumutung. Es zeigt und führt hin, mehr nicht.
    """

    return html.Div(
        [
            html.Div(
                [
                    ui.icon("autorenew", "text-sm af-run__spin"),
                    html.Span("Simulation läuft", className="af-dock__title"),
                    html.Span(_percent(progress), className="af-dock__percent af-num"),
                ],
                className="af-dock__head",
            ),
            _bar(progress, compact=True),
            html.Div(
                [
                    html.Span(_readout(progress), className=ui.CAPTION),
                    dcc.Link(
                        "Ansehen",
                        href=routing.url(leitstand_route()),
                        className="af-dock__link",
                    ),
                ],
                className="af-dock__foot",
            ),
        ],
        className="af-dock",
        id=DOCK_HOST,
    )


def leitstand_route() -> str:
    """Wo der Leitstand liegt — aus der Bereichsliste, nicht hingeschrieben.

    Die Adresse ist mit P1.7 schon einmal umgezogen; ein zweiter Ort, an dem sie
    steht, waere die naechste Drift.
    """

    from dashboard.web import shell

    return next(route for route, label in shell.ROUTES if label == "Leitstand")


def finished_link() -> html.Div:
    """Der Weg von der Fertigmeldung in die Ergebnisse."""

    from dashboard.web import shell

    ziel = next(route for route, label in shell.ROUTES if label == "Ergebnisse")
    return html.Div(
        dcc.Link(
            [ui.icon("arrow_forward", "text-sm"), "Ergebnisse ansehen"],
            href=routing.url(ziel),
            className="af-btn af-btn--primary inline-flex items-center gap-1.5 "
            "px-3 py-1.5 font-body text-xs font-medium",
        ),
        className="mt-3",
    )


__all__ = ["render", "dock", "finished_link", "DOCK_HOST", "DOCK_TOGGLE"]
