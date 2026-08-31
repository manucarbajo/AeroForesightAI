"""P2.4 — die Bevölkerung altert nicht, und das ist entschieden (2026-08-31).

**Die Entscheidung, die diese Datei trägt:** Die simulierte Bevölkerung ist eine
**wiederholte Querschnittserhebung**, keine Kohorte. Jeder Tick zeigt «die
Bevölkerung, wie sie ist» — nicht dieselben Personen, die älter werden. Ein
Alterungspfad wird **nicht** gebaut.

Zwei Gründe, beide gemessen und nicht gefühlt:

1. **`age` ist für das Verhalten inert.** Alle Personen um zwanzig Jahre zu
   altern verändert die mittlere Buchungswahrscheinlichkeit um **exakt null**.
   `booking_probability` kennt WTP, Einkommen, Umweltbewusstsein,
   Preissensitivität, Substitutionsbereitschaft und Sättigung — kein Alter. Auch
   die Shift-Regeln erreichen es nicht: Sie ändern genau drei Attribute.
2. **Alterung hieße Kalenderzeit.** Eine Rate «Jahre je Tick» ist genau die
   Semantik, die [Invariante 5](../CLAUDE.md) ausschließt. Man müsste sie
   einführen, um eine Statistik zu bewegen, die in keine Rechnung eingeht.

**Was diese Tests deshalb halten, ist die Voraussetzung der Entscheidung, nicht
ihr Ergebnis:** Sobald `age` anfängt, Verhalten zu beeinflussen, fällt Grund 1
weg — und dann gehört die Entscheidung neu auf den Tisch, statt stillschweigend
weiterzugelten. **Ein rotes Ergebnis ist hier keine Panne, sondern genau diese
Nachricht.**

Dasselbe Muster wie `test_faktoren_abgeleitet.py` und
`test_nachfragetreiber.py`: Sie messen einen Ist-Stand, auf dem eine
Entscheidung ruht.
"""

from __future__ import annotations

from statistics import mean

import pytest

from src.config_loader import build_initial_state, load_properties_config
from src.models.property_models import ShiftRule

#: **Aus dem Quellmodul, nicht als Kopie hier** — sonst prüfte der Test seine
#: eigene Liste. Wächst sie um `age`, ist die Entscheidung neu zu treffen.
from src.population.population_sampler import (
    SHIFT_ZIELE,  # noqa: E402
    apply_factor_shifts,
    booking_probability,
    initialize_population,
)


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


@pytest.fixture(scope="module")
def faktoren():
    """Eine Faktorlage, in der die Testregeln greifen.

    Mit einer Bedingung, die nicht zutrifft, liefe jeder Test unten grün,
    ohne je ein Ziel geprüft zu haben.
    """

    zustand = build_initial_state()
    lage = zustand.environment.factors
    lage["F1"] = lage["F1"].model_copy(update={"current_state": "F1.2"})
    return lage


@pytest.fixture(scope="module")
def leute(properties):
    zustand = build_initial_state()
    config = next(
        agent for agent in zustand.agents if getattr(agent, "population_config", None)
    ).population_config
    return initialize_population(properties, config, seed=42)


def _rate(personen, properties, preis: float = 140.0) -> float:
    return mean(
        booking_probability(
            person,
            ticket_price=preis,
            carbon_tax=50.0,
            koeffizienten=properties.booking_model,
        )
        for person in personen
    )


