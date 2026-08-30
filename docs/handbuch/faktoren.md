Sieben Faktoren beschreiben die Welt, in der ein Lauf stattfindet. Sie sind die
grobe Ebene über den konkreten Zahlen: Nicht «CO₂-Abgabe 120 EUR», sondern
«radikale Dekarbonisierung» oder «moderater Klimaschutz».

Die vollständige Liste mit beiden Zuständen je Faktor steht unter
[Faktoren F1–F7](/doku/ref-faktoren).

## Warum nur zwei Zustände

Jeder Faktor kennt genau zwei mögliche Zustände. Das ist keine Vereinfachung aus
Bequemlichkeit, sondern Voraussetzung für die Konsistenzprüfung: Bei sieben
Faktoren mit je zwei Zuständen gibt es 128 mögliche Weltbilder — wenige genug,
um jede Kombination zu bewerten, und viele genug, um interessante Spannungen zu
enthalten.

Feinere Abstufungen finden auf der Ebene der Systemgrößen statt. Dort ist die
CO₂-Abgabe eine Zahl mit Verlauf, nicht eine Kategorie.

## Ein Faktor kommt von außen

Sechs der sieben Faktoren beschreiben etwas, das der Luftverkehr mitgestaltet:
Nachfrage, Regulierung, Technik, Wirtschaft, Alternativen, gesellschaftliche
Haltung. Der siebte nicht. **F7 «Geopolitische Stabilität»** — offene Lufträume
und multilaterale Kooperation auf der einen Seite, Fragmentierung, Sperrungen
und Konflikte auf der anderen — wirkt auf das System, ohne nennenswert
zurückbeeinflusst zu werden. Ob in Europa die Schiene ausgebaut wird, ändert
nichts an der Weltlage; eine geschlossene Luftstraße oder eine Pandemie ändern
den Luftverkehr dagegen sofort und stark.

Das ist beabsichtigt und in der Einflussmatrix auch so hinterlegt: F7 hat den
mit Abstand niedrigsten Wert für «wird beeinflusst». Praktisch heißt das, dass
sich F7 am besten als Annahme lesen lässt, die Sie einem Lauf mitgeben — nicht
als Ergebnis, das er hervorbringt.

## Wie Faktoren und Zahlen zusammenhängen

Die Faktoren setzen den Rahmen, die Systemgrößen füllen ihn aus. Ein Lauf im
Zustand «radikale Dekarbonisierung» wird typischerweise mit einer hohen
CO₂-Abgabe und einer strengen SAF-Quote konfiguriert. Zwingend ist das nicht —
Sie können beides unabhängig einstellen.

Genau hier setzt die Konsistenzprüfung an. Sie merkt, wenn Faktorzustände
gewählt sind, die schlecht zusammenpassen, und weist das Ergebnis als weniger
stimmig aus. Sie verbietet es aber nicht.

## Was sich im Lauf verändert

Faktoren sind nicht eingefroren. Der Regulator darf zwei von ihnen verschieben,
nämlich die regulatorische Strenge und den gesellschaftlichen Wertewandel. Die
übrigen fünf bleiben über den Lauf konstant, sofern sie nicht durch ein Preset
mit einem zeitlichen Verlauf versehen wurden.

In der Ansicht **Figures** zeigt die Aussage «4 · Die Szenarien nebeneinander»
die Faktorlage **am Ende** jedes Szenario-Laufs — daran unterscheiden sich die
Szenarien sichtbar. Den *Verlauf* über die Ticks, also wann welcher Zustand
gewechselt hat, finden Sie im Bild `factor_states.png` unter «PNG-Export» und in
`timeseries/factors.csv`. Als eigene Bildschirmansicht gab es ihn bis August
2026; sieben Treppenlinien nebeneinander beantworteten für sich genommen keine
Frage.

## Wo Sie sie einstellen

Unter **Simulation starten** im Tab **Rahmenbedingungen**. Jeder Faktor trägt
dort seinen Namen und seine Leitfrage, etwa «F1 · Mobilitätsbedürfnis / Nachfrage
— Wie stark wollen Menschen fliegen?».

Achten Sie darauf, dass **Eigene Werte anwenden** eingeschaltet ist. Sonst
rechnet der Lauf mit der Ausgangslage aus den Konfigurationsdateien, und Ihre
Auswahl bleibt wirkungslos.
