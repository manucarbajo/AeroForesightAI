"""Der Bereich «Einrichten»: alles, was einen Lauf festlegt — auf voller Breite.

Bis P1.6 stand das hier in der linken Spalte. Gemessen am laufenden System war
diese Spalte damit **10,7 Bildschirme** hoch, trug 752 Wörter und 122
Eingabefelder, und der Start-Knopf lag 6,1 Bildschirme tief. Der geführte
Ablauf aus P1.1 war für eine 1400 px breite Seite entworfen; in 336 px wurde
aus jeder Preset-Zeile eine 102 px hohe Karte und aus zehn Presets ein
Dreifach-Bildschirm.

**Einrichten und Beobachten sind zwei Betriebsarten mit gegenläufigen
Anforderungen.** Einrichten braucht Fläche, Fließtext und sechzig Felder;
Beobachten braucht Dichte, Ruhe und wenige, immer sichtbare Bedienelemente.
Sie in dieselbe Zone zu legen geht nur zulasten einer von beiden.

Deshalb ist das Einrichten seit P1.6 ein eigener Viewport-Bereich, wie
«Ergebnisse» und «Handbuch» auch. Der Inhalt ist **verschoben, nicht neu
geschrieben**: derselbe `start_flow`, dieselben vier Editor-Tabs, dieselben
Callbacks.

**Der Start-Knopf bleibt links im Bedienfeld** und damit sichtbar, während man
hier einstellt. Ein zweiter hier wäre eine zweite Feld-ID und ein zweiter
Startpfad — beides ohne Gewinn.
"""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web import config_editor
from dashboard.web.state import initial_draft_dict


def layout(draft: dict | None = None) -> html.Div:
    """Der geführte Ablauf, darunter die vier Editor-Bereiche."""

    draft = draft or initial_draft_dict()
    return html.Div(
        [
            ui.page_heading(
                "Lauf einrichten",
                "Drei Entscheidungen genügen: was gerechnet wird, wie weit, und womit. "
                "Alles Weitere ist mit sinnvollen Werten vorbelegt.",
            ),
            # Der Hinweis gilt nur dort, wo die Spalte eine Schublade ist —
            # dann steht der Start-Knopf nicht sichtbar daneben. Auf breiten
            # Fenstern blendet ihn das Stylesheet aus.
            html.Div(
                ui.note(
                    "Gestartet wird links im Bedienfeld. Auf schmalen Fenstern öffnen Sie "
                    "es über das Menü-Symbol oben links.",
                    icon_name="arrow_back",
                ),
                className="af-drawer-hint",
            ),
            html.Div(config_editor.start_layout(draft), className="mt-6"),
            ui.divider("my-8"),
            html.Div(
                [
                    html.H2("Alle Einstellungen", className=ui.H2),
                    html.P(
                        "Die Annahmen hinter dem Lauf. Änderungen wirken auf den nächsten "
                        "Start; die «Speichern»-Knöpfe unter «Nachfrage & Preisbildung» "
                        "schreiben zusätzlich in die Dateien unter `configs/`.",
                        className=f"{ui.CAPTION} mt-1 mb-4 max-w-3xl",
                    ),
                    config_editor.layout(draft),
                ]
            ),
        ],
        className="af-pane",
    )
