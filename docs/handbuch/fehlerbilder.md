Manche Verläufe sehen falsch aus und sind es nicht. Andere sehen unauffällig aus
und verraten, dass eine Einstellung nicht gegriffen hat. Diese Sammlung ordnet
die häufigsten Beobachtungen ein.

## Die Buchungsrate fällt stetig

Das ist der Normalfall, kein Fehler. In den ersten Runden bucht, wer buchen will;
danach ist ein wachsender Teil der Bevölkerung gesättigt. Siehe
[Sättigung](/doku/saettigung).

Auffällig wird es erst, wenn die Rate gegen null geht und dort bleibt. Dann ist
entweder die Erholung je Runde zu niedrig eingestellt oder der Preis über die
Zahlungsbereitschaft fast aller Personen gestiegen.

## Die Buchungsrate bleibt konstant

Hier lohnt Misstrauen. Eine über den ganzen Lauf unveränderte Rate heißt meist,
dass keine Rückkopplung greift.

Prüfen Sie zuerst, ob unter **Nachfrage & Preisbildung** die Preisanpassung
eingeschaltet ist und ob unter **Technik** «Marktmodell abschalten» aus ist.
Prüfen Sie dann, ob **Eigene Werte anwenden** aktiv ist — sonst rechnet der Lauf
mit der Standard-Ausgangslage und ignoriert Ihre Änderungen.

## Der Preis klebt an einem Wert

Zwei Grenzen kommen infrage. Entweder ist die Preisuntergrenze erreicht, dann
kann der Preis nicht weiter fallen, obwohl die Nachfrage schwach ist. Oder der
Preisdeckel je Runde ist so eng gesetzt, dass sich der Preis nur in winzigen
Schritten bewegen darf.

In der Ansicht **Figures** zeigt die Aussage «1 · Preis und Nachfrage» die Zusammensetzung aus
Kosten und Marge. Ist die Marge nahe null, liegt der Preis an der Untergrenze.

## Der Preis schwingt hin und her

Zu heftige Reaktion. Senken Sie die Reaktionsstärke oder erhöhen Sie die
Dämpfung, beide unter **Nachfrage & Preisbildung** in der Feinabstimmung.

Ein weiterer Verdächtiger ist die Kopplung an die Buchungen. Steht sie nahe 1,
folgt die Nachfrage vollständig den beobachteten Buchungen, was den Regelkreis
sehr reaktiv und damit schwingungsanfällig macht.

## Eine Änderung zeigt keine Wirkung

Vier Ursachen, in der Reihenfolge ihrer Häufigkeit.

Erstens: **Eigene Werte anwenden** ist ausgeschaltet. Das ist mit Abstand der
häufigste Fall; im Preflight über dem Start-Knopf erscheint dafür eine Warnung.

Zweitens: Der Modus steht auf «Szenario-Preset». Dann rechnet der Lauf mit den
Werten des Presets, nicht mit Ihren.

Drittens: Die Größe wirkt erst ab einer Schwelle. Die CO₂-Abgabe etwa geht erst
oberhalb von 50 EUR je Tonne in die Kaufentscheidung ein.

Viertens: Der Lauf war zu kurz. Rückkopplungen brauchen Runden; bei fünf Ticks
ist oft noch nichts zu sehen.

## Die Ansicht «Szenario» ist leer

Entweder wurde der Lauf mit «Keine Szenarien erzeugen» gerechnet, oder er wurde
abgebrochen, bevor die Auswertung lief. Im ersten Fall hilft der Knopf «Szenarien
neu erzeugen» im selben Tab — der Lauf muss dafür nicht wiederholt werden.

## Der Lauf startet gar nicht erst

Statt eines Fortschrittsfensters erscheint ein roter Kasten mit einer Liste. Dann
hat die Konfiguration einen Fehler, der den Lauf sicher scheitern ließe — er wird
deshalb abgewiesen, bevor er anfängt.

Die häufigsten Fälle: ein negativer Zufallsstartwert, ein Lauf über null Ticks,
oder ein Agentenprofil, das auf einen Faktor verweist, den es nicht gibt. Im
Modus «Mit Sprachmodell» kommen die Ollama-Einstellungen dazu — Kreativität
außerhalb von 0 bis 2, Antwortlänge 0, leerer Modellname. Jeder Punkt der Liste
nennt das betroffene Feld; im Preflight über dem Start-Knopf steht dieselbe Liste schon vor
dem Klick auf «Start».

