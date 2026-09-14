"""Der Leitstand-Rahmen: fünf Zonen, eine Zeitachse, ein Zustand (P1.5).

Was hier geprüft wird, ist nicht das Aussehen — das entscheidet das Stylesheet.
Geprüft wird, dass die Aussagen des Rahmens stimmen:

* **Fünf Zonen sind da**, in jedem Bereich, auch ohne einen einzigen Lauf.
* **Genau ein Viewport-Bereich ist sichtbar**, und zwar der, auf den die
  Adresse zeigt. Zwei gleichzeitig hieße doppelte IDs im DOM.
* **Eine Zeitachse.** Der Tick kommt aus `tick-store`; Szene, Kennzahlen und
  Verläufe lesen alle denselben Wert.
* **Die Zeitleiste läuft nicht über ihr Ende hinaus** und hält am Ende von
  selbst an, statt in Schleife zu gehen.
"""

from __future__ import annotations

import pytest
from dash import html

from dashboard.web import app as web_app
from dashboard.web import run_data, shell, status, timeline
from dashboard.web.views import scene, telemetry


def _text(component) -> str:
    return str(component)


class _MitschreibendeApp:
    """Nimmt Callbacks entgegen, statt sie zu verdrahten.

    Dieselbe Hilfe wie in `test_web_runner.py`: So lässt sich eine
    Callback-Funktion samt Rückgabe-Tupel prüfen, ohne einen Server zu starten.
    """

    def __init__(self) -> None:
        self.callbacks: list[tuple[list[str], object]] = []

    def callback(self, *outputs, **kwargs):
        ids = [o.component_id for o in outputs if hasattr(o, "component_id")]

        def decorator(fn):
            self.callbacks.append((ids, fn))
            return fn

        return decorator

    def clientside_callback(self, *args, **kwargs):  # pragma: no cover - nur Attrappe
        return None


def _callback(register, name: str):
    app = _MitschreibendeApp()
    register(app)
    for _ids, fn in app.callbacks:
        if fn.__name__ == name:
            return fn
    raise AssertionError(f"Callback «{name}» nicht gefunden")


@pytest.fixture
def demo() -> run_data.RunData:
    return run_data.demo()


# --- Die fünf Zonen --------------------------------------------------------


class TestFuenfZonen:
    ZONEN = (
        "af-shell__header",
        "af-shell__left",
        "af-shell__main",
        "af-shell__timeline",
        "af-shell__right",
    )

    def test_the_layout_carries_all_five(self, demo):
        gerendert = _text(
            shell.layout(
                active="",
                state=status.derive(running=False, demo=True, degraded=False),
                run_options=[],
                run_value=None,
                left=html.Div("links"),
                main=html.Div("mitte"),
                timeline=html.Div("unten"),
                right=html.Div("rechts"),
            )
        )

        for zone in self.ZONEN:
            assert zone in gerendert, f"Zone fehlt: {zone}"

    def test_the_whole_app_carries_all_five(self):
        """Nicht nur der Baustein — auch das, was der Server ausliefert."""

        gerendert = _text(web_app.serve_layout())

        for zone in self.ZONEN:
            assert zone in gerendert, f"Zone fehlt im Seitenlayout: {zone}"

    def test_the_header_holds_status_run_selection_and_actions(self):
        gerendert = _text(
            shell.header(
                "",
                state=status.derive(running=True, demo=False, degraded=False),
                run_options=[{"label": "run_1", "value": "run_1"}],
                run_value="run_1",
            )
        )

        assert shell.RUN_SELECT in gerendert
        assert shell.ACTION_SAVE in gerendert
        assert shell.ACTION_SNAPSHOT in gerendert
        assert shell.ACTION_EXPORT in gerendert
        assert shell.THEME_TOGGLE in gerendert
        assert "af-status--running" in gerendert

    def test_the_drawer_toggles_exist_for_narrow_windows(self):
        gerendert = _text(shell.navbar(""))

        assert shell.LEFT_TOGGLE in gerendert
        assert "af-drawer-toggle" in gerendert


# --- Routing ---------------------------------------------------------------


