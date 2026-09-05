"""Scenario sweeps: runs parameter-sweep scenarios in deterministic mode
and evaluates end-states against the CIB consistency matrix.

CLI usage:
    python src/scenario_sweeps.py                           # all sweeps in configs/sweeps/
    python src/scenario_sweeps.py --ticks 10000             # 10k-tick benchmark
    python src/scenario_sweeps.py --sweep co2_delayed.json  # single sweep
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# **Hier stand bis P3.10 ein Import-Seiteneffekt** (2026-09-05):
#
#     if hasattr(sys.stdout, "reconfigure"):
#         sys.stdout.reconfigure(encoding="utf-8", errors="replace")
#
# Zwei Zeilen auf Modulebene, die einen **prozessglobalen** Zustand ändern —
# ausgelöst dadurch, dass irgendjemand irgendetwas aus `src.orchestration`
# importiert (das Paket-`__init__` zieht dieses Modul mit). Gemessen deckte das
# 7 von 11 Einstiegspunkten ab, ohne dass es irgendwo stand: Der CLI-Lauf, das
# Dashboard und der State Explorer waren **zufällig** sicher, `create_graph.py`,
# `serve_graph.py` und `cib_visualizer.py` nicht. Und `stderr` war nirgends
# gesichert — dort landen die Logging-Fehler und die Befundliste aus P3.3.
#
# Die Umstellung liegt jetzt in `logging_setup.stdio_auf_utf8()`, und jeder
# Einstieg ruft sie ausdrücklich. Ein Prozess, dessen Ausgabe von der
# Importreihenfolge abhängt, sagt niemandem, warum er es tut.
from src.cib.scenario_consistency import ConsistencyChecker, ScenarioDescriptor
from src.config_loader import build_initial_state, load_cib_frozen
from src.llm import OllamaClient, OllamaConfig
from src.logging_setup import stdio_auf_utf8
from src.market.market_feedback import BOOKING_YIELD_FEEDBACK
from src.models.llm_models import LLMIncident
from src.models.run_models import RunArgs
from src.models.state_models import Rahmenszenario
from src.models.sweep_models import (
    MilestoneCheck,
    SweepConfig,
    SweepResult,
    SweepSummary,
)
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner
from src.reporting.output_writer import (
    resolve_run_output_dir,
    save_cib_matrix,
    save_event_log,
    save_factors_timeseries,
    save_final_narrative,
    save_llm_incidents,
    save_population_timeseries,
    save_price_history,
    save_properties_timeseries,
    save_round_history,
    save_run_metadata,
    save_segment_analysis,
    save_tick_mechanics,
)
from src.reporting.run_scenario_generator import generate_and_save_run_scenario

#: Sweeps laufen bewusst mit festem Seed — sie sollen vergleichbar sein,
#: nicht variabel. Stand bis P0.6 zweimal als Literal im Modul: einmal im
#: Lauf, einmal in den Metadaten, die ihn behaupteten.
SWEEP_SEED = 42


@dataclass(frozen=True)
class Festlegung:
    """Eine Einstellung, die der Szenario-Vergleich **vorgibt** statt entgegenzunehmen."""

    #: Wie das Feld im Entwurf des Assistenten heißt.
    feld: str
    #: Der Wert, mit dem der Sweep tatsächlich rechnet.
    wert: object
    #: Was dem Nutzer dazu gesagt wird. Ein Satz, kein Fachbegriff.
    grund: str


#: **Der Vertrag des Szenario-Vergleichs (P1.9-W1.1).**
#:
#: Ein Sweep nimmt vom Entwurf des Assistenten fast nichts entgegen: Er rechnet
#: alle hinterlegten Szenarien unter **gleichen** Bedingungen, weil sie sonst
#: nicht vergleichbar wären. Das ist eine bewusste Entscheidung und bleibt so.
#:
#: Was daran falsch war, ist nicht die Festlegung, sondern ihr **Schweigen**:
#: Der Assistent fragte Rechenmodus und Zufallsstartwert ab, der Preflight
#: zeigte die Antworten an, und der Lauf verwarf sie. Ein Nutzer beantwortete
#: Schritt 3 und bekam etwas anderes, ohne Hinweis.
#:
#: Diese Tabelle ist die Antwort darauf — und sie ist **die Quelle des
#: Verhaltens**, nicht eine Beschreibung daneben. `run_single_sweep` liest
#: seine Werte hier heraus; eine Fassung, die den Vertrag nur *beschreibt*,
#: liefe früher oder später von ihm weg. Genau diese Drift hat dieses Projekt
#: schon dreimal bezahlt (F7, die drei Rule-Evaluatoren, der Kostendruck).
#:
#: `dashboard/web/config_editor/` liest sie ebenfalls und stellt die
#: betroffenen Felder als vorgegeben dar (W1.3).
FESTLEGUNGEN: tuple[Festlegung, ...] = (
    Festlegung(
        "deterministic_only",
        True,
        "Der Szenario-Vergleich rechnet immer ohne Agenten-Dialog — acht Läufe mit "
        "Sprachmodell wären nicht vergleichbar und dauerten Stunden.",
    ),
    Festlegung(
        "seed",
        SWEEP_SEED,
        f"Alle Szenarien laufen mit demselben Zufallsstartwert ({SWEEP_SEED}). Nur so "
        "zeigt ein Unterschied zwischen ihnen das Szenario und nicht die Ziehung.",
    ),
    Festlegung(
        "checkpoint_interval",
        0,
        "Ein Vergleich schreibt keine Zwischenstände — er wird nicht fortgesetzt, "
        "sondern wiederholt.",
    ),
)

#: Felder, die der Szenario-Vergleich **gar nicht beachtet** — im Unterschied zu
#: `FESTLEGUNGEN`, wo er einen bestimmten Wert einsetzt. Für den Nutzer ist der
#: Unterschied gering («meine Antwort zählt hier nicht»), für den Code nicht:
#: Diese hier tragen keinen Wert, den `run_single_sweep` einsetzen könnte.
#:
#: Der wichtigste ist `apply_custom_overrides`. Ein Vergleich rechnet jedes
#: Szenario **unvermischt** aus seiner eigenen Datei — genau das, was P1.1 für
#: den Einzellauf hergestellt hat. Wer im Assistenten Faktoren und Systemgrößen
#: einstellt und dann einen Vergleich startet, sieht davon nichts wieder.
UNBEACHTET: tuple[Festlegung, ...] = (
    Festlegung(
        "apply_custom_overrides",
        None,
        "Jedes Szenario gilt unvermischt aus seiner eigenen Datei. Eigene "
        "Systemgrößen wirken im Vergleich nicht — sonst verglichen Sie nicht mehr "
        "die Szenarien, sondern Ihre Änderung mit sich selbst.",
    ),
    Festlegung(
        "factor_states",
        None,
        "Die Faktorlage entsteht im Lauf aus den Systemgrößen des Szenarios — sie "
        "wird nicht mehr vorgegeben. Das gilt für jeden Startweg, nicht nur für den "
        "Vergleich: Ein vorher gesetzter Faktorzustand hieße, die Antwort vor die "
        "Rechnung zu stellen.",
    ),
    Festlegung(
        "use_seed",
        None,
        "Der Zufallsstartwert ist vorgegeben; ob Sie einen eigenen gesetzt haben, "
        "spielt im Vergleich keine Rolle.",
    ),
    Festlegung(
        "mock_llm",
        None,
        "Der Vergleich rechnet ohne Agenten-Dialog. Ob ein Sprachmodell bereitstünde, "
        "ändert daran nichts.",
    ),
    Festlegung(
        "no_market",
        None,
        "Der Marktmechanismus läuft in jedem Vergleich mit — ohne ihn gäbe es nichts "
        "zu vergleichen.",
    ),
    Festlegung(
        "redebedarf",
        None,
        "Redebedarf betrifft den Agenten-Dialog, den es hier nicht gibt.",
    ),
    Festlegung(
        "simulation_name",
        None,
        "Jeder Lauf trägt den Namen seines Szenarios, nicht den, den Sie oben "
        "eingetragen haben.",
    ),
    Festlegung(
        "simulation_description",
        None,
        "Wie beim Namen: Es gilt die Beschreibung des jeweiligen Szenarios.",
    ),
    Festlegung(
        "base_price",
        None,
        "Jedes Szenario bringt sein eigenes Preisniveau mit. Ein gemeinsamer "
        "Startpreis würde genau den Unterschied einebnen, den der Vergleich zeigen soll.",
    ),
    Festlegung(
        "rounds",
        None,
        "Jedes Szenario läuft so lang, wie es angelegt ist. Vier der hinterlegten "
        "Szenarien sind auf 50 Ticks entworfen und prüfen ihren Schlusspunkt genau "
        "dort — auf 40 Ticks gekürzt erreichen sie ihn nie. Die Länge stellen Sie "
        "für einen einzelnen Lauf ein, nicht für den Vergleich.",
    ),
)


def vorgegebene_felder() -> dict[str, Festlegung]:
    """Alle Felder, über die der Szenario-Vergleich nicht mit sich reden lässt.

    Die eine Anlaufstelle für die Oberfläche: Was hier drinsteht, darf der
    Assistent beim Vergleich nicht als freie Wahl darstellen (W1.3).
    """

    return {f.feld: f for f in (*FESTLEGUNGEN, *UNBEACHTET)}


#: Was der Vertrag **nicht** abdeckt und trotzdem gilt: Der Szenariotext am Ende
#: jedes Sweeps entsteht mit `prefer_llm=True`. Ein Sweep ist deshalb weder rein
#: deterministisch noch ein Lauf «mit Sprachmodell» — er trägt in
#: `run_metadata.json` den eigenen Modus `deterministic_with_llm_narrative`.
#: Wer «ohne Sprachmodell» wählt und einen Vergleich startet, erreicht Ollama
#: also trotzdem. Steht hier, weil es sonst nirgends stünde.
SZENARIOTEXT_NUTZT_LLM = True


def festlegung_fuer(feld: str) -> Festlegung | None:
    """Die Festlegung zu einem Entwurfsfeld — oder `None`, wenn es frei ist."""

    return vorgegebene_felder().get(feld)


def sweep_metadata_args(sweep_id: str) -> SimpleNamespace:
    """Die Argumente, unter denen ein Sweep sein `run_metadata.json` schreibt.

    Eigene Funktion, damit prüfbar ist, was dort behauptet wird. Der Sweep
    **rechnet** deterministisch, erzeugt den Szenariotext am Ende aber mit
    ``prefer_llm=True`` — er ist damit weder das eine noch das andere und
    trägt den eigenen Modus ``deterministic_with_llm_narrative``.

    Zwei Angaben waren hier vorher unwahr. ``deterministic_only=False`` machte
    aus dem Sweep im Dashboard einen Lauf «Mit Sprachmodell», obwohl an seinen
    Zahlen keines beteiligt ist. Und ``model="dummy_for_sweeps"`` benannte ein
    Modell, das es nicht gibt — befragt wird das Modell aus `OllamaConfig`,
    dasselbe, das die Szenario-Erzeugung unten benutzt. Beides steht jetzt so
    da, wie es ist.

    Der Degradations-Marker hängt an keiner dieser Angaben: `save_run_metadata`
    leitet ``degraded`` allein aus den Vorfällen ab. Ein Ausfall des
    Abschlusstextes bleibt also sichtbar, ohne dass der Rechenmodus dafür
    gebeugt werden müsste.
    """

    llm_defaults = OllamaConfig()
    # `sweep=sweep_id` stand hier bis P3.11 und wurde **von niemandem gelesen** —
    # ein Feld, das der typisierte Vertrag nicht kennt und das deshalb auffällt,
    # statt still mitzureisen. Die Zugehörigkeit eines Laufs zu seinem Sweep
    # steht ohnehin im Ablageort und im Rahmenszenario.
    return RunArgs(
        deterministic_only=True,
        llm_narrative=True,
        mock_llm=False,
        seed=SWEEP_SEED,
        model=llm_defaults.model,
        base_url=llm_defaults.base_url,
        temperature=llm_defaults.temperature,
        max_tokens=llm_defaults.max_tokens,
        no_market=False,
    )


SWEEPS_DIR = REPO_ROOT / "configs" / "sweeps"
SWEEP_OUTPUT_DIR = REPO_ROOT / "outputs" / "sweeps"


def load_sweep_config(path: Path) -> SweepConfig:
    """Load a single sweep configuration from a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return SweepConfig.model_validate(data)


