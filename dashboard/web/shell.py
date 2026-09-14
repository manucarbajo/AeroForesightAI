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
#:
#: **Die Reihenfolge ist der Arbeitsablauf** (seit P1.7): Man richtet ein, sieht
#: dann zu, und wertet zuletzt aus. Vorher stand der Leitstand vorn und
#: «Einrichten» an zweiter Stelle — wer das Dashboard zum ersten Mal öffnete,
#: landete auf einer Ansicht, für die es noch nichts zu sehen gab.
#:
#: Der leere Pfad gehört deshalb dem Einrichten. Der Leitstand hat mit `lauf`
#: eine eigene Adresse bekommen; `setup` bleibt als Alias bestehen (siehe
#: `ALIASES`), damit gespeicherte Verweise nicht ins Leere zeigen.
#: **«Modell» steht hinter den Ergebnissen und nicht mitten im Ablauf** (P1.9-W3.1).
#: Einrichten → Leitstand → Ergebnisse ist der Arbeitsablauf eines Laufs; das
#: Modell zu pflegen gehört nicht hinein, sondern daneben. Es steht deshalb bei
#: dem anderen Bereich, den man aufsucht statt durchläuft: dem Handbuch.
#: Der eine Bereich mit Seitenzonen und Zeitleiste (D2, P7.3-U3.1).
LEITSTAND = "lauf"

ROUTES = [
    ("", "Einrichten"),
    (LEITSTAND, "Leitstand"),
    ("runs", "Ergebnisse"),
    ("modell", "Modell"),
    ("doku", "Handbuch"),
]

#: Alte Adressen, die weiterhin funktionieren sollen — Pfad → Bereich.
ALIASES = {"setup": ""}

#: Bereiche, die es gibt, die die Navigation aber nicht zeigt (P7.1-U1.6). Heute
#: einer: die **Musterseite**, jeder Baustein in jedem Zustand — die Referenz,
#: gegen die die Gestaltungswächter laufen. Wer sie braucht, ruft ihre Adresse
#: auf; in den Arbeitsablauf gehört sie nicht.
INTERNE_ROUTES = [("muster", "Musterseite")]

#: Jeder Bereich mit eigenem Wirt im Layout, verlinkt oder nicht. **Daraus**
#: leiten `app.visibility`, der Seitentitel und die Ansage ab; die Navigation
#: liest nur `ROUTES`.
BEREICHE = ROUTES + INTERNE_ROUTES


def active_route(pathname: str | None) -> str:
    """Welcher Bereich zu einer Adresse gehört.

    Als eigene Funktion und nicht im Callback: So ist die Entscheidung ohne
    laufende App prüfbar, und der Callback bleibt eine Verdrahtung.

    **Sie steht seit P3.12 hier und nicht in `app.py`**, weil sie ausschließlich
    aus `ROUTES` und `ALIASES` folgt — beide stehen darüber. Der Anlass war ein
    zweiter Aufrufer: `config_editor` muss wissen, ob der Modell-Bereich offen
    ist, und `app.py` von dort zu importieren wäre ein Zyklus. Die Antwort
    zweimal zu berechnen wäre die Alternative gewesen: zwei Quellen für die
    Frage, welcher Bereich gilt.
    """

    relative = routing.relative(pathname)
    # Das Handbuch hat Unterseiten (`doku/cib`) — hier zählt der Anfang.
    if relative.startswith("doku"):
        return "doku"
    if relative in ALIASES:
        return ALIASES[relative]
    return relative if relative in {route for route, _ in BEREICHE} else ""


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
#: Wirt für das Fortschrittsfenster eines laufenden Laufs (P1.7).
DOCK_HOST = "shell-dock"
#: Die Bereichslinks. Eigener Wirt, damit das Routing nur sie austauscht und
#: nicht die ganze Kopfzeile samt Auswahlfeld und Zustandsanzeige neu baut.
NAV_HOST = "shell-nav"

#: Wo der Bereichswechsel angesagt wird. **Außerhalb der umgeschalteten
#: Bereiche**, sonst entsteht die Region im Moment der Änderung selbst neu — und
#: Vorlesesoftware liest sie dann nicht vor. Dieselbe Lehre wie bei der
#: Schrittfolge (P1.9-W5.3).
BEREICH_ANSAGE = "shell-bereich-ansage"

