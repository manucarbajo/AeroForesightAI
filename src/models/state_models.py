from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from src.models.population_models import ScenarioParameter


class FactorState(BaseModel):
    id: str
    name: str
    description: str
    current_state: str
    possible_states: dict[str, str]


class ConfigChangeEntry(BaseModel):
    """Timestamped record of a runtime configuration change."""

    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    round_number: int | None = None
    parameter_id: str
    old_value: Any
    new_value: Any
    source_agent: str = "EnvironmentAgent"
    reason: str = ""


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

    current_round: int = 0
    max_rounds: int = 40
    tick_unit: str = "tick"

    def tick_label_for_round(self, round_number: int) -> str:
        """Return the display label for a 1-based tick index."""

        if round_number < 1:
            raise ValueError("round_number must be >= 1")
        return f"Tick {round_number}"


class LLMConfig(BaseModel):
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048


class SimulationConfig(BaseModel):
    name: str
    description: str
    clock: SimulationClock
    llm: LLMConfig = LLMConfig()
    seed: int | None = None
    scenario_parameters: list[ScenarioParameter] = Field(default_factory=list)
    change_log: list[ConfigChangeEntry] = Field(default_factory=list)

    def update_scenario_parameter(
        self,
        parameter_id: str,
        new_value: float,
        *,
        source_agent: str = "EnvironmentAgent",
        reason: str = "",
        round_number: int | None = None,
    ) -> None:
        """Update a scenario parameter and append a timestamped change log entry."""

        for parameter in self.scenario_parameters:
            if parameter.id != parameter_id:
                continue

            old_value = parameter.value
            parameter.value = new_value
            self.change_log.append(
                ConfigChangeEntry(
                    round_number=round_number,
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


class InputState(BaseModel):
    """Studio-facing input defaults for AP3 runs."""

    max_rounds: int = Field(default=40, description="Maximale Anzahl an Ticks")
    rounds: int = Field(default=4, description="Alias für max_rounds")
    seed: int | None = Field(default=None, description="Seed für Multi-Run")
    llm_model: str = Field(default="llama3.2", description="LLM-Modellname")
    llm_temperature: float = Field(default=0.7, description="LLM-Temperatur")
    llm_max_tokens: int = Field(default=2048, description="Maximale Token pro Antwort")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama-Base-URL")
    scenario_parameters: list[dict[str, Any]] = Field(default_factory=list, description="Szenarioparameter")


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


# deferred imports for forward refs
from src.models.agent_models import AgentConfig  # noqa: E402
from src.models.cib_models import CIBMatrix, CIBMatrixHistory  # noqa: E402
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult  # noqa: E402

SimulationState.model_rebuild()
