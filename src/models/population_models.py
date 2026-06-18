from pydantic import BaseModel, Field

from src.models.enums import DistributionType


class DistributionConfig(BaseModel):
    type: DistributionType = DistributionType.NORMAL
    mean: float = 0.5
    std_dev: float = 0.1
    min_value: float = 0.0
    max_value: float = 1.0


class ConsumerSegment(BaseModel):
    id: str
    name: str
    share: float
    price_elasticity: DistributionConfig = DistributionConfig()
    income_level: DistributionConfig = DistributionConfig()
    environmental_awareness: DistributionConfig = DistributionConfig()
    description: str = ""


class PopulationConfig(BaseModel):
    segments: list[ConsumerSegment]
    total_population: int = 1000
    default_distribution: DistributionType = DistributionType.NORMAL


# Fallback-Mapping für Legacy-Segmentnamen (agents.json → properties.json label-IDs)
SEGMENT_LABEL_MAP: dict[str, str] = {
    "business": "business",
    "leisure_price_sensitive": "price_sensitive",
    "leisure_eco_conscious": "eco_conscious",
}


class Individual(BaseModel):
    id: int
    age: int
    labels: dict[str, bool] = Field(default_factory=dict)
    wtp_eur: float
    environmental_awareness: float
    substitution_readiness: float = 0.5
    price_sensitivity: float
    base_income_factor: float = 1.0
    income_factor: float = 1.0
    booked: bool = False
    applied_shift_rules: list[str] = Field(default_factory=list)
    last_booked_tick: int | None = None

