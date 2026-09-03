from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from src.models.enums import DistributionType


class SetEffect(BaseModel):
    type: Literal["set"] = "set"
    value: float


class RampEffect(BaseModel):
    type: Literal["ramp"] = "ramp"
    value: float
    duration_ticks: int = 1


TrajectoryEffect = Annotated[Union[SetEffect, RampEffect], Field(discriminator="type")]


class TrajectoryRule(BaseModel):
    active_from_tick: int
    effect: TrajectoryEffect


class StepPoint(BaseModel):
    tick: int
    value: float


class BaselineTrajectory(BaseModel):
    """Constant baseline with optional tick-based overrides (set / ramp)."""

    baseline: float = 0.0
    rules: list[TrajectoryRule] = Field(default_factory=list)


class StepFunctionTrajectory(BaseModel):
    type: Literal["step_function"] = "step_function"
    points: list[StepPoint] = Field(default_factory=list)


TrajectoryConfig = Union[BaselineTrajectory, StepFunctionTrajectory]


class SystemProperty(BaseModel):
    id: str
    type: Literal["numeric", "integer", "boolean"] = "numeric"
    unit: str = ""
    description: str = ""
    source: Literal["trajectory", "runtime", "computed"] = "trajectory"
    price_component_type: Literal["none", "tax", "fee"] = "none"
    min_value: float | None = None
    max_value: float | None = None
    trajectory: BaselineTrajectory | StepFunctionTrajectory = Field(
        default_factory=BaselineTrajectory
    )

    @model_validator(mode="before")
    @classmethod
    def _parse_trajectory(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        trajectory = data.get("trajectory")
        if not isinstance(trajectory, dict):
            return data
        if trajectory.get("type") == "step_function":
            data["trajectory"] = StepFunctionTrajectory.model_validate(trajectory)
        else:
            data["trajectory"] = BaselineTrajectory.model_validate(trajectory)
        return data


class SaturationConfig(BaseModel):
    """Continuous saturation after booking (P2.1)."""

    booking_increase: float = 0.6
    utility_penalty_factor: float = 1.0


class IndividualProperty(BaseModel):
    id: str
    type: Literal["boolean", "distribution", "numeric"] = "boolean"
    prevalence: float | None = None
    enabled: bool = True
    exclusive_group: str | None = None
    saturation_decay: float | None = None
    distribution: DistributionType | None = None
    mean: float | None = None
    std_dev: float | None = None
    min_value: float | None = None
    max_value: float | None = None
    alpha: float | None = None
    beta: float | None = None
    modifiers: dict[str, float] = Field(default_factory=dict)
    #: Woher die Verteilungsparameter stammen. Freiwillig — aber wo sie steht,
    #: ist sie prüfbar, und das ist der Unterschied zwischen einer belegten und
    #: einer gesetzten Zahl (dieselbe Trennung wie bei `BookingCoefficient`).
    quelle: str = ""


class ShiftRule(BaseModel):
    id: str = ""
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)
    once: bool = False


class FactorRuleEffect(BaseModel):
    set_state: str


class FactorRule(BaseModel):
    """Deterministic factor transition triggered by runtime metrics / system properties."""

    id: str
    factor_id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: FactorRuleEffect
    priority: int = 0
    once: bool = False