class TestGenauEinBereichIstSichtbar:
    """Alle vier liegen im DOM; sichtbar ist einer. Zwei wären doppelte IDs."""

    def test_every_route_has_its_own_area(self):
        """Die Sichtbarkeiten und die Bereichsliste dürfen nicht auseinanderlaufen."""

        assert len(web_app.visibility("")) == len(shell.BEREICHE)

    #: Reihenfolge wie in `shell.ROUTES` — seit P1.7 der Arbeitsablauf:
    #: Einrichten, Leitstand, Ergebnisse, Handbuch.
    @pytest.mark.parametrize(
        ("pathname", "sichtbar"),
        [
            ("/app/", 0),
            ("/app/lauf", 1),
            ("/app/runs", 2),
            ("/app/modell", 3),
            ("/app/doku", 4),
            ("/app/doku/cib", 4),
            # Die Musterseite hat eine Adresse, aber keinen Link (P7.1-U1.6).
            ("/app/muster", 5),
            ("/app", 0),
            # Der Aliaspfad aus P1.6: gespeicherte Verweise dürfen nicht ins
            # Leere zeigen, nur weil das Einrichten umgezogen ist.
            ("/app/setup", 0),
        ],
    )
    def test_the_address_decides(self, pathname, sichtbar):
        stile = web_app.visibility(web_app.active_route(pathname))

        angezeigt = [index for index, stil in enumerate(stile) if stil != {"display": "none"}]
        assert angezeigt == [sichtbar], f"{pathname} zeigt {angezeigt}"

    def test_an_unknown_address_falls_back_to_the_first_area(self):
        """Unbekannt heißt «von vorn» — und vorn ist seit P1.7 das Einrichten."""

        assert web_app.active_route("/app/gibt-es-nicht") == ""
        assert web_app.visibility("")[0] != {"display": "none"}

    def test_the_order_of_the_areas_is_the_workflow(self):
        """Die Reihenfolge ist eine Aussage, keine Zufälligkeit (P1.7).

        Vor P1.7 stand der Leitstand vorn; wer das Dashboard zum ersten Mal
        öffnete, landete auf einer Ansicht, für die es noch nichts zu sehen gab.
        """

        assert [label for _, label in shell.ROUTES] == [
            "Einrichten",
            "Leitstand",
            "Ergebnisse",
            # «Modell» steht seit P1.9-W3.1 **hinter** dem Ablauf und nicht
            # darin: Einrichten → Leitstand → Ergebnisse ist der Weg eines
            # Laufs; das Modell zu pflegen gehört daneben, bei dem anderen
            # Bereich, den man aufsucht statt durchläuft.
            "Modell",
            "Handbuch",
        ]

    def test_every_alias_points_at_a_real_area(self):
        """Ein Alias auf einen Bereich, den es nicht gibt, führt ins Leere."""

        bereiche = {route for route, _ in shell.ROUTES}
        for alias, ziel in shell.ALIASES.items():
            assert ziel in bereiche, f"Alias «{alias}» zeigt auf «{ziel}»"

    def test_the_manual_keeps_its_subpages(self):
        """`doku/cib` gehoert zum Handbuch, nicht zum Leitstand."""

        assert web_app.active_route("/app/doku/cib") == "doku"

    def test_the_browser_tab_names_the_brand_and_the_area(self):
        """P7.2-U2.7: «Technology Lab · Leitstand» stand auf jedem Bereich im Tab."""

        from dashboard.web import shell

        assert web_app.TITLE == shell.MARKE == "AeroForesight AI"
        for route, label in shell.ROUTES:
            assert shell.seitentitel(route) == f"AeroForesight AI · {label}"
        assert "AeroForesight AI · Einrichten" in str(web_app.serve_layout())

    def test_the_shipped_defaults_carry_no_prototype_wording(self):
        """Der Vorgabename landet im Bericht und in der Lauf-Auswahl (P7.2-U2.7)."""

        import json
        from pathlib import Path

        pfad = Path(__file__).resolve().parents[1] / "configs" / "simulation_config.json"
        vorgabe = json.loads(pfad.read_text(encoding="utf-8"))

        for feld in ("name", "description"):
            text = vorgabe[feld]
            assert "MVP" not in text and "Prototyp" not in text, (feld, text)
            assert " fuer " not in f" {text} ", (feld, text)


# --- Die eine Zeitachse ----------------------------------------------------


