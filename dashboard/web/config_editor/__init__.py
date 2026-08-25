"""Config-Editor: fünf Tabs, ein Store, zwei Callbacks.

Aufbau in einem Satz: jedes Eingabefeld trägt den Pfad, an dem sein Wert im
Draft steht, und ein einziger Callback (`_sync`) schreibt alle sichtbaren
Felder dorthin. Alles, was den Entwurf *strukturell* ändert — Preset
übernehmen, Property anlegen oder löschen, Speichern — läuft über einen
zweiten Callback (`_actions`), der danach den aktiven Tab neu aufbaut.

Diese Zweiteilung ist der Ersatz für Streamlits „Skript läuft bei jeder
Interaktion neu": Werte fließen ohne Neuaufbau, Struktur ändert sich mit.
"""

from __future__ import annotations

from dataclasses import asdict

from dash import ALL, MATCH, Input, Output, State, ctx, html, no_update

from dashboard.config_catalog import (
    PopulationEditState,
    add_custom_property,
    apply_sweep_to_draft,
    default_config_draft,
    delete_custom_property,
    extract_factor_states_from_file,
    extract_population_edits_from_file,
    extract_property_edits_from_file,
    list_sweep_presets,
    save_custom_sweep_preset,
    save_market_feedback_to_file,
    save_population_edits_to_file,
    save_saturation_to_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import (
    compute_mode,
    experiment,
    llm_pipeline,
    macro,
    micro,
    overview,
    save_start,
)
from dashboard.web.config_editor import controls as c
from dashboard.web.state import STORE_ID, draft_from_dict, draft_to_dict

# Reihenfolge ist die Lesereihenfolge: erst das, was jeder einstellen muss,
# dann die Annahmen von grob nach fein, zuletzt Technik und Kontrolle.
TABS = [
    ("Überblick", "overview"),
    ("Rahmenbedingungen", "macro"),
    ("Nachfrage & Preisbildung", "micro"),
    ("Lauf & Ablage", "experiment"),
    ("Technik", "llm"),
    ("Kontrolle", "save"),
]

DEFAULT_TAB = "overview"

_LAYOUTS = {
    "overview": overview.layout,
    "experiment": experiment.layout,
    "macro": macro.layout,
    "micro": micro.layout,
    "llm": llm_pipeline.layout,
    "save": save_start.layout,
}


def tab_layout(tab: str, draft: dict):
    try:
        return _LAYOUTS.get(tab or DEFAULT_TAB, experiment.layout)(draft)
    except Exception as exc:  # noqa: BLE001 - eine kaputte Config soll den Editor nicht sprengen
        return ui.alert(f"Editor konnte nicht aufgebaut werden: {exc}", "error")


def layout(draft: dict) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Alle Änderungen wirken auf den nächsten Lauf. Die «Speichern»-Knöpfe "
                        "in «Mikro-Parameter» schreiben zusätzlich in die Dateien unter `configs/`.",
                        className=f"{ui.CAPTION} max-w-2xl",
                    ),
                    ui.button(
                        "Auf Standard-Config zurücksetzen",
                        id=c.action_id("reset"),
                        variant="secondary",
                        icon_name="restart_alt",
                    ),
                ],
                className="flex items-start justify-between gap-4 flex-wrap mb-4",
            ),
            html.Div(id="cfg-status", className="mb-4"),
            ui.tabs("cfg-tabs", TABS, value=DEFAULT_TAB),
            html.Div(tab_layout(DEFAULT_TAB, draft), id="cfg-tab-content"),
        ],
        className="af-tabs--sub",
    )


# --- Werte einsammeln ------------------------------------------------------


def _rule_entries(inputs_list) -> dict:
    """Regelfelder aus `ctx.inputs_list` nach Property und Index gruppieren."""

    grouped: dict[str, dict[int, dict]] = {}
    for entry in inputs_list or []:
        identifier = entry.get("id") or {}
        prop = identifier.get("prop")
        index = identifier.get("index")
        key = identifier.get("key")
        if prop is None or index is None or key is None:
            continue
        grouped.setdefault(prop, {}).setdefault(int(index), {})[key] = entry.get("value")
    return grouped


def _rules_from_entries(entries: dict[int, dict]) -> list[dict]:
    rules = []
    for index in sorted(entries):
        cells = entries[index]
        kind = cells.get("kind") or "set"
        effect: dict = {"type": kind, "value": float(cells.get("value") or 0.0)}
        if kind == "ramp":
            effect["duration_ticks"] = int(cells.get("duration") or 5)
        rules.append({"active_from_tick": int(cells.get("tick") or 1), "effect": effect})
    return rules


