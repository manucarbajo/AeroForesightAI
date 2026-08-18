"""CLI entrypoint: generate global or per-run scenario figures."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.reporting.figure_generator.global_figures import DEFAULT_FIGURES_DIR, generate_all_figures
from src.reporting.figure_generator.run_figures import generate_run_figures
from src.reporting.output_writer import OUTPUT_DIR


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Challenge-4 scenario figures (M10).")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_FIGURES_DIR),
        help="Directory for PNG outputs.",
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        default=None,
        help="Use an existing outputs/<run_id>/ directory as reference run.",
    )
    parser.add_argument(
        "--reference-ticks", type=int, default=40, help="Ticks for synthetic reference run."
    )
    parser.add_argument("--sweep-ticks", type=int, default=50, help="Ticks per Foresight sweep.")
    parser.add_argument(
        "--run-only",
        type=str,
        default=None,
        metavar="RUN_DIR",
        help="Only generate per-run figures into outputs/<run_id>/figures/ (no global sweep batch).",
    )
    parser.add_argument(
        "--skip-sweeps",
        action="store_true",
        help="Skip sweep re-run (use only reference run figures).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.run_only:
        run_dir = args.run_only
        if not Path(run_dir).is_absolute():
            candidate = Path(OUTPUT_DIR) / run_dir
            run_dir = str(candidate if candidate.is_dir() else Path(run_dir))
        result = generate_run_figures(run_dir)
        print(f"Generated {len(result.figure_paths)} run figures in {result.run_dir / 'figures'}")
        for title, path in result.figure_paths.items():
            print(f"  - {title}: {path}")
        return 0

    run_dir = args.run_dir
    if run_dir and not Path(run_dir).is_absolute():
        candidate = Path(OUTPUT_DIR) / run_dir
        run_dir = str(candidate if candidate.is_dir() else Path(run_dir))

    result = generate_all_figures(
        output_dir=args.output_dir,
        reference_run_dir=run_dir,
        reference_ticks=args.reference_ticks,
        sweep_ticks=args.sweep_ticks,
        run_sweeps=not args.skip_sweeps,
    )
    print(f"Generated {len(result.figure_paths)} figures in {args.output_dir}")
    for title, path in result.figure_paths.items():
        print(f"  - {title}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
