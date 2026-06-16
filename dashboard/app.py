"""Streamlit-Oberfläche: Simulation starten, Ergebnisse ansehen, Run abfragen."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import matplotlib.pyplot as plt
import streamlit as st

from dashboard.config_ui import render_config_editor
from dashboard.service import (
    REPO_ROOT,
    generate_figures_for_run,
    launch_from_draft,
    list_run_files,
    list_run_figures,
    list_runs,
    load_event_log,
    load_price_series,
    load_tick_mechanics,
    outputs_root,
    read_run_file,
)
from src.state_explorer import (
    StateExplorer,
    build_grounded_context_block,
    load_run_context,
    parse_tick_hint,
)


def _init_session_state() -> None:
    defaults = {
        "selected_run_id": None,
        "explorer_messages": {},
        "last_launched_run_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_overview(run_dir: Path, run_id: str) -> None:
    metadata_path = run_dir / "run_metadata.json"
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        cols = st.columns(4)
        cols[0].metric("Ticks", f"{metadata.get('ticks_completed', '?')} / {metadata.get('ticks_max', '?')}")
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
        booking = [float(row["booking_rate"]) for row in ticks if row.get("booking_rate") is not None]
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


def _render_narrative(run_dir: Path) -> None:
    narrative_path = run_dir / "final_narrative.md"
    if not narrative_path.is_file():
        st.warning("`final_narrative.md` fehlt in diesem Run.")
        return
    st.markdown(read_run_file(narrative_path))


def _resolve_focus_tick(manual_tick: int, question: str) -> int | None:
    if manual_tick > 0:
        return manual_tick
    return parse_tick_hint(question)


def _render_explorer(run_id: str) -> None:
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
        use_mock = st.checkbox("Demo ohne Ollama (Mock)", value=True)
        show_context = st.checkbox("Datenkontext anzeigen", value=False)

    messages = st.session_state.explorer_messages.setdefault(run_id, [])

    question = st.chat_input("Frage zur Simulation …")
    focus_tick = _resolve_focus_tick(int(manual_tick), question or "")
    context = load_run_context(run_id, focus_tick=focus_tick)

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


def _render_animation(run_dir: Path) -> None:
    history_file = run_dir / "individuals_history.csv"
    if not history_file.is_file():
        st.info(
            "Keine History-Datei `individuals_history.csv` gefunden. "
            "Starten Sie eine neue Simulation, um die Agenten-History aufzuzeichnen."
        )
        return
        
    import pandas as pd
    import plotly.express as px
    
    st.markdown("### Animierter Population-Scatter-Plot")
    st.caption("Verfolgen Sie die Agenten über die Ticks hinweg.")
    
    try:
        df = pd.read_csv(history_file)
        if df.empty:
            st.warning("History-Datei ist leer.")
            return
            
        # Load price history to calculate consumer surplus
        price_file = run_dir / "price_history.json"
        if price_file.is_file():
            import json
            with open(price_file, "r") as f:
                price_data = json.load(f)
            price_map = {item["round_number"]: item["price"] for item in price_data}
            df["ticket_price"] = df["tick"].map(price_map)
            df["surplus"] = df["wtp_eur"] - df["ticket_price"].fillna(df["wtp_eur"]) # fallback to 0 surplus if price missing
        else:
            df["ticket_price"] = 0
            df["surplus"] = df["wtp_eur"]
            
        # Determine visual labels: Color by booked (yes/no), symbol by business/leisure
        df["Segment"] = df.apply(lambda row: "Business" if str(row.get("business", False)).lower() == "true" else "Leisure", axis=1)
        df["Gebucht"] = df["booked"].astype(str)
        
        # We cap awareness and wtp if there are outliers, but let plotly scale automatically
        fig = px.scatter(
            df,
            x="wtp_eur",
            y="environmental_awareness",
            animation_frame="tick",
            animation_group="id",
            color="Gebucht",
            symbol="Segment",
            hover_name="id",
            hover_data=["age", "substitution_readiness", "price_sensitivity"],
            title="Population über Zeit",
            labels={
                "wtp_eur": "Zahlungsbereitschaft (WTP) in €",
                "environmental_awareness": "Umweltbewusstsein (Awareness)",
                "tick": "Tick",
            },
            color_discrete_map={"True": "green", "False": "red"},
            range_x=[df["wtp_eur"].quantile(0.01) * 0.9, df["wtp_eur"].quantile(0.99) * 1.1],
            range_y=[-0.1, 1.1]
        )
        fig.update_traces(marker=dict(size=4, opacity=0.4, line=dict(width=0)))
        
        # Make animation truly smooth
        if fig.layout.updatemenus:
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
            fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
            fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False
            
        st.plotly_chart(fig, width="stretch")
        
        st.divider()
        st.markdown("### Aggregation nach Altersgruppen")
        st.caption("Verfolgen Sie die Buchungsraten und -mengen pro Altersgruppe über die Ticks hinweg.")
        
        # Create Age Groups
        df["Altersgruppe"] = pd.cut(
            df["age"], 
            bins=[0, 18, 26, 36, 51, 66, 120], 
            labels=["<18", "18-25", "26-35", "36-50", "51-65", ">65"],
            right=False
        )
        
        # Aggregate by tick and age_group
        df_booked_bool = df.copy()
        df_booked_bool["booked_num"] = df_booked_bool["booked"].astype(bool).astype(int)
        
        agg_df = df_booked_bool.groupby(["tick", "Altersgruppe"], observed=False).agg(
            total_agenten=("id", "count"),
            gebucht=("booked_num", "sum"),
            avg_wtp=("wtp_eur", "mean"),
            ticket_price=("ticket_price", "mean"),
            avg_awareness=("environmental_awareness", "mean")
        ).reset_index()
        
        agg_df["Buchungsrate"] = agg_df["gebucht"] / agg_df["total_agenten"].replace(0, pd.NA)
        agg_df["Buchungsrate"] = agg_df["Buchungsrate"].fillna(0)
        
        # Filter out empty age groups
        agg_df = agg_df[agg_df["total_agenten"] > 0]
        
        fig2 = px.scatter(
            agg_df,
            x="Buchungsrate",
            y="avg_wtp",
            size="gebucht",
            color="Altersgruppe",
            animation_frame="tick",
            animation_group="Altersgruppe",
            hover_name="Altersgruppe",
            hover_data={
                "gebucht": True,
                "total_agenten": True,
                "avg_wtp": ":.2f",
                "ticket_price": ":.2f"
            },
            title="Buchungsverhalten nach Altersgruppen",
            labels={
                "Buchungsrate": "Buchungsrate (0-1)",
                "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
                "gebucht": "Anzahl Buchungen"
            },
            size_max=50,
            range_x=[-0.1, 1.1],
            range_y=[agg_df["avg_wtp"].min() * 0.8, agg_df["avg_wtp"].max() * 1.2]
        )
        
        # Make animation truly smooth
        if fig2.layout.updatemenus:
            fig2.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
            fig2.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
            fig2.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
            fig2.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False
            
        st.plotly_chart(fig2, width="stretch")
        
        st.divider()
        st.markdown("### Aggregation nach Segmenten")
        st.caption("Verfolgen Sie die Buchungsraten und -mengen pro Segment über die Ticks hinweg.")
        
        # Extract dynamic segment columns
        base_cols = {"id", "tick", "age", "wtp_eur", "environmental_awareness", "price_sensitivity", "substitution_readiness", "booked", "Segment", "Gebucht", "Altersgruppe", "booked_num"}
        segment_cols = [c for c in df.columns if c not in base_cols]
        
        if segment_cols:
            segment_records = []
            for t in sorted(df["tick"].unique()):
                df_t = df_booked_bool[df_booked_bool["tick"] == t]
                for seg in segment_cols:
                    # check if string "True" or bool True
                    in_segment = df_t[df_t[seg].astype(str).str.lower() == "true"]
                    total_agenten = len(in_segment)
                    if total_agenten > 0:
                        gebucht = in_segment["booked_num"].sum()
                        avg_wtp = in_segment["wtp_eur"].mean()
                        ticket_price = in_segment["ticket_price"].mean()
                        avg_awareness = in_segment["environmental_awareness"].mean()
                        segment_records.append({
                            "tick": t,
                            "Segment": seg.replace("_", " ").title(),
                            "total_agenten": total_agenten,
                            "gebucht": gebucht,
                            "Buchungsrate": gebucht / total_agenten,
                            "ticket_price": ticket_price,
                            "avg_wtp": avg_wtp,
                            "avg_awareness": avg_awareness
                        })
            
            if segment_records:
                seg_df = pd.DataFrame(segment_records)
                fig3 = px.scatter(
                    seg_df,
                    x="Buchungsrate",
                    y="avg_wtp",
                    size="gebucht",
                    color="Segment",
                    animation_frame="tick",
                    animation_group="Segment",
                    hover_name="Segment",
                    hover_data={
                        "gebucht": True,
                        "total_agenten": True,
                        "avg_wtp": ":.2f",
                        "ticket_price": ":.2f"
                    },
                    title="Buchungsverhalten nach Segmenten",
                    labels={
                        "Buchungsrate": "Buchungsrate (0-1)",
                        "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
                        "gebucht": "Anzahl Buchungen"
                    },
                    size_max=50,
                    range_x=[-0.1, 1.1],
                    range_y=[seg_df["avg_wtp"].min() * 0.8, seg_df["avg_wtp"].max() * 1.2]
                )
                
                if fig3.layout.updatemenus:
                    fig3.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
                    fig3.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
                    fig3.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
                    fig3.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False
                    
                st.plotly_chart(fig3, width="stretch")
                
                st.divider()
                st.markdown("### Segment-Effizienz (Buchungsanteil vs. Populationsanteil)")
                st.caption("Liegt eine Bubble oberhalb der diagonalen Linie, bucht dieses Segment überdurchschnittlich oft in Relation zu seiner Größe (z.B. wenig Vielflieger, aber viele Buchungen).")
                
                # Map total agents and total bookings
                total_agents_dict = df_booked_bool.groupby("tick")["id"].count().to_dict()
                total_booked_dict = df_booked_bool.groupby("tick")["booked_num"].sum().to_dict()
                
                seg_df["pop_share"] = seg_df.apply(lambda row: row["total_agenten"] / total_agents_dict.get(row["tick"], 1), axis=1)
                seg_df["booking_share"] = seg_df.apply(lambda row: row["gebucht"] / max(total_booked_dict.get(row["tick"], 1), 1), axis=1)
                
                fig4 = px.scatter(
                    seg_df,
                    x="pop_share",
                    y="booking_share",
                    size="gebucht",
                    color="Segment",
                    animation_frame="tick",
                    animation_group="Segment",
                    hover_name="Segment",
                    hover_data={
                        "gebucht": True,
                        "total_agenten": True,
                        "pop_share": ":.1%",
                        "booking_share": ":.1%"
                    },
                    title="Marktanteil vs. Populationsanteil",
                    labels={
                        "pop_share": "Anteil an Gesamtpopulation (0-1)",
                        "booking_share": "Anteil an Gesamtbuchungen (0-1)",
                        "gebucht": "Anzahl Buchungen"
                    },
                    size_max=50,
                    range_x=[-0.05, 1.05],
                    range_y=[-0.05, 1.05]
                )
                
                # Add diagonal line y=x
                fig4.add_shape(
                    type="line", line=dict(dash="dash", color="gray"),
                    x0=0, y0=0, x1=1, y1=1
                )
                
                if fig4.layout.updatemenus:
                    fig4.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
                    fig4.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
                    fig4.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
                    fig4.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False
                    
                st.plotly_chart(fig4, width="stretch")
                
            else:
                st.info("Keine Daten für die definierten Segmente gefunden.")
        else:
            st.info("Keine Segmente (Labels) in der Population definiert.")
        
    except Exception as exc:
        st.error(f"Fehler beim Rendern der Animation: {exc}")


def _render_figures(run_dir: Path) -> None:
    figures = list_run_figures(run_dir)
    col1, col2 = st.columns([1, 3])
    with col1:
        regenerate = st.button("Figures neu erzeugen", width="stretch")
    with col2:
        st.caption(f"Speicherort: `{run_dir / 'figures'}`")

    if regenerate:
        with st.spinner("Figures werden erzeugt …"):
            try:
                figures = generate_figures_for_run(run_dir)
                st.success(f"{len(figures)} Figures erzeugt.")
            except Exception as exc:
                st.error(f"Figure-Erzeugung fehlgeschlagen: {exc}")
                return

    if not figures:
        st.info(
            "Noch keine Figures für diesen Run. "
            "Aktivieren Sie «Figures nach Lauf erzeugen» beim Start oder klicken Sie oben auf «Figures neu erzeugen»."
        )
        return

    for index, figure in enumerate(figures):
        st.markdown(f"**{figure.title}**")
        st.image(str(figure.absolute_path), width="stretch")
        if index < len(figures) - 1:
            st.divider()


def _render_files(run_dir: Path) -> None:
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


def _render_launch_page() -> None:
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
                st.json(result.artifacts)
                return
            if result.multi_run_batch:
                st.session_state.last_launched_run_id = result.run_id
                st.session_state.selected_run_id = result.run_id
                st.success(
                    f"Multi-Run `{result.batch_id}` — {len(result.child_run_ids)} Läufe, "
                    f"je {result.ticks_completed} Ticks, {result.total_events} Events gesamt."
                )
                st.caption("Einzelne Läufe unter Ergebnisse ansehen: " + ", ".join(f"`{rid}`" for rid in result.child_run_ids))
                return
            st.session_state.last_launched_run_id = result.run_id
            st.session_state.selected_run_id = result.run_id
            st.session_state.explorer_messages.pop(result.run_id, None)
            st.success(
                f"Run `{result.run_id}` — {result.ticks_completed} Ticks, {result.total_events} Events."
            )
            if draft.generate_figures:
                st.caption("Figures liegen unter `figures/` — Tab «Figures» in Ergebnisse ansehen.")


def _render_run_browser() -> None:
    runs = list_runs()
    if not runs:
        st.info("Noch keine Runs vorhanden. Starten Sie oben eine Simulation.")
        return

    run_ids = [run.run_id for run in runs]
    default_index = 0
    if st.session_state.selected_run_id in run_ids:
        default_index = run_ids.index(st.session_state.selected_run_id)
    elif st.session_state.last_launched_run_id in run_ids:
        default_index = run_ids.index(st.session_state.last_launched_run_id)

    selected_run_id = st.selectbox("Run", run_ids, index=default_index)
    st.session_state.selected_run_id = selected_run_id
    summary = next(run for run in runs if run.run_id == selected_run_id)
    run_dir = summary.run_dir

    st.caption(
        f"{summary.timestamp or '—'} · "
        f"{summary.ticks_completed or '?'} Ticks · "
        f"Modell {summary.model or '—'}"
    )

    tabs = st.tabs(["Übersicht", "Animation", "Figures", "Bericht", "Abfrage", "Dateien"])
    with tabs[0]:
        _render_overview(run_dir, selected_run_id)
    with tabs[1]:
        _render_animation(run_dir)
    with tabs[2]:
        _render_figures(run_dir)
    with tabs[3]:
        _render_narrative(run_dir)
    with tabs[4]:
        _render_explorer(selected_run_id)
    with tabs[5]:
        _render_files(run_dir)


def main() -> None:
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
        unsafe_allow_html=True
    )
    
    _init_session_state()

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
        _render_launch_page()
    else:
        _render_run_browser()


if __name__ == "__main__":
    main()
