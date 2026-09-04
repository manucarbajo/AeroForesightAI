# Entscheidung: die Angebotsseite

**Stand 2026-08-31 · Weg A entschieden und gebaut (siehe Nachtrag unten) · Grundlage für [P2.8](projektplan.md#p28--die-nachfrage-kann-nicht-wachsen--erledigt-2026-09-03-weg-a-2026-08-31)**

Der Backtest hat auf der Nachfrageseite einen Fehlschlag gemessen: Das Modell
lässt die Nachfrage bis 2019 auf **86** fallen, real stiegen die europäischen
Fluggastzahlen auf **126**. Nicht ungenau — verkehrt herum.

Die naheliegende Erklärung ist ausgeräumt. `income_index` wird seit P2.8 aus dem
realen EU-BIP gespeist, der Kanal ist korrekt geformt (Einkommenselastizität
+1,10), und er trägt **1,6 von 40** fehlenden Prozentpunkten bei. Auch das
Altersprofil aus P2.4 hat die Nachfrageseite nicht gerettet.

Beim Nachmessen der Ursache kam etwas anderes heraus, und es ist grundsätzlicher
als «dem Modell fehlt ein Nachfragetreiber»:

> **Die Nachfragehöhe des Modells ist eine Konfigurationskonstante, kein
> Ergebnis.** Sie folgt der Zielauslastung des Anbieters (`target_booking_rate`),
> nicht den simulierten Konsumenten. Wer die Konstante ändert, ändert die
> Nachfrage; wer die Konsumenten ändert, kaum.

Diese Vorlage legt die Messungen offen, benennt drei Wege und empfiehlt einen.
Sie war als Entscheidungsgrundlage geschrieben; **Weg A ist am selben Tag gebaut
worden**, der Nachtrag am Ende trägt das Ergebnis.

---

## Die Grundlage, nachgemessen

Alle Zahlen am 2026-08-31 an der ausgelieferten Konfiguration gemessen,
Standardlauf über 40 Ticks, Mittel über das letzte Viertel.

### 1. Die Buchungsrate folgt der Zielauslastung

`configs/properties.json` enthält eine Regel `provider_yield_feedback`: Der
Anbieter passt seinen Aufschlag je Tick an, bis die Buchungsrate ihre
**Zielrate** erreicht. Ausgeliefert steht sie auf `0.37`.

Ändert man nur diese eine Zahl:

| `target_booking_rate` | Buchungsrate | Ticketpreis |
| ---: | ---: | ---: |
| 0,25 | 0,1875 | 141,90 |
| 0,37 *(ausgeliefert)* | 0,2539 | 118,12 |
| 0,50 | 0,3100 | 97,61 |
| 0,65 | 0,3715 | 75,99 |

Die Buchungsrate verdoppelt sich, der Preis halbiert sich. **Das ist keine
Marktreaktion, das ist ein Regler.** Der Anbieter senkt den Preis, bis genug
Menschen buchen — und weil er keine Kapazitätsgrenze hat, kann er das beliebig
weit tun.

### 2. Ein Nachfrageimpuls kommt dagegen kaum an

Dieselbe Konfiguration, Zielrate fest auf 0,37, nur das Einkommensniveau
verschoben:

| `income_index` | Buchungsrate | Ticketpreis |
| ---: | ---: | ---: |
| 0,9 | 0,2519 | 112,57 |
| 1,0 | 0,2539 | 118,12 |
| 1,2 | 0,2599 | 123,65 |
| 1,4 | **0,2655** | 124,76 |

**Vierzig Prozent mehr Einkommen ergeben 4,6 Prozent mehr Buchungen.** Der Rest
verschwindet im Preis, der um 5,6 Prozent steigt. Gemessen ist die Zielrate rund
**zwanzigmal** so wirksam wie das Einkommen.

### 3. Deshalb reicht kein Nachfragekanal, den man dazubaut

Das erklärt, warum P2.8 im ersten Anlauf nicht weiterkam. Der Einkommenskanal
ist da, er ist richtig geformt, und er trägt trotzdem 1,6 von 40 Punkten — weil
zwei Drittel seiner Wirkung sofort über den Preis wegbesteuert werden. Jeder
weitere Nachfragetreiber würde denselben Weg nehmen.

Statisch, ohne Rückkopplung, hätte der Einkommenskanal **+9,8 %** gebracht; im
Lauf kamen **+3,0 %** an.

### 4. Real war es umgekehrt, und das ist der Kern

Der europäische Luftverkehr wuchs 2015–2019 um **26 %**, während die Realpreise
ungefähr **flach** blieben. Beides zusammen geht nur, wenn das *Angebot* wächst:
mehr Sitzplätze, mehr Strecken, mehr Wettbewerb. Genau das war das Jahrzehnt der
Billigflieger-Expansion.

Im Modell ist diese Kombination **unmöglich**. Mehr Nachfrage heißt dort
zwangsläufig höherer Preis, weil ein einziger Anbieter über den Preis seine
Zielauslastung hält. Wachstum bei konstantem Preis hat keine Darstellung.

### 5. Die Zielrate ist ungeeicht und trägt keine Herkunft

`0.37` steht ohne Quelle in der Config. Zum Vergleich: Reale Sitzladefaktoren
europäischer Fluggesellschaften lagen 2015–2019 bei **rund 83 bis 85 Prozent**.
Die beiden Zahlen messen nicht dasselbe — die Buchungsrate des Modells ist der
Anteil einer Personenstichprobe, der in einem Tick bucht, nicht die Auslastung
eines Flugzeugs. **Aber genau das ist das Problem:** Eine Größe, die den
wichtigsten Ausgabewert des Modells festlegt, hat weder eine Quelle noch eine
klare Entsprechung in der Wirklichkeit.

---

## Was daraus folgt

**Der Befund ist nicht «es fehlt eine Kapazitätsgrenze».** Er ist schärfer: Das
Modell hat die Rollen vertauscht. Der Anbieter bestimmt die Nachfragemenge, die
Konsumenten liefern nur die Streuung darum herum.

Für das Produkt heißt das zweierlei:

- **Nachfragezahlen sind keine Mengenprognose.** Das steht seit P2.8 im
  Handbuch, und diese Messung sagt, warum: Sie sind eine Umsetzung der
  eingestellten Zielauslastung.
- **Wirkungsrichtungen bleiben belastbar** — «CO₂-Abgabe hoch, Preis hoch,
  Nachfrage runter» stimmt. Nur das *Niveau* der Nachfrage ist gesetzt.

Der Backtest bleibt dabei der Maßstab: Was hier auch gebaut wird, wird **vorher
und nachher** mit unverändertem Verfahren gemessen. Die heutigen Werte stehen in
[P2.7](projektplan.md#p27--backtest-gegen-20152024--erledigt-2026-08-30).

---

## Die drei Wege

### A — Kapazität als exogene Systemgröße

Eine Größe `kapazitaet` (verfügbare Sitzplätze) mit Verlauf, wie `income_index`
und `altersmittel_jahre`. Der Anbieter kann seinen Preis nur so weit senken, wie
Kapazität da ist; wächst sie, kann Nachfrage bei konstantem Preis wachsen.

- **Kosten:** klein. Eine Systemgröße, eine Schranke in der Preisregel, ein
  Wächter. Ein bis zwei Tage.
- **Was es löst:** Die reale Kombination «Wachstum bei flachen Preisen» wird
  darstellbar. Ein Rahmenszenario kann Kapazitätsausbau oder -knappheit
  vorgeben, und das ist eine der zwei, drei Fragen, die eine Strategieabteilung
  im Luftverkehr wirklich umtreibt.
- **Was es nicht löst:** Die Kapazität ist dann eine *Annahme*, keine Reaktion.
  Ein Anbieter, der bei hoher Nachfrage investiert, entsteht nicht.
- **Belegbarkeit:** brauchbar, aber schwächer als hier zunächst behauptet.
  **Korrektur vom 2026-08-31:** Der Satz lautete «Eurostat und IATA weisen
  Sitzplatzkapazität aus» — für Eurostat stimmt das auf dieser Ebene **nicht**.
  Verfügbar sind gewerbliche Passagier**flüge** (`avia_paoc`, `CAF_PAS`),
  monatlich; Sitze pro Flug und Auslastung fehlen. Der Näherungswert
  unterschätzt das Kapazitätswachstum deshalb systematisch (Flüge +14,5 % von
  2015 auf 2019, Passagiere +26,3 %). Siehe den Nachtrag unten — genau dieser
  Unterschied erklärt, warum die Nachfrageseite nach der Pandemie schlechter
  wird.

### B — Kapazität als Entscheidung des Anbieters

Wie A, aber der Provider baut Kapazität auf, wenn seine Auslastung dauerhaft
hoch ist, und ab, wenn sie niedrig ist — mit Verzögerung, weil Flugzeuge nicht
über Nacht kommen.

- **Kosten:** mittel bis groß. Eine Investitionslogik mit Vorlauf, und damit ein
  zweiter Regelkreis neben dem Preis. Zwei Regelkreise, die aufeinander wirken,
  schwingen leicht — das ist zu dämpfen und zu prüfen.
- **Was es löst:** Der Zyklus, der den Luftverkehr prägt: Nachfrage steigt →
  Preise steigen → Kapazität wird bestellt → kommt verspätet → Überkapazität →
  Preisverfall.
- **Was es nicht löst:** Es bleibt **ein** Anbieter. Wettbewerb, der Preise
  drückt, entsteht nicht.
- **Belegbarkeit:** schwächer. Vorlaufzeiten und Investitionsschwellen sind
  gesetzt, nicht geschätzt — dieselbe Lage wie bei den Buchungskoeffizienten.

### C — Mehrere Anbieter

Zwei oder drei Anbieter mit eigenen Kosten und eigener Preissetzung; die
Konsumenten wählen. Der Preis entsteht aus Wettbewerb statt aus einem Zielregler.

- **Kosten:** groß. Das ist ein anderes Marktmodell, kein Zusatz — die
  Buchungsentscheidung wird eine Wahl *zwischen* Anbietern, die
  Agentenarchitektur und jede Auswertung ändern sich mit.
- **Was es löst:** Die Preisbildung wäre erstmals ein Ergebnis. Die Frage
  «was passiert, wenn ein Wettbewerber die Route aufgibt» würde beantwortbar.
- **Was es nicht löst:** Ohne Kapazität schwebt auch der Wettbewerb frei.
  Braucht A ohnehin.
- **Belegbarkeit:** die Struktur ist Standard (Oligopolmodelle), die
  Parametrisierung wäre wieder gesetzt.

---

## Empfehlung: A, und zwar allein

**Weg A, ohne B oder C daneben** — aus drei Gründen.

**Erstens ist A die Voraussetzung für beide anderen.** Sowohl der
Investitionszyklus als auch der Wettbewerb brauchen eine Kapazitätsgröße, an der
sie ansetzen. Wer B oder C zuerst baut, baut A implizit mit und schlechter.

**Zweitens ist A der einzige Weg, dessen Wirkung sich am Backtest messen lässt.**
Kapazität ist als Reihe beschaffbar; ein Lauf mit historischer Kapazität gegen
einen ohne sagt, wie viel von den 40 fehlenden Punkten daran hing. Bei B und C
gibt es keine historische Reihe, gegen die man die Mechanik halten könnte — man
baut und hofft.

**Drittens beantwortet A die Frage, die das Produkt stellt.** «Was passiert mit
der Nachfrage, wenn die CO₂-Abgabe steigt und gleichzeitig die Kapazität
knapper wird» ist eine Szenariofrage. «Wann bestellt eine Airline Flugzeuge»
ist eine Frage der Unternehmensplanung — ein anderes Produkt.

**Was zu A gehört, damit es nicht auf halber Strecke stehen bleibt:**

1. **Die Zielrate bekommt eine Quelle oder verschwindet.** Solange `0.37` ohne
   Herkunft dasteht und den wichtigsten Ausgabewert festlegt, ist jede
   Nachfragezahl eine Setzung. Mit einer Kapazitätsschranke könnte die Zielrate
   entfallen — der Anbieter füllt dann, was er hat.
2. **Der Backtest wird vorher und nachher gerechnet**, mit unverändertem
   Verfahren, und beide Zahlen stehen nebeneinander im Plan.
3. **Nicht nachjustieren.** Wenn A die Lücke nur halb schließt, ist das das
   Ergebnis. Eine Kapazitätskurve, die auf den Backtest hin eingestellt wird,
   macht ihn wertlos.

---

## Nachtrag: Weg A ist gebaut (2026-08-31, am selben Tag)

`kapazitaet_index` skaliert die Zielauslastung, Standard 1,0 — nachgeprüft, dass der
Backtest damit exakt dieselben Zahlen liefert wie vorher. Ein Rahmenszenario kann die
Kapazität jetzt vorgeben, und der Backtest bekommt sie aus echten Daten.

**Die Reihe ist ein Näherungswert, und das ist die wichtigste Einschränkung:** Eurostat
veröffentlicht auf dieser Ebene keine Sitzplätze, gezählt sind **Flüge** (`CAF_PAS`).
Kapazität ist aber Flüge × Sitze × Auslastung. Real wuchsen die Flüge 2015–2019 um
14,5 %, die Passagiere um 26,3 %.

**Das Ergebnis, mittlerer Abstand:**

| | vorher | mit Kapazität |
| --- | ---: | ---: |
| Preis gesamt | 14,78 | **10,66** |
| Preis 2022–2024 | 37,31 | **23,27** |
| Nachfrage 2015–2019 | 23,43 | **18,13** |
| Nachfrage 2022–2024 | 34,38 | 58,76 |

Zwei Verbesserungen, eine Verschlechterung — und die Verschlechterung ist der Näherungswert
selbst: Das Modell folgt jetzt treu den Flügen (2024: 107,6) und verfehlt damit die
Passagiere (128,4). **Dass es dem Näherungswert folgt, ist der Beleg, dass die Mechanik
greift.** Die nächste Verbesserung ist eine Datenfrage — eine Sitzplatzreihe —, keine
Parameterfrage. Nachjustiert wurde nichts.

**Was damit nicht erledigt ist:** Weg A ist keine Kapazitäts*schranke*. Der Anbieter kann
seinen Preis weiterhin beliebig senken, er zielt nur auf ein anderes Füllniveau. Weg B
(Investitionszyklus) und Weg C (mehrere Anbieter) stehen unverändert offen und bauen
darauf auf.

## Zweiter Nachtrag: eine Methodik ist ein Bias (2026-08-31)

**Weg A allein war zu eng**, und der Einwand kam von außen: «Es kann ja auch mal mehr
Plätze geben, aber gleich teuer bleiben. Wenn wir nur eine Methodik haben, hat das System
einen Bias und es wird nicht abgenommen.»

Die Messung von Weg A bestätigt es: Kapazität 0,8 → Preis 136,19; Kapazität 1,5 → Preis
88,63. **Mehr Plätze erzwangen einen niedrigeren Preis.** Damit war ausgerechnet die reale
Lage 2015–2019, um derentwillen Weg A gebaut wurde, weiterhin nicht darstellbar.

**Die Preisstrategie ist deshalb jetzt eine Wahl** (`auslastung` / `marge`), nicht eine
Annahme. Unter `marge` hält der Anbieter seinen Aufschlag, die Kapazität wirkt als
Schranke statt als Ziel, und der Preis bleibt stehen, wenn Plätze dazukommen:

| Kapazität | `auslastung` Rate / Preis | `marge` Rate / Preis |
| ---: | --- | --- |
| 0,5 | 0,1529 / 159,42 | 0,1063 / **189,78** |
| 1,0 | 0,2587 / 118,85 | 0,1064 / **189,78** |
| 1,3 | 0,3052 / 100,50 | 0,1064 / **189,78** |

Der Standard bleibt `auslastung` — der Backtest liefert unverändert 10,66 / 33,36. Eine
neue Wahlmöglichkeit darf nichts verschieben, solange niemand wählt.

**Zwei Entscheidungen dabei, beide bewusst.** Die Kapazität ist nur unter `marge` eine
Schranke — unter `auslastung` steuert der Preis ohnehin auf sie zu. Und **wer keinen Platz
bekommt, wird zufällig gewählt**: Eine Auswahl nach Zahlungsbereitschaft wäre eine
*zweite* stille Verhaltensannahme, und genau gegen solche steht dieses Paket.

**Das ändert auch die Einordnung der drei Wege oben.** Sie waren als *Alternativen*
geschrieben; richtig ist, dass Weg B und C weitere **Strategien** sind, keine Ersetzungen.
`STRATEGIEN` ist eine Liste, kein Schalter: Ein Anbieter mit Erlösmanagement (Marge weitet
sich bei Knappheit) oder mehrere Anbieter im Wettbewerb kommen als weitere Einträge dazu,
nicht als Umbau.

## Was diese Entscheidung nicht berührt

- **Die Preisseite des Backtests.** Sie traf vor der Pandemie auf 1,27
  Indexpunkte; A sollte sie nicht verschlechtern. **Gemessen hat es sie dort
  verschlechtert (3,09) und insgesamt verbessert (14,78 → 10,66)** — siehe den
  Nachtrag.
- **Die Szenarienschicht.** Variante C aus [P2.2](projektplan.md#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31)
  bleibt: Kapazität wäre ein weiterer exogener Verlauf im Rahmenszenario, mit
  Kohärenzbegründung wie die anderen.
- **Invariante 1.** Kapazität ist eine Zahl aus Python; kein Agent bestimmt sie.
- **Die offene Tick-Dauer** ([P3.8](projektplan.md#p38--was-ein-tick-bedeutet-ist-dreimal-verschieden-entschieden--neu-2026-08-31)).
  Eine Kapazitätskurve hängt daran wie jede zeitabhängige Größe — sie ist als
  exogener Verlauf in Ticks formulierbar, aber ihre Steigung ist erst
  interpretierbar, wenn die Tick-Dauer feststeht. **Das ist ein Argument, P3.8
  vorher zu entscheiden**, nicht eines gegen A.

---

## Quellen

- Messungen dieser Vorlage: `configs/properties.json`
  (`provider_yield_feedback`), Läufe über 40 Ticks im Modus «Nur Zahlen»,
  Seed 42, am 2026-08-31.
- Backtest-Ergebnisse: [P2.7](projektplan.md#p27--backtest-gegen-20152024--erledigt-2026-08-30),
  Rohdaten in `configs/backtest/` samt `quellen.json`.
- Einkommenselastizität und Preiselastizität: `tests/test_nachfragetreiber.py`,
  Maßstab Brons, Pels, Nijkamp & Rietveld (2002), *Journal of Air Transport
  Management* 8, 165–175 (im Repo unter `docs/research/literature/`).
- Reale Sitzladefaktoren: IATA Annual Review 2024
  (`docs/research/studies_future/iata-annual-review-2024.pdf`). **Nicht
  unmittelbar mit der Buchungsrate des Modells vergleichbar** — die Angabe steht
  hier als Größenordnung, nicht als Zielwert.
