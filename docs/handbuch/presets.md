Ein Szenario-Preset ist eine gespeicherte Annahmenwelt. Statt bei jedem Lauf
Faktoren, Politik und Kosten einzeln einzustellen, wählen Sie eines aus und
passen davon ausgehend an.

Die mitgelieferten Presets stehen mit Beschreibung und Begründung unter
[Szenario-Presets](/doku/ref-presets).

## Zwei Arten von Preset

Unter den hinterlegten Szenarien liegen zwei verschiedene Dinge, und seit dem
2026-08-31 sagen sie es auch:

**Ein Rahmenszenario** ist eine begründete Behauptung über eine mögliche Welt —
«Business as Usual», «CO₂-Verzögerung», «Freiwillige Wende»,
«Transformationskonflikt». Sobald Sie eines auswählen, steht unter dem Raster,
*was* es behauptet und *warum* diese Entwicklungen zusammen eine Welt ergeben;
unter «Quellen und was davon nicht belegt ist» finden Sie die Belege und —
ebenso wichtig — den Vorbehalt.

Denn belegt ist immer die Geschichte, **nicht ihre Bezifferung**: Dass strenge
Regulierung ohne verfügbaren Ausweichpfad zur reinen Verteuerung wird, ist
begründbar. Bei welchem Tick die CO₂-Abgabe dann auf welchen Wert springt, ist
gesetzt und nicht aus Daten geschätzt. Wer ein Szenario nach außen zitiert,
zitiert die Geschichte, nicht die Zahl.

**Auch «keine Auswahl» ist eine Auswahl.** Wer kein Szenario nimmt, rechnet unter der
**Standard-Ausgangslage** — und das ist kein Nullpunkt, sondern ein Weltbild mit
eigenen Annahmen über Politik, Kosten und Konjunktur. Seit dem 2026-09-03 steht seine
Begründung an derselben Stelle wie die der vier Szenarien, mit Quellen und Vorbehalt.
Wer eigene Werte zusammenstellt, findet dort stattdessen den Hinweis, dass es für sie
keine hinterlegte Begründung gibt — die muss man dann selbst liefern.

**Seit dem 2026-09-03 sagt jedes Rahmenszenario auch etwas über das Angebot.**
Bis dahin beschrieben die vier Welten nur, was auf den Luftverkehr *einwirkt* —
CO₂-Preis, Beimischung, Konjunktur, Ölpreis — und ließen offen, wie viele Sitze
es gibt. Damit unterstellten sie stillschweigend eine unveränderte Kapazität, und
das ist eine Aussage über die Welt und keine Abwesenheit einer Aussage: In
«Business as Usual» wächst das Angebot mit, in der «Freiwilligen Wende» stagniert
es, im «Transformationskonflikt» geht es zurück.

**Dazu gehört, wie der Anbieter preist.** Zwei Möglichkeiten stehen zur Wahl: Er
senkt den Preis, bis die Sitze voll sind, oder er hält seinen Aufschlag und nimmt
eine schwankende Auslastung in Kauf. Beides kommt vor, und welches gilt, ist eine
Frage an die Welt und nicht an das Modell — deshalb steht es jetzt in der Datei
des Szenarios. Drei der vier Rahmen wählen den Wettbewerbsfall, der
«Transformationskonflikt» den anderen.

Beides ist im Text des Szenarios begründet, und beides trägt denselben Vorbehalt
wie der Rest: **Die Richtung ist argumentiert, die Zahlen sind gesetzt.**

**Ein Stresstest** ist ein Belastungs- oder Sichtprüfungslauf der Engine. Seine
Verläufe fahren durch Extreme, damit man sieht, ob etwas bricht — sie behaupten
nichts über die Zukunft. Die Kachel schreibt «Stresstest» davor, und ein
Szenario-Vergleich lässt ihn aus.

## Ein Preset verwenden

Unter **Simulation starten** ist die Auswahl die erste der drei Entscheidungen.
Jedes Preset steht dort mit seiner Beschreibung; aufklappbar daneben die
Begründung, warum es so aufgebaut ist.

**Das gewählte Preset gilt unverändert.** Politik, Kosten und Nachfrageumfeld kommen
aus seiner Datei unter `configs/sweeps/`; was Sie unten unter «Alle
Einstellungen» eingestellt haben, bleibt dafür außen vor. Genau eine Größe
bleibt Ihre Entscheidung: die **Länge** des Laufs. Auf wie viele Ticks ein
Preset angelegt ist, steht neben seiner Beschreibung — seine Meilensteine sind
auf diese Länge hin gedacht.

**Im Szenario-Vergleich gilt das nicht.** Wer alle Szenarien nacheinander
rechnen lässt, stellt keine Länge ein: Jedes läuft so lang, wie es angelegt ist.
Alles andere hieße, Szenarien unterschiedlicher Bauart über einen Kamm zu
scheren — ein auf 50 Ticks entworfenes Szenario erreicht seinen Schlusspunkt
nach 40 Ticks schlicht nicht.

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

So oder so wird jedes **Rahmenszenario** einmal durchgerechnet, ohne
Agenten-Dialog und damit deutlich schneller. Die Ergebnisse liegen unter
`outputs/sweeps/` und erscheinen einzeln in der Lauf-Auswahl.

Das ist der schnellste Weg zu der Frage, wie weit die Annahmenwelten überhaupt
auseinanderliegen.

**Die Stresstests sind dabei nicht dabei**, und das ist seit dem 2026-08-31 so.
Unter den hinterlegten Dateien liegen zwei verschiedene Dinge: begründete
Weltbilder und Belastungstests der Engine. Ein Vergleich stellt Weltbilder
gegeneinander — ein Stresstest, dessen Verläufe auf Sichtbarkeit gebaut sind,
gehört nicht als Zukunft daneben. Starten lässt er sich weiterhin einzeln; in
der Auswahl steht «Stresstest» an seiner Kachel.

## Meilensteine

Manche Presets bringen Meilensteine mit: Erwartungen der Form «ab Runde 10 sollte
die CO₂-Abgabe bei 50 liegen». Sie beschreiben, wie das Szenario gemeint ist, und
helfen beim Gegenlesen eines Laufs. In der Referenz sind sie je Preset
aufgeführt.
