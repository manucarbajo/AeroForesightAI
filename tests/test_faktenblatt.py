"""Das Faktenblatt eines Laufs — die Rechnung in Sätzen, bevor das Sprachmodell schreibt (P8-V3).

**Der Befund:** Am 2026-09-29 schrieb `llama3.2` unter «Business as Usual»,
die Preise für Treibhausgasemissionen stiegen kontinuierlich — die CO₂-Abgabe
stand über 120 Ticks bei 50 EUR. Das Modell bekam Rohzahlen und zwei
Trendwörter mit eigenen Schwellen (`booking_trend`, `price_trend`) und deutete
selbst. Seither bekommt es die Richtung jeder Kerngröße als fertigen Satz.

**Die tragende Zusage ist eine Quelle für Text und Prüfung:** Jeder Satz des
Faktenblatts besteht die Prüfung, gegen die der Text danach gehalten wird —
sonst widerspräche die Vorlage ihrem eigenen Maßstab.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.reporting.aussagen_pruefung import faktenblatt, faktorwechsel, laufzeilen, pruefe
from src.reporting.run_scenario_generator import load_run_scenario_context
from src.reporting.run_scenario_generator.prompt import build_scenario_prompt, faktenblatt_saetze
from tests.test_run_scenario_generator import _write_scenario_fixture


def _ticks(**verlauf: tuple[float, ...]) -> list[dict]:
    felder = {
        "preis": "market_price_after_feedback_eur",
        "buchung": "booking_rate",
        "co2": "carbon_tax_level",
        "saf": "saf_mandate_share",
        "nachfrage": "demand_level",
    }
    laenge = max(len(werte) for werte in verlauf.values())
    return [
        {"tick": i + 1, **{felder[k]: v[i] for k, v in verlauf.items() if i < len(v)}}
        for i in range(laenge)
    ]


#: «Business as Usual» am 2026-09-29: CO₂-Abgabe steht, Preis kaum bewegt.
BAU = _ticks(
    preis=(140.6, 138.2, 131.9),
    buchung=(0.479, 0.41, 0.374),
    co2=(50.0, 50.0, 50.0),
    saf=(0.02, 0.04, 0.06),
    nachfrage=(1.0, 0.98, 0.97),
)
#: «Transformationskonflikt»: Preis von 140 auf 437 EUR.
TK = _ticks(preis=(140.05, 300.0, 437.27), buchung=(0.37, 0.1, 0.003), co2=(50.0, 150.0, 250.0))


class TestDasBlattSagtDieRichtung:
    def test_eine_stehende_abgabe_steht_als_unveraendert_da(self):
        saetze = [f.satz for f in faktenblatt(BAU)]

        assert "CO₂-Abgabe bleibt unverändert bei 50,00 € (Tick 1 bis 3)." in saetze

    def test_ein_steigender_preis_mit_anfang_und_ende(self):
        preis = next(f for f in faktenblatt(TK) if f.groesse == "Ticketpreis")

        assert preis.richtung == "steigt"
        assert "steigt von 140,05 € auf 437,27 €" in preis.satz

    def test_ein_anteil_steht_in_prozent(self):
        rate = next(f for f in faktenblatt(BAU) if f.groesse == "Buchungsrate")

        assert "47,9 %" in rate.satz and "37,4 %" in rate.satz

    def test_eine_groesse_ohne_werte_fehlt(self):
        """Worüber das Blatt nichts sagt, darüber darf der Text nichts behaupten."""

        assert "Kostendruck" not in {f.groesse for f in faktenblatt(BAU)}


class TestEineQuelleFuerTextUndPruefung:
    @pytest.mark.parametrize("ticks", [BAU, TK], ids=["bau", "tk"])
    def test_jeder_satz_des_blatts_besteht_die_pruefung(self, ticks):
        for fakt in faktenblatt(ticks):
            assert pruefe(fakt.satz, ticks) == [], fakt.satz

    def test_die_pruefung_erkennt_die_groessen_des_blatts(self):
        """Sonst bestünde das Blatt die Prüfung nur, weil sie es nicht liest."""

        falsch = "Die CO₂-Abgabe steigt kontinuierlich an. Die SAF-Quote sinkt."
        arten = [b.erklaerung.split(":")[0] for b in pruefe(falsch, BAU)]

        assert arten == ["CO₂-Abgabe", "SAF-Quote"]


class TestFaktorwechsel:
    ZEILEN = [
        {"tick": "1", "F1": "F1.1", "F2": "F2.1", "F6": "F6.1"},
        {"tick": "2", "F1": "F1.1", "F2": "F2.1", "F6": "F6.2"},
        {"tick": "3", "F1": "F1.2", "F2": "F2.1", "F6": "F6.1"},
    ]

    def test_je_faktor_ein_satz(self):
        saetze = faktorwechsel(self.ZEILEN, {"F1": "Nachfrage", "F1.2": "Stagnation"})

        assert saetze == [
            "F1 (Nachfrage) wechselt von F1.1 zu F1.2 «Stagnation» (1-mal im Lauf).",
            "F2 bleibt den ganzen Lauf bei F2.1.",
            "F6 beginnt und endet bei F6.1, wechselt dazwischen 2-mal.",
        ]


class TestDerAbschlusstextBekommtDasBlatt:
    def test_laufzeilen_nehmen_die_saf_quote_aus_den_systemgroessen(self, tmp_path: Path):
        _write_scenario_fixture(tmp_path, booking_start=0.6, booking_end=0.4)
        (tmp_path / "timeseries" / "properties.csv").write_text(
            "tick,saf_mandate_share,carbon_tax_level\n0,0.0,50\n1,0.02,50\n2,0.04,50\n3,0.06,50\n",
            encoding="utf-8",
        )

        zeilen = laufzeilen(tmp_path)

        assert [z["saf_mandate_share"] for z in zeilen] == [0.02, 0.04, 0.06]
        assert "SAF-Quote steigt von 2,0 % auf 6,0 %" in faktenblatt(zeilen)[1].satz

    def test_das_blatt_steht_vorn_im_prompt(self, tmp_path: Path):
        _write_scenario_fixture(tmp_path, booking_start=0.6, booking_end=0.4)
        context = load_run_scenario_context("fixture", run_dir=tmp_path)

        prompt = build_scenario_prompt(context)
        daten = json.loads(prompt.split("```json\n", 1)[1].split("\n```", 1)[0])

        assert next(iter(daten)) == "faktenblatt"
        assert daten["faktenblatt"] == faktenblatt_saetze(context)
        assert any(satz.startswith("Buchungsrate sinkt") for satz in daten["faktenblatt"])
        assert any(satz.startswith("F3 (") for satz in daten["faktenblatt"])

    def test_keine_zweite_trendquelle_daneben(self, tmp_path: Path):
        """`booking_trend`/`price_trend` hatten eigene Schwellen — zwei Antworten auf eine Frage."""

        _write_scenario_fixture(tmp_path, booking_start=0.6, booking_end=0.4)
        prompt = build_scenario_prompt(load_run_scenario_context("fixture", run_dir=tmp_path))

        assert '"booking_trend"' not in prompt and '"price_trend"' not in prompt


class TestDieAbfrageBekommtDasBlatt:
    def test_es_steht_vor_den_rohdaten(self, tmp_path: Path):
        from src.reporting.state_explorer import build_grounded_context_block, load_run_context

        _write_scenario_fixture(tmp_path / "lauf", booking_start=0.6, booking_end=0.4)
        block = build_grounded_context_block(load_run_context("lauf", outputs_root=tmp_path))

        assert block.index("faktenblatt") < block.index("run_summary:")
        assert "- Buchungsrate sinkt von 60,0 % auf 40,0 %" in block


class TestDieVorlageSprichtDieselbeRichtung:
    """Die deterministische Vorlage des Abschlusstexts urteilte mit eigenen Schwellen."""

    def test_ein_kleiner_preisanstieg_ist_auch_dort_stabil(self):
        from src.reporting.run_scenario_generator.context import _price_trend

        # +6 EUR sind über der alten Schwelle von 5 EUR, aber unter fünf Prozent.
        metriken = {"ticket_price_start_eur": 140.0, "ticket_price_end_eur": 146.0}

        assert _price_trend(metriken) == "stabil"

    def test_das_lauf_narrativ_der_vorlage_besteht_die_pruefung(self, tmp_path: Path):
        from src.reporting.run_scenario_generator import build_factor_profile, build_run_narrative

        _write_scenario_fixture(tmp_path, booking_start=0.6, booking_end=0.4)
        context = load_run_scenario_context("fixture", run_dir=tmp_path)

        text = build_run_narrative(context, build_factor_profile(context))

        assert pruefe(text, laufzeilen(tmp_path)) == [], text
