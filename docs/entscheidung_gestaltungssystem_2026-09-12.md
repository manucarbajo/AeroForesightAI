# Entscheidung: das Gestaltungssystem (D1)

**Stand 2026-09-12 · entschieden (Haiko, siehe «Die Entscheidung» unten) · Grundlage für [P7.1](projektplan.md#p71--ein-gestaltungssystem-statt-einzelregeln--offen) und die beiden letzten Wächter aus [P7.0](projektplan.md#p70--messfundament-für-die-gestaltung--offen)**

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
| **E3** | Lesemaß | **38 rem = 608 px** (≈ 66 Zeichen bei 15 px), gesetzt am Container. Karten und Raster behalten `--breite-inhalt`. |
| **E4** | Abstände | **4-px-Raster mit acht Stufen** (4, 8, 12, 16, 24, 32, 48, 64). Werte unter 4 px bleiben für Rahmen erlaubt, mit Begründung. |
| **E5** | Bausteine | **Vollständig, einschließlich des gestalteten Bestätigungsdialogs.** Damit ist **D7 mitentschieden**. |
| **D3** | Begründungen | **These und zwei Sätze sichtbar, in Fließtextgröße; der Rest hinter einer Klappe «Begründung und Quellen».** Am selben Tag nachentschieden, weil E3 ohne D3 nicht baubar war — siehe den Nachtrag unten. |

**Was daraus folgt, und zwar sofort:** Die Zusage aus P1.9-W5.4 wird künftig **am
Container gemessen** statt am Element, der Höhenwächter bekommt neue Deckel, und
`dcc.ConfirmDialogProvider` verschwindet aus `dashboard/web/` — das ist das
Abnahmekriterium von P7.1.

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
ist jetzt baubar, weil der Block eine Größe hat.

**Was offen bleibt:** D2, D4, D5 und D6 des Audits. Sie hängen an
Produktfragen, nicht an den Tokens.

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
4. **`ui.expert` zählt nur, wenn es Parameter sind.** Heute steht «Rohdaten
   ansehen (3 Parameter)» an einem Block, der drei **Dateivorschauen** enthält
   (`experiment.py:156`, `count=3`) — der Baustein zählt, was man ihm gibt, und
   nennt es Parameter.
5. **Ein gestalteter Bestätigungsdialog** statt des Browser-Dialogs — das ist
   zugleich **D7**, und die folgenreichste Handlung der Oberfläche (ein
   Schreibzugriff ins Modell) hängt daran.

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
