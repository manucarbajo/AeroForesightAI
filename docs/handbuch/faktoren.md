Sieben Faktoren beschreiben die Welt, in der ein Lauf stattfindet. Sie sind die
grobe Ebene über den konkreten Zahlen: Nicht «CO₂-Abgabe 120 €», sondern
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

**Wenn mehrere Regeln denselben Faktor betreffen, gilt die mit dem höchsten
Rang.** Das klingt selbstverständlich und war es bis zum 7. September 2026 nicht:
Traf die höchstrangige Regel schon zu — ihr Zustand war bereits gesetzt —, zählte
das nicht als Entscheidung, und der Faktor fiel an die nächste Regel, auch an eine
mit gegenteiliger Wirkung. **Der gesellschaftliche Wertewandel kippte deshalb in
jedem Tick hin und her**, und der Zustand *am Ende* eines Laufs hing davon ab, ob
seine Tickzahl gerade oder ungerade war. Läufe von vor diesem Datum sind
deshalb mit Vorsicht zu lesen — siehe [Läufe vergleichen](/doku/vergleiche).

In der Ansicht **Diagramme** zeigt die Aussage «4 · Die Szenarien nebeneinander»
die Faktorlage **am Ende** jedes Szenario-Laufs — daran unterscheiden sich die
Szenarien sichtbar. Den *Verlauf* über die Ticks, also wann welcher Zustand
gewechselt hat, finden Sie im Bild `factor_states.png` unter «PNG-Export» und in
`timeseries/factors.csv`. Als eigene Bildschirmansicht gab es ihn bis August
2026; sieben Treppenlinien nebeneinander beantworteten für sich genommen keine
Frage.

## Sie stellen sie nicht ein — der Lauf erzeugt sie

**Seit August 2026 sind die Faktoren ein Ergebnis, keine Eingabe.** Sie stellen
die Annahmen über die Außenwelt ein — CO₂-Abgabe, SAF-Quote, Ölpreis, Konjunktur,
und zwar über die Wahl des Szenarios im ersten Schritt. Aus deren Verlauf
entsteht die Faktorlage während des Laufs.

Der Grund ist gemessen, nicht gefühlt. Vorher gab es einen Schritt, der die
sieben Zustände abfragte, und die Antwort trug nicht weit:

- **Vier der sieben** (Regulierung, Technologie, Gesellschaft, Geopolitik)
  werden schon im **ersten Tick** überschrieben. Ihre Regeln binden sie an
  CO₂-Abgabe, SAF-Quote und Ölpreis — was Sie vorher eingestellt hatten, war
  danach weg.
- In allen vier mitgelieferten Szenarien, die eine Faktorvorgabe trugen, endete
  der Lauf auf **denselben** Zuständen wie ohne sie.

Das ist keine Einschränkung, sondern der Sinn der Sache: Ein Szenario beschreibt
eine **Außenwelt**, und was daraus für Nachfrage, Regulierungsdruck und
Technologie folgt, soll die Simulation herausfinden — nicht die Eingabemaske
vorwegnehmen.

## Wo Sie das Ergebnis sehen

Am Ende eines Laufs in der Ansicht **Szenario** und, über die Ticks aufgelöst, in
`timeseries/factors.csv` sowie im Bild `factor_states.png`.

Ein Beispiel aus einem Lauf über 40 Ticks: In Tick 1 stehen alle sieben
Faktoren auf ihrem ersten Zustand, in Tick 40 auf `F1.2, F2.2, F3.2, F4.2,
F5.2, F6.1, F7.1` — eine **gemischte** Lage, die so niemand eingestellt hat.
