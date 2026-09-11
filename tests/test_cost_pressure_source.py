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

    Bei der Prüfung dieses Commits (2026-08-28) kamen **zwei weitere** heraus,
    beide in derselben Datei: `evaluate_booking(properties=None)` und
    `aggregate_population_stats(properties=None)`. Ohne Angabe traten dort
    ``0.6`` und ``1.0`` an die Stelle der konfigurierten Sättigungswerte —
    heute zufällig dieselben Zahlen, nach einer Änderung im Config-Editor
    still auseinanderlaufend (nachgestellt: Sättigungssumme 195.25 gegen
    468.60).

    **Deshalb ist die Liste unten nicht mehr der Wächter.** Eine
    handgepflegte Aufzählung findet einen Rückfall auf den bereits bekannten
    Stellen, aber nie einen **übersehenen Geschwisterfall** — genau daran ist
    der erste Anlauf gescheitert. Den übernimmt
    `TestKeinKontextparameterEntgehtDemSweep` weiter unten: ein AST-Durchlauf
    über ``src/``, mit einer benannten Ausnahmeliste statt eines Vorsatzes.
    Die Liste hier bleibt als ausdrücklicher Anker für die Stellen, an denen
    der Fehler tatsächlich aufgetreten ist.
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
        # `rng` seit P2.1: Ein selbst besorgter Generator waere in jedem Tick
        # derselbe -- es buchten immer dieselben Individuen.
        # `system_properties` seit dem 2026-09-03: Die Kapazitaetsschranke gehoert
        # vor die Saettigung, also in diese Funktion. Ein Default hiesse "keine
        # Kapazitaet" -- und das ist eine andere Zahl, kein Fehler.
        (
            "src.population.population_sampler",
            "evaluate_booking",
            ("properties", "system_properties", "rng"),
        ),
        ("src.population.population_sampler", "aggregate_population_stats", ("properties",)),
        # `verfuegbarkeit` seit B2: das Angebot ist ein Merkmal der Alternative
        # und gehoert in den Nutzen. Ein Default waere "Kapazitaet unveraendert"
        # -- eine Aussage ueber die Welt, die niemand getroffen haette.
        ("src.population.population_sampler", "booking_probability", ("verfuegbarkeit",)),
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


