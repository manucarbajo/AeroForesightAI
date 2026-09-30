"""Der Vorführbestand: drei vorgerechnete Läufe und sonst nichts in ``outputs/`` (P8-V5).

Aufruf (Ollama muss laufen, das Modell aus ``configs/simulation_config.json`` geladen sein)::

    python -m dashboard.vorfuehrbestand
    python -m dashboard.vorfuehrbestand --archiv F:/Ablage/outputs_archiv
    python -m dashboard.vorfuehrbestand --nur vorfuehrung_bau
    python -m dashboard.vorfuehrbestand --nur-pruefen

**Warum es ihn gibt:** Ein Lauf mit Sprachmodell dauert Minuten — vor Publikum zu
lange —, und der Lauf-Browser listete am 2026-09-29 rund 980 Ordner, darunter
hunderte Mess- und Prüfläufe. Vorgeführt wird deshalb, was vorher gerechnet ist,
und die Liste zeigt nur das.

**Was der Aufruf tut, in dieser Reihenfolge:**

1. **Archivieren.** Alles in ``outputs/`` wandert in einen Unterordner mit
   Zeitstempel im Archiv — **verschoben, nicht gelöscht**, und das Archiv liegt
   **außerhalb** von ``outputs/``, sonst listete der Lauf-Browser es weiter.
   Liegen bleiben ``.gitkeep`` und die Demo-Anfragen der Landingpage: Sie sind
   keine Läufe, sondern Post.
2. **Rechnen**, über denselben Weg wie das Dashboard (`launch_simulation`), damit
   der Bestand genau so aussieht wie ein Lauf aus der Oberfläche: erst der
   Szenario-Vergleich, dann «Business as Usual», zuletzt derselbe Rahmen mit
   steigender CO₂-Abgabe — der Anwendungsfall aus dem Pitch. Der letzte ist der
   jüngste und steht im Lauf-Browser oben.
3. **Prüfen**, gegen den Teil der Abnahme, der sich ohne Browser messen lässt
   (`pruefen`). Ein harter Befund macht den Aufruf rot; Widersprüche des
   Abschlusstexts werden gezählt, nicht verworfen — sie stehen im Lauf markiert.

``--nur-pruefen`` rechnet nichts und verschiebt nichts: Es prüft, was schon da ist.
``--nur KENNUNG`` rechnet einen Lauf neu und verschiebt nur dessen Ordner — für den
Fall, dass einer durchfällt: Die Antworten des Modells streuen, und den ganzen
Bestand deswegen neu zu rechnen kostet zwanzig Minuten.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dashboard.config_catalog import PropertyEditState
from dashboard.run_launcher import RunLaunchConfig, launch_simulation
from src.logging_setup import stdio_auf_utf8
from src.reporting.aussagen_pruefung import ist_englisch
from src.reporting.output_writer.paths import OUTPUT_DIR

REPO = Path(__file__).resolve().parents[1]

#: Wohin der bisherige Inhalt von ``outputs/`` wandert: neben das Repository, nicht
#: hinein — ein Archiv im Repo läge im Weg jeder Suche und jedes Pakets.
ARCHIV = REPO.parent / "AeroForesight_outputs_archiv"

#: Was in ``outputs/`` liegen bleibt. Keine Läufe: die Platzhalterdatei des
#: Repositorys und die Demo-Anfragen, die über die Landingpage eingegangen sind.
BEHALTEN = frozenset({".gitkeep", "demo_anfragen.jsonl"})

#: Die CO₂-Abgabe des Pitch-Falls: «Business as Usual» steht bei 50 €, dieser
#: Lauf springt in Tick 24 auf 200 € — so zeigt es Folie 4 des Pitches.
CO2_ABWEICHUNG = PropertyEditState(
    property_id="carbon_tax_level",
    baseline=50.0,
    rules=[
        {"active_from_tick": 1, "effect": {"type": "set", "value": 50.0}},
        {"active_from_tick": 24, "effect": {"type": "set", "value": 200.0}},
    ],
)


@dataclass(frozen=True)
class Vorfuehrlauf:
    """Ein Lauf des Bestands — was er ist, wie er gerechnet wird, was er liefern muss."""

    kennung: str
    beschreibung: str
    konfiguration: RunLaunchConfig
    #: Der Rechenmodus, den `run_metadata.json` danach nennen muss.
    rechenmodus: str
    #: Die Laufordner relativ zu ``outputs/``, die danach geprüft werden.
    ordner: tuple[str, ...] = field(default_factory=tuple)


def bestand() -> list[Vorfuehrlauf]:
    """Die drei Läufe, in der Reihenfolge, in der sie gerechnet werden."""

    from src.orchestration.scenario_sweeps import rahmenszenarien

    mit_modell = {"mock_llm": False, "deterministic_only": False, "generate_figures": True}
    return [
        Vorfuehrlauf(
            kennung="vergleich",
            beschreibung="Szenario-Vergleich der vier Rahmen, je 120 Ticks, Abschlusstexte vom Modell",
            konfiguration=RunLaunchConfig(run_all_sweeps=True, **mit_modell),
            rechenmodus="deterministic_with_llm_narrative",
            ordner=tuple(f"sweeps/sweep_{rahmen.id}" for rahmen in rahmenszenarien()),
        ),
        Vorfuehrlauf(
            kennung="vorfuehrung_bau",
            beschreibung="«Business as Usual», 40 Ticks, mit Sprachmodell",
            konfiguration=RunLaunchConfig(
                rounds=40,
                scenario_mode="sweep",
                sweep_id="business_as_usual",
                simulation_name="Vorführung: Business as Usual",
                run_id="run_vorfuehrung_bau",
                **mit_modell,
            ),
            rechenmodus="llm",
            ordner=("run_vorfuehrung_bau",),
        ),
        Vorfuehrlauf(
            kennung="vorfuehrung_co2",
            beschreibung="Derselbe Rahmen, CO₂-Abgabe ab Tick 24 bei 200 € — der Fall aus dem Pitch",
            konfiguration=RunLaunchConfig(
                rounds=40,
                scenario_mode="sweep",
                sweep_id="business_as_usual",
                apply_custom_overrides=True,
                abweichungen={"carbon_tax_level": CO2_ABWEICHUNG},
                simulation_name="Vorführung: CO₂-Abgabe steigt auf 200 €",
                run_id="run_vorfuehrung_co2",
                **mit_modell,
            ),
            rechenmodus="llm",
            ordner=("run_vorfuehrung_co2",),
        ),
    ]


def archivieren(ausgabe: Path, archiv: Path, nur: tuple[str, ...] | None = None) -> Path | None:
    """Alles außer `BEHALTEN` aus ``ausgabe`` nach ``archiv/<Zeitstempel>/`` verschieben.

    Gibt den Zielordner zurück, oder ``None``, wenn es nichts zu verschieben gab.
    **Ein Archiv in ``outputs/`` wird abgewiesen**: Der Lauf-Browser läse es weiter,
    und der Zweck wäre verfehlt.

    Mit ``nur`` wandern allein diese Ordner (relativ zu ``ausgabe``) — für einen
    Lauf, der einzeln neu gerechnet wird; der übrige Bestand bleibt stehen.
    """

    ausgabe, archiv = ausgabe.resolve(), archiv.resolve()
    if archiv == ausgabe or ausgabe in archiv.parents:
        raise ValueError(f"Das Archiv darf nicht in {ausgabe} liegen: {archiv}")
    if nur is None:
        eintraege = sorted(p for p in ausgabe.iterdir() if p.name not in BEHALTEN)
    else:
        eintraege = [ausgabe / ordner for ordner in nur if (ausgabe / ordner).exists()]
    if not eintraege:
        return None
    ziel = archiv / datetime.now().strftime("%Y-%m-%dT%H%M%S")
    ziel.mkdir(parents=True, exist_ok=False)
    for eintrag in eintraege:
        platz = ziel / eintrag.relative_to(ausgabe)
        platz.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(eintrag), str(platz))
    return ziel


def pruefen(run_dir: Path, rechenmodus: str) -> tuple[list[str], list[str]]:
    """Der messbare Teil der Abnahme für einen Lauf: (harte Befunde, Hinweise).

    **Hart** ist, was die Vorführung bricht oder den Lauf etwas Falsches über sich
    sagen lässt: fehlende Metadaten, ein anderer Rechenmodus, ein Ausfall des
    Sprachmodells, ein Abschlusstext aus der Vorlage statt vom Modell, englischer
    Text. **Ein Hinweis** sind die markierten Widersprüche des Abschlusstexts —
    sie stehen im Lauf sichtbar unter dem Text (P8-V3), wer vorführt, muss sie
    kennen.
    """

    hart: list[str] = []
    hinweise: list[str] = []

    def lesen(name: str) -> Any:
        pfad = run_dir / name
        return json.loads(pfad.read_text(encoding="utf-8")) if pfad.is_file() else None

    metadaten = lesen("run_metadata.json")
    if not isinstance(metadaten, dict):
        return ["run_metadata.json fehlt"], hinweise
    if metadaten.get("compute_mode") != rechenmodus:
        hart.append(f"Rechenmodus {metadaten.get('compute_mode')!r} statt {rechenmodus!r}")
    if metadaten.get("degraded"):
        hart.append("Das Sprachmodell ist im Lauf ausgefallen (degraded)")
    if metadaten.get("ticks_completed") != metadaten.get("ticks_max"):
        hart.append(
            f"{metadaten.get('ticks_completed')} von {metadaten.get('ticks_max')} Ticks gerechnet"
        )

    szenario = lesen("run_scenario.json")
    if not isinstance(szenario, dict):
        hart.append("run_scenario.json fehlt")
    else:
        if szenario.get("source") != "llm":
            hart.append("Der Abschlusstext stammt aus der Vorlage, nicht vom Sprachmodell")
        for eintrag in szenario.get("widersprueche") or []:
            hinweise.append(f"markierter Widerspruch: {eintrag.get('zeile', '')}")

    ereignisse = lesen("event_log.json") or []
    # Nur was das Modell schreibt: Die Zeilen des Rechenkerns ([delta:…],
    # Marktberichte) schreibt Python — wie im Prüfsatz ausgenommen.
    englisch = [
        text
        for e in ereignisse
        if isinstance(e, dict)
        and not (text := str(e.get("description", ""))).startswith("[delta")
        and e.get("event_type") != "market_event"
        and ist_englisch(text)
    ]
    if englisch:
        hart.append(f"{len(englisch)} englische Ereignistexte, etwa «{englisch[0][:80]}»")
    return hart, hinweise


def main(argv: list[str] | None = None) -> int:
    stdio_auf_utf8()
    parser = argparse.ArgumentParser(description="Den Vorführbestand erzeugen und prüfen.")
    parser.add_argument("--archiv", type=Path, default=ARCHIV, help="Wohin outputs/ wandert")
    parser.add_argument(
        "--nur-pruefen", action="store_true", help="Nichts verschieben, nichts rechnen"
    )
    parser.add_argument(
        "--nur",
        choices=[lauf.kennung for lauf in bestand()],
        help="Nur diesen Lauf neu rechnen; der übrige Bestand bleibt stehen",
    )
    args = parser.parse_args(argv)
    ausgabe = Path(OUTPUT_DIR)
    laeufe = bestand()

    if not args.nur_pruefen:
        zu_rechnen = [lauf for lauf in laeufe if args.nur in (None, lauf.kennung)]
        nur = tuple(o for lauf in zu_rechnen for o in lauf.ordner) if args.nur else None
        ziel = archivieren(ausgabe, args.archiv, nur)
        print(f"Archiviert nach {ziel}" if ziel else "Nichts zu archivieren.")
        for lauf in zu_rechnen:
            print(f"\n=== {lauf.beschreibung} ===", flush=True)
            launch_simulation(lauf.konfiguration, repo_root=REPO)

    rot = False
    print("\n=== Abnahme ===")
    for lauf in laeufe:
        for ordner in lauf.ordner:
            hart, hinweise = pruefen(ausgabe / ordner, lauf.rechenmodus)
            rot = rot or bool(hart)
            print(f"{'FEHLT' if hart else 'ok':5}  {ordner}")
            for zeile in hart:
                print(f"       ✗ {zeile}")
            for zeile in hinweise:
                print(f"       · {zeile}")
    return 1 if rot else 0


if __name__ == "__main__":
    sys.exit(main())
