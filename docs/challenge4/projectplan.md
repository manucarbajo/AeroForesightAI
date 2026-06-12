# Project Plan — Challenge 4 (Meilensteine)

| | |
| --- | --- |
| **Stand** | 11.06.2026 (Review nach `run_20260611T155300Z`) |
| **Branch** | `m3/challenge4` |
| **Ziel** | Vollständige Umsetzung C4: Dynamik, Wechselwirkungen, Emergenz, Exploration |
| **Fortschritt** | **M0–M5 erledigt** · M6–M12 offen · pytest **179** grün |
| **Nächster Schritt** | **M6** (Regulierung, Einkommen, Verteilungen) |

## Forschungsfrage

> Wie und in welcher Qualität können soziotechnische Systeme mit gegenseitig wechselwirkenden Einflussfaktoren durch Multiagentensysteme qualitativ über Zeiträume simuliert werden?

Beantwortung über implementierte Mechanismen und `challenge4_report.md` (M11).

## C4 Aufgabenstellung

1. Dynamisierung der Einflussfaktoren (z. B. CO₂ ab Tick N)
2. Wechselwirkungen im System (Faktoren, Markt, Population, Agenten) — emergent, nicht trivial
3. Exploration des Simulationsstands (Chat über Checkpoint/Protokoll)

**Emergenz:** Nicht-monotone, wechselwirkungsgetriebene Verläufe — keine Kette „Input steigt → Output fällt“. Szenarien (BAU / Wende / Transformations-Konflikt) entstehen aus Faktor-Kombinationen in Python; LLM erklärt nur.

**Ticks:** `max_ticks` = Epochen/Iterationen, keine Kalenderjahre.

## Meilenstein-Kette

```
M0 ─ M1 ─ M2 ─ M3 ─ M4 ─ M5 (erledigt)
                              │
                              ├─► M6 Regulierung + Einkommen + Verteilungen  ← NÄCHSTER SCHRITT
                         ├─► M7 Agent-Profiling
                         │
                         └─► M8 Sweeps ─► M9 Events/Explorer ─► M10 Figures ─► M11 Doku ─► M12 Integration
```

**Reihenfolge:** M5 → M6 → M7 → M8 → M9 → M10 → M11 → M12 (M4 abgeschlossen).  
M5/M6/M7 vor M8 (Sweeps brauchen Faktor-Regeln, Einkommen, Profile).

## Traceability Challenges 1–4

| Challenge | Meilenstein | Status |
| --------- | ----------- | ------ |
| **C1** Systementwurf (Domäne, F1–F7) | M0–M3 | erledigt |
| **C2** Workbench (LangGraph, Studio, CLI) | M1 | erledigt |
| **C3** Statisches Verhalten (CIB-Referenz) | M0 | erledigt |
| **C4** Dynamik + Emergenz | M4–M12 | **teilweise** (M0–M5 erledigt; M6–M12 offen) |

| C3 (statisch) | C4 (dynamisch) | Meilenstein |
| ------------- | -------------- | ----------- |
| Fixe CIB-Matrix | `factor_rules` aus CIB-Kanten | M5 |
| Segment-Shares | Persistente Individuen + Multi-Label | M3 |
| LLM-Faktorvorschläge ungegated | Python-Validierung | M5 |
| Einmalige Marktformel | `market_rules` + Runtime-Properties + `sync_demand_level` | M4 |
| Keine Sweeps | 10.000 Ticks deterministisch | M8 |

## Coaching-Prinzipien (Leitplanken)

| Prinzip | Umsetzung | Meilenstein |
| ------- | --------- | ----------- |
| Eigenschaften statt Klassen | `properties.json` | M2, M3 |
| Variablen über Lauf | Trajectories + Tick-Regeln | M2, M6 |
| Diskrete Epochen | Orchestrator → Agenten → Markt → Environment | M1 |
| Zahlen Python, LLM qualitativ | Arbeitsteilung (Anhang A) | M4–M9 |
| 1000 heterogene Agenten | Verteilungen, Multi-Label, persistent | M3 |
| Stabilität vieler Iterationen | Clipping, 10k-Benchmark | M4, M8 |
| Events aus Deltas | `event_log` | M9 |
| 6 Regulierungseinflüsse | `regulatory_influences[]` | M6 |
| CIB vergleichend | `scenario_consistency`, `scenario_scores.json` | M5, M8 |
| Agent-Profiling | `agent_profiles.json` | M7 |
| Einkommen über Zeit | `income_index` + `income_factor` | M6 |

