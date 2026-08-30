"""Deterministic scenario-candidate constellations, CIB scoring, and LLM-selection mapping."""

from __future__ import annotations

from typing import Any

from src.reporting.run_scenario_generator.agent_digest import _agent_perspective_clause
from src.reporting.run_scenario_generator.context import (
    RunScenarioContext,
    _booking_trend,
)
from src.reporting.run_scenario_generator.factors import (
    FACTOR_IDS,
    _factor_state_label,
    _flip_state,
)
from src.reporting.run_scenario_generator.narrative import build_scenario_tick_grounding

SCENARIO_MIN_STORY_LEN = 200


def _slide_scenario_title(scenario_kind: str) -> str:
    if scenario_kind == "fortsetzung":
        return "Trend-Fortsetzung"
    if scenario_kind == "alternative":
        return "Alternativ-Szenario"
    if scenario_kind == "spannung":
        return "Spannungs-Szenario"
    return "Exploratives Szenario"


def _build_scenario_description(
    *,
    scenario_kind: str,
    slide_title: str,
    context: RunScenarioContext,
    catalog: dict[str, Any],
    states: dict[str, str],
    agent_digest: dict[str, Any] | None = None,
) -> str:
    """Sachliche Szenario-Beschreibung — aus Faktoren, Lauf und Agenten-Perspektiven."""
    agent_digest = agent_digest or context.agent_digest
    agent_clause = _agent_perspective_clause(agent_digest)
    f1 = _factor_state_label(catalog, "F1", states.get("F1", ""))
    f2 = _factor_state_label(catalog, "F2", states.get("F2", ""))
    f3 = _factor_state_label(catalog, "F3", states.get("F3", ""))
    f5 = _factor_state_label(catalog, "F5", states.get("F5", ""))
    f6 = _factor_state_label(catalog, "F6", states.get("F6", ""))
    booking = _booking_trend(context.summary_metrics)

    if scenario_kind == "fortsetzung":
        return (
            f"«{slide_title}»: Die im Lauf erreichte Faktorlage setzt sich fort "
            f"({f1}; {f2}). Nachfrage und Preis würden den im Lauf {booking}en Trend "
            f"plausibel fortsetzen. {f3} und {f5} bleiben Rahmenbedingungen. {f6} prägt "
            f"die gesellschaftliche Akzeptanz von Flugreisen.{agent_clause}"
        )

    if scenario_kind == "alternative":
        return (
            f"«{slide_title}»: Gegenüber der Lauf-Endlage weicht mindestens ein Faktor ab "
            f"(siehe oben). Typisch: Verschiebungen bei {f1} und {f2}. {f5} und {f6} "
            f"können Modal Shift verstärken oder dämpfen. Explorative Konstellation, keine Prognose."
            f"{agent_clause}"
        )

    return (
        f"«{slide_title}»: Widersprüchliche Faktortrends ({f1} vs. {f2}). "
        f"Anpassungsdruck auf Politik, Anbieter und Nachfrage. {f6} kann Spannungen verstärken."
        f"{agent_clause}"
    )


