# Project Plan – Challenge 3

Simulation statischen und erwartbaren Verhaltens.

Weiterentwicklung des C2-Prototyps zu einer vollständigen Simulation mit CIB-Matrix, Gesprächsprotokoll und Szenarioableitung.

Was C3 liefern muss:
- Repräsentation der 7 Einflussfaktoren mit Stärke (-3 bis +3) und Wechselwirkungen
- Vollständige CIB-Matrix (7 Faktoren x 2 Zustände = 14x14)
- Agentisches Gesprächsprotokoll als Simulationsstand
- Ableitung konsistenter Szenarien aus CIB-Matrix + Protokoll


## Feedback C2-Präsentation (14.05.)

| Feedback | Umsetzung |
|----------|-----------|
| Quartale statt Jahre | `tick_unit` = Quartal (Q1 2026 – Q4 2035) |
| Bei Abbruch weitermachen | Checkpoint/Resume |
| CIB-Matrix besser darstellen | 14x14 mit -3/+3 Skala + Visualisierung |
| Nur 1 Simulation → mehr Durchläufe | Multi-Run (5-10 Runs, verschiedene Seeds) |
| Szenarien aus CIB generieren | Szenario-Agent |
| Population dynamisch, überlappend | EnvironmentAgent steuert Populationsentwicklung |


## Designentscheidungen

### Memory: Nein

Kein Memory für Agenten in C3. Die Simulation bildet statisches Verhalten ab – Agenten entscheiden auf Basis der aktuellen Faktor-Zustände und CIB-Matrix, nicht auf Basis vergangener Gespräche. Memory würde Reproduzierbarkeit kaputt machen und ist erst für C4 (adaptives Verhalten) relevant.

Checkpoint/Resume ist kein Agent-Memory, sondern State-Persistenz für Wiederaufnahme nach Abbruch.

### Einflussfaktoren: dynamisch

Die Wechselwirkungsstärken zwischen Faktoren werden nicht einmalig festgelegt, sondern durch die Agenten-Diskussion iterativ bestimmt. Die CIB-Matrix aktualisiert sich pro Runde basierend auf dem Agenten-Konsens. Änderungen werden dokumentiert. Begrenzung: max. ±1 pro Wert pro Runde.

### Config: dynamisch

Simulationsparameter sind zur Laufzeit anpassbar:
- EnvironmentAgent kann Szenario-Parameter pro Runde ändern (z.B. Regulierungsintensität)
- Jeder Multi-Run kann eigene Config-Overrides mitbringen
- Alle Änderungen werden mit Zeitstempel geloggt

### Bevölkerungsdynamik: EnvironmentAgent entscheidet

Anfangswerte (Segmentanteile) sind fest in der Config definiert. Die Entwicklung über die Runden entscheidet der EnvironmentAgent – keine Regel-Engine, sondern LLM-basierte Entscheidung mit Begründungspflicht.

- Inputs: Faktor-Zustände, CIB-Matrix, bisherige Entwicklung
- Outputs: neue Segmentanteile + Begründung
- Segmente können überlappen (Geschäftsreisender + umweltbewusst)
- Max. 5% Verschiebung pro Segment pro Runde

### Redebedarf-Score: Dynamische Sprechreihenfolge

Kein Round-Robin. Ein deterministischer Score (0–10) bestimmt, wer wann und wie oft spricht.

Trigger:
- Faktor-Relevanz (+2 bis +3): anderer Agent verändert Faktor im eigenen Bereich
- Widerspruch (+2): eigene Einschätzung weicht von Diskussion ab
- Stillstand (+1 pro übersprungene Runde): verhindert Schweigen
- Nach Sprechen: Reset auf 0

Ablauf pro Runde:
1. Scores berechnen (aus letzter Runde)
2. Agenten absteigend sortieren → Sprechliste
3. Agent kann mehrfach sprechen wenn Score erneut Schwelle überschreitet
4. Max. 3 Beiträge pro Agent pro Runde
5. Schwellenwert: Redebedarf ≥ 3

Reproduzierbarkeit: Berechnung ist deterministisch. Bei Gleichstand entscheidet alphabetische Agent-ID. Gleiche Ausgangsbedingungen → gleiche Reihenfolge.


## Team

| Person | AP | Fokus |
|--------|-----|-------|
| Marc | AP1 | CIB-Matrix, Einflussfaktor-Repräsentation, Visualisierung |
| Manuel | AP2 | Gesprächsprotokoll, Prompt-Verbesserung, Szenario-Agent |
| Haiko | AP3 | Multi-Run, Checkpoint, Zeitmodell, Redebedarf-Scheduler |
| Jonas | AP4 | Szenario-Ableitung, EnvironmentAgent, Testing, Doku |


## Zeitplan (Deadline: 02.06.2026)

