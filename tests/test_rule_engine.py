"""P0.4 — die eine Regelauswertung.

Das Abnahmekriterium des Pakets steht in
`TestSelbeKlauselUeberallGleich`: Dieselbe Klausel muss an allen drei
Aufrufstellen dasselbe Ergebnis liefern. Der Rest hält die Zusage fest, dass
struktureller Unsinn laut fehlschlägt statt still `False` zu liefern.
"""

from __future__ import annotations

import pytest

from src.models.population_models import Individual
from src.models.state_models import FactorState
from src.rule_engine import (
    KNOWN_METRICS,
    RuleContext,
    RuntimeMetrics,
    UnknownRuleConditionError,
    check_when,
    describe_when,
    rule_matches,
)


def _factors(**states: str) -> dict[str, FactorState]:
    return {
        factor_id: FactorState(
            id=factor_id,
            name=factor_id,
            description=factor_id,
            current_state=state,
            possible_states={f"{factor_id}.1": "eins", f"{factor_id}.2": "zwei"},
        )
        for factor_id, state in states.items()
    }


def _person() -> Individual:
    return Individual(
        id=1,
        age=40,
        wtp_eur=200.0,
        environmental_awareness=0.5,
        price_sensitivity=0.5,
    )


def _context(
    *,
    tick: int = 1,
    factors: dict[str, FactorState] | None = None,
    metrics: dict[str, float | None] | None = None,
    system_properties: dict[str, float] | None = None,
) -> RuleContext:
    base = {name: None for name in KNOWN_METRICS}
    base["tick"] = tick
    base.update(metrics or {})
    return RuleContext(
        tick=tick,
        factors=factors or {},
        metrics=base,
        system_properties=system_properties or {},
    )


class TestFaktorbedingung:
    def test_matches_current_state(self) -> None:
        context = _context(factors=_factors(F1="F1.2"))
        assert rule_matches({"factor": "F1", "state": "F1.2"}, context) is True

    def test_other_state_does_not_match(self) -> None:
        context = _context(factors=_factors(F1="F1.1"))
        assert rule_matches({"factor": "F1", "state": "F1.2"}, context) is False

    def test_unknown_factor_does_not_match(self) -> None:
        assert rule_matches({"factor": "F9", "state": "F9.1"}, _context()) is False

    def test_factor_without_state_raises(self) -> None:
        """Bis P0.4 wurde gegen "" verglichen — die Regel griff still nie."""

        with pytest.raises(UnknownRuleConditionError, match="braucht ein 'state'"):
            rule_matches({"factor": "F1"}, _context(factors=_factors(F1="F1.1")))

    @pytest.mark.parametrize("state", [None, "", "   ", 5, ["F1.1"]])
    def test_state_must_be_a_non_empty_text(self, state) -> None:
        """Gegenprobe 2026-08-27: Der Leerstring wurde abgewiesen, `null` nicht.

        `str(None)` ist "None" und damit wahrheitswertig — die Klausel kam
        durch die Prüfung und wurde danach gegen den Zustand "None" verglichen.
        Sichtbar fehlte ihr nichts, sie traf nur nie zu. Dasselbe galt für jede
        Nicht-Zeichenkette.
        """

        with pytest.raises(UnknownRuleConditionError, match="braucht ein 'state'"):
            rule_matches({"factor": "F1", "state": state}, _context(factors=_factors(F1="F1.1")))

    def test_state_without_factor_raises(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="ohne 'factor'"):
            rule_matches({"state": "F1.1"}, _context())


