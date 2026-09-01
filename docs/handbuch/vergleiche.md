Ein einzelner Lauf zeigt einen möglichen Verlauf. Interessant wird es erst im
Vergleich — und dabei lässt sich einiges falsch machen.

## Den Zufall festhalten

Zu Beginn eines Laufs wird die Bevölkerung gezogen: Wer welche
Zahlungsbereitschaft, welches Alter, welche Merkmale bekommt. Ohne festen
Zufallsstartwert ist diese Bevölkerung in jedem Lauf eine andere.

Zwei Läufe unterscheiden sich dann aus zwei Gründen gleichzeitig — durch die
geänderte Annahme und durch die andere Stichprobe. Welcher der beiden die
beobachtete Wirkung erzeugt hat, lässt sich nicht mehr trennen.

Setzen Sie deshalb unter **Technik** «Zufallsstartwert festlegen» und lassen Sie
den Wert in beiden Läufen gleich. Dann geht der Unterschied allein auf die
geänderte Annahme zurück.

## Nur eine Sache ändern

Ändern Sie zwischen zwei Läufen genau eine Größe. Wer gleichzeitig die CO₂-Abgabe
erhöht und die Zielauslastung senkt, sieht am Ende eine Wirkung und hat zwei
Kandidaten dafür.

Wenn mehrere Änderungen zusammen geprüft werden sollen, rechnen Sie die Stufen
einzeln: erst A, dann B, dann A und B zusammen. Der dritte Lauf zeigt dann, ob
sich die Wirkungen addieren oder gegenseitig aufheben.

## Namen vergeben

Tragen Sie unter **Lauf & Ablage** einen Namen und die Fragestellung ein. In der
Lauf-Auswahl erscheint der Name neben der Run-ID; ohne ihn stehen dort nur
Zeitstempel, die sich nach dem dritten Lauf nicht mehr unterscheiden lassen.

Ein brauchbares Schema ist der Bezug auf den Vergleich, etwa «CO₂ 200 ab Runde 5»
gegen «CO₂ konstant 50».

## Streuung von Wirkung unterscheiden

Bevor Sie einen Unterschied zwischen zwei Läufen für eine Wirkung halten, prüfen
Sie, wie groß die natürliche Streuung ist. Stellen Sie dazu im zweiten Schritt
hinter «Feinabstimmung» die **Wiederholungen** auf fünf und lassen Sie den
Zufallsstartwert frei. Sie
bekommen fünf Läufe mit derselben Konfiguration, aber unterschiedlich gezogener
Bevölkerung, und sehen, wie weit die Ergebnisse auseinanderliegen.

Wichtig ist dabei das Feld **Wiederholungen**. Denselben Lauf einfach zweimal zu
starten genügt **nicht**: Ein einzelner Lauf ist auch ohne eigenen Startwert
wiederholbar und liefert beide Male dasselbe Ergebnis. Sie würden eine Streuung
von null messen und danach jeden Unterschied für belastbar halten.

Ist der Unterschied zwischen Ihren beiden Läufen kleiner als diese Streuung, ist
er nicht belastbar.

**Seit August 2026 müssen Sie das nicht mehr von Hand vergleichen.** Ein Lauf mit
Wiederholungen legt in `multi_run_summary.json` ein **Band** ab: für jede Runde
den Median und ein 80-Prozent-Intervall über alle Wiederholungen, für
Buchungsrate und Ticketpreis. Die Streuung steht damit als Zahl da, statt aus
mehreren Läufen abgelesen werden zu müssen.

**Und Sie sehen es.** Wählen Sie einen der Läufe aus einem Durchgang mit
Wiederholungen aus — in der Lauf-Auswahl steht er als
`batch_…/run_003` — und öffnen Sie unter **Ergebnisse** die Ansicht **Figures**,
Aussage 1 «Preis und Nachfrage». Die Linien zeigen weiterhin **diesen einen**
Lauf; hinter ihnen liegen getönte Flächen, und die zeigen, wo 80 Prozent aller
Wiederholungen lagen.

