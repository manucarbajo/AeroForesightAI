"""P2.8-B — die Preisstrategie ist eine Wahl, keine Annahme.

**Der Bias-Befund, der dazu geführt hat** (2026-08-31): P2.8 Weg A hat die
Kapazität eingeführt, aber nur *eine* Art, darauf zu reagieren — der Anbieter
senkte den Preis, bis er voll war. Gemessen hieß das: Kapazität +50 % erzwang
Preis −25 %.

Damit war ausgerechnet die reale Lage 2015–2019 im Modell **nicht darstellbar**:
mehr Sitze bei **flachen** Preisen. Und das Werkzeug hatte eine Theorie der
Preissetzung eingebaut, statt sie zur Auswahl zu stellen.

**Warum das mehr ist als eine fehlende Option:** Ein Szenariowerkzeug, das nur
eine Verhaltensannahme kennt, beantwortet «was wäre wenn» immer nur unter dieser
Annahme. Ein Fachprüfer liest darin zu Recht einen Bias — und eine Simulation,
die eine Möglichkeit baulich ausschließt, ist keine Simulation dieser
Möglichkeit.

**Zwei Strategien, beide gültig:**

- `auslastung` — der Anbieter senkt den Preis, bis die Kapazität gefüllt ist.
  Das Verhalten bis P2.8-B und weiterhin der **Standard**, damit sich ohne
  Zutun nichts ändert.
- `marge` — der Anbieter hält seinen Aufschlag; die Auslastung schwankt.
  Kommt Kapazität dazu, bleibt der Preis, wo er ist.

Welche gilt, ist eine Frage an das Szenario, nicht an das Modell.
"""

from __future__ import annotations

from statistics import mean

import pytest

from src.config_loader import build_initial_state, load_properties_config
from src.llm.studio_helpers import MockLLM
from src.models.property_models import STRATEGIEN, MarketFeedbackConfig
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner


def _lauf(strategie: str, kapazitaet: float, *, ticks: int = 40) -> tuple[float, float]:
    """Buchungsrate und Preis im letzten Viertel eines Laufs."""

    zustand = build_initial_state()
    zustand.clock.max_ticks = ticks

    regeln = []
    for regel in zustand.properties.market_rules:
        if regel.effect.get("type") == "booking_yield_feedback":
            effekt = dict(regel.effect)
            effekt["strategie"] = strategie
            regel = regel.model_copy(update={"effect": effekt})
        regeln.append(regel)
    zustand.properties = zustand.properties.model_copy(update={"market_rules": regeln})

    for prop in zustand.properties.system_properties:
        if prop.id == "kapazitaet_index" and prop.trajectory is not None:
            prop.trajectory.baseline = kapazitaet
            prop.trajectory.rules = []

    ende = SimulationRunner(
        llm=MockLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    ).run(zustand, seed=42, run_id=f"strategie_{strategie}_{kapazitaet}")

    spaet = [e for e in ende.price_history if e.round_number > ticks * 0.75]
    raten = [e.booking_rate for e in spaet if e.booking_rate is not None]
    return mean(raten), mean(e.price for e in spaet)


class TestDerStandardBleibtWieErWar:
    """Eine neue Wahlmöglichkeit darf nichts ändern, solange niemand wählt."""

    def test_die_ausgelieferte_config_regelt_auf_auslastung(self):
        from src.market.market_feedback import resolve_market_feedback_config

        config = resolve_market_feedback_config(load_properties_config())

        assert config.strategie == "auslastung"

    def test_der_modell_default_ebenfalls(self):
        assert MarketFeedbackConfig().strategie == "auslastung"

    def test_eine_unbekannte_strategie_scheitert_laut(self):
        """Sonst fiele ein Tippfehler still auf `auslastung` zurück — dieselbe
        Klasse von Befund wie bei den Shift-Zielen (P2.4)."""

        with pytest.raises(ValueError, match="Unbekannte Preisstrategie"):
            MarketFeedbackConfig(strategie="marge_")

    def test_es_bleiben_genau_zwei(self):
        assert STRATEGIEN == ("auslastung", "marge")


