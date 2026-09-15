Ein vollständiger Lauf dauert im schnellsten Modus wenige Sekunden. Diese
Anleitung führt einmal durch, vom leeren Leitstand bis zum fertigen Szenario.

## Der Bildschirm in einem Absatz

Das Dashboard hat fünf Bereiche, zwischen denen Sie oben in der Kopfzeile wechseln.
Der **Leitstand** ist der eine mit Seitenzonen: links das Bedienfeld, in der Mitte
die Simulation, rechts die Kennzahlen und die Konsole, unten die Zeitleiste.
Einrichten, Ergebnisse, Modell und Handbuch bekommen den Bildschirm allein. Im
Leitstand bleiben Kopfzeile und Zeitleiste stehen; die drei Bereiche dazwischen
rollen jeder für sich.
Ist Ihr Fenster schmal, weichen die beiden Seitenspalten in Schubladen aus — die
Knöpfe dafür sitzen links und rechts in der Kopfzeile. Sie erscheinen jeweils
erst dann, wenn ihre Spalte wirklich zur Schublade geworden ist: die Telemetrie
rechts unter 1280 Pixel Fensterbreite, das Bedienfeld links unter 1024. Auf
einem breiten Schirm sehen Sie deshalb keinen der beiden — dort steht ohnehin
alles nebeneinander.

**Die Breiten können Sie selbst einstellen.** Zwischen den Zonen liegt je eine
schmale Griffleiste; ziehen Sie daran, wird die Seitenspalte breiter oder
schmaler, und der Viewport in der Mitte gibt nach. Ein Doppelklick auf den Griff
stellt die Ausgangsbreite wieder her. Mit der Tastatur geht es auch: Griff
anspringen und mit den Pfeiltasten verschieben. Was Sie einstellen, merkt sich
Ihr Browser bis zum nächsten Mal. Sobald eine Spalte zur Schublade wird, ist ihr
Griff weg — dort gibt es nichts mehr zu ziehen.

**Das Bedienfeld links ist kein Formular.** Es heißt **Nächster Lauf** und zeigt
in drei Zeilen, was eingestellt ist, darunter in einem Satz, was gleich passiert,
und ganz unten den Start-Knopf — der bleibt immer sichtbar. Hinweise vor dem
Start stehen dort nur gezählt; ausführlich stehen sie in «Prüfen & Starten».
Eingestellt wird im Bereich **Einrichten**, den Sie oben in der Kopfzeile
erreichen oder über jede der drei Zeilen.

Rechts oben schalten Sie zwischen hellem und dunklem Design um. Die Wahl bleibt
im Browser gespeichert und gilt beim nächsten Öffnen weiter.

Drei Entscheidungen genügen bis zum Start. Sie stehen im Bereich
**Einrichten** nebeneinander, jede mit ihrer Erklärung daneben.

## Schritt 1: Was soll gerechnet werden?

Öffnen Sie **Einrichten**. Zuerst steht die Frage, womit Sie anfangen möchten:
einen neuen Lauf einrichten, den Szenario-Vergleich starten, oder die letzten
Einstellungen weiterverwenden. Für den ersten Durchgang wählen Sie **Neuen Lauf
einrichten**.

Danach wählen Sie die Annahmenwelt, von der der Lauf ausgeht — die
Möglichkeiten stehen als Karten nebeneinander.

Nehmen Sie eines der vorbereiteten Szenarien, etwa *Business as Usual*. Unter
jedem steht, wofür es steht. Ein Szenario legt Politik, Kosten und Nachfrage in
einem Zug fest und ist deutlich schneller, als jede Größe einzeln einzustellen.

Ein gewähltes Szenario gilt, wie seine Datei unter `configs/sweeps/` es
beschreibt. Wollen Sie davon ausgehen und einzelne Annahmen ändern, tun Sie das
in den nächsten beiden Schritten, **Verläufe** und **Modellannahmen** — der Lauf
legt Ihre Änderungen auf das Szenario. Der Bereich **Modell** ist dafür nicht der
Ort: Was dort steht, wirkt erst gespeichert, und dann für alle Läufe.

Nach dieser Wahl folgt der Schritt **Verläufe**. Er zeigt, wie sich die Größen,
die das Szenario vorgibt — etwa die CO₂-Abgabe —, über den Lauf entwickeln: links
die Größe, rechts ihre Kurve. Er ist optional; für den ersten Durchgang klicken
Sie auf **Weiter**.

## Schritt 2: Wie weit reicht der Lauf?

Setzen Sie die Länge auf **10 Ticks**. Das reicht, um Rückkopplungen zu sehen,
und ist in Sekunden gerechnet.

Ein Tick ist ein Monat Modellzeit, ohne Kalenderdatum. Mehr dazu unter
[Tick, Lauf und Szenario](/doku/tick-und-lauf).

Jedes Szenario nennt daneben, auf wie viele Ticks es angelegt ist — seine
Meilensteine sind auf diese Länge hin gedacht. Die Länge bleibt trotzdem Ihre
Entscheidung; das Szenario setzt sie nicht selbst. Hinter «Feinabstimmung»
stehen die Wiederholungen, die Sie zunächst bei 1 lassen.