## Ist-Zustand (11.06.2026)

| Bereich | Status | Details |
| ------- | ------ | ------- |
| M0–M3 Basis | **erledigt** | Property-Engine, 1000 Individuen, CIB frozen, Pipeline |
| M4 Markt | **erledigt** | Rückkopplung, `cost_index`, `market_rules`, 30-Tick-Abnahmetest grün |
| M1 Workbench | **erledigt** | Tick-Terminal, Checkpoints/5, Consumer nach Buchung, Narrative-Aggregation |
| LLM-Runs (40 Ticks) | **demo-tauglich** | Referenz: `run_20260611T155300Z` — Mechanik ok, Narrative noch repetitiv |
| Faktoren | **erledigt (M5)** | `factor_rules` F1–F7, `validate_factor_proposals()`, `timeseries/factors.csv` |
| CIB-Methodik | **teilweise** | `factor_rules` + `cib_rationale.md` (M5); Sweeps fehlen (M8) |
| Agent-Profiling | **teilweise** | Prompt-Grounding M1.8/M1.9; `agent_profiles.json` fehlt (M7) |
| Einkommen | **offen (M6)** | Nur Segment-`income_level`; kein `income_index` |
| Exploration | **offen (M9)** | Checkpoints + `--resume` da; kein `state_explorer` |
| Sweeps / 10k | **offen (M8)** | — |
| Figures / Report | **offen (M10–M11)** | — |

**Ist-Pipeline:** `orchestrator → apply_factor_rules → parallel_round (provider/regulator) → environment (booking, validate_factor_proposals) → consumer → market (market_rules) → factors.csv`.

**Referenz-Run M4 (LLM, 40 Ticks):** Preis 98,78 → 126,74 → 118,93 €; booking 52–77 %, kein Kollaps auf 0 %; CO₂-Shocks Tick 15/30 wirksam.

### Bekannte Lücken (nicht M4, vor M8 adressieren)

- LLM verwechselt teils `demand_level` mit `booking_rate` (Provider Tick 1)
- Consumer-Narrative wiederholt „eco-friendly / SAF“ trotz hoher Buchung
- 11× „Fallback event…“ im letzten Run → **M7/M9**

---

# Erledigte Meilensteine

## M0 — CIB als Referenz — erledigt

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M0.1 | `cib_frozen.json` (14×14) | `configs/` | erledigt |
| M0.2 | Kein CIB-LLM im Tick-Loop | `simulation_runner.py` | erledigt |
| M0.3 | Kein `impact_assessment` in Prompts | `prompts/` | erledigt |
| M0.4 | Export Referenzkopie | `output_writer.py` | erledigt |
| M0.5 | `scenario_consistency.py` vorhanden | `src/` | erledigt |

## M1 — Workbench & Pipeline — erledigt

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M1.1 | Tick-Modell (`tick_unit: tick`) | `simulation_config.json` | erledigt |
| M1.2 | LangGraph: Orchestrator → ParallelRound → Environment → Consumer → Market | `langgraph_workflow.py` | erledigt |
| M1.3 | Studio + CLI | `run_simulation.py` | erledigt |
| M1.4 | `outputs/<run_id>/`, Checkpoints alle **5 Ticks** (+ letzter Tick) | `checkpoint_manager.py`, `simulation_runner.py` | erledigt |
| M1.5 | Ollama / MockLLM | `llm_client.py` | erledigt |
| M1.6 | Englische Agent-Prompts | `prompts/` | erledigt |
| M1.7 | Terminal: Tick-Fortschritt (`[tick N/M] done — price, booking, carbon`) | `simulation_runner.py` | erledigt |
| M1.8 | Consumer **nach** Buchung (Events an `booking_rate` gekoppelt) | `parallel_round_node.py`, `agent_node.py`, `consumer.md` | erledigt |
| M1.9 | Provider/Regulator: `prior_booking_block` (Vortick Ground Truth), 1 Event/Tick, NO_OP nur bei Stabilität | `agent_node.py`, `provider.md`, `regulator.md` | erledigt |
| M1.10 | `final_narrative.md`: alle Agenten + Events pro Tick aus `event_log` (nicht nur letzter `RoundResult`) | `output_writer.py` | erledigt |