class RegulatoryInfluence(BaseModel):
    """One regulatory cost driver (e.g. EU-ETS, RefuelEU) with conditional activation."""

    id: str
    description: str = ""
    cost_contribution: float = 0.0
    when: dict[str, Any] = Field(default_factory=dict)
    trajectory: BaselineTrajectory | StepFunctionTrajectory = Field(
        default_factory=BaselineTrajectory
    )

    @model_validator(mode="before")
    @classmethod
    def _parse_trajectory(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        trajectory = data.get("trajectory")
        if not isinstance(trajectory, dict):
            return data
        if trajectory.get("type") == "step_function":
            data["trajectory"] = StepFunctionTrajectory.model_validate(trajectory)
        else:
            data["trajectory"] = BaselineTrajectory.model_validate(trajectory)
        return data


class PriceCoefficientsConfig(BaseModel):
    """Configurable cost/price formula weights."""

    carbon_per_tonne: float = 0.001
    saf_premium_factor: float = 0.5
    min_ticket_price: float = 1.0
    margin_reference_fraction: float = 0.08
    margin_floor_fraction: float = 0.05
    target_booking_tolerance: float = 0.9


class PriceModelConfig(BaseModel):
    """Ticket cost from fixed base + policy properties."""

    base_price: float = 100.0
    initial_markup: float = 0.0
    compound_fuel_on_cost: bool = True
    coefficients: PriceCoefficientsConfig = Field(default_factory=PriceCoefficientsConfig)
    cost_properties: list[str] = Field(
        default_factory=lambda: [
            "fuel_price_change",
            "carbon_tax_level",
            "oil_price_index",
            "saf_mandate_share",
            "efuel_subsidy",
        ]
    )


#: Wie der Anbieter auf freie Kapazität reagiert. **Eine Wahl, keine Annahme.**
#:
#: **Der Grund ist ein Bias-Befund** (2026-08-31): Bis dahin gab es nur eine
#: Strategie — der Anbieter senkte den Preis, bis er voll war. Gemessen hieß das:
#: Kapazität +50 % erzwang Preis −25 %. Damit war die reale Lage 2015–2019
#: (**mehr Sitze bei flachen Preisen**) im Modell **nicht darstellbar**, und das
#: Werkzeug hatte eine Theorie der Preissetzung eingebaut, statt sie zur
#: Auswahl zu stellen.
#:
#: Ein Szenariowerkzeug, das nur eine Verhaltensannahme kennt, beantwortet die
#: Frage «was wäre wenn» immer nur unter dieser einen Annahme — und ein
#: Fachprüfer liest darin zu Recht einen Bias.
STRATEGIEN = ("auslastung", "marge")


class MarketFeedbackConfig(BaseModel):
    """Provider markup adjusts each tick toward the target booking rate."""

    enabled: bool = True
    #: **Wie der Anbieter preist** — `auslastung` senkt den Preis, bis die
    #: Kapazität gefüllt ist (Verhalten bis 2026-08-31 und weiterhin der
    #: Standard); `marge` hält den Aufschlag und lässt die Auslastung
    #: schwanken. Unter `marge` bleibt der Preis gleich, wenn Kapazität
    #: dazukommt — die Nachfrage darf dann wachsen, ohne dass der Preis
    #: nachgibt. Beides kommt vor, und welches gilt, ist eine Frage an das
    #: Szenario, nicht an das Modell.
    strategie: str = "auslastung"
    # Target share of population booking per tick (calibrated ~DE annual flight rate).
    target_booking_rate: float = 0.37
    markup_adjustment_per_tick: float = 0.08
    max_price_change_fraction: float = 0.08
    damping: float = 0.85
    booking_weight: float = 0.6
    marginal_cost_fraction: float = 0.33

    @field_validator("strategie")
    @classmethod
    def _strategie_ist_bekannt(cls, wert: str) -> str:
        """Ein unbekannter Name fiele sonst still auf `auslastung` zurück.

        Dieselbe Klasse von Befund wie bei den Shift-Zielen (P2.4): Wer
        `marge_` schreibt, bekäme klammheimlich die andere Strategie und
        wunderte sich über seine Zahlen.
        """

        if wert not in STRATEGIEN:
            raise ValueError(f"Unbekannte Preisstrategie {wert!r}; erlaubt sind {STRATEGIEN}")
        return wert


class MarketRule(BaseModel):
    """Declarative market feedback rule (same when/effect pattern as shift_rules)."""

    id: str
    when: dict[str, Any] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)


class BookingCoefficient(BaseModel):
    """Ein Koeffizient des Buchungsmodells — **mit seiner Herkunft** (P2.1).

    Bis P2.1 standen diese Zahlen als Literale in `booking_probability`. Sie
    bestimmen, wie stark Preis, Abgabe und Bahnalternative gegen den Nutzen
    arbeiten, und damit jede Buchungsrate, die das Produkt ausgibt — ohne dass
    irgendwo stand, woher sie kommen.

    **`quelle` ist Pflicht und trägt zwei Angaben**, weil beide auseinanderfallen:
    die *Funktionsform* (belegt) und der *Zahlenwert* (in diesem Modell
    gesetzt). `docs/research/references.md` sagt es für die Substitution
    ausdrücklich — «keine Standard-Einheitsformel, sondern modellabhängig».
    Eine Literaturangabe an eine handgesetzte Zahl zu heften wäre eine erfundene
    Provenienz, und die ist schlimmer als eine fehlende: Sie sieht aus wie eine
    Kalibrierung.
    """

    wert: float
    quelle: str

    @field_validator("quelle")
    @classmethod
    def _quelle_ist_keine_floskel(cls, v: str) -> str:
        if len(v.strip()) < 20:
            raise ValueError(
                "Die Herkunft eines Koeffizienten braucht einen Satz, kein Stichwort — "
                "sie soll einem Fachprüfer sagen, was belegt ist und was gesetzt."
            )
        return v


