"""Playground runner for the full Technology-Lab simulation.

This script is intentionally thin: it loads the playground environment and then
forwards all run configuration to the real AP3 entrypoint in `src.run_simulation`.

Use this when you want to exercise the complete program from the `haiko_playground`
folder while keeping LangSmith / LangGraph environment variables active.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


try:
    from src.studio_helpers import load_env
except Exception:  # pragma: no cover - fallback for direct execution
    from studio_helpers import load_env


def _default_int(name: str, fallback: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None or str(raw_value).strip() == "":
        return fallback
    try:
        return int(raw_value)
    except ValueError:
        return fallback


def _default_float(name: str, fallback: float) -> float:
    raw_value = os.environ.get(name)
    if raw_value is None or str(raw_value).strip() == "":
        return fallback
    try:
        return float(raw_value)
    except ValueError:
        return fallback


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full Technology-Lab simulation from haiko_playground.")
    parser.add_argument(
        "--preset",
        choices=("quick_test", "full_ap3"),
        default=os.environ.get("SIM_PRESET"),
        help="Optional AP3 preset for faster local runs.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        help="LLM model name passed through to src.run_simulation.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        help="Ollama base URL passed through to src.run_simulation.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=_default_float("OLLAMA_TEMPERATURE", 0.7),
        help="LLM temperature.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=_default_int("OLLAMA_MAX_TOKENS", 2048),
        help="Maximum tokens per response.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=_default_int("SIM_ROUNDS", 40),
        help="Number of rounds to simulate. Defaults to the AP3 quarterly horizon (40).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=_default_int("SIM_RUNS", 1),
        help="Number of independent runs.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=os.environ.get("SIM_SEED") and _default_int("SIM_SEED", 0),
        help="Optional base seed for deterministic multi-run sequencing.",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=os.environ.get("SIM_RESUME"),
        help="Resume from a checkpoint file path or run id.",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=os.environ.get("SIM_CHECKPOINT_DIR", str(ROOT / "outputs" / "checkpoints")),
        help="Checkpoint directory used by AP3.",
    )
    parser.add_argument(
        "--no-market",
        action="store_true",
        help="Disable the market node.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce console output.",
    )
    parser.add_argument("--no-protocol", action="store_true", help="Do not generate protocol output.")
    parser.add_argument("--no-scenarios", action="store_true", help="Do not generate scenarios output.")
    return parser


def main() -> int:
    # Load .env and prompt for missing LangSmith secrets when needed.
    load_env()

    # Keep LangSmith tracing enabled by default in the playground when the user has
    # not explicitly chosen a different setting.
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "Technology-Lab Playground")

    parser = _build_parser()
    args = parser.parse_args()

    preset_defaults = {
        "quick_test": {"rounds": 4, "runs": 1, "seed": 42, "model": os.environ.get("OLLAMA_MODEL", "llama3")},
        "full_ap3": {"rounds": 40, "runs": 1, "seed": 42, "model": os.environ.get("OLLAMA_MODEL", "llama3.2")},
    }
    selected_preset = preset_defaults.get(args.preset, {})

    model = args.model or selected_preset.get("model", "llama3.2")
    rounds = args.rounds if args.rounds is not None else int(selected_preset.get("rounds", 40))
    runs = args.runs if args.runs is not None else int(selected_preset.get("runs", 1))
    seed = args.seed if args.seed is not None else selected_preset.get("seed")

    # Forward directly into the real CLI entrypoint so the complete AP3 pipeline runs.
    forwarded_argv = [
        "src.run_simulation",
        "--model",
        model,
        "--base-url",
        args.base_url,
        "--temperature",
        str(args.temperature),
        "--max-tokens",
        str(args.max_tokens),
        "--rounds",
        str(rounds),
        "--runs",
        str(runs),
        "--checkpoint-dir",
        args.checkpoint_dir,
    ]

    if seed is not None:
        forwarded_argv.extend(["--seed", str(seed)])
    if args.resume:
        forwarded_argv.extend(["--resume", args.resume])
    if args.no_market:
        forwarded_argv.append("--no-market")
    if args.quiet:
        forwarded_argv.append("--quiet")
    if args.no_protocol:
        forwarded_argv.append("--no-protocol")
    if args.no_scenarios:
        forwarded_argv.append("--no-scenarios")

    from src.run_simulation import main as run_simulation_main

    previous_argv = sys.argv[:]
    try:
        sys.argv = forwarded_argv
        return run_simulation_main()
    finally:
        sys.argv = previous_argv


if __name__ == "__main__":
    raise SystemExit(main())