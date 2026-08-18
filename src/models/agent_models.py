from typing import Any

from pydantic import BaseModel, Field

from src.models.enums import AgentType
from src.models.population_models import PopulationConfig


class AgentProfile(BaseModel):
    observes: list[str] = Field(default_factory=list)
    may_propose: list[str] = Field(default_factory=list)
    must_not_output: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)

    @property
    def observed_factors(self) -> list[str]:
        """Extract explicit factor IDs from observes list (e.g., 'factors F1,F5,F6')."""
        factors = []
        for item in self.observes:
            if item.startswith("factors "):
                parts = item.replace("factors ", "").split(",")
                factors.extend([p.strip() for p in parts if p.strip()])
        return factors


class AgentConfig(BaseModel):
    id: str
    name: str
    agent_type: AgentType
    description: str
    goals: list[str]
    constraints: list[str] = []
    population_config: PopulationConfig | None = None
    profile: AgentProfile | None = None


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
    # Optional field: Consumer liefert segmentspezifische qualitative Analyse.
    segment_analysis: dict[str, Any] = Field(default_factory=dict)
    redebedarf_score: int | None = None
    redebedarf_reasons: list[str] = Field(default_factory=list)
    raw_output: str = ""