def load_all_sweep_configs(directory: Path | None = None) -> list[SweepConfig]:
    """Load all sweep configs from a directory — **Rahmen und Stresstests**."""
    directory = directory or SWEEPS_DIR
    configs: list[SweepConfig] = []
    for path in sorted(directory.glob("*.json")):
        configs.append(load_sweep_config(path))
    return configs


def rahmenszenarien(directory: Path | None = None) -> list[SweepConfig]:
    """Nur die **begründeten Weltbilder** — was ein Szenario-Vergleich vergleicht.

    **Der Grund ist P2.2 / Variante C.** Bis dahin lagen unter `configs/sweeps/`
    zwei Dinge ununterscheidbar nebeneinander, und `run_all_sweeps` startete
    beide: vier Behauptungen über eine mögliche Welt und vier Stresstests der
    Engine. «Totaler Wahnsinn (Alle Parameter)» stand gleichrangig neben
    «Business as Usual» — einem Kunden wurde damit ein Belastungstest als
    Zukunft angeboten, und der Vergleich stellte acht Ergebnisse nebeneinander,
    von denen die Hälfte keine Aussage über die Welt war.

    Ein Stresstest bleibt **lauffähig und wählbar** — er wird nur nicht mehr
    mitverglichen. Wer ihn einzeln starten will, kann das weiterhin.
    """

    return [config for config in load_all_sweep_configs(directory) if config.art == "rahmen"]


