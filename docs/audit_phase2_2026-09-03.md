# Audit der Phase 2 — Modellsubstanz

**Unabhängige Prüfung von Manus Umsetzung · 2026-09-03 · Codestand `aff7d63` (`feat/phase-2-p20-rahmen`)**

Geprüft wurde zweierlei, getrennt: **hält jedes Paket sein eigenes
Abnahmekriterium** (Teil A), und **hält die Umsetzung einer Prüfung stand, die
den Projektplan nicht als Maßstab nimmt** (Teil B) — Korrektheit,
Sinnhaftigkeit, Effizienz. Dazu Doku- und Prozesskonformität (Teil C) und das
nach außen gereichte Artefakt «Bilanz der Modellsubstanz» (Teil D).

**Nachgemessen, nicht gelesen.** Jede Zahl unten stammt aus einem Skript, das im
Anhang steht und sich wiederholen lässt. Das ist die Arbeitsweise, die Phase 2
selbst etabliert hat — *eine Messung findet, was wirklich dasteht; ein Blick in
den Code findet, was jemand hingeschrieben hat* —, hier auf Phase 2 angewandt.

---

## Urteil in vier Sätzen

**Phase 2 ist substanziell und handwerklich stark.** Sechs der zehn Pakete
halten, was sie zusagen, und ihre veröffentlichten Messwerte reproduzieren am
laufenden System. Die Befunde ballen sich an **einer** Stelle: **P2.8/P2.8-B,
die Angebotsseite** — dort steckt ein echter Rechenfehler, und die tragende
Zusage des Pakets wird von seinen eigenen Zahlen widerlegt. Dazu kommen zwei
Methodikbefunde am Backtest, ein rot gewordener Wächter, den niemand laufen
lässt, und Doku-Drift, die nach außen zeigt.

**Was ausdrücklich nicht beanstandet wird:** die Arbeitsweise. Vorher/Nachher
mit unverändertem Verfahren, das Ergebnis auch dann behalten, wenn es schlechter
wird, und die Entscheidung «real statt nominal», die gegen das eigene Ergebnis
ging — das ist die Substanz dieser Phase und sollte niemand antasten.

---

## Prüfstand

| | |
| --- | --- |
| **Codestand** | `aff7d63`, Arbeitsbaum sauber, `.venv` nach Konvention |
| **Statisch** | vollständige Lektüre von `population_sampler`, `market_feedback`, `simulation_functions`, `src/backtest/*`, `scenario_consistency`, `state_explorer`, `scenario_sweeps`, `property_models`; alle acht Dateien in `configs/sweeps/`; `configs/properties.json`; `configs/cib_frozen.json` |
| **Dynamisch** | fünf Messskripte (Anhang): Kapazität × Strategie über 40 Ticks, Sättigung je Person, Elastizitäten an 5000 Personen, Faktorlagen über 50 Läufe, cProfile des Bevölkerungs-Ticks |
| **Suite** | `pytest` vollständig (ohne die zwei dokumentierten Ollama-Hänger): **7 failed, 1549 passed, 1 skipped, 2 deselected** in 19:24 min |
| **Linter** | `ruff check .` grün · `black --check .` grün (241 Dateien) |
| **Nicht angefasst** | keine Datei im Repo wurde für dieses Audit verändert |

---

## Teil A — Abgleich gegen den Projektplan

| Paket | Zusage gehalten? | Befund |
| --- | --- | --- |
| **P2.0** Rahmen statt Urteil | **teilweise**, als ✅ geführt | 2 von 4 Abnahmeklauseln offen → **A1**; Stufe C hat zudem den Browser-Wächter rot gemacht → **C5** |
| **P2.1** Echte Ziehung + Koeffizienten | ✅ | `DEFAULT_LOGIT_THRESHOLD` und `_seed_runtime` wirklich entfernt, `rng` Pflicht ohne Default, acht Koeffizienten mit erzwungener Herkunftsangabe |
| **P2.2** Szenarienschicht (Variante C) | ✅ | echte Rechtsquellen, PDFs im Repo; zwei Kleinigkeiten → **B7a**, **B7b** |
| **P2.3** Matrix-Provenienz (entfallen, Rest) | ✅ | `source` umbenannt, `entries` weg, Erzeuger mitgeändert — alles nachgeprüft |
| **P2.4** Das Alter prägt die Person (+D, +E) | ✅ | Altersgruppen-Tabelle und Preiselastizität reproduzieren → **D-Tabelle** |
| **P2.5** Grounding durchsetzen | ✅ | Zusage korrekt eng formuliert; Trennschärfe begrenzt → **B7c** |
| **P2.6** Ensemble-Band | ✅ | Perzentile korrekt, Band hat Breite, Darstellung sauber |
| **P2.7** Backtest gegen 2015–2024 | ✅ mit **Methodikvorbehalt** | → **B3**, **B4** |
| **P2.8 / P2.8-B** Angebotsseite | **nein**, als «Weg A umgesetzt» geführt | → **B1**, **B2**, **B5**, **B6** |
| **P2.9** Altersverteilung | ✅ | 1,6 % Klemmung nachgemessen, wie angegeben |

### A1 — P2.0 trägt ✅, zwei seiner vier Abnahmeklauseln sind offen

Der Wortlaut aus «Fertig wenn», Klausel für Klausel geprüft:

**1. «Ein Lauf nimmt ein benanntes Rahmenszenario entgegen und erzeugt
Faktorlabels, statt sie zu bekommen» — erfüllt.**
Gemessen über alle vier Rahmen: Sie erzeugen unterschiedliche Endlagen
(`business_as_usual` → `F2.1/F3.1`, `co2_delayed` → `F2.2/F3.2`,
`transformation_conflict` → `F6.2/F7.2`). Es gibt keinen Schreibweg mehr zur
Faktorlage. **Die Umdrehung steht** — das ist das inhaltliche Herz von P2.0 und
es funktioniert.

**2. «die Sweeps sind der reguläre Startpfad» — offen.**
Stufe C sagt es selbst, im selben Paket: «Die Sweeps sind noch nicht der
reguläre Startpfad — ein Einzellauf ohne Preset rechnet weiterhin gegen die
Datei-Defaults.» Die Klausel wurde mit abgehakt, ohne dass jemand sie strich
oder als Rest auswies.

**3. «kein Codepfad bewertet mehr den Endzustand gegen die Matrix, um zu
entscheiden, was gezeigt wird» — formal erfüllt, substanziell nicht.**
`derive_scenarios(top_n=3, allow_inconsistent=False)` läuft unverändert in
[`scenario_agent_node.py:81`](../src/cib/scenario_agent_node.py), zählt alle
2⁷ Kombinationen durch, rankt sie nach Konsistenzwert und liefert auf der
ausgelieferten Matrix **genau eine**. Der *Endzustand* ging dabei nie ein — die
Klausel unterstellte einen Mechanismus, den der Code nie hatte, und P2.0-B hat
das selbst gemessen und festgehalten. Was gezeigt wird, entscheidet damit
weiterhin die Matrix; das Artefakt sagt es inzwischen ehrlich, aber es ist
unverändert so.

**4. «Ein Test zeigt, dass zwei Läufe unter demselben Rahmen unterschiedliche
Faktorlabels erzeugen können» — den Test gibt es nicht, und die Eigenschaft ist
abwesend.**

Nachgemessen, **50 Läufe** (5 Seeds × 5 Rahmen × {20, 40} Ticks):

