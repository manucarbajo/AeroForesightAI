from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from src.models.llm_models import LLMIncident
from src.models.population_models import Individual
from src.models.property_models import PropertiesConfig


class FactorState(BaseModel):
    id: str
    name: str
    description: str
    current_state: str
    possible_states: dict[str, str]


class EnvironmentState(BaseModel):
    factors: dict[str, FactorState]
    global_context: str = ""


class SpeechCandidateState(BaseModel):
    """Serialized speech candidate emitted by the RedebedarfScheduler."""

    agent_id: str
    score: int
    reasons: list[str] = Field(default_factory=list)
    contributions_this_round: int = 0


class SpeechPlanState(BaseModel):
    """Round-level speech plan generated before agent execution."""

    round_number: int
    order: list[str] = Field(default_factory=list)
    candidates: list[SpeechCandidateState] = Field(default_factory=list)
    scores: dict[str, int] = Field(default_factory=dict)


class SimulationClock(BaseModel):
    """Discrete simulation clock. One tick is one tick.  No calendar mapping."""

    current_tick: int = 0
    max_ticks: int = 40
    tick_unit: str = "tick"

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_fields(cls, data: Any) -> Any:
        """Accept legacy ``current_round`` / ``max_rounds`` keys from older checkpoints."""

        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "current_tick" not in normalized and "current_round" in normalized:
            normalized["current_tick"] = normalized["current_round"]
        if "max_ticks" not in normalized and "max_rounds" in normalized:
            normalized["max_ticks"] = normalized["max_rounds"]
        return normalized

    def tick_label(self, tick: int) -> str:
        """Return the display label for a 1-based tick index."""

        if tick < 1:
            raise ValueError("tick must be >= 1")
        return f"Tick {tick}"


class LLMConfig(BaseModel):
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048


#: Der Seed, mit dem gerechnet wird, wenn die Konfiguration keinen nennt.
#:
#: Der Wert stand bis dahin als Literal in `environment_node`, und nur dort:
#: Ein Lauf ohne konfigurierten Seed zog seine Bevölkerung reproduzierbar mit
#: 42, während `run_metadata.json` `null` schrieb und die Oberfläche den Lauf
#: "frei" nannte. Beides war falsch — der Lauf war reproduzierbar, sagte es nur
#: niemandem. Aufgelöst wird der Seed jetzt einmal in
#: `SimulationRunner.run`; diese Konstante ist seine einzige Quelle.
DEFAULT_SEED = 42


class SimulationConfig(BaseModel):
    name: str
    description: str
    llm: LLMConfig = LLMConfig()
    seed: int | None = None


class ConfigFingerprint(BaseModel):
    """Je ein Kurzhash über die Eingaben, aus denen ein Lauf entstanden ist.

    Wird **beim Start** eines Laufs genommen, nicht am Ende. Der Unterschied
    ist nicht kosmetisch: `factors` enthält den Zustand jedes Deskriptors, und
    den verschiebt der Lauf selbst. Am Ende gehasht trugen zwei Läufe derselben
    Konfiguration mit verschiedenen Seeds verschiedene Fingerabdrücke — womit
    der Abdruck genau die Frage nicht mehr beantwortete, für die er da ist.
    Weglassen ließ sich der Zustand nicht: Der **Start**zustand ist eine
    Eingabe, jeder Sweep setzt ihn über `FactorOverride.initial_state`.
    """

    simulation_config: str
    properties: str
    factors: str
    agent_profiles: str
    cib_matrix: str | None = None


