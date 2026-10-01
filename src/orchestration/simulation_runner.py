from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.agents.agent_node import AgentNode
from src.agents.orchestrator_node import OrchestratorNode
from src.agents.parallel_round_node import ParallelRoundNode
from src.agents.redebedarf_node import RoundExecutionNode
from src.config_loader import build_initial_state
from src.llm import LLMCallable
from src.market.market_node import MarketNode
from src.models.agent_models import AgentConfig
from src.models.enums import AgentType
from src.models.state_models import DEFAULT_SEED, SimulationState
from src.orchestration.environment_node import EnvironmentNode
from src.orchestration.konsole import tick_zeile
from src.reporting.output_writer import append_individuals_history, resolve_run_output_dir
from src.reporting.output_writer.provenance import config_fingerprint
from src.validation import horizontluecken, validate_state

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunnerOptions:
    enable_market: bool = True
    enable_cib: bool = True  # load frozen CIB from configs/cib_frozen.json
    enable_redebedarf: bool = False
    deterministic_only: bool = False  # M8: skip LLM agent calls entirely
    checkpoint_interval: int = 5
    verbose_ticks: bool = True
    tick_progress_callback: Callable[[str], None] | None = None
    #: Wird **zwischen** zwei Ticks gefragt: Soll der Lauf abbrechen?
    #: (P1.9-W4.5)
    #:
    #: Ein Lauf lief bis dahin bis zum Ende oder bis der Prozess starb. Wer
    #: versehentlich 500 Ticks mit Sprachmodell startete, konnte nur warten oder
    #: den Server neu starten.
    #:
    #: **Kooperativ und nicht gewaltsam:** Ein Thread lässt sich von außen nicht
    #: sauber beenden — mitten in einem Tick abgebrochen bliebe ein halber
    #: Zustand zurück, und die Artefakte beschrieben einen Lauf, den es so nie
    #: gab. Gefragt wird deshalb an der einen Stelle, an der der Zustand
    #: vollständig ist: nach einem fertigen Tick.
    should_stop: Callable[[], bool] | None = None


@dataclass(frozen=True)
class SingleRunResult:
    """Container with metadata for one completed simulation run."""

    run_id: str
    seed: int | None
    final_state: SimulationState
    ticks_completed: int
    checkpoint_paths: list[Path]


@dataclass(frozen=True)
class MultiRunResult:
    """Aggregated result payload for a batch of simulation runs."""

    runs: list[SingleRunResult]
    aggregate: dict[str, Any]


class CheckpointStore(Protocol):
    """Persistence interface used by the runner for checkpoint/resume."""

    def save(self, state: SimulationState, *, run_id: str, round_number: int) -> Path:
        """Persist the current state and return the written checkpoint path."""

    def load(self, reference: str | Path) -> SimulationState:
        """Restore a previously persisted simulation state."""


#: Welche Perzentile ein Band trägt. **Median plus ein 80-Prozent-Intervall** —
#: nicht Minimum und Maximum: Die Ränder einer Stichprobe wandern mit jeder
#: weiteren Wiederholung nach außen, ein Perzentil tut das nicht. Ein Band aus
#: min/max sähe mit fünfzig Läufen breiter aus als mit zehn, ohne dass sich am
#: Modell etwas geändert hätte.
PERZENTILE: tuple[int, ...] = (10, 50, 90)

#: Welche Reihen ein Band bekommen. Die zwei Größen, um die sich der Regelkreis
#: dreht — mehr wäre Ballast im Artefakt, und wer eine dritte braucht, trägt sie
#: hier ein statt eine eigene Auswertung danebenzustellen.
ENSEMBLE_REIHEN: tuple[str, ...] = ("booking_rate", "ticket_price")


