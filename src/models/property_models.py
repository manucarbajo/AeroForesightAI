from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

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


class SaturationConfig(BaseModel):
    """Continuous saturation after booking (P2.1)."""

    booking_increase: float = 0.6
    utility_penalty_factor: float = 1.0


class IndividualProperty(BaseModel):
    id: str
    type: Literal["boolean", "distribution", "numeric"] = "boolean"
    prevalence: float | None = None
    enabled: bool = True
    exclusive_group: str | None = None
    saturation_decay: float | None = None
    distribution: DistributionType | None = None
    mean: float | None = None
    std_dev: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    alpha: float | None = None
    beta: float | None = None
    modifiers: dict[str, float] = Field(default_factory=dict)


class ShiftRule(BaseModel):
    id: str = ""
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)
    once: bool = False


class FactorRuleEffect(BaseModel):
    set_state: str


class FactorRule(BaseModel):
    """Deterministic factor transition triggered by runtime metrics / system properties."""

    id: str
    factor_id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: FactorRuleEffect
    priority: int = 0
    once: bool = False


class RegulatoryInfluence(BaseModel):
    """One regulatory cost driver (e.g. EU-ETS, RefuelEU) with conditional activation."""

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
    """Configurable cost/price formula weights."""

    carbon_per_tonne: float = 0.001
    saf_premium_factor: float = 0.5
    min_ticket_price: float = 1.0
    margin_reference_fraction: float = 0.08
    margin_floor_fraction: float = 0.05
    target_booking_tolerance: float = 0.9


class PriceModelConfig(BaseModel):
    """Ticket cost from fixed base + policy properties."""

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
    """Provider markup adjusts each tick toward the target booking rate."""

    enabled: bool = True
    # Target share of population booking per tick (calibrated ~DE annual flight rate).
    target_booking_rate: float = 0.37
    markup_adjustment_per_tick: float = 0.08
    max_price_change_fraction: float = 0.08
    damping: float = 0.85
    booking_weight: float = 0.6
    marginal_cost_fraction: float = 0.33


class MarketRule(BaseModel):
    """Declarative market feedback rule (same when/effect pattern as shift_rules)."""

    id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)


class BookingCoefficient(BaseModel):
    """Ein Koeffizient des Buchungsmodells — **mit seiner Herkunft** (P2.1).

    Bis P2.1 standen diese Zahlen als Literale in `booking_probability`. Sie
    bestimmen, wie stark Preis, Abgabe und Bahnalternative gegen den Nutzen
    arbeiten, und damit jede Buchungsrate, die das Produkt ausgibt — ohne dass
    irgendwo stand, woher sie kommen.

    **`quelle` ist Pflicht und trägt zwei Angaben**, weil beide auseinanderfallen:
    die *Funktionsform* (belegt) und der *Zahlenwert* (in diesem Modell
    gesetzt). `docs/research/references.md` sagt es für die Substitution
    ausdrücklich — «keine Standard-Einheitsformel, sondern modellabhängig».
    Eine Literaturangabe an eine handgesetzte Zahl zu heften wäre eine erfundene
    Provenienz, und die ist schlimmer als eine fehlende: Sie sieht aus wie eine
    Kalibrierung.
    """

    wert: float
    quelle: str

    @field_validator("quelle")
    @classmethod
    def _quelle_ist_keine_floskel(cls, v: str) -> str:
        if len(v.strip()) < 20:
            raise ValueError(
                "Die Herkunft eines Koeffizienten braucht einen Satz, kein Stichwort — "
                "sie soll einem Fachprüfer sagen, was belegt ist und was gesetzt."
            )
        return v


