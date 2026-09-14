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
    extract_population_edits_from_file,
    extract_property_edits_from_file,
    list_sweep_presets,
    save_market_feedback_to_file,
    save_population_edits_to_file,
    save_saturation_to_file,
)
from dashboard.web import components as ui
from dashboard.web.config_editor import (
    compute_mode,
    delta,
    experiment,
    llm_pipeline,
    macro,
    micro,
    sichern,
    start_flow,
    wizard,
)
from dashboard.web.config_editor import controls as c
from dashboard.web.pages import model_editor
from dashboard.web.state import RUECKNAHME_ID, STORE_ID, draft_from_dict, draft_to_dict

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
        return ui.hinweis(f"Editor konnte nicht aufgebaut werden: {exc}", "fehler")


def reset_button() -> html.Div:
    """«Alle Einstellungen zurücksetzen» — im Schritt «Lauf & Ablage», **rücknehmbar**.

    Seit P1.7 steht er hier statt über den Reitern. Bis P7.4-U4.3 hieß er «Auf
    Standard-Config zurücksetzen» und verwarf den ganzen Entwurf ohne Rückfrage
    und ohne Weg zurück — in einem als optional markierten Schritt. Jetzt hält
    `state.RUECKNAHME_ID` den Stand davor, und die Meldung trägt «Rückgängig».

    **Eine Rückfrage davor gibt es bewusst nicht.** Das Paket nannte beides; das
    Kriterium verlangt die Rücknahme mit einem Klick, und vor einer Handlung,
    die sich so zurücknehmen lässt, wäre eine Rückfrage nur ein Hindernis.
    """

    return html.Div(
        [
            ui.button(
                "Alle Einstellungen zurücksetzen",
                id=c.action_id("reset"),
                variant="secondary",
                icon_name="restart_alt",
            ),
            ui.hint_text(
                "Setzt jede Einstellung auf den Auslieferungszustand. Lässt sich danach "
                "mit einem Klick rückgängig machen.",
                class_name="mt-2",
            ),
        ],
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
    c.register_callbacks(app)
    sichern.register_callbacks(app)

    @app.callback(
        Output(STORE_ID, "data"),
        Input({"type": c.CFG, "field": ALL}, "value"),
        Input({"type": c.CFG_BOOL, "field": ALL}, "value"),
        Input({"type": macro.RULE, "prop": ALL, "index": ALL, "key": ALL}, "value"),
        State(STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def _sync(_values, _flags, _rules, draft: dict | None):
        """Sichtbare Felder in den Store — **und nur, wenn sich etwas ändert** (P3.9).

        Der zweite Halbsatz ist die ganze Arbeit von P3.9. Dieser Callback feuert
        nicht nur beim Tippen: Sobald ein Schritt gezeichnet wird, melden seine
        Eingabefelder ihren *unveränderten* Wert, und bis zum 2026-09-05 schrieb
        `_sync` daraufhin einen neuen Entwurf in den Store. Ein neues Dict ist für
        Dash eine Änderung, also zog es alles nach, was am Entwurf hängt:
        Preflight, Feldfehler, Tor, Zusammenfassungen, Laufübersicht — **acht bis
        elf Server-Aufrufe für einen Klick, der keine Einstellung anfasst.**

        Gemessen im Browser (die einzige Messung, die hier zählt): 0,72 bis 1,49
        Sekunden je Klick, und `config-draft-store.data` stand **dreimal** in
        derselben Kette.

        **Ein Vergleich, keine Ausnahmeliste.** Der naheliegende Weg wäre, den
        Schritt-Wechsel als Sonderfall auszunehmen. Das wäre eine zweite Stelle,
        die wissen muss, was ein Schritt ist — und die nächste Ursache für ein
        folgenloses Schreiben käme von woanders. Ist der berechnete Entwurf
        gleich dem gespeicherten, gibt es nichts mitzuziehen: Jeder Verwender
        hat genau diese Daten schon gesehen.
        """

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

        neu = _normalise(updated)
        if draft is not None and neu == draft:
            return no_update
        return neu

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
        Input("url", "pathname"),
        Input("cfg-editor-refresh", "data"),
        State(STORE_ID, "data"),
    )
    def _model_editor(pathname: str | None, _refresh, draft: dict | None):
        """Den Modell-Bereich bauen, **wenn jemand ihn aufsucht** (P3.12).

        Zwei Auslöser, zwei Gründe:

        * **Der Pfad** — der Bereich entsteht erst beim Aufsuchen und wird beim
          Verlassen wieder abgebaut. Bis P3.12 lag er dauernd im DOM: **1404 der
          2882 Knoten** der ganzen Anwendung, auch während jemand in der
          Schrittfolge arbeitete. Das kostete dort **jeden Klick rund eine
          Sekunde**, weil Dashs `dash_renderer` bei *jeder* Callback-Antwort alle
          angeschlossenen Komponenten benachrichtigt (`notifyNestedSubs`) — die
          Kosten hängen an ihrer Zahl, nicht an der Größe des sichtbaren
          Bereichs. Gemessen: 1218 ms → 246 ms in `dash_renderer`, längste
          Browser-Aufgabe 1144 ms → 267 ms.
        * **`cfg-editor-refresh`** — wie bisher, wenn sich der Entwurf
          *strukturell* ändert. Nicht am Entwurf selbst: Die Felder unter den
          Fingern auszutauschen wäre bei jedem Tastendruck ein Fokusverlust.
          Werte fließen ohnehin über `_sync` in den Store; neu gebaut werden muss
          nur, wenn eine Größe **dazukommt oder verschwindet** — Preset
          übernehmen, Property anlegen oder löschen, Segment entfernen,
          Zurücksetzen. Ohne diesen Auslöser zeigte der Bereich nach «Werte
          übernehmen» weiterhin die Zahlen von vorher.

        **Regel 6 ist hier nicht berührt, und das ist gemessen, nicht vermutet:**
        Der Rumpf trägt **keine einzige feste ID** — alle neun Kennungen darin
        sind Muster (`cfg`, `cfg-bool`, `cfg-rule`, …), und ein Muster-Eingang mit
        `ALL` verträgt null Treffer von Haus aus. Wer hier eine Komponente mit
        fester ID einbaut, an der ein Callback hängt, nimmt diesen Callback mit
        aus dem DOM — `tests/test_web_lazy_modell.py` sagt es ihm.

        **`prevent_initial_call` ist weg**, und zwar mit Absicht: Wer die Adresse
        `/app/modell` direkt öffnet, muss den Bereich sehen. Der erste Aufruf
        entscheidet dann anhand des Pfads, ob gebaut wird — beim Start auf einem
        anderen Bereich kostet er nichts.
        """

        return model_editor.rumpf_fuer(pathname, draft)

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
        # Der Stand vor dem Zurücksetzen (P7.4-U4.3), siehe `_ruecknahme_nach`.
        Output(RUECKNAHME_ID, "data"),
        Input({"type": c.ACTION, "action": ALL}, "n_clicks"),
        # **Die schreibenden Aktionen melden sich erst mit der Bestätigung**
        # (P1.9-W3.2, seit P7.1-U1.4 im gestalteten Dialog): Ihre ID trägt der
        # Knopf **im** Dialog, nicht der, der ihn öffnet (`c.ASK`). Der Klick auf
        # der Seite erreicht den Server also gar nicht.
        Input({"type": c.WRITE, "action": ALL}, "n_clicks"),
        Input({"type": delta.REVERT, "feld": ALL}, "n_clicks"),
        Input({"type": macro.PROP_DELETE, "prop": ALL}, "n_clicks"),
        Input({"type": micro.SEGMENT_DELETE, "segment": ALL}, "n_clicks"),
        State(STORE_ID, "data"),
        State({"type": c.FREE, "name": ALL}, "value"),
        State("cfg-editor-refresh", "data"),
        State(RUECKNAHME_ID, "data"),
        prevent_initial_call=True,
    )
    def _actions(_a, _w, _r, _p, _s, draft: dict | None, _free, refresh, gemerkt):
        trigger = ctx.triggered_id
        if not isinstance(trigger, dict) or not any(
            entry["value"] for entry in ctx.triggered if entry["value"]
        ):
            return no_update, no_update, no_update, no_update, no_update

        free = ctx.states_list[1]
        vorher = dict(draft or {})
        data = dict(vorher)
        version = int(refresh or 0) + 1

        try:
            data, message, kind = _handle_action(trigger, data, free, ruecknahme=gemerkt)
        except Exception as exc:  # noqa: BLE001 - Datei- und Validierungsfehler gehören in die UI
            fehler = ui.hinweis(str(exc), "fehler")
            return no_update, no_update, fehler, fehler, no_update

        if message is None:
            return no_update, no_update, no_update, no_update, no_update
        return (
            data,
            version,
            _meldung(trigger, message, kind, knopf=True),
            _meldung(trigger, message, kind, knopf=False),
            _ruecknahme_nach(trigger, vorher, gemerkt),
        )


def _ruecknahme_nach(trigger: dict, vorher: dict, gemerkt: dict | None):
    """Was der Rücknahme-Store nach einer Aktion hält (P7.4-U4.3).

    Nach «zurücksetzen» den Stand davor; nach «Rückgängig» nichts mehr — eine
    Rücknahme wirkt einmal, sonst setzte ein zweiter Klick wieder zurück. Jede
    andere Aktion lässt stehen, was gemerkt ist.
    """

    aktion = trigger.get("action")
    if aktion == "reset":
        return vorher
    if aktion == "reset-undo":
        return None
    return no_update


def _meldung(trigger: dict, message: str, kind: str, *, knopf: bool) -> object:
    """Die Meldung einer Aktion — nach dem Zurücksetzen mit «Rückgängig».

    **Der Knopf steht nur in einer der beiden Meldungen** (*knopf*): Dieselbe
    Meldung geht an die Schrittfolge und an den Modell-Bereich, und zweimal
    dieselbe Kennung ist für Dash ein Laufzeitfehler. Zurückgesetzt wird nur im
    Einrichten, also steht er dort.
    """

    hinweis = ui.hinweis(message, kind)
    if not knopf or trigger.get("action") != "reset":
        return hinweis
    return html.Div(
        [
            hinweis,
            html.Div(
                ui.button("Rückgängig", id=c.action_id("reset-undo"), variant="ghost"),
                className="mt-2",
            ),
        ]
    )


def _namensvorschlag(draft: dict) -> str:
    """Ein Name, der einen Lauf in der Liste unterscheidbar macht.

    Drei Angaben, in der Reihenfolge, in der man sie sucht: **woher** der Lauf
    ausgeht, **wie lang** er ist, und **wann** er entstanden ist. Der Rechenmodus
    steht bewusst nicht dabei — er steht im Artefakt und macht den Namen nur
    länger.
    """

    from datetime import datetime

    if draft.get("run_all_sweeps"):
        woher = "Szenario-Vergleich"
    elif draft.get("scenario_mode") == "sweep" and draft.get("sweep_id"):
        preset = next(
            (s for s in list_sweep_presets() if s.id == draft["sweep_id"]),
            None,
        )
        woher = preset.name if preset is not None else str(draft["sweep_id"])
    elif draft.get("scenario_mode") == "custom":
        woher = "Eigene Einstellungen"
    else:
        woher = "Standard-Ausgangslage"

    stempel = datetime.now().strftime("%d.%m.%Y, %H:%M")
    if draft.get("run_all_sweeps"):
        return f"{woher} · {stempel}"
    return f"{woher} · {draft.get('rounds', '?')} Ticks · {stempel}"


def _handle_action(
    trigger: dict, data: dict, free: list, *, ruecknahme: dict | None = None
) -> tuple[dict, str | None, str]:
    """Eine Aktion ausführen und (neuer Draft, Meldung, Ton des Hinweises) zurückgeben.

    Der Ton ist einer aus `ui.HINWEIS_TOENE`; `tests/test_web_hinweis.py` liest
    jede Rückgabe hier und hält sie dagegen.
    """

    kind = trigger.get("type")

    if kind == delta.REVERT:
        feld = trigger["feld"]
        data = delta.zuruecknehmen(data, feld)
        return data, f"«{delta._name(feld)}» auf den Auslieferungswert zurückgesetzt.", "erfolg"

    if kind == macro.PROP_DELETE:
        prop = trigger["prop"]
        delete_custom_property(prop, data.get("properties_file", "properties.json"))
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, f"Property «{prop}» gelöscht.", "erfolg"

    if kind == micro.SEGMENT_DELETE:
        segment = trigger["segment"]
        data["population_edits"] = [
            item for item in (data.get("population_edits") or []) if item.get("id") != segment
        ]
        draft = draft_from_dict(data)
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        return data, f"Segment «{segment}» gelöscht.", "erfolg"

    # `WRITE` und `ACTION` tragen denselben Schlüssel `action`; welcher Typ eine
    # Aktion trägt, sagt nur, ob eine Rückfrage davorsteht.
    action = trigger.get("action")

    if action == "suggest-name":
        # **Ein Vorschlag ist eine Handlung, kein Rückfall** (P1.9-W4.1). Den
        # Namen beim Rendern vorzubelegen wäre der Fehler aus Befund A7: Der
        # Wert käme aus dem Quelltext statt aus einer Entscheidung, und
        # `touched()` meldete danach Einstellungen, die niemand vorgenommen hat.
        # Hier drückt jemand auf einen Knopf — das ist eine Entscheidung.
        data["simulation_name"] = _namensvorschlag(data)
        return data, f"Name gesetzt: «{data['simulation_name']}»", "erfolg"

    if action == "reset":
        return (
            draft_to_dict(default_config_draft()),
            "Alle Einstellungen stehen wieder auf dem Auslieferungszustand.",
            "erfolg",
        )

    if action == "reset-undo":
        # *ruecknahme* kommt aus `state.RUECKNAHME_ID` (P7.4-U4.3).
        if not ruecknahme:
            return data, "Es gibt nichts zurückzunehmen.", "info"
        return dict(ruecknahme), "Die Einstellungen von vorher sind wiederhergestellt.", "erfolg"

    if action == "apply-sweep":
        sweeps = list_sweep_presets()
        sweep = next((s for s in sweeps if s.id == data.get("sweep_id")), None)
        if sweep is None:
            return data, "Kein Szenario-Preset ausgewählt.", "warnung"
        applied = apply_sweep_to_draft(draft_from_dict(data), sweep)
        return draft_to_dict(applied), f"Parameter von «{sweep.name}» übernommen.", "erfolg"

    if action == "reload-properties":
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, "Properties neu geladen.", "erfolg"

    if action == "add-property":
        prop_id = c.free_value(free, "new-prop-id").strip()
        if not prop_id or not prop_id.isidentifier():
            return data, "Bitte eine gültige Property-ID angeben (Python-Bezeichner).", "warnung"
        add_custom_property(
            prop_id,
            c.free_value(free, "new-prop-label").strip() or prop_id,
            data.get("properties_file", "properties.json"),
            c.free_value(free, "new-prop-category", "none"),
        )
        edits = extract_property_edits_from_file(data.get("properties_file", "properties.json"))
        data["property_edits"] = {k: asdict(v) for k, v in edits.items()}
        return data, f"Property «{prop_id}» angelegt.", "erfolg"

    if action == "save-market-feedback":
        draft = draft_from_dict(data)
        save_market_feedback_to_file(draft.market_feedback_edit, draft.properties_file)
        return data, "Markt-Feedback gespeichert.", "erfolg"

    if action == "add-segment":
        segment_id = c.free_value(free, "new-segment-id").strip()
        if not segment_id or not segment_id.isidentifier():
            return data, "Bitte eine gültige Segment-ID angeben (Python-Bezeichner).", "warnung"
        segments = data.get("population_edits") or []
        if any(item.get("id") == segment_id for item in segments):
            return data, f"Ein Segment «{segment_id}» existiert bereits.", "warnung"
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
        return data, f"Segment «{segment_id}» angelegt.", "erfolg"

    if action == "save-population":
        draft = draft_from_dict(data)
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        save_saturation_to_file(draft.saturation_edit, draft.properties_file)
        return data, "Population und Sättigung gespeichert.", "erfolg"

    return data, None, "info"
