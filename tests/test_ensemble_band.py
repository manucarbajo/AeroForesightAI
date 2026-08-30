"""P2.6 — mehrere Läufe eines Rahmens ergeben ein Band, keinen Punktwert.

`run_multi` gab es schon; was fehlte, war die Auswertung. `aggregate_runs`
zählte bis zum 2026-08-30 nur Buchhaltung — wie viele Läufe, welche Seeds, wie
viele Ereignisse. Über das, wofür man mehrere Läufe überhaupt rechnet, sagte sie
nichts. **Ein Ensemble ohne Verteilung ist eine teure Art, denselben Punktwert
mehrfach zu bekommen.**

Der Unterschied für ein Unternehmen: «Yields fallen um 11 %» ist eine
Behauptung, «Yields fallen um 8 bis 14 %» eine Aussage.

**Die Reihenfolge im Projektplan war kein Zufall.** Ohne die echte Ziehung aus
P2.1 ergaben fünfzig Seeds fünfzig identische Buchungsverläufe — das Band hätte
die Streuung des Bevölkerungs-Samplings gezeigt und wäre für die Unsicherheit
des Modells gehalten worden. Der Test unten misst deshalb nicht nur, *dass* ein
Band da ist, sondern dass es **Breite hat**.

**Gemessen am 2026-08-30** (20 Läufe, 12 Ticks, Standardrahmen):

    booking_rate  Tick  7: p10 0,3096  p50 0,3215  p90 0,3414   Breite 0,032
    ticket_price  Tick 13: p10 138,90  p50 140,38  p90 142,26   Breite 3,36 €
"""

from __future__ import annotations

import pytest

from src.config_loader import build_initial_state
from src.llm.studio_helpers import MockLLM
from src.orchestration.simulation_runner import (
    ENSEMBLE_REIHEN,
    PERZENTILE,
    RunnerOptions,
    SimulationRunner,
    ensemble_baender,
)

TICKS = 8
LAEUFE = 8


def _runner() -> SimulationRunner:
    return SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )


def _ensemble(*, laeufe: int = LAEUFE, seed: int | None = None):
    state = build_initial_state()
    state.clock.max_ticks = TICKS
    if seed is not None:
        state.config.seed = seed
    return _runner().run_multi(laeufe, base_state=state)


@pytest.fixture(scope="module")
def ensemble():
    return _ensemble()


class TestDasBandIstDa:
    def test_der_aggregat_traegt_es(self, ensemble):
        assert (
            "baender" in ensemble.aggregate
        ), "`aggregate_runs` liefert kein Band — dann zählt es wieder nur Buchhaltung."
        band = ensemble.aggregate["baender"]
        assert band["laeufe"] == LAEUFE
        assert band["ticks"] > 0
        assert set(band["reihen"]) == set(ENSEMBLE_REIHEN)

    @pytest.mark.parametrize("reihe", ENSEMBLE_REIHEN)
    def test_jede_reihe_traegt_jedes_perzentil(self, ensemble, reihe):
        werte = ensemble.aggregate["baender"]["reihen"][reihe]
        ticks = ensemble.aggregate["baender"]["ticks"]

        for p in PERZENTILE:
            assert f"p{p}" in werte
            assert len(werte[f"p{p}"]) == ticks, (
                f"{reihe}/p{p} hat {len(werte[f'p{p}'])} Werte statt {ticks} — "
                "dann beschreibt das Band nicht den ganzen Lauf."
            )

    @pytest.mark.parametrize("reihe", ENSEMBLE_REIHEN)
    def test_die_perzentile_liegen_in_der_richtigen_reihenfolge(self, ensemble, reihe):
        werte = ensemble.aggregate["baender"]["reihen"][reihe]

        for i, (unten, mitte, oben) in enumerate(zip(werte["p10"], werte["p50"], werte["p90"])):
            if None in (unten, mitte, oben):
                continue
            assert unten <= mitte <= oben, f"{reihe}, Tick {i + 1}: {unten} / {mitte} / {oben}"


