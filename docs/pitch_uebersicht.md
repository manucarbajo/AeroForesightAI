# Pitch: Wo liegt was?

Diese Seite beantwortet, wenn im Chat jemand fragt „wo ist der Pitch, wie ändere ich ihn, woher kommt die Zahl?". Anlass ist der Pitch bei „Pitch, Please!" am 08.10.2026 im HdM Startup Center Stuttgart. Stand 2026-09-29, Umbau auf 5 Minuten begonnen.

## Die Dateien

| Was | Wo | Zweck |
| --- | --- | --- |
| Präsentation zum Vorführen | [`pitch.html`](../pitch.html) im Repo-Wurzelverzeichnis | Eine einzige Datei, per Doppelklick im Browser zu öffnen. Pfeiltasten oder Klick blättern, F schaltet Vollbild. Die Bilder sind eingebettet. Nur die Schriften (Plus Jakarta Sans, Inter) kommen aus dem Netz, ohne Internet greifen Systemschriften |
| Gesprochener Text | [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md) | Die **5-Minuten-Fassung** mit zwölf Folien (rund 4:35): je Folie, was darauf steht und was gesprochen wird, dazu Anhang für die Fragerunde, die Quellen jeder Zahl und die Herleitung von TAM, SAM und SOM |
| Bearbeitbare Fassung | Artefakt in claude.ai (Haikos Konto): <https://claude.ai/artifact/XRaiAGbnRJ4dj2VQ6qPBEw> | Hier wird der Pitch inhaltlich angepasst, und aus ihm entsteht `pitch.html`. Von dort lässt sich als PowerPoint oder PDF exportieren. Privat, bis es über das Teilen-Menü freigegeben ist |
| Frühere Fassung | Artefakt in claude.ai (Manus Konto): <https://claude.ai/artifact/V8DxvLSBtGVAmrFFYnaVnz> | Manus Deck, auf dem die bearbeitbare Fassung am 2026-09-28 aufsetzt. Es liegt in einer anderen Organisation, und Änderungen daran ließen sich aus Haikos Sitzung nicht speichern; deshalb die Kopie. **Wird nicht mehr gepflegt** (von Haiko entschieden am 2026-09-29): Änderungen gehören in die bearbeitbare Fassung darüber |
| Bilder für die Folien | [`docs/pitch/`](pitch/): `pitch_folie3_leitstand.png` (Leitstand, in der 5-Minuten-Fassung Folie 5), daneben `pitch_folie3_leitstand_voll.png`, dazu `pitch_folie4_verlaeufe.png` und `pitch_folie6_szenarien.png` | Der Leitstand nach einem Lauf, 3160 × 2052 bzw. 3840 × 2160 px (1920 × 1080 bei doppelter Pixeldichte). Die erste Fassung ist ohne die linke Spalte zugeschnitten und für die Folie gedacht; die zweite zeigt das ganze Fenster. Wie sie entstanden sind, steht unten |
| Diese Übersicht | `docs/pitch_uebersicht.md` | Wegweiser |

## Umbau auf 5 Minuten (seit 2026-09-29)

Anlass ist eine Vorab-Prüfung am 2026-09-29: Die Sprechzeit steigt von drei auf fünf Minuten, die Folien sollen stützen statt vorlesen, das Produkt soll in großen Bildern zu sehen sein, die Bitte soll sagen, wen wir suchen und warum man sich melden sollte, und der Markt soll als Einstiegsmarkt mit Ausbaupfad erscheinen. Die Entscheidungen dazu stehen im Skript.

| Schritt | Stand |
| --- | --- |
| Skript für 5 Minuten | **erledigt** (2026-09-29) |
| Drei ganzseitige Screenshots | **erledigt** (2026-09-29): `docs/pitch/pitch_folie4_verlaeufe.png` (Verläufe, CO₂-Steuer angehoben), `pitch_folie3_leitstand.png` für Folie 5, `pitch_folie6_szenarien.png` (die vier Rahmen im Vergleich, frisch gerechnet über 120 Ticks); je 1920 × 1080 bei doppelter Pixeldichte. **Ohne KI-Text** (entschieden am 2026-09-29): Die Texte mit `llama3.2` widersprachen der Rechnung, und ein Bild der Ansicht „Abfrage“ scheiterte am selben Grund — siehe Skript |
| Grafiken (Zeitstrahl, Kreislauf, Markttreppe, Vergleichstabelle, Bausteine) | offen |
| Deck umbauen: zwölf Folien plus Anhang, Stichworte statt Sätze, Notizen gleich Skript | offen |
| `pitch.html` neu erzeugen und jede Folie im Browser prüfen | offen |
| Probe mit Stoppuhr | offen (Manuel und Haiko) |

