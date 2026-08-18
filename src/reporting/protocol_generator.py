from __future__ import annotations

import json
from collections import defaultdict
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
    include_redebedarf: bool = False


def _safe_first_line(text: str, fallback: str = "") -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return fallback
    return cleaned.splitlines()[0].strip()


def _descriptor_to_factor_id(descriptor: str | None) -> str | None:
    """Extract the factor id (e.g. F1) from a descriptor such as F1.2."""

    if not descriptor:
        return None

    candidate = str(descriptor).strip()
    if not candidate:
        return None

    factor_id = candidate.split("→", 1)[0].split("|")[-1].strip().split(".")[0]
    if factor_id.startswith("F") and factor_id[1:].isdigit():
        return factor_id
    return None


def _group_round_results(round_results: list[RoundResult]) -> dict[int, list[RoundResult]]:
    grouped: dict[int, list[RoundResult]] = {}
    for rr in round_results:
        grouped.setdefault(rr.round_number, []).append(rr)
    return grouped


def build_protocol_payload(
    state: SimulationState, options: ProtocolOptions | None = None
) -> dict[str, Any]:
    """Build a structured conversation protocol from SimulationState."""

    options = options or ProtocolOptions()
    redebedarf_by_contribution = (
        _resolve_redebedarf_by_contribution(state) if options.include_redebedarf else {}
    )

    by_round = _group_round_results(state.round_results)
    rounds: list[dict[str, Any]] = []

    for round_number in sorted(by_round.keys()):
        contributions: list[dict[str, Any]] = []
        contribution_index = 0
        for rr in by_round[round_number]:
            for resp in rr.agent_responses:
                redebedarf = redebedarf_by_contribution.get((round_number, contribution_index), {})
                contributions.append(
                    _agent_contribution(
                        resp,
                        rr.events,
                        options,
                        redebedarf_score=redebedarf.get("redebedarf_score"),
                        redebedarf_reasons=redebedarf.get("redebedarf_reasons", []),
                    )
                )
                contribution_index += 1

        rounds.append(
            {
                "round_number": round_number,
                "market": _market_snapshot_for_round(state, round_number),
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
            "ticks_completed": state.clock.current_tick,
            "ticks_max": state.clock.max_ticks,
            "tick_unit": state.clock.tick_unit,
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
        "system_properties": state.resolved_properties().model_dump(),
        "price_history": [entry.model_dump() for entry in state.price_history],
    }
    return payload


def _events_for_round(state: SimulationState, round_number: int) -> list[EventLogEntry]:
    return [e for e in state.event_log if e.round_number == round_number]


def _market_snapshot_for_round(state: SimulationState, round_number: int) -> dict[str, Any]:
    """Per-tick market data: deterministic demand_level (M2) and sampled booking_rate (M3)."""

    price_entry = next(
        (entry for entry in state.price_history if entry.round_number == round_number), None
    )
    pop_stat = next(
        (entry for entry in state.population_stats if entry.get("round_number") == round_number),
        None,
    )

    booking_rate = None
    if price_entry is not None and price_entry.booking_rate is not None:
        booking_rate = price_entry.booking_rate
    elif pop_stat is not None:
        booking_rate = pop_stat.get("total_demand")

    snapshot: dict[str, Any] = {
        "price": price_entry.price if price_entry is not None else None,
        "demand_level": price_entry.demand_level if price_entry is not None else None,
        "booking_rate": booking_rate,
    }
    return snapshot


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


def _resolve_redebedarf_by_contribution(
    state: SimulationState,
) -> dict[tuple[int, int], dict[str, Any]]:
    """Resolve per-contribution Redebedarf metadata from stored or replayed scores."""

    stored = _stored_redebedarf_by_contribution(state)
    if _all_contributions_have_redebedarf(state, stored):
        return stored
    return _replay_redebedarf_by_contribution(state)


def _stored_redebedarf_by_contribution(
    state: SimulationState,
) -> dict[tuple[int, int], dict[str, Any]]:
    stored: dict[tuple[int, int], dict[str, Any]] = {}
    by_round = _group_round_results(state.round_results)

    for round_number in sorted(by_round.keys()):
        contribution_index = 0
        for rr in by_round[round_number]:
            for resp in rr.agent_responses:
                if resp.redebedarf_score is not None:
                    stored[(round_number, contribution_index)] = {
                        "redebedarf_score": int(resp.redebedarf_score),
                        "redebedarf_reasons": list(resp.redebedarf_reasons or []),
                    }
                contribution_index += 1
    return stored


def _all_contributions_have_redebedarf(
    state: SimulationState,
    stored: dict[tuple[int, int], dict[str, Any]],
) -> bool:
    total_contributions = sum(len(rr.agent_responses) for rr in state.round_results)
    return total_contributions > 0 and len(stored) == total_contributions


def _replay_redebedarf_by_contribution(
    state: SimulationState,
) -> dict[tuple[int, int], dict[str, Any]]:
    """Replay AP3 scheduler logic to reconstruct per-contribution scores."""

    from src.agents._scheduling_helpers import initial_score_ledger as _initial_score_ledger
    from src.agents.redebedarf_scheduler import FactorChangeObservation, RedebedarfScheduler

    result: dict[tuple[int, int], dict[str, Any]] = {}
    by_round = _group_round_results(state.round_results)
    partial_round_results: list[RoundResult] = []
    end_of_round_scores: dict[str, int] = {}

    for round_number in sorted(by_round.keys()):
        partial_state = state.model_copy(deep=True)
        partial_state.round_results = list(partial_round_results)
        partial_state.redebedarf_scores = dict(end_of_round_scores)

        scheduler = RedebedarfScheduler.from_simulation_state(
            partial_state, apply_score_deltas=False
        )
        scheduler._score_by_agent = _initial_score_ledger(partial_state, scheduler, round_number)

        last_spoken: dict[str, int] = {}
        for rr in partial_round_results:
            for response in rr.agent_responses:
                last_spoken[response.agent_id] = max(
                    last_spoken.get(response.agent_id, 0),
                    rr.round_number,
                )
        scheduler._last_spoken_round = {
            agent_id: last_spoken.get(agent_id, 0) for agent_id in scheduler.agent_ids
        }
        scheduler.start_round(round_number)
        scheduler._contributions_this_round = {agent_id: 0 for agent_id in scheduler.agent_ids}

        contribution_index = 0
        for rr in by_round[round_number]:
            for resp in rr.agent_responses:
                score_at_speak = int(scheduler.snapshot_scores().get(resp.agent_id, 0))
                reasons_at_speak = list(scheduler.snapshot_reasons().get(resp.agent_id, ()))
                result[(round_number, contribution_index)] = {
                    "redebedarf_score": score_at_speak,
                    "redebedarf_reasons": reasons_at_speak,
                }

                observed_factor_ids = {change.factor_id for change in resp.state_changes}
                observed_factor_ids.update(
                    factor_id for event in rr.events for factor_id in event.affected_factors
                )
                for factor_id in sorted(observed_factor_ids):
                    scheduler.register_factor_change(
                        FactorChangeObservation(
                            factor_id=factor_id,
                            source_agent=resp.agent_id,
                        )
                    )
                scheduler.mark_spoken(resp.agent_id, round_number=round_number)
                contribution_index += 1

        end_of_round_scores = scheduler.snapshot_scores()
        partial_round_results.extend(by_round[round_number])

    return result


def _agent_contribution(
    resp: AgentResponse,
    events: list[EventLogEntry],
    options: ProtocolOptions,
    *,
    redebedarf_score: int | None = None,
    redebedarf_reasons: list[str] | None = None,
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
        },
        "redebedarf_score": redebedarf_score,
        "redebedarf_reasons": list(redebedarf_reasons or []),
        "segment_analysis": (
            resp.segment_analysis if isinstance(resp.segment_analysis, dict) else {}
        ),
    }

    if options.include_raw_output:
        payload["raw_output"] = resp.raw_output

    return payload