class TestVergleiche:
    @pytest.mark.parametrize(
        ("when", "value", "expected"),
        [
            ({"above": 0.3}, 0.35, True),
            ({"above": 0.3}, 0.3, False),
            ({"below": 0.3}, 0.25, True),
            ({"below": 0.3}, 0.3, False),
            ({"at_least": 0.3}, 0.3, True),
            ({"at_least": 0.3}, 0.29, False),
            ({"at_most": 0.3}, 0.3, True),
            ({"at_most": 0.3}, 0.31, False),
            ({"eq": 0.3}, 0.3, True),
            ({"eq": 0.3}, 0.31, False),
            ({"gte": 0.3}, 0.3, True),
            ({"lte": 0.3}, 0.3, True),
        ],
    )
    def test_operators_on_metric(self, when: dict, value: float, expected: bool) -> None:
        context = _context(metrics={"booking_rate": value})
        assert rule_matches({"metric": "booking_rate", **when}, context) is expected

    def test_above_and_below_are_combined(self) -> None:
        """Regression: der Zweig für regulatory_influences verkettete per elif,
        `below` wurde neben `above` nie geprüft."""

        when = {"system_property": "carbon_tax_level", "above": 50, "below": 100}
        assert rule_matches(when, _context(system_properties={"carbon_tax_level": 75})) is True
        assert rule_matches(when, _context(system_properties={"carbon_tax_level": 200})) is False
        assert rule_matches(when, _context(system_properties={"carbon_tax_level": 10})) is False

    def test_missing_value_does_not_match(self) -> None:
        """`booking_rate` gibt es im ersten Tick noch nicht — das ist ein
        Laufzeitzustand, kein Config-Fehler."""

        assert rule_matches({"metric": "booking_rate", "above": 0.3}, _context()) is False

    def test_missing_system_property_does_not_match(self) -> None:
        assert rule_matches({"system_property": "gibt_es_nicht", "above": 1}, _context()) is False


class TestTick:
    def test_shorthand_is_equality(self) -> None:
        assert rule_matches({"tick": 5}, _context(tick=5)) is True
        assert rule_matches({"tick": 5}, _context(tick=4)) is False

    def test_range_via_metric(self) -> None:
        when = {"metric": "tick", "at_least": 3}
        assert rule_matches(when, _context(tick=3)) is True
        assert rule_matches(when, _context(tick=2)) is False

    @pytest.mark.parametrize("tick", [3.7, 0.5, -1.5])
    def test_a_fractional_tick_raises(self, tick) -> None:
        """Gegenprobe 2026-08-27: `rule_matches` verglich über `int(...)`, das
        die Nachkommastelle abschneidet — `{"tick": 3.7}` griff in Tick 3. Ein
        Zahlendreher sah damit aus wie eine Regel, die woanders greift.
        Ein Tick ist ein Tick (Invariante 5)."""

        with pytest.raises(UnknownRuleConditionError, match="ganze Zahl"):
            rule_matches({"tick": tick}, _context(tick=3))

    def test_an_integral_float_is_still_fine(self) -> None:
        """JSON kennt kein int: `3.0` ist eine zulässige Schreibweise für 3."""

        assert rule_matches({"tick": 3.0}, _context(tick=3))

    def test_shorthand_with_operator_raises(self) -> None:
        """Die alte Fassung ignorierte den Wert stillschweigend, sobald ein
        Operator danebenstand."""

        with pytest.raises(UnknownRuleConditionError, match="verträgt sich nicht"):
            rule_matches({"tick": 5, "gte": 3}, _context())


class TestStrukturfehler:
    def test_unknown_key_raises(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="unbekannte Bedingung"):
            rule_matches({"metrik": "booking_rate", "above": 0.3}, _context())

    def test_operator_without_subject_raises(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="ohne Bezugsgröße"):
            rule_matches({"above": 0.3}, _context())

    def test_subject_without_operator_raises(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="ohne Vergleich"):
            rule_matches({"metric": "booking_rate"}, _context())

    def test_two_numeric_subjects_raise(self) -> None:
        """Der Vergleich ließe sich keiner der beiden zuordnen."""

        when = {"metric": "booking_rate", "system_property": "carbon_tax_level", "above": 1}
        with pytest.raises(UnknownRuleConditionError, match="mehrere Bezugsgrößen"):
            rule_matches(when, _context())

    def test_non_numeric_comparison_raises(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="keine Zahl"):
            rule_matches({"metric": "booking_rate", "above": "viel"}, _context())

    def test_rule_id_is_named(self) -> None:
        with pytest.raises(UnknownRuleConditionError, match="f7_oil_stress"):
            check_when({"quatsch": 1}, rule_id="f7_oil_stress")


