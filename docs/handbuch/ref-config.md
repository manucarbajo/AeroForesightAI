Die Ausgangslage jedes Laufs steht in sechs Dateien unter `configs/`. Im
Normalbetrieb müssen Sie sie nicht anfassen — alles Nötige lässt sich im Editor
einstellen. Wer mit alternativen Konfigurationen arbeiten will, wählt sie im Tab
**Lauf & Ablage** unter «Datengrundlage».

| Datei | Inhalt |
|---|---|
| `simulation_config.json` | Name der Simulation, Laufzeit (`clock.max_ticks`), Voreinstellungen für das Sprachmodell |
| `properties.json` | Systemgrößen, Personen-Merkmale, Marktregeln, Preismodell, Marktrückkopplung, Sättigung |
| `factors.json` | Die sieben Faktoren mit Namen, Leitfrage und je zwei Zuständen |
| `cib_frozen.json` | Die eingefrorene Einflussmatrix für die Konsistenzprüfung |
| `agents.json` | Die drei Akteure mit ihren Rollen |
| `agent_profiles.json` | Was jeder Akteur sehen und vorschlagen darf |

Dazu kommt `configs/sweeps/` mit den Szenario-Presets, je eines pro Datei.

## Was wo drinsteht

`properties.json` ist die umfangreichste Datei und trägt mehrere Abschnitte.
Unter `system_properties` stehen die Systemgrößen mit Beschreibung, Einheit und
Wertebereich; unter `individual_properties` die Merkmale einer Person mit ihren
Verteilungen. `price_model`, `market_feedback` und `saturation` enthalten die
Werte, die im Editor unter **Nachfrage & Preisbildung** stehen.

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
| `system_property` | Eine Systemgröße aus `system_properties`, verglichen mit einem Zahlenwert. |
| `metric` | Eine Laufzeitgröße: `booking_rate`, `prior_booking_rate`, `cost_pressure`, `cost_index`, `ticket_price`, `demand_level`, `carbon_tax_level`, `saf_mandate_share`, `fuel_price_change`, `oil_price_index`, `tick`. |
| `tick` | Kurzform für „genau in dieser Runde". |

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

Zwei Feinheiten, die im Verlauf sichtbar werden: Eine `shift_rule`, die auf
`booking_rate` reagiert, sieht die Rate der **vorigen** Runde — die aktuelle
entsteht erst aus der Kaufentscheidung, die die Regel gerade beeinflusst. Und
ein `regulatory_influence` kann **keine** `metric` prüfen: Die Kostenrechnung
läuft, bevor es Laufzeitgrößen gibt. Statt wirkungslos zu bleiben, wird eine
solche Regel beim Start abgewiesen.

Ein leeres `when` heißt „immer". Bei einem Kostentreiber ist das erlaubt und
sinnvoll. Bei `factor_rules` und `shift_rules` wird es abgewiesen: Eine Regel,
die in jeder Runde greift, ist fast immer ein vergessenes `when`.

Zwei Schreibweisen weist die Prüfung ausdrücklich ab, weil sie früher still
wirkungslos blieben: ein `factor` mit leerem oder fehlendem `state` (`null`
zählt dazu — die Regel wurde dann gegen den Zustand „None" verglichen und traf
nie zu), und ein `tick` mit Nachkommastelle. `{"tick": 3.7}` griff in Runde 3,
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
«Bevölkerung als Standard speichern» in `properties.json`. Unter **Kontrolle**
legt «Szenario sichern» eine neue Datei unter `configs/sweeps/` an.

## Die eingefrorene Matrix

`cib_frozen.json` trägt das Kennzeichen `"frozen": true` und darf sich nicht aus
Simulationsläufen ableiten. Der Grund steht unter
[CIB-Konsistenzprüfung](/doku/cib): Käme der Maßstab aus dem Messobjekt, wäre
die Bewertung zirkulär.
