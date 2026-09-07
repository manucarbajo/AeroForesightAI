from dataclasses import dataclass

from src.agents.agent_dependencies import KNOWN_DEPENDENCIES
from src.agents.agent_permissions import parse_factor_permission
from src.market.property_engine import darf_in_regel_stehen
from src.models.agent_models import AgentConfig
from src.models.enums import DistributionType
from src.models.population_models import (
    ConsumerSegment,
    DistributionConfig,
    PopulationConfig,
)
from src.models.property_models import (
    FactorRule,
    PropertiesConfig,
    RampEffect,
    RegulatoryInfluence,
    ShiftRule,
    StepFunctionTrajectory,
    SystemProperty,
)
from src.models.state_models import (
    FactorState,
    SimulationClock,
    SimulationConfig,
    SimulationState,
)
from src.rule_engine import KNOWN_METRICS, UnknownRuleConditionError, check_when

#: Zulässiger Bereich für `llm.temperature`. Ollama nimmt Werte darüber
#: entgegen, liefert aber nur noch Rauschen.
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0

#: Die erste Zeile, die ein Nutzer liest, wenn seine Konfiguration abgewiesen
#: wird — **an einer Stelle** (P3.17-Nachlauf, C2 des Phase-3-Audits).
#:
#: Hier stand bis zum 2026-09-06 `"validierungsfehler:"`: klein geschrieben,
#: ohne Satzform, und an **drei** Stellen wörtlich wiederholt (hier, im
#: LLM-Zweig der CLI und als Rückfall in `run_simulation._melde_befunde`). Sie
#: ist älter als Phase 3 — aber P3.3 hat sie zur ersten Zeile befördert, die ein
#: CLI-Nutzer überhaupt sieht, und direkt neben einen ordentlich gebauten Satz
#: gestellt: «Der Zwischenstand passt nicht zu dieser Fassung:» meldet der
#: Checkpoint-Zweig zwei Zeilen weiter.
#:
#: **Der Text sagt jetzt, was passiert ist, und nicht, wie der Fehler heißt.**
#: «Validierungsfehler» ist ein Wort aus dem Code; was der Nutzer wissen muss,
#: ist, dass sein Lauf nicht startet und warum — die Liste darunter nennt die
#: Gründe, jeder mit seinem Feld.
BEFUND_KOPF = "Die Konfiguration lässt diesen Lauf nicht zu:"


class ValidationError(Exception):
    pass


class ValidationIssue(str):
    """Ein Befund, der weiß, an welchem Eingabefeld er hängt.

    Bewusst eine `str`-**Unterklasse** und kein eigenes Modell: Die Befunde
    werden heute an mehreren Stellen wie Zeichenketten behandelt —
    `validate_state` baut daraus mit `"\\n".join(...)` seine Ausnahme, die
    Oberflächen setzen sie in Listen, und mehrere Tests prüfen mit `in` gegen
    den Text. Eine Dataclass hätte jeden dieser Aufrufer gleichzeitig brechen
    müssen; so bleibt jeder von ihnen unverändert richtig, und nur wer die
    Zuordnung braucht, greift auf `.field` zu.

    *field* ist ein oberflächenneutraler Schlüssel (`seed`, `rounds`,
    `temperature`, …), kein Pfad in ein bestimmtes Datenmodell — Dashboard und
    CLI benennen dieselbe Einstellung verschieden. Wo es keine einzelne
    Einstellung gibt, an der der Befund hängt (Regeln, Agentenprofile,
    Systemgrößen), bleibt es `None`; solche Befunde gehören in eine gesammelte
    Liste, nicht an ein Feld.
    """

    field: str | None

    def __new__(cls, text: str, field: str | None = None) -> "ValidationIssue":
        issue = super().__new__(cls, text)
        issue.field = field
        return issue


def issue(text: str, field: str | None = None) -> ValidationIssue:
    return ValidationIssue(text, field)


def field_of(entry: object) -> str | None:
    """Feld eines Befunds — auch wenn er von woanders als schlichter `str` kam."""

    return getattr(entry, "field", None)


