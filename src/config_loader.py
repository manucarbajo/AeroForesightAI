import json
from pathlib import Path

from src.models.agent_models import AgentConfig
from src.models.cib_models import CIBMatrix
from src.models.population_models import PopulationConfig
from src.models.state_models import (
    EnvironmentState,
    FactorState,
    SimulationClock,
    SimulationConfig,
    SimulationState,
)

CONFIGS_DIR = Path(__file__).parent.parent / "configs"


def load_simulation_config(path: Path | None = None) -> SimulationConfig:
    path = path or CONFIGS_DIR / "simulation_config.json"
    with open(path) as f:
        data = json.load(f)
    return SimulationConfig(**data)


def load_agents(path: Path | None = None) -> list[AgentConfig]:
    path = path or CONFIGS_DIR / "agents.json"
    with open(path) as f:
        data = json.load(f)
    return [AgentConfig(**agent) for agent in data]


def load_factors(path: Path | None = None) -> dict[str, FactorState]:
    path = path or CONFIGS_DIR / "factors.json"
    with open(path) as f:
        data = json.load(f)
    return {fid: FactorState(**fdata) for fid, fdata in data.items()}


def load_population_config(agents: list[AgentConfig]) -> PopulationConfig | None:
    for agent in agents:
        if agent.agent_type.value == "consumer" and agent.population_config:
            return agent.population_config
    return None


def load_cib_frozen(path: Path | None = None) -> CIBMatrix:
    """Load the fixed CIB matrix used for C4 runs (no per-tick LLM updates)."""
    path = path or CONFIGS_DIR / "cib_frozen.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return CIBMatrix.model_validate(data)


def build_initial_state(
    config_path: Path | None = None,
    agents_path: Path | None = None,
    factors_path: Path | None = None,
    *,
    cib_path: Path | None = None,
    load_cib: bool = True,
) -> SimulationState:
    config = load_simulation_config(config_path)
    agents = load_agents(agents_path)
    factors = load_factors(factors_path)

    environment = EnvironmentState(factors=factors)
    clock = SimulationClock(**config.clock.model_dump())

    cib_matrix = load_cib_frozen(cib_path) if load_cib else None

    return SimulationState(
        config=config,
        clock=clock,
        environment=environment,
        agents=agents,
        cib_matrix=cib_matrix,
    )
