# Traceability — Challenges 1 bis 4

Überblick, wie Konzepte aus C1–C3 in Challenge 4 weitergeführt oder ersetzt wurden.

| Challenge | Fokus | C4-Status |
| --- | --- | --- |
| **C1** | Domäne, F1–F7, Akteure, CIB-Konzept | Basis unverändert |
| **C2** | LangGraph-MVP, Event-Log, CIB-Extractor | Pipeline erweitert; Extractor → Legacy |
| **C3** | Statisches Verhalten, Protokoll, Multi-Run | Referenz-CIB frozen |
| **C4** | Dynamik, Emergenz, Sweeps, Explorer | M0–M11 umgesetzt |

---

## Einflussfaktoren F1–F7

| Konzept | C1 | C2/C3 | C4 |
| --- | --- | --- | --- |
| 7 Faktoren, je 2 Zustände | ✓ | `configs/factors.json` | unverändert |
| Faktor im State | `EnvironmentState.factors` | ✓ | ✓ |
| Dynamik | LLM-Vorschläge | teils ungegated | **`factor_rules`** (Python, M5) |
| CIB zur Laufzeit | live / Extractor | LLM-Extractor | **frozen** + End-Score (`scenario_consistency`) |
| Zeitreihe | — | — | `timeseries/factors.csv` |

---

## Akteure & Population

| Konzept | C1 | C2 | C4 |
| --- | --- | --- | --- |
| Consumer, Provider, Regulator | MVP-Akteure | `agents.json` | + **`agent_profiles.json`** (M7) |
| Heterogene Konsumenten | Segmente | Verteilungen | **1000 persistente Individuen** (M3) |
| Multi-Label-Segmente | — | — | business, leisure, price_sensitive, frequent_flyer |
| Regulator-Instanzen | 6 Akteure (Vision) | 1 LLM-Agent | **`regulatory_influences[]`** Properties (M6) |

---

## System-Properties & Markt

| Konzept | C1/C2 | C4 |
| --- | --- | --- |
| Szenarioparameter | JSON-Config | **`properties.json`**: trajectories, rules |
| Preisbildung | Markt-Node heuristisch | **`market_rules`**, `cost_pressure`, yield feedback (M4) |
| CO₂, SAF, Öl, Nachfrage | statisch / einfach | **Trajektorien + Shocks** (M2) |
| Einkommen | — | **`income_index`** + `income_factor` (M6) |
| Runtime-Properties | — | `provider_markup`, `ticket_price` (emergent) |

---

## Simulationslogik

| Konzept | C2 | C4 |
| --- | --- | --- |
| Rundenloop | `run_simulation.py` | **`simulation_runner.py`** + Checkpoints |
| Agenten-Reihenfolge | sequentiell | **parallel_round** (provider/regulator) → consumer |
| Faktor-Update | Environment LLM | **`apply_factor_rules_at_tick_start`** |
| Booking | Segment-Shares | **Population-Sampler** + `evaluate_booking` |
| Events | Agent-Text | **Deltas + Narrative** (`event_deltas.py`, M9) |
| Zeitmodell | Jahre/Runden | **Ticks** (neutral, keine Kalenderzuordnung) |
| CIBExtractorNode | `src/nodes/` | **`src/legacy/cib_extractor_node.py`** |

---

## Outputs & Exploration

| Konzept | C2 | C4 |
| --- | --- | --- |
| `event_log.json` | ✓ | + `[delta:…]`-Einträge |
| `price_history.json` | ✓ | + demand_level, booking_rate |
| `cib_matrix.json` (live) | post-hoc Extractor | Referenz frozen; Score in Sweeps |
| Ground Truth pro Tick | — | **`tick_mechanics.json`** (M9) |
| Chat über Run | — | **`state_explorer.py`** |
| Szenario-Vergleich | — | **Sweeps + Figures** (M8, M10) |
| Dashboard | — | optional `dashboard/` |

---

## Tests

| Phase | Tests (ca.) | Fokus |
| --- | --- | --- |
| C2 | 41 | Config, Agent-Parsing, E2E |
| C4 M11 | **217** | Markt, Faktoren, Sweeps, Profile, Explorer, Dashboard |

---

## Bewusste Abweichungen von C1/C2

| C1/C2 Erwartung | C4 Realität | Begründung |
| --- | --- | --- |
| CIB live aus Event-Log | frozen + `factor_rules` | Reproduzierbarkeit, kein LLM-Matrix-Drift |
| LLM setzt Faktoren frei | Python-Regeln + gated Vorschläge | Emergenz aus Mechanik, nicht aus Prompt |
| Kalenderjahre 2025–2035 | neutrale Ticks | Coaching-Vorgabe C4 |
| 6 Regulator-Agenten | 6 Property-Einflüsse | MVP-Komplexitätsgrenze |
| Irreversible Faktorwechsel | bidirektionale Regeln | Szenario-Vielfalt (z. B. F1.1 ↔ F1.2) |

---

## Datei-Index (C4 Kern)

| Thema | Datei |
| --- | --- |
| Faktor-Regeln | `src/factor_dynamics.py`, `configs/properties.json` |
| Markt | `src/nodes/market_node.py`, `src/simulation_functions.py` |
| Population | `src/population_sampler.py` |
| Sweeps | `src/scenario_sweeps.py`, `configs/sweeps/*.json` |
| CIB-Score | `src/scenario_consistency.py` |
| Explorer | `src/state_explorer.py` |
| Profile | `configs/agent_profiles.json`, `src/agent_dependencies.py` |
| Report | `docs/challenge4/challenge4_report.md` |
