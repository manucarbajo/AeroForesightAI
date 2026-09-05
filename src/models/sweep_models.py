"""Sweep configuration models for M8 (Foresight-Szenarien).

A SweepConfig defines parameter overrides that modify the default simulation
configuration to model a specific future scenario. Overrides can target:
- system_property trajectory baselines and rules
- initial factor states
- simulation clock settings (max_ticks)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class PropertyOverride(BaseModel):
    """Override for a single system property's trajectory."""

    property_id: str
    baseline: float | None = None
    rules: list[dict[str, Any]] | None = None  # replaces trajectory.rules if provided


class FactorOverride(BaseModel):
    """Override for a factor's initial state."""

    factor_id: str
    initial_state: str  # e.g. "F2.2"


class MilestoneCheck(BaseModel):
    """A checkpoint to evaluate during the sweep at a specific tick."""

    tick: int
    description: str
    check_property: str | None = None  # system property to read
    check_factor: str | None = None  # factor to read
    expected_value: Any = None  # optional expected value for logging
    expected_factor_state: str | None = None  # e.g. "F2.2"


#: Was eine Datei unter `configs/sweeps/` ist. **Zwei Dinge lagen dort bis P2.2
#: ununterscheidbar nebeneinander**, und der Szenario-Vergleich startete beide:
#: vier Behauptungen über eine mögliche Welt und vier Stresstests der Engine.
#: «Totaler Wahnsinn (Alle Parameter)» stand gleichrangig neben «Business as
#: Usual» — einem Kunden wurde damit ein Belastungstest als Zukunft angeboten.
ARTEN = ("rahmen", "stresstest")


class Kohaerenz(BaseModel):
    """Warum die Verläufe eines Rahmenszenarios zusammen eine Welt ergeben.

    **Das ist die Umsetzung von Variante C** ([Entscheidung vom 2026-08-29],
    bestätigt am 2026-08-31 nach dem Backtest): Die Kohärenz eines Bündels wird
    **in Prosa mit Quellen** begründet, nicht von einem Algorithmus geprüft. Die
    CIB-Matrix misst nachweislich Polarität statt Plausibilität, und eine neu
    erhobene Matrix wäre ein Versprechen von Präzision, das die Daten nicht
    decken.

    **Die Trennung von Form und Wert ist dieselbe wie bei den
    Buchungskoeffizienten (P2.1), und sie ist der Kern der Ehrlichkeit hier:**
    Belegt ist die *Storyline* — dass diese Entwicklungen zusammen auftreten
    können und warum. **Nicht belegt sind die Zahlen**, mit denen sie im Lauf
    eingestellt werden: bei welchem Tick die CO₂-Abgabe auf welchen Wert
    springt, ist gesetzt und nicht geschätzt. `vorbehalt` sagt das je Szenario,
    damit eine Quellenangabe nicht wie eine Kalibrierung aussieht.
    """

    #: Die Welt in einem Satz — was hier behauptet wird.
    these: str
    #: Warum diese Entwicklungen zusammengehören statt nur zusammen dazustehen.
    begruendung: str
    #: Womit die Storyline belegt ist. Leere Liste ist unzulässig — dann ist es
    #: eine Meinung, und die gehört nicht als Rahmenszenario ausgeliefert.
    quellen: list[str] = Field(min_length=1)
    #: Was hier **nicht** belegt ist. Pflicht, aus demselben Grund wie oben.
    vorbehalt: str

    @field_validator("these", "begruendung", "vorbehalt")
    @classmethod
    def _nicht_leer(cls, wert: str) -> str:
        """Ein Platzhalter ist schlimmer als eine Lücke — er sieht aus wie eine
        Begründung. Dieselbe Prüfung wie bei `BookingCoefficient.quelle`."""

        if len(wert.strip()) < 30:
            raise ValueError(
                "Zu kurz für eine Begründung — Variante C trägt die Kohärenz in "
                "Prosa; ein Halbsatz erfüllt das nicht."
            )
        return wert.strip()


class SweepConfig(BaseModel):
    """Configuration for a single parameter sweep scenario."""

    id: str
    name: str
    description: str
    rationale: str = ""  # Why these parameters were chosen
    #: **Rahmen oder Stresstest** (P2.2). Der Standard ist `stresstest`, nicht
    #: `rahmen`: Ein im Dashboard gesichertes Experiment ist zunächst kein
    #: begründetes Weltbild, und die stillere Voreinstellung wäre die falsche —
    #: sie machte jede gespeicherte Datei ungefragt zu einer Aussage über die
    #: Zukunft. Wer ein Rahmenszenario will, sagt es und begründet es.
    art: str = "stresstest"
    #: Pflicht für `art == "rahmen"`, sonst leer. Siehe `Kohaerenz`.
    kohaerenz: Kohaerenz | None = None

    @model_validator(mode="after")
    def _rahmen_traegt_seine_begruendung(self) -> "SweepConfig":
        if self.art not in ARTEN:
            raise ValueError(f"Unbekannte Art {self.art!r}; erlaubt sind {ARTEN}")
        if self.art == "rahmen" and self.kohaerenz is None:
            raise ValueError(
                f"Rahmenszenario {self.id!r} ohne `kohaerenz`. Variante C begründet "
                "die Kohärenz in Prosa mit Quellen — ohne sie ist es ein Stresstest."
            )
        return self

    max_ticks: int = 50
    #: Wie der Anbieter in **dieser Welt** preist — `auslastung` oder `marge`.
    #:
    #: **P2.8-B hat die Strategie zu einer Wahl gemacht und sie zugleich
    #: unerreichbar gelassen** (P2.10, 2026-09-03): «Welche gilt, ist eine Frage
    #: an das Szenario, nicht an das Modell» — nur konnte ein Szenario sie nicht
    #: stellen. Sie lebt in `market_rules[].effect`, und ein Sweep überschreibt
    #: nur Systemgrößen. Wer ein Weltbild ausliefern wollte, in dem der Anbieter
    #: seine Marge hält, musste die ausgelieferte Konfiguration ändern — also
    #: das Modell statt des Experiments (Regel 7 der Oberfläche, eine Ebene
    #: tiefer).
    #:
    #: `None` heißt «wie ausgeliefert» und ist der Standard: Ein Szenario, das
    #: nichts sagt, ändert nichts. Ein unbekannter Name scheitert laut — beim
    #: Laden der Datei, über `MarketFeedbackConfig`.
    preisstrategie: str | None = None
    base_price: float | None = None  # P2.3: override price_model.base_price
    property_overrides: list[PropertyOverride] = Field(default_factory=list)
    factor_overrides: list[FactorOverride] = Field(default_factory=list)
    milestones: list[MilestoneCheck] = Field(default_factory=list)


class SweepResult(BaseModel):
    """Result of a single sweep execution."""

    sweep_id: str
    sweep_name: str
    ticks_completed: int
    final_factor_states: dict[str, str]  # F1 -> F1.2 etc
    final_properties: dict[str, float]  # property_id -> value
    consistency_score: float = 0.0
    stability_index: float = 0.0
    conflicts: list[str] = Field(default_factory=list)
    milestone_results: list[dict[str, Any]] = Field(default_factory=list)


class SweepSummary(BaseModel):
    """Aggregated results of all sweeps."""

    total_sweeps: int = 0
    results: list[SweepResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
