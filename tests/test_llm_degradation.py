"""P0.1: Ein ausgefallenes Sprachmodell darf nicht wie ein erfolgreicher Lauf aussehen.

Die Tests hier gehen den Weg von hinten nach vorn: Erst der Client, der nicht
mehr still mockt, dann der Agent, der den Ausfall festhält, dann das Artefakt,
das ihn nach außen trägt, und zuletzt der Banner, der ihn zeigt.
"""

from __future__ import annotations

import json
import logging
from argparse import Namespace

import pytest
import requests

from src.agents.agent_node import AgentNode
from src.config_loader import build_initial_state
from src.llm.studio_helpers import LocalOllama, MockLLM
from src.logging_setup import configure_logging, progress_logging
from src.models.llm_models import LLMDegradation, LLMIncident
from src.reporting.output_writer import save_llm_incidents, save_run_metadata


class _FailingLLM:
    """Ein Backend, das jeden Aufruf verweigert — und mitzählt, wie oft gefragt wurde."""

    def __init__(self, message: str = "Ollama nicht erreichbar") -> None:
        self.message = message
        self.calls = 0

    def call(self, prompt: str) -> str:
        self.calls += 1
        raise RuntimeError(self.message)


def _consumer_node(llm) -> tuple[AgentNode, object]:
    state = build_initial_state()
    consumer = next(agent for agent in state.agents if agent.id == "consumer")
    return AgentNode(config=consumer, llm=llm), state


# --- Der Client mockt nicht mehr still -------------------------------------


def test_local_ollama_raises_instead_of_faking_an_answer(monkeypatch) -> None:
    """Der Kern des Findings: `LocalOllama` gab bei Netzwerkfehlern eine Mock-Antwort zurück."""

    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    def _refuse(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "post", _refuse)

    with pytest.raises(RuntimeError) as excinfo:
        LocalOllama().call("Wie ist die Lage?")

    # Die alte Fassung hätte hier ein NO_OP-JSON geliefert.
    assert "connection refused" in str(excinfo.value)


def test_mock_llm_stays_a_deliberate_backend() -> None:
    """`--mock-llm` ist kein Ausfall: `MockLLM` antwortet weiterhin ohne Fehler."""

    payload = json.loads(MockLLM().call("Wie ist die Lage?"))

    assert payload["actions"] == ["NO_OP"]
    assert payload["reasoning"] == "mock"


# --- Der Agent hält den Ausfall fest ---------------------------------------


def test_failing_llm_records_exactly_one_incident() -> None:
    llm = _FailingLLM()
    node, state = _consumer_node(llm)
    state.clock.current_tick = 7

    updated = node.invoke(state)

    assert len(updated.llm_incidents) == 1
    incident = updated.llm_incidents[0]
    assert incident.tick == 7
    assert incident.caller == "agent:consumer"
    assert incident.kind == "no_op_emitted"
    assert "Ollama nicht erreichbar" in incident.error


def test_failing_llm_does_not_reach_for_a_second_backend() -> None:
    """Der zweite Versuch über `get_llm()` war der Weg, auf dem Mock-Daten hereinkamen."""

    llm = _FailingLLM()
    node, state = _consumer_node(llm)

    node.invoke(state)

    assert llm.calls == 1


def test_failing_llm_still_produces_a_round_result() -> None:
    """Ein Aussetzer beendet den Lauf nicht — der Agent setzt sichtbar aus."""

    node, state = _consumer_node(_FailingLLM())

    updated = node.invoke(state)
    response = updated.round_results[-1].agent_responses[0]

    assert response.agent_id == "consumer"
    assert response.actions == ["NO_OP"]
    assert updated.round_results[-1].events == []


def test_parallel_agents_carry_their_incidents_back() -> None:
    """Die Agenten laufen auf tiefen Kopien — was nicht eingesammelt wird, geht verloren.

    Beim ersten Anlauf von P0.1 fehlten genau deshalb Provider und Regulator in
    `llm_incidents.json`, obwohl das Log ihren Ausfall zeigte.
    """

    from src.agents.parallel_round_node import ParallelRoundNode

    state = build_initial_state()
    state.clock.current_tick = 1
    node = ParallelRoundNode(agents=state.agents, llm=_FailingLLM())

    updated = node.invoke(state)

    callers = {incident.caller for incident in updated.llm_incidents}
    assert "agent:provider" in callers
    assert "agent:regulator" in callers


def test_successful_run_records_nothing() -> None:
    class _WorkingLLM:
        def call(self, prompt: str) -> str:
            return json.dumps(
                {"reasoning": "ok", "actions": ["NO_OP"], "state_changes": [], "events": []}
            )

    node, state = _consumer_node(_WorkingLLM())

    assert node.invoke(state).llm_incidents == []


