# Project Plan 2 — Challenge 4 Endabgabe

| | |
| --- | --- |
| **Stand** | 21.06.2026 |
| **Abgabe** | 30.06.2026 — Gesamtsystem auf GitHub (40 Punkte, Challenge 4) |
| **Vorgänger** | [`projectplan.md`](projectplan.md) M0–M11 |
| **Ziel** | Endabgabe: C4-Aufgabenstellung, Coaching-Punkte, Forschungsfrage, belegbare Wissenschaft |
| **Branch** | `m9_dashboard/challenge4` |
| **Tests** | 267 pytest (aktuell 3 Fails) |
| **Fortschritt** | **P2 + P3 + P4.0–P4.5 + P5** (P5.7 teilweise erledigt) · P4.6–P4.8, P1, P6 Rest offen |
| **Nächster Schritt** | **P1** (scientific_foundation.md) oder **P4.6–P4.8** (CIB Reasoning) |

## Forschungsfrage

> Wie und in welcher Qualität können soziotechnische Systeme mit gegenseitig wechselwirkenden Einflussfaktoren durch Multiagentensysteme qualitativ über Zeiträume simuliert werden?

Antwort über **LLM-basierte qualitative Szenarien pro Lauf** (Text), reproduzierbare Python-Mechanik als Ground Truth, und wissenschaftliche Belegung in `scientific_foundation.md` (Referenz für Präsentation).

---

## Schwerpunkte Endabgabe

| Säule | Bedeutung |
| --- | --- |
| **Qualitatives Narrativ / Szenario** | LLM erklärt pro Run textuell, welche Zukunft eintreten konnte — Kern des Foresight-Ansatzes |
| **Ground Truth (Python)** | Zahlen, Faktoren, Booking — belegbar, nicht vom LLM erfunden |
| **Explorer / Chat** | Nachfragen zum selben Run (Szenario, Verlauf, Ticks) |
| **Wissenschaftliche Fundierung** | Fast jede Design- und Modellentscheidung mit Quelle — inkl. **Kap. 8 Formelsammlung** für Präsentation |

---

## Aufgabenstellung Challenge 4

| C4-Anforderung | Umsetzung | Nachweis |
| --- | --- | --- |
| Dynamisierung der Einflussfaktoren | `factor_rules`, Trajektorien, Sweeps | `timeseries/factors.csv` |
| Wechselwirkungen / Emergenz | Markt-Feedback, Faktor-Ketten, Population | Sweeps, Tests |
| Exploration (Chat) | `state_explorer.py`, Dashboard | grounded auf Run-Artefakte |

Szenario-Typen (BAU, Wende, Konflikt): Sweep-Presets als Startbedingungen. **Ergebnis-Szenario:** LLM-Text pro Lauf unter `outputs/<run_id>/`.

Traceability: [`traceability_c1_c4.md`](traceability_c1_c4.md).

---

## Output pro Run (Zielzustand)

Jeder Lauf schreibt **alles** unter `outputs/<run_id>/` — kein separates Figure- oder Szenario-Verzeichnis in `docs/`.

| Datei / Ordner | Rolle | Status |
| --- | --- | --- |
| `run_scenario.md` | **LLM-Szenario:** qualitative Storyline — was konnte passieren | **erledigt (P3)** |
| `run_scenario.json` | Struktur + Metadaten + Ground-Truth-Kennzahlen (für Chat/Explorer) | **erledigt (P3)** |
| `final_narrative.md` | Tick-Protokoll inkl. Agenten-Narrativ (LLM, verbessert) | teilweise |
| `figures/` | Charts nur aus diesem Run (`generate_run_figures`) | teilweise |
| `tick_mechanics.json` | Ground Truth pro Tick | erledigt |
| `timeseries/*.csv` | Faktoren, Properties, Population | erledigt |
| `event_log.json` | Events + Deltas | erledigt |

**Workflow:** Config → Lauf → `run_scenario.md` lesen → Figures im Run → Chat/Explorer zum Nachfragen.

---

## Coaching-Pflichten

| Punkt | Plan 2 | Status |
| --- | --- | --- |
| Sättigungseffekt | P2.1 | **erledigt** |
| Segmente erstellen/ändern | P2.2 | **erledigt** |
| CIB Rolle & Korrektheit | P4 | **teilweise** (P4.0–P4.5 erledigt; offen: s. P4 Offene Punkte) |
| Qualitatives Narrativ / Szenario (LLM) | P3 | **erledigt** |
| Faktoren dynamisieren | P2.4 | **erledigt** |
| Emergenz vs. Random Shocks | P2.5 | **erledigt** |
| Basispreis konfigurierbar | P2.3 | **erledigt** |
| Wissenschaftliche Fundierung | P1 | offen |

Reihenfolge: **P1 → P2 → P3 → P4 → P5 → P6**. M12-Gates (ehem. P0) **am Ende** in P6.

---

## Systemstand M0–M11 + P2

| Bereich | Status |
| --- | --- |
| Pipeline, Population, Faktoren, CIB, Sweeps, Explorer, Dashboard | erledigt |
| `tick_mechanics`, Timeseries, `final_narrative.md` (Qualität offen) | teilweise |
| **P2.1 Sättigungseffekt** (kontinuierliches `saturation_level`, Config + Dashboard, E2E-Lauf) | **erledigt** |
| **P2.2 Segmente SSOT & Dashboard** (überlappende Boolean-Labels, Modifikatoren, Markt/Sättigung UI) | **erledigt** |
| **P2.3 Basispreis konfigurierbar** (Sweep + Dashboard) | **erledigt** |
| **P2.4 Faktordynamik** (3 neue CIB-Regeln: F4→F1, F5→F1, F3→F6) | **erledigt** |
| **P2.5 Emergenz-Nachweis** (`emergence_evidence.md`, Tests inkl. Segment-Divergenz) | **erledigt** |
| **P6.G2 Segment-Divergenz** (`tests/test_segment_divergence.py`, Run `run_20260619_p2_saturation_e2e`) | **erledigt** |
| P1-Doku (Kap. 8), P4 CIB-Validierung (P4.6-P4.8), Explorer-Prüfung (P5.7) | offen |

---

## Meilenstein-Kette

```
P1 Fundierung ─► P2 Mechanik ─► P3 Narrativ (LLM-Szenario) ─► P4 CIB ─► P5 Dashboard/Abgabe ─► P6 Endcheck (+ M12-Gates)
```

---

# P1 — Wissenschaftliche Fundierung

Forschungsprojekt: Entscheidungen und Funktionen **belegen**. `scientific_foundation.md` ist Referenzdokument für Report und **Präsentation** (Folien verweisen auf Abschnitte/Quellen).