## Schritt 3: Womit wird gerechnet?

Lassen Sie **Ohne Sprachmodell** stehen. Der Lauf braucht dann kein lokales
Ollama. Die Kennzahlen sind identisch — sie kommen ohnehin aus dem
Rechenmodell; nur die erzählenden Texte der Agenten sind Platzhalter.

Darunter steht, ob Ollama gerade erreichbar ist. Läuft es nicht, funktionieren
nur die beiden unteren Modi.

## Schritt 4: Gegenlesen und starten

Der Blick geht jetzt nach links. Dort steht in einem Satz, was gleich passiert,
dazu die wichtigsten Werte als Kacheln — Länge, Wiederholungen,
Zufallsstartwert. Lesen Sie den Satz einmal gegen; er ändert sich mit jeder
Einstellung mit, auch während Sie rechts noch einstellen.

Steht dort ein roter Kasten, ist die Konfiguration nicht lauffähig; der
betroffene Wert ist zusätzlich am Feld selbst markiert. Sonst klicken Sie auf
**Start**.

Der Zustand in der Kopfzeile wechselt auf «Simulation läuft» und der Punkt
daneben pulsiert. Der Fortschritt läuft Tick für Tick in die **Konsole** rechts
— klappen Sie sie auf, um Preis und Buchungsrate je Tick zu sehen. Ist der Lauf
fertig, meldet das Bedienfeld die Kennung des Laufs, die Zahl der Ticks und die Zahl der
Ereignisse, und der neue Lauf ist in der Auswahl oben bereits gesetzt.

## Schritt 5: Ergebnis lesen

Der Leitstand zeigt den neuen Lauf sofort. In der Mitte steht die Population zu
**einem** Tick: jeder Punkt ein Individuum, waagerecht seine Zahlungsbereitschaft,
senkrecht sein Umweltbewusstsein, eingefärbt danach, ob es gebucht hat. Darüber
liegt der Streifen mit den sieben Faktorzuständen; ein hervorgehobener Chip heißt,
dass dieser Deskriptor gekippt ist.

Ziehen Sie unten den **Regler** durch den Lauf oder drücken Sie **Abspielen**.
Szene, Kennzahlen und Verläufe rechts folgen alle demselben Tick — die Zeitleiste
ist die einzige Zeitachse der Oberfläche. Die Marker unter der Leiste zeigen, wo
im Lauf etwas passiert ist; die gelben sind politische Eingriffe.

Für die ausführlichen Auswertungen wechseln Sie oben auf **Ergebnisse**. Die
erste Ansicht **Szenario** zeigt das Lauf-Narrativ und darunter die drei
Szenarien, jeweils mit den Tick-Werten, auf die sie sich stützen. Danach lohnt
sich **Übersicht** für den Verlauf von Buchungsrate und Preis, und **Diagramme**
für die Detailauswertungen. Die empfohlene Lesereihenfolge steht unter
[Ergebnisse lesen](/doku/ergebnisse-lesen).

## Ohne Maus durch die Bereiche

Die Kopfzeile führt durch fünf Bereiche — Einrichten, Leitstand, Ergebnisse,
Modell, Handbuch. Mit der Tastatur geht das seit August 2026 ohne Umwege:

Der **erste** Griff auf jeder Seite ist «Zum Inhalt springen». Er erscheint,
sobald er den Fokus hat, und überspringt Kopfzeile und Bereichsliste — sonst
tastet man sich vor jedem Bereich durch dieselben acht Elemente.

Wechseln Sie den Bereich, wandert der **Fokus auf dessen Überschrift**, und der
Wechsel wird angesagt: «Bereich gewechselt: Ergebnisse». In der Bereichsliste
ist der offene Bereich nicht nur farblich hervorgehoben, sondern auch als
solcher ausgezeichnet.

Für die Schrittfolge im Bereich **Einrichten** gilt dasselbe; es steht in
[Lauf konfigurieren](lauf-konfigurieren.md) unter «Ohne Maus, ohne Bildschirm».

Zwei Einschränkungen der Ehrlichkeit halber: Diese Zusagen sind geprüft und am
laufenden System gemessen, eine vollständige WCAG-Prüfung sind sie nicht. Und
sie gelten für Bereichswechsel und Schrittfolge — die einzelnen Ergebnis-
Ansichten sind noch nicht in gleicher Weise durchgegangen.

## Was Sie als Nächstes probieren sollten

Wiederholen Sie den Lauf mit einem anderen Szenario und vergleichen Sie die
Ergebnisse. Oder gehen Sie unter **Einrichten** einen Schritt weiter zu
**Rahmenbedingungen** und ändern unter
**Rahmenbedingungen** eine einzelne Größe, etwa die CO₂-Abgabe, und sehen nach,
ob die Wirkung Ihrer Erwartung entspricht. Für einen sauberen Vergleich zweier
Läufe setzen Sie vorher hinter «Feinabstimmung» einen festen Zufallsstartwert —
warum, steht unter [Läufe vergleichen](/doku/vergleiche).
