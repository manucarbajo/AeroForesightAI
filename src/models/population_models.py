from pydantic import BaseModel

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


class ScenarioParameter(BaseModel):
    id: str
    name: str
    description: str = ""
    value: float = 0.0
    unit: str = ""
    min_value: float | None = None
    max_value: float | None = None

