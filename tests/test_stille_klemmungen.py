"""P3.5: Ein geklemmter Wert und eine Debugausgabe sagen jetzt, dass sie da sind.

Zwei Befunde, ein Paket:

1. **`threshold` und `max_contributions_per_agent` wurden stillschweigend
   geklemmt.** Wer bewusst `threshold=1` setzte, bekam 3 — die Einstellung war
   entgegengenommen und nicht wirksam. Dieselbe Klasse wie die erfundenen
   Vorgabewerte aus P1.9-W5.1 (Dashboard) und P2.11 (Marktkonstanten): eine
   zweite Quelle für einen Wert, den jemand ausdrücklich genannt hat.
2. **Acht `print()` im Scheduler**, unbedingt in jedem Tick, ohne Level und ohne
   Abschaltmöglichkeit.

**Die Reihenfolge war der Fallstrick, und sie ist eingehalten:** P3.5 durfte
nicht vor P0.1 kommen, weil das Fortschritts-Log des Dashboards ausschließlich
von `print()` gespeist wurde (`run_launcher` leitet `stdout` in einen Tee um).
Der Logging-Handler, der in denselben Tee schreibt, ist mit P0.1 entstanden
(`logging_setup.progress_logging`) — deshalb ist die tragende Zusage hier nicht
«kein `print` mehr», sondern **dass das Fortschrittsfenster weiter sieht, was es
vorher sah**.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from src.agents.redebedarf_scheduler import (
    DEFAULT_MAX_CONTRIBUTIONS_PER_AGENT,
    DEFAULT_THRESHOLD,
    RedebedarfScheduler,
)
from src.agents.scheduler_node import SchedulerNode
from src.config_loader import build_initial_state
from src.logging_setup import progress_logging

ROOT = Path(__file__).resolve().parent.parent


class TestEinGeklemmterWertWirdAbgewiesen:
    """Abweisen statt klemmen — die Grenzen sind dieselben, sie sagen nur etwas."""

    def test_die_vorgabewerte_gehen_durch(self):
        scheduler = RedebedarfScheduler(["consumer"])

        assert scheduler.threshold == DEFAULT_THRESHOLD
        assert scheduler.max_contributions_per_agent == DEFAULT_MAX_CONTRIBUTIONS_PER_AGENT

    @pytest.mark.parametrize("wert", [1, 2, 0, -5])
    def test_eine_zu_kleine_schwelle_wird_abgewiesen(self, wert):
        """**Der Befund im Wortlaut:** `threshold=1` ergab stillschweigend 3."""

        with pytest.raises(ValueError, match="threshold"):
            RedebedarfScheduler(["consumer"], threshold=wert)

    @pytest.mark.parametrize("wert", [0, 4, 99])
    def test_eine_beitragsgrenze_ausserhalb_des_bereichs_ebenso(self, wert):
        with pytest.raises(ValueError, match="max_contributions_per_agent"):
            RedebedarfScheduler(["consumer"], max_contributions_per_agent=wert)

    def test_die_meldung_nennt_den_zulaessigen_bereich(self):
        with pytest.raises(ValueError) as fehler:
            RedebedarfScheduler(["consumer"], max_contributions_per_agent=9)

        assert "1–3" in str(fehler.value)

    def test_eine_schwelle_ueber_der_skala_wird_abgewiesen(self):
        """**Mit P3.5 dazugekommen**, und der Fall war vorher nicht geklemmt.

        Liegt die Schwelle über `max_score`, kann kein Agent sie je
        überschreiten: Der Scheduler bliebe dauerhaft stumm und sähe aus wie ein
        Lauf, in dem niemand Redebedarf hatte. Die alte Klemmung fing nur nach
        unten ab.
        """

        with pytest.raises(ValueError, match="max_score"):
            RedebedarfScheduler(["consumer"], threshold=11, max_score=10)

    def test_ein_wert_am_rand_gilt(self):
        """Die Grenzen sind einschließend — sonst hätte P3.5 sie verschoben."""

        scheduler = RedebedarfScheduler(
            ["consumer"], threshold=DEFAULT_THRESHOLD, max_contributions_per_agent=1
        )

        assert scheduler.threshold == DEFAULT_THRESHOLD
        assert scheduler.max_contributions_per_agent == 1

    def test_die_grenzen_stehen_nicht_als_literale_im_konstruktor(self):
        """Sonst wären es wieder zwei Quellen für dieselbe Zahl (P2.11).

        Vorher stand `max(3, threshold)` und `max(1, min(3, …))` **neben**
        `DEFAULT_THRESHOLD = 3` und `DEFAULT_MAX_CONTRIBUTIONS_PER_AGENT = 3` —
        wer eine der Konstanten geändert hätte, hätte die Klemmung unverändert
        gelassen.
        """

        quelle = (ROOT / "src" / "agents" / "redebedarf_scheduler.py").read_text("utf-8")
        baum = ast.parse(quelle)
        init = next(
            k for k in ast.walk(baum) if isinstance(k, ast.FunctionDef) and k.name == "__init__"
        )
        aufrufe = {
            k.func.id
            for k in ast.walk(init)
            if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
        }

        assert "max" not in aufrufe and "min" not in aufrufe, (
            "Im Konstruktor wird wieder geklemmt — dann nimmt er eine Einstellung "
            "an und rechnet mit einer anderen."
        )


class TestEinNormalerLaufIstAufStdoutStill:
    """Und das Fortschrittsfenster sieht trotzdem, was es vorher sah."""

    @staticmethod
    def _zustand():
        state = build_initial_state()
        state.clock.current_tick = 1
        state.clock.max_ticks = 3
        return state

    def test_kein_print_mehr_im_scheduler(self):
        """Gemessen am Syntaxbaum, nicht an der Ausgabe: Ein `print` in einem
        Zweig, den dieser Test nicht durchläuft, fällt sonst nicht auf."""

        for name in ("scheduler_node.py", "redebedarf_scheduler.py"):
            quelle = (ROOT / "src" / "agents" / name).read_text("utf-8")
            aufrufe = [
                k.lineno
                for k in ast.walk(ast.parse(quelle))
                if isinstance(k, ast.Call) and isinstance(k.func, ast.Name) and k.func.id == "print"
            ]

            assert not aufrufe, f"{name} ruft noch `print` in Zeile {aufrufe}"

    def test_der_lauf_schreibt_nichts_auf_stdout(self, capsys):
        SchedulerNode().invoke(self._zustand())

        assert capsys.readouterr().out == "", "Der Scheduler schreibt weiter auf stdout"

    def test_das_fortschrittsfenster_sieht_die_reihenfolge(self):
        """**Die tragende Zusage von P3.5**, und der Grund für die Reihenfolge
        gegenüber P0.1.

        Gemessen wird nicht «es wird geloggt», sondern dass die Zeile durch
        `progress_logging` wirklich am Fortschrittsfenster ankommt — dieselbe
        Kette, die das Dashboard benutzt.
        """

        zeilen: list[str] = []
        with progress_logging(zeilen.append):
            SchedulerNode().invoke(self._zustand())

        assert any("Redebedarf-Reihenfolge" in z for z in zeilen), (
            "Das Fortschrittsfenster sieht die Sprechreihenfolge nicht mehr — "
            f"angekommen ist: {zeilen}"
        )

    def test_die_debugzeilen_bleiben_im_normalfall_weg(self, caplog):
        """Sieben der acht Zeilen waren Debugausgabe und laufen nicht mehr mit."""

        with caplog.at_level(logging.INFO):
            SchedulerNode().invoke(self._zustand())

        assert "bereits gesprochen" not in caplog.text
        assert "Redebedarf-Punkte" not in caplog.text

    def test_auf_ausdrueckliche_nachfrage_sind_sie_noch_da(self, caplog):
        """Weggeworfen wäre schlechter als leise: Sie helfen beim Nachstellen."""

        with caplog.at_level(logging.DEBUG):
            SchedulerNode().invoke(self._zustand())

        assert "bereits gesprochen" in caplog.text
