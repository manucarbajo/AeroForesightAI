"""End-to-end scenario generation: load context, prompt/parse, render, persist."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.llm import LLMCallable, MockLLM, auf_deutsch
from src.models.llm_models import LLMIncident
from src.reporting.aussagen_pruefung import laufzeilen, widersprueche
from src.reporting.run_scenario_generator.candidates import _normalize_scenarios
from src.reporting.run_scenario_generator.context import load_run_scenario_context
from src.reporting.run_scenario_generator.factors import _load_factor_catalog, build_factor_profile
from src.reporting.run_scenario_generator.prompt import (
    _extract_json_object,
    build_ground_truth_block,
    build_scenario_prompt,
    validate_scenario_narrative,
)
from src.reporting.run_scenario_generator.rendering import (
    build_template_scenario,
    render_run_scenario_markdown,
)

logger = logging.getLogger(__name__)


def generate_run_scenario(
    run_id: str,
    llm: LLMCallable | None = None,
    *,
    run_dir: Path | None = None,
    prefer_llm: bool = True,
) -> dict[str, Any]:
    context = load_run_scenario_context(run_id, run_dir=run_dir)
    catalog = _load_factor_catalog()
    factor_profile = build_factor_profile(context, catalog)
    ground_truth = build_ground_truth_block(context)

    narrative: dict[str, Any] | None = None
    grounding_warnings: list[str] = []
    llm_error: str | None = None
    llm_fehlerart = "call_failed"

    # **Ein Platzhalter ist kein Sprachmodell** (P8-V5): Ein Lauf «Ohne
    # Sprachmodell» gibt `MockLLM` weiter, dessen Antwort nie ein Abschlusstext
    # ist. Seit eine verworfene Antwort ein Vorfall ist, machte das jeden
    # bewussten Lauf ohne Modell zu einem beeinträchtigten — genau das, was
    # Invariante 1 ausschließt. Er bekommt die Vorlage, ohne gefragt zu werden.
    if prefer_llm and llm is not None and not isinstance(llm, MockLLM):
        # Fällt der Aufruf aus, greift weiter unten `build_template_scenario` —
        # ein deterministisches Narrativ ohne Sprachmodell. Ohne dieses `except`
        # riss der Ausfall den ganzen Lauf mit, und zwar *nachdem* er gerechnet
        # war: es gäbe dann kein `run_metadata.json`, keinen Warnbanner, keinen
        # Lauf in der Liste — die Degradation wäre unsichtbar, weil gar nichts
        # ankommt. Der Fehler geht als `llm_error` an den Aufrufer zurück, der
        # ihn als Vorfall protokolliert.
        prompt = build_scenario_prompt(context)
        parsed: dict[str, Any] | None = None
        # **Eine unbrauchbare Antwort bekommt einen zweiten Versuch** (P8-V5). Die
        # Antworten von `llama3.2` streuen: Beim Vorführbestand kam auch nach dem
        # nachsichtigen Lesen einer von sechs Texten als «kein lesbares
        # JSON-Objekt» zurück, während zwölf direkte Aufrufe mit demselben Prompt
        # gelangen. Ein gescheiterter **Aufruf** wird hier nicht wiederholt — das
        # tut der Client schon, mit Backoff.
        for versuch in range(1, VERSUCHE + 1):
            try:
                raw = llm.call(auf_deutsch(prompt))
            except Exception as exc:  # noqa: BLE001 - jeder Backend-Fehler endet im Template
                logger.warning(
                    "Lauf-Szenario konnte nicht vom Sprachmodell erzeugt werden: %s. "
                    "Es wird das deterministische Template verwendet.",
                    exc,
                )
                llm_error = f"{type(exc).__name__}: {exc}"
                break
            parsed = _extract_json_object(raw)
            if _brauchbar(parsed):
                break
            logger.warning(
                "Lauf-Szenario: Antwort %d von %d nicht verwertbar (%s).",
                versuch,
                VERSUCHE,
                _warum_unbrauchbar(parsed),
            )
        if parsed is not None and _brauchbar(parsed):
            scenarios_raw = parsed["scenarios"]
            parsed["factor_profile"] = factor_profile
            parsed["agent_digest"] = context.agent_digest
            if not parsed.get("run_narrative"):
                parsed["run_narrative"] = parsed.get("observed_run", "")
            parsed["observed_run"] = parsed.get("run_narrative", "")
            parsed["scenarios"] = _normalize_scenarios(
                scenarios_raw,
                context=context,
                factor_profile=factor_profile,
                catalog=catalog,
            )
            grounding_warnings = validate_scenario_narrative(parsed, context)
            narrative = parsed
            narrative["source"] = "llm"
            if grounding_warnings:
                narrative["grounding_warnings"] = grounding_warnings
        elif llm_error is None:
            # **Geantwortet, aber nicht verwertbar** (P8-V5). Bis dahin sprang hier
            # die Vorlage ein, ohne dass es irgendwo stand — Invariante 1 verlangt,
            # dass ein Ausfall sichtbar ist, und eine verworfene Antwort ist einer.
            llm_error = f"Antwort nicht verwertbar: {_warum_unbrauchbar(parsed)}"
            llm_fehlerart = "answer_unusable"
            logger.warning("Lauf-Szenario: %s. Es wird die Vorlage verwendet.", llm_error)

    if narrative is None:
        narrative = build_template_scenario(context)
    else:
        narrative.setdefault("agent_digest", context.agent_digest)
        if len(str(narrative.get("summary") or "")) < 200:
            template = build_template_scenario(context)
            narrative["summary"] = template["summary"]
        # Was der Text über den Lauf sagt, gegen die Rechnung gehalten (P8-V3):
        # markiert wie eine unbelegte Zahl, nicht zurückgewiesen. **Nach** dem
        # Ersetzen einer zu kurzen Zusammenfassung — sonst stünde ein Befund zu
        # einem Satz da, den niemand mehr sieht.
        widerspruch = widersprueche(narrative, laufzeilen(context.run_dir))
        if widerspruch:
            narrative["widersprueche"] = widerspruch

    scenarios = narrative.get("scenarios") or _normalize_scenarios(
        [],
        context=context,
        factor_profile=factor_profile,
        catalog=catalog,
    )
    markdown = render_run_scenario_markdown(
        narrative,
        ground_truth,
        agent_digest=context.agent_digest,
    )
    return {
        "run_id": context.run_id,
        "title": narrative.get("title", ""),
        "summary": narrative.get("summary", ""),
        "scenarios": scenarios,
        "source": narrative.get("source", "template"),
        "grounding_warnings": grounding_warnings,
        "widersprueche": narrative.get("widersprueche", []),
        "llm_error": llm_error,
        "llm_fehlerart": llm_fehlerart if llm_error else None,
        "agent_digest": context.agent_digest,
        "narrative": narrative,
        "ground_truth": ground_truth,
        "markdown": markdown,
    }


#: Wie oft der Abschlusstext erfragt wird, bevor die Vorlage einspringt.
VERSUCHE = 2


def _brauchbar(parsed: dict[str, Any] | None) -> bool:
    """Ob sich aus der Antwort ein Abschlusstext bauen lässt: Titel, Laufverlauf, zwei Szenarien."""

    szenarien = parsed.get("scenarios") if isinstance(parsed, dict) else None
    return bool(
        isinstance(parsed, dict)
        and parsed.get("title")
        and (parsed.get("run_narrative") or parsed.get("observed_run"))
        and isinstance(szenarien, list)
        and len(szenarien) >= 2
    )


def _warum_unbrauchbar(parsed: dict[str, Any] | None) -> str:
    """Warum eine Antwort des Modells nicht übernommen wurde — für den Vorfall."""

    if not isinstance(parsed, dict):
        return "kein lesbares JSON-Objekt"
    fehlt = [
        name
        for name, da in (
            ("title", parsed.get("title")),
            ("run_narrative", parsed.get("run_narrative") or parsed.get("observed_run")),
        )
        if not da
    ]
    if fehlt:
        return "es fehlt " + ", ".join(fehlt)
    return "weniger als zwei Szenarien"


def szenario_vorfall(ergebnis: dict[str, Any], tick: int) -> LLMIncident | None:
    """Der Vorfall zu einem Abschlusstext, der nicht vom Modell stammt — oder keiner.

    **Eine Stelle für beide Startpfade** (Einzellauf und Szenario-Vergleich). Bis
    P8-V5 baute jeder seinen Vorfall selbst, beide mit `call_failed` — eine
    verworfene Antwort kam darin nicht vor.
    """

    fehler = ergebnis.get("llm_error")
    if not fehler:
        return None
    return LLMIncident(
        tick=tick,
        caller="run_scenario_generator",
        kind=ergebnis.get("llm_fehlerart") or "call_failed",
        error=str(fehler),
    )


def save_run_scenario_artifacts(
    run_dir: Path | str,
    result: dict[str, Any],
) -> tuple[Path, Path]:
    directory = Path(run_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "run_scenario.json"
    md_path = directory / "run_scenario.md"

    json_payload = {
        "run_id": result.get("run_id"),
        "title": result.get("title"),
        "summary": result.get("summary"),
        "selection_reasoning": (result.get("narrative") or {}).get("selection_reasoning"),
        "run_narrative": (result.get("narrative") or {}).get("run_narrative"),
        "factor_profile": (result.get("narrative") or {}).get("factor_profile")
        or result.get("ground_truth", {}).get("factor_profile"),
        "scenarios": result.get("scenarios") or (result.get("narrative") or {}).get("scenarios"),
        "source": result.get("source"),
        "grounding_warnings": result.get("grounding_warnings", []),
        "widersprueche": result.get("widersprueche", []),
        "agent_digest": result.get("agent_digest")
        or (result.get("narrative") or {}).get("agent_digest"),
        "narrative": result.get("narrative"),
        "ground_truth": result.get("ground_truth"),
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(str(result.get("markdown", "")), encoding="utf-8")
    return md_path, json_path


def generate_and_save_run_scenario(
    run_id: str,
    llm: LLMCallable | None = None,
    *,
    run_dir: Path | None = None,
    prefer_llm: bool = True,
) -> dict[str, Any]:
    from src.reporting.state_explorer import resolve_run_dir

    directory = run_dir or resolve_run_dir(run_id)
    result = generate_run_scenario(
        run_id,
        llm,
        run_dir=directory,
        prefer_llm=prefer_llm,
    )
    md_path, json_path = save_run_scenario_artifacts(directory, result)
    result["paths"] = {"markdown": str(md_path), "json": str(json_path)}
    return result
