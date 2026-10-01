"""Config-Katalog: Sweeps, Properties, Faktoren und Config-Dateien für das Dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from src.config_loader import CONFIGS_DIR, build_initial_state, load_properties_config
from src.llm.defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
)
from src.market.market_feedback import resolve_market_feedback_config
from src.models.property_models import BaselineTrajectory, StepFunctionTrajectory
from src.models.state_models import LLMConfig, Rahmenszenario
from src.models.sweep_models import PropertyOverride, SweepConfig
from src.orchestration.scenario_sweeps import (
    SWEEPS_DIR,
    apply_sweep_overrides,
    load_all_sweep_configs,
    load_sweep_config,
)
from src.orchestration.scenario_sweeps import (
    rahmenszenarien as _rahmenszenarien,
)
from src.validation import collect_state_errors, field_of, issue

REPO_ROOT = Path(__file__).resolve().parents[1]

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

#: **Die Namen der Systemgrößen — die eine Quelle** für Diagramme, Modell-Bereich
#: und Handbuch (P7.1-U1.5). Bis zum 2026-09-13 standen hier acht von sechzehn;
#: die übrigen erschienen als Kennung (`maintenance_cost_index`), und das
#: Diagramm «Was die Politik bewirkt» benannte **alle** seine Reihen so, weil es
#: die Liste gar nicht benutzte. `tests/test_web_diagrammnamen.py` hält jede
#: Größe aus `configs/properties.json` gegen diese Liste.
PROPERTY_LABELS: dict[str, str] = {
    "carbon_tax_level": "CO₂-Steuer (€/t)",
    "saf_mandate_share": "SAF-Mandat (0–1)",
    "demand_growth_rate": "Nachfragewachstum / Tick",
    "income_index": "Einkommensindex",
    "oil_price_index": "Ölpreis-Index",
    "fuel_price_change": "Treibstoff-Trend / Tick",
    "efuel_subsidy": "E-Fuel-Subvention",
    "bevoelkerungsentwicklung": "Bevölkerung (Personen)",
    "provider_markup": "Anbieter-Marge (€)",
    "ticket_price": "Ticketpreis (€)",
    "kapazitaet_index": "Kapazitätsindex",
    "altersmittel_jahre": "Altersmittel (Jahre)",
    "erneuerungsrate": "Erneuerungsrate / Tick",
    "maintenance_cost_index": "Wartungskostenindex",
    "staff_cost_index": "Personalkostenindex",
    "airport_fee": "Flughafengebühr (€)",
}

#: Einheiten aus `properties.json` — (kurz für Achsentitel, lang für Tabellen).
#: Bis zum 2026-09-13 lebte eine zweite, halbe Fassung im Handbuch
#: (`docs_reference.UNIT_LABELS`), und sie sprach noch von «Runde» statt Tick.
EINHEITEN: dict[str, tuple[str, str]] = {
    "eur_per_tonne": ("€/t", "€ je Tonne"),
    "fraction": ("0–1", "Anteil (0–1)"),
    "fraction_per_tick": ("Anteil je Tick", "Anteil je Tick"),
    "share_per_tick": ("Anteil je Tick", "Anteil je Tick"),
    "index": ("Index", "Index (1.0 = Basis)"),
    "eur": ("€", "Euro"),
    "EUR": ("€", "Euro"),
    "persons": ("Personen", "Personen"),
    "years": ("Jahre", "Jahre"),
    "%": ("%", "Prozent"),
}

#: Die Namen der Bevölkerungssegmente — dieselbe Quelle für die Karten im
#: Modell-Bereich und die Linien in «Wer noch fliegt». Vorher entstand der Name
#: an beiden Stellen aus der Kennung («Eco Conscious»).
SEGMENT_NAMEN: dict[str, str] = {
    "business": "Geschäftsreisende",
    "family": "Familien",
    "price_sensitive": "Preisbewusste",
    "eco_conscious": "Umweltbewusste",
    "frequent_flyer": "Vielflieger",
}


#: Die Kurznamen der sieben Faktoren — für die Faktorleiste über der Szene (P7.5-U5.3,
#: von Haiko entschieden am 2026-09-15: eine Reihe, Kurzname und Zustand als Marke).
#: Die langen Namen in `configs/factors.json` («Mobilitaetsbeduerfnis / Nachfrage»)
#: passen bei 1280 px in keinen Chip; gemessen blieben je Chip 72 px. Die Wörter sind
#: die des Domain-Glossars in CLAUDE.md.
FAKTOR_KURZNAMEN: dict[str, str] = {
    "F1": "Nachfrage",
    "F2": "Regulierung",
    "F3": "Technologie",
    "F4": "Wirtschaft",
    "F5": "Alternativen",
    "F6": "Gesellschaft",
    "F7": "Geopolitik",
}


def segment_name(segment_id: str) -> str:
    """Der Name eines Segments — für ein unbekanntes die Kennung in Lesbarform."""

    return SEGMENT_NAMEN.get(segment_id, segment_id.replace("_", " "))


def property_einheit(property_id: str, properties_file: str = "properties.json") -> str:
    """Die kurze Einheit einer Systemgröße, gelesen aus der Konfiguration.

    **Nicht zwischengespeichert:** Eine eigene Systemgröße kann zur Laufzeit dazukommen.
    """

    path = CONFIGS_DIR / properties_file
    if not path.is_file():
        return ""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for eintrag in data.get("system_properties", []):
        if isinstance(eintrag, dict) and eintrag.get("id") == property_id:
            return EINHEITEN.get(str(eintrag.get("unit") or ""), ("", ""))[0]
    return ""


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
        f.write("\n")
    if label:
        PROPERTY_LABELS[property_id] = label


def abweichungen_benannt(abweichungen: list[str] | tuple[str, ...]) -> list[str]:
    """Die Abweichungen eines abgeleiteten Laufs in den Namen der Oberfläche (P8-V6).

    `rahmen.abweichungen` trägt Kennungen (`carbon_tax_level`, `preisstrategie`,
    `abschnitt.wert`); gezeigt wird, was `PROPERTY_LABELS` dazu kennt. Eine
    Kennung ohne Namen bleibt stehen — lieber sie als gar nichts.
    """

    eigene = {"preisstrategie": "Preisstrategie"}
    return [PROPERTY_LABELS.get(a, eigene.get(a, a)) for a in abweichungen]


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
            f.write("\n")


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
    #: **Was vom gewählten Szenario abweicht** (P7.13-U13.2) — je Größe nur, was
    #: jemand geändert hat, keine volle Kopie wie `property_edits`. Beim Start liegt
    #: es **auf** dem Szenario; eine volle Kopie drehte dessen Verläufe still zurück
    #: (so rechnete «Business as Usual» vor P1.1 mit dem Sprung auf 120).
    abweichungen: dict[str, PropertyEditState] = field(default_factory=dict)
    #: Die Preisstrategie, wenn sie vom Szenario abweicht; `None` heißt «wie das Szenario».
    preisstrategie: str | None = None
    #: **Modellannahmen dieses Laufs** (P7.13-U13.5): Preisbildung, Sättigung und
    #: Segmente, je Abschnitt nur, was vom gewählten Szenario abweicht — Format wie
    #: `SweepConfig.modellannahmen`. **Nicht** `market_feedback_edit` und die übrigen
    #: vollen Kopien: Die gehören dem Bereich «Modell» und wirken nur gespeichert.
    #: Anders als `abweichungen` überleben sie einen Szenariowechsel — sie sind
    #: Annahmen über das Modell, nicht über den Verlauf einer Welt.
    modellannahmen: dict[str, Any] = field(default_factory=dict)
    # `factor_states` ist mit P2.0-C entfallen. Die Faktorlage war eine
    # **Eingabe** des Entwurfs und wurde als `factor_overrides` in den Lauf
    # gereicht; heute entsteht sie im Lauf aus den exogenen Systemgrößen.
    population_edits: list[PopulationEditState] = field(default_factory=list)
    saturation_edit: SaturationEditState = field(default_factory=SaturationEditState)
    market_feedback_edit: MarketFeedbackEditState = field(default_factory=MarketFeedbackEditState)

    # UI State
    mock_llm: bool = True
    deterministic_only: bool = False
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS

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
    """Alles unter `configs/sweeps/` — **Rahmen und Stresstests**.

    Für die **Auswahl** richtig: Ein Stresstest bleibt einzeln startbar. Für
    einen **Vergleich** falsch — dafür `rahmenszenarien()`.
    """

    if not SWEEPS_DIR.is_dir():
        return []
    return load_all_sweep_configs(SWEEPS_DIR)


def rahmenszenarien() -> list[SweepConfig]:
    """Nur die begründeten Weltbilder (P2.2). Siehe `scenario_sweeps.rahmenszenarien`."""

    if not SWEEPS_DIR.is_dir():
        return []
    return _rahmenszenarien(SWEEPS_DIR)


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
        f.write("\n")


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
        f.write("\n")


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
        f.write("\n")


def save_property_edits_to_file(
    edits: dict[str, PropertyEditState], filename: str = "properties.json"
) -> list[str]:
    """Startwerte und Verläufe als neuer Standard in die Datei (P7.13-U13.3).

    **Von Haiko entschieden am 2026-09-15:** Startwerte und Verläufe aus dem
    Bereich «Modell» wirken nur gespeichert; für einen einzelnen Lauf ändert man
    sie im Schritt «Verläufe». Bis dahin gab es keinen Schreibweg — die Werte
    gingen in `property_edits` und wirkten nur unter der Standard-Ausgangslage mit
    «Eigene Werte anwenden», unter einem Rahmenszenario still gar nicht.

    **Geschrieben wird nur, was sich von der Datei unterscheidet.** Eine Größe als
    Stufenfunktion (`bevoelkerungsentwicklung`) behält so ihre Form, solange
    niemand sie ändert. **Eine ausgeschaltete Größe** wird mit Startwert 0 und ohne
    Regeln gespeichert — genau das, womit ein Lauf sie bisher gerechnet hat (von
    Haiko entschieden); die Rückfrage vor dem Speichern sagt es.

    Gibt die Kennungen der geschriebenen Größen zurück.
    """

    path = CONFIGS_DIR / filename
    if not path.is_file():
        return []
    ausgeliefert = extract_property_edits_from_file(filename)
    neu: dict[str, dict[str, Any]] = {}
    for prop_id, edit in edits.items():
        alt = ausgeliefert.get(prop_id)
        if alt is None:
            continue
        baseline = float(edit.baseline) if edit.is_active else 0.0
        rules = list(edit.rules) if edit.is_active else []
        if baseline == float(alt.baseline) and rules == list(alt.rules):
            continue
        neu[prop_id] = {"baseline": baseline, "rules": rules}
    if not neu:
        return []

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for item in data.get("system_properties", []):
        if isinstance(item, dict) and item.get("id") in neu:
            item["trajectory"] = neu[item["id"]]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return sorted(neu)


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


# `apply_sweep_to_draft` («Werte übernehmen und selbst anpassen») ist mit
# P7.13-U13.3 entfallen. Es schrieb die Verläufe eines Szenarios in
# `property_edits` und schaltete auf die Standard-Ausgangslage — und
# `property_edits` erreicht seither keinen Lauf mehr. Ein Szenario ändert man im
# Schritt «Verläufe», auf dem Szenario selbst.


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


# `factor_overrides_from_states` ist mit P2.0-C entfallen. Sie übersetzte die im
# Assistenten gewählte Faktorlage in Vorgaben für den Lauf — und stellte damit
# die Antwort vor die Rechnung. Die Faktoren entstehen heute im Lauf aus den
# exogenen Systemgrößen des Rahmenszenarios.


def exogene_groessen(properties_file: str = "properties.json") -> list[str]:
    """Die Systemgrößen, deren Verlauf ein Szenario vorgibt — in Dateireihenfolge (P7.13-U13.1).

    Gesucht über `source == "trajectory"`, nicht aufgezählt: `provider_markup` und
    `ticket_price` rechnet der Lauf selbst, und eine neue Größe in der Datei steht
    ohne weiteres Zutun im Schritt «Verläufe».
    """

    from src.market.property_engine import is_exogenous_property

    properties = load_properties_config(CONFIGS_DIR / properties_file)
    return [prop.id for prop in properties.system_properties if is_exogenous_property(prop)]


def von_rahmen_veraendert() -> set[str]:
    """Welche Systemgrößen mindestens ein Rahmenszenario verändert (P7.13-U13.1).

    Sie stehen im Schritt «Verläufe» offen, die übrigen hinter «Weitere Größen» —
    von Haiko entschieden am 2026-09-15. Abgeleitet aus den Dateien, damit ein
    neues Rahmenszenario die Liste mitbringt.
    """

    return {
        override.property_id
        for preset in list_sweep_presets()
        if preset.art == "rahmen"
        for override in preset.property_overrides
    }


def _ohne_abweichungen(draft: ConfigDraft) -> ConfigDraft:
    return replace(draft, abweichungen={}, preisstrategie=None, modellannahmen={})


def _annahmen_namen(annahmen: dict[str, Any]) -> list[str]:
    """Wie eine Modellannahme im Artefakt heißt: `abschnitt.wert`, bei Segmenten mit Kennung."""

    namen = []
    for abschnitt, werte in (annahmen or {}).items():
        if abschnitt == "population":
            for segment, felder in (werte or {}).items():
                namen += [f"population.{segment}.{feld}" for feld in felder or {}]
        else:
            namen += [f"{abschnitt}.{feld}" for feld in werte or {}]
    return sorted(namen)


def _annahmen_bereinigen(annahmen: dict[str, Any], basis: Any) -> dict[str, Any]:
    """Was den Werten des Szenarios gleicht, ist keine Modellannahme (P7.13-U13.5)."""

    from src.market.market_feedback import resolve_market_feedback_config

    vorlage = {
        "market_feedback": resolve_market_feedback_config(basis),
        "saturation": basis.saturation,
    }
    segmente = {p.id: p for p in basis.individual_properties}
    ergebnis: dict[str, Any] = {}
    for abschnitt, werte in (annahmen or {}).items():
        if abschnitt == "population":
            behalten = {}
            for segment, felder in (werte or {}).items():
                ist = segmente.get(segment)
                rest = {
                    k: v
                    for k, v in (felder or {}).items()
                    if ist is None or getattr(ist, k, None) != v
                }
                if rest:
                    behalten[segment] = rest
        else:
            ist = vorlage.get(abschnitt)
            behalten = {
                k: v for k, v in (werte or {}).items() if ist is None or getattr(ist, k, None) != v
            }
        if behalten:
            ergebnis[abschnitt] = behalten
    return ergebnis


def szenario_verlauf(draft: ConfigDraft, groesse: str) -> PropertyEditState:
    """Startwert und Regeln einer Größe **im gewählten Szenario** — ohne die Abweichungen.

    Die Vorbelegung des Editors und der Maßstab dafür, was eine Abweichung ist.
    Gelesen aus dem Zustand, den der Lauf ohne Abweichungen bekäme, nicht aus der
    Szenariodatei: Nur so gilt dieselbe Regel wie beim Rechnen, auch für die
    Standard-Ausgangslage mit «Eigene Werte anwenden».
    """

    state = prepare_simulation_state(_ohne_abweichungen(draft))
    prop = next(p for p in state.properties.system_properties if p.id == groesse)
    return _trajectory_to_edit_state(groesse, prop.trajectory)


def szenario_preisstrategie(draft: ConfigDraft) -> str:
    """Die Preisstrategie des gewählten Szenarios, ohne eine eigene Wahl."""

    state = prepare_simulation_state(_ohne_abweichungen(draft))
    for regel in state.properties.market_rules:
        if regel.effect.get("type") == "booking_yield_feedback":
            return str(regel.effect.get("strategie") or "auslastung")
    return "auslastung"


def verlaeufe_je_tick(draft: ConfigDraft, groesse: str) -> tuple[list[float], list[float]]:
    """Die beiden Kurven des Schritts «Verläufe»: Szenario und eigene Fassung, je Tick.

    **Dieselbe Rechnung wie im Lauf** (P7.13-U13.1): beide aus dem Zustand, den
    `prepare_simulation_state` bauen würde, gefragt über `resolve_property` —
    samt Begrenzung auf Mindest- und Höchstwert. Eine zweite Verlaufsrechnung für
    die Oberfläche könnte von der ersten abweichen, und die Kurve zeigte etwas
    anderes, als gerechnet wird.
    """

    from src.market.property_engine import resolve_property

    ticks = range(0, int(draft.rounds) + 1)
    basis = prepare_simulation_state(_ohne_abweichungen(draft)).properties
    eigen = prepare_simulation_state(draft).properties
    return (
        [resolve_property(groesse, tick, basis) for tick in ticks],
        [resolve_property(groesse, tick, eigen) for tick in ticks],
    )


def _letzter_tick(edit: PropertyEditState) -> int:
    """Ab welchem Tick sich ein Verlauf nicht mehr ändert — spätester Stützpunkt samt Dauer."""

    ticks = [0]
    for regel in edit.rules or []:
        effekt = regel.get("effect") or {}
        ticks.append(
            int(regel.get("active_from_tick") or 0) + int(effekt.get("duration_ticks") or 0)
        )
    return max(ticks)


def abweichungen_bereinigen(draft: ConfigDraft) -> ConfigDraft:
    """Was im Verlauf dem Szenario gleicht, ist keine Abweichung und fällt weg (P7.13).

    Der Editor zeigt die Werte des Szenarios, und ein Eingabefeld meldet beim
    Zeichnen seinen unveränderten Wert. Ohne diese Bereinigung stünde jede
    angesehene Größe als «abgeleitet» im Artefakt, obwohl niemand etwas geändert hat.

    **Verglichen wird der Verlauf je Tick, nicht die Regeln** (U13.6). Die erste
    Fassung verglich die Regeln, und gemessen stand ein Lauf unter «Business as
    Usual» als «abgeleitet» im Artefakt, nachdem der Stützpunkt «ab Tick 1 auf 50»
    bei einem Startwert von 50 entfernt war — kein Tick hatte sich geändert.
    Gefragt wird über `resolve_property`, also samt Begrenzung, genau wie im Lauf.

    **Bis zum spätesten Stützpunkt beider Fassungen, nicht nur bis zur Lauflänge**:
    Danach sind beide Verläufe konstant, der Vergleich ist also exakt. Nur bis zur
    Lauflänge verlöre eine Änderung bei Tick 100 in einem Lauf über 40 Ticks — und
    «Als Szenario sichern» legt das Szenario in seiner eigenen Länge ab.

    **Der Schalter «Eigene Werte anwenden» gilt dabei als an**: Aus, wirkte keine
    Abweichung, jede sähe wirkungslos aus und fiele still weg — nach dem
    Wiedereinschalten wären sie verloren.
    """

    from src.market.property_engine import resolve_property

    angewendet = replace(draft, apply_custom_overrides=True)
    basis = prepare_simulation_state(_ohne_abweichungen(angewendet)).properties

    def _wirkt(groesse: str, edit: PropertyEditState) -> bool:
        prop = basis.get_system_property(groesse)
        if prop is None:
            return True
        vorlage = _trajectory_to_edit_state(groesse, prop.trajectory)
        mit = prepare_simulation_state(
            replace(angewendet, abweichungen={groesse: edit}, preisstrategie=None)
        ).properties
        horizont = max(int(draft.rounds), _letzter_tick(edit), _letzter_tick(vorlage)) + 1
        return any(
            resolve_property(groesse, tick, basis) != resolve_property(groesse, tick, mit)
            for tick in range(horizont + 1)
        )

    behalten = {
        groesse: edit for groesse, edit in draft.abweichungen.items() if _wirkt(groesse, edit)
    }
    strategie = draft.preisstrategie
    if strategie is not None and strategie == szenario_preisstrategie(draft):
        strategie = None
    annahmen = _annahmen_bereinigen(draft.modellannahmen, basis) if draft.modellannahmen else {}
    return replace(draft, abweichungen=behalten, preisstrategie=strategie, modellannahmen=annahmen)


def abweichungen_als_sweep(draft: ConfigDraft, state: Any) -> SweepConfig:
    """Die Abweichungen des Entwurfs als Szenario, das auf den Zustand gelegt wird.

    **Eine unbekannte Größe scheitert laut** (P7.13-U13.2): `apply_sweep_overrides`
    überspringt sie still, und eine Abweichung, die nicht ankommt, wäre genau der
    Fehler, gegen den das Paket angetreten ist.
    """

    bekannt = {prop.id for prop in state.properties.system_properties}
    unbekannt = sorted(set(draft.abweichungen) - bekannt)
    if unbekannt:
        raise ValueError(f"Abweichungen für unbekannte Systemgrößen: {unbekannt}")
    return SweepConfig(
        id="abweichungen",
        name="Abweichungen vom gewählten Szenario",
        description="Abweichungen aus dem Assistenten",
        max_ticks=int(draft.rounds),
        preisstrategie=draft.preisstrategie,
        modellannahmen=dict(draft.modellannahmen or {}),
        property_overrides=property_overrides_from_edits(draft.abweichungen),
    )


def build_custom_sweep_from_draft(draft: ConfigDraft, filename: str = "") -> SweepConfig:
    sweep_name = draft.simulation_name
    # **Der Vorgabename kommt aus der Datei, nicht aus einem Literal** (P7.2-U2.7).
    # Hier stand bis zum 2026-09-11 «Flugverkehr Szenarioplanung MVP» ein zweites
    # Mal — wer den Namen in `simulation_config.json` änderte, hätte jedes
    # gesicherte Szenario unter dem Vorgabenamen statt unter dem Dateinamen
    # abgelegt.
    vorgabe = str(load_config_file("simulation_config.json").get("name", ""))
    if not sweep_name or sweep_name == vorgabe:
        sweep_name = filename or "Dashboard Custom"

    return SweepConfig(
        id="dashboard_custom",
        name=sweep_name,
        description=draft.simulation_description
        or "Benutzerdefinierte Overrides aus dem Dashboard",
        max_ticks=draft.rounds,
        base_price=draft.base_price,
        # **Aus der Datei, nicht aus dem Entwurf** (P7.13-U13.3): Startwerte und
        # Verläufe aus dem Bereich «Modell» wirken nur gespeichert. `property_edits`
        # im Entwurf ist die Eingabe des Modell-Editors, nicht die eines Laufs.
        property_overrides=property_overrides_from_edits(
            extract_property_edits_from_file(draft.properties_file)
        ),
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


def llm_config_from_draft(draft: ConfigDraft) -> LLMConfig | None:
    """Welches Sprachmodell dieser Entwurf benutzt — oder `None`, wenn keines (P3.4).

    **Die eine Ableitungsregel.** Sie hat zwei Leser: `prepare_simulation_state`
    legt das Ergebnis in `state.config.llm` ab, und `run_launcher` baut seinen
    `OllamaClient` daraus. Vorher hatte jeder seine eigene Ableitung, und
    `state.config.llm` las überhaupt niemand — der Client entstand direkt aus
    `RunLaunchConfig`, also stand im Zustand etwas anderes als im Lauf.

    `None` heißt «ohne Sprachmodell»: `mock_llm` beantwortet die Frage, welches
    Modell rechnet, mit «keines». Ein `LLMConfig` mit Vorgabewerten
    zurückzugeben wäre hier eine Aussage über ein Modell, das nie gerufen wird.
    """

    if draft.mock_llm:
        return None
    # **Kein Rückfall auf einen Vorgabewert.** Ein leeres Modellfeld ist ein
    # Befund und keine Gelegenheit, `llama3.2` einzusetzen: Der erste Anlauf
    # dieser Funktion schrieb `draft.model.strip() or DEFAULT_MODEL`, und damit
    # wurde aus «kein Modell angegeben» stillschweigend ein Lauf mit dem
    # Vorgabemodell — dieselbe erfundene Vorgabe, die P1.9-W5.1 im Dashboard
    # abgeräumt hat. Leer weitergegeben landet der Wert in `state.config.llm`,
    # und `validate_config` meldet ihn.
    return LLMConfig(
        model=draft.model.strip(),
        base_url=draft.base_url.strip(),
        temperature=float(draft.temperature),
        max_tokens=int(draft.max_tokens),
    )


def _eigene_werte_weichen_ab(draft: ConfigDraft) -> bool:
    """Ob die eigenen Werte des Entwurfs etwas an der ausgelieferten Datei ändern.

    **Seit P7.13-U13.3 ist das nur noch der Startpreis.** Startwerte und Verläufe
    kommen aus der Datei (`build_custom_sweep_from_draft`); der Startpreis bleibt
    vorerst die eine Eingabe des Bereichs «Modell», die ungespeichert wirkt (von
    Haiko entschieden am 2026-09-15, eigenes Paket).
    """

    return draft.base_price is not None


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

    # Ein gewähltes Preset gilt **unvermischt** (seit P1.1). Vorher wurde erst
    # das Preset angewendet und danach der Entwurf darübergelegt — und weil
    # `apply_custom_overrides` per Default an ist und der Entwurf die
    # Datei-Defaults aus `properties.json` mitführt, hat die zweite Runde die
    # erste stillschweigend zurückgedreht: `business_as_usual` verspricht eine
    # konstante CO₂-Abgabe von 50 und rechnete im Dashboard trotzdem mit dem
    # Sprung auf 120 in Tick 15. Über die CLI (`run_single_sweep`) stimmte es,
    # nur dieser Pfad nicht. Wer von einem Preset ausgehen und dann eigene
    # Werte setzen will, ändert es im Schritt «Verläufe» (P7.13-U13.2).
    # **Der Rahmen wird hier gesetzt** (P2.0-B). Nur an dieser Stelle ist
    # bekannt, welches Szenario gilt — nach `apply_sweep_overrides` stehen nur
    # noch Zahlen im Zustand, aus denen sich kein Name zurückgewinnen lässt.
    #
    # **Er folgt der Wahl des Nutzers, nicht dem internen Pfad.** Der erste
    # Anlauf hängte ihn an den Zweig, der die Overrides anwendet — und weil
    # `apply_custom_overrides` per Vorgabe an ist, hätte ein Lauf mit der
    # Standard-Ausgangslage das Etikett «eigene Werte» getragen, ohne dass
    # jemand etwas geändert hat. Der Wirkungstest hat das gemeldet: Das Feld
    # erreichte plötzlich die Simulation, die es vorher nachweislich nicht
    # erreichte.
    if draft.scenario_mode == "sweep" and draft.sweep_id:
        sweep_path = SWEEPS_DIR / f"{draft.sweep_id}.json"
        if not sweep_path.is_file():
            sweep_path = Path(draft.sweep_id)
        sweep = load_sweep_config(sweep_path)
        state.rahmen = Rahmenszenario(id=sweep.id, name=sweep.name, quelle="preset")
        state = apply_sweep_overrides(state, sweep)
    elif draft.scenario_mode == "custom":
        state.rahmen = Rahmenszenario(id="eigen", name="Eigene Werte", quelle="eigen")
    else:
        # Auch das ist ein Rahmen — die ausgelieferten Dateien tragen eigene
        # exogene Verläufe. Er hieß bisher nur nicht so, und deshalb sah es aus,
        # als liefe der Lauf «ohne Szenario».
        state.rahmen = Rahmenszenario(
            id="standard",
            name="Standard-Ausgangslage",
            quelle="standard",
        )

    if draft.scenario_mode != "sweep" and (
        draft.apply_custom_overrides or draft.scenario_mode == "custom"
    ):
        custom = build_custom_sweep_from_draft(draft)
        state = apply_sweep_overrides(state, custom)
        # **Geänderte Werte heißen «eigen», auch unter der Standard-Ausgangslage**
        # (P7.13, gemessen am 2026-09-15): Mit «Eigene Werte anwenden» und einem im
        # Modell auf 99 gesetzten CO₂-Startwert rechnete der Lauf mit 99 und stand
        # im Artefakt als «Standard-Ausgangslage». Ohne Änderung bleibt es der
        # Standard — der Schalter ist per Vorgabe an.
        if _eigene_werte_weichen_ab(draft):
            state.rahmen = Rahmenszenario(id="eigen", name="Eigene Werte", quelle="eigen")

    # **Abweichungen liegen auf dem Szenario** (P7.13-U13.2), unter demselben
    # Schalter wie die eigenen Werte — und anders als diese auch auf einem
    # Rahmenszenario. Ohne Abweichung bleibt ein Szenario unvermischt. Der Rahmen
    # sagt es: Ein geändertes Szenario steht nicht als unverändertes im Artefakt.
    if (draft.apply_custom_overrides or draft.scenario_mode == "custom") and (
        draft.abweichungen or draft.preisstrategie or draft.modellannahmen
    ):
        state = apply_sweep_overrides(state, abweichungen_als_sweep(draft, state))
        basis = state.rahmen
        state.rahmen = Rahmenszenario(
            id=basis.id if basis else "standard",
            name=basis.name if basis else "Standard-Ausgangslage",
            quelle="abgeleitet",
            abweichungen=sorted(draft.abweichungen)
            + (["preisstrategie"] if draft.preisstrategie else [])
            # **Und die Modellannahmen mit Namen** (P7.13-U13.5): `abschnitt.wert`,
            # bei Segmenten mit Kennung — ein Lauf mit anderer Ziel-Auslastung steht
            # sonst ununterscheidbar neben einem mit anderer CO₂-Abgabe.
            + _annahmen_namen(draft.modellannahmen),
        )

    state.clock.max_ticks = int(draft.rounds)
    if draft.use_seed and draft.seed is not None:
        state.config.seed = int(draft.seed)

    # **Das Sprachmodell gehört in den Zustand** (P3.4). Bis dahin las
    # `state.config.llm` kein Laufpfad: Der Client entstand direkt aus
    # `RunLaunchConfig`, im Zustand stand weiter, was in der Config-Datei stand,
    # und `validate_draft` musste die Werte deshalb eigens danebenprüfen.
    #
    # Bei `mock_llm` bleibt das Feld unberührt — gerufen wird nichts, also
    # beschreibt es nichts, und `compute_mode` sagt das im Artefakt.
    llm = llm_config_from_draft(draft)
    if llm is not None:
        state.config.llm = llm

    return state


def validate_draft(draft: ConfigDraft) -> list[str]:
    """Was an dieser Konfiguration einen Lauf scheitern lassen würde.

    Leere Liste heißt startklar. Absichtlich nicht werfend: Die Oberfläche will
    alle Befunde auf einmal zeigen, statt sie einzeln aus Ausnahmen zu klauben.
    Scheitert schon das Bauen des States (fehlende oder kaputte Config-Datei),
    ist das ebenfalls ein Befund und keine Ausnahme, die nach oben durchschlägt.
    """

    # **Vor** dem Bauen des States, nicht danach (P1.9-W1.6): Ein eingeschalteter
    # Zufallsstartwert ohne Wert lässt `draft_to_launch_config` mit
    # `TypeError: int() argument ... not 'NoneType'` sterben — kein Befund,
    # ein Absturz. Erreichbar ist das heute nicht, und zwar aus dem schlechtesten
    # denkbaren Grund: Der Render-Rückfall in `mode_step` schreibt vorher
    # stillschweigend eine 42 in den Entwurf. **W5.1 räumt genau das weg** und
    # macht den Absturz damit erreichbar; diese Prüfung steht deshalb davor.
    #
    # Die CLI kommt an dieser Stelle nicht vorbei, weil sie den Schalter gar
    # nicht kennt: Dort ist ein fehlender Seed schlicht keiner.
    if draft.use_seed and draft.seed is None:
        return [
            issue(
                "Zufallsstartwert ist eingeschaltet, aber keiner angegeben. "
                "Entweder eine Zahl eintragen oder den Schalter ausschalten — "
                "dann rechnet der Lauf mit dem Standardwert.",
                field="seed",
            )
        ]

    try:
        state = prepare_simulation_state(draft)
    except Exception as exc:  # noqa: BLE001 - eine unlesbare Config ist ein Befund, kein Absturz
        return [f"Konfiguration konnte nicht geladen werden: {exc}"]

    errors = collect_state_errors(state)

    # **Hier stand bis P3.4 eine zweite Prüfung der Sprachmodell-Felder.** Sie
    # war nötig, solange sie den State nicht erreichten: Der Client entstand
    # direkt aus `RunLaunchConfig`, und `collect_state_errors` prüfte deshalb die
    # Werte aus der Config-Datei statt die eingestellten — ein Draft mit
    # temperature=5.0 galt als fehlerfrei.
    #
    # Seit `prepare_simulation_state` sie nach `state.config.llm` schreibt, prüft
    # `collect_state_errors` genau die eingestellten Werte, und die zweite
    # Prüfung lieferte jeden Befund **doppelt** — einmal als «config.llm: …» und
    # einmal als «Technik: …», mit demselben Feld daran. Nachgemessen am
    # 2026-09-05, deshalb ist sie weg.
    #
    # Die Bedingung, die sie trug, gilt weiter und liegt jetzt in
    # `llm_config_from_draft`: Bei `mock_llm` fasst niemand Modellname,
    # Temperatur oder Antwortlänge an, also darf ein leeres Modellfeld in beiden
    # unteren Rechenmodi keinen Lauf verhindern.
    return errors


def issues_by_field(errors: list[str]) -> dict[str, list[str]]:
    """Befunde nach dem Feld gruppieren, an dem sie hängen.

    Was kein Feld trägt, taucht hier nicht auf — solche Befunde gehören in die
    gesammelte Liste vor dem Start, nicht unter ein Eingabefeld. Die Zuordnung
    kommt aus `src/validation.py` und nicht aus einer Tabelle hier: Eine
    Schlüsselwort-Tabelle bräche still, sobald jemand einen Meldungstext
    umformuliert.
    """

    grouped: dict[str, list[str]] = {}
    for entry in errors:
        name = field_of(entry)
        if name:
            grouped.setdefault(name, []).append(str(entry))
    return grouped


def unfielded_issues(errors: list[str]) -> list[str]:
    """Die Befunde, für die es kein Eingabefeld gibt."""

    return [str(entry) for entry in errors if not field_of(entry)]


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
        # **Die Abweichungen, nicht `property_edits`** (P7.13-U13.3): Nur sie
        # erreichen den Lauf.
        summary["property_overrides"] = [
            {
                "property_id": edit.property_id,
                "baseline": edit.baseline,
                "rules": edit.rules,
            }
            for edit in draft.abweichungen.values()
        ]
    return summary


def sweep_ziel(filename: str) -> Path:
    """Wohin ein Szenario unter diesem Namen gesichert wird — ohne etwas zu schreiben.

    Eine eigene Funktion, damit sich **vor** dem Sichern fragen lässt, ob es
    die Datei schon gibt. Die Regel ist dieselbe wie beim Schreiben, weil
    `save_custom_sweep_preset` sie hier holt: Leerzeichen werden Unterstriche,
    alles klein, `.json` angehängt, wenn es fehlt.
    """

    safe_name = filename.strip().replace(" ", "_").lower()
    if not safe_name.endswith(".json"):
        safe_name = f"{safe_name}.json"
    return SWEEPS_DIR / safe_name


def szenario_zum_sichern(draft: ConfigDraft, filename: str) -> SweepConfig:
    """Was «Als Szenario sichern» ablegt: das gewählte Szenario samt seinen Abweichungen.

    **Bis zum 2026-09-14 war es die Standard-Ausgangslage** (P7.13-U13.2 Teil 3):
    Gebaut wurde aus `property_edits`, der vollen Kopie der Dateiwerte, und aus der
    Länge des Entwurfs. Mit «Business as Usual» gewählt entstand ein Szenario mit
    dem CO₂-Sprung auf 120 und 200 statt konstant 50, 40 statt 120 Ticks, ohne
    Preisstrategie und mit 16 statt 6 Systemgrößen.

    **Die Regel ist dieselbe wie beim Rechnen** in `prepare_simulation_state`: das
    Szenario, darauf die Abweichungen, sofern «Eigene Werte anwenden» an ist.
    Meilensteine und Kohärenzbegründung eines Rahmens gehen nicht mit — sie
    beschreiben das unveränderte Szenario. Gesichert wird immer als Stresstest mit
    der Herkunft «eigen» (P2.2).
    """

    eigene = draft.apply_custom_overrides or draft.scenario_mode == "custom"
    name = build_custom_sweep_from_draft(draft, filename=filename).name
    if draft.scenario_mode == "sweep" and draft.sweep_id:
        pfad = SWEEPS_DIR / f"{draft.sweep_id}.json"
        basis = load_sweep_config(pfad if pfad.is_file() else Path(draft.sweep_id))
        verlaeufe = {o.property_id: o for o in basis.property_overrides}
        strategie = basis.preisstrategie
        beschreibung = f"Abgeleitet von «{basis.name}»."
        grundlage = basis
    else:
        grundlage = build_custom_sweep_from_draft(draft, filename=filename)
        # Aus der Datei, wie beim Rechnen (P7.13-U13.3).
        verlaeufe = {o.property_id: o for o in grundlage.property_overrides}
        strategie = None
        beschreibung = grundlage.description
    annahmen = {k: dict(v) for k, v in (grundlage.modellannahmen or {}).items()}
    if eigene:
        for override in property_overrides_from_edits(draft.abweichungen):
            verlaeufe[override.property_id] = override
        strategie = draft.preisstrategie or strategie
        for abschnitt, werte in (draft.modellannahmen or {}).items():
            if abschnitt == "population":
                ziel = annahmen.setdefault("population", {})
                for segment, felder in werte.items():
                    ziel[segment] = {**ziel.get(segment, {}), **felder}
            else:
                annahmen[abschnitt] = {**annahmen.get(abschnitt, {}), **werte}
    return grundlage.model_copy(
        update={
            "id": filename,
            "name": name,
            "description": draft.simulation_description or beschreibung,
            "rationale": "Erstellt im Dashboard als eigenes Szenario.",
            "art": "stresstest",
            "kohaerenz": None,
            "herkunft": "eigen",
            "preisstrategie": strategie,
            "modellannahmen": annahmen,
            "property_overrides": list(verlaeufe.values()),
            "milestones": [],
        }
    )


def save_custom_sweep_preset(draft: ConfigDraft, filename: str) -> Path:
    """Persistiert den aktuellen Entwurf als Sweep unter configs/sweeps/."""

    SWEEPS_DIR.mkdir(parents=True, exist_ok=True)
    target = sweep_ziel(filename)
    sweep = szenario_zum_sichern(draft, filename=target.stem)
    # **Der Name ist, was eingegeben wurde** (Befund 13 der Abnahme, 2026-10-01).
    # Ohne eigenen Laufnamen hieß das Szenario wie seine Datei: Aus «Abnahme V6»
    # wurde in der Auswahl «abnahme_v6». Die Kennung bleibt der Dateiname.
    eingabe = filename.strip().removesuffix(".json").strip()
    if eingabe and sweep.name == target.stem:
        sweep = sweep.model_copy(update={"name": eingabe})
    payload = sweep.model_dump(mode="json")
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target
