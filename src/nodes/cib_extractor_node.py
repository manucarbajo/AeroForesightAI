"""LLM-based CIB matrix extractor node.

Evaluates cross-impact influences between factor descriptors using an LLM.
Enforces delta constraint (max ±1 per cell per round) for iterative updates.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from src.models.cib_models import (
    CIBCell,
    CIBMatrix,
    CIBMatrixHistory,
    DESCRIPTOR_IDS,
    FACTOR_IDS,
    apply_delta_constraint,
)
from src.models.state_models import SimulationState

logger = logging.getLogger(__name__)


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str: ...


# Pairs to evaluate: all cross-factor descriptor combinations
def _build_evaluation_pairs() -> list[tuple[str, str]]:
    pairs = []
    for src in DESCRIPTOR_IDS:
        for tgt in DESCRIPTOR_IDS:
            if src.split(".")[0] != tgt.split(".")[0]:
                pairs.append((src, tgt))
    return pairs


EVALUATION_PAIRS = _build_evaluation_pairs()

CIB_SYSTEM_PROMPT = """Du bist ein Experte für Cross-Impact Balance (CIB) Analyse im Bereich Luftfahrt und Mobilität.

Deine Aufgabe: Bewerte die Wechselwirkungen zwischen Einflussfaktor-Deskriptoren.

Skala:
- +3: Stark fördernd (Deskriptor A macht B sehr viel wahrscheinlicher)
- +2: Fördernd
- +1: Leicht fördernd
- 0: Kein Einfluss
- -1: Leicht hemmend
- -2: Hemmend
- -3: Stark hemmend (Deskriptor A macht B sehr unwahrscheinlich)

Frage: "Wenn Deskriptor A eintritt, wie beeinflusst das die Wahrscheinlichkeit von Deskriptor B?"
"""


def _build_cib_prompt(
    state: SimulationState,
    pairs_batch: list[tuple[str, str]],
    previous_matrix: CIBMatrix | None = None,
) -> str:
    """Build the LLM prompt for CIB evaluation."""
    factors_context = _format_factors_context(state)
    events_context = _format_events_context(state)
    previous_context = _format_previous_matrix(previous_matrix, pairs_batch)

    pairs_text = "\n".join(
        f"- {src} → {tgt}" for src, tgt in pairs_batch
    )

    prompt = f"""{CIB_SYSTEM_PROMPT}

## Einflussfaktoren

{factors_context}

## Aktuelle Simulationsrunde: {state.clock.current_round}

## Relevante Events dieser Runde

{events_context}

{previous_context}

## Zu bewertende Paare

{pairs_text}

## Antwort-Format

Antworte ausschließlich als JSON-Array. Jedes Element:
{{"source": "<Deskriptor-ID>", "target": "<Deskriptor-ID>", "influence": <int -3 bis +3>, "reasoning": "<kurze Begründung>"}}

Beispiel:
[
  {{"source": "F1.1", "target": "F2.1", "influence": 2, "reasoning": "Reiseboom erzeugt Druck für moderate Regulierung"}},
  {{"source": "F1.1", "target": "F2.2", "influence": -1, "reasoning": "Boom macht radikale Verbote politisch schwierig"}}
]