def collect_agent_factor_references(payload: dict[str, Any]) -> dict[str, set[str]]:
    """Collect factor references per agent from a structured protocol payload.

    The helper walks the real AP2 payload and extracts factors mentioned in
    state changes, events and impact summaries. This is used by AP3 to build
    deterministic speech-demand relevance relations from actual data instead of
    a static mock table.
    """

    references: dict[str, set[str]] = defaultdict(set)

    for agent in payload.get("agents", []):
        agent_id = agent.get("id")
        if isinstance(agent_id, str) and agent_id.strip():
            references[agent_id.strip()]  # ensure key exists

    for round_payload in payload.get("rounds", []):
        for contribution in round_payload.get("contributions", []):
            agent_id = contribution.get("agent_id")
            if not isinstance(agent_id, str) or not agent_id.strip():
                continue

            factor_ids = _collect_factor_ids_from_contribution(contribution)
            if factor_ids:
                references[agent_id.strip()].update(factor_ids)

    return {agent_id: set(sorted(factor_ids)) for agent_id, factor_ids in references.items()}


def collect_contradiction_signals(
    payload: dict[str, Any],
    *,
    cib_matrix: Any | None = None,
) -> list[dict[str, Any]]:
    """Detect deterministic contradiction signals from AP2 protocol data.

    Conflicting state changes for the same factor within one round.
    """

    signals: list[dict[str, Any]] = []

    for round_payload in payload.get("rounds", []):
        round_number = round_payload.get("round_number")
        if not isinstance(round_number, int):
            continue

        state_change_votes: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

        for contribution in round_payload.get("contributions", []):
            agent_id = contribution.get("agent_id")
            if not isinstance(agent_id, str) or not agent_id.strip():
                continue

            for change in contribution.get("state_changes", []):
                if not isinstance(change, dict):
                    continue
                factor_id = change.get("factor_id")
                proposed_state = change.get("proposed_state")
                if not isinstance(factor_id, str) or not isinstance(proposed_state, str):
                    continue
                factor_id = factor_id.strip()
                proposed_state = proposed_state.strip()
                if not factor_id or not proposed_state:
                    continue
                state_change_votes[factor_id][proposed_state].add(agent_id.strip())

        for factor_id, votes in state_change_votes.items():
            if len(votes) <= 1:
                continue
            majority_state = _deterministic_majority_state(votes)
            minority_agents = sorted(
                {
                    agent_id
                    for state, agents in votes.items()
                    if state != majority_state
                    for agent_id in agents
                }
            )
            if minority_agents:
                signals.append(
                    {
                        "round_number": round_number,
                        "agent_ids": minority_agents,
                        "factor_id": factor_id,
                        "kind": "state_change_conflict",
                        "reason": (
                            f"Konkurrierende Zustandsvorschläge für {factor_id}; Mehrheit: {majority_state}"
                        ),
                        "weight": 2,
                    }
                )

    return signals