class TestUnterMargeBleibtDerPreisStehen:
    """**Die Zusage, für die das Paket gebaut wurde.**

    «Es kann ja auch mal mehr Plätze geben, aber gleich teuer bleiben.» Unter
    `auslastung` ist das baulich unmöglich; unter `marge` ist es der Normalfall.
    """

    KAPAZITAETEN = (0.5, 0.7, 1.0, 1.3)

    def test_mehr_plaetze_aendern_den_preis_nicht(self):
        preise = [_lauf("marge", k)[1] for k in self.KAPAZITAETEN]

        spanne = max(preise) - min(preise)
        assert spanne < 1.0, (
            f"Der Preis bewegt sich um {spanne:.2f} EUR über Kapazitäten von "
            f"{self.KAPAZITAETEN[0]} bis {self.KAPAZITAETEN[-1]}. Unter `marge` "
            "soll er stehen bleiben."
        )

    def test_unter_auslastung_bewegt_er_sich_deutlich(self):
        """Die Gegenprobe — ohne sie prüfte der Test oben nur, dass irgendetwas
        konstant ist."""

        preise = [_lauf("auslastung", k)[1] for k in self.KAPAZITAETEN]

        assert max(preise) - min(preise) > 30.0, (
            f"Unter `auslastung` bewegt sich der Preis nur um "
            f"{max(preise) - min(preise):.2f} EUR — dann unterscheiden sich die "
            "beiden Strategien nicht mehr."
        )

    def test_und_unter_auslastung_faellt_er_mit_mehr_kapazitaet(self):
        """Die eingebaute Annahme, die P2.8-B sichtbar gemacht hat: Der Anbieter
        senkt den Preis, bis er voll ist."""

        wenig = _lauf("auslastung", 0.5)[1]
        viel = _lauf("auslastung", 1.3)[1]

        assert viel < wenig * 0.8, f"0,5 → {wenig:.2f} EUR, 1,3 → {viel:.2f} EUR"


