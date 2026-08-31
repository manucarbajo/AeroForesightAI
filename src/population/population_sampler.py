"""Persistent population sampling and booking.

Individuals are created once, shifted by config rules each tick, then evaluated
for booking deterministically from WTP + logit utility.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from src.models.enums import DistributionType
from src.models.population_models import (
    SEGMENT_LABEL_MAP,
    AgeGroupStats,
    Individual,
    PopulationConfig,
    PopulationStats,
    SegmentStats,
)
from src.models.property_models import (
    BookingModelConfig,
    IndividualProperty,
    PropertiesConfig,
    ShiftRule,
)
from src.models.state_models import DEFAULT_SEED, FactorState
from src.rule_engine import KNOWN_METRICS, RuleContext, rule_matches

# `DEFAULT_LOGIT_THRESHOLD` ist mit P2.1 entfallen. Gegen 0,5 zu vergleichen
# hieß, die Sigmoid zu berechnen und dann wegzuwerfen: Weil sie monoton ist,
# war `p >= 0.5` identisch mit `utility >= 0`. Gezogen wird jetzt gegen die
# Wahrscheinlichkeit (`evaluate_booking`).
# Die Koeffizienten des Buchungsmodells stehen seit P2.1 in
# `PropertiesConfig.booking_model` — als Daten mit Herkunftsangabe statt als
# Literale hier. `DEFAULT_GREEN_PREMIUM`, `HIGH_PRICE_SENSITIVITY_THRESHOLD`,
# `HIGH_PRICE_SENSITIVITY_PENALTY` und `DEFAULT_CARBON_ECO_BASELINE` sind damit
# entfallen; ihre Werte und ihre Begründung stehen in
# `src/models/property_models.BookingModelConfig`.


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def buchungsstrom(seed: int, tick: int) -> np.random.Generator:
    """Der Zufallsstrom **eines Ticks** eines **bestimmten Laufs** (P2.1).

    Der Fallstrick, den der Projektplan seit dem 2026-08-26 benannt hat, und er
    ist keiner der Theorie: `run_population_tick` bekommt in **jedem** Tick
    denselben `state.config.seed`. Ein naiv daraus gebauter Generator zöge in
    jedem Tick dieselbe Zahlenfolge — es buchten immer dieselben Individuen,
    und die Buchungsrate würde zur Stufenfunktion. Reproduzierbar, aber falsch,
    und schwer zu bemerken, weil die Zahlen plausibel aussehen.

    `SeedSequence([seed, tick])` mischt beide zu einem eigenen Strom: gleicher
    Lauf und gleicher Tick ergeben dieselbe Folge, verschiedene Ticks
    verschiedene. Das ist die Eigenschaft, auf der P2.6 (Ensemble) aufsetzt.
    """

    return np.random.default_rng(np.random.SeedSequence([int(seed), int(tick)]))


def _get_individual_property(
    properties: PropertiesConfig,
    prop_id: str,
) -> IndividualProperty | None:
    for prop in properties.individual_properties:
        if prop.id == prop_id:
            return prop
    return None


#: Wie viel Wahrscheinlichkeitsmasse eine Verteilung höchstens an ihre Grenzen
#: verlieren darf, bevor sie als falsch parametrisiert gilt.
#:
#: **Zehn Prozent, und die Zahl ist ein Deckel, kein Ideal.** Etwas Klemmung ist
#: bei einer beschränkten Größe normal — eine Normalverteilung um 45 mit
#: Streuung 15 verliert an einer Untergrenze von 2 fast nichts. Wer ein Zehntel
#: verliert, hat dagegen keine geklemmte Verteilung mehr, sondern einen Stapel
#: an der Wand.
#:
#: **Der Anlass ist gemessen** (P2.9, 2026-08-31): `age` stand als `lognormal`
#: mit `mean: 73.0, std_dev: 1.0` in der Config. `_sample_lognormal` liest
#: `mean` als **Median**, die Verteilung hat damit den Mittelwert 120 und legt
#: **41,8 %** ihrer Masse über die Obergrenze 90. Genau dieser Anteil landete
#: dort — 41 % der Bevölkerung waren exakt 90 Jahre alt, und niemand hat es
#: bemerkt, weil `np.clip` still ist.
KLEMM_DECKEL = 0.10


class VerteilungGeklemmt(ValueError):
    """Eine Verteilung verliert zu viel Masse an ihre Grenzen.

    Kein Rechenfehler, sondern eine **Fehlparametrisierung**: Die Ziehung tut,
    was dasteht — was dasteht, ergibt aber keine Verteilung mehr.
    """


def _klemmen(
    werte: np.ndarray | float,
    *,
    min_value: float,
    max_value: float,
    name: str,
) -> np.ndarray | float:
    """Auf die Grenzen bringen — und melden, wenn dabei zu viel hängen bleibt.

    **Die Prüfung braucht viele Ziehungen, nicht eine.** Eine einzelne Ziehung
    ist entweder geklemmt oder nicht; ob die *Verteilung* falsch steht, zeigt
    sich erst am Anteil. Deshalb prüft diese Funktion nur, wenn sie ein ganzes
    Feld bekommt — bei Einzelwerten klemmt sie schweigend, wie zuvor.
    """

    geklemmt = np.clip(werte, min_value, max_value)
    if not isinstance(werte, np.ndarray) or werte.size < 50:
        return geklemmt

    anteil = float(np.mean((werte < min_value) | (werte > max_value)))
    if anteil > KLEMM_DECKEL:
        raise VerteilungGeklemmt(
            f"'{name}': {anteil:.1%} der Ziehungen liegen außerhalb von "
            f"[{min_value:g}, {max_value:g}] und würden dorthin geklemmt. "
            f"Erlaubt sind {KLEMM_DECKEL:.0%}. Die Verteilung ist falsch "
            "parametrisiert — geklemmte Masse ist kein Rand, sondern ein Stapel."
        )
    return geklemmt


def _sample_beta(rng: np.random.Generator, alpha: float, beta: float) -> float:
    return float(rng.beta(max(0.1, alpha), max(0.1, beta)))


def _sample_normal(
    rng: np.random.Generator,
    *,
    mean: float,
    std_dev: float,
    min_value: float,
    max_value: float,
) -> float:
    value = float(rng.normal(mean, max(0.001, std_dev)))
    return float(np.clip(value, min_value, max_value))


def _sample_lognormal(
    rng: np.random.Generator,
    *,
    mean: float,
    std_dev: float,
    min_value: float,
    max_value: float,
) -> float:
    """**`mean` ist der Median der Lognormalen, nicht ihr Mittelwert.**

    `mu = log(mean)` heißt: Die Hälfte der Ziehungen liegt unter *mean*. Der
    Mittelwert der Verteilung ist `mean * exp(sigma²/2)` und damit größer —
    bei `sigma = 1` um den Faktor 1,65. Das ist eine Falle im Feldnamen und in
    P2.9 als offene Frage vermerkt; hier steht es wenigstens da.
    """

    mu = np.log(max(0.01, mean))
    sigma = max(0.01, std_dev)
    value = float(rng.lognormal(mean=mu, sigma=sigma))
    return float(np.clip(value, min_value, max_value))


def pruefe_verteilung(
    rng: np.random.Generator,
    prop: IndividualProperty,
    *,
    stichprobe: int = 4000,
) -> None:
    """Einmal vorab ziehen und prüfen, ob die Parameter eine Verteilung ergeben.

    Läuft **vor** dem Aufbau der Bevölkerung, mit einem eigenen Generator: Die
    Prüfziehung darf den Zufallsstrom des Laufs nicht verschieben, sonst hinge
    die Bevölkerung daran, ob geprüft wurde.
    """

    if prop.distribution is None or prop.min_value is None or prop.max_value is None:
        return

    if prop.distribution == DistributionType.NORMAL:
        roh = rng.normal(prop.mean or 0.0, max(0.001, prop.std_dev or 1.0), stichprobe)
    elif prop.distribution == DistributionType.LOGNORMAL:
        roh = rng.lognormal(
            np.log(max(0.01, prop.mean or 1.0)), max(0.01, prop.std_dev or 1.0), stichprobe
        )
    else:
        # Beta und Uniform ziehen per Konstruktion innerhalb ihrer Grenzen.
        return

    _klemmen(roh, min_value=prop.min_value, max_value=prop.max_value, name=prop.id)


def _assign_boolean_labels(
    rng: np.random.Generator,
    properties: PropertiesConfig,
) -> dict[str, bool]:
    """Assign boolean labels.

    By default each label is drawn independently (a person may have several).
    Properties sharing the same ``exclusive_group`` are mutually exclusive —
    use only when segments are meant as personas, not overlapping traits.
    """

    labels: dict[str, bool] = {}
    grouped: dict[str, list[IndividualProperty]] = {}
    independent: list[IndividualProperty] = []

    for prop in properties.individual_properties:
        if prop.type != "boolean" or not prop.enabled:
            continue
        if prop.exclusive_group:
            grouped.setdefault(prop.exclusive_group, []).append(prop)
        else:
            independent.append(prop)

    for prop in independent:
        prevalence = prop.prevalence if prop.prevalence is not None else 0.0
        labels[prop.id] = bool(rng.random() < float(prevalence))

    for group_props in grouped.values():
        weights = [max(0.0, float(prop.prevalence or 0.0)) for prop in group_props]
        total = sum(weights)
        if total <= 0:
            for prop in group_props:
                labels[prop.id] = False
            continue
        probs = [weight / total for weight in weights]
        chosen_idx = int(rng.choice(len(group_props), p=probs))
        for index, prop in enumerate(group_props):
            labels[prop.id] = index == chosen_idx

    return labels


def initialize_population(
    properties: PropertiesConfig,
    config: PopulationConfig,
    *,
    seed: int = 42,
) -> list[Individual]:
    """Create N persistent individuals once per simulation run."""

    # **Erst prüfen, ob die Verteilungen welche sind** (P2.9). Mit eigenem
    # Generator, damit die Prüfziehung den Zufallsstrom des Laufs nicht
    # verschiebt: Sonst hinge die Bevölkerung daran, ob geprüft wurde.
    for prop in properties.individual_properties:
        if prop.type == "distribution" and prop.enabled:
            pruefe_verteilung(np.random.default_rng(0), prop)

    rng = _rng(seed)
    total_pop = config.total_population
    individuals: list[Individual] = []

    awareness_prop = _get_individual_property(properties, "environmental_awareness")
    wtp_prop = _get_individual_property(properties, "wtp_eur")
    age_prop = _get_individual_property(properties, "age")
    subst_prop = _get_individual_property(properties, "substitution_readiness")

    for person_id in range(total_pop):
        labels = _assign_boolean_labels(rng, properties)

        if awareness_prop and awareness_prop.distribution == DistributionType.BETA:
            awareness = _sample_beta(
                rng,
                awareness_prop.alpha or 2.0,
                awareness_prop.beta or 5.0,
            )
        elif awareness_prop and awareness_prop.distribution == DistributionType.NORMAL:
            awareness = _sample_normal(
                rng,
                mean=awareness_prop.mean or 0.5,
                std_dev=awareness_prop.std_dev or 0.1,
                min_value=awareness_prop.min_value or 0.0,
                max_value=awareness_prop.max_value or 1.0,
            )
        else:
            awareness = float(rng.uniform(0.2, 0.8))

        if wtp_prop and wtp_prop.distribution == DistributionType.LOGNORMAL:
            wtp = _sample_lognormal(
                rng,
                mean=wtp_prop.mean or 120.0,
                std_dev=wtp_prop.std_dev or 0.35,
                min_value=wtp_prop.min_value or 50.0,
                max_value=wtp_prop.max_value or 500.0,
            )
        elif wtp_prop and wtp_prop.distribution == DistributionType.NORMAL:
            wtp = _sample_normal(
                rng,
                mean=wtp_prop.mean or 120.0,
                std_dev=wtp_prop.std_dev or 20.0,
                min_value=wtp_prop.min_value or 50.0,
                max_value=wtp_prop.max_value or 500.0,
            )
        else:
            wtp = float(rng.uniform(80.0, 200.0))

        if age_prop and age_prop.distribution == DistributionType.NORMAL:
            age = int(
                _sample_normal(
                    rng,
                    mean=age_prop.mean or 45.0,
                    std_dev=age_prop.std_dev or 15.0,
                    min_value=age_prop.min_value or 2.0,
                    max_value=age_prop.max_value or 90.0,
                )
            )
        elif age_prop and age_prop.distribution == DistributionType.LOGNORMAL:
            age = int(
                _sample_lognormal(
                    rng,
                    mean=age_prop.mean or 45.0,
                    std_dev=age_prop.std_dev or 15.0,
                    min_value=age_prop.min_value or 2.0,
                    max_value=age_prop.max_value or 90.0,
                )
            )
        elif age_prop and age_prop.distribution == DistributionType.UNIFORM:
            age = int(rng.integers(age_prop.min_value or 2.0, (age_prop.max_value or 90.0) + 1))
        else:
            age = int(rng.integers(2, 91))

        if subst_prop and subst_prop.distribution == DistributionType.BETA:
            substitution_readiness = _sample_beta(
                rng, subst_prop.alpha or 2.0, subst_prop.beta or 5.0
            )
        elif subst_prop and subst_prop.distribution == DistributionType.NORMAL:
            substitution_readiness = _sample_normal(
                rng, subst_prop.mean or 0.5, subst_prop.std_dev or 0.2, 0.0, 1.0
            )
        else:
            substitution_readiness = float(rng.uniform(0.1, 0.9))

        base_income = 1.0
        price_sensitivity = 0.5

        for prop in properties.individual_properties:
            if prop.type == "boolean" and labels.get(prop.id):
                mods = prop.modifiers
                if "wtp_multiplier" in mods:
                    wtp *= mods["wtp_multiplier"]
                if "substitution_readiness_multiplier" in mods:
                    substitution_readiness *= mods["substitution_readiness_multiplier"]
                if "base_income_delta" in mods:
                    base_income += mods["base_income_delta"]
                if "price_sensitivity_delta" in mods:
                    price_sensitivity += mods["price_sensitivity_delta"]

        base_income = float(np.clip(base_income + rng.normal(0.0, 0.05), 0.5, 1.5))

        # **Das Alter zieht die Merkmale** (P2.4, 2026-08-31) — nach den
        # Segment-Modifikatoren und **vor** dem Klemmen, damit beides zusammen
        # in denselben Grenzen landet.
        #
        # Bis dahin wurde jedes Merkmal unabhängig gezogen: Ein 90-Jähriger
        # hatte genauso wahrscheinlich ein hohes Einkommen und niedrige
        # Preisempfindlichkeit wie ein 25-Jähriger, und `age` war für das
        # Verhalten exakt folgenlos. Alter wirkt hier über die Merkmale und
        # **nicht** als eigener Term im Nutzen — sonst zählte es doppelt.
        profil = properties.alters_profil
        zyklus = profil.lebenszyklus(age)
        jahrzehnte = (age - profil.gipfel_alter.wert) / 10.0

        base_income *= 1.0 + profil.einkommen_spanne.wert * (zyklus - 0.5)
        wtp *= 1.0 + profil.einkommen_spanne.wert * (zyklus - 0.5)
        price_sensitivity += profil.preissensitivitaet_kopplung.wert * (1.0 - zyklus)
        awareness += profil.awareness_je_jahrzehnt.wert * jahrzehnte
        substitution_readiness += profil.substitution_je_jahrzehnt.wert * jahrzehnte

        base_income = float(np.clip(base_income, 0.5, 1.5))
        price_sensitivity = float(np.clip(price_sensitivity, 0.0, 1.0))
        awareness = float(np.clip(awareness, 0.0, 1.0))
        substitution_readiness = float(np.clip(substitution_readiness, 0.0, 1.0))
        wtp = float(max(0.0, wtp))

        individuals.append(
            Individual(
                id=person_id,
                age=age,
                labels=labels,
                wtp_eur=round(wtp, 2),
                environmental_awareness=round(awareness, 4),
                substitution_readiness=round(substitution_readiness, 4),
                price_sensitivity=round(price_sensitivity, 4),
                base_income_factor=round(base_income, 4),
                income_factor=round(base_income, 4),
            )
        )

    return individuals


#: Welche Individuen-Attribute eine ``shift_rule`` verändern kann — je Ziel das
#: Attribut und seine Grenzen.
#:
#: **Das ist die Quelle, nicht eine Beschreibung daneben** (P2.4, 2026-08-31):
#: `apply_factor_shifts` wertet sie aus, `validation._validate_shift_rules`
#: prüft dagegen. Vorher stand die Liste als `if`/`elif`-Kette hier — **ohne
#: `else`**. Eine Regel auf `age` tat nichts, ein Tippfehler wie
#: `price_sensitivty` ebenso: keine Meldung, kein Fehler, nur eine Regel, die
#: nie greift. Dieselbe Klasse von Befund, gegen die Invariante 6 im
#: `rule_engine` angetreten ist — was nicht auswertbar ist, schlägt laut fehl.
#:
#: `income_factor` wirkt auf `base_income_factor`: Der laufende `income_factor`
#: wird in jedem Tick aus Basis mal `income_index` neu gebildet, ein Schreiben
#: darauf wäre im nächsten Tick weg.
SHIFT_ZIELE: dict[str, tuple[str, float, float]] = {
    "environmental_awareness": ("environmental_awareness", 0.0, 1.0),
    "price_sensitivity": ("price_sensitivity", 0.0, 1.0),
    "income_factor": ("base_income_factor", 0.0, 5.0),
}


def _mit_altersmittel(
    properties: PropertiesConfig,
    system_properties: dict[str, float],
) -> PropertiesConfig:
    """Die Altersverteilung auf das aktuell geltende Mittel setzen.

    **Kein neuer Kontextparameter** (Invariante 1): Der Wert kommt aus
    ``system_properties``, die ``run_population_tick`` ohnehin bekommt. Ein
    eigenes Argument mit Default hieße «irgendein Altersmittel» und wäre in
    jedem Tick dasselbe — genau die Falle, die die Regel abräumt.

    Fehlt die Systemgröße, bleibt alles wie es ist: Eine Config ohne
    ``altersmittel_jahre`` beschreibt eine **stationäre** Gesellschaft, und das
    ist eine gültige Aussage, kein Versehen.
    """

    mittel = system_properties.get("altersmittel_jahre")
    if mittel is None:
        return properties

    merkmale = []
    for prop in properties.individual_properties:
        if prop.id == "age" and prop.mean is not None:
            prop = prop.model_copy(update={"mean": float(mittel)})
        merkmale.append(prop)
    return properties.model_copy(update={"individual_properties": merkmale})


def apply_factor_shifts(
    individuals: list[Individual],
    shift_rules: list[ShiftRule],
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
    *,
    tick: int,
    metrics: Mapping[str, float | None] | None,
) -> list[Individual]:
    """Apply config shift rules to numeric individual attributes.

    *tick* und *metrics* kamen mit P0.4 dazu: Bis dahin hatte dieses Modul einen
    eigenen, ärmeren Evaluator, und eine ``shift_rule`` mit ``tick``- oder
    ``at_least``-Bedingung griff hier still nie. Jetzt wertet dieselbe Funktion
    aus wie für die Faktor-Regeln — dafür braucht sie denselben Kontext.

    Beide sind **Pflicht**, seit P0.7 dieselbe Falle auf der Marktseite
    abgeräumt hat. Sie hatten Defaults (``tick=0``, ``metrics=None``), und die
    bedeuteten: Tick 0 gibt es nicht, und keine Metrik hat einen Wert — eine
    ``shift_rule`` mit ``tick``- oder ``metric``-Bedingung griff bei einem
    vergessenen Argument also wieder still nie. Genau der Zustand, den P0.4
    beseitigen sollte, nur eine Ebene höher. Wer wirklich keinen Kontext hat,
    schreibt ``metrics=None`` — eine Aussage statt eines Versehens.
    """

    if not shift_rules:
        return individuals

    context = RuleContext(
        tick=tick,
        factors=factors,
        metrics=metrics if metrics is not None else {name: None for name in KNOWN_METRICS},
        system_properties=system_properties,
    )
    active_rules = [
        rule for rule in shift_rules if rule_matches(rule.when, context, rule_id=rule.id)
    ]
    if not active_rules:
        return individuals

    updated: list[Individual] = []
    for person in individuals:
        werte = {attribut: getattr(person, attribut) for attribut, _, _ in SHIFT_ZIELE.values()}
        applied_rules = list(person.applied_shift_rules)

        for index, rule in enumerate(active_rules):
            rule_id = rule.id or f"shift_rule_{index}"
            if rule.once and rule_id in applied_rules:
                continue
            effect = rule.effect
            prop_id = str(effect.get("property", ""))
            ziel = SHIFT_ZIELE.get(prop_id)
            if ziel is None:
                # **Laut statt still** (P2.4). `validation` weist eine solche
                # Regel schon beim Laden ab; wer eine Regel im Code baut, kommt
                # daran vorbei und soll es hier erfahren.
                raise ValueError(
                    f"shift_rule '{rule_id}': unbekanntes Ziel {prop_id!r}. "
                    f"Erreichbar sind {sorted(SHIFT_ZIELE)}."
                )
            attribut, unten, oben = ziel
            delta = float(effect.get("delta", 0.0))
            werte[attribut] = float(np.clip(werte[attribut] + delta, unten, oben))
            if rule.once:
                applied_rules.append(rule_id)

        updated.append(
            person.model_copy(
                update={
                    **{name: round(wert, 4) for name, wert in werte.items()},
                    "applied_shift_rules": applied_rules,
                }
            )
        )

    return updated


def booking_probability(
    person: Individual,
    *,
    ticket_price: float,
    carbon_tax: float,
    koeffizienten: BookingModelConfig,
    saturation_penalty_factor: float = 1.0,
) -> float:
    """Die Buchungswahrscheinlichkeit dieser Person — eine Zahl in [0, 1].

    **Bis P2.1 gab diese Funktion ein `bool` zurück.** Sie rechnete die Sigmoid
    und verglich sie gegen 0,5 — weil die Sigmoid monoton ist, war das
    mathematisch identisch mit `utility >= 0`. Der Logit-Teil tat nichts: Es
    wurde nie gegen die Wahrscheinlichkeit gezogen, und zwei Personen mit
    p = 0,51 und p = 0,99 buchten gleichermaßen sicher.

    Ohne Ziehung gibt es keine Verteilung, und ohne Verteilung keine
    Bandbreite — der Grund, warum P2.6 (Ensemble) ohne dieses Paket sinnlos
    wäre: Fünfzig Seeds ergäben fünfzig identische Buchungsverläufe.

    **Null heißt hier «kann nicht», nicht «will nicht».** Wer sich das Ticket
    nicht leisten kann, bucht nicht — das ist eine harte Schranke und keine
    Wahrscheinlichkeit, die bei genug Ziehungen doch einmal zuschlägt.
    """

    k = koeffizienten
    affordability_limit = (
        person.wtp_eur
        * person.income_factor
        * (1.0 + k.green_premium.wert * person.environmental_awareness)
    )
    if ticket_price > affordability_limit:
        return 0.0

    base_utility = k.base_utility.wert
    normalized_price = ticket_price / k.price_reference_eur.wert
    price_penalty = person.price_sensitivity * normalized_price
    excess_carbon = max(0.0, carbon_tax - k.carbon_eco_baseline_eur.wert)
    normalized_tax = excess_carbon / k.carbon_reference_eur.wert
    eco_penalty = person.environmental_awareness * normalized_tax
    if person.price_sensitivity > k.high_price_sensitivity_threshold.wert and normalized_tax > 0:
        eco_penalty += k.high_price_sensitivity_penalty.wert * min(1.0, normalized_tax)

    substitution_penalty = (
        person.substitution_readiness * normalized_price * k.substitution_weight.wert
    )
    saturation_penalty = person.saturation_level * saturation_penalty_factor

    utility = base_utility - price_penalty - eco_penalty - substitution_penalty - saturation_penalty
    return float(1.0 / (1.0 + np.exp(-utility)))


def evaluate_booking(
    individuals: list[Individual],
    *,
    ticket_price: float,
    carbon_tax: float,
    properties: PropertiesConfig | None,
    rng: np.random.Generator,
) -> tuple[list[Individual], PopulationStats]:
    """Evaluate booking decisions for persistent individuals.

    *properties* ist **Pflicht** (P0.7-Regel), auch wenn ``None`` zulässig
    bleibt. Der Default war genau die Falle, die diese Regel abräumt: Ohne
    Angabe treten ``0.6`` und ``1.0`` an die Stelle von
    ``saturation.booking_increase`` und ``saturation.utility_penalty_factor``
    — kein Fehler, keine Meldung, nur eine andere Zahl. Heute stimmen beide
    Konstanten zufällig mit der ausgelieferten Config überein; beide Felder
    haben aber eine eigene Bedienung im Config-Editor, und nach einer Änderung
    dort läuft die Sättigung still auseinander (nachgestellt: Summe 195.25
    gegen 468.60). Sie trägt in die Buchungsentscheidungen des nächsten Ticks.

    *rng* ist seit P2.1 **Pflicht und ohne Default** — aus demselben Grund. Ein
    Generator, den die Funktion sich selbst besorgt, wäre bei jedem Aufruf
    derselbe: Es buchten in jedem Tick dieselben Individuen, die Buchungsrate
    würde zur Stufenfunktion, und das Ergebnis sähe dabei plausibel aus. Wer den
    Strom aufbaut, weiß als Einziger, wofür er stehen soll — deshalb kommt er
    von außen (`run_population_tick`).
    """

    saturation = properties.saturation if properties is not None else None
    booking_increase = saturation.booking_increase if saturation is not None else 0.6
    penalty_factor = saturation.utility_penalty_factor if saturation is not None else 1.0
    # Ohne Config gelten die Vorgabewerte **des Modells** — nicht Literale an
    # dieser Stelle. Der Unterschied ist der aus P1.9-W5.1: Ein Rückfall auf
    # eine zweite, hier hingeschriebene Zahl wäre eine eigene Quelle; der
    # Rückfall auf `BookingModelConfig()` ist derselbe Wert wie überall sonst,
    # und er trägt seine Herkunftsangabe mit.
    koeffizienten = properties.booking_model if properties is not None else BookingModelConfig()

    booked_individuals: list[Individual] = []
    for person in individuals:
        wahrscheinlichkeit = booking_probability(
            person,
            ticket_price=ticket_price,
            carbon_tax=carbon_tax,
            koeffizienten=koeffizienten,
            saturation_penalty_factor=penalty_factor,
        )
        # **Die Ziehung** (P2.1). Vorher stand hier ein Vergleich gegen 0,5.
        # `< p` und nicht `<= p`: Bei p = 0 darf niemand buchen — das ist die
        # Unbezahlbarkeits-Schranke, und `rng.random()` liefert die 0,0 mit
        # positiver Wahrscheinlichkeit.
        booked = bool(rng.random() < wahrscheinlichkeit)
        update: dict[str, object] = {"booked": booked}
        if booked:
            new_saturation = min(1.0, person.saturation_level + booking_increase)
            update["saturation_level"] = round(new_saturation, 4)
        booked_individuals.append(person.model_copy(update=update))

    return booked_individuals, aggregate_population_stats(booked_individuals, properties=properties)


def aggregate_population_stats(
    individuals: list[Individual],
    *,
    properties: "PropertiesConfig | None",
) -> PopulationStats:
    """Aggregate booking stats overall and per segment label.

    When *properties* is provided, segments are derived dynamically from all
    boolean ``individual_properties`` (P2.2 SSOT).  Falls back to the legacy
    ``SEGMENT_LABEL_MAP`` when called without properties.

    *properties* ist **Pflicht** (P0.7-Regel), ``None`` bleibt zulässig. Der
    Default entschied still zwischen zwei Segmentierungen — dieselbe Klasse
    wie bei ``evaluate_booking``, nur in der Auswertung statt im Modell.
    """

    total_pop = len(individuals)
    total_booked = sum(1 for person in individuals if person.booked)
    total_income_factor = sum(person.income_factor for person in individuals)

    if properties is not None:
        segment_label_pairs = [
            (prop.id, prop.id)
            for prop in properties.individual_properties
            if prop.type == "boolean" and prop.enabled
        ]
    else:
        segment_label_pairs = list(SEGMENT_LABEL_MAP.items())

    segments: dict[str, SegmentStats] = {}
    for segment_id, label_id in segment_label_pairs:
        members = [person for person in individuals if person.labels.get(label_id)]
        booked = sum(1 for person in members if person.booked)
        count = len(members)
        segments[segment_id] = SegmentStats(
            segment_id=segment_id,
            share=count / total_pop if total_pop else 0.0,
            total_individuals=count,
            booked_individuals=booked,
            booking_rate=booked / count if count else 0.0,
            avg_income_factor=sum(p.income_factor for p in members) / count if count else 1.0,
        )

    age_groups_dict: dict[str, list[Individual]] = {
        "<18": [],
        "18-25": [],
        "26-35": [],
        "36-50": [],
        "51-65": [],
        ">65": [],
    }
    for person in individuals:
        if person.age < 18:
            age_groups_dict["<18"].append(person)
        elif person.age <= 25:
            age_groups_dict["18-25"].append(person)
        elif person.age <= 35:
            age_groups_dict["26-35"].append(person)
        elif person.age <= 50:
            age_groups_dict["36-50"].append(person)
        elif person.age <= 65:
            age_groups_dict["51-65"].append(person)
        else:
            age_groups_dict[">65"].append(person)

    age_stats: dict[str, AgeGroupStats] = {}
    for group, members in age_groups_dict.items():
        count = len(members)
        booked = sum(1 for person in members if person.booked)
        age_stats[group] = AgeGroupStats(
            age_group=group,
            total_individuals=count,
            booked_individuals=booked,
            booking_rate=booked / count if count else 0.0,
            avg_wtp=sum(p.wtp_eur for p in members) / count if count else 0.0,
            avg_income_factor=sum(p.income_factor for p in members) / count if count else 1.0,
            avg_awareness=sum(p.environmental_awareness for p in members) / count if count else 0.0,
        )

    return PopulationStats(
        total_population=total_pop,
        total_booked=total_booked,
        total_demand=total_booked / total_pop if total_pop else 0.0,
        avg_income_factor=total_income_factor / total_pop if total_pop else 1.0,
        segments=segments,
        age_groups=age_stats,
    )


def update_income_factors(
    individuals: list[Individual],
    income_index: float,
) -> list[Individual]:
    """Scale each individual's income_factor as base_income_factor × income_index."""
    return [
        person.model_copy(
            update={"income_factor": round(person.base_income_factor * income_index, 4)}
        )
        for person in individuals
    ]