class AltersProfil(BaseModel):
    """Wie das Alter die Merkmale einer Person zieht (P2.4, 2026-08-31).

    **Warum das Alter hier steht und nicht in `booking_probability`:** Alter
    verursacht keine Buchung. Es wirkt über Einkommen, Lebensphase und
    Reiseanlass — und all das steht bereits als eigenes Merkmal im Nutzenterm.
    Ein zusätzlicher Alters-Term dort würde **doppelt zählen**, und die
    Nutzenfunktion ist ein Discrete-Choice-Modell über *entscheidungsrelevante
    Merkmale* (Ben-Akiva/Lerman 1985), nicht über Soziodemografie.

    Das Alter gehört deshalb **vor** die Entscheidung: Es formt beim Ziehen die
    Merkmale, mit denen die Person dann entscheidet.

    **Der Befund, der das ausgelöst hat** (gemessen am 2026-08-31): Alle
    Merkmale wurden **unabhängig** gezogen. Die Korrelation des Alters mit
    Einkommen, Zahlungsbereitschaft, Preisempfindlichkeit, Umweltbewusstsein
    und Substitutionsbereitschaft lag durchgängig unter 0,08 — reines
    Stichprobenrauschen. Ein 90-Jähriger hatte genauso wahrscheinlich ein hohes
    Einkommen und niedrige Preisempfindlichkeit wie ein 25-Jähriger. Und `age`
    war für das Verhalten **exakt** folgenlos: Alle um zwanzig Jahre zu altern
    änderte die Buchungsrate um 0,00e+00.

    **Richtung belegt, Höhe gesetzt** — dieselbe Trennung wie bei den
    Buchungskoeffizienten (P2.1), und `docs/research/references.md` sagt sie für
    das Alter ausdrücklich: «Alter wird empirisch als erklärende Variable in
    Mobilitäts- und Nachfragemodellen genutzt, **meist ohne universelle
    Formel**.» Jeder Wert unten trägt deshalb, was belegt ist und was nicht.
    """

    gipfel_alter: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=50.0,
            quelle=(
                "Alter des Einkommensmaximums über den Lebenszyklus. Die Form — ein "
                "Anstieg bis zur Lebensmitte und ein Rückgang danach — ist in der "
                "Einkommensforschung Standard (Lebenszyklus-Verdienstprofile). Der "
                "Wert 50 ist in diesem Modell **gesetzt** und nicht aus Daten "
                "geschätzt; die EU-Erwerbseinkommen erreichen ihr Maximum je nach "
                "Land und Erhebung zwischen etwa 45 und 55."
            ),
        )
    )
    gipfel_breite: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=18.0,
            quelle=(
                "Wie breit der Gipfel ist, in Jahren (Streuung der Glockenform). "
                "Belegt ist nur, dass der Abfall zu beiden Rändern allmählich und "
                "nicht sprunghaft verläuft. Der Wert ist **gesetzt**: Er ergibt bei "
                "18 Jahren rund ein Fünftel des Gipfelwerts und bei 90 Jahren rund ein "
                "Zwölftel — die Glocke ist um den Gipfel symmetrisch, die Altersspanne "
                "ist es nicht."
            ),
        )
    )
    einkommen_spanne: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.5,
            quelle=(
                "Wie weit der Einkommensfaktor zwischen Rand und Gipfel des "
                "Lebenszyklus schwankt: ±25 % um den gezogenen Basiswert, also rund "
                "Faktor 1,5 zwischen Anfang zwanzig und Lebensmitte. Die Richtung "
                "ist belegt, die **Höhe gesetzt** — reale Lebenszyklus-Profile "
                "streuen stärker, aber dieser Faktor multipliziert einen bereits "
                "gezogenen Basiswert und würde sich sonst mit ihm aufschaukeln."
            ),
        )
    )
    preissensitivitaet_kopplung: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.20,
            quelle=(
                "Wie stark eine Lage fern des Einkommensgipfels die "
                "Preisempfindlichkeit hebt. **Kein zweiter Alterseffekt**, sondern "
                "die Kehrseite desselben: Wer wenig verfügbares Einkommen hat, "
                "reagiert stärker auf den Preis — das ist in der "
                "Preiselastizitätsliteratur der Regelfall (Brons et al. 2002 führen "
                "das Einkommen ausdrücklich als Determinante). Der Wert ist gesetzt."
            ),
        )
    )
    awareness_je_jahrzehnt: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=-0.020,
            quelle=(
                "Umweltbewusstsein je Jahrzehnt Altersunterschied, bezogen auf 50 "
                "Jahre. Negativ, weil jüngere Kohorten in europäischen Erhebungen "
                "durchgängig höhere Klimabesorgnis angeben. Die **Richtung** ist "
                "belegt, die Höhe gesetzt: über die Spanne 18–90 ergibt sie rund "
                "0,14 Punkte auf einer Skala von 0 bis 1 — bewusst klein gegenüber "
                "der individuellen Streuung, weil Alter dort ein schwacher "
                "Prädiktor ist."
            ),
        )
    )
    substitution_je_jahrzehnt: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=-0.015,
            quelle=(
                "Bereitschaft, die Bahn statt des Flugzeugs zu nehmen, je Jahrzehnt "
                "Altersunterschied. Negativ aus zwei belegten Richtungen: Jüngere "
                "nutzen den Schienenverkehr stärker, und lange Bahnfahrten setzen "
                "körperliche Belastbarkeit und Zeitbudget voraus. Höhe gesetzt."
            ),
        )
    )

    def lebenszyklus(self, alter: float) -> float:
        """Wo im Erwerbslebenszyklus diese Person steht — 1,0 am Gipfel, gegen 0 an den Rändern.

        Eine Glockenform und keine Treppe: Ein Sprung an einer Altersgrenze
        erzeugte zwei künstlich verschiedene Gruppen, wo es einen Übergang gibt.
        """

        import math

        breite = max(1.0, self.gipfel_breite.wert)
        return math.exp(-((alter - self.gipfel_alter.wert) ** 2) / (2.0 * breite**2))


