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

| Thema | Problem bisher | Endziel C4 |
| ----- | -------------- | ---------- |
| CIB | 182 Zellen per LLM pro Runde | Fixe Referenzmatrix, nur vergleichend |
| Agenten | Freie Zahlen, Halluzinationen | LLM nur qualitativ; Zahlen aus Python |
| Konfiguration | Feste Parameter-Whitelist (`policy_schedule`), 3 Segmentklassen | Einheitliches Property-Modell, Szenarien ohne Codeänderung |
| Population | Neu-Sampling pro Tick, LLM für Shares | N persistente Individuen, Multi-Label, Regeln statt LLM |
| Zeitmodell | Quartale, implizite Jahre | Tick = abstrakte Epoche; Iterationsanzahl, kein Kalender |
| Variablen über Lauf | Unklar, teils LLM | Trajectories (`set`, `ramp`, `step_function`) + Tick-Regeln |
| Laufzeit | LLM in Berechnungsschleifen | Deterministischer Kern; Demo mit LLM, Sweeps ohne |
| Orchestrierung | Redebedarf, sequentiell | Parallel, 1x je Agent/Tick (erledigt, M1c) |
| Pipeline | Getrennte Einstiege | Batch + Studio, ein CLI (erledigt, M1) |

## Architektur (Endziel)

### Zwei Ebenen von Eigenschaften

| Ebene | Was | Beispiele | Mechanismus |
| ----- | --- | --------- | ----------- |
| System-Eigenschaften | Globale Größen pro Tick | `carbon_tax_level`, `ticket_price`, `total_population`, `oil_price_index` | Trajectory in Config (`set`, `ramp`, `step_function`) + `resolve_property()` |
| Individuen-Eigenschaften | Werte pro Person | `price_sensitive`, `awareness`, `wtp_eur`, `age` | Initial-Sampling + `apply_factor_shifts()` pro Tick |

Keine festen Klassen oder Parameter-Whitelist im Code. Neue Eigenschaft = Eintrag in Config, nicht neuer Python-Parameter.

### Tick-Pipeline

```
State(t)
  -> Orchestrator (+1)
  -> Agenten (je 1x, qualitativ)
  -> resolve_system_properties(tick)      # Trajectories + Regeln
  -> MarketNode (Preis, Metriken)
  -> apply_factor_shifts(individuals)     # Individuen-Regeln
  -> evaluate_booking(individuals)        # Buchung
  -> aggregate + log
  -> State(t+1)
```

Innerhalb eines Ticks keine weitere Interaktion. `max_ticks` = Iterationsanzahl, nicht Jahre. Große Sprünge pro Tick werden geclippt (numerische Stabilität).

### Arbeitsteilung LLM vs. Python

| Komponente | Python | LLM |
| ---------- | ------ | --- |
| System-Eigenschaften / Trajectories | ja | nein |
| Buchungsentscheidungen | ja | nein |
| Populations-Shifts, Attribute | ja | nein |
| Faktorübergänge (wenn regelbasiert) | ja | nein |
| Preis, Steuer, SAF, Nachfrage | ja | nein |
| CIB | Referenz laden | nein |
| Consumer/Provider/Regulator | Aggregat als Input | reasoning, actions, events, optional `proposed_state` |
| Chat-Explorer | liest State | erfindet keine Zahlen |
| Sweeps / Benchmarks | vollständig | `MockLLM` |

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

Kernfunktion: `resolve_property(prop_id, tick, state) -> float` in `src/property_engine.py`.

`policy_schedule` wird migriert: gleiche Regeln als System-Properties, danach deprecaten.

### Individuen und Population

N = 1000 persistente Individuen (`state.population_individuals`), feste IDs über alle Ticks.

Multi-Label: eine Person kann mehrere Properties tragen (`price_sensitive` + `business`). Keine disjunkte Partition. Alter als Querschnittsattribut, Kreuzauswertung Alter x Property.

