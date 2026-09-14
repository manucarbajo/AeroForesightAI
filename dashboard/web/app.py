"""Einstiegspunkt der Dash-Oberfläche: der Leitstand-Rahmen, Routing, Stores.

Start:

    python -m dashboard.web.app --port 8511

Die Anwendung ist **ein** Bildschirm, kein Stapel Seiten: links die Parameter,
in der Mitte der Viewport, rechts die Telemetrie, unten die Zeitleiste, oben die
Kopfzeile. Der Bereichswechsel (`Einrichten` / `Leitstand` / `Ergebnisse` /
`Modell` / `Handbuch`) tauscht nur den Inhalt des Viewports — die anderen vier
Zonen bleiben stehen — **aber nur im Leitstand**: Jeder andere Bereich bekommt
den Bildschirm allein (`shell.FOCUS_ROUTES`, seit P7.3-U3.1). Dazu kommt die
**Musterseite** unter `/app/muster`, ein
Bereich ohne Link (`shell.INTERNE_ROUTES`, P7.1-U1.6).
Das Raster steht in `assets/dashboard.css`, der Aufbau in `shell.py`.

Alle sechs Viewport-Bereiche liegen dauerhaft im Layout und werden nur ein- und
ausgeblendet: So existiert jede Komponente, auf die ein Callback zeigt, von
Anfang an, der Wechsel ist ohne Nachladen sofort sichtbar, und der Browser
meldet keine fehlenden Inputs. **Eine Ausnahme seit P3.12:** Der Rumpf des
Modell-Bereichs entsteht erst beim Aufsuchen — er trägt keine feste ID; sein
Wirt liegt trotzdem von Anfang an da. Die Musterseite folgt demselben Muster.

**Zum Theme:** Die Klasse `dark` muss auf `<html>` stehen, **bevor** der Browser
zum ersten Mal zeichnet — sonst blitzt bei jedem Laden das helle Design auf. Ein
Dash-Callback kommt dafür zu spät; deshalb steht ein kurzes Skript im `<head>`,
das `localStorage` liest. Der Wert läuft zusätzlich in `theme-store`, weil die
Plotly-Figuren serverseitig entstehen und ihr Template kennen müssen.
"""

from __future__ import annotations

import argparse

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from dashboard.config_catalog import save_custom_sweep_preset
from dashboard.web import components as ui
from dashboard.web import (
    files_route,
    landing_route,
    routing,
    run_data,
    runner,
    shell,
    state,
    status,
    theme,
    timeline,
)
from dashboard.web.config_editor import wizard
from dashboard.web.pages import docs as docs_page
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import model_editor as model_page
from dashboard.web.pages import muster as muster_page
from dashboard.web.pages import runs as runs_page
from dashboard.web.pages import setup as setup_page

# `active_route` steht seit P3.12 in `shell` (dort stehen `ROUTES` und
# `ALIASES`). Hier weiterhin unter dem alten Namen erreichbar: mehrere Tests
# und zwei Callbacks in dieser Datei rufen `web_app.active_route`.
from dashboard.web.shell import active_route
from dashboard.web.state import STORE_ID, draft_from_dict
from dashboard.web.views import scene, telemetry
from src.logging_setup import stdio_auf_utf8

#: Der Titel beim ersten Laden. Danach setzt ihn der Bereichswechsel
#: (`shell.seitentitel`); bis zum 2026-09-11 stand hier «Technology Lab ·
#: Leitstand» — auf jedem Bereich und unter einem Namen, den das Produkt sonst
#: nirgends trägt (P7.2-U2.7).
TITLE = shell.MARKE

_HIDDEN = {"display": "none"}


def _bereichstitel(name: str):
    """Eine Überschrift, die den Bereich benennt — für die Tastatur (P1.5).

    **Nicht jeder Bereich hatte eine.** «Leitstand» und «Ergebnisse» begannen
    mit dem Inhalt; gemessen landete der Fokus nach dem Wechsel deshalb auf
    `BODY` oder auf einer beliebigen Zwischenüberschrift («Population im Tick»).
    Wer mit der Tastatur ankommt, soll zuerst hören, **wo** er ist.

    Nur vorgelesen, nicht gezeichnet: Die Bereiche tragen ihren Namen schon in
    der Kopfzeile, und ein zweites Mal danebengeschrieben wäre Doppelung.
    """

    return html.H1(name, className="af-nur-vorlesen", tabIndex=-1)