# --- Die Zusammenfassung ----------------------------------------------------


def test_degradation_summary_collapses_ticks() -> None:
    incidents = [
        LLMIncident(tick=3, caller="agent:consumer", kind="no_op_emitted", error="x"),
        LLMIncident(tick=3, caller="agent:provider", kind="no_op_emitted", error="y"),
        LLMIncident(tick=1, caller="scenario_node", kind="call_failed", error="z"),
    ]

    summary = LLMDegradation.from_incidents(incidents)

    assert summary.degraded is True
    assert summary.incident_count == 3
    assert summary.degraded_ticks == [1, 3]


def test_clean_run_summary_is_not_degraded() -> None:
    summary = LLMDegradation.from_incidents([])

    assert summary.degraded is False
    assert summary.incident_count == 0
    assert summary.degraded_ticks == []


# --- Die Artefakte ----------------------------------------------------------


def _run_args() -> Namespace:
    return Namespace(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
        no_market=False,
        simulation_name=None,
        simulation_description=None,
    )


def test_metadata_marks_a_degraded_run(tmp_path) -> None:
    state = build_initial_state()
    state.llm_incidents.append(
        LLMIncident(tick=4, caller="agent:provider", kind="no_op_emitted", error="boom")
    )

    save_run_metadata(state, _run_args(), run_dir=tmp_path, run_id="run_test")
    metadata = json.loads((tmp_path / "run_metadata.json").read_text(encoding="utf-8"))

    assert metadata["degraded"] is True
    assert metadata["llm_incident_count"] == 1
    assert metadata["llm_degraded_ticks"] == [4]


def test_metadata_says_so_even_when_nothing_broke(tmp_path) -> None:
    """Die Felder stehen immer drin — sonst wäre ihr Fehlen nicht deutbar."""

    save_run_metadata(build_initial_state(), _run_args(), run_dir=tmp_path, run_id="run_test")
    metadata = json.loads((tmp_path / "run_metadata.json").read_text(encoding="utf-8"))

    assert metadata["degraded"] is False
    assert metadata["llm_incident_count"] == 0


def test_incident_file_is_written_only_when_there_are_incidents(tmp_path) -> None:
    assert save_llm_incidents([], run_dir=tmp_path) is None
    assert not (tmp_path / "llm_incidents.json").exists()

    path = save_llm_incidents(
        [LLMIncident(tick=2, caller="scenario_node", kind="call_failed", error="timeout")],
        run_dir=tmp_path,
    )

    assert path is not None
    written = json.loads((tmp_path / "llm_incidents.json").read_text(encoding="utf-8"))
    assert written[0]["caller"] == "scenario_node"
    assert written[0]["tick"] == 2


# --- Der Weg ins Fortschrittsfenster ---------------------------------------


def test_log_lines_reach_the_progress_callback() -> None:
    """Ohne diesen Handler bliebe das Fortschrittsfenster nach der print-Umstellung leer."""

    lines: list[str] = []
    logger = logging.getLogger("src.test.progress")

    with progress_logging(lines.append):
        logger.warning("Ollama antwortet nicht")

    assert any("Ollama antwortet nicht" in line for line in lines)


def test_progress_handler_is_removed_afterwards() -> None:
    lines: list[str] = []
    logger = logging.getLogger("src.test.progress")

    with progress_logging(lines.append):
        pass
    logger.warning("nach dem Lauf")

    assert lines == []


def test_console_handler_ignores_a_later_stdout_redirect() -> None:
    """Der Konsolen-Handler bindet seinen Stream beim Einrichten, nicht beim Schreiben.

    Darauf beruht die Arbeitsteilung im Run-Launcher: `configure_logging` läuft
    **vor** dem `redirect_stdout`, deshalb geht eine Logzeile einmal auf die
    Konsole und einmal über `progress_logging` ins Dashboard — nicht zweimal
    durch den Tee.
    """

    import contextlib
    import io

    root = logging.getLogger()
    original_handlers = list(root.handlers)
    root.handlers.clear()
    try:
        console = io.StringIO()
        configure_logging(stream=console)

        tee = io.StringIO()
        with contextlib.redirect_stdout(tee):
            logging.getLogger("src.test.redirect").warning("Ollama antwortet nicht")

        assert "Ollama antwortet nicht" in console.getvalue()
        assert tee.getvalue() == ""
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)


def test_configure_logging_is_idempotent() -> None:
    configure_logging()
    root = logging.getLogger()
    before = len(root.handlers)

    configure_logging()
    configure_logging()

    assert len(root.handlers) == before