def validate_factor(factor: FactorState) -> list[str]:
    errors = []

    if not factor.possible_states:
        errors.append(f"{factor.id}: keine possible_states definiert")

    if factor.current_state not in factor.possible_states:
        errors.append(
            f"{factor.id}: current_state '{factor.current_state}' "
            f"nicht in possible_states {list(factor.possible_states.keys())}"
        )

    return errors


def validate_agent(agent: AgentConfig, factor_ids: set[str]) -> list[str]:
    """Prüft einen Agenten — inklusive der Faktoren, auf die sein Profil zeigt.

    *factor_ids* wurde bis P0.3 entgegengenommen und nie benutzt. Genau dafür war
    der Parameter gedacht: Ein Tippfehler in `agent_profiles.json` lässt den
    Agenten den Faktor sonst einfach nicht sehen — ohne Fehler, ohne Hinweis.
    """

    errors = []

    if not agent.goals:
        errors.append(f"agent '{agent.id}': keine goals definiert")

    if agent.population_config:
        errors.extend(validate_population_config(agent.population_config))

    errors.extend(_validate_agent_profile(agent, factor_ids))

    return errors


def _validate_agent_profile(agent: AgentConfig, factor_ids: set[str]) -> list[str]:
    profile = agent.profile
    if profile is None:
        # Seit P0.5 ist `agent_profiles.json` die **einzige** Quelle der
        # Faktor-Berechtigungen, und ohne Profil ist nichts erlaubt. Ein
        # fehlendes Profil schaltet damit still ab, was Invariante 2 durchsetzen
        # soll: `config_loader` vergibt keines, wenn die Datei fehlt oder den
        # Agenten nicht kennt, der Lauf rechnet klaglos zu Ende, und kein
        # Vorschlag kommt je durch. Vor P0.5 trug das hartcodierte Dict die
        # Rechte und der Fall blieb folgenlos — deshalb schwieg diese Prüfung.
        # Jetzt ist er der Ausfall selbst. Gefunden 2026-08-27.
        return [
            f"agent '{agent.id}': kein Profil in agent_profiles.json. "
            "Ohne Profil darf der Agent nichts vorschlagen — die Berechtigungen "
            "kämen still gar nicht erst zustande."
        ]

    errors: list[str] = []
    known = ", ".join(sorted(factor_ids)) if factor_ids else "keine"

    for factor_id in profile.observed_factors:
        if factor_id not in factor_ids:
            errors.append(
                f"agent '{agent.id}': observes verweist auf unbekannten Faktor "
                f"'{factor_id}' (bekannt: {known})"
            )

    for entry in profile.may_propose:
        factor_id = parse_factor_permission(entry)
        if factor_id is None:
            continue
        if factor_id not in factor_ids:
            errors.append(
                f"agent '{agent.id}': may_propose verweist auf unbekannten Faktor "
                f"'{factor_id}' (bekannt: {known})"
            )

    for dependency in profile.depends_on:
        if dependency not in KNOWN_DEPENDENCIES:
            errors.append(
                f"agent '{agent.id}': depends_on '{dependency}' ist unbekannt und würde in "
                f"jedem Tick als unerfüllt gelten (erlaubt: "
                f"{', '.join(sorted(KNOWN_DEPENDENCIES))})"
            )

    return errors


