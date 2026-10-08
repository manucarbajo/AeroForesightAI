from __future__ import annotations

import json
from pathlib import Path

from src.reporting.run_scenario_generator import (
    build_candidate_constellations,
    build_factor_profile,
    build_run_narrative,
    build_template_scenario,
    generate_and_save_run_scenario,
    generate_run_scenario,
    load_run_scenario_context,
    render_run_scenario_markdown,
    save_run_scenario_artifacts,
)

FACTOR_HEADER = "tick,F1,F2,F3,F4,F5,F6,F7\n"


def _write_segment_analysis_fixture(run_dir: Path) -> None:
    (run_dir / "segment_analysis.json").write_text(
        json.dumps(
            [
                {
                    "tick": 1,
                    "agents": {
                        "consumer": {
                            "reasoning": "Preissensibles Segment reagiert auf steigende Ticketpreise.",
                            "actions": ["Reduce bookings"],
                            "segment_analysis": {
                                "price_sensitive": "Buchungen sinken bei Preisanstieg.",
                                "business": "Stabile Nachfrage trotz Preisdruck.",
                            },
                        },
                        "provider": {
                            "reasoning": "Yield-Anpassung wegen schwacher Auslastung.",
                            "actions": ["Adjust markup"],
                            "segment_analysis": {},
                        },
                        "regulator": {
                            "reasoning": "CO2-Rahmen bleibt vorerst unverändert.",
                            "actions": ["NO_OP"],
                            "segment_analysis": {},
                        },
                    },
                },
                {
                    "tick": 3,
                    "agents": {
                        "consumer": {
                            "reasoning": "Substitution zu Bahn bei Langstrecke nimmt zu.",
                            "actions": ["Shift to rail"],
                            "segment_analysis": {
                                "price_sensitive": "Deutlicher Rückgang der Flugbuchungen.",
                            },
                        },
                        "provider": {
                            "reasoning": "Margendruck, aber Preisfloor durch Grenzkosten.",
                            "actions": ["Hold price floor"],
                            "segment_analysis": {},
                        },
                    },
                },
            ]
        ),
        encoding="utf-8",
    )