class TestDieKapazitaetIstUnterMargeEineSchranke:
    """Ohne sie täte die Kapazität unter `marge` **nichts**.

    Der Anbieter hält seinen Aufschlag, die Nachfrage ergibt sich aus der
    Bevölkerung — ob zehn oder tausend Sitze da sind, stünde nirgends in der
    Rechnung. Erst als Grenze wird «mehr Plätze» zu einer Aussage.
    """

    @staticmethod
    def _ein_tick(strategie: str, kapazitaet: float, preis: float):
        from src.population.population_sampler import run_population_tick

        properties = load_properties_config()
        regeln = []
        for regel in properties.market_rules:
            if regel.effect.get("type") == "booking_yield_feedback":
                effekt = dict(regel.effect)
                effekt["strategie"] = strategie
                regel = regel.model_copy(update={"effect": effekt})
            regeln.append(regel)
        properties = properties.model_copy(update={"market_rules": regeln})

        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        _, stats = run_population_tick(
            properties,
            config,
            None,
            ticket_price=preis,
            carbon_tax=50.0,
            factors={},
            system_properties={
                "bevoelkerungsentwicklung": 1000,
                "kapazitaet_index": kapazitaet,
            },
            seed=42,
            current_tick=1,
            metrics={},
        )
        return stats.total_demand

    @pytest.mark.parametrize("kapazitaet", [0.5, 1.0])
    def test_niemand_bucht_ueber_die_kapazitaet_hinaus(self, kapazitaet: float):
        """Bei niedrigem Preis übersteigt die Nachfrage die Plätze — dann bleiben
        Leute übrig."""

        from src.market.market_feedback import resolve_market_feedback_config

        basis = resolve_market_feedback_config(load_properties_config()).target_booking_rate
        schranke = basis * kapazitaet

        gebucht = self._ein_tick("marge", kapazitaet, preis=100.0)

        assert (
            gebucht <= schranke + 1e-9
        ), f"{gebucht:.4f} gebucht bei einer Schranke von {schranke:.4f}"

    def test_ohne_schranke_waeren_es_mehr(self):
        """Die Gegenprobe: Unter `auslastung` greift kein Deckel, weil der Preis
        ohnehin dorthin steuert."""

        mit = self._ein_tick("marge", 0.5, preis=100.0)
        ohne = self._ein_tick("auslastung", 0.5, preis=100.0)

        assert ohne > mit, f"mit Schranke {mit:.4f}, ohne {ohne:.4f}"

    def test_wer_keinen_platz_bekommt_wird_zufaellig_gewaehlt(self):
        """**Bewusst keine zweite Verhaltensannahme.**

        Eine Auswahl nach Zahlungsbereitschaft unterstellte ein
        Erlösmanagement, das teure Buchungen bevorzugt — genau die stille
        Annahme, gegen die dieses Paket steht. Geprüft wird es daran, dass die
        mittlere Zahlungsbereitschaft der Buchenden sich **nicht** verschiebt.
        """

        from src.market.market_feedback import resolve_market_feedback_config
        from src.population.population_sampler import run_population_tick

        properties = load_properties_config()
        regeln = []
        for regel in properties.market_rules:
            if regel.effect.get("type") == "booking_yield_feedback":
                effekt = dict(regel.effect)
                effekt["strategie"] = "marge"
                regel = regel.model_copy(update={"effect": effekt})
            regeln.append(regel)
        properties = properties.model_copy(update={"market_rules": regeln})

        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        leute, _ = run_population_tick(
            properties,
            config,
            None,
            ticket_price=100.0,
            carbon_tax=50.0,
            factors={},
            system_properties={"bevoelkerungsentwicklung": 1000, "kapazitaet_index": 0.5},
            seed=42,
            current_tick=1,
            metrics={},
        )

        gebucht = [p for p in leute if p.booked]
        leer = [p for p in leute if not p.booked and p.wtp_eur >= 100.0]

        assert gebucht and leer, "Der Fall kommt im Test nicht vor"
        assert mean(p.wtp_eur for p in gebucht) < mean(p.wtp_eur for p in leer) * 1.25, (
            "Die Buchenden haben deutlich höhere Zahlungsbereitschaft — dann "
            "wählt die Schranke nach Zahlungsbereitschaft aus, und das wäre eine "
            "Verhaltensannahme, die niemand getroffen hat."
        )
        assert resolve_market_feedback_config(properties).strategie == "marge"