class TestLeereKlausel:
    def test_empty_when_matches(self) -> None:
        """Keine Bedingung schränkt nichts ein. Ob eine Regel *ohne* Bedingung
        zulässig ist, entscheidet `validation.py`, nicht der Evaluator."""

        assert rule_matches({}, _context()) is True
        assert rule_matches(None, _context()) is True

    def test_empty_when_passes_structural_check(self) -> None:
        check_when({})


class TestBeschreibung:
    """`describe_when` und `rule_matches` müssen dieselbe Klausel meinen —
    der Protokollgenerator hatte vorher seine eigene, unvollständige Lesart."""

    def test_empty_when_is_immer(self) -> None:
        assert describe_when({}) == "immer"

    def test_factor(self) -> None:
        assert describe_when({"factor": "F1", "state": "F1.2"}) == "Faktor F1 = F1.2"

    def test_system_property(self) -> None:
        assert describe_when({"system_property": "carbon_tax_level", "above": 50}) == (
            "`carbon_tax_level` > 50"
        )

    def test_at_least_is_rendered(self) -> None:
        """Die alte Fassung kannte nur above/below und ließ at_least weg."""

        assert "≥" in describe_when({"system_property": "saf_mandate_share", "at_least": 0.05})

    def test_metric_is_rendered(self) -> None:
        """Die alte Fassung kannte `metric` überhaupt nicht."""

        assert describe_when({"metric": "booking_rate", "below": 0.25}) == "`booking_rate` < 0.25"

    def test_tick(self) -> None:
        assert describe_when({"tick": 5}) == "Tick = 5"

    def test_combined(self) -> None:
        described = describe_when({"factor": "F4", "state": "F4.2", "tick": 3})
        assert described == "Faktor F4 = F4.2, Tick = 3"


class TestRuntimeMetrics:
    def test_as_mapping_covers_known_metrics(self) -> None:
        metrics = RuntimeMetrics(
            tick=2,
            booking_rate=0.4,
            prior_booking_rate=None,
            cost_pressure=None,
            cost_index=None,
            ticket_price=None,
            demand_level=None,
            carbon_tax_level=None,
            saf_mandate_share=None,
            fuel_price_change=None,
            oil_price_index=None,
        )
        assert set(metrics.as_mapping()) == set(KNOWN_METRICS)
        assert metrics.as_mapping()["booking_rate"] == 0.4

    def test_from_metrics_builds_context(self) -> None:
        metrics = RuntimeMetrics(
            tick=7,
            booking_rate=0.4,
            prior_booking_rate=None,
            cost_pressure=None,
            cost_index=None,
            ticket_price=None,
            demand_level=None,
            carbon_tax_level=None,
            saf_mandate_share=None,
            fuel_price_change=None,
            oil_price_index=None,
        )
        context = RuleContext.from_metrics(metrics, factors={}, system_properties={"x": 1.0})
        assert context.tick == 7
        assert rule_matches({"metric": "booking_rate", "above": 0.3}, context) is True
        assert rule_matches({"tick": 7}, context) is True


