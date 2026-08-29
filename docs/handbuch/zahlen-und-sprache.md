Die Plattform verbindet zwei Dinge, die sonst gern vermischt werden: ein
Rechenmodell und ein Sprachmodell. Die Trennlinie dazwischen ist der eigentliche
Kern des Produkts.

## Die Regel

**Alle Zahlen kommen aus dem Rechenmodell.** Preise, Buchungsraten,
Faktorzustände, Kosten, Segmentanteile — jede Kennzahl wird deterministisch in
Python berechnet.

**Das Sprachmodell liefert ausschließlich Text.** Es deutet, was gerechnet wurde,
schreibt Narrative und bringt Ereignisse ein. Es rechnet nichts aus, und es darf
keine Kennzahl nennen, die es sich selbst ausgedacht hat.

## Warum das so streng gehandhabt wird

Ein Sprachmodell, das gebeten wird, eine plausible Buchungsrate zu nennen, nennt
eine plausible Buchungsrate. Sie sieht richtig aus, sie passt zum Kontext, und
sie ist erfunden. In einem Werkzeug, das Entscheidungsgrundlagen liefern soll,
ist das nicht ein Schönheitsfehler, sondern ein Ausschlusskriterium.

Deshalb wird die Trennung nicht durch Prompts nahegelegt, sondern in Python
geprüft. Jedes Agentenprofil führt unter `must_not_output`, welche Begriffe eine
Antwort nicht enthalten darf. Ein Provider, der über den Ticketpreis reden will,
kommt damit nicht durch. Die Profile stehen unter
[Rechte der Akteure](/doku/ref-akteure).

## Was das für die Bedienung heißt

Der Rechenmodus unter **Technik** ändert deshalb nicht, *was* herauskommt,
sondern nur, wie viel dazu erzählt wird.

| Modus | Zahlen | Narrative |
|---|---|---|
| Mit Sprachmodell | aus dem Rechenmodell | von Ollama geschrieben |
| Ohne Sprachmodell | aus dem Rechenmodell | Platzhaltertexte |
| Nur Zahlen | aus dem Rechenmodell | keine |

Der Editor zeigt unter «Rechenmodus» zugleich an, ob Ollama gerade erreichbar
ist und ob das eingestellte Modell dort vorliegt. Läuft der Dienst nicht,
stehen die beiden unteren Modi weiterhin zur Verfügung — die Zahlen ändern
sich dadurch nicht.

Für einen schnellen Test der Zahlen brauchen Sie also kein Sprachmodell. Für die
Präsentation eines Szenarios brauchen Sie eines, weil die Deutung dort den
Unterschied macht.

## Wie man es überprüft

Vertrauen ist gut, Nachsehen ist eingebaut. In der Ansicht **Abfrage** blenden Sie über
«Artefakt-Checks anzeigen» eine Prüfung ein, die die erzeugten Dateien
gegeneinander abgleicht — etwa ob die Preise in `tick_mechanics.json` und
`price_history.json` übereinstimmen und ob die Änderungen im Ereignisprotokoll
als Python-Deltas markiert sind.

Über «Datenkontext anzeigen» sehen Sie außerdem genau die Daten, die einer
Abfrage übergeben werden. Was dort nicht steht, kann in der Antwort nicht
vorkommen.
