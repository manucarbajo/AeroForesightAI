Der Tab **Abfrage** beantwortet Fragen zu genau einem Lauf. Er ist kein
allgemeiner Chat: Er sieht nur die Artefakte dieses Laufs und kann darüber hinaus
nichts wissen.

## Was er sieht

Die Antwort stützt sich auf die Kennzahlen je Runde, den Preisverlauf und das
Ereignisprotokoll. Sind Zwischenstände geschrieben worden, kommen einzelne
Runden im Detail dazu.

Über den Schalter «Datenkontext anzeigen» sehen Sie genau die Daten, die einer
Frage mitgegeben werden. Das ist die verlässlichste Art, eine Antwort
einzuordnen: Was dort nicht steht, kann in der Antwort nicht vorkommen.

## Fragen stellen

Sie können den ganzen Lauf abfragen oder eine einzelne Runde. Für eine Runde
tragen Sie entweder die Nummer in das Feld ein oder nennen sie in der Frage —
«Was passierte bei Tick 15?» erkennt das Modell selbst. Steht das Feld auf 0,
gilt die Frage dem gesamten Lauf.

Gut funktionieren Fragen nach Verläufen, Vergleichen zwischen Runden und nach
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
