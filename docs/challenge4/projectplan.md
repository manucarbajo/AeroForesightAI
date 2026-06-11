# Project Plan, Challenge 4

C4 Aufgabenstellung:

- Dynamisierung der Einflussfaktoren (z. B. CO2-Steuer erst ab Tick N)
- Wechselwirkungen im System (Faktoren, Markt, Population, Agenten)
- Explorationsmöglichkeiten des Simulationsstands (z. B. Chat über Checkpoint/Protokoll)

## Simulationsziel

Ausgangslage und Grundannahmen definieren, dann mit einem agentischen Framework prüfen, ob plausible Szenarien entstehen: Marktreaktionen, Populationsverschiebungen, Policy-Effekte über diskrete Epochen (Ticks).

Quantitative Effekte laufen deterministisch über konfigurierbare Eigenschaften und Regeln. LLM-Agenten liefern nur qualitative Begründungen und Rollenentscheidungen. Die CIB aus C3 ist vergleichende Referenz, wird weder generiert noch im Lauf verändert.

Erfolgskriterium: nachvollziehbare Zeitreihen, statistische Populationsauswertungen, narrative Agentenbegründungen passend zu berechneten Aggregaten, skalierbare Laufzeit (Sweeps ohne LLM bis 10.000 Ticks).

## Ausgangslage

| Thema | Problem bisher | Endziel C4 | Status |
| ----- | -------------- | ---------- | ------ |
| CIB | 182 Zellen per LLM pro Runde | Fixe Referenzmatrix, nur vergleichend | erledigt (M0) |
| Agenten | Freie Zahlen, Halluzinationen | LLM nur qualitativ; Zahlen aus Python | teilweise erledigt (M2a/M3) |
| Konfiguration | Feste Parameter-Whitelist (`policy_schedule`), 3 Segmentklassen | Einheitliches Property-Modell, Szenarien ohne Codeänderung | teilweise erledigt (M2a) |
| Population | Neu-Sampling pro Tick, LLM für Shares | N persistente Individuen, Multi-Label, Regeln statt LLM | offen (M3) |
| Zeitmodell | Quartale, implizite Jahre | Tick = abstrakte Epoche; Iterationsanzahl, kein Kalender | erledigt (M1) |
| Variablen über Lauf | Unklar, teils LLM | Trajectories (`set`, `ramp`, `step_function`) + Tick-Regeln | teilweise erledigt (M2a) |
| Laufzeit | LLM in Berechnungsschleifen | Deterministischer Kern; Demo mit LLM, Sweeps ohne | teilweise erledigt |
| Orchestrierung | Redebedarf, sequentiell | Parallel, 1x je Agent/Tick | erledigt (M1c) |
| Pipeline | Getrennte Einstiege | Batch + Studio, ein CLI | erledigt (M1) |

## Architektur (Endziel)

### Zwei Ebenen von Eigenschaften

| Ebene | Was | Beispiele | Mechanismus | Status |
| ----- | --- | --------- | ----------- | ------ |
| System-Eigenschaften | Globale Größen pro Tick | `carbon_tax_level`, `ticket_price`, `total_population`, `oil_price_index` | Trajectory in Config (`set`, `ramp`, `step_function`) + `resolve_property()` | offen (M2); Zwischenlösung `policy_schedule` erledigt (M2a) |
| Individuen-Eigenschaften | Werte pro Person | `price_sensitive`, `awareness`, `wtp_eur`, `age` | Initial-Sampling + `apply_factor_shifts()` pro Tick | offen (M3) |

Keine festen Klassen oder Parameter-Whitelist im Code. Neue Eigenschaft = Eintrag in Config, nicht neuer Python-Parameter. **Aktuell:** 6er-Whitelist in `policy_schedule` / `scenario_parameters` (Zwischenlösung M2a).

### Tick-Pipeline

```
State(t)
  -> Orchestrator (+1)                         [erledigt]
  -> Agenten (je 1x, qualitativ)              [erledigt — ParallelRoundNode]
  -> resolve_system_properties(tick)           [teilweise — resolve_policy() statt property_engine]
  -> MarketNode (Preis, Metriken)              [erledigt — simulation_functions]
  -> apply_factor_shifts(individuals)          [offen]
  -> evaluate_booking(individuals)             [teilweise — run_population_sampling(), nicht persistent]
  -> aggregate + log                           [teilweise — segment_analysis, population_stats]
  -> State(t+1)
```

