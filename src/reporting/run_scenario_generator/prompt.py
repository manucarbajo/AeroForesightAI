"""LLM scenario prompt construction and grounding validation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.reporting import aussagen_pruefung
from src.reporting.run_scenario_generator.candidates import (
    KONSISTENZ_BEDEUTUNG,
    build_candidate_constellations,
)
from src.reporting.run_scenario_generator.context import (
    RunScenarioContext,
    _cib_score,
    _safe_float,
)
from src.reporting.run_scenario_generator.factors import (
    _load_factor_catalog,
    build_factor_profile,
    faktor_namen,
)

RUN_SCENARIO_MARKER = "RUN_SCENARIO_GENERATOR"


#: Die Vorlage für den Abschlusstext eines Laufs — **neben dem Code**, nicht im
#: Arbeitsverzeichnis gesucht. Modulkonstante, damit ein Test sie umbiegen kann.
VORLAGE = Path(__file__).resolve().parents[2] / "prompts" / "run_scenario.md"


def faktenblatt_saetze(
    context: RunScenarioContext, catalog: dict[str, Any] | None = None
) -> list[str]:
    """Das Faktenblatt dieses Laufs, mit den Faktorbezeichnungen aus dem Katalog (P8-V3)."""

    catalog = catalog if catalog is not None else _load_factor_catalog()
    return aussagen_pruefung.faktenblatt_saetze(
        context.run_dir, context.factors, faktor_namen(catalog)
    )


def build_scenario_prompt(context: RunScenarioContext) -> str:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    candidates = build_candidate_constellations(context, factor_profile, catalog)

    # Expose the candidate constellations the LLM may select from. The LLM picks
    # by candidate_id; factor states stay Python-owned (grounding/reproducibility).
    clean_candidates = []
    for sc in candidates:
        clean_candidates.append(
            {
                "candidate_id": sc.get("candidate_id"),
                "scenario_kind": sc.get("scenario_kind"),
                "consistency_score": sc.get("consistency_score"),
                "konsistenz_band": sc.get("konsistenz_band"),
                "factor_constellation": sc.get("factor_constellation"),
                "delta_from_end": sc.get("delta_from_end"),
                "tick_grounding": sc.get("tick_grounding"),
            }
        )

    payload = {
        # **Zuerst, und als Sätze** (P8-V3): Das Modell formuliert die Richtung
        # jeder Kerngröße, statt sie aus Zahlenreihen selbst zu deuten. Bis dahin
        # standen hier `booking_trend`/`price_trend` mit eigenen Schwellen neben
        # den Rohzahlen, und `llama3.2` las daraus eine steigende CO₂-Abgabe, wo
        # sie über 120 Ticks bei 50 EUR stand.
        "faktenblatt": faktenblatt_saetze(context, catalog),
        "run_id": context.run_id,
        "metadata": context.metadata,
        "summary_metrics": context.summary_metrics,
        "factor_profile": factor_profile,
        "phase_ticks": context.phase_ticks,
        "events_sample": context.event_log[-12:],
        "segment_booking_end": context.summary_metrics.get("segment_booking_end"),
        "cib_consistency_score": _cib_score(context),
        # Die Zahl reist nicht ohne ihre Lesart. Ohne diesen Satz hat das Modell
        # den Score als Wahrscheinlichkeit ausgedeutet — genau die Aussage, die
        # er nicht trägt (P2.0).
        "cib_consistency_bedeutung": KONSISTENZ_BEDEUTUNG,
        "candidate_scenarios": clean_candidates,
        "agent_digest": context.agent_digest,
    }

    # **Neben dem Code gesucht, und ohne stillen Rückfall** (2026-09-11). Bis
    # dahin stand hier `Path("src/prompts/run_scenario.md")` — relativ zum
    # Arbeitsverzeichnis. Lief der Prozess anderswo, fand er die Vorlage nicht und
    # nahm ohne jede Meldung einen Einzeiler: Das Sprachmodell bekam eine
    # verkümmerte Anweisung, und niemand erfuhr es. Seit P4.6 ist `src` von überall
    # importierbar, der Fall also erreichbar. Eine fehlende Vorlage scheitert jetzt
    # laut — `generate_run_scenario` fängt das ab, nimmt das Template und hält den
    # Vorfall fest (Invariante 1: ein Ausfall ist sichtbar).
    prompt_template = VORLAGE.read_text(encoding="utf-8")

    return f"{RUN_SCENARIO_MARKER}\n\nRUN CONTEXT (Ground Truth):\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```\n\n{prompt_template}\n"


#: Steuerzeichen in einem JSON-Text zulassen (P8-V5). `llama3.2` schreibt in lange
#: Texte wie `story` gelegentlich einen echten Zeilenumbruch statt `\n`; der
#: strenge Leser wies die ganze Antwort ab, und der Abschlusstext kam aus der
#: Vorlage — am 2026-09-30 bei drei von sechs Läufen des Vorführbestands.
_NACHSICHTIG = json.JSONDecoder(strict=False)


#: Was nach einem Backslash in einem JSON-Text stehen darf.
_GUELTIGE_ESCAPES = frozenset('"\\/bfnrtu')

#: Woran ein Szenario-Objekt zu erkennen ist, wenn das Modell es außerhalb von
#: `scenarios` schreibt.
_SZENARIO_MERKMALE = ("candidate_id", "story", "rank")


def _escapes_reparieren(text: str) -> str:
    """Ungültige Escape-Sequenzen lesbar machen (2026-10-02).

    `llama3.2` schrieb in einen langen Text einen Backslash direkt vor einen
    Zeilenumbruch — eine Fortsetzungszeile wie in Python, in JSON ungültig. Der
    Backslash vor einem Umbruch fällt weg; jeder andere ungültige wird verdoppelt
    und steht damit als Zeichen im Text. Gelesen wird **paarweise**, damit ein
    korrekt geschriebenes `\\\\` nicht als Anfang einer neuen Sequenz gilt.
    """

    def ersetzen(treffer: re.Match[str]) -> str:
        zeichen = treffer.group(1)
        if zeichen in _GUELTIGE_ESCAPES:
            return treffer.group(0)
        if zeichen in "\r\n":
            return zeichen
        return "\\\\" + zeichen

    return re.sub(r"\\(.)", ersetzen, text, flags=re.DOTALL)


def _bereinigen(text: str) -> str:
    return _escapes_reparieren(re.sub(r",\s*([\]}])", r"\1", text))


def _objekte(text: str) -> list[Any]:
    """Alle JSON-Objekte, die hintereinander im Text stehen — auch durch Kommas getrennt."""

    gefunden: list[Any] = []
    pos = text.find("{")
    while 0 <= pos < len(text):
        try:
            objekt, ende = _NACHSICHTIG.raw_decode(text, pos)
        except json.JSONDecodeError:
            break
        gefunden.append(objekt)
        pos = ende
        while pos < len(text) and text[pos] in " \t\r\n,":
            pos += 1
        if pos < len(text) and text[pos] != "{":
            break
    return gefunden


def _zusammensetzen(objekte: list[Any]) -> dict[str, Any] | None:
    """Ein Hauptobjekt, dem das Modell die Szenarien als eigene Objekte nachgeschoben hat.

    Gemessen am 2026-10-02: Eine von acht Antworten schloss das Objekt nach
    `summary` und schrieb die Szenarien danach als `{…}` `{…}` `{…}`. Was ein
    Szenario-Merkmal trägt, wird zu `scenarios`; andere Felder der folgenden
    Objekte werden übernommen, **wenn sie im Hauptobjekt fehlen** — nichts wird
    überschrieben, was das Modell schon gesagt hat.
    """

    if not objekte or not isinstance(objekte[0], dict):
        return None
    haupt = dict(objekte[0])
    if len(objekte) == 1 or haupt.get("scenarios"):
        return haupt
    szenarien = [
        o for o in objekte[1:] if isinstance(o, dict) and any(m in o for m in _SZENARIO_MERKMALE)
    ]
    for o in objekte[1:]:
        if isinstance(o, dict) and o not in szenarien:
            for schluessel, wert in o.items():
                haupt.setdefault(schluessel, wert)
    if szenarien:
        haupt["scenarios"] = szenarien
    return haupt


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Das JSON-Objekt einer Antwort — so nachsichtig, wie es ohne Raten geht.

    Nachsichtig sind vier Dinge, und jedes kommt aus einer gemessenen Antwort von
    `llama3.2`: echte Zeilenumbrüche in Texten (`_NACHSICHTIG`), ein Komma vor
    der schließenden Klammer, ungültige Escape-Sequenzen und Szenarien, die als
    eigene Objekte hinter dem Hauptobjekt stehen. Bei acht Aufrufen mit demselben
    Prompt waren am 2026-10-02 zwei unlesbar — eine aus jedem der beiden letzten
    Gründe —, und bei zwei Versuchen je Text fiel im Probelauf des Vorführbestands
    einer von sieben Abschlusstexten auf die Vorlage zurück.
    """

    text = text.strip()
    if not text:
        return None
    try:
        parsed = _NACHSICHTIG.decode(_bereinigen(text))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    anfang = text.find("{")
    if anfang < 0:
        return None
    return _zusammensetzen(_objekte(_bereinigen(text[anfang:])))


