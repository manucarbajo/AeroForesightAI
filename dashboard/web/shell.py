"""Der Rahmen des Leitstands: fünf Zonen, die den Bildschirm füllen.

    ┌──────────────────────────────────────────────────────────┐
    │ Kopfzeile — Name, Zustand, Lauf, globale Aktionen         │
    ├───────────────┬──────────────────────────┬───────────────┤
    │ Parameter     │ Viewport                 │ Telemetrie    │
    │ (der geführte │ (Szene oder eine der     │ (Kennzahlen,  │
    │  Ablauf aus   │  bestehenden Ansichten)  │  Verläufe,    │
    │  P1.1)        │                          │  Konsole)     │
    │               ├──────────────────────────┤               │
    │               │ Zeitleiste               │               │
    └───────────────┴──────────────────────────┴───────────────┘

Bis hierher war das Dashboard eine Dokumentseite: alles untereinander, der
Browser scrollt. Wer einen Parameter änderte und die Wirkung sehen wollte,
scrollte zwischen beidem hin und her. Im Leitstand steht beides nebeneinander,
Kopfzeile und Zeitleiste bleiben stehen, und **jede Zone scrollt für sich** —
das Raster dafür steht in `assets/dashboard.css` unter `.af-shell`.

Was hier **nicht** steht: der Inhalt der Zonen. Die Parameterspalte füllt
`pages.launch`, den Viewport `pages.runs`/`views.scene`, die Telemetrie
`views.telemetry`, die Zeitleiste `timeline`. Dieses Modul kennt nur den
Rahmen und die Kopfzeile.
"""

from __future__ import annotations

from typing import Any

from dash import Input, Output, State, dcc, html

from dashboard.web import components as ui
from dashboard.web import routing, status

#: Bereiche des Dashboards, jeweils relativ zu `routing.BASE_PATH`.
ROUTES = [
    ("", "Leitstand"),
    ("setup", "Einrichten"),
    ("runs", "Ergebnisse"),
    ("doku", "Handbuch"),
]

LANDING_URL = routing.LANDING_PATH

#: Der Umschalter zwischen hell und dunkel. Der Wert steht zusätzlich in
#: `localStorage`, damit die Wahl einen Neustart des Browsers überlebt.
THEME_STORE = "theme-store"
THEME_TOGGLE = "theme-toggle"

#: Die Schubladen für schmale Fenster.
SHELL_ID = "af-shell"
LEFT_TOGGLE = "shell-left-toggle"
RIGHT_TOGGLE = "shell-right-toggle"
SCRIM = "shell-scrim"
DRAWER_STORE = "shell-drawer-store"

STATUS_HOST = "shell-status"
#: Die Bereichslinks. Eigener Wirt, damit das Routing nur sie austauscht und
#: nicht die ganze Kopfzeile samt Auswahlfeld und Zustandsanzeige neu baut.
NAV_HOST = "shell-nav"
RUN_SELECT = "shell-run-select"

#: Globale Aktionen der Kopfzeile. Alle drei gibt es bereits als Funktion — sie
#: standen nur an drei verschiedenen Stellen tief in der Seite.
ACTION_SAVE = "shell-action-save"
ACTION_SNAPSHOT = "shell-action-snapshot"
ACTION_EXPORT = "shell-action-export"


def _nav_link(href: str, label: str, active: bool):
    suffix = " af-nav__link--active" if active else ""
    return dcc.Link(label, href=href, className=f"af-nav__link{suffix}".strip())


def nav_links(active: str) -> list:
    """Die Bereichslinks, mit dem aktiven hervorgehoben."""

    return [_nav_link(routing.url(route), label, route == active) for route, label in ROUTES]


def navbar(active: str) -> html.Div:
    """Der linke Teil der Kopfzeile: Marke und Bereichswechsel."""

    return html.Div(
        [
            ui.icon_button(
                "menu",
                "Parameter ein- oder ausblenden",
                id=LEFT_TOGGLE,
                # Die beiden Umschalter tragen **verschiedene** Modifikatoren,
                # weil ihre Zonen bei verschiedenen Breiten zur Schublade
                # werden — links unter 1024 px, rechts unter 1280 px. Mit einer
                # gemeinsamen Klasse stand der linke Knopf schon ab 1280 px da,
                # während die Spalte noch Rasterspalte war: Der Klick bewegte
                # nichts und hinterließ eine offene Schublade für später.
                className="af-drawer-toggle af-drawer-toggle--left",
            ),
            html.A(
                "AeroForesight AI",
                href=LANDING_URL,
                className="font-headline text-base font-bold af-text-accent tracking-tight "
                "whitespace-nowrap",
            ),
            html.Nav(
                nav_links(active),
                id=NAV_HOST,
                className="af-nav__links flex items-center gap-1 ml-2",
            ),
        ],
        className="flex items-center gap-2 min-w-0",
    )


def theme_toggle() -> html.Button:
    """Hell/dunkel. Ein Knopf, kein Auswahlfeld — es sind genau zwei Zustände.

    Beide Symbole stehen im DOM, sichtbar ist per CSS immer nur das passende.
    Der Grund: Das Umschalten läuft im Browser, ohne Serverrunde — der Server
    weiß also gar nicht, welches Symbol gerade richtig wäre, und ein Callback
    dafür würde den Knopf nur träge machen.
    """

    return html.Button(
        [
            ui.icon("dark_mode", "text-lg af-theme-toggle__to-dark"),
            ui.icon("light_mode", "text-lg af-theme-toggle__to-light"),
        ],
        id=THEME_TOGGLE,
        className="af-icon-btn af-theme-toggle",
        title="Zwischen hellem und dunklem Design wechseln",
        n_clicks=0,
        **{"aria-label": "Zwischen hellem und dunklem Design wechseln"},
    )


