from typing import Any

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
    saturation_level: float = Field(default=0.0, ge=0.0, le=1.0)


class SegmentStats(BaseModel):
    segment_id: str
    share: float
    total_individuals: int
    booked_individuals: int
    booking_rate: float
    avg_income_factor: float = 1.0


class AgeGroupStats(BaseModel):
    age_group: str
    total_individuals: int
    booked_individuals: int
    booking_rate: float
    avg_wtp: float
    avg_income_factor: float
    avg_awareness: float


class PopulationStats(BaseModel):
    total_population: int
    total_booked: int
    total_demand: float
    avg_income_factor: float = 1.0
    segments: dict[str, SegmentStats]
    age_groups: dict[str, AgeGroupStats] = Field(default_factory=dict)


class PopulationShift(BaseModel):
    """Population shift for one segment."""

    segment_id: str
    segment_name: str
    old_share: float
    new_share: float
    shift_amount: float
    reasoning: str
    clamped: bool = False


class PopulationUpdateResult(BaseModel):
    """Result of a population update."""

    round_number: int
    shifts: list[PopulationShift] = Field(default_factory=list)
    total_reasoning: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
