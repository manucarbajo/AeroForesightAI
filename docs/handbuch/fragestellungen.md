Vier typische Fragen und der Weg zur Antwort. Sie zeigen zugleich, wie sich die
Bedienschritte kombinieren lassen.

## Was passiert bei einer hohen CO₂-Abgabe?

Gehen Sie in **Rahmenbedingungen** und öffnen Sie die Systemgröße
«CO₂-Steuer (EUR/t)». Setzen Sie eine Regel: ab Runde 5, Art «fährt hoch auf den
Wert», Zielwert 200, über zehn Runden. Ein Sprung wäre unrealistisch, ein
Hochfahren bildet eine angekündigte Verschärfung ab.

Achten Sie darauf, dass **Eigene Werte anwenden** eingeschaltet ist, und setzen
Sie unter **Technik** einen festen Zufallsstartwert. Rechnen Sie mindestens 30
Ticks, damit die Rückkopplung Zeit hat zu wirken.

Im Ergebnis schauen Sie zuerst in **Übersicht** auf Preis und Buchungsrate, dann
in **Diagramme** unter «Segmente & Alter», welche Gruppen zuerst aussteigen. Wichtig
zu wissen: Die Abgabe wirkt auf die Kaufentscheidung erst oberhalb von 50 EUR je
Tonne, siehe [Wie eine Buchung entsteht](/doku/kaufentscheidung).

## Wie stark hängt das Ergebnis an der Airline-Strategie?

Rechnen Sie denselben Aufbau zweimal, einmal mit einer Zielauslastung von 0,30
und einmal mit 0,50. Beide Werte stehen in **Nachfrage & Preisbildung** ganz
oben.

Die niedrigere Zielauslastung führt zu höheren Preisen, weil die Airline früher
anzieht. Ob das die Buchungsrate stärker drückt als der Gewinn aus der Marge
einbringt, zeigt der Vergleich der beiden Läufe.

## Trägt dieses Ergebnis überhaupt?

Stellen Sie im zweiten Schritt hinter «Feinabstimmung» die Wiederholungen auf
fünf und lassen Sie den Zufallsstartwert **frei**. Sie bekommen fünf Läufe mit derselben Konfiguration,
aber unterschiedlich gezogener Bevölkerung.

Liegen die Buchungsraten dicht beieinander, hängt das Ergebnis an den Annahmen
und ist belastbar. Streuen sie stark, hing es an der Stichprobe — dann brauchen
Sie eine größere Bevölkerung oder eine vorsichtigere Aussage.

## Welche Annahmenwelten unterscheiden sich überhaupt?

Schalten Sie in **Lauf & Ablage** «Alle Szenarien vergleichen» ein. Jedes
hinterlegte Preset wird einmal durchgerechnet, ohne Agenten-Dialog und damit
schnell.

Danach gehen Sie die Läufe in der Lauf-Auswahl durch und vergleichen in
**Übersicht** die Endwerte. Presets, die zu ähnlichen Verläufen führen,
unterscheiden sich in ihren Annahmen weniger, als ihre Namen vermuten lassen —
auch das ist ein Ergebnis.

## Was diese Fragen gemeinsam haben

In allen vier Fällen ändern Sie **eine** Sache und lassen den Rest fest. Das
klingt selbstverständlich, ist aber der häufigste Fehler: Wer gleichzeitig die
Abgabe erhöht und die Zielauslastung senkt, kann die beobachtete Wirkung
hinterher keiner der beiden Änderungen zuordnen. Mehr dazu unter
[Läufe vergleichen](/doku/vergleiche).