def validate_llm_settings(
    model: str,
    temperature: float,
    max_tokens: int,
    *,
    context: str,
    base_url: str,
) -> list[str]:
    """Die Regeln für Modellname, Temperatur und Antwortlänge — an *einer* Stelle.

    Diese Werte standen im Projekt an drei Orten: in `simulation_config.json`
    (`config.llm`), im Dashboard-Draft und in den CLI-Argumenten. **Seit P3.4 ist
    es einer**: Beide Oberflächen schreiben nach `config.llm`, und der Client
    entsteht daraus — geprüft wird damit genau das, womit gerechnet wird. Vorher
    war `config.llm` die einzige Stelle, die *nicht* im Lauf ankam, und das
    Dashboard musste seine Werte eigens danebenprüfen; jeder Befund stand
    dadurch doppelt da.

    *base_url* ist mit P3.4 dazugekommen — vorher prüfte niemand ihn, und ein
    leeres Feld ergab einen Aufruf gegen `/api/generate` ohne Host: ein
    Verbindungsfehler, dem niemand die Ursache ansieht.

    *context* sagt, wo der Wert herkommt, damit die Meldung zum Ort passt.
    """

    errors: list[str] = []

    if not str(model).strip():
        errors.append(issue(f"{context}: Modellname darf nicht leer sein", "model"))

    endpunkt = str(base_url).strip()
    if not endpunkt:
        errors.append(issue(f"{context}: Endpunkt darf nicht leer sein", "base_url"))
    elif not endpunkt.startswith(("http://", "https://")):
        errors.append(
            issue(
                f"{context}: Endpunkt '{base_url}' braucht ein Schema "
                "(http:// oder https://) — sonst erreicht der Aufruf keinen Host",
                "base_url",
            )
        )

    if not (MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE):
        errors.append(
            issue(
                f"{context}: temperature ({temperature}) muss zwischen "
                f"{MIN_TEMPERATURE} und {MAX_TEMPERATURE} liegen",
                "temperature",
            )
        )

    if max_tokens < 1:
        errors.append(
            issue(f"{context}: max_tokens ({max_tokens}) muss mindestens 1 sein", "max_tokens")
        )

    return errors


def validate_config(config: SimulationConfig) -> list[str]:
    """Pflichtfelder und Wertebereiche der Lauf-Konfiguration.

    Bis P0.3 stand hier `return []` — die Funktion wurde von `validate_state`
    aufgerufen, als würde sie prüfen. Gemeldet wird nur, was einen Lauf falsch
    oder unmöglich macht; eine leere `description` etwa blockiert nichts und
    bleibt erlaubt.
    """

    errors: list[str] = []

    if not config.name.strip():
        errors.append(issue("config: name darf nicht leer sein", "simulation_name"))

    errors.extend(
        validate_llm_settings(
            config.llm.model,
            config.llm.temperature,
            config.llm.max_tokens,
            # **«Sprachmodell» und nicht «config.llm»** (P3.4). Der
            # Herkunftsort steht jetzt nur noch an einer Stelle, also liest
            # *jede* Oberfläche diese Meldung — und «config.llm» ist der Name
            # eines Datenfelds, nicht der einer Einstellung. Bis dahin sah ein
            # Dashboard-Nutzer «Technik: …», weil die Oberfläche eigens
            # danebenprüfte; genau diese Doppelprüfung ist weg.
            context="Sprachmodell",
            base_url=config.llm.base_url,
        )
    )

    # Der einzige Wert hier, der heute schon einen Lauf zerreißt: `default_rng`
    # im Bevölkerungs-Sampling wirft bei negativem Seed `ValueError: expected
    # non-negative integer` — mitten im ersten Tick, ohne Bezug zum Seed.
    if config.seed is not None and config.seed < 0:
        errors.append(
            issue(
                f"config: seed ({config.seed}) muss 0 oder größer sein — "
                "negative Werte brechen die Bevölkerungsziehung ab",
                "seed",
            )
        )

    return errors


def validate_clock(clock: SimulationClock) -> list[str]:
    errors = []

    if clock.max_ticks < 1:
        errors.append(issue("max_ticks muss mindestens 1 sein", "rounds"))

    if clock.tick_unit != "tick":
        errors.append("tick_unit muss 'tick' sein")

    return errors


def validate_distribution(dist: DistributionConfig, context: str = "") -> list[str]:
    errors = []
    prefix = f"{context}: " if context else ""

    if dist.min_value >= dist.max_value:
        errors.append(
            f"{prefix}min_value ({dist.min_value}) muss kleiner als max_value ({dist.max_value}) sein"
        )

    if dist.type == DistributionType.NORMAL:
        if dist.std_dev <= 0:
            errors.append(f"{prefix}std_dev muss positiv sein")
        if not (dist.min_value <= dist.mean <= dist.max_value):
            errors.append(f"{prefix}mean ({dist.mean}) muss zwischen min und max liegen")

    return errors


