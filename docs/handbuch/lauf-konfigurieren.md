Wenn Sie **Einrichten** öffnen, steht zuerst eine Frage: Womit möchten Sie
anfangen? Drei Wege stehen zur Wahl.

**Neuen Lauf einrichten** führt in die Schrittfolge unten — die Fragen der Reihe
nach. Das ist der Weg, wenn Sie den Lauf zusammenstellen wollen.

**Szenario-Vergleich starten** rechnet alle hinterlegten Szenarien nacheinander
und legt sie am Ende nebeneinander. Sie landen unmittelbar bei **Prüfen &
Starten**; wie viele Ticks gerechnet werden, steht dort und lässt sich vorher
noch ändern.

**Letzte Einstellungen weiterverwenden** springt ebenfalls ans Ende, mit dem, was
zuletzt eingestellt war — ohne die Fragen erneut durchzugehen. Dieser Weg ist
ausgegraut, solange Sie in dieser Sitzung nichts geändert haben; es gäbe dann
nichts weiterzuverwenden.

Die beiden ersten Wege sagen jeder genau eine Sache, und sie stellen sie auch
ein: «Neuen Lauf einrichten» heißt *ein* Lauf, «Szenario-Vergleich» heißt *alle*.
Wer den Vergleich einmal gewählt hat und danach doch einen einzelnen Lauf will,
bekommt ihn also, ohne ein Kästchen suchen zu müssen.

Einen Weg zurück gibt es auch: **Zurück** auf dem ersten Schritt führt wieder auf
diese Auswahl.

## Die Schrittfolge

Einrichten geht seit August 2026 Schritt für Schritt. Sie beantworten eine
Frage, klicken auf **Weiter**, und kommen zur nächsten; **Zurück** führt jederzeit
zum vorigen Schritt, und links steht die ganze Liste — Sie können jeden Schritt
direkt anspringen. Bei jedem Wechsel springt die Ansicht an den Anfang des neuen
Schritts, damit Sie dessen Frage sehen und nicht dort landen, wo Sie im vorigen
gerade gelesen haben.

**Drei Schritte genügen.** Was gerechnet wird, wie weit, und womit: Danach ist
alles Weitere mit sinnvollen Werten vorbelegt, und der Knopf **Direkt zum Start**
bringt Sie ans Ende. Die Schritte vier bis sieben sind als *optional*
gekennzeichnet — Rahmenbedingungen, Nachfrage & Preisbildung, Lauf & Ablage,
Technik. Wer sie braucht, findet sie; wer nicht, geht daran vorbei.

**Die Liste links sagt Ihnen, wo Sie waren.** Ein Haken steht an den Schritten,
die Sie wirklich geöffnet hatten; ein Strich an denen, an denen Sie
vorbeigesprungen sind; ein leerer Kreis an denen, die noch kommen. Wenn Sie
etwas übergangen haben, steht die Zahl unter der Liste. Das ist kein Tadel —
sechs der acht Schritte dürfen übersprungen werden. Es beantwortet nur die
Frage, die man am Ende hat: *Habe ich etwas übersehen?*

> **Bis August 2026 log die Liste.** Sie richtete sich allein danach, wo Sie
> gerade stehen: Alles davor bekam einen Haken. Wer über «Szenario-Vergleich
> starten» direkt zum letzten Schritt sprang, sah dort sieben Haken für sieben
> Schritte, die er nie gesehen hatte.

**Was den Lauf verhindert, hält Sie auch auf.** Steht in einem Schritt ein Wert,
mit dem der Lauf nicht starten kann, ist **Weiter** dort gesperrt, und daneben
steht, woran es liegt. In allen anderen Schritten bleibt **Weiter** offen — was
Sie an dieser Stelle gar nicht einstellen können, soll Sie dort auch nicht
festhalten. **Lauf starten** ist gesperrt, solange irgendwo ein solcher Wert
steht; die Meldung sagt dann, in welchem Schritt er zu beheben ist.

> **Bis August 2026 hielt nichts auf.** Die Fehler wurden angezeigt, aber
> **Weiter** war nie gesperrt: Man konnte durch alle acht Schritte gehen und erst
> beim Klick auf **Lauf starten** erfahren, dass Schritt 2 ungültig war.

Der letzte Schritt heißt **Prüfen & Starten**: Dort steht, was gleich passiert,
und daneben die beiden Wege hinaus — den Lauf starten, oder die Einstellungen als
Szenario speichern und später wieder aufrufen.

Solange Sie einrichten, gehört Ihnen der ganze Bildschirm: Bedienfeld, Telemetrie
und Zeitleiste treten zurück. Einrichten ist eine Sache für sich, und eine Szene
daneben, die einen *anderen* Lauf zeigt, lenkt nur ab.

Gestartet wird am Ende der Schrittfolge — oder jederzeit im Bedienfeld links,
sobald Sie das Einrichten verlassen haben. Beide Knöpfe führen in denselben
Lauf; der Bildschirm wechselt dabei auf den **Leitstand**, damit Sie sehen, was
Sie angestoßen haben.

Bis P1.6 stand dieser Bereich in der linken Spalte selbst. Das war eine
Fehlkonstruktion — sechzig Eingabefelder in einer 336 px breiten Spalte ergaben
zehn Bildschirme Höhe, und der Start-Knopf lag sechs davon tief. Einrichten
braucht Fläche, Beobachten braucht Ruhe; beides in dieselbe Zone zu legen geht
nur zulasten einer von beiden.

Wer nur die drei Entscheidungen anfasst, bekommt einen sinnvollen Lauf.

