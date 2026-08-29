"""Run metadata: Modell, Backend, Tick-Zahlen — und wie der Lauf entstanden ist."""

import json
from datetime import UTC, datetime
from pathlib import Path

from src.models.llm_models import LLMDegradation
from src.reporting.output_writer.paths import ensure_output_dir, resolve_output_path
from src.reporting.output_writer.provenance import (
    MODES_WITHOUT_ANY_LLM,
    code_version,
    compute_mode,
    recorded_fingerprint,
)

#: Felder, die ausschliesslich ein beteiligtes Sprachmodell beschreiben. Sie
#: stammen aus den Argumenten und stehen dort auch dann, wenn nie gefragt
#: wurde — bei einem Lauf ohne Modell sind sie deshalb `null`.
LLM_ONLY_FIELDS = ("model", "base_url", "temperature", "max_tokens")


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
        # **Wie lange gerechnet wurde** (P1.9-W4.3). Kommt aus dem Zustand und
        # wird hier nicht neu berechnet: `save_run_metadata` läuft nach dem
        # Schreiben mehrerer Artefakte und misst sonst die falsche Spanne —
        # derselbe Fehler, den P0.6 beim Config-Fingerabdruck gefunden hat.
        "elapsed_seconds": getattr(state, "elapsed_seconds", None),
        "tick_unit": state.clock.tick_unit,
        "market_enabled": not args.no_market,
        "total_events": len(state.event_log),
        "total_round_results": len(state.round_results),
        "total_price_history": len(state.price_history),
    }

    # P0.6: Woraus dieser Lauf entstanden ist. Ohne diese Felder ließ sich ein
    # Lauf aus seinen Artefakten nicht nachstellen — bei einem Produkt, dessen
    # Verkaufsargument Reproduzierbarkeit ist, die teuerste Lücke in Phase 0.
    # Der Seed kommt aus dem State, nicht aus den Argumenten: Dort steht der
    # tatsächlich benutzte, während `args.seed` bei einem Multi-Run nur der
    # Ausgangswert der Folge ist.
    state_seed = getattr(getattr(state, "config", None), "seed", None)
    metadata["seed"] = state_seed if state_seed is not None else getattr(args, "seed", None)
    metadata["compute_mode"] = compute_mode(args)
    metadata["mock_llm"] = bool(getattr(args, "mock_llm", False))
    metadata["deterministic_only"] = bool(getattr(args, "deterministic_only", False))
    metadata["config_fingerprint"] = recorded_fingerprint(state).model_dump()
    metadata["code_version"] = code_version()

    # Ohne Sprachmodell beschreiben diese vier Felder nichts. `args.model` und
    # die drei daneben stehen unabhaengig davon, ob je gefragt wurde — ein
    # Mock-Lauf schrieb damit `"model": "llama3.2"` neben
    # `"compute_mode": "mock_llm"`. Die erste Gegenprobe zu P0.6 hat genau
    # diesen Widerspruch gefunden; behoben war er nur in der Dashboard-Kachel
    # (`views/overview.py::_model_label`), also fuer eine einzige Oberflaeche.
    # Die Zusage von P0.6 lautet aber «aus `run_metadata.json` **allein**» —
    # wer die Datei ohne Dashboard liest, bekam vier Angaben ueber ein Modell,
    # das nie beteiligt war. Die Schluessel bleiben stehen und werden `null`:
    # Das Schema aendert sich nicht, und `null` ist eine Aussage, kein Fehlen.
    if metadata["compute_mode"] in MODES_WITHOUT_ANY_LLM:
        for field in LLM_ONLY_FIELDS:
            metadata[field] = None

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
