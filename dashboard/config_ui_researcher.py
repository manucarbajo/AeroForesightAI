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
    save_saturation_to_file,
    extract_saturation_from_file,
    save_market_feedback_to_file,
    extract_market_feedback_from_file,
)


def init_config_draft() -> None:
    if "config_draft" not in st.session_state:
        st.session_state.config_draft = default_config_draft()
        return
    draft: ConfigDraft = st.session_state.config_draft
    if not hasattr(draft, "saturation_edit"):
        draft.saturation_edit = extract_saturation_from_file(draft.properties_file)
    if not hasattr(draft, "market_feedback_edit"):
        draft.market_feedback_edit = extract_market_feedback_from_file(draft.properties_file)


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
            st.success(f"Parameter von {sweep.name} übernommen.")
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

    # P2.3: Basispreis konfigurierbar
    st.markdown("#### Preismodell")
    col_bp1, col_bp2 = st.columns([1, 3])
    with col_bp1:
        enable_base_price = st.checkbox(
            "Basispreis überschreiben",
            value=draft.base_price is not None,
            key="enable_base_price",
        )
    with col_bp2:
        if enable_base_price:
            draft.base_price = st.number_input(
                "Basispreis (EUR)",
                min_value=1.0,
                max_value=1000.0,
                value=float(draft.base_price) if draft.base_price is not None else 100.0,
                step=5.0,
                format="%.1f",
                key="base_price_input",
                help="Überschreibt price_model.base_price in properties.json für diesen Lauf.",
            )
        else:
            draft.base_price = None
            st.caption("Standard: 100.0 € (aus `properties.json → price_model.base_price`)")

    st.markdown("#### Yield / Markt-Feedback")
    st.caption(
        "Steuert, wie stark der Anbieter Preis und Marge an die beobachtete Buchungsrate anpasst. "
        "Wird in `properties.json` gespeichert (`market_feedback` + `market_rules`)."
    )
    mf = draft.market_feedback_edit
    mf.enabled = st.checkbox("Markt-Feedback aktiv", value=mf.enabled, key="mf_enabled")
    col_mf1, col_mf2, col_mf3 = st.columns(3)
    with col_mf1:
        mf.target_booking_rate = st.number_input(
            "Ziel-Buchungsrate",
            min_value=0.05,
            max_value=1.0,
            value=float(mf.target_booking_rate),
            step=0.01,
            format="%.2f",
            key="mf_target_br",
            help="Yield-Feedback zielt auf diesen Anteil buchender Personen pro Tick.",
        )
        mf.marginal_cost_fraction = st.number_input(
            "Grenzkosten-Anteil",
            min_value=0.05,
            max_value=1.0,
            value=float(mf.marginal_cost_fraction),
            step=0.01,
            format="%.2f",
            key="mf_marginal_cost",
            help="Untergrenze: Grenzkosten + Steuern/Gebühren (Anteil der Kostenbasis).",
        )
    with col_mf2:
        mf.markup_adjustment_per_tick = st.number_input(
            "Markup-Anpassung / Tick",
            min_value=0.01,
            max_value=0.5,
            value=float(mf.markup_adjustment_per_tick),
            step=0.01,
            format="%.2f",
            key="mf_markup_adj",
        )
        mf.damping = st.number_input(
            "Dämpfung",
            min_value=0.1,
            max_value=1.0,
            value=float(mf.damping),
            step=0.05,
            format="%.2f",
            key="mf_damping",
        )
    with col_mf3:
        mf.max_price_change_fraction = st.number_input(
            "Max. Preisänderung / Tick",
            min_value=0.01,
            max_value=0.5,
            value=float(mf.max_price_change_fraction),
            step=0.01,
            format="%.2f",
            key="mf_max_price_chg",
        )
        mf.booking_weight = st.number_input(
            "Booking-Gewicht (Makro-Nachfrage)",
            min_value=0.0,
            max_value=1.0,
            value=float(mf.booking_weight),
            step=0.05,
            format="%.2f",
            key="mf_booking_weight",
        )
    if st.button("Markt-Feedback speichern", key="btn_save_market_feedback", type="secondary"):
        save_market_feedback_to_file(mf, draft.properties_file)
        st.success("Markt-Feedback in properties.json gespeichert.")

    st.divider()

    if draft.properties_file != "properties.json":
        if st.button("Properties aus gewählter Datei neu laden"):
            draft.property_edits = extract_property_edits_from_file(draft.properties_file)
            st.rerun()

    draft.apply_custom_overrides = st.checkbox(
        "Property- und Faktor-Overrides beim Lauf anwenden",
        value=draft.apply_custom_overrides or draft.scenario_mode == "custom",
        help="Startwerte aus den Tabs Properties und Faktoren in die Simulation übernehmen.",
    )

    with st.container(border=True):
        st.markdown("**Neue Property hinzufügen**")
        c1, c2, c3 = st.columns([2, 2, 2])
        new_prop_id = c1.text_input("Property ID", placeholder="z.B. airport_fee", key="new_prop_id")
        new_prop_label = c2.text_input("Anzeigename", placeholder="z.B. Airport Fee", key="new_prop_label")
        
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
        
        if st.button("Property Hinzufügen", type="primary", use_container_width=True):
            if new_prop_id and new_prop_id.isidentifier():
                add_custom_property(new_prop_id, new_prop_label, draft.properties_file, price_component_type)
                draft.property_edits = extract_property_edits_from_file(draft.properties_file)
                st.success(f"Property {new_prop_label or new_prop_id} als {selected_category} hinzugefügt!")
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
                        st.markdown('<span class="delete-btn-marker"></span>', unsafe_allow_html=True)
                        if st.button(f"Property '{prop_id}' löschen", key=f"init_del_inactive_{prop_id}"):
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
                        st.markdown('<span class="delete-btn-marker"></span>', unsafe_allow_html=True)
                        if st.button(f"Property '{prop_id}' löschen", key=f"init_del_active_{prop_id}"):
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
            "von Property- und Faktor-Overrides beim Lauf anwenden (Tab Properties)."
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
        help="Speichert PNGs unter outputs/<run_id>/figures/ und zeigt sie im Tab Figures.",
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

    if "save_success_msg" in st.session_state:
        st.success(st.session_state.save_success_msg)
        del st.session_state.save_success_msg

    st.divider()
    preset_name = st.text_input("Als Szenario speichern (configs/sweeps/)", value="mein_szenario")
    if st.button("Szenario speichern"):
        try:
            # Run-Name und Szenario-Name synchronisieren, wie vom User gewünscht
            draft.simulation_name = preset_name
            path = save_custom_sweep_preset(draft, preset_name)
            st.session_state.config_draft = draft
            st.session_state.save_success_msg = f"Gespeichert: `{path}`"
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    return draft


