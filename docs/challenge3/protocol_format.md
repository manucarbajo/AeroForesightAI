## Gesprächsprotokoll – Format (Challenge 3 / AP2)

Dieses Dokument beschreibt das Ausgabeformat des Gesprächsprotokolls, das aus dem Simulationsstate (`SimulationState`) erzeugt wird.

### Dateien

- `outputs/protocol.json`: strukturiertes Protokoll (maschinenlesbar)
- `outputs/protocol.md`: lesbare Kurzform (Markdown)

### JSON Top-Level

`protocol.json` ist ein JSON-Objekt mit folgenden Feldern:

- `protocol_version` (string): aktuell `"1.0"`
- `generated_at` (string): ISO-8601 Zeitstempel (UTC, `...Z`)
- `run` (object): Metadaten des Runs
- `agents` (array): Agenten-Metadaten (id, name, type, goals, constraints)
- `rounds` (array): Runden mit Beiträgen und Events
- `final_environment` (object): finaler Faktor-Zustand
- `cib` (object|null): finaler CIB-Matrix Dump (falls vorhanden)

### Runden & Beiträge

`rounds[]`:

- `round_number` (int)
- `contributions[]`: Beiträge in Append-Reihenfolge der Simulation
- `events[]`: alle Events dieser Runde (aus `state.event_log`)

`contributions[]`:

- `agent_id` (string)
- `round_number` (int)
- `why` (string): erste Zeile aus `reasoning` (kurzer Summary-Satz)
- `reasoning` (string): vollständige Begründung
- `actions` (string[])
- `state_changes` (array): Liste von `{ factor_id, proposed_state, reasoning }`
- `events` (array): Events, die zu diesem Agent-Beitrag gehören
- `impact` (object):
  - `affected_factors` (string[]): union aus `state_changes.factor_id` und `events.affected_factors`
  - `impact_assessment` (array): optional, frei strukturiert (vom Agent gelieferte CIB-Argumentation)
- `redebedarf_score` (number|null): Platzhalter für AP3 (Scheduler)
- `segment_analysis` (object): Segment-Analysen (aktuell nur Consumer)

### Events

Jedes Event in `events[]` (rundeweit oder beitragsspezifisch) hat:

- `id` (string)
- `round_number` (int)
- `source_agent` (string)
- `event_type` (string)
- `description` (string)
- `affected_factors` (string[])
- `timestamp` (string)

### Notes / Erweiterbarkeit

- Das Protokoll ist **append-only erweiterbar**: neue Felder können ergänzt werden, ohne bestehende Auswertung zu brechen.
- `redebedarf_score` ist absichtlich `null`, bis AP3 die deterministische Score-Berechnung integriert.

