"""P3.8 — ein Tick ist ein Monat, und jeder Mechanismus rechnet damit.

**Diese Datei löst `test_tickdauer_ist_uneinheitlich.py` ab** (gelöscht am
2026-09-07). Deren tragende Zusage lautete: «die Zeitskalen widersprechen sich
noch». Sie war ein Ist-Stand-Wächter und hat getan, wozu er gebaut war — er ist
rot geworden, als jemand die Skalen anglich. Was hier steht, ist die
Gegenrichtung: **sie stimmen überein, und zwar auf den Monat.**

**Die Entscheidung** (2026-09-07, Weg 1 der drei aus [P3.8](../docs/projektplan.md)):
Ein Tick ist ein Monat. Sie folgt der Mehrheit der Mechanismen — Sättigung und
Backtest sagten das schon, `fuel_price_change` ebenfalls —, und sie ist die
einzige, die den Backtest nicht neu abbilden muss.

**Was daran gemessen wird und was nicht.** Diese Datei prüft die *Raten*: alles,
was sich **je Tick** verändert, unterstellt eine Zeitskala und muss auf
dieselbe rechnen. Sie prüft **nicht** die Tick-Zahlen in
`configs/sweeps/*.json` — wann in einem Rahmenszenario die CO₂-Abgabe springt,
ist eine Erzählung über die Welt und keine Rate. Dass diese Erzählungen unter
der Monatslesart eine sehr kurze Kalenderspanne ergeben, ist eine offene
Produktfrage und steht als eigenes Paket im Plan.

**Invariante 5 bleibt gültig, und zwar unverändert:** In Configs, Checkpoints
und Ausgaben steht weiterhin kein Datum. Was sich geändert hat, ist nicht die
Regel für Datenformate, sondern die Antwort auf die Frage, welche Zeitskala die
Mechanik unterstellt. Sie war dreimal beantwortet, um den Faktor 12 verschieden;
jetzt einmal.

**Warum das keine Formalie ist** (gemessen am 2026-08-31): Läse man einen Tick
als Jahr und ließe die Kohorte mitaltern, fiele die Buchungsrate über einen
40-Tick-Lauf um **47,6 %** — mehr als jeder andere Effekt im Modell.

**Und warum die Wächter hier rechnen statt zu lesen:** Der Befund, der P3.8
aufgelöst hat, war ein Feld, das sich **selbst widersprach** —
`demand_growth_rate` trug `unit: "fraction_per_tick"` und daneben die
Beschreibung «Jaehrliche Wachstumsrate». Ein Wächter, der Beschreibungen nach
dem Wort «jährlich» durchsucht, schlägt an den Erklärtexten an, die genau diesen
Fall schildern — dieselbe Falle wie in P3.3, wo drei von drei Zusagen an der
eigenen Prosa hängen blieben. Geprüft wird deshalb der **Zahlenwert**: Eine Rate
je Tick, zwölfmal aufgezinst, muss eine plausible Jahresrate ergeben.
"""

from __future__ import annotations

import pytest

from src.backtest.reihen import tick_je_monat
from src.config_loader import load_properties_config
from src.models.property_models import StepFunctionTrajectory

#: Ein Tick ist ein Monat — die Entscheidung von P3.8, als Zahl.
MONATE_JE_JAHR = 12

#: Länge eines Standardlaufs (`configs/simulation_config.json`).
STANDARDLAUF_TICKS = 40

#: Länge des Backtest-Fensters, 2015-01 bis 2024-12.
BACKTEST_TICKS = 120

#: Was für die europäische Bevölkerung plausibel ist, jährlich. Eurostat weist
#: für die EU-27 seit Jahren Werte um 0,1 bis 0,3 % aus; alles über einem
#: Prozent wäre kein Bevölkerungswachstum, sondern Zuwanderung im Krisenmaßstab.
#: Die untere Grenze ist der **Zweck** dieser Spanne: Eine Kurve, die als Jahre
#: gelesen nahezu stillsteht, wäre als Jahreskurve nicht gemeint gewesen.
BEVOELKERUNG_BAND_PA = (0.0005, 0.010)

