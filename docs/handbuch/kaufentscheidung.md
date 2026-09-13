Die Buchungsrate ist kein Parameter, den man einstellt. Sie ist das Ergebnis
vieler Einzelentscheidungen: In jedem Tick wird für jede simulierte Person
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
| Preis | Preisempfindlichkeit der Person, multipliziert mit dem Ticketpreis **im Verhältnis zu ihrem Einkommen** |
| CO₂-Abgabe | Umweltbewusstsein, multipliziert mit dem Teil der Abgabe, der über dem Referenzwert von 50 EUR je Tonne liegt |
| Bahn als Alternative | Wechselbereitschaft der Person, multipliziert mit dem Preis, mit anderthalbfachem Gewicht |
| Sättigung | Wie viel diese Person zuletzt schon geflogen ist |

**Der Preis zählt seit September 2026 relativ zum Einkommen**, und das ist mehr
als eine Feinheit: Bis dahin entschied das Einkommen nur über die Hürde davor.
Wer sie genommen hatte, für den war es danach ohne jede Wirkung — ein
Gutverdiener und jemand knapp über der Grenze empfanden dieselben 140 Euro als
gleich schmerzhaft. Jetzt ist derselbe Betrag ein anderer Verzicht, je nachdem
wovon er abgeht.

**Die Bahn wird bewusst nicht so gerechnet.** Sie steht mit dem Ticketpreis in
der Tabelle, nicht mit dem einkommensrelativen — denn ob sich der Umstieg lohnt,
hängt am Verhältnis von Fahrpreis und Reisezeit, nicht am eigenen Kontostand.

Besonders preisempfindliche Personen bekommen zusätzlich einen Aufschlag auf den
CO₂-Malus. Die Begründung: Wer ohnehin genau aufs Geld schaut, spürt eine Abgabe
doppelt — einmal als Preis und einmal als Anlass, das Fliegen zu hinterfragen.

Aus der Summe wird über eine logistische Funktion eine Wahrscheinlichkeit — und
gegen die wird **gezogen**. Eine Person mit 70 Prozent bucht in etwa sieben von
zehn Fällen, eine mit 51 Prozent in gut der Hälfte.

Eine Ausnahme gibt es: Wer sich das Ticket schlicht nicht leisten kann, bucht
nicht. Das ist eine harte Grenze und keine kleine Wahrscheinlichkeit, die bei
genug Versuchen doch einmal zuschlägt.

## Warum gezogen wird — und was das ändert

**Bis August 2026 wurde nicht gezogen, sondern geschwellt:** Wer über 50 Prozent
lag, buchte mit Sicherheit; wer darunter lag, gar nicht. Zwei Personen mit 51 und
99 Prozent waren nicht zu unterscheiden.

Das hatte zwei Folgen. Erstens verzerrte es die Nachfrage systematisch — bei
niedrigen Preisen nach oben, bei hohen nach unten, weil jede Wahrscheinlichkeit
auf null oder eins gedrückt wurde. Zweitens gab es zu jedem Preis genau **eine**
mögliche Buchungsrate: keine Bandbreite, und damit keine Aussage darüber, wie
sicher eine Zahl ist. Die Größenordnung der Verzerrung steht in
[Vergleiche](/doku/vergleiche).

**Reproduzierbar bleibt der Lauf trotzdem.** Der Zufallsstartwert bestimmt beides:
das Ziehen der Bevölkerung zu Beginn und die Buchungsentscheidungen in jedem
Tick. Zwei Läufe mit demselben Startwert liefern exakt dasselbe Ergebnis — auch
dann, wenn Sie unter **Technik** keinen eigenen setzen: Dann rechnet der Lauf mit
einem Standardwert.

Jeder Tick bekommt dabei seinen eigenen Zufallsstrom. Ohne das buchten in jedem
Tick dieselben Personen, und die Buchungsrate würde zur Treppe statt zu einer
Kurve.

## Was daraus folgt

Weil jede Person einzeln entscheidet, wirken Änderungen ungleich. Eine
Preiserhöhung trifft zuerst die preisempfindlichen Segmente, während Vielflieger
mit hoher Zahlungsbereitschaft lange unbeeindruckt bleiben. Die aggregierte
Buchungsrate verdeckt das; in der Ansicht **Diagramme** unter «Segmente & Alter» wird es
sichtbar.

Ebenso wirkt eine CO₂-Abgabe erst oberhalb von 50 EUR je Tonne überhaupt auf die
Entscheidung ein. Wer den Wert von 30 auf 45 anhebt und keine Reaktion sieht, hat
nichts falsch gemacht — der Referenzwert war schlicht noch nicht überschritten.
