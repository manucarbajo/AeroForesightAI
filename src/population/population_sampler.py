"""Persistent population sampling and booking.

Individuals are created once, shifted by config rules each tick, then evaluated
for booking deterministically from WTP + logit utility.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from src.models.enums import DistributionType
from src.models.population_models import (
    SEGMENT_LABEL_MAP,
    AgeGroupStats,
    Individual,
    PopulationConfig,
    PopulationStats,
    SegmentStats,
)
from src.models.property_models import IndividualProperty, PropertiesConfig, ShiftRule
from src.models.state_models import FactorState
from src.rule_engine import KNOWN_METRICS, RuleContext, rule_matches

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


def _assign_boolean_labels(
    rng: np.random.Generator,
    properties: PropertiesConfig,
) -> dict[str, bool]:
    """Assign boolean labels.

    By default each label is drawn independently (a person may have several).
    Properties sharing the same ``exclusive_group`` are mutually exclusive —
    use only when segments are meant as personas, not overlapping traits.
    """

    labels: dict[str, bool] = {}
    grouped: dict[str, list[IndividualProperty]] = {}
    independent: list[IndividualProperty] = []

    for prop in properties.individual_properties:
        if prop.type != "boolean" or not prop.enabled:
            continue
        if prop.exclusive_group:
            grouped.setdefault(prop.exclusive_group, []).append(prop)
        else:
            independent.append(prop)

    for prop in independent:
        prevalence = prop.prevalence if prop.prevalence is not None else 0.0
        labels[prop.id] = bool(rng.random() < float(prevalence))

    for group_props in grouped.values():
        weights = [max(0.0, float(prop.prevalence or 0.0)) for prop in group_props]
        total = sum(weights)
        if total <= 0:
            for prop in group_props:
                labels[prop.id] = False
            continue
        probs = [weight / total for weight in weights]
        chosen_idx = int(rng.choice(len(group_props), p=probs))
        for index, prop in enumerate(group_props):
            labels[prop.id] = index == chosen_idx

    return labels


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
    age_prop = _get_individual_property(properties, "age")
    subst_prop = _get_individual_property(properties, "substitution_readiness")

    for person_id in range(total_pop):
        labels = _assign_boolean_labels(rng, properties)

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

        if age_prop and age_prop.distribution == DistributionType.NORMAL:
            age = int(
                _sample_normal(
                    rng,
                    mean=age_prop.mean or 45.0,
                    std_dev=age_prop.std_dev or 15.0,
                    min_value=age_prop.min_value or 2.0,
                    max_value=age_prop.max_value or 90.0,
                )
            )
        elif age_prop and age_prop.distribution == DistributionType.LOGNORMAL:
            age = int(
                _sample_lognormal(
                    rng,
                    mean=age_prop.mean or 45.0,
                    std_dev=age_prop.std_dev or 15.0,
                    min_value=age_prop.min_value or 2.0,
                    max_value=age_prop.max_value or 90.0,
                )
            )
        elif age_prop and age_prop.distribution == DistributionType.UNIFORM:
            age = int(rng.integers(age_prop.min_value or 2.0, (age_prop.max_value or 90.0) + 1))
        else:
            age = int(rng.integers(2, 91))

        if subst_prop and subst_prop.distribution == DistributionType.BETA:
            substitution_readiness = _sample_beta(
                rng, subst_prop.alpha or 2.0, subst_prop.beta or 5.0
            )
        elif subst_prop and subst_prop.distribution == DistributionType.NORMAL:
            substitution_readiness = _sample_normal(
                rng, subst_prop.mean or 0.5, subst_prop.std_dev or 0.2, 0.0, 1.0
            )
        else:
            substitution_readiness = float(rng.uniform(0.1, 0.9))

        base_income = 1.0
        price_sensitivity = 0.5

        for prop in properties.individual_properties:
            if prop.type == "boolean" and labels.get(prop.id):
                mods = prop.modifiers
                if "wtp_multiplier" in mods:
                    wtp *= mods["wtp_multiplier"]
                if "substitution_readiness_multiplier" in mods:
                    substitution_readiness *= mods["substitution_readiness_multiplier"]
                if "base_income_delta" in mods:
                    base_income += mods["base_income_delta"]
                if "price_sensitivity_delta" in mods:
                    price_sensitivity += mods["price_sensitivity_delta"]

        base_income = float(np.clip(base_income + rng.normal(0.0, 0.05), 0.5, 1.5))
        price_sensitivity = float(np.clip(price_sensitivity, 0.0, 1.0))

        individuals.append(
            Individual(
                id=person_id,
                age=age,
                labels=labels,
                wtp_eur=round(wtp, 2),
                environmental_awareness=round(awareness, 4),
                substitution_readiness=round(substitution_readiness, 4),
                price_sensitivity=round(price_sensitivity, 4),
                base_income_factor=round(base_income, 4),
                income_factor=round(base_income, 4),
            )
        )

    return individuals


def apply_factor_shifts(
    individuals: list[Individual],
    shift_rules: list[ShiftRule],
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
    *,
    tick: int = 0,
    metrics: Mapping[str, float | None] | None = None,
) -> list[Individual]:
    """Apply config shift rules to numeric individual attributes.

    *tick* und *metrics* kamen mit P0.4 dazu: Bis dahin hatte dieses Modul einen
    eigenen, ärmeren Evaluator, und eine ``shift_rule`` mit ``tick``- oder
    ``at_least``-Bedingung griff hier still nie. Jetzt wertet dieselbe Funktion
    aus wie für die Faktor-Regeln — dafür braucht sie denselben Kontext.
    """

    if not shift_rules:
        return individuals

    context = RuleContext(
        tick=tick,
        factors=factors,
        metrics=metrics if metrics is not None else {name: None for name in KNOWN_METRICS},
        system_properties=system_properties,
    )
    active_rules = [
        rule for rule in shift_rules if rule_matches(rule.when, context, rule_id=rule.id)
    ]
    if not active_rules:
        return individuals

    updated: list[Individual] = []
    for person in individuals:
        awareness = person.environmental_awareness
        price_sensitivity = person.price_sensitivity
        base_income_factor = person.base_income_factor
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
                base_income_factor = float(np.clip(base_income_factor + delta, 0.0, 5.0))
            if rule.once:
                applied_rules.append(rule_id)

        updated.append(
            person.model_copy(
                update={
                    "environmental_awareness": round(awareness, 4),
                    "price_sensitivity": round(price_sensitivity, 4),
                    "base_income_factor": round(base_income_factor, 4),
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
    saturation_penalty_factor: float = 1.0,
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
    if person.price_sensitivity > HIGH_PRICE_SENSITIVITY_THRESHOLD and normalized_tax > 0:
        eco_penalty += HIGH_PRICE_SENSITIVITY_PENALTY * min(1.0, normalized_tax)

    substitution_penalty = person.substitution_readiness * normalized_price * 1.5
    saturation_penalty = person.saturation_level * saturation_penalty_factor

    utility = base_utility - price_penalty - eco_penalty - substitution_penalty - saturation_penalty
    probability = float(1.0 / (1.0 + np.exp(-utility)))
    return bool(probability >= logit_threshold)


def evaluate_booking(
    individuals: list[Individual],
    *,
    ticket_price: float,
    carbon_tax: float,
    properties: PropertiesConfig | None = None,
) -> tuple[list[Individual], PopulationStats]:
    """Evaluate booking decisions for persistent individuals."""

    saturation = properties.saturation if properties is not None else None
    booking_increase = saturation.booking_increase if saturation is not None else 0.6
    penalty_factor = saturation.utility_penalty_factor if saturation is not None else 1.0

    booked_individuals: list[Individual] = []
    for person in individuals:
        booked = _booking_probability(
            person,
            ticket_price=ticket_price,
            carbon_tax=carbon_tax,
            saturation_penalty_factor=penalty_factor,
        )
        update: dict[str, object] = {"booked": bool(booked)}
        if booked:
            new_saturation = min(1.0, person.saturation_level + booking_increase)
            update["saturation_level"] = round(new_saturation, 4)
        booked_individuals.append(person.model_copy(update=update))

    return booked_individuals, aggregate_population_stats(booked_individuals, properties=properties)


def aggregate_population_stats(
    individuals: list[Individual],
    properties: "PropertiesConfig | None" = None,
) -> PopulationStats:
    """Aggregate booking stats overall and per segment label.

    When *properties* is provided, segments are derived dynamically from all
    boolean ``individual_properties`` (P2.2 SSOT).  Falls back to the legacy
    ``SEGMENT_LABEL_MAP`` when called without properties.
    """

    total_pop = len(individuals)
    total_booked = sum(1 for person in individuals if person.booked)
    total_income_factor = sum(person.income_factor for person in individuals)

    if properties is not None:
        segment_label_pairs = [
            (prop.id, prop.id)
            for prop in properties.individual_properties
            if prop.type == "boolean" and prop.enabled
        ]
    else:
        segment_label_pairs = list(SEGMENT_LABEL_MAP.items())

    segments: dict[str, SegmentStats] = {}
    for segment_id, label_id in segment_label_pairs:
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
        "<18": [],
        "18-25": [],
        "26-35": [],
        "36-50": [],
        "51-65": [],
        ">65": [],
    }
    for person in individuals:
        if person.age < 18:
            age_groups_dict["<18"].append(person)
        elif person.age <= 25:
            age_groups_dict["18-25"].append(person)
        elif person.age <= 35:
            age_groups_dict["26-35"].append(person)
        elif person.age <= 50:
            age_groups_dict["36-50"].append(person)
        elif person.age <= 65:
            age_groups_dict["51-65"].append(person)
        else:
            age_groups_dict[">65"].append(person)

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
    """Scale each individual's income_factor as base_income_factor × income_index."""
    return [
        person.model_copy(
            update={"income_factor": round(person.base_income_factor * income_index, 4)}
        )
        for person in individuals
    ]