def _collect_factor_ids_from_contribution(contribution: dict[str, Any]) -> set[str]:
    factor_ids: set[str] = set()

    for change in contribution.get("state_changes", []):
        if not isinstance(change, dict):
            continue
        factor_id = change.get("factor_id")
        if isinstance(factor_id, str) and factor_id.strip():
            factor_ids.add(factor_id.strip())

    impact = contribution.get("impact", {})
    if isinstance(impact, dict):
        for factor_id in impact.get("affected_factors", []):
            if isinstance(factor_id, str) and factor_id.strip():
                factor_ids.add(factor_id.strip())

    for event in contribution.get("events", []):
        if not isinstance(event, dict):
            continue
        for factor_id in event.get("affected_factors", []):
            if isinstance(factor_id, str) and factor_id.strip():
                factor_ids.add(factor_id.strip())

    return factor_ids


def _deterministic_majority_state(votes: dict[str, set[str]]) -> str:
    ranked = sorted(votes.items(), key=lambda item: (-len(item[1]), item[0]))
    return ranked[0][0]


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
    lines.append(f"- **Ticks:** {run.get('ticks_completed')} / {run.get('ticks_max')}")
    if run.get("seed") is not None:
        lines.append(f"- **Seed:** {run.get('seed')}")

    lines.append("")
    lines.append("## Protokoll")
    for r in payload.get("rounds", []):
        round_number = r.get("round_number")
        lines.append("")
        lines.append(f"### Tick {round_number}")

        market = r.get("market") or {}
        if market:
            price = market.get("price")
            demand_level = market.get("demand_level")
            booking_rate = market.get("booking_rate")
            market_parts: list[str] = []
            if price is not None:
                market_parts.append(f"price={price:.2f}")
            if demand_level is not None:
                market_parts.append(f"demand_level={demand_level:.3f}")
            if booking_rate is not None:
                market_parts.append(f"booking_rate={booking_rate:.1%}")
            if market_parts:
                lines.append(f"- **Markt:** {', '.join(market_parts)}")

        for contrib in r.get("contributions", []):
            agent_id = contrib.get("agent_id", "?")
            why = contrib.get("why", "")
            score = contrib.get("redebedarf_score")
            score_suffix = f" (Redebedarf={score})" if score is not None else ""
            lines.append(f"- **{agent_id}:** {why}{score_suffix}")

            reasons = contrib.get("redebedarf_reasons", [])
            if isinstance(reasons, list) and reasons:
                lines.append(
                    f"  - redebedarf_reasons: {', '.join(str(reason) for reason in reasons)}"
                )

            impacted = contrib.get("impact", {}).get("affected_factors", [])
            if impacted:
                lines.append(f"  - impacted_factors: {', '.join(impacted)}")

        events = r.get("events", [])
        if events:
            lines.append("")
            lines.append(f"**Events ({len(events)}):**")
            for e in events:
                lines.append(
                    f"- [{e.get('source_agent','?')}] {e.get('event_type','?')} :: {e.get('description','')}"
                )

    return "\n".join(lines) + "\n"
