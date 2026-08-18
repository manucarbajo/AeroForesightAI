"""Derived scenario persistence."""

import json
from pathlib import Path

from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def save_scenarios(
    payload: dict,
    filename: str = "scenarios.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save derived scenarios as JSON."""
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return filepath


def save_scenarios_markdown(
    markdown: str,
    filename: str = "scenarios.md",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """Save derived scenarios as Markdown."""
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
    return filepath
