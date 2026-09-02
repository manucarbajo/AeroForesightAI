# Bilanz der Phase 2 — Modellsubstanz

**Stand 2026-09-02 · zehn Pakete, alle abgeschlossen · [Projektplan](projektplan.md)**

Diese Datei fasst zusammen, was Phase 2 am Modell verändert hat. Sie ist
**Synthese, keine Quelle**: Jede Zahl unten steht mit ihrer Herleitung im
Projektplan, und die Backtest-Werte gelten nur zum genannten Datum — die
jeweils aktuellen schreibt jeder Lauf nach
[`backtest_vorlauf.md`](backtest_vorlauf.md).

Wer eines der Pakete anfasst, pflegt **dort** und darf diese Datei veralten
lassen; wer sie liest, prüft das Datum oben. Eine Übersicht, die zur zweiten
Wahrheit wird, ist schlimmer als keine.

---

## Das Muster hinter den zehn Paketen

Fast jedes Paket hat dieselbe Sorte Befund abgeräumt: **Etwas gab vor zu
rechnen und tat es nicht.**

- Das Buchungsmodell verglich seine Sigmoid gegen 0,5 — weil sie monoton ist,
  war das identisch mit einer festen Schwelle. Der Logit-Teil war folgenlos
  (P2.1).
- `age` wurde je Person gezogen und danach **exakt** ignoriert; alle Merkmale
  waren voneinander unabhängig, Korrelation mit dem Alter durchgängig unter
  0,08 (P2.4).
- Der CIB-Score hieß «Plausibilität» und misst nachgemessen **Polarität**
  (+0,56 über alle 128 Systemzustände) — die Matrix ist im Kern eine einzige
  Achse (P2.0, [Entscheidung](entscheidung_szenarienschicht_2026-08-29.md)).
- «Keine erfundenen Zahlen» stand im Prompt des State Explorers und wurde
  nirgends durchgesetzt (P2.5).
- Die Nachfragehöhe war eine **Konfigurationskonstante ohne Quelle**
  (`target_booking_rate = 0.37`), gemessen rund zwanzigmal so wirksam wie das
  Einkommen (P2.8).
- 41 % der simulierten Bevölkerung waren exakt 90 Jahre alt — an die
  Obergrenze geklemmt, unbemerkt (P2.9).

Das ist kein Zufall, sondern der Ertrag einer Arbeitsweise: **Eine Messung
findet, was wirklich dasteht; ein Blick in den Code findet, was jemand
hingeschrieben hat.** Alle sechs Befunde oben stammen aus Messungen, keiner aus
Codelektüre.

## Der Backtest ist der Wendepunkt

P2.7 hat dem Modell zum ersten Mal einen Maßstab **außerhalb seiner selbst**
gegeben. Bis dahin prüften alle Nachweise das Modell gegen sich selbst.

Er hat sofort mehr geliefert, als er messen sollte: Die Nachfrageseite lag
nicht ungenau, sondern **verkehrt herum** — das Modell fiel auf 86, wo real 126
stand. Daraus wurde der Architekturbefund von P2.8, und der hat die
Angebotsseite überhaupt erst entstehen lassen.

### Die Kette über die Pakete hinweg

Jedes Paket hat vorher und nachher mit unverändertem Verfahren gemessen. Die
Einzelmessungen stehen bei den Paketen; **zusammengesetzt** ergeben sie das
hier. Angaben sind mittlere Abstände in Indexpunkten, Jahresmittel,
2015–2019 — kleiner ist besser.

| Schritt | Preis | Nachfrage | Fundstelle |
| --- | ---: | ---: | --- |
| Erstmessung, 2026-08-30 | 1,84 | 21,76 | P2.7 |
| **+ Einkommen** (reales EU-BIP) | **1,29** | 21,81 | P2.8 |
| **+ Alter** (Merkmale nach Lebenszyklus) | 1,27 | **23,43** | P2.4 |
| **+ Kapazität und Preisstrategie** | **3,09** | **18,13** | P2.8 / P2.8-B |

Über alle bewerteten Jahre steht die Preisseite heute bei **10,66** (vor
Kapazität und Preisstrategie 14,78), die Nachfrageseite bei **33,36** (27,54).
2020 und 2021 werden mitgerechnet, aber nicht bewertet.

**Zwei Zeilen darin sind Verschlechterungen, und sie stehen bewusst da.** Das
Altersprofil hat die Nachfrageseite verschlechtert und wurde trotzdem behalten;
die Kapazität hat die Preisseite vor der Pandemie verschlechtert und insgesamt
deutlich verbessert. Der Grund ist in beiden Fällen derselbe: **Ein Modell, das
den Backtest besteht, weil es auf ihn hin eingestellt wurde, ist an nichts
geeicht.** Begründet wird über den Mechanismus, nicht über die Punktzahl.

## Was Phase 2 nicht gelöst hat

Nichts davon ist neu — alles steht als Finding oder Paket. Die Liste ordnet nur
nach Schwere und sagt, wo es steht.

| Offen | Wo es steht |
| --- | --- |
| **Zwei Preisstrategien sind zwei, nicht alle.** Erlösmanagement (Marge weitet sich bei Knappheit) und mehrere Anbieter fehlen. `STRATEGIEN` nimmt beide auf. | P2.8-B, Wege B und C der [Entscheidungsvorlage](entscheidung_angebotsseite_2026-08-31.md) |
| **Die Kapazitätsreihe zählt Flüge, nicht Sitze.** Flüge +14,5 %, Passagiere +26,3 % (2015→2019). Erklärt den schlechten Wert nach der Pandemie. **Eine Datenfrage, keine Parameterfrage.** | P2.8, Abschnitt zur Reihe |
| **Das Modell kennt keine Saison** — es schwankt um 12 Indexpunkte, die Zielreihe um 40. Deshalb wird auf Jahresmitteln verglichen. | P2.7 |
| **Was ein Tick bedeutet, ist dreimal verschieden unterstellt** (Faktor 12). Blockiert unter anderem eine sinnvolle Erneuerungsrate. | P3.8, `tests/test_tickdauer_ist_uneinheitlich.py` |
| **Trajektorien enden vor dem Lauf** (Tick 30 bei 40 bzw. 120 Ticks) und halten still ihren letzten Wert. | P2.8, Restposition |
| **Ein Klick in der Schrittfolge kostet bis zu 2,9 s** — zehn Rundläufe, nicht die Rechnung. | P3.9 |
| **Titel und Legende überlappen** in jedem Diagramm. | P3.7 |
| **Impressum, Datenschutz und AGB brauchen Inhalte.** | P1.4, [`landingpage.md`](landingpage.md) |

## Was am Ende trägt

- **Wirkungsrichtungen sind belastbar** — «CO₂-Abgabe hoch, Preis hoch,
  Nachfrage runter» stimmt und ist gegen Beobachtetes geprüft.
- **Niveaus sind es nicht.** Nachfragezahlen sind keine Mengenprognose; das
  steht so im Handbuch.
- **Jede gesetzte Zahl sagt, dass sie gesetzt ist.** Die Trennung von Form und
  Wert — Funktionsform belegt, Bezifferung gesetzt — gilt für die
  Buchungskoeffizienten, das Altersprofil und die Rahmenszenarien.
