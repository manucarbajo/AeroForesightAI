# Entscheidung: Rahmen statt Richter

**Datum:** 2026-08-29 · **Status:** getroffen · **Betrifft:** die Szenarienschicht (CIB)

Die CIB-Schicht bewertet heute das Ergebnis der Simulation. Das erzeugt zwei polare
Szenarien, bestraft die realistischen Mischlagen und lässt den Lauf nichts erzeugen, was
nicht vorher feststand. **Entschieden ist Variante C:** Ein Szenario wird ein benanntes
Bündel exogener Verläufe; F1–F7 bleiben als lesbare Zustandslabel, die aus dem Lauf
*abgeleitet* werden, statt ihn zu bewerten. Ein Rest von Variante B — eine
Verträglichkeitsprüfung beim Einrichten — bleibt als Wächter.

Ausgangspunkt war eine kleinere Frage: Sollen die 48 F7-Matrixzellen aus P0.2 fachlich
abgenommen werden? Die Antwort lautet **noch nicht** — und zwar nicht wegen der 48 Zellen,
sondern wegen dessen, was beim Nachmessen der übrigen 120 sichtbar wurde.

## Die Grundlage, nachgemessen

Alle Zahlen unten sind am 2026-08-29 gegen den Stand dieses Branches reproduziert worden,
nicht aus der Vorlage übernommen. Das Impact-Balance-Kriterium wurde dafür
nachimplementiert und über den vollständigen Zustandsraum ausgewertet.
Sie stehen als Messung in [`tests/test_cib_einachsigkeit.py`](../tests/test_cib_einachsigkeit.py) —
bewegt sich eine, wird der Test rot, und die Entscheidung gehört neu auf den Tisch.

### 1. Der Score misst Polarität, nicht Plausibilität

`compute_consistency_score` bildet das Verhältnis positiver zu allen Einflüssen — also
Widerspruchsfreiheit. Über alle 128 Systemzustände ausgewertet hängt der Wert fast nur
davon ab, wie einheitlich die Faktoren gepolt sind:

| Gleichpolige Faktoren | Fälle | Score ⌀ | Score max |
| --- | ---: | ---: | ---: |
| 4 von 7 | 70 | 0,499 | 0,678 |
| 5 von 7 | 42 | 0,562 | 0,771 |
| 6 von 7 | 14 | 0,682 | 0,945 |
| 7 von 7 | 2 | 0,853 | 0,970 |

Korrelation zwischen Score und Polaritäts-Reinheit: **+0,56**, über die vier Gruppen
monoton. Die drei Archetyp-Kennzahlen fallen genau darauf: **BAU 0,970** ist der
vollständig gleichpolige Zustand, **Konflikt 0,867** liegt bei 6 von 7 — und die
**Wende 0,629** wird bestraft, weil sie gemischt ist.

### 2. Das echte Kriterium liefert zwei Szenarien, nicht drei

Nach Weimer-Jehles Impact Balance ist ein Szenario konsistent, wenn jeder Deskriptor in
dem Zustand steht, den seine eingehende Bilanz empfiehlt. Über alle 128 Zustände geprüft
erfüllen das **genau zwei**: `(F1.1 … F7.1)` und `(F1.2, F2.2, F3.1, F4.2, F5.2, F6.2, F7.2)`.
Beide sind Pole — der zweite mit der einen Ausnahme, dass F3 nicht mitkippt.

