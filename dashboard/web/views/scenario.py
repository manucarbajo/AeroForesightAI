"""Tab «Szenario» — die Hauptansicht nach einem Lauf.

Zeigt das aus dem Lauf abgeleitete Szenario-Tripleset: Lauf-Narrativ, die
einzelnen Szenarien mit ihren Tick-Anhaltspunkten und die Python-Kennzahlen,
auf denen sie fußen. Der Knopf «Szenarien neu erzeugen» ruft denselben
Generator wie die Pipeline (`regenerate_run_scenario`).
"""

from __future__ import annotations

from pathlib import Path

from dash import Input, Output, State, dcc, html, no_update

from dashboard.run_browser import load_run_scenario, read_run_file, regenerate_run_scenario
from dashboard.web import components as ui
from dashboard.web import theme


def _scenario_items(scenario: dict) -> list:
    narrative = scenario.get("narrative") if isinstance(scenario.get("narrative"), dict) else {}
    scenarios = scenario.get("scenarios") or narrative.get("scenarios") or []
    items: list = []
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        rank = item.get("rank", "?")
        try:
            expanded = int(rank) == 1
        except (TypeError, ValueError):
            expanded = False
        items.append(
            ui.accordion(
                f"{rank}. {item.get('title', 'Szenario')}",
                html.P(
                    "Anhaltspunkte aus dem Lauf (Ticks)",
                    className=f"font-body {ui.KLEIN} font-semibold tracking-wide af-text-muted uppercase mb-1",
                ),
                ui.markdown(str(item.get("tick_grounding", ""))),
                ui.divider("my-4"),
                html.P(
                    "Szenario-Beschreibung",
                    className=f"font-body {ui.KLEIN} font-semibold tracking-wide af-text-muted uppercase mb-1",
                ),
                ui.markdown(str(item.get("story") or item.get("what_could_happen", ""))),
                open=expanded,
            )
        )
    return items


def body(run_dir: Path, run_id: str) -> html.Div:
    scenario = load_run_scenario(run_dir)
    md_path = run_dir / "run_scenario.md"
    children: list = []

    if scenario:
        title = scenario.get("title")
        summary = scenario.get("summary")
        if title:
            html_title = html.H3(str(title), className=f"{ui.H2} mb-2")
            children.append(html_title)
        if summary:
            children.append(ui.markdown(str(summary), class_name="mb-6"))

        narrative = scenario.get("narrative") if isinstance(scenario.get("narrative"), dict) else {}
        run_story = (
            scenario.get("run_narrative")
            or narrative.get("run_narrative")
            or scenario.get("observed_run")
        )
        if run_story:
            children.append(
                ui.card(
                    html.P(
                        "Lauf-Narrativ — was im Lauf passiert ist",
                        className=f"font-body {ui.KLEIN} font-semibold tracking-wide af-text-muted uppercase mb-2",
                    ),
                    ui.markdown(str(run_story)),
                    class_name="mb-6",
                )
            )

        items = _scenario_items(scenario)
        if items:
            children.append(html.H3("Szenarien", className=f"{ui.H2} mb-3"))
            children.extend(items)

        source = scenario.get("source")
        if source:
            children.append(
                html.P(["Quelle: ", html.Code(str(source))], className=f"{ui.CAPTION} mt-4")
            )

        warnings = scenario.get("grounding_warnings") or []
        if warnings:
            children.append(
                ui.alert(
                    "Grounding-Hinweise: " + "; ".join(str(item) for item in warnings[:5]),
                    "warning",
                    class_name="mt-4",
                )
            )

        ground_truth = scenario.get("ground_truth")
        if isinstance(ground_truth, dict) and ground_truth:
            children.append(
                ui.accordion(
                    "Ground Truth (Python-Kennzahlen)",
                    ui.json_view(ground_truth),
                    open=False,
                )
            )

    if md_path.is_file() and not scenario:
        children.append(ui.markdown(read_run_file(md_path)))
    elif md_path.is_file():
        children.append(
            ui.accordion(
                "Vollständiges Markdown (run_scenario.md)",
                ui.markdown(read_run_file(md_path)),
                open=False,
            )
        )
    elif not scenario:
        children.append(
            ui.alert(
                "`run_scenario.md` fehlt in diesem Run. Starten Sie eine neue Simulation "
                "oder klicken Sie auf «Szenarien neu erzeugen».",
                "warning",
            )
        )

    return html.Div(children)


def render(run_dir: Path, run_id: str, *, mode: str = theme.LIGHT) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Szenarien aus dem Lauf: Tick-Anhaltspunkte und sachliche Beschreibung.",
                        className=ui.CAPTION,
                    ),
                    ui.button(
                        "Szenarien neu erzeugen",
                        id="scenario-regenerate-btn",
                        variant="secondary",
                        icon_name="refresh",
                    ),
                ],
                className="flex items-center justify-between gap-4 flex-wrap mb-4",
            ),
            html.Div(id="scenario-status"),
            dcc.Loading(
                html.Div(body(run_dir, run_id), id="scenario-body"),
                type="dot",
                color=theme.palette(mode)["accent"],
            ),
        ]
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("scenario-body", "children"),
        Output("scenario-status", "children"),
        Input("scenario-regenerate-btn", "n_clicks"),
        State("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _regenerate(n_clicks: int | None, selected: dict | None):
        if not n_clicks or not selected:
            return no_update, no_update
        run_id = selected["run_id"]
        run_dir = Path(selected["run_dir"])
        try:
            regenerate_run_scenario(run_id, run_dir=run_dir, mock_llm=True, deterministic_only=True)
        except Exception as exc:  # noqa: BLE001 - Fehler gehört in die UI, nicht in die Konsole
            return no_update, ui.alert(f"Szenario-Erzeugung fehlgeschlagen: {exc}", "error")
        return body(run_dir, run_id), ui.alert("Szenarien aktualisiert.", "success")
