"""Read-only access to run artifacts under outputs/: listing, loading, regenerating."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.llm import MockLLM, OllamaClient, OllamaConfig
from src.llm.defaults import DEFAULT_BASE_URL, DEFAULT_MODEL
from src.reporting.output_writer import OUTPUT_DIR, resolve_run_output_dir


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    run_dir: Path
    ticks_completed: int | None
    ticks_max: int | None
    total_events: int | None
    model: str | None
    timestamp: str | None
    has_narrative: bool
    has_tick_mechanics: bool
    has_run_scenario: bool
    scenario_title: str | None
    scenario_summary: str | None
    #: True, wenn waehrend des Laufs mindestens ein LLM-Aufruf ins Leere ging.
    #: Aeltere Laeufe kennen das Feld nicht — dort bleibt es False.
    degraded: bool = False
    llm_incident_count: int = 0
    #: Der Name aus `run_metadata.json`, **unverändert** — ob es ein vergebener oder
    #: der Vorgabename ist, entscheidet die Oberfläche (D6, P7.3-U3.3).
    simulation_name: str | None = None
    #: Unter welchem Rahmenszenario der Lauf stand (`rahmen.name`, seit P2.0-B).
    rahmen_name: str | None = None
    #: Womit gerechnet wurde (`compute_mode`, seit P0.6) — für den Lauf-Kopf (P7.3-U3.2).
    compute_mode: str | None = None
    #: Welches Rahmenszenario (`rahmen.id`) und woher es kam (`rahmen.quelle`:
    #: `preset`, `eigen`, `standard`) — für die Art im Lauf-Browser (P7.3-U3.3).
    rahmen_id: str | None = None
    rahmen_quelle: str | None = None
    #: Was an einem abgeleiteten Lauf vom Szenario abweicht (`rahmen.abweichungen`,
    #: seit P7.13-U13.2) — damit Auswahl und Kopf ihn von einem unveränderten
    #: unterscheiden (P8-V6).
    rahmen_abweichungen: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunFileEntry:
    relative_path: str
    absolute_path: Path
    size_bytes: int
    kind: str


#: Der Titel stand im Manifest — der Satz ist der, den die Erzeugung gemeint hat.
MANIFEST = "manifest"

#: Kein Manifest: Der Titel ist aus dem Dateinamen geraten, und ob der Satz
#: vollständig ist, weiß niemand.
GERATEN = "geraten"


@dataclass(frozen=True)
class RunFigureEntry:
    """Eine Bilddatei eines Laufs — **und woher wir wissen, wie sie heißt** (P1.2).

    `herkunft` unterscheidet zwei Fälle, die vorher gleich aussahen: Steht der
    Titel im Manifest, ist der Satz der, den die Erzeugung gemeint hat. Ist kein
    Manifest da, wird der Titel aus dem Dateinamen geraten — und dann weiß
    niemand, ob der Satz vollständig ist. Beides als dieselbe Liste
    auszuliefern hieß, eine Vermutung als Auskunft auszugeben.
    """

    title: str
    relative_path: str
    absolute_path: Path
    #: `"manifest"` oder `"geraten"`.
    herkunft: str = MANIFEST


@dataclass(frozen=True)
class RunFigureSet:
    """Was `list_run_figures` wirklich weiß: die Bilder **und** ihr Zustand.

    Die Funktion gab bisher nur eine Liste zurück. Zwei Befunde passten da nicht
    hinein: dass der Satz geraten ist, und dass das Manifest Dateien nennt, die
    es nicht gibt — die wurden stillschweigend übersprungen, und der Satz kam um
    zwei Bilder kürzer zurück, ohne dass jemand davon erfuhr.
    """

    entries: list[RunFigureEntry]
    herkunft: str = MANIFEST
    #: Im Manifest genannt, aber nicht auf der Platte.
    fehlend: tuple[str, ...] = ()

    def __bool__(self) -> bool:  # damit `if figures:` weiterhin trägt
        return bool(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    @property
    def vollstaendig(self) -> bool:
        """Ob man diesem Satz ansehen kann, dass er einer ist."""

        return self.herkunft == MANIFEST and not self.fehlend


def outputs_root(path: Path | str | None = None) -> Path:
    return Path(path or OUTPUT_DIR)


def _load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_run_scenario_preview(run_dir: Path) -> tuple[bool, str | None, str | None]:
    scenario_path = run_dir / "run_scenario.json"
    if not scenario_path.is_file():
        return False, None, None
    payload = _load_json(scenario_path)
    if not isinstance(payload, dict):
        return True, None, None
    title = payload.get("title")
    summary = payload.get("summary")
    scenarios = payload.get("scenarios")
    if isinstance(scenarios, list) and scenarios:
        first = scenarios[0] if isinstance(scenarios[0], dict) else {}
        preview_title = first.get("title")
        archetypes = ", ".join(
            str(item.get("archetype"))
            for item in scenarios[:3]
            if isinstance(item, dict) and item.get("archetype")
        )
        if summary and archetypes:
            preview_summary = f"{summary} · Top-3: {archetypes}"
        elif archetypes:
            preview_summary = f"Top-3: {archetypes}"
        else:
            preview_summary = summary
        return (
            True,
            str(preview_title or title) if (preview_title or title) else None,
            str(preview_summary) if preview_summary else None,
        )
    return (
        True,
        str(title) if title else None,
        str(summary) if summary else None,
    )


def load_run_scenario(run_dir: Path | str) -> dict[str, Any] | None:
    payload = _load_json(Path(run_dir) / "run_scenario.json")
    return payload if isinstance(payload, dict) else None


def regenerate_run_scenario(
    run_id: str,
    *,
    run_dir: Path | str | None = None,
    mock_llm: bool = True,
    deterministic_only: bool = False,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    from src.reporting.run_scenario_generator import generate_and_save_run_scenario

    directory = Path(run_dir) if run_dir is not None else resolve_run_output_dir(run_id)
    if mock_llm:
        # Wie im Lauf selbst: der Schalter bedeutet «ohne Sprachmodell», nicht
        # «was die Umgebung gerade hergibt» (P0.1).
        llm = MockLLM()
    else:
        llm = OllamaClient(
            OllamaConfig(
                base_url=base_url,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    return generate_and_save_run_scenario(
        run_id,
        llm,
        run_dir=directory,
        prefer_llm=not deterministic_only,
    )


#: Die Zeit in einer Kennung wie `run_20260914T065633Z` — der Rückfall für einen
#: Lauf, dessen Metadaten keinen Zeitstempel tragen.
_KENNUNG_ZEIT = re.compile("([0-9]{8}T[0-9]{6}Z)")


def _zeitpunkt(summary: RunSummary) -> datetime:
    """Wann ein Lauf entstand: der Zeitstempel, sonst die Kennung, sonst ganz früh."""

    if summary.timestamp:
        try:
            zeit = datetime.fromisoformat(summary.timestamp)
        except ValueError:
            pass
        else:
            return zeit if zeit.tzinfo else zeit.replace(tzinfo=UTC)
    treffer = _KENNUNG_ZEIT.search(summary.run_id)
    if treffer:
        return datetime.strptime(treffer.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    return datetime.min.replace(tzinfo=UTC)


def list_runs(root: Path | str | None = None) -> list[RunSummary]:
    base = outputs_root(root)
    if not base.is_dir():
        return []

    summaries: list[RunSummary] = []

    def _append_run(run_dir: Path, run_id: str) -> None:
        metadata = _load_json(run_dir / "run_metadata.json")
        meta_dict = metadata if isinstance(metadata, dict) else {}
        has_scenario, scenario_title, scenario_summary = _read_run_scenario_preview(run_dir)

        sim_name = meta_dict.get("simulation_name")
        sim_desc = meta_dict.get("simulation_description")

        # Manuelle Namen aus der UI überschreiben automatisch generierte Szenario-Titel
        if sim_name:
            scenario_title = sim_name
        if sim_desc:
            scenario_summary = sim_desc

        summaries.append(
            RunSummary(
                run_id=run_id,
                run_dir=run_dir,
                ticks_completed=meta_dict.get("ticks_completed"),
                ticks_max=meta_dict.get("ticks_max"),
                total_events=meta_dict.get("total_events"),
                model=meta_dict.get("model"),
                timestamp=meta_dict.get("timestamp"),
                has_narrative=(run_dir / "final_narrative.md").is_file(),
                has_tick_mechanics=(run_dir / "tick_mechanics.json").is_file(),
                has_run_scenario=has_scenario,
                scenario_title=scenario_title,
                scenario_summary=scenario_summary,
                degraded=bool(meta_dict.get("degraded", False)),
                llm_incident_count=int(meta_dict.get("llm_incident_count") or 0),
                simulation_name=sim_name or None,
                rahmen_name=str((meta_dict.get("rahmen") or {}).get("name") or "") or None,
                compute_mode=meta_dict.get("compute_mode"),
                rahmen_id=str((meta_dict.get("rahmen") or {}).get("id") or "") or None,
                rahmen_quelle=str((meta_dict.get("rahmen") or {}).get("quelle") or "") or None,
                rahmen_abweichungen=tuple(
                    str(a) for a in (meta_dict.get("rahmen") or {}).get("abweichungen") or []
                ),
            )
        )

    for entry in sorted(base.iterdir(), reverse=True):
        if not entry.is_dir():
            continue
        if entry.name.startswith("run_"):
            # **Nur ein Ordner mit Laufdaten ist ein Lauf** (P7.3-U3.3), wie in den
            # beiden Zweigen darunter. Die CLI legt Laufverzeichnis und `checkpoints/`
            # an, bevor sie die Konfiguration prüft; am 2026-09-14 waren 452 der 646
            # Einträge solche leeren Ordner.
            if (entry / "run_metadata.json").is_file():
                _append_run(entry, entry.name)
            continue
        if entry.name.startswith("batch_"):
            child_dirs = sorted(
                (
                    child
                    for child in entry.iterdir()
                    if child.is_dir() and child.name.startswith("run_")
                ),
                reverse=True,
            )
            for child_dir in child_dirs:
                if (child_dir / "run_metadata.json").is_file():
                    _append_run(child_dir, f"{entry.name}/{child_dir.name}")
            continue
        if entry.name == "sweeps":
            for sweep_dir in sorted(
                (
                    child
                    for child in entry.iterdir()
                    if child.is_dir() and child.name.startswith("sweep_")
                ),
                reverse=True,
            ):
                if (sweep_dir / "run_metadata.json").is_file():
                    _append_run(sweep_dir, f"sweeps/{sweep_dir.name}")

    # **Der jüngste zuerst, über alle drei Zweige** (P7.3-U3.3). Bis dahin kam
    # die Reihenfolge aus `sorted(base.iterdir(), reverse=True)` — alphabetisch,
    # und weil `sweeps` vor `run_*` verarbeitet wurde, stand ein Sweep vorn:
    # Vorausgewählt war `sweeps/sweep_transformation_conflict` vom 2026-09-07,
    # während der jüngste Lauf vom 2026-09-14 stammte.
    summaries.sort(key=_zeitpunkt, reverse=True)
    return summaries


def list_run_figures(run_dir: Path | str) -> RunFigureSet:
    """Die Bilder eines Laufs — und ob man ihnen trauen kann (P1.2).

    **Der Rückfall auf `glob` bleibt, aber er sagt jetzt, dass er einer ist.**
    Läufe von vor dem 2026-08-30 haben Figures ohne Manifest; sie wegzulassen
    hieße, ältere Ergebnisse zu verlieren. Sie aber wie einen benannten Satz
    auszuliefern hieß, eine Vermutung als Auskunft auszugeben — die Titel sind
    aus Dateinamen geraten, und ob der Satz vollständig ist, weiß niemand.
    """

    base = Path(run_dir) / "figures"
    if not base.is_dir():
        return RunFigureSet(entries=[])

    manifest_path = base / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
        title_map = manifest.get("figures") or {}
        entries: list[RunFigureEntry] = []
        fehlend: list[str] = []
        for title, filename in title_map.items():
            path = base / filename
            if path.is_file():
                entries.append(
                    RunFigureEntry(
                        title=str(title),
                        relative_path=f"figures/{filename}",
                        absolute_path=path,
                        herkunft=MANIFEST,
                    )
                )
            else:
                # **Nicht verschlucken.** Bisher kam der Satz hier still um zwei
                # Bilder kürzer zurück, und niemand erfuhr davon.
                fehlend.append(str(title))
        if entries:
            return RunFigureSet(entries=entries, herkunft=MANIFEST, fehlend=tuple(fehlend))

    entries = [
        RunFigureEntry(
            title=path.stem.replace("_", " ").title(),
            relative_path=f"figures/{path.name}",
            absolute_path=path,
            herkunft=GERATEN,
        )
        for path in sorted(base.glob("*.png"))
    ]
    return RunFigureSet(entries=entries, herkunft=GERATEN if entries else MANIFEST)


def generate_figures_for_run(run_dir: Path | str) -> RunFigureSet:
    from src.reporting.figure_generator import generate_run_figures

    result = generate_run_figures(run_dir)
    return list_run_figures(result.run_dir)


#: Verzeichnisse, die kein Ergebnis sind, sondern ein Rest davon. Sie entstehen,
#: wenn die Figurenerzeugung mittendrin abbricht (siehe `run_figures`), und
#: gehören nicht in die Dateiliste eines Laufs: Wer dort ein `manifest.json`
#: findet, hält es für **das** Manifest.
WERKSTATT_VERZEICHNISSE = {"figures.neu", "figures.alt"}


def list_run_files(run_dir: Path | str) -> list[RunFileEntry]:
    base = Path(run_dir)
    if not base.is_dir():
        return []

    entries: list[RunFileEntry] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if WERKSTATT_VERZEICHNISSE & set(path.relative_to(base).parts):
            continue
        suffix = path.suffix.lower()
        if suffix in {".json", ".md", ".csv", ".txt"}:
            kind = suffix.lstrip(".")
        elif suffix == ".png":
            kind = "png"
        else:
            kind = "other"
        entries.append(
            RunFileEntry(
                relative_path=str(path.relative_to(base)).replace("\\", "/"),
                absolute_path=path,
                size_bytes=path.stat().st_size,
                kind=kind,
            )
        )
    return entries


def read_run_file(path: Path | str, *, max_chars: int = 250_000) -> str:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n… [gekürzt, {len(text) - max_chars} Zeichen ausgeblendet]"
    return text


def load_price_series(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "price_history.json")
    return payload if isinstance(payload, list) else []


def load_tick_mechanics(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "tick_mechanics.json")
    if isinstance(payload, dict):
        ticks = payload.get("ticks")
        return ticks if isinstance(ticks, list) else []
    return []


def load_event_log(run_dir: Path | str) -> list[dict[str, Any]]:
    payload = _load_json(Path(run_dir) / "event_log.json")
    return payload if isinstance(payload, list) else []
