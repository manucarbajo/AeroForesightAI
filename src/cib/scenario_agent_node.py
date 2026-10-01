from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.cib.scenario_consistency import ScenarioDeriver, scenarios_to_dict
from src.llm import LLMCallable, auf_deutsch
from src.models.cib_models import DESCRIPTOR_IDS, MAX_INFLUENCE, MIN_INFLUENCE, CIBMatrix
from src.models.llm_models import LLMIncident
from src.models.scenario_models import (
    ErzaehltesSzenario,
    ErzaehlteSzenarien,
    GerechnetesSzenario,
    GerechneteSzenarien,
)
from src.models.state_models import SimulationState

logger = logging.getLogger(__name__)


SCENARIO_SYSTEM_PROMPT = """Du bist ein Szenario-Analyst für Cross-Impact Balance (CIB) im Kontext Luftfahrt/Mobilität.

Du bekommst eine fertige CIB-Matrix (14x14; 7 Faktoren mit je 2 Deskriptoren F1.1/F1.2 ... F7.1/F7.2).

Ziel: Leite 2-3 konsistente, plausible Szenarien ab:
- jedes Szenario hat einen Titel und eine kurze Narrative (5-10 Sätze)
- nennt zentrale Treiber (Deskriptoren) und die wichtigsten Wechselwirkungen (mit -3..+3 Stärke)
- ist "intern konsistent": die ausgewählten Deskriptoren passen zueinander (starke Widersprüche vermeiden)

Wichtig:
- Keine langen Listen, Fokus auf die 6-10 wichtigsten Beziehungen.
- Keine Spekulation jenseits der gegebenen Faktoren/Deskriptoren.
"""


def _format_factor_context(state: SimulationState) -> str:
    lines: list[str] = []
    for factor in state.environment.factors.values():
        lines.append(f"### {factor.id}: {factor.name}")
        lines.append(f"Beschreibung: {factor.description}")
        for sid, desc in factor.possible_states.items():
            lines.append(f"- {sid}: {desc}")
        lines.append("")
    return "\n".join(lines).strip()


def _top_influences(matrix: CIBMatrix, limit: int = 40) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for cell in matrix.cells.values():
        if abs(cell.influence) >= 2:
            items.append(
                {
                    "source": cell.source_descriptor,
                    "target": cell.target_descriptor,
                    "influence": cell.influence,
                    "reasoning": cell.reasoning,
                }
            )
    items.sort(key=lambda x: abs(int(x.get("influence", 0))), reverse=True)
    return items[:limit]


def _build_consistent_scenarios(state: SimulationState) -> GerechneteSzenarien:
    """Die deterministisch abgeleiteten Kandidaten — **typisiert** (P1.3).

    Diese Funktion gab ihren Teil bis zum 2026-08-30 als rohes Dict unter dem
    Schlüssel `"scenarios"` zurück — demselben Namen, unter dem der Aufrufer
    danach das **LLM-Narrativ** ablegte. Derselbe Name für beide Seiten der
    Grenze, einmal innen, einmal außen.
    """

    if state.cib_matrix is None:
        return GerechneteSzenarien()

    deriver = ScenarioDeriver(state.cib_matrix)
    derived = deriver.derive_scenarios(top_n=3, allow_inconsistent=False)
    roh = scenarios_to_dict(derived)
    return GerechneteSzenarien(
        matrix_round=roh.get("matrix_round"),
        total_evaluated=int(roh.get("total_evaluated") or 0),
        consistent_count=int(roh.get("consistent_count") or 0),
        szenarien=[GerechnetesSzenario(**s) for s in roh.get("scenarios", [])],
    )