## Die drei Entscheidungen

**1. Was soll gerechnet werden?** Die Annahmenwelt: die Standard-Ausgangslage
aus `configs/`, eines der vorbereiteten Szenarien, oder das, was Sie sich in den
Schritten vier bis sieben selbst zusammengestellt haben. Unter jedem Szenario steht, wofür es
steht; aufklappbar dazu die Begründung, warum es so aufgebaut ist.

**2. Wie weit reicht der Lauf?** Die Länge in Ticks. Hinter «Feinabstimmung»
die Wiederholungen und der Schalter «Alle Szenarien vergleichen» — denselben
Schalter legt der Einstieg um, wenn Sie dort «Szenario-Vergleich starten»
wählen.

**3. Womit wird gerechnet?** Der Rechenmodus, dazu die Auskunft, ob Ollama
gerade erreichbar ist. Hinter «Feinabstimmung» der Zufallsstartwert.

Zu jeder Einstellung steht die kurze Wirkungsbeschreibung direkt unter dem Feld,
die ausführliche hinter «Mehr dazu» daneben. Die vollständige Liste aller
Einstellungen mit Einheit und Config-Feld steht unter
[Alle Einstellungen](/doku/ref-parameter).

## Preflight: der letzte Blick vor dem Start

Unter den drei Schritten steht in Klartext, was gleich passiert, darunter sechs
Kacheln mit den Werten, die einen zweiten Blick lohnen.

Daneben erscheinen Warnungen für die Fälle, die später enttäuschen:
Wiederholungen ohne festen Zufallsstartwert, abgeschaltete Szenario-Erzeugung,
und — außerhalb des Szenario-Modus — abgeschaltete eigene Werte.

Steht dort ein **roter Kasten**, ist die Konfiguration nicht lauffähig, und der
Knopf «Start» weist den Lauf dann auch ab, statt ihn anzufangen und unterwegs
scheitern zu lassen. Wo sich ein Befund einem einzelnen Feld zuordnen lässt,
steht er zusätzlich **direkt an diesem Feld**; der rote Kasten nennt dann nur
noch, wie viele es sind. Geprüft wird:

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
lautlos ins Leere laufen — der Agent sähe den Faktor einfach nicht. Solche
Befunde hängen an keinem Eingabefeld und stehen deshalb nur im roten Kasten.

## Alle Einstellungen

### Rahmenbedingungen

Die Ausgangslage. Oben die sieben Faktoren mit Namen und Leitfrage, darunter die
Systemgrößen für Politik, Kosten und Konjunktur.

Jede Systemgröße hat einen Startwert und kann über Regeln einen zeitlichen
Verlauf bekommen: «ab Runde 10 springt die CO₂-Abgabe auf 120» oder «ab Runde 5
über acht Runden hochfahren auf 200». Aufklappen, Anzahl der Regeln setzen,
Werte eintragen.

Der Schalter **Eigene Werte anwenden** ist hier der wichtigste. Steht er auf
aus, rechnet der Lauf mit den Konfigurationsdateien und ignoriert alles, was Sie
auf diesem Tab eingestellt haben. Ist oben ein Szenario gewählt, greifen diese
Werte ohnehin nicht — dann gilt allein das Szenario.

### Nachfrage & Preisbildung

Zwei Regelkreise. Oben das Preisverhalten der Airline, bei dem die Zielauslastung
die entscheidende Größe ist. Darunter die Sättigung. Dann die Segmente der
Bevölkerung mit ihren Anteilen, und zuletzt die Verteilungen für
Zahlungsbereitschaft und Umweltbewusstsein.

Die beiden Speichern-Knöpfe auf diesem Tab schreiben in `configs/properties.json`
und wirken damit über den einzelnen Lauf hinaus. Alles andere im Editor gilt nur
für den nächsten Start.

### Lauf & Ablage

Name und Fragestellung des Laufs — sie erscheinen im Bericht und in der
Lauf-Auswahl; ohne sie sind mehrere Läufe später schwer auseinanderzuhalten.
Darunter «Als Szenario sichern», mit dem der aktuelle Stand als eigenes Preset
unter `configs/sweeps/` landet, die Auswahl der Konfigurationsdateien, und ganz
unten die Rohdaten: was tatsächlich an die Simulation übergeben wird.

### Technik

Welches Sprachmodell unter welcher Adresse, wie oft ein Zwischenstand
geschrieben wird, und was am Ende ausgegeben wird. Nichts davon verändert die
berechneten Zahlen. **Ob** überhaupt ein Sprachmodell beteiligt ist und mit
welchem Zufallsstartwert gerechnet wird, entscheiden Sie oben im dritten
Schritt.

Ein einzelner Lauf ist auch ohne eigenen Startwert wiederholbar — ohne Angabe
gilt ein Standardwert. Der Startwert zählt an zwei Stellen: Setzen Sie ihn fest,
wenn Sie **Wiederholungen** rechnen und alle dieselbe Bevölkerung sehen sollen
(ohne ihn bekommt jede Wiederholung eine eigene Ziehung — genau dafür gibt es
sie), oder wenn Sie denselben Aufbau bewusst mit einer **anderen** Ziehung sehen
wollen.

## Feinabstimmung

In jedem Block steht vorn die Einstellung, die die Wirkung bestimmt. Alles
Weitere liegt hinter «Feinabstimmung». Verborgen ist nichts — die Vorgabewerte
tragen einen sinnvollen Lauf, und wer aufklappt, weiß in der Regel warum.
