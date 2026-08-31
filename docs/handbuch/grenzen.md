Ein Modell ist nur brauchbar, wenn man weiß, wo es aufhört zu tragen. Diese
Grenzen sind bekannt und bewusst in Kauf genommen.

## Keine Kalenderzeit

Ein Tick ist eine Modellrunde ohne Zeitbezug. Aussagen der Form «im Jahr 2032»
lassen sich aus einem Lauf nicht ableiten, auch nicht durch Umrechnung. Was das
Modell liefert, sind Wirkungsrichtungen und Größenordnungen unter gegebenen
Annahmen.

## Ein Anbieter statt eines Marktes

Die Angebotsseite besteht aus einem Provider. Es gibt keinen Wettbewerb zwischen
Fluggesellschaften, keine Strecken, keine Flotten, keine Slots und keine
Kapazitätsgrenzen. Fragen nach Marktanteilen zwischen Anbietern oder nach der
Wirkung einer Fusion kann das Modell nicht beantworten.

Die Buchungsrate ist entsprechend keine Auslastung eines Flugzeugs, sondern der
Anteil der Bevölkerung, der sich in einer Runde für eine Reise entscheidet.

## Eine Alternative statt vieler

Als Ausweichoption ist die Bahn abgebildet, über die Wechselbereitschaft der
Personen. Videokonferenzen, Fernbusse, der Verzicht auf die Reise oder ein
anderes Reiseziel sind darin nicht getrennt modelliert.

## Keine Kapazitäten und keine Lieferketten

Ob Flugzeuge, Personal oder nachhaltiger Treibstoff überhaupt in der benötigten
Menge verfügbar sind, prüft das Modell nicht. Eine SAF-Quote von 50 Prozent
erhöht die Kosten, aber sie scheitert nie an der Verfügbarkeit.

## Die Bevölkerung ist eine Stichprobe

Die simulierten Personen werden zu Beginn gezogen. Bei kleiner Bevölkerung
schwanken die Ergebnisse zwischen Läufen spürbar. Bevor Sie einen Unterschied für
eine Wirkung halten, prüfen Sie mit Wiederholungen, wie groß die natürliche
Streuung ist — siehe [Läufe vergleichen](/doku/vergleiche).

## Niemand wird älter

Die simulierten Personen behalten ihr Alter über den ganzen Lauf. Das ist eine
Entscheidung, keine Lücke — und sie hat zwei Gründe.

Erstens: **Das Alter beeinflusst im Modell nichts.** Ob jemand 30 oder 70 ist,
ändert an seiner Buchungsentscheidung exakt nichts; die hängt an
Zahlungsbereitschaft, Einkommen, Umweltbewusstsein, Preisempfindlichkeit,
Substitutionsbereitschaft und Sättigung. Eine Alterung würde also nur die
Altersgrafik bewegen, sonst nichts.

Zweitens: **Eine Runde ist kein Zeitraum.** Sie hat bewusst keine
Kalenderbedeutung. Jemanden je Runde altern zu lassen hieße festzulegen, wie
viele Jahre eine Runde ist — und damit genau die Bedeutung einzuführen, auf die
das Modell verzichtet.

**Wie Sie die Altersgrafik deshalb lesen:** Sie beschreibt die
**Zusammensetzung** der Bevölkerung, nicht denselben Menschen über die Zeit.
Wächst die Bevölkerung im Lauf, kommen neu gezogene Personen dazu; die
Altersstruktur bleibt dabei stabil, weil sie aus derselben Verteilung stammen.
Es ist eine stehende Gesellschaft, kein alternder Jahrgang.

**Und eine Einschränkung dazu, die Sie kennen sollten:** Die Altersverteilung
selbst ist derzeit unplausibel — rund 40 Prozent der gezogenen Personen liegen
auf der Obergrenze von 90 Jahren. Das ist ein bekannter Fehler in der
Parametrisierung und ändert nichts an den berechneten Zahlen, weil das Alter
nirgends eingeht. Nutzen Sie die Altersgrafik bis auf Weiteres nicht als
Aussage über die Reisenden.

## Die Parameter sind gesetzt, nicht geschätzt

Die Parameter sind fachlich plausibel gewählt, aber nicht gegen historische
Marktdaten geschätzt. Absolute Werte — ein Ticketpreis von 141 Euro, eine
Buchungsrate von 43 Prozent — sind deshalb keine Aussage über den realen Markt.
Belastbar sind Vergleiche innerhalb desselben Modells: dass Preis A höher liegt
als Preis B, wenn Annahme X gilt.

## Was der Vergleich mit der Wirklichkeit ergeben hat

