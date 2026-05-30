from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models.agent_models import AgentResponse
from src.models.event_models import EventLogEntry, RoundResult
from src.models.state_models import SimulationState


@dataclass(frozen=True)
class ProtocolOptions:
    include_raw_output: bool = False


def _safe_first_line(text: str, fallback: str = "") -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return fallback
    return cleaned.splitlines()[0].strip()


def _group_round_results(round_results: list[RoundResult]) -> dict[int, list[RoundResult]]:
    grouped: dict[int, list[RoundResult]] = {}
    for rr in round_results:
        grouped.setdefault(rr.round_number, []).append(rr)
    return grouped


def build_protocol_payload(state: SimulationState, options: ProtocolOptions | None = None) -> dict[str, Any]:
    """Build a structured conversation protocol from SimulationState.

    Notes:
    - Current implementation uses existing `round_results` ordering (append order).
    - If AP3 (Redebedarf-Scheduler) adds per-contribution scores later, this format
      can be extended without breaking consumers by adding optional fields.
    """
    options = options or ProtocolOptions()

    by_round = _group_round_results(state.round_results)
    rounds: list[dict[str, Any]] = []

    for round_number in sorted(by_round.keys()):
        contributions: list[dict[str, Any]] = []
        for rr in by_round[round_number]:
            for resp in rr.agent_responses:
                contributions.append(_agent_contribution(resp, rr.events, options))

        rounds.append(
            {
                "round_number": round_number,
                "contributions": contributions,
                "events": [_event_payload(e) for e in _events_for_round(state, round_number)],
            }
        )

    payload: dict[str, Any] = {
        "protocol_version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "run": {
            "name": state.config.name,
            "description": state.config.description,
            "rounds_completed": state.clock.current_round,
            "rounds_max": state.clock.max_rounds,
            "seed": state.config.seed,
        },
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.agent_type.value,
                "goals": a.goals,
                "constraints": a.constraints,
            }
            for a in state.agents
        ],
        "rounds": rounds,
        "final_environment": {
            fid: {
                "name": f.name,
                "current_state": f.current_state,
                "state_label": f.possible_states.get(f.current_state, f.current_state),
            }
            for fid, f in state.environment.factors.items()
        },
        "cib": state.cib_matrix.model_dump() if state.cib_matrix is not None else None,
    }
    return payload


def _events_for_round(state: SimulationState, round_number: int) -> list[EventLogEntry]:
    return [e for e in state.event_log if e.round_number == round_number]


def _event_payload(event: EventLogEntry) -> dict[str, Any]:
    return {
        "id": event.id,
        "round_number": event.round_number,
        "source_agent": event.source_agent,
        "event_type": event.event_type.value,
        "description": event.description,
        "affected_factors": event.affected_factors,
        "timestamp": event.timestamp,
    }


def _agent_contribution(
    resp: AgentResponse, events: list[EventLogEntry], options: ProtocolOptions
) -> dict[str, Any]:
    affected_factors: set[str] = set()
    for sc in resp.state_changes:
        affected_factors.add(sc.factor_id)
    for e in events:
        for fid in e.affected_factors:
            affected_factors.add(fid)

    payload: dict[str, Any] = {
        "agent_id": resp.agent_id,
        "round_number": resp.round_number,
        "why": _safe_first_line(resp.reasoning, fallback=""),
        "reasoning": resp.reasoning,
        "actions": resp.actions,
        "state_changes": [sc.model_dump() for sc in resp.state_changes],
        "events": [_event_payload(e) for e in events],
        "impact": {
            "affected_factors": sorted(affected_factors),
            "impact_assessment": resp.impact_assessment,
        },
        # Placeholder for AP3 (scheduler) integration
        "redebedarf_score": None,
        "segment_analysis": resp.segment_analysis if isinstance(resp.segment_analysis, dict) else {},
    }

    if options.include_raw_output:
        payload["raw_output"] = resp.raw_output

    return payload


def write_protocol_files(
    state: SimulationState,
    output_dir: str | Path,
    options: ProtocolOptions | None = None,
    json_filename: str = "protocol.json",
    md_filename: str = "protocol.md",
) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = build_protocol_payload(state, options=options)
    json_path = output_dir / json_filename
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = output_dir / md_filename
    md_path.write_text(render_protocol_markdown(payload), encoding="utf-8")

    return json_path, md_path


def render_protocol_markdown(payload: dict[str, Any]) -> str:
    run = payload.get("run", {})
    lines: list[str] = []
    lines.append(f"# Gesprächsprotokoll: {run.get('name', 'Simulation')}")
    if run.get("description"):
        lines.append("")
        lines.append(str(run["description"]).strip())

    lines.append("")
    lines.append("## Überblick")
    lines.append(f"- **Runden:** {run.get('rounds_completed')} / {run.get('rounds_max')}")
    if run.get("seed") is not None:
        lines.append(f"- **Seed:** {run.get('seed')}")

    lines.append("")
    lines.append("## Protokoll")
    for r in payload.get("rounds", []):
        round_number = r.get("round_number")
        lines.append("")
        lines.append(f"### Runde {round_number}")

        for contrib in r.get("contributions", []):
            agent_id = contrib.get("agent_id", "?")
            why = contrib.get("why", "")
            lines.append(f"- **{agent_id}:** {why}")

            impacted = contrib.get("impact", {}).get("affected_factors", [])
            if impacted:
                lines.append(f"  - impacted_factors: {', '.join(impacted)}")

            ia = contrib.get("impact", {}).get("impact_assessment", [])
            if isinstance(ia, list) and ia:
                lines.append("  - impact_assessment:")
                for item in ia[:8]:
                    if isinstance(item, dict):
                        s = json.dumps(item, ensure_ascii=False)
                        lines.append(f"    - {s}")

        events = r.get("events", [])
        if events:
            lines.append("")
            lines.append(f"**Events ({len(events)}):**")
            for e in events:
                lines.append(
                    f"- [{e.get('source_agent','?')}] {e.get('event_type','?')} :: {e.get('description','')}"
                )

    return "\n".join(lines) + "\n"

