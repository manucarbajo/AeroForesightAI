"""Run-artifact loading, summary metrics, and the LLMCallable protocol."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunScenarioContext:
    run_id: str
    run_dir: Path
    metadata: dict[str, Any]
    tick_mechanics: dict[str, Any]
    event_log: list[dict[str, Any]]
    price_history: list[dict[str, Any]]
    population_segments: list[dict[str, Any]]
    factors: list[dict[str, Any]]
    cib_matrix: dict[str, Any] | None
    summary_metrics: dict[str, Any]
    phase_ticks: list[dict[str, Any]]
    agent_digest: dict[str, Any]


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_factor_transitions(factors: list[dict[str, str]]) -> list[dict[str, Any]]:
    if len(factors) < 2:
        return []
    factor_ids = sorted(key for key in factors[0] if key != "tick")
    transitions: list[dict[str, Any]] = []
    previous = {factor_id: factors[0].get(factor_id) for factor_id in factor_ids}
    for row in factors[1:]:
        tick = int(row.get("tick") or 0)
        for factor_id in factor_ids:
            current = row.get(factor_id)
            if current and current != previous.get(factor_id):
                transitions.append(
                    {
                        "tick": tick,
                        "factor_id": factor_id,
                        "from_state": previous.get(factor_id),
                        "to_state": current,
                    }
                )
            previous[factor_id] = current
    return transitions


def _compute_summary_metrics(
    ticks: list[dict[str, Any]],
    population_segments: list[dict[str, str]],
    factors: list[dict[str, str]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "ticks_completed": metadata.get("ticks_completed"),
        "ticks_max": metadata.get("ticks_max"),
        "simulation_name": metadata.get("simulation_name") or metadata.get("name"),
    }
    if ticks:
        bookings = [_safe_float(row.get("booking_rate")) for row in ticks]
        bookings = [value for value in bookings if value is not None]
        prices = [_safe_float(row.get("market_price_after_feedback_eur")) for row in ticks]
        prices = [value for value in prices if value is not None]
        if bookings:
            summary["booking_rate_start"] = round(bookings[0], 4)
            summary["booking_rate_end"] = round(bookings[-1], 4)
            summary["booking_rate_min"] = round(min(bookings), 4)
            summary["booking_rate_max"] = round(max(bookings), 4)
        if prices:
            summary["ticket_price_start_eur"] = round(prices[0], 2)
            summary["ticket_price_end_eur"] = round(prices[-1], 2)
            summary["ticket_price_min_eur"] = round(min(prices), 2)
            summary["ticket_price_max_eur"] = round(max(prices), 2)

    if population_segments:
        last_tick = max(int(row["tick"]) for row in population_segments if row.get("tick"))
        end_rows = [row for row in population_segments if int(row["tick"]) == last_tick]
        summary["segment_booking_end"] = {
            row["segment_id"]: round(float(row["booking_rate"]), 4)
            for row in end_rows
            if row.get("segment_id") and row.get("booking_rate")
        }

    if factors:
        last = factors[-1]
        first = factors[0]
        summary["factor_states_end"] = {key: value for key, value in last.items() if key != "tick"}
        summary["factor_states_start"] = {
            key: value for key, value in first.items() if key != "tick"
        }
        summary["factor_transitions"] = _extract_factor_transitions(factors)

    return summary


def _select_phase_ticks(
    ticks: list[dict[str, Any]], *, max_phases: int = 3
) -> list[dict[str, Any]]:
    if not ticks:
        return []
    if len(ticks) <= max_phases:
        return ticks
    indices = [0, len(ticks) // 2, len(ticks) - 1]
    selected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index in indices:
        if index in seen:
            continue
        seen.add(index)
        selected.append(ticks[index])
    return selected


def load_run_scenario_context(
    run_id: str,
    *,
    run_dir: Path | None = None,
    outputs_root: Path | str | None = None,
) -> RunScenarioContext:
    from src.reporting.run_scenario_generator.agent_digest import build_agent_digest
    from src.reporting.state_explorer import resolve_run_dir

    directory = run_dir or resolve_run_dir(run_id, outputs_root=outputs_root)
    metadata = _load_json(directory / "run_metadata.json", {})
    tick_mechanics = _load_json(directory / "tick_mechanics.json", {"ticks": []})
    ticks = list(tick_mechanics.get("ticks") or [])
    population_segments = _load_csv(directory / "timeseries" / "population.csv")
    factors = _load_csv(directory / "timeseries" / "factors.csv")
    phase_ticks = _select_phase_ticks(ticks)
    event_log = _load_json(directory / "event_log.json", [])
    event_log = event_log if isinstance(event_log, list) else []
    return RunScenarioContext(
        run_id=run_id,
        run_dir=directory,
        metadata=metadata if isinstance(metadata, dict) else {},
        tick_mechanics=tick_mechanics if isinstance(tick_mechanics, dict) else {"ticks": []},
        event_log=event_log,
        price_history=_load_json(directory / "price_history.json", []),
        population_segments=population_segments,
        factors=factors,
        cib_matrix=_load_json(directory / "cib_matrix.json", None),
        summary_metrics=_compute_summary_metrics(
            ticks,
            population_segments,
            factors,
            metadata if isinstance(metadata, dict) else {},
        ),
        phase_ticks=phase_ticks,
        agent_digest=build_agent_digest(
            run_dir=directory,
            phase_ticks=phase_ticks,
            event_log=event_log,
        ),
    )


def _cib_score(context: RunScenarioContext) -> float | None:
    matrix = context.cib_matrix
    if not isinstance(matrix, dict):
        return None
    meta = matrix.get("metadata") or {}
    if isinstance(meta, dict) and meta.get("consistency_score") is not None:
        return float(meta["consistency_score"])
    scores = matrix.get("factor_scores") or []
    if isinstance(scores, list) and scores:
        active = [
            float(item.get("active_score", 0))
            for item in scores
            if isinstance(item, dict) and item.get("active_score") is not None
        ]
        if active:
            return round(sum(active) / len(active), 3)
    return None


def _booking_trend(metrics: dict[str, Any]) -> str:
    start = metrics.get("booking_rate_start")
    end = metrics.get("booking_rate_end")
    if start is None or end is None:
        return "stabil"
    delta = float(end) - float(start)
    if delta > 0.05:
        return "steigend"
    if delta < -0.05:
        return "fallend"
    return "stabil"


def _price_trend(metrics: dict[str, Any]) -> str:
    start = metrics.get("ticket_price_start_eur")
    end = metrics.get("ticket_price_end_eur")
    if start is None or end is None:
        return "stabil"
    delta = float(end) - float(start)
    if delta > 5:
        return "steigend"
    if delta < -5:
        return "fallend"
    return "stabil"


# `_plausibility_for_rank` ist mit P2.0 entfallen. Sie machte aus dem
# Präsentationsrang eine Aussage über die Welt — Rang 1 hieß «hoch plausibel»,
# Rang 3 «niedrig» —, und zwar auch dann, wenn gar kein CIB-Score vorlag. Ohne
# Score gibt es heute **kein** Band (`candidates._konsistenz_band`).


def lauf_name(context: RunScenarioContext) -> str:
    """Wie ein Lauf in seinen Artefakten heißt — **ein Name, kein Pfad** (P7.2-U2.3).

    Die Überschrift von `run_scenario.md` lautete «Szenarien zum Lauf
    sweeps/sweep_transformation_conflict»: Sie nahm den eingegebenen Namen und
    fiel sonst auf die **Kennung** zurück — und die Kennung eines Laufs aus
    einem Szenario-Vergleich ist sein Ablageort.

    Drei Quellen in dieser Reihenfolge, und jede ist eine Aussage:

    * der **Name**, den jemand dem Lauf gegeben hat;
    * sonst der **Rahmen**, unter dem er stand (`rahmen.name`, seit P2.0-B im
      Artefakt) — genau das, was einen Vergleichslauf unterscheidbar macht;
    * sonst die **Kennung ohne ihren Ordner**: ein Name bleibt sie auch dann.
    """

    name = (context.summary_metrics or {}).get("simulation_name")
    if isinstance(name, str) and name.strip():
        return name.strip()

    rahmen = (context.metadata or {}).get("rahmen") or {}
    aus_rahmen = rahmen.get("name") if isinstance(rahmen, dict) else None
    if isinstance(aus_rahmen, str) and aus_rahmen.strip():
        return aus_rahmen.strip()

    return str(context.run_id).replace("\\", "/").rsplit("/", 1)[-1]
