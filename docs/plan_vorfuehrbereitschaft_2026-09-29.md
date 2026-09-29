# Vorführbereitschaft zum Pitch — Plan (2026-09-29)

**Ziel:** Am 08.10.2026 bei „Pitch, Please!“ lässt sich die Simulationsumgebung vor Ort zeigen — jede Funktion, die jemand anklicken kann, liefert ein richtiges, verständliches Ergebnis, ohne Fehler und in einer Zeit, die man vor Publikum aushält. Das schließt die Anbindung an das Sprachmodell, alle Texte, alle Berechnungen und die ganze Oberfläche ein.

**Stand dieses Plans:** 2026-09-29, erstellt aus einer Bestandsaufnahme am laufenden System (unten). Bis zum Pitch bleiben **neun Tage**. Der Plan ist deshalb nach **Muss / Soll / Kann** geordnet und sagt ausdrücklich, was **nicht** vor dem Pitch drankommt.

**Was „vollständig funktionsfähig“ hier heißt** — die Abnahme für jeden Bereich:

1. **Es läuft:** kein Fehler in Konsole oder Server-Log, kein leerer Bildschirm, kein Absturz.
2. **Es stimmt:** Jede Zahl kommt aus der Rechnung; jeder Text über einen Lauf widerspricht dessen Zahlen nicht.
3. **Es ist verständlich:** deutsche Sprache durchgängig, keine Entwicklerbegriffe, keine veralteten Verweise.
4. **Es ist schnell genug:** Ein Klick antwortet sichtbar in unter einer Sekunde; was länger dauert, zeigt eine Ladeanzeige und ist für die Vorführung vorgerechnet.
5. **Es läuft vor Ort:** auf dem Vorführrechner, ohne Internet, mit lokal laufendem Sprachmodell.

---

## Bestandsaufnahme am 2026-09-29 (gemessen, nicht geschätzt)

| Bereich | Ergebnis | Urteil |
| --- | --- | --- |
| Test-Suite | **3093 bestanden, 5 übersprungen**, 11:28 min; darin der Browser-Wächter mit 165 Zusagen | ✅ |
| `ruff`, `black`, `mypy` | alle grün | ✅ |
| Lauf mit Sprachmodell (Kommandozeile, 3 Ticks, `llama3.2`) | läuft, kein Ausfall, 25 Ereignisse; **rund 10 s je Tick** auf dem Entwicklungsrechner → 40 Ticks ≈ 7 min, 120 Ticks ≈ 21 min. Auf dem Vorführ-Laptop eher langsamer, dort neu zu messen (V1) | ✅ technisch, ⚠️ zu langsam für live |
| Szenario-Vergleich (4 Rahmen × 120 Ticks, Abschlusstexte mit Sprachmodell) | 113 s, Zahlen plausibel, Vergleichsansicht aussagekräftig | ✅ |
| **Texte der Agenten** | **englisch** («Implement a pilot program for SAF-powered flights …»), die Oberfläche ist deutsch; die Prompts in `src/prompts/` sind englisch, und nichts verlangt eine deutsche Ausgabe | ❌ |
| **Abschlusstext eines Laufs / Szenario-Vergleichs** | widerspricht der Rechnung: steigende CO₂-Preise bei konstant 50 €, «Elektroflotte», erfundenes Datum «2023-01-01», «Die Temperaturen stiegen» | ❌ |
| **Abfrage (State Explorer)** | «keine Veränderung im Ticketpreis», wo er von rund 140 auf über 400 € steigt; nichts markiert. Dazu der bekannte Befund N10: ganzzahlige Prozentangaben 1–250 % gelten immer als belegt | ❌ |
| **Kopfzeile des Abschlusstexts** | «? Ticks» im Einzellauf, **«50 Ticks» bei 120 gerechneten** im Szenario-Vergleich (liest die Metadaten des vorigen Laufs); alte `llm_incidents.json` bleibt neben `degraded: false` liegen | ❌ |
| Ansicht «Animation» | 8,5 s und 9,1 MiB je Aufruf (P7.6-U6.2), mit Ladeanzeige | ⚠️ |
| Vergleichsansicht | Satzfehler «unter aus einem»; zieht jeden Ordner unter `outputs/sweeps/` mit, auch Testläufe | ⚠️ |
| Handbuch | sechs Befunde der Gegenprüfung vom 2026-09-21 weiter offen: falsche Schrittnummern (4 Kapitel), «Demo ohne Ollama» statt der sichtbaren Beschriftung, «sechs» statt «vier» Auswertungen, **veraltete Backtest-Zahlen in `grenzen.md`** (1,8 / 38 / 86), toter Verweis «Segmente & Alter» (2 Stellen), zerrissene Tabelle in `ref-config.md` | ⚠️ |
| Sprunglink | nicht der erste Tab-Stopp beim ersten Laden (Befund 3 vom 2026-09-21) | ⚠️ |
| Landingpage auf `/` | Impressum, Datenschutz, AGB und Demo-Anfrage mit sichtbarem Platzhalter-Warnblock (P1.4-Rest) | ⚠️ |
| Lauf-Browser | **980 Ordner** unter `outputs/`, 199 mit Metadaten, 327 davon Mess- und Prüfläufe (`audit_…`, `messung_…`, `p2…`, `strategie_…`) | ⚠️ für die Vorführung |
| Offen im Projektplan | P2.14, P7.0, P7.6–P7.11, P1.4-Rest | siehe unten |

