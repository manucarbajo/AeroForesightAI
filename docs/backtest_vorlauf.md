# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 94.38 | 97.42 | -3.04 |  |
| 2017 | 103.80 | 102.64 | +1.16 |  |
| 2018 | 100.87 | 104.95 | -4.08 |  |
| 2019 | 99.82 | 107.00 | -7.18 |  |
| 2020 | 138.23 | 102.48 | +35.75 | ungewertet |
| 2021 | 165.45 | 105.98 | +59.47 | ungewertet |
| 2022 | 145.32 | 131.93 | +13.39 |  |
| 2023 | 125.09 | 144.57 | -19.48 |  |
| 2024 | 111.31 | 148.25 | -36.94 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 12.18 |
| Größter Abstand | 36.94 (2024) |
| davon 2016–2019 | 3.87 |
| davon 2022–2024 | 23.27 |
| Richtung der Jahresveränderung getroffen | 3/7 |
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
| 2016 | 99.31 | 106.34 | -7.03 |  |
| 2017 | 88.60 | 114.54 | -25.94 |  |
| 2018 | 93.04 | 121.54 | -28.50 |  |
| 2019 | 97.12 | 126.28 | -29.16 |  |
| 2020 | 51.66 | 33.76 | +17.90 | ungewertet |
| 2021 | 27.26 | 45.60 | -18.34 | ungewertet |
| 2022 | 39.49 | 99.63 | -60.14 |  |
| 2023 | 54.60 | 118.70 | -64.10 |  |
| 2024 | 76.35 | 128.38 | -52.03 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 38.13 |
| Größter Abstand | 64.09 (2023) |
| davon 2016–2019 | 22.66 |
| davon 2022–2024 | 58.76 |
| Richtung der Jahresveränderung getroffen | 5/7 |
| Saisonschwankung Modell / Ziel | 28.9 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 29. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

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
