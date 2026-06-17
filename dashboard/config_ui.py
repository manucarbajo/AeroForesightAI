"""Streamlit-UI zum Bearbeiten der vollen Simulations-Konfiguration."""

from __future__ import annotations

import json

import streamlit as st

from dashboard.config_catalog import (
    CONFIG_FILE_OPTIONS,
    STANDARD_PROPERTY_IDS,
    get_editable_property_ids,
    add_custom_property,
    delete_custom_property,
    PROPERTY_LABELS,
    ConfigDraft,
    PropertyEditState,
    apply_sweep_to_draft,
    default_config_draft,
    effective_config_summary,
    extract_property_edits_from_file,
    extract_factor_states_from_file,
    factor_options_from_file,
    list_sweep_presets,
    load_config_file,
    save_custom_sweep_preset,
    PopulationEditState,
    save_population_edits_to_file,
    extract_population_edits_from_file,
)


def init_config_draft() -> None:
    if "config_draft" not in st.session_state:
        st.session_state.config_draft = default_config_draft()


def _clear_factor_widget_keys(draft: ConfigDraft) -> None:
    """Remove stale Streamlit keys so factor selectboxes follow ``draft.factor_states``."""
    for factor_id in factor_options_from_file(draft.factors_file):
        st.session_state.pop(f"factor_{factor_id}", None)


def _render_scenario_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Szenario")
    mode_labels = {
        "Standard (configs/)": "basis",
        "Szenario-Preset": "sweep",
        "Eigene Parameter": "custom",
    }
    label_list = list(mode_labels.keys())
    current_label = next(
        (label for label, mode in mode_labels.items() if mode == draft.scenario_mode),
        label_list[0],
    )
    selected_label = st.radio(
        "Modus",
        label_list,
        index=label_list.index(current_label),
        horizontal=True,
    )
    draft.scenario_mode = mode_labels[selected_label]

    sweeps = list_sweep_presets()
    if draft.scenario_mode == "sweep" and sweeps:
        sweep_ids = [s.id for s in sweeps]
        default_idx = sweep_ids.index(draft.sweep_id) if draft.sweep_id in sweep_ids else 0
        selected_id = st.selectbox(
            "Szenario",
            sweep_ids,
            index=default_idx,
            format_func=lambda sid: next(s.name for s in sweeps if s.id == sid),
        )
        sweep = next(s for s in sweeps if s.id == selected_id)
        draft.sweep_id = selected_id

        st.info(sweep.description)
        if sweep.rationale:
            with st.expander("Hintergrund zum Szenario", expanded=False):
                st.markdown(sweep.rationale)

        if st.button("Szenario-Parameter übernehmen", key="apply_sweep"):
            draft = apply_sweep_to_draft(draft, sweep)
            _clear_factor_widget_keys(draft)
            st.session_state.config_draft = draft
            st.success(f"Parameter von «{sweep.name}» übernommen.")
            st.rerun()

        draft.rounds = st.number_input(
            "Anzahl Ticks",
            min_value=1,
            max_value=500,
            value=int(sweep.max_ticks),
            step=1,
        )
    elif draft.scenario_mode == "custom":
        draft.apply_custom_overrides = True
        st.caption("Properties und Faktoren in den nächsten Tabs anpassen.")
        draft.rounds = st.number_input("Ticks", min_value=1, max_value=500, value=draft.rounds, step=1)
    else:
        draft.sweep_id = None
        sim = load_config_file(draft.simulation_config_file)
        default_ticks = int(sim.get("clock", {}).get("max_ticks", draft.rounds))
        draft.rounds = st.number_input("Ticks", min_value=1, max_value=500, value=default_ticks, step=1)

    with st.expander("Erweitert: alle Szenarien vergleichen", expanded=False):
        draft.run_all_sweeps = st.checkbox(
            "Alle Szenario-Presets nacheinander (schnell, ohne Agenten-Dialog)",
            value=draft.run_all_sweeps,
        )
        if draft.run_all_sweeps:
            st.caption("Ergebnis unter outputs/sweeps/")
            draft.run_count = 1
        else:
            draft.run_count = st.number_input(
                "Anzahl Läufe (Multi-Run)",
                min_value=1,
                max_value=20,
                value=int(draft.run_count),
                step=1,
                help="Mehrere unabhängige Läufe mit gleicher Config; Seeds werden hochgezählt. "
                "Ergebnis unter outputs/batch_<Zeitstempel>/run_001 …",
            )

    return draft


