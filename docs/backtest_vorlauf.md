# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 94.42 | 97.42 | -3.00 |  |
| 2017 | 104.51 | 102.64 | +1.87 |  |
| 2018 | 101.42 | 104.95 | -3.53 |  |
| 2019 | 102.50 | 107.00 | -4.50 |  |
| 2020 | 129.36 | 102.48 | +26.88 | ungewertet |
| 2021 | 145.34 | 105.98 | +39.36 | ungewertet |
| 2022 | 131.32 | 131.93 | -0.61 |  |
| 2023 | 116.28 | 144.57 | -28.29 |  |
| 2024 | 106.32 | 148.25 | -41.93 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 11.96 |
| Größter Abstand | 41.93 (2024) |
| davon 2016–2019 | 3.23 |
| davon 2022–2024 | 23.61 |
| Richtung der Jahresveränderung getroffen | 4/7 |
| Saisonschwankung Modell / Ziel | 14.5 / 39.8 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 40 Indexpunkte im Jahr, das Modell um 14. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Nachfrage: `booking_rate` gegen `fluggaeste`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 100.10 | 106.34 | -6.24 |  |
| 2017 | 88.96 | 114.54 | -25.58 |  |
| 2018 | 94.43 | 121.54 | -27.11 |  |
| 2019 | 95.32 | 126.28 | -30.96 |  |
| 2020 | 47.33 | 33.76 | +13.57 | ungewertet |
| 2021 | 34.84 | 45.60 | -10.76 | ungewertet |
| 2022 | 49.13 | 99.63 | -50.50 |  |
| 2023 | 64.00 | 118.70 | -54.70 |  |
| 2024 | 84.49 | 128.38 | -43.89 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 34.14 |
| Größter Abstand | 54.69 (2023) |
| davon 2016–2019 | 22.47 |
| davon 2022–2024 | 49.70 |
| Richtung der Jahresveränderung getroffen | 6/7 |
| Saisonschwankung Modell / Ziel | 29.7 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 30. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

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
