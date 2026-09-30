"""Die Prüfung der Aussagen erkennt die Fälle vom 2026-09-29 — und nur sie (P8-V1).

Die vier Regressionsfälle sind **wörtlich** aus dem Szenario-Vergleich und der
Abfrage vom 2026-09-29 übernommen, gemessen mit `llama3.2`. Daneben stehen
Gegenproben: richtige Aussagen, die **keinen** Befund auslösen dürfen — ein
Fehlalarm trainiert den Leser, die Markierung zu überlesen (dieselbe Abwägung wie
beim State Explorer, P2.5).
"""

from __future__ import annotations

from src.reporting.aussagen_pruefung import ist_englisch, pruefe, verlaeufe


def _ticks(**verlauf: tuple[float, float]) -> list[dict]:
    """Zwei Ticks mit Anfangs- und Endwert je Größe."""

    felder = {
        "preis": "market_price_after_feedback_eur",
        "buchung": "booking_rate",
        "co2": "carbon_tax_level",
        "kosten": "cost_pressure_eur",
    }
    anfang = {felder[k]: v[0] for k, v in verlauf.items()}
    ende = {felder[k]: v[1] for k, v in verlauf.items()}
    return [{"tick": 1, **anfang}, {"tick": 120, **ende}]


#: «Business as Usual»: CO₂-Abgabe konstant 50 €, Preis und Buchungsrate kaum bewegt.
BAU = _ticks(preis=(140.6, 131.9), buchung=(0.479, 0.374), co2=(50.0, 50.0))
#: «Transformationskonflikt»: Preis von 140 auf 437 €, Buchungsrate bricht ein.
TK = _ticks(preis=(140.05, 437.27), buchung=(0.37, 0.003), co2=(50.0, 250.0))


class TestDieFaelleVomNeunundzwanzigsten:
    def test_steigende_co2_preise_bei_konstanter_abgabe(self):
        text = (
            "Ein starker Anstieg der Nachfrage nach Luftfahrtdiensten führte zu einer Krise im Bereich "
            "der Nachhaltigkeit. Die Preise für Treibhausgasemissionen steigen kontinuierlich an."
        )
        befunde = [b for b in pruefe(text, BAU) if b.art == "richtung"]
        assert any("CO₂-Abgabe" in b.erklaerung for b in befunde), befunde
        assert not any(
            "Ticketpreis" in b.erklaerung for b in befunde
        ), "«Preise für Treibhausgase» ist keine Aussage über den Ticketpreis"

    def test_keine_veraenderung_im_ticketpreis(self):
        befunde = pruefe("Der Lauf zeigt jedoch keine Veränderung im Ticketpreis.", TK)
        assert [b.erklaerung for b in befunde] == [
            "Ticketpreis: im Text «gleich», gerechnet «steigt»."
        ]

    def test_ein_erfundenes_datum(self):
        text = "2023-01-01: Nach einer starken Nachfrage-Rückgewinnung beginnt die Nachfrageschwelle zu steigen."
        assert any(b.art == "datum" for b in pruefe(text, TK))

    def test_ein_englischer_agententext(self):
        text = "Implement a pilot program for SAF-powered flights on selected routes to test efficiency and reduce costs."
        assert ist_englisch(text)
        assert any(b.art == "englisch" for b in pruefe(text, BAU))


class TestRichtigeAussagenBleibenStill:
    def test_eine_richtige_richtung(self):
        assert pruefe("Der Ticketpreis steigt auf über 400 Euro.", TK) == []
        assert pruefe("Die Buchungsrate sinkt fast auf null.", TK) == []
        assert pruefe("Die CO₂-Abgabe bleibt konstant bei 50 Euro.", BAU) == []

    def test_ein_deutscher_satz_mit_fachwort_ist_nicht_englisch(self):
        assert not ist_englisch("Die SAF-Quote steigt, und der Kostendruck wächst mit dem Mandat.")

    def test_zwei_groessen_in_einem_satz_werden_getrennt_geprueft(self):
        """«Nachfrage steigt, Preise sinken» — beide Hälften falsch für den Transformationskonflikt."""

        befunde = pruefe("Trends: Nachfrage steigt, Preise sinken.", TK)
        assert sorted(b.erklaerung.split(":")[0] for b in befunde) == [
            "Nachfrage",
            "Ticketpreis",
        ]

    def test_ein_satzteil_ohne_eindeutige_groesse_wird_uebergangen(self):
        """Keine Größe, zwei Größen oder zwei Richtungen: kein Befund statt eines geratenen."""

        assert pruefe("Alles steigt.", TK) == []
        assert pruefe("Die Lage steigt und sinkt je nach Monat.", TK) == []

    def test_eine_groesse_ohne_werte_wird_nicht_geprueft(self):
        assert pruefe("Der Kostendruck sinkt.", TK) == []


def test_verlaeufe_messen_vom_ersten_zum_letzten_tick():
    assert verlaeufe(TK) == {
        "CO₂-Abgabe": {"steigt"},
        "Ticketpreis": {"steigt"},
        "Buchungsrate": {"sinkt"},
        "Nachfrage": {"sinkt"},
    }
    assert verlaeufe(BAU)["CO₂-Abgabe"] == {"gleich"}


class TestDieFehlalarmeDesErstenPruefsatzes:
    """Drei Fehlalarme aus dem ersten Prüfsatz am 2026-09-29, wörtlich — sie bleiben still."""

    def test_abzunehmen_ist_kein_anstieg(self):
        assert pruefe("In der dritten Phase begann die Nachfrage langsam abzunehmen.", BAU) == []

    def test_ein_bedingungssatz_behauptet_nichts(self):
        text = (
            "Wenn die Buchungsrate-Steigerung positiv ist, dann ist die Buchungsrate im Lauf "
            "gestiegen. Buchungsrate-Steigerung = (Buchungsrate am Ende / Buchungsrate am Anfang) - 1"
        )
        assert pruefe(text, BAU) == []

    def test_nachfrage_darf_das_nachfrageniveau_meinen(self):
        """Buchungsrate sinkt, Nachfrageniveau steigt: «die Nachfrage steigt» ist eine Lesart."""

        ticks = [
            {"tick": 1, "booking_rate": 0.40, "demand_level": 1.00},
            {"tick": 40, "booking_rate": 0.30, "demand_level": 1.20},
        ]
        assert pruefe("Die Nachfrage steigt im Lauf.", ticks) == []
        assert [b.art for b in pruefe("Die Buchungsrate steigt im Lauf.", ticks)] == ["richtung"]


class TestEinGenanntesJahrIstEinDatum:
    """Aus dem Vorführbestand vom 2026-09-30, wörtlich — ein Tick hat kein Kalenderjahr."""

    def test_der_satz_aus_dem_pitch_fall(self):
        text = "Im Lauf des Jahres 2025 wächst die globale Luftverkehrsnachfrage."

        assert [b.stelle for b in pruefe(text, BAU) if b.art == "datum"] == ["Jahres 2025"]

    def test_im_jahr_und_ein_volles_datum(self):
        assert any(b.art == "datum" for b in pruefe("Im Jahr 2030 gilt die Quote.", BAU))
        assert any(b.art == "datum" for b in pruefe("Am 01.01.2023 begann es.", BAU))

    def test_eine_blosse_zahl_ist_kein_jahr(self):
        assert not any(b.art == "datum" for b in pruefe("Es waren 2048 Personen in Tick 20.", BAU))
