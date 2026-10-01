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
| Drei ganzseitige Screenshots | **erledigt** (2026-09-29): `docs/pitch/pitch_folie4_verlaeufe.png` (Verläufe, CO₂-Steuer angehoben), `pitch_folie3_leitstand.png` für Folie 5, `pitch_folie6_szenarien.png` (die vier Rahmen im Vergleich; **alle drei am 2026-10-01 neu aus dem Vorführbestand**, siehe «Die Bilder»; ursprünglich frisch gerechnet über 120 Ticks); je 1920 × 1080 bei doppelter Pixeldichte. **Ohne KI-Text** (entschieden am 2026-09-29): Die Texte mit `llama3.2` widersprachen der Rechnung, und ein Bild der Ansicht „Abfrage“ scheiterte am selben Grund — siehe Skript |
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

**Neu aufgenommen am 2026-10-01**, weil die Bilder vom 2026-09-28/29 nicht mehr zur Geschichte passten: Folie 4 zeigte eine CO₂-Abgabe, die ab Tick 24 allmählich steigt, unter «Plätze füllen»; Folie 5 zeigte direkt danach einen **unveränderten** «Business as Usual»-Lauf mit lesbarer «CO₂-Abgabe 50 €/t» — während gesprochen wird, die Planerin habe die Abgabe erhöht. Dazu standen im Leitstand Zahlen mit englischem Dezimalpunkt («37.4%», «131.94 €»). Alle drei Bilder kommen jetzt aus dem **Vorführbestand** (`python -m dashboard.vorfuehrbestand`), also aus denselben Läufen, die am Stand gezeigt werden. Aufgenommen mit Playwright bei 1920 × 1080 und doppelter Pixeldichte am laufenden Dashboard, Codestand dieses Branches.

- **Folie 4 (Verläufe):** «Business as Usual», 40 Ticks, CO₂-Steuer mit einem zweiten Stützpunkt: ab Tick 24 «springt auf den Wert» 200 €/t, Preisstrategie «Aufschlag halten» — genau die Einstellung des Pitch-Falls im Bestand.
- **Folie 5 (Leitstand, ohne linke Spalte zugeschnitten; daneben `pitch_folie3_leitstand_voll.png`):** der Pitch-Fall «Vorführung: CO₂-Abgabe steigt auf 200 €» (Mit Sprachmodell, 40 Ticks), Zeitleiste auf Tick 40. Zu sehen: Buchungsrate 8,2 %, Ticketpreis 201,23 €, Kostendruck 173,23 € bei «CO₂-Abgabe 200 €/t»; der Verlauf der Buchungsrate bricht bei Tick 24 ein. **Die Zahlen sind eine Momentaufnahme** des Modellstands und keine Aussage des Pitches; gesprochen wird über sie nicht. Die Referenz ohne Erhöhung («Business as Usual, Aufschlag halten») steht bei Tick 40 bei 194,08 € und 15,9 % (Nachtrag zu Befund 8 im Abnahme-Protokoll).
- **Folie 6 (Szenarien im Vergleich):** der Szenario-Vergleich des Bestands vom 2026-09-30, gewählt «Transformationskonflikt», «Diagramme → 4 · Die Szenarien nebeneinander»; vier Rahmen über 120 Ticks, Achsen mit Dezimalkomma.

**Wer die Bilder neu aufnimmt**, nimmt sie aus dem Bestand und nicht aus einem eigenen Lauf — sonst meinen Folie und Stand verschiedene Zahlen. In `pitch.html` werden sie dann ausgetauscht, nicht die ganze Datei neu gebaut; im Artefakt sind es Assets. **Am 2026-10-01 in beiden nachgezogen:** in `pitch.html` die drei eingebetteten Bilder, im Artefakt (Version 8) drei neue Assets, auf die die Folien «Produkt · Einrichten», «Produkt · Leitstand» und «Produkt · Ergebnis» jetzt zeigen, mit angepassten Alternativtexten. Die alten Assets liegen weiter im Artefakt, damit frühere Versionen ihre Bilder behalten.

## Offene Punkte

- Das Artefakt ist privat. Für andere braucht es Freigabe über sein Teilen-Menü.
- Platzhalter: `[Rolle]` je Person auf Folie 11, `[Kontakt]` auf Folie 12.
- Die Quelle „Aviation sector decarbonisation as a case of deep uncertainty" (ScienceDirect 2025) wurde nur über die Trefferbeschreibung geprüft, nicht im Volltext.
- Das Marktbericht-Zitat für den Cross-Check der Marktgröße hat keinen benannten Herausgeber und gilt nur als Größenordnung.
