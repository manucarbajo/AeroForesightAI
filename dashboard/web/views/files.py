"""Tab «Dateien»: Rohdaten-Browser über alle Artefakte eines Runs.

Jede Datei wird nach ihrem Typ dargestellt — JSON eingerückt, CSV als
sortier- und filterbare Tabelle, Markdown gerendert, PNG als Bild. Das ist
mehr als die Streamlit-Variante konnte (dort war CSV reiner Text), kostet aber
nichts, weil `dash_table` mitgeliefert wird.
"""

from __future__ import annotations

import json
from pathlib import Path

from dash import Input, Output, State, dash_table, html, no_update

from dashboard.run_browser import list_run_files, read_run_file
from dashboard.web import components as ui
from dashboard.web import theme
from dashboard.web.files_route import run_file_url

#: Obergrenze für die Tabellenvorschau. Population-History-Dateien haben
#: schnell sechsstellige Zeilenzahlen — die will kein Browser rendern.
MAX_TABLE_ROWS = 2000

#: Ab dieser Größe wird der Inhalt erst auf Klick aufgebaut. Checkpoint-JSONs
#: sind schnell dreiviertel Megabyte groß; die ungefragt in den DOM zu legen
#: lässt den Tab-Wechsel spürbar hängen.
LAZY_THRESHOLD_BYTES = 256 * 1024