| Rahmen | 20 Ticks | 40 Ticks |
| --- | --- | --- |
| Standard | 1 Lage über 5 Seeds | 1 Lage über 5 Seeds |
| `business_as_usual` | 1 | 1 |
| `co2_delayed` | 1 | 1 |
| `freiwillige_wende` | 1 | 1 |
| `transformation_conflict` | 1 | 1 |

**In jedem einzelnen Fall enden alle fünf Seeds auf derselben Faktorlage.**
P2.1 hatte das nebenbei bereits gemessen («Der Seed verschiebt die
Faktor-Endzustände jetzt kaum noch») und die betroffenen Tests in
`test_run_provenance.py` auf die schwächere Aussage «der Lauf bewegt die
Faktoren überhaupt» umgestellt — **ohne das Abnahmekriterium von P2.0
nachzuziehen**.

**Das ist keine Panne, sondern ein falsches Kriterium.** Über tausend Personen
mitteln sich die Einzelentscheidungen aus, und die Faktorregeln sind
Schwellwerte — Streuung *kann* dort nicht durchschlagen. Die tragfähige Fassung
lautet: *zwei verschiedene Rahmen erzeugen verschiedene Lagen*, und die ist
erfüllt. Sie gehört an die Stelle der alten, statt dass die alte stillschweigend
abgehakt bleibt.

**Und eine Produktaussage hängt daran.** Das Tripleset soll «aus der Wahl der
Rahmenszenarien» kommen. Es gibt **vier** Rahmen, nicht drei, und keinen
Codepfad, der aus ihnen ein Tripleset bildet. `README.md:7` verspricht
unverändert, jeder Lauf erzeuge automatisch eines aus Trendfortsetzung,
Strukturwende und Krisenkonflikt.

---

## Teil B — Unabhängige Prüfung

### B1 · Die Rationierung sättigt, wen sie abweist ⛔ **schwer, Rechenfehler**

**Fundstelle:** [`src/population/population_sampler.py:926`](../src/population/population_sampler.py)
(`_kapazitaet_begrenzen`), im Zusammenspiel mit `evaluate_booking` (Z. 700–704).

Bei knapper Kapazität setzt `_kapazitaet_begrenzen` den überzähligen Personen
`booked = False` — **nimmt aber den Sättigungsaufschlag nicht zurück**, den
`evaluate_booking` unmittelbar davor vergeben hat.

Der Docstring behauptet ausdrücklich das Gegenteil:

> «Die Sättigung bleibt unberührt: Wer keinen Platz bekommt, hat nicht gebucht
> und wird deshalb auch nicht gesättigt. Das fällt automatisch heraus, weil
> `booked` zurückgesetzt wird, bevor die Sättigung daran anknüpft.»

Sie knüpft nicht *danach* an. Sie ist bereits vergeben, wenn `booked`
zurückgesetzt wird.

**Gemessen** (Strategie `marge`, `kapazitaet_index = 0,5`, ein Tick,
1000 Personen, Seed 42):

| | |
| --- | ---: |
| wollten buchen | 658 |
| bekamen einen Platz | 185 |
| **gehen leer aus und tragen trotzdem `saturation_level = 0,6`** | **473** |

Diese 473 Personen werden im nächsten Tick für eine Reise bestraft, die sie
nicht angetreten haben: Die Sättigung geht als Malus in ihren Nutzen ein.

**Wirkung:** Unter `marge` sinkt die Nachfrage dauerhaft **unter** die
Kapazität, statt sich an ihr zu stauen — der Mechanismus arbeitet gegen die
Aussage, für die er gebaut wurde (siehe **B2**).

**Warum kein Wächter es fängt:** Die elf Zusagen von
`test_preisstrategie_ist_eine_wahl.py` prüfen den Preis über Kapazitäten hinweg
und die Zufälligkeit der Auswahl. Den **Zustand der Abgewiesenen** prüft keine.

**Fix:** die Sättigung erst *nach* der Rationierung vergeben, plus eine Zusage,
die genau diese Personengruppe misst.

> **Behoben noch am 2026-09-03.** `_kapazitaet_begrenzen` ist entfallen;
> `evaluate_booking` zieht, rationiert und sättigt jetzt in dieser Reihenfolge,
> weil das *eine* Entscheidung ist. Ein Zurückrechnen wäre nicht einmal möglich
> gewesen — `min(1.0, …)` klemmt die Sättigung, der Ausgangswert ist damit weg.
> Der Standard bewegt sich nicht: Unter `auslastung` gibt es keine Schranke, ein
> Standardlauf über 40 Ticks liefert unverändert 0,2587 / 118,85. Wächter:
> `TestWerKeinenPlatzBekommtWirdNichtGesaettigt`, fünf Zusagen.

### B2 · «Mehr Plätze bei gleichem Preis» ist weiterhin nicht darstellbar ⛔ **schwer, Zusage**

CLAUDE.md sagt heute: «Damit ist die Kombination *Wachstum bei flachen Preisen*
erstmals darstellbar.» **Nachgemessen ist sie es nicht.**

40 Ticks, Standardkonfiguration, variiert werden nur Strategie und
`kapazitaet_index`; angegeben ist das letzte Viertel:

| `kapazitaet_index` | `marge` — Rate / Preis | `auslastung` — Rate / Preis |
| ---: | --- | --- |
| 0,3 | 0,1003 / 189,78 | — |
| 0,5 | 0,1063 / 189,78 | 0,1529 / 159,42 |
| 0,7 | 0,1064 / 189,78 | — |
| 1,0 | 0,1064 / 189,78 | 0,2587 / 118,85 |
| 1,3 | 0,1064 / 189,78 | 0,3052 / 100,50 |

Drei Aussagen stehen darin:

1. **Unter `marge` tut die Kapazität nichts.** Von 0,5 bis 1,3 — also bei mehr
   als der doppelten Sitzzahl — ändert sich die Buchungsrate um **0,0001**.
   Selbst bei 0,3 (Schranke = 0,37 × 0,3 = 0,111) bleibt die Rate mit 0,1003
   **unter** der Schranke; sie greift dort gar nicht.
2. **Der Grund ist strukturell, nicht numerisch.** Eine Obergrenze kann
   Nachfrage nur **senken**, nie heben. «Mehr Plätze → mehr Verkehr» ist unter
   `marge` baulich unmöglich, bei jedem Wert — die Schranke ist die einzige
   Wirkung, die die Kapazität dort hat.
3. **Unter `auslastung` wächst der Verkehr** — aber nur mit fallendem Preis
   (0,5 → 159,42 EUR, 1,3 → 100,50 EUR), also mit genau dem Verhalten, das
   P2.8-B als eingebaute Annahme benannt und abschaffen wollte.

**Damit ist der konkrete Fall, für den P2.8-B gebaut wurde — die reale Lage
2015–2019, mehr Sitze bei flachen Preisen — in keiner der beiden Strategien
darstellbar.** Die Diagnose des Pakets (ein Werkzeug mit nur einer
Verhaltensannahme trägt einen Bias) ist richtig; die Behebung greift nicht.
Verstärkt wird das durch **B1**: Die Rationierung drückt die Nachfrage
zusätzlich unter die Kapazität.

