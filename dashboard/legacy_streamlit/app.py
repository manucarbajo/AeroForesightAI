"""Streamlit-Oberfläche (Ops-Variante): Simulation starten, Ergebnisse ansehen, Run abfragen."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from dashboard.legacy_streamlit.config_ui import render_config_editor
from dashboard.legacy_streamlit.shared_views import run_dashboard
from dashboard.run_browser import generate_figures_for_run, list_run_figures


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
            df["surplus"] = df["wtp_eur"] - df["ticket_price"].fillna(
                df["wtp_eur"]
            )  # fallback to 0 surplus if price missing
        else:
            df["ticket_price"] = 0
            df["surplus"] = df["wtp_eur"]

        # Determine visual labels: Color by booked (yes/no), symbol by business/leisure
        df["Segment"] = df.apply(
            lambda row: (
                "Business" if str(row.get("business", False)).lower() == "true" else "Leisure"
            ),
            axis=1,
        )
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
            range_y=[-0.1, 1.1],
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
        st.caption(
            "Verfolgen Sie die Buchungsraten und -mengen pro Altersgruppe über die Ticks hinweg."
        )

        # Create Age Groups
        df["Altersgruppe"] = pd.cut(
            df["age"],
            bins=[0, 18, 26, 36, 51, 66, 120],
            labels=["<18", "18-25", "26-35", "36-50", "51-65", ">65"],
            right=False,
        )

        # Aggregate by tick and age_group
        df_booked_bool = df.copy()
        df_booked_bool["booked_num"] = df_booked_bool["booked"].astype(bool).astype(int)

        agg_df = (
            df_booked_bool.groupby(["tick", "Altersgruppe"], observed=False)
            .agg(
                total_agenten=("id", "count"),
                gebucht=("booked_num", "sum"),
                avg_wtp=("wtp_eur", "mean"),
                ticket_price=("ticket_price", "mean"),
                avg_awareness=("environmental_awareness", "mean"),
            )
            .reset_index()
        )

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
                "ticket_price": ":.2f",
            },
            title="Buchungsverhalten nach Altersgruppen",
            labels={
                "Buchungsrate": "Buchungsrate (0-1)",
                "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
                "gebucht": "Anzahl Buchungen",
            },
            size_max=50,
            range_x=[-0.1, 1.1],
            range_y=[agg_df["avg_wtp"].min() * 0.8, agg_df["avg_wtp"].max() * 1.2],
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
        base_cols = {
            "id",
            "tick",
            "age",
            "wtp_eur",
            "environmental_awareness",
            "price_sensitivity",
            "substitution_readiness",
            "booked",
            "Segment",
            "Gebucht",
            "Altersgruppe",
            "booked_num",
        }
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
                        segment_records.append(
                            {
                                "tick": t,
                                "Segment": seg.replace("_", " ").title(),
                                "total_agenten": total_agenten,
                                "gebucht": gebucht,
                                "Buchungsrate": gebucht / total_agenten,
                                "ticket_price": ticket_price,
                                "avg_wtp": avg_wtp,
                                "avg_awareness": avg_awareness,
                            }
                        )

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
                        "ticket_price": ":.2f",
                    },
                    title="Buchungsverhalten nach Segmenten",
                    labels={
                        "Buchungsrate": "Buchungsrate (0-1)",
                        "avg_wtp": "Ø Zahlungsbereitschaft (WTP) in €",
                        "gebucht": "Anzahl Buchungen",
                    },
                    size_max=50,
                    range_x=[-0.1, 1.1],
                    range_y=[seg_df["avg_wtp"].min() * 0.8, seg_df["avg_wtp"].max() * 1.2],
                )

                if fig3.layout.updatemenus:
                    fig3.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
                    fig3.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 500
                    fig3.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
                    fig3.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False

                st.plotly_chart(fig3, width="stretch")

                st.divider()
                st.markdown("### Segment-Effizienz (Buchungsanteil vs. Populationsanteil)")
                st.caption(
                    "Liegt eine Bubble oberhalb der diagonalen Linie, bucht dieses Segment überdurchschnittlich oft in Relation zu seiner Größe (z.B. wenig Vielflieger, aber viele Buchungen)."
                )

                # Map total agents and total bookings
                total_agents_dict = df_booked_bool.groupby("tick")["id"].count().to_dict()
                total_booked_dict = df_booked_bool.groupby("tick")["booked_num"].sum().to_dict()

                seg_df["pop_share"] = seg_df.apply(
                    lambda row: row["total_agenten"] / total_agents_dict.get(row["tick"], 1), axis=1
                )
                seg_df["booking_share"] = seg_df.apply(
                    lambda row: row["gebucht"] / max(total_booked_dict.get(row["tick"], 1), 1),
                    axis=1,
                )

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
                        "booking_share": ":.1%",
                    },
                    title="Marktanteil vs. Populationsanteil",
                    labels={
                        "pop_share": "Anteil an Gesamtpopulation (0-1)",
                        "booking_share": "Anteil an Gesamtbuchungen (0-1)",
                        "gebucht": "Anzahl Buchungen",
                    },
                    size_max=50,
                    range_x=[-0.05, 1.05],
                    range_y=[-0.05, 1.05],
                )

                # Add diagonal line y=x
                fig4.add_shape(
                    type="line", line=dict(dash="dash", color="gray"), x0=0, y0=0, x1=1, y1=1
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


def main() -> None:
    run_dashboard(
        render_animation=_render_animation,
        render_figures=_render_figures,
        render_config_editor=render_config_editor,
    )


if __name__ == "__main__":
    main()
