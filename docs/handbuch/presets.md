Ein Szenario-Preset ist eine gespeicherte Annahmenwelt. Statt bei jedem Lauf
Faktoren, Politik und Kosten einzeln einzustellen, wählen Sie eines aus und
passen davon ausgehend an.

Die mitgelieferten Presets stehen mit Beschreibung und Begründung unter
[Szenario-Presets](/doku/ref-presets).

## Ein Preset verwenden

Unter **Simulation starten** ist die Auswahl die erste der drei Entscheidungen.
Jedes Preset steht dort mit seiner Beschreibung; aufklappbar daneben die
Begründung, warum es so aufgebaut ist.

**Das gewählte Preset gilt unverändert.** Faktorlage, Politik und Kosten kommen
aus seiner Datei unter `configs/sweeps/`; was Sie unten unter «Alle
Einstellungen» eingestellt haben, bleibt dafür außen vor. Genau eine Größe
bleibt Ihre Entscheidung: die **Länge** des Laufs. Auf wie viele Ticks ein
Preset angelegt ist, steht neben seiner Beschreibung — seine Meilensteine sind
auf diese Länge hin gedacht.

> **Bis August 2026 war das anders**, ohne dass es jemand sehen konnte: Das
> Dashboard legte nach dem Preset noch die Werte aus den Konfigurationsdateien
> darüber und drehte es damit still zurück. Ein Lauf mit *Business as Usual*
> rechnete deshalb mit steigender CO₂-Abgabe, obwohl das Szenario genau das
> ausschließt. Läufe von vor und nach dieser Korrektur sind nicht vergleichbar —
> siehe [Läufe vergleichen](/doku/vergleiche).

## Ein Preset als Ausgangspunkt nehmen

Wenn Sie von einem Preset ausgehen, aber einzelne Annahmen ändern wollen,
klicken Sie unter der Auswahl auf «Werte übernehmen und selbst anpassen». Die
Werte wandern damit in den Editor, und die Auswahl springt auf «Eigene
Einstellungen».

Dieser Wechsel ist nötig, nicht kosmetisch: Solange ein Preset gewählt ist,
gelten ausschließlich seine Werte. Erst unter «Eigene Einstellungen» wirkt, was
im Editor steht.

Danach können Sie im Schritt **Rahmenbedingungen** und
**Nachfrage & Preisbildung** einzelne Größen verändern, ohne den Rest neu
aufsetzen zu müssen.

## Einen eigenen Stand sichern

Im Schritt **Lauf & Ablage** geben Sie einen
Dateinamen ein und klicken auf «Szenario sichern». Der aktuelle Entwurf landet
als Datei unter `configs/sweeps/` und erscheint danach oben in der Auswahl.

Nützlich, sobald Sie eine Konstellation gefunden haben, auf die Sie mehrfach
zurückkommen wollen — etwa eine Referenzwelt, gegen die alle weiteren Läufe
verglichen werden.

## Alle Presets auf einmal rechnen

Der kürzeste Weg dorthin ist **Szenario-Vergleich starten** auf dem Einstieg
von «Einrichten»: Er stellt den Vergleich ein und bringt Sie unmittelbar zu
«Prüfen & Starten». Dasselbe bewirkt der Schalter «Alle Szenarien vergleichen»
hinter der «Feinabstimmung» des zweiten Schritts — es ist derselbe Schalter,
nur an der Stelle, an der man ihn auch fein einstellt.

So oder so wird jedes hinterlegte Preset einmal durchgerechnet, ohne
Agenten-Dialog und damit deutlich schneller. Die Ergebnisse liegen unter
`outputs/sweeps/` und erscheinen einzeln in der Lauf-Auswahl.

Das ist der schnellste Weg zu der Frage, wie weit die Annahmenwelten überhaupt
auseinanderliegen.

## Meilensteine

Manche Presets bringen Meilensteine mit: Erwartungen der Form «ab Runde 10 sollte
die CO₂-Abgabe bei 50 liegen». Sie beschreiben, wie das Szenario gemeint ist, und
helfen beim Gegenlesen eines Laufs. In der Referenz sind sie je Preset
aufgeführt.