> **Behoben am 2026-09-03 — als Modellentscheidung, nicht als Fix.** Die
> Kapazität steht seither als Merkmal der Alternative im Nutzen
> (`gewicht × ln(kapazitaet_index)`): Mehr Angebot heißt mehr Frequenzen und
> Strecken, also niedrigere generalisierte Reisekosten. Unter `marge` steigt der
> Verkehr damit von 0,0692 auf 0,1151, **während der Preis bei 189,78 steht**.
> `ln(1) = 0`, der Standard bewegt sich nicht. Der Backtest gewinnt in sieben von
> acht Kennzahlen — mit dem Vorbehalt aus **B4**: Er speist die Kapazität aus
> derselben Tabelle wie seine Nachfrage-Zielreihe, der neue Kanal macht diesen
> Widerhall stärker. Die tragende Evidenz ist deshalb die Tabelle oben, nicht der
> Backtest.

**Warum der Wächter es nicht sah:** Er prüfte zwei Dinge getrennt, die
zusammengehören — Preiskonstanz über Kapazitäten (`marge`, 40 Ticks) und das
Greifen der Schranke (ein Tick, künstlich auf 100 EUR gesetzter Preis). Eine
Zusage «mehr Kapazität ⇒ mehr Verkehr bei gleichem Preis» gibt es nicht, und
sie wäre heute rot. Das ist dieselbe Lehre, die P2.4-E schon einmal gezogen
hat: *Ein Wächter, der den Mechanismus prüft statt die Zusage, ist grün und
nutzlos.*

### B3 · Der Backtest mittelt ein tautologisches Jahr mit 🔶 **mittel, Methodik**

`bewerten()` indexiert Modell **und** Zielreihe auf 2015 = 100. **2015 hat damit
per Konstruktion den Abstand 0** — und geht trotzdem in jede veröffentlichte
Kennzahl ein:

| | veröffentlicht (mit 2015) | ohne 2015 |
| --- | ---: | ---: |
| Preis, 2015–2019 | **3,09** | 3,87 |
| Preis, alle bewerteten Jahre | **10,66** | 12,18 |
| Nachfrage, 2015–2019 | **18,13** | 22,66 |
| Nachfrage, alle bewerteten Jahre | **33,36** | 38,13 |

Ein Fünftel des Vorpandemie-Fensters ist ein Datenpunkt, der **nicht anders
ausfallen kann**. Der Projektplan benennt die Tautologie («2015 liegt durch die
Indexbasis per Konstruktion auf null»), zieht daraus aber keine Konsequenz für
die Kennzahl.

**Verschärfend:** Die Ergebnistabelle in P2.7 zeigt die Jahre **2016–2024**, das
Basisjahr also gar nicht — der daneben stehende Wert schließt es ein. Der
veröffentlichte Wert ist aus der veröffentlichten Tabelle **nicht
nachrechenbar**, und genau das prüft ein Fachprüfer zuerst nach.

**Empfehlung:** Basisjahr aus der Kennzahl herausnehmen (die Tabelle darf es
zeigen), beide Zahlenreihen einmal nachziehen, den Schnitt in
`docs/handbuch/vergleiche.md` benennen. Die Aussage des Backtests wird dadurch
nicht schlechter — sie wird prüfbar.

> **Umgesetzt am 2026-09-03.** Die Kennzahlen stehen seither auf 12,18 / 3,87
> (Preis) und 38,13 / 22,66 (Nachfrage). Eine Unterscheidung kam beim Bauen
> dazu: Tautologisch ist das **Niveau** im Basisjahr, nicht die **Bewegung** zum
> Folgejahr — die Richtungskennzahl zählt es deshalb weiterhin mit und steht
> unverändert bei 3/7 und 5/7. Zwei Marken statt einer: «Basis» sagt etwas über
> die Messung, «ungewertet» über das Modell.

### B4 · Eingang und Ziel der Nachfrageseite stammen aus derselben Erhebung 🔶 **mittel, Methodik**

Seit P2.8 speist der Backtest:

- **Eingang** `kapazitaet_index` ← Eurostat `avia_paoc`, `CAF_PAS` (Flüge)
- **Ziel** `fluggaeste` ← Eurostat `avia_paoc`, `PAS_CRD` (Passagiere)

Dieselbe Erhebung, dieselbe Tabelle, und mechanisch verbunden:
Passagiere = Flüge × Sitze je Flugzeug × Auslastung. Die Doku benennt die
*Näherung* sauber («zählt Flüge, nicht Sitze») — **nicht**, dass damit ein enger
Proxy der Zielgröße als exogene Eingabe in den Lauf geht.

Zwei Konsequenzen:

1. **Der Nachfrage-Backtest misst ab 2022 überwiegend die
   Sitze-je-Flug-Lücke** (Flüge 107,6 gegen Passagiere 128,4 im Jahr 2024), nicht
   die Modellmechanik. Der Plan liest das richtig («das Modell folgt jetzt treu
   den Flügen») und zieht daraus den Schluss, die Mechanik greife — belegt ist
   vor allem, dass die Eingabe durchschlägt.
2. **Der Satz «ein Maßstab *außerhalb* seiner selbst»** gilt für die Preisseite
   uneingeschränkt; für die Nachfrageseite gilt er seit P2.8 nur noch
   eingeschränkt. Das gehört dazugeschrieben, weil es die stärkste Aussage der
   ganzen Phase relativiert.

> **Gemessen am 2026-09-03 — und Punkt 2 war zu pessimistisch. Diese Einschätzung
> korrigiere ich hiermit.** Die Sorge ließ sich nachrechnen statt beteuern:
> derselbe Lauf ohne die Kapazitätsreihe, sonst unverändertes Verfahren. Ergebnis:
> Auf der Nachfrageseite ist der Abstand **mit** dem Eingang **größer** (36,36
> gegen 28,65). Ein Widerhall sähe umgekehrt aus — die Zirkularität bläht die
> Übereinstimmung also **nicht** auf, das Modell folgt treu den Flügen und
> verfehlt damit die Passagiere.
>
> Was der Eingang beiträgt, zeigt sich an zwei Stellen, die nicht zirkulär sein
> können: an der **Richtung** (5/7 gegen 1/7 — ohne Kapazität trifft das Modell
> die Wendepunkte praktisch nie) und an der **Preisseite** mit ihrer unabhängigen
> Zielreihe (16,70 → **9,72**). Auch die Bemerkung bei **B2**, der neue
> Verfügbarkeitskanal mache den Widerhall «stärker», hält so nicht — er macht die
> Richtung besser und den Abstand schlechter.
>
> **Der Vorbehalt bleibt, nur präziser:** Nicht die Zirkularität ist das Problem,
> sondern die Sitze-gegen-Flüge-Lücke. Die Gegenprobe steht seither dauerhaft im
> Bericht (P2.7, Abschnitt «Gegenprobe»), gehalten von
> `TestDieGegenprobeStehtImBericht`.

**Nebenbefund:** Die Begründung, 2020/21 nicht zu bewerten («das Modell hat für
Reisebeschränkungen keinen Mechanismus»), ist seit P2.8 überholt — der Einbruch
*wird* über die Kapazitätsreihe eingespeist, und das Modell fällt 2021 auf 27,3.
Die Entscheidung, die Jahre nicht zu bewerten, bleibt richtig; ihre Begründung
gehört neu geschrieben.

### B5 · Einkommen wirkt als Schwelle, nicht als Elastizität 🔶 **mittel, Sachaussage**

Projektplan und CLAUDE.md führen **+1,10** als belegte «korrekte Form»:

> «Die Einkommenselastizität des Buchungsmodells beträgt **+1,10** … Luftverkehr
> gilt als Luxusgut mit Einkommenselastizität über 1. **Die Form stimmt also**,
> und das ist eine gute Nachricht über das Modell.»

