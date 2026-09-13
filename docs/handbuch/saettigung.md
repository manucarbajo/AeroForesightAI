Ohne Sättigung hinge die Nachfrage allein am Preis. Wer sich ein Ticket leisten
kann, würde in jedem Tick erneut buchen, und die Buchungsrate wäre eine reine
Preisfunktion. Das trifft die Wirklichkeit nicht: Wer gerade geflogen ist, fliegt
so schnell nicht wieder.

## Wie es wirkt

Jede Person trägt einen Sättigungsgrad zwischen 0 und 1. Bucht sie, steigt er um
den eingestellten Wert. Er wirkt anschließend als Malus in der Kaufentscheidung
und senkt damit die Wahrscheinlichkeit einer weiteren Buchung.

Drei Größen steuern das Zusammenspiel.

| Größe | Wirkung |
|---|---|
| Sättigung nach einer Buchung | Wie stark der Grad je Buchung steigt. Bei 1 fällt die Person vorerst ganz als Nachfrager aus. |
| Wirkung der Sättigung | Wie schwer der aufgebaute Grad in der Entscheidung wiegt. |
| Erholung je Tick | Wie schnell der Grad wieder abgebaut wird — je Segment einstellbar. |

Die ersten beiden gelten für die gesamte Bevölkerung und stehen unter
**Nachfrage & Preisbildung** im Abschnitt «Sättigung». Die Erholung ist eine
Eigenschaft des einzelnen Segments und steht dort in der Feinabstimmung der
jeweiligen Karte.

## Was sich damit einstellen lässt

Über die Erholung unterscheiden sich Segmente in ihrem Reiseverhalten. Ein
Vielflieger-Segment mit hoher Erholung ist schon im nächsten Tick wieder
buchbereit; ein Urlaubssegment mit niedriger Erholung bucht einmal und fällt für
längere Zeit aus.

Setzen Sie die Erholung auf 0, kommt ein Segment nach einer Buchung nie zurück.
Das ergibt Sinn, wenn Sie eine einmalige Kaufentscheidung modellieren wollen, und
führt sonst dazu, dass die Buchungsrate über den Lauf stetig fällt.

## Warum die Buchungsrate typischerweise sinkt

In den ersten Ticks bucht, wer buchen will. Danach ist ein wachsender Teil der
Bevölkerung gesättigt, und die Rate fällt — auch dann, wenn der Preis
unverändert bleibt.

Dieses Absinken ist Absicht und kein Fehler. Es ist der Grund, warum die
Zielauslastung der Airline deutlich unter 1 liegt: Sie steuert gegen eine
Nachfrage, die sich selbst dämpft.

Wenn Sie eine Buchungsrate sehen, die über den ganzen Lauf konstant hoch bleibt,
lohnt der Blick auf diese drei Werte. Eine sehr niedrige Sättigung nach einer
Buchung oder eine Erholung nahe 1 heben den Effekt praktisch auf.
