"""Der Lauf-Browser: ein Dialog aus der Kopfzeile statt eines Auswahlfelds (P7.3-U3.3, D6).

**Warum kein Auswahlfeld mehr.** Das Audit zählte 388 Einträge in einer Liste ohne
Art, ohne Rechenmodus und ohne Zustand, Prüfläufe gleichrangig neben Rahmen. Name
und Sortierung sind mit Teil 1 und 2 gelöst (Name · Rahmen · Datum, der jüngste
zuerst); was fehlte, war **finden**: eine Suche, ein Filter nach Art und eine
Zeile, die sagt, was für ein Lauf das ist.

**Warum ein Dialog** (von Haiko entschieden am 2026-09-14): Er nimmt keinem Bereich
Fläche weg, und der Browser leistet, was ein Dialog braucht — `showModal()` hält den
Fokus darin, Escape schließt, der Fokus kehrt zum Öffner zurück. Dieselbe Maschinerie
wie die Rückfrage (`config_editor/controls.write_action`). Der Öffner steht seit
P7.3-U3.4 nur im Leitstand und unter «Ergebnisse».

**Wie viel davon im DOM steht.** Jede eingehängte Komponente kostet jeden Klick in
der Schrittfolge etwas (P3.12). Die Liste wird deshalb erst beim Öffnen gefüllt,
nach einer Wahl geleert und zeigt höchstens `LISTE_MAX` Einträge — wer mehr sucht,
grenzt ein.
"""

from __future__ import annotations

from dataclasses import dataclass

from dash import ALL, Input, Output, ctx, dcc, html, no_update

from dashboard.config_catalog import rahmenszenarien
from dashboard.run_browser import RunSummary
from dashboard.web import components as ui
from dashboard.web import shell
from dashboard.web.pages import runs as runs_page
from src.reporting.output_writer.provenance import COMPUTE_MODE_LABELS

DIALOG = "lauf-wahl-dialog"
SUCHE = "lauf-wahl-suche"
FILTER = "lauf-wahl-filter"
LISTE = "lauf-wahl-liste"
#: Der Typ der Muster-Kennung einer Zeile: `{"type": EINTRAG, "run": run_id}`.
EINTRAG = "lauf-wahl-eintrag"

#: Art → wie sie heißt. **«Wiederholung» und nicht «Ensemble»**, weil das Handbuch
#: sie so nennt (`lauf-starten.md`); ein zweites Wort für dieselbe Sache wäre die
#: Drift, die das Glossar verhindern soll.
ARTEN = {
    "einzellauf": "Einzellauf",
    "wiederholung": "Wiederholung",
    "vergleich": "Szenario-Vergleich",
    "pruef": "Prüflauf",
}

#: Der Filter, der beim Öffnen gilt: alles außer Prüfläufen (D6).
OHNE_PRUEF = "ohne-pruef"

FILTER_OPTIONEN = [
    {"label": "Alle außer Prüfläufen", "value": OHNE_PRUEF},
    {"label": "Einzelläufe", "value": "einzellauf"},
    {"label": "Wiederholungen", "value": "wiederholung"},
    {"label": "Szenario-Vergleiche", "value": "vergleich"},
    {"label": "Prüfläufe", "value": "pruef"},
]

#: Wie viele Zeilen die Liste höchstens zeigt. Gemessen lagen am 2026-09-14 194
#: Läufe unter `outputs/`; alle zu zeigen hieße 194 Knöpfe im DOM.
LISTE_MAX = 30

#: Was an einem Lauf steht, dessen Metadaten keinen Rechenmodus kennen.
OHNE_MODUS = "Rechenmodus nicht festgehalten"


