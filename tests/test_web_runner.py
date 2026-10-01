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
    def fake_launch(draft, *, repo_root=None, on_progress=None, should_stop=None):
        for tick in (1, 2, 3):
            on_progress(f"[Tick {tick}/3] price=100")
        return "fertig"

    monkeypatch.setattr(runner, "launch_from_draft", fake_launch)

    job = _warte_auf_ende(runner.start(initial_draft_dict()))

    assert job.done is True
    assert job.error is None
    assert job.result == "fertig"
    assert len(job.lines) == 3
    assert job.lines[0].startswith("[Tick 1/3]")


def test_progress_arrives_while_the_run_is_still_going(monkeypatch):
    """Sonst erschiene das Protokoll erst am Ende — der Sinn wäre weg."""

    freigabe = threading.Event()

    def fake_launch(draft, *, repo_root=None, on_progress=None, should_stop=None):
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

    def fake_launch(draft, *, repo_root=None, on_progress=None, should_stop=None):
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
        lambda draft, *, repo_root=None, on_progress=None, should_stop=None: [
            on_progress(f"Zeile {i}") for i in range(ueberzaehlig)
        ],
    )

    job = _warte_auf_ende(runner.start(initial_draft_dict()), sekunden=10)

    assert len(job.lines) == runner.MAX_LOG_LINES
    assert job.lines[-1] == f"Zeile {ueberzaehlig - 1}", "die jüngsten Zeilen bleiben"


class TestDieFertigmeldungGehtNichtVerloren:
    """**Befund 9 der Abnahme vom 2026-09-30.** Nach dem Szenario-Vergleich kam
    keine Fertigmeldung, «Lauf aktiv …» blieb stehen, und kein Lauf wurde gewählt.

    Dash verwirft die Antwort eines Callbacks, der noch läuft, wenn sein Takt
    ihn erneut auslöst. `_poll` vergaß den Job in genau der Antwort, die ihn als
    fertig meldete — ging sie verloren, fand der nächste Aufruf nichts mehr.
    """

    def _poll(self):
        from dashboard.web.pages import launch as launch_page

        app = _MitschreibendeApp()
        launch_page.register_callbacks(app)
        return next(fn for _ids, fn in app.callbacks if fn.__name__ == "_poll")

    def test_ein_zweites_abholen_sagt_dasselbe(self, monkeypatch):
        from dashboard.run_launcher import RunLaunchResult

        ergebnis = RunLaunchResult(
            run_id="run_x", run_dir=None, ticks_completed=3, total_events=0, artifacts={}
        )
        monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: ergebnis)
        job_id = runner.start(initial_draft_dict())
        _warte_auf_ende(job_id)

        erste, zweite = self._poll()(1, job_id), self._poll()(2, job_id)

        assert str(erste) == str(zweite)
        assert erste[3] == "run_x", "der fertige Lauf wird gewählt"
        assert erste[1] is True, "danach fragt niemand mehr nach"

    def test_der_naechste_start_raeumt_auf(self, monkeypatch):
        monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: "ok")
        erster = runner.start(initial_draft_dict())
        _warte_auf_ende(erster)

        zweiter = runner.start(initial_draft_dict())
        _warte_auf_ende(zweiter)

        assert runner.poll(erster) is None and runner.poll(zweiter) is not None


# --- Der Start-Knopf selbst -------------------------------------------------


class _MitschreibendeApp:
    """Nimmt die Callbacks entgegen, statt eine echte Dash-App zu bauen.

    So lässt sich `_start` mitsamt seiner Verdrahtung prüfen — auch die
    Reihenfolge des Rückgabe-Tupels, die zu den fünf `Output`s passen muss.
    Ein Fehler dort würde die Meldung in der falschen Komponente landen lassen,
    ohne dass irgendetwas rot wird.
    """

    def __init__(self) -> None:
        self.callbacks: list[tuple[list[str], object]] = []

    def callback(self, *outputs, **kwargs):
        ids = [o.component_id for o in outputs if hasattr(o, "component_id")]

        def decorator(fn):
            self.callbacks.append((ids, fn))
            return fn

        return decorator

    def clientside_callback(self, *args, **kwargs):
        """Clientseitige Callbacks laufen im Browser und haben hier nichts zu tun.

        Die Attrappe muss sie trotzdem annehmen: `register_callbacks` meldet
        seit P1.7 auch den Sprung nach oben an, und ohne diese Methode bräche
        die Anmeldung ab, bevor der geprüfte Callback überhaupt entsteht.
        """


