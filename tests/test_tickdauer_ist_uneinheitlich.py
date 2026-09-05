"""P3.8 — was ein Tick bedeutet, ist dreimal verschieden entschieden.

**[Invariante 5](../CLAUDE.md) sagt: «Ein Tick ist ein Tick» — keine
Kalendersemantik in Configs, Checkpoints oder Ausgaben.** Das ist als *Regel für
Datenformate* eingehalten: Nirgends steht ein Datum. Als Aussage über das
**Modellverhalten** hält sie nicht.

Denn eine Zeitskala verschwindet nicht dadurch, dass man sie nicht aufschreibt.
Jeder Mechanismus, der pro Tick etwas verändert, unterstellt eine — und im
Modell unterstellen drei davon **drei verschiedene**, um den Faktor 12
auseinander:

| Mechanismus | plausibel, wenn ein Tick … |
| --- | --- |
| `bevoelkerungsentwicklung`, +8 % über 29 Ticks | ein **Jahr** ist (+0,27 % p.a.) |
| Sättigung, eine Reise nach ~3 Ticks «vergessen» | ein **Monat** ist |
| Backtest (`reihen.tick_je_monat`) | ein **Monat** ist, ausdrücklich |

**Diese Datei entscheidet nichts.** Sie misst den Ist-Stand und hält ihn fest,
damit der Widerspruch bei der nächsten Änderung sichtbar ist statt unbemerkt
mitzuwandern — dasselbe Muster wie `test_faktoren_abgeleitet.py` und
`test_nachfragetreiber.py`.

**Ein rotes Ergebnis ist hier eine gute Nachricht:** Es heißt, dass jemand die
Zeitskalen angeglichen hat. Dann gehört P3.8 geschlossen und diese Datei
entfernt.

**Warum es zählt** (gemessen am 2026-08-31): Läse man einen Tick als Jahr und
ließe die Kohorte mitaltern, fiele die Buchungsrate über einen 40-Tick-Lauf um
**47,6 %** — mehr als jeder andere Effekt im Modell. Die Frage «wie lang ist ein
Tick» ist also keine Formalie.
"""

from __future__ import annotations

import pytest

from src.backtest.reihen import tick_je_monat
from src.config_loader import load_properties_config

#: Wie viele Ticks ein Jahr hätte, je Lesart.
LESARTEN = {"Monate": 12, "Quartale": 4, "Jahre": 1}

#: Was für die europäische Bevölkerung plausibel ist, jährlich. Eurostat weist
#: für die EU-27 seit Jahren Werte um 0,1 bis 0,3 % aus; alles über einem
#: Prozent wäre kein Bevölkerungswachstum, sondern Zuwanderung im Krisenmaßstab.
BEVOELKERUNG_PLAUSIBEL_PA = 0.010


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


def _bevoelkerungskurve(properties):
    punkte = sorted(
        properties.get_system_property("bevoelkerungsentwicklung").trajectory.points,
        key=lambda punkt: punkt.tick,
    )
    ticks = punkte[-1].tick - punkte[0].tick
    wachstum = punkte[-1].value / punkte[0].value - 1.0
    return ticks, wachstum


class TestDieBevoelkerungskurveUnterstelltJahre:
    def test_als_monate_gelesen_waere_sie_unplausibel(self, properties):
        """+8 % über 29 Ticks sind als Monate +3,24 % im Jahr.

        Das gibt es in Europa nirgends — die Kurve kann so nicht gemeint sein.
        """

        ticks, wachstum = _bevoelkerungskurve(properties)
        jahre = ticks / LESARTEN["Monate"]
        pro_jahr = (1.0 + wachstum) ** (1.0 / jahre) - 1.0

        assert pro_jahr > BEVOELKERUNG_PLAUSIBEL_PA, (
            f"Als Monate gelesen wären es {pro_jahr:.2%} p.a. — das ist jetzt "
            "plausibel, also wurde die Kurve angepasst. P3.8 neu prüfen."
        )

    def test_als_jahre_gelesen_ist_sie_plausibel(self, properties):
        ticks, wachstum = _bevoelkerungskurve(properties)
        jahre = ticks / LESARTEN["Jahre"]
        pro_jahr = (1.0 + wachstum) ** (1.0 / jahre) - 1.0

        assert (
            0.0 < pro_jahr < BEVOELKERUNG_PLAUSIBEL_PA
        ), f"Als Jahre gelesen: {pro_jahr:.2%} p.a. — nicht mehr im plausiblen Band."


