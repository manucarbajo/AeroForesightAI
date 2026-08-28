# Audit: Der Einrichten-Assistent

**Stand:** 2026-08-28 · **Gegenstand:** `dashboard/web/config_editor/` (Stand `1700979`) · **Verfahren:** unabhängig, ohne Bezug auf die Abnahmekriterien von P1.1/P1.5/P1.6/P1.7

Dieses Dokument prüft den Wizard gegen eigene Maßstäbe, nicht gegen die des Projektplans. Wo eine Aussage gemessen wurde, steht die Messung dabei; wo sie aus dem Code folgt, steht die Fundstelle. Die Umsetzungsvorschläge stehen ab [Teil 3](#teil-3--neuausrichtung).

## Methodik

Gemessen am laufenden System (eigene Instanz auf Port 8531, Codestand des Arbeitszweigs), Fenster 1280 × 720, Zone «Einrichten» 1040 px breit, Inhaltsspalte 760 px, sichtbare Höhe 664 px. Zusätzlich 375 × 812. Ergänzt um Codelesen in `dashboard/web/config_editor/`, `dashboard/web/pages/launch.py`, `dashboard/run_launcher.py` und `src/orchestration/scenario_sweeps.py`.

Nicht gemessen: reale Nutzer. Alle Aussagen über Verständlichkeit sind Fachurteil, keine Empirie — sie sind als solche gekennzeichnet.

---

## Teil 1 — Audit

### A. Sinnhaftigkeit: Was der Wizard verspricht und was er einlöst

#### A1 — Auf dem Sweep-Pfad verspricht der Wizard Kontrolle, die er nicht hat · **kritisch**

`run_single_sweep` (`src/orchestration/scenario_sweeps.py:250`) baut seinen Runner selbst und schreibt drei Dinge fest, die der Wizard zu erfragen vorgibt:

```
deterministic_only=True      # Schritt 3 «Womit wird gerechnet?» ist wirkungslos
seed=SWEEP_SEED              # der Zufallsstartwert aus Schritt 3 ebenso
checkpoint_interval=0        # das Feld aus Schritt 7 ebenso
OllamaClient(OllamaConfig())  # und trotz «deterministisch» wird Ollama gerufen
```

Vom gesamten Entwurf erreicht genau **ein** Feld den Sweep-Lauf: `rounds`, als `ticks_override` (`dashboard/run_launcher.py:209`). Alles andere — Faktorlage, Systemgrößen, Bevölkerung, Preisbildung, Modellname, Ausgaben — wird von den Presets unter `configs/sweeps/` gestellt.

Gemessen, nach einem Klick auf «Szenario-Vergleich starten», Schritt 8 im Wortlaut:

> «Sie starten alle 8 hinterlegten Szenarien nacheinander über 40 Ticks, ausgehend von **der Standard-Ausgangslage aus `configs/`**, **ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind Platzhalter**.»

Drei Aussagen, drei Mal falsch: Die Ausgangslage ist je Szenario eine andere; es gibt gar keine Agenten-Texte (deterministisch); und ein Sprachmodell wird sehr wohl gerufen, für den Szenario-Text am Ende. Dazu sechs Kacheln — Ziel-Auslastung 37 %, Segmente 5, Aktive Systemgrößen 13, Zufallsstartwert 42 — die allesamt den Entwurf zeigen und nicht den Lauf.

Das ist derselbe Fehlertyp, den die harten Invarianten für die Engine verbieten («Was der Code nicht tut, darf die Doku nicht behaupten»), nur eine Ebene höher: Die **Oberfläche** behauptet es. Sie ist die Doku, die der Nutzer wirklich liest.

#### A2 — Weg 2 überschreibt still die Bauart jedes Szenarios · **hoch**

`ticks_override=int(config.rounds) if config.rounds else None` — und `rounds` hat immer einen Wert. Jedes Preset läuft also mit der Länge des Entwurfs, nicht mit seiner eigenen `max_ticks`.

Schritt 1 warnt genau davor: «Angelegt ist es auf **{max_ticks} Ticks** — die Länge stellen Sie im nächsten Schritt selbst ein.» Der Weg «Szenario-Vergleich starten» springt aber direkt auf Schritt 8 und überspringt diesen Schritt. Wer den Vergleich über den vorgesehenen Weg startet, sieht die Frage nie und bekommt trotzdem ihre Wirkung.

#### A3 — «Erledigt» ist eine Behauptung, keine Messung · **hoch**

`_rail_entry` (`wizard.py:283`) vergibt den Zustand rein nach Position: `index < current` ⇒ `done`, mit Häkchen. Gemessen nach einem Klick auf «Szenario-Vergleich starten»:

```
rail: ["done","done","done","done","done","done","done","current"]
```

Sieben grüne Häkchen für sieben Schritte, die nie auf dem Schirm standen. Dasselbe nach «Direkt zum Start». Ein Fortschrittsanzeiger, der Übersprungenes als Erledigt ausweist, ist schlechter als keiner: Er nimmt dem Nutzer genau die Information, für die er da ist.

#### A4 — Es gibt kein Tor · **hoch**

`_navigate` prüft nichts. `wizard-next` ist nie `disabled`, `wizard-start` nur während eines laufenden Laufs. Fehler werden gezeigt (`_live` füllt `cfg-error` je Feld, der Preflight sammelt sie) — aber sie halten nichts auf. Man kann durch acht Schritte laufen und erst beim Start erfahren, dass Schritt 2 ungültig war.

Ein Wizard unterscheidet sich von einer Reiterleiste dadurch, dass «Weiter» etwas garantiert. Ohne Tor ist diese Schrittfolge eine Reiterleiste mit zusätzlichen Klicks — und die Reiterleiste hatte P1.7 gerade abgeschafft.

#### A5 — Der Rückweg stimmt nicht · **mittel**

Zwei der drei Wege des Einstiegs landen auf Schritt 8. «Zurück» rechnet dort `jetzt - 1` und landet auf Schritt 7 «Technik» — gemessen: `afterBack: "SCHRITT 7 VON 8"`. Wer über «Szenario-Vergleich» kam, steht nach einem Klick auf «Zurück» in den Sprachmodell-Feineinstellungen, die er nie sehen wollte und die auf seinem Pfad ohnehin wirkungslos sind (A1).

Der Zurück-Knopf braucht einen Verlauf, keine Subtraktion.

#### A6 — Der Wizard hat versteckten Schreibzugriff auf die ausgelieferte Konfiguration · **kritisch**

Innerhalb der als *optional* und «bereits sinnvoll vorbelegt» gekennzeichneten Schritte 4 und 5 liegen fünf Bedienelemente, die sofort und ohne Rückfrage `configs/properties.json` verändern (`config_editor/__init__.py:_handle_action`):

| Element | Schritt | Wirkung |
| --- | --- | --- |
| «Entfernen» am Segment | 5 | `save_population_edits_to_file` — Segment ist aus der Datei weg |
| «Größe dauerhaft löschen» | 4 | `delete_custom_property` — Systemgröße ist aus der Datei weg |
| «Als Standard speichern» | 5 | schreibt Markt-Feedback in die Datei |
| «Bevölkerung als Standard speichern» | 5 | schreibt Population und Sättigung in die Datei |
| «Größe anlegen» | 4 | schreibt eine neue Systemgröße in die Datei |

Kein Bestätigungsdialog, kein Undo, keine Sicherung. Die Wirkung reicht über den Lauf hinaus, über die Sitzung hinaus und über den Nutzer hinaus — die nächste Person, die das Dashboard öffnet, arbeitet mit dem veränderten Modell, ohne es zu erfahren.

Das ist kein Bedienfehler, sondern ein Kategorienfehler: **Ein Assistent, der einen Lauf einrichtet, darf das Modell nicht ändern.** Modellpflege und Experimentkonfiguration sind zwei Tätigkeiten mit unterschiedlicher Reichweite, unterschiedlicher Umkehrbarkeit und unterschiedlichem Publikum.

#### A7 — Ein Render-Rückfall schreibt in den Entwurf · **mittel**

Gemessen mit geleerter Session, ohne eine einzige Eingabe, nur durch Klicken durch die Schrittliste:

```
Schritt 1: (keine Änderung)
Schritt 2: (keine Änderung)
Schritt 3: seed: null -> 42
Schritt 4-8: seed: null -> 42
```

Verursacher: `start_flow.mode_step` rendert `c.number("seed", int(seed if seed is not None else DEFAULT_SEED))`; `_sync` liest den gerenderten Wert und schreibt ihn zurück. Der Entwurf ist damit nicht mehr der Auslieferungszustand.

Folgen, ebenfalls gemessen:

* `touched()` (`wizard.py:214`) vergleicht gegen `initial_draft_dict()` und ist danach dauerhaft wahr.
* Der Store ist `storage_type="session"` — der Zustand überlebt das Neuladen.
* Der Einstieg bietet nach einem Reload «Letzte Einstellungen weiterverwenden — **mit dem, was zuletzt eingestellt war**» **aktiv** an, obwohl nie etwas eingestellt wurde (`resumeAtLoad: true` → `resumeAfter: false`, ohne Eingabe).

Für den Lauf selbst ist es folgenlos (`use_seed` bleibt aus), für die Oberfläche nicht. Und die Bauart ist verallgemeinerbar: Jedes Feld mit Literal-Rückfall kann so einen Wert erfinden, den niemand gewählt hat. Der brisanteste steht in `micro._FEEDBACK_FINE`: `marginal_cost_fraction` mit Rückfall **0,33**, während `configs/properties.json` **0,25** liefert — genau der in CLAUDE.md als ungeklärt vermerkte Widerspruch. Fehlt der Schlüssel im Entwurf, spritzt die Oberfläche 0,33 in den Lauf. Das ist die Klasse «erfundene Konstante», die P0.7 in der Engine mit einem AST-Wächter verboten hat; in `dashboard/` gilt das Verbot nicht.

### B. Anordnung und Flow

#### B1 — Kein einziger der acht Schritte passt auf einen Bildschirm · **hoch**

Die Zusage von P1.7 lautet: eine Frage auf dem Schirm. Gemessen bei 1280 × 720 (sichtbare Höhe 664 px):

| # | Schritt | Höhe | Bildschirme | Bedienelemente |
| --- | --- | ---: | ---: | ---: |
| 1 | Was soll gerechnet werden? | 1100 px | **2,15** | 10 |
| 2 | Wie weit reicht der Lauf? | 424 px | **1,13** | 3 |
| 3 | Womit wird gerechnet? | 457 px | **1,18** | 5 |
| 4 | Rahmenbedingungen | 1910 px | **3,37** | 104 |
| 5 | Nachfrage & Preisbildung | 2621 px | **4,44** | 64 |
| 6 | Lauf & Ablage | 1278 px | **2,42** | 13 |
| 7 | Technik | 1138 px | **2,21** | 11 |
| 8 | Prüfen & Starten | 467 px | **1,20** | 0 |

Das Abnahmekriterium von P1.7 war «nur der offene Schritt steht im DOM». Das ist erfüllt und misst das Falsche — es zählt Knoten, nicht Bildschirme. **Exakt derselbe Fehlertyp, den P1.6 an P1.1 und P1.5 gefunden hat**, ein Paket später und mit demselben Ergebnis: Die Kriterien sind grün, die Sache ist es nicht.

Schritt 4 stellt 104 Bedienelemente unter die Überschrift «Rahmenbedingungen — bereits sinnvoll vorbelegt». Schritt 5 stellt 64 unter «Nachfrage & Preisbildung».

#### B2 — Die Schrittliste mischt zwei unvereinbare Sorten · **hoch**

Schritte 1–3 sind Entscheidungen: eine Auswahl, eine Zahl, eine Auswahl — Sekunden. Schritte 4–7 sind Parameterflächen: 104, 64, 13, 11 Bedienelemente — Stunden, wenn man sie ernst nimmt. Beides in einer Liste mit gleichem Gewicht zu führen, macht die Zählung «Schritt 5 von 8» bedeutungslos: Der fünfte Schritt ist nicht ⅝ des Weges, er ist das Zehnfache aller anderen zusammen.

Die vier Parameterflächen sind erkennbar die alten Reiter unter neuem Namen — die Modulköpfe sagen es selbst («Tab «Rahmenbedingungen»», «Tab «Technik»»). Umgehängt, nicht umgebaut.

#### B3 — Der Prüfschritt prüft nichts · **hoch**

Schritt 8 zeigt einen Satz und sechs Kacheln. Er zeigt **nicht**, was gegenüber dem Standard geändert wurde. Bei 122 Eingabefeldern über sieben Schritte ist das die einzige Frage, die vor einem Start wirklich zählt — und die einzige, auf die man ohne Delta-Ansicht keine Antwort bekommt. «Auf Standard zurücksetzen» ist der einzige Umkehrmechanismus, und er wirft alles weg.

#### B4 — Kein Zeit- und Ressourcenvoranschlag · **hoch**

40 Ticks «Nur Zahlen» dauern Sekunden, 40 Ticks mit Sprachmodell Minuten, acht Szenarien ein Vielfaches. Der Wizard sagt dazu kein Wort — weder vor dem Start noch als Restzeit während des Laufs. Für eine Simulationsumgebung ist das die zentrale Erwartungssetzung; ihr Fehlen ist der Grund, aus dem Nutzer Läufe abbrechen, die fast fertig waren.

Dazu passend: **Ein laufender Lauf lässt sich nicht abbrechen.** `dashboard/web/runner.py` kennt `start`, `poll`, `progress`, `forget` — kein `cancel`.

#### B5 — Der Lauf hat keinen Namen, wo er entsteht · **mittel**

`simulation_name` liegt in Schritt 6, als optional gekennzeichnet. Wer über «Szenario-Vergleich», «Weiterverwenden» oder «Direkt zum Start» startet — also über drei von vier Wegen — kommt dort nie vorbei. Alle Läufe heißen dann «Flugverkehr Szenarioplanung MVP». Die Run-Liste ist damit nach kurzer Zeit unbrauchbar, und genau das behauptet Schritt 6 selbst: «Ohne sie sind mehrere Läufe später kaum auseinanderzuhalten.»

#### B6 — Die drei Wege sind ungleich häufig und gleich groß · **niedrig**

Weg 1 ist der Erstnutzungsfall, Weg 3 der mit Abstand häufigste Wiederholfall, Weg 2 ein Spezialfall. Alle drei haben dieselbe Fläche, dasselbe Gewicht, dieselbe Position. Fachurteil, nicht gemessen.

### C. UI-Handwerk

#### C1 — Barrierefreiheit ist nicht adressiert · **hoch**

Gemessen im laufenden DOM:

* `aria-live`-Regionen im gesamten Dokument: **0**. Schrittwechsel, Statusmeldungen (`cfg-status`) und Feldfehler sind für Screenreader stumm.
* Schrittliste: kein `role="list"`, kein `aria-current="step"`; der Zustand steckt allein in Klassenname und Symbolschrift-Ligatur.
* Kein `<form>`, keine `fieldset`/`legend` um die Radiogruppen — «Was soll gerechnet werden?» ist für einen Screenreader eine Reihe unbeschrifteter Optionen.
* Beim Schrittwechsel wandert der Fokus nicht; der clientseitige Callback scrollt nur. Nach «Weiter» steht der Fokus im Nichts.

Für ein Werkzeug, das an Hochschulen und in B2B-Kontexten laufen soll, ist das ein Beschaffungshindernis, kein Schönheitsfehler.

#### C2 — Eine Breite für acht sehr verschiedene Schritte · **mittel**

`grid-template-columns: 15rem minmax(0, 1fr)`, gemessen `240px 760px` bei 1040 px Zone. Dieselben 760 px tragen Schritt 2 mit drei Feldern (viel zu breit, die Zahl steht in einer `max-w-xs`-Insel) und Schritt 4 mit 104 (viel zu schmal, das Faktorraster fällt auf zwei Spalten zurück). Auf dem Einstieg sind die 240 px der Schrittliste reserviert, obwohl sie dort unsichtbar ist.

#### C3 — Mobil tragfähig, aber ungeplant · **niedrig**

375 × 812: kein Querlauf (gut). Aber die Schrittliste stapelt sich als acht Knöpfe **über** dem Inhalt, die klebende Fußleiste bricht auf 133 px um (16 % der Höhe), und Schritt 5 ist 3595 px hoch.

#### C4 — Was gut ist · Fairness

Nicht alles ist zu kritisieren, und drei Dinge sind ausdrücklich besser als der Branchenschnitt:

* **Progressive Offenlegung ist konsequent durchgezogen.** `ui.expert` mit «Feinabstimmung (2 Parameter)» und ausgeschriebenen Namen im Deckel ist besser als jedes «Erweitert»-Dreieck: Man weiß, was drin ist, bevor man aufklappt.
* **Der Rechenmodus als eine Auswahl statt zweier verneinter Kästchen** (`compute_mode.py`) ist eine saubere Modellierung — inklusive der Begründung, dass eine der vier Kombinationen unsinnig war.
* **Die Erklärtexte stehen am Entscheidungsort**, nicht auf einer Doku-Seite, und kommen aus einer Quelle (`glossary.py`). Das ist der Grund, warum die drei Entscheidungsschritte trotz Fachtiefe lesbar sind.
* **Die klebende Fußleiste hält «Weiter» sichtbar** — gemessen auf jedem Schritt bei y = 662 von 664 px. Das war eine echte Verbesserung.

---

## Teil 2 — Benchmark

Verglichen mit dem, was ein Experiment-Assistent in AnyLogic, COMSOL, Ansys Workbench, Simulink oder einem Foundry-Scenario-Builder leistet. Nicht verglichen mit Consumer-Onboarding — der Maßstab hier ist das Fachwerkzeug.

| Erwartung an eine professionelle Simulationsumgebung | AeroForesight heute | Lücke |
| --- | --- | --- |
| **Modell und Experiment sind getrennt.** Das Modell ist ein versioniertes Artefakt; das Experiment wählt daraus und variiert. | Der Wizard mischt beides; fünf Bedienelemente in «optionalen» Schritten schreiben ins Modell (A6). | **fundamental** |
| **Jede Abweichung von der Baseline ist gelistet, benannt, einzeln rücknehmbar.** | Kein Delta, kein Einzel-Undo; nur «alles zurücksetzen» (B3). | groß |
| **Validierung ist ein Tor**: «Weiter» sperrt, die Zusammenfassung listet Blocker mit Sprungmarke. | Kein Tor; Fehler erst beim Start (A4). | groß |
| **Laufzeit- und Ressourcenschätzung vor dem Start**, aus vergangenen Läufen. | Fehlt vollständig (B4). | groß |
| **Ein Lauf ist abbrechbar.** | Kein `cancel` im Runner (B4). | groß |
| **Experiment-Identität ist Pflicht**: Name, Fragestellung, Vergleichsgruppe. | Optional, in Schritt 6, auf drei von vier Wegen unerreichbar (B5). | mittel |
| **Reproduzierbarkeit ist vor dem Start sichtbar**: Seed, Codestand, Config-Fingerabdruck. | Existiert als Artefakt (P0.6), erscheint aber erst *nach* dem Lauf; vorher nur die Seed-Kachel. | mittel |
| **Presets sind Startpunkte, keine Zwangsjacken**: laden ⇒ editierbare Kopie, Abweichungen sichtbar. | «Werte übernehmen und selbst anpassen» ist genau richtig gebaut — aber der Sweep-Pfad ignoriert danach jede Anpassung (A1). | mittel |
| **Der Assistent beschreibt den Lauf, der wirklich stattfindet.** | Auf dem Sweep-Pfad falsch in allen drei Aussagen (A1). | **fundamental** |
| **Fortschritt ist ehrlich**: besucht, gültig, übersprungen sind drei verschiedene Zustände. | Zwei Zustände, positionsbasiert; Übersprungenes gilt als erledigt (A3). | groß |
| **Barrierefreiheit nach WCAG 2.1 AA** ist Beschaffungsvoraussetzung. | Nicht adressiert (C1). | groß |
| **Progressive Offenlegung mit benannten Inhalten.** | Vorbildlich gelöst (C4). | — |

Die beiden als *fundamental* markierten Zeilen sind keine Feature-Lücken, sondern Strukturfragen. Sie lassen sich nicht durch Nachbessern am Wizard schließen — sie verlangen einen Schnitt zwischen zwei Werkzeugen.

**Das Kernurteil in einem Satz:** Der Wizard ist handwerklich sorgfältig gebaut und konzeptionell falsch geschnitten — er ist ein Modell-Editor mit einem Experiment-Assistenten davor, und weil beides in derselben Schrittfolge steht, kann er weder das eine ruhig noch das andere schnell.

---

## Teil 3 — Neuausrichtung

### 3.1 Welche abgeschlossenen Pakete wieder geöffnet werden müssen

| Paket | Status | Entscheidung | Begründung |
| --- | --- | --- | --- |
| **P1.1** — «Simulation starten» neu bauen | ✅ | **wieder öffnen** | Das Kriterium «drei Entscheidungen genügen» ist erfüllt und misst das Falsche: Auf dem Sweep-Pfad sind zwei der drei Entscheidungen wirkungslos (A1). Zählen ersetzt nicht Wirksamkeit. |
| **P1.5** — Leitstand-Oberfläche | ✅ | **Abnahme ergänzen** | Zonen, Theme und Zeitleiste tragen. Fehlt: eine Barrierefreiheits-Größe in den Kriterien (C1). Kein inhaltlicher Rückbau. |
| **P1.6** — Einrichten/Beobachten trennen | ✅ | **bleibt** | Das Prinzip trägt und hat sich bewährt. Es ist die richtige Grundlage für den Schnitt in 3.2. |
| **P1.7** — Der Ablauf wird die Oberfläche | ✅ | **wieder öffnen** | Die Zusage «eine Frage auf dem Schirm» ist mit 1,13 bis 4,44 Bildschirmen je Schritt nicht gehalten (B1). Das Abnahmekriterium zählte DOM-Knoten. Zusätzlich: A3, A4, A5, A7. |
| **P1.8** — Gegenprobe zu P1.7 | ✅ | **Verfahren nachschärfen** | Das Ergebnis bleibt gültig; der Prüfumfang war zu eng. Die Gegenprobe hat drei gemeldete Befunde geprüft, aber keine der Zusagen **gemessen**. Genau die Messung hätte B1 gefunden. |
| **P1.3** — Szenariogestaltung neu denken | offen | **vorziehen und verschmelzen** | Der Sweep-Pfad ist die Ursache von A1 und A2. Ihn kosmetisch zu reparieren, ohne die Szenariogestaltung zu klären, wäre doppelte Arbeit. |
| **P3.6** — Stabiler Vertrag für den Run-Launcher | offen | **vorziehen** | A1 ist im Kern kein UI-Fehler, sondern ein fehlender Vertrag zwischen Wizard, `run_launcher` und `scenario_sweeps`. Ohne ihn lässt sich die Zusage aus W1.3 nicht mechanisch halten. |

Zwei Pakete bleiben ausdrücklich unangetastet: **P1.2** (Ergebnisse und Plots) und **P1.4** (Landingpage). Sie liegen hinter dem hier behandelten Schnitt.

### 3.2 Der Schnitt: zwei Werkzeuge statt eines

Die tragende Entscheidung dieses Plans, und die einzige, die vor allen Arbeitspaketen zu treffen ist:

> **Der Assistent richtet ein Experiment ein. Der Modell-Editor pflegt das Modell. Es sind zwei Orte, und nur einer davon schreibt in `configs/`.**

Daraus folgt unmittelbar:

* Der Assistent schrumpft auf das, was ein Experiment ausmacht: Ausgangspunkt, Umfang, Rechenmodus, Identität, Prüfung, Start. **Fünf bis sechs Schritte, jeder auf einem Bildschirm.**
* Die 168 Bedienelemente der heutigen Schritte 4 und 5 ziehen in den Modell-Editor — mit Fläche, mit Suche, mit sichtbarem Delta und mit einer bewussten, bestätigten Speicherung.
* A6 fällt strukturell weg, nicht durch einen Bestätigungsdialog.
* Die Zählung «Schritt n von m» wird wieder wahr, weil alle Schritte vergleichbar groß sind.

Ohne diesen Schnitt sind W3 und W4 unten nicht umsetzbar; alles andere wäre Verschieben von Feldern.

---

## Teil 4 — Arbeitspakete (P1.9)

Reihenfolge ist Absicht: erst messen, dann die Unwahrheiten, dann der Schnitt, dann das Fehlende, zuletzt das Handwerk. Jedes Paket ist **ein Commit** (siehe Teil 5).

### W0 — Messfundament (vor jedem Umbau)

Ohne diese beiden Pakete wiederholt sich der Fehler von P1.7: eine Zusage, die von einer Zählung bewacht wird statt von einer Messung.

| # | Paket | Abnahme |
| --- | --- | --- |
| **W0.1** | Höhenwächter je Schritt in `tests/test_web_overflow.py`: misst jeden Schritt bei 1280 × 720 und 1440 × 900 in Bildschirmen. | Der Test meldet den Ist-Zustand als bekannte Abweichung und schlägt fehl, sobald ein Schritt **wächst**. Deckel wird in W3 auf 1,0 gesenkt. |
| **W0.2** | Wirkungstest: welche Draft-Felder erreichen auf welchem Startpfad tatsächlich die Simulation (Einzellauf, Wiederholungen, Sweep). | Eine Tabelle im Test, mechanisch erzeugt. Ein Feld, das die UI erfragt und der Pfad verwirft, lässt den Test fehlschlagen. |

### W1 — Der Assistent sagt die Wahrheit (kritisch)

| # | Paket | Abnahme |
| --- | --- | --- |
| **W1.1** | Vertrag für den Sweep-Pfad: `run_single_sweep` nimmt Rechenmodus, Seed und Checkpoint-Intervall entgegen — **oder** der Pfad deklariert seine Fixierungen als Teil seines Vertrags. Genau eine der beiden Antworten, im Code und in CLAUDE.md. | `W0.2` ist grün: kein erfragtes Feld wird still verworfen. |
| **W1.2** | `ticks_override` nur, wenn die Länge bewusst gewählt wurde; sonst gilt `max_ticks` des Presets. | Ein Sweep über den Weg «Szenario-Vergleich» läuft mit der Länge, die Schritt 1 nennt. |
| **W1.3** | Der Preflight beschreibt den **tatsächlichen** Lauf: eigener Satz und eigene Kacheln je Startpfad; nichts Wirkungsloses wird als wirksam gezeigt. | Test: Für jeden Startpfad enthält der Preflight nur Aussagen, die `W0.2` als wirksam ausweist. |
| **W1.4** | Weg 2 führt nicht mehr an der Längenfrage vorbei — entweder über den Schritt oder als bewusste Bestätigung im Preflight. | Kein Startpfad überspringt eine Frage, deren Antwort er verwendet. |

### W2 — Der Assistent lügt nicht über den Fortschritt

| # | Paket | Abnahme |
| --- | --- | --- |
| **W2.1** | Drei Zustände in der Schrittliste statt zwei: *offen*, *besucht*, *übersprungen*. Ein Häkchen nur für tatsächlich Besuchtes. | Nach «Szenario-Vergleich» trägt kein übersprungener Schritt ein Häkchen. |
| **W2.2** | Validierungstor: «Weiter» sperrt, solange der Schritt Blocker hat, mit Begründung am Feld; «Lauf starten» sperrt bei Befunden aus `validate_draft`, mit Sprungmarke zum betroffenen Schritt. | Ein ungültiger Wert kommt nicht am Schritt vorbei. |
| **W2.3** | «Zurück» folgt einem Navigationsverlauf statt `current - 1`. | Aus Schritt 8, betreten über den Einstieg, führt «Zurück» auf den Einstieg. |

### W3 — Der Schnitt (setzt 3.2 um)

| # | Paket | Abnahme |
| --- | --- | --- |
| **W3.1** | Modell-Editor als eigener Bereich; `macro` und `micro` ziehen dorthin um, unverändert im Verhalten. | Reiner Umzug, keine Verhaltensänderung — eigener Commit vor allen Änderungen daran. |
| **W3.2** | Schreiben in `configs/` nur noch im Modell-Editor, nur mit Bestätigung, mit Anzeige der Reichweite («gilt ab sofort für alle Läufe»). | Kein Schreibpfad in `configs/` ist aus dem Assistenten erreichbar. |
| **W3.3** | Faktorlage (7 Auswahlen) bleibt als **eine** Frage im Assistenten — sie gehört zum Experiment, nicht zum Modell. | Ein Bildschirm, sieben Auswahlen. |
| **W3.4** | Schritt 1: Presets als Kachelraster mit Kennzahl statt zehn gestapelter Radiokarten. | Höhe unter 1,0 Bildschirm bei 1280 × 720. |
| **W3.5** | Deckel in `W0.1` auf 1,0 Bildschirm senken; jeder verbleibende Schritt hält ihn. | Der Wächter ist scharf, nicht dokumentierend. |

### W4 — Was ein Experiment ausmacht

| # | Paket | Abnahme |
| --- | --- | --- |
| **W4.1** | Lauf-Identität nach vorn: Name und Fragestellung mit Vorschlag, auf **jedem** Startpfad, vor dem Start. | Kein Lauf trägt mehr den Vorgabenamen, ohne dass jemand ihn gesehen hat. |
| **W4.2** | Delta-Ansicht im Prüfschritt: «Was weicht vom Standard ab», je Zeile mit Sprung und Einzelrücknahme. | Jede Abweichung ist gelistet und einzeln rücknehmbar. |
| **W4.3** | Laufzeitschätzung aus `run_metadata.json` vergangener Läufe, vor dem Start und als Restzeit während des Laufs. | Ein Spannenwert je Rechenmodus, kein Punktwert. |
| **W4.4** | Reproduzierbarkeit vor dem Start: Seed, Codestand, Config-Fingerabdruck — dieselben Größen, die P0.6 danach schreibt. | Was `run_metadata.json` hinterher festhält, steht vorher auf dem Schirm. |
| **W4.5** | `runner.cancel()` und ein Abbruch-Knopf im Ladebildschirm. | Ein laufender Lauf lässt sich beenden, ohne den Prozess zu töten. |

### W5 — Handwerk

| # | Paket | Abnahme |
| --- | --- | --- |
| **W5.1** | Render-Rückfälle schreiben nicht mehr in den Entwurf. Ein fehlender Wert wird als fehlend dargestellt, nicht als Literal erfunden. | AST-Wächter über `dashboard/web/`, analog `test_cost_pressure_source.py`: jeder Literal-Rückfall in einem Feld-Renderer wird gemeldet; Ausnahmen mit Begründung in einer `AUSNAHMEN`-Liste. |
| **W5.2** | `touched()` vergleicht gegen den normalisierten Entwurf. | Ohne Eingabe bleibt «Weiterverwenden» gesperrt — auch nach einem Reload. |
| **W5.3** | Barrierefreiheit: `aria-current="step"`, Live-Region für Schrittwechsel und Statusmeldungen, Fokus auf die Schrittüberschrift, `fieldset`/`legend` um jede Radiogruppe. | Ein Test, der diese vier Größen prüft. Ziel WCAG 2.1 AA für die Schrittfolge. |
| **W5.4** | Breite je Schritt statt einer Breite für alles; die Schrittliste reserviert auf dem Einstieg keinen Platz. | Kein Schritt unter 60 % oder über 100 % Spaltenausnutzung. |
| **W5.5** | Mobil: Schrittliste als kompakter Fortschrittsbalken, Fußleiste einzeilig. | Fußleiste unter 72 px bei 375 px Breite. |
| **W5.6** | Gewichtung der drei Wege des Einstiegs nach Häufigkeit. | Fachurteil, keine Messung — bewusst als solches gekennzeichnet. |

### 4.1 Reihenfolge und Abhängigkeiten

```
W0.1 ─┬─> W1.1 ─> W1.2 ─> W1.3 ─> W1.4
W0.2 ─┘                      │
                             v
                     W2.1 ─> W2.2 ─> W2.3
                             │
                             v
        W3.1 ─> W3.2 ─> W3.3 ─> W3.4 ─> W3.5
                             │
                             v
        W4.1 ─> W4.2 ─> W4.3 ─> W4.4 ─> W4.5
                             │
                             v
        W5.1 ─> W5.2 ─> W5.3 ─> W5.4 ─> W5.5 ─> W5.6
```

W5.1 und W5.2 dürfen vorgezogen werden — sie hängen an nichts und beheben einen aktiv falschen Zustand.

---

## Teil 5 — Workflow-Regelwerk: atomare Commits

**Ab sofort verbindlich für jede Änderung an diesem Projekt, für alle im Team und für jede Claude-Session.**

1. **Ein Commit = ein Befund oder ein Feature.** Kein Sammelcommit. Wer zwei Dinge behoben hat, macht zwei Commits — auch wenn sie dieselbe Datei berühren.
2. **Der Commit-Titel benennt Paket und sichtbares Ergebnis**, nicht die Datei: `fix(wizard): kein Haken für einen übersprungenen Schritt (W2.1)`, nicht `update wizard.py`.
3. **Jeder Commit ist für sich lauffähig und grün.** `pytest`, `ruff check .` und `black --check .` laufen vor jedem Commit, nicht vor jedem Push.
4. **Jeder Verhaltens-Commit bringt seinen Test mit** — im selben Commit, nicht im nächsten. Ein Test, der nachgereicht wird, prüft, was gebaut wurde, statt was zugesagt war.
5. **Doku im selben Commit** (Doku-Pflicht aus CLAUDE.md). Bleibt die Doku bewusst unverändert, steht der Grund in der Commit-Message.
6. **Refactoring und Verhaltensänderung nie im selben Commit.** W3.1 ist deshalb ein reiner Umzug; alles, was danach am Umgezogenen geändert wird, ist ein eigener Commit.
7. **Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung.** Wer «passt auf einen Bildschirm» zusagt, misst Bildschirme. Wer «drei Entscheidungen genügen» zusagt, misst, ob die drei wirken. Das ist die Lehre aus P1.6 *und* aus B1 dieses Audits — derselbe Fehler, zweimal, mit grünen Kriterien.
8. **Gepusht wird nicht automatisch.** Commits bleiben lokal, bis Haiko sie selbst pusht.

---

## Anhang — Befunde als Liste

| ID | Schwere | Befund | Paket |
| --- | --- | --- | --- |
| A1 | kritisch | Sweep-Pfad ignoriert Rechenmodus, Seed, Checkpoints; Preflight beschreibt ihn falsch | W1.1, W1.3 |
| A6 | kritisch | Fünf Bedienelemente in «optionalen» Schritten schreiben ohne Rückfrage in `configs/` | W3.2 |
| A2 | hoch | Weg 2 überschreibt still die Länge jedes Presets | W1.2, W1.4 |
| A3 | hoch | Übersprungene Schritte tragen ein Erledigt-Häkchen | W2.1 |
| A4 | hoch | Kein Validierungstor; Fehler halten nichts auf | W2.2 |
| B1 | hoch | Kein Schritt passt auf einen Bildschirm (1,13–4,44) | W0.1, W3.x |
| B2 | hoch | Schrittliste mischt Entscheidungen und Parameterflächen | W3.1 |
| B3 | hoch | Prüfschritt zeigt kein Delta gegenüber dem Standard | W4.2 |
| B4 | hoch | Keine Laufzeitschätzung, kein Abbruch | W4.3, W4.5 |
| C1 | hoch | Barrierefreiheit nicht adressiert (0 Live-Regionen, kein `aria-current`) | W5.3 |
| A5 | mittel | «Zurück» kehrt nicht dorthin zurück, wo man herkam | W2.3 |
| A7 | mittel | Render-Rückfall schreibt `seed=42`; `touched()` dauerhaft falsch-wahr | W5.1, W5.2 |
| B5 | mittel | Lauf-Name auf drei von vier Wegen unerreichbar | W4.1 |
| C2 | mittel | Eine Spaltenbreite für acht verschiedene Schritte | W5.4 |
| B6 | niedrig | Die drei Wege sind ungleich häufig und gleich groß | W5.6 |
| C3 | niedrig | Mobil tragfähig, aber ungeplant | W5.5 |