def _start_callback():
    from dashboard.web.pages import launch as launch_page

    app = _MitschreibendeApp()
    launch_page.register_callbacks(app)
    for _ids, fn in app.callbacks:
        if fn.__name__ == "_start":
            return fn
    raise AssertionError("Start-Callback nicht gefunden")


#: Die fünf Outputs in ihrer Reihenfolge — job-store, poll, status, log, knopf.
_STATUS = 2
_KNOPF = 4


def test_the_start_button_refuses_a_config_that_cannot_run(monkeypatch):
    """P0.3 verspricht, dass «Start» abweist — geprüft war bisher nur die Ansicht."""

    gestartet: list[dict] = []
    monkeypatch.setattr(runner, "start", lambda draft: gestartet.append(draft) or "job")

    draft = initial_draft_dict()
    draft["use_seed"] = True
    draft["seed"] = -1

    # Zwei Ausloeser seit P1.7: Bedienfeld und letzter Schritt des
    # Einrichtens. Ein Callback, eine Pruefung, ein `runner.start`.
    ergebnis = _start_callback()(1, None, draft)

    assert gestartet == [], "es darf kein Lauf angefangen haben"
    assert "seed" in str(ergebnis[_STATUS])
    assert ergebnis[_KNOPF] is False, "der Knopf muss wieder bedienbar sein"


def test_the_start_button_starts_a_healthy_config(monkeypatch):
    monkeypatch.setattr(runner, "start", lambda draft: "job-4711")

    ergebnis = _start_callback()(1, None, initial_draft_dict())

    assert ergebnis[0] == "job-4711"
    assert ergebnis[_KNOPF] is True, "während des Laufs ist der Knopf gesperrt"


class TestNachDemStartStehtEinrichtenAmEinstieg:
    """**Befund 7 der Abnahme vom 2026-09-30.** Nach einem Szenario-Vergleich blieb
    die Schrittfolge auf «Prüfen & Starten» stehen. Wer dort einen Einzellauf
    einstellte, wählte Szenario und Verläufe ohne Warnung — und startete wieder
    den Vergleich, der beides nicht übernimmt. Seit dem Start steht «Einrichten»
    wieder am Einstieg, wie der Docstring von `wizard.STEP_STORE` es verspricht."""

    #: Die drei letzten Ausgänge: Schritt, Besuchtes, Verlauf.
    SCHRITT, BESUCHT, VERLAUF = 6, 7, 8

    def test_ein_gestarteter_lauf_setzt_die_schrittfolge_zurueck(self, monkeypatch):
        from dashboard.web.config_editor import wizard

        monkeypatch.setattr(runner, "start", lambda draft: "job-1")

        ergebnis = _start_callback()(None, 1, {**initial_draft_dict(), "run_all_sweeps": True})

        assert ergebnis[self.SCHRITT] is wizard.ENTRY
        assert ergebnis[self.BESUCHT] == [] and ergebnis[self.VERLAUF] == []

    def test_ein_abgewiesener_start_laesst_sie_stehen(self, monkeypatch):
        """Wer die Fehlermeldung lesen soll, bleibt bei den Feldern."""

        from dash import no_update

        monkeypatch.setattr(runner, "start", lambda draft: "job-1")
        draft = {**initial_draft_dict(), "use_seed": True, "seed": -1}

        ergebnis = _start_callback()(None, 1, draft)

        assert ergebnis[self.SCHRITT :] == (no_update, no_update, no_update)


