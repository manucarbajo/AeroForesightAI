Gestartet wird im **Bedienfeld links**. Es zeigt oben in drei Zeilen, was
eingestellt ist — Szenario, Länge, Rechenmodus —, darunter den Preflight (in
Klartext, was gleich passiert, dazu die wichtigsten Werte als Kacheln), und ganz
unten den Start-Knopf. Der bleibt sichtbar, egal wie lang die Warnungen darüber
werden. Ein Klick genügt.

Eingestellt wird nicht hier, sondern im Bereich **Einrichten** — über die
Kopfzeile oder über jede der drei Zeilen. Für einen ersten Lauf ist das nicht
nötig: Die Vorbelegung trägt einen sinnvollen Lauf.

## Während der Lauf rechnet

Der Zustand oben in der Kopfzeile wechselt auf **Simulation läuft**, und der
Punkt daneben pulsiert. Es ist die einzige Bewegung in der Oberfläche und
deshalb eindeutig.

Der Fortschritt läuft in die **Konsole** in der rechten Spalte. Sie ist
zugeklappt — die Zahl daneben sagt, wie viele Meldungen anliegen. Aufgeklappt
zeigt sie je Runde die vergangene Zeit, die Geschwindigkeit, den Ticketpreis und
die Buchungsrate — dieselben Zeilen, die auch im Terminal stehen —, und darüber,
was sonst noch zu melden ist: ausgefallene Modellaufrufe in Gelb, ein Lauffehler
in Rot. Der Start-Knopf ist gesperrt, solange gerechnet wird.

Es rechnet immer nur **ein** Lauf, und zwar für alle: Der Zustand hängt am
Server, nicht an Ihrem Browserfenster. Laden Sie die Seite mitten im Lauf neu
oder öffnen Sie das Dashboard in einem zweiten Tab, sehen Sie dort ebenfalls
«Simulation läuft», einen gesperrten Start-Knopf **und denselben Fortschritt**.

## Während gerechnet wird

Sobald der Lauf angefangen hat, wechselt der **Leitstand** das Bild: Statt der
Szene steht dort der Ladebildschirm — wie weit der Lauf ist, was er rechnet
(Szenario, Umfang, Rechenmodus), und darunter die Konsole, hier aufgeklappt.
Solange gerechnet wird, ist sie das Einzige, was sich bewegt.

Sie müssen nicht zusehen. Wechseln Sie nach **Ergebnisse**, um einen früheren
Lauf anzuschauen, oder ins **Handbuch** — der Fortschritt wandert dann in ein
kleines Fenster unten rechts und bleibt dort sichtbar. Ein Klick auf «Ansehen»
bringt Sie zurück zum Ladebildschirm. Abbrechen können Sie den Lauf von dort
aus nicht; er gehört dem Server und nicht diesem Fenster.

**Steht der Balken still und zeigt keinen Prozentwert**, ist das kein Fehler:
Bis zur ersten Tick-Meldung weiß niemand, wie weit der Lauf ist, und dann läuft
ein unbestimmter Balken statt einer erfundenen Zahl. Die Prozentangabe erscheint,
sobald der erste Tick gerechnet ist.

Ist der Lauf fertig, meldet das Bedienfeld links die Run-ID mit der Zahl der
Ticks und Events — und daneben steht der Weg weiter: **Ergebnisse ansehen**.

Der Lauf läuft im Hintergrund. Sie können in der Zwischenzeit auf **Einrichten**,
**Ergebnisse** oder ins **Handbuch** wechseln, ohne ihn abzubrechen — die Kopfzeile bleibt
dabei stehen, und der Zustand ist von überall sichtbar. Was Sie nicht können:
einen zweiten Lauf parallel starten. Das Modell leitet während eines Laufs die
Programmausgabe um, und zwei gleichzeitige Läufe würden sich die Protokolle
gegenseitig zerschneiden.

## Wie lange es dauert

Grob geschätzt, für eine Bevölkerung in Standardgröße:

| Modus | Zehn Ticks |
|---|---|
| Nur Zahlen (ohne Agenten-Dialog) | unter einer Sekunde |
| Ohne Sprachmodell (Mock) | wenige Sekunden |
| Mit Sprachmodell | Minuten, je nach Modell und Rechner |

Der Unterschied liegt allein bei den Agenten-Narrativen. Die Kennzahlen sind in
allen drei Fällen dieselben.

## Die drei Ausgänge

Was am Ende erscheint, hängt davon ab, was Sie konfiguriert haben.

Bei einem **Einzellauf** meldet das Bedienfeld die Run-ID, die Zahl der
gerechneten Ticks und die Zahl der Ereignisse. Der Lauf ist danach in der
Auswahl oben in der Kopfzeile bereits gesetzt, und Szene, Kennzahlen und
Zeitleiste zeigen ihn.

