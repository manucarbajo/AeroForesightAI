"""Tab «Makro-Parameter»: Faktor-Startzustände und System-Properties.

Properties tragen ihre Zeitverläufe als Regeln («ab Tick X setze/rampe auf
Wert Y»). Die Regelzeilen entstehen dynamisch, deshalb tragen ihre Felder
Pattern-Matching-IDs mit Property und Regelindex.
"""

from __future__ import annotations

from dash import html

from dashboard.config_catalog import (
    PROPERTY_LABELS,
    factor_options_from_file,
    get_editable_property_ids,
    load_config_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c

RULE = "cfg-rule"
RULE_COUNT = "cfg-rule-count"
RULE_HOST = "cfg-rule-host"
PROP_DELETE = "cfg-prop-delete"

PRICE_CATEGORY_OPTIONS = [
    {"label": "Keine Preisbindung", "value": "none"},
    {"label": "Steuer (prozentual auf Ticketpreis)", "value": "tax"},
    {"label": "Gebühr (absoluter EUR-Betrag)", "value": "fee"},
]

_BADGES = {"tax": "Steuer (%)", "fee": "Gebühr (EUR)"}


def rule_id(prop: str, index: int, key: str) -> dict:
    return {"type": RULE, "prop": prop, "index": index, "key": key}


def _factor_block(draft: dict) -> html.Div:
    factors_file = draft.get("factors_file", "factors.json")
    options = factor_options_from_file(factors_file)
    if not options:
        return ui.alert("Keine Faktoren in der gewählten Datei gefunden.", "warning")

    states = draft.get("factor_states") or {}
    fields = []
    for factor_id in sorted(options):
        available = options[factor_id]
        keys = list(available.keys())
        current = states.get(factor_id) or (keys[0] if keys else None)
        fields.append(
            c.select(
                factor_id,
                f"factor_states.{factor_id}",
                current,
                [{"label": f"{key}: {available[key][:60]}", "value": key} for key in keys],
            )
        )

    children: list = [ui.grid(*fields, cols="lg:grid-cols-2")]
    if factors_file != "factors.json":
        children.insert(
            0,
            html.Div(
                ui.button(
                    "Faktoren neu laden",
                    id=c.action_id("reload-factors"),
                    variant="secondary",
                    icon_name="refresh",
                ),
                className="mb-4",
            ),
        )
    return html.Div(children)


def rule_rows(prop_id: str, rules: list, count: int, baseline: float) -> list:
    """Regelzeilen für eine Property aufbauen — im Layout wie im Callback."""

    rows = []
    for index in range(int(count or 0)):
        existing = rules[index] if index < len(rules) else {}
        effect = existing.get("effect") or {}
        kind = effect.get("type", "set")
        cells = [
            ui.field(
                f"Tick #{index + 1}",
                _rule_input(
                    prop_id, index, "tick", int(existing.get("active_from_tick", 1)), 1, 500, 1
                ),
            ),
            ui.field(
                f"Typ #{index + 1}",
                _rule_select(prop_id, index, kind),
            ),
            ui.field(
                f"Wert #{index + 1}",
                _rule_input(
                    prop_id,
                    index,
                    "value",
                    float(effect.get("value", baseline)),
                    None,
                    None,
                    0.0001,
                ),
            ),
        ]
        if kind == "ramp":
            cells.append(
                ui.field(
                    f"Dauer #{index + 1}",
                    _rule_input(
                        prop_id, index, "duration", int(effect.get("duration_ticks", 5)), 1, 100, 1
                    ),
                )
            )
        rows.append(html.Div(ui.grid(*cells, cols="sm:grid-cols-4", gap="gap-3"), className="mb-3"))
    return rows


def _rule_input(prop_id: str, index: int, key: str, value, minimum, maximum, step):
    from dash import dcc

    return dcc.Input(
        id=rule_id(prop_id, index, key),
        type="number",
        value=value,
        min=minimum,
        max=maximum,
        step=step,
        className="af-input",
        debounce=True,
    )


def _rule_select(prop_id: str, index: int, value: str):
    from dash import dcc

    return dcc.Dropdown(
        id=rule_id(prop_id, index, "kind"),
        options=[{"label": "set", "value": "set"}, {"label": "ramp", "value": "ramp"}],
        value=value,
        clearable=False,
        className="af-dropdown",
    )


def _property_card(prop_id: str, edit: dict, badge: str) -> html.Details:
    label = PROPERTY_LABELS.get(prop_id, prop_id)
    is_active = bool(edit.get("is_active", True))
    baseline = float(edit.get("baseline", 0.0))
    rules = edit.get("rules") or []

    body: list = [
        c.check("In dieser Simulation aktiv", f"property_edits.{prop_id}.is_active", is_active)
    ]

    if is_active:
        body.append(
            c.number(
                "Baseline",
                f"property_edits.{prop_id}.baseline",
                baseline,
                step=0.0001,
                class_name="max-w-xs mt-4",
            )
        )
        body.append(
            html.Div(
                [
                    html.P("Regeln", className=f"{ui.H3} mt-6 mb-3"),
                    _rule_count_input(prop_id, len(rules)),
                    html.Div(
                        rule_rows(prop_id, rules, len(rules), baseline),
                        id={"type": RULE_HOST, "prop": prop_id},
                        className="mt-4",
                    ),
                ]
            )
        )
    else:
        body.append(
            ui.alert(
                "Deaktiviert — wird in diesem Lauf nicht angewendet.", "info", class_name="mt-4"
            )
        )
        body.append(
            html.Div(
                ui.button(
                    "Property dauerhaft löschen",
                    id={"type": PROP_DELETE, "prop": prop_id},
                    variant="danger",
                    icon_name="delete",
                ),
                className="mt-4",
            )
        )

    return ui.accordion(label, html.Div(body), open=False, badge=badge or None)


def _add_property_block() -> html.Div:
    return ui.card(
        html.P("Neue Property hinzufügen", className=f"{ui.H3} mb-4"),
        ui.grid(
            ui.field(
                "Property-ID",
                _plain_input(c.free_id("new-prop-id"), "z. B. airport_fee"),
                hint="Muss ein gültiger Python-Bezeichner sein.",
            ),
            ui.field("Anzeigename", _plain_input(c.free_id("new-prop-label"), "z. B. Airport Fee")),
            _price_category_select(),
            cols="lg:grid-cols-3",
        ),
        html.Div(
            ui.button("Property hinzufügen", id=c.action_id("add-property"), icon_name="add"),
            className="mt-4",
        ),
        class_name="mb-6",
    )


def _plain_input(element_id: dict, placeholder: str):
    from dash import dcc

    return dcc.Input(
        id=element_id, type="text", value="", placeholder=placeholder, className="af-input"
    )


def _price_category_select():
    from dash import dcc

    return ui.field(
        "Preiskategorie",
        dcc.Dropdown(
            id=c.free_id("new-prop-category"),
            options=PRICE_CATEGORY_OPTIONS,
            value="none",
            clearable=False,
            className="af-dropdown",
        ),
    )


def _rule_count_input(prop_id: str, count: int):
    from dash import dcc

    return ui.field(
        "Anzahl Regeln",
        dcc.Input(
            id={"type": RULE_COUNT, "prop": prop_id},
            type="number",
            min=0,
            max=8,
            step=1,
            value=count,
            className="af-input",
            debounce=True,
        ),
        class_name="max-w-[10rem]",
    )


def layout(draft: dict) -> html.Div:
    properties_file = draft.get("properties_file", "properties.json")
    payload = load_config_file(properties_file)
    price_components = {
        item["id"]: item["price_component_type"]
        for item in payload.get("system_properties", [])
        if isinstance(item, dict) and item.get("price_component_type")
    }

    edits = draft.get("property_edits") or {}
    overrides_on = (
        bool(draft.get("apply_custom_overrides")) or draft.get("scenario_mode") == "custom"
    )
    base_price = draft.get("base_price")

    cards = []
    for prop_id in get_editable_property_ids(properties_file):
        edit = edits.get(prop_id)
        if edit is None:
            continue
        cards.append(
            _property_card(prop_id, edit, _BADGES.get(price_components.get(prop_id, ""), ""))
        )

    reload_button = (
        html.Div(
            ui.button(
                "Properties aus Datei neu laden",
                id=c.action_id("reload-properties"),
                variant="secondary",
                icon_name="refresh",
            ),
            className="mb-4",
        )
        if properties_file != "properties.json"
        else None
    )

    return html.Div(
        [
            ui.section(
                "Faktoren-Startzustände",
                (
                    None
                    if overrides_on
                    else ui.alert(
                        "Overrides sind deaktiviert — die Startzustände unten werden nicht angewendet.",
                        "warning",
                        class_name="mb-4",
                    )
                ),
                ui.card(_factor_block(draft)),
                subtitle="Startzustände F1–F7 vor dem Lauf.",
            ),
            ui.section(
                "System-Properties (Steuern & Gebühren)",
                ui.card(
                    ui.grid(
                        c.check(
                            "Basispreis überschreiben",
                            "base_price_enabled",
                            base_price is not None,
                        ),
                        (
                            c.number(
                                "Basispreis (EUR)",
                                "base_price",
                                float(base_price) if base_price is not None else 100.0,
                                min=1.0,
                                max=1000.0,
                                step=5.0,
                            )
                            if base_price is not None
                            else html.Div()
                        ),
                        cols="sm:grid-cols-2",
                    ),
                    html.Div(
                        c.check(
                            "Property- und Faktor-Overrides anwenden",
                            "apply_custom_overrides",
                            overrides_on,
                        ),
                        className="mt-4",
                    ),
                    class_name="mb-6",
                ),
                reload_button,
                _add_property_block(),
                html.Div(cards),
            ),
        ]
    )
