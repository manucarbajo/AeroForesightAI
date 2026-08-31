"""P2.4 (neu gefasst am 2026-08-31) — das Alter formt die Person.

**Diese Datei ersetzt `test_bevoelkerung_altert_nicht.py`**, und der Grund ist
eine Korrektur: Die erste Fassung von P2.4 stellte fest, dass `age` für das
Verhalten **exakt** folgenlos war, und behandelte das als *Begründung* dafür,
keinen Alterungspfad zu bauen. Das war der Befund, nicht die Rechtfertigung. Ein
Achtzehnjähriger ist ein anderer Reisender als ein Siebzigjähriger — dass das
Modell den Unterschied nicht kannte, war die Lücke.

**Wo das Alter jetzt wirkt, und wo bewusst nicht:**

Es formt die Merkmale **beim Ziehen** (`AltersProfil`) und steht **nicht** als
Term in `booking_probability`. Alter verursacht keine Buchung; es wirkt über
Einkommen, Lebensphase und Reiseanlass — und die stehen dort bereits. Ein
zusätzlicher Alters-Term zählte doppelt, und die Nutzenfunktion ist ein
Discrete-Choice-Modell über entscheidungsrelevante Merkmale, nicht über
Soziodemografie.

**Daraus folgt eine Eigenschaft, die überrascht und richtig ist:** Eine
*bestehende* Person nachträglich zu altern ändert ihr Verhalten nicht. Ihr
Einkommen wurde beim Ziehen festgelegt und wird nicht rückwirkend neu bestimmt.
Wer echte Alterung will, müsste die Merkmale je Tick neu ableiten — und dafür
festlegen, wie viele Jahre ein Tick ist. Das ist die Kalendersemantik, die
Invariante 5 ausschließt. **Die Bevölkerung bleibt deshalb eine wiederholte
Querschnittserhebung**: Wächst sie, kommen frisch gezogene Personen dazu, und
die Altersstruktur bleibt stabil.
"""

from __future__ import annotations

from statistics import mean

import pytest

from src.config_loader import build_initial_state, load_properties_config
from src.models.property_models import ShiftRule
from src.population.population_sampler import (
    SHIFT_ZIELE,
    apply_factor_shifts,
    booking_probability,
    initialize_population,
)


@pytest.fixture(scope="module")
def properties():
    return load_properties_config()


@pytest.fixture(scope="module")
def leute(properties):
    zustand = build_initial_state()
    config = next(
        agent for agent in zustand.agents if getattr(agent, "population_config", None)
    ).population_config
    return initialize_population(properties, config, seed=42)


@pytest.fixture(scope="module")
def faktoren():
    zustand = build_initial_state()
    lage = zustand.environment.factors
    lage["F1"] = lage["F1"].model_copy(update={"current_state": "F1.2"})
    return lage


def _gruppe(leute, unten: int, oben: int):
    return [person for person in leute if unten <= person.age <= oben]


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


