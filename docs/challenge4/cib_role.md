# Rolle der Cross-Impact-Balance-Analyse im System

> Referenz: Weimer-Jehle, W. (2023). *Einführung in die Cross-Impact-Bilanzanalyse (CIB):
> Wege zur qualitativen System- und Szenarioanalyse.* (vgl. Aufgabenstellung Folie 21–22)

## Was ist CIB?

Die Cross-Impact-Balance-Analyse (CIB) ist eine strukturierte Methode aus dem Strategic Foresight,
um die **interne Konsistenz** von Faktor-Konstellationen zu bewerten. Sie fragt: Passen die
gleichzeitig aktiven Zustände mehrerer Einflussfaktoren logisch zusammen — oder widersprechen sie
sich gegenseitig?

Für jedes Faktorpaar (Quelle → Ziel) wird ein Einfluss-Wert auf der Skala −3 … +3 vergeben:

| Wert | Bedeutung |
|------|-----------|
| +3   | Starke Unterstützung (Quellzustand begünstigt Zielzustand stark) |
| +1   | Leichte Unterstützung |
|  0   | Kein Einfluss |
| −1   | Leichte Hemmung |
| −3   | Starke Hemmung (Quellzustand wirkt aktiv gegen Zielzustand) |

Eine Faktor-Konstellation gilt als **konsistent**, wenn die Summe der Einflüsse aller aktiven
Deskriptoren aufeinander positiv ist.

## Warum CIB in diesem Projekt?

Das System modelliert das soziotechnische System **Luftfahrt** mit 7 Faktoren (F1–F7) und je
zwei Zuständen. Die Faktoren beeinflussen sich gegenseitig — eine Simulation kann dadurch in
Konstellationen enden, die intern widersprüchlich sind (z.B. strenge Regulierung F2.2 ohne
Technologiedurchbruch F3.1, während gleichzeitig die Wirtschaft schrumpft F4.2).

CIB leistet hier drei Dinge:

1. **Plausibilitätsbewertung** (F-CIB1 — Consistency Score):
   Jeder Simulationslauf wird am Ende mit `scenario_consistency.py` bewertet. Der Score
   (0–1) gibt an, wie gut die erreichten Faktorzustände zur Referenz-CIB-Matrix passen.
   Ein Score nahe 1 bedeutet eine in sich stimmige Zukunftskonstellation.

2. **Kandidaten-Generierung** (P3 — Szenarioentwicklung):
   `run_scenario_generator.py` erzeugt aus dem Simulationsendzustand eine Menge
   CIB-bewerteter Kandidaten-Konstellationen. Das LLM wählt daraus 3 Szenarien aus und
   begründet seine Auswahl. Die numerischen Faktor-Werte bleiben damit immer Python-geerdet —
   das LLM erfindet keine Zustände, sondern interpretiert vorgegebene CIB-konsistente
   Konstellationen.

3. **Sweep-Validierung** (M8 — Archetypen-Ranking):
   Die drei Sweep-Presets replizieren die CIB-Beispielszenarien aus den Vorlesungsfolien.
   Ein quantitativer Test (`tests/test_cib_ranking.py`) prüft, dass das Ranking der Scores
   der theoretischen Erwartung entspricht.

