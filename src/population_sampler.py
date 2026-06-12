"""Persistent population sampling and booking (M3).

Individuals are created once, shifted by config rules each tick, then evaluated
for booking deterministically from WTP + logit utility.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field

from src.models.enums import DistributionType
from src.models.population_models import (
    SEGMENT_LABEL_MAP,
    Individual,
    PopulationConfig,
)
from src.models.property_models import IndividualProperty, PropertiesConfig, ShiftRule
from src.models.state_models import FactorState


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


DEFAULT_LOGIT_THRESHOLD = 0.5
DEFAULT_GREEN_PREMIUM = 0.1
HIGH_PRICE_SENSITIVITY_THRESHOLD = 0.8
HIGH_PRICE_SENSITIVITY_PENALTY = 0.3
DEFAULT_CARBON_ECO_BASELINE = 50.0


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _get_individual_property(
    properties: PropertiesConfig,
    prop_id: str,
) -> IndividualProperty | None:
    for prop in properties.individual_properties:
        if prop.id == prop_id:
            return prop
    return None


def _sample_beta(rng: np.random.Generator, alpha: float, beta: float) -> float:
    return float(rng.beta(max(0.1, alpha), max(0.1, beta)))


def _sample_normal(
    rng: np.random.Generator,
    *,
    mean: float,
    std_dev: float,
    min_value: float,
    max_value: float,
) -> float:
    value = float(rng.normal(mean, max(0.001, std_dev)))
    return float(np.clip(value, min_value, max_value))


def _sample_lognormal(
    rng: np.random.Generator,
    *,
    mean: float,
    std_dev: float,
    min_value: float,
    max_value: float,
) -> float:
    mu = np.log(max(0.01, mean))
    sigma = max(0.01, std_dev)
    value = float(rng.lognormal(mean=mu, sigma=sigma))
    return float(np.clip(value, min_value, max_value))


def _derive_price_sensitivity(labels: dict[str, bool]) -> float:
    value = 0.5
    if labels.get("business"):
        value -= 0.2
    if labels.get("price_sensitive"):
        value += 0.3
    if labels.get("eco_conscious"):
        value += 0.05
    return float(np.clip(value, 0.0, 1.0))


def initialize_population(
    properties: PropertiesConfig,
    config: PopulationConfig,
    *,
    seed: int = 42,
) -> list[Individual]:
    """Create N persistent individuals once per simulation run."""

    rng = _rng(seed)
    total_pop = config.total_population
    individuals: list[Individual] = []

    awareness_prop = _get_individual_property(properties, "environmental_awareness")
    wtp_prop = _get_individual_property(properties, "wtp_eur")

    for person_id in range(total_pop):
        labels: dict[str, bool] = {}
        for prop in properties.individual_properties:
            if prop.type != "boolean" or not prop.enabled:
                continue
            prevalence = prop.prevalence if prop.prevalence is not None else 0.0
            labels[prop.id] = bool(rng.random() < float(prevalence))

        if awareness_prop and awareness_prop.distribution == DistributionType.BETA:
            awareness = _sample_beta(
                rng,
                awareness_prop.alpha or 2.0,
                awareness_prop.beta or 5.0,
            )
        elif awareness_prop and awareness_prop.distribution == DistributionType.NORMAL:
            awareness = _sample_normal(
                rng,
                mean=awareness_prop.mean or 0.5,
                std_dev=awareness_prop.std_dev or 0.1,
                min_value=awareness_prop.min_value or 0.0,
                max_value=awareness_prop.max_value or 1.0,
            )
        else:
            awareness = float(rng.uniform(0.2, 0.8))

        if wtp_prop and wtp_prop.distribution == DistributionType.LOGNORMAL:
            wtp = _sample_lognormal(
                rng,
                mean=wtp_prop.mean or 120.0,
                std_dev=wtp_prop.std_dev or 0.35,
                min_value=wtp_prop.min_value or 50.0,
                max_value=wtp_prop.max_value or 500.0,
            )
        elif wtp_prop and wtp_prop.distribution == DistributionType.NORMAL:
            wtp = _sample_normal(
                rng,
                mean=wtp_prop.mean or 120.0,
                std_dev=wtp_prop.std_dev or 20.0,
                min_value=wtp_prop.min_value or 50.0,
                max_value=wtp_prop.max_value or 500.0,
            )
        else:
            wtp = float(rng.uniform(80.0, 200.0))

        if labels.get("business"):
            wtp *= 1.25

        individuals.append(
            Individual(
                id=person_id,
                age=int(rng.integers(18, 76)),
                labels=labels,
                wtp_eur=round(wtp, 2),
                environmental_awareness=round(awareness, 4),
                price_sensitivity=_derive_price_sensitivity(labels),
            )
        )

    return individuals


def _rule_matches(
    rule: ShiftRule,
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
) -> bool:
    when = rule.when
    if not when:
        return False

    if "factor" in when:
        factor_id = str(when["factor"])
        expected_state = str(when.get("state", ""))
        factor = factors.get(factor_id)
        if factor is None or factor.current_state != expected_state:
            return False

    if "system_property" in when:
        prop_id = str(when["system_property"])
        value = system_properties.get(prop_id)
        if value is None:
            return False
        if "above" in when and value <= float(when["above"]):
            return False
        if "below" in when and value >= float(when["below"]):
            return False

    return True


def apply_factor_shifts(
    individuals: list[Individual],
    shift_rules: list[ShiftRule],
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
) -> list[Individual]:
    """Apply config shift rules to numeric individual attributes."""

    if not shift_rules:
        return individuals

    active_rules = [rule for rule in shift_rules if _rule_matches(rule, factors, system_properties)]
    if not active_rules:
        return individuals

    updated: list[Individual] = []
    for person in individuals:
        awareness = person.environmental_awareness
        price_sensitivity = person.price_sensitivity
        income_factor = person.income_factor
        applied_rules = list(person.applied_shift_rules)

        for index, rule in enumerate(active_rules):
            rule_id = rule.id or f"shift_rule_{index}"
            if rule.once and rule_id in applied_rules:
                continue
            effect = rule.effect
            prop_id = str(effect.get("property", ""))
            delta = float(effect.get("delta", 0.0))
            if prop_id == "environmental_awareness":
                awareness = float(np.clip(awareness + delta, 0.0, 1.0))
            elif prop_id == "price_sensitivity":
                price_sensitivity = float(np.clip(price_sensitivity + delta, 0.0, 1.0))
            elif prop_id == "income_factor":
                income_factor = float(np.clip(income_factor + delta, 0.0, 5.0))
            if rule.once:
                applied_rules.append(rule_id)

        updated.append(
            person.model_copy(
                update={
                    "environmental_awareness": round(awareness, 4),
                    "price_sensitivity": round(price_sensitivity, 4),
                    "income_factor": round(income_factor, 4),
                    "applied_shift_rules": applied_rules,
                }
            )
        )

    return updated


def _booking_probability(
    person: Individual,
    *,
    ticket_price: float,
    carbon_tax: float,
    green_premium: float = DEFAULT_GREEN_PREMIUM,
    logit_threshold: float = DEFAULT_LOGIT_THRESHOLD,
) -> bool:
    affordability_limit = (
        person.wtp_eur
        * person.income_factor
        * (1.0 + green_premium * person.environmental_awareness)
    )
    if ticket_price > affordability_limit:
        return False

    base_utility = 2.0
    normalized_price = ticket_price / 100.0
    price_penalty = person.price_sensitivity * normalized_price
    excess_carbon = max(0.0, carbon_tax - DEFAULT_CARBON_ECO_BASELINE)
    normalized_tax = excess_carbon / 100.0
    eco_penalty = person.environmental_awareness * normalized_tax
    if person.price_sensitivity > HIGH_PRICE_SENSITIVITY_THRESHOLD:
        eco_penalty += HIGH_PRICE_SENSITIVITY_PENALTY

    utility = base_utility - price_penalty - eco_penalty
    probability = float(1.0 / (1.0 + np.exp(-utility)))
    return bool(probability >= logit_threshold)


def evaluate_booking(
    individuals: list[Individual],
    *,
    ticket_price: float,
    carbon_tax: float,
) -> tuple[list[Individual], PopulationStats]:
    """Evaluate booking decisions for persistent individuals."""

    booked_individuals: list[Individual] = []
    for person in individuals:
        booked = _booking_probability(
            person,
            ticket_price=ticket_price,
            carbon_tax=carbon_tax,
        )
        booked_individuals.append(person.model_copy(update={"booked": bool(booked)}))

    return booked_individuals, aggregate_population_stats(booked_individuals)


def aggregate_population_stats(individuals: list[Individual]) -> PopulationStats:
    """Aggregate booking stats overall and per legacy segment label."""

    total_pop = len(individuals)
    total_booked = sum(1 for person in individuals if person.booked)
    total_income_factor = sum(person.income_factor for person in individuals)

    segments: dict[str, SegmentStats] = {}
    for segment_id, label_id in SEGMENT_LABEL_MAP.items():
        members = [person for person in individuals if person.labels.get(label_id)]
        booked = sum(1 for person in members if person.booked)
        count = len(members)
        segments[segment_id] = SegmentStats(
            segment_id=segment_id,
            share=count / total_pop if total_pop else 0.0,
            total_individuals=count,
            booked_individuals=booked,
            booking_rate=booked / count if count else 0.0,
            avg_income_factor=sum(p.income_factor for p in members) / count if count else 1.0,
        )

    age_groups_dict: dict[str, list[Individual]] = {
        "18-25": [],
        "26-35": [],
        "36-50": [],
        "51-65": [],
        "66+": [],
    }
    for person in individuals:
        if person.age <= 25:
            age_groups_dict["18-25"].append(person)
        elif person.age <= 35:
            age_groups_dict["26-35"].append(person)
        elif person.age <= 50:
            age_groups_dict["36-50"].append(person)
        elif person.age <= 65:
            age_groups_dict["51-65"].append(person)
        else:
            age_groups_dict["66+"].append(person)

    age_stats: dict[str, AgeGroupStats] = {}
    for group, members in age_groups_dict.items():
        count = len(members)
        booked = sum(1 for person in members if person.booked)
        age_stats[group] = AgeGroupStats(
            age_group=group,
            total_individuals=count,
            booked_individuals=booked,
            booking_rate=booked / count if count else 0.0,
            avg_wtp=sum(p.wtp_eur for p in members) / count if count else 0.0,
            avg_income_factor=sum(p.income_factor for p in members) / count if count else 1.0,
            avg_awareness=sum(p.environmental_awareness for p in members) / count if count else 0.0,
        )

    return PopulationStats(
        total_population=total_pop,
        total_booked=total_booked,
        total_demand=total_booked / total_pop if total_pop else 0.0,
        avg_income_factor=total_income_factor / total_pop if total_pop else 1.0,
        segments=segments,
        age_groups=age_stats,
    )


def update_income_factors(
    individuals: list[Individual],
    income_index: float,
) -> list[Individual]:
    """Scale each individual's income_factor by the macro income_index."""
    return [
        person.model_copy(update={"income_factor": round(income_index, 4)})
        for person in individuals
    ]


