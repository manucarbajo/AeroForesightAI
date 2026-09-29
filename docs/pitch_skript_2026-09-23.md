# Pitch-Skript: AeroForesight AI

Gesprochener Text für den Pitch bei „Pitch, Please!" (HdM Startup Center Stuttgart, 08.10.2026). Er folgt Folie für Folie der Präsentation, siehe [pitch_uebersicht.md](pitch_uebersicht.md). Stand 2026-09-29; Folien, Sprechernotizen und dieser Text tragen denselben Stand.

Länge: rund 275 Wörter, rund 2:45 Minuten bei ruhigem Tempo (etwa 100 Wörter pro Minute); der Rest der drei Minuten ist Puffer für Pausen und Folienwechsel. Wer ergänzt, streicht an anderer Stelle — bis zum 2026-09-28 waren es 229 Wörter, und der Zuwachs ist Folie 4, der Produktbeleg auf Folie 3 und die Bitte am Schluss. Kurze Sätze, keine Aufzählungen.

---

## Folie 1: Cover

Ab 2026 bekommen Airlines in Europa keine kostenlosen CO₂-Zertifikate mehr. Wie teuer das wird, hängt am CO₂-Preis, an der SAF-Quote und an der Bahn, alles zugleich. Wer das nur schätzt, plant mit Millionen im Blindflug.

Wir liefern die Zukunft des europäischen Luftverkehrs. Berechnet, nicht geraten.

## Folie 2: Problem

Die Zukunft der Luftfahrt ist tief unsicher. Die SAF-Quote steigt von 2 Prozent heute auf 6 Prozent bis 2030. Und die Forschung sagt: Eine einzelne Prognose reicht nicht. Es braucht mehrere Szenarien.

## Folie 3: Lösung

Genau die liefern wir. In unserem Modell handeln drei Akteure: Passagiere, Fluggesellschaften und Regulierer. Sie reagieren aufeinander, so wie im echten Markt. Daraus rechnen wir verschiedene Zukünfte vor, und die KI erklärt jedes Szenario verständlich. Das ist kein Entwurf: Der Prototyp läuft, mit Dashboard und Szenario-Vergleich.

## Folie 4: Warum wir

Was uns unterscheidet: Jede Zahl kommt aus der Berechnung, nie aus der KI. Die KI erzählt, sie rechnet nicht. Das Sprachmodell läuft auf eigener Infrastruktur, ohne externen KI-Dienst. Und wir messen das Modell an echten Marktdaten von 2015 bis 2024 und zeigen offen, wo es trifft und wo noch nicht.

## Folie 5: Markt

Unsere Kunden sind rund 80 Airlines, 120 Flughäfen und 35 Regulierer in Europa. Das ist ein Markt von 9 Millionen Euro in Europa und 33 Millionen weltweit. Und das ist nur der Kern: Beratungen und SAF-Hersteller stehen vor denselben Fragen.

## Folie 6: Fahrplan

Unser Ziel: drei Design-Partner im ersten Jahr, acht Kunden im zweiten, fünfzehn im dritten. Das sind rund 570 Tausend Euro Jahresumsatz.

## Folie 7: Team

Wir sind Manuel und Haiko, beide Wirtschaftsinformatik im Master. Unsere Profile findet ihr per QR-Code.

## Folie 8: Schluss

Dafür suchen wir jetzt unsere ersten Design-Partner: Menschen aus Strategie und Netzwerkplanung bei Airlines und Flughäfen. Wenn ihr jemanden kennt, sprecht uns an. AeroForesight AI. Berechnet, nicht geraten.

---

## Herkunft der Fakten

Jede Zahl der Folien ist hier belegt oder als eigene Rechnung ausgewiesen.

