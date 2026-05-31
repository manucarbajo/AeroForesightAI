from typing import Any

from pydantic import BaseModel, Field

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
    # Optional field: Consumer liefert segmentspezifische qualitative Analyse.
    segment_analysis: dict[str, Any] = Field(default_factory=dict)
    # Optional: maschinenlesbare Einschätzung von Einflussstärken (-3..+3),
    # z.B. um Diskussion/Protokoll und CIB-Argumentation konsistenter zu machen.
    # Struktur ist absichtlich flexibel (dicts), damit Prompts iterierbar bleiben.
    impact_assessment: list[dict[str, Any]] = Field(default_factory=list)
    redebedarf_score: int | None = None
    redebedarf_reasons: list[str] = Field(default_factory=list)
    raw_output: str = ""