class TestSelbeKlauselUeberallGleich:
    """Das Abnahmekriterium von P0.4.

    Dieselbe Klausel wird durch alle drei Aufrufstellen geschickt — die
    Faktor-Regeln, die Shift-Regeln der Bevölkerung und die Aktivierung der
    regulatorischen Kostentreiber. Vor P0.4 hatte jede ihren eigenen Evaluator
    mit eigenem Vokabular, und keine meldete, was sie nicht verstand.

    ``metric``-Klauseln fehlen bei den Kostentreibern bewusst: Die Kostenrechnung
    hat keine Metrik-Momentaufnahme (``cost_pressure`` ist selbst eine davon).
    Statt dort still nie zu greifen, weist `validation.py` sie ab — siehe
    `TestValidierungDerKlauseln`.
    """

    TICK = 4
    CARBON_TAX = 120.0

    FACTOR_CLAUSES = [
        {"factor": "F6", "state": "F6.2"},
        {"factor": "F6", "state": "F6.1"},
        {"system_property": "carbon_tax_level", "above": 50},
        {"system_property": "carbon_tax_level", "at_least": 120},
        {"system_property": "carbon_tax_level", "at_least": 130},
        {"system_property": "carbon_tax_level", "above": 50, "below": 100},
        {"tick": 4},
        {"tick": 5},
    ]
    METRIC_CLAUSES = [
        {"metric": "booking_rate", "below": 0.25},
        {"metric": "booking_rate", "above": 0.25},
        {"metric": "tick", "at_least": 3},
    ]

    @classmethod
    def _properties(cls, **kwargs):
        from src.models.property_models import BaselineTrajectory, PropertiesConfig, SystemProperty

        return PropertiesConfig(
            system_properties=[
                SystemProperty(
                    id="carbon_tax_level",
                    trajectory=BaselineTrajectory(baseline=cls.CARBON_TAX),
                )
            ],
            **kwargs,
        )

    @classmethod
    def _expected(cls, when: dict) -> bool:
        metrics = {name: None for name in KNOWN_METRICS}
        metrics.update({"tick": cls.TICK, "booking_rate": 0.2})
        context = RuleContext(
            tick=cls.TICK,
            factors=_factors(F6="F6.2"),
            metrics=metrics,
            system_properties={"carbon_tax_level": cls.CARBON_TAX},
        )
        return rule_matches(when, context)

    @pytest.mark.parametrize("when", FACTOR_CLAUSES + METRIC_CLAUSES)
    def test_sampler_agrees(self, when: dict) -> None:
        from src.models.property_models import ShiftRule
        from src.population.population_sampler import apply_factor_shifts

        metrics = {name: None for name in KNOWN_METRICS}
        metrics.update({"tick": self.TICK, "booking_rate": 0.2})
        person = _person()

        shifted = apply_factor_shifts(
            [person],
            [
                ShiftRule(
                    id="probe",
                    when=when,
                    effect={"property": "price_sensitivity", "delta": 0.1},
                )
            ],
            _factors(F6="F6.2"),
            {"carbon_tax_level": self.CARBON_TAX},
            tick=self.TICK,
            metrics=metrics,
        )
        fired = shifted[0].price_sensitivity > person.price_sensitivity
        assert fired is self._expected(when)

    @pytest.mark.parametrize("when", FACTOR_CLAUSES + METRIC_CLAUSES)
    def test_factor_rule_agrees(self, when: dict) -> None:
        from src.config_loader import build_initial_state
        from src.market.factor_dynamics import apply_factor_rules
        from src.models.property_models import FactorRule, FactorRuleEffect

        state = build_initial_state()
        state.clock.current_tick = self.TICK
        state.environment.factors["F6"].current_state = "F6.2"
        state.market_metrics = {"booking_rate": 0.2}
        state.properties = self._properties(
            factor_rules=[
                FactorRule(
                    id="probe",
                    factor_id="F6",
                    when=when,
                    effect=FactorRuleEffect(set_state="F6.1"),
                )
            ]
        )

        fired = bool(apply_factor_rules(state))
        assert fired is self._expected(when)

    @pytest.mark.parametrize("when", FACTOR_CLAUSES)
    def test_regulatory_influence_agrees(self, when: dict) -> None:
        from src.market.simulation_functions import compute_cost_pressure
        from src.models.property_models import RegulatoryInfluence

        kwargs = {
            "factors": _factors(F6="F6.2"),
            "system_properties": {"carbon_tax_level": self.CARBON_TAX},
        }
        baseline = compute_cost_pressure(self.TICK, self._properties(), **kwargs)
        with_rule = compute_cost_pressure(
            self.TICK,
            self._properties(
                regulatory_influences=[
                    RegulatoryInfluence(id="probe", cost_contribution=25.0, when=when)
                ]
            ),
            **kwargs,
        )
        assert (with_rule > baseline) is self._expected(when)

    def test_at_least_now_fires_in_sampler(self) -> None:
        """Der Kernbefund von P0.4: Diese Regel griff im Sampler still nie."""

        from src.models.property_models import ShiftRule
        from src.population.population_sampler import apply_factor_shifts

        person = _person()
        shifted = apply_factor_shifts(
            [person],
            [
                ShiftRule(
                    id="at_least_probe",
                    when={"system_property": "carbon_tax_level", "at_least": 100},
                    effect={"property": "price_sensitivity", "delta": 0.1},
                )
            ],
            {},
            {"carbon_tax_level": 120.0},
        )
        assert shifted[0].price_sensitivity > person.price_sensitivity

    def test_tick_now_fires_in_sampler(self) -> None:
        from src.models.property_models import ShiftRule
        from src.population.population_sampler import apply_factor_shifts

        rule = ShiftRule(
            id="tick_probe",
            when={"tick": 3},
            effect={"property": "price_sensitivity", "delta": 0.1},
        )
        person = _person()

        matching = apply_factor_shifts([person], [rule], {}, {}, tick=3)
        assert matching[0].price_sensitivity > person.price_sensitivity

        other = apply_factor_shifts([person], [rule], {}, {}, tick=2)
        assert other[0].price_sensitivity == person.price_sensitivity


