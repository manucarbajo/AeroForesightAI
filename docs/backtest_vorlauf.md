# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 97.76 | 97.42 | +0.34 |  |
| 2017 | 105.57 | 102.64 | +2.93 |  |
| 2018 | 105.96 | 104.95 | +1.01 |  |
| 2019 | 107.33 | 107.00 | +0.33 |  |
| 2020 | 130.19 | 102.48 | +27.71 | ungewertet |
| 2021 | 157.16 | 105.98 | +51.18 | ungewertet |
| 2022 | 141.02 | 131.93 | +9.09 |  |
| 2023 | 124.51 | 144.57 | -20.06 |  |
| 2024 | 113.28 | 148.25 | -34.97 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 9.82 |
| Größter Abstand | 34.97 (2024) |
| davon 2016–2019 | 1.15 |
| davon 2022–2024 | 21.37 |
| Richtung der Jahresveränderung getroffen | 5/7 |
| Saisonschwankung Modell / Ziel | 17.9 / 39.8 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 40 Indexpunkte im Jahr, das Modell um 18. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Nachfrage: `booking_rate` gegen `fluggaeste`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 94.99 | 106.34 | -11.35 |  |
| 2017 | 89.13 | 114.54 | -25.41 |  |
| 2018 | 92.06 | 121.54 | -29.48 |  |
| 2019 | 92.37 | 126.28 | -33.91 |  |
| 2020 | 48.47 | 33.76 | +14.71 | ungewertet |
| 2021 | 30.84 | 45.60 | -14.76 | ungewertet |
| 2022 | 47.74 | 99.63 | -51.89 |  |
| 2023 | 61.47 | 118.70 | -57.23 |  |
| 2024 | 82.57 | 128.38 | -45.81 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 36.44 |
| Größter Abstand | 57.22 (2023) |
| davon 2016–2019 | 25.04 |
| davon 2022–2024 | 51.64 |
| Richtung der Jahresveränderung getroffen | 5/7 |
| Saisonschwankung Modell / Ziel | 30.5 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 31. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Gegenprobe: was hängt am Kapazitätseingang?

Der Eingang `kapazitaet_index` (Eurostat `avia_paoc`, `CAF_PAS` — Flüge) und die Nachfrage-Zielreihe (`avia_paoc`, `PAS_CRD` — Passagiere) stammen aus **derselben Tabelle** und hängen mechanisch zusammen. Unten steht deshalb derselbe Lauf ohne die Kapazitätsreihe, mit sonst unverändertem Verfahren.

| Seite | Kennzahl | mit Kapazität | ohne |
| --- | --- | ---: | ---: |
| Preis | Abstand gesamt | 9.82 | 16.56 |
| Preis | davon 2016–2019 | 1.15 | 1.96 |
| Preis | davon 2022–2024 | 21.37 | 36.03 |
| Preis | Richtung getroffen | 5/7 | 5/7 |
| Nachfrage | Abstand gesamt | 36.44 | 28.15 |
| Nachfrage | davon 2016–2019 | 25.04 | 26.13 |
| Nachfrage | davon 2022–2024 | 51.64 | 30.84 |
| Nachfrage | Richtung getroffen | 5/7 | 3/7 |

**Wie das zu lesen ist:** Würde der Eingang die Übereinstimmung nur widerhallen, müsste der **Abstand** mit ihm kleiner sein. Auf der Nachfrageseite ist er größer — das Modell folgt den *Flügen* und verfehlt damit die *Passagiere*, die stärker gewachsen sind. Was er beiträgt, zeigt sich an der **Richtung** und an der **Preisseite**, deren Zielreihe aus einer ganz anderen Quelle stammt (Eurostat `prc_hicp_midx`) und deshalb nicht zirkulär sein kann.

Der Vorbehalt bleibt trotzdem stehen: Eine Kapazitätsreihe, die Sitze zählt statt Flüge, gibt es bei Eurostat auf dieser Ebene nicht. Das ist eine **Datenfrage**, keine Parameterfrage.

## Datenquellen

| Reihe | Monate | Abgerufen | Herkunft |
| --- | ---: | --- | --- |
| `eua_auktionspreis.csv` | 119 | 2026-09-01 | EEX, Emission Spot Primary Market Auction Report. |
| `brent_rohoel.csv` | 120 | 2026-09-01 | Europe Brent Spot Price FOB, Monatsmittel. |
| `hicp_flugreisen.csv` | 120 | 2026-09-01 | Eurostat `prc_hicp_midx`, COICOP `CP0733` (Passenger transport by air), EU-27, Index 2015 = 100. |
| `bip_real.csv` | 120 | 2026-09-01 | Eurostat `namq_10_gdp`, reales BIP der EU-27 (`B1GQ`, verkettete Volumen zu Preisen von 2015, saison- und kalenderbereinigt), **vierteljährlich** und linear auf Monate interpoliert. |
| `fluege.csv` | 120 | 2026-09-01 | Eurostat `avia_paoc`, gewerbliche Passagierfluege (`CAF_PAS`), EU-27, monatlich. |
| `fluggaeste.csv` | 120 | 2026-09-01 | Eurostat `avia_paoc`, beförderte Fluggäste (`PAS_CRD`), EU-27, monatlich, Inlands- und Auslandsverkehr. |

Fenster: 2015-01 bis 2024-12. Nicht bewertet: 2020, 2021.

> Der Einbruch 2020 war keine Preiswirkung, sondern Folge von Reisebeschränkungen. Das Modell hat dafür keinen Mechanismus. Die Jahre werden mitgerechnet und gezeigt, aber nicht bewertet — sonst bestätigte der Backtest eine Eingabe statt einer Rechnung.
