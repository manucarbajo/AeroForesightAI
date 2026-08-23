Unter **Ergebnisse ansehen** wählen Sie oben einen Lauf; darunter liegen sieben
Ansichten auf dieselben Daten. Welche wann sinnvoll ist, steht unter
[Ergebnisse lesen](/doku/ergebnisse-lesen).

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

Vier Kacheln und zwei Diagramme. Die Kacheln nennen erreichte und geplante Ticks,
die Zahl der Ereignisse, das verwendete Modell und ob das Marktmodell aktiv war.

Die Diagramme zeigen den Verlauf von Buchungsrate und Ticketpreis. Das ist der
Regelkreis, um den sich alles dreht, und meist der schnellste Weg zur Frage, ob
im Lauf überhaupt etwas passiert ist.

## Animation

Vier Streudiagramme, die sich über die Ticks abspielen lassen. Das erste zeigt
jede einzelne Person nach Zahlungsbereitschaft und Umweltbewusstsein, eingefärbt
danach, ob sie gebucht hat. Die übrigen drei fassen nach Altersgruppen und
Segmenten zusammen.

Das vierte ist das aufschlussreichste: Es stellt den Anteil eines Segments an der
Bevölkerung seinem Anteil an den Buchungen gegenüber. Liegt ein Punkt über der
Diagonalen, bucht dieses Segment überdurchschnittlich oft, gemessen an seiner
Größe.

Die Ansicht setzt voraus, dass der Lauf die Personen-Historie mitgeschrieben hat.

## Figures

Sechs thematische Auswertungen plus die exportierten Bilddateien.

| Bereich | Zeigt |
|---|---|
| Yield & Markt | Preis gegen Buchungsrate, dazu die Zusammensetzung aus Kosten und Marge |
| Segmente & Alter | Buchungsraten je Profil-Segment und je Altersgruppe |
| Policies & Steuern | Verlauf der politischen Instrumente |
| Makro-Wirtschaft | Einkommen, Bevölkerung, Nachfragewachstum, Ölpreis |
| Airline-Kosten | Wartung, Personal, Treibstoff |
| CIB-Faktoren | Die Zustands-Trajektorien von F1 bis F7 als Treppenlinien |
| PNG-Export | Die sechs Bilddateien für Berichte, mit Knopf zum Neuerzeugen |

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
