"""Deterministic speech-demand scheduler for AP3.

The scheduler is intentionally not round-robin. It scores agents on a 0-10 scale
based on factor relevance, contradictions, and stagnation. When an agent speaks,
its score resets to 0. The scheduler supports multiple contributions per round as
long as a speaker crosses the threshold again and stays below the per-round cap.

This version is wired to real AP1/AP2 data:
- factor relevance comes from the checked-in agent/factor metadata and, when available,
  the live CIB matrix and protocol references,
- contradictions come from actual protocol conflicts instead of a mock table.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from src.config_loader import load_agents, load_factors
from src.models.agent_models import AgentConfig
from src.models.cib_models import CIBMatrix
from src.models.state_models import FactorState, SimulationState
from src.protocol_generator import (
    build_protocol_payload,
    collect_agent_factor_references,
    collect_contradiction_signals,
)

DEFAULT_THRESHOLD = 3
DEFAULT_MAX_SCORE = 10
DEFAULT_MAX_CONTRIBUTIONS_PER_AGENT = 3


@dataclass(frozen=True)
class FactorChangeObservation:
    """Observed factor change used to trigger speech demand."""

    factor_id: str
    source_agent: str | None = None
    target_agent_ids: tuple[str, ...] | None = None
    weight: int | None = None


@dataclass(frozen=True)
class SpeechCandidate:
    """A single scheduler candidate with a deterministic score and reasons."""

    agent_id: str
    score: int
    reasons: tuple[str, ...] = field(default_factory=tuple)
    contributions_this_round: int = 0


class RedebedarfScheduler:
    """Score-based speech scheduler with deterministic ordering."""

    def __init__(
        self,
        agent_ids: Sequence[str],
        *,
        factor_relevance_map: Mapping[str, Mapping[str, int]] | None = None,
        threshold: int = DEFAULT_THRESHOLD,
        max_score: int = DEFAULT_MAX_SCORE,
        max_contributions_per_agent: int = DEFAULT_MAX_CONTRIBUTIONS_PER_AGENT,
    ) -> None:
        self.agent_ids = tuple(sorted({str(agent_id) for agent_id in agent_ids}))
        base_map = factor_relevance_map or self._build_workspace_default_factor_relevance_map(
            self.agent_ids
        )
        self.factor_relevance_map = self._normalize_factor_relevance_map(base_map)
        self.threshold = max(3, threshold)
        self.max_score = max_score
        self.max_contributions_per_agent = max(1, min(3, max_contributions_per_agent))

        self._current_round = 0
        self._score_by_agent: dict[str, int] = {agent_id: 0 for agent_id in self.agent_ids}
        self._reasons_by_agent: dict[str, list[str]] = {agent_id: [] for agent_id in self.agent_ids}
        self._contributions_this_round: dict[str, int] = {
            agent_id: 0 for agent_id in self.agent_ids
        }
        self._last_spoken_round: dict[str, int] = {agent_id: 0 for agent_id in self.agent_ids}
        self._agents_by_factor: dict[str, tuple[str, ...]] = self._build_reverse_index(
            self.factor_relevance_map
        )
        self._agent_factor_refs: dict[str, set[str]] = self._build_agent_factor_refs(
            self.factor_relevance_map
        )

    @classmethod
    def from_simulation_state(
        cls,
        state: SimulationState,
        *,
        apply_score_deltas: bool = True,
    ) -> RedebedarfScheduler:
        """Create a scheduler from the live simulation state."""

        scheduler = cls([agent.id for agent in state.agents])
        scheduler.prime_from_state(state, apply_score_deltas=apply_score_deltas)
        return scheduler

    @property
    def current_round(self) -> int:
        return self._current_round

    def prime_from_state(self, state: SimulationState, *, apply_score_deltas: bool = True) -> None:
        """Refresh relevance and contradiction context from a live state."""

        protocol_payload = build_protocol_payload(state)
        self.ingest_protocol_payload(
            protocol_payload,
            cib_matrix=state.cib_matrix,
            apply_score_deltas=apply_score_deltas,
        )

        merged = self._merge_relevance_maps(
            self.factor_relevance_map,
            self._infer_relevance_from_state(state),
        )
        self.factor_relevance_map = self._normalize_factor_relevance_map(merged)
        self._agents_by_factor = self._build_reverse_index(self.factor_relevance_map)
        self._agent_factor_refs = self._build_agent_factor_refs(self.factor_relevance_map)

    def start_round(self, round_number: int) -> None:
        """Start a new round and apply stagnation points deterministically."""

        if round_number < 1:
            raise ValueError("round_number must be >= 1")
        if round_number < self._current_round:
            raise ValueError("round_number cannot move backwards")

        self._current_round = round_number
        for agent_id in self.agent_ids:
            self._contributions_this_round[agent_id] = 0
            silent_rounds = max(0, round_number - self._last_spoken_round[agent_id] - 1)
            if silent_rounds:
                self._add_score(agent_id, silent_rounds, f"Stillstand +{silent_rounds}")

    def register_factor_change(self, observation: FactorChangeObservation) -> None:
        """Apply factor relevance points for a single observed factor change."""

        targets = self._resolve_targets(observation)
        if not targets:
            return

        relevance_weight = observation.weight
        for agent_id in targets:
            if observation.source_agent is not None and observation.source_agent == agent_id:
                continue
            weight = (
                relevance_weight
                if relevance_weight is not None
                else self._default_weight(
                    observation.factor_id,
                    agent_id,
                )
            )
            if weight <= 0:
                continue
            self._add_score(agent_id, weight, f"Faktor-Relevanz {observation.factor_id} +{weight}")

    def register_contradiction(
        self,
        agent_id: str,
        *,
        factor_id: str | None = None,
        reason: str = "Widerspruch +2",
    ) -> None:
        """Apply the contradiction trigger to a specific agent."""

        if agent_id not in self._score_by_agent:
            return

        suffix = f" ({factor_id})" if factor_id else ""
        self._add_score(agent_id, 2, f"{reason}{suffix}")

    def ingest_protocol_payload(
        self,
        payload: dict[str, Any],
        *,
        cib_matrix: CIBMatrix | None = None,
        apply_score_deltas: bool = True,
    ) -> None:
        """Update the scheduler from a protocol payload."""

        protocol_refs = collect_agent_factor_references(payload)
        if protocol_refs:
            self._merge_agent_factor_refs(protocol_refs)
            relevance_from_protocol = self._build_relevance_from_protocol_refs(
                protocol_refs, cib_matrix
            )
            self.factor_relevance_map = self._normalize_factor_relevance_map(
                self._merge_relevance_maps(self.factor_relevance_map, relevance_from_protocol)
            )
            self._agents_by_factor = self._build_reverse_index(self.factor_relevance_map)
            self._agent_factor_refs = self._build_agent_factor_refs(self.factor_relevance_map)

        if not apply_score_deltas:
            return

        for signal in collect_contradiction_signals(payload, cib_matrix=cib_matrix):
            agent_ids = signal.get("agent_ids", [])
            factor_id = signal.get("factor_id")
            reason = str(signal.get("reason", "Widerspruch +2")).strip() or "Widerspruch +2"
            for agent_id in agent_ids:
                if isinstance(agent_id, str) and agent_id.strip():
                    self.register_contradiction(
                        agent_id.strip(),
                        factor_id=factor_id if isinstance(factor_id, str) else None,
                        reason=reason,
                    )

        for source_agent_id, target_agent_id, weight, reason in self._build_direct_mention_signals(
            payload
        ):
            if source_agent_id == target_agent_id:
                continue
            self._add_score(target_agent_id, weight, reason)

    def build_speech_candidates(self) -> list[SpeechCandidate]:
        """Return the speaking queue in deterministic order."""

        candidates = [
            SpeechCandidate(
                agent_id=agent_id,
                score=score,
                reasons=tuple(self._reasons_by_agent[agent_id]),
                contributions_this_round=self._contributions_this_round[agent_id],
            )
            for agent_id, score in self._score_by_agent.items()
            if score >= self.threshold
            and self._contributions_this_round[agent_id] < self.max_contributions_per_agent
        ]
        return sorted(candidates, key=lambda candidate: (-candidate.score, candidate.agent_id))

    def next_speaker(self) -> SpeechCandidate | None:
        """Return the highest-ranked speaker candidate or None if nobody is eligible."""

        candidates = self.build_speech_candidates()
        return candidates[0] if candidates else None

    def mark_spoken(
        self,
        agent_id: str,
        *,
        round_number: int | None = None,
        count_contribution: bool = True,
    ) -> None:
        """Reset an agent's score after speaking and count the contribution."""

        if agent_id not in self._score_by_agent:
            return

        self._score_by_agent[agent_id] = 0
        self._reasons_by_agent[agent_id] = []
        if count_contribution:
            self._contributions_this_round[agent_id] += 1
        self._last_spoken_round[agent_id] = round_number or self._current_round

    def schedule_round(
        self,
        round_number: int,
        *,
        factor_changes: Sequence[FactorChangeObservation] | None = None,
        contradictions: Sequence[str] | None = None,
        protocol_payload: dict[str, Any] | None = None,
        cib_matrix: CIBMatrix | None = None,
    ) -> list[SpeechCandidate]:
        """Convenience API that scores a round and returns the speaking order."""

        self.start_round(round_number)
        for observation in factor_changes or []:
            self.register_factor_change(observation)
        for agent_id in contradictions or []:
            self.register_contradiction(agent_id)
        if protocol_payload is not None:
            self.ingest_protocol_payload(protocol_payload, cib_matrix=cib_matrix)
        return self.build_speech_candidates()

    def snapshot_scores(self) -> dict[str, int]:
        """Return a copy of the current score map."""

        return dict(self._score_by_agent)

    def snapshot_reasons(self) -> dict[str, tuple[str, ...]]:
        """Return the current trigger reasons for each agent."""

        return {agent_id: tuple(reasons) for agent_id, reasons in self._reasons_by_agent.items()}

    def _resolve_targets(self, observation: FactorChangeObservation) -> tuple[str, ...]:
        if observation.target_agent_ids is not None:
            return tuple(
                sorted(
                    {
                        agent_id
                        for agent_id in observation.target_agent_ids
                        if agent_id in self._score_by_agent
                    }
                )
            )

        direct_refs = self._agents_by_factor.get(observation.factor_id, ())
        if direct_refs:
            return direct_refs

        relevance = self.factor_relevance_map.get(observation.factor_id, {})
        return tuple(sorted(agent_id for agent_id in relevance if agent_id in self._score_by_agent))

    def _default_weight(self, factor_id: str, agent_id: str) -> int:
        weight = self.factor_relevance_map.get(factor_id, {}).get(agent_id, 0)
        if weight <= 0:
            return 0
        return max(2, min(3, weight))

    def _add_score(self, agent_id: str, delta: int, reason: str) -> None:
        if agent_id not in self._score_by_agent or delta <= 0:
            return

        new_score = max(0, min(self.max_score, self._score_by_agent[agent_id] + delta))
        self._score_by_agent[agent_id] = new_score
        self._reasons_by_agent[agent_id].append(reason)

    @staticmethod
    def _flatten_protocol_contribution_text(contribution: Mapping[str, Any]) -> str:
        parts: list[str] = []
        for key in ("why", "reasoning", "actions"):
            value = contribution.get(key)
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(str(item) for item in value if str(item).strip())

        for change in contribution.get("state_changes", []):
            if isinstance(change, Mapping):
                parts.extend(
                    str(change.get(field, ""))
                    for field in ("factor_id", "proposed_state", "reason")
                )

        for event in contribution.get("events", []):
            if isinstance(event, Mapping):
                parts.extend(str(event.get(field, "")) for field in ("event_type", "description"))

        return " ".join(part for part in parts if part).lower()

    def _build_direct_mention_signals(
        self,
        payload: dict[str, Any],
    ) -> list[tuple[str, str, int, str]]:
        agents = payload.get("agents", [])
        agent_names: dict[str, str] = {}
        for agent in agents:
            if not isinstance(agent, Mapping):
                continue
            agent_id = str(agent.get("id", "")).strip()
            if not agent_id:
                continue
            agent_names[agent_id] = str(agent.get("name", agent_id)).strip().lower()

        signals: list[tuple[str, str, int, str]] = []
        for round_payload in payload.get("rounds", []):
            if not isinstance(round_payload, Mapping):
                continue
            contributions = round_payload.get("contributions", [])
            if not isinstance(contributions, list):
                continue
            for contribution in contributions:
                if not isinstance(contribution, Mapping):
                    continue
                source_agent_id = str(contribution.get("agent_id", "")).strip()
                if not source_agent_id:
                    continue
                text = self._flatten_protocol_contribution_text(contribution)
                if not text:
                    continue
                for target_agent_id, target_name in agent_names.items():
                    if target_agent_id == source_agent_id:
                        continue
                    if target_agent_id.lower() in text or (target_name and target_name in text):
                        weight = 2 if target_agent_id in text or target_name in text else 1
                        signals.append(
                            (
                                source_agent_id,
                                target_agent_id,
                                weight,
                                f"Direkte Nennung {target_agent_id} +{weight}",
                            )
                        )
        return signals

    @classmethod
    def _build_workspace_default_factor_relevance_map(
        cls,
        agent_ids: Sequence[str],
    ) -> dict[str, dict[str, int]]:
        """Infer a deterministic baseline relevance map from actual repo data."""

        try:
            agents = load_agents()
            factors = load_factors()
        except Exception:
            return {}

        wanted_agents = set(agent_ids)
        agent_lookup = {agent.id: agent for agent in agents if agent.id in wanted_agents}
        if not agent_lookup:
            return {}

        base_map: dict[str, dict[str, int]] = defaultdict(dict)
        factor_text_index = {
            factor_id: cls._factor_text(factor) for factor_id, factor in factors.items()
        }
        for agent_id, agent in agent_lookup.items():
            agent_text = cls._agent_text(agent)
            for factor_id, factor_text in factor_text_index.items():
                score = cls._text_overlap_score(agent_text, factor_text, factor_id)
                if score <= 0:
                    continue
                base_map[factor_id][agent_id] = 3 if score >= 3 else 2

        return dict(base_map)

    @classmethod
    def _infer_relevance_from_state(cls, state: SimulationState) -> dict[str, dict[str, int]]:
        """Infer relevance from live AP1/AP2 state using current data."""

        base_map: dict[str, dict[str, int]] = defaultdict(dict)
        factor_text_index = {
            factor_id: cls._factor_text(factor)
            for factor_id, factor in state.environment.factors.items()
        }
        for agent in state.agents:
            agent_text = cls._agent_text(agent)
            for factor_id, factor_text in factor_text_index.items():
                score = cls._text_overlap_score(agent_text, factor_text, factor_id)
                if score <= 0:
                    continue
                base_map[factor_id][agent.id] = 3 if score >= 3 else 2

        return dict(base_map)

    @classmethod
    def _build_relevance_from_protocol_refs(
        cls,
        protocol_refs: dict[str, set[str]],
        cib_matrix: CIBMatrix | None,
    ) -> dict[str, dict[str, int]]:
        """Convert AP2 factor references into weighted factor relevance."""

        if not protocol_refs:
            return {}

        centrality = cls._factor_centrality_ranking(cib_matrix)
        relevance: dict[str, dict[str, int]] = defaultdict(dict)
        for agent_id, factor_ids in protocol_refs.items():
            for factor_id in factor_ids:
                if not factor_id:
                    continue
                weight = 2
                if centrality.get(factor_id, 0) > 0:
                    weight = 3
                relevance[factor_id][agent_id] = max(relevance[factor_id].get(agent_id, 0), weight)
        return dict(relevance)

    @classmethod
    def _factor_centrality_ranking(cls, cib_matrix: CIBMatrix | None) -> dict[str, int]:
        if cib_matrix is None:
            return {}

        if not cib_matrix.factor_scores:
            cib_matrix.compute_factor_scores()

        ranked = sorted(
            cib_matrix.factor_scores,
            key=lambda score: (-(score.active_score + score.passive_score), score.factor_id),
        )
        if not ranked:
            return {}

        top_cutoff = max(1, len(ranked) // 3)
        return {
            factor_score.factor_id: (1 if index < top_cutoff else 0)
            for index, factor_score in enumerate(ranked)
        }

    @staticmethod
    def _build_reverse_index(
        factor_relevance_map: Mapping[str, Mapping[str, int]],
    ) -> dict[str, tuple[str, ...]]:
        by_factor: dict[str, list[str]] = defaultdict(list)
        for factor_id, agent_weights in factor_relevance_map.items():
            for agent_id, weight in agent_weights.items():
                if weight > 0:
                    by_factor[factor_id].append(agent_id)
        return {factor_id: tuple(sorted(agent_ids)) for factor_id, agent_ids in by_factor.items()}

    @staticmethod
    def _build_agent_factor_refs(
        factor_relevance_map: Mapping[str, Mapping[str, int]],
    ) -> dict[str, set[str]]:
        refs: dict[str, set[str]] = defaultdict(set)
        for factor_id, agent_weights in factor_relevance_map.items():
            for agent_id, weight in agent_weights.items():
                if weight > 0:
                    refs[agent_id].add(factor_id)
        return {agent_id: set(sorted(factor_ids)) for agent_id, factor_ids in refs.items()}

    @staticmethod
    def _normalize_factor_relevance_map(
        factor_relevance_map: Mapping[str, Mapping[str, int]],
    ) -> dict[str, dict[str, int]]:
        normalized: dict[str, dict[str, int]] = {}
        for factor_id, agent_weights in factor_relevance_map.items():
            cleaned: dict[str, int] = {}
            for agent_id, weight in agent_weights.items():
                if weight <= 0:
                    continue
                cleaned[str(agent_id)] = max(2, min(3, int(weight)))
            if cleaned:
                normalized[str(factor_id)] = dict(sorted(cleaned.items(), key=lambda item: item[0]))
        return normalized

    @staticmethod
    def _merge_relevance_maps(*maps: Mapping[str, Mapping[str, int]]) -> dict[str, dict[str, int]]:
        merged: dict[str, dict[str, int]] = defaultdict(dict)
        for mapping in maps:
            for factor_id, agent_weights in mapping.items():
                for agent_id, weight in agent_weights.items():
                    if weight <= 0:
                        continue
                    merged[str(factor_id)][str(agent_id)] = max(
                        merged[str(factor_id)].get(str(agent_id), 0),
                        int(weight),
                    )
        return dict(merged)

    def _merge_agent_factor_refs(self, references: Mapping[str, set[str]]) -> None:
        for agent_id, factor_ids in references.items():
            self._agent_factor_refs.setdefault(agent_id, set()).update(factor_ids)

    @staticmethod
    def _agent_text(agent: AgentConfig) -> str:
        return " ".join(
            [
                agent.id,
                agent.name,
                agent.description,
                " ".join(agent.goals),
                " ".join(agent.constraints),
                getattr(agent.agent_type, "value", str(agent.agent_type)),
            ]
        ).lower()

    @staticmethod
    def _factor_text(factor: FactorState) -> str:
        return " ".join(
            [
                factor.id,
                factor.name,
                factor.description,
                factor.current_state,
                " ".join(factor.possible_states.values()),
            ]
        ).lower()

    @staticmethod
    def _text_overlap_score(agent_text: str, factor_text: str, factor_id: str) -> int:
        agent_tokens = set(re.findall(r"[a-z0-9äöüß]+", agent_text.lower()))
        factor_tokens = set(re.findall(r"[a-z0-9äöüß]+", factor_text.lower()))
        overlap = len(agent_tokens & factor_tokens)
        direct_match = 2 if factor_id.lower() in agent_text.lower() else 0
        return overlap + direct_match
