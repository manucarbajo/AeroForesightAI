from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from src.figure_generator import (
    RunSeries,
    extract_series_from_run_dir,
    generate_all_figures,
    generate_run_figures,
    plot_factor_states,
    plot_price_vs_booking,
    plot_scenario_comparison,
)


def _write_sample_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    ticks = [
        {
            "tick": i,
            "booking_rate": 0.5 + i * 0.01,
            "market_price_after_feedback_eur": 120.0 + i,
            "carbon_tax_level": 50.0 if i < 15 else 120.0,
            "income_index": 1.0,
        }
        for i in range(1, 21)
    ]
    (run_dir / "tick_mechanics.json").write_text(json.dumps({"ticks": ticks}), encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(json.dumps({"simulation_name": "Test Run"}), encoding="utf-8")
    (run_dir / "timeseries").mkdir(exist_ok=True)
    with (run_dir / "timeseries" / "factors.csv").open("w", encoding="utf-8") as handle:
        handle.write("tick,F1,F2\n")
        for i in range(1, 21):
            handle.write(f"{i},F1.1,F2.1\n")
    with (run_dir / "timeseries" / "age_property.csv").open("w", encoding="utf-8") as handle:
        handle.write("tick,age_group,booking_rate\n")
        for i in range(1, 6):
            handle.write(f"{i},18-25,0.45\n")
            handle.write(f"{i},51-65,0.55\n")


class TestFigureGenerator:
    def test_extract_series_from_run_dir(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_run_"))
        try:
            run_dir = tmpdir / "run_test"
            _write_sample_run(run_dir)
            series = extract_series_from_run_dir(run_dir)
            assert len(series.ticks) == 20
            assert series.booking_rate[0] == 0.51
            assert series.carbon_tax[14] == 120.0
        finally:
            shutil.rmtree(tmpdir)

    def test_plot_functions_write_png(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_plot_"))
        try:
            series_a = RunSeries(
                label="A",
                ticks=[1, 2, 3],
                booking_rate=[0.5, 0.52, 0.54],
                ticket_price=[100.0, 101.0, 102.0],
            )
            series_b = RunSeries(
                label="B",
                ticks=[1, 2, 3],
                booking_rate=[0.6, 0.58, 0.56],
                ticket_price=[110.0, 109.0, 108.0],
            )
            out = Path(tmpdir)
            p1 = plot_scenario_comparison([series_a, series_b], out / "cmp.png", metric="booking")
            p2 = plot_price_vs_booking(series_a, out / "pvb.png")
            p3 = plot_factor_states(
                RunSeries(label="X", factor_ticks=[1, 2], factor_values={"F1": [1.1, 1.2]}),
                out / "fac.png",
            )
            assert p1.is_file() and p1.stat().st_size > 0
            assert p2.is_file() and p2.stat().st_size > 0
            assert p3.is_file() and p3.stat().st_size > 0
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_run_figures_writes_manifest(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_run_gen_"))
        try:
            run_dir = Path(tmpdir) / "run_test"
            _write_sample_run(run_dir)
            result = generate_run_figures(run_dir)
            assert len(result.figure_paths) == 6
            assert (run_dir / "figures" / "manifest.json").is_file()
            assert (run_dir / "figures" / "price_vs_booking.png").is_file()
        finally:
            shutil.rmtree(tmpdir)

    def test_generate_all_figures_skip_sweeps(self):
        tmpdir = Path(tempfile.mkdtemp(prefix="fig_all_"))
        try:
            run_dir = Path(tmpdir) / "run_ref"
            fig_dir = Path(tmpdir) / "figures"
            _write_sample_run(run_dir)
            result = generate_all_figures(
                output_dir=fig_dir,
                reference_run_dir=run_dir,
                run_sweeps=False,
            )
            assert len(result.figure_paths) >= 5
            assert (fig_dir / "price_vs_booking.png").is_file()
            assert (fig_dir.parent / "scenario_runs.md").is_file()
        finally:
            shutil.rmtree(tmpdir)
