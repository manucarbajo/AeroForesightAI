Den Lauf wählen Sie oben in der Kopfzeile — die Wahl gilt für den ganzen
Leitstand, also auch für Szene, Kennzahlen und Zeitleiste. Unter **Ergebnisse**
liegen sieben Ansichten auf dieselben Daten. Welche wann sinnvoll ist, steht
unter [Ergebnisse lesen](/doku/ergebnisse-lesen).

## Der Leitstand selbst

Bevor Sie in die sieben Ansichten gehen: Der Bereich **Leitstand** beantwortet
die erste Frage meist schon.

In der Mitte steht die Population zu **einem** Tick — jeder Punkt eine Person,
waagerecht ihre Zahlungsbereitschaft, senkrecht ihr Umweltbewusstsein, eingefärbt
danach, ob sie gebucht hat. Die Achsen stehen über den ganzen Lauf fest, damit
eine Bewegung im Bild wirklich eine Bewegung der Bevölkerung ist und nicht bloß
eine nachgeführte Achse. Darüber liegt der Streifen mit den sieben
Faktorzuständen; ein hervorgehobener Chip heißt, dieser Deskriptor ist gekippt.

Rechts stehen die Kennzahlen desselben Ticks — Buchungsrate, Ticketpreis,
Kostendruck, Nachfrageniveau, jeweils mit der Veränderung zum Vortick —, darunter
dieselben Größen als Verlauf mit einer Marke an der aktuellen Stelle. Ganz unten
die Konsole; sie ist zugeklappt, die Zahl daneben sagt, wie viele Meldungen
anliegen.

Unten führt die **Zeitleiste** durch den Lauf: ziehen, schrittweise gehen oder
abspielen. Sie ist die einzige Zeitachse der Oberfläche; alles andere folgt ihr.
Die Marker unter der Leiste zeigen, wo etwas passiert ist — die gelben sind
politische Eingriffe.

## Szenario

Die Hauptansicht. Oben das Lauf-Narrativ, also was im Lauf tatsächlich passiert
ist, darunter das Tripleset aus drei möglichen Fortsetzungen.

Jedes Szenario lässt sich aufklappen und zeigt dann zweierlei: die Anhaltspunkte
aus dem Lauf mit konkreten Tick-Werten, und die Beschreibung selbst. Die
Anhaltspunkte sind der Beleg dafür, dass die Erzählung an gerechneten Zahlen
hängt.

Ganz unten stehen die Python-Kennzahlen, aus denen das Szenario gebaut wurde, und
das vollständige Markdown. Der Knopf «Szenarien neu erzeugen» rechnet die
Auswertung erneut, ohne den Lauf zu wiederholen — nützlich, wenn der Lauf ohne
Szenario-Erzeugung gerechnet wurde.

## Übersicht

Vier Kacheln und zwei Diagramme — dieselben Größen wie in der Telemetrie rechts,
aber über den ganzen Lauf statt zu einem Tick. Die Kacheln nennen erreichte und geplante Ticks,
die Zahl der Ereignisse, das verwendete Modell und ob das Marktmodell aktiv war.

Darunter steht, **woraus der Lauf entstanden ist**: das Rahmenszenario, der
Rechenmodus, der Zufallsstartwert und der Codestand.

Das **Rahmenszenario** ist dabei die wichtigste der vier Angaben — es ist die
Außenwelt, aus der alle Zahlen des Laufs entstanden sind. Es steht seit August
2026 dort; davor ließ sich einem fertigen Lauf nicht ansehen, unter welchen
Annahmen er gerechnet hatte. Läufe von davor zeigen «nicht festgehalten».

Die Diagramme zeigen den Verlauf von Buchungsrate und Ticketpreis. Das ist der
Regelkreis, um den sich alles dreht, und meist der schnellste Weg zur Frage, ob
im Lauf überhaupt etwas passiert ist.

## Animation

Vier Streudiagramme, die sich über die Ticks abspielen lassen. Sie bringen ihre
eigenen Abspielknöpfe mit und folgen **nicht** der Zeitleiste unten — anders als
die Szene im Bereich «Leitstand», die genau das tut. Wer beides nebeneinander
braucht, nimmt die Szene; wer eine Aggregation über Alters- oder Segmentgruppen
sucht, ist hier richtig. Das erste zeigt
jede einzelne Person nach Zahlungsbereitschaft und Umweltbewusstsein, eingefärbt
danach, ob sie gebucht hat. Die übrigen drei fassen nach Altersgruppen und
Segmenten zusammen.

