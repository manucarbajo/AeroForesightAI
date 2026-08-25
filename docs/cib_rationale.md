# CIB-Methodik

> Anwendernahe Fassung im Dashboard unter «Dokumentation → CIB-Konsistenzprüfung».

## Referenz vs. Lauf

- **Referenz:** `configs/cib_frozen.json` (14×14 Deskriptoren, eingefroren)
- **Lauf:** Keine neue CIB pro Tick; stattdessen `factor_rules` + `timeseries/factors.csv`
- **Score:** `scenario_consistency.py` bewertet Endzustand F1–F7 pro Lauf/Sweep (M8)

Eine frühere Version nutzte `CIBExtractorNode` (LLM/heuristisch aus Event-Log). Der
Extractor liegt jetzt unter **`src/legacy/`** — nicht Teil der Tick-Pipeline.

---

## CIB-Kante ↔ `factor_rule` Mapping

Jede `factor_rule` in `configs/properties.json` ist aus einer oder mehreren CIB-Kanten
motiviert. Die Tabelle zeigt: Welche CIB-Einflüsse begründen welche Zustandsübergangs-Regel?

### Metrik-getriebene Regeln (Systemkennzahlen → Faktorzustand)

Diese Regeln übersetzen kontinuierliche Systemkennzahlen in diskrete Faktorzustände.
Die CIB-Kante gibt den qualitativen Zusammenhang an, den die Schwellenwert-Logik quantifiziert.

| Regel-ID | Beobachtete CIB-Kanten (Einfluss) | Schwellenwert | Effekt | Begründung |
|---|---|---|---|---|
| `f1_low_booking_substitution` | F5.2→F1.2 (+2), F4.2→F1.2 (-3*) | `booking_rate < 0.25` | F1 → F1.2 | Niedrige Buchungsrate signalisiert Substitution durch Alternativen (F5) oder Rezession (F4) |
| `f1_strong_demand` | F6.1→F1.1 (+3), F4.1→F1.1 (+1) | `booking_rate > 0.35` | F1 → F1.1 | Hohe Buchung = gesellschaftliche Akzeptanz (F6.1) + Wirtschaftskraft (F4.1) |
| `f2_high_carbon_policy` | F1.2→F2.2 (-3*), F6.2→F2.2 (0) | `carbon_tax_level > 100` | F2 → F2.2 | CO₂-Steuer > 100 EUR → strikte Dekarbonisierungspolitik (Folie B2) |
| `f2_moderate_policy` | F3.1→F2.1 (+2), F4.1→F2.1 (-3*) | `carbon_tax_level < 80` | F2 → F2.1 | Niedrige Steuer = moderate Klimapolitik; keine radikale Regulierung (Folie B1) |
| `f3_saf_mandate_breakthrough` | F2.2→F3.2 (+3), F1.1→F3.2 (+3) | `saf_mandate_share ≥ 0.05` | F3 → F3.2 | SAF-Mandat ≥ 5% → Technologiedurchbruch (Folie A2); F2.2 treibt F3.2 stark |
| `f3_incremental_tech` | F2.1→F3.1 (-3), F5.1→F3.1 (-3) | `saf_mandate_share < 0.03` | F3 → F3.1 | Ohne Mandat bleibt SAF teuer (F3.1); moderate Politik hemmt Durchbruch |
| `f4_high_cost_pressure` | F2.2→F4.2 (+2), F3.1→F4.2 (+3) | `cost_pressure > 135` | F4 → F4.2 | Hoher Kostendruck = Regulierungskosten (F2.2) + fehlende Technologie (F3.1) |
| `f4_stable_growth` | F2.1→F4.1 (+3), F6.1→F4.1 (-3*) | `cost_pressure < 115` | F4 → F4.1 | Niedriger Druck = moderate Politik; F2.1 stützt Wirtschaftsstabilität |
| `f6_flight_shaming_high_tax` | F2.2→F6.2 (0), F1.2→F6.2 (+1) | `carbon_tax_level > 80` | F6 → F6.2 | CO₂-Steuer > 80 EUR signalisiert gesellschaftlichen Wandel → Flight Shaming |
| `f6_accepted_flying` | F3.1→F6.1 (+3), F4.1→F6.1 (+3) | `carbon_tax_level < 60` | F6 → F6.1 | Niedrige Steuer + keine Alternativen = Fliegen gesellschaftlich akzeptiert |
| `f7_oil_stress` | F4.2→F7.2 (-1*), F2.2→F7.2 (-3) | `oil_price_index > 1.15` | F7 → F7.2 | Ölpreis-Schock → Marktfragmentierung; F2.2 wirkt negativ auf F7.2 (Regulierung vs. Markt) |
| `f7_open_markets` | F4.1→F7.1 (-2*), F3.1→F7.1 (-3) | `oil_price_index ≤ 1.1` | F7 → F7.1 | Stabiler Ölpreis = offene, integrierte Märkte (F7.1) |

