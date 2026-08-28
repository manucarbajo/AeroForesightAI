"""Der Zustand der Anlage — an genau einer Stelle abgeleitet.

Die Kopfzeile zeigt ihn als Punkt, das Log-Panel als Überschrift, der Viewport
als Banner. Drei Darstellungen derselben Aussage; sie dürfen sich nicht
widersprechen. Deshalb steht die Ableitung hier und nicht dreimal verteilt —
dasselbe Muster wie `agent_permissions.may_propose_factor` in P0.5.

Vier Zustände, in dieser Rangfolge:

* ``running``  — es rechnet gerade ein Lauf. Schlägt alles andere, weil es das
  einzige ist, was sich von selbst ändert.
* ``demo``     — es gibt keinen einzigen Lauf, gezeigt wird der Demo-Datensatz.
  Muss sichtbar bleiben, solange er sichtbar ist.
* ``degraded`` — der gewählte Lauf ist unter Ausfall eines Sprachmodells
  entstanden (P0.1).
* ``ready``    — nichts davon.
"""

from __future__ import annotations

from dataclasses import dataclass

RUNNING = "running"
DEMO = "demo"
DEGRADED = "degraded"
READY = "ready"


@dataclass(frozen=True)
class Status:
    """Was die Oberfläche über den aktuellen Zustand sagt."""

    tone: str
    label: str
    detail: str

    @property
    def is_demo(self) -> bool:
        return self.tone == DEMO

    @property
    def is_running(self) -> bool:
        return self.tone == RUNNING


def derive(*, running: bool, demo: bool, degraded: bool, incidents: int = 0) -> Status:
    """Aus den drei Tatsachen den einen Zustand machen.

    Bewusst ohne Zugriff auf `runner` oder `run_browser`: Die Funktion nimmt
    Wahrheitswerte entgegen und ist damit ohne laufendes System prüfbar. Wer
    sie ruft, weiß, woher seine Wahrheitswerte kommen.
    """

    if running:
        return Status(
            RUNNING,
            "Simulation läuft",
            "Ein Lauf rechnet im Hintergrund. Der Fortschritt steht in der Konsole.",
        )
    if demo:
        return Status(
            DEMO,
            "Demo-Daten",
            "Es liegt noch kein gerechneter Lauf vor. Alle Zahlen auf dieser Seite "
            "stammen aus einem Beispieldatensatz und sind keine Simulationsergebnisse.",
        )
    if degraded:
        calls = "ein Aufruf" if incidents == 1 else f"{incidents} Aufrufe"
        return Status(
            DEGRADED,
            "Lauf beeinträchtigt",
            f"{calls} an das Sprachmodell blieben unbeantwortet. Die gerechneten "
            "Zahlen sind davon unberührt.",
        )
    return Status(READY, "System bereit", "Kein Lauf aktiv.")
