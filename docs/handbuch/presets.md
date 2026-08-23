Ein Preset ist eine gespeicherte Annahmenwelt. Statt bei jedem Lauf Faktoren,
Politik und Kosten einzeln einzustellen, wählen Sie eines aus und passen davon
ausgehend an.

Die mitgelieferten Presets stehen mit Beschreibung und Begründung unter
[Szenario-Presets](/doku/ref-presets).

## Ein Preset verwenden

Unter **Simulation starten** im Tab **Überblick** stellen Sie «Womit starten?»
auf «Szenario-Preset» und wählen eines aus. Unter der Auswahl erscheint, wofür es
steht.

Damit rechnet der Lauf mit den Werten des Presets. Die anderen Tabs zeigen
weiterhin Ihre eigenen Einstellungen — diese greifen aber nicht, solange der
Modus auf «Szenario-Preset» steht.

## Ein Preset als Ausgangspunkt nehmen

Wenn Sie von einem Preset ausgehen, aber einzelne Annahmen ändern wollen, gehen
Sie in den Tab **Lauf & Ablage** und klicken dort auf «Werte dieses Szenarios
übernehmen». Die Werte wandern damit in Ihren Entwurf, und der Modus wechselt auf
eigene Parameter.

Danach können Sie in **Rahmenbedingungen** und **Nachfrage & Preisbildung**
einzelne Größen verändern, ohne den Rest neu aufsetzen zu müssen.

## Einen eigenen Stand sichern

Im Tab **Kontrolle** ganz unten geben Sie einen Dateinamen ein und klicken auf
«Szenario sichern». Der aktuelle Entwurf landet als Datei unter
`configs/sweeps/` und erscheint danach in der Preset-Auswahl.

Nützlich, sobald Sie eine Konstellation gefunden haben, auf die Sie mehrfach
zurückkommen wollen — etwa eine Referenzwelt, gegen die alle weiteren Läufe
verglichen werden.

## Alle Presets auf einmal rechnen

Der Schalter «Alle Szenarien vergleichen» im Tab **Lauf & Ablage** rechnet jedes
hinterlegte Preset einmal durch, ohne Agenten-Dialog und damit deutlich
schneller. Die Ergebnisse liegen unter `outputs/sweeps/` und erscheinen einzeln
in der Run-Liste.

Das ist der schnellste Weg zu der Frage, wie weit die Annahmenwelten überhaupt
auseinanderliegen.

## Meilensteine

Manche Presets bringen Meilensteine mit: Erwartungen der Form «ab Runde 10 sollte
die CO₂-Abgabe bei 50 liegen». Sie beschreiben, wie das Szenario gemeint ist, und
helfen beim Gegenlesen eines Laufs. In der Referenz sind sie je Preset
aufgeführt.
