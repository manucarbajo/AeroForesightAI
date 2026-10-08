# Szenario-Läufe — Workflow & Artefakte

Anleitung: Wie aus einem Simulationslauf ein exploratives Szenario wird und wie das Dashboard dafür genutzt wird.

## Präsentations-Demo (empfohlene Reihenfolge)

1. **Dashboard starten:** `python -m dashboard.web.app --port 8511`
2. **Simulation starten** — Szenario wählen, Ticks setzen, optional «Figures nach Lauf erzeugen»
3. **Ergebnisse ansehen** → Run wählen
4. Tab **Szenario** — LLM-generiertes exploratives Szenario (`run_scenario.md`) lesen (Hauptartefakt)
5. Tab **Figures** — 6 PNGs aus `outputs/<run_id>/figures/`
6. Tab **Abfrage** — grounded Chat zum selben Run (State Explorer)
7. Optional: Tab **Bericht** (`final_narrative.md`) für Tick-Detail

Gleicher Ablauf für **Sweep-Läufe** unter `outputs/sweeps/sweep_<preset_id>/` (z. B. `sweeps/sweep_business_as_usual`).

## Output pro Run

Jeder Lauf erzeugt einen **eigenen Ordner** unter `outputs/`:

| Pfad | Inhalt |
| --- | --- |
| `run_scenario.md` / `.json` | **Exploratives Szenario** (P3): LLM wählt 3 CIB-Kandidaten, schreibt Narrativ |
| `final_narrative.md` | Tick-für-Tick-Bericht (Agenten, Kennzahlen) |
| `tick_mechanics.json` | Ground Truth pro Tick (Preis, Booking, Properties) |
| `price_history.json` | Preis, demand_level, booking_rate |
| `event_log.json` | Agenten-Events + Python-Deltas `[delta:…]` |
| `run_metadata.json` | Ticks, Modell, Timestamp |
| `timeseries/*.csv` | Properties, Faktoren F1–F7, Population, Segmente |
| `figures/` | 6 PNGs + `manifest.json` (pro Run, nicht global) |
| `checkpoints/` | Optional — für Resume und Explorer-Tick-Fokus |

### Figures (6 PNGs pro Run)

Erzeugt via `generate_run_figures(run_dir)`:

Der Satz folgt seit August 2026 den **vier Aussagen** der Ergebnisdarstellung;
der Titel im Manifest nennt die Aussage.

| Datei | Aussage | Inhalt |
| --- | --- | --- |
| `preis_und_nachfrage.png` | 1 | Ticketpreis und Buchungsrate |
| `politik_und_wirkung.png` | 2 | CO₂-Abgabe und Buchungsrate |
| `wer_noch_fliegt.png` | 3 | Alterssegmente |
| `bevoelkerung.png` | 3 | Populationsverteilung |
| `faktorlage.png` | 4 | Faktor-Zustände F1–F7 |

`system_dynamics.png` gehört nicht mehr dazu — sie zeigt Eingänge, nicht
Ergebnisse, und entsteht weiterhin als laufübergreifende Auswertung über die CLI.

Figures liegen **nur** im Run-Ordner, es gibt keinen globalen Sammelordner.

## Szenario-Sweeps

Vier Foresight-Presets unter `configs/sweeps/`:

| Preset | Run-ID | Beschreibung |
| --- | --- | --- |
| `business_as_usual` | `sweeps/sweep_business_as_usual` | A1+B1 — hochstabiles Szenario |
| `freiwillige_wende` | `sweeps/sweep_freiwillige_wende` | A2+B2 — selbstverstärkende Wende |
| `transformation_conflict` | `sweeps/sweep_transformation_conflict` | B2 vs A1 — Transformationskonflikt |
| `co2_delayed` | `sweeps/sweep_co2_delayed` | Verzögerte CO₂-Politik |

**CLI:**

```powershell
python -m src.scenario_sweeps
python -m src.scenario_sweeps --sweep transformation_conflict
```

**Aggregate:** `outputs/sweeps/sweep_summary.json`, `outputs/sweeps/scenario_scores.json`

**Dashboard:** Checkbox «Alle Szenario-Presets…» startet alle Sweeps; danach einzelne Runs unter **Ergebnisse ansehen** wählen (`sweeps/sweep_*`).

## CLI-Alternativen

```powershell
# Einzellauf
python src/run_simulation.py --mock-llm --rounds 30

# Figures nachträglich
python -m src.figure_generator --run-only run_20260614T112808Z

# Explorer (CLI)
python -m src.state_explorer --run-id run_20260614T112808Z --question "Warum fiel booking?"
```

## Weiterführend

- [`cib_role.md`](cib_role.md) — Rolle der CIB-Referenz-Matrix
- [`cib_rationale.md`](cib_rationale.md) — CIB-Kanten ↔ factor_rules
