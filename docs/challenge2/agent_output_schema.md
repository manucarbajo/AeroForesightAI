# Agent Output Schema (AP2)

## Ziel
Dieses Schema definiert ein parserfreundliches Standardformat fuer alle drei MVP-Agenten (`consumer`, `provider`, `regulator`).
Der Parser in `src/nodes/agent_node.py` verarbeitet rohe LLM-Antworten zu:
- `AgentResponse`
- `EventLogEntry[]`

## Erwartetes JSON-Format
```json
{
  "reasoning": "Kurzbegruendung der Entscheidung",
  "actions": [
    "Konkrete Aktion 1",
    "Konkrete Aktion 2"
  ],
  "state_changes": [
    {
      "factor_id": "F1",
      "proposed_state": "F1.2",
      "reasoning": "Warum dieser Wechsel plausibel ist"
    }
  ],
  "events": [
    {
      "event_type": "demand_shift",
      "description": "Beschreibt das Ereignis praezise",
      "affected_factors": ["F1", "F5"]
    }
  ],
  "segment_analysis": {
    "business": "string"
  }
}
```

## Feldregeln
- `reasoning`: Pflicht, nicht leerer String.
- `actions`: Pflichtliste, bei fehlender Angabe wird auf `["NO_OP"]` normalisiert.
- `state_changes`: optionale Liste.
  - `factor_id` muss einer bekannten Faktor-ID entsprechen (`F1` ... `F7`).
  - `proposed_state` muss als Zustands-ID angegeben werden (z.B. `F2.2`).
- `events`: optionale Liste.
  - `event_type` bevorzugt Werte aus `EventType`:
    - `price_change`
    - `regulation`
    - `demand_shift`
    - `investment`
    - `policy_change`
    - `market_event`
    - `technology_shift`
  - `affected_factors` wird auf bekannte Faktoren gefiltert.
- `segment_analysis`: optionales Objekt (Consumer liefert es, Provider/Regulator sollen `{}` liefern)
  - Key: `segment_id`
  - Value: `string` (Kurzbegruendung/erwartete Segmentreaktion)

## Parse- und Fallback-Strategie
- Der Parser akzeptiert:
  - direktes JSON
  - JSON in Markdown-Codeblock
  - eingebettetes JSON innerhalb von Freitext (erstes gueltiges Objekt)
- Bei Parse-Fehler:
  - `AgentResponse` wird als Fallback mit `NO_OP_PARSE_FALLBACK` erzeugt
  - `segment_analysis` wird auf `{}` gesetzt
  - ein Default-Event wird agententypabhaengig erzeugt:
    - Consumer -> `demand_shift`
    - Provider -> `price_change`
    - Regulator -> `policy_change`

## Beispielantworten

### Consumer
```json
{
  "reasoning": "Steigende Preise und bessere Bahnverbindungen reduzieren Freizeitflugnachfrage.",
  "actions": ["Freizeitfluege reduzieren", "Kurzstrecke auf Bahn verlagern"],
  "state_changes": [
    {
      "factor_id": "F1",
      "proposed_state": "F1.2",
      "reasoning": "Nachfrage zeigt Substitutionsmuster."
    }
  ],
  "events": [
    {
      "event_type": "demand_shift",
      "description": "Freizeitreisende verschieben Buchungen auf Alternativen.",
      "affected_factors": ["F1", "F5"]
    }
  ],
  "segment_analysis": {
    "leisure_price_sensitive": "Hohe Preise stoeren preissensitive Segmente besonders; Substitution Richtung Bahn/Wettbewerb.",
    "business": "Geschaeftsreisende reagieren weniger preissensitiv, daher kleinere Nachfrageverschiebung."
  }
}
```

### Provider
```json
{
  "reasoning": "Kostendruck erfordert Tarifanpassung bei gleichzeitiger Effizienzsteigerung.",
  "actions": ["Preise im Peak-Segment erhoehen", "SAF-Pilotroute priorisieren"],
  "state_changes": [
    {
      "factor_id": "F3",
      "proposed_state": "F3.2",
      "reasoning": "Investitionen beschleunigen Lernkurve."
    }
  ],
  "events": [
    {
      "event_type": "price_change",
      "description": "Airline passt Tarife differenziert nach Segmenten an.",
      "affected_factors": ["F1", "F3", "F4"]
    }
  ]
}
```

### Regulator
```json
{
  "reasoning": "Klimaziele werden verfehlt; ein verbindlicherer Policy-Rahmen ist erforderlich.",
  "actions": ["CO2-Preisband anheben", "Foerderfenster fuer SAF ausbauen"],
  "state_changes": [
    {
      "factor_id": "F2",
      "proposed_state": "F2.2",
      "reasoning": "Regulatorische Strenge nimmt zu."
    }
  ],
  "events": [
    {
      "event_type": "policy_change",
      "description": "Neue Dekarbonisierungsauflagen fuer Kurz- und Mittelstrecke.",
      "affected_factors": ["F2", "F3", "F6"]
    }
  ]
}
```