#: Der Name, unter dem das Produkt im Browser-Tab steht (P7.2-U2.7).
MARKE = "AeroForesight AI"

#: Träger des Seitentitels je Bereich. Unsichtbar; ein clientseitiger Callback
#: schreibt seinen Text nach `document.title`.
SEITENTITEL = "shell-seitentitel"

#: Das Sprungziel des «Zum Inhalt springen»-Links (WCAG 2.4.1).
MAIN_ID = "shell-main"
RUN_SELECT = "shell-run-select"

#: Aktionen der Kopfzeile. Alle drei gibt es bereits als Funktion — sie
#: standen nur an drei verschiedenen Stellen tief in der Seite.
ACTION_SAVE = "shell-action-save"
ACTION_SNAPSHOT = "shell-action-snapshot"
ACTION_EXPORT = "shell-action-export"

#: Die Bereiche, die einen Lauf zeigen (P7.3-U3.4).
LAUF_BEREICHE = frozenset({LEITSTAND, "runs"})

#: **Was in der Kopfzeile nur zu bestimmten Bereichen gehört** — Kennung → Bereiche
#: (P7.3-U3.4, von Haiko entschieden am 2026-09-14).
#:
#: Bis dahin stand alles auf jedem Bereich: Auf dem Handbuch bot die Kopfzeile
#: an, Einstellungen zu sichern, im Einrichten die Dateien eines Laufs. Und
#: beschriftet passte es nicht mehr — gemessen drückten die beiden
#: Speicher-Aktionen die Bereichsnavigation bei 1280 px um 224 px zusammen,
#: solange die Laufauswahl daneben stand. **Die Laufauswahl gehört deshalb zu den
#: Bereichen mit einem Lauf**, das Sichern zum Einrichten.
KONTEXT = {
    RUN_SELECT: LAUF_BEREICHE,
    ACTION_SAVE: frozenset({""}),
    ACTION_SNAPSHOT: frozenset({""}),
    ACTION_EXPORT: LAUF_BEREICHE,
}

#: Was zusätzlich einen gewählten Lauf braucht — ohne ihn gibt es keine Dateien.
BRAUCHT_LAUF = frozenset({ACTION_EXPORT})

#: **Knöpfe der Kopfzeile, die ohne sichtbare Beschriftung bleiben** — mit Grund
#: (P7.3-U3.4). Jeder andere trägt seinen Namen sichtbar; ein Name, der nur im
#: `title` steht, erscheint erst, wenn jemand mit der Maus darauf verweilt.
OHNE_BESCHRIFTUNG = {
    THEME_TOGGLE: (
        "ein Zustandsschalter und keine Aktion: Sonne und Mond sagen, wohin er "
        "schaltet, und eine Beschriftung nähme der Navigation die Breite"
    ),
    LEFT_TOGGLE: "erscheint erst unter 1024 px, wo die Beschriftungen beschnitten sind",
    RIGHT_TOGGLE: "erscheint erst unter 1280 px, wo die Beschriftungen beschnitten sind",
}


#: Bereiche, die den Bildschirm **allein** bekommen. Seitenzonen und Zeitleiste
#: verschwinden dort.
#:
#: **Seit P7.3-U3.1 ist das jeder Bereich außer dem Leitstand** (D2, von Haiko
#: entschieden am 2026-09-14), und die Menge wird abgeleitet statt aufgezählt —
#: ein neuer Bereich ist ohne weiteren Eintrag einer. Bis dahin standen hier
#: Einrichten, Modell und Musterseite; «Ergebnisse» und «Handbuch» teilten den
#: Bildschirm mit Bedienfeld, Telemetrie und Zeitleiste und zeigten damit drei
#: Zusammenhänge zugleich: den Entwurf des nächsten Laufs links, einen
#: vergangenen Lauf in der Mitte, dessen Kennzahlen bei Tick 1 rechts. **Die
#: Zeitleiste bewegte gemessen keine der sieben Ergebnis-Ansichten** — es geht
#: nichts verloren, was dort wirkte.
FOCUS_ROUTES = {route for route, _ in BEREICHE} - {LEITSTAND}


def shell_class(active: str) -> str:
    """Die Klasse des Rahmens — mit oder ohne Seitenzonen."""

    return "af-shell af-shell--focus" if active in FOCUS_ROUTES else "af-shell"


