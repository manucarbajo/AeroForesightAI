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

import inspect

import pytest
from dash import html

from dashboard.web import app as web_app
from dashboard.web import run_data, shell, status, timeline
from dashboard.web.views import scene, telemetry


def _text(component) -> str:
    return str(component)


def _alle(knoten):
    """Jeder Knoten eines Komponentenbaums, der Wurzelknoten eingeschlossen."""

    yield knoten
    kinder = getattr(knoten, "children", None)
    for kind in kinder if isinstance(kinder, (list, tuple)) else [kinder]:
        if kind is not None and not isinstance(kind, str):
            yield from _alle(kind)


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
                state=status.derive(running=False, demo=True),
                lauf_bezeichnung=None,
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
                state=status.derive(running=True, demo=False),
                lauf_bezeichnung="Standard-Ausgangslage · 14.09.2026, 08:56",
            )
        )

        assert shell.LAUF_WAHL in gerendert
        assert shell.ACTION_SAVE in gerendert
        assert shell.ACTION_EXPORT in gerendert
        assert shell.THEME_TOGGLE in gerendert
        assert "af-status--running" in gerendert

    def test_the_drawer_toggles_exist_for_narrow_windows(self):
        gerendert = _text(shell.navbar(""))

        assert shell.LEFT_TOGGLE in gerendert
        assert "af-drawer-toggle" in gerendert


def _knoepfe(knoten) -> list:
    """Jeder Knopf im Baum — gesucht, nicht aufgezählt."""

    eigen = [knoten] if isinstance(knoten, html.Button) else []
    kinder = getattr(knoten, "children", None)
    if kinder is None or isinstance(kinder, str):
        return eigen
    kinder = kinder if isinstance(kinder, (list, tuple)) else [kinder]
    return eigen + [k for kind in kinder for k in _knoepfe(kind)]


def _beschriftung(knoten) -> str:
    """Der Text eines Knopfs ohne seine Symbole."""

    if isinstance(knoten, str):
        return knoten
    if "material-symbols" in (getattr(knoten, "className", "") or ""):
        return ""
    kinder = getattr(knoten, "children", None)
    if kinder is None:
        return ""
    kinder = kinder if isinstance(kinder, (list, tuple)) else [kinder]
    return "".join(_beschriftung(k) for k in kinder)


def _kopf(active: str = "") -> html.Header:
    return shell.header(
        active,
        state=status.derive(running=False, demo=False),
        lauf_bezeichnung="Standard-Ausgangslage · 14.09.2026, 08:56",
    )


class TestJederKopfknopfSagtWasErTut:
    """P7.3-U3.4: Kein Symbolknopf ohne Beschriftung in der Kopfzeile.

    Bis dahin trugen die drei Aktionen ihren Namen nur im `title` — sichtbar erst,
    wenn jemand mit der Maus darauf verweilt. Gesucht wird jeder Knopf im Baum
    der Kopfzeile, nicht die drei heutigen; wer keinen Namen trägt, steht mit
    Grund in `shell.OHNE_BESCHRIFTUNG`. Dass die Beschriftung ab 1280 px auch
    **sichtbar** ist, misst der Browser-Wächter.
    """

    #: Gegen die eigene Blindheit: zwei Umschalter, drei Aktionen, das Design.
    KOPFKNOEPFE_MIN = 6

    def test_every_header_button_carries_its_name(self):
        knoepfe = _knoepfe(_kopf())
        stumm = [
            k.id
            for k in knoepfe
            if not _beschriftung(k).strip() and k.id not in shell.OHNE_BESCHRIFTUNG
        ]

        assert len(knoepfe) >= self.KOPFKNOEPFE_MIN, len(knoepfe)
        assert not stumm, f"Knöpfe ohne Beschriftung in der Kopfzeile: {stumm}"

    def test_every_exception_names_a_button_that_exists(self):
        kennungen = {k.id for k in _knoepfe(_kopf())}

        assert set(shell.OHNE_BESCHRIFTUNG) <= kennungen

    def test_the_guard_would_notice_a_mute_action(self):
        stumm = html.Div([shell.ui.icon_button("save", "Sichern", id="probe")])

        assert not _beschriftung(_knoepfe(stumm)[0]).strip()


