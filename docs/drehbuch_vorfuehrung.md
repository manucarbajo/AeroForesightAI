# Drehbuch: Vorführung am Stand (Pitch, Please!, 08.10.2026)

Paket [P8-V8](plan_vorfuehrbereitschaft_2026-09-29.md). Stand 2026-10-01.

**Wann:** nicht im Pitch. Der dauert fünf Minuten und ist nur die Präsentation ([Skript](pitch_skript_2026-09-23.md)). Gezeigt wird danach **am eigenen Stand, auf Nachfrage**: drei Minuten, die die Folien 4 bis 6 fortsetzen. Wer selbst klicken will, darf das; die Regeln unten sagen, wohin besser nicht.

**Was:** Alles mit Sprachmodell ist **vorgerechnet** (der Vorführbestand). **Live** gerechnet wird nur ohne Sprachmodell: Das dauert Sekunden und ergibt dieselben Zahlen wie der vorgerechnete Lauf.

## Vorher, auf dem Vorführ-Laptop

1. `python -m dashboard.vorfuehrbestand --nur-pruefen` — jeder Lauf «ok». Sonst den durchgefallenen mit `--nur KENNUNG` neu rechnen.
2. Ollama läuft, `llama3.2` ist geladen — nur für die Abfrage (Schritt 5) nötig. Die Frage aus Schritt 5 einmal am Pitch-Fall stellen und die Antwort lesen: Sie ist dort noch nicht geprüft.
3. `python -m dashboard.web.app --port 8511`, im Browser **`http://localhost:8511/app/lauf`** — nicht `/`: Die Landingpage zeigt noch Platzhalter für Impressum und Datenschutz.
4. Helles Design, Browser-Zoom so, dass die Kennzahlen rechts vom Stand aus lesbar sind (bei 1920 × 1080 eher 125 %).
5. Kopfzeile «Lauf wählen» → Suche «Vorführung» → **«Vorführung: CO₂-Abgabe steigt auf 200 €»**. Zeitleiste auf Tick 23.
6. Daneben bereit: `pitch.pdf` (falls das Dashboard nicht will) und die Aufnahme aus V7.

## Der Ablauf (rund drei Minuten)

| # | Klick | Was man sagt |
| --- | --- | --- |
| 1 | Leitstand, Pitch-Fall auf **Tick 23**, dann **«Ein Tick vor»** | «Das ist die Frage von der Folie: Business as Usual, aber die CO₂-Abgabe springt im 24. Monat von 50 auf 200 €. Jeder Punkt ist ein Reisender, der bucht oder nicht. In diesem einen Monat fällt die Buchungsrate von 23,3 auf 12,0 %.» |
| 2 | «Ans Ende» (Tick 40) | «Nach gut drei Jahren: 201 € je Ticket, 8,2 % Buchungen. Die Fluggesellschaft hält ihren Aufschlag und gibt die Kosten weiter.» |
| 3 | Lauf wählen → **«Vorführung: Business as Usual, Aufschlag halten»** → «Ans Ende» | «Zum Vergleich dieselbe Welt ohne Erhöhung: 194 € und 15,9 %. Die Abgabe macht das Ticket rund 7 € teurer und halbiert die Buchungen.» |
| 4 | **Ergebnisse → Szenario** (Pitch-Fall) | «Die KI fasst den Lauf in Worte. Das Produkt prüft jeden Satz gegen die Rechnung.» **Steht unter dem Text ein Hinweis «Widerspricht der Rechnung»** (im Bestand vom 2026-09-30: «Nachfrage steigt», gerechnet sinkt sie): «Hier hat sich die KI geirrt — und das Produkt markiert es, statt es durchzulassen. Deshalb kommt keine Zahl von der KI.» **Steht keiner:** «Kein Satz widerspricht der Rechnung; sonst stünde hier eine Markierung.» Welcher Fall gilt, nach dem Neurechnen des Bestands auf dem Laptop einmal ansehen. |
| 5 | **Abfrage**, eine Frage aus dem Prüfsatz, etwa «Wie hat sich die CO₂-Abgabe über den Lauf entwickelt?» | «Man kann den Lauf auch fragen. Unter jeder Antwort steht, welche Zahlen geprüft wurden.» — nur, wenn die Antworten auf dem Laptop in wenigen Sekunden kommen (V1). |
| 6 | Lauf wählen → **«Transformationskonflikt»** (Szenario-Vergleich) → **Diagramme → 4 · Die Szenarien nebeneinander** | «Das Bild von Folie 6: vier Rahmenszenarien über zehn Jahre. Nur im Transformationskonflikt bricht die Nachfrage weg, und der Preis steigt über 400 €.» |