**Nachgemessen am heutigen Stand** (5000 Personen, 140 EUR, fester Preis):

| Einkommensschock | Buchungsneigung | Elastizität |
| --- | --- | ---: |
| +5 % | 0,4815 → 0,4996 | **+0,75** |
| +10 % | 0,4815 → 0,5146 | **+0,69** |
| +40 % | 0,4815 → 0,5733 | **+0,48** |

Die Ursache steht im Code: `income_factor` erscheint in `booking_probability`
**ausschließlich** in der Erschwinglichkeitsschranke —
`affordability_limit = wtp_eur × income_factor × (1 + green_premium × awareness)`,
und wer darüber liegt, bekommt `return 0.0` — und **kommt im Nutzenterm nicht
vor**. Einkommen verschiebt also nur eine harte Grenze. Die «Elastizität» ist
damit die Dichte der WTP-Verteilung am aktuellen Preis, kein
Verhaltensparameter, und sie fällt mit steigendem Einkommen, weil die Masse
jenseits der Schwelle dünner wird.

> **Behoben am 2026-09-03 (P2.12).** Der Preis wird jetzt an dem gemessen, was
> jemand hat (`normalized_price / income_factor`) — die Budgetanteils-Form, und
> sie kostet **keinen neuen Koeffizienten**: Einkommen wirkt über den
> Preiskanal, den es ohnehin gibt. Die Elastizität liegt am Rand bei **+1,02**
> statt +0,75 und folgt damit aus der **Form** statt aus einer gesetzten Zahl.
> Der Backtest gewinnt auf der Preisseite deutlich (3,23 → **1,01** vor der
> Pandemie, der beste je gemessene Wert) und verliert auf der Nachfrageseite
> leicht (22,47 → 24,85); behalten wird es wegen des Mechanismus, nicht wegen
> der Punktzahl — dieselbe Entscheidung wie beim Altersprofil in P2.4.
> **Anders als bei B2 bewegt sich der Standard**: 0,264167 / 120,13 statt
> 0,258704 / 118,85, also ein Schnitt im Handbuch.

**Was das für P2.8 heißt:** Die **Schlussfolgerung** — der Einkommenskanal
schließt die Nachfragelücke nicht — wird dadurch **gestützt**, nicht
angezweifelt. Falsch ist die **Begründung**: Ein Schwellenmechanismus ist mit
der Einkommenselastizität bei Brons et al. nicht vergleichbar. Es ist genau die
Trennung «Form belegt / Wert gesetzt», auf die das Projekt sonst besteht — hier
wurde die Form als belegt geführt, obwohl es eine andere ist.

### B6 · Was gebaut ist, benutzt kein ausgeliefertes Szenario 🔶 **mittel, Produktwirkung**

Nachgezählt über alle acht Dateien in `configs/sweeps/` und über
`configs/properties.json`:

| Größe | ausgeliefert | von einem Szenario gesetzt? |
| --- | --- | --- |
| `kapazitaet_index` | 1,0, **keine Regel** | **nein, in keiner Datei** |
| `strategie` | `auslastung` | **nein** |
| `erneuerungsrate` | 0,0 | **nein** |
| `altersmittel_jahre` | 50,8, konstant | **nein** |
| `income_index` | 1,0 + 2 Regeln | ja, alle vier Rahmen |

**Die Angebotsseite aus P2.8/P2.8-B und die alternde Gesellschaft aus P2.4-D/E
leben heute ausschließlich im Backtest.** Für die vier ausgelieferten Weltbilder
ist die Kapazität konstant — obwohl ihre Kohärenzbegründungen
Nachfrageentwicklungen behaupten, die ohne Angebotsentwicklung nicht darstellbar
sind. Das ist wörtlich der Befund von P2.8, nur jetzt auf die eigenen Szenarien
angewandt. Der Nutzen der Pakete **am Produkt** ist heute null, und das steht
nirgends.

Ergänzend, weil es dieselbe Lücke ist: `bevoelkerungsentwicklung` endet bei
Tick 30, die vier Rahmen laufen über 50 Ticks — **20 von 50 Ticks mit
eingefrorener Bevölkerung, in jedem ausgelieferten Weltbild**. Als Restposition
von P2.8 korrekt benannt und offen.

> **Behoben am 2026-09-03 (P2.10).** Alle vier Rahmen tragen jetzt einen
> begründeten Kapazitätspfad und ihre Preisstrategie — letztere konnte ein
> Szenario bis dahin gar nicht setzen, obwohl P2.8-B sie «eine Frage an das
> Szenario» nannte. Gemessen kommt sie an: «Business as Usual» 0,3024 → 0,3892,
> «Transformationskonflikt» 0,2585 → 0,0363. **Eine Messung hat dabei eine Wahl
> widerlegt** — `marge` für «Freiwillige Wende» erzeugte den Nachfrageeinbruch,
> den die These des Szenarios ausschließt; gewählt ist `auslastung`, und der
> Grund steht in der Datei. Die Restposition zur Bevölkerungskurve bleibt.

### B7 · Kleinere Befunde

**B7a — `co2_delayed` trägt keinen eigenen Vorbehalt.** Sein `vorbehalt`-Feld
ist **exakt** der Textbaustein, den alle vier Rahmen teilen (316 Zeichen; der
gemeinsame Präfix aller vier ist ebenfalls 316 Zeichen lang). Die drei anderen
tragen einen szenariospezifischen Zusatz. Die 48 Zusagen von
`test_rahmen_traegt_begruendung.py` fangen das nicht — es ist genau das «leere
Feld in sechs Monaten», gegen das der Wächter angetreten ist. Er braucht eine
Zusage «der Vorbehalt geht über den Baustein hinaus».

**B7b — eine Quellenangabe zeigt ins Leere.** Zwei Rahmen zitieren
`docs/research/studies_future/evolution-of-alternative-fuels-for-aviation.pdf`;
im Repo heißt die Datei `…-for-aviation.pdf.coredownload.inline.pdf`. Der
Wächter prüft nicht, ob die genannten Pfade existieren.

**B7c — Trennschärfe der Grounding-Prüfung.** `pruefe_gegen_kontext` hält jede
Zahl der Antwort gegen **alle** Zahlen des Kontextblocks, ohne Bezug zur Größe,
und akzeptiert zusätzlich `wert × 100` bzw. `wert / 100`; 0–10 und 100 sind
ohnehin ausgenommen. Die Zusage ist korrekt eng formuliert («steht diese Zahl in
den Laufdaten»), aber die Trennschärfe sinkt mit der Länge des Blocks: Eine
erfundene Zahl, die irgendwo im Kontext vorkommt, gilt als belegt. **Kein
Fehler, eine Grenze** — sichtbar machen ließe sie sich, indem `Antwort` die Zahl
der Kontextzahlen mitführt.

**B7d — `resolve_market_feedback_config` hat sieben Literal-Rückfälle.** *(Behoben am 2026-09-03: `_FELDER` setzt nur, was eine Regel wirklich nennt; alles andere füllt `MarketFeedbackConfig`. Die ausgelieferte 0,25 gilt, der Test sagt es, und der dritte `--deselect` in der CI ist weg.)*
`0.37`, `0.08`, `0.08`, `0.85`, `0.6`, `0.33` und seit P2.8-B `"auslastung"`
stehen dort neben denselben Vorgabewerten in `MarketFeedbackConfig`. Zwei
Quellen für denselben Wert — dieselbe Klasse, die P1.9-W5.1 im Dashboard und
P2.1 in `booking_probability` abgeräumt haben, und die Ursache des seit Monaten
roten Tests (`0.33` gegen `0.25` aus der Config). P2.8-B hat `strategie` in
genau dieses Muster eingefügt, statt es aufzulösen.

