"""Streamlit view functions shared by app.py (ops) and app_researcher.py (deep-dive).

The two entry points differ only in their animation tab and figures tab
(pre-rendered PNGs vs. live Plotly dashboards) and in which config editor
they use. Everything else - session state, scenario/overview/narrative/
explorer/files tabs, the launch page, the run browser, and page setup -
lives here once, injected with the two variant renderers and the config
editor via parameters instead of being duplicated per file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import streamlit as st

from dashboard.service import (
    REPO_ROOT,
    launch_from_draft,
    list_run_files,
    list_runs,
    load_price_series,
    load_run_scenario,
    load_tick_mechanics,
    outputs_root,
    read_run_file,
    regenerate_run_scenario,
    run_consistency_checks,
)
from src.reporting.state_explorer import (
    StateExplorer,
    build_grounded_context_block,
    load_run_context,
    parse_tick_hint,
)


def init_session_state() -> None:
    defaults = {
        "selected_run_id": None,
        "explorer_messages": {},
        "last_launched_run_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_overview(run_dir: Path, run_id: str) -> None:
    metadata_path = run_dir / "run_metadata.json"
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        cols = st.columns(4)
        cols[0].metric(
            "Ticks", f"{metadata.get('ticks_completed', '?')} / {metadata.get('ticks_max', '?')}"
        )
        cols[1].metric("Events", metadata.get("total_events", "?"))
        cols[2].metric("Modell", metadata.get("model", "—"))
        cols[3].metric("Markt", "an" if metadata.get("market_enabled", True) else "aus")
        st.caption(f"Run-ID: `{run_id}` · erstellt {metadata.get('timestamp', '—')}")

    ticks = load_tick_mechanics(run_dir)
    prices = load_price_series(run_dir)
    if not ticks and not prices:
        st.info("Keine Zeitreihen-Daten vorhanden.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    if ticks:
        x = [int(row["tick"]) for row in ticks if row.get("tick") is not None]
        booking = [
            float(row["booking_rate"]) for row in ticks if row.get("booking_rate") is not None
        ]
        if x and booking and len(x) == len(booking):
            axes[0].plot(x, booking, marker="o", color="#2563eb")
            axes[0].set_title("Booking Rate")
            axes[0].set_xlabel("Tick")
            axes[0].set_ylim(0, 1)
            axes[0].grid(True, alpha=0.3)

    if prices:
        x = [int(row["round_number"]) for row in prices if row.get("round_number") is not None]
        y = [float(row["price"]) for row in prices if row.get("price") is not None]
        if x and y and len(x) == len(y):
            axes[1].plot(x, y, marker="o", color="#059669")
            axes[1].set_title("Ticketpreis")
            axes[1].set_xlabel("Tick")
            axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_scenario(run_dir: Path, run_id: str) -> None:
    scenario = load_run_scenario(run_dir)
    md_path = run_dir / "run_scenario.md"

    col1, col2 = st.columns([1, 3])
    with col1:
        regenerate = st.button("Szenarien neu erzeugen", width="stretch")
    with col2:
        st.caption("P3 — Szenarien aus dem Lauf: Tick-Anhaltspunkte und sachliche Beschreibung.")

    if regenerate:
        with st.spinner("Szenarien werden erzeugt …"):
            try:
                regenerate_run_scenario(
                    run_id, run_dir=run_dir, mock_llm=True, deterministic_only=True
                )
                st.success("Szenarien aktualisiert.")
                st.rerun()
            except Exception as exc:
                st.error(f"Szenario-Erzeugung fehlgeschlagen: {exc}")
                return

    if scenario:
        title = scenario.get("title")
        summary = scenario.get("summary")
        if title:
            st.subheader(str(title))
        if summary:
            st.markdown(str(summary))

        narrative = scenario.get("narrative") if isinstance(scenario.get("narrative"), dict) else {}
        run_story = (
            scenario.get("run_narrative")
            or narrative.get("run_narrative")
            or scenario.get("observed_run")
        )
        if run_story:
            st.markdown("**Lauf-Narrativ — was im Lauf passiert ist**")
            st.markdown(str(run_story))

        scenarios = scenario.get("scenarios") or narrative.get("scenarios") or []
        if scenarios:
            st.markdown("### Szenarien")
            for item in scenarios:
                if not isinstance(item, dict):
                    continue
                rank = item.get("rank", "?")
                header = f"{rank}. {item.get('title', 'Szenario')}"
                with st.expander(header, expanded=int(item.get("rank", 99)) == 1):
                    st.markdown("**Anhaltspunkte aus dem Lauf (Ticks)**")
                    st.markdown(str(item.get("tick_grounding", "")))
                    st.markdown("**Szenario-Beschreibung**")
                    st.markdown(str(item.get("story") or item.get("what_could_happen", "")))

        source = scenario.get("source")
        if source:
            st.caption(f"Quelle: `{source}`")
        warnings = scenario.get("grounding_warnings") or []
        if warnings:
            st.warning("Grounding-Hinweise: " + "; ".join(str(item) for item in warnings[:5]))

        ground_truth = scenario.get("ground_truth")
        if isinstance(ground_truth, dict) and ground_truth:
            with st.expander("Ground Truth (Python-Kennzahlen)", expanded=False):
                st.json(ground_truth)

    if md_path.is_file() and not scenario:
        st.markdown(read_run_file(md_path))
    elif md_path.is_file():
        with st.expander("Vollständiges Markdown (`run_scenario.md`)", expanded=False):
            st.markdown(read_run_file(md_path))
    elif not scenario:
        st.warning(
            "`run_scenario.md` fehlt in diesem Run. "
            "Starten Sie eine neue Simulation oder klicken Sie auf «Szenarien neu erzeugen»."
        )


def render_narrative(run_dir: Path) -> None:
    narrative_path = run_dir / "final_narrative.md"
    if not narrative_path.is_file():
        st.warning("`final_narrative.md` fehlt in diesem Run.")
        return
    st.markdown(read_run_file(narrative_path))


def _resolve_focus_tick(manual_tick: int, question: str) -> int | None:
    if manual_tick > 0:
        return manual_tick
    return parse_tick_hint(question)


def render_explorer(run_id: str) -> None:
    st.markdown(
        "Fragen Sie den gesamten Lauf ab — z. B. Verlauf über alle Ticks, "
        "Vergleiche oder einzelne Perioden. Optional: Tick-Nummer eingeben "
        "oder in der Frage nennen (z. B. «Was passierte bei Tick 15?»)."
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        manual_tick = st.number_input(
            "Tick einschränken (0 = gesamter Lauf)",
            min_value=0,
            max_value=500,
            value=0,
            step=1,
        )
        use_mock = st.checkbox(
            "Demo ohne Ollama (Mock)",
            value=False,
            help="Deaktivieren für echte Antworten via Ollama (Modell in .env).",
        )
        show_context = st.checkbox("Datenkontext anzeigen", value=False)
        show_checks = st.checkbox("Artefakt-Checks anzeigen", value=False)

    messages = st.session_state.explorer_messages.setdefault(run_id, [])

    question = st.chat_input("Frage zur Simulation …")
    focus_tick = _resolve_focus_tick(int(manual_tick), question or "")
    context = load_run_context(run_id, focus_tick=focus_tick)

    if show_checks:
        with st.expander("Konsistenz-Checks (Ground Truth)", expanded=False):
            checks = run_consistency_checks(context.run_dir)
            for check in checks:
                icon = {"ok": "✅", "warn": "⚠️", "fail": "❌"}.get(check.status, "•")
                st.markdown(f"{icon} **{check.title}** — {check.detail}")

    if show_context:
        with st.expander("Daten, die an die Abfrage übergeben werden", expanded=False):
            st.code(build_grounded_context_block(context))

    for role, content in messages:
        with st.chat_message(role):
            st.markdown(content)

    if question:
        messages.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)

        if use_mock:

            class _MockLLM:
                def call(self, prompt: str) -> str:
                    scope = f"Tick {focus_tick}" if focus_tick else "dem gesamten Lauf"
                    return (
                        f"Demo-Antwort: Die Frage bezieht sich auf {scope}. "
                        "Deaktivieren Sie «Demo ohne Ollama», wenn Ollama für echte Antworten laufen soll."
                    )

            explorer = StateExplorer(context, llm=_MockLLM())
        else:
            explorer = StateExplorer(context)

        with st.chat_message("assistant"):
            with st.spinner("Antwort wird erstellt …"):
                try:
                    answer = explorer.ask(question)
                except Exception as exc:
                    answer = f"Abfrage fehlgeschlagen: {exc}"
                st.markdown(answer)
        messages.append(("assistant", answer))


def render_files(run_dir: Path) -> None:
    files = list_run_files(run_dir)
    if not files:
        st.warning("Keine Dateien gefunden.")
        return

    labels = [f"{entry.relative_path} ({entry.size_bytes // 1024} KB)" for entry in files]
    selected_label = st.selectbox("Datei", labels, index=0)
    selected = files[labels.index(selected_label)]
    st.caption(str(selected.absolute_path))

    if selected.kind == "json":
        try:
            payload = json.loads(selected.absolute_path.read_text(encoding="utf-8"))
            st.json(payload)
        except json.JSONDecodeError:
            st.code(read_run_file(selected.absolute_path))
    elif selected.kind == "csv":
        st.code(read_run_file(selected.absolute_path, max_chars=120_000))
    elif selected.kind == "md":
        st.markdown(read_run_file(selected.absolute_path))
    elif selected.kind == "png":
        st.image(str(selected.absolute_path), width="stretch")
    else:
        st.code(read_run_file(selected.absolute_path))


def render_launch_page(*, render_config_editor: Callable[[], object]) -> None:
    st.header("Simulation starten")
    st.caption("Szenario wählen, Parameter anpassen, Lauf starten.")

    draft = render_config_editor()

    col1, col2 = st.columns([1, 3])
    with col1:
        start = st.button("Start", type="primary", width="stretch")
    with col2:
        run_label = f"{draft.run_count} Läufe" if draft.run_count > 1 else "1 Lauf"
        st.caption(f"Szenario: {draft.scenario_mode} · Ticks: {draft.rounds} · {run_label}")

    if start:
        progress_lines: list[str] = []
        terminal_box = st.empty()

        def on_progress(line: str) -> None:
            progress_lines.append(line)
            terminal_box.code("\n".join(progress_lines), language="log")

        with st.status("Lauf aktiv …", expanded=True) as status:
            st.markdown("**Fortschritt**")
            terminal_box.code("Starte …", language="log")
            try:
                result = launch_from_draft(draft, repo_root=REPO_ROOT, on_progress=on_progress)
            except Exception as exc:
                status.update(label="Fehler", state="error")
                st.error(f"Lauf fehlgeschlagen: {exc}")
                return
            status.update(label="Fertig", state="complete")
            if result.sweep_batch:
                st.success("Szenario-Vergleich abgeschlossen.")
                if result.sweep_summary_path:
                    st.caption(f"Summary: `{result.sweep_summary_path}`")
                if result.child_run_ids:
                    st.session_state.last_launched_run_id = result.child_run_ids[0]
                    st.session_state.selected_run_id = result.child_run_ids[0]
                    st.info(
                        "Einzelne Sweep-Runs unter **Ergebnisse ansehen** wählen: "
                        + ", ".join(f"`{rid}`" for rid in result.child_run_ids)
                    )
                else:
                    st.json(result.artifacts)
                return
            if result.multi_run_batch:
                st.session_state.last_launched_run_id = result.run_id
                st.session_state.selected_run_id = result.run_id
                st.success(
                    f"Multi-Run `{result.batch_id}` — {len(result.child_run_ids)} Läufe, "
                    f"je {result.ticks_completed} Ticks, {result.total_events} Events gesamt."
                )
                st.caption(
                    "Einzelne Läufe unter Ergebnisse ansehen: "
                    + ", ".join(f"`{rid}`" for rid in result.child_run_ids)
                )
                return
            st.session_state.last_launched_run_id = result.run_id
            st.session_state.selected_run_id = result.run_id
            st.session_state.explorer_messages.pop(result.run_id, None)
            st.success(
                f"Run `{result.run_id}` — {result.ticks_completed} Ticks, {result.total_events} Events."
            )
            st.caption("Tab «Szenario» in Ergebnisse ansehen — erste Lesart nach dem Lauf.")
            if draft.generate_figures:
                st.caption("Figures liegen unter `figures/` — Tab «Figures» in Ergebnisse ansehen.")


def render_run_browser(
    *,
    render_animation: Callable[[Path], None],
    render_figures: Callable[[Path], None],
) -> None:
    runs = list_runs()
    if not runs:
        st.info("Noch keine Runs vorhanden. Starten Sie oben eine Simulation.")
        return

    run_ids = [run.run_id for run in runs]
    run_labels = []
    for run in runs:
        label = run.run_id
        if run.scenario_title:
            label = f"{run.run_id} — {run.scenario_title}"
        run_labels.append(label)

    default_index = 0
    if st.session_state.selected_run_id in run_ids:
        default_index = run_ids.index(st.session_state.selected_run_id)
    elif st.session_state.last_launched_run_id in run_ids:
        default_index = run_ids.index(st.session_state.last_launched_run_id)

    selected_label = st.selectbox("Run", run_labels, index=default_index)
    selected_run_id = run_ids[run_labels.index(selected_label)]
    st.session_state.selected_run_id = selected_run_id
    summary = next(run for run in runs if run.run_id == selected_run_id)
    run_dir = summary.run_dir

    preview = summary.scenario_summary or "Kein Szenario-Preview — Run ohne `run_scenario.json`."
    st.caption(
        f"{summary.timestamp or '—'} · "
        f"{summary.ticks_completed or '?'} Ticks · "
        f"Modell {summary.model or '—'}"
    )
    st.info(preview)

    tabs = st.tabs(
        ["Szenario", "Übersicht", "Animation", "Figures", "Bericht", "Abfrage", "Dateien"]
    )
    with tabs[0]:
        render_scenario(run_dir, selected_run_id)
    with tabs[1]:
        render_overview(run_dir, selected_run_id)
    with tabs[2]:
        render_animation(run_dir)
    with tabs[3]:
        render_figures(run_dir)
    with tabs[4]:
        render_narrative(run_dir)
    with tabs[5]:
        render_explorer(selected_run_id)
    with tabs[6]:
        render_files(run_dir)


def run_dashboard(
    *,
    render_animation: Callable[[Path], None],
    render_figures: Callable[[Path], None],
    render_config_editor: Callable[[], object],
) -> None:
    """Shared page setup + navigation for both dashboard entry points."""

    st.set_page_config(
        page_title="Technology Lab · Simulation",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS Hack: Hide "Ask ChatGPT" and "Ask Google" buttons from exception tracebacks
    st.markdown(
        """
        <style>
        [data-testid="stException"] a[href*="platform.openai.com/playground"],
        [data-testid="stException"] a[href*="google.com/search"],
        [data-testid="stException"] a[href*="chat.openai.com"],
        [data-testid="stException"] a[href*="chatgpt.com"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()

    st.title("Technology Lab · Simulation")
    st.caption("Prototypische Workbench für Szenarioplanung im Flugverkehr")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Bereich",
            ["Simulation starten", "Ergebnisse ansehen"],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption(f"Outputs: `{outputs_root()}`")
        if st.session_state.last_launched_run_id:
            st.caption(f"Zuletzt: `{st.session_state.last_launched_run_id}`")

    if page == "Simulation starten":
        render_launch_page(render_config_editor=render_config_editor)
    else:
        render_run_browser(render_animation=render_animation, render_figures=render_figures)
