# Emergence Evidence — Challenge 4

Stand: 18.06.2026

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

### 2. Emergenz ohne exogenen CO₂-Shock (P2.5) — NEU belegt

**Test:** `test_price_reversal_from_yield_feedback_only` in `tests/test_market_feedback.py`

**Setup:** Alle Trajektorien flatten (carbon_tax=const, oil=const, saf=const, income=const, fuel=const)
→ keinerlei exogene Stufen oder Rampen.

**Ergebnis:** ≥ 1 Preis-Richtungswechsel entsteht allein aus dem Yield-Feedback-Loop.

**Interpretation:** Das System ist inherent oszillierend — nicht ein Thermostat, sondern ein
gedämpfter Schwingkreis (damping=0.85, adjustment=0.06).

---

### 3. Segment-Divergenz bei CO₂-Schock + Einkommensdynamik (M7/M6)

**Gate:** `price_sensitive` vs. `business` Buchungsrate divergiert um ≥ 15 Prozentpunkte
wenn F4.2 (Rezession) + fallender `income_index` aktiv sind.

**Mechanismus:**
- `income_index` ramp Tick 10→15 (1.0 → 0.92)
- F4.2 → shift_rule `income_drop_f4_strict` (−0.05 income_factor)
- `price_sensitive` Individuen: WTP × income_factor sinkt → Logit-Schwelle nicht mehr erreicht
- `business` Individuen: WTP bleibt hoch genug → weiterhin Buchung

---

### 4. Faktor-Ketten (M5/P2.4) — neu belegt

**Tests (P2.4):** `tests/test_factor_dynamics.py::TestNewFactorRules`

**Ketten:**
- F4.2 (Rezession) → F1.2 (Nachfragerückgang) → Booking ↓ → Markup ↓ → Preis ↓
- F5.2 (Alternativen) → F1.2 (Substitution) → gleicher Pfad
- F3.2 (SAF-Durchbruch) → F6.1 (Fliegen akzeptiert) → weniger eco_penalty → Booking ↑

Diese 3 neuen CIB-gestützten Regeln (P2.4) schließen kritische Kanten der 14×14 CIB-Matrix.

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

- Sweep Transformations-Konflikt über 3 Seeds reproduzierbar (M12.4)
- Konkrete Run-IDs für Segment-Divergenz-Nachweis (M7 Gate)
- LLM-Run mit 40+ Ticks nach Saturation-Cooldown (P2.1 Ende-zu-Ende)