def _write_scenario_fixture(run_dir: Path, *, booking_start: float, booking_end: float) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": 3,
                "ticks_max": 3,
                "simulation_name": "Fixture Run",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {
                        "tick": 1,
                        "booking_rate": booking_start,
                        "market_price_after_feedback_eur": 120.0,
                    },
                    {
                        "tick": 2,
                        "booking_rate": (booking_start + booking_end) / 2,
                        "market_price_after_feedback_eur": 125.0,
                    },
                    {
                        "tick": 3,
                        "booking_rate": booking_end,
                        "market_price_after_feedback_eur": 130.0,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "price_history.json").write_text(
        json.dumps(
            [
                {"round_number": 1, "price": 120.0},
                {"round_number": 3, "price": 130.0},
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "event_log.json").write_text(
        json.dumps(
            [
                {
                    "round_number": 2,
                    "source_agent": "system",
                    "event_type": "demand_shift",
                    "description": "[delta:booking:population] booking rate changed (Python delta)",
                }
            ]
        ),
        encoding="utf-8",
    )
    ts_dir = run_dir / "timeseries"
    ts_dir.mkdir(parents=True, exist_ok=True)
    (ts_dir / "population.csv").write_text(
        "tick,business,price_sensitive,booking_rate\n1,0.3,0.4,0.5\n",
        encoding="utf-8",
    )
    (ts_dir / "factors.csv").write_text(
        FACTOR_HEADER
        + "1,F1.1,F2.1,F3.1,F4.1,F5.1,F6.1,F7.1\n"
        + "2,F1.1,F2.1,F3.2,F4.1,F5.1,F6.1,F7.1\n"
        + "3,F1.2,F2.1,F3.2,F4.1,F5.1,F6.2,F7.1\n",
        encoding="utf-8",
    )


class TestRunScenarioGenerator:
    def test_load_context_includes_factor_transitions(self, tmp_path):
        run_id = "run_fixture"
        run_dir = tmp_path / run_id
        _write_scenario_fixture(run_dir, booking_start=0.6, booking_end=0.4)
        context = load_run_scenario_context(run_id, run_dir=run_dir)
        transitions = context.summary_metrics.get("factor_transitions") or []
        assert any(item["factor_id"] == "F3" for item in transitions)
        assert any(item["factor_id"] == "F1" for item in transitions)

    def test_run_narrative_mentions_factors(self, tmp_path):
        run_dir = tmp_path / "run_narr"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        context = load_run_scenario_context("run_narr", run_dir=run_dir)
        profile = build_factor_profile(context)
        narrative = build_run_narrative(context, profile)
        assert "F1" in narrative
        assert "F3" in narrative
        assert "Faktor" in narrative

    def test_template_produces_factor_grounded_scenarios(self, tmp_path):
        run_dir = tmp_path / "run_a"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        context = load_run_scenario_context("run_a", run_dir=run_dir)
        payload = build_template_scenario(context)

        assert payload.get("run_narrative")
        assert payload.get("factor_profile", {}).get("end")
        assert len(payload["summary"]) >= 80
        assert len(payload["scenarios"]) == 3
        for scenario in payload["scenarios"]:
            assert scenario.get("tick_grounding")
            assert scenario.get("story")
            assert len(scenario["story"]) >= 80
            assert "Flughafen" not in scenario["story"]
        kinds = {item["scenario_kind"] for item in payload["scenarios"]}
        assert kinds == {"fortsetzung", "alternative", "spannung"}

    def test_die_anhaltspunkte_sprechen_keine_programmsprache(self, tmp_path):
        """Befund 13 der Abnahme vom 2026-09-30: In der Szenario-Ansicht standen
        «Tick 1, BR 37.0%» und «F1=F1.2, F2=F2.2». Seither «Buchungsrate 37,0 %»
        und die Kurzform der Faktorleiste."""

        import re

        run_dir = tmp_path / "run_a"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        payload = build_template_scenario(load_run_scenario_context("run_a", run_dir=run_dir))
        texte = [s["tick_grounding"] for s in payload["scenarios"]] + [payload["summary"]]

        assert all("Buchungsrate" in s["tick_grounding"] for s in payload["scenarios"])
        for text in texte:
            assert not re.search(r"\bBR\b|F\d=F\d|\d\.\d %", text), text

    def test_load_context_builds_agent_digest(self, tmp_path):
        run_dir = tmp_path / "run_digest"
        _write_scenario_fixture(run_dir, booking_start=0.6, booking_end=0.4)
        _write_segment_analysis_fixture(run_dir)
        context = load_run_scenario_context("run_digest", run_dir=run_dir)
        digest = context.agent_digest
        assert digest["has_agent_content"] is True
        assert "consumer" in digest["summary_by_agent"]
        assert digest["segment_themes"]["price_sensitive"]
        assert len(digest["phase_highlights"]) >= 1

    def test_markdown_renders_agent_perspectives(self, tmp_path):
        run_dir = tmp_path / "run_agents"
        _write_scenario_fixture(run_dir, booking_start=0.55, booking_end=0.5)
        _write_segment_analysis_fixture(run_dir)
        context = load_run_scenario_context("run_agents", run_dir=run_dir)
        payload = build_template_scenario(context)
        md = render_run_scenario_markdown(payload, {"run_id": "run_agents"})
        assert "Akteur-Perspektiven" in md
        assert "Passagiere (Consumer)" in md
        assert "price_sensitive" in md

    def test_template_scenario_story_references_agent_digest(self, tmp_path):
        run_dir = tmp_path / "run_story"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        _write_segment_analysis_fixture(run_dir)
        context = load_run_scenario_context("run_story", run_dir=run_dir)
        payload = build_template_scenario(context)
        stories = " ".join(item["story"] for item in payload["scenarios"])
        assert "Tick-Protokoll" in stories

    def test_markdown_renders_factor_profile_and_scenarios(self, tmp_path):
        run_dir = tmp_path / "run_md"
        _write_scenario_fixture(run_dir, booking_start=0.55, booking_end=0.5)
        context = load_run_scenario_context("run_md", run_dir=run_dir)
        payload = build_template_scenario(context)
        md = render_run_scenario_markdown(payload, {"run_id": "run_md"})
        assert "Lauf-Narrativ" in md
        assert "Anhaltspunkte aus dem Lauf" in md
        assert "Szenario-Beschreibung" in md
        assert "CIB-Einordnung" not in md

    def test_generate_and_save_artifacts(self, tmp_path):
        run_id = "run_save"
        run_dir = tmp_path / run_id
        _write_scenario_fixture(run_dir, booking_start=0.55, booking_end=0.5)

        result = generate_run_scenario(run_id, llm=None, run_dir=run_dir, prefer_llm=False)
        md_path, json_path = save_run_scenario_artifacts(run_dir, result)

        assert md_path.is_file()
        assert json_path.is_file()
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert payload["run_narrative"]
        assert payload["factor_profile"]
        assert payload.get("agent_digest") is not None
        assert len(payload["scenarios"]) == 3

    def test_build_candidate_constellations_are_scored_and_ided(self, tmp_path):
        run_dir = tmp_path / "run_cand"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        context = load_run_scenario_context("run_cand", run_dir=run_dir)
        profile = build_factor_profile(context)
        candidates = build_candidate_constellations(context, profile, {})

        assert len(candidates) >= 3
        ids = [c["candidate_id"] for c in candidates]
        assert ids == [f"C{i + 1}" for i in range(len(candidates))]
        kinds = {c["scenario_kind"] for c in candidates}
        assert "fortsetzung" in kinds
        assert "alternative" in kinds
        assert "spannung" in kinds
        # First candidate is always the run-end continuation
        assert candidates[0]["scenario_kind"] == "fortsetzung"
        assert candidates[0]["factor_constellation"]["F1"] == "F1.2"

    def test_llm_selection_maps_candidate_ids_to_python_constellations(self, tmp_path):
        run_dir = tmp_path / "run_sel"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        context = load_run_scenario_context("run_sel", run_dir=run_dir)
        profile = build_factor_profile(context)
        candidates = build_candidate_constellations(context, profile, {})
        chosen = [
            candidates[0]["candidate_id"],
            candidates[1]["candidate_id"],
            candidates[-1]["candidate_id"],
        ]
        constellation_by_id = {c["candidate_id"]: c["factor_constellation"] for c in candidates}

        long_story = (
            "Diese Welt entfaltet sich entlang der beobachteten Faktorlage (F1.2). "
            "Airlines reagieren auf die Nachfrage (F2.1), waehrend die Politik steuert (F6.2). "
            "Die Logik folgt klaren Wenn-Dann-Ketten und der CIB-Bewertung des Pfads."
        ) * 2

        class _MockLLM:
            def call(self, prompt: str) -> str:
                payload = {
                    "title": "Drei Zukuenfte des Luftverkehrs",
                    "summary": "Sachliche Zusammenfassung des Laufs " * 6,
                    "run_narrative": "Kompakter Laufverlauf mit Faktoren F1, F3, F6.",
                    "selection_reasoning": "Fortsetzung, Alternative und Spannung decken das Foresight-Feld ab.",
                    "scenarios": [
                        {
                            "rank": 1,
                            "candidate_id": chosen[0],
                            "title": "Kreativ-Titel A",
                            "story": long_story,
                        },
                        {
                            "rank": 2,
                            "candidate_id": chosen[1],
                            "title": "Kreativ-Titel B",
                            "story": long_story,
                        },
                        {
                            "rank": 3,
                            "candidate_id": chosen[2],
                            "title": "Kreativ-Titel C",
                            "story": long_story,
                        },
                    ],
                    "limitations": "Explorative Szenarien, keine Prognose.",
                }
                return json.dumps(payload, ensure_ascii=False)

        result = generate_run_scenario("run_sel", _MockLLM(), run_dir=run_dir, prefer_llm=True)

        assert result["source"] == "llm"
        scenarios = result["scenarios"]
        assert len(scenarios) == 3
        assert [s["title"] for s in scenarios] == [
            "Kreativ-Titel A",
            "Kreativ-Titel B",
            "Kreativ-Titel C",
        ]
        # Constellations must come verbatim from the Python candidates, not the LLM
        for scenario, cand_id in zip(scenarios, chosen):
            assert scenario["factor_constellation"] == constellation_by_id[cand_id]
        assert result["narrative"].get("selection_reasoning")

    def test_llm_thin_story_falls_back_to_template(self, tmp_path):
        run_dir = tmp_path / "run_thin"
        _write_scenario_fixture(run_dir, booking_start=0.7, booking_end=0.3)
        context = load_run_scenario_context("run_thin", run_dir=run_dir)
        profile = build_factor_profile(context)
        candidates = build_candidate_constellations(context, profile, {})
        chosen = [c["candidate_id"] for c in candidates[:3]]

        class _ThinLLM:
            def call(self, prompt: str) -> str:
                payload = {
                    "title": "Duenne Stories",
                    "summary": "Sachliche Zusammenfassung des Laufs " * 6,
                    "run_narrative": "Kompakter Laufverlauf.",
                    "scenarios": [
                        {
                            "rank": i + 1,
                            "candidate_id": cid,
                            "title": f"T{i}",
                            "story": "zu kurz",
                        }
                        for i, cid in enumerate(chosen)
                    ],
                }
                return json.dumps(payload, ensure_ascii=False)

        result = generate_run_scenario("run_thin", _ThinLLM(), run_dir=run_dir, prefer_llm=True)
        assert result["source"] == "llm"
        for scenario in result["scenarios"]:
            assert len(scenario["story"]) >= 80
            assert scenario["story"] != "zu kurz"

    def test_generate_and_save_run_scenario_integration(self, tmp_path):
        run_id = "run_int"
        run_dir = tmp_path / run_id
        _write_scenario_fixture(run_dir, booking_start=0.62, booking_end=0.58)

        result = generate_and_save_run_scenario(
            run_id,
            llm=None,
            run_dir=run_dir,
            prefer_llm=False,
        )
        assert Path(result["paths"]["markdown"]).is_file()
        assert Path(result["paths"]["json"]).is_file()
        assert result["source"] == "template"
        assert len(result["scenarios"]) == 3


class TestDieVorlageKommtVonNebenDemCode:
    """Die Vorlage für den Abschlusstext hing am Arbeitsverzeichnis (2026-09-11).

    `build_scenario_prompt` las `Path("src/prompts/run_scenario.md")` und fiel ohne
    Meldung auf einen Einzeiler zurück, wenn der Prozess nicht im
    Repo-Wurzelverzeichnis stand. Aufgefallen bei P4.6: Seit dort `src` von überall
    importierbar ist, ist der Fall erreichbar.
    """

    #: Der erste Satz der echten Vorlage — daran ist zu erkennen, dass sie ankam.
    ERSTER_SATZ = "Du schreibst **sachliche** explorative Szenarien"

    def _kontext(self, tmp_path):
        run_dir = tmp_path / "run_vorlage"
        _write_scenario_fixture(run_dir, booking_start=0.6, booking_end=0.4)
        return load_run_scenario_context("run_vorlage", run_dir=run_dir)

    def test_aus_einem_fremden_arbeitsverzeichnis_kommt_die_echte_vorlage(
        self, tmp_path, monkeypatch
    ):
        from src.reporting.run_scenario_generator import prompt as prompt_modul

        kontext = self._kontext(tmp_path)
        anderswo = tmp_path / "anderswo"
        anderswo.mkdir()
        monkeypatch.chdir(anderswo)

        text = prompt_modul.build_scenario_prompt(kontext)

        assert self.ERSTER_SATZ in text, (
            "Aus einem anderen Arbeitsverzeichnis kam die Vorlage nicht an — der "
            "Prompt beginnt mit etwas anderem als ihrem ersten Satz."
        )

    def test_eine_fehlende_vorlage_scheitert_laut(self, tmp_path, monkeypatch):
        """Kein Einzeiler an ihrer Stelle: Ein Ausfall ist sichtbar (Invariante 1)."""

        import pytest

        from src.reporting.run_scenario_generator import prompt as prompt_modul

        kontext = self._kontext(tmp_path)
        monkeypatch.setattr(prompt_modul, "VORLAGE", tmp_path / "gibt_es_nicht.md")

        with pytest.raises(FileNotFoundError):
            prompt_modul.build_scenario_prompt(kontext)


# --- Ein Lauf heisst mit Namen (P7.2-U2.3) -----------------------------------


def _mit_metadaten(run_dir, metadaten: dict) -> None:
    """Die Metadaten der Fixture ersetzen — sie setzt sonst immer denselben Namen."""

    (run_dir / "run_metadata.json").write_text(json.dumps(metadaten), encoding="utf-8")


class TestEinLaufHeisstMitNamen:
    """Q6: «Szenarien zum Lauf sweeps/sweep_transformation_conflict».

    Die Überschrift des Artefakts nahm die **Kennung**, wenn kein Name gesetzt
    war — und die Kennung eines Vergleichslaufs ist sein Ablageort.
    """

    def _kontext(self, tmp_path, run_id: str, metadaten: dict):
        from src.reporting.run_scenario_generator.context import load_run_scenario_context

        run_dir = tmp_path / "lauf"
        _write_scenario_fixture(run_dir, booking_start=0.6, booking_end=0.4)
        _mit_metadaten(run_dir, {"ticks_completed": 3, "ticks_max": 3, **metadaten})
        return load_run_scenario_context(run_id, run_dir=run_dir)

    def test_the_given_name_wins(self, tmp_path):
        from src.reporting.run_scenario_generator.context import lauf_name

        context = self._kontext(
            tmp_path,
            "sweeps/sweep_x",
            {"simulation_name": "Meine Frage", "rahmen": {"name": "Business as Usual"}},
        )

        assert lauf_name(context) == "Meine Frage"

    def test_without_a_name_the_frame_names_it(self, tmp_path):
        from src.reporting.run_scenario_generator.context import lauf_name

        context = self._kontext(
            tmp_path, "sweeps/sweep_x", {"rahmen": {"name": "Transformationskonflikt (B2 vs A1)"}}
        )

        assert lauf_name(context) == "Transformationskonflikt (B2 vs A1)"

    def test_without_both_the_identifier_loses_its_folder(self, tmp_path):
        from src.reporting.run_scenario_generator.context import lauf_name

        context = self._kontext(tmp_path, "sweeps/sweep_transformation_conflict", {})

        assert lauf_name(context) == "sweep_transformation_conflict"

    def test_no_artifact_title_shows_a_path(self, tmp_path):
        """Die Stelle, an der der Befund lag — gemessen am gerenderten Titel."""

        context = self._kontext(
            tmp_path, "sweeps/sweep_x", {"rahmen": {"name": "Business as Usual (A1+B1)"}}
        )

        payload = build_template_scenario(context)

        assert payload["title"] == "Szenarien zum Lauf Business as Usual (A1+B1)"
        assert "/" not in payload["title"]
        assert "sweeps" not in payload["summary"]

    def test_no_text_of_the_generator_writes_the_identifier(self):
        """**Gesucht, nicht aufgezählt:** jede Zeichenkette, die `run_id` einsetzt.

        `lauf_name` ist die eine Stelle, die sie noch lesen darf — und auch dort
        nur als Rückfall, ohne ihren Ordner.
        """

        import ast
        from pathlib import Path

        from src.reporting.run_scenario_generator import context as kontext_modul

        wurzel = Path(kontext_modul.__file__).resolve().parent
        befunde = []
        for pfad in sorted(wurzel.glob("*.py")):
            baum = ast.parse(pfad.read_text(encoding="utf-8"))
            for funktion in ast.walk(baum):
                if not isinstance(funktion, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if funktion.name == "lauf_name":
                    continue
                for knoten in ast.walk(funktion):
                    if not isinstance(knoten, ast.JoinedStr):
                        continue
                    for teil in knoten.values:
                        if isinstance(teil, ast.FormattedValue) and "run_id" in ast.unparse(
                            teil.value
                        ):
                            befunde.append(f"{pfad.name}:{knoten.lineno} in {funktion.name}")

        assert not befunde, "\n  ".join(
            [
                "Diese Texte setzen die Kennung ein statt des Namens:",
                *befunde,
                "`lauf_name(context)` liefert den Namen — die Kennung ist ein Ablageort.",
            ]
        )
