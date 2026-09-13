Die Ausgangslage jedes Laufs steht in sechs Dateien unter `configs/`. Im
Normalbetrieb müssen Sie sie nicht anfassen — alles Nötige lässt sich im Editor
einstellen. Wer mit alternativen Konfigurationen arbeiten will, wählt sie im
Schritt **Lauf & Ablage** unter «Datengrundlage».

| Datei | Inhalt |
|---|---|
| `simulation_config.json` | Name der Simulation, Laufzeit (`clock.max_ticks`), Voreinstellungen für das Sprachmodell |
| `properties.json` | Systemgrößen, Personen-Merkmale, Marktregeln, Preismodell, Marktrückkopplung, Sättigung |
| `factors.json` | Die sieben Faktoren mit Namen, Leitfrage und je zwei Zuständen |
| `cib_frozen.json` | Die eingefrorene Einflussmatrix für die Konsistenzprüfung |

## Die Koeffizienten der Buchungsentscheidung

Unter `booking_model` in `properties.json` stehen die acht Zahlen, die
bestimmen, wie stark Preis, CO₂-Abgabe und Bahnalternative gegen die
Buchungsbereitschaft arbeiten. Sie standen bis August 2026 als Literale im
Programmcode.

Jede trägt zwei Felder: `wert` und `quelle`. **Die Quelle nennt beides
getrennt** — die Funktionsform und den Zahlenwert. Dass der Preis negativ in den
Nutzen eingeht, ist Standard der diskreten Wahltheorie und belegt. Dass das
Gewicht der Bahnalternative *1,5* beträgt, ist es nicht: Dieser Wert ist in
diesem Modell gesetzt.

**Keiner der acht Werte ist aus Daten geschätzt.** Das steht so in jeder
Quellenangabe, und ein Test hält es fest — eine Literaturangabe an eine
handgesetzte Zahl zu heften sähe aus wie eine Kalibrierung, die es nicht gibt.
Wer sie eicht, ersetzt beides: den Wert und seine Herkunft.

| Feld | Was es bestimmt |
|---|---|
| `base_utility` | Bei welchem Preisniveau die Buchungswahrscheinlichkeit durch 50 Prozent geht |
| `price_reference_eur` | Bezugsgröße, auf die der Ticketpreis normiert wird |
| `substitution_weight` | Gewicht der Bahnalternative gegenüber dem reinen Preisterm |
| `carbon_reference_eur` | Bezugsgröße für den Teil der CO₂-Abgabe oberhalb des Referenzwerts |
| `carbon_eco_baseline_eur` | Ab welcher Abgabe ein Umwelt-Malus überhaupt entsteht |
| `green_premium` | Aufschlag auf die Zahlungsbereitschaft umweltbewusster Personen |
| `high_price_sensitivity_threshold` | Ab welcher Preisempfindlichkeit der zusätzliche Abgaben-Malus greift |
| `high_price_sensitivity_penalty` | Wie hoch dieser zusätzliche Malus ausfällt |

Der Bereich **Modell** im Dashboard zeigt diese Felder noch nicht — sie sind
über die Datei zu ändern.
| `agents.json` | Die drei Akteure mit ihren Rollen |
| `agent_profiles.json` | Was jeder Akteur sehen und vorschlagen darf |

Dazu kommt `configs/sweeps/` mit den Szenario-Presets, je eines pro Datei. Eine
solche Datei überschreibt Systemgrößen (`property_overrides`) und darf seit dem
2026-09-03 zusätzlich `preisstrategie` setzen — `auslastung` oder `marge`. Fehlt
das Feld, gilt die ausgelieferte Konfiguration; ein unbekannter Name wird beim
Laden abgewiesen. Es hat bewusst keinen Tick-Verlauf: Ein Anbieter wechselt nicht
mitten im Lauf seine Preislogik.

## Was wo drinsteht

`properties.json` ist die umfangreichste Datei und trägt mehrere Abschnitte.
Unter `system_properties` stehen die Systemgrößen mit Beschreibung, Einheit und
Wertebereich; unter `individual_properties` die Merkmale einer Person mit ihren
Verteilungen. `price_model`, `market_feedback` und `saturation` enthalten die
Werte, die im Editor unter **Nachfrage & Preisbildung** stehen.