def apply_sweep_overrides(state: Any, sweep: SweepConfig) -> Any:
    """Apply sweep overrides to an initial SimulationState.

    Modifies the state in-place:
    - Adjusts system property trajectories (baseline + rules)
    - Overrides initial factor states
    - Sets max_ticks from sweep config
    """
    state.clock.max_ticks = sweep.max_ticks

    prop_lookup: dict[str, Any] = {}
    for prop in state.properties.system_properties:
        prop_lookup[prop.id] = prop

    for override in sweep.property_overrides:
        prop = prop_lookup.get(override.property_id)
        if prop is None:
            continue
        traj = prop.trajectory
        if traj is None:
            continue

        if override.baseline is not None:
            if hasattr(traj, "baseline"):
                traj.baseline = override.baseline

        if override.rules is not None:
            if hasattr(traj, "rules"):
                from src.models.property_models import TrajectoryRule

                new_rules = []
                for rule_data in override.rules:
                    new_rules.append(TrajectoryRule.model_validate(rule_data))
                traj.rules = new_rules

    # **`factor_overrides` werden seit P2.0-C nicht mehr angewendet.** Ein
    # Rahmenszenario setzt die exogenen Verläufe; die Faktorlage entsteht daraus
    # im Lauf. Sie vorher zu setzen hieße, die Antwort vor die Rechnung zu
    # stellen (Leitentscheidung vom 2026-08-29).
    #
    # Gemessen, bevor das entfernt wurde — vier Presets trugen eine Vorgabe, je
    # 20 Ticks mit und ohne: **In allen vieren landen alle sieben Faktoren auf
    # denselben Zuständen.** Die Vorgabe bestimmte das Ergebnis also nicht, sie
    # störte nur die ersten Ticks, solange die Regeln sie noch nicht
    # überschrieben hatten (Ticketpreis 0,6 % bei `p5.7`, 2,4 % bei
    # `alles_drin_szenario`).
    #
    # Das Feld bleibt im Modell und in den Dateien lesbar — es beschreibt, von
    # welcher Lage ein Szenario erzählt. Wirksam ist es nicht mehr, und weil
    # Invariante 7 verlangt, dass ein Pfad sagt, was er verwirft, steht es in
    # `UNBEACHTET`.

    if sweep.preisstrategie is not None:
        _preisstrategie_setzen(state, sweep.preisstrategie)

    if sweep.base_price is not None:
        state.properties.price_model.base_price = sweep.base_price

    return state