class BookingModelConfig(BaseModel):
    """Die Koeffizienten der Buchungsentscheidung (P2.1).

    Sie standen als Literale in `src/population/population_sampler.py`. Hier
    sind sie sichtbar, änderbar und tragen je eine Herkunftsangabe.
    """

    base_utility: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=2.0,
            quelle=(
                "Konstante des Nutzenterms (Ben-Akiva/Lerman 1985, McFadden 1974: "
                "Alternativenspezifische Konstante). Der Wert 2,0 ist in diesem Modell "
                "gesetzt und nicht geschätzt — er legt fest, bei welchem Preisniveau die "
                "Buchungswahrscheinlichkeit durch 0,5 geht."
            ),
        )
    )
    price_reference_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=100.0,
            quelle=(
                "Normierungsgröße, kein Verhaltensparameter: Der Ticketpreis wird darauf "
                "bezogen, damit `price_sensitivity` in einer Größenordnung um 1 liegt. "
                "Gesetzt, nicht geschätzt; verschiebt man sie, verschiebt sich die "
                "Bedeutung jeder Preisempfindlichkeit mit."
            ),
        )
    )
    substitution_weight: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=1.5,
            quelle=(
                "Gewicht der Bahnalternative gegenüber dem reinen Preisterm. Die Form "
                "folgt der diskreten Wahltheorie (Ben-Akiva/Lerman 1985), der Wert ist "
                "in diesem Modell gesetzt: `docs/research/references.md` hält fest, dass "
                "es für Substitutionseffekte keine Standard-Einheitsformel gibt."
            ),
        )
    )
    carbon_reference_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=100.0,
            quelle=(
                "Normierungsgröße für den Teil der CO₂-Abgabe oberhalb des Referenzwerts. "
                "Gesetzt wie `price_reference_eur` und aus demselben Grund."
            ),
        )
    )
    carbon_eco_baseline_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=50.0,
            quelle=(
                "Ab welcher Abgabe ein Umwelt-Malus überhaupt entsteht — der Ausgangswert "
                "von `carbon_tax_level` in der ausgelieferten Konfiguration. Damit ist der "
                "Malus im Startzustand null und misst die Veränderung, nicht das Niveau."
            ),
        )
    )
    green_premium: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.1,
            quelle=(
                "Aufschlag auf die Zahlungsbereitschaft umweltbewusster Personen "
                "(Bamberg/Ajzen/Schmidt 2003: Einstellung wirkt auf die Verkehrsmittelwahl). "
                "Zehn Prozent sind gesetzt, nicht aus einer Erhebung übernommen."
            ),
        )
    )
    high_price_sensitivity_threshold: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.8,
            quelle=(
                "Ab welcher Preisempfindlichkeit der zusätzliche Abgaben-Malus greift. "
                "Gesetzt; die Begründung ist inhaltlich (wer aufs Geld schaut, spürt eine "
                "Abgabe doppelt) und nicht empirisch belegt."
            ),
        )
    )
    high_price_sensitivity_penalty: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.3,
            quelle=(
                "Höhe dieses zusätzlichen Malus. Gesetzt wie die Schwelle darüber und aus "
                "demselben Grund ohne empirischen Beleg."
            ),
        )
    )


class PropertiesConfig(BaseModel):
    system_properties: list[SystemProperty] = Field(default_factory=list)
    individual_properties: list[IndividualProperty] = Field(default_factory=list)
    shift_rules: list[ShiftRule] = Field(default_factory=list)
    factor_rules: list[FactorRule] = Field(default_factory=list)
    regulatory_influences: list[RegulatoryInfluence] = Field(default_factory=list)
    market_rules: list[MarketRule] = Field(default_factory=list)
    price_model: PriceModelConfig = Field(default_factory=PriceModelConfig)
    market_feedback: MarketFeedbackConfig = Field(default_factory=MarketFeedbackConfig)
    saturation: SaturationConfig = Field(default_factory=SaturationConfig)
    booking_model: BookingModelConfig = Field(default_factory=BookingModelConfig)

    def system_property_ids(self) -> list[str]:
        return [prop.id for prop in self.system_properties]

    def get_system_property(self, prop_id: str) -> SystemProperty | None:
        for prop in self.system_properties:
            if prop.id == prop_id:
                return prop
        return None
