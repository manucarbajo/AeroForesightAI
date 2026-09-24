"""Die Musterseite: jeder Baustein in jedem Zustand (P7.1-U1.6).

**Wozu es sie gibt.** Die Gestaltungswächter aus P7.0 messen, was die Bereiche
zeigen — und ein Bereich zeigt, was sein Inhalt gerade braucht. Ein Ton, den
kein Bereich benutzt, eine Variante, die heute nirgends steht, ein Zustand, der
nur bei einem Fehler erscheint: Sie wurden nie gemessen, weil sie nie
gezeichnet wurden. Hier stehen sie alle nebeneinander, und die Wächter laufen
auch gegen diese Seite.

**Was «jeder Zustand» heißt**, und zwar gesucht statt aufgezählt
(`tests/test_web_musterseite.py`): jede öffentliche Funktion aus
`components.py`; jeder Wahrheitswert in ihrer Signatur mit beiden Werten; jeder
Eintrag einer Zustandsmenge, die sie liest (`HINWEIS_TOENE`, `LOG_LEVELS` …);
und jeder Modifikator, den sie als `af-…--{parameter}` zusammensetzt und das
Stylesheet kennt. Nicht dazu gehören Zustände, die erst der Browser herstellt —
Zeigen, Fokus, Drücken —, denn die wählt kein Aufruf.

**Hell und dunkel über den Umschalter**, nicht nebeneinander (von Haiko
entschieden am 2026-09-13): Die dunklen Tokens hängen an `html.dark`, und ein
dunkler Abschnitt in einer hellen Seite bräuchte eine zweite Token-Gruppe, die
vom Betrieb abweichen könnte. So sieht die Seite dunkel genau so aus wie jeder
Bereich.

**Nicht in der Navigation** (`shell.INTERNE_ROUTES`) und **erst beim Aufsuchen
gebaut** — dasselbe Muster wie der Modell-Bereich (P3.12): Der Rumpf trägt
keine feste Kennung, und `rumpf_fuer` liefert auf jedem anderen Pfad nichts.

**Jede Probe trägt, was sie zeigt**, als `data-baustein` und `data-zustand`.
So misst der Wächter die gezeichnete Seite und nicht diese Datei.
"""

from __future__ import annotations

from typing import Any

from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web import status

#: Unter welcher Adresse die Seite liegt — **eine** Quelle, wie beim Modell.
ROUTE = "muster"

#: Wirt für den Rumpf. Leer, bis jemand die Seite aufsucht.
HOST = "muster-host"

#: Der Typ der Muster-Kennungen auf dieser Seite. Nur `ui.tabs` braucht eine.
KENNUNG = "muster"


def _probe(baustein: str, element: Any, **zustand: object) -> html.Div:
    """Ein Baustein in einem Zustand — beschriftet und maschinenlesbar."""

    zeichen = " ".join(f"{name}={wert}" for name, wert in zustand.items())
    beschriftung = f"ui.{baustein}"
    if zustand:
        beschriftung += " · " + ", ".join(f"{name} {wert}" for name, wert in zustand.items())
    return html.Div(
        [html.Div(beschriftung, className=f"{ui.CAPTION} mb-2"), element],
        **{"data-baustein": baustein, "data-zustand": zeichen},
    )


def _gruppe(titel: str, unterzeile: str, *proben: Any) -> html.Section:
    return ui.section(titel, html.Div(list(proben), className="space-y-4"), subtitle=unterzeile)


def _reihe(*proben: Any) -> html.Div:
    return html.Div(list(proben), className="flex flex-wrap items-start gap-4")


def _schrift() -> html.Section:
    return _gruppe(
        "Schrift und Text",
        "Überschriften, Sätze, Markdown und Code.",
        _probe(
            "page_heading",
            html.Div(
                ui.page_heading("Seitentitel", "Die Unterzeile sagt, wozu die Seite dient."),
                **{"aria-hidden": "true"},
            ),
        ),
        _probe(
            "section",
            ui.section(
                "Abschnitt",
                ui.satz("Der Inhalt des Abschnitts."),
                subtitle="Eine Unterzeile unter dem Abschnittstitel.",
                actions=ui.button("Aktion", variant="secondary"),
            ),
        ),
        _probe("satz", ui.satz("Ein schlichter Satz bleibt ein Absatz."), klein=False),
        _probe(
            "satz",
            ui.satz("Ein kleiner Satz mit **Auszeichnung** wird Markdown.", klein=True),
            klein=True,
        ),
        _probe("lede", ui.lede("Der **Einleitungssatz** eines Blocks ist Fließtext.")),
        _probe(
            "markdown",
            ui.markdown(
                "Ein Absatz mit `Code`, **Fettung** und einer Liste:\n\n"
                "- erster Punkt\n- zweiter Punkt"
            ),
        ),
        _probe("hint_text", ui.hint_text("Der Kurzhinweis unter einem Feld.")),
        _probe("code_block", ui.code_block("max_ticks = 40\nseed = 42")),
        _probe("json_view", ui.json_view({"rahmen": {"id": "standard", "quelle": "standard"}})),
        _probe("doc_link", ui.doc_link("glossar")),
        _probe("icon", ui.icon("science")),
        _probe("divider", ui.divider("my-4")),
    )