So liest man das: Läuft Ihre Linie mitten im Band, ist sie ein typischer
Vertreter. Läuft sie am Rand, haben Sie einen Ausreißer erwischt — und sollten
für eine Aussage lieber den Median nehmen. Ist das Band an einer Stelle breit,
ist die Zahl dort schlecht bestimmt, egal wie genau sie angezeigt wird.

Perzentile und nicht Minimum und Maximum, und das ist kein Detail: Die Ränder
einer Stichprobe wandern mit jeder weiteren Wiederholung nach außen. Ein Band aus
Minimum und Maximum sähe mit fünfzig Läufen breiter aus als mit zehn, ohne dass
sich am Modell etwas geändert hätte.

Zwei Hinweise dazu. Das Band ist **so lang wie der kürzeste** Lauf — sonst stünde
am Ende ein Wert aus zwei statt fünfzig Läufen und sähe wie ein zusammenlaufendes
Band aus. Und Wiederholungen lohnen sich vor allem **ohne Sprachmodell**:
gemessen brauchen fünfzig Wiederholungen über acht Szenarien rund vier Minuten im
Modus «Nur Zahlen» und knapp zwölf ohne Sprachmodell — mit Modell wären es
Stunden, und für die Streuung der Zahlen trägt es nichts bei.

## Läufe aus verschiedenen Ständen der Software

Vergleichen Sie nur Läufe, die mit demselben Stand gerechnet wurden. Am
2026-08-27 wurde ein Fehler in der Kostenrechnung behoben: Regulatorische
Abgaben gingen bis dahin nicht in den Startpreis ein. Läufe von davor beginnen
deshalb billiger, und die Nachfrage weicht später aus — im Standardlauf kippt
die Mobilitätsnachfrage seither in Runde 4 statt in Runde 15. Die Endzustände
der Faktoren sind dieselben geblieben, der Weg dorthin nicht.

Am selben Tag wurde ein zweiter Unterschied begradigt: **Wiederholungen ohne
eigenen Startwert** begannen ihre Folge bei einem anderen Wert als ein
Einzellauf. Beides beginnt jetzt gleich, wodurch die erste Wiederholung
derselbe Lauf ist wie ein einzeln gestarteter. Wiederholungen aus der Zeit
davor tragen andere Startwerte und damit andere Zahlen — die Aussagen, die man
aus ihrer Streuung gezogen hat, bleiben gültig, die Einzelwerte nicht.

Am 2026-08-28 kam ein dritter Schnitt dazu, und er trifft **nur Läufe aus einem
Szenario-Preset**: Bis dahin legte das Dashboard nach dem Preset noch die Werte
aus den Konfigurationsdateien darüber und drehte es damit still zurück.
Betroffen waren alle acht ausgelieferten Presets — je nach Preset zwischen zwei
und zehn Systemgrößen, bei «Totaler Wahnsinn» zusätzlich alle sieben Faktoren.
Am deutlichsten bei «Business as Usual»: Das Szenario schließt eine steigende
CO₂-Abgabe ausdrücklich aus, gerechnet wurde sie trotzdem, womit die Regulierung
in Runde 15 auf «streng» kippte. Preset-Läufe von davor beschreiben also nicht
die Annahmenwelt, deren Namen sie tragen. Über die Kommandozeile gestartete
Sweeps waren nie betroffen.

Am 2026-08-30 kam ein vierter Schnitt dazu: **Die Faktorlage wird nicht mehr
vorgegeben.** Vier der acht Szenarien setzten bis dahin Faktorzustände fest,
und der Assistent bot dafür einen eigenen Schritt an. Beides ist entfallen — die
Faktoren entstehen jetzt im Lauf aus den Systemgrößen.

Für die **Endzustände** ändert das nichts: Nachgemessen über 20 Runden landen in
allen vier betroffenen Szenarien alle sieben Faktoren auf denselben Zuständen wie
zuvor. Was sich ändert, sind die **ersten Runden**, in denen die Vorgabe noch
stand, bevor die Regeln sie überschrieben — und über die Rückkopplung auch die
Preise am Ende: bei «Totaler Wahnsinn» 588,47 statt 574,47 Euro (2,4 %), bei
«P5.7» 121,27 statt 120,59 (0,6 %). Für die anderen beiden ist kein Unterschied
messbar. Läufe dieser vier Szenarien von vor diesem Datum sind mit späteren also
nur eingeschränkt vergleichbar.