_VISIBLE: dict = {}

SCENE_HOST = "scene-host"

#: Wo der Inhalt des Leitstands hängt. **Getrennt von `SCENE_HOST`**, weil der
#: Szenen-Callback seine Kinder bei jedem Tick austauscht — die Überschrift des
#: Bereichs lag dort und wurde damit weggeräumt; gemessen landete der Fokus
#: danach auf einer Zwischenüberschrift («Population im Tick») statt auf dem
#: Namen des Bereichs (P1.5).
SCENE_CONTENT = "scene-content"
TELEMETRY_HOST = "telemetry-host"

_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        <script>
            // Laeuft vor dem ersten Zeichnen: Ohne diese Zeilen blitzt bei
            // jedem Laden das helle Design auf, bevor Dash uebernimmt. Fehlt
            // eine gespeicherte Wahl, entscheidet die Systemeinstellung.
            (function () {
                try {
                    var stored = window.localStorage.getItem("af-theme");
                    var dark = stored
                        ? stored === "dark"
                        : window.matchMedia("(prefers-color-scheme: dark)").matches;
                    document.documentElement.classList.toggle("dark", dark);
                } catch (e) {}
            })();
            // Ebenso vor dem ersten Zeichnen: die gezogenen Zonenbreiten
            // (P1.7). Als Dash-Callback kaeme das zu spaet, und die Spalten
            // blitzten bei jedem Laden erst in der Standardbreite auf.
            // Geschrieben werden sie von `assets/shell_resize.js`.
            (function () {
                try {
                    [["af-shell-left", "--shell-left"],
                     ["af-shell-right", "--shell-right"]].forEach(function (paar) {
                        var wert = window.localStorage.getItem(paar[0]);
                        if (wert) {
                            document.documentElement.style.setProperty(paar[1], wert + "px");
                        }
                    });
                } catch (e) {}
            })();
        </script>
        <!-- **Tailwind kommt aus `assets/00-tailwind.css`** (P1.4), erzeugt von
             `npm run build:css`. Bis zum 2026-08-30 stand hier ein CDN-Skript,
             das die Klassen zur Laufzeit erzeugte -- und dabei die IP jedes
             Betrachters an einen fremden Host meldete. Die Zahlen im Dateinamen
             sind keine Zierde: Dash laedt seine Assets alphabetisch, und
             `dashboard.css` muss **nach** Tailwind kommen, sonst gewinnen dessen
             Utilities gegen die af-Tokens. -->
        <!-- Die Schriften kommen aus `assets/01-schriften.css` und
             `assets/fonts/` (P1.4), geholt von `scripts/schriften_holen.py`.
             Bis zum 2026-08-30 stand hier ein Verweis auf `fonts.googleapis.com`
             — jeder Seitenaufruf meldete damit die IP des Betrachters dorthin. -->
        {%css%}
    </head>
    <body class="font-body antialiased">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

#: Die Palette steht seit P1.4 in `tailwind.config.js` und wird beim Build
#: eingesetzt — nicht mehr zur Laufzeit in die Seite geschrieben. Das Template
#: braucht deshalb keinen Platzhalter mehr.
_INDEX = _INDEX_TEMPLATE


# --- Zonen-Inhalte ---------------------------------------------------------


def _progress_from(payload: dict | None) -> runner.Progress | None:
    """Den Fortschritt aus dem Store zurückbauen — oder `None`.

    Der Store trägt eine einfache Zuordnung, weil er durch den Browser läuft;
    die Ansichten wollen das Objekt mit seiner `fraction`-Regel.
    """

    if not payload or not payload.get("job_id"):
        return None
    return runner.Progress(
        job_id=str(payload["job_id"]),
        tick=payload.get("tick"),
        total=payload.get("total"),
        line=str(payload.get("line") or ""),
        lines=tuple(payload.get("lines") or ()),
        cancellable=bool(payload.get("cancellable", True)),
        # Muss mit durch den Browser, sonst fiele die Restzeit genau dort aus,
        # wo sie gezeigt wird — dieselbe Falle wie bei `cancellable`.
        tick_seconds=tuple(float(w) for w in (payload.get("tick_seconds") or ())),
    )


