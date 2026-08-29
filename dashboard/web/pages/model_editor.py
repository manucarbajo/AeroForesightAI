"""Der Bereich «Modell»: die Annahmen, aus denen jeder Lauf rechnet (P1.9-W3.1).

**Der Assistent richtet ein Experiment ein. Hier wird das Modell gepflegt.**
Das ist die tragende Entscheidung aus P1.9, und sie kommt aus einem
Kategorienfehler: Bis hierher lagen beide in derselben Schrittfolge. Die
Schritte 4 und 5 — «Rahmenbedingungen» und «Nachfrage & Preisbildung» — trugen
zusammen **168 Bedienelemente** und brauchten 3,0 bzw. 4,0 Bildschirme, während
die drei Entscheidungsschritte davor mit drei, fünf und zehn Feldern auskamen.
In einer Liste mit gleichem Gewicht geführt, machte das die Zählung «Schritt 5
von 8» bedeutungslos: Der fünfte Schritt war nicht fünf Achtel des Weges, er
war das Vielfache aller anderen zusammen.

Die beiden Sorten Arbeit vertragen sich nicht:

* **Ein Experiment einrichten** ist eine kurze, lineare Entscheidungsfolge. Sie
  braucht Führung, wenige Fragen und einen sichtbaren Ausgang.
* **Ein Modell pflegen** ist Facharbeit an vielen Zahlen. Sie braucht Fläche,
  Überblick und die Möglichkeit, zwischen Größen hin- und herzuspringen — genau
  das, was eine Schrittfolge verhindert.

**Dieses Modul ist ein reiner Umzug** (Regel 6 des Commit-Regelwerks): Es
rendert `macro.layout` und `micro.layout` unverändert. Was an ihnen zu ändern
ist, gehört in eigene Commits — allen voran W3.2, das die fünf Bedienelemente
angeht, die von hier aus ohne Rückfrage in `configs/properties.json` schreiben.

**Der Bereich bekommt den Bildschirm allein** (`FOCUS_ROUTES`), aus demselben
Grund wie das Einrichten: Eine Szene daneben, die einen anderen Lauf zeigt,
lenkt von einer Arbeit ab, bei der es auf Zahlen ankommt.
"""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import macro, micro

#: Wirt für den Inhalt. Eigener Knoten, damit ein Callback ihn nachziehen kann,
#: ohne die Überschrift neu zu bauen — dieselbe Aufteilung wie bei den Wirten
#: der Schrittfolge.
HOST = "model-editor-host"

#: Wo die Rückmeldung einer Aktion erscheint — «Segment gelöscht», «Population
#: gespeichert».
#:
#: **Ohne diesen Ort landete sie im Nichts.** `_actions` schrieb sie nach
#: `cfg-status`, und der liegt in der Schrittfolge — also im Bereich
#: «Einrichten», der während der Arbeit am Modell ausgeblendet ist. Die Meldung
#: entstand, war im DOM, und niemand sah sie. Am laufenden System bei der
#: Umsetzung von W3.2 aufgefallen: Der Umzug aus W3.1 hat die Aktionen
#: mitgenommen, ihre Rückmeldung aber nicht.
STATUS = "model-editor-status"


def body(draft: dict) -> html.Div:
    """Faktorlage, Systemgrößen, Bevölkerung und Preisbildung — unverändert.

    Die Reihenfolge ist die aus der Schrittfolge und bleibt es: erst die Welt in
    groben Zügen (`macro`), dann wer darin bucht und wie der Preis entsteht
    (`micro`).
    """

    try:
        return html.Div([macro.layout(draft), micro.layout(draft)])
    except Exception as exc:  # noqa: BLE001 - eine kaputte Config soll den Bereich nicht sprengen
        return ui.alert(f"Modell konnte nicht aufgebaut werden: {exc}", "error")


def layout(draft: dict | None = None) -> html.Div:
    from dashboard.web.state import initial_draft_dict

    entwurf = draft if draft is not None else initial_draft_dict()

    return html.Div(
        [
            ui.page_heading(
                "Modell",
                "Die Annahmen, aus denen jeder Lauf rechnet — Faktorlage, Systemgrößen, "
                "Bevölkerung und Preisbildung. Was Sie hier ändern, gilt für den nächsten "
                "Lauf; was Sie ausdrücklich speichern, für alle künftigen.",
            ),
            html.Div(
                id=STATUS,
                className="mb-4",
                # «Segment gelöscht» ist eine Rückmeldung auf eine Handlung,
                # die man gerade ausgelöst hat — sie gehört angesagt (W5.3).
                **{"aria-live": "polite"},
            ),
            html.Div(body(entwurf), id=HOST),
        ],
        className="af-pane af-pane--focus",
    )
