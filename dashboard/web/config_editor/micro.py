"""Tab «Nachfrage & Preisbildung».

Zwei Fragen: Wie reagiert die Airline auf die Auslastung, und wer sind die
Menschen, die buchen? Je Block steht vorn die Stellschraube, die die Wirkung
bestimmt; die Feinabstimmung liegt aufklappbar darunter.

Die «Speichern»-Knöpfe schreiben direkt in `configs/properties.json` — sie
wirken also über den einzelnen Lauf hinaus. Seit P1.9-W3.2 stehen sie deshalb
hinter einer Rückfrage (`controls.write_action`), und ihre Reichweite steht als
Hinweis darunter. Dieses Modul wird seit W3.1 im Bereich «Modell» gerendert,
nicht mehr in der Schrittfolge.
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

SEGMENT_DELETE = "cfg-segment-delete"

DISTRIBUTIONS = ["normal", "beta", "lognormal", "uniform"]

_DISTRIBUTION_LABELS = {
    "wtp_eur": "Zahlungsbereitschaft (in Euro)",
    "environmental_awareness": "Umweltbewusstsein",
}

_MODIFIERS = [
    ("wtp_multiplier", 1.0),
    ("base_income_delta", 0.0),
    ("price_sensitivity_delta", 0.0),
    ("substitution_readiness_multiplier", 1.0),
]

_FEEDBACK_FINE = [
    ("marginal_cost_fraction", 0.33, 0.05, 1.0, 0.01),
    ("markup_adjustment_per_tick", 0.08, 0.01, 0.5, 0.01),
    ("damping", 0.85, 0.1, 1.0, 0.05),
    ("max_price_change_fraction", 0.08, 0.01, 0.5, 0.01),
    ("booking_weight", 0.6, 0.0, 1.0, 0.05),
]


def _market_feedback(draft: dict) -> html.Div:
    feedback = draft.get("market_feedback_edit") or {}
    prefix = "market_feedback_edit"

    return ui.card(
        c.check(f"{prefix}.enabled", feedback.get("enabled", True)),
        html.Div(
            c.number(
                f"{prefix}.target_booking_rate",
                float(feedback.get("target_booking_rate", 0.37)),
                min=0.05,
                max=1.0,
                step=0.01,
                class_name="max-w-sm",
            ),
            className="mt-5",
        ),
        ui.expert(
            ui.grid(
                *[
                    c.number(
                        f"{prefix}.{name}",
                        float(feedback.get(name, default)),
                        min=low,
                        max=high,
                        step=step,
                    )
                    for name, default, low, high, step in _FEEDBACK_FINE
                ],
                cols="md:grid-cols-2 xl:grid-cols-3",
            ),
            count=len(_FEEDBACK_FINE),
            names="Preisuntergrenze, Reaktionsstärke, Dämpfung, Preisdeckel, Kopplung",
        ),
        c.write_action(
            "save-market-feedback",
            "Als Standard speichern",
            frage="Das Preisverhalten wird als neuer Standard in die "
            "Konfigurationsdatei geschrieben.",
            icon_name="save",
            class_name="mt-5",
        ),
    )


def _saturation(draft: dict) -> html.Div:
    saturation = draft.get("saturation_edit") or {}
    return ui.card(
        c.number(
            "saturation_edit.booking_increase",
            float(saturation.get("booking_increase", 0.6)),
            min=0.0,
            max=1.0,
            step=0.05,
            class_name="max-w-sm",
        ),
        ui.expert(
            c.number(
                "saturation_edit.utility_penalty_factor",
                float(saturation.get("utility_penalty_factor", 1.0)),
                min=0.0,
                max=3.0,
                step=0.1,
                class_name="max-w-sm",
            ),
            count=1,
            names="Wirkung auf die Buchungsneigung",
        ),
    )


def _exclusive_hint(segment: dict) -> str | None:
    group = segment.get("exclusive_group")
    if not group:
        return None
    return f"Exklusive Gruppe «{group}» — pro Person kann nur ein Segment dieser Gruppe zutreffen."


def _segment_card(index: int, segment: dict) -> html.Div:
    segment_id = segment.get("id", "")
    label = segment_id.replace("_", " ").title()
    path = f"population_edits.{index}"
    modifiers = segment.get("modifiers") or {}
    decay = segment.get("saturation_decay")

    return ui.card(
        html.Div(
            [
                html.Div(
                    [
                        html.P(label, className=ui.H3),
                        html.Code(segment_id, className=ui.CAPTION),
                    ]
                ),
                c.write_action(
                    "segment-delete",
                    "Entfernen",
                    frage=f"Das Segment «{label}» wird aus der Konfigurationsdatei entfernt.",
                    variant="danger",
                    icon_name="delete",
                    identifier={"type": SEGMENT_DELETE, "segment": segment_id},
                ),
            ],
            className="flex items-start justify-between gap-3 mb-4",
        ),
        c.slider(
            f"{path}.prevalence",
            float(segment.get("prevalence") or 0.0),
            key="segment.prevalence",
            hint=_exclusive_hint(segment),
        ),
        ui.expert(
            c.slider(
                f"{path}.saturation_decay",
                float(decay if decay is not None else 0.2),
                key="segment.saturation_decay",
            ),
            html.Div(
                ui.grid(
                    *[
                        c.number(
                            f"{path}.modifiers.{name}",
                            float(modifiers.get(name, fallback)),
                            key=f"segment.{name}",
                            step=0.05,
                        )
                        for name, fallback in _MODIFIERS
                    ],
                    cols="sm:grid-cols-2",
                ),
                className="mt-5",
            ),
            count=1 + len(_MODIFIERS),
            title="Verhalten dieses Segments",
        ),
        class_name="h-full",
    )


def _distribution_card(index: int, segment: dict) -> html.Details:
    segment_id = segment.get("id", "")
    label = _DISTRIBUTION_LABELS.get(segment_id, segment_id.replace("_", " ").title())
    path = f"population_edits.{index}"
    kind = segment.get("distribution") if segment.get("distribution") in DISTRIBUTIONS else "normal"

    if kind == "beta":
        shape = [
            c.number(f"{path}.alpha", float(segment.get("alpha") or 2.0), label="Alpha", step=0.01),
            c.number(f"{path}.beta", float(segment.get("beta") or 5.0), label="Beta", step=0.01),
        ]
    else:
        shape = [
            c.number(
                f"{path}.mean",
                float(segment.get("mean") or 0.0),
                label="Mittelwert",
                hint="Der typische Wert in der Bevölkerung.",
                step=0.01,
            ),
            c.number(
                f"{path}.std_dev",
                float(segment.get("std_dev") or 1.0),
                label="Streuung",
                hint="Wie weit die Menschen um diesen Wert auseinanderliegen.",
                step=0.01,
            ),
        ]
    bounds = [
        c.number(
            f"{path}.min_value",
            float(segment.get("min_value") or 0.0),
            label="Minimum",
            hint="Werte darunter kommen nicht vor.",
            step=0.01,
        ),
        c.number(
            f"{path}.max_value",
            float(segment.get("max_value") or 1.0),
            label="Maximum",
            hint="Werte darüber kommen nicht vor.",
            step=0.01,
        ),
    ]

    return ui.accordion(
        label,
        c.select(
            f"{path}.distribution",
            kind,
            [{"label": name, "value": name} for name in DISTRIBUTIONS],
            key="distribution.kind",
            class_name="max-w-xs mb-5",
        ),
        ui.grid(*shape, *bounds, cols="sm:grid-cols-2 lg:grid-cols-4"),
        open=False,
    )


def _add_segment_block() -> html.Div:
    return ui.card(
        html.P("Neues Segment anlegen", className=f"{ui.H3} mb-1"),
        html.P(
            "Ein Segment ist eine Personengruppe mit eigenem Verhalten — etwa Vielflieger "
            "oder preissensible Urlauber.",
            className=f"{ui.CAPTION} mb-4",
        ),
        html.Div(
            [
                ui.field(
                    "Kurzname",
                    dcc.Input(
                        id=c.free_id("new-segment-id"),
                        type="text",
                        value="",
                        placeholder="z. B. frequent_flyer",
                        className="af-input",
                    ),
                    hint="Kleinbuchstaben und Unterstriche, keine Leerzeichen.",
                    class_name="flex-1 min-w-[16rem]",
                ),
                c.write_action(
                    "add-segment",
                    "Segment anlegen",
                    frage="Das neue Segment wird in die Konfigurationsdatei geschrieben.",
                    icon_name="add",
                    variant="primary",
                    class_name="pt-7",
                ),
            ],
            className="flex items-start gap-4 flex-wrap",
        ),
        class_name="mb-6",
    )


def layout(draft: dict) -> html.Div:
    segments = draft.get("population_edits") or []
    booleans = [(i, s) for i, s in enumerate(segments) if s.get("type") == "boolean"]
    distributions = [(i, s) for i, s in enumerate(segments) if s.get("type") == "distribution"]

    return html.Div(
        [
            ui.section(
                "Preisverhalten der Airline",
                ui.lede(
                    "Wie der Anbieter auf die beobachtete Auslastung reagiert. Das ist der "
                    "Regelkreis, der Preis und Nachfrage im Lauf aneinander koppelt."
                ),
                _market_feedback(draft),
                actions=ui.doc_link("preisbildung"),
            ),
            ui.section(
                "Sättigung",
                ui.lede(
                    "Wer gerade geflogen ist, bucht so schnell nicht wieder. Diese beiden "
                    "Werte bestimmen, wie stark dieser Effekt die Nachfrage bremst."
                ),
                _saturation(draft),
                actions=ui.doc_link("saettigung"),
            ),
            ui.section(
                "Wer fliegt?",
                ui.lede(
                    "Die Bevölkerung besteht aus Segmenten mit eigenem Verhalten. Der Anteil "
                    "bestimmt, wie stark ein Segment das Gesamtergebnis prägt."
                ),
                _add_segment_block(),
                (
                    ui.grid(
                        *[_segment_card(i, s) for i, s in booleans],
                        cols="lg:grid-cols-2 2xl:grid-cols-3",
                    )
                    if booleans
                    else ui.alert("Keine Segmente definiert.", "info")
                ),
                actions=ui.doc_link("kaufentscheidung"),
            ),
            ui.section(
                "Streuung der Eigenschaften",
                ui.lede(
                    "Zahlungsbereitschaft und Umweltbewusstsein sind nicht bei allen gleich. "
                    "Hier legen Sie fest, wie breit sie über die Bevölkerung streuen."
                ),
                (
                    html.Div([_distribution_card(i, s) for i, s in distributions])
                    if distributions
                    else ui.alert("Keine Verteilungen definiert.", "info")
                ),
            ),
            c.write_action(
                "save-population",
                "Bevölkerung als Standard speichern",
                frage="Bevölkerung und Sättigung werden als neuer Standard in die "
                "Konfigurationsdatei geschrieben.",
                icon_name="save",
                variant="primary",
                class_name="mt-2",
            ),
        ]
    )
