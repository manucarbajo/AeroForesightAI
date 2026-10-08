"""Persistence for LLM incidents (`llm_incidents.json`).

Die Datei entsteht **nur**, wenn es Vorfälle gab. Das ist Absicht: ein sauberer
Lauf soll kein leeres Beweisstück hinterlassen. Damit die Abwesenheit trotzdem
eindeutig ist, trägt `run_metadata.json` die Felder `degraded` und
`llm_incident_count` immer — auch mit `false` und `0`.
"""

import json
from pathlib import Path

from src.models.llm_models import LLMIncident
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def save_llm_incidents(
    incidents: list[LLMIncident],
    filename: str = "llm_incidents.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str | None:
    """Vorfälle als JSON ablegen; ``None``, wenn es keine gab.

    **Ohne Vorfall bleibt auch keine Datei eines früheren Laufs liegen** (P8-V4).
    Ein Szenario-Vergleich schreibt in feste Ordner (``sweeps/sweep_<id>``);
    bis zum 2026-09-29 lag dort eine ``llm_incidents.json`` vom 2026-09-07
    neben ``degraded: false`` des neuen Laufs, und die Telemetrie im Leitstand
    liest genau diese Datei — sie zeigte einen Ausfall, den es nicht gab.
    Abgeräumt wird nur in einem benannten Laufordner, nie im Ausgabewurzel.
    """

    if not incidents:
        if run_dir is not None:
            veraltet = Path(run_dir) / filename
            if veraltet.is_file():
                veraltet.unlink()
        return None

    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)
    payload = [incident.model_dump() for incident in incidents]
    with open(filepath, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)
    return filepath