**M1.9 Abnahme (Coaching-konform):** Zahlen aus Python (`population_stats` Vortick + `scheduled_property_events`); LLM nur qualitativ. Entspricht Coaching „Events aus Deltas“ (Vorstufe M9) und M7-Schema `depends_on: consumer.booking_rate` (Vortick). Pipeline unverändert: Provider/Regulator **vor** Buchung. Explizites `NO_OP` erzeugt kein Fallback-Event mehr.

## M2 — Property-Engine — erledigt

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M2.1 | `resolve_property()`, Trajectories | `property_engine.py` | erledigt |
| M2.2 | Typen: baseline, set, ramp, step_function | `property_engine.py` | erledigt |
| M2.3 | `properties.json` System-Properties | `configs/` | erledigt |
| M2.4 | Markt aus Properties (kein LLM für Zahlen) | `simulation_functions.py` | erledigt |
| M2.5 | `timeseries/properties.csv` | `output_writer.py` | erledigt |
| M2.6 | CO₂ ab Tick 15 in Config + Tests | `test_property_engine.py` | erledigt |
| M2.7 | `policy_schedule` entfernt | Code, Config | erledigt |

## M3 — Population & Individuen — erledigt

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M3.1 | `Individual` persistent, Multi-Label | `population_models.py` | erledigt |
| M3.2 | 1000 Individuen, lognormal/beta | `population_sampler.py` | erledigt |
| M3.3 | `evaluate_booking()` WTP + Logit | `population_sampler.py` | erledigt |
| M3.4 | `apply_factor_shifts()` (2 Regeln) | `properties.json` | erledigt |
| M3.5 | Environment ohne LLM-Shares | `environment_node.py` | erledigt |
| M3.6 | `population.csv`, `timeseries/population.csv` | `output_writer.py` | erledigt |
| M3.7 | Tests Persistenz, Multi-Label | `test_population_sampler.py` | erledigt |
| M3.8 | `shift_rules` mit `once: true` + `applied_shift_rules`; `eco_penalty` nur über CO₂-Baseline | `population_sampler.py`, `properties.json` | erledigt |

## M4 — Markt-Systemdynamik & Emergenz — erledigt

**Ziel:** Geschlossene Rückkopplung Anbieter ↔ Nachfrage mit **sichtbarer** Systemdynamik (Foresight-Demo-tauglich), nicht nur technisches „Preis kann theoretisch fallen“.

**Pipeline (verbindlich):** `parallel_round (provider+regulator) → environment (booking) → consumer (narrative) → market (feedback)` — auch in `simulation_runner.py`.

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M4.1 | `MarketFeedbackConfig`, `PriceModelConfig` | `property_models.py` | erledigt |
| M4.2 | `market_feedback`, `price_model` in Config | `properties.json` | erledigt |
| M4.3 | `compute_cost_pressure()` | `simulation_functions.py` | erledigt |
| M4.4 | `apply_market_feedback()` | `simulation_functions.py` | erledigt |
| M4.5 | `sync_demand_level()` | `simulation_functions.py` | erledigt |
| M4.6 | `ticket_price` in `market_metrics` + `property_timeseries` | `market_node.py` | erledigt |
| M4.7 | Pipeline: Buchung vor Feedback (LangGraph + Runner) | `environment_node.py`, `market_node.py`, `langgraph_workflow.py`, `simulation_runner.py` | erledigt |
| M4.8 | Stabilitäts-Clipping | `simulation_functions.py` | erledigt |
| M4.9 | Unit-Tests Feedback-Loop | `tests/test_market_feedback.py` | erledigt |
| M4.10 | `cost_index`: kumulierende Treibstoffkosten (Kosten ≠ Ticket) | `simulation_functions.py`, `environment_node.py`, `market_node.py` | erledigt |
| M4.11 | Stärkeres Feedback (Markup ∝ Referenz, höhere Dämpfung) | `simulation_functions.py`, `properties.json` | erledigt |
| M4.12 | Emergenz-Abnahmetest 30 Ticks (hart) | `tests/test_market_feedback.py` | erledigt |
| M4.13 | Preis konfigurierbar: `price_coefficients`, `provider_markup`/`ticket_price` Properties, `market_rules` | `properties.json`, `market_rules.py`, `simulation_functions.py` | erledigt |

