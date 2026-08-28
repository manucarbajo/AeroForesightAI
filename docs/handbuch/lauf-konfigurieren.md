Der Editor unter **Simulation starten** hat sechs Tabs. Sie sind so geordnet,
dass die ersten Entscheidungen zuerst kommen — wer nur den ersten Tab anfasst,
bekommt bereits einen sinnvollen Lauf.

## Überblick

Die fünf Entscheidungen, die einen Lauf prägen: von welcher Annahmenwelt er
ausgeht, wie lang er ist, wie oft er wiederholt wird und ob mit oder ohne
Sprachmodell gerechnet wird. Ganz unten steht in einem Satz, was gleich passiert;
er läuft beim Tippen mit.

Für die meisten Fragen reicht dieser Tab.

## Rahmenbedingungen

Die Ausgangslage. Oben die sieben Faktoren mit Namen und Leitfrage, darunter die
Systemgrößen für Politik, Kosten und Konjunktur.

Jede Systemgröße hat einen Startwert und kann über Regeln einen zeitlichen
Verlauf bekommen: «ab Runde 10 springt die CO₂-Abgabe auf 120» oder «ab Runde 5
über acht Runden hochfahren auf 200». Aufklappen, Anzahl der Regeln setzen,
Werte eintragen.

Der Schalter **Eigene Werte anwenden** ist hier der wichtigste. Steht er auf aus,
rechnet der Lauf mit den Konfigurationsdateien und ignoriert alles, was Sie auf
diesem Tab eingestellt haben.

## Nachfrage & Preisbildung

Zwei Regelkreise. Oben das Preisverhalten der Airline, bei dem die Zielauslastung
die entscheidende Größe ist. Darunter die Sättigung. Dann die Segmente der
Bevölkerung mit ihren Anteilen, und zuletzt die Verteilungen für
Zahlungsbereitschaft und Umweltbewusstsein.

Die beiden Speichern-Knöpfe auf diesem Tab schreiben in `configs/properties.json`
und wirken damit über den einzelnen Lauf hinaus. Alles andere im Editor gilt nur
für den nächsten Start.

## Lauf & Ablage

Name und Fragestellung des Laufs, Mehrfachläufe, und in der Feinabstimmung die
Auswahl der Konfigurationsdateien. Name und Fragestellung erscheinen im Bericht
und in der Run-Liste; ohne sie sind mehrere Läufe später schwer auseinanderzuhalten.

## Technik

Sprachmodell, Reproduzierbarkeit und Ausgaben. Nichts davon verändert die
berechneten Zahlen — mit einer Ausnahme, dem Zufallsstartwert.

Ein einzelner Lauf ist auch ohne eigenen Startwert wiederholbar — ohne Angabe
gilt ein Standardwert. Der Startwert zählt an zwei Stellen: Setzen Sie ihn
fest, wenn Sie **Wiederholungen** rechnen und alle dieselbe Bevölkerung sehen
sollen (ohne ihn bekommt jede Wiederholung eine eigene Ziehung — genau dafür
gibt es sie), oder wenn Sie denselben Aufbau bewusst mit einer **anderen**
Ziehung sehen wollen.

## Kontrolle

Der letzte Blick vor dem Start. Oben in Klartext, was gleich passiert, darunter
sechs Kacheln mit den Werten, die einen zweiten Blick lohnen.

Darunter erscheinen Warnungen für die drei Fälle, die später enttäuschen:
Wiederholungen ohne festen Zufallsstartwert, abgeschaltete Szenario-Erzeugung und
abgeschaltete eigene Werte. Ganz unten lässt sich der Stand als eigenes Preset
sichern.

Steht dort ein **roter Kasten**, ist die Konfiguration nicht lauffähig. Er nennt
jeden Fehler einzeln — und der Knopf «Start» weist den Lauf dann auch ab, statt
ihn anzufangen und unterwegs scheitern zu lassen. Geprüft wird:

| Einstellung | Zulässig | Wann geprüft |
|---|---|---|
| Zufallsstartwert | 0 oder größer | immer |
| Länge des Laufs | mindestens 1 Tick | immer |
| Ollama-Modell | nicht leer | nur bei «Mit Sprachmodell» |
| Kreativität der Agenten | 0 bis 2 | nur bei «Mit Sprachmodell» |
| Antwortlänge | mindestens 1 | nur bei «Mit Sprachmodell» |

Die letzten drei betreffen ausschließlich Ollama. In den Modi «Ohne
Sprachmodell» und «Nur Zahlen» wird gar kein Client aufgebaut — dort dürfen die
Felder also stehen, wie sie wollen, und blockieren nichts.

Der **Name des Laufs** darf leer bleiben — dann greift der Name aus
`simulation_config.json`. Leer sein darf er nur dort nicht.

Dazu kommt die Referenz-Integrität: Verweist ein Agentenprofil in
`agent_profiles.json` auf einen Faktor, den es nicht gibt, oder auf eine
unbekannte Abhängigkeit, wird das ebenfalls hier gemeldet. Beides würde sonst
lautlos ins Leere laufen — der Agent sähe den Faktor einfach nicht.

## Feinabstimmung

In jedem Block steht vorn die Einstellung, die die Wirkung bestimmt. Alles
Weitere liegt hinter «Feinabstimmung». Verborgen ist nichts — die Vorgabewerte
tragen einen sinnvollen Lauf, und wer aufklappt, weiß in der Regel warum.

Die vollständige Liste aller Einstellungen mit Einheit und Config-Feld steht
unter [Alle Einstellungen](/doku/ref-parameter).
