from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from dashboard.config_catalog import (
    apply_sweep_to_draft,
    default_config_draft,
    effective_config_summary,
    extract_market_feedback_from_file,
    extract_saturation_from_file,
    list_sweep_presets,
    prepare_simulation_state,
    save_custom_sweep_preset,
    save_market_feedback_to_file,
    save_saturation_to_file,
)
from dashboard.service import (
    draft_to_launch_config,
    generate_figures_for_run,
    list_run_files,
    list_run_figures,
    list_runs,
    load_run_scenario,
    regenerate_run_scenario,
    run_consistency_checks,
)


def _write_minimal_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps({"ticks_completed": 2, "ticks_max": 2, "total_events": 5}),
        encoding="utf-8",
    )
    (run_dir / "final_narrative.md").write_text("# Test", encoding="utf-8")
    (run_dir / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {
                        "tick": 1,
                        "market_price_after_feedback_eur": 100.0,
                        "booking_rate": 0.5,
                        "booking_rate_delta": None,
                    },
                    {
                        "tick": 2,
                        "market_price_after_feedback_eur": 102.0,
                        "booking_rate": 0.48,
                        "booking_rate_delta": -0.02,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "price_history.json").write_text(
        json.dumps(
            [
                {"round_number": 1, "price": 100.0, "demand_level": 0.5},
                {"round_number": 2, "price": 102.0, "demand_level": 0.48},
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "event_log.json").write_text(
        json.dumps(
            [
                {
                    "round_number": 2,
                    "source_agent": "system",
                    "event_type": "demand_shift",
                    "description": "[delta:booking:population] booking rate 50.0% → 48.0% (-2.0 pp, Python delta)",
                }
            ]
        ),
        encoding="utf-8",
    )


class TestDashboardService:
    def test_list_runs_and_files(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_test_"))
        try:
            run_dir = tmpdir / "run_20260101T120000Z"
            _write_minimal_run(run_dir)
            runs = list_runs(tmpdir)
            assert len(runs) == 1
            assert runs[0].run_id == "run_20260101T120000Z"
            assert runs[0].has_run_scenario is False
            files = list_run_files(run_dir)
            assert any(entry.relative_path == "tick_mechanics.json" for entry in files)
        finally:
            shutil.rmtree(tmpdir)

    def test_consistency_checks_pass_for_aligned_run(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_check_"))
        try:
            run_dir = tmpdir / "run_20260101T120000Z"
            _write_minimal_run(run_dir)
            checks = run_consistency_checks(run_dir)
            statuses = {check.check_id: check.status for check in checks}
            assert statuses["required_files"] == "ok"
            assert statuses["price_alignment"] == "ok"
            assert statuses["delta_events"] == "ok"
        finally:
            shutil.rmtree(tmpdir)


class TestConfigCatalog:
    def test_default_draft_loads_properties_and_factors(self):
        draft = default_config_draft()
        assert draft.rounds >= 1
        assert "carbon_tax_level" in draft.property_edits
        assert "F1" in draft.factor_states
        assert draft.saturation_edit.booking_increase == 0.6
        assert draft.market_feedback_edit.target_booking_rate == 0.37

    def test_save_saturation_and_market_feedback_to_properties_json(self):
        import dashboard.config_catalog as catalog

        tmpdir = Path(tempfile.mkdtemp(prefix="dash_props_"))
        try:
            src = catalog.CONFIGS_DIR / "properties.json"
            dst = tmpdir / "properties.json"
            shutil.copy(src, dst)
            original = catalog.CONFIGS_DIR
            catalog.CONFIGS_DIR = tmpdir

            save_saturation_to_file(
                catalog.SaturationEditState(booking_increase=0.45, utility_penalty_factor=0.8),
                "properties.json",
            )
            save_market_feedback_to_file(
                catalog.MarketFeedbackEditState(
                    target_booking_rate=0.42,
                    marginal_cost_fraction=0.4,
                ),
                "properties.json",
            )

            sat = extract_saturation_from_file("properties.json")
            mf = extract_market_feedback_from_file("properties.json")
            assert sat.booking_increase == 0.45
            assert sat.utility_penalty_factor == 0.8
            assert mf.target_booking_rate == 0.42
            assert mf.marginal_cost_fraction == 0.4

            payload = json.loads(dst.read_text(encoding="utf-8"))
            rule_effect = next(
                r["effect"]
                for r in payload["market_rules"]
                if r.get("effect", {}).get("type") == "booking_yield_feedback"
            )
            assert rule_effect["target_booking_rate"] == 0.42
            assert rule_effect["marginal_cost_fraction"] == 0.4

            catalog.CONFIGS_DIR = original
        finally:
            shutil.rmtree(tmpdir)

    def test_effective_config_summary_includes_mechanics(self):
        draft = default_config_draft()
        summary = effective_config_summary(draft)
        assert "saturation" in summary
        assert "market_feedback" in summary
        assert summary["market_feedback"]["target_booking_rate"] == 0.37

    def test_sweep_presets_available(self):
        sweeps = list_sweep_presets()
        assert len(sweeps) >= 4
        ids = {sweep.id for sweep in sweeps}
        assert "business_as_usual" in ids
        assert "co2_delayed" in ids

    def test_apply_sweep_overrides_carbon_tax(self):
        draft = default_config_draft()
        sweep = next(s for s in list_sweep_presets() if s.id == "co2_delayed")
        draft = apply_sweep_to_draft(draft, sweep)
        assert draft.sweep_id == "co2_delayed"
        carbon = draft.property_edits["carbon_tax_level"]
        assert any(rule.get("active_from_tick") == 25 for rule in carbon.rules)

    def test_prepare_state_with_custom_property_override(self):
        draft = default_config_draft()
        draft.scenario_mode = "custom"
        draft.apply_custom_overrides = True
        draft.rounds = 5
        draft.property_edits["carbon_tax_level"].baseline = 99.0
        draft.property_edits["carbon_tax_level"].rules = [
            {"active_from_tick": 1, "effect": {"type": "set", "value": 99.0}}
        ]
        state = prepare_simulation_state(draft)
        assert state.clock.max_ticks == 5
        prop = next(p for p in state.properties.system_properties if p.id == "carbon_tax_level")
        assert float(prop.trajectory.baseline) == 99.0

    def test_effective_config_summary_includes_overrides(self):
        draft = default_config_draft()
        draft.scenario_mode = "custom"
        draft.apply_custom_overrides = True
        summary = effective_config_summary(draft)
        assert "property_overrides" in summary
        assert summary["config_files"]["properties"] == "properties.json"

    def test_save_custom_sweep_preset(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="sweep_save_"))
        try:
            from dashboard import config_catalog

            original = config_catalog.SWEEPS_DIR
            config_catalog.SWEEPS_DIR = tmpdir
            draft = default_config_draft()
            draft.scenario_mode = "custom"
            draft.apply_custom_overrides = True
            draft.simulation_name = "Test Sweep"
            path = save_custom_sweep_preset(draft, "test_preset")
            assert path.is_file()
            payload = json.loads(path.read_text(encoding="utf-8"))
            assert payload["id"] == "test_preset"
            config_catalog.SWEEPS_DIR = original
        finally:
            shutil.rmtree(tmpdir)

    def test_list_runs_scenario_preview(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_scenario_"))
        try:
            run_dir = tmpdir / "run_20260101T120000Z"
            _write_minimal_run(run_dir)
            (run_dir / "run_scenario.json").write_text(
                json.dumps(
                    {
                        "title": "Drei Zukunftspfade",
                        "summary": "Drei explorative Pfade.",
                        "scenarios": [
                            {
                                "rank": 1,
                                "title": "Wende im Mobilitätsmix",
                                "archetype": "Wende",
                                "what_could_happen": "Policy und Verhalten kippen.",
                            },
                            {
                                "rank": 2,
                                "title": "BAU",
                                "archetype": "BAU",
                                "what_could_happen": "Weiter wie bisher.",
                            },
                            {
                                "rank": 3,
                                "title": "Konflikt",
                                "archetype": "Konflikt",
                                "what_could_happen": "Nachfrage bricht.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            runs = list_runs(tmpdir)
            assert runs[0].has_run_scenario is True
            assert runs[0].scenario_title == "Wende im Mobilitätsmix"
            assert "Top-3:" in (runs[0].scenario_summary or "")
            loaded = load_run_scenario(run_dir)
            assert loaded is not None
            assert loaded["scenarios"][0]["title"] == "Wende im Mobilitätsmix"
        finally:
            shutil.rmtree(tmpdir)

    def test_regenerate_run_scenario(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_regen_"))
        try:
            run_dir = tmpdir / "run_20260101T120000Z"
            _write_minimal_run(run_dir)
            result = regenerate_run_scenario(
                "run_20260101T120000Z",
                run_dir=run_dir,
                mock_llm=True,
                deterministic_only=True,
            )
            assert Path(result["paths"]["json"]).is_file()
            assert Path(result["paths"]["markdown"]).is_file()
        finally:
            shutil.rmtree(tmpdir)

    def test_list_runs_includes_batch_children(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_batch_"))
        try:
            batch_dir = tmpdir / "batch_20260101T120000Z"
            for sub_id in ("run_001", "run_002"):
                _write_minimal_run(batch_dir / sub_id)
            runs = list_runs(tmpdir)
            run_ids = {run.run_id for run in runs}
            assert "batch_20260101T120000Z/run_001" in run_ids
            assert "batch_20260101T120000Z/run_002" in run_ids
        finally:
            shutil.rmtree(tmpdir)

    def test_list_run_figures_and_generate(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="dash_fig_"))
        try:
            run_dir = tmpdir / "run_20260101T120000Z"
            _write_minimal_run(run_dir)
            assert list_run_figures(run_dir) == []
            entries = generate_figures_for_run(run_dir)
            assert len(entries) == 6
            assert any("price_vs_booking.png" in e.relative_path for e in entries)
            listed = list_run_figures(run_dir)
            assert len(listed) == 6
            assert any(entry.title == "Preis vs. Booking" for entry in listed)
        finally:
            shutil.rmtree(tmpdir)

    def test_draft_to_launch_config_multi_run(self):
        draft = default_config_draft()
        draft.run_count = 3
        config = draft_to_launch_config(draft)
        assert config.runs == 3
        draft = default_config_draft()
        draft.scenario_mode = "sweep"
        draft.sweep_id = "business_as_usual"
        draft.rounds = 50
        config = draft_to_launch_config(draft)
        assert config.sweep_id == "business_as_usual"
        assert config.rounds == 50
        assert config.run_id is None
