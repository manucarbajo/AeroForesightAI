Ein vollständiger Lauf dauert im schnellsten Modus wenige Sekunden. Diese
Anleitung führt einmal durch, vom leeren Dashboard bis zum fertigen Szenario.

Drei Entscheidungen genügen bis zum Start. Sie stehen untereinander auf der
Seite **Simulation starten**, jede mit ihrer Erklärung daneben.

## Schritt 1: Was soll gerechnet werden?

Öffnen Sie **Simulation starten**. Ganz oben wählen Sie die Annahmenwelt, von
der der Lauf ausgeht.

Nehmen Sie eines der vorbereiteten Szenarien, etwa *Business as Usual*. Unter
jedem steht, wofür es steht. Ein Szenario legt Faktorlage, Politik und Kosten in
einem Zug fest und ist deutlich schneller, als jede Größe einzeln einzustellen.

Ein gewähltes Szenario gilt **unverändert**: Die Werte kommen aus seiner Datei
unter `configs/sweeps/`, und was Sie weiter unten im Editor eingestellt haben,
bleibt dafür außen vor. Wollen Sie von einem Szenario ausgehen und einzelne
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

Unter den drei Schritten steht in einem Satz, was gleich passiert, dazu die
wichtigsten Werte als Kacheln — Länge, Wiederholungen, Zufallsstartwert. Lesen
Sie den Satz einmal gegen; er ändert sich mit jeder Einstellung mit.

Steht dort ein roter Kasten, ist die Konfiguration nicht lauffähig; der
betroffene Wert ist zusätzlich am Feld selbst markiert. Sonst klicken Sie auf
**Start**. Es erscheint ein Protokollfenster, das den Fortschritt Runde für
Runde zeigt, mit Preis und Buchungsrate je Tick. Ist der Lauf fertig, meldet das
Dashboard die Run-ID, die Zahl der Ticks und die Zahl der Ereignisse.

## Schritt 5: Ergebnis lesen

Wechseln Sie zu **Ergebnisse ansehen**. Der eben erzeugte Lauf ist bereits
ausgewählt. Der erste Tab **Szenario** ist die Hauptansicht: Er zeigt das
Lauf-Narrativ und darunter die drei Szenarien, jeweils mit den Tick-Werten, auf
die sie sich stützen.

Danach lohnt sich **Übersicht** für den Verlauf von Buchungsrate und Preis, und
**Figures** für die ausführlichen Auswertungen. Die empfohlene Lesereihenfolge
steht unter [Ergebnisse lesen](/doku/ergebnisse-lesen).

## Was Sie als Nächstes probieren sollten

Wiederholen Sie den Lauf mit einem anderen Szenario und vergleichen Sie die
Ergebnisse. Oder klappen Sie unten **Alle Einstellungen** auf und ändern unter
**Rahmenbedingungen** eine einzelne Größe, etwa die CO₂-Abgabe, und sehen nach,
ob die Wirkung Ihrer Erwartung entspricht. Für einen sauberen Vergleich zweier
Läufe setzen Sie vorher hinter «Feinabstimmung» einen festen Zufallsstartwert —
warum, steht unter [Läufe vergleichen](/doku/vergleiche).
