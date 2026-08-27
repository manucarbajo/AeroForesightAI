Jeder Lauf legt ein eigenes Verzeichnis unter `outputs/` an, benannt nach seiner
Run-ID. Läufe eines Szenario-Vergleichs liegen unter `outputs/sweeps/`.

Alle Dateien sind im Tab **Dateien** einsehbar und herunterladbar.

## Ergebnisse zum Lesen

| Datei | Inhalt |
|---|---|
| `run_scenario.md` / `.json` | Das Szenario-Tripleset — Hauptergebnis eines Laufs, Grundlage des Tabs «Szenario» |
| `final_narrative.md` | Der Tick-für-Tick-Bericht mit Kennzahlen und Akteursbeiträgen |
| `scenarios.md` / `.json` | Die CIB-Kandidaten mit ihren Konsistenzwerten |
| `protocol.md` / `.json` | Das Gesprächsprotokoll der Akteure |

## Zahlen zum Nachrechnen

| Datei | Inhalt |
|---|---|
| `tick_mechanics.json` | Die maßgeblichen Kennzahlen je Runde: Preis, Buchungsrate, Kostendruck, Marge |
| `price_history.json` | Preisverlauf mit Nachfrageniveau und Buchungsrate |
| `event_log.json` | Alle Ereignisse, einschließlich der als `[delta:…]` markierten Python-Änderungen |
| `round_history.json` | Der Zustand je Runde |
| `run_metadata.json` | Ticks, Modell, Zeitstempel, ob das Marktmodell aktiv war — und ob der Lauf beeinträchtigt war |
| `llm_incidents.json` | Nur vorhanden, wenn Aufrufe an das Sprachmodell ins Leere gingen: welcher Tick, welcher Aufrufer, welcher Fehler |
| `segment_analysis.json` | Auswertung nach Segmenten |
| `cib_matrix.json` | Die im Lauf verwendete Einflussmatrix |

Drei Felder in `run_metadata.json` betreffen die Verlässlichkeit eines Laufs:
`degraded` sagt, ob mindestens ein Aufruf an das Sprachmodell unbeantwortet
blieb, `llm_incident_count` zählt sie, und `llm_degraded_ticks` nennt die
betroffenen Runden. Die drei stehen **immer** in der Datei, auch bei einem
sauberen Lauf mit `false` und `0` — fehlen sie ganz, stammt der Lauf aus der
Zeit vor dieser Aufzeichnung. `llm_incidents.json` entsteht dagegen nur, wenn es
etwas zu berichten gibt.

## Zeitreihen

Unter `timeseries/` liegen vier Tabellen im CSV-Format, geeignet zur
Weiterverarbeitung in einer Tabellenkalkulation.

| Datei | Inhalt |
|---|---|
| `properties.csv` | Alle Systemgrößen je Runde |
| `factors.csv` | Die Zustände von F1 bis F7 je Runde |
| `population.csv` | Buchungsraten je Profil-Segment |
| `age_property.csv` | Buchungsraten je Altersgruppe |

## Personen und Zwischenstände

`individuals_history.csv` enthält jede simulierte Person in jeder Runde, mit
Merkmalen und Buchungsentscheidung. Das ist die Grundlage des Tabs «Animation»
und die größte Datei eines Laufs. `population.csv` im Hauptverzeichnis enthält
die gezogene Ausgangsbevölkerung.

Unter `checkpoints/` liegen Zwischenstände, sofern das unter **Technik**
eingeschaltet war. Sie werden gebraucht, um einen Lauf fortzusetzen und um im Tab
**Abfrage** einzelne Runden im Detail nachzuschlagen. Ohne sie funktioniert die
Abfrage weiterhin, aber gröber.

## Bilddateien

Unter `figures/` liegen sechs Diagramme im PNG-Format plus eine
`manifest.json` mit ihren Titeln. Sie entstehen, wenn beim Start
«Auswertungsgrafiken erzeugen» aktiv war, und lassen sich im Tab **Figures**
unter «PNG-Export» jederzeit neu erzeugen.

| Datei | Inhalt |
|---|---|
| `price_vs_booking.png` | Ticketpreis gegen Buchungsrate |
| `policy_shock_co2_booking.png` | Wirkung eines CO₂-Schocks |
| `system_dynamics.png` | Zusammenspiel der Systemgrößen |
| `factor_states.png` | Faktor-Trajektorien |
| `age_segment_booking.png` | Buchungen nach Alter und Segment |
| `population_distribution.png` | Verteilung der Bevölkerungsmerkmale |
