from src.models.agent_models import AgentConfig
from src.models.state_models import FactorState, SimulationConfig, SimulationState


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

    return errors


def validate_config(config: SimulationConfig) -> list[str]:
    errors = []

    if config.clock.max_rounds < 1:
        errors.append("max_rounds muss mindestens 1 sein")

    if config.clock.years_per_round < 1:
        errors.append("years_per_round muss mindestens 1 sein")

    return errors


def validate_state(state: SimulationState) -> list[str]:
    errors = []

    errors.extend(validate_config(state.config))

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
