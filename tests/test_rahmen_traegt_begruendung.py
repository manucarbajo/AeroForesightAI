"""P2.2 / Variante C — ein Rahmenszenario trägt seine Kohärenzbegründung.

**Die Entscheidung, die diese Datei durchsetzt** ([P2.2](../docs/projektplan.md),
getroffen am 2026-08-31 nach dem Backtest): Die Kohärenz eines Rahmenszenarios
wird **in Prosa mit Quellen** begründet, nicht von einem Algorithmus geprüft.
Die CIB-Matrix misst nachweislich Polarität statt Plausibilität
(`test_cib_einachsigkeit.py`), und eine neu erhobene Matrix wäre ein Versprechen
von Präzision, das die Daten nicht decken.

**Der Preis von Variante C ist, dass nichts sie mechanisch erzwingt** — außer
diesem Wächter. Eine Prosa-Begründung, die niemand prüft, ist in sechs Monaten
ein leeres Feld. Er hält deshalb dieselbe Zusage wie
`test_buchungskoeffizienten.py` für die Buchungskoeffizienten: **Jede Aussage
trägt ihre Herkunft, und keine behauptet eine Genauigkeit, die es nicht gibt.**

**Der Fund, aus dem das Paket seinen Umfang bekam:** Unter `configs/sweeps/`
lagen zwei Dinge ununterscheidbar nebeneinander, und der Szenario-Vergleich
startete beide — vier begründete Weltbilder und vier Stresstests der Engine.
«Totaler Wahnsinn (Alle Parameter)» stand gleichrangig neben «Business as
Usual». Einem Kunden wurde damit ein Belastungstest als Zukunft angeboten.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from dashboard.config_catalog import list_sweep_presets, rahmenszenarien
from src.models.sweep_models import ARTEN, SweepConfig
from src.orchestration.scenario_sweeps import SWEEPS_DIR

ALLE = list_sweep_presets()
RAHMEN = [s for s in ALLE if s.art == "rahmen"]


def test_es_liegen_ueberhaupt_rahmenszenarien_da():
    """Ohne diesen Test wäre jeder folgende leer und damit grün."""

    assert len(RAHMEN) >= 4, f"Nur {len(RAHMEN)} Rahmenszenarien gefunden"


@pytest.mark.parametrize("szenario", ALLE, ids=lambda s: s.id)
class TestJedeDateiSagtWasSieIst:
    def test_die_art_ist_bekannt(self, szenario: SweepConfig):
        assert szenario.art in ARTEN

    def test_nichts_liegt_dazwischen(self, szenario: SweepConfig):
        """Entweder begründetes Weltbild oder erklärter Stresstest.

        Ein drittes gibt es nicht — und das ist der Punkt: Vor P2.2 waren
        **alle acht** dieses Dritte, nämlich unmarkiert.
        """

        if szenario.art == "rahmen":
            assert szenario.kohaerenz is not None
        else:
            assert len(szenario.rationale.strip()) > 40, (
                f"{szenario.id} ist als Stresstest geführt, sagt aber nicht wozu. "
                "Ein Stresstest ohne Zweck ist ein Rahmen ohne Begründung."
            )


@pytest.mark.parametrize("szenario", RAHMEN, ids=lambda s: s.id)
class TestEinRahmenTraegtSeineBegruendung:
    def test_er_behauptet_eine_welt_in_einem_satz(self, szenario: SweepConfig):
        assert len(szenario.kohaerenz.these) >= 30

    def test_er_sagt_warum_die_verlaeufe_zusammengehoeren(self, szenario: SweepConfig):
        """**Die eigentliche Zusage von Variante C.**

        Nicht «welche Regel greift bei welchem Tick» — das steht im
        `rationale` und ist eine Umsetzungsnotiz. Sondern: *warum* diese
        Entwicklungen zusammen eine Welt ergeben. Die Grenze ist die Länge
        nicht sicher zu prüfen, aber ein Halbsatz ist es garantiert nicht.
        """

        assert len(szenario.kohaerenz.begruendung) >= 300, (
            f"{szenario.id}: {len(szenario.kohaerenz.begruendung)} Zeichen Begründung. "
            "Variante C trägt die Kohärenz in Prosa — das ist die einzige "
            "Absicherung, die dieses Szenario hat."
        )

    def test_er_nennt_quellen(self, szenario: SweepConfig):
        assert szenario.kohaerenz.quellen, "Ohne Quelle ist es eine Meinung"

    def test_jede_quelle_ist_nachschlagbar(self, szenario: SweepConfig):
        """Eine Quellenangabe muss zu etwas führen — Datei, Rechtsakt oder Reihe.

        Ein Autorenname allein wäre hier zu wenig: Er lässt sich nicht
        nachschlagen, ohne zu raten, was gemeint war.
        """

        for quelle in szenario.kohaerenz.quellen:
            assert len(quelle) >= 40, f"{szenario.id}: Quelle zu knapp — {quelle!r}"

    def test_er_sagt_was_daran_nicht_belegt_ist(self, szenario: SweepConfig):
        """**Die Lehre aus P2.1, hier wiederholt.**

        Eine Literaturangabe an eine handgesetzte Zahl zu heften sieht aus wie
        eine Kalibrierung. Belegt ist die *Storyline*; die Tick-Werte, mit denen
        sie eingestellt wird, sind gesetzt und nicht geschätzt. Jedes
        Rahmenszenario sagt das selbst — nicht nur die Doku daneben.
        """

        vorbehalt = szenario.kohaerenz.vorbehalt
        assert len(vorbehalt) >= 100
        assert "nicht" in vorbehalt.lower()

    def test_keine_quelle_behauptet_eine_eichung(self, szenario: SweepConfig):
        """Das Modell ist auf der Nachfrageseite nachweislich nicht geeicht
        (P2.7). Ein Rahmenszenario darf das nicht anders klingen lassen."""

        text = (szenario.kohaerenz.begruendung + szenario.kohaerenz.these).lower()
        for wort in ("geeicht", "kalibriert", "geschätzt aus", "regressions"):
            assert wort not in text, (
                f"{szenario.id} behauptet mit «{wort}» eine Eichung. Belegt ist die "
                "Storyline, nicht ihre Bezifferung."
            )


class TestDerVergleichVergleichtWeltbilder:
    """Der Befund, der P2.2 seinen Umfang gab."""

    def test_er_laesst_die_stresstests_aus(self):
        ids = {s.id for s in rahmenszenarien()}

        assert ids == {s.id for s in RAHMEN}
        assert "alles_drin_szenario" not in ids, (
            "«Totaler Wahnsinn (Alle Parameter)» wird wieder mitverglichen — "
            "ein Belastungstest ist keine Zukunft."
        )

    def test_ein_stresstest_bleibt_einzeln_startbar(self):
        """Ausgelassen heißt nicht abgeschafft. Wer ihn ausdrücklich nennt,
        bekommt ihn — er verschwindet nur aus dem Vergleich."""

        assert "alles_drin_szenario" in {s.id for s in list_sweep_presets()}


class TestDasSchemaErzwingtEs:
    """Ohne diese beiden wäre der Rest eine Konvention, keine Regel."""

    def test_ein_rahmen_ohne_kohaerenz_wird_abgewiesen(self):
        with pytest.raises(ValidationError, match="kohaerenz"):
            SweepConfig(id="x", name="X", description="", art="rahmen")

    def test_eine_unbekannte_art_wird_abgewiesen(self):
        with pytest.raises(ValidationError, match="Unbekannte Art"):
            SweepConfig(id="x", name="X", description="", art="vielleicht")

    def test_ein_platzhalter_statt_einer_begruendung_wird_abgewiesen(self):
        """Ein Platzhalter ist schlimmer als eine Lücke — er sieht aus wie eine
        Begründung."""

        with pytest.raises(ValidationError, match="Zu kurz"):
            SweepConfig(
                id="x",
                name="X",
                description="",
                art="rahmen",
                kohaerenz={
                    "these": "TODO",
                    "begruendung": "TODO",
                    "quellen": ["irgendwas"],
                    "vorbehalt": "TODO",
                },
            )

    def test_der_standard_ist_stresstest_nicht_rahmen(self):
        """**Die stillere Voreinstellung wäre die falsche.**

        Ein im Dashboard gesichertes Experiment landet in demselben Ordner. Mit
        `rahmen` als Standard würde jede gespeicherte Datei ungefragt zu einer
        begründeten Aussage über die Zukunft.
        """

        assert SweepConfig(id="x", name="X", description="").art == "stresstest"


def test_die_dateien_tragen_das_feld_wirklich():
    """Gegen den Fall, dass ein Default den Test grün hält.

    `art` hat einen Standardwert. Läse eine Datei ihn nicht, fiele sie still
    auf `stresstest` — und jeder Test oben bliebe grün, während das Szenario
    aus dem Vergleich verschwindet.
    """

    for pfad in sorted(SWEEPS_DIR.glob("*.json")):
        roh = json.loads(pfad.read_text(encoding="utf-8"))
        assert "art" in roh, f"{pfad.name} sagt nicht, was es ist"
        if roh["art"] == "rahmen":
            assert "kohaerenz" in roh, f"{pfad.name} ist ein Rahmen ohne Begründung"
