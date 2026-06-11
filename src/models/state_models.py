from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from src.models.population_models import ScenarioParameter

class FactorState(BaseModel):
    id: str
    name: str
    description: str
    current_state: str
    possible_states: dict[str, str]


class EnvironmentState(BaseModel):
    factors: dict[str, FactorState]
    global_context: str = ""


class SpeechCandidateState(BaseModel):
    """Serialized speech candidate emitted by the RedebedarfScheduler."""

    agent_id: str
    score: int
    reasons: list[str] = Field(default_factory=list)
    contributions_this_round: int = 0


class SpeechPlanState(BaseModel):
    """Round-level speech plan generated before agent execution."""

    round_number: int
    order: list[str] = Field(default_factory=list)
    candidates: list[SpeechCandidateState] = Field(default_factory=list)
    scores: dict[str, int] = Field(default_factory=dict)


class SimulationClock(BaseModel):
    """Discrete simulation clock. One tick is one tick.  No calendar mapping."""

    current_tick: int = 0
    max_ticks: int = 40
    tick_unit: str = "tick"

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_fields(cls, data: Any) -> Any:
        """Accept legacy ``current_round`` / ``max_rounds`` keys from older checkpoints."""

        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "current_tick" not in normalized and "current_round" in normalized:
            normalized["current_tick"] = normalized["current_round"]
        if "max_ticks" not in normalized and "max_rounds" in normalized:
            normalized["max_ticks"] = normalized["max_rounds"]
        return normalized

    def tick_label(self, tick: int) -> str:
        """Return the display label for a 1-based tick index."""

        if tick < 1:
            raise ValueError("tick must be >= 1")
        return f"Tick {tick}"


class LLMConfig(BaseModel):
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048


class ConfigChangeEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    tick_number: int | None = None
    parameter_id: str
    old_value: Any
    new_value: Any
    source_agent: str = "EnvironmentAgent"
    reason: str = ""


class PolicyEntry(BaseModel):
    """One policy shock: from ``tick`` onward, set ``parameter`` to ``value``."""

    tick: int
    parameter: str
    value: float


class SimulationConfig(BaseModel):
    name: str
    description: str
    llm: LLMConfig = LLMConfig()
    seed: int | None = None
    policy_schedule: list[PolicyEntry] = Field(default_factory=list)
    scenario_parameters: list[ScenarioParameter] = Field(default_factory=list)
    change_log: list[ConfigChangeEntry] = Field(default_factory=list)

    def update_scenario_parameter(
        self,
        parameter_id: str,
        new_value: float,
        *,
        source_agent: str = "EnvironmentAgent",
        reason: str = "",
        tick_number: int | None = None,
    ) -> None:
        for parameter in self.scenario_parameters:
            if parameter.id != parameter_id:
                continue

            old_value = parameter.value
            parameter.value = new_value
            self.change_log.append(
                ConfigChangeEntry(
                    tick_number=tick_number,
                    parameter_id=parameter_id,
                    old_value=old_value,
                    new_value=new_value,
                    source_agent=source_agent,
                    reason=reason,
                )
            )
            return

        raise KeyError(f"Unknown scenario parameter: {parameter_id}")

    def runtime_parameter_map(self) -> dict[str, float]:
        """Return the current scenario parameters as a flat runtime mapping."""

        return {parameter.id: parameter.value for parameter in self.scenario_parameters}


class SimulationState(BaseModel):
    config: SimulationConfig
    clock: SimulationClock
    environment: EnvironmentState
    agents: list[AgentConfig]
    redebedarf_scores: dict[str, int] = Field(default_factory=dict)
    current_speech_candidates: list[SpeechCandidateState] = Field(default_factory=list)
    current_speech_order: list[str] = Field(default_factory=list)
    current_round_spoken_agents: list[str] = Field(default_factory=list)
    speech_plan: SpeechPlanState | None = None
    event_log: list[EventLogEntry] = Field(default_factory=list)
    price_history: list[PriceHistoryEntry] = Field(default_factory=list)
    round_results: list[RoundResult] = Field(default_factory=list)
    cib_matrix: CIBMatrix | None = None
    cib_history: CIBMatrixHistory | None = None
    market_metrics: dict[str, float] = Field(default_factory=dict)
    population_stats: list[dict[str, Any]] = Field(default_factory=list)

class InputState(BaseModel):
    """Studio-facing input defaults for AP3 runs."""

    max_rounds: int = Field(default=40, description="Maximale Anzahl an Ticks")
    rounds: int = Field(default=4, description="Alias für max_rounds")
    seed: int | None = Field(default=None, description="Seed für Multi-Run")
    llm_model: str = Field(default="llama3.2", description="LLM-Modellname")
    llm_temperature: float = Field(default=0.7, description="LLM-Temperatur")
    llm_max_tokens: int = Field(default=2048, description="Maximale Token pro Antwort")
    enable_redebedarf: bool = Field(
        default=False,
        description="C3 Redebedarf-Scheduler statt paralleler Agenten pro Tick",
    )
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama-Base-URL")


class PlaygroundState(InputState):
    """Graph state schema tolerant to partial/empty Studio payloads."""

    config: dict[str, Any] | None = Field(default=None)
    clock: dict[str, Any] | None = Field(default=None)
    environment: dict[str, Any] | None = Field(default=None)
    agents: list[dict[str, Any]] | None = Field(default=None)

    event_log: list[dict[str, Any]] = Field(default_factory=list)
    price_history: list[dict[str, Any]] = Field(default_factory=list)
    round_results: list[dict[str, Any]] = Field(default_factory=list)
    cib_matrix: dict[str, Any] | None = Field(default=None)
    cib_history: dict[str, Any] | None = Field(default=None)

    redebedarf_scores: dict[str, int] = Field(default_factory=dict)
    current_speech_candidates: list[SpeechCandidateState] = Field(default_factory=list)
    current_speech_order: list[str] = Field(default_factory=list)
    current_round_spoken_agents: list[str] = Field(default_factory=list)
    speech_plan: SpeechPlanState | None = Field(default=None)
    market_metrics: dict[str, float] = Field(default_factory=dict)


# deferred imports for forward refs
from src.models.agent_models import AgentConfig  # noqa: E402
from src.models.cib_models import CIBMatrix, CIBMatrixHistory  # noqa: E402
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult  # noqa: E402

SimulationState.model_rebuild()
