"""Streamlit-UI zum Bearbeiten der vollen Simulations-Konfiguration (Researcher-Layout).

5-Tab-Umgruppierung derselben Felder wie config_ui.py's 7-Tab-Layout; die
tatsächlichen Feld-Renderer, die beide Varianten unverändert teilen
(init_config_draft, clear_factor_widget_keys, render_llm_pipeline_tab),
leben in dashboard/config_fields.py.
"""

from __future__ import annotations

import streamlit as st

from dashboard.config_catalog import (
    PROPERTY_LABELS,
    ConfigDraft,
    PopulationEditState,
    PropertyEditState,
    add_custom_property,
    apply_sweep_to_draft,
    default_config_draft,
    effective_config_summary,
    extract_factor_states_from_file,
    extract_population_edits_from_file,
    extract_property_edits_from_file,
    factor_options_from_file,
    get_editable_property_ids,
    list_sweep_presets,
    load_config_file,
    save_custom_sweep_preset,
    save_market_feedback_to_file,
    save_population_edits_to_file,
    save_saturation_to_file,
)
from dashboard.legacy_streamlit.config_fields import (
    clear_factor_widget_keys,
    init_config_draft,
    render_llm_pipeline_tab,
)


def render_config_editor() -> ConfigDraft:
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    init_config_draft()
    draft: ConfigDraft = st.session_state.config_draft

    if st.button("Auf Standard-Config zurücksetzen"):
        draft = default_config_draft()
        clear_factor_widget_keys(draft)
        st.session_state.config_draft = draft
        st.rerun()

    tabs = st.tabs(
        [
            "Experiment und Datenbasis",
            "Makro-Parameter",
            "Mikro-Parameter und Bevoelkerung",
            "LLM und Pipeline",
            "Speichern und Starten",
        ]
    )
    with tabs[0]:
        draft = _render_tab_experiment(draft)
    with tabs[1]:
        draft = _render_tab_macro(draft)
    with tabs[2]:
        draft = _render_tab_micro(draft)
    with tabs[3]:
        draft = render_llm_pipeline_tab(draft)
    with tabs[4]:
        draft = _render_tab_save_start(draft)

    st.session_state.config_draft = draft
    return draft


def _render_tab_experiment(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Experiment und Datenbasis")
    st.caption(
        "Grundlegende Einstellungen fuer den Lauf. Die JSON-Basisdateien (properties, factors, etc.) werden automatisch aus dem configs/ Ordner geladen."
    )

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
            clear_factor_widget_keys(draft)
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
        st.caption("Properties und Faktoren in den naechsten Tabs anpassen.")
        draft.rounds = st.number_input(
            "Ticks", min_value=1, max_value=500, value=draft.rounds, step=1
        )
    else:
        draft.sweep_id = None
        sim = load_config_file(draft.simulation_config_file)
        default_ticks = int(sim.get("clock", {}).get("max_ticks", draft.rounds))
        draft.rounds = st.number_input(
            "Ticks", min_value=1, max_value=500, value=default_ticks, step=1
        )

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
                clear_factor_widget_keys(draft)
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
        new_prop_id = c1.text_input(
            "Property ID", placeholder="z.B. airport_fee", key="new_prop_id"
        )
        new_prop_label = c2.text_input(
            "Anzeigename", placeholder="z.B. Airport Fee", key="new_prop_label"
        )

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
                add_custom_property(
                    new_prop_id, new_prop_label, draft.properties_file, price_component_type
                )
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
            is_active = st.checkbox(
                "In dieser Simulation aktiv", value=edit.is_active, key=f"prop_active_{prop_id}"
            )
            edit.is_active = is_active
            if not is_active:
                st.info("Deaktiviert")
                continue
            baseline = st.number_input(
                "Baseline", value=float(edit.baseline), format="%.4f", key=f"prop_base_{prop_id}"
            )
            st.markdown("**Regeln**")
            rule_count = st.number_input(
                "Anzahl Regeln",
                min_value=0,
                max_value=8,
                value=len(edit.rules),
                step=1,
                key=f"prop_rule_count_{prop_id}",
            )
            new_rules = []
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
                        f"Dauer #{idx + 1}",
                        min_value=1,
                        max_value=100,
                        value=int(effect.get("duration_ticks", 5)),
                        key=f"prop_rule_dur_{prop_id}_{idx}",
                    )
                    new_effect["duration_ticks"] = int(duration)

                new_rules.append({"active_from_tick": int(tick), "effect": new_effect})
            draft.property_edits[prop_id] = PropertyEditState(
                property_id=prop_id, baseline=float(baseline), rules=new_rules, is_active=is_active
            )

    return draft