Damit ist die Frage beantwortet, die [P2.2](projektplan.md#p22--die-szenarienschicht-endgültig-festlegen)
als Fallstrick offengelassen hatte: Das Tripleset ist aus dem echten Kriterium **nicht**
bedienbar. Mit einer Zahl statt einer Vermutung.

### 3. Die Matrix ist im Kern eine einzige Achse

| Zelltyp | Anzahl | Wert ⌀ |
| --- | ---: | ---: |
| gleichpolig (x.1 → y.1, x.2 → y.2) | 84 | +1,13 |
| gegenpolig (x.1 → y.2, x.2 → y.1) | 84 | −0,85 |

Nur **12 von 84** gleichpoligen Zellen tragen einen negativen Wert, also echte Spannung —
und **11 davon** betreffen F3 (Technologie), neun davon den Durchbruchszustand F3.2. Alle
übrigen Beziehungen verstärken sich gegenseitig.

> Gegenüber der Entscheidungsvorlage präzisiert: Dort stand «9 davon betreffen F3». Neun
> ist die Zahl der Zellen, an denen **F3.2** beteiligt ist; F3 insgesamt ist an elf der
> zwölf beteiligt.

### 4. Bei der zentralen Rückkopplung stehen die Vorzeichen falsch

| Wirkung laut Matrix | Zelle | Wert | Begründung |
| --- | --- | ---: | --- |
| Nachfrageboom → strenge Regulierung | F1.1 → F2.2 | −2 | keine |
| Nachfrageboom → Flugscham | F1.1 → F6.2 | −2 | keine |
| Nachfrageboom → Schienenausbau | F1.1 → F5.2 | −2 | keine |
| Wirtschaftswachstum → strenge Regulierung | F4.1 → F2.2 | −2 | keine |

Die Matrix sagt: *Wachstum beruhigt die Regulierer.* Real ist es umgekehrt.
EU-ETS-Ausweitung, ReFuelEU, nationale Ticketsteuern, Flygskam, das französische
Kurzstreckenverbot, der Deutschlandtakt — sämtlich Reaktionen *auf* das Verkehrswachstum.

**Und das erklärt alles Vorherige.** Eine negative Rückkopplung — Wachstum erzeugt
Regulierung erzeugt Preis erzeugt Substitution erzeugt weniger Wachstum — ist der Motor,
der gemischte Szenarien hervorbringt. Sind alle diese Schleifen als gleichgerichtet
kodiert, bleibt eine Achse übrig und darauf genau zwei kohärente Welten: alles gut, alles
schlecht. Die Einachsigkeit ist kein Zufall der Bewertung, sie ist deren Folge.

### 5. Die 120 Zellen ohne Begründung tragen dieselbe Autorität

| Zellgruppe | mit Begründung |
| --- | ---: |
| F7-Zellen, als prüfbedürftig markiert | 48 / 48 |
| übrige Zellen | 0 / 120 |

Die einzigen begründeten Zellen der Matrix sind ausgerechnet die, die als unsicher
gekennzeichnet sind. Die 120 anderen tragen dasselbe `"frozen": true` und damit denselben
Anspruch auf fachliche Geltung — ohne einen Satz Herleitung. Die vier Zellen mit dem
falschen Vorzeichen stehen in dieser Gruppe.

### Ein Nebenbefund, der entwarnt werden kann

43 der 84 Urteilsgruppen verletzen Weimer-Jehles Nullsummen-Regel. Geprüft, ob das etwas
ändert: nein. Bei zwei Zuständen je Faktor wirkt der Gruppenversatz auf beide Zustände
gleich und kürzt sich im Vergleich heraus — **0 von 128** Szenarien werden anders
beurteilt. Relevant wird es erst, wenn ein Faktor einen dritten Zustand bekommt. Beim
Umsetzen von P2.2 mitnehmen, sonst nicht.

## Warum keine Simulation entsteht

Heute simuliert die Engine einen Verlauf, und die CIB-Schicht beurteilt anschließend den
Endzustand. Damit steht die Antwort vor der Rechnung: Der Lauf kann sie nur bestätigen
oder danebenliegen. Er erzeugt nichts, was nicht vorher als zulässig festgelegt war.

```
heute          Simulation ──► Endzustand F1…F7 ──► CIB urteilt (konsistent? Score?)
                                                   Ergebnis wird bewertet, nicht erzeugt

künftig        Rahmen ──► Simulation ──► Ergebnis
               (Regulierung,  (rechnet im   (Preise, Yields,
                Geopolitik,    Rahmen)       Segmente)
                Konjunktur)
               Der Rahmen setzt die Außenwelt, der Lauf erzeugt die Zahlen
```

In der Energie- und Klimaforschung wird CIB genau so verwendet: als Erzeuger kohärenter
*Rahmenszenarien*, in denen anschließend quantitative Modelle rechnen. Der Rahmen fixiert
die exogenen Größen — Regulierung, Geopolitik, Konjunktur —, also die, die ein Unternehmen
nicht steuert. Nachfrage, Substitution, Akzeptanz, Preise und Buchungsraten kommen aus dem
Lauf.

**Nebeneffekt:** Der bekannte Widerspruch, dass die Sweeps ihre eigenen `*_END_STATES`
nicht erreichen, verschwindet. Er ist heute ein Fehler, weil der Endzustand vorgegeben
ist. Nach der Umdrehung ist er das erwartete Verhalten.

## Die drei Wege — und warum C

| | Weg | Preis |
| --- | --- | --- |
| **A** | CIB behalten, Rolle umdrehen. Die Matrix erzeugt Rahmenszenarien statt Urteile; behält die Weimer-Jehle-Fundierung und die akademische Anschlussfähigkeit. | Die Matrix muss neu erhoben werden — 168 begründete Urteile über gerichtete Einflussstärken. Unvermeidlich, weil die heutigen Werte die Rückkopplungen verneinen. |
| **B** | CIB durch morphologische Analyse ersetzen. Statt gerichteter Einflussstärken nur paarweise Verträglichkeit: widersprüchlich, angespannt oder unproblematisch. | Kein Score mehr, nur eine Menge zulässiger Kombinationen. Die Rangfolge entfällt — kein Verlust, wenn dieser Rang ohnehin Polarität gemessen hat. |
| **C** ✅ | **Szenarien als exogene Pfadbündel.** CO₂-Preis, SAF-Quote, Konjunktur, Ölpreis, Schienenkapazität, geopolitische Schocks. Alles andere rechnet die Simulation. So arbeiten Energie- und Verkehrsmodelle (IEA, IPCC-Storylines). | Die Kohärenz der Bündel muss anders begründet werden als durch eine Matrix — in Prosa mit Quellen, wie bei den SSP-Storylines. Dafür entfällt eine ganze Schicht nicht belegbarer Urteile. |

**Gewählt: C als Rückgrat, ein Rest von B als Wächter.** Szenarien werden exogene
Pfadbündel. F1–F7 bleiben als *lesbare Zustandslabel*, die aus dem Lauf abgeleitet werden —
nicht als Eingaben. Eine kleine Verträglichkeitsprüfung im Stil von B fängt beim
Konfigurieren Unsinn ab («Rezession und Reiseboom gleichzeitig»). Die CIB-Matrix in ihrer
heutigen Rolle entfällt; sie kann später als Variante A zurückkommen, wenn jemand sie
sauber erhebt.

## Warum C günstig ist: die Maschinerie steht

| Baustein | Stand (gemessen 2026-08-29) |
| --- | --- |
| Systemgrößen mit Trajektorie | 13 / 13 — davon 11 wirklich exogen; `ticket_price` und `provider_markup` sind nur Startwerte für Größen, die der Lauf selbst erzeugt |
| Sweeps = benannte exogene Bündel | 8 unter `configs/sweeps/` |
| davon ganz ohne Faktor-Vorgaben | 4 (`action_szenario`, `co2_delayed`, `freiwillige_wende`, `transformation_conflict`) |
| Stufenfunktionen, Regeln, Preiskomponenten | vorhanden |

> Gegenüber der Vorlage präzisiert: Dort stand «3» für die Sweeps ohne Faktor-Vorgaben;
> gegen den heutigen Stand sind es vier.

Die Sweeps *sind* bereits exogene Pfadbündel. Was fehlt, ist die Beförderung: Sie sind
heute ein Nebenweg neben dem eigentlichen Lauf, sie müssen der Hauptweg werden. Das ist
Umverdrahtung, kein Neubau.

## Fünf Hebel, die mehr wiegen als die Szenarienfrage

Die Frage nach der Szenarienschicht ist die sichtbarste, aber nicht die wirksamste. Für
ein Produkt, das Unternehmen etwas verkaufen soll, wiegen diese fünf schwerer:

1. **Eine echte Ziehung statt einer Schwelle** (P2.1). Ohne Ziehung keine Verteilung, ohne
   Verteilung keine Bandbreite. «Yields fallen um 8 bis 14 %» ist eine Aussage — «Yields
   fallen um 11 %» ist eine Behauptung.
2. **Ensemble-Läufe je Szenario.** `run_multi` existiert und wurde gerade begradigt.
   Fünfzig Seeds je Rahmenszenario, ausgewertet als Perzentile, verwandeln Punktwerte in
   Bänder. Größter Glaubwürdigkeitsgewinn pro Aufwand im ganzen Projekt.
3. **Ein Backtest gegen die Vergangenheit.** Heute ist das Modell an nichts geeicht.
   Speist man die tatsächlichen Verläufe 2015–2024 ein und prüft, ob die Simulation
   Richtung und Größenordnung trifft, entsteht das Argument, nach dem jeder Fachprüfer
   zuerst fragt: *Hat es je etwas Reales reproduziert?*
4. **Treiber-Attribution statt Szenariovergleich.** «Ihr Yield reagiert dreimal so stark
   auf den CO₂-Preis wie auf die Schienenkonkurrenz» ist die verkaufbare Aussage — und mit
   der Sweep-Maschinerie günstig zu rechnen.
5. **Faktoren endogen machen.** F1 ist heute eine Schwellenregel auf der Buchungsrate, also
   eine Umbenennung dessen, was das Modell ohnehin ausrechnet. Wer die Faktoren ableitet
   statt konfiguriert, verkleinert die handgesetzte Fläche — und genau diese Fläche ist der
   Grund, warum sich der Lauf vorgegeben anfühlt.

## Reihenfolge

1. **Rolle umdrehen** — Rahmenszenario = feste Lage der exogenen Größen, Lauf erzeugt den
   Rest; die Sweeps werden vom Nebenweg zum Hauptweg. *(klein · verdrahten, nicht neu bauen
   — [P2.0](projektplan.md#p20--die-rolle-umdrehen-rahmen-statt-urteil))*
2. **Ziehung und Ensemble** — echte Ziehung im Buchungsmodell, dann Ensemble-Läufe je
   Rahmen. Ab hier liefert das Produkt Bandbreiten statt Punktwerte. *(mittel ·
   [P2.1](projektplan.md#p21--buchungsmodell-echte-ziehung-statt-schwellwert) +
   [P2.6](projektplan.md#p26--ensemble-läufe-je-rahmenszenario))*
3. **Backtest** — gegen 2015–2024 rechnen und veröffentlichen, wie gut es trifft, auch wenn
   es schlecht trifft. Ein dokumentierter Fehlschlag ist mehr wert als ein ungeprüftes
   Modell. *(mittel · [P2.7](projektplan.md#p27--backtest-gegen-20152024))*
4. **Erst dann die Szenarienschicht endgültig festlegen** — ob ein Rest CIB oder
   morphologische Verträglichkeit die Bündel absichert, entscheidet sich leichter, wenn das
   Modell geeicht ist. Vorher wäre es eine Entscheidung über ein Werkzeug, dessen Wirkung
   niemand kennt. *(offen · [P2.2](projektplan.md#p22--die-szenarienschicht-endgültig-festlegen))*

## Was daraus für die 48 F7-Zellen folgt

Sie jetzt fachlich abnehmen zu lassen wäre verfrüht. Ob `F5.1 → F7.1` bei 0 oder +1 steht,
bewegt gegen die Einachsigkeit nichts. Wer die 48 prüft, bevor über Rolle und Erhebung der
Matrix entschieden ist, prüft Werte, die danach ohnehin neu erhoben werden müssten — und
mit C entfällt die Prüfung ganz. Die offene Position aus P0.2 ist damit **zurückgestellt
mit Grund**, nicht erledigt: `metadata.source` bleibt `llm_proposed_pending_review_v3`.

## Was diese Entscheidung nicht berührt

Die deterministische Rechenschicht, die Trennung «Zahlen aus Python, Narrativ vom Modell»,
die Provenienz-Kette aus Seed, Rechenmodus, Fingerabdruck und Codestand, die Beschränkung
der Agenten auf ihr Profil: Das ist der eigentliche Unterscheidungspunkt gegenüber einem
Chatbot mit Diagrammen, und nach den Prüfrunden der letzten Woche steht es sauber. Nichts
davon wird von dieser Entscheidung berührt. Die Invarianten 1 bis 7 in
[`CLAUDE.md`](../CLAUDE.md) gelten unverändert — Invariante 3 (die Matrix bleibt
eingefroren) so lange, wie die Matrix in Gebrauch ist.

**Der Satz, an dem ein Kunde einhakt:** Solange die Matrix so steht, sagt der
Konsistenzwert einem Unternehmen: polarisierte Welten sind plausibel, gemischte nicht.
Strenge Regulierung *bei* starker Nachfrage ist die reale europäische Lage — und das
Modell bewertet sie heute als unplausibel. Das ist die Stelle, an der ein Fachprüfer beim
Kunden nachfragt. Bis P2.0 steht, gilt deshalb die abgeschwächte Formulierung in
`docs/cib_role.md` und `docs/handbuch/cib.md`.

## Quellen

- Weimer-Jehle, W. (2006). *Cross-impact balances* — <https://www.cross-impact.org/ressourcen/cib_weimer-jehle_2006.pdf>
- *Properties of Cross-Impact Balance Analysis* — <https://arxiv.org/pdf/0912.5352>
- EASA / T&E zu Verkehrswachstum als Handlungstreiber — <https://www.transportenvironment.org/articles/easa-report-confirms-urgent-need-for-eu-action-on-e-fuels-taxation-and-air-traffic-growth>
- *Air traffic growth jeopardises European aviation's climate mitigation* — <https://www.nature.com/articles/s43247-025-02935-5>
