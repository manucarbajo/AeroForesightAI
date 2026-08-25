"""Der Lauf im Hintergrund: Thread, Queue, Abholung.

Ein Lauf dauert Minuten und darf den Callback nicht blockieren. Die Mechanik
dahinter — Worker-Thread, Fortschritts-Queue, Zustand beim Abholen — ist
eigener Code und damit eine eigene Fehlerquelle, unabhängig davon, ob die
Simulation selbst rechnet.

Die Simulation wird deshalb hier ersetzt. Was sie tut, prüfen die Tests der
Engine; was hier zählt, ist der Weg ihrer Ausgaben in die Oberfläche.
"""

from __future__ import annotations

import threading
import time

import pytest

from dashboard.web import runner
from dashboard.web.state import initial_draft_dict


@pytest.fixture(autouse=True)
def _leerer_zustand():
    """Kein Job aus einem früheren Test darf hier hineinragen."""

    runner._JOBS.clear()
    yield
    runner._JOBS.clear()


def _warte_auf_ende(job_id: str, sekunden: float = 5.0) -> runner.Job:
    frist = time.monotonic() + sekunden
    while time.monotonic() < frist:
        job = runner.poll(job_id)
        if job is not None and job.done:
            return job
        time.sleep(0.02)
    raise AssertionError("Lauf wurde nicht fertig")


# --- Erfolgsfall -----------------------------------------------------------


def test_a_run_reports_its_progress_and_result(monkeypatch):
    def fake_launch(draft, *, repo_root=None, on_progress=None):
        for tick in (1, 2, 3):
            on_progress(f"[tick {tick}/3] price=100")
        return "fertig"

    monkeypatch.setattr(runner, "launch_from_draft", fake_launch)

    job = _warte_auf_ende(runner.start(initial_draft_dict()))

    assert job.done is True
    assert job.error is None
    assert job.result == "fertig"
    assert len(job.lines) == 3
    assert job.lines[0].startswith("[tick 1/3]")


def test_progress_arrives_while_the_run_is_still_going(monkeypatch):
    """Sonst erschiene das Protokoll erst am Ende — der Sinn wäre weg."""

    freigabe = threading.Event()

    def fake_launch(draft, *, repo_root=None, on_progress=None):
        on_progress("erste Zeile")
        freigabe.wait(timeout=5)
        return "fertig"

    monkeypatch.setattr(runner, "launch_from_draft", fake_launch)
    job_id = runner.start(initial_draft_dict())

    frist = time.monotonic() + 5
    while time.monotonic() < frist:
        job = runner.poll(job_id)
        if job and job.lines:
            break
        time.sleep(0.02)

    assert job.lines == ["erste Zeile"]
    assert job.done is False, "Lauf sollte noch laufen"

    freigabe.set()
    _warte_auf_ende(job_id)


# --- Fehlerfall ------------------------------------------------------------


def test_a_failure_lands_in_the_job_not_in_the_thread(monkeypatch):
    """Eine Ausnahme im Thread wäre sonst unsichtbar — der Lauf hinge ewig."""

    def fake_launch(draft, *, repo_root=None, on_progress=None):
        on_progress("bis hierher")
        raise RuntimeError("Ollama antwortet nicht")

    monkeypatch.setattr(runner, "launch_from_draft", fake_launch)

    job = _warte_auf_ende(runner.start(initial_draft_dict()))

    assert job.done is True
    assert "Ollama antwortet nicht" in job.error
    assert job.lines == ["bis hierher"], "bis dahin Geschriebenes bleibt erhalten"


# --- Nur ein Lauf gleichzeitig ---------------------------------------------


def test_a_second_run_is_refused_while_one_is_active(monkeypatch):
    """`launch_simulation` leitet die Ausgabe des ganzen Prozesses um —
    zwei gleichzeitige Läufe würden sich die Protokolle zerschneiden."""

    freigabe = threading.Event()
    monkeypatch.setattr(
        runner,
        "launch_from_draft",
        lambda draft, **kw: freigabe.wait(timeout=5),
    )

    job_id = runner.start(initial_draft_dict())
    try:
        assert runner.is_running() is True
        with pytest.raises(RuntimeError, match="bereits"):
            runner.start(initial_draft_dict())
    finally:
        freigabe.set()
        _warte_auf_ende(job_id)

    assert runner.is_running() is False


def test_a_new_run_is_possible_once_the_previous_one_finished(monkeypatch):
    monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: "ok")

    _warte_auf_ende(runner.start(initial_draft_dict()))
    zweiter = runner.start(initial_draft_dict())

    assert _warte_auf_ende(zweiter).result == "ok"


# --- Aufräumen -------------------------------------------------------------


def test_polling_an_unknown_job_returns_nothing():
    assert runner.poll("gibt-es-nicht") is None
    assert runner.poll(None) is None


def test_a_finished_job_can_be_forgotten(monkeypatch):
    monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: "ok")
    job_id = runner.start(initial_draft_dict())
    _warte_auf_ende(job_id)

    runner.forget(job_id)

    assert runner.poll(job_id) is None


def test_a_running_job_is_not_forgotten(monkeypatch):
    """Sonst verlöre die Oberfläche mitten im Lauf ihren Faden."""

    freigabe = threading.Event()
    monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: freigabe.wait(timeout=5))
    job_id = runner.start(initial_draft_dict())

    runner.forget(job_id)
    try:
        assert runner.poll(job_id) is not None
    finally:
        freigabe.set()
        _warte_auf_ende(job_id)


def test_the_log_does_not_grow_without_bound(monkeypatch):
    """Ein 500-Tick-Lauf schreibt mehr, als ein Browser darstellen mag."""

    ueberzaehlig = runner.MAX_LOG_LINES + 50

    monkeypatch.setattr(
        runner,
        "launch_from_draft",
        lambda draft, *, repo_root=None, on_progress=None: [
            on_progress(f"Zeile {i}") for i in range(ueberzaehlig)
        ],
    )

    job = _warte_auf_ende(runner.start(initial_draft_dict()), sekunden=10)

    assert len(job.lines) == runner.MAX_LOG_LINES
    assert job.lines[-1] == f"Zeile {ueberzaehlig - 1}", "die jüngsten Zeilen bleiben"