class TestValidierungDerKlauseln:
    """Was der Evaluator zur Laufzeit nicht unterscheiden kann, fängt die
    Config-Prüfung vor dem Start ab (P0.4)."""

    @staticmethod
    def _properties(**kwargs):
        from src.models.property_models import BaselineTrajectory, PropertiesConfig, SystemProperty

        return PropertiesConfig(
            system_properties=[
                SystemProperty(id="carbon_tax_level", trajectory=BaselineTrajectory(baseline=50.0))
            ],
            **kwargs,
        )

    def test_shipped_config_is_clean(self) -> None:
        """Die ausgelieferte properties.json darf durch alle neuen Prüfungen."""

        from src.config_loader import load_properties_config
        from src.validation import validate_properties_config

        assert validate_properties_config(load_properties_config()) == []

    def test_shift_rule_without_when_is_rejected(self) -> None:
        from src.models.property_models import ShiftRule
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                shift_rules=[
                    ShiftRule(id="ohne_bedingung", effect={"property": "price_sensitivity"})
                ]
            )
        )
        assert any("darf nicht leer sein" in error for error in errors)

    def test_factor_rule_without_when_is_rejected(self) -> None:
        from src.models.property_models import FactorRule, FactorRuleEffect
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                factor_rules=[
                    FactorRule(id="ohne", factor_id="F1", effect=FactorRuleEffect(set_state="F1.2"))
                ]
            )
        )
        assert any("darf nicht leer sein" in error for error in errors)

    def test_regulatory_influence_may_be_unconditional(self) -> None:
        """Ein Kostentreiber ohne Bedingung gilt schlicht immer."""

        from src.models.property_models import RegulatoryInfluence
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                regulatory_influences=[RegulatoryInfluence(id="immer", cost_contribution=5.0)]
            )
        )
        assert errors == []

    def test_regulatory_influence_rejects_metric(self) -> None:
        from src.models.property_models import RegulatoryInfluence
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                regulatory_influences=[
                    RegulatoryInfluence(
                        id="metrik",
                        cost_contribution=5.0,
                        when={"metric": "booking_rate", "above": 0.3},
                    )
                ]
            )
        )
        assert any("nicht auswertbar" in error for error in errors)

    def test_unknown_metric_name_is_rejected(self) -> None:
        """Zur Laufzeit sieht ein Tippfehler wie ein fehlender Wert aus — hier
        nicht."""

        from src.models.property_models import ShiftRule
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                shift_rules=[
                    ShiftRule(
                        id="tippfehler",
                        when={"metric": "bokking_rate", "above": 0.3},
                        effect={"property": "price_sensitivity", "delta": 0.1},
                    )
                ]
            )
        )
        assert any("unbekannte Metrik" in error for error in errors)

    def test_unknown_system_property_is_rejected(self) -> None:
        from src.models.property_models import FactorRule, FactorRuleEffect
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                factor_rules=[
                    FactorRule(
                        id="tippfehler",
                        factor_id="F2",
                        when={"system_property": "carbon_tax_lvl", "above": 50},
                        effect=FactorRuleEffect(set_state="F2.2"),
                    )
                ]
            )
        )
        assert any("unbekannte Systemgröße" in error for error in errors)

    def test_structural_error_is_reported_not_raised(self) -> None:
        """`validate_properties_config` sammelt, es wirft nicht — sonst käme der
        Befund im Dashboard nie in der Fehlerliste an."""

        from src.models.property_models import ShiftRule
        from src.validation import validate_properties_config

        errors = validate_properties_config(
            self._properties(
                shift_rules=[
                    ShiftRule(
                        id="quatsch",
                        when={"gibts_nicht": 1},
                        effect={"property": "price_sensitivity", "delta": 0.1},
                    )
                ]
            )
        )
        assert any("unbekannte Bedingung" in error for error in errors)


