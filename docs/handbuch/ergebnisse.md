Den Lauf wählen Sie oben in der Kopfzeile, solange Sie im Leitstand oder hier sind —
die Wahl gilt für den Leitstand mit
Szene, Kennzahlen und Zeitleiste und für die sieben Ansichten unter **Ergebnisse**,
die auf dieselben Daten schauen. «Ergebnisse» bekommt den Bildschirm allein:
Bedienfeld, Kennzahlen und Zeitleiste gibt es nur im Leitstand. Welche Ansicht
wann sinnvoll ist, steht
unter [Ergebnisse lesen](/doku/ergebnisse-lesen).

Neben der Auswahl führt «Dateien des Laufs» zu den Dateien des gewählten Laufs.
Beides erscheint nur hier und im Leitstand: Beim Einrichten, im Modell und im
Handbuch geht es nicht um einen Lauf, der schon gerechnet ist.

Ein Klick auf den Namen des Laufs öffnet **Lauf wählen**: die Läufe, der jüngste
zuerst, mit Art, Rechenmodus und — wenn ein Sprachmodell ausgefallen ist — dem
Vermerk «beeinträchtigt». Die Suche geht über Name, Rahmen, Datum und
Rechenmodus; jedes Wort muss passen. Darunter wählen Sie, welche Art Sie sehen
wollen: Einzelläufe, Wiederholungen, Szenario-Vergleiche oder Prüfläufe.
**Prüfläufe sind ausgeblendet, bis Sie sie wählen** — Läufe unter einem
Szenario, das heute kein Rahmenszenario ist, etwa einem Stresstest. Die Liste
zeigt höchstens 30 Läufe; die Suche grenzt ein. Ein Klick auf eine Zeile wählt
den Lauf und schließt das Fenster, Escape schließt es ohne Wahl.

**Ein Lauf, der ein Szenario verändert hat, sagt es im Namen:** Haben Sie im
Schritt «Verläufe» etwa die CO₂-Abgabe angehoben, heißt der Lauf «Business as
Usual (A1+B1), verändert» — in der Auswahl, im Kopf des Laufs und in der
Übersicht, wo unter dem Rahmenszenario steht, welche Größen abweichen. Bis Ende
September 2026 hieß er genau wie der unveränderte Rahmen.

## Der Leitstand selbst

Bevor Sie in die sieben Ansichten gehen: Der Bereich **Leitstand** beantwortet
die erste Frage meist schon.

In der Mitte steht die Population zu **einem** Tick — jeder Punkt eine Person,
waagerecht ihre Zahlungsbereitschaft, senkrecht ihr Umweltbewusstsein, eingefärbt
danach, ob sie gebucht hat. Die Achsen stehen über den ganzen Lauf fest, damit
eine Bewegung im Bild wirklich eine Bewegung der Bevölkerung ist und nicht bloß
eine nachgeführte Achse. Darüber liegt der Streifen mit den sieben Faktoren, je
Kurzname und Zustand («Regulierung», «F2.1»); ein hervorgehobener Chip heißt,
dieser Faktor ist gekippt. Der volle Zustandstext steht im Tooltip des Chips.

Rechts stehen die Kennzahlen desselben Ticks — Buchungsrate, Ticketpreis,
Kostendruck, Nachfrageniveau, jeweils mit der Veränderung zum Vortick —, darunter
dieselben Größen als Verlauf mit einer Marke an der aktuellen Stelle, jeder mit
seiner Einheit im Titel. Die Veränderung trägt einen Pfeil — ↑ gestiegen,
↓ gefallen — und keine Farbe: Ob ein steigender Preis gut oder schlecht ist,
entscheidet Ihre Fragestellung, nicht die Oberfläche. Ganz unten
die Konsole; sie ist zugeklappt, die Zahl daneben sagt, wie viele Meldungen
anliegen.

