# Pitch: Wo liegt was?

Diese Seite beantwortet, wenn im Chat jemand fragt „wo ist der Pitch, wie ändere ich ihn, woher kommt die Zahl?". Anlass ist der Pitch bei „Pitch, Please!" am 08.10.2026 im HdM Startup Center Stuttgart. Stand 2026-09-29: 5-Minuten-Fassung mit zwölf Folien und drei Anhangfolien, zwei Platzhalter offen.

## Die Dateien

| Was | Wo | Zweck |
| --- | --- | --- |
| Präsentation zum Vorführen | [`pitch.html`](../pitch.html) im Repo-Wurzelverzeichnis | Eine einzige Datei, per Doppelklick im Browser zu öffnen. Pfeiltasten oder Klick blättern, F schaltet Vollbild. Die Bilder sind eingebettet. Nur die Schriften (Plus Jakarta Sans, Inter) kommen aus dem Netz, ohne Internet greifen Systemschriften |
| Gesprochener Text | [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md) | Die **5-Minuten-Fassung** mit zwölf Folien (rund 4:35): je Folie, was darauf steht und was gesprochen wird, dazu Anhang für die Fragerunde, die Quellen jeder Zahl und die Herleitung von TAM, SAM und SOM |
| Bearbeitbare Fassung | Artefakt in claude.ai (Haikos Konto): <https://claude.ai/artifact/XRaiAGbnRJ4dj2VQ6qPBEw> | Hier wird der Pitch inhaltlich angepasst, und aus ihm entsteht `pitch.html`. Von dort lässt sich als PowerPoint oder PDF exportieren. Privat, bis es über das Teilen-Menü freigegeben ist |
| Frühere Fassung | Artefakt in claude.ai (Manus Konto): <https://claude.ai/artifact/V8DxvLSBtGVAmrFFYnaVnz> | Manus Deck, auf dem die bearbeitbare Fassung am 2026-09-28 aufsetzt. Es liegt in einer anderen Organisation, und Änderungen daran ließen sich aus Haikos Sitzung nicht speichern; deshalb die Kopie. **Wird nicht mehr gepflegt** (von Haiko entschieden am 2026-09-29): Änderungen gehören in die bearbeitbare Fassung darüber |
| Bilder für die Folien | [`docs/pitch/`](pitch/): `pitch_folie3_leitstand.png` (Leitstand, in der 5-Minuten-Fassung Folie 5), daneben `pitch_folie3_leitstand_voll.png`, dazu `pitch_folie4_verlaeufe.png` und `pitch_folie6_szenarien.png` | Screenshots aus dem laufenden Dashboard, 1920 × 1080 bei doppelter Pixeldichte (der Leitstand ohne linke Spalte zugeschnitten, 3160 × 2052; daneben das ganze Fenster). Wie sie entstanden sind, steht unten |
| Diese Übersicht | `docs/pitch_uebersicht.md` | Wegweiser |

## Umbau auf 5 Minuten (seit 2026-09-29)

Anlass ist eine Vorab-Prüfung am 2026-09-29: Die Sprechzeit steigt von drei auf fünf Minuten, die Folien sollen stützen statt vorlesen, das Produkt soll in großen Bildern zu sehen sein, die Bitte soll sagen, wen wir suchen und warum man sich melden sollte, und der Markt soll als Einstiegsmarkt mit Ausbaupfad erscheinen. Die Entscheidungen dazu stehen im Skript.

| Schritt | Stand |
| --- | --- |
| Skript für 5 Minuten | **erledigt** (2026-09-29) |
| Drei ganzseitige Screenshots | **erledigt** (2026-09-29): `docs/pitch/pitch_folie4_verlaeufe.png` (Verläufe, CO₂-Steuer angehoben), `pitch_folie3_leitstand.png` für Folie 5, `pitch_folie6_szenarien.png` (die vier Rahmen im Vergleich, frisch gerechnet über 120 Ticks); je 1920 × 1080 bei doppelter Pixeldichte. **Ohne KI-Text** (entschieden am 2026-09-29): Die Texte mit `llama3.2` widersprachen der Rechnung, und ein Bild der Ansicht „Abfrage“ scheiterte am selben Grund — siehe Skript |
| Grafiken (Zeitstrahl, Kreislauf, Markttreppe, Vergleichstabelle, Bausteine) | **erledigt** (2026-09-29), als Folienbausteine im Deck, nicht als Bilder — sie bleiben im Editor bearbeitbar |
| Deck umbauen: zwölf Folien plus Anhang, Stichworte statt Sätze, Notizen gleich Skript | **erledigt** (2026-09-29) bis auf zwei Platzhalter: `[Rolle]` je Person auf Folie 11, `[Kontakt]` auf Folie 12 |
| `pitch.html` neu erzeugen und jede Folie im Browser prüfen | **erledigt** (2026-09-29): 15 Folien bei 1920 × 1080 in Chromium aufgenommen, keine Skriptfehler, kein Element unter y = 920 außerhalb der Fußzeile |
| Probe mit Stoppuhr | offen (Manuel und Haiko) |

