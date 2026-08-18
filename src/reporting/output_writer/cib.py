"""CIB matrix persistence."""

import json
from pathlib import Path

from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def save_cib_matrix(
    state,
    filename: str = "cib_matrix.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Speichert die CIB-Matrix als JSON.
        state: finaler SimulationState
        Default Name der Ausgabedatei: cib_matrix.json
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)

    if state.cib_matrix is None:
        cib_data = {"entries": [], "round_generated": 0, "metadata": {}}
    else:
        cib_data = state.cib_matrix.model_dump()

        # Faktornamen direkt in source_factor und target_factor einbetten
        enriched_entries = []
        for entry in cib_data["entries"]:
            source_id = entry["source_factor"]
            target_id = entry["target_factor"]

            source_factor = state.environment.factors.get(source_id)
            target_factor = state.environment.factors.get(target_id)

            entry["source_factor"] = (
                f"{source_id} - {source_factor.name}" if source_factor else source_id
            )
            entry["target_factor"] = (
                f"{target_id} - {target_factor.name}" if target_factor else target_id
            )

            enriched_entries.append(entry)

        cib_data["entries"] = enriched_entries

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cib_data, f, indent=2, ensure_ascii=False)

    return filepath