Verteilungen: lognormal (`wtp_eur`), beta (`environmental_awareness`). `price_sensitivity` abgeleitet, nicht vom LLM.

Buchung (deterministisch):

```
book if ticket_price <= wtp_eur * (1 + green_premium * awareness)
     AND logit(base_utility - price_sensitivity * normalized_price - eco_penalty) > threshold
```

SFO-Typologien (Leisure, Business, …) sind Beispiel-Instanz der `individual_properties`, nicht hard-codiert im Code.

### Faktor-Dynamik (F1 bis F7)

Faktoren in `factors.json` werden über drei Wege dynamisiert:

1. Trajectory auf verknüpfte System-Property (CO2 ab Tick N)
2. `shift_rules` in Config (F6.2 -> `awareness += δ`)
3. Schwellenregeln (`price_sensitivity > 0.8` -> Utility-Penalty)

Regulator-LLM darf `proposed_state` vorschlagen; Übergang nur wenn Validierung/Regel es erlaubt. Zahlen kommen aus Python.

### CIB

Statische Referenz aus C3 (`configs/cib_frozen.json`). Kein LLM, kein Update im Lauf, keine Emergenz aus Agenten-Diskurs. `scenario_consistency.py` vergleicht Simulations-Szenarien mit Referenz.

### Laufzeit

| Modus | Ticks | LLM |
| ----- | ----- | --- |
| Demo | 30 bis 40 | ja |
| Sweep | variabel | nein |
| Benchmark | bis 10.000 | nein |

## Ist-Zustand vs. Endziel (Jun 2026)

| Thema | Ist | Endziel | Meilenstein |
| ----- | --- | ------- | ----------- |
| CIB frozen, kein LLM-CIB | ja | ja | M0 (erledigt) |
| Pipeline, Studio, Parallel | ja | ja | M1 (erledigt) |
| `policy_schedule` (6 Parameter, Whitelist) | ja | migriert zu Property-Engine | M2 |
| `property_engine.py`, `step_function` | nein | ja | M2 |
| `properties.json` | nein | ja | M2 |
| Preis aus Properties/Regeln | teilweise | ja | M2 |
| Persistente Individuen | nein | ja | M3 |
| Property-Modell in `agents.json` | nein (3 Segmente) | ja | M3 |
| Environment ohne LLM | nein (LLM-Shifts) | ja | M3 |
| `apply_factor_shifts()` | nein | ja | M3 |
| Faktor-Regeln in Config | nein | ja | M4 |
| Sweeps ohne LLM | nein | ja | M4 |
| CIB-Vergleichsdoku | nein | ja | M2b |
| Report, Chat, Figures | teilweise | ja | M5 |

## Verzeichnisstruktur (Endziel)

```
configs/
  simulation_config.json    clock, llm, seed
  properties.json             system + individual properties, shift_rules, trajectories
  agents.json                 Agent-Rollen, Verweis auf individual_properties
  factors.json                F1 bis F7
  cib_frozen.json             Referenzmatrix
  sweeps/
    co2_delayed.yaml

src/
  property_engine.py          resolve_property(), Trajectory-Typen, shift_rules
  simulation_functions.py       derive_ticket_price(), compute_market_metrics() aus Properties
  population_sampler.py       initialize, evaluate_booking, apply_factor_shifts, aggregate
  scenario_sweeps.py
  state_explorer.py
  simulation_runner.py
  run_simulation.py             --studio, --redebedarf, --deterministic-only, --sweep
  config_loader.py
  output_writer.py
  models/
    property_models.py        SystemProperty, IndividualProperty, Trajectory, ShiftRule
    population_models.py      Individual
  nodes/
    parallel_round_node.py
    environment_node.py       regelbasiert, kein LLM Default
    market_node.py
    agent_node.py

docs/challenge4/
  projectplan.md
  calibration_agents.md
  cib_rationale.md
  challenge4_report.md

tests/
  test_property_engine.py
  test_population_sampler.py
  test_parallel_round.py
  test_scenario_sweeps.py
```

