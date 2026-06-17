from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, model_validator

from src.models.enums import DistributionType


class SetEffect(BaseModel):
    type: Literal["set"] = "set"
    value: float


class RampEffect(BaseModel):
    type: Literal["ramp"] = "ramp"
    value: float
    duration_ticks: int = 1


TrajectoryEffect = Annotated[Union[SetEffect, RampEffect], Field(discriminator="type")]


class TrajectoryRule(BaseModel):
    active_from_tick: int
    effect: TrajectoryEffect


class StepPoint(BaseModel):
    tick: int
    value: float


class BaselineTrajectory(BaseModel):
    """Constant baseline with optional tick-based overrides (set / ramp)."""

    baseline: float = 0.0
    rules: list[TrajectoryRule] = Field(default_factory=list)


class StepFunctionTrajectory(BaseModel):
    type: Literal["step_function"] = "step_function"
    points: list[StepPoint] = Field(default_factory=list)


TrajectoryConfig = Union[BaselineTrajectory, StepFunctionTrajectory]


class SystemProperty(BaseModel):
    id: str
    type: Literal["numeric", "integer", "boolean"] = "numeric"
    unit: str = ""
    description: str = ""
    source: Literal["trajectory", "runtime", "computed"] = "trajectory"
    price_component_type: Literal["none", "tax", "fee"] = "none"
    min_value: float | None = None
    max_value: float | None = None
    trajectory: BaselineTrajectory | StepFunctionTrajectory = Field(
        default_factory=BaselineTrajectory
    )

    @model_validator(mode="before")
    @classmethod
    def _parse_trajectory(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        trajectory = data.get("trajectory")
        if not isinstance(trajectory, dict):
            return data
        if trajectory.get("type") == "step_function":
            data["trajectory"] = StepFunctionTrajectory.model_validate(trajectory)
        else:
            data["trajectory"] = BaselineTrajectory.model_validate(trajectory)
        return data


class IndividualProperty(BaseModel):
    id: str
    type: Literal["boolean", "distribution", "numeric"] = "boolean"
    prevalence: float | None = None
    enabled: bool = True
    distribution: DistributionType | None = None
    mean: float | None = None
    std_dev: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    alpha: float | None = None
    beta: float | None = None


class ShiftRule(BaseModel):
    """M3/M4 placeholder for population shift rules."""

    id: str = ""
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)
    once: bool = False


class FactorRuleEffect(BaseModel):
    """M5: set a factor to a concrete descriptor state."""

    set_state: str


class FactorRule(BaseModel):
    """M5: deterministic factor transition from runtime metrics / properties."""

    id: str
    factor_id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: FactorRuleEffect
    priority: int = 0
    once: bool = False


class RegulatoryInfluence(BaseModel):
    """M6: One EU/national regulatory cost driver (e.g. EU-ETS, RefuelEU)."""

    id: str
    description: str = ""
    cost_contribution: float = 0.0
    when: dict[str, Any] = Field(default_factory=dict)
    trajectory: BaselineTrajectory | StepFunctionTrajectory = Field(
        default_factory=BaselineTrajectory
    )

    @model_validator(mode="before")
    @classmethod
    def _parse_trajectory(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        trajectory = data.get("trajectory")
        if not isinstance(trajectory, dict):
            return data
        if trajectory.get("type") == "step_function":
            data["trajectory"] = StepFunctionTrajectory.model_validate(trajectory)
        else:
            data["trajectory"] = BaselineTrajectory.model_validate(trajectory)
        return data


class PriceCoefficientsConfig(BaseModel):
    """M4.13: configurable cost/price formula weights (no magic numbers in code)."""

    carbon_per_tonne: float = 0.001
    saf_premium_factor: float = 0.5
    min_ticket_price: float = 1.0
    margin_reference_fraction: float = 0.08
    margin_floor_fraction: float = 0.05
    target_booking_tolerance: float = 0.9


class PriceModelConfig(BaseModel):
    """M4: ticket cost from fixed base + policy properties (no compounding on prior price)."""

    base_price: float = 100.0
    initial_markup: float = 0.0
    compound_fuel_on_cost: bool = True
    coefficients: PriceCoefficientsConfig = Field(default_factory=PriceCoefficientsConfig)
    cost_properties: list[str] = Field(
        default_factory=lambda: [
            "fuel_price_change",
            "carbon_tax_level",
            "oil_price_index",
            "saf_mandate_share",
            "efuel_subsidy",
        ]
    )


class MarketFeedbackConfig(BaseModel):
    """M4: provider markup adjusts toward target booking rate."""

    enabled: bool = True
    target_booking_rate: float = 0.84
    markup_adjustment_per_tick: float = 0.06
    max_price_change_fraction: float = 0.08
    damping: float = 0.85
    booking_weight: float = 0.6


class MarketRule(BaseModel):
    """M4.13: declarative market feedback (same when/effect pattern as shift_rules)."""

    id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)


class PropertiesConfig(BaseModel):
    system_properties: list[SystemProperty] = Field(default_factory=list)
    individual_properties: list[IndividualProperty] = Field(default_factory=list)
    shift_rules: list[ShiftRule] = Field(default_factory=list)
    factor_rules: list[FactorRule] = Field(default_factory=list)
    regulatory_influences: list[RegulatoryInfluence] = Field(default_factory=list)
    market_rules: list[MarketRule] = Field(default_factory=list)
    price_model: PriceModelConfig = Field(default_factory=PriceModelConfig)
    market_feedback: MarketFeedbackConfig = Field(default_factory=MarketFeedbackConfig)

    def system_property_ids(self) -> list[str]:
        return [prop.id for prop in self.system_properties]

    def get_system_property(self, prop_id: str) -> SystemProperty | None:
        for prop in self.system_properties:
            if prop.id == prop_id:
                return prop
        return None
