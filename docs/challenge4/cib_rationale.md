# CIB-Methodik — Challenge 4 (M5 / M11)

## Referenz vs. Lauf

- **Referenz:** `configs/cib_frozen.json` (14×14 Deskriptoren, statisch)
- **Lauf:** Keine neue CIB pro Tick; stattdessen `factor_rules` + `timeseries/factors.csv`
- **Score:** `scenario_consistency.py` bewertet Endzustand F1–F7 pro Lauf/Sweep (M8)

Challenge 2/3 nutzten `CIBExtractorNode` (LLM/heuristisch aus Event-Log). In C4 liegt der Extractor unter **`src/legacy/`** — nicht Teil der Tick-Pipeline.

## Mapping CIB → `factor_rules`

| CIB-Intuition | Regel-ID | Bedingung | Effekt |
| --- | --- | --- | --- |
| Niedrige Buchung → Substitution | `f1_low_booking_substitution` | `booking_rate < 0.45` | F1 → F1.2 |
| Hohe Buchung → Boom | `f1_strong_demand` | `booking_rate > 0.68` | F1 → F1.1 |
| Hohe CO₂ → strenge Regulierung | `f2_high_carbon_policy` | `carbon_tax_level > 100` | F2 → F2.2 |
| Moderate CO₂ | `f2_moderate_policy` | `carbon_tax_level < 80` | F2 → F2.1 |
| SAF-Mandat → Tech-Durchbruch | `f3_saf_mandate_breakthrough` | `saf_mandate_share ≥ 0.05` | F3 → F3.2 |
| Geringes SAF | `f3_incremental_tech` | `saf_mandate_share < 0.03` | F3 → F3.1 |
| Hoher Kostendruck → Rezession | `f4_high_cost_pressure` | `cost_pressure > 135` | F4 → F4.2 |
| Stabiles Wachstum | `f4_stable_growth` | `cost_pressure < 115` | F4 → F4.1 |
| Flight Shaming → Alternativen | `f5_alternatives_flight_shaming` | F6 = F6.2 | F5 → F5.2 |
| Keine Alternative | `f5_no_alternative` | F6 = F6.1 | F5 → F5.1 |
| Hohe CO₂ → Flight Shaming | `f6_flight_shaming_high_tax` | `carbon_tax_level > 80` | F6 → F6.2 |
| Akzeptiertes Fliegen | `f6_accepted_flying` | `carbon_tax_level < 60` | F6 → F6.1 |
| Ölpreis-Stress | `f7_oil_stress` | `oil_price_index > 1.25` | F7 → F7.2 |
| Offene Märkte | `f7_open_markets` | `oil_price_index ≤ 1.1` | F7 → F7.1 |

Kanten mit starker negativer CIB-Wirkung werden als **bedingte Übergänge** modelliert, nicht als LLM-Sprünge. Vollständige Regeln: `configs/properties.json` → `factor_rules`.

## Arbeitsteilung

| Komponente | Python | LLM |
| --- | --- | --- |
| Faktorzustand | `apply_factor_rules()` | narrativ (kein freier Sprung) |
| LLM-Vorschlag | nur via `validate_factor_proposals()` | Regulator: F2, F6 |
| End-Score | `scenario_consistency` vs. frozen CIB | — |

## Consistency-Score (M8)

Nach Sweep-Läufen: `outputs/sweeps/scenario_scores.json`. Erwartung laut Projektplan: **Transformations-Konflikt** erzielt niedrigeren `consistency_score` als **Business as Usual** (weniger konsistente Faktor-Kombination relativ zur Referenz-CIB).

## Tests

- `tests/test_factor_dynamics.py` — Regeln, 30-Tick-Übergänge ohne LLM
- `tests/test_scenario_consistency.py` — Score-Berechnung
- `tests/test_scenario_sweeps.py` — Sweep-Overrides und Endzustände