*) Einfluss ist formal negativ, wirkt aber im Kontext des Nicht-Auftretens als Abwesenheitsargument.

### Faktor-kaskadierende Regeln (Faktorzustand → Faktorzustand)

Diese Regeln kodieren direkte CIB-Wechselwirkungen: ein aktiver Faktor-Zustand löst einen anderen aus.
Die Einfluss-Werte in der Tabelle entsprechen direkt den Zellen in `cib_frozen.json`.

| Regel-ID | CIB-Kante | CIB-Einfluss | Bedingung | Effekt | Begründung |
|---|---|---|---|---|---|
| `f5_alternatives_flight_shaming` | F6.2→F5.2 (−1) | −1 | F6 = F6.2 | F5 → F5.2 | Flight Shaming treibt Nachfrage nach Schiene/Alternativen; CIB-Wert −1 = moderate Hemmung des Status quo F5.1 |
| `f5_no_alternative` | F6.1→F5.1 (+2) | +2 | F6 = F6.1 | F5 → F5.1 | Akzeptiertes Fliegen = keine Investition in Alternativen (F5 bleibt bei F5.1) |
| `f1_recession_demand_drop` | F4.2→F1.2 (−3*) | −3 | F4 = F4.2 | F1 → F1.2 | Rezession/Kostenkrise senkt Mobilitätsnachfrage drastisch |
| `f1_alternatives_substitution` | F5.2→F1.2 (−3*) | −3 | F5 = F5.2 | F1 → F1.2 | Günstige Alternativen (Schiene) substituieren Flugverkehr |
| `f6_tech_breakthrough_acceptance` | F3.2→F6.1 (+3) | +3 | F3 = F3.2 | F6 → F6.1 | SAF-Durchbruch reduziert gesellschaftlichen Widerstand → Fliegen wieder akzeptiert |

> **Hinweis zur Priorität**: Regeln höherer Priorität (höherer `priority`-Wert) überschreiben
> niedrigere. Z.B. hat `f6_flight_shaming_high_tax` (Prio 10) Vorrang vor
> `f6_tech_breakthrough_acceptance` (Prio 3) — bei hoher CO₂-Steuer bleibt F6.2, auch wenn
> F3.2 aktiv ist. Dies spiegelt das P2.4-Designprinzip wider: Regulierung dominiert Technologie.

---

## Kaskaden-Regeln

Die zwei folgenden Regeln ermöglichen emergente Nachfrage-Dynamiken über Faktor-Kaskaden:

| Regel-ID | Trigger | Effekt | CIB-Grundlage |
|---|---|---|---|
| `f1_recession_demand_drop` | F4 = F4.2 (Wirtschaftskrise) | F1 → F1.2 (sinkende Nachfrage) | F4.2→F1.2: stark negativ in CIB-Matrix |
| `f1_alternatives_substitution` | F5 = F5.2 (Alternativen vorhanden) | F1 → F1.2 (Substitution durch Schiene) | F5.2→F1.1: −3 (Alternativen schaden Fliegen) |

Diese Regeln erzeugen Kaskaden-Effekte: F2.2 → F6.2 → F5.2 → F1.2 modelliert den
vollständigen Pfad von "strenger Regulierung" über "Flight Shaming" und "Schienenausbau"
bis zu "sinkender Flug-Nachfrage" — alles ohne manuellen LLM-Eingriff.

---

## CIB im Kandidaten-System (Szenarioentwicklung)

