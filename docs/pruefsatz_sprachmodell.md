# Prüfsatz Sprachmodell

> Erzeugt von `python -m src.reporting.pruefsatz_sprachmodell`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

Gemessen am 2026-09-29 auf «Entwicklungsrechner», Modell `llama3.2`. Die Antworten eines Sprachmodells streuen von Aufruf zu Aufruf; eine einzelne Messung ist ein Ausgangswert, kein Urteil.

| Weg | Texte | englisch | mit Datum | Richtungswiderspruch | unbelegte Zahlen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Abschlusstexte | 7 | 0 | 0 | 2 | 0 |
| Abfrage | 10 | 0 | 0 | 2 | 0 |
| Agenten | 17 | 15 | 0 | 0 | 0 |

**Sekunden je Tick** im Lauf mit Agenten: 9.7

## Befunde im Einzelnen

### Abschlusstexte

- **Business as Usual (A1+B1): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Ein starker Anstieg der Nachfrage nach Ressourcen führt zu einer Krise.»
  - richtung: Ticketpreis: im Text «steigt», gerechnet «sinkt». — «Die Preise steigen»
- **Freiwillige Wende (A2+B2): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Nachfrage steigt kontinuierlich (40%)»

### Abfrage

- **business_as_usual: Ist die Buchungsrate im Lauf gestiegen oder gesunken?**
  - richtung: Buchungsrate: im Text «steigt», gerechnet «sinkt». — «Die Buchungsrate ist im Lauf gestiegen»
  - richtung: Buchungsrate: im Text «steigt», gerechnet «sinkt». — «dass die Buchungsrate im Lauf gestiegen ist.»
- **transformation_conflict: Ist die Buchungsrate im Lauf gestiegen oder gesunken?**
  - richtung: Buchungsrate: im Text «steigt», gerechnet «sinkt». — «Die Buchungsrate ist im Lauf gestiegen.»

### Agenten

- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «Investing in Sustainable Aviation Fuel (SAF) and modernising the fleet to reduce»
- **Agent, policy_change**
  - englisch: Der Text ist überwiegend englisch. — «Update regulation to align with the growing demand for air travel while reducing»
- **Agent, demand_shift**
  - englisch: Der Text ist überwiegend englisch. — «Shift in demand towards eco-conscious airlines due to increasing environmental a»
- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «Airlines will increase investment in Sustainable Aviation Fuel (SAF) and moderni»
- **Agent, policy_change**
  - englisch: Der Text ist überwiegend englisch. — «Update regulation to align with the growing demand for air travel while reducing»
- **Agent, demand_shift**
  - englisch: Der Text ist überwiegend englisch. — «Shift in demand towards eco-conscious airlines due to increasing environmental a»
- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «Increase investment in Sustainable Aviation Fuel (SAF) and modernize fleet to re»
- **Agent, policy_change**
  - englisch: Der Text ist überwiegend englisch. — «Update regulation to align with the growing demand for air travel while reducing»
- **Agent, demand_shift**
  - englisch: Der Text ist überwiegend englisch. — «Booking rate increases for eco-conscious airlines as consumers prioritize sustai»
- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «To capitalize on the growing demand for eco-conscious airlines, we will announce»
- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «We will announce a new sustainable aviation fuel sourcing initiative, aiming to »
- **Agent, policy_change**
  - englisch: Der Text ist überwiegend englisch. — «Update regulation to align with growing demand for sustainable aviation practice»
- **Agent, price_change**
  - englisch: Der Text ist überwiegend englisch. — «We will announce a new sustainable aviation fuel sourcing initiative, aiming to »
- **Agent, policy_change**
  - englisch: Der Text ist überwiegend englisch. — «We update regulation to align with the growing demand for sustainable aviation p»
- **Agent, demand_shift**
  - englisch: Der Text ist überwiegend englisch. — «The consumer's booking behaviour influences the demand for air travel, which in »

## Was der Prüfsatz nicht sieht

Erfundene Dinge ohne falsche Richtung oder Zahl («eine Elektroflotte») erkennt er nicht; dafür braucht es ein Faktenblatt (P8-V3). Eine Richtungsaussage zählt nur, wenn ihr Satzteil genau eine Größe und genau eine Richtung nennt — alles andere wird übergangen statt geraten.
