# Pitch: Wo liegt was?

Diese Seite beantwortet, wenn im Chat jemand fragt „wo ist der Pitch, wie ändere ich ihn, woher kommt die Zahl?". Anlass ist der Pitch bei „Pitch, Please!" am 08.10.2026 im HdM Startup Center Stuttgart. Stand 2026-09-28.

## Die Dateien

| Was | Wo | Zweck |
| --- | --- | --- |
| Präsentation zum Vorführen | [`pitch.html`](../pitch.html) im Repo-Wurzelverzeichnis | Eine einzige Datei, per Doppelklick im Browser zu öffnen. Pfeiltasten oder Klick blättern, F schaltet Vollbild. Die Bilder sind eingebettet. Nur die Schriften (Plus Jakarta Sans, Inter) kommen aus dem Netz, ohne Internet greifen Systemschriften |
| Gesprochener Text | [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md) | Der Text je Folie, rund 2:45 Minuten, dazu die Quellen jeder Zahl und die Herleitung von TAM, SAM und SOM |
| Bearbeitbare Fassung | Artefakt in claude.ai: <https://claude.ai/artifact/V8DxvLSBtGVAmrFFYnaVnz> | Hier wird der Pitch inhaltlich angepasst. Von dort lässt sich als PowerPoint oder PDF exportieren. Das Artefakt ist privat, nur wer den Link geöffnet und Zugriff bekommen hat, sieht es |
| Bild für Folie 3 | [`docs/pitch/pitch_folie3_leitstand.png`](pitch/pitch_folie3_leitstand.png), daneben `pitch_folie3_leitstand_voll.png` | Der Leitstand nach einem Lauf, 3160 × 2052 bzw. 3840 × 2160 px (1920 × 1080 bei doppelter Pixeldichte). Die erste Fassung ist ohne die linke Spalte zugeschnitten und für die Folie gedacht; die zweite zeigt das ganze Fenster. Wie sie entstanden sind, steht unten |
| Diese Übersicht | `docs/pitch_uebersicht.md` | Wegweiser |

## Was steht auf den sieben Folien

1. **Cover.** Der Aufhänger (EU senkt das CO₂-Preislimit, Airlines raten) und der Satz „Wir liefern die Zukunft des europäischen Luftverkehrs. Berechnet, nicht geraten."
2. **Problem.** Die Zukunft der Luftfahrt ist tief unsicher. Ab 2026 keine kostenlosen Emissionszertifikate mehr, die Forschung fordert mehrere Szenarien.
3. **Lösung.** Drei Akteure (Passagiere, Fluggesellschaften, Regulierer) handeln, daraus werden verschiedene Szenarien gerechnet, die KI erklärt sie.
4. **Markt.** EU-ETS, RefuelEU, CORSIA, dazu TAM 33 Mio. €, SAM 9 Mio. €, SOM 570 Tsd. €.
5. **Traktion.** Nur Kennzahlen: 3 Design-Partner (Jahr 1), ≈300 Tsd. € (Jahr 2), ≈570 Tsd. € (Jahr 3). Das sind Ziele, keine Ist-Werte.
6. **Team.** Manuel Carbajo und Haiko Wiedenberg mit Foto und LinkedIn-QR-Code.
7. **Schluss.** Name und Leitsatz.

## Woher kommen die Zahlen?

Alles steht mit Quelle in [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md), Abschnitt „Herkunft der Fakten". Kurz:

- **Regulierung** (Gratiszertifikate, SAF-Quote): EASA und EU-Kommission.
- **TAM, SAM, SOM:** eigene Bottom-up-Rechnung aus ACI Europe (Flughäfen) und Airlines for Europe (Airlines), mit offen genannten Annahmen zu Kundenzahl und Jahresvertrag. Sie sind keine Marktstudie. Wer eine Annahme ändert, rechnet im Skript neu und passt Folie 4 und 5 an.
- **Alles über das Modell** (drei Akteure, Zahlen aus der Berechnung, Prüfung an Marktdaten 2015 bis 2024): `README.md`, `CLAUDE.md`, `docs/backtest_vorlauf.md`.

## Was bewusst nicht drin steht

- **Keine Code-Kennzahlen** (Tests, Commits, Zeilen). Sie sagen Investoren nichts über Kunden oder Umsatz.
- **Kein Satz über „Excel" als Planungswerkzeug der Airlines.** Dafür fand sich keine Quelle, er wurde gestrichen.
- **Nichts darüber, wie die Szenarien im System heute aussehen** (etwa Anzahl oder Prozentangaben). Der Pitch verkauft die Fähigkeit, realistische Szenarien zu liefern. Prozentangaben je Szenario gibt es im Produkt noch nicht, deshalb stehen sie nirgends.
- **Keine Pilotkunden, kein Umsatz, keine Investitionssumme.** Nichts davon ist belegt. Die frühere Ask-Folie ist entfallen; seit dem 2026-09-28 steht am Schluss wieder eine Bitte, aber um Kontakte zu Design-Partnern und nicht um Geld.

## So ändert man etwas

