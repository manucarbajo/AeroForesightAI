from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config_loader import build_initial_state
from src.llm_client import OllamaClient, OllamaConfig
from src.nodes.agent_node import AgentNode
from src.nodes.environment_node import EnvironmentNode
from src.nodes.market_node import MarketNode
from src.nodes.orchestrator_node import OrchestratorNode
from src.validation import validate_state
from src.output_writer import (save_event_log,
                               save_price_history,
                               save_round_history,
                               save_run_metadata,
                               save_segment_analysis,
                               save_final_narrative,
                               save_cib_matrix,
                               save_protocol,
                               save_protocol_markdown,
                               save_scenarios,
                               save_scenarios_markdown)
from src.nodes.cib_extractor_node import CIBExtractorNode
from src.protocol_generator import build_protocol_payload, render_protocol_markdown
from src.nodes.scenario_agent_node import ScenarioAgentNode, render_scenarios_markdown


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Challenge-2 simulation (AP3).")
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
        "--no-market",
        action="store_true",
        help="Disable minimal MarketNode (no price_history updates).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce per-round console output.",
    )
    parser.add_argument("--no-protocol", action="store_true", help="Do not generate protocol output.")
    parser.add_argument("--no-scenarios", action="store_true", help="Do not generate scenarios from CIB matrix.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    llm = OllamaClient(
        OllamaConfig(
            base_url=args.base_url,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    )

    state = build_initial_state()
    if args.rounds is not None:
        state.clock.max_rounds = int(args.rounds)

    validate_state(state)

    orchestrator = OrchestratorNode(state.agents)
    agent_by_id = {a.id: a for a in state.agents}
    consumer = AgentNode(agent_by_id["consumer"], llm=llm)
    provider = AgentNode(agent_by_id["provider"], llm=llm)
    regulator = AgentNode(agent_by_id["regulator"], llm=llm)

    market = MarketNode()
    environment = EnvironmentNode(prefer_agent_order=["regulator", "provider", "consumer"])

    if not args.quiet:
        print(
            f"Simulation start: rounds={state.clock.max_rounds}, model={args.model}, "
            f"market={'off' if args.no_market else 'on'}"
        )

    while state.clock.current_round < state.clock.max_rounds:
        state = orchestrator.invoke(state)

        if not args.quiet:
            print(f"\n--- Round {state.clock.current_round}/{state.clock.max_rounds} ---")

        state = consumer.invoke(state)
        if not args.quiet:
            print(f"consumer done (event_log={len(state.event_log)})")

        state = provider.invoke(state)
        if not args.quiet:
            print(f"provider done (event_log={len(state.event_log)})")

        state = regulator.invoke(state)
        if not args.quiet:
            print(f"regulator done (event_log={len(state.event_log)})")

        if not args.no_market:
            state = market.invoke(state)
            if not args.quiet:
                print(f"market done (price_history={len(state.price_history)})")

        state = environment.invoke(state)

        if not args.quiet:
            last_summary = state.round_results[-1].summary.strip().splitlines()[0]
            print(f"environment done :: {last_summary}")

    cib_extractor = CIBExtractorNode()
    state = cib_extractor.invoke(state)

    validate_state(state)

    event_log_path = save_event_log(state.event_log)
    price_history_path = save_price_history(state.price_history)
    round_history_path = save_round_history(state.round_results)
    metadata_path = save_run_metadata(state, args)
    segment_analysis_path = save_segment_analysis(state.round_results)
    final_narrative_path = save_final_narrative(state)
    cib_matrix_path = save_cib_matrix(state)

    protocol_path = None
    protocol_md_path = None
    if not args.no_protocol:
        protocol_payload = build_protocol_payload(state)
        protocol_path = save_protocol(protocol_payload)
        protocol_md_path = save_protocol_markdown(render_protocol_markdown(protocol_payload))

    scenarios_path = None
    scenarios_md_path = None
    if not args.no_scenarios and state.cib_matrix is not None:
        scenario_node = ScenarioAgentNode(llm=llm)
        state = scenario_node.invoke(state)
        scenarios_payload = {"scenarios": state.cib_matrix.metadata.get("scenarios", []) if state.cib_matrix.metadata else []}
        scenarios_path = save_scenarios(scenarios_payload)
        scenarios_md_path = save_scenarios_markdown(render_scenarios_markdown(scenarios_payload, state))

    print(
        "Saved: "
        + ", ".join(
            [p for p in [event_log_path, price_history_path, round_history_path, metadata_path, segment_analysis_path, final_narrative_path, cib_matrix_path, protocol_path, protocol_md_path, scenarios_path, scenarios_md_path] if p]
        )
    )

    print(
        f"\nDone. rounds={state.clock.current_round}, events={len(state.event_log)}, "
        f"round_results={len(state.round_results)}, price_history={len(state.price_history)}"
    )
    print(f"Saved: {event_log_path}, {price_history_path}, {round_history_path}, {metadata_path}, {segment_analysis_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
