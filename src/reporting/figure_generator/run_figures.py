"""Per-run figure generation: outputs/<run_id>/figures/ + manifest.json.

**Ein Figurensatz entsteht ganz oder gar nicht** (P1.2). Bis 2026-08-30 wurden
die PNGs direkt an ihren Platz geschrieben und das Manifest danach. Brach ein
Plot ab, lagen die vorher fertigen Bilder da — und ein **altes** Manifest aus
einem früheren Lauf blieb daneben liegen und passte nicht mehr dazu. Die
Ergebnisansicht zeigte einen Satz aus neuen und alten Bildern, ohne dass
irgendwo stand, dass er keiner ist.

Gebaut wird deshalb in einer Werkstatt neben dem Ziel, und erst der fertige Satz
zieht um. Was dabei liegen bleibt, ist **sichtbar** — ein Verzeichnis mit einem
Namen, der nichts anderes bedeuten kann — statt sich als vollständiger Satz
auszugeben.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from src.reporting.figure_generator.plots import (
    _ensure_dir,
    plot_age_segments,
    plot_factor_states,
    plot_policy_shock,
    plot_population_distribution,
    plot_price_vs_booking,
    plot_system_dynamics,
)
from src.reporting.figure_generator.series import RunSeries, extract_series_from_run_dir

#: Wo der Satz entsteht, bevor er an seinen Platz zieht. Der Name ist bewusst
#: sprechend: Wer ihn nach einem Abbruch im Lauf-Verzeichnis findet, weiß, was
#: passiert ist.
WERKSTATT = "figures.neu"

#: Wohin der alte Satz für die Dauer des Umzugs ausweicht. **Zwei Schritte statt
#: eines**, weil `os.replace` auf ein nicht leeres Verzeichnis unter Windows
#: scheitert — und weil so zu keinem Zeitpunkt beide Sätze weg sind: Stirbt der
#: Prozess mittendrin, liegt der alte hier und der neue in der Werkstatt.
AUSWEICHE = "figures.alt"


@dataclass(frozen=True)
class RunFigureGenerationResult:
    figure_paths: dict[str, Path]
    run_dir: Path


def _detect_policy_shock_ticks(series: RunSeries) -> tuple[int, ...]:
    shocks: list[int] = []
    previous: float | None = None
    for tick, value in zip(series.ticks, series.carbon_tax, strict=False):
        if previous is not None and value == value and value != previous:
            shocks.append(int(tick))
        previous = value
    return tuple(shocks) if shocks else (15, 30)


def generate_run_figures(run_dir: Path | str) -> RunFigureGenerationResult:
    """Generate per-run PNG figures under ``outputs/<run_id>/figures/``."""

    run_path = Path(run_dir)
    if not run_path.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_path}")

    series = extract_series_from_run_dir(run_path)
    shock_ticks = _detect_policy_shock_ticks(series)

    # Reste eines abgebrochenen Laufs zuerst wegräumen — sonst scheitert der
    # Umzug unten an einem Verzeichnis, das es schon gibt.
    ziel = run_path / "figures"
    werkstatt = run_path / WERKSTATT
    ausweiche = run_path / AUSWEICHE
    shutil.rmtree(werkstatt, ignore_errors=True)
    shutil.rmtree(ausweiche, ignore_errors=True)
    figures_dir = _ensure_dir(werkstatt)

    figure_paths: dict[str, Path] = {
        "Preis vs. Booking": plot_price_vs_booking(series, figures_dir / "price_vs_booking.png"),
        "CO₂-Policy-Shock": plot_policy_shock(
            series, figures_dir / "policy_shock_co2_booking.png", shock_ticks=shock_ticks
        ),
        "Systemdynamik": plot_system_dynamics(series, figures_dir / "system_dynamics.png"),
        "Faktor-Zustände": plot_factor_states(series, figures_dir / "factor_states.png"),
        "Alterssegmente": plot_age_segments(series, figures_dir / "age_segment_booking.png"),
        "Populationsverteilung": plot_population_distribution(
            run_path, figures_dir / "population_distribution.png"
        ),
    }

    manifest = {
        "run_id": run_path.name,
        "figures": {title: path.name for title, path in figure_paths.items()},
    }
    (figures_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # **Jetzt erst der Umzug.** Bis hierher ist nichts am Platz des alten Satzes
    # verändert worden; jeder Abbruch oberhalb dieser Zeile lässt ihn unberührt.
    if ziel.exists():
        ziel.rename(ausweiche)
    werkstatt.rename(ziel)
    shutil.rmtree(ausweiche, ignore_errors=True)

    figure_paths = {titel: ziel / pfad.name for titel, pfad in figure_paths.items()}
    return RunFigureGenerationResult(figure_paths=figure_paths, run_dir=run_path)