Unten führt die **Zeitleiste** durch den Lauf: ziehen, schrittweise gehen oder
abspielen. Sie ist die einzige Zeitachse der Oberfläche; alles andere folgt ihr.
Die Marker unter der Leiste zeigen, wo etwas passiert ist — die gelben sind
politische Eingriffe; die Legende darunter sagt es ebenfalls. Zeigen Sie mit der
Maus auf einen Marker, nennt er die Ereignisse dieses Ticks, Politik zuerst und
höchstens drei; alle stehen in der Konsole.

## Szenario

Die Hauptansicht. Oben das Lauf-Narrativ, also was im Lauf tatsächlich passiert
ist, darunter das Tripleset aus drei möglichen Fortsetzungen.

**Widerspricht der Text der Rechnung, steht das direkt darunter.** Seit Ende
September 2026 hält das Programm Titel, Zusammenfassung, Lauf-Narrativ und
Auswahlbegründung eines vom Sprachmodell geschriebenen Texts gegen den
gerechneten Verlauf: Schreibt der Text, die CO₂-Abgabe steige, während sie den
ganzen Lauf bei 50 € stand, erscheint ein gelber Hinweis «Widerspricht der
Rechnung» mit der Stelle. Ebenso ein Kalenderdatum oder ein genanntes Jahr («im Jahr 2030») — ein Tick
hat keines — und englischer Text. Der Text wird nicht verändert oder verworfen. Die drei
Szenarien sind ausgenommen: Sie beschreiben mögliche Zukünfte, die anders
verlaufen dürfen als der Lauf. **Was die Prüfung nicht erkennt**, sind frei
erfundene Dinge ohne falsche Richtung — etwa eine «Elektroflotte», die das
Modell nicht kennt.

**Auch was die Akteure sagen, wird geprüft** — seit dem 2. Oktober 2026, im
Bericht und in der Konsole des Leitstands. Gehalten wird ein Akteurstext gegen
den Stand **bis zu seinem Tick**, nicht gegen den ganzen Lauf: Wer in Tick 3
schreibt, die Nachfrage sei gestiegen, hat recht, wenn sie bis dahin stieg,
auch wenn sie danach fällt. Markiert wird nur ein klarer Gegensatz — der Text
sagt «gestiegen», gerechnet ist «gesunken» —, im Bericht mit ⚠ unter der
Stelle, in der Konsole als gelbe Zeile.

Jedes Szenario lässt sich aufklappen und zeigt dann zweierlei: die Anhaltspunkte
aus dem Lauf mit konkreten Tick-Werten, und die Beschreibung selbst. Die
Anhaltspunkte nennen Buchungsrate und Ticketpreis zu einigen Ticks, die
Faktorlage des Szenarios in derselben Kurzform wie die Faktorleiste im
Leitstand (etwa «F1.2, F2.2, …») und, wo sie vom Ende des Laufs abweicht, den
Wechsel («Anders als am Ende des Laufs: F3.1 → F3.2»). Die
Anhaltspunkte sind der Beleg dafür, dass die Erzählung an gerechneten Zahlen
hängt.

Ganz unten stehen die Python-Kennzahlen, aus denen das Szenario gebaut wurde, und
das vollständige Markdown. Der Knopf «Szenarien neu erzeugen» rechnet die
Auswertung erneut, ohne den Lauf zu wiederholen — nützlich, wenn der Lauf ohne
Szenario-Erzeugung gerechnet wurde.

## Übersicht

Vier Kacheln und zwei Diagramme — dieselben Größen wie in den Kennzahlen des Leitstands,
aber über den ganzen Lauf statt zu einem Tick. Die Kacheln nennen erreichte und geplante Ticks,
die Zahl der Ereignisse, das verwendete Modell und ob das Marktmodell aktiv war.

Darunter steht, **woraus der Lauf entstanden ist**: das Rahmenszenario, der
Rechenmodus und der Zufallsstartwert. Codestand und der Fingerabdruck der
gelesenen Konfigurationsdateien stehen hinter «Technische Details» — sie
beantworten, ob zwei Läufe vergleichbar sind, und nicht, was herausgekommen
ist.