def get_decay_rate(person: Individual, properties: PropertiesConfig) -> float:
    found_decay: float | None = None
    for prop in properties.individual_properties:
        if prop.type == "boolean" and person.labels.get(prop.id):
            if prop.saturation_decay is not None:
                if found_decay is None:
                    found_decay = prop.saturation_decay
                else:
                    found_decay = max(found_decay, prop.saturation_decay)
    return found_decay if found_decay is not None else 0.2


def run_population_tick(
    properties: PropertiesConfig,
    config: PopulationConfig,
    individuals: list[Individual] | None,
    *,
    ticket_price: float,
    carbon_tax: float,
    factors: dict[str, FactorState],
    system_properties: dict[str, float],
    seed: int = DEFAULT_SEED,
    current_tick: int,
    metrics: Mapping[str, float | None] | None,
) -> tuple[list[Individual], PopulationStats]:
    """Full population pipeline for one tick.

    *current_tick* wurde bis P0.4 entgegengenommen und nie benutzt. Es ist
    genau der Wert, den eine ``shift_rule`` mit ``tick``-Bedingung braucht, und
    wird jetzt an die Regelauswertung durchgereicht. *metrics* ist der
    dazugehörige Rest des Kontexts (`RuntimeMetrics.as_mapping()`).

    Beide sind seit P0.7 **Pflicht** — sie werden nach `apply_factor_shifts`
    durchgereicht, und ein vergessenes Argument hätte dort still die
    Tick- und Metrik-Regeln abgeschaltet.
    """

    # **Die alternde Gesellschaft ist ein exogener Verlauf** (P2.4-D,
    # 2026-08-31), kein Alterungspfad je Person. Wer neu in die Bevölkerung
    # kommt, wird aus der Verteilung gezogen, die *jetzt* gilt.
    #
    # Der Unterschied ist nicht kosmetisch: Eine mitalternde Kohorte ohne
    # Nachwuchs verliert über 40 Ticks **47,6 %** ihrer Buchungsrate und ist am
    # Ende im Schnitt 83 Jahre alt — das ist ein Jahrgang, keine Gesellschaft.
    # Eine Gesellschaft altert, weil sich die *Zusammensetzung* verschiebt, und
    # das tut sie langsam.
    properties = _mit_altersmittel(properties, system_properties)

    if not individuals:
        individuals = initialize_population(properties, config, seed=seed)

    target_population = int(system_properties.get("bevoelkerungsentwicklung", len(individuals)))
    if target_population > len(individuals):
        needed = target_population - len(individuals)
        temp_config = config.model_copy(update={"total_population": needed})
        new_seed = seed + len(individuals)
        new_individuals = initialize_population(properties, temp_config, seed=new_seed)
        start_id = max((p.id for p in individuals), default=-1) + 1
        for i, person in enumerate(new_individuals):
            new_individuals[i] = person.model_copy(update={"id": start_id + i})
        individuals.extend(new_individuals)
    elif target_population < len(individuals):
        rng = _rng(seed + len(individuals))
        to_keep = rng.choice(individuals, size=target_population, replace=False)
        individuals = list(to_keep)

    income_index = system_properties.get("income_index", 1.0)
    shifted = apply_factor_shifts(
        individuals,
        properties.shift_rules,
        factors,
        system_properties,
        tick=current_tick,
        metrics=metrics,
    )
    individuals = update_income_factors(shifted, income_index)

    individuals = [
        person.model_copy(
            update={
                "saturation_level": max(
                    0.0, round(person.saturation_level - get_decay_rate(person, properties), 4)
                )
            }
        )
        for person in individuals
    ]

    return evaluate_booking(
        individuals,
        ticket_price=ticket_price,
        carbon_tax=carbon_tax,
        properties=properties,
        rng=buchungsstrom(seed, current_tick),
    )


def run_population_sampling(
    config: PopulationConfig,
    ticket_price: float,
    carbon_tax: float,
    *,
    properties: PropertiesConfig | None = None,
    seed: int = 42,
) -> PopulationStats:
    """Backward-compatible entry point (non-persistent single-tick sample)."""

    from src.config_loader import load_properties_config

    resolved_properties = properties or load_properties_config()
    individuals, stats = run_population_tick(
        resolved_properties,
        config,
        None,
        ticket_price=ticket_price,
        carbon_tax=carbon_tax,
        factors={},
        system_properties={},
        seed=seed,
        # Eine einzelne Stichprobe ohne Lauf: Es gibt keinen Tick und keine
        # Laufzeitmetriken. Das steht jetzt da, statt aus Defaults zu folgen —
        # eine `shift_rule` mit `tick`- oder `metric`-Bedingung greift hier
        # nicht, und das ist eine Aussage, kein Versehen.
        current_tick=0,
        metrics=None,
    )
    _ = individuals
    return stats