Das vierte ist das aufschlussreichste: Es stellt den Anteil eines Segments an der
Bevölkerung seinem Anteil an den Buchungen gegenüber. Liegt ein Punkt über der
Diagonalen, bucht dieses Segment überdurchschnittlich oft, gemessen an seiner
Größe.

Die Ansicht setzt voraus, dass der Lauf die Personen-Historie mitgeschrieben hat.

## Figures

**Vier Fragen, die ein Lauf beantwortet** — und daneben der Bildexport.

| Aussage | Beantwortet |
|---|---|
| 1 · Preis und Nachfrage | Wie stark antwortet die Buchungsrate auf den Ticketpreis, und woraus setzt der Preis sich zusammen |
| 2 · Was die Politik bewirkt | Welche Instrumente laufen — und was sie bei den Kosten der Anbieter auslösen |
| 3 · Wer noch fliegt | Wer zuerst wegbleibt: nach Profil-Segment und nach Altersgruppe |
| 4 · Die Szenarien nebeneinander | Worin sich die Szenario-Läufe unterscheiden — in Kurven und in ihrer Faktorlage am Ende |
| PNG-Export | Die Bilddateien für Berichte, mit Knopf zum Neuerzeugen |

Der Schnitt folgt seit August 2026 den **Fragen**, nicht den Datenquellen. Vorher
waren es sechs Bereiche nach Herkunft der Zeitreihen — «Yield & Markt»,
«Makro-Wirtschaft», «Airline-Kosten», «CIB-Faktoren» und so fort. Wer sie
durchsah, bekam sechs Sammlungen von Kurven und keine Auskunft.

**Zwei Bereiche sind dabei weggefallen, und beide aus demselben Grund:** Sie
zeigten, was man dem Lauf *vorgibt*, nicht was er *ergibt*. Die
makroökonomischen Indizes (Einkommen, Ölpreis, Bevölkerung) finden Sie unter
**Modell**; sie sind Eingang, nicht Ergebnis. Die sieben Faktor-Verläufe stehen
jetzt bei Aussage 4 — dort erklären sie etwas, nämlich in welcher Weltlage ein
Szenario endet.

**Aussage 4 braucht mehr als einen Lauf.** Steht Ihr Lauf allein, sagt die
Ansicht das und zeigt seine Faktorlage am Ende; ein Vergleich entsteht über
**Einrichten → Szenario-Vergleich starten**. Verglichen werden dann alle
Szenario-Läufe unter `outputs/sweeps/` — auch solche aus früheren Durchläufen.

Unter **PNG-Export** kann eine Warnung über den Bildern stehen; sie sagt, dass
dem Satz nicht zu trauen ist. Zwei Fälle gibt es:

**«Kein Manifest»** — die Bilder liegen da, aber die Liste ihrer Titel fehlt.
Das betrifft ältere Läufe: Ihre Titel sind aus den Dateinamen abgeleitet, und ob
der Satz vollständig ist, lässt sich nicht sagen. «Figures neu erzeugen» stellt
einen benannten Satz her.

**«Das Manifest nennt Bilder, die nicht vorliegen»** — der Satz ist
unvollständig. Vorher fehlten sie einfach, ohne dass es jemand sagte.

Steht keine Warnung da, ist der Satz vollständig und benannt.

## Bericht

Der Tick-für-Tick-Bericht des Laufs, mit Kennzahlen und dem, was die Akteure
gesagt haben. Der richtige Ort, um einer einzelnen Runde nachzugehen.

## Abfrage

Ein Chat, der ausschließlich über die Daten dieses Laufs antwortet. Ausführlich
unter [Läufe abfragen](/doku/abfrage).

## Dateien

Alle Rohdaten des Laufs. JSON eingerückt, Tabellen sortier- und filterbar,
Markdown gerendert, Bilder angezeigt, alles herunterladbar.

Dateien über 256 KB werden erst auf Klick geladen — ein Zwischenstand ist
schnell dreiviertel Megabyte groß. Welche Datei was enthält, steht unter
[Ausgabedateien](/doku/ref-ausgaben).
