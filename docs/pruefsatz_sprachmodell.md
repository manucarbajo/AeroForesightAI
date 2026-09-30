# Prüfsatz Sprachmodell

> Erzeugt von `python -m src.reporting.pruefsatz_sprachmodell`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

Gemessen am 2026-09-30 auf «Entwicklungsrechner», Modell `llama3.2`. Die Antworten eines Sprachmodells streuen von Aufruf zu Aufruf; eine einzelne Messung ist ein Ausgangswert, kein Urteil.

| Weg | Texte | englisch | mit Datum | Richtungswiderspruch | davon unmarkiert | unbelegte Zahlen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Abschlusstexte | 10 | 0 | 0 | 3 | 0 | 0 |
| Abfrage | 10 | 0 | 0 | 0 | 0 | 0 |
| Agenten | 18 | 0 | 0 | 5 | 5 | 0 |

**Sekunden je Tick** im Lauf mit Agenten: 12.1

## Befunde im Einzelnen

### Abschlusstexte

- **Business as Usual (A1+B1): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Nachfrage steigt»
- **Transformationskonflikt (B2 vs A1): run_narrative**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Nachfrage steigt»
- **Transformationskonflikt (B2 vs A1): selection_reasoning**
  - richtung: Nachfrage: im Text «steigt», gerechnet «sinkt». — «aber langsam steigende Nachfrage»

### Abfrage

Keine.

### Agenten

- **Agent, demand_shift**
  - richtung **(unmarkiert)**: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Die gestiegene Nachfrage nach Luftfahrtdiensten»
- **Agent, demand_shift**
  - richtung **(unmarkiert)**: Nachfrage: im Text «steigt», gerechnet «sinkt». — «Aufgrund des gestiegenen Flugverkehrsaufkommens wird die Nachfrage nach Luftfahrdiensten erhöht.»
- **Agent, demand_shift**
  - richtung **(unmarkiert)**: Nachfrage: im Text «steigt», gerechnet «sinkt». — «was auf eine höhere Nachfrage nach Luftfahrtdiensten zurückzuführen ist.»
- **Agent, demand_shift**
  - richtung **(unmarkiert)**: Nachfrage: im Text «steigt», gerechnet «sinkt». — «dass die Nachfrage nach Luftfahrtdiensten gestiegen ist.»
- **Agent, demand_shift**
  - richtung **(unmarkiert)**: Nachfrage: im Text «steigt», gerechnet «sinkt». — «die gestiegene Nachfrage führen zu einer höheren Booking-Rate.»

## Was der Prüfsatz nicht sieht

Erfundene Dinge ohne falsche Richtung oder Zahl («eine Elektroflotte») erkennt er nicht — das Faktenblatt sagt dem Modell nur, was es behaupten darf. Eine Richtungsaussage zählt nur, wenn ihr Satzteil genau eine Größe und genau eine Richtung nennt — alles andere wird übergangen statt geraten.

**«davon unmarkiert»** zählt Befunde, die das Produkt dem Leser nicht zeigt. Abschlusstext und Abfrage markieren seit P8-V3 jeden Befund dieser Prüfung; die Texte der Agenten markiert das Produkt nicht, weil sie den Zustand eines Ticks beschreiben und nicht den ganzen Lauf — ihr Richtungsbefund ist deshalb ein Hinweis, kein sicherer Widerspruch.