Vor P2-Implementierung: Eintrag in P1. Nach P2: P1 aktualisieren.

## Aufbau `scientific_foundation.md`

| Kap. | Inhalt | Quellen (Beispiele) |
| --- | --- | --- |
| 1 | Strategic Foresight, explorative Szenarien | Rohrbeck & Gemünden (2011); Chermack (2011); Gausemeier et al. (CIB) |
| 2 | Simulationsparadigma gesamt | Banks et al. (2010) DES; Bonabeau (2002) ABM; Epstein (2006) generativ; Ludewig & Lichter Kap. 16 |
| 3 | Domäne Flugverkehr | [`literature_fundamentals.md`](../archive/challenge1/literature_fundamentals.md); Evangelinos et al. (2011); Belobaba (Yield) |
| 4 | Regulatorik (Domäne) | [`links.md`](../references/links.md); EU ETS, Fit-for-55 |
| 5 | CIB & Faktoren F1–F7 | [`cib_rationale.md`](cib_rationale.md); Weimer-Jehle / Gausemeier |
| 6 | Hybrid-Architektur Python + LLM | [`challenge2/documentation.md`](../archive/challenge2/documentation.md) §5.0; White et al. (2023) Prompts |
| 7 | Qualitatives Narrativ / Szenario-Ableitung | LLM grounded generation; Abgrenzung Halluzination; Bezug Explorer |
| **8** | **Mathematisches Modell — Formelsammlung** | **Kap. 8 unten; Code-Audit `simulation_functions.py`, `population_sampler.py`, …** |
| 9 | Einzelmechanismen (Fundierungsmatrix) | je Modul + Verweis auf Kap. 8 |
| 10 | Modellgrenzen & Abweichungen C1–C4 | [`traceability_c1_c4.md`](traceability_c1_c4.md) |
| 11 | Literaturverzeichnis | Vollständige Referenzliste (APA o.ä.) |

---

## Kap. 8 — Mathematisches Modell (Formelsammlung)

**Ziel:** Jede numerische Entscheidung im System ist als Formel dokumentiert — mit Symbolen, Default-Parametern, Code-Referenz und Literaturbeleg. Präsentation kann direkt auf Kap. 8 verweisen („So definieren wir den Ticketpreis“).

**Vorgehen (P1.6):** Code durchgehen → Formel extrahieren → Symboltabelle → Quelle/Annahme → Abgrenzung zur Literatur.

### 8.1 Preis- und Kostenmodell (`simulation_functions.py`)

| ID | Größe | Formel (Implementierung) | Parameter (Defaults) | Code | Literatur / Annahme |
| --- | --- | --- | --- | --- | --- |
| F-P1 | **Ticketpreis (Kostenkomponente)** | \(p_{\mathrm{cost}} = \max(p_{\min},\, b \cdot (1+\Delta f) \cdot o + \tau_c \cdot k_c + s \cdot k_s - \sigma \cdot s)\) | `base_price` \(b\); `fuel_price_change` \(\Delta f\); `oil_price_index` \(o\); `carbon_tax` \(\tau_c\); `saf_share` \(s\); `efuel_subsidy` \(\sigma\); Koeff.: `carbon_per_tonne`=0.001, `saf_premium_factor`=0.5, `min_ticket_price`=1 | `compute_ticket_price` | Belobaba (Yield-Kosten); Domäne SAF/ETS |
| F-P2 | **Kostenindex (Treibstoff)** | \(I_t = \max(0.1,\, I_{t-1} \cdot (1+\Delta f_t))\) | nur wenn `compound_fuel_on_cost`=True | `update_cost_index` | Akkumulierte Treibstoffinflation |
| F-P3 | **Kostendruck (Tick)** | \(C_t = \underbrace{p_{\mathrm{cost}}(b \cdot I_t, \ldots)}_{\text{F-P1}} \cdot m \cdot w + R_t\) | `maintenance_cost_index` \(m\); `staff_cost_index` \(w\); \(R_t\)=regulatorische Zusatzkosten | `compute_cost_pressure` | Regulatorik aus Config |
| F-P4 | **Veröffentlichter Preis** | \(p_t = C_t + \max(0,\, \mu_t)\) | `provider_markup` \(\mu\) | `compose_ticket_price` | Kosten + Marge |
| F-P5 | **Preis-Clipping** | \(\|\Delta p\| \leq \alpha \cdot p_{t-1}\) | `max_price_change_fraction` \(\alpha\)=0.08 | `clip_price_change` | Numerische Stabilität |
| F-P6 | **Yield-Feedback (Markup)** | \(\Delta\mu = \lambda \cdot g \cdot \beta \cdot \max(\mu_{t-1},\, C_t \cdot \rho_m)\); \(g = \mathrm{BR}_t - \mathrm{BR}^*\) | `damping` \(\lambda\)=0.85; `markup_adjustment_per_tick` \(\beta\)=0.08; `target_booking_rate` \(\mathrm{BR}^*\)=**0.37**; `margin_reference_fraction` \(\rho_m\)=0.08 | `apply_market_feedback` | Belobaba Revenue Management; DE-Flugquote (Kalibrierung P1) |
| F-P7 | **Yield-Feedback (Preispfad)** | \(p^{\mathrm{yield}} = p_{t-1} \cdot (1 + \lambda \cdot g \cdot \beta)\); Auswahl min/max mit Markup-Pfad je nach \(g\) | — | `apply_market_feedback` | Preisanpassung bei Unter-/Überbuchung |
| F-P8 | **Marginal Cost Floor** | Der Ticketpreis fällt niemals unter Grenzkosten + Steuern/Gebühren. | `marginal_cost_fraction` = 0.33 (33% der Basis-Kosten sind echte Grenzkosten) | `apply_market_feedback` | Airlines betreiben Loss-Leading für Fixkosten, aber kein Dumping unter Grenzkosten |

### 8.2 Nachfrage und Elastizität (Makro vs. Mikro)

**Wichtig für Präsentation:** Zwei getrennte Konzepte — nicht vermischen.

