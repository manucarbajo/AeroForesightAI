"""Simulationsläufe im Hintergrund starten und ihren Fortschritt abholen.

Ein Lauf dauert Minuten — er darf den Callback nicht blockieren. Dash bietet
dafür «background callbacks» mit Diskcache oder Celery an; beides bringt für
eine Ein-Prozess-Workbench mehr Abhängigkeiten und (unter Windows) mehr
Pickling-Ärger als Nutzen. Stattdessen: ein Worker-Thread, eine Queue für die
Fortschrittszeilen, und ein `dcc.Interval`, das sie abholt.

Bewusst nur **ein** Lauf gleichzeitig: `launch_simulation` leitet `stdout` des
gesamten Prozesses um, um an die Fortschrittszeilen zu kommen
(`dashboard/run_launcher.py`). Zwei parallele Läufe würden sich dabei
gegenseitig die Ausgabe abschneiden.
"""

from __future__ import annotations

import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from dashboard.run_launcher import REPO_ROOT, launch_from_draft
from dashboard.web.state import draft_from_dict

#: Wie viele Zeilen das Log höchstens behält. Ein 500-Tick-Lauf schreibt sonst
#: mehr in den Browser, als dieser flüssig darstellen kann.
MAX_LOG_LINES = 2000


@dataclass
class Job:
    job_id: str
    lines: list[str] = field(default_factory=list)
    queue: "queue.Queue[str]" = field(default_factory=queue.Queue)
    result: Any = None
    error: str | None = None
    done: bool = False


_JOBS: dict[str, Job] = {}
_LOCK = threading.Lock()


def is_running() -> bool:
    with _LOCK:
        return any(not job.done for job in _JOBS.values())


def start(draft_data: dict) -> str:
    """Lauf starten und die Job-ID zurückgeben."""

    if is_running():
        raise RuntimeError("Es läuft bereits eine Simulation. Bitte abwarten.")

    job = Job(job_id=uuid.uuid4().hex)
    with _LOCK:
        _JOBS[job.job_id] = job

    draft = draft_from_dict(draft_data)

    def _work() -> None:
        try:
            job.result = launch_from_draft(draft, repo_root=REPO_ROOT, on_progress=job.queue.put)
        except Exception as exc:  # noqa: BLE001 - jeder Fehler gehört ins Log, nicht in den Thread
            job.error = str(exc)
        finally:
            job.done = True

    threading.Thread(target=_work, name=f"sim-{job.job_id[:8]}", daemon=True).start()
    return job.job_id


def poll(job_id: str | None) -> Job | None:
    """Neue Ausgabezeilen einsammeln und den aktuellen Job-Zustand liefern."""

    if not job_id:
        return None
    with _LOCK:
        job = _JOBS.get(job_id)
    if job is None:
        return None

    while True:
        try:
            job.lines.append(job.queue.get_nowait())
        except queue.Empty:
            break
    if len(job.lines) > MAX_LOG_LINES:
        del job.lines[: len(job.lines) - MAX_LOG_LINES]
    return job


def forget(job_id: str | None) -> None:
    """Abgeschlossenen Job vergessen, damit der Speicher nicht mitwächst."""

    if not job_id:
        return
    with _LOCK:
        job = _JOBS.get(job_id)
        if job is not None and job.done:
            _JOBS.pop(job_id, None)
