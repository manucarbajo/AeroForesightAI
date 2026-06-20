# Simulations-Dashboard

Einfache Web-Oberfläche für die Präsentation: Simulation starten, Ergebnisse ansehen, Run per Chat abfragen.

## Start

```powershell
python -m streamlit run dashboard/app.py
```

Browser: `http://localhost:8501`

## Funktionen

| Bereich | Inhalt |
| --- | --- |
| **Simulation starten** | Szenario, Properties, Faktoren, LLM, Multi-Run, Figures nach Lauf |
| **Ergebnisse ansehen** | Tab **Szenario** (Hauptansicht), Übersicht, Figures, Bericht, Abfrage, Dateien |

**Präsentations-Demo:** Run wählen → **Szenario** lesen → **Figures** → **Abfrage** (Chat). Details: [`../docs/challenge4/scenario_runs.md`](../docs/challenge4/scenario_runs.md)

Run-Figures: `outputs/<run_id>/figures/` (6 PNGs + `manifest.json`) bei aktivierter Option «Figures nach Lauf erzeugen» (Standard). Sweep-Runs: `outputs/sweeps/sweep_<preset>/`.

Projekt-README: [`../README.md`](../README.md)