#: Obergrenze für eine **ausgelieferte** Rate je Tick, aufs Jahr gerechnet.
#: Bewusst weit: Sie soll keine Modellwahl treffen, sondern eine
#: Größenordnungsverwechslung fangen. Der Wert, der P3.8 ausgelöst hat, lag mit
#: 42,58 % p.a. darüber; die beiden heutigen liegen mit 3,04 % und 6,17 % weit
#: darunter. Für die Stresstests in `configs/sweeps/` gilt sie nicht — deren
#: Verläufe sind auf Sichtbarkeit gebaut und nicht auf Plausibilität.
RATE_OBERGRENZE_PA = 0.25


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


def _jahresrate(je_tick: float) -> float:
    """Eine Rate je Tick, über ein Jahr aufgezinst — so, wie das Modell rechnet."""

    return (1.0 + je_tick) ** MONATE_JE_JAHR - 1.0


def _raten_je_tick(properties) -> dict[str, float]:
    """Jede ausgelieferte Systemgröße, deren Einheit «je Tick» sagt."""

    raten = {}
    for prop in properties.system_properties:
        if not prop.unit.endswith("_per_tick"):
            continue
        if isinstance(prop.trajectory, StepFunctionTrajectory):
            continue
        raten[prop.id] = prop.trajectory.baseline
    return raten


def _bevoelkerungskurve(properties):
    punkte = sorted(
        properties.get_system_property("bevoelkerungsentwicklung").trajectory.points,
        key=lambda punkt: punkt.tick,
    )
    ticks = punkte[-1].tick - punkte[0].tick
    wachstum = punkte[-1].value / punkte[0].value - 1.0
    return ticks, wachstum


class TestJedeRateJeTickIstAlsMonatsratePlausibel:
    """**Der Wächter, der P3.8 gefunden hätte.**

    Er zählt die Stellen nicht auf, sondern sucht sie: jede Systemgröße, deren
    Einheit auf ``_per_tick`` endet. Eine handgepflegte Liste hätte
    ``demand_growth_rate`` genau so lange übersehen, wie es niemand aufschrieb.
    """

    def test_es_gibt_ueberhaupt_welche(self, properties):
        """Sonst misst der Wächter unten nichts und ist trotzdem grün."""

        raten = _raten_je_tick(properties)

        assert set(raten) >= {"demand_growth_rate", "fuel_price_change", "erneuerungsrate"}, (
            f"Gefundene Raten je Tick: {sorted(raten)}. Fehlt eine bekannte, hat sich "
            "ihre Einheit geändert — dann prüft dieser Wächter sie nicht mehr mit."
        )

    def test_keine_von_ihnen_ist_in_wahrheit_eine_jahresrate(self, properties):
        """Zwölfmal aufgezinst muss eine Monatsrate eine Jahresrate ergeben.

        Genau daran ist ``demand_growth_rate`` gescheitert: 0,03 je Tick sind
        **42,58 %** im Jahr und über die 120 Ticks des Backtests der Faktor
        34,7. Als Jahresrate gelesen waren dieselben 0,03 unauffällig — und
        genau das stand in der Beschreibung.
        """

        for name, je_tick in _raten_je_tick(properties).items():
            jahresrate = _jahresrate(je_tick)

            assert abs(jahresrate) <= RATE_OBERGRENZE_PA, (
                f"{name} = {je_tick} je Tick sind {jahresrate:.2%} im Jahr. Das ist "
                "keine Monatsrate, sondern sehr wahrscheinlich eine Jahresrate an "
                "der Stelle einer Tickrate — der Befund, der P3.8 ausgelöst hat."
            )

    def test_der_waechter_wuerde_den_alten_wert_melden(self):
        """Die Gegenprobe: Ohne sie wäre grün nur die Abwesenheit einer Messung."""

        assert _jahresrate(0.03) > RATE_OBERGRENZE_PA
        assert _jahresrate(0.03) == pytest.approx(0.4258, abs=5e-4)


