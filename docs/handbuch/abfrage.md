Der Ansicht **Abfrage** beantwortet Fragen zu genau einem Lauf. Er ist kein
allgemeiner Chat: Er sieht nur die Artefakte dieses Laufs und kann darüber hinaus
nichts wissen.

## Was er sieht

Die Antwort stützt sich auf die Kennzahlen je Tick, den Preisverlauf und das
Ereignisprotokoll. Ganz vorn steht seit Ende September 2026 ein **Faktenblatt**:
die Richtung jeder Kerngröße über den Lauf — «Buchungsrate sinkt von 47,9 % auf
35,7 %» — und jeder Faktorwechsel, fertig gerechnet. Das Modell soll die Richtung
von dort übernehmen, statt sie aus Zahlenreihen zu deuten. Sind Zwischenstände geschrieben worden, kommen einzelne
Ticks im Detail dazu.

Über den Schalter «Datenkontext anzeigen» sehen Sie genau die Daten, die einer
Frage mitgegeben werden.

## Jede Zahl wird nachgeschlagen

Seit dem 31. August 2026 prüft das Programm jede Zahl der Antwort gegen diesen
Datenkontext. Was sich dort nicht wiederfindet, wird unter der Antwort
aufgeführt:

> ⚠️ **Nicht in den Laufdaten belegt:** 213,50

**Die Prüfung beantwortet eine engere Frage, als es zunächst klingt:** «Steht
diese Zahl in den Laufdaten?» — nicht «ist diese Zahl richtig». Der Unterschied
ist wichtig, weil er beide Richtungen betrifft.

**Und umgekehrt ist eine *nicht* markierte Zahl nicht automatisch an der
richtigen Stelle.** Geprüft wird, ob sie in den Laufdaten **vorkommt** — nicht,
ob sie zu der Größe gehört, über die der Satz spricht. Je mehr Zahlen in den
Daten stehen, desto eher trifft eine erfundene zufällig eine davon. Der Hinweis
unter einer markierten Antwort sagt deshalb seit September 2026 dazu, gegen wie
viele verschiedene Zahlen geprüft wurde: «Geprüft wurden 2 Zahlen der Antwort
gegen 6 verschiedene Zahlen der Laufdaten.» Bei sechs heißt «belegt» mehr als
bei sechshundert.

Eine markierte Zahl ist **nicht automatisch falsch.** Rechnet das Modell eine
Differenz aus — «der Preis stieg um 12,50 Euro» —, dann steht diese 12,50
nirgends in den Daten, obwohl die Rechnung stimmen kann. Auch das wird markiert,
und das ist Absicht: Sie sollen sehen, welche Zahl abgelesen und welche
gerechnet ist. Ob eine Rechnung stimmt, kann die Prüfung nicht wissen.

Umgekehrt gilt: Eine **nicht** markierte Zahl steht so in den Daten. Gerundete
Angaben zählen dabei mit — «rund 140 Euro» gilt als belegt, wenn der Wert 140,38
beträgt. Und Prozentangaben werden erkannt: «48,2 %» belegt einen gespeicherten
Anteil von 0,4818. Eine Prozentangabe wird dabei nur gegen Anteile und
Prozentwerte gehalten, nicht gegen jede Zahl — «140 %» belegt also keinen
Ticketpreis von 140 Euro, und «49 %» keine Buchungsrate, die nie bei 49 % lag.

**Zurückgewiesen wird nichts.** Eine Antwort mit einer nicht belegten Zahl wäre
oft trotzdem brauchbar — sie kommt deshalb vollständig, mit dem Vorbehalt
darunter.

**Auch eine falsche Richtung wird markiert.** Sagt die Antwort, die Buchungsrate
sei gestiegen, während sie über den Lauf fiel, steht darunter «Widerspricht der
Rechnung» mit der Stelle — geprüft gegen das Faktenblatt. Bei einer Frage zu
einem einzelnen Tick entfällt diese Prüfung, weil eine Größe dort anders laufen
kann als über den ganzen Lauf.

**Und jede Antwort sagt, dass sie geprüft wurde.** Seit Ende September 2026 steht
auch unter einer Antwort ohne Befund ein Satz, etwa «Prüfung: 3 Zahlen der
Antwort, gehalten gegen 442 verschiedene Zahlen der Laufdaten — jede kommt dort
vor.» Enthält die Antwort keine Zahl, steht das dort. Vorher blieb eine belegte
Antwort ohne Hinweis und sah damit aus wie eine ungeprüfte.

## Fragen stellen

Sie können den ganzen Lauf abfragen oder einen einzelnen Tick. Für einen Tick
tragen Sie entweder die Nummer in das Feld ein oder nennen sie in der Frage —
«Was passierte bei Tick 15?» erkennt das Modell selbst. Steht das Feld auf 0,
gilt die Frage dem gesamten Lauf.

Gut funktionieren Fragen nach Verläufen, Vergleichen zwischen Ticks und nach
dem Zusammenhang zwischen einer Änderung und ihrer Wirkung. Schlecht funktionieren
Fragen, die Wissen von außen brauchen, etwa nach realen Marktdaten oder nach
einem anderen Lauf.

## Ohne Ollama

Der Schalter «Demo ohne Ollama» beantwortet Fragen mit einem Platzhaltertext.
Sinnvoll, um den Ablauf vorzuführen, ohne ein Sprachmodell laufen zu haben. Für
echte Antworten schalten Sie ihn aus; dann muss Ollama erreichbar sein.

## Die Artefakt-Checks

Der Schalter «Artefakt-Checks anzeigen» blendet eine Prüfung ein, die die
erzeugten Dateien gegeneinander abgleicht. Sie prüft, ob alle Pflichtdateien
vorliegen, ob die Preise in den verschiedenen Dateien übereinstimmen, ob die
Änderungen als Python-Deltas protokolliert sind und ob Zwischenstände existieren.

Diese Prüfung ist unabhängig vom Sprachmodell und der schnellste Weg zu der Frage,
ob einem Lauf zu trauen ist.

## Der Verlauf

Der Gesprächsverlauf wird je Lauf getrennt gehalten. Wechseln Sie den Lauf und
kommen zurück, steht Ihre frühere Unterhaltung wieder da. Sie liegt in der
Browser-Sitzung, nicht auf dem Server — ein neues Fenster beginnt leer.
