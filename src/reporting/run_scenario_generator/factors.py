"""Factor catalog lookups and the per-context factor profile (start/end/transitions)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.reporting.run_scenario_generator.context import RunScenarioContext

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FACTOR_CATALOG = REPO_ROOT / "configs" / "factors.json"
FACTOR_IDS = tuple(f"F{i}" for i in range(1, 8))


def _load_factor_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_FACTOR_CATALOG
    if not catalog_path.is_file():
        return {}
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _factor_state_label(catalog: dict[str, Any], factor_id: str, state_id: str | None) -> str:
    if not state_id:
        return "unbekannt"
    factor = catalog.get(factor_id) or {}
    states = factor.get("possible_states") or {}
    return str(states.get(state_id) or state_id)


def _factor_name(catalog: dict[str, Any], factor_id: str) -> str:
    factor = catalog.get(factor_id) or {}
    return str(factor.get("name") or factor_id)


def faktor_namen(catalog: dict[str, Any]) -> dict[str, str]:
    """Faktor- und Zustandskennungen auf ihre Bezeichnung — für das Faktenblatt (P8-V3)."""

    namen: dict[str, str] = {}
    for factor_id, eintrag in catalog.items():
        if not isinstance(eintrag, dict):
            continue
        namen[factor_id] = _factor_name(catalog, factor_id)
        for state_id in eintrag.get("possible_states") or {}:
            namen[state_id] = _factor_state_label(catalog, factor_id, state_id)
    return namen


def _flip_state(state_id: str) -> str:
    if not state_id or "." not in state_id:
        return state_id
    factor_id, suffix = state_id.split(".", 1)
    flipped = "2" if suffix == "1" else "1"
    return f"{factor_id}.{flipped}"


def _format_factor_compact(catalog: dict[str, Any], states: dict[str, str]) -> str:
    parts: list[str] = []
    for factor_id in FACTOR_IDS:
        state_id = states.get(factor_id)
        if state_id:
            parts.append(f"{factor_id}={state_id}")
    return ", ".join(parts)


def _format_factor_labels_short(
    catalog: dict[str, Any], states: dict[str, str], *, max_items: int = 4
) -> str:
    bits: list[str] = []
    for factor_id in FACTOR_IDS:
        state_id = states.get(factor_id)
        if not state_id:
            continue
        bits.append(f"{factor_id} {_factor_state_label(catalog, factor_id, state_id)}")
        if len(bits) >= max_items:
            break
    suffix = " …" if len(bits) < len([f for f in FACTOR_IDS if states.get(f)]) else ""
    return "; ".join(bits) + suffix


def build_factor_profile(
    context: RunScenarioContext,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = catalog or _load_factor_catalog()
    metrics = context.summary_metrics
    start_states = dict(metrics.get("factor_states_start") or {})
    end_states = dict(metrics.get("factor_states_end") or {})
    if not end_states and context.factors:
        last = context.factors[-1]
        end_states = {key: value for key, value in last.items() if key != "tick"}
    if not start_states and context.factors:
        first = context.factors[0]
        start_states = {key: value for key, value in first.items() if key != "tick"}

    def _enrich(states: dict[str, Any]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for factor_id in FACTOR_IDS:
            state_id = states.get(factor_id)
            if not state_id:
                continue
            rows.append(
                {
                    "factor_id": factor_id,
                    "factor_name": _factor_name(catalog, factor_id),
                    "state_id": str(state_id),
                    "state_label": _factor_state_label(catalog, factor_id, str(state_id)),
                }
            )
        return rows

    transitions: list[dict[str, Any]] = []
    for item in metrics.get("factor_transitions") or []:
        if not isinstance(item, dict):
            continue
        factor_id = str(item.get("factor_id") or "")
        from_state = str(item.get("from_state") or "")
        to_state = str(item.get("to_state") or "")
        transitions.append(
            {
                "tick": item.get("tick"),
                "factor_id": factor_id,
                "factor_name": _factor_name(catalog, factor_id),
                "from_state": from_state,
                "from_label": _factor_state_label(catalog, factor_id, from_state),
                "to_state": to_state,
                "to_label": _factor_state_label(catalog, factor_id, to_state),
            }
        )

    return {
        "start": _enrich(start_states),
        "end": _enrich(end_states),
        "transitions": transitions,
        "end_by_id": {row["factor_id"]: row["state_id"] for row in _enrich(end_states)},
    }
