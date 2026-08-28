"""P0.7 — der Kostendruck kommt aus einer Quelle.

`compute_cost_pressure` wurde an zwei Stellen ohne Faktoren und Systemgrößen
gerufen. Beide Parameter waren optional und fielen auf ``None`` zurück, was
bedeutete: kein Faktor steht in irgendeinem Zustand, also greift kein bedingter
regulatorischer Kostentreiber. Wer sie vergaß, bekam still eine andere Zahl.

Zwei Aufrufer hatten sie vergessen — der Environment-Node und der
Vorschau-Zweig im Agenten-Prompt. Deshalb prüft dieses Modul beides: dass
dieselbe Lage überall denselben Kostendruck ergibt, **und** dass ein dritter
Aufrufer die Angabe nicht mehr weglassen kann.
"""

from __future__ import annotations

import pytest

from src.config_loader import build_initial_state
from src.market.property_engine import resolve_system_properties
from src.market.simulation_functions import compute_cost_pressure, compute_market_metrics

#: Die Lagen, in denen sich die bedingten Kostentreiber unterscheiden.
#: `airport_infrastructure_levy` hat keine Bedingung und gilt überall.
LAGEN = [
    ("F2.1", "F4.1", "F6.1"),
    ("F2.1", "F4.2", "F6.1"),
    ("F2.2", "F4.1", "F6.1"),
    ("F2.2", "F4.2", "F6.2"),
]


def _state(f2: str, f4: str, f6: str):
    state = build_initial_state()
    state.environment.factors["F2"].current_state = f2
    state.environment.factors["F4"].current_state = f4
    state.environment.factors["F6"].current_state = f6
    return state


class TestDerKontextIstPflicht:
    """Ein Default, der still ein anderes Ergebnis liefert, ist die Falle selbst.

    Beide Parameter waren optional. Ein vierter Aufrufer, der sie vergisst,
    bekäme wieder lautlos eine Zahl ohne die bedingten Kostentreiber — statt
    eines Fehlers. Deshalb sind sie seit P0.7 Pflicht: Wer wirklich keine
    Faktoren hat, sagt das mit ``factors={}``.
    """

    def test_cost_pressure_requires_the_context(self) -> None:
        properties = build_initial_state().resolved_properties()
        with pytest.raises(TypeError, match="factors"):
            compute_cost_pressure(10, properties)  # type: ignore[call-arg]

    def test_market_metrics_requires_the_context(self) -> None:
        properties = build_initial_state().resolved_properties()
        with pytest.raises(TypeError, match="factors"):
            compute_market_metrics(10, properties, previous_price=100.0)  # type: ignore[call-arg]

    def test_an_empty_context_is_allowed_but_explicit(self) -> None:
        """Es geht nicht darum, leere Faktoren zu verbieten — nur darum, dass
        sie eine Aussage sind und kein Versehen."""

        properties = build_initial_state().resolved_properties()
        ohne = compute_cost_pressure(10, properties, factors={}, system_properties={})
        assert ohne > 0


class TestBedingteKostentreiberWirken:
    @pytest.mark.parametrize(("f2", "f4", "f6"), LAGEN)
    def test_the_factor_state_moves_the_cost_pressure(self, f2: str, f4: str, f6: str) -> None:
        """Ohne Kontext war der Kostendruck für **jede** Faktorlage derselbe —
        das war der Befund."""

        state = _state(f2, f4, f6)
        properties = state.resolved_properties()
        blind = compute_cost_pressure(10, properties, factors={}, system_properties={})
        sehend = compute_cost_pressure(
            10,
            properties,
            factors=state.environment.factors,
            system_properties=resolve_system_properties(10, properties),
        )
        assert sehend > blind, "keine bedingte Regel greift — dann prüft der Test nichts"

    def test_the_unconditional_driver_applies_either_way(self) -> None:
        """`airport_infrastructure_levy` hat ein leeres `when` und gilt immer.
        Der alte Pfad war also nicht völlig blind, nur blind für alles Bedingte —
        die genaue Aussage ist wichtig, wenn jemand die Zahlen nachrechnet."""

        properties = build_initial_state().resolved_properties()
        blind = compute_cost_pressure(10, properties, factors={}, system_properties={})
        ohne_treiber = properties.model_copy(update={"regulatory_influences": []})
        gar_keine = compute_cost_pressure(10, ohne_treiber, factors={}, system_properties={})
        assert blind > gar_keine


