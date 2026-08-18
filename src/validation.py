from src.models.agent_models import AgentConfig
from src.models.enums import DistributionType
from src.models.population_models import (
    ConsumerSegment,
    DistributionConfig,
    PopulationConfig,
)
from src.models.property_models import (
    FactorRule,
    PropertiesConfig,
    RampEffect,
    StepFunctionTrajectory,
    SystemProperty,
)
from src.models.state_models import (
    FactorState,
    SimulationClock,
    SimulationConfig,
    SimulationState,
)


class ValidationError(Exception):
    pass


def validate_factor(factor: FactorState) -> list[str]:
    errors = []

    if not factor.possible_states:
        errors.append(f"{factor.id}: keine possible_states definiert")

    if factor.current_state not in factor.possible_states:
        errors.append(
            f"{factor.id}: current_state '{factor.current_state}' "
            f"nicht in possible_states {list(factor.possible_states.keys())}"
        )

    return errors


def validate_agent(agent: AgentConfig, factor_ids: set[str]) -> list[str]:
    errors = []

    if not agent.goals:
        errors.append(f"agent '{agent.id}': keine goals definiert")

    if agent.population_config:
        errors.extend(validate_population_config(agent.population_config))

    return errors


def validate_config(config: SimulationConfig) -> list[str]:
    return []


def validate_clock(clock: SimulationClock) -> list[str]:
    errors = []

    if clock.max_ticks < 1:
        errors.append("max_ticks muss mindestens 1 sein")

    if clock.tick_unit != "tick":
        errors.append("tick_unit muss 'tick' sein")

    return errors


def validate_distribution(dist: DistributionConfig, context: str = "") -> list[str]:
    errors = []
    prefix = f"{context}: " if context else ""

    if dist.min_value >= dist.max_value:
        errors.append(
            f"{prefix}min_value ({dist.min_value}) muss kleiner als max_value ({dist.max_value}) sein"
        )

    if dist.type == DistributionType.NORMAL:
        if dist.std_dev <= 0:
            errors.append(f"{prefix}std_dev muss positiv sein")
        if not (dist.min_value <= dist.mean <= dist.max_value):
            errors.append(f"{prefix}mean ({dist.mean}) muss zwischen min und max liegen")

    return errors


def validate_segments(segments: list[ConsumerSegment]) -> list[str]:
    errors = []

    if not segments:
        errors.append("keine consumer-segmente definiert")
        return errors

    total_share = sum(seg.share for seg in segments)
    if abs(total_share - 1.0) > 1e-6:
        errors.append(f"segmentanteile summieren sich auf {total_share}, erwartet 1.0")

    seen_ids = set()
    for seg in segments:
        if seg.share <= 0 or seg.share > 1:
            errors.append(f"segment '{seg.id}': share ({seg.share}) muss zwischen 0 und 1 liegen")

        if seg.id in seen_ids:
            errors.append(f"segment-id '{seg.id}' ist doppelt vergeben")
        seen_ids.add(seg.id)

        errors.extend(
            validate_distribution(seg.price_elasticity, f"segment '{seg.id}' price_elasticity")
        )
        errors.extend(validate_distribution(seg.income_level, f"segment '{seg.id}' income_level"))
        errors.extend(
            validate_distribution(
                seg.environmental_awareness, f"segment '{seg.id}' environmental_awareness"
            )
        )

    return errors


def validate_population_config(pop: PopulationConfig) -> list[str]:
    errors = []

    if pop.total_population < 1:
        errors.append("total_population muss mindestens 1 sein")

    errors.extend(validate_segments(pop.segments))

    return errors


def validate_properties_config(properties: PropertiesConfig) -> list[str]:
    errors = []
    seen_ids: set[str] = set()

    for index, prop in enumerate(properties.system_properties):
        prefix = f"system_properties[{index}]"
        if not prop.id:
            errors.append(f"{prefix}: id darf nicht leer sein")
            continue
        if prop.id in seen_ids:
            errors.append(f"{prefix}: id '{prop.id}' ist doppelt vergeben")
        seen_ids.add(prop.id)

        if prop.min_value is not None and prop.max_value is not None:
            if prop.min_value >= prop.max_value:
                errors.append(f"{prefix} '{prop.id}': min_value muss kleiner als max_value sein")

        errors.extend(_validate_trajectory(prop, prefix))

    errors.extend(_validate_factor_rules(properties.factor_rules))

    return errors


def _validate_factor_rules(rules: list[FactorRule]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, rule in enumerate(rules):
        prefix = f"factor_rules[{index}]"
        if not rule.id:
            errors.append(f"{prefix}: id darf nicht leer sein")
        elif rule.id in seen_ids:
            errors.append(f"{prefix}: id '{rule.id}' ist doppelt vergeben")
        seen_ids.add(rule.id)
        if not rule.factor_id:
            errors.append(f"{prefix}: factor_id darf nicht leer sein")
        if not rule.effect.set_state:
            errors.append(f"{prefix}: effect.set_state darf nicht leer sein")
    return errors


def _validate_trajectory(prop: SystemProperty, prefix: str) -> list[str]:
    errors: list[str] = []
    trajectory = prop.trajectory

    if isinstance(trajectory, StepFunctionTrajectory):
        if not trajectory.points:
            errors.append(f"{prefix} '{prop.id}': step_function braucht mindestens einen Punkt")
        for point_index, point in enumerate(trajectory.points):
            if point.tick < 0:
                errors.append(f"{prefix} '{prop.id}': points[{point_index}].tick muss >= 0 sein")
        return errors

    for rule_index, rule in enumerate(trajectory.rules):
        if rule.active_from_tick < 0:
            errors.append(
                f"{prefix} '{prop.id}': rules[{rule_index}].active_from_tick muss >= 0 sein"
            )
        if isinstance(rule.effect, RampEffect) and rule.effect.duration_ticks < 1:
            errors.append(
                f"{prefix} '{prop.id}': rules[{rule_index}].duration_ticks muss >= 1 sein"
            )

    return errors


def validate_state(state: SimulationState) -> list[str]:
    errors = []

    errors.extend(validate_config(state.config))
    errors.extend(validate_properties_config(state.resolved_properties()))
    errors.extend(validate_clock(state.clock))

    factor_ids = set(state.environment.factors.keys())
    for factor in state.environment.factors.values():
        errors.extend(validate_factor(factor))

    for agent in state.agents:
        errors.extend(validate_agent(agent, factor_ids))

    if not state.agents:
        errors.append("keine agenten konfiguriert")

    if not state.environment.factors:
        errors.append("keine faktoren konfiguriert")

    if errors:
        raise ValidationError("validierungsfehler:\n" + "\n".join(f"  - {e}" for e in errors))

    return errors