class TestKeinKontextparameterEntgehtDemSweep:
    """Der Wächter, den die Liste oben nicht sein kann.

    Eine handgepflegte Aufzählung hält fest, was schon bekannt ist. Sie findet
    keinen **übersehenen** Geschwisterfall — und genau daran ist der erste
    Anlauf gescheitert: Er nannte acht Stellen und erklärte, ein Sweep über
    ``src/`` finde danach keine weitere. Er fand zwei, beide in der Datei, die
    derselbe Commit angefasst hatte.

    Deshalb ist der Sweep hier ein Test statt einer einmaligen Handbewegung.
    Er läuft über den AST jeder Datei in ``src/`` und schlägt an, sobald ein
    Parameter mit Tick-Kontext einen Default trägt.

    **Die Ausnahmen sind benannt, nicht stillschweigend.** Nicht jeder
    Default dieser Namen ist die Falle: Sie liegt vor, wenn der Rückfall eine
    *erfundene Konstante* ist (``tick=0``, ``0.6``, ``None`` für „kein
    Faktor"). Leitet eine Funktion ihren Rückfall dagegen aus lebendem
    Zustand ab, den sie ohnehin hat, kann sie gar nicht anders rechnen als
    ihr Aufrufer — das ist kein Versehen, sondern Bequemlichkeit. Wer hier
    einträgt, schreibt den Grund dazu.
    """

    #: Parameternamen, die den Kontext eines Ticks tragen.
    KONTEXTNAMEN = frozenset(
        {
            "tick",
            "current_tick",
            # `round_number` ist in diesem Repo ein Tick unter anderem Namen —
            # der Environment-Node reicht ihn direkt als `tick` weiter.
            "round_number",
            "metrics",
            "properties",
            "factors",
            "system_properties",
            # `rng` seit P2.1: Ein Zufallsstrom traegt den Kontext eines Ticks
            # genauso wie `tick` selbst. Ein Default hiesse hier "irgendein
            # Generator" -- und weil `run_population_tick` in jedem Tick
            # denselben Seed bekommt, waere das in jedem Tick derselbe.
            "rng",
            # `verfuegbarkeit` seit B2 (2026-09-03): der `kapazitaet_index` des
            # Ticks. Ein Default hiesse "Kapazitaet unveraendert" -- und das ist
            # keine Abwesenheit, sondern eine Aussage ueber die Welt. Wer sie
            # trifft, soll sie hinschreiben.
            "verfuegbarkeit",
        }
    )

    #: (Funktion, Parameter) -> Grund, warum ein Default hier vertretbar ist.
    AUSNAHMEN = {
        ("mark_spoken", "round_number"): (
            "Faellt auf `self._current_round` zurueck — den Wert, den das Objekt "
            "ohnehin fuehrt. Keine erfundene Konstante."
        ),
        ("allowed_factor_targets", "properties"): (
            "Faellt auf `state.resolved_properties()` zurueck, also auf denselben "
            "State, den die Funktion als erstes Argument bekommt. Sie kann damit "
            "nicht anders rechnen als ihr Aufrufer."
        ),
    }

    @staticmethod
    def _fundstellen() -> list[tuple[str, int, str, str]]:
        import ast
        import pathlib

        treffer: list[tuple[str, int, str, str]] = []
        for pfad in sorted(pathlib.Path("src").rglob("*.py")):
            baum = ast.parse(pfad.read_text(encoding="utf-8"))
            for knoten in ast.walk(baum):
                if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                args = knoten.args
                positional = args.posonlyargs + args.args
                mit_default = positional[len(positional) - len(args.defaults) :]
                kwonly = [a for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
                for arg in mit_default + kwonly:
                    if arg.arg in TestKeinKontextparameterEntgehtDemSweep.KONTEXTNAMEN:
                        treffer.append((str(pfad), knoten.lineno, knoten.name, arg.arg))
        return treffer

    def test_no_context_parameter_carries_a_default(self) -> None:
        offen = [
            f"{pfad}:{zeile}  {funktion}({parameter}=...)"
            for pfad, zeile, funktion, parameter in self._fundstellen()
            if (funktion, parameter) not in self.AUSNAHMEN
        ]
        assert not offen, (
            "Kontextparameter mit Default gefunden:\n  "
            + "\n  ".join(offen)
            + "\n\nEntweder den Default entfernen (der Regelfall) oder die Stelle "
            "in AUSNAHMEN eintragen — mit Grund, warum ihr Rueckfall aus lebendem "
            "Zustand kommt und nicht aus einer erfundenen Konstante."
        )

    def test_every_exception_still_exists(self) -> None:
        """Eine Ausnahme fuer eine Stelle, die es nicht mehr gibt, verdeckt
        beim naechsten Mal eine echte."""

        gefunden = {(funktion, parameter) for _, _, funktion, parameter in self._fundstellen()}
        verwaist = sorted(set(self.AUSNAHMEN) - gefunden)
        assert not verwaist, f"AUSNAHMEN nennt Stellen, die es nicht mehr gibt: {verwaist}"

    def test_the_sweep_would_notice_a_relapse(self) -> None:
        """Der Sweep prueft sich selbst: Die zehn Stellen aus der Liste oben
        muessen ihm auffallen, wenn sie einen Default zurueckbekaemen."""

        namen = {parameter for _, _, parameter in ()} or set()
        for _, _, parameter in TestKeinKontextparameterHatEinenDefault.KONTEXTPARAMETER:
            namen.update(parameter)
        assert namen <= self.KONTEXTNAMEN, (
            "Die Liste oben nennt Parameter, die der Sweep gar nicht kennt: "
            f"{sorted(namen - self.KONTEXTNAMEN)}"
        )
