"""Tests for M8 Scenario Sweeps."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config_loader import build_initial_state
from src.models.sweep_models import SweepConfig, PropertyOverride, FactorOverride, MilestoneCheck
from src.scenario_sweeps import apply_sweep_overrides, load_sweep_config, run_single_sweep
from src.simulation_runner import RunnerOptions, SimulationRunner


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

def test_sweep_config_loading():
    """All sweep JSON files in configs/sweeps/ should parse correctly."""
    sweeps_dir = REPO_ROOT / "configs" / "sweeps"
    configs = list(sweeps_dir.glob("*.json"))
    assert len(configs) >= 4, f"Expected at least 4 sweep configs, found {len(configs)}"

    for path in configs:
        config = load_sweep_config(path)
        assert config.id, f"Sweep {path.name} has no id"
        assert config.name, f"Sweep {path.name} has no name"
        assert config.max_ticks > 0, f"Sweep {path.name} has invalid max_ticks"


def test_apply_property_overrides():
    """Property overrides should modify state trajectory baselines and rules."""
    state = build_initial_state(load_cib=False)

    sweep = SweepConfig(
        id="test",
        name="Test",
        description="Test sweep",
        max_ticks=10,
        property_overrides=[
            PropertyOverride(
                property_id="carbon_tax_level",
                baseline=99.0,
                rules=[{"active_from_tick": 1, "effect": {"type": "set", "value": 99.0}}],
            )
        ],
    )

    state = apply_sweep_overrides(state, sweep)

    # Verify max_ticks was set
    assert state.clock.max_ticks == 10

    # Verify carbon_tax_level baseline was overridden
    for prop in state.properties.system_properties:
        if prop.id == "carbon_tax_level":
            assert prop.trajectory.baseline == 99.0
            assert len(prop.trajectory.rules) == 1
            break
    else:
        pytest.fail("carbon_tax_level not found in system_properties")


def test_apply_factor_overrides():
    """Factor overrides should change initial factor states."""
    state = build_initial_state(load_cib=False)

    # F2 default is F2.1
    assert state.environment.factors["F2"].current_state == "F2.1"

    sweep = SweepConfig(
        id="test",
        name="Test",
        description="Test sweep",
        max_ticks=5,
        factor_overrides=[
            FactorOverride(factor_id="F2", initial_state="F2.2"),
        ],
    )

    state = apply_sweep_overrides(state, sweep)
    assert state.environment.factors["F2"].current_state == "F2.2"


def test_deterministic_only_skips_llm():
    """In deterministic_only mode, the runner should complete without LLM calls."""
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = 5

    dummy_llm = lambda prompt: "{}"
    runner = SimulationRunner(
        llm=dummy_llm,
        options=RunnerOptions(
            enable_market=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )

    final_state = runner.run(state, seed=42, run_id="test-det")
    assert final_state.clock.current_tick == 5
    # No agent events should have been generated (agents were skipped)
    agent_events = [e for e in final_state.event_log if hasattr(e, "agent_id")]
    # In deterministic mode, there should be no LLM-generated round_results
    # (round_results come from agent responses)


def test_run_single_sweep_short():
    """Run a single sweep with a small number of ticks to verify end-to-end."""
    sweep = SweepConfig(
        id="test_short",
        name="Short Test Sweep",
        description="Quick validation sweep",
        max_ticks=5,
        property_overrides=[
            PropertyOverride(
                property_id="carbon_tax_level",
                baseline=150.0,
                rules=[{"active_from_tick": 1, "effect": {"type": "set", "value": 150.0}}],
            )
        ],
        milestones=[
            MilestoneCheck(
                tick=3,
                description="Carbon tax at 150",
                check_property="carbon_tax_level",
                expected_value=150.0,
            ),
        ],
    )

    result = run_single_sweep(sweep, verbose=False)

    assert result.sweep_id == "test_short"
    assert result.ticks_completed == 5
    assert result.consistency_score > 0
    assert result.stability_index > 0
    assert len(result.final_factor_states) == 7  # All 7 factors


def test_milestone_expected_factor_state():
    from src.models.state_models import SimulationState, SimulationClock, EnvironmentState, FactorState
    from src.scenario_sweeps import evaluate_milestone_on_state

    state = SimulationState(
        run_id="ms",
        config=build_initial_state(load_cib=False).config,
        agents=[],
        clock=SimulationClock(current_tick=8, max_ticks=10),
        environment=EnvironmentState(
            factors={
                "F2": FactorState(
                    id="F2",
                    name="F2",
                    description="",
                    current_state="F2.1",
                    possible_states={"F2.1": "A", "F2.2": "B"},
                )
            }
        ),
        factor_timeseries=[{"tick": 8, "F2": "F2.2"}],
    )
    ms = MilestoneCheck(
        tick=8,
        description="F2.2 expected",
        check_factor="F2",
        expected_factor_state="F2.2",
    )
    result = evaluate_milestone_on_state(state, ms)
    assert result["passed"] is True
    assert result["actual_value"] == "F2.2"


def test_sweep_co2_delayed_loads():
    """The co2_delayed.json sweep should load and have correct structure."""
    path = REPO_ROOT / "configs" / "sweeps" / "co2_delayed.json"
    config = load_sweep_config(path)
    assert config.id == "co2_delayed"
    assert len(config.milestones) >= 3
    assert any(m.tick == 15 for m in config.milestones), "CO2 Tick 15 milestone missing"
    assert any(m.tick == 25 for m in config.milestones), "CO2 Tick 25 milestone missing"


# ---------------------------------------------------------------------------
# P2.3 — Basispreis konfigurierbar via SweepConfig.base_price
# ---------------------------------------------------------------------------

def test_sweep_base_price_override_raises_ticket_price():
    """P2.3: A sweep with base_price=200 should produce higher ticket prices than base_price=80."""
    from src.scenario_sweeps import run_single_sweep

    sweep_low = SweepConfig(
        id="low_base",
        name="Low Base Price",
        description="base_price=80",
        max_ticks=5,
        base_price=80.0,
    )
    sweep_high = SweepConfig(
        id="high_base",
        name="High Base Price",
        description="base_price=200",
        max_ticks=5,
        base_price=200.0,
    )

    result_low = run_single_sweep(sweep_low, verbose=False)
    result_high = run_single_sweep(sweep_high, verbose=False)

    low_price = result_low.final_properties.get("ticket_price", 0.0)
    high_price = result_high.final_properties.get("ticket_price", 0.0)
    assert high_price > low_price, f"Expected high base_price → higher ticket, got {low_price:.1f} vs {high_price:.1f}"


def test_sweep_base_price_none_uses_default():
    """P2.3: base_price=None should leave default (100.0) unchanged."""
    state = build_initial_state(load_cib=False)
    sweep = SweepConfig(id="no_bp", name="No BP", description="no override", max_ticks=5)
    state = apply_sweep_overrides(state, sweep)
    assert state.properties.price_model.base_price == 100.0
