"""P0.6 — ein Lauf sagt, wie er entstanden ist.

Das Abnahmekriterium: Aus `run_metadata.json` allein muss erkennbar sein, mit
welchem Seed und in welchem Rechenmodus ein Lauf entstanden ist. Und ein Sweep
gegen einen toten Endpunkt muss als degradiert markiert sein und ein
`llm_incidents.json` haben — vorher schrieb der Sweep-Pfad an dieser Kette
vorbei.
"""

from __future__ import annotations

import json

import pytest

from src.config_loader import build_initial_state
from src.llm.defaults import DEFAULT_BASE_URL
from src.models.llm_models import LLMIncident
from src.models.run_models import RunArgs
from src.reporting.output_writer.metadata import save_run_metadata
from src.reporting.output_writer.provenance import (
    COMPUTE_MODE_LABELS,
    code_version,
    compute_mode,
    config_fingerprint,
)


def _args(**overrides) -> RunArgs:
    """Die Lauf-Argumente eines Tests — seit P3.11 **typisiert**.

    Vorher ein `SimpleNamespace`, und der Helfer nannte `llm_narrative` nicht:
    Er verliess sich auf `getattr(args, "llm_narrative", False)` in
    `provenance.py`. Genau dieser Rückfall ist der Befund von P3.11 — der Helfer
    hat ihn mitbenutzt und damit auch mitgetestet.
    """

    base = dict(
        model="llama3.2",
        base_url=DEFAULT_BASE_URL,
        temperature=0.7,
        max_tokens=2048,
        no_market=False,
        seed=None,
        mock_llm=False,
        deterministic_only=False,
        llm_narrative=False,
        simulation_name="Test",
        simulation_description="Test",
    )
    base.update(overrides)
    return RunArgs(**base)


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
        eines heißen: älter als P0.6.

        Der Fall hier — State **und** Argumente ohne Seed — erreicht keinen
        echten Lauf mehr: `SimulationRunner.run` löst den Seed vorher auf.
        Er bleibt als Zusicherung für Aufrufer stehen, die `save_run_metadata`
        ohne Runner benutzen. Dass ein *Lauf* ohne genannten Seed den
        tatsächlich benutzten festhält, prüft
        `TestDerSeedStehtImArtefakt`.
        """

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
        assert config_fingerprint(state).properties != before.properties

    def test_changed_factor_state_changes_it(self) -> None:
        state = build_initial_state()
        before = config_fingerprint(state)
        factor = state.environment.factors["F2"]
        factor.current_state = next(s for s in factor.possible_states if s != factor.current_state)
        assert config_fingerprint(state).factors != before.factors

    def test_changed_permission_changes_it(self) -> None:
        """Die Berechtigungen aus P0.5 gehören zur Herkunft eines Laufs."""

        state = build_initial_state()
        before = config_fingerprint(state)
        regulator = next(agent for agent in state.agents if agent.id == "regulator")
        regulator.profile.may_propose = [*regulator.profile.may_propose, "factor_state F4"]
        assert config_fingerprint(state).agent_profiles != before.agent_profiles

    def test_consistency_score_does_not_change_it(self) -> None:
        """Der Wert wird *nach* dem Lauf in die Matrix geschrieben. Er
        beschreibt das Ergebnis, nicht die Eingabe."""

        state = build_initial_state()
        before = config_fingerprint(state)
        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        state.cib_matrix.metadata["consistency_score"] = 0.87
        assert config_fingerprint(state).cib_matrix == before.cib_matrix


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

    def test_sweep_names_its_own_mode(self) -> None:
        """Der Sweep rechnet deterministisch, erzeugt den Szenariotext aber mit
        `prefer_llm=True` — er ist keines von beidem.

        Vorher stand hier `compute_mode(args) == "llm"`, weil `deterministic_only`
        behauptet hätte, es sei kein Modell beteiligt gewesen. Das war die
        Gegenrichtung desselben Fehlers: Das Dashboard zeigte «Mit
        Sprachmodell» für einen Lauf, an dessen Zahlen keines beteiligt ist.
        """

        from src.orchestration.scenario_sweeps import SWEEP_SEED, sweep_metadata_args

        args = sweep_metadata_args("demo")
        assert compute_mode(args) == "deterministic_with_llm_narrative"
        assert args.seed == SWEEP_SEED

    def test_sweep_names_the_model_it_actually_asks(self) -> None:
        """`dummy_for_sweeps` benannte ein Modell, das es nicht gibt. Befragt
        wird das aus `OllamaConfig` — dasselbe, das der Sweep-Pfad für den
        Abschlusstext instanziiert."""

        from src.llm import OllamaConfig
        from src.orchestration.scenario_sweeps import sweep_metadata_args

        args = sweep_metadata_args("demo")
        assert args.model == OllamaConfig().model
        assert args.base_url == OllamaConfig().base_url

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
        before = config_fingerprint(state).cib_matrix

        if state.cib_matrix.metadata is None:
            state.cib_matrix.metadata = {}
        for key in RUN_PRODUCED_MATRIX_METADATA:
            state.cib_matrix.metadata[key] = {"irgendwas": "aus diesem Lauf"}

        assert config_fingerprint(state).cib_matrix == before

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


class TestMultiRunTraegtDenRechenmodus:
    """Gegenprobe 2026-08-27: `build_run_args` ließ sich `mock_llm` entziehen,
    ohne dass ein Test rot wurde — dann verlöre jeder Teillauf eines Multi-Runs
    seinen Rechenmodus."""

    def test_run_args_carry_the_compute_mode(self) -> None:
        from src.run_simulation import build_run_args

        base = _args(mock_llm=True, deterministic_only=False)
        built = build_run_args(base, run_index=2, seed=77)
        assert compute_mode(built) == "mock_llm"
        assert built.seed == 77

    def test_metadata_of_a_sub_run_says_mock(self, tmp_path) -> None:
        from src.run_simulation import build_run_args

        state = build_initial_state()
        state.config.seed = 78
        metadata = _write(
            tmp_path, state, build_run_args(_args(mock_llm=True), run_index=2, seed=78)
        )
        assert metadata["compute_mode"] == "mock_llm"
        assert metadata["seed"] == 78


class TestDasDashboardZeigtDieHerkunft:
    """Die Ansicht war von keinem Test berührt — dieselbe Lücke, die die dritte
    Nachprüfung von P0.3 für den Start-Callback gefunden hat."""

    @staticmethod
    def _render(tmp_path, metadata: dict) -> str:
        from dashboard.web.views import overview

        (tmp_path / "run_metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
        )
        return str(overview.render(tmp_path, "run_test"))

    def test_mode_and_seed_are_shown(self, tmp_path) -> None:
        rendered = self._render(
            tmp_path,
            {"compute_mode": "llm", "seed": 4242, "model": "llama3.2", "ticks_completed": 3},
        )
        assert "Mit Sprachmodell" in rendered
        assert "4242" in rendered

    def test_mock_run_carries_a_hint(self, tmp_path) -> None:
        """Ein Lauf ohne Sprachmodell darf nicht wie ein vollwertiger aussehen."""

        rendered = self._render(
            tmp_path, {"compute_mode": "mock_llm", "seed": 1, "model": "llama3.2"}
        )
        assert "Ohne Sprachmodell (Mock)" in rendered
        assert "ohne Sprachmodell entstanden" in rendered

    def test_mock_run_does_not_claim_a_model(self, tmp_path) -> None:
        """Gegenprobe-Fund: Die Kachel «Modell» zeigte `llama3.2` auch bei einem
        Mock-Lauf — der Modellname steht in den Argumenten, auch wenn nie
        gefragt wurde."""

        rendered = self._render(
            tmp_path, {"compute_mode": "mock_llm", "seed": 1, "model": "llama3.2"}
        )
        assert "llama3.2" not in rendered

    def test_llm_run_still_names_its_model(self, tmp_path) -> None:
        rendered = self._render(tmp_path, {"compute_mode": "llm", "seed": 1, "model": "llama3.2"})
        assert "llama3.2" in rendered

    def test_old_run_says_so_instead_of_inventing(self, tmp_path) -> None:
        """Läufe von vor P0.6 kennen die Felder nicht."""

        rendered = self._render(tmp_path, {"ticks_completed": 3, "model": "llama3.2"})
        assert "nicht festgehalten" in rendered


# --- Gegenprobe zur Gegenprobe (2026-08-27) ---------------------------------
#
# Drei Zusagen von P0.6 hielten am laufenden System nicht, und keine davon
# hätte ein Test bemerkt: Die Tests riefen `config_fingerprint` und
# `save_run_metadata` direkt und reichten den Zustand selbst hinein. Geprüft
# war damit die Funktion, nicht der Weg dorthin — dasselbe Muster, das die
# erste Gegenprobe bei den Shift-Regeln gefunden hat. Die folgenden Tests
# fahren deshalb einen echten Lauf.


class _StummesLLM:
    """Antwortet gültig und ohne Inhalt — die Zahlen entstehen ohnehin in Python."""

    def call(self, prompt: str) -> str:
        return (
            '{"reasoning": "", "actions": [], "state_changes": [], '
            '"events": [], "segment_analysis": {}}'
        )


def _lauf(*, seed=None, ticks: int = 4):
    """Ein vollständiger Lauf über den Runner — der Weg, den die Tests bisher umgingen."""

    from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

    state = build_initial_state()
    state.clock.max_ticks = ticks
    runner = SimulationRunner(
        llm=_StummesLLM(),
        options=RunnerOptions(
            enable_market=True,
            enable_cib=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )
    return runner.run(state, seed=seed, run_id="run_test")


class TestDerFingerabdruckBeschreibtDieEingabe:
    """Er wurde am Ende genommen und hat den Lauf mitgehasht.

    Gemessen an zwei echten Läufen derselben Konfiguration mit den Seeds 1
    und 2: vier Komponenten gleich, `factors` verschieden. Grund war nicht
    die Formel, sondern der Zeitpunkt — `factors` trägt den Zustand jedes
    Deskriptors, und den verschiebt der Lauf. Damit beantwortete der
    Fingerabdruck genau die Frage nicht mehr, für die er da ist.
    """

    def test_two_runs_of_one_config_share_it(self, tmp_path) -> None:
        """Der Befund selbst — und bewusst über das Artefakt geprüft.

        Die erste Fassung verglich `final.config_fingerprint` der beiden Läufe
        direkt. Beim Abschalten des Fixes blieb sie grün: Ohne ihn ist das Feld
        auf beiden Seiten `None`, und `None == None` hält. Ein Test, der nur
        greift, solange der Code funktioniert, ist keiner. Über
        `save_run_metadata` fällt der fehlende Wert dagegen auf den am Ende
        genommenen Abdruck zurück — und der geht auseinander.
        """

        erster = _write(tmp_path / "a", _lauf(seed=1), _args(seed=1))
        zweiter = _write(tmp_path / "b", _lauf(seed=2), _args(seed=2))

        assert erster["config_fingerprint"] == zweiter["config_fingerprint"]
        assert erster["seed"] != zweiter["seed"]

    def test_der_lauf_verschiebt_die_faktoren_ueberhaupt(self) -> None:
        """Der Kontrolltest zum vorigen — und er ist nicht redundant.

        **Die Achse hat sich mit P2.1 geändert, und das ist selbst ein Befund.**
        Vorher stand hier: Zwei Läufe *mit verschiedenen Seeds* enden in
        verschiedenen Faktorzuständen. Das galt, solange die Buchung eine
        Schwelle war — dann hing das Ergebnis an der Zusammensetzung der
        gezogenen Bevölkerung, und ein anderer Seed hieß eine andere Rate.

        Mit der echten Ziehung mitteln sich die Einzelentscheidungen über tausend
        Personen aus: Nachgemessen landen die Seeds 1, 2 und 3 nach 10, 15 und 20
        Ticks auf **denselben** Faktorzuständen. Der alte Kontrolltest wäre damit
        rot geworden, ohne dass am Fingerabdruck etwas falsch ist.

        Worauf es ankommt, ist ohnehin etwas anderes: dass der Lauf die Faktoren
        **überhaupt bewegt**. Nur dann hasht ein am Ende genommener Abdruck das
        Ergebnis mit — und genau das belegt der Test darunter. Vier Ticks
        genügten dafür nie; bei fünfzehn bewegen sich vier der sieben.
        """

        start = {k: v.current_state for k, v in build_initial_state().environment.factors.items()}
        ende = {k: v.current_state for k, v in _lauf(seed=1, ticks=15).environment.factors.items()}

        bewegt = sorted(k for k in start if start[k] != ende[k])
        assert bewegt, (
            "Kein Faktor hat sich im Lauf bewegt — dann hasht auch ein am Ende "
            "genommener Fingerabdruck nichts vom Ergebnis, und der Test darunter "
            "wäre aus dem falschen Grund grün."
        )

    def test_the_old_way_would_have_differed(self) -> None:
        """Und dass der alte Weg wirklich der Fehler war: derselbe Abdruck,
        am Ende genommen, weicht vom Abdruck am Anfang ab."""

        am_anfang = config_fingerprint(build_initial_state())
        am_ende = config_fingerprint(_lauf(seed=1, ticks=15))

        assert am_ende.factors != am_anfang.factors, (
            "Der am Ende genommene Abdruck stimmt mit dem am Anfang überein — "
            "dann trüge `factors` den Laufzustand nicht mehr, und der Fix von "
            "2026-08-27 wäre gegenstandslos geworden."
        )

    def test_it_is_taken_before_the_first_tick(self) -> None:
        final = _lauf(seed=1)
        assert final.config_fingerprint == config_fingerprint(build_initial_state())

    def test_a_changed_start_state_still_changes_it(self) -> None:
        """Der naheliegende Fix — `current_state` einfach weglassen — wäre
        falsch gewesen: Der **Start**zustand ist eine Eingabe, jeder Sweep
        setzt ihn über `FactorOverride.initial_state`."""

        from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

        state = build_initial_state()
        state.clock.max_ticks = 1
        factor = state.environment.factors["F2"]
        factor.current_state = next(s for s in factor.possible_states if s != factor.current_state)

        runner = SimulationRunner(
            llm=_StummesLLM(),
            options=RunnerOptions(deterministic_only=True, checkpoint_interval=0),
        )
        verschoben = runner.run(state, seed=1, run_id="run_test")

        assert (
            verschoben.config_fingerprint.factors
            != _lauf(seed=1, ticks=1).config_fingerprint.factors
        )

    def test_a_resumed_run_keeps_the_original(self) -> None:
        """Beim Fortsetzen sind die Faktoren des Checkpoints bereits Ergebnis.
        Neu berechnen hieße, das Ergebnis zur Eingabe zu erklären.

        **16 Ticks, nicht die vier der anderen Tests.** Die erste Fassung lief
        über `_lauf(seed=1)`, und bei vier Ticks steht kein Faktor anders als
        beim Start — dann liefert ein Neuberechnen zufällig dasselbe, und der
        Test bleibt grün, auch wenn der Runner den Abdruck beim Fortsetzen
        verwirft. Gefunden bei der Mutationsprüfung am 2026-08-27: dieselbe
        Schwäche wie die `None == None`-Falle eine Zeile weiter oben, nur
        anders verkleidet. Die Vorbedingung steht deshalb jetzt als eigene
        Zusicherung im Test.
        """

        from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

        fremd = config_fingerprint(build_initial_state())
        final = _lauf(seed=1, ticks=16)
        assert final.config_fingerprint == fremd

        bewegt = config_fingerprint(final).factors != fremd.factors
        assert bewegt, (
            "die Faktoren stehen nach dem Lauf noch auf dem Startzustand — dann "
            "zeigt dieser Test nichts, weil Neuberechnen dasselbe ergäbe"
        )

        # Zustand mit gesetztem Feld erneut durch den Runner: bleibt stehen.
        final.clock.max_ticks = final.clock.current_tick + 1
        runner = SimulationRunner(
            llm=_StummesLLM(),
            options=RunnerOptions(deterministic_only=True, checkpoint_interval=0),
        )
        fortgesetzt = runner.run(final, seed=1, run_id="run_test")
        assert fortgesetzt.config_fingerprint == fremd

    def test_the_artifact_carries_the_recorded_one(self, tmp_path) -> None:
        """Der Weg bis in die Datei — nicht nur das Feld im State."""

        final = _lauf(seed=1)
        metadata = _write(tmp_path, final, _args(seed=1))
        assert (
            metadata["config_fingerprint"] == config_fingerprint(build_initial_state()).model_dump()
        )


class TestDerSeedStehtImArtefakt:
    """`seed: null` bei jedem Standardlauf — obwohl der Lauf reproduzierbar war.

    `configs/simulation_config.json` nennt keinen Seed, also schrieb das
    Artefakt `null` und das Dashboard zeigte «nicht festgehalten». Gezogen
    wurde trotzdem reproduzierbar: `environment_node` fiel still auf 42
    zurück. Zwei Wiederholungen waren bitgleich, während die Oberfläche den
    Lauf «frei» nannte. Das Abnahmekriterium von P0.6 verlangt das Gegenteil.
    """

    def test_a_run_without_a_configured_seed_records_the_one_it_used(self, tmp_path) -> None:
        from src.models.state_models import DEFAULT_SEED

        final = _lauf(seed=None)
        metadata = _write(tmp_path, final, _args(seed=None))

        assert metadata["seed"] == DEFAULT_SEED

    def test_an_explicit_seed_still_wins(self, tmp_path) -> None:
        metadata = _write(tmp_path, _lauf(seed=4711), _args(seed=None))
        assert metadata["seed"] == 4711

    def test_two_runs_without_a_seed_are_identical(self) -> None:
        """Die Zusage, die die Oberfläche jetzt macht — gemessen, nicht behauptet."""

        erster = _lauf(seed=None)
        zweiter = _lauf(seed=None)

        assert [entry.model_dump() for entry in erster.price_history] == [
            entry.model_dump() for entry in zweiter.price_history
        ]
        assert erster.population_stats == zweiter.population_stats

    def test_the_default_seed_has_exactly_one_source(self) -> None:
        """Die 42 stand als Literal in `environment_node` und nirgends sonst.

        Genau deshalb kannte das Artefakt sie nicht: Sie war eine lokale
        Notlösung, kein benannter Standard.
        """

        from pathlib import Path

        quelle = Path("src/orchestration/environment_node.py").read_text(encoding="utf-8")
        assert "DEFAULT_SEED" in quelle
        assert "else 42" not in quelle

    def test_the_fallback_really_is_the_constant(self) -> None:
        """Und zwar dem Verhalten nach, nicht nur dem Wortlaut.

        Die Prüfung darüber liest den Quelltext — sie hält fest, dass dort
        `DEFAULT_SEED` steht und keine 42 mehr. Bei der Mutationsprüfung am
        2026-08-27 fiel auf: Ein `else 999` erfüllt beide Zusicherungen und
        blieb grün. Der Rückfall gilt den Aufrufern, die den Node **ohne**
        Runner benutzen (Studio, Tests) — für die zählt der Wert, nicht das
        Wort. Gemessen wird deshalb an der gezogenen Bevölkerung.
        """

        from src.models.state_models import DEFAULT_SEED
        from src.orchestration.environment_node import EnvironmentNode

        def erste_person(seed):
            state = build_initial_state()
            state.config.seed = seed
            state.clock.current_tick = 1
            gelaufen = EnvironmentNode().invoke(state)
            return gelaufen.population_individuals[0]

        ohne = erste_person(None)
        mit = erste_person(DEFAULT_SEED)
        assert (ohne.wtp_eur, ohne.environmental_awareness) == (
            mit.wtp_eur,
            mit.environmental_awareness,
        )

    def test_the_dashboard_does_not_call_an_unseeded_run_free(self) -> None:
        """Der Editor nannte einen Lauf ohne eigenen Startwert «frei» und
        versprach abweichende Wiederholungen. Beides war gemessen falsch."""

        from pathlib import Path

        # Der Text stand bis P1.1 im Tab «Kontrolle»; seither steht er im
        # Preflight des geführten Ablaufs. Der Wächter zieht mit, sonst prüfte
        # er eine Datei, die es nicht mehr gibt.
        quelle = Path("dashboard/web/config_editor/start_flow.py").read_text(encoding="utf-8")
        assert '"frei"' not in quelle
        assert "DEFAULT_SEED" in quelle


class TestDerDashboardPfadMeldetDenBenutztenSeed:
    """Der Weg über `launch_simulation`, nicht nur über den Runner.

    Gefunden bei der Mutationsprüfung am 2026-08-27: `run_launcher` ließ sich
    auf `config.seed` zurückdrehen — den **angeforderten** Wert, der leer
    bleibt, wenn niemand einen nennt — ohne dass ein Test rot wurde. Dass der
    Runner den Seed auflöst, prüfte `TestDerSeedStehtImArtefakt`; dass die
    Oberfläche den aufgelösten weiterreicht, niemand.
    """

    def test_a_dashboard_run_without_a_seed_records_the_default(self, tmp_path) -> None:
        from dashboard.run_launcher import RunLaunchConfig, launch_simulation
        from src.models.state_models import DEFAULT_SEED

        ergebnis = launch_simulation(
            RunLaunchConfig(
                rounds=1,
                seed=None,
                mock_llm=True,
                deterministic_only=True,
                checkpoint_interval=0,
                no_protocol=True,
                no_scenarios=True,
                generate_figures=False,
                run_id=f"seedprobe_{tmp_path.name}",
            )
        )
        metadata = json.loads((ergebnis.run_dir / "run_metadata.json").read_text(encoding="utf-8"))
        assert metadata["seed"] == DEFAULT_SEED


class TestDerHybridModusDesSweeps:
    """Ein Sweep ist weder «Mit Sprachmodell» noch «Nur Zahlen».

    P0.6 setzte `deterministic_only=False`, damit das Artefakt nicht behauptet,
    es sei kein Modell beteiligt gewesen. Damit behauptete es die Gegenrichtung:
    Das Dashboard zeigte «Mit Sprachmodell» und «Modell: dummy_for_sweeps» für
    einen Lauf, dessen Ticks mit `RunnerOptions(deterministic_only=True)`
    gerechnet werden. Beide Angaben waren unwahr.
    """

    def test_the_sweep_computes_its_ticks_deterministically(self) -> None:
        """Der Beleg für die Prämisse — sonst stritte der Test über nichts.

        **Geprüft wird die Zusage, nicht ihre Schreibweise** (angepasst mit
        P1.9-W1.1). Vorher stand hier die Textsuche `"deterministic_only=True"
        in optionen` über dem Quelltext des Runner-Baus. Sie ist gebrochen, als
        W1.1 den Wert aus dem Vertrag `FESTLEGUNGEN` zog statt ihn als Literal
        hinzuschreiben — die zugesagte Eigenschaft galt unverändert, nur die
        Buchstaben hatten sich verschoben.

        Der Vertrag ist jetzt die load-bearing Stelle: `run_single_sweep` liest
        ihn, und `tests/test_web_wirkung.py` hält fest, dass er das tut. Hier
        wird deshalb der Vertrag befragt.
        """

        from pathlib import Path

        from src.orchestration.scenario_sweeps import festlegung_fuer

        festlegung = festlegung_fuer("deterministic_only")
        assert festlegung is not None, "Der Sweep-Vertrag sagt nichts mehr über den Rechenmodus"
        assert festlegung.wert is True, (
            "Der Sweep rechnet seine Ticks nicht mehr deterministisch — dann trägt "
            "dieser ganze Abschnitt über den Hybrid-Modus nicht mehr."
        )

        quelle = Path("src/orchestration/scenario_sweeps.py").read_text(encoding="utf-8")
        assert "prefer_llm=True" in quelle

    def test_the_mode_says_both_halves(self) -> None:
        from src.orchestration.scenario_sweeps import sweep_metadata_args

        modus = compute_mode(sweep_metadata_args("demo"))
        label = COMPUTE_MODE_LABELS[modus]
        assert "Nur Zahlen" in label
        assert "Modell" in label

    def test_degradation_does_not_depend_on_the_mode(self, tmp_path) -> None:
        """Die Begründung für die gebeugte Angabe trägt nicht: `degraded`
        kommt allein aus den Vorfällen, nicht aus dem Rechenmodus."""

        state = build_initial_state()
        state.llm_incidents.append(
            LLMIncident(tick=3, caller="run_scenario_generator", kind="call_failed", error="tot")
        )
        from src.orchestration.scenario_sweeps import sweep_metadata_args

        metadata = _write(tmp_path, state, sweep_metadata_args("demo"))
        assert metadata["compute_mode"] == "deterministic_with_llm_narrative"
        assert metadata["degraded"] is True

    def test_the_dashboard_separates_the_two_halves(self, tmp_path) -> None:
        rendered = TestDasDashboardZeigtDieHerkunft._render(
            tmp_path,
            {
                "compute_mode": "deterministic_with_llm_narrative",
                "seed": 42,
                "model": "llama3.2",
            },
        )
        # Der Text ist da: die Zahlen deterministisch, das Modell nur am Schluss.
        assert "rein deterministisch" in rendered
        # Und das Modell wird genannt — es *wurde* eines befragt.
        assert "llama3.2" in rendered
        assert "keins" not in rendered


class TestDerCodestandFriertNichtEin:
    """Das Dashboard läuft als ein Prozess über Stunden. Ein `lru_cache` hätte
    Commit und `dirty` beim Prozessstart festgehalten, und jeder spätere Lauf
    trüge den Codestand von damals."""

    def test_code_version_is_not_cached(self) -> None:
        from src.reporting.output_writer import provenance

        assert not hasattr(provenance.code_version, "cache_info")

    def test_a_second_call_asks_git_again(self, monkeypatch) -> None:
        from src.reporting.output_writer import provenance

        aufrufe: list[tuple[str, ...]] = []
        echtes_run = provenance.subprocess.run

        def zaehlend(args, **kwargs):
            aufrufe.append(tuple(args))
            return echtes_run(args, **kwargs)

        monkeypatch.setattr(provenance.subprocess, "run", zaehlend)
        provenance.code_version()
        erste_runde = len(aufrufe)
        provenance.code_version()

        assert erste_runde > 0
        assert len(aufrufe) > erste_runde


class TestDasArtefaktBehauptetKeinModell:
    """Die vierte Runde (2026-08-27) fand den Rest eines Befunds der ersten.

    Die erste Gegenprobe sah «Modell llama3.2» neben «Rechenmodus: Ohne
    Sprachmodell» und meldete den Widerspruch als behoben. Behoben war er
    aber nur in `views/overview.py::_model_label`, also in **einer**
    Oberflächenkachel — `save_run_metadata` schrieb `args.model` weiterhin
    unbedingt. Die Zusage von P0.6 lautet «aus `run_metadata.json` **allein**»;
    wer die Datei ohne Dashboard las, bekam vier Angaben über ein Modell, das
    nie gefragt wurde. Dasselbe Muster wie die Testlücken beider Gegenproben:
    geprüft war die Anzeige, nicht der Weg dorthin.
    """

    def test_a_mock_run_names_no_model(self, tmp_path) -> None:
        state = build_initial_state()
        metadata = _write(tmp_path, state, _args(mock_llm=True))

        assert metadata["compute_mode"] == "mock_llm"
        for feld in ("model", "base_url", "temperature", "max_tokens"):
            assert metadata[feld] is None, f"{feld} beschreibt ein Modell, das nie gefragt wurde"

    def test_a_numbers_only_run_names_no_model(self, tmp_path) -> None:
        state = build_initial_state()
        metadata = _write(tmp_path, state, _args(deterministic_only=True))

        assert metadata["compute_mode"] == "deterministic_only"
        assert metadata["model"] is None

    def test_the_keys_stay_in_the_file(self, tmp_path) -> None:
        """`null` statt Weglassen: Das Schema bleibt gleich, und ein fehlender
        Schlüssel kann weiterhin nur eines heissen — älter als P0.6."""

        state = build_initial_state()
        metadata = _write(tmp_path, state, _args(mock_llm=True))

        for feld in ("model", "base_url", "temperature", "max_tokens"):
            assert feld in metadata

    def test_a_real_run_still_names_its_model(self, tmp_path) -> None:
        """Die Gegenrichtung — sonst prüfte der Test nur, dass etwas fehlt."""

        state = build_initial_state()
        metadata = _write(tmp_path, state, _args())

        assert metadata["compute_mode"] == "llm"
        assert metadata["model"] == "llama3.2"
        assert metadata["base_url"] == DEFAULT_BASE_URL
        assert metadata["temperature"] == 0.7
        assert metadata["max_tokens"] == 2048

    def test_the_sweep_keeps_its_model(self, tmp_path) -> None:
        """Ein Sweep rechnet deterministisch, lässt den Abschlusstext aber vom
        Modell schreiben. Dort *war* eines beteiligt — der Name bleibt."""

        from src.orchestration.scenario_sweeps import sweep_metadata_args

        state = build_initial_state()
        metadata = _write(tmp_path, state, sweep_metadata_args("demo"))

        assert metadata["compute_mode"] == "deterministic_with_llm_narrative"
        assert metadata["model"] is not None
