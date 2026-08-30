Die Cross-Impact-Bilanzanalyse, kurz CIB, beantwortet eine Frage, die
Einzelprognosen nicht stellen: Passen die gleichzeitig angenommenen Zustände
logisch zusammen, oder widersprechen sie sich?

> Methodische Grundlage: Weimer-Jehle, W. (2023). *Einführung in die
> Cross-Impact-Bilanzanalyse (CIB): Wege zur qualitativen System- und
> Szenarioanalyse.*

## Wie bewertet wird

Für jedes Paar aus Faktorzuständen ist hinterlegt, wie stark der eine den anderen
begünstigt oder hemmt. Die Skala reicht von −3 bis +3.

| Wert | Bedeutung |
|---|---|
| +3 | Starke Unterstützung |
| +1 | Leichte Unterstützung |
| 0 | Kein Einfluss |
| −1 | Leichte Hemmung |
| −3 | Starke Hemmung |

Für eine Konstellation aus sieben Zuständen werden alle wechselseitigen
Einflüsse aufsummiert. Fällt die Bilanz positiv aus, stützen sich die Annahmen
gegenseitig. Fällt sie negativ aus, enthält das Weltbild Spannungen.

Ein Beispiel: «Massiver Schienenausbau» und «Fliegen alternativlos» stützen sich
nicht — sie beschreiben gegenläufige Entwicklungen. Wer beides gleichzeitig
annimmt, bekommt eine negative Bilanz und damit den Hinweis, dass hier zwei
Erwartungen kollidieren.

## Was der Wert sagt — und was nicht

Der Konsistenzwert misst **Widerspruchsfreiheit, nicht Wahrscheinlichkeit**. Er
sagt, wie einheitlich ein Weltbild gepolt ist: Eine Zukunft, in der alles in
dieselbe Richtung zeigt, bekommt einen hohen Wert; eine gemischte Lage einen
niedrigen.

Das ist eine echte Einschränkung, und sie ist am 29. August 2026 nachgemessen
worden: Über alle 128 möglichen Konstellationen hängt der Wert fast nur an der
Einheitlichkeit der Polung. **Ein niedriger Wert heißt deshalb nicht
«unwahrscheinlich».** Strenge Regulierung *bei* gleichzeitig starker Nachfrage
ist die reale europäische Lage — und bekommt hier einen niedrigen Wert, weil sie
gemischt ist.

Lesen Sie den Wert also als *Spannungsanzeige*, nicht als Bewertung. Er zeigt,
wo in einem Weltbild Kräfte gegeneinander arbeiten. Das ist nützlich; es ersetzt
aber keine Einschätzung, wie wahrscheinlich diese Zukunft ist.

## Warum die Matrix eingefroren ist

Die Einflusswerte stehen in `configs/cib_frozen.json` und tragen dort das
Kennzeichen `"frozen": true`. Sie werden **nicht** aus Simulationsläufen
abgeleitet.

Das ist die wichtigste methodische Festlegung des Systems. Würde die Matrix aus
den eigenen Läufen gelernt, käme der Maßstab aus dem Messobjekt: Die Simulation
würde jede Konstellation für konsistent erklären, die sie selbst häufig erzeugt.
Die Bewertung wäre zirkulär und damit wertlos.

Stattdessen ist die Matrix ein unabhängiger Maßstab, an dem sich Läufe messen
lassen müssen.

Wie gut dieser Maßstab geeicht ist, steht auf einem anderen Blatt: Von den 168
Einflusswerten trägt heute rund ein Viertel eine niedergeschriebene Begründung.
Die Herkunft der übrigen ist in den Projektdateien vermerkt, und die Schärfung
dieses Maßstabs ist eingeplant.

## Was das im Ergebnis bewirkt

Am Ende eines Laufs wählt das System drei Konstellationen aus und ordnet sie nach
ihrer Konsistenz. Daraus entsteht das Tripleset in der Ansicht **Szenario**: die
Fortsetzung des Trends, eine strukturell abweichende Entwicklung und eine
Konstellation mit Spannungen.

Das dritte Szenario ist dabei kein Fehlschlag. Es ist häufig das lehrreichste,
weil es zeigt, welche Erwartungen sich gegenseitig ausschließen — und damit,
worüber in einer Planungsrunde eigentlich gestritten werden muss.

## Vertiefung

Die ausführliche methodische Begründung samt Literaturbezug steht in den
Projektdateien `docs/cib_role.md` und `docs/cib_rationale.md`.
