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

**Buchungsrate** — Anteil der simulierten Bevölkerung, der sich in einer Runde
für eine Reise entscheidet. Ergebnis vieler Einzelentscheidungen, kein
Parameter.

**CIB** — Cross-Impact-Bilanzanalyse. Verfahren, das bewertet, ob eine
Kombination von Faktorzuständen in sich stimmig ist. Siehe
[CIB-Konsistenzprüfung](/doku/cib).

**Dämpfung** — Bremst die Preisreaktion der Airline. Niedrige Werte ergeben
ruhigere Preisverläufe.

**Einrichten** — Der Bereich, in dem ein Lauf festgelegt wird: die drei
Entscheidungen und darunter alle weiteren Einstellungen. Er nimmt die volle
Breite ein, weil Konfiguration Fläche braucht; gestartet wird trotzdem links im
Bedienfeld, das dabei sichtbar bleibt.

**Faktor** — Eine von sieben Zustandsvariablen, die die Welt in groben Zügen
beschreiben, jeweils mit zwei möglichen Zuständen. Siehe
[Faktoren F1–F7](/doku/ref-faktoren).

## G bis P

**Grenzkosten** — Der Teil der Stückkosten, unter den der Ticketpreis nie fällt.
Über die Preisuntergrenze einstellbar.

**Konsistenz** — Maß dafür, wie gut die gleichzeitig angenommenen Faktorzustände
zusammenpassen. Ergebnis der CIB-Bewertung.

**Lauf** — Eine Folge von Ticks aus einer festgelegten Ausgangslage. Erzeugt ein
eigenes Verzeichnis unter `outputs/`.

**Leitstand** — Die Form der Oberfläche: ein Bildschirm mit fünf Bereichen —
Kopfzeile, Parameter links, Viewport in der Mitte, Telemetrie rechts, Zeitleiste
unten — statt mehrerer Seiten hintereinander. Gedacht für den Fall, dass
Einstellung und Wirkung gleichzeitig im Blick bleiben sollen.

**Logit-Modell** — Das Verfahren, mit dem aus den Merkmalen einer Person eine
Buchungsentscheidung wird. Siehe
[Wie eine Buchung entsteht](/doku/kaufentscheidung).

**Marge** — Der Aufschlag der Airline auf die Kosten. Zusammen mit dem
Kostenanteil ergibt er den Ticketpreis.

**Mock** — Betrieb ohne Sprachmodell. Die Kennzahlen sind unverändert, die
Agenten-Texte sind Platzhalter.

**Preset** — Eine gespeicherte Annahmenwelt unter `configs/sweeps/`. Siehe
[Szenario-Presets](/doku/ref-presets).

## R bis Z

**Redebedarf** — Betriebsart, in der sich Akteure nur äußern, wenn sich für sie
etwas Wesentliches geändert hat.

**Run-ID** — Eindeutige Kennung eines Laufs, zugleich der Name seines
Ausgabeverzeichnisses.

**SAF** — Sustainable Aviation Fuel, nachhaltiger Flugtreibstoff. Als Quote eine
Systemgröße, die die Kosten der Airline erhöht.

**Sättigung** — Dämpfung der Buchungsneigung nach einer Reise. Siehe
[Sättigung](/doku/saettigung).

**Segment** — Eine Personengruppe mit eigenem Verhalten, etwa Vielflieger oder
preissensible Reisende. Anteile sind unabhängig; eine Person kann mehreren
Segmenten angehören.

**Systemgröße** — Eine der Zahlen hinter den Faktoren: CO₂-Abgabe, SAF-Quote,
Ölpreis, Einkommensindex und weitere. Siehe
[Systemgrößen](/doku/ref-systemgroessen).

**Szene** — Die Darstellung in der Mitte des Leitstands: die simulierte
Bevölkerung zu **einem** Tick, jeder Punkt eine Person. Sie folgt der
Zeitleiste; ihre Achsen stehen über den ganzen Lauf fest, damit eine Bewegung im
Bild eine Bewegung der Bevölkerung ist und nicht eine nachgeführte Achse.

**Szenario** — Eine mögliche Fortsetzung nach dem Lauf, nicht der Lauf selbst.
Jeder Lauf erzeugt drei davon.

**Tick** — Eine Modellrunde. Ohne Kalenderbedeutung. Siehe
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
