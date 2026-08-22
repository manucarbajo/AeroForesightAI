"""Config-editor building blocks shared by config_ui.py (7-tab ops layout) and
config_ui_researcher.py (5-tab researcher layout) - each arranges these into a
different tab structure, so only the genuinely shared pieces live here."""

from __future__ import annotations

import streamlit as st

from dashboard.config_catalog import (
    ConfigDraft,
    default_config_draft,
    extract_market_feedback_from_file,
    extract_saturation_from_file,
    factor_options_from_file,
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


def clear_factor_widget_keys(draft: ConfigDraft) -> None:
    """Remove stale Streamlit keys so factor selectboxes follow ``draft.factor_states``."""
    for factor_id in factor_options_from_file(draft.factors_file):
        st.session_state.pop(f"factor_{factor_id}", None)


def render_llm_pipeline_tab(draft: ConfigDraft) -> ConfigDraft:
    st.subheader("LLM & Pipeline")
    c1, c2 = st.columns(2)
    with c1:
        draft.mock_llm = st.checkbox("Mock-LLM", value=draft.mock_llm)
        draft.deterministic_only = st.checkbox(
            "Deterministisch (ohne Agenten-LLM)", value=draft.deterministic_only
        )
        draft.model = st.text_input("Ollama-Modell", value=draft.model)
        draft.base_url = st.text_input("Ollama Base-URL", value=draft.base_url)
    with c2:
        draft.temperature = st.slider("Temperature", 0.0, 1.5, float(draft.temperature), 0.05)
        draft.max_tokens = st.number_input(
            "Max Tokens", min_value=256, max_value=8192, value=int(draft.max_tokens)
        )
        draft.checkpoint_interval = st.number_input(
            "Checkpoint alle N Ticks", min_value=0, value=int(draft.checkpoint_interval)
        )
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
