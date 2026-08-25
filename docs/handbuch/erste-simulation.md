Ein vollständiger Lauf dauert im schnellsten Modus wenige Sekunden. Diese
Anleitung führt einmal durch, vom leeren Dashboard bis zum fertigen Szenario.

## Schritt 1: Annahmenwelt wählen

Öffnen Sie **Simulation starten**. Der erste Tab **Überblick** trägt die
wenigen Entscheidungen, die einen Lauf tatsächlich prägen.

Stellen Sie «Womit starten?» auf **Szenario-Preset** und wählen Sie eines der
hinterlegten Szenarien, etwa *Business as Usual*. Ein Preset legt Faktorlage,
Politik und Kosten in einem Zug fest und ist deutlich schneller als jede Größe
einzeln einzustellen. Unter der Auswahl steht, wofür das Szenario steht.

## Schritt 2: Umfang festlegen

Setzen Sie die Länge auf **10 Ticks**. Das reicht, um Rückkopplungen zu sehen,
und ist in Sekunden gerechnet. Die Wiederholungen lassen Sie bei 1.

Ein Tick ist eine Modellrunde, kein Quartal und kein Jahr. Mehr dazu unter
[Tick, Lauf und Szenario](/doku/tick-und-lauf).

## Schritt 3: Rechenmodus prüfen

Lassen Sie **Ohne Ollama rechnen** eingeschaltet. Der Lauf braucht dann kein
lokales Sprachmodell. Die Kennzahlen sind identisch — sie kommen ohnehin aus dem
Rechenmodell; nur die erzählenden Texte der Agenten sind Platzhalter.

Ganz unten auf dem Tab steht in einem Satz, was gleich passiert. Lesen Sie ihn
einmal gegen; er ändert sich mit jeder Einstellung mit.

## Schritt 4: Starten

Klicken Sie unter dem Editor auf **Start**. Es erscheint ein Protokollfenster,
das den Fortschritt Runde für Runde zeigt, mit Preis und Buchungsrate je Tick.
Wenn der Lauf fertig ist, meldet das Dashboard die Run-ID, die Zahl der Ticks
und die Zahl der Ereignisse.

## Schritt 5: Ergebnis lesen

Wechseln Sie zu **Ergebnisse ansehen**. Der eben erzeugte Lauf ist bereits
ausgewählt. Der erste Tab **Szenario** ist die Hauptansicht: Er zeigt das
Lauf-Narrativ und darunter die drei Szenarien, jeweils mit den Tick-Werten, auf
die sie sich stützen.

Danach lohnt sich **Übersicht** für den Verlauf von Buchungsrate und Preis, und
**Figures** für die ausführlichen Auswertungen. Die empfohlene Lesereihenfolge
steht unter [Ergebnisse lesen](/doku/ergebnisse-lesen).

## Was Sie als Nächstes probieren sollten

Wiederholen Sie den Lauf mit einem anderen Preset und vergleichen Sie die
Szenarien. Oder ändern Sie im Tab **Rahmenbedingungen** eine einzelne Größe,
etwa die CO₂-Abgabe, und sehen Sie nach, ob die Wirkung Ihrer Erwartung
entspricht. Für einen sauberen Vergleich zweier Läufe setzen Sie vorher unter
**Technik** einen festen Zufallsstartwert — warum, steht unter
[Läufe vergleichen](/doku/vergleiche).