### Abnahme M4 — erfüllt

| Kriterium | Schwelle | Status |
| --------- | -------- | ------ |
| Preis-Amplitude | Range ≥ **8 %** vom Mittelwert | ✓ `test_m4_emergence_over_30_ticks` |
| Richtungswechsel Preis | ≥ **2** lokale Umkehrungen | ✓ |
| `booking_rate`-Amplitude | Range ≥ **0,12** | ✓ |
| Marge (Preis − Kosten) | Range ≥ **8 €** | ✓ |
| Tick 1 | `booking_rate` gesetzt | ✓ |
| Kopplung | `demand_level` via `sync_demand_level` | ✓ |
| Config statt Hardcoding | `price_coefficients` + `market_rules` in JSON | ✓ |
| Runtime-Properties | `provider_markup`, `ticket_price` in `property_timeseries` | ✓ |
| LLM-Referenzlauf 40 Ticks | Mechanik stabil, keine Booking-Kollaps | ✓ `run_20260611T155300Z` |

**Nicht M4:** Segment-Divergenz business/price_sensitive (M7), Szenario-Scores (M8) — Faktor-Wechselwirkungen in M5.

## M5 — Faktor-Dynamik & CIB-Methodik — erledigt

**Ziel:** Wechselwirkungen F1–F7; CIB als Referenzrahmen für Regeln und End-Score — Matrix wird im Lauf nicht neu generiert.

**Pipeline-Erweiterung:** `apply_factor_rules_at_tick_start` vor `parallel_round`; LLM-`state_changes` nur nach `validate_factor_proposals()` (Regulator: F2/F6; Provider/Consumer: keine Faktorvorschläge).

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M5.1 | `RuntimeMetrics` + Regel-Injection | `factor_dynamics.py` | erledigt |
| M5.2 | `apply_factor_rules()` | `factor_dynamics.py` | erledigt |
| M5.3 | `factor_rules` F1–F7 (14 Regeln) | `properties.json` | erledigt |
| M5.4 | `shift_rules` F1–F7 (je ≥ 1, 8 Regeln) | `properties.json` | erledigt |
| M5.5 | `validate_factor_proposals()` | `factor_dynamics.py`, `environment_node.py`, `validation.py` | erledigt |
| M5.6 | CIB-Kanten → Regeln (+ optional Loader) | `properties.json` | erledigt (manuell); Loader optional übersprungen |
| M5.7 | `timeseries/factors.csv` | `output_writer.py`, `run_simulation.py` | erledigt |
| M5.8 | `cib_rationale.md` (Methodik, Kanten-Mapping) | `docs/challenge4/cib_rationale.md` | erledigt |
| M5.9 | Tests | `tests/test_factor_dynamics.py`, `tests/test_simulation_runner_e2e.py` | erledigt |

### Abnahme M5 — erfüllt

| Kriterium | Status |
| --------- | ------ |
| Faktorübergänge via `factor_rules` ohne LLM | ✓ `test_factor_transitions_without_llm_over_30_ticks` |
| LLM-Vorschläge nur innerhalb erlaubter Targets | ✓ `validate_factor_proposals`, Regulator F2/F6 |
| Provider/Consumer-Faktorvorschläge abgelehnt | ✓ `AGENT_FACTOR_PERMISSIONS` |
| `timeseries/factors.csv` Export | ✓ |
| Konflikt-Sweep &lt; BAU bei `consistency_score` | offen (M8 Sweeps) |

---

## M6 — Regulierung, Verteilungen, Einkommensdynamik — erledigt

**Ziel:** 6 Regulierungs-Instanzen; Bevölkerung step_function; 3 Verteilungstypen; Einkommen über den Lauf.

### Einkommensdynamik

| Ebene | Property | Mechanismus |
| ----- | -------- | ----------- |
| System | `income_index` | Trajectory (ramp / step_function) |
| Individuum | `income_factor` | Initial × `income_index(tick)` |
| Kopplung | `wtp_eur` | Skalierung pro Tick |
| Regeln | `shift_rules` | F4.2 → `income_factor` −δ |