Am 2026-08-30 kam ein **fünfter Schnitt** dazu, und er ist der größte: **Die
Buchungsentscheidung wird gezogen, nicht mehr geschwellt.** Bis dahin buchte
jeder, dessen rechnerische Buchungswahrscheinlichkeit über 50 Prozent lag — und
zwar mit Sicherheit. Zwei Personen mit 51 und 99 Prozent waren nicht zu
unterscheiden.

Das verschiebt **jede** Zahl, und zwar systematisch. Gemessen an 2000 Personen
der Standardkonfiguration:

| Ticketpreis | vorher | heute | Streuung über 20 Ziehungen |
|---|---:|---:|---|
| 80 € | 0,968 | 0,742 | 0,715 – 0,755 |
| 110 € | 0,847 | 0,602 | 0,577 – 0,615 |
| 140 € | 0,621 | 0,439 | 0,419 – 0,449 |
| 180 € | 0,299 | 0,243 | 0,229 – 0,255 |
| 250 € | 0,059 | 0,072 | 0,065 – 0,082 |

Die alte Schwelle **überzeichnete** die Nachfrage bei niedrigen Preisen und
**unterzeichnete** sie bei hohen: Sie drückte jede Wahrscheinlichkeit auf null
oder eins und stauchte die Nachfragekurve damit zu den Rändern hin. Läufe von
vor diesem Datum sind mit späteren **nicht** vergleichbar — auch nicht in der
Richtung, denn die Verzerrung hat je nach Preisniveau ein anderes Vorzeichen.

Dafür gibt es jetzt eine **Streuung**, wo vorher keine war: Derselbe Lauf mit
demselben Ausgangspunkt liefert je nach Zufallsstartwert leicht verschiedene
Raten. Das ist kein Mangel an Genauigkeit, sondern die Bandbreite, die eine
Einzelzahl nur vorgetäuscht hat.

Zwei Dinge bleiben: Ein Lauf mit demselben Zufallsstartwert liefert weiterhin
**exakt** dasselbe Ergebnis. Und ein Seed ändert die **Faktor-Endzustände**
heute kaum noch — nachgemessen landen die Startwerte 1, 2 und 3 nach 10, 15 und
20 Runden auf denselben sieben Zuständen. Die Einzelentscheidungen mitteln sich
über tausend Personen aus; was streut, sind die Raten, nicht die Lage.

Ebenfalls am 2026-08-28 kam ein vierter Schnitt, und er trifft **nur den
Szenario-Vergleich** — also den Weg, der alle hinterlegten Szenarien
nacheinander rechnet. Bis dahin gab das Dashboard seine eingestellte Länge an
jedes Szenario weiter, und weil dort immer eine Zahl steht (vorbelegt mit 40),
lief **jedes** Preset auf dieser Länge statt auf seiner eigenen. Vier der acht
ausgelieferten Szenarien sind auf 50 Ticks angelegt; sie wurden um ein Fünftel
gekürzt. **Drei von ihnen verlieren dadurch ihren End-State-Meilenstein** —
«Business as Usual», «Freiwillige Wende» und «Transformation Conflict» prüfen
genau bei Tick 50, ob das Szenario sein Ziel erreicht hat, und diese Prüfung
fand nie statt. Ein Vergleich aus der Zeit davor hat die verkürzten Verläufe
nebeneinandergelegt und die eigentliche Aussage jedes Szenarios ausgelassen.

Seither läuft im Vergleich jedes Szenario so lang, wie es angelegt ist. Die
Längenangabe im Assistenten gilt weiterhin — aber für einen **einzelnen** Lauf,
nicht für den Vergleich. Über die Kommandozeile lässt sich die Länge weiterhin
übersteuern (`--ticks`); dort sagt man es ausdrücklich, statt einen Vorgabewert
mitzuschleppen.

