# Luftfahrtmarkt 2026

Vorschlag der zu übernehmenden Werte, damit die Startwerte realistisch sind.
Überlegung auch die anderen Akteure mit den Segmenten zu versehen, damit diese auch immer geupdated werden (?)

***

## Consumer-Segmente

| Attribut | Ist-Wert (Config) | Empfohlener Startwert | Quelle |
|---|---|---|---|
| `business.share` | 0.30 | **0.20** | ADV-Fluggastbefragung 2025 – https://www.adv.aero/wp-content/uploads/2025/05/14-2025-Umfassende-repr%C3%A4sentative-Fluggastbefragung.pdf |
| `leisure_price_sensitive.share` | 0.50 | **0.55** | ADV-Fluggastbefragung 2025 – https://www.adv.aero/wp-content/uploads/2025/05/14-2025-Umfassende-repr%C3%A4sentative-Fluggastbefragung.pdf |
| `leisure_eco_conscious.share` | 0.20 | **0.25** | ADV-Fluggastbefragung 2025 – https://www.adv.aero/wp-content/uploads/2025/05/14-2025-Umfassende-repr%C3%A4sentative-Fluggastbefragung.pdf |
| `business.price_elasticity.mean` | 0.30 | **0.25–0.30** | IATA Business Travel Report 2024 |
| `leisure_price_sensitive.price_elasticity.mean` | 0.80 | **0.75–0.85** | Brons, M., Pels, E., Nijkamp, P. & Rietveld, P. (2002). Price elasticities of demand for passenger air travel: a meta-analysis. Journal of Air Transport Management, 8(3), 165–175. https://www.sciencedirect.com/science/article/abs/pii/S0969699701000503 & Gutachten Standortkosten Luftverkehr, BMVI: Die Preiselastizität der Nachfrage im Luftverkehr wird in der empirischen Literatur durchschnittlich auf etwa −1,1 beziffert. https://www.bmv.de/SharedDocs/DE/Anlage/LF/gutachten-standortkosten-luftverkehr.pdf |
| `leisure_eco_conscious.environmental_awareness.mean` | 0.85 | **0.80–0.85** | ADV-Befragung 2025 – https://www.adv.aero/wp-content/uploads/2025/05/14-2025-Umfassende-repr%C3%A4sentative-Fluggastbefragung.pdf |
| `total_population` | 1000 | **1000** (normiert, kann auch mehr sein und sich an dem Marktvolumen anpassen, für Realismus) | – |

***

## Provider-Betriebsparameter

| Attribut | Ist-Wert (Config) | Empfohlener Startwert | Quelle |
|---|---|---|---|
| Kerosinkosten-Anteil (operativ) | nicht spezifiziert | **~26,8%** der Betriebskosten | Österr. Parlament / IATA 2025 – https://www.apf.gv.at/news-detail/Kerosin |
| SAF-Anteil am Kraftstoffmix | nicht spezifiziert | **~0,8% (2025)** / Pflichtquote 2% | IATA aerotelegraph 2025 – https://www.aerotelegraph.com/ticker/nachhaltiger-flugkraftstoff-iata-warnt-vor-geringerem-wachstum-und-hohen-kosten-beim/zx5yc0 |
| SAF-Kostenaufschlag gegenüber Kerosin | nicht spezifiziert | **Faktor 3–5×** | Lufthansa Group Politikbrief 2024 – https://politikbrief.lufthansagroup.com/fileadmin/user_upload/2024-sep/art2/LHG-PB_2024-3_art2_nachhaltige-flugkraftstoffe.pdf |
| LCC-Marktanteil Europa | nicht spezifiziert | **~35,4%** | Eurocontrol / airliners.de 2026 – https://www.airliners.de/europa-flugverkehr-2025-erstmals-vorkrisenniveau/85464 |
| Luftverkehrssteuer Kurzstrecke (DE) | nicht spezifiziert | **13,03 € ab Juli 2026** (vorher 15,53 €) | Tagesschau 2026 – https://www.tagesschau.de/wirtschaft/verbraucher/flugtickets-senkung-steuer-100.html |

***

## Regulator-Rahmenbedingungen

| Attribut | Ist-Wert (Config) | Empfohlener Startwert | Quelle |
|---|---|---|---|
| EU-Klimaziel 2030 (Reduktion ggü. 1990) | nicht spezifiziert | **−55%** (rechtsverbindlich) | Europ. Parlament – https://www.europarl.europa.eu/topics/de/article/20180305STO99003/reduktion-von-co2-emissionen-ziele-und-massnahmen-der-eu |
| EU-Netto-Null-Zieldatum | nicht spezifiziert | **2050** | EU-Kommission – https://www.europarl.europa.eu/topics/de/article/20220610STO32720/reduzierung-der-emissionen-im-luft-und-schiffsverkehr-eu-massn |
| ETS-Reduktionsfaktor Luftfahrt p.a. | nicht spezifiziert | **4,3% (2024–2027)**, dann 4,4% | Umweltbundesamt – https://www.umweltbundesamt.de/daten/klima/der-europaeische-emissionshandel |
| Kostenlose ETS-Zertifikate | nicht spezifiziert | **0% ab 2026** (vollständige Versteigerung) | Umweltbundesamt – https://www.umweltbundesamt.de/daten/klima/der-europaeische-emissionshandel |
| SAF-Beimischpflicht 2025 | nicht spezifiziert | **2%** (EU RefuelEU Aviation) | Lufthansa Group Politikbrief – https://politikbrief.lufthansagroup.com/fileadmin/user_upload/2024-sep/art2/LHG-PB_2024-3_art2_nachhaltige-flugkraftstoffe.pdf |
| SAF-Beimischpflicht 2030 | nicht spezifiziert | **6%** | ING Luftfahrtindustrie 2026 – https://www.ingwb.com/de/insights/keine-turbulenzen-voraus-die-luftfahrtindustrie-2026 |

***

## Marktvolumen

| Attribut | Ist-Wert (Config) | Empfohlener Startwert | Quelle |
|---|---|---|---|
| Fluggäste Deutschland 2025 | nicht spezifiziert | **207,2 Mio.** (+3,9% ggü. 2024) | Destatis Jan. 2026 – https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/01/PD26_031_464.html |
| Flüge Europa 2025 | nicht spezifiziert | **11,1 Mio. Flüge** (+4% ggü. 2024) | airliners.de 2026 – https://www.airliners.de/europa-flugverkehr-2025-erstmals-vorkrisenniveau/85464 |
| Wachstumsprognose Europa 2026 | nicht spezifiziert | **+3%** (≈ 11,4 Mio. Flüge) | airliners.de 2026 – https://www.airliners.de/europa-flugverkehr-2025-erstmals-vorkrisenniveau/85464 |
| Anteil Luftfahrt an EU-Verkehrsemissionen | nicht spezifiziert | **13,4%** | Europ. Parlament – https://www.europarl.europa.eu/topics/de/article/20180305STO99003/reduktion-von-co2-emissionen-ziele-und-massnahmen-der-eu |
