"""Ein Lauf heißt Name · Rahmen · Datum, und die Kennung steht bei den Hashes (D6).

**Von Haiko entschieden am 2026-09-14.** Gemessen trugen 179 von 190 Läufen in
der Auswahl denselben Titel «Trend-Fortsetzung» hinter ihrer Kennung; der
Rahmen ist das, was sie unterscheidet. Die Kennung ist ein Ablageort — sie
steht unter «Technische Details» der Übersicht und nicht in der Auswahl.
"""

from __future__ import annotations

import re
from pathlib import Path

from dashboard.run_browser import RunSummary
from dashboard.web.pages import runs

VORGABE = "Flugverkehr-Szenarioplanung"

#: Eine Kennung, wie `create_run_id` sie baut, oder der Name eines Sweep-Ordners.
KENNUNG = re.compile("run_[0-9]{8}T|sweep_|batch_")


def _lauf(
    run_id="run_20260914T065633Z",
    *,
    name=None,
    rahmen="Business as Usual",
    zeit="2026-09-14T06:56:33+00:00",
) -> RunSummary:
    return RunSummary(
        run_id=run_id,
        run_dir=Path("."),
        ticks_completed=3,
        ticks_max=3,
        total_events=0,
        model=None,
        timestamp=zeit,
        has_narrative=False,
        has_tick_mechanics=True,
        has_run_scenario=False,
        scenario_title="Trend-Fortsetzung",
        scenario_summary=None,
        simulation_name=name,
        rahmen_name=rahmen,
    )


class TestEinLaufHeisstNameRahmenDatum:
    def test_the_label_names_the_run_and_not_its_folder(self):
        text = runs.lauf_bezeichnung(_lauf(name="CO₂ 200 ab Tick 5"), vorgabe=VORGABE)

        assert text.startswith("CO₂ 200 ab Tick 5 · Business as Usual · ")
        assert not KENNUNG.search(text), text

    def test_the_default_name_is_no_name(self):
        text = runs.lauf_bezeichnung(_lauf(name=VORGABE), vorgabe=VORGABE)

        assert text.startswith("Business as Usual · "), text
        assert VORGABE not in text

    def test_without_a_frame_it_says_so(self):
        text = runs.lauf_bezeichnung(_lauf(rahmen=None), vorgabe=VORGABE)

        assert text.startswith(runs.OHNE_RAHMEN + " · "), text

    def test_the_title_of_a_generated_scenario_is_not_the_name(self):
        """«Trend-Fortsetzung» stand bei 179 von 190 Läufen — genau das, was D6 abräumt."""

        assert "Trend-Fortsetzung" not in runs.lauf_bezeichnung(_lauf(), vorgabe=VORGABE)

    def test_repetitions_of_a_batch_carry_their_number(self):
        erste = runs.lauf_bezeichnung(_lauf("batch_20260914T065633Z/run_001"), vorgabe=VORGABE)
        zweite = runs.lauf_bezeichnung(_lauf("batch_20260914T065633Z/run_002"), vorgabe=VORGABE)

        assert erste != zweite
        assert erste.endswith("Wiederholung 1") and zweite.endswith("Wiederholung 2")