**Bis der Umbau durch ist, gehören Skript und Folien zu verschiedenen Fassungen**: das Skript zur neuen mit zwölf Folien, Deck und `pitch.html` zur alten mit acht.

## Was steht auf den acht Folien (3-Minuten-Fassung, Deck und `pitch.html`)

1. **Cover.** Der Aufhänger — ab 2026 keine kostenlosen CO₂-Zertifikate mehr, und wer die Kosten nur schätzt, plant im Blindflug — und der Satz „Wir liefern die Zukunft des europäischen Luftverkehrs. Berechnet, nicht geraten.“
2. **Problem.** Die Zukunft der Luftfahrt ist tief unsicher. Die SAF-Quote steigt von 2 % auf 6 % bis 2030, die Forschung fordert mehrere Szenarien.
3. **Lösung.** Drei Akteure (Passagiere, Fluggesellschaften, Regulierer) handeln, daraus werden Szenarien gerechnet, die KI erklärt sie. Darunter der Screenshot des Leitstands und „Der Prototyp läuft.“
4. **Warum wir.** Jede Zahl aus der Berechnung, nie aus der KI; das Sprachmodell auf eigener Infrastruktur; gemessen an Marktdaten 2015–2024, offen, wo das Modell trifft.
5. **Markt.** EU-ETS, RefuelEU, CORSIA, dazu TAM 33 Mio. €, SAM 9 Mio. €, SOM 570 Tsd. €, und dass Beratungen und SAF-Hersteller vor denselben Fragen stehen.
6. **Fahrplan.** 3 Design-Partner (Jahr 1), ≈300 Tsd. € (Jahr 2), ≈570 Tsd. € (Jahr 3). Das sind Ziele, keine Ist-Werte.
7. **Team.** Manuel Carbajo und Haiko Wiedenberg mit Foto und je einem LinkedIn-QR-Code.
8. **Schluss.** Die Bitte um Design-Partner aus Strategie und Netzwerkplanung, Name und Leitsatz.

Die Sprechernotizen jeder Folie tragen den Text aus dem Skript.

## Woher kommen die Zahlen?

Alles steht mit Quelle in [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md), Abschnitt „Herkunft der Fakten". Kurz:

- **Regulierung** (Gratiszertifikate, SAF-Quote): EASA und EU-Kommission.
- **TAM, SAM, SOM:** eigene Bottom-up-Rechnung aus ACI Europe (Flughäfen) und Airlines for Europe (Airlines), mit offen genannten Annahmen zu Kundenzahl und Jahresvertrag. Sie sind keine Marktstudie. Wer eine Annahme ändert, rechnet im Skript neu und passt Folie 5 und 6 an.
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

Seit dem 2026-09-29 tragen Folien und Skript denselben Stand; die Liste, was nachzuziehen war, ist abgearbeitet. **Eine Stelle weicht bewusst ab: das Bild auf Folie 3.** Die drei Karten darüber brauchen im Browser drei Zeilen und enden bei 671 px, das Deck gibt ihnen 588 px; an der Stelle aus dem Deck deckte der Screenshot die letzte Zeile der ersten Karte zu. In `pitch.html` steht er deshalb ab 694 px und 382 × 248 px groß, und „Der Prototyp läuft“ rückt nach. Ob das Artefakt selbst betroffen ist, ließ sich nicht prüfen — der Slides-Editor verkleinert übervolle Kästen womöglich. Wer `pitch.html` neu erzeugt, prüft Folie 3 und setzt die Korrektur wieder, oder er behebt sie im Artefakt.

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
