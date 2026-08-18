"""CLI entrypoint: generate run_scenario.md/json for a completed run."""

from __future__ import annotations

import argparse

from src.reporting.output_writer import OUTPUT_DIR
from src.reporting.run_scenario_generator.pipeline import generate_and_save_run_scenario
from src.reporting.state_explorer import resolve_run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate run_scenario.md/json for a completed run."
    )
    parser.add_argument("--run-id", required=True, help="Existing outputs/<run_id>/ directory")
    parser.add_argument(
        "--outputs-root",
        default=str(OUTPUT_DIR),
        help="Outputs root (default: outputs/)",
    )
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Skip LLM and use deterministic template narrative.",
    )
    args = parser.parse_args(argv)

    llm = None
    if not args.template_only:
        from src.llm import get_llm

        llm = get_llm()

    result = generate_and_save_run_scenario(
        args.run_id,
        llm,
        run_dir=resolve_run_dir(args.run_id, outputs_root=args.outputs_root),
        prefer_llm=not args.template_only,
    )
    print(result["paths"]["markdown"])
    print(result["paths"]["json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