def _meldungen() -> html.Section:
    return _gruppe(
        "Hinweise und Zustände",
        "Jeder Ton des Hinweises, jeder Zustand der Anlage.",
        # Die Töne stehen wörtlich da und nicht aus `HINWEIS_TOENE` gelesen:
        # `tests/test_web_hinweis.py` prüft jeden Ton am Aufruf, und ob keiner
        # fehlt, sagt `tests/test_web_musterseite.py`.
        _probe(
            "hinweis",
            ui.hinweis("Erklärender **Kontext** neben einer Entscheidung.", "kontext"),
            ton="kontext",
        ),
        _probe(
            "hinweis",
            ui.hinweis("Eine **Auskunft**: Das gilt für diesen Lauf.", "info"),
            ton="info",
        ),
        _probe(
            "hinweis",
            ui.hinweis("Ein **Erfolg**: Die Population ist gespeichert.", "erfolg"),
            ton="erfolg",
        ),
        _probe(
            "hinweis",
            ui.hinweis("Eine **Warnung**: Der Verlauf endet vor dem Lauf.", "warnung"),
            ton="warnung",
        ),
        _probe(
            "hinweis",
            ui.hinweis("Ein **Fehler**: Die Konfiguration ist ungültig.", "fehler"),
            ton="fehler",
        ),
        _probe(
            "hinweis",
            ui.hinweis("Ein **Beispiel**: Das sind keine echten Laufdaten.", "demo"),
            ton="demo",
        ),
        _reihe(
            _probe("status_dot", ui.status_dot("bereit", "Erreichbar"), zustand="bereit"),
            _probe("status_dot", ui.status_dot("pruefen", "Wird geprüft …"), zustand="pruefen"),
            _probe(
                "status_dot",
                ui.status_dot("aus", "Nicht erreichbar", hint="Der Dienst antwortet nicht."),
                zustand="aus",
            ),
        ),
        _reihe(
            *[
                _probe("status_indicator", ui.status_indicator(ton, text), tone=ton)
                for ton, text in (
                    (status.READY, "System bereit"),
                    (status.RUNNING, "Lauf rechnet"),
                    (status.DEGRADED, "Eingeschränkt"),
                    (status.DEMO, "Beispieldaten"),
                )
            ]
        ),
        _reihe(
            _probe("badge", ui.badge("Standard"), variant="default"),
            _probe(
                "badge", ui.badge("Beispiel", variant="demo", icon_name="science"), variant="demo"
            ),
            _probe("badge", ui.badge("Achtung", variant="warning"), variant="warning"),
        ),
        _probe(
            "empty_state",
            ui.empty_state(
                "Noch keine Läufe.", hint="Nach dem Start erscheint er hier.", icon_name="science"
            ),
        ),
        _probe("console", ui.console([]), lines="leer"),
        *[
            _probe(
                "log_line",
                ui.console([ui.log_line(stufe, f"Eine Zeile der Stufe «{stufe}».", tick=12)]),
                level=stufe,
            )
            for stufe in ui.LOG_LEVELS
        ],
    )


def _kacheln() -> html.Section:
    return _gruppe(
        "Kacheln",
        "Jede Variante; eine Veränderung trägt nur die kompakte.",
        ui.grid(
            _probe("kachel", ui.kachel("Ticks", 40, "Ein Tick ist ein Monat."), variante="zahl"),
            _probe(
                "kachel",
                ui.kachel("Szenario", "Standard-Ausgangslage", variante="text"),
                variante="text",
            ),
            *[
                _probe(
                    "kachel",
                    ui.kachel(
                        "Ticketpreis",
                        "118,85 €",
                        variante="kompakt",
                        delta=delta,
                        direction=richtung,
                    ),
                    variante="kompakt",
                    direction=richtung,
                )
                for richtung, delta in (("up", "+2,1 %"), ("down", "−1,4 %"), (None, None))
            ],
        ),
        _probe(
            "grid", ui.grid(ui.card(ui.satz("Linke Zelle.")), ui.card(ui.satz("Rechte Zelle.")))
        ),
    )


def _knoepfe() -> html.Section:
    return _gruppe(
        "Knöpfe",
        "Eine Primäraktion je Fläche; die übrigen Varianten daneben.",
        _reihe(
            _probe("button", ui.button("Lauf starten", icon_name="play_arrow"), variant="primary"),
            _probe("button", ui.button("Speichern", variant="secondary"), variant="secondary"),
            _probe("button", ui.button("Abbrechen", variant="ghost"), variant="ghost"),
            _probe("button", ui.button("Entfernen", variant="danger"), variant="danger"),
            _probe(
                "button",
                ui.button("Gesperrt", variant="secondary", disabled=True),
                variant="secondary",
                disabled=True,
            ),
        ),
        _reihe(
            _probe("icon_button", ui.icon_button("dark_mode", "Dunkel"), active=False),
            _probe(
                "icon_button", ui.icon_button("zoom_in", "Vergrößern", active=True), active=True
            ),
        ),
    )