Das **Rahmenszenario** ist dabei die wichtigste der drei Angaben — es ist die
Außenwelt, aus der alle Zahlen des Laufs entstanden sind. Es steht seit August
2026 dort; davor ließ sich einem fertigen Lauf nicht ansehen, unter welchen
Annahmen er gerechnet hatte. Läufe von davor zeigen «nicht festgehalten».

Die Diagramme zeigen den Verlauf von Buchungsrate und Ticketpreis. Das ist der
Regelkreis, um den sich alles dreht, und meist der schnellste Weg zur Frage, ob
im Lauf überhaupt etwas passiert ist.

## Animation

Streudiagramme, die sich über die Ticks abspielen lassen. Sie bringen ihre
eigenen Abspielknöpfe mit; eine Zeitleiste gibt es unter «Ergebnisse» nicht — anders als
die Szene im Bereich «Leitstand», die genau das tut. Wer beides nebeneinander
braucht, nimmt die Szene; wer eine Aggregation über Alters- oder Segmentgruppen
sucht, ist hier richtig. **Jedes Diagramm rechnet erst, wenn Sie «Diagramm
zeigen» drücken** — je nach Länge des Laufs dauert das einige Sekunden; die
Ansicht selbst ist sofort da. Das erste zeigt eine feste Stichprobe von 200
Personen nach Zahlungsbereitschaft und Umweltbewusstsein, eingefärbt danach, ob
sie gebucht hat.

**«Wer sich den Flug leisten kann»** zeigt eine feste Stichprobe von 150 Personen, in jedem
Tick dieselben. Waagrecht steht der höchste Ticketpreis, den eine Person
überhaupt bezahlen kann, senkrecht ihr Abstand zum Ticketpreis des Ticks. Steigt
der Preis, sinkt die ganze Wolke. Wer unter die gestrichelte Linie fällt, kann
sich das Ticket nicht leisten und bucht nicht. Oberhalb der Linie entscheidet die
Wahrscheinlichkeit — ein Punkt knapp darüber bucht oft trotzdem nicht. Läufe vor
dem 11. September 2026 zeigen an seiner Stelle einen Hinweis, weil ihnen die
nötige Spalte fehlt.

**«Sättigung»** zeigt dieselben Personen mit ihrer Zahlungsbereitschaft
gegen den Reisebedarf, also eins minus die Sättigung. Wer bucht, ist danach
gesättigt, und sein Punkt fällt nach unten. Tick für Tick klingt die Sättigung
ab, und der Punkt steigt wieder — wie schnell, hängt am Segment.

**Drei Merkmals-Streuungen** zeigen dieselben Personen nach je zwei Merkmalen:
Preisempfindlichkeit gegen Bahnbereitschaft, Alter gegen Umweltbewusstsein und
Einkommensfaktor gegen Zahlungsbereitschaft. Diese Merkmale entstehen beim Ziehen
einer Person und bewegen sich im Lauf wenig: Einmalige Regeln können
Preisempfindlichkeit und Umweltbewusstsein anheben, der Einkommensfaktor folgt dem
Einkommensindex. Zu sehen ist vor allem, an welchen Stellen der Wolke gebucht wird.

Die Aggregations-Sichten darunter fassen nach Altersgruppen und Segmenten zusammen. Die Sicht
«Marktanteil vs. Populationsanteil» ist die aufschlussreichste: Es stellt den Anteil eines Segments an der
Bevölkerung seinem Anteil an den Buchungen gegenüber. Liegt ein Punkt über der
Diagonalen, bucht dieses Segment überdurchschnittlich oft, gemessen an seiner
Größe.

Die Ansicht setzt voraus, dass der Lauf die Personen-Historie mitgeschrieben hat.

