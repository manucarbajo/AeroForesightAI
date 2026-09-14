Begriffe, wie sie in dieser Anwendung gebraucht werden.

## A bis F

**Agent** — Einer der drei Akteure, umgesetzt als Sprachmodell mit beschränkter
Sicht und beschränkten Rechten. Siehe [Die drei Akteure](/doku/akteure).

**Annahmenwelt** — Die Ausgangslage eines Laufs: Faktorzustände plus die
zugehörigen Zahlen für Politik, Kosten und Konjunktur. Als Datei gespeichert
heißt sie Preset.

**Auslastung** — Hier gleichbedeutend mit Buchungsrate. Nicht die Auslastung
eines einzelnen Flugzeugs.

**Bedienfeld** — Die linke Zone des Leitstands: was eingestellt ist, der
Preflight, der Start-Knopf. Bewusst **kein** Formular — eingestellt wird im
Bereich «Einrichten». So bleibt der Start-Knopf immer sichtbar, statt hinter
sechzig Eingabefeldern zu verschwinden.

**Beispieldatensatz** — Was der Leitstand zeigt, solange kein einziger Lauf
gerechnet wurde: erfundene, aber plausible Zahlen, damit die Ansicht nicht leer
bleibt. Er ist überall als solcher markiert — Abzeichen in der Kopfzeile, Banner
über dem Viewport, eigene Farbe — und verschwindet mit dem ersten echten Lauf.
Er wird nirgends gespeichert.

**Buchungsrate** — Anteil der simulierten Bevölkerung, der sich in einem Tick
für eine Reise entscheidet. Ergebnis vieler Einzelentscheidungen, kein
Parameter.

**CIB** — Cross-Impact-Bilanzanalyse. Verfahren, das bewertet, ob eine
Kombination von Faktorzuständen in sich stimmig ist. Siehe
[CIB-Konsistenzprüfung](/doku/cib).

**Dämpfung** — Bremst die Preisreaktion der Airline. Niedrige Werte ergeben
ruhigere Preisverläufe.

**Einrichten** — Der Bereich, in dem ein Lauf festgelegt wird, und der erste in
der Navigation: Man richtet ein, sieht dann zu, und wertet zuletzt aus. Er
beginnt mit dem **Einstieg** und läuft danach als Schrittfolge; dabei bekommt
er den ganzen Bildschirm — Bedienfeld, Telemetrie und Zeitleiste treten zurück.
Gestartet wird am Ende der Schrittfolge; der Knopf im Bedienfeld tut dasselbe.

**Einstieg** — Die Auswahl, die beim Öffnen von «Einrichten» steht: neuen Lauf
einrichten, Szenario-Vergleich starten, oder die letzten Einstellungen
weiterverwenden. Die ersten beiden legen zugleich fest, ob *ein* Lauf gerechnet
wird oder *alle* Szenarien; der dritte fasst nichts an.

**Faktor** — Eine von sieben Zustandsvariablen, die die Welt in groben Zügen
beschreiben, jeweils mit zwei möglichen Zuständen. Siehe
[Faktoren F1–F7](/doku/ref-faktoren).

## G bis P

**Grenzkosten** — Der Teil der Stückkosten, unter den der Ticketpreis nie fällt.
Über die Preisuntergrenze einstellbar.

**Konsistenz** — Maß dafür, wie **widerspruchsfrei** die gleichzeitig
angenommenen Faktorzustände zusammenpassen. Ergebnis der CIB-Bewertung. Der Wert
ist hoch, wenn alle Faktoren in dieselbe Richtung zeigen, und niedrig bei
gemischten Lagen — er sagt damit **nichts über die Wahrscheinlichkeit** einer
Zukunft. In den Laufdateien steht er als `consistency_score` mit dem Band
`widerspruchsfrei` / `gemischt` / `spannungsreich`. Ausführlich:
[CIB-Konsistenzprüfung](/doku/cib).

**Schrittfolge** — Die Form des Einrichtens seit August 2026: eine Frage je
Bildschirm, mit «Zurück» und «Weiter» und einer Liste aller Schritte daneben.
Drei davon genügen bis zum Start, der Rest ist optional. «Zurück» auf dem ersten
Schritt führt zurück auf den **Einstieg**.

**Ladebildschirm** — Was der Leitstand zeigt, solange ein Lauf rechnet: wie weit
er ist, was er rechnet, und die aufgeklappte Konsole. Er tritt an die Stelle der
Szene, weil die währenddessen einen anderen, älteren Lauf zeigen würde.

**Fortschrittsfenster** — Die kleine Anzeige unten rechts, die den laufenden Lauf
im Blick behält, während man in einem anderen Bereich arbeitet. Sie zeigt und
führt zum Ladebildschirm; abbrechen kann man von dort nicht.

**Lauf** — Eine Folge von Ticks aus einer festgelegten Ausgangslage. Erzeugt ein
eigenes Verzeichnis unter `outputs/`.

**Leitstand** — Der Bereich, in dem ein Lauf läuft und sich beobachten lässt:
Kopfzeile, Bedienfeld links, Szene in der Mitte, Kennzahlen rechts, Zeitleiste
unten. Gedacht für den Fall, dass Einstellung und Wirkung gleichzeitig im Blick
bleiben sollen. **Seit September 2026 der einzige Bereich mit diesen Seitenzonen** —
Einrichten, Ergebnisse, Modell und Handbuch bekommen den Bildschirm allein.

