from src.models.agent_models import AgentConfig
from src.models.enums import DistributionType
from src.models.population_models import (
    ConsumerSegment,
    DistributionConfig,
    PopulationConfig,
    ScenarioParameter,
)
from src.models.state_models import (
    FactorState,
    PolicySchedule,
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
    errors = []

    for param in config.scenario_parameters:
        errors.extend(validate_scenario_parameter(param))

    if config.policy_schedule:
        errors.extend(validate_policy_schedule(config.policy_schedule))

    return errors


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
        errors.append(f"{prefix}min_value ({dist.min_value}) muss kleiner als max_value ({dist.max_value}) sein")

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

        errors.extend(validate_distribution(seg.price_elasticity, f"segment '{seg.id}' price_elasticity"))
        errors.extend(validate_distribution(seg.income_level, f"segment '{seg.id}' income_level"))
        errors.extend(validate_distribution(seg.environmental_awareness, f"segment '{seg.id}' environmental_awareness"))

    return errors


def validate_population_config(pop: PopulationConfig) -> list[str]:
    errors = []

    if pop.total_population < 1:
        errors.append("total_population muss mindestens 1 sein")

    errors.extend(validate_segments(pop.segments))

    return errors


def validate_scenario_parameter(param: ScenarioParameter) -> list[str]:
    errors = []

    if not param.id:
        errors.append("scenario_parameter: id darf nicht leer sein")

    if not param.name:
        errors.append(f"scenario_parameter '{param.id}': name darf nicht leer sein")

    if param.min_value is not None and param.max_value is not None:
        if param.min_value >= param.max_value:
            errors.append(
                f"scenario_parameter '{param.id}': "
                f"min_value ({param.min_value}) muss kleiner als max_value ({param.max_value}) sein"
            )
        if not (param.min_value <= param.value <= param.max_value):
            errors.append(
                f"scenario_parameter '{param.id}': "
                f"value ({param.value}) muss zwischen min und max liegen"
            )

    return errors


def validate_policy_schedule(schedule: PolicySchedule) -> list[str]:
    errors = []
    
    valid_parameters = {
        "carbon_tax_level", 
        "fuel_price_change", 
        "oil_price_index", 
        "saf_mandate_share", 
        "efuel_subsidy", 
        "demand_growth_rate"
    }
    
    for key in schedule.baseline.keys():
        if key not in valid_parameters:
            errors.append(f"policy_schedule: baseline parameter '{key}' ist ungueltig")

    for rule in schedule.rules:
        if rule.parameter not in valid_parameters:
            errors.append(f"policy_schedule: rule '{rule.id}' referenziert ungueltigen parameter '{rule.parameter}'")
        
        if rule.active_from_tick < 1:
            errors.append(f"policy_schedule: rule '{rule.id}' active_from_tick muss >= 1 sein")
            
        if rule.active_until_tick is not None and rule.active_until_tick < rule.active_from_tick:
            errors.append(f"policy_schedule: rule '{rule.id}' active_until_tick muss >= active_from_tick sein")
            
        if rule.effect.type not in ["set", "ramp"]:
            errors.append(f"policy_schedule: rule '{rule.id}' effect.type '{rule.effect.type}' ungueltig (erwartet 'set' oder 'ramp')")
            
        if rule.effect.type == "ramp" and rule.effect.per_tick is None:
            errors.append(f"policy_schedule: rule '{rule.id}' mit type 'ramp' benoetigt 'per_tick'")

    return errors


def validate_state(state: SimulationState) -> list[str]:
    errors = []

    errors.extend(validate_config(state.config))
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
        raise ValidationError(
            "validierungsfehler:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    return errors
