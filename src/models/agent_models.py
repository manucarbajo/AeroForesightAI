from pydantic import BaseModel

from src.models.enums import AgentType
from src.models.population_models import PopulationConfig


class AgentConfig(BaseModel):
    id: str
    name: str
    agent_type: AgentType
    description: str
    goals: list[str]
    constraints: list[str] = []
    population_config: PopulationConfig | None = None


class StateChange(BaseModel):
    factor_id: str
    proposed_state: str
    reasoning: str


class AgentResponse(BaseModel):
    agent_id: str
    round_number: int
    reasoning: str
    actions: list[str]
    state_changes: list[StateChange] = []
    raw_output: str = ""