def scene_block(
    data: run_data.RunData,
    tick: int,
    *,
    mode: str = theme.LIGHT,
    zoom: int = 0,
    progress: runner.Progress | None = None,
    draft: dict | None = None,
    running_now: bool = False,
):
    """Der Viewport im Bereich «Leitstand».

    **Rechnet gerade ein Lauf, gehört der Bildschirm ihm** (seit P1.7). Die
    Szene zeigt dann ohnehin den zuletzt gewählten, *anderen* Lauf — sie
    danebenzustellen hieße, zwei Läufe gleichzeitig zu zeigen und keinen davon
    zu benennen.

    Sonst: Demo-Hinweis, dann die Szene. Der Hinweis steht **über** der Szene
    und nicht daneben — wer Zahlen abliest, soll vorher gelesen haben, woher sie
    kommen.
    """

    if progress is not None or running_now:
        from dashboard.web.views import running

        # **Der Bildschirm folgt dem Laufzustand, nicht der ersten Tick-Zeile.**
        # `_start` leert den Fortschritt, und gefüllt wird er erst, wenn die
        # Simulation ihre erste Zeile schreibt — bis dahin vergingen gemessen
        # 1,7 s, in denen die Kopfzeile «Simulation läuft» sagte und die Mitte
        # die Szene des **vorigen** Laufs zeigte. Genau der Widerspruch,
        # gegen den `status.py` angetreten ist.
        #
        # Ohne Zahlen heißt hier ehrlich «unbestimmt»: `Progress.fraction` gibt
        # dann `None` zurück und die Ansicht zeigt einen unbestimmten Balken,
        # keine erfundene Prozentzahl (Invariante 1).
        lauf = progress or runner.Progress(job_id="", tick=None, total=None, line="")
        return running.render(lauf, draft or {})

    children: list = []
    if data.is_demo:
        from dashboard.web import demo_run

        children.append(html.Div(ui.hinweis(demo_run.notice(), "demo"), className="px-4 pt-4"))
    children.append(scene.render(data, tick, mode=mode, zoom_index=zoom))
    return html.Div(children)


def visibility(active: str) -> tuple[dict, ...]:
    """Welcher der sechs Viewport-Bereiche sichtbar ist — genau einer.

    Alle sechs bleiben im DOM (sonst zeigten Callbacks auf Komponenten, die es
    nicht gibt); umgeschaltet wird nur die Sichtbarkeit.

    Die Reihenfolge ist die von `shell.BEREICHE` — erst die Navigation, dann die
    Bereiche ohne Link — und zwar **abgeleitet**, nicht
    abgeschrieben: Seit P1.7 ist diese Reihenfolge der Arbeitsablauf und hat
    sich einmal geändert. Eine zweite handgepflegte Liste hätte an dem Tag
    stillschweigend den falschen Bereich eingeblendet.
    """

    return tuple(_VISIBLE if active == route else _HIDDEN for route, _ in shell.BEREICHE)


def _status_for(data: run_data.RunData, *, running: bool = False) -> status.Status:
    return status.derive(
        running=running,
        demo=data.is_demo,
        degraded=bool(data.metadata.get("degraded")),
        incidents=int(data.metadata.get("llm_incident_count") or 0),
    )


