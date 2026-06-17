# Challenge 4 — Abschlussbericht

| | |
| --- | --- |
| **Projekt** | Multi-Agenten-Simulation für Szenarioplanung im Flugverkehr |
| **Challenge** | C4 — Dynamik, Wechselwirkungen, Emergenz, Exploration |
| **Domäne** | Europäischer Flugverkehr (F1–F7, 3 Agenten, 1000 Individuen) |
| **Stack** | Python, LangGraph, Ollama / Mock-LLM, Streamlit (optional) |
| **Stand** | Juni 2026 · M0–M11 · **217** pytest-Tests grün |

---

## 1. Forschungsfrage

> Wie und in welcher Qualität können soziotechnische Systeme mit gegenseitig wechselwirkenden Einflussfaktoren durch Multiagentensysteme qualitativ über Zeiträume simuliert werden?

### Antwort (Kurzform)

Challenge 4 zeigt, dass **qualitative Szenarien über Zeiträume simulierbar** sind, wenn numerische Systemdynamik **deterministisch in Python** liegt und LLM-Agenten **nur narrativ** ergänzen (Events, Begründungen, begrenzte Faktorvorschläge). Wechselwirkungen entstehen **emergent** aus gekoppelten Mechanismen (Properties → Kosten → Booking → Markt-Feedback → Faktorregeln → Population-Shifts), nicht aus freier LLM-Interpretation.

**Qualität** wird über reproduzierbare Artefakte (`tick_mechanics.json`, `timeseries/*.csv`, Sweeps, CIB-Consistency-Score) und **217 automatisierte Tests** abgesichert. Der **State Explorer** (M9) antwortet ausschließlich aus Run-Daten — keine erfundenen Kennzahlen.

---

## 2. C4-Aufgabenstellung

| Aufgabe | Umsetzung | Nachweis |
| --- | --- | --- |
| **1. Dynamisierung der Einflussfaktoren** | 14 `factor_rules` in `properties.json`; Startzustände via Sweeps/Dashboard | `timeseries/factors.csv`, `test_factor_dynamics.py` |
| **2. Wechselwirkungen / Emergenz** | Property-Trajektorien, Markt-Feedback, Population-Shifts, Faktor-Ketten (z. B. CO₂ → F2/F6 → F5) | M4-Gates (Preis-Amplitude, Booking-Kopplung), Sweep-Vergleich |
| **3. Exploration des Simulationsstands** | `state_explorer.py`, Dashboard-Chat, Checkpoints | `test_state_explorer.py`, grounded Prompt |

**Emergenz-Definition (Projekt):** Nicht-monotone, wechselwirkungsgetriebene Verläufe — keine triviale Kette „Input steigt → Output fällt“. Szenarien (BAU, Wende, Konflikt) entstehen aus **Faktor-Kombinationen und Regeln in Python**; das LLM erklärt und kommentiert.

---

## 3. Architektur & Arbeitsteilung

### Tick-Pipeline (Endzustand)

```
orchestrator (+1)
  → apply_factor_rules          # Python, M5
  → parallel_round (LLM)        # provider, regulator
  → environment (booking)       # Python, M3/M4
  → consumer (LLM)
  → market (market_rules)       # Python, M4
  → write_events_from_deltas    # Python, M9
  → timeseries, checkpoint
```

Details: [`projectplan.md`](projectplan.md) Anhang A.

### LLM vs. Python

| Komponente | Python | LLM |
| --- | --- | --- |
| Properties, Preis, Booking, Shifts | ✓ | — |
| `factor_rules` (F1–F7) | ✓ | — |
| Faktor-`proposed_state` | validieren (`validate_factor_proposals`) | Regulator: F2, F6 vorschlagen |
| Events | aus Deltas (`[delta:…]`) | beschreiben |
| CIB zur Laufzeit | — (frozen Referenz) | — |
| Chat-Explorer | State lesen | grounded antworten |
| Szenario-Sweeps / 10k Ticks | vollständig | Mock-LLM |

---

## 4. Kernergebnisse

### 4.1 Markt- und Buchungsdynamik (M4)

Referenzlauf (LLM, 40 Ticks): Ticketpreis **98,78 → 126,74 → 118,93 €**; Booking **52–77 %**, kein Kollaps auf 0 %. CO₂-Shocks (Tick 15/30) wirken auf Kosten, Markup und Booking.

Automatisierte Gates: Preis-Amplitude ≥ 8 %, ≥ 2 Richtungswechsel, Booking-Range ≥ 0,12, Kopplung `demand_level` ↔ `booking_rate`.

### 4.2 Faktor-Dynamik (M5)