Bewerte ALLE {len(pairs_batch)} Paare. Nur JSON, kein weiterer Text."""

    return prompt


def _format_factors_context(state: SimulationState) -> str:
    lines = []
    for factor in state.environment.factors.values():
        lines.append(f"### {factor.id}: {factor.name}")
        lines.append(f"Beschreibung: {factor.description}")
        lines.append(f"Aktueller Zustand: {factor.current_state}")
        for sid, desc in factor.possible_states.items():
            lines.append(f"  - {sid}: {desc}")
        lines.append("")
    return "\n".join(lines)


def _format_events_context(state: SimulationState) -> str:
    current_round = state.clock.current_round
    round_events = [e for e in state.event_log if e.round_number == current_round]

    if not round_events:
        return "Keine Events in dieser Runde."

    lines = []
    for event in round_events[-10:]:
        factors = ", ".join(event.affected_factors) if event.affected_factors else "-"
        lines.append(f"- [{event.source_agent}] {event.description} (Faktoren: {factors})")
    return "\n".join(lines)


def _format_previous_matrix(
    previous: CIBMatrix | None,
    pairs_batch: list[tuple[str, str]],
) -> str:
    if previous is None:
        return ""

    lines = ["## Bisherige Bewertungen (letzte Runde)", ""]
    for src, tgt in pairs_batch:
        cell = previous.get_cell(src, tgt)
        if cell and cell.influence != 0:
            lines.append(f"- {src} → {tgt}: {cell.influence:+d}")

    if len(lines) <= 2:
        return ""
    return "\n".join(lines)


def _parse_cib_response(raw_output: str) -> list[dict[str, Any]]:
    """Parse the LLM JSON response into a list of cell evaluations."""
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).strip()

    # Try direct parse
    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in output
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(cleaned[start:end + 1])
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    logger.warning("Failed to parse CIB LLM response")
    return []


class CIBExtractorNode:
    """Extracts and updates the CIB matrix using LLM-based evaluation.

    Per round, the LLM evaluates cross-impact influences between all
    descriptor pairs. Delta constraint (max ±1) is enforced for rounds > 1.
    """

    BATCH_SIZE = 42  # evaluate 42 pairs per LLM call (fits context well)

    def __init__(self, llm: LLMCallable | None = None) -> None:
        self.llm = llm
        self._history = CIBMatrixHistory()

    def invoke(self, state: SimulationState) -> SimulationState:
        if self.llm is None:
            return self._invoke_heuristic(state)

        previous = self._history.latest
        proposed = self._evaluate_with_llm(state, previous)

        if previous is not None and proposed is not None:
            final = apply_delta_constraint(previous, proposed)
        elif proposed is not None:
            final = proposed
        else:
            # LLM failed completely — keep previous or create empty
            final = previous or CIBMatrix.empty(state.clock.current_round)

        final.compute_factor_scores()
        self._history.add(final)
        state.cib_matrix = final
        return state

    def _evaluate_with_llm(
        self, state: SimulationState, previous: CIBMatrix | None
    ) -> CIBMatrix | None:
        """Run LLM evaluation in batches and assemble the full matrix."""
        all_cells: dict[str, CIBCell] = {}

        for batch_start in range(0, len(EVALUATION_PAIRS), self.BATCH_SIZE):
            batch = EVALUATION_PAIRS[batch_start:batch_start + self.BATCH_SIZE]
            prompt = _build_cib_prompt(state, batch, previous)

            try:
                raw_output = self.llm.call(prompt)
            except Exception as e:
                logger.error(f"LLM call failed for CIB batch: {e}")
                continue

            evaluations = _parse_cib_response(raw_output)
            for item in evaluations:
                src = str(item.get("source", "")).strip()
                tgt = str(item.get("target", "")).strip()
                influence = item.get("influence", 0)
                reasoning = str(item.get("reasoning", "")).strip()

                if src not in DESCRIPTOR_IDS or tgt not in DESCRIPTOR_IDS:
                    continue
                if not isinstance(influence, int):
                    try:
                        influence = int(influence)
                    except (ValueError, TypeError):
                        continue

                influence = max(-3, min(3, influence))
                cell = CIBCell(
                    source_descriptor=src,
                    target_descriptor=tgt,
                    influence=influence,
                    reasoning=reasoning,
                )
                all_cells[CIBMatrix.cell_key(src, tgt)] = cell

        if not all_cells:
            return None

        return CIBMatrix(
            cells=all_cells,
            round_generated=state.clock.current_round,
            metadata={
                "total_events": len(state.event_log),
                "cells_evaluated": len(all_cells),
                "evaluation_method": "llm",
            },
        )

    def _invoke_heuristic(self, state: SimulationState) -> SimulationState:
        """Fallback: heuristic-based extraction (C2 logic) when no LLM available."""
        from src.models.cib_models import CIBEntry

        pair_scores: dict[tuple[str, str], list[float]] = {}
        pair_reasoning: dict[tuple[str, str], str] = {}

        agent_weight = {
            "regulator": 1.0,
            "provider": 0.75,
            "consumer": 0.5,
            "market": 0.25,
        }

        for event in state.event_log:
            if len(event.affected_factors) < 2:
                continue

            weight = agent_weight.get(event.source_agent, 0.5)
            factors = event.affected_factors

            for i in range(len(factors)):
                for j in range(len(factors)):
                    if i == j:
                        continue
                    source = factors[i]
                    target = factors[j]
                    if source not in state.environment.factors:
                        continue
                    if target not in state.environment.factors:
                        continue

                    pair = (source, target)
                    if pair not in pair_scores:
                        pair_scores[pair] = []
                        pair_reasoning[pair] = event.description
                    pair_scores[pair].append(weight)

        entries: list[CIBEntry] = []
        for (source, target), scores in pair_scores.items():
            avg_score = sum(scores) / len(scores)
            entries.append(
                CIBEntry(
                    source_factor=source,
                    target_factor=target,
                    influence_score=round(avg_score, 3),
                    reasoning=pair_reasoning[(source, target)],
                )
            )

        entries.sort(key=lambda e: e.influence_score, reverse=True)

        state.cib_matrix = CIBMatrix(
            entries=entries,
            round_generated=state.clock.current_round,
            metadata={
                "total_events": len(state.event_log),
                "total_entries": len(entries),
                "rounds": state.clock.current_round,
                "evaluation_method": "heuristic",
            },
        )
        return state