class TestDasAlterIstFuerDasVerhaltenInert:
    """Grund 1 der Entscheidung — der tragende."""

    def test_zwanzig_jahre_aeltern_aendert_die_nachfrage_um_null(self, leute, properties):
        """**Nicht «wenig», sondern exakt null.**

        Deshalb steht hier kein `approx`: Ein Unterschied von 1e-15 wäre schon
        die Nachricht, dass irgendwo doch ein Alterspfad hineinwirkt.
        """

        gealtert = [p.model_copy(update={"age": min(95, p.age + 20)}) for p in leute]

        assert (
            mean(p.age for p in gealtert) > mean(p.age for p in leute) + 10
        ), "Die Alterung ist im Test selbst nicht angekommen — dann prüft er nichts."
        assert _rate(gealtert, properties) == _rate(leute, properties), (
            "Das Alter beeinflusst jetzt die Buchungswahrscheinlichkeit. Damit "
            "fällt der tragende Grund für P2.4 weg: Die Entscheidung gegen einen "
            "Alterungspfad gehört neu auf den Tisch."
        )

    def test_das_buchungsmodell_liest_kein_alter(self, properties):
        """Die Gegenprobe zur Messung — im Quelltext statt am Ergebnis.

        Die Messung oben könnte auch dann null liefern, wenn ein Alterseffekt
        sich gerade zufällig aufhebt.
        """

        import inspect

        quelle = inspect.getsource(booking_probability)
        körper = quelle.split('"""')[-1]

        assert ".age" not in körper, "`booking_probability` liest jetzt das Alter"

    def test_shift_regeln_erreichen_das_alter_nicht(self, leute, faktoren):
        """Der zweite Weg, auf dem sich das Alter bewegen könnte — versperrt.

        **Und seit dem 2026-08-31 laut versperrt.** Bis dahin tat eine Regel auf
        `age` einfach nichts: keine Meldung, kein Fehler, nur eine Regel, die
        nie greift. Wer sie schrieb, hätte geglaubt, die Bevölkerung altere.
        """

        regel = ShiftRule(
            id="altern",
            when={"factor": "F1", "state": "F1.2"},
            effect={"property": "age", "delta": 5.0},
        )

        with pytest.raises(ValueError, match="unbekanntes Ziel"):
            apply_factor_shifts(
                list(leute[:20]), [regel], faktoren, tick=1, metrics={}, system_properties={}
            )

    def test_es_bleiben_genau_drei_erreichbare_attribute(self, leute, faktoren):
        """Die Menge selbst, damit ein vierter Kanal auffällt.

        **Gemessen statt gelesen:** Für jedes Attribut wird eine Regel gebaut
        und ausgeführt. Ein erreichbares Ziel verändert die Person, ein
        unbekanntes wirft. Ein Test gegen `SHIFT_ZIELE` allein prüfte nur, dass
        eine Konstante ihrem eigenen Wert gleicht.
        """

        erreichbar = set()
        for kandidat in (*SHIFT_ZIELE, "age", "wtp_eur", "substitution_readiness"):
            regel = ShiftRule(
                id=kandidat,
                when={"factor": "F1", "state": "F1.2"},
                effect={"property": kandidat, "delta": 0.1},
            )
            try:
                ergebnis = apply_factor_shifts(
                    list(leute[:5]), [regel], faktoren, tick=1, metrics={}, system_properties={}
                )
            except ValueError:
                continue
            if any(
                a.model_dump() != b.model_dump() for a, b in zip(ergebnis, leute[:5], strict=True)
            ):
                erreichbar.add(kandidat)

        assert erreichbar == set(
            SHIFT_ZIELE
        ), f"Erreichbar sind jetzt {sorted(erreichbar)} statt {sorted(SHIFT_ZIELE)}."


class TestDieBevoelkerungIstEinQuerschnittKeineKohorte:
    """Grund 2 — warum das auch ohne Alterungspfad vertretbar ist."""

    def test_wachstum_zieht_neue_personen_aus_derselben_verteilung(self, properties, leute):
        """Deshalb bleibt die **Verteilung** stabil, obwohl niemand altert.

        Ein Lauf, dessen Bevölkerung von 1000 auf 1080 wächst, hängt 80 frisch
        gezogene Personen an. Die Altersstruktur verschiebt sich dadurch um
        Bruchteile eines Prozentpunkts — sie ist nicht «eingefroren», sie ist
        **stationär**, und das ist eine andere Aussage.
        """

        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config
        zuwachs = initialize_population(
            properties, config.model_copy(update={"total_population": 80}), seed=42 + 1000
        )

        vorher = mean(p.age for p in leute)
        nachher = mean(p.age for p in [*leute, *zuwachs])

        assert abs(nachher - vorher) < 2.0, (
            f"Altersmittel verschiebt sich um {nachher - vorher:.1f} Jahre — die "
            "Zuwächse kommen offenbar aus einer anderen Verteilung."
        )


class TestDieAltersstatistikIstNichtBelastbar:
    """**Der Fund, der beim Entscheiden dazukam** — und das zweite Argument.

    Die Altersverteilung ist nicht nur folgenlos, sie ist auch **falsch
    gezogen**: `_sample_lognormal` liest `mean` als Median der Lognormalen, und
    mit `mean: 73, std_dev: 1.0` liegt rund die Hälfte der Masse über der
    Obergrenze 90. Sie wird dorthin geklemmt.

    Eigener Befund, eigenes Paket (P2.9) — hier steht er, weil er begründet,
    warum in eine Alterung dieser Statistik nicht investiert wird: Man würde
    eine kaputte Verteilung sorgfältig altern lassen.
    """

    def test_ein_grosser_teil_liegt_auf_der_oberen_klemme(self, leute):
        an_der_wand = sum(1 for p in leute if p.age == 90) / len(leute)

        assert an_der_wand > 0.2, (
            f"Nur noch {an_der_wand:.1%} auf der Obergrenze — die Verteilung ist "
            "offenbar repariert worden. Dann gehört P2.9 geschlossen und dieser "
            "Test entfernt."
        )
