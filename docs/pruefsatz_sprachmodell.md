# Prüfsatz Sprachmodell

> Erzeugt von `python -m src.reporting.pruefsatz_sprachmodell`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

Gemessen am 2026-09-29 auf «Entwicklungsrechner», Modell `llama3.2`. Die Antworten eines Sprachmodells streuen von Aufruf zu Aufruf; eine einzelne Messung ist ein Ausgangswert, kein Urteil.

| Weg | Texte | englisch | mit Datum | Richtungswiderspruch | unbelegte Zahlen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Abschlusstexte | 7 | 0 | 0 | 3 | 0 |
| Abfrage | 10 | 0 | 0 | 3 | 0 |
| Agenten | 17 | 0 | 0 | 1 | 0 |

**Sekunden je Tick** im Lauf mit Agenten: 13.8

## Befunde im Einzelnen

### Abschlusstexte

- **Business as Usual (A1+B1): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Ein starker Anstieg in der Nachfrage nach Flugreisen führte zu einer erheblichen Belastung der Infrastruktur»
- **CO₂-Verzögerung: run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «gefolgt von einer Erhöhung der Nachfrage nach Flugreisen.»
- **Transformationskonflikt (B2 vs A1): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «die Nachfrage nach erneuerbarer Energie nimmt zu.»

### Abfrage

- **business_as_usual: Ist die Buchungsrate im Lauf gestiegen oder gesunken?**
  - richtung: Buchungsrate: im Text «steigt», gerechnet «sinkt». — «Die Buchungsrate im Lauf ist gestiegen.»
- **business_as_usual: Wie hat sich der Kostendruck entwickelt?**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «da die Nachfrage nach Flugreisen noch nicht stark anstieg.»
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «der zunehmenden Nachfrage nach Flugreisen.»
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «der zunehmenden Nachfrage nach Flugreisen.»
- **transformation_conflict: Ist die Buchungsrate im Lauf gestiegen oder gesunken?**
  - richtung: Buchungsrate: im Text «steigt», gerechnet «sinkt». — «Die Buchungsrate ist gestiegen.»

### Agenten

- **Agent, demand_shift**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Die Nachfrage nach Flughäusern steigt aufgrund des steigenden Bedarfs von Reisenden»
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «was zu einer Erhöhung der Nachfrage führt.»

## Was der Prüfsatz nicht sieht

Erfundene Dinge ohne falsche Richtung oder Zahl («eine Elektroflotte») erkennt er nicht; dafür braucht es ein Faktenblatt (P8-V3). Eine Richtungsaussage zählt nur, wenn ihr Satzteil genau eine Größe und genau eine Richtung nennt — alles andere wird übergangen statt geraten.