class TestWerKeinenPlatzBekommtWirdNichtGesaettigt:
    """**Der Rechenfehler, den das Audit vom 2026-09-03 gefunden hat.**

    Bis dahin lief die Kapazitätsschranke als eigener Schritt **nach**
    `evaluate_booking` und setzte den Überzähligen `booked = False` — der
    Sättigungsaufschlag war da aber schon vergeben. Gemessen (`marge`,
    `kapazitaet_index = 0,5`, ein Tick, 1000 Personen): 658 wollten buchen, 185
    bekamen einen Platz, und **473 gingen leer aus und trugen trotzdem
    `saturation_level = 0,6`** in den nächsten Tick. Sie wurden für eine Reise
    bestraft, die sie nicht angetreten haben — und die Nachfrage sank dadurch
    dauerhaft unter die Kapazität, statt sich an ihr zu stauen.

    **Warum ihn kein Wächter gefangen hat, und das ist die Lehre:** Die elf
    Zusagen dieser Datei prüften den *Preis* über Kapazitäten hinweg und die
    Zufälligkeit der Auswahl. Den **Zustand der Abgewiesenen** prüfte keine —
    dieselbe Klasse wie bei P2.4-E: *Ein Wächter, der den Mechanismus prüft
    statt die Zusage, ist grün und nutzlos.*

    Der Docstring der Funktion behauptete das Gegenteil («Die Sättigung bleibt
    unberührt … weil `booked` zurückgesetzt wird, bevor die Sättigung daran
    anknüpft»). Sie knüpfte nicht danach an, sie war schon vergeben.
    """

    @staticmethod
    def _ein_tick(kapazitaet: float, preis: float = 100.0):
        from src.population.population_sampler import run_population_tick

        properties = load_properties_config()
        regeln = []
        for regel in properties.market_rules:
            if regel.effect.get("type") == "booking_yield_feedback":
                effekt = dict(regel.effect)
                effekt["strategie"] = "marge"
                regel = regel.model_copy(update={"effect": effekt})
            regeln.append(regel)
        properties = properties.model_copy(update={"market_rules": regeln})

        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        return run_population_tick(
            properties,
            config,
            None,
            ticket_price=preis,
            carbon_tax=50.0,
            factors={},
            system_properties={"bevoelkerungsentwicklung": 1000, "kapazitaet_index": kapazitaet},
            seed=42,
            current_tick=1,
            metrics={},
        )

    def test_die_schranke_greift_in_diesem_aufbau_ueberhaupt(self):
        """Ohne diese Vorbedingung wäre der Test unten trivial grün."""

        leute, stats = self._ein_tick(0.5)
        gebucht = [p for p in leute if p.booked]

        assert len(gebucht) < len(leute) * 0.5, "in diesem Aufbau bleibt niemand übrig"
        assert stats.total_demand > 0, "es bucht niemand — dann misst der Test nichts"

    @pytest.mark.parametrize("kapazitaet", [0.3, 0.5])
    def test_niemand_ohne_buchung_traegt_einen_aufschlag(self, kapazitaet: float):
        """**Die eigentliche Zusage.**

        Im ersten Tick startet jede Person bei 0 und der Abbau lässt sie dort.
        Wer danach `booked = False` trägt, darf keine Sättigung haben — sonst
        ist er für eine Reise bestraft, die er nicht angetreten hat.
        """

        leute, _ = self._ein_tick(kapazitaet)
        falsch = [p for p in leute if not p.booked and p.saturation_level > 0.0]

        assert not falsch, (
            f"{len(falsch)} von {sum(1 for p in leute if not p.booked)} Nicht-Buchenden "
            f"tragen einen Sättigungsaufschlag (z. B. id={falsch[0].id}: "
            f"{falsch[0].saturation_level}). Die Rationierung muss **vor** die "
            "Sättigung, nicht danach — zurückrechnen geht nicht, weil `min(1.0, …)` "
            "klemmt."
        )

    def test_wer_fliegt_wird_sehr_wohl_gesaettigt(self):
        """Die Gegenprobe — sonst wäre der Test oben auch grün, wenn die
        Sättigung ganz ausfiele."""

        leute, _ = self._ein_tick(0.5)
        gebucht = [p for p in leute if p.booked]

        assert gebucht, "niemand hat gebucht"
        assert all(p.saturation_level > 0.0 for p in gebucht), (
            "Buchende tragen keine Sättigung mehr — dann ist der Aufschlag beim "
            "Umbau ganz verlorengegangen."
        )

    def test_unter_auslastung_bleibt_alles_wie_es_war(self):
        """Ohne Schranke wird nicht rationiert, also auch nichts verschoben —
        und der Zufallsstrom des Ticks bleibt derselbe."""

        from src.population.population_sampler import run_population_tick

        properties = load_properties_config()
        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        leute, _ = run_population_tick(
            properties,
            config,
            None,
            ticket_price=100.0,
            carbon_tax=50.0,
            factors={},
            system_properties={"bevoelkerungsentwicklung": 1000, "kapazitaet_index": 0.5},
            seed=42,
            current_tick=1,
            metrics={},
        )

        assert all(p.saturation_level > 0.0 for p in leute if p.booked)
        assert all(p.saturation_level == 0.0 for p in leute if not p.booked)


