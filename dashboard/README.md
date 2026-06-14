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
| **Ergebnisse ansehen** | Übersicht, **Figures**, Bericht, Abfrage, Dateien |

Run-Figures landen unter `outputs/<run_id>/figures/` (5 PNGs + `manifest.json`), wenn «Figures nach Lauf erzeugen» aktiv ist (Standard).

Projekt-README: [`../README.md`](../README.md)
