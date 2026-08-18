"""LangGraph project entry for Technology-Lab simulation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.orchestration.langgraph_adapter import get_build_options
from src.orchestration.langgraph_workflow import build_playground_stategraph


def build_stategraph():
    return build_playground_stategraph()


try:
    build_options = get_build_options()
except Exception:
    build_options = {"max_rounds": {"type": "int", "default": 2}}


try:
    graph = build_stategraph()
except Exception as e:
    graph = None
    _build_error = e


def get_build_error():
    return globals().get("_build_error")