```json
{
  "id": "income_index",
  "trajectory": {
    "baseline": 1.0,
    "rules": [
      { "active_from_tick": 10, "effect": { "type": "ramp", "to_value": 0.92, "over_ticks": 5 } },
      { "active_from_tick": 20, "effect": { "type": "set", "value": 1.05 } }
    ]
  }
}
```

| ID | Aufgabe | Datei | Status | Erklärung |
| -- | ------- | ----- | ------ | --------- |
| M6.1 | 6 `regulatory_influences` | `properties.json` | erledigt | Eingepflegt in properties.json inkl. when-Bedingungen. |
| M6.2 | `bevoelkerungsentwicklung` step_function | `properties.json` | erledigt | Trajectory in Config; Wachstums-/Schrumpfungs-Logik in population_sampler implementiert. |
| M6.3 | Normalverteilung (3. Typ neben lognormal, beta) | `population_sampler.py` | erledigt | Implementiert via `_sample_normal` Funktion. |
| M6.4 | Alter × Property Export | `output_writer.py` | erledigt | `save_age_property_csv` aggregiert nach Altersgruppen (WTP, Awareness, Income). |
| M6.5 | Provider-Kosten-Properties | `properties.json` | erledigt | `maintenance_cost_index` & `staff_cost_index` angelegt und in `compute_cost_pressure` als Multiplikator ergänzt. |
| M6.6 | `income_index` System-Property | `properties.json` | erledigt | Trajectory angelegt. |
| M6.7 | `income_factor` pro Individual, Update/Tick | `population_models.py`, `population_sampler.py` | erledigt | Funktion `update_income_factors` skaliert individuelles Einkommen. |
| M6.8 | WTP-Kopplung Einkommen | `evaluate_booking()` | erledigt | `affordability_limit` multipliziert `wtp_eur` mit `income_factor`. |
| M6.9 | `shift_rules` F4 ↔ Einkommen | `properties.json` | erledigt | `income_drop_f4_strict` Regel senkt Faktor via `-0.15` Delta. |
| M6.10 | Export `income_factor` in CSV/timeseries | `output_writer.py` | erledigt | Durchschnittlicher Faktor in `population.csv` & `age_property.csv` enthalten. |
| M6.11 | Tests | `tests/test_income_dynamics.py` | erledigt | Abdeckung über M6 Tests erfolgreich. |

**Abnahme M6:** F4.2 + fallender `income_index` → booking-Divergenz `price_sensitive` vs. `business`.

---

# Offene Meilensteine

## M7 — Agent-Profiling

**Ziel:** Explizite Profile mit `observes`, `depends_on`, `must_not_output`; Agenten reagieren auf `event_log`.

**Vorarbeit (M1.8–M1.10, noch ohne `agent_profiles.json`):** Consumer `observed_booking_block`; Provider/Regulator `prior_booking_block`; Narrative zeigt alle Agenten-Events; `NO_OP` ohne Fallback-Event.

### Profil-Schema (`configs/agent_profiles.json`)

```json
{
  "consumer": {
    "observes": ["market_metrics", "population_stats", "event_log_recent", "factors F1,F5,F6"],
    "may_propose": [],
    "must_not_output": ["ticket_price", "booking_rate", "numeric_shares"],
    "depends_on": ["provider.events", "regulator.proposed_state"]
  },
  "provider": {
    "observes": ["market_metrics", "booking_rate", "cost_pressure", "event_log_recent", "factors F3,F4"],
    "may_propose": ["events"],
    "must_not_output": ["ticket_price", "carbon_tax_level"],
    "depends_on": ["regulatory_influences", "consumer.booking_rate"]
  },
  "regulator": {
    "observes": ["market_metrics", "factors F2,F6,F7", "event_log_recent", "population_stats"],
    "may_propose": ["factor_state F2", "factor_state F6"],
    "must_not_output": ["ticket_price", "tax_level_numeric"],
    "depends_on": ["provider.events", "consumer.booking_rate"]
  }
}
```

