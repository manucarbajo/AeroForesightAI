from pydantic import BaseModel


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
