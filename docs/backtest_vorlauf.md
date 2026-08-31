# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 93.86 | 97.42 | -3.56 |  |
| 2017 | 107.78 | 102.64 | +5.14 |  |
| 2018 | 104.84 | 104.95 | -0.11 |  |
| 2019 | 106.62 | 107.00 | -0.38 |  |
| 2020 | 101.35 | 102.48 | -1.13 | ungewertet |
| 2021 | 104.80 | 105.98 | -1.18 | ungewertet |
| 2022 | 105.97 | 131.93 | -25.96 |  |
| 2023 | 101.17 | 144.57 | -43.40 |  |
| 2024 | 102.46 | 148.25 | -45.79 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 15.54 |
| Größter Abstand | 45.79 (2024) |
| davon 2015–2019 | 1.84 |
| davon 2022–2024 | 38.38 |
| Richtung der Jahresveränderung getroffen | 4/7 |
| Saisonschwankung Modell / Ziel | 11.7 / 39.8 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 40 Indexpunkte im Jahr, das Modell um 12. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Nachfrage: `booking_rate` gegen `fluggaeste`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 101.39 | 106.34 | -4.95 |  |
| 2017 | 84.12 | 114.54 | -30.42 |  |
| 2018 | 88.62 | 121.54 | -32.92 |  |
| 2019 | 85.77 | 126.28 | -40.51 |  |
| 2020 | 93.67 | 33.76 | +59.91 | ungewertet |
| 2021 | 84.01 | 45.60 | +38.41 | ungewertet |
| 2022 | 76.92 | 99.63 | -22.71 |  |
| 2023 | 80.29 | 118.70 | -38.41 |  |
| 2024 | 85.70 | 128.38 | -42.68 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 26.58 |
| Größter Abstand | 42.68 (2024) |
| davon 2015–2019 | 21.76 |
| davon 2022–2024 | 34.60 |
| Richtung der Jahresveränderung getroffen | 5/7 |
| Saisonschwankung Modell / Ziel | 31.1 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 31. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Datenquellen

| Reihe | Monate | Abgerufen | Herkunft |
| --- | ---: | --- | --- |
| `eua_auktionspreis.csv` | 119 | 2026-08-31 | EEX, Emission Spot Primary Market Auction Report. |
| `brent_rohoel.csv` | 120 | 2026-08-31 | Europe Brent Spot Price FOB, Monatsmittel. |
| `hicp_flugreisen.csv` | 120 | 2026-08-31 | Eurostat `prc_hicp_midx`, COICOP `CP0733` (Passenger transport by air), EU-27, Index 2015 = 100. |
| `fluggaeste.csv` | 120 | 2026-08-31 | Eurostat `avia_paoc`, beförderte Fluggäste (`PAS_CRD`), EU-27, monatlich, Inlands- und Auslandsverkehr. |

Fenster: 2015-01 bis 2024-12. Nicht bewertet: 2020, 2021.

> Der Einbruch 2020 war keine Preiswirkung, sondern Folge von Reisebeschränkungen. Das Modell hat dafür keinen Mechanismus. Die Jahre werden mitgerechnet und gezeigt, aber nicht bewertet — sonst bestätigte der Backtest eine Eingabe statt einer Rechnung.