def _render_properties_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("System-Properties")
    st.caption("Trajektorien aus `properties.json` — Baseline und Regeln pro Tick.")

    if draft.properties_file != "properties.json":
        if st.button("Properties aus gewählter Datei neu laden"):
            draft.property_edits = extract_property_edits_from_file(draft.properties_file)
            st.rerun()

    draft.apply_custom_overrides = st.checkbox(
        "Property- und Faktor-Overrides beim Lauf anwenden",
        value=draft.apply_custom_overrides or draft.scenario_mode == "custom",
        help="Startwerte aus den Tabs «Properties» und «Faktoren» in die Simulation übernehmen.",
    )

    with st.expander(" Neue Property hinzufügen", expanded=False):
        c1, c2 = st.columns([2, 2])
        new_prop_id = c1.text_input("Property ID", placeholder="z.B. airport_fee", key="new_prop_id")
        new_prop_label = c2.text_input("Anzeigename", placeholder="z.B. Airport Fee", key="new_prop_label")
        c3, c4 = st.columns([2, 1])
        price_category_options = {
            "Keine Preisbindung": "none",
            "Steuer (Prozentual auf Ticketpreis)": "tax",
            "Gebühr (Absoluter EUR-Betrag)": "fee",
        }
        selected_category = c3.selectbox(
            "Preiskategorie",
            options=list(price_category_options.keys()),
            index=0,
            key="new_prop_price_category",
            help="Steuern werden prozentual auf den Ticketpreis aufgeschlagen (z.B. 0.19 = 19%). "
                 "Gebühren werden als absoluter EUR-Betrag addiert (z.B. 10.0 = 10 €).",
        )
        price_component_type = price_category_options[selected_category]
        c4.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if c4.button("Hinzufügen", width="stretch"):
            if new_prop_id and new_prop_id.isidentifier():
                add_custom_property(new_prop_id, new_prop_label, draft.properties_file, price_component_type)
                draft.property_edits = extract_property_edits_from_file(draft.properties_file)
                st.success(f"Property «{new_prop_label or new_prop_id}» als {selected_category} hinzugefügt!")
                st.rerun()
            else:
                st.error("Ungültige ID")

    # Load price_component_type mapping from properties.json for badge display
    _props_data = load_config_file(draft.properties_file)
    _price_component_map: dict[str, str] = {}
    for _sp in _props_data.get("system_properties", []):
        if isinstance(_sp, dict) and _sp.get("price_component_type"):
            _price_component_map[_sp["id"]] = _sp["price_component_type"]

    for prop_id in get_editable_property_ids(draft.properties_file):
        edit = draft.property_edits.get(prop_id)
        if edit is None:
            continue
        label = PROPERTY_LABELS.get(prop_id, prop_id)
        pct = _price_component_map.get(prop_id, "none")
        badge = ""
        if pct == "tax":
            badge = " Steuer (%)"
        elif pct == "fee":
            badge = " Gebühr (€)"
        with st.expander(f"{label}{badge}", expanded=False):
            is_active = st.checkbox("In dieser Simulation aktiv", value=edit.is_active, key=f"prop_active_{prop_id}")
            
            edit.is_active = is_active
            
            if not is_active:
                # We still need to render the "Erweitert" expander so they can delete it when inactive
                with st.expander("Erweitert", expanded=False):
                    confirm_key = f"confirm_del_{prop_id}"
                    if st.session_state.get(confirm_key, False):
                        st.warning(f"Wollen Sie Property '{prop_id}' wirklich dauerhaft aus der JSON löschen?")
                        c1, c2 = st.columns(2)
                        if c1.button("Ja, endgültig löschen", key=f"do_del_inactive_{prop_id}"):
                            st.session_state[confirm_key] = False
                            delete_custom_property(prop_id, draft.properties_file)
                            draft.property_edits = extract_property_edits_from_file(draft.properties_file)
                            st.success(f"Property {prop_id} gelöscht!")
                            st.rerun()
                        if c2.button("Abbrechen", key=f"cancel_del_inactive_{prop_id}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                    else:
                        if st.button(f"🗑️ Property '{prop_id}' löschen", key=f"init_del_inactive_{prop_id}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                continue

            baseline = st.number_input(
                "Baseline",
                value=float(edit.baseline),
                format="%.4f",
                key=f"prop_base_{prop_id}",
            )
            st.markdown("**Regeln** (Tick → Effekt)")
            rule_count = st.number_input(
                "Anzahl Regeln",
                min_value=0,
                max_value=8,
                value=len(edit.rules),
                step=1,
                key=f"prop_rule_count_{prop_id}",
            )
            new_rules: list[dict] = []
            for idx in range(int(rule_count)):
                existing = edit.rules[idx] if idx < len(edit.rules) else {}
                effect = existing.get("effect") or {}
                effect_type = effect.get("type", "set")
                
                cols = st.columns([1, 1, 1, 1])
                tick = cols[0].number_input(
                    f"Tick #{idx + 1}",
                    min_value=1,
                    max_value=500,
                    value=int(existing.get("active_from_tick", 1)),
                    key=f"prop_rule_tick_{prop_id}_{idx}",
                )
                r_type = cols[1].selectbox(
                    f"Typ #{idx + 1}",
                    ["set", "ramp"],
                    index=0 if effect_type == "set" else 1,
                    key=f"prop_rule_type_{prop_id}_{idx}",
                )
                value = cols[2].number_input(
                    f"Wert #{idx + 1}",
                    value=float(effect.get("value", baseline)),
                    format="%.4f",
                    key=f"prop_rule_val_{prop_id}_{idx}",
                )
                
                new_effect = {"type": r_type, "value": float(value)}
                if r_type == "ramp":
                    duration = cols[3].number_input(
                        f"Dauer (Ticks) #{idx + 1}",
                        min_value=1,
                        max_value=100,
                        value=int(effect.get("duration_ticks", 5)),
                        key=f"prop_rule_dur_{prop_id}_{idx}",
                    )
                    new_effect["duration_ticks"] = int(duration)

                new_rules.append(
                    {
                        "active_from_tick": int(tick),
                        "effect": new_effect,
                    }
                )
            draft.property_edits[prop_id] = PropertyEditState(
                property_id=prop_id,
                baseline=float(baseline),
                rules=new_rules,
                is_active=is_active,
            )

            if prop_id not in STANDARD_PROPERTY_IDS and is_active:
                with st.expander("Erweitert", expanded=False):
                    confirm_key = f"confirm_del_{prop_id}"
                    if st.session_state.get(confirm_key, False):
                        st.warning(f"Wollen Sie Property '{prop_id}' wirklich dauerhaft aus der JSON löschen?")
                        c1, c2 = st.columns(2)
                        if c1.button("Ja, endgültig löschen", key=f"do_del_active_{prop_id}"):
                            st.session_state[confirm_key] = False
                            delete_custom_property(prop_id, draft.properties_file)
                            draft.property_edits = extract_property_edits_from_file(draft.properties_file)
                            st.success(f"Property {prop_id} gelöscht!")
                            st.rerun()
                        if c2.button("Abbrechen", key=f"cancel_del_active_{prop_id}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                    else:
                        if st.button(f"🗑️ Property '{prop_id}' löschen", key=f"init_del_active_{prop_id}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
    return draft


def _render_factors_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Faktor-Startzustände")
    st.caption(
        "Startzustände F1–F7 vor dem Lauf. Während der Simulation wechseln Faktoren "
        "automatisch über `factor_rules` in `properties.json` (z. B. bei CO₂-Schock oder Booking)."
    )
    if not (draft.apply_custom_overrides or draft.scenario_mode == "custom"):
        st.warning(
            "Overrides sind deaktiviert — Änderungen hier wirken erst nach Aktivierung "
            "von «Property- und Faktor-Overrides beim Lauf anwenden» (Tab Properties)."
        )
    options = factor_options_from_file(draft.factors_file)
    if not options:
        st.warning("Keine Faktoren in der gewählten Datei.")
        return draft

    if draft.factors_file != "factors.json":
        if st.button("Faktoren aus gewählter Datei neu laden"):
            draft.factor_states = extract_factor_states_from_file(draft.factors_file)
            _clear_factor_widget_keys(draft)
            st.rerun()

    cols = st.columns(2)
    factor_ids = sorted(options.keys())
    for idx, factor_id in enumerate(factor_ids):
        states = options[factor_id]
        state_keys = list(states.keys())
        current = draft.factor_states.get(factor_id, state_keys[0] if state_keys else "")
        default_idx = state_keys.index(current) if current in state_keys else 0
        with cols[idx % 2]:
            selected = st.selectbox(
                factor_id,
                state_keys,
                index=default_idx,
                format_func=lambda k, st_map=states: f"{k}: {st_map[k][:50]}",
            )
            draft.factor_states[factor_id] = selected
    return draft


def _render_llm_pipeline_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("LLM & Pipeline")
    c1, c2 = st.columns(2)
    with c1:
        draft.mock_llm = st.checkbox("Mock-LLM", value=draft.mock_llm)
        draft.deterministic_only = st.checkbox("Deterministisch (ohne Agenten-LLM)", value=draft.deterministic_only)
        draft.model = st.text_input("Ollama-Modell", value=draft.model)
        draft.base_url = st.text_input("Ollama Base-URL", value=draft.base_url)
    with c2:
        draft.temperature = st.slider("Temperature", 0.0, 1.5, float(draft.temperature), 0.05)
        draft.max_tokens = st.number_input("Max Tokens", min_value=256, max_value=8192, value=int(draft.max_tokens))
        draft.checkpoint_interval = st.number_input("Checkpoint alle N Ticks", min_value=0, value=int(draft.checkpoint_interval))
        draft.resume_from = st.text_input("Resume (Run-ID oder Pfad)", value=draft.resume_from)

    st.markdown("**Pipeline-Optionen**")
    p1, p2, p3, p4 = st.columns(4)
    draft.no_market = p1.checkbox("Markt aus", value=draft.no_market)
    draft.redebedarf = p2.checkbox("Redebedarf-Modus", value=draft.redebedarf)
    draft.no_protocol = p3.checkbox("Kein Protocol", value=draft.no_protocol)
    draft.no_scenarios = p4.checkbox("Keine Szenarien", value=draft.no_scenarios)

    s1, s2 = st.columns(2)
    draft.use_seed = s1.checkbox("Seed setzen", value=draft.use_seed)
    draft.seed = s2.number_input("Seed", min_value=0, value=int(draft.seed or 42), step=1)
    draft.generate_figures = st.checkbox(
        "Figures nach Lauf erzeugen",
        value=draft.generate_figures,
        help="Speichert PNGs unter outputs/<run_id>/figures/ und zeigt sie im Tab «Figures».",
    )

    return draft


def _render_config_files_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Config-Dateien")
    st.caption("Standard liegt unter `configs/` — alternative Dateien für Experimente.")

    file_keys = list(CONFIG_FILE_OPTIONS.keys())
    c1, c2 = st.columns(2)
    draft.simulation_config_file = c1.selectbox(
        "Simulation",
        file_keys,
        index=file_keys.index(draft.simulation_config_file) if draft.simulation_config_file in file_keys else 0,
        format_func=lambda f: CONFIG_FILE_OPTIONS.get(f, f),
    )
    draft.properties_file = c2.selectbox(
        "Properties",
        file_keys,
        index=file_keys.index(draft.properties_file) if draft.properties_file in file_keys else 1,
        format_func=lambda f: CONFIG_FILE_OPTIONS.get(f, f),
    )
    c3, c4 = st.columns(2)
    draft.agents_file = c3.selectbox(
        "Agents",
        file_keys,
        index=file_keys.index(draft.agents_file) if draft.agents_file in file_keys else 2,
        format_func=lambda f: CONFIG_FILE_OPTIONS.get(f, f),
    )
    draft.factors_file = c4.selectbox(
        "Factors",
        file_keys,
        index=file_keys.index(draft.factors_file) if draft.factors_file in file_keys else 4,
        format_func=lambda f: CONFIG_FILE_OPTIONS.get(f, f),
    )
    draft.cib_file = st.selectbox(
        "Einflussmatrix",
        file_keys,
        index=file_keys.index(draft.cib_file) if draft.cib_file in file_keys else 5,
        format_func=lambda f: CONFIG_FILE_OPTIONS.get(f, f),
    )

    draft.simulation_name = st.text_input("Run-Name (optional)", value=draft.simulation_name)
    draft.simulation_description = st.text_area(
        "Run-Beschreibung (optional)",
        value=draft.simulation_description,
        height=80,
    )

    with st.expander("JSON-Vorschau: simulation_config.json", expanded=False):
        st.json(load_config_file(draft.simulation_config_file))
    with st.expander("JSON-Vorschau: properties.json (Auszug)", expanded=False):
        props = load_config_file(draft.properties_file)
        st.json({"system_properties": props.get("system_properties", [])[:3], "...": "gekürzt"})

    st.divider()
    preset_name = st.text_input("Als Szenario speichern (configs/sweeps/)", value="mein_szenario")
    if st.button("Szenario speichern"):
        try:
            path = save_custom_sweep_preset(draft, preset_name)
            st.success(f"Gespeichert: `{path}`")
        except Exception as exc:
            st.error(str(exc))

    return draft


def _render_population_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Bevölkerungs-Struktur (Agenten)")
    st.info("Diese Einstellungen steuern die Wahrscheinlichkeitsverteilungen, mit denen individuelle Agenten beim Simulationsstart generiert werden.")
    
    if st.button("Populations-Config aus JSON neu laden", key="btn_reload_pop"):
        draft.population_edits = extract_population_edits_from_file("properties.json")
        st.rerun()

    st.markdown("### Segment-Anteile (Prevalence)")
    if not hasattr(draft, "population_edits") or not draft.population_edits:
        draft.population_edits = extract_population_edits_from_file("properties.json")
    boolean_props = [p for p in draft.population_edits if p.type == "boolean"]
    cols = st.columns(3)
    for i, p in enumerate(boolean_props):
        with cols[i % 3]:
            label = p.id.replace("_", " ").title()
            val = float(p.prevalence) if p.prevalence is not None else 0.0
            new_val = st.slider(f"{label}", 0.0, 1.0, val, 0.05, key=f"pop_prev_{p.id}")
            p.prevalence = new_val

    st.markdown("### Eigenschaften-Verteilungen")
    dist_props = [p for p in draft.population_edits if p.type == "distribution"]
    for p in dist_props:
        label = p.id.replace("_", " ").title()
        if p.id == "wtp_eur": label = "Zahlungsbereitschaft (WTP in Euro)"
        if p.id == "environmental_awareness": label = "Umweltbewusstsein (0-1)"
        
        with st.expander(label, expanded=False):
            dist_opts = ["normal", "beta", "lognormal", "uniform"]
            current_dist = p.distribution if p.distribution in dist_opts else "normal"
            dist_type = st.selectbox("Verteilungstyp", dist_opts, index=dist_opts.index(current_dist), key=f"pop_dist_{p.id}")
            p.distribution = dist_type
            
            c1, c2, c3, c4 = st.columns(4)
            if dist_type in ("normal", "lognormal"):
                with c1: p.mean = st.number_input("Mittelwert", value=p.mean or 0.0, format="%.2f", key=f"pop_mean_{p.id}")
                with c2: p.std_dev = st.number_input("Std Dev", value=p.std_dev or 1.0, format="%.2f", key=f"pop_std_{p.id}")
                with c3: p.min_value = st.number_input("Min", value=p.min_value or 0.0, format="%.2f", key=f"pop_min_{p.id}")
                with c4: p.max_value = st.number_input("Max", value=p.max_value or 1.0, format="%.2f", key=f"pop_max_{p.id}")
            elif dist_type == "beta":
                with c1: p.alpha = st.number_input("Alpha", value=p.alpha or 2.0, format="%.2f", key=f"pop_alpha_{p.id}")
                with c2: p.beta = st.number_input("Beta", value=p.beta or 5.0, format="%.2f", key=f"pop_beta_{p.id}")
                with c3: p.min_value = st.number_input("Min", value=p.min_value or 0.0, format="%.2f", key=f"pop_min_{p.id}")
                with c4: p.max_value = st.number_input("Max", value=p.max_value or 1.0, format="%.2f", key=f"pop_max_{p.id}")
                
    st.divider()
    if st.button("Änderungen an Population speichern", type="primary"):
        save_population_edits_to_file(draft.population_edits, "properties.json")
        st.success("Populations-Konfiguration erfolgreich gespeichert!")

    return draft


def render_config_editor() -> ConfigDraft:
    init_config_draft()
    draft: ConfigDraft = st.session_state.config_draft

    if st.button("Auf Standard-Config zurücksetzen"):
        draft = default_config_draft()
        _clear_factor_widget_keys(draft)
        st.session_state.config_draft = draft
        st.rerun()

    tabs = st.tabs(["Szenario", "Bevölkerung", "Properties", "Faktoren", "LLM & Pipeline", "Config-Dateien", "Vorschau"])
    with tabs[0]:
        draft = _render_scenario_tab(draft)
    with tabs[1]:
        draft = _render_population_tab(draft)
    with tabs[2]:
        draft = _render_properties_tab(draft)
    with tabs[3]:
        draft = _render_factors_tab(draft)
    with tabs[4]:
        draft = _render_llm_pipeline_tab(draft)
    with tabs[5]:
        draft = _render_config_files_tab(draft)
    with tabs[6]:
        st.subheader("Effektive Konfiguration")
        st.json(effective_config_summary(draft))

    st.session_state.config_draft = draft
    return draft
