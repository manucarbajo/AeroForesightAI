Ein vollständiger Lauf dauert im schnellsten Modus wenige Sekunden. Diese
Anleitung führt einmal durch, vom leeren Leitstand bis zum fertigen Szenario.

## Der Bildschirm in einem Absatz

Das Dashboard ist ein Leitstand: **eine** Ansicht, fünf Bereiche, kein Blättern.
Links das Bedienfeld, in der Mitte die Simulation, rechts die Kennzahlen und die
Konsole, unten die Zeitleiste, oben der Zustand der Anlage. Kopfzeile und
Zeitleiste bleiben stehen; die drei Bereiche dazwischen rollen jeder für sich.
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

**Das Bedienfeld links ist kein Formular.** Es zeigt in drei Zeilen, was
eingestellt ist, darunter den Preflight, und ganz unten den Start-Knopf — der
bleibt immer sichtbar. Eingestellt wird im Bereich **Einrichten**, den Sie oben
in der Kopfzeile erreichen oder über jede der drei Zeilen.

Rechts oben schalten Sie zwischen hellem und dunklem Design um. Die Wahl bleibt
im Browser gespeichert und gilt beim nächsten Öffnen weiter.

Drei Entscheidungen genügen bis zum Start. Sie stehen im Bereich
**Einrichten** nebeneinander, jede mit ihrer Erklärung daneben.

## Schritt 1: Was soll gerechnet werden?

Öffnen Sie **Einrichten**. Ganz oben wählen Sie die Annahmenwelt, von der der
Lauf ausgeht — die Möglichkeiten stehen als Karten nebeneinander.

Nehmen Sie eines der vorbereiteten Szenarien, etwa *Business as Usual*. Unter
jedem steht, wofür es steht. Ein Szenario legt Faktorlage, Politik und Kosten in
einem Zug fest und ist deutlich schneller, als jede Größe einzeln einzustellen.

Ein gewähltes Szenario gilt **unverändert**: Die Werte kommen aus seiner Datei
unter `configs/sweeps/`, und was Sie weiter unten unter «Alle Einstellungen»
eingestellt haben, bleibt dafür außen vor. Wollen Sie von einem Szenario ausgehen und einzelne
Annahmen ändern, klicken Sie auf «Werte übernehmen und selbst anpassen» — dann
wandern seine Werte in den Editor, und die Auswahl springt auf «Eigene
Einstellungen».

## Schritt 2: Wie weit reicht der Lauf?

Setzen Sie die Länge auf **10 Ticks**. Das reicht, um Rückkopplungen zu sehen,
und ist in Sekunden gerechnet.

Ein Tick ist eine Modellrunde, kein Quartal und kein Jahr. Mehr dazu unter
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
daneben pulsiert. Der Fortschritt läuft Runde für Runde in die **Konsole** rechts
— klappen Sie sie auf, um Preis und Buchungsrate je Tick zu sehen. Ist der Lauf
fertig, meldet das Bedienfeld die Run-ID, die Zahl der Ticks und die Zahl der
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
sich **Übersicht** für den Verlauf von Buchungsrate und Preis, und **Figures**
für die Detailauswertungen. Die empfohlene Lesereihenfolge steht unter
[Ergebnisse lesen](/doku/ergebnisse-lesen).

## Was Sie als Nächstes probieren sollten

Wiederholen Sie den Lauf mit einem anderen Szenario und vergleichen Sie die
Ergebnisse. Oder gehen Sie unter **Einrichten** weiter nach unten zu **Alle
Einstellungen** und ändern unter
**Rahmenbedingungen** eine einzelne Größe, etwa die CO₂-Abgabe, und sehen nach,
ob die Wirkung Ihrer Erwartung entspricht. Für einen sauberen Vergleich zweier
Läufe setzen Sie vorher hinter «Feinabstimmung» einen festen Zufallsstartwert —
warum, steht unter [Läufe vergleichen](/doku/vergleiche).