def lauf_art(summary: RunSummary, rahmen_ids: set[str] | frozenset[str]) -> str:
    """Welche Art ein Lauf ist — **abgeleitet, weil ein Lauf sie nicht festhält**.

    **Ein Prüflauf ist ein Lauf unter einem hinterlegten Szenario, das heute kein
    Rahmenszenario ist.** Dieselbe Quelle, aus der ein Szenario-Vergleich seine
    Rahmen nimmt (`rahmenszenarien`): Was dort nicht steht, behauptet keine
    Zukunft. Die Regel fragt bewusst **nicht** nach `art == "stresstest"`: Gemessen
    am 2026-09-14 standen sieben von zehn Vergleichsläufen unter Szenarien, deren
    Datei es nicht mehr gibt («Short Test Sweep», «High Base Price», «LLM-Schalter»)
    — ihre Art lässt sich nicht mehr nachschlagen, und genau sie sind die
    Prüfläufe, die das Audit gleichrangig in der Auswahl fand.

    Ein Lauf unter der Standard-Ausgangslage oder unter eigenen Werten ist kein
    Prüflauf, auch wenn er ohne Sprachmodell gerechnet ist.
    """

    if summary.rahmen_quelle == "preset" and summary.rahmen_id not in rahmen_ids:
        return "pruef"
    if summary.run_id.startswith("sweeps/"):
        return "vergleich"
    if summary.run_id.startswith("batch_"):
        return "wiederholung"
    return "einzellauf"


@dataclass(frozen=True)
class Eintrag:
    """Eine Zeile des Lauf-Browsers — und wonach sie sich finden lässt."""

    run_id: str
    bezeichnung: str
    art: str
    merkmale: str
    suchtext: str


def eintraege(
    summaries: list[RunSummary],
    *,
    rahmen_ids: set[str] | frozenset[str],
    bezeichnungen: dict[str, str],
) -> list[Eintrag]:
    """Die Zeilen in der Reihenfolge der Läufe — der jüngste zuerst (`list_runs`).

    *bezeichnungen* kommt aus `runs.run_options`, damit der Dialog einen Lauf so
    nennt wie Lauf-Kopf und Übersicht: Name · Rahmen · Datum (D6).
    """

    zeilen: list[Eintrag] = []
    for summary in summaries:
        art = lauf_art(summary, rahmen_ids)
        bezeichnung = bezeichnungen.get(summary.run_id, summary.run_id)
        merkmale = [ARTEN[art], COMPUTE_MODE_LABELS.get(summary.compute_mode or "", OHNE_MODUS)]
        if summary.degraded:
            merkmale.append("beeinträchtigt")
        text = " · ".join(merkmale)
        zeilen.append(
            Eintrag(
                run_id=summary.run_id,
                bezeichnung=bezeichnung,
                art=art,
                merkmale=text,
                suchtext=f"{bezeichnung} {text}".casefold(),
            )
        )
    return zeilen


def filtern(zeilen: list[Eintrag], *, suche: str | None, art: str | None) -> list[Eintrag]:
    """Was zu Suche und Filter passt — **jedes Wort** der Suche, groß oder klein.

    Gesucht wird in Bezeichnung, Art und Rechenmodus. Die Reihenfolge bleibt die
    der Läufe: Der erste Treffer ist der jüngste.
    """

    woerter = (suche or "").casefold().split()
    gewaehlt = art or OHNE_PRUEF
    return [
        zeile
        for zeile in zeilen
        if (zeile.art != "pruef" if gewaehlt == OHNE_PRUEF else zeile.art == gewaehlt)
        and all(wort in zeile.suchtext for wort in woerter)
    ]


def _zeile(zeile: Eintrag) -> html.Button:
    return html.Button(
        [
            html.Span(
                zeile.bezeichnung,
                className=f"af-laufwahl__name font-body {ui.BESCHRIFTUNG} font-medium af-text-body",
            ),
            html.Span(zeile.merkmale, className=f"af-laufwahl__merkmale {ui.CAPTION}"),
        ],
        id={"type": EINTRAG, "run": zeile.run_id},
        # **Ein Absenden des Formulars schließt den Dialog** — ohne eine Zeile
        # Skript, wie bei der Rückfrage. Die Wahl selbst geht über `n_clicks`.
        type="submit",
        n_clicks=0,
        className="af-laufwahl__eintrag",
    )


def liste(treffer: list[Eintrag]) -> list:
    """Höchstens `LISTE_MAX` Zeilen, und was darüber hinausgeht, als Zahl."""

    if not treffer:
        return [ui.empty_state("Kein Lauf passt zu Suche und Filter.", icon_name="science")]
    zeilen: list = [_zeile(zeile) for zeile in treffer[:LISTE_MAX]]
    rest = len(treffer) - LISTE_MAX
    if rest > 0:
        zeilen.append(
            html.P(f"{rest} weitere — die Suche grenzt ein.", className=f"{ui.CAPTION} mt-2")
        )
    return zeilen