def validate_segments(segments: list[ConsumerSegment]) -> list[str]:
    errors = []

    if not segments:
        errors.append("keine consumer-segmente definiert")
        return errors

    total_share = sum(seg.share for seg in segments)
    if abs(total_share - 1.0) > 1e-6:
        errors.append(f"segmentanteile summieren sich auf {total_share}, erwartet 1.0")

    seen_ids = set()
    for seg in segments:
        if seg.share <= 0 or seg.share > 1:
            errors.append(f"segment '{seg.id}': share ({seg.share}) muss zwischen 0 und 1 liegen")

        if seg.id in seen_ids:
            errors.append(f"segment-id '{seg.id}' ist doppelt vergeben")
        seen_ids.add(seg.id)

        errors.extend(
            validate_distribution(seg.price_elasticity, f"segment '{seg.id}' price_elasticity")
        )
        errors.extend(validate_distribution(seg.income_level, f"segment '{seg.id}' income_level"))
        errors.extend(
            validate_distribution(
                seg.environmental_awareness, f"segment '{seg.id}' environmental_awareness"
            )
        )

    return errors


def validate_population_config(pop: PopulationConfig) -> list[str]:
    errors = []

    if pop.total_population < 1:
        errors.append("total_population muss mindestens 1 sein")

    errors.extend(validate_segments(pop.segments))

    return errors


def validate_properties_config(properties: PropertiesConfig) -> list[str]:
    errors = []
    seen_ids: set[str] = set()

    for index, prop in enumerate(properties.system_properties):
        prefix = f"system_properties[{index}]"
        if not prop.id:
            errors.append(f"{prefix}: id darf nicht leer sein")
            continue
        if prop.id in seen_ids:
            errors.append(f"{prefix}: id '{prop.id}' ist doppelt vergeben")
        seen_ids.add(prop.id)

        if prop.min_value is not None and prop.max_value is not None:
            if prop.min_value >= prop.max_value:
                errors.append(f"{prefix} '{prop.id}': min_value muss kleiner als max_value sein")

        errors.extend(_validate_trajectory(prop, prefix))

    errors.extend(_validate_factor_rules(properties.factor_rules))
    errors.extend(_validate_shift_rules(properties.shift_rules))
    errors.extend(_validate_regulatory_influences(properties.regulatory_influences))
    errors.extend(_validate_rule_property_names(properties))

    return errors


def _validate_when(
    when: dict[str, object],
    prefix: str,
    *,
    allow_empty: bool,
) -> list[str]:
    """Prüft eine ``when``-Klausel beim Laden statt erst im Tick (P0.4).

    Der Evaluator wirft zur Laufzeit — dann steckt der Fehler aber schon mitten
    in einem Lauf. Dieselbe Prüfung hier vorgezogen meldet ihn vor dem Start.

    *allow_empty* trennt die Regelarten: Ein Kostentreiber ohne Bedingung gilt
    schlicht immer und ist zulässig. Eine ``factor_rule`` oder ``shift_rule``
    ohne Bedingung würde dagegen in **jedem** Tick feuern — das ist fast sicher
    ein vergessenes ``when`` und wird abgewiesen.
    """

    if not when:
        if allow_empty:
            return []
        return [f"{prefix}: when darf nicht leer sein (die Regel würde in jedem Tick greifen)"]

    try:
        check_when(when)
    except UnknownRuleConditionError as exc:
        return [f"{prefix}: {exc}"]
    return []


