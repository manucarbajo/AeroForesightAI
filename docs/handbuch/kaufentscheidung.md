Die Buchungsrate ist kein Parameter, den man einstellt. Sie ist das Ergebnis
vieler Einzelentscheidungen: In jeder Runde wird für jede simulierte Person
gerechnet, ob sie bucht oder nicht.

## Zwei Stufen

Die Entscheidung fällt in zwei Schritten. Zuerst prüft das Modell, ob die Person
sich das Ticket überhaupt leisten kann und will. Ihre Zahlungsbereitschaft wird
dafür mit ihrem Einkommensfaktor multipliziert und um einen Aufschlag für
Umweltbewusstsein erhöht — wer Umweltthemen wichtig findet, ist bereit, für das
Fliegen etwas mehr auszugeben, wenn es denn sein muss. Liegt der Ticketpreis über
dieser Grenze, endet die Sache hier: keine Buchung, unabhängig von allem anderen.

Erst wenn diese Hürde genommen ist, wird der Nutzen der Reise abgewogen.

## Was gegen die Buchung spricht

Der Nutzen startet bei einem festen Grundwert und wird durch vier Größen
gemindert.

| Was mindert | Wodurch |
|---|---|
| Preis | Preisempfindlichkeit der Person, multipliziert mit dem Ticketpreis |
| CO₂-Abgabe | Umweltbewusstsein, multipliziert mit dem Teil der Abgabe, der über dem Referenzwert von 50 EUR je Tonne liegt |
| Bahn als Alternative | Wechselbereitschaft der Person, multipliziert mit dem Preis, mit anderthalbfachem Gewicht |
| Sättigung | Wie viel diese Person zuletzt schon geflogen ist |

Besonders preisempfindliche Personen bekommen zusätzlich einen Aufschlag auf den
CO₂-Malus. Die Begründung: Wer ohnehin genau aufs Geld schaut, spürt eine Abgabe
doppelt — einmal als Preis und einmal als Anlass, das Fliegen zu hinterfragen.

Aus der Summe wird über eine logistische Funktion eine Wahrscheinlichkeit. Liegt
sie bei mindestens 0,5, wird gebucht.

## Warum das deterministisch ist

Es wird nicht gewürfelt. Der Schwellwert entscheidet, nicht ein Zufallszug. Bei
gleicher Ausgangslage und gleichem Preis fällt dieselbe Person immer gleich.

Zufall steckt nur an einer Stelle im Modell, nämlich beim Ziehen der Bevölkerung
zu Beginn: Wer welche Zahlungsbereitschaft, welches Alter und welche Merkmale
bekommt, hängt vom Zufallsstartwert ab. Der ganze Lauf ist damit reproduzierbar —
auch dann, wenn Sie unter **Technik** keinen eigenen Startwert setzen: Dann
rechnet der Lauf mit einem Standardwert.

## Was daraus folgt

Weil jede Person einzeln entscheidet, wirken Änderungen ungleich. Eine
Preiserhöhung trifft zuerst die preisempfindlichen Segmente, während Vielflieger
mit hoher Zahlungsbereitschaft lange unbeeindruckt bleiben. Die aggregierte
Buchungsrate verdeckt das; in der Ansicht **Figures** unter «Segmente & Alter» wird es
sichtbar.

Ebenso wirkt eine CO₂-Abgabe erst oberhalb von 50 EUR je Tonne überhaupt auf die
Entscheidung ein. Wer den Wert von 30 auf 45 anhebt und keine Reaktion sieht, hat
nichts falsch gemacht — der Referenzwert war schlicht noch nicht überschritten.
