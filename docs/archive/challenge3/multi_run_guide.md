# AP3 Multi‑Run Guide

Kurzbeschreibung
- Dieses Dokument erklärt, wie Multi‑Run Simulationen für Challenge‑3 (AP3) ausgeführt, checkpointed und wieder aufgenommen werden.

CLI Beispiele
- Single run (standard):

```
python src/run_simulation.py --runs 1
```

- Mehrere deterministische Läufe mit Basis‑Seed 42:

```
python src/run_simulation.py --runs 5 --seed 42
```

Checkpointing und Resume
- Checkpoints werden nach jedem abgeschlossenen Round in `outputs/checkpoints/<run-id>/round_XXXX.json` geschrieben.
- Resume von letzter Checkpoint:

```
python src/run_simulation.py --resume run-001 --runs 1
```

Deterministische Seeds
- Pro Run wird ein Seed verwendet; `SimulationRunner` löst Seeds deterministisch auf Basis des `config.seed` oder des übergebenen `--seed`.

Artefakte
- Standardausgabe: `outputs/<run-id>/...` enthält `event_log.json`, `cib_matrix.json`, `round_history.json`, `run_metadata.json`, `final_narrative.md`.

Runtime Konfig‑Overrides
- Agenten können einfache Aktionen verwenden, um Szenarioparameter zur Laufzeit zu ändern. Format (Aktionsstring):

```
update_scenario_parameter:<parameter_id>=<numeric_value>
```

Beispiel: `update_scenario_parameter:demand_growth_rate=0.05` — wird in `state.config.change_log` protokolliert.

Tests
- Unit tests liegen unter `tests/` und prüfen u. a. Multi‑speak Semantik und Checkpoint Save/Load.
# AP3 Multi-Run, Checkpoint und Resume

## Zweck

AP3 erweitert die Simulation um drei operative Funktionen:

- mehrere voneinander getrennte Durchläufe mit unterschiedlichen Seeds,
- Checkpointing nach jeder Runde,
- Wiederaufnahme eines abgebrochenen Laufs an exakt derselben Stelle.

Das Zeitmodell arbeitet in Quartalen. Ein Lauf deckt standardmäßig Q1 2026 bis Q4 2035 ab, also 40 Runden.

## Single Run

Ein einzelner Lauf nutzt den kompletten Simulations-Stack und schreibt nach jeder Runde einen Checkpoint.

```bash
python -m src.run_simulation --rounds 40 --seed 42
```

Wichtige Artefakte:

- `outputs/event_log.json`
- `outputs/price_history.json`
- `outputs/round_history.json`
- `outputs/run_metadata.json`
- `outputs/segment_analysis.json`
- `outputs/final_narrative.md`
- `outputs/cib_matrix.json`
- optional `outputs/protocol.json` und `outputs/protocol.md`
- optional `outputs/scenarios.json` und `outputs/scenarios.md`
- Checkpoints in `outputs/checkpoints/run-001/`

## Multi-Run

Für unabhängige Wiederholungen wird jeder Lauf mit einem eigenen Seed ausgeführt. Die Seeds werden deterministisch aus dem Basis-Seed abgeleitet, wenn keine explizite Seed-Liste übergeben wird.

```bash
python -m src.run_simulation --runs 5 --seed 100 --rounds 40
```

Ergebnis pro Lauf:

- eigene Artefakte mit Präfix wie `run_001_...`, `run_002_...`
- eigener Checkpoint-Ordner unter `outputs/checkpoints/run-00X/`
- aggregierte Übersicht in `outputs/multi_run_summary.json`

## Resume

Ein Lauf kann über einen Checkpoint oder einen Run-Identifier fortgesetzt werden.

```bash
python -m src.run_simulation --resume outputs/checkpoints/run-001/round_0012.json
```

Alternativ kann der Run-Identifier verwendet werden, wenn der letzte Checkpoint eines Laufs fortgesetzt werden soll:

```bash
python -m src.run_simulation --resume run-001
```

Beim Resume gilt:

- der geladene State ist die einzige Quelle der Wahrheit,
- es wird kein Agent-Memory wiederhergestellt,
- die Simulation läuft ab der gespeicherten Runde weiter.

## Determinismus

Die Reihenfolge der Runs, die Seed-Verteilung und die Sprechreihenfolge im Scheduler sind deterministisch.

- Multi-Run: Seed-Reihenfolge ist fest und reproduzierbar.
- Checkpointing: Der komplette State wird nach jeder Runde geschrieben.
- Scheduler: Gleichstände werden alphabetisch nach Agent-ID aufgelöst.

Damit lassen sich zwei Durchläufe mit identischen Startbedingungen reproduzierbar vergleichen.

## Hinweise für die Integration

- AP1 sollte die tatsächlichen Faktor-Relevanzen an den Scheduler liefern, damit die Standard-Mock-Matrix ersetzt werden kann.
- AP2 sollte Widersprüche und Argumentationssignale strukturiert aus dem Protokoll an den Scheduler zurückmelden.
- AP4 sollte Checkpoint-Resume in Tests gegen echte Abbrüche und Teilstände prüfen, nicht nur gegen Vollständigkeit am Laufende.

## Praktische Empfehlung

Für Integrationstests ist der beste Einstieg:

1. 1 Run mit 1 Seed.
2. Danach 3 Runs mit identischem Basis-Seed.
3. Dann ein Resume auf Basis eines mittleren Checkpoints.

So werden Determinismus, Persistenz und Mehrfachausführung getrennt validiert.