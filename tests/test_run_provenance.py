"""P0.6 — ein Lauf sagt, wie er entstanden ist.

Das Abnahmekriterium: Aus `run_metadata.json` allein muss erkennbar sein, mit
welchem Seed und in welchem Rechenmodus ein Lauf entstanden ist. Und ein Sweep
gegen einen toten Endpunkt muss als degradiert markiert sein und ein
`llm_incidents.json` haben — vorher schrieb der Sweep-Pfad an dieser Kette
vorbei.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from src.config_loader import build_initial_state
from src.models.llm_models import LLMIncident
from src.reporting.output_writer.metadata import save_run_metadata
from src.reporting.output_writer.provenance import (
    COMPUTE_MODE_LABELS,
    code_version,
    compute_mode,
    config_fingerprint,
)


def _args(**overrides) -> SimpleNamespace:
    base = dict(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.7,
        max_tokens=2048,
        no_market=False,
        seed=None,
        mock_llm=False,
        deterministic_only=False,
        simulation_name="Test",
        simulation_description="Test",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _write(tmp_path, state, args) -> dict:
    save_run_metadata(state, args, run_dir=tmp_path, run_id="run_test")
    return json.loads((tmp_path / "run_metadata.json").read_text(encoding="utf-8"))


class TestRechenmodus:
    @pytest.mark.parametrize(
        ("flags", "expected"),
        [
            ({}, "llm"),
            ({"mock_llm": True}, "mock_llm"),
            ({"deterministic_only": True}, "deterministic_only"),
            # Beides gesetzt: `deterministic_only` ist der striktere Modus.
            ({"mock_llm": True, "deterministic_only": True}, "deterministic_only"),
        ],
    )
    def test_compute_mode(self, flags: dict, expected: str) -> None:
        assert compute_mode(_args(**flags)) == expected

    def test_every_mode_has_a_label(self) -> None:
        """Das Dashboard zeigt den Modus im Klartext — kein Modus darf dort als
        Rohwert auftauchen."""

        for flags in ({}, {"mock_llm": True}, {"deterministic_only": True}):
            assert compute_mode(_args(**flags)) in COMPUTE_MODE_LABELS

    def test_mock_run_is_recorded_but_not_degraded(self, tmp_path) -> None:
        """Ein bewusster Mock-Lauf ist kein Ausfall (P0.1) — aber er muss als
        Mock-Lauf erkennbar sein (P0.6)."""

        state = build_initial_state()
        metadata = _write(tmp_path, state, _args(mock_llm=True))
        assert metadata["mock_llm"] is True
        assert metadata["compute_mode"] == "mock_llm"
        assert metadata["degraded"] is False


class TestSeed:
    def test_seed_from_state_wins(self, tmp_path) -> None:
        """Der State trägt den tatsächlich benutzten Seed; `args.seed` ist bei
        einem Multi-Run nur der Ausgangswert der Folge."""

        state = build_initial_state()
        state.config.seed = 4711
        metadata = _write(tmp_path, state, _args(seed=42))
        assert metadata["seed"] == 4711

    def test_seed_falls_back_to_args(self, tmp_path) -> None:
        state = build_initial_state()
        state.config.seed = None
        metadata = _write(tmp_path, state, _args(seed=42))
        assert metadata["seed"] == 42

    def test_seed_field_exists_even_without_one(self, tmp_path) -> None:
        """Das Feld steht immer in der Datei. Seine Abwesenheit kann damit nur
        eines heißen: älter als P0.6."""

        state = build_initial_state()
        state.config.seed = None
        metadata = _write(tmp_path, state, _args(seed=None))
        assert "seed" in metadata
        assert metadata["seed"] is None


class TestFingerabdruck:
    def test_same_config_same_fingerprint(self) -> None:
        assert config_fingerprint(build_initial_state()) == config_fingerprint(
            build_initial_state()
        )

    def test_seed_does_not_change_it(self) -> None:
        """Zwei Läufe derselben Konfiguration müssen denselben Fingerabdruck
        tragen — sonst beantwortet er die Frage nicht, für die er da ist. Der
        Seed steht als eigenes Feld daneben."""

        first = build_initial_state()
        second = build_initial_state()
        second.config.seed = 999
        assert config_fingerprint(first) == config_fingerprint(second)

    def test_changed_properties_change_it(self) -> None:
        state = build_initial_state()
        before = config_fingerprint(state)
        state.properties.price_model.base_price += 1.0
        assert config_fingerprint(state)["properties"] != before["properties"]

    def test_changed_factor_state_changes_it(self) -> None:
        state = build_initial_state()
        before = config_fingerprint(state)
        factor = state.environment.factors["F2"]
        factor.current_state = next(s for s in factor.possible_states if s != factor.current_state)
        assert config_fingerprint(state)["factors"] != before["factors"]

    def test_changed_permission_changes_it(self) -> None:
        """Die Berechtigungen aus P0.5 gehören zur Herkunft eines Laufs."""

        state = build_initial_state()
        before = config_fingerprint(state)
        regulator = next(agent for agent in state.agents if agent.id == "regulator")
        regulator.profile.may_propose = [*regulator.profile.may_propose, "factor_state F4"]
        assert config_fingerprint(state)["agent_profiles"] != before["agent_profiles"]

    def test_consistency_score_does_not_change_it(self) -> None:
        """Der Wert wird *nach* dem Lauf in die Matrix geschrieben. Er
        beschreibt das Ergebnis, nicht die Eingabe."""

        state = build_initial_state()
        before = config_fingerprint(state)
        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        state.cib_matrix.metadata["consistency_score"] = 0.87
        assert config_fingerprint(state)["cib_matrix"] == before["cib_matrix"]


class TestCodestand:
    def test_code_version_is_a_commit_or_none(self) -> None:
        """Ohne Git ist die Herkunft nicht feststellbar — dann `None`, statt
        eine zu behaupten, die niemand prüfen kann."""

        version = code_version()
        if version is None:
            pytest.skip("kein Git-Repository verfügbar")
        assert len(version["commit"]) == 40
        assert isinstance(version["dirty"], bool)

    def test_metadata_carries_the_field(self, tmp_path) -> None:
        metadata = _write(tmp_path, build_initial_state(), _args())
        assert "code_version" in metadata


class TestSweepSchreibtNichtMehrVorbei:
    """Der Sweep-Pfad lief bis P0.6 an der Kette aus P0.1 vorbei."""

    def test_metadata_is_written_after_the_scenario(self) -> None:
        """Reihenfolge im Quelltext: Erst der Vorfall, dann die Metadaten.
        Andersherum kann `degraded` den Ausfall gar nicht mehr sehen."""

        from pathlib import Path

        source = Path("src/orchestration/scenario_sweeps.py").read_text(encoding="utf-8")
        scenario_at = source.index("scenario_result = generate_and_save_run_scenario")
        incidents_at = source.index("save_llm_incidents(final_state.llm_incidents")
        metadata_at = source.index("save_run_metadata(final_state, dummy_args")
        assert scenario_at < incidents_at < metadata_at

    def test_sweep_seed_is_one_constant(self) -> None:
        """Der Seed stand zweimal als Literal — einmal im Lauf, einmal in den
        Metadaten, die ihn behaupteten."""

        from src.orchestration.scenario_sweeps import SWEEP_SEED

        assert isinstance(SWEEP_SEED, int)

    def test_sweep_does_not_claim_deterministic_only(self) -> None:
        """Der Sweep rechnet deterministisch, erzeugt den Szenariotext aber mit
        `prefer_llm=True`. `deterministic_only` im Artefakt hätte behauptet, es
        sei kein Modell beteiligt gewesen."""

        from src.orchestration.scenario_sweeps import SWEEP_SEED, sweep_metadata_args

        args = sweep_metadata_args("demo")
        assert compute_mode(args) == "llm"
        assert args.seed == SWEEP_SEED

    def test_incident_marks_the_run_degraded(self, tmp_path) -> None:
        """Der Kern: Ein Ausfall im Szenariotext muss den Sweep als degradiert
        markieren. Vorher stand dort `degraded: false`, und der einzige Hinweis
        war `"source": "template"` in `run_scenario.json`."""

        state = build_initial_state()
        state.llm_incidents.append(
            LLMIncident(
                tick=state.clock.current_tick,
                caller="run_scenario_generator",
                kind="call_failed",
                error="connection refused",
            )
        )
        metadata = _write(tmp_path, state, _args(deterministic_only=True))
        assert metadata["degraded"] is True
        assert metadata["llm_incident_count"] == 1


class TestDerFingerabdruckWandertNicht:
    """Die Matrix wird *während* eines Laufs beschrieben. Was dabei entsteht,
    darf den Fingerabdruck nicht bewegen — sonst hätten zwei Läufe derselben
    Konfiguration verschiedene, und er beantwortete seine eigene Frage nicht.
    """

    def test_run_produced_metadata_is_ignored(self) -> None:
        from src.reporting.output_writer.provenance import RUN_PRODUCED_MATRIX_METADATA

        state = build_initial_state()
        before = config_fingerprint(state)["cib_matrix"]

        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        for key in RUN_PRODUCED_MATRIX_METADATA:
            state.cib_matrix.metadata[key] = {"irgendwas": "aus diesem Lauf"}

        assert config_fingerprint(state)["cib_matrix"] == before

    def test_every_run_written_key_is_declared(self) -> None:
        """Der Wächter: Wer einen neuen Schlüssel in `cib_matrix.metadata`
        schreibt, muss ihn hier eintragen. Sonst wandert der Fingerabdruck
        wieder still — genau die Sorte Drift, die diese Phase abräumt.
        """

        import re
        from pathlib import Path

        from src.reporting.output_writer.provenance import RUN_PRODUCED_MATRIX_METADATA

        written: set[str] = set()
        for path in Path("src").rglob("*.py"):
            if "legacy" in path.parts:
                continue
            for match in re.finditer(
                r"cib_matrix\.metadata\[[\"']([a-z_]+)[\"']\]\s*=",
                path.read_text(encoding="utf-8"),
            ):
                written.add(match.group(1))

        assert written, "kein einziger Schreibzugriff gefunden — Muster veraltet?"
        undeclared = written - RUN_PRODUCED_MATRIX_METADATA
        assert not undeclared, (
            f"Diese Schlüssel schreibt ein Lauf in die Matrix, ohne dass der "
            f"Fingerabdruck sie kennt: {sorted(undeclared)}"
        )