| ID | Aufgabe | Datei | Status | Umsetzung |
| -- | ------- | ----- | ------ | --------- |
| M7.1 | `AgentProfile` Modell | `models/agent_models.py` | erledigt | `AgentProfile` Pydantic Modell mit `observes`, `may_propose`, `must_not_output` und `depends_on` hinzugefügt. |
| M7.2 | Profile laden + Prompt-Injection | `config_loader.py`, `agent_node.py` | erledigt | `configs/agent_profiles.json` angelegt; wird in `load_agents()` an `AgentConfig` angehängt. `AgentNode` filtert nun Metriken/Faktoren und erzwingt `may_propose` hart im Parser. |
| M7.3 | Prompts: nur `observes`, keine freien Zahlen | `prompts/*.md` | erledigt | Agenten-Prompts (consumer, provider, regulator) angepasst, um Zahlenerfindungen strikt zu verbieten. |
| M7.4 | Reaktion auf `event_log` (letzte N Events) | `agent_node.py` | erledigt | Agenten müssen laut Prompt zwingend `Recent events` beachten, aber dürfen sie nicht einfach kopieren; NO_OP falls nichts passiert. |
| M7.5 | `agent_profiles.md` Abhängigkeitsgraph | `docs/challenge4/` | erledigt | Datei `agent_profiles.md` inkl. Mermaid-Diagramm für Output-Abhängigkeiten erstellt. |
| M7.6 | Tests | `tests/test_agent_profiling.py` | erledigt | Neue Unittests (`test_agent_node_filters_*`) geschrieben, die alle Profileinstellungen erfolgreich prüfen. |

**Abnahme M7:** Provider referenziert Event aus Log; Regulator nur F2/F6; Consumer keine erfundenen Zahlen.

---

## M8 — Sweeps & Benchmark

**Ziel:** Vier Foresight-Szenarien; 10.000 Ticks ohne LLM; CIB-Scores pro Sweep.

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M8.1 | `scenario_sweeps.py` | `src/` | offen |
| M8.2 | CLI `--deterministic-only`, `--sweep` | `run_simulation.py` | offen |
| M8.3 | Sweep `co2_delayed.yaml` | `configs/sweeps/` | offen |
| M8.4 | Sweep `business_as_usual.yaml` (A1+B1) | `configs/sweeps/` | offen |
| M8.5 | Sweep `freiwillige_wende.yaml` (A2+B2) | `configs/sweeps/` | offen |
| M8.6 | Sweep `transformation_conflict.yaml` (B2 vs A1) | `configs/sweeps/` | offen |
| M8.7 | `sweep_summary.json` | `scenario_sweeps.py` | offen |
| M8.8 | End-Tick → `scenario_scores.json` | `scenario_sweeps.py`, `scenario_consistency.py` | offen |
| M8.9 | Benchmark 10.000 Ticks | Test | offen |
| M8.10 | Tests | `tests/test_scenario_sweeps.py` | offen |

**Abnahme M8:** Vier Sweeps reproduzierbar; 10k stabil; CO₂ Tick 15 messbar in Sweep.

---

## M9 — Events & Exploration (C4 Aufgabe 3)

**Ziel:** Geschehnisse im Log; Provider-Reaktionen sichtbar; grounded Chat über Checkpoint.

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M9.1 | `write_events_from_deltas()` | `protocol_generator.py` / neu | offen |
| M9.2 | Provider-Events bei Preisänderung | `market_node.py` | offen |
| M9.3 | `state_explorer.py` | `src/` | offen |
| M9.4 | CLI `state_explorer.py --run-id` | `src/` | offen |
| M9.5 | Checkpoint-Load Tick N | `checkpoint_manager.py`, `run_simulation.py --resume` | **teilweise** (Load/Resume da; Explorer-Integration fehlt) |
| M9.6 | Explorer-Prompt: keine erfundenen Zahlen | `state_explorer.py` | offen |
| M9.7 | Koppelung Profile + `event_log` in Agent-Prompts | `agent_node.py` | offen |
| M9.8 | Tests | `tests/test_state_explorer.py` | offen |

**Abnahme M9:** `event_log` enthält Preis-/Faktor-Deltas; Chat antwortet nur aus State/CSV.

---

## M10 — Szenario-Outputs & Figures

| ID | Aufgabe | Artefakt | Status |
| -- | ------- | -------- | ------ |
| M10.1 | Dokumentierte Sweep-Läufe (≥ 3) | `outputs/` | offen |
| M10.2 | Figure booking_rate je Property | `docs/challenge4/figures/` | offen |
| M10.3 | Figure Preis vs. booking (30 Ticks) | `figures/` | offen |
| M10.4 | Figure CO₂ vor/nach Tick 15 | `figures/` | offen |
| M10.5 | Figure Alter × Property | `figures/` | offen |
| M10.6 | Figure Faktor-Zustände über Zeit | `figures/` | offen |

