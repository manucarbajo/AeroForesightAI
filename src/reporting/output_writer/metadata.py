"""Run metadata (model, backend, tick counts) persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path

from src.models.llm_models import LLMDegradation
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path


def save_run_metadata(
    state,
    args,
    filename: str = "run_metadata.json",
    *,
    output_subdir: str | Path | None = None,
    run_dir: Path | None = None,
    run_id: str | None = None,
) -> str:
    """
    Speichert Metadaten des Simulationslaufs als JSON.
        state: finaler SimulationState
        args: geparste CLI-Argumente
        Default Name der Ausgabedatei: run_metadata.json
    """
    ensure_output_dir()
    filepath = resolve_output_path(filename, output_subdir, run_dir=run_dir)

    metadata = {
        "timestamp": datetime.now(UTC).isoformat(),
        "run_id": run_id or (run_dir.name if run_dir is not None else None),
        "simulation_name": getattr(args, "simulation_name", None),
        "simulation_description": getattr(args, "simulation_description", None),
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "ticks_completed": state.clock.current_tick,
        "ticks_max": state.clock.max_ticks,
        "tick_unit": state.clock.tick_unit,
        "market_enabled": not args.no_market,
        "total_events": len(state.event_log),
        "total_round_results": len(state.round_results),
        "total_price_history": len(state.price_history),
    }

    # P0.1: Ein Lauf, dessen Sprachmodell ausgefallen ist, sagt das hier. Die
    # drei Felder stehen immer in der Datei — auch bei einem sauberen Lauf —,
    # damit ihre Abwesenheit nur eines heissen kann: aelter als P0.1.
    degradation = LLMDegradation.from_incidents(list(getattr(state, "llm_incidents", []) or []))
    metadata["degraded"] = degradation.degraded
    metadata["llm_incident_count"] = degradation.incident_count
    metadata["llm_degraded_ticks"] = degradation.degraded_ticks

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return filepath