Outputs pro Lauf: `outputs/<run_id>/` mit `timeseries/properties.csv`, `population.csv`, `factors.csv`, `cib_matrix.json` (Referenzkopie), Checkpoints mit `population_individuals`.

## Meilensteine

```
M0 (erledigt) -> M1 (erledigt) -> M2 -> M3 -> M4 -> M5
                                    |
                                    +-> M2b (parallel zu M2/M4)
```

### M0: CIB als Referenz (erledigt)

- `configs/cib_frozen.json` laden, kein `CIBExtractorNode` im Loop
- Kein `impact_assessment`, kein LLM für CIB-Zellen
- Export `cib_matrix.json` als unveränderte Referenzkopie
- Szenarioableitung vergleichend über `scenario_consistency.py`

### M1: Fundament (erledigt)

- Tick-Modell (`tick_unit: tick`), eine Pipeline, `outputs/<run_id>/`
- `ParallelRoundNode` Default, `--redebedarf` Legacy
- LangGraph Studio, `run_simulation.py --studio`
- Zwischenlösung `policy_schedule` in `simulation_functions.py` (wird in M2 abgelöst)

### M2: Property-Engine und System-Eigenschaften

Ziel: alle globalen Variablen über Config steuerbar; Variablen über den Simulationslauf ohne Codeänderung; `policy_schedule` ablösen.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `SystemProperty`, `Trajectory`, `ShiftRule` Modelle | `property_models.py` | offen |
| `resolve_property(id, tick, state)` | `property_engine.py` | offen |
| Trajectory-Typen: `baseline`, `set`, `ramp`, `step_function` | `property_engine.py` | offen (nur set/ramp in policy_schedule) |
| `configs/properties.json` mit System-Properties | Config | offen |
| Migration: `policy_schedule` -> `properties.json` | `config_loader.py`, Tests | offen |
| `simulation_functions.py` liest Werte aus `resolve_property()` | `simulation_functions.py` | offen |
| `derive_ticket_price()` aus System-Properties, nicht feste Heuristik | `simulation_functions.py` | offen |
| `oil_price_index` in Preisformel | `simulation_functions.py` | offen |
| Validator: beliebige Property-IDs, keine 6er-Whitelist | `validation.py` | offen |
| `timeseries/properties.csv` pro Tick | `output_writer.py` | offen |
| Tests: step_function, CO2 ab Tick 15, Ramp SAF | `test_property_engine.py` | offen |
| `policy_schedule` deprecaten (Kompatibilitäts-Layer optional) | `config_loader.py` | offen |

Feedback-Bezug: keine hard-codierten Parameter; Variable über Lauf führen; Preis/Steuer berechnet, nicht LLM; Dynamisierung ab Tick N.

Ergebnis: `property_engine.py`, `properties.json`, Marktmetriken vollständig property-gesteuert.

### M2b: CIB-Vergleichsdokumentation

Ziel: Referenz und Vergleichsmethodik dokumentieren.

| Aufgabe | Status |
| ------- | ------ |
| `docs/challenge4/cib_rationale.md` | offen |
| Abgleich Faktorverläufe / `scenarios.json` mit Referenz-CIB | offen |
| `CIBExtractorNode` nach `src/legacy/` | offen |

Kein `cib_engine`, kein LLM, kein Laufzeit-Update der Matrix.

### M3: Individuen-Eigenschaften und Population

Ziel: Multi-Label Properties, persistente Individuen, Buchung und Shifts in Python; Environment ohne LLM.

