# Audit: Oberfläche und Bedienung des Dashboards (UI/UX)

**Stand:** 2026-09-11 · **Gegenstand:** `dashboard/web/`, alle fünf Bereiche (Einrichten, Leitstand, Ergebnisse, Modell, Handbuch), Codestand `24bcf7c` auf `chore/phase-5-p51-toter-code-pr` · **Ausgenommen:** die Landingpage — sie gilt als abgenommen · **Teil 1 von 2:** Dieses Dokument prüft Gestaltung und Bedienung. Die technische Umsetzung ist Teil 2 und wird geplant, wenn die Pakete hier umgesetzt sind.

**Verfahren:** unabhängig von den Abnahmekriterien der Phase 1 und von P1.9. Maßstab ist ein professionelles Analyse- und Simulationswerkzeug, nicht der eigene Plan. Wo eine Aussage gemessen wurde, steht die Messung dabei; wo sie aus dem Code folgt, die Fundstelle. Die Arbeitspakete stehen ab [Teil 5](#teil-5--arbeitspakete-phase-7) und sind im Projektplan als [Phase 7](projektplan.md#phase-7--oberfläche-auf-produktniveau-uiux-audit-2026-09-11--offen) eingeplant.

## Methodik

- **Instanz:** Dash-App aus `.claude/launch.json` auf Port 8511, Datenbestand in `outputs/` wie vorgefunden. Die Lauf-Auswahl trug **388** Einträge, vorgewählt war `sweeps/sweep_transformation_conflict` (50 Ticks, beeinträchtigt).
- **Breiten:** 1440 × 900 (Hauptmessung), 1024 × 768 und 375 × 812; dunkles und helles Design.
- **Messskript im Browser**, je Ansicht: Höhe in Bildschirmen (`scrollHeight / clientHeight` von `.af-shell__main`), die gerenderten Schriftgrößen, Breite und Zeilenzahl der Textblöcke, und der Kontrast **jedes** sichtbaren Textknotens gegen seinen tatsächlichen Hintergrund (WCAG-Formel, Hintergrund über die Vorfahren aufgelöst).
- **Serverseitig:** Renderzeit und Nutzlast der Ansicht «Animation», gemessen mit `animation.render` im Projekt-venv.
- **Codelesen:** `shell.py`, `app.py`, `components.py`, `theme.py`, `assets/dashboard.css`, `config_editor/*`, `pages/*`, `views/*`.

**Nicht gemessen — und das gehört zum Ergebnis:**

- **Keine echten Nutzer.** Jede Aussage über Verständlichkeit ist Fachurteil und steht als solches da.
- **Kein laufender Lauf.** Ladebildschirm und Fortschrittsfenster sind aus dem Code beurteilt. Ein Lauf hätte `outputs/` beschrieben und damit die Vorauswahl der Instanz verändert.
- **Kein Durchgang mit Vorlesesoftware** und keine vollständige Tastaturprüfung. Die Fokus-Stichprobe per Skript war nicht schlüssig (siehe Q9).
- **Kontraste nur im dunklen Design** gemessen; das helle ist per Sichtprüfung beurteilt.

---

## Kernurteil

**Die Oberfläche hat ein Farbsystem, aber kein Gestaltungssystem.** Farbe läuft seit P1.5 über Tokens, und das trägt: beide Designs sind durchgängig stimmig. Für **Schrift, Abstand, Breite und Komponentenwahl** gibt es dagegen keine Tokens, sondern Einzelregeln, jede gegen einen gemessenen Befund eingezogen — `af-mass`, `af-body--lesen`, `max-w-2xl`, `max-w-3xl`, `pt-7`. Jede davon ist lokal richtig begründet, zusammen widersprechen sie sich: **Der Block aus dem Screenshot, der dieses Audit ausgelöst hat, trägt vier verschiedene Textbreiten übereinander** (Q1).

**Die Oberfläche spricht Entwicklersprache.** Paketkennungen («P3 —», ein Szenario namens «P5.7»), Verzeichnis- und Feldnamen (`sweeps/sweep_transformation_conflict`, `saf_mandate_share`), roh stehendes Markdown, veraltete Verweise auf Schritte, die es nicht mehr gibt, und lange Absätze, in denen das Produkt seine eigene Entstehungsgeschichte erzählt (Q6).

**Und sie mischt Kontexte.** Unter «Ergebnisse» stehen gleichzeitig der Entwurf des *nächsten* Laufs (links), ein *vergangener* Lauf (Mitte), dessen Kennzahlen bei *Tick 1* (rechts) und eine Zeitleiste, die keine der Ergebnis-Ansichten bewegt (Q5).

Handwerklich ist vieles sorgfältiger als üblich. Die Mängel sitzen eine Ebene höher: **Es fehlt die Instanz, die aus Einzelentscheidungen ein Bild macht.**

## Was gut ist

Nicht alles ist zu kritisieren, und einiges liegt deutlich über dem, was Fachwerkzeuge dieser Größe üblicherweise mitbringen:

- **Farbe und Dark Mode.** Eine semantische Token-Ebene, dieselben Namen in `theme.py` und im Stylesheet, Dashs eigene Komponenten über `--Dash-*` mitgefärbt, kein Aufblitzen beim Laden. Bei 1440 px fanden sich im dunklen Design unter 73 Textknoten nur drei Kontrastverstöße (Q9).
- **Ehrlichkeit als Gestaltungsprinzip.** Unbestimmter Balken statt erfundener Prozentzahl, «Lauf beeinträchtigt» statt stiller Degradierung, Zufallsstartwert und Codestand vor dem Start, Abweichungen vom Auslieferungszustand einzeln rücknehmbar.
- **Führung im Einrichten.** Tor vor «Weiter», ehrlicher Fortschritt (besucht/übersprungen), «Zurück» mit Verlauf, Laufzeitschätzung, Abbruch. Die Befunde von 2026-08-28 sind wirklich behoben.
- **Barrierefreiheits-Grundlagen.** Sprunglink, Live-Regionen, Fokusführung beim Schritt- und Bereichswechsel, `fieldset`/`legend`.
- **Datenhoheit.** Schriften und Stylesheet lokal; kein Seitenaufruf verlässt den Server.
- **Ziehbare Zonen, Fokusmodus, klebende Fußleiste** — alles ruhig und ohne Serverrundlauf gebaut.

---

## Teil 1 — Querschnittsbefunde

Befunde, die nicht an einer Ansicht hängen, sondern an einer fehlenden Regel. Behoben werden sie deshalb nicht Ansicht für Ansicht, sondern im Fundament (P7.1, P7.2).

### Q1 — Das Lesemaß erzeugt vier Textbreiten in einem Block · **hoch**

Gemessen in Schritt 1 bei «Standard-Ausgangslage», 1440 × 900 — der Fall aus dem Screenshot:

| Element | Schrift | Breite | Zeichen | Zeilen |
| --- | ---: | ---: | ---: | ---: |
| Slot (Container) | — | 710 px | — | — |
| Hinweiskasten (`ui.note`), Kasten | 15 px | **710 px** | — | — |
| Hinweiskasten, Text | 15 px | **454 px** | 167 | 5 |
| These | 14 px | **424 px** | 190 | 4 |
| Begründung | 12 px | **363 px** | 984 | 17 |
| Vorbehalt (aufgeklappt) | 12 px | **363 px** | 1303 | 23 |

**Ursache:** `.af-mass { max-width: 48ch }`. Die Einheit `ch` ist die Breite der Ziffer Null **in der Schrift des Elements selbst** — dieselbe Regel ergibt bei 15, 14 und 12 px drei verschiedene Kanten. Dazu setzt `ui.alert` und `ui.note` das Maß auf den **Text** und nicht auf den **Kasten**: Der Kasten läuft über die volle Spalte, sein Text endet bei gut der Hälfte. Dasselbe Bild steht in «Prüfen & Starten» bei jedem Hinweis.

**Warum es trotzdem durch alle Wächter kam:** Die Zusage aus P1.9-W5.4 lautet «höchstens 75 Zeichen je Zeile», und die ist erfüllt. **Eine Zusage über Zeichen je Zeile ist erfüllbar, ohne dass eine Seite gut aussieht** — sie misst die Lesbarkeit einer Zeile, nicht die Ordnung einer Fläche. Dieselbe Klasse wie P1.1 (Entscheidungen gezählt, Erreichbarkeit nicht) und P1.7 (Knoten gezählt, Bildschirme nicht).

**Folge:** Ein ausgefranster linker Textblock neben vollbreiten Kästen und Rastern. Das ist das Erste, was ein Kunde sieht, noch vor jeder Funktion.

### Q2 — Keine Schriftskala, und die Hierarchie steht teils auf dem Kopf · **hoch**

- **Acht Schriftgrößen in einem Schritt** (Schritt 1, ohne Symbolschrift): 11, 12, 12,19, 13, 14, 15, 16 und 20 px. Ein Gestaltungssystem kommt mit fünf bis sieben Rollen aus.
- **Der Hinweis unter einem Feld ist größer als dessen Beschriftung:** gemessen 15 px gegen 14 px (Schritt 4). `ui.hint_text` rendert als `dcc.Markdown` mit den Klassen `af-hint af-md`; `.af-md { font-size: 0.9375rem }` steht im Stylesheet **nach** `.af-hint { font-size: 0.75rem }`, bei gleicher Spezifität gewinnt die spätere Regel. Der Kurzhinweis ist damit das lauteste Element des Feldes.
- **Frage und Abschnitt sind gleich groß.** Die Überschrift eines Schritts ist ein `h1` in der Klasse `H2` (20 px); die Abschnittsüberschriften darin — «Fragestellung» in Schritt 4, «Sprachmodell» in Schritt 5 — sind ebenfalls 20 px. Zwischen «worum geht es auf diesem Schirm» und «ein Teil davon» gibt es optisch keinen Unterschied.
- **Text im Zahlensatz.** Die Kacheln in «Übersicht» setzen «Transformationskonflikt (B2 vs A1)» und «e536a509 + Änderungen» in 24 px fett — der Stil für Kennzahlen, angewendet auf Namen und Hashes. `metric_tile(prose=True)` gibt es, benutzt wird es nur an einigen Stellen.

### Q3 — Markdown steht roh in der Oberfläche · **hoch**

Zu sehen im Browser:

- Schritt 4: «Der `**Name**` steht im letzten Schritt» (`experiment.layout` → `ui.lede`)
- Schritt 5: «`**Ob**` ein Sprachmodell beteiligt ist» (`llm_pipeline.layout` → `ui.lede`)
- Schritt 1, Kohärenzbegründung: «er kommt `**nicht**` überraschend», «`**Und die Kapazität bleibt konstant …**`» (`start_flow._kohaerenz_block` → `html.P`)

**Ursache:** `ui.lede` und `_kohaerenz_block` rendern `html.P`, die Texte sind aber als Markdown geschrieben — in Python-Literalen und in den Daten (`configs/properties.json` enthält `**` an vier Stellen, die vier Rahmenszenarien in `configs/sweeps/` je zwei). **Ob Markdown gerendert wird, entscheidet der Aufrufer, nicht der Text.** Solange das so bleibt, kehrt der Fehler mit dem nächsten Textbaustein zurück.

### Q4 — Kein Raster: Die Fläche wird nicht genutzt, und die Kanten springen · **mittel**

- **Einrichten bei 1440 px:** Der Fokusbereich ist auf 68 rem (1088 px) gedeckelt, darin 240 px Schrittliste und 760 px Inhalt. Die als «lesen» markierten Schritte deckeln zusätzlich auf 34 rem: Schritt 2 steht als 544 px breite Karte in einem 1440 px breiten Fenster, rechts daneben rund 700 px Leere.
- **Einstieg:** drei Karten über 1040 px, jede mit einer Zeile Text — wirkt leer statt fokussiert.
- **Keine gemeinsame Kante.** In Schritt 1 enden Überschrift (760 px), Karte (710 px) und die vier Textblöcke (363–454 px) an sechs verschiedenen rechten Kanten. «Im Handbuch nachlesen» hängt allein über der rechten Kartenkante.
- **Ergebnisse und Handbuch** laufen in 868 px zwischen Bedienfeld und Telemetrie (60 % der Breite), obwohl keine der beiden Seitenzonen dort etwas zur Aufgabe beiträgt (Q5).

### Q5 — Ein Bildschirm, drei Kontexte · **hoch**

Unter «Ergebnisse», 1440 × 900, gleichzeitig sichtbar:

| Zone | zeigt | Kontext |
| --- | --- | --- |
| links, Bedienfeld | Standard-Ausgangslage, 40 Ticks, Ohne Sprachmodell | der **Entwurf** des nächsten Laufs |
| Mitte | Transformationskonflikt, 50 Ticks, Nur Zahlen | ein **vergangener** Lauf |
| rechts, Telemetrie | Buchungsrate 37,0 %, «Tick 1 von 50» | derselbe Lauf, aber **bei Tick 1** |
| unten, Zeitleiste | Tick 1 / 50 | bewegt **keine** der sieben Ergebnis-Ansichten |

Dazu die Kopfzeile: «Lauf beeinträchtigt» steht auf **jedem** Bereich — auch in «Einrichten», «Modell» und «Handbuch» — und klingt dort wie ein Zustand der Anlage. Gemeint ist der gewählte vergangene Lauf. Im Leitstand selbst steht der Name des gezeigten Laufs nirgends außer im abgeschnittenen Auswahlfeld («sweeps/sweep_transfor…»).

**Folge (Fachurteil):** Wer vergleicht, liest drei Zahlen aus drei Zusammenhängen und muss selbst herausfinden, welche zu welchem Lauf gehört. Genau das, wogegen `status.py` und die «eine Zeitachse» aus P1.5 angetreten sind — nur eine Ebene höher.

### Q6 — Entwicklersprache statt Produktsprache · **hoch**

**Interne Kennungen im sichtbaren Text** (alle im Browser gesehen):

| Ort | Text |
| --- | --- |
| Ergebnisse › Szenario | «P3 — Szenarien aus dem Lauf: Tick-Anhaltspunkte …» |
| Ergebnisse › Szenario | Überschrift «Szenarien zum Lauf sweeps/sweep_transformation_conflict» |
| Einrichten › Schritt 1 | ein Szenario namens «P5.7» |
| Kopfzeile | «sweeps/sweep_transformation_conflict — Trend-Fortsetzung» |
| Prüfen & Starten, Bedienfeld | «… der früheste ist `saf_mandate_share` bei Tick 16» |
| Bedienfeld, Fußzeile | «Szenario: basis · Ticks: 40 · 1 Lauf» |
| Modell | Klappen «provider_markup», «ticket_price» |
| Abfrage | «Demo ohne Ollama (Mock)», «Modell in .env» |
| Dateien | absoluter lokaler Pfad «F:\AeroForesight\…\cib_matrix.json» |
| Ergebnisse, Kopfzeile des Laufs | «2026-09-07T18:25:55.248822+00:00» |
| Browser-Tab | «Technology Lab · Leitstand» (die Marke heißt AeroForesight AI) |
| Bericht, Vorgabename | «Flugverkehr Szenarioplanung MVP» |

**Veraltete Texte**, die eine Oberfläche beschreiben, die es nicht mehr gibt:

| Ort | Text | Stand heute |
| --- | --- | --- |
| Schritt 1, Karte «Eigene Einstellungen» | «Was Sie in den Schritten 4 bis 7 selbst eingestellt haben» | sechs Schritte; eigene Werte entstehen im Bereich «Modell» |
| Schritt 4, Untertitel | «Name, Beschreibung und was am Ende geschrieben wird» | der Name steht seit W4.1 in Schritt 6 |
| Modell, Untertitel | «… Faktorlage, Systemgrößen, …» | seit P2.0-C gibt es keinen Schreibweg zur Faktorlage |
| Modell, Warnung (`macro.layout`) | «Einschalten im Einrichten, Schritt «Ausgangslage»» | der Schritt ist mit P2.0-C entfallen |
| Leere Zustände (`runs.layout`, `scene.render`) | «Starten Sie links einen Lauf» | gestartet wird seit P1.7 hauptsächlich am Ende der Schrittfolge |

**Sprachmischung:** «Figures», «Events», «Run-ID», «Markt an», «Ground Truth», «Behavioral Split», «Surplus Pulse», «Saturation Swarm», «Income vs WTP». **Uneinheitliche Begriffe:** «Tick» überall, aber «ab Runde», «über … Runden» und «je Runde» im Regel-Editor des Modells.

**Metakommentar und Textmenge.** Die Oberfläche erklärt ihre eigene Entstehung: «Auch das ist ein Rahmenszenario — es trägt eigene Annahmen … und heißt nur nicht so.» Begründung und Vorbehalt des Standardrahmens haben zusammen **2 287 Zeichen** in 12 px. Das ist die Tonlage des Projektplans, nicht die eines Produkts. **Die Begründung gehört nicht weg — sie gehört eine Ebene tiefer.**

### Q7 — Warten ohne Rückmeldung · **hoch**

- **«Animation» braucht serverseitig 10,5 s und liefert 19,3 MB** an den Browser (`animation.render` für `sweep_transformation_conflict`, 50 Ticks, rund 4 000 Personen, neun animierte Diagramme; Serialisierung weitere 0,7 s). Im Browser stand **nach 10 s** weiterhin der Inhalt der vorigen Ansicht unter dem bereits aktiven Reiter «Animation» — ohne Ladeanzeige, ohne Meldung.
- **Die Ladeanzeige ist global abgeschaltet:** `._dash-loading { display: none; }` in `assets/dashboard.css`. Nur drei Ansichten legen ein eigenes `dcc.Loading` an (Szenario, Abfrage, PNG-Galerie).
- **«Ollama wird geprüft …»** steht mit demselben grauen Punkt da wie «Ollama ist nicht erreichbar» — ein laufender und ein gescheiterter Zustand sehen gleich aus.

### Q8 — Dieselbe Aufgabe, verschiedene Bausteine · **mittel**

- **Zwei Hinweisarten, die gleich aussehen:** `ui.note` (Kontext) und `ui.alert(..., "info")` (Meldung) sind im dunklen Design kaum zu unterscheiden, tragen aber verschiedene Bedeutung.
- **«(n Parameter)» für Dinge, die keine Parameter sind:** «Rohdaten ansehen (3 Parameter)», «Als Szenario sichern (1 Parameter)», «Zufallsstartwert (2 Parameter)». `ui.expert` zählt, was man ihm gibt.
- **Drei Arten aufzuklappen:** Karten-Akkordeon (`ui.accordion`), leise Klappe (`ui.expert`), «Mehr dazu» (`ui.explainer`) — ohne erkennbare Regel, wann welche.
- **Vier Wege, den Entwurf als Szenario zu sichern**, mit drei Namensregeln: Kopfzeile «Speichern» (Simulationsname), Kopfzeile «Snapshot» (Name + Zeitstempel), Schritt 4 «Szenario sichern» (eigenes Feld, vorbelegt «mein_szenario»), Schritt 6 «Als Szenario speichern» (Simulationsname).
- **Dauerhafte Modelländerungen über den Dialog des Browsers** (`dcc.ConfirmDialogProvider`). Der Docstring von `controls.write_action` wägt das bewusst ab; für ein Produkt ist ein ungestalteter Systemdialog vor der folgenreichsten Handlung der Oberfläche trotzdem der falsche Ort — ohne Diff, ohne Bezug zum Modell.

### Q9 — Kontraste und Fokus · **mittel**

- **«optional» in der Schrittliste:** 11 px, Kontrast **3,77** (auf der markierten Zeile **2,87**). WCAG 2.2 AA verlangt 4,5.
- **Symbole:** 2,80 (`lightbulb`, `schedule`, `check_circle`). Für informationstragende Grafik verlangt WCAG 3,0.
- **Fokusstile uneinheitlich:** Eigene Fokusringe haben Knöpfe, Wege, Schalter, Regler und der Ziehgriff. Bereichslinks, Stand-Zeilen, Ansichtsleiste, Schrittliste und Handbuch-Links haben **keine** eigene Regel und verlassen sich auf den Browserstandard. Die Stichprobe per `element.focus()` zeigte an keinem davon einen Ring, **ist aber nicht schlüssig**: Programmatischer Fokus löst `:focus-visible` nicht zuverlässig aus. Ein Tastaturdurchgang gehört deshalb in die Abnahme, nicht in eine Vermutung.

### Q10 — Schmale Breiten: Die Navigation verschwindet · **hoch**

- **1024 × 768:** Die Bereichslinks verschwinden hinter Zustandsanzeige und Lauf-Auswahl. Sichtbar sind «Einrichten», «Leitstand» und ein angeschnittenes «Ergi…»; **«Modell» und «Handbuch» sind nicht zu sehen**. Die Leiste scrollt waagerecht, ihr Rollbalken ist absichtlich ausgeblendet (`.af-nav__links { scrollbar-width: none }`).
- **375 × 812:** Die Bereichsleiste hat `clientWidth 0` — **es gibt keine Bereichsnavigation**. Der einzige Umschalter öffnet das Bedienfeld, nicht die Bereiche.
- **Faktor-Chips** sind schon bei 1440 px auf rund 14 Zeichen gekürzt («Globaler Reise…», «Moderater Klim…»), bei 1024 px nicht besser.

### Q11 — Diagramm-Handwerk · **mittel**

- **Beschnittene Achsentitel:** «Figures › 1 · Preis und Nachfrage» bei 1440 px zeigt «etpreis (EUR)» und «ungsrate (0–1)» — beide Achsentitel ragen aus der Zeichenfläche.
- **Rohnamen als Reihen:** «Was die Politik bewirkt» benennt Reihen mit Spaltennamen (`carbon_tax_level`, `saf_mandate_share`, …; `figures._view_politik`).
- **Der Szenario-Vergleich vergleicht, was im Ordner liegt:** zehn Verzeichnisse, darunter Testläufe («High Base», «Low Base», «Kein Sprachmodell», «Llm Schalter An», «Llm Schalter Aus», «Test Short»), benannt aus dem Verzeichnis («Co2 Delayed») statt aus dem Szenario («CO₂-Verzögerung»), in zehn Farben der Standardfolge.
- **Eine zweite Zeitachse:** «Animation» zeigt neun Plotly-Animationen mit je eigenen Abspielknöpfen, während unten die Zeitleiste steht. P1.5 hatte genau das abgeschafft («zwei Zeitachsen nebeneinander sagen nie dasselbe»).
- **Szene:** Die Einblendung «Tick / Individuen / Zoom» liegt über den Datenpunkten; 4 000 Punkte ohne Dichtebehandlung.

---

## Teil 2 — Befunde je Bereich

Schwere: **kritisch** (die Oberfläche behauptet etwas Falsches oder verhindert die Aufgabe), **hoch** (beeinträchtigt die Aufgabe deutlich), **mittel** (sichtbarer Qualitätsmangel), **niedrig** (Politur). Die Spalte «Paket» verweist auf Teil 5.

### K — Kopfzeile und Navigation

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| K1 | hoch | **Lauf-Auswahl ist nicht bedienbar.** 388 Einträge, beschriftet mit der technischen Kennung; alle acht zuerst gelisteten tragen denselben Zusatz «— Trend-Fortsetzung». Kein Datum, kein Rahmenname, keine Gruppen, Testläufe gleichrangig. Sortiert alphabetisch statt zeitlich (vorbestehend, `audit_findings.md`). | P7.3 |
| K2 | mittel | «Lauf beeinträchtigt» bezieht sich auf den gewählten Lauf, steht aber als Anlagenzustand auf jedem Bereich (Q5). | P7.3 |
| K3 | mittel | Drei Symbolknöpfe ohne Beschriftung. «Speichern» sichert den **Entwurf** als Szenario — auch von «Ergebnisse» aus, wo man einen fertigen Lauf ansieht. Das Download-Symbol lädt nichts herunter, sondern öffnet die Dateiansicht. | P7.3 |
| K4 | hoch | Navigation bei 1024 px teilweise, bei 375 px ganz unerreichbar (Q10). | P7.9 |
| K5 | niedrig | Browser-Titel «Technology Lab · Leitstand» auf jedem Bereich. | P7.2 |

### E — Einrichten

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| E1 | **kritisch** | **Der Szenario-Vergleich wird widersprüchlich gezählt.** Einstieg «Alle 8 hinterlegten Szenarien» (`wizard.entry` zählt `list_sweep_presets()`), Bedienfeld «Vergleich · 8 Szenarien» (`launch._summary`, `summary_rows`), Kachel «Szenarien 8» samt Längenspanne über alle Presets (`start_flow._vergleich_tiles`) — und darüber der Satz «alle **4** Rahmenszenarien» (`_vergleich_satz` zählt `rahmenszenarien()`). Gerechnet werden die vier Rahmen. Dieselbe Klasse wie A1 des Audits vom 2026-08-28: Die Oberfläche beschreibt einen Lauf, der so nicht stattfindet. | P7.2 (vorziehbar) |
| E2 | hoch | **Schritt 1 mischt Weltbilder und Belastungstests.** Vier der acht Presets sind Stresstests — «Achterbahn der Extreme», «Action-Szenario», «Totaler Wahnsinn (Alle Parameter)», «P5.7» —, alphabetisch zwischen die Rahmen sortiert und nur am 11-px-Zusatz «Stresstest» zu erkennen. Beschreibungen sind mitten im Satz auf zwei Zeilen gekürzt. | P7.4 |
| E3 | hoch | **Der Detailblock unter der Auswahl** (Anlass dieses Audits): vier Textbreiten (Q1), Roh-Markdown (Q3), Metakommentar und 2 287 Zeichen in 12 px (Q6). Er steht unter dem Raster statt bei der gewählten Karte. Schritt 1 ist **1,84 Bildschirme** hoch. | P7.1, P7.2, P7.4 |
| E4 | mittel | Karte «Eigene Einstellungen» verweist auf «Schritte 4 bis 7» (Q6). | P7.2 (vorziehbar) |
| E5 | mittel | Feldhinweise größer als Feldbeschriftungen (Q2). | P7.1 (vorziehbar) |
| E6 | mittel | Schritt 3: Die Ollama-Prüfung hat keinen eigenen Zustand (Q7). «Mit Sprachmodell» bleibt ohne Unterschied wählbar, wenn Ollama nicht erreichbar ist — nur ein Hinweistext darunter. | P7.4 |
| E7 | mittel | **Schritt 4 «Lauf & Ablage»:** verspricht im Untertitel den Namen, der in Schritt 6 steht; Roh-`**Name**`; «Fragestellung» dreimal (Abschnitt, Feld, Hinweis); Vorgabetext «… fuer Szenarioplanung …» ohne Umlaut; eigener Speicherweg (Q8); «Auf Standard-Config zurücksetzen» verwirft den **ganzen** Entwurf ohne Rückfrage, und das in einem als optional markierten Schritt. | P7.4 |
| E8 | mittel | **Schritt 5 «Technik»:** Modellname, Adresse, Kreativität und Antwortlänge stehen voll bedienbar da, auch wenn «Ohne Sprachmodell» oder «Nur Zahlen» gewählt ist — ohne Hinweis, dass sie nicht wirken. Roh-`**Ob**`. Tooltip des Schiebereglers dauerhaft eingeblendet. | P7.4 |
| E9 | hoch | **Schritt 6 «Prüfen & Starten» beantwortet die eine Frage auf acht Blöcke verteilt:** Name, Satz, Horizont-Hinweis mit `saf_mandate_share`, Dauer, Herkunft (Klappe), sechs Kacheln mit Modellinterna («Ziel-Auslastung 37 %», «Segmente 5», «Aktive Systemgrößen 16»), die Abweichungen erst ganz unten, dann ein Speicherhinweis. **1,59 Bildschirme.** Hinweiskästen voller Breite mit halbbreitem Text (Q1). | P7.4 |
| E10 | mittel | Vier Speicherwege mit drei Namensregeln (Q8). | P7.4 |
| E11 | niedrig | Einstieg bei 1440 px: drei vollbreite Karten mit je einer Zeile (Q4). | P7.4 |

### L — Leitstand

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| L1 | hoch | **Bedienfeld:** Die Werte der drei Stand-Zeilen sind auf drei bis vier Zeichen gekürzt — «Stand…», «40 Ti…», «Ohne …» — bei 272 px Spaltenbreite und fester Beschriftungsspalte von 6,5 rem. Die Zone ist **1,73 Bildschirme** hoch (1458 / 844 px); P1.6 hatte höchstens 1,5 zugesagt. Der klebende Fuß verdeckt den Hinweistext darüber. | P7.5 |
| L2 | hoch | **Der gezeigte Lauf hat keinen Namen im Viewport** (Q5). Faktor-Chips unlesbar gekürzt (Q10). | P7.5 |
| L3 | mittel | Szene: Einblendung über den Datenpunkten, keine Dichtebehandlung (Q11). Die Minus-Lupe heißt «Ausschnitt vergrößern» — sachlich richtig, im Wortsinn verkehrt herum. | P7.5 |
| L4 | mittel | **Zeitleiste:** Die Marken «49» und «50» überlagern sich zu «490». `timeline._marks` setzt bei 50 Ticks alle acht Ticks eine Marke ab 1 (…, 41, 49) und die Endmarke 50 direkt daneben. Der Ereignisstreifen darunter hat keine Legende. | P7.5 (vorziehbar) |
| L5 | niedrig | Telemetrie: Sparklines teils ohne Einheit an der Achse; Richtung der Veränderung ist farbcodiert, ohne dass gesagt wird, ob «hoch» gut oder schlecht ist. Die Entscheidung dagegen ist im Docstring begründet — eine Legende fehlt trotzdem. | P7.5 |

### R — Ergebnisse

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| R1 | hoch | **Der Kopf eines Laufs steht über jeder der sieben Ansichten** — Beeinträchtigt-Banner und Zusammenfassung, zusammen rund 350 px. In «Figures» beginnt das erste Diagramm bei etwa y = 560 von 900. Die Zusammenfassung steht in «Szenario» ein zweites Mal wörtlich. | P7.6 |
| R2 | hoch | **«Animation» wechselt nicht sichtbar:** 10,5 s Serverzeit, 19,3 MB, keine Ladeanzeige (Q7). | P7.6 |
| R3 | hoch | **Szenario:** Paketkennung und Verzeichnisname in Unterzeile und Überschrift (Q6); Faktorcodes im Fließtext («F1.1→F1.2 … F7.1→F7.2»); «Ground Truth (Python-Kennzahlen)». «Szenarien neu erzeugen» rechnet immer ohne Sprachmodell (`scenario._regenerate`: `mock_llm=True, deterministic_only=True`) und sagt es nicht. | P7.6 |
| R4 | mittel | **Übersicht:** Namen und Hashes im Kennzahlensatz (Q2), roher Konfigurations-Fingerabdruck als Fließtext, ISO-Zeitstempel mit Mikrosekunden. | P7.6 |
| R5 | hoch | **Figures:** beschnittene Achsentitel, Spaltennamen als Reihen, Vergleich über Testläufe (Q11). Der Reitername ist Englisch. | P7.6 |
| R6 | mittel | **Abfrage:** «Demo ohne Ollama (Mock)», «Modell in .env», «Tick einschränken (0 = gesamter Lauf)»; zwei Entwicklerschalter («Datenkontext anzeigen», «Artefakt-Checks anzeigen») stehen gleichrangig neben der Frage. | P7.6 |
| R7 | mittel | **Dateien:** absoluter lokaler Pfad sichtbar; vorgewählt ist die alphabetisch erste Datei (`cib_matrix.json`) statt einer, die jemand öffnen will. | P7.6 |
| R8 | mittel | **Animation:** englische Titel (Q6), neun Diagramme mit eigener Zeitachse (Q11). | P7.6 |
| R9 | niedrig | Bericht: Titel «Simulationsbericht: Flugverkehr Szenarioplanung MVP» aus dem Vorgabenamen. | P7.2 |

### M — Modell

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| M1 | hoch | **157 Eingabeelemente auf 4,19 Bildschirmen** in einer flachen Liste aus Klappen — ohne Suche, ohne Sprungmarken zu den fünf Abschnitten, ohne Anzeige, was geändert ist. | P7.7 |
| M2 | hoch | **Zwei Wirkungen in einer Fläche, ohne sichtbare Trennung.** Felder ändern den Entwurf (gilt für den nächsten Lauf), Knöpfe schreiben dauerhaft in `configs/` (gilt für alle). Welches was tut, steht nur im Hinweistext unter dem Knopf; die Rückfrage ist ein Browserdialog ohne Diff (Q8). | P7.7 |
| M3 | mittel | Laufzeit- und Rechengrößen erscheinen als bearbeitbare Klappen mit Rohnamen («provider_markup», «ticket_price»). Seit P3.1 dürfen sie nicht einmal in Regeln stehen. | P7.7 |
| M4 | mittel | **Regel-Editor:** «ab Runde», «über … Runden» (Q6); Regeln entstehen über ein Zahlenfeld «Anzahl Regeln» statt über Hinzufügen und Entfernen; kein Bild des entstehenden Verlaufs. | P7.7 |
| M5 | mittel | Veraltete Texte: «Faktorlage» im Untertitel, Verweis auf den entfallenen Schritt «Ausgangslage» (Q6). | P7.2 (vorziehbar) |

### H — Handbuch

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| H1 | hoch | **Das Handbuch liest sich zwischen Bedienfeld, Telemetrie und Zeitleiste.** Es ist kein Fokusbereich: 868 px Fläche, davon 16 rem Kapitelliste; rechts laufen Kennzahlen eines Laufs, der mit dem Kapitel nichts zu tun hat. | P7.3, P7.8 |
| H2 | mittel | **Inhalte gegen die Oberfläche prüfen.** Das Kapitel «CIB-Konsistenzprüfung — Wie bewertet wird, ob ein Szenario in sich stimmig ist» rahmt eine Bewertung, die seit P2.2 (Variante C) keine Rolle mehr hat; der Text selbst nennt die Grenze ehrlich. Weitere Kandidaten: «die sieben Ansichten» (`ergebnisse-lesen`), «Gestartet wird im Bedienfeld links» (`lauf-starten`). Nicht vollständig gegengelesen. | P7.8 |
| H3 | niedrig | Die Suche findet Kapitel, nicht Stellen — keine Trefferzeile, kein Abschnittsverzeichnis im Kapitel. | P7.8 |

---

## Teil 3 — Benchmark

Verglichen mit dem, was professionelle Analyse- und Simulationsoberflächen leisten (Grafana, Datadog, Tableau, AnyLogic, Foundry) und was etablierte Gestaltungssysteme festschreiben (IBM Carbon, Atlassian, Material 3). Der Maßstab ist das Fachwerkzeug, nicht die Verbraucher-App.

| Erwartung | AeroForesight heute | Lücke |
| --- | --- | --- |
| **Tokens für Schrift, Abstand und Breite**, nicht nur für Farbe | Farbe ja; alles andere als Einzelregeln (Q1, Q2, Q4) | **fundamental** |
| **Ein Kontext je Bildschirm**, und der ist benannt | Entwurf, vergangener Lauf und Tick 1 gleichzeitig (Q5) | **fundamental** |
| **Produktsprache**: keine internen Kennungen, ein Begriff je Sache, eine Sprache | Paket-IDs, Dateinamen, Roh-Markdown, Deutsch/Englisch, Tick/Runde (Q3, Q6) | groß |
| **Lauf-Verwaltung**: Name, Datum, Status, Suche, Filter, Gruppen | 388 technische Kennungen in einem Auswahlfeld (K1) | groß |
| **Rückmeldung**: Ladeanzeige ab etwa 300 ms, Budget für sichtbare Wechsel | Ladeanzeige global aus; 10,5 s ohne Anzeige (Q7) | groß |
| **Navigation auf jeder unterstützten Breite erreichbar** | ab 1024 px teilweise, bei 375 px gar nicht (Q10) | groß |
| **Diagramme**: vollständige Achsen, lokalisierte Reihen, kategoriale Palette, eine Zeitachse | beschnittene Titel, Spaltennamen, zehn Standardfarben, zweite Zeitachse (Q11) | mittel |
| **Formularmuster**: Beschriftung > Hinweis > Fehler; bedingte Felder | Hinweis größer als Beschriftung; wirkungslose Felder aktiv (E5, E8) | mittel |
| **Modellpflege**: Suche, Diff vor dem Speichern, gestalteter Bestätigungsdialog, Verlaufsvorschau | flache Liste, Browserdialog, kein Diff (M1, M2) | mittel |
| **WCAG 2.2 AA** geprüft, einheitlicher Fokusring | Grundlagen da; Kontrastverstöße, Fokus uneinheitlich (Q9) | mittel |
| **Progressive Offenlegung mit benannten Inhalten** | vorbildlich, nur uneinheitlich im Baustein (Q8) | klein |
| **Ehrliche Zustände** (unbestimmt, beeinträchtigt, Abbruch) | vorbildlich | — |

---

## Teil 4 — Zielbild und Entscheidungen vorab

Das Zielbild in einem Satz: **Ein ruhiges, dichtes Fachwerkzeug, das auf jedem Bildschirm genau eine Sache zeigt, sie benennt, und in einer Sprache darüber spricht, die ein Strategieanalyst ohne Projektgeschichte versteht.**

Sieben Entscheidungen stehen vor den Paketen. Je eine Empfehlung ist dabei; entschieden wird von Haiko.

| # | Frage | Empfehlung | Warum |
| --- | --- | --- | --- |
| **D1** | Ein Gestaltungssystem in Tokens (Schrift, Abstand, Breite, Komponentenrollen) vor jeder Ansichtsarbeit? | **Ja.** | Ohne es wird jede Ansicht einzeln repariert, und Q1 wiederholt sich an der nächsten. |
| **D2** | Welche Bereiche zeigen die Seitenzonen? | **Nur der Leitstand.** Ergebnisse und Handbuch werden Fokusbereiche mit eigenem Lauf-Kopf; Telemetrie und Zeitleiste gehören dem Leitstand. | Q5 lässt sich nicht durch Beschriftung lösen, nur durch Weglassen. |
| **D3** | Wohin gehören Begründungen, Vorbehalte und Entstehungsgeschichte? | **In eine zweite Ebene.** Sichtbar sind These und höchstens zwei Sätze; der Rest steht hinter «Begründung und Quellen». Metakommentar entfällt. | Die Ehrlichkeit bleibt vollständig erreichbar, stört aber nicht mehr die Entscheidung. |
| **D4** | Welche Breiten werden unterstützt? | **Voll ab 1280 px, bedienbar ab 1024 px, lesbar ab 375 px** (Ergebnisse und Handbuch mit Navigation; Einrichten und Modell am Telefon nur lesend). | Ein Leitstand auf dem Telefon ist kein Ziel; eine unerreichbare Navigation ist trotzdem ein Fehler. |
| **D5** | Wie viele Zeitachsen gibt es in «Ergebnisse»? | **Eine.** Die animierten Diagramme folgen dem Tick der Zeitleiste oder zeigen den Endstand; eigene Abspielknöpfe entfallen. | P1.5 hat die zweite Zeitachse aus gutem Grund abgeschafft; «Animation» hat sie zurückgebracht. |
| **D6** | Wie heißt ein Lauf in der Oberfläche? | **Name · Rahmen · Datum**, die Kennung nur in «Technische Details». Testläufe standardmäßig ausgeblendet. | K1 ist mit 388 Einträgen heute schon nicht mehr bedienbar. |
| **D7** | Wie wird eine dauerhafte Modelländerung bestätigt? | **Gestalteter Dialog mit Diff** (alt → neu je Größe) und Reichweite. | Die folgenreichste Handlung der Oberfläche verdient den besten Dialog, nicht den des Browsers. |

---

## Teil 5 — Arbeitspakete (Phase 7)

**Reihenfolge ist Absicht:** erst messen, dann das Fundament, dann die Sprache, dann Rahmen und Navigation, dann die Bereiche, zuletzt Barrierefreiheit und Gegenprobe. Jedes Unterpaket ist **ein Commit** mit Test und Doku (Regelwerk im Projektplan). **Jede Abnahme ist eine Messung, keine Zählung** — Regel 7; Q1 zeigt, was passiert, wenn man die falsche Größe misst.

### P7.0 — Messfundament für die Gestaltung

Ohne diese Wächter wiederholt sich der Befund aus Q1: eine Zusage, die erfüllt ist, während die Seite schlecht aussieht. Alle messen im Browser-Wächter (`tests/test_web_overflow.py` oder eine Schwesterdatei) in beiden Designs, bei 1440 und 1024 px, und halten den Ist-Stand zunächst als Sperrklinke.

| # | Paket | Abnahme |
| --- | --- | --- |
| U0.1 | **Kantenwächter:** Innerhalb eines Inhaltscontainers enden Fließtexte an höchstens einer rechten Kante; Kasten und Text eines Hinweises sind gleich breit (± Innenabstand). | Meldet heute Schritt 1 und «Prüfen & Starten»; eine Mutationsprobe mit `48ch` auf 12-px-Text wird rot. |
| U0.2 | **Schriftwächter:** Die gerenderten Schriftgrößen je Ansicht liegen in der Skala aus U1.1; ein Feldhinweis ist nie größer als seine Beschriftung. | Meldet heute acht Größen in Schritt 1 und 15 > 14 px in Schritt 4. |
| U0.3 | **Markdown-Wächter:** kein `**`, kein Backtick-Paar im sichtbaren Text außerhalb von Code-Elementen — im DOM gemessen **und** statisch per AST (`html.P`/`html.Span` mit Markdown-Literal). | Meldet heute die drei Stellen aus Q3. |
| U0.4 | **Kontrastwächter:** jeder sichtbare Textknoten ≥ 4,5 (große Schrift ≥ 3,0), informationstragende Symbole ≥ 3,0. | Meldet heute «optional» und drei Symbole. |
| U0.5 | **Wechselwächter** je Ergebnis-Ansicht: sichtbarer neuer Inhalt nach < 1 s, **oder** eine Ladeanzeige nach < 300 ms; Nutzlast je Ansicht gedeckelt. | Meldet heute «Animation» (10,5 s, 19,3 MB). |
| U0.6 | **Sprachwächter** über den gerenderten Text aller Ansichten: keine Paketkennungen (`P\d\.\d+`), keine Pfade unter `configs/` und `outputs/`, keine `snake_case`-Bezeichner außerhalb von Code-Elementen und der Ansicht «Dateien». Ausnahmen mit Grund in einer Liste; eine verfallene Ausnahme wird gemeldet. | Meldet heute die Liste aus Q6. |

### P7.1 — Ein Gestaltungssystem statt Einzelregeln (setzt D1 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U1.1 | **Schriftskala als Tokens:** höchstens sieben Rollen (etwa Titel, Überschrift, Zwischenüberschrift, Fließtext, klein, Beschriftung, Mono). `H1`/`H2`/`H3`/`CAPTION`/`HINT`/`LABEL` in `components.py` bauen darauf. Die Kaskadenkollision `af-md` gegen `af-hint` ist behoben, nicht umgangen. Frage und Abschnitt sind unterscheidbar. | U0.2 grün auf allen Ansichten. |
| U1.2 | **Breiten als Tokens statt `ch` am Element:** `--breite-lesen`, `--breite-formular`, `--breite-inhalt` in `rem`, gesetzt **am Container**. Texte füllen ihren Container; Hinweiskästen nehmen die Breite ihres Inhalts. `af-mass` und die verstreuten `max-w-*` entfallen oder werden Aliase. Die Zusage «höchstens 75 Zeichen je Zeile» bleibt und wird am Container gehalten. | U0.1 grün; die Zeichenzusage aus W5.4 bleibt grün; der Linux-Vorbehalt aus P3.17 ist mit `rem` gegenstandslos. |
| U1.3 | **Abstands- und Rasterskala:** ein Grundraster (4 px), feste Abstände zwischen Abschnitt, Karte, Feld und Hinweis; ein Inhaltsraster, an dem Überschrift, Karte und Text dieselbe Kante teilen. | Kein Abstand außerhalb der Skala im CSS (statischer Wächter); die rechten Kanten aus Q4 fallen auf höchstens zwei zusammen. |
| U1.4 | **Komponentenrollen:** **ein** Hinweisbaustein mit Tönen (Kontext, Info, Erfolg, Warnung, Fehler) statt `note` und `alert`; **eine** Kachel mit Varianten Zahl/Text/kompakt; `expert` zählt nur, wenn es Parameter sind; **eine** Regel, wann Akkordeon, Klappe oder «Mehr dazu»; höchstens eine Primäraktion je Fläche; ein gestalteter Bestätigungsdialog (D7). **Markdown als Eigenschaft des Textes**: Ein Baustein nimmt Text entgegen und entscheidet selbst — kein Aufrufer wählt mehr zwischen `html.P` und `dcc.Markdown`. | U0.3 grün; kein `dcc.ConfirmDialogProvider` mehr in `dashboard/web/`. |
| U1.5 | **Diagrammstandard:** kategoriale Palette aus den Tokens mit höchstens acht Tönen (darüber Gruppierung); Achsentitel nie beschnitten; Reihennamen aus dem Glossar statt aus Spaltennamen; Einheit im Achsentitel; zwei Höhenstufen. | Teil 8 des Browser-Wächters misst zusätzlich die Achsentitel-Box gegen die Figurenbox. |
| U1.6 | **Musterseite** unter einem internen Pfad: jeder Baustein in allen Zuständen, hell und dunkel — die Referenz, gegen die U0.1 bis U0.4 laufen. | Die Wächter aus P7.0 laufen auch gegen diese Seite. |

### P7.2 — Produktsprache (setzt D3 und D6 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U2.1 | **Widerspruchsfreie Zählung des Vergleichs** (E1): eine Funktion liefert, was ein Vergleich rechnet; Einstieg, Bedienfeld, Kacheln und Satz lesen daraus. **Vorziehbar.** | Ein Test hält alle vier Stellen gegen `rahmenszenarien()`. |
| U2.2 | **Veraltete Texte korrigieren** (E4, E7, M5, leere Zustände). Texte, die auf Schritte verweisen, nehmen Nummer und Titel aus `wizard.STEPS`. **Vorziehbar.** | Ein Wächter meldet jede Schrittnummer und jeden Schrittnamen in einem Literal, die nicht aus `STEPS` stammen. |
| U2.3 | **Interne Kennungen aus dem sichtbaren Text** (Q6): Paket-IDs streichen, Stresstest «P5.7» umbenennen, Feldnamen durch Glossar-Namen ersetzen, Pfade und Hashes hinter «Technische Details». | U0.6 grün. |
| U2.4 | **Ein Oberflächen-Glossar:** Tick (nicht Runde), Lauf (nicht Run), Diagramme (nicht Figures), Ereignisse (nicht Events), Kennung (nicht Run-ID); deutsche Diagrammtitel; Fachbegriffe wie «Surplus» nur mit deutscher Erklärung. `glossary.py` ist die Quelle. | Ein Wächter hält die verbotenen Varianten fern (Textdurchlauf mit Ausnahmeliste). |
| U2.5 | **Textbudgets und zweite Ebene** (D3): Vorspann ≤ 200 Zeichen, Hinweis ≤ 280, Kachelhinweis ≤ 80. Kohärenzbegründung: These und Kurzfassung sichtbar, Langfassung, Quellen und Vorbehalt hinter einer Klappe. Metakommentar entfällt. **Kein Inhalt geht verloren** — `test_rahmen_traegt_begruendung.py` bleibt unverändert grün. | Statischer Wächter über Literale und über die Kohärenzfelder. |
| U2.6 | **Formate:** Zeitstempel lokal und lesbar («07.09.2026, 20:25»), Tausenderpunkte, Einheiten; Ticks mit Modellzeit («120 Ticks · rund 10 Jahre Modellzeit»). **Zu entscheiden:** ob die Umrechnung angezeigt wird — Invariante 5 betrifft Daten, nicht die Anzeige, P3.8 hat die Einheit festgelegt. | Kein ISO-Zeitstempel im sichtbaren Text (Teil von U0.6). |
| U2.7 | **Marke und Vorgaben:** Browser-Titel «AeroForesight AI · ‹Bereich›», Vorgabename ohne «MVP», Umlaute in allen Vorgabetexten. **Vorziehbar.** | Ein Test über `serve_layout` und die Vorgaben. |

### P7.3 — Rahmen, Navigation und Kontext (setzt D2 und D6 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U3.1 | **Seitenzonen nur im Leitstand** (D2): Ergebnisse und Handbuch werden Fokusbereiche. | `shell.FOCUS_ROUTES` enthält alles außer dem Leitstand; `test_web_shell.py` hält es; Viewport «Ergebnisse» bei 1280 px ≥ 90 % der Breite. |
| U3.2 | **Lauf-Kopf** im Leitstand und in «Ergebnisse»: Name, Rahmen, Rechenmodus, Datum, Zustand — **einmal**, kompakt, Banner nach dem ersten Lesen einklappbar. Die Kopfzeile trägt keinen laufbezogenen Zustand mehr, sondern nur, ob gerade gerechnet wird. | R1: erstes Diagramm in «Figures» bei 1440 × 900 oberhalb von y = 300. |
| U3.3 | **Lauf-Browser statt Auswahlfeld** (D6): Liste mit Name, Rahmen, Datum, Modus und Zustand; Suche; Filter nach Art (Einzellauf, Vergleich, Ensemble, Test); zeitlich sortiert. Behebt nebenbei die alphabetische Vorauswahl. | Mit 388 Läufen findet eine Suche nach einem Rahmennamen den jüngsten Lauf mit höchstens zwei Eingaben; Testläufe standardmäßig ausgeblendet. |
| U3.4 | **Kopfzeilen-Aktionen im Kontext:** «Als Szenario sichern» nur im Einrichten, «Dateien herunterladen» nur bei einem Lauf; jede Aktion beschriftet oder mit sichtbarem Tooltip. | Kein Symbolknopf ohne sichtbare Beschriftung ab 1280 px. |
| U3.5 | **Ladeanzeige global:** `._dash-loading` wird nicht pauschal versteckt; ein gestalteter Ladezustand (Skelett oder Balken) erscheint nach 300 ms für jeden Bereich, der neu gebaut wird. | U0.5 grün auf allen Ansichten außer «Animation» (die kommt in P7.6). |

### P7.4 — Einrichten

| # | Paket | Abnahme |
| --- | --- | --- |
| U4.1 | **Schritt 1 neu gegliedert:** Rahmenszenarien und Stresstests als zwei Gruppen, Stresstests zugeklappt; Kachel mit Name, Kurzthese, Länge und Eingriffen ohne gekürzten Satz; Einzelheiten neben der Auswahl statt darunter; Kohärenz nach U2.5. | Schritt 1 ≤ 1,0 Bildschirm bei 1440 × 900; U0.1 bis U0.3 grün. |
| U4.2 | **Formularmuster in den Schritten 2 bis 5:** Beschriftung > Hinweis > Fehler; Felder, die im gewählten Rechenmodus nicht wirken, sind ausgegraut **und** sagen warum (Regel 6: ausblenden, nicht weglassen); die Ollama-Prüfung hat drei unterscheidbare Zustände. | Ein Test: Bei «Nur Zahlen» sind Modellname, Adresse, Kreativität und Antwortlänge `disabled` und tragen einen Grund. |
| U4.3 | **«Lauf & Ablage» aufgeräumt:** eine Überschriftebene, kein doppelter Speicherweg, «Zurücksetzen» mit Rückfrage und Rücknahme. | Kein zweiter Speicherweg im Schritt; Zurücksetzen lässt sich mit einem Klick rückgängig machen. |
| U4.4 | **«Prüfen & Starten» als Zusammenfassung:** was läuft (ein Satz), womit, wie lange, was abweicht, was zu beachten ist — in dieser Reihenfolge. Modellinterna und Herkunft hinter «Technische Details»; Hinweise als eine Liste mit Sprung zum Schritt. | ≤ 1,0 Bildschirm bei 1440 × 900 für einen Lauf ohne Abweichungen; der Höhen-Deckel in `DECKEL` wird entsprechend gesenkt (Sperrklinke). |
| U4.5 | **Ein Speicherweg** «Als Szenario sichern» mit Name, Vorschlag und Warnung vor dem Überschreiben; «Snapshot» wird eine Option dieses Weges. | Genau eine Aktion, die `save_custom_sweep_preset` auslöst; `app._save` und `_handle_action("save-preset")` sind zusammengeführt. |
| U4.6 | **Einstieg** kompakt und mittig, Wege als Raster statt als drei vollbreite Karten. | Einstieg ≤ 0,6 Bildschirme bei 1440 × 900, ohne Leerraum über 50 % der Inhaltsbreite. |

### P7.5 — Leitstand

| # | Paket | Abnahme |
| --- | --- | --- |
| U5.1 | **Bedienfeld:** Stand-Zeilen mit Beschriftung über dem Wert statt daneben; Preflight kompakt (ein Satz, Hinweise als Zähler mit Sprung); interne Kennungen weg; der klebende Fuß verdeckt nichts. | Keine gekürzte Stand-Zeile bei 1280 px; Zone ≤ 1,0 Bildschirm; die P1.6-Zusage (≤ 1,5) ist wieder gehalten und verschärft. |
| U5.2 | **Lauf-Kopf** im Viewport (aus U3.2). | Der Name des gezeigten Laufs steht ungekürzt im Viewport. |
| U5.3 | **Szene:** Faktorleiste lesbar (Kurzname, zweizeilig, Langtext im Tooltip); Einblendung außerhalb der Zeichenfläche; Überplottung behandelt (Transparenz nach Dichte oder Stichprobe mit Angabe). | Kein gekürzter Faktorname bei 1280 px; die Einblendung überdeckt keinen Datenpunkt. |
| U5.4 | **Zeitleiste:** Marken ohne Überlappung (Mindestabstand in Pixeln statt fester Schritt); Ereignisstreifen mit Legende und Tooltip, der das Ereignis nennt. **Vorziehbar.** | Ein Test auf `_marks` für 1 bis 500 Ticks: keine zwei Marken näher als ein Mindestabstand; im Browser keine überlappenden Beschriftungen. |
| U5.5 | **Telemetrie:** Einheiten an allen Verläufen; eine Legende, die sagt, was die Färbung der Veränderung bedeutet. | Jede Sparkline trägt ihre Einheit. |

### P7.6 — Ergebnisse (setzt D5 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U6.1 | **Gliederung der Ansichten:** Der Lauf-Kopf steht einmal (U3.2); die sieben Ansichten in drei Gruppen — Auswertung (Szenario, Diagramme, Bericht), Population (Animation), Werkzeuge (Abfrage, Dateien, Herkunft). «Übersicht» heißt, was sie ist: Herkunft des Laufs. | R1 behoben; keine doppelte Zusammenfassung. |
| U6.2 | **Animation schnell und mit einer Zeitachse** (D5): die Diagramme folgen dem Tick der Zeitleiste oder zeigen den Endstand; jedes Diagramm lädt erst beim Aufklappen; Stichprobe oder Aggregat statt aller Personen je Frame. | U0.5 grün für «Animation»; Nutzlast der Ansicht ≤ 2 MB; keine Plotly-Abspielknöpfe mehr im Dashboard. |
| U6.3 | **Szenario-Ansicht:** Name statt Kennung, Faktorzustände in Klartext, «Gerechnete Kennzahlen» statt «Ground Truth», «Szenarien neu erzeugen» sagt, dass es ohne Sprachmodell rechnet. | U0.6 grün für die Ansicht. |
| U6.4 | **Diagramme:** Standard aus U1.5; der Vergleich zeigt die Rahmen **eines** Vergleichslaufs mit ihren Namen, nicht alles aus `outputs/sweeps/`; Politik-Reihen mit Glossar-Namen. | Keine Testläufe im Vergleich; Reihennamen ohne `_`. |
| U6.5 | **Abfrage:** Produkttexte (Beispielantwort statt «Mock», kein `.env`), Tick-Filter ohne Magie-Null, Entwicklerschalter hinter «Technische Details». | U0.6 grün für die Ansicht. |
| U6.6 | **Dateien:** relative Pfade, sinnvolle Vorauswahl (Bericht oder `run_metadata.json`), gruppiert nach Art. | Kein absoluter Pfad im sichtbaren Text. |
| U6.7 | **Übersicht/Herkunft:** Namen und Hashes in der Textvariante der Kachel, Fingerabdruck als Tabelle hinter «Technische Details». | U0.2 grün für die Ansicht. |

### P7.7 — Modell (setzt D7 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U7.1 | **Orientierung:** Sprungmarken zu den fünf Abschnitten, Suche nach Größe, Anzeige der geänderten Größen je Abschnitt. | Jede Größe mit höchstens zwei Eingaben erreichbar; die Zahl der Änderungen steht an jedem Abschnitt. |
| U7.2 | **Zwei Wirkungen sichtbar getrennt:** Änderungen für den nächsten Lauf und dauerhaftes Speichern ins Modell unterscheiden sich in Farbe, Ort und Beschriftung; Speichern zeigt einen Diff (alt → neu) im gestalteten Dialog. | Kein Browserdialog; ein Test: Speichern ohne Änderung ist gesperrt, Speichern mit Änderung zeigt jede Differenz. |
| U7.3 | **Laufzeit- und Rechengrößen** (`source: runtime`/`computed`) nicht als bearbeitbare Klappe, sondern als Lesewert mit Erklärung. | Ein Test gegen `property_engine.darf_in_regel_stehen`. |
| U7.4 | **Regel-Editor:** «Regel hinzufügen» und «Entfernen» statt «Anzahl Regeln»; «ab Tick»; eine kleine Vorschau des entstehenden Verlaufs. | Keine «Runde» im Modell-Bereich (Teil von U2.4). |

### P7.8 — Handbuch

| # | Paket | Abnahme |
| --- | --- | --- |
| U8.1 | **Lesefläche:** Fokusbereich (U3.1), Lesebreite aus U1.2, Abschnittsverzeichnis des Kapitels, Suche mit Trefferzeile. | Artikelbreite = `--breite-lesen`; ein Suchtreffer zeigt die Stelle. |
| U8.2 | **Inhalte gegen die Oberfläche geprüft:** jede Bedienaussage aller Kapitel am laufenden System nachgestellt; das CIB-Kapitel nach P2.2 gerahmt (Beleg, keine bewertende Rolle). | Ein Protokoll im Paket listet jede geprüfte Aussage mit Ergebnis. |

### P7.9 — Barrierefreiheit und schmale Breiten (setzt D4 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| U9.1 | **Kontraste** in beiden Designs nach U0.4. | U0.4 grün, hell und dunkel. |
| U9.2 | **Ein Fokusring-Token** für alle interaktiven Elemente; ein Tastaturdurchgang je Bereich, protokolliert. | Jedes interaktive Element trägt bei `:focus-visible` denselben Ring (statisch geprüft); Protokoll im Paket. |
| U9.3 | **Navigation auf jeder unterstützten Breite** (D4): bei 1024 px vollständig sichtbar, darunter als Menü. | Bei 1024 und 375 px sind alle fünf Bereiche mit höchstens einem Klick erreichbar (Browser-Wächter). |
| U9.4 | **Automatisierte WCAG-Prüfung** im Browser-Wächter (etwa axe-core, **lokal eingebunden**, kein CDN — P1.4). | Keine Verstöße der Stufen «serious» und «critical» auf allen Ansichten; Ausnahmen mit Grund. |

### P7.10 — Gegenprobe

| # | Paket | Abnahme |
| --- | --- | --- |
| U10.1 | **Unabhängige Gegenprobe** der zugesagten Größen (nicht der gemeldeten Befunde — Lehre aus P1.8): alle Ansichten, beide Designs, drei Breiten, mit Bildschirmfotos im Protokoll. | Jede Abnahme aus P7.0 bis P7.9 nachgemessen; Abweichungen werden eigene Pakete. |
| U10.2 | **Übergang zu Teil 2** (technische Umsetzung): Nebenbefunde aus Anhang B und alles, was bei der Umsetzung aufgefallen ist. | Teil 2 des Audits ist beauftragt. |

---

## Teil 6 — Reihenfolge und Sofortmaßnahmen

```
P7.0 (Messen) ─> P7.1 (Gestaltungssystem) ─┬─> P7.2 (Sprache) ─┐
                                           │                   │
                                           └─> P7.3 (Rahmen) ──┼─> P7.4 Einrichten
                                                               ├─> P7.5 Leitstand
                                                               ├─> P7.6 Ergebnisse
                                                               ├─> P7.7 Modell
                                                               └─> P7.8 Handbuch
                                                                        │
                                               P7.9 (A11y, Breiten) ────┤  (begleitend ab P7.1)
                                                                        v
                                                                  P7.10 (Gegenprobe)
```

**Vorziehbar**, weil sie an nichts hängen und einen sichtbar falschen Zustand beheben — je ein Commit mit Test:

1. **U2.1** — Vergleich widerspruchsfrei zählen (E1, kritisch)
2. **U2.2** — veraltete Texte (E4, E7, M5, leere Zustände)
3. **U0.3 + Q3-Fix** — Roh-Markdown (die drei Stellen, samt Wächter)
4. **U5.4** — Zeitleistenmarken «490»
5. **Q2-Kaskade** — Hinweis kleiner als Beschriftung (Teil von U1.1)
6. **Q9** — Kontrast von «optional» (Teil von U9.1)
7. **U2.7** — Browser-Titel und «MVP»

Die sieben ändern keine Architektur und machen die Oberfläche in einem Tag spürbar ordentlicher. **Den Befund aus dem Screenshot beheben sie nicht**: Q1 braucht U1.2, und U1.2 braucht D1.

---

## Anhang A — Messwerte

**Höhe in Bildschirmen**, 1440 × 900, dunkles Design:

| Ansicht | Bildschirme | Anmerkung |
| --- | ---: | --- |
| Einrichten › Einstieg | < 1 | Inhalt 567 px |
| Schritt 1 «Was soll gerechnet werden?» | **1,84** | mit Standard-Ausgangslage |
| Schritt 2 «Wie weit reicht der Lauf?» | 1,00 | |
| Schritt 3 «Womit wird gerechnet?» | 1,00 | |
| Schritt 4 «Lauf & Ablage» | 1,07 | |
| Schritt 5 «Technik» | 1,00 | |
| Schritt 6 «Prüfen & Starten» | **1,59** | ohne Abweichungen |
| Leitstand › Bedienfeld | **1,73** | 1458 / 844 px |
| Leitstand › Telemetrie | 1,07 | 904 / 844 px |
| Modell | **4,19** | 157 Eingabeelemente |

**Zonenbreiten**, 1440 px, Leitstand/Ergebnisse/Handbuch: Bedienfeld 272 px, Viewport 868 px (60 %), Telemetrie 288 px.

**Schriftgrößen**, Schritt 1 ohne Symbolschrift: 11, 12, 12,19, 13, 14, 15, 16, 20 px. Feldhinweis 15 px, Feldbeschriftung 14 px (Schritt 4).

**Kontraste**, dunkel: «optional» 3,77 und 2,87; Symbole 2,80. Übrige Textknoten der Schrittfolge ≥ 4,5.

**Animation:** `animation.render` 10,52 s, Serialisierung 0,71 s, Nutzlast 19,3 MB; im Browser nach 10 s kein Wechsel.

**Lauf-Auswahl:** 388 Einträge; die ersten acht: `sweeps/sweep_transformation_conflict`, `…test_short`, `…low_base`, `…llm_schalter_aus`, `…llm_schalter_an`, `…kein_sprachmodell`, `…high_base`, `…freiwillige_wende`, alle mit «— Trend-Fortsetzung».

**Schmale Breiten:** 1024 px — sichtbar «Einrichten», «Leitstand», «Ergi…»; 375 px — `.af-nav__links` `clientWidth 0`, Seite ohne waagerechten Überlauf (`scrollWidth 375`).

## Anhang B — Nebenbefunde außerhalb des Auftrags (für Teil 2)

Beim Lesen aufgefallen, nicht Gegenstand dieses Teils, **nicht nachgemessen**:

- **`docs/audit_findings.md`, Abschnitt Dashboard**, führt Befunde, deren Pakete laut Projektplan erledigt sind — null Live-Regionen (W5.3), kein `cancel` (W4.5), Sweep-Pfad verwirft den Entwurf (W1.1), `ticks_override` (W1.2), Schrittliste nach Position (W2.1–W2.3), CDN-Abhängigkeiten (P1.4). Das wäre die Pflegeregel des Dokuments; zu prüfen und zu entfernen.
- **Veraltete Docstrings:** `config_editor/__init__.py` spricht von «acht Schritten» und vier Reitern, `macro.py` von einem Modul `factors.py`, das es nicht mehr gibt.
- **Testläufe in `outputs/sweeps/`** fließen in Vergleiche ein (Q11). Neben der Oberfläche (U6.4) ist das eine Frage der Datenhaltung.
- **`scenario._regenerate`** erzwingt `mock_llm=True, deterministic_only=True`, unabhängig vom Rechenmodus des Laufs — Oberfläche in U6.3, Verhalten in Teil 2.