def _preisstrategie_setzen(state: Any, strategie: str) -> None:
    """Die Preisstrategie dieser Welt in die Marktregel schreiben (P2.10).

    **Warum das hier steht und nicht in `property_overrides`:** Die Strategie
    ist keine Systemgröße mit Verlauf, sondern eine Eigenschaft der einen
    `booking_yield_feedback`-Regel. Sie hat keinen Tick-Pfad — ein Anbieter
    wechselt nicht mitten im Lauf seine Preislogik, und wer das modellieren
    will, braucht dafür ein eigenes Paket.

    **Ein unbekannter Name scheitert laut**, und zwar über
    `MarketFeedbackConfig` — dieselbe Prüfung wie überall sonst, statt einer
    zweiten hier. Ein Tippfehler wie `marge_` fiele sonst still auf
    `auslastung` zurück, und das Szenario erzählte etwas anderes als seine
    Begründung.
    """

    from src.models.property_models import MarketFeedbackConfig

    MarketFeedbackConfig(strategie=strategie)  # wirft bei unbekanntem Namen

    regeln = []
    for regel in state.properties.market_rules:
        if regel.effect.get("type") == BOOKING_YIELD_FEEDBACK:
            effekt = dict(regel.effect)
            effekt["strategie"] = strategie
            regel = regel.model_copy(update={"effect": effekt})
        regeln.append(regel)
    state.properties = state.properties.model_copy(update={"market_rules": regeln})