### Einheiten, die eine Zeitskala tragen

**Ein Tick ist ein Monat** (P3.8, seit dem 7. September 2026). Das steht in
keiner Datei als Feld, wirkt sich aber auf jede Größe aus, deren Einheit auf
`_per_tick` endet: Ihr Wert wird Tick für Tick aufgezinst.

| Größe | Einheit | ausgeliefert | im Jahr |
| --- | --- | ---: | ---: |
| `demand_growth_rate` | `fraction_per_tick` | 0,0025 | 3,04 % |
| `fuel_price_change` | `fraction_per_tick` | 0,005 | 6,17 % |
| `erneuerungsrate` | `share_per_tick` | 0,0 | 0 % |

**Wenn Sie einen dieser Werte ändern, rechnen Sie ihn zuerst aufs Jahr hoch** —
zwölfmal aufgezinst, nicht mal zwölf. Der Unterschied ist der Grund, aus dem
P3.8 überhaupt aufgefallen ist: `demand_growth_rate` stand auf 0,03 und war in
der Beschreibung als *jährliche* Rate ausgewiesen. Aufgezinst waren es 42,6
Prozent im Jahr.

Dasselbe gilt für Verläufe mit Stützpunkten: `bevoelkerungsentwicklung` trägt
Jahresstufen im Abstand von zwölf Ticks und reicht bis Tick 120, also über
zehn Jahre.

### Wie der Anbieter preist

Unter `market_rules` steht die Regel `provider_yield_feedback`, und in ihr das
Feld **`strategie`**. Es entscheidet, wie der Anbieter auf freie Kapazität
reagiert, und es gibt genau zwei Werte:

| Wert | Verhalten |
| --- | --- |
| `auslastung` *(Standard)* | Der Anbieter senkt den Preis, bis die Kapazität gefüllt ist. |
| `marge` | Der Anbieter hält seinen Aufschlag; die Auslastung schwankt. Kommt Kapazität dazu, bleibt der Preis, wo er ist. |

**Beides kommt in der Wirklichkeit vor**, und das Modell legt sich deshalb nicht
fest. Ein unbekannter Wert wird beim Laden abgewiesen — sonst fiele ein
Tippfehler still auf `auslastung` zurück.

Wie viel Kapazität da ist, steht als Systemgröße `kapazitaet_index` (1,0 =
Ausgangsniveau). Unter `marge` wirkt sie als **Grenze**: Mehr Menschen können
buchen wollen, als Plätze da sind, und dann bleiben welche übrig — zufällig
ausgewählt, nicht nach Zahlungsbereitschaft.

## Regeln und ihre Bedingungen

Drei Abschnitte in `properties.json` arbeiten mit Regeln: `factor_rules`
verschieben einen Faktor, `shift_rules` verändern Merkmale der Bevölkerung, und
`regulatory_influences` schalten einen regulatorischen Kostentreiber zu. Alle
drei tragen dasselbe Feld `when` — die Bedingung, unter der sie greifen. Seit
der Vereinheitlichung im August 2026 bedeutet dieselbe Bedingung in allen drei
Abschnitten dasselbe; vorher verstand jeder Abschnitt einen anderen Ausschnitt,
ohne das zu melden.

Eine Bedingung nennt **eine Bezugsgröße** und vergleicht sie:

| Bezugsgröße | Bedeutung |
|---|---|
| `factor` + `state` | Ein Faktor steht in einem bestimmten Zustand. Beide Felder sind Pflicht. |
| `system_property` | Eine Systemgröße aus `system_properties`, verglichen mit einem Zahlenwert. Nur **exogene** Verläufe (`source: "trajectory"`) — siehe den Hinweis unten. |
| `metric` | Eine Laufzeitgröße: `booking_rate`, `prior_booking_rate`, `cost_pressure`, `cost_index`, `ticket_price`, `demand_level`, `carbon_tax_level`, `saf_mandate_share`, `fuel_price_change`, `oil_price_index`, `tick`. |
| `tick` | Kurzform für „genau in diesem Tick". |

