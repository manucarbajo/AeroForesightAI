from __future__ import annotations

from pydantic import BaseModel

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


class SimulationClock(BaseModel):
    current_round: int = 0
    max_rounds: int = 10
    year_start: int = 2025
    years_per_round: int = 1


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
    scenario_parameters: list[ScenarioParameter] = []


class SimulationState(BaseModel):
    config: SimulationConfig
    clock: SimulationClock
    environment: EnvironmentState
    agents: list[AgentConfig]
    event_log: list[EventLogEntry] = []
    price_history: list[PriceHistoryEntry] = []
    round_results: list[RoundResult] = []
    cib_matrix: CIBMatrix | None = None


# deferred imports for forward refs
from src.models.agent_models import AgentConfig  # noqa: E402
from src.models.cib_models import CIBMatrix  # noqa: E402
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult  # noqa: E402

SimulationState.model_rebuild()