def ensemble_baender(run_results: Sequence[SingleRunResult]) -> dict[str, Any]:
    """Perzentile je Tick über mehrere Läufe desselben Rahmens (P2.6).

    **Ohne die echte Ziehung aus P2.1 wäre das sinnlos gewesen**, und der
    Projektplan sagt das seit dem 2026-08-26: Solange die Buchung eine Schwelle
    war, ergaben fünfzig Seeds fünfzig identische Buchungsverläufe. Das Band
    hätte die Streuung des Bevölkerungs-Samplings gezeigt und wäre für die
    Unsicherheit des Modells gehalten worden.

    **Nur volle Ticks kommen ins Band.** Läufe verschiedener Länge — etwa nach
    einem Abbruch — hätten am Ende ein Perzentil aus zwei statt fünfzig Werten;
    das sähe wie ein zusammenlaufendes Band aus und wäre nur eine dünner
    besetzte Stichprobe. `ticks` sagt deshalb, wie weit das Band trägt.
    """

    if not run_results:
        return {}

    # `float | None`: `booking_rate` ist optional, und eine fehlende Messung reist
    # bis zum Band mit — herausgefiltert wird erst dort, nicht hier (P4.4).
    reihen: dict[str, list[list[float | None]]] = {name: [] for name in ENSEMBLE_REIHEN}
    for ergebnis in run_results:
        werte: dict[str, list[float | None]] = {name: [] for name in ENSEMBLE_REIHEN}
        for eintrag in ergebnis.final_state.price_history:
            werte["booking_rate"].append(eintrag.booking_rate)
            werte["ticket_price"].append(eintrag.price)
        for name, spalte in werte.items():
            reihen[name].append(spalte)

    ticks = min((len(spalte) for spalte in reihen[ENSEMBLE_REIHEN[0]]), default=0)
    if ticks == 0:
        return {}

    baender: dict[str, Any] = {
        "laeufe": len(run_results),
        "ticks": ticks,
        "perzentile": list(PERZENTILE),
        "reihen": {},
    }
    for name, spalten in reihen.items():
        # Ein Lauf ohne Wert an dieser Stelle (`booking_rate` ist optional)
        # fällt heraus, statt als 0 in das Perzentil einzugehen — eine fehlende
        # Messung ist keine Messung von null.
        je_tick = [
            sorted(v for v in (spalte[i] for spalte in spalten) if v is not None)
            for i in range(ticks)
        ]
        baender["reihen"][name] = {
            f"p{p}": [_perzentil(werte, p) for werte in je_tick] for p in PERZENTILE
        }
    return baender


def _perzentil(sortiert: Sequence[float], p: int) -> float | None:
    """Lineare Interpolation zwischen den Rängen — ohne numpy-Import hier.

    Bei einer einzigen Messung liefern alle Perzentile denselben Wert. Das ist
    richtig und sichtbar: Ein Band aus einem Lauf ist eine Linie.
    """

    if not sortiert:
        return None
    if len(sortiert) == 1:
        return float(sortiert[0])
    stelle = (len(sortiert) - 1) * (p / 100.0)
    unten = int(stelle)
    oben = min(unten + 1, len(sortiert) - 1)
    anteil = stelle - unten
    return float(sortiert[unten] * (1.0 - anteil) + sortiert[oben] * anteil)


