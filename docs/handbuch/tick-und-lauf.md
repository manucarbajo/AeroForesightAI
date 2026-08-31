Drei Begriffe bauen aufeinander auf: Tick, Lauf und Szenario. Sie sauber
auseinanderzuhalten erspart die häufigste Fehldeutung von Ergebnissen.

## Der Tick

Ein Tick ist eine Runde des Modells. In ihm entscheidet die Bevölkerung über
Buchungen, die Airline passt den Preis an, die Akteure bringen Ereignisse ein und
Faktoren können sich verschieben.

Ein Tick hat **keine Kalenderbedeutung**. Er ist weder ein Monat noch ein Quartal
noch ein Jahr. Das ist eine bewusste Entscheidung, keine fehlende Angabe: Sobald
man Ticks in Jahre übersetzt, entstehen Aussagen der Form «2032 kostet das Ticket
214 Euro», für die das Modell keine Grundlage hat. Was es liefert, sind
Wirkungsrichtungen und Größenordnungen unter gegebenen Annahmen.

Ein längerer Lauf bildet deshalb nicht mehr Zeit ab, sondern mehr Gelegenheiten
für Anpassung und Rückkopplung. Vierzig Ticks zeigen, wohin sich ein System
einpendelt; zehn zeigen die erste Reaktion.

**Eine Einschränkung dazu, seit dem 31. August 2026 gemessen und offen benannt:**
Der Satz oben gilt für das, was das Modell *ausgibt* — dort steht nirgends ein
Datum. Er gilt nicht durchgehend für das, was es *rechnet*.

Denn jeder Mechanismus, der sich pro Runde verändert, unterstellt stillschweigend
eine Zeitskala. Im Modell unterstellen sie nicht dieselbe: Die hinterlegte
Bevölkerungskurve wächst um acht Prozent über 29 Runden — plausibel, wenn eine
Runde ein Jahr ist, und unmöglich, wenn sie ein Monat ist. Die Sättigung dagegen
lässt eine Reise nach etwa drei Runden «vergessen» sein; als Jahre gelesen wären
das drei Jahre zwischen zwei Familienflügen. Und der Backtest, der das Modell
gegen die Jahre 2015 bis 2024 hält, bildet eine Runde ausdrücklich auf einen
Monat ab.

**Was Sie daraus mitnehmen sollten:** Lesen Sie einen Lauf weiterhin als
Wirkungskette, nicht als Zeitreihe — dafür ist er gebaut. Aber übersetzen Sie
Rundenzahlen nicht in Jahre, auch nicht im Kopf, und vergleichen Sie zwei Läufe
nur bei gleicher Rundenzahl. Die offene Frage ist im Projektplan als P3.8
vermerkt.

## Der Lauf

Ein Lauf ist eine Folge von Ticks aus einer festgelegten Ausgangslage. Er erzeugt
ein eigenes Verzeichnis unter `outputs/` mit allen Zwischenständen, Zeitreihen
und Auswertungen. Was genau darin liegt, steht unter
[Ausgabedateien](/doku/ref-ausgaben).

Mehrere Läufe mit identischer Konfiguration heißen Wiederholungen. Sie
unterscheiden sich nur im Zufallsstartwert, also darin, welche Bevölkerung
gezogen wurde. Weichen ihre Ergebnisse stark voneinander ab, trägt die Aussage
nicht — dann hing das Ergebnis an der Stichprobe und nicht an den Annahmen.

## Das Szenario

Ein Szenario ist keine Fortschreibung des Laufs, sondern eine mögliche
Fortsetzung. Am Ende jedes Laufs entsteht ein Tripleset aus dreien.

| Szenario | Was es beschreibt |
|---|---|
| Trend-Fortsetzung | Die im Lauf erreichte Faktorlage setzt sich fort. |
| Alternativ-Szenario | Mindestens ein Faktor entwickelt sich anders als im Lauf. |
| Spannungs-Szenario | Faktoren, die sich gegenseitig widersprechen. |

Alle drei stützen sich auf dieselben gerechneten Zahlen; sie nennen die Ticks, aus
denen sie ihre Anhaltspunkte ziehen. Das dritte ist dabei nicht ein Fehler,
sondern der interessanteste Fall: Es macht sichtbar, welche Erwartungen sich
gegenseitig ausschließen. Wie diese Bewertung zustande kommt, steht unter
[CIB-Konsistenzprüfung](/doku/cib).

## Die Uhr im Lauf

Das Dashboard zeigt den Fortschritt als `current_tick / max_ticks`. Erreicht ein
Lauf sein Maximum nicht, wurde er abgebrochen — dann fehlen typischerweise auch
die Auswertungen am Ende, und die Ansicht «Szenario» bleibt leer.
