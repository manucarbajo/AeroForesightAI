from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import requests

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.checkpoint_manager import CheckpointManager
from src.config_loader import build_initial_state
from src.llm_client import OllamaClient, OllamaConfig
from src.nodes.scenario_agent_node import ScenarioAgentNode, render_scenarios_markdown
from src.output_writer import (
    save_cib_matrix,
    save_event_log,
    save_final_narrative,
    save_price_history,
    save_protocol,
    save_protocol_markdown,
    save_round_history,
    save_run_metadata,
    save_scenarios,
    save_scenarios_markdown,
    save_segment_analysis,
)
from src.protocol_generator import build_protocol_payload, render_protocol_markdown
from src.simulation_runner import MultiRunResult, SimulationRunner
from src.studio_helpers import get_llm


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Challenge-3 simulation (AP3).")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name, e.g. llama3.2")
    parser.add_argument(
        "--base-url",
        default="http://localhost:11434",
        help="Ollama base URL, default: http://localhost:11434",
    )
    parser.add_argument("--temperature", type=float, default=0.7, help="LLM temperature")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Max tokens per response")
    parser.add_argument(
        "--rounds",
        type=int,
        default=None,
        help="Override max rounds (uses configs/simulation_config.json by default).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of independent runs to execute.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional base seed used for deterministic multi-run sequencing.",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume from a checkpoint file path or run id.",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=str(Path("outputs") / "checkpoints"),
        help="Directory used for AP3 checkpoints.",
    )
    parser.add_argument(
        "--no-market",
        action="store_true",
        help="Disable minimal MarketNode (no price_history updates).",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce per-round console output.")
    parser.add_argument("--no-protocol", action="store_true", help="Do not generate protocol output.")
    parser.add_argument("--no-scenarios", action="store_true", help="Do not generate scenarios from CIB matrix.")
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Use the Studio mock LLM backend (or LocalOllama/transformers via env) instead of OllamaClient.",
    )
    parser.add_argument(
        "--use-local-ollama",
        action="store_true",
        help="Require and use a locally running Ollama model (uses `ollama ps` to verify).",
    )
    parser.add_argument(
        "--ollama-wait-seconds",
        type=int,
        default=180,
        help="Maximum seconds to wait for local Ollama model to become ready (used with --use-local-ollama).",
    )
    return parser.parse_args()


def _prefixed_name(prefix: str, filename: str) -> str:
    return f"{prefix}{filename}" if prefix else filename


def _run_output_subdir(prefix: str) -> str | None:
    if not prefix:
        return None
    return prefix[:-1] if prefix.endswith("_") else prefix


def _save_run_outputs(
    state,
    args: argparse.Namespace,
    llm: OllamaClient,
    *,
    prefix: str = "",
) -> dict[str, str | None]:
    """Persist the standard simulation artefacts for one completed run."""

    output_subdir = _run_output_subdir(prefix)

    event_log_path = save_event_log(state.event_log, filename="event_log.json", output_subdir=output_subdir)
    price_history_path = save_price_history(
        state.price_history,
        filename="price_history.json",
        output_subdir=output_subdir,
    )
    round_history_path = save_round_history(
        state.round_results,
        filename="round_history.json",
        output_subdir=output_subdir,
    )
    metadata_path = save_run_metadata(state, args, filename="run_metadata.json", output_subdir=output_subdir)
    segment_analysis_path = save_segment_analysis(
        state.round_results,
        filename="segment_analysis.json",
        output_subdir=output_subdir,
    )
    final_narrative_path = save_final_narrative(
        state,
        filename="final_narrative.md",
        output_subdir=output_subdir,
    )
    cib_matrix_path = save_cib_matrix(state, filename="cib_matrix.json", output_subdir=output_subdir)

    protocol_path = None
    protocol_md_path = None
    if not args.no_protocol:
        protocol_payload = build_protocol_payload(state)
        protocol_path = save_protocol(
            protocol_payload,
            filename="protocol.json",
            output_subdir=output_subdir,
        )
        protocol_md_path = save_protocol_markdown(
            render_protocol_markdown(protocol_payload),
            filename="protocol.md",
            output_subdir=output_subdir,
        )

    scenarios_path = None
    scenarios_md_path = None
    if not args.no_scenarios and state.cib_matrix is not None:
        scenario_node = ScenarioAgentNode(llm=llm)
        state = scenario_node.invoke(state)
        scenarios_payload = {
            "scenarios": state.cib_matrix.metadata.get("scenarios", []) if state.cib_matrix.metadata else []
        }
        scenarios_path = save_scenarios(
            scenarios_payload,
            filename="scenarios.json",
            output_subdir=output_subdir,
        )
        scenarios_md_path = save_scenarios_markdown(
            render_scenarios_markdown(scenarios_payload, state),
            filename="scenarios.md",
            output_subdir=output_subdir,
        )

    return {
        "event_log": event_log_path,
        "price_history": price_history_path,
        "round_history": round_history_path,
        "run_metadata": metadata_path,
        "segment_analysis": segment_analysis_path,
        "final_narrative": final_narrative_path,
        "cib_matrix": cib_matrix_path,
        "protocol": protocol_path,
        "protocol_markdown": protocol_md_path,
        "scenarios": scenarios_path,
        "scenarios_markdown": scenarios_md_path,
    }


