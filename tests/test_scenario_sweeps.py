"""Tests for M8 Scenario Sweeps."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.models.sweep_models import FactorOverride, MilestoneCheck, PropertyOverride, SweepConfig
from src.orchestration.scenario_sweeps import (
    apply_sweep_overrides,
    load_sweep_config,
    run_single_sweep,
)
from src.orchestration.simulation_runner import RunnerOptions, SimulationRunner

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------


def test_sweep_config_loading():
    """All sweep JSON files in configs/sweeps/ should parse correctly."""
    sweeps_dir = REPO_ROOT / "configs" / "sweeps"
    configs = list(sweeps_dir.glob("*.json"))
    assert len(configs) >= 4, f"Expected at least 4 sweep configs, found {len(configs)}"

    for path in configs:
        config = load_sweep_config(path)
        assert config.id, f"Sweep {path.name} has no id"
        assert config.name, f"Sweep {path.name} has no name"
        assert config.max_ticks > 0, f"Sweep {path.name} has invalid max_ticks"


def test_apply_property_overrides():
    """Property overrides should modify state trajectory baselines and rules."""
    state = build_initial_state(load_cib=False)

    sweep = SweepConfig(
        id="test",
        name="Test",
        description="Test sweep",
        max_ticks=10,
        property_overrides=[
            PropertyOverride(
                property_id="carbon_tax_level",
                baseline=99.0,
                rules=[{"active_from_tick": 1, "effect": {"type": "set", "value": 99.0}}],
            )
        ],
    )

    state = apply_sweep_overrides(state, sweep)

    # Verify max_ticks was set
    assert state.clock.max_ticks == 10

    # Verify carbon_tax_level baseline was overridden
    for prop in state.properties.system_properties:
        if prop.id == "carbon_tax_level":
            assert prop.trajectory.baseline == 99.0
            assert len(prop.trajectory.rules) == 1
            break
    else:
        pytest.fail("carbon_tax_level not found in system_properties")


def test_factor_overrides_werden_nicht_mehr_angewendet():
    """P2.0-C: Ein Rahmenszenario setzt Verläufe, nicht die Antwort.

    Der Test hieß bis dahin `test_apply_factor_overrides` und prüfte das
    Gegenteil. Gemessen war die Vorgabe folgenlos: In allen vier Presets, die
    eine trugen, landeten nach 20 Ticks alle sieben Faktoren auf denselben
    Zuständen wie ohne sie — sie störte nur die ersten Ticks, bevor die Regeln
    sie überschrieben.

    Das Feld bleibt im Modell lesbar; wirksam ist es nicht mehr, und der
    Sweep-Vertrag sagt das (`UNBEACHTET`, Invariante 7).
    """

    state = build_initial_state(load_cib=False)
    assert state.environment.factors["F2"].current_state == "F2.1"

    sweep = SweepConfig(
        id="test",
        name="Test",
        description="Test sweep",
        max_ticks=5,
        factor_overrides=[
            FactorOverride(factor_id="F2", initial_state="F2.2"),
        ],
    )

    state = apply_sweep_overrides(state, sweep)
    assert state.environment.factors["F2"].current_state == "F2.1", (
        "Eine Faktor-Vorgabe hat den Startzustand wieder verschoben — dann ist "
        "die Umdrehung aus P2.0-C zurückgenommen."
    )


def test_der_vertrag_nennt_die_verworfene_faktorlage():
    """Invariante 7: Ein Pfad, der etwas verwirft, sagt es."""

    from src.orchestration.scenario_sweeps import UNBEACHTET

    felder = {f.feld for f in UNBEACHTET}
    assert (
        "factor_states" in felder
    ), "Die Faktorlage wird verworfen, ohne dass der Vertrag es nennt."


def test_deterministic_only_skips_llm():
    """In deterministic_only mode, the runner should complete without LLM calls."""
    state = build_initial_state(load_cib=True)
    state.clock.max_ticks = 5

    def dummy_llm(prompt):
        return "{}"

    runner = SimulationRunner(
        llm=dummy_llm,
        options=RunnerOptions(
            enable_market=True,
            deterministic_only=True,
            checkpoint_interval=0,
            verbose_ticks=False,
        ),
    )

    final_state = runner.run(state, seed=42, run_id="test-det")
    assert final_state.clock.current_tick == 5
    # In deterministic mode, there should be no LLM-generated round_results
    # (round_results come from agent responses)


def test_run_single_sweep_short():
    """Run a single sweep with a small number of ticks to verify end-to-end.

    **Dieser Test stand bis P4.2 in der Ausnahmeliste der CI** — zusammen mit
    `test_sweep_base_price_override_raises_ticket_price` der Grund, warum ein
    lokaler `pytest` etwas anderes war als ein CI-Lauf.

    Er braucht kein Sprachmodell und hat nie eines gebraucht: Ein Sweep rechnet
    seine Ticks deterministisch. Was ihn aufhielt, war der **Abschlusstext** am
    Ende von `run_single_sweep` — eine Stelle, die mit dem zu tun hat, was hier
    geprüft wird: nichts. `llm_narrative=False` sagt das jetzt, statt den ganzen
    Test wegen ihm zu überspringen.
    """
    sweep = SweepConfig(
        id="test_short",
        name="Short Test Sweep",
        description="Quick validation sweep",
        max_ticks=5,
        property_overrides=[
            PropertyOverride(
                property_id="carbon_tax_level",
                baseline=150.0,
                rules=[{"active_from_tick": 1, "effect": {"type": "set", "value": 150.0}}],
            )
        ],
        milestones=[
            MilestoneCheck(
                tick=3,
                description="Carbon tax at 150",
                check_property="carbon_tax_level",
                expected_value=150.0,
            ),
        ],
    )

    result = run_single_sweep(sweep, verbose=False, llm_narrative=False)

    assert result.sweep_id == "test_short"
    assert result.ticks_completed == 5
    assert result.consistency_score > 0
    assert result.stability_index > 0
    assert len(result.final_factor_states) == 7  # All 7 factors


def test_milestone_expected_factor_state():
    from src.models.state_models import (
        EnvironmentState,
        FactorState,
        SimulationClock,
        SimulationState,
    )
    from src.orchestration.scenario_sweeps import evaluate_milestone_on_state

    state = SimulationState(
        run_id="ms",
        config=build_initial_state(load_cib=False).config,
        agents=[],
        clock=SimulationClock(current_tick=8, max_ticks=10),
        environment=EnvironmentState(
            factors={
                "F2": FactorState(
                    id="F2",
                    name="F2",
                    description="",
                    current_state="F2.1",
                    possible_states={"F2.1": "A", "F2.2": "B"},
                )
            }
        ),
        factor_timeseries=[{"tick": 8, "F2": "F2.2"}],
    )
    ms = MilestoneCheck(
        tick=8,
        description="F2.2 expected",
        check_factor="F2",
        expected_factor_state="F2.2",
    )
    result = evaluate_milestone_on_state(state, ms)
    assert result["passed"] is True
    assert result["actual_value"] == "F2.2"


def test_sweep_co2_delayed_loads():
    """The co2_delayed.json sweep should load and have correct structure."""
    path = REPO_ROOT / "configs" / "sweeps" / "co2_delayed.json"
    config = load_sweep_config(path)
    assert config.id == "co2_delayed"
    assert len(config.milestones) >= 3
    # Seit P4.5 auf 120 Ticks gestreckt (vorher Tick 15 und 25, x2,4).
    assert any(m.tick == 36 for m in config.milestones), "CO2 Tick 36 milestone missing"
    assert any(m.tick == 60 for m in config.milestones), "CO2 Tick 60 milestone missing"


# ---------------------------------------------------------------------------
# P2.3 — Basispreis konfigurierbar via SweepConfig.base_price
# ---------------------------------------------------------------------------


def test_sweep_base_price_override_raises_ticket_price():
    """P2.3: A sweep with base_price=200 should produce higher ticket prices than base_price=80.

    Der zweite der beiden bis P4.2 deselektierten Tests, aus demselben Grund und
    mit derselben Antwort — siehe `test_run_single_sweep_short`. Er startet zwei
    Läufe und zahlte den Abschlusstext deshalb doppelt.
    """
    from src.orchestration.scenario_sweeps import run_single_sweep

    sweep_low = SweepConfig(
        id="low_base",
        name="Low Base Price",
        description="base_price=80",
        max_ticks=5,
        base_price=80.0,
    )
    sweep_high = SweepConfig(
        id="high_base",
        name="High Base Price",
        description="base_price=200",
        max_ticks=5,
        base_price=200.0,
    )

    result_low = run_single_sweep(sweep_low, verbose=False, llm_narrative=False)
    result_high = run_single_sweep(sweep_high, verbose=False, llm_narrative=False)

    low_price = result_low.final_properties.get("ticket_price", 0.0)
    high_price = result_high.final_properties.get("ticket_price", 0.0)
    assert (
        high_price > low_price
    ), f"Expected high base_price → higher ticket, got {low_price:.1f} vs {high_price:.1f}"


def test_sweep_base_price_none_uses_default():
    """P2.3: base_price=None should leave default (100.0) unchanged."""
    state = build_initial_state(load_cib=False)
    sweep = SweepConfig(id="no_bp", name="No BP", description="no override", max_ticks=5)
    state = apply_sweep_overrides(state, sweep)
    assert state.properties.price_model.base_price == 100.0


# ---------------------------------------------------------------------------
# P4.2 -- der Abschlusstext ist abschaltbar, und das ist gemessen
# ---------------------------------------------------------------------------


class TestEinSweepOhneAbschlusstextFragtNiemanden:
    """Die tragende Zusage hinter `llm_narrative=False`.

    **Sie lautet nicht «der Test ist schnell», sondern «es wird kein Endpunkt
    befragt».** Eine Zeitmessung waere hier der falsche Waechter: Sie ginge auf
    einer langsamen Maschine grundlos rot und bliebe gruen, sobald irgendwo ein
    Ollama antwortet -- also genau dann, wenn die Zusage nicht mehr geprueft
    wird. Gemessen wird deshalb, ob der Client ueberhaupt **gebaut** wird.

    Die Gegenprobe daneben ist Pflicht: Ohne sie waere diese Klasse auch dann
    gruen, wenn `run_single_sweep` das Sprachmodell gar nicht mehr erreichen
    koennte -- ein anderer Befund, von aussen nicht zu unterscheiden. Dieselbe
    Falle wie beim ersten Anlauf des P2.13-Waechters.
    """

    def _sweep(self, sweep_id: str) -> SweepConfig:
        return SweepConfig(
            id=sweep_id,
            name="LLM-Schalter",
            description="Prueft, ob der Abschlusstext einen Endpunkt befragt",
            max_ticks=3,
        )

    def _gebaute_clients(self, monkeypatch, *, llm_narrative: bool) -> list[object]:
        from src.orchestration import scenario_sweeps as sweeps

        gebaut: list[object] = []

        class BeobachteterClient:
            def __init__(self, config=None):
                gebaut.append(config)

            def call(self, prompt: str, **kwargs) -> str:
                # Leere Antwort -> `generate_run_scenario` faellt aufs Template
                # zurueck. Der Waechter misst den *Griff* zum Modell, nicht die
                # Qualitaet seiner Antwort, und darf dafuer kein Netz brauchen.
                return ""

        monkeypatch.setattr(sweeps, "OllamaClient", BeobachteterClient)
        suffix = "an" if llm_narrative else "aus"
        sweeps.run_single_sweep(
            self._sweep(f"llm_schalter_{suffix}"),
            verbose=False,
            llm_narrative=llm_narrative,
        )
        return gebaut

    def test_ohne_abschlusstext_wird_kein_client_gebaut(self, monkeypatch):
        gebaut = self._gebaute_clients(monkeypatch, llm_narrative=False)

        assert not gebaut, (
            "`llm_narrative=False` hat trotzdem einen Ollama-Client gebaut -- "
            "der Sweep-Pfad greift also weiterhin nach einem Endpunkt, und die "
            "beiden Tests darueber koennen wieder minutenlang haengen."
        )

    def test_mit_abschlusstext_wird_einer_gebaut(self, monkeypatch):
        """Die Gegenprobe: Der Standardweg ist unveraendert."""

        gebaut = self._gebaute_clients(monkeypatch, llm_narrative=True)

        assert len(gebaut) == 1, (
            f"{len(gebaut)} Clients statt genau einem. Der Standardweg soll den "
            "Abschlusstext weiterhin vom Modell schreiben lassen -- sonst misst "
            "die Zusage darueber nichts."
        )


def test_ein_sweep_ohne_abschlusstext_behauptet_das_auch_im_artefakt():
    """Ein Lauf ohne Sprachmodell darf nicht wie einer mit aussehen.

    Dieselbe Klasse wie P3.11 und P3.13: ein Artefakt, das ueber sich selbst
    etwas Falsches sagt. `deterministic_with_llm_narrative` ist die Aussage
    "die Zahlen sind deterministisch, den Text schrieb das Modell" -- und ohne
    Abschlusstext stimmt ihre zweite Haelfte nicht mehr.
    """

    from src.orchestration.scenario_sweeps import sweep_metadata_args
    from src.reporting.output_writer.provenance import compute_mode

    assert compute_mode(sweep_metadata_args()) == "deterministic_with_llm_narrative"
    assert compute_mode(sweep_metadata_args(llm_narrative=False)) == "deterministic_only"


# ---------------------------------------------------------------------------
# P4.4: Der Sweep-Pfad hat kein Sprachmodell, und er sagt es
# ---------------------------------------------------------------------------


class TestDerSweepHatKeinSprachmodell:
    """Der Platzhalter an der Stelle des Sprachmodells (P4.4, 2026-09-11).

    Bis dahin stand dort eine nackte Funktion, wo der Runner ein Objekt mit
    ``.call()`` verlangt — gefunden von ``mypy``. **Die tragende Zusage ist
    nicht «der Platzhalter wirft»**, sondern «ein Sweep ruft ihn nie»: Sonst
    wäre ein Sweep, der still Ausfälle sammelt, von einem sauberen nicht zu
    unterscheiden. Die Gegenprobe zeigt, dass die Messung darüber einen Aufruf
    überhaupt bemerken würde.
    """

    def _sweep(self) -> SweepConfig:
        return SweepConfig(
            id="kein_sprachmodell",
            name="Kein Sprachmodell",
            description="Prueft, dass ein Sweep sein Sprachmodell nie ruft",
            max_ticks=3,
        )

    def test_der_platzhalter_nennt_die_ursache(self):
        from src.orchestration.scenario_sweeps import KeinSprachmodell

        with pytest.raises(RuntimeError, match="kein Sprachmodell"):
            KeinSprachmodell().call("egal")

    def test_ein_sweep_ruft_ihn_nie(self, monkeypatch):
        from src.orchestration import scenario_sweeps as sweeps

        gesehen: list[tuple[object, RunnerOptions, object]] = []
        echter_runner = sweeps.SimulationRunner

        class BeobachteterRunner(echter_runner):
            def run(self, *args, **kwargs):
                ende = super().run(*args, **kwargs)
                gesehen.append((self.llm, self.options, ende))
                return ende

        monkeypatch.setattr(sweeps, "SimulationRunner", BeobachteterRunner)
        sweeps.run_single_sweep(self._sweep(), verbose=False, llm_narrative=False)

        assert len(gesehen) == 1, f"{len(gesehen)} Läufe statt genau einem"
        llm, optionen, ende = gesehen[0]
        assert isinstance(llm, sweeps.KeinSprachmodell), (
            f"Der Sweep übergibt {type(llm).__name__} statt des Platzhalters -- "
            "wer hier ein Objekt einsetzt, das still antwortet, macht einen "
            "Aufruf wieder unsichtbar."
        )
        assert optionen.deterministic_only
        assert not ende.llm_incidents, (
            f"{len(ende.llm_incidents)} Ausfälle in einem Sweep: Ein Knoten hat "
            "das Sprachmodell gerufen, obwohl `FESTLEGUNGEN` den deterministischen "
            "Modus festlegt."
        )

    def test_gegenprobe_ein_aufruf_waere_sichtbar(self):
        """Ohne deterministischen Modus rufen die Agenten ihn — und der Lauf meldet es."""

        from src.orchestration.scenario_sweeps import KeinSprachmodell

        state = build_initial_state(load_cib=True)
        state.clock.max_ticks = 1
        ende = SimulationRunner(
            llm=KeinSprachmodell(),
            options=RunnerOptions(
                deterministic_only=False, checkpoint_interval=0, verbose_ticks=False
            ),
        ).run(state, seed=42)

        assert ende.llm_incidents, (
            "Kein Ausfall, obwohl die Agenten laufen -- dann misst "
            "`test_ein_sweep_ruft_ihn_nie` nichts."
        )
        assert all("kein Sprachmodell" in i.error for i in ende.llm_incidents)


class TestEineStufenfunktionLaesstSichUeberschreiben:
    """P7.13, gemessen am 2026-09-15.

    `bevoelkerungsentwicklung` ist die einzige Stufenfunktion unter den
    Systemgrößen. `apply_sweep_overrides` prüfte nur, ob ein Verlauf `baseline`
    und `rules` hat — eine Überschreibung darauf fiel still weg. Über das Dashboard
    stand die Abweichung dann im Artefakt («abgeleitet»), im Lauf nicht.
    """

    GROESSE = "bevoelkerungsentwicklung"

    def _verlauf(self, state) -> list[float]:
        from src.market.property_engine import resolve_trajectory

        prop = next(p for p in state.properties.system_properties if p.id == self.GROESSE)
        return [resolve_trajectory(prop.trajectory, tick) for tick in range(0, 131)]

    def _szenario(self, **override):
        from src.models.sweep_models import PropertyOverride, SweepConfig

        return SweepConfig(
            id="probe",
            name="Probe",
            description="Stufenfunktion",
            property_overrides=[PropertyOverride(property_id=self.GROESSE, **override)],
        )

    def test_the_conversion_alone_changes_no_tick(self):
        from src.config_loader import build_initial_state

        vorher = self._verlauf(build_initial_state())
        nachher = self._verlauf(apply_sweep_overrides(build_initial_state(), self._szenario()))

        assert nachher == vorher

    def test_a_new_start_value_arrives(self):
        from src.config_loader import build_initial_state

        state = apply_sweep_overrides(
            build_initial_state(), self._szenario(baseline=5000.0, rules=[])
        )

        assert set(self._verlauf(state)) == {5000.0}

    def test_an_override_with_its_own_values_leaves_its_form(self):
        """Jeder Entwurf mit «Eigene Werte anwenden» trägt die Punkte als Regeln.

        Das ist keine Änderung. Die erste Fassung wandelte trotzdem um, und der
        Wirkungstest sah den Schalter auf dem Einzellauf wirken, obwohl sich kein
        einziger Wert bewegte — nur die Darstellung im Zustand.
        """

        from src.config_loader import build_initial_state
        from src.models.property_models import StepFunctionTrajectory

        state = build_initial_state()
        prop = next(p for p in state.properties.system_properties if p.id == self.GROESSE)
        punkte = sorted(prop.trajectory.points, key=lambda punkt: punkt.tick)
        regeln = [
            {"active_from_tick": punkt.tick, "effect": {"type": "set", "value": punkt.value}}
            for punkt in punkte
        ]

        nachher = apply_sweep_overrides(
            state, self._szenario(baseline=punkte[0].value, rules=regeln)
        )

        prop = next(p for p in nachher.properties.system_properties if p.id == self.GROESSE)
        assert isinstance(prop.trajectory, StepFunctionTrajectory)
