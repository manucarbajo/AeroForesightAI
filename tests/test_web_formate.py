"""Zeitstempel zeigt die Oberfläche lesbar und in Ortszeit (P7.2-U2.6).

**Der Befund (Q6 des UI/UX-Audits):** In der Kopfzeile eines Laufs und in der
Übersicht stand der Zeitstempel roh aus `run_metadata.json` —
«2026-09-07T18:25:55.248822+00:00».

**Was gilt:** Er kommt durch `formate.zeitpunkt` und steht als «07.09.2026,
20:25» da, in der Ortszeit dessen, der hinsieht. In den Daten bleibt er ISO.
**Gemessen am gezeichneten Text** beider Stellen, nicht an der Aufrufstelle.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import pytest

from dashboard.web import formate

#: Wie ein roher ISO-Zeitstempel im Text aussieht.
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")

MOMENT = datetime(2026, 9, 7, 18, 25, 55, 248822, tzinfo=timezone.utc)


def _text(knoten) -> str:
    if knoten is None:
        return ""
    if isinstance(knoten, str):
        return knoten
    if isinstance(knoten, (list, tuple)):
        return " ".join(_text(k) for k in knoten)
    return _text(getattr(knoten, "children", None))


def _ortszeit(moment: datetime) -> str:
    return moment.astimezone().strftime("%d.%m.%Y, %H:%M")


class TestZeitpunkt:
    @pytest.mark.parametrize("wert", [MOMENT.isoformat(), "2026-09-07T18:25:55Z"])
    def test_an_iso_timestamp_reads_in_local_time(self, wert):
        assert formate.zeitpunkt(wert) == _ortszeit(MOMENT.replace(microsecond=0))

    @pytest.mark.parametrize(("wert", "erwartet"), [(None, "—"), ("", "—"), ("gestern", "gestern")])
    def test_what_cannot_be_read_stays_as_it_is(self, wert, erwartet):
        assert formate.zeitpunkt(wert) == erwartet


class TestKeinRoherZeitstempelImGezeichnetenText:
    def test_the_run_header_shows_a_readable_timestamp(self, tmp_path):
        from dashboard.run_browser import RunSummary
        from dashboard.web.pages import runs

        summary = RunSummary(
            run_id="run_probe",
            run_dir=tmp_path,
            ticks_completed=3,
            ticks_max=3,
            total_events=0,
            model="llama3.2",
            timestamp=MOMENT.isoformat(),
            has_narrative=False,
            has_tick_mechanics=False,
            has_run_scenario=False,
            scenario_title=None,
            scenario_summary=None,
        )

        text = _text(runs.lauf_kopf(summary))

        assert not _ISO.search(text), text
        assert _ortszeit(MOMENT) in text

    def test_the_overview_shows_a_readable_timestamp(self, tmp_path):
        from dashboard.web.views import overview

        (tmp_path / "run_metadata.json").write_text(
            json.dumps({"ticks_completed": 3, "ticks_max": 3, "timestamp": MOMENT.isoformat()}),
            encoding="utf-8",
        )

        text = _text(overview.render(tmp_path, "run_probe"))

        assert not _ISO.search(text), text
        assert _ortszeit(MOMENT) in text

    def test_the_search_would_notice_a_raw_timestamp(self):
        assert _ISO.search(f"erstellt {MOMENT.isoformat()}")
        assert not _ISO.search(f"erstellt {_ortszeit(MOMENT)}")


# --- Die Modellzeit (U2.6 Teil 3) ----------------------------------------------------------

#: (Datei unter `dashboard/web/`, Funktion) → Grund, warum dort eine Tick-Zahl
#: ohne Modellzeit steht.
OHNE_MODELLZEIT = {
    ("config_editor/__init__.py", "_namensvorschlag"): (
        "Ein Name soll kurz bleiben; die Modellzeit steht im Prüfschritt direkt daneben."
    ),
    ("config_editor/start_flow.py", "_vergleich_tiles"): (
        "Die Spanne zweier Längen tritt nur auf, wenn Rahmenszenarien verschieden lang "
        "sind; heute sind alle 120 Ticks lang."
    ),
    ("config_editor/start_flow.py", "_horizont_hinweis"): (
        "Zählt einen Abstand im Satz («die letzten N Ticks»), keine Lauflänge."
    ),
}


def _tick_zahlen(quelle: str) -> set[tuple[str, int]]:
    """(Funktion, Zeile) jeder f-Zeichenkette, die eine Tick-Zahl ohne `formate` baut."""

    import ast

    baum = ast.parse(quelle)
    funde: set[tuple[str, int]] = set()
    for funktion in ast.walk(baum):
        if not isinstance(funktion, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for knoten in ast.walk(funktion):
            if not isinstance(knoten, ast.JoinedStr):
                continue
            teile = knoten.values
            for i, teil in enumerate(teile):
                if not isinstance(teil, ast.FormattedValue):
                    continue
                aufruf = teil.value
                if (
                    isinstance(aufruf, ast.Call)
                    and isinstance(aufruf.func, ast.Attribute)
                    and isinstance(aufruf.func.value, ast.Name)
                    and aufruf.func.value.id == "formate"
                ):
                    continue
                danach = teile[i + 1] if i + 1 < len(teile) else None
                davor = teile[i - 1] if i > 0 else None
                zahl_davor = isinstance(danach, ast.Constant) and re.match(
                    r"\**\s*Ticks\b", str(danach.value)
                )
                beschriftung_davor = isinstance(davor, ast.Constant) and re.search(
                    r"Ticks:\s*$", str(davor.value)
                )
                if zahl_davor or beschriftung_davor:
                    funde.add((funktion.name, knoten.lineno))
    return funde


def _alle_tick_zahlen() -> dict[tuple[str, int], set[str]]:
    from pathlib import Path

    wurzel = Path(formate.__file__).resolve().parent
    orte: dict[tuple[str, int], set[str]] = {}
    for pfad in sorted(wurzel.rglob("*.py")):
        datei = pfad.relative_to(wurzel).as_posix()
        if datei == "formate.py":
            # Die Quelle selbst: Hier entsteht die Form, die alle anderen nehmen.
            continue
        for name, zeile in _tick_zahlen(pfad.read_text(encoding="utf-8")):
            orte.setdefault((datei, zeile), set()).add(name)
    return orte


class TestModellzeit:
    @pytest.mark.parametrize(
        ("ticks", "erwartet"),
        [
            (1, "1 Monat"),
            (6, "6 Monate"),
            (11, "11 Monate"),
            (12, "1 Jahr"),
            (18, "rund 2 Jahre"),
            (40, "rund 3 Jahre"),
            (50, "rund 4 Jahre"),
            (120, "10 Jahre"),
            ("40", "rund 3 Jahre"),
        ],
    )
    def test_a_tick_count_reads_as_model_time(self, ticks, erwartet):
        assert formate.modellzeit(ticks) == erwartet

    @pytest.mark.parametrize("ticks", ["?", None, 0, -3, "vierzig"])
    def test_an_unknown_length_has_no_model_time(self, ticks):
        assert formate.modellzeit(ticks) == ""

    def test_the_short_form_carries_both(self):
        assert formate.ticks_mit_modellzeit(40) == "40 Ticks · rund 3 Jahre"
        assert formate.ticks_mit_modellzeit("?") == "? Ticks"

    def test_it_follows_the_mechanics(self):
        """Gemessen an der einen Kalenderzuordnung, die es gibt (P3.8) — nicht gesetzt."""

        from src.backtest.reihen import tick_je_monat

        zuordnung = tick_je_monat()

        assert zuordnung["2016-01"] - zuordnung["2015-01"] == formate.TICKS_JE_JAHR


class TestJedeLauflaengeSagtIhreModellzeit:
    """**Gesucht, nicht aufgezählt:** jede f-Zeichenkette unter `dashboard/web/`,
    die eine Zahl vor «Ticks» oder hinter «Ticks:» setzt, ohne `formate` zu fragen."""

    def test_no_tick_count_is_built_without_model_time(self):
        befunde = [
            f"{datei}:{zeile} in {sorted(namen)}"
            for (datei, zeile), namen in sorted(_alle_tick_zahlen().items())
            if not any((datei, name) in OHNE_MODELLZEIT for name in namen)
        ]

        assert not befunde, "\n  ".join(
            [
                "Diese Stellen nennen eine Tick-Zahl ohne Modellzeit:",
                *befunde,
                "`formate.ticks_mit_modellzeit(ticks)` — oder mit Grund in `OHNE_MODELLZEIT`.",
            ]
        )

    def test_every_exception_still_has_its_place_and_a_reason(self):
        orte = _alle_tick_zahlen()

        for (datei, funktion), grund in OHNE_MODELLZEIT.items():
            assert any(
                d == datei and funktion in namen for (d, _), namen in orte.items()
            ), f"Ausnahme ohne Stelle dahinter: {datei} · {funktion}"
            assert len(grund) >= 30, f"Ausnahme ohne Grund: {datei} · {funktion}"

    def test_the_search_would_notice_a_bare_tick_count(self):
        probe = (
            'def a(t):\n    return f"{t} Ticks"\n'
            'def b(t):\n    return f"Ticks: {t}"\n'
            'def c(t):\n    return f"über **{t} Ticks**"\n'
            'def d(t):\n    return f"{formate.ticks_mit_modellzeit(t)}"\n'
            'def e(t):\n    return f"bei Tick {t}"\n'
        )

        assert sorted(name for name, _ in _tick_zahlen(probe)) == ["a", "b", "c"]

    def test_the_setup_and_the_rail_name_the_model_time(self):
        from dashboard.web.config_editor import start_flow
        from dashboard.web.pages import launch
        from dashboard.web.state import initial_draft_dict

        entwurf = {**initial_draft_dict(), "rounds": 40, "run_all_sweeps": False}

        assert "40 Ticks · rund 3 Jahre" in start_flow.summary_sentence(entwurf)
        # Seit P7.5-U5.1 die Stand-Zeile — die Zeile unter dem Start-Knopf ist entfallen.
        assert "40 Ticks · rund 3 Jahre" in str(launch.summary_rows(entwurf))


# --- Zahlen (P8-V6, 2026-10-01) ------------------------------------------------

#: Ein englischer Dezimalbruch: Punkt vor höchstens zwei Ziffern. «1.027» ist eine
#: deutsche Tausendertrennung und zählt nicht.
_ENGLISCH = re.compile(r"\b\d+\.\d{1,2}\b")


class TestZahlen:
    """Im Leitstand standen «37.4%» und «131.94 €» — auf einer Folie des Pitches."""

    @pytest.mark.parametrize(
        ("wert", "stellen", "erwartet"),
        [(131.94, 2, "131,94"), (1027.5, 2, "1.027,50"), (0.81, 2, "0,81"), (50.0, 0, "50")],
    )
    def test_eine_zahl_steht_deutsch_da(self, wert, stellen, erwartet):
        assert formate.zahl(wert, stellen) == erwartet

    def test_geld_und_anteil(self):
        assert formate.euro(131.94) == "131,94 €"
        assert formate.prozent(0.374) == "37,4 %"

    @pytest.mark.parametrize("tick", [1, 2, 20, 35])
    def test_die_kennzahlen_des_leitstands_sind_deutsch(self, tick):
        from dashboard.web import run_data
        from dashboard.web.views import telemetry

        text = _text(telemetry.kpi_row(run_data.demo(), tick))

        assert "%" in text and "€" in text, "Misst der Test ins Leere?"
        assert not _ENGLISCH.findall(text), _ENGLISCH.findall(text)

    def test_die_veraenderung_der_buchungsrate_steht_in_prozentpunkten(self):
        """Neben «23,3 %» stand «↓ −0,036» — ein Anteil neben einem Prozentwert (2026-10-02)."""

        from dashboard.web.run_data import RunData
        from dashboard.web.views import telemetry

        daten = RunData(
            run_id="probe",
            run_dir=None,
            ticks=[{"tick": 23, "booking_rate": 0.233, "booking_rate_delta": -0.036}],
        )

        text = _text(telemetry.kpi_row(daten, 23))

        assert "−3,6 Pp." in text
        assert "0,036" not in text