def _render_tab_micro(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("Mikro-Parameter und Bevoelkerung")

    st.markdown("### Yield / Markt-Feedback")
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
            key="mf_target_br",
        )
        mf.marginal_cost_fraction = st.number_input(
            "Grenzkosten-Anteil",
            min_value=0.05,
            max_value=1.0,
            value=float(mf.marginal_cost_fraction),
            step=0.01,
            key="mf_marginal_cost",
        )
    with col_mf2:
        mf.markup_adjustment_per_tick = st.number_input(
            "Markup-Anpassung / Tick",
            min_value=0.01,
            max_value=0.5,
            value=float(mf.markup_adjustment_per_tick),
            step=0.01,
            key="mf_markup_adj",
        )
        mf.damping = st.number_input(
            "Daempfung",
            min_value=0.1,
            max_value=1.0,
            value=float(mf.damping),
            step=0.05,
            key="mf_damping",
        )
    with col_mf3:
        mf.max_price_change_fraction = st.number_input(
            "Max. Preisaenderung / Tick",
            min_value=0.01,
            max_value=0.5,
            value=float(mf.max_price_change_fraction),
            step=0.01,
            key="mf_max_price_chg",
        )
        mf.booking_weight = st.number_input(
            "Booking-Gewicht",
            min_value=0.0,
            max_value=1.0,
            value=float(mf.booking_weight),
            step=0.05,
            key="mf_booking_weight",
        )
    if st.button("Markt-Feedback speichern", key="btn_save_market_feedback", type="secondary"):
        save_market_feedback_to_file(mf, draft.properties_file)
        st.success("Gespeichert.")

    st.divider()

    st.markdown("### Saettigung (global)")
    sat = draft.saturation_edit
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sat.booking_increase = st.number_input(
            "Saettigungs-Anstieg bei Buchung",
            min_value=0.0,
            max_value=1.0,
            value=float(sat.booking_increase),
            step=0.05,
            key="sat_booking_increase",
        )
    with col_s2:
        sat.utility_penalty_factor = st.number_input(
            "Logit-Penalty-Faktor",
            min_value=0.0,
            max_value=3.0,
            value=float(sat.utility_penalty_factor),
            step=0.1,
            key="sat_penalty_factor",
        )

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
                    new_seg = PopulationEditState(
                        id=new_seg_id, type="boolean", prevalence=0.1, saturation_decay=0.2
                    )
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
                new_prev = st.slider(
                    "Anteil (Prevalence)", 0.0, 1.0, val_prev, 0.05, key=f"pop_prev_{p.id}"
                )
                p.prevalence = new_prev

                val_decay = float(p.saturation_decay) if p.saturation_decay is not None else 0.2
                new_decay = st.slider(
                    "Erholung pro Tick (Decay)", 0.0, 1.0, val_decay, 0.05, key=f"pop_decay_{p.id}"
                )
                p.saturation_decay = new_decay

                with st.expander("Modifikatoren", expanded=False):
                    p.modifiers["wtp_multiplier"] = st.number_input(
                        "WTP Multiplikator",
                        value=float(p.modifiers.get("wtp_multiplier", 1.0)),
                        step=0.05,
                        key=f"mod_wtp_{p.id}",
                    )
                    p.modifiers["base_income_delta"] = st.number_input(
                        "Einkommen Delta",
                        value=float(p.modifiers.get("base_income_delta", 0.0)),
                        step=0.05,
                        key=f"mod_inc_{p.id}",
                    )
                    p.modifiers["price_sensitivity_delta"] = st.number_input(
                        "Preissensibilitaet Delta",
                        value=float(p.modifiers.get("price_sensitivity_delta", 0.0)),
                        step=0.05,
                        key=f"mod_price_{p.id}",
                    )
                    p.modifiers["substitution_readiness_multiplier"] = st.number_input(
                        "Bahn-Wechselbereitschaft",
                        value=float(p.modifiers.get("substitution_readiness_multiplier", 1.0)),
                        step=0.05,
                        key=f"mod_subst_{p.id}",
                    )

    st.markdown("### Eigenschaften-Verteilungen")
    dist_props = [p for p in draft.population_edits if p.type == "distribution"]
    for p in dist_props:
        label = p.id.replace("_", " ").title()
        if p.id == "wtp_eur":
            label = "Zahlungsbereitschaft (WTP in Euro)"
        if p.id == "environmental_awareness":
            label = "Umweltbewusstsein (0-1)"

        with st.expander(label, expanded=False):
            dist_opts = ["normal", "beta", "lognormal", "uniform"]
            current_dist = p.distribution if p.distribution in dist_opts else "normal"
            dist_type = st.selectbox(
                "Verteilungstyp",
                dist_opts,
                index=dist_opts.index(current_dist),
                key=f"pop_dist_{p.id}",
            )
            p.distribution = dist_type

            c1, c2, c3, c4 = st.columns(4)
            if dist_type in ("normal", "lognormal"):
                with c1:
                    p.mean = st.number_input(
                        "Mittelwert", value=p.mean or 0.0, format="%.2f", key=f"pop_mean_{p.id}"
                    )
                with c2:
                    p.std_dev = st.number_input(
                        "Std Dev", value=p.std_dev or 1.0, format="%.2f", key=f"pop_std_{p.id}"
                    )
                with c3:
                    p.min_value = st.number_input(
                        "Min", value=p.min_value or 0.0, format="%.2f", key=f"pop_min_{p.id}"
                    )
                with c4:
                    p.max_value = st.number_input(
                        "Max", value=p.max_value or 1.0, format="%.2f", key=f"pop_max_{p.id}"
                    )
            elif dist_type == "beta":
                with c1:
                    p.alpha = st.number_input(
                        "Alpha", value=p.alpha or 2.0, format="%.2f", key=f"pop_alpha_{p.id}"
                    )
                with c2:
                    p.beta = st.number_input(
                        "Beta", value=p.beta or 5.0, format="%.2f", key=f"pop_beta_{p.id}"
                    )
                with c3:
                    p.min_value = st.number_input(
                        "Min", value=p.min_value or 0.0, format="%.2f", key=f"pop_min_{p.id}"
                    )
                with c4:
                    p.max_value = st.number_input(
                        "Max", value=p.max_value or 1.0, format="%.2f", key=f"pop_max_{p.id}"
                    )

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

    preset_name = st.text_input(
        "Als Szenario speichern (configs/sweeps/)", value="mein_szenario", key="preset_name_2"
    )
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
