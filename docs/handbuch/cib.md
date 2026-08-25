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
gegenseitig und die Konstellation gilt als konsistent. Fällt sie negativ aus,
enthält das Weltbild Spannungen.

Ein Beispiel: «Massiver Schienenausbau» und «Fliegen alternativlos» stützen sich
nicht — sie beschreiben gegenläufige Entwicklungen. Wer beides gleichzeitig
annimmt, bekommt eine negative Bilanz und damit den Hinweis, dass hier zwei
Erwartungen kollidieren.

## Warum die Matrix eingefroren ist

Die Einflusswerte stehen in `configs/cib_frozen.json` und tragen dort das
Kennzeichen `"frozen": true`. Sie werden **nicht** aus Simulationsläufen
abgeleitet.

Das ist die wichtigste methodische Festlegung des Systems. Würde die Matrix aus
den eigenen Läufen gelernt, käme der Maßstab aus dem Messobjekt: Die Simulation
würde jede Konstellation für konsistent erklären, die sie selbst häufig erzeugt.
Die Bewertung wäre zirkulär und damit wertlos.

Stattdessen ist die Matrix ein unabhängiger, fachlich begründeter Maßstab, an dem
sich Läufe messen lassen müssen.

## Was das im Ergebnis bewirkt

Am Ende eines Laufs wählt das System drei Konstellationen aus und ordnet sie nach
ihrer Konsistenz. Daraus entsteht das Tripleset im Tab **Szenario**: die
Fortsetzung des Trends, eine strukturell abweichende Entwicklung und eine
Konstellation mit Spannungen.

Das dritte Szenario ist dabei kein Fehlschlag. Es ist häufig das lehrreichste,
weil es zeigt, welche Erwartungen sich gegenseitig ausschließen — und damit,
worüber in einer Planungsrunde eigentlich gestritten werden muss.

## Vertiefung

Die ausführliche methodische Begründung samt Literaturbezug steht in den
Projektdateien `docs/cib_role.md` und `docs/cib_rationale.md`.
