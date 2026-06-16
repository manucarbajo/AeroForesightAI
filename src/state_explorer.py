"""Grounded chat exploration over completed simulation runs."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from src.checkpoint_manager import CheckpointManager
from src.llm_client import OllamaClient, OllamaConfig
from src.output_writer import OUTPUT_DIR

EXPLORER_INSTRUCTIONS = """You are a simulation explorer for an aviation scenario run.
Answer ONLY using the GROUND TRUTH DATA block below.

Rules:
- Never invent numbers, ticks, prices, booking rates, or events.
- If the answer is not contained in the data, reply exactly:
  "Nicht in den Run-Daten enthalten."
- Prefer tick_mechanics and structured run_summary over agent narratives.
- Booking decisions use the prior tick market price; final ticket price is set after market feedback.
- Cite tick numbers when referencing metrics.
- Answer in the same language as the user question (German if the question is German).
"""


def parse_tick_hint(text: str) -> int | None:
    """Optional tick number from a natural-language question (e.g. 'bei Tick 15')."""

    match = re.search(r"(?:tick|periode)\s*(\d+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


class LLMCallable(Protocol):
    def call(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class RunExplorerContext:
    run_id: str
    run_dir: Path
    tick_mechanics: dict[str, Any]
    event_log: list[dict[str, Any]]
    price_history: list[dict[str, Any]]
    factors_timeseries: list[dict[str, Any]]
    metadata: dict[str, Any]
    focus_tick: int | None
    checkpoint_tick: int | None
    checkpoint_snapshot: dict[str, Any] | None


def resolve_run_dir(run_id: str, *, outputs_root: Path | str | None = None) -> Path:
    root = Path(outputs_root or OUTPUT_DIR)
    run_dir = root / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    return run_dir


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _checkpoint_path(run_dir: Path, run_id: str, tick: int) -> Path | None:
    manager = CheckpointManager(checkpoint_dir=run_dir / "checkpoints")
    candidates = [
        manager.checkpoint_dir / run_id / f"tick_{tick:04d}.json",
        manager.checkpoint_dir / f"tick_{tick:04d}.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _summarize_checkpoint(state: dict[str, Any]) -> dict[str, Any]:
    clock = state.get("clock", {})
    market_metrics = state.get("market_metrics", {})
    return {
        "current_tick": clock.get("current_tick"),
        "max_ticks": clock.get("max_ticks"),
        "market_metrics": market_metrics,
        "factor_states": {
            factor_id: factor.get("current_state")
            for factor_id, factor in (state.get("environment", {}).get("factors") or {}).items()
        },
        "event_count": len(state.get("event_log") or []),
        "population_size": len(state.get("population_individuals") or []),
    }


def load_run_context(
    run_id: str,
    *,
    focus_tick: int | None = None,
    outputs_root: Path | str | None = None,
) -> RunExplorerContext:
    run_dir = resolve_run_dir(run_id, outputs_root=outputs_root)
    tick_mechanics = _load_json(run_dir / "tick_mechanics.json", {"ticks": []})
    event_log = _load_json(run_dir / "event_log.json", [])
    price_history = _load_json(run_dir / "price_history.json", [])
    factors_timeseries = _load_json(run_dir / "factors_timeseries.json", [])
    metadata = _load_json(run_dir / "run_metadata.json", {})

    checkpoint_snapshot = None
    checkpoint_tick = None
    if focus_tick is not None and focus_tick >= 1:
        checkpoint_tick = focus_tick
        ck_path = _checkpoint_path(run_dir, run_id, focus_tick)
        if ck_path is not None:
            payload = json.loads(ck_path.read_text(encoding="utf-8"))
            checkpoint_snapshot = _summarize_checkpoint(payload.get("state", {}))

    return RunExplorerContext(
        run_id=run_id,
        run_dir=run_dir,
        tick_mechanics=tick_mechanics,
        event_log=event_log,
        price_history=price_history,
        factors_timeseries=factors_timeseries,
        metadata=metadata,
        focus_tick=focus_tick,
        checkpoint_tick=checkpoint_tick,
        checkpoint_snapshot=checkpoint_snapshot,
    )


def _select_ticks(context: RunExplorerContext, limit: int = 8) -> list[dict[str, Any]]:
    ticks = list(context.tick_mechanics.get("ticks") or [])
    if not ticks:
        return []
    if context.focus_tick is not None:
        selected = [row for row in ticks if int(row.get("tick", -1)) == context.focus_tick]
        if selected:
            return selected
        nearby = sorted(ticks, key=lambda row: abs(int(row.get("tick", 0)) - context.focus_tick))
        return nearby[:limit]
    if len(ticks) <= limit:
        return ticks
    # Gesamtlauf: Anfang, Ende und gleichmäßige Stichprobe
    if limit >= len(ticks):
        return ticks
    head = ticks[:3]
    tail = ticks[-max(3, limit // 2):]
    middle_budget = max(0, limit - len(head) - len(tail))
    if middle_budget <= 0:
        return head + tail
    step = max(1, (len(ticks) - len(head) - len(tail)) // middle_budget)
    middle = ticks[len(head): len(ticks) - len(tail): step][:middle_budget]
    return head + middle + tail


def _build_run_summary(context: RunExplorerContext) -> dict[str, Any]:
    ticks = list(context.tick_mechanics.get("ticks") or [])
    prices = list(context.price_history)
    if not ticks and not prices:
        return {"note": "Keine Zeitreihen im Run."}

    summary: dict[str, Any] = {
        "ticks_recorded": len(ticks),
        "events_total": len(context.event_log),
    }
    if ticks:
        booking = [float(row["booking_rate"]) for row in ticks if row.get("booking_rate") is not None]
        if booking:
            summary["booking_rate_start"] = booking[0]
            summary["booking_rate_end"] = booking[-1]
            summary["booking_rate_min"] = min(booking)
            summary["booking_rate_max"] = max(booking)
    if prices:
        price_vals = [float(row["price"]) for row in prices if row.get("price") is not None]
        if price_vals:
            summary["ticket_price_start"] = price_vals[0]
            summary["ticket_price_end"] = price_vals[-1]
            summary["ticket_price_min"] = min(price_vals)
            summary["ticket_price_max"] = max(price_vals)
    if context.metadata:
        summary["ticks_completed"] = context.metadata.get("ticks_completed")
        summary["ticks_max"] = context.metadata.get("ticks_max")
        summary["model"] = context.metadata.get("model")
    return summary


def _select_events(context: RunExplorerContext, limit: int = 20) -> list[dict[str, Any]]:
    events = list(context.event_log)
    if context.focus_tick is not None:
        tick_events = [event for event in events if event.get("round_number") == context.focus_tick]
        if tick_events:
            return tick_events
    delta_events = [
        event
        for event in events
        if "[delta:" in str(event.get("description", ""))
    ]
    if delta_events:
        return delta_events[-limit:]
    return events[-limit:]


def _context_tick_limit(context: RunExplorerContext) -> int:
    return 8 if context.focus_tick is not None else 24


def build_grounded_context_block(context: RunExplorerContext) -> str:
    lines = [
        f"run_id={context.run_id}",
        f"simulation={context.metadata.get('simulation_name', context.metadata.get('name', 'unknown'))}",
    ]
    if context.tick_mechanics.get("reading_guide"):
        lines.append(f"reading_guide: {context.tick_mechanics['reading_guide']}")

    lines.append("run_summary:")
    lines.append(json.dumps(_build_run_summary(context), ensure_ascii=False, indent=2))

    selected_ticks = _select_ticks(context, limit=_context_tick_limit(context))
    if selected_ticks:
        lines.append("tick_mechanics:")
        lines.append(json.dumps(selected_ticks, ensure_ascii=False, indent=2))
    else:
        lines.append("tick_mechanics: []")

    selected_events = _select_events(context)
    if selected_events:
        lines.append("event_log:")
        lines.append(json.dumps(selected_events, ensure_ascii=False, indent=2))
    else:
        lines.append("event_log: []")

    if context.price_history:
        if context.focus_tick is not None:
            price_rows = [
                row for row in context.price_history if row.get("round_number") == context.focus_tick
            ]
        else:
            price_rows = context.price_history[-min(24, len(context.price_history)):]
        lines.append("price_history:")
        lines.append(json.dumps(price_rows, ensure_ascii=False, indent=2))

    if context.factors_timeseries:
        if context.focus_tick is not None:
            factor_rows = [
                row for row in context.factors_timeseries if row.get("tick") == context.focus_tick
            ]
        else:
            factor_rows = context.factors_timeseries[-min(24, len(context.factors_timeseries)):]
        if factor_rows:
            lines.append("factors_timeseries:")
            lines.append(json.dumps(factor_rows, ensure_ascii=False, indent=2))

    if context.checkpoint_snapshot is not None:
        lines.append(f"checkpoint_tick_{context.checkpoint_tick}:")
        lines.append(json.dumps(context.checkpoint_snapshot, ensure_ascii=False, indent=2))

    return "\n".join(lines)


class StateExplorer:
    def __init__(
        self,
        context: RunExplorerContext,
        llm: LLMCallable | None = None,
    ) -> None:
        self.context = context
        self.llm = llm or OllamaClient(OllamaConfig(temperature=0.2))

    def build_prompt(self, question: str) -> str:
        grounded = build_grounded_context_block(self.context)
        return (
            f"{EXPLORER_INSTRUCTIONS}\n\n"
            f"GROUND TRUTH DATA:\n{grounded}\n\n"
            f"USER QUESTION:\n{question.strip()}\n\n"
            "ANSWER:"
        )

    def ask(self, question: str) -> str:
        prompt = self.build_prompt(question)
        return self.llm.call(prompt)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grounded state explorer for simulation runs (M9).")
    parser.add_argument("--run-id", required=True, help="Run id under outputs/ (e.g. run_20260614T111705Z).")
    parser.add_argument("--tick", type=int, default=None, help="Focus on a specific tick (loads checkpoint if present).")
    parser.add_argument("--question", type=str, default=None, help="Single question; omit for interactive mode.")
    parser.add_argument("--outputs-root", type=str, default=None, help="Override outputs directory.")
    parser.add_argument("--mock-llm", action="store_true", help="Echo grounded context without calling Ollama.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    context = load_run_context(
        args.run_id,
        focus_tick=args.tick,
        outputs_root=args.outputs_root,
    )

    if args.mock_llm:

        class _EchoLLM:
            def call(self, prompt: str) -> str:
                return (
                    "Mock explorer response (grounded context attached in prompt).\n"
                    "Use without --mock-llm and a running Ollama instance for real answers."
                )

        llm: LLMCallable = _EchoLLM()
    else:
        llm = OllamaClient(OllamaConfig(temperature=0.2))

    explorer = StateExplorer(context, llm=llm)

    if args.question:
        print(explorer.ask(args.question))
        return 0

    print(f"State explorer for {args.run_id} (tick focus={args.tick}). Type 'exit' to quit.")
    while True:
        try:
            question = input("\nFrage> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in {"exit", "quit", "q"}:
            break
        print(explorer.ask(question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