Innerhalb eines Ticks keine weitere Interaktion. `max_ticks` = Iterationsanzahl, nicht Jahre. Große Sprünge pro Tick werden geclippt (numerische Stabilität).

### Arbeitsteilung LLM vs. Python

| Komponente | Python | LLM | Status |
| ---------- | ------ | --- | ------ |
| System-Eigenschaften / Trajectories | ja | nein | teilweise (M2a: policy_schedule; M2 Endziel offen) |
| Buchungsentscheidungen | ja | nein | teilweise (Logit-Sampler, nicht persistent) |
| Populations-Shifts, Attribute | ja | nein | offen (Environment nutzt noch LLM für Shares) |
| Faktorübergänge (wenn regelbasiert) | ja | nein | teilweise (Agent proposed_state, keine Config-Regeln) |
| Preis, Steuer, SAF, Nachfrage | ja | nein | erledigt (M2a) |
| CIB | Referenz laden | nein | erledigt (M0) |
| Consumer/Provider/Regulator | Aggregat als Input | reasoning, actions, events, optional `proposed_state` | erledigt |
| Chat-Explorer | liest State | erfindet keine Zahlen | offen (M5) |
| Sweeps / Benchmarks | vollständig | `MockLLM` | offen (M4) |

### Property-Config (Endziel)

Eine Datei `configs/properties.json` (oder Abschnitt in `simulation_config.json`) definiert alle Eigenschaften:

```json
{
  "system_properties": [
    {
      "id": "carbon_tax_level",
      "type": "numeric",
      "unit": "EUR/t",
      "trajectory": {
        "baseline": 0,
        "rules": [{ "active_from_tick": 15, "effect": { "type": "set", "value": 85 } }]
      }
    },
    {
      "id": "bevoelkerungsentwicklung",
      "type": "integer",
      "trajectory": {
        "type": "step_function",
        "points": [{ "tick": 0, "value": 83000000 }, { "tick": 4, "value": 90000000 }]
      }
    }
  ],
  "individual_properties": [
    {
      "id": "price_sensitive",
      "type": "boolean",
      "prevalence": 0.4,
      "enabled": true
    },
    {
      "id": "environmental_awareness",
      "type": "distribution",
      "distribution": "beta",
      "alpha": 2,
      "beta": 5
    }
  ],
  "shift_rules": [
    { "when": { "factor": "F6", "state": "F6.2" }, "effect": { "property": "environmental_awareness", "delta": 0.02 } },
    { "when": { "system_property": "carbon_tax_level", "above": 50 }, "effect": { "property": "price_sensitivity", "delta": 0.05 } }
  ]
}
```

Kernfunktion: `resolve_property(prop_id, tick, state) -> float` in `src/property_engine.py`. **Status: offen (M2).**

`policy_schedule` wird migriert: gleiche Regeln als System-Properties, danach deprecaten. **Status: offen (M2).** Zwischenlösung `policy_schedule` + `scenario_parameters` ist erledigt (M2a).

### Individuen und Population

N = 1000 persistente Individuen (`state.population_individuals`), feste IDs über alle Ticks. **Status: offen (M3).**

Multi-Label: eine Person kann mehrere Properties tragen (`price_sensitive` + `business`). Keine disjunkte Partition. Alter als Querschnittsattribut, Kreuzauswertung Alter x Property. **Status: offen (M3).**

Verteilungen: lognormal (`wtp_eur`), beta (`environmental_awareness`). `price_sensitivity` abgeleitet, nicht vom LLM. **Status: teilweise** — lognormal im Sampler, beta vereinfacht als normal; kein `wtp_eur`-Modell.

Buchung (deterministisch):

```
book if ticket_price <= wtp_eur * (1 + green_premium * awareness)
     AND logit(base_utility - price_sensitivity * normalized_price - eco_penalty) > threshold
```

**Status: teilweise** — vereinfachte Logit-Formel in `run_population_sampling()`, kein WTP, nicht persistent.

