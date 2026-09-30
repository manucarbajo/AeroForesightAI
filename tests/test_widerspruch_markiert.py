"""Ein Text, der der Rechnung widerspricht, wird markiert — im Artefakt, im Dashboard und in der Abfrage (P8-V3).

**Der Befund vom 2026-09-29:** Die Abschlusstexte des Sprachmodells widersprachen
der Rechnung, zu der sie gehören («die Preise für Treibhausgasemissionen steigen»
bei einer CO₂-Abgabe, die über 120 Ticks bei 50 EUR stand), und die Abfrage
antwortete «die Buchungsrate ist gestiegen», während sie fiel. Geprüft wurde
davon nichts: Die Zahlenprüfung aus P2.5 sieht keine Richtung.

**Markieren statt zurückweisen**, dieselbe Produktentscheidung wie bei der
unbelegten Zahl: Der Text bleibt stehen, der Widerspruch steht direkt darunter.
Geprüft wird, was über **den gerechneten Lauf** gesagt ist — die drei Szenarien
beschreiben mögliche Zukünfte und bleiben ausgenommen.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.reporting.aussagen_pruefung import widersprueche
from src.reporting.run_scenario_generator import (
    build_candidate_constellations,
    build_factor_profile,
    generate_and_save_run_scenario,
    load_run_scenario_context,
)
from src.reporting.state_explorer import StateExplorer, load_run_context
from tests.test_run_scenario_generator import _write_scenario_fixture

#: Die Buchungsrate fällt im Fixture von 70 auf 30 %.
FALSCH = "Die Buchungsrate steigt über den ganzen Lauf deutlich an."
RICHTIG = "Die Buchungsrate sinkt über den Lauf von 70 auf 30 Prozent."


def _abschlusstext(run_dir: Path, *, run_narrative: str, story: str) -> dict:
    context = load_run_scenario_context(run_dir.name, run_dir=run_dir)
    kandidaten = build_candidate_constellations(context, build_factor_profile(context), {})
    antwort = {
        "title": "Drei Zukünfte des Luftverkehrs",
        # Über 200 Zeichen, sonst ersetzt die Pipeline sie durch die Vorlage.
        "summary": "Der Lauf zeigt eine sachlich beschriebene Entwicklung. " * 5,
        "run_narrative": run_narrative,
        "selection_reasoning": "Fortsetzung, Alternative und Spannung.",
        "scenarios": [
            {"rank": i + 1, "candidate_id": k["candidate_id"], "title": f"T{i}", "story": story}
            for i, k in enumerate(kandidaten[:3])
        ],
    }

    class _Modell:
        def call(self, prompt: str) -> str:
            return json.dumps(antwort, ensure_ascii=False)

    return generate_and_save_run_scenario(run_dir.name, _Modell(), run_dir=run_dir)


class TestDerAbschlusstextWirdMarkiert:
    def test_ein_widerspruch_steht_in_artefakt_und_markdown(self, tmp_path: Path):
        run_dir = tmp_path / "lauf"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)

        ergebnis = _abschlusstext(run_dir, run_narrative=FALSCH, story=RICHTIG * 3)

        gespeichert = json.loads((run_dir / "run_scenario.json").read_text(encoding="utf-8"))
        markdown = (run_dir / "run_scenario.md").read_text(encoding="utf-8")
        assert [w["feld"] for w in gespeichert["widersprueche"]] == ["run_narrative"]
        assert "gerechnet «sinkt»" in gespeichert["widersprueche"][0]["zeile"]
        assert "Widerspricht der Rechnung" in markdown
        assert ergebnis["widersprueche"] == gespeichert["widersprueche"]

    def test_ein_richtiger_text_bleibt_ohne_markierung(self, tmp_path: Path):
        run_dir = tmp_path / "lauf"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)

        _abschlusstext(run_dir, run_narrative=RICHTIG, story=RICHTIG * 3)

        gespeichert = json.loads((run_dir / "run_scenario.json").read_text(encoding="utf-8"))
        assert gespeichert["widersprueche"] == []
        assert "Widerspricht der Rechnung" not in (run_dir / "run_scenario.md").read_text(
            encoding="utf-8"
        )

    def test_die_szenarien_sind_ausgenommen(self, tmp_path: Path):
        """Eine mögliche Zukunft darf anders verlaufen als der gerechnete Lauf."""

        run_dir = tmp_path / "lauf"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)

        ergebnis = _abschlusstext(run_dir, run_narrative=RICHTIG, story=FALSCH * 3)

        assert ergebnis["widersprueche"] == []

    def test_die_faelle_vom_neunundzwanzigsten_werden_markiert(self):
        ticks = [
            {"tick": 1, "carbon_tax_level": 50.0, "market_price_after_feedback_eur": 140.05},
            {"tick": 120, "carbon_tax_level": 50.0, "market_price_after_feedback_eur": 437.27},
        ]
        text = {
            "run_narrative": "Die Preise für Treibhausgasemissionen steigen kontinuierlich an.",
            "summary": "Der Lauf zeigt jedoch keine Veränderung im Ticketpreis.",
            "title": "2023-01-01: Nachfrage-Rückgewinnung",
        }

        felder = sorted((w["feld"], w["art"]) for w in widersprueche(text, ticks))

        assert felder == [
            ("run_narrative", "richtung"),
            ("summary", "richtung"),
            ("title", "datum"),
        ]


class TestDasDashboardZeigtIhnUnterDemText:
    def test_der_hinweis_steht_direkt_nach_dem_lauf_narrativ(self, tmp_path: Path):
        from dashboard.web.views import scenario

        run_dir = tmp_path / "lauf"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        _abschlusstext(run_dir, run_narrative=FALSCH, story=RICHTIG * 3)

        text = str(scenario.body(run_dir, "lauf"))

        assert "Widerspricht der Rechnung" in text
        assert text.index("Widerspricht der Rechnung") < text.index("Szenarien")


class TestDieAbfrageMarkiertIhn:
    class _Antwortet:
        def __init__(self, text: str) -> None:
            self.text = text

        def call(self, prompt: str) -> str:
            return self.text

    def _frage(self, tmp_path: Path, antwort: str, *, tick: int | None = None):
        _write_scenario_fixture(tmp_path / "lauf", booking_start=0.7, booking_end=0.3)
        kontext = load_run_context("lauf", focus_tick=tick, outputs_root=tmp_path)
        return StateExplorer(kontext, llm=self._Antwortet(antwort)).ask("Wie lief es?")

    def test_eine_falsche_richtung_steht_im_warnblock(self, tmp_path: Path):
        antwort = self._frage(tmp_path, "Die Buchungsrate ist im Lauf gestiegen.")

        assert len(antwort.widersprueche) == 1
        assert "⚠️ **Widerspricht der Rechnung:**" in str(antwort)
        assert "Prüfung:" not in str(antwort), "Kein «alles in Ordnung» unter einem Befund"

    def test_eine_richtige_antwort_bleibt_ohne_warnung(self, tmp_path: Path):
        antwort = self._frage(tmp_path, "Die Buchungsrate ist im Lauf gesunken.")

        assert antwort.widersprueche == ()
        assert "Widerspricht" not in str(antwort)

    def test_eine_frage_zu_einem_tick_prueft_keine_richtung(self, tmp_path: Path):
        """Im einzelnen Tick darf die Buchungsrate steigen, auch wenn sie über den Lauf fällt."""

        antwort = self._frage(tmp_path, "Die Buchungsrate ist gestiegen.", tick=2)

        assert antwort.widersprueche == ()
