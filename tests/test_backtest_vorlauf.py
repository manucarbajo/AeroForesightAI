"""P2.7 — der Vorlauf misst, was er zu messen behauptet.

Das Ergebnis des Vorlaufs steht in `docs/backtest_vorlauf.md` und wird bei jedem
Aufruf überschrieben. Diese Tests halten nicht das *Ergebnis*, sondern die
**Eigenschaften der Messung** — die Zahlen dürfen sich bewegen, das Verfahren
nicht.

**Eine Lehre steckt schon im Bau des Pakets**, und sie gehört festgehalten: Der
erste Anlauf verglich die **monatliche** Bewegungsrichtung und kam auf 44 %
Treffer — unter dem Münzwurf. Das sah aus wie ein vernichtender Befund über das
Modell und war einer über die Kennzahl: Air-Fare-Preise schwanken saisonal um
rund 40 Indexpunkte im Jahr, das Modell um 12, weil es keine Saison kennt. Der
Monatsvergleich maß vor allem, ob das Modell eine Sommersaison hat.

Auf Jahresmitteln sieht dasselbe Modell völlig anders aus — und die eigentliche
Aussage ist die Zweiteilung: vor der Pandemie nah dran, danach nicht.
"""

from __future__ import annotations

import pytest

from src.backtest.auswertung import bewerten, indexieren, jahresmittel, saisonspanne
from src.backtest.rahmen import ZUORDNUNG, historischer_rahmen
from src.backtest.reihen import (
    FENSTER,
    UNBEWERTET,
    alle_monate,
    ist_bewertet,
    laden,
    monat_je_tick,
    tick_je_monat,
)


class TestDieKalenderzuordnungLebtNurHier:
    """Invariante 5 — ein Tick ist ein Tick, auch im Backtest."""

    def test_das_fenster_hat_zwoelf_monate_je_jahr(self):
        monate = alle_monate()
        assert len(monate) == 120
        assert monate[0] == FENSTER[0] and monate[-1] == FENSTER[1]

    def test_tick_eins_ist_der_erste_monat(self):
        assert tick_je_monat()[FENSTER[0]] == 1
        assert monat_je_tick()[1] == FENSTER[0]

    def test_die_zuordnung_ist_umkehrbar(self):
        hin, zurueck = tick_je_monat(), monat_je_tick()
        assert all(zurueck[t] == m for m, t in hin.items())

    def test_kein_datum_erreicht_das_rahmenszenario(self):
        """Der Sweep trägt Ticks, keine Monate — sonst stünde ein Datum in einer
        Config, und genau das verbietet Invariante 5."""

        reihen = {name: laden(name) for name in ZUORDNUNG}
        sweep = historischer_rahmen(reihen)

        for override in sweep.property_overrides:
            for regel in override.rules or []:
                assert isinstance(regel["active_from_tick"], int)
                assert "-" not in str(regel["active_from_tick"])


class TestDieReihenTragenIhreHerkunft:
    @pytest.mark.parametrize("name", sorted(ZUORDNUNG) + ["hicp_flugreisen"])
    def test_jede_reihe_kennt_ihre_quelle(self, name: str):
        reihe = laden(name)

        assert reihe.quelle["url"], f"{name} hat keine URL"
        assert reihe.quelle["abgerufen"], f"{name} hat kein Abrufdatum"
        assert len(str(reihe.quelle["hinweis"])) > 40

    def test_eine_reihe_ohne_herkunft_wird_abgewiesen(self):
        with pytest.raises(KeyError, match="quellen.json"):
            laden("gibt-es-nicht")

    def test_die_zielreihe_ist_vollstaendig(self):
        assert laden("hicp_flugreisen").luecken == []

    def test_die_eua_luecke_ist_benannt_und_echt(self):
        """Im Januar 2021 fand keine gemeinsame EU-Auktion statt.

        Sie **nicht** zu füllen ist die Aussage: Ein Monat ohne Auktion ist kein
        Monat mit dem Preis null. Für die Eingabe in den Lauf wird der letzte
        beobachtete Preis fortgeschrieben, für die Auswertung nicht.
        """

        reihe = laden("eua_auktionspreis")

        assert reihe.luecken == ["2021-01"]
        assert "2021-01" not in reihe.werte
        assert reihe.fortgeschrieben()["2021-01"] == reihe.werte["2020-12"]

    def test_fortschreiben_erfindet_nichts_dazwischen(self):
        reihe = laden("eua_auktionspreis")
        gefuellt = reihe.fortgeschrieben()

        for monat, wert in reihe.werte.items():
            assert gefuellt[monat] == wert, f"{monat} wurde beim Fortschreiben verändert"


class TestDerRahmenSpeistDieAussenwelt:
    def test_er_deckt_das_ganze_fenster_ab(self):
        sweep = historischer_rahmen({name: laden(name) for name in ZUORDNUNG})

        assert sweep.max_ticks == 120
        assert {o.property_id for o in sweep.property_overrides} == {
            "carbon_tax_level",
            "oil_price_index",
        }

    def test_der_oelpreis_wird_indexiert_der_co2_preis_nicht(self):
        """`oil_price_index` ist ein Index mit Ausgangswert 1,0, Brent steht in
        Dollar je Barrel. Roh eingespeist stünde dort 52 statt 1,0."""

        sweep = historischer_rahmen({name: laden(name) for name in ZUORDNUNG})
        je_id = {o.property_id: o for o in sweep.property_overrides}

        oel = [r["effect"]["value"] for r in je_id["oil_price_index"].rules or []]
        assert (
            0.3 < min(oel) < max(oel) < 3.0
        ), f"Ölpreisindex außerhalb des Erwarteten: {min(oel)}–{max(oel)}"

        co2 = [r["effect"]["value"] for r in je_id["carbon_tax_level"].rules or []]
        assert 3.0 < min(co2) and max(co2) > 50.0, "Der CO₂-Preis sieht nicht nach EUR/t aus"

    def test_eine_fehlende_reihe_scheitert_laut(self):
        with pytest.raises(KeyError, match="brent_rohoel"):
            historischer_rahmen({"eua_auktionspreis": laden("eua_auktionspreis")})