**B7e — die Lebenszyklus-Kurve ist nicht symmetrisch, ihre Quelle behauptet
es.** `gipfel_breite.quelle` sagt, der Wert «ergibt bei 18 und 90 Jahren rund
ein Fünftel des Gipfelwerts». Gemessen: **0,206** bei 18 — und **0,085** bei 90,
also eher ein Zwölftel. Und die Feinstruktur der veröffentlichten
Altersgruppen-Tabelle ist Rauschen: Bei n = 5000 liegen 36–50 bei 56,9 % und
51–65 bei **57,8 %**; der Plan führt 57,8 % und 54,7 %, also mit umgekehrter
Ordnung. Die Aussage «die Lebensmitte fliegt am meisten» hält, die Rangfolge
innerhalb der Mitte nicht.

**B7f — 3,9 % der Bevölkerung sind exakt 18 Jahre alt.** Die P2.9-Doku beziffert
nur die obere Klemme (1,6 %, reproduziert). Zusammen sind 5,5 % der Masse
geklemmt — deutlich unter dem 10-%-Deckel und kein Fehler, aber die untere Zahl
gehört genannt, weil sie dieselbe Frage betrifft.

### B8 · Effizienz — 63 % des Bevölkerungs-Ticks sind Objektkopien 🔷 **klein**

cProfile, 10 Ticks, 1000 Personen, Standardkonfiguration:

| Posten | Zeit | Anteil |
| --- | ---: | ---: |
| `pydantic.model_copy` (30 000 Aufrufe) | 0,316 s | **63 %** |
| `booking_probability` (10 000 Aufrufe) | 0,020 s | 4 % |
| alles übrige | 0,162 s | 33 % |

Ein Bevölkerungs-Tick kostet **21,1 ms**. Die Bevölkerung wird pro Tick
**dreimal** vollständig kopiert (`apply_factor_shifts`, `update_income_factors`,
Sättigungsabbau, `evaluate_booking`), bei greifender Kapazitätsschranke ein
viertes Mal. **Das eigentliche Modell ist 4 % der Rechenzeit.**

Keine Regression von Phase 2 — aber P2.6 macht es relevant: 400 Läufe
(50 Wiederholungen × 8 Szenarien) sind gemessen 4,3 bis 11,7 Minuten, und zwei
Drittel davon sind Kopien. Der billigste Hebel wäre In-Place-Mutation innerhalb
eines Ticks oder Merkmale als Arrays statt als Modell je Person.

**Entwarnung an einer Stelle:** `pruefe_verteilung` (P2.9) zieht 4000 Werte je
Merkmal vor jedem Bevölkerungsaufbau, mit eingeschalteter Erneuerung also in
jedem Tick. Gemessen kostet das **1,08×** — die Vorabziehung ist kein Problem.

---

## Teil C — Doku, Wächter und Prozess

### C1 · README.md trägt vier Aussagen, die der Code nicht deckt 🔶

- **Z. 3:** «CIB-Konsistenzfilter **nach Weimer-Jehle**» — genau die
  Formulierung, die das eigene Glossar untersagt («Bis P2.2 umgesetzt ist, nicht
  als *Algorithmus nach Weimer-Jehle* bezeichnen»). P2.2 hat entschieden, die
  Impact Balance **nicht** zu implementieren; die Zuschreibung ist damit
  dauerhaft falsch, nicht mehr nur vorläufig.
- **Z. 7:** «jeder Lauf erzeugt automatisch ein Tripleset aus Trendfortsetzung,
  Strukturwende und Krisenkonflikt» — unverändert seit vor P2.0, obwohl P2.0
  ausdrücklich festhält, dass diese Produktaussage mitzieht.
- **Z. 228:** «LLM wählt 3 CIB-Kandidaten» — auf der ausgelieferten Matrix ist
  es **einer**.
- **Der Backtest kommt in README gar nicht vor**, obwohl P2.6 und P2.7 ihn dort
  unter «Doku zieht mit» führen. Das ist die Zusage, nach der ein Fachprüfer
  zuerst sucht, und sie steht im Einstiegsdokument nicht.

### C2 · Zwei Oberflächentexte beschreiben abgeschaffte Bedienung 🔶

- [`dashboard/web/pages/docs_reference.py:88–95`](../dashboard/web/pages/docs_reference.py)
  — das Referenzkapitel «Faktoren», im Dashboard sichtbar: «Welche Kombination
  Sie wählen, legen Sie unter «Simulation starten» im Tab
  **«Rahmenbedingungen»** fest.» Der Schritt existiert seit P1.9-W3.1/P2.0-C
  nicht mehr. Direkt daneben: Widersprüchliche Kombinationen «tauchen im
  Szenario-Tripleset typischerweise als Spannungs-Szenario auf» — die
  Bewertungslesart, die P2.0-A abgeschafft hat.
- [`dashboard/web/config_editor/wizard.py`](../dashboard/web/config_editor/wizard.py),
  `STEPS[0]`: «Ein vorbereitetes Szenario … legt **Faktorlage**, Politik und
  Kosten in einem Zug fest.» Die Faktorlage legt es seit P2.0-C nicht mehr fest
  (`factor_overrides: []` in allen acht Dateien, `apply_sweep_overrides` wendet
  sie nicht an).

Beides ist Text, den ein Nutzer im laufenden Produkt liest — nicht Doku daneben.

### C3 · Sechs veraltete Messwerte 🔷

Der Durchgang vom 2026-09-02 (`9a5f72c`) hat sechs veraltete Messwerte gefunden
und ersetzt. Diese hier sind noch da:

| Behauptung | Fundstelle | Ist |
| --- | --- | --- |
| «die Zielreihe schwankt saisonal um 40 Indexpunkte, das Modell um **12**» | CLAUDE.md (Architektur-Map), `phase2_bilanz.md` | 39,8 / **17,9** (Preis), 75,9 / **28,9** (Nachfrage) |
| «Zielreihe **34**, Modell **14**» | `src/backtest/auswertung.py`, Moduldocstring | dieselben Werte wie oben |
| «Einkommenselastizität **+1,10**» | CLAUDE.md, Projektplan P2.8 | **+0,69 … +0,75**, und es ist keine Elastizität → **B5** |
| «bei 18 und 90 Jahren rund ein Fünftel» | `property_models.AltersProfil.gipfel_breite.quelle` | 0,206 / **0,085** → **B7e** |
| Altersgruppen 36–50 (57,8 %) > 51–65 (54,7 %) | Projektplan P2.4 | bei n = 5000 umgekehrt, Unterschied im Rauschen |
| `tests/test_bevoelkerung_altert_nicht.py` «hält P2.4 fest» | CLAUDE.md, Präsens | Datei ist gelöscht — drei Aufzählungspunkte später steht das auch |

### C4 · `docs/audit_findings.md` verletzt seine eigene Pflegeregel fünfmal 🔶

Die Regel steht in CLAUDE.md **und** in der Datei selbst: «Ein behobenes Finding
wird hier **entfernt**, nicht abgehakt — die Liste zeigt immer nur den offenen
Stand.» Offen gelistet sind trotzdem:

1. **`_booking_probability` vergleicht gegen 0,5** — mit P2.1 behoben, die
   Funktion heißt heute `booking_probability` und zieht.
2. **`_seed_runtime` seedet den globalen Zustand** — mit P2.1 entfernt; im Code
   steht nur noch der erklärende Kommentar.
3. **`entries: []` in `cib_frozen.json`** — mit P2.3-Rest entfernt, nachgeprüft.
4. **`metadata.source = expert_defined_aviation_domain_v2`** — heißt heute
   `beleg_keine_bewertende_rolle`; das Finding ist inhaltlich falsch geworden
   und trägt eine Aussage weiter, die P2.3-Rest ausdrücklich korrigiert hat.
5. Das **Alters-/Sampling-Finding** ist inline als «behoben» **abgehakt statt
   entfernt** — genau der Fall, den die Regel wörtlich ausschließt.

Der Grund, warum das mehr ist als Aufräumen, steht in derselben Datei: «Ein
stehengelassenes Finding ist keine harmlose Altlast: Es verbreitet weiter, was
sein Paket längst korrigiert hat.»

**Dazu:** Eine Leerzeile vor der Zeile `dashboard/web/theme.py` bricht die
Dashboard-Tabelle in drei getrennte Tabellen auf.

### C5 · P2.0-C hat den Browser-Wächter rot gemacht — seit dem 2026-08-30 ⛔ **schwer**

Vollständiger Lauf: **7 failed, 1549 passed, 1 skipped, 2 deselected** (19:24 min).
`ruff` und `black` sind grün. Alle **Phase-2-Wächter sind grün** — 270 Zusagen
in den fünfzehn Dateien, die zu Phase 2 gehören.

**Sechs der sieben Fehlschläge stehen in `tests/test_web_overflow.py`, und alle
sechs gehen auf P2.0-C zurück:**

| Test | Meldung | Ursache |
| --- | --- | --- |
| `test_no_step_grew_beyond_its_ratchet` `[1280px]`, `[1024px]` | «Bei 1280 px nicht gemessen: `['Schritt 7']`» | `DECKEL` führt **Schritt 1–7**; `wizard.STEPS` hat seit P2.0-C **sechs** Schritte. Die Sperrklinke wurde nicht mitgezogen. |
| `test_no_line_runs_longer_than_the_eye_can_follow` `[1280px]`, `[1024px]` | «Was soll gerechnet werden?: **89 Zeichen** in P — *Ist der Schalter aus, bleiben alle Anpas…*» (bei 1024 px: 81) | Genau der Text des `apply_custom_overrides`-Schalters, den **P2.0-C nach Schritt 1 verschoben** hat. Er steht außerhalb des `af-mass`-Deckels; zugesagt sind ≤ 75 Zeichen (P1.9-W5.4). |
| `test_the_width_guard_would_notice_a_relapse` `[1280px]`, `[1024px]` | `assert (96.7 >= 60.0 and 89 <= 75)` | Die Vorbedingung des Selbsttests: Er kann keinen Rückfall nachstellen, solange der Ist-Stand schon außerhalb liegt. |

**Warum es niemand gemerkt hat, und das ist der eigentliche Befund:** Der
Wächter ist opt-in (Extra `ui` plus Chromium) und überspringt sich sonst
schweigend; die CI hat keinen Browser. Die Zusagen «kein Schritt ist höher als
sein Deckel» und «keine Zeile läuft über 75 Zeichen» sind damit seit dem
2026-08-30 ungeprüft, und die Commit-Regel «Test und Doku im selben Commit»
wurde bei P2.0-C für genau den Wächter nicht eingehalten, der die Schrittfolge
misst.

> **Behoben noch am 2026-09-03.** Und beide Hälften anders als vermutet: Die
> Zeilenlänge war kein Textproblem — `ui.explainer` rendert **jede**
> Glossar-Erklärung ohne Lesemaß, P2.0-C hat es nur sichtbar gemacht. Der
> Deckel ist nachgemessen (1280 px: 1,00 / 1,34 / 1,00 / 1,00 / 1,22 / 1,02 /
> 1,45), und der Zuwachs auf Schritt 1 kommt **vollständig** vom zugezogenen
> Schalter, nicht vom neuen Lesemaß: Mit und ohne `af-mass` misst der Schritt
> dieselben 1,34, weil der Erklärungskörper zugeklappt keine Höhe trägt.

Der siebte Fehlschlag ist der bekannte Dauerläufer
`test_market_feedback.py::TestM413ConfigurablePrice::test_market_rules_resolve_marginal_cost_fraction`
(0,25 gegen 0,33). Er ist **kein Testproblem**, sondern die doppelte Wertquelle
aus **B7d**.

---

## Teil D — Das Artefakt «Bilanz der Modellsubstanz»

Geprüft wurde zusätzlich das nach außen gereichte Artefakt
(`claude.ai/code/artifact/527ff171-…`, Stand **31. August 2026**), weil es die
Fassung ist, die ein Dritter zu sehen bekommt. Es fasst dieselben zehn Pakete
zusammen wie [`phase2_bilanz.md`](phase2_bilanz.md), in anderer Sprache und mit
eigener Kennzahlenzeile.

**Was daran gut ist:** Die Backtest-Kette (1,84 / 21,76 → 1,29 / 21,81 →
1,27 / 23,43 → 3,09 / 18,13) stimmt mit dem Projektplan und mit dem aktuellen
`backtest_vorlauf.md` überein. Der Abschnitt «Wo man ausbessern könnte» nennt
sieben offene Punkte ehrlich beim Namen, darunter die Kapazitätsreihe, die
fehlende Saison und die Tickdauer. Und die Fußzeile sagt richtig: «Die jeweils
gültigen Backtest-Werte stehen im Vorlauf-Bericht, nicht hier.»

**Fünf Befunde:**

### D1 · «Das Modell ist geeicht» ist die falsche Vokabel ⛔ **schwer, Außendarstellung**

Die Überschrift zu P2.7 lautet **«Das Modell ist geeicht»**, und der
hervorgehobene Schlusssatz verstärkt es: «Genau das ist der Zweck einer
Eichung.»

**Geeicht wurde nichts.** Kein einziger Koeffizient wurde an Daten angepasst —
P2.1 hält ausdrücklich fest: «Keiner der acht Werte ist an Daten geprüft», und
P2.7 selbst schreibt: «Der Backtest sagt, **wo** das Modell trägt und wo nicht;
er macht es nicht richtig.» Was stattfand, ist ein **Vergleich mit unabhängigen
Reihen** — wertvoll, aber etwas anderes. Ein Fachprüfer liest «geeicht» als
«kalibriert» und sucht danach die Schätzung, die es nicht gibt.

**Fairerweise:** Die Formulierung ist **nicht im Artefakt erfunden** — der
Projektplan trägt sie im Vorspann von P2.7 wörtlich («Das Modell ist geeicht —
und das Ergebnis ist zweigeteilt»). Das Artefakt hat sie zur Überschrift
befördert. Und die Erwartung stand noch eine Stufe früher: Die Einleitung von
`CLAUDE.md` versprach «geeicht wird erst mit P2.7». Nach dem Lauf wurde aus der
Erwartung eine Behauptung — niemand hat sie erfunden, sie ist durchgereicht
worden.