class SimulationState(BaseModel):
    config: SimulationConfig
    properties: PropertiesConfig
    clock: SimulationClock
    environment: EnvironmentState
    agents: list[AgentConfig]
    #: Fingerabdruck der Eingaben, gesetzt von `SimulationRunner.run` vor dem
    #: ersten Tick. Bleibt danach unverändert — auch beim Fortsetzen aus einem
    #: Checkpoint, der Lauf setzt ja dieselbe Konfiguration fort.
    config_fingerprint: ConfigFingerprint | None = None
    #: Wie lange der Lauf gerechnet hat, in Sekunden — gesetzt von
    #: `SimulationRunner.run`, wenn der letzte Tick durch ist (P1.9-W4.3).
    #:
    #: **Bis dahin hielt kein Artefakt fest, wie lange ein Lauf dauert.** Der
    #: Zeitstempel in `run_metadata.json` sagt, *wann* die Metadaten geschrieben
    #: wurden, nicht *wie lange* gerechnet wurde. Damit ließ sich vor einem Lauf
    #: auch nichts abschätzen: Die Angaben im Handbuch waren geschätzt und als
    #: geschätzt gekennzeichnet.
    #:
    #: Nach demselben Muster wie `config_fingerprint`: am richtigen Moment
    #: genommen, im Zustand abgelegt, von dort gelesen — nicht am Ende noch
    #: einmal berechnet.
    elapsed_seconds: float | None = None
    redebedarf_scores: dict[str, int] = Field(default_factory=dict)
    current_speech_candidates: list[SpeechCandidateState] = Field(default_factory=list)
    current_speech_order: list[str] = Field(default_factory=list)
    current_round_spoken_agents: list[str] = Field(default_factory=list)
    speech_plan: SpeechPlanState | None = None
    event_log: list[EventLogEntry] = Field(default_factory=list)
    price_history: list[PriceHistoryEntry] = Field(default_factory=list)
    round_results: list[RoundResult] = Field(default_factory=list)
    cib_matrix: CIBMatrix | None = None
    cib_history: CIBMatrixHistory | None = None
    market_metrics: dict[str, float] = Field(default_factory=dict)
    property_timeseries: list[dict[str, Any]] = Field(default_factory=list)
    population_individuals: list[Individual] = Field(default_factory=list)
    population_stats: list[dict[str, Any]] = Field(default_factory=list)
    applied_factor_rule_ids: list[str] = Field(default_factory=list)
    factor_timeseries: list[dict[str, Any]] = Field(default_factory=list)
    #: Nicht beantwortete LLM-Aufrufe. Leer bei einem sauberen Lauf; der Default
    #: macht ältere Checkpoints ohne dieses Feld weiterhin ladbar.
    llm_incidents: list[LLMIncident] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _load_properties_for_legacy_checkpoints(cls, data: Any) -> Any:
        """Old checkpoints may omit ``properties`` — load from ``properties.json``."""

        if not isinstance(data, dict):
            return data
        if data.get("properties") is not None:
            return data

        from src.config_loader import load_properties_config

        data = dict(data)
        data["properties"] = load_properties_config().model_dump()
        return data

    def resolved_properties(self) -> PropertiesConfig:
        return self.properties


class InputState(BaseModel):
    """Studio-facing input defaults for AP3 runs."""

    max_rounds: int = Field(default=40, description="Maximale Anzahl an Ticks")
    rounds: int = Field(default=4, description="Alias für max_rounds")
    seed: int | None = Field(default=None, description="Seed für Multi-Run")
    llm_model: str = Field(default="llama3.2", description="LLM-Modellname")
    llm_temperature: float = Field(default=0.7, description="LLM-Temperatur")
    llm_max_tokens: int = Field(default=2048, description="Maximale Token pro Antwort")
    enable_redebedarf: bool = Field(
        default=False,
        description="C3 Redebedarf-Scheduler statt paralleler Agenten pro Tick",
    )
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama-Base-URL")


class PlaygroundState(InputState):
    """Graph state schema tolerant to partial/empty Studio payloads."""

    config: dict[str, Any] | None = Field(default=None)
    clock: dict[str, Any] | None = Field(default=None)
    environment: dict[str, Any] | None = Field(default=None)
    agents: list[dict[str, Any]] | None = Field(default=None)

    event_log: list[dict[str, Any]] = Field(default_factory=list)
    price_history: list[dict[str, Any]] = Field(default_factory=list)
    round_results: list[dict[str, Any]] = Field(default_factory=list)
    cib_matrix: dict[str, Any] | None = Field(default=None)
    cib_history: dict[str, Any] | None = Field(default=None)

    redebedarf_scores: dict[str, int] = Field(default_factory=dict)
    current_speech_candidates: list[SpeechCandidateState] = Field(default_factory=list)
    current_speech_order: list[str] = Field(default_factory=list)
    current_round_spoken_agents: list[str] = Field(default_factory=list)
    speech_plan: SpeechPlanState | None = Field(default=None)
    market_metrics: dict[str, float] = Field(default_factory=dict)


# deferred imports for forward refs
from src.models.agent_models import AgentConfig  # noqa: E402
from src.models.cib_models import CIBMatrix, CIBMatrixHistory  # noqa: E402
from src.models.event_models import EventLogEntry, PriceHistoryEntry, RoundResult  # noqa: E402

SimulationState.model_rebuild()