**Logit-Modell** — Das Verfahren, mit dem aus den Merkmalen einer Person eine
Buchungsentscheidung wird. Siehe
[Wie eine Buchung entsteht](/doku/kaufentscheidung).

**Marge** — Der Aufschlag der Airline auf die Kosten. Zusammen mit dem
Kostenanteil ergibt er den Ticketpreis.

**Ohne Sprachmodell** — Rechenmodus, in dem kein Sprachmodell befragt wird (in der
Kommandozeile `--mock-llm`). Die Kennzahlen sind unverändert, die Agenten-Texte
sind Platzhalter.

**Preset** — Eine gespeicherte Annahmenwelt unter `configs/sweeps/`. Siehe
[Szenario-Presets](/doku/ref-presets).

## R bis Z

**Redebedarf** — Betriebsart, in der sich Akteure nur äußern, wenn sich für sie
etwas Wesentliches geändert hat.

**Rahmenszenario** — Ein benanntes Bündel äußerer Entwicklungen: Was die Welt
dem Modell vorgibt, nicht was im Modell herauskommt. Jedes trägt seine
**Begründung mit Quellen** — die Kohaerenz wird in Prosa belegt, es gibt keinen
Algorithmus dafür. Belegt ist dabei immer die *Geschichte*, nicht ihre
Bezifferung: Bei welchem Tick die CO₂-Abgabe auf welchen Wert springt, ist
gesetzt und nicht aus Daten geschätzt. Welche Zeitspanne es beschreibt, sagt
jedes Rahmenszenario in seinem Vorbehalt. Siehe [Presets](/doku/presets).

**Kennung** (eines Laufs) — Eindeutiger Name eines Laufs, zugleich der Name
seines Ausgabeverzeichnisses, etwa `run_20260913_142530`.

**SAF** — Sustainable Aviation Fuel, nachhaltiger Flugtreibstoff. Als Quote eine
Systemgröße, die die Kosten der Airline erhöht.

**Sättigung** — Dämpfung der Buchungsneigung nach einer Reise. Siehe
[Sättigung](/doku/saettigung).

**Segment** — Eine Personengruppe mit eigenem Verhalten, etwa Vielflieger oder
preissensible Reisende. Anteile sind unabhängig; eine Person kann mehreren
Segmenten angehören.

**Stresstest** — Ein hinterlegtes Szenario, das die Engine belastet oder die
Darstellung prüft, statt eine Zukunft zu behaupten. Seine Verläufe fahren durch
Extreme, damit man sieht, ob etwas bricht. In der Auswahl steht das Wort an der
Kachel; ein Szenario-Vergleich lässt ihn aus. Gegenstück zum
**Rahmenszenario**.

**Systemgröße** — Eine der Zahlen hinter den Faktoren: CO₂-Abgabe, SAF-Quote,
Ölpreis, Einkommensindex und weitere. Siehe
[Systemgrößen](/doku/ref-systemgroessen).

**Szene** — Die Darstellung in der Mitte des Leitstands: die simulierte
Bevölkerung zu **einem** Tick, jeder Punkt eine Person. Sie folgt der
Zeitleiste; ihre Achsen stehen über den ganzen Lauf fest, damit eine Bewegung im
Bild eine Bewegung der Bevölkerung ist und nicht eine nachgeführte Achse.

**Szenario** — Eine mögliche Fortsetzung nach dem Lauf, nicht der Lauf selbst.
Jeder Lauf erzeugt drei davon.

**Tick** — Ein Rechenschritt des Modells. **In der Mechanik ein Monat** (seit dem 7. September 2026): Alles, was sich pro Tick verändert, rechnet in Monaten, vierzig Ticks sind gut drei Jahre. **Ein Datum ist ein Tick trotzdem nicht** — er lässt sich auf keine Jahreszahl abbilden. Siehe
[Tick, Lauf und Szenario](/doku/tick-und-lauf).

**Telemetrie** — Der rechte Bereich des Leitstands: Kennzahlen des gewählten
Ticks, dieselben Größen als Verlauf, und die Konsole mit Ereignissen,
Modellausfällen und dem Fortschritt eines laufenden Laufs.

**Tripleset** — Die drei Szenarien am Ende eines Laufs: Trend-Fortsetzung,
Alternative und Spannungs-Szenario.

**Yield Management** — Die Praxis, Preise laufend an die beobachtete Nachfrage
anzupassen. Im Modell der Regelkreis unter
[Wie der Preis entsteht](/doku/preisbildung).

**Zahlungsbereitschaft** — Der Betrag, den eine Person höchstens für ein Ticket
auszugeben bereit ist. Im Englischen WTP, willingness to pay.

**Zeitleiste** — Die Leiste am unteren Rand des Leitstands. Sie ist die
**einzige** Zeitachse der Oberfläche: Szene, Kennzahlen und Verläufe folgen alle
dem Tick, der hier eingestellt ist. Die Marker darunter zeigen, wo im Lauf etwas
passiert ist.

**Zufallsstartwert** — Legt fest, welche Bevölkerung gezogen wird. Ein einzelner
Lauf ist **auch ohne eigenen Startwert** wiederholbar: Dann gilt ein
Standardwert, nicht der Zufall. Welcher es war, steht nach dem Lauf im Tab
**Übersicht** und in `run_metadata.json`. Einen eigenen Startwert setzen Sie,
wenn Sie denselben Aufbau bewusst mit einer anderen Ziehung sehen wollen. Siehe
[Einen Lauf starten](/doku/lauf-starten).
