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
