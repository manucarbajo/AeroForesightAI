Der Ticketpreis wird nicht vorgegeben. Er entsteht in jeder Runde neu, aus den
Kosten der Airline und ihrer Reaktion auf die beobachtete Auslastung — dem, was
in der Branche Yield Management heißt.

## Der Regelkreis

Die Airline hat eine Zielauslastung. Am Ende jeder Runde vergleicht sie die
tatsächliche Buchungsrate damit. Liegt die Buchungsrate über dem Ziel, ist die
Nachfrage stärker als erwartet und der Preis steigt. Liegt sie darunter, fällt
er. Der veränderte Preis wirkt in der nächsten Runde auf die
Kaufentscheidungen — und verändert damit die Buchungsrate, die die nächste
Preisanpassung auslöst.

Das ist der Grund, warum eine niedrigere Zielauslastung tendenziell zu höheren
Preisen führt: Die Airline zieht dann schon bei schwächerer Nachfrage an.

## Wie stark angepasst wird

Drei Größen bestimmen die Heftigkeit der Reaktion. Die **Reaktionsstärke** legt
fest, wie kräftig auf eine Abweichung reagiert wird. Die **Dämpfung** bremst das
zusätzlich ab. Und der **Preisdeckel** begrenzt hart, wie weit sich der Preis in
einer einzelnen Runde bewegen darf, nach oben wie nach unten.

Der Deckel ist der Grund, warum ein Preis manchmal über mehrere Runden
gleichmäßig steigt, obwohl die Nachfrage längst eingebrochen ist: Das Modell
lässt ihn nicht schneller fallen, als ein realer Anbieter es durchsetzen könnte.

## Die Untergrenze

Unter die Grenzkosten fällt der Preis nie. Welcher Anteil der Stückkosten als
echte Grenzkosten gilt, stellt die **Preisuntergrenze** ein. Steuern und Gebühren
kommen darauf noch obendrauf.

Damit sind Verkäufe unterhalb der Vollkosten möglich — die Airline kann
Marktanteil verteidigen und Fixkosten nur teilweise decken — aber Dumping unter
die tatsächlichen Grenzkosten ist ausgeschlossen. Klebt der Preis im Verlauf über
viele Runden an einem Wert, ist meist diese Grenze erreicht.

## Woraus sich der Preis zusammensetzt

Der Preis besteht aus einem Kostenanteil und einer Marge. Der Kostenanteil folgt
den Systemgrößen für Treibstoff, Wartung und Personal, die Marge ist das, woran
die Airline dreht. In der Ansicht **Diagramme** zeigt die Aussage «1 · Preis und Nachfrage» beides
übereinandergestapelt.

Auf den Kostenanteil wirken zusätzlich die Systemgrößen, die als Steuer oder
Gebühr angelegt sind — eine CO₂-Abgabe erhöht ihn prozentual, eine
Flughafengebühr um einen festen Betrag. Welche Größe wie wirkt, steht in der
Referenz unter [Systemgrößen](/doku/ref-systemgroessen).

## Regulatorische Kostentreiber

Zusätzlich zu den Systemgrößen kann `properties.json` einzelne Kostentreiber
führen — EU-ETS, RefuelEU, CORSIA, eine nationale Luftverkehrsabgabe, ein
Lärmzuschlag. Jeder trägt einen Betrag und eine Bedingung, unter der er
überhaupt anfällt: der EU-ETS-Aufschlag etwa nur, solange die Regulierung
streng ist. Welche Bedingungen dort stehen dürfen, steht unter
[Die Konfigurationsdateien](/doku/ref-config).

Ein Kostentreiber ohne Bedingung — im Auslieferungsstand die
Flughafen-Infrastrukturabgabe — gilt immer. Die übrigen hängen an einem
Faktorzustand und schalten sich zu, wenn er eintritt.

Bis August 2026 rechnete eine der beiden Stellen, die den Kostendruck bilden,
ohne die Faktoren — dort konnte kein bedingter Treiber greifen. Sichtbar war das
vor allem am Preis der ersten Runde, der ohne die Regulierungskosten zu niedrig
begann und über die Preisrückkopplung den ganzen Verlauf mitzog. Das ist
behoben; beide Stellen rechnen mit demselben Zustand.

## Wenn der Regelkreis stört

Für manche Fragen ist die Preisreaktion im Weg, etwa wenn Sie allein wissen
wollen, wie die Bevölkerung auf eine Abgabe reagiert. Schalten Sie dann unter
**Nachfrage & Preisbildung** die Preisanpassung ab. Der Preis folgt dann nur noch
den Kosten, und die Nachfrageseite wird isoliert sichtbar.