def _nav_link(href: str, label: str, active: bool):
    """Ein Bereichslink — **und die Auskunft, ob er der offene ist** (P1.5).

    Bis zum 2026-08-30 steckte das allein in einer Farbklasse. Für eine
    Vorlesesoftware sind fünf gleich klingende Links dann fünf gleich klingende
    Links; welcher gerade offen ist, war nur zu sehen, nicht zu hören.

    **`aria-current` wird clientseitig gesetzt, nicht hier** — und das ist keine
    Bequemlichkeit: `dcc.Link` nimmt keine fremden Attribute an («received an
    unexpected keyword argument: `aria-current`»), und `html.A` an seiner Stelle
    lüde bei jedem Bereichswechsel die ganze Seite neu. Die Klasse
    `af-nav__link--active` ist deshalb die Quelle; der Callback in `app.py`
    stempelt daraus das Attribut.
    """

    suffix = " af-nav__link--active" if active else ""
    return dcc.Link(label, href=href, className=f"af-nav__link{suffix}".strip())


def nav_links(active: str) -> list:
    """Die Bereichslinks, mit dem aktiven hervorgehoben."""

    return [_nav_link(routing.url(route), label, route == active) for route, label in ROUTES]


def bereich_ansage(active: str) -> str:
    """Was beim Bereichswechsel vorgelesen wird (P1.5).

    Der Name des Bereichs genügt nicht: «Ergebnisse» allein könnte auch eine
    Überschrift sein, die zufällig vorgelesen wird. Der Satz sagt, dass etwas
    **gewechselt** hat.
    """

    for route, label in BEREICHE:
        if route == active:
            return f"Bereich gewechselt: {label}"
    return ""


def seitentitel(active: str) -> str:
    """Was im Browser-Tab steht — Marke und Bereich (P7.2-U2.7).

    Bis zum 2026-09-11 stand dort auf **jedem** Bereich «Technology Lab ·
    Leitstand»: ein Name, den das Produkt nirgends sonst trägt, und ein Bereich,
    in dem man meistens gar nicht war. Wer mehrere Tabs offen hat, findet den
    richtigen am Titel — und nur, wenn er sagt, was darin offen ist.
    """

    bereich = dict(BEREICHE).get(active)
    return f"{MARKE} · {bereich}" if bereich else MARKE


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
                className=f"font-headline {ui.ABSCHNITT} font-bold af-text-accent tracking-tight "
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


def kontext_stile(active: str, *, lauf: bool) -> dict[str, dict | None]:
    """Welche Teile der Kopfzeile in diesem Bereich stehen (P7.3-U3.4).

    Als eigene Funktion und nicht im Callback, damit die Entscheidung ohne
    laufende App prüfbar ist. **Ausgeblendet, nicht weggelassen** (Regel 6):
    `app._save`, `app._export` und die Laufauswahl hängen an diesen Kennungen.
    """

    return {
        kennung: (
            None
            if active in bereiche and (lauf or kennung not in BRAUCHT_LAUF)
            else {"display": "none"}
        )
        for kennung, bereiche in KONTEXT.items()
    }