**Live, wenn jemand selbst etwas einstellen will** (rund eine Minute): Einrichten → «Neuen Lauf einrichten» → «Business as Usual» → «Verläufe»: CO₂-Steuer, «Stützpunkt hinzufügen», ab Tick 24, «springt auf den Wert», 200; Preisstrategie «Aufschlag halten» → «Wie weit reicht der Lauf?»: 40 → «Womit wird gerechnet?»: **«Ohne Sprachmodell»** → «Prüfen & Starten» → «Lauf starten». Nach rund fünf Sekunden steht der Lauf da, mit denselben Zahlen wie der vorgerechnete (am 2026-10-01 nachgerechnet: Tick 23, 24 und 40 auf den Cent gleich). Satz dazu: «Die Zahlen sind deterministisch — gleiche Annahmen, gleiches Ergebnis.» Die Gesprächspartnerin kann statt 200 € auch einen eigenen Wert nehmen.

## Regeln

1. **Live nur «Ohne Sprachmodell»** (oder «Nur Zahlen», gleich schnell). «Mit Sprachmodell» braucht 40 Ticks lang rund 10 s je Tick (Entwicklungsrechner; auf dem Laptop eher mehr). «Ohne Sprachmodell» ist die sichere Wahl, weil es Ollama auch dann nicht braucht, wenn auf dem Laptop etwas klemmt.
2. Keinen Szenario-Vergleich live starten (rund zwei Minuten mit Sprachmodell), keinen Lauf abbrechen (eine Minute ohne Rückmeldung, Befund 10).
3. Im Bereich «Modell» nichts speichern — das ändert die Auslieferung (Befund 14).
4. «Animation» darf jetzt offen werden: Die Ansicht ist sofort da, jedes Diagramm rechnet auf «Diagramm zeigen» in ein bis zwei Sekunden (Pitch-Fall), und die Legende ist deutsch (V11, seit 2026-10-01). Das erste Diagramm zeigt die Wolke der Reisenden über die Ticks — passend zu Schritt 1.
5. Den Pitch-Fall gegen seine Referenz «Aufschlag halten» zeigen, nicht gegen «Vorführung: Business as Usual» — die rechnet mit «Plätze füllen», und dort sinkt der Ticketpreis nach dem Sprung (Befund 8).

## Wenn jemand fragt

- **Wie genau ist das?** Gemessen an Marktdaten 2015–2024, nicht daran geeicht. Die Preisseite liegt 2016–2019 im Mittel 1,15 Indexpunkte neben der Wirklichkeit, die Nachfrageseite 25 — dem Modell fehlt ein Treiber, der die Nachfrage wachsen lässt, und wir sagen das (Anhang A1, Zahlen aus `docs/backtest_vorlauf.md`).
- **Woher kommen die Verhaltensannahmen?** Die Form des Nutzenmodells ist aus der Literatur belegt; die einzelnen Zahlen sind gesetzt, nicht geschätzt, und jede trägt ihre Herkunft.
- **Was macht die KI genau?** Sie erzählt und rechnet nicht. Drei KI-Akteure bringen Ereignisse und Vorschläge ein, nur in den Grenzen ihrer Rolle; die Zahlen kommen aus Python. Texte werden gegen die Rechnung geprüft, Widersprüche markiert. Läuft lokal mit `llama3.2`, keine Daten an einen externen Dienst (Anhang A3).
- **Warum 40 Ticks?** Ein Tick ist ein Monat; 40 sind gut drei Jahre. Die Rahmenszenarien laufen 120 Ticks, also zehn Jahre.
- **Warum fällt die Buchungsrate schon ohne Erhöhung?** Unter «Aufschlag halten» reicht die Fluggesellschaft den wachsenden Kostendruck voll weiter; der Preis steigt in 40 Ticks von 140 auf 194 €.
- **Kann ich das bei uns ausprobieren?** Genau das ist die Bitte von Folie 12: ein kostenloser Pilot zu Ihrer eigenen Frage.

## Wenn etwas schiefgeht

- **Dashboard startet nicht oder hängt:** `pitch.pdf` zeigen, dann die Aufnahme.
- **Abfrage antwortet nicht:** Ollama läuft nicht oder ist langsam — Schritt 5 auslassen, er ist der einzige, der das Sprachmodell live braucht.
- **Falscher Lauf gewählt:** Lauf wählen → Suche «Vorführung».
- **Seite reagiert nicht:** neu laden. Der Bestand liegt auf der Platte; danach den Lauf wieder wählen.

## Offen

- Zweimal proben, mit Stoppuhr, auf dem Laptop (Manuel und Haiko).
- V1 auf dem Laptop: entscheidet, ob Schritt 5 drin bleibt.
- V7: Aufnahme als Rückfall.