class TestBeideAufrufstellenStimmenUeberein:
    """Das Abnahmekriterium von P0.7."""

    @pytest.mark.parametrize(("f2", "f4", "f6"), LAGEN)
    def test_environment_node_sees_the_regulatory_costs(self, f2: str, f4: str, f6: str) -> None:
        """Der Environment-Node berechnet den Kostendruck selbst. Bis P0.7 ohne
        Faktoren — er landete so in `state.market_metrics` und im
        Vortick-Preis, den die Bevölkerung im ersten Tick sieht."""

        from src.orchestration.environment_node import EnvironmentNode

        state = _state(f2, f4, f6)
        state.clock.current_tick = 1
        properties = state.resolved_properties()
        faktoren = dict(state.environment.factors)

        gelaufen = EnvironmentNode().invoke(state)
        gemessen = gelaufen.market_metrics["cost_pressure"]

        # Gegen den *gleichen* Kostenindex rechnen, den der Node benutzt hat.
        # Eine erste Fassung verglich gegen `cost_index=1.0` und war dadurch
        # unscharf: Der Node kommt über die Treibstoffinflation auf einen
        # höheren Index, und der allein machte den Wert schon größer als den
        # blinden Vergleichswert — der Test blieb grün, auch wenn der Node die
        # Faktoren gar nicht mitgab. Gefunden bei der Mutationsprüfung.
        index = gelaufen.market_metrics["cost_index"]
        richtig = compute_cost_pressure(
            1,
            properties,
            cost_index=index,
            factors=faktoren,
            system_properties=resolve_system_properties(1, properties),
        )
        blind = compute_cost_pressure(
            1, properties, cost_index=index, factors={}, system_properties={}
        )
        assert richtig > blind, "keine bedingte Regel greift — dann prüft der Test nichts"
        assert gemessen == pytest.approx(richtig)

    @pytest.mark.parametrize(("f2", "f4", "f6"), LAGEN)
    def test_the_agent_preview_shows_the_same_number(self, f2: str, f4: str, f6: str) -> None:
        """Der Vorschau-Zweig im Agenten-Prompt greift genau dann, wenn
        `state.market_metrics` leer ist — also im ersten Tick jedes Laufs, weil
        die Agenten vor dem Environment-Node laufen. Er zeigte dort einen
        Kostendruck ohne die bedingten Kostentreiber: Dem Agenten wurde eine
        andere Zahl gesagt, als die Simulation benutzt. Das greift Invariante 1
        an — die Zahlen kommen aus Python, aber es müssen dieselben sein.
        """

        from src.agents.agent_node import AgentNode

        state = _state(f2, f4, f6)
        state.clock.current_tick = 10
        state.market_metrics = {}
        properties = state.resolved_properties()

        agent = next(a for a in state.agents if a.id == "provider")
        text = AgentNode(agent, llm=lambda _: "{}")._format_market_metrics(state)
        assert "preview from properties.json" in text, "der Vorschau-Zweig greift hier nicht"

        gezeigt = next(
            float(zeile.split(":")[1])
            for zeile in text.splitlines()
            if zeile.strip().startswith("- cost_pressure:")
        )
        richtig = compute_market_metrics(
            10,
            properties,
            previous_price=100.0,
            previous_demand=1.0,
            factors=state.environment.factors,
            system_properties=resolve_system_properties(10, properties),
        )["cost_pressure"]
        assert gezeigt == pytest.approx(richtig)


class TestKeinKontextparameterHatEinenDefault:
    """Die Verallgemeinerung von P0.7 — als Test statt als Vorsatz.

    Der Befund war nie „diese eine Funktion hat einen Default". Er war: Ein
    Parameter, der den Kontext eines Ticks trägt, darf keinen haben, weil sein
    Weglassen kein Fehler ist, sondern eine **andere Zahl**. `factors=None`
    hieß "kein Faktor steht irgendwo", `tick=0` hieß "es gibt keinen Tick" —
    beides ohne Meldung, beides mit stillen Folgen im Ergebnis.

    P0.7 hat das für die zwei Marktfunktionen geschlossen. Bei der Prüfung des
    Pakets (2026-08-27) lagen dieselben Defaults noch in der
    Bevölkerungshälfte: `apply_factor_shifts(tick=0, metrics=None)` und
    `run_population_tick(current_tick=0, metrics=None)`. Eine `shift_rule` mit
    `tick`- oder `metric`-Bedingung wäre bei einem vergessenen Argument wieder
    still nie gegriffen — genau der Zustand, den P0.4 beseitigen sollte.

    Dieser Test hält die Regel für alle vier Stellen fest, damit sie nicht ein
    fünftes Mal einzeln gefunden werden muss. Wer eine neue Funktion mit
    Tick-Kontext baut, trägt sie hier ein.
    """

    #: (Modul, Funktion, Parameter, die keinen Default haben dürfen)
    KONTEXTPARAMETER = [
        (
            "src.market.simulation_functions",
            "compute_cost_pressure",
            ("factors", "system_properties"),
        ),
        (
            "src.market.simulation_functions",
            "compute_market_metrics",
            ("factors", "system_properties"),
        ),
        ("src.population.population_sampler", "apply_factor_shifts", ("tick", "metrics")),
        ("src.population.population_sampler", "run_population_tick", ("current_tick", "metrics")),
        ("src.market.simulation_functions", "compose_ticket_price", ("properties", "tick")),
        ("src.market.simulation_functions", "apply_market_feedback", ("properties", "tick")),
        ("src.market.market_feedback", "initial_provider_markup", ("tick",)),
        ("src.market.market_feedback", "initial_ticket_price", ("tick",)),
        ("src.population.population_sampler", "evaluate_booking", ("properties",)),
        ("src.population.population_sampler", "aggregate_population_stats", ("properties",)),
    ]

    @pytest.mark.parametrize(("modul", "funktion", "parameter"), KONTEXTPARAMETER)
    def test_it_has_no_default(self, modul: str, funktion: str, parameter: tuple[str, ...]) -> None:
        import importlib
        import inspect

        signatur = inspect.signature(getattr(importlib.import_module(modul), funktion))

        for name in parameter:
            assert name in signatur.parameters, f"{funktion} kennt '{name}' nicht mehr"
            p = signatur.parameters[name]
            assert p.default is inspect.Parameter.empty, (
                f"{funktion}({name}=...) hat wieder einen Default. Ein weggelassener "
                "Kontext liefert damit still ein anderes Ergebnis, statt laut zu "
                "scheitern — siehe P0.7."
            )

    @pytest.mark.parametrize(("modul", "funktion", "parameter"), KONTEXTPARAMETER)
    def test_it_is_keyword_only(
        self, modul: str, funktion: str, parameter: tuple[str, ...]
    ) -> None:
        """Positionell übergeben ließe sich der Kontext still vertauschen."""

        import importlib
        import inspect

        signatur = inspect.signature(getattr(importlib.import_module(modul), funktion))
        for name in parameter:
            assert (
                signatur.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
            ), f"{funktion}({name}) ist nicht keyword-only"