class TestEineZeitachse:
    def test_the_timeline_offers_the_media_controls(self, demo):
        gerendert = _text(timeline.layout(demo, 1))

        for knopf in (
            timeline.PLAY,
            timeline.STOP,
            timeline.STEP_BACK,
            timeline.STEP_FORWARD,
            timeline.TO_START,
            timeline.TO_END,
        ):
            assert knopf in gerendert, f"Knopf fehlt: {knopf}"
        assert timeline.SLIDER in gerendert

    def test_an_empty_run_disables_the_controls(self):
        leer = run_data.RunData(run_id="leer", run_dir=None)

        assert "disabled" in _text(timeline.layout(leer, 1))

    def test_the_marks_stay_readable(self, demo):
        """Höchstens sieben Beschriftungen — mehr überlagern sich."""

        assert len(timeline._marks(demo.max_tick)) <= 8
        assert len(timeline._marks(500)) <= 8
        assert timeline._marks(1) == {1: "1"}

    @pytest.mark.parametrize("max_tick", range(2, 501))
    def test_no_two_marks_crowd_each_other(self, max_tick):
        """Keine zwei Marken näher als ein Zwölftel der Leiste (P7.5-U5.4).

        Bei 50 Ticks standen die Marken 49 und 50 nebeneinander und überlagerten
        sich im Browser zu «490». Ein Zwölftel ist gut die Hälfte eines regulären
        Schritts; bei einer rund 600 px breiten Leiste sind das 50 px — Platz für
        eine dreistellige Zahl. Geprüft wird **jede** Länge, weil der Schritt
        gerundet ist und der Fehler an einzelnen Längen hängt.
        """

        ticks = sorted(timeline._marks(max_tick))

        assert ticks[0] == 1 and ticks[-1] == max_tick
        abstaende = [b - a for a, b in zip(ticks, ticks[1:])]
        assert min(abstaende) >= max(1, (max_tick - 1) / 12), (max_tick, ticks)

    def test_the_tick_never_leaves_its_range(self):
        """Tick 41 in einem Lauf ueber 40 gibt es nicht — auch nicht kurz."""

        assert timeline._clamp(41, 40) == 40
        assert timeline._clamp(0, 40) == 1
        assert timeline._clamp("Unsinn", 40) == 1

    def test_playback_halts_at_the_end_instead_of_looping(self):
        """Ein Lauf hat ein Ende. Eine Schleife täuschte vor, es ginge weiter."""

        from dash import no_update

        advance = _callback(timeline.register_callbacks, "_advance")

        weiter, unveraendert = advance(1, True, 12, 40)
        assert weiter == 13
        assert unveraendert is no_update, "mittendrin wird die Wiedergabe nicht angefasst"

        letzter, gestoppt = advance(1, True, 40, 40)
        assert letzter == 40
        assert gestoppt is False, "am Ende haelt sie von selbst an"

    def test_a_freshly_mounted_interval_does_not_move_the_tick(self):
        """Der Fund vom laufenden System: nach dem Laufwechsel stand Tick 2.

        Wird die Leiste beim Wechsel des Laufs neu aufgebaut, ist das
        `dcc.Interval` für Dash ein neuer Eingang und feuert einmal, bevor
        `_transport` es abschalten kann. Ohne die Prüfung auf den
        Abspielzustand sprang der Tick dabei von 1 auf 2 — in Regler,
        Kennzahlen und Szene gleichzeitig, also plausibel genug, um es zu
        übersehen.
        """

        from dash import no_update

        advance = _callback(timeline.register_callbacks, "_advance")

        for pausiert in (None, False):
            tick, laeuft = advance(1, pausiert, 1, 40)
            assert tick is no_update, f"Tick bewegt sich bei playing={pausiert!r}"
            assert laeuft is no_update

    def test_the_readout_names_both_numbers(self):
        assert timeline.readout(12, 40) == "Tick 12 / 40"

    def test_events_are_marked_on_the_track(self, demo):
        gerendert = _text(timeline.event_strip(demo))

        assert "af-timeline__event" in gerendert
        # Die Politikwechsel des Beispieldatensatzes stechen hervor.
        assert "af-timeline__event--warning" in gerendert


# --- Szene und Telemetrie folgen demselben Tick ----------------------------