def actions(active: str = "", *, lauf: bool = False) -> html.Div:
    """Die Aktionen der Kopfzeile — beschriftet, und nur dort, wo sie passen.

    «Als Szenario sichern» legt die Einstellungen als Szenario unter
    `configs/sweeps/` ab, «Zwischenstand sichern» dieselben Werte unter einem
    Namen mit Zeitstempel, damit ein Zwischenstand den benannten Stand nicht
    überschreibt — beide gehören zum Einrichten. «Dateien des Laufs» führt in
    die Dateiablage des gewählten Laufs.

    **Bis P7.3-U3.4 waren es drei Symbolknöpfe**, deren Name nur im `title`
    stand. Unter 1280 px wird die Beschriftung beschnitten und nicht entfernt
    (`af-kopfaktion` im Stylesheet): Der Name bleibt im Baum und im `title`.
    """

    stile = kontext_stile(active, lauf=lauf)
    knoepfe = [
        (ACTION_SAVE, "Als Szenario sichern", "save"),
        (ACTION_SNAPSHOT, "Zwischenstand sichern", "photo_camera"),
        (ACTION_EXPORT, "Dateien des Laufs", "download"),
    ]
    return html.Div(
        [
            ui.button(
                beschriftung,
                variant="ghost",
                icon_name=symbol,
                id=kennung,
                title=beschriftung,
                className="af-kopfaktion",
                style=stile[kennung],
            )
            for kennung, beschriftung, symbol in knoepfe
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
    stile = kontext_stile(active, lauf=run_value is not None)
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
                        style=stile[RUN_SELECT],
                    ),
                    actions(active, lauf=run_value is not None),
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


def _gutter(seite: str, titel: str) -> html.Div:
    """Ein Ziehgriff zwischen zwei Zonen (P1.7).

    Ohne Dash-Callback: Das Ziehen läuft in `assets/shell_resize.js`, weil ein
    Serverrundlauf je Mausbewegung das Ziehen zäh macht — dieselbe Begründung
    wie beim Theme-Umschalter. Der Griff ist deshalb ein reines Ziel für das
    Skript und hat bewusst **keine** Dash-ID.

    `tabIndex` und `role`, weil er sonst nur mit der Maus bedienbar wäre; die
    Pfeiltasten verschieben ihn in Sechzehner-Schritten.
    """

    return html.Div(
        className=f"af-shell__gutter af-shell__gutter--{seite}",
        title=f"{titel} — ziehen, Doppelklick setzt zurück",
        tabIndex="0",
        **{
            "role": "separator",
            "aria-orientation": "vertical",
            "aria-label": titel,
        },
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
            # **Der erste Griff für die Tastatur** (P1.5, WCAG 2.4.1). Ohne ihn
            # tastet man sich vor jedem Bereich durch Kopfzeile, Schubladen-
            # umschalter und fünf Bereichslinks, bevor der Inhalt kommt.
            # Sichtbar nur, wenn er den Fokus hat.
            html.A(
                "Zum Inhalt springen",
                href=f"#{MAIN_ID}",
                className="af-sprunglink",
            ),
            # Die Live-Region des Bereichswechsels. Sie steht **hier**, außerhalb
            # der fünf Zonen: Was beim Wechsel ausgetauscht wird, kann keine
            # Ansage tragen.
            html.Div(
                id=BEREICH_ANSAGE,
                className="af-nur-vorlesen",
                **{"aria-live": "polite", "aria-atomic": "true"},
            ),
            # Der Seitentitel. `hidden` und nicht `af-nur-vorlesen`: Die Ansage
            # darüber sagt den Wechsel schon, ein zweiter Text wäre Doppelung.
            html.Div(seitentitel(active), id=SEITENTITEL, hidden=True),
            header(active, state=state, run_options=run_options, run_value=run_value),
            html.Aside(left, className="af-shell__left", id="shell-left"),
            _gutter("left", "Breite des Bedienfelds ändern"),
            html.Main(main, className="af-shell__main", id=MAIN_ID),
            _gutter("right", "Breite der Telemetrie ändern"),
            html.Div(timeline, className="af-shell__timeline", id="shell-timeline"),
            html.Aside(right, className="af-shell__right", id="shell-right"),
            # Der Verdunkler liegt über dem Inhalt, sobald eine Schublade offen
            # ist. Ein Klick schließt sie — auf schmalen Geräten die einzige
            # Geste, die ohne Zielen funktioniert.
            html.Div(id=SCRIM, className="af-shell__scrim", n_clicks=0),
            # Das Fortschrittsfenster eines laufenden Laufs (P1.7). Es liegt
            # ausserhalb der fünf Zonen, weil es über allen schwebt — und es
            # bleibt leer, solange nichts rechnet oder man ohnehin auf dem
            # Leitstand steht.
            html.Div(id=DOCK_HOST),
        ],
        className=shell_class(active),
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

    # Der Browser-Tab folgt dem Bereich (P7.2-U2.7). Clientseitig, weil
    # `document.title` nur im Browser existiert; der Text selbst entsteht auf
    # dem Server in `seitentitel`, damit er ohne Browser prüfbar bleibt.
    app.clientside_callback(
        """
        function(titel) {
            if (titel) { document.title = titel; }
            return window.dash_clientside.no_update;
        }
        """,
        Output(SEITENTITEL, "title"),
        Input(SEITENTITEL, "children"),
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