def _walk_numbers(obj: Any):
    if isinstance(obj, (int, float)):
        yield float(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _walk_numbers(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_numbers(item)


def _number_tokens(value: float) -> set[str]:
    tokens = {f"{value}", f"{value:.1f}", f"{value:.2f}", f"{value:.3f}", f"{value:.4f}"}
    if 0 < abs(value) < 1:
        tokens.add(f"{value:.1%}".replace("%", ""))
        tokens.add(f"{value * 100:.1f}")
    return tokens


def _allowed_number_tokens(context: RunScenarioContext) -> set[str]:
    allowed: set[str] = set()
    for value in _walk_numbers(context.summary_metrics):
        allowed.update(_number_tokens(value))
    for row in context.phase_ticks:
        for value in _walk_numbers(row):
            allowed.update(_number_tokens(value))
    for row in context.population_segments[-20:]:
        for key in ("booking_rate", "avg_income_factor"):
            value = _safe_float(row.get(key))
            if value is not None:
                allowed.update(_number_tokens(value))
    if context.metadata.get("ticks_completed") is not None:
        allowed.add(str(int(context.metadata["ticks_completed"])))
    for row in context.phase_ticks:
        if row.get("tick") is not None:
            allowed.add(str(int(row["tick"])))

    # Allow scenario ranks and CIB scores
    allowed.update({"1", "2", "3"})
    cib_score = _cib_score(context)
    if cib_score is not None:
        allowed.update(_number_tokens(cib_score))

    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    for sc in build_candidate_constellations(context, factor_profile, catalog):
        score = sc.get("consistency_score")
        if score is not None:
            allowed.update(_number_tokens(float(score)))

    return allowed


def validate_scenario_narrative(payload: dict[str, Any], context: RunScenarioContext) -> list[str]:
    allowed = _allowed_number_tokens(context)
    warnings: list[str] = []
    text_parts = [
        str(payload.get("summary", "")),
        str(payload.get("run_narrative", "")),
        str(payload.get("observed_run", "")),
        str(payload.get("starting_conditions", "")),
        str(payload.get("limitations", "")),
    ]
    for scenario in payload.get("scenarios") or []:
        if not isinstance(scenario, dict):
            continue
        text_parts.append(str(scenario.get("story", "")))
        text_parts.append(str(scenario.get("what_could_happen", "")))
    for item in payload.get("timeline") or []:
        if isinstance(item, dict):
            text_parts.append(str(item.get("narrative", "")))

    joined = " ".join(text_parts)
    for match in re.finditer(r"(?<!\w)(\d+[.,]\d+|\d+)(?!\w)", joined):
        token = match.group(1).replace(",", ".")
        if token in allowed:
            continue
        if re.search(rf"(?:Tick|tick)\s*{re.escape(token)}\b", joined):
            continue
        warnings.append(token)
    return warnings


def build_ground_truth_block(context: RunScenarioContext) -> dict[str, Any]:
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    block = dict(context.summary_metrics)
    block["run_id"] = context.run_id
    block["cib_consistency_score"] = _cib_score(context)
    block["factor_profile"] = factor_profile
    # Was das Sprachmodell als Rechnung bekommen hat, steht im Artefakt daneben —
    # wer den Text liest, kann ihn gegen dieselben Sätze halten (P8-V3).
    block["faktenblatt"] = faktenblatt_saetze(context, catalog)
    return block