class TestSzeneUndTelemetrieFolgenDemselbenTick:
    def test_the_overlay_names_tick_population_and_zoom(self, demo):
        gerendert = _text(scene.overlay(12, 40, 240, 0))

        assert "12 / 40" in gerendert
        assert "240" in gerendert
        assert "100%" in gerendert

    def test_the_overlay_states_no_framerate(self, demo):
        """Es wird nichts fortlaufend gerendert, das eine Framerate hätte."""

        gerendert = _text(scene.overlay(1, 40, 240, 0)).lower()

        assert "fps" not in gerendert
        assert "framerate" not in gerendert

    @pytest.mark.parametrize("index", range(len(scene.ZOOM_STEPS)))
    def test_every_zoom_step_has_a_label(self, index):
        assert scene.zoom_label(index).endswith("%")

    def test_zoom_stays_inside_its_range(self):
        assert scene.zoom_factor(-5) == scene.ZOOM_STEPS[0]
        assert scene.zoom_factor(99) == scene.ZOOM_STEPS[-1]

    def test_the_factor_strip_shows_all_seven(self, demo):
        gerendert = _text(scene.factor_strip(demo.factors_at(30)))

        for factor in range(1, 8):
            assert f"F{factor}." in gerendert

    def test_a_missing_factor_series_is_said_out_loud(self):
        assert "timeseries/factors.csv" in _text(scene.factor_strip({}))

    def test_the_kpis_follow_the_scrubbed_tick(self, demo):
        frueh = _text(telemetry.kpi_row(demo, 2))
        spaet = _text(telemetry.kpi_row(demo, 35))

        assert frueh != spaet, "die Kennzahlen kleben am selben Tick"

    def test_a_tick_without_data_says_so(self, demo):
        assert "keine Kennzahlen" in _text(telemetry.kpi_row(demo, 9999))

    def test_the_console_puts_failures_first(self, demo):
        zeilen = telemetry.console_lines(demo, progress=["Tick 1 …"], error="Ollama weg")

        assert "af-console__line--error" in _text(zeilen[0])

    def test_the_console_survives_an_empty_run(self):
        leer = run_data.RunData(run_id="leer", run_dir=None)

        assert "Noch keine Meldungen" in _text(telemetry.console(leer))


# --- Der Zustand kommt aus einer Quelle ------------------------------------


class TestDerZustandKommtAusEinerQuelle:
    """Kopfzeile, Banner und Konsole dürfen sich nicht widersprechen."""

    @pytest.mark.parametrize(
        ("running", "demo_flag", "degraded", "erwartet"),
        [
            (True, True, True, status.RUNNING),
            (False, True, True, status.DEMO),
            (False, False, True, status.DEGRADED),
            (False, False, False, status.READY),
        ],
    )
    def test_the_ranking_holds(self, running, demo_flag, degraded, erwartet):
        zustand = status.derive(running=running, demo=demo_flag, degraded=degraded)

        assert zustand.tone == erwartet

    def test_the_incident_count_is_phrased_in_the_singular(self):
        einer = status.derive(running=False, demo=False, degraded=True, incidents=1)
        mehrere = status.derive(running=False, demo=False, degraded=True, incidents=3)

        assert "ein Aufruf" in einer.detail
        assert "3 Aufrufe" in mehrere.detail

    def test_the_header_renders_every_tone(self):
        for tone in (status.RUNNING, status.DEMO, status.DEGRADED, status.READY):
            gerendert = _text(shell.status_view(status.Status(tone, "Text", "Detail")))
            assert f"af-status--{tone}" in gerendert


class TestNurDerLeitstandHatSeitenzonen:
    """D2, P7.3-U3.1: Bedienfeld, Telemetrie und Zeitleiste gibt es nur im Leitstand.

    Die Menge wird aus den Bereichen abgeleitet; diese Klasse hält, dass sie
    wirklich alles außer dem Leitstand umfasst — und dass der Leitstand selbst
    seine Zonen behält.
    """

    def test_every_area_but_the_control_room_is_a_focus_area(self):
        alle = {route for route, _ in shell.BEREICHE}

        assert shell.FOCUS_ROUTES == alle - {shell.LEITSTAND}

    def test_the_control_room_keeps_its_zones(self):
        assert shell.shell_class(shell.LEITSTAND) == "af-shell"
        for route, _ in shell.BEREICHE:
            if route != shell.LEITSTAND:
                assert "af-shell--focus" in shell.shell_class(route), route