def _property_at_tick(state: Any, tick: int, property_id: str) -> Any:
    for ts_row in state.property_timeseries:
        if ts_row.get("tick") == tick and property_id in ts_row:
            return ts_row[property_id]
    return state.market_metrics.get(property_id)


def _factor_at_tick(state: Any, tick: int, factor_id: str) -> str | None:
    for ts_row in state.factor_timeseries:
        if ts_row.get("tick") == tick and factor_id in ts_row:
            return str(ts_row[factor_id])
    factor = state.environment.factors.get(factor_id)
    if factor is not None and state.clock.current_tick == tick:
        return factor.current_state
    return None


def evaluate_milestone_on_state(state: Any, ms: MilestoneCheck) -> dict[str, Any]:
    """Evaluate one milestone against a completed simulation state."""
    result: dict[str, Any] = {
        "tick": ms.tick,
        "description": ms.description,
        "passed": False,
        "actual_value": None,
    }

    if ms.check_property:
        actual = _property_at_tick(state, ms.tick, ms.check_property)
        result["actual_value"] = actual
        if actual is not None:
            if ms.expected_value is not None:
                tolerance = 0.5 if ms.check_property == "income_index" else 0.01
                result["passed"] = abs(float(actual) - float(ms.expected_value)) <= tolerance
            else:
                result["passed"] = True

    if ms.check_factor:
        actual = _factor_at_tick(state, ms.tick, ms.check_factor)
        result["actual_value"] = actual
        if actual is not None:
            if ms.expected_factor_state is not None:
                result["passed"] = actual == ms.expected_factor_state
            else:
                result["passed"] = True

    return result


def evaluate_milestones(
    state: Any,
    milestones: list[MilestoneCheck],
    tick: int,
) -> list[dict[str, Any]]:
    """Evaluate milestones that are due at this tick."""
    return [evaluate_milestone_on_state(state, ms) for ms in milestones if ms.tick == tick]


