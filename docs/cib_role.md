# Rolle der Cross-Impact-Balance-Analyse im System

> ## Diese Rolle gibt es nicht mehr
>
> **Abgewählt am 2026-08-29, ersetzt am 2026-08-31.** Die CIB-Schicht bewertet nichts
> mehr im Modell:
>
> - Mit [P2.0](projektplan.md#p20--die-rolle-umdrehen-rahmen-statt-urteil) ist ein
>   Szenario ein benanntes Bündel **exogener Verläufe**; F1–F7 werden aus dem Lauf
>   *abgeleitet* statt ihn zu bewerten.
> - Mit [P2.2](projektplan.md#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31)
>   ist **Variante C** gewählt: Die Kohärenz eines Rahmenszenarios wird in **Prosa mit
>   Quellen** begründet. Es gibt keinen Algorithmus, der sie prüft — die Impact Balance
>   wird nicht implementiert.
>
> **Warum `configs/cib_frozen.json` trotzdem im Repo liegt:** Sie ist ein **Beleg, kein
> Werkzeug.** Die Datei trägt die vier Messwerte, auf denen die Abwahl steht — der Score
> korreliert mit **+0,56** mit der Zahl gleichpolig gesetzter Faktoren, nur **12** von 84
> gleichpoligen Zellen tragen Spannung, das echte Impact-Balance-Kriterium trägt **2** von
> 128 Zuständen statt der drei, die das Produkt verspricht, und **vier** unbegründete
> Zellen verneinen die Rückkopplung, aus der gemischte Szenarien entstehen. Wer die Datei
> löscht, löscht den Beleg. `tests/test_cib_einachsigkeit.py` hält alle vier fest.
>
> **Und eine fachliche Abnahme ist nicht mehr vorgesehen.** Bis zum 2026-08-31 trug
> `metadata.source` das Label `llm_proposed_pending_review_v3` — es kündigte eine Prüfung
> an, die niemand mehr vorhat, weil sie Werte prüfen würde, die nichts entscheiden. Das
> Label heißt jetzt `beleg_keine_bewertende_rolle`, und die Notiz in der Datei sagt es
> ausdrücklich ([P2.3-Rest](projektplan.md#p23--matrix-provenienz-herstellen--entfällt-seit-2026-08-31-ein-rest-bleibt)).
>
> **Was unterhalb dieses Kastens steht, beschreibt die abgewählte Rolle** — es bleibt als
> Herleitung stehen, nicht als Beschreibung des heutigen Verhaltens. Zahlen und Argumente:
> [`entscheidung_szenarienschicht_2026-08-29.md`](entscheidung_szenarienschicht_2026-08-29.md).

> Anwendernahe Fassung im Dashboard unter «Dokumentation → CIB-Konsistenzprüfung».

> Referenz: Weimer-Jehle, W. (2023). *Einführung in die Cross-Impact-Bilanzanalyse (CIB):
> Wege zur qualitativen System- und Szenarioanalyse.*

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

Eine Faktor-Konstellation gilt nach der Methode als **konsistent**, wenn jeder Deskriptor in
dem Zustand steht, den seine eingehende Einflussbilanz empfiehlt (Impact Balance).

> **Was der Code stattdessen tut:** `ConsistencyChecker.check_scenario` prüft **einzelne
> Zellen** gegen einen Schwellwert (`≤ −1.5` gilt als Konflikt) und summiert die Konflikte;
> `compute_consistency_score` bildet das Verhältnis positiver zu allen Einflüssen. Beides
> ist eine eigene Heuristik, nicht die Impact Balance. Solange [P2.2](projektplan.md#p22--die-szenarienschicht-endgültig-festlegen)
> offen ist, gehört sie nicht als „Algorithmus nach Weimer-Jehle" bezeichnet.

## Warum CIB in diesem Projekt?

Das System modelliert das soziotechnische System **Luftfahrt** mit 7 Faktoren (F1–F7) und je
zwei Zuständen. Die Faktoren beeinflussen sich gegenseitig — eine Simulation kann dadurch in
Konstellationen enden, die intern widersprüchlich sind (z.B. strenge Regulierung F2.2 ohne
Technologiedurchbruch F3.1, während gleichzeitig die Wirtschaft schrumpft F4.2).

CIB leistet hier drei Dinge:

1. **Widerspruchsfreiheits-Bewertung** (F-CIB1 — Consistency Score):
   Jeder Simulationslauf wird am Ende mit `scenario_consistency.py` bewertet. Der Score
   (0–1) gibt an, wie gut die erreichten Faktorzustände zur Referenz-CIB-Matrix passen.

   > **Am 2026-08-29 nachgemessen — der Score misst Polarität, nicht Plausibilität.**
   > Über alle 128 Systemzustände hängt er fast nur davon ab, wie einheitlich die Faktoren
   > gepolt sind: Korrelation **+0,56** mit der Zahl gleichpoliger Faktoren, über die vier
   > Gruppen monoton (Mittel 0,499 → 0,562 → 0,682 → 0,853). Der Grund liegt in der Matrix:
   > Nur 12 der 84 gleichpoligen Zellen tragen Spannung, sie ist im Kern eine einzige Achse.
   > **Ein Score nahe 1 bedeutet also ein einheitlich gepoltes Weltbild, nicht ein
   > plausibles** — die realistischen Mischlagen werden systematisch abgewertet.

2. **Kandidaten-Generierung** (Szenarioentwicklung):
   `run_scenario_generator.py` erzeugt aus dem Simulationsendzustand eine Menge
   CIB-bewerteter Kandidaten-Konstellationen. Das LLM wählt daraus 3 Szenarien aus und
   begründet seine Auswahl. Die numerischen Faktor-Werte bleiben damit immer Python-geerdet —
   das LLM erfindet keine Zustände, sondern interpretiert vorgegebene CIB-konsistente
   Konstellationen.

3. **Sweep-Validierung** (Archetypen-Ranking):
   Die drei Sweep-Presets replizieren die CIB-Beispielszenarien der Referenzmethodik.
   Ein quantitativer Test (`tests/test_cib_ranking.py`) prüft, dass das Ranking der Scores
   der theoretischen Erwartung entspricht.

## CIB im Systemüberblick

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Simulation                                                             │
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

> **Sie entscheidet seit dem 2026-08-31 nichts mehr** — siehe den Kasten oben. Was hier
> folgt, beschreibt ihren Aufbau, weil sie als Beleg im Repo bleibt.

Die Referenz-CIB wurde deterministisch mit Seed 42 erzeugt und ist **eingefroren**
(`"frozen": true`). **`entries` ist mit dem 2026-08-31 daraus entfernt worden**: eine
durchgängig leere Liste neben den 168 Zellen, die kein Lesepfad füllte oder auswertete —
wer die Datei zum ersten Mal öffnete, sah zwei Strukturen und musste raten, welche die
eigentliche ist. Sie enthält 14 Deskriptoren (F1.1, F1.2, …, F7.1, F7.2) mit
168 Cross-Factor-Zellen (14×14 − 7×4 Diagonal-Blöcke)..

Active/Passive-Scores aus der Matrix (Faktor-Wichtigkeit):

| Faktor | Active Score | Passive Score | Interpretation |
|--------|-------------|---------------|----------------|
| F1 Mobilitätsnachfrage | 41 | 47 | Aktiv und zugleich am stärksten beeinflussbar |
| F2 Regulierung         | 47 | 37 | Stärkstes aktives Element — zentraler Steuerungsfaktor |
| F3 Technologie (SAF)   | 33 | 33 | Ausgeglichen — reagiert und wirkt in gleichem Maß |
| F4 Wirtschaft          | 38 | 40 | Hohe Gesamtwirkung, beide Richtungen |
| F5 Alternativen        | 24 | 39 | Stark abhängig, wenig aktiv |
| F6 Gesellschaft        | 42 | 39 | Aktiv und passiv stark |
| F7 Geopolitische Stabilität | 29 | 19 | Wirkt nach außen, wird kaum zurückbeeinflusst — exogen |

Die Zahlen stammen aus `factor_scores` in `configs/cib_frozen.json` und werden von
`scripts/rebuild_cib_frozen.py` mitberechnet. **Korrigiert am 2026-08-26:** Die
frühere Tabelle stimmte mit keiner einzigen Zeile — sie war irgendwann von Hand
eingetragen und nie nachgezogen worden. Der niedrige Passive-Score von F7 ist
kein Fehler, sondern das erwartete Bild eines exogenen Faktors (siehe P0.2).

## Empirisches Ranking der drei Sweep-Archetypen

Berechnet mit `scenario_consistency.ConsistencyChecker` auf `cib_frozen.json`
(verifiziert durch `tests/test_cib_ranking.py`):

| Szenario | Consistency Score | Stability Index | Konflikte |
|----------|:-----------------:|:---------------:|:---------:|
| Business as Usual (A1+B1) | **0.970** | **1.000** | 0 |
| Transformationskonflikt (B2 vs A1) | 0.867 | 0.952 | 2 |
| Freiwillige Wende (A2+B2) | 0.629 | 0.833 | 7 |

Das Ranking BAU (0.970) > Transformationskonflikt (0.867) > Freiwillige Wende (0.629) ist
stabil und wird von `tests/test_cib_ranking.py` gehalten; die Neubewertung der F7-Zellen in
P0.2 hat daran nichts geändert.

> **Was es belegt — und was nicht (2026-08-29).** Der Rang war bis dahin als *Kernnachweis*
> geführt, also als Beleg dafür, dass die Bewertung Plausibilität erkennt. Das trägt er
> nicht. Die drei Zahlen fallen exakt auf die Polaritätsleiter: **BAU (0.970)** ist der
> **vollständig gleichpolige** Zustand (7 von 7), **Konflikt (0.867)** liegt bei 6 von 7,
> und die **Wende (0.629)** wird abgewertet, **weil** sie gemischt ist. Der Test ist
> korrekt — er misst, was er misst. Falsch war nur die Deutung: Er zeigt, dass die
> Bewertung einheitlich gepolte Weltbilder bevorzugt, nicht dass sie plausible erkennt.

BAU ist das perfekt selbstverstärkende Szenario (0 Konflikte, Stability = 1.0). Alle
Faktorkombinationen in BAU unterstützen sich gegenseitig — es ist zugleich einer der beiden
Zustände, die das echte Impact-Balance-Kriterium erfüllt. Der andere ist sein Gegenpol.
**Ein drittes konsistentes Szenario gibt es unter diesem Kriterium nicht**, das
Produktversprechen «Tripleset» ist daraus nicht bedienbar; deshalb kommt es künftig aus der
Wahl der Rahmenszenarien (P2.0) statt aus einem Ranking.

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

Die Einfluss-Werte in `cib_frozen.json` sind domänenspezifisch gesetzt und nicht zufällig
generiert (z.B. `F2.2→F3.2: +3`: Strenge Regulierung treibt Technologiedurchbruch;
`F6.2→F2.1: -3`: Flight Shaming untergräbt moderate Politik).

> **Eingefroren heißt nicht belegt (2026-08-29).** Von den 168 Zellen tragen **48** eine
> Begründung — ausgerechnet die, die als *prüfbedürftig* markiert sind (die F7-Zellen aus
> P0.2). Die übrigen **120 tragen keine**, aber dasselbe `"frozen": true` und damit denselben
> Anspruch auf fachliche Geltung. Vier davon zeigen nachweislich in die falsche Richtung:
> `F1.1→F2.2`, `F1.1→F6.2`, `F1.1→F5.2` und `F4.1→F2.2` stehen auf −2 und behaupten, Nachfrage-
> und Wirtschaftswachstum **hemmten** strenge Regulierung, Flugscham und Schienenausbau. Real
> ist es umgekehrt — EU-ETS-Ausweitung, ReFuelEU, Ticketsteuern, das französische
> Kurzstreckenverbot und der Deutschlandtakt sind Reaktionen *auf* das Verkehrswachstum. Genau
> diese verneinte Rückkopplung ist der Grund für die Einachsigkeit weiter oben. Eingeplant als
> P2.3, gemessen in `tests/test_cib_einachsigkeit.py`.

Eine frühere Version (`CIBExtractorNode`, LLM + Heuristik) hatte versucht, die CIB-Matrix
dynamisch aus dem Event-Log zu extrahieren. Dieser Ansatz war eine Exploration, ist aber
methodisch problematisch (Matrix ändert sich je nach Lauf → kein stabiler Referenzwert).
Der Extractor liegt daher jetzt unter **`src/legacy/`** und ist nicht Teil der Pipeline.

## Weiterführende Dokumente

- `docs/entscheidung_szenarienschicht_2026-08-29.md` — warum diese Rolle abgewählt wurde
- `tests/test_cib_einachsigkeit.py` — die vier Messwerte, auf denen die Entscheidung steht
- `docs/cib_rationale.md` — CIB-Kanten-zu-Regel-Mapping
- `configs/cib_frozen.json` — Vollständige Referenz-Matrix
- `src/cib/scenario_consistency.py` — Score-Implementierung (F-CIB1/2/3)
- `tests/test_cib_ranking.py` — Quantitativer Nachweis P4.3/P4.5
- `tests/test_scenario_consistency.py` — Score-Unit-Tests
