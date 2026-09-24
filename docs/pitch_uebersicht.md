# Pitch: Wo liegt was?

Diese Seite beantwortet, wenn im Chat jemand fragt „wo ist der Pitch, wie ändere ich ihn, woher kommt die Zahl?". Anlass ist der Pitch bei „Pitch, Please!" am 08.10.2026 im HdM Startup Center Stuttgart. Stand 2026-09-24.

## Die Dateien

| Was | Wo | Zweck |
| --- | --- | --- |
| Präsentation zum Vorführen | [`pitch.html`](../pitch.html) im Repo-Wurzelverzeichnis | Eine einzige Datei, per Doppelklick im Browser zu öffnen. Pfeiltasten oder Klick blättern, F schaltet Vollbild. Die Bilder sind eingebettet. Nur die Schriften (Plus Jakarta Sans, Inter) kommen aus dem Netz, ohne Internet greifen Systemschriften |
| Gesprochener Text | [`docs/pitch_skript_2026-09-23.md`](pitch_skript_2026-09-23.md) | Der Text je Folie, rund 2:15 Minuten, dazu die Quellen jeder Zahl und die Herleitung von TAM, SAM und SOM |
| Bearbeitbare Fassung | Artefakt in claude.ai: <https://claude.ai/artifact/V8DxvLSBtGVAmrFFYnaVnz> | Hier wird der Pitch inhaltlich angepasst. Von dort lässt sich als PowerPoint oder PDF exportieren. Das Artefakt ist privat, nur wer den Link geöffnet und Zugriff bekommen hat, sieht es |
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
- **Keine Pilotkunden, kein Umsatz, keine Investitionssumme.** Nichts davon ist belegt. Die frühere Ask-Folie ist entfallen.

## So ändert man etwas

- **Text oder Layout ändern:** im Artefakt bearbeiten (Link oben).
- **`pitch.html` neu erzeugen:** im Chat sagen „erzeuge pitch.html aus dem Artefakt neu". Dabei wird der aktuelle Artefakt-Stand gelesen und jede Folie in die Datei übernommen. Der animierte Hintergrund wird als eingebettetes Fenster eingesetzt, die Bilder werden als Base64 eingebettet, die Sprechernotizen entfallen.
- **PowerPoint:** im Artefakt über das Teilen-Menü als .pptx exportieren. Der animierte Hintergrund wird dabei zu einem Standbild.
- **Skript angleichen:** Nach jeder Textänderung an den Folien gehört das Skript mit, sonst laufen Folie und gesprochener Text auseinander.

## Offene Punkte

- Das Artefakt ist privat. Für andere braucht es Freigabe über sein Teilen-Menü.
- Die Teamfolie zeigt „Wirtschaftsinformatik im Master" als Hintergrund. Weitere Angaben zu Rolle und Erfahrung stehen dort nicht.
- Die Quelle „Aviation sector decarbonisation as a case of deep uncertainty" (ScienceDirect 2025) wurde nur über die Trefferbeschreibung geprüft, nicht im Volltext.
- Das Marktbericht-Zitat für den Cross-Check der Marktgröße hat keinen benannten Herausgeber und gilt nur als Größenordnung.
