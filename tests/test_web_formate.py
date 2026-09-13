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

        text = _text(runs._meta(summary))

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