**Die Zusammenfassung in einem Satz:** Rechnung, Oberfläche und Tests tragen; **was nicht trägt, ist alles, was das Sprachmodell schreibt** — es ist englisch, wo es deutsch sein soll, und es widerspricht der Rechnung. Genau das ist aber das Versprechen «KI fasst zusammen», und es ist das, was ein Zuschauer vor Ort als Erstes ausprobiert.

---

## Arbeitspakete

### Muss — ohne diese keine Vorführung

#### V1 — Mit `llama3.2` auf dem Laptop auskommen, mit Messung statt Gefühl

**Befund:** Vorgeführt wird auf einem Laptop, ein größeres Modell läuft dort nicht — es bleibt bei `llama3.2` (3 Mrd. Parameter). Genau dieses Modell widerspricht in allen vier Abschlusstexten und in der Abfrage der Rechnung. Die Güte der Texte muss deshalb aus dem kommen, was das Modell bekommt (V3: Faktenblatt statt Deutung), nicht aus einem größeren Modell.
**Was zu tun ist:** Einen **festen Prüfsatz** bauen — die vier Abschlusstexte eines Szenario-Vergleichs, fünf Abfragen mit bekannter Antwort (Preisverlauf, Buchungsrate, Faktorwechsel, CO₂-Abgabe, Vergleich zweier Ticks), die Agententexte eines Laufs über 6 Ticks. Gemessen je Durchgang: Widersprüche gegen die Laufdaten (gezählt), Deutsch ja/nein, Sekunden je Tick. Einmal jetzt als Ausgangswert, danach nach V2 und V3 — und **einmal auf dem Laptop**, weil dort die Sekunden je Tick über den Vorführbestand (V5) und das Drehbuch (V8) entscheiden.
**Fertig wenn:** Der Prüfsatz liegt als wiederholbarer Test vor (markiert, läuft nur mit Ollama), der Ausgangswert ist festgehalten, und die Sekunden je Tick auf dem Laptop sind gemessen.
**Aufwand:** ½ Tag. **Zuerst**, weil V2 und V3 daran gemessen werden.

#### V2 — Alles, was das Modell schreibt, ist deutsch

**Befund:** Die Prompts der drei Agenten sind englisch und verlangen keine Ausgabesprache; die Texte erscheinen englisch in Protokoll, Ereignisstreifen und Bericht. Der Abschlusstext ist deutsch, die Agenten nicht.
**Fundstelle:** die LLM-Aufrufer im Lauf und daneben, gezählt am 2026-09-29: `src/agents/agent_node.py` mit `src/prompts/consumer.md`, `provider.md`, `regulator.md`; `src/cib/scenario_agent_node.py`; `src/reporting/run_scenario_generator/pipeline.py` und `prompt.py` mit `src/prompts/run_scenario.md`; `src/reporting/state_explorer.py`.
**Was zu tun ist:** Jeden LLM-Aufrufer im Lauf auf eine deutsche Ausgabe festlegen (Anweisung im Prompt, die maschinenlesbaren Schlüssel bleiben wie sie sind). Ein Wächter, der **sucht statt aufzuzählen**: jeder Prompt unter `src/prompts/` und jeder Aufrufer, der `OllamaClient` benutzt, verlangt Deutsch.
**Fertig wenn:** Ein Lauf über 6 Ticks mit `llama3.2` erzeugt keinen englischen Satz in `event_log.json`, `protocol.md`, `run_scenario.md`; Handbuch und `docs/agent_profiles.md` sagen es.
**Aufwand:** ½ Tag.

#### V3 — Ein Text über einen Lauf widerspricht dessen Zahlen nicht