| Aufgabe | Datei | Status |
| ------- | ----- | ------ |
| `Individual` Modell (`id`, `age`, `properties`, `wtp_eur`, `awareness`, `price_sensitivity`) | `population_models.py` | offen |
| `individual_properties` in `properties.json` | Config | offen |
| `initialize_population(seed)` einmalig | `population_sampler.py` | offen |
| `evaluate_booking()` mit WTP, persistent | `population_sampler.py` | offen |
| `apply_factor_shifts()` aus `shift_rules` + Faktoren | `population_sampler.py` | offen |
| Schwellenregeln (arithmetisch) | `population_sampler.py` | offen |
| lognormal + beta in `_sample_distribution()` | `population_sampler.py` | offen |
| `state.population_individuals` über Ticks, Checkpoints | `state_models.py`, `environment_node.py` | offen |
| Environment: LLM-Pfad für Shares entfernen, Regeln Default | `environment_node.py` | offen |
| Consumer-Prompt: nur Aggregat-Statistik, keine freien Zahlen | `agent_node.py`, `consumer.md` | offen |
| `population.csv`: Alter x Property, Quantile, booking_rate | `output_writer.py` | offen |
| Migration: 3 Legacy-Segmente -> Properties | `agents.json` | offen |
| Tests: Multi-Label, Persistenz, Environment ohne LLM | `test_population_sampler.py` | offen |

Feedback-Bezug: keine Segmentklassen; Multi-Label + Alter; Population-Shifts arithmetisch; Buchung deterministisch; LLM nur Narrativ.

Ergebnis: persistente Population, regelbasierte Shifts, Export für M4/M5.

### M4: Faktor-Dynamik, Sweeps, Skalierung

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
| Szenarien gegen CIB-Referenz (vergleichend) | `scenario_consistency.py` | offen |

Feedback-Bezug: Dynamisierung Einflussfaktoren; Laufzeit; numerische Stabilität über viele Ticks; kein LLM in Schleife.

### M5: Abgabe

Ziel: Report, Präsentation, Chat; Architektur und Grenzen.

| Aufgabe | Status |
| ------- | ------ |
| `state_explorer.py` (grounded Chat) | offen |
| `challenge4_report.md`: Property-Engine, zwei Ebenen, LLM-Grenze, Epochenmodell, CIB-Vergleich, Grenzen agentisches Framework | offen |
| `calibration_agents.md` finalisieren | offen |
| Figures: booking_rate je Property, Alter x Property, CO2-Vor/Nach Tick 15 | offen |
| Präsentation: Architektur, Sweep-Demo, CIB-Referenz, Verteilungen | offen |
| Tests ohne Ollama (`MockLLM`) | offen |
| Doku archivieren | offen |

### Erledigte Teile (nicht zurückbauen)

| Teil | Meilenstein |
| ---- | ----------- |
| CIB frozen, kein impact_assessment | M0 |
| Tick-Pipeline, outputs/<run_id>/, Studio | M1 |
| ParallelRoundNode, englische Prompts | M1c |
| policy_schedule + simulation_functions (Zwischenlösung) | M1/M2a |

Diese bleiben als Basis, bis M2 die Property-Engine liefert.

## Priorität bei Zeitdruck

1. M2: `property_engine.py` + Migration `policy_schedule` (sonst bleibt alles schema-hardcoded)
2. M3: Environment ohne LLM + persistente Individuen + `apply_factor_shifts`
3. M4: Sweep CO2 ab Tick 15 ohne LLM (Hauptdemo)
4. M2b + M5: Doku und Report

## Präsentation (Gliederung)

1. Simulationsziel und Architektur (Property-Engine, LLM-Grenze)
2. Zwei Ebenen: System-Properties und Individuen-Properties
3. Epochenmodell (Tick, Stabilität, keine Kalenderjahre)
4. Emergenz-Demo: Sweep CO2 ab Tick 15, booking_rate je Property
5. CIB-Referenz und Szenario-Vergleich
6. Verteilungen, Alter x Property, Zeitreihen
7. Grenzen und Ausblick
