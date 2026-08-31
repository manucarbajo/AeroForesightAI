"""Der Befund aus P2.7: Dem Modell fehlt jeder Nachfragetreiber nach oben.

Diese Datei hält **nicht** eine Zusage, sondern einen **Ist-Stand** — dasselbe
Muster wie `test_faktoren_abgeleitet.py` und `test_cib_einachsigkeit.py`. Sie
misst zwei Größen, die der Backtest ans Licht gebracht hat, und schlägt an, wenn
sich eine davon bewegt.

**Ein rotes Ergebnis ist hier keine Panne**, sondern die Nachricht, dass jemand
die Nachfrageseite angefasst hat. Dann gehört der Befund im Projektplan neu
geschrieben und der Backtest neu gerechnet — in dieser Reihenfolge, nicht
umgekehrt: Eine Mechanik, die *auf* den Backtest hin gebaut wird, kann er danach
nicht mehr prüfen.
"""

from __future__ import annotations

import pytest

from src.config_loader import load_properties_config
from src.market.property_engine import resolve_property

#: Was ein Standardlauf braucht. Er ist heute länger als die einzige
#: Trajektorie des Modells reicht — genau das ist der Befund.
STANDARDLAUF_TICKS = 40
BACKTEST_TICKS = 120


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


@pytest.fixture(scope="module")
def leute(properties):
    """Die Stichprobe, gegen die die Elastizität gemessen wird.

    Auf Modulebene und nicht in der Klasse: Eine klassenweite Fixture als
    Instanzmethode ist seit pytest 8 verwarnt, und eine Verwarnung, die stehen
    bleibt, verdeckt die nächste.
    """

    from src.config_loader import build_initial_state
    from src.population.population_sampler import initialize_population

    zustand = build_initial_state()
    config = next(
        agent for agent in zustand.agents if getattr(agent, "population_config", None)
    ).population_config
    return initialize_population(properties, config, seed=42)


class TestDieBevoelkerungskurveEndetVorDemLauf:
    """Befund 1 — der Horizont der Trajektorie hängt an nichts."""

    def test_es_gibt_genau_eine_trajektorie_im_modell(self, properties):
        """Wächst diese Zahl, ist der Befund unvollständig: Dann hat eine
        zweite Systemgröße einen Verlauf, und ihr Horizont ist ebenso zu prüfen.
        """

        mit_verlauf = [
            prop.id
            for prop in properties.system_properties
            if getattr(prop, "trajectory", None) is not None
            and getattr(prop.trajectory, "points", None)
        ]

        assert mit_verlauf == ["bevoelkerungsentwicklung"], (
            f"Trajektorien im Modell: {mit_verlauf}. Der Befund in P2.7 nennt eine — "
            "wer eine zweite anlegt, prüft ihren Horizont mit."
        )

    def test_der_letzte_stuetzpunkt_liegt_vor_dem_ende_eines_standardlaufs(self, properties):
        prop = properties.get_system_property("bevoelkerungsentwicklung")
        letzter = max(punkt.tick for punkt in prop.trajectory.points)

        assert letzter == 30, f"Letzter Stützpunkt bei Tick {letzter}, erwartet 30"
        assert letzter < STANDARDLAUF_TICKS, (
            "Die Kurve reicht jetzt über einen Standardlauf hinaus — schöne "
            "Nachricht, aber der Befund in P2.7 stimmt dann nicht mehr."
        )

    def test_jenseits_des_horizonts_haelt_sie_still_ihren_letzten_wert(self, properties):
        """Für eine Stufenfunktion korrekt — und genau deshalb unsichtbar.

        Nichts im Lauf sagt, dass die Vorgabe aufgebraucht ist. Der Backtest
        verbringt so **90 von 120 Ticks** mit eingefrorener Bevölkerung.
        """

        bei_30 = resolve_property("bevoelkerungsentwicklung", 30, properties)
        bei_120 = resolve_property("bevoelkerungsentwicklung", BACKTEST_TICKS, properties)

        assert bei_30 == bei_120 == 1080.0
        assert BACKTEST_TICKS - 30 == 90


class TestDerZuwachsReichteAuchUngekuerztNicht:
    """Befund 2 — die Größenordnung stimmt unabhängig vom Horizont nicht."""

    def test_die_kurve_waechst_um_acht_prozent_der_reale_verkehr_um_sechsundzwanzig(
        self, properties
    ):
        """Die Zahlen des Backtests, nebeneinander.

        Real: Eurostat `avia_paoc`, EU27, Jahresmittel 2015 → 2019, Index
        100 → 126,28. Modell: die einzige Größe, über die die Nachfragemenge
        wachsen könnte.
        """

        punkte = sorted(
            properties.get_system_property("bevoelkerungsentwicklung").trajectory.points,
            key=lambda punkt: punkt.tick,
        )
        zuwachs_modell = punkte[-1].value / punkte[0].value - 1.0
        zuwachs_real = 126.28 / 100.0 - 1.0

        assert zuwachs_modell == pytest.approx(0.08), (
            f"Die Kurve wächst um {zuwachs_modell:.1%} statt 8 % — der Befund in "
            "P2.7 nennt diese Zahl."
        )
        assert zuwachs_modell < zuwachs_real / 3, (
            f"Modell +{zuwachs_modell:.1%} gegen real +{zuwachs_real:.1%}. Nähert "
            "sich das an, ist die Nachfrageseite in Bewegung — Backtest neu rechnen."
        )


