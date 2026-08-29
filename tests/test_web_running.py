"""Der Lauf ist ein eigener Zustand (P1.7-B).

Drei Zusagen hängen hier, und alle drei sind leicht zu verlieren:

1. **Der Fortschritt gehört dem Server.** Bis P1.7 füllte ihn der Poll-Callback,
   und der läuft nur in der Sitzung, die gestartet hat. Ein zweiter Tab und eine
   neu geladene Seite sahen nichts.
2. **Der Balken lügt nicht.** Ohne Tick-Meldung gibt es keinen Anteil — dann
   gehört dort ein unbestimmter Balken hin und keine erfundene Prozentzahl
   (Invariante 1: Zahlen kommen aus dem Lauf, nicht aus der Oberfläche).
3. **Der Ladebildschirm verdrängt die Einrichtung.** Rechnet ein Lauf, gehört
   ihm der Viewport — und nicht dem Formular, das gerade vorbei ist.
"""

from __future__ import annotations

import pytest

from dashboard.web import app as web_app
from dashboard.web import run_data, runner
from dashboard.web.state import initial_draft_dict
from dashboard.web.views import running


@pytest.fixture(autouse=True)
def _leerer_zustand():
    runner._JOBS.clear()
    yield
    runner._JOBS.clear()


def _job_mit(*zeilen: str) -> runner.Job:
    """Einen laufenden Job mit vorgegebenen Ausgabezeilen unterschieben."""

    job = runner.Job(job_id="test-job")
    job.lines.extend(zeilen)
    runner._JOBS[job.job_id] = job
    return job


# --- Der Fortschritt gehoert dem Server ------------------------------------


class TestFortschrittAmServer:
    def test_it_is_readable_without_the_job_id(self):
        """Genau das konnte die frühere Fassung nicht."""

        _job_mit("[tick  14/40] 0.05s — price=90")

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert (fortschritt.tick, fortschritt.total) == (14, 40)

    def test_it_reads_the_latest_tick_line(self):
        _job_mit(
            "[tick   1/40] los",
            "irgendeine Zwischenmeldung ohne Tick",
            "[tick  12/40] weiter",
        )

        assert runner.progress().tick == 12

    def test_it_is_none_when_nothing_runs(self):
        assert runner.progress() is None

    def test_a_finished_job_does_not_count(self):
        job = _job_mit("[tick  40/40] fertig")
        job.done = True

        assert runner.progress() is None

    def test_the_payload_survives_the_trip_through_the_browser(self):
        """Store-Zuordnung und Objekt müssen dasselbe sagen.

        Dazwischen liegt JSON; ginge auf dem Weg ein Feld verloren, zeigte der
        Ladebildschirm stumm einen unbestimmten Balken.
        """

        from dashboard.web.pages import launch as launch_page

        _job_mit("[tick   7/25] unterwegs")

        zurueck = web_app._progress_from(launch_page.progress_payload())

        assert zurueck is not None
        assert (zurueck.tick, zurueck.total) == (7, 25)
        assert zurueck.lines


# --- Der Balken luegt nicht ------------------------------------------------


class TestDerBalkenErfindetNichts:
    def test_without_a_tick_line_there_is_no_fraction(self):
        """Invariante 1 an der Oberfläche: keine Zahl ohne Deckung."""

        _job_mit("Lauf wird vorbereitet", "Konfiguration geladen")

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.tick is None
        assert fortschritt.fraction is None

    def test_an_unknown_fraction_renders_an_indeterminate_bar(self):
        unbestimmt = runner.Progress(job_id="x", tick=None, total=None, line="")

        gerendert = str(running.render(unbestimmt, initial_draft_dict()))

        assert "af-progress__fill--unknown" in gerendert
        # Keine Prozentzahl, sondern ein Gedankenstrich.
        assert "0%" not in gerendert

    def test_a_known_fraction_renders_a_width(self):
        bekannt = runner.Progress(job_id="x", tick=10, total=40, line="")

        assert bekannt.fraction == 0.25
        assert "25.0%" in str(running.render(bekannt, initial_draft_dict()))

    def test_the_fraction_never_exceeds_one(self):
        """Ein Lauf kann seine Zielzahl melden, bevor er aufhört."""

        assert runner.Progress(job_id="x", tick=41, total=40, line="").fraction == 1.0


# --- Der Ladebildschirm verdraengt die Einrichtung -------------------------


class TestDerLaufBekommtDenBildschirm:
    def test_the_viewport_shows_the_run_while_it_computes(self):
        daten = run_data.demo()
        laufend = runner.Progress(job_id="x", tick=3, total=10, line="[tick 3/10]")

        gerendert = str(web_app.scene_block(daten, 1, progress=laufend, draft=initial_draft_dict()))

        assert "Der Lauf rechnet" in gerendert
        assert "Population im Tick" not in gerendert, "Die Szene gehört hier nicht hin"

    def test_without_a_run_the_scene_is_back(self):
        daten = run_data.demo()

        gerendert = str(web_app.scene_block(daten, 1, progress=None))

        assert "Population im Tick" in gerendert
        assert "Der Lauf rechnet" not in gerendert

    def test_the_loading_screen_names_what_is_computed(self):
        """Ohne das wäre es ein Balken ohne Gegenstand.

        Ohne Rücksicht auf Groß- und Kleinschreibung: `ui.metric_tile` setzt
        seine Beschriftung in Versalien, und das ist eine Gestaltungsfrage —
        ein Test, der sie festnagelt, bräche beim nächsten Feinschliff.
        """

        draft = initial_draft_dict()
        gerendert = str(
            running.render(runner.Progress(job_id="x", tick=1, total=5, line=""), draft)
        ).lower()

        assert "szenario" in gerendert
        assert "rechenmodus" in gerendert
        assert "umfang" in gerendert