> **Im Repo behoben am 2026-09-03.** Drei Stellen: die Einleitung von `CLAUDE.md`
> (das Versprechen), die Architektur-Map (`src/backtest/` heißt jetzt «der
> Vergleich», nicht «die Eichung») und der Vorspann von P2.7 («zum ersten Mal an
> etwas gemessen, das nicht aus ihm selbst stammt»). `README.md` trug die
> Korrektur schon aus **C1**.
>
> **Das Artefakt bleibt offen, und zwar nicht aus Nachlässigkeit:** Es ist mit
> Haiko *geteilt*, nicht sein eigenes — es lässt sich von hier aus nicht ändern.
> Solange es die Überschrift «Das Modell ist geeicht» trägt, widerspricht die nach
> außen gereichte Fassung dem Repo. Das gehört zu **D2** und **D3** in einem
> Aufwasch zurück an Manu.

### D2 · «10 / 10 Pakete abgeschlossen» stimmt nicht mit dem eigenen Plan überein 🔶

Die Kennzahlenzeile sagt **10 / 10**. Der Projektplan führt P2.8 als
**⚠️ teilweise** — der Trajektorien-Horizont ist ausdrücklich offen. Das
Artefakt weiß das sogar: Sein Kasten «Kurven enden vor dem Lauf, und nichts sagt
es» beschreibt exakt diese Restposition. Der Zähler und der Inhalt derselben
Seite widersprechen sich. Richtig wäre **9 + 1 offen**.

### D3 · Die Testzahl ist eine feste Zahl in der Doku — genau das, was P4.3 untersagt 🔷

«**1 473** Tests, davon **254** für Phase 2», datiert 31. August. Heute
gemessen: **1 559** eingesammelt, davon **270** in den fünfzehn
Phase-2-Dateien. Beide Zahlen sind binnen drei Tagen um rund 6 % gewandert —
und CLAUDE.md sagt zu genau diesem Fall: «die genaue Zahl liefert
`pytest --collect-only -q`, sie gehört bewusst **nicht** als feste Zahl in die
Doku» (P4.3).

**Und die wichtigere Hälfte fehlt:** Eine Testzahl als Qualitätssignal auf einer
Seite, die nach außen geht, ohne den Hinweis, dass **sieben davon rot sind** —
darunter sechs seit dem 30. August (siehe **C5**) —, sagt mehr, als sie belegen
kann.

### D4 · «Die Angebotsseite existiert» und «Die Bevölkerung ist plausibel» überziehen 🔶

- **«Die Angebotsseite existiert»** — die Größe existiert, ihre zugesagte
  Wirkung nicht: Unter `marge` ist die Kapazität im Betriebspunkt wirkungslos,
  unter `auslastung` erzwingt sie einen Preisverfall, und die Rationierung
  sättigt die Abgewiesenen (**B1**, **B2**). Dazu setzt sie **kein
  ausgeliefertes Szenario** (**B6**).
- **«Die Bevölkerung ist plausibel»** — behoben sind die stille Klemmung und die
  Quelle der Altersverteilung. Ob die Bevölkerung als Bild **Flugreisender**
  plausibel ist, sagt P2.9 ausdrücklich **nicht**: Genommen ist bewusst die
  Gesamtbevölkerung, «wer davon fliegt, soll das Modell ergeben». Die Überschrift
  behauptet mehr als das Paket.

### D5 · Eine zweite Synthese ohne Eigentümer 🔷

`phase2_bilanz.md` warnt in eigener Sache: «Eine Übersicht, die zur zweiten
Wahrheit wird, ist schlimmer als keine» — und trägt deshalb ein Datum, einen
Pflegehinweis und den Satz «Synthese, keine Quelle». Das Artefakt ist eine
**zweite** solche Übersicht, drei Tage älter, nach außen teilbar, im Repo nicht
verlinkt und in der Doku-Pflicht-Tabelle nicht vorgesehen. Nichts hält es
aktuell.

**Empfehlung:** entweder das Artefakt als Rendering von `phase2_bilanz.md`
führen (eine Quelle, ein Erzeugungsweg) oder ihm dieselbe Kopfzeile geben —
Datum, «Synthese, keine Quelle», und den Verweis auf den Vorlauf-Bericht, den es
in der Fußzeile schon hat.

---

## Teil E — Was ausdrücklich gut ist

Ein Audit ohne diesen Teil ergibt kein Bild. Vier Dinge tragen:

**Die Arbeitsweise ist der eigentliche Ertrag der Phase.** Vorher und nachher am
Backtest gemessen, mit unverändertem Verfahren. Das Ergebnis auch dann behalten,
wenn es schlechter wird — das Altersprofil hat die Nachfrageseite verschlechtert
(21,81 → 23,43) und wurde nicht zurückgebaut, weil der Mechanismus stimmt. Und
die Entscheidung «reales statt nominales BIP», die gegen das eigene Ergebnis
ging, mit dem Satz daneben: *Die Wahl nach dem Ergebnis zu treffen wäre genau
der Fehler, den dieses Paket vermeiden soll.* Das ist selten, und niemand sollte
es antasten.

**Die veröffentlichten Kernzahlen reproduzieren.** Unabhängig nachgerechnet:

| Kennzahl | veröffentlicht | nachgemessen |
| --- | ---: | ---: |
| Preiselastizität am Betriebspunkt | −1,27 | **−1,30** |
| Spanne über plausible Preise | −0,46 … −2,76 | **−0,46 … −2,80** |
| Anteil an der Altersobergrenze | 1,6 % | **1,6 %** |
| Altersmittel der Bevölkerung | 50,8 | **50,6** |
| Buchungsneigung 18–25 / 36–50 / 66+ bei 140 EUR | 25,2 / 57,8 / 36,2 % | **24,4 / 56,9 / 35,0 %** |
| Backtest, alle Kennzahlen | 3,09 / 23,27 / 18,13 / 58,76 | **identisch** |

Die einzige Abweichung von Belang ist die Einkommenselastizität (**B5**).

**Fünf Pakete sind sauber gebaut.** P2.1 (echte Ziehung mit eigenem Strom je
(Lauf, Tick), acht Koeffizienten mit erzwungener Herkunftsangabe und einem
Validator gegen Floskeln), P2.4 (Alter formt die Merkmale beim Ziehen statt als
Term im Nutzen — die richtige Modellierungsentscheidung, mit Begründung),
P2.9 (Klemm-Wächter über **jedes** Merkmal, nicht nur `age`, mit eigenem
Generator, damit die Prüfziehung den Lauf nicht verschiebt), P2.5 (Grounding mit
einer Zusage, die genau das behauptet, was sie prüft — und acht Ruhe-Fälle gegen
drei Alarm-Fälle im Wächter) und P2.6 (Median plus 80-Prozent-Intervall statt
min/max, Band nur so lang wie der kürzeste Lauf, fehlende Messung fällt heraus
statt als 0 einzugehen).

**Die Kohärenzbegründungen aus P2.2 sind echt.** Richtlinie (EU) 2023/958,
Verordnung (EU) 2023/2405 (ReFuelEU), die IATA-Net-Zero-Roadmaps und Rounsevell
et al. 2010 als Methodenbeleg — die PDFs liegen im Repo (bis auf **B7b**). Und
die Trennung «Storyline belegt, Bezifferung gesetzt» ist in jedem Vorbehalt
ausgesprochen.

**P2.3-Rest ist vorbildlich abgeschlossen:** Erzeuger mitgeändert statt nur die
Datei, zur Probe neu gebaut, und der Wächter prüft die *Zuweisung* von `source`
statt des bloßen Vorkommens des alten Labels — weil die neue Notiz es absichtlich
nennt.

