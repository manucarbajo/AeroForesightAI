"""M7 / P6.G2 — Segment-Divergenz business vs. price_sensitive (≥ 15 pp)."""

from __future__ import annotations

from src.config_loader import build_initial_state, load_properties_config
from src.models.population_models import PopulationConfig
from src.models.state_models import FactorState
from src.population.population_sampler import initialize_population, run_population_tick
from src.simulation_runner import RunnerOptions, SimulationRunner


def _max_business_price_sensitive_gap(population_stats: list) -> tuple[float, int]:
    max_gap = 0.0
    best_tick = 0
    for entry in population_stats:
        segments = entry.get("segments") or {}
        business = float(segments.get("business", {}).get("booking_rate", 0.0))
        price_sensitive = float(segments.get("price_sensitive", {}).get("booking_rate", 0.0))
        gap = abs(business - price_sensitive)
        if gap > max_gap:
            max_gap = gap
            best_tick = int(entry.get("round_number") or 0)
    return max_gap, best_tick


def _recession_factors() -> dict[str, FactorState]:
    return {
        "F4": FactorState(
            id="F4",
            name="F4",
            description="",
            current_state="F4.2",
            possible_states={"F4.2": "Recession"},
        )
    }


class TestSegmentDivergence:
    def test_stress_tick_business_vs_price_sensitive_at_least_15pp(self) -> None:
        """Isolated population tick: F4.2 + lower income_index widens segment booking gap."""
        properties = load_properties_config()
        config = PopulationConfig(segments=[], total_population=5000)
        individuals = initialize_population(properties, config, seed=42)

        _, stats = run_population_tick(
            properties,
            config,
            individuals,
            ticket_price=140.0,
            carbon_tax=80.0,
            factors=_recession_factors(),
            system_properties={"income_index": 0.85, "carbon_tax_level": 80.0},
            seed=42,
        )

        business = stats.segments["business"].booking_rate
        price_sensitive = stats.segments["price_sensitive"].booking_rate
        gap_pp = abs(business - price_sensitive) * 100.0

        assert gap_pp >= 15.0, (
            f"Expected ≥15 pp divergence, got {gap_pp:.1f} pp "
            f"(business={business:.3f}, price_sensitive={price_sensitive:.3f})"
        )
        assert business > price_sensitive, "business should book more under income stress"

    def test_e2e_40_ticks_deterministic_segment_gap_and_saturation(self) -> None:
        """P6.G2 + P2.1 E2E: full pipeline, income ramp (tick 10+), F4.2, saturation active."""
        state = build_initial_state(load_cib=False)
        state.clock.max_ticks = 40
        state.environment.factors["F4"].current_state = "F4.2"

        runner = SimulationRunner(
            llm=lambda prompt: "{}",
            options=RunnerOptions(
                enable_market=True,
                deterministic_only=True,
                checkpoint_interval=0,
                verbose_ticks=False,
            ),
        )
        final = runner.run(state, seed=42, run_id="test_p2_saturation_e2e")

        gap, tick = _max_business_price_sensitive_gap(final.population_stats)
        assert final.clock.current_tick == 40
        assert gap >= 0.15, f"max segment gap {gap * 100:.1f} pp at tick {tick} — need ≥15 pp"
        assert any(
            person.saturation_level > 0 for person in final.population_individuals
        ), "saturation_level should be > 0 for at least one individual after bookings"
        assert max(person.saturation_level for person in final.population_individuals) >= 0.6