def run_population_tick(
    properties: PropertiesConfig,
    config: PopulationConfig,
    individuals: list[Individual] | None,
    *,
    ticket_price: float,
    carbon_tax: float,
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
    seed: int = 42,
) -> tuple[list[Individual], PopulationStats]:
    """Full M3 population pipeline for one tick."""

    if not individuals:
        individuals = initialize_population(properties, config, seed=seed)

    target_population = int(system_properties.get("bevoelkerungsentwicklung", len(individuals)))
    if target_population > len(individuals):
        needed = target_population - len(individuals)
        temp_config = config.model_copy(update={"total_population": needed})
        new_seed = seed + len(individuals)  # unique seed for new batch
        new_individuals = initialize_population(properties, temp_config, seed=new_seed)
        
        # fix IDs so they don't overlap
        start_id = max((p.id for p in individuals), default=-1) + 1
        for i, person in enumerate(new_individuals):
            new_individuals[i] = person.model_copy(update={"id": start_id + i})
            
        individuals.extend(new_individuals)

    income_index = system_properties.get("income_index", 1.0)
    individuals = update_income_factors(individuals, income_index)

    shifted = apply_factor_shifts(
        individuals,
        properties.shift_rules,
        factors,
        system_properties,
    )
    return evaluate_booking(
        shifted,
        ticket_price=ticket_price,
        carbon_tax=carbon_tax,
    )


def run_population_sampling(
    config: PopulationConfig,
    ticket_price: float,
    carbon_tax: float,
    *,
    properties: PropertiesConfig | None = None,
    seed: int = 42,
) -> PopulationStats:
    """Backward-compatible entry point (non-persistent single-tick sample)."""

    from src.config_loader import load_properties_config

    resolved_properties = properties or load_properties_config()
    individuals, stats = run_population_tick(
        resolved_properties,
        config,
        None,
        ticket_price=ticket_price,
        carbon_tax=carbon_tax,
        factors={},
        system_properties={},
        seed=seed,
    )
    _ = individuals
    return stats
