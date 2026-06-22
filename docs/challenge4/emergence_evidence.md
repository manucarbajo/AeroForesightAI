# Emergence Evidence — Challenge 4

Stand: 19.06.2026

## Was ist Emergenz im System?

**Definition (Systemkontext):** Nicht-monotone, wechselwirkungsgetriebene Verläufe — keine einfache
Kette „Input steigt → Output fällt", sondern Rückkopplungsschleifen zwischen Buchungsrate, Ticketpreis,
Markup und Population erzeugen Umkehrpunkte ohne exogene Schocks.

**Abgrenzung:** Exogene Shocks (CO₂-Stufen in `properties.json`) sind *Antriebe*, keine Emergenz.
Emergenz entsteht aus den internen Kopplungen — insbesondere dem Yield-Management-Feedback
(`apply_market_feedback`) und der heterogenen Logit-Buchungsentscheidung.

---

## Bewiesene Emergenz-Mechanismen

### 1. Yield-Feedback-Loop (M4) — automatisiert belegt

**Test:** `test_m4_emergence_over_30_ticks` in `tests/test_market_feedback.py`

**Mechanismus:**
```
Booking ↑ → Markup ↑ → Preis ↑ → Booking ↓ → Markup ↓ → Preis ↓ → Booking ↑ ...
```

**Abnahme-Gates (alle bestanden):**
- Preis-Amplitude ≥ 5 % vom Mittelwert ✓
- ≥ 1 Preis-Richtungswechsel ✓
- Booking-Range ≥ 0.10 ✓
- Margin-Range ≥ 4 € ✓

**Referenzlauf:** `run_20260611T155300Z` (40 Ticks, LLM)
- Preis 98,78 € → 126,74 € → 118,93 € (Anstieg + Umkehr)
- CO₂-Shocks Tick 15 (→120€) und Tick 30 (→200€) wirksam

---

### 2. Emergenz ohne exogenen CO₂-Shock (P2.5) — belegt

**Test:** `test_price_reversal_from_yield_feedback_only` in `tests/test_market_feedback.py`

**Setup:** Alle Trajektorien flatten (`resolve_trajectory` Tick 1) → konstante Exogenwerte, keine Stufen/Rampen.

**Ergebnis:** ≥ 1 Preis-Richtungswechsel entsteht allein aus dem Yield-Feedback-Loop.

**Interpretation:** Gedämpfter Schwingkreis (`damping=0.85`, `markup_adjustment_per_tick=0.08`).

---

### 3. Segment-Divergenz business vs. price_sensitive (M7 / P6.G2) — belegt

**Tests:**
- `test_stress_tick_business_vs_price_sensitive_at_least_15pp` in `tests/test_segment_divergence.py`
- `test_e2e_40_ticks_deterministic_segment_gap_and_saturation` in `tests/test_segment_divergence.py`

**Gate:** Buchungsrate `price_sensitive` vs. `business` divergiert um **≥ 15 Prozentpunkte**.

**Mechanismus:**
- F4.2 (Rezession) aktiv → `income_drop_f4_strict` senkt `income_factor`
- `income_index`-Rampe ab Tick 10 (1.0 → 0.92) in `properties.json`
- `price_sensitive`: niedrigeres Einkommen/WTP → Logit-Schwelle seltener erreicht
- `business`: höhere WTP/Einkommen → Buchung bleibt höher

**Referenzlauf (E2E, 40 Ticks, deterministic-only, seed 42):** `run_20260619_p2_saturation_e2e`
- Max. Segment-Gap **59,1 pp** bei Tick 12 (`business` 0,69 vs. `price_sensitive` 0,10)
- Tick 40: `business` 33,3 % vs. `price_sensitive` 7,6 % (25,7 pp)
- Artefakte: `timeseries/population.csv`, `tick_mechanics.json`, `population.csv`

**Reproduktion:**
```bash
python -m src.run_simulation --deterministic-only --rounds 40 --seed 42 \
  --run-id run_20260619_p2_saturation_e2e --no-protocol --no-scenarios
```

---

### 4. Sättigung über volle Pipeline (P2.1 E2E) — belegt

**Test:** `test_e2e_40_ticks_deterministic_segment_gap_and_saturation` (s. oben)

**Referenzlauf:** `run_20260619_p2_saturation_e2e`
- Nach 40 Ticks: `saturation_level > 0` bei **624** von 1080 Individuen
- `max(saturation_level) = 1.0` (kontinuierliches Modell, kein Cooldown)

**Config:** `properties.json → saturation` (`booking_increase`, `utility_penalty_factor`); segment-spezifische Decay-Raten in `individual_properties`.

---

### 5. Faktor-Ketten (M5/P2.4) — belegt

**Tests (P2.4):** `tests/test_factor_dynamics.py::TestNewFactorRules`

**Ketten:**
- F4.2 (Rezession) → F1.2 (Nachfragerückgang) → Booking ↓ → Markup ↓ → Preis ↓
- F5.2 (Alternativen) → F1.2 (Substitution) → gleicher Pfad
- F3.2 (SAF-Durchbruch) → F6.1 (Fliegen akzeptiert) → weniger eco_penalty → Booking ↑

---

## Sweep-Belege (M8)

| Sweep | CIB-Score | Interpretation |
|-------|-----------|---------------|
| `business_as_usual` | 0.573 | Höchste Konsistenz — keine internen Konflikte |
| `freiwillige_wende` | ~0.51 | Konsistent: SAF + CO₂ erzeugen kohärentes Szenario |
| `transformation_conflict` | < BAU | Konflikte (F2.2 vs F4.2 vs F3.1) → niedrigerer Score |

**Abnahme M5:** Transformations-Konflikt hat niedrigeren `consistency_score` als BAU ✓

---

## Lücken (noch offen)

- Sweep Transformations-Konflikt über 3 Seeds reproduzierbar (P6.G3)
- CIB-Ranking Konflikt < BAU automatisieren (P6.G4)
- P1: Literatur/Formeln für Sättigung, Yield-Kalibrierung (0.37), Segment-Überlappung