def _validate_factor_rules(rules: list[FactorRule]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, rule in enumerate(rules):
        prefix = f"factor_rules[{index}]"
        if not rule.id:
            errors.append(f"{prefix}: id darf nicht leer sein")
        elif rule.id in seen_ids:
            errors.append(f"{prefix}: id '{rule.id}' ist doppelt vergeben")
        seen_ids.add(rule.id)
        if not rule.factor_id:
            errors.append(f"{prefix}: factor_id darf nicht leer sein")
        if not rule.effect.set_state:
            errors.append(f"{prefix}: effect.set_state darf nicht leer sein")
        errors.extend(_validate_when(rule.when, prefix, allow_empty=False))
    return errors


def _validate_shift_rules(rules: list[ShiftRule]) -> list[str]:
    """Bedingung **und Wirkung** prüfen (Wirkung seit P2.4, 2026-08-31).

    Bis dahin prüfte diese Funktion nur die ``when``-Klausel. Das ``effect``
    kam ungeprüft durch, und zur Laufzeit fiel ein unbekanntes Ziel still
    heraus: Eine Regel auf ``age`` tat nichts, ein Tippfehler wie
    ``price_sensitivty`` ebenso — keine Meldung, nur eine Regel, die nie greift.
    Genau die Sorte Befund, gegen die Invariante 6 im ``rule_engine`` steht.
    """

    from src.population.population_sampler import SHIFT_ZIELE

    errors: list[str] = []
    for index, rule in enumerate(rules):
        prefix = f"shift_rules[{index}]" + (f" '{rule.id}'" if rule.id else "")
        errors.extend(_validate_when(rule.when, prefix, allow_empty=False))

        effect = rule.effect or {}
        ziel = str(effect.get("property", ""))
        if not ziel:
            errors.append(f"{prefix}: effect ohne 'property'")
        elif ziel not in SHIFT_ZIELE:
            errors.append(
                f"{prefix}: unbekanntes Ziel '{ziel}'. Eine shift_rule erreicht "
                f"{sorted(SHIFT_ZIELE)} — alles andere greift nie."
            )

        if "delta" in effect:
            try:
                float(effect["delta"])
            except (TypeError, ValueError):
                errors.append(f"{prefix}: 'delta' ist keine Zahl ({effect['delta']!r})")

    return errors


def _validate_regulatory_influences(influences: list[RegulatoryInfluence]) -> list[str]:
    errors: list[str] = []
    for index, influence in enumerate(influences):
        prefix = f"regulatory_influences[{index}]" + (f" '{influence.id}'" if influence.id else "")
        errors.extend(_validate_when(influence.when, prefix, allow_empty=True))
        if "metric" in (influence.when or {}):
            # Die Kostenrechnung hat keine Metrik-Momentaufnahme — `cost_pressure`
            # ist selbst eine davon. Eine solche Bedingung könnte dort nie
            # zutreffen. Das laut zu sagen ist der Sinn von P0.4; still nie zu
            # greifen war der Befund.
            errors.append(
                f"{prefix}: 'metric' ist bei regulatory_influences nicht auswertbar "
                "(die Kostenrechnung kennt keine Laufzeit-Metriken). "
                "Für eine Bedingung auf den Systemzustand 'system_property' benutzen."
            )
    return errors


def _validate_rule_property_names(properties: PropertiesConfig) -> list[str]:
    """Prüft die *Namen* in ``when``-Klauseln gegen die bekannten Vokabulare.

    Der Evaluator tut das bewusst nicht: Zur Laufzeit ist "Wert nicht da" ein
    normaler Zustand (`booking_rate` gibt es im ersten Tick noch nicht). Ein
    Tippfehler im Namen sieht davon ununterscheidbar aus — und wäre damit
    wieder genau die stille Wirkungslosigkeit, gegen die P0.4 antritt. Hier
    sind beide Vokabulare bekannt, also fällt er hier auf.

    **Seit P3.1 prüft er nicht nur den Namen, sondern die Quelle** (2026-09-05).
    Eine Systemgröße mit ``source in {"runtime", "computed"}`` — heute
    ``provider_markup`` und ``ticket_price`` — existiert, liefert einer Regel
    aber die statische Baseline statt des Laufzeitwerts. Der Name stimmt, die
    Zahl ist veraltet: dieselbe stille Wirkungslosigkeit, nur eine Ebene
    tiefer. Warum das Durchreichen des Laufzeitwerts die schlechtere Antwort
    wäre, steht bei :func:`~src.market.property_engine.darf_in_regel_stehen` —
    dort liegt die Regel, hier nur ihre Anwendung.
    """

    known_properties = set(properties.system_property_ids())
    errors: list[str] = []

    groups: list[tuple[str, list[object]]] = [
        ("factor_rules", list(properties.factor_rules)),
        ("shift_rules", list(properties.shift_rules)),
        ("regulatory_influences", list(properties.regulatory_influences)),
    ]
    for label, rules in groups:
        for index, rule in enumerate(rules):
            when = getattr(rule, "when", {}) or {}
            rule_id = getattr(rule, "id", "")
            prefix = f"{label}[{index}]" + (f" '{rule_id}'" if rule_id else "")
            metric = when.get("metric")
            if metric is not None and str(metric) not in KNOWN_METRICS:
                errors.append(
                    f"{prefix}: unbekannte Metrik '{metric}'. "
                    f"Bekannt sind: {', '.join(sorted(KNOWN_METRICS))}"
                )
            prop = when.get("system_property")
            if prop is None:
                continue
            if str(prop) not in known_properties:
                errors.append(f"{prefix}: unbekannte Systemgröße '{prop}'")
                continue
            eintrag = properties.get_system_property(str(prop))
            if eintrag is not None and not darf_in_regel_stehen(eintrag):
                errors.append(
                    f"{prefix}: Systemgröße '{prop}' ist laufzeitgebunden "
                    f"(source '{eintrag.source}') und in einer Bedingung nicht lesbar. "
                    "Eine Regel darauf prüfte gegen die Trajektorien-Baseline, nicht "
                    "gegen den Wert des laufenden Ticks. Erlaubt sind Systemgrößen mit "
                    "source 'trajectory'; für den Preis oder den Aufschlag des laufenden "
                    "Ticks gibt es 'metric'."
                )
    return errors


def _validate_trajectory(prop: SystemProperty, prefix: str) -> list[str]:
    errors: list[str] = []
    trajectory = prop.trajectory

    if isinstance(trajectory, StepFunctionTrajectory):
        if not trajectory.points:
            errors.append(f"{prefix} '{prop.id}': step_function braucht mindestens einen Punkt")
        for point_index, point in enumerate(trajectory.points):
            if point.tick < 0:
                errors.append(f"{prefix} '{prop.id}': points[{point_index}].tick muss >= 0 sein")
        return errors

    for rule_index, rule in enumerate(trajectory.rules):
        if rule.active_from_tick < 0:
            errors.append(
                f"{prefix} '{prop.id}': rules[{rule_index}].active_from_tick muss >= 0 sein"
            )
        if isinstance(rule.effect, RampEffect) and rule.effect.duration_ticks < 1:
            errors.append(
                f"{prefix} '{prop.id}': rules[{rule_index}].duration_ticks muss >= 1 sein"
            )

    return errors


@dataclass(frozen=True)
class Horizontluecke:
    """Ein Verlauf, dessen letzter Stützpunkt vor dem Ende des Laufs liegt."""

    property_id: str
    letzter_stuetzpunkt: int
    max_ticks: int

    @property
    def ticks_darueber(self) -> int:
        return self.max_ticks - self.letzter_stuetzpunkt

    def __str__(self) -> str:
        return (
            f"`{self.property_id}` endet bei Tick {self.letzter_stuetzpunkt}, der Lauf "
            f"geht bis {self.max_ticks} — {self.ticks_darueber} Ticks halten den letzten "
            "Wert."
        )


def _letzter_stuetzpunkt(prop: SystemProperty) -> int | None:
    """Ab welchem Tick ein Verlauf nichts Neues mehr sagt.

    **Eine flache Baseline hat keinen Horizont.** Sie ist überall definiert und
    sagt «konstant» — das ist eine Aussage und keine aufgebrauchte Vorgabe.
    Einen Horizont hat nur, wer Stützpunkte gesetzt hat und hinter dem letzten
    weiterläuft.
    """

    trajectory = prop.trajectory
    if isinstance(trajectory, StepFunctionTrajectory):
        return max((point.tick for point in trajectory.points), default=None)
    return max((regel.active_from_tick for regel in trajectory.rules), default=None)


def horizontluecken(properties: PropertiesConfig, *, max_ticks: int) -> list[Horizontluecke]:
    """Welche Verläufe vor dem Ende des Laufs aufhören (P2.8, Restposition).

    **Der Befund kam aus dem Backtest und ist genau deshalb unsichtbar
    gewesen:** `bevoelkerungsentwicklung` ist eine `step_function` mit vier
    Stützpunkten, der letzte bei Tick 30. `_resolve_step_function` hält danach
    still den letzten Wert — für eine Stufenfunktion **korrektes** Verhalten,
    und es gibt keine Meldung, weil nichts falsch ist. Der Backtest läuft 120
    Ticks, davon 90 mit eingefrorener Bevölkerung; die vier ausgelieferten
    Rahmen laufen 50 Ticks bei einer Kurve, die bei 30 endet.

    **Deshalb ist das hier kein Fehler und steht nicht in
    `collect_state_errors`.** Über den letzten Stützpunkt hinauszulaufen ist
    zulässig und meistens gewollt: Eine CO₂-Abgabe, die ihren Endwert erreicht
    hat, *bleibt* dort. Was fehlte, war nicht eine Schranke, sondern die
    **Auskunft** — dass ein Viertel des Laufs mit einer fortgeschriebenen
    Vorgabe rechnet, soll dastehen, statt dass man es aus der Config erschließen
    muss.

    Der Aufrufer entscheidet, was er damit tut: Der Runner schreibt es ins Log,
    der Assistent zeigt es vor dem Start.
    """

    luecken = []
    for prop in properties.system_properties:
        letzter = _letzter_stuetzpunkt(prop)
        if letzter is not None and max_ticks > letzter:
            luecken.append(
                Horizontluecke(
                    property_id=prop.id, letzter_stuetzpunkt=letzter, max_ticks=max_ticks
                )
            )
    return sorted(luecken, key=lambda h: h.letzter_stuetzpunkt)


def collect_state_errors(state: SimulationState) -> list[str]:
    """Alle Befunde einsammeln, ohne zu werfen.

    Der Einstieg für alles, was Fehler *anzeigen* statt abbrechen will — das
    Dashboard weist einen Lauf damit vor dem Start ab, statt ihn mitten im
    ersten Tick scheitern zu lassen. Gesammelt wird vollständig: Wer eine Config
    repariert, will alle Fehler auf einmal sehen und nicht einen pro Anlauf.
    """

    errors: list[str] = []

    errors.extend(validate_config(state.config))
    errors.extend(validate_properties_config(state.resolved_properties()))
    errors.extend(validate_clock(state.clock))

    factor_ids = set(state.environment.factors.keys())
    for factor in state.environment.factors.values():
        errors.extend(validate_factor(factor))

    for agent in state.agents:
        errors.extend(validate_agent(agent, factor_ids))

    if not state.agents:
        errors.append("keine agenten konfiguriert")

    if not state.environment.factors:
        errors.append("keine faktoren konfiguriert")

    return errors


def validate_state(state: SimulationState) -> list[str]:
    """Wie `collect_state_errors`, wirft aber bei Befunden.

    Der werfende Weg für den Runner: ein Lauf mit kaputter Config soll gar nicht
    erst anfangen. Der Rückgabewert ist deshalb immer die leere Liste — wer die
    Befunde *lesen* will, nimmt `collect_state_errors`.
    """

    errors = collect_state_errors(state)

    if errors:
        raise ValidationError(BEFUND_KOPF + "\n" + "\n".join(f"  - {e}" for e in errors))

    return errors
