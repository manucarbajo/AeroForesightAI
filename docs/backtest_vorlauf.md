# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 97.78 | 97.42 | +0.36 |  |
| 2017 | 105.83 | 102.64 | +3.19 |  |
| 2018 | 107.60 | 104.95 | +2.65 |  |
| 2019 | 107.16 | 107.00 | +0.16 |  |
| 2020 | 104.35 | 102.48 | +1.87 | ungewertet |
| 2021 | 108.19 | 105.98 | +2.21 | ungewertet |
| 2022 | 105.93 | 131.93 | -26.00 |  |
| 2023 | 102.43 | 144.57 | -42.14 |  |
| 2024 | 104.47 | 148.25 | -43.78 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 14.78 |
| Größter Abstand | 43.78 (2024) |
| davon 2015–2019 | 1.27 |
| davon 2022–2024 | 37.31 |
| Richtung der Jahresveränderung getroffen | 4/7 |
| Saisonschwankung Modell / Ziel | 11.5 / 39.8 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 40 Indexpunkte im Jahr, das Modell um 11. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Nachfrage: `booking_rate` gegen `fluggaeste`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 94.44 | 106.34 | -11.90 |  |
| 2017 | 85.66 | 114.54 | -28.88 |  |
| 2018 | 84.76 | 121.54 | -36.78 |  |
| 2019 | 86.68 | 126.28 | -39.60 |  |
| 2020 | 84.48 | 33.76 | +50.72 | ungewertet |
| 2021 | 80.02 | 45.60 | +34.42 | ungewertet |
| 2022 | 78.18 | 99.63 | -21.45 |  |
| 2023 | 80.57 | 118.70 | -38.13 |  |
| 2024 | 84.82 | 128.38 | -43.56 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 27.54 |
| Größter Abstand | 43.57 (2024) |
| davon 2015–2019 | 23.43 |
| davon 2022–2024 | 34.38 |
| Richtung der Jahresveränderung getroffen | 4/7 |
| Saisonschwankung Modell / Ziel | 28.2 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 28. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Datenquellen

| Reihe | Monate | Abgerufen | Herkunft |
| --- | ---: | --- | --- |
| `eua_auktionspreis.csv` | 119 | 2026-08-31 | EEX, Emission Spot Primary Market Auction Report. |
| `brent_rohoel.csv` | 120 | 2026-08-31 | Europe Brent Spot Price FOB, Monatsmittel. |
| `hicp_flugreisen.csv` | 120 | 2026-08-31 | Eurostat `prc_hicp_midx`, COICOP `CP0733` (Passenger transport by air), EU-27, Index 2015 = 100. |
| `bip_real.csv` | 120 | 2026-08-31 | Eurostat `namq_10_gdp`, reales BIP der EU-27 (`B1GQ`, verkettete Volumen zu Preisen von 2015, saison- und kalenderbereinigt), **vierteljährlich** und linear auf Monate interpoliert. |
| `fluggaeste.csv` | 120 | 2026-08-31 | Eurostat `avia_paoc`, beförderte Fluggäste (`PAS_CRD`), EU-27, monatlich, Inlands- und Auslandsverkehr. |

Fenster: 2015-01 bis 2024-12. Nicht bewertet: 2020, 2021.

> Der Einbruch 2020 war keine Preiswirkung, sondern Folge von Reisebeschränkungen. Das Modell hat dafür keinen Mechanismus. Die Jahre werden mitgerechnet und gezeigt, aber nicht bewertet — sonst bestätigte der Backtest eine Eingabe statt einer Rechnung.
