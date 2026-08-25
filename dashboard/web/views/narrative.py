"""Tab «Bericht»: das abschließende Narrativ des Laufs (`final_narrative.md`)."""

from __future__ import annotations

from pathlib import Path

from dash import html

from dashboard.run_browser import read_run_file
from dashboard.web import components as ui


def render(run_dir: Path, run_id: str) -> html.Div:
    path = run_dir / "final_narrative.md"
    if not path.is_file():
        return ui.alert("`final_narrative.md` fehlt in diesem Run.", "warning")
    return ui.card(ui.markdown(read_run_file(path)), class_name="max-w-4xl")
