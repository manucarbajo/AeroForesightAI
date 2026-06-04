from __future__ import annotations

from dataclasses import dataclass
import random
from pathlib import Path
import sys
from typing import Any, Callable, Protocol, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config_loader import build_initial_state
from src.models.agent_models import AgentConfig
from src.models.enums import AgentType
from src.models.state_models import SimulationState
from src.nodes.agent_node import AgentNode, LLMCallable
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.nodes.redebedarf_node import RoundExecutionNode
from src.validation import validate_state


@dataclass(frozen=True)
class RunnerOptions:
    enable_market: bool = True
    enable_cib: bool = True  # load frozen CIB from configs/cib_frozen.json


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


class SimulationRunner:
    def __init__(self, llm: LLMCallable, options: RunnerOptions | None = None) -> None:
        self.llm = llm
        self.options = options or RunnerOptions()

    def build_graph(self, agents: list[AgentConfig]) -> Callable[[SimulationState], SimulationState]:
        # LangGraph ist optional; wenn nicht vorhanden, liefern wir einen deterministischen Runner-Fallback.
        try:
            from langgraph.graph import END, StateGraph  # type: ignore
        except Exception:
            return self._build_sequential_runner(agents)

        orchestrator = OrchestratorNode(agents)
        round_execution = RoundExecutionNode(agents, llm=self.llm)
        market_node = MarketNode()
        environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])

        # LangGraph arbeitet intern mit dict-State; wir halten die Public-API als SimulationState.
        def _wrap(node_fn: Callable[[SimulationState], SimulationState]) -> Callable[[dict], dict]:
            def _inner(payload: dict) -> dict:
                state_in = SimulationState(**payload)
                state_out = node_fn(state_in)
                return state_out.model_dump()

            return _inner

        graph = StateGraph(dict)
        graph.add_node("orchestrator", _wrap(orchestrator.invoke))
        graph.add_node("round_execution", _wrap(round_execution.invoke))
        if self.options.enable_market:
            graph.add_node("market", _wrap(market_node.invoke))
        graph.add_node("environment", _wrap(environment_node.invoke))

        graph.set_entry_point("orchestrator")

        graph.add_edge("orchestrator", "round_execution")
        if self.options.enable_market:
            graph.add_edge("round_execution", "market")
            graph.add_edge("market", "environment")
        else:
            graph.add_edge("round_execution", "environment")

        def _should_continue(payload: dict) -> str:
            state = SimulationState(**payload)
            return "orchestrator" if state.clock.current_tick < state.clock.max_ticks else END

        graph.add_conditional_edges("environment", _should_continue)

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
        if seed is not None:
            state.config.seed = seed

        self._seed_runtime(seed if seed is not None else state.config.seed)
        validate_state(state)

        state = self._run_to_completion(
            state,
            checkpoint_store=checkpoint_store,
            run_id=run_id,
        )
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

        base_state = (base_state or build_initial_state(load_cib=self.options.enable_cib)).model_copy(deep=True)
        if not self.options.enable_cib:
            base_state.cib_matrix = None
        base_seed = base_state.config.seed or 0
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
                        checkpoint_store.save(final_state, run_id=run_id, round_number=final_state.clock.current_tick)
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
        """Build a deterministic summary across multiple runs."""

        if not run_results:
            return {
                "run_count": 0,
                "seeds": [],
                "ticks_completed": [],
                "total_events": 0,
                "total_round_results": 0,
            }

        return {
            "run_count": len(run_results),
            "seeds": [result.seed for result in run_results],
            "ticks_completed": [result.ticks_completed for result in run_results],
            "total_events": sum(len(result.final_state.event_log) for result in run_results),
            "total_round_results": sum(len(result.final_state.round_results) for result in run_results),
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

    def _seed_runtime(self, seed: int | None) -> None:
        """Seed local runtime randomness for reproducible multi-run execution."""

        if seed is None:
            return

        random.seed(seed)
        try:
            import numpy as np  # type: ignore

            np.random.seed(seed)
        except Exception:
            pass

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

        while state.clock.current_tick < state.clock.max_ticks:
            state = self._run_single_round(state, components)
            if checkpoint_store is not None:
                checkpoint_store.save(state, run_id=run_id, round_number=state.clock.current_tick)

        return state

    def _create_components(
        self,
        agents: list[AgentConfig],
    ) -> tuple[OrchestratorNode, RoundExecutionNode, MarketNode, EnvironmentNode]:
        """Build the reusable nodes that make up one simulation round."""

        orchestrator = OrchestratorNode(agents)
        round_execution = RoundExecutionNode(agents, llm=self.llm)
        market_node = MarketNode()
        environment_node = EnvironmentNode(prefer_agent_order=orchestrator.ordered_agent_ids()[::-1])
        return orchestrator, round_execution, market_node, environment_node

    def _run_single_round(
        self,
        state: SimulationState,
        components: tuple[OrchestratorNode, RoundExecutionNode, MarketNode, EnvironmentNode],
    ) -> SimulationState:
        """Run a single deterministic round using the configured nodes."""

        orchestrator, round_execution, market_node, environment_node = components
        state = orchestrator.invoke(state)
        state = round_execution.invoke(state)
        if self.options.enable_market:
            state = market_node.invoke(state)
        state = environment_node.invoke(state)
        return state

    def _build_sequential_runner(self, agents: list[AgentConfig]) -> Callable[[SimulationState], SimulationState]:
        components = self._create_components(agents)

        def _run(state: SimulationState) -> SimulationState:
            while state.clock.current_tick < state.clock.max_ticks:
                state = self._run_single_round(state, components)
            return state

        return _run