---

## M11 — Doku & Report

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| M11.1 | `challenge4_report.md` (Forschungsfrage, Qualität, Grenzen Framework) | `docs/challenge4/` | offen |
| M11.2 | `cib_rationale.md` (nach M5.8) | `docs/challenge4/` | offen |
| M11.3 | `agent_profiles.md` (nach M7.5) | `docs/challenge4/` | offen |
| M11.4 | `traceability_c1_c4.md` | `docs/challenge4/` | offen |
| M11.5 | README: Sweeps, Explorer, Profile, Emergenz | `README.md` | offen |
| M11.6 | `CIBExtractorNode` → `src/legacy/` | Refactor | offen |

---

## M12 — Integration & Gesamtabnahme

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| M12.1 | E2E: 30 Ticks MockLLM | **teilweise** (`test_simulation_runner_e2e.py`) |
| M12.2 | E2E: 30 Ticks `deterministic-only` — gleiche Numerik | offen (braucht M8.2 `--deterministic-only`) |
| M12.3 | Voller `pytest`-Lauf (alle M4–M9 Tests) | **teilweise** (179 Tests M0–M5; M6–M9 Tests fehlen noch) |
| M12.4 | Gesamtabnahme Emergenz (Checkliste Anhang B) | offen |

---

# Anhänge

## Anhang A — Architektur Endzustand

### Arbeitsteilung LLM vs. Python

| Komponente | Python | LLM |
| ---------- | ------ | --- |
| Properties, Preis, Buchung, Shifts, `factor_rules` | ✓ | — |
| Faktor-`proposed_state` | validieren | vorschlagen |
| Events | aus Deltas | beschreiben |
| CIB | Referenz | — |
| Chat-Explorer | State lesen | grounded antworten |
| Sweeps / 10k Ticks | vollständig | MockLLM |

### Ebenen

| Ebene | Beispiele | Mechanismus |
| ----- | --------- | ----------- |
| System-Properties (trajectory) | `carbon_tax_level`, `fuel_price_change`, `saf_mandate_share`, … | `resolve_exogenous_system_properties()` |
| System-Properties (runtime/computed) | `provider_markup`, `ticket_price` | Baseline in JSON; Laufwerte aus `market_rules` |
| Individuen-Properties | `price_sensitive`, `wtp_eur`, `awareness`, `income_factor` | Sampling + Shifts + `income_index(t)` |
| Regulierungs-Instanzen | EU-ETS, RefuelEU, … (6) | → `cost_pressure` (M6) |
| Runtime-Metrics | `booking_rate`, `cost_pressure`, `cost_index` | → `market_rules`, `factor_rules` (M5) |

### Tick-Pipeline (Endzustand)

```
State(t)
  → orchestrator (+1)
  → resolve_exogenous_system_properties(tick)
  → apply_factor_rules(factors, runtime_metrics)
  → parallel_round (LLM / MockLLM)
  → validate_factor_proposals(factor_rules)
  → compute_cost_pressure(price_model.coefficients, cost_index)
  → apply_factor_shifts(individuals)
  → evaluate_booking(individuals, last ticket_price)
  → apply_market_rules(booking_rate → provider_markup → ticket_price)
  → sync_demand_level(booking_rate)
  → write_events_from_deltas()
  → aggregate, timeseries, checkpoint
  → State(t+1)
```

**LangGraph:** `parallel_round (provider/regulator) → environment (booking) → consumer → market (market_rules) → log`.

### `properties.json` — Ist-Schema M4 (Auszug)

