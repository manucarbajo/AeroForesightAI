"""Seite «Dokumentation» — das Handbuch.

Aufbau wie eine klassische Dokumentation: links die Kapitel mit Suchfeld,
rechts der Text, jede Zwischenüberschrift verlinkbar. Erreichbar über
`/doku` und `/doku/<kapitel>`.

Kapitel kommen aus zwei Quellen. Erklärende Texte liegen als Markdown unter
`docs/handbuch/` und lassen sich ohne Python ändern. Referenzkapitel erzeugt
`docs_reference.py` aus dem Glossar und den Dateien unter `configs/` — sie
können dadurch nicht veralten. Beide liefern Markdown und laufen durch
dieselbe Darstellung.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from dash import Input, Output, dcc, html

from dashboard.web import components as ui
from dashboard.web import routing
from dashboard.web.pages import docs_reference as ref

#: Interner Pfad des Handbuchs, relativ zum Dashboard-Präfix.
ROUTE = "doku"

#: Wo die geschriebenen Kapitel liegen.
HANDBOOK_DIR = Path(__file__).resolve().parents[3] / "docs" / "handbuch"


@dataclass(frozen=True)
class Chapter:
    slug: str
    title: str
    part: str
    summary: str
    markdown: str | None = None
    builder: Callable[[], str] | None = None

    @property
    def href(self) -> str:
        return routing.url(f"{ROUTE}/{self.slug}")

    def source(self) -> str:
        """Markdown-Quelltext des Kapitels."""

        if self.builder is not None:
            return self.builder()
        if self.markdown:
            path = HANDBOOK_DIR / self.markdown
            if path.is_file():
                return path.read_text(encoding="utf-8")
            return f"Kapitel fehlt: `docs/handbuch/{self.markdown}`"
        return ""


CHAPTERS: list[Chapter] = [
    # --- Einstieg ---------------------------------------------------------
    Chapter(
        "was-ist-das",
        "Was diese Plattform tut",
        "Einstieg",
        "Wofür die Simulation gedacht ist und wofür nicht.",
        markdown="was-ist-das.md",
    ),
    Chapter(
        "erste-simulation",
        "Die erste Simulation",
        "Einstieg",
        "In fünf Minuten vom Start zum fertigen Szenario.",
        markdown="erste-simulation.md",
    ),
    Chapter(
        "ergebnisse-lesen",
        "Ergebnisse lesen",
        "Einstieg",
        "In welcher Reihenfolge man die sieben Ansichten liest.",
        markdown="ergebnisse-lesen.md",
    ),
    # --- Konzepte ---------------------------------------------------------
    Chapter(
        "tick-und-lauf",
        "Tick, Lauf und Szenario",
        "Konzepte",
        "Warum ein Tick kein Zeitraum ist.",
        markdown="tick-und-lauf.md",
    ),
    Chapter(
        "zahlen-und-sprache",
        "Zahlen und Sprache",
        "Konzepte",
        "Die Trennlinie zwischen Rechenmodell und Sprachmodell.",
        markdown="zahlen-und-sprache.md",
    ),
    Chapter(
        "akteure",
        "Die drei Akteure",
        "Konzepte",
        "Consumer, Provider, Regulator und ihre Informationsgrenzen.",
        markdown="akteure.md",
    ),
    Chapter(
        "faktoren-konzept",
        "Die sieben Faktoren",
        "Konzepte",
        "Wie die Faktoren die Welt eines Laufs beschreiben.",
        markdown="faktoren.md",
    ),
    Chapter(
        "cib",
        "CIB-Konsistenzprüfung",
        "Konzepte",
        "Wie bewertet wird, ob ein Szenario in sich stimmig ist.",
        markdown="cib.md",
    ),
    Chapter(
        "kaufentscheidung",
        "Wie eine Buchung entsteht",
        "Konzepte",
        "Die Kaufentscheidung einer einzelnen Person.",
        markdown="kaufentscheidung.md",
    ),
    Chapter(
        "preisbildung",
        "Wie der Preis entsteht",
        "Konzepte",
        "Der Regelkreis aus Auslastung, Kosten und Preis.",
        markdown="preisbildung.md",
    ),
    Chapter(
        "saettigung",
        "Sättigung",
        "Konzepte",
        "Warum Nachfrage nicht allein am Preis hängt.",
        markdown="saettigung.md",
    ),
    # --- Bedienung --------------------------------------------------------
    Chapter(
        "lauf-konfigurieren",
        "Einen Lauf konfigurieren",
        "Bedienung",
        "Die Schrittfolge des Einrichtens — und was stattdessen im Modell steht.",
        markdown="lauf-konfigurieren.md",
    ),
    Chapter(
        "lauf-starten",
        "Einen Lauf starten",
        "Bedienung",
        "Start, Fortschritt und die drei möglichen Ausgänge.",
        markdown="lauf-starten.md",
    ),
    Chapter(
        "ergebnisse",
        "Die Ergebnis-Ansichten",
        "Bedienung",
        "Alle sieben Tabs im Einzelnen.",
        markdown="ergebnisse.md",
    ),
    Chapter(
        "abfrage",
        "Läufe abfragen",
        "Bedienung",
        "Was der State Explorer kann und was ihn begrenzt.",
        markdown="abfrage.md",
    ),
    Chapter(
        "presets",
        "Szenarien sichern und vergleichen",
        "Bedienung",
        "Eigene Annahmenwelten ablegen und wiederverwenden.",
        markdown="presets.md",
    ),
    # --- Referenz ---------------------------------------------------------
    Chapter(
        "ref-parameter",
        "Alle Einstellungen",
        "Referenz",
        "Jeder Parameter des Editors mit Einheit und Config-Feld.",
        builder=ref.parameter,
    ),
    Chapter(
        "ref-faktoren",
        "Faktoren F1–F7",
        "Referenz",
        "Alle Faktoren mit beiden Zuständen.",
        builder=ref.faktoren,
    ),
    Chapter(
        "ref-systemgroessen",
        "Systemgrößen",
        "Referenz",
        "Politik, Kosten, Konjunktur mit Einheit und Wertebereich.",
        builder=ref.systemgroessen,
    ),
    Chapter(
        "ref-presets",
        "Szenario-Presets",
        "Referenz",
        "Die hinterlegten Annahmenwelten samt Begründung.",
        builder=ref.presets,
    ),
    Chapter(
        "ref-akteure",
        "Rechte der Akteure",
        "Referenz",
        "Was jeder Agent sieht und vorschlagen darf.",
        builder=ref.akteure,
    ),
    Chapter(
        "ref-ausgaben",
        "Ausgabedateien",
        "Referenz",
        "Was ein Lauf erzeugt und wofür es gut ist.",
        markdown="ref-ausgaben.md",
    ),
    Chapter(
        "ref-config",
        "Konfigurationsdateien",
        "Referenz",
        "Was in welcher Datei unter configs/ steht.",
        markdown="ref-config.md",
    ),
    # --- Praxis -----------------------------------------------------------
    Chapter(
        "fragestellungen",
        "Typische Fragestellungen",
        "Praxis",
        "Konkrete Fragen und der Weg zur Antwort.",
        markdown="fragestellungen.md",
    ),
    Chapter(
        "vergleiche",
        "Läufe vergleichen",
        "Praxis",
        "Zwei Annahmen sauber gegeneinander stellen.",
        markdown="vergleiche.md",
    ),
    Chapter(
        "fehlerbilder",
        "Auffällige Verläufe deuten",
        "Praxis",
        "Was es heißt, wenn Zahlen aus dem Ruder laufen.",
        markdown="fehlerbilder.md",
    ),
    Chapter(
        "grenzen",
        "Grenzen des Modells",
        "Praxis",
        "Wo Ergebnisse nicht mehr tragen.",
        markdown="grenzen.md",
    ),
    # --- Nachschlagen -----------------------------------------------------
    Chapter(
        "glossar",
        "Glossar",
        "Nachschlagen",
        "Begriffe von Auslastung bis Yield Management.",
        markdown="glossar.md",
    ),
]

PARTS = ["Einstieg", "Konzepte", "Bedienung", "Referenz", "Praxis", "Nachschlagen"]

BY_SLUG = {chapter.slug: chapter for chapter in CHAPTERS}
DEFAULT_SLUG = CHAPTERS[0].slug


def slug_from_path(pathname: str | None) -> str:
    """`/app/doku/cib` → `cib`; alles Unbekannte auf das erste Kapitel."""

    relative = routing.relative(pathname)
    if relative.startswith(f"{ROUTE}/"):
        slug = relative[len(ROUTE) + 1 :]
        if slug in BY_SLUG:
            return slug
    return DEFAULT_SLUG


# --- Darstellung -----------------------------------------------------------


def anchor(text: str) -> str:
    """Überschrift in eine ID überführen, die sich verlinken lässt."""

    lowered = text.lower()
    for old, new in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        lowered = lowered.replace(old, new)
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", lowered)).strip("-") or "abschnitt"


def split_sections(markdown: str) -> list[tuple[str | None, str]]:
    """Text an `##`-Überschriften teilen.

    Jeder Abschnitt wird eine eigene `<section>` mit ID. Das ist der Grund für
    die Zerlegung: `dcc.Markdown` vergibt keine IDs, und ohne IDs lässt sich
    keine Stelle im Handbuch verlinken.
    """

    sections: list[tuple[str | None, str]] = []
    title: str | None = None
    body: list[str] = []
    in_code = False

    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith("## "):
            sections.append((title, "\n".join(body).strip()))
            title = line[3:].strip()
            body = []
            continue
        body.append(line)

    sections.append((title, "\n".join(body).strip()))
    return [item for item in sections if item[0] or item[1]]


def with_prefix(markdown: str) -> str:
    """Querverweise auf das Dashboard-Präfix umschreiben.

    In den Markdown-Dateien steht `](/doku/grenzen)` — kurz, lesbar und auch
    auf GitHub sinnvoll. Im Browser muss daraus `](/app/doku/grenzen)` werden.
    """

    return markdown.replace(f"](/{ROUTE}/", f"]({routing.url(ROUTE)}/")


def render(chapter: Chapter) -> html.Div:
    sections = split_sections(with_prefix(chapter.source()))
    blocks: list = []
    for title, body in sections:
        children: list = []
        if title:
            children.append(html.H2(title, className=f"{ui.H2} mb-3 scroll-mt-24"))
        if body:
            children.append(ui.markdown(body))
        # `id` nur setzen, wenn es eine Überschrift gibt — Dash lehnt `id=None`
        # ab, und der Vorspann eines Kapitels braucht kein Sprungziel.
        extra = {"id": anchor(title)} if title else {}
        blocks.append(html.Section(children, className="mb-8", **extra))

    return html.Div(
        [
            html.P(
                chapter.part.upper(), className=f"font-body {ui.KLEIN} tracking-wider af-text-muted"
            ),
            html.H1(chapter.title, className=f"{ui.H1} mt-1"),
            html.P(chapter.summary, className="font-body af-text-body mt-2 mb-8"),
            *blocks,
            _chapter_footer(chapter),
        ],
        className="af-breite-inhalt",
    )


def _chapter_footer(chapter: Chapter) -> html.Div:
    """Blättern zum vorigen und nächsten Kapitel."""

    index = next((i for i, item in enumerate(CHAPTERS) if item.slug == chapter.slug), 0)
    previous = CHAPTERS[index - 1] if index > 0 else None
    following = CHAPTERS[index + 1] if index + 1 < len(CHAPTERS) else None

    def link(target: Chapter | None, label: str, align: str):
        if target is None:
            return html.Div()
        return dcc.Link(
            [
                html.Span(label, className=f"{ui.CAPTION} block"),
                html.Span(
                    target.title,
                    className=f"font-body {ui.BESCHRIFTUNG} font-medium af-text-accent",
                ),
            ],
            href=target.href,
            className=f"block {align} hover:opacity-70 transition-opacity",
        )

    return html.Div(
        [link(previous, "Zurück", "text-left"), link(following, "Weiter", "text-right")],
        className="flex items-start justify-between gap-6 af-border-t pt-6 mt-12",
    )


# --- Navigation ------------------------------------------------------------


def _search_index() -> dict[str, str]:
    """Kleingeschriebener Volltext je Kapitel, für die Suche."""

    index = {}
    for chapter in CHAPTERS:
        try:
            body = chapter.source()
        except Exception:  # noqa: BLE001 - ein kaputtes Kapitel darf die Suche nicht kippen
            body = ""
        index[chapter.slug] = f"{chapter.title} {chapter.summary} {body}".lower()
    return index


def navigation(active_slug: str, query: str = "") -> html.Div:
    needle = (query or "").strip().lower()
    if needle:
        index = _search_index()
        visible = {slug for slug, text in index.items() if needle in text}
    else:
        visible = set(BY_SLUG)

    blocks: list = []
    for part in PARTS:
        chapters = [c for c in CHAPTERS if c.part == part and c.slug in visible]
        if not chapters:
            continue
        blocks.append(
            html.P(
                part.upper(),
                className=f"font-body {ui.KLEIN} tracking-wider af-text-faint mt-6 mb-2 first:mt-0",
            )
        )
        blocks.append(
            html.Ul(
                [
                    html.Li(
                        dcc.Link(
                            chapter.title,
                            href=chapter.href,
                            className=(
                                f"block py-1 font-body {ui.BESCHRIFTUNG} border-l-2 pl-3 -ml-px "
                                + (
                                    "af-docs__link af-docs__link--active"
                                    if chapter.slug == active_slug
                                    else "af-docs__link"
                                )
                            ),
                        )
                    )
                    for chapter in chapters
                ],
                className="af-docs__list",
            )
        )

    if not blocks:
        blocks.append(
            html.P(
                f"Nichts gefunden zu «{query}».",
                className=f"font-body {ui.BESCHRIFTUNG} af-text-muted py-2",
            )
        )
    return html.Div(blocks)


def layout() -> html.Div:
    return html.Div(
        [
            html.Aside(
                [
                    dcc.Input(
                        id="docs-search",
                        type="search",
                        placeholder="Im Handbuch suchen …",
                        value="",
                        className="af-input mb-2",
                    ),
                    html.Div(navigation(DEFAULT_SLUG), id="docs-nav"),
                ],
                className="af-docs__nav",
            ),
            html.Div(render(BY_SLUG[DEFAULT_SLUG]), id="docs-content", className="min-w-0"),
        ],
        # `af-pane` gibt dem Handbuch denselben Innenabstand wie den übrigen
        # Viewport-Inhalten — es scrollt jetzt in der mittleren Zone, nicht
        # mehr als Seite.
        className="af-docs af-pane",
    )


def register_callbacks(app) -> None:
    @app.callback(
        Output("docs-content", "children"),
        Input("url", "pathname"),
        prevent_initial_call=True,
    )
    def _chapter(pathname: str | None):
        return render(BY_SLUG[slug_from_path(pathname)])

    @app.callback(
        Output("docs-nav", "children"),
        Input("url", "pathname"),
        Input("docs-search", "value"),
        prevent_initial_call=True,
    )
    def _nav(pathname: str | None, query: str | None):
        return navigation(slug_from_path(pathname), query or "")
