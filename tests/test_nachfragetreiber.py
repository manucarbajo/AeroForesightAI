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
