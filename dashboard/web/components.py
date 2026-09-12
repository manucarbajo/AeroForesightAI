"""Wiederverwendbare Bausteine des Leitstands.

Die Klassennamen sind Tailwind-Utilities für **Layout, Abstand und Typografie**
— dieselbe Konfiguration, die `aeroforesight-ai-landing-page/index.html` lädt.

**Farben stehen nicht darunter.** Sie kommen ausschließlich über `af-*`-Klassen
aus `assets/dashboard.css`, die ihre Werte aus den semantischen Tokens von
`theme.py` beziehen. Der Grund ist der Dark Mode: `bg-white` ist im dunklen
Modus eine falsche Aussage, `af-surface` ist in beiden Modi dieselbe richtige.
`tests/test_web_theme.py` prüft mechanisch, dass keine Farbklasse zurückkehrt —
eine gepflegte Liste finge nur den Rückfall an bekannter Stelle.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from dash import dcc, html

from dashboard.web import routing

# --- Klassenbausteine ------------------------------------------------------

CARD = "af-card"
CARD_PAD = f"{CARD} p-5 sm:p-6"
#: Die sechs Rollen der Schriftskala (P7.1-U1.1, entschieden am 2026-09-12).
#: Größe, Gewicht und Zeilenhöhe stehen in `assets/dashboard.css` als
#: `.af-schrift-*`; hier stehen nur die Namen. **Vorher kamen die Größen aus
#: drei Quellen** — dem Stylesheet, Tailwinds `text-*`-Klassen im Python-Code
#: und diesen Konstanten, die selbst wieder Tailwind zusammensetzten —, und
#: gerendert waren es dreizehn Größen in 23 Kombinationen aus Größe und
#: Gewicht. Wer eine siebte Rolle braucht, ändert die Skala und nicht den
#: Aufruf; `tests/test_web_schriftskala.py` meldet jede Größe daneben.
TITEL = "af-schrift-titel"
UEBERSCHRIFT = "af-schrift-ueberschrift"
ABSCHNITT = "af-schrift-abschnitt"
TEXT = "af-schrift-text"
BESCHRIFTUNG = "af-schrift-beschriftung"
KLEIN = "af-schrift-klein"

LABEL = f"block font-body {BESCHRIFTUNG} font-medium af-text-body mb-1.5"
#: Der kleine Erklaertext unter einem Feld oder einer Zustandsanzeige.
#:
#: **Ohne Deckel seit dem 2026-09-12** (Ruecknahme von E3): Er laeuft so weit
#: wie der Rahmen, in dem er steht. P3.17 hatte ihm ein Lesemass gegeben, weil
#: der Browser-Waechter an `status_dot` 106 Zeichen je Zeile gemessen hatte;
#: zugesagt waren 75. **Die Beobachtung von damals bleibt wahr und ist
#: aufschlussreich:** Die laengste Zeichenkette, die hier ankommen kann, ist
#: die Fehlermeldung eines fremden Dienstes («Nicht erreichbar: [WinError
#: 10061] …») — die schreibt niemand kuerzer, und ein Deckel hat sie nicht
#: gekuerzt, sondern nur umgebrochen.
HINT = f"font-body {KLEIN} af-text-muted mt-1.5"
CAPTION = f"font-body {KLEIN} af-text-muted"
#: Der Einleitungssatz eines Schritts oder eines Blocks — **Fliesstext**.
#:
#: **Seit dem 2026-09-12 eine eigene Rolle, und zwar in Fliesstextgroesse.**
#: Vorher war eine Lede zweierlei: die eines Schritts stand in `CAPTION`
#: (12 px), die eines Blocks in `af-md--lede` (14 px) — beide kleiner als der
#: Fliesstext, den sie einleiten. Gemessen war die Schritt-Lede damit der
#: schmalste Text des Bildschirms (409 px von 760, 53,8 %), weil 12-px-Prosa
#: fuer 75 Zeichen nur 416 px braucht. **Eine Lede ist kein Beiwerk zum Text,
#: sie ist der erste Satz davon** — und eine Bildunterschrift ist sie schon
#: deshalb nicht, weil kein Bild darueber steht.
LEDE = f"font-body {TEXT} af-text-muted"
H1 = f"font-headline {TITEL} font-bold af-text tracking-tight"
H2 = f"font-headline {UEBERSCHRIFT} font-semibold af-text tracking-tight"
H3 = f"font-headline {ABSCHNITT} font-semibold af-text"

_BUTTON_BASE = (
    "af-btn inline-flex items-center justify-center gap-2 px-5 py-2.5 font-body "
    f"{BESCHRIFTUNG} font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
)
_BUTTON_VARIANTS = {
    "primary": "af-btn--primary",
    "secondary": "af-btn--secondary",
    "ghost": "af-btn--ghost",
    "danger": "af-btn--danger",
}

_ALERT_VARIANTS = {
    "info": ("af-alert--info", "info"),
    "success": ("af-alert--success", "check_circle"),
    "warning": ("af-alert--warning", "warning"),
    "error": ("af-alert--error", "error"),
    "demo": ("af-alert--demo", "science"),
}

#: Die vier Stufen der Konsole. Reihenfolge ist Rangfolge — `status.py` und die
#: Zeitleiste ordnen ihre Marker danach ein.
LOG_LEVELS = ("muted", "info", "warning", "error")


# --- Bausteine -------------------------------------------------------------


def icon(name: str, class_name: str = "text-base") -> html.Span:
    """Material-Symbol wie auf der Landingpage."""

    return html.Span(name, className=f"material-symbols-outlined {class_name}")


def card(*children: Any, class_name: str = "", pad: bool = True) -> html.Div:
    base = CARD_PAD if pad else CARD
    return html.Div(list(children), className=f"{base} {class_name}".strip())


def section(
    title: str | None,
    *children: Any,
    subtitle: str | None = None,
    actions: Any = None,
    class_name: str = "",
) -> html.Section:
    head: list[Any] = []
    if title or actions:
        head.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(title, className=H2) if title else None,
                            html.P(subtitle, className=f"{CAPTION} mt-1") if subtitle else None,
                        ]
                    ),
                    (
                        html.Div(actions, className="flex items-center gap-2 shrink-0")
                        if actions
                        else None
                    ),
                ],
                className="flex items-start justify-between gap-4 mb-4 flex-wrap",
            )
        )
    return html.Section(head + list(children), className=f"mb-8 {class_name}".strip())


def page_heading(title: str, subtitle: str | None = None) -> html.Div:
    return html.Div(
        [
            html.H1(title, className=H1),
            html.P(subtitle, className="font-body af-text-body mt-2") if subtitle else None,
        ],
        className="mb-6",
    )


def button(label: str, *, variant: str = "primary", icon_name: str | None = None, **kwargs: Any):
    """Ein Knopf. **Die Beschriftung steht in einem eigenen Träger** (P1.9-W5.5).

    Als blanker Text ließe sie sich nicht ansprechen — und genau das braucht die
    schmale Breite: Dort werden die Beschriftungen zweitrangiger Knöpfe
    beschnitten, damit die Fußleiste einzeilig bleibt. **Beschnitten, nicht
    entfernt**: Der Name bleibt damit im Baum und wird vorgelesen; `display:
    none` nähme ihn auch der Vorlesesoftware und machte aus dem Knopf ein
    stummes Symbol.
    """

    children: list[Any] = [html.Span(label, className="af-btn__label")]
    if icon_name:
        children.append(icon(icon_name, "text-sm"))
    class_name = f"{_BUTTON_BASE} {_BUTTON_VARIANTS.get(variant, _BUTTON_VARIANTS['primary'])}"
    extra = kwargs.pop("className", "")
    return html.Button(children, className=f"{class_name} {extra}".strip(), n_clicks=0, **kwargs)


def icon_button(icon_name: str, title: str, *, active: bool = False, **kwargs: Any) -> html.Button:
    """Quadratische Schaltfläche ohne Beschriftung.

    Für die Media-Controls der Zeitleiste und die Werkzeuge der Kopfzeile. Der
    Klartext steht als `title` — ohne ihn wäre ein Symbol allein für
    Screenreader und für Neulinge stumm.
    """

    extra = kwargs.pop("className", "")
    state = " af-icon-btn--active" if active else ""
    return html.Button(
        icon(icon_name, "text-lg"),
        className=f"af-icon-btn{state} {extra}".strip(),
        title=title,
        n_clicks=0,
        **{"aria-label": title, **kwargs},
    )


def hint_text(hint: str | None, *, class_name: str = "") -> Any:
    """Erklärung unter einem Feld.

    Als Markdown, weil die Texte aus dem Glossar den technischen Feldnamen in
    Backticks mitführen — als reiner Text stünden die Zeichen sichtbar da.
    """

    if not hint:
        return None
    return dcc.Markdown(hint, className=f"af-hint af-md af-md--tight {class_name}".strip())


#: Die Breiten, die eine Eingabe haben darf — als Stufe, nicht als Wert. Die
#: Werte stehen als `--breite-feld-*` in `assets/dashboard.css`.
FELDBREITEN = ("feld-klein", "feld", "feld-weit")


def field(
    label: str,
    control: Any,
    *,
    hint: str | None = None,
    below: Any = None,
    class_name: str = "",
    breite: str | None = None,
) -> html.Div:
    """Beschriftetes Eingabefeld.

    *below* nimmt auf, was unter Feld und Kurzhinweis gehört — heute der
    Platzhalter für Fehlermeldungen aus der Konfigurationsprüfung und die
    aufklappbare Langerklärung aus dem Glossar.

    **`breite` begrenzt die Eingabe, nicht das Feld** (2026-09-12). Bis dahin
    kam die Breite über `class_name` — und `class_name` sitzt auf dem Rahmen um
    Beschriftung, Eingabe, Hinweis *und* Erklärung. Ein `max-w-xs` für ein
    Zahlenfeld stellte damit die Glossar-Erklärung zu «Ticks» in einen 320 px
    breiten Streifen, mitten in einer 760 px breiten Karte. Das war ein
    Lesemaß unter anderem Namen, und es hat die Rücknahme von E3 überlebt, weil
    der Breitenwächter zunächst nur eine Ebene über dem Text nachsah.

    Jetzt steckt nur die Eingabe in einem begrenzten Träger; alles darunter
    füllt den Rahmen. `class_name` bleibt für Abstände (`mb-5`). Ein
    unbekannter Wert scheitert laut, statt still keine Breite zu setzen.
    """

    if breite is not None and breite not in FELDBREITEN:
        raise ValueError(f"Unbekannte Feldbreite {breite!r}; erlaubt sind {FELDBREITEN}.")
    eingabe = html.Div(control, className=f"af-breite-{breite}") if breite else control
    return html.Div(
        [
            html.Label(label, className=LABEL),
            eingabe,
            hint_text(hint),
            below,
        ],
        className=class_name,
    )


def field_errors(messages: list[str]) -> Any:
    """Befunde direkt unter dem Feld, das sie betreffen.

    Leere Liste heißt: nichts anzeigen. Der Platzhalter bleibt trotzdem im DOM,
    damit der Callback ihn füllen kann, sobald sich etwas ändert.
    """

    if not messages:
        return None
    return html.Div(
        [
            html.Div(
                [icon("error", "text-sm shrink-0 mt-0.5"), html.Span(text)],
                className="flex items-start gap-1.5",
            )
            for text in messages
        ],
        className=f"font-body {KLEIN} af-text-negative mt-1.5 space-y-1",
    )


# Anordnung und Ausrichtung von Checkbox, Umschalter und Auswahl stehen in
# `assets/dashboard.css` (`.af-check label`, `.af-switch label`,
# `.af-radio label`, `.af-radio--cards label`) — **nicht** hier.
#
# Bis Dash 3 ging das nicht: `dcc.Checklist` schrieb `display: block` selbst als
# Inline-Style auf das Label und haette jede Regel aus dem Stylesheet
# ueberstimmt. Deshalb lagen die Werte frueher als `labelStyle`-Dicts in diesem
# Modul. **Dash 4 schreibt nicht mehr inline** — am laufenden System nachgesehen:
# `label.getAttribute("style")` ist `null`, und die Option traegt jetzt einen
# `span.dash-options-list-option-wrapper` um das Eingabeelement.
#
# Die Dicts wirkten seither nicht mehr. Sie sind entfernt und nicht bloss
# auskommentiert: Stehengeblieben waeren sie eine Falle, in die genau einmal
# jemand tritt, der dort etwas aendert und sich wundert, dass nichts passiert.


def checkbox(
    label: str, *, value: bool, hint: str | None = None, below: Any = None, **kwargs: Any
) -> html.Div:
    """Einzelne Checkbox mit Beschriftung — ersetzt ``st.checkbox``."""

    return html.Div(
        [
            dcc.Checklist(
                options=[{"label": label, "value": "on"}],
                value=["on"] if value else [],
                className="af-check",
                inputClassName="af-check__input",
                labelClassName="af-check__label",
                **kwargs,
            ),
            hint_text(hint, class_name="af-check__hint"),
            below,
        ]
    )


def toggle(
    label: str, *, value: bool, hint: str | None = None, below: Any = None, **kwargs: Any
) -> html.Div:
    """Schalter für einen Systemzustand, der an oder aus ist.

    Technisch dieselbe `dcc.Checklist` wie `checkbox` — optisch bewusst etwas
    anderes: Eine Checkbox wählt aus einer Menge aus, ein Schalter kippt einen
    Zustand. In einer Parameterspalte, in der beides nebeneinander steht, ist
    dieser Unterschied ablesbar und nicht bloß dekorativ.
    """

    return html.Div(
        [
            dcc.Checklist(
                options=[{"label": label, "value": "on"}],
                value=["on"] if value else [],
                className="af-switch",
                **kwargs,
            ),
            hint_text(hint, class_name="af-check__hint"),
            below,
        ]
    )


#: Als Kartenraster statt als Liste. Die Beschriftungen werden zu Gitterfeldern;
#: das Innere bleibt dieselbe Zeile aus Knopf und Text. Fuer Auswahlen mit
#: vielen Moeglichkeiten und je einem beschreibenden Satz — untereinander waeren
#: zehn davon drei Bildschirme lang.
def radio(
    options: list[dict],
    *,
    value: Any,
    cards: bool = False,
    legend: str | None = None,
    **kwargs: Any,
):
    """Auswahl unter sich ausschließenden Möglichkeiten.

    Anordnung und Ausrichtung stehen im Stylesheet: `.af-radio label` richtet an
    der ersten Textzeile aus (eine gerade Spalte von Haken neben den
    Beschriftungen), `.af-radio--cards label` dagegen **mittig** — eine Karte
    ist eine Fläche, die man als Ganzes auswählt, und ein Haken bei 12 % ihrer
    Höhe wirkt oben angeheftet.

    *cards* stellt die Möglichkeiten als Raster nebeneinander statt
    untereinander. Der Unterschied ist nicht kosmetisch: Bei zehn Optionen mit
    je einem erklärenden Satz ist die Liste drei Bildschirme lang, das Raster
    drei Reihen.
    """

    gruppe = dcc.RadioItems(
        options=options,
        value=value,
        className="af-radio af-radio--cards" if cards else "af-radio",
        inputClassName="af-radio__input",
        labelClassName="af-radio__label",
        **kwargs,
    )
    if legend is None:
        return gruppe

    # **`fieldset` und `legend`, nicht nur eine Überschrift daneben**
    # (P1.9-W5.3). Für einen Screenreader ist eine Reihe von Radioknöpfen ohne
    # Gruppe eine Reihe unbeschrifteter Optionen: Er liest «Standard-Ausgangslage,
    # 1 von 10» vor, ohne zu sagen, **wovon** das eine von zehn ist. Die Legende
    # beantwortet genau das und wird beim Betreten der Gruppe einmal
    # mitgesprochen.
    #
    # Sichtbar ist sie nicht: Der Titel des Schritts steht bereits darüber, und
    # eine zweite Überschrift wäre für Sehende eine Dopplung. `af-nur-vorlesen`
    # nimmt sie aus dem Bild, **nicht** aus dem Baum — `display: none` oder
    # `visibility: hidden` nähmen sie auch dem Screenreader.
    return html.Fieldset(
        [html.Legend(legend, className="af-nur-vorlesen"), gruppe],
        className="af-fieldset",
    )


def status_dot(ok: bool, text: str, *, hint: str | None = None) -> html.Div:
    """Zustandsanzeige für etwas, das erreichbar sein kann oder nicht."""

    tone = "af-status__dot--ok" if ok else "af-status__dot--off"
    return html.Div(
        [
            html.Span(className=f"af-status__dot mt-1.5 {tone}"),
            html.Div(
                [
                    html.Span(text, className=f"font-body {BESCHRIFTUNG} af-text-body"),
                    html.P(hint, className=HINT) if hint else None,
                ]
            ),
        ],
        className="flex items-start gap-2.5",
    )


def status_indicator(tone: str, text: str, *, hint: str | None = None) -> html.Div:
    """Der Zustand der Anlage in der Kopfzeile.

    *tone* ist einer der Werte aus `dashboard.web.status` — `ready`, `running`,
    `degraded`, `demo`. Bei `running` und `demo` pulsiert der Punkt; das ist
    die einzige Bewegung in der Oberfläche und deshalb eindeutig.
    """

    return html.Div(
        [
            html.Span(className="af-status__dot"),
            html.Span(text),
        ],
        className=f"af-status af-status--{tone}",
        title=hint or text,
    )


def badge(text: str, *, variant: str = "default", icon_name: str | None = None) -> html.Span:
    suffix = "" if variant == "default" else f" af-badge--{variant}"
    children: list[Any] = [icon(icon_name, "text-xs")] if icon_name else []
    children.append(text)
    return html.Span(children, className=f"af-badge{suffix}")


def metric_tile(
    label: str, value: Any, hint: str | None = None, *, prose: bool = False
) -> html.Div:
    """Beschriftung über einem Wert, in einer Karte.

    *prose* ist die Fassung für Werte, die **Text** sind statt einer Zahl —
    «Standard-Ausgangslage», «Ohne Sprachmodell». Der große Zahlensatz (2xl,
    fett, Ziffern gleicher Breite) ist für sie zu groß: In einer dreispaltigen
    Reihe trat er aus der Karte heraus und lief in die Nachbarkachel. Die
    Textfassung setzt kleiner, erlaubt den Umbruch **innerhalb** eines Wortes
    und schaltet die Ziffernbreite ab, die bei Buchstaben nur Lücken erzeugt.

    `af-tile__value` deckelt in beiden Fällen den Überlauf — eine Karte, aus der
    Text heraussteht, ist keine Karte.
    """

    wert = (
        f"font-headline {ABSCHNITT} font-semibold af-text-accent mt-1 af-tile__value"
        if prose
        else f"font-headline {TITEL} font-bold af-text-accent mt-1 "
        "tracking-tight af-num af-tile__value"
    )
    return html.Div(
        [
            html.Div(label.upper(), className=f"font-body {KLEIN} tracking-wider af-text-muted"),
            html.Div(str(value), className=wert),
            html.Div(hint, className=f"{CAPTION} mt-1") if hint else None,
        ],
        className=f"{CARD} p-4 min-w-0",
    )


def kpi_card(
    label: str,
    value: Any,
    *,
    delta: str | None = None,
    direction: str | None = None,
    hint: str | None = None,
) -> html.Div:
    """Kennzahl der Telemetrie — kompakter als `metric_tile`, mit Veränderung.

    *direction* ist `up`, `down` oder `None`. Es färbt nur die Veränderung,
    nicht den Wert: Ob ein steigender Preis gut oder schlecht ist, entscheidet
    die Fragestellung, nicht die Oberfläche.
    """

    tone = f" af-kpi__delta--{direction}" if direction in {"up", "down"} else ""
    return html.Div(
        [
            html.Div(label, className="af-kpi__label"),
            html.Div(str(value), className="af-kpi__value"),
            html.Div(delta, className=f"af-kpi__delta{tone}") if delta else None,
            html.Div(hint, className="af-kpi__hint") if hint else None,
        ],
        className="af-kpi",
    )


def log_line(level: str, text: str, *, tick: int | str | None = None) -> html.Div:
    """Eine Zeile der Konsole, nach Stufe gefärbt.

    Info blau, Warnung gelb, Fehler rot — dieselben Rollen wie in `alert`, nur
    zeilenweise. `muted` trägt, was nur Kontext ist (Fortschrittszeilen).
    """

    stufe = level if level in LOG_LEVELS else "info"
    marker = html.Span(f"{tick:>4}" if tick is not None else "    ", className="af-console__tick")
    return html.Div(
        [marker, html.Span(text, className="min-w-0")],
        className=f"af-console__line af-console__line--{stufe}",
    )


def console(lines: Iterable[Any], *, empty: str = "Noch keine Meldungen.") -> html.Div:
    entries = list(lines)
    if not entries:
        return html.Div(
            html.Div(empty, className="af-console__line af-console__line--muted"),
            className="af-console",
        )
    return html.Div(entries, className="af-console")


def alert(text: Any, kind: str = "info", *, class_name: str = "") -> html.Div:
    """Ein Hinweis mit Symbol.

    **Ohne Lesemaß seit dem 2026-09-12**, und der Weg dorthin ist eine Lehre
    über Zusagen. P3.17 hat dem Rumpf ein `af-mass` gegeben, weil der
    Browser-Wächter hier 98 Zeichen je Zeile gemessen hatte; zugesagt waren 75.
    Die Zusage selbst ist mit der Rücknahme von E3 gefallen — nachgemessen war
    der Deckel nicht zu eng, sondern ausgereizt: Um eine 760 px breite Spalte
    mit höchstens 75 Zeichen zu füllen, müsste Fließtext rund 21 px groß sein.
    Ein Hinweis füllt jetzt den Rahmen, in dem er steht.

    **Was von P3.17 bleibt, ist die Stelle:** Breite gehört an die Komponente
    und nicht an die Aufrufstelle — sonst ist sie eine Frage der Sorgfalt an
    jedem einzelnen Aufruf, und der nächste vergisst sie.
    """

    tone, icon_name = _ALERT_VARIANTS.get(kind, _ALERT_VARIANTS["info"])
    body = dcc.Markdown(text, className="af-md") if isinstance(text, str) else text
    return html.Div(
        [
            icon(icon_name, "text-lg shrink-0 mt-0.5"),
            html.Div(body, className=f"font-body {BESCHRIFTUNG} min-w-0"),
        ],
        className=f"af-alert {tone} flex items-start gap-3 px-4 py-3 {class_name}".strip(),
    )


def empty_state(text: str, *, hint: str | None = None, icon_name: str = "inbox") -> html.Div:
    return html.Div(
        [
            icon(icon_name, "text-3xl af-text-faint"),
            html.P(text, className=f"font-body {BESCHRIFTUNG} af-text-body mt-3"),
            html.P(hint, className=f"{CAPTION} mt-1") if hint else None,
        ],
        className=f"{CARD} flex flex-col items-center justify-center text-center px-6 py-12",
    )


def accordion(title: Any, *children: Any, open: bool = False, badge: str | None = None):
    """Aufklappbarer Block — ersetzt ``st.expander`` ohne eigenen Callback."""

    summary = html.Summary(
        [
            icon("chevron_right", "af-acc__chevron text-lg af-text-faint"),
            html.Span(title, className=f"font-body {BESCHRIFTUNG} font-medium af-text flex-1"),
            (html.Span(badge, className="af-badge") if badge else None),
        ],
        className="af-acc__summary flex items-center gap-2 cursor-pointer select-none px-4 py-3",
    )
    return html.Details(
        [summary, html.Div(list(children), className="px-4 pb-4 pt-1")],
        open=open,
        className=f"af-acc {CARD} mb-2",
    )


def expert(
    *children: Any,
    count: int | None = None,
    title: str = "Feinabstimmung",
    names: str | None = None,
) -> html.Details:
    """Aufklappbarer Block für Parameter, die selten angefasst werden.

    Bewusst schlichter als `accordion`: keine Karte, kleinere Schrift. Der
    Block soll erkennbar zweitrangig sein — die Standardwerte tragen einen
    sinnvollen Lauf, wer hier aufklappt, weiß in der Regel warum.
    """

    heading = title if count is None else f"{title} ({count} Parameter)"
    return html.Details(
        [
            html.Summary(
                [
                    icon("chevron_right", "af-acc__chevron text-base af-text-faint"),
                    html.Span(heading, className=f"font-body {BESCHRIFTUNG} af-text-muted"),
                    (
                        html.Span(names, className=f"{CAPTION} truncate hidden sm:inline")
                        if names
                        else None
                    ),
                ],
                className="af-acc__summary flex items-center gap-2 cursor-pointer select-none py-2",
            ),
            html.Div(list(children), className="pt-3 pb-1 pl-6"),
        ],
        className="af-acc af-expert af-border-t af-border-subtle mt-5",
    )


def explainer(text: str, *, label: str = "Mehr dazu") -> html.Details:
    """Die ausführliche Erklärung eines Parameters, aufklappbar am Feld selbst.

    Bis P1.1 stand sie ausschließlich auf der Dokumentationsseite — also nicht
    dort, wo entschieden wird. Zugeklappt, weil der Kurzhinweis darüber für die
    meisten reicht; wer mehr will, klappt an Ort und Stelle auf, statt die Seite
    zu verlassen.

    **Das Lesemaß, das hier vom 2026-09-03 bis zum 2026-09-12 stand, ist weg**
    (Rücknahme von E3): Der Körper einer Erklärung füllt den Rahmen, in dem er
    steht. Die Beobachtung von damals bleibt trotzdem richtig und gehört
    aufgehoben — aufgefallen war das fehlende Maß an **einer** Erklärung, weil
    P2.0-C den Schalter «Eigene Werte anwenden» nach Schritt 1 verschoben hatte;
    betroffen war aber **jede** Erklärung an jedem Feld. Den Text zu kürzen
    hätte den einen Fall behoben und den Mechanismus stehen lassen.
    """

    return html.Details(
        [
            html.Summary(
                [
                    icon("chevron_right", "af-acc__chevron text-sm af-text-faint"),
                    html.Span(label, className=f"{CAPTION} underline decoration-dotted"),
                ],
                className="af-acc__summary flex items-center gap-1 cursor-pointer select-none py-1",
            ),
            markdown(text, class_name="af-md--tight af-text-body pl-5 pb-1"),
        ],
        className="af-acc mt-1.5",
    )


def note(text: str, *, icon_name: str = "lightbulb") -> html.Div:
    """Erklärender Fließtext ohne Alarmcharakter — Kontext, keine Meldung.

    **Ohne Lesemaß seit dem 2026-09-12** (Rücknahme von E3): Der Text füllt den
    Rahmen, in dem er steht.
    """

    return html.Div(
        [
            icon(icon_name, "text-base af-text-faint shrink-0 mt-0.5"),
            dcc.Markdown(text, className="af-md af-md--tight"),
        ],
        className=f"flex items-start gap-2.5 font-body {BESCHRIFTUNG} af-text-body "
        "af-surface-inset af-bordered rounded px-4 py-3",
    )


def doc_link(slug: str, label: str = "Im Handbuch nachlesen") -> Any:
    """Verweis von einer Einstellung ins zugehörige Kapitel.

    Bewusst leise: Wer weiß, was er tut, soll nicht daran vorbeilesen müssen —
    wer nicht, findet die Erklärung genau dort, wo die Frage entsteht.
    """

    return dcc.Link(
        [label, icon("arrow_forward", "text-xs")],
        href=routing.url(f"doku/{slug}"),
        className=f"af-link inline-flex items-center gap-1 font-body {KLEIN}",
    )


def lede(text: str) -> dcc.Markdown:
    """Einleitungssatz über einem Block — sagt, wozu die Einstellungen dienen.

    **Als Markdown, seit dem 2026-09-11** (P7.1-U1.4, vorgezogen). Die
    Einleitungen sind mit `**fett**` und `` `Pfad` `` geschrieben, gerendert
    wurden sie als `html.P` — im Browser stand «Der `**Name**` steht im letzten
    Schritt» mit Sternchen.

    **Und seit dem 2026-09-12 in Fließtextgröße.** Bis dahin hielt die Rolle
    `af-md--lede` die 14 px des Absatzes, den sie ersetzt hatte — das war beim
    Umstieg auf Markdown richtig (nichts sollte sich optisch ändern) und ist
    als Dauerzustand falsch: Eine Lede leitet Fließtext ein und ist selbst
    welcher. Die Rolle ist damit **weg** statt umgestellt; `.af-md` setzt die
    15 px ohnehin, und eine Regel, die nur eine Größe wiederholt, ist eine
    Stelle zu viel, an der sie auseinanderlaufen kann.
    """

    return dcc.Markdown(text, className="af-md af-md--tight font-body mb-4")


def code_block(text: str, *, max_height: str = "24rem") -> html.Pre:
    return html.Pre(
        text,
        className=f"af-code {KLEIN} p-4 overflow-auto whitespace-pre",
        style={"maxHeight": max_height},
    )


def json_view(payload: Any, *, max_height: str = "24rem") -> html.Pre:
    try:
        text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(payload)
    return code_block(text, max_height=max_height)


def markdown(text: str, *, class_name: str = "") -> dcc.Markdown:
    """Markdown mit den Typo-Regeln aus `assets/dashboard.css`."""

    return dcc.Markdown(text or "", className=f"af-md {class_name}".strip(), link_target="_blank")


def tabs(tab_id: str, items: Iterable[tuple[str, str]], value: str) -> dcc.Tabs:
    """Tab-Leiste im Landingpage-Stil (Unterstrich, Akzent aktiv)."""

    return dcc.Tabs(
        id=tab_id,
        value=value,
        parent_className="af-tabs",
        className="af-tabs__list",
        content_className="af-tabs__content",
        children=[
            dcc.Tab(
                label=label,
                value=val,
                className="af-tab",
                selected_className="af-tab--selected",
            )
            for label, val in items
        ],
    )


def grid(*children: Any, cols: str = "md:grid-cols-2", gap: str = "gap-4") -> html.Div:
    """Ein Raster mit `af-grid` als Trägerklasse.

    `af-grid` setzt `min-width: 0` auf die Kinder. Ohne das schrumpft ein
    Rasterelement nicht unter seinen Inhalt: Ein langes Wort schiebt dann die
    Spalte auf, statt umzubrechen, und der Nachbar wird herausgedrückt. Genau so
    trat «Standard-Ausgangslage» im Ladebildschirm aus seiner Kachel.
    """

    return html.Div(list(children), className=f"af-grid grid grid-cols-1 {cols} {gap}")


def divider(class_name: str = "my-6") -> html.Hr:
    return html.Hr(className=f"af-divider {class_name}")
