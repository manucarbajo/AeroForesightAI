"""P0.3: Eine kaputte Konfiguration soll auffallen, bevor der Lauf anfängt.

Bis dahin gab `validate_config` bedingungslos `[]` zurück. Der teuerste Fall war
ein negativer Seed: Er kam durch alle Prüfungen und riss den Lauf erst im ersten
Tick mit `ValueError: expected non-negative integer` aus numpy ab — ohne jeden
Bezug zum Seed.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.config_loader import build_initial_state
from src.models.property_models import IndividualProperty, ShiftRule
from src.models.state_models import LLMConfig, SimulationClock, SimulationConfig
from src.validation import (
    ValidationError,
    ValidationIssue,
    collect_state_errors,
    field_of,
    validate_agent,
    validate_clock,
    validate_config,
    validate_llm_settings,
    validate_state,
)


def _config(**overrides) -> SimulationConfig:
    fields = dict(name="Testlauf", description="Beschreibung", llm=LLMConfig(), seed=None)
    fields.update(overrides)
    return SimulationConfig(**fields)


def _messages(errors: list[str]) -> str:
    return " | ".join(errors)


# --- Die ausgelieferte Konfiguration muss sauber sein ----------------------


def test_shipped_configuration_has_no_errors():
    """Wenn das hier rot wird, ist entweder `configs/` kaputt oder eine Regel zu streng."""

    assert collect_state_errors(build_initial_state()) == []


def test_a_healthy_config_passes():
    assert validate_config(_config()) == []


# --- Wertebereiche ----------------------------------------------------------


@pytest.mark.parametrize("seed", [0, 1, 42, None])
def test_valid_seeds_pass(seed):
    assert validate_config(_config(seed=seed)) == []


def test_negative_seed_is_rejected():
    """Der Fall, der heute erst tief in numpy auffällt."""

    errors = validate_config(_config(seed=-1))

    assert len(errors) == 1
    assert "seed" in _messages(errors)


def test_temperature_outside_the_allowed_range_is_rejected():
    assert "temperature" in _messages(validate_config(_config(llm=LLMConfig(temperature=3.0))))
    assert "temperature" in _messages(validate_config(_config(llm=LLMConfig(temperature=-0.1))))


@pytest.mark.parametrize("temperature", [0.0, 0.7, 2.0])
def test_temperature_at_the_edges_passes(temperature):
    assert validate_config(_config(llm=LLMConfig(temperature=temperature))) == []


def test_max_tokens_below_one_is_rejected():
    assert "max_tokens" in _messages(validate_config(_config(llm=LLMConfig(max_tokens=0))))


def test_empty_name_is_rejected():
    assert "name" in _messages(validate_config(_config(name="   ")))


def test_empty_model_is_rejected():
    errors = validate_config(_config(llm=LLMConfig(model="")))

    assert "Modellname" in _messages(errors)
    assert "config.llm" in _messages(errors)


def test_empty_description_is_allowed():
    """Eine fehlende Beschreibung macht keinen Lauf falsch — sie blockiert also nicht."""

    assert validate_config(_config(description="")) == []


# --- Referenz-Integrität der Agentenprofile --------------------------------


def _regulator():
    state = build_initial_state()
    return state, next(agent for agent in state.agents if agent.id == "regulator")


def test_observes_pointing_at_an_unknown_factor_is_rejected():
    state, regulator = _regulator()
    regulator.profile.observes = ["market_metrics", "factors F2,F9"]

    errors = validate_agent(regulator, set(state.environment.factors))

    assert "F9" in _messages(errors)
    assert "regulator" in _messages(errors)


def test_may_propose_pointing_at_an_unknown_factor_is_rejected():
    state, regulator = _regulator()
    regulator.profile.may_propose = ["factor_state F42"]

    assert "F42" in _messages(validate_agent(regulator, set(state.environment.factors)))


def test_an_unknown_dependency_is_rejected():
    """Unbekannte `depends_on`-Werte gelten in jedem Tick als unerfüllt — lautlos."""

    state, regulator = _regulator()
    regulator.profile.depends_on = ["consumer.bookingrate"]

    errors = validate_agent(regulator, set(state.environment.factors))

    assert "depends_on" in _messages(errors)
    assert "consumer.bookingrate" in _messages(errors)


def test_the_shipped_profiles_reference_only_existing_factors():
    state = build_initial_state()
    factor_ids = set(state.environment.factors)

    for agent in state.agents:
        assert validate_agent(agent, factor_ids) == [], f"agent {agent.id}"


def test_an_agent_without_a_profile_is_rejected():
    """Bis P0.5 hieß dieser Test "…is_fine" — und das stimmte damals auch.

    Ohne Profil ließ der Parser alles durch, die Durchsetzung nahm die Rechte
    aus dem hartcodierten `AGENT_FACTOR_PERMISSIONS`, und der Lauf verhielt
    sich richtig. P0.5 hat das Dict entfernt und `agent_profiles.json` zur
    einzigen Quelle gemacht: Seitdem heißt "kein Profil" **nichts erlaubt**.

    Damit ist ein fehlendes Profil kein harmloser Sonderfall mehr, sondern
    schaltet still ab, was Invariante 2 durchsetzen soll. Nachgestellt am
    2026-08-27: `configs/agent_profiles.json` weggeschoben, und der Lauf
    rechnet klaglos zu Ende — kein Agent kann noch einen Faktor vorschlagen,
    keine Meldung sagt es. `config_loader` vergibt nämlich schlicht kein
    Profil, wenn die Datei fehlt oder den Agenten nicht kennt.
    """

    state = build_initial_state()
    agent = state.agents[0]
    agent.profile = None

    errors = validate_agent(agent, set(state.environment.factors))
    assert "kein Profil" in _messages(errors)


def test_a_missing_profiles_file_does_not_pass_silently(tmp_path, monkeypatch):
    """Der Weg dorthin, nicht nur die Funktion: Fehlt die Datei, muss die
    Prüfung anschlagen — vorher lief der Lauf ohne jede Berechtigung durch."""

    import src.config_loader as config_loader

    monkeypatch.setattr(config_loader, "CONFIGS_DIR", tmp_path)
    for name in ("simulation_config.json", "agents.json", "properties.json", "factors.json"):
        shutil.copy(Path("configs") / name, tmp_path / name)
    # agent_profiles.json bewusst nicht mitkopiert.

    state = config_loader.build_initial_state(load_cib=False)
    fehler = collect_state_errors(state)

    ohne_profil = [message for message in fehler if "kein Profil" in message]
    assert len(ohne_profil) == len(state.agents)


# --- Der Vertrag: sammeln vs. werfen ---------------------------------------


def test_collect_reports_every_error_at_once():
    """Wer eine Config repariert, will alle Befunde sehen — nicht einen pro Anlauf."""

    state = build_initial_state()
    state.config.seed = -1
    state.config.name = ""
    state.config.llm.max_tokens = 0

    errors = collect_state_errors(state)

    assert len(errors) == 3


def test_collect_does_not_raise():
    state = build_initial_state()
    state.config.seed = -1

    assert collect_state_errors(state)  # keine Exception


def test_validate_state_still_raises():
    state = build_initial_state()
    state.config.seed = -1

    with pytest.raises(ValidationError) as excinfo:
        validate_state(state)

    assert "seed" in str(excinfo.value)


def test_validate_state_returns_empty_for_a_healthy_state():
    assert validate_state(build_initial_state()) == []


# --- Der Weg durch das Dashboard -------------------------------------------


def test_the_dashboard_reports_a_broken_draft():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    draft = ConfigDraft(rounds=2, use_seed=True, seed=-1)

    assert "seed" in _messages(validate_draft(draft))


def test_the_dashboard_reports_nothing_for_a_healthy_draft():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    assert validate_draft(ConfigDraft(rounds=2)) == []


def test_the_dashboard_checks_the_llm_values_it_actually_uses():
    """Die Lücke, die der erste Anlauf von P0.3 offen ließ.

    `prepare_simulation_state` überträgt vom Draft nur den Seed; Modellname,
    Temperatur und Antwortlänge gehen über `RunLaunchConfig` direkt an den
    Client. Geprüft wurde vorher `state.config.llm` — ein Feld, das kein
    Laufpfad liest. Ein Draft mit diesen Werten galt deshalb als fehlerfrei.
    """

    from dashboard.config_catalog import ConfigDraft, validate_draft

    errors = validate_draft(
        ConfigDraft(rounds=2, mock_llm=False, temperature=5.0, max_tokens=0, model="")
    )

    assert len(errors) == 3
    assert "temperature" in _messages(errors)
    assert "max_tokens" in _messages(errors)
    assert "Modellname" in _messages(errors)


def test_a_run_without_a_language_model_is_not_blocked_by_ollama_settings():
    """Die Prüfung darf keine Tür verriegeln, durch die niemand geht.

    Beide unteren Rechenmodi («Ohne Sprachmodell» und «Nur Zahlen») setzen
    `mock_llm`, und dann liefert `_build_llm()` ein `MockLLM` — Modellname,
    Temperatur und Antwortlänge werden nie angefasst. Ein leeres Modellfeld darf
    dort also keinen Lauf verhindern.
    """

    from dashboard.config_catalog import ConfigDraft, validate_draft

    ohne_sprachmodell = ConfigDraft(rounds=2, mock_llm=True, model="", max_tokens=0)
    nur_zahlen = ConfigDraft(
        rounds=2, mock_llm=True, deterministic_only=True, model="", temperature=9.0
    )

    assert validate_draft(ohne_sprachmodell) == []
    assert validate_draft(nur_zahlen) == []


def test_with_a_language_model_the_settings_are_checked():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    errors = validate_draft(ConfigDraft(rounds=2, mock_llm=False, temperature=5.0))

    assert "temperature" in _messages(errors)


# --- Eine Regelquelle für drei Herkunftsorte -------------------------------


def test_llm_rules_live_in_one_place():
    """Config, Draft und CLI müssen denselben Wert gleich beurteilen."""

    from dashboard.config_catalog import ConfigDraft, validate_draft
    from src.validation import validate_llm_settings

    direct = validate_llm_settings("llama3.2", 5.0, 2048, context="X")
    from_draft = validate_draft(ConfigDraft(rounds=2, mock_llm=False, temperature=5.0))
    from_config = validate_config(_config(llm=LLMConfig(temperature=5.0)))

    assert len(direct) == 1
    # Gleicher Befund, nur mit dem jeweiligen Herkunftsort davor.
    for errors in (direct, from_draft, from_config):
        assert "temperature (5.0) muss zwischen 0.0 und 2.0 liegen" in _messages(errors)


@pytest.mark.parametrize(
    "context,expected",
    [("config.llm", "config.llm:"), ("Technik", "Technik:"), ("CLI", "CLI:")],
)
def test_the_message_names_where_the_value_came_from(context, expected):
    from src.validation import validate_llm_settings

    errors = validate_llm_settings("m", 9.0, 1, context=context)

    assert _messages(errors).startswith(expected)


def test_an_unreadable_config_file_becomes_a_finding_not_a_crash():
    from dashboard.config_catalog import ConfigDraft, validate_draft

    draft = ConfigDraft(rounds=2, factors_file="gibt-es-nicht.json")

    errors = validate_draft(draft)

    assert errors
    assert "geladen werden" in _messages(errors)


class TestBefundeTragenIhrFeld:
    """P1.1: Ein Befund weiß, an welchem Eingabefeld er hängt.

    Der Feldbezug entsteht in der Prüfung, nicht in der Oberfläche. Eine
    Zuordnung über Schlüsselwörter im Meldungstext bräche still, sobald jemand
    eine Formulierung ändert — und still brechende Prüfungen sind genau das,
    was Phase 0 abgeräumt hat.
    """

    def test_a_negative_seed_points_at_the_seed_field(self) -> None:
        befunde = validate_config(_config(seed=-1))

        assert [field_of(entry) for entry in befunde] == ["seed"]

    def test_an_empty_name_points_at_the_name_field(self) -> None:
        befunde = validate_config(_config(name="   "))

        assert "simulation_name" in [field_of(entry) for entry in befunde]

    def test_the_llm_rules_name_their_own_fields(self) -> None:
        befunde = validate_llm_settings("", 9.0, 0, context="Technik")

        assert sorted(field_of(entry) for entry in befunde) == [
            "max_tokens",
            "model",
            "temperature",
        ]

    def test_a_finding_still_behaves_like_a_string(self) -> None:
        """Der Grund für die `str`-Unterklasse — jeder heutige Konsument bleibt richtig."""

        befund = ValidationIssue("max_ticks muss mindestens 1 sein", "rounds")

        assert "mindestens" in befund
        assert chr(10).join([befund, befund]).count(chr(10)) == 1
        assert befund == "max_ticks muss mindestens 1 sein"

    def test_findings_without_a_field_stay_unassigned(self) -> None:
        """Regeln und Profile hängen an keinem einzelnen Eingabefeld."""

        clock = SimulationClock(max_ticks=0)

        assert field_of(validate_clock(clock)[0]) == "rounds"
        assert field_of("ein Befund von woanders") is None


class TestEineShiftRegelWirdAuchAufIhreWirkungGeprueft:
    """P2.4-Nebenbefund (2026-08-31) — **ein Ziel, das es nicht gibt, war still**.

    `_validate_shift_rules` prüfte bis dahin nur die ``when``-Klausel. Das
    ``effect`` kam ungeprüft durch, und zur Laufzeit fiel ein unbekanntes Ziel
    aus einer ``if``/``elif``-Kette **ohne ``else``** heraus: Eine Regel auf
    ``age`` tat nichts, ein Tippfehler wie ``price_sensitivty`` ebenso. Keine
    Meldung, kein Fehler — nur eine Regel, die nie greift, und jemand, der
    glaubt, sein Modell verschiebe etwas.

    Dieselbe Klasse von Befund, gegen die Invariante 6 im ``rule_engine``
    angetreten ist: **Was nicht auswertbar ist, schlägt laut fehl.**
    """

    @staticmethod
    def _regel(ziel: str, delta: object = 0.1) -> ShiftRule:
        return ShiftRule(
            id="test",
            when={"factor": "F1", "state": "F1.2"},
            effect={"property": ziel, "delta": delta},
        )

    def test_ein_bekanntes_ziel_geht_durch(self):
        from src.population.population_sampler import SHIFT_ZIELE
        from src.validation import _validate_shift_rules

        for ziel in SHIFT_ZIELE:
            assert _validate_shift_rules([self._regel(ziel)]) == [], ziel

    def test_ein_unbekanntes_ziel_wird_abgewiesen(self):
        from src.validation import _validate_shift_rules

        befunde = _validate_shift_rules([self._regel("age")])

        assert len(befunde) == 1
        assert "unbekanntes Ziel" in befunde[0] and "age" in befunde[0]

    def test_ein_tippfehler_wird_abgewiesen(self):
        """**Der eigentliche Alltagsfall.** `age` schreibt jemand absichtlich;
        `price_sensitivty` schreibt niemand absichtlich."""

        from src.validation import _validate_shift_rules

        befunde = _validate_shift_rules([self._regel("price_sensitivty")])

        assert befunde and "unbekanntes Ziel" in befunde[0]

    def test_ein_effekt_ohne_ziel_wird_abgewiesen(self):
        from src.validation import _validate_shift_rules

        regel = ShiftRule(id="leer", when={"factor": "F1", "state": "F1.2"}, effect={"delta": 0.1})

        assert any("ohne 'property'" in b for b in _validate_shift_rules([regel]))

    def test_ein_delta_das_keine_zahl_ist_wird_abgewiesen(self):
        from src.validation import _validate_shift_rules

        befunde = _validate_shift_rules([self._regel("price_sensitivity", delta="viel")])

        assert any("keine Zahl" in b for b in befunde)

    def test_die_ausgelieferte_config_haelt_das_ein(self):
        """Die Regel wäre wertlos, wenn `configs/properties.json` sie bräche."""

        from src.config_loader import load_properties_config
        from src.validation import _validate_shift_rules

        assert _validate_shift_rules(load_properties_config().shift_rules) == []

    def test_zur_laufzeit_scheitert_es_ebenfalls_laut(self):
        """**Zwei Schranken, und beide werden gebraucht.**

        Die Validierung fängt eine Regel aus einer Config-Datei. Wer eine Regel
        im Code baut — Tests, Sweeps, das Dashboard — kommt daran vorbei und
        soll es an der Auswertung erfahren.
        """

        import pytest

        from src.config_loader import build_initial_state, load_properties_config
        from src.population.population_sampler import apply_factor_shifts, initialize_population

        properties = load_properties_config()
        zustand = build_initial_state()
        config = next(
            agent for agent in zustand.agents if getattr(agent, "population_config", None)
        ).population_config
        leute = initialize_population(properties, config, seed=42)[:5]
        # Die Bedingung muss zutreffen, sonst prüft der Test nichts.
        lage = zustand.environment.factors
        lage["F1"] = lage["F1"].model_copy(update={"current_state": "F1.2"})

        with pytest.raises(ValueError, match="unbekanntes Ziel"):
            apply_factor_shifts(
                leute, [self._regel("age")], lage, tick=1, metrics={}, system_properties={}
            )


class TestEineVerteilungDieAnDieWandKlemmtSagtEs:
    """P2.9 (2026-08-31) — **still geklemmte Masse ist keine Verteilung mehr**.

    Der Anlass ist gemessen: `age` stand als `lognormal` mit
    ``mean: 73.0, std_dev: 1.0`` in der Config. `_sample_lognormal` liest `mean`
    als **Median**, die Verteilung hat damit den Mittelwert 120 und legt
    **41,8 %** ihrer Masse über die Obergrenze 90. Genau dieser Anteil landete
    dort: **41 % der Bevölkerung waren exakt 90 Jahre alt** — und niemand hat es
    bemerkt, weil `np.clip` schweigt.

    Der Wächter prüft **jede** Verteilung, nicht nur `age`: Wer `wtp_eur`
    ähnlich parametrisiert, bekäme sonst dasselbe, ohne es zu merken.
    """

    @staticmethod
    def _merkmal(**felder) -> IndividualProperty:
        basis = {
            "id": "test",
            "type": "distribution",
            "distribution": "normal",
            "mean": 50.0,
            "std_dev": 10.0,
            "min_value": 0.0,
            "max_value": 100.0,
        }
        return IndividualProperty(**{**basis, **felder})

    def test_eine_passende_verteilung_geht_durch(self):
        import numpy as np

        from src.population.population_sampler import pruefe_verteilung

        pruefe_verteilung(np.random.default_rng(0), self._merkmal())

    def test_eine_verteilung_neben_ihren_grenzen_wird_gemeldet(self):
        import numpy as np

        from src.population.population_sampler import VerteilungGeklemmt, pruefe_verteilung

        with pytest.raises(VerteilungGeklemmt, match="falsch parametrisiert"):
            pruefe_verteilung(np.random.default_rng(0), self._merkmal(mean=95.0, std_dev=30.0))

    def test_der_alte_zustand_wuerde_heute_auffallen(self):
        """Die Nachstellung des Befunds — sonst prüft der Wächter nur sich selbst."""

        import numpy as np

        from src.population.population_sampler import VerteilungGeklemmt, pruefe_verteilung

        alt = self._merkmal(
            id="age",
            distribution="lognormal",
            mean=73.0,
            std_dev=1.0,
            min_value=2.0,
            max_value=90.0,
        )

        with pytest.raises(VerteilungGeklemmt, match=r"4[0-9]\.[0-9]%"):
            pruefe_verteilung(np.random.default_rng(0), alt)

    def test_die_ausgelieferte_config_haelt_es_ein(self):
        """Die Regel wäre wertlos, wenn die eigene Config sie bräche."""

        import numpy as np

        from src.config_loader import load_properties_config
        from src.population.population_sampler import pruefe_verteilung

        for prop in load_properties_config().individual_properties:
            if prop.type == "distribution" and prop.enabled:
                pruefe_verteilung(np.random.default_rng(0), prop)

    def test_die_altersverteilung_traegt_jetzt_eine_quelle(self):
        """P2.9 hat sie aus echten Daten gesetzt statt geraten."""

        from src.config_loader import load_properties_config

        age = next(p for p in load_properties_config().individual_properties if p.id == "age")

        assert "Eurostat" in age.quelle and "demo_pjangroup" in age.quelle
        assert age.min_value == 18.0, "Kinder buchen keine Flüge"


class TestEineRegelLiestKeinenLaufzeitwert:
    """P3.1 (2026-09-05) — **der Name stimmte, die Zahl war veraltet.**

    Für Systemgrößen mit ``source in {"runtime", "computed"}`` — heute
    ``provider_markup`` und ``ticket_price`` — liefert
    ``resolve_system_properties`` laut eigenem Docstring die statische
    Trajektorien-Baseline und nicht den Wert des laufenden Ticks. Die
    Namensprüfung aus P0.4 ließ eine Regel darauf durch: Sie **existiert** ja.
    Folgenlos war das nur, solange keine ausgelieferte Regel eine solche Größe
    nennt — die nächste hätte still gegen eine veraltete Zahl geprüft, und
    genau das ist die stille Wirkungslosigkeit, gegen die P0.4 angetreten ist.

    **Der Laufzeitwert wird bewusst nicht durchgereicht.** Er machte die
    Auswertung innerhalb eines Ticks reihenfolgeabhängig:
    ``apply_factor_rules_at_tick_start`` läuft **vor** der Preisberechnung, eine
    Regel auf ``ticket_price`` prüfte je nach Einhängepunkt gegen den Preis von
    vorhin oder von jetzt. Das ist eine Modellentscheidung, und sie gehört nicht
    nebenbei getroffen.
    """

    @staticmethod
    def _config_mit_regel(prop_id: str):
        from src.config_loader import load_properties_config
        from src.models.property_models import FactorRule

        properties = load_properties_config()
        return properties.model_copy(
            update={
                "factor_rules": [
                    FactorRule(
                        id="test",
                        factor_id="F1",
                        when={"system_property": prop_id, "above": 1.0},
                        effect={"set_state": "F1.2"},
                    )
                ]
            }
        )

    def test_eine_exogene_systemgroesse_geht_durch(self):
        from src.validation import _validate_rule_property_names

        assert _validate_rule_property_names(self._config_mit_regel("carbon_tax_level")) == []

    @pytest.mark.parametrize("prop_id", ["provider_markup", "ticket_price"])
    def test_eine_laufzeitgebundene_wird_abgewiesen(self, prop_id):
        from src.validation import _validate_rule_property_names

        befunde = _validate_rule_property_names(self._config_mit_regel(prop_id))

        assert len(befunde) == 1, befunde
        assert prop_id in befunde[0]
        assert "laufzeitgebunden" in befunde[0]
        # Die Meldung sagt, was stattdessen geht — sonst weiß niemand weiter.
        assert "metric" in befunde[0]

    def test_eine_unbekannte_bleibt_unbekannt(self):
        """Die alte Meldung darf nicht von der neuen verdeckt werden."""

        from src.validation import _validate_rule_property_names

        befunde = _validate_rule_property_names(self._config_mit_regel("gibt_es_nicht"))

        assert len(befunde) == 1
        assert "unbekannte Systemgröße" in befunde[0]
        assert "laufzeitgebunden" not in befunde[0]

    def test_der_ganze_lauf_weist_es_ab_nicht_nur_die_teilpruefung(self):
        """**Die Zusage von P3.1 im Wortlaut**: abgewiesen *beim Laden*."""

        from src.config_loader import build_initial_state

        state = build_initial_state()
        state.properties = self._config_mit_regel("ticket_price")

        befunde = collect_state_errors(state)

        assert any("laufzeitgebunden" in b for b in befunde), befunde
        with pytest.raises(ValidationError, match="laufzeitgebunden"):
            validate_state(state)

    def test_die_quelle_der_regel_liegt_beim_mechanismus(self):
        """Nicht in `validation.py` — dort steht nur ihre Anwendung.

        Dieselbe Bauform wie `SHIFT_ZIELE` (P2.4) und `KNOWN_METRICS` (P0.4):
        Das Vokabular wohnt bei dem Code, der es auswertet. Eine zweite Liste in
        der Validierung liefe beim nächsten `source`-Wert auseinander.
        """

        from src.config_loader import load_properties_config
        from src.market.property_engine import darf_in_regel_stehen

        properties = load_properties_config()
        erlaubt = {p.id for p in properties.system_properties if darf_in_regel_stehen(p)}
        gesperrt = {p.id for p in properties.system_properties} - erlaubt

        assert gesperrt == {"provider_markup", "ticket_price"}, (
            "Die Menge der laufzeitgebundenen Systemgrößen hat sich geändert. "
            "Wenn das gewollt ist, gehört die neue hier hinein — und ein Blick "
            "darauf, ob `resolve_system_properties` für sie wirklich nur die "
            "Baseline liefert."
        )
        assert erlaubt, "Ohne erlaubte Systemgröße wäre die Prüfung sinnlos scharf"