Verglichen wird mit `above` (echt größer), `below` (echt kleiner), `at_least`,
`at_most` oder `eq`. `gte` und `lte` sind ältere Namen für `at_least` und
`at_most` und bleiben gültig. Mehrere Vergleiche in einer Bedingung gelten
zusammen: `{"system_property": "carbon_tax_level", "above": 50, "below": 100}`
trifft nur zwischen 50 und 100 zu.

Ein `factor` und eine numerische Bezugsgröße dürfen zusammen in einer Bedingung
stehen; **zwei numerische** dürfen es nicht, weil sich ein Vergleich dann keiner
von beiden zuordnen ließe. Solche Bedingungen weist die Prüfung vor dem Start
ab — ebenso einen Tippfehler im Namen einer Metrik oder Systemgröße, einen
Vergleich ohne Bezugsgröße und ein `factor` ohne `state`.

**Nicht jede Systemgröße ist in einer Bedingung lesbar.** `provider_markup`
und `ticket_price` entstehen im Lauf (`source: "runtime"` bzw. `"computed"`);
ihre `trajectory` ist nur ein Startwert. Eine Bedingung darauf käme deshalb nicht
an den Preis des laufenden Ticks, sondern an diesen Startwert — der Name stimmte,
die Zahl wäre veraltet. Solche Bedingungen weist die Prüfung vor dem Start ab und
nennt die Alternative: Den Preis des laufenden Ticks gibt es als `metric`.

Der Grund, warum der Laufzeitwert nicht einfach durchgereicht wird, ist eine
Modellentscheidung und keine Bequemlichkeit: Die Faktor-Regeln laufen **vor** der
Preisberechnung eines Ticks. Eine Bedingung auf `ticket_price` prüfte je nach
Einhängepunkt gegen den Preis von vorhin oder von jetzt — dieselbe Regel würde
je nach Ort im Ablauf etwas anderes bedeuten.

Zwei Feinheiten, die im Verlauf sichtbar werden: Eine `shift_rule`, die auf
`booking_rate` reagiert, sieht die Rate des **vorigen** Ticks — die aktuelle
entsteht erst aus der Kaufentscheidung, die die Regel gerade beeinflusst. Und
ein `regulatory_influence` kann **keine** `metric` prüfen: Die Kostenrechnung
läuft, bevor es Laufzeitgrößen gibt. Statt wirkungslos zu bleiben, wird eine
solche Regel beim Start abgewiesen.

Ein leeres `when` heißt „immer". Bei einem Kostentreiber ist das erlaubt und
sinnvoll. Bei `factor_rules` und `shift_rules` wird es abgewiesen: Eine Regel,
die in jedem Tick greift, ist fast immer ein vergessenes `when`.

Zwei Schreibweisen weist die Prüfung ausdrücklich ab, weil sie früher still
wirkungslos blieben: ein `factor` mit leerem oder fehlendem `state` (`null`
zählt dazu — die Regel wurde dann gegen den Zustand „None" verglichen und traf
nie zu), und ein `tick` mit Nachkommastelle. `{"tick": 3.7}` griff in Tick 3,
weil die Nachkommastelle abgeschnitten wurde; ein Zahlendreher sah damit aus
wie eine Regel, die eben woanders greift. `3.0` bleibt zulässig — JSON kennt
keine ganzen Zahlen als eigenen Typ.

Die technischen Feldnamen in der Referenz
[Alle Einstellungen](/doku/ref-parameter) verweisen genau auf diese Abschnitte —
so finden Sie zu jeder Einstellung der Oberfläche die zugehörige Stelle in der
Datei.

## Was die Oberfläche schreibt

Die meisten Einstellungen im Editor gelten nur für den nächsten Lauf und
verändern keine Datei. Drei Aktionen schreiben dauerhaft.

Unter **Nachfrage & Preisbildung** schreiben «Als Standard speichern» und
«Bevölkerung als Standard speichern» in `properties.json`. Unter **Lauf & Ablage**
legt «Szenario sichern» eine neue Datei unter `configs/sweeps/` an.

## Die eingefrorene Matrix

`cib_frozen.json` trägt das Kennzeichen `"frozen": true` und darf sich nicht aus
Simulationsläufen ableiten. Der Grund steht unter
[CIB-Konsistenzprüfung](/doku/cib): Käme der Maßstab aus dem Messobjekt, wäre
die Bewertung zirkulär.