## Diagramme

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
**Einrichten → Szenario-Vergleich starten**. Verglichen werden dann die
heutigen Rahmenszenarien, jedes mit seinem jüngsten Lauf aus einem Vergleich.
Läufe unter Szenarien, die heute kein Rahmen mehr sind — ältere Prüfläufe etwa
—, bleiben draußen; der Satz unter dem Vergleich sagt, wie viele es sind. Im
Lauf-Browser finden Sie sie unter dem Filter «Prüfläufe».

Unter **PNG-Export** kann eine Warnung über den Bildern stehen; sie sagt, dass
dem Satz nicht zu trauen ist. Zwei Fälle gibt es:

**«Kein Manifest»** — die Bilder liegen da, aber die Liste ihrer Titel fehlt.
Das betrifft ältere Läufe: Ihre Titel sind aus den Dateinamen abgeleitet, und ob
der Satz vollständig ist, lässt sich nicht sagen. «Diagramme neu erzeugen» stellt
einen benannten Satz her.

**«Das Manifest nennt Bilder, die nicht vorliegen»** — der Satz ist
unvollständig. Vorher fehlten sie einfach, ohne dass es jemand sagte.

Steht keine Warnung da, ist der Satz vollständig und benannt.

## Bericht

Der Tick-für-Tick-Bericht des Laufs, mit Kennzahlen und dem, was die Akteure
gesagt haben. Der richtige Ort, um einem einzelnen Tick nachzugehen.
Überblick und Endstand stehen offen; die Vorgaben des Szenarios und **jeder
Tick sind zugeklappt**. Die Zeile eines Ticks nennt Buchungsrate und Preis,
ein Tick mit Faktorwechsel trägt eine Marke — wer einem Tick nachgeht, klappt
ihn auf. Ein Bericht über 40 Ticks war bis zum 1. Oktober 2026 rund 60
Bildschirme lang, seither knapp fünf.
Vorangestellt sind die vom Szenario geplanten Änderungen der Systemgrößen —
nur die, die in die Länge dieses Laufs fallen. Ein Bericht vor dem 1. Oktober
2026 listet dort noch alle Stützpunkte samt ihrer Konfigurationsbeschreibung.

Je Tick steht eine Kennzahlenzeile — Buchungsrate, Veränderung in
Prozentpunkten, Preis vorher und nachher, die Vorgaben des Szenarios für diesen
Tick —, darunter ein **Faktorwechsel**, wenn es einen gab, dann **Wer bucht**
nach Segment, die **Begründungen der Akteure** und ihre **Meldungen**. Die
beiden letzten gibt es nur in einem Lauf mit Sprachmodell. Die Meldungen des
Systems selbst («[delta:…]») stehen nicht im Bericht, weil die Kennzahlenzeile
dieselben Zahlen nennt; im Ereignisprotokoll (`event_log.json`) bleiben sie.
Berichte von vor dem 1. Oktober 2026 nennen Segmente und Größen noch mit ihren
Kennungen und schreiben Zahlen mit Punkt.

## Abfrage

Ein Chat, der ausschließlich über die Daten dieses Laufs antwortet. Ausführlich
unter [Läufe abfragen](/doku/abfrage).

Beim Wechsel zwischen den Ansichten erscheint ein Ladepunkt, solange die neue
Ansicht gebaut wird. Die Ansichten sind in Bruchteilen einer Sekunde da; die
Diagramme unter «Animation» rechnen einzeln auf Knopfdruck, weil jedes die
simulierten Personen selbst überträgt.

## Dateien

Alle Rohdaten des Laufs. JSON eingerückt, Tabellen sortier- und filterbar,
Markdown gerendert, Bilder angezeigt, alles herunterladbar. Gewählt ist beim
Öffnen der Abschlusstext (`run_scenario.md`), ohne ihn die Angaben zum Lauf.

Dateien über 256 KB werden erst auf Klick geladen — ein Zwischenstand ist
schnell dreiviertel Megabyte groß. Welche Datei was enthält, steht unter
[Ausgabedateien](/doku/ref-ausgaben).
