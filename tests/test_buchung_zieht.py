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
def koeffizienten(properties):
    """Die ausgelieferten Koeffizienten — nicht die Vorgaben des Modells.

    Sie sollen identisch sein (`test_buchungskoeffizienten.py` misst das); der
    Test nimmt trotzdem die Datei, weil er das prüft, was ein Lauf benutzt.
    """

    return properties.booking_model


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
        system_properties={},
        rng=buchungsstrom(42, tick),
    )
    return stats.total_demand


class TestDieWahrscheinlichkeitIstEineZahl:
    """Zusage 1 — sie wird nicht mehr auf 0 oder 1 gerundet."""

    def test_sie_liegt_zwischen_null_und_eins(self, leute, koeffizienten):
        werte = [
            booking_probability(
                x,
                ticket_price=140.0,
                carbon_tax=50.0,
                koeffizienten=koeffizienten,
                verfuegbarkeit=1.0,
            )
            for x in leute
        ]
        assert all(0.0 <= w <= 1.0 for w in werte)
        assert not all(
            w in (0.0, 1.0) for w in werte
        ), "Alle Wahrscheinlichkeiten sind 0 oder 1 — dann ist die Schwelle zurück."

    def test_zwischenwerte_kommen_wirklich_vor(self, leute, koeffizienten):
        """Der Kern: Personen, die die Schwelle gleich behandelt hätte."""

        mittel = [
            w
            for w in (
                booking_probability(
                    x,
                    ticket_price=140.0,
                    carbon_tax=50.0,
                    koeffizienten=koeffizienten,
                    verfuegbarkeit=1.0,
                )
                for x in leute
            )
            if 0.5 < w < 0.9
        ]
        assert len(mittel) > 20, (
            f"Nur {len(mittel)} Personen mit einer Wahrscheinlichkeit zwischen 0,5 und 0,9 — "
            "genau diese hat die alte Schwelle alle als sichere Bucher behandelt."
        )

    def test_wer_es_sich_nicht_leisten_kann_bucht_nicht(self, leute, koeffizienten):
        """Null heißt «kann nicht», nicht «unwahrscheinlich»."""

        werte = [
            booking_probability(
                x,
                ticket_price=100_000.0,
                carbon_tax=50.0,
                koeffizienten=koeffizienten,
                verfuegbarkeit=1.0,
            )
            for x in leute
        ]
        assert set(werte) == {0.0}

        _, stats = evaluate_booking(
            leute,
            ticket_price=100_000.0,
            carbon_tax=50.0,
            properties=None,
            system_properties={},
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

    def test_die_schwelle_ueberzeichnete_die_nachfrage(self, leute, properties, koeffizienten):
        """Der gemessene Unterschied, an einer Stelle festgehalten.

        Bei 80 Euro buchten unter der Schwelle 96,8 % — mit Ziehung sind es
        74,2 %. Der Test prüft die **Richtung**, nicht die Nachkommastelle: Eine
        Konfigurationsänderung darf die Zahlen verschieben, den systematischen
        Charakter des Unterschieds aber nicht.
        """

        ps = [
            booking_probability(
                x,
                ticket_price=80.0,
                carbon_tax=50.0,
                koeffizienten=koeffizienten,
                verfuegbarkeit=1.0,
            )
            for x in leute
        ]
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


class TestEinkommenWirktNichtNurAlsSchwelle:
    """**Der Befund B5 des Audits vom 2026-09-03, als Zusage.**

    `income_factor` stand bis dahin **ausschließlich** in der
    Erschwinglichkeitsschranke. Die Folge, und sie ist schwer zu übersehen,
    sobald man sie ausspricht: **Wer sich das Ticket leisten konnte, für den war
    Einkommen danach exakt folgenlos.** Ein Doppelverdiener und jemand knapp
    über der Grenze verspürten denselben Verzicht, und die gemessene
    «Einkommenselastizität» von +0,69 war nichts als die Dichte der
    Zahlungsbereitschaft am Preis — kein Verhaltensparameter.

    **Seither wird der Preis an dem gemessen, was jemand hat**
    (`normalized_price / income_factor`): dieselbe Ausgabe ist ein anderer
    Verzicht, je nachdem wovon sie abgeht. Das ist die Budgetanteils-Form und in
    der Nachfragetheorie der Regelfall — und sie kostet **keinen neuen
    Koeffizienten**, weil Einkommen über den Preiskanal wirkt, den es ohnehin
    gibt.
    """

    @staticmethod
    def _person(leute, *, einkommen: float):
        """Jemand, für den die Schranke **nicht** bindet.

        Das ist die Kontrolle, ohne die der Test nichts sagt: Ohne sie misst er
        wieder nur die Erschwinglichkeit, also genau den Mechanismus, der schon
        vorher da war.
        """

        vorlage = leute[0]
        return vorlage.model_copy(
            update={"wtp_eur": 1000.0, "income_factor": einkommen, "saturation_level": 0.0}
        )

    def test_wer_es_sich_beide_leisten_koennen_entscheidet_verschieden(self, leute, koeffizienten):
        """**Die tragende Zusage.** Genau der Fall, der vorher folgenlos war."""

        arm = self._person(leute, einkommen=0.7)
        reich = self._person(leute, einkommen=1.4)

        p_arm, p_reich = (
            booking_probability(
                person,
                ticket_price=140.0,
                carbon_tax=50.0,
                koeffizienten=koeffizienten,
                verfuegbarkeit=1.0,
            )
            for person in (arm, reich)
        )

        # Die Kontrolle: Bei 1000 EUR Zahlungsbereitschaft bindet die Schranke
        # für keinen von beiden — was hier auseinandergeht, ist der Nutzen.
        assert 0.0 < p_arm < p_reich, (
            f"Ärmer {p_arm:.4f}, reicher {p_reich:.4f}. Beide können sich das Ticket "
            "leisten; unterscheiden sie sich nicht, steht das Einkommen wieder nur "
            "in der Schranke."
        )
        assert p_reich - p_arm > 0.05, (
            f"Der Unterschied beträgt {p_reich - p_arm:.4f} — das ist Rauschen, " "keine Wirkung."
        )

    def test_die_elastizitaet_liegt_am_rand_ueber_eins(self, leute, koeffizienten):
        """Luftverkehr gilt als Luxusgut — und das folgt hier aus der **Form**,
        nicht aus einer gesetzten Zahl.

        Geprüft wird am Rand (+5 %), weil die Elastizität im Logit vom
        Betriebspunkt abhängt: Sie fällt mit steigendem Einkommen, wie die
        Preiselastizität mit steigendem Preis.
        """

        from statistics import mean

        def rate(faktor: float) -> float:
            return mean(
                booking_probability(
                    person.model_copy(update={"income_factor": person.income_factor * faktor}),
                    ticket_price=140.0,
                    carbon_tax=50.0,
                    koeffizienten=koeffizienten,
                    verfuegbarkeit=1.0,
                )
                for person in leute
            )

        basis, hoch = rate(1.0), rate(1.05)
        elastizitaet = ((hoch - basis) / basis) / 0.05

        assert elastizitaet > 1.0, (
            f"Einkommenselastizität {elastizitaet:.2f}. Unter 1 wäre Fliegen ein "
            "gewöhnliches Gut — die Fachlage führt es als Luxusgut, und die "
            "Budgetanteils-Form gibt das her, ohne dass jemand eine Zahl setzt."
        )

    def test_ohne_einkommen_keine_reise(self, leute, koeffizienten):
        """Der Rand des Wertebereichs — und der Grund, warum kein Epsilon im
        Nenner steht. Erreichbar ist der Fall nur bei einem Ticketpreis von
        null; sonst greift die Erschwinglichkeitsschranke zuerst."""

        assert (
            booking_probability(
                self._person(leute, einkommen=0.0),
                ticket_price=0.0,
                carbon_tax=0.0,
                koeffizienten=koeffizienten,
                verfuegbarkeit=1.0,
            )
            == 0.0
        )

    def test_die_bahn_wird_nicht_am_einkommen_gemessen(self, leute, koeffizienten):
        """**Bewusst nicht deflationiert.** Der Substitutionsterm sagt, wie
        attraktiv die Alternative gegenüber dem Flug ist — das hängt am Fahrpreis-
        und Zeitverhältnis, nicht am Budgetanteil. Ihn mitzuskalieren hiesse, das
        Einkommen zweimal durch denselben Nutzenterm zu schicken.

        Gemessen daran, dass zwei Personen mit gleicher Zahlungsbereitschaft und
        gleichem Einkommen, aber verschiedener Bahnbereitschaft, sich weiterhin
        um genau den Substitutionsterm unterscheiden.
        """

        basis = self._person(leute, einkommen=1.0).model_copy(
            update={"substitution_readiness": 0.0}
        )
        bahnaffin = basis.model_copy(update={"substitution_readiness": 0.8})

        args = dict(
            ticket_price=140.0, carbon_tax=50.0, koeffizienten=koeffizienten, verfuegbarkeit=1.0
        )
        reich = basis.model_copy(update={"income_factor": 2.0})
        reich_bahnaffin = bahnaffin.model_copy(update={"income_factor": 2.0})

        import math

        def logit(p: float) -> float:
            return math.log(p / (1.0 - p))

        # Der Abstand im Nutzen ist der Substitutionsterm. Haengt er am
        # Einkommen, waere er bei den Reichen kleiner.
        arm_delta = logit(booking_probability(basis, **args)) - logit(
            booking_probability(bahnaffin, **args)
        )
        reich_delta = logit(booking_probability(reich, **args)) - logit(
            booking_probability(reich_bahnaffin, **args)
        )

        assert arm_delta == pytest.approx(reich_delta, rel=1e-9), (
            f"Substitutionsabstand {arm_delta:.4f} gegen {reich_delta:.4f} — der Term "
            "haengt am Einkommen, und damit zaehlt es zweimal."
        )