Angezeigt werden immer **alle** Fehler auf einmal, nicht einer nach dem anderen —
eine Konfiguration lässt sich so in einem Durchgang reparieren.

**Auf der Kommandozeile ist es dieselbe Liste.** `python -m src.run_simulation`
schreibt sie nach `stderr` und endet mit dem Code **2** — nicht 1: So lässt sich
«die Eingabe war falsch» von «das Programm ist abgestürzt» unterscheiden, ohne die
Meldung zu lesen, was für Skripte und CI der Unterschied ist. Bis September 2026
kam an dieser Stelle ein Python-Traceback, in dem die eigentliche Meldung unterging;
die Prüfung war schon richtig, nur ihre Darstellung nicht.

Ein Traceback auf der Kommandozeile heißt seither: **kein Konfigurationsfehler,
sondern ein Programmfehler.** Er gehört gemeldet, mit den vollen Zeilen.

## Der Zwischenstand passt nicht zu dieser Fassung

Beim Fortsetzen eines Laufs erscheint eine Meldung, dass der Zwischenstand eine
andere Formatversion trägt. Dann stammt er aus einer anderen Fassung des Programms,
und was darin steht, muss nicht mehr zu dem passen, was der heutige Code erwartet.

Der Lauf wird deshalb **nicht** fortgesetzt: Ein stillschweigend geladener
Zwischenstand mit fehlenden Feldern rechnete mit Vorgabewerten weiter, die niemand
gewählt hat. Es gibt bewusst keine Umwandlung alter Zwischenstände — der Lauf wird
neu gestartet. Zwischenstände sind Fortsetzungspunkte, kein Archiv.

## Der Lauf ist als beeinträchtigt markiert

Über den Tabs steht ein gelber Hinweis, dass Aufrufe an das Sprachmodell
unbeantwortet blieben. Das heißt nicht, dass die Zahlen falsch sind: Preise,
Buchungsraten und Faktorzustände rechnet Python, unabhängig vom Sprachmodell.
Fehlen können die Beiträge der Akteure und Teile der Deutung — an den
betroffenen Stellen hat der jeweilige Akteur ausgesetzt.

Welche Runden es traf und woran es lag, steht in `llm_incidents.json`; im Tab
**Dateien** lässt sie sich öffnen. Die häufigste Ursache ist ein nicht laufendes
Ollama. Prüfen Sie im Tab **Technik**, ob der angegebene Endpunkt erreichbar
ist, und starten Sie das Modell gegebenenfalls mit `ollama run llama3.2`.

Ein Lauf, der bewusst ohne Sprachmodell gerechnet wurde, ist **nicht**
beeinträchtigt und bekommt diesen Hinweis nicht. Der Unterschied ist Absicht:
Der Hinweis meldet, dass etwas nicht funktioniert hat, nicht dass etwas
abgeschaltet war.

## Neben `figures/` liegt ein `figures.neu/`

**Was Sie sehen:** Im Verzeichnis des Laufs steht ein zweiter Ordner mit einem
Namen wie `figures.neu` oder `figures.alt`.

**Was das heißt:** Die Erzeugung der Auswertungsgrafiken ist abgebrochen. Der
Ordner ist ihr Rest, kein Ergebnis — was darin liegt, ist unvollständig.

**Was gilt:** Der Satz unter `figures/` ist davon **unberührt**. Er stammt noch
vom letzten geglückten Durchlauf und ist vollständig; die Bilder entstehen
bewusst erst nebenan und ziehen nur als ganzer Satz um.

**Was zu tun ist:** In der Ansicht **Figures** unter «PNG-Export» neu erzeugen.
Gelingt es, verschwindet der Rest von selbst. Gelingt es wieder nicht, steht der
Grund im Protokoll des Laufs.

## Sehr wenige Ereignisse

Die Übersicht zählt Ereignisse. Sind es auffällig wenige, wurde vermutlich ohne
Agenten-Dialog gerechnet. Die Kennzahlen sind dann trotzdem vollständig, es fehlt
nur die Deutung.

## Wenn nichts davon passt

Der Ansicht **Abfrage** blendet über «Artefakt-Checks anzeigen» eine Prüfung ein, die
die erzeugten Dateien gegeneinander abgleicht. Sie sagt unabhängig vom
Sprachmodell, ob ein Lauf in sich stimmig ist.
