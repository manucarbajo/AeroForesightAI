"""Seite «Dokumentation»: was die Parameter bedeuten und wie das Modell rechnet.

Alles, was zum Verstehen nötig ist, aber im Editor im Weg stünde. Der Editor
zeigt je Feld eine Zeile; hier steht die Erklärung im Zusammenhang.
"""

from __future__ import annotations

from dash import html

from dashboard.web import components as ui
from dashboard.web.config_editor import glossary

GRUNDLAGEN = [
    (
        "Ein Tick ist eine Modellrunde",
        "Ticks haben keine Kalenderbedeutung. Sie stehen weder für Quartale noch für Jahre. "
        "Ein längerer Lauf bildet nicht mehr Zeit ab, sondern mehr Gelegenheiten für "
        "Anpassung und Rückkopplung zwischen Preis und Nachfrage.",
    ),
    (
        "Die Zahlen kommen aus dem Rechenmodell",
        "Preise, Buchungsraten und Faktorzustände entstehen deterministisch in Python. Das "
        "Sprachmodell liefert ausschließlich die Deutung dazu. Wer den Rechenmodus umstellt, "
        "ändert also, wie viel erzählt wird, nicht was herauskommt.",
    ),
    (
        "Buchungen entstehen einzeln, nicht als Quote",
        "Für jede simulierte Person wird die Kaufentscheidung einzeln gerechnet, aus "
        "Zahlungsbereitschaft, Preisempfindlichkeit, Umweltbewusstsein und Sättigung. Die "
        "Buchungsrate ist das Ergebnis dieser Entscheidungen, keine Vorgabe.",
    ),
    (
        "Die sieben Faktoren beschreiben die Welt",
        "F1 bis F7 fassen Nachfrage, Regulierung, Technologie, Wirtschaft, Alternativen, "
        "Gesellschaft und Geopolitik in je zwei möglichen Zuständen. Aus ihrer Kombination "
        "bewertet die CIB-Matrix, ob eine Konstellation in sich stimmig ist. Diese Matrix "
        "ist eingefroren und wird nicht aus Läufen abgeleitet, sonst würde der Maßstab aus "
        "dem Messobjekt gewonnen.",
    ),
    (
        "Der Preis hat eine Untergrenze",
        "Unter die Grenzkosten samt Steuern und Gebühren fällt der Ticketpreis nie. Das "
        "erlaubt Verkäufe unter Vollkosten, verbietet aber Dumping.",
    ),
]


def _param_row(path: str) -> html.Div:
    param = glossary.get(path)
    if param is None:
        return html.Div()

    meta = []
    if param.unit:
        meta.append(html.Span(param.unit, className="font-body text-xs text-slate-500"))
    if param.technical:
        meta.append(html.Code(param.technical, className="text-xs text-slate-500"))

    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        param.label, className="font-body text-sm font-medium text-slate-900"
                    ),
                    html.Div(meta, className="flex items-center gap-3 shrink-0") if meta else None,
                ],
                className="flex items-baseline justify-between gap-4 flex-wrap",
            ),
            html.P(
                param.detail or param.short,
                className="font-body text-sm text-slate-600 leading-relaxed mt-1 max-w-3xl",
            ),
        ],
        className="py-4 border-b border-slate-100 last:border-0",
    )


def _group(group: glossary.Group) -> html.Section:
    return ui.section(
        group.title,
        ui.lede(group.intro),
        ui.card(
            html.Div([_param_row(path) for path in group.paths]),
            pad=False,
            class_name="px-5 sm:px-6",
        ),
    )


def layout() -> html.Div:
    return html.Div(
        [
            ui.page_heading(
                "Dokumentation",
                "Wie das Modell rechnet und was die einzelnen Einstellungen bewirken.",
            ),
            ui.section(
                "Grundlagen",
                ui.card(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P(title, className=f"{ui.H3} mb-1"),
                                    html.P(
                                        body,
                                        className="font-body text-sm text-slate-600 "
                                        "leading-relaxed max-w-3xl",
                                    ),
                                ],
                                className="py-4 border-b border-slate-100 last:border-0",
                            )
                            for title, body in GRUNDLAGEN
                        ]
                    ),
                    pad=False,
                    class_name="px-5 sm:px-6",
                ),
            ),
            *[_group(group) for group in glossary.GROUPS],
            ui.section(
                "Weiterführend",
                ui.card(
                    ui.markdown(
                        "Zur CIB-Methodik und ihrer Begründung: `docs/cib_role.md` und "
                        "`docs/cib_rationale.md`. Zu den Rechten der Agenten: "
                        "`docs/agent_profiles.md`. Die Rohwerte aller Einstellungen liegen "
                        "unter `configs/`, die technischen Feldnamen oben verweisen darauf."
                    )
                ),
            ),
        ]
    )


def register_callbacks(app) -> None:
    """Die Seite ist statisch — sie braucht keine."""

    return None