class TestDiePreiselastizitaetIstDieEineStellschraube:
    """**Die Diagnose, die den Befund von «es fehlt etwas» zu «es ist eines» macht.**

    Gemessen am 2026-08-31: Rund **85 %** des Nachfrageeinbruchs im Backtest
    sind allein der Preiskanal, der auf den selbst erzeugten Preisanstieg wirkt.
    Das Modell hat nicht zu wenige Nachfragekanäle — es hat praktisch **genau
    einen**, und der läuft unopponiert.

    Maßstab ist die Metaanalyse, die im Repo liegt: **Brons, Pels, Nijkamp &
    Rietveld (2002)**, *Journal of Air Transport Management* 8, 165–175 —
    204 Schätzungen aus 37 Studien, Mittelwert **−1,146**, Standardabweichung
    **0,619**, niedrigster Einzelwert **−3,20**.
    """

    #: Brons et al. (2002), Tabelle im Abschnitt «Descriptive statistical results».
    METAANALYSE_MITTEL = -1.146
    METAANALYSE_SD = 0.619
    METAANALYSE_NIEDRIGSTER = -3.20

    @staticmethod
    def _rate(leute, properties, preis: float) -> float:
        from statistics import mean

        from src.population.population_sampler import booking_probability

        return mean(
            booking_probability(
                person,
                ticket_price=preis,
                carbon_tax=50.0,
                koeffizienten=properties.booking_model,
            )
            for person in leute
        )

    @classmethod
    def _elastizitaet(cls, leute, properties, a: float, b: float) -> float:
        """Bogenelastizität nach der Mittelpunktsformel."""

        qa, qb = cls._rate(leute, properties, a), cls._rate(leute, properties, b)
        return ((qb - qa) / ((qa + qb) / 2)) / ((b - a) / ((a + b) / 2))

    def test_am_betriebspunkt_liegt_sie_auf_der_elastischen_seite(self, leute, properties):
        """−1,83 gegen ein Metaanalyse-Mittel von −1,146: rund 1,1
        Standardabweichungen steiler, aber innerhalb der Verteilung."""

        e = self._elastizitaet(leute, properties, 130.0, 145.0)

        assert e == pytest.approx(-1.83, abs=0.15), f"Elastizität am Betriebspunkt: {e:.2f}"

        abstand = (abs(e) - abs(self.METAANALYSE_MITTEL)) / self.METAANALYSE_SD
        assert 0.7 < abstand < 1.5, (
            f"{abstand:.1f} Standardabweichungen vom Metaanalyse-Mittel. Bewegt sich "
            "das, gehört der Befund in P2.8 neu geschrieben."
        )

    def test_sie_ist_nicht_konstant_sondern_versechsfacht_sich(self, leute, properties):
        """**Der schwerere der beiden Befunde.**

        Eine Elastizität, die über eine plausible Preisspanne von −0,58 auf
        −3,54 läuft, ist eine Eigenschaft der Sigmoid mit harter
        Erschwinglichkeitsschwelle — keine Modellierungsentscheidung, die
        jemand getroffen hätte. Am oberen Ende ist sie steiler als der
        **niedrigste** aller 204 Schätzwerte der Metaanalyse.
        """

        flach = self._elastizitaet(leute, properties, 80.0, 100.0)
        steil = self._elastizitaet(leute, properties, 200.0, 250.0)

        assert abs(steil) > 5 * abs(flach), (
            f"Spanne {flach:.2f} bis {steil:.2f} — die Elastizität ist "
            "gleichmäßiger geworden. Gute Nachricht, aber P2.8 stimmt dann nicht mehr."
        )
        assert steil < self.METAANALYSE_NIEDRIGSTER, (
            f"{steil:.2f} liegt nicht mehr jenseits des niedrigsten Schätzwerts "
            f"({self.METAANALYSE_NIEDRIGSTER}) der Metaanalyse."
        )

    def test_der_preiskanal_erklaert_den_einbruch_fast_allein(self, leute, properties):
        """Die Rechnung, die P2.8 trägt.

        Stand nach P2.8, also **mit** gespeistem Einkommen: Modellpreis
        2015→2019 133,16 → 142,48 (+7,0 %), Buchungsrate 0,3500 → 0,3060
        (−12,6 %). Bei der gemessenen Elastizität erwartet man aus dem Preis
        allein rund −12,8 %.

        Dass beides so nah beieinanderliegt, **obwohl** der Einkommenskanal
        inzwischen +3,0 Punkte beisteuert, ist der Befund von P2.8: Der Beitrag
        wird von den Ausgleichsmechanismen des Modells (Preisrückkopplung,
        Sättigung) fast vollständig aufgezehrt.
        """

        e = self._elastizitaet(leute, properties, 130.0, 145.0)
        preisanstieg = (142.48 - 133.16) / 133.16
        erwartet = e * preisanstieg
        gemessen = (0.3060 - 0.3500) / 0.3500

        anteil = erwartet / gemessen
        assert 0.7 < anteil < 1.1, (
            f"Der Preiskanal erklärt {anteil:.0%} des Einbruchs (erwartet "
            f"{erwartet:.1%}, gemessen {gemessen:.1%}). Weicht das ab, hat sich "
            "entweder die Elastizität bewegt oder ein zweiter Kanal ist dazugekommen."
        )
