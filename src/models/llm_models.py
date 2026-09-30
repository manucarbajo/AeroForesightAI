"""Record of moments a run did not get the LLM answer it asked for.

Ein Lauf, dessen Sprachmodell ausgefallen ist, liefert weiterhin Artefakte —
er soll sie nur nicht als vollwertig ausgeben. Diese Modelle sind der
schriftliche Beleg dafür: sie wandern über `SimulationState` in den Checkpoint,
nach `llm_incidents.json` und als Zusammenfassung in `run_metadata.json`.

Bewusst **nicht** im `event_log`: dort stehen Fachereignisse der Simulation,
die von Figures, Protokoll und State Explorer gezählt werden. Ein technischer
Ausfall dort würde die Ereigniszahl eines Laufs verfälschen.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

#: Was genau schiefging. `call_failed` ist der Aufruf selbst; `no_op_emitted`
#: sagt zusätzlich, dass der Agent daraufhin einen Leerzug eingesetzt hat.
#: `answer_unusable` (seit P8-V5): Das Modell hat geantwortet, aber die Antwort
#: ließ sich nicht verwenden, und an ihre Stelle trat die Vorlage. Am 2026-09-30
#: geschah das bei drei von sechs Läufen des Vorführbestands, **ohne** Vorfall —
#: der Lauf sah vollwertig aus.
LLMIncidentKind = Literal["call_failed", "no_op_emitted", "answer_unusable"]


class LLMIncident(BaseModel):
    """Ein einzelner nicht beantworteter LLM-Aufruf."""

    tick: int = Field(description="Tick, in dem der Aufruf scheiterte")
    caller: str = Field(description="Wer gefragt hat, z. B. 'agent:consumer' oder 'scenario_node'")
    kind: LLMIncidentKind = Field(description="Art des Vorfalls")
    error: str = Field(description="Fehlertext des gescheiterten Aufrufs")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class LLMDegradation(BaseModel):
    """Zusammenfassung aller Vorfälle eines Laufs, wie sie in die Metadaten geht."""

    degraded: bool = False
    incident_count: int = 0
    degraded_ticks: list[int] = Field(default_factory=list)

    @classmethod
    def from_incidents(cls, incidents: list[LLMIncident]) -> "LLMDegradation":
        ticks = sorted({incident.tick for incident in incidents})
        return cls(
            degraded=bool(incidents),
            incident_count=len(incidents),
            degraded_ticks=ticks,
        )