Faktorübergänge laufen **ohne LLM** über `apply_factor_rules_at_tick_start`. Beispiel: ab Tick 15 (CO₂ > 100 EUR/t) → F2.2, F6.2; niedrige Booking → F1.2.

CIB dient als **Referenzrahmen** (`cib_frozen.json`), nicht als live generierte Matrix. Mapping: [`cib_rationale.md`](cib_rationale.md).

### 4.3 Population & Einkommen (M6)

1000 persistente Individuen mit Verteilungen (normal, beta, lognormal). `income_index` (System) skaliert `income_factor` (Individuum) und damit WTP/Booking. Sechs `regulatory_influences` fließen in `cost_pressure`.

### 4.4 Agent-Profiling (M7)

`agent_profiles.json` steuert `observes`, `may_propose`, `must_not_output`, `depends_on`. Prompt-Filter und harte Parser-Grenzen verhindern erfundene Kennzahlen. Details: [`agent_profiles.md`](agent_profiles.md).

### 4.5 Szenario-Sweeps (M8)

Vier Presets unter `configs/sweeps/`: `business_as_usual`, `co2_delayed`, `freiwillige_wende`, `transformation_conflict`. Deterministische Läufe bis 10.000 Ticks; Auswertung via `scenario_scores.json` und CIB-Consistency. Anleitung: [`scenario_runs.md`](scenario_runs.md).

### 4.6 Exploration & Figures (M9–M10)

- **State Explorer:** CLI + Dashboard-Chat, Kontext aus `tick_mechanics`, `price_history`, `event_log`.
- **Figures:** Global (4-Szenario-Vergleich) und pro Run (5 PNGs + Manifest).

---

## 5. Outputs

Nach jedem Lauf unter `outputs/<run_id>/`:

| Artefakt | Rolle |
| --- | --- |
| `tick_mechanics.json` | Ground Truth pro Tick (M9) |
| `price_history.json` | Preis, demand_level, booking_rate |
| `event_log.json` | Agenten-Events + `[delta:…]` |
| `timeseries/factors.csv` | Faktorzustände F1–F7 |
| `timeseries/properties.csv` | System-Properties |
| `final_narrative.md` | Lesbarer Bericht |
| `checkpoints/` | Resume + Explorer |
| `figures/` | Optional (M10) |

---

## 6. Testabdeckung

**217 Tests** (Stand M11), u. a.:

| Bereich | Testdateien |
| --- | --- |
| Markt-Feedback | `test_market_feedback.py` |
| Faktor-Regeln | `test_factor_dynamics.py` |
| Sweeps & CIB-Score | `test_scenario_sweeps.py`, `test_scenario_consistency.py` |
| Einkommen | `test_income_dynamics.py` |
| Agent-Profile | `test_agent_profiling.py` |
| Explorer | `test_state_explorer.py` |
| Dashboard | `test_dashboard_service.py` |
| E2E | `test_simulation_runner_e2e.py` |

```powershell
python -m pytest
```

---

## 7. Grenzen des Frameworks

| Grenze | Konsequenz |
| --- | --- |
| **Keine live CIB-Generierung** | Dynamik über `factor_rules`, nicht über LLM-Matrix-Updates |
| **3 aggregierte Agenten** | Keine 6 separaten Regulator-LLMs; Regulierung als Properties |
| **Ticks ≠ Kalenderjahre** | Epochen/Iterationen, keine Datumsachse |
| **LLM-Narrative** | Gelegentliche Verwechslung `demand_level` / `booking_rate`; Fallback-Events bei Parse-Fehlern |
| **Emergenz-Gates M7/M8** | Segment-Divergenz und Konflikt-Sweep teils noch offen (M12.4) |
| **Dashboard** | Optionale Präsentationsschicht, kein Abnahme-Kriterium |

Legacy: `CIBExtractorNode` (Challenge 2/3) liegt unter `src/legacy/` — nicht Teil der C4-Pipeline.

---

## 8. Fazit

Challenge 4 erfüllt die Aufgabenstellung **Dynamisierung**, **Wechselwirkungen** und **Exploration** durch eine **hybride Architektur**: Python garantiert reproduzierbare Systemdynamik; LLM-Agenten liefern erklärende Narrative innerhalb enger Profile. Die Forschungsfrage wird **positiv, mit dokumentierten Grenzen** beantwortet: Qualität entsteht durch Ground-Truth-Artefakte, Tests, Sweeps und grounded Exploration — nicht durch freie LLM-Halluzination.

Weiterführend: [`traceability_c1_c4.md`](traceability_c1_c4.md) · [`projectplan.md`](projectplan.md)
