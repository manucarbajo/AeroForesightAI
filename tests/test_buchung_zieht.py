"""P2.1 — die Buchung zieht gegen die Wahrscheinlichkeit, statt sie wegzuwerfen.

Bis zum 2026-08-30 rechnete `_booking_probability` die Sigmoid und verglich sie
gegen 0,5. Weil die Sigmoid monoton ist, war das mathematisch identisch mit
`utility >= 0` — der Logit-Teil tat nichts. Zwei Personen mit p = 0,51 und
p = 0,99 buchten gleichermaßen sicher, und über einen ganzen Lauf gab es zu
jedem Preis genau **eine** mögliche Buchungsrate.

**Was das an den Zahlen ändert**, gemessen an 2000 Personen der ausgelieferten
Konfiguration (`carbon_tax = 50`):

    Preis   Schwelle   Ziehung   Streuung über 20 Ströme
       80      0,968     0,742     0,715 – 0,755
      110      0,847     0,602     0,577 – 0,615
      140      0,621     0,439     0,419 – 0,449
      180      0,299     0,243     0,229 – 0,255
      250      0,059     0,072     0,065 – 0,082

Die Schwelle **überzeichnet** die Nachfrage bei niedrigen Preisen und
**unterzeichnet** sie bei hohen: Sie drückt jede Wahrscheinlichkeit auf 0 oder 1
und staucht damit die Nachfragekurve zu den Rändern hin. Und sie liefert keine
Streuung — der Grund, warum P2.6 (Ensemble) ohne dieses Paket sinnlos wäre.

Vier Zusagen hängen hier, und die vierte ist die, an der das Paket scheitern
konnte: **Ein Strom pro Tick.** `run_population_tick` bekommt in jedem Tick
denselben Lauf-Seed. Ein naiv daraus gebauter Generator zöge jedes Mal dieselbe
Folge — es buchten immer dieselben Individuen, und die Rate würde zur
Stufenfunktion. Reproduzierbar, aber falsch, und schwer zu bemerken, weil die
Zahlen plausibel aussehen.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.config_loader import load_properties_config
from src.models.population_models import PopulationConfig
from src.population.population_sampler import (
    booking_probability,
    buchungsstrom,
    evaluate_booking,
    initialize_population,
)


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


@pytest.fixture(scope="module")
def leute(properties):
    return initialize_population(
        properties, PopulationConfig(segments=[], total_population=800), seed=42
    )


def _rate(leute, properties, *, preis: float, tick: int) -> float:
    _, stats = evaluate_booking(
        leute,
        ticket_price=preis,
        carbon_tax=50.0,
        properties=properties,
        rng=buchungsstrom(42, tick),
    )
    return stats.total_demand


class TestDieWahrscheinlichkeitIstEineZahl:
    """Zusage 1 — sie wird nicht mehr auf 0 oder 1 gerundet."""

    def test_sie_liegt_zwischen_null_und_eins(self, leute):
        werte = [booking_probability(x, ticket_price=140.0, carbon_tax=50.0) for x in leute]
        assert all(0.0 <= w <= 1.0 for w in werte)
        assert not all(
            w in (0.0, 1.0) for w in werte
        ), "Alle Wahrscheinlichkeiten sind 0 oder 1 — dann ist die Schwelle zurück."

    def test_zwischenwerte_kommen_wirklich_vor(self, leute):
        """Der Kern: Personen, die die Schwelle gleich behandelt hätte."""

        mittel = [
            w
            for w in (booking_probability(x, ticket_price=140.0, carbon_tax=50.0) for x in leute)
            if 0.5 < w < 0.9
        ]
        assert len(mittel) > 20, (
            f"Nur {len(mittel)} Personen mit einer Wahrscheinlichkeit zwischen 0,5 und 0,9 — "
            "genau diese hat die alte Schwelle alle als sichere Bucher behandelt."
        )

    def test_wer_es_sich_nicht_leisten_kann_bucht_nicht(self, leute):
        """Null heißt «kann nicht», nicht «unwahrscheinlich»."""

        werte = [booking_probability(x, ticket_price=100_000.0, carbon_tax=50.0) for x in leute]
        assert set(werte) == {0.0}

        _, stats = evaluate_booking(
            leute,
            ticket_price=100_000.0,
            carbon_tax=50.0,
            properties=None,
            rng=buchungsstrom(42, 1),
        )
        assert stats.total_demand == 0.0, (
            "Bei p = 0 hat trotzdem jemand gebucht — dann ist der Vergleich `<` zu `<=` "
            "geworden, und `rng.random()` liefert die 0,0 mit positiver Wahrscheinlichkeit."
        )


class TestEsWirdWirklichGezogen:
    """Zusage 2 — verschiedene Ströme, verschiedene Ergebnisse."""

    def test_zwei_stroeme_ergeben_verschiedene_raten(self, leute, properties):
        raten = {_rate(leute, properties, preis=140.0, tick=t) for t in range(1, 11)}
        assert (
            len(raten) > 1
        ), f"Zehn Ströme, eine einzige Rate ({raten}) — dann wird nicht gezogen."

    def test_die_streuung_ist_klein_aber_da(self, leute, properties):
        """Eine Bandbreite, keine Beliebigkeit — sonst wäre das Modell wertlos."""

        raten = [_rate(leute, properties, preis=140.0, tick=t) for t in range(1, 21)]
        spanne = max(raten) - min(raten)
        assert 0.0 < spanne < 0.1, (
            f"Die Streuung über 20 Ströme beträgt {spanne:.3f}. Null hieße: keine "
            "Ziehung. Mehr als 0,1 bei 800 Personen hieße: hier stimmt etwas nicht."
        )

    def test_die_schwelle_ueberzeichnete_die_nachfrage(self, leute, properties):
        """Der gemessene Unterschied, an einer Stelle festgehalten.

        Bei 80 Euro buchten unter der Schwelle 96,8 % — mit Ziehung sind es
        74,2 %. Der Test prüft die **Richtung**, nicht die Nachkommastelle: Eine
        Konfigurationsänderung darf die Zahlen verschieben, den systematischen
        Charakter des Unterschieds aber nicht.
        """

        ps = [booking_probability(x, ticket_price=80.0, carbon_tax=50.0) for x in leute]
        wie_schwelle = sum(1 for p in ps if p >= 0.5) / len(ps)
        mit_ziehung = _rate(leute, properties, preis=80.0, tick=1)

        assert wie_schwelle > mit_ziehung + 0.1, (
            f"Schwelle {wie_schwelle:.3f}, Ziehung {mit_ziehung:.3f} — der "
            "systematische Aufschlag der Schwelle bei niedrigen Preisen ist weg."
        )


class TestDerStromGehoertEinemTick:
    """Zusage 3 und 4 — reproduzierbar, aber nicht in jedem Tick dieselbe Folge."""

    def test_gleicher_lauf_gleicher_tick_gleiche_folge(self):
        a = buchungsstrom(42, 7).random(5)
        b = buchungsstrom(42, 7).random(5)
        assert np.array_equal(a, b)

    def test_verschiedene_ticks_verschiedene_folge(self):
        """**Der Fallstrick des Pakets.** Ohne diese Eigenschaft buchten in jedem
        Tick dieselben Individuen, und die Buchungsrate würde zur Stufenfunktion."""

        folgen = {tuple(buchungsstrom(42, t).random(5)) for t in range(1, 11)}
        assert len(folgen) == 10, (
            "Zwei Ticks teilen sich eine Zahlenfolge — dann hängt der Strom nicht "
            "mehr am Tick, und es buchen immer dieselben Personen."
        )

    def test_verschiedene_laeufe_verschiedene_folge(self):
        folgen = {tuple(buchungsstrom(s, 1).random(5)) for s in range(1, 11)}
        assert len(folgen) == 10

    def test_der_lauf_gibt_ihn_von_aussen_hinein(self):
        """`evaluate_booking` darf sich keinen eigenen besorgen (Invariante 1)."""

        import inspect

        signatur = inspect.signature(evaluate_booking)
        assert "rng" in signatur.parameters
        assert (
            signatur.parameters["rng"].default is inspect.Parameter.empty
        ), "`rng` hat einen Default — dann wäre er in jedem Tick derselbe."


class TestDerLaufBleibtReproduzierbar:
    """Zusage 3 — die Ziehung nimmt dem Lauf seine Wiederholbarkeit nicht."""

    def test_zwei_laeufe_mit_gleichem_seed_sind_gleich(self):
        from src.config_loader import build_initial_state
        from src.llm.studio_helpers import MockLLM
        from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

        def lauf():
            state = build_initial_state()
            state.clock.max_ticks = 4
            runner = SimulationRunner(
                llm=MockLLM(),
                options=RunnerOptions(
                    enable_market=True,
                    enable_cib=True,
                    deterministic_only=True,
                    checkpoint_interval=0,
                    verbose_ticks=False,
                ),
            )
            ende = runner.run(state, seed=11, run_id="probe")
            return [round(e.booking_rate, 6) for e in ende.price_history]

        assert lauf() == lauf(), (
            "Zwei Läufe mit demselben Seed liefern verschiedene Buchungsraten — "
            "dann hängt die Ziehung an etwas anderem als am Seed."
        )
