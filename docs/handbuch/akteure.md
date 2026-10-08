Drei Akteure handeln in jedem Tick: der Consumer als Nachfrageseite, der
Provider als Airline, der Regulator als Politik. Sie sind als Sprachmodell-Agenten
umgesetzt, und sie sind absichtlich beschränkt.

## Informationsbeschränkung

Jeder Akteur sieht nur einen Ausschnitt der Lage. Der Provider kennt Buchungsrate
und Kostendruck, aber nicht die politischen Beweggründe des Regulators. Der
Consumer sieht Marktkennzahlen und Ereignisse, aber nicht die Margenkalkulation
der Airline.

Das ist keine technische Einschränkung, sondern der Punkt der Übung. Ein Modell,
in dem alle alles wissen, produziert Abstimmung, wo in der Wirklichkeit
Fehleinschätzung herrscht. Die Reibung zwischen unvollständig informierten
Akteuren ist das, was die Simulation abbilden soll.

Welcher Akteur was sieht, steht vollständig unter
[Rechte der Akteure](/doku/ref-akteure).

## Wer was darf

| Akteur | Darf vorschlagen |
|---|---|
| Consumer | nichts — er reagiert nur |
| Provider | Ereignisse |
| Regulator | Ereignisse und Änderungen an den Faktoren F2 und F6 |

Dass allein der Regulator Faktoren verschieben darf, und auch nur die beiden für
Regulierung und gesellschaftlichen Wertewandel, wird in Python geprüft. Ein
Vorschlag außerhalb dieser Rechte wird verworfen, nicht diskutiert.

## Die Reihenfolge eines Ticks

Zuerst rechnet das Modell: Die Bevölkerung entscheidet über Buchungen, daraus
entsteht die Buchungsrate, die Airline passt den Preis an, Systemgrößen und
Faktoren werden fortgeschrieben.

Erst danach kommen die Akteure zu Wort. Sie sehen das Ergebnis des Ticks und
deuten es. Was sie sagen, kann Ereignisse für den nächsten Tick erzeugen — aber
es verändert nicht rückwirkend die Zahlen dieses Ticks.

Die Akteure schreiben **deutsch**, ebenso Abschlusstext und Abfrage. Englisch
bleiben nur Kennungen, die das Programm wörtlich liest — Ereignisarten wie
`demand_shift` und Faktornummern wie F1.1. Das mitgelieferte kleine Sprachmodell
formuliert dabei nicht immer sauber und wiederholt sich über mehrere Ticks; die
Zahlen berührt das nicht, sie kommen aus der Rechnung.

## Redebedarf

Im Normalbetrieb äußert sich jeder Akteur in jedem Tick. Das erzeugt viel Text,
von dem wenig neu ist. Der **Redebedarf-Modus** unter **Technik** ändert das: Ein
Akteur meldet sich nur, wenn sich für ihn etwas Wesentliches verändert hat.

Die Protokolle werden dadurch kürzer und dichter. Für lange Läufe ist das meist
die bessere Wahl; für die Vorführung eines kurzen Laufs ist der vollständige
Dialog anschaulicher.

Im Fortschrittsfenster steht in diesem Modus je Tick **eine** Zeile: wer spricht.
Bis September 2026 waren es acht — eine Sprechreihenfolge zwischen sieben Zeilen
Innenansicht des Zählwerks. Die sieben gibt es weiterhin, aber nur auf Nachfrage
(Logstufe `DEBUG`); weggeworfen wären sie beim Nachstellen eines Laufs zu
vermissen.

Greift die **Sicherheitsgrenze** — mehr als zehn Beiträge in einem Tick —, wird
der Rest des Ticks übersprungen und geht direkt an die Marktberechnung. Das steht
seither als Warnung da, nicht mehr als eine Zeile unter acht.