def _normalise(draft: dict) -> dict:
    """Felder nachziehen, die nicht 1:1 einem Eingabefeld entsprechen."""

    # Der Schalter «Basispreis überschreiben» ist kein Draft-Feld: aus ihm folgt
    # nur, ob `base_price` gesetzt ist oder None.
    if "base_price_enabled" in draft:
        if not draft.pop("base_price_enabled"):
            draft["base_price"] = None
        elif draft.get("base_price") is None:
            draft["base_price"] = 100.0

    # Der Rechenmodus ist eine Auswahl über zwei Draft-Felder.
    if compute_mode.FIELD in draft:
        draft = compute_mode.apply(draft, draft.get(compute_mode.FIELD))
    return draft


# --- Callbacks -------------------------------------------------------------


def register_callbacks(app) -> None:
    @app.callback(
        Output("cfg-tab-content", "children"),
        Input("cfg-tabs", "value"),
        Input("cfg-editor-refresh", "data"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _render_tab(tab: str | None, _refresh, draft: dict | None):
        return tab_layout(tab or DEFAULT_TAB, draft or {})

    @app.callback(
        Output(STORE_ID, "data"),
        Input({"type": c.CFG, "field": ALL}, "value"),
        Input({"type": c.CFG_BOOL, "field": ALL}, "value"),
        Input({"type": macro.RULE, "prop": ALL, "index": ALL, "key": ALL}, "value"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _sync(_values, _flags, _rules, draft: dict | None):
        scalars, flags, rules = ctx.inputs_list[0], ctx.inputs_list[1], ctx.inputs_list[2]
        entries = [(entry.get("id"), entry.get("value")) for entry in list(scalars) + list(flags)]
        updated = c.apply_inputs(draft or {}, entries)

        # Regeln werden aus den sichtbaren Zeilen neu aufgebaut — aber nur für
        # Properties, die gerade im DOM stehen. Sonst würde ein Tab-Wechsel die
        # Regeln aller übrigen Properties leeren.
        for prop, cells in _rule_entries(rules).items():
            edits = updated.setdefault("property_edits", {})
            edit = edits.setdefault(prop, {"property_id": prop, "baseline": 0.0, "rules": []})
            edit["rules"] = _rules_from_entries(cells)

        return _normalise(updated)

    @app.callback(
        Output({"type": overview.SUMMARY, "slot": ALL}, "children"),
        Input(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _summaries(draft: dict | None):
        """Klartext-Zusammenfassungen mitziehen, sobald sich etwas ändert."""

        sentence = ui.markdown(overview.summary_sentence(draft or {}))
        return [sentence] * len(ctx.outputs_list)

    @app.callback(
        Output({"type": compute_mode.STATUS, "slot": ALL}, "children"),
        Input("cfg-tab-content", "children"),
        State(STORE_ID, "data"),
    )
    def _llm_status(_content, draft: dict | None):
        """Erreichbarkeit von Ollama nachreichen, sobald ein Tab steht.

        Bewusst nach dem Rendern: Die Abfrage kann mehrere Sekunden dauern —
        unter Windows laeuft `localhost` erst in einen IPv6-Timeout — und so
        lange soll die Seite nicht warten.
        """

        return [compute_mode.availability(draft or {})] * len(ctx.outputs_list)

    @app.callback(
        Output({"type": macro.RULE_HOST, "prop": MATCH}, "children"),
        Input({"type": macro.RULE_COUNT, "prop": MATCH}, "value"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _rule_rows(count, draft: dict | None):
        prop = ctx.triggered_id["prop"]
        edit = ((draft or {}).get("property_edits") or {}).get(prop) or {}
        return macro.rule_rows(
            prop, edit.get("rules") or [], int(count or 0), float(edit.get("baseline") or 0.0)
        )

    @app.callback(
        Output(STORE_ID, "data", allow_duplicate=True),
        Output("cfg-editor-refresh", "data"),
        Output("cfg-status", "children"),
        Input({"type": c.ACTION, "action": ALL}, "n_clicks"),
        Input({"type": macro.PROP_DELETE, "prop": ALL}, "n_clicks"),
        Input({"type": micro.SEGMENT_DELETE, "segment": ALL}, "n_clicks"),
        State(STORE_ID, "data"),
        State({"type": c.FREE, "name": ALL}, "value"),
        State("cfg-editor-refresh", "data"),
        prevent_initial_call=True,
    )
    def _actions(_a, _p, _s, draft: dict | None, _free, refresh):
        trigger = ctx.triggered_id
        if not isinstance(trigger, dict) or not any(
            entry["value"] for entry in ctx.triggered if entry["value"]
        ):
            return no_update, no_update, no_update

        free = ctx.states_list[1]
        data = dict(draft or {})
        version = int(refresh or 0) + 1

        try:
            data, message, kind = _handle_action(trigger, data, free)
        except Exception as exc:  # noqa: BLE001 - Datei- und Validierungsfehler gehören in die UI
            return no_update, no_update, ui.alert(str(exc), "error")

        if message is None:
            return no_update, no_update, no_update
        return data, version, ui.alert(message, kind)


def _handle_action(trigger: dict, data: dict, free: list) -> tuple[dict, str | None, str]:
    """Eine Aktion ausführen und (neuer Draft, Meldung, Meldungsart) zurückgeben."""

    kind = trigger.get("type")

    if kind == macro.PROP_DELETE:
        prop = trigger["prop"]
        delete_custom_property(prop, data.get("properties_file", "properties.json"))
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, f"Property «{prop}» gelöscht.", "success"

    if kind == micro.SEGMENT_DELETE:
        segment = trigger["segment"]
        data["population_edits"] = [
            item for item in (data.get("population_edits") or []) if item.get("id") != segment
        ]
        draft = draft_from_dict(data)
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        return data, f"Segment «{segment}» gelöscht.", "success"

    action = trigger.get("action")

    if action == "reset":
        return (
            draft_to_dict(default_config_draft()),
            "Auf Standard-Config zurückgesetzt.",
            "success",
        )

    if action == "apply-sweep":
        sweeps = list_sweep_presets()
        sweep = next((s for s in sweeps if s.id == data.get("sweep_id")), None)
        if sweep is None:
            return data, "Kein Szenario-Preset ausgewählt.", "warning"
        applied = apply_sweep_to_draft(draft_from_dict(data), sweep)
        return draft_to_dict(applied), f"Parameter von «{sweep.name}» übernommen.", "success"

    if action == "reload-factors":
        data["factor_states"] = extract_factor_states_from_file(
            data.get("factors_file", "factors.json")
        )
        return data, "Faktoren neu geladen.", "success"

    if action == "reload-properties":
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, "Properties neu geladen.", "success"

    if action == "add-property":
        prop_id = c.free_value(free, "new-prop-id").strip()
        if not prop_id or not prop_id.isidentifier():
            return data, "Bitte eine gültige Property-ID angeben (Python-Bezeichner).", "warning"
        add_custom_property(
            prop_id,
            c.free_value(free, "new-prop-label").strip() or prop_id,
            data.get("properties_file", "properties.json"),
            c.free_value(free, "new-prop-category", "none"),
        )
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, f"Property «{prop_id}» angelegt.", "success"

    if action == "save-market-feedback":
        draft = draft_from_dict(data)
        save_market_feedback_to_file(draft.market_feedback_edit, draft.properties_file)
        return data, "Markt-Feedback gespeichert.", "success"

    if action == "add-segment":
        segment_id = c.free_value(free, "new-segment-id").strip()
        if not segment_id or not segment_id.isidentifier():
            return data, "Bitte eine gültige Segment-ID angeben (Python-Bezeichner).", "warning"
        segments = data.get("population_edits") or []
        if any(item.get("id") == segment_id for item in segments):
            return data, f"Ein Segment «{segment_id}» existiert bereits.", "warning"
        if not segments:
            draft = draft_from_dict(data)
            segments = [
                asdict(item) for item in extract_population_edits_from_file(draft.properties_file)
            ]
        segments.insert(
            0,
            asdict(
                PopulationEditState(
                    id=segment_id, type="boolean", prevalence=0.1, saturation_decay=0.2
                )
            ),
        )
        data["population_edits"] = segments
        draft = draft_from_dict(data)
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        return data, f"Segment «{segment_id}» angelegt.", "success"

    if action == "save-population":
        draft = draft_from_dict(data)
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        save_saturation_to_file(draft.saturation_edit, draft.properties_file)
        return data, "Population und Sättigung gespeichert.", "success"

    if action == "save-preset":
        name = c.free_value(free, "preset-name", "mein_szenario").strip()
        draft = draft_from_dict(data)
        draft.simulation_name = name
        path = save_custom_sweep_preset(draft, name)
        data = draft_to_dict(draft)
        return data, f"Gespeichert: `{path}`", "success"

    return data, None, "info"