Woran Sie es erkennen: `run_metadata.json` hält unter `code_version` fest, mit
welchem Stand ein Lauf gerechnet wurde, und unter `seed`, mit welchem Startwert.
Unterscheiden sich zwei Läufe dort, gehören ihre Verläufe nicht nebeneinander.

Am **2026-08-30** kam ein vierter Schnitt dazu, und er betrifft nicht die
Zahlen, sondern **wo sie stehen**: Die Szenario-Artefakte eines Laufs heißen
anders. Die gerechneten Kandidaten liegen unter `gerechnete_szenarien` statt
unter `scenario_candidates`, die Erzählung unter `erzaehlte_szenarien` statt
unter `scenarios`, und der vom Sprachmodell behauptete Einflusswert heißt
`behaupteter_einfluss` statt `influence`. **Gerechnet wird dasselbe** — wer
Läufe von davor und danach vergleicht, vergleicht dieselben Zahlen; wer sie
maschinell ausliest, muss den Schlüssel nachziehen.

Am **2026-08-31** kam ein fünfter Schnitt dazu, und er betrifft, **was ein
Szenario-Vergleich überhaupt vergleicht**: Bis dahin rechnete er *alle acht*
hinterlegten Dateien durch. Vier davon sind aber keine Zukünfte, sondern
Stresstests der Engine — «Achterbahn der Extreme», «Action-Szenario», «Totaler
Wahnsinn (Alle Parameter)» und ein gesichertes Experiment namens «P5.7». Ihre
Verläufe sind auf Sichtbarkeit und Belastung gebaut, nicht auf Plausibilität.

Ein Vergleich stellt seither **vier Rahmenszenarien** nebeneinander statt acht
Dateien. Wer einen älteren Vergleichslauf offen hat, findet dort vier Ergebnisse
mehr — und die vier zusätzlichen sagen nichts über die Welt. Die Stresstests
sind nicht verschwunden: Sie lassen sich weiterhin einzeln starten, und die
Auswahl schreibt jetzt «Stresstest» an die Kachel.

Am **2026-08-31** kam ein sechster Schnitt dazu, und er ist der tiefste seit
Langem: **Das Alter prägt jetzt, wer eine simulierte Person ist.** Vorher wurde
jedes Merkmal unabhängig gezogen und das Alter beeinflusste die
Buchungsentscheidung überhaupt nicht; seither bestimmt es Einkommen,
Zahlungsbereitschaft, Preisempfindlichkeit, Umweltbewusstsein und
Bahnbereitschaft mit. Zugleich wurde die Altersverteilung selbst korrigiert —
sie stammt jetzt aus Eurostat-Daten statt aus einer Parametrisierung, die 41
Prozent der Bevölkerung auf exakt 90 Jahre setzte.

**Jede Zahl bewegt sich dadurch.** Läufe von vor und nach diesem Datum gehören
nicht nebeneinander. Woran Sie es erkennen: `run_metadata.json` hält unter
`code_version` fest, mit welchem Stand gerechnet wurde.

Am **2026-08-31** kam ein siebter Schnitt dazu: **Die Kapazität ist eine eigene
Größe geworden.** Bis dahin steuerte der Anbieter den Preis auf eine feste
Zielauslastung, und die Nachfragehöhe hing an dieser Zahl statt an den simulierten
Menschen. Ohne Vorgabe bleibt alles wie es war — die Standardwerte sind so gewählt,
dass sich nichts ändert. Wer aber eine Kapazität vorgibt, bekommt andere Zahlen.

## Wo Sie vergleichen

Die Endwerte stehen in **Übersicht**. Für den Verlauf über die Zeit eignet sich
**Figures** unter «1 · Preis und Nachfrage», weil dort Preis und Buchungsrate gemeinsam
dargestellt sind.

Wollen Sie die Zahlen nebeneinanderlegen, laden Sie aus dem Ansicht **Dateien** die
Datei `timeseries/properties.csv` beider Läufe herunter — sie enthält alle
Systemgrößen je Runde in tabellarischer Form.
