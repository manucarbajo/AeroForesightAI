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

        Ohne Rücksicht auf Groß- und Kleinschreibung: `ui.kachel` setzt
        seine Beschriftung in Versalien, und das ist eine Gestaltungsfrage —
        ein Test, der sie festnagelt, bräche beim nächsten Feinschliff.
        """

        draft = initial_draft_dict()
        gerendert = str(
            running.render(runner.Progress(job_id="x", tick=1, total=5, line=""), draft)
        ).lower()

        assert "szenario" in gerendert
        assert "rechenmodus" in gerendert
        # «Länge» wie im Bedienfeld — seit P8-V6 kommen beide Angaben aus `stand`.
        assert "länge" in gerendert


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


# --- Die Restzeit (P1.9-W4.3) ----------------------------------------------


class TestDieRestzeitWirdGemessenNichtGeraten:
    """Der Lauf ist der beste Zeuge fuer sein eigenes Tempo.

    Die Schaetzung im Pruefschritt (`config_editor.dauer`) muss aus vergangenen
    Laeufen raten, weil es den laufenden noch nicht gibt. Waehrend des Laufs ist
    das nicht noetig: Jede Tick-Zeile traegt ihre eigene Dauer.
    """

    def test_sie_kommt_aus_den_tickdauern_des_laufenden_laufs(self):
        _job_mit(
            "[tick   1/10] 2.00s (0.50 ticks/s) - price=90",
            "[tick   2/10] 2.00s (0.50 ticks/s) - price=91",
        )

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.tick_seconds == (2.0, 2.0)
        # Acht Ticks stehen aus, jeder dauerte zwei Sekunden.
        assert fortschritt.remaining_seconds == (16.0, 16.0)

    def test_sie_ist_eine_spanne_und_kein_punktwert(self):
        _job_mit(
            "[tick   1/11] 1.00s - price=90",
            "[tick   2/11] 3.00s - price=91",
        )

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.remaining_seconds == (9.0, 27.0)

    def test_aus_einer_einzigen_messung_wird_nichts_abgeleitet(self):
        """Dieselbe Zurueckhaltung wie `config_editor.dauer.MINDESTENS`."""

        _job_mit("[tick   1/40] 2.00s - price=90")

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.tick_seconds == (2.0,)
        assert fortschritt.remaining_seconds is None

    def test_ohne_tick_zeile_gibt_es_nichts_zu_sagen(self):
        """Der Szenario-Vergleich schreibt keine `[tick n/m]`-Zeilen."""

        _job_mit("Sweep: Business as Usual", "Completed 50 ticks")

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.remaining_seconds is None

    def test_im_letzten_tick_steht_dort_nichts_mehr(self):
        _job_mit(
            "[tick   9/10] 2.00s - price=90",
            "[tick  10/10] 2.00s - price=91",
        )

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert fortschritt.remaining_seconds is None

    def test_nur_die_juengsten_tickdauern_zaehlen(self):
        """Ein Lauf wird langsamer; die Anzeige soll dem folgen."""

        zeilen = [f"[tick {n:>3}/100] 1.00s" for n in range(1, 21)]
        zeilen += [f"[tick {n:>3}/100] 5.00s" for n in range(21, 41)]
        _job_mit(*zeilen)

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert len(fortschritt.tick_seconds) == runner.TEMPO_FENSTER
        # Die alten, schnellen Ticks sind aus dem Fenster gefallen.
        assert set(fortschritt.tick_seconds) == {5.0}

    def test_eine_fehlende_dauer_nimmt_dem_balken_nicht_seine_zahl(self):
        """Die Restzeit darf ausfallen, der Fortschritt nicht."""

        _job_mit("[tick  12/40] weiter ohne Dauer")

        fortschritt = runner.progress()

        assert fortschritt is not None
        assert (fortschritt.tick, fortschritt.total) == (12, 40)
        assert fortschritt.tick_seconds == ()
        assert fortschritt.remaining_seconds is None

    def test_sie_ueberlebt_die_reise_durch_den_browser(self):
        """Faellt sie unterwegs weg, zeigte der Ladebildschirm sie nie."""

        from dashboard.web.pages import launch as launch_page

        _job_mit(
            "[tick   1/10] 2.00s - price=90",
            "[tick   2/10] 2.00s - price=91",
        )

        zurueck = web_app._progress_from(launch_page.progress_payload())

        assert zurueck is not None
        assert zurueck.remaining_seconds == (16.0, 16.0)

    def test_der_ladebildschirm_zeigt_sie_an(self):
        _job_mit(
            "[tick   1/10] 2.00s - price=90",
            "[tick   2/10] 2.00s - price=91",
        )
        fortschritt = runner.progress()

        gezeigt = str(running.render(fortschritt, initial_draft_dict()))

        assert "noch etwa 16 Sekunden" in gezeigt

    def test_null_sekunden_werden_nicht_gezaehlt(self):
        """Am laufenden System stand bei Tick 39 von 40 «noch etwa 0 Sekunden».

        Eine Zahl, die schlechter ist als keine. Der Satz sagt dasselbe, ohne
        etwas Falsches zu behaupten.
        """

        _job_mit(
            "[tick  38/40] 0.02s - price=90",
            "[tick  39/40] 0.02s - price=91",
        )
        fortschritt = runner.progress()

        gezeigt = str(running.render(fortschritt, initial_draft_dict()))

        assert "0 Sekunden" not in gezeigt
        assert "gleich fertig" in gezeigt

    def test_und_schweigt_wenn_es_nichts_zu_sagen_gibt(self):
        """Kein «unbekannt» — der Platz bleibt leer."""

        _job_mit("[tick   1/40] 2.00s - price=90")
        fortschritt = runner.progress()

        gezeigt = str(running.render(fortschritt, initial_draft_dict()))

        assert "noch etwa" not in gezeigt

    def test_das_fortschrittsfenster_zeigt_sie_auch(self):
        """Wer waehrenddessen einen aelteren Lauf ansieht, will sie auch sehen."""

        _job_mit(
            "[tick   1/10] 2.00s - price=90",
            "[tick   2/10] 2.00s - price=91",
        )
        fortschritt = runner.progress()

        assert "noch etwa 16 Sekunden" in str(running.dock(fortschritt))

    def test_beide_orte_sprechen_dieselbe_sprache(self):
        """«3 Minuten» im Pruefschritt und «180 s» im Lauf waeren zwei Groessen."""

        from dashboard.web.config_editor import dauer

        assert dauer.spanne(16.0) == "16 Sekunden"
        assert dauer.spanne(180.0) == "3 Minuten"

    def test_die_einzahl_wird_mitgefuehrt(self):
        """Am laufenden System stand dort «noch etwa 1 Sekunden bis 2 Sekunden».

        Vor W4.3 fiel das nicht auf: Die Schaetzung im Pruefschritt beschreibt
        einen ganzen Lauf und landet praktisch nie bei eins. Die Restzeit tut es
        in jedem letzten Tick.
        """

        from dashboard.web.config_editor import dauer

        assert dauer.spanne(1.0) == "1 Sekunde"
        assert dauer.spanne(2.0) == "2 Sekunden"
        # 60 Sekunden bleiben Sekunden -- die Schwelle liegt bei 90.
        assert dauer.spanne(60.0) == "60 Sekunden"
        assert dauer.spanne(120.0) == "2 Minuten"

    def test_keine_zahl_bekommt_die_falsche_endung(self):
        """Breiter als die eine Stelle, an der es aufgefallen ist.

        Die Einzahl bei den Minuten ist mit der 90-Sekunden-Schwelle heute nicht
        erreichbar -- die Formatierung fuehrt sie trotzdem mit, damit eine
        verschobene Schwelle nicht «1 Minuten» zurueckbringt.
        """

        from dashboard.web.config_editor import dauer

        for sekunden in [0.4, 1.0, 1.4, 2.0, 89.0, 90.0, 150.0, 5399.0, 5400.0]:
            text = dauer.spanne(sekunden)
            zahl = float(text.split()[0])
            einzahl = text.split()[1].endswith("e")
            assert einzahl == (zahl == 1), f"{sekunden}s -> {text!r}"


# --- Der Szenario-Vergleich auf dem Ladebildschirm (P8-V6, Befund 9) ----------


class TestDerVergleichSagtWasErRechnet:
    """**Befund 9 der Abnahme vom 2026-09-30.** Während vier Rahmen rechneten,
    beschrieb der Ladebildschirm einen Einzellauf («Standard-Ausgangslage ·
    40 Ticks»), und der Fortschritt hieß «nicht bezifferbar» — obwohl die
    Ausgabe jedes Szenario mit Kopf und Abschluss meldet."""

    KOEPFE = (
        "Sweep: Business as Usual (A1+B1) (business_as_usual)",
        "  Completed 120 ticks in 3.20s (38 ticks/sec)",
        "Sweep: CO₂-Verzögerung (co2_delayed)",
    )

    def _vergleich(self, *zeilen: str) -> runner.Progress:
        job = _job_mit(*zeilen)
        job.szenarien = 4
        fortschritt = runner.progress()
        assert fortschritt is not None
        return fortschritt

    def test_er_zaehlt_die_fertigen_szenarien(self):
        fortschritt = self._vergleich(*self.KOEPFE)

        assert fortschritt.szenarien_fertig == 1
        assert fortschritt.fraction == 0.25
        text = str(running.render(fortschritt, initial_draft_dict()))
        assert "Szenario 2 von 4: CO₂-Verzögerung" in text
        assert "nicht bezifferbar" not in text

    def test_gezaehlt_wird_ueber_alle_zeilen(self):
        """Durch den Browser gehen nur die letzten `VISIBLE_LINES` Zeilen."""

        fuellung = ("Protokoll",) * (runner.VISIBLE_LINES + 5)
        fortschritt = self._vergleich(*self.KOEPFE[:2], *fuellung)

        assert fortschritt.szenarien_fertig == 1

    def test_am_ende_sagt_er_es(self):
        zeilen = []
        for i in range(4):
            zeilen += [f"Sweep: Rahmen {i} (r{i})", "  Completed 40 ticks in 1.00s (40 ticks/sec)"]

        fortschritt = self._vergleich(*zeilen)

        assert fortschritt.fraction == 1.0
        assert "Alle 4 Szenarien gerechnet" in str(
            running.render(fortschritt, initial_draft_dict())
        )

    def test_die_zaehlung_kommt_durch_den_browser(self):
        from dashboard.web.pages import launch as launch_page

        self._vergleich(*self.KOEPFE)

        zurueck = web_app._progress_from(launch_page.progress_payload())

        assert zurueck is not None
        assert (zurueck.szenarien, zurueck.szenarien_fertig, zurueck.szenario_name) == (
            4,
            1,
            "CO₂-Verzögerung",
        )

    def test_ein_vergleich_bekommt_die_zahl_seiner_rahmen(self, monkeypatch):
        from dashboard.config_catalog import rahmenszenarien

        monkeypatch.setattr(runner, "launch_from_draft", lambda draft, **kw: "ok")
        entwurf = {**initial_draft_dict(), "run_all_sweeps": True}

        job = runner.poll(runner.start(entwurf))

        assert job is not None and job.szenarien == len(rahmenszenarien())

    def test_ein_einzellauf_zaehlt_keine_szenarien(self):
        _job_mit("Sweep: X (x)")
        fortschritt = runner.progress()

        assert fortschritt is not None and fortschritt.szenarien is None
        assert fortschritt.fraction is None

    def test_die_kacheln_beschreiben_den_vergleich(self):
        from dashboard.config_catalog import rahmenszenarien

        entwurf = {**initial_draft_dict(), "run_all_sweeps": True}
        leer = runner.Progress(job_id="x", tick=None, total=None, line="", szenarien=4)

        text = str(running.render(leer, entwurf))

        assert f"Vergleich · {len(rahmenszenarien())} Rahmenszenarien" in text
        assert "Standard-Ausgangslage" not in text