class BookingModelConfig(BaseModel):
    """Die Koeffizienten der Buchungsentscheidung (P2.1).

    Sie standen als Literale in `src/population/population_sampler.py`. Hier
    sind sie sichtbar, änderbar und tragen je eine Herkunftsangabe.
    """

    verfuegbarkeit_gewicht: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.5,
            quelle=(
                "Wie stark das **Angebot** auf die Buchungsentscheidung wirkt: "
                "`gewicht × ln(kapazitaet_index)` im Nutzen. Mehr Kapazität heißt in "
                "der Wirklichkeit mehr Frequenzen und mehr Strecken, also niedrigere "
                "generalisierte Reisekosten — Wartezeit, Umsteigen, Zielauswahl. "
                "**Belegt ist die Form**: In einem Discrete-Choice-Modell stehen die "
                "Merkmale der Alternative im Nutzen (Ben-Akiva/Lerman 1985), und "
                "Angebotsgrößen gehen dort logarithmisch ein — damit ist der Beitrag "
                "bei unveränderter Kapazität exakt null und die Elastizität konstant. "
                "**Belegt ist auch die Richtung**: mehr Angebot, mehr Nachfrage; das "
                "ist der Mechanismus, mit dem der europäische Verkehr 2015–2019 um "
                "26 % wuchs, während die Realpreise flach blieben (P2.8). **Die Höhe "
                "ist gesetzt** und nicht geschätzt. Was 0,5 bedeutet, hängt vom "
                "Betriebspunkt ab — im Logit ist die Elastizität β·(1−p), sie ist also "
                "wie die Preiselastizität keine Konstante: gemessen **+0,18** an der "
                "ruhenden Bevölkerung bei 140 EUR (p ≈ 0,48) und **+0,37** im laufenden "
                "Modell unter `marge` (p ≈ 0,09). Beides ist deutlich schwächer als die "
                "Preiselastizität von −1,30 am selben Punkt, und dass Angebotseffekte "
                "schwächer wirken als Preiseffekte, ist der durchgängige Befund. **Eine "
                "Zahl dafür gibt die hier vorliegende Literatur nicht her** — "
                "`references.md` hat keinen Eintrag zu Frequenz- oder "
                "Angebotselastizität —, und eine Quellenangabe daran zu heften sähe aus "
                "wie eine Kalibrierung. Der Wert stand fest, **bevor** der Backtest "
                "damit gerechnet wurde."
            ),
        )
    )

    base_utility: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=2.0,
            quelle=(
                "Konstante des Nutzenterms (Ben-Akiva/Lerman 1985, McFadden 1974: "
                "Alternativenspezifische Konstante). Der Wert 2,0 ist in diesem Modell "
                "gesetzt und nicht geschätzt — er legt fest, bei welchem Preisniveau die "
                "Buchungswahrscheinlichkeit durch 0,5 geht."
            ),
        )
    )
    price_reference_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=100.0,
            quelle=(
                "Normierungsgröße, kein Verhaltensparameter: Der Ticketpreis wird darauf "
                "bezogen, damit `price_sensitivity` in einer Größenordnung um 1 liegt. "
                "Gesetzt, nicht geschätzt; verschiebt man sie, verschiebt sich die "
                "Bedeutung jeder Preisempfindlichkeit mit."
            ),
        )
    )
    substitution_weight: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=1.5,
            quelle=(
                "Gewicht der Bahnalternative gegenüber dem reinen Preisterm. Die Form "
                "folgt der diskreten Wahltheorie (Ben-Akiva/Lerman 1985), der Wert ist "
                "in diesem Modell gesetzt: `docs/research/references.md` hält fest, dass "
                "es für Substitutionseffekte keine Standard-Einheitsformel gibt."
            ),
        )
    )
    carbon_reference_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=100.0,
            quelle=(
                "Normierungsgröße für den Teil der CO₂-Abgabe oberhalb des Referenzwerts. "
                "Gesetzt wie `price_reference_eur` und aus demselben Grund."
            ),
        )
    )
    carbon_eco_baseline_eur: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=50.0,
            quelle=(
                "Ab welcher Abgabe ein Umwelt-Malus überhaupt entsteht — der Ausgangswert "
                "von `carbon_tax_level` in der ausgelieferten Konfiguration. Damit ist der "
                "Malus im Startzustand null und misst die Veränderung, nicht das Niveau."
            ),
        )
    )
    green_premium: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.1,
            quelle=(
                "Aufschlag auf die Zahlungsbereitschaft umweltbewusster Personen "
                "(Bamberg/Ajzen/Schmidt 2003: Einstellung wirkt auf die Verkehrsmittelwahl). "
                "Zehn Prozent sind gesetzt, nicht aus einer Erhebung übernommen."
            ),
        )
    )
    high_price_sensitivity_threshold: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.8,
            quelle=(
                "Ab welcher Preisempfindlichkeit der zusätzliche Abgaben-Malus greift. "
                "Gesetzt; die Begründung ist inhaltlich (wer aufs Geld schaut, spürt eine "
                "Abgabe doppelt) und nicht empirisch belegt."
            ),
        )
    )
    high_price_sensitivity_penalty: BookingCoefficient = Field(
        default_factory=lambda: BookingCoefficient(
            wert=0.3,
            quelle=(
                "Höhe dieses zusätzlichen Malus. Gesetzt wie die Schwelle darüber und aus "
                "demselben Grund ohne empirischen Beleg."
            ),
        )
    )


class PropertiesConfig(BaseModel):
    system_properties: list[SystemProperty] = Field(default_factory=list)
    individual_properties: list[IndividualProperty] = Field(default_factory=list)
    shift_rules: list[ShiftRule] = Field(default_factory=list)
    factor_rules: list[FactorRule] = Field(default_factory=list)
    regulatory_influences: list[RegulatoryInfluence] = Field(default_factory=list)
    market_rules: list[MarketRule] = Field(default_factory=list)
    price_model: PriceModelConfig = Field(default_factory=PriceModelConfig)
    market_feedback: MarketFeedbackConfig = Field(default_factory=MarketFeedbackConfig)
    saturation: SaturationConfig = Field(default_factory=SaturationConfig)
    booking_model: BookingModelConfig = Field(default_factory=BookingModelConfig)
    #: Wie das Alter die Merkmale zieht (P2.4). Siehe `AltersProfil`.
    alters_profil: AltersProfil = Field(default_factory=AltersProfil)

    def system_property_ids(self) -> list[str]:
        return [prop.id for prop in self.system_properties]

    def get_system_property(self, prop_id: str) -> SystemProperty | None:
        for prop in self.system_properties:
            if prop.id == prop_id:
                return prop
        return None