Bei **Wiederholungen** entsteht ein Bündel unter einer gemeinsamen Batch-ID. Die
Meldung nennt, wie viele Läufe entstanden sind und wie viele Ereignisse
insgesamt. Die einzelnen Läufe wählen Sie danach über die Auswahl in der
Kopfzeile.

Beim **Szenario-Vergleich** — also wenn Sie ihn auf dem Einstieg von
«Einrichten» gewählt oder «Alle Szenarien vergleichen» hinter der
«Feinabstimmung» des zweiten Schritts eingeschaltet haben — wird jedes Preset
einmal durchgerechnet. Die Ergebnisse
liegen unter `outputs/sweeps/`, dazu entsteht eine Zusammenfassung. Auch hier
erscheinen die einzelnen Läufe in der Auswahl der Kopfzeile.

**Ein Vergleich übernimmt Ihre Einstellungen nicht.** Er rechnet jedes Szenario
unter denselben Bedingungen — sonst verglichen Sie nicht die Szenarien, sondern
Ihre Änderungen mit sich selbst. Länge, Rechenmodus, Zufallsstartwert und eigene
Faktoren kommen deshalb nicht aus den Schritten, sondern aus den Szenarien selbst
bzw. sind fest vorgegeben. Der Preflight sagt Ihnen vor dem Start, was das im
Einzelnen heißt: Unter «Was der Vergleich vorgibt» steht jede Vorgabe mit ihrer
Begründung.

Eine Sache fällt dabei aus dem Rahmen und steht deshalb im Satz darüber: Für den
abschließenden **Szenariotext** jedes Laufs wird das Sprachmodell befragt — auch
dann, wenn Sie «ohne Sprachmodell» gewählt haben. Die Zahlen entstehen trotzdem
rein rechnerisch; betroffen ist nur der Text am Ende.

## Was der Lauf über sich festhält

Jeder Lauf schreibt mit, unter welchen Bedingungen er entstanden ist: Seed,
Rechenmodus und Codestand. Sie finden das nach dem Lauf unter **Ergebnisse** in
der Ansicht **Übersicht**, direkt unter den Kennzahlen.

**Vor dem Start steht dasselbe im Prüfschritt.** Startwert und Rechenmodus als
Kacheln, dazu aufklappbar «Woran dieser Lauf später wiederzuerkennen ist»:
Codestand und der Fingerabdruck der gelesenen Konfigurationsdateien. Das ist
nicht Buchhaltung, sondern die Vorbedingung fürs Vergleichen — ein Lauf mit
anderem Codestand oder anderem Fingerabdruck gehört nicht neben einen anderen,
und das merkt man besser vorher als nach einer halben Stunde Rechenzeit.

Das ist keine Buchhaltung um ihrer selbst willen. Wer ein Ergebnis
weiterverwendet, muss sehen können, ob überhaupt ein Sprachmodell beteiligt war
— ein Lauf im Modus «Ohne Sprachmodell» liefert vollwertige Zahlen, aber
Platzhaltertexte statt Akteurs-Narrativen. Und wer denselben Lauf noch einmal
rechnen will, braucht den Seed. Alle Felder stehen auch in
`run_metadata.json`, beschrieben unter
[Was ein Lauf hinterlässt](/doku/ref-ausgaben).

**Auch ohne eigenen Startwert ist ein Lauf wiederholbar.** Lassen Sie das Feld
«Eigenen Zufallsstartwert festlegen» im dritten Schritt aus, rechnet der Lauf mit einem
Standardwert — nicht zufällig. Zwei Wiederholungen desselben Aufbaus liefern
dann dasselbe Ergebnis, und welcher Wert es war, steht nach dem Lauf in der
Ansicht **Übersicht**. Einen eigenen Startwert brauchen Sie erst, wenn Sie denselben
Aufbau bewusst mit einer anderen Ziehung sehen wollen.

## Wenn etwas schiefgeht

Bricht der Lauf ab, erscheint die Fehlermeldung im Bedienfeld über dem
Start-Knopf, in der Konsole rechts steht sie rot obenan, und der Fortschritt
bleibt stehen. Die häufigsten Ursachen: Ollama läuft nicht, obwohl
«Ohne Ollama rechnen» ausgeschaltet ist, oder eine Kombination aus
Wiederholungen und «Lauf fortsetzen», die sich gegenseitig ausschließt.

Ein abgebrochener Lauf hinterlässt trotzdem ein Verzeichnis unter `outputs/`,
allerdings ohne die Auswertungen am Ende. In der Lauf-Auswahl erkennen Sie ihn
daran, dass die Zahl der Ticks unter dem Maximum liegt und die Ansicht
«Szenario» leer bleibt. Die Zeitleiste reicht dann nur bis zum letzten
gerechneten Tick — sie richtet sich nach dem, was da ist, nicht nach dem, was
geplant war.
