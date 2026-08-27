Unter dem Editor stehen der Start-Knopf und daneben eine Zeile, die den aktuellen
Stand zusammenfasst. Ein Klick genügt.

## Während der Lauf rechnet

Es erscheint ein Protokollfenster. Es zeigt je Runde die vergangene Zeit, die
Geschwindigkeit, den Ticketpreis und die Buchungsrate — dieselben Zeilen, die
auch auf der Konsole stehen. Der Start-Knopf ist gesperrt, solange gerechnet
wird.

Der Lauf läuft im Hintergrund. Sie können in der Zwischenzeit zu **Ergebnisse
ansehen** oder ins Handbuch wechseln, ohne ihn abzubrechen. Was Sie nicht
können: einen zweiten Lauf parallel starten. Das Modell leitet während eines
Laufs die Programmausgabe um, und zwei gleichzeitige Läufe würden sich die
Protokolle gegenseitig zerschneiden.

## Wie lange es dauert

Grob geschätzt, für eine Bevölkerung in Standardgröße:

| Modus | Zehn Ticks |
|---|---|
| Ohne Agenten-Dialog | unter einer Sekunde |
| Ohne Ollama (Mock) | wenige Sekunden |
| Mit Ollama | Minuten, je nach Modell und Rechner |

Der Unterschied liegt allein bei den Agenten-Narrativen. Die Kennzahlen sind in
allen drei Fällen dieselben.

## Die drei Ausgänge

Was am Ende erscheint, hängt davon ab, was Sie konfiguriert haben.

Bei einem **Einzellauf** meldet das Dashboard die Run-ID, die Zahl der
gerechneten Ticks und die Zahl der Ereignisse. Der Lauf ist danach unter
**Ergebnisse ansehen** bereits ausgewählt.

Bei **Wiederholungen** entsteht ein Bündel unter einer gemeinsamen Batch-ID. Die
Meldung nennt, wie viele Läufe entstanden sind und wie viele Ereignisse
insgesamt. Die einzelnen Läufe wählen Sie danach über die Run-Liste.

Beim **Szenario-Vergleich** — also wenn «Alle Szenarien vergleichen»
eingeschaltet war — wird jedes Preset einmal durchgerechnet. Die Ergebnisse
liegen unter `outputs/sweeps/`, dazu entsteht eine Zusammenfassung. Auch hier
erscheinen die einzelnen Läufe in der Run-Liste.

## Was der Lauf über sich festhält

Jeder Lauf schreibt mit, unter welchen Bedingungen er entstanden ist: Seed,
Rechenmodus und Codestand. Sie finden das nach dem Lauf unter «Ergebnisse
ansehen» im Tab **Übersicht**, direkt unter den Kennzahlen.

Das ist keine Buchhaltung um ihrer selbst willen. Wer ein Ergebnis
weiterverwendet, muss sehen können, ob überhaupt ein Sprachmodell beteiligt war
— ein Lauf im Modus «Ohne Sprachmodell» liefert vollwertige Zahlen, aber
Platzhaltertexte statt Akteurs-Narrativen. Und wer denselben Lauf noch einmal
rechnen will, braucht den Seed. Alle Felder stehen auch in
`run_metadata.json`, beschrieben unter
[Was ein Lauf hinterlässt](/doku/ref-ausgaben).

**Auch ohne eigenen Startwert ist ein Lauf wiederholbar.** Lassen Sie das Feld
«Eigenen Zufallsstartwert festlegen» aus, rechnet der Lauf mit einem
Standardwert — nicht zufällig. Zwei Wiederholungen desselben Aufbaus liefern
dann dasselbe Ergebnis, und welcher Wert es war, steht nach dem Lauf im Tab
**Übersicht**. Einen eigenen Startwert brauchen Sie erst, wenn Sie denselben
Aufbau bewusst mit einer anderen Ziehung sehen wollen.

## Wenn etwas schiefgeht

Bricht der Lauf ab, erscheint die Fehlermeldung im Statusbereich, und das
Protokoll bleibt stehen. Die häufigsten Ursachen: Ollama läuft nicht, obwohl
«Ohne Ollama rechnen» ausgeschaltet ist, oder eine Kombination aus
Wiederholungen und «Lauf fortsetzen», die sich gegenseitig ausschließt.

Ein abgebrochener Lauf hinterlässt trotzdem ein Verzeichnis unter `outputs/`,
allerdings ohne die Auswertungen am Ende. In der Run-Liste erkennen Sie ihn
daran, dass die Zahl der Ticks unter dem Maximum liegt und der Tab «Szenario»
leer bleibt.
