"""CIB matrix visualization module.

Provides heatmap, network diagram, and active/passive bar chart
renderings of the CIB cross-impact matrix.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import numpy as np

from src.models.cib_models import (
    CIBMatrix,
    DESCRIPTOR_IDS,
    FACTOR_IDS,
    NUM_FACTORS,
    STATES_PER_FACTOR,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


# ---------------------------------------------------------------------------
# Color configuration
# ---------------------------------------------------------------------------

CIB_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "cib_diverging",
    ["#d32f2f", "#ffcdd2", "#ffffff", "#c8e6c9", "#388e3c"],
    N=256,
)

FACTOR_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2",
]


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------


def render_heatmap(
    matrix: CIBMatrix,
    output_path: Path | None = None,
    title: str = "CIB Cross-Impact Matrix",
    figsize: tuple[float, float] = (12, 10),
) -> Figure:
    """Render the CIB matrix as a 14×14 heatmap."""
    data = matrix.to_numpy()

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    im = ax.imshow(data, cmap=CIB_CMAP, vmin=-3, vmax=3, aspect="equal")

    # Axis labels
    ax.set_xticks(range(len(DESCRIPTOR_IDS)))
    ax.set_yticks(range(len(DESCRIPTOR_IDS)))
    ax.set_xticklabels(DESCRIPTOR_IDS, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(DESCRIPTOR_IDS, fontsize=8)

    # Cell value annotations
    for i in range(len(DESCRIPTOR_IDS)):
        for j in range(len(DESCRIPTOR_IDS)):
            src_factor = DESCRIPTOR_IDS[i].split(".")[0]
            tgt_factor = DESCRIPTOR_IDS[j].split(".")[0]
            if src_factor == tgt_factor:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=True, color="#e0e0e0"))
                continue
            value = data[i, j]
            if value != 0:
                color = "white" if abs(value) >= 2 else "black"
                ax.text(j, i, str(value), ha="center", va="center", fontsize=7, color=color)

    # Factor group separators
    for k in range(1, NUM_FACTORS):
        pos = k * STATES_PER_FACTOR - 0.5
        ax.axhline(pos, color="black", linewidth=0.8, alpha=0.5)
        ax.axvline(pos, color="black", linewidth=0.8, alpha=0.5)

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Ziel-Deskriptor (wird beeinflusst)")
    ax.set_ylabel("Quell-Deskriptor (beeinflusst)")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Einflussstärke (-3 hemmend ... +3 fördernd)")
    cbar.set_ticks([-3, -2, -1, 0, 1, 2, 3])

    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    return fig


# ---------------------------------------------------------------------------
# Network diagram
# ---------------------------------------------------------------------------


def render_network(
    matrix: CIBMatrix,
    output_path: Path | None = None,
    title: str = "CIB Factor Network",
    threshold: int = 1,
    figsize: tuple[float, float] = (10, 10),
) -> Figure:
    """Render the CIB matrix as a factor-level network diagram.

    Nodes are factors, edges represent net influence between factors.
    Only edges with absolute influence >= threshold are shown.
    """
    data = matrix.to_numpy()
    G = nx.DiGraph()

    # Add factor nodes
    for i, fid in enumerate(FACTOR_IDS):
        G.add_node(fid, color=FACTOR_COLORS[i])

    # Aggregate influences at factor level
    for i, src_factor in enumerate(FACTOR_IDS):
        for j, tgt_factor in enumerate(FACTOR_IDS):
            if i == j:
                continue
            # Sum influences from all source descriptors to all target descriptors
            total = 0
            for si in range(STATES_PER_FACTOR):
                for sj in range(STATES_PER_FACTOR):
                    row = i * STATES_PER_FACTOR + si
                    col = j * STATES_PER_FACTOR + sj
                    total += data[row, col]

            if abs(total) >= threshold:
                G.add_edge(src_factor, tgt_factor, weight=total)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    pos = nx.circular_layout(G)

    # Draw nodes
    node_colors = [FACTOR_COLORS[i] for i in range(len(FACTOR_IDS))]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=800, node_color=node_colors, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight="bold")

    # Draw edges with color/width based on weight
    edges = G.edges(data=True)
    for u, v, d in edges:
        weight = d["weight"]
        color = "#388e3c" if weight > 0 else "#d32f2f"
        width = min(abs(weight) * 0.5, 4.0)
        alpha = min(abs(weight) / 6.0 + 0.3, 1.0)
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)], ax=ax,
            width=width, edge_color=color, alpha=alpha,
            arrows=True, arrowsize=15,
            connectionstyle="arc3,rad=0.1",
        )

    # Edge labels
    edge_labels = {(u, v): f"{d['weight']:+d}" for u, v, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax, font_size=7)

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    return fig


# ---------------------------------------------------------------------------
# Active/Passive bar chart
# ---------------------------------------------------------------------------


def render_active_passive_bar(
    matrix: CIBMatrix,
    output_path: Path | None = None,
    title: str = "CIB Factor Scores (Aktiv / Passiv)",
    figsize: tuple[float, float] = (10, 6),
) -> Figure:
    """Render a bar chart comparing active and passive scores per factor."""
    scores = matrix.compute_factor_scores()

    factor_ids = [s.factor_id for s in scores]
    active = [s.active_score for s in scores]
    passive = [s.passive_score for s in scores]

    x = np.arange(len(factor_ids))
    width = 0.35

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    bars_active = ax.bar(x - width / 2, active, width, label="Aktiv-Score", color="#1976d2", alpha=0.85)
    bars_passive = ax.bar(x + width / 2, passive, width, label="Passiv-Score", color="#f57c00", alpha=0.85)

    ax.set_xlabel("Faktor")
    ax.set_ylabel("Score (Summe Absolutwerte)")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(factor_ids)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Value labels on bars
    for bar in bars_active:
        height = bar.get_height()
        if height > 0:
            ax.annotate(str(int(height)), xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)
    for bar in bars_passive:
        height = bar.get_height()
        if height > 0:
            ax.annotate(str(int(height)), xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)

    plt.tight_layout()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    return fig


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="CIB Matrix Visualizer")
    parser.add_argument("--input", required=True, help="Path to CIB matrix JSON file")
    parser.add_argument("--output", required=True, help="Output directory for images")
    parser.add_argument("--format", choices=["png", "svg"], default="png", help="Output format")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path) as f:
        data = json.load(f)

    matrix = CIBMatrix(**data)
    ext = args.format

    render_heatmap(matrix, output_dir / f"cib_heatmap.{ext}")
    render_network(matrix, output_dir / f"cib_network.{ext}")
    render_active_passive_bar(matrix, output_dir / f"cib_scores.{ext}")

    print(f"Visualizations saved to {output_dir}/")


if __name__ == "__main__":
    main()
