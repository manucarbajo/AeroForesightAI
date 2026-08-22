"""Tab «Mikro-Parameter & Bevölkerung».

Markt-Rückkopplung, Sättigung, die Segmente der Population und die
Verteilungen ihrer Eigenschaften. Die «Speichern»-Knöpfe schreiben direkt in
`configs/properties.json` — sie wirken also über den einzelnen Lauf hinaus.
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

SEGMENT_DELETE = "cfg-segment-delete"

DISTRIBUTIONS = ["normal", "beta", "lognormal", "uniform"]

_DISTRIBUTION_LABELS = {
    "wtp_eur": "Zahlungsbereitschaft (WTP in Euro)",
    "environmental_awareness": "Umweltbewusstsein (0–1)",
}

_MODIFIERS = [
    ("wtp_multiplier", "WTP-Multiplikator", 1.0),
    ("base_income_delta", "Einkommen-Delta", 0.0),
    ("price_sensitivity_delta", "Preissensibilität-Delta", 0.0),
    ("substitution_readiness_multiplier", "Bahn-Wechselbereitschaft", 1.0),
]


def _market_feedback(draft: dict) -> html.Div:
    feedback = draft.get("market_feedback_edit") or {}
    prefix = "market_feedback_edit"
    return ui.card(
        c.check("Markt-Feedback aktiv", f"{prefix}.enabled", feedback.get("enabled", True)),
        html.Div(
            ui.grid(
                c.number(
                    "Ziel-Buchungsrate",
                    f"{prefix}.target_booking_rate",
                    float(feedback.get("target_booking_rate", 0.37)),
                    min=0.05,
                    max=1.0,
                    step=0.01,
                ),
                c.number(
                    "Grenzkosten-Anteil",
                    f"{prefix}.marginal_cost_fraction",
                    float(feedback.get("marginal_cost_fraction", 0.33)),
                    min=0.05,
                    max=1.0,
                    step=0.01,
                ),
                c.number(
                    "Markup-Anpassung / Tick",
                    f"{prefix}.markup_adjustment_per_tick",
                    float(feedback.get("markup_adjustment_per_tick", 0.08)),
                    min=0.01,
                    max=0.5,
                    step=0.01,
                ),
                c.number(
                    "Dämpfung",
                    f"{prefix}.damping",
                    float(feedback.get("damping", 0.85)),
                    min=0.1,
                    max=1.0,
                    step=0.05,
                ),
                c.number(
                    "Max. Preisänderung / Tick",
                    f"{prefix}.max_price_change_fraction",
                    float(feedback.get("max_price_change_fraction", 0.08)),
                    min=0.01,
                    max=0.5,
                    step=0.01,
                ),
                c.number(
                    "Booking-Gewicht",
                    f"{prefix}.booking_weight",
                    float(feedback.get("booking_weight", 0.6)),
                    min=0.0,
                    max=1.0,
                    step=0.05,
                ),
                cols="md:grid-cols-2 xl:grid-cols-3",
            ),
            className="mt-4",
        ),
        html.Div(
            ui.button(
                "Markt-Feedback speichern",
                id=c.action_id("save-market-feedback"),
                variant="secondary",
                icon_name="save",
            ),
            className="mt-5",
        ),
    )


def _saturation(draft: dict) -> html.Div:
    saturation = draft.get("saturation_edit") or {}
    return ui.card(
        ui.grid(
            c.number(
                "Sättigungs-Anstieg bei Buchung",
                "saturation_edit.booking_increase",
                float(saturation.get("booking_increase", 0.6)),
                min=0.0,
                max=1.0,
                step=0.05,
            ),
            c.number(
                "Logit-Penalty-Faktor",
                "saturation_edit.utility_penalty_factor",
                float(saturation.get("utility_penalty_factor", 1.0)),
                min=0.0,
                max=3.0,
                step=0.1,
            ),
            cols="sm:grid-cols-2",
        )
    )


def _segment_card(index: int, segment: dict) -> html.Div:
    segment_id = segment.get("id", "")
    label = segment_id.replace("_", " ").title()
    path = f"population_edits.{index}"
    modifiers = segment.get("modifiers") or {}
    return ui.card(
        html.Div(
            [
                html.P(label, className=ui.H3),
                ui.button(
                    "Entfernen",
                    id={"type": SEGMENT_DELETE, "segment": segment_id},
                    variant="danger",
                    icon_name="delete",
                    className="!px-3 !py-1.5 text-xs",
                ),
            ],
            className="flex items-start justify-between gap-3 mb-4",
        ),
        c.slider(
            "Anteil (Prevalence)",
            f"{path}.prevalence",
            float(segment.get("prevalence") or 0.0),
            hint=(
                f"Exklusive Gruppe «{segment['exclusive_group']}»: nur ein Segment dieser "
                "Gruppe pro Person."
                if segment.get("exclusive_group")
                else None
            ),
        ),
        html.Div(
            c.slider(
                "Erholung pro Tick (Decay)",
                f"{path}.saturation_decay",
                float(
                    segment.get("saturation_decay")
                    if segment.get("saturation_decay") is not None
                    else 0.2
                ),
                hint="Wie viel Sättigung pro Zeiteinheit abgebaut wird (0.0 = nie, 1.0 = sofort).",
            ),
            className="mt-5",
        ),
        ui.accordion(
            "Modifikatoren",
            ui.grid(
                *[
                    c.number(
                        title,
                        f"{path}.modifiers.{key}",
                        float(modifiers.get(key, fallback)),
                        step=0.05,
                    )
                    for key, title, fallback in _MODIFIERS
                ],
                cols="sm:grid-cols-2",
            ),
            open=False,
        ),
        class_name="h-full",
    )


def _distribution_card(index: int, segment: dict) -> html.Details:
    segment_id = segment.get("id", "")
    label = _DISTRIBUTION_LABELS.get(segment_id, segment_id.replace("_", " ").title())
    path = f"population_edits.{index}"
    kind = segment.get("distribution") if segment.get("distribution") in DISTRIBUTIONS else "normal"

    if kind == "beta":
        fields = [
            c.number("Alpha", f"{path}.alpha", float(segment.get("alpha") or 2.0), step=0.01),
            c.number("Beta", f"{path}.beta", float(segment.get("beta") or 5.0), step=0.01),
        ]
    else:
        fields = [
            c.number("Mittelwert", f"{path}.mean", float(segment.get("mean") or 0.0), step=0.01),
            c.number("Std Dev", f"{path}.std_dev", float(segment.get("std_dev") or 1.0), step=0.01),
        ]
    fields += [
        c.number("Min", f"{path}.min_value", float(segment.get("min_value") or 0.0), step=0.01),
        c.number("Max", f"{path}.max_value", float(segment.get("max_value") or 1.0), step=0.01),
    ]

    return ui.accordion(
        label,
        c.select(
            "Verteilungstyp",
            f"{path}.distribution",
            kind,
            [{"label": name, "value": name} for name in DISTRIBUTIONS],
            class_name="max-w-xs mb-4",
        ),
        ui.grid(*fields, cols="sm:grid-cols-2 lg:grid-cols-4"),
        open=False,
    )


def _add_segment_block() -> html.Div:
    return ui.card(
        html.P("Neues Segment hinzufügen", className=f"{ui.H3} mb-4"),
        html.Div(
            [
                ui.field(
                    "Segment-ID",
                    dcc.Input(
                        id=c.free_id("new-segment-id"),
                        type="text",
                        value="",
                        placeholder="z. B. frequent_flyer",
                        className="af-input",
                    ),
                    class_name="flex-1 min-w-[16rem]",
                ),
                html.Div(
                    ui.button("Segment hinzufügen", id=c.action_id("add-segment"), icon_name="add"),
                    className="pt-7",
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
                "Yield / Markt-Feedback",
                _market_feedback(draft),
                subtitle="Wie stark der Anbieter Preis und Marge an die Buchungslage anpasst.",
            ),
            ui.section(
                "Sättigung (global)",
                _saturation(draft),
                subtitle="Wie stark eine Buchung die weitere Buchungsneigung dämpft.",
            ),
            ui.section(
                "Segmente",
                _add_segment_block(),
                (
                    ui.grid(
                        *[_segment_card(i, s) for i, s in booleans],
                        cols="lg:grid-cols-2 2xl:grid-cols-3",
                    )
                    if booleans
                    else ui.alert("Keine Boolean-Segmente definiert.", "info")
                ),
            ),
            ui.section(
                "Eigenschaften-Verteilungen",
                (
                    html.Div([_distribution_card(i, s) for i, s in distributions])
                    if distributions
                    else ui.alert("Keine Verteilungen definiert.", "info")
                ),
            ),
            html.Div(
                ui.button(
                    "Änderungen an Population speichern",
                    id=c.action_id("save-population"),
                    icon_name="save",
                ),
                className="mt-2",
            ),
        ]
    )