class TestDieAuswertungMisstDasRichtige:
    def test_zwanzig_zwanzig_wird_mitgerechnet_aber_nicht_bewertet(self):
        assert UNBEWERTET == {"2020", "2021"}
        assert not ist_bewertet("2020-06") and not ist_bewertet("2021-06")
        assert ist_bewertet("2019-12") and ist_bewertet("2022-01")

    def test_die_ausgenommenen_jahre_stehen_trotzdem_in_der_tabelle(self):
        """«Mitgerechnet, aber nicht bewertet» heißt: sichtbar, nicht verrechnet."""

        modell = {m: 100.0 for m in alle_monate()}
        ziel = {m: 100.0 + (50.0 if m.startswith("2020") else 0.0) for m in alle_monate()}

        ergebnis = bewerten(modell, ziel)

        assert "2020" in ergebnis.modell_je_jahr, "Das Jahr fehlt in der Tabelle"
        assert "2020" in ergebnis.unbewertete_jahre
        assert "2020" not in ergebnis.bewertete_jahre
        assert ergebnis.mittlerer_abstand < 1.0, (
            "Der Ausschlag von 2020 ist in die Kennzahl eingegangen — dann wird er "
            "doch bewertet."
        )

    def test_der_index_setzt_das_basisjahr_auf_hundert(self):
        reihe = {m: 42.0 for m in alle_monate()}
        indexiert = indexieren(reihe, basisjahr="2015")

        assert jahresmittel(indexiert)["2015"] == pytest.approx(100.0)

    def test_die_saisonspanne_misst_innerhalb_eines_jahres(self):
        glatt = {m: 100.0 for m in alle_monate()}
        gezackt = {m: 100.0 + (20.0 if m.endswith("-07") else 0.0) for m in alle_monate()}

        assert saisonspanne(glatt) == 0.0
        assert saisonspanne(gezackt) == pytest.approx(20.0)

    def test_die_saisonwarnung_erscheint_wenn_sie_muss(self):
        """**Der Befund, der die Kennzahl umgebaut hat.** Eine Zielreihe mit
        Saison und ein Modell ohne muss als solche benannt werden — sonst liest
        jemand einen Monatsvergleich als Urteil über die Mechanik."""

        glatt = {m: 100.0 for m in alle_monate()}
        saisonal = {
            m: 100.0 + (30.0 if m.endswith(("-06", "-07", "-08")) else 0.0) for m in alle_monate()
        }

        hinweise = " ".join(bewerten(glatt, saisonal).hinweise)

        assert "Saison" in hinweise and "Monatsvergleich" in hinweise

    def test_ohne_ueberlappung_scheitert_es_laut(self):
        with pytest.raises(ValueError):
            bewerten({}, {m: 100.0 for m in alle_monate()})


def test_der_vorlauf_laeuft_durch_und_liefert_beide_seiten():
    """Der ganze Weg einmal — langsam, aber die einzige Zusage, die zaehlt.

    **Beide Zielreihen kommen aus einem Lauf.** Zwei Laeufe verglichen zwei
    verschiedene Welten, und die Nachfrage antwortete auf einen anderen Preis
    als den, der geprueft wird.
    """

    from src.backtest.vorlauf import ZIELREIHEN, modellpfade

    pfade = modellpfade()

    for titel, (modellgroesse, zielname) in ZIELREIHEN.items():
        assert (
            len(pfade[modellgroesse]) == 120
        ), f"{titel}: der Lauf liefert {len(pfade[modellgroesse])} statt 120 Monate"

        ergebnis = bewerten(pfade[modellgroesse], laden(zielname).werte)
        vor = [j for j in ergebnis.bewertete_jahre if j < "2020"]
        nach = [j for j in ergebnis.bewertete_jahre if j > "2021"]

        assert ergebnis.abstand_ueber(vor) is not None, titel
        assert ergebnis.abstand_ueber(nach) is not None, titel
        assert "2020" in ergebnis.unbewertete_jahre, titel


def test_die_beiden_seiten_sagen_verschiedenes():
    """Der eigentliche Befund des Pakets, als Messung festgehalten.

    Die **Preisseite** trifft vor der Pandemie fast genau (rund zwei
    Indexpunkte), die **Nachfrageseite** liegt schon dort um ein Vielfaches
    daneben — und zwar in die falsche Richtung: Das Modell laesst die
    Buchungsrate fallen, wo real die Fluggastzahlen stiegen.

    Wuerde dieser Test gruen bleiben, waere das eine gute Nachricht und der
    Anlass, den Bericht neu zu schreiben.
    """

    from src.backtest.vorlauf import modellpfade

    pfade = modellpfade()
    vorjahre = ["2015", "2016", "2017", "2018", "2019"]

    preis = bewerten(pfade["ticket_price"], laden("hicp_flugreisen").werte)
    nachfrage = bewerten(pfade["booking_rate"], laden("fluggaeste").werte)

    assert nachfrage.abstand_ueber(vorjahre) > 3 * preis.abstand_ueber(vorjahre), (
        f"Preis {preis.abstand_ueber(vorjahre)}, Nachfrage "
        f"{nachfrage.abstand_ueber(vorjahre)} — die Zweiteilung ist weg. "
        "Entweder hat jemand die Nachfrageseite repariert (dann gehoert der "
        "Bericht neu geschrieben) oder die Preisseite ist schlechter geworden."
    )