Der Szenario-Generator nutzt CIB für drei Zwecke:

### 1. Kandidaten-Pool generieren (`build_candidate_constellations`)

`run_scenario_generator.py` erzeugt ausgehend vom Simulationsendzustand eine Menge
CIB-bewerteter Kandidaten-Konstellationen:

- **Continuation**: exakter Endzustand der Simulation
- **Single-Factor-Alternates**: je ein Faktor wird auf seinen alternativen Zustand geflippt
  (7 Varianten — wählt die Faktoren mit dem größten Einfluss-Konflikt lt. CIB)
- **Tension Scenarios**: der Faktor mit den meisten negativen CIB-Kanten wird geflippt

Jeder Kandidat erhält einen `consistency_score` aus `scenario_consistency.ConsistencyChecker`.

### 2. LLM-Selektion

Das LLM erhält alle Kandidaten mit ihren `candidate_id`s, Faktor-Zuständen und CIB-Scores.
Es wählt genau 3 aus, begründet seine Auswahl (`selection_reasoning`) und schreibt die
qualitativen Narrativen. Die numerischen Werte (Factor-States, CIB-Score) bleiben immer
Python-geerdet — das LLM erfindet keine Zahlenwerte.

### 3. Plausibilitäts-Ableitung

`_plausibility_from_score()` leitet die qualitative Plausibilität direkt aus dem
`consistency_score` ab:

| Score | Plausibilität |
|-------|--------------|
| ≥ 0.5 | hoch |
| ≥ 0.3 | mittel |
| < 0.3 | niedrig |

---

## Arbeitsteilung Python ↔ LLM

| Komponente | Python | LLM |
|---|---|---|
| Faktorzustand | `apply_factor_rules()` | narrativ (kein freier Sprung) |
| LLM-Vorschlag | nur via `validate_factor_proposals()` | Regulator: F2, F6 |
| Kandidaten-Score | `ConsistencyChecker.compute_consistency_score()` | — |
| Szenario-Auswahl | — | LLM wählt aus Python-Kandidaten |
| Szenario-Plausibilität | `_plausibility_from_score()` | — |
| Narrativ | — | LLM, geerdet auf Python-Werte |
| End-Score | `scenario_consistency` vs. frozen CIB | — |

---

## Empirisches Ranking der drei Sweep-Archetypen

Quantitativer Nachweis aus `tests/test_cib_ranking.py` (10 Tests, alle grün):

| Szenario | Consistency Score | Stability Index | Konflikte |
|---|:-:|:-:|:-:|
| **Business as Usual** (F1.1, F2.1, F3.1, F4.1, F5.1, F6.1, F7.1) | **0.973** | **1.000** | 0 |
| Transformationskonflikt (F1.2, F2.2, F3.1, F4.2, F5.2, F6.2, F7.2) | 0.867 | 0.952 | 2 |
| Freiwillige Wende (F1.2, F2.2, F3.2, F4.1, F5.2, F6.2, F7.1) | 0.603 | 0.810 | 8 |

**Kernnachweis**: `consistency_score(BAU) = 0.973 > consistency_score(Konflikt) = 0.867` ✓

Interpretation: BAU ist das perfekt selbstverstärkende Szenario (0 Konflikte, Stability = 1.0).
Der Transformationskonflikt hat 2 strukturelle Kern-Konflikte (F2.2+F3.1: strenge Regulierung
ohne Technologiedurchbruch; F4.2+F2.2: Rezession untergräbt strenge Regulierung), ist aber
insgesamt konsistenter als die Wende. Die Freiwillige Wende hat 8 Konflikte durch
selbst-untergrabende Dynamiken: F3.2 untergräbt F2.2 (−2) und F6.2 (−3), da technologischer
Erfolg Regulierungsdruck und Flight Shaming überflüssig macht.

---

## Tests

- `tests/test_factor_dynamics.py` — Regeln, 30-Tick-Übergänge ohne LLM
- `tests/test_scenario_consistency.py` — Score-Berechnung (F-CIB1/2/3)
- `tests/test_scenario_sweeps.py` — Sweep-Overrides und Endzustände
- `tests/test_cib_ranking.py` — **P4.3/P4.5** BAU > Konflikt Ranking (10 Tests)