def _eingaben() -> html.Section:
    return _gruppe(
        "Eingaben",
        "Felder in jeder Breite, mit Hinweis, Befund und Erklärung.",
        _probe("field", ui.field("Ohne Breite", dcc.Input(type="text")), breite=None),
        *[
            _probe(
                "field",
                ui.field(f"Breite «{breite}»", dcc.Input(type="number"), breite=breite),
                breite=breite,
            )
            for breite in ui.FELDBREITEN
        ],
        _probe(
            "explainer",
            ui.field(
                "Ticks",
                dcc.Input(type="number"),
                hint="Wie lange der Lauf rechnet.",
                below=html.Div(
                    ui.explainer("Ein Tick ist ein Monat; 40 Ticks sind gut drei Jahre.")
                ),
                breite="feld-klein",
            ),
        ),
        _probe(
            "field_errors",
            ui.field(
                "Name",
                dcc.Input(type="text"),
                below=ui.field_errors(["Der Name darf nicht leer sein."]),
                breite="feld",
            ),
        ),
        _probe("checkbox", ui.checkbox("Alle Szenarien", value=True), value=True),
        _probe(
            "checkbox",
            ui.checkbox("Eigene Werte anwenden", value=False, hint="Sonst gilt die Auslieferung."),
            value=False,
        ),
        _probe("toggle", ui.toggle("Sprachmodell", value=True), value=True),
        _probe("toggle", ui.toggle("Diagramme nach Lauf", value=False), value=False),
        _probe(
            "radio",
            ui.radio(_optionen(), value="standard", legend="Ausgangslage"),
            cards=False,
        ),
        _probe("radio", ui.radio(_optionen(), value="eigen", cards=True), cards=True),
    )


def _optionen() -> list[dict]:
    return [
        {"label": "Standard-Ausgangslage", "value": "standard"},
        {"label": "Eigene Werte", "value": "eigen"},
        {"label": "Business as Usual", "value": "bau"},
    ]


def _aufklappen() -> html.Section:
    return _gruppe(
        "Aufklappen",
        "Akkordeon für Gleichrangiges, Klappe für Zweitrangiges, «Mehr dazu» am Feld.",
        _probe(
            "accordion",
            ui.accordion("Geöffneter Abschnitt", ui.satz("Sein Inhalt."), open=True, badge="3"),
            open=True,
        ),
        _probe(
            "accordion",
            ui.accordion("Geschlossener Abschnitt", ui.satz("Sein Inhalt.")),
            open=False,
        ),
        _probe(
            "expert",
            ui.expert(
                ui.field("Seed", dcc.Input(type="number"), breite="feld-klein"),
                ui.field("Wiederholungen", dcc.Input(type="number"), breite="feld-klein"),
                count=2,
                names="Seed, Wiederholungen",
            ),
        ),
        _probe(
            "expert",
            ui.expert(
                ui.satz("Drei Vorschauen, keine Eingabe."),
                count=3,
                title="Rohdaten ansehen",
                einheit=("Vorschau", "Vorschauen"),
            ),
        ),
        _probe(
            "tabs",
            ui.tabs(
                {"type": KENNUNG, "name": "reiter"},
                [("Erster Reiter", "eins"), ("Zweiter Reiter", "zwei")],
                "eins",
            ),
        ),
        _probe("card", ui.card(ui.satz("Eine Karte mit Polsterung.")), pad=True),
        _probe("card", ui.card(ui.satz("Eine Karte ohne Polsterung."), pad=False), pad=False),
    )


def body() -> html.Div:
    """Jede Gruppe der Musterseite, von der Schrift bis zum Aufklappen."""

    return html.Div([_schrift(), _meldungen(), _kacheln(), _knoepfe(), _eingaben(), _aufklappen()])


def rumpf_fuer(pathname: str | None) -> object:
    """Der Rumpf, wenn die Seite offen ist — sonst nichts (wie `model_editor.rumpf_fuer`)."""

    from dashboard.web import shell

    if shell.active_route(pathname) != ROUTE:
        return []
    return body()


def layout() -> html.Div:
    """Der Rahmen: Überschrift und der leere Wirt."""

    return html.Div(
        [
            ui.page_heading(
                "Musterseite",
                "Jeder Baustein der Oberfläche in jedem Zustand, den ein Aufruf wählen kann. "
                "Hell und dunkel über den Umschalter in der Kopfzeile. Die Seite ist nicht "
                "verlinkt; gegen sie laufen die Wächter des Gestaltungssystems.",
            ),
            # **In einer Ladeanzeige** (P7.3-U3.5): Der Rumpf entsteht erst beim Aufsuchen.
            # Braucht das länger als `LADEANZEIGE_NACH_MS`, sieht man, dass etwas kommt;
            # sonst sieht man nichts davon.
            dcc.Loading(
                html.Div([], id=HOST),
                type="dot",
                className="af-ladeanzeige",
                delay_show=ui.LADEANZEIGE_NACH_MS,
            ),
        ],
        className="af-pane af-pane--focus",
    )