## Was auf den Folien steht

1. **Aufhänger.** Zeitstrahl der Gratiszertifikate: 75 % (2024) → 50 % (2025) → 0 % ab 2026; Leitsatz „Berechnet, nicht geraten.“
2. **Problem.** Drei Karten — CO₂-Preis „voll ab 2026“, SAF-Quote „2 → 6 → 70 %“, Bahn „Wettbewerb“ — und das Band „Tiefe Unsicherheit: mehrere Szenarien statt einer Prognose“.
3. **Lösung.** Diagramm: Fluggesellschaften, Passagiere und Regulierer reagieren aufeinander → Szenarien → „KI fasst zusammen“, „die Zahlen liefert die Rechnung“.
4. **Produkt · Einrichten.** Screenshot „Verläufe“ (CO₂-Steuer 50 → 200 €/t), drei Stichworte.
5. **Produkt · Leitstand.** Screenshot des Leitstands, drei Stichworte.
6. **Produkt · Ergebnis.** Die vier Rahmen im Vergleich, drei Stichworte. **Kein KI-Text.**
7. **Warum wir.** Tabelle Einzelprognose gegen AeroForesight, vier Zeilen.
8. **Markt.** „235 Organisationen in Europa“ und eine Treppe ① Europa ≈ 9 Mio. € → ② weltweit ≈ 33 Mio. € → ③ weitere regulierte Märkte. **Die Stufen sind nicht maßstäblich**, die Beträge stehen als Zahl darin.
9. **Geschäftsmodell & Fahrplan.** „Jahresabo je Organisation, 30–50 Tsd. €“ und drei Balken, **in der Höhe proportional zum Jahresumsatz**.
10. **Aussicht.** Bausteine: gemeinsamer Kern, darauf „Luftfahrt“ und zwei gestrichelte „nächste Branche“.
11. **Team.** Manuel und Haiko mit Foto, `[Rolle]` und LinkedIn-QR-Code, dazu „Du? Mitgründer:in Vertrieb & Business Development“.
12. **Bitte.** „Wir suchen 3 Design-Partner“ — wen, was sie bekommen, `[Kontakt]`.
- **A1–A3, Anhang für die Fragerunde:** Genauigkeit (Abgleich mit den Marktdaten, Stand 29.09.2026), Marktrechnung als Tabelle, warum ein Sprachmodell — mit dem Satz, dass die Texte mit dem heutigen Modell noch unzuverlässig sind.

Die Sprechernotizen jeder Folie tragen den Text aus dem Skript, die Anhangfolien eine vorbereitete Antwort.

## Woher kommen die Zahlen?

Alles steht mit Quelle in [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md), Abschnitt „Herkunft der Fakten". Kurz:

- **Regulierung** (Gratiszertifikate, SAF-Quote): EASA und EU-Kommission.
- **TAM, SAM, SOM:** eigene Bottom-up-Rechnung aus ACI Europe (Flughäfen) und Airlines for Europe (Airlines), mit offen genannten Annahmen zu Kundenzahl und Jahresvertrag. Sie sind keine Marktstudie. Wer eine Annahme ändert, rechnet im Skript neu und passt Folie 8, 9 und A2 an.
- **Alles über das Modell** (drei Akteure, Zahlen aus der Berechnung, Prüfung an Marktdaten 2015 bis 2024): `README.md`, `CLAUDE.md`, `docs/backtest_vorlauf.md`.

## Was bewusst nicht drin steht

- **Keine Code-Kennzahlen** (Tests, Commits, Zeilen). Sie sagen Investoren nichts über Kunden oder Umsatz.
- **Kein Satz über „Excel" als Planungswerkzeug der Airlines.** Dafür fand sich keine Quelle, er wurde gestrichen.
- **Nichts darüber, wie die Szenarien im System heute aussehen** (etwa Anzahl oder Prozentangaben). Der Pitch verkauft die Fähigkeit, realistische Szenarien zu liefern. Prozentangaben je Szenario gibt es im Produkt noch nicht, deshalb stehen sie nirgends.
- **Keine Pilotkunden, kein Umsatz, keine Investitionssumme.** Nichts davon ist belegt. Die frühere Ask-Folie ist entfallen; seit dem 2026-09-28 steht am Schluss wieder eine Bitte, aber um Kontakte zu Design-Partnern und nicht um Geld.

