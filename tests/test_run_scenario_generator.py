from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from src.run_scenario_generator import (
    build_factor_profile,
    build_run_narrative,
    build_template_scenario,
    generate_and_save_run_scenario,
    generate_run_scenario,
    load_run_scenario_context,
    render_run_scenario_markdown,
    save_run_scenario_artifacts,
)

FACTOR_HEADER = "tick,F1,F2,F3,F4,F5,F6,F7\n"


def _write_scenario_fixture(run_dir: Path, *, booking_start: float, booking_end: float) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": 3,
                "ticks_max": 3,
                "simulation_name": "Fixture Run",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {
                        "tick": 1,
                        "booking_rate": booking_start,
                        "market_price_after_feedback_eur": 120.0,
                    },
                    {
                        "tick": 2,
                        "booking_rate": (booking_start + booking_end) / 2,
                        "market_price_after_feedback_eur": 125.0,
                    },
                    {
                        "tick": 3,
                        "booking_rate": booking_end,
                        "market_price_after_feedback_eur": 130.0,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "price_history.json").write_text(
        json.dumps(
            [
                {"round_number": 1, "price": 120.0},
                {"round_number": 3, "price": 130.0},
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
                    "description": "[delta:booking:population] booking rate changed (Python delta)",
                }
            ]
        ),
        encoding="utf-8",
    )
    ts_dir = run_dir / "timeseries"
    ts_dir.mkdir(parents=True, exist_ok=True)
    (ts_dir / "population.csv").write_text(
        "tick,business,price_sensitive,booking_rate\n1,0.3,0.4,0.5\n",
        encoding="utf-8",
    )
    (ts_dir / "factors.csv").write_text(
        FACTOR_HEADER
        + "1,F1.1,F2.1,F3.1,F4.1,F5.1,F6.1,F7.1\n"
        + "2,F1.1,F2.1,F3.2,F4.1,F5.1,F6.1,F7.1\n"
        + "3,F1.2,F2.1,F3.2,F4.1,F5.1,F6.2,F7.1\n",
        encoding="utf-8",
    )


class TestRunScenarioGenerator:
    def test_load_context_includes_factor_transitions(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_ctx_"))
        try:
            run_id = "run_fixture"
            run_dir = tmpdir / run_id
            _write_scenario_fixture(run_dir, booking_start=0.6, booking_end=0.4)
            context = load_run_scenario_context(run_id, run_dir=run_dir)
            transitions = context.summary_metrics.get("factor_transitions") or []
            assert any(item["factor_id"] == "F3" for item in transitions)
            assert any(item["factor_id"] == "F1" for item in transitions)
        finally:
            shutil.rmtree(tmpdir)

    def test_run_narrative_mentions_factors(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_narr_"))
        try:
            run_dir = tmpdir / "run_narr"
            _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
            context = load_run_scenario_context("run_narr", run_dir=run_dir)
            profile = build_factor_profile(context)
            narrative = build_run_narrative(context, profile)
            assert "F1" in narrative
            assert "F3" in narrative
            assert "Faktor" in narrative
        finally:
            shutil.rmtree(tmpdir)

    def test_template_produces_factor_grounded_scenarios(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_tpl_"))
        try:
            run_dir = tmpdir / "run_a"
            _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
            context = load_run_scenario_context("run_a", run_dir=run_dir)
            payload = build_template_scenario(context)

            assert payload.get("run_narrative")
            assert payload.get("factor_profile", {}).get("end")
            assert len(payload["summary"]) >= 80
            assert len(payload["scenarios"]) == 3
            for scenario in payload["scenarios"]:
                assert scenario.get("tick_grounding")
                assert scenario.get("story")
                assert len(scenario["story"]) >= 80
                assert "Flughafen" not in scenario["story"]
            kinds = {item["scenario_kind"] for item in payload["scenarios"]}
            assert kinds == {"fortsetzung", "alternative", "spannung"}
        finally:
            shutil.rmtree(tmpdir)

    def test_markdown_renders_factor_profile_and_scenarios(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_md_"))
        try:
            run_dir = tmpdir / "run_md"
            _write_scenario_fixture(run_dir, booking_start=0.55, booking_end=0.5)
            context = load_run_scenario_context("run_md", run_dir=run_dir)
            payload = build_template_scenario(context)
            md = render_run_scenario_markdown(payload, {"run_id": "run_md"})
            assert "Lauf-Narrativ" in md
            assert "Anhaltspunkte aus dem Lauf" in md
            assert "Szenario-Beschreibung" in md
            assert "CIB-Einordnung" not in md
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_and_save_artifacts(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_save_"))
        try:
            run_id = "run_save"
            run_dir = tmpdir / run_id
            _write_scenario_fixture(run_dir, booking_start=0.55, booking_end=0.5)

            result = generate_run_scenario(run_id, llm=None, run_dir=run_dir, prefer_llm=False)
            md_path, json_path = save_run_scenario_artifacts(run_dir, result)

            assert md_path.is_file()
            assert json_path.is_file()
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            assert payload["run_narrative"]
            assert payload["factor_profile"]
            assert len(payload["scenarios"]) == 3
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_and_save_run_scenario_integration(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="scenario_int_"))
        try:
            run_id = "run_int"
            run_dir = tmpdir / run_id
            _write_scenario_fixture(run_dir, booking_start=0.62, booking_end=0.58)

            result = generate_and_save_run_scenario(
                run_id,
                llm=None,
                run_dir=run_dir,
                prefer_llm=False,
            )
            assert Path(result["paths"]["markdown"]).is_file()
            assert Path(result["paths"]["json"]).is_file()
            assert result["source"] == "template"
            assert len(result["scenarios"]) == 3
        finally:
            shutil.rmtree(tmpdir)
