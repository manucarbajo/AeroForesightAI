# CIB-Matrix Format Spezifikation

## Überblick

Die Cross-Impact Balance (CIB) Matrix bildet die Wechselwirkungen zwischen Einflussfaktoren der Simulation ab. Sie ist das zentrale Analyseinstrument zur Ableitung konsistenter Szenarien.

## Struktur

### Deskriptoren

Jeder der 7 Einflussfaktoren hat genau 2 mögliche Zustände (Deskriptoren):

| Faktor | ID | Zustand 1 | Zustand 2 |
|--------|-----|-----------|-----------|
| Mobilitätsbedürfnis | F1 | F1.1 Globaler Reiseboom | F1.2 Stagnation/Verzicht |
| Regulatorische Strenge | F2 | F2.1 Moderater Klimaschutz | F2.2 Radikale Dekarbonisierung |
| Technologische Reife | F3 | F3.1 Inkrementelle Verbesserungen | F3.2 Durchbruch SAF/E-Fuels/H2 |
| Wirtschaftliche Entwicklung | F4 | F4.1 Stabiles Wachstum | F4.2 Rezession/Stagflation |
| Verfügbarkeit Alternativen | F5 | F5.1 Schiene stagniert | F5.2 Massiver Schienenausbau |
| Gesellschaftlicher Wertewandel | F6 | F6.1 Fliegen akzeptiert | F6.2 Flight Shaming |
| Geopolitische Stabilität | F7 | F7.1 Offene Märkte | F7.2 Fragmentierung |

### Matrix-Aufbau

Die CIB-Matrix ist eine **14×14 Matrix** (7 Faktoren × 2 Zustände = 14 Deskriptoren).

- **Zeile** = Quell-Deskriptor (beeinflusst andere)
- **Spalte** = Ziel-Deskriptor (wird beeinflusst)
- **Zelle (i,j)** = "Wenn Deskriptor i eintritt, wie beeinflusst das die Wahrscheinlichkeit von Deskriptor j?"

Zellen innerhalb desselben Faktors (z.B. F1.1 → F1.2) werden nicht bewertet (sind per Definition gegenseitig exklusiv).

## Skala

| Wert | Bedeutung |
|------|-----------|
| +3 | Stark fördernd |
| +2 | Fördernd |
| +1 | Leicht fördernd |
| 0 | Kein Einfluss |
| -1 | Leicht hemmend |
| -2 | Hemmend |
| -3 | Stark hemmend |

## Scores

### Aktiv-Score (pro Faktor)

Summe der Absolutwerte aller Zellen in den Zeilen des Faktors. Misst, wie stark ein Faktor andere beeinflusst.

```
Aktiv(F1) = Σ |Zelle(F1.x, Fy.z)| für alle y ≠ 1, alle x, z
```

### Passiv-Score (pro Faktor)

Summe der Absolutwerte aller Zellen in den Spalten des Faktors. Misst, wie stark ein Faktor von anderen beeinflusst wird.

```
Passiv(F1) = Σ |Zelle(Fy.z, F1.x)| für alle y ≠ 1, alle x, z
```

### Aktivitäts-Verhältnis

```
Ratio = Aktiv / Passiv
```

- Ratio > 1: Faktor ist Treiber (beeinflusst mehr als er beeinflusst wird)
- Ratio < 1: Faktor ist reaktiv
- Ratio ≈ 1: Faktor ist ausgeglichen

## Delta-Constraint

Die CIB-Matrix wird **iterativ pro Simulationsrunde aktualisiert**. Um Stabilität zu gewährleisten:

- **Max. ±1 Änderung pro Zelle pro Runde**
- Wenn das LLM eine Änderung von z.B. 0 → +3 vorschlägt, wird auf 0 → +1 begrenzt
- Über mehrere Runden kann sich eine Zelle dennoch um den vollen Bereich bewegen
- In Runde 1 gibt es keine Einschränkung (initiale Bewertung)

## JSON-Schema

```json
{
  "cells": {
    "F1.1|F2.1": {
      "source_descriptor": "F1.1",
      "target_descriptor": "F2.1",
      "influence": 2,
      "reasoning": "Hohe Nachfrage erzeugt politischen Druck für Regulierung"
    },
    "F1.1|F2.2": {
      "source_descriptor": "F1.1",
      "target_descriptor": "F2.2",
      "influence": -1,
      "reasoning": "Reiseboom macht radikale Verbote politisch schwierig"
    }
  },
  "entries": [],
  "round_generated": 3,
  "factor_scores": [
    {
      "factor_id": "F1",
      "active_score": 24,
      "passive_score": 18
    }
  ],
  "metadata": {
    "model": "llama3",
    "total_events_considered": 12
  }
}
```

### Felder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `cells` | dict | Key = `"source\|target"`, Value = CIBCell |
| `entries` | list | Deprecated, backward-compat mit C2 |
| `round_generated` | int | Simulationsrunde der Erstellung |
| `factor_scores` | list | Aktiv/Passiv-Scores pro Faktor |
| `metadata` | dict | Frei belegbar (Model, Event-Count, etc.) |

### CIBCell

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `source_descriptor` | str | z.B. "F1.1" |
| `target_descriptor` | str | z.B. "F2.2" |
| `influence` | int | -3 bis +3 |
| `reasoning` | str | LLM-Begründung |

## Beispiel (Ausschnitt)

```
         F1.1  F1.2  F2.1  F2.2  F3.1  F3.2  ...
F1.1      -     -    +2    -1    +1    +2    ...
F1.2      -     -    -1    +2    -1    -1    ...
F2.1     +1    -1     -     -    +1    -1    ...
F2.2     -2    +2     -     -    -1    +2    ...
...
```

Leserichtung: "Wenn F1.1 (Reiseboom) eintritt, fördert das F2.1 (moderater Klimaschutz) mit +2."