class TestVerdrahtungImEchtenLauf:
    """Die Gegenprobe vom 2026-08-27 fand hier eine Lücke.

    Die Tests oben rufen `apply_factor_shifts` direkt und reichen Tick und
    Metriken selbst hinein. Ob die **Pipeline** sie durchreicht, prüfte keiner
    — man konnte `tick=current_tick` im Sampler durch `tick=0` ersetzen und
    `metrics=metrics` im Environment-Node durch `metrics=None`, ohne dass ein
    Test rot wurde. Genau diese Verdrahtung ist aber die Zusage des Pakets:
    Eine `shift_rule` mit `tick`- oder `at_least`-Bedingung soll im echten Lauf
    greifen, nicht nur in einem Direktaufruf.
    """

    @staticmethod
    def _awareness_over_ticks(rules: list, ticks=(1, 2, 3)) -> list[tuple[float, float]]:
        from src.config_loader import build_initial_state
        from src.orchestration.environment_node import EnvironmentNode

        state = build_initial_state()
        state.properties.shift_rules = rules
        node = EnvironmentNode()
        seen: list[tuple[float, float]] = []
        for tick in ticks:
            state.clock.current_tick = tick
            state = node.invoke(state)
            person = state.population_individuals[0]
            seen.append((person.price_sensitivity, person.environmental_awareness))
        return seen

    def test_tick_rule_fires_only_in_its_tick(self) -> None:
        from src.models.property_models import ShiftRule

        ohne = self._awareness_over_ticks([])
        mit = self._awareness_over_ticks(
            [
                ShiftRule(
                    id="tick_probe",
                    when={"tick": 2},
                    effect={"property": "price_sensitivity", "delta": 0.2},
                )
            ]
        )
        assert mit[0][0] == ohne[0][0], "Tick 1: Regel darf nicht greifen"
        assert mit[1][0] > ohne[1][0], "Tick 2: Regel muss greifen"

    def test_metric_rule_reaches_the_sampler(self) -> None:
        """`cost_pressure` steht nur in den Metriken — kommen die nicht an,
        bleibt die Regel wirkungslos."""

        from src.models.property_models import ShiftRule

        ohne = self._awareness_over_ticks([])
        mit = self._awareness_over_ticks(
            [
                ShiftRule(
                    id="metric_probe",
                    when={"metric": "cost_pressure", "at_least": 50},
                    effect={"property": "environmental_awareness", "delta": 0.2},
                )
            ]
        )
        assert all(m[1] > o[1] for m, o in zip(mit, ohne, strict=True))


