# Entscheidung: das Gestaltungssystem (D1)

**Stand 2026-09-12 · entschieden (Haiko, siehe «Die Entscheidung» unten) · Grundlage für [P7.1](projektplan.md#p71--ein-gestaltungssystem-statt-einzelregeln--erledigt-2026-09-13) und die beiden letzten Wächter aus [P7.0](projektplan.md#p70--messfundament-für-die-gestaltung--offen)**

Das UI/UX-Audit vom 2026-09-11 stellt D1 als Ja/Nein-Frage: «Ein Gestaltungssystem
in Tokens vor jeder Ansichtsarbeit?», mit der Empfehlung «Ja». Das Ja/Nein ist
der leichte Teil. **Die eigentliche Entscheidung sind die Werte darin**, und
diese Vorlage legt sie als fünf Einzelfragen hin — je mit dem gemessenen
Ist-Stand, einem Vorschlag und dem, was er kostet.

Sie ist nach demselben Muster geschrieben wie die
[Angebotsseite](entscheidung_angebotsseite_2026-08-31.md) und die
[Szenarienschicht](entscheidung_szenarienschicht_2026-08-29.md): Jede Zahl ist
nachgemessen, jeder Vorschlag nennt seinen Preis, und wo ein Vorschlag auf einer
Abwägung statt auf einer Messung steht, sagt er das.

**Warum jetzt.** Zwei der sechs Wächter aus P7.0 lassen sich ohne diese
Entscheidung nicht bauen: U0.1 misst, ob Texte an einer gemeinsamen Kante enden
— die Kante entsteht erst mit E3; U0.2 misst, ob Schriftgrößen einer Skala
folgen — die Skala entsteht erst mit E1. Und der Befund, mit dem das Audit
angefangen hat (ein Text auf der halben Spalte), hängt an E3.

---

## Die Entscheidung

**Am 2026-09-12 von Haiko getroffen — alle fünf Fragen wie vorgeschlagen.** D1
selbst ist damit «Ja»: Das Gestaltungssystem kommt in Tokens, vor jeder
Ansichtsarbeit.

| # | Frage | Entschieden |
| --- | --- | --- |
| **E1** | Schriftrollen | **Sieben Rollen, kleinste 12 px.** 11 px entfällt; 30, 22 und 17 px verschwinden ersatzlos. Die Konsole wird dadurch höher, und die Deckel des Höhenwächters wandern bewusst mit. |
| **E2** | Textfarbstufen | **Zwei lesbare, eine gedämpfte, eine für Abgeschaltetes.** `--text-muted` wird 1,5 % dunkler (`#64748b` → `#617087`), `--text-faint` verliert seine Rolle als Textfarbe. |
| **E3** | Lesemaß | ~~38 rem = 608 px, gesetzt am Container.~~ **Am selben Tag zurückgenommen: das Lesemaß fällt ganz** — Fließtext füllt seinen Rahmen. Gedeckelt werden nur Eingaben (`--breite-feld-*`, an der Eingabe statt am Feld) und die Seite (`--breite-inhalt`); `--breite-formular` ist ebenfalls gefallen. Siehe den zweiten und dritten Nachtrag. |
| **E4** | Abstände | **4-px-Raster mit acht Stufen** (4, 8, 12, 16, 24, 32, 48, 64). Werte unter 4 px bleiben für Rahmen erlaubt, mit Begründung. **Am 2026-09-13 ergänzt:** Gleichstand wird abgerundet, Knöpfe bekommen 44 px — siehe den Nachtrag vom 2026-09-13. |
| **E5** | Bausteine | **Vollständig, einschließlich des gestalteten Bestätigungsdialogs.** Damit ist **D7 mitentschieden**. |
| **D3** | Begründungen | **These und zwei Sätze sichtbar, in Fließtextgröße; der Rest hinter einer Klappe «Begründung und Quellen».** Am selben Tag nachentschieden, weil E3 ohne D3 nicht baubar war — siehe den Nachtrag unten. |

**Was daraus folgt, und zwar sofort:** Der Höhenwächter bekommt neue Deckel, und
`dcc.ConfirmDialogProvider` verschwindet aus `dashboard/web/` — das ist das
Abnahmekriterium von P7.1. **Die Zusage aus P1.9-W5.4** sollte dabei zunächst nur
vom Element an den Container wandern; sie ist am selben Tag ganz
zurückgenommen und durch ihr Gegenteil ersetzt worden — siehe den zweiten
Nachtrag.

**Nachtrag vom selben Tag: D3 ist mitentschieden, und E3 musste dafür warten.**
Der erste Anlauf von U1.2 ist an einer Zusage gescheitert, die diese Vorlage
nicht geprüft hatte: **608 px tragen bei 15 px rund 66 Zeichen, bei 14 px aber
88 und bei 12 px 106** — die Zusage aus P1.9-W5.4 (höchstens 75 Zeichen je
Zeile) bricht also, sobald ein Block mit festem Pixeldeckel Text in mehreren
Größen enthält. Genau deshalb stand das Lesemaß bis dahin in `ch`. Der Wert 38
rem in E3 ist für Fließtext gerechnet und war für die kleineren Rollen nicht
geprüft; das ist ein Fehler dieser Vorlage.

**Die Regel, die daraus folgt:** Ein Leseblock hat **eine** Textgröße. Der
Kohärenzblock verletzte sie (These 14 px, Begründung 12 px) — und das ist
derselbe Block, den das Audit unter Q6 ohnehin beanstandet. **D3 ist deshalb
vorgezogen und entschieden:** Sichtbar sind These und die ersten zwei Sätze der
Begründung, beide in Fließtextgröße; Restbegründung, Quellen und Vorbehalt
liegen hinter einer Klappe «Begründung und Quellen». Sichtbar sind damit 513 bis
787 Zeichen je Szenario statt 1163 bis 2429. **E3 bleibt wie entschieden** — es
ist jetzt baubar, weil der Block eine Größe hat. *(Dieser letzte Satz hat noch
am selben Tag aufgehört zu gelten; siehe den zweiten Nachtrag.)*

**Was offen bleibt:** D2, D4, D5 und D6 des Audits. Sie hängen an
Produktfragen, nicht an den Tokens.

**Zweiter Nachtrag vom selben Tag: E3 ist zurückgenommen — das Lesemaß fällt
ganz.** Anlass war der Blick auf den fertigen Schritt 1: Text und Überschrift
füllten die Spalte nur zur Hälfte. Nachgemessen im Browser bei 1440 px, Spalte
760 px:

| Text in Schritt 1 | Breite | Anteil | Schrift | Zeichen/Zeile |
| --- | ---: | ---: | ---: | ---: |
| Lede unter der Überschrift | 409 px | **53,8 %** | 12 px | **72** |
| These des Kohärenzblocks | 495 px | 65,1 % | 15 px | 69 |
| Begründungsabsatz | 509 px | **67,0 %** | 15 px | **72** |
| Quellenzeile | 343 px | 45,1 % | 12 px | 57 |

**Der Deckel war nicht zu eng, er war ausgereizt.** Die Lede trug auf ihren
409 px schon 72 der 75 erlaubten Zeichen. Gemessen sind es 7,17 px je Zeichen
bei 15 px Schrift — **um 760 px mit höchstens 75 Zeichen zu füllen, müsste der
Fließtext rund 21 px groß sein.** «Text füllt seine Spalte» und «höchstens 75
Zeichen je Zeile» sind bei dieser Spaltenbreite nicht gleichzeitig erfüllbar;
E1 hat die Schriftgröße schon entschieden, also fällt die andere Zusage.

**Entschieden:** Alle Deckel für Fließtext fallen. `--breite-formular` (die
Breite eines kurzen Formulars) und `--breite-inhalt` (der Rahmen der Seite)
bleiben — sie deckeln Bedienelemente und Seiten, keine Sätze. *(Für
`--breite-formular` hat das noch am selben Tag aufgehört zu gelten: Sein
einziger Nutzer deckelte gemessen Prosa. Siehe den dritten Nachtrag.)*

**Das Argument dafür ist gemessen, nicht ästhetisch:** Die 75-Zeichen-Zusage
schützt den Rücksprung des Auges über *viele* Zeilen. Fast jeder Text im
Assistenten ist 150 bis 300 Zeichen lang und steht bei voller Breite auf einer
bis zwei Zeilen — der Rücksprung, um den es geht, kommt dort kaum vor. Dreißig
Prozent der Breite für einen Zweizeiler zu opfern ist der falsche Tausch.

**Der Preis, gemessen statt geschätzt.** Nach dem Umbau zählt der
Browser-Wächter als längste gesetzte Zeile:

| Ort | längste Zeile |
| --- | ---: |
| Bereich «Modell» | **168 Zeichen** |
| Ergebnisse / Übersicht | 135 |
| Leitstand | 128 |
| Schritt 1 | 119 |
| Handbuch | 76 |

Die 106 Zeichen, mit denen die Entscheidung gerechnet wurde, gelten für eine
760 px breite Spalte; wo der Rahmen bis `--breite-inhalt` (1088 px) reicht, sind
es mehr. **168 Zeichen liegen weit über jeder typografischen Empfehlung.** Das
ist eine bewusste Entscheidung für diese Oberfläche und keine Erkenntnis über
Lesbarkeit — und es ist die Zahl, an der man sie später bestreiten kann.

**Die Zusage wird nicht gelöscht, sondern umgedreht.** An die Stelle von
«höchstens 75 Zeichen je Zeile» tritt: **Kein Prosablock wird schmaler gesetzt
als der Platz, den er hat.** Gemessen wird je Block im Browser, am Verhältnis
seiner Breite zur verfügbaren Breite seines Elternelements — nicht an einer
Klassenliste, und mit Mutationsprobe.

**Dabei ist eine Zuschreibung von mir falsch gewesen, und das gehört dazu.**
Zuerst hieß es hier, der bisherige Wächter (`FUELLUNG_MIN = 60`) messe nur
`input, select, textarea, button, img, svg` und damit keinen Text.
Nachgelesen stimmt das nicht: Die Zeichenschleife speist dieselbe Messung mit
den Textrechtecken. **Blind war er aus einem anderen Grund** — er misst *eine
Hüllbreite* für den ganzen Schritt, von der linkesten bis zur rechtesten Tinte.
Schritt 1 ist voll von Auswahlkarten, deren Raster die Spalte füllt; die
Füllung stand bei ~100 %, während die Lede daneben auf 53,8 % lag. Eine
Hüllbreite kann nicht sehen, dass *innerhalb* von ihr ein Absatz die Hälfte
leer lässt. Die Konsequenz ist dieselbe, die Lehre eine andere: nicht «Text
zählt nicht mit», sondern **eine Summe über eine Fläche findet keinen Befund an
einem einzelnen Block**.

**Und der neue Wächter musste gegen seine eigene Blindheit geprüft werden**, weil
er beim ersten scharfen Durchlauf sofort grün war. Gezählt: 52 Prosablöcke über
die sechs Schritte, 2 bis 194 je Ansicht, alle bei 99,8 bis 100,2 %. Eine
Auswahl, die Bedienelemente, Code, Tabellen, Navigationsmarken und jedes Kind
eines Flex- oder Grid-Containers überspringt, könnte am Ende nichts übriglassen
und wäre dann trivial erfüllt; `PROSA_BLOECKE_MIN = 30` hält das fest.

**Und U1.2 ist damit zum größeren Teil wieder abgeräumt**, am Tag seiner
Fertigstellung. Was bleibt, ist die Arbeit, die trägt: dass es überhaupt Tokens
gibt, dass Deckel am Block statt am Element sitzen, und die drei gemessenen
Fehlschläge, die jetzt als Zusagen dastehen. Was fällt, ist der Wert — und der
war die Entscheidung dieser Vorlage, nicht die des Pakets.

**Ein zweiter Befund über U1.2 kam beim Abräumen heraus:** Es hat die
`af-*`-Deckel vereinheitlicht und die **Tailwind-Deckel übersehen**. `max-w-md`,
`max-w-2xl` (3×), `max-w-3xl` (4×) und `max-w-4xl` standen weiter an Prosa,
während das Paket «zwei Textbreiten» meldete — darunter der Kapitelrumpf des
Handbuchs und die Erzählung eines Laufs. Sie sind jetzt weg, und was an
Bedienelementen bleibt, steht als Sperrklinke mit Grund in
`tests/test_web_breiten.py`. **Von den gefallenen Prosa-Deckeln lag kein
einziger in der Schrittfolge** — ein Wächter, der nur die Schritte abgeht, hätte
alle durchgelassen; deshalb messen die neuen Zusagen über alle Bereiche.

**Dritter Nachtrag vom selben Tag: Das Lesemaß hatte sich in den Eingabefeldern
versteckt.** Beim Umbau der 13 übrig gebliebenen Tailwind-Deckel zu Tokens kam
heraus, dass ihre Begründungen nicht stimmten. Die Sperrklinke nannte sie
«Zahlenfeld Ticks», «Zahlenfeld Checkpoint-Intervall» — gemeint war eine
Eingabe. `ui.field` legte die Breitenklasse aber auf den **Rahmen** um
Beschriftung, Eingabe, Hinweis und Glossar-Erklärung. «Zahlenfeld Ticks» hieß
in Wahrheit: die Erklärung zu Ticks in einem 320 px breiten Streifen mitten in
einer 760 px breiten Karte. Elf Felder standen so da. **Eine Begründung, die
niemand am gezeichneten Baum nachgeprüft hat, ist eine Behauptung** — und genau
davor sollte die Liste schützen.

**Der Wächter aus dem zweiten Nachtrag hat es nicht gesehen, und der Grund ist
benennbar:** Er verglich einen Absatz nur mit seinem direkten Elternelement.
Der Hinweis füllte seinen Rahmen, der Rahmen stand auf 320 px, die Messung sah
100 %. Er prüft jetzt jede Ebene bis zum ersten Flex- oder Grid-Container, und
gegen den alten Code gemessen meldete er die Feldrahmen sofort (etwa der Hinweis
unter dem Startwert einer Systemgröße: 320 von 1006 px, 31,8 %).

**Dabei hat er zwei Klassen Fehlalarme geliefert, und beide sind jetzt Regeln:**
den **Seitenrahmen** (`.af-pane--focus`, 1088 px in 1280 px — jeder Text im
Einstieg und im Modell mit 85 %), deshalb endet der Aufstieg am Token
`--breite-inhalt`; und die **Einrückung** unter einem Kästchen (94,7 %), die
Ausrichtung ist und dem Kantenwächter gehört, deshalb zählt ein Rand als Platz,
ein `max-width` nicht. Ein dritter kam aus einem Plotly-Diagramm (Text in einem
SVG-`<g>`); SVG ist ausgenommen wie im Überlauf-Detektor.

**Was jetzt gilt:** Die Breite einer Eingabe gehört an die Eingabe
(`ui.field(breite=…)`, drei Stufen `--breite-feld-klein`/`-feld`/`-feld-weit`
mit 160/320/512 px); Beschriftung, Hinweis und Erklärung füllen den Rahmen. Fünf
Tailwind-Werte sind drei Stufen geworden — sichtbar schmaler werden drei
Zahlenfelder des Buchungs- und Sättigungsmodells (384 → 320 px) und die
Textfläche für die Fragestellung (672 → 512 px). Die eine Breite, die Bedeutung
trägt, hat ein eigenes Token: die Sprechblase im Explorer.

**Und der Rumpf-Deckel ist gefallen, gemessen statt vermutet.** Nach dem Umbau
blieb in «Wie weit reicht der Lauf?» genau ein Befund: `af-body--lesen`, 480 px
— der Schrittrumpf aus W5.4, der ein einsames Feld nicht in einer breiten
Spalte stehen lassen wollte. Dieses Anliegen ist jetzt an der Eingabe gelöst;
übrig blieb nur der Satz-Deckel. Mit ihm ist `--breite-formular` gefallen, dessen
einziger Nutzer er war — der zweite Nachtrag hatte das Token noch als bleibend
genannt. «Lauf & Ablage» ist ohne ihn von 1,22 auf 1,16 Schirme gefallen.

**Nachtrag vom 2026-09-13: Wohin ein Wert zwischen zwei Stufen geht (E4).**
Die Skala hatte beantwortet, *welche* Abstände es gibt, nicht, wohin einer
fällt, der genau dazwischen liegt — und das war die Mehrheit: 6, 10, 14, 20, 28
und 40 px. Zwei Entscheidungen, beide von Haiko:

1. **Ein Gleichstand wird abgerundet** (6 → 4, 10 → 8, 20 → 16, 28 → 24,
   40 → 32). Abgewogen gegen Aufrunden (luftiger, aber fast jeder Schritt wächst
   und «Was soll gerechnet werden?» rückt von einem Schirm weg) und gegen eine
   Regel nach Rolle (innen ab, außen auf — feiner, aber eine Regel mehr, die ein
   Wächter halten muss). Der Grund: Die Oberfläche ist dicht, und die
   Schritthöhe trägt eine Zusage.
2. **Knöpfe weichen ab und bekommen 44 px.** Rund 40 px hoch, wären sie
   abgerundet 36 px geworden; aufgerundet sind sie so hoch wie die übliche
   Mindestgröße einer Trefferfläche. Die Ausnahme gilt senkrecht; waagerecht
   folgen sie der Regel.

Umgesetzt mit U1.3 Teil B: 45 Deklarationen im Stylesheet und 50
Tailwind-Klassen in 17 Dateien. Werte, die keine Abstände sind, sondern
Geometrie, folgen der Rundung nicht und stehen mit Grund im Wächter.

**Nachtrag vom selben Tag: eine Lede ist Fließtext.** Sie war zweierlei — die
eines Schritts stand in der Rolle einer Bildunterschrift (12 px), die eines
Blocks in `af-md--lede` (14 px) —, und beide waren damit kleiner als der
Fließtext, den sie einleiten. Gemessen war die Schritt-Lede der **schmalste
Text des Bildschirms**: 409 px von 760, weil 12-px-Prosa für 75 Zeichen nur
416 px braucht; auf diesen 409 px trug sie schon 72 der 75 erlaubten Zeichen.
Es ist jetzt **eine** Rolle in **einer** Größe (`components.LEDE`), und die
Regel `af-md--lede` ist weg statt umgestellt: `.af-md` setzt die 15 px ohnehin,
und eine Regel, die nur eine Größe wiederholt, ist eine Stelle zu viel, an der
sie auseinanderlaufen kann. Die Rollenfrage war für U1.4 vorgemerkt und ist
vorgezogen, weil sie an keiner anderen Entscheidung hängt.

---

## Wie gemessen wurde

| Was | Wie |
| --- | --- |
| Schriftgrößen, Textbreiten, rechte Kanten | Kopfloser Chromium über alle fünf Bereiche bei 1440 × 900, dazu Schritt 1 einzeln mit aufgeklappten Schubladen. Gezählt wurde je Element der **eigene** Textknoten, nicht der geerbte; Symbolschrift ausgenommen. |
| Kontraste | Gerechnet aus `theme.PALETTE` nach WCAG 2.2, je Token gegen **jeden Grund, auf dem es vorkommen kann**. Dazu eine Messung über jeden sichtbaren Textknoten im Browser, beide Designs. |
| Abstände | Statisch über `assets/dashboard.css`, Kommentare entfernt; gezählt sind `margin`, `padding` und `gap` in `rem`, `px` und `em`. |
| Bausteine | Aufrufstellen über `dashboard/web/**.py`. |

**Was nicht gemessen ist:** kein echter Nutzer, keine Tastaturbedienung, keine
Vorlesesoftware. Die Vorlage entscheidet über Tokens, nicht über Bedienbarkeit.

---

## E1 — Wie viele Schriftrollen, und welche?

### Ist-Stand

**Dreizehn verschiedene Schriftgrößen** stehen gleichzeitig in der Oberfläche,
in **23** Kombinationen aus Größe und Gewicht:

| Bereich | verschiedene Größen |
| --- | --- |
| Einstieg | 7 |
| Leitstand | 11 |
| Ergebnisse | 11 |
| Modell | 8 |
| Handbuch | 11 |
| Schritt 1 allein | 8 |

Dahinter stehen **drei unabhängige Quellen**, und das ist der eigentliche
Befund: 60 `font-size`-Regeln im Stylesheet mit 14 verschiedenen Werten, sieben
Tailwind-Textklassen im Python-Code (`text-sm` 26×, `text-xs` 15×, `text-base`
10×, `text-lg` 6×, `text-3xl` 3×, `text-2xl` 3×, `text-xl` 1×) und sechs
Rollenkonstanten in `components.py` (`H1`, `H2`, `H3`, `LABEL`, `HINT`,
`CAPTION`), die selbst wieder Tailwind-Klassen zusammensetzen.

**Zwei Regeln rechnen in `em` statt in `rem`** und erzeugen damit Größen, die
auf keiner Skala liegen können: `.af-hint code { 0.95em }` und `.af-md code
{ 0.8125em }`. Gemessen erscheinen daraus **12,2 px** und **9,8 px** — Werte,
die niemand gewählt hat.

### Vorschlag: sieben Rollen

Abgeleitet aus dem, was heute am häufigsten benutzt wird — nicht neu erfunden:

| Rolle | Vorschlag | heute dafür im Einsatz |
| --- | --- | --- |
| Titel | 24 px / 700 | 30 px (3×) und 24 px (10×) |
| Überschrift | 20 px / 600 | 20 px (16×), 22 px (12×) |
| Zwischenüberschrift | 16 px / 600 | 16 px/600 (28×), 17 px (4×) |
| Fließtext | 15 px / 400 | 15 px/400 (62×), 16 px/400 (34×) |
| Beschriftung | 14 px / 500 | 14 px/500 (192×) |
| Klein (Hinweis, Bildunterschrift) | 12 px / 400 | 12 px/400 (257×), 13 px (50×) |
| Mono (Konsole, Code) | 13 px / 400 | gemischt 11–13 px |

Dazu: **keine `em`-Größen mehr** — Code in einem Hinweis bekommt eine Rolle,
nicht einen Anteil seines Elternelements.

### Was es kostet

**Die 11-px-Gruppe ist der teure Teil.** Sie ist mit 560 Vorkommen die größte
überhaupt: die Tick-Marken der Konsole, `af-choice__meta` in den
Auswahlkarten, der Zusatz «optional» in der Schrittliste. Auf 12 px gehoben
wird die Konsole rund ein Zehntel höher, und die Auswahlkarten tragen eine
Zeile mehr. Der Höhenwächter aus P1.9-W0.1 hält Ist-Stände je Schritt — die
müssten mitwandern, und das ist eine **bewusste** Eintragung, keine
stillschweigende.

**Drei Größen verschwinden ersatzlos:** 30 px (dreimal benutzt, `sm:text-3xl`
an `H1`), 22 px und 17 px. Das ist der Teil ohne Nebenwirkung.

### Offene Nebenfrage

Ob «Mono» wirklich eine eigene Größe braucht oder die Rolle «Klein» in
Festbreitenschrift genügt. Ich habe keine Messung, die das entscheidet.

---

## E2 — Drei Textfarbstufen oder zwei?

Diese Frage stand nicht im Audit. Sie kommt aus der Messung für
[U0.4](projektplan.md#p70--messfundament-für-die-gestaltung--offen) vom
2026-09-12 und gehört hierher, weil sie dieselbe Sorte Entscheidung ist.

### Ist-Stand

Vier Textfarben plus eine für farbige Gründe. Gerechnet gegen **jeden** Grund,
auf dem sie vorkommen können:

| Token | hell, schlechtester Grund | dunkel | WCAG 2.2 AA |
| --- | ---: | ---: | ---: |
| `--text` | 16,16 | 13,51 | 4,5 ✅ |
| `--text-body` | 9,38 | 12,43 | 4,5 ✅ |
| `--text-muted` | **4,31** | 5,36 | 4,5 ❌ hell |
| `--text-faint` | **2,32** | **2,80** | 4,5 ❌ beide |
| `--text-inverted` (auf dem Akzent) | 9,07 | 9,35 | 4,5 ✅ |

Eine Messung über **jeden sichtbaren Textknoten** aller fünf Bereiche in beiden
Designs fand 19 Kombinationen unter dem Grenzwert — **alle 19 derselbe Token**,
`--text-faint`. Er trägt heute die Chevrons, die Hinweiszeile einer Kennzahl,
die Tick-Marken von Zeitleiste und Konsole, die Abschnittsmarken des Handbuchs
und den Titel des abgeschalteten dritten Einstiegswegs.

### Vorschlag: zwei lesbare Stufen, eine gedämpfte, und eine für Abgeschaltetes

1. `--text` und `--text-body` bleiben, wie sie sind.
2. `--text-muted` wird **1,5 % dunkler**: `#64748b` → `#617087`. Damit erreicht
   es auf jedem Grund mindestens **4,55** (Rechnung unten). Der Farbton bleibt
   gleich, nur die Helligkeit sinkt.
3. **`--text-faint` verliert seine Rolle als Textfarbe.** Alles, was heute
   lesbar sein soll und ihn benutzt, geht auf `--text-muted`. Übrig bleibt er
   für **abgeschaltete Bedienelemente** — die nimmt WCAG 2.2 ausdrücklich aus
   (1.4.3, «inactive user interface components»).

Nachgerechnet für `#617087` im hellen Design:

| Grund | Kontrast |
| --- | ---: |
| `--accent-soft` | 4,55 |
| `--surface-inset` | 4,59 |
| `--canvas` / `--surface-hover` / `--surface-sunken` | 4,81 |
| `--surface` / `--surface-raised` / `--paper-bg` | 5,03 |

### Was es kostet

**19 Stellen werden dunkler.** Die Oberfläche verliert an dieser Stelle
Zurückhaltung — heute sind Chevrons und Tick-Marken fast unsichtbar, danach
sind sie zu sehen. Das ist der Zweck, aber es ist eine sichtbare Änderung des
Erscheinungsbilds und keine reine Korrektur.

**Der abgeschaltete dritte Einstiegsweg bleibt blass** — und dann aus einem
Grund statt aus Zufall.

### Die Alternative, damit sie dasteht

`--text-faint` so weit anheben, dass es selbst 4,5 hält. Dann liegt es bei
`--text-muted` (4,31 bis 4,76), und zwei Token tragen dieselbe Aufgabe. Das
wäre die Antwort «drei Stufen», und sie kostet eine Stufe, die keinen
Unterschied mehr macht.

---

## E3 — Welche Breiten, und wo gesetzt?

**Das ist der Befund aus dem Screenshot**, mit dem das Audit angefangen hat.

### Ist-Stand

Vier Breitendeckel im Stylesheet, in drei verschiedenen Einheiten:
`af-mass { max-width: 48ch }`, `af-body--lesen { 34rem }`, dazu `46rem` und
`68rem` an je einer Stelle.

Gemessen in **Schritt 1 bei 1440 px** — jede Zeile ein Textbaustein über 25
Zeichen:

| Breite | rechte Kante | Zeichen je Zeile | was |
| ---: | ---: | ---: | --- |
| 760 px | 1240 | 26 | die Frage (Überschrift) |
| 660 px | 1215 | 59 | Kurzhinweis «Aus: Der Lauf nutzt …» |
| 454 px | 1010 | 49 | Vorspann der Kohärenzbegründung |
| 434 px | 983 | 43 | Erklärung «Ist der Schalter aus …» |
| 424 px | 929 | 48 | Szenariobeschreibung |
| 363 px | 843 / 868 / 892 | 49–54 | Lede, Begründung, Vorbehalt |
| 341 px | 892 | 42–47 | die Quellenliste |

**Sechs verschiedene Textbreiten und elf verschiedene rechte Kanten** auf einem
Bildschirm. Und die Zusage aus P1.9-W5.4 — höchstens 75 Zeichen je Zeile — ist
dabei **an jeder Stelle erfüllt** (42 bis 59). Genau das ist die Lehre des
Audits: Eine Zusage über eine Einzelgröße lässt sich einhalten, während die
Fläche ungeordnet ist.

**Die Ursache ist subtiler, als sie aussieht.** `af-mass` sitzt in diesem
Schritt auf genau **einem** Element (363,375 px = 48ch bei 12 px). Die übrigen
Breiten kommen von Containern, die `af-mass` weiter oben verengt hat — die
Klasse wirkt also nicht dort, wo sie steht, sondern eine Ebene tiefer, und
`ch` macht sie von der Schriftgröße des jeweiligen Elements abhängig: 48
Zeichen sind bei 15 px 454 px und bei 12 px 363 px.

### Vorschlag: drei Tokens in `rem`, gesetzt am Container

| Token | Vorschlag | ergibt bei Fließtext (15 px) |
| --- | --- | --- |
| `--breite-lesen` | 38 rem = 608 px | ≈ 66 Zeichen je Zeile |
| `--breite-formular` | 30 rem = 480 px | drei Felder ohne Leerlauf |
| `--breite-inhalt` | 68 rem = 1088 px | Karten, Raster, Tabellen |

Gerechnet aus der Messung: 454 px tragen bei 15 px 49 Zeichen, also 9,27 px je
Zeichen; 608 px ergeben 65,6. Die Zusage «höchstens 75» bleibt damit erfüllt,
**und sie wird künftig am Container gemessen** statt am Element.

Der Unterschied zum heutigen Zustand ist nicht «der Text wird breiter», sondern:
**Der Container *ist* das Lesemaß, und der Text füllt ihn.** Damit fallen die
elf rechten Kanten auf eine zusammen.

### Was es kostet

**Die Schrittspalte wird schmaler**, bei 1440 px von 760 auf 608 px. Die
Auswahlkarten in Schritt 1 haben heute 171 px je Karte bei vier Spalten — mit
608 px wären es drei Spalten oder engere Karten. `Step.breite` aus P1.9-W5.4
unterscheidet schon zwischen «voll» und «lesen»; die Karten bekämen
`--breite-inhalt`, der Fließtext `--breite-lesen`. Das heißt: **nicht ein
Container je Schritt, sondern einer je Block** — und damit fallen die Kanten
auf **zwei** zusammen, nicht auf eine.

**`af-mass` entfällt oder wird ein Alias.** Sieben Aufrufstellen in
`components.py`, sechs in `start_flow.py`, drei in `wizard.py`, eine in
`controls.py`.

---

## E4 — Welche Abstandsskala?

### Ist-Stand

**25 verschiedene Abstandswerte** im Stylesheet, **13 davon nicht auf einem
4-px-Raster**:

| auf dem Raster | daneben |
| --- | --- |
| 4, 8, 12, 16, 20, 24, 28, 32, 40, 56, 64 px | −1, 1,2, 1,6, 2, 3, 4,8, 5, 5,6, 6, 10, 14, 22, 26 px |

Fünf der dreizehn liegen unter 4 px und sind eher Haarlinien-Korrekturen als
Abstände; **acht sind echte Abstände neben dem Raster** (4,8 / 5 / 5,6 / 6 / 10 /
14 / 22 / 26 px).

### Vorschlag

Ein 4-px-Grundraster mit acht Stufen: **4, 8, 12, 16, 24, 32, 48, 64 px**.
Werte unter 4 px bleiben erlaubt, aber nur für Rahmen und optische Korrekturen
— und dann mit einem Kommentar, der sagt warum.

Feste Abstände zwischen Abschnitt, Karte, Feld und Hinweis, damit Überschrift,
Karte und Text dieselbe linke Kante teilen.

### Was es kostet

Wenig Risiko, viel Kleinarbeit: Die sieben echten Ausreißer wandern auf die
nächste Stufe, was einzelne Kästen um 1 bis 2 px verschiebt. Ein statischer
Wächter kann danach jeden Abstand außerhalb der Skala melden — das ist U1.3s
Abnahmekriterium.

---

## E5 — Welche Bausteine, und welche Regeln dafür?

### Ist-Stand

| Aufgabe | heute |
| --- | --- |
| Hinweis / Meldung | **zwei Bausteine**: `ui.alert` 69× mit fünf Tönen (error 13, info 12, warning 11, success 4, demo 1), `ui.note` 7× |
| Kachel / Karte | **drei**: `ui.card` 30×, `ui.metric_tile` 21×, `ui.kpi_card` 4× |
| Aufklappen | **drei ohne Regel**: `ui.expert` 19×, `ui.accordion` 8×, `ui.explainer` 1× |
| Bestätigen | **der Dialog des Browsers** (`dcc.ConfirmDialogProvider`, eine Stelle in `controls.py`) |
| Primäraktion | 3× `variant="primary"`, alle drei im Bereich «Modell» |

`ui.note` und `ui.alert(..., "info")` sind im dunklen Design kaum zu
unterscheiden, tragen aber verschiedene Bedeutung: Kontext gegen Meldung.

### Vorschlag

1. **Ein Hinweisbaustein** `hinweis(text, ton=…)` mit sechs Tönen: `kontext`,
   `info`, `erfolg`, `warnung`, `fehler`, `demo`. `note` wird
   `hinweis(…, ton="kontext")`, `alert` wird der Rest. 76 Aufrufstellen wandern
   — mechanisch, ohne Entscheidung je Stelle.
2. **Eine Kachel** mit Varianten Zahl / Text / kompakt. `card` bleibt, was es
   ist (ein Behälter), `metric_tile` und `kpi_card` werden Varianten.
3. **Eine Regel zum Aufklappen:** Akkordeon für gleichrangige Abschnitte,
   Klappe (`expert`) für Zweitrangiges innerhalb eines Abschnitts, «Mehr dazu»
   (`explainer`) nur direkt an einem Feld. Mit einem Aufruf ist `explainer`
   heute der Kandidat zum Streichen — das wäre zu entscheiden, nicht
   vorzuschlagen.
   **Nachtrag vom 2026-09-13 (U1.4 Teil 4):** `explainer` bleibt — im Code
   ein Aufruf, gezeichnet aber an jedem Feld mit Glossar-Erklärung (sechsmal
   in der Schrittfolge); die Zählung der Aufrufstellen hatte ihn kleiner
   aussehen lassen, als er ist. Und **in etwas Aufgeklapptem steht nur
   Niedrigeres**: «Rohdaten ansehen» trug drei Klappen in einer Klappe. Von
   Haiko entschieden: Die drei Vorschauen stehen offen in der einen Klappe.
4. **`ui.expert` zählt nur, wenn es Parameter sind.** Heute steht «Rohdaten
   ansehen (3 Parameter)» an einem Block, der drei **Dateivorschauen** enthält
   (`experiment.py:156`, `count=3`) — der Baustein zählt, was man ihm gibt, und
   nennt es Parameter.
5. **Ein gestalteter Bestätigungsdialog** statt des Browser-Dialogs — das ist
   zugleich **D7**, und die folgenreichste Handlung der Oberfläche (ein
   Schreibzugriff ins Modell) hängt daran.
   **Nachtrag vom 2026-09-13 (U1.4 Teil 7):** Von Haiko entschieden — gestaltet,
   **gleicher Inhalt, keine Änderungsvorschau**. Der teure Teil aus «Was es
   kostet» ist dadurch klein geworden: Fokusführung und Escape liefert der
   Browser selbst, sobald der Dialog ein `<dialog>` mit `showModal()` ist.
   Die Änderungsvorschau bleibt eine Frage von U7.2.

### Was es kostet

Punkt 1 bis 4 sind Umbau ohne Produktentscheidung. **Punkt 5 ist der teure**:
Ein eigener Dialog braucht Fokusführung, Escape-Verhalten und einen Diff, der
zeigt, was sich am Modell ändert. Der Docstring von `controls.write_action`
wägt den Browser-Dialog heute bewusst ab — die Begründung ist nachzulesen,
bevor sie ersetzt wird.

---

## Wenn D1 «Nein» heißt

Dann bleibt es bei Einzelregeln, und das hat eine benennbare Folge: Jede Ansicht
wird für sich repariert, und der Befund aus Q1 wiederholt sich an der nächsten.
Konkret nicht baubar bleiben **U0.1** (Kantenwächter — es gibt keine Kante, die
er halten könnte) und **U0.2** (Schriftwächter — es gibt keine Skala). Die
übrigen vier Wächter aus P7.0 stehen und halten weiter; P7.2 bis P7.9 wären
ohne gemeinsame Tokens jeweils eigene Korrekturen.

---

## Was danach passiert

| Reihenfolge | was |
| --- | --- |
| 1 | E1 bis E4 als Tokens in `assets/dashboard.css` und `theme.py` (U1.1 bis U1.3) |
| 2 | U0.1 und U0.2 als Wächter darauf — sie messen dann eine Skala, die es gibt |
| 3 | E5 als Bausteinumbau (U1.4), inklusive D7 |
| 4 | U1.5 Diagrammstandard, U1.6 Musterseite |
| 5 | P7.2 bis P7.9 gegen die Wächter |

**Was diese Vorlage nicht entscheidet:** D2 bis D7 des Audits. Sie hängen nicht
an den Tokens, sondern an Produktfragen — welche Bereiche Seitenzonen zeigen,
wohin Begründungen gehören, welche Breiten unterstützt werden, wie viele
Zeitachsen es gibt, wie ein Lauf heißt, und wie eine Modelländerung bestätigt
wird. D7 fällt mit E5 Punkt 5 zusammen und ist dort mitgestellt.