def _table(path: Path, mode: str = theme.LIGHT) -> html.Div:
    tone = theme.palette(mode)
    import pandas as pd

    try:
        frame = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 - kaputte CSV soll lesbar bleiben
        return html.Div(
            [
                ui.alert(f"CSV konnte nicht gelesen werden: {exc}", "warning", class_name="mb-3"),
                ui.code_block(read_run_file(path, max_chars=120_000)),
            ]
        )

    total = len(frame)
    preview = frame.head(MAX_TABLE_ROWS)
    children: list = [
        dash_table.DataTable(
            data=preview.to_dict("records"),
            columns=[{"name": str(c), "id": str(c)} for c in preview.columns],
            page_size=25,
            sort_action="native",
            filter_action="native",
            style_as_list_view=True,
            style_table={"overflowX": "auto"},
            style_cell={
                "fontFamily": theme.FONT_BODY,
                "fontSize": f"{theme.SCHRIFT_PX['beschriftung']}px",
                "padding": "8px 12px",
                "color": tone["text-body"],
                "border": "none",
                "borderBottom": f"1px solid {tone['border-subtle']}",
                "textAlign": "left",
                "maxWidth": "260px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
            style_header={
                "fontFamily": theme.FONT_HEADLINE,
                "fontWeight": "600",
                "fontSize": f"{theme.SCHRIFT_PX['klein']}px",
                "color": tone["text"],
                "backgroundColor": tone["surface-inset"],
                "borderBottom": f"1px solid {tone['border']}",
            },
            style_filter={"backgroundColor": tone["surface-inset"]},
        )
    ]
    if total > MAX_TABLE_ROWS:
        children.append(
            html.P(
                f"Vorschau der ersten {MAX_TABLE_ROWS:,} von {total:,} Zeilen.".replace(",", "."),
                className=f"{ui.CAPTION} mt-3",
            )
        )
    return html.Div(children, className="af-table")


def _content(path: Path, kind: str, mode: str = theme.LIGHT) -> html.Div:
    if kind == "json":
        try:
            return ui.json_view(json.loads(path.read_text(encoding="utf-8")), max_height="40rem")
        except (json.JSONDecodeError, OSError):
            return ui.code_block(read_run_file(path), max_height="40rem")
    if kind == "csv":
        return _table(path, mode)
    if kind == "md":
        return ui.markdown(read_run_file(path))
    if kind == "png":
        url = run_file_url(path)
        if not url:
            return ui.alert("Datei liegt außerhalb des Outputs-Verzeichnisses.", "warning")
        return html.Div(html.Img(src=url, className="w-full rounded"), className="af-paper")
    return ui.code_block(read_run_file(path), max_height="40rem")


def _options(run_dir: Path) -> list[dict]:
    return [
        {
            "label": f"{entry.relative_path}  ({entry.size_bytes // 1024} KB)",
            "value": entry.relative_path,
        }
        for entry in list_run_files(run_dir)
    ]


def _download_link(path: Path):
    url = run_file_url(path, download=True)
    if not url:
        return None
    return html.A(
        [ui.icon("download", "text-sm"), "Herunterladen"],
        href=url,
        className="af-btn af-btn--secondary inline-flex items-center gap-2 px-4 py-2 "
        f"font-body {ui.BESCHRIFTUNG} font-medium",
    )


def _view(run_dir: Path, relative_path: str, mode: str = theme.LIGHT):
    """Inhalt und Download-Link für eine Datei — im Layout wie im Callback."""

    entry = next(
        (item for item in list_run_files(run_dir) if item.relative_path == relative_path),
        None,
    )
    if entry is None:
        return ui.alert("Datei nicht mehr vorhanden.", "warning"), None
    # **Der Pfad im Lauf, nicht der auf der Platte** (P7.0-U0.6): Hier stand
    # `entry.absolute_path`, also etwas wie
    # «F:\AeroForesight\AeroForesightAI\outputs\run_…\cib_matrix.json». Brauchbar
    # daran ist genau der hintere Teil — welche Datei des Laufs man ansieht; der
    # vordere beschreibt die Maschine, auf der der Server läuft, und gehört im
    # Mehrbenutzerbetrieb niemandem außer ihr. Der Download-Link unten benutzt
    # weiterhin den absoluten Pfad, nur zeigt er ihn nicht.
    header = html.P(entry.relative_path, className=f"{ui.CAPTION} mb-3 break-all")

    if entry.kind != "png" and entry.size_bytes > LAZY_THRESHOLD_BYTES:
        # Nicht bloß ausblenden — gar nicht erst übertragen. Ein geschlossenes
        # <details> läge trotzdem vollständig im DOM.
        content = html.Div(
            [
                ui.alert(
                    f"Große Datei ({entry.size_bytes // 1024} KB). Der Inhalt wird erst "
                    "auf Klick geladen.",
                    "info",
                    class_name="mb-3",
                ),
                ui.button(
                    "Inhalt laden",
                    id="files-lazy-load",
                    variant="secondary",
                    icon_name="visibility",
                ),
                html.Div(id="files-lazy-content", className="mt-4"),
            ]
        )
    else:
        content = _content(entry.absolute_path, entry.kind, mode)

    return html.Div([header, content]), _download_link(entry.absolute_path)


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    from dash import dcc

    options = _options(run_dir)
    if not options:
        return ui.alert("Keine Dateien gefunden.", "warning")

    first = options[0]["value"]
    content, download = _view(run_dir, first, mode)
    return html.Div(
        [
            html.Div(
                [
                    ui.field(
                        "Datei",
                        dcc.Dropdown(
                            id="files-select",
                            options=options,
                            value=first,
                            clearable=False,
                            className="af-dropdown",
                        ),
                        class_name="flex-1 min-w-[18rem]",
                    ),
                    html.Div(download, id="files-download", className="af-neben-feld"),
                ],
                className="flex items-start gap-4 flex-wrap mb-4",
            ),
            html.Div(content, id="files-content"),
        ]
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("files-content", "children"),
        Output("files-download", "children"),
        Input("files-select", "value"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _show_file(relative_path: str | None, selected: dict | None):
        if not relative_path or not selected:
            return no_update, no_update
        return _view(Path(selected["run_dir"]), relative_path)

    @app.callback(
        Output("files-lazy-content", "children"),
        Input("files-lazy-load", "n_clicks"),
        State("files-select", "value"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _load_large_file(n_clicks: int | None, relative_path: str | None, selected: dict | None):
        if not n_clicks or not relative_path or not selected:
            return no_update
        run_dir = Path(selected["run_dir"])
        entry = next(
            (item for item in list_run_files(run_dir) if item.relative_path == relative_path),
            None,
        )
        if entry is None:
            return ui.alert("Datei nicht mehr vorhanden.", "warning")
        return _content(entry.absolute_path, entry.kind)