## CIB im Systemüberblick

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Simulation (C4)                                                        │
│                                                                         │
│  Tick-Pipeline:  properties.json/factor_rules  →  Faktorzustände F1–F7 │
│                                                                         │
│  Am Laufende:   scenario_consistency.py         →  Consistency Score   │
│                                                                         │
│  P3:            build_candidate_constellations  →  CIB-Kandidaten Pool │
│                 (Python, deterministisch)                               │
│                  ↓                                                      │
│                 LLM wählt 3 aus 7+ Kandidaten   →  Szenario-Narrativ   │
│                                                                         │
│  Sweep-Tests:   configs/sweeps/*.json           →  test_cib_ranking.py │
└─────────────────────────────────────────────────────────────────────────┘

        ↑ Alle Score-Berechnungen referenzieren configs/cib_frozen.json
```

## Referenz-Matrix (`configs/cib_frozen.json`)

Die Referenz-CIB wurde deterministisch mit Seed 42 erzeugt und ist **eingefroren**
(`"frozen": true`). Sie enthält 14 Deskriptoren (F1.1, F1.2, …, F7.1, F7.2) mit
168 Cross-Factor-Zellen (14×14 − 7×4 Diagonal-Blöcke)..

Active/Passive-Scores aus der Matrix (Faktor-Wichtigkeit):

| Faktor | Active Score | Passive Score | Interpretation |
|--------|-------------|---------------|----------------|
| F1 Mobilitätsnachfrage | 37 | 30 | Aktiv beeinflussend, mittel beeinflussbar |
| F2 Regulierung         | 37 | 32 | Stark aktiv und passiv — zentraler Steuerungsfaktor |
| F3 Technologie (SAF)   | 36 | 40 | Stark beeinflussbar — reagiert auf Regulierung und Markt |
| F4 Wirtschaft          | 41 | 42 | Höchste Gesamtwirkung — treibt das gesamte System |
| F5 Alternativen        | 29 | 41 | Stark abhängig (von F6), wenig aktiv |
| F6 Gesellschaft        | 42 | 32 | Stärkstes aktives Element — beeinflusst alle anderen |
| F7 Marktstruktur       | 33 | 38 | Mittel aktiv, stärker beeinflussbar |

## Empirisches Ranking der drei Sweep-Archetypen

Berechnet mit `scenario_consistency.ConsistencyChecker` auf `cib_frozen.json`
(verifiziert durch `tests/test_cib_ranking.py`):

| Szenario | Consistency Score | Stability Index | Konflikte |
|----------|:-----------------:|:---------------:|:---------:|
| Business as Usual (A1+B1) | **0.973** | **1.000** | 0 |
| Transformationskonflikt (B2 vs A1) | 0.867 | 0.952 | 2 |
| Freiwillige Wende (A2+B2) | 0.603 | 0.810 | 8 |

**P4.3-Kernnachweis**: BAU (0.973) > Transformationskonflikt (0.867) ✓

BAU ist das perfekt selbstverstärkende Szenario (0 Konflikte, Stability = 1.0). Alle
Faktorkombinationen in BAU unterstützen sich gegenseitig.

Wissenschaftliche Randnotiz — warum Wende < Konflikt beim Consistency Score:
Die Freiwillige Wende hat 8 CIB-Konflikte, weil das Szenario selbst-untergrabende Dynamiken
enthält: F3.2 (SAF-Durchbruch) → F2.2 (−2) und F3.2 → F6.2 (−3): Sobald die Technologie
das Problem löst, werden strenge Regulierung und Flight Shaming überflüssig. Zusätzlich
spannen F4.1 (stabile Wirtschaft) und F7.1 (offene Märkte) gegen F2.2 (strenge Regulierung).
Der Transformationskonflikt hat trotz seines Namens nur 2 strukturelle Konflikte (F2.2+F3.1
und F4.2+F2.2), da die anderen Faktoren sich gut ergänzen.

## Warum die CIB-Matrix eingefroren ist — und das korrekt ist

Die Matrix ist absichtlich statisch. CIB-Methodik nach Weimer-Jehle definiert die
Cross-Impact-Matrix **vorab durch Domänenexperten** als Referenz-Brille. Sie darf sich
nicht aus Simulationsläufen ergeben — sonst würde man den Maßstab aus dem Messobjekt
ableiten (zirkulär).

Die Einfluss-Werte in `cib_frozen.json` sind domänenspezifisch und inhaltlich durchdacht
(z.B. `F2.2→F3.2: +3`: Strenge Regulierung treibt Technologiedurchbruch; `F6.2→F2.1: -3`:
Flight Shaming untergräbt moderate Politik). Sie wurden nicht zufällig generiert.

In Challenge 2/3 hatte `CIBExtractorNode` (LLM + Heuristik) versucht, die CIB-Matrix
dynamisch aus dem Event-Log zu extrahieren. Dieser Ansatz war eine Exploration, ist aber
methodisch problematisch (Matrix ändert sich je nach Lauf → kein stabiler Referenzwert).
In C4 liegt der Extractor daher unter **`src/legacy/`** und ist nicht Teil der Pipeline.

## Weiterführende Dokumente

- `docs/challenge4/cib_rationale.md` — CIB-Kanten-zu-Regel-Mapping
- `configs/cib_frozen.json` — Vollständige Referenz-Matrix
- `src/scenario_consistency.py` — Score-Implementierung (F-CIB1/2/3)
- `tests/test_cib_ranking.py` — Quantitativer Nachweis P4.3/P4.5
- `tests/test_scenario_consistency.py` — Score-Unit-Tests