def _build_scenario_prompt(state: SimulationState, gerechnet: GerechneteSzenarien) -> str:
    if state.cib_matrix is None:
        raise ValueError("ScenarioAgentNode requires state.cib_matrix")

    matrix = state.cib_matrix
    factors = _format_factor_context(state)
    top = _top_influences(matrix, limit=48)
    top_json = json.dumps(top, ensure_ascii=False, indent=2)
    scores = matrix.factor_scores or []
    scores_json = json.dumps([s.model_dump() for s in scores], ensure_ascii=False, indent=2)
    consistent_json = json.dumps(gerechnet.model_dump(), ensure_ascii=False, indent=2)

    return f"""{SCENARIO_SYSTEM_PROMPT}

## Faktoren & Deskriptoren
{factors}

## Aktueller Simulationsstand
- round_generated: {matrix.round_generated}
- is_complete: {matrix.is_complete}
- total_cells: {len(matrix.cells)}

## Faktor-Scores (active/passive)
{scores_json}

## Stärkste Beziehungen (abs(influence) >= 2)
{top_json}

## Mathematisch konsistente Szenario-Kandidaten
{consistent_json}

## Output-Format (strict)
Antworte mit exakt einem JSON-Objekt ohne Markdown und ohne Codeblock:
{{
  "scenarios": [
    {{
      "id": "S1",
      "title": "string",
      "narrative": "string",
      "selected_descriptors": ["F1.1","F2.2"],
      "key_relationships": [
        {{"source": "F1.1", "target": "F2.2", "influence": 2, "why": "string"}}
      ],
      "implications": ["string"]
    }}
  ]
}}
Regeln:
- 2 bis 3 Szenarien
- narrative: 5-10 Sätze
- selected_descriptors: 7 Einträge (genau einer pro Faktor F1..F7; jeweils .1 oder .2)
- key_relationships: 6-10 Einträge, influence -3..+3
- Nur JSON, kein weiterer Text.
"""


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).strip()
    # Steuerzeichen in Texten zulassen — derselbe Befund wie beim Abschlusstext
    # (P8-V5): ein echter Zeilenumbruch in einem JSON-Text verwarf die Antwort.
    decoder = json.JSONDecoder(strict=False)
    try:
        direct = decoder.decode(cleaned)
        if isinstance(direct, dict):
            return direct
    except json.JSONDecodeError:
        pass

    for idx, ch in enumerate(cleaned):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(cleaned[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _normalize_descriptor(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip()
    return v if v in DESCRIPTOR_IDS else None


def _normalize_selected_descriptors(selected: Any) -> list[str]:
    """Return exactly 7 descriptors (one per factor F1..F7)."""
    factor_choice: dict[str, str] = {}
    if isinstance(selected, list):
        for item in selected:
            desc = _normalize_descriptor(item)
            if desc is None:
                continue
            factor_id = desc.split(".")[0]
            # keep first occurrence per factor to remain stable
            factor_choice.setdefault(factor_id, desc)

    normalized: list[str] = []
    for i in range(1, 8):
        fid = f"F{i}"
        normalized.append(factor_choice.get(fid, f"{fid}.1"))
    return normalized


def _clamp_influence(value: Any) -> int:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 0
    return max(MIN_INFLUENCE, min(MAX_INFLUENCE, v))


def _normalize_key_relationships(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        src = _normalize_descriptor(item.get("source"))
        tgt = _normalize_descriptor(item.get("target"))
        if src is None or tgt is None:
            continue
        out.append(
            {
                "source": src,
                "target": tgt,
                # **`behaupteter_einfluss`, nicht `influence`** (P1.3): Der Wert
                # kommt aus dem Sprachmodell, nicht aus der Matrix. Unter dem
                # alten Namen stand er im selben Vokabular wie `CIBCell.influence`.
                "behaupteter_einfluss": _clamp_influence(item.get("influence")),
                "why": str(item.get("why", "")).strip(),
            }
        )
    # Keep 10 max (prompt rule)
    return out[:10]


def _normalize_scenarios(payload: dict[str, Any]) -> dict[str, Any]:
    scenarios_raw = payload.get("scenarios", [])
    if not isinstance(scenarios_raw, list):
        scenarios_raw = []

    scenarios: list[dict[str, Any]] = []
    for idx, s in enumerate(scenarios_raw[:3], start=1):
        if not isinstance(s, dict):
            continue
        scenario_id = str(s.get("id") or f"S{idx}").strip() or f"S{idx}"
        title = str(s.get("title", "")).strip()
        narrative = str(s.get("narrative", "")).strip()
        selected = _normalize_selected_descriptors(s.get("selected_descriptors"))
        rel = _normalize_key_relationships(s.get("key_relationships"))
        implications_raw = s.get("implications", [])
        implications: list[str] = []
        if isinstance(implications_raw, list):
            for imp in implications_raw:
                text = str(imp).strip()
                if text:
                    implications.append(text)

        scenarios.append(
            {
                "id": scenario_id,
                "title": title,
                "narrative": narrative,
                "selected_descriptors": selected,
                "key_relationships": rel,
                "implications": implications,
            }
        )

    # Ensure at least 2 scenarios if any exist (prompt rule). If LLM returns 1, duplicate skeleton.
    if len(scenarios) == 1:
        s = dict(scenarios[0])
        s["id"] = "S2"
        if not s.get("title"):
            s["title"] = "Alternativszenario (Fallback)"
        scenarios.append(s)

    return {"scenarios": scenarios}


class ScenarioAgentNode:
    def __init__(
        self, llm: LLMCallable, output_dir: Path | None = None, *, erzaehlen: bool = True
    ) -> None:
        """*erzaehlen* ``False``: nur die gerechneten Szenarien, kein Aufruf ans Modell.

        **Für «Nur Zahlen»** (`deterministic_only`, seit 2026-10-01). Bis dahin
        fragte dieser Knoten das Sprachmodell auch in einem reinen Zahlenlauf:
        Ohne Ollama wurde der Lauf als beeinträchtigt markiert, mit Ollama stand
        ein Modelltext unter `compute_mode: deterministic_only`.
        """

        self.llm = llm
        self.output_dir = output_dir
        self.erzaehlen = erzaehlen

    def invoke(self, state: SimulationState) -> SimulationState:
        if state.cib_matrix is None:
            return state

        gerechnet = _build_consistent_scenarios(state)
        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        # **Zwei Schlüssel, die sich nicht um ein Wort unterscheiden** (P1.3).
        # Vorher: `scenario_candidates` und `scenarios`.
        state.cib_matrix.metadata["gerechnete_szenarien"] = gerechnet.model_dump()
        if not self.erzaehlen:
            return state

        prompt = _build_scenario_prompt(state, gerechnet)
        try:
            raw = self.llm.call(auf_deutsch(prompt))
        except Exception as e:
            # Ohne Narrativ bleibt der deterministische Teil (`gerechnete_szenarien`)
            # stehen — der Lauf ist damit unvollständig, nicht falsch. Festhalten,
            # damit das Artefakt es sagt statt nur das Log.
            logger.warning(
                "Szenario-Narrativ konnte nicht erzeugt werden: %s. "
                "Die gerechneten Kandidaten bleiben erhalten, der Lauf wird als "
                "beeinträchtigt markiert.",
                e,
            )
            state.llm_incidents.append(
                LLMIncident(
                    tick=state.clock.current_tick,
                    caller="scenario_node",
                    kind="call_failed",
                    error=f"{type(e).__name__}: {e}",
                )
            )
            return state

        payload = _extract_json_object(raw)
        if payload is None:
            logger.warning("ScenarioAgentNode: failed to parse JSON output")
            return state

        erzaehlt = ErzaehlteSzenarien(
            szenarien=[ErzaehltesSzenario(**s) for s in _normalize_scenarios(payload)["scenarios"]]
        )
        payload = erzaehlt.model_dump()
        state.cib_matrix.metadata["erzaehlte_szenarien"] = payload

        # Optional file output
        if self.output_dir is not None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "scenarios.json"
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

            md_path = self.output_dir / "scenarios.md"
            md_path.write_text(render_scenarios_markdown(payload, state), encoding="utf-8")

        return state


def render_scenarios_markdown(payload: dict[str, Any], state: SimulationState) -> str:
    lines: list[str] = []
    lines.append(f"# Szenarien: {state.config.name}")
    if state.cib_matrix is not None:
        lines.append(f"- **CIB round_generated:** {state.cib_matrix.round_generated}")
        if state.cib_matrix.metadata:
            # Die gerechneten Kennzahlen stehen seit P1.3 typisiert in
            # `gerechnete_szenarien` statt in einem eigenen Metadaten-Schlüssel.
            gerechnet = state.cib_matrix.metadata.get("gerechnete_szenarien")
            if isinstance(gerechnet, dict) and gerechnet:
                lines.append(
                    f"- **Gerechnet:** {gerechnet.get('consistent_count', 0)} von "
                    f"{gerechnet.get('total_evaluated', 0)} Konstellationen konsistent"
                )
    lines.append("")
    # **Woher diese Konstellationen kommen** (P2.0-B). Sie stehen in einem
    # Lauf-Verzeichnis und sehen deshalb aus, als kämen sie aus dem Lauf. Sie
    # kommen aus der Matrix: `derive_scenarios` zählt alle 2^7 Kombinationen
    # durch und rankt sie nach ihrem Konsistenzwert — der Endzustand des Laufs
    # geht dabei an keiner Stelle ein. Wer das nicht weiß, liest hier ein
    # Ergebnis, wo eine Eigenschaft der Matrix steht.
    lines.append(
        "> Diese Konstellationen stammen aus der **Einflussmatrix**, nicht aus "
        "diesem Lauf: Es sind die bestbewerteten aller Kombinationen von F1–F7. "
        "Sie fallen deshalb für jeden Lauf gleich aus. Das Szenario-Tripleset "
        "*dieses* Laufs steht in `run_scenario.md`."
    )
    lines.append("")

    # **`szenarien`, nicht `scenarios`** (P1.3). Der Bericht las den alten
    # Schlüssel weiter und wäre leer geblieben — gefunden vom Test, nicht beim
    # Lesen des Codes.
    scenarios = payload.get("szenarien", [])
    if not isinstance(scenarios, list) or not scenarios:
        lines.append("_Keine Szenarien generiert._")
        return "\n".join(lines) + "\n"

    for s in scenarios:
        if not isinstance(s, dict):
            continue
        sid = s.get("id", "")
        title = s.get("title", "")
        lines.append(f"## {sid} – {title}".strip())
        narrative = str(s.get("narrative", "")).strip()
        if narrative:
            lines.append("")
            lines.append(narrative)
            lines.append("")

        selected = s.get("selected_descriptors", [])
        if isinstance(selected, list) and selected:
            lines.append(f"- **selected_descriptors:** {', '.join(str(x) for x in selected)}")

        rel = s.get("key_relationships", [])
        if isinstance(rel, list) and rel:
            # **Die Überschrift sagt, woher die Zahlen kommen** (P1.3). Vorher
            # stand hier «key_relationships» und darunter Werte, die neben den
            # Matrixwerten desselben Berichts nicht zu unterscheiden waren.
            lines.append(
                "- **Vom Sprachmodell behauptete Wirkbeziehungen** "
                "(erzählt, nicht aus der Matrix gerechnet):"
            )
            for item in rel:
                if isinstance(item, dict):
                    lines.append(
                        f"  - {item.get('source')} → {item.get('target')}: "
                        f"{item.get('behaupteter_einfluss')} (behauptet) "
                        f":: {item.get('why', '')}"
                    )

        implications = s.get("implications", [])
        if isinstance(implications, list) and implications:
            lines.append("- **implications:**")
            for imp in implications:
                lines.append(f"  - {str(imp).strip()}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
