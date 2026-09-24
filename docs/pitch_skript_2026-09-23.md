# Pitch-Skript: AeroForesight AI

Gesprochener Text für den Pitch bei „Pitch, Please!" (HdM Startup Center Stuttgart, 08.10.2026). Er folgt Folie für Folie der Präsentation, siehe [pitch_uebersicht.md](pitch_uebersicht.md). Stand 2026-09-24.

Länge: rund 2:15 Minuten bei ruhigem Tempo (etwa 100 Wörter pro Minute), Puffer für Pausen und Folienwechsel. Kurze Sätze, keine Aufzählungen.

---

## Folie 1: Cover

Die EU senkt heute das CO₂-Preislimit. Morgen weiß keine Airline, was das für ihre Marge heißt. Sie raten, und es geht um Millionen.

Wir liefern die Zukunft des europäischen Luftverkehrs. Berechnet, nicht geraten.

## Folie 2: Problem

Die Zukunft der Luftfahrt ist tief unsicher. CO₂-Preise, SAF-Quoten und die Bahn wirken gleichzeitig und verstärken sich. Ab 2026 gibt es keine kostenlosen Emissionszertifikate mehr für Airlines. Und die Forschung sagt: Eine einzelne Prognose reicht nicht. Es braucht mehrere Szenarien.

## Folie 3: Lösung

Genau die liefern wir. In unserem Modell handeln drei Akteure: Passagiere, Fluggesellschaften und Regulierer. Sie reagieren aufeinander, so wie im echten Markt. Daraus rechnen wir verschiedene Zukünfte vor. Jede Zahl kommt aus der Berechnung. Die KI erklärt danach jedes Szenario, verständlich und nah an der Realität. Geprüft haben wir das an echten Marktdaten von 2015 bis 2024.

## Folie 4: Markt

Alles greift gleichzeitig: Emissionshandel, SAF-Quote und CORSIA. Unsere Kunden sind rund 80 Airlines, 120 Flughäfen und 35 Regulierer in Europa. Das ist ein Markt von 9 Millionen Euro in Europa und 33 Millionen weltweit. Davon wollen wir in drei Jahren 570 Tausend Euro erreichen.

## Folie 5: Traktion

Unser Ziel: drei Design-Partner im ersten Jahr, acht Kunden im zweiten, fünfzehn im dritten. Das sind rund 570 Tausend Euro Jahresumsatz.

## Folie 6: Team

Wir sind Manuel und Haiko, beide Wirtschaftsinformatik im Master. Unsere LinkedIn-Profile findet ihr als QR-Code auf der Folie.

## Folie 7: Schluss

AeroForesight AI. Wir liefern die Zukunft des Luftverkehrs. Berechnet, nicht geraten. Sprecht uns gern an.

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
| Geprüft an Marktdaten 2015 bis 2024 | `docs/backtest_vorlauf.md`, Paket `src/backtest/`. Ein Vergleich, keine Eichung, und er schneidet nicht überall gut ab |
| Rund 80 Airlines, 120 Flughäfen, 35 Regulierer, 9 und 33 Mio. €, 570 Tsd. € | Eigene Rechnung, siehe unten |
| Wir sind Manuel und Haiko, Wirtschaftsinformatik im Master | Angabe aus der Teamfolie im Artefakt |

Nicht belegt und bewusst nicht behauptet: Pilotkunden, Umsatz, Investitionssumme. Die Traktionsfolie nennt nur Ziele, keine Ist-Werte.

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
