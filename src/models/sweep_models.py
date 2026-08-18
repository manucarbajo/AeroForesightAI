"""Sweep configuration models for M8 (Foresight-Szenarien).

A SweepConfig defines parameter overrides that modify the default simulation
configuration to model a specific future scenario. Overrides can target:
- system_property trajectory baselines and rules
- initial factor states
- simulation clock settings (max_ticks)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PropertyOverride(BaseModel):
    """Override for a single system property's trajectory."""

    property_id: str
    baseline: float | None = None
    rules: list[dict[str, Any]] | None = None  # replaces trajectory.rules if provided


class FactorOverride(BaseModel):
    """Override for a factor's initial state."""

    factor_id: str
    initial_state: str  # e.g. "F2.2"


class MilestoneCheck(BaseModel):
    """A checkpoint to evaluate during the sweep at a specific tick."""

    tick: int
    description: str
    check_property: str | None = None  # system property to read
    check_factor: str | None = None  # factor to read
    expected_value: Any = None  # optional expected value for logging
    expected_factor_state: str | None = None  # e.g. "F2.2"


class SweepConfig(BaseModel):
    """Configuration for a single parameter sweep scenario."""

    id: str
    name: str
    description: str
    rationale: str = ""  # Why these parameters were chosen
    max_ticks: int = 50
    base_price: float | None = None  # P2.3: override price_model.base_price
    property_overrides: list[PropertyOverride] = Field(default_factory=list)
    factor_overrides: list[FactorOverride] = Field(default_factory=list)
    milestones: list[MilestoneCheck] = Field(default_factory=list)


class SweepResult(BaseModel):
    """Result of a single sweep execution."""

    sweep_id: str
    sweep_name: str
    ticks_completed: int
    final_factor_states: dict[str, str]  # F1 -> F1.2 etc
    final_properties: dict[str, float]  # property_id -> value
    consistency_score: float = 0.0
    stability_index: float = 0.0
    conflicts: list[str] = Field(default_factory=list)
    milestone_results: list[dict[str, Any]] = Field(default_factory=list)


class SweepSummary(BaseModel):
    """Aggregated results of all sweeps."""

    total_sweeps: int = 0
    results: list[SweepResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