class TestDasAlterFormtDieMerkmale:
    """Der Kern: ein Achtzehnjähriger ist ein anderer Reisender."""

    def test_das_einkommen_folgt_dem_lebenszyklus(self, leute):
        """Eine **Glocke**, keine Gerade — jung und alt liegen beide niedriger.

        Deshalb wäre eine lineare Korrelation mit dem Alter hier nahe null und
        als Prüfung wertlos: Sie misst die Steigung einer Kurve, die keine hat.
        """

        jung = mean(p.base_income_factor for p in _gruppe(leute, 18, 25))
        mitte = mean(p.base_income_factor for p in _gruppe(leute, 36, 50))
        alt = mean(p.base_income_factor for p in _gruppe(leute, 66, 90))

        assert mitte > jung * 1.15, f"Lebensmitte {mitte:.3f} gegen jung {jung:.3f}"
        assert mitte > alt * 1.15, f"Lebensmitte {mitte:.3f} gegen alt {alt:.3f}"

    def test_preisempfindlichkeit_ist_an_den_raendern_hoeher(self, leute):
        """Die Kehrseite des Einkommens, **kein zweiter Alterseffekt**."""

        jung = mean(p.price_sensitivity for p in _gruppe(leute, 18, 25))
        mitte = mean(p.price_sensitivity for p in _gruppe(leute, 36, 50))
        alt = mean(p.price_sensitivity for p in _gruppe(leute, 66, 90))

        assert jung > mitte and alt > mitte

    @pytest.mark.parametrize("merkmal", ["environmental_awareness", "substitution_readiness"])
    def test_umweltbewusstsein_und_bahnbereitschaft_fallen_mit_dem_alter(self, leute, merkmal):
        """Hier **monoton**, nicht glockenförmig — anders als das Einkommen."""

        jung = mean(getattr(p, merkmal) for p in _gruppe(leute, 18, 30))
        alt = mean(getattr(p, merkmal) for p in _gruppe(leute, 66, 90))

        assert jung > alt, f"{merkmal}: jung {jung:.3f}, alt {alt:.3f}"

    def test_und_das_kommt_bei_der_buchung_an(self, leute, properties):
        """**Die eigentliche Zusage.** Ohne diesen Test wären die Merkmale nur
        anders verteilt, ohne dass es irgendwo einen Unterschied macht — genau
        der Zustand, den P2.4 vorgefunden hat.

        Erwartet wird derselbe Glockenverlauf: Menschen in der Lebensmitte
        fliegen am meisten.
        """

        jung = _rate(_gruppe(leute, 18, 25), properties)
        mitte = _rate(_gruppe(leute, 36, 50), properties)
        alt = _rate(_gruppe(leute, 66, 90), properties)

        assert mitte > jung * 1.5, f"Lebensmitte {mitte:.3f} gegen jung {jung:.3f}"
        assert mitte > alt * 1.3, f"Lebensmitte {mitte:.3f} gegen alt {alt:.3f}"

    def test_jeder_koeffizient_traegt_seine_herkunft(self, properties):
        """Wie bei den Buchungskoeffizienten (P2.1): **Richtung belegt, Höhe
        gesetzt** — und jeder Wert sagt selbst, was davon auf ihn zutrifft."""

        profil = properties.alters_profil
        felder = [
            name for name in type(profil).model_fields if hasattr(getattr(profil, name), "quelle")
        ]

        assert len(felder) >= 6
        for name in felder:
            quelle = getattr(profil, name).quelle
            assert len(quelle) > 80, f"{name}: Herkunft zu knapp"
            assert "gesetzt" in quelle.lower() or "belegt" in quelle.lower(), name


class TestDasAlterStehtNichtImNutzenterm:
    """Die Gestaltungsentscheidung, festgehalten — sie ist leicht zu übersehen."""

    def test_booking_probability_liest_kein_alter(self):
        """Ein Alters-Term dort zählte doppelt: Einkommen und Preisempfindlichkeit
        tragen den Alterseffekt bereits, weil sie aus ihm gezogen wurden."""

        import inspect

        körper = inspect.getsource(booking_probability).split('"""')[-1]

        assert ".age" not in körper

    def test_eine_bestehende_person_nachtraeglich_zu_altern_wirkt_nicht(self, leute, properties):
        """**Überraschend und richtig.**

        Das Alter wirkt beim Ziehen. Wer eine fertige Person älter macht, ändert
        ihr Einkommen nicht rückwirkend — genau deshalb ist echte Alterung eine
        andere, größere Frage als «beeinflusst Alter das Verhalten».
        """

        gealtert = [p.model_copy(update={"age": min(90, p.age + 20)}) for p in leute]

        assert _rate(gealtert, properties) == _rate(leute, properties)


class TestDieBevoelkerungBleibtEinQuerschnitt:
    """Was von der ersten Fassung von P2.4 gilt — mit neuer Begründung."""

    def test_wachstum_zieht_aus_derselben_verteilung(self, properties, leute):
        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config
        zuwachs = initialize_population(
            properties, config.model_copy(update={"total_population": 80}), seed=1042
        )

        vorher = mean(p.age for p in leute)
        nachher = mean(p.age for p in [*leute, *zuwachs])

        assert abs(nachher - vorher) < 2.0

    def test_shift_regeln_erreichen_das_alter_weiterhin_nicht(self, leute, faktoren):
        """Und zwar laut — seit dem 2026-08-31."""

        regel = ShiftRule(
            id="altern",
            when={"factor": "F1", "state": "F1.2"},
            effect={"property": "age", "delta": 5.0},
        )

        with pytest.raises(ValueError, match="unbekanntes Ziel"):
            apply_factor_shifts(
                list(leute[:20]), [regel], faktoren, tick=1, metrics={}, system_properties={}
            )

    def test_die_erreichbaren_ziele_sind_unveraendert(self):
        assert set(SHIFT_ZIELE) == {
            "environmental_awareness",
            "price_sensitivity",
            "income_factor",
        }