**Befund:** Die Zahlenprüfung aus P2.5 gilt nur für die Abfrage, prüft keine Richtungsaussagen («steigt», «sinkt») und lässt ganzzahlige Prozentangaben ungeprüft durch (N10). Abschlusstext und Szenariotext sind gar nicht geprüft.
**Was zu tun ist:** (a) N10 beheben (Prozentangaben gegen die passende Größe, nicht gegen jede Zahl). (b) Den Abschlusstext mit einem **Faktenblatt** erzeugen, das die Richtung jeder Kerngröße über den Lauf bereits ausrechnet (Preis, Buchungsrate, CO₂-Abgabe, SAF-Quote, Faktorwechsel) — das Modell formuliert, statt zu deuten. (c) Eine Prüfung der Richtungsaussagen gegen dieses Faktenblatt; ein Widerspruch wird markiert wie eine unbelegte Zahl. (d) Der Vorbehalt der Abfrage erscheint immer, nicht nur bei einer unbelegten Zahl.
**Fertig wenn:** Der Prüfsatz aus V1 ergibt **null unmarkierte Widersprüche**; die vier Fälle vom 2026-09-29 (CO₂ steigt bei 50 €, «Elektroflotte», Datum, «keine Veränderung im Ticketpreis») sind als Regressionsfälle festgehalten.
**Aufwand:** 1½–2 Tage. **Das größte Paket und das wichtigste**: Invariante 1 verspricht es.

#### V4 — Der Abschlusstext liest die Daten seines eigenen Laufs

**Befund:** `save_run_outputs` und `run_single_sweep` erzeugen den Szenariotext, **bevor** `run_metadata.json` geschrieben ist: «? Ticks» im Einzellauf, die Tickzahl des vorigen Laufs im Szenario-Vergleich. `save_llm_incidents` schreibt ohne Vorfall nichts, eine alte Datei bleibt liegen.
**Fundstelle:** `src/run_simulation.py::save_run_outputs`, `src/orchestration/scenario_sweeps.py::run_single_sweep`, `src/reporting/output_writer/llm_incidents.py`.
**Was zu tun ist:** Die Metadaten vor dem Text bereitstellen (aus dem Zustand übergeben statt von der Platte lesen), und ein Lauf in einen bestehenden Ordner räumt die Artefakte des vorigen Laufs ab oder überschreibt jede. Ein Test, der die **echte** Schreibreihenfolge abbildet, nicht eine vorab angelegte Datei.
**Fertig wenn:** Einzellauf und Szenario-Vergleich nennen die richtige Tickzahl, und ein zweiter Vergleich in denselben Ordnern hinterlässt keine Datei des ersten. Die zwei Zeilen in `audit_findings.md` sind entfernt.
**Aufwand:** ½ Tag.

#### V5 — Eine aufgeräumte Vorführumgebung mit vorgerechneten Läufen

**Befund:** Ein Lauf mit Sprachmodell dauert Minuten; der Lauf-Browser listet 980 Ordner, darunter hunderte Mess- und Prüfläufe.
**Was zu tun ist:** Einen **Vorführbestand** festlegen und vorrechnen, mit `llama3.2` und nach V2 bis V4: (1) «Business as Usual», 40 Ticks, mit Sprachmodell; (2) derselbe Rahmen mit angehobener CO₂-Abgabe (der Anwendungsfall aus dem Pitch); (3) Szenario-Vergleich der vier Rahmen über 120 Ticks. Der übrige Inhalt von `outputs/` wandert in ein Archiv außerhalb des Ordners (verschieben, nicht löschen). Ein kurzes Skript oder eine Anleitung, die den Bestand reproduzierbar erzeugt.
**Fertig wenn:** Der Lauf-Browser zeigt nur den Vorführbestand; jeder Lauf darin besteht die Abnahme oben.
**Aufwand:** ½ Tag Arbeit, dazu Rechenzeit.

#### V6 — Abnahme-Durchgang: jede Funktion einmal angefasst, mit Protokoll

