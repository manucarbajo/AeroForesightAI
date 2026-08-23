"""Tab «Rahmenbedingungen»: Ausgangslage des Systems und exogene Größen.

Zwei Ebenen. Die **Faktoren F1–F7** beschreiben die Welt in groben Zügen —
je Faktor zwei mögliche Zustände, aus `configs/factors.json` samt Namen und
Leitfrage übernommen. Die **Systemgrößen** sind die Zahlen dahinter: CO₂-Abgabe,
SAF-Quote, Ölpreis. Sie haben einen Startwert und können sich im Lauf über
Regeln verändern.
"""

from __future__ import annotations

from dash import dcc, html

from dashboard.config_catalog import (
    PROPERTY_LABELS,
    factor_options_from_file,
    get_editable_property_ids,
    load_config_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor import glossary

RULE = "cfg-rule"
RULE_COUNT = "cfg-rule-count"
RULE_HOST = "cfg-rule-host"
PROP_DELETE = "cfg-prop-delete"

PRICE_CATEGORY_OPTIONS = [
    {"label": "Keine Preiswirkung", "value": "none"},
    {"label": "Steuer — prozentual auf den Ticketpreis", "value": "tax"},
    {"label": "Gebühr — fester Betrag je Ticket", "value": "fee"},
]

_BADGES = {"tax": "wirkt als Steuer", "fee": "wirkt als Gebühr"}

#: Kurzbeschreibungen der Standardgrößen. PROPERTY_LABELS liefert nur den
#: Namen; hier steht, wozu die Größe im Modell dient.
_PROPERTY_EFFECTS = {
    "carbon_tax_level": "Abgabe je Tonne CO₂. Wird auf den Ticketpreis aufgeschlagen und "
    "verteuert das Fliegen gegenüber der Bahn.",
    "saf_mandate_share": "Vorgeschriebener Anteil nachhaltigen Treibstoffs. Höher = höhere "
    "Kosten für die Airline, solange SAF teurer ist als Kerosin.",
    "demand_growth_rate": "Wachstum der Grundnachfrage je Runde, unabhängig vom Preis.",
    "income_index": "Kaufkraft der Bevölkerung. Höher = die Menschen halten steigende "
    "Preise länger aus.",
    "oil_price_index": "Ölpreis als Index. Treibt die Treibstoffkosten der Airline.",
    "fuel_price_change": "Trend der Treibstoffkosten je Runde.",
    "efuel_subsidy": "Förderung synthetischer Kraftstoffe. Dämpft die Mehrkosten aus der "
    "SAF-Quote.",
    "bevoelkerungsentwicklung": "Größe der Bevölkerung, aus der die Nachfrage entsteht.",
}


def rule_id(prop: str, index: int, key: str) -> dict:
    return {"type": RULE, "prop": prop, "index": index, "key": key}


# --- Faktoren --------------------------------------------------------------


def _factor_meta(factors_file: str) -> dict[str, dict]:
    """Namen und Leitfragen der Faktoren aus der Konfigurationsdatei holen."""

    try:
        payload = load_config_file(factors_file)
    except Exception:  # noqa: BLE001 - fehlende Datei darf den Tab nicht sprengen
        return {}
    return {k: v for k, v in payload.items() if isinstance(v, dict) and v.get("name")}


def _factor_block(draft: dict) -> html.Div:
    factors_file = draft.get("factors_file", "factors.json")
    options = factor_options_from_file(factors_file)
    if not options:
        return ui.alert("Keine Faktoren in der gewählten Datei gefunden.", "warning")

    meta = _factor_meta(factors_file)
    states = draft.get("factor_states") or {}

    fields = []
    for factor_id in sorted(options):
        available = options[factor_id]
        keys = list(available.keys())
        current = states.get(factor_id) or (keys[0] if keys else None)
        info = meta.get(factor_id, {})
        name = info.get("name", factor_id)
        question = info.get("description", "")
        fields.append(
            c.select(
                f"factor_states.{factor_id}",
                current,
                [{"label": available[key], "value": key} for key in keys],
                label=f"{factor_id} · {name}",
                hint=question or None,
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


# --- Regeln ----------------------------------------------------------------


def rule_rows(prop_id: str, rules: list, count: int, baseline: float) -> list:
    """Regelzeilen für eine Systemgröße aufbauen — im Layout wie im Callback."""

    rows = []
    for index in range(int(count or 0)):
        existing = rules[index] if index < len(rules) else {}
        effect = existing.get("effect") or {}
        kind = effect.get("type", "set")
        cells = [
            ui.field(
                "ab Runde",
                _rule_input(
                    prop_id, index, "tick", int(existing.get("active_from_tick", 1)), 1, 500, 1
                ),
            ),
            ui.field("Art der Änderung", _rule_select(prop_id, index, kind)),
            ui.field(
                "Zielwert",
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
                    "über … Runden",
                    _rule_input(
                        prop_id, index, "duration", int(effect.get("duration_ticks", 5)), 1, 100, 1
                    ),
                )
            )
        rows.append(
            html.Div(
                ui.grid(*cells, cols="sm:grid-cols-2 lg:grid-cols-4", gap="gap-3"),
                className="mb-3 pb-3 border-b border-slate-100 last:border-0",
            )
        )
    return rows


def _rule_input(prop_id: str, index: int, key: str, value, minimum, maximum, step):
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
    return dcc.Dropdown(
        id=rule_id(prop_id, index, "kind"),
        options=[
            {"label": "springt auf den Wert (set)", "value": "set"},
            {"label": "fährt hoch auf den Wert (ramp)", "value": "ramp"},
        ],
        value=value,
        clearable=False,
        className="af-dropdown",
    )


def _rule_count_input(prop_id: str, count: int):
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


# --- Systemgrößen ----------------------------------------------------------


def _property_card(prop_id: str, edit: dict, badge: str) -> html.Details:
    label = PROPERTY_LABELS.get(prop_id, prop_id)
    is_active = bool(edit.get("is_active", True))
    baseline = float(edit.get("baseline", 0.0))
    rules = edit.get("rules") or []
    effect_text = _PROPERTY_EFFECTS.get(prop_id)

    body: list = []
    if effect_text:
        body.append(html.Div(ui.note(effect_text), className="mb-5"))
    body.append(c.check(f"property_edits.{prop_id}.is_active", is_active, key="property.is_active"))

    if is_active:
        body.append(
            html.Div(
                c.number(
                    f"property_edits.{prop_id}.baseline",
                    baseline,
                    key="property.baseline",
                    step=0.0001,
                    class_name="max-w-xs",
                ),
                className="mt-5",
            )
        )
        rule_param = glossary.get("property.rules")
        body.append(
            html.Div(
                [
                    html.P("Zeitlicher Verlauf", className=f"{ui.H3} mt-6 mb-1"),
                    html.P(
                        rule_param.short if rule_param else "",
                        className=f"{ui.CAPTION} mb-4 max-w-2xl",
                    ),
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
                    "Größe dauerhaft löschen",
                    id={"type": PROP_DELETE, "prop": prop_id},
                    variant="danger",
                    icon_name="delete",
                ),
                className="mt-4",
            )
        )

    return ui.accordion(label, html.Div(body), open=False, badge=badge or None)


def _add_property_block() -> html.Details:
    """Seltene Aktion — gehört nicht auf die erste Ebene."""

    return ui.expert(
        html.P(
            "Etwa eine Flughafengebühr oder eine regionale Abgabe, die es im Standardmodell "
            "noch nicht gibt.",
            className=f"{ui.CAPTION} mb-4",
        ),
        ui.grid(
            ui.field(
                "Kurzname",
                _plain_input(c.free_id("new-prop-id"), "z. B. airport_fee"),
                hint="Kleinbuchstaben und Unterstriche, keine Leerzeichen.",
            ),
            ui.field(
                "Anzeigename",
                _plain_input(c.free_id("new-prop-label"), "z. B. Flughafengebühr"),
                hint="So erscheint die Größe in der Oberfläche.",
            ),
            ui.field(
                "Wirkt auf den Preis als",
                dcc.Dropdown(
                    id=c.free_id("new-prop-category"),
                    options=PRICE_CATEGORY_OPTIONS,
                    value="none",
                    clearable=False,
                    className="af-dropdown",
                ),
                hint="Bestimmt, ob und wie die Größe in den Ticketpreis eingeht.",
            ),
            cols="lg:grid-cols-3",
        ),
        html.Div(
            ui.button("Größe anlegen", id=c.action_id("add-property"), icon_name="add"),
            className="mt-4",
        ),
        title="Eigene Systemgröße anlegen",
    )


def _plain_input(element_id: dict, placeholder: str):
    return dcc.Input(
        id=element_id, type="text", value="", placeholder=placeholder, className="af-input"
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

    cards = [
        _property_card(prop_id, edits[prop_id], _BADGES.get(price_components.get(prop_id, ""), ""))
        for prop_id in get_editable_property_ids(properties_file)
        if prop_id in edits
    ]

    reload_button = (
        html.Div(
            ui.button(
                "Werte aus der Datei neu laden",
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
                "Ausgangslage des Systems",
                ui.lede(
                    "Sieben Faktoren beschreiben die Welt, in der der Lauf startet — je "
                    "Faktor zwei mögliche Zustände. Aus ihrer Kombination bewertet die "
                    "CIB-Matrix später, ob ein Szenario in sich stimmig ist."
                ),
                (
                    None
                    if overrides_on
                    else ui.alert(
                        "Eigene Werte sind abgeschaltet — die Auswahl unten wird nicht angewendet. "
                        "Einschalten unter «Systemgrößen».",
                        "warning",
                        class_name="mb-4",
                    )
                ),
                ui.card(_factor_block(draft)),
                actions=ui.doc_link("faktoren-konzept"),
            ),
            ui.section(
                "Systemgrößen",
                ui.lede(
                    "Politik, Kosten und Konjunktur als Zahlen. Jede Größe hat einen "
                    "Startwert und kann sich über Regeln im Lauf verändern."
                ),
                ui.card(
                    c.check(
                        "apply_custom_overrides",
                        overrides_on,
                    ),
                    html.Div(
                        ui.grid(
                            c.check(
                                "base_price_enabled",
                                base_price is not None,
                                label="Startpreis selbst festlegen",
                                hint="Aus: Der Startpreis kommt aus der Konfigurationsdatei.",
                            ),
                            (
                                c.number(
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
                        className="mt-5",
                    ),
                    class_name="mb-6",
                ),
                reload_button,
                _add_property_block(),
                html.Div(cards),
                actions=ui.doc_link("ref-systemgroessen"),
            ),
        ]
    )
