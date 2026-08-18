---
description: Mock-Simulation laufen lassen und Kernkennzahlen berichten
---

Führe einen kurzen deterministischen Smoke-Test der Simulation aus, ohne Ollama:

```powershell
python src/run_simulation.py --mock-llm --rounds $ARGUMENTS --quiet
```

Falls `$ARGUMENTS` leer ist, nutze `--rounds 5`.

Danach:
1. Prüfe den Exit-Code und die Konsolenausgabe auf Fehler.
2. Öffne `outputs/<run_id>/tick_mechanics.json` und `outputs/<run_id>/final_narrative.md` (neuester `run_id`-Ordner unter `outputs/`) und fasse kurz zusammen: Anzahl Ticks, Preis-/Booking-Trend, aufgetretene Events.
3. Melde knapp, ob der Lauf sauber durchlief oder wo er abgebrochen ist.
