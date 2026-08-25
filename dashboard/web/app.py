"""Einstiegspunkt der Dash-Oberfläche: Seitenrahmen, Routing, Stores.

Start:

    python -m dashboard.web.app --port 8511

Die Seite besteht aus zwei Bereichen — «Simulation starten» und «Ergebnisse
ansehen» —, zwischen denen ``dcc.Location`` umschaltet. Beide Bereiche liegen
dauerhaft im Layout und werden nur ein- und ausgeblendet: so existiert jede
Komponente, auf die ein Callback zeigt, von Anfang an, der Wechsel ist ohne
Nachladen sofort sichtbar, und der Browser meldet keine fehlenden Inputs.

Der Rahmen (Navigation, Fußzeile, Typografie) ist derselbe wie auf der
Landingpage.
"""

from __future__ import annotations

import argparse

from dash import Dash, Input, Output, dcc, html

from dashboard.run_browser import outputs_root
from dashboard.web import components as ui
from dashboard.web import files_route, landing_route, routing, state, theme
from dashboard.web.pages import docs as docs_page
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import runs as runs_page

TITLE = "Technology Lab · Simulation"
SUBTITLE = "Prototypische Workbench für Szenarioplanung im Flugverkehr"

#: Die Landingpage liegt in derselben Anwendung auf `/` — deshalb ein
#: relativer Pfad, der in jeder Umgebung stimmt.
LANDING_URL = routing.LANDING_PATH

#: Bereiche des Dashboards, jeweils relativ zu `routing.BASE_PATH`.
ROUTES = [
    ("", "Simulation starten"),
    ("runs", "Ergebnisse ansehen"),
    ("doku", "Dokumentation"),
]

_HIDDEN = {"display": "none"}
_VISIBLE = {"display": "block"}