SFO-Typologien (Leisure, Business, …) sind Beispiel-Instanz der `individual_properties`, nicht hard-codiert im Code. **Status: offen** — noch 3 Legacy-Segmente in `agents.json`.

### Faktor-Dynamik (F1 bis F7)

Faktoren in `factors.json` werden über drei Wege dynamisiert:

1. Trajectory auf verknüpfte System-Property (CO2 ab Tick N) — **teilweise erledigt** (über `policy_schedule`, nicht Property-Engine)
2. `shift_rules` in Config (F6.2 -> `awareness += δ`) — **offen (M3/M4)**
3. Schwellenregeln (`price_sensitivity > 0.8` -> Utility-Penalty) — **offen (M3)**

Regulator-LLM darf `proposed_state` vorschlagen; Übergang nur wenn Validierung/Regel es erlaubt. Zahlen kommen aus Python. **Status: teilweise erledigt.**

### CIB

Statische Referenz aus C3 (`configs/cib_frozen.json`). Kein LLM, kein Update im Lauf, keine Emergenz aus Agenten-Diskurs. `scenario_consistency.py` vergleicht Simulations-Szenarien mit Referenz. **Status: erledigt (M0).**

### Laufzeit

| Modus | Ticks | LLM | Status |
| ----- | ----- | --- | ------ |
| Demo | 30 bis 40 | ja | erledigt (`--mock-llm`, `--rounds`) |
| Sweep | variabel | nein | offen (M4) |
| Benchmark | bis 10.000 | nein | offen (M4) |

## Ist-Zustand vs. Endziel (Stand: Branch `m3/challenge4`)

| Thema | Ist | Endziel | Meilenstein | Status |
| ----- | --- | ------- | ----------- | ------ |
| CIB frozen, kein LLM-CIB | ja | ja | M0 | erledigt |
| Pipeline, Studio, Parallel | ja | ja | M1 | erledigt |
| `policy_schedule` Zwischenlösung (6 Parameter) | ja | migriert zu Property-Engine | M2a | erledigt |
| `scenario_parameters` + `resolve_policy()` | ja | Property-Engine | M2a | erledigt |
| `property_engine.py`, `step_function` | nein | ja | M2 | offen |
| `properties.json` | nein | ja | M2 | offen |
| Preis/Steuer/Nachfrage deterministisch (kein LLM) | ja | ja | M2a | erledigt |
| Preis aus Properties/Regeln (Endziel) | nein | ja | M2 | offen |
| `population_sampler` (Logit, Segmente) | ja | persistente Individuen | M3 | teilweise erledigt |
| Persistente Individuen | nein | ja | M3 | offen |
| Property-Modell in `agents.json` | nein (3 Segmente) | ja | M3 | offen |
| Environment ohne LLM | nein (LLM-Shifts) | ja | M3 | offen |
| `apply_factor_shifts()` | nein | ja | M3 | offen |
| Englische Prompts, keine `impact_assessment` | ja | ja | M1c | erledigt |
| Faktor-Regeln in Config | nein | ja | M4 | offen |
| Sweeps ohne LLM | nein | ja | M4 | offen |
| CIB-Vergleichsdoku | nein | ja | M2b | offen |
| Report, Chat, Figures | nein | ja | M5 | offen |
| Tests mit MockLLM (Unit/E2E) | ja | ja | M1/M5 | teilweise erledigt |

## Verzeichnisstruktur (Endziel vs. Ist)