def serve_layout() -> html.Div:
    """Layout pro Browser-Sitzung neu aufbauen.

    Als Funktion statt als fertiges Objekt, damit jede Sitzung die aktuelle
    Run-Liste und die aktuellen Config-Dateien sieht — sonst würde der Stand
    vom Serverstart eingefroren.
    """

    selection = runs_page.default_selection()
    draft = state.initial_draft_dict()
    data = run_data.load(selection)
    options, _ = runs_page.run_options()
    run_value = (selection or {}).get("run_id")
    start = visibility("")

    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id=STORE_ID, storage_type="session", data=draft),
            dcc.Store(id="selected-run-store", data=selection),
            dcc.Store(id="last-launched-run-store", storage_type="session"),
            dcc.Store(id="explorer-messages-store", storage_type="session", data={}),
            dcc.Store(id=shell.THEME_STORE, storage_type="local", data=theme.LIGHT),
            dcc.Store(id=shell.DRAWER_STORE),
            dcc.Store(id=timeline.TICK_STORE, data=1),
            dcc.Store(id=timeline.PLAY_STORE, data=False),
            dcc.Store(id=scene.ZOOM_STORE, data=scene.DEFAULT_ZOOM),
            dcc.Store(id=runs_page.TAB_STORE, data=runs_page.DEFAULT_TAB),
            # Welcher Schritt des Einrichtens offen ist (P1.7). Als Store und
            # nicht als Adresse: Ein halb ausgefuelltes Formular ist kein Ort,
            # den man verlinken oder mit dem Zurueck-Knopf ansteuern will.
            #
            # `ENTRY` und nicht `0`: Jede Sitzung beginnt beim Einstieg mit den
            # drei Wegen, nicht mitten in der Schrittfolge. Der Store wird
            # bewusst **nicht** gespeichert -- er soll nach einem Neuladen genau
            # das zeigen.
            dcc.Store(id=wizard.STEP_STORE, data=wizard.ENTRY),
            dcc.Store(id=wizard.VISITED_STORE, data=[]),
            dcc.Store(id=wizard.HISTORY_STORE, data=[]),
            shell.layout(
                active="",
                # Auch beim ersten Zeichnen gilt der Serverzustand: Ein Lauf,
                # den eine andere Sitzung gestartet hat, ist einer.
                state=_status_for(data, running=runner.is_running()),
                run_options=options,
                run_value=run_value,
                left=launch_page.rail(draft),
                # Die Anfangssichtbarkeiten kommen aus derselben Funktion wie die
                # späteren — sonst zeigte der erste Aufbau einen anderen Bereich
                # als das Routing eine Sekunde danach.
                main=html.Div(
                    [
                        html.Div(setup_page.layout(draft), id="page-setup", style=start[0]),
                        html.Div(
                            [
                                _bereichstitel("Leitstand"),
                                html.Div(
                                    scene_block(
                                        data,
                                        1,
                                        progress=_progress_from(launch_page.progress_payload()),
                                        draft=draft,
                                    ),
                                    id=SCENE_CONTENT,
                                ),
                            ],
                            id=SCENE_HOST,
                            style=start[1],
                        ),
                        html.Div(
                            [_bereichstitel("Ergebnisse"), runs_page.layout(selection)],
                            id="page-runs",
                            style=start[2],
                        ),
                        html.Div(model_page.layout(draft), id="page-modell", style=start[3]),
                        html.Div(docs_page.layout(), id="page-docs", style=start[4]),
                        html.Div(muster_page.layout(), id="page-muster", style=start[5]),
                    ],
                    id="page-scene-wrap",
                ),
                timeline=html.Div(timeline.layout(data, 1), id=timeline.HOST),
                right=html.Div(telemetry.render(data, 1), id=TELEMETRY_HOST),
            ),
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

    # Die Sichtbarkeiten stehen in der Reihenfolge von `shell.BEREICHE`:
    # Einrichten, Leitstand, Ergebnisse, Modell, Handbuch, Musterseite.
    @app.callback(
        Output(shell.NAV_HOST, "children"),
        Output(shell.SHELL_ID, "className"),
        Output("page-setup", "style"),
        Output(SCENE_HOST, "style"),
        Output("page-runs", "style"),
        Output("page-modell", "style"),
        Output("page-docs", "style"),
        Output("page-muster", "style"),
        Output(shell.BEREICH_ANSAGE, "children"),
        Output(shell.SEITENTITEL, "children"),
        Input("url", "pathname"),
    )
    def _route(pathname: str | None):
        active = active_route(pathname)
        return (
            shell.nav_links(active),
            shell.shell_class(active),
            *visibility(active),
            # **Der Wechsel wird angesagt** (P1.5). Ohne das geschieht er
            # lautlos: Der Bildschirm zeigt etwas anderes, und wer nicht
            # hinsieht, erfährt es nicht.
            shell.bereich_ansage(active),
            shell.seitentitel(active),
        )

    @app.callback(Output(muster_page.HOST, "children"), Input("url", "pathname"))
    def _musterseite(pathname: str | None):
        """Die Musterseite bauen, **wenn jemand sie aufsucht** (P7.1-U1.6).

        Aus demselben Grund wie der Modell-Bereich (P3.12): Jede eingehängte
        Komponente kostet jeden Klick in der Schrittfolge etwas, und diese Seite
        sieht fast nie jemand. Ihr Rumpf trägt keine feste Kennung.
        """

        return muster_page.rumpf_fuer(pathname)

    # **Der Fokus wandert auf die Überschrift des neuen Bereichs** (P1.5).
    #
    # Am `af-shell__main` hängend, nicht am Pfad: Der Pfad ändert sich beim
    # Klick, den neuen Inhalt gibt es erst mit der Antwort des Servers. Und
    # über einen `MutationObserver`, nicht über `requestAnimationFrame` — das
    # feuert in einem Tab, den niemand sieht, gar nicht. Beide Fehler standen
    # schon in der Schrittfolge (P1.9-W5.3) und sind dort nachzulesen.
    app.clientside_callback(
        """
        function (pfad) {
            var wirt = document.getElementById("%s");
            if (!wirt) { return window.dash_clientside.no_update; }
            var setzen = function () {
                var aktiv = document.activeElement;
                // **Auch frei, wenn das Fokussierte unsichtbar geworden ist.**
                // Ein Bereichswechsel schaltet die Sichtbarkeiten nacheinander:
                // Fuer einen Augenblick ist die alte Ueberschrift noch da, und
                // wer sie in diesem Moment fokussiert, bleibt fuer immer dort --
                // gemessen: nach «Handbuch» stand der Fokus auf «Modell».
                var frei = !aktiv || aktiv === document.body || !document.contains(aktiv)
                           || aktiv.offsetParent === null;
                if (!frei) { return; }
                // **Die Ueberschrift des *sichtbaren* Bereichs.** Alle fuenf
                // liegen gleichzeitig im DOM -- `querySelector` liefert sonst
                // die erste in Dokumentreihenfolge, und die gehoert womoeglich
                // zu einem ausgeblendeten Bereich. Ein ausgeblendetes Element
                // nimmt keinen Fokus an: Am laufenden System stand er danach
                // auf `BODY`, bei vier von fuenf Wechseln.
                var titel = null;
                var kandidaten = wirt.querySelectorAll("h1, h2");
                for (var k = 0; k < kandidaten.length; k++) {
                    if (kandidaten[k].offsetParent !== null) { titel = kandidaten[k]; break; }
                }
                if (titel) {
                    if (!titel.hasAttribute("tabindex")) { titel.setAttribute("tabindex", "-1"); }
                    titel.focus({ preventScroll: true });
                }
            };
            // **`aria-current` aus der Klasse ableiten.** `dcc.Link` nimmt das
            // Attribut nicht entgegen, und `html.A` laedt die Seite neu.
            var kennzeichnen = function () {
                var links = document.querySelectorAll(".af-nav__link");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].classList.contains("af-nav__link--active")) {
                        links[i].setAttribute("aria-current", "page");
                    } else {
                        links[i].removeAttribute("aria-current");
                    }
                }
            };
            // **Beide Wirte beobachten.** Inhalt und Bereichsliste werden von
            // getrennten Ausgängen desselben Callbacks gezeichnet; wer nur den
            // Inhalt beobachtet, stempelt `aria-current` auf eine Liste, die es
            // im selben Moment noch gar nicht gibt.
            // **Auch auf Attribute hoeren, nicht nur auf Kinder.** Ein
            // Bereichswechsel tauscht hier nichts aus -- er schaltet `style`
            // von `display: none` auf sichtbar. Ein Beobachter, der nur
            // `childList` kennt, feuert dabei nie.
            var achten = { childList: true, subtree: true, attributes: true,
                           attributeFilter: ["style", "class"] };
            var beob = new MutationObserver(function () { setzen(); kennzeichnen(); });
            beob.observe(wirt, achten);
            var nav = document.getElementById("%s");
            if (nav) { beob.observe(nav, achten); }
            window.setTimeout(function () { beob.disconnect(); }, 2500);
            setzen();
            kennzeichnen();
            return window.dash_clientside.no_update;
        }
        """ % (shell.MAIN_ID, shell.NAV_HOST),
        Output(shell.BEREICH_ANSAGE, "title"),
        Input("url", "pathname"),
        prevent_initial_call=True,
    )

    # --- Die Lauf-Auswahl der Kopfzeile ------------------------------------

    @app.callback(
        Output(shell.RUN_SELECT, "options"),
        Output(shell.RUN_SELECT, "value"),
        Input("last-launched-run-store", "data"),
        State(shell.RUN_SELECT, "value"),
    )
    def _refresh_runs(last_launched: str | None, current: str | None):
        """Die Liste nachziehen, sobald ein Lauf fertig geworden ist."""

        options, _ = runs_page.run_options()
        values = [option["value"] for option in options]
        if last_launched in values:
            return options, last_launched
        return options, (current if current in values else (values[0] if values else None))

    @app.callback(
        Output("selected-run-store", "data"),
        Input(shell.RUN_SELECT, "value"),
        prevent_initial_call=True,
    )
    def _select_run(run_id: str | None):
        if not run_id:
            return no_update
        _, by_id = runs_page.run_options()
        summary = by_id.get(run_id)
        if summary is None:
            return no_update
        return {"run_id": run_id, "run_dir": str(summary.run_dir)}

    # --- Die vier Zonen, die dem Lauf und dem Tick folgen -------------------

    @app.callback(
        Output(timeline.HOST, "children"),
        Output(timeline.TICK_STORE, "data"),
        Output(timeline.PLAY_STORE, "data", allow_duplicate=True),
        Input("selected-run-store", "data"),
        prevent_initial_call=True,
    )
    def _rebuild_timeline(selected: dict | None):
        """Beim Wechsel des Laufs: neue Leiste, zurück auf Tick 1, Wiedergabe aus.

        Den Tick stehen zu lassen wäre die bequemere Wahl und die falsche: Tick
        30 in einem Lauf über 16 Ticks gibt es nicht, und ein Regler, der über
        seinem Maximum steht, zeigt stumm etwas anderes an als sein Wert sagt.
        """

        data = run_data.load(selected)
        return timeline.layout(data, 1), 1, False

    @app.callback(
        Output(SCENE_CONTENT, "children"),
        Input(timeline.TICK_STORE, "data"),
        Input(shell.THEME_STORE, "data"),
        Input(scene.ZOOM_STORE, "data"),
        Input("selected-run-store", "data"),
        Input(launch_page.PROGRESS_STORE, "data"),
        Input(launch_page.RUNNING_STORE, "data"),
        State(STORE_ID, "data"),
    )
    def _scene(tick, mode: str | None, zoom, selected: dict | None, progress, laeuft, draft):
        data = run_data.load(selected)
        return scene_block(
            data,
            max(1, int(tick or 1)),
            mode=theme.normalise(mode),
            zoom=int(zoom or 0),
            progress=_progress_from(progress),
            draft=draft or {},
            running_now=bool(laeuft),
        )

    @app.callback(
        Output(TELEMETRY_HOST, "children"),
        Input(timeline.TICK_STORE, "data"),
        Input(shell.THEME_STORE, "data"),
        Input("selected-run-store", "data"),
        Input(launch_page.PROGRESS_STORE, "data"),
    )
    def _telemetry(tick, mode: str | None, selected: dict | None, progress: dict | None):
        data = run_data.load(selected)
        lauf = _progress_from(progress)
        return telemetry.render(
            data,
            max(1, int(tick or 1)),
            mode=theme.normalise(mode),
            progress=list(lauf.lines) if lauf else [],
        )

    @app.callback(
        Output(shell.STATUS_HOST, "children"),
        Input(launch_page.RUNNING_STORE, "data"),
        Input("selected-run-store", "data"),
    )
    def _status(running: bool | None, selected: dict | None):
        data = run_data.load(selected)
        return shell.status_view(_status_for(data, running=bool(running)))

    @app.callback(
        Output(shell.DOCK_HOST, "children"),
        Input(launch_page.PROGRESS_STORE, "data"),
        Input("url", "pathname"),
    )
    def _dock(progress: dict | None, pathname: str | None):
        """Das Fortschrittsfenster — überall **außer** auf dem Leitstand.

        Dort steht der Ladebildschirm, und zwei Fortschrittsbalken auf einem
        Schirm wären zwei Aussagen über dieselbe Sache. Sonst gilt: Wer während
        eines Laufs einen älteren ansehen will, soll das können, ohne den
        laufenden aus den Augen zu verlieren.
        """

        from dashboard.web.views import running

        lauf = _progress_from(progress)
        if lauf is None or active_route(pathname) == running.leitstand_route():
            return None
        return running.dock(lauf)

    @app.callback(
        Output(scene.ZOOM_STORE, "data"),
        Input(scene.ZOOM_IN, "n_clicks"),
        Input(scene.ZOOM_OUT, "n_clicks"),
        State(scene.ZOOM_STORE, "data"),
        prevent_initial_call=True,
    )
    def _zoom(_in, _out, current):
        index = int(current or 0)
        if ctx.triggered_id == scene.ZOOM_IN:
            return min(index + 1, len(scene.ZOOM_STEPS) - 1)
        return max(index - 1, 0)

    # --- Globale Aktionen der Kopfzeile ------------------------------------

    @app.callback(
        Output("cfg-status", "children", allow_duplicate=True),
        Input(shell.ACTION_SAVE, "n_clicks"),
        Input(shell.ACTION_SNAPSHOT, "n_clicks"),
        # Zweiter Ausloeser aus dem letzten Schritt des Einrichtens -- **kein**
        # zweiter Speicherpfad: derselbe Callback, dieselbe Funktion dahinter.
        Input(wizard.SAVE, "n_clicks"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _save(save_clicks, snapshot_clicks, wizard_clicks, data: dict | None):
        """Entwurf als Szenario sichern — benannt oder als Zwischenstand.

        Der Unterschied ist der Name: «Speichern» schreibt unter dem Namen der
        Simulation und überschreibt damit denselben Stand wieder, «Snapshot»
        hängt einen Zeitstempel an. Beide landen in `configs/sweeps/` und stehen
        danach im ersten Schritt des geführten Ablaufs zur Auswahl.
        """

        if not (save_clicks or snapshot_clicks or wizard_clicks):
            return no_update

        draft = draft_from_dict(data or {})
        name = (draft.simulation_name or "mein_szenario").strip() or "mein_szenario"
        if ctx.triggered_id == shell.ACTION_SNAPSHOT:
            from datetime import datetime, timezone

            name = f"{name}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"

        try:
            path = save_custom_sweep_preset(draft, name)
        except Exception as exc:  # noqa: BLE001 - Dateifehler gehören in die UI
            return ui.hinweis(f"Konnte nicht gespeichert werden: {exc}", "fehler")
        return ui.hinweis(f"Gespeichert: `{path}`", "erfolg")

    @app.callback(
        Output("url", "pathname"),
        Output(runs_page.TAB_STORE, "data", allow_duplicate=True),
        Output("runs-viewbar", "children", allow_duplicate=True),
        Input(shell.ACTION_EXPORT, "n_clicks"),
        prevent_initial_call=True,
    )
    def _export(n_clicks):
        """«Exportieren» führt dorthin, wo die Dateien des Laufs liegen.

        Kein eigener Download-Weg: Die Ansicht «Dateien» kann bereits jede Datei
        einzeln herunterladen, und ein zweiter Pfad daneben wäre eine zweite
        Wahrheit darüber, was zu einem Lauf gehört.
        """

        if not n_clicks:
            return no_update, no_update, no_update
        return routing.url("runs"), "files", runs_page.viewbar("files").children

    shell.register_callbacks(app)
    timeline.register_callbacks(app)
    launch_page.register_callbacks(app)
    runs_page.register_callbacks(app)
    docs_page.register_callbacks(app)
    return app


app = create_app()
server = app.server


def main() -> None:
    parser = argparse.ArgumentParser(description="AeroForesight AI — Simulations-Leitstand")
    parser.add_argument("--port", type=int, default=8511)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    main()