**Befund:** Die Test-Suite ist grün, aber kein Test klickt die Vorführung von vorne bis hinten durch; der Weg «Einrichten → Lauf mit Sprachmodell starten → Fortschritt → Abbrechen → Ergebnisse» ist im Dashboard mit echtem Modell nicht geprüft.
**Was zu tun ist:** Ein Protokoll über **jeden** Bereich und jede Ansicht: Einstieg und alle acht Schritte, beide Startwege (Einzellauf, Vergleich), alle drei Rechenmodi, Abbrechen eines Laufs, Leitstand mit Zeitleiste und Abspielen, alle sieben Ergebnis-Ansichten mit PNG-Export und «Dateien des Laufs», Abfrage mit fünf Fragen, Lauf-Browser mit Suche und Filter, Modell-Bereich lesen und einmal speichern **und zurücksetzen**, Handbuch mit Suche, Szenario sichern, helles und dunkles Design, 1920 × 1080 (Beamer) und 1280 × 800. Jede Abweichung wird ein Befund mit Paket.
**Fertig wenn:** Das Protokoll liegt unter `docs/` und hat keinen offenen Befund der Stufe «bricht die Vorführung».
**Aufwand:** 1 Tag, **zweimal**: einmal nach V1–V4, einmal als Generalprobe am Vortag.

#### V7 — Der Laptop und die Offline-Probe

**Befund:** Die Datenhoheits-Zusage heißt «kein Aufruf verlässt den Server» — für die Vorführung heißt sie: Es muss **ohne Internet** gehen. Vorgeführt wird auf einem Laptop; ungeprüft ist, ob Ollama mit `llama3.2` dort läuft und wie schnell. `pitch.html` lädt seine Schriften von Google (ohne Netz greifen Systemschriften).
**Was zu tun ist:** Auf dem Laptop `ollama pull llama3.2`, `.venv`, Dashboard-Start, der Vorführbestand aus V5; dann **mit getrenntem Netz** V6 in Kurzform. Beamer-Auflösung prüfen. Die Schriften von `pitch.html` einbetten oder die Datei ohne Netz abnehmen. Ein Plan B: Bildschirmaufnahme des Vorführpfads als Video, falls vor Ort etwas nicht startet.
**Fertig wenn:** Ein Durchgang ohne Netz auf dem Laptop ist protokolliert; die Aufnahme liegt bereit.
**Aufwand:** ½ Tag.

#### V8 — Das Drehbuch der Vorführung

**Was zu tun ist:** Festlegen, **wann** vorgeführt wird (im Pitch selbst ist keine Zeit — also am Stand oder in der Fragerunde) und **was**: der Anwendungsfall aus dem Pitch in drei Minuten, mit den Klicks in fester Reihenfolge; was live gerechnet wird (ein Lauf «Nur Zahlen» über 40 Ticks dauert Sekunden) und was vorgerechnet gezeigt wird (alles mit Sprachmodell); was man sagt, wenn eine Frage auf eine bekannte Grenze zielt (Nachfrageseite, Kalibrierung).
**Fertig wenn:** Ein Drehbuch von einer Seite liegt bei der Übersicht des Pitches und ist zweimal geprobt.
**Aufwand:** ¼ Tag plus Proben.

### Soll — sichtbar, wenn jemand selbst klickt

#### V9 — Das Handbuch sagt, was die Oberfläche tut

**Befund:** sechs Befunde der Gegenprüfung vom 2026-09-21 (4)–(9), am 2026-09-29 nachgeprüft offen.
**Was zu tun ist:** Schrittnummern in `lauf-starten.md`, `fragestellungen.md`, `vergleiche.md`, `presets.md` über die Namen der Schritte statt über Zahlen; der Demo-Schalter mit einem Namen in Code und Handbuch; «vier» Auswertungen in `ergebnisse-lesen.md`; die Backtest-Zahlen in `grenzen.md` aus `backtest_vorlauf.md`; «Segmente & Alter» → «Wer noch fliegt»; die Tabelle in `ref-config.md` zusammenfügen.
**Fertig wenn:** Alle sechs Stellen stimmen, und `grenzen.md` nennt die Zahlen mit Datum. Die Zeile der Gegenprüfung in `audit_findings.md` ist entsprechend gekürzt.
**Aufwand:** ½ Tag.

#### V10 — Der Vergleich zeigt nur Rahmen, und sein Satz stimmt

**Befund:** «unter aus einem» unter der Vergleichsansicht; die Ansicht nimmt jeden Ordner unter `outputs/sweeps/` mit (P7.6-U6.4).
**Was zu tun ist:** Den Satz korrigieren; die Ansicht vergleicht nur Läufe unter einem heutigen Rahmenszenario (dieselbe Ableitung wie der Prüflauf-Filter im Lauf-Browser).
**Fertig wenn:** Ein Testlauf in `outputs/sweeps/` taucht im Vergleich nicht auf; ein Wächter hält es.
**Aufwand:** ¼ Tag.

#### V11 — «Animation» ohne acht Sekunden Warten