def run_single_sweep(
    sweep: SweepConfig,
    *,
    ticks_override: int | None = None,
    verbose: bool = True,
) -> SweepResult:
    """Execute a single sweep in deterministic-only mode."""

    if verbose:
        print(f"\n{'='*60}")
        print(f"Sweep: {sweep.name} ({sweep.id})")
        print(f"  {sweep.description[:80]}...")
        print(f"{'='*60}")

    effective_ticks = ticks_override or sweep.max_ticks

    # Build initial state
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = effective_ticks

    # Apply sweep overrides
    state = apply_sweep_overrides(state, sweep)
    # Welcher Rahmen gilt (P2.0-B) — hier bekannt, später nicht mehr.
    state.rahmen = Rahmenszenario(id=sweep.id, name=sweep.name, quelle="preset")
    if ticks_override:
        state.clock.max_ticks = ticks_override

    # Create a dummy LLM (never called in deterministic mode)
    def dummy_llm(prompt):
        return "{}"

    # Die drei festgelegten Werte kommen aus `FESTLEGUNGEN` und stehen hier
    # nicht mehr als Literal (W1.1). Der Vertrag ist damit die Quelle des
    # Verhaltens: Wer ihn ändert, ändert den Lauf — und wer den Lauf ändert,
    # kommt an ihm nicht vorbei. Eine Tabelle, die nur beschriebe, was daneben
    # hartkodiert ist, wäre in einem halben Jahr falsch.
    festgelegt = {f.feld: f.wert for f in FESTLEGUNGEN}

    runner = SimulationRunner(
        llm=dummy_llm,
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=bool(festgelegt["deterministic_only"]),
            checkpoint_interval=int(festgelegt["checkpoint_interval"]),
            verbose_ticks=False,
        ),
    )

    start_time = time.time()
    run_id_str = f"sweeps/sweep_{sweep.id}"
    final_state = runner.run(
        state,
        seed=int(festgelegt["seed"]),
        run_id=run_id_str,
    )
    elapsed = time.time() - start_time

    # Collect final factor states
    final_factors = {
        fid: factor.current_state for fid, factor in final_state.environment.factors.items()
    }

    # Collect final property values
    final_props: dict[str, float] = {}
    for key, value in final_state.market_metrics.items():
        if isinstance(value, (int, float)):
            final_props[key] = float(value)

    milestone_results = [evaluate_milestone_on_state(final_state, ms) for ms in sweep.milestones]

    # CIB Consistency Scoring
    cib_matrix = load_cib_frozen()
    checker = ConsistencyChecker(cib_matrix)
    scenario = ScenarioDescriptor(factor_states=final_factors)
    consistency_score = checker.compute_consistency_score(scenario)
    stability_index = checker.compute_stability_index(scenario)
    check_result = checker.check_scenario(scenario)

    # Save artifacts like a normal run
    run_dir_path = resolve_run_output_dir(run_id_str)

    dummy_args = sweep_metadata_args(sweep.id)

    save_event_log(final_state.event_log, run_dir=run_dir_path)
    save_tick_mechanics(final_state, run_dir=run_dir_path)
    save_properties_timeseries(final_state.property_timeseries, run_dir=run_dir_path)
    save_population_timeseries(final_state.population_stats, run_dir=run_dir_path)
    save_factors_timeseries(final_state.factor_timeseries, run_dir=run_dir_path)
    save_round_history(final_state.round_results, run_dir=run_dir_path)
    save_price_history(final_state.price_history, run_dir=run_dir_path)
    save_segment_analysis(final_state.round_results, run_dir=run_dir_path)
    save_final_narrative(final_state, run_dir=run_dir_path)

    if final_state.cib_matrix is not None:
        if final_state.cib_matrix.metadata is None:
            final_state.cib_matrix.metadata = {}
        final_state.cib_matrix.metadata["consistency_score"] = consistency_score
    save_cib_matrix(final_state, run_dir=run_dir_path)

    # Generate LLM Scenario
    llm = OllamaClient(OllamaConfig())
    scenario_result = generate_and_save_run_scenario(
        run_id_str,
        llm,
        run_dir=run_dir_path,
        prefer_llm=True,  # Always prefer LLM for the final scenario text
    )
    # P0.6: Bis hierher schrieb der Sweep an P0.1 vorbei — die Metadaten
    # entstanden *vor* der Szenario-Erzeugung, der zurückgegebene `llm_error`
    # wurde verworfen, und `save_llm_incidents` lief nie. Ein Sweep rechnet
    # deterministisch und hat damit genau eine Ausfallquelle: diesen Text.
    # Fiel er auf das Template zurück, stand im Sweep trotzdem
    # `degraded: false`. Dieselbe Kette wie in `run_simulation.save_run_outputs`,
    # und in derselben Reihenfolge: erst der Vorfall, dann die Metadaten.
    scenario_llm_error = scenario_result.get("llm_error")
    if scenario_llm_error:
        final_state.llm_incidents.append(
            LLMIncident(
                tick=final_state.clock.current_tick,
                caller="run_scenario_generator",
                kind="call_failed",
                error=str(scenario_llm_error),
            )
        )

    save_llm_incidents(final_state.llm_incidents, run_dir=run_dir_path)
    save_run_metadata(final_state, dummy_args, run_dir=run_dir_path, run_id=run_id_str)

    try:
        from src.reporting.figure_generator import generate_run_figures

        generate_run_figures(run_dir_path)
        if verbose:
            print(f"  Figures saved under {run_dir_path / 'figures'}")
    except Exception as exc:
        if verbose:
            print(f"  Warning: figure generation failed: {exc}")

    if verbose:
        ticks_done = final_state.clock.current_tick
        print(
            f"  Completed {ticks_done} ticks in {elapsed:.2f}s "
            f"({ticks_done / elapsed:.0f} ticks/sec)"
        )
        print(f"  Final factors: {final_factors}")
        print(f"  CIB consistency: {consistency_score:.3f}, stability: {stability_index:.3f}")
        if check_result.conflicts:
            print(f"  Conflicts ({len(check_result.conflicts)}):")
            for c in check_result.conflicts[:5]:
                print(f"    - {c.encode('ascii', 'replace').decode()}")
        ms_passed = sum(1 for m in milestone_results if m["passed"])
        print(f"  Milestones: {ms_passed}/{len(milestone_results)} passed")
        for m in milestone_results:
            status = "OK" if m["passed"] else "FAIL"
            desc = m["description"].encode("ascii", "replace").decode()
            print(f"    [{status}] Tick {m['tick']}: {desc} " f"(actual={m['actual_value']})")

    return SweepResult(
        sweep_id=sweep.id,
        sweep_name=sweep.name,
        ticks_completed=final_state.clock.current_tick,
        final_factor_states=final_factors,
        final_properties=final_props,
        consistency_score=consistency_score,
        stability_index=stability_index,
        conflicts=check_result.conflicts,
        milestone_results=milestone_results,
    )


