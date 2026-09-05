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

import json
from pathlib import Path

import pytest

from dashboard.web.views import figures as figuren
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


# ---------------------------------------------------------------------------
# Die Darstellung — die zweite Hälfte von P2.6 (2026-08-31)
# ---------------------------------------------------------------------------


class TestDasBandWirdAuchGezeichnet:
    """**Ohne diese Klasse war P2.6 eine Datei, die niemand sieht.**

    Die Perzentile lagen seit dem 2026-08-30 in `multi_run_summary.json`, und
    die Ansicht «Preis und Nachfrage» zeigte weiterhin eine Linie. Ein Band, das
    nur im Artefakt steht, beantwortet die Frage nicht, für die es gebaut wurde:
    *Wie sicher ist diese Zahl?*

    Gezeichnet wird es in `dashboard/web/views/figures._view_nachfrage` — bei
    **Aussage 1**, weil `ENSEMBLE_REIHEN` genau deren beide Größen abdeckt.
    """

    TICKS = 4

    @pytest.fixture(autouse=True)
    def _plotly_templates(self):
        """Ohne die Registrierung wirft `style_figure` auf einen Namen.

        **Nicht auf die Testreihenfolge verlassen:** `app.py` registriert sie
        beim Start, `test_web_theme.py` nebenbei — wer sich darauf verlässt,
        hat einen Test, der allein läuft und im Verbund grün ist (oder
        umgekehrt).
        """

        from dashboard.web import theme

        theme.register_template()

    @staticmethod
    def _lauf(verzeichnis: Path) -> Path:
        """Ein Laufverzeichnis mit dem Nötigsten für Aussage 1."""

        verzeichnis.mkdir(parents=True, exist_ok=True)
        (verzeichnis / "tick_mechanics.json").write_text(
            json.dumps(
                {
                    "ticks": [
                        {"tick": t, "booking_rate": 0.4, "ticket_price": 100.0 + t}
                        for t in range(1, TestDasBandWirdAuchGezeichnet.TICKS + 1)
                    ]
                }
            ),
            encoding="utf-8",
        )
        return verzeichnis

    @classmethod
    def _batch(cls, wurzel: Path, *, laeufe: int) -> Path:
        """Ein Batch-Verzeichnis samt Zusammenfassung; gibt einen Lauf zurück."""

        wurzel.mkdir(parents=True, exist_ok=True)
        lauf = cls._lauf(wurzel / "run_001")
        spanne = list(range(cls.TICKS))
        (wurzel / "multi_run_summary.json").write_text(
            json.dumps(
                {
                    "aggregate": {
                        "baender": {
                            "laeufe": laeufe,
                            "ticks": cls.TICKS,
                            "perzentile": [10, 50, 90],
                            "reihen": {
                                "booking_rate": {
                                    "p10": [0.30 for _ in spanne],
                                    "p50": [0.40 for _ in spanne],
                                    "p90": [0.50 for _ in spanne],
                                },
                                "ticket_price": {
                                    "p10": [98.0 + t for t in spanne],
                                    "p50": [101.0 + t for t in spanne],
                                    "p90": [104.0 + t for t in spanne],
                                },
                            },
                        }
                    },
                    "runs": [],
                }
            ),
            encoding="utf-8",
        )
        return lauf

    @staticmethod
    def _spuren(knoten) -> list:
        """Alle Plotly-Spuren aus einem Dash-Baum einsammeln."""

        gefunden: list = []

        def geh(n):
            if n is None or isinstance(n, str):
                return
            if hasattr(n, "figure"):
                gefunden.extend(n.figure.data)
            kinder = getattr(n, "children", None)
            if isinstance(kinder, list):
                for kind in kinder:
                    geh(kind)
            else:
                geh(kinder)

        geh(knoten)
        return gefunden

    def test_ein_ensemble_bekommt_sein_band(self, tmp_path):
        lauf = self._batch(tmp_path / "batch", laeufe=8)

        flaechen = [s for s in self._spuren(figuren._view_nachfrage(lauf)) if s.fill == "toself"]

        assert len(flaechen) == 2, "Erwartet je eine Fläche für Preis und Buchungsrate"
        assert all("80 %" in s.name for s in flaechen), [s.name for s in flaechen]

    def test_ein_einzellauf_bekommt_keines(self, tmp_path):
        """**Kein Fehlerfall, sondern der Normalfall.** Ein Lauf ohne
        Batch-Nachbarn zeigt seine Linie, und das ist richtig so."""

        lauf = self._lauf(tmp_path / "run_allein")

        assert figuren._baender(lauf) is None
        assert not [s for s in self._spuren(figuren._view_nachfrage(lauf)) if s.fill == "toself"]

    def test_ein_ensemble_aus_einem_lauf_bekommt_auch_keines(self, tmp_path):
        """Bei einem Lauf fallen alle Perzentile zusammen (siehe `_perzentil`).

        Das als Band zu zeichnen ergäbe eine Fläche der Breite null — unsichtbar,
        aber mit einer Legende, die Streuung **behauptet**. Lieber keine Aussage
        als eine leere.
        """

        lauf = self._batch(tmp_path / "batch_eins", laeufe=1)

        assert figuren._baender(lauf) is None

    def test_das_band_liegt_hinter_den_linien(self, tmp_path):
        """Plotly zeichnet in der Reihenfolge des Hinzufügens.

        Läge die Fläche darüber, verschleierte sie genau das, was die Aussage
        trägt — den Median.
        """

        lauf = self._batch(tmp_path / "batch", laeufe=8)
        spuren = self._spuren(figuren._view_nachfrage(lauf))

        letzte_flaeche = max(i for i, s in enumerate(spuren) if s.fill == "toself")
        erste_linie = min(i for i, s in enumerate(spuren) if s.fill != "toself")

        assert letzte_flaeche < erste_linie

    @pytest.mark.parametrize("modus", ["light", "dark"])
    def test_die_bandfarbe_kommt_aus_den_tokens(self, tmp_path, modus):
        """Regel 4 des Dashboards — Farbe kommt aus `theme`, nirgends sonst her.

        Plotly braucht für eine Fläche Alpha, die Tokens sind Hex ohne. Die
        Umrechnung steht deshalb in `theme.band_fill` und **leitet ab**, statt
        einen zweiten Farbwert danebenzustellen.
        """

        from dashboard.web import theme

        lauf = self._batch(tmp_path / "batch", laeufe=8)
        spuren = self._spuren(figuren._view_nachfrage(lauf, modus))
        fuellungen = {s.fillcolor for s in spuren if s.fill == "toself"}

        assert fuellungen == {theme.band_fill("price", modus), theme.band_fill("booking", modus)}

    def test_hell_und_dunkel_faerben_verschieden(self, tmp_path):
        lauf = self._batch(tmp_path / "batch", laeufe=8)

        hell = {s.fillcolor for s in self._spuren(figuren._view_nachfrage(lauf, "light")) if s.fill}
        dunkel = {
            s.fillcolor for s in self._spuren(figuren._view_nachfrage(lauf, "dark")) if s.fill
        }

        assert hell and dunkel and hell != dunkel

    def test_das_band_reicht_nur_so_weit_wie_es_traegt(self, tmp_path):
        """Es ist so lang wie der **kürzeste** Lauf; die Linie darf länger sein.

        Würde es auf die volle Tick-Achse gestreckt, liefe es am Ende auf
        Perzentile aus zwei statt fünfzig Werten hinaus — sichtbar als
        zusammenlaufendes Band, tatsächlich nur eine dünnere Stichprobe.
        """

        lauf = self._batch(tmp_path / "batch", laeufe=8)
        # Der Lauf selbst geht zwei Ticks weiter als das Band.
        inhalt = json.loads((lauf / "tick_mechanics.json").read_text(encoding="utf-8"))
        inhalt["ticks"] += [
            {"tick": t, "booking_rate": 0.4, "ticket_price": 120.0}
            for t in (self.TICKS + 1, self.TICKS + 2)
        ]
        (lauf / "tick_mechanics.json").write_text(json.dumps(inhalt), encoding="utf-8")

        spuren = self._spuren(figuren._view_nachfrage(lauf))
        flaeche = next(s for s in spuren if s.fill == "toself")
        linie = next(s for s in spuren if s.fill != "toself")

        # Eine geschlossene Fläche trägt jeden Tick zweimal (hin und zurück).
        assert len(flaeche.x) == 2 * self.TICKS
        assert len(linie.x) == self.TICKS + 2
