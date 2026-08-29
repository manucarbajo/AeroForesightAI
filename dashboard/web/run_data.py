"""Die Daten eines Laufs, wie der Leitstand sie braucht — aus einer Hand.

Szene, Telemetrie und Zeitleiste zeigen denselben Lauf aus drei Blickwinkeln.
Ohne eine gemeinsame Ladestelle würde jede von ihnen dieselben Dateien einzeln
öffnen und dabei ihre eigene Vorstellung davon entwickeln, was ein fehlendes
`tick_mechanics.json` bedeutet. Hier liegt die eine Antwort.

Der Demo-Fall ist hier ebenfalls zu Hause, und zwar als **Auswahl der Quelle**,
nicht als Sonderweg der Ansichten: `load()` liefert entweder die Dateien eines
echten Laufs oder den Beispieldatensatz aus `demo_run` — in beiden Fällen
dieselben Formen. Ob es der Beispieldatensatz war, sagt `RunData.is_demo`, und
die Oberfläche macht es sichtbar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from dashboard.run_browser import (
    load_event_log,
    load_price_series,
    load_tick_mechanics,
)
from dashboard.web import demo_run


@dataclass
class RunData:
    """Alles, was die drei Zonen des Leitstands aus einem Lauf lesen."""

    run_id: str
    run_dir: Path | None
    ticks: list[dict[str, Any]] = field(default_factory=list)
    prices: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    factors: dict[int, dict[str, str]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_demo: bool = False

    @property
    def max_tick(self) -> int:
        """Der letzte Tick, für den es Daten gibt.

        Nicht `ticks_max` aus den Metadaten: Ein abgebrochener Lauf verspricht
        dort mehr, als er geliefert hat, und die Zeitleiste würde ins Leere
        scrubben.
        """

        candidates = [int(row.get("tick") or 0) for row in self.ticks]
        candidates += [int(row.get("round_number") or 0) for row in self.prices]
        return max(candidates) if candidates else 0

    @property
    def has_series(self) -> bool:
        return bool(self.ticks or self.prices)

    def tick_row(self, tick: int) -> dict[str, Any]:
        """Die Zeile eines Ticks — leer, wenn es sie nicht gibt."""

        for row in self.ticks:
            if int(row.get("tick") or 0) == tick:
                return row
        return {}

    def events_at(self, tick: int) -> list[dict[str, Any]]:
        return [event for event in self.events if int(event.get("round_number") or 0) == tick]

    def factors_at(self, tick: int) -> dict[str, str]:
        """Die Faktorlage eines Ticks — sonst die des letzten bekannten davor.

        Faktoren wechseln selten; eine Lücke in der Zeitreihe heißt «unverändert»
        und nicht «keine Angabe». Vorwärts zu suchen wäre dagegen falsch: Es
        stünde ein Zustand da, den es zu diesem Zeitpunkt noch nicht gab.
        """

        if not self.factors:
            return {}
        known = sorted(t for t in self.factors if t <= tick)
        if known:
            return self.factors[known[-1]]
        return self.factors[min(self.factors)]


def _load_factor_series(run_dir: Path) -> dict[int, dict[str, str]]:
    """`timeseries/factors.csv` als Zuordnung Tick → Faktorzustände."""

    path = run_dir / "timeseries" / "factors.csv"
    if not path.is_file():
        return {}
    try:
        import pandas as pd

        frame = pd.read_csv(path)
    except Exception:  # noqa: BLE001 - eine defekte Zeitreihe darf die Seite nicht killen
        return {}
    if frame.empty or "tick" not in frame.columns:
        return {}

    spalten = [c for c in frame.columns if c != "tick"]
    return {
        int(row["tick"]): {column: str(row[column]) for column in spalten}
        for _, row in frame.iterrows()
    }


def _load_metadata(run_dir: Path) -> dict[str, Any]:
    import json

    path = run_dir / "run_metadata.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def demo() -> RunData:
    """Der Beispieldatensatz in derselben Form wie ein echter Lauf."""

    return RunData(
        run_id=demo_run.RUN_ID,
        run_dir=None,
        ticks=demo_run.tick_mechanics(),
        prices=demo_run.price_series(),
        events=demo_run.event_log(),
        factors={
            row["tick"]: demo_run.factor_states(row["tick"]) for row in demo_run.tick_mechanics()
        },
        metadata=demo_run.metadata(),
        is_demo=True,
    )


def load(selected: dict | None) -> RunData:
    """Die Daten des gewählten Laufs — oder den Beispieldatensatz.

    *selected* ist der Inhalt von `selected-run-store`: `{"run_id", "run_dir"}`
    oder `None`. Fehlt er oder zeigt er auf ein Verzeichnis, das es nicht mehr
    gibt, greift der Demo-Fall — dann steht überall dasselbe Abzeichen, statt
    dass eine Ansicht leer bleibt und die nächste eine Fehlermeldung zeigt.
    """

    if not selected or not selected.get("run_dir"):
        return demo()

    run_dir = Path(selected["run_dir"])
    if not run_dir.is_dir():
        return demo()

    return RunData(
        run_id=str(selected.get("run_id") or run_dir.name),
        run_dir=run_dir,
        ticks=load_tick_mechanics(run_dir),
        prices=load_price_series(run_dir),
        events=load_event_log(run_dir),
        factors=_load_factor_series(run_dir),
        metadata=_load_metadata(run_dir),
        is_demo=False,
    )


#: Wie viele Läufe ihre Individuen-History gleichzeitig im Speicher behalten.
#: Drei, weil das Vergleichen zweier Läufe der übliche Fall ist und der dritte
#: den Wechsel dazwischen abfedert. Mehr wäre Speicher ohne erkennbaren Nutzen.
_POPULATION_CACHE_SIZE = 3


@lru_cache(maxsize=_POPULATION_CACHE_SIZE)
def _load_population(run_dir: str, _fingerprint: tuple[int, int]):
    """Die History eines Laufs, einmal gelesen.

    Der Schlüssel trägt Größe und Änderungszeit der Datei mit: Wird sie neu
    geschrieben, entsteht ein neuer Eintrag, und der alte fällt heraus. Ohne das
    zeigte die Szene nach einem Lauf gleichen Namens weiter die alten Punkte.
    """

    from dashboard.web.views.animation import load_history

    return load_history(Path(run_dir))


def population(data: RunData):
    """Die Individuen-History als DataFrame — oder `None`, wenn es keine gibt.

    Bewusst nicht Teil von `RunData`: Die Datei ist die mit Abstand größte eines
    Laufs, und nur die Szene braucht sie.

    **Und sie wird gecacht.** Die Szene wird bei *jedem* Schritt der Zeitleiste
    neu gebaut; die Datei je Tick erneut zu parsen macht das Abspielen auf einem
    längeren Lauf unbenutzbar. Der Cache hängt an Pfad, Größe und Änderungszeit —
    ein neu geschriebener Lauf gleichen Namens bekommt dadurch einen eigenen
    Eintrag.
    """

    if data.is_demo:
        return demo_run.population_frame()
    if data.run_dir is None:
        return None

    path = data.run_dir / "individuals_history.csv"
    if not path.is_file():
        return None
    try:
        stat = path.stat()
        return _load_population(str(data.run_dir), (stat.st_size, stat.st_mtime_ns))
    except Exception:  # noqa: BLE001 - defekte History soll die Szene nicht sprengen
        return None
