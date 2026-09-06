"""Der CLI-Einstieg der Simulation — **und die geteilte Schnittstelle darum** (P3.6).

Dieses Modul ist zwei Dinge, und bis zum 2026-09-05 gab es nur für das erste
einen Namen: Es ist der Batch-Einstieg (`python -m src.run_simulation`), **und**
es hält, was jeder Startpfad nach einem Lauf tut — Artefakte schreiben,
Lauf-Argumente normalisieren, eine Mehrfachlauf-Zusammenfassung ablegen.

`dashboard/run_launcher.py` braucht genau dieses zweite und importierte dafür
drei **unterstrichs-präfixierte** Namen: `_build_run_args`, `_save_run_outputs`,
`_write_multi_run_summary`. Ein Unterstrich sagt «privat, kann sich jederzeit
ändern» — ein Refactor hätte den Launcher stumm gebrochen, und niemand hätte es
vor dem nächsten Dashboard-Lauf gemerkt.

**Was öffentlich ist, steht in `__all__`:**

* :func:`main` — der Einstieg, den `__main__` ruft.
* :func:`build_run_args` — die Lauf-Argumente eines Teillaufs.
* :func:`save_run_outputs` — alle Artefakte eines fertigen Laufs.
* :func:`write_multi_run_summary` — die Zusammenfassung über mehrere Läufe.
* :data:`EXIT_KONFIGURATION` — der Exit-Code für eine Konfiguration, die
  keinen Lauf zulässt (P3.3).

Alles andere hier ist Innenleben des CLI-Ablaufs und trägt weiter einen
Unterstrich. Wer aus `dashboard/` etwas davon braucht, hebt es hierher — nicht
den Import.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.cib.scenario_agent_node import ScenarioAgentNode, render_scenarios_markdown
from src.config_loader import build_initial_state
from src.llm import STUDIO_DIR, MockLLM, OllamaClient, OllamaConfig, load_env
from src.llm.defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
)
from src.logging_setup import configure_logging, stdio_auf_utf8
from src.models.llm_models import LLMIncident
from src.models.run_models import RunArgs, run_args_from
from src.models.state_models import LLMConfig, Rahmenszenario
from src.orchestration.checkpoint_manager import CheckpointManager, CheckpointVersionError
from src.orchestration.simulation_runner import MultiRunResult, RunnerOptions, SimulationRunner
from src.reporting.output_writer import (
    create_run_id,
    resolve_run_output_dir,
    save_age_property_csv,
    save_cib_matrix,
    save_event_log,
    save_factors_timeseries,
    save_final_narrative,
    save_llm_incidents,
    save_population_individuals,
    save_population_timeseries,
    save_price_history,
    save_properties_timeseries,
    save_protocol,
    save_protocol_markdown,
    save_round_history,
    save_run_metadata,
    save_scenarios,
    save_scenarios_markdown,
    save_segment_analysis,
    save_tick_mechanics,
)
from src.reporting.protocol_generator import (
    ProtocolOptions,
    build_protocol_payload,
    render_protocol_markdown,
)
from src.reporting.run_scenario_generator import generate_and_save_run_scenario
from src.validation import ValidationError, validate_llm_settings

#: Die öffentliche Schnittstelle dieses Moduls (P3.6). Was nicht hier steht,
#: ist Innenleben des CLI-Ablaufs — `dashboard/` importiert es nicht.
__all__ = [
    "main",
    "build_run_args",
    "save_run_outputs",
    "write_multi_run_summary",
    "EXIT_KONFIGURATION",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AeroForesight simulation.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model name, default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Ollama base URL, default: {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--temperature", type=float, default=DEFAULT_TEMPERATURE, help="LLM temperature"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Max tokens per response"
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=None,
        help="Override max ticks (uses configs/simulation_config.json by default).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of independent runs to execute.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional base seed used for deterministic multi-run sequencing.",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume from a checkpoint file path or run id.",
    )
    parser.add_argument(
        "--studio",
        action="store_true",
        help="Start LangGraph Studio (interactive UI) instead of a batch simulation run.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Optional run id for outputs/<run_id>/ (default: run_<UTC timestamp>).",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=None,
        help="Directory for checkpoints (default: outputs/<run_id>/checkpoints).",
    )
    parser.add_argument(
        "--no-market",
        action="store_true",
        help="Disable minimal MarketNode (no price_history updates).",
    )
    parser.add_argument(
        "--redebedarf",
        action="store_true",
        help="Use C3 Redebedarf scheduler (sequential, score-based) instead of default parallel agents.",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce per-round console output.")
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=5,
        help="Save a checkpoint every N ticks (default: 5). Final tick is always saved.",
    )
    parser.add_argument(
        "--no-protocol", action="store_true", help="Do not generate protocol output."
    )
    parser.add_argument(
        "--no-scenarios", action="store_true", help="Do not generate scenarios from CIB matrix."
    )
    parser.add_argument(
        "--no-run-scenario",
        action="store_true",
        help="Do not generate P3 run_scenario.md/json after the run.",
    )
    parser.add_argument(
        "--generate-run-scenario-only",
        action="store_true",
        help="Only regenerate run_scenario.md/json for --run-id (no simulation).",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use the deterministic mock LLM backend instead of calling Ollama. "
        "Independent of OLLAMA_MODEL and other environment variables.",
    )
    parser.add_argument(
        "--use-local-ollama",
        action="store_true",
        help="Require and use a locally running Ollama model (uses `ollama ps` to verify).",
    )
    parser.add_argument(
        "--ollama-wait-seconds",
        type=int,
        default=180,
        help="Maximum seconds to wait for local Ollama model to become ready (used with --use-local-ollama).",
    )
    parser.add_argument(
        "--deterministic-only",
        action="store_true",
        help="Run simulation without LLM agent calls (pure deterministic mode for sweeps/benchmarks).",
    )
    parser.add_argument(
        "--sweep",
        type=str,
        default=None,
        help="Path to a sweep config JSON file. Overrides simulation parameters with sweep settings.",
    )
    # **Eine Aussage ohne Schalter** (P3.11). `llm_narrative` beschreibt den
    # Hybridmodus: deterministisch gerechnete Ticks, aber ein Abschlusstext vom
    # Modell. Den erzeugt **nur** der Sweep-Pfad — dieser Einstieg gibt
    # `prefer_llm=not deterministic_only` weiter, ein rein deterministischer Lauf
    # bekommt hier also gar kein Modell zu sehen. `False` ist damit kein
    # Rückfall, sondern eine Eigenschaft dieses Pfades; sie steht hier, weil
    # `RunArgs` das Feld zu Recht verlangt und ein weggelassenes von einem
    # abgeschalteten nicht zu unterscheiden wäre.
    parser.set_defaults(llm_narrative=False)
    return parser.parse_args()


def save_run_outputs(
    state,
    args: RunArgs,
    llm: OllamaClient,
    *,
    run_dir: Path,
    run_id: str,
) -> dict[str, str | None]:
    """Persist the standard simulation artefacts for one completed run."""

    event_log_path = save_event_log(state.event_log, run_dir=run_dir)
    price_history_path = save_price_history(state.price_history, run_dir=run_dir)
    properties_timeseries_path = save_properties_timeseries(
        state.property_timeseries,
        run_dir=run_dir,
    )
    population_timeseries_path = save_population_timeseries(
        state.population_stats,
        run_dir=run_dir,
    )
    age_property_csv_path = save_age_property_csv(
        state.population_stats,
        run_dir=run_dir,
    )
    factors_timeseries_path = save_factors_timeseries(
        state.factor_timeseries,
        run_dir=run_dir,
    )
    population_csv_path = save_population_individuals(
        state.population_individuals,
        run_dir=run_dir,
    )
    round_history_path = save_round_history(state.round_results, run_dir=run_dir)
    segment_analysis_path = save_segment_analysis(state.round_results, run_dir=run_dir)
    final_narrative_path = save_final_narrative(state, run_dir=run_dir)
    tick_mechanics_path = save_tick_mechanics(state, run_dir=run_dir)
    if state.cib_matrix is not None:
        from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor

        checker = ConsistencyChecker(state.cib_matrix)
        final_factors = {
            k: v.current_state for k, v in state.environment.factors.items() if v.current_state
        }
        scenario_desc = ScenarioDescriptor(factor_states=final_factors)
        consistency_score = checker.compute_consistency_score(scenario_desc)

        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        state.cib_matrix.metadata["consistency_score"] = consistency_score

    cib_matrix_path = save_cib_matrix(state, run_dir=run_dir)

    protocol_path = None
    protocol_md_path = None
    if not args.no_protocol:
        protocol_payload = build_protocol_payload(
            state,
            ProtocolOptions(include_redebedarf=args.redebedarf),
        )
        protocol_path = save_protocol(protocol_payload, run_dir=run_dir)
        protocol_md_path = save_protocol_markdown(
            render_protocol_markdown(protocol_payload),
            run_dir=run_dir,
        )

    scenarios_path = None
    scenarios_md_path = None
    if not args.no_scenarios and state.cib_matrix is not None:
        scenario_node = ScenarioAgentNode(llm=llm)
        state = scenario_node.invoke(state)
        # **`erzaehlte_szenarien`, nicht `scenarios`** (behoben mit P2.0-B).
        # P1.3 hat den Metadaten-Schlüssel umbenannt und diesen Leser nicht
        # mitgezogen — seither schrieb jeder Lauf ein leeres `scenarios.json`.
        # Dieselbe Drift hatte P1.3 in `render_scenarios_markdown` schon einmal
        # gefunden; sie saß eine Ebene weiter außen ein zweites Mal.
        #
        # Die Form ist die von `ErzaehlteSzenarien.model_dump()`, also
        # `{"szenarien": [...]}` — genau das, was der Bericht erwartet. Vorher
        # bekam er `{"scenarios": …}` und hätte auch mit gefülltem Schlüssel
        # nichts anzeigen können.
        scenarios_payload = (state.cib_matrix.metadata or {}).get("erzaehlte_szenarien") or {
            "szenarien": []
        }
        scenarios_path = save_scenarios(scenarios_payload, run_dir=run_dir)
        scenarios_md_path = save_scenarios_markdown(
            render_scenarios_markdown(scenarios_payload, state),
            run_dir=run_dir,
        )

    run_scenario_md_path = None
    run_scenario_json_path = None
    if not args.no_run_scenario:
        scenario_result = generate_and_save_run_scenario(
            run_id,
            llm,
            run_dir=run_dir,
            prefer_llm=not args.deterministic_only,
        )
        paths = scenario_result.get("paths") or {}
        run_scenario_md_path = paths.get("markdown")
        run_scenario_json_path = paths.get("json")
        # Die Pipeline fällt bei einem Ausfall auf ihr deterministisches Template
        # zurück, statt den fertig gerechneten Lauf mitzureißen. Damit das Ergebnis
        # nicht als vollwertiges Narrativ durchgeht, wird der Ausfall hier zum
        # Vorfall — und landet damit in `llm_incidents.json` und im Warnbanner.
        scenario_llm_error = scenario_result.get("llm_error")
        if scenario_llm_error:
            state.llm_incidents.append(
                LLMIncident(
                    tick=state.clock.current_tick,
                    caller="run_scenario_generator",
                    kind="call_failed",
                    error=str(scenario_llm_error),
                )
            )

    # Zuletzt, damit auch ein Ausfall im Szenario-Narrativ noch mitgezaehlt wird.
    llm_incidents_path = save_llm_incidents(state.llm_incidents, run_dir=run_dir)
    metadata_path = save_run_metadata(
        state,
        args,
        run_dir=run_dir,
        run_id=run_id,
    )

    return {
        "run_id": run_id,
        "output_dir": str(run_dir),
        "event_log": event_log_path,
        "price_history": price_history_path,
        "round_history": round_history_path,
        "run_metadata": metadata_path,
        "llm_incidents": llm_incidents_path,
        "segment_analysis": segment_analysis_path,
        "final_narrative": final_narrative_path,
        "tick_mechanics": tick_mechanics_path,
        "cib_matrix": cib_matrix_path,
        "protocol": protocol_path,
        "protocol_markdown": protocol_md_path,
        "scenarios": scenarios_path,
        "scenarios_markdown": scenarios_md_path,
        "run_scenario": run_scenario_json_path,
        "run_scenario_markdown": run_scenario_md_path,
        "properties_timeseries": properties_timeseries_path,
        "population_timeseries": population_timeseries_path,
        "age_property_csv": age_property_csv_path,
        "factors_timeseries": factors_timeseries_path,
        "population_csv": population_csv_path,
    }


def _resolve_run_layout(args: argparse.Namespace, repo_root: Path) -> tuple[str, Path, Path]:
    """Resolve run id, output directory, and checkpoint directory."""

    run_id = args.run_id or create_run_id()
    run_dir = resolve_run_output_dir(run_id)

    if args.checkpoint_dir:
        ck_path = Path(args.checkpoint_dir)
        if not ck_path.is_absolute():
            ck_path = repo_root / ck_path
    else:
        ck_path = run_dir / "checkpoints"

    return run_id, run_dir, ck_path


def _launch_studio() -> int:
    """Start the LangGraph dev server for interactive debugging."""

    if not STUDIO_DIR.is_dir():
        raise RuntimeError(f"LangGraph Studio directory not found: {STUDIO_DIR}")

    print(f"Starting LangGraph Studio in {STUDIO_DIR}")
    print("Open the URL shown below in your browser. Press Ctrl+C to stop.")

    try:
        import langgraph_api  # noqa: F401
        import langgraph_cli  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "LangGraph Studio dependencies missing. Run: pip install -r requirements.txt "
            "(needs langgraph-cli[inmem] with langgraph-api)."
        ) from exc

    return subprocess.call(
        [sys.executable, "-m", "langgraph_cli", "dev"],
        cwd=STUDIO_DIR,
    )


def build_run_args(base_args: object, *, run_index: int, seed: int | None) -> RunArgs:
    """Die Lauf-Argumente eines Teillaufs — **typisiert** seit P3.11.

    Hier stand bis zum 2026-09-05 ein handgeschriebener `SimpleNamespace` mit
    sechzehn Feldern, von denen zehn über ``getattr(..., False)`` entstanden.
    Zwei Folgen davon sind belegt:

    * Ein Feld, das der Aufrufer vergisst, war von einem abgeschalteten nicht zu
      unterscheiden. Genau so wurde jeder Dashboard-Lauf «Ohne Sprachmodell» als
      vollwertiger LLM-Lauf protokolliert (Gegenprobe zu P0.6).
    * **`llm_narrative` wurde gar nicht mitkopiert.** Nachgestellt: Aus
      ``deterministic_with_llm_narrative`` wurde beim Durchreichen
      ``deterministic_only``. Kein Pfad erreicht den Fall heute — die nächste
      Änderung hätte ihn erreicht, und niemand hätte es gesehen.

    Beides geht mit der Typisierung weg, ohne dass hier eine Feldliste stünde:
    :func:`~src.models.run_models.run_args_from` übernimmt, was das Modell kennt,
    und das Modell allein hält die Vorgabewerte.

    *base_args* ist bewusst `object` und nicht `argparse.Namespace`: Auch das
    Dashboard baut hier hinein, und es hat keine CLI.
    """

    return run_args_from(base_args, run_index=run_index, seed=seed)


def write_multi_run_summary(
    *,
    summary_path: Path,
    result: MultiRunResult,
    run_artifacts: list[dict[str, str | None]],
) -> None:
    summary_payload: dict[str, Any] = {
        "aggregate": result.aggregate,
        "runs": [],
    }
    for run_result, artifacts in zip(result.runs, run_artifacts, strict=False):
        summary_payload["runs"].append(
            {
                "run_id": run_result.run_id,
                "seed": run_result.seed,
                "ticks_completed": run_result.ticks_completed,
                "tick_timeline": list(range(1, run_result.ticks_completed + 1)),
                "checkpoint_paths": [str(path) for path in run_result.checkpoint_paths],
                "artifacts": artifacts,
            }
        )

    summary_path.write_text(
        json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


#: Exit-Code fuer eine Konfiguration, die einen Lauf nicht zulaesst (P3.3).
#:
#: **Nicht 1.** Ein Aufrufer soll «deine Eingabe ist falsch» von «mir ist etwas
#: kaputtgegangen» unterscheiden koennen, ohne die Meldung zu lesen — Skripte und
#: CI tun genau das. Die 2 ist die Konvention, die `argparse` fuer denselben Fall
#: schon benutzt (unbekanntes Argument), und damit die einzige, die hier keinen
#: neuen Dialekt einfuehrt.
EXIT_KONFIGURATION = 2


def _llm_config_from_args(args: argparse.Namespace) -> LLMConfig:
    """Welches Sprachmodell dieser Aufruf benutzt — **die eine Ableitung** (P3.4).

    Sie hat zwei Leser: den `OllamaClient` und `state.config.llm`. Vorher baute
    jede der drei Client-Stellen ihre `OllamaConfig` selbst aus `args`, und
    `state.config.llm` las niemand — im Zustand stand, was in der Config-Datei
    stand, während der Lauf mit den Argumenten rechnete.

    Das Gegenstück auf der Dashboard-Seite ist
    `dashboard.config_catalog.llm_config_from_draft`. Zwei Oberflächen, zwei
    Eingabeformen, aber je genau eine Ableitung — und `tests/test_llm_defaults.py`
    hält beide gegen den Client, der daraus entsteht.
    """

    return LLMConfig(
        model=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )


def _ollama_client(llm_config: LLMConfig) -> OllamaClient:
    return OllamaClient(
        OllamaConfig(
            base_url=llm_config.base_url,
            model=llm_config.model,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens,
        )
    )


def _melde_befunde(kopf: str, befunde: list[str]) -> None:
    """Eine Fehlerliste auf `stderr`, wie das Dashboard sie im roten Kasten zeigt.

    **Dieselbe Liste, nicht dieselbe Ausnahme.** Seit P0.3 weist ein Lauf mit
    kaputter Config sauber ab — im Dashboard als roter Kasten mit *allen*
    Befunden, auf der CLI als roher Python-Traceback: zwanzig Zeilen Stack, in
    denen die eigentliche Meldung unterging, und ein Exit-Code, der nichts sagte.
    Die Pruefung war richtig, ihre Darstellung nicht.

    **Geschrieben wird zeichensatzfest**, und der Grund ist gemessen: Die
    Windows-Konsole dieses Projekts steht auf `cp1252`, und in `src/` stehen 46
    Zeichenketten mit Zeichen, die dieser Zeichensatz nicht kennt (`→`, `≥`,
    `₂`, `Δ`) — **gezaehlt ohne Docstrings**, denn ein Docstring wird nicht
    ausgegeben. Wer alle Konstanten zaehlt, kommt auf 55; die Definition gehoert
    deshalb neben die Zahl (C1 des Phase-3-Audits). Kein heutiger Validierungsbefund enthaelt eines davon — aber ein
    einziges genuegte, um die Liste durch einen `UnicodeEncodeError` zu
    ersetzen: einen Traceback an der Stelle, an der dieses Paket gerade einen
    weggeraeumt hat. Ein Fehlerweg, der selbst scheitern kann, ist keiner.
    Der weitere Umgang mit diesen 46 Stellen ist ein eigener Befund (P3.10).
    """

    _schreibe(kopf)
    for befund in befunde:
        _schreibe(f"  - {befund}")


def _schreibe(zeile: str) -> None:
    """Eine Zeile auf `stderr`, notfalls mit ersetzten Zeichen statt gar nicht.

    `backslashreplace` und nicht `replace`: Ein `\\u2265` ist nachschlagbar, ein
    `?` ist verloren. Wer den Befund weitermeldet, soll sagen koennen, was dort
    stand.

    **Der Ausweichpfad braucht nichts als `write`** (P3.14). Bis zum 2026-09-05
    schrieb er die entschaerften Bytes nach ``sys.stderr.buffer`` — und ein
    Strom **ohne** dieses Attribut machte aus dem `UnicodeEncodeError` einen
    `AttributeError`: einen Traceback an genau der Stelle, an der P3.3 einen
    weggeraeumt hat. Ein Fehlerweg, der selbst scheitern kann, ist keiner, und
    dieser hier ist die Reserve fuer genau den Fall, den `stdio_auf_utf8`
    offenlaesst (ein Strom, der die Umstellung verweigert — dafuer warnt sie,
    statt zu scheitern).

    **Der Umweg ueber die Bytes war ueberfluessig**, und das ist der Grund, warum
    hier kein `getattr(..., "buffer", None)` steht: `backslashreplace` ersetzt
    genau die Zeichen, die diese Kodierung *nicht* kann, durch ASCII-Escapes —
    was uebrig bleibt, ist per Konstruktion schreibbar. Zurueckdekodiert geht es
    deshalb durch dieselbe `print`-Zeile wie der Normalfall. Ein Zeichen, das
    die Konsole darstellen kann (`oe`, `—`), bleibt dabei stehen; nur das
    Unschreibbare wird zu `\\u2265`.
    """

    try:
        print(zeile, file=sys.stderr)
    except UnicodeEncodeError:
        kodierung = getattr(sys.stderr, "encoding", None) or "ascii"
        entschaerft = zeile.encode(kodierung, errors="backslashreplace").decode(
            kodierung, errors="replace"
        )
        print(entschaerft, file=sys.stderr)


def main() -> int:
    """Der Einstieg der CLI — und die Stelle, an der ein Befund lesbar wird (P3.3).

    Was hier gefangen wird, sind die **erwarteten** Fehlschläge: eine
    Konfiguration, die keinen Lauf zulässt, und ein Zwischenstand aus einem
    fremden Format. Beide sind Aussagen über die Eingabe und kein Programmfehler,
    also gehören sie als Liste auf `stderr` und nicht als Traceback.

    **Alles andere schlägt weiterhin durch.** Ein `KeyError` aus der Engine ist
    keine Nachricht an den Nutzer, sondern ein Befund für die Entwicklung — der
    Stack ist dort die nützlichere Ausgabe. Ein `except Exception` an dieser
    Stelle wäre genau das Muster, das P3.3 an zwei anderen Stellen abräumt.
    """

    try:
        return _main()
    except ValidationError as fehler:
        # `validate_state` und die CLI-Pruefung werfen beide mit dem Kopf
        # "validierungsfehler:" und einer eingerueckten Liste. Hier wird sie
        # wieder in Zeilen zerlegt, damit die Darstellung an *einer* Stelle
        # entsteht und nicht zweimal formatiert wird.
        zeilen = str(fehler).splitlines()
        kopf = zeilen[0] if zeilen else "validierungsfehler:"
        befunde = [z.strip().removeprefix("- ") for z in zeilen[1:] if z.strip()]
        _melde_befunde(kopf, befunde or [str(fehler)])
        return EXIT_KONFIGURATION
    except CheckpointVersionError as fehler:
        _melde_befunde("Der Zwischenstand passt nicht zu dieser Fassung:", [str(fehler)])
        return EXIT_KONFIGURATION


def _main() -> int:
    # **Vor dem ersten Zeichen** (P3.10): Ist die Ausgabe umgeleitet, spricht
    # `sys.stdout` unter Windows cp1252, und jede Meldung mit `→`, `≥` oder `₂`
    # wirft einen `UnicodeEncodeError` statt zu erscheinen. Auf einer echten
    # Konsole ändert der Aufruf nichts — sie spricht schon UTF-8.
    stdio_auf_utf8()
    args = _parse_args()
    # Vor allem anderen: ohne diesen Aufruf hat das Projekt keinen Log-Handler,
    # und jede Warnung unterhalb von WARNING verschwindet spurlos. `--quiet`
    # daempft die Ausgabe, schaltet aber Warnungen nicht ab — ein LLM-Ausfall
    # soll auch im stillen Modus zu sehen sein.
    configure_logging(logging.WARNING if args.quiet else logging.INFO)
    load_env()

    # **Einmal abgeleitet, zweimal benutzt** (P3.4): hier für den Client, unten
    # für `state.config.llm`. Nach `load_env()`, weil die Umgebung aus
    # `langgraph_studio/.env` sonst zu spät käme.
    llm_config = _llm_config_from_args(args)

    # Diese drei gehen direkt an den `OllamaClient` und nie durch `validate_state`
    # — ohne die Prüfung hier käme ein `--temperature 99` erst beim Modell an.
    # Mit `--mock-llm` wird gar kein Client gebaut, dann wäre die Prüfung eine
    # Schranke vor einer Tür, durch die niemand geht.
    if not args.mock_llm:
        llm_errors = validate_llm_settings(
            llm_config.model,
            llm_config.temperature,
            llm_config.max_tokens,
            context="CLI",
            base_url=llm_config.base_url,
        )
        if llm_errors:
            raise ValidationError(
                "validierungsfehler:\n" + "\n".join(f"  - {e}" for e in llm_errors)
            )

    if args.studio:
        if args.resume is not None:
            raise ValueError("--studio cannot be combined with --resume")
        if args.runs != 1:
            raise ValueError("--studio cannot be combined with --runs")
        return _launch_studio()

    if args.generate_run_scenario_only:
        if not args.run_id:
            raise ValueError("--generate-run-scenario-only requires --run-id")
        if args.mock_llm:
            llm = MockLLM()
        else:
            llm = _ollama_client(llm_config)
        run_dir = resolve_run_output_dir(args.run_id)
        result = generate_and_save_run_scenario(
            args.run_id,
            llm,
            run_dir=run_dir,
            prefer_llm=not args.deterministic_only,
        )
        if not args.quiet:
            print(result["paths"]["markdown"])
            print(result["paths"]["json"])
        return 0

    if args.mock_llm:
        # Bewusst `MockLLM` statt `get_llm()`: letzteres liefert `LocalOllama`,
        # sobald OLLAMA_MODEL gesetzt ist — der Schalter tat dann nicht, was sein
        # Name sagt. Seit P0.1 ist `--mock-llm` unabhaengig von der Umgebung.
        llm = MockLLM()
    elif args.use_local_ollama:
        try:
            proc = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
            out = proc.stdout
        except Exception as exc:
            raise RuntimeError(
                "Failed to run `ollama ps`. Ensure Ollama CLI is installed and on PATH."
            ) from exc

        model_tag = args.model
        if model_tag not in out and f"{model_tag}:latest" not in out:
            raise RuntimeError(
                f"Requested local Ollama model '{model_tag}' not found in `ollama ps` output. Start it with `ollama run {model_tag}`."
            )

        llm = _ollama_client(llm_config)
        print(
            f"Waiting up to {args.ollama_wait_seconds}s for local Ollama model '{args.model}' to become ready..."
        )
        generate_url = args.base_url.rstrip("/") + "/api/generate"
        deadline = time.time() + float(args.ollama_wait_seconds)
        warmed = False
        test_payload = {
            "model": args.model,
            "prompt": "Hello",
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 8},
        }
        while time.time() < deadline:
            try:
                resp = requests.post(generate_url, json=test_payload, timeout=(5, 30))
                if resp.status_code == 200:
                    warmed = True
                    print("Local Ollama model ready.")
                    break
                else:
                    print(f"Model not ready yet (status={resp.status_code}), retrying...")
            except Exception as exc:
                print(f"Waiting for model: {exc}")
            time.sleep(2.0)

        if not warmed:
            raise RuntimeError(
                f"Local Ollama model '{args.model}' did not become ready within {args.ollama_wait_seconds} seconds."
            )
    else:
        llm = _ollama_client(llm_config)

    runner = SimulationRunner(
        llm=llm,
        options=RunnerOptions(
            enable_market=not args.no_market,
            enable_redebedarf=bool(args.redebedarf),
            deterministic_only=bool(args.deterministic_only),
            checkpoint_interval=max(0, int(args.checkpoint_interval)),
            verbose_ticks=not args.quiet,
        ),
    )
    repo_root = Path(__file__).resolve().parents[1]

    if args.resume is not None and args.runs != 1:
        raise ValueError("--resume is only supported for single-run execution")

    if args.resume is not None:
        run_id, run_dir, ck_path = _resolve_run_layout(args, repo_root)
        checkpoint_manager = CheckpointManager(ck_path)
        state = None
        if not args.quiet:
            print(f"Resuming simulation from checkpoint reference: {args.resume}")
        final_state = runner.run(
            state,
            checkpoint_store=checkpoint_manager,
            resume_from=args.resume,
            run_id=run_id,
        )
        artifacts = save_run_outputs(
            final_state,
            build_run_args(args, run_index=1, seed=final_state.config.seed),
            llm,
            run_dir=run_dir,
            run_id=run_id,
        )
        if not args.quiet:
            print(f"Output directory: {run_dir}")
            print(
                "Saved: "
                + ", ".join([path for path in artifacts.values() if isinstance(path, str) and path])
            )
            print(
                f"\nDone. ticks={final_state.clock.current_tick}, events={len(final_state.event_log)}, "
                f"round_results={len(final_state.round_results)}, price_history={len(final_state.price_history)}"
            )
        return 0

    base_state = build_initial_state()
    # Die ausgelieferten Dateien **sind** ein Rahmenszenario — sie tragen eigene
    # exogene Verläufe (P2.0-B). Sie hießen bisher nur nicht so, und deshalb sah
    # ein CLI-Lauf aus, als liefe er «ohne Szenario».
    base_state.rahmen = Rahmenszenario(
        id="standard", name="Standard-Ausgangslage", quelle="standard"
    )
    if args.rounds is not None:
        base_state.clock.max_ticks = int(args.rounds)
    if args.seed is not None:
        base_state.config.seed = int(args.seed)
    if not args.mock_llm:
        # **Der Zustand trägt jetzt, mit welchem Modell gerechnet wird** (P3.4).
        # Vorher stand hier weiter der Wert aus `configs/simulation_config.json`,
        # während der Lauf mit `--model` rechnete — und weil niemand das Feld
        # las, fiel der Widerspruch nicht auf. Bei `--mock-llm` bleibt es
        # unberührt: Gerufen wird nichts, also beschreibt es nichts.
        base_state.config.llm = llm_config

    if args.runs == 1:
        run_id, run_dir, ck_path = _resolve_run_layout(args, repo_root)
        checkpoint_manager = CheckpointManager(ck_path)

        if not args.quiet:
            print(
                f"Simulation start: ticks={base_state.clock.max_ticks}, model={args.model}, "
                f"market={'off' if args.no_market else 'on'}, "
                f"orchestration={'redebedarf' if args.redebedarf else 'parallel'}, run_id={run_id}"
            )

        final_state = runner.run(
            base_state,
            seed=args.seed,
            checkpoint_store=checkpoint_manager,
            run_id=run_id,
        )
        artifacts = save_run_outputs(
            final_state,
            build_run_args(args, run_index=1, seed=args.seed),
            llm,
            run_dir=run_dir,
            run_id=run_id,
        )
        if not args.quiet:
            print(f"Output directory: {run_dir}")
            print(
                "Saved: "
                + ", ".join([path for path in artifacts.values() if isinstance(path, str) and path])
            )
            print(
                f"\nDone. ticks={final_state.clock.current_tick}, events={len(final_state.event_log)}, "
                f"round_results={len(final_state.round_results)}, price_history={len(final_state.price_history)}"
            )
        return 0

    batch_id = args.run_id or create_run_id("batch")
    batch_dir = resolve_run_output_dir(batch_id)
    ck_path = Path(args.checkpoint_dir) if args.checkpoint_dir else batch_dir / "checkpoints"
    if not ck_path.is_absolute():
        ck_path = repo_root / ck_path
    checkpoint_manager = CheckpointManager(ck_path)

    if not args.quiet:
        print(
            f"Simulation start: runs={args.runs}, ticks={base_state.clock.max_ticks}, model={args.model}, "
            f"market={'off' if args.no_market else 'on'}, batch_id={batch_id}"
        )

    if not args.quiet:
        print(f"Starting multi-run: runs={args.runs}, ticks={base_state.clock.max_ticks}")

    multi_result = runner.run_multi(
        args.runs,
        base_state=base_state,
        checkpoint_store=checkpoint_manager,
    )

    all_artifacts: list[dict[str, str | None]] = []
    for index, run_result in enumerate(multi_result.runs, start=1):
        run_id = f"run_{index:03d}"
        run_dir = batch_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        run_args = build_run_args(args, run_index=index, seed=run_result.seed)
        artifacts = save_run_outputs(
            run_result.final_state,
            run_args,
            llm,
            run_dir=run_dir,
            run_id=run_id,
        )
        all_artifacts.append(artifacts)

    if checkpoint_manager is not None:
        for run_result in multi_result.runs:
            try:
                ck_existing = checkpoint_manager.list_checkpoints(run_result.run_id)
                if not ck_existing:
                    checkpoint_manager.save(
                        run_result.final_state,
                        run_id=run_result.run_id,
                        round_number=run_result.final_state.clock.current_tick,
                    )
            except Exception as exc:
                print(f"Warning: failed to ensure checkpoint for {run_result.run_id}: {exc}")

    summary_path = batch_dir / "multi_run_summary.json"
    write_multi_run_summary(
        summary_path=summary_path, result=multi_result, run_artifacts=all_artifacts
    )

    for idx, run_result in enumerate(multi_result.runs, start=1):
        seed_info = run_result.seed
        print(
            f"Run {idx:03d}: run_id={run_result.run_id} seed={seed_info} checkpoints={run_result.checkpoint_paths}"
        )

    if not args.quiet:
        print(
            "Saved: "
            + ", ".join(
                [
                    str(summary_path),
                    *[
                        path
                        for artifacts in all_artifacts
                        for path in artifacts.values()
                        if isinstance(path, str) and path
                    ],
                ]
            )
        )
        print(f"\nDone. runs={len(multi_result.runs)}, aggregate={multi_result.aggregate}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
