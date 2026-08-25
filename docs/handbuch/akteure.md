Drei Akteure handeln in jeder Runde: der Consumer als Nachfrageseite, der
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

## Die Reihenfolge einer Runde

Zuerst rechnet das Modell: Die Bevölkerung entscheidet über Buchungen, daraus
entsteht die Buchungsrate, die Airline passt den Preis an, Systemgrößen und
Faktoren werden fortgeschrieben.

Erst danach kommen die Akteure zu Wort. Sie sehen das Ergebnis der Runde und
deuten es. Was sie sagen, kann Ereignisse für die nächste Runde erzeugen — aber
es verändert nicht rückwirkend die Zahlen dieser Runde.

## Redebedarf

Im Normalbetrieb äußert sich jeder Akteur in jeder Runde. Das erzeugt viel Text,
von dem wenig neu ist. Der **Redebedarf-Modus** unter **Technik** ändert das: Ein
Akteur meldet sich nur, wenn sich für ihn etwas Wesentliches verändert hat.

Die Protokolle werden dadurch kürzer und dichter. Für lange Läufe ist das meist
die bessere Wahl; für die Vorführung eines kurzen Laufs ist der vollständige
Dialog anschaulicher.