class TestDieKopfzeileZeigtNurWasZumBereichPasst:
    """P7.3-U3.4: Laufauswahl und Dateien bei den Läufen, das Sichern beim Einrichten.

    Von Haiko entschieden am 2026-09-14, nachdem gemessen beschriftete
    Speicher-Aktionen neben der Laufauswahl die Navigation um 224 px
    zusammendrückten. Geprüft über **jeden** Bereich aus `shell.BEREICHE`.
    """

    @staticmethod
    def _sichtbar(stil) -> bool:
        return stil is None

    def test_saving_belongs_to_setup_alone(self):
        for route, _ in shell.BEREICHE:
            for lauf in (True, False):
                stile = shell.kontext_stile(route, lauf=lauf)

                erwartet = route == ""
                assert self._sichtbar(stile[shell.ACTION_SAVE]) is erwartet, route

    def test_the_run_and_its_files_belong_to_the_run_areas(self):
        for route, _ in shell.BEREICHE:
            for lauf in (True, False):
                stile = shell.kontext_stile(route, lauf=lauf)

                bei_laeufen = route in shell.LAUF_BEREICHE
                assert self._sichtbar(stile[shell.LAUF_WAHL]) is bei_laeufen, route
                assert self._sichtbar(stile[shell.ACTION_EXPORT]) is (bei_laeufen and lauf)

    def test_hidden_controls_stay_in_the_tree(self):
        """Regel 6: `config_editor.sichern` und `app._export` hängen an diesen Kennungen."""

        gerendert = _text(_kopf("doku"))

        for kennung in shell.KONTEXT:
            assert kennung in gerendert, kennung

    def test_every_action_of_the_header_has_a_place(self):
        aktionen = {k.id for k in _knoepfe(_kopf()) if str(k.id).startswith("shell-action-")}

        assert aktionen and aktionen <= set(shell.KONTEXT), aktionen

    def test_the_app_switches_them_with_the_area(self):
        schluessel = " ".join(web_app.app.callback_map)

        for kennung in shell.KONTEXT:
            assert f"{kennung}.style" in schluessel, kennung


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

    def test_a_marker_names_its_events_policy_first(self, demo):
        """P7.5-U5.4 (L4): Der Tooltip stand auf «Tick 12» und nannte kein Ereignis."""

        politik = next(
            e
            for e in demo.events
            if "policy" in str(e.get("event_type")) and int(e.get("round_number") or 0) > 0
        )
        tick = int(politik["round_number"])
        titel = [
            k.title
            for k in _alle(timeline.event_strip(demo))
            if "af-timeline__event" in str(getattr(k, "className", "") or "")
            and str(getattr(k, "title", "")).startswith(f"Tick {tick}:")
        ]

        assert len(titel) == 1, titel
        texte = titel[0].split(": ", 1)[1].split(" · ")
        assert texte[0] == politik["description"].strip(), "Politik steht nicht zuerst"
        assert len([t for t in texte if not t.startswith("+")]) <= timeline.TOOLTIP_MAX

    def test_many_events_on_one_tick_are_counted(self, demo):
        ereignisse = [{"description": f"E{i}", "event_type": "market_event"} for i in range(5)]

        titel = timeline._tooltip(7, ereignisse)

        assert titel == "Tick 7: E0 · E1 · E2 · +2 weitere"

    def test_the_legend_explains_every_colour_the_strip_sets(self, demo):
        gerendert = _text(timeline.event_strip(demo))

        assert "af-timeline__legend" in gerendert
        for stufe, name in timeline.LEGENDE:
            assert name in gerendert
            if stufe:
                assert f"af-timeline__swatch--{stufe}" in gerendert
                assert f"af-timeline__event--{stufe}" in gerendert

    def test_no_events_no_legend(self, demo):
        import dataclasses

        assert "af-timeline__legend" not in _text(
            timeline.event_strip(dataclasses.replace(demo, events=[]))
        )


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

    def test_the_overlay_no_longer_floats_over_the_plot(self):
        """P7.5-U5.3 (L3): Absolut über der Zeichenfläche deckte die Einblendung Punkte zu.

        Gelesen aus dem Stylesheet, weil die Lage dort entschieden wird; ob sie im
        Browser wirklich neben dem Diagramm steht, misst der Browser-Wächter.
        """

        import re
        from pathlib import Path

        css = (
            Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"
        ).read_text(encoding="utf-8")
        regeln = re.findall(r"\.af-scene__overlay\s*\{([^}]*)\}", css)

        assert regeln, "Die Regel für die Einblendung fehlt"
        assert not any("position: absolute" in regel for regel in regeln), regeln

    def test_dense_scenes_get_more_transparent(self):
        """P7.5-U5.3: Überplottung — bis zum Bezug unverändert, darüber durchsichtiger."""

        grund = 0.42
        assert scene.deckkraft(grund, 50) == grund
        assert scene.deckkraft(grund, scene.DICHTE_BEZUG) == grund
        assert scene.deckkraft(grund, 4 * scene.DICHTE_BEZUG) == pytest.approx(grund / 2)
        assert scene.deckkraft(grund, 10**7) == scene.DECKKRAFT_MIN

    def test_the_scene_uses_the_damping(self):
        """Die Formel allein reicht nicht — die Figur muss sie benutzen.

        Die Gegenprobe hat es gezeigt: Mit fester Deckkraft in `_figure` blieb jeder
        Test grün, weil nur `deckkraft` geprüft war.
        """

        import pandas as pd

        punkte = 4 * scene.DICHTE_BEZUG
        frame = pd.DataFrame(
            {
                "tick": [3] * punkte,
                "booked": [i % 2 == 0 for i in range(punkte)],
                "wtp_eur": [100.0 + i % 200 for i in range(punkte)],
                "environmental_awareness": [(i % 100) / 100 for i in range(punkte)],
            }
        )

        figur = scene._figure(frame, 3, 1.0, "light")

        deckkraefte = sorted(float(spur.marker.opacity) for spur in figur.data)
        assert deckkraefte == pytest.approx(
            sorted(scene.deckkraft(grund, punkte) for grund in (0.42, 0.62))
        )

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

    def test_each_chip_carries_short_name_state_and_wording(self, demo):
        """P7.5-U5.3: Kurzname und Zustand sichtbar, der Wortlaut im Tooltip und für Vorlesesoftware."""

        from dashboard.config_catalog import FAKTOR_KURZNAMEN, factor_options_from_file

        zustaende = demo.factors_at(30)
        texte = factor_options_from_file()
        streifen = scene.factor_strip(zustaende)
        chips = [
            k
            for k in streifen.children
            if "af-factor" in str(getattr(k, "className", "") or "").split()
        ]

        assert len(chips) == len(zustaende) == 7
        for chip in chips:
            teile = {k.className: k.children for k in chip.children if isinstance(k, html.Span)}
            factor_id = teile["af-factor__id"].split(".")[0]
            wortlaut = texte[factor_id][teile["af-factor__id"]]
            assert teile["af-factor__name"] == FAKTOR_KURZNAMEN[factor_id]
            assert wortlaut in chip.title
            assert wortlaut in teile["af-nur-vorlesen"]
        assert "af-factor__state" not in str(streifen), "Der abgeschnittene Zustandstext ist zurück"

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
    """Die Kopfzeile kennt drei Zustände der Anlage — keinen des gewählten Laufs."""

    @pytest.mark.parametrize(
        ("running", "demo_flag", "erwartet"),
        [
            (True, True, status.RUNNING),
            (False, True, status.DEMO),
            (False, False, status.READY),
        ],
    )
    def test_the_ranking_holds(self, running, demo_flag, erwartet):
        zustand = status.derive(running=running, demo=demo_flag)

        assert zustand.tone == erwartet

    def test_the_header_says_nothing_about_the_selected_run(self, tmp_path):
        """K2, P7.3-U3.2: «Lauf beeinträchtigt» stand als Anlagenzustand auf jedem Bereich.

        Die Warnung gehört dem gewählten Lauf und steht in dessen Kopf; die Singular-
        Zusage zu «ein Aufruf» hält `tests/test_web_layout.py` dort.
        """

        assert "degraded" not in inspect.signature(status.derive).parameters

        lauf = tmp_path / "run_kaputt"
        lauf.mkdir()
        (lauf / "run_metadata.json").write_text('{"degraded": true}', encoding="utf-8")
        auswahl = {"run_id": "run_kaputt", "run_dir": str(lauf)}

        assert web_app._status_for(auswahl).tone == status.READY

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