class TestDieBevoelkerungskurveRechnetInMonaten:
    """Der eine Mechanismus, der vor P3.8 Jahre unterstellte."""

    def test_ihre_jahresrate_liegt_im_europaeischen_band(self, properties):
        ticks, wachstum = _bevoelkerungskurve(properties)
        jahre = ticks / MONATE_JE_JAHR
        pro_jahr = (1.0 + wachstum) ** (1.0 / jahre) - 1.0

        unten, oben = BEVOELKERUNG_BAND_PA
        assert unten < pro_jahr < oben, (
            f"Als Monate gelesen wächst die Kurve um {pro_jahr:.3%} p.a. — außerhalb "
            f"des Bandes {unten:.2%} bis {oben:.2%}, das für die EU-27 plausibel ist."
        )

    def test_als_jahre_gelesen_waere_sie_jetzt_unplausibel(self, properties):
        """**Die Zusage, die den Unterschied zum Ist-Stand von vorher macht.**

        Vorher war die Kurve als Jahre plausibel und als Monate unmöglich. Jetzt
        ist es umgekehrt — nicht bloß «auch als Monate lesbar». Ohne diese
        Richtung wäre der Wächter mit einer Kurve zufrieden, die beides zulässt,
        und dann sagt er nichts.
        """

        ticks, wachstum = _bevoelkerungskurve(properties)
        pro_jahr_als_jahre = (1.0 + wachstum) ** (1.0 / ticks) - 1.0

        assert pro_jahr_als_jahre < BEVOELKERUNG_BAND_PA[0], (
            f"Als Jahre gelesen wären es {pro_jahr_als_jahre:.4%} p.a. — das ist "
            "wieder plausibel, also unterstellt die Kurve nicht mehr eindeutig Monate."
        )

    def test_die_jahresrate_ist_die_von_vorher(self, properties):
        """**P3.8 hat die Einheit geändert, nicht die Aussage über die Welt.**

        Die alte Kurve behauptete als Jahre gelesen 0,2657 % p.a. Genau diese
        Zahl trägt die neue — sonst wäre unter dem Deckmantel einer
        Einheitenkorrektur eine Neuschätzung eingezogen, und der Backtest hätte
        anschließend eine Größe geprüft, die auf ihn hin gesetzt wurde.
        """

        ticks, wachstum = _bevoelkerungskurve(properties)
        pro_jahr = (1.0 + wachstum) ** (MONATE_JE_JAHR / ticks) - 1.0
        vor_p38 = (1080 / 1000) ** (1 / 29) - 1.0

        assert pro_jahr == pytest.approx(vor_p38, abs=5e-4), (
            f"Neu {pro_jahr:.4%} p.a. gegen {vor_p38:.4%} p.a. vor P3.8. Weicht das "
            "ab, ist die Rate neu gesetzt worden — das ist erlaubt, gehört aber "
            "begründet und nicht in eine Einheitenkorrektur."
        )

    def test_sie_deckt_das_fenster_des_backtests(self, properties):
        """Der zweite Befund aus P2.8, mit erledigt.

        Vorher endete die Kurve bei Tick 30, und der Backtest rechnete **90 von
        120** Ticks mit eingefrorener Bevölkerung. Als Jahre gelesen war das
        eine sinnvolle Kurve an der falschen Skala; als Monate ist ein Horizont
        von zehn Jahren das Mindeste.
        """

        punkte = properties.get_system_property("bevoelkerungsentwicklung").trajectory.points
        letzter = max(punkt.tick for punkt in punkte)

        assert letzter >= BACKTEST_TICKS, (
            f"Letzter Stützpunkt bei Tick {letzter}, der Backtest läuft "
            f"{BACKTEST_TICKS}. Dann friert die Bevölkerung wieder mitten im "
            "Vergleichsfenster ein, ohne dass es jemand sieht."
        )

    def test_sie_bewegt_sich_innerhalb_eines_standardlaufs(self, properties):
        """Ein Horizont ist nicht dasselbe wie eine Wirkung.

        Zehn Stützpunkte am Ende des Laufs wären ein gedeckter Horizont und
        trotzdem eine im Standardlauf konstante Bevölkerung. Die Kurve trägt
        deshalb **Jahresstufen** — die Quelle ist jährlich erhoben, das Raster
        also nicht feiner zu machen, aber innerhalb von 40 Ticks liegen drei.
        """

        from src.market.property_engine import resolve_property

        am_anfang = resolve_property("bevoelkerungsentwicklung", 1, properties)
        am_ende = resolve_property("bevoelkerungsentwicklung", STANDARDLAUF_TICKS, properties)

        assert am_ende > am_anfang, (
            f"Über {STANDARDLAUF_TICKS} Ticks bewegt sich die Bevölkerung nicht "
            f"({am_anfang} → {am_ende}) — die Stützpunkte liegen zu weit auseinander."
        )