Seit dem 30. August 2026 gibt es dazu eine Messung statt einer Vermutung. Das
Modell wurde gegen die Jahre 2015–2024 gerechnet: Die tatsächlichen CO₂- und
Ölpreise gingen als Außenwelt hinein, und was herauskam, wurde gegen die realen
Flugpreise und Fluggastzahlen gehalten. Das Ergebnis ist zweigeteilt, und beide
Hälften sollten Sie kennen, bevor Sie eine Zahl aus diesem Modell zitieren.

**Die Preisseite trifft — bis 2019.** Die mittlere Abweichung liegt bei 1,8
Indexpunkten. Für ein Modell, dessen Parameter sämtlich von Hand gesetzt und nie
angepasst wurden, ist das bemerkenswert. Ein Beweis ist es nicht: Es sind vier
frei vergleichbare Jahre, und das Basisjahr liegt per Konstruktion auf null.

**Ab 2022 verfehlt sie den Markt deutlich** — 38 Indexpunkte. Die realen
Flugpreise liegen seither rund die Hälfte über dem Niveau von 2015, das Modell
bei plus zwei Prozent. Es kennt den Strukturbruch nach der Pandemie nicht.

**Die Nachfrageseite läuft in die falsche Richtung**, und das ist die wichtigere
Einschränkung. Das Modell lässt die Buchungsrate bis 2019 auf 86 sinken; real
stiegen die europäischen Fluggastzahlen auf 126. Die Ursache ist nachgemessen:
Das Modell hat praktisch **nur einen** Kanal, über den Nachfrage sich bewegt,
und der ist der Preis. Real wuchs der Luftverkehr, *obwohl* die Preise anzogen —
getragen von Einkommen, Netzausbau und Kapazität. Davon kennt das Modell nichts.

Nachgemessen wurde auch, **woran es liegt** — der naheliegende Verdacht war
falsch. Ein fehlender Einkommenseffekt ist es nicht: Seit dem 31. August 2026
speist der Backtest das reale europäische Bruttoinlandsprodukt ein, und die
Nachfrage bewegt sich dadurch um **1,6 von 40 fehlenden Prozentpunkten**. Die
Ursache liegt eine Ebene tiefer, und sie steht schon weiter oben in diesem
Kapitel: **Das Modell kennt einen Anbieter ohne Kapazitätsgrenze.** Jeder
Nachfrageimpuls treibt darin sofort den Preis, und der Preis nimmt die Nachfrage
wieder weg.

Real wuchs der europäische Luftverkehr 2015–2019 um gut ein Viertel, **während
die Realpreise ungefähr flach blieben** — weil das Angebot wuchs: mehr
Sitzplätze, mehr Strecken, mehr Wettbewerb. Wachstum bei gleichbleibendem Preis
setzt Kapazitätsausweitung voraus. Dafür hat dieses Modell keine Größe, und
deshalb kann es einen wachsenden Markt nicht abbilden.

**Praktische Folge:** Nutzen Sie Nachfragezahlen dieses Modells nicht als
Mengenprognose. Belastbar bleibt die Frage, in welche Richtung und wie stark
eine Annahme wirkt — nicht, wie viele Menschen am Ende fliegen. Die vollständige
Auswertung samt Datenquellen steht in `docs/backtest_vorlauf.md`.

## Die Konsistenzbewertung ist ein Urteil

Die CIB-Matrix bildet fachliches Urteil darüber ab, welche Faktorzustände
zusammenpassen. Sie ist gesetzt, nicht gemessen — und von ihren 168 Einflusswerten
trägt bislang rund ein Viertel eine niedergeschriebene Begründung. Eine als
inkonsistent bewertete Konstellation ist nicht unmöglich — sie ist schwerer zu
erklären.

Dazu kommt eine Einschränkung, die im August 2026 nachgemessen wurde: **Der
Konsistenzwert steigt vor allem mit der Einheitlichkeit einer Faktorlage.** Eine
Zukunft, in der alles in dieselbe Richtung zeigt, bekommt einen hohen Wert; eine
gemischte einen niedrigen. Das ist kein Fehler in der Rechnung, sondern eine
Eigenschaft der hinterlegten Matrix — sie enthält kaum gegenläufige
Wechselwirkungen. **Praktische Folge:** Strenge Regulierung *bei* gleichzeitig
starker Nachfrage — die reale europäische Lage — bekommt hier einen niedrigen
Wert. Lesen Sie ihn als Spannungsanzeige, nicht als Bewertung.

## Was daraus folgt

Nutzen Sie die Plattform, um Annahmen explizit zu machen, Wirkungsrichtungen zu
prüfen und Widersprüche in Erwartungen sichtbar zu machen. Nutzen Sie sie nicht
als Quelle für Zahlen, die ohne den zugehörigen Annahmensatz zitiert werden.

Jedes Ergebnis gilt nur zusammen mit der Konfiguration, aus der es entstanden
ist. Deshalb lohnt es sich, Läufe zu benennen und Annahmenwelten als Preset zu
sichern.
