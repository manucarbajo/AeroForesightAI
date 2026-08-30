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
    """Wo die CO₂-Abgabe gesprungen ist — **oder nirgends** (P1.2).

    Bis zum 2026-08-30 gab diese Funktion `(15, 30)` zurück, wenn sie nichts
    fand. Die Figur zeichnete daraufhin senkrechte Markierungen bei Tick 15 und
    30 in einen Lauf, in dem **kein** Politik-Schock stattgefunden hatte — bei
    einem Lauf über fünf Ticks sogar weit hinter dessen Ende. Ein Bild, das
    Ereignisse markiert, die es nicht gab, ist schlimmer als eines ohne
    Markierungen.

    Ein leeres Ergebnis heißt jetzt, was es heißt: kein Sprung.
    """

    shocks: list[int] = []
    previous: float | None = None
    for tick, value in zip(series.ticks, series.carbon_tax, strict=False):
        if previous is not None and value == value and value != previous:
            shocks.append(int(tick))
        previous = value
    return tuple(shocks)


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

    # **Die Titel nennen die Aussage, zu der ein Bild gehört** (P1.2). Der Satz
    # folgt derselben Wirkungskette wie die Ansichten im Dashboard; wer ein PNG
    # in einen Bericht zieht, soll nicht raten müssen, welche Frage es
    # beantwortet.
    #
    # **Fünf Dateien für vier Aussagen, und das ist Absicht:** «Wer noch fliegt»
    # braucht zwei Bilder — wie sich die Buchungsrate je Altersgruppe entwickelt,
    # und wie die Bevölkerung überhaupt zusammengesetzt ist. Eine Zahl zu
    # erzwingen wäre eine schönere Aufzählung und eine schlechtere Auskunft.
    #
    # **«Systemdynamik» ist aus dem Lauf-Satz herausgefallen** — sie zeigt das
    # Zusammenspiel der Systemgrößen, also Eingänge, nicht das Ergebnis. Als
    # laufübergreifende Auswertung bleibt sie in `global_figures`.
    figure_paths: dict[str, Path] = {
        "1 · Preis und Nachfrage": plot_price_vs_booking(
            series, figures_dir / "preis_und_nachfrage.png"
        ),
        "2 · Was die Politik bewirkt": plot_policy_shock(
            series, figures_dir / "politik_und_wirkung.png", shock_ticks=shock_ticks
        ),
        "3 · Wer noch fliegt": plot_age_segments(series, figures_dir / "wer_noch_fliegt.png"),
        "3 · Wer noch fliegt — die Bevölkerung": plot_population_distribution(
            run_path, figures_dir / "bevoelkerung.png"
        ),
        "4 · Die Faktorlage des Laufs": plot_factor_states(series, figures_dir / "faktorlage.png"),
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
