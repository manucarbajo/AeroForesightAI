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

## Wo Sie vergleichen

Die Endwerte stehen in **Übersicht**. Für den Verlauf über die Zeit eignet sich
**Figures** unter «1 · Preis und Nachfrage», weil dort Preis und Buchungsrate gemeinsam
dargestellt sind.

Wollen Sie die Zahlen nebeneinanderlegen, laden Sie aus dem Ansicht **Dateien** die
Datei `timeseries/properties.csv` beider Läufe herunter — sie enthält alle
Systemgrößen je Runde in tabellarischer Form.