def _render_population_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Bevölkerungs-Struktur (Agenten)")
    st.info(
        "Diese Einstellungen steuern die Wahrscheinlichkeitsverteilungen beim Simulationsstart. "
        "Segment-Anteile sind **unabhängig** — eine Person kann mehreren Segmenten gleichzeitig angehören "
        "(z. B. business und price_sensitive)."
    )
    
    if st.button("Populations-Config aus JSON neu laden", key="btn_reload_pop"):
        draft.population_edits = extract_population_edits_from_file(draft.properties_file)
        draft.saturation_edit = extract_saturation_from_file(draft.properties_file)
        st.rerun()

    st.markdown("### Sättigung (global)")
    st.caption(
        "Nach einer Buchung steigt das Sättigungslevel; es baut sich pro Tick über die segment-spezifische "
        "Erholungsrate wieder ab und reduziert die Logit-Buchungswahrscheinlichkeit."
    )
    sat = draft.saturation_edit
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sat.booking_increase = st.number_input(
            "Sättigungs-Anstieg bei Buchung",
            min_value=0.0,
            max_value=1.0,
            value=float(sat.booking_increase),
            step=0.05,
            format="%.2f",
            key="sat_booking_increase",
        )
    with col_s2:
        sat.utility_penalty_factor = st.number_input(
            "Logit-Penalty-Faktor",
            min_value=0.0,
            max_value=3.0,
            value=float(sat.utility_penalty_factor),
            step=0.1,
            format="%.2f",
            key="sat_penalty_factor",
            help="Multiplikator auf saturation_level in der Nutzenfunktion.",
        )

    st.markdown("### Segmente (Anteile & Verhalten)")
    if not hasattr(draft, "population_edits") or not draft.population_edits:
        draft.population_edits = extract_population_edits_from_file(draft.properties_file)

    with st.container(border=True):
        st.markdown("**Neues Segment hinzufügen**")
        c1, c2 = st.columns([3, 1])
        new_seg_id = c1.text_input("Segment ID (z.B. family_traveler)", key="new_seg_id")
        c2.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if c2.button("Segment Hinzufügen", key="btn_add_seg", type="primary", use_container_width=True):
            if new_seg_id and new_seg_id.isidentifier():
                if any(e.id == new_seg_id for e in draft.population_edits):
                    st.error("Ein Segment mit dieser ID existiert bereits!")
                else:
                    new_seg = PopulationEditState(
                        id=new_seg_id, type="boolean", prevalence=0.1, saturation_decay=0.2
                    )
                    draft.population_edits.insert(0, new_seg)
                    save_population_edits_to_file(draft.population_edits, draft.properties_file)
                    st.success(f"Segment '{new_seg_id}' angelegt!")
                    st.rerun()
            else:
                st.error("Ungültige ID. Bitte nur Buchstaben und Unterstriche verwenden.")

    boolean_props = [p for p in draft.population_edits if p.type == "boolean"]
    cols = st.columns(3)
    for i, p in enumerate(boolean_props):
        with cols[i % 3]:
            label = p.id.replace("_", " ").title()
            with st.container(border=True):
                st.markdown(f"**{label}**")
                
                val_prev = float(p.prevalence) if p.prevalence is not None else 0.0
                new_prev = st.slider("Anteil (Prevalence)", 0.0, 1.0, val_prev, 0.05, key=f"pop_prev_{p.id}")
                p.prevalence = new_prev
                if p.exclusive_group:
                    st.caption(
                        f"Exklusive Gruppe `{p.exclusive_group}`: nur ein Segment dieser Gruppe pro Person."
                    )
                
                val_decay = float(p.saturation_decay) if p.saturation_decay is not None else 0.2
                new_decay = st.slider("Erholung pro Tick (Decay)", 0.0, 1.0, val_decay, 0.05, key=f"pop_decay_{p.id}", help="Wieviel Sättigung wird pro Zeiteinheit abgebaut (0.0=nie, 1.0=sofort)")
                p.saturation_decay = new_decay

                with st.expander("Modifikatoren (Verhalten)", expanded=False):
                    wtp = st.number_input("Zahlungsbereitschaft (WTP) Multiplikator", value=float(p.modifiers.get("wtp_multiplier", 1.0)), step=0.05, format="%.2f", key=f"mod_wtp_{p.id}")
                    inc = st.number_input("Einkommen Delta", value=float(p.modifiers.get("base_income_delta", 0.0)), step=0.05, format="%.2f", key=f"mod_inc_{p.id}")
                    price = st.number_input("Preissensibilität Delta", value=float(p.modifiers.get("price_sensitivity_delta", 0.0)), step=0.05, format="%.2f", key=f"mod_price_{p.id}")
                    subst = st.number_input("Bahn-Wechselbereitschaft Multiplikator", value=float(p.modifiers.get("substitution_readiness_multiplier", 1.0)), step=0.05, format="%.2f", key=f"mod_subst_{p.id}")
                    
                    p.modifiers["wtp_multiplier"] = wtp
                    p.modifiers["base_income_delta"] = inc
                    p.modifiers["price_sensitivity_delta"] = price
                    p.modifiers["substitution_readiness_multiplier"] = subst

                    LEGACY_SEGMENTS = {"business", "price_sensitive", "eco_conscious", "frequent_flyer"}
                    if p.id not in LEGACY_SEGMENTS:
                        st.divider()
                        confirm_key = f"confirm_del_seg_{p.id}"
                        if st.session_state.get(confirm_key, False):
                            st.warning(f"Segment '{p.id}' wirklich löschen?")
                            c1, c2 = st.columns(2)
                            if c1.button("Ja, löschen", key=f"do_del_seg_{p.id}"):
                                st.session_state[confirm_key] = False
                                draft.population_edits = [e for e in draft.population_edits if e.id != p.id]
                                save_population_edits_to_file(draft.population_edits, draft.properties_file)
                                st.success(f"Segment {p.id} gelöscht!")
                                st.rerun()
                            if c2.button("Abbruch", key=f"cancel_del_seg_{p.id}"):
                                st.session_state[confirm_key] = False
                                st.rerun()
                        else:
                            st.markdown('<span class="delete-btn-marker"></span>', unsafe_allow_html=True)
                            if st.button(f"Segment '{p.id}' löschen", key=f"init_del_seg_{p.id}", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()

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
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        save_saturation_to_file(draft.saturation_edit, draft.properties_file)
        st.success("Populations- und Sättigungs-Konfiguration gespeichert!")

    return draft


def render_config_editor() -> ConfigDraft:
    st.markdown("""
        <style>
        div.element-container:has(.delete-btn-marker) + div.element-container button {
            background-color: #8b0000 !important;
            color: white !important;
            border-color: #8b0000 !important;
        }
        div.element-container:has(.delete-btn-marker) + div.element-container button:hover {
            background-color: #ff4b4b !important;
            border-color: #ff4b4b !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_config_draft()
    draft: ConfigDraft = st.session_state.config_draft

    if st.button("Auf Standard-Config zurücksetzen"):
        draft = default_config_draft()
        _clear_factor_widget_keys(draft)
        st.session_state.config_draft = draft
        st.rerun()

    tabs = st.tabs(["Experiment und Datenbasis", "Makro-Parameter", "Mikro-Parameter und Bevoelkerung", "LLM und Pipeline", "Speichern und Starten"])
    with tabs[0]:
        draft = _render_tab_experiment(draft)
    with tabs[1]:
        draft = _render_tab_macro(draft)
    with tabs[2]:
        draft = _render_tab_micro(draft)
    with tabs[3]:
        draft = _render_llm_pipeline_tab(draft)
    with tabs[4]:
        draft = _render_tab_save_start(draft)

    st.session_state.config_draft = draft
    return draft

def _render_tab_experiment(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Experiment und Datenbasis")
    st.caption("Grundlegende Einstellungen fuer den Lauf. Die JSON-Basisdateien (properties, factors, etc.) werden automatisch aus dem configs/ Ordner geladen.")
    
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
            "Szenario Preset",
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

        if st.button("Szenario-Parameter uebernehmen", key="apply_sweep"):
            draft = apply_sweep_to_draft(draft, sweep)
            _clear_factor_widget_keys(draft)
            st.session_state.config_draft = draft
            st.success(f"Parameter von {sweep.name} uebernommen.")
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
        st.caption("Properties und Faktoren in den naechsten Tabs anpassen.")
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
                "Anzahl Laeufe (Multi-Run)",
                min_value=1,
                max_value=20,
                value=int(draft.run_count),
                step=1,
                help="Mehrere unabhaengige Laeufe mit gleicher Config; Seeds werden hochgezaehlt. Ergebnis unter outputs/batch_<Zeitstempel>/run_001",
            )
            
    draft.simulation_name = st.text_input("Run-Name (optional)", value=draft.simulation_name)
    draft.simulation_description = st.text_area(
        "Run-Beschreibung (optional)",
        value=draft.simulation_description,
        height=80,
    )
            
    return draft

def _render_tab_macro(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Makro-Parameter")
    
    st.markdown("### Faktoren-Startzustaende")
    st.caption("Startzustaende F1-F7 vor dem Lauf.")
    if not (draft.apply_custom_overrides or draft.scenario_mode == "custom"):
        st.warning("Overrides sind deaktiviert.")
    options = factor_options_from_file(draft.factors_file)
    if options:
        if draft.factors_file != "factors.json":
            if st.button("Faktoren neu laden"):
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
                
    st.divider()
    st.markdown("### System-Properties (Steuern & Gebuehren)")
    
    col_bp1, col_bp2 = st.columns([1, 3])
    with col_bp1:
        enable_base_price = st.checkbox(
            "Basispreis ueberschreiben",
            value=draft.base_price is not None,
            key="enable_base_price",
        )
    with col_bp2:
        if enable_base_price:
            draft.base_price = st.number_input(
                "Basispreis (EUR)",
                min_value=1.0,
                max_value=1000.0,
                value=float(draft.base_price) if draft.base_price is not None else 100.0,
                step=5.0,
                format="%.1f",
                key="base_price_input",
            )
        else:
            draft.base_price = None
            
    if draft.properties_file != "properties.json":
        if st.button("Properties aus Datei neu laden"):
            draft.property_edits = extract_property_edits_from_file(draft.properties_file)
            st.rerun()

    draft.apply_custom_overrides = st.checkbox(
        "Property- und Faktor-Overrides anwenden",
        value=draft.apply_custom_overrides or draft.scenario_mode == "custom",
    )
    
    with st.container(border=True):
        st.markdown("**Neue Property hinzufuegen**")
        c1, c2, c3 = st.columns([2, 2, 2])
        new_prop_id = c1.text_input("Property ID", placeholder="z.B. airport_fee", key="new_prop_id")
        new_prop_label = c2.text_input("Anzeigename", placeholder="z.B. Airport Fee", key="new_prop_label")
        
        price_category_options = {
            "Keine Preisbindung": "none",
            "Steuer (Prozentual auf Ticketpreis)": "tax",
            "Gebuehr (Absoluter EUR-Betrag)": "fee",
        }
        selected_category = c3.selectbox(
            "Preiskategorie",
            options=list(price_category_options.keys()),
            index=0,
            key="new_prop_price_category",
        )
        price_component_type = price_category_options[selected_category]
        
        if st.button("Property Hinzufuegen", type="primary", use_container_width=True):
            if new_prop_id and new_prop_id.isidentifier():
                add_custom_property(new_prop_id, new_prop_label, draft.properties_file, price_component_type)
                draft.property_edits = extract_property_edits_from_file(draft.properties_file)
                st.success("Property hinzugefuegt!")
                st.rerun()

    _props_data = load_config_file(draft.properties_file)
    _price_component_map = {}
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
            badge = " Gebuehr (EUR)"
        with st.expander(f"{label}{badge}", expanded=False):
            is_active = st.checkbox("In dieser Simulation aktiv", value=edit.is_active, key=f"prop_active_{prop_id}")
            edit.is_active = is_active
            if not is_active:
                st.info("Deaktiviert")
                continue
            baseline = st.number_input("Baseline", value=float(edit.baseline), format="%.4f", key=f"prop_base_{prop_id}")
            st.markdown("**Regeln**")
            rule_count = st.number_input("Anzahl Regeln", min_value=0, max_value=8, value=len(edit.rules), step=1, key=f"prop_rule_count_{prop_id}")
            new_rules = []
            for idx in range(int(rule_count)):
                existing = edit.rules[idx] if idx < len(edit.rules) else {}
                effect = existing.get("effect") or {}
                effect_type = effect.get("type", "set")
                
                cols = st.columns([1, 1, 1, 1])
                tick = cols[0].number_input(f"Tick #{idx + 1}", min_value=1, max_value=500, value=int(existing.get("active_from_tick", 1)), key=f"prop_rule_tick_{prop_id}_{idx}")
                r_type = cols[1].selectbox(f"Typ #{idx + 1}", ["set", "ramp"], index=0 if effect_type == "set" else 1, key=f"prop_rule_type_{prop_id}_{idx}")
                value = cols[2].number_input(f"Wert #{idx + 1}", value=float(effect.get("value", baseline)), format="%.4f", key=f"prop_rule_val_{prop_id}_{idx}")
                
                new_effect = {"type": r_type, "value": float(value)}
                if r_type == "ramp":
                    duration = cols[3].number_input(f"Dauer #{idx + 1}", min_value=1, max_value=100, value=int(effect.get("duration_ticks", 5)), key=f"prop_rule_dur_{prop_id}_{idx}")
                    new_effect["duration_ticks"] = int(duration)

                new_rules.append({"active_from_tick": int(tick), "effect": new_effect})
            draft.property_edits[prop_id] = PropertyEditState(property_id=prop_id, baseline=float(baseline), rules=new_rules, is_active=is_active)
    
    return draft

def _render_tab_micro(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Mikro-Parameter und Bevoelkerung")
    
    st.markdown("### Yield / Markt-Feedback")
    mf = draft.market_feedback_edit
    mf.enabled = st.checkbox("Markt-Feedback aktiv", value=mf.enabled, key="mf_enabled")
    col_mf1, col_mf2, col_mf3 = st.columns(3)
    with col_mf1:
        mf.target_booking_rate = st.number_input("Ziel-Buchungsrate", min_value=0.05, max_value=1.0, value=float(mf.target_booking_rate), step=0.01, key="mf_target_br")
        mf.marginal_cost_fraction = st.number_input("Grenzkosten-Anteil", min_value=0.05, max_value=1.0, value=float(mf.marginal_cost_fraction), step=0.01, key="mf_marginal_cost")
    with col_mf2:
        mf.markup_adjustment_per_tick = st.number_input("Markup-Anpassung / Tick", min_value=0.01, max_value=0.5, value=float(mf.markup_adjustment_per_tick), step=0.01, key="mf_markup_adj")
        mf.damping = st.number_input("Daempfung", min_value=0.1, max_value=1.0, value=float(mf.damping), step=0.05, key="mf_damping")
    with col_mf3:
        mf.max_price_change_fraction = st.number_input("Max. Preisaenderung / Tick", min_value=0.01, max_value=0.5, value=float(mf.max_price_change_fraction), step=0.01, key="mf_max_price_chg")
        mf.booking_weight = st.number_input("Booking-Gewicht", min_value=0.0, max_value=1.0, value=float(mf.booking_weight), step=0.05, key="mf_booking_weight")
    if st.button("Markt-Feedback speichern", key="btn_save_market_feedback", type="secondary"):
        save_market_feedback_to_file(mf, draft.properties_file)
        st.success("Gespeichert.")

    st.divider()

    st.markdown("### Saettigung (global)")
    sat = draft.saturation_edit
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sat.booking_increase = st.number_input("Saettigungs-Anstieg bei Buchung", min_value=0.0, max_value=1.0, value=float(sat.booking_increase), step=0.05, key="sat_booking_increase")
    with col_s2:
        sat.utility_penalty_factor = st.number_input("Logit-Penalty-Faktor", min_value=0.0, max_value=3.0, value=float(sat.utility_penalty_factor), step=0.1, key="sat_penalty_factor")

    st.divider()

    st.markdown("### Segmente")
    if not hasattr(draft, "population_edits") or not draft.population_edits:
        draft.population_edits = extract_population_edits_from_file(draft.properties_file)

    with st.container(border=True):
        st.markdown("**Neues Segment hinzufuegen**")
        c1, c2 = st.columns([3, 1])
        new_seg_id = c1.text_input("Segment ID", key="new_seg_id")
        if c2.button("Segment Hinzufuegen", key="btn_add_seg", type="primary"):
            if new_seg_id and new_seg_id.isidentifier():
                if any(e.id == new_seg_id for e in draft.population_edits):
                    st.error("Existiert bereits!")
                else:
                    new_seg = PopulationEditState(id=new_seg_id, type="boolean", prevalence=0.1, saturation_decay=0.2)
                    draft.population_edits.insert(0, new_seg)
                    save_population_edits_to_file(draft.population_edits, draft.properties_file)
                    st.success("Angelegt!")
                    st.rerun()

    boolean_props = [p for p in draft.population_edits if p.type == "boolean"]
    cols = st.columns(3)
    for i, p in enumerate(boolean_props):
        with cols[i % 3]:
            label = p.id.replace("_", " ").title()
            with st.container(border=True):
                st.markdown(f"**{label}**")
                
                val_prev = float(p.prevalence) if p.prevalence is not None else 0.0
                new_prev = st.slider("Anteil (Prevalence)", 0.0, 1.0, val_prev, 0.05, key=f"pop_prev_{p.id}")
                p.prevalence = new_prev
                
                val_decay = float(p.saturation_decay) if p.saturation_decay is not None else 0.2
                new_decay = st.slider("Erholung pro Tick (Decay)", 0.0, 1.0, val_decay, 0.05, key=f"pop_decay_{p.id}")
                p.saturation_decay = new_decay

                with st.expander("Modifikatoren", expanded=False):
                    p.modifiers["wtp_multiplier"] = st.number_input("WTP Multiplikator", value=float(p.modifiers.get("wtp_multiplier", 1.0)), step=0.05, key=f"mod_wtp_{p.id}")
                    p.modifiers["base_income_delta"] = st.number_input("Einkommen Delta", value=float(p.modifiers.get("base_income_delta", 0.0)), step=0.05, key=f"mod_inc_{p.id}")
                    p.modifiers["price_sensitivity_delta"] = st.number_input("Preissensibilitaet Delta", value=float(p.modifiers.get("price_sensitivity_delta", 0.0)), step=0.05, key=f"mod_price_{p.id}")
                    p.modifiers["substitution_readiness_multiplier"] = st.number_input("Bahn-Wechselbereitschaft", value=float(p.modifiers.get("substitution_readiness_multiplier", 1.0)), step=0.05, key=f"mod_subst_{p.id}")

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
    if st.button("Aenderungen an Population speichern", type="primary"):
        save_population_edits_to_file(draft.population_edits, draft.properties_file)
        save_saturation_to_file(draft.saturation_edit, draft.properties_file)
        st.success("Gespeichert!")

    return draft

def _render_tab_save_start(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Speichern und Starten")
    
    with st.expander("JSON-Vorschau: simulation_config.json", expanded=False):
        st.json(load_config_file(draft.simulation_config_file))
    with st.expander("JSON-Vorschau: properties.json (Auszug)", expanded=False):
        props = load_config_file(draft.properties_file)
        st.json({"system_properties": props.get("system_properties", [])[:3], "...": "gekuerzt"})

    st.divider()
    if "save_success_msg" in st.session_state:
        st.success(st.session_state.save_success_msg)
        del st.session_state.save_success_msg

    preset_name = st.text_input("Als Szenario speichern (configs/sweeps/)", value="mein_szenario", key="preset_name_2")
    if st.button("Szenario speichern", key="btn_save_2"):
        try:
            draft.simulation_name = preset_name
            path = save_custom_sweep_preset(draft, preset_name)
            st.session_state.config_draft = draft
            st.session_state.save_success_msg = f"Gespeichert: `{path}`"
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
            
    st.divider()
    st.subheader("Effektive Konfiguration")
    st.json(effective_config_summary(draft))

    return draft