# --- Ein Lauf gehört dem Server, nicht der Sitzung --------------------------
#
# `runner` lässt genau **einen** Lauf im ganzen Prozess zu: `launch_simulation`
# leitet `stdout` um, zwei Läufe schnitten sich gegenseitig die Ausgabe ab.
# Die Anzeige las den Laufzustand trotzdem nur aus den Schaltern der eigenen
# Sitzung — mit der Begründung, die Anzeige gehöre zu dieser einen. Das trifft
# für die Anzeige zu, nicht für die Sache dahinter.
#
# Am laufenden System nachgestellt: Während ein Lauf bei Tick 14 von 20 stand,
# meldete eine frisch geladene Seite «System bereit», der Start-Knopf stand
# aktiv da, und sein Druck endete in «Es läuft bereits eine Simulation. Bitte
# abwarten.» Genau der Widerspruch, gegen den `status.py` angetreten ist.


def _running_callback():
    from dashboard.web.pages import launch as launch_page

    app = _MitschreibendeApp()
    launch_page.register_callbacks(app)
    for _ids, fn in app.callbacks:
        if fn.__name__ == "_running":
            return fn
    raise AssertionError("Running-Callback nicht gefunden")


def test_a_foreign_run_is_visible_in_a_session_that_did_not_start_it(monkeypatch):
    """Fremder Lauf: Diese Sitzung pollt nicht, muss ihn aber melden."""

    monkeypatch.setattr(runner, "is_running", lambda: True)

    # poll_disabled=True heißt «diese Sitzung hat keinen eigenen Lauf».
    laeuft, knopf_gesperrt = _running_callback()(1, True, False)

    assert laeuft is True, "die Kopfzeile muss den fremden Lauf zeigen"
    assert knopf_gesperrt is True, "«Start» darf nicht anbieten, was runner ablehnt"


def test_an_idle_server_leaves_the_button_usable(monkeypatch):
    monkeypatch.setattr(runner, "is_running", lambda: False)

    laeuft, knopf_gesperrt = _running_callback()(1, True, True)

    assert laeuft is False
    assert knopf_gesperrt is False


def test_the_own_run_is_reported_before_the_heartbeat_catches_up(monkeypatch):
    """Der eigene Start zählt sofort, nicht erst beim nächsten Takt.

    `runner.is_running()` steht hier auf `False` — der Takt weiß also noch
    nichts. Ohne `run-poll` als zweite Quelle bliebe der eigene Lauf bis zu
    zwei Sekunden lang unbestätigt.
    """

    monkeypatch.setattr(runner, "is_running", lambda: False)

    laeuft, _knopf = _running_callback()(1, False, False)

    assert laeuft is True


def test_nothing_is_written_while_the_state_is_unchanged(monkeypatch):
    """Der Takt darf die Kopfzeile nicht alle zwei Sekunden neu bauen.

    Jede Änderung an `run-running-store` stößt `_status` an, und der lädt die
    Laufdaten neu. Ein Takt, der unverändert schreibt, wäre eine Dauerlast
    ohne Aussage.
    """

    from dash import no_update

    monkeypatch.setattr(runner, "is_running", lambda: True)

    ergebnis = _running_callback()(7, True, True)

    assert ergebnis == (no_update, no_update)


def test_the_rail_renders_a_locked_button_during_a_foreign_run(monkeypatch):
    """Schon beim ersten Zeichnen — nicht erst beim ersten Takt."""

    from dashboard.web.pages import launch as launch_page

    monkeypatch.setattr(runner, "is_running", lambda: True)
    gesperrt = str(launch_page.rail(initial_draft_dict()))

    monkeypatch.setattr(runner, "is_running", lambda: False)
    frei = str(launch_page.rail(initial_draft_dict()))

    assert "disabled=True" in gesperrt
    assert gesperrt != frei


# --- Abbrechen (P1.9-W4.5) -------------------------------------------------


