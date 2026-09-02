# Vorschlag: Datenquellen für den Backtest (P2.7)

**Datum:** 2026-08-30 · **Status:** Vorschlag, zu entscheiden · **Betrifft:** [P2.7](projektplan.md#p27--backtest-gegen-20152024--erledigt-2026-08-30)

P2.7 sagt: *«Welche Reihe die Zielgröße ist und woher sie kommt, gehört **vor** die
Umsetzung; sonst wird das Kriterium nachträglich an die Daten angepasst, die sich
beschaffen ließen.»* Dieses Dokument macht dafür einen Vorschlag. Alle genannten
Quellen sind am 2026-08-30 auf Existenz und Abdeckung geprüft, nicht aus dem
Gedächtnis zitiert.

**Drei Dinge sind zu entscheiden**, und die zweite und dritte sind wichtiger als die
Frage nach den Quellen selbst:

1. Welche Reihen speisen die exogenen Größen?
2. **Woran wird gemessen** — und in welcher Einheit?
3. **Was passiert mit 2020?**

---

## 1. Die Eingangsseite

Das Modell kennt elf exogene Systemgrößen. Nicht alle brauchen eine historische
Reihe: Was der Backtest nicht füttert, bleibt auf seinem ausgelieferten Verlauf.

| Systemgröße | Vorgeschlagene Quelle | Abdeckung | Bemerkung |
| --- | --- | --- | --- |
| `carbon_tax_level` | EUA-Preis (EU ETS), Jahres- oder Monatsmittel | 2015–2024 | Siehe Auswahl unten |
| `oil_price_index` | [EIA, Europe Brent Spot Price FOB](https://www.eia.gov/dnav/pet/hist/rbrteA.htm) | ab 1987 | Amtlich, frei, täglich bis jährlich |
| `fuel_price_change` | aus derselben Brent-Reihe abgeleitet | ab 1987 | Veränderungsrate statt Niveau |
| `income_index` | Eurostat, BIP oder verfügbares Einkommen (EU-27) | ab 1995 | |
| `bevoelkerungsentwicklung` | Eurostat, Bevölkerungsstand | ab 1960 | Bewegt sich im Fenster kaum |
| `saf_mandate_share` | **0 für das ganze Fenster** | — | ReFuelEU greift erst ab 2025; die realen Beimischungen lagen unter 0,1 % |
| `efuel_subsidy` | **0 für das ganze Fenster** | — | Wie oben |
| `airport_fee`, `maintenance_cost_index`, `staff_cost_index` | *nicht speisen* | — | Siehe unten |
| `provider_markup`, `ticket_price` | *nicht speisen* | — | Der Lauf erzeugt sie |

**Zu den drei Kostenindizes:** Für Flughafenentgelte, Wartung und Personal gibt es
keine europaweite, frei zugängliche Zeitreihe in der Auflösung, die das Modell
braucht. Der Vorschlag ist, sie **auf ihrem ausgelieferten Verlauf zu lassen und das
zu sagen** — statt einen Hilfsindex zu basteln, der wie eine Datenquelle aussieht.
Das ist dieselbe Regel, nach der die Buchungskoeffizienten ihre Herkunft tragen: eine
fehlende Angabe ist besser als eine erfundene.

### Zur Auswahl beim EUA-Preis

Drei Wege, in der Reihenfolge meiner Empfehlung:

1. **EEX-Auktionsergebnisse** — die Primärquelle. Der EUA-Auktionskalender und die
   Zuschlagspreise sind öffentlich und decken das Fenster vollständig ab. Vorteil: Es
   ist der Markt selbst, kein Aggregat.
2. **[Sandbag Carbon Price Viewer](https://sandbag.be/carbon-price-viewer/)** —
   aufbereitete Zeitreihe ab Phase II (2008). Bequemer, eine Ebene weiter weg.
3. **[ESMA Carbon Markets Report](https://www.esma.europa.eu/sites/default/files/2025-10/ESMA50-481369926-30552_Carbon_Markets_Report_2025.pdf)** —
   amtliche EU-Aufsicht, aber als Bericht und nicht als Reihe; taugt zur Gegenprobe,
   nicht als Datenquelle.

**Wichtig für die Erwartung:** Der Luftverkehr war im Fenster nur für Flüge **innerhalb**
des EWR ETS-pflichtig, und bis 2023 mit erheblicher kostenloser Zuteilung. Der
EUA-Preis wirkte auf die Ticketpreise also deutlich schwächer, als sein Verlauf
nahelegt. Wer erwartet, dass das Modell den Preissprung von 2021/22 in den Tickets
wiederfindet, misst am falschen Maßstab.

---

## 2. Die Zielgröße — hier liegt die eigentliche Entscheidung

Das Modell liefert zwei Größen, die man prüfen kann: `booking_rate` und
`ticket_price`. Keine von beiden hat ein direktes öffentliches Gegenstück.

### Vorschlag: zwei Zielreihen, beide als Index

| Modellgröße | Zielreihe | Quelle |
| --- | --- | --- |
| `booking_rate` | Fluggäste in der EU, jährlich | [Eurostat `avia_paoc`](https://ec.europa.eu/eurostat/databrowser/view/avia_paoc/default/table?lang=en) — «Air passenger transport by type of schedule, transport coverage and country» |
| `ticket_price` | Verbraucherpreisindex Flugreisen | [Eurostat `prc_hicp_midx`, COICOP `CP0733`](https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_midx/default/table?lang=en) — «Passenger transport by air» |

**Beide sind Indizes, und das ist der Kern des Vorschlags.** `CP0733` hat die Basis
**2015 = 100** — genau der Anfang des Fensters. Das ist ein glücklicher Zufall und
sollte genutzt werden.

**Verglichen wird die relative Veränderung, nicht das Niveau.** Der absolute
Ticketpreis des Modells hängt an `base_price = 100` und an acht Koeffizienten, von
denen seit P2.1 aktenkundig **keiner geschätzt ist**. Ein Vergleich auf Euro-Niveau
würde eine Genauigkeit prüfen, die das Modell nie behauptet hat — und er würde
scheitern, ohne etwas über die Mechanik zu sagen. Was der Backtest prüfen kann, ist:

- **Richtung**: Geht es hoch, wenn es real hoch ging?
- **Größenordnung**: Ist die Bewegung 5 % oder 50 %, wenn real 20 % waren?
- **Wendepunkte**: Kippt die Nachfrage dort, wo sie real kippte?

Alles drei sind Aussagen über die Mechanik. Das Preisniveau ist keine.

### Die Auflösung

`CP0733` liegt monatlich vor, `avia_paoc` jährlich. Vorschlag: **ein Tick = ein
Monat**, 120 Ticks für 2015–2024, die Jahresreihe wird zur Prüfung auf Jahresenden
aggregiert.

Und die Warnung, die der Plan schon aufschreibt: **Die Zuordnung von Monaten zu Ticks
gehört in die Auswertung, nicht ins Modell.** Invariante 5 gilt weiter — kein Datum in
Config, Checkpoint oder Output. Der Backtest bringt seine eigene Übersetzungstabelle
mit und lässt den Tick ein Tick sein.

---

## 3. Das Problem 2020 — und warum es die Aussage des ganzen Pakets entscheidet

Der Einbruch 2020 war **kein Preiseffekt**. Er kam aus Reisebeschränkungen,
Grenzschließungen und Quarantänepflichten. Das Modell hat dafür **keinen
Mechanismus**: Es kennt Preis, Abgabe, Substitution und Sättigung — keine
Kapazitätsgrenze und kein Reiseverbot. Der einzige Faktor, der Pandemien überhaupt
benennt, ist F7, und der wird aus dem Ölpreis abgeleitet.

Daraus folgen drei Möglichkeiten, und sie sind nicht gleichwertig:

| | Weg | Was er wert ist |
| --- | --- | --- |
| **A** | Den Einbruch über `demand_growth_rate` einspeisen | **Wertlos als Test.** Das Modell sagt 2020 dann nicht voraus, es bekommt es gesagt — und der Backtest bestätigt eine Eingabe. Genau die Zirkularität, wegen der P2.7 hinter P2.0 steht. |
| **B** ✅ | 2020 und 2021 aus der **Bewertung** ausschließen, aber mitrechnen und **zeigen** | Ehrlich und lehrreich: Die Abweichung ist dann sichtbar und benannt — «hier fehlt dem Modell ein Mechanismus». Das ist eine Aussage über die Grenzen, und die ist verkaufbar. |
| **C** | Eine exogene Größe «Reisebeschränkung» einführen | Sauber, aber ein Modellumbau. Er gehört in ein eigenes Paket, nicht in den Backtest. |

**Empfehlung: B.** Der Backtest rechnet 2015–2024 durch, bewertet 2015–2019 und
2022–2024, und stellt 2020–2021 **unbewertet daneben** — mit dem Satz, warum. Ein
Modell, das seine eigene Lücke zeigt, ist glaubwürdiger als eines, das sie
wegdefiniert.

---

## 4. Was ich zuerst bauen würde

Nicht die ganze Pipeline. **Ein Vorlauf mit zwei Reihen**, um herauszufinden, ob die
Übung überhaupt trägt:

1. Brent (EIA) und EUA-Preis als Monatsreihen holen, nach `configs/backtest/` legen —
   mit einer Quellendatei daneben, die Abrufdatum und URL festhält.
2. Sie als Rahmenszenario einspeisen (die Maschinerie dafür steht seit P2.0).
3. Den Ticketpreis des Laufs gegen `CP0733` **indexiert** vergleichen, 2015 = 100.
4. Die Abweichung beziffern und **veröffentlichen, auch wenn sie groß ist.**

Erst wenn das steht, lohnt die Nachfrageseite. Der Grund ist Reihenfolge, nicht
Bequemlichkeit: Trifft schon der Preispfad die Größenordnung nicht, sagt die
Nachfrageseite nichts mehr dazu — sie hängt am Preis.

**Was der Vorlauf beantwortet, bevor jemand mehr investiert:** Ob das Modell die
Richtung überhaupt trifft. Fällt schon das durch, ist das ein Ergebnis — und der
Projektplan sagt seit dem 2026-08-29, dass ein dokumentierter Fehlschlag mehr wert
ist als ein ungeprüftes Modell.

---

## Was noch offen ist

- **Der EUA-Bezug.** Ob EEX-Auktionen oder eine aufbereitete Reihe — eine Entscheidung
  über Aufwand gegen Nähe zur Quelle.
- **Die Nachfragereihe.** `avia_paoc` ist jährlich; ob eine monatliche Reihe
  (Eurostat führt auch monatliche Fluggastdaten) den Aufwand lohnt, hängt daran, ob
  Wendepunkte innerhalb eines Jahres geprüft werden sollen.
- **Lizenz und Ablage.** Eurostat- und EIA-Daten sind frei nutzbar mit Quellenangabe.
  Ob die Reihen ins Repo kommen oder beim Lauf geholt werden, ist eine Frage der
  Reproduzierbarkeit — für einen Backtest spricht viel dafür, sie **einzuchecken**,
  samt Abrufdatum: Eine später revidierte Reihe ändert sonst rückwirkend das Ergebnis.

## Quellen

- [Eurostat, `avia_paoc` — Air passenger transport](https://ec.europa.eu/eurostat/databrowser/view/avia_paoc/default/table?lang=en)
- [Eurostat, `prc_hicp_midx` — HICP monthly index (COICOP `CP0733`)](https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_midx/default/table?lang=en)
- [Eurostat, Air passenger transport statistics (Statistics Explained)](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Air_passenger_transport_statistics)
- [EIA, Europe Brent Spot Price FOB (jährlich)](https://www.eia.gov/dnav/pet/hist/rbrteA.htm)
- [EIA, Spot Prices for Crude Oil and Petroleum Products](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_m.htm)
- [Sandbag Carbon Price Viewer](https://sandbag.be/carbon-price-viewer/)
- [ESMA, EU Carbon Markets Report 2025](https://www.esma.europa.eu/sites/default/files/2025-10/ESMA50-481369926-30552_Carbon_Markets_Report_2025.pdf)
- [FRED-Spiegelung von `CP0733` für die EU](https://fred.stlouisfed.org/series/CP0733EUCCM086NEST)