| Aussage | Beleg |
| --- | --- |
| Ab 2026 keine kostenlosen Emissionszertifikate für Airlines | [EASA, EU-Emissionshandel](https://www.easa.europa.eu/en/domains/environment/eaer/market-based-measures/eu-emissions-trading-system): Gratiszuteilung 25 % (2024), 50 % (2025), 0 % ab 2026 (Ausnahme: 20 Mio. Zertifikate als SAF-Anreiz) |
| SAF-Quote 2 % ab 2025, 6 % bis 2030, 70 % bis 2050 | [EASA, Sustainable Aviation Fuels](https://www.easa.europa.eu/en/domains/environment/eaer/sustainable-aviation-fuels) (ReFuelEU Aviation) |
| Forschung fordert mehrere Szenarien statt einer Prognose | ScienceDirect 2025, [„Aviation sector decarbonisation as a case of deep uncertainty"](https://www.sciencedirect.com/science/article/pii/S2214629625002397). Nur über die Trefferbeschreibung geprüft, nicht im Volltext gelesen |
| Drei Akteure handeln gegeneinander | `README.md`, `CLAUDE.md`, Paket `src/agents/` |
| Alle Zahlen aus der Berechnung, die KI erklärt nur | Invariante 1 in `CLAUDE.md` |
| Gemessen an Marktdaten 2015 bis 2024, offen, wo es trifft und wo nicht | `docs/backtest_vorlauf.md`, Paket `src/backtest/`. Ein Vergleich, keine Eichung. Stand 2026-09-28: Die Preisseite liegt 2016–2019 im Mittel 1,15 Indexpunkte neben der Zielreihe, die Nachfrageseite 25,04 (über alle bewerteten Jahre 9,82 bzw. 36,44). Deshalb „gemessen“ statt „geprüft“: Das Wort klang nach bestanden, und auf der Nachfrageseite ist es das nicht. Die Zahlen gehören in die Antwort auf eine Rückfrage, nicht in den Pitch — die Datei wird mit jedem Lauf überschrieben |
| Wie teuer der Ausstieg aus den Gratiszertifikaten wird, hängt an mehreren Größen zugleich | Folgt aus den Zeilen zu EU-ETS und SAF-Quote. „Wer das nur schätzt, plant im Blindflug“ ist bewusst ein Bedingungssatz: Dass Airlines heute schätzen, ist nicht belegt und wird nicht behauptet (derselbe Grund, aus dem der Satz über Excel gestrichen wurde) |
| Der Prototyp läuft, mit Dashboard und Szenario-Vergleich | Dash-App unter `dashboard/web/`, Start laut `README.md`; der Szenario-Vergleich ist der zweite Weg im Einstieg des Bereichs „Einrichten“. Ein Prototyp, kein Produkt im Kundeneinsatz |
| Das Sprachmodell läuft auf eigener Infrastruktur, ohne externen KI-Dienst | Ein einziger LLM-Client für ein lokal laufendes Ollama (`src/llm/llm_client.py`), Deployment-Ziel in `CLAUDE.md`. Bewusst nicht gesagt: „auf unseren Servern beim Kunden“ — das Deployment ist laut `CLAUDE.md` noch nicht produktionsscharf |
| Die KI erzählt, sie rechnet nicht | Invariante 1 in `CLAUDE.md`, wie die Zeile darüber |
| Beratungen und SAF-Hersteller stehen vor denselben Fragen | Eigene Einschätzung, nicht beziffert und **nicht** in TAM, SAM oder SOM eingerechnet. Sie sagt nur, dass der Kern nicht die Grenze ist. Wer nach einer Zahl fragt, bekommt keine |
| Rund 80 Airlines, 120 Flughäfen, 35 Regulierer, 9 und 33 Mio. €, 570 Tsd. € | Eigene Rechnung, siehe unten |
| Wir sind Manuel und Haiko, Wirtschaftsinformatik im Master | Angabe aus der Teamfolie im Artefakt |

Nicht belegt und bewusst nicht behauptet: Pilotkunden, Umsatz, Investitionssumme. Die Fahrplanfolie nennt nur Ziele, keine Ist-Werte — sie hieß bis zum 2026-09-28 „Traktion“, und so benannt versprach sie Ist-Werte, die sie nicht zeigte. Die Bitte am Schluss ist bewusst keine Geldsumme, sondern Kontakte zu künftigen Design-Partnern; sie passt damit zum Ziel auf Folie 6.

**Entfallen am 2026-09-28:** der frühere Aufhänger „Die EU senkt heute das CO₂-Preislimit“. Er war die einzige Aussage ohne Zeile in dieser Tabelle, band sich mit „heute“ an einen Tag, und eine gesenkte Preisobergrenze senkte die Kosten eher, statt sie zu erhöhen. Ersetzt durch die belegte Tatsache aus Folie 2, die dort deshalb der SAF-Quote Platz macht.

### Herleitung TAM/SAM/SOM (2026-09-23, eigene Rechnung, bottom-up)

Keine der drei Zahlen stammt aus einer Marktstudie über AeroForesight selbst, es gibt keine. Sie sind aus öffentlich belegten Kennzahlen der Branche plus offen ausgewiesenen Annahmen zu Kundenzahl und Jahresvertragswert (ACV) gerechnet. Wer die Annahmen für falsch hält, kann sie ersetzen, die Rechnung selbst steht offen.

**Kernzielgruppe (Annahme, begründet):**

| Segment | Anzahl | Beleg für die Grundgesamtheit | ACV-Annahme |
| --- | --- | --- | --- |
| Große Fluggesellschaften (Strategie/Netzwerkplanung) | 80 | Airlines for Europe (A4E): 16 Airline-Gruppen tragen >80 % des europ. Luftverkehrs (771 Mio. Passagiere 2024). 80 ist eine großzügigere Fassung inkl. weiterer Netzwerk-/Charter-Gruppen unterhalb der A4E-Schwelle | 45.000 €/Jahr |
| Strategisch relevante Flughäfen (Top-Tier) | 120 | ACI Europe: 600+ Flughäfen in 55 Ländern, >95 % des europ. Luftverkehrs. 120 als Top-Tier-Schätzung (Verkehrsvolumen rechtfertigt strategische Planungssoftware) | 30.000 €/Jahr |
| Regulierer/Ministerien (EASA, nationale Behörden, DG MOVE) | 35 | EASA-Mitgliedstaaten (EU-27 + EFTA) + UK CAA + EU-Kommission, überschlägig | 50.000 €/Jahr |

**SAM (Europa/EWR, bottom-up):** 80×45.000 + 120×30.000 + 35×50.000 = 3.600.000 + 3.600.000 + 1.750.000 = **8.950.000 €/Jahr** (gerundet: ~9 Mio. €).

**TAM (global):** SAM ÷ Europas Anteil am weltweiten Luftverkehr (~27 %, EUROCONTROL/IATA-Größenordnung) = 8.950.000 ÷ 0,27 ≈ **33.150.000 €/Jahr** (gerundet: ~33 Mio. €). Gleiche Käufertypen, global statt nur Europa.

**Cross-Check (top-down, unabhängige Quelle):** Der globale Markt für „Aviation Analysis Software" wird mit 1,65 Mrd. USD (2025, ≈ 1,52 Mrd. €) beziffert, wachsend auf 3,25 Mrd. USD bis 2034 (CAGR 8,5 %). Unser TAM entspricht darin einem Nischenanteil von ≈ 2,2 %. Das ist plausibel, weil diese Kategorie überwiegend operative Analytics (Flugbetrieb, Wartung/MRO, Crew-Planung) abdeckt und strategische Szenarioplanung nur ein kleiner Teilbereich ist.

**SOM (Jahr 3, eigenes Ziel):** 15 zahlende Kunden × Ø 38.085 €/Jahr (SAM-gewichteter Mittelwert der drei Segmente) ≈ **571.000 €/Jahr** (gerundet: ~570.000 €). Das sind 6,4 % des SAM, ein für ein kleines Team in drei Jahren übliches Ziel für ein neues B2B-Nischensegment. Der Zwischenschritt Jahr 2 (8 Kunden, ≈300 Tsd. €) ist derselbe Mittelwert mal acht, Jahr 1 (3 Design-Partner) ist gesetzt.

Quellen: [ACI Europe](https://www.aci-europe.org/) („600+ airports in 55 countries", „over 95% of commercial air traffic"); [Airlines for Europe](https://a4e.eu/) („16 airline group members", „over 80% of European air traffic", „771 million passengers in 2024"); Marktbericht „Aviation Analysis Software Market" (1,65 Mrd. USD 2025 → 3,25 Mrd. USD 2034, CAGR 8,5 %), Websuche 2026-09-23, Herausgeber nicht im Repository hinterlegt, deshalb nur als Größenordnung zu lesen.