class TestMehrPlaetzeBeiGleichemPreisHeisstMehrVerkehr:
    """**Die Zusage, die bis zum 2026-09-03 keine Zeile geprüft hat.**

    P2.8-B versprach, dass «mehr Sitze bei flachen Preisen» darstellbar wird —
    die reale Lage 2015–2019. Geprüft wurden davon zwei Hälften: dass der Preis
    unter `marge` über Kapazitäten hinweg steht, und dass die Schranke in einem
    Ein-Tick-Aufbau greift. **Das Paar dazwischen fehlte**, und genau darin lag
    der Befund: Über 40 Ticks änderte die doppelte Sitzzahl die Buchungsrate um
    0,0001. Eine Obergrenze kann Nachfrage nur senken, nie heben.

    Seit B2 ist die Kapazität ein **Merkmal der Alternative** und steht im
    Nutzen: Mehr Angebot heißt mehr Frequenzen und Strecken, also niedrigere
    generalisierte Reisekosten. Diese Klasse prüft die Zusage als Ganzes —
    *beide* Größen zugleich, weil jede für sich trivial zu erfüllen wäre.
    """

    KAPAZITAETEN = (0.5, 1.0, 1.3)

    def test_mehr_kapazitaet_heisst_mehr_verkehr(self):
        raten = [_lauf("marge", k)[0] for k in self.KAPAZITAETEN]

        assert raten == sorted(raten), (
            f"Die Buchungsrate folgt der Kapazität nicht: {raten}. Unter `marge` "
            "soll mehr Angebot mehr Verkehr bedeuten."
        )
        assert raten[-1] > raten[0] * 1.2, (
            f"Von {self.KAPAZITAETEN[0]} auf {self.KAPAZITAETEN[-1]} bewegt sich die "
            f"Rate nur von {raten[0]:.4f} auf {raten[-1]:.4f} — das ist der Zustand "
            "vor B2, in dem die Kapazität nur als Obergrenze wirkte."
        )

    def test_und_zwar_ohne_dass_der_preis_nachgibt(self):
        """**Das Paar ist die Zusage, nicht die Hälfte.**

        Mehr Verkehr allein bekommt man auch unter `auslastung` — dort aber nur,
        weil der Anbieter den Preis senkt. Genau diese eingebaute
        Verhaltensannahme war der Bias-Befund.
        """

        preise = [_lauf("marge", k)[1] for k in self.KAPAZITAETEN]

        assert max(preise) - min(preise) < 1.0, (
            f"Der Preis bewegt sich um {max(preise) - min(preise):.2f} EUR — dann ist "
            "es dieselbe Aussage wie unter `auslastung`."
        )

    def test_der_standard_bleibt_unberuehrt(self):
        """`ln(1) = 0` — ohne Kapazitätsvorgabe ändert der Kanal exakt nichts.

        Dieselbe Disziplin wie beim Einführen der Größe selbst (P2.8): Eine neue
        Wirkung darf nichts verschieben, solange niemand sie einstellt.
        """

        from src.models.property_models import BookingModelConfig
        from src.population.population_sampler import booking_probability

        properties = load_properties_config()
        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        from src.population.population_sampler import initialize_population

        leute = initialize_population(properties, config, seed=42)
        ohne = BookingModelConfig(
            **{
                **properties.booking_model.model_dump(),
                "verfuegbarkeit_gewicht": {
                    "wert": 0.0,
                    "quelle": properties.booking_model.verfuegbarkeit_gewicht.quelle,
                },
            }
        )

        for person in leute[:200]:
            mit = booking_probability(
                person,
                ticket_price=140.0,
                carbon_tax=50.0,
                koeffizienten=properties.booking_model,
                verfuegbarkeit=1.0,
            )
            neutral = booking_probability(
                person,
                ticket_price=140.0,
                carbon_tax=50.0,
                koeffizienten=ohne,
                verfuegbarkeit=1.0,
            )
            assert mit == neutral

    def test_ohne_sitze_fliegt_niemand(self):
        """Der Rand des Wertebereichs — und zugleich der Grund, warum kein
        Epsilon im Logarithmus steht."""

        from src.population.population_sampler import booking_probability

        properties = load_properties_config()
        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config

        from src.population.population_sampler import initialize_population

        person = initialize_population(properties, config, seed=42)[0]

        assert (
            booking_probability(
                person,
                ticket_price=1.0,
                carbon_tax=0.0,
                koeffizienten=properties.booking_model,
                verfuegbarkeit=0.0,
            )
            == 0.0
        )