## So ändert man etwas

- **Text oder Layout ändern:** im Artefakt bearbeiten (die bearbeitbare Fassung oben).
- **`pitch.html` neu erzeugen:** im Chat sagen „erzeuge pitch.html aus dem Artefakt neu". Dabei wird der aktuelle Artefakt-Stand gelesen und jede Folie in die Datei übernommen. Der animierte Hintergrund wird als eingebettetes Fenster eingesetzt, die Bilder werden als Base64 eingebettet, die Sprechernotizen entfallen.
- **PowerPoint:** im Artefakt über das Teilen-Menü als .pptx exportieren. Der animierte Hintergrund wird dabei zu einem Standbild.
- **Skript angleichen:** Nach jeder Textänderung an den Folien gehört das Skript mit, sonst laufen Folie und gesprochener Text auseinander.

## Wo `pitch.html` vom Artefakt abweicht

Zwei Bausteine des Folienformats kennt ein gewöhnlicher Browser nicht; `pitch.html` bildet sie nach:

- **Verbindungslinien** (`x-connector`, Folie 3) werden als SVG-Linien mit Pfeilspitzen gezeichnet.
- **Tabellen** (Folie 7, A2) bekommen ihre Zellenabstände und Trennlinien über eine Regel im Kopf der Datei; im Editor setzt sie das Folienformat selbst.

Die Korrektur am Bild von Folie 3 aus der 3-Minuten-Fassung entfällt mit dem Umbau: Die Screenshots stehen jetzt je auf einer eigenen Folie. Wer `pitch.html` neu erzeugt, rendert danach jede Folie und prüft, dass nichts unter die Fußzeile ragt.

## Die Bilder

**Leitstand (Folie 5):**

Aufgenommen am 2026-09-28 aus dem laufenden Dashboard, Codestand dieses Branches. Der Lauf ist über den Assistenten eingerichtet: Szenario „Business as Usual“, 120 Ticks (10 Jahre), Rechenmodus „Nur Zahlen“, Zufallsstartwert 42; die Zeitleiste steht auf Tick 120. Wer das Bild neu aufnimmt, stellt denselben Lauf ein, damit Folie und Q&A dieselben Zahlen meinen.

- **„Nur Zahlen“, weil beim Aufnehmen kein Ollama lief.** Erkennbar ist das nur an der Zeile oben links. Das Bild zeigt das Rechnen, nicht das Erzählen — ein Bild der KI-Texte bräuchte einen Lauf mit Sprachmodell. Ein Lauf „Ohne Sprachmodell“ wäre die schlechtere Wahl gewesen: Er füllt die Agententexte mit Platzhaltern, und die gehören nicht auf eine Folie.
- **Die Kachel „CO₂-Abgabe 50 €/t“ bei Tick 120 ist richtig.** Unter „Business as Usual“ bleibt die Abgabe laut Szenariodatei bei 50 €; der Anstieg auf 200 € gehört zur Standard-Ausgangslage. Der Kostendruck steigt trotzdem auf 348 €, aus anderen Treibern. Beides ist eine naheliegende Rückfrage.
- **Die Zahlen auf dem Bild sind eine Momentaufnahme** des Modellstands vom 2026-09-28 und keine Aussage des Pitches; gesprochen wird über sie nicht.

**Verläufe und Vergleich (Folien 4 und 6), aufgenommen am 2026-09-29:** Folie 4 zeigt den Schritt „Verläufe“ unter „Business as Usual“ mit „Eigene Werte anwenden“, 120 Ticks und einem Stützpunkt: ab Tick 24 „fährt hoch“ auf 200 €/t über 48 Ticks. Folie 6 zeigt „Die Szenarien nebeneinander“ nach einem Szenario-Vergleich mit Ollama (`llama3.2`); sechs Testläufe vom 2026-09-14, die sonst mitgezeichnet worden wären, lagen dafür im Archivordner `outputs/_archiv_testlaeufe_2026-09-14/`.

## Offene Punkte

- Das Artefakt ist privat. Für andere braucht es Freigabe über sein Teilen-Menü.
- Platzhalter: `[Rolle]` je Person auf Folie 11, `[Kontakt]` auf Folie 12.
- Die Quelle „Aviation sector decarbonisation as a case of deep uncertainty" (ScienceDirect 2025) wurde nur über die Trefferbeschreibung geprüft, nicht im Volltext.
- Das Marktbericht-Zitat für den Cross-Check der Marktgröße hat keinen benannten Herausgeber und gilt nur als Größenordnung.