_INDEX = """<!DOCTYPE html>
<html class="light" lang="de">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap">
        <script>
            // Identisch zur Landingpage, damit beide Seiten dieselben Tokens teilen.
            tailwind.config = {
                darkMode: "class",
                theme: {
                    extend: {
                        colors: {
                            navy: {
                                50: '#f0f4f9', 100: '#e0eaf3', 200: '#c2d5e7',
                                300: '#94b8d7', 400: '#6094c1', 500: '#3e76a6',
                                600: '#2d5e8a', 700: '#244b70', 800: '#1E3A5F',
                                900: '#1c3453', 950: '#122238'
                            }
                        },
                        borderRadius: {
                            "DEFAULT": "0.5rem", "lg": "0.75rem",
                            "xl": "1rem", "full": "9999px"
                        },
                        fontFamily: {
                            "headline": ["Plus Jakarta Sans", "sans-serif"],
                            "display": ["Plus Jakarta Sans", "sans-serif"],
                            "body": ["Inter", "sans-serif"],
                            "label": ["Inter", "sans-serif"]
                        }
                    }
                }
            }
        </script>
        {%css%}
    </head>
    <body class="bg-slate-50 text-slate-800 font-body antialiased selection:bg-navy-200 selection:text-navy-900">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


def _nav_link(href: str, label: str, active: bool) -> html.A:
    base = "font-body text-sm font-medium px-3 py-2 border-b-2 transition-colors duration-200"
    tone = (
        "text-navy-800 border-navy-800"
        if active
        else "text-slate-600 border-transparent hover:text-navy-800"
    )
    return dcc.Link(label, href=href, className=f"{base} {tone}")


def _navbar(active: str) -> html.Nav:
    return html.Nav(
        html.Div(
            [
                html.Div(
                    [
                        html.A(
                            "AeroForesight AI",
                            href=LANDING_URL,
                            className="text-lg font-headline font-bold text-navy-800 tracking-tight",
                        ),
                        html.Span(
                            "Simulation",
                            className="font-body text-xs text-slate-500 border-l border-slate-200 pl-3 ml-1 hidden sm:inline",
                        ),
                    ],
                    className="flex items-center gap-3",
                ),
                html.Div(
                    [
                        _nav_link(routing.url(route), label, route == active)
                        for route, label in ROUTES
                    ],
                    className="af-nav__links flex items-center gap-1",
                ),
            ],
            className="max-w-[1400px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4",
        ),
        className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200",
    )


def _footer() -> html.Footer:
    return html.Footer(
        html.Div(
            [
                html.Span(SUBTITLE, className=ui.CAPTION),
                html.Div(
                    [
                        html.Span(id="footer-last-run", className=ui.CAPTION),
                        html.Span(
                            [
                                "Outputs: ",
                                html.Code(str(outputs_root()), className="text-slate-600"),
                            ],
                            className=ui.CAPTION,
                        ),
                    ],
                    className="flex flex-wrap items-center gap-4",
                ),
            ],
            className="max-w-[1400px] mx-auto px-4 sm:px-6 py-5 flex flex-wrap items-center justify-between gap-3",
        ),
        className="border-t border-slate-200 bg-white mt-12",
    )


def serve_layout() -> html.Div:
    """Layout pro Browser-Sitzung neu aufbauen.

    Als Funktion statt als fertiges Objekt, damit jede Sitzung die aktuelle
    Run-Liste und die aktuellen Config-Dateien sieht — sonst würde der Stand
    vom Serverstart eingefroren.
    """

    selection = runs_page.default_selection()
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id=state.STORE_ID, storage_type="session", data=state.initial_draft_dict()),
            dcc.Store(id="selected-run-store", data=selection),
            dcc.Store(id="last-launched-run-store", storage_type="session"),
            dcc.Store(id="explorer-messages-store", storage_type="session", data={}),
            html.Div(id="navbar-host"),
            html.Main(
                [
                    html.Div(launch_page.layout(state.initial_draft_dict()), id="page-launch"),
                    html.Div(runs_page.layout(selection), id="page-runs", style=_HIDDEN),
                    html.Div(docs_page.layout(), id="page-docs", style=_HIDDEN),
                ],
                className="max-w-[1400px] mx-auto px-4 sm:px-6 py-8 min-h-[70vh]",
            ),
            _footer(),
        ]
    )


def create_app() -> Dash:
    theme.register_template()

    app = Dash(
        __name__,
        title=TITLE,
        update_title=None,
        suppress_callback_exceptions=True,
        index_string=_INDEX,
        # Das Dashboard liegt unter `/app/`, damit `/` der Landingpage gehört.
        url_base_pathname=routing.BASE_PATH,
    )
    files_route.register(app.server)
    landing_route.register(app.server)
    app.layout = serve_layout

    @app.callback(
        Output("navbar-host", "children"),
        Output("page-launch", "style"),
        Output("page-runs", "style"),
        Output("page-docs", "style"),
        Input("url", "pathname"),
    )
    def _route(pathname: str | None):
        relative = routing.relative(pathname)
        # Das Handbuch hat Unterseiten (`doku/cib`) — hier zählt der Anfang.
        if relative.startswith("doku"):
            active = "doku"
        else:
            active = relative if relative in {route for route, _ in ROUTES} else ""
        return (
            _navbar(active),
            _VISIBLE if active == "" else _HIDDEN,
            _VISIBLE if active == "runs" else _HIDDEN,
            _VISIBLE if active == "doku" else _HIDDEN,
        )

    @app.callback(
        Output("footer-last-run", "children"),
        Input("last-launched-run-store", "data"),
    )
    def _last_run(run_id: str | None):
        if not run_id:
            return None
        return ["Zuletzt: ", html.Code(str(run_id), className="text-slate-600")]

    launch_page.register_callbacks(app)
    runs_page.register_callbacks(app)
    docs_page.register_callbacks(app)
    return app


app = create_app()
server = app.server


def main() -> None:
    parser = argparse.ArgumentParser(description="AeroForesight AI — Simulations-Dashboard")
    parser.add_argument("--port", type=int, default=8511)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