def _build_run_args(base_args: argparse.Namespace, *, run_index: int, seed: int | None) -> SimpleNamespace:
    return SimpleNamespace(
        model=base_args.model,
        base_url=base_args.base_url,
        temperature=base_args.temperature,
        max_tokens=base_args.max_tokens,
        no_market=base_args.no_market,
        no_protocol=getattr(base_args, "no_protocol", False),
        no_scenarios=getattr(base_args, "no_scenarios", False),
        quiet=getattr(base_args, "quiet", False),
        run_index=run_index,
        seed=seed,
    )


def _write_multi_run_summary(
    *,
    summary_path: Path,
    result: MultiRunResult,
    run_artifacts: list[dict[str, str | None]],
) -> None:
    summary_payload: dict[str, Any] = {
        "aggregate": result.aggregate,
        "runs": [],
    }
    for run_result, artifacts in zip(result.runs, run_artifacts, strict=False):
        summary_payload["runs"].append(
            {
                "run_id": run_result.run_id,
                "seed": run_result.seed,
                "rounds": run_result.final_state.clock.current_round,
                "quarter_timeline": [quarter.label for quarter in run_result.quarter_timeline],
                "checkpoint_paths": [str(path) for path in run_result.checkpoint_paths],
                "artifacts": artifacts,
            }
        )

    summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = _parse_args()

    if args.mock_llm:
        llm = get_llm()
    elif args.use_local_ollama:
        try:
            proc = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
            out = proc.stdout
        except Exception as exc:
            raise RuntimeError("Failed to run `ollama ps`. Ensure Ollama CLI is installed and on PATH.") from exc

        model_tag = args.model
        if model_tag not in out and f"{model_tag}:latest" not in out:
            raise RuntimeError(
                f"Requested local Ollama model '{model_tag}' not found in `ollama ps` output. Start it with `ollama run {model_tag}`."
            )

        llm = OllamaClient(
            OllamaConfig(
                base_url=args.base_url,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
        )
        print(f"Waiting up to {args.ollama_wait_seconds}s for local Ollama model '{args.model}' to become ready...")
        generate_url = args.base_url.rstrip("/") + "/api/generate"
        deadline = time.time() + float(args.ollama_wait_seconds)
        warmed = False
        test_payload = {"model": args.model, "prompt": "Hello", "stream": False, "options": {"temperature": 0.0, "num_predict": 8}}
        while time.time() < deadline:
            try:
                resp = requests.post(generate_url, json=test_payload, timeout=(5, 30))
                if resp.status_code == 200:
                    warmed = True
                    print("Local Ollama model ready.")
                    break
                else:
                    print(f"Model not ready yet (status={resp.status_code}), retrying...")
            except Exception as exc:
                print(f"Waiting for model: {exc}")
            time.sleep(2.0)

        if not warmed:
            raise RuntimeError(
                f"Local Ollama model '{args.model}' did not become ready within {args.ollama_wait_seconds} seconds."
            )
    else:
        llm = OllamaClient(
            OllamaConfig(
                base_url=args.base_url,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
        )

    runner = SimulationRunner(llm=llm)
    repo_root = Path(__file__).resolve().parents[1]
    ck_path = Path(args.checkpoint_dir)
    if not ck_path.is_absolute():
        ck_path = repo_root / ck_path
    checkpoint_manager = CheckpointManager(ck_path)

    if args.resume is not None and args.runs != 1:
        raise ValueError("--resume is only supported for single-run execution")

    if args.resume is not None:
        state = None
        if not args.quiet:
            print(f"Resuming simulation from checkpoint reference: {args.resume}")
        final_state = runner.run(
            state,
            checkpoint_store=checkpoint_manager,
            resume_from=args.resume,
            run_id="run-resume",
        )
        artifacts = _save_run_outputs(final_state, _build_run_args(args, run_index=1, seed=final_state.config.seed), llm)
        if not args.quiet:
            print("Saved: " + ", ".join([path for path in artifacts.values() if path]))
            print(
                f"\nDone. rounds={final_state.clock.current_round}, events={len(final_state.event_log)}, "
                f"round_results={len(final_state.round_results)}, price_history={len(final_state.price_history)}"
            )
        return 0

    base_state = build_initial_state()
    if args.rounds is not None:
        base_state.clock.max_rounds = int(args.rounds)
    if args.seed is not None:
        base_state.config.seed = int(args.seed)

    if args.runs == 1:
        if not args.quiet:
            print(
                f"Simulation start: rounds={base_state.clock.max_rounds}, model={args.model}, "
                f"market={'off' if args.no_market else 'on'}"
            )

        final_state = runner.run(
            base_state,
            seed=args.seed,
            checkpoint_store=checkpoint_manager,
            run_id="run-001",
        )
        artifacts = _save_run_outputs(final_state, _build_run_args(args, run_index=1, seed=args.seed), llm)
        if not args.quiet:
            print("Saved: " + ", ".join([path for path in artifacts.values() if path]))
            print(
                f"\nDone. rounds={final_state.clock.current_round}, events={len(final_state.event_log)}, "
                f"round_results={len(final_state.round_results)}, price_history={len(final_state.price_history)}"
            )
        return 0

    if not args.quiet:
        print(
            f"Simulation start: runs={args.runs}, rounds={base_state.clock.max_rounds}, model={args.model}, "
            f"market={'off' if args.no_market else 'on'}"
        )

    if args.rounds is not None:
        base_state.clock.max_rounds = int(args.rounds)

    if not args.quiet:
        print(f"Starting multi-run: runs={args.runs}, rounds={base_state.clock.max_rounds}")

    multi_result = runner.run_multi(
        args.runs,
        base_state=base_state,
        checkpoint_store=checkpoint_manager,
    )

    all_artifacts: list[dict[str, str | None]] = []
    for index, run_result in enumerate(multi_result.runs, start=1):
        prefix = f"run_{index:03d}_"
        run_args = _build_run_args(args, run_index=index, seed=run_result.seed)
        artifacts = _save_run_outputs(run_result.final_state, run_args, llm, prefix=prefix)
        all_artifacts.append(artifacts)

    if checkpoint_manager is not None:
        for run_result in multi_result.runs:
            try:
                ck_existing = checkpoint_manager.list_checkpoints(run_result.run_id)
                if not ck_existing:
                    checkpoint_manager.save(run_result.final_state, run_id=run_result.run_id, round_number=run_result.final_state.clock.current_round)
            except Exception as exc:
                print(f"Warning: failed to ensure checkpoint for {run_result.run_id}: {exc}")

    summary_path = Path("outputs") / "multi_run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_multi_run_summary(summary_path=summary_path, result=multi_result, run_artifacts=all_artifacts)
    except Exception as exc:
        print(f"Warning: failed to write multi_run_summary.json: {exc}")

    for idx, run_result in enumerate(multi_result.runs, start=1):
        seed_info = run_result.seed
        print(f"Run {idx:03d}: run_id={run_result.run_id} seed={seed_info} checkpoints={run_result.checkpoint_paths}")

    summary_path = Path("outputs") / "multi_run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    _write_multi_run_summary(summary_path=summary_path, result=multi_result, run_artifacts=all_artifacts)

    if not args.quiet:
        print(
            "Saved: "
            + ", ".join(
                [
                    str(summary_path),
                    *[path for artifacts in all_artifacts for path in artifacts.values() if path],
                ]
            )
        )
        print(f"\nDone. runs={len(multi_result.runs)}, aggregate={multi_result.aggregate}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