def run_all_sweeps(
    *,
    ticks_override: int | None = None,
    sweep_filter: str | None = None,
    verbose: bool = True,
) -> SweepSummary:
    """Run every **framework** scenario and produce a summary.

    Seit P2.2 sind das die Dateien mit ``art == "rahmen"`` — die Stresstests der
    Engine sind hier heraus, weil ein Vergleich Weltbilder gegeneinanderstellt
    und kein Belastungstest eine Zukunft ist. Ein `sweep_filter` greift
    weiterhin auf **alle** Dateien zu: Wer einen Stresstest ausdrücklich nennt,
    bekommt ihn.
    """

    configs = load_all_sweep_configs() if sweep_filter else rahmenszenarien()
    if sweep_filter:
        configs = [c for c in configs if c.id == sweep_filter or sweep_filter in c.id]

    if not configs:
        print("No sweep configs found.")
        return SweepSummary()

    results: list[SweepResult] = []
    total_start = time.time()

    for config in configs:
        result = run_single_sweep(
            config,
            ticks_override=ticks_override,
            verbose=verbose,
        )
        results.append(result)

    total_elapsed = time.time() - total_start

    summary = SweepSummary(
        total_sweeps=len(results),
        results=results,
        metadata={
            "total_elapsed_seconds": round(total_elapsed, 2),
            "ticks_override": ticks_override,
            "sweep_ids": [r.sweep_id for r in results],
        },
    )

    # Save outputs
    _save_sweep_outputs(summary)

    if verbose:
        print(f"\n{'='*60}")
        print("SWEEP SUMMARY")
        print(f"{'='*60}")
        print(f"Total sweeps: {len(results)}")
        print(f"Total time: {total_elapsed:.2f}s")
        print("\nConsistency ranking:")
        for r in sorted(results, key=lambda x: x.consistency_score, reverse=True):
            print(
                f"  {r.sweep_name:40s}  "
                f"consistency={r.consistency_score:.3f}  "
                f"stability={r.stability_index:.3f}  "
                f"conflicts={len(r.conflicts)}"
            )

    return summary


def _save_sweep_outputs(summary: SweepSummary) -> None:
    """Save sweep results to JSON files."""
    SWEEP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # sweep_summary.json
    summary_path = SWEEP_OUTPUT_DIR / "sweep_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2, ensure_ascii=False, default=str)
    print(f"\nSaved: {summary_path}")

    # scenario_scores.json — focused view on CIB scores
    scores = []
    for r in summary.results:
        scores.append(
            {
                "sweep_id": r.sweep_id,
                "sweep_name": r.sweep_name,
                "ticks_completed": r.ticks_completed,
                "final_factor_states": r.final_factor_states,
                "consistency_score": r.consistency_score,
                "stability_index": r.stability_index,
                "num_conflicts": len(r.conflicts),
                "conflicts": r.conflicts,
            }
        )
    scores_path = SWEEP_OUTPUT_DIR / "scenario_scores.json"
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved: {scores_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run parameter-sweep scenarios (M8)")
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Override tick count for all sweeps (e.g. 10000 for benchmark).",
    )
    parser.add_argument(
        "--sweep",
        type=str,
        default=None,
        help="Run only the sweep with this ID (e.g. 'co2_delayed').",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output.",
    )
    args = parser.parse_args()

    summary = run_all_sweeps(
        ticks_override=args.ticks,
        sweep_filter=args.sweep,
        verbose=not args.quiet,
    )

    if not summary.results:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    # Der Prozess sichert seine Ausgabe, bevor er das erste Zeichen schreibt
    # (P3.10): Umgeleitet spricht `sys.stdout` unter Windows cp1252, und dann
    # wirft jede Meldung mit `→`, `≥` oder `₂` statt zu erscheinen.
    stdio_auf_utf8()
    main()