class TestDasBandHatBreite:
    """Der Kern — und der Grund, warum P2.6 auf P2.1 wartete."""

    @pytest.mark.parametrize("reihe", ENSEMBLE_REIHEN)
    def test_es_ist_nicht_ueberall_eine_linie(self, ensemble, reihe):
        werte = ensemble.aggregate["baender"]["reihen"][reihe]
        breiten = [
            oben - unten
            for unten, oben in zip(werte["p10"], werte["p90"])
            if None not in (unten, oben)
        ]

        assert breiten, f"{reihe}: keine auswertbaren Ticks"
        assert max(breiten) > 0.0, (
            f"Das Band von {reihe} ist über den ganzen Lauf eine Linie. Dann liefern "
            "die Wiederholungen identische Verläufe — genau der Zustand, den P2.1 "
            "beseitigt hat, und das Ensemble misst nichts."
        )

    def test_ein_einzelner_lauf_ergibt_eine_linie(self):
        """Die Gegenprobe: Mit einem Lauf müssen alle Perzentile zusammenfallen.

        Fiele der Test um, läge die Breite nicht an den Läufen, sondern an der
        Perzentil-Rechnung.
        """

        band = _ensemble(laeufe=1).aggregate["baender"]
        werte = band["reihen"]["ticket_price"]

        assert all(
            a == b == c for a, b, c in zip(werte["p10"], werte["p50"], werte["p90"])
        ), "Ein einziger Lauf ergibt ein Band mit Breite — dann rechnet das Perzentil falsch."


class TestDasBandIstReproduzierbar:
    def test_gleicher_ausgangswert_gleiches_band(self):
        a = _ensemble(seed=7).aggregate["baender"]
        b = _ensemble(seed=7).aggregate["baender"]

        assert a == b, (
            "Zwei Ensembles mit demselben Ausgangswert liefern verschiedene Bänder — "
            "dann hängt die Ziehung an etwas anderem als am Seed."
        )

    def test_ein_anderer_ausgangswert_ergibt_ein_anderes_band(self):
        a = _ensemble(seed=7).aggregate["baender"]
        b = _ensemble(seed=99).aggregate["baender"]

        assert a != b, (
            "Zwei Ensembles mit verschiedenen Ausgangswerten liefern dasselbe Band — "
            "dann geht der Seed nicht in die Wiederholungen ein."
        )


class TestDieRechnungSelbst:
    """Die Perzentile ohne einen Lauf drumherum — schnell und scharf."""

    def test_eine_fehlende_messung_ist_keine_null(self):
        """`booking_rate` ist optional. Ein fehlender Wert darf das Perzentil
        nicht nach unten ziehen, als sei nichts gebucht worden."""

        from src.models.event_models import PriceHistoryEntry
        from src.orchestration.simulation_runner import SingleRunResult

        def lauf(raten):
            state = build_initial_state()
            state.price_history = [
                PriceHistoryEntry(
                    round_number=i + 1,
                    agent_id="provider",
                    price=100.0,
                    demand_level=1.0,
                    booking_rate=r,
                )
                for i, r in enumerate(raten)
            ]
            return SingleRunResult(
                run_id="r",
                seed=1,
                final_state=state,
                ticks_completed=len(raten),
                checkpoint_paths=[],
            )

        band = ensemble_baender([lauf([0.4]), lauf([None]), lauf([0.6])])
        werte = band["reihen"]["booking_rate"]

        assert werte["p50"][0] == pytest.approx(0.5), (
            f"Der Median ist {werte['p50'][0]} — bei 0,4 und 0,6 plus einer fehlenden "
            "Messung wäre 0,5 richtig. Eine 0 an ihrer Stelle zöge ihn auf 0,4."
        )

    def test_kuerzere_laeufe_kuerzen_das_band(self):
        """Sonst stünde am Ende ein Perzentil aus zwei statt fünfzig Werten — das
        sähe wie ein zusammenlaufendes Band aus und wäre nur dünner besetzt."""

        from src.models.event_models import PriceHistoryEntry
        from src.orchestration.simulation_runner import SingleRunResult

        def lauf(ticks):
            state = build_initial_state()
            state.price_history = [
                PriceHistoryEntry(
                    round_number=i + 1,
                    agent_id="p",
                    price=100.0,
                    demand_level=1.0,
                    booking_rate=0.5,
                )
                for i in range(ticks)
            ]
            return SingleRunResult(
                run_id="r", seed=1, final_state=state, ticks_completed=ticks, checkpoint_paths=[]
            )

        band = ensemble_baender([lauf(10), lauf(4), lauf(10)])

        assert band["ticks"] == 4
        assert len(band["reihen"]["ticket_price"]["p50"]) == 4

    def test_ohne_laeufe_gibt_es_kein_band(self):
        assert ensemble_baender([]) == {}