def _build_constellation_scenario(
    *,
    rank: int,
    scenario_kind: str,
    states: dict[str, str],
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    slide_title = _slide_scenario_title(scenario_kind)
    title = slide_title

    tick_grounding = build_scenario_tick_grounding(context, factor_profile, catalog, states)
    story = _build_scenario_description(
        scenario_kind=scenario_kind,
        slide_title=slide_title,
        context=context,
        catalog=catalog,
        states=states,
    )

    return {
        "rank": rank,
        "id": f"S{rank}",
        "title": title,
        "scenario_kind": scenario_kind,
        "factor_constellation": dict(states),
        "tick_grounding": tick_grounding,
        "story": story,
        "what_could_happen": story,
    }


def _pick_alternative_constellation(
    end_states: dict[str, str], transitions: list[dict[str, Any]]
) -> dict[str, str]:
    states = dict(end_states)
    if transitions:
        pivot = transitions[0]["factor_id"]
        states[pivot] = _flip_state(str(states.get(pivot, "")))
        return states
    for pivot in ("F6", "F3", "F5", "F4"):
        if pivot in states:
            states[pivot] = _flip_state(str(states[pivot]))
            return states
    return states


def _pick_tension_constellation(end_states: dict[str, str]) -> dict[str, str]:
    states = dict(end_states)
    f1 = str(states.get("F1", "F1.1"))
    f2 = str(states.get("F2", "F2.1"))
    if f1.endswith(".1") and f2.endswith(".1"):
        states["F2"] = _flip_state(f2)
    elif f1.endswith(".2") and f2.endswith(".2"):
        states["F1"] = _flip_state(f1)
    else:
        states["F1"] = "F1.1"
        states["F2"] = "F2.2"
    return states


def build_explorative_scenarios(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    end_states = dict(factor_profile.get("end_by_id") or {})
    if not end_states:
        end_states = {f"F{i}": f"F{i}.1" for i in range(1, 8)}

    transitions = factor_profile.get("transitions") or []
    continuation = _build_constellation_scenario(
        rank=1,
        scenario_kind="fortsetzung",
        states=end_states,
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    alternative = _build_constellation_scenario(
        rank=2,
        scenario_kind="alternative",
        states=_pick_alternative_constellation(end_states, transitions),
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    tension = _build_constellation_scenario(
        rank=3,
        scenario_kind="spannung",
        states=_pick_tension_constellation(end_states),
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )

    scenarios = [continuation, alternative, tension]
    _score_constellations(context, scenarios)
    return scenarios


#: Was der CIB-Score über eine Konstellation aussagen darf — ein Satz, der mit
#: dem Artefakt mitreist. Der State Explorer und das Sprachmodell lesen die
#: Datei ohne diese Doku daneben; ohne den Satz stünde die Zahl nackt da und
#: würde wieder als Wahrscheinlichkeit gelesen.
KONSISTENZ_BEDEUTUNG = (
    "Der CIB-Score misst Widerspruchsfreiheit, nicht Wahrscheinlichkeit: Er ist hoch, "
    "wenn alle Faktoren einheitlich gepolt sind, und niedrig bei gemischten Lagen. "
    "Eine gemischte Konstellation ist deshalb nicht unwahrscheinlicher — strenge "
    "Regulierung bei starker Nachfrage ist die reale europäische Lage und bekommt "
    "hier trotzdem einen niedrigen Wert."
)


def _konsistenz_band(score: float | None) -> str | None:
    """Den CIB-Score in ein Band übersetzen, das sagt, was er misst.

    **Hieß bis P2.0 `_plausibility_from_score` und lieferte hoch/mittel/niedrig.**
    Das war eine Wertung, die der Score nicht trägt: Am 2026-08-29 nachgemessen
    misst er **Polarität, nicht Plausibilität** — über alle 128 Systemzustände
    korreliert er mit +0,56 und monoton mit der Zahl gleichpolig gesetzter
    Faktoren (`tests/test_cib_einachsigkeit.py`). Das Etikett «hoch» lag damit
    ausgerechnet auf der Welt, in der sich nichts widerspricht, weil sich nichts
    bewegt, und «niedrig» auf der realen europäischen Mischlage.

    Die Bänder benennen jetzt die gemessene Größe. Ohne Score gibt es **kein**
    Band — die frühere Fassung fiel auf den Präsentationsrang zurück und machte
    damit aus einer Reihenfolge eine Aussage über die Welt.
    """

    if score is None:
        return None
    if score >= 0.7:
        return "widerspruchsfrei"
    if score >= 0.4:
        return "gemischt"
    return "spannungsreich"


def _score_constellations(
    context: RunScenarioContext,
    scenarios: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach the CIB consistency_score and its band in place."""
    if isinstance(context.cib_matrix, dict):
        try:
            from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
            from src.models.cib_models import CIBMatrix

            matrix_obj = CIBMatrix.model_validate(context.cib_matrix)
            checker = ConsistencyChecker(matrix_obj)
            for sc in scenarios:
                desc = ScenarioDescriptor(factor_states=sc["factor_constellation"])
                sc["consistency_score"] = round(checker.compute_consistency_score(desc), 3)
        except Exception:
            for sc in scenarios:
                sc["consistency_score"] = None
    else:
        for sc in scenarios:
            sc["consistency_score"] = None

    for sc in scenarios:
        sc["konsistenz_band"] = _konsistenz_band(sc.get("consistency_score"))
        sc["konsistenz_bedeutung"] = KONSISTENZ_BEDEUTUNG
    return scenarios


def _delta_from_end(end_states: dict[str, str], states: dict[str, str]) -> list[str]:
    """Human-readable factor differences of a constellation vs. the run end state."""
    diffs: list[str] = []
    for factor_id in FACTOR_IDS:
        target = states.get(factor_id)
        base = end_states.get(factor_id)
        if target and base and target != base:
            diffs.append(f"{factor_id} {base}→{target}")
    return diffs


def build_candidate_constellations(
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Deterministic set of CIB-scored future constellations for LLM *selection*.

    Python derives every candidate (continuation, single-factor alternatives,
    cross-impact tension) from the run end state and scores each with the CIB
    matrix. The LLM later selects and justifies three of them — it never invents
    factor states, which keeps the scenario space reproducible and grounded.
    """
    end_states = dict(factor_profile.get("end_by_id") or {})
    if not end_states:
        end_states = {f"F{i}": f"F{i}.1" for i in range(1, 8)}

    transitions = factor_profile.get("transitions") or []
    raw: list[tuple[str, dict[str, str]]] = [("fortsetzung", dict(end_states))]

    pivots: list[str] = []
    for item in transitions:
        fid = str(item.get("factor_id") or "")
        if fid and fid not in pivots:
            pivots.append(fid)
    for fid in ("F1", "F2", "F3", "F5", "F6"):
        if fid not in pivots:
            pivots.append(fid)
    for fid in pivots:
        if fid not in end_states:
            continue
        alt = dict(end_states)
        alt[fid] = _flip_state(str(alt[fid]))
        raw.append(("alternative", alt))

    raw.append(("spannung", _pick_tension_constellation(end_states)))

    seen: set[frozenset] = set()
    candidates: list[dict[str, Any]] = []
    for kind, states in raw:
        key = frozenset(states.items())
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            {
                "scenario_kind": kind,
                "factor_constellation": dict(states),
                "tick_grounding": build_scenario_tick_grounding(
                    context, factor_profile, catalog, states
                ),
                "delta_from_end": _delta_from_end(end_states, states),
            }
        )

    _score_constellations(context, candidates)

    def _sort_key(item: dict[str, Any]) -> tuple[int, float]:
        kind_rank = 0 if item.get("scenario_kind") == "fortsetzung" else 1
        score = item.get("consistency_score")
        score = float(score) if isinstance(score, (int, float)) else -1.0
        return (kind_rank, -score)

    candidates.sort(key=_sort_key)
    candidates = candidates[:7]
    for index, item in enumerate(candidates, start=1):
        item["candidate_id"] = f"C{index}"
    return candidates


def _fallback_story_for_candidate(
    candidate: dict[str, Any],
    *,
    context: RunScenarioContext,
    catalog: dict[str, Any],
) -> str:
    """Deterministic story used when the LLM story is missing or too thin."""
    return _build_scenario_description(
        scenario_kind=candidate.get("scenario_kind", "explorativ"),
        slide_title=_slide_scenario_title(candidate.get("scenario_kind", "")),
        context=context,
        catalog=catalog,
        states=candidate.get("factor_constellation", {}),
    )


def _normalize_scenarios(
    raw: Any,
    *,
    context: RunScenarioContext,
    factor_profile: dict[str, Any],
    catalog: dict[str, Any],
) -> list[dict[str, Any]]:
    """Map the LLM's candidate *selection* back to Python-owned constellations.

    The LLM only contributes title + story and chooses which candidate to use
    via ``candidate_id``. Factor states, CIB score and tick grounding are taken
    verbatim from the deterministic candidate so nothing numeric is invented.
    """
    candidates = build_candidate_constellations(context, factor_profile, catalog)
    candidates_by_id = {c["candidate_id"]: c for c in candidates}
    canonical = build_explorative_scenarios(context, factor_profile, catalog)

    selected: list[dict[str, Any]] = []
    used_keys: set[frozenset] = set()

    if isinstance(raw, list):
        for index, item in enumerate(raw):
            if len(selected) >= 3 or not isinstance(item, dict):
                continue
            cand_id = str(item.get("candidate_id") or "").strip().upper()
            candidate = candidates_by_id.get(cand_id)
            if candidate is None and index < len(candidates):
                candidate = candidates[index]
            if candidate is None:
                continue
            key = frozenset(candidate["factor_constellation"].items())
            if key in used_keys:
                continue
            used_keys.add(key)

            story = str(
                item.get("story") or item.get("what_could_happen") or item.get("narrative") or ""
            ).strip()
            if len(story) < SCENARIO_MIN_STORY_LEN:
                story = _fallback_story_for_candidate(candidate, context=context, catalog=catalog)

            scenario_kind = candidate.get("scenario_kind", "explorativ")
            selected.append(
                {
                    "title": str(item.get("title") or _slide_scenario_title(scenario_kind)),
                    "scenario_kind": scenario_kind,
                    "consistency_score": candidate.get("consistency_score"),
                    "factor_constellation": dict(candidate.get("factor_constellation", {})),
                    "tick_grounding": candidate.get("tick_grounding", ""),
                    "candidate_id": candidate.get("candidate_id"),
                    "story": story,
                    "what_could_happen": story,
                }
            )

    # Guarantee three distinct paths: fill from the canonical fortsetzung/
    # alternative/spannung defaults if the LLM selected fewer.
    if len(selected) < 3:
        for fallback in canonical:
            key = frozenset((fallback.get("factor_constellation") or {}).items())
            if key in used_keys:
                continue
            used_keys.add(key)
            selected.append(dict(fallback))
            if len(selected) >= 3:
                break

    selected = selected[:3]
    for index, item in enumerate(selected, start=1):
        item["rank"] = index
        item["id"] = f"S{index}"
        item["konsistenz_band"] = _konsistenz_band(item.get("consistency_score"))
        item["konsistenz_bedeutung"] = KONSISTENZ_BEDEUTUNG
    return selected
