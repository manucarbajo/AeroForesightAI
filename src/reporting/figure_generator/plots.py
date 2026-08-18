"""All matplotlib figure renderers, one function per PNG artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.reporting.figure_generator.series import RunSeries


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    _ensure_dir(path.parent)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_scenario_comparison(
    series_list: list[RunSeries], output_path: Path, *, metric: str
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    for series in series_list:
        if metric == "booking":
            y = series.booking_rate
            ylabel = "Booking Rate"
            title = "Szenario-Vergleich: Booking Rate"
        else:
            y = series.ticket_price
            ylabel = "Ticketpreis (EUR)"
            title = "Szenario-Vergleich: Ticketpreis"
        ax.plot(series.ticks, y, marker=".", linewidth=1.8, label=series.label)
    ax.set_xlabel("Tick")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    return _save_figure(fig, output_path)


def plot_segment_booking(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if series.segment_booking:
        for group, rates in series.segment_booking.items():
            ax.plot(
                series.segment_ticks[: len(rates)],
                rates,
                label=group.replace("_", " ").title(),
                marker="s",
            )
    ax.set_title(f"Buchungsrate nach Segment: {series.label}")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Buchungsrate")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    return _save_figure(fig, output_path)


def plot_cib_scores(scores: list[dict[str, Any]], output_path: Path) -> Path:
    names = [row["sweep_name"] for row in scores]
    values = [float(row["consistency_score"]) for row in scores]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(names, values, color="#2563eb")
    ax.set_xlabel("CIB Consistency Score")
    ax.set_title("Szenario-Plausibilität (CIB Consistency)")
    ax.set_xlim(0, max(values) * 1.15 if values else 1)
    for bar, value in zip(bars, values):
        ax.text(
            value + 0.005,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}",
            va="center",
            fontsize=8,
        )
    ax.grid(True, axis="x", alpha=0.3)
    return _save_figure(fig, output_path)


def plot_price_vs_booking(series: RunSeries, output_path: Path) -> Path:
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(series.ticks, series.ticket_price, color="#059669", marker="o", label="Ticketpreis")
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Ticketpreis (EUR)", color="#059669")
    ax1.tick_params(axis="y", labelcolor="#059669")
    ax2 = ax1.twinx()
    ax2.plot(series.ticks, series.booking_rate, color="#2563eb", marker="s", label="Booking Rate")
    ax2.set_ylabel("Booking Rate", color="#2563eb")
    ax2.tick_params(axis="y", labelcolor="#2563eb")
    ax2.set_ylim(0, 1)
    ax1.set_title(f"Markt-Rückkopplung: Preis und Booking ({series.label})")
    ax1.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_policy_shock(
    series: RunSeries, output_path: Path, shock_ticks: tuple[int, ...] = (15, 30)
) -> Path:
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.plot(series.ticks, series.carbon_tax, color="#dc2626", marker="o", label="CO₂-Steuer")
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("CO₂-Steuer (EUR/t)", color="#dc2626")
    ax1.tick_params(axis="y", labelcolor="#dc2626")
    for tick in shock_ticks:
        ax1.axvline(tick, color="#dc2626", linestyle="--", alpha=0.45, linewidth=1)
    ax2 = ax1.twinx()
    ax2.plot(series.ticks, series.booking_rate, color="#2563eb", marker="s", label="Booking Rate")
    ax2.set_ylabel("Booking Rate", color="#2563eb")
    ax2.tick_params(axis="y", labelcolor="#2563eb")
    ax2.set_ylim(0, 1)
    ax1.set_title(f"Policy-Shock: CO₂-Steuer und Booking ({series.label})")
    ax1.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_system_dynamics(series: RunSeries, output_path: Path) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    axes[0].plot(
        series.ticks, series.booking_rate, color="#2563eb", marker="o", label="Booking Rate"
    )
    axes[0].set_ylabel("Booking Rate")
    axes[0].set_ylim(0, 1)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(f"Systemdynamik: Booking und Properties ({series.label})")

    axes[1].plot(series.ticks, series.carbon_tax, label="CO₂-Steuer", linewidth=1.8)
    if any(v == v for v in series.income_index):
        axes[1].plot(series.ticks, series.income_index, label="Einkommensindex", linewidth=1.8)
    if series.saf_mandate and any(v == v for v in series.saf_mandate):
        axes[1].plot(series.ticks, series.saf_mandate, label="SAF-Mandat", linewidth=1.8)
    axes[1].set_xlabel("Tick")
    axes[1].set_ylabel("Property-Wert")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_age_segments(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if not series.age_booking:
        ax.text(0.5, 0.5, "Keine Alterssegment-Daten", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    for group, values in sorted(series.age_booking.items()):
        ticks = series.age_ticks[: len(values)]
        ax.plot(ticks, values, marker="o", linewidth=1.5, label=group)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Booking Rate")
    ax.set_ylim(0, 1)
    ax.set_title(f"Booking nach Altersgruppe ({series.label})")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_factor_states(series: RunSeries, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    if not series.factor_values:
        ax.text(0.5, 0.5, "Keine Faktor-Zeitreihen", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    for factor_id, values in sorted(series.factor_values.items()):
        ticks = series.factor_ticks[: len(values)]
        ax.step(ticks, values, where="post", linewidth=1.8, label=factor_id)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Faktor-Zustand (numerisch)")
    ax.set_title(f"Faktor-Zustände über Zeit ({series.label})")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    return _save_figure(fig, output_path)


def plot_population_distribution(run_path: Path, output_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))
    pop_csv = run_path / "population.csv"
    if not pop_csv.is_file():
        ax.text(0.5, 0.5, "Keine Populationsdaten", ha="center", va="center")
        ax.set_axis_off()
        return _save_figure(fig, output_path)

    try:
        import pandas as pd

        df = pd.read_csv(pop_csv)

        # Color by segment
        if "business" in df.columns:
            # Pandas might read booleans as strings depending on format
            is_business = df["business"].astype(str).str.lower().isin(["true", "1"])
            colors = is_business.map({True: "#1f77b4", False: "#ff7f0e"})  # Blue/Orange
            # Create dummy lines for legend
            ax.scatter([], [], c="#1f77b4", label="Business")
            ax.scatter([], [], c="#ff7f0e", label="Leisure")
            ax.legend()
        else:
            colors = "#1f77b4"

        # Optional: scale marker size by income
        sizes = 20
        if "income_factor" in df.columns:
            sizes = df["income_factor"].astype(float) * 20

        ax.scatter(
            df["wtp_eur"],
            df["environmental_awareness"],
            c=colors,
            s=sizes,
            alpha=0.6,
            edgecolors="none",
        )
        ax.set_xlabel("Zahlungsbereitschaft (WTP in €)")
        ax.set_ylabel("Umweltbewusstsein (0-1)")
        ax.set_title("Agenten-Verteilung: Umweltbewusstsein vs. WTP")
        ax.grid(True, alpha=0.3)
    except Exception as e:
        ax.text(0.5, 0.5, f"Fehler:\n{str(e)}", ha="center", va="center")
        ax.set_axis_off()

    return _save_figure(fig, output_path)