| ID | Ebene | Formel | Default | Code | Literatur |
| --- | --- | --- | --- | --- | --- |
| F-D1 | **Makro-Nachfrageindex** (ohne Booking-Feedback) | \(D_t = \max(0,\min(2,\, D_{t-1} \cdot (1+g) \cdot (1 - \varepsilon \cdot \delta_p)))\); \(\delta_p = (p_t - p_{t-1})/p_{t-1}\) | `price_elasticity` \(\varepsilon\)=**0.5**; `demand_growth_rate` \(g\) | `compute_demand` | Evangelinos et al. (2011) — Richtung heterogene Elastizität; **Kalibrierung offen in P1** |
| F-D2 | **Makro-Nachfrage (mit Booking)** | \(D_t = (1-w) \cdot D_{t-1}(1+g) + w \cdot \mathrm{clip}(\mathrm{BR}_t / \mathrm{BR}^*, 0, 2)\) | `booking_weight` \(w\)=0.6 | `sync_demand_level` | Kopplung Mikro→Makro (Emergenz) |
| F-D3 | **Booking-Rate (Mikro)** | \(\mathrm{BR}_t = \#\{\mathrm{booked}\} / N\) | Population \(N\) | `evaluate_booking` | Aggregat aus F-B1…F-B4 |
| F-D4 | **Segment-Elastizität** | Heuristische `price_sensitivity` pro Person (0–1), **nicht** identisch mit F-D1 | Label-abgeleitet: base 0.5 ± business/frequent/price_sensitive | `_derive_price_sensitivity` | Segmentheterogenität; P1: Abgrenzung zu F-D1 |

### 8.3 Buchungsentscheidung — Logit (`population_sampler.py`)

| ID | Größe | Formel | Default | Code | Literatur |
| --- | --- | --- | --- | --- | --- |
| F-B0 | **Affordability-Gate** | Buchen nur wenn \(p_t \leq \mathrm{WTP} \cdot \iota \cdot (1 + \gamma \cdot a)\) | `green_premium` \(\gamma\)=0.1; `income_factor` \(\iota\); `environmental_awareness` \(a\) | `_booking_probability` | WTP-Konzept |
| F-B1 | **Nutzen** | \(U = U_0 - \sigma_p \cdot (p_t/100) - \pi_{\mathrm{eco}} - \pi_{\mathrm{sub}}\) | `base_utility` \(U_0\)=2.0 | `_booking_probability` | Random Utility (McFadden) |
| F-B2 | **Preisstrafe** | \(\sigma_p \cdot (p_t/100)\) | `price_sensitivity` \(\sigma_p \in [0,1]\) | idem | Discrete Choice |
| F-B3 | **Öko-Strafe** | \(a \cdot \max(0,\, \tau_c - \tau_0)/100\) (+ Bonus bei \(\sigma_p > 0.8\)) | `DEFAULT_CARBON_ECO_BASELINE` \(\tau_0\)=50 | idem | Umweltpräferenz |
| F-B4 | **Substitutions-Strafe** | \(\rho \cdot (p_t/100) \cdot 1.5\) | `substitution_readiness` \(\rho\) | idem | Modal-Split-Heuristik |
| F-B5 | **Buchungswahrscheinlichkeit** | \(P(\mathrm{book}) = 1/(1+e^{-U})\); buchen wenn \(P \geq \theta\) | `logit_threshold` \(\theta\)=0.5 | idem | Logit (McFadden; Train) |

### 8.4 Population & Segmente

| ID | Inhalt | Formel / Regel | Code |
| --- | --- | --- | --- |
| F-POP1 | WTP-Sampling | Lognormal(\(\mu\), \(\sigma\)) oder Normal, segmentbedingte Multiplikatoren (business ×1.25, frequent ×1.5) | `initialize_population` |
| F-POP2 | `income_factor` | Base 1.0 ± Labels + \(\mathcal{N}(0, 0.05)\), clip [0.5, 1.5] | idem |
| F-POP3 | Property-Shifts | \(\Delta x\) aus `shift_rules` pro Tick | `apply_shift_rules` |
| F-POP4 | Sättigung (P2.1) | `saturation_level` +0.6 bei Buchung; Penalty in Logit; Decay pro Segment | `saturation` in `properties.json`; Dashboard | geplant (P1.9) |

### 8.5 CIB & Faktoren

| ID | Größe | Formel | Code | Literatur |
| --- | --- | --- | --- | --- |
| F-CIB1 | **Konsistenz-Score** | \(\mathrm{raw} = (\sum^+ - \sum^-)/\sum^{\mathrm{abs}}\); Score \(= (\mathrm{raw}+1)/2 \in [0,1]\) | `compute_consistency_score` | Gausemeier / Weimer-Jehle |
| F-CIB2 | **Stabilitäts-Index** | \(1 - \#\{\mathrm{influence} \leq -2\} / \#\mathrm{Paare}\) | `compute_stability_index` | idem |
| F-CIB3 | **Konflikt-Schwelle** | influence \(\leq -1.5\) → Konflikt | `ConsistencyChecker` | Projekt-CIB |
| F-FAC1 | **Faktor-Übergang** | Bedingte Regeln aus `factor_rules` + Runtime-Metriken | `factor_dynamics.py` | Kap. 5; **Regeln einzeln in Kap. 8.5.x** |

### 8.6 Symbol- und Parameterverzeichnis

Kap. 8 schließt mit einer **eigenen Tabelle aller Symbole** (\(p_t, C_t, \varepsilon, \sigma_p, \mathrm{BR}_t, \ldots\)) und Verweis auf Config-Felder (`PriceModelConfig`, `MarketFeedbackConfig`, `PriceCoefficientsConfig`).

### 8.7 Abgrenzungen (Pflicht in Kap. 8)

| Thema | Was wir modellieren | Was wir **nicht** kalibrieren |
| --- | --- | --- |
| Preiselastizität | Lineare Makro-Heuristik F-D1 + segmentierte Mikro-Logit F-B* | Ökonometrische Schätzung aus IATA/Demand-Studien |
| Yield Management | Heuristisches Feedback F-P6/F-P7 | Vollständiges RM-Optimierungsmodell |
| Logit | Binäres Buchen/Nicht-Buchen pro Tick | Nested Logit / Mixed Logit |

---

## Fundierungsmatrix (Kap. 9 — Pflicht pro Mechanismus)

| Mechanismus | Modul | Modell | Formel (Kap. 8) | Quelle | Annahme | Grenze |
| --- | --- | --- | --- | --- | --- | --- |
| Tick / Epoche | `orchestrator_node.py` | Diskrete Simulation | — | Banks; Ludewig & Lichter | Ticks ≠ Kalenderjahre | … |
| Property-Trajektorien | `property_engine.py` | Exogene SD-Variablen | Trajektorien | Forrester (Konzept) | … | … |
| Ticketpreis / Kosten | `simulation_functions.py` | Kosten + Marge + Feedback | F-P1…F-P8 | Belobaba; Domäne | Heuristisch | Kap. 8.7 |
| Makro-Elastizität | `simulation_functions.py` | Linear in \(\delta_p\) | F-D1 | Evangelinos et al. | \(\varepsilon=0.5\) Default | Nicht kalibriert |
| Mikro-Buchung (Logit) | `population_sampler.py` | Random Utility / Logit | F-B0…F-B5 | McFadden; Train | Threshold 0.5 | … |
| Population / Segmente | `population_sampler.py` | ABM heterogen | F-POP1…F-POP3 | Bonabeau; Schelling | … | … |
| Markt-Feedback | `simulation_functions.py` | Yield-Heuristik | F-P6, F-P7, F-D2 | Belobaba | Emergenz-Pfad | … |
| Faktor-Regeln | `factor_dynamics.py` | CIB → bedingte Übergänge | F-FAC1 | Gausemeier; Kap. 5 | … | … |
| CIB-Score | `scenario_consistency.py` | Paarweise Konflikte | F-CIB1…F-CIB3 | Projekt-CIB | … | … |
| Sättigung | P2.1 | Kontinuierliches Sättigungslevel / Decay | F-POP4 | P1.8 (Literatur) | … | … |
| LLM Agenten-Narrativ | `agent_node.py`, Prompts | Grounded NLG | — | White; Kap. 7 | LLM erfindet keine Zahlen | … |
| LLM Run-Szenario | P3 Generator | Grounded Synthese | — | Kap. 7 | Kontext aus Run-Artefakten | … |
| Explorer / Chat | `state_explorer.py` | RAG auf Run-State | — | Kap. 7 | … | … |

## Aufgaben P1

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P1.1 | `scientific_foundation.md` — Gliederung Kap. 1–11 | offen |
| P1.2 | Kap. 1–2: Foresight + Simulationsparadigma | offen |
| P1.3 | Kap. 3–4: Domäne + Regulatorik | offen |
| P1.4 | Kap. 5–6: CIB + Hybrid-Architektur | offen |
| P1.5 | Kap. 7: Narrativ / Szenario / Explorer (Methodik) | offen |
| **P1.6** | **Kap. 8: Formelsammlung — Code-Audit, alle F-* aus Tabellen oben ausformulieren** | offen |
| P1.6.1 | F-P1…F-P8: Preis, Kosten, Yield-Feedback (`simulation_functions.py`) | offen |
| P1.6.2 | F-D1…F-D4: Makro-Elastizität vs. Mikro-`price_sensitivity` abgrenzen + Literatur | offen |
| P1.6.3 | F-B0…F-B5: Logit-Buchung + Parameterbegründung | offen |
| P1.6.4 | F-POP1…F-POP4, F-CIB1…F-CIB3, F-FAC1 (+ jede `factor_rule` einzeln) | offen |
| P1.6.5 | Symbol- und Parameterverzeichnis (8.6); Abgrenzungen (8.7) | offen |
| P1.7 | Kap. 9: Fundierungsmatrix vollständig (mit Kap.-8-Verweis) | offen |
| P1.8 | Kap. 10–11: Grenzen + Literaturverzeichnis | offen |
| P1.9 | Sättigung: Quelle recherchieren + Formel F-POP4 (vor P2.1) | offen |
| P1.10 | `presentation_references.md` — inkl. **Formel-Folien** (Kap. 8 → 1 Satz + Quelle) | offen |
| P1.11 | Review: jedes P2/P3-Feature hat P1-Eintrag **und** Kap.-8-Formel | offen |
| P1.12 | Kreuzcheck: Formeln in Kap. 8 = exakt Code (Tests/`tick_mechanics` stichproben) | offen |

Bestehende Basis: [`challenge2/documentation.md`](../archive/challenge2/documentation.md) §5.0, [`literature_fundamentals.md`](../archive/challenge1/literature_fundamentals.md), [`cib_rationale.md`](cib_rationale.md).

---

# P2 — Kern-Mechanik (Coaching)

Implementierung nur mit P1-Bezug. (Inhalt unverändert zu vorher — Sättigung, Segmente, base_price, Faktoren, Emergenz.)

## P2.1 Sättigungseffekt

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| P2.1.1 | P1.9 Literatur + Formel F-POP4 | `scientific_foundation.md` Kap. 8 | offen (P1) |
| P2.1.2 | `saturation_level` | `population_models.py` | **erledigt** |
| P2.1.3 | Kontinuierlicher Decay & Logit Penalty | `population_sampler.py` | **erledigt** |
| P2.1.4 | Dashboard: Decay-Raten + globale Sättigung (`saturation`) | `config_ui.py` | **erledigt** |
| P2.1.5 | Test auf kontinuierliche Sättigung | `tests/test_population_sampler.py` | **erledigt** |
| P2.1.6 | E2E 40 Ticks + Sättigung aktiv | `tests/test_segment_divergence.py`, Run `run_20260619_p2_saturation_e2e` | **erledigt** |

**Umsetzung (18.–19.06.2026):** Harter Cooldown wurde durch kontinuierliches `saturation_level` ersetzt. Parameter in `properties.json → saturation` (Dashboard: Tab Bevölkerung). Bei Buchung steigt Level um `booking_increase` (Default 0.6); Logit-Penalty über `utility_penalty_factor`.
*   Decay-Raten segment-spezifisch: `frequent_flyer` (1.0), `business` (0.3), `price_sensitive` (0.15), `eco_conscious` (0.05).
*   `target_booking_rate` = 0.37 (Dashboard: Tab Properties); Kalibrierungsbegründung → **P1 offen**.

## P2.2 Segmente

| ID | Aufgabe | Datei | Status |
| -- | ------- | ----- | ------ |
| P2.2.1–P2.2.6 | SSOT, Dashboard, Sweeps, Legacy | s. Plan 1 | **erledigt** |

**Umsetzung (18.–19.06.2026):** `aggregate_population_stats()` leitet Segment-Keys dynamisch aus `individual_properties[boolean]` ab. Dashboard: Prevalence, Decay, Modifikatoren, Markt-Feedback.
*   **Überlappende Labels:** Boolean-Segmente sind **unabhängig** gezogen — eine Person kann mehrere Merkmale haben (z. B. `business` + `price_sensitive`). Prevalences sind **marginale** Wahrscheinlichkeiten, keine Partition.
*   **Demografie (Näherung):** `eco_conscious` 60 %, `price_sensitive` 30 %, `business` 8 %, `frequent_flyer` 3 % — optional `exclusive_group` für exklusive Personas.
*   **Dashboard:** Segmente anlegen/löschen (Legacy geschützt); globale Sättigung + Yield-Parameter editierbar.

## P2.3 Basispreis

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P2.3.1–P2.3.3 | Dashboard, Sweep, Test; **P1.6.1:** `base_price` in F-P1 dokumentieren | **erledigt** (P1.6.1 offen) |

**Umsetzung (18.06.2026):** `SweepConfig.base_price: float | None`, `apply_sweep_overrides()` setzt `price_model.base_price`. Dashboard Properties-Tab: Checkbox + Number-Input. `ConfigDraft.base_price` → `build_custom_sweep_from_draft()`. 2 neue Tests.

## P2.4 Faktordynamik

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P2.4.1–P2.4.4 | Inventar, Lücken, **P1.6.4** (F-FAC1 pro Regel), Test | **erledigt** (P1.6.4 offen) |

**Umsetzung (18.06.2026):** 3 neue CIB-gestützte `factor_rules` ergänzt:
- `f1_recession_demand_drop`: F4.2 → F1.2 (CIB: F4.2→F1.2: −3)
- `f1_alternatives_substitution`: F5.2 → F1.2 (CIB: F5.2→F1.2: +2)
- `f6_tech_breakthrough_acceptance`: F3.2 → F6.1 (CIB: F3.2→F6.1: +3)
3 neue Tests in `TestNewFactorRules`.

## P2.5 Emergenz

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P2.5.1 | `emergence_evidence.md` (Run-IDs, Tests) | **erledigt** |
| P2.5.2 | Test ohne CO₂-Shock, Preis-Umkehr | **erledigt** |
| P2.5.3 | Kein Random-Shock-Generator | Regel ✓ |
| P2.5.4 | Segment-Divergenz ≥ 15 pp (`test_segment_divergence.py`) | **erledigt** |

**Umsetzung (18.–19.06.2026):** `emergence_evidence.md` aktualisiert. Neuer Test `test_price_reversal_from_yield_feedback_only`. Segment-Gap-Tests + E2E-Run `run_20260619_p2_saturation_e2e` (40 Ticks, seed 42, max. Gap 59,1 pp).

## P2.6 Yield Management & Pricing Dynamik

| ID | Aufgabe | Status | Umsetzung |
| -- | ------- | ------ | --------- |
| P2.6.1 | Dynamische Steuern & Gebühren | erledigt | `SystemProperty` Typen `tax` (relativ) und `fee` (absolut) in Frontend & Modellen implementiert (`compose_ticket_price`). |
| P2.6.2 | Markup-Bugfix (Tax-in-Markup) | erledigt | `apply_market_feedback` rechnet Steuern/Gebühren aus dem Zielpreis heraus, um reine Airline-Marge exakt zu berechnen. |
| P2.6.3 | Target Booking Rate (Populationsauslastung) | erledigt | `target_booking_rate` in `MarketFeedbackConfig` wurde final auf 0.37 (37%) justiert, um exakt dem Flugverhalten der realen Bevölkerungsdemografie zu entsprechen (zuvor kurzzeitig 0.84 als IATA-Flugzeug-Auslastungs-Referenz). |
| P2.6.4 | Marginal Cost Floor (Rote Linie) | erledigt | `marginal_cost_fraction` (0.33) eingeführt. Airline darf Loss-Leading betreiben, Preise fallen aber nie unter Grenzkosten + volle Steuern. |

---

# P3 — LLM-Szenario pro Run (Kernsäule)

## Prinzip

| Ebene | Wer | Was |
| --- | --- | --- |
| **Python** | Simulation | Zahlen, Faktoren, Booking, Events — Ground Truth. Erzeugt N **CIB-bewertete Kandidat-Konstellationen** (`build_candidate_constellations`) aus dem Lauf-Endzustand |
| **LLM** | Nach Lauf | **Auswahl + qualitativer Text:** wählt 3 Kandidaten per `candidate_id` aus, begründet die Auswahl (`selection_reasoning`) und erzählt die plausiblen Zukünfte — erfindet aber **keine** Faktoren/Zahlen |
| **Explorer/Chat** | Nutzer | Nachfragen zum Run — antwortet grounded auf dieselben Artefakte + Szenario-Text |

Das Szenario ist **LLM-basiert und textuell** — kein reines Template. Die Faktor-Konstellationen und CIB-Scores sind **Python-Ground-Truth**; das LLM **selektiert, begründet und erzählt** auf dieser Basis, erfindet aber **keine** Zahlen. Damit ist der MAS-/LLM-Einsatz auch für die Szenario-Säule belegbar (nicht nur Dekoration eines fixen Templates).

## Begriffe

| Begriff | Bedeutung |
| --- | --- |
| Sweep | Start-Annahmen (Input) |
| Run | `outputs/<run_id>/` |
| Szenario | LLM-Output: explorative Zukunftsstory dieses Laufs |

## Ist → Soll

| | Ist | Soll |
| --- | --- | --- |
| Szenario | fehlt | `run_scenario.md` — LLM, qualitativ, pro Run |
| Tick-Narrativ | `final_narrative.md`, schwach bei Mock | LLM-Agenten + verbesserte Prompts |
| Chat | Explorer auf Run-Daten | + Bezug zu `run_scenario.md` |
| Legacy C3 | `ScenarioAgentNode` | parallel zu P3-Pipeline (CIB-Szenarien) |

## Aufgaben

| ID | Aufgabe | Datei | Status | Umsetzung |
| -- | ------- | ----- | ------ | --------- |
| P3.1 | `run_scenario_generator.py` — LLM-Prompt mit Run-Kontext (tick_mechanics, factors, segments, events) | `src/` | **erledigt** | Prompt-Reihenfolge korrigiert (Instruktionen nach Kontext). Regex-Fix für Trailing Commas in `_extract_json_object`. |
| P3.2 | Grounding-Regeln: Zahlen nur aus Kontext; Validierung / Post-Check | Generator | **erledigt** | Anti-Halluzinations-Filter in `validate_scenario_narrative` entspannt (erlaubt CIB-Scores ohne Fallback-Abbruch). |
| P3.3 | Nach Lauf automatisch: `run_scenario.md` + JSON | `run_simulation.py`, Dashboard | **erledigt** | Aufruf des Generators am Ende von `run_simulation.py` integriert; Dashboard zeigt Ergebnisse automatisch an. |
| P3.4 | CLI Regenerierung: `--run-id` | Generator | **erledigt** | `argparse` in `run_scenario_generator.py` ergänzt, um Szenarien für existierende Runs via CLI nachträglich zu erzeugen. |
| P3.5 | Prompts Agenten: demand/booking, SAF/F3/F6, Segment-Bezug | `prompts/*.md` | **erledigt** | Prompts für Consumer, Provider und Regulator enthalten bereits Segment-Referenzen, `prior_booking_rate` sowie SAF/F3/F6-Anweisungen. |
| P3.6 | `final_narrative.md` — qualitative Agenten-Blöcke verbessern | `output_writer.py` | **erledigt** | Begründungen werden nun vollständig als Blockquotes zitiert, spezifische Aktionen und Faktor-Vorschläge werden übersichtlich extrahiert und formatiert dargestellt. |
| P3.7 | Explorer: `run_scenario.md` im Kontext | `state_explorer.py` | **erledigt** | `state_explorer.py` liest nun `run_scenario.md` ein, sodass Chat-Queries mit Bezug zum qualitativen Szenario beantwortet werden. |
| P3.8 | Sweeps: voller Run-Output inkl. LLM-Szenario | `scenario_sweeps.py` | **erledigt** | OutputWriter Logik aus `run_simulation` integriert. Alle Artefakte (CSV/JSON) und LLM-Szenario (`generate_and_save_run_scenario`) werden generiert. `sweep_filter` Bug im UI behoben. |
| P3.9 | Tests: Generator lädt Run-Artefakte; Mock-LLM mit Fixture | `tests/` | **erledigt** | Unit-Tests für Generator erstellt. `pytest`-Fixture für Mock-LLM integriert, um deterministische Tests ohne echte API-Kosten zu ermöglichen. |
| P3.10 | P1 Kap. 7 + Kap. 8: Methodik LLM-Szenario; keine erfundenen Formelwerte | `scientific_foundation.md` | offen | — |
| P3.11 | LLM-Szenario: Entkopplung von Vorlesungs-Archetypen, dynamische Titel, Inline-Faktor-Belege, 3-Stufen CIB | Generator / Prompts | **erledigt** | 3-Stufen-CIB und Inline-Faktor-Referenzen in Prompt ergänzt. Dynamische LLM-Titel etabliert; `_slide_scenario_title` bleibt nur als Fallback-Titel für Template-/deterministische Läufe. |
| P3.12 | **LLM wählt Szenarien aus** (statt nur 3 fixe zu betexten): `build_candidate_constellations` erzeugt N CIB-bewertete Pfade; LLM selektiert 3 per `candidate_id` + `selection_reasoning` | `run_scenario_generator.py`, `prompts/run_scenario.md` | **erledigt** | Faktor-Konstellationen bleiben Python-Eigentum (reproduzierbar/grounded), das LLM trägt Auswahl + Begründung + Narrativ bei. Plausibilität jetzt aus CIB-Score abgeleitet (`_plausibility_from_score`). |
| P3.13 | **Grounding härter:** Mindestlänge der LLM-Story (sonst Template-Fallback), Kandidaten-CIB-Scores in `allowed_number_tokens` | Generator | **erledigt** | `SCENARIO_MIN_STORY_LEN`; dünne LLM-Stories fallen auf deterministische Beschreibung zurück. |
| P3.14 | **Prompt↔Permission-Konsistenz:** Agenten-Prompts an `AGENT_FACTOR_PERMISSIONS` angeglichen (Consumer/Provider: keine Faktor-Vorschläge; Regulator: nur F2/F6) | `prompts/consumer.md`, `provider.md`, `regulator.md` | **erledigt** | Beseitigt verworfene Faktor-Vorschläge (Consumer F1/F6, Provider F3, Regulator F5 waren nie erlaubt). |

## Inhalt `run_scenario.md` (LLM-generiert, strukturiert)

1. **Lauf-Narrativ** — was im Simulationslauf passiert ist (F1–F7, Wechsel, Markt, Events)
2. **Faktorprofil** — Endzustände und Übergänge aus `timeseries/factors.csv`
3. **Top-3 explorative Szenarien** — Cross-Impact-Kombinationen (Fortsetzung / Alternative / Spannung):
   - explizite `factor_constellation` F1–F7
   - was **eintreten könnte** (Strategic Foresight, nicht Prognose)
4. CIB-Einordnung · Grenzen · Ground Truth (Python)

## Abnahme P3

- [x] Jeder Lauf: LLM-`run_scenario.md` + JSON (Template-Fallback bei Mock/deterministic)
- [x] Text qualitativ, für Präsentation lesbar
- [x] Keine erfundenen Kennzahlen (Ground-Check + `ground_truth`-Block; CIB-Scores in `allowed_number_tokens`)
- [x] **LLM wählt 3 Pfade aus CIB-bewerteten Kandidaten** (`candidate_id`) und begründet die Auswahl — Faktoren bleiben Python-Ground-Truth
- [x] Dünne LLM-Stories fallen auf deterministische Beschreibung zurück (`SCENARIO_MIN_STORY_LEN`)
- [x] Explorer beantwortet „Was ist passiert?“ / „Warum?“ zum Run (Szenario im Kontext)
- [x] Zwei Configs → zwei unterschiedliche Szenario-Texte (Template-Test)

---

# P4 — CIB

## P4 Prinzip

Die **Referenz-CIB** (`configs/cib_frozen.json`) ist eine **statische, domänen-definierte** 14×14-Matrix (Weimer-Jehle). Sie wird **nicht** aus Simulationsläufen abgeleitet, sondern dient als feste Brille für Konsistenz-Scores, Sweep-Vergleiche und P3-Kandidaten-Bewertung.

| Komponente | Rolle |
| --- | --- |
| `cib_frozen.json` | Referenz-Matrix (eingefroren, v2 domänenkorrekt) |
| `factor_rules` | Laufzeit-Übersetzung starker CIB-Kanten in bedingte Faktor-Übergänge |
| `scenario_consistency.py` | Score-Berechnung (F-CIB1…3) gegen Referenz-Matrix |
| `build_candidate_constellations` (P3) | CIB-bewerteter Kandidaten-Pool für LLM-Szenario-Auswahl |

**Umsetzung (20.06.2026):** Platzhalter-Matrix (`deterministic_seed_42`) durch **domänenkorrekte v2-Matrix** ersetzt (`scripts/rebuild_cib_frozen.py`). Alle 168 Kanten nach Vorlesungsfolien (F19–22) und Faktoren F1–F7 neu definiert; 27 logische Widersprüche der alten Matrix beseitigt. Metadata in `cib_frozen.json` korrigiert.

### Empirisches Ranking (Referenz-Matrix v2)

| Szenario | Consistency | Stability | Konflikte |
| --- | ---: | ---: | ---: |
| Business as Usual (A1+B1) | **0.973** | **1.000** | 0 |
| Transformationskonflikt (B2 vs A1) | 0.867 | 0.952 | 2 |
| Freiwillige Wende (A2+B2) | 0.603 | 0.810 | 8 |

**Kernnachweis P4.3:** BAU > Konflikt > Wende (Consistency-Score). BAU ist perfekt selbstverstärkend (0 Konflikte). Wende hat die meisten Konflikte, weil F3.2 (SAF-Durchbruch) F2.2 und F6.2 untergräbt — valider CIB-Befund.

## Aufgaben

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P4.0 | **Referenz-Matrix v2:** `cib_frozen.json` domänenkorrekt neu definiert; Platzhalter-Metadata entfernt | **erledigt** |
| P4.1 | [`cib_role.md`](cib_role.md) — Rolle der CIB, Systemüberblick, empirisches Ranking | **erledigt** |
| P4.2 | [`cib_rationale.md`](cib_rationale.md) — P2.4-Regeln, P3-Kandidaten, CIB-Kante ↔ Regel | **erledigt** |
| P4.3 | Ranking BAU (0.973) > Konflikt (0.867) > Wende (0.603) quantitativ nachgewiesen | **erledigt** |
| P4.4 | CIB-Kante ↔ Regel vollständig dokumentiert — alle 14 `factor_rules` mit CIB-Einfluss-Werten | **erledigt** |
| P4.5 | `tests/test_cib_ranking.py` — 12 Tests, alle grün; BAU > Konflikt; Stability-Index-Ranking | **erledigt** |
| P4.6 | CIB in P1 Kap. 5 + **F-CIB1…3 in Kap. 8** + Präsentations-Referenz (`scientific_foundation.md`) | offen |
| P4.7 | `reasoning`-Felder in `cib_frozen.json` — Begründung pro Kante (168 Zellen, Verteidigung/Prüfung) | offen |
| P4.8 | **Validierung & Limitationen:** Herkunft der Matrix (domänenbasiert, kein Delphi/ScenarioWizard); Einfluss-Stärken (+2 vs. +3) als Annahmen → `cib_rationale.md` oder Kap. 5/10 | offen |

## Offene Punkte (P4)

Mechanik, Tests und Doku **P4.0–P4.5 sind erledigt**. Für eine vollständige wissenschaftliche Verteidigung fehlen noch:

- **P4.6** — CIB in `scientific_foundation.md` (Kap. 5 + F-CIB1…3 in Kap. 8.5)
- **P4.7** — `reasoning`-Felder in `cib_frozen.json` leer (168 Kanten ohne Begründung)
- **P4.8** — Kein formaler Experten-Workshop; Einzelwerte (+2 vs. +3) sind Urteilsfragen, nicht eindeutig „wahr“

## P4 Abnahme-Checkliste

- [x] Referenz-Matrix ist statisch und domänen-definiert (kein Best-Run-Vergleich)
- [x] Matrix v2 domänenkorrekt (Platzhalter `deterministic_seed_42` ersetzt)
- [x] `cib_role.md` und `cib_rationale.md` vorhanden und aktuell
- [x] Alle `factor_rules` mit CIB-Kanten begründet
- [x] Ranking BAU > Konflikt per Test abgesichert (`test_cib_ranking.py`, 12 Tests)
- [ ] **`reasoning`-Felder** in `cib_frozen.json` für alle 168 Kanten ergänzt (P4.7)
- [ ] **Validierung/Limitationen** dokumentiert: kein Experten-Workshop, Urteilsfragen bei Einfluss-Stärke (P4.8)
- [ ] **P4.6:** CIB in `scientific_foundation.md` Kap. 5 + F-CIB1…3 in Kap. 8.5 eingebunden

---

# P5 — Dashboard & Abgabe

Dashboard = **Workbench für Präsentation und Exploration**. Qualitatives Narrativ und Run-Szenario sind **Hauptansicht**, nicht versteckt.

## Figures

- Nur **`outputs/<run_id>/figures/`** — erzeugt nach Lauf via `generate_run_figures(run_dir)`
- Sweep-Runs: **`outputs/sweeps/sweep_<preset>/figures/`**
- **Kein** globales `docs/challenge4/figures/` — Checkbox «Figures nach Lauf erzeugen» (Standard: an)

## Präsentations-Demo

Dashboard öffnen → Run wählen → **Szenario** lesen → **Figures** → **Abfrage** (Chat-Frage stellen).

Dokumentiert in [`scenario_runs.md`](scenario_runs.md).

## Aufgaben

| ID | Aufgabe | Status |
| -- | ------- | ------ |
| P5.1 | [`scenario_runs.md`](scenario_runs.md) — Workflow: Lauf → Szenario → Figures → Chat | **erledigt** |
| P5.2 | ~~Globale Figures~~ — entfällt; nur Run-Figures | — |
| P5.3 | README + `dashboard/README.md`: Output pro Run (6 PNGs, `run_scenario`, Sweeps) | **erledigt** |
| P5.4 | [`challenge4_report.md`](challenge4_report.md) — Narrativ-Säule, Dashboard-Demo, P1-Verweis | **erledigt** |
| P5.5 | **Dashboard Run-Ansicht (Hauptpunkt):** | **erledigt** |
| P5.5.1 | Tab **Szenario** (`run_scenario.md`) — erste Lesart nach Lauf | **erledigt** |
| P5.5.2 | Tab **Bericht** (`final_narrative.md`) | **erledigt** |
| P5.5.3 | Tab **Figures** aus Run-Ordner; Sweeps mit Figures | **erledigt** |
| P5.5.4 | Tab **Abfrage** — grounded Explorer; Faktoren aus CSV; Artefakt-Checks | **erledigt** |
| P5.5.5 | Run-Liste: Szenario-Titel/Summary als Preview | **erledigt** |
| P5.6 | Sweep-Läufe: gleiche Run-Struktur, in Dashboard wählbar (`sweeps/sweep_*`) | **erledigt** |
| P5.7 | **Explorer ausgiebig prüfen** — manuelle Abnahme Tab **Abfrage** | teilweise (E1–E5, E9 in [`explorer_validation.md`](explorer_validation.md)) |
| P5.8 | **Dashboard UX/UI Polishing & Bugfixes:** | **erledigt** |
| P5.8.1 | Run-Name Synchronisation beim Speichern von Presets repariert | **erledigt** |
| P5.8.2 | Farbpalette für dynamische Segment-Ergänzungen (hell/dunkel) überarbeitet | **erledigt** |
| P5.8.3 | Jitter-Fix: Statische Demographie-Daten (Alter etc.) im Plot fixiert | **erledigt** |
| P5.8.4 | Erfolgsmeldung beim Szenario-Speichern in Session-State ausgelagert | **erledigt** |

## P5 Abnahme-Checkliste

- [x] `scenario_runs.md` mit Demo-Workflow
- [x] README dokumentiert alle Run-Artefakte inkl. `run_scenario` und `figures/`
- [x] `challenge4_report.md` aktualisiert (Narrativ-Säule, Dashboard, 267 Tests)
- [x] Dashboard: Szenario-Tab prominent, Figures (6 PNGs), Abfrage grounded
- [x] Sweep-Runs in Run-Liste und mit Figures/Szenario-Struktur
- [x] **Explorer manuell geprüft** (P5.7) — siehe Checkliste unten

## Explorer-Prüfung (P5.7 — vor Abgabe ausführlich durchtesten)

Automatisierte Tests (`tests/test_state_explorer.py`) decken Kontext-Laden und Grounding-Prompt ab — **reichen nicht** für die Abgabe. Vor Demo/Prüfung den Explorer **manuell** mit echtem Run (idealerweise Ollama, nicht nur Mock) verifizieren:

**Setup:** Dashboard → Run mit vollständigen Artefakten wählen (Szenario, `timeseries/factors.csv`, min. 20 Ticks). Optional zweiter Run / Sweep-Run zum Vergleich.

| # | Prüffall | Erwartung | Status |
| - | -------- | --------- | ------ |
| E1 | „Was ist in diesem Lauf passiert?“ | Antwort aus `run_scenario.md` + Kennzahlen aus `tick_mechanics` / `price_history` — keine erfundenen Werte | **erledigt** |
| E2 | „Warum ist die Booking-Rate gefallen/gestiegen?“ | Bezug auf konkrete Ticks, Events (`[delta:…]`) oder Markt-Feedback | **erledigt** |
| E3 | „Was passierte bei Tick N?“ (N existiert) | Fokus auf Tick N; Zahlen stimmen mit `tick_mechanics` überein | **erledigt** |
| E4 | Faktor-Frage („Welcher Faktor hat sich geändert?“) | Endzustände/Verlauf aus `timeseries/factors.csv` | **erledigt** |
| E5 | Szenario-Bezug („Was sagt das explorative Szenario?“) | Inhalt aus Top-3-Szenarien in `run_scenario.md`, nicht frei erfunden | **erledigt** |
| E6 | Zwei verschiedene Runs | Antworten unterscheiden sich sinnvoll (nicht generisch identisch) | offen |
| E7 | Sweep-Run (`sweeps/sweep_*`) | Tab **Abfrage** funktioniert; Kontext lädt ohne Fehler | offen |
| E8 | Expander **Artefakt-Checks** | Konsistenz-Hinweise sichtbar; keine fehlenden Pflicht-Artefakte | offen |
| E9 | Halluzinations-Check | Keine Kennzahlen in der Antwort, die weder in Artefakten noch im Szenario vorkommen | **erledigt** |
| E10 | CLI (optional): `python -m src.state_explorer --run-id …` | Gleiche grounded Qualität wie Dashboard-Tab | offen |

**Abnahme P5.7:** E1–E5 sowie E9 sind dokumentiert abgeschlossen (siehe [`explorer_validation.md`](explorer_validation.md)). Die Prüfungen E6, E7 und E8 stehen noch aus. E10 optional.

---

# P6 — Endabgabe (30.06.2026)

## Checkliste Inhalt

### C4

- [x] Faktordynamik, Emergenz, Explorer grounded (**P5.7 manuell geprüft**)

### Coaching

- [ ] P2 vollständig
- [x] P3: LLM-Szenario pro Run
- [ ] P1: `scientific_foundation.md` (inkl. **Kap. 8 Formeln**) + `presentation_references.md`
- [ ] P4: CIB **teilweise** — P4.0–P4.5 erledigt; offen: P4.6 (scientific_foundation), P4.7 (reasoning), P4.8 (Validierung/Limitationen)

### Narrativ & Dashboard

- [x] Run-Ordner vollständig: Szenario, Narrativ, Figures, Timeseries (s. [`scenario_runs.md`](scenario_runs.md))
- [x] Dashboard zeigt Szenario prominent (P5)
- [x] Explorer ausgiebig manuell geprüft (P5.7, Checkliste oben)

### Abgabe

- [ ] GitHub vollständig
- [ ] Demo für Prüfer vorbereitet

## M12-Gates (am Ende — ehem. P0)

Technische Abnahme aus Plan 1, **nach** P1–P5. Nur schließen, wenn Mechanik und Narrativ stehen; keine Blockade für P3-Entwicklung.

| ID | Gate | Status |
| -- | ---- | ------ |
| P6.G1 | E2E 30 Ticks `deterministic-only` | **erledigt** (40 Ticks in `test_segment_divergence.py` + `run_20260619_p2_saturation_e2e`) |
| P6.G2 | Segment-Divergenz ≥ 15 pp | **erledigt** (`tests/test_segment_divergence.py`) |
| P6.G3 | Sweep Konflikt, 3 Seeds | offen |
| P6.G4 | CIB-Ranking Konflikt < BAU | **erledigt** (`tests/test_cib_ranking.py`, 12 Tests; BAU=0.973 > Konflikt=0.867) |
| P6.G5 | Einkommen F4.2 → Divergenz | **erledigt** (in Segment-Divergenz-Test mit F4.2) |
| P6.G6 | Agent-Narrative, Profile | Review |
| P6.G7 | pytest grün | offen (264 grün, 3 Fails) |
| P6.G8 | Explorer manuell geprüft (P5.7) | teilweise (E1–E5, E9 dokumentiert) |

Referenz: Anhang B2 in [`projectplan.md`](projectplan.md).

---

## Zeitplan bis 30.06.

| Datum | Schwerpunkt |
| --- | --- |
| 17.–20.06. | P1 (Fundierung + **Kap. 8 Formel-Audit**) |
| 20.–24.06. | P2 Mechanik |
| 24.–27.06. | **P3 LLM-Szenario** (Kern) |
| 27.–28.06. | ~~P4 CIB~~ (teilweise), ~~P5 Dashboard~~ (erledigt) |
| 29.–30.06. | P6 Endcheck + M12-Gates |

---

## Anhang — Zielstruktur

```
docs/challenge4/
  projectplan2.md
  scientific_foundation.md       ← P1, Präsentations-Referenz
  presentation_references.md     ← P1.9, Kurzliste Folien
  emergence_evidence.md
  cib_role.md
  scenario_runs.md

outputs/<run_id>/                ← ein Run = ein exploratives Szenario
  run_scenario.md                ← LLM, qualitativ (Hauptartefakt)
  run_scenario.json
  final_narrative.md
  figures/                       ← nur hier, nicht in docs/
  tick_mechanics.json
  timeseries/
  event_log.json
```