| KW | Zeitraum | Meilenstein |
|----|----------|-------------|
| 21 | 14.–18.05. | M0: Kickoff, Interface-Design |
| 21 | 19.–21.05. | M1: Interfaces eingefroren |
| 22 | 22.–25.05. | M2: Kern-Implementierung (je AP mit Mock-Daten) |
| 23 | 26.–28.05. | M3: Integration (End-to-End) |
| 23 | 29.05.–01.06. | M4: Validierung + Doku |
| 23 | **02.06.** | Abgabe |


## Arbeitspakete

### AP1 – CIB-Matrix & Einflussfaktoren (Marc)

14x14 CIB-Matrix mit -3/+3 Skala. LLM-basierte Bewertung statt Heuristik. Iterative Aktualisierung pro Runde (Delta max. ±1). Aktiv-/Passiv-Score pro Faktor. Visualisierung als Heatmap + Netzwerkdiagramm. Validierung gegen Referenz-CIB.

Deliverables:
- `src/nodes/cib_extractor_node.py`
- `src/models/cib_models.py`
- `src/cib_visualizer.py`
- `docs/challenge3/cib_format.md`

Braucht: Event-Log aus AP3, CIB-Format in M1 einfrieren.

### AP2 – Gesprächsprotokoll & Szenario-Agent (Manuel)

Strukturiertes Protokoll pro Simulationslauf: wer sagt was, warum, mit welchem Impact. Redebedarf-Score pro Beitrag dokumentiert. Szenario-Agent der aus fertiger CIB-Matrix 2-3 konsistente Szenarien mit Narrativ ableitet. Prompts überarbeiten damit Agenten expliziter über Einflussstärken argumentieren.

Deliverables:
- `src/protocol_generator.py`
- `src/nodes/scenario_agent_node.py`
- Überarbeitete Prompts in `src/prompts/`
- `docs/challenge3/protocol_format.md`

Braucht: CIB-Format aus AP1, Multi-Run aus AP3. Kann mit C2-Mock-Daten starten.

### AP3 – Multi-Run, Checkpoint, Zeitmodell & Redebedarf (Haiko)

Multi-Run: N Durchläufe mit verschiedenen Seeds, Ergebnisse separat gespeichert, Aggregation über Runs. Checkpoint/Resume: State nach jeder Runde serialisieren, bei Abbruch fortsetzen (`--resume`). Zeitmodell auf Quartale. Redebedarf-Scheduler: Score-Berechnung, Sprechlisten-Erstellung, Mehrfach-Sprechen. Dynamische Config: Laufzeit-Anpassung durch EnvironmentAgent mit Logging.

Deliverables:
- `src/simulation_runner.py`
- `src/redebedarf_scheduler.py`
- `src/checkpoint_manager.py`
- `configs/simulation_config.json`
- `docs/challenge3/multi_run_guide.md`

Braucht: Grundstruktur aus C2, Faktor-Zuordnungen aus AP1 für Redebedarf-Treiber.

### AP4 – Szenarien, EnvironmentAgent & Testing (Jonas)

Szenario-Konsistenzprüfung: aus CIB-Matrix konsistente Zustandskombinationen ableiten, Top-N identifizieren. EnvironmentAgent: entscheidet Populationsverschiebungen pro Runde (LLM-basiert, begründet, max. 5%/Segment, überlappende Segmente). Testing: CIB-Validierung, Multi-Run-Stabilität, Checkpoint, Szenario-Plausibilität, Protokoll-Vollständigkeit. Doku: C3-Report, Traceability C2→C3.

Deliverables:
- `src/scenario_consistency.py`
- `src/nodes/environment_agent_node.py`
- `tests/test_cib_matrix.py`
- `tests/test_multi_run.py`
- `tests/test_checkpoint.py`
- `tests/test_scenario_derivation.py`
- `tests/test_environment_agent.py`
- `docs/challenge3/challenge3_report.md`

Braucht: CIB-Output aus AP1, Multi-Run aus AP3, Szenario-Agent aus AP2.


## Integration

Branches: `feature/ap1-cib-matrix`, `feature/ap2-protocol-scenario`, `feature/ap3-multirun-checkpoint`, `feature/ap4-scenarios-testing`

Merge-Punkte:
- M1: Datenmodelle + Interfaces
- M2: Kern-Implementierungen (separat)
- M3: Alles zusammen
- M4: Tests + Docs

### Done wenn:

- [ ] CIB-Matrix 14x14, -3/+3, wird iterativ pro Runde aktualisiert
- [ ] Einflussfaktor-Stärken dargestellt (Aktiv/Passiv)
- [ ] Gesprächsprotokoll pro Lauf
- [ ] Mind. 5 Runs mit verschiedenen Szenarien
- [ ] Mind. 3 konsistente Szenarien abgeleitet
- [ ] Checkpoint/Resume funktioniert
- [ ] Quartals-Zeitmodell
- [ ] Config dynamisch durch EnvironmentAgent
- [ ] Populationsdynamik durch EnvironmentAgent (fest → dynamisch)
- [ ] Redebedarf-Score steuert Sprechreihenfolge (deterministisch)
- [ ] Kein Agent-Memory (bewusste Entscheidung)
- [ ] Tests grün, Doku fertig
