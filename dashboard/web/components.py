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
import re
from typing import Any, Iterable

from dash import dcc, html

from dashboard.web import routing

# --- Klassenbausteine ------------------------------------------------------

CARD = "af-card"
CARD_PAD = f"{CARD} p-4 sm:p-6"
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

#: Nach wie vielen Millisekunden eine Ladeanzeige erscheint (P7.3-U3.5). Was
#: schneller fertig ist, zeigt keine — sonst blitzte sie bei jeder Ansicht auf,
#: die in 90 ms steht. Eine Zahl für jeden Bereich, der neu gebaut wird.
LADEANZEIGE_NACH_MS = 300

LABEL = f"block font-body {BESCHRIFTUNG} font-medium af-text-body mb-1"
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
HINT = f"font-body {KLEIN} af-text-muted mt-1"
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
    "af-btn inline-flex items-center justify-center gap-2 px-4 py-3 font-body "
    f"{BESCHRIFTUNG} font-medium cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
)
_BUTTON_VARIANTS = {
    "primary": "af-btn--primary",
    "secondary": "af-btn--secondary",
    "ghost": "af-btn--ghost",
    "danger": "af-btn--danger",
}

#: Die Töne des Hinweisbausteins — Ton → (Klasse, Symbol) (P7.1-U1.4, E5).
#:
#: **`kontext` ist keine Meldung**, sondern erklärender Text neben einer
#: Entscheidung. Die übrigen fünf melden etwas: dass etwas gilt (`info`),
#: gelungen ist (`erfolg`), Aufmerksamkeit braucht (`warnung`), gescheitert ist
#: (`fehler`) oder nur ein Beispiel zeigt (`demo`). Die Klassen tragen weiter
#: ihre alten Namen; umbenannt sind die Töne, nicht das Stylesheet.
HINWEIS_TOENE: dict[str, tuple[str, str]] = {
    "kontext": ("", "lightbulb"),
    "info": ("af-alert--info", "info"),
    "erfolg": ("af-alert--success", "check_circle"),
    "warnung": ("af-alert--warning", "warning"),
    "fehler": ("af-alert--error", "error"),
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
                            (
                                satz(subtitle, class_name=f"{CAPTION} mt-1", klein=True)
                                if subtitle
                                else None
                            ),
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
            satz(subtitle, class_name="font-body af-text-body mt-2") if subtitle else None,
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


#: Was einen Text als Markdown kennzeichnet: Fettung, Code, ein Verweis oder eine
#: Aufzählung. Ohne das bleibt ein Satz ein Satz — und der Baum genau so, wie er
#: war.
_AUSZEICHNUNG = re.compile(r"\*\*|`[^`\n]+`|\[[^\]\n]+\]\([^)\s]+\)|^\s*[-*] \S", re.M)


def satz(text: Any, *, class_name: str = "", element: Any = html.P, klein: bool = False) -> Any:
    """Ein Text, der selbst entscheidet, ob er Markdown ist (P7.1-U1.4).

    **Markdown ist eine Eigenschaft des Textes, nicht die Wahl des Aufrufers.**
    Bis zum 2026-09-11 stand in der Oberfläche `**Name**` mit Sternchen, weil ein
    Aufrufer `html.P` gewählt hatte, wo der Text Markdown war (Q3). Die ersten
    Korrekturen stellten die betroffenen Aufrufe um — und ließen den Mechanismus
    stehen: `section`, `page_heading`, `empty_state`, `kachel` und `status_dot`
    setzten ihren Text weiter wörtlich, gleich was man ihnen gab.

    Ohne Auszeichnung entsteht das Element, das dort immer stand, mit derselben
    Klasse; mit Auszeichnung ein `dcc.Markdown`. *klein* nimmt die Satzgröße
    einer Bildunterschrift (`af-md--caption`), damit ein ausgezeichneter Hinweis
    nicht größer wird als sein schlichter Nachbar. Was kein Text ist, bleibt,
    wie es ist.
    """

    if not isinstance(text, str):
        return text
    if _AUSZEICHNUNG.search(text):
        rolle = "af-md af-md--tight af-md--caption" if klein else "af-md af-md--tight"
        return dcc.Markdown(text, className=f"{rolle} {class_name}".strip())
    return element(text, className=class_name)


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
    füllt den Rahmen. `class_name` bleibt für Abstände (`mb-4`). Ein
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
                className="flex items-start gap-1",
            )
            for text in messages
        ],
        className=f"font-body {KLEIN} af-text-negative mt-1 space-y-1",
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