def get_decay_rate(person: Individual, properties: PropertiesConfig) -> float:
    found_decay: float | None = None
    for prop in properties.individual_properties:
        if prop.type == "boolean" and person.labels.get(prop.id):
            if prop.saturation_decay is not None:
                if found_decay is None:
                    found_decay = prop.saturation_decay
                else:
                    found_decay = max(found_decay, prop.saturation_decay)
    return found_decay if found_decay is not None else 0.2


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
    current_tick: int = 0,
    metrics: Mapping[str, float | None] | None = None,
) -> tuple[list[Individual], PopulationStats]:
    """Full population pipeline for one tick.

    *current_tick* wurde bis P0.4 entgegengenommen und nie benutzt. Es ist
    genau der Wert, den eine ``shift_rule`` mit ``tick``-Bedingung braucht, und
    wird jetzt an die Regelauswertung durchgereicht. *metrics* ist der
    dazugehörige Rest des Kontexts (`RuntimeMetrics.as_mapping()`).
    """

    if not individuals:
        individuals = initialize_population(properties, config, seed=seed)

    target_population = int(system_properties.get("bevoelkerungsentwicklung", len(individuals)))
    if target_population > len(individuals):
        needed = target_population - len(individuals)
        temp_config = config.model_copy(update={"total_population": needed})
        new_seed = seed + len(individuals)
        new_individuals = initialize_population(properties, temp_config, seed=new_seed)
        start_id = max((p.id for p in individuals), default=-1) + 1
        for i, person in enumerate(new_individuals):
            new_individuals[i] = person.model_copy(update={"id": start_id + i})
        individuals.extend(new_individuals)
    elif target_population < len(individuals):
        rng = _rng(seed + len(individuals))
        to_keep = rng.choice(individuals, size=target_population, replace=False)
        individuals = list(to_keep)

    income_index = system_properties.get("income_index", 1.0)
    shifted = apply_factor_shifts(
        individuals,
        properties.shift_rules,
        factors,
        system_properties,
        tick=current_tick,
        metrics=metrics,
    )
    individuals = update_income_factors(shifted, income_index)

    individuals = [
        person.model_copy(
            update={
                "saturation_level": max(
                    0.0, round(person.saturation_level - get_decay_rate(person, properties), 4)
                )
            }
        )
        for person in individuals
    ]

    return evaluate_booking(
        individuals,
        ticket_price=ticket_price,
        carbon_tax=carbon_tax,
        properties=properties,
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