def dialog() -> html.Dialog:
    """Der Dialog «Lauf wählen».

    **Suche und Filter stehen außerhalb des Formulars**, die Zeilen darin. Sonst
    schlösse ein Druck auf die Eingabetaste im Suchfeld den Dialog, ohne dass
    etwas gewählt ist. Das Suchfeld ist das erste fokussierbare Element: Es
    bekommt beim Öffnen den Fokus, und wer tippt, sucht.
    """

    return html.Dialog(
        [
            html.H3("Lauf wählen", className=ui.H3),
            ui.field(
                "Suchen",
                dcc.Input(
                    id=SUCHE,
                    type="search",
                    value="",
                    placeholder="Name, Rahmen, Datum oder Rechenmodus",
                    autoComplete="off",
                    className="af-input",
                ),
                class_name="mt-4",
            ),
            html.Div(
                ui.radio(FILTER_OPTIONEN, value=OHNE_PRUEF, legend="Welche Läufe", id=FILTER),
                className="mt-4",
            ),
            html.Form(
                [
                    html.Div(id=LISTE, className="af-laufwahl__liste mt-4"),
                    html.Div(
                        ui.button("Schließen", variant="ghost", type="submit"),
                        className="flex justify-end mt-4",
                    ),
                ],
                method="dialog",
            ),
        ],
        id=DIALOG,
        className="af-rueckfrage",
        **{"aria-label": "Lauf wählen"},
    )


def _alle_eintraege() -> list[Eintrag]:
    optionen, by_id = runs_page.run_options()
    return eintraege(
        [by_id[option["value"]] for option in optionen],
        rahmen_ids={rahmen.id for rahmen in rahmenszenarien()},
        bezeichnungen={option["value"]: option["label"] for option in optionen},
    )


def bezeichnung_fuer(selected: dict | None) -> str | None:
    """Wie der gewählte Lauf auf dem Öffner heißt — oder nichts, wenn es ihn nicht gibt."""

    run_id = (selected or {}).get("run_id")
    if not run_id:
        return None
    optionen, _ = runs_page.run_options()
    return next((option["label"] for option in optionen if option["value"] == run_id), None)


def register_callbacks(app) -> None:
    # **Öffnen im Browser, ohne Rundlauf** — und mit `showModal()`, nicht mit dem
    # Attribut `open`: Nur der modale Aufruf hält den Fokus im Dialog und schließt
    # mit Escape. Der Ausgang wird nie geschrieben; Dash verlangt einen.
    app.clientside_callback(
        """
        function (geklickt) {
            if (!geklickt) { return window.dash_clientside.no_update; }
            var dialog = document.getElementById('%s');
            if (dialog && !dialog.open) { dialog.showModal(); }
            return window.dash_clientside.no_update;
        }
        """ % DIALOG,
        Output(DIALOG, "title"),
        Input(shell.LAUF_WAHL, "n_clicks"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output(LISTE, "children"),
        Input(shell.LAUF_WAHL, "n_clicks"),
        Input(SUCHE, "value"),
        Input(FILTER, "value"),
        prevent_initial_call=True,
    )
    def _liste(_geoeffnet, suche: str | None, art: str | None):
        return liste(filtern(_alle_eintraege(), suche=suche, art=art))

    @app.callback(
        Output("selected-run-store", "data", allow_duplicate=True),
        Output(LISTE, "children", allow_duplicate=True),
        Input({"type": EINTRAG, "run": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _waehle(_klicks):
        """Eine Zeile gewählt: Lauf setzen, Liste leeren (siehe Modul-Docstring).

        Eine neu gezeichnete Liste meldet ihre Zeilen mit `n_clicks = 0` — das ist
        keine Wahl.
        """

        ausloeser = ctx.triggered_id
        if not isinstance(ausloeser, dict) or not (ctx.triggered and ctx.triggered[0].get("value")):
            return no_update, no_update
        run_id = ausloeser.get("run")
        _, by_id = runs_page.run_options()
        summary = by_id.get(run_id)
        if summary is None:
            return no_update, no_update
        return {"run_id": run_id, "run_dir": str(summary.run_dir)}, []

    @app.callback(
        Output(shell.LAUF_WAHL, "children"),
        Input("selected-run-store", "data"),
    )
    def _oeffner(selected: dict | None):
        return shell.lauf_wahl_inhalt(bezeichnung_fuer(selected))
