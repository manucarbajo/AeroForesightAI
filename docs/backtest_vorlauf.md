# Backtest-Vorlauf 2015–2024

> Erzeugt von `python -m src.backtest.vorlauf`. **Diese Datei wird überschrieben** — wer ein Ergebnis festhalten will, kopiert es heraus.

## Preis: `ticket_price` gegen `hicp_flugreisen`

| Jahr | Modell | Zielreihe | Abstand | |
| --- | ---: | ---: | ---: | --- |
| 2015 | 100.00 | 100.00 | +0.00 | Basis, Abstand per Konstruktion 0 |
| 2016 | 97.84 | 97.42 | +0.42 |  |
| 2017 | 104.93 | 102.64 | +2.29 |  |
| 2018 | 105.95 | 104.95 | +1.00 |  |
| 2019 | 107.31 | 107.00 | +0.31 |  |
| 2020 | 130.23 | 102.48 | +27.75 | ungewertet |
| 2021 | 157.20 | 105.98 | +51.22 | ungewertet |
| 2022 | 141.09 | 131.93 | +9.16 |  |
| 2023 | 124.62 | 144.57 | -19.95 |  |
| 2024 | 113.37 | 148.25 | -34.88 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 9.72 |
| Größter Abstand | 34.88 (2024) |
| davon 2016–2019 | 1.01 |
| davon 2022–2024 | 21.33 |
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
| 2016 | 95.19 | 106.34 | -11.15 |  |
| 2017 | 90.24 | 114.54 | -24.30 |  |
| 2018 | 91.54 | 121.54 | -30.00 |  |
| 2019 | 92.35 | 126.28 | -33.93 |  |
| 2020 | 48.67 | 33.76 | +14.91 | ungewertet |
| 2021 | 30.71 | 45.60 | -14.89 | ungewertet |
| 2022 | 47.82 | 99.63 | -51.81 |  |
| 2023 | 61.45 | 118.70 | -57.25 |  |
| 2024 | 82.30 | 128.38 | -46.08 |  |

| Kennzahl | Wert |
| --- | ---: |
| Mittlerer Abstand, bewertete Jahre | 36.36 |
| Größter Abstand | 57.25 (2023) |
| davon 2016–2019 | 24.85 |
| davon 2022–2024 | 51.71 |
| Richtung der Jahresveränderung getroffen | 5/7 |
| Saisonschwankung Modell / Ziel | 31.0 / 75.9 |

- Verglichen wird der Index (Basis 2015 = 100) auf **Jahresmitteln**, nicht das Preisniveau und nicht monatlich.
- 2015 steht in der Tabelle, geht aber **nicht** in den Abstand ein: Beide Reihen sind darauf indexiert, sein Abstand ist per Konstruktion null. In die **Richtung** der Jahresveränderung zählt es mit — tautologisch ist das Niveau, nicht die Bewegung zum Folgejahr.
- Die absoluten Euro-Beträge des Modells hängen an ungeeichten Koeffizienten (P2.1); ein Niveauvergleich prüfte eine Genauigkeit, die nie behauptet wurde.
- 2020, 2021 sind mitgerechnet, aber nicht bewertet: Der Einbruch war keine Preiswirkung, und das Modell kennt keine Reisebeschränkung.
- Die Zielreihe schwankt saisonal um 76 Indexpunkte im Jahr, das Modell um 31. **Ein Monatsvergleich misst deshalb vor allem die fehlende Saison** — deswegen die Jahresmittel.

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