**Befund:** 8,5 s und 9,1 MiB je Aufruf, weil die Ansicht Personen statt Ergebnisse überträgt (P7.6-U6.2).
**Was zu tun ist:** Die Stichprobe aus U6.2 (etwa 300 Personen statt aller) — der kleinste Eingriff, der die Zusage von 2 MB erfüllt. Die zweite Zeitachse (D5) bleibt P7.6.
**Fertig wenn:** Nutzlast ≤ 2 MB, Aufruf < 2 s, die Ausnahme im Wechselwächter entfällt.
**Aufwand:** ½ Tag. **Falls die Zeit nicht reicht:** in der Vorführung nicht öffnen.

### Kann — nur, wenn Zeit bleibt

- **V12 — Sprunglink als erster Tab-Stopp** (Befund 3 vom 2026-09-21): der Fokus-folgt-der-Frage-Mechanismus greift beim ersten Laden nicht. ¼ Tag.
- **V13 — Rechtstexte der Landingpage** (P1.4-Rest): braucht Inhalte vom Team; bis dahin beginnt jede Vorführung auf `/app/` statt auf `/`, damit kein Warnblock zu sehen ist.
- **V14 — Klick-Latenz** (P7.11): gemessen 541–747 ms statt 500. Für eine Vorführung spürbar, aber nicht störend; die Ursache sind sieben Rundläufe je Klick, ein Umbau vor dem Pitch wäre riskant.

### Bewusst nicht vor dem Pitch

Diese Pakete bleiben offen, und das ist eine Entscheidung, keine Lücke: **P7.0** (Messfundament, Rest), **P7.6** außer U6.2 und U6.4, **P7.7** (Modell-Bereich: funktioniert, ist aber eine lange Liste — in der Vorführung nur zeigen, nicht bearbeiten), **P7.8** (Handbuch-Lesefläche), **P7.9** (schmale Breiten und Barrierefreiheit — der Beamer ist breit), **P7.10** (Gegenprobe der Phase 7), **P2.14** (eine Modellfrage, die erst gemessen werden muss). Jedes davon nach dem Pitch in der Reihenfolge des Projektplans.

---

## Zeitplan

| Tag | Was |
| --- | --- |
| Di 30.09. | V1 (Prüfsatz, Ausgangswert) · V4 |
| Mi 01.10. | V2 · V3 (a, d) |
| Do 02.10. | V3 (b, c) · V10 |
| Fr 03.10. | V5 (Vorführbestand rechnen) · V9 |
| Sa 04.10. | V6, erster Abnahme-Durchgang · daraus entstehende Befunde |
| So 05.10. | Befunde aus V6 · V11 |
| Mo 06.10. | V7 (Laptop, Offline-Probe, Aufnahme) · V8 (Drehbuch) |
| Di 07.10. | **Einfrieren am Mittag** — danach nur noch Fehler, die die Vorführung brechen · V6 als Generalprobe |
| Mi 08.10. | Pitch |

**Regel für die letzten 24 Stunden:** Nach dem Einfrieren wird nichts mehr gebaut. Ein Befund aus der Generalprobe wird entweder in weniger als einer Stunde mit Test behoben oder im Drehbuch umgangen.

## Entscheidungen, die Haiko treffen muss

**Entschieden am 2026-09-29:** Vorgeführt wird auf einem Laptop, ein größeres Modell kommt nicht in Frage — es bleibt bei `llama3.2`.


1. **Wann vorgeführt wird** — am Stand, in der Fragerunde, oder nur auf Nachfrage (V8).
2. **Ob «Animation» repariert oder in der Vorführung ausgelassen wird** (V11).

## Risiken

- **V3 ist Forschung, nicht nur Handwerk.** Richtungsaussagen gegen Daten zu prüfen ist machbar; freie Behauptungen wie «Elektroflotte» zu erkennen nur über das Faktenblatt (was dort nicht steht, darf der Text nicht behaupten). Fällt V3 kürzer aus, bleibt der Satz aus dem Pitch: Wir zeigen keine KI-Texte, die Rechnung trägt.
- **Der Laptop kann deutlich langsamer rechnen** als der Entwicklungsrechner. Dann trägt der vorgerechnete Bestand (V5) alles mit Sprachmodell, und live wird nur «Nur Zahlen» gerechnet — das Drehbuch (V8) plant das von vornherein so.
- **Neun Tage sind knapp.** Der Plan hält das Muss bei rund fünf Arbeitstagen, damit Puffer für die Befunde aus V6 bleibt.
