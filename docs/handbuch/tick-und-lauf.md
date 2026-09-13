Drei Begriffe bauen aufeinander auf: Tick, Lauf und Szenario. Sie sauber
auseinanderzuhalten erspart die häufigste Fehldeutung von Ergebnissen.

## Der Tick

Ein Tick ist ein Rechenschritt des Modells. In ihm entscheidet die Bevölkerung über
Buchungen, die Airline passt den Preis an, die Akteure bringen Ereignisse ein und
Faktoren können sich verschieben.

**Ein Tick ist ein Monat.** Seit dem 7. September 2026 ist das festgelegt, und
zwar für alles, was das Modell *rechnet*: Wie schnell eine Reise «vergessen» ist,
wie schnell die Bevölkerung wächst, wie schnell Treibstoff teurer wird — all das
läuft in Monaten. Vierzig Ticks sind damit gut drei Jahre, fünfzig gut vier.

**In den Zahlen, die Sie zu sehen bekommen, steht trotzdem nirgends ein Datum**,
und das bleibt so. Der Grund ist derselbe wie vorher: Sobald aus Tick 40 der
«Dezember 2029» wird, entstehen Aussagen der Form «2029 kostet das Ticket 214
Euro», für die das Modell keine Grundlage hat — es ist nicht auf Jahreszahlen
geeicht, kennt keine Saison und keine Reisebeschränkung. Was es liefert, sind
Wirkungsrichtungen und Größenordnungen unter gegebenen Annahmen.

Die beiden Sätze widersprechen sich nicht. Der erste sagt, in welchem Takt die
Mechanik rechnet; der zweite, dass ein Tick trotzdem kein Kalendermonat ist,
den man auf einen Zeitstrahl legen könnte.

**Warum das überhaupt eine Frage war.** Jeder Mechanismus, der sich pro Tick
verändert, unterstellt stillschweigend eine Zeitskala — und im Modell
unterstellten sie bis September 2026 nicht dieselbe, sondern drei verschiedene um
den Faktor zwölf auseinander. Die Bevölkerungskurve wuchs um acht Prozent über 29
Ticks: plausibel als Jahre, unmöglich als Monate. Die Sättigung ließ eine Reise
nach etwa drei Ticks vergessen sein: plausibel als Monate, absurd als Jahre. Der
Backtest bildete einen Tick ausdrücklich auf einen Monat ab. Und eine vierte
Größe widersprach sich sogar selbst: Das Nachfragewachstum war als «jährlich»
beschrieben und wurde je Tick aufgezinst — aus drei Prozent wurden so
zweiundvierzig im Jahr.

**Was sich dadurch an den Zahlen geändert hat:** Die Bevölkerungskurve wächst
jetzt um 2,7 Prozent über zehn Jahre statt um acht Prozent über eine Strecke, die
als Jahre gemeint war. Die *Jahresrate* ist dabei dieselbe geblieben — geändert
wurde die Einheit, nicht die Aussage. Ein Standardlauf endet seither bei einer
Buchungsrate von 0,2679 statt 0,2685. Läufe von vor diesem Datum gehören nicht
neben spätere (siehe [Läufe vergleichen](/doku/vergleiche)).

**Was Sie daraus mitnehmen sollten:** Lesen Sie einen Lauf als Wirkungskette,
nicht als Zeitreihe — dafür ist er gebaut. Wenn Sie die Zeitskala trotzdem
brauchen, um eine Vorgabe einzustellen (wie schnell soll die Abgabe steigen?),
rechnen Sie zwölf Ticks auf ein Jahr. Und vergleichen Sie zwei Läufe nur bei
gleicher Tickzahl.

**Die Oberfläche rechnet es Ihnen vor:** Neben jeder Lauflänge steht die
Modellzeit, gerundet — «40 Ticks · rund 3 Jahre», «120 Ticks · 10 Jahre». Ein
Datum ist das nicht; es sagt nur, wie lang der Ausschnitt ist.

**Die mitgelieferten Rahmenszenarien laufen seit dem 11. September 2026
hundertzwanzig Ticks, also zehn Jahre.** Vorher waren es fünfzig — gut vier
Jahre, in denen die CO₂-Abgabe binnen 20 Monaten von 50 auf 200 Euro stieg.
Gestreckt wurde jede Marke im selben Verhältnis, nicht nur die Länge. Ein
Standardlauf über 40 Ticks bleibt dagegen, was er war: ein Ausschnitt von gut
drei Jahren.

## Der Lauf

Ein Lauf ist eine Folge von Ticks aus einer festgelegten Ausgangslage. Er erzeugt
ein eigenes Verzeichnis unter `outputs/` mit allen Zwischenständen, Zeitreihen
und Auswertungen. Was genau darin liegt, steht unter
[Ausgabedateien](/doku/ref-ausgaben).

Mehrere Läufe mit identischer Konfiguration heißen Wiederholungen. Sie
unterscheiden sich nur im Zufallsstartwert, also darin, welche Bevölkerung
gezogen wurde. Weichen ihre Ergebnisse stark voneinander ab, trägt die Aussage
nicht — dann hing das Ergebnis an der Stichprobe und nicht an den Annahmen.

## Wie weit die Vorgaben reichen

Manche Systemgrößen haben einen Verlauf mit Stützpunkten — die CO₂-Abgabe steigt
etwa in zwei Stufen, die Bevölkerung wächst bis zu einem bestimmten Tick. **Hinter
dem letzten Stützpunkt hält eine solche Kurve ihren letzten Wert.**

Das ist meistens gemeint: Eine Abgabe, die ihren Endwert erreicht hat, bleibt dort.
Bei der Bevölkerung hieß derselbe Mechanismus aber «ab hier wächst niemand mehr»,
und das ist eine ganz andere Aussage — im Standardlauf betraf es die letzten zehn
von vierzig Ticks.

**Diese eine Kurve reicht seit dem 7. September 2026 weiter** (P3.8): Sie läuft
bis Tick 120, also über jeden üblichen Lauf hinaus. Der Hinweis unten gibt es
weiterhin und er greift weiterhin — im Standardlauf nennt er jetzt **drei**
Verläufe statt vier (SAF-Mandat, Einkommensindex, CO₂-Abgabe). Dass ausgerechnet
die Bevölkerung ihn nicht mehr auslöst, ist dabei kein Nebeneffekt: Ein Hinweis,
der ohnehin bei jedem Lauf erscheint, wird überlesen.

**Deshalb sagt der Lauf es seit September 2026.** Der Preflight nennt vor dem Start
den frühesten Verlauf und wie viele Ticks über ihn hinauslaufen; im Protokoll steht
es für jeden betroffenen Verlauf. Es ist ein **Hinweis und kein Fehler**: Der Lauf
startet, die Zahlen stimmen, Sie wissen nur, worauf sie beruhen.

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
