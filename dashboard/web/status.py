"""Der Zustand der Anlage — an genau einer Stelle abgeleitet, für die Kopfzeile.

Drei Zustände, in dieser Rangfolge:

* ``running`` — es rechnet gerade ein Lauf. Schlägt alles andere, weil es das
  einzige ist, was sich von selbst ändert.
* ``demo``    — es gibt keinen einzigen Lauf, gezeigt wird der Demo-Datensatz.
  Muss sichtbar bleiben, solange er sichtbar ist (Invariante 1).
* ``ready``   — nichts davon.

**«Beeinträchtigt» ist seit P7.3-U3.2 kein Zustand der Anlage mehr.** Er gehört
dem gewählten Lauf und steht in dessen Kopf (`pages.runs.lauf_kopf`), im Leitstand
und unter «Ergebnisse». Bis dahin stand «Lauf beeinträchtigt» als Anlagenzustand
auf jedem Bereich, auch in «Einrichten», «Modell» und «Handbuch» (K2). Dieser
Docstring nannte außerdem Log-Panel und Banner als weitere Darstellungen; im Code
leitete nur die Kopfzeile ab. `DEGRADED` bleibt als Ton des Bausteins
`status_indicator` — die Musterseite zeigt ihn.
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


def derive(*, running: bool, demo: bool) -> Status:
    """Aus den zwei Tatsachen den einen Zustand machen.

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
    return Status(READY, "System bereit", "Kein Lauf aktiv.")