class TestDieGesellschaftDarfAlternDieKohorteNicht:
    """P2.4-D (2026-08-31) — **die Altersstruktur ist ein exogener Verlauf**.

    Der Einwand, der dazu geführt hat: «Es kommt doch darauf an, wie viele Ticks
    man macht — evtl. möchte man Jahre.» Richtig, und die Antwort ist nicht,
    Personen altern zu lassen.

    **Gemessen am 2026-08-31**: Ließe man die Kohorte über 40 Ticks mitaltern,
    fiele die Buchungsrate um **47,6 %** und die Bevölkerung wäre am Ende im
    Schnitt **83** Jahre alt. Das ist ein Jahrgang, keine Gesellschaft — real
    kommen junge nach und alte scheiden aus.

    Eine Gesellschaft altert, weil sich ihre **Zusammensetzung** verschiebt.
    `altersmittel_jahre` ist deshalb eine Systemgröße wie `income_index`: Ein
    Rahmenszenario gibt ihren Verlauf vor, und wer neu in die Bevölkerung kommt,
    wird aus der Verteilung gezogen, die *dann* gilt. Ohne Verlauf bleibt die
    Gesellschaft stationär — eine gültige Aussage, kein Versehen.
    """

    @staticmethod
    def _ziehen(properties, altersmittel: float | None):
        from src.population.population_sampler import run_population_tick

        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config
        system = {"bevoelkerungsentwicklung": 1000}
        if altersmittel is not None:
            system["altersmittel_jahre"] = altersmittel

        return run_population_tick(
            properties,
            config,
            None,
            ticket_price=140.0,
            carbon_tax=50.0,
            factors={},
            system_properties=system,
            seed=42,
            current_tick=1,
            metrics={},
        )

    def test_die_systemgroesse_gibt_es_und_sie_steht_auf_dem_datenwert(self, properties):
        prop = properties.get_system_property("altersmittel_jahre")

        assert prop.trajectory.baseline == pytest.approx(50.8), "Der Eurostat-Wert"
        assert "Eurostat" in (prop.description or "")

    @pytest.mark.parametrize("mittel", [55.0, 60.0])
    def test_ein_hoeheres_altersmittel_kommt_in_der_ziehung_an(self, properties, mittel):
        leute, _ = self._ziehen(properties, mittel)

        assert mean(p.age for p in leute) == pytest.approx(mittel, abs=1.5)

    def test_eine_aeltere_gesellschaft_bucht_weniger(self, properties):
        """**Die Zusage, für die das gebaut wurde** — und die Größenordnung.

        Rund fünf Prozent weniger bei neun Jahren höherem Altersmittel. Deutlich
        weniger als die 47,6 % einer alternden Kohorte, und das ist der Punkt:
        Eine Gesellschaft altert langsam, weil sie sich erneuert.
        """

        _, jung = self._ziehen(properties, 50.8)
        _, alt = self._ziehen(properties, 60.0)

        rate_jung = jung.total_booked / jung.total_population
        rate_alt = alt.total_booked / alt.total_population

        assert rate_alt < rate_jung, f"jung {rate_jung:.4f}, alt {rate_alt:.4f}"
        assert rate_alt > rate_jung * 0.85, (
            f"Der Rückgang ist auf {1 - rate_alt / rate_jung:.1%} gewachsen. Über "
            "15 % wäre es kein Kompositionseffekt mehr — dann altert hier doch "
            "eine Kohorte."
        )

    def test_ohne_die_systemgroesse_bleibt_alles_stationaer(self, properties):
        """Eine Config, die sie nicht kennt, beschreibt eine stehende Gesellschaft."""

        ohne, _ = self._ziehen(properties, None)
        mit, _ = self._ziehen(properties, 50.8)

        assert mean(p.age for p in ohne) == pytest.approx(mean(p.age for p in mit), abs=0.01)