class TestOnceBleibtErhalten:
    """`once` ist seit P0.4 kein Teil des Prädikats mehr — die Aufrufer führen
    es selbst. Ungeprüft war, ob sie es auch tun."""

    @staticmethod
    def _state_with_once_rule():
        from src.config_loader import build_initial_state
        from src.models.property_models import FactorRule, FactorRuleEffect

        state = build_initial_state()
        state.clock.current_tick = 3
        state.market_metrics = {"cost_pressure": 150.0}
        state.environment.factors["F4"].current_state = "F4.1"
        state.properties.factor_rules = [
            FactorRule(
                id="einmalig",
                factor_id="F4",
                once=True,
                when={"metric": "cost_pressure", "at_least": 100},
                effect=FactorRuleEffect(set_state="F4.2"),
            )
        ]
        return state

    def test_once_rule_applies_only_once(self) -> None:
        from src.market.factor_dynamics import apply_factor_rules

        state = self._state_with_once_rule()
        assert [a.rule_id for a in apply_factor_rules(state)] == ["einmalig"]
        assert state.applied_factor_rule_ids == ["einmalig"]

        state.environment.factors["F4"].current_state = "F4.1"
        assert apply_factor_rules(state) == []
        assert state.environment.factors["F4"].current_state == "F4.1"

    def test_once_rule_is_no_longer_an_allowed_target(self) -> None:
        """Auch der Vorschlags-Filter muss `once` beachten — sonst könnte ein
        Agent den Zustand herbeiführen, den die Regel schon verbraucht hat."""

        from src.market.factor_dynamics import allowed_factor_targets, apply_factor_rules

        state = self._state_with_once_rule()
        assert "F4.2" in allowed_factor_targets(state)["F4"]

        apply_factor_rules(state)
        state.environment.factors["F4"].current_state = "F4.1"
        assert "F4.2" not in allowed_factor_targets(state)["F4"]


class TestProtokollUndAuswertungAusEinerQuelle:
    """`narrative.py` hatte seine eigene, unvollständige Lesart einer Klausel.
    Ungeprüft war, ob es die gemeinsame jetzt tatsächlich benutzt."""

    @staticmethod
    def _narrative(rules: list, tmp_path) -> str:
        from pathlib import Path

        from src.config_loader import build_initial_state
        from src.reporting.output_writer.narrative import save_final_narrative

        state = build_initial_state()
        state.clock.current_tick = 1
        state.properties.shift_rules = rules
        return Path(save_final_narrative(state, run_dir=tmp_path)).read_text(encoding="utf-8")

    def test_metric_rule_is_described(self, tmp_path) -> None:
        """Die alte Fassung kannte `metric` nicht und schrieb für eine solche
        Regel «immer» ins Protokoll — also das Gegenteil."""

        from src.models.property_models import ShiftRule

        text = self._narrative(
            [
                ShiftRule(
                    id="probe",
                    when={"metric": "booking_rate", "below": 0.25},
                    effect={"property": "price_sensitivity", "delta": 0.1},
                )
            ],
            tmp_path,
        )
        assert "`booking_rate` < 0.25" in text
        assert "Wenn immer" not in text

    def test_at_least_is_described(self, tmp_path) -> None:
        from src.models.property_models import ShiftRule

        text = self._narrative(
            [
                ShiftRule(
                    id="probe",
                    when={"system_property": "carbon_tax_level", "at_least": 80},
                    effect={"property": "price_sensitivity", "delta": 0.1},
                )
            ],
            tmp_path,
        )
        assert "≥ 80" in text

    def test_description_matches_the_evaluator(self, tmp_path) -> None:
        """Der eigentliche Punkt: dieselbe Klausel, dieselbe Quelle."""

        from src.models.property_models import ShiftRule
        from src.rule_engine import describe_when

        when = {"factor": "F4", "state": "F4.2"}
        text = self._narrative(
            [ShiftRule(id="probe", when=when, effect={"property": "price_sensitivity"})],
            tmp_path,
        )
        assert describe_when(when) in text