class SimulationRunner:
    def __init__(self, llm: LLMCallable, options: RunnerOptions | None = None) -> None:
        self.llm = llm
        self.options = options or RunnerOptions()

    def build_graph(
        self, agents: list[AgentConfig]
    ) -> Callable[[SimulationState], SimulationState]:
        # LangGraph ist optional; wenn nicht vorhanden, liefern wir einen deterministischen Runner-Fallback.
        try:
            from langgraph.graph import END, StateGraph  # type: ignore
        except Exception:
            return self._build_sequential_runner(agents)

        orchestrator = OrchestratorNode(agents)
        round_execution = self._build_round_execution(agents)
        market_node = MarketNode()
        environment_node = EnvironmentNode(
            prefer_agent_order=orchestrator.ordered_agent_ids()[::-1],
            llm=self.llm,
        )

        # LangGraph arbeitet intern mit dict-State; wir halten die Public-API als SimulationState.
        def _wrap(node_fn: Callable[[SimulationState], SimulationState]) -> Callable[[dict], dict]:
            def _inner(payload: dict) -> dict:
                state_in = SimulationState(**payload)
                state_out = node_fn(state_in)
                return state_out.model_dump()

            return _inner

        # LangGraphs eigene Typen erlauben als Zustand nur TypedDict, Dataclass oder
        # BaseModel. Der Graph arbeitet hier **bewusst** über `dict` (siehe `_wrap`
        # oben), und die Suite prüft es zur Laufzeit. `Any` statt einer Ausnahme je
        # `add_node`, damit die Begründung an **einer** Stelle steht (P4.4).
        graph: Any = StateGraph(dict)  # type: ignore[type-var]
        graph.add_node("orchestrator", _wrap(orchestrator.invoke))
        graph.add_node("round_execution", _wrap(round_execution.invoke))
        if self.options.enable_market:
            graph.add_node("market", _wrap(market_node.invoke))
        graph.add_node("environment", _wrap(environment_node.invoke))

        graph.set_entry_point("orchestrator")

        graph.add_edge("orchestrator", "round_execution")
        graph.add_edge("round_execution", "environment")
        if self.options.enable_market:
            graph.add_edge("environment", "market")

        def _should_continue(payload: dict) -> str:
            state = SimulationState(**payload)
            return "orchestrator" if state.clock.current_tick < state.clock.max_ticks else END

        tick_end = "market" if self.options.enable_market else "environment"
        graph.add_conditional_edges(tick_end, _should_continue)

        compiled = graph.compile()

        def _run(state: SimulationState) -> SimulationState:
            out = compiled.invoke(state.model_dump())
            return SimulationState(**out)

        return _run

    def run(
        self,
        state: SimulationState | None = None,
        *,
        seed: int | None = None,
        checkpoint_store: CheckpointStore | None = None,
        resume_from: str | Path | None = None,
        run_id: str = "run-0",
    ) -> SimulationState:
        """Run a single simulation to completion.

        The method executes the simulation round by round so that checkpoints can be
        written after every completed round.
        """

        if resume_from is not None:
            if checkpoint_store is None:
                raise ValueError("checkpoint_store is required when resume_from is provided")
            state = checkpoint_store.load(resume_from)
        elif state is None:
            state = build_initial_state(load_cib=self.options.enable_cib)

        state = state.model_copy(deep=True)
        if not self.options.enable_cib:
            state.cib_matrix = None

        # Der Seed wird hier **einmal** aufgelöst und in den State geschrieben.
        # Vorher blieb er `None`, wenn ihn niemand nannte — die Bevölkerung zog
        # trotzdem reproduzierbar, weil `environment_node` still auf 42
        # zurückfiel. Das Artefakt schrieb daraufhin `seed: null` und die
        # Oberfläche nannte den Lauf "frei", obwohl zwei Wiederholungen
        # bitgleich waren. Wer ab hier den Seed liest — Bevölkerung, Metadaten,
        # Dashboard —, liest denselben Wert.
        if seed is not None:
            state.config.seed = seed
        elif state.config.seed is None:
            state.config.seed = DEFAULT_SEED

        validate_state(state)

        # **Was über den letzten Stützpunkt hinausläuft, sagt es** (P2.8,
        # Restposition). Kein Fehler und deshalb nicht in `validate_state`: Eine
        # Stufenfunktion hält hinter ihrem letzten Punkt korrekt den letzten Wert,
        # und bei einer CO₂-Abgabe, die ihren Endwert erreicht hat, ist genau das
        # gemeint. Unsichtbar war es trotzdem — der Backtest rechnete 90 von 120
        # Ticks mit eingefrorener Bevölkerung, ohne dass irgendwo etwas stand.
        for luecke in horizontluecken(state.resolved_properties(), max_ticks=state.clock.max_ticks):
            _LOG.info("Trajektorien-Horizont: %s", luecke)

        # Der Fingerabdruck der Eingaben, genommen **bevor** ein Tick etwas
        # daran verschiebt. Beim Fortsetzen aus einem Checkpoint steht er schon
        # da und bleibt stehen: Der Lauf setzt dieselbe Konfiguration fort, und
        # die Faktoren des Checkpoints sind bereits Ergebnis, nicht Eingabe.
        if state.config_fingerprint is None:
            state.config_fingerprint = config_fingerprint(state)

        self._progress_started_at = time.perf_counter()
        self._progress_last_tick_at = self._progress_started_at

        state = self._run_to_completion(
            state,
            checkpoint_store=checkpoint_store,
            run_id=run_id,
        )
        # Die reine Rechenzeit, ohne das Schreiben der Artefakte danach — das
        # ist die Zahl, aus der sich ein nächster Lauf abschätzen lässt
        # (P1.9-W4.3). `perf_counter` und nicht die Uhrzeit: Sie misst Dauer,
        # nicht Tageszeit, und kippt nicht bei einer Zeitumstellung.
        state.elapsed_seconds = round(time.perf_counter() - self._progress_started_at, 3)
        validate_state(state)
        return state

    def run_multi(
        self,
        runs: int,
        *,
        base_state: SimulationState | None = None,
        seeds: Sequence[int] | None = None,
        checkpoint_store: CheckpointStore | None = None,
    ) -> MultiRunResult:
        """Execute multiple isolated runs with deterministic seed assignment."""

        if runs < 1:
            raise ValueError("runs must be >= 1")

        base_state = (
            base_state or build_initial_state(load_cib=self.options.enable_cib)
        ).model_copy(deep=True)
        if not self.options.enable_cib:
            base_state.cib_matrix = None
        # Derselbe Standard wie im Einzellauf. Bis 2026-08-27 stand hier `or 0`:
        # Ein Multi-Run ohne genannten Seed begann seine Folge bei 0, ein
        # Einzellauf rechnete mit `DEFAULT_SEED` — derselbe Aufbau lieferte je
        # nach Pfad andere Zahlen, ohne dass irgendwo stand, warum. Die Vielfalt
        # der Wiederholungen kommt aus `base_seed + index`, nicht aus dem
        # fehlenden Seed; sie bleibt davon unberührt. Gewonnen ist dabei, dass
        # die **erste** Wiederholung jetzt derselbe Lauf ist wie ein Einzellauf.
        #
        # `is None` statt `or`: Ein ausdrücklich gesetzter Seed 0 ist eine
        # Angabe, kein fehlender Wert.
        base_seed = base_state.config.seed if base_state.config.seed is not None else DEFAULT_SEED
        resolved_seeds = self._resolve_seeds(runs=runs, seeds=seeds, base_seed=base_seed)

        run_results: list[SingleRunResult] = []
        for index, run_seed in enumerate(resolved_seeds, start=1):
            run_state = base_state.model_copy(deep=True)
            run_state.config.seed = run_seed
            run_id = f"run-{index:03d}"
            final_state = self.run(
                run_state,
                seed=run_seed,
                checkpoint_store=checkpoint_store,
                run_id=run_id,
            )
            # Ensure at least one checkpoint exists for this run: some environments
            # or failures may prevent per-round saves from being written. As a
            # safeguard, persist the final state as a checkpoint if the store is
            # available and no checkpoints were recorded for this run.
            if checkpoint_store is not None:
                try:
                    existing = []
                    list_fn = getattr(checkpoint_store, "list_checkpoints", None)
                    if callable(list_fn):
                        existing = list_fn(run_id)
                    latest_fn = getattr(checkpoint_store, "latest_checkpoint", None)
                    latest = latest_fn(run_id) if callable(latest_fn) else None
                    if not existing and latest is None:
                        checkpoint_store.save(
                            final_state, run_id=run_id, round_number=final_state.clock.current_tick
                        )
                except Exception:
                    # Non-fatal: we do not want checkpoint write issues to stop
                    # the multi-run aggregation; they will be visible in logs.
                    pass
            run_results.append(
                SingleRunResult(
                    run_id=run_id,
                    seed=run_seed,
                    final_state=final_state,
                    ticks_completed=final_state.clock.current_tick,
                    checkpoint_paths=self._checkpoint_paths_from_store(checkpoint_store, run_id),
                )
            )

        return MultiRunResult(runs=run_results, aggregate=self.aggregate_runs(run_results))

    def aggregate_runs(self, run_results: Sequence[SingleRunResult]) -> dict[str, Any]:
        """Build a deterministic summary across multiple runs.

        **Bis P2.6 zählte diese Funktion nur Buchhaltung** — wie viele Läufe,
        welche Seeds, wie viele Ereignisse. Über das, wofür man mehrere Läufe
        rechnet, sagte sie nichts: Ein Ensemble ohne Verteilung ist eine teure
        Art, denselben Punktwert mehrfach zu bekommen.

        Seit P2.6 kommt `baender` dazu — Perzentile je Tick über alle Läufe.
        Das ist der Unterschied zwischen «Yields fallen um 11 %» und «Yields
        fallen um 8 bis 14 %»: eine Behauptung gegen eine Aussage.
        """

        if not run_results:
            return {
                "run_count": 0,
                "seeds": [],
                "ticks_completed": [],
                "total_events": 0,
                "total_round_results": 0,
                "baender": {},
            }

        return {
            "run_count": len(run_results),
            "seeds": [result.seed for result in run_results],
            "ticks_completed": [result.ticks_completed for result in run_results],
            "total_events": sum(len(result.final_state.event_log) for result in run_results),
            "total_round_results": sum(
                len(result.final_state.round_results) for result in run_results
            ),
            "baender": ensemble_baender(run_results),
        }

    def _build_agent_nodes(self, agents: list[AgentConfig]) -> dict[str, AgentNode]:
        by_type: dict[AgentType, AgentConfig] = {a.agent_type: a for a in agents}

        # Der MVP erwartet genau diese drei Agenten.
        consumer = AgentNode(by_type[AgentType.CONSUMER], llm=self.llm)
        provider = AgentNode(by_type[AgentType.PROVIDER], llm=self.llm)
        regulator = AgentNode(by_type[AgentType.REGULATOR], llm=self.llm)

        return {
            "consumer": consumer,
            "provider": provider,
            "regulator": regulator,
        }

    # `_seed_runtime` ist mit P2.1 entfallen. Sie seedete das stdlib-`random`
    # und den **globalen Legacy**-Zustand von `np.random` — beides benutzt in
    # diesem Projekt niemand. Gezogen wird über `np.random.default_rng`, und
    # eine unabhängige Generator-Instanz lässt sich von `np.random.seed()`
    # nicht beeinflussen. Die Funktion war damit wirkungslos und gefährlich
    # zugleich: Wer neuen Zufallscode schrieb, konnte sich auf sie verlassen.
    #
    # Die Reproduzierbarkeit hängt nicht an ihr. `state.config.seed` wird
    # explizit durchgereicht (`environment_node` → `run_population_tick` →
    # `buchungsstrom`), und `tests/test_buchung_zieht.py` misst nach, dass zwei
    # Läufe mit demselben Seed dieselben Buchungsraten liefern.

    def _resolve_seeds(
        self,
        *,
        runs: int,
        seeds: Sequence[int] | None,
        base_seed: int,
    ) -> list[int]:
        """Resolve a deterministic, per-run seed sequence."""

        if seeds is not None:
            if len(seeds) != runs:
                raise ValueError("seeds must contain exactly one value per run")
            return [int(seed) for seed in seeds]

        return [base_seed + index for index in range(runs)]

    def _checkpoint_paths_from_store(
        self,
        checkpoint_store: CheckpointStore | None,
        run_id: str,
    ) -> list[Path]:
        """Best-effort helper used to keep the run summary serialisable."""

        if checkpoint_store is None:
            return []

        list_checkpoints = getattr(checkpoint_store, "list_checkpoints", None)
        if callable(list_checkpoints):
            paths = list_checkpoints(run_id)
            if paths:
                return [Path(path) for path in paths]

        checkpoint_path = getattr(checkpoint_store, "last_saved_path", None)
        if isinstance(checkpoint_path, Path):
            return [checkpoint_path]

        checkpoint_dir = getattr(checkpoint_store, "checkpoint_dir", None)
        if isinstance(checkpoint_dir, Path):
            return [checkpoint_dir / run_id]

        return []

    def _run_to_completion(
        self,
        state: SimulationState,
        *,
        checkpoint_store: CheckpointStore | None,
        run_id: str,
    ) -> SimulationState:
        """Execute the simulation one round at a time and persist checkpoints."""

        components = self._create_components(state.agents)

        max_ticks = state.clock.max_ticks
        while state.clock.current_tick < max_ticks:
            state = self._run_single_round(state, components)
            tick = state.clock.current_tick

            # **Nach dem Tick gefragt, nicht mittendrin.** Hier ist der Zustand
            # vollständig: Der Lauf bricht mit weniger Ticks ab, als er
            # vorhatte, und schreibt seine Artefakte wie jeder unvollständige
            # Lauf. `ticks_completed < ticks_max` sagt hinterher, dass er nicht
            # durchgelaufen ist — dieselbe Kennung wie bei einem Absturz.
            if self.options.should_stop is not None and self.options.should_stop():
                if self.options.verbose_ticks:
                    print(f"Abgebrochen nach Tick {tick} von {max_ticks}.")
                break

            # Save individual history for animation — always write to run_dir,
            # independent of whether a checkpoint_store is configured.
            run_dir = resolve_run_output_dir(run_id)
            if checkpoint_store is not None and hasattr(checkpoint_store, "checkpoint_dir"):
                # Prefer the checkpoint_store's parent dir if available (keeps paths consistent)
                run_dir = checkpoint_store.checkpoint_dir.parent
            append_individuals_history(
                tick,
                state.population_individuals,
                koeffizienten=state.resolved_properties().booking_model,
                run_dir=run_dir,
            )

            if self.options.verbose_ticks:
                self._print_tick_progress(state, tick=tick, max_ticks=max_ticks)
            if checkpoint_store is not None and self._should_save_checkpoint(tick, max_ticks):
                checkpoint_store.save(state, run_id=run_id, round_number=tick)

        return state

    def _should_save_checkpoint(self, tick: int, max_ticks: int) -> bool:
        interval = self.options.checkpoint_interval
        if interval <= 0:
            return False
        return tick % interval == 0 or tick >= max_ticks

    def _print_tick_progress(self, state: SimulationState, *, tick: int, max_ticks: int) -> None:
        metrics = state.market_metrics
        price = metrics.get("ticket_price")
        if price is None and state.price_history:
            price = state.price_history[-1].price
        booking = metrics.get("booking_rate")
        if booking is None and state.price_history:
            booking = state.price_history[-1].booking_rate

        now = time.perf_counter()
        tick_elapsed = now - getattr(self, "_progress_last_tick_at", now)
        total_elapsed = now - getattr(self, "_progress_started_at", now)
        self._progress_last_tick_at = now
        rate = tick / total_elapsed if total_elapsed > 0 else 0.0

        msg = tick_zeile(
            tick,
            max_ticks,
            sekunden=tick_elapsed,
            je_sekunde=rate,
            preis=price,
            buchungsrate=booking,
        )
        print(msg, flush=True)
        callback = self.options.tick_progress_callback
        if callback is not None:
            callback(msg)

    def _create_components(
        self,
        agents: list[AgentConfig],
    ) -> tuple[
        OrchestratorNode,
        ParallelRoundNode | RoundExecutionNode,
        EnvironmentNode,
        AgentNode | None,
        MarketNode,
    ]:
        """Build the reusable nodes that make up one simulation round."""

        orchestrator = OrchestratorNode(agents)
        round_execution = self._build_round_execution(agents)
        market_node = MarketNode()
        environment_node = EnvironmentNode(
            prefer_agent_order=orchestrator.ordered_agent_ids()[::-1],
            llm=self.llm,
        )
        consumer_config = next((agent for agent in agents if agent.id == "consumer"), None)
        consumer_node = (
            AgentNode(consumer_config, llm=self.llm)
            if consumer_config is not None and not self.options.enable_redebedarf
            else None
        )
        return orchestrator, round_execution, environment_node, consumer_node, market_node

    def _run_single_round(
        self,
        state: SimulationState,
        components: tuple[
            OrchestratorNode,
            ParallelRoundNode | RoundExecutionNode,
            EnvironmentNode,
            AgentNode | None,
            MarketNode,
        ],
    ) -> SimulationState:
        """Run a single deterministic round using the configured nodes."""

        from src.market.factor_dynamics import (
            apply_factor_rules_at_tick_start,
            record_factor_timeseries,
        )
        from src.orchestration.event_deltas import write_events_from_deltas

        orchestrator, round_execution, environment_node, consumer_node, market_node = components
        state = orchestrator.invoke(state)
        state = apply_factor_rules_at_tick_start(state)
        if not self.options.deterministic_only:
            state = round_execution.invoke(state)
        state = environment_node.invoke(state)
        if consumer_node is not None and not self.options.deterministic_only:
            state = consumer_node.invoke(state)
            state = environment_node.apply_consumer_factor_updates(state)
        if self.options.enable_market:
            state = market_node.invoke(state)
        state = record_factor_timeseries(state)
        return write_events_from_deltas(state)

    def _build_round_execution(
        self,
        agents: list[AgentConfig],
    ) -> ParallelRoundNode | RoundExecutionNode:
        if self.options.enable_redebedarf:
            return RoundExecutionNode(agents, llm=self.llm)
        return ParallelRoundNode(agents, llm=self.llm)

    def _build_sequential_runner(
        self, agents: list[AgentConfig]
    ) -> Callable[[SimulationState], SimulationState]:
        components = self._create_components(agents)

        def _run(state: SimulationState) -> SimulationState:
            while state.clock.current_tick < state.clock.max_ticks:
                state = self._run_single_round(state, components)
            return state

        return _run
