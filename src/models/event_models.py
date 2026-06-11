from pydantic import BaseModel, Field

from src.models.agent_models import AgentResponse
from src.models.enums import EventType
from src.models.state_models import EnvironmentState


class EventLogEntry(BaseModel):
    id: str
    round_number: int
    source_agent: str
    event_type: EventType
    description: str
    affected_factors: list[str] = Field(default_factory=list)
    timestamp: str = ""


class PriceHistoryEntry(BaseModel):
    round_number: int
    agent_id: str
    price: float
    demand_level: float
    booking_rate: float | None = None
    load_factor: float = 0.0


class RoundResult(BaseModel):
    round_number: int
    agent_responses: list[AgentResponse]
    events: list[EventLogEntry]
    environment_snapshot: EnvironmentState
    summary: str = ""