```
configs/
  simulation_config.json    clock, llm, seed, policy_schedule, scenario_parameters  [erledigt]
  properties.json             system + individual properties, shift_rules           [offen]
  agents.json                 Agent-Rollen (noch 3 Segmente)                        [teilweise]
  factors.json                F1 bis F7                                             [erledigt]
  cib_frozen.json             Referenzmatrix 14×14                                  [erledigt]
  sweeps/
    co2_delayed.yaml                                                                [offen]

src/
  property_engine.py          resolve_property(), Trajectory-Typen                  [offen]
  simulation_functions.py       resolve_policy(), compute_ticket_price(), compute_demand()  [erledigt — M2a]
  population_sampler.py         run_population_sampling() (vereinfacht)               [teilweise]
  scenario_sweeps.py                                                                  [offen]
  state_explorer.py                                                                   [offen]
  simulation_runner.py          Parallel Default, enable_cib=frozen                   [erledigt]
  run_simulation.py             --studio, --redebedarf, --mock-llm                    [erledigt]
                                --deterministic-only, --sweep                         [offen]
  config_loader.py              load_cib_frozen(), build_initial_state()              [erledigt]
  output_writer.py              outputs/<run_id>/, cib_matrix, segment_analysis     [erledigt]
                                timeseries/*.csv                                      [offen]
  models/
    property_models.py                                                                [offen]
    population_models.py      ScenarioParameter, Segmente (kein Individual)           [teilweise]
  nodes/
    parallel_round_node.py                                                            [erledigt]
    environment_node.py       LLM-Shifts + population_sampler                       [teilweise]
    market_node.py            deterministisch                                       [erledigt]
    agent_node.py             englische Prompts, market_metrics                     [erledigt]

docs/challenge4/
  projectplan.md                                                                      [erledigt]
  calibration_agents.md       (in docs/archive/challenge3/)                           [offen — M5]
  cib_rationale.md                                                                    [offen — M2b]
  challenge4_report.md                                                                [offen — M5]

tests/
  test_policy_schedule.py     CO2 ab Tick 15, resolve_policy, compute_*               [erledigt — M2a]
  test_parallel_round.py                                                              [erledigt — M1c]
  test_property_engine.py                                                             [offen]
  test_population_sampler.py                                                          [offen]
  test_scenario_sweeps.py                                                             [offen]
```

Outputs pro Lauf: `outputs/<run_id>/` mit `cib_matrix.json` (Referenzkopie), `segment_analysis.json`, `protocol.json/md`, `price_history.json`. **Erledigt.**

Noch offen: `timeseries/properties.csv`, `population.csv`, `factors.csv`, Checkpoints mit `population_individuals`.

## Meilensteine

```
M0 (erledigt) -> M1 (erledigt) -> M2a (erledigt) -> M2 (offen) -> M3 (teilweise) -> M4 (offen) -> M5 (offen)
                                                      |
                                                      +-> M2b (offen, parallel zu M2/M4)
```

### M0: CIB als Referenz — erledigt

| Aufgabe | Status |
| ------- | ------ |
| `configs/cib_frozen.json` laden (vollständige 14×14-Matrix) | erledigt |
| Kein `CIBExtractorNode` im Tick-Loop (`enable_cib` lädt nur Frozen-Matrix) | erledigt |
| Kein `impact_assessment` in Agent-Prompts | erledigt |
| Export `outputs/<run_id>/cib_matrix.json` als unveränderte Referenzkopie | erledigt |
| Szenarioableitung vergleichend über `scenario_consistency.py` | erledigt |

### M1: Fundament — erledigt

| Aufgabe | Status |
| ------- | ------ |
| Tick-Modell (`current_tick` / `max_ticks`, `tick_unit: tick`) | erledigt |
| Eine Pipeline, `outputs/<run_id>/` | erledigt |
| `ParallelRoundNode` Default, `--redebedarf` Legacy | erledigt |
| LangGraph Studio, `run_simulation.py --studio` | erledigt |
| `environment_node_c2.py` entfernt | erledigt |
| README aktualisiert | erledigt |

### M2a: Policy-Schedule Zwischenlösung — erledigt

Ziel: deterministischer Marktkern mit zeitgesteuerter Dynamisierung (CO2 ab Tick N etc.), ohne LLM für Zahlen.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `PolicyEntry` + `policy_schedule`-Liste in Config | `state_models.py`, `simulation_config.json` | erledigt |
| `scenario_parameters` mit Defaults und `runtime_parameter_map()` | `state_models.py`, `population_models.py` | erledigt |
| `resolve_policy(tick, schedule)` | `simulation_functions.py` | erledigt |
| `compute_ticket_price()`, `compute_demand()` | `simulation_functions.py` | erledigt |
| `compute_market_metrics()` für Agent-Prompts | `simulation_functions.py` | erledigt |
| `oil_price_index` in Preisformel | `simulation_functions.py` | erledigt |
| `MarketNode` nutzt Funktionen, kein Text-Parsing | `market_node.py` | erledigt |
| CO2-Demo: Tick 1/15/30 in Config + Tests | `simulation_config.json`, `test_policy_schedule.py` | erledigt |
| Validator für 6 Parameter-Whitelist | `validation.py` | erledigt |
| Agenten bekommen `market_metrics` als Kontext, produzieren keine Zahlen | `agent_node.py`, Prompts | erledigt |