def status_dot(zustand: str, text: str, *, hint: str | None = None) -> html.Div:
    """Zustandsanzeige für etwas, das erreichbar sein kann — **in drei Zuständen**.

    `bereit`, `pruefen` (der Punkt pulsiert) und `aus`. **Bis P7.4-U4.2 waren es
    zwei**, ein Wahrheitswert: «Ollama wird geprüft …» stand mit demselben
    grauen Punkt da wie «Ollama ist nicht erreichbar», und wer nicht las, sah
    eine Absage, wo noch gefragt wurde. Ein unbekannter Zustand scheitert laut.
    """

    if zustand not in ("bereit", "pruefen", "aus"):
        raise ValueError(f"Unbekannter Zustand {zustand!r} für status_dot.")
    return html.Div(
        [
            html.Span(className=f"af-status__dot mt-1 af-status__dot--{zustand}"),
            html.Div(
                [
                    html.Span(text, className=f"font-body {BESCHRIFTUNG} af-text-body"),
                    satz(hint, class_name=HINT, klein=True) if hint else None,
                ]
            ),
        ],
        className="flex items-start gap-2",
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


#: Die Varianten der Kachel (P7.1-U1.4, Entscheidung E5): eine **Zahl** im
#: großen Satz, ein **Text** im kleineren, und **kompakt** für die Telemetrie,
#: dort mit einer Veränderung daneben.
KACHEL_VARIANTEN = ("zahl", "text", "kompakt")


#: Die Richtung einer Veränderung als Zeichen (P7.5-U5.5). **Zeichen, kein
#: Material-Symbol:** Der geladene Teilsatz hat keine Pfeile nach oben und unten, und
#: ein fehlendes Symbol erschiene als sein Name in Buchstaben.
PFEILE = {"up": "↑ ", "down": "↓ "}


def kachel(
    label: str,
    value: Any,
    hint: str | None = None,
    *,
    variante: str = "zahl",
    delta: str | None = None,
    direction: str | None = None,
) -> html.Div:
    """Beschriftung über einem Wert — **eine** Kachel in drei Varianten (P7.1-U1.4).

    Bis zum 2026-09-13 waren das zwei Bausteine: `metric_tile` (mit einem
    Schalter `prose` für Text) und `kpi_card` für die Telemetrie. Welche
    Gestalt eine Kennzahl bekam, hing daran, welcher Baustein an der Stelle
    gerade importiert wurde. Jetzt ist es eine Variante aus
    :data:`KACHEL_VARIANTEN`, und ein unbekannter Name scheitert laut.

    **`text` ist die Fassung für Werte, die Text sind statt einer Zahl** —
    «Standard-Ausgangslage», «Ohne Sprachmodell». Der große Zahlensatz (Titel,
    fett, Ziffern gleicher Breite) ist für sie zu groß: In einer dreispaltigen
    Reihe trat er aus der Karte heraus und lief in die Nachbarkachel. Die
    Textfassung setzt kleiner, erlaubt den Umbruch **innerhalb** eines Wortes
    und schaltet die Ziffernbreite ab, die bei Buchstaben nur Lücken erzeugt.
    `af-tile__value` deckelt in beiden Fällen den Überlauf — eine Karte, aus der
    Text heraussteht, ist keine Karte.

    **`kompakt` trägt als einzige eine Veränderung** (*delta*, *direction*).
    *direction* ist `up`, `down` oder `None` und färbt nur die Veränderung,
    nicht den Wert: Ob ein steigender Preis gut oder schlecht ist, entscheidet
    die Fragestellung, nicht die Oberfläche. An einer anderen Variante scheitert
    eine Veränderung laut, statt still zu verschwinden.

    **Das Aussehen ist unverändert**; die drei Varianten tragen die Gestalt der
    Bausteine, aus denen sie entstanden sind.
    """

    if variante not in KACHEL_VARIANTEN:
        raise ValueError(
            f"Unbekannte Kachel-Variante {variante!r}; erlaubt sind {KACHEL_VARIANTEN}."
        )
    if variante != "kompakt" and (delta is not None or direction is not None):
        raise ValueError(
            "Eine Veränderung (`delta`, `direction`) trägt nur die Variante «kompakt»."
        )

    if variante == "kompakt":
        tone = f" af-kpi__delta--{direction}" if direction in {"up", "down"} else ""
        # **Die Richtung als Pfeil, nicht als Farbe** (P7.5-U5.5, von Haiko entschieden
        # am 2026-09-15): Gestiegen stand grün, gefallen rot — auch beim Ticketpreis,
        # wo gestiegen meist keine gute Nachricht ist. Die Klassen bleiben, ihre Farbe
        # ist seither neutral.
        pfeil = PFEILE.get(direction or "", "")
        return html.Div(
            [
                html.Div(label, className="af-kpi__label"),
                html.Div(str(value), className="af-kpi__value"),
                html.Div(f"{pfeil}{delta}", className=f"af-kpi__delta{tone}") if delta else None,
                (
                    satz(hint, class_name="af-kpi__hint", element=html.Div, klein=True)
                    if hint
                    else None
                ),
            ],
            className="af-kpi",
        )

    wert = (
        f"font-headline {ABSCHNITT} font-semibold af-text-accent mt-1 af-tile__value"
        if variante == "text"
        else f"font-headline {TITEL} font-bold af-text-accent mt-1 "
        "tracking-tight af-num af-tile__value"
    )
    return html.Div(
        [
            html.Div(label.upper(), className=f"font-body {KLEIN} tracking-wider af-text-muted"),
            html.Div(str(value), className=wert),
            (
                satz(hint, class_name=f"{CAPTION} mt-1", element=html.Div, klein=True)
                if hint
                else None
            ),
        ],
        className=f"{CARD} p-4 min-w-0",
    )


def log_line(level: str, text: str, *, tick: int | str | None = None) -> html.Div:
    """Eine Zeile der Konsole, nach Stufe gefärbt.

    Info blau, Warnung gelb, Fehler rot — dieselben Rollen wie in `hinweis`, nur
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


def hinweis(
    text: Any, ton: str = "info", *, icon_name: str | None = None, class_name: str = ""
) -> html.Div:
    """Ein Hinweis mit Symbol — **der eine** Baustein für Kontext und Meldung (P7.1-U1.4).

    Bis zum 2026-09-13 waren das zwei: `note` für erklärenden Text neben einer
    Entscheidung, `alert` mit fünf Tönen für Meldungen. Welcher gemeint war,
    entschied der Name des Aufrufs; jetzt entscheidet es der **Ton**
    (:data:`HINWEIS_TOENE`). **Ein unbekannter Ton scheitert laut** — `alert`
    fiel still auf «info» zurück, und ein Tippfehler machte aus einer Warnung
    eine Auskunft.

    **Das Aussehen ist unverändert:** `kontext` trägt die Gestalt des alten
    `note`, die übrigen Töne die des alten `alert`. Dass sich Kontext und Info im
    dunklen Design kaum unterscheiden (Audit vom 2026-09-11), ist damit nicht
    behoben, sondern an **eine** Stelle gebracht, an der es sich beheben lässt.

    **Ohne Lesemaß seit dem 2026-09-12** (Rücknahme von E3): Ein Hinweis füllt
    den Rahmen, in dem er steht. Was von P3.17 bleibt, ist die Stelle — Breite
    gehört an den Baustein und nicht an die Aufrufstelle, sonst ist sie eine
    Frage der Sorgfalt an jedem einzelnen Aufruf.

    *text* wird als Markdown gesetzt, wenn es eine Zeichenkette ist; ein
    fertiger Baustein steht, wie er ist.
    """

    if ton not in HINWEIS_TOENE:
        raise ValueError(f"Unbekannter Ton {ton!r}; erlaubt sind {tuple(HINWEIS_TOENE)}.")
    klasse, symbol = HINWEIS_TOENE[ton]
    symbol = icon_name or symbol
    if ton == "kontext":
        rumpf = (
            dcc.Markdown(text, className="af-md af-md--tight") if isinstance(text, str) else text
        )
        return html.Div(
            [icon(symbol, "text-base af-text-faint shrink-0 mt-0.5"), rumpf],
            className=f"flex items-start gap-2 font-body {BESCHRIFTUNG} af-text-body "
            f"af-surface-inset af-bordered rounded px-6 py-3 {class_name}".strip(),
        )
    rumpf = dcc.Markdown(text, className="af-md") if isinstance(text, str) else text
    return html.Div(
        [
            icon(symbol, "text-lg shrink-0 mt-0.5"),
            html.Div(rumpf, className=f"font-body {BESCHRIFTUNG} min-w-0"),
        ],
        className=f"af-alert {klasse} flex items-start gap-3 px-6 py-3 {class_name}".strip(),
    )


def empty_state(text: str, *, hint: str | None = None, icon_name: str) -> html.Div:
    """Ein leerer Zustand: Symbol, Satz und ein Hinweis, wie er sich füllt.

    **Das Symbol ist Pflicht, ohne Vorgabe** (2026-09-13). Die Vorgabe lautete
    «inbox», und dieser Name steckt nicht im Symbol-Teilsatz — gesetzt worden
    wäre er als Wort. Jeder Aufrufer gab ein eigenes Symbol mit, deshalb fiel es
    nicht auf. Eine Vorgabe, die niemand benutzt, ist eine Falle für den
    Ersten, der es tut.
    """

    return html.Div(
        [
            icon(icon_name, "text-3xl af-text-faint"),
            satz(text, class_name=f"font-body {BESCHRIFTUNG} af-text-body mt-3"),
            satz(hint, class_name=f"{CAPTION} mt-1", klein=True) if hint else None,
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
        className="af-acc__summary flex items-center gap-2 cursor-pointer select-none px-6 py-3",
    )
    return html.Details(
        [summary, html.Div(list(children), className="px-6 pb-4 pt-1")],
        open=open,
        className=f"af-acc {CARD} mb-2",
    )


def expert(
    *children: Any,
    count: int | None = None,
    title: str = "Feinabstimmung",
    names: str | None = None,
    einheit: tuple[str, str] = ("Parameter", "Parameter"),
) -> html.Details:
    """Aufklappbarer Block für Parameter, die selten angefasst werden.

    Bewusst schlichter als `accordion`: keine Karte, kleinere Schrift. Der
    Block soll erkennbar zweitrangig sein — die Standardwerte tragen einen
    sinnvollen Lauf, wer hier aufklappt, weiß in der Regel warum.

    **Die Zahl nennt, was sie zählt** (P7.1-U1.4, E5 Punkt 4). Bis zum
    2026-09-13 hing der Baustein an jede Zahl das Wort «Parameter» — auch an
    «Rohdaten ansehen», eine Klappe mit drei Vorschauen und keiner einzigen
    Eingabe. Wer etwas anderes zählt, sagt es mit *einheit* (Einzahl, Mehrzahl).
    **«N Parameter» heißt N Eingaben**, und `tests/test_web_klappen.py` misst das
    im gerenderten Baum.
    """

    if count is None:
        heading = title
    else:
        heading = f"{title} ({count} {einheit[0] if count == 1 else einheit[1]})"
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
        className="af-acc af-expert af-border-t af-border-subtle mt-4",
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
            markdown(text, class_name="af-md--tight af-text-body pl-6 pb-1"),
        ],
        className="af-acc mt-1",
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