def actions() -> html.Div:
    """Speichern, Snapshot, Exportieren — die drei Aktionen der Kopfzeile.

    «Speichern» sichert die Einstellungen als Szenario-Preset unter
    `configs/sweeps/`, «Snapshot» legt dieselben Werte unter einem Namen mit
    Zeitstempel ab, damit ein Zwischenstand den benannten Entwurf nicht
    überschreibt, und «Exportieren» führt in die Dateiablage des gewählten
    Laufs.
    """

    return html.Div(
        [
            ui.icon_button("save", "Einstellungen als Szenario sichern", id=ACTION_SAVE),
            ui.icon_button("photo_camera", "Snapshot des Entwurfs anlegen", id=ACTION_SNAPSHOT),
            ui.icon_button("download", "Dateien dieses Laufs ansehen", id=ACTION_EXPORT),
        ],
        className="flex items-center gap-1",
    )


def status_view(state: status.Status) -> html.Div:
    return ui.status_indicator(state.tone, state.label, hint=state.detail)


def header(
    active: str,
    *,
    state: status.Status,
    run_options: list[dict],
    run_value: str | None,
) -> html.Header:
    return html.Header(
        [
            navbar(active),
            html.Div(
                [
                    html.Div(status_view(state), id=STATUS_HOST),
                    dcc.Dropdown(
                        id=RUN_SELECT,
                        options=run_options,
                        value=run_value,
                        clearable=False,
                        placeholder="Kein Lauf vorhanden",
                        className="af-dropdown w-64 hidden lg:block",
                    ),
                    actions(),
                    theme_toggle(),
                    ui.icon_button(
                        "insights",
                        "Telemetrie ein- oder ausblenden",
                        id=RIGHT_TOGGLE,
                        className="af-drawer-toggle af-drawer-toggle--right",
                    ),
                ],
                className="flex items-center gap-2 shrink-0",
            ),
        ],
        className="af-shell__header",
    )


def layout(
    *,
    active: str,
    state: status.Status,
    run_options: list[dict],
    run_value: str | None,
    left: Any,
    main: Any,
    timeline: Any,
    right: Any,
) -> html.Div:
    """Die fünf Zonen zusammensetzen."""

    return html.Div(
        [
            header(active, state=state, run_options=run_options, run_value=run_value),
            html.Aside(left, className="af-shell__left", id="shell-left"),
            html.Main(main, className="af-shell__main", id="shell-main"),
            html.Div(timeline, className="af-shell__timeline", id="shell-timeline"),
            html.Aside(right, className="af-shell__right", id="shell-right"),
            # Der Verdunkler liegt über dem Inhalt, sobald eine Schublade offen
            # ist. Ein Klick schließt sie — auf schmalen Geräten die einzige
            # Geste, die ohne Zielen funktioniert.
            html.Div(id=SCRIM, className="af-shell__scrim", n_clicks=0),
        ],
        className="af-shell",
        id=SHELL_ID,
    )


def register_callbacks(app) -> None:
    """Theme-Umschalter und Schubladen — beides ohne Serverrunde.

    Als `clientside_callback`, weil beides reine Darstellung ist: Der Server
    hat dazu nichts beizutragen, und ein Rundlauf würde den Umschalter träge
    machen. Der Serverzustand (`theme-store`) läuft trotzdem mit, weil die
    Plotly-Figuren serverseitig entstehen und den Modus brauchen.
    """

    app.clientside_callback(
        """
        function(n_clicks, current) {
            var next = current === 'dark' ? 'light' : 'dark';
            if (!n_clicks) { next = current || 'light'; }
            document.documentElement.classList.toggle('dark', next === 'dark');
            try { window.localStorage.setItem('af-theme', next); } catch (e) {}
            return next;
        }
        """,
        Output(THEME_STORE, "data"),
        Input(THEME_TOGGLE, "n_clicks"),
        State(THEME_STORE, "data"),
    )

    app.clientside_callback(
        """
        function(left, right, scrim) {
            var shell = document.getElementById('af-shell');
            if (!shell) { return window.dash_clientside.no_update; }
            var context = window.dash_clientside.callback_context;
            var trigger = (context.triggered[0] || {}).prop_id || '';
            if (trigger.indexOf('shell-left-toggle') === 0) {
                shell.classList.remove('af-shell--right-open');
                shell.classList.toggle('af-shell--left-open');
            } else if (trigger.indexOf('shell-right-toggle') === 0) {
                shell.classList.remove('af-shell--left-open');
                shell.classList.toggle('af-shell--right-open');
            } else {
                shell.classList.remove('af-shell--left-open');
                shell.classList.remove('af-shell--right-open');
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output(DRAWER_STORE, "data"),
        Input(LEFT_TOGGLE, "n_clicks"),
        Input(RIGHT_TOGGLE, "n_clicks"),
        Input(SCRIM, "n_clicks"),
        prevent_initial_call=True,
    )