Ergebnis: deterministische Preis/Steuer/Nachfrage-Berechnung, Policy-Shocks ab Tick N. Bleibt als Basis bis M2 (Property-Engine).

### M2: Property-Engine und System-Eigenschaften — offen

Ziel: alle globalen Variablen über Config steuerbar; `policy_schedule` ablösen.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `SystemProperty`, `Trajectory`, `ShiftRule` Modelle | `property_models.py` | offen |
| `resolve_property(id, tick, state)` | `property_engine.py` | offen |
| Trajectory-Typen: `baseline`, `set`, `ramp`, `step_function` | `property_engine.py` | offen |
| `configs/properties.json` mit System-Properties | Config | offen |
| Migration: `policy_schedule` -> `properties.json` | `config_loader.py`, Tests | offen |
| `simulation_functions.py` liest Werte aus `resolve_property()` | `simulation_functions.py` | offen |
| `derive_ticket_price()` aus System-Properties, nicht feste Heuristik | `simulation_functions.py` | offen |
| Validator: beliebige Property-IDs, keine 6er-Whitelist | `validation.py` | offen |
| `timeseries/properties.csv` pro Tick | `output_writer.py` | offen |
| Tests: step_function, CO2 ab Tick 15, Ramp SAF | `test_property_engine.py` | offen |
| `policy_schedule` deprecaten (Kompatibilitäts-Layer optional) | `config_loader.py` | offen |

Ergebnis: `property_engine.py`, `properties.json`, Marktmetriken vollständig property-gesteuert.

### M2b: CIB-Vergleichsdokumentation — offen

Ziel: Referenz und Vergleichsmethodik dokumentieren.

| Aufgabe | Status |
| ------- | ------ |
| `docs/challenge4/cib_rationale.md` | offen |
| Abgleich Faktorverläufe / `scenarios.json` mit Referenz-CIB | offen |
| `CIBExtractorNode` nach `src/legacy/` | offen |

Kein `cib_engine`, kein LLM, kein Laufzeit-Update der Matrix.

### M3: Individuen-Eigenschaften und Population — teilweise erledigt

Ziel: Multi-Label Properties, persistente Individuen, Buchung und Shifts in Python; Environment ohne LLM.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `Individual` Modell (`id`, `age`, `properties`, `wtp_eur`, `awareness`, `price_sensitivity`) | `population_models.py` | offen |
| `individual_properties` in `properties.json` | Config | offen |
| `initialize_population(seed)` einmalig | `population_sampler.py` | offen |
| `evaluate_booking()` mit WTP, persistent | `population_sampler.py` | offen |
| `run_population_sampling()` Logit-Buchung pro Tick (Segmente) | `population_sampler.py` | erledigt |
| `apply_factor_shifts()` aus `shift_rules` + Faktoren | `population_sampler.py` | offen |
| Schwellenregeln (arithmetisch) | `population_sampler.py` | offen |
| lognormal in `_sample_distribution()` | `population_sampler.py` | erledigt |
| beta in `_sample_distribution()` | `population_sampler.py` | offen (Fallback auf normal) |
| `state.population_individuals` über Ticks, Checkpoints | `state_models.py`, `environment_node.py` | offen |
| `state.population_stats` pro Tick (Aggregat) | `state_models.py`, `environment_node.py` | erledigt |
| Environment: LLM-Pfad für Shares entfernen, Regeln Default | `environment_node.py` | offen |
| Consumer-Prompt: englisch, Aggregat-Kontext | `consumer.md`, `agent_node.py` | erledigt |
| Consumer-Prompt: nur Aggregat-Statistik, keine freien Zahlen (strikt) | `agent_node.py`, `consumer.md` | teilweise erledigt |
| `segment_analysis.json` Export | `output_writer.py` | erledigt |
| `population.csv`: Alter x Property, Quantile, booking_rate | `output_writer.py` | offen |
| Migration: 3 Legacy-Segmente -> Properties | `agents.json` | offen |
| Tests: Multi-Label, Persistenz, Environment ohne LLM | `test_population_sampler.py` | offen |
| `ParallelRoundNode` + Tests | `parallel_round_node.py`, `test_parallel_round.py` | erledigt |

