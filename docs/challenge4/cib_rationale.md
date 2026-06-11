# CIB-Methodik — Challenge 4 (M5)

## Referenz vs. Lauf

- **Referenz:** `configs/cib_frozen.json` (14×14 Deskriptoren, statisch)
- **Lauf:** Keine neue CIB pro Tick; stattdessen `factor_rules` + `timeseries/factors.csv`
- **Score:** `scenario_consistency.py` bewertet Endzustand F1–F7 pro Lauf/Sweep (M8)

## Mapping CIB → `factor_rules`

| CIB-Intuition | Beispiel-Regel in `properties.json` |
| ------------- | ------------------------------------- |
| Hohe CO₂-Bepreisung → strengere Regulierung | `f2_high_carbon_policy` → F2.2 |
| Flight Shaming / hohe CO₂ → F6.2 | `f6_flight_shaming_high_tax` |
| F6.2 → Schienenalternative | `f5_alternatives_flight_shaming` → F5.2 |
| SAF-Mandat → Technologie-Durchbruch | `f3_saf_mandate_breakthrough` → F3.2 |
| Niedrige Buchung → Nachfrage-Stagnation | `f1_low_booking_substitution` → F1.2 |

Kanten mit starker negativer CIB-Wirkung werden als **bedingte Übergänge** modelliert, nicht als LLM-Sprünge.

## Arbeitsteilung

| Komponente | Python | LLM |
| ---------- | ------ | --- |
| Faktorzustand | `apply_factor_rules()` | narrativ (kein freier Sprung) |
| LLM-Vorschlag | nur via `validate_factor_proposals()` (Regulator: F2, F6) | vorschlagen |