```json
{
  "system_properties": [
    { "id": "carbon_tax_level", "source": "trajectory", "trajectory": { "baseline": 50, "rules": [...] } },
    { "id": "provider_markup", "source": "runtime", "trajectory": { "baseline": 28 } },
    { "id": "ticket_price", "source": "computed", "trajectory": { "baseline": 128 } }
  ],
  "market_rules": [{
    "id": "provider_yield_feedback",
    "when": { "enabled": true },
    "effect": {
      "type": "booking_yield_feedback",
      "update_property": "provider_markup",
      "publish_property": "ticket_price",
      "compose": "cost_pressure + provider_markup",
      "target_booking_rate": 0.70,
      "markup_adjustment_per_tick": 0.08,
      "max_price_change_fraction": 0.08,
      "damping": 0.85,
      "booking_weight": 0.6
    }
  }],
  "price_model": {
    "base_price": 100,
    "compound_fuel_on_cost": true,
    "coefficients": {
      "carbon_per_tonne": 0.001,
      "saf_premium_factor": 0.5,
      "margin_reference_fraction": 0.08
    }
  },
  "market_feedback": { "...": "Fallback wenn market_rules leer" }
}
```

**Property-`source`:** `trajectory` = exogen pro Tick; `runtime` = emergent (nur Baseline in JSON); `computed` = aus anderen Properties zusammengesetzt.

**Zielschema M6+** (noch offen): `regulatory_influences[]`, `income_index`. `factor_rules` + `shift_rules` F1–F7 erledigt (M5).

## Anhang B — Emergenz-Gates pro Meilenstein

| Meilenstein | Emergenz-Gate (hart) |
| ----------- | -------------------- |
| **M4** | Preis-Amplitude ≥ 8 %, ≥ 2 Richtungswechsel, booking/markup-Amplitude s. oben |
| **M5** | Faktorübergang F1–F7 via `factor_rules`; Konflikt-Sweep &lt; BAU bei `consistency_score` |
| **M6** | CO₂ Tick 15 → messbare Buchungsreaktion; `income_index`-Trajektorie |
| **M7** | Segment-Divergenz `price_sensitive` vs. `business` ≥ 15 pp booking |
| **M8** | Sweep Transformations-Konflikt reproduzierbar über 3 Seeds |
| **M9** | Chat-Explorer: grounded, keine erfundenen Zahlen |

## Anhang B2 — Gesamtabnahme Emergenz (M12.4)

- [ ] M4–M9 Gates alle grün (s. Anhang B)
- [x] Ticketpreis steigt **und** fällt über 30 Ticks (M4)
- [x] `booking_rate` und `demand_level` gekoppelt (M4)
- [x] Faktorübergang via `factor_rules` ohne LLM (M5)
- [ ] Segment-Divergenz: `price_sensitive` vs. `business`
- [ ] Sweep Transformations-Konflikt reproduzierbar
- [x] CO₂ Tick 15: Effekt auf Population (M4-Run: booking −3 pp, Kosten/Markup-Reaktion)
- [ ] CIB: Konflikt &lt; BAU bei `consistency_score`
- [ ] Einkommen: F4.2 + fallender `income_index` → booking-Divergenz
- [ ] Agenten: Narrative in Profil-Grenzen, Reaktion auf `event_log`
- [ ] Chat-Explorer grounded, keine erfundenen Zahlen

## Anhang C — Verzeichnisstruktur (Ziel)

```
configs/
  simulation_config.json, properties.json, factors.json
  agents.json, agent_profiles.json, cib_frozen.json
  sweeps/
    co2_delayed.yaml, business_as_usual.yaml
    freiwillige_wende.yaml, transformation_conflict.yaml

src/
  property_engine.py, factor_dynamics.py, cib_rule_loader.py
  simulation_functions.py, population_sampler.py
  scenario_sweeps.py, scenario_consistency.py, state_explorer.py
  nodes/market_node.py, nodes/environment_node.py
  legacy/cib_extractor_node.py

docs/challenge4/
  projectplan.md, challenge4_report.md, cib_rationale.md
  agent_profiles.md, traceability_c1_c4.md, figures/

tests/
  test_market_feedback.py, test_factor_dynamics.py
  test_scenario_consistency.py, test_scenario_sweeps.py
  test_agent_profiling.py, test_income_dynamics.py, test_state_explorer.py
  (+ M0–M3 bestehende Tests)
```

## Anhang D — Scope-Abgrenzung

| Nicht | Stattdessen |
| ----- | ----------- |
| 6 LLM-Regulator-Agenten | `regulatory_influences` Properties |
| FEL / SimPy / A2A | LangGraph-Loop + `event_log` |
| CIB live generieren | Frozen + `factor_rules` |
| Emergenz aus Chat allein | Python-Kopplungen (M4–M6) |