Ergebnis: persistente Population, regelbasierte Shifts, Export für M4/M5 — **noch nicht vollständig.**

### M4: Faktor-Dynamik, Sweeps, Skalierung — offen

Ziel: Wechselwirkungen sichtbar; lange Läufe ohne LLM; Emergenz-Demos.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `shift_rules` für F1 bis F7 vollständig in Config | `properties.json` | offen |
| Faktorzustand -> System-Property Kopplung dokumentiert | `calibration_agents.md` | offen |
| `scenario_sweeps.py` mit `MockLLM` | `scenario_sweeps.py` | offen |
| CLI `--deterministic-only`, `--sweep` | `run_simulation.py` | offen |
| Sweep `co2_delayed.yaml` (CO2 ab Tick 15) | `configs/sweeps/` | offen |
| Sweeps: Elastizität, F6-Awareness, Property-Prevalence | Config | offen |
| `sweep_summary.json` mit booking_rate-Delta je Property | `scenario_sweeps.py` | offen |
| Benchmark-Lauf 10.000 Ticks ohne LLM | Tests/Doku | offen |
| Szenarien gegen CIB-Referenz (vergleichend) | `scenario_consistency.py` | teilweise erledigt (Code vorhanden, Sweep-Integration offen) |

### M5: Abgabe — offen

Ziel: Report, Präsentation, Chat; Architektur und Grenzen.

| Aufgabe | Status |
| ------- | ------ |
| `state_explorer.py` (grounded Chat) | offen |
| `challenge4_report.md`: Property-Engine, zwei Ebenen, LLM-Grenze, Epochenmodell, CIB-Vergleich, Grenzen agentisches Framework | offen |
| `calibration_agents.md` finalisieren | offen |
| Figures: booking_rate je Property, Alter x Property, CO2-Vor/Nach Tick 15 | offen |
| Präsentation: Architektur, Sweep-Demo, CIB-Referenz, Verteilungen | offen |
| Tests ohne Ollama (`MockLLM`) in Unit/E2E | teilweise erledigt |
| Doku archivieren | teilweise erledigt (`docs/archive/`) |

### Erledigte Teile (nicht zurückbauen)

| Teil | Meilenstein | Status |
| ---- | ----------- | ------ |
| CIB frozen (14×14), kein `impact_assessment`, kein CIB-LLM pro Tick | M0 | erledigt |
| Tick-Pipeline, `outputs/<run_id>/`, Studio, `--mock-llm` | M1 | erledigt |
| `ParallelRoundNode`, `--redebedarf` Legacy, englische Prompts | M1c | erledigt |
| `policy_schedule` + `scenario_parameters` + `simulation_functions` | M2a | erledigt |
| `population_sampler` (Logit, segmentweise, `population_stats`) | M3 (Teil) | erledigt |

Diese bleiben als Basis, bis M2 die Property-Engine liefert.

## Priorität bei Zeitdruck

1. **M2 (offen):** `property_engine.py` + Migration `policy_schedule` → `properties.json`
2. **M3 (offen):** Environment ohne LLM + persistente Individuen + `apply_factor_shifts`
3. **M4 (offen):** Sweep CO2 ab Tick 15 ohne LLM (Hauptdemo)
4. **M2b + M5 (offen):** Doku und Report

## Präsentation (Gliederung)

1. Simulationsziel und Architektur (Property-Engine, LLM-Grenze)
2. Zwei Ebenen: System-Properties und Individuen-Properties
3. Epochenmodell (Tick, Stabilität, keine Kalenderjahre)
4. Emergenz-Demo: Sweep CO2 ab Tick 15, booking_rate je Property
5. CIB-Referenz und Szenario-Vergleich
6. Verteilungen, Alter x Property, Zeitreihen
7. Grenzen und Ausblick