- **Text oder Layout ändern:** im Artefakt bearbeiten (Link oben).
- **`pitch.html` neu erzeugen:** im Chat sagen „erzeuge pitch.html aus dem Artefakt neu". Dabei wird der aktuelle Artefakt-Stand gelesen und jede Folie in die Datei übernommen. Der animierte Hintergrund wird als eingebettetes Fenster eingesetzt, die Bilder werden als Base64 eingebettet, die Sprechernotizen entfallen.
- **PowerPoint:** im Artefakt über das Teilen-Menü als .pptx exportieren. Der animierte Hintergrund wird dabei zu einem Standbild.
- **Skript angleichen:** Nach jeder Textänderung an den Folien gehört das Skript mit, sonst laufen Folie und gesprochener Text auseinander.

## Folien nachziehen

Das Skript ist am 2026-09-28 überarbeitet worden, die Folien noch nicht. Sie werden im Artefakt geändert und `pitch.html` danach neu erzeugt — nicht in `pitch.html` von Hand, sonst überschreibt die nächste Erzeugung die Änderung. Bis dahin sagen Folie und Sprecher an diesen Stellen Verschiedenes:

- **Folie 1:** Der Aufhänger „Die EU senkt heute das CO₂-Preislimit …“ ist entfallen, weil er keine Quelle hat. Neu: „Ab 2026 bekommen Airlines in Europa keine kostenlosen CO₂-Zertifikate mehr. Wie teuer das wird, hängt am CO₂-Preis, an der SAF-Quote und an der Bahn, alles zugleich.“
- **Folie 2:** Statt der Gratiszertifikate (jetzt auf Folie 1) die SAF-Quote: „2 % heute, 6 % bis 2030“.
- **Folie 3:** „Geprüft an echten Marktdaten von 2015 bis 2024“ wandert auf die neue Folie 4 und wird dort zu „Gemessen an echten Marktdaten von 2015 bis 2024“. Die Nachfrageseite liegt deutlich daneben; „geprüft“ klang nach bestanden. **An seine Stelle kommt ein Bild des Produkts**: der Screenshot des Leitstands aus `docs/pitch/`, dazu „Der Prototyp läuft“. Bis dahin beschrieb der Pitch die Lösung nur in Worten.
- **Neue Folie 4 „Warum wir“:** drei Punkte — jede Zahl aus der Berechnung, nie aus der KI; das Sprachmodell läuft auf eigener Infrastruktur, ohne externen KI-Dienst; gemessen an Marktdaten 2015–2024, offen, wo es trifft. Konkurrenz und Alleinstellung fehlten bis dahin ganz. Die übrigen Folien rücken um eins nach, es werden acht.
- **Folie 5 (Markt, bisher 4):** eine Zeile „Und das ist nur der Kern: Beratungen und SAF-Hersteller“ unter TAM, SAM und SOM — ohne Zahl, siehe Skript.
- **Folie 6 (bisher 5):** Titel „Fahrplan“ statt „Traktion“. Inhalt unverändert; es sind Ziele, und so heißt die Folie jetzt auch.
- **Folie 8 (Schluss, bisher 7):** die Bitte „Wir suchen Design-Partner aus Strategie und Netzwerkplanung bei Airlines und Flughäfen“ über dem Leitsatz.

## Das Bild auf Folie 3

Aufgenommen am 2026-09-28 aus dem laufenden Dashboard, Codestand dieses Branches. Der Lauf ist über den Assistenten eingerichtet: Szenario „Business as Usual“, 120 Ticks (10 Jahre), Rechenmodus „Nur Zahlen“, Zufallsstartwert 42; die Zeitleiste steht auf Tick 120. Wer das Bild neu aufnimmt, stellt denselben Lauf ein, damit Folie und Q&A dieselben Zahlen meinen.

- **„Nur Zahlen“, weil beim Aufnehmen kein Ollama lief.** Erkennbar ist das nur an der Zeile oben links. Das Bild zeigt das Rechnen, nicht das Erzählen — ein Bild der KI-Texte bräuchte einen Lauf mit Sprachmodell. Ein Lauf „Ohne Sprachmodell“ wäre die schlechtere Wahl gewesen: Er füllt die Agententexte mit Platzhaltern, und die gehören nicht auf eine Folie.
- **Die Kachel „CO₂-Abgabe 50 €/t“ bei Tick 120 ist richtig.** Unter „Business as Usual“ bleibt die Abgabe laut Szenariodatei bei 50 €; der Anstieg auf 200 € gehört zur Standard-Ausgangslage. Der Kostendruck steigt trotzdem auf 348 €, aus anderen Treibern. Beides ist eine naheliegende Rückfrage.
- **Die Zahlen auf dem Bild sind eine Momentaufnahme** des Modellstands vom 2026-09-28 und keine Aussage des Pitches; gesprochen wird über sie nicht.

## Offene Punkte

- Das Artefakt ist privat. Für andere braucht es Freigabe über sein Teilen-Menü.
- Die Teamfolie zeigt „Wirtschaftsinformatik im Master" als Hintergrund. Weitere Angaben zu Rolle und Erfahrung stehen dort nicht.
- Die Quelle „Aviation sector decarbonisation as a case of deep uncertainty" (ScienceDirect 2025) wurde nur über die Trefferbeschreibung geprüft, nicht im Volltext.
- Das Marktbericht-Zitat für den Cross-Check der Marktgröße hat keinen benannten Herausgeber und gilt nur als Größenordnung.