class TestDieSaettigungUnterstelltMonate:
    def test_eine_reise_ist_nach_wenigen_ticks_vergessen(self, properties):
        """Eine Buchung hebt die Sättigung, sie fällt je Tick um einen festen Wert.

        Der Abstand zwischen zwei Reisen ist damit **in Ticks** festgelegt — und
        als Jahre gelesen ergäbe er für jedes Segment einen absurden Wert.
        """

        anstieg = properties.saturation.booking_increase
        abbau = {
            prop.id: prop.saturation_decay
            for prop in properties.individual_properties
            if prop.saturation_decay
        }

        assert abbau, "Kein Segment hat einen Sättigungsabbau — der Test misst nichts"

        for segment, rate in abbau.items():
            ticks = anstieg / rate
            assert ticks < 12, (
                f"{segment}: {ticks:.1f} Ticks zwischen zwei Reisen. Über einem Jahr "
                "wäre die Monatslesart nicht mehr die naheliegende."
            )

    def test_als_jahre_gelesen_waere_der_reiseabstand_absurd(self, properties):
        """Die Kehrseite — sie macht den Widerspruch zur Bevölkerungskurve aus."""

        anstieg = properties.saturation.booking_increase
        familie = next(
            prop.saturation_decay
            for prop in properties.individual_properties
            if prop.id == "family"
        )
        ticks = anstieg / familie

        assert ticks >= 2.0, (
            f"Familien reisen alle {ticks:.1f} Ticks. Als Jahre gelesen wären das "
            f"{ticks:.0f} Jahre zwischen zwei Flügen."
        )


class TestDerBacktestLegtSichFest:
    def test_er_bildet_einen_tick_auf_einen_monat_ab(self):
        """**Die einzige Stelle, die es ausspricht** — und sie sagt «Monat».

        `reihen.tick_je_monat` lebt bewusst nur im Backtest (CLAUDE.md), damit
        kein Datum in Config oder Ausgabe gelangt. Die *Annahme* wandert damit
        aber nicht weg, sie steht nur woanders.
        """

        zuordnung = tick_je_monat()

        assert len(zuordnung) == 120
        assert zuordnung["2015-01"] == 1 and zuordnung["2015-02"] == 2
        assert zuordnung["2016-01"] == 13, "Zwölf Ticks je Jahr — also Monate"


def test_die_drei_lesarten_widersprechen_sich_noch(properties):
    """**Die tragende Zusage dieser Datei.**

    Solange Bevölkerungskurve und Sättigung verschiedene Zeitskalen
    unterstellen, ist die Frage offen. Wird dieser Test rot, sind sie
    angeglichen — dann gehört P3.8 geschlossen.
    """

    ticks, wachstum = _bevoelkerungskurve(properties)
    bevoelkerung_als_jahre = (1.0 + wachstum) ** (LESARTEN["Jahre"] / ticks) - 1.0

    anstieg = properties.saturation.booking_increase
    familie = next(
        prop.saturation_decay for prop in properties.individual_properties if prop.id == "family"
    )
    reiseabstand_ticks = anstieg / familie

    bevoelkerung_meint_jahre = bevoelkerung_als_jahre < BEVOELKERUNG_PLAUSIBEL_PA
    saettigung_meint_monate = reiseabstand_ticks < 12

    assert bevoelkerung_meint_jahre and saettigung_meint_monate, (
        "Die Zeitskalen stimmen überein — gute Nachricht. P3.8 gehört dann "
        "geschlossen und diese Datei entfernt.\n"
        f"  Bevölkerung als Jahre: {bevoelkerung_als_jahre:.2%} p.a.\n"
        f"  Reiseabstand: {reiseabstand_ticks:.1f} Ticks"
    )