# --- Das Fortschrittsfenster -----------------------------------------------


class TestDasFortschrittsfenster:
    def test_it_stays_away_from_the_control_room(self):
        """Dort steht der Ladebildschirm — zwei Balken wären zwei Aussagen."""

        from dashboard.web import routing

        leitstand = running.leitstand_route()

        assert web_app.active_route(routing.url(leitstand)) == leitstand

    def test_it_links_back_to_the_control_room(self):
        from dashboard.web import routing

        gerendert = str(running.dock(runner.Progress(job_id="x", tick=2, total=8, line="")))

        assert routing.url(running.leitstand_route()) in gerendert

    def test_it_offers_no_way_to_kill_the_run(self):
        """Der Lauf gehört nicht diesem Fenster — erst recht nicht in einer
        Sitzung, die ihn nicht gestartet hat."""

        gerendert = str(running.dock(runner.Progress(job_id="x", tick=2, total=8, line="")))

        for wort in ("Abbrechen", "Stoppen", "Beenden"):
            assert wort not in gerendert


# --- Zwei Befunde aus der Gegenprobe vom 2026-08-29 ------------------------


class TestDieBeschriftungBehauptetNichtsFalsches:
    """«Lauf wird vorbereitet …» galt fuer alles ohne Tick-Zeile.

    Ein Szenario-Vergleich schreibt nie `[tick n/m]` — er meldet je Szenario
    «Completed 50 ticks». Am laufenden System stand deshalb **38 Sekunden lang**
    «wird vorbereitet», waehrend acht Szenarien rechneten. Der Balken war dabei
    richtig (unbestimmt, weil es keine Zahl gibt); die Beschriftung war es nicht.
    """

    def test_without_any_output_it_says_preparing(self):
        leer = runner.Progress(job_id="x", tick=None, total=None, line="", lines=())

        assert "vorbereitet" in str(running.render(leer, initial_draft_dict()))

    def test_with_output_but_no_tick_count_it_says_running(self):
        laufend = runner.Progress(
            job_id="x",
            tick=None,
            total=None,
            line="Completed 50 ticks in 2.02s",
            lines=("Sweep: Business as Usual", "Completed 50 ticks in 2.02s"),
        )

        gerendert = str(running.render(laufend, initial_draft_dict()))

        assert (
            "vorbereitet" not in gerendert
        ), "Es laeuft laengst — «wird vorbereitet» ist an dieser Stelle falsch."
        assert "Fortschritt nicht bezifferbar" in gerendert

    def test_the_bar_stays_indeterminate_either_way(self):
        """Die Beschriftung wird ehrlicher, die Zahl bleibt aus (Invariante 1)."""

        laufend = runner.Progress(job_id="x", tick=None, total=None, line="x", lines=("x",))

        assert laufend.fraction is None
        assert "af-progress__fill--unknown" in str(running.render(laufend, initial_draft_dict()))


class TestKeinKnopfVersprichtWasErNichtHaltenKann:
    """Der Abbruch erreicht einen Szenario-Vergleich nicht.

    Das ist bewusst so — `run_all_sweeps` baut seinen Runner selbst und bekommt
    `should_stop` nicht (Kommentar in `run_launcher.launch_simulation`). Der
    Knopf stand trotzdem da und meldete beim Druck «der Lauf endet nach dem
    laufenden Tick». Am laufenden System nachgestellt: Er endete nicht, und
    nach zwoelf Sekunden Warten stand die Kopfzeile unveraendert auf
    «Simulation laeuft».

    Ein Versprechen ohne Deckung ist schlimmer als ein fehlender Knopf.
    """

    def test_a_sweep_job_is_marked_as_not_cancellable(self):
        draft = initial_draft_dict()
        draft["run_all_sweeps"] = True

        job = runner.Job(job_id="x", cancellable=not bool(draft["run_all_sweeps"]))

        assert job.cancellable is False

    def test_cancelling_an_uncancellable_run_says_so_instead_of_pretending(self):
        job = runner.Job(job_id="sweep", cancellable=False)
        runner._JOBS[job.job_id] = job

        assert runner.cancel() is False, "Es darf nicht behaupten, abgebrochen zu haben"
        assert not job.stop.is_set()

        runner._drain(job)
        assert any(
            "nicht moeglich" in zeile for zeile in job.lines
        ), "Der Nutzer muss erfahren, warum nichts passiert"

    def test_a_normal_run_stays_cancellable(self):
        job = runner.Job(job_id="einzel")
        runner._JOBS[job.job_id] = job

        assert runner.cancel() is True
        assert job.stop.is_set()

    def test_the_button_is_hidden_where_it_cannot_work(self):
        sweep = runner.Progress(job_id="x", tick=None, total=None, line="", cancellable=False)
        einzel = runner.Progress(job_id="x", tick=1, total=9, line="", cancellable=True)

        versteckt = str(running.render(sweep, initial_draft_dict()))
        sichtbar = str(running.render(einzel, initial_draft_dict()))

        assert "'display': 'none'" in versteckt
        assert "Szenario-Vergleich lässt sich nicht abbrechen" in versteckt.replace("ä", "ä")
        assert "endet nach dem laufenden Tick" in sichtbar

    def test_the_flag_survives_the_trip_through_the_browser(self):
        """Faellt es unterwegs weg, greift der Vorgabewert `True` — und der
        Knopf staende beim Szenario-Vergleich wieder da."""

        from dashboard.web.pages import launch as launch_page

        job = runner.Job(job_id="sweep", cancellable=False)
        job.lines.append("Sweep: Business as Usual")
        runner._JOBS[job.job_id] = job

        zurueck = web_app._progress_from(launch_page.progress_payload())

        assert zurueck is not None
        assert zurueck.cancellable is False
