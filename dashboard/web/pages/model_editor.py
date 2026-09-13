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
#:
#: **Er bleibt leer, bis jemand den Bereich aufsucht** (P3.12, 2026-09-05). Der
#: Inhalt lag auch dann im DOM, wenn jemand in der Schrittfolge arbeitete, und
#: kostete gemessen **jeden Klick dort rund eine Sekunde**: Dashs
#: `dash_renderer` benachrichtigt bei *jeder* Callback-Antwort alle
#: angeschlossenen Komponenten (`notifyNestedSubs`), und das skaliert mit ihrer
#: Zahl — nicht mit der Größe des sichtbaren Bereichs.
#:
#: Gemessen im CPU-Profil eines Klicks: 71,6 % der Zeit in `dash_renderer`,
#: 10,5 % in React, Plotly gar nicht. Mit leerem Wirt fielen die 1218 ms auf
#: 246 ms und die längste Browser-Aufgabe von 1144 ms auf 267 ms.
#:
#: **Die Größe dieses Bereichs, nachgemessen am 2026-09-06 — und mit der
#: Methode, weil sie das Ergebnis bestimmt** (C1 des Phase-3-Audits):
#:
#: * **1477** Knoten hat die Schrittfolge, wenn dieser Wirt leer ist
#:   (`document.querySelectorAll('*').length` bei 1280 px, nach dem Klick auf
#:   «Neuen Lauf einrichten»).
#: * **1886** Knoten trägt sein Teilbaum, wenn der Bereich offen ist
#:   (`#model-editor-host` mit allen Nachkommen), darunter **146**
#:   Bedienelemente (`input, select, textarea` darin).
#: * **3364** Knoten hätte die Seite, wenn beides gleichzeitig hinge — also
#:   **mehr als die Hälfte** für einen Bereich, den niemand sieht.
#:
#: **Die drei Zahlen standen hier bis zum 2026-09-06 als 168 / 1404 / 2882, und
#: keine davon reproduzierte.** Sie stammten aus verschiedenen Messungen zu
#: verschiedenen Zeitpunkten — 2882 − 1404 ergibt 1478 und nicht 1477, und daran
#: fiel es auf. Die 168 sind zudem eine **historische** Zahl: Sie beschreibt die
#: beiden Schritte 4 und 5 des Assistenten, wie sie vor P1.9-W3.1 aussahen, nicht
#: diesen Bereich heute. Wer eine Zahl in die Doku schreibt, schreibt dazu, **wie**
#: sie entstanden ist — sonst ist sie in drei Tagen ein Gerücht. Das gilt
#: allgemein und ist als [P4.3](../../../docs/projektplan.md) eingeplant.
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

#: Unter welcher Adresse dieser Bereich liegt — **eine** Quelle (P3.12).
#:
#: Der Callback, der den Rumpf baut, muss wissen, ob der Bereich offen ist. Den
#: Pfad `"modell"` dort als Zeichenkette hinzuschreiben wäre eine zweite Quelle
#: neben `shell.ROUTES`: Wer den Bereich später umbenennt, ließe einen Bereich
#: zurück, der nie mehr gebaut wird — und zwar lautlos.
ROUTE = "modell"


def body(draft: dict) -> html.Div:
    """Faktorlage, Systemgrößen, Bevölkerung und Preisbildung — unverändert.

    Die Reihenfolge ist die aus der Schrittfolge und bleibt es: erst die Welt in
    groben Zügen (`macro`), dann wer darin bucht und wie der Preis entsteht
    (`micro`).
    """

    try:
        return html.Div([macro.layout(draft), micro.layout(draft)])
    except Exception as exc:  # noqa: BLE001 - eine kaputte Config soll den Bereich nicht sprengen
        return ui.hinweis(f"Modell konnte nicht aufgebaut werden: {exc}", "fehler")


def rumpf_fuer(pathname: str | None, draft: dict | None) -> object:
    """Der Rumpf, wenn dieser Bereich offen ist — sonst nichts (P3.12).

    Als eigene Funktion und nicht im Callback, aus demselben Grund wie bei
    `shell.active_route`: So ist die Entscheidung ohne laufende App prüfbar, und
    `config_editor._model_editor` bleibt eine Verdrahtung. Ein umhüllter
    Dash-Callback lässt sich von außen nicht aufrufen — er verlangt seinen
    Kontext —, und eine Entscheidung, die nur im Browser prüfbar ist, wird
    seltener geprüft.

    **Leeren statt stehen lassen**, wenn der Bereich nicht offen ist: Ein
    Bereich, den niemand sieht, soll auch nicht mitgerechnet werden. Genau darin
    liegt der Gewinn — Dashs `dash_renderer` benachrichtigt bei jeder Antwort
    alle angeschlossenen Komponenten, und der Teilbaum dieses Wirts ist **mehr
    als die Hälfte** aller (1886 von 3364 — die Messung steht bei :data:`HOST`).
    """

    from dashboard.web import shell

    if shell.active_route(pathname) != ROUTE:
        return []
    return body(draft or {})


def layout(draft: dict | None = None) -> html.Div:
    """Der Rahmen des Bereichs — **ohne** seine 146 Bedienelemente (P3.12).

    *draft* wird nicht mehr gelesen und bleibt in der Signatur: `app.py` ruft
    `layout(draft)` beim Aufbau des Bildschirms, und der Rumpf entsteht jetzt im
    Callback `config_editor._model_editor`, sobald jemand den Bereich aufsucht.
    Ein Parameter zu entfernen, den ein Aufrufer noch übergibt, wäre eine zweite
    Änderung in derselben Zeile.
    """

    return html.Div(
        [
            ui.page_heading(
                "Modell",
                "Die Annahmen, aus denen jeder Lauf rechnet — Systemgrößen, Preisbildung, "
                "Sättigung und Bevölkerung. Was Sie hier ändern, gilt für den nächsten "
                "Lauf; was Sie ausdrücklich speichern, für alle künftigen.",
            ),
            html.Div(
                id=STATUS,
                className="mb-4",
                # «Segment gelöscht» ist eine Rückmeldung auf eine Handlung,
                # die man gerade ausgelöst hat — sie gehört angesagt (W5.3).
                **{"aria-live": "polite"},
            ),
            # **Leer** — gefüllt wird beim Aufsuchen des Bereichs (P3.12). Der
            # Callback `_model_editor` hört dafür auf den Pfad; `entwurf` steht
            # hier nur noch für die Überschriften darüber.
            html.Div([], id=HOST),
        ],
        className="af-pane af-pane--focus",
    )