---

## Befunde nach Schwere

| # | Befund | Schwere | Art | Betrifft |
| --- | --- | --- | --- | --- |
| **B1** | Rationierung sättigt die Abgewiesenen; Docstring behauptet das Gegenteil | ⛔ | Rechenfehler | P2.8-B |
| **B2** | «Mehr Plätze bei gleichem Preis» ist in keiner Strategie darstellbar | ⛔ | Zusage nicht eingelöst | P2.8-B |
| **C5** | Browser-Wächter seit dem 2026-08-30 rot (6 Fehlschläge), CI sieht es nicht | ⛔ | Wächter | P2.0-C |
| **D1** | «Das Modell ist geeicht» — geeicht wurde nichts | ⛔ | Außendarstellung | P2.7, Artefakt |
| **B3** | Tautologisches Basisjahr steckt in jeder Backtest-Kennzahl | 🔶 | Methodik | P2.7 |
| **B4** | Eingang und Ziel der Nachfrageseite aus derselben Eurostat-Tabelle | 🔶 | Methodik | P2.8 |
| **B5** | Einkommen wirkt als Schwelle; +1,10 ist heute +0,69 … +0,75 | 🔶 | Sachaussage | P2.8 |
| **B6** | Kein ausgeliefertes Szenario nutzt Kapazität, Strategie, Erneuerung | 🔶 | Produktwirkung | P2.8, P2.4-D/E |
| **A1** | P2.0 ✅ mit zwei offenen Abnahmeklauseln, eine davon messbar unerfüllbar | 🔶 | Plankonformität | P2.0 |
| **C1** | README: Weimer-Jehle, Tripleset, «3 Kandidaten», kein Backtest | 🔶 | Doku-Pflicht | P2.0, P2.2, P2.7 |
| **C2** | Zwei Oberflächentexte beschreiben abgeschaffte Bedienung | 🔶 | Doku-Pflicht | P2.0-A, P2.0-C |
| **C4** | `audit_findings.md` verletzt seine Pflegeregel fünfmal | 🔶 | Prozess | P2.1, P2.3 |
| **D2** | Artefakt zählt 10 / 10, der Plan führt P2.8 als teilweise | 🔶 | Außendarstellung | Artefakt |
| **D4** | «Angebotsseite existiert», «Bevölkerung ist plausibel» überziehen | 🔶 | Außendarstellung | Artefakt |
| **B7a** | `co2_delayed` trägt nur den Standard-Vorbehalt | 🔷 | Wächterlücke | P2.2 |
| **B7b** | Eine Quellenangabe zeigt auf einen nicht existierenden Pfad | 🔷 | Wächterlücke | P2.2 |
| **B7c** | Grounding vergleicht gegen alle Kontextzahlen ohne Bezug | 🔷 | Grenze | P2.5 |
| **B7d** | Sieben Literal-Rückfälle in `resolve_market_feedback_config` | 🔷 | Doppelte Quelle | P2.8-B, Altbestand |
| **B7e** | Lebenszyklus-Quelle behauptet Symmetrie, die nicht besteht | 🔷 | Messwert | P2.4 |
| **B7f** | 3,9 % an der Altersuntergrenze, nirgends beziffert | 🔷 | Messwert | P2.9 |
| **B8** | 63 % des Bevölkerungs-Ticks sind Objektkopien | 🔷 | Effizienz | Altbestand, durch P2.6 relevant |
| **C3** | Sechs veraltete Messwerte in CLAUDE.md, Bilanz, Docstrings | 🔷 | Doku-Pflicht | P2.4, P2.7, P2.8 |
| **D3** | Feste Testzahl im Artefakt, ohne die sieben roten zu nennen | 🔷 | Außendarstellung | Artefakt |
| **D5** | Zweite Synthese ohne Eigentümer und ohne Pflegehinweis | 🔷 | Prozess | Artefakt |

---

## Empfehlung zur Reihenfolge

**Zuerst, weil sie Zahlen verschieben und deshalb vor jede weitere Messung
gehören:**

1. **B1** beheben (Sättigung erst nach der Rationierung) und **B2** neu
   entscheiden — vermutlich braucht `marge` eine Kapazitätswirkung, die *nach
   oben* zeigt, sonst ist die Strategie für ihren Zweck untauglich. Beides mit
   Vorher/Nachher am Backtest, nach der Hausregel dieses Projekts.
2. **B3** korrigieren (Basisjahr aus der Kennzahl) und die vier Zahlen einmal
   nachziehen. Danach sind alle folgenden Messungen vergleichbar.

**Danach, weil sie Aussagen betreffen und keine Rechnung:**

3. **D1**, **C1**, **C2** — die Formulierungen, die nach außen gehen.
4. **A1** — das Abnahmekriterium von P2.0 durch die tragfähige Fassung ersetzen,
   Klausel 2 als Rest ausweisen.
5. **B4**, **B5** — die beiden Methodik-Abschnitte in P2.7 und P2.8 nachtragen.
6. **C3**, **C4**, **C5** — Doku-Pflege und der rote Wächter.

**Zuletzt, weil sie Arbeit sind und nichts blockieren:**

7. **B6** als eigenes Paket (ein Rahmenszenario, das die Angebotsseite wirklich
   benutzt — sonst bleibt P2.8 eine Backtest-Funktion).
8. **B7d** (doppelte Wertquelle, löst den dauerhaft roten Test mit auf),
   **B7a–c**, **B8**.

---

## Anhang — die Messskripte

Alle fünf laufen gegen `aff7d63` im aktivierten `.venv` und schreiben nichts ins
Repo. Sie sind der Beleg für **A1**, **B1**, **B2**, **B3**, **B5** und **B8**.

| Messung | Verfahren | Ergebnis |
| --- | --- | --- |
| **B1** — Sättigung nach Rationierung | ein `run_population_tick` mit `strategie="marge"`, `kapazitaet_index=0,5`, 1000 Personen, Seed 42; danach zählen, wie viele Nicht-Buchende `saturation_level > 0` tragen | 473 von 815 |
| **B2** — Wirkung der Kapazität | je ein 40-Tick-Lauf über `{0,3; 0,5; 0,7; 1,0; 1,3} × {marge, auslastung}`, Mittel von Rate und Preis im letzten Viertel | Tabelle in B2 |
| **B3** — Beitrag des Basisjahres | `docs/backtest_vorlauf.md` einlesen, mittleren absoluten Abstand einmal mit und einmal ohne 2015 bilden | Tabelle in B3 |
| **B5** — Elastizitäten | 5000 Personen aus `initialize_population`, `booking_probability` bei festen Preisen; Bogenelastizität über Preispaare, Einkommen über einen Faktor auf `income_factor` | Tabellen in B5 und E |
| **B8** — Laufzeit | 20 Ticks messen, 10 weitere unter `cProfile`, nach kumulierter Zeit sortiert | Tabelle in B8 |
| **A1** — Faktorlagen | 5 Seeds × {Standard + 4 Rahmen} × {20, 40} Ticks, Endzustände von F1–F7 vergleichen | 1 Lage je Kombination |

Die Skripte selbst liegen nicht im Repo — sie sind Wegwerfmessungen, keine
Wächter. **Was daraus ein Wächter werden sollte**, steht bei **B1** und **B2**:
eine Zusage, die den Zustand der Abgewiesenen prüft, und eine, die «mehr
Kapazität ⇒ mehr Verkehr bei gleichem Preis» misst.
