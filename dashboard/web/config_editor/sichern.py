"""«Als Szenario sichern» — der eine Speicherweg (P7.4-U4.5).

**Bis dahin gab es vier**, mit drei Namensregeln: «Als Szenario sichern» und
«Zwischenstand sichern» in der Kopfzeile, «Als Szenario speichern» in der
Fußleiste des letzten Schritts (derselbe Callback wie der erste) und «Szenario
sichern» hinter einer Klappe in «Lauf & Ablage» mit eigenem Namensfeld — das
den eingegebenen Namen nebenbei auch zum Namen des Laufs machte. Keiner warnte,
wenn es das Szenario schon gab: `save_custom_sweep_preset` überschreibt.

**Was gilt** (von Haiko entschieden am 2026-09-14): Der Knopf in der Kopfzeile
des Einrichtens öffnet diesen Dialog — Name mit Vorschlag, «Mit Zeitstempel im
Namen sichern» als Option, eine Warnung, bevor etwas überschrieben wird. Er ist
der einzige
Aufrufer von `save_custom_sweep_preset`; `tests/test_web_sichern.py` sucht jeden
Aufruf im Quelltext.

Ein Szenario zu sichern ist die Ablage des **Experiments**, nicht des Modells
(Regel 7). Deshalb kein Hinweis auf eine Reichweite wie bei der Rückfrage im
Modell-Bereich — nur die Warnung, wenn ein vorhandenes Szenario ersetzt wird.

**Die Option heißt nicht «Zwischenstand».** So heißt in diesem Produkt der
Checkpoint eines Laufs (`checkpoint_interval`, im Glossar «Zwischenstand
sichern»). P7.3-U3.4 hatte den Kopfzeilen-Knopf trotzdem so genannt — ein Wort
für zwei Dinge, das beim Nachlesen auffiel und nicht beim Messen.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from dash import Input, Output, State, dcc, html, no_update

from dashboard.config_catalog import load_config_file, save_custom_sweep_preset, sweep_ziel
from dashboard.web import components as ui
from dashboard.web import shell
from dashboard.web.state import STORE_ID, draft_from_dict

DIALOG = "sichern-dialog"
NAME = "sichern-name"
ZEITSTEMPEL = "sichern-zeitstempel"
WARNUNG = "sichern-warnung"
BESTAETIGEN = "sichern-bestaetigen"

#: Der Vorschlag, wenn der Lauf keinen eigenen Namen trägt.
OHNE_NAMEN = "mein_szenario"


def vorschlag(draft: dict) -> str:
    """Der Name, den der Dialog vorschlägt: der des Laufs — außer dem Vorgabenamen.

    Dieselbe Regel wie `config_catalog.build_custom_sweep_from_draft` und
    `runs.lauf_bezeichnung`: Den Vorgabenamen trägt jeder Entwurf, als Name eines
    Szenarios unterschiede er nichts.
    """

    name = str(draft.get("simulation_name") or "").strip()
    vorgabe = str(load_config_file("simulation_config.json").get("name", ""))
    return name if name and name != vorgabe else OHNE_NAMEN


def dateiname(name: str | None, *, zeitstempel: bool, jetzt: datetime | None = None) -> str:
    """Unter welchem Namen gesichert wird — mit Zeitstempel, wenn er gewünscht ist.

    Leer, wenn kein Name eingegeben ist. Der Zeitstempel ist UTC und steht in
    derselben Form wie in der Kennung eines Laufs.
    """

    grund = (name or "").strip()
    if not grund:
        return ""
    if zeitstempel:
        return f"{grund}_{(jetzt or datetime.now(UTC)):%Y%m%dT%H%M%SZ}"
    return grund


def pruefen(name: str | None, *, zeitstempel: bool) -> tuple[Any, bool]:
    """Was der Dialog vor dem Sichern sagt — und ob «Sichern» gesperrt ist."""

    ziel = dateiname(name, zeitstempel=zeitstempel)
    if not ziel:
        return ui.hinweis("Ohne Namen lässt sich nichts sichern.", "info"), True
    pfad = sweep_ziel(ziel)
    if pfad.exists():
        return (
            ui.hinweis(
                f"Ein Szenario «{pfad.stem}» gibt es schon. «Sichern» ersetzt es.", "warnung"
            ),
            False,
        )
    return None, False


def dialog() -> html.Dialog:
    """Der Dialog. **Name und Option stehen außerhalb des Formulars**, die Knöpfe darin.

    Sonst schlösse die Eingabetaste im Namensfeld den Dialog ohne Absicht —
    dieselbe Anordnung wie beim Lauf-Browser. «Abbrechen» steht vor «Sichern»:
    Wer den Dialog versehentlich öffnet, trifft zuerst den harmlosen Knopf.
    """

    return html.Dialog(
        [
            html.H3("Als Szenario sichern", className=ui.H3),
            ui.satz(
                "Legt die Einstellungen als Szenario ab. Danach steht es im ersten Schritt "
                "des Einrichtens zur Auswahl.",
                class_name=f"font-body {ui.TEXT} af-text-body mt-2",
            ),
            ui.field(
                "Name",
                dcc.Input(id=NAME, type="text", value="", autoComplete="off", className="af-input"),
                class_name="mt-4",
            ),
            html.Div(
                ui.checkbox(
                    "Mit Zeitstempel im Namen sichern",
                    value=False,
                    hint="So ersetzt der Stand kein Szenario, das es unter dem Namen schon gibt.",
                    id=ZEITSTEMPEL,
                ),
                className="mt-4",
            ),
            html.Div(id=WARNUNG, className="mt-4", **{"aria-live": "polite"}),
            html.Form(
                html.Div(
                    [
                        ui.button("Abbrechen", variant="ghost", type="submit"),
                        ui.button(
                            "Sichern",
                            variant="secondary",
                            icon_name="save",
                            id=BESTAETIGEN,
                            type="submit",
                        ),
                    ],
                    className="flex justify-end gap-3 mt-6 flex-wrap",
                ),
                method="dialog",
            ),
        ],
        id=DIALOG,
        className="af-rueckfrage",
        **{"aria-label": "Als Szenario sichern"},
    )


def register_callbacks(app) -> None:
    # Öffnen im Browser, mit `showModal()` — wie Rückfrage und Lauf-Browser.
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
        Input(shell.ACTION_SAVE, "n_clicks"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output(NAME, "value"),
        Input(shell.ACTION_SAVE, "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _vorschlagen(_geoeffnet, data: dict | None):
        """Beim Öffnen steht der Vorschlag im Feld — eine Handlung, kein Rückfall.

        Das Feld gehört nicht zum Entwurf: Was hier steht, landet nicht im Store,
        Regel 2 ist also nicht berührt.
        """

        return vorschlag(data or {})

    @app.callback(
        Output(WARNUNG, "children"),
        Output(BESTAETIGEN, "disabled"),
        Input(NAME, "value"),
        Input(ZEITSTEMPEL, "value"),
    )
    def _pruefen(name: str | None, zeitstempel: list | None):
        return pruefen(name, zeitstempel=bool(zeitstempel))

    @app.callback(
        Output("cfg-status", "children", allow_duplicate=True),
        Input(BESTAETIGEN, "n_clicks"),
        State(NAME, "value"),
        State(ZEITSTEMPEL, "value"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _sichern(geklickt, name: str | None, zeitstempel: list | None, data: dict | None):
        if not geklickt:
            return no_update
        ziel = dateiname(name, zeitstempel=bool(zeitstempel))
        if not ziel:
            return ui.hinweis("Ohne Namen wurde nichts gesichert.", "fehler")
        try:
            pfad = save_custom_sweep_preset(draft_from_dict(data or {}), ziel)
        except Exception as exc:  # noqa: BLE001 - Dateifehler gehören in die UI
            return ui.hinweis(f"Konnte nicht gesichert werden: {exc}", "fehler")
        return ui.hinweis(
            f"Als Szenario «{pfad.stem}» gesichert. Es steht jetzt im ersten Schritt zur Auswahl.",
            "erfolg",
        )
