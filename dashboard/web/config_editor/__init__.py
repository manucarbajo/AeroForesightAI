"""Die Oberfläche zum Konfigurieren eines Laufs — seit P1.7 eine Schrittfolge.

Die acht Schritte stehen in `wizard.py`; die ersten drei sind die Entscheidungen
aus P1.1 (`start_flow`), die vier danach sind die Bereiche, die bis P1.7 Reiter
waren (`macro`, `micro`, `experiment`, `llm_pipeline`), und der letzte ist
«Prüfen & Starten». Alle schreiben in denselben Store.

Aufbau in einem Satz: jedes Eingabefeld trägt den Pfad, an dem sein Wert im
Draft steht, und ein einziger Callback (`_sync`) schreibt alle **sichtbaren**
Felder dorthin. Alles, was den Entwurf *strukturell* ändert — Preset übernehmen,
Property anlegen oder löschen, Speichern — läuft über einen zweiten Callback
(`_actions`), der danach den offenen Schritt neu aufbaut.

Diese Zweiteilung ist der Ersatz für Streamlits „Skript läuft bei jeder
Interaktion neu": Werte fließen ohne Neuaufbau, Struktur ändert sich mit.

**Ein Feld darf nur an einer Stelle stehen.** Deshalb steht immer nur der offene
Schritt im DOM — dieselbe Feld-ID zweimal ist für Dash ein Laufzeitfehler.
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
    start_flow,
    wizard,
)
from dashboard.web.config_editor import controls as c
from dashboard.web.pages import model_editor
from dashboard.web.state import STORE_ID, draft_from_dict, draft_to_dict

# Die vier Bereiche, die bis P1.7 Reiter waren und jetzt die Schritte vier bis
# sieben sind. Reihenfolge ist die Lesereihenfolge: die Annahmen von grob nach
# fein, dann Organisatorisches, zuletzt Technik. Der Name `TABS` bleibt, weil
# mehrere Tests über ihn laufen; die Reiterleiste selbst gibt es nicht mehr.
TABS = [
    ("Rahmenbedingungen", "macro"),
    ("Nachfrage & Preisbildung", "micro"),
    ("Lauf & Ablage", "experiment"),
    ("Technik", "llm"),
]

DEFAULT_TAB = "macro"

_LAYOUTS = {
    "macro": macro.layout,
    "micro": micro.layout,
    "experiment": experiment.layout,
    "llm": llm_pipeline.layout,
}


def tab_layout(tab: str, draft: dict):
    try:
        return _LAYOUTS.get(tab or DEFAULT_TAB, experiment.layout)(draft)
    except Exception as exc:  # noqa: BLE001 - eine kaputte Config soll den Editor nicht sprengen
        return ui.alert(f"Editor konnte nicht aufgebaut werden: {exc}", "error")


def reset_button() -> html.Div:
    """«Auf Standard zurücksetzen» — seit P1.7 im Schritt «Lauf & Ablage».

    Vorher stand er über den Reitern und damit über *allen* Einstellungen. In
    einer Schrittfolge gibt es diesen Ort nicht mehr; er gehört dorthin, wo man
    ohnehin über den Lauf als Ganzes nachdenkt.
    """

    return html.Div(
        ui.button(
            "Auf Standard-Config zurücksetzen",
            id=c.action_id("reset"),
            variant="secondary",
            icon_name="restart_alt",
        ),
        className="mt-6",
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

    # Die Szenario-Auswahl des geführten Ablaufs ebenso: eine Entscheidung,
    # aus der `scenario_mode` und `sweep_id` folgen.
    draft = start_flow.normalise(draft)
    return draft


# --- Callbacks -------------------------------------------------------------


def register_callbacks(app) -> None:
    # Seit P1.7 zeichnet `wizard._render` den offenen Schritt — auch die vier
    # Editor-Bereiche, die vorher Reiter waren. Ein eigener Callback dafür gibt
    # es nicht mehr; er hinge an `cfg-tabs`, und die Reiter sind weg.
    wizard.register_callbacks(app)

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
        Output({"type": start_flow.SUMMARY, "slot": ALL}, "children"),
        Input(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _summaries(draft: dict | None):
        """Klartext-Zusammenfassungen mitziehen, sobald sich etwas ändert."""

        sentence = ui.markdown(start_flow.summary_sentence(draft or {}))
        return [sentence] * len(ctx.outputs_list)

    @app.callback(
        Output({"type": start_flow.SLOT, "slot": ALL}, "children"),
        Output({"type": c.ERROR, "field": ALL}, "children"),
        Output(wizard.NEXT, "disabled"),
        Output(wizard.START, "disabled"),
        Output(wizard.GATE, "children"),
        Input(STORE_ID, "data"),
        Input(wizard.STEP_STORE, "data"),
    )
    def _live(draft: dict | None, step):
        """Was sich mit dem Entwurf ändert: Beschreibung, Preflight, Feldfehler — und das Tor.

        Bewusst **ein** Callback für alles: Die Prüfung baut den ganzen
        Simulationszustand auf und soll je Änderung einmal laufen, nicht je
        Ausgabefeld. Der Feldbezug kommt aus `src/validation.py` — die
        Oberfläche ordnet nichts über Schlüsselwörter zu, sie stellt nur dar.

        **Das Tor hängt seit P1.9-W2.2 mit dran**, aus demselben Grund: Es
        braucht dieselben Befunde. Ein eigener Callback dafür ließe
        `validate_draft` zweimal je Tastendruck laufen — und der baut jedes Mal
        den vollständigen `SimulationState` auf.

        Der offene Schritt kommt als zweiter `Input` dazu: Ohne ihn bliebe ein
        gesperrtes «Weiter» gesperrt, wenn man den Schritt verlässt, auf dem der
        Befund liegt.
        """

        data = draft or {}
        slots, by_field = start_flow.live_state(data)
        slot_out = [slots.get((entry["id"] or {}).get("slot")) for entry in ctx.outputs_list[0]]
        error_out = [
            ui.field_errors(by_field.get((entry["id"] or {}).get("field"), []))
            for entry in ctx.outputs_list[1]
        ]

        gesperrt_weiter, gesperrt_start, meldung = wizard.gate(data, step)
        return slot_out, error_out, gesperrt_weiter, gesperrt_start, meldung

    @app.callback(
        Output(model_editor.HOST, "children"),
        Input("cfg-editor-refresh", "data"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _model_editor(_refresh, draft: dict | None):
        """Den Modell-Bereich neu zeichnen, wenn sich der Entwurf **strukturell** ändert.

        Nicht am Entwurf selbst: Der Bereich trägt 168 Eingabefelder, und sie
        unter den Fingern auszutauschen wäre bei jedem Tastendruck ein
        Fokusverlust. Werte fließen ohnehin über `_sync` in den Store und
        stehen dort richtig — neu gebaut werden muss nur, wenn eine Größe
        **dazukommt oder verschwindet**: Preset übernehmen, Property anlegen
        oder löschen, Segment entfernen, Zurücksetzen. Genau dafür gibt es
        `cfg-editor-refresh`, und genau daran hängt auch die Schrittfolge.

        Ohne diese Zeilen zeigte der Bereich nach «Werte übernehmen» weiterhin
        die Zahlen von vorher — richtig im Store, falsch auf dem Schirm.
        """

        return model_editor.body(draft or {})

    @app.callback(
        Output({"type": compute_mode.STATUS, "slot": ALL}, "children"),
        Input(compute_mode.FIELD_ID, "value"),
        Input("wizard-content-host", "children"),
        State(STORE_ID, "data"),
    )
    def _llm_status(_mode, _content, draft: dict | None):
        """Erreichbarkeit von Ollama nachreichen, sobald ein Tab steht.

        Bewusst nach dem Rendern: Die Abfrage kann mehrere Sekunden dauern —
        unter Windows laeuft `localhost` erst in einen IPv6-Timeout — und so
        lange soll die Seite nicht warten.

        Ausgelöst vom Rechenmodus und vom Schrittwechsel,
        **nicht** vom Store: Bei jedem Tastendruck zu fragen würde die Oberfläche
        an einen Netzwerk-Timeout hängen.
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
        # **Dieselbe Meldung an beiden Orten.** Eine Aktion kann aus der
        # Schrittfolge oder aus dem Modell-Bereich kommen, und der jeweils
        # andere ist dann ausgeblendet. Sie nur an einen zu schreiben hiesse,
        # die Haelfte aller Rueckmeldungen ins Nichts zu schicken -- genau das
        # war zwischen W3.1 und W3.2 der Fall.
        Output(model_editor.STATUS, "children"),
        Input({"type": c.ACTION, "action": ALL}, "n_clicks"),
        # **Die schreibenden Aktionen liefern `submit_n_clicks`** (P1.9-W3.2):
        # Sie stecken in einer `ConfirmDialogProvider`, und die meldet erst,
        # wenn jemand die Rückfrage bejaht hat. Ein Callback kann nicht beide
        # Eigenschaften derselben ID-Menge abhören — deshalb tragen sie einen
        # eigenen Typ.
        Input({"type": c.WRITE, "action": ALL}, "submit_n_clicks"),
        Input({"type": macro.PROP_DELETE, "prop": ALL}, "submit_n_clicks"),
        Input({"type": micro.SEGMENT_DELETE, "segment": ALL}, "submit_n_clicks"),
        State(STORE_ID, "data"),
        State({"type": c.FREE, "name": ALL}, "value"),
        State("cfg-editor-refresh", "data"),
        prevent_initial_call=True,
    )
    def _actions(_a, _w, _p, _s, draft: dict | None, _free, refresh):
        trigger = ctx.triggered_id
        if not isinstance(trigger, dict) or not any(
            entry["value"] for entry in ctx.triggered if entry["value"]
        ):
            return no_update, no_update, no_update, no_update

        free = ctx.states_list[1]
        data = dict(draft or {})
        version = int(refresh or 0) + 1

        try:
            data, message, kind = _handle_action(trigger, data, free)
        except Exception as exc:  # noqa: BLE001 - Datei- und Validierungsfehler gehören in die UI
            fehler = ui.alert(str(exc), "error")
            return no_update, no_update, fehler, fehler

        if message is None:
            return no_update, no_update, no_update, no_update
        meldung = ui.alert(message, kind)
        return data, version, meldung, meldung


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

    # `WRITE` und `ACTION` tragen denselben Schlüssel `action`; welcher Typ eine
    # Aktion trägt, sagt nur, ob eine Rückfrage davorsteht.
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
