"""Streamlit-Oberfläche (Researcher-Variante): Deep-Dive-Animationen und wissenschaftliche Auswertungen."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from dashboard.config_ui_researcher import render_config_editor
from dashboard.shared_views import run_dashboard


def _render_animation(run_dir: Path) -> None:
    history_file = run_dir / "individuals_history.csv"
    if not history_file.is_file():
        st.info("Keine History-Datei `individuals_history.csv` gefunden.")
        return

    import numpy as np
    import pandas as pd
    import plotly.express as px

    st.markdown("### Deep Dive Animationen (Mikro-Verhalten)")

    anim_type = st.selectbox(
        "Wähle eine Animations-Perspektive:",
        [
            "1. Der Surplus Pulse (Ökonomie & Preiselastizität)",
            "2. Saturation Swarm (Sättigung & Hunger)",
            "3. Behavioral Split (Psychologische Sensibilität)",
            "4. Demographie & Umwelt (Segmente)",
            "5. Einkommen vs WTP (Kaufkraft)",
        ],
    )

    try:
        df = pd.read_csv(history_file)
        if df.empty:
            st.warning("History-Datei ist leer.")
            return

        # Downsampling für bessere Übersichtlichkeit
        unique_ids = df["id"].unique()
        max_agents = len(unique_ids)
        if max_agents > 150:
            sample_size = st.slider(
                "Anzahl angezeigter Agenten (für mehr Übersicht):",
                min_value=10,
                max_value=max_agents,
                value=150,
                step=10,
            )
            # Konstanten Seed verwenden, damit die gleichen Agenten pro Frame gerendert werden
            np.random.seed(42)
            sampled_ids = np.random.choice(unique_ids, sample_size, replace=False)
            df = df[df["id"].isin(sampled_ids)].copy()

        # 1. Datenaufbereitung
        # Dynamische Ermittlung der Segmente (alle Spalten, die nicht zu den Basis-Metriken gehören)
        base_cols = {
            "tick",
            "id",
            "age",
            "wtp_eur",
            "environmental_awareness",
            "substitution_readiness",
            "price_sensitivity",
            "income_factor",
            "saturation_level",
            "booked",
            "last_booked_tick",
            "flight_hunger",
            "Segment",
            "Gebucht",
            "ColorGroup",
        }
        segment_labels = [c for c in df.columns if c not in base_cols]

        for col in segment_labels:
            df.loc[df[col].astype(str).str.lower() == "true", "Segment"] = col.replace(
                "_", " "
            ).title()

        # Fallback fuer Leute, die keins der obigen Labels haben (z.B. pures Leisure)
        df.loc[df["Segment"] == "Unbekannt", "Segment"] = "Standard Leisure"

        df["last_booked_tick"] = pd.to_numeric(df["last_booked_tick"], errors="coerce").fillna(0)
        df["flight_hunger"] = df["tick"] - df["last_booked_tick"]
        df["Gebucht"] = df["booked"].astype(str)

        # Segment-Farben dynamisch zuweisen
        df["ColorGroup"] = (
            df["Segment"]
            + " ("
            + df["booked"].astype(bool).map({True: "Gebucht", False: "Nicht Gebucht"})
            + ")"
        )

        palette_pairs = [
            ("#1d4ed8", "#93c5fd"),  # Blue
            ("#c2410c", "#fdba74"),  # Orange
            ("#15803d", "#86efac"),  # Green
            ("#b91c1c", "#fca5a5"),  # Red
            ("#0f766e", "#5eead4"),  # Teal
            ("#b45309", "#fcd34d"),  # Yellow
            ("#be185d", "#f9a8d4"),  # Pink
            ("#4d7c0f", "#bef264"),  # Lime
        ]

        segment_colors = {}
        unique_segments = sorted(df["Segment"].dropna().unique())
        for i, seg in enumerate(unique_segments):
            if seg == "Standard Leisure":
                dark, light = ("#7e22ce", "#d8b4fe")  # Lila für Standard Leisure
            else:
                dark, light = palette_pairs[i % len(palette_pairs)]

            segment_colors[f"{seg} (Gebucht)"] = dark
            segment_colors[f"{seg} (Nicht Gebucht)"] = light

        df["income_factor"] = pd.to_numeric(df["income_factor"], errors="coerce").fillna(1.0)
        df["effective_wtp"] = df["wtp_eur"] * df["income_factor"]

        # Ticketpreis auslesen, um Konsumentenrente (Surplus) zu berechnen
        price_file = run_dir / "price_history.json"
        if price_file.is_file():
            import json

            with open(price_file, "r") as f:
                price_data = json.load(f)
            price_map = {item["round_number"]: item["price"] for item in price_data}
            df["ticket_price"] = df["tick"].map(price_map)
            df["surplus"] = df["effective_wtp"] - df["ticket_price"].fillna(df["effective_wtp"])
        else:
            df["surplus"] = df["effective_wtp"]

        # Konsistenter Jitter pro Agent (damit statische Werte nicht pro Frame springen)
        jitter_strength = 0.05
        np.random.seed(42)
        unique_ids_for_jitter = df["id"].unique()

        surplus_std = df["surplus"].std()
        if pd.isna(surplus_std) or surplus_std == 0:
            surplus_std = 10.0
        eff_wtp_std = df["effective_wtp"].std()
        if pd.isna(eff_wtp_std) or eff_wtp_std == 0:
            eff_wtp_std = 10.0
        wtp_std = df["wtp_eur"].std()
        if pd.isna(wtp_std) or wtp_std == 0:
            wtp_std = 10.0

        offsets = pd.DataFrame(
            {
                "id": unique_ids_for_jitter,
                "offset_wtp": np.random.normal(
                    0, wtp_std * jitter_strength, size=len(unique_ids_for_jitter)
                ),
                "offset_eff_wtp": np.random.normal(
                    0, eff_wtp_std * jitter_strength, size=len(unique_ids_for_jitter)
                ),
                "offset_age": np.random.normal(0, 1.5, size=len(unique_ids_for_jitter)),
                "offset_env": np.random.normal(0, 0.05, size=len(unique_ids_for_jitter)),
                "offset_price_sens": np.random.normal(0, 0.05, size=len(unique_ids_for_jitter)),
                "offset_subst": np.random.normal(0, 0.05, size=len(unique_ids_for_jitter)),
                "offset_inc": np.random.normal(0, 0.02, size=len(unique_ids_for_jitter)),
                "offset_surplus_y": np.random.normal(
                    0, surplus_std * jitter_strength, size=len(unique_ids_for_jitter)
                ),
                "offset_hunger_y": np.random.normal(0, 0.02, size=len(unique_ids_for_jitter)),
            }
        )
        df = df.merge(offsets, on="id", how="left")

        fig = None

        if anim_type.startswith("1"):
            st.info(
                "**Lesehilfe: Der Surplus Pulse**\n\n"
                "Dieses Diagramm zeigt die **Preiselastizität in Echtzeit**. \n"
                "- **X-Achse (Effektive WTP):** Die absolute Kaufkraft des Agenten (Grundzahlungsbereitschaft mal aktueller Einkommensindex).\n"
                "- **Y-Achse (Konsumentenrente / Surplus):** Der individuelle finanzielle Spielraum (Effektive WTP minus aktueller Ticketpreis).\n"
                "- **Interpretation:** Sobald die Airline den Ticketpreis erhöht, rutscht die gesamte Agenten-Wolke nach unten. "
                "Agenten, die unter die gestrichelte rote Linie fallen (Y < 0), können sich das Ticket nicht mehr leisten und werden aus dem Markt gedrängt (grau). "
                "Du siehst hier live, wie Yield-Management funktioniert."
            )
            # Jitter auf X für WTP und Y für Surplus
            df["eff_wtp_jittered"] = df["effective_wtp"] + df["offset_eff_wtp"]
            df["surplus_jittered"] = df["surplus"] + df["offset_surplus_y"]

            fig = px.scatter(
                df,
                x="eff_wtp_jittered",
                y="surplus_jittered",
                animation_frame="tick",
                animation_group="id",
                color="ColorGroup",
                symbol="Segment",
                size="income_factor",
                hover_name="id",
                range_x=[0, df["effective_wtp"].max() * 1.1],
                range_y=[df["surplus"].min() - 50, df["surplus"].max() + 50],
                title="Der Surplus Pulse (Wirtschaftliche Dynamik)",
                labels={
                    "eff_wtp_jittered": "Effektive WTP (EUR)",
                    "surplus_jittered": "Konsumentenrente (Surplus)",
                },
                color_discrete_map=segment_colors,
            )
            # Nulllinie für Surplus
            fig.add_hline(
                y=0, line_dash="dash", line_color="red", annotation_text="Kauf-Grenze (Surplus = 0)"
            )

        elif anim_type.startswith("2"):
            st.info(
                "**Lesehilfe: Saturation Swarm**\n\n"
                "Dieses Diagramm macht die unsichtbare **Sättigungs-Mechanik** der Simulation sichtbar.\n"
                "- **X-Achse (Absolute WTP):** Basis-Zahlungsbereitschaft des Agenten.\n"
                "- **Y-Achse (Flug-Hunger / Need):** Berechnet aus `1.0 - Saturation`. Zeigt den mathematisch exakten Drang zu fliegen.\n"
                "- **Interpretation:** Du siehst, wie Agenten mit jedem Tick langsam nach oben steigen (der 'Bedarf' wächst, die Sättigung klingt ab). "
                "Sobald ein Agent bucht (grün wird), baut sich seine Sättigung sofort auf 1.0 auf und der Punkt 'stürzt' auf die Nulllinie (Y=0) hinab. "
                "Verschiedene Segmente steigen unterschiedlich schnell wieder auf (unterschiedliche Decay-Rates)!"
            )
            df["wtp_jittered"] = df["wtp_eur"] + df["offset_wtp"]

            # Reale Sättigung nutzen, falls vorhanden (neue CSVs), sonst Fallback
            if "saturation_level" in df.columns:
                df["exact_hunger"] = 1.0 - pd.to_numeric(
                    df["saturation_level"], errors="coerce"
                ).fillna(0.0)
                df["hunger_jittered"] = df["exact_hunger"] + df["offset_hunger_y"]
                y_range = [-0.1, 1.2]
            else:
                df["hunger_jittered"] = df["flight_hunger"] + (df["offset_hunger_y"] * 25)
                y_range = [-1, df["flight_hunger"].max() + 2]

            fig = px.scatter(
                df,
                x="wtp_jittered",
                y="hunger_jittered",
                animation_frame="tick",
                animation_group="id",
                color="ColorGroup",
                symbol="Segment",
                size="income_factor",
                hover_name="id",
                range_x=[0, df["wtp_eur"].max() * 1.1],
                range_y=y_range,
                title="Saturation Swarm (Organische Sättigungsdynamik)",
                labels={
                    "wtp_jittered": "Absolute WTP (EUR)",
                    "hunger_jittered": "Flug-Hunger (1.0 - Saturation)",
                },
                color_discrete_map=segment_colors,
            )

        elif anim_type.startswith("3"):
            st.info(
                "**Lesehilfe: Behavioral Split**\n\n"
                "Hier untersuchen wir die **psychologische Widerstandsfähigkeit** der Agenten gegenüber äußeren Schocks.\n"
                "- **X-Achse:** Preissensibilität (Wie stark reagiert der Agent auf teure Tickets?).\n"
                "- **Y-Achse:** Substitutionsbereitschaft (Wie leicht fällt dem Agenten der Umstieg auf Bahn/Auto?).\n"
                "- **Interpretation:** Oben rechts befinden sich die 'kritischsten' Agenten (sehr preissensibel und bereit umzusteigen). "
                "Wenn z.B. eine hohe CO2-Steuer eingeführt wird, wirst du beobachten, wie eine 'Welle' der Nicht-Buchungen (graue Punkte) "
                "von rechts oben nach links unten wandert."
            )
            df["price_sens_jittered"] = df["price_sensitivity"] + df["offset_price_sens"]
            df["subst_jittered"] = df["substitution_readiness"] + df["offset_subst"]
            fig = px.scatter(
                df,
                x="price_sens_jittered",
                y="subst_jittered",
                animation_frame="tick",
                animation_group="id",
                color="ColorGroup",
                symbol="Segment",
                hover_name="id",
                range_x=[-0.1, 1.1],
                range_y=[-0.1, 1.1],
                title="Behavioral Split (Psychologische Demographie)",
                labels={
                    "price_sens_jittered": "Preissensibilität",
                    "subst_jittered": "Substitutionsbereitschaft",
                },
                color_discrete_map=segment_colors,
            )

        elif anim_type.startswith("4"):
            st.info(
                "**Lesehilfe: Demographischer Cluster**\n\n"
                "- **X-Achse:** Alter des Agenten.\n"
                "- **Y-Achse:** Umweltbewusstsein.\n"
                "- **Interpretation:** Ein reiner Demographie-Scan. Gibt es Alters- oder Umweltcluster, die signifikant häufiger buchen? "
                "Besonders nützlich, wenn in der CIB-Matrix (Faktor F1) das Umweltbewusstsein schockartig in der Gesellschaft ansteigt."
            )
            df["age_jittered"] = df["age"] + df["offset_age"]
            df["env_jittered"] = df["environmental_awareness"] + df["offset_env"]
            fig = px.scatter(
                df,
                x="age_jittered",
                y="env_jittered",
                animation_frame="tick",
                animation_group="id",
                color="ColorGroup",
                symbol="Segment",
                size="income_factor",
                hover_name="id",
                range_x=[15, 90],
                range_y=[-0.1, 1.1],
                title="Demographischer Cluster (Alter vs. Umwelt)",
                labels={"age_jittered": "Alter", "env_jittered": "Umweltbewusstsein"},
                color_discrete_map=segment_colors,
            )

        elif anim_type.startswith("5"):
            st.info(
                "**Lesehilfe: Income vs WTP**\n\n"
                "- **X-Achse (Einkommensindex):** Der Makroökonomische Multiplikator.\n"
                "- **Y-Achse (Basis WTP):** Die intrinsische Zahlungsbereitschaft in EUR.\n"
                "- **Interpretation:** Veranschaulicht Makro-Dynamiken. Wenn sich der Einkommensindex verändert (z.B. wegen eines Kondratieff-Zyklus), "
                "verschiebt sich die Wolke auf der X-Achse. Du siehst live, wie Wohlstand (Punkte wandern nach rechts) die Gesamt-Buchungsrate (Grün-Anteil) stärkt."
            )
            df["wtp_jittered"] = df["wtp_eur"] + df["offset_wtp"]
            df["inc_jittered"] = df["income_factor"] + df["offset_inc"]
            fig = px.scatter(
                df,
                x="inc_jittered",
                y="wtp_jittered",
                animation_frame="tick",
                animation_group="id",
                color="ColorGroup",
                symbol="Segment",
                hover_name="id",
                range_x=[df["income_factor"].min() - 0.2, df["income_factor"].max() + 0.2],
                range_y=[0, df["wtp_eur"].max() * 1.1],
                title="Income vs WTP",
                labels={
                    "inc_jittered": "Einkommensindex (Multiplikator)",
                    "wtp_jittered": "Basis WTP (EUR)",
                },
                color_discrete_map=segment_colors,
            )

        if fig is not None:
            if len(fig.layout.sliders) > 0:
                fig.layout.sliders[0].currentvalue.prefix = "Tick: "

            # Make animation fast and smooth!
            if fig.layout.updatemenus:
                fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 800
                fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["easing"] = "linear"
                fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"] = False

            st.plotly_chart(fig, width="stretch")

    except Exception as exc:
        st.error(f"Fehler beim Rendern der Animation: {exc}")


def _render_figures(run_dir: Path) -> None:
    st.markdown("### Wissenschaftliche Auswertungen (Figures)")

    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    ts_dir = run_dir / "timeseries"

    tick_file = run_dir / "tick_mechanics.json"
    props_file = ts_dir / "properties.csv"
    factors_file = ts_dir / "factors.csv"
    pop_file = ts_dir / "population.csv"
    age_file = ts_dir / "age_property.csv"

    tabs = st.tabs(
        [
            "1. Yield & Markt",
            "2. Segmente & Alter",
            "3. Policies & Steuern",
            "4. Makro-Wirtschaft",
            "5. Airline-Kosten",
            "6. CIB-Faktoren",
        ]
    )

    # Lade alle Daten einmal
    df_ticks, df_props, df_factors, df_pop, df_age = None, None, None, None, None
    if tick_file.is_file():
        import json

        with open(tick_file, "r") as f:
            data = json.load(f)
        if data.get("ticks"):
            df_ticks = pd.DataFrame(data["ticks"])
    if props_file.is_file():
        df_props = pd.read_csv(props_file)
    if factors_file.is_file():
        df_factors = pd.read_csv(factors_file)
    if pop_file.is_file():
        df_pop = pd.read_csv(pop_file)
    if age_file.is_file():
        df_age = pd.read_csv(age_file)

    # TAB 1: YIELD & MARKT
    with tabs[0]:
        st.subheader("Angebot vs. Nachfrage")
        if df_ticks is not None:
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(
                go.Scatter(
                    x=df_ticks["tick"],
                    y=df_ticks.get("market_price_after_feedback_eur", df_ticks.get("ticket_price")),
                    name="Ticketpreis (EUR)",
                    line=dict(color="#059669", width=2.5),
                ),
                secondary_y=False,
            )
            fig1.add_trace(
                go.Scatter(
                    x=df_ticks["tick"],
                    y=df_ticks["booking_rate"],
                    name="Buchungsrate",
                    line=dict(color="#2563eb", dash="dot", width=2.5),
                ),
                secondary_y=True,
            )
            fig1.update_layout(
                title_text="Markt-Rückkopplung (Yield Management)", hovermode="x unified"
            )
            fig1.update_yaxes(title_text="Ticketpreis (EUR)", secondary_y=False)
            fig1.update_yaxes(title_text="Buchungsrate (0-1)", range=[0, 1.05], secondary_y=True)
            st.plotly_chart(fig1, width="stretch")

            # Zusätzlicher Plot: Marge vs Kosten
            if "cost_pressure" in df_ticks.columns and "provider_markup" in df_ticks.columns:
                fig_margin = go.Figure()
                fig_margin.add_trace(
                    go.Bar(
                        x=df_ticks["tick"], y=df_ticks["cost_pressure"], name="Kostendruck (Base)"
                    )
                )
                fig_margin.add_trace(
                    go.Bar(
                        x=df_ticks["tick"],
                        y=df_ticks["provider_markup"],
                        name="Airline-Marge (Markup)",
                    )
                )
                fig_margin.update_layout(
                    barmode="stack", title="Preis-Zusammensetzung", hovermode="x unified"
                )
                st.plotly_chart(fig_margin, width="stretch")
        else:
            st.info("Keine Marktdaten verfügbar.")

    # TAB 2: SEGMENTE & ALTER
    with tabs[1]:
        st.subheader("Mikro-Verhalten")
        c1, c2 = st.columns(2)
        with c1:
            if df_pop is not None and not df_pop.empty:
                fig_pop = go.Figure()
                for segment in df_pop["segment_id"].unique():
                    df_seg = df_pop[df_pop["segment_id"] == segment]
                    fig_pop.add_trace(
                        go.Scatter(
                            x=df_seg["tick"],
                            y=df_seg["booking_rate"],
                            mode="lines+markers",
                            name=segment.replace("_", " ").title(),
                        )
                    )
                fig_pop.update_layout(
                    title="Buchungsrate nach Profil-Segment",
                    xaxis_title="Tick",
                    yaxis_title="Buchungsrate",
                    yaxis_range=[0, 1.05],
                    hovermode="x unified",
                )
                st.plotly_chart(fig_pop, width="stretch")
            else:
                st.info("Keine Profil-Segment-Daten.")
        with c2:
            if df_age is not None and not df_age.empty:
                fig_age = go.Figure()
                for grp in df_age["age_group"].unique():
                    df_g = df_age[df_age["age_group"] == grp]
                    fig_age.add_trace(
                        go.Scatter(
                            x=df_g["tick"], y=df_g["booking_rate"], mode="lines", name=str(grp)
                        )
                    )
                fig_age.update_layout(
                    title="Buchungsrate nach Altersgruppe",
                    xaxis_title="Tick",
                    yaxis_title="Buchungsrate",
                    yaxis_range=[0, 1.05],
                    hovermode="x unified",
                )
                st.plotly_chart(fig_age, width="stretch")
            else:
                st.info("Keine Altersgruppen-Daten.")

    # TAB 3: POLICIES
    with tabs[2]:
        st.subheader("Politik & Steuern (Exogen)")
        if df_props is not None:
            policy_cols = [
                c
                for c in df_props.columns
                if c in ["carbon_tax_level", "saf_mandate_share", "efuel_subsidy", "airport_fee"]
            ]
            if policy_cols:
                fig_pol = make_subplots(specs=[[{"secondary_y": True}]])
                for col in policy_cols:
                    is_tax = col in ["carbon_tax_level", "airport_fee"]
                    fig_pol.add_trace(
                        go.Scatter(x=df_props["tick"], y=df_props[col], name=col),
                        secondary_y=not is_tax,
                    )
                fig_pol.update_layout(title="Politische Instrumente", hovermode="x unified")
                fig_pol.update_yaxes(title_text="Betrag (EUR/t o.ä.)", secondary_y=False)
                fig_pol.update_yaxes(title_text="Anteil (0-1)", secondary_y=True)
                st.plotly_chart(fig_pol, width="stretch")
            else:
                st.info("Keine Policy-Properties gefunden.")

    # TAB 4: MAKRO-WIRTSCHAFT
    with tabs[3]:
        st.subheader("Makroökonomische Indizes")
        if df_props is not None:
            macro_cols = [
                c
                for c in df_props.columns
                if c
                in [
                    "income_index",
                    "bevoelkerungsentwicklung",
                    "demand_growth_rate",
                    "oil_price_index",
                ]
            ]
            if macro_cols:
                fig_mac = make_subplots(specs=[[{"secondary_y": True}]])
                for mc in macro_cols:
                    is_pop = mc == "bevoelkerungsentwicklung"
                    fig_mac.add_trace(
                        go.Scatter(x=df_props["tick"], y=df_props[mc], name=mc), secondary_y=is_pop
                    )
                fig_mac.update_layout(title="Wirtschaft & Demographie", hovermode="x unified")
                fig_mac.update_yaxes(title_text="Index (1.0 = Basis)", secondary_y=False)
                fig_mac.update_yaxes(title_text="Population", secondary_y=True)
                st.plotly_chart(fig_mac, width="stretch")

    # TAB 5: AIRLINE-KOSTEN
    with tabs[4]:
        st.subheader("Kostenstruktur der Anbieter")
        if df_props is not None:
            cost_cols = [
                c
                for c in df_props.columns
                if c in ["maintenance_cost_index", "staff_cost_index", "fuel_price_change"]
            ]
            if cost_cols:
                fig_cost = go.Figure()
                for cc in cost_cols:
                    fig_cost.add_trace(go.Scatter(x=df_props["tick"], y=df_props[cc], name=cc))
                fig_cost.update_layout(title="Airline-Kosten-Indizes", hovermode="x unified")
                st.plotly_chart(fig_cost, width="stretch")

    # TAB 6: CIB-FAKTOREN
    with tabs[5]:
        st.subheader("CIB-Faktoren State (F1 - F7)")
        if df_factors is not None and not df_factors.empty:

            def factor_to_num(val):
                if isinstance(val, str) and val.startswith("F"):
                    try:
                        parts = val[1:].split(".")
                        return float(parts[0]) + (float(parts[1]) * 0.1)
                    except (ValueError, IndexError):
                        pass
                return 0.0

            df_f_num = df_factors.copy()
            for c in df_f_num.columns:
                if c != "tick":
                    df_f_num[c] = df_f_num[c].apply(factor_to_num)

            fig_cib = go.Figure()
            for col in [c for c in df_f_num.columns if c != "tick"]:
                fig_cib.add_trace(
                    go.Scatter(
                        x=df_f_num["tick"], y=df_f_num[col], mode="lines", name=col, line_shape="hv"
                    )
                )  # Step-lines
            fig_cib.update_layout(title="Faktoren (Zustands-Trajektorien)", hovermode="x unified")
            st.plotly_chart(fig_cib, width="stretch")
        else:
            st.info("Keine Faktoren-Daten verfügbar.")


def main() -> None:
    run_dashboard(
        render_animation=_render_animation,
        render_figures=_render_figures,
        render_config_editor=render_config_editor,
    )


if __name__ == "__main__":
    main()
