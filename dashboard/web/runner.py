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
import re
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
    #: Wird gesetzt, wenn jemand abbricht. Der Tick-Loop fragt ihn zwischen zwei
    #: Ticks (P1.9-W4.5) — ein Thread lässt sich von außen nicht sauber beenden.
    stop: threading.Event = field(default_factory=threading.Event)


#: Die Fortschrittszeile des Tick-Loops: `[tick  14/40] 0.14s (…) — price=…`.
#: Gelesen, nicht geschätzt — steht dort nichts, gibt es keine Prozentzahl
#: (Invariante 1: Zahlen werden nicht erfunden).
_TICK_LINE = re.compile(r"\[tick\s+(\d+)\s*/\s*(\d+)\]")

#: Wie viele Zeilen die Oberfläche höchstens bekommt. Die Konsole zeigt
#: ohnehin nur die letzten; alles davor waere Ballast im Browser.
VISIBLE_LINES = 200


@dataclass(frozen=True)
class Progress:
    """Wie weit der **aktive** Lauf ist — für jede Sitzung, nicht nur für seine.

    Der Fortschritt hing bis P1.7 am Job, und an den kam nur heran, wer dessen
    Kennung hatte. Ein zweiter Tab und eine neu geladene Seite sahen deshalb
    nichts. Dieselbe Klasse von Sitzungsblindheit wie beim Laufzustand, nur eine
    Ebene weiter.
    """

    job_id: str
    tick: int | None
    total: int | None
    line: str
    lines: tuple[str, ...] = ()

    @property
    def fraction(self) -> float | None:
        """Anteil zwischen 0 und 1 — oder `None`, wenn es keine Zahl gibt.

        `None` heißt «unbestimmt» und gehört als unbestimmter Balken dargestellt.
        Eine Null an dieser Stelle waere eine Behauptung.
        """

        if not self.tick or not self.total:
            return None
        return min(1.0, self.tick / self.total)


_JOBS: dict[str, Job] = {}
_LOCK = threading.Lock()


def is_running() -> bool:
    with _LOCK:
        return any(not job.done for job in _JOBS.values())


def _drain(job: Job) -> None:
    """Neue Zeilen aus der Queue in die Liste holen.

    Unter dem Lock, weil seit P1.7 **mehrere** Sitzungen gleichzeitig danach
    fragen: Der Takt jeder offenen Seite ruft `progress()`. Ohne Lock koennten
    zwei Threads die Queue verschraenkt leeren und die Zeilen vertauschen.
    """

    with _LOCK:
        while True:
            try:
                job.lines.append(job.queue.get_nowait())
            except queue.Empty:
                break
        if len(job.lines) > MAX_LOG_LINES:
            del job.lines[: len(job.lines) - MAX_LOG_LINES]


def active() -> Job | None:
    """Der eine Lauf, der gerade rechnet — es kann nur einen geben."""

    with _LOCK:
        for job in _JOBS.values():
            if not job.done:
                return job
    return None


def progress() -> Progress | None:
    """Fortschritt des aktiven Laufs, oder `None`, wenn keiner rechnet."""

    job = active()
    if job is None:
        return None

    _drain(job)
    zeilen = list(job.lines)

    tick: int | None = None
    total: int | None = None
    zeile = zeilen[-1] if zeilen else ""
    for eintrag in reversed(zeilen):
        treffer = _TICK_LINE.search(eintrag)
        if treffer:
            tick, total = int(treffer.group(1)), int(treffer.group(2))
            zeile = eintrag
            break

    return Progress(
        job_id=job.job_id,
        tick=tick,
        total=total,
        line=zeile,
        lines=tuple(zeilen[-VISIBLE_LINES:]),
    )


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
            job.result = launch_from_draft(
                draft,
                repo_root=REPO_ROOT,
                on_progress=job.queue.put,
                should_stop=job.stop.is_set,
            )
        except Exception as exc:  # noqa: BLE001 - jeder Fehler gehört ins Log, nicht in den Thread
            job.error = str(exc)
        finally:
            job.done = True

    threading.Thread(target=_work, name=f"sim-{job.job_id[:8]}", daemon=True).start()
    return job.job_id


def cancel(job_id: str | None = None) -> bool:
    """Den laufenden Lauf abbrechen — kooperativ (P1.9-W4.5).

    Gibt zurück, ob überhaupt etwas zum Abbrechen da war.

    **Der Lauf endet nicht sofort, sondern nach dem laufenden Tick.** Ein Thread
    lässt sich von außen nicht sauber beenden; mitten im Tick abgeschnitten
    bliebe ein halber Zustand zurück, und die Artefakte beschrieben einen Lauf,
    den es so nie gab. Bei «Nur Zahlen» ist das eine Sache von Millisekunden,
    mit Sprachmodell kann der letzte Tick noch laufen.

    Ohne `job_id` trifft es den aktiven Lauf — das ist der Fall, den die
    Oberfläche braucht: Wer die Seite neu geladen hat, kennt keine Kennung mehr,
    darf aber trotzdem abbrechen. Es läuft ohnehin höchstens einer.
    """

    with _LOCK:
        if job_id:
            job = _JOBS.get(job_id)
        else:
            job = next((eintrag for eintrag in _JOBS.values() if not eintrag.done), None)
    if job is None or job.done:
        return False
    job.stop.set()
    job.queue.put("Abbruch angefordert — der Lauf endet nach dem laufenden Tick.")
    return True


def poll(job_id: str | None) -> Job | None:
    """Neue Ausgabezeilen einsammeln und den aktuellen Job-Zustand liefern."""

    if not job_id:
        return None
    with _LOCK:
        job = _JOBS.get(job_id)
    if job is None:
        return None

    _drain(job)
    return job


def forget(job_id: str | None) -> None:
    """Abgeschlossenen Job vergessen, damit der Speicher nicht mitwächst."""

    if not job_id:
        return
    with _LOCK:
        job = _JOBS.get(job_id)
        if job is not None and job.done:
            _JOBS.pop(job_id, None)
