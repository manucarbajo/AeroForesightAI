"""Config-Katalog: Sweeps, Properties, Faktoren und Config-Dateien für das Dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.config_loader import CONFIGS_DIR, build_initial_state, load_properties_config
from src.market.market_rules import resolve_market_feedback_config
from src.models.property_models import BaselineTrajectory, StepFunctionTrajectory
from src.models.sweep_models import FactorOverride, PropertyOverride, SweepConfig
from src.orchestration.scenario_sweeps import (
    SWEEPS_DIR,
    apply_sweep_overrides,
    load_all_sweep_configs,
    load_sweep_config,
)
from src.validation import collect_state_errors, validate_llm_settings

REPO_ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE_OPTIONS: dict[str, str] = {
    "simulation_config.json": "Simulation (Name, Clock, LLM-Defaults)",
    "properties.json": "System-Properties & Marktregeln",
    "agents.json": "Agenten (Provider, Regulator, Consumer)",
    "agent_profiles.json": "Agent-Profile (observes, depends_on)",
    "factors.json": "Faktor-Landschaft F1–F7",
    "cib_frozen.json": "Fixe CIB-Matrix",
}

STANDARD_PROPERTY_IDS: tuple[str, ...] = (
    "carbon_tax_level",
    "saf_mandate_share",
    "demand_growth_rate",
    "income_index",
    "oil_price_index",
    "fuel_price_change",
    "efuel_subsidy",
    "bevoelkerungsentwicklung",
    "provider_markup",
    "ticket_price",
    "maintenance_cost_index",
    "staff_cost_index",
)

PROPERTY_LABELS: dict[str, str] = {
    "carbon_tax_level": "CO₂-Steuer (EUR/t)",
    "saf_mandate_share": "SAF-Mandat (0–1)",
    "demand_growth_rate": "Nachfragewachstum / Tick",
    "income_index": "Einkommensindex",
    "oil_price_index": "Ölpreis-Index",
    "fuel_price_change": "Treibstoff-Trend / Tick",
    "efuel_subsidy": "E-Fuel-Subvention",
    "bevoelkerungsentwicklung": "Bevölkerung (Personen)",
}


def get_editable_property_ids(properties_file: str = "properties.json") -> list[str]:
    """Liest alle dynamisch verfügbaren Properties aus der JSON-Datei."""
    path = CONFIGS_DIR / properties_file
    if not path.is_file():
        return list(STANDARD_PROPERTY_IDS)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    props = data.get("system_properties", [])
    return [p.get("id") for p in props if isinstance(p, dict) and "id" in p]


def add_custom_property(
    property_id: str,
    label: str = "",
    properties_file: str = "properties.json",
    price_component_type: str = "none",
) -> None:
    """Fügt eine neue Property dauerhaft in die properties.json ein."""
    path = CONFIGS_DIR / properties_file
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "system_properties" not in data or not isinstance(data["system_properties"], list):
        data["system_properties"] = []

    props = data["system_properties"]
    if not any(p.get("id") == property_id for p in props if isinstance(p, dict)):
        props.append(
            {
                "id": property_id,
                "type": "numeric",
                "unit": (
                    "%"
                    if price_component_type == "tax"
                    else ("EUR" if price_component_type == "fee" else "custom")
                ),
                "description": label or "Custom Property",
                "source": "trajectory",
                "price_component_type": price_component_type,
                "trajectory": {"baseline": 0.0, "rules": []},
            }
        )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if label:
        PROPERTY_LABELS[property_id] = label


def delete_custom_property(property_id: str, properties_file: str = "properties.json") -> None:
    """Löscht eine Property dauerhaft aus der properties.json."""
    if property_id in STANDARD_PROPERTY_IDS:
        return
    path = CONFIGS_DIR / properties_file
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "system_properties" in data and isinstance(data["system_properties"], list):
        data["system_properties"] = [
            p
            for p in data["system_properties"]
            if not (isinstance(p, dict) and p.get("id") == property_id)
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


@dataclass
class PropertyEditState:
    property_id: str
    baseline: float
    rules: list[dict[str, Any]] = field(default_factory=list)
    is_active: bool = True


@dataclass
class PopulationEditState:
    id: str
    type: str
    prevalence: float | None = None
    exclusive_group: str | None = None
    saturation_decay: float | None = None
    distribution: str | None = None
    mean: float | None = None
    std_dev: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    alpha: float | None = None
    beta: float | None = None
    modifiers: dict[str, float] = field(default_factory=dict)


@dataclass
class SaturationEditState:
    booking_increase: float = 0.6
    utility_penalty_factor: float = 1.0


@dataclass
class MarketFeedbackEditState:
    enabled: bool = True
    target_booking_rate: float = 0.37
    marginal_cost_fraction: float = 0.33
    markup_adjustment_per_tick: float = 0.08
    max_price_change_fraction: float = 0.08
    damping: float = 0.85
    booking_weight: float = 0.6


@dataclass
class ConfigDraft:
    """Session-State-freundlicher Entwurf für einen Simulationslauf."""

    scenario_mode: str = "basis"  # basis | sweep | custom
    sweep_id: str | None = None
    rounds: int = 40
    seed: int | None = None
    use_seed: bool = False

    simulation_config_file: str = "simulation_config.json"
    properties_file: str = "properties.json"
    agents_file: str = "agents.json"
    factors_file: str = "factors.json"
    cib_file: str = "cib_frozen.json"

    simulation_name: str = ""
    simulation_description: str = ""
    apply_custom_overrides: bool = True

    property_edits: dict[str, PropertyEditState] = field(default_factory=dict)
    factor_states: dict[str, str] = field(default_factory=dict)
    population_edits: list[PopulationEditState] = field(default_factory=list)
    saturation_edit: SaturationEditState = field(default_factory=SaturationEditState)
    market_feedback_edit: MarketFeedbackEditState = field(default_factory=MarketFeedbackEditState)

    # UI State
    mock_llm: bool = True
    deterministic_only: bool = False
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2048

    no_market: bool = False
    redebedarf: bool = False
    checkpoint_interval: int = 5
    no_protocol: bool = False
    no_scenarios: bool = False
    resume_from: str = ""

    run_all_sweeps: bool = False
    sweep_batch_deterministic: bool = True
    run_count: int = 1
    generate_figures: bool = True
    base_price: float | None = None  # P2.3: override price_model.base_price


def configs_dir() -> Path:
    return CONFIGS_DIR


def sweeps_dir() -> Path:
    return SWEEPS_DIR


def list_sweep_presets() -> list[SweepConfig]:
    if not SWEEPS_DIR.is_dir():
        return []
    return load_all_sweep_configs(SWEEPS_DIR)


def load_config_file(filename: str) -> dict[str, Any]:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def default_config_draft() -> ConfigDraft:
    sim = load_config_file("simulation_config.json")
    clock = sim.get("clock", {})
    draft = ConfigDraft(
        rounds=int(clock.get("max_ticks", 40)),
        simulation_name=str(sim.get("name", "")),
        simulation_description=str(sim.get("description", "")),
    )
    draft.property_edits = extract_property_edits_from_file("properties.json")
    draft.factor_states = extract_factor_states_from_file("factors.json")
    draft.population_edits = extract_population_edits_from_file("properties.json")
    draft.saturation_edit = extract_saturation_from_file("properties.json")
    draft.market_feedback_edit = extract_market_feedback_from_file("properties.json")
    return draft


def _trajectory_to_edit_state(
    prop_id: str, traj: BaselineTrajectory | StepFunctionTrajectory
) -> PropertyEditState:
    if isinstance(traj, BaselineTrajectory):
        rules = [rule.model_dump(mode="json") for rule in traj.rules]
        return PropertyEditState(property_id=prop_id, baseline=float(traj.baseline), rules=rules)
    points = traj.points or []
    baseline = float(points[0].value) if points else 0.0
    rules = [
        {
            "active_from_tick": int(point.tick),
            "effect": {"type": "set", "value": float(point.value)},
        }
        for point in points
    ]
    return PropertyEditState(property_id=prop_id, baseline=baseline, rules=rules)


def extract_property_edits_from_file(
    filename: str = "properties.json",
) -> dict[str, PropertyEditState]:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return {}
    properties = load_properties_config(path)
    edits: dict[str, PropertyEditState] = {}
    editable_ids = get_editable_property_ids(filename)
    for prop in properties.system_properties:
        if prop.id not in editable_ids:
            continue
        traj = prop.trajectory
        if traj is None:
            continue
        if not isinstance(traj, (BaselineTrajectory, StepFunctionTrajectory)):
            continue
        edits[prop.id] = _trajectory_to_edit_state(prop.id, traj)
    return edits


def extract_population_edits_from_file(
    filename: str = "properties.json",
) -> list[PopulationEditState]:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    edits = []
    for p in data.get("individual_properties", []):
        edits.append(
            PopulationEditState(
                id=p.get("id", ""),
                type=p.get("type", "boolean"),
                prevalence=p.get("prevalence"),
                exclusive_group=p.get("exclusive_group"),
                saturation_decay=p.get("saturation_decay"),
                distribution=p.get("distribution"),
                mean=p.get("mean"),
                std_dev=p.get("std_dev"),
                min_value=p.get("min_value"),
                max_value=p.get("max_value"),
                alpha=p.get("alpha"),
                beta=p.get("beta"),
                modifiers=p.get("modifiers", {}),
            )
        )
    return edits


def save_population_edits_to_file(
    edits: list[PopulationEditState], filename: str = "properties.json"
) -> None:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    new_props = []
    for e in edits:
        d = {"id": e.id, "type": e.type, "enabled": True}
        if e.type == "boolean":
            if e.prevalence is not None:
                d["prevalence"] = float(e.prevalence)
            if e.exclusive_group:
                d["exclusive_group"] = e.exclusive_group
            if e.saturation_decay is not None:
                d["saturation_decay"] = float(e.saturation_decay)
            d["modifiers"] = e.modifiers
        else:
            if e.distribution:
                d["distribution"] = e.distribution
            if e.mean is not None:
                d["mean"] = float(e.mean)
            if e.std_dev is not None:
                d["std_dev"] = float(e.std_dev)
            if e.min_value is not None:
                d["min_value"] = float(e.min_value)
            if e.max_value is not None:
                d["max_value"] = float(e.max_value)
            if e.alpha is not None:
                d["alpha"] = float(e.alpha)
            if e.beta is not None:
                d["beta"] = float(e.beta)
        new_props.append(d)

    data["individual_properties"] = new_props
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_saturation_from_file(filename: str = "properties.json") -> SaturationEditState:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return SaturationEditState()
    properties = load_properties_config(path)
    return SaturationEditState(
        booking_increase=float(properties.saturation.booking_increase),
        utility_penalty_factor=float(properties.saturation.utility_penalty_factor),
    )


def save_saturation_to_file(edit: SaturationEditState, filename: str = "properties.json") -> None:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["saturation"] = {
        "booking_increase": float(edit.booking_increase),
        "utility_penalty_factor": float(edit.utility_penalty_factor),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_market_feedback_from_file(filename: str = "properties.json") -> MarketFeedbackEditState:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return MarketFeedbackEditState()
    properties = load_properties_config(path)
    config = resolve_market_feedback_config(properties)
    return MarketFeedbackEditState(
        enabled=bool(config.enabled),
        target_booking_rate=float(config.target_booking_rate),
        marginal_cost_fraction=float(config.marginal_cost_fraction),
        markup_adjustment_per_tick=float(config.markup_adjustment_per_tick),
        max_price_change_fraction=float(config.max_price_change_fraction),
        damping=float(config.damping),
        booking_weight=float(config.booking_weight),
    )


def save_market_feedback_to_file(
    edit: MarketFeedbackEditState, filename: str = "properties.json"
) -> None:
    path = CONFIGS_DIR / filename
    if not path.is_file():
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    payload = {
        "enabled": bool(edit.enabled),
        "target_booking_rate": float(edit.target_booking_rate),
        "marginal_cost_fraction": float(edit.marginal_cost_fraction),
        "markup_adjustment_per_tick": float(edit.markup_adjustment_per_tick),
        "max_price_change_fraction": float(edit.max_price_change_fraction),
        "damping": float(edit.damping),
        "booking_weight": float(edit.booking_weight),
    }
    data["market_feedback"] = payload

    sync_keys = (
        "target_booking_rate",
        "marginal_cost_fraction",
        "markup_adjustment_per_tick",
        "max_price_change_fraction",
        "damping",
        "booking_weight",
    )
    for rule in data.get("market_rules", []):
        if not isinstance(rule, dict):
            continue
        effect = rule.get("effect")
        if isinstance(effect, dict) and effect.get("type") == "booking_yield_feedback":
            for key in sync_keys:
                effect[key] = payload[key]
            break

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_factor_states_from_file(filename: str = "factors.json") -> dict[str, str]:
    data = load_config_file(filename)
    return {
        factor_id: str(factor.get("current_state", ""))
        for factor_id, factor in data.items()
        if isinstance(factor, dict)
    }


def factor_options_from_file(filename: str = "factors.json") -> dict[str, dict[str, str]]:
    data = load_config_file(filename)
    options: dict[str, dict[str, str]] = {}
    for factor_id, factor in data.items():
        if not isinstance(factor, dict):
            continue
        states = factor.get("possible_states") or {}
        if isinstance(states, dict):
            options[factor_id] = {str(k): str(v) for k, v in states.items()}
    return options


def apply_sweep_to_draft(draft: ConfigDraft, sweep: SweepConfig) -> ConfigDraft:
    """Merge sweep overrides into property/factor edits for UI display."""

    prop_edits = dict(draft.property_edits)
    for override in sweep.property_overrides:
        existing = prop_edits.get(override.property_id)
        baseline = (
            override.baseline
            if override.baseline is not None
            else (existing.baseline if existing else 0.0)
        )
        rules = (
            override.rules if override.rules is not None else (existing.rules if existing else [])
        )
        prop_edits[override.property_id] = PropertyEditState(
            property_id=override.property_id,
            baseline=float(baseline),
            rules=list(rules),
        )

    factor_states = dict(draft.factor_states)
    for fo in sweep.factor_overrides:
        factor_states[fo.factor_id] = fo.initial_state

    draft.scenario_mode = "sweep"
    draft.sweep_id = sweep.id
    draft.rounds = sweep.max_ticks
    draft.property_edits = prop_edits
    draft.factor_states = factor_states
    draft.apply_custom_overrides = True
    return draft


def property_overrides_from_edits(edits: dict[str, PropertyEditState]) -> list[PropertyOverride]:
    overrides: list[PropertyOverride] = []
    for prop_id, edit in edits.items():
        if not edit.is_active:
            overrides.append(
                PropertyOverride(
                    property_id=prop_id,
                    baseline=0.0,
                    rules=[],
                )
            )
            continue
        overrides.append(
            PropertyOverride(
                property_id=prop_id,
                baseline=edit.baseline,
                rules=edit.rules,
            )
        )
    return overrides


def factor_overrides_from_states(states: dict[str, str]) -> list[FactorOverride]:
    return [
        FactorOverride(factor_id=factor_id, initial_state=state)
        for factor_id, state in sorted(states.items())
        if state
    ]


def build_custom_sweep_from_draft(draft: ConfigDraft, filename: str = "") -> SweepConfig:
    sweep_name = draft.simulation_name
    if not sweep_name or sweep_name == "Flugverkehr Szenarioplanung MVP":
        sweep_name = filename or "Dashboard Custom"

    return SweepConfig(
        id="dashboard_custom",
        name=sweep_name,
        description=draft.simulation_description
        or "Benutzerdefinierte Overrides aus dem Dashboard",
        max_ticks=draft.rounds,
        base_price=draft.base_price,
        property_overrides=property_overrides_from_edits(draft.property_edits),
        factor_overrides=factor_overrides_from_states(draft.factor_states),
        milestones=[],
    )


def resolve_config_paths(draft: ConfigDraft) -> dict[str, Path]:
    return {
        "simulation": CONFIGS_DIR / draft.simulation_config_file,
        "properties": CONFIGS_DIR / draft.properties_file,
        "agents": CONFIGS_DIR / draft.agents_file,
        "factors": CONFIGS_DIR / draft.factors_file,
        "cib": CONFIGS_DIR / draft.cib_file,
    }


def prepare_simulation_state(draft: ConfigDraft):
    """Build SimulationState with file paths, sweep and/or custom overrides."""

    paths = resolve_config_paths(draft)
    state = build_initial_state(
        config_path=paths["simulation"],
        agents_path=paths["agents"],
        factors_path=paths["factors"],
        properties_path=paths["properties"],
        cib_path=paths["cib"],
    )

    if draft.simulation_name:
        state.config.name = draft.simulation_name
    if draft.simulation_description:
        state.config.description = draft.simulation_description

    if draft.scenario_mode == "sweep" and draft.sweep_id:
        sweep_path = SWEEPS_DIR / f"{draft.sweep_id}.json"
        if not sweep_path.is_file():
            sweep_path = Path(draft.sweep_id)
        sweep = load_sweep_config(sweep_path)
        state = apply_sweep_overrides(state, sweep)

    if draft.apply_custom_overrides or draft.scenario_mode == "custom":
        custom = build_custom_sweep_from_draft(draft)
        state = apply_sweep_overrides(state, custom)

    state.clock.max_ticks = int(draft.rounds)
    if draft.use_seed and draft.seed is not None:
        state.config.seed = int(draft.seed)

    return state


def validate_draft(draft: ConfigDraft) -> list[str]:
    """Was an dieser Konfiguration einen Lauf scheitern lassen würde.

    Leere Liste heißt startklar. Absichtlich nicht werfend: Die Oberfläche will
    alle Befunde auf einmal zeigen, statt sie einzeln aus Ausnahmen zu klauben.
    Scheitert schon das Bauen des States (fehlende oder kaputte Config-Datei),
    ist das ebenfalls ein Befund und keine Ausnahme, die nach oben durchschlägt.
    """

    try:
        state = prepare_simulation_state(draft)
    except Exception as exc:  # noqa: BLE001 - eine unlesbare Config ist ein Befund, kein Absturz
        return [f"Konfiguration konnte nicht geladen werden: {exc}"]

    errors = collect_state_errors(state)

    # Die Sprachmodell-Felder des Drafts landen **nicht** im State — sie gehen
    # über `RunLaunchConfig` direkt an den `OllamaClient` (das Durchschreiben
    # nach `config.llm` ist P3.4). Ohne diese Zeilen prüfte die Oberfläche
    # deshalb die Werte aus der Config-Datei statt die eingestellten: ein Draft
    # mit temperature=5.0 und max_tokens=0 galt als fehlerfrei.
    errors.extend(
        validate_llm_settings(
            draft.model,
            draft.temperature,
            draft.max_tokens,
            context="Technik",
        )
    )

    return errors


def effective_config_summary(draft: ConfigDraft) -> dict[str, Any]:
    """JSON-Vorschau der effektiven Lauf-Konfiguration."""

    summary: dict[str, Any] = {
        "scenario_mode": draft.scenario_mode,
        "sweep_id": draft.sweep_id,
        "rounds": draft.rounds,
        "seed": draft.seed if draft.use_seed else None,
        "config_files": {
            "simulation": draft.simulation_config_file,
            "properties": draft.properties_file,
            "agents": draft.agents_file,
            "factors": draft.factors_file,
            "cib": draft.cib_file,
        },
        "llm": {
            "mock_llm": draft.mock_llm,
            "deterministic_only": draft.deterministic_only,
            "model": draft.model,
            "temperature": draft.temperature,
        },
        "pipeline": {
            "market": not draft.no_market,
            "redebedarf": draft.redebedarf,
            "protocol": not draft.no_protocol,
            "scenarios": not draft.no_scenarios,
            "checkpoint_interval": draft.checkpoint_interval,
        },
        "saturation": {
            "booking_increase": draft.saturation_edit.booking_increase,
            "utility_penalty_factor": draft.saturation_edit.utility_penalty_factor,
        },
        "market_feedback": {
            "enabled": draft.market_feedback_edit.enabled,
            "target_booking_rate": draft.market_feedback_edit.target_booking_rate,
            "marginal_cost_fraction": draft.market_feedback_edit.marginal_cost_fraction,
            "markup_adjustment_per_tick": draft.market_feedback_edit.markup_adjustment_per_tick,
            "max_price_change_fraction": draft.market_feedback_edit.max_price_change_fraction,
            "damping": draft.market_feedback_edit.damping,
            "booking_weight": draft.market_feedback_edit.booking_weight,
        },
    }
    if draft.apply_custom_overrides or draft.scenario_mode == "custom":
        summary["property_overrides"] = [
            {
                "property_id": edit.property_id,
                "baseline": edit.baseline,
                "rules": edit.rules,
            }
            for edit in draft.property_edits.values()
        ]
        summary["factor_overrides"] = draft.factor_states
    return summary


def save_custom_sweep_preset(draft: ConfigDraft, filename: str) -> Path:
    """Persistiert den aktuellen Entwurf als Sweep unter configs/sweeps/."""

    SWEEPS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = filename.strip().replace(" ", "_").lower()
    if not safe_name.endswith(".json"):
        safe_name = f"{safe_name}.json"
    sweep = build_custom_sweep_from_draft(draft, filename=Path(safe_name).stem)
    payload = sweep.model_dump(mode="json")
    payload["id"] = Path(safe_name).stem
    payload["rationale"] = "Erstellt im Dashboard als benutzerdefiniertes Szenario."
    target = SWEEPS_DIR / safe_name
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target