class TestDieSaettigungRechnetInMonaten:
    """Unverändert seit dem Ist-Stand-Wächter — sie sagte schon Monate."""

    def test_eine_reise_ist_nach_wenigen_ticks_vergessen(self, properties):
        """Die Grenze ist **einschließend**, und das ist kein Schludern.

        `eco_conscious` liegt bei genau zwölf Ticks — als Monate gelesen eine
        Reise im Jahr, völlig plausibel; als Jahre gelesen zwölf Jahre zwischen
        zwei Flügen. Die Zusage trennt also weiterhin. Ein `<` hätte hier nur
        deshalb gehalten, weil ``0.6 / 0.05`` in Fließkomma
        **11,999999999999998** ergibt — ein Wächter, der an einer
        Rundungsstelle hängt, sagt beim nächsten Wert etwas anderes als beim
        letzten.
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
            assert ticks <= MONATE_JE_JAHR, (
                f"{segment}: {ticks:.1f} Ticks zwischen zwei Reisen. Über einem Jahr "
                "wäre die Monatslesart nicht mehr die naheliegende."
            )

    def test_als_jahre_gelesen_waere_der_reiseabstand_absurd(self, properties):
        """Die Kehrseite — sie macht die Monatslesart eindeutig."""

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


class TestDerBacktestBildetEinenTickAufEinenMonatAb:
    def test_zwoelf_ticks_sind_ein_jahr(self):
        """**Die Stelle, die es immer schon aussprach** — und sie sagt «Monat».

        `reihen.tick_je_monat` lebt bewusst nur im Backtest (CLAUDE.md), damit
        kein Datum in Config oder Ausgabe gelangt. Seit P3.8 ist sie nicht mehr
        die einzige Stelle mit einer Meinung, sondern die, an der sich die
        anderen ausgerichtet haben.
        """

        zuordnung = tick_je_monat()

        assert len(zuordnung) == BACKTEST_TICKS
        assert zuordnung["2015-01"] == 1 and zuordnung["2015-02"] == 2
        assert zuordnung["2016-01"] == 1 + MONATE_JE_JAHR


def test_alle_mechanismen_nennen_dieselbe_zeitskala(properties):
    """**Die tragende Zusage dieser Datei.**

    Sie ist die Umkehrung von
    `test_tickdauer_ist_uneinheitlich.test_die_drei_lesarten_widersprechen_sich_noch`:
    Wird sie rot, hat jemand eine Zeitskala wieder auseinanderlaufen lassen.

    Geprüft werden alle vier Mechanismen zusammen und nicht einzeln — der
    Fallstrick aus P3.8 lautet: *Wer nur eine Stelle anfasst, verschiebt den
    Widerspruch, statt ihn aufzulösen.*
    """

    ticks, wachstum = _bevoelkerungskurve(properties)
    bevoelkerung_pa = (1.0 + wachstum) ** (MONATE_JE_JAHR / ticks) - 1.0

    anstieg = properties.saturation.booking_increase
    familie = next(
        prop.saturation_decay for prop in properties.individual_properties if prop.id == "family"
    )
    reiseabstand_ticks = anstieg / familie

    raten = _raten_je_tick(properties)
    schlimmste_rate = max((abs(_jahresrate(wert)) for wert in raten.values()), default=0.0)

    sagt_monate = {
        "Bevölkerungskurve": BEVOELKERUNG_BAND_PA[0] < bevoelkerung_pa < BEVOELKERUNG_BAND_PA[1],
        "Sättigung": reiseabstand_ticks <= MONATE_JE_JAHR,
        "Raten je Tick": schlimmste_rate <= RATE_OBERGRENZE_PA,
        "Backtest": tick_je_monat()["2016-01"] == 1 + MONATE_JE_JAHR,
    }

    assert all(sagt_monate.values()), (
        "Nicht jeder Mechanismus rechnet in Monaten — P3.8 ist damit wieder offen.\n"
        + "\n".join(
            f"  {name}: {'Monate' if ok else 'NICHT Monate'}" for name, ok in sagt_monate.items()
        )
        + f"\n  Bevölkerung {bevoelkerung_pa:.3%} p.a., Reiseabstand "
        f"{reiseabstand_ticks:.1f} Ticks, größte Rate {schlimmste_rate:.2%} p.a."
    )