class TestEinLaufLaesstSichAbbrechen:
    """W4.5 — bis dahin lief ein Lauf bis zum Ende oder bis der Prozess starb.

    Wer versehentlich 500 Ticks mit Sprachmodell startete, konnte nur warten
    oder den Server neu starten.

    **Kooperativ und nicht gewaltsam:** Ein Thread lässt sich von außen nicht
    sauber beenden. Mitten in einem Tick abgebrochen bliebe ein halber Zustand
    zurück, und die Artefakte beschrieben einen Lauf, den es so nie gab.
    Gefragt wird deshalb zwischen zwei Ticks.
    """

    def test_nothing_running_is_not_an_error(self):
        assert runner.cancel() is False

    def test_the_flag_reaches_the_run(self, monkeypatch):
        """Der Lauf bekommt eine Frage gestellt, die er beantworten kann."""

        gesehen: dict = {}

        def fake_launch(draft, *, repo_root=None, on_progress=None, should_stop=None):
            gesehen["vorher"] = should_stop()
            runner.cancel()
            gesehen["nachher"] = should_stop()
            return "fertig"

        monkeypatch.setattr(runner, "launch_from_draft", fake_launch)
        job_id = runner.start({})
        _warte(job_id)

        assert gesehen == {"vorher": False, "nachher": True}, gesehen

    def test_it_finds_the_active_run_without_a_job_id(self, monkeypatch):
        """Wer die Seite neu geladen hat, kennt keine Kennung — darf aber abbrechen.

        Dieselbe Überlegung wie beim Laufzustand: Was dem Server gehört, wird
        beim Server erfragt, nicht aus dem Zustand einer Sitzung abgeleitet.
        """

        angehalten: dict = {}

        def fake_launch(draft, *, repo_root=None, on_progress=None, should_stop=None):
            angehalten["konnte"] = runner.cancel()  # ohne Kennung
            angehalten["wirkt"] = should_stop()
            return "fertig"

        monkeypatch.setattr(runner, "launch_from_draft", fake_launch)
        _warte(runner.start({}))

        assert angehalten == {"konnte": True, "wirkt": True}

    def test_a_finished_run_cannot_be_cancelled(self, monkeypatch):
        """Sonst meldete die Oberfläche einen Abbruch, den es nicht gab."""

        monkeypatch.setattr(
            runner,
            "launch_from_draft",
            lambda draft, *, repo_root=None, on_progress=None, should_stop=None: "fertig",
        )
        job_id = runner.start({})
        _warte(job_id)

        assert runner.cancel(job_id) is False


def test_the_tick_loop_asks_before_the_next_round():
    """Der Haken sitzt **nach** einem fertigen Tick, nicht mittendrin.

    Dort ist der Zustand vollständig; der Lauf endet dann mit weniger Ticks,
    als er vorhatte, und schreibt seine Artefakte wie jeder unvollständige
    Lauf.
    """

    from pathlib import Path

    quelle = Path("src/orchestration/simulation_runner.py").read_text(encoding="utf-8")
    schleife = quelle[quelle.index("while state.clock.current_tick < max_ticks:") :][:900]

    assert "self.options.should_stop" in schleife, (
        "Die Tick-Schleife fragt nicht mehr nach einem Abbruch — dann ist der "
        "Knopf im Ladebildschirm wirkungslos."
    )
    assert schleife.index("_run_single_round") < schleife.index("should_stop"), (
        "Der Haken sitzt vor dem Tick statt danach — dann bricht der Lauf mit "
        "einem halben Zustand ab."
    )


def _warte(job_id, sekunden: float = 3.0):
    """Auf das Ende des Jobs warten, ohne fest zu schlafen."""

    import time as _time

    frist = _time.time() + sekunden
    while _time.time() < frist:
        job = runner.poll(job_id)
        if job is not None and job.done:
            return job
        _time.sleep(0.01)
    raise AssertionError("Der Job wurde nicht fertig")
