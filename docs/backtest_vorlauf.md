# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 95.83 | 97.42 | -1.59 |  |
| 2017 | 107.18 | 102.64 | +4.54 |  |
| 2018 | 104.62 | 104.95 | -0.33 |  |
| 2019 | 107.00 | 107.00 | +0.00 |  |
| 2020 | 100.93 | 102.48 | -1.55 | ungewertet |
| 2021 | 105.64 | 105.98 | -0.34 | ungewertet |
| 2022 | 105.95 | 131.93 | -25.98 |  |
| 2023 | 104.15 | 144.57 | -40.42 |  |
| 2024 | 104.29 | 148.25 | -43.96 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 14.60 |
| Größter Abstand | 43.96 (2024) |
| davon 2015–2019 | 1.29 |
| davon 2022–2024 | 36.79 |
| Richtung der Jahresveränderung getroffen | 4/7 |
| Saisonschwankung Modell / Ziel | 10.1 / 39.8 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 40 Indexpunkte im Jahr, das Modell um 10. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

## Nachfrage: `booking_rate` gegen `fluggaeste`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 |  |
| 2016 | 99.60 | 106.34 | -6.74 |  |
| 2017 | 83.40 | 114.54 | -31.14 |  |
| 2018 | 89.25 | 121.54 | -32.29 |  |
| 2019 | 87.42 | 126.28 | -38.86 |  |
| 2020 | 89.69 | 33.76 | +55.93 | ungewertet |
| 2021 | 85.33 | 45.60 | +39.73 | ungewertet |
| 2022 | 81.36 | 99.63 | -18.27 |  |
| 2023 | 81.32 | 118.70 | -37.38 |  |
| 2024 | 88.30 | 128.38 | -40.08 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 25.60 |
| Größter Abstand | 40.08 (2024) |
| davon 2015–2019 | 21.81 |
| davon 2022–2024 | 31.91 |
| Richtung der Jahresveränderung getroffen | 3/7 |
| Saisonschwankung Modell / Ziel | 25.3 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 25. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

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
