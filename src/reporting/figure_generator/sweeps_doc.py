"""Sweep timeseries JSON export and the generated scenario_runs.md summary doc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.reporting.figure_generator.series import RunSeries


def _save_sweep_timeseries(series: RunSeries, output_dir: Path) -> Path:
    payload = {
        "sweep_id": series.run_id,
        "label": series.label,
        "ticks": series.ticks,
        "booking_rate": series.booking_rate,
        "ticket_price": series.ticket_price,
        "carbon_tax": series.carbon_tax,
    }
    path = output_dir / f"{series.run_id}_timeseries.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_scenario_runs_doc(
    *,
    output_path: Path,
    figure_paths: dict[str, Path],
    sweep_series: list[RunSeries],
    reference: RunSeries,
    scores: list[dict[str, Any]],
) -> Path:
    lines = [
        "# Szenario-Läufe und Figures",
        "",
        "Automatisch erzeugte Visualisierungen für Strategic Foresight.",
        "",
        "## Foresight-Szenarien (deterministisch, in ihrer angelegten Länge)",
        "",
        "| Szenario | ID | Consistency |",
        "| --- | --- | --- |",
    ]
    score_by_id = {row["sweep_id"]: row for row in scores}
    for series in sweep_series:
        score = score_by_id.get(series.run_id, {})
        consistency = score.get("consistency_score", "—")
        if isinstance(consistency, float):
            consistency = f"{consistency:.3f}"
        lines.append(f"| {series.label} | `{series.run_id}` | {consistency} |")

    lines.extend(
        [
            "",
            f"## Referenzlauf ({reference.label})",
            "",
            f"- Ticks: {len(reference.ticks)}",
            (
                f"- Booking: {reference.booking_rate[0]:.1%} → {reference.booking_rate[-1]:.1%}"
                if reference.booking_rate
                else "- Booking: —"
            ),
            "",
            "## Figures",
            "",
        ]
    )
    for title, path in figure_paths.items():
        rel = (
            path.relative_to(output_path.parent)
            if path.is_relative_to(output_path.parent)
            else path.name
        )
        lines.append(f"- **{title}:** `{rel}`")

    lines.extend(
        [
            "",
            "## Erzeugung",
            "",
            "```powershell",
            "python -m src.reporting.figure_generator",
            "```",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
