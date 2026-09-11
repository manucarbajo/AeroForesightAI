# Projektplan

**Stand:** 2026-09-11 — **P5.1 ist erledigt**: Toter Code und irreführende Namen sind weg — darunter `--sweep`, das stumm den Standardlauf rechnete —, und die Nachmessung des Kriteriums fand elf Namen, die in der Liste fehlten; zwei Wächter halten jetzt, was die Liste nicht halten konnte. **Neu offen aus der Nachmessung: [P2.14](#p214--einmalige-verschiebungen-laufen-an-den-anschlag--offen-neu-2026-09-11-aus-p51)** — mehr als ein Viertel der Bevölkerung hängt am oberen Anschlag der Preisempfindlichkeit, weil sich einmalige Verschiebungen summieren. Davor, am selben Tag: **P5.3 ist erledigt**: `src/legacy/` ist entfernt, samt `CIBMatrixHistory`, `apply_delta_constraint` und dem Feld `cib_history`, die nur der LLM-Extraktor benutzte; ältere Checkpoints laden weiter. Davor, am selben Tag: **Phase 4 ist abgeschlossen.** Zuletzt **P4.5**: Die vier Rahmenszenarien laufen 120 Ticks, also zehn Jahre, jede Marke im selben Verhältnis gestreckt — alle Meilensteine halten, die Endlagen der Faktoren bleiben gleich, und der Transformationskonflikt zeigt über zehn Jahre praktisch den Stillstand des Marktes, gesagt statt nachjustiert. Davor, am selben Tag: **P4.4 ist erledigt**: `mypy` prüft die Grenzen in der CI, über eine Dateiliste in `pyproject.toml`, die wächst. Der erste Lauf fand 23 Meldungen; zwei betrafen Verhalten und sind behoben — `coerce_payload` stürzte bei `max_ticks: 0` ab, und der Platzhalter für das Sprachmodell im Sweep war kleiner als vermutet: gerufen hätte er schon vorher einen sichtbaren Ausfall erzeugt, nur mit der falschen Ursache. Davor, am selben Tag: **P4.6 ist erledigt**: `src` ist über die Installation importierbar, aus jedem Arbeitsverzeichnis und nur als Paket; die CI installiert das Projekt dafür jetzt selbst. Davor, am selben Tag: **P4.3 ist erledigt**: Ein Register hält die Zahlen in CLAUDE.md, die den heutigen Stand beschreiben, gegen ihre Messung — und fand beim Anlegen vier veraltete Aussagen, jede beim Schreiben richtig und von einem späteren Commit nicht mitgezogen. Davor, am selben Tag: **P4.1 und P4.2 sind erledigt** ([#14](https://github.com/manucarbajo/AeroForesightAI/pull/14)): Die CI läuft ohne Ausnahmeliste, das Debug-Skript, die `sys.path`-Eingriffe und der `unittest`-Stil sind weg, und jede dieser Regeln hält ein Wächter, der das Merkmal sucht statt die Dateien aufzuzählen (`tests/test_testfundament.py`) — keine der Befundlisten stimmte beim Anfassen vollständig. P4.1 dazu: 39 Temp-Verzeichnisse auf `tmp_path` statt der gezählten 32, fünf handgemachte Umbiegungen auf `monkeypatch` — zwei davon stellten nicht zurück —, und `MockLLM` ist ein Name für ein Ding. **Neu offen aus der Arbeit: [P4.6](#p46--die-installation-macht-src-nicht-importierbar--erledigt-2026-09-11-neu-2026-09-11-aus-p42)** — die Installation macht `src` nicht importierbar. Davor: 2026-09-07 — **Phase 3 ist vollständig abgeschlossen und gemergt** ([#12](https://github.com/manucarbajo/AeroForesightAI/pull/12)); der Browser-Wächter ist dabei erstmals auf **Linux** gelaufen und hat in vier Anläufen drei Dinge gefunden, die lokal unsichtbar waren — sechs Zusagen hingen an vorhandenen Läufen in `outputs/`, der Breitenwächter wartete nicht auf die Webschrift, und `af-mass: 53ch` hat unter Linux **nie** gehalten (`ch` ist der Ziffernvorschub, und Chromium quantisiert den dort auf ganze Pixel). **Danach eröffnet und am selben Tag geschlossen: [P2.13](#p213--f6-kippte-in-jedem-tick--erledigt-2026-09-07-neu-2026-09-07)** — F6 kippte in jedem Tick, und der Endzustand eines Laufs hing an der Parität seiner Tickzahl. Der Anlass war eine Frage, kein Wächter. Zu Phase 3: Die zuletzt zurückgestellte Tickdauer ist entschieden und umgesetzt — **ein Tick ist ein Monat** ([P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31)); geändert wurde die **Einheit** und nicht die Aussage über die Welt, und am Backtest fünf von acht Kennzahlen verschlechtern sich, eine verbessert sich geringfügig, zwei bleiben gleich — **keine einzige spricht für die Änderung** — genau der Beleg, dass nicht auf ihn hin eingestellt wurde. Dabei kam ein **vierter** Zeitskalen-Widerspruch heraus, den der alte Wächter nicht finden konnte: `demand_growth_rate` trug «je Tick» in der Einheit und «jährlich» in der Beschreibung, aufgezinst 42,58 % im Jahr. Neu offen ist allein die Frage, die dabei sichtbar wurde und bewusst nicht mitentschieden ist: der Zeithorizont der Rahmenszenarien ([P4.5](#p45--was-ein-rahmenszenario-über-die-zeit-behauptet--erledigt-2026-09-11-neu-2026-09-07)). Davor: 2026-09-05 — **Phase 3 abgeschlossen und am selben Tag vollständig geprüft** (elf Pakete erledigt; drei der elf sind erst aus der Arbeit entstanden — [Bilanz](#phase-3--engine-härtung--vollständig-abgeschlossen-am-2026-09-07)). Das [Audit](#audit-der-phase-3-2026-09-05--fünf-pakete-der-schwere-befund-ist-vorbestehend) bestätigt elf von zwölf Paketen **nachgemessen** und alle fünfzehn tragenden Wächter über eine Mutationsprobe; **kein Befund berührt die Zahlen eines Laufs**. Vier Ränder hielten nicht (P3.13 bis P3.16); **alle vier sind am selben Tag behoben** — der erfundene `llama3.2` im Launcher, der Ausweichpfad, der `sys.stderr.buffer` voraussetzte, die Signatur, die ihrem Rumpf widersprach (deren **Klasse** offen bleibt als P4.4: kein Typprüfer im Projekt), und das 500-ms-Kriterium, das jetzt einen Wächter auf seiner Höhe hat. **Auch die fünf kleinen Befunde sind erledigt**, und zwei davon waren beim Anfassen größer als gemeldet: Bei C1 reproduzierte **keine** der drei Zahlen zum Modell-Bereich, bei C2 stand die Kopfzeile an **drei** Stellen wörtlich. **Der einzige schwere Befund war vorbestehend und ist am 2026-09-06 behoben**: Der Browser-Wächter war 112 zu 6 rot, weil C5 des Phase-2-Audits am 2026-09-03 behoben und von Commits desselben Tages ungültig gemacht wurde; er ist jetzt **118 zu 0** grün und läuft nächtlich sowie bei jedem Pull Request auf `dashboard/web/**` (P3.17). Die Einschränkung gehört dazu — **das Audit ist nicht unabhängig**, dieselbe Sitzung hat gebaut und geprüft. Davor: 2026-08-28 — **Phase 0 ist abgeschlossen**, **P1.1 ist erledigt**, und darauf ist **P1.5** gefolgt: Das Dashboard ist jetzt ein **Leitstand** — ein Bildschirm mit fünf Zonen statt eines Stapels Seiten, mit umschaltbarem hellen und dunklen Design und einer Tick-Zeitleiste, die Szene, Kennzahlen und Verläufe gemeinsam führt ([Einzelheiten](#p15--leitstand-oberfläche--erledigt-2026-08-28)). Auch dort lag der eigentliche Fund unter der Oberfläche: Die Stile für Dashs eigene Komponenten griffen seit dem Sprung auf Dash 4 an **keiner einzigen Stelle** mehr — im hellen Modus unsichtbar, im dunklen ein violetter Regler mit schwarzer Beschriftung auf schwarzem Grund. Direkt darauf folgte **P1.6**, weil die Vermessung des Ergebnisses einen Rückschritt zeigte: Die linke Spalte war mit der hineingepressten Konfiguration **10,7 Bildschirme** hoch, und der Start-Knopf lag 6,1 Bildschirme tief — bei erfüllten Abnahmekriterien beider Vorgängerpakete. Einrichten und Beobachten sind jetzt getrennt, die Spalte ist ein Bedienfeld, und die Kriterien von P1.1 und P1.5 sind um eine Größe ergänzt, die **Erreichbarkeit** misst statt Anzahl ([Einzelheiten](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28)). Zu P1.1: «Simulation starten» führt jetzt in drei Entscheidungen zum Lauf ([Einzelheiten](#p11--simulation-starten-neu-bauen--erledigt-2026-08-28)). Dabei kam ein Fund heraus, der nicht in der Oberfläche lag: Ein gewähltes Szenario-Preset wurde im Dashboard **still von den Datei-Defaults überschrieben** — bei allen acht ausgelieferten Presets, ein Lauf «Business as Usual» rechnete mit steigender CO₂-Abgabe. Behoben, mit einem Wächter über jede Datei unter `configs/sweeps/`. Phase 0 im Übrigen unverändert und **sechsfach** gegengeprüft: Haikos Gegenprobe deckte 36 von 36 Zusagen mechanisch ab ([Einzelheiten](#gegenprobe-zu-p04p06-2026-08-27)), Manus zweite Runde am laufenden System fand drei Zusagen von P0.6, die im Artefakt nicht hielten — alle behoben ([Einzelheiten](#zweite-gegenprobe-zu-p06-manu-2026-08-27)) —, die dritte Runde hat seine Befunde nachgestellt und drei Lücken in den neuen Tests geschlossen ([Einzelheiten](#dritte-runde-manus-gegenprobe-nachgeprüft-haiko-2026-08-27)), die vierte hat die Phase als Ganzes geprüft (**im Code hält alles, fünf Lücken lagen in der Doku**, [Einzelheiten](#vierte-runde-phase-0-als-ganzes-geprüft-2026-08-27)), und die fünfte hat P0.7 gegengeprüft: Der Fix hält, ein Geschwister seines Musters lag noch in der Bevölkerungshälfte und ist mit behoben ([Einzelheiten](#fünfte-runde-p07-gegengeprüft-manu-2026-08-27)), und die sechste hat diese Verallgemeinerung gegengeprüft: Sie hält, zwei weitere Geschwister lagen in derselben Datei und sind mit behoben ([Einzelheiten](#sechste-runde-die-verallgemeinerung-gegengeprüft-haiko-2026-08-28)). P0.7 kam aus der Umsetzung von P0.4 dazu und ist ebenfalls erledigt; drei seiner eigenen Befundaussagen mussten dabei korrigiert werden. Offen aus P0.2 war die fachliche Abnahme der 48 neu bewerteten Matrixzellen — die einzige offene Position der Phase; sie ist seit dem **2026-08-29 zurückgestellt mit Grund** und nicht mehr eingeplant, siehe die Entscheidung unten. Die drei Phase-1-Pakete sind **gegengeprüft** (Manu, 2026-08-28): Die tragenden Zusagen halten, drei Befunde lagen in der Darstellung — ein Schubladen-Knopf, dessen Versteck-Regel die Kaskade verlor und deshalb nie wirkte, sein Haltepunkt, der der falschen Zone gehörte, und ein Laufzustand, der nur die eigene Sitzung kannte; alle drei behoben ([Einzelheiten](#gegenprobe-zu-p11p15p16-manu-2026-08-28)). Daraus ist **P1.7** entstanden, und es ist erledigt: Der Ablauf **ist** jetzt die Oberfläche — Einrichten zuerst, der Lauf als eigener Bildschirm, das Einrichten als Schrittfolge hinter einem Einstieg mit drei Wegen statt einer Bildlaufstrecke ([Einzelheiten](#p17--der-ablauf-wird-die-oberfläche--erledigt-2026-08-28)). **Alle vier Stufen sind fertig** — zuletzt am 2026-08-28 der Einstieg mit den drei Wegen (Stufe C) und der mechanische Überlauf-Wächter (Stufe D). Beim Wächter kam die Entscheidung dazu, die der Plan offengelassen hatte: Playwright als **optionales** Extra, damit die CI ohne Browser grün bleibt und wer die Oberfläche anfasst ihn lokal scharf hat. Und er hat sich beim ersten Durchlauf selbst korrigiert — zwei weitere Phantome kamen zu den drei aus P1.8 dazu, darunter `scrollWidth` selbst: Ein ausgeschwebtes Kind zählt in den `scrollWidth` seines Vorfahren, und Dashs eigenes Dropdown ließ die Zeitleiste 145 px Überlauf melden, obwohl nichts zu sehen war. P1.7 ist gegengeprüft (Haiko, 2026-08-28): drei Befunde behoben — der Start aus der Schrittfolge wechselte den Bildschirm nicht, ein Widerspruch von 1,7 s zwischen Kopfzeile und Mitte, und ein Text, der auf einen aufgelösten Abschnitt zeigte; ein vierter Befund hat sich unter genauerer Messung aufgelöst und ist samt zurückgenommener Korrektur protokolliert ([Einzelheiten](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt)). Am **2026-08-28** ist der Einrichten-Assistent unabhängig auditiert worden — bewusst ohne die Abnahmekriterien dieses Plans als Maßstab, und genau dadurch hat das Audit gefunden, was die Kriterien durchgelassen haben: Auf dem Sweep-Pfad erreicht **genau ein** Feld des Entwurfs die Simulation, während der Preflight einen Lauf beschreibt, der so nicht stattfindet; fünf Bedienelemente in als *optional* gekennzeichneten Schritten schreiben ohne Rückfrage in `configs/properties.json`; und **kein einziger der acht Schritte passt auf einen Bildschirm** (1,13 bis 4,44), obwohl genau das die Zusage von P1.7 war. Daraus ist [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28) entstanden: **P1.1 und P1.7 sind wieder offen**, P1.5 bekommt ein Kriterium dazu, P1.8 schärft sein Verfahren nach, P1.3 und P3.6 werden vorgezogen ([Einzelheiten](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28), Vollfassung in [`wizard_audit_2026-08-28.md`](wizard_audit_2026-08-28.md)). Dieselbe Lehre wie bei P1.6, diesmal als Regel festgehalten: **Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung** — nachzulesen im [Commit-Regelwerk](#regelwerk-atomare-commits-ab-2026-08-28-verbindlich), das ab sofort für jede Änderung gilt. Am **2026-08-29** ist die Szenarienschicht entschieden worden — **Rahmen statt Richter**, und der Anlass war eine kleinere Frage: ob die 48 F7-Zellen jetzt fachlich abzunehmen sind. Beim Nachmessen der übrigen 120 kam heraus, dass der Konsistenz-Score **Polarität misst, nicht Plausibilität** (Korrelation +0,56 mit der Zahl gleichpolig gesetzter Faktoren, über alle vier Gruppen monoton), dass das **echte** Impact-Balance-Kriterium **genau zwei** der 128 Zustände trägt statt der drei, die das Produkt verspricht, und dass **vier unbegründete Zellen** die Rückkopplung verneinen, aus der gemischte Szenarien überhaupt erst entstehen: Nachfrage- und Wirtschaftswachstum hemmen dort strenge Regulierung, Flugscham und Schienenausbau. Damit bewertet das Modell die reale europäische Lage — strenge Regulierung *bei* starker Nachfrage — als unplausibel. Entschieden ist **Variante C**: Ein Szenario wird ein benanntes Bündel exogener Verläufe, F1–F7 werden aus dem Lauf *abgeleitet* statt ihn zu bewerten; die Sweeps sind bereits solche Bündel und werden vom Nebenweg zum Hauptweg. Phase 2 ist danach neu geschnitten — [P2.0](#p20--die-rolle-umdrehen-rahmen-statt-urteil--erledigt-2026-08-30) (Rolle umdrehen), P2.1, [P2.6](#p26--ensemble-läufe-je-rahmenszenario--erledigt-2026-08-31) (Ensemble), [P2.7](#p27--backtest-gegen-20152024--erledigt-2026-08-30) (Backtest), und **erst danach** [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31), weil sich eine Entscheidung über ein Werkzeug leichter trifft, wenn das Modell geeicht ist ([Einzelheiten](#leitentscheidung-die-szenarienschicht-2026-08-29), Vollfassung in [`entscheidung_szenarienschicht_2026-08-29.md`](entscheidung_szenarienschicht_2026-08-29.md)). Am **2026-08-30 ist Phase 1 abgeschlossen** — mit genau einer benannten Restposition. P1.9 ist vollständig (W3.5 entschieden: der Höhen-Deckel hält den Ist-Stand statt Inhalt wegzulassen), womit **P1.1 und P1.7 wieder geschlossen** sind. Dazu erledigt: **P1.2** (vier Aussagen statt sechs Datenquellen; Figuren entstehen ganz oder gar nicht; ein Farb- und Achsensystem für PNG und Bildschirm), **P1.3** im zugesagten Umfang (die Grenze zwischen Gerechnetem und Erzähltem steht im Schema — wie die Szenarien *entstehen*, bleibt P2.0), **P1.5** (der Bereichswechsel ist ansagbar und führt den Fokus) und **P1.4** bis auf die Rechtstexte: Kein Seitenaufruf verlässt mehr den eigenen Server, und die Demo-Anfrage kommt an. **Offen bleibt allein, dass Impressum, Datenschutzerklärung und AGB Inhalte brauchen** — die Gliederung steht, jede Pflichtangabe ist als benannte Lücke markiert, und `docs/landingpage.md` führt die Liste zum Abarbeiten. Auffällig an diesem Durchgang: **Fünf der neuen Wächter haben beim ersten scharfen Durchlauf zugeschlagen**, drei davon auf Fehler, die im selben Commit entstanden waren — darunter ein Symbol-Teilsatz, dem vier Namen fehlten, weil sie in einem Modul-Dict statt im Aufruf stehen; die Schrittliste brach daraufhin um 308 px aus. Daraus kam die Regel, die über das Paket hinausgeht: **Ein Parser findet, was jemand hingeschrieben hat; eine Messung findet, was wirklich dasteht.** · **Leitentscheidung:** Erst Funktionalität und UI, dann B2B-Readiness. Ein Produkt, das im Demo unverständlich aussieht, wird nicht gekauft — egal wie sauber die Engine darunter ist.

Dieser Plan ist die verbindliche Reihenfolge der nächsten Schritte. **Alle Findings aus [`audit_findings.md`](audit_findings.md) sind hier eingeplant** — die Zeit der dokumentierten, aber unangefassten Baustellen ist vorbei. Das Audit bleibt die Detailliste mit Befund und Auswirkung; dieser Plan sagt, wann was drankommt. Die Zuordnung steht am Ende unter [Abdeckung](#abdeckung-des-audits).

> **Verifiziert am 2026-08-25:** Jedes Finding wurde vor der Aufnahme einzeln gegen den Codestand geprüft. **Keines hat sich stillschweigend erledigt.** Drei Korrekturen gegenüber dem Audit-Text: die Streamlit-Duplikate betreffen nur noch `dashboard/legacy_streamlit/` (P5.2), die hartcodierten LLM-Defaults sind von 7 auf 10 Produktionsdateien gewachsen (P3.4), und der als "echter Bug" geführte Testfehler ist eine veraltete Testerwartung, kein Code-Fehler (P4.2).

> **Gegengeprüft am 2026-08-26:** Nach dem Dash-Umbau und der neuen Landingpage wurde jede
> Fundstelle noch einmal aufgeschlagen. **Siebzehn von zwanzig Paketen beschreiben den Codestand
> unverändert korrekt.** Drei Befunde waren falsch oder überholt und sind unten ausgetauscht
> (P1.1 Start-Flow, P1.2 Manifest, Testzahl in Phase 4); sechs Pakete haben einen technischen
> Fallstrick bekommen, der vor der Umsetzung zu entscheiden ist (jeweils als **Fallstrick:**
> ausgewiesen). Neu aufgenommen wurden vier Pakete für Themen, die bisher gar nicht im Plan
> standen: **P0.6** (Run-Artefakte belegen den Reproduzierbarkeits-Claim nicht), **P1.4**
> (die Landingpage kam im Plan nicht vor), **P2.5** (State-Explorer-Grounding) und **P4.3**
> (Doku-Zahlen mechanisch halten).

Gepflegt wird bei jeder abgeschlossenen Aufgabe (siehe [Doku-Pflicht in CLAUDE.md](../CLAUDE.md#doku-pflicht)). Jedes Arbeitspaket nennt **Befund**, **Fundstelle**, **Was zu tun ist**, **Fertig wenn** und **Doku, die mitzieht**. Ein behobenes Finding wird in `audit_findings.md` **entfernt**, nicht abgehakt.

## Was bewusst nicht in diesem Plan steht

- **API-Layer / Multi-Tenancy / Auth / Billing** — noch nicht im Scope (Phase 6).
- **Kundengespräche und Vertrieb** — läuft außerhalb des Repos.
- **IP-/Autorenschaftsfrage** — geklärt, kein Arbeitspaket mehr.
- **Laufzeit und Skalierung** — bewusst offen, aber benannt: wie lange ein realistischer
  LLM-Lauf tatsächlich dauert, steht nirgends. `dashboard/web/runner.py` sagt im eigenen
  Docstring "Ein Lauf dauert Minuten", der 10.000-Tick-Benchmark lief mit `dummy_llm`
  (siehe Phase 6). Für P1.1 war das eine Annahme, kein gemessener Wert. **Der Auslöser ist
  seit dem 2026-08-28 eingetreten** — der Start-Flow steht —, die Zeitangaben in
  `docs/handbuch/lauf-starten.md` sind also weiterhin geschätzt. Dazugekommen ist eine
  zweite Größe, die niemand gemessen hat: Der Preflight baut bei jeder Änderung des
  Entwurfs den vollständigen `SimulationState` auf. Auf einer lokalen Workbench nicht
  spürbar, für Phase 6 zu messen. Gehört als eigenes Paket in Phase 1 oder 3 eingeplant,
  sobald jemand die Reihenfolge festlegt. **Seit P1.5 wiegt der Punkt schwerer:** Die
  Parameterspalte steht jetzt dauerhaft neben Szene und Telemetrie, der Preflight wird
  also häufiger angestoßen als zu der Zeit, als er auf einer eigenen Seite lag.

---

## Phase 0 — Vertrauens-Blocker (vor dem nächsten Demo)

Punkte, die das Kernversprechen "Zahlen aus Python, Narrativ vom LLM" direkt angreifen. Zwei davon produzieren still falsche Ergebnisse — die gehören nach vorn, nicht in eine Hygiene-Liste.

### P0.1 — Stiller LLM-Ausfall wird sichtbar ✅ erledigt 2026-08-26

**Befund (behoben):** Fiel Ollama aus, erzeugte der Agent hartkodierte `NO_OP`-Einträge, der Studio-Client lieferte stumm Mock-Antworten. Ein degradierter Lauf war im Output von einem echten nicht unterscheidbar — nur ein `print()` auf stdout, nichts in den Artefakten. Verschärfend: zwei unabhängige Ollama-Clients mit gegenteiliger Fehlerphilosophie, derselbe Ausfall verhielt sich je nach aktivem Client einmal laut und einmal leise.

**Fundstelle:** [`src/agents/agent_node.py:50-80`](../src/agents/agent_node.py), [`src/llm/studio_helpers.py:153-161`](../src/llm/studio_helpers.py) (`LocalOllama.call`), [`src/llm/llm_client.py`](../src/llm/llm_client.py) (`OllamaClient`).

**Was zu tun ist:** Jeden Fallback über `logging` statt `print` melden; im Run-Artefakt ein Feld `degraded: true` plus Zähler der Fallback-Ticks in `run_metadata.json` schreiben; im Dashboard einen sichtbaren Warnbanner auf jedem Lauf, der degradiert lief. Die zwei Clients auf einen zusammenführen und die laute Philosophie (Retry mit Backoff, dann `RuntimeError`) zum Standard machen.

**Fallstrick (2026-08-26):** "`print` durch `logging` ersetzen" bricht das Fortschritts-Log des Dashboards. [`dashboard/run_launcher.py:397`](../dashboard/run_launcher.py) fängt die Laufausgabe mit `contextlib.redirect_stdout(_StdoutTee())` ab — die Live-Zeilen unter «Simulation starten» werden **ausschließlich** von `print()` gespeist. Ohne einen `logging.Handler`, der in denselben Tee schreibt, bleibt das Fenster danach leer. Dieser Handler ist Teil dieses Pakets und muss **vor** P3.5 stehen, das dieselbe Umstellung im Scheduler macht.

**Fertig wenn:** Ein Lauf mit abgeschaltetem Ollama ist im Dashboard auf den ersten Blick als degradiert erkennbar, das Fortschritts-Log zeigt weiterhin jede Zeile, und ein Test deckt beides ab.

**Umgesetzt am 2026-08-26.** Ein Client (`OllamaClient`), `LocalOllama` nur noch Env-Übersetzung ohne stillen Mock. Ausfälle wandern als typisierte `LLMIncident` über `state.llm_incidents` nach `llm_incidents.json` und markieren den Lauf in `run_metadata.json` als `degraded`; «Ergebnisse ansehen» zeigt darüber einen Warnbanner. `src/logging_setup.py` richtet das bis dahin fehlende Logging ein und reicht die Zeilen zusätzlich ins Fortschrittsfenster — ohne den stdout-Tee zu doppeln. `--mock-llm` liefert jetzt unabhängig von der Umgebung den Mock; ein bewusster Mock-Lauf gilt **nicht** als degradiert.

Zwei Dinge, die bei der Umsetzung auffielen und über den Plan hinausgingen:

- **Der zweite Fallback war der eigentliche Schaden.** `AgentNode` versuchte bei einem Fehler `get_llm()` — war `OLLAMA_MODEL` gesetzt, kam von dort eine erfundene Antwort. Dieser Zweig ist ersatzlos weg; der Agent setzt sichtbar aus, statt heimlich einen Mock zu befragen.
- **Ein Ausfall am Ende riss den ganzen Lauf mit.** Die Erzeugung des Lauf-Szenarios läuft **nach** der Simulation und rief das LLM ungeschützt auf. Mit dem jetzt lauten Client bedeutete das: fertig gerechnet, dann `RuntimeError` — kein `run_metadata.json`, kein Eintrag in der Run-Liste, kein Warnbanner. Die Degradation wäre unsichtbar geworden, weil überhaupt nichts ankommt. Die Pipeline hatte bereits ein deterministisches Template als Fallback; sie fällt jetzt darauf zurück und meldet den Ausfall als Vorfall. Aufgefallen erst beim Nachstellen des Dashboard-Pfades — die erste Prüfung lief mit `--no-run-scenario` und ging daran vorbei.
- **`ParallelRoundNode` verwirft, was es nicht ausdrücklich einsammelt.** Die Agenten laufen auf tiefen Kopien; zurückgetragen wurden nur `round_results` und `event_log`. Provider- und Regulator-Vorfälle gingen deshalb zunächst verloren — sichtbar erst im Lauf gegen einen toten Endpunkt, nicht im Test. Jetzt werden Vorfälle mitgeerntet, ein Regressionstest hält das fest. **Für P3.5 und jeden künftigen Zustand am `SimulationState` gilt dasselbe:** wer dort ein Feld ergänzt, das ein Agent füllt, muss `_invoke_agent_isolated` mitziehen.

**Nachgeprüft am 2026-08-26.** Hält: kein stiller Mock-Pfad mehr (`_build_mock_response` wird nur noch von `MockLLM` aufgerufen), Vorfälle überleben Checkpoint und Resume, `run_multi` isoliert die Läufe sauber, der Redebedarf-Pfad braucht kein Einsammeln (er arbeitet auf dem echten State), und `llm_incidents.json` erscheint tatsächlich im Tab «Dateien». Zwei Kleinigkeiten korrigiert: `OLLAMA_TIMEOUT_SECONDS` war seit der Client-Zusammenführung wirkungslos — `LocalOllama` las die Variable weiter, `call` delegierte aber an den Client, der nur `OLLAMA_READ_TIMEOUT` kennt; `OllamaConfig` hat jetzt ein `read_timeout`, das durchgereicht wird. Und Invariante 1 in `CLAUDE.md` galt pauschal für „einen LLM-Aufruf", trifft aber nur die Aufrufer **innerhalb eines Laufs** — der State Explorer hat keinen State und bekommt seine Zusage in P2.5.

**Gegengeprüft am 2026-08-26 (zweite Person, frisches venv).** Tests, Linting und Formatierung
sind sauber; der einzige Fehlschlag ist der bekannte `marginal_cost_fraction` aus P4.2. Alle
Zusagen des Pakets wurden am laufenden System nachgestellt: ein Lauf gegen einen toten Endpunkt
rechnet zu Ende und protokolliert alle Vorfälle inklusive Provider und Regulator, das
Fortschrittsfenster zeigt `print`- **und** `logging`-Zeilen ohne Dopplung, ein bewusster
Mock-Lauf gilt korrekt nicht als degradiert, und die Prüfungen aus P0.3 greifen an CLI und
Dashboard. **Drei Punkte hat die Gegenprobe zusätzlich gefunden** — keiner blockiert den Merge,
alle drei sind unten eingeplant:

- **Ein Sweep kann nicht als degradiert markiert werden.** Eingeplant in [P0.6](#p06--ein-lauf-sagt-wie-er-entstanden-ist--erledigt-2026-08-27).
- **`get_llm()` wählt weiterhin still den Mock**, wenn keine Umgebungsvariable gesetzt ist. Eingeplant in [P3.4](#p34--llm-konfiguration-zentralisieren--erledigt-2026-09-05).
- **Ein Config-Fehler auf der CLI kommt als roher Traceback.** Eingeplant in [P3.3](#p33--fehlermeldungen-die-auch-greifen--erledigt-2026-09-05).

Der erste Punkt war in der Nachprüfung oben als erledigt vermerkt („Sweeps schreiben die
`degraded`-Felder mit"). Die Aussage stimmt wörtlich und führt trotzdem in die Irre: Geprüft war,
dass die Felder in der Datei landen — nicht, ob sie je `true` werden können. Der Satz ist deshalb
entfernt. **Als Prüfmuster mitnehmen:** Bei einem Feld, das einen Ausfall melden soll, ist "steht
drin" nicht die Frage, sondern "wird es gesetzt, wenn der Ausfall eintritt".

**Doku zieht mit:** `docs/handbuch/fehlerbilder.md`, `docs/handbuch/ref-ausgaben.md`, `README.md`, `CLAUDE.md` (Invariante 1 um "Ausfall ist sichtbar" ergänzt).

### P0.2 — F7-Drift auflösen ✅ erledigt 2026-08-26

> ## ✅ ENTSCHIEDEN **und umgesetzt** am 2026-08-26: **F7 ist „Geopolitische Stabilität"**
>
> **Frage war:** Bedeutet **F7** „Geopolitische Stabilität" oder „Marktstruktur"?
>
> | Wer | Position | Stand |
> | --- | --- | --- |
> | **Haiko** | **Geopolitische Stabilität** | festgelegt am 2026-08-26 |
> | **Manu** | **Geopolitische Stabilität** | bestätigt am 2026-08-26 |
>
> Beide Positionen decken sich mit der *Entscheidungsgrundlage* unten. Damit gilt **Variante A**
> (siehe *Umsetzung nach der Entscheidung*): Der Blocker ist weg, das Paket ist umsetzbar.
>
> **Was die Entscheidung kostet — bewusst mitentschieden:** 48 der 168 Matrixzellen wurden
> unter der Marktlesart bewertet und müssen deshalb **alle neu geprüft** werden. Nachgezählt am
> 2026-08-26: **acht davon sind unter der geopolitischen Lesart nachweislich falsch** — die
> Zeilen `F5.x → F7.x` und `F6.x → F7.x`, denn gesellschaftliche Flugakzeptanz und
> Schienenausbau treiben keine Weltpolitik; `F6.1 → F7.1 = +3` ist dabei der höchste Wert der
> ganzen eingehenden Spalte. Der Rest reicht von plausibel (`F2.x`, `F4.x` lesen sich unter
> beiden Bedeutungen) bis vertretbar — verlassen kann man sich darauf trotzdem nicht, weil er
> unter einer anderen Bedeutung entstanden ist. Neu bewertet wird mit der Begründung aus
> [P2.3](#p23--matrix-provenienz-herstellen--abgeschlossen-2026-08-31-entfallen-rest-erledigt) in einem Zug — zweimal durchgehen ist der teure
> Weg. P0.2 ist deshalb **kein kleines Umbenennungs-Paket**; wer es anfasst, plant die
> Zellendurchsicht mit ein.
>
> **Und eine Vorbedingung, die daraus folgt:** F7 wird in
> [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31) pro Szenario als fixierter
> Deskriptor behandelt. Grund ist der Einwand unten: Geopolitik wirkt stark nach außen und wird
> kaum zurückbeeinflusst — die eingehende Spalte wird nach der Neubewertung dünn.

**Befund:** Die eingefrorene Matrix wurde für **F7 Marktstruktur** bewertet, die Simulation läuft mit **F7 Geopolitische Stabilität**. Die Zustände passen semantisch zufällig (offen/fragmentiert), die Bedeutung nicht. Matrix, Config, Doku und Outputs widersprechen sich — bei einem Produkt, dessen Verkaufsargument Reproduzierbarkeit ist, ist das teuer.

**Fundstelle:** [`configs/factors.json`](../configs/factors.json) (F7 = "Geopolitische Stabilitaet") gegen [`configs/cib_frozen.json`](../configs/cib_frozen.json) (`metadata.note`, 168 Zellen inkl. `F*.*|F7.*`).

**Entscheidungsgrundlage (erarbeitet am 2026-08-26).**

Die Drift ist **kein späterer Umbenennungsfehler**: Im allerersten Commit des Repos (`7692a91`) steht in `factors.json` bereits "Geopolitische Stabilitaet" und in `cib_frozen.json` bereits "F7 Marktstruktur". Es gibt keine ursprüngliche Absicht, die wiederherzustellen wäre — die Lesart ist frei zu wählen.

*Was die Matrix sagt: **Marktstruktur**.* Die eingehende Spalte lässt sich nur so lesen. Die vier stärksten Einflüsse auf F7.1 sind `F2.1 → F7.1 = +3` (milde Regulierung → offener Markt, also Liberalisierung), `F6.1 → F7.1 = +3` (Fliegen bleibt akzeptiert → Markt wächst), `F5.1 → F7.1 = +2` (keine Schienenkonkurrenz → Luftverkehrsmarkt floriert) und `F1.1 → F7.1 = +2` (Nachfrageboom → Marktexpansion). Unter "Geopolitik" wären davon mindestens sechs der 24 eingehenden Zellen schlicht falsch, darunter der höchste Wert der Spalte: gesellschaftliche Flugakzeptanz treibt keine Weltpolitik, Schienenausbau erst recht nicht. Auch die ausgehende Zeile passt zur Marktlesart — `F7.1 → F1.1 = +2` ist die Liberalisierungs- und Billigflieger-Geschichte in einer Zelle. [`docs/cib_role.md`](cib_role.md) und [`docs/cib_rationale.md`](cib_rationale.md) folgen derselben Lesart ("Marktfragmentierung", "offene, integrierte Märkte", "Regulierung vs. Markt").

*Was die Engine sagt: **Geopolitik**.* Zwei Funde wiegen schwerer als die Matrix:

1. **Das Rechenmodell kennt keinen Wettbewerb.** Eine Suche nach `competition`, `concentration`, `market_share`, `hhi` oder `n_carriers` über `src/` und `configs/` liefert **null Treffer**. Es gibt einen Provider-Agenten, einen Markup, einen Ticketpreis. "Marktstruktur" wäre ein Deskriptor, den die Simulation nicht darstellen kann — dieselbe Klasse von Claim-ohne-Deckung, die P2.1, P2.2 und P2.5 gerade abräumen.
2. **Die einzige Regel für F7 hängt an einem exogenen Ölpreis.** `f7_oil_stress` und `f7_open_markets` ([`configs/properties.json`](../configs/properties.json)) schalten F7 allein über `oil_price_index` — und diese Property ist `source: "trajectory"` mit Baseline 1.0 und ohne Regeln, also ein reiner Szenario-Schalter von außen. Marktstruktur, die ausschließlich einem exogenen Ölindex folgt und keinerlei Rückkopplung aus Preis, Buchungsrate oder Marge kennt, ist modelltheoretisch verkehrt: Marktstruktur *entsteht* aus dem Markt. Für einen externen Schock ist genau dieses Muster richtig.

*Empfehlung: **Geopolitische Stabilität**.* Der Grund ist eine Kostenrechnung. Bei "Marktstruktur" bliebe die Matrix stehen, aber man schuldete der Engine einen Wettbewerbsmechanismus (mehrere Anbieter, Konzentration, Marktanteile) — kein Phase-0-Paket, sondern ein Umbau des Marktmodells. Bei "Geopolitik" sind **48 der 168 Zellen** neu zu bewerten; da P2.3 ohnehin verlangt, jede Zelle mit einer Begründung zu versehen, ist einmal unter dem richtigen Namen durchgehen billiger als zweimal. Dazu kommt: Es ist, was heute läuft (`factors.json`, die F7-Regeln, Dashboard, Handbuch), die Zustandsbeschreibung ist bereits geopolitisch ("Offene Lufträume, Konflikte, Pandemien"), und produktseitig fehlte sonst die einzige Schockachse — F1–F6 sind alle innereuropäisch und endogen, während eine Strategieabteilung Pandemie, Krieg und Luftraumsperrungen durchspielen will. Marktstruktur ist über F2 (Liberalisierung) und F1 (Nachfrage) zudem teilweise schon abgedeckt.

*Der Einwand, der dazugehört.* CIB will endogene Deskriptoren, die einander beeinflussen. Geopolitik wirkt stark nach außen und wird kaum zurückbeeinflusst — die eingehende Spalte wird nach der Neubewertung dünn. Das ist beherrschbar, muss aber bewusst entschieden werden und **löst eine Vorbedingung in [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31) aus**.

*Nebenbefund, unabhängig von der Entscheidung.* Die Zustandsbezeichnung "F7.1 Offene Märkte, Kooperation" **mischt beide Lesarten** — "offene Märkte" ist Marktsprache, "Kooperation" ist Politik. Das ist vermutlich die Bruchstelle, an der die Drift entstand. Unter Geopolitik müssten die Zustände etwa "Offene Lufträume, multilaterale Kooperation" und "Fragmentierung, Sperrungen, Konflikte" heißen; die Umbenennung gehört in dieses Paket.

**Was zu tun ist:** Entscheiden, welche Bedeutung F7 trägt. Dann Matrix, `factors.json`, Glossar und Handbuch auf **eine** Lesart ziehen. Danach ein Test, der Faktor-IDs und -Namen zwischen `factors.json` und `cib_frozen.json` mechanisch vergleicht, damit die Drift nicht wiederkommt.

**Abgrenzung zu P2.3 — abhängig von der Entscheidung:** Fällt sie auf **Marktstruktur**, ist hier nur umzubenennen und die 168 Einflusswerte bleiben unberührt; Phase 0 hängt dann nicht an einer Zellendurchsicht. Fällt sie auf **Geopolitische Stabilität** (die Empfehlung oben), sind alle 48 F7-Zellen neu zu bewerten — acht davon nachweislich falsch, der Rest unter einer anderen Bedeutung entstanden und damit nicht belastbar — dann gehört P2.3 für diese Zellen vorgezogen, weil zweimal durchgehen der teure Weg ist. In beiden Fällen bleibt der mechanische Namensabgleich zwischen `factors.json` und `cib_frozen.json` Teil dieses Pakets.

**Umsetzung nach der Entscheidung.** Beide Wege sind hier vollständig ausgeschrieben, damit nach dem einen fehlenden Satz nichts mehr zu klären ist.

*Variante A — **Geopolitische Stabilität*** (Haikos Position und Empfehlung dieser Auswertung):

1. `configs/factors.json`: Zustandsbezeichnungen entmischen — `F7.1` von „Offene Maerkte, Kooperation" auf „Offene Lufträume, multilaterale Kooperation", `F7.2` von „Fragmentierung, Konflikte" auf „Fragmentierung, Sperrungen, Konflikte". Name und Beschreibung bleiben.
2. `configs/cib_frozen.json`: `metadata.factors` auf „F7 Geopolitische Stabilität" ziehen, `metadata.note` nachführen — **und die 48 F7-Zellen neu bewerten**, weil die heutigen Werte eine Marktlogik kodieren. Für diese Zellen [P2.3](#p23--matrix-provenienz-herstellen--abgeschlossen-2026-08-31-entfallen-rest-erledigt) vorziehen: Begründung gleich mitschreiben statt zweimal durchgehen. Die Matrix bleibt eingefroren (Invariante 3).
3. [`scripts/rebuild_cib_frozen.py`](../scripts/rebuild_cib_frozen.py) mitziehen, damit ein Neubau dieselben Werte erzeugt.
4. `docs/cib_role.md`: die Active/Passive-Tabelle enthält F7-Scores, die aus den alten Zellen stammen — nach der Neubewertung neu rechnen. `docs/cib_rationale.md`: die Zeilen zu `f7_oil_stress` und `f7_open_markets` sprechen von „Marktfragmentierung" und „offene, integrierte Märkte" und müssen auf die geopolitische Lesart (Ölpreis als Indikator geopolitischer Spannung) umgeschrieben werden.
5. Test, der Faktor-IDs **und -Namen** zwischen `factors.json` und `cib_frozen.json` mechanisch vergleicht — damit die Drift nicht wiederkommt.
6. Die Vorbedingung in [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31) festschreiben: F7 wird pro Szenario als fixierter Deskriptor behandelt.
7. `CLAUDE.md` (Glossar), `docs/handbuch/faktoren.md`.

*Variante B — **Marktstruktur***:

1. `configs/factors.json`: F7-Name auf „Marktstruktur", Beschreibung von „Offene Luftraeume, Konflikte, Pandemien" auf eine Marktbeschreibung; `F7.1`/`F7.2` auf „Offener, wettbewerblicher Markt" bzw. „Konsolidierung/Fragmentierung".
2. `configs/cib_frozen.json` bleibt unberührt — das ist der Vorteil dieser Variante.
3. Die beiden F7-Regeln überdenken: `oil_price_index` als **einzige** Ursache von Marktstruktur ist schwach, und die Wirkrichtung „Ölschock → Fragmentierung" ist ökonomisch eher umgekehrt (Ölschock → Insolvenzen → *Konsolidierung*).
4. **Offene Schuld eintragen:** Die Engine kennt keinen Wettbewerbsbegriff (kein `competition`, `concentration`, `market_share`, `n_carriers`; ein Provider, ein Markup, ein Preis). F7 trüge dann einen Namen, den die Simulation nicht einlösen kann. Das gehört als neues Finding in `docs/audit_findings.md` und als eigenes Paket in Phase 2 — sonst entsteht genau die Sorte Claim-ohne-Deckung, die P2.1, P2.2 und P2.5 gerade abräumen.
5. Test wie in Variante A, Schritt 5.
6. `CLAUDE.md` (Glossar), `docs/handbuch/faktoren.md`, `docs/cib_role.md`, `docs/cib_rationale.md`.

**Fertig wenn:** Faktorname in Config, Matrix, Doku und Run-Output identisch; die 48 F7-Zellen sind unter der geopolitischen Lesart neu bewertet und je mit Begründung versehen; der mechanische Namensabgleich zwischen `factors.json` und `cib_frozen.json` läuft als Test grün.

**Umgesetzt am 2026-08-26 (Variante A).** Alle 48 F7-Zellen einzeln durchgegangen: **19 geändert, 29 unverändert bestätigt** — jede mit Begründung, die jetzt als `reasoning` in der JSON steht (P2.3 für diese Zellen vorgezogen). Die acht offensichtlich falschen (`F5.x → F7.x`, `F6.x → F7.x`) stehen auf **0**: Schienenausbau und gesellschaftliche Flugakzeptanz treiben keine Weltpolitik, und dafür gibt es keinen schwachen Wert, sondern gar keinen Mechanismus. Deutlich verstärkt wurde dagegen die Gegenrichtung — `F7.2 → F1.1` von −2 auf **−3**, weil Luftraumsperrungen und Pandemien der größte beobachtete Nachfrageschock der Branche sind.

Drei Dinge, die dabei über den Plan hinausgingen:

- **Die Namen kommen jetzt aus einer Quelle.** `metadata.factors` in der Matrix wurde bisher von Hand gepflegt — genau die doppelte Pflege, aus der die Drift entstand. `rebuild_cib_frozen.py` liest die Namen jetzt aus `factors.json`; beim Neubau ist ein Auseinanderlaufen baulich unmöglich, und der neue Test fängt eine Änderung von Hand ab. Nebenbefund: **F1–F6 tragen in beiden Dateien verschiedene Namen** („Regulatorische Strenge" vs. „Regulierung") — Kurzformen, keine Widersprüche, aber ein strenger Vergleich hätte sie sonst fälschlich angeschlagen. Sie sind mit angeglichen.
- **Die Active/Passive-Tabelle in `docs/cib_role.md` war schon vorher falsch.** Keine einzige Zeile stimmte mit der Matrix überein — nicht durch diese Änderung, sondern seit Längerem von Hand eingetragen und nie nachgezogen. Korrigiert, mit Hinweis auf die Herkunft der Zahlen.
- **`scripts/rebuild_cib_frozen.py` brach nach dem Schreiben ab.** Der Selbsttest am Ende importiert `src`, was beim Start über den Dateipfad nicht auf dem Suchpfad liegt. Die Matrix wurde also geschrieben, danach flog ein `ModuleNotFoundError` — wer das Skript benutzte, sah einen Fehler und eine trotzdem geänderte Datei. Behoben.

**Was sich an den Kennzahlen verschoben hat:** BAU 0.973 → 0.970, Konflikt 0.867 (unverändert), Freiwillige Wende 0.603 → 0.629 bei einem Konflikt weniger. **Der Kernnachweis BAU > Konflikt hält.** Die Wende bewegt sich, weil ihr Widerspruch zum Teil daran hing, dass offene *Märkte* mit strenger Regulierung kollidierten — offene *Lufträume* tun das nicht im selben Maß. `test_cib_ranking.py` und beide CIB-Dokumente sind nachgezogen.

**Offen und bewusst so markiert:** Die 48 Werte sind modellgeneriert und fachlich nicht abgenommen; die Notiz in `cib_frozen.json` sagt das, und ein Test hält es fest. **Das Quellenlabel hat sich am 2026-08-31 geändert** — es hieß `llm_proposed_pending_review_v3` und kündigte damit eine Durchsicht an; seit P2.3-Rest heißt es `beleg_keine_bewertende_rolle`, weil unter Variante C keine mehr vorgesehen ist.

**Zurückgestellt am 2026-08-29 — mit Grund, nicht vergessen.** Die fachliche Abnahme der 48 Zellen ist **nicht mehr eingeplant**, bis die Szenarienschicht steht ([Leitentscheidung](#leitentscheidung-die-szenarienschicht-2026-08-29)). Der Grund kam aus dem Versuch, sie vorzubereiten: Beim Nachmessen der übrigen 120 Zellen zeigte sich, dass die Matrix im Kern **eine einzige Achse** ist — nur 12 von 84 gleichpoligen Zellen tragen Spannung, und vier unbegründete Zellen verneinen die Rückkopplung, aus der gemischte Szenarien entstehen. Ob `F5.1 → F7.1` bei 0 oder +1 steht, bewegt dagegen nichts. Wer die 48 prüft, bevor über **Rolle und Erhebung** der Matrix entschieden ist, prüft Werte, die danach ohnehin neu erhoben werden müssten; unter der gewählten Variante C entfällt die Prüfung ganz. Das Label `llm_proposed_pending_review_v3` blieb deshalb zunächst stehen und war ab da **richtig**, nicht nur vorläufig. **Am 2026-08-31 ist es ersetzt worden** (P2.3-Rest): Nachdem P2.2 die Abnahme endgültig hat entfallen lassen, kündigte ein «pending review» eine Prüfung an, die niemand mehr vorhat — die Quelle heißt jetzt `beleg_keine_bewertende_rolle`.

**Doku zieht mit:** `docs/handbuch/faktoren.md`, `docs/cib_role.md`, `docs/cib_rationale.md`, `CLAUDE.md` (Glossar).

### P0.3 — `validate_config` implementieren ✅ erledigt 2026-08-26

**Befund (behoben):** `validate_config` gab bedingungslos `[]` zurück, wurde aber von `validate_state` behandelt, als würde echt geprüft. Fehlerhafte Configs liefen unbemerkt durch.

**Fundstelle:** [`src/validation.py:54-55`](../src/validation.py); vestigieller Parameter `factor_ids` in `validate_agent` (Zeile 42-51) gleich mitnehmen.

**Was zu tun ist:** Pflichtfelder, Wertebereiche (`llm.temperature`, `max_ticks`, Seeds) und Referenz-Integrität prüfen — insbesondere, ob Agenten auf existierende Faktor-IDs verweisen (dafür ist `factor_ids` gedacht). Fehler als Liste zurückgeben, im Dashboard vor dem Start anzeigen.

**Fertig wenn:** Eine absichtlich kaputte Config wird beim Start mit klarer Meldung abgewiesen, Tests decken die Fälle ab.

**Umgesetzt am 2026-08-26.** `validate_config` prüft Name, Modellname, `llm.temperature` (0–2), `llm.max_tokens` und den Seed; `validate_agent` benutzt endlich seinen `factor_ids`-Parameter und schlägt an, wenn ein Profil auf einen unbekannten Faktor oder eine unbekannte Abhängigkeit zeigt. Neu daneben: `collect_state_errors` sammelt alle Befunde, ohne zu werfen — `validate_state` bleibt der werfende Weg für den Runner. Das Dashboard zeigt die Liste im Tab «Kontrolle» und weist den Start ab, statt den Lauf anfangen zu lassen. `max_ticks` war bereits in `validate_clock` abgedeckt und wurde nicht dupliziert.

Drei Dinge, die bei der Umsetzung dazukamen:

- **Der Befund war belegbar, nicht theoretisch.** Ein negativer Seed kam durch alle Prüfungen und riss den Lauf erst im ersten Tick mit `ValueError: expected non-negative integer` aus numpy ab — im Dashboard sichtbar als „Lauf fehlgeschlagen: expected non-negative integer", ohne jeden Bezug zum Seed. Jetzt wird er vor dem Start mit Namensnennung abgewiesen.
- **`depends_on` war die stillste Lücke.** `check_depends_on` kennt genau vier gültige Werte; alles andere landet im `else`-Zweig und gilt in **jedem** Tick als unerfüllt. Ein Tippfehler in `agent_profiles.json` hätte den Agentenkontext dauerhaft und lautlos beschnitten. Das Vokabular liegt jetzt als `KNOWN_DEPENDENCIES` in `agent_dependencies.py`, und die Validierung prüft dagegen — bewusst **eine** Quelle, keine zweite Liste (genau die Doppelung räumt P0.5 an anderer Stelle ab).
- **Reihenfolge im Runner korrigiert.** `_seed_runtime` lief vor `validate_state`; jetzt umgekehrt. Erst prüfen, dann handeln.

**Nachgeprüft am 2026-08-26 — eine Lücke gefunden und geschlossen.** Die erste Fassung prüfte `llm.model`, `llm.temperature` und `llm.max_tokens` auf `state.config.llm` — ein Feld, das **kein Laufpfad liest**. Die einzigen Leser sind `langgraph_adapter.py` (Schema-Defaults für Studio) und die Prüfung selbst. Die Werte, die tatsächlich beim Modell landen, kommen aus dem Dashboard-Draft bzw. den CLI-Argumenten und gingen ungeprüft durch: ein Draft mit `temperature=5.0`, `max_tokens=0` und leerem Modellnamen galt als fehlerfrei. Also genau die Klasse von Problem, gegen die dieses Paket angetreten ist.

Behoben: `validate_llm_settings` hält die Regeln **einmal** und wird von drei Orten aufgerufen — `validate_config` (Datei), `validate_draft` (Dashboard) und `main()` (CLI). Der Seed war nicht betroffen; er wird aus dem Draft in den State geschrieben *und* vom Sampler gelesen, war also von Anfang an richtig geprüft. Die Lücke blieb offen, weil die Tests `validate_draft` nur mit dem Default-Draft und mit `seed=-1` prüften — auch das ist ergänzt.

**Zweite Nachprüfung, gleicher Tag — die Korrektur hatte selbst einen Fehler.** Die neue Prüfung lief unbedingt und blockierte damit Läufe, die gar kein Sprachmodell benutzen: Beide unteren Rechenmodi («Ohne Sprachmodell» und «Nur Zahlen») setzen `mock_llm`, und dann liefert `_build_llm()` ein `MockLLM` — Modellname, Temperatur und Antwortlänge werden nie angefasst. Ein leeres Modellfeld verhinderte trotzdem den Start. Dasselbe auf der CLI mit `--mock-llm --max-tokens 0`. Die Prüfung hängt jetzt an `mock_llm`, und zwei Tests halten beide Richtungen fest. Aufgefallen ist es, weil `ConfigDraft` per Default `mock_llm=True` führt — meine eigenen Tests prüften deshalb ins Leere und mussten mitgezogen werden.

Bewusst **nicht** hier behoben: dass `state.config.llm` von niemandem gelesen wird. Das gehört zu [P3.4](#p34--llm-konfiguration-zentralisieren--erledigt-2026-09-05).

**Dritte Nachprüfung — mechanisch statt nach Gefühl.** Weil die beiden vorigen Funde dieselbe Ursache hatten (ein Test, der seine eigene Voraussetzung nicht erreichte), wurde diesmal jede Zusage einzeln im Code abgeschaltet und geprüft, ob ein Test das merkt. **Dreizehn von dreizehn** Zusagen aus P0.1 und P0.3 sind so gedeckt. Eine Lücke kam dabei heraus: Der Start-Callback in `dashboard/web/pages/launch.py` — also die Zusage „«Start» weist ab" — war von keinem Test berührt; gedeckt war nur die Ansicht im Tab «Kontrolle». Zwei Tests in `tests/test_web_runner.py` prüfen ihn jetzt mitsamt der Reihenfolge seines Rückgabe-Tupels, die zu den fünf `Output`s passen muss.

**Doku zieht mit:** `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/fehlerbilder.md`.

### P0.4 — Regelauswertung vereinheitlichen ✅ erledigt 2026-08-27

**Befund:** Die generische "when/effect"-Regelauswertung existiert **dreimal unabhängig** und ist bereits auseinandergelaufen: `factor_dynamics.rule_matches` kennt `tick`, `metric` und `system_property`, `population_sampler._rule_matches` nur exaktes `factor`-Matching und `system_property`, und die Aktivierung der `regulatory_influences` in `simulation_functions` wertet dieselbe Klausel ein drittes Mal aus. Eine `shift_rule` mit `at_least`- oder `tick`-Bedingung greift im Sampler **still nie** — kein Fehler, kein Hinweis, einfach kein Effekt. Dazu: `market_rules.py` behandelt trotz generischem Namen nur einen einzigen hartcodierten Regeltyp (`booking_yield_feedback`).

**Fundstelle:** [`src/market/factor_dynamics.py:87`](../src/market/factor_dynamics.py) (`rule_matches`), [`src/population/population_sampler.py:243`](../src/population/population_sampler.py) (`_rule_matches`), [`src/market/simulation_functions.py:124`](../src/market/simulation_functions.py) (`regulatory_influences`), [`src/market/market_feedback.py`](../src/market/market_feedback.py) — hieß zum Zeitpunkt des Befunds `market_rules.py`.

**Verifiziert am 2026-08-26:** `rule_matches` (Zeile 87) kennt `tick` (`gte`/`lte`/`eq`), `factor`, `metric` (`above`/`below`/`at_most`/`at_least`) und `system_property` (inkl. `at_least`) — `_rule_matches` (Zeile 243) nur exaktes `factor`-Matching und `system_property` mit `above`/`below`. Die Divergenz ist real und unverändert. (Die frühere Fassung dieser Zeile sagte "nur `system_property`" und widersprach damit dem eigenen Befund oben; `factor` kann der Sampler sehr wohl.)

**Gegengeprüft am 2026-08-27 — eine Entschärfung, vier Ergänzungen.**

*Die Entschärfung:* Alle `when`-Klauseln aller Configs wurden inventarisiert. **Keine ausgelieferte `shift_rule` benutzt heute `at_least` oder `tick`** — die neun Shift-Regeln in `properties.json` nutzen ausschließlich `factor`/`state` und ein `system_property` mit `above`, also genau die Schnittmenge, die beide Evaluatoren beherrschen. `configs/sweeps/` enthält überhaupt keine Regeln, und die Oberfläche kann keine schreiben: Shift-Regeln werden von Hand in `properties.json` gepflegt. Die Divergenz produziert also **noch keine** falschen Zahlen, sie ist eine scharf gestellte Falle für die nächste Regel. Der frühere Satz "das sind falsche Zahlen" stand im Präsens und ist deshalb hier ersetzt — die Priorität bleibt, die Behauptung wird korrekt.

*Die Ergänzungen:*

1. **Ein dritter Evaluator, bisher weder im Plan noch im Audit.** [`simulation_functions.py:124`](../src/market/simulation_functions.py) wertet `regulatory_influences[].when` eigenständig aus und kennt nur `factor` und `system_property`.
2. **Und er hat einen echten Bug.** Seine Vergleiche sind per `elif` verkettet (Zeilen 137–139): stehen `above` **und** `below` in derselben Klausel, wird `below` nie geprüft. Latent — keine heutige Config nutzt beides.
3. **`factor` ohne `state` greift in allen drei Evaluatoren still nie.** Überall steht `str(when.get("state", ""))`, verglichen wird gegen `""`. Ein vergessenes `state` ist dieselbe lautlose Wirkungslosigkeit, gegen die dieses Paket antritt.
4. **Doku und Code widersprechen sich beim leeren `when`.** [`narrative.py:238`](../src/reporting/output_writer/narrative.py) schreibt für eine Regel ohne Bedingung "immer" ins Protokoll — der Code lässt sie nie greifen (`if not when: return False`). Derselbe Renderer kennt `metric` und `at_least` nicht und stellt solche Regeln unvollständig dar.

**Entschieden am 2026-08-27 (Haiko).** Zwei Fragen, die den Umfang bzw. das Verhalten ändern, sind vor der Umsetzung geklärt:

- **Alle drei Evaluatoren werden zusammengeführt**, nicht nur die zwei aus dem ursprünglichen Befund. Zwei von drei zu vereinigen würde die Doppelung verschieben statt auflösen — derselbe Fallstrick, den [P0.5](#p05--faktor-berechtigungen-aus-einer-quelle--erledigt-2026-08-27) für die Berechtigungen beschreibt. Der `elif`-Bug verschwindet dabei von selbst.
- **Ein leeres `when` heißt "keine Bedingung", also wahr** — die semantisch richtige Lesart, die auch das Protokoll schon behauptet. Damit eine bedingungslose `factor_rule` oder `shift_rule` nicht plötzlich in jedem Tick feuert, wird sie stattdessen in `validation.py` **laut abgewiesen**: eine Regel ohne Bedingung ist fast sicher ein Config-Fehler. `regulatory_influences` dürfen unbedingt gelten und bleiben erlaubt. Prüfen statt raten — dieselbe Linie wie [P0.3](#p03--validate_config-implementieren--erledigt-2026-08-26).

**Was zu tun ist:** Einen gemeinsamen Evaluator bauen, alle drei Aufrufer darauf ziehen. Unbekannte Bedingungstypen müssen **laut fehlschlagen** statt still `False` zurückzugeben — genau das hat die Divergenz so lange versteckt. `market_rules.py` entsprechend seinem tatsächlichen Inhalt benennen oder auflösen.

**Vorgesehener Schnitt (2026-08-27).** Neues Top-Level-Modul `src/rule_engine.py` — dieselbe Begründung wie bei `validation.py` und `config_loader.py`: von mehreren Paketen genutzt. `src/population` importiert heute nichts aus `src/market`, und diese Richtung soll nicht neu entstehen.

1. `RuleContext` (Tick, Faktoren, Metriken, System-Properties) und **ein** `rule_matches(when, context)`.
2. `UnknownRuleConditionError` bei unbekanntem Schlüssel, bei einem Operator ohne Subjekt (`above` ohne `metric`/`system_property`/`tick`) und bei `factor` ohne `state`.
3. `once` fliegt aus dem Prädikat heraus — es ist keine `when`-Bedingung, und beide Aufrufer führen ihre Buchhaltung ohnehin getrennt (`applied_factor_rule_ids` global, `applied_shift_rules` pro Person).
4. Tick und Metriken werden bis in den Sampler durchgereicht. `build_runtime_metrics` bleibt in `factor_dynamics`, weil es den `SimulationState` braucht; der Evaluator sieht nur eine Zuordnung von Metrik-Namen auf Werte.
5. `narrative.py` beschreibt Regeln über **eine** Funktion des neuen Moduls, damit Protokolltext und Auswertung nicht wieder auseinanderlaufen.

**Nebenbefund, der sich mitauflöst:** `run_population_tick` nimmt bereits ein `current_tick`, das nirgends benutzt wird — in [P5.1](#p51--toter-code-und-irreführende-namen--erledigt-2026-09-11) als toter Parameter geführt. Es ist genau der Wert, den der gemeinsame Evaluator für `tick`-Bedingungen braucht. Das Audit sagt zu diesem Parameter bereits, er solle **nicht** entfernt werden, weil P2.1 ihn braucht — P0.4 macht ihn schlicht schon vorher benutzt, womit er aufhört, vestigiell zu sein. Der tote Code **in** `market_rules.py` (`initial_ticket_price`, `active_market_rule`) bleibt dagegen bei P5.1 und wird hier nicht vorgezogen.

**Fertig wenn:** Dieselbe Regel liefert an allen drei Aufrufstellen dasselbe Ergebnis; ein Test deckt `at_least` und `tick` im Sampler-Pfad ab; eine unbekannte Bedingung und ein `factor` ohne `state` schlagen sichtbar fehl statt still zu verpuffen; eine Regel ohne Bedingung wird von der Config-Prüfung abgewiesen; der Protokolltext beschreibt dieselbe Bedingung, die auch ausgewertet wird.

**Umgesetzt am 2026-08-27.** `src/rule_engine.py` ist die eine Auswertung; `factor_dynamics.rule_matches`, `population_sampler._rule_matches` und der Zweig in `simulation_functions` sind ersatzlos weg. `market_rules.py` heißt jetzt `market_feedback.py` — der Config-Schlüssel `market_rules` bleibt, umbenannt wurde nur das Modul. `describe_when` speist den Protokolltext, damit Beschreibung und Auswertung dieselbe Quelle haben. Neue Invariante 6 in `CLAUDE.md`.

Vier Dinge, die bei der Umsetzung über den Plan hinausgingen:

- **Das Vokabular ist jetzt für alle Bezugsgrößen dasselbe.** Vorher kannte `metric` ein `at_most`, `system_property` nicht, und `tick` hatte mit `gte`/`lte`/`eq` einen dritten Satz. Jetzt gelten `above`, `below`, `at_least`, `at_most`, `eq` überall; `gte`/`lte` bleiben als Altnamen gültig.
- **Zwei numerische Bezugsgrößen in einer Klausel sind jetzt ein Fehler.** Die alte Fassung wandte denselben Operator unabhängig auf `metric` **und** `system_property` an — ein Vergleich ließ sich keiner von beiden zuordnen. Das ist keine Bedingung mehr, sondern eine Meldung.
- **`metric` ist bei `regulatory_influences` nicht auswertbar** und wird jetzt abgewiesen. Die Kostenrechnung läuft, bevor es Laufzeitmetriken gibt (`cost_pressure` ist selbst eine davon). Das laut zu sagen ist billiger als eine Regel, die nie greift — genau der Befund dieses Pakets, nur an einer Stelle, wo die Fähigkeit wirklich fehlt.
- **Namen prüft `validation.py`, nicht der Evaluator.** Zur Laufzeit sieht ein Tippfehler in `metric` oder `system_property` aus wie ein Wert, den es in diesem Tick eben noch nicht gibt — ununterscheidbar. Beim Laden sind beide Vokabulare bekannt, dort fällt er auf. Ein leeres `when` wird bei `factor_rules` und `shift_rules` abgewiesen, bei `regulatory_influences` erlaubt.

**Was die Zahlen macht:** nichts. Die ausgelieferte `properties.json` läuft durch alle neuen Prüfungen fehlerfrei, und keine ihrer Regeln benutzte eine Bedingung, die vorher an einer Stelle anders gelesen wurde. 649 Tests grün, davon 80 neue in `tests/test_rule_engine.py`; der einzige Fehlschlag bleibt der bekannte `marginal_cost_fraction` aus P4.2.

**Ein Fund, der hier bewusst liegen bleibt:** Der Kostendruck wird an zwei Stellen berechnet, und nur eine übergibt Faktoren und Systemgrößen — siehe [P0.7](#p07--kostendruck-aus-einer-quelle--erledigt-2026-08-27). Die Korrektur verschiebt Faktorverläufe und damit Laufergebnisse; das ist eine Modelländerung und gehört nicht in ein Paket, das Auswertungen vereinheitlicht.

**Doku zieht mit:** `docs/handbuch/ref-config.md`, `docs/handbuch/preisbildung.md`, `CLAUDE.md` (Architektur-Map, Invariante 6, Glossar-Eintrag `when`-Klausel).

### P0.5 — Faktor-Berechtigungen aus einer Quelle ✅ erledigt 2026-08-27

**Befund:** Zwei unabhängige Quellen für "welcher Agent darf welchen Faktor ändern": ein hartcodiertes Dict `AGENT_FACTOR_PERMISSIONS` und `may_propose` in `agent_profiles.json`. Beide stimmen heute überein, werden aber nicht mechanisch synchron gehalten — und die hartcodierte ist die durchsetzende. Eine neue Berechtigung in der JSON würde still ins Leere laufen. Das greift Invariante 2 direkt an.

**Fundstelle:** [`src/market/factor_dynamics.py:13`](../src/market/factor_dynamics.py), [`src/agents/agent_node.py`](../src/agents/agent_node.py), Durchsetzung in `environment_node._apply_state_changes`.

**Was zu tun ist:** Berechtigungen ausschließlich aus `configs/agent_profiles.json` ableiten, das Dict entfernen. Test, der eine in der JSON ergänzte Berechtigung end-to-end durchreicht.

**Fallstrick (2026-08-26):** Eine gemeinsame Quelle reicht nicht — es gibt auch zwei **Prüfstellen**. `agent_node.py` wertet `profile.may_propose` unabhängig von `factor_dynamics.validate_factor_proposals` aus. Beide nur auf dieselbe JSON zu ziehen, verschiebt die Doppelung, statt sie aufzulösen: die Regel steht dann weiterhin an zwei Orten und kann weiterhin auseinanderlaufen. Zusammenführen auf **eine** Funktion, die beide Aufrufer benutzen.

**Fertig wenn:** `agent_profiles.json` ist die einzige Quelle **und** es gibt genau eine Funktion, die eine Berechtigung prüft; eine Änderung in der JSON wirkt ohne Codeänderung.

**Umgesetzt am 2026-08-27.** `AGENT_FACTOR_PERMISSIONS` ist entfernt, `configs/agent_profiles.json` ist die einzige Quelle. Geprüft wird in `src/agents/agent_permissions.may_propose_factor` — Parser und Durchsetzung rufen dieselbe Funktion, der Fallstrick ist damit adressiert. Der Abnahmetest baut ein Konfigurationsverzeichnis mit **einer** zusätzlichen Zeile in `may_propose` und zeigt, dass sie bis in `validate_factor_proposals` durchreicht; er prüft vorher, dass dieselbe Berechtigung ohne diese Zeile abgewiesen wird — sonst prüfte er nichts.

Zwei Dinge, die dabei auffielen:

- **Die zwei Prüfstellen hatten gegenläufige Voreinstellungen.** Ohne Profil ließ der Parser in `agent_node` **alles** durch (`if self.config.profile and ...`), die Durchsetzung ließ **nichts** durch (`.get(agent_id, set())`). Das fiel nie auf, weil die Durchsetzung als zweite läuft und das Ergebnis rettete. Für eine Berechtigungsregel ist nur eine Richtung vertretbar: Wer nicht ausdrücklich darf, darf nicht. Beide Stellen verhalten sich jetzt so.
- **Die Grammatik `factor_state F2` stand an drei Stellen als Zeichenkette** — Parser, Durchsetzung und `validation.py`. Sie liegt jetzt einmal in `agent_permissions.py`; `validation.py` benutzt denselben Parser, statt das Präfix erneut zu buchstabieren.

**Doku zieht mit:** `docs/agent_profiles.md`, `CLAUDE.md` (Invariante 2, Architektur-Map).

### P0.6 — Ein Lauf sagt, wie er entstanden ist ✅ erledigt 2026-08-27

**Befund (neu am 2026-08-26):** `run_metadata.json` belegt den Reproduzierbarkeits-Claim nicht. Geschrieben werden Modell, `base_url`, Temperatur, `max_tokens` und Tick-Zahlen — **nicht** der Seed, nicht `mock_llm`, nicht `deterministic_only`, kein Hash der verwendeten Configs, kein Codestand. An einem echten Artefakt geprüft (`outputs/sweeps/sweep_low_base/run_metadata.json`): dort steht `"model": "dummy_for_sweeps"`, aber weder mit welchem Seed gezogen wurde noch ob überhaupt ein LLM beteiligt war. Aus den Artefakten allein lässt sich ein Lauf heute nicht nachstellen — bei einem Produkt, dessen Verkaufsargument Reproduzierbarkeit ist, die teuerste Lücke in Phase 0.

**Fundstelle:** [`src/reporting/output_writer/metadata.py:28-43`](../src/reporting/output_writer/metadata.py) (`save_run_metadata`); Aufrufer in [`src/run_simulation.py`](../src/run_simulation.py) und [`dashboard/run_launcher.py`](../dashboard/run_launcher.py).

**Dazugekommen aus der P0.1-Gegenprobe (2026-08-26): der Sweep-Pfad schreibt an P0.1 vorbei.**
[`scenario_sweeps.py:262`](../src/orchestration/scenario_sweeps.py) ruft `save_run_metadata`
**vor** `generate_and_save_run_scenario` (Zeile 281), verwirft den zurückgegebenen `llm_error`
und ruft `save_llm_incidents` überhaupt nicht. Ein Sweep läuft `deterministic_only`, hat also
genau eine Ausfallquelle — den Szenario-Text am Ende. Fällt der auf das Template zurück, steht
im Sweep trotzdem `degraded: false`, und es entsteht kein `llm_incidents.json`. Sweeps stehen in
derselben Run-Liste wie normale Läufe; der Warnbanner bleibt aus, obwohl das Narrativ nicht vom
Modell stammt. Auffindbar ist es nur an `"source": "template"` in `run_scenario.json` — also
genau die stille Degradation, gegen die P0.1 angetreten ist, nur auf dem Sweep-Pfad.

**Was zu tun ist:** `seed`, `mock_llm`, `deterministic_only`, einen Hash der geladenen Config-Dateien und den Codestand (Git-Commit, sofern verfügbar) in `run_metadata.json` schreiben. Die Ansicht «Ergebnisse ansehen» zeigt Seed und Rechenmodus im Überblick, damit ein Mock-Lauf nicht als echter Lauf präsentiert wird. Fällt mit P0.1 zusammen — der Degradations-Marker (`degraded`, Fallback-Zähler) gehört in dieselbe Datei und dieselbe Anzeige, also beides in einem Zug. **Dabei den Sweep-Pfad mitziehen:** Metadaten erst nach der Szenario-Erzeugung schreiben, `llm_error` als Vorfall aufnehmen und `save_llm_incidents` aufrufen — dieselbe Kette wie in `run_simulation._save_run_outputs`, die dort bereits richtig herum steht.

**Fertig wenn:** Aus `run_metadata.json` allein ist erkennbar, mit welchem Seed und in welchem Rechenmodus ein Lauf entstanden ist; ein Test hält die Felder fest. Ein Sweep gegen einen toten Endpunkt ist als degradiert markiert und hat ein `llm_incidents.json` — ebenfalls per Test.

**Umgesetzt am 2026-08-27.** `run_metadata.json` trägt jetzt `seed`, `compute_mode`, `mock_llm`, `deterministic_only`, `config_fingerprint` und `code_version`. Die Ansicht «Ergebnisse ansehen» zeigt Rechenmodus, Seed und Codestand im Tab «Übersicht»; ein Lauf ohne Sprachmodell trägt dort einen Hinweis, damit er nicht als vollwertiger durchgeht. Der Sweep-Pfad schreibt die Metadaten jetzt **nach** der Szenario-Erzeugung, nimmt den `llm_error` als Vorfall auf und ruft `save_llm_incidents` — dieselbe Kette wie `run_simulation._save_run_outputs`.

Vier Dinge, die dabei über den Plan hinausgingen:

- **Der Fingerabdruck hasht den Lauf, nicht die Dateien.** Der Plan sagte „Hash der geladenen Config-Dateien". Das wäre falsch gewesen: Ein Lauf aus dem Dashboard arbeitet mit einem Entwurf, der `configs/` gar nicht anfasst — ein Dateihash behauptete dort eine Gleichheit, die es nicht gibt. Gehasht werden die Konfigurationsobjekte aus dem `SimulationState`.
- **Und er wanderte zuerst.** Die erste Fassung lieferte für zwei Läufe derselben Konfiguration verschiedene Werte, weil die CIB-Matrix **während** des Laufs beschrieben wird (`consistency_score`, `scenarios`, `scenario_candidates`, `scenario_consistency`, `scenario_llm_payload` — fünf Schlüssel, von denen die erste Fassung zwei kannte). Diese Schlüssel stehen jetzt als benannte Menge im Code, **und ein Test liest alle Schreibzugriffe auf `cib_matrix.metadata[...]` aus `src/` und vergleicht sie damit**. Wer einen sechsten einführt, bekommt einen roten Test statt eines still wandernden Fingerabdrucks. Eine Aufzählung ohne Wächter wäre genau die Sorte Drift, die diese Phase abräumt.
- **Der Seed kommt aus dem State, nicht aus den Argumenten.** `args.seed` ist bei einem Multi-Run nur der Ausgangswert der Folge; der tatsächlich benutzte steht in `state.config.seed`. Nebenbei musste `_build_run_args` `mock_llm` mittragen — sonst wäre der Rechenmodus bei jedem Multi-Run-Teillauf verloren gegangen.
- **Der Sweep behauptete `deterministic_only`.** Er rechnet zwar deterministisch, erzeugt den Szenariotext am Ende aber mit `prefer_llm=True`. Das Artefakt hätte also gesagt, es sei kein Modell beteiligt gewesen — und ein Ausfall genau dieses Aufrufs wäre wieder unsichtbar geworden. Die Metadaten-Argumente liegen jetzt in `sweep_metadata_args()`, damit prüfbar ist, was sie behaupten; der Sweep-Seed stand zweimal als Literal und ist jetzt eine Konstante.

**Nachgestellt:** Zwei Läufe mit verschiedenen Seeds (1234, 9999) tragen denselben Fingerabdruck und verschiedene Seeds — genau die Trennung, für die er da ist.

**Doku zieht mit:** `docs/handbuch/ref-ausgaben.md`, `docs/handbuch/lauf-starten.md`, `README.md`.

### Gegenprobe zu P0.4–P0.6 (2026-08-27)

Jede Zusage der drei Pakete wurde einzeln im Code abgeschaltet, um zu sehen, ob ein Test das merkt — dasselbe mechanische Prüfmuster wie in der dritten Nachprüfung von P0.3. **36 Zusagen, im ersten Durchgang 29 gedeckt.** Alle sechs Lücken waren Testlücken, nicht Codefehler: Jede der sechs Zusagen wurde am laufenden System einzeln nachgestellt und hielt. Die Lücken sind geschlossen, der zweite Durchgang steht bei 36 von 36.

Was fehlte, hatte ein Muster — es war **jeweils der Weg zur Funktion, nicht die Funktion**:

- **Die Verdrahtung der Shift-Regeln.** Die Tests riefen `apply_factor_shifts` direkt und reichten Tick und Metriken selbst hinein. Man konnte `tick=current_tick` im Sampler durch `tick=0` ersetzen und `metrics=metrics` im Environment-Node durch `metrics=None` — kein Test wurde rot. Ausgerechnet die Kernzusage von P0.4 („eine `shift_rule` mit `at_least` oder `tick` greift jetzt") hing damit an ungeprüftem Draht. Nachgestellt: Eine `tick`-Regel greift genau in ihrem Tick, eine `cost_pressure`-Regel in jedem — beides jetzt als Test durch `EnvironmentNode`.
- **`once`.** P0.4 hat es aus dem Prädikat herausgezogen; dass die Aufrufer es weiterhin führen, prüfte niemand.
- **Der Protokolltext.** Dass `narrative.py` `describe_when` tatsächlich benutzt, war ungedeckt.
- **`mock_llm` in `_build_run_args`** und **die Dashboard-Anzeige der Herkunft** — Letzteres exakt dieselbe Lücke, die die dritte Nachprüfung von P0.3 für den Start-Callback gefunden hat.

**Zwei echte Befunde kamen dazu:**

- **Ein Mock-Lauf behauptete ein Modell.** Die Kachel «Modell» zeigte `llama3.2` neben «Rechenmodus: Ohne Sprachmodell» — der Modellname steht in den Argumenten, auch wenn nie gefragt wurde. Genau der Widerspruch, den P0.6 abstellen soll. Behoben: Ohne Sprachmodell steht dort «keins».
- **Fünf tote Modulpfade in der Doku**, zwei davon in **offenen** Findings (P5.1 und P4.2 zeigten auf das umbenannte `market_rules.py`; drei weitere Kapitel nannten `event_deltas`, `scenario_consistency` und `population_sampler` noch auf oberster Ebene, obwohl sie längst in ihren Paketen liegen). Behoben, und `tests/test_packaging.py` prüft jetzt jeden in Backticks genannten `src/…py`-Pfad gegen das Dateisystem. Ohne Ausnahmeliste: Ein früherer Modulname gehört in den Fließtext, nicht in eine Pfadangabe.

**Am laufenden System nachgestellt**, weil kein Test es erreicht: Ein Sweep gegen einen toten Endpunkt rechnet zu Ende, ist in `run_metadata.json` als `degraded: true` markiert, hat ein `llm_incidents.json` mit dem echten Verbindungsfehler, und das Dashboard zeigt den Warnbanner — das «Fertig wenn» von P0.6 wörtlich. Der Mock-Lauf zeigt Rechenmodus, Seed und Codestand im Tab «Übersicht». Ein Multi-Run gibt jedem Teillauf seinen eigenen Seed (77, 78) und den Rechenmodus mit.

**Ein Nebenbefund ging an P3.4:** `OllamaConfig` liest keine einzige Umgebungsvariable — `OLLAMA_BASE_URL` blieb beim Nachstellen wirkungslos.

### Zweite Gegenprobe zu P0.6 (Manu, 2026-08-27)

Haikos Gegenprobe oben hat 36 von 36 Zusagen geprüft und sechs Testlücken geschlossen. Diese
zweite Runde hat den Branch **am laufenden System** nachgestellt statt am Testobjekt — frisches
venv, echte Läufe, Artefakte aufgeschlagen. Mechanik war sauber (701 Tests, nur der bekannte
`marginal_cost_fraction` rot; `ruff` und `black` grün). **Drei Zusagen von P0.6 hielten
trotzdem nicht**, alle drei im selben Muster: geprüft war die Funktion, nicht der Weg dorthin.

**Zum Gegenprüfen, Haiko** — jeder Punkt nennt, wie er sich in einer Minute widerlegen ließe.

**1. Der Fingerabdruck hat den Lauf mitgehasht.** Zwei echte Läufe derselben Konfiguration mit
Seed 1 und Seed 2: vier Komponenten gleich, `factors` verschieden. `config_fingerprint` lief über
den **finalen** State, und `FactorState.current_state` ist Ergebnis, nicht Eingabe — dieselbe
Klasse Fehler, gegen die `RUN_PRODUCED_MATRIX_METADATA` bereits absichert, ein Feld daneben.
Damit beantwortete der Abdruck genau die Frage nicht mehr, für die er da ist.
*Der naheliegende Fix wäre falsch gewesen:* `current_state` einfach wegzulassen macht ihn blind
für den Faktor-Startzustand — und der ist eine Eingabe, jeder Sweep setzt ihn über
`FactorOverride.initial_state`. Behoben über den **Zeitpunkt**: `SimulationRunner.run` nimmt die
Momentaufnahme vor dem ersten Tick und legt sie in `state.config_fingerprint`
(neues Feld, `ConfigFingerprint`) ab; `save_run_metadata` liest sie von dort. Beim Fortsetzen aus
einem Checkpoint bleibt der ursprüngliche Abdruck stehen.
*Nachstellen:* zwei Läufe mit `--seed 1` und `--seed 2`, `config_fingerprint` in beiden
`run_metadata.json` vergleichen — muss identisch sein.

**2. `seed: null` bei jedem Standardlauf.** `configs/simulation_config.json` nennt keinen Seed,
also schrieb das Artefakt `null` und das Dashboard «nicht festgehalten». Gezogen wurde trotzdem
reproduzierbar: `environment_node` fiel still auf `42` zurück. Gemessen sind zwei Wiederholungen
ohne Seed **bitgleich** — während der Editor den Lauf «frei» nannte und abweichende
Wiederholungen versprach. Das «Fertig wenn» von P0.6 verlangt das Gegenteil, und die 42 war
nirgends benannt. Behoben: `DEFAULT_SEED` in `src/models/state_models.py` als einzige Quelle,
aufgelöst **einmal** in `SimulationRunner.run` und in den State geschrieben; `environment_node`
zeigt nur noch auf die Konstante, `run_launcher` liest den aufgelösten statt des angeforderten
Werts. Die beiden Oberflächentexte, die Nicht-Determinismus behaupteten, sind mitkorrigiert.
*Nachstellen:* `python -m src.run_simulation --mock-llm --rounds 3 --quiet`, dann
`run_metadata.json` — dort steht jetzt `"seed": 42`.

**3. Der Sweep tauschte eine Falschaussage gegen eine andere.** `sweep_metadata_args` setzte
`deterministic_only=False`, damit das Artefakt nicht behauptet, es sei kein Modell beteiligt
gewesen. Damit behauptete es die Gegenrichtung: Das Dashboard zeigte «Mit Sprachmodell» und
«Modell: dummy_for_sweeps» für einen Lauf, dessen Ticks mit
`RunnerOptions(deterministic_only=True)` gerechnet werden. Die Begründung trägt zudem nicht —
`degraded` leitet `save_run_metadata` allein aus den Vorfällen ab, der Ausfall des
Abschlusstextes bleibt also auch ohne gebeugten Rechenmodus sichtbar. Behoben mit einem vierten,
ehrlichen Modus `deterministic_with_llm_narrative` («Nur Zahlen, Abschlusstext vom Modell») und
dem Modellnamen aus `OllamaConfig` statt `dummy_for_sweeps`.

**Dazu eine Kleinigkeit:** `code_version()` war `@lru_cache`-gepuffert. Das Dashboard läuft als
ein Prozess über Stunden — Commit und `dirty` wären beim Prozessstart eingefroren, und jeder
spätere Lauf trüge den Codestand von damals. Cache entfernt.

**Was die Tests daraus gelernt haben.** Jeder Fix ist einzeln abgeschaltet worden, um zu sehen,
ob ein Test rot wird — Haikos Muster. Der erste Anlauf hat dabei **zwei eigene Testlücken**
aufgedeckt, beide lehrreich:

- Der Regressionstest zum Fingerabdruck verglich `final.config_fingerprint` beider Läufe direkt
  und blieb beim Abschalten grün: Ohne den Fix ist das Feld auf beiden Seiten `None`, und
  `None == None` hält. Er läuft jetzt über `save_run_metadata`, also über das Artefakt, das der
  Nutzer sieht.
- Der Kontrolltest fragte, ob sich ein Faktor gegenüber dem Startzustand bewegt hat — bei vier
  Ticks tut er das für Seed 1 nicht, und der Test darüber hätte nichts gezeigt. Worauf es
  ankommt, ist die Divergenz der **beiden** Läufe.

**Beim zweiten Durchgang kamen drei weitere Befunde dazu** — diesmal in P0.4 und P0.5, gefunden
durch Abtasten der Ränder statt durch Lesen:

- **`{"factor": "F1", "state": null}` blieb still wirkungslos.** Der Leerstring wurde abgewiesen,
  `null` nicht: `str(None)` ist `"None"` und damit wahrheitswertig, die Klausel kam durch
  `check_when` und wurde danach gegen den Zustand `"None"` verglichen. Dasselbe galt für jede
  Nicht-Zeichenkette. Genau die Klasse Fehler, gegen die P0.4 angetreten ist — im Prüfer selbst.
- **`{"tick": 3.7}` griff in Tick 3.** `rule_matches` vergleicht über `int(...)`, das die
  Nachkommastelle abschneidet; `check_when` prüfte nur, *dass* es eine Zahl ist. Ein Zahlendreher
  sah damit aus wie eine Regel, die eben woanders greift. Ein Tick ist ein Tick (Invariante 5).
  `3.0` bleibt zulässig — JSON kennt keinen eigenen Ganzzahltyp.
- **Ein fehlendes Profil schaltete Invariante 2 lautlos ab.** `config_loader` vergibt kein Profil,
  wenn `agent_profiles.json` fehlt oder den Agenten nicht kennt — und seit P0.5 heißt „kein
  Profil" *nichts erlaubt*. Nachgestellt: Datei weggeschoben, Lauf gestartet; er rechnet klaglos
  zu Ende, kein Agent kann noch einen Faktor vorschlagen, `collect_state_errors` meldet nichts.
  Vor P0.5 blieb derselbe Fall folgenlos, weil das hartcodierte Dict die Rechte trug — das ist
  der Preis der Vereinfachung, und er war nicht bezahlt. `validation.py` weist einen Agenten ohne
  Profil jetzt ab. Der Test, der das Gegenteil festschrieb (`test_an_agent_without_a_profile_is_fine`),
  war zum Zeitpunkt seiner Entstehung richtig und ist mit P0.5 falsch geworden; er ist umgedreht.
- **Zwei tote Anker im Plan selbst.** Die Verweise auf P0.5 und P0.6 zeigten noch auf die
  Überschriften ohne „✅ erledigt" und liefen ins Leere — dieselbe stille Doku-Drift wie die fünf
  toten Modulpfade der ersten Gegenprobe, eine Ebene höher. Behoben, und
  `tests/test_packaging.py` prüft jetzt jeden Anker innerhalb einer Datei gegen ihre
  Überschriften. Im ganzen Repo waren es genau diese zwei.

**Bewusst nicht angefasst**, beides gehört gemeldet statt still geändert:

- **`run_multi` hat einen anderen Standard.** `base_seed = base_state.config.seed or 0` ergibt
  ohne konfigurierten Seed die Folge 0, 1, 2 …, während ein Einzellauf jetzt 42 nimmt. Falsche
  Angaben entstehen dadurch keine — jeder Teillauf schreibt seinen eigenen Seed mit —, aber
  derselbe Aufbau rechnet je nach Pfad anders. Das anzugleichen verschiebt Zahlen und ist damit
  eine Modelländerung, kein Review-Fix.
- **`run_population_sampling`** reicht weiterhin weder `current_tick` noch `metrics` durch; eine
  `tick`-Regel wäre dort wirkungslos. Es ist der Rest genau des Bugs, den P0.4 abgeräumt hat —
  aber toter Code, der in `audit_findings.md` bereits zum Entfernen steht. Dort ergänzt.


---

### Dritte Runde: Manus Gegenprobe nachgeprüft (Haiko, 2026-08-27)

Manus vier Commits sind einzeln nachgestellt worden — jede Behauptung am laufenden System, nicht am Commit-Text. **Alle drei Befunde von P0.6 halten**, ebenso die zwei Randfälle in P0.4 und der fehlende-Profil-Fall in P0.5. Dazu ein Mutationslauf über **49 Zusagen** (meine 36 aus der ersten Runde, sechs davon an den geänderten Code angepasst, plus seine 13 neuen): **46 gedeckt.**

**Nachgestellt und bestätigt:**

- *Der Fingerabdruck hat den Lauf mitgehasht.* Seine Kopfzeile stimmt aufs Wort: Seeds 1 und 2 über vier Ticks mit aktivem CIB — vier Komponenten gleich, `factors` verschieden, weil F1 auseinanderläuft. (Mein erster Reproduktionsversuch mit abgeschaltetem CIB über 40 Ticks zeigte nichts, weil beide Läufe bis dahin wieder in derselben Endlage ankommen. Der Aufbau entscheidet, nicht der Befund.) Deutlicher noch ohne Seed-Unterschied: **dieselbe Konfiguration, derselbe Seed, nur 5 statt 40 Ticks** ergab am Ende `31e57fbb…` gegen `1b6de2d0…`, beim Start beidemal `31e57fbb…`.
- *Der Abdruck überlebt Checkpoint und Fortsetzen.* 30-Tick-Lauf mit Checkpoints: Der Startabdruck steht im Checkpoint, wird beim Fortsetzen nicht neu genommen, obwohl die Faktoren sich bewegt haben. Alte Checkpoints (ohne das Feld) laden weiterhin — sie bekommen beim Fortsetzen allerdings einen Abdruck aus bereits gelaufenem Zustand. Enger Randfall, gehört in die Zuständigkeit von [P3.2](#p32--checkpoint-version-wirklich-prüfen--erledigt-2026-09-05).
- *`seed: null` bei jedem Standardlauf.* Bestätigt und behoben: Ein Lauf ohne `--seed` schreibt jetzt `42`, und zwei solche Läufe sind in `price_history.json`, `tick_mechanics.json` und `factors.csv` **bitgleich** — die Reproduzierbarkeit war schon vorher da, nur sagte es niemand.
- *Der Sweep-Modus.* Ein Sweep gegen einen toten Endpunkt trägt jetzt `deterministic_with_llm_narrative`, den echten Modellnamen, `degraded: true` und ein `llm_incidents.json` mit dem Verbindungsfehler. Das «Fertig wenn» von P0.6 hält unverändert.
- *Beide Audit-Findings.* `run_multi` beginnt seine Folge tatsächlich bei 0 und 1, während ein Einzellauf 42 nimmt — gemessen. `run_population_sampling` reicht Tick und Metriken wirklich nicht durch. Beide zu Recht ins Audit statt in einen Fix.

**Drei Lücken, die der Mutationslauf fand — alle in den neuen Tests, keine im Code:**

- **Der Resume-Test bewies nichts.** `test_a_resumed_run_keeps_the_original` lief über vier Ticks, und bei vier Ticks steht kein Faktor anders als beim Start — ein Neuberechnen liefert dann zufällig dasselbe. Genau die Schwäche, die Manu eine Zeile weiter oben als `None == None`-Falle beschreibt, nur anders verkleidet. Der Test läuft jetzt über 16 Ticks (die Grenze, ab der sich Faktoren bewegen) und sichert diese Vorbedingung als eigene Zusicherung ab.
- **Die Prüfung des Seed-Rückfalls las nur den Quelltext.** Sie verlangt `DEFAULT_SEED` und verbietet `else 42` — ein `else 999` erfüllt beides. Daneben steht jetzt eine, die die gezogene Bevölkerung vergleicht.
- **Der Dashboard-Pfad war ungedeckt.** Neu: ein Lauf über `launch_simulation` ohne Seed muss `DEFAULT_SEED` ins Artefakt schreiben.

**Und eine Zeile, die keine Prüfung decken kann.** `run_launcher` liest den aufgelösten Seed statt des angeforderten — das ist richtig, heute aber **wirkungslos**: `save_run_metadata` bevorzugt ohnehin `state.config.seed` und greift auf den Argumentwert nur zurück, wenn dort keiner steht, was nach einem Runner-Lauf nicht vorkommt. Die Zeile bleibt (sie wird load-bearing, sobald jemand diese Reihenfolge umdreht), trägt aber jetzt einen Kommentar, der das sagt. Eine Zusage, die sich nicht widerlegen lässt, als "gedeckt" zu zählen, wäre genau die Art Buchführung, die diese Runden abschaffen sollen.

---

### P0.7 — Kostendruck aus einer Quelle ✅ erledigt 2026-08-27

**Befund (neu am 2026-08-27, gefunden bei der Umsetzung von P0.4):** `compute_cost_pressure` wird an zwei Stellen gerufen, aber nur eine übergibt `factors` und `system_properties`. [`environment_node.py:101`](../src/orchestration/environment_node.py) übergibt **keins von beiden** — dort kann deshalb kein einziger regulatorischer Kostentreiber aktiv werden, weil ~~alle fünf ausgelieferten an einer `factor`-Bedingung hängen~~ — **berichtigt bei der Umsetzung:** es sind sechs, und einer davon gilt unbedingt; blind war der Pfad für die fünf **bedingten** (siehe «Was am Befund nicht stimmte» unten). [`simulation_functions.py:359`](../src/market/simulation_functions.py) übergibt sie korrekt.

**Gemessen:** Bei F2.2 (strenge Regulierung) liefert der Environment-Pfad 103.06, der Market-Pfad 108.06 — die 5.00 des EU-ETS. Der Environment-Wert landet als `cost_pressure` in `state.market_metrics` und ist genau die Größe, gegen die `f4_high_cost_pressure` (> 135) und `f4_stable_growth` (< 115) schwellen. ~~**Die F4-Übergänge urteilen also über einen Kostendruck ohne Regulierungskosten, während die Kundschaft den vollen Preis zahlt.**~~ — **widerlegt bei der Umsetzung:** Der Market-Node überschreibt den Wert im selben Tick, bevor die Faktor-Regeln ihn im nächsten lesen. Der Satz galt nur mit `--no-market`. Gewirkt hat der Fehler über den Startpreis, nicht über die F4-Schwellen (dritte Korrektur unten).

**Was zu tun ist:** Den Environment-Pfad die Faktoren und Systemgrößen mitgeben lassen, die er ohnehin zur Hand hat (`state.environment.factors`, `resolve_system_properties(round_number, properties)` steht dort neun Zeilen später). Danach prüfen, ob der Parameter überhaupt optional bleiben darf — ein Default, der still ein anderes Ergebnis liefert, ist dieselbe Klasse Problem.

**Was das kostet — vor der Umsetzung geschätzt:** Der Kostendruck steigt in Läufen mit strenger Regulierung, und damit ändern sich Faktorverläufe. Das ist eine **Modelländerung**, kein Refactoring — deshalb wurde der Fund in P0.4 bewusst nicht mitbehoben. ~~F4 kippt früher, Konsistenzwerte und die drei erzeugten Szenarien ändern sich; die Kennzahlen aus P0.2 (BAU 0.970, Konflikt 0.867, Wende 0.629) sind neu zu erheben, `test_cib_ranking.py` mitzuziehen.~~ — **gemessen widerlegt:** F4 bewegt sich nicht, Konsistenzwerte und Endlagen bleiben gleich, und der Test rechnet keinen Lauf. Was sich wirklich verschiebt, steht in der Tabelle unten. Die Schätzung war zu grob **und in die falsche Richtung** — sie nannte die Größe, die sich nicht bewegt, und übersah die, die sich stark bewegt.

**Fertig wenn:** Beide Aufrufstellen liefern für denselben Zustand denselben Kostendruck, und ein Test hält das fest. ~~Und die verschobenen Kennzahlen sind in `docs/cib_role.md` und `test_cib_ranking.py` nachgezogen.~~ — **hinfällig, siehe die vierte Korrektur unten:** Der Test bewertet fest verdrahtete Faktorzustände gegen die eingefrorene Matrix, er rechnet keinen Lauf; ein geänderter Kostendruck kann seine Zahlen nicht bewegen, und in `docs/cib_role.md` steht nichts zum Kostendruck. Das Kriterium stand hier, weil bei seiner Formulierung noch nicht geprüft war, woher der Test seine Eingaben nimmt. Durchgestrichen statt gelöscht, damit nachvollziehbar bleibt, dass es nicht übergangen, sondern widerlegt wurde.

**Umgesetzt am 2026-08-27 — und dabei drei Aussagen dieses Pakets korrigiert.** `factors` und `system_properties` sind an `compute_cost_pressure` **und** `compute_market_metrics` jetzt Pflichtparameter; wer wirklich keine hat, sagt das mit `factors={}`. Das beantwortet die Frage aus «Was zu tun ist» mit Ja: Ein Default, der still ein anderes Ergebnis liefert, ist die Falle selbst, und ein vierter blinder Aufrufer kann so nicht mehr entstehen.

**Was am Befund nicht stimmte:**

1. **Es sind sechs Kostentreiber, nicht fünf** — und einer, `airport_infrastructure_levy` (3.00), hat ein **leeres `when`** und gilt immer. Der alte Pfad war also nicht blind für alle, sondern für alle **bedingten**. Wer die Zahlen nachrechnet, braucht diese Unterscheidung: Der Environment-Wert war 103.06, nicht 100.06.
2. **Die Lücke ist größer als gemessen.** Der Plan nannte 5.00 (EU-ETS bei F2.2). Tatsächlich stapeln sich die Treiber je nach Lage: F2.1+F4.1 → **+8.00**, F2.2+F4.1 → +5.00, F2.2+F4.2 → +11.00, F2.1+F4.2 → **+14.00**. Der Environment-Pfad lieferte für **jede** Faktorlage denselben Wert.
3. **Der Mechanismus war falsch beschrieben.** Der Satz «Die F4-Übergänge urteilen über einen Kostendruck ohne Regulierungskosten» trifft im Standardbetrieb **nicht** zu. Reihenfolge im Tick: Faktor-Regeln → Agenten → Environment → Consumer → Markt. Der Environment-Node schreibt seinen Kostendruck nach `state.market_metrics`, **der Market-Node überschreibt ihn im selben Tick**, und erst im nächsten Tick lesen die Faktor-Regeln. Sie sahen also immer den korrekt gerechneten Wert des Market-Knotens. Nur mit `--no-market` überlebt der Environment-Wert bis dorthin — dann, und nur dann, galt der Satz.

**Ein zweiter blinder Aufrufer, der nicht im Plan stand:** [`agent_node.py:335`](../src/agents/agent_node.py) ruft `compute_market_metrics` für die Vorschau im Agenten-Prompt — ebenfalls ohne Faktoren. Dieser Zweig greift, wenn `state.market_metrics` leer ist, also im **ersten Tick jedes Laufs**, weil die Agenten vor dem Environment-Node laufen. Gemessen bei F2.2+F4.2: Dem Agenten wurde `cost_pressure: 103.56` gezeigt, während die Simulation mit 114.56 rechnete. Das greift Invariante 1 an einer unerwarteten Stelle an — die Zahlen kamen aus Python, aber es waren zwei verschiedene.

**Wie der Fehler tatsächlich wirkte:** über den Preis, nicht über die Faktor-Regeln. Im ersten Tick ist `price_history` leer, und der Environment-Node bildet aus seinem Kostendruck den `provisional_price` — genau den Preis, den die Bevölkerung in Tick 1 sieht. Der zu niedrige Startpreis zog über die Preisrückkopplung den ganzen Verlauf mit.

**Was sich verschoben hat — gemessen, vorher/nachher mit demselben Skript:**

| | vorher | nachher |
| --- | --- | --- |
| Ticketpreis am Ende, BAU (40 Ticks) | 134.39 | **131.13** |
| Ticketpreis am Ende, Freiwillige Wende | 73.25 | **73.08** |
| Ticketpreis am Ende, Transformationskonflikt | 65.20 | **65.31** |
| Ticketpreis am Ende, Standardlauf | 89.54 | **89.32** |
| Faktorverlauf Standardlauf | F1 kippt später | **F1 kippt in Tick 4** |
| Faktor-**Endlagen** aller drei Archetypen | — | **unverändert** |
| Konsistenzwerte aller drei Archetypen | — | **unverändert** |

**Der Verlaufssprung ist der eigentliche Preis dieses Pakets, nicht die
Preisdifferenz.** Unabhängig nachgemessen (15 Ticks, deterministisch, Seed 42):
F1 kippt vorher in Tick 15, nachher in **Tick 4** — statt einem verbringt der
Lauf **zwölf von fünfzehn** Ticks in F1.2. Die Zeile «Endlagen unverändert»
darüber stimmt und kann trotzdem in die Irre führen: Ein Szenarienprodukt
verkauft Verläufe, nicht Endzustände. Wer Läufe von vor und nach diesem Commit
nebeneinanderlegt, vergleicht zwei Modelle.

Erkennbar ist das an `code_version` in `run_metadata.json` — deshalb steht es
dort seit P0.6. Gesagt werden muss es trotzdem: `docs/handbuch/vergleiche.md`
nennt den Schnitt jetzt beim Namen.

**Und damit auch die vierte Korrektur:** «Die Kennzahlen aus P0.2 sind neu zu erheben, `test_cib_ranking.py` mitzuziehen» war nicht nötig. Der Test bewertet **fest verdrahtete** Faktorzustände gegen die eingefrorene Matrix — er rechnet keinen Lauf. Ein geänderter Kostendruck kann seine Zahlen gar nicht bewegen. Auch `docs/cib_role.md` blieb unberührt: Dort steht nichts zum Kostendruck.

**Dabei aufgefallen, als eigenes Finding ins Audit:** Zwei der drei Zustandsmengen in `test_cib_ranking.py` heißen `*_END_STATES`, werden aber von den gleichnamigen Sweeps **nicht erreicht** — schon vor diesem Paket nicht. Ein Sweep `business_as_usual` endet bei F1.2/F4.2, die Konstante sagt F1.1/F4.1.

**Doku zieht mit:** `docs/handbuch/preisbildung.md`, `CLAUDE.md` (Invariante 1 um die eine Quelle des Kostendrucks ergänzt).

---

### Vierte Runde: Phase 0 als Ganzes geprüft (2026-08-27)

Die drei Runden davor haben je ein Paket oder eine Handvoll geprüft. Diese Runde hat **Phase 0 im Ganzen** gegen den Codestand gehalten: alle sieben Pakete, jedes «Fertig wenn» einzeln, dazu die Doku, die laut den Paketen mitziehen sollte. **Im Code hält alles** — die sieben Pakete lösen ihre Zusagen mechanisch ein (`rule_engine` als einzige Auswertung mit fünf Importeuren und keinem Rest der drei alten Evaluatoren; `may_propose_factor` mit genau zwei Aufrufern; `factors`/`system_properties` keyword-only **ohne** Default, womit ein vierter blinder Aufrufer baulich unmöglich ist; ein echter Lauf schreibt `seed: 42`, `compute_mode`, Fingerabdruck und Codestand). Suite: 749 grün, rot nur der bekannte `marginal_cost_fraction` aus P4.2.

**Fünf Lücken, alle auf der Doku-Seite** — und vier davon Varianten desselben Musters, das schon die erste Gegenprobe beschreibt: *geprüft war die Funktion, nicht der Weg dorthin.*

1. **Drei behobene Findings standen noch in `audit_findings.md`** — der Kostendruck (P0.7), der Sweep-Pfad und die fehlenden Reproduzierbarkeits-Felder (beide P0.6) —, obwohl die [Abdeckungstabelle](#abdeckung-des-audits) alle drei bereits mit ✅ führte. Das Kostendruck-Finding trug dabei die drei Aussagen weiter, die P0.7 bei der Umsetzung ausdrücklich widerlegt hat (fünf statt sechs Kostentreiber, konstante 5.00 statt +5.00…+14.00, und der Satz über die F4-Übergänge, der im Standardbetrieb nicht zutrifft). Entfernt. Die Pflegeregel im Audit nennt jetzt die Abdeckungstabelle als Gegencheck.
2. **Die Backlog-Zeile in `CLAUDE.md` war stehengeblieben.** Sie führte P0.4, P0.5 und P0.6 ohne ✅ als offen, kannte P0.7 gar nicht und sprach von „den **zwei** auseinandergelaufenen Rule-Evaluatoren" — obwohl P0.4 als eigene Ergänzung festgehalten hat, dass es drei sind. Wer nur `CLAUDE.md` las, hielt Phase 0 für halb offen. Nachgezogen.
3. **`run_metadata.json` behauptete für einen Mock-Lauf weiterhin ein Modell.** Gemessen: `"model": "llama3.2"`, dazu `base_url`, `temperature`, `max_tokens` — neben `"compute_mode": "mock_llm"`. Die **erste** Gegenprobe hat genau diesen Widerspruch gefunden und als behoben gemeldet; behoben war er aber nur in `views/overview.py::_model_label`, also in einer einzigen Oberflächenkachel. Die Zusage von P0.6 lautet «aus `run_metadata.json` **allein**» — wer die Datei ohne Dashboard las, bekam vier Angaben über ein Modell, das nie gefragt wurde. Die vier Felder stehen bei `mock_llm` und `deterministic_only` jetzt auf `null`; die Schlüssel bleiben, damit das Schema gleich bleibt und ein *fehlender* Schlüssel weiterhin nur eines heißen kann: älter als P0.6. Ein Sweep behält seinen Modellnamen — dort schreibt das Modell den Abschlusstext. Vier neue Tests, mutationsgeprüft.
4. **Die Seed-Korrektur der zweiten Gegenprobe hatte das Handbuch nicht erreicht.** Sie vermerkt „Die beiden Oberflächentexte … sind mitkorrigiert" — drei Handbuchtexte behaupteten weiter Nicht-Determinismus: `glossar.md` («Fest gesetzt, ist ein Lauf reproduzierbar»), `kaufentscheidung.md` und, am deutlichsten, `lauf-konfigurieren.md` («Ohne ihn unterscheiden sich die Läufe schon dadurch, dass eine andere Bevölkerung gezogen wurde»). Alle drei nachgezogen. **Dabei bestätigt, nicht angeglichen:** `fragestellungen.md` rät bei Wiederholungen zum freien Startwert und verspricht verschieden gezogene Bevölkerungen — das stimmt, weil `run_multi` seine Folge bei 0 beginnt. Es ist genau die Pfadabhängigkeit, die als Finding im Audit steht; der Text ist für seinen Fall richtig und bleibt.
5. **Das «Fertig wenn» von P0.7 verlangte, was das Paket selbst widerlegt hat.** Durchgestrichen statt gelöscht, mit Begründung — siehe oben.

**Was daraus als Prüfmuster bleibt.** Die erste Gegenprobe hat für tote Modulpfade und Anker einen Wächter gebaut (`tests/test_packaging.py`). Punkt 1 und 2 sind dieselbe Drift eine Ebene höher — zwischen Plan, Audit und `CLAUDE.md` —, und dort greift kein Wächter. Bis [P4.3](#p43--doku-zahlen-mechanisch-halten--erledigt-2026-09-11) das mechanisch macht, gilt die Handregel: **Wer ein Paket auf ✅ setzt, geht im selben Zug durch `audit_findings.md` und die Backlog-Liste in `CLAUDE.md`.** Und Punkt 3 wiederholt die Lehre der ersten Runde wörtlich — eine Zusage über ein *Artefakt* ist nicht geprüft, solange nur die *Anzeige* geprüft ist.

### Fünfte Runde: P0.7 gegengeprüft (Manu, 2026-08-27)

Der Fix selbst hält — unabhängig nachgemessen und mutationsgeprüft. Bestätigt: die
Node-Reihenfolge (`market_node` überschreibt `state.market_metrics`, die Faktor-Regeln lesen erst
im nächsten Tick), der dritte blinde Aufrufer in `agent_node`, und der `*_END_STATES`-Befund (BAU
endet bei F1.2/F4.2, `freiwillige_wende` weicht bei F4/F6 ab, `transformation_conflict` passt).
Der Fix in beiden Aufrufern neutralisiert macht **acht** parametrisierte Tests über vier
Faktorlagen rot — die Zusagen sind gedeckt.

**Ein Geschwister des Musters war übrig.** P0.7 hat die stillen Defaults auf der Marktseite
abgeräumt; auf der Bevölkerungsseite standen sie noch: `apply_factor_shifts(tick=0, metrics=None)`
und `run_population_tick(current_tick=0, metrics=None)`. `tick=0` heißt "es gibt keinen Tick" —
ein vergessenes Argument hätte jede `tick`- und `metric`-Regel wieder still abgeschaltet, also
genau den Zustand hergestellt, den P0.4 beseitigt hat. Beide sind jetzt Pflicht.

**Und weil das nicht die letzte war, ist die Regel jetzt ein Test statt eines Vorsatzes.** Die
Suche nach Geschwistern über das ganze Paket fand vier weitere: `compose_ticket_price(tick=0)`
und `apply_market_feedback(tick=0)` (dazu je ein `properties=None`, das Steuern und Gebühren ganz
wegfallen ließ) sowie `initial_provider_markup(tick=0)` und `initial_ticket_price(tick=0)`. Der
Markup-Fall ist der lehrreichste: **alle sechs** Aufrufer nahmen den Default, und es ist heute
folgenlos — weil `provider_markup` im ausgelieferten Config eine flache Baseline ist. Gibt ihr
jemand im Editor eine Stufenfunktion, wird die Zahl still falsch. Ein Fehler, der auf einen
Konfigurationswert wartet, ist keiner, den man findet; er ist einer, den man ausschließt.

`TestKeinKontextparameterHatEinenDefault` prüft jetzt **acht** Funktionen auf «kein Default,
keyword-only», und ein Sweep über `src/` findet keinen Kontextparameter mit Default mehr. Wer
eine neunte Funktion mit Tick-Kontext baut, trägt sie dort ein. Das ist die eigentliche Lehre aus
P0.7: Der Befund war nie «diese eine Funktion», sondern «ein Kontextparameter mit Default liefert
still eine andere Zahl».

**Alle diese Änderungen sind rein strukturell.** Nachgewiesen, nicht angenommen: Derselbe
deterministische Lauf liefert vor und nach ihnen bitgleiche Preise, Kostendrücke, Faktorverläufe
und Endlagen. Die Aufrufer übergaben die Werte bereits — neu ist nur, dass sie es müssen.

**Drei Doku-Befunde, alle behoben:**

1. **Der Verlaufssprung war zu leise benannt.** Die Tabelle betont «Endlagen unverändert» — was
   stimmt. Gemessen kippt F1 aber in Tick 4 statt Tick 15, also zwölf statt einem von fünfzehn
   Ticks in F1.2. Ein Szenarienprodukt verkauft Verläufe, nicht Endzustände; wer Läufe über
   diesen Commit hinweg vergleicht, vergleicht zwei Modelle. Steht jetzt in der Tabelle und als
   eigener Abschnitt in `docs/handbuch/vergleiche.md`, samt dem Hinweis, dass `code_version` den
   Schnitt erkennbar macht.
2. **Drei widerlegte Aussagen standen unmarkiert über ihren Korrekturen** — der Befundsatz über
   die fünf Kostentreiber, der fett gesetzte F4-Satz und die Forderung, `test_cib_ranking.py`
   nachzuziehen. Beim «Fertig wenn» war das Durchstreichen-mit-Begründung schon angewandt, bei
   diesen dreien nicht; wer den Abschnitt von oben las, bekam erst die falschen Aussagen. Jetzt
   nach demselben Muster markiert. **Dabei aufgefallen:** Die Vorab-Schätzung lag nicht nur zu
   grob, sondern in der falschen Richtung — sie nannte F4, das sich nicht bewegt, und übersah F1,
   das sich stark bewegt.
3. **`vergleiche.md` empfahl eine Methode, die ins Leere laufen konnte.** «Rechnen Sie denselben
   Aufbau mehrfach mit freiem Zufallsstartwert», ohne das Feld **Wiederholungen** zu nennen. Wer
   stattdessen denselben Einzellauf zweimal startet, misst seit der Seed-Korrektur Streuung null
   und hält danach jeden Unterschied für belastbar. In `lauf-konfigurieren.md` war die
   Unterscheidung schon richtig getroffen, hier fehlte sie.

**Und eine Entscheidung ist gefallen: `run_multi` ist angeglichen.** Die Pfadabhängigkeit —
Wiederholungen begannen ihre Seed-Folge bei 0, ein Einzellauf rechnete mit `DEFAULT_SEED` —
stand als Finding im Audit und trug zugleich eine **dokumentierte Arbeitsweise**: Die
Streuungsmessung in `fragestellungen.md` und `vergleiche.md` beruht auf ihr. Ein Finding, auf dem
eine Produktzusage ruht, gehört entschieden statt verwaltet; entschieden wurde für Angleichen.

**Die Sorge dabei war unbegründet, und das ist der eigentliche Ertrag der Prüfung.** Die Frage
lautete, ob `run_multi` ohne die Abweichung eine andere Quelle für Vielfalt braucht. Sie braucht
keine: Die Wiederholungen unterscheiden sich durch `base_seed + index`, nicht durch den fehlenden
Seed. Das Angleichen kostet also nichts und bringt eine Eigenschaft ein, die vorher fehlte — die
**erste Wiederholung ist jetzt derselbe Lauf wie ein Einzellauf**, statt ein vierter, unerklärter
Fall zu sein. `or 0` ist dabei zu `is None` geworden: Ein ausdrücklich gesetzter Seed 0 ist eine
Angabe, kein fehlender Wert.

**Was das sichtbar verschiebt:** Wiederholungen ohne eigenen Startwert rechnen jetzt mit
42, 43, 44 … statt 0, 1, 2 … — andere Zahlen, dieselbe Methode. Die Aussagen, die jemand aus der
Streuung älterer Wiederholungen gezogen hat, bleiben gültig; ihre Einzelwerte nicht.
`docs/handbuch/vergleiche.md` nennt den Schnitt neben dem aus P0.7.

**Dabei aufgefallen:** `run_multi` hatte **keinen einzigen Test** — eine Funktion, auf der zwei
Handbuchkapitel eine Methode aufbauen. `tests/test_run_multi_seeds.py` deckt jetzt den Startwert
der Folge, den Vorrang eines gesetzten Seeds, die ausdrückliche 0, übergebene Seed-Listen, die
Verschiedenheit der Wiederholungen und den Seed jedes Teillaufs im Artefakt ab. Drei davon
werden rot, wenn man `or 0` zurückschreibt.

**Zwei eigene Fehlgriffe, protokolliert** — beide von den Wächtern aus der zweiten Runde gefangen,
nicht von Aufmerksamkeit: Das Skript, das die Testaufrufe auf die neuen Pflichtparameter
umgestellt hat, hielt einen **Docstring** für einen Aufruf und schrieb Argumente in Prosa; und der
erste Anlauf für diesen Abschnitt hat ihn gar nicht geschrieben (zwei `write_text` nacheinander,
das zweite verwarf das erste), sodass die Stand-Zeile auf eine Überschrift zeigte, die es nicht
gab. Ersteres fällt beim Diff-Lesen auf, Letzteres hat `test_internal_doc_anchors_point_somewhere`
gemeldet. Wer Dateien skriptgesteuert ändert, liest den Diff und lässt die Wächter laufen.

---

### Sechste Runde: die Verallgemeinerung gegengeprüft (Haiko, 2026-08-28)

Manus drei Commits sind einzeln nachgestellt worden. **Die tragenden Behauptungen halten, und zwar die schwersten zuerst:** Der Bitgleichheits-Nachweis der Pflichtparameter stimmt — derselbe Lauf (15 Ticks, Seed 42) liefert über ein Worktree beidseitig identische `price_history.json`, `tick_mechanics.json` und alle drei Zeitreihen. Die Verlaufsmessung stimmt auf den Tick: F1 kippt vor P0.7 in Tick 15, danach in Tick 4, zwölf statt einem von fünfzehn Ticks in F1.2. `run_multi` rechnet gemessen mit 42/43/44, die erste Wiederholung ist bis auf sechs Nachkommastellen derselbe Lauf wie ein Einzellauf, und die Angabe „drei Tests werden rot" ist exakt — es sind genau drei.

**Zwei Befunde, beide an derselben Stelle der Argumentation.**

1. **Der Sweep hatte zwei Geschwisterfälle übersehen — in der Datei, die derselbe Commit anfasste.** [`evaluate_booking`](../src/population/population_sampler.py) und `aggregate_population_stats` trugen `properties=None`. Ohne Angabe traten `0.6` und `1.0` an die Stelle von `saturation.booking_increase` und `saturation.utility_penalty_factor` — **genau der Fall, den der Commit selbst „den lehrreichsten" nennt**: heute folgenlos, weil die ausgelieferte Config zufällig dieselben Zahlen trägt, aber beide Felder haben eine eigene Bedienung im Config-Editor. Nachgestellt mit 0.25/2.0: Die Sättigungssumme läuft auf 195.25 gegen 468.60 auseinander, ohne Fehler und ohne Meldung, und sie trägt in die Buchungsentscheidungen des nächsten Ticks. Beide sind jetzt Pflicht; `None` bleibt zulässig, ist aber eine Aussage. Die Umstellung ist wieder rein strukturell — bitgleich geprüft wie die Vorlage.

2. **Der Wächter konnte diese Klasse gar nicht finden.** `TestKeinKontextparameterHatEinenDefault` ist eine handgepflegte Liste. Sie fängt einen **Rückfall** auf bekannten Stellen, nie einen **übersehenen** Fall — Befund 1 ist der Beleg. Der Commit stellte den Sweep sprachlich neben den Wächter („die Regel ist ein Test statt eines Vorsatzes … ein Sweep über `src/` findet danach keinen mehr"), aber der Sweep war einmalig und von Hand. Er ist jetzt selbst ein Test: `TestKeinKontextparameterEntgehtDemSweep` läuft über den AST jeder Datei in `src/`. Mutationsgeprüft mit einer frisch angelegten Funktion `(*, tick: int = 0)`, die in keiner Liste steht — der Sweep meldet sie von sich aus. Die Liste bleibt als ausdrücklicher Anker für die Stellen, an denen der Fehler tatsächlich auftrat, und steht bei zehn.

   **Die drei verbliebenen Defaults sind Ausnahmen mit Namen und Grund**, nicht Übersehenes: `mark_spoken`, `allowed_factor_targets` und `run_population_sampling` leiten ihren Rückfall aus lebendem Zustand ab (eigenes Feld, `state.resolved_properties()`, die geladene Config) statt aus einer erfundenen Konstante — sie können gar nicht anders rechnen als ihr Aufrufer. Ein zweiter Test hält fest, dass keine Ausnahme verwaist: eine für eine Stelle, die es nicht mehr gibt, verdeckt beim nächsten Mal eine echte.

   Nebenbei hat genau dieser Test einen Fehler in seiner eigenen ersten Fassung gefunden — `round_number` fehlte in der Namensmenge, wodurch die `mark_spoken`-Ausnahme ins Leere zeigte. In diesem Repo ist `round_number` ein Tick unter anderem Namen; der Environment-Node reicht ihn direkt als `tick` weiter.

**Zwei veraltete Zahlen mitgezogen:** Der Docstring des Wächters sprach von „allen vier Stellen … ein fünftes Mal", `CLAUDE.md` Invariante 1 ebenso — beide entstanden, als die Liste vier Einträge hatte, und wuchsen im selben Commit auf acht. Dieselbe Klasse wie die toten Modulpfade der ersten Runde, nur mit Zahlen. Bis [P4.3](#p43--doku-zahlen-mechanisch-halten--erledigt-2026-09-11) greift, ist die Handregel: **Wer eine Aufzählung erweitert, sucht ihre Anzahl im Fließtext.**

**Eine Zeile, die noch fehlt und nicht der Review gehört:** Die Angleichung von `run_multi` ist eine Modelländerung — das Audit hatte sie ausdrücklich als „kein Review-Fix" geführt. Die Begründung trägt und ist nachgerechnet, aber der Plan schreibt „entschieden wurde für Angleichen" im Passiv, während das Haus sonst zuschreibt (P0.2, P0.4). Wer sie getroffen hat, gehört dazu.

---

## Phase 1 — Funktionalität und UI ✅ abgeschlossen 2026-08-30 (offen: die Rechtstexte)

### P1.1 — "Simulation starten" neu bauen ✅ erledigt 2026-08-28

**Befund (korrigiert am 2026-08-26):** Der Start-Flow ist UX-seitig der schwächste Teil des Dashboards. Wer zum ersten Mal einen Lauf startet, versteht nicht, was er einstellt. Der Config-Editor ist mit rund 1.700 Zeilen über sechs Tabs zu tief, die Presets aus `configs/sweeps/` stehen nicht vorn, und die Erklärtexte in `config_editor/glossary.py` (401 Zeilen) stehen nicht dort, wo entschieden wird.

**Was hier nicht mehr gilt:** Die ursprüngliche Fassung nannte einen "blockierenden Wartezustand". Den gibt es nicht mehr — [`dashboard/web/runner.py`](../dashboard/web/runner.py) fährt den Lauf in einem Worker-Thread mit Queue, und [`pages/launch.py:37,147-182`](../dashboard/web/pages/launch.py) holt die Fortschrittszeilen per `dcc.Interval` ab. Fortschrittsanzeige ist erledigt und kein Teil dieses Pakets mehr.

**Fundstelle (Stand des Befunds, 2026-08-26):** [`dashboard/web/pages/launch.py`](../dashboard/web/pages/launch.py), `dashboard/web/config_editor/save_start.py`, [`dashboard/web/runner.py`](../dashboard/web/runner.py), die sechs Editor-Tabs in [`dashboard/web/config_editor/`](../dashboard/web/config_editor/). **`save_start.py` gibt es nicht mehr** — das Modul ist mit `5c6cf7e` entfallen, Sichern und Starten liegen seit P1.7 in [`wizard.py`](../dashboard/web/config_editor/wizard.py) und [`config_editor/__init__.py`](../dashboard/web/config_editor/__init__.py); aus den sechs Tabs sind mit P2.0-C sechs **Schritte** geworden. Der Verweis stand hier als toter Link, bis ihn am 2026-09-05 eine Ankerprobe über 491 Überschriften gefunden hat. **Der Dateiname bleibt als Name stehen und nicht als Link:** Eine Fundstelle beschreibt den Zustand *bei der Aufnahme des Befunds* — sie nachträglich auf das heutige Modul umzubiegen machte die Befundgeschichte unlesbar.

**Was zu tun ist:** Den Weg von "Preset wählen" bis "Lauf läuft" auf einen geführten Ablauf reduzieren. Presets nach vorn (`configs/sweeps/`), Expertenparameter dahinter. Erklärtexte aus `config_editor/glossary.py` dort zeigen, wo entschieden wird, nicht in einem eigenen Tab. Fehlermeldungen aus P0.3 direkt am Feld. Seed und Rechenmodus aus P0.6 sichtbar machen, damit vor dem Start klar ist, ob ein echter oder ein Mock-Lauf entsteht.

**Fertig wenn:** Jemand ohne Vorwissen startet einen sinnvollen Lauf ohne Rückfragen, und `test_web_layout.py` deckt den neuen Flow ab. **Messbar gemacht (2026-08-26):** Der geführte Ablauf braucht bis zum Start höchstens drei Entscheidungen, jede davon mit ihrem Erklärtext an Ort und Stelle. Dieses Kriterium ist zugleich das Tor für P5.2 und Phase 6 — siehe dort.

**Umgesetzt am 2026-08-28.** Vorn steht `dashboard/web/config_editor/start_flow.py` mit drei Entscheidungen — was gerechnet wird (Preset-Karten mit Beschreibung und Begründung), wie weit, womit —, darunter Preflight und Start; der Editor rutscht zugeklappt dahinter. Aus sechs Tabs werden vier: «Überblick» und «Kontrolle» gehen im geführten Block auf, «Als Szenario sichern» und die Rohdaten wandern nach «Lauf & Ablage». Die Erklärtexte aus `glossary.py` stehen im geführten Ablauf aufklappbar am Feld statt nur auf der Dokumentationsseite; Seed und Rechenmodus stehen im Preflight, bevor jemand startet.

**Das Abnahmekriterium ist eine Zusicherung, keine Absichtserklärung.** `tests/test_web_start_flow.py` läuft über den gerenderten Komponentenbaum, überspringt jeden `html.Details`-Teilbaum (also alles hinter «Feinabstimmung») und zählt die verbleibenden Felder — höchstens drei, und zwar diese drei. Ein Kontrolltest mit einem vierten Feld zeigt, dass der Zähler zählt, statt immer drei zu finden. Derselbe Durchlauf prüft die zweite tragende Zusage: **kein Feld steht doppelt.** Der geführte Block und der aktive Tab liegen gleichzeitig im DOM, und eine doppelt vergebene Dash-ID ist ein Laufzeitfehler im Browser — ohne Test fiele er erst dem auf, der die Seite öffnet.

**Der eigentliche Fund liegt tiefer als die Oberfläche: ein gewähltes Preset griff gar nicht.** `prepare_simulation_state` wandte erst das Preset an und legte danach den Entwurf darüber; weil `apply_custom_overrides` per Default an ist und der Entwurf die Defaults aus `properties.json` mitführt, drehte die zweite Runde die erste still zurück. Über die CLI (`run_single_sweep`) stimmte es, nur der Dashboard-Pfad nicht. **Betroffen waren alle acht ausgelieferten Presets** — je nach Preset zwischen zwei und zehn Systemgrößen, bei `alles_drin_szenario` zusätzlich alle sieben Faktoren. Am deutlichsten bei `business_as_usual`: Das Szenario verspricht eine konstante CO₂-Abgabe von 50 und trägt dazu einen eigenen Meilenstein («Kein CO₂-Anstieg bei Tick 15»); über das Dashboard sprang die Abgabe in Tick 15 auf 120 und in Tick 30 auf 200, womit F2 auf strenge Regulierung kippte — das Gegenteil dessen, wofür das Szenario steht. Presets nach vorn zu holen, während sie stillschweigend überschrieben werden, wäre ein Versprechen ohne Deckung gewesen; der Fund ist deshalb in diesem Paket behoben und nicht in `audit_findings.md` gewandert.

**Die erste Messung dazu war zu schmal.** Sie verglich drei Systemgrößen über drei Presets und meldete «zwei von drei betroffen, `freiwillige_wende` unverändert». Erst der vollständige Abgleich — alle Systemgrößen, alle Faktoren, alle acht Dateien — zeigte, dass keines unberührt blieb. Als Prüfmuster mitnehmen: Eine Stichprobe sagt, **dass** ein Fehler existiert, nie **wie weit** er reicht.

Vier Dinge, die bei der Umsetzung über den Plan hinausgingen:

- **«Werte übernehmen» musste mitgezogen werden.** `apply_sweep_to_draft` ließ den Modus auf `sweep` stehen. Nach dem Fix wären die eben sichtbar in den Editor geschriebenen Werte damit wirkungslos gewesen — der Schalter steht jetzt auf `custom`, genau wie `docs/handbuch/presets.md` es seit Längerem beschreibt.
- **Die Lauflänge wird beim Preset-Wechsel bewusst *nicht* vorbelegt.** Der Plan sah das vor; am laufenden System zeigte sich, warum es nicht geht. Werte fließen in dieser Oberfläche in genau eine Richtung, vom Feld in den Store. Von der anderen Seite gesetzt, schrieb das Eingabefeld seinen alten Wert beim nächsten Abgleich zurück — im Fenster stand 40, im Preflight 50, gerechnet worden wäre 50. Der Versuch, das über einen Neuaufbau des Blocks zu retten, machte es schlimmer: Dann gewann der alte Wert, und die Vorbelegung verschwand ganz. Die Länge, auf die ein Szenario angelegt ist, steht jetzt als Hinweis daneben. **Diese Einbahnstraße steht als Regel in `CLAUDE.md`** — sie gilt für jedes künftige Feld, nicht nur für dieses.
- **Der Feldbezug entsteht in der Prüfung, nicht in der Oberfläche.** `ValidationIssue` (eine `str`-Unterklasse, damit `"
".join(...)` und `in` bei allen heutigen Konsumenten weiter stimmen) trägt das Feld; jedes Eingabefeld bekommt einen Platzhalter, den ein Callback füllt. Eine Tabelle «Schlüsselwort → Feld» im Dashboard bräche still, sobald jemand einen Meldungstext umformuliert.
- **Zwei Wächter mussten ihrem Gegenstand folgen.** Der Seed-Wächter aus P0.6 las `save_start.py` über einen festen Pfad; der Doku-Link-Wächter durchsuchte nur `config_editor/*.py` und hätte die Verweise des neuen Moduls nicht abgedeckt. Beides nachgezogen — dieselbe Klasse wie die toten Modulpfade aus der ersten Gegenprobe.

**Was sich an den Zahlen verschiebt:** Läufe aus einem Szenario-Preset rechnen ab jetzt anders — nämlich so, wie das Preset es sagt. Über die Kommandozeile gestartete Sweeps waren nie betroffen. `docs/handbuch/vergleiche.md` nennt den Schnitt neben denen aus P0.7 und der `run_multi`-Angleichung; erkennbar ist er an `code_version` in `run_metadata.json`.

**Am laufenden System nachgestellt:** Ein `business_as_usual`-Lauf über 16 Ticks aus dem Dashboard-Pfad (`launch_from_draft`) hält `carbon_tax_level` über alle Ticks bei 50.0 und F2 bei F2.1. Die Seite selbst zeigt die drei Schritte, die Preset-Karten mit ihren Beschreibungen, die Ollama-Erreichbarkeit und den Preflight; ein Klick auf ein Preset zieht Beschreibung und Klartext-Satz live nach.

**Offen und bewusst nicht hier erledigt:** Der Preflight ruft die Konfigurationsprüfung bei jeder Änderung des Entwurfs auf, und die baut jedes Mal den vollständigen `SimulationState` auf. Auf einer lokalen Workbench ist das nicht spürbar; für den Mehrbenutzerbetrieb aus Phase 6 gehört es gemessen.

**Nachtrag vom 2026-08-28 — das Abnahmekriterium hat die falsche Größe gemessen.** «Höchstens drei Entscheidungen bis zum Start» zählt **Entscheidungen**, nicht **Wege**. Auf der 1400 px breiten Seite, für die der Ablauf entworfen wurde, fielen beide zusammen. In der 336-px-Spalte von [P1.5](#p15--leitstand-oberfläche--erledigt-2026-08-28) liefen sie auseinander: Die drei Entscheidungen blieben drei, der Start-Knopf lag danach **6,1 Bildschirme tief**, und Schritt 1 allein war 1.954 px hoch — zehn Preset-Optionen à 102 px untereinander. Der Test war grün.

Das Kriterium ist deshalb um eine zweite Größe ergänzt, und die misst Erreichbarkeit: **Der Start ist ohne Scrollen erreichbar, und die Spalte, in der er steht, bleibt unter anderthalb Bildschirmen.** Mechanisch gehalten wird das von `tests/test_web_rail.py` (Umfang des Bedienfelds) — nachgestellt wird es im Browser, weil ein pytest-Lauf keine Pixel kennt. Umgesetzt in [P1.6](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28).

**Als Prüfmuster mitnehmen:** Ein Kriterium, das eine Anzahl misst, sagt nichts über die Erreichbarkeit. Beides fällt nur so lange zusammen, wie der Platz reicht.

**Wieder geöffnet am 2026-08-28 — das ergänzte Kriterium reichte nicht.** Das Audit hat die zweite Größe geprüft, die P1.6 nachgetragen hat, und eine dritte gefunden, die keine der beiden misst: **Wirksamkeit.** «Höchstens drei Entscheidungen bis zum Start» zählt Entscheidungen — nicht, ob sie etwas bewirken. Auf dem Sweep-Pfad sind zwei der drei wirkungslos: `run_single_sweep` schreibt Rechenmodus und Seed fest, und vom Entwurf erreicht nur `rounds` den Lauf. Ein Kriterium, das Entscheidungen zählt, ist damit auf dieselbe Weise blind wie das, das Bildschirme nicht kannte. Aufgenommen in [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28) (Befund 1, Pakete W0.2 und W1.1).

**Doku zieht mit:** `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`.

### P1.2 — Ergebnisse und Plots refactoren ✅ erledigt 2026-08-30

> **Erledigt am 2026-08-30, in drei Teilen.** **Der Schnitt folgt jetzt Fragen statt Datenquellen:** vier Aussagen entlang der Wirkungskette (Preis → Nachfrage, Politik → Kosten, wer bleibt weg, Szenarien nebeneinander) statt sechs Reitern nach Herkunft der Zeitreihen. Zwei Ansichten sind weggefallen, beide weil sie **Eingänge statt Ergebnisse** zeigten — «Makro-Wirtschaft» steht unter «Modell», die Faktorlage ist Kontext an Aussage 4, wo sie die Szenarien unterscheidet. Der Bildexport folgt derselben Gliederung; die Titel im Manifest nennen die Aussage.
>
> **Der stille Teilstand ist weg, an beiden Ursachen:** Die Figuren entstehen in einer Werkstatt und ziehen erst als ganzer Satz um; ein liegengebliebenes `figures.neu/` ist ein sichtbarer Fehlerrest. Und ein Satz ohne Manifest sagt jetzt, dass seine Titel geraten sind — der Rückfall auf `glob` bleibt, weil ältere Läufe sonst verloren gingen.
>
> **Ein Farb- und Achsensystem für PNG und Bildschirm** (`figure_generator/stil.py`), von dem `theme.py` sich bedient — die Richtung so herum, weil `src/` nichts aus `dashboard/` importieren darf. Dabei kam ein Befund heraus, der schwerer wiegt als die Farben: Die Policy-Figur zeichnete Schockmarkierungen bei Tick 15 und 30 in Läufe **ohne** Schock, bei einem Lauf über fünf Ticks weit hinter dessen Ende. Ein leeres Ergebnis heißt jetzt, was es heißt.
>
> **Und der Test hat sich selbst korrigiert:** Die erste Fassung des Atomaritäts-Tests rechnete zweimal dieselben Daten und war grün, ohne dass etwas repariert war — die Plots sind deterministisch, ein Byte-Vergleich sah nichts.


**Befund:** Die Ergebnisdarstellung überzeugt inhaltlich nicht — die Plots zeigen nicht das, was eine Strategieabteilung sehen will. Dazu ein Robustheitsproblem: Bricht die Figure-Erzeugung mittendrin ab, zeigt die nächste Ansicht den unvollständigen Satz ohne Hinweis.

**Mechanismus korrigiert am 2026-08-26:** Die ursprüngliche Fassung sprach von einem "teilweise befüllten `manifest.json`". Das kann nicht passieren: [`run_figures.py:48-68`](../src/reporting/figure_generator/run_figures.py) baut alle sechs Figures in **einem** Dict-Literal und schreibt das Manifest erst danach — bricht ein Plot ab, entsteht **gar kein** Manifest. Der stille Teilstand entsteht an zwei anderen Stellen: [`dashboard/run_browser.py:224-231`](../dashboard/run_browser.py) fällt bei fehlendem Manifest auf `base.glob("*.png")` zurück und zeigt die halb geschriebenen PNGs mit aus dem Dateinamen erzeugten Titeln; und ein **altes** Manifest aus einem früheren Lauf bleibt liegen und passt dann nicht mehr zu den frisch überschriebenen PNGs.

**Fundstelle:** [`dashboard/web/views/figures.py`](../dashboard/web/views/figures.py) (441 Zeilen), [`dashboard/web/views/animation.py`](../dashboard/web/views/animation.py), [`dashboard/web/views/overview.py`](../dashboard/web/views/overview.py), Erzeugung in [`src/reporting/figure_generator/run_figures.py`](../src/reporting/figure_generator/run_figures.py), Glob-Fallback in [`dashboard/run_browser.py:201-231`](../dashboard/run_browser.py) (`list_run_figures`).

**Was zu tun ist:** Zuerst festlegen, welche **drei bis fünf Aussagen** ein Lauf beantworten soll — dann die Plots dafür bauen und den Rest streichen. Ein durchgehendes Farb- und Achsensystem aus `theme.py` statt pro Figur eigener Entscheidungen. Das Tripleset (Trendfortsetzung / Strukturwende / Krisenkonflikt) vergleichbar nebeneinander, nicht in getrennten Tabs. Für den Teilstand: Figures in ein temporäres Verzeichnis schreiben und erst nach dem letzten Plot samt Manifest atomar an ihren Platz ziehen — dann gibt es nur ganz oder gar nicht. Den Glob-Fallback in `list_run_figures` entweder streichen oder das Ergebnis sichtbar als "ohne Manifest, Vollständigkeit unbekannt" kennzeichnen.

**Fertig wenn:** Ein Lauf lässt sich in einem Screenshot erklären; ein abgebrochener Figure-Lauf hinterlässt keinen stillen Teilstand — weder über den Glob-Fallback noch über ein stehengebliebenes Manifest.

**Doku zieht mit:** `docs/handbuch/ergebnisse.md`, `docs/handbuch/ergebnisse-lesen.md`, `docs/handbuch/vergleiche.md`, `docs/handbuch/ref-ausgaben.md`.

### P1.3 — Szenariogestaltung neu denken ✅ erledigt 2026-08-30 (Datenschema; die Entstehung bleibt P2.0)

> **Erledigt am 2026-08-30 — im zugesagten Umfang.** Das Abnahmekriterium lautete «kein Konsument kann LLM-behauptete Einflusswerte mit echten Matrixwerten verwechseln», und genau das ist eingelöst: zwei typisierte Strukturen (`src/models/scenario_models.py`) statt eines Dicts mit zwei fast gleichen Schlüsseln, das Feld heißt **`behaupteter_einfluss`** statt `influence`, und jede Sammlung führt ihre `herkunft` mit. Vier Metadaten-Schlüssel werden zu zwei.
>
> **Der Wächter misst die Zusage, statt sie zu zählen:** Er geht die erzählte Struktur rekursiv durch und verlangt für **jeden** Zahlenwert, dass sein Feldname die Herkunft trägt — und hat sofort einen Fehler gefunden, den die Umstellung eingebaut hatte (`render_scenarios_markdown` las den alten Schlüssel weiter, der Bericht wäre leer geblieben).
>
> **Bewusst nicht hier:** wie die drei Szenarien entstehen. Das ist [P2.0](#p20--die-rolle-umdrehen-rahmen-statt-urteil--erledigt-2026-08-30); es jetzt mitzubauen hieße, es zweimal zu bauen.


**Befund:** Wie die drei Szenarien entstehen und was sie unterscheidet, ist im Produkt nicht nachvollziehbar. Zusätzlich liegen zwei ähnlich benannte Sammlungen im selben Metadaten-Dict: `scenario_candidates` (deterministisch aus dem `ScenarioDeriver`) und `scenarios` (LLM-Narrativ mit geklemmten, aber vom LLM erfundenen `influence`-Werten). Die Python/LLM-Grenze steht hier nur im Code-Kommentar, nicht im Datenschema.

**Fundstelle:** [`src/cib/scenario_agent_node.py:264,282`](../src/cib/scenario_agent_node.py), [`dashboard/web/views/scenario.py`](../dashboard/web/views/scenario.py), [`src/reporting/run_scenario_generator/`](../src/reporting/run_scenario_generator/).

**Was zu tun ist:** Die Grenze ins Datenschema ziehen: getrennte, eindeutig benannte Strukturen, LLM-Werte als solche markiert. In der UI sichtbar machen, welche Zahl gerechnet und welcher Satz erzählt ist.

**Fertig wenn:** Kein Konsument kann LLM-behauptete Einflusswerte mit echten Matrixwerten verwechseln.

**Doku zieht mit:** `docs/handbuch/zahlen-und-sprache.md`, `docs/handbuch/fragestellungen.md`, `docs/cib_role.md`.

> **Vorgezogen am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28)): Der Sweep-Pfad ist die Ursache der beiden kritischen Audit-Befunde — er verwirft alles außer `rounds` und überschreibt still die `max_ticks` jedes Presets. Diese Szenariogestaltung zu klären, **bevor** die Oberfläche darüber etwas behauptet, spart die doppelte Arbeit; W1.1 und W1.2 gehören fachlich hierher.

### P1.4 — Landingpage produktionsreif ⚠️ erledigt bis auf die Rechtstexte (2026-08-30)

> **Zwei von drei Punkten sind am 2026-08-30 erledigt.** **Kein Seitenaufruf verlässt mehr den eigenen Server:** Tailwind kommt aus einem Build (`npm run build:css`), die Schriften liegen im Repo — Material Symbols als Teilsatz von **5 KiB** statt Megabyte. Und das **Demo-Formular kommt an** (`POST /demo-anfrage`), als Datei abgelegt, ohne Mailversand, mit serverseitiger Prüfung und einer Rückmeldung in beiden Fällen.
>
> **Vier Wächter halten das**, und zwei davon haben beim ersten Durchlauf zugeschlagen: Der Klassen-Wächter (jede benutzte Klasse hat eine Regel) meldete zwei Phantome, die an ihm selbst lagen; der Symbol-Wächter fand drei Symbole, an die niemand gedacht hatte — und **vier weitere entgingen ihm**, weil sie in einem Modul-Dict stehen statt im Aufruf. Sie wurden als Wort gesetzt, und die Schrittliste brach um bis zu 308 px aus. Daraus kam ein fünfter Wächter, der **misst statt zu parsen**. Der wichtigste ist der Netzwerk-Wächter: Er hört die Anfragen jeder Ansicht mit und ist damit die Zusage selbst.
>
> **Offen bleibt genau eine Position: die Rechtstexte.** Die Gliederung steht, jede Pflichtangabe ist als benannte Lücke markiert, und `docs/landingpage.md` führt die Liste zum Abarbeiten mit Quelle je Angabe. Der Warnblock bleibt, solange eine Lücke offen ist — ein Test hält ihn fest. Die Inhalte brauchen Firmendaten und eine juristische Prüfung; erfundene Rechtstexte wären schlimmer als erkennbar unfertige.


**Befund (neu am 2026-08-26):** Die Landingpage kam in diesem Plan bisher nicht vor, obwohl Phase 1 "Funktionalität und UI" heißt und sie die einzige öffentlich sichtbare Oberfläche ist. [`docs/landingpage.md`](landingpage.md) führt drei offene Punkte, keiner davon war eingeplant:

1. **Das Demo-Formular geht ins Leere.** `demo-anfragen.html:151` hat `action="#"` — jede Anfrage über die Kontaktseite wird verworfen, ohne dass der Absender es merkt.
2. **Impressum, Datenschutz und AGB sind Platzhalter** mit `[…]`-Stellen und einem gelben Warnblock, der vor Veröffentlichung raus muss.
3. **Tailwind und Schriften kommen von CDNs** — auf der Landingpage (`index.html:7-9`) **und im Dashboard** (`dashboard/web/app.py:53-56`). Das widerspricht dem erklärten Deployment-Ziel Datenhoheit direkt: jeder Seitenaufruf meldet die IP des Betrachters an zwei fremde Hosts. Bei Google Fonts kommt die deutsche Rechtslage dazu.

**Fundstelle:** [`aeroforesight-ai-landing-page/`](../aeroforesight-ai-landing-page/) (5 Seiten, 1.928 Zeilen), [`dashboard/web/app.py:53-56`](../dashboard/web/app.py), [`dashboard/web/landing_route.py`](../dashboard/web/landing_route.py), [`docs/landingpage.md`](landingpage.md) (Abschnitt "Offene Punkte").

**Was zu tun ist:** Einen Endpunkt für das Demo-Formular anlegen (die Landingpage wird ohnehin von der Flask-App unter `landing_route.py` ausgeliefert — die Route gehört dorthin) samt Bestätigung für den Absender und einer Ablage, die niemand übersieht. Rechtstexte durch geprüfte Fassungen ersetzen und den Warnblock entfernen. Tailwind und die Schriften lokal ausliefern, für Landingpage und Dashboard in einem Zug, damit das Ergebnis nicht halb bleibt.

**Fertig wenn:** Ein Seitenaufruf erzeugt keine Anfrage an einen externen Host, keine `[…]`-Stelle und kein Warnblock ist mehr übrig, und eine abgeschickte Demo-Anfrage kommt nachweislich an.

**Doku zieht mit:** `docs/landingpage.md` ("Offene Punkte" leeren), `aeroforesight-ai-landing-page/DEPLOY.md`, `CLAUDE.md` (Deployment-Ziel, Datenhoheit).

### P1.5 — Leitstand-Oberfläche ✅ erledigt 2026-08-28

> **Abnahme ergänzt am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28)): Zonen, Theme und Zeitleiste tragen und werden **nicht** zurückgebaut. Den Kriterien fehlt aber eine Größe, die niemand geprüft hat — **Barrierefreiheit**. Gemessen: null `aria-live`-Regionen im gesamten Dokument, kein `aria-current`, keine Fokusführung beim Bereichswechsel. Nachzuziehen mit Paket W5.3. — **Teilweise eingelöst am 2026-08-29:** W5.3 hat die Schrittfolge durchgearbeitet (fünf Live-Regionen, `aria-current`, Fokus auf die Frage, `fieldset`/`legend`). Die **übrigen Zonen des Leitstands** blieben damit offen. — **Eingelöst am 2026-08-30:** Der Bereichswechsel trägt jetzt dieselben vier Größen. Gemessen am laufenden System, und dabei kamen drei Dinge heraus, die im Baum nicht zu sehen waren: `dcc.Link` **nimmt keine ARIA-Attribute an** (und `html.A` an seiner Stelle lüde die Seite neu, deshalb wird `aria-current` aus der Klasse abgeleitet); ein Bereichswechsel **tauscht nichts aus**, er schaltet `style` um — ein Beobachter, der nur `childList` kennt, feuert dabei nie; und **zwei der fünf Bereiche hatten gar keine Überschrift**, weshalb der Fokus auf `BODY` oder auf «Population im Tick» landete. Dazu ein «Zum Inhalt springen»-Link als erstes fokussierbares Element. **Was offen bleibt und hier so steht:** die einzelnen Ergebnis-Ansichten und eine vollständige WCAG-Prüfung mit Hilfsmitteln und Menschen.

**Befund:** P1.1 hat den *Weg* zum Lauf in Ordnung gebracht, nicht den *Rahmen* darum. Das Dashboard war eine klassische Dokumentseite — `max-w-[1400px]`, drei Bereiche untereinander, Browser-Scroll für alles. Für Ingenieure, Analysten und Forscher, die einen laufenden Lauf beobachten und dabei Parameter, Kennzahlen und Log gleichzeitig im Blick brauchen, ist das die falsche Form: Man scrollt zwischen Einstellung und Wirkung hin und her, statt beides nebeneinander zu sehen. Dazu gab es **nur Light Mode** — für lange Sitzungen vor Zeitreihen ein ergonomisches Problem.

**Fundstelle:** [`dashboard/web/app.py`](../dashboard/web/app.py), [`dashboard/web/theme.py`](../dashboard/web/theme.py), [`dashboard/web/components.py`](../dashboard/web/components.py), [`dashboard/web/assets/dashboard.css`](../dashboard/web/assets/dashboard.css), [`dashboard/web/pages/`](../dashboard/web/pages/).

**Was zu tun war:** Ein vollflächiges Leitstand-Layout (100 dvh, fünf Zonen, kein unkontrolliertes Seiten-Scrollen) mit umschaltbarem Light-/Dark-Theme. Der geführte Ablauf aus P1.1 zieht als linke Parameterspalte mit ein, ohne dass seine Zusicherungen wackeln.

**Drei Entscheidungen vorab (Haiko, 2026-08-28):**

1. **Das ganze Dashboard** zieht in den Rahmen, nicht nur eine neue Ansicht daneben.
2. **Platzhalter-Daten nur als markierter Demo-Lauf.** Die Vorgabe verlangte Mock-Data; das kollidiert mit Invariante 1. Auflösung: Standard ist der jüngste echte Lauf; gibt es keinen, zeigt der Leitstand einen synthetischen Datensatz mit Abzeichen in der Kopfzeile, Banner über dem Viewport und eigener Signalfarbe.
3. **Der Viewport zeigt die Population**, keinen WebGL-Platzhalter. Die Domäne hat keine Geometrie; sie hat einige hundert Individuen je Tick und sieben Faktorzustände.

**Fertig wenn:** Fünf Zonen füllen den Bildschirm, Kopfzeile und Zeitleiste bleiben stehen, jede Zone scrollt für sich, kein Seiten-Scroll; beide Themes tragen jede Fläche; `test_web_start_flow.py` bleibt unverändert grün.

**Umgesetzt am 2026-08-28.** `shell.py` hält den Rahmen, `status.py` **eine** Ableitung des Anlagenzustands (läuft / Demo / beeinträchtigt / bereit) für Kopfzeile, Banner und Konsole, `run_data.py` die Daten eines Laufs aus einer Hand, `timeline.py` die einzige Zeitachse der Oberfläche, `views/scene.py` den Viewport, `views/telemetry.py` die rechte Zone. Farbe läuft über eine semantische Token-Ebene, die in `theme.py` und `assets/dashboard.css` **dieselben Namen** trägt — je einmal hell und einmal dunkel.

**Der Wächter ist der Kern des Pakets.** `tests/test_web_theme.py` läuft als AST-Durchlauf über `dashboard/web/` und meldet jede Tailwind-Farbklasse und jeden rohen Farbwert. Eine gepflegte Dateiliste finge nur den Rückfall an bekannter Stelle; genau daran wäre dieses Paket sonst gescheitert — der Sweep fand beim ersten Lauf vier Stellen, an die niemand gedacht hatte, darunter die Farben der Ladeanzeigen in drei Ansichten.

Vier Dinge, die bei der Umsetzung über den Plan hinausgingen:

- **Die Stile für Dashs eigene Komponenten griffen seit dem Sprung auf Dash 4 an keiner einzigen Stelle mehr.** `assets/dashboard.css` stylte `rc-slider-*` und `Select-*`; Dash 4.4 liefert `dash-slider-*` und `dash-dropdown-*`. Im hellen Modus fiel das nie auf, weil Dashs Standarddesign hell ist — im dunklen trug der Regler der Zeitleiste Dashs Violett, und seine Beschriftungen standen schwarz auf schwarz. Behoben nicht über einzelne Selektoren, sondern indem Dashs eigene Token-Ebene (`--Dash-*`) auf unsere abgebildet wird: Damit trägt **jede** Dash-Komponente in beiden Modi die richtigen Farben, auch die, die noch niemand angefasst hat. Am laufenden System gefunden, nicht im Test — die Klassennamen stehen in keinem Python-Modul.
- **Die Konsole ist in beiden Modi dunkel, ihre Stufen dürfen es nicht sein.** Der helle Warnton (`#b45309`) kam auf Navy-950 nur auf ein Kontrastverhältnis von 3,2. Die drei Konsolenrollen tragen deshalb in beiden Paletten dieselben hellen Töne. Nachgemessen im Browser, nicht geschätzt; schlechtester Wert der Oberfläche liegt jetzt bei 4,55.
- **Der Zoom-Overlay zeigt keine Framerate.** Die Vorgabe nannte eine; es wird nichts fortlaufend gerendert, das eine hätte. An ihrer Stelle stehen Tick, Populationsgröße und Ausschnitt — die drei Angaben, die beim Betrachten der Szene wirklich fehlen.
- **Die Achsen der Szene stehen über alle Ticks fest**, nicht über den gezeigten. Sonst atmet der Ausschnitt bei jedem Schritt der Zeitleiste, und eine Bewegung im Bild hieße nicht mehr «die Population verschiebt sich», sondern «die Achse hat sich angepasst».

**Was sich an den Zahlen verschiebt:** nichts. Das Paket fasst ausschließlich die Darstellung an; kein Rechenpfad, keine Config und kein Artefakt ändern sich. `docs/handbuch/vergleiche.md` bleibt deshalb bewusst unberührt.

**Offen und bewusst nicht hier erledigt:** Die PNG-Tafeln unter `figures/` werden von matplotlib hell gerendert und stehen im Dark Mode auf einer weißen Fläche wie ein aufgelegtes Blatt. Sie dunkel zu erzeugen gehört zu [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30). Ebenso bleibt der Vorbehalt aus P1.1 bestehen und wiegt jetzt schwerer: Der Preflight baut bei jeder Änderung des Entwurfs den vollständigen `SimulationState` auf, und die Parameterspalte ist ab jetzt dauerhaft sichtbar — er wird also häufiger angestoßen als vorher. Für Phase 6 zu messen.

**Nachtrag vom 2026-08-28 — «Fertig wenn» prüfte Mechanik, nicht Brauchbarkeit.** Fünf Zonen, feste Kopfzeile, jede Zone scrollt für sich, beide Themes tragen jede Fläche: alles erfüllt. Die Oberfläche war trotzdem nicht bedienbar, weil das Kriterium nichts über die **Verteilung** sagte. Gemessen am Tag danach (1280 × 720):

| | links | Mitte | rechts |
| --- | --- | --- | --- |
| Breite | 336 px | 592 px (**46 %**) | 352 px |
| Inhaltshöhe | **7.112 px = 10,7 Bildschirme** | 595 px = 1,0 | 1.022 px = 1,5 |
| Wörter | 752 | 87 | 3.307 |
| Eingabefelder | **122** | – | – |

P1.5 hat den geführten Ablauf aus P1.1 — entworfen für 1400 px Seitenbreite — samt Editor in eine 336-px-Spalte gepresst. Das Kriterium ist deshalb ergänzt: **Der Viewport trägt bei 1280 px mindestens 55 % der Breite, und keine Zone verlangt mehr als anderthalb Bildschirme Scrollen für das, was sie ständig zeigt.** Behoben in [P1.6](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28).

**Doku zieht mit:** `CLAUDE.md` (Architektur-Map, dritte Regel zur Farbe), `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/ergebnisse.md`, `README.md`.

### P1.6 — Einrichten und Beobachten trennen ✅ erledigt 2026-08-28

**Befund:** Die linke Zone des Leitstands trug die vollständige Konfiguration — den geführten Ablauf aus P1.1 **und** die vier Editor-Tabs — in 336 px Breite. Die Zahlen stehen im Nachtrag zu P1.5 oben. Der Kern: **Einrichten und Beobachten sind zwei Betriebsarten mit gegenläufigen Anforderungen.** Einrichten braucht Fläche, Fließtext und sechzig Felder; Beobachten braucht Dichte, Ruhe und wenige, immer sichtbare Bedienelemente. Kein professionelles Werkzeug (Grafana, Datadog, Kibana, Simulink) legt die vollständige Konfiguration dauerhaft neben die Live-Ansicht; überall ist das Einrichten ein eigener Modus, der die volle Breite bekommt.

**Fundstelle:** [`dashboard/web/pages/launch.py`](../dashboard/web/pages/launch.py), [`dashboard/web/config_editor/start_flow.py`](../dashboard/web/config_editor/start_flow.py), [`dashboard/web/assets/dashboard.css`](../dashboard/web/assets/dashboard.css).

**Was zu tun war:** Die Konfiguration in einen eigenen Viewport-Bereich, die Spalte auf ein Bedienfeld zurückführen — was eingestellt ist, der Preflight, der Start.

**Fertig wenn:** Die linke Zone bleibt unter anderthalb Bildschirmen, der Start-Knopf ist ohne Scrollen erreichbar, der Viewport trägt bei 1280 px mindestens 55 %, und `test_web_start_flow.py` bleibt unverändert grün.

**Umgesetzt am 2026-08-28.** `dashboard/web/pages/setup.py` ist der vierte Bereich neben Leitstand, Ergebnisse und Handbuch; er enthält, was vorher in der Spalte stand — **verschoben, nicht neu geschrieben**. Die Spalte trägt jetzt drei Stand-Zeilen (Szenario, Länge, Rechenmodus, je ein Verweis ins Einrichten), den Preflight und den Start-Knopf in einem klebenden Fuß. Die Presets stehen als Kartenraster statt als Liste, Schritt 2 und 3 nebeneinander.

Gemessen nach dem Umbau, mit denselben Werkzeugen wie vorher:

| | vorher | jetzt |
| --- | --- | --- |
| Linke Zone | 10,7 Bildschirme | **1,4** |
| Wörter links | 752 | **53** |
| Eingabefelder links | 122 | **0** |
| Start-Knopf | 6,1 Bildschirme tief | **ohne Scrollen sichtbar** |
| Viewport bei 1280 px | 46 % | **55 %** |
| Konsolenzeilen im DOM | 254 | **≤ 80**, zugeklappt |
| Szene | 534 × 374 px | **652 × 446 px** |

Drei Dinge, die bei der Umsetzung über den Plan hinausgingen:

- **Tailwinds Haltepunkte messen das Fenster, nicht die Zone.** `xl:grid-cols-2` teilte bei 1280 px die 720 px des Viewports in zwei 319-px-Spalten — dieselbe Enge, gegen die dieses Paket antritt, nur eine Ebene tiefer. Die Schritte teilen sich die Reihe jetzt erst ab `2xl`. **Für jede künftige Spaltenaufteilung innerhalb einer Zone gilt das genauso.**
- **Der Wächter kann keine Pixel zählen**, und eine Liste erlaubter Feldnamen wäre wertlos gewesen. `tests/test_web_rail.py` zählt stattdessen die Größen, aus denen die Pixel entstehen: Eingabefelder (null), Wörter (heute 53, erlaubt 160), Textblöcke. Ein Kontrolltest schiebt den Editor zurück in die Spalte und zeigt, dass der Zähler anschlägt.
- **Der Preflight wandert, er wird nicht kopiert.** Zwei Fassungen hießen zwei Platzhalter mit derselben Dash-ID. `preflight()` nimmt den Slot-Namen jetzt als Parameter; `test_web_start_flow.py::test_live_state_fills_every_slot_the_layout_declares` geht seither **beide** Bäume ab — Einrichten und Bedienfeld —, weil ein Slot ohne Inhalt nach der ersten Änderung leer stehen bliebe.

**Ein Hinweis für den, der als Nächstes im Browser misst:** Ist die Vorschau-Ansicht nicht sichtbar, zeichnet die Seite keine Bilder, und **laufende CSS-Übergänge bleiben eingefroren**. `getComputedStyle` liefert dann den alten Wert — auch gegen `!important`. Drei vermeintliche Fehler in diesem Paket (die Schublade öffnet nicht, die gewählte Karte bleibt ungerahmt, die Stand-Zeilen sind im Dark Mode weiß) waren genau das. Wer misst, schaltet vorher `transition: none` zu.

**Was sich an den Zahlen verschiebt:** nichts. Nur Darstellung; kein Rechenpfad, keine Config, kein Artefakt. `vergleiche.md` bleibt unberührt.

**Offen und bewusst nicht hier erledigt:** Der Bereich «Einrichten» ist bei 1280 px 7,3 Bildschirme lang. Das ist für eine Konfigurationsseite in Ordnung — sie wird gelesen, nicht überwacht —, aber die 90 Eingabefelder unter «Systemgrößen» sind ein eigener Fall für [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30) oder ein späteres Paket. Ebenso unverändert: Der Preflight baut bei jeder Entwurfsänderung den vollen `SimulationState` auf.

**Doku zieht mit:** `CLAUDE.md` (Architektur-Map, vierte Regel zur linken Spalte), `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/ergebnisse.md`, `docs/handbuch/glossar.md`, `README.md`, `dashboard/README.md`.

---

### Gegenprobe zu P1.1/P1.5/P1.6 (Manu, 2026-08-28)

Die drei Pakete wurden am laufenden System nachgestellt. **Die tragenden Zusagen halten:** keine einzige doppelte Dash-ID im vollständig zusammengebauten Layout (228 IDs, 228 eindeutig — mechanisch geprüft, nicht nach Gefühl), der geführte Ablauf schreibt bei echter Tastatureingabe sauber in den Store, das Bedienfeld trägt null Eingabefelder, und der Start-Knopf steht bei 1440 px ohne Scrollen sichtbar neben dem Bereich «Einrichten». Auch die Messung zum Zwischenspeicher stimmt: `run_data.load` braucht 2,7 ms, ein Tick-Schritt löst drei davon aus — 7 % der Taktzeit bei vierfachem Tempo, also kein Fall für weiteres Zwischenspeichern. Der Verdacht war da, die Messung hat ihn ausgeräumt.

**Drei Befunde, alle in der Darstellung, keiner an einer Zahl.**

1. **Der Schubladen-Knopf war auf jeder Breite sichtbar — auch dort, wo es keine Schublade gibt.** `.af-drawer-toggle { display: none }` steht in `dashboard.css` **vor** `.af-icon-btn { display: inline-flex }`, und beide tragen genau eine Klasse. Bei gleicher Spezifität gewinnt das Spätere: Die Versteck-Regel hat **nie** gewirkt. Bei 1600 px, wo beide Zonen feste Rasterspalten sind, standen trotzdem beide Umschalter da. Behoben mit zwei Klassen (`.af-icon-btn.af-drawer-toggle`) statt einer — das ist ordnungsunabhängig, während ein Verschieben des Blocks nur bis zur nächsten Umsortierung hält. **Dieselbe Falle wie bei Dashs `--Dash-*`-Ebene in P1.5**, wo `html:root` gegen `:root` gesetzt werden musste: Wer eine fremde Regel schlagen will, verlässt sich nicht auf die Reihenfolge.
2. **Und sein Haltepunkt gehörte der falschen Zone.** Beide Umschalter teilten sich eine Sichtbarkeitsregel bei 1280 px, obwohl die Parameterspalte erst unter 1024 px zur Schublade wird. Zwischen 1024 und 1279 px setzte der Klick nachweislich `af-shell--left-open`, die Spalte blieb aber `position: static` bei x=0 und der Verdunkler aus — **nichts bewegte sich**. Schlimmer als folgenlos: Der Zustand blieb stehen, und beim nächsten Verkleinern sprang die Schublade samt Verdunkler ungefragt auf. Jeder Umschalter trägt jetzt seinen eigenen Modifikator.
3. **Der Laufzustand kannte nur die eigene Sitzung.** `_running` las die beiden Schalter, die der eigene Lauf setzt — mit der ausdrücklichen Begründung, die Anzeige gehöre zu dieser einen Sitzung. Für die Anzeige stimmt das, für die Sache dahinter nicht: `runner` lässt **einen** Lauf im ganzen Prozess zu. Nachgestellt bei einem Lauf über 500 Ticks: Eine mitten im Lauf neu geladene Seite meldete «System bereit», der Start-Knopf stand aktiv da, und sein Druck endete in «Es läuft bereits eine Simulation. Bitte abwarten.» Genau der Widerspruch, gegen den `status.py` angetreten ist — nur eine Ebene tiefer, weil die Tatsache gar nicht erst bis zu ihm kam. `runner.is_running()` entscheidet jetzt, beim ersten Zeichnen und im Takt von `run-heartbeat`; `run-poll` bleibt daneben, weil nur er den eigenen Start ohne Verzögerung bestätigt.

**Was die Wächter angeht, ist der zweite Befund der lehrreiche.** Der erste Anlauf für `tests/test_web_drawers.py` verglich nur die beiden Haltepunkt-Zahlen aus dem Stylesheet — und wäre grün geblieben, denn die Zahlen standen richtig da; falsch war, welche Regel am Ende gewinnt. Der Wächter rechnet deshalb jetzt die Kaskade nach (Spezifität, dann Reihenfolge) und prüft in einem zweiten Test, dass der Gegenspieler überhaupt noch existiert — sonst sicherte er irgendwann nichts mehr. Beide Wächter sind mutationsgeprüft: Mit dem alten Stand eingebaut melden sie ihn, und zwar mit der gewinnenden Regel im Text.

**Ein Fehlgriff in eigener Sache, protokolliert:** Die erste Messung setzte den Wert des Längenfelds per JavaScript und schloss aus dem unveränderten Store auf einen Bug. Das war keiner — Dash hört auf Reacts Ereignisse, die ein synthetisches `input` nicht auslöst. Mit echtem Klick und echter Tastatur griff der Store sofort. **Wer eine Oberfläche prüft, bedient sie wie ein Mensch**; was am Werkzeug scheitert, ist noch kein Befund.

**Zwei Doku-Zahlen mitgezogen:** `CLAUDE.md` kündigte «Drei Regeln» an und zählte vier auf — dieselbe Klasse wie die veralteten Zahlen der sechsten Runde in Phase 0, und dieselbe Handregel: Wer eine Aufzählung erweitert, sucht ihre Anzahl im Fließtext. Jetzt fünf, mit der neuen Regel zum Serverzustand.

**Nicht hier behoben, weil vorbestehend:** `default_selection` verspricht «der jüngste Run», nimmt aber `runs[0]` aus einer **alphabetisch** absteigenden Verzeichnisliste (`run_browser.list_runs`). Der Leitstand startet deshalb auf einem Sweep statt auf dem zuletzt gerechneten Lauf. Stammt aus dem ursprünglichen Run-Browser, nicht aus diesen drei Paketen; wiegt seit P1.5 aber schwerer, weil die Vorauswahl jetzt den ganzen Bildschirm füllt. Gehört als Finding in `audit_findings.md` und in ein Paket der Phase 1.

**Was die Zahlen macht:** nichts. Alle drei Befunde liegen in der Darstellung; kein Rechenpfad, keine Config, kein Artefakt. `vergleiche.md` bleibt unberührt.

---

### P1.7 — Der Ablauf wird die Oberfläche ✅ erledigt 2026-08-28

> **Wieder geöffnet am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28)): Die tragende Zusage dieses Pakets — *eine Frage auf dem Schirm* — ist **nicht gehalten**. Gemessen bei 1280 × 720 braucht kein einziger der acht Schritte weniger als einen Bildschirm; Schritt 4 braucht 3,37 und trägt 104 Bedienelemente, Schritt 5 braucht 4,44. Abgenommen wurde «nur der offene Schritt steht im DOM» — das ist erfüllt und zählt Knoten statt Bildschirme. Dazu drei Wegführungsbefunde: übersprungene Schritte tragen ein Erledigt-Häkchen, «Weiter» garantiert nichts, und «Zurück» kehrt nicht dorthin zurück, wo man herkam. Der Fokus-Modus, die klebende Fußleiste und der Einstieg mit drei Wegen bleiben — sie haben sich bewährt.

**Befund (Manu am Produkt, 2026-08-28).** P1.6 hat Einrichten und Beobachten in zwei Zonen getrennt. Getrennt sind sie damit räumlich, nicht zeitlich: Die Oberfläche zeigt weiterhin alles gleichzeitig und sagt nirgends, in welcher Reihenfolge man es tut. Fünf Beobachtungen, alle am fertigen Leitstand:

1. **Die Navigation steht gegen den Arbeitsablauf.** «Leitstand» kommt zuerst, «Einrichten» an zweiter Stelle — angefangen wird aber immer beim Einrichten. Wer das Dashboard zum ersten Mal öffnet, landet auf einer Ansicht, für die es noch nichts zu sehen gibt.
2. **Der Start ist kein Ereignis.** Man drückt «Start», und die Seite sieht aus wie vorher. Dass etwas passiert, steht in einem Statuspunkt in der Kopfzeile und in einer zugeklappten Konsole. Das Auffälligste am Bildschirm bleibt das Einrichtungsformular — also genau das, was jetzt vorbei ist.
3. **Wer währenddessen weggeht, verliert den Lauf aus dem Blick.** Es gibt keinen Grund, während eines Laufs nicht einen älteren anzusehen; heute gibt es dabei aber keine Anzeige, wie weit der laufende ist.
4. **Der Bereich «Einrichten» ist eine Bildlaufstrecke mit Reitern am Ende.** Bei 1280 px sind es 7,3 Bildschirme; die vier Editor-Reiter liegen unten hinter einer Trennlinie. Reiter unterhalb des Falzes sind keine Gliederung — man findet sie nur, wenn man ohnehin schon weiß, dass es sie gibt.
5. **Ein Knopf, der nichts hinzufügt.** Das Bedienfeld trägt neben der Überschrift «Lauf» einen Knopf «Einrichten», der dorthin führt, wo der Navigationspunkt daneben auch hinführt.

Dazu ein Wunsch, der keine Fehlbedienung behebt, sondern eine Einschränkung: **Die Zonenbreiten sind fest.** Wer die Szene größer haben will oder die Telemetrie breiter, kann das nicht.

**Fundstelle:** [`dashboard/web/shell.py`](../dashboard/web/shell.py) (`ROUTES`, Kopfzeile, Zonenmaße), [`dashboard/web/pages/setup.py`](../dashboard/web/pages/setup.py), [`dashboard/web/pages/launch.py`](../dashboard/web/pages/launch.py) (Bedienfeld und Start), [`dashboard/web/config_editor/start_flow.py`](../dashboard/web/config_editor/start_flow.py), [`dashboard/web/runner.py`](../dashboard/web/runner.py) (Fortschritt hängt am Job, nicht am Server), [`dashboard/web/assets/dashboard.css`](../dashboard/web/assets/dashboard.css) (`--shell-left`, `--shell-right`).

**Die Leitidee: Die drei Tätigkeiten haben verschiedene Takte.** Einrichten ist eine überlegte, lineare Arbeit mit vielen Entscheidungen. Rechnen ist Warten, und dabei zählt genau eine Auskunft. Auswerten ist Stöbern in etwas Fertigem. Die Oberfläche zeigt heute alle drei gleichzeitig und gleich laut. Sie sollen künftig **nacheinander** kommen und der Bildschirm soll sagen, wo man gerade steht.

Was dabei **nicht** verloren gehen darf, ist die Zusicherung aus P1.1: **drei Entscheidungen genügen bis zum Start.** Ein geführter Ablauf, der acht Schritte erzwingt, wäre ein Rückschritt gegenüber dem, was P1.1 erreicht hat — die Schritte vier bis sieben sind deshalb überspringbar, und `tests/test_web_start_flow.py::TestDreiEntscheidungen` bleibt gültig.

---

#### Stufe A — Rahmen: Reihenfolge, ziehbare Zonen, ein Knopf weniger ✅ erledigt 2026-08-28

1. **`shell.ROUTES` in die Reihenfolge des Ablaufs bringen:** Einrichten, Leitstand, Ergebnisse, Handbuch. Der leere Pfad (`/app/`) wird **Einrichten** — dort fängt man an. Der Leitstand zieht auf `/app/lauf`. `setup` bleibt als Aliaspfad bestehen, damit gespeicherte Verweise und die Stand-Zeilen des Bedienfelds nicht ins Leere zeigen.
2. **Ziehbare Trenner** zwischen Bedienfeld und Viewport sowie zwischen Viewport und Telemetrie. Umgesetzt als schmale Greifflächen, die per `clientside_callback` `--shell-left` bzw. `--shell-right` auf dem Shell-Element setzen; der Wert wird in `localStorage` gehalten und beim Aufbau zurückgelesen. Grenzen aus dem heutigen `clamp()` übernehmen, Doppelklick setzt zurück. **Serverseitig passiert dabei nichts** — dieselbe Begründung wie beim Theme-Umschalter in P1.5: Ein Rundlauf je Mausbewegung macht das Ziehen zäh. Unterhalb von 1024 px greift die Schubladenlogik aus P1.5/P1.6 unverändert; dort sind die Trenner ausgeblendet.
3. **Der Knopf «Einrichten» im Bedienfeld entfällt.** Die drei Stand-Zeilen führen bereits dorthin, und der Navigationspunkt steht zwei Zentimeter darüber.

**Fertig wenn:** Die Navigation liest sich als Ablauf; beide Trenner lassen sich ziehen, die Breite überlebt einen Neuladen, und ein Doppelklick stellt den Ausgangswert her; im Bedienfeld steht kein zweiter Weg ins Einrichten mehr.

---

#### Stufe B — Der Lauf ist ein eigener Zustand ✅ erledigt 2026-08-28

1. **Der Fortschritt gehört dem Server, nicht dem Job-Besitzer.** `runner` bekommt eine Auskunft über den **aktiven** Lauf (Kennung, aktueller Tick, Zieltick, letzte Zeile) — abgeleitet aus den Zeilen, die er ohnehin sammelt. Ohne das kann nur die Sitzung, die gestartet hat, etwas anzeigen; genau diese Grenze ist beim Fix zum Laufzustand bewusst stehen geblieben und wird hier eingelöst. **Die Zahlen bleiben, was sie sind:** Der Fortschritt wird aus den Fortschrittszeilen *gelesen*, nicht geschätzt — steht dort nichts, zeigt die Oberfläche einen unbestimmten Balken statt einer erfundenen Prozentzahl (Invariante 1).
2. **Der Leitstand wird während eines Laufs zum Ladebildschirm.** Kein Formular, keine Editorreste: der Name des Laufs, was er rechnet (Szenario, Länge, Rechenmodus), ein Fortschrittsbalken mit «Tick x von y», und die Konsole — hier **aufgeklappt**, weil sie in diesem Zustand das Einzige ist, was es zu sehen gibt. Ist der Lauf fertig, führt ein deutlicher Weg nach «Ergebnisse».
3. **Ein Fortschrittsfenster unten rechts**, sobald ein Lauf läuft und man **nicht** auf dem Leitstand steht. Es zeigt Balken und Tick-Stand, führt mit einem Klick zum Ladebildschirm und lässt sich zuklappen (nicht abbrechen — der Lauf gehört nicht dem Fenster). Damit ist der eigentliche Wunsch erfüllt: Während gerechnet wird, kann man in «Ergebnisse» einen älteren Lauf ansehen, ohne den laufenden aus den Augen zu verlieren.
4. **Nach dem Ende** wechselt der Zustand sichtbar: Der Ladebildschirm wird zur Fertigmeldung mit den Kennzahlen des Laufs und dem Weg in die Ergebnisse; das Fortschrittsfenster verschwindet.

**Fallstrick — der Takt ist schon da, die Zeilen sind es nicht.** `run-heartbeat` aus dem Laufzustand-Fix läuft in jeder Sitzung und ist der richtige Träger. Was fehlt, ist die serverseitige Fortschrittsauskunft aus Punkt 1; ohne sie zeigt jede fremde Sitzung einen leeren Balken. Reihenfolge deshalb: erst `runner`, dann die beiden Ansichten.

**Fertig wenn:** Ein Start wechselt sichtbar den Bildschirm; während des Laufs ist von der Einrichtung nichts mehr zu sehen; ein zweiter Tab zeigt denselben Fortschritt; ein Wechsel nach «Ergebnisse» lässt das Fortschrittsfenster erscheinen; nach dem Ende führt ein Klick zum fertigen Lauf.

---

#### Stufe C — Einrichten als geführter Ablauf ✅ erledigt 2026-08-28

**Punkt 1 kam am 2026-08-28 nach.** Die Schrittfolge (Punkte 2–4) lief seit dem Vortag; der Einstieg fehlte, und damit war «Szenario-Vergleich starten» weiterhin eine Ankreuzoption hinter der Feinabstimmung in Schritt 2 — genau die Unauffindbarkeit, gegen die Punkt 1 antritt. Die Marke stand hier zwischenzeitlich auf «erledigt»; das war falsch und ist beim Abgleich mit dem Besprochenen aufgefallen.

**Wie der Einstieg gebaut ist.** Drei ganzflächige Karten in `wizard.entry`; der Schritt-Store hält `None` für «Einstieg» und einen Index für einen Schritt. Einstieg und Schrittfolge stehen **beide** dauerhaft im DOM, umgeschaltet wird nur die Sichtbarkeit — die drei Wege hängen am selben Callback wie «Weiter» und «Zurück», und ein Eingang, den es auf Schritt 3 nicht gäbe, nähme die ganze Navigation mit (Regel 6, in P1.7 schon einmal passiert). «Zurück» auf Schritt 1 führt zurück auf den Einstieg; vorher war der Knopf dort abgeschaltet, und die Schrittfolge wäre eine Sackgasse gewesen.

**Ein Punkt, der eine Regel berührt.** Die beiden ersten Wege *schreiben* in den Draft-Store — das ist die erste Ausnahme von der Einbahnstraße aus P1.1. Sie ist bewusst und eng: «ein Lauf» und «alle Szenarien» sind die Entscheidung selbst, es gibt kein anderes Feld dafür als jenes Kästchen hinter der Feinabstimmung, geschrieben wird genau ein Feld (`run_all_sweeps`), und nur, solange kein Eingabefeld sichtbar ist, das den Wert zurückschreiben könnte. Ohne dieses Schreiben bliebe ein einmal gewählter Vergleich beim nächsten Weg still aktiv — man startete acht Läufe, wo man einen wollte. Am laufenden System nachgestellt: «Neuen Lauf einrichten» nach «Szenario-Vergleich» setzt das Kästchen in Schritt 2 wieder aus, und umgekehrt.

«Letzte Einstellungen weiterverwenden» schreibt dagegen **nichts** und springt nur ans Ende. Es ist ausgegraut, solange der Entwurf dem Auslieferungszustand entspricht — ein Weg, der nichts anzubieten hat, wird ausgegraut und nicht weggelassen (wieder Regel 6). Der Draft-Store liegt in `sessionStorage` und überlebt einen Neuladen; genau daraus bezieht dieser Weg seinen Sinn.

1. **Ein Einstieg mit drei Wegen** statt einer Bildlaufstrecke: «Neuen Lauf einrichten» (der Ablauf unten), «Szenario-Vergleich starten» (alle Presets nacheinander — heute eine Ankreuzoption hinter «Feinabstimmung», also faktisch unauffindbar) und «Letzte Einstellungen weiterverwenden».
2. **Der Ablauf selbst als Schrittfolge** mit Schrittleiste, «Zurück» und «Weiter». **Jeder Schrittwechsel setzt die Ansicht wieder an den Anfang** — die Bildlaufhöhe des vorigen Schritts bleibt sonst erhalten, und gerade nach dem langen vierten Schritt stünde man mitten im nächsten statt bei dessen Frage. Die Schritte eins bis drei sind die drei Entscheidungen aus P1.1 und bleiben inhaltlich unverändert. Die Schritte vier bis sieben sind die vier heutigen Editor-Reiter — **jeder überspringbar**, und aus Schritt drei führt ein Weg direkt zum letzten Schritt. Damit bleibt «drei Entscheidungen bis zum Start» wahr, und die Reiter hören auf, ein Anhängsel unterhalb des Falzes zu sein: Sie werden benannte Stationen mit sichtbarem Fortschritt.
3. **Der letzte Schritt ist «Prüfen & Starten»** — der Preflight, und daneben die beiden Ausgänge, die dieser Bildschirm schuldet: **als Szenario speichern** oder **Lauf starten**.
4. **Zwei Auslöser, ein Startpfad.** Der Startknopf im Bedienfeld bleibt, wo er ist; der im letzten Schritt ist ein **zweiter Auslöser desselben Callbacks**, keine zweite Startlogik. Der Einwand aus P1.6 («ein zweiter Startpfad wäre ohne Gewinn») trifft eine zweite Prüfung und eine zweite `runner.start`-Stelle — nicht einen zweiten Knopf, der in dieselbe Funktion führt. Zwei Knöpfe mit **derselben** ID wären dagegen weiterhin ein Laufzeitfehler; die Regel aus der Architektur-Map gilt unverändert.

**Fallstrick — die Schrittfolge darf die Einbahnstraße nicht brechen.** Die Felder tragen Pattern-IDs und fließen über `_sync` in den Store (Regel 2 der Architektur-Map). Ein Schritt, der beim Verlassen Werte *zurückschreibt*, führte dieselbe Zahl an zwei Stellen — genau der Fehler, den P1.1 bei der Lauflänge gemacht und wieder ausgebaut hat. Ein Schrittwechsel tauscht **nur**, was sichtbar ist; gespeichert wird weiterhin ausschließlich vom Feld in den Store. Und: Nur der sichtbare Schritt darf im DOM stehen, sonst stehen Felder doppelt.

**Fertig wenn:** Von «Einrichten» bis «Lauf läuft» kommt man ohne zu scrollen und ohne einen Reiter zu suchen; jede heutige Einstellung ist weiterhin erreichbar; ein Lauf lässt sich nach wie vor nach drei Entscheidungen starten; `test_web_start_flow.py` und `test_web_rail.py` bleiben grün. — **Gemessen:** Der Einstieg passt bei 1280 × 720 ohne Bildlauf auf den Schirm (Inhalt 664 px in 664 px, letzter Weg endet bei y = 508). `test_web_wizard.py` hält den Einstieg jetzt mit fest: drei Wege, kein Eingabefeld darin, jeder Weg auf **jedem** Schritt im DOM, keine doppelte ID mit Einstieg und Schritt im selben Baum, und je Weg genau ein geschriebenes Feld.

---

---

#### Stufe D — Nichts tritt aus seiner Box ✅ erledigt 2026-08-28

**Befund (Manu am Bild, 2026-08-28).** Zwei Sorten von Schlamperei, die ein Kunde vor jeder Funktion sieht: Text, der aus seinem Kasten tritt oder den Nachbarn überlappt, und Haken, die nicht dort sitzen, wo sie hingehören. Beides war belegbar — «Standard-Ausgangslage» sprengte seine Kachel, und der Haken einer 137 px hohen Auswahlkarte saß bei 12 % ihrer Höhe.

**Was zu tun ist:** Beides an der Ursache beheben statt an der Fundstelle, und mit einem Wächter versehen, der die *Größen* prüft, aus denen die Pixel entstehen — Pixel selbst kann eine Testsuite ohne Browser nicht messen.

**Erledigt:**

- **Werte bleiben in ihrer Kachel.** `metric_tile` bekam eine Textfassung (`prose=True`); dazu zwei Regeln, die allgemeiner greifen: `af-tile__value` mit `overflow-wrap: anywhere` und `af-grid > * { min-width: 0 }`. Letzteres war das Wirksamste — ein Durchlauf über den Einrichten-Bereich meldete vorher **62** Stellen mit waagerechtem Überlauf, danach **null**.
- **Haken sitzen richtig.** Auf einer Auswahlkarte mittig (gemessen 0 px Abweichung bei jeder Kartenhöhe), in einer Liste an der ersten Textzeile (1 px). Beides steht mit Begründung im Stylesheet.
- **Die Falle dahinter ist zu.** `labelStyle` wirkt seit Dash 4 nicht mehr; die toten Stildicts sind entfernt, und `tests/test_web_controls.py` macht ihre Rückkehr zu einem roten Test.

**Der Wächter kam am 2026-08-28 nach — mit der Entscheidung, die er brauchte.** Playwright steht jetzt im Extra `ui`, nicht in `dev`: `tests/test_web_overflow.py` öffnet jede Ansicht in einem Kopflos-Browser, und ohne Paket oder ohne Browser überspringt er sich. Die CI bleibt damit ohne Browser grün — kein `--deselect`, ein `skip` mit Begründung; die Zeile dazu steht im Workflow. Gemessen werden zwei Breiten (1280 und 1024) über alle vier Bereiche, alle acht Schritte des Einrichtens und alle sechs Ergebnis-Ansichten, dazu die grobe Probe ohne Ausnahmen: Die Seite selbst darf sich nicht waagerecht schieben lassen. Laufzeit rund vier Minuten (mit den Messungen aus W5.4 und W5.5 inzwischen rund zwölf).

**Der Detektor war die eigentliche Arbeit — und er hat sich beim ersten scharfen Durchlauf selbst korrigiert.** Die drei Ausnahmen aus [P1.8](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt) waren richtig, aber nicht vollständig; zwei weitere kamen aus echten Fehlalarmen dazu:

- **SVG.** In den Plotly-Diagrammen meldete jede Achsenbeschriftung 4 bis 27 px Überlauf. `clientWidth` ist für SVG-Elemente nicht definiert und liefert 0 — die Differenz war die Textbreite selbst.
- **`scrollWidth` selbst.** Die Ausnahme «absichtlich Überstehendes» auf den *Kasten* anzuwenden genügt nicht: Ein ausgeschwebtes Kind zählt weiterhin in den `scrollWidth` seines Vorfahren. Dashs eigenes Dropdown legt ein 241 px breites, unsichtbares Fokusziel in einen 96 px breiten Wrapper; die Zeitleiste meldete daraufhin 145 px Überlauf, obwohl nichts zu sehen war und nichts verrutschte. Gemessen wird deshalb nicht `scrollWidth`, sondern die rechte Kante dessen, was wirklich **im Fluss** steht — die Kästen der Kinder und die Zeilen der Textknoten. **Eine Ausnahme, die nur den Kasten kennt und nicht seine Nachkommen, ist keine.**

Damit der Wächter nicht aus dem falschen Grund grün ist — die Lehre aus P1.8 —, erzeugt `test_the_detector_would_notice_a_relapse` einen echten Überlauf und alle fünf Phantome daneben und prüft beides. Zusätzlich am laufenden System gegengeprobt: Ein langer unzerbrechlicher Wert in einer Kachel, deren `min-width`-Schutz entfernt wurde, wird mit 542 px gemeldet — also genau die Form, mit der «Standard-Ausgangslage» seine Kachel gesprengt hat.

**Ergebnis des ersten vollständigen Durchlaufs: alle Ansichten bei null.**

**Offen — und bewusst woanders:**

- **Das Auswahlfeld «Art der Änderung» in den Regelzeilen** (Schritte 4 und 5) tritt 68 px aus seiner Spalte — der Optionstext «springt auf den Wert (set)» ist breiter als die Zelle. Ein Versuch mit `min-width: 0` auf Dashs Wrapper half nachweislich **nicht** und wurde wieder entfernt, statt als wirkungslose Regel stehenzubleiben. Vorbestehend; gehört zum Umfang der Regelzeilen und damit zu [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30). **Der Wächter meldet ihn nicht** — Schritte 4 und 5 sind bei beiden Breiten auf null. Warum, ist nicht nachgemessen; naheliegend ist Ausnahme 1, weil Dashs Auswahlfeld seinen Text mit `overflow: hidden` abschneidet. Das ist keine Entwarnung, sondern die Grenze dieses Wächters: Abgeschnittener Text sieht schlecht aus, ohne den Nachbarn zu schieben. Wer P1.2 anfasst, sieht dort mit eigenen Augen nach.

**Fertig wenn:** Keine Ansicht meldet waagerechten Überlauf, und ein Wächter fängt den Rückfall, statt dass es beim nächsten Blick auffällt. — **Erfüllt.**

---

**Was die Zahlen macht: nichts.** Das ganze Paket fasst Darstellung und Wegführung an — kein Rechenpfad, keine Config, kein Artefakt. `vergleiche.md` bleibt unberührt.

---

### P1.8 — Gegenprobe zu P1.7 (Haiko, 2026-08-28) ✅ erledigt

P1.7 wurde am laufenden System nachgemessen. **Die tragenden Zusagen halten:** die Schrittfolge zeigt nur den aktuellen Schritt (keine doppelte Dash-ID auf keinem der acht — 116, 267 und 115 IDs, alle eindeutig), «Weiter» ist auf jedem Schritt ohne Scrollen sichtbar, jeder Schrittwechsel setzt die Ansicht auf 0, die Zieh-Griffe halten ihre Grenzen (220 px unten, 32 % oben), überleben einen Neuladen und stellen sich per Doppelklick zurück, und die neuen Bausteine tragen im Dark Mode Kontraste zwischen 7,2 und 16,8.

**Drei Befunde, alle behoben.**

1. **Der Start aus der Schrittfolge wechselte den Bildschirm nicht.** Stufe B sagt zu: «Ein Start wechselt sichtbar den Bildschirm; während des Laufs ist von der Einrichtung nichts mehr zu sehen.» Das galt für den Knopf im Bedienfeld — von dort ist man bereits auf dem Leitstand. **Stufe C hat danach den Knopf am Ende der Schrittfolge ergänzt und damit den Hauptweg dorthin verlegt**, ohne das Kriterium erneut zu prüfen: Über sechs Messpunkte blieb die Adresse auf `/app/`, der Fokus-Modus aktiv und das Formular vollflächig sichtbar, während die Kopfzeile «Simulation läuft» meldete und der Balken auf 70 % stieg. `_start` führt jetzt nach `routing.url(running.leitstand_route())`; gemessen wechselt die Adresse nach 0,53 s, das Formular ist weg. **Dieselbe Klasse wie die Nachträge zu P1.1 und P1.5** — ein Kriterium, das bei seiner Formulierung stimmte und durch eine spätere Stufe still falsch wurde.
2. **Eine Lücke von 1,7 s, in der Kopfzeile und Bildschirm sich widersprachen.** Die Kopfzeile meldete «Simulation läuft» nach 2,2 s, der Ladebildschirm erschien nach 3,91 s; dazwischen zeigte die Mitte die Szene des **vorigen** Laufs. Ursache: Der Ladebildschirm hing allein an `PROGRESS_STORE`, und den leert `_start` — gefüllt wird er erst, wenn die Simulation ihre erste Tick-Zeile schreibt. Er hängt jetzt zusätzlich am Laufzustand; ohne Zahlen zeigt er einen **unbestimmten** Balken, keine erfundene Prozentzahl (Invariante 1). Gemessen: Ladebildschirm nach 1,98 s, kein Widerspruch mehr.
3. **Ein Text im Produkt zeigte auf einen Abschnitt, den es nicht mehr gibt.** Die Karte «Eigene Einstellungen» beschrieb sich mit «Was weiter unten unter **Alle Einstellungen** eingestellt ist» — den Abschnitt hat P1.7 in die Schritte 4 bis 7 aufgelöst. Dasselbe in `erste-simulation.md`, `presets.md` und `lauf-konfigurieren.md`; letzteres widersprach sich zusätzlich in zwei aufeinanderfolgenden Absätzen (erst «Bedienfeld tritt zurück», dann «bleibt sichtbar, während Sie hier einstellen» — seit dem Fokus-Modus falsch).

**Ein Wächter war aus dem falschen Grund grün.** `test_web_layout.py::test_the_setup_area_builds_with_the_default_draft` prüfte auf die Zeichenkette «Alle Einstellungen». Die stand seit P1.7 nur noch in der Beschriftung einer Preset-Karte — der Abschnitt selbst war längst weg. Erst die Korrektur des Kartentexts hat den Test rot gemacht. **Ein Wächter, der aus dem falschen Grund grün ist, ist schlechter als keiner:** Er wiegt in Sicherheit. Er prüft jetzt die Schrittfolge selbst.

**Ein Befund, der sich unter der Messung aufgelöst hat — protokolliert, weil der Weg dahin lehrreich ist.** Ein erster Durchlauf meldete **41, 32 und 2** überlaufende Elemente in den Schritten 4, 5 und 7 und schien Stufe D deutlich zu erweitern. Die Zahlen waren falsch, und zwar dreifach: Der Detektor zählte (a) Inhalte, die `overflow: hidden` sauber abschneidet, (b) Inhalte in **zugeklappten** `<details>`-Blöcken, die gar nicht gezeichnet werden, und (c) Tooltips, die an einem 16-px-Reglerknopf hängen und definitionsgemäß über dessen Kasten hinausragen. Mit einem Detektor, der nur zählt, was wirklich gezeichnet wird und die Zone verlässt, sind **alle acht Schritte bei null**. Zwei bereits geschriebene Korrekturen (Auswahlfelder abschneiden, Reglerbeschriftung abschalten) wurden deshalb **wieder zurückgenommen**, statt als Fix ohne Befund stehenzubleiben. **Als Prüfmuster mitnehmen:** Ein Überlauf-Wächter, der `scrollWidth > clientWidth` allein auswertet, meldet Phantome — er muss abgeschnittene, eingeklappte und absichtlich überstehende Inhalte ausnehmen. Das gehört in die Anforderungen des Wächters, den Stufe D noch schuldet.

**Was die Zahlen macht: nichts.** Nur Wegführung und Text.

**Doku zieht mit:** `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/erste-simulation.md`, `docs/handbuch/presets.md`.

**Verfahren nachgeschärft am 2026-08-28.** Das Ergebnis dieser Gegenprobe bleibt gültig — alle drei Befunde waren echt und sind behoben. Der **Prüfumfang** war zu eng: Geprüft wurden die drei gemeldeten Befunde und die Mechanik (keine doppelte ID, «Weiter» sichtbar, Scroll auf 0, Kontraste). **Gemessen wurde keine der Zusagen selbst.** «Eine Frage auf dem Schirm» steht als Zusage in `wizard.py` und in P1.7 — hätte die Gegenprobe die Höhe jedes Schritts in Bildschirmen genommen statt seinen waagerechten Überlauf, wäre Befund 3 aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28) hier aufgefallen und nicht erst zwei Tage später. Als Regel festgehalten: **Eine Gegenprobe prüft nicht die gemeldeten Befunde, sondern die zugesagten Größen** — die Befunde sind der Anlass, nicht der Umfang.

**Abgrenzung.** Die 90 Eingabefelder unter «Systemgrößen» werden hier **umsortiert, nicht reduziert** — ihre Menge ist ein eigener Fall und bleibt bei [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30). Ebenso bleibt offen, dass der Preflight bei jeder Änderung den vollen `SimulationState` aufbaut.

**Umgesetzt am 2026-08-28, in drei Commits entlang der Stufen.** Vier Dinge, die dabei über den Plan hinausgingen — drei davon Fallen, die erst am laufenden System sichtbar wurden:

- **Ein fehlender `Input` legt den ganzen Callback lahm.** Dash führt ihn **gar nicht erst aus** und meldet nur in der Browserkonsole «A nonexistent object was used in an `Input`». «Direkt zum Start» wurde auf Schritt 1 nicht gerendert — und damit tat auch «Weiter» nichts, der Zähler blieb bei «Schritt 1 von 8». Bedingt sichtbare Bedienelemente werden seither **ausgeblendet, nicht weggelassen**; das ist jetzt die sechste Dashboard-Regel in `CLAUDE.md`. Aus demselben Grund stehen «Lauf starten» und «Als Szenario speichern» in der Navigationsleiste und nicht im letzten Schritt.
- **Ein klebendes Element braucht Spielraum in seinem Elternkasten.** «Weiter» trug `position: sticky` und lag trotzdem bei y=1381 in einem 900-px-Fenster — sein Wirt war exakt so hoch wie es selbst. Das Kleben sitzt jetzt am Wirt, dessen Eltern die volle Höhe haben; gemessen y=842, ohne Scrollen sichtbar.
- **`labelStyle` wirkt seit Dash 4 nicht mehr.** Der erste Versuch, den Haken auf einer Auswahlkarte mittig zu setzen, blieb folgenlos: Dash schreibt keinen Inline-Stil mehr aufs Label (`getAttribute("style")` ist `null`). Die Stildicts in `components.py` waren tot und sind entfernt — stehengeblieben wären sie eine Falle für den Nächsten. Dieselbe Klasse wie Dashs `--Dash-*`-Ebene in P1.5.
- **Der Fokus-Modus kam aus der Benutzung, nicht aus dem Plan.** Der Plan sagte nur «Schrittfolge»; am Bildschirm zeigte sich, dass daneben eine Szene läuft, die einen *anderen* Lauf zeigt, und links Stand-Zeilen stehen, die wiederholen, was man gerade einstellt. `af-shell--focus` blendet beim Einrichten Bedienfeld, Telemetrie und Zeitleiste aus.

**Am laufenden System durchgespielt:** alle acht Schritte vorwärts, Sprung über die Schrittliste, «Direkt zum Start» ab Schritt 3 nach Schritt 8, Start aus der Schrittfolge (Kopfzeile «Simulation läuft», Fortschrittsfenster «Tick 30 von 500»). Überlauf-Durchlauf je Schritt: Schritte 1–3 und 6 ohne Befund.

**Offen und benannt:** In den Regelzeilen (Schritte 4 und 5) tritt das Auswahlfeld «Art der Änderung» 68 px aus seiner Spalte — der Optionstext «springt auf den Wert (set)» ist breiter als die Zelle. Ein Versuch mit `min-width: 0` auf dem Dash-Wrapper half nachweislich **nicht** und ist wieder entfernt statt als wirkungslose Regel stehengelassen. Vorbestehend, gehört zum Umfang der Regelzeilen und damit zu [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30).

**Doku zieht mit:** `CLAUDE.md` (Architektur-Map: neue Module und Routen; die Dashboard-Regeln um den Umgang mit der Schrittfolge ergänzen), `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`, `docs/handbuch/glossar.md` (Ladebildschirm, Fortschrittsfenster, Schrittfolge), `README.md` und `dashboard/README.md` (Routentabelle).

---

### P1.9 — Der Assistent richtet ein Experiment ein ✅ erledigt 2026-08-30 (Audit 2026-08-28)

**Herkunft:** Unabhängiges Audit des Einrichten-Assistenten am 2026-08-28, gemessen an einer eigenen Instanz bei 1280 × 720 und gegengelesen im Code. Vollfassung mit allen Messwerten: [`wizard_audit_2026-08-28.md`](wizard_audit_2026-08-28.md). Das Audit hat die Abnahmekriterien dieses Plans **bewusst nicht** als Maßstab genommen, sondern eigene — und genau dadurch gefunden, was die Kriterien durchgelassen haben.

**Befund in einem Satz:** Der Assistent ist ein Modell-Editor mit einem Experiment-Assistenten davor. Weil beides in derselben Schrittfolge steht, kann er weder das eine ruhig noch das andere schnell.

**Die vier tragenden Befunde:**

1. **Der Assistent beschreibt einen Lauf, der nicht stattfindet** (kritisch). [`run_single_sweep`](../src/orchestration/scenario_sweeps.py) baut seinen Runner selbst und schreibt `deterministic_only=True`, `seed=SWEEP_SEED` und `checkpoint_interval=0` fest — und ruft trotzdem `OllamaClient` für den Szenario-Text. Vom Entwurf erreicht **genau ein** Feld den Sweep-Lauf: `rounds`, als `ticks_override` ([`run_launcher.py:209`](../dashboard/run_launcher.py)). Gemessen sagt Schritt 8 nach «Szenario-Vergleich starten» wörtlich: «ausgehend von der Standard-Ausgangslage aus `configs/`, ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind Platzhalter» — drei Aussagen, drei Mal falsch. Dazu sechs Kacheln, die den Entwurf zeigen statt den Lauf. **Das ist Invariante 1 auf der Oberfläche verletzt:** Was der Code nicht tut, darf die Oberfläche nicht behaupten — und die Oberfläche ist die Doku, die tatsächlich gelesen wird.
2. **Fünf Bedienelemente in «optionalen» Schritten schreiben ohne Rückfrage in `configs/properties.json`** (kritisch). «Entfernen» an einem Segment, «Größe dauerhaft löschen», «Als Standard speichern», «Bevölkerung als Standard speichern», «Größe anlegen» — alle in `_handle_action` ([`config_editor/__init__.py`](../dashboard/web/config_editor/__init__.py)), alle ohne Dialog, ohne Undo, ohne Sicherung. Die Wirkung reicht über den Lauf, die Sitzung und den Nutzer hinaus. Kein Bedienfehler, sondern ein Kategorienfehler.
3. **Kein einziger der acht Schritte passt auf einen Bildschirm** (hoch). Gemessen bei 1280 × 720, sichtbare Höhe 664 px: 2,15 / 1,13 / 1,18 / **3,37** / **4,44** / 2,42 / 2,21 / 1,20 Bildschirme. Schritt 4 trägt 104 Bedienelemente unter der Überschrift «Rahmenbedingungen — bereits sinnvoll vorbelegt», Schritt 5 deren 64. Die vier mittleren Schritte sind erkennbar die alten Reiter unter neuem Namen; ihre Modulköpfe sagen es selbst («Tab «Rahmenbedingungen»»).
4. **Die Schrittliste lügt, und «Weiter» garantiert nichts** (hoch). `_rail_entry` vergibt den Zustand rein nach Position — gemessen nach «Szenario-Vergleich starten»: `["done","done","done","done","done","done","done","current"]`, also sieben Häkchen für nie gesehene Schritte. `_navigate` prüft nichts, «Weiter» ist nie gesperrt, «Lauf starten» nur während eines Laufs. Ein Wizard unterscheidet sich von einer Reiterleiste dadurch, dass «Weiter» etwas garantiert.

**Die Kriterien waren grün — schon wieder.** P1.7 hat zugesagt: eine Frage auf dem Schirm. Abgenommen wurde: nur der offene Schritt steht im DOM. Das ist erfüllt und misst Knoten statt Bildschirme. **Es ist derselbe Fehlertyp, den P1.6 an P1.1 und P1.5 gefunden und ausdrücklich als Prüfmuster notiert hat** — ein Paket später, mit demselben Ergebnis. Zweimal derselbe Fehler ist kein Zufall mehr, sondern eine Lücke im Verfahren; daraus folgt Regel 7 des Commit-Regelwerks unten.

#### Was wieder aufgemacht wird

> **Nachtrag 2026-08-30: alle vier Positionen sind geschlossen.** P1.9 ist vollständig, damit gelten P1.1 und P1.7 wieder als erledigt; das ergänzte Kriterium von P1.5 ist eingelöst (für Schrittfolge **und** Bereichswechsel), und P1.3 ist im vorgezogenen Umfang gebaut. **Nicht** gebaut wurde P3.6 — der Vertrag, dessen Fehlen W1.1 begründete, steht seit W1.1 als `FESTLEGUNGEN`/`UNBEACHTET` in `scenario_sweeps.py`; die allgemeine Fassung bleibt in Phase 3 und ist dort nicht mehr dringlich.

| Paket | Entscheidung | Begründung |
| --- | --- | --- |
| [P1.1](#p11--simulation-starten-neu-bauen--erledigt-2026-08-28) ✅ | **wieder öffnen** | «Drei Entscheidungen genügen» ist erfüllt und misst das Falsche: Auf dem Sweep-Pfad sind zwei der drei wirkungslos. Zählen ersetzt nicht Wirksamkeit. |
| [P1.5](#p15--leitstand-oberfläche--erledigt-2026-08-28) ✅ | **Abnahme ergänzen** | Zonen, Theme und Zeitleiste tragen. Es fehlt eine Barrierefreiheits-Größe in den Kriterien. Kein inhaltlicher Rückbau. |
| [P1.6](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28) ✅ | **bleibt** | Das Prinzip trägt und ist die Grundlage für den Schnitt unten. |
| [P1.7](#p17--der-ablauf-wird-die-oberfläche--erledigt-2026-08-28) ✅ | **wieder öffnen** | «Eine Frage auf dem Schirm» ist nicht gehalten (Befund 3), dazu Befund 4 und die Handwerksbefunde. |
| [P1.8](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt) ✅ | **Verfahren nachschärfen** | Das Ergebnis bleibt gültig, der Prüfumfang war zu eng: Die Gegenprobe hat drei gemeldete Befunde geprüft, aber keine der Zusagen **gemessen**. Genau die Messung hätte Befund 3 gefunden. |
| [P1.3](#p13--szenariogestaltung-neu-denken--erledigt-2026-08-30-datenschema-die-entstehung-bleibt-p20) | **vorziehen** | Der Sweep-Pfad ist die Ursache der Befunde 1 und 2. Ihn kosmetisch zu reparieren, ohne die Szenariogestaltung zu klären, wäre doppelte Arbeit. |
| [P3.6](#p36--stabiler-vertrag-für-den-run-launcher--erledigt-2026-09-05) | **vorziehen** | Befund 1 ist im Kern ein fehlender Vertrag zwischen Assistent, Run-Launcher und Sweeps. Ohne ihn lässt sich die Zusage aus W1.3 nicht mechanisch halten. |

Unangetastet bleiben [P1.2](#p12--ergebnisse-und-plots-refactoren--erledigt-2026-08-30) und [P1.4](#p14--landingpage-produktionsreif--erledigt-bis-auf-die-rechtstexte-2026-08-30) — sie liegen hinter diesem Schnitt.

#### Die tragende Entscheidung: zwei Werkzeuge statt eines

> **Der Assistent richtet ein Experiment ein. Der Modell-Editor pflegt das Modell. Es sind zwei Orte, und nur einer davon schreibt in `configs/`.**

Daraus folgt: Der Assistent schrumpft auf das, was ein Experiment ausmacht — Ausgangspunkt, Umfang, Rechenmodus, Identität, Prüfung, Start; fünf bis sechs Schritte, jeder auf einem Bildschirm. Die 168 Bedienelemente der heutigen Schritte 4 und 5 ziehen in den Modell-Editor, mit Fläche, mit sichtbarem Delta und mit bestätigter Speicherung. Befund 2 fällt damit **strukturell** weg und nicht durch einen Bestätigungsdialog. Und «Schritt n von m» wird wieder wahr, weil alle Schritte vergleichbar groß sind.

**Diese Entscheidung ist vor dem ersten Arbeitspaket zu treffen.** Ohne sie sind W3 und W4 nicht umsetzbar, und alles andere wäre Verschieben von Feldern.

#### Arbeitspakete

Reihenfolge ist Absicht: erst messen, dann die Unwahrheiten, dann der Schnitt, dann das Fehlende, zuletzt das Handwerk. **Jedes Paket ist genau ein Commit** (Regelwerk unten).

**W0 — Messfundament, vor jedem Umbau.** Ohne diese beiden wiederholt sich der Fehler von P1.7: eine Zusage, die von einer Zählung bewacht wird statt von einer Messung.

**Zur Geometrie, abweichend vom ersten Entwurf dieses Pakets:** Gemessen wird bei **1280 × 800 und 1024 × 800** und nicht bei 1280 × 720 und 1440 × 900. Grund ist der Preis: `test_web_overflow.py` besucht diese beiden Breiten bereits, und jede weitere Geometrie kostet einen vollständigen Browser-Durchlauf über acht Schritte und sieben Ansichten. Die Zahlen fallen dadurch niedriger aus als im Audit (1,01 bis 4,03 statt 1,13 bis 4,44) — derselbe Inhalt, mehr Fenster. **Die Aussage bleibt in beiden Messungen dieselbe: kein einziger Schritt kommt ohne Scrollen aus.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W0.1 ✅ | Höhenwächter je Schritt in `tests/test_web_overflow.py`, gemessen in Bildschirmen. | **Erledigt 2026-08-28.** Der Wächter hält den Ist-Stand je Breite und Schritt und schlägt an, sobald ein Schritt **wächst** — und ebenso, wenn einer um mehr als 0,25 Bildschirme **schrumpft**, ohne dass der Deckel mitgezogen wird. Deckel wird in W3.5 auf `ZIEL = 1.0` gesenkt. — **Nachgezogen 2026-08-30:** Dazu ist es nicht gekommen. W3.5 hat vier der sieben Schritte auf 1,00 gebracht und für die übrigen drei entschieden, den Ist-Stand zu halten; `ZIEL` steht weiterhin als Zahl daneben. |
| W0.2 ✅ | Wirkungstest: welche Draft-Felder erreichen auf welchem Startpfad (Einzellauf, Wiederholungen, Sweep) tatsächlich die Simulation. | **Erledigt 2026-08-28** in `tests/test_web_wirkung.py`. «Wirksam» heißt dort: *es ändert, was bei der Simulation ankommt* — gemessen als Unterschied zwischen zwei Läufen desselben Pfads, einmal mit und einmal ohne das Feld. Eine Definition ohne Annahmen über den Code. |

**Zwei Befunde, die erst diese Messung ans Licht gebracht hat** — beide standen nicht im Audit, weil sie sich am Bildschirm nicht zeigen:

* **Der Startpreis geht unterwegs verloren.** `build_custom_sweep_from_draft` wertet `base_price` korrekt aus — es kommt dort nur nie an. `launch_from_draft` schickt den Entwurf durch `RunLaunchConfig`, und diese Datenklasse hat **kein solches Feld**; der Wert fällt auf der Rundreise `draft_to_launch_config` → `launch_config_to_draft` lautlos heraus. «Startpreis selbst festlegen» im Assistenten ist über das Dashboard **wirkungslos**, über die CLI nicht. Neues Paket **W1.5**.
* **`use_seed` ohne `seed` stürzt ab.** `draft_to_launch_config` rechnet `int(draft.seed)`, sobald der Schalter an ist — bei `seed = None` ein `TypeError` statt eines Prüfbefunds. Heute unerreichbar, und zwar aus dem schlechtesten denkbaren Grund: Befund A7 schreibt beim Anzeigen von Schritt 3 stillschweigend `seed = 42`, bevor jemand den Schalter finden kann. **W5.1 räumt A7 weg und macht diesen Absturz damit erreichbar** — wer W5.1 umsetzt, fasst diese Zeile mit an. Aufgenommen als **W1.6**.

**W1 — Der Assistent sagt die Wahrheit** (kritisch, zuerst).

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W1.1 ✅ | **Entschieden am 2026-08-28 (Haiko): der Pfad deklariert seine Fixierungen.** Nicht die andere Möglichkeit — ein Vergleich rechnet alle Szenarien unter gleichen Bedingungen, sonst vergleicht er sie nicht. Falsch war nie die Festlegung, sondern ihr Schweigen. | **Erledigt 2026-08-28.** `scenario_sweeps.FESTLEGUNGEN` (drei Werte, die der Sweep einsetzt) und `UNBEACHTET` (sieben Felder, die er ignoriert) sind **die Quelle des Verhaltens**: `run_single_sweep` liest seinen Runner daraus, statt Literale zu tragen. `tests/test_web_wirkung.py` schließt den Kreis in beide Richtungen — was verworfen wird, steht im Vertrag, und was im Vertrag steht, wird verworfen. Damit ist «still verworfen» mechanisch ausgeschlossen. **Was der Nutzer davon sieht, kommt mit W1.3.** |
| W1.2 ✅ | `ticks_override` nur bei bewusst gewählter Länge; sonst gilt die `max_ticks` des Presets. | **Erledigt 2026-08-28.** Die Frage, woran man «bewusst gewählt» erkennt, hat der Entwurf nicht beantwortet — 40 ist ein Vorgabewert, kein Wunsch. Die CLI hat das Signal (`--ticks` steht auf `None`, bis jemand es angibt) und behält den Weg; das Dashboard gibt ihn auf. **Gemessene Wirkung:** Vier der acht Presets sind auf 50 Ticks angelegt und liefen auf 40; drei davon verloren dabei ihren End-State-Meilenstein. |
| W1.3 ✅ | Der Preflight beschreibt den **tatsächlichen** Lauf. | **Erledigt 2026-08-28.** Beim Vergleich ein eigener Satz, vier eigene Kacheln (Szenarien, «40–50 Ticks je Szenario», «Nur Zahlen · vorgegeben», «42 · vorgegeben») und ein aufklappbarer Block, der jede Vorgabe begründet. **Die Begründungen kommen aus dem Vertrag**, nicht aus der Oberfläche — sonst gäbe es zwei Quellen für dieselbe Aussage. Mitgezogen sind die beiden Stellen, die dieselbe Behauptung in der Nachbarzone aufstellten: die drei Stand-Zeilen des Bedienfelds und die Kopfzeile. Genannt ist auch, was der Vertrag nicht abdeckt: Für den Abschlusstext wird Ollama gerufen, auch bei «ohne Sprachmodell». |
| W1.4 ✅ | Der Weg «Szenario-Vergleich» führt nicht mehr an der Längenfrage vorbei. | **Mit W1.2 erledigt, aber andersherum als geplant** — und das ist ehrlicher: Das Paket wollte die Frage in den Weg stellen. Nach W1.2 gibt es sie für den Vergleich gar nicht mehr, weil er die Antwort nicht verwendet. Das Kriterium («kein Startpfad überspringt eine Frage, deren Antwort er verwendet») ist damit erfüllt, ohne dass ein Schritt dazukommt. `ERWARTET[SWEEP]` ist leer: Der Vergleich nimmt vom Entwurf **nichts** entgegen. |
| W1.5 ✅ | `base_price` erreicht den Lauf auch über das Dashboard. | **Erledigt 2026-08-28** als Feld in `RunLaunchConfig`, in **beiden** Richtungen verdrahtet. Dazu ein Wächter über die ganze Fehlerklasse statt über diesen einen Fall: `TestDieRundreiseVerliertNichts` schickt **jedes** Feld des Entwurfs durch `RunLaunchConfig` und meldet, was dabei herausfällt. Eine geduldete Ausnahme bleibt, benannt statt unsichtbar — der tote Schalter `sweep_batch_deterministic`, den kein Launcher liest (gehört zu P5.1). |
| W1.6 ✅ | `use_seed` ohne `seed` ergibt einen Prüfbefund, keinen `TypeError`. | **Erledigt 2026-08-28.** `validate_draft` prüft das **vor** dem Bauen des States und hängt den Befund ans Feld `seed`, wo man ihn beheben kann. Ein Test stellt zusätzlich nach, dass der Absturz ohne diese Prüfung wirklich stünde — eine Meldung allein belegt nicht, dass sie nötig war. Die Sperre für W5.1 ist damit weg. |

**W1 ist damit abgeschlossen** (W1.1 bis W1.6, davon zwei erst durch W0.2 gefunden). Der Assistent beschreibt auf allen drei Startpfaden den Lauf, der wirklich stattfindet, und verwirft nichts mehr stillschweigend.

**W2 — Der Assistent lügt nicht über den Fortschritt.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W2.1 ✅ | Zustände in der Schrittliste, die nicht mehr an der Position hängen. | **Erledigt 2026-08-28 — vier statt der geplanten drei.** «Nicht besucht» allein hätte den Befund abgestellt, beantwortet aber nicht die Frage, die man am Ende hat: *Habe ich etwas übergangen?* Ein Schritt, der noch kommt, und einer, an dem man vorbeigesprungen ist, sahen sonst gleich aus. Dazu die Zahl unter der Liste, und `aria-current="step"` als Vorgriff auf W5.3 — diese Funktion vergibt gerade die Zustände, sie später ein zweites Mal aufzuschlagen wäre Arbeit ohne Ertrag. |
| W2.2 ✅ | Validierungstor an «Weiter» und «Lauf starten». | **Erledigt 2026-08-28.** Zwei Tore mit zwei verschiedenen Regeln: «Weiter» sperrt **nur** in dem Schritt, in dem der Befund behoben werden kann — sonst stünde man auf Schritt 1 fest wegen eines Modellnamens aus Schritt 7, eine Sackgasse statt einer Führung. «Lauf starten» sperrt bei **jedem** Befund und nennt den Schritt. Die Zuordnung Feld→Schritt (`FELD_SCHRITT`) ist eine Tabelle, aber eine **bewachte**: Ein Test rendert jeden Schritt, liest heraus, welche Felder er zeigt, und meldet jede Zeile, die nicht mehr stimmt. |
| W2.3 ✅ | «Zurück» folgt einem Navigationsverlauf statt `current - 1`. | **Erledigt 2026-08-28.** Am laufenden System nachgestellt: Vergleich → Schritt 8 → «Zurück» → Einstieg (vorher «Technik»); Sprung von 1 auf 7 → «Zurück» → Schritt 1 (vorher 6). Der gerade Weg bleibt unverändert — 1 → 2 → 3 und zurück ergibt weiterhin 2, 1, Einstieg. Ein leerer Verlauf führt auf den Einstieg: keine Notlösung, sondern die einzige Antwort, die keine Sackgasse ist. |

**W2 ist damit abgeschlossen.** Die Schrittfolge behauptet keinen Fortschritt mehr, den es nicht gab, «Weiter» garantiert wieder etwas, und «Zurück» führt dorthin, wo man war.

**W3 — Der Schnitt.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W3.1 ✅ | Modell-Editor als eigener Bereich; `macro` und `micro` ziehen dorthin um. | **Erledigt 2026-08-29.** Die Schrittfolge fällt von acht auf **sechs** Schritte, der neue Bereich trägt gemessene **168** Bedienelemente. Reiner Umzug: Die beiden Module sind unverändert, nur ihr Anzeigeort ist neu. Der Höhenwächter hat beim Umnummerieren des Deckels einen Fehler gefangen — für Schritt 4 war die Zahl aus dem Audit (720 px Fensterhöhe) statt die des Wächters (800 px) eingetragen. |
| W3.2 ✅ | Schreiben ins **Modell** nur noch im Modell-Editor, nur mit Bestätigung und mit Anzeige der Reichweite. | **Erledigt 2026-08-29.** Die Zusage ist präzisiert: kein Schreibpfad **ins Modell** — «Als Szenario speichern» legt unter `configs/sweeps/` ab und bleibt in der Schrittfolge, weil das die Ablage des Experiments ist und nicht das Modell. Sechs Schaltflächen stehen jetzt hinter einer Rückfrage, die Reichweite steht in jeder von ihnen und im Hinweis darunter, aus **einer** Quelle (`controls.REICHWEITE`). **Der Wächter prüft die Wirkung, nicht die Namen:** Er ersetzt die schreibenden Funktionen und ruft jede Aktion des Assistenten auf — wer eine neue schreibende Aktion hinzufügt und sie in keine Liste einträgt, fällt trotzdem auf. Beide Richtungen sind nachgestellt. |
| W3.3 ✅ | Die Faktorlage als **eine** Frage im Assistenten — sie gehört zum Experiment, nicht zum Modell. | **Erledigt 2026-08-29** als Schritt 4 «Ausgangslage» (`factors.py`). **Das Abnahmekriterium ist nur zur Hälfte erfüllt, und das steht hier so:** Sieben Auswahlen ja — ein Bildschirm nein. Gemessen **1,46** (1280 px) und **1,49** (1024 px). Der Rest sind die sieben Leitfragen unter den Feldern; sie wegzulassen machte den Schritt kürzer und die Auswahl unverständlich. Die Entscheidung gehört zu W3.5, wo der Deckel für **alle** Schritte auf 1,0 fällt — hier vorwegzunehmen hieße, sie ohne den Vergleich mit den anderen sechs zu treffen. Zum Vergleich: Der Schritt, aus dem die Faktoren kommen, brauchte 3,0. **Über den Wortlaut hinaus ist der Schalter «Eigene Werte anwenden» mitgekommen** — er entscheidet, ob die Auswahl auf diesem Bildschirm überhaupt wirkt. Bliebe er im Modell, zeigte der Schritt sieben Felder und daneben den Hinweis, dass man anderswo etwas einschalten muss, damit sie zählen. |
| W3.4 ✅ | Schritt 1: Kacheln mit Kennzahl, Beschreibung auf zwei Zeilen geklemmt. | **Erledigt 2026-08-29.** 1,92 → **1,41** (1280 px) und 2,05 → **1,53** (1024 px). Das Raster steht jetzt in **drei** Spalten statt zwei (`minmax` von 16 auf 14 rem), und alle Kacheln sind **gleich hoch** — vorher zwischen 88 und 264 px, je nach Länge der Beschreibung. Ein Raster mit ungleichen Zeilen lässt sich nicht überfliegen: Man liest zehn Absätze, statt zehn Möglichkeiten zu vergleichen. Der volle Text steht seither unter dem Raster, sobald ein Szenario gewählt ist.
**Das Kriterium «unter 1,0» ist nicht erreicht, und die Messung sagt auch, warum:** Von den 1049 px des Schritts entfallen nur noch **725 px auf den Inhalt** — das Raster selbst misst 468 px. Die übrigen **324 px sind Rahmen**: die Bereichsüberschrift «Lauf einrichten» samt Einführungssatz, die auf **jedem** Schritt steht, der leere Meldungsplatz und die Fußleiste. Der Rahmen kostet mehr als der Inhalt. Das ist kein Befund über Schritt 1, sondern über die Schrittfolge als Ganzes — und damit W3.5. |
| W3.5 ✅ | Deckel senken. | **Erledigt 2026-08-30 — mit einer Entscheidung statt mit einer Kürzung.** Die Schritte 2, 3, 6 und 7 stehen auf **1,00** — sie passen. Schritt 1 auf 1,20, Schritt 4 auf 1,28, Schritt 5 auf 1,31 (bei 1024 px 1,31 / 1,34 / 1,31).
**Was den Unterschied gemacht hat**, war nicht Sparsamkeit an einer Stelle: der Umzug der 168 Bedienelemente (W3.1), ein Rahmen ohne den auf jedem Schritt wiederholten Einführungstext (−116 px, W3.5), und eine Gliederungsebene weniger in den Schritten — «Technik» trug 307 px Überschrift, Einleitung und Doku-Verweis für **ein** Zahlenfeld, «Lauf & Ablage» 604 px für drei selten gebrauchte Abschnitte. Beide Schritte fielen dadurch von 1,97 bzw. 2,16 auf 1,00 bzw. 1,31.
**`ZIEL` bleibt bei 1,0, und der Deckel steht darüber** — der Wächter ist damit scharf gegen Wachstum, aber nicht auf dem Ziel. Die drei verbliebenen Schritte tragen Inhalt, der sich nur durch **Weglassen** kürzen ließe: zehn Szenarien mit Kennzahl, sieben Faktoren mit ihrer Leitfrage, die Benennung eines Laufs.

**Entschieden am 2026-08-30 (Haiko): der Deckel hält den Ist-Stand, das Ziel bleibt daneben stehen.** Das Weglassen ist den Tausch nicht wert — die zehn Szenarien ohne ihre Kennzahl sind zehn Namen, die sieben Faktoren ohne ihre Leitfrage sind sieben Fachbegriffe, und ein Lauf ohne Namen ist später nicht wiederzufinden. «Prüfen & Starten» ist zudem der Schritt, auf dem man ohnehin innehält; seine **1,45** sind mit den kürzeren Zeilen aus W5.4 bezahlt und dort begründet.

**Was diese Entscheidung nicht ist: ein Freibrief.** Die Sperrklinke bleibt in beide Richtungen scharf — wächst ein Schritt über seinen Deckel, wird es rot; schrumpft er um mehr als 0,25 Bildschirme, ohne dass der Deckel mitgezogen wird, ebenso. `ZIEL = 1.0` steht weiterhin daneben und sagt, wohin es ginge, wenn der Inhalt es je zuließe. |

**Stand von W3 (2026-08-30): abgeschlossen** (Entscheidung zu W3.5 am 2026-08-30). Die Schrittfolge ist von acht auf sieben Schritte gegangen, vier davon passen auf einen Bildschirm, und kein Schritt trägt mehr als 13 Bedienelemente. Der höchste stand nach W3 bei **1,31** und steht heute bei **1,45** — «Prüfen & Starten», gewachsen mit dem Lesemaß aus W5.4 und dort als bezahlt eingetragen. Für die drei Schritte über 1,0 ist entschieden, den Ist-Stand zu halten statt Inhalt wegzulassen.

**W4 — Was ein Experiment ausmacht.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W4.1 ✅ | Lauf-Identität nach vorn. | **Erledigt 2026-08-29.** Der **Name** steht jetzt auf «Prüfen & Starten» — dem einzigen Schritt, den **jeder** Startweg passiert. Er lag im optionalen Schritt «Lauf & Ablage», an dem drei von vier Wegen vorbeiführen; alle Läufe hießen deshalb gleich, genau wie der Text neben dem Feld es vorhersagte. Die **Fragestellung** bleibt dort: Sie ist ausführlich und gehört zur Dokumentation, nicht auf den Startbildschirm. Ein Knopf setzt einen Vorschlag aus Ausgangspunkt, Länge und Zeitpunkt — **als Handlung, nicht als Render-Rückfall** (das wäre Befund A7). Kosten: Schritt 7 wächst von 1,00 auf 1,13 Bildschirme; ein Lauf, den niemand benennen konnte, kostet später mehr. |
| W4.2 ✅ | Delta-Ansicht im Prüfschritt. | **Erledigt 2026-08-29** in `delta.py`. Verglichen wird gegen den **Auslieferungszustand**, nicht gegen «vorher»: Ein Entwurf hat keine Geschichte, er hat einen Ausgangspunkt — dieselbe Quelle wie `touched()`. Verschachteltes wird **gezählt statt aufgezählt** («Systemgrößen — 3 geändert»); dreizehn Systemgrößen mit Startwert, Regeln und Schalter ergäben Dutzende Zeilen und keinen Überblick. Je Zeile ein Knopf, der **nur diese eine** Änderung zurücknimmt. Die Startpfadwahl steht nicht in der Liste — «Sie haben den Vergleich gewählt» ist der Satz darüber, keine Abweichung. **Ein Sprung je Zeile fehlt** (das Paket sah ihn vor): Die Zuordnung Feld→Schritt gibt es in `FELD_SCHRITT` nur für die sechs prüfbaren Felder, und sie für alle zu erweitern hieße, die handgepflegte Tabelle zu vergrößern, die W2.2 gerade eng gehalten hat. |
| W4.3 ✅ | Laufzeitschätzung. | **Teilweise erledigt 2026-08-29 — das Paket stand auf einer falschen Prämisse.** Es sah eine Schätzung «aus `run_metadata.json`» vor; das Artefakt hielt aber **keine Dauer** fest, nur einen Zeitstempel (*wann* geschrieben wurde). Es war also nichts zu schätzen, sondern zuerst etwas zu messen: `SimulationRunner.run` schreibt jetzt `elapsed_seconds` in den Zustand, `save_run_metadata` hält sie fest — nach demselben Muster wie der Config-Fingerabdruck aus P0.6, am richtigen Moment genommen und von dort gelesen. Der Prüfschritt zeigt daraus eine **Spanne je Rechenmodus**, gerechnet je Tick, mit der Zahl der herangezogenen Läufe daneben; unter zwei Messwerten zeigt er **nichts**. **Die Restzeit während des Laufs ist am 2026-08-29 nachgeliefert** — und sie braucht die Daten aus vergangenen Läufen gar nicht: Die Tick-Zeile trägt die Dauer **jedes** Ticks (`[tick 14/40] 0.14s`), und die wurde bisher weggeworfen. Der laufende Lauf ist der beste Zeuge für sein eigenes Tempo — Rechenmodus, Bevölkerungsgröße und Maschine stimmen dort per Definition. Gezeigt wird eine **Spanne** aus den letzten zehn Tickdauern mal den verbleibenden Ticks, auf dem Ladebildschirm und im Fortschrittsfenster; unter zwei Messwerten, ohne Tick-Zeile (Szenario-Vergleich) und im letzten Tick steht dort **nichts**. **Die Tickdauer im Muster ist bewusst optional**: Verlangte das Muster sie, ginge bei einer Zeile ohne Dauer auch `tick`/`total` verloren — der Balken verlöre seine Zahl, weil eine Nebenauskunft fehlt. **Zwei Fehler hat erst der Blick aufs laufende System gefunden**, beide in der Sprache: «noch etwa 1 **Sekunden** bis 2 Sekunden» (die Einzahl fehlte in `dauer.spanne` — im Prüfschritt nie aufgefallen, weil ein ganzer Lauf praktisch nie eine Sekunde dauert) und «noch etwa **0 Sekunden**» bei Tick 39 von 40, eine Zahl, die schlechter ist als keine; dort steht jetzt «gleich fertig». **W4.3 ist damit erledigt.** |
| W4.4 ✅ | Reproduzierbarkeit vor dem Start. | **Erledigt 2026-08-29.** Codestand (Commit, Zweig, ob nicht eingecheckt) und der Config-Fingerabdruck stehen aufklappbar im Prüfschritt; der Seed stand schon als Kachel da. **Dieselbe Quelle wie das Artefakt** (`output_writer.provenance`) und keine zweite Berechnung daneben — sonst stünde vorher etwas anderes als hinterher, und genau diese Drift hat P0.6 an anderer Stelle gekostet. Im Bedienfeld bleibt es aus: Dort sind drei Kacheln der ganze Platz. |
| W4.5 ✅ | `runner.cancel()` und ein Abbruch-Knopf im Ladebildschirm. | **Erledigt 2026-08-29, kooperativ.** `RunnerOptions.should_stop` wird **zwischen** zwei Ticks gefragt — dort ist der Zustand vollständig. Ein Thread lässt sich von außen nicht sauber beenden; mitten im Tick abgeschnitten bliebe ein halber Zustand, und die Artefakte beschrieben einen Lauf, den es so nie gab. Der abgebrochene Lauf schreibt seine Artefakte wie jeder unvollständige und ist an `ticks_completed < ticks_max` erkennbar. Der Knopf braucht **keine Job-Kennung**: Wer die Seite neu geladen hat, kennt keine, darf aber abbrechen — es läuft ohnehin höchstens einer (Regel 5 der Architektur-Map). **Der Sweep-Pfad bekommt ihn nicht**: `run_all_sweeps` baut seinen Runner selbst, und ihn dafür zu öffnen wäre eine Änderung an seinem Vertrag aus W1.1 — eigenes Paket. Am echten Lauf nachgestellt: 40 Ticks geplant, nach 7 abgebrochen. |

**Stand von W4 (2026-08-29): abgeschlossen.** W4.1 bis W4.5 sind erledigt. Die Laufzeit wird **gemessen** statt geschätzt — vorher aus vergangenen Läufen, während des Laufs aus ihm selbst. Alle drei Zuwächse an Schritthöhe liegen auf «Prüfen & Starten», dem Schritt, auf dem man innehält (1,00 → 1,29).

**W5 — Handwerk.** W5.1 und W5.2 hängen an nichts und dürfen vorgezogen werden — sie beheben einen aktiv falschen Zustand.

**Stand von W5 (2026-08-29): abgeschlossen.** W5.1 bis W5.6 sind erledigt. Aus W5.3 kommt eine Lehre, die über das Paket hinausgeht: **Eine Zusage, die von der Sichtbarkeit eines Tabs abhängt, ist keine.** Zwei Fassungen der Fokusführung waren im Test grün und am laufenden System wirkungslos, weil sie an der Bildtaktung des Browsers hingen statt an dem Ereignis, um das es ging.

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W5.1 ✅ | Render-Rückfälle schreiben nicht mehr in den Entwurf. | **Erledigt 2026-08-29. Siebzehn Fundstellen, keine einzige brauchte eine Ausnahme.** Jedes Literal war eine **zweite Quelle** für einen Vorgabewert, den `default_config_draft()` schon kennt — und beim Kostenanteil liefen die beiden bereits auseinander (0,33 im Quelltext gegen 0,25 in der Datei). Zwei Wächter statt eines: ein AST-Durchlauf (*wo* im Quelltext) und eine Nachbildung von `_sync` samt `_normalise` (*dass* es passiert) — der erste kennt nur die drei Formen, die vorkamen, der zweite auch die vierte. **Am laufenden System nachgestellt:** frische Sitzung, alle sieben Schritte durchlaufen, Entwurf unverändert, Seed-Feld leer, «Weiterverwenden» auch nach einem Neuladen gesperrt. |
| W5.2 ✅ | «Weiterverwenden» bleibt ohne Eingabe gesperrt. | **Mit W5.1 erfüllt, ohne eigene Änderung.** Das Paket wollte `touched()` gegen den normalisierten Entwurf vergleichen — eine Behandlung des Symptoms. Die Ursache war der Render-Rückfall: Schreibt niemand mehr in den Entwurf, meldet `touched()` auch nichts. Am laufenden System nachgestellt: frische Sitzung, sieben Schritte durchlaufen, neu geladen — `seed: null`, «Weiterverwenden» gesperrt, mit dem richtigen Text. **Ein Paket, das sich durch ein anderes erledigt, wird abgehakt und nicht vorsorglich umgesetzt.** |
| W5.3 ✅ | Barrierefreiheit: `aria-current="step"`, Live-Region für Schrittwechsel und Statusmeldungen, Fokus auf die Schrittüberschrift, `fieldset`/`legend` um jede Radiogruppe. Gemessen: **0** `aria-live`-Regionen im ganzen Dokument. | **Erledigt 2026-08-29, alle vier am laufenden System nachgemessen.** Fünf Live-Regionen statt null; die Ansage nennt Ort und Frage in einem Satz («Schritt 4 von 7: Ausgangslage») und steht **außerhalb** des Teilbaums, den der Wechsel austauscht — eine Region, die im Moment der Änderung selbst neu entsteht, wird nicht vorgelesen. `fieldset`/`legend` genau dort, wo Radiogruppen sind (Schritte 1 und 3), die Legende beschnitten statt versteckt: `display: none` nähme sie auch der Vorlesesoftware. **Der Fokus hat drei Anläufe gebraucht, und beide Fehlschläge waren derselbe Fehler** — zu raten, wann der neue Baum steht. Erst hing der Callback am Schritt-Store (der ändert sich beim Klick, der Inhalt kommt erst mit der Antwort des Servers), dann am Inhalt, aber über `requestAnimationFrame` — und das feuert in einem Tab, den niemand sieht, **gar nicht**: `visibilityState: "hidden"`, der Scroll daneben lief (er ist synchron), in drei Sekunden kam kein einziges Bild. Ein `MutationObserver` hängt am Ereignis selbst. Danach saßen sechs der sieben Schritte — «Prüfen & Starten» nicht, weil Vorschau und Zeitschätzung dort nachzeichnen; das Fenster ist deshalb weit (2,5 s) und die Wache davor eng: Genommen wird der Fokus nur, wenn ihn **niemand** hält. **Ein Wächter musste dabei selbst nachgeschärft werden**: Die erste Fassung fragte nach dem Wort `MutationObserver` und war schon durch den Kommentar darüber zufrieden — sie prüfte die Begründung statt der Tat. |
| W5.4 ✅ | Breite je Schritt statt einer Breite für alles. Gemessen `240px 760px` bei 1040 px Zone — zu breit für Schritt 2 mit drei Feldern, zu schmal für Schritt 4 mit 104. | **Erledigt 2026-08-29 — mit einem geänderten Kriterium, und das ist der Kern des Pakets.** «Spaltenausnutzung», am breitesten Bedienelement gemessen, misst nicht, was es zu messen vorgibt: Das Raster der Ausgangslage füllt seine Spalte vollständig und meldete trotzdem **32 %**, weil jede einzelne Auswahl schmal ist. Ein Kriterium, das ein gefülltes Raster als leer meldet, wird nicht erfüllt, sondern **ersetzt** — durch drei Größen, die dem Befund entsprechen: (1) **Füllung des Rumpfes** (Ausdehnung aller Tinte, an der Breite des Rumpfes): jetzt 89,6 bis 100 % auf allen sieben Schritten, keiner unter 60. (2) **Zeichen je Zeile ≤ 75**, die typografische Spanne: vorher bis **124**, jetzt 67 bis 74. (3) **Der Einstieg hält keine Spalte für die Schrittliste vor**, die er nicht hat: statt `240px 760px` jetzt eine Spalte über 1040 px. Umgesetzt als `Step.breite` (kurze Formulare aufs Lesemaß, Karten und Raster über die volle Spalte) und `af-mass` in **`ch`** statt `rem` — die Zusage handelt von Zeichen, und ein `rem`-Deckel hängt an der Schriftgröße: 34rem ergaben im Fließtext 84, in der Bildunterschrift 90. **Zwei eigene Messfehler unterwegs**, beide erst beim Gegenlesen der Zahlen aufgefallen: Element-Kästen statt Text-Ausdehnung zu messen (jeder Absatz füllte die Spalte, alles meldete 100 %), und Zeichen aus der Pixelbreite zu schätzen statt sie zu zählen (rund 10 % daneben — genug, um einen wirkenden Deckel für wirkungslos zu halten). Und ein echter Fehler: Die Klasse des Einstiegs stand erst in `layout`, das einmal läuft — sie blieb danach auf **jedem** Schritt gesetzt. |
| W5.5 ✅ | Mobil: Schrittliste als kompakter Fortschrittsbalken statt acht gestapelter Knöpfe, Fußleiste einzeilig (heute 133 px bei 375 px Breite). | **Erledigt 2026-08-29.** Fußleiste **59 px** auf allen sieben Schritten (zugesagt: unter 72), Schrittliste von **358 auf 36 px**. Je Schritt gemessen, nicht einmal: Die Höhe hing daran, wie viele Knöpfe ein Schritt zeigt — «Prüfen & Starten» war mit 153 px der höchste. Der Umbruch sitzt sauber bei 899/900 px. **Kein Element verschwindet dabei aus dem DOM**, nur Beschriftungen aus dem Bild — beschnitten wie in W5.3, damit der Name vorgelesen wird: Die Sprungknöpfe der Liste sind Eingänge, und ein fehlender Eingang legt in Dash den ganzen Callback lahm (Regel 6). Dafür trägt die Beschriftung eines Knopfes jetzt einen eigenen Träger (`af-btn__label`); als blanker Text ließ sie sich nicht ansprechen. **Der Rückfall-Test musste nachgeschärft werden:** Die erste Fassung drehte das Stylesheet zurück und hoffte auf einen Umbruch — er kam nicht, und der Test meldete einen blinden Wächter, wo nur die Nachstellung zu zaghaft war. |
| W5.6 ✅ | Gewichtung der drei Wege des Einstiegs nach Häufigkeit. | **Erledigt 2026-08-29 — als Fachurteil gekennzeichnet, und zwar dort, wo die Entscheidung fällt** (`wizard._hauptweg`, im Docstring). Häufigkeit lässt sich ohne Nutzungsdaten nicht messen; was die Oberfläche wirklich weiß, ist **ob es etwas fortzusetzen gibt**. Danach richtet sich die Hervorhebung: frische Sitzung → «Neuen Lauf einrichten», sonst → «Letzte Einstellungen weiterverwenden». Alles andere wäre geraten. **Die Reihenfolge bleibt fest**, und auch das ist eine Entscheidung: Wer die Wege je nach Zustand umsortiert, nimmt dem wiederkehrenden Nutzer das Einzige, was er hier schon kann — hinsehen, wo der Weg letztes Mal lag. Gewicht ändert sich, Ort nicht. Ein gesperrter Weg wird nie hervorgehoben. Drei Tests halten das fest; ein vierter musste nachgezogen werden, weil er `className` auf **Gleichheit** mit `"af-way"` prüfte und mit dem Gewicht null Wege statt dreier fand. |

#### Was ausdrücklich gut ist und bleibt

Nicht alles ist zu ändern, und vier Dinge sind besser als der Branchenschnitt: die konsequente progressive Offenlegung mit ausgeschriebenen Namen im Deckel («Feinabstimmung (2 Parameter)»), der Rechenmodus als **eine** Auswahl statt zweier verneinter Kästchen, die Erklärtexte am Entscheidungsort aus **einer** Quelle (`glossary.py`), und die klebende Fußleiste, die «Weiter» auf jedem Schritt bei y = 662 von 664 px hält. Diese vier sind beim Umbau zu erhalten, nicht neu zu erfinden.

**Fertig wenn:** Jeder Schritt des Assistenten passt bei 1280 × 720 auf einen Bildschirm (W0.1 scharf), kein erfragtes Feld wird von seinem Startpfad still verworfen (W0.2 grün), kein Schreibpfad in `configs/` ist aus dem Assistenten erreichbar, und der Preflight beschreibt den Lauf, der wirklich stattfindet.

**Was die Zahlen macht:** W1.1 und W1.2 verschieben, was ein Sweep rechnet — die Länge kommt künftig aus dem Preset, und der Rechenmodus wird nicht mehr verworfen. **Der Schnitt gehört in `docs/handbuch/vergleiche.md`**, sobald das Paket steht; Läufe von davor und danach sind nicht vergleichbar. W2 bis W5 fassen nur Wegführung, Darstellung und Text an.

**Doku zieht mit:** `CLAUDE.md` (Architektur-Map: der Schnitt zwischen Assistent und Modell-Editor, die Dashboard-Regeln; Dev-Workflow: das Commit-Regelwerk), `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`, `docs/handbuch/vergleiche.md`, `docs/handbuch/glossar.md` (Modell-Editor als neuer Begriff), `README.md` und `dashboard/README.md` (Routentabelle).

---

### Regelwerk: atomare Commits (ab 2026-08-28 verbindlich)

Gilt für jede Änderung an diesem Projekt — für alle im Team und für jede Claude-Session, nicht nur für P1.9.

1. **Ein Commit = ein Befund oder ein Feature.** Kein Sammelcommit. Wer zwei Dinge behoben hat, macht zwei Commits — auch wenn sie dieselbe Datei berühren.
2. **Der Titel benennt Paket und sichtbares Ergebnis**, nicht die Datei: `fix(wizard): kein Haken für einen übersprungenen Schritt (W2.1)`, nicht `update wizard.py`.
3. **Jeder Commit ist für sich lauffähig und grün.** `pytest`, `ruff check .`, `black --check .` und seit P4.4 `mypy` laufen vor jedem **Commit**, nicht erst vor dem Push.
4. **Jeder Verhaltens-Commit bringt seinen Test mit** — im selben Commit, nicht im nächsten. Ein nachgereichter Test prüft, was gebaut wurde, statt was zugesagt war.
5. **Doku im selben Commit** ([Doku-Pflicht](../CLAUDE.md#doku-pflicht)). Bleibt sie bewusst unverändert, steht der Grund in der Commit-Message.
6. **Refactoring und Verhaltensänderung nie im selben Commit.** W3.1 ist deshalb ein reiner Umzug; alles, was danach am Umgezogenen geändert wird, ist ein eigener Commit.
7. **Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung.** Wer «passt auf einen Bildschirm» zusagt, misst Bildschirme. Wer «drei Entscheidungen genügen» zusagt, misst, ob die drei wirken. Das ist die Lehre aus P1.6 **und** aus P1.9 — derselbe Fehler, zweimal, mit grünen Kriterien.
8. **Gepusht wird nicht automatisch.** Commits bleiben lokal, bis Haiko sie selbst pusht.

---

## Phase 2 — Modellsubstanz (Claims und Code in Deckung bringen)

Diese Punkte entscheiden, ob die wissenschaftlichen Aussagen einem Fachprüfer standhalten. Solange sie offen sind, gehören die Formulierungen in Pitch, README und Handbuch abgeschwächt.

> **Stand 2026-09-03: acht der zehn Pakete sind abgeschlossen, zwei sind wieder offen.** Ein unabhängiges Audit hat drei schwere Befunde gefunden — zwei in [P2.8-B](#nachtrag-am-selben-tag-eine-methodik-ist-ein-bias-p28-b) und einen in [P2.0 Stufe C](#stufe-c--die-faktorlage-hört-auf-eingabe-zu-sein--erledigt-2026-08-30). Vollfassung mit allen Messungen: [`audit_phase2_2026-09-03.md`](audit_phase2_2026-09-03.md); die Detailliste steht wie immer in [`audit_findings.md`](audit_findings.md).
>
> Was die Phase zusammen verändert hat — und die Backtest-Kette über die Pakete hinweg, die sich aus den Einzelmessungen unten nicht ablesen lässt — steht in der [Bilanz der Phase 2](phase2_bilanz.md). Sie ist eine Synthese und keine Quelle: gepflegt wird **hier**, an den Paketen.

### Leitentscheidung: die Szenarienschicht (2026-08-29)

**Rahmen statt Richter.** Die CIB-Schicht bewertet heute den Endzustand eines Laufs. Damit steht die Antwort vor der Rechnung: Der Lauf kann sie nur bestätigen oder danebenliegen, er erzeugt nichts, was nicht vorher als zulässig festgelegt war. Entschieden ist **Variante C** — ein Szenario wird ein benanntes Bündel **exogener Verläufe** (CO₂-Preis, SAF-Quote, Konjunktur, Ölpreis, Schienenkapazität, geopolitische Schocks); F1–F7 bleiben als **lesbare Zustandslabel, die aus dem Lauf abgeleitet werden**, nicht als Eingaben. Ein Rest von Variante B — eine Verträglichkeitsprüfung beim Einrichten («Rezession und Reiseboom gleichzeitig») — bleibt als Wächter. Die CIB-Matrix in ihrer heutigen Rolle entfällt; sie kann als Variante A zurückkommen, wenn jemand sie sauber erhebt.

**Worauf die Entscheidung steht — vier Messungen, am 2026-08-29 gegen den aktuellen Stand reproduziert:**

| Befund | Zahl |
| --- | --- |
| Der Konsistenz-Score misst **Polarität**, nicht Plausibilität | Korrelation +0,56 mit der Zahl gleichpolig gesetzter Faktoren; Gruppenmittel 0,499 → 0,562 → 0,682 → 0,853 über 4/5/6/7 gleichpolige Faktoren |
| Das **echte** Impact-Balance-Kriterium trägt kein Tripleset | **2** von 128 Zuständen sind konsistent, beide Pole |
| Die Matrix ist im Kern **eine Achse** | nur **12** von 84 gleichpoligen Zellen tragen Spannung, 11 davon betreffen F3 |
| Vier Zellen verneinen die tragende Rückkopplung | `F1.1→F2.2`, `F1.1→F6.2`, `F1.1→F5.2`, `F4.1→F2.2` stehen auf **−2**, keine mit Begründung |

Der letzte Befund erklärt die drei davor: Eine negative Rückkopplung — Wachstum erzeugt Regulierung erzeugt Preis erzeugt Substitution erzeugt weniger Wachstum — ist der Motor, der gemischte Szenarien hervorbringt. Sind alle diese Schleifen gleichgerichtet kodiert, bleibt eine Achse übrig und darauf genau zwei kohärente Welten. **Die Einachsigkeit ist kein Zufall der Bewertung, sie ist deren Folge** — und sie hat eine Kundenseite: Strenge Regulierung *bei* starker Nachfrage ist die reale europäische Lage, und das Modell bewertet sie heute als unplausibel.

**Die Grundlage ist gemessen, nicht beschrieben:** [`tests/test_cib_einachsigkeit.py`](../tests/test_cib_einachsigkeit.py) hält alle vier Zahlen gegen die ausgelieferte Matrix. Fasst jemand `cib_frozen.json` an, wird der Test rot — und das ist die Nachricht, dass die Entscheidung neu auf den Tisch gehört, statt stillschweigend weitergetragen zu werden.

**Was das an der Reihenfolge ändert:** [P2.0](#p20--die-rolle-umdrehen-rahmen-statt-urteil--erledigt-2026-08-30) kommt neu davor, [P2.6](#p26--ensemble-läufe-je-rahmenszenario--erledigt-2026-08-31) und [P2.7](#p27--backtest-gegen-20152024--erledigt-2026-08-30) kommen dazu, und **P2.2 rutscht ans Ende der Phase**: Ob ein Rest CIB oder morphologische Verträglichkeit die Bündel absichert, entscheidet sich leichter, wenn das Modell geeicht ist. Vorher wäre es eine Entscheidung über ein Werkzeug, dessen Wirkung niemand kennt. Reihenfolge also: **P2.0 → P2.1 → P2.6 → P2.7 → P2.2**, P2.3 hing an P2.2 und **entfällt seit dem 2026-08-31 in seiner bisherigen Form**; P2.4 und P2.5 sind davon unabhängig.

**Was die Entscheidung nicht berührt:** Die deterministische Rechenschicht, die Trennung «Zahlen aus Python, Narrativ vom Modell», die Provenienz-Kette und die Beschränkung der Agenten auf ihr Profil. Die Invarianten 1–7 gelten unverändert; Invariante 3 (die Matrix bleibt eingefroren) so lange, wie die Matrix in Gebrauch ist.

Vollfassung mit Herleitung, den drei Wegen und den Quellen: [`entscheidung_szenarienschicht_2026-08-29.md`](entscheidung_szenarienschicht_2026-08-29.md).

### P2.0 — Die Rolle umdrehen: Rahmen statt Urteil ✅ erledigt 2026-08-30

**Befund:** Die Szenarienschicht steht hinter der Simulation statt davor. `derive_scenarios` bewertet den Endzustand gegen die eingefrorene Matrix, das LLM wählt daraus drei Kandidaten. Was ein Lauf produzieren *darf*, steht damit vor dem Lauf fest.

**Fundstelle:** [`src/cib/scenario_consistency.py`](../src/cib/scenario_consistency.py) (`derive_scenarios`), [`src/orchestration/scenario_sweeps.py`](../src/orchestration/scenario_sweeps.py), [`configs/sweeps/`](../configs/sweeps/).

**Was zu tun ist:** Die Sweeps vom Nebenweg zum Hauptweg befördern. Ein Rahmenszenario ist eine benannte, feste Lage der **exogenen** Systemgrößen; der Lauf erzeugt Nachfrage, Preise, Buchungsraten und Segmentverschiebungen daraus. F1–F7 werden am Laufende aus dem Ergebnis **abgeleitet** und als Label gezeigt, nicht mehr als Eingabe gesetzt. Der Schalter `apply_custom_overrides` und der Schritt «Faktorlage» im Assistenten (P1.9-W3.3) sind davon betroffen und ziehen mit.

**Die Maschinerie steht weitgehend — gemessen am 2026-08-29:** 13 von 13 Systemgrößen tragen eine Trajektorie (11 davon wirklich exogen; `ticket_price` und `provider_markup` sind nur Startwerte für Größen, die der Lauf selbst erzeugt), es gibt **8** Sweeps unter `configs/sweeps/`, **4** davon ganz ohne Faktor-Vorgaben. Stufenfunktionen, Regeln und Preiskomponenten sind vorhanden. Das ist Umverdrahtung, kein Neubau.

**Fallstrick — was dabei sichtbar wird:** Der bekannte Widerspruch, dass die Sweeps ihre eigenen `*_END_STATES` nicht erreichen (Finding in [`audit_findings.md`](audit_findings.md), Abschnitt Markt), **verschwindet nicht, er wechselt die Bedeutung**: Heute ist er ein Fehler, weil der Endzustand vorgegeben ist; nach der Umdrehung ist er das erwartete Verhalten. Die Konstanten in `tests/test_cib_ranking.py` gehören dann umbenannt, nicht nachgezogen.

**Zweiter Fallstrick — die Außendarstellung hängt daran:** Das Tripleset (Trendfortsetzung / Strukturwende / Krisenkonflikt) kommt heute aus dem Ranking. Nach der Umdrehung kommt es aus der Wahl der Rahmenszenarien — drei benannte Bündel statt drei bestbewerteter Konstellationen. Das ist eine Produktaussage und gehört mit [P1.3](#p13--szenariogestaltung-neu-denken--erledigt-2026-08-30-datenschema-die-entstehung-bleibt-p20) abgestimmt, bevor jemand anfängt.

**Fertig wenn** ✅ **(2026-08-30 abgehakt, am 2026-09-03 nachgeschärft und geschlossen):** Ein Lauf nimmt ein benanntes Rahmenszenario entgegen und erzeugt Faktorlabels, statt sie zu bekommen ✅; **zwei verschiedene Rahmen erzeugen verschiedene Faktorlagen** ✅ (gemessen: `business_as_usual` → `F2.1/F3.1`, `co2_delayed` → `F2.2/F3.2`, `transformation_conflict` → `F6.2/F7.2`); **jeder Lauf steht unter einem benannten Rahmen, und jeder Rahmen trägt seine Begründung — auch der Standard** ✅ (2026-09-03, ersetzt «die Sweeps sind der reguläre Startpfad», siehe unten); kein Codepfad bewertet mehr den Endzustand gegen die Matrix, um zu entscheiden, was gezeigt wird ✅ (formal — der Endzustand ging nie ein, siehe Stufe B).

> **Zwei Klauseln haben 2026-08-30 nicht gehalten, und eine davon war die falsche Frage** (Audit vom 2026-09-03). Der ursprüngliche Wortlaut verlangte: «die Sweeps sind der reguläre Startpfad» — Stufe C sagt selbst, dass sie es nicht sind, und die Klausel wurde trotzdem mit abgehakt; sie steht jetzt als offen da. Und: «Ein Test zeigt, dass zwei Läufe unter **demselben** Rahmen unterschiedliche Faktorlabels erzeugen können.» Den Test gibt es nicht, und die Eigenschaft ist **abwesend**: 50 Läufe (5 Seeds × Standard und vier Rahmen × 20 und 40 Ticks) enden **jedes Mal auf derselben Lage**. Das ist kein Fehler, sondern erwartbar — über tausend Personen mitteln sich die Einzelentscheidungen aus, und die Faktorregeln sind Schwellwerte; P2.1 hatte es nebenbei schon gemessen und zwei Kontrolltests deswegen umgebaut, ohne dieses Kriterium nachzuziehen. Die tragfähige Fassung ist die über **verschiedene Rahmen**, und die steht jetzt oben. Herleitung: [Audit Phase 2, A1](audit_phase2_2026-09-03.md).

#### Stufe A — der Score verlässt den Lauf nicht mehr als Urteil ✅ erledigt 2026-08-29

**Der Befund kam beim Aufschlagen und war schlimmer als erwartet.** Die Leitentscheidung sagte, der Score messe Polarität. Was sie nicht wusste: Er wurde **als «Plausibilität» ausgeliefert**. `_plausibility_from_score` übersetzte ihn in `hoch` / `mittel` / `niedrig` und schrieb das als Feld `plausibility` in jedes `run_scenario.json` — **und in den Prompt des Sprachmodells**, das daraufhin Narrative über die «plausibelste» Zukunft schrieb. Die Prompt-Vorlage verlangte das sogar ausdrücklich: «Schließe mit einer Bewertung von **Wahrscheinlichkeit** und Stabilität ab, die den exakten `consistency_score` nennt.»

Im Artefakt `outputs/run_20260827T181422Z/run_scenario.json` liest sich das Ergebnis so: Rang 1, alle sieben Faktoren auf `.1` — der vollständig gleichpolige Zustand —, `plausibility: hoch`. Rang 3 kippt F2 auf strenge Regulierung bei weiterhin boomender Nachfrage, also die reale europäische Lage, und bekommt weniger. **Das Produkt sagte einem Kunden wörtlich, die Welt, in der sich nichts bewegt, sei die plausibelste.**

Ein zweiter Fund daneben: Lag **gar kein** Score vor, fiel die Funktion auf den **Präsentationsrang** zurück — Rang 1 hieß dann «hoch plausibel», Rang 3 «niedrig». Aus einer Reihenfolge wurde eine Aussage über die Welt.

**Was umgesetzt ist:**

- `plausibility` ist weg. An seiner Stelle steht `konsistenz_band` mit `widerspruchsfrei` / `gemischt` / `spannungsreich` — Wörter, die die **gemessene** Größe benennen statt sie zu bewerten. Ohne Score gibt es **kein** Band (`null`), der Rangfallback ist gelöscht.
- Jede Konstellation trägt `konsistenz_bedeutung`, einen Satz zur Lesart. Er steht **in jeder Datei**, weil das Artefakt einzeln gelesen wird — vom State Explorer und vom Sprachmodell, beide ohne die Doku daneben.
- Der Prompt-Kontext trägt denselben Satz als `cib_consistency_bedeutung`, und die Vorlage verbietet die Wahrscheinlichkeitsaussage jetzt ausdrücklich, statt sie zu verlangen.
- Der Plot-Titel heißt «Szenario-Widerspruchsfreiheit» statt «Szenario-Plausibilität».

**Der Wächter:** `tests/test_konsistenz_kein_urteil.py`. Er läuft als **AST** über `src/` und kennt vier Rückfallformen — Dict-Schlüssel, Funktionsdefinition, Aufruf, Import —, während Docstrings und Kommentare das alte Wort weiter nennen dürfen; genau sie erklären ja, warum es weg ist. Ein Grep könnte das nicht trennen. `test_der_waechter_wuerde_einen_rueckfall_bemerken` stellt alle vier Formen nach und prüft den Docstring als Fehlalarm gegen.

**Was Stufe A nicht ist:** die Umdrehung selbst. Der Endzustand wird weiterhin gegen die Matrix bewertet — nur sagt das Ergebnis jetzt, was es misst. Stufe C (Faktoren abgeleitet statt gesetzt) und der erste Teil von Stufe B (ein Lauf sagt, unter welchem Rahmen er stand) sind am 2026-08-30 gefolgt.

**Doku mitgezogen:** `docs/handbuch/ref-ausgaben.md` (neuer Abschnitt zu den drei Feldern, samt Hinweis, dass ältere Läufe `plausibility` weitertragen), `docs/handbuch/glossar.md`, `docs/handbuch/grenzen.md`.

#### Vorarbeit zu Stufe C — die Umdrehung ist zur Hälfte schon gebaut (gemessen 2026-08-29)

Vor dem Umbau gehörte gemessen, wie viel «Faktoren ableiten statt setzen» heute bereits zutrifft. Verfahren wie bei `test_web_wirkung.py`: **zwei Läufe, alles gleich außer der Startlage** — einmal alle sieben Faktoren auf `.1`, einmal auf `.2` —, dann nachsehen, was von der Vorgabe übrig bleibt. Zahl der Faktoren, die ihre Startlage vergessen haben:

| Ticks | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 15 | 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gleich | 4 | 6 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 7 |

Drei Gruppen stecken darin, und ihre Aufteilung ist der eigentliche Fund:

- **F2, F3, F6, F7 — der Rahmen.** Sie vergessen ihre Startlage **im ersten Tick**, weil ihre Regeln an *exogenen* Systemgrößen hängen: CO₂-Abgabe (F2, F6), SAF-Quote (F3), Ölpreis (F7). **Für diese vier ist «Rahmen statt Richter» bereits gebaut.** Die `factor_rules` in `configs/properties.json` sind schon die Ableitung, die P2.0 verlangt — jede der sieben Faktorgruppen hat Regeln für **beide** Zustände. Stufe C ist damit kein Neubau der Mechanik, sondern das Abschalten der konkurrierenden *Eingabe*.
- **F1, F5 — der Lauf.** Sie folgen Buchungsrate und Gesellschaftsfaktor und brauchen ein paar Ticks. Der Einbruch bei Tick 3 ist kein Messfehler: Solange F4 zwischen beiden Läufen auseinanderliegt, laufen auch die Buchungsraten auseinander, und F1 kippt zu verschiedenen Zeitpunkten.
- **F4 — die Vorgabe.** Hält seine Startlage bis etwa Tick 20. **Kein Fehler, sondern ein Totband:** Die Regeln greifen unter 115 (`F4.1`) und über 135 (`F4.2`), ein Hysteresefenster gegen Flattern. Der `cost_pressure` startet bei rund 118 und wächst je Tick um etwa eins — er liegt also lange dazwischen, und dort feuert keine der beiden Regeln.

**Festgehalten in `tests/test_faktoren_abgeleitet.py`** — geprüft wird die stabile Aussage (die vier Rahmenfaktoren, nach einem Tick, plus der Nachweis, dass jede ihrer Regeln an einer exogenen Größe hängt) und das Totband als Config-Eigenschaft. Die Tabelle oben ist Beschreibung, keine Zusage: Eine Sperrklinke auf «genau sechs nach sechs Ticks» wäre über den Tick-3-Einbruch hinweg spröde.

**Der Befund für P1.9, der dabei herausfiel:** Der Schritt «Faktorlage» (W3.3) fragt **sieben** Auswahlen ab, und im Standardlauf ist die Antwort auf vier davon nach *einem* Tick überschrieben, auf sechs nach wenigen. Das ist nicht Invariante 7 im engeren Sinn — der Startpfad *verwirft* nichts, er reicht die Wahl korrekt durch —, aber es ist dieselbe Enttäuschung für den Nutzer: eine Frage, deren Antwort das Ergebnis nicht prägt. Als Finding aufgenommen; die Auflösung ist Stufe C, nicht ein Hinweistext im Assistenten.

**Reihenfolge entschieden am 2026-08-29: Stufe B und C warten auf P1.9.** Beide fassen den Assistenten an — Stufe C nimmt dem Schritt «Faktorlage» seine Eingabe —, und P1.9 ist offen. Zwei Umbauten gleichzeitig an derselben Schrittfolge kosten mehr, als die Wartezeit wert ist. **Was damit bewusst offen stehen bleibt:** Der Assistent stellt bis dahin weiter sieben Fragen, deren Antwort das Ergebnis nicht prägt. Der Befund steht in `audit_findings.md` und ist gemessen; er wird **nicht** durch einen Hinweistext beruhigt, weil ein Hinweis die Frage nicht wirksam macht. Wer P1.9 abschließt, nimmt Stufe C als Nächstes.

**Die naheliegende Form für Stufe C, damit sie nicht neu erfunden wird:** Der Schritt «Faktorlage» verschwindet nicht, er wechselt die Ebene — statt sieben Faktorzuständen fragt er die **exogenen Größen**, an denen die Faktoren gemessen ohnehin hängen: CO₂-Abgabe (F2, F6), SAF-Quote (F3), Ölpreis (F7). Aus sieben folgenlosen Auswahlen werden drei wirksame, und das *ist* die Umdrehung.

#### Stufe B — ein Lauf sagt, unter welchem Rahmen er stand ✅ erledigt 2026-08-30

**Der Befund:** Mit der Umdrehung ist das Rahmenszenario die **zentrale Eingabe** — es setzt die exogenen Verläufe, aus denen der Lauf alles Weitere erzeugt. Bis dahin hielt **kein Artefakt fest, welches es war.** `run_metadata.json` kennt Seed, Rechenmodus, Fingerabdruck und Codestand; das Szenario fehlte.

**Ganz unsichtbar war es nicht — und der Unterschied ist wichtig.** Gemessen unterscheidet `config_fingerprint` die neun Rahmen sauber: Jeder erzeugt einen eigenen `properties`-Hash. Man sah damit, **dass** ein anderer Rahmen lief, nicht **welcher**. Für die Frage «unter welcher Außenwelt ist diese Zahl entstanden» — die Frage, um die es beim Verkaufen geht — war das keine Antwort.

**Was umgesetzt ist:**

- `SimulationState.rahmen` trägt `id`, `name` und `quelle`. **Gesetzt beim Aufbau des Zustands, gelesen beim Schreiben der Metadaten** — dasselbe Muster wie `config_fingerprint` und `elapsed_seconds`. Am Ende erraten ginge auch nicht: Ein Sweep legt seine Werte in den Zustand, und aus den Zahlen allein lässt sich kein Name zurückgewinnen.
- Drei Quellen, weil es drei Wege gibt: `preset` (Datei unter `configs/sweeps/`), `eigen` (im Assistenten zusammengestellt), `standard` (die ausgelieferten Dateien). **Auch der Standard ist ein Rahmen** — er trägt eigene exogene Verläufe und hieß nur bisher nicht so; deshalb sah ein Lauf ohne Preset aus, als liefe er «ohne Szenario».
- Alle drei Startpfade setzen ihn: Dashboard, Sweep-Lauf und CLI.
- Die Ansicht «Übersicht» zeigt ihn als **erste** der vier Herkunftskacheln. Ein Lauf ohne Angabe bekommt «nicht festgehalten» statt einer Vermutung.

**Der Wirkungstest hat einen Entwurfsfehler gefunden, bevor er ins Artefakt kam.** Der erste Anlauf hängte den Rahmen an den Zweig, der die Overrides anwendet. Weil `apply_custom_overrides` per Vorgabe an ist, hätte damit ein Lauf mit der **Standard-Ausgangslage** das Etikett «eigene Werte» getragen, ohne dass jemand etwas geändert hat. `test_web_wirkung.py` meldete das sofort: Ein Feld erreichte plötzlich die Simulation, das sie vorher nachweislich nicht erreichte. Der Rahmen folgt jetzt der **Wahl** des Nutzers (`scenario_mode`), nicht dem internen Pfad.

**Der Wächter:** `tests/test_rahmen_im_artefakt.py`. Er prüft alle acht Presets statt eines, gleicht Kennung und Name gegen die Datei ab — und misst nach, **warum** das Feld nötig war: dass der Fingerabdruck die Rahmen zwar unterscheidet, sie aber nicht benennt. Wäre er umkehrbar, wäre das Feld überflüssig.

**Doku mitgezogen:** `docs/handbuch/ref-ausgaben.md` (das Feld und der Grund neben dem Fingerabdruck), `docs/handbuch/ergebnisse.md` (die Kachel).

**Der zweite Teil: `scenarios.json` behauptete etwas über den Lauf, das nicht aus ihm stammt.** Drei Befunde, alle gemessen:

1. **Das Artefakt war leer — in jedem Lauf.** P1.3 hat den Metadaten-Schlüssel des Narrativs von `scenarios` auf `erzaehlte_szenarien` umbenannt und `render_scenarios_markdown` mitgezogen (der Kommentar dort hält es fest), **`run_simulation.py` aber nicht**. Der Schreiber las den alten Schlüssel weiter und übergab dem Bericht obendrein die falsche Form (`{"scenarios": …}` statt `{"szenarien": …}`). Dieselbe Drift, eine Ebene weiter außen — und niemand hat sie bemerkt, weil niemand die Datei liest.
2. **Der Nenner machte aus einem Befund eine Erfolgsmeldung.** `total_evaluated` zählte die **behaltenen** Konstellationen statt der bewerteten. Bei `allow_inconsistent=False` stand im Bericht «1 von 1 Konstellationen konsistent», wo **1 von 128** richtig ist.
3. **Die Konstellationen kommen nicht aus dem Lauf.** `derive_scenarios` zählt alle 2⁷ Kombinationen durch und rankt sie nach Konsistenzwert; der Endzustand geht an keiner Stelle ein. Auf der ausgelieferten Matrix bleibt **genau eine** übrig — der vollständig gleichpolige Zustand. Das Artefakt liegt trotzdem im Lauf-Verzeichnis und sieht dort aus wie ein Ergebnis.

**Umgesetzt:** Alle drei behoben. Der Bericht trägt jetzt einen Satz, der sagt, woher seine Konstellationen stammen und wo das Tripleset *dieses* Laufs steht (`run_scenario.md`). Der Wächter in `tests/test_szenario_herkunft.py` prüft den **Weg** statt der Namen: Was der Node ablegt, muss der Schreiber finden, und was der Schreiber übergibt, muss der Bericht lesen können.

**Nicht angefasst — und das ist Absicht:** Ob die CIB-Schicht diese Rolle behält, entscheidet [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31) **nach** dem Backtest. Sie jetzt zu entfernen hieße, diese Entscheidung vorwegzunehmen. Was Stufe B leistet, ist die Ehrlichkeit davor: Das Artefakt sagt, was es ist.

#### Stufe C — die Faktorlage hört auf, Eingabe zu sein ✅ erledigt 2026-08-30

**Ausgeführt, sobald P1.9 stand.** Die Reihenfolge-Entscheidung vom 2026-08-29 hat Stufe C auf den Abschluss von P1.9 gelegt; der kam am 2026-08-30.

**Die Form war anders als geplant — und der Plan lag falsch.** Vorgesehen war, den Schritt «Ausgangslage» auf die Ebene der exogenen Größen zu heben: statt sieben Faktorzuständen die CO₂-Abgabe, die SAF-Quote und den Ölpreis. Beim Aufschlagen zeigte sich, dass das **dieselbe Falle in neuer Verkleidung** gewesen wäre: `carbon_tax_level` trägt eine Regel, die ab **Tick 1** setzt — ein dort eingestellter Startwert wäre folgenlos, genau wie die Faktorlage vorher. Der Rahmen ist der **Verlauf**, nicht der Startwert.

**Und Verläufe gibt es schon: die acht Presets.** Jedes trägt `property_overrides` auf exogenen Größen — sie *sind* die Rahmenszenarien, und Schritt 1 wählt bereits zwischen ihnen. Zu tun blieb damit nichts Additives, sondern ein Schnitt.

**Gemessen, bevor geschnitten wurde.** Vier der acht Presets gaben zusätzlich Faktorzustände vor. Je 20 Ticks mit und ohne diese Vorgabe:

| Preset | Vorgaben | Faktoren am Ende | Ticketpreis |
| --- | ---: | --- | --- |
| `achterbahn_szenario` | 3 | identisch | gleich |
| `alles_drin_szenario` | 7 | identisch | 588,47 vs 574,47 (2,4 %) |
| `business_as_usual` | 3 | identisch | gleich |
| `p5.7` | 7 | identisch | 121,27 vs 120,59 (0,6 %) |

**In allen vieren landen alle sieben Faktoren auf denselben Zuständen.** Die Vorgabe bestimmte das Ergebnis nicht — sie störte nur die ersten Ticks, bevor die Regeln sie überschrieben. Das ist die Umdrehung in einer Zeile: Die Antwort stand vor der Rechnung, und die Rechnung kam ohnehin dort an.

**Was umgesetzt ist:**

- `factor_overrides` steht in allen acht Presets auf `[]`, und `apply_sweep_overrides` wendet sie nicht mehr an. Das Feld bleibt im Modell lesbar; **der Sweep-Vertrag nennt es in `UNBEACHTET`** (Invariante 7 — ein Pfad, der etwas verwirft, sagt es).
- `ConfigDraft.factor_states` ist weg, ebenso `RunLaunchConfig.factor_states`, `factor_overrides_from_states` und `extract_factor_states_from_file`. Es gibt **keinen Schreibweg mehr** zur Faktorlage.
- Der Schritt «Ausgangslage» ist entfallen; die Schrittfolge geht von **sieben auf sechs**.
- Der Schalter `apply_custom_overrides` ist nach Schritt 1 umgezogen, **hinter «Feinabstimmung»**. Der erste Anlauf legte ihn auf die Entscheidungsfläche — der Wächter aus P1.1 meldete sofort vier Felder statt drei und hatte recht: «gelten meine Werte» ist kein vierter Schritt zum Lauf.
- Die abgelöste Streamlit-Oberfläche zeigt an der Stelle ihrer Faktor-Auswahl jetzt einen Hinweis statt Auswahlfeldern. **Sie wird von keinem Test berührt** — ohne diese Anpassung wäre sie still kaputtgegangen, und «nur noch zum Vergleich lauffähig» hätte nicht mehr gestimmt.

**Am laufenden System nachgewiesen:** Ein Lauf über 40 Ticks startet mit allen sieben Faktoren auf `.1` und **erzeugt** bis Tick 40 `F1.2, F2.2, F3.2, F4.2, F5.2, F6.1, F7.1` — eine **gemischte** Lage, die niemand eingestellt hat und die die alte Bewertung als «weniger plausibel» abgewertet hätte.

**Doku mitgezogen:** `docs/handbuch/faktoren.md` (das Kapitel heißt jetzt «Sie stellen sie nicht ein — der Lauf erzeugt sie»), `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`, `docs/handbuch/erste-simulation.md`, **`docs/handbuch/vergleiche.md`** (vierter Schnitt: Endzustände gleich, erste Ticks und damit die Preise nicht), `CLAUDE.md` (Glossar und Architektur-Map).

#### ✅ Wieder geöffnet und geschlossen am 2026-09-03 — der Browser-Wächter war seit dem Umbau rot

**Der Schnitt war richtig, die Sperrklinke ist nicht mitgezogen worden.** Stufe C hat die Schrittfolge von sieben auf sechs Schritte verkürzt und den `apply_custom_overrides`-Schalter nach Schritt 1 verschoben. Beides misst `tests/test_web_overflow.py` — und beides hat ihn rot gemacht, **am 2026-08-30, unbemerkt bis zum 2026-09-03**:

| Zusage | Meldung | Ursache |
| --- | --- | --- |
| «kein Schritt ist höher als sein Deckel» | «Bei 1280 px nicht gemessen: `['Schritt 7']`» (ebenso bei 1024 px) | `DECKEL` führt Schritt 1–7, `wizard.STEPS` hat sechs |
| «keine Zeile läuft über 75 Zeichen» (P1.9-W5.4) | «Was soll gerechnet werden?: **89 Zeichen** in P — *Ist der Schalter aus, bleiben alle Anpas…*»; bei 1024 px 81 | der verschobene Schaltertext steht außerhalb des `af-mass`-Deckels |
| der Selbsttest des Breiten-Wächters | `assert (96.7 >= 60.0 and 89 <= 75)` | er kann keinen Rückfall nachstellen, solange der Ist-Stand schon außerhalb liegt |

**Warum es niemand gesehen hat, und das ist der eigentliche Befund:** Der Wächter ist opt-in (Extra `ui` plus Chromium) und überspringt sich sonst schweigend; die CI hat keinen Browser. Vier Tage lang waren beide Zusagen ungeprüft, und die Regel «Test und Doku im selben Commit» wurde ausgerechnet für den Wächter nicht eingehalten, der die Schrittfolge misst.

**Erledigt am 2026-09-03, und beide Hälften anders als vermutet.**

*Die Zeilenlänge war kein Textproblem, sondern ein Strukturproblem.* Nicht der verschobene Schaltertext war zu lang — `ui.explainer` rendert **jede** Glossar-Erklärung ohne Lesemaß, an jedem Feld. P2.0-C hat es nur sichtbar gemacht, weil der Wächter Schritt 1 misst. Den einen Text zu kürzen hätte den Fall behoben und den Mechanismus stehen lassen; jetzt trägt der Körper einer Erklärung `af-mass` wie jeder andere Fließtext.

*Und der Deckel ist nachgemessen statt gestrichen.* Ist-Stand bei 1280 / 1024 px:

| | Einstieg | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1280 px | 1,00 | **1,34** | 1,00 | 1,00 | 1,22 | 1,02 | 1,45 |
| 1024 px | 1,00 | **1,42** | 1,00 | 1,00 | 1,22 | 1,08 | 1,45 |

Die Schritte 4 bis 6 sind **dieselben wie vorher, eine Nummer weiter** — der alte 5 (1,31) misst als neuer 4 nun 1,22, der alte 6 als neuer 5 nun 1,02. Gewachsen ist nur **Schritt 1**, von 1,20 auf 1,34 (bzw. 1,37 auf 1,42), und der Zuwachs ist gemessen zugeordnet: Er kommt **vollständig** vom zugezogenen Schalter und **nicht** vom neuen Lesemaß — mit und ohne `af-mass` misst der Schritt dieselben 1,34, weil der Erklärungskörper in einem zugeklappten `<details>` steckt und keine Höhe trägt.

**Fertig wenn** ✅ `tests/test_web_overflow.py` wieder grün ist und im Commit steht, warum es durchging. Herleitung: [Audit Phase 2, C5](audit_phase2_2026-09-03.md).

#### ✅ Die zweite offene Klausel, beantwortet am 2026-09-03 (A1)

**«Die Sweeps sind der reguläre Startpfad» war das falsche Mittel**, und deshalb wird die Klausel ersetzt statt nachgeholt. Ein `configs/sweeps/standard.json` müsste **jede Trajektorie aus `properties.json` wiederholen** — zwei Quellen für denselben Wert, genau die Klasse, die [P2.11](#p211--zwei-quellen-für-dieselbe-marktkonstante--erledigt-2026-09-03) gerade abgeräumt hat und die dieses Projekt schon dreimal bezahlt hat (F7, die drei Rule-Evaluatoren, der Kostendruck).

**Was wirklich fehlte, war kleiner und konkreter.** Stufe B hält fest: «Auch der Standard ist ein Rahmen — er trägt eigene exogene Verläufe und hieß nur bisher nicht so.» Trotzdem war ausgerechnet **dieser** Rahmen der einzige **ohne Begründung**, während `test_rahmen_traegt_begruendung.py` sie von jedem Preset verlangt — und er ist der meistgenutzte: Jeder Lauf, der kein Preset wählt, steht darunter. In der Oberfläche war die Stelle sogar ausdrücklich leer (`if choice in {STANDARD, CUSTOM}: return html.Div()`).

**Umgesetzt:** `PropertiesConfig.kohaerenz` — These, Begründung, Quellen und Vorbehalt **neben den Zahlen, die sie begründen**, nicht in einer zweiten Datei. Der Assistent zeigt sie jetzt für den Standard wie für jedes Preset, und beide benutzen **denselben** Renderer; zwei wären die nächste Stelle gewesen, an der sie auseinanderlaufen. Für **eigene Werte** steht dort bewusst keine Begründung, sondern der Satz, dass es keine gibt: Wer eigene Verläufe nach außen zitiert, begründet ihre Stimmigkeit selbst.

**Was die Begründung dabei aufdeckt:** Der Standard ist seit [P2.10](#p210--ein-rahmenszenario-das-die-angebotsseite-wirklich-benutzt--erledigt-2026-09-03) der **einzige** Rahmen mit konstanter Kapazität — eine Annahme und keine Abwesenheit einer Annahme. Sie steht jetzt in seinem Vorbehalt, zusammen mit der damals offenen Restposition von P2.8 (die Bevölkerungskurve endete bei Tick 30, ein Standardlauf geht 40). **Diese zweite ist seit dem 2026-09-07 geschlossen** ([P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31)): Die Kurve reicht bis Tick 120. Der Vorbehalt nennt jetzt ihre **Höhe** statt ihres Horizonts.

**Gehalten von** `TestAuchDerStandardIstEinRahmen`, fünf Zusagen — darunter die, die den Umweg verbaut: Es darf **keine** `configs/sweeps/standard.json` geben.

**Was Stufe C nicht ist:** Stufe B. Die Sweeps sind noch nicht der reguläre Startpfad — ein Einzellauf ohne Preset rechnet weiterhin gegen die Datei-Defaults, und `derive_scenarios` bewertet den Endzustand weiterhin gegen die Matrix. Der Unterschied ist, dass diese Bewertung jetzt nichts mehr **vorgibt**.

**Doku zieht mit:** `docs/cib_role.md`, `docs/handbuch/cib.md`, `docs/handbuch/faktoren.md`, `docs/handbuch/presets.md`, `docs/scenario_runs.md`, `CLAUDE.md` (Glossar «CIB-Matrix», «Faktoren F1–F7», Architektur-Map zu `src/cib/`).

### P2.1 — Buchungsmodell: echte Ziehung statt Schwellwert ✅ erledigt 2026-08-30

> **Beide Hälften stehen:** `booking_probability` liefert eine Zahl in [0, 1] und `evaluate_booking` zieht dagegen; die acht Koeffizienten stehen als Daten mit Herkunftsangabe in `configs/properties.json`.

**Was umgesetzt ist (2026-08-30):**

- `_booking_probability` gab ein `bool` zurück und verglich die Sigmoid gegen 0,5. Weil die Sigmoid monoton ist, war das identisch mit `utility >= 0` — der Logit-Teil tat nichts. Sie heißt jetzt `booking_probability`, liefert die Wahrscheinlichkeit, und `evaluate_booking` zieht mit `rng.random() < p`. `DEFAULT_LOGIT_THRESHOLD` ist entfallen.
- **Der Fallstrick ist gelöst, wie der Plan ihn beschrieb:** `buchungsstrom(seed, tick)` baut über `SeedSequence([seed, tick])` einen Strom je (Lauf, Tick). `rng` ist in `evaluate_booking` **Pflicht ohne Default** und steht im Kontextparameter-Wächter (`tests/test_cost_pressure_source.py`) — ein selbst besorgter Generator wäre in jedem Tick derselbe.
- `_seed_runtime` ist **entfernt**. Sie seedete das stdlib-`random` und den globalen Legacy-Zustand von `np.random`; beides benutzt niemand, gezogen wird über `default_rng`. Sie war wirkungslos und zugleich gefährlich: Wer neuen Zufallscode schrieb, konnte sich auf sie verlassen.
- **Null heißt «kann nicht», nicht «unwahrscheinlich»**: Wer sich das Ticket nicht leisten kann, bucht nicht — `< p` und nicht `<= p`, weil `rng.random()` die 0,0 mit positiver Wahrscheinlichkeit liefert.

**Was das an den Zahlen verschiebt** (2000 Personen, `carbon_tax = 50`, **gemessen am 2026-08-30**):

> Die Bevölkerung hat sich mit [P2.4](#p24--das-alter-prägt-die-person--erledigt-2026-08-31-erste-fassung-korrigiert) verändert — das Alter formt seither die Merkmale, und die Werte unten liegen heute anders (bei 250 € etwa 0,090 statt 0,059 und 0,134 statt 0,072). **Die Aussage der Tabelle hält trotzdem**, und sie ist die Richtung, nicht die Zahl: Die Schwelle überzeichnet die Nachfrage bei niedrigen Preisen und unterzeichnet sie bei hohen. Nachgemessen am 2026-08-31.

| Ticketpreis | Schwelle | Ziehung | Streuung über 20 Ströme |
| --- | ---: | ---: | --- |
| 80 € | 0,968 | 0,742 | 0,715 – 0,755 |
| 110 € | 0,847 | 0,602 | 0,577 – 0,615 |
| 140 € | 0,621 | 0,439 | 0,419 – 0,449 |
| 180 € | 0,299 | 0,243 | 0,229 – 0,255 |
| 250 € | 0,059 | 0,072 | 0,065 – 0,082 |

Die Schwelle **überzeichnete** die Nachfrage bei niedrigen Preisen und **unterzeichnete** sie bei hohen — sie drückte jede Wahrscheinlichkeit auf 0 oder 1 und stauchte die Nachfragekurve zu den Rändern. Der Schnitt steht in `docs/handbuch/vergleiche.md`; Läufe von davor sind mit späteren **nicht** vergleichbar, auch nicht der Richtung nach.

**Ein Nebenbefund, der zwei Tests umgebaut hat:** Der Seed verschiebt die **Faktor-Endzustände** jetzt kaum noch — die Startwerte 1, 2 und 3 landen nach 10, 15 und 20 Ticks auf denselben sieben Zuständen. Die Einzelentscheidungen mitteln sich über tausend Personen aus; was streut, sind die Raten, nicht die Lage. Zwei Kontrolltests in `test_run_provenance.py` standen auf «zwei Seeds divergieren» und wären dadurch rot geworden, ohne dass am Fingerabdruck etwas falsch ist. Sie messen jetzt, was sie eigentlich brauchen: **dass der Lauf die Faktoren überhaupt bewegt** (bei 15 Ticks vier von sieben).

**Der Wächter:** `tests/test_buchung_zieht.py` — elf Zusagen in vier Gruppen: die Wahrscheinlichkeit ist eine Zahl, es wird wirklich gezogen, der Strom gehört einem Tick, und der Lauf bleibt bei gleichem Seed reproduzierbar.

**Doku mitgezogen:** `docs/handbuch/kaufentscheidung.md` (der Abschnitt hieß «Warum das deterministisch ist»), `docs/handbuch/vergleiche.md` (fünfter Schnitt), `docs/handbuch/ref-config.md` (die acht Felder), `docs/research/references.md` (der Vorbehalt, dass die Einträge die Form belegen und nicht die Zahlen), `CLAUDE.md` (Glossar «Logit-Modell» und der Vorbehalt in der Einleitung).

**Die zweite Hälfte: die Koeffizienten (2026-08-30).** Acht Zahlen standen als Literale in `booking_probability` — `base_utility = 2.0`, die Normierungen `/100.0`, das Substitutionsgewicht `1.5`, die Öko-Basislinie, der Grün-Aufschlag und die beiden Werte für preisempfindliche Personen. Sie bestimmen jede Buchungsrate, die das Produkt ausgibt, und nirgends stand, woher sie kommen.

Sie stehen jetzt in `PropertiesConfig.booking_model` und in `configs/properties.json`, jede mit einem Pflichtfeld `quelle`.

**Und hier war eine Versuchung, der das Paket nicht nachgegeben hat.** Der Plan verwies auf die Literatur in `docs/research/literature/`. Beim Nachlesen zeigt sich: `docs/research/references.md` belegt die **Funktionsform** (Ben-Akiva/Lerman 1985, McFadden 1974 — der Preis geht negativ in den Nutzen ein) und sagt für die Substitution ausdrücklich, es gebe «keine Standard-Einheitsformel, sondern modellabhängig». **Für keinen der acht Zahlenwerte gibt die vorhandene Literatur eine Zahl her.** Eine Quellenangabe daranzuheften hätte ausgesehen wie eine Kalibrierung, die es nicht gibt — dieselbe Klasse erfundener Provenienz, gegen die P2.3 und die Matrix-Befunde stehen.

Jede `quelle` nennt deshalb **beides getrennt**: die belegte Form und den gesetzten Wert. Ein Test hält fest, dass keine von ihnen eine Schätzung behauptet; ein Validator im Modell weist Floskeln wie `quelle="handgesetzt"` ab.

**Der Wächter:** `tests/test_buchungskoeffizienten.py` — 38 Zusagen in vier Gruppen: jeder Koeffizient trägt einen Satz zur Herkunft und sagt, ob der Wert gesetzt ist; keine Zahl steht mehr in `booking_probability` (AST-Durchlauf, `0.0` und `1.0` bleiben als Bereichsgrenzen erlaubt); Datei und Modell laufen nicht auseinander; und ein Schreibzugriff des Modell-Editors verliert den Block nicht — er kennt ihn nicht, liest aber die ganze Datei und schreibt sie zurück. Diese Eigenschaft ist jetzt gemessen statt angenommen.

**Was bewusst nicht dazugehört:** Der Bereich «Modell» im Dashboard zeigt die acht Felder **nicht**. Sie sind über die Datei änderbar, und `docs/handbuch/ref-config.md` sagt das. Acht Bedienelemente dorthin zu legen wäre eine Oberflächenentscheidung, die dieses Paket nicht trifft — und die Zusage von P2.1 hängt nicht daran.

**Eichung bleibt offen, und das ist jetzt sichtbar statt verborgen:** Keiner der acht Werte ist an Daten geprüft. Das ist genau die Lücke, die [P2.7](#p27--backtest-gegen-20152024--erledigt-2026-08-30) schließen soll — der Backtest ist der erste Anlass, bei dem sie sich beziffern lässt.


**Befund:** Das "Logit-Modell" ist keines. Es wird `p = 1/(1+e^-u)` gerechnet und dann `p >= 0.5` geprüft — weil die Sigmoid monoton ist, ist das mathematisch identisch mit `u >= 0`. Der Logit-Teil tut nichts; es wird nie gegen die Wahrscheinlichkeit gezogen. Die Koeffizienten (`base_utility = 2.0`, `/100.0`, `*1.5`) sind handgesetzt, nicht geschätzt.

**Fundstelle:** [`src/population/population_sampler.py:355`](../src/population/population_sampler.py) (`_booking_probability`), Schwelle `DEFAULT_LOGIT_THRESHOLD = 0.5` in Zeile 23.

**Was zu tun ist:** Gegen die Wahrscheinlichkeit ziehen (`rng.random() < p`) mit einem aus dem Lauf-Seed abgeleiteten Strom, damit Reproduzierbarkeit erhalten bleibt. Koeffizienten nach `configs/properties.json` auslagern und ihre Herkunft dokumentieren — die Literatur liegt bereits in `docs/research/literature/` (Preiselastizitäten im Luftverkehr).

**Fallstrick (2026-08-26) — "mit dem Lauf-Seed" reicht nicht:** `evaluate_booking` bekommt heute **überhaupt keinen** RNG, und `run_population_tick` wird in jedem Tick mit demselben `state.config.seed` aufgerufen ([`environment_node.py:157`](../src/orchestration/environment_node.py)). Wer dort naiv `rng.random() < p` mit dem Lauf-Seed einbaut, zieht in jedem Tick dieselbe Zahlenfolge: es buchen immer dieselben Individuen, und die Buchungsrate wird zur Stufenfunktion. Reproduzierbar, aber falsch — und schwer zu bemerken, weil die Zahlen plausibel aussehen. Nötig ist ein Strom pro **(Lauf, Tick)**, z. B. `default_rng(SeedSequence([seed, tick]))`. Der Einstiegspunkt existiert schon: `run_population_tick` nimmt `current_tick` entgegen und **benutzt es nirgends** (einziges Vorkommen: die Signatur in Zeile 508).

**Zur Vorbedingung (richtiggestellt am 2026-08-26):** `_seed_runtime` ([`simulation_runner.py:269-281`](../src/orchestration/simulation_runner.py)) seedet das globale `np.random`, gezogen wird über `default_rng` — die Funktion ist also tatsächlich wirkungslos und gehört aufgeräumt. Die Reproduzierbarkeit des Samplers hängt aber **nicht** daran: `state.config.seed` wird explizit durchgereicht (`environment_node.py:157` → `run_population_tick` → `_rng`). Die frühere Formulierung, ohne diese Korrektur sei "die Reproduzierbarkeit mit dem ersten echten Zufall weg", trifft nicht zu. Das eigentliche Risiko ist der Fallstrick oben.

**Fertig wenn:** Buchungsentscheidungen sind stochastisch, unterscheiden sich zwischen Ticks, sind bei gleichem Seed reproduzierbar, und jeder Koeffizient hat eine benannte Quelle. Ein Test zeigt beides: gleicher Seed gleiches Ergebnis, aufeinanderfolgende Ticks unterschiedliche Ziehung.

**Doku zieht mit:** `docs/handbuch/kaufentscheidung.md`, `docs/handbuch/saettigung.md`, `README.md`, `CLAUDE.md` (Glossar "Logit-Modell").

### P2.2 — Die Szenarienschicht endgültig festlegen ✅ entschieden 2026-08-31

> **Entschieden am 2026-08-31 (Haiko): Variante 1 — nichts Formales.** Die Kohärenz eines Rahmenszenarios wird **in Prosa mit Quellen** begründet, wie bei den SSP-Storylines; es gibt keinen Algorithmus, der sie prüft. Der Backtest, der diese Entscheidung tragen sollte, hat sie beantwortet: Die dringende Baustelle ist die **Modellsubstanz**, nicht das Absicherungswerkzeug. Eine neu erhobene Matrix hätte 168 Urteile gekostet und ein Modell abgesichert, dessen Nachfrageseite nachweislich verkehrt herum läuft.

> **Neu geschnitten am 2026-08-29** ([Leitentscheidung](#leitentscheidung-die-szenarienschicht-2026-08-29)). Das Paket hieß «Impact-Balance-Kriterium implementieren» und war ein Umsetzungsauftrag. Es ist jetzt eine **Entscheidung**, und sie kommt **nach** dem Backtest — nicht davor. Der Grund: Die Umsetzung wurde probehalber vorgenommen und über den vollständigen Zustandsraum ausgewertet; das Ergebnis ist der Anlass, das Paket umzuschneiden statt es abzuarbeiten.

**Befund:** Die Konsistenzprüfung ist nicht der Weimer-Jehle-Algorithmus. Sie prüft einzelne Zellen gegen einen Schwellwert und summiert Konflikte. Das eigentliche CIB-Kriterium ist die **Impact Balance**: ein Szenario ist konsistent, wenn für jeden Faktor der gewählte Zustand die Summe der eingehenden Einflüsse maximiert. Diese Gleichgewichtsbedingung steht nirgends im Code.

**Fundstelle:** [`src/cib/scenario_consistency.py:99`](../src/cib/scenario_consistency.py) (`ConsistencyChecker.check_scenario` und `compute_consistency_score`; die Methode hiess in einer aelteren Fassung dieses Absatzes `check_consistency` — korrigiert am 2026-08-31).

**Die offene Frage ist beantwortet — mit einer Zahl (2026-08-29):** Der Fallstrick unten fragte, was passiert, wenn das echte Kriterium weniger als drei konsistente Szenarien liefert. Über alle 128 Zustände nachgerechnet: Es liefert **genau zwei**, und beide sind Pole. Das Tripleset ist aus dem Impact-Balance-Kriterium auf der heutigen Matrix **nicht bedienbar** — nicht knapp, sondern grundsätzlich, weil die Matrix im Kern eine einzige Achse ist. Gemessen und festgehalten in [`tests/test_cib_einachsigkeit.py`](../tests/test_cib_einachsigkeit.py).

#### Die Wahl und ihre Umsetzung (2026-08-31)

**Gewählt ist Variante 1.** Die Begründung ist nicht, dass sie die billigste ist, sondern dass die beiden anderen mehr Präzision versprächen, als die Datenlage hergibt: Variante 3 hätte 168 begründete Urteile über gerichtete Einflussstärken gekostet — und der Backtest hatte einen Tag zuvor gezeigt, dass die Nachfrageseite des Modells nicht bloß ungenau, sondern **invertiert** ist. Ein formales Konsistenzkriterium über einem Modell, das die Richtung verfehlt, verlagert nur die Frage.

**Variante C ist kein Verzicht, sondern eine Bringschuld** — sie verlagert die Absicherung von der Mechanik in den Text, und der Text muss dann auch da sein. Umgesetzt in vier Teilen:

1. **Ein Szenario sagt, was es ist** (`SweepConfig.art`: `rahmen` oder `stresstest`). **Der Fund, der dem Paket seinen Umfang gab:** Unter `configs/sweeps/` lagen zwei Dinge ununterscheidbar nebeneinander, und der Szenario-Vergleich startete beide — vier begründete Weltbilder und vier Stresstests der Engine. «Totaler Wahnsinn (Alle Parameter)» und ein im Dashboard gesichertes Experiment namens «P5.7» standen gleichrangig neben «Business as Usual». Einem Kunden wurde damit ein Belastungstest als Zukunft angeboten. Der **Standard ist `stresstest`**, nicht `rahmen`: Die stillere Voreinstellung wäre die falsche, weil das Sichern eines Experiments in denselben Ordner schreibt.
2. **Jedes Rahmenszenario trägt seine Kohärenzbegründung** (`SweepConfig.kohaerenz`): eine These, die Begründung *warum diese Entwicklungen zusammen eine Welt ergeben*, die Quellen, und der **Vorbehalt**. Der bisherige `rationale` bleibt daneben und ist etwas anderes — er erklärt, welche Regel bei welchem Tick greift; das ist eine Umsetzungsnotiz, keine Begründung.
3. **Die Trennung von Form und Wert ist dieselbe wie bei den Buchungskoeffizienten** (P2.1), und sie ist hier der Kern der Ehrlichkeit: Belegt ist die *Storyline* — dass diese Entwicklungen zusammen auftreten können und warum. **Nicht belegt sind die Zahlen**, mit denen sie im Lauf eingestellt werden. Bei welchem Tick die CO₂-Abgabe auf welchen Wert springt, ist gesetzt und nicht geschätzt, und jedes Szenario sagt das selbst. Eine Literaturangabe an eine handgesetzte Zahl zu heften sähe aus wie eine Kalibrierung.
4. **Der Vergleich vergleicht Weltbilder** (`scenario_sweeps.rahmenszenarien`). Ein Stresstest bleibt lauffähig und einzeln wählbar — er wird nur nicht mehr mitverglichen, und die Kachel sagt, was er ist.

**Was dabei auffiel und in die Begründungen eingegangen ist:** «Business as Usual» hält die CO₂-Abgabe konstant bei 50 EUR. Der Backtest hat am Vortag gemessen, dass der reale EU-Zertifikatspreis 2015 bei 7,6 EUR und 2022/23 bei rund 80 EUR lag, und ReFuelEU schreibt Beimischung ab 2025 verbindlich vor. Das Szenario beschreibt damit **das Ausbleiben einer bereits beschlossenen Verschärfung**, nicht deren Fortsetzung — es darf nicht als «wenn nichts passiert» gelesen werden. Genau das steht jetzt in seinem `vorbehalt`.

**Und eine Bestätigung nebenbei:** Die Kohärenzbehauptung von «Freiwillige Wende» — verbindliche Beimischung schafft die Investitionssicherheit, die den Hochlauf trägt, und ohne Ausweichpfad ist strenge Regulierung politisch nicht durchzuhalten — ist **genau die Rückkopplung, die die CIB-Matrix mit −2 verneint**. Dass sich diese Welt in Prosa mühelos begründen lässt und die Matrix sie als unplausibel führt, ist der vierte unabhängige Beleg für die Leitentscheidung.

**Der Wächter:** [`tests/test_rahmen_traegt_begruendung.py`](../tests/test_rahmen_traegt_begruendung.py), 48 Zusagen. **Er ist der eigentliche Preis von Variante C**: Eine Prosa-Begründung, die niemand prüft, ist in sechs Monaten ein leeres Feld. Er hält, dass jede Datei sagt was sie ist, dass kein Rahmen ohne Begründung und Quellen ausgeliefert wird, dass jeder seinen Vorbehalt trägt, dass **keine Begründung eine Eichung behauptet**, und dass der Vergleich die Stresstests auslässt. Zwei Fallen sind eigens abgedeckt: dass ein leerer Rahmensatz alle Tests grün hielte, und dass `art` einen Standardwert hat — läse eine Datei ihn nicht, fiele sie still auf `stresstest` und verschwände aus dem Vergleich, ohne dass etwas rot wird.

**Was damit nicht getan ist:** Die Impact Balance wird **nicht** implementiert — sie war nur für Variante 2 und 3 fällig. `derive_scenarios` bleibt, wie P2.0-A es hinterlassen hat: Der Score verlässt den Lauf nicht mehr als «Plausibilität». Und **P2.3 (Matrix-Provenienz) entfällt in seiner bisherigen Form**: Es hing an dieser Entscheidung, und unter Variante C gibt es keine Matrix, deren Herkunft herzustellen wäre. Was von ihm bleibt, steht dort.

<details>
<summary>Die drei Möglichkeiten, die zur Wahl standen</summary>

**Was zu tun ist — jetzt eine Wahl, kein Auftrag:** Nach P2.7 entscheiden, was die Rahmenbündel aus P2.0 absichert. Drei Möglichkeiten, in der Reihenfolge ihrer Kosten:

1. **Nichts Formales** — die Kohärenz der Bündel wird in Prosa mit Quellen begründet, wie bei den SSP-Storylines. Billigste Variante, und die ehrlichste, solange keine belegte Matrix existiert.
2. **Morphologische Verträglichkeit** (Variante B der Leitentscheidung) — paarweise: widersprüchlich, angespannt, unproblematisch. Kein Score, nur eine Menge zulässiger Kombinationen. Reicht für den Wächter beim Einrichten.
3. **CIB mit neu erhobener Matrix** (Variante A) — 168 begründete Urteile über gerichtete Einflussstärken. Behält die akademische Anschlussfähigkeit, ist aber unvermeidlich teuer: Die heutigen Werte verneinen die Rückkopplungen, also ist Nachbessern keine Option.

Fällt die Wahl auf 2 oder 3, ist die Impact Balance dann auch zu implementieren — `derive_scenarios` iteriert bereits über alle 128 Kombinationen ([`scenario_consistency.py:209`](../src/cib/scenario_consistency.py)), die Prüfung ist dort rund zwanzig Zeilen. Der Prototyp steht in `_impact_balance_konsistent` im Test und ist übernehmbar.

</details>

**Mitzunehmen, egal wie die Wahl ausfällt — der Nullsummen-Nebenbefund (2026-08-29):** 43 der 84 Urteilsgruppen verletzen Weimer-Jehles Nullsummen-Regel. Nachgeprüft, ob das etwas ändert: **nein.** Bei zwei Zuständen je Faktor wirkt der Gruppenversatz auf beide Zustände gleich und kürzt sich im Vergleich heraus — 0 von 128 Szenarien werden anders beurteilt. Relevant wird es erst, wenn ein Faktor einen **dritten** Zustand bekommt. Wer die Matrix anfasst, weiß das; sonst ist es kein Handlungsbedarf.

**Vorbedingung aus P0.2 — seit 2026-08-26 belegt, nicht mehr nur erwartet:** F7 wird als **Geopolitische Stabilität** geführt, und die Neubewertung der 48 Zellen hat den Passive-Score von 32 auf **19** gedrückt — mit Abstand der niedrigste aller sieben Faktoren. F7 ist damit messbar ein weitgehend exogener Faktor — er wirkt auf das System, wird aber kaum zurückbeeinflusst. Unter Impact Balance hieße das, dass sein Zustand nicht durch das Gleichgewicht bestimmt wird, sondern durch Annahme. Der saubere Umgang: F7 pro Szenario als **fixierten Deskriptor** behandeln und die Impact Balance über F1–F6 rechnen — CIB sieht das ausdrücklich vor. Faktisch ist F7 durch die Ölpreis-Regel heute schon ein exogener Schalter; die Methode zöge damit nur nach, was die Engine tut. Diese Festlegung gehört vor die Umsetzung.

**Fallstrick (2026-08-26), am 2026-08-29 eingetreten:** Echte Impact Balance liefert **null, eine oder viele** konsistente Konstellationen; die heutige Heuristik liefert immer eine sortierte Liste, aus der `top_n=3` gegriffen wird. Das Produktversprechen ist aber ein festes **Tripleset**. Der Fall «weniger als drei» ist keine Hypothese mehr, sondern der gemessene Normalfall — zwei. Die Antwort darauf ist mit P2.0 gefallen: **Das Tripleset kommt künftig aus der Wahl der Rahmenszenarien**, nicht aus einem Ranking. Damit bricht P2.2 die Ergebnisdarstellung aus [P1.3](#p13--szenariogestaltung-neu-denken--erledigt-2026-08-30-datenschema-die-entstehung-bleibt-p20) nicht mehr — P2.0 muss allerdings davor stehen, sonst hat P1.3 nichts, worauf es aufsetzt.

**Vorbedingung:** [P2.7](#p27--backtest-gegen-20152024--erledigt-2026-08-30). Vorher wäre es eine Entscheidung über ein Werkzeug, dessen Wirkung niemand kennt.

**Fertig wenn** ✅ **(2026-08-31):** Die Wahl ist getroffen und begründet; jedes ausgelieferte Rahmenszenario trägt These, Begründung, Quellen und Vorbehalt; kein Stresstest wird mehr als Zukunft angeboten; und ein Wächter hält beides fest, statt es einer Konvention zu überlassen.

**Doku zieht mit:** `docs/cib_role.md`, `docs/cib_rationale.md`, `docs/handbuch/cib.md`, `CLAUDE.md` (Glossar), `docs/entscheidung_szenarienschicht_2026-08-29.md` (die getroffene Wahl gehört dort nachgetragen).

### P2.8 — Die Nachfrage kann nicht wachsen ✅ erledigt 2026-09-03 (Weg A 2026-08-31)

> **Der erste Befund, den der Backtest ohne Zutun geliefert hat.** Er entstand nicht aus einem Audit und nicht aus einer Code-Lektüre, sondern daraus, dass zum ersten Mal etwas außerhalb des Modells als Maßstab danebenlag.

**Befund:** Dem Modell fehlt **jeder** Mechanismus, der Nachfrage wachsen lässt. Die Buchungsrate reagiert auf Preis, Kostendruck, Sättigung und Faktor-Shifts — sämtlich Kanäle nach unten. Die einzige Größe, über die die Nachfragemenge steigen könnte, ist `bevoelkerungsentwicklung` mit **+8 %** über die ganze Kurve; real stieg der europäische Luftverkehr 2015–2019 um **+26 %**. `income_index` existiert, bewegt sich aber nicht mit. Herleitung und Messwerte: [P2.7](#befund-dem-modell-fehlt-jeder-nachfragetreiber-nach-oben-2026-08-31). **Seit dem 2026-09-07 sind es +2,7 %** ([P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31)) — dieselbe Jahresrate, jetzt in Monaten statt in vermeintlichen Jahren gerechnet. Der Befund ist damit **schärfer** geworden, nicht kleiner.

**Zweiter Befund, technisch unabhängig:** Die Bevölkerungskurve ist eine `step_function` mit vier Stützpunkten, der letzte bei **Tick 30**; `_resolve_step_function` hält danach still den letzten Wert. Sie ist die **einzige** Trajektorie im Modell, und ihr Horizont hängt an nichts. Der Backtest läuft 120 Ticks — 90 davon mit eingefrorener Bevölkerung; schon ein Standardlauf über 40 Ticks verbringt ein Viertel seiner Länge jenseits des letzten Stützpunkts. Für eine Stufenfunktion korrektes Verhalten und **genau deshalb unsichtbar**. **Erledigt am 2026-09-07 mit [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31):** Die Kurve trägt Jahresstufen bis Tick 120 — kein Tick des Backtests rechnet mehr mit eingefrorener Bevölkerung.

**Fundstelle:** [`configs/properties.json`](../configs/properties.json) (`bevoelkerungsentwicklung`), [`src/market/property_engine.py:37`](../src/market/property_engine.py) (`_resolve_step_function`), [`src/population/population_sampler.py:606`](../src/population/population_sampler.py).

**Warum es nicht in P2.7 mitbehoben wurde — und das ist die tragende Entscheidung dieses Pakets:** Eine Nachfragemechanik, die *auf* den Backtest hin gebaut wird, kann er danach nicht mehr prüfen. Er bestätigte dann seine eigene Eingabe, und das Modell wäre wieder an nichts geeicht — nur mit einer Zahl daneben, die das Gegenteil behauptet. Der Backtest muss der Maßstab **vor und nach** dem Eingriff sein, mit unverändertem Verfahren.

**Nachgemessen am 2026-08-31 — und die Diagnose ist schärfer als «es fehlt ein Treiber»:** Die Preiselastizität des Buchungsmodells beträgt am Betriebspunkt (130–145 EUR) **−1,83**. Zum Vergleich die Metaanalyse, die im Repo liegt — [Brons, Pels, Nijkamp & Rietveld (2002)](../docs/research/literature/price_elasticities_of_demand_for_passenger_air_travel.pdf), *Journal of Air Transport Management* 8, 165–175, 204 Schätzungen aus 37 Studien: **Mittelwert −1,146, Standardabweichung 0,619**, niedrigster Einzelwert −3,20.

Zwei Befunde daraus, und der zweite wiegt schwerer:

| Preisspanne | Elastizität des Modells |
| --- | ---: |
| 80 → 100 EUR | −0,58 |
| 120 → 140 EUR | −1,44 |
| 140 → 160 EUR | −2,40 |
| 200 → 250 EUR | **−3,54** |

- **Der Betriebspunkt liegt 1,1 Standardabweichungen unter dem Mittel** — innerhalb der beobachteten Verteilung, aber deutlich auf der elastischen Seite.
- **Die Elastizität ist nicht konstant**, sondern versechsfacht sich über eine plausible Preisspanne. Bei 250 EUR ist sie steiler als der **niedrigste** der 204 Schätzwerte der Metaanalyse. Das ist eine Eigenschaft der Sigmoid mit harter Erschwinglichkeitsschwelle, keine Modellierungsentscheidung, die jemand getroffen hätte.

**Und damit ist der Einbruch erklärt, nicht nur beschrieben.** Der Modellpreis stieg 2015–2019 von 132,40 auf 141,16 (+6,6 %). Bei −1,83 erwartet man daraus **−12,1 %** Nachfrage; gemessen wurden **−14,3 %**. **Rund 85 % des Nachfrageeinbruchs sind allein der Preiskanal**, der auf den selbst erzeugten Preisanstieg wirkt — der Rest verteilt sich auf CO₂-Abgabe, Sättigung und Faktor-Shifts.

**Das Modell hat also nicht «zu wenige» Nachfragekanäle, sondern praktisch genau einen** — und der ist steiler als die Literatur und läuft unopponiert. Real stiegen die Fluggastzahlen 2015–2019 um 26 %, *obwohl* die Nominalpreise leicht anzogen: Einkommenswachstum, Netzausbau und Kapazität der Billigflieger haben den Preiseffekt überkompensiert. Von diesen drei kennt das Modell keinen.

**Was zu tun ist**, in dieser Reihenfolge, weil der zweite Punkt ohne den ersten nichts bringt:

1. **Den Horizont einer Trajektorie sichtbar machen.** Nicht die Kurve verlängern — das ist Symptomkosmetik —, sondern melden, wenn ein Lauf über den letzten Stützpunkt hinausgeht. Der Ort dafür ist `validation.py` (Invariante: neue Prüfungen gehören dorthin, nicht in Eingabefelder), und die Prüfung ist billig: `max_ticks` gegen den letzten Stützpunkt jeder Trajektorie.
2. ~~**Den Gegenkanal bauen — und `income_index` ist der naheliegende.**~~ **Erledigt und gemessen am 2026-08-31, siehe oben: Er trägt 1,6 von 40 Punkten.** Er **existiert bereits** als Systemgröße, aber niemand speist ihn: Er steht auf 1,0 und bleibt dort. Das ist der billigste und am besten belegbare Weg, weil Einkommenselastizität für Luftverkehr in derselben Literatur behandelt wird (Brons et al. nennen sie als Determinante; Luftverkehr gilt dort als Luxusgut mit Einkommenselastizität über 1). Die Alternativen — Bevölkerungsverlauf verlängern, eigene exogene Größe — sind beide schwächer belegt: Die Bevölkerung erklärt real nur einen Bruchteil des Wachstums, und eine eigene Größe wäre ein Sammelbecken ohne Entsprechung in den Daten.
   **Der Backtest darf die Wahl nicht treffen.** Er sagt, *dass* ein Gegenkanal fehlt; welcher es ist, entscheidet die Fachlage. Wer die Variante wählt, die den Abstand am stärksten drückt, hat auf ihn hin gebaut.
3. **Die Elastizität ist dabei mit auf dem Tisch**, und zwar als eigene Frage: Ein Gegenkanal, der gegen einen zu steilen Preiskanal ankämpft, verdeckt nur die Ursache. Ob −1,83 am Betriebspunkt richtig ist, ist an Brons et al. prüfbar; dass sie über die Preisspanne von −0,58 auf −3,54 läuft, ist es schwerer zu rechtfertigen. **Beides nicht gleichzeitig ändern** — sonst ist hinterher nicht zu sagen, welche der beiden Änderungen gewirkt hat (Regel: Refactoring und Verhaltensänderung nie im selben Commit, hier auf zwei Verhaltensänderungen angewandt).
4. **Die Wahl im Nutzenmodell verankern**, nicht als Aufschlag daneben. Ein additiver Wachstumsterm auf die Buchungsrate wäre genau die Art Korrektur, die den Backtest grün macht und das Modell schlechter — die Koeffizienten tragen seit P2.1 ihre Herkunft, und ein Term ohne Herkunft fiele dort auf.

#### Der Einkommenskanal ist gebaut — und er reicht nicht (2026-08-31)

> **Das Ergebnis ist kein Fix, und es ist wertvoller als einer.** Der naheliegende Verdacht ist ausgeräumt, und dahinter kommt ein Befund über die **Architektur** zum Vorschein, nicht über einen fehlenden Parameter.

**Was gebaut wurde:** `income_index` wird im Backtest jetzt aus echten Daten gespeist — Eurostat `namq_10_gdp`, reales BIP der EU-27 (verkettete Volumen zu Preisen von 2015, saison- und kalenderbereinigt), vierteljährlich und linear auf Monate interpoliert. Die Reihe liegt eingecheckt in `configs/backtest/bip_real.csv` wie die vier anderen.

**Real und nicht nominal — und die Entscheidung gehört offengelegt, weil sie gegen das eigene Ergebnis ging:** Nominal wüchse die Reihe bis 2019 um **14,8 %** statt 9,0 % und hätte die Nachfragerichtung des Backtests ins Positive gedreht. Gewählt ist trotzdem real, weil [Brons et al. (2002)](../docs/research/literature/price_elasticities_of_demand_for_passenger_air_travel.pdf) — dieselbe Metaanalyse, an der die Elastizitäten dieses Modells gemessen werden — GDP ausdrücklich preisbereinigt verwenden. **Die Wahl nach dem Ergebnis zu treffen wäre genau der Fehler, den dieses Paket vermeiden soll.**

**Vorher geprüft, ob der Kanal überhaupt trägt** — die Empfehlung stand sonst auf einer Vermutung. Die Einkommenselastizität des Buchungsmodells beträgt **+1,10**, gemessen bei festem Preis. Das passt zur Fachlage: Luftverkehr gilt als Luxusgut mit Einkommenselastizität über 1. **Die Form stimmt also**, und das ist eine gute Nachricht über das Modell.

**Das Ergebnis, isoliert gemessen** (zwei Läufe, ein Unterschied — der Einkommens-Override):

| | ohne Einkommen | mit Einkommen | real |
| --- | ---: | ---: | ---: |
| Nachfrage 2015→2019 | −14,2 % | **−12,6 %** | **+26,3 %** |
| Abstand Nachfrageseite | 21,76 | 21,81 | — |
| Abstand **Preisseite** | 1,84 | **1,29** | — |

Drei Dinge stehen darin:

1. **Die Nachfrageseite bewegt sich um 1,6 Punkte von 40.** Der Kanal trägt bei — bis 2022 sind es +6,9 % —, aber er schließt nichts.
2. **Die Preisseite wird deutlich besser** (1,84 → **1,29** vor der Pandemie). Das war nicht das Ziel und ist trotzdem der beste Einzelgrund, die Änderung zu behalten: Ein historischer Lauf, in dem `income_index` als einzige Größe auf 1,0 eingefroren steht, während CO₂-Preis und Öl sich bewegen, war ohnehin nicht zu rechtfertigen.
3. **Der Beitrag wird zu zwei Dritteln aufgezehrt.** Die statische Elastizität hätte +9,8 % erwarten lassen, angekommen sind +3,0 %. Die Differenz absorbieren die Ausgleichsmechanismen des Modells: die Preisrückkopplung (mehr Nachfrage → höherer Preis → weniger Nachfrage; im Lauf gemessen) und die Sättigung.

#### Was dahinter zum Vorschein kommt: dem Modell fehlt die Angebotsseite

**Punkt 3 ist der eigentliche Befund**, und er ist größer als P2.8. Jeder Nachfrageimpuls wird im Modell sofort über den Preis wegbesteuert, weil es **einen einzigen Anbieter ohne Kapazitätsgrenze** gibt: Der Preis ist Kosten plus Aufschlag plus Nachfragerückkopplung, und mehr Nachfrage heißt zwangsläufig höherer Preis.

**Real war es umgekehrt.** Der europäische Luftverkehr wuchs 2015–2019 um 26 %, **während die Realpreise ungefähr flach blieben** — weil das *Angebot* wuchs: Billigfluggesellschaften stellten Sitzplätze bereit, Strecken kamen dazu, Auslastung und Flottengröße stiegen. Wachstum bei konstantem Preis setzt Kapazitätsausweitung voraus, und dafür hat das Modell keine Größe.

**Damit ist die Frage neu gestellt:** Es ist nicht «welcher Nachfragetreiber fehlt», sondern «kann eine Architektur mit einem Anbieter und ohne Kapazität einen wachsenden Markt überhaupt abbilden». Die Antwort ist ehrlicherweise nein — und das steht auch schon in [`grenzen.md`](handbuch/grenzen.md) unter «Ein Anbieter statt eines Marktes», nur bisher ohne die Messung daneben.

**Was daraus folgt — und was ausdrücklich nicht:**

- **Behalten**, was gebaut ist. Der Einkommenskanal ist fachlich richtig, belegt, verbessert die Preisseite und beseitigt einen Widerspruch im Backtest. Er wird **nicht** deshalb zurückgenommen, weil er die Nachfrageseite nicht rettet.
- **Nicht nachjustieren.** Die Versuchung, die Elastizität zu drücken oder nominal statt real zu nehmen, bis die Zahl passt, ist genau der Fehler, gegen den dieses Paket geschrieben ist. Ein Modell, das den Backtest besteht, weil es auf ihn hin eingestellt wurde, ist an nichts geeicht.
- **Die Angebotsseite ist ein eigenes, großes Paket** — und seit dem 2026-08-31 liegt dazu eine **Entscheidungsvorlage** vor: [`entscheidung_angebotsseite_2026-08-31.md`](entscheidung_angebotsseite_2026-08-31.md). Sie enthält einen Befund, der schärfer ist als «es fehlt eine Kapazitätsgrenze»: **Die Nachfragehöhe des Modells folgt der Zielauslastung des Anbieters** (`target_booking_rate`, ausgeliefert 0,37), nicht den Konsumenten. Gemessen verdoppelt sich die Buchungsrate, wenn man nur diese eine Zahl von 0,25 auf 0,65 setzt (0,19 → 0,37), während der Preis sich halbiert — ein Einkommensschock von **+40 %** bewegt sie dagegen um **4,6 %**. Die Zielrate ist rund **zwanzigmal** so wirksam wie das Einkommen, sie trägt keine Quelle, und sie erklärt, warum jeder zusätzliche Nachfragekanal versickert. Empfohlen ist **Weg A** (Kapazität als exogene Systemgröße) allein — er ist Voraussetzung der beiden anderen und der einzige, dessen Wirkung sich am Backtest messen lässt.

**Der ursprüngliche Satz dazu bleibt richtig:** — Kapazität als Systemgröße, mehrere Anbieter, oder wenigstens ein exogener Kapazitätspfad. Das ist Architektur, nicht ein Parameter, und es gehört entschieden statt nebenbei gebaut.
- **Bis dahin gilt die Aussage in `grenzen.md`:** Nachfragezahlen dieses Modells sind keine Mengenprognose. Belastbar bleibt die Richtung einer Annahme, nicht die Höhe.

#### Weg A ist umgesetzt (2026-08-31)

**Gewählt und gebaut ist Weg A** aus der [Entscheidungsvorlage](entscheidung_angebotsseite_2026-08-31.md): Kapazität als exogene Systemgröße. Die dort vorgelegte Messung ist der Grund — **die Nachfragehöhe war eine Konfigurationskonstante**: Der Anbieter steuerte den Preis auf eine feste `target_booking_rate` von 0,37 (ohne Quelle), und diese Zahl war rund **zwanzigmal** so wirksam wie das Einkommen.

**Was gebaut ist:**

- `kapazitaet_index` ist eine Systemgröße mit Verlauf, Standard **1,0**. Sie skaliert die Zielauslastung: `zielauslastung() = target_booking_rate × kapazitaet_index`. Wächst die Kapazität, darf die Nachfrage mitwachsen, ohne dass der Preis sie wegdrückt.
- **Aufgelöst wird sie in `compute_market_metrics`**, wo `system_properties` ohnehin vorliegt — und **vor beiden Verwendern**, damit `apply_market_feedback` und `sync_demand_level` denselben Sollwert sehen. Getrennt gesetzt folgte das Nachfrageniveau einem anderen Ziel als der Preis.
- **Der Standard 1,0 ändert nichts.** Nachgeprüft: Der Backtest liefert mit der neuen Größe und ohne Verlauf exakt dieselben Zahlen wie vorher (1,27 / 23,43). Die Aussage «die Kapazität bleibt gleich» ist damit ausgesprochen statt unterstellt.

**Gemessen, was die Größe tut** (Standardlauf, letztes Viertel):

| `kapazitaet_index` | Buchungsrate | Preis |
| ---: | ---: | ---: |
| 0,8 | 0,2079 | 136,19 |
| 1,0 | 0,2587 | 118,85 |
| 1,5 | 0,3370 | 88,63 |

Mehr Kapazität, mehr Verkehr, niedrigerer Preis — **die Kombination, die das Modell vorher nicht darstellen konnte** und die real das Jahrzehnt 2015–2019 geprägt hat.

#### Der Backtest mit echter Kapazität — beide Richtungen

**Die Reihe:** Eurostat `avia_paoc`, gewerbliche Passagierflüge (`CAF_PAS`), EU-27, monatlich, 120 Monate. **Ein Näherungswert, und das steht dran:** Kapazität ist Flüge × Sitze je Flugzeug × Auslastung; gezählt sind nur die Flüge. Real wuchsen sie 2015–2019 um **14,5 %**, die Passagiere um **26,3 %** — die Differenz sind größere Flugzeuge und höhere Auslastung. Die Reihe **unterschätzt das Kapazitätswachstum systematisch**. Sie ist trotzdem die ehrlichere Wahl als ein gebastelter Sitzplatzindex: gezählt statt gerechnet, und Eurostat veröffentlicht auf dieser Ebene keine Sitzplatzreihe.

**Saisonbereinigt eingespeist, und das ist keine Anpassung an den Backtest:** Die Flugzahlen schwanken saisonal um **57 Indexpunkte** im Jahr, das reale BIP daneben um 3, weil Eurostat es bereinigt liefert. Das Modell kennt **keine Saison** — P2.7 hat das gemessen und deshalb auf Jahresmitteln verglichen. Einen Eingang mit voller Saison in ein Modell ohne Saison zu speisen ist derselbe Kategorienfehler, nur an der anderen Seite: Der Anbieter jagte einem Sollwert hinterher, der sich zwölfmal im Jahr um ein Drittel bewegt, und sein Regler ist auf Trends ausgelegt. Der Unterschied ist gemessen — roh eingespeist verschlechterte die Kapazität die Nachfrageseite auf **25,35**, geglättet verbessert sie sie auf **18,13**.

**Das Ergebnis, mittlerer Abstand in Indexpunkten:**

| | vor P2.8-A | mit Kapazität |
| --- | ---: | ---: |
| **Preis** gesamt | 14,78 | **10,66** |
| Preis 2015–2019 | **1,27** | 3,09 |
| Preis 2022–2024 | 37,31 | **23,27** |
| **Nachfrage** gesamt | 27,54 | 33,36 |
| Nachfrage 2015–2019 | 23,43 | **18,13** |
| Nachfrage 2022–2024 | 34,38 | 58,76 |

**Zwei Verbesserungen und eine Verschlechterung, und alle drei sind erklärbar:**

- **Die Preisseite gewinnt deutlich** (14,78 → 10,66), vor allem nach der Pandemie (37,31 → 23,27). Der Kapazitätseinbruch 2020/21 und der langsame Wiederaufbau erklären einen Teil des Preisanstiegs, den das Modell vorher gar nicht kannte.
- **Die Nachfrageseite vor der Pandemie gewinnt** (23,43 → **18,13**), also dort, wo der Backtest überhaupt etwas über die Mechanik sagt.
- **Die Nachfrageseite nach der Pandemie verliert stark** (34,38 → 58,76) — und der Grund ist der oben benannte Vorbehalt, nicht ein Fehler: Die Flüge erreichten 2024 nur **107,6**, die Passagiere **128,4**. Das Modell folgt jetzt treu den Flügen und verfehlt damit die Sitze. **Dass es dem Näherungswert folgt, ist der Beleg, dass die Mechanik greift** — und dass der Näherungswert zu grob ist, war vorher aufgeschrieben.

**Nicht nachjustiert.** Eine Kapazitätskurve, die auf den Backtest hin eingestellt würde, machte ihn wertlos; ein «Sitze je Flug»-Faktor ohne Datenreihe wäre genau das. Die nächste Verbesserung ist deshalb eine **Datenfrage**, keine Parameterfrage.

**Was Weg A ausdrücklich nicht ist:** eine Kapazitätsschranke im engeren Sinn. Der Anbieter kann seinen Preis weiterhin beliebig senken; er zielt nur auf ein anderes Füllniveau. Eine harte Grenze und ein Investitionszyklus sind Weg B, mehrere Anbieter Weg C — beide bauen auf A auf.

#### Nachtrag am selben Tag: eine Methodik ist ein Bias (P2.8-B)

> **Der Einwand kam von Haiko, und er trifft:** «Es kann ja auch mal mehr Plätze geben, aber gleich teuer bleiben. Es ist eine Simulation, es kann alles passieren. Wenn wir nur eine Methodik haben, hat das System einen Bias und es wird nicht abgenommen.»

**Er hat recht, und die Messung von Weg A zeigt es selbst:**

| `kapazitaet_index` | Preis |
| ---: | ---: |
| 0,8 | 136,19 |
| 1,5 | 88,63 |

**Mehr Plätze erzwangen einen niedrigeren Preis.** Der Anbieter senkte ihn immer, bis er voll war — eine eingebaute Verhaltensannahme. Ausgerechnet die reale Lage 2015–2019, die Weg A darstellbar machen sollte (**mehr Sitze bei flachen Preisen**), war damit *weiterhin* nicht darstellbar. Weg A hat die Kapazität eingeführt, aber nur **eine** Art, auf sie zu reagieren.

**Das ist mehr als eine fehlende Option.** Ein Szenariowerkzeug, das nur eine Verhaltensannahme kennt, beantwortet «was wäre wenn» immer nur unter dieser Annahme — und eine Simulation, die eine Möglichkeit baulich ausschließt, ist keine Simulation dieser Möglichkeit. Ein Fachprüfer liest darin zu Recht einen Bias.

**Umgesetzt: die Preisstrategie ist eine Wahl.**

| Strategie | Verhalten | Kapazität wirkt als |
| --- | --- | --- |
| `auslastung` *(Standard)* | Der Anbieter senkt den Preis, bis die Kapazität gefüllt ist | **Ziel** |
| `marge` | Der Anbieter hält seinen Aufschlag, die Auslastung schwankt | **Schranke** |

**Gemessen, beide Strategien nebeneinander:**

| Kapazität | `auslastung` Rate / Preis | `marge` Rate / Preis |
| ---: | --- | --- |
| 0,5 | 0,1529 / 159,42 | 0,1063 / **189,78** |
| 0,7 | 0,1956 / 141,85 | 0,1064 / **189,78** |
| 1,0 | 0,2587 / 118,85 | 0,1064 / **189,78** |
| 1,3 | 0,3052 / 100,50 | 0,1064 / **189,78** |

Unter `marge` steht der Preis, egal wie viele Plätze da sind — **genau der Fall, der vorher fehlte.**

**Zwei Entscheidungen dabei, beide bewusst:**

1. **Die Kapazität ist nur unter `marge` eine Schranke.** Unter `auslastung` steuert der Preis ohnehin auf sie zu; ein zusätzlicher Deckel schnitte in eine Regelung hinein, die dorthin läuft. Ohne die Schranke täte die Kapazität unter `marge` allerdings **gar nichts** — der Anbieter hielte seinen Aufschlag, und ob zehn oder tausend Sitze da sind, stünde nirgends in der Rechnung.
2. **Wer keinen Platz bekommt, wird zufällig gewählt.** Eine Auswahl nach Zahlungsbereitschaft wäre eine **zweite** Verhaltensannahme — sie unterstellte ein Erlösmanagement, das teure Buchungen bevorzugt. Genau solche stillen Annahmen sind der Grund für dieses Paket; wer sie will, macht sie zu einer eigenen Strategie. Ein Test misst, dass die Zahlungsbereitschaft der Buchenden sich nicht verschiebt.

**Der Standard ändert nichts**, und das ist nachgeprüft: `auslastung` ist die ausgelieferte Strategie, und der Backtest liefert unverändert 10,66 / 33,36. Eine neue Wahlmöglichkeit darf nichts verschieben, solange niemand wählt.

**Ein unbekannter Strategiename scheitert laut** — sonst fiele ein Tippfehler wie `marge_` still auf `auslastung` zurück, und jemand wunderte sich über seine Zahlen. Dieselbe Klasse von Befund wie bei den Shift-Zielen in P2.4.

**Der Wächter:** [`tests/test_preisstrategie_ist_eine_wahl.py`](../tests/test_preisstrategie_ist_eine_wahl.py), elf Zusagen. Die tragende ist nicht «`marge` hält den Preis», sondern das **Paar**: dass er unter `marge` steht *und* sich unter `auslastung` um mehr als 30 EUR bewegt. Ohne die Gegenprobe prüfte der erste Test nur, dass irgendetwas konstant ist.

#### ✅ Wieder geöffnet und geschlossen am 2026-09-03 — die Zusage hielt nicht, und ein Rechenfehler steckte darin

> **Der Einwand von Haiko war richtig, und die Antwort darauf greift nicht.** Ein unabhängiges Audit hat beides nachgemessen. Der Befund ist unangenehm, weil er die tragende Zusage dieses Nachtrags betrifft — und weil der Wächter daneben grün steht.

**Erstens, ein Rechenfehler:** `_kapazitaet_begrenzen` setzt bei knapper Kapazität `booked = False`, **nimmt aber den Sättigungsaufschlag nicht zurück**, den `evaluate_booking` unmittelbar davor vergeben hat. Der Docstring behauptet ausdrücklich das Gegenteil («Die Sättigung bleibt unberührt … weil `booked` zurückgesetzt wird, bevor die Sättigung daran anknüpft») — sie knüpft nicht *danach* an, sie ist schon vergeben. Gemessen (`marge`, `kapazitaet_index = 0,5`, ein Tick, 1000 Personen): 658 wollten buchen, 185 bekamen einen Platz, **473 gehen leer aus und tragen trotzdem `saturation_level = 0,6`** in den nächsten Tick. Sie werden für eine Reise bestraft, die sie nicht angetreten haben.

**Zweitens, und das wiegt schwerer: «mehr Plätze bei gleichem Preis» ist weiterhin nicht darstellbar.** 40 Ticks, letztes Viertel:

| `kapazitaet_index` | `marge` Rate / Preis | `auslastung` Rate / Preis |
| ---: | --- | --- |
| 0,3 | 0,1003 / 189,78 | — |
| 0,5 | 0,1063 / 189,78 | 0,1529 / 159,42 |
| 0,7 | 0,1064 / 189,78 | — |
| 1,0 | 0,1064 / 189,78 | 0,2587 / 118,85 |
| 1,3 | 0,1064 / 189,78 | 0,3052 / 100,50 |

Unter `marge` ändert die doppelte Sitzzahl die Buchungsrate um **0,0001**. Selbst bei 0,3 (Schranke 0,111) bleibt die Rate mit 0,1003 **unter** der Schranke — sie greift dort gar nicht. Der Grund ist **strukturell und nicht numerisch: Eine Obergrenze kann Nachfrage nur senken, nie heben.** Unter `auslastung` wächst der Verkehr, aber nur mit fallendem Preis — also mit genau dem Verhalten, das dieser Nachtrag abschaffen wollte. Der Fall, für den er gebaut wurde, ist damit in **keiner** der beiden Strategien darstellbar.

**Warum der Wächter grün ist:** Er prüft zwei Dinge getrennt, die zusammengehören — Preiskonstanz über Kapazitäten (`marge`, 40 Ticks) und das Greifen der Schranke (ein Tick, künstlich auf 100 EUR gesetzter Preis). Eine Zusage «mehr Kapazität ⇒ mehr Verkehr **bei gleichem Preis**» gibt es nicht, und sie wäre heute rot. Dieselbe Lehre wie bei P2.4-E: *Ein Wächter, der den Mechanismus prüft statt die Zusage, ist grün und nutzlos.*

**Zu tun, in dieser Reihenfolge:**

1. ~~**Die Sättigung erst nach der Rationierung vergeben.**~~ **Erledigt am 2026-09-03.** `_kapazitaet_begrenzen` ist entfallen; `evaluate_booking` macht jetzt alle drei Schritte — ziehen, rationieren, sättigen —, weil sie **eine** Entscheidung sind: wer wirklich fliegt. Ein nachträgliches Zurückrechnen wäre nicht einmal möglich gewesen, weil `min(1.0, …)` die Sättigung klemmt und der Ausgangswert damit verloren ist. `system_properties` ist dafür Pflicht ohne Default geworden (Invariante 1; der AST-Wächter hat die Signatur mitgenommen). **Der Standard bewegt sich nicht:** Unter `auslastung` gibt es keine Schranke, es wird nichts rationiert und auch nichts aus dem Zufallsstrom gezogen — ein Standardlauf über 40 Ticks liefert unverändert 0,2587 / 118,85. Der Wächter ist `tests/test_preisstrategie_ist_eine_wahl.py::TestWerKeinenPlatzBekommtWirdNichtGesaettigt` mit fünf Zusagen; die tragende prüft den **Zustand der Abgewiesenen**, dazu die Vorbedingung (greift die Schranke in diesem Aufbau überhaupt) und die Gegenprobe (wer fliegt, wird sehr wohl gesättigt) — sonst wäre er auch grün, wenn die Sättigung ganz ausfiele.
2. **Neu entscheiden, was die Kapazität unter `marge` tun soll.** Als reine Obergrenze ist sie für ihren Zweck untauglich; sie müsste nach oben wirken (etwa: der Anbieter hält seine Marge, aber unbesetzte Kapazität senkt seine Stückkosten). Das ist eine Modellentscheidung mit eigenem Belegbedarf und gehört entschieden, nicht nebenbei gebaut.
3. **Erst danach den Backtest neu rechnen**, mit unverändertem Verfahren — der Vorher-Wert ist seit dem 2026-09-03 **12,18 / 38,13** (ohne das Basisjahr, siehe P2.7).

#### Erledigt am 2026-09-03 — das Angebot ist ein Merkmal der Alternative

**Gewählt ist der Verfügbarkeitseffekt** (Haiko, 2026-09-03), nicht die Rücknahme der Zusage und nicht Weg B. Die Begründung ist der Mechanismus, den P2.8 selbst benannt hat: Mehr Kapazität heißt in der Wirklichkeit **mehr Frequenzen und mehr Strecken**, also niedrigere generalisierte Reisekosten — Wartezeit, Umsteigen, Zielauswahl. Genau damit wuchs der europäische Verkehr 2015–2019 um 26 % bei flachen Realpreisen.

**Sie gehört deshalb in den Nutzen und nicht in die Ziehung.** Kapazität ist ein Merkmal der *Alternative*, wie der Preis — anders als das Alter, das über Einkommen und Lebensphase wirkt und im Nutzenterm doppelt zählte (P2.4). `booking_probability` trägt seither `gewicht × ln(kapazitaet_index)`.

**Logarithmisch, und das ist keine Bequemlichkeit:** `ln(1) = 0` — der Standardfall ändert damit **exakt nichts**, dieselbe Disziplin wie beim Einführen der Größe selbst. Nachgeprüft: Ein Standardlauf über 40 Ticks liefert unverändert 0,258704 / 118,8492 und dieselbe Faktorlage, und die Preiselastizität steht unverändert bei −1,30 bzw. −2,80.

**Die Höhe ist gesetzt, und sie stand fest, bevor der Backtest damit gerechnet hat.** `verfuegbarkeit_gewicht = 0,5`. Belegt sind Form (Merkmale der Alternative im Nutzen, Ben-Akiva/Lerman 1985; Angebotsgrößen logarithmisch) und Richtung; **eine Zahl gibt die vorliegende Literatur nicht her** — `docs/research/references.md` hat keinen Eintrag zu Frequenz- oder Angebotselastizität. Was 0,5 bedeutet, hängt wie bei der Preiselastizität vom Betriebspunkt ab (im Logit β·(1−p)): gemessen **+0,18** an der ruhenden Bevölkerung bei 140 EUR und **+0,37** im laufenden Modell unter `marge` — beides deutlich schwächer als der Preiskanal, was der durchgängige Befund ist.

**Die Zusage hält jetzt** (40 Ticks, letztes Viertel):

| `kapazitaet_index` | `marge` Rate | `marge` Preis | `auslastung` Rate / Preis |
| ---: | ---: | ---: | --- |
| 0,3 | 0,0692 | 189,78 | — |
| 0,5 | 0,0823 | 189,78 | 0,1404 / 150,69 |
| 0,7 | 0,0931 | 189,78 | — |
| 1,0 | 0,1064 | 189,78 | 0,2587 / 118,85 |
| 1,3 | 0,1151 | 189,78 | 0,3212 / 102,74 |

Unter `marge` steigt der Verkehr um **66 %** von 0,3 auf 1,3 — **bei unverändertem Preis**. Das ist die Kombination, die vorher baulich unmöglich war. Unter `auslastung` wirkt die Kapazität jetzt über **zwei** Kanäle, den Preis und die Verfügbarkeit; das ist kein Doppelzählen desselben Mechanismus, sondern die Preissetzung des Anbieters *und* die Angebotsqualität — aber es gehört gesagt.

**Der Backtest, mit unverändertem Verfahren neu gerechnet:**

| | vor B2 | nach B2 |
| --- | ---: | ---: |
| **Preis** gesamt | 12,18 | **11,96** |
| Preis 2016–2019 | 3,87 | **3,23** |
| Preis 2022–2024 | **23,27** | 23,61 |
| Preis, Richtung getroffen | 3/7 | **4/7** |
| **Nachfrage** gesamt | 38,13 | **34,14** |
| Nachfrage 2016–2019 | 22,66 | **22,47** |
| Nachfrage 2022–2024 | 58,76 | **49,70** |
| Nachfrage, Richtung getroffen | 5/7 | **6/7** |

**Sieben von acht Kennzahlen werden besser, und die beiden wichtigsten sind die Richtungstreffer** — das Modell verspricht Wirkungsrichtungen und keine Niveaus.

**Ein Vorbehalt gehört daneben, sonst liest sich das besser, als es ist.** Der Backtest speist `kapazitaet_index` aus derselben Eurostat-Tabelle, aus der die Zielreihe der Nachfrage kommt (`CAF_PAS` gegen `PAS_CRD`, siehe den Methodikabschnitt in [P2.7](#p27--backtest-gegen-20152024--erledigt-2026-08-30)). Der neue Kanal macht diesen Widerhall **stärker**, nicht schwächer. Die tragende Evidenz für B2 ist deshalb **nicht** der Backtest, sondern die Tabelle darüber: Preis konstant, Nachfrage folgt der Kapazität. Die steht unabhängig von den Daten.

**Der Wächter, und er ist der eigentliche Preis dieses Pakets:** `TestMehrPlaetzeBeiGleichemPreisHeisstMehrVerkehr` prüft die Zusage als **Paar** — beide Größen zugleich, weil jede für sich trivial zu erfüllen wäre. Genau das fehlte: Geprüft waren die Preiskonstanz und das Greifen der Schranke, nie ihr Zusammenspiel. Dazu die Gegenprobe, dass der Standard unberührt bleibt, und der Rand: ohne Sitze fliegt niemand.

**`tests/test_nachfragetreiber.py` ist mitgezogen** — er misst einen Ist-Stand, und der hat sich geändert. Seine Aussage «das Modell hat praktisch genau einen Nachfragekanal» stimmt nicht mehr; die Elastizitätsmessungen darin gelten weiter, weil sie bei unveränderter Kapazität rechnen.

**Fertig wenn** ✅ **(2026-09-03):** Wer keinen Platz bekommt, trägt keinen Sättigungsaufschlag; eine Zusage misst die **Wirkungsrichtung** der Kapazität und nicht nur die Konstanz des Preises; und der Backtest ist mit unverändertem Verfahren davor und danach gerechnet. Herleitung: [Audit Phase 2, B1 und B2](audit_phase2_2026-09-03.md).

**Was damit weiterhin offen ist:** Zwei Strategien sind zwei, nicht alle. Ein Anbieter, der bei knapper Kapazität die Marge *ausweitet* (Erlösmanagement), fehlt ebenso wie mehrere Anbieter im Wettbewerb (Weg C). Die Architektur nimmt beide jetzt auf — `STRATEGIEN` ist eine Liste, kein Schalter.

**Fallstrick — die Reihenfolge der Messung:** Der Backtest wird **vor** dem Eingriff einmal festgehalten (die Zahlen stehen in P2.7 und in `tests/test_nachfragetreiber.py`) und danach neu gerechnet. Wer erst baut und dann misst, hat keinen Vorher-Wert mehr.

**Zweiter Fallstrick — Invariante 1:** Ein Nachfragetreiber ist eine **Zahl aus Python**. Er darf nicht aus einem Agenten-Narrativ stammen und nicht aus einem Vorgabewert, den niemand benannt hat. Wer einen Rückfall braucht, trägt ihn mit Begründung ein — die AST-Prüfung in `test_cost_pressure_source.py` findet ihn sonst.

**Gehalten von:** [`tests/test_nachfragetreiber.py`](../tests/test_nachfragetreiber.py) — er misst den **Ist-Stand** (Horizontlücke in Ticks, Zuwachs der Kurve) und schlägt an, sobald sich einer der beiden bewegt. **Ein rotes Ergebnis ist dort keine Panne**, sondern die Nachricht, dass jemand die Nachfrageseite angefasst hat; dann gehört dieser Abschnitt neu geschrieben und der Backtest neu gerechnet, in dieser Reihenfolge.

#### Der Trajektorien-Horizont, geschlossen am 2026-09-03

**Er hing angeblich an [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31), und das war eine Verwechslung von zwei Fragen.** Ob eine Kurve **zu kurz** ist, hängt wirklich daran, wie lang ein Tick ist — die Frage war damals offen und ist es seit dem 2026-09-07 nicht mehr. Ob ein Lauf **über sie hinausgeht**, hängt an nichts dergleichen: Das ist eine Beschreibung und keine Bewertung. Damit ließ sich der Rest vorziehen, statt ihn ein viertes Mal zu verschieben.

**Gemeldet wird, nicht abgewiesen** — die tragende Entscheidung. Über den letzten Stützpunkt hinauszulaufen ist zulässig und meistens gewollt: Eine CO₂-Abgabe, die ihren Endwert erreicht hat, *bleibt* dort. Ein Fehler in `collect_state_errors` hätte **jeden ausgelieferten Rahmen sofort ungültig gemacht** — alle vier laufen 50 Ticks bei Kurven, die früher enden —, und ein Wächter, der den Normalfall abweist, wird binnen einer Woche entnervt gelockert. Was fehlte, war die **Auskunft**.

**`validation.horizontluecken`** liefert sie; der Runner schreibt sie ins Log, der Assistent zeigt sie vor dem Start. Gemeldet wird der **früheste** Horizont und wie viele Verläufe betroffen sind — eine Liste von dreizehn Zeilen läse niemand.

**Eine flache Baseline hat keinen Horizont**, und diese Unterscheidung entscheidet darüber, ob der Hinweis trägt: Ein Verlauf ohne Stützpunkte sagt «konstant», das ist eine Aussage und keine aufgebrauchte Vorgabe. Ohne sie meldete der Preflight jede Größe des Modells und sagte nichts mehr.

**Gemessen am ausgelieferten Stand** (vier Verläufe mit Stützpunkten):

| Verlauf | letzter Stützpunkt | Standardlauf (40) | Rahmen (50) | Backtest (120) |
| --- | ---: | ---: | ---: | ---: |
| `saf_mandate_share` | 16 | 24 Ticks darüber | 34 | 104 |
| `income_index` | 20 | 20 | 30 | 100 |
| `carbon_tax_level` | 30 | 10 | 20 | 90 |
| `bevoelkerungsentwicklung` | 30 | 10 | 20 | **90** |

Der letzte ist der Anlass gewesen: die **einzige** Trajektorie des Modells, und der Backtest rechnet drei Viertel seiner Länge mit eingefrorener Bevölkerung.

**Gehalten von** `TestEinLaufSagtWieWeitSeineVorgabenReichen` in `tests/test_nachfragetreiber.py`, vier Zusagen — darunter die beiden, die den Hinweis brauchbar halten: dass eine flache Baseline **nicht** gemeldet wird, und dass der Hinweis **kein Fehler** ist.

**Fertig wenn** ✅ **(2026-09-03):** Die Herkunft des Nachfragewachstums ist entschieden und begründet; der Backtest ist mit unverändertem Verfahren neu gerechnet, mit beiden Zahlen nebeneinander; und ein Lauf, der über den letzten Stützpunkt hinausgeht, sagt es — im Log und vor dem Start.

**Doku zieht mit:** `CLAUDE.md` (Glossar, Invarianten), `docs/handbuch/grenzen.md`, `docs/handbuch/vergleiche.md` (ein Schnitt — Läufe von davor und danach sind nicht vergleichbar), `docs/backtest_vorlauf.md`.

### P2.3 — Matrix-Provenienz herstellen ✅ abgeschlossen 2026-08-31 (entfallen, Rest erledigt)

**Befund:** Alle 168 Zellen in `cib_frozen.json` haben ein leeres `reasoning`-Feld; `metadata.source` sagt `expert_defined_aviation_domain_v2` (Basis: Vorlesungsfolien, Experte = das Team selbst). Für einen Prototyp legitim — aber die Kalibrierung ist genau das Asset, das später verkauft wird.

**Fundstelle:** [`configs/cib_frozen.json`](../configs/cib_frozen.json), erzeugt von [`scripts/rebuild_cib_frozen.py`](../scripts/rebuild_cib_frozen.py).

**Zusätzlich (2026-08-26):** Neben dem befüllten `cells`-Dict liegt in derselben Datei ein zweites, durchgängig leeres `entries: []`. Eine unbenutzte Struktur mitten im eingefrorenen Asset — beim Durchgehen mit entfernen oder befüllen, je nachdem, wofür sie gedacht war.

**Belegt am 2026-08-29 — «beim Durchgehen fallen inhaltliche Fehler auf» ist eingetreten, ohne dass jemand durchgegangen ist:** Vier der 120 unbegründeten Zellen verneinen die tragende Rückkopplung des Systems (`F1.1→F2.2`, `F1.1→F6.2`, `F1.1→F5.2`, `F4.1→F2.2`, alle auf **−2**): Die Matrix sagt, Wachstum beruhige die Regulierer. Real ist es umgekehrt. Der Befund steht in [`audit_findings.md`](audit_findings.md) und ist der Grund, warum P2.3 nicht mehr «Begründungen nachtragen» heißen kann — man kann keine Begründung unter eine Zahl schreiben, die in die falsche Richtung zeigt.

**Die Bedingung ist eingetreten (2026-08-31).** Das Paket hing an [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31), und dort steht seit dem 2026-08-31 **Variante C**. Damit gilt der Satz, den dieses Paket selbst für diesen Fall vorgesehen hatte: **Es gibt keine Matrix mehr, deren Provenienz herzustellen wäre.** 168 Zellen zu begründen hieße, Werte zu belegen, die keine Rolle mehr tragen — und vier davon zeigen nachweislich in die falsche Richtung.

**Was noch offen ist, und es ist etwas anderes:** `cib_frozen.json` liegt weiterhin im Repo und wird weiterhin gelesen. Es **jetzt** zu entfernen wäre voreilig — der Score ist seit P2.0-A entschärft (er verlässt den Lauf nicht mehr als «Plausibilität»), und die Datei trägt vier Messwerte, auf denen die Leitentscheidung steht (`tests/test_cib_einachsigkeit.py`). Wird sie gelöscht, ist auch der Beleg weg, warum die Rolle abgewählt wurde.

**Was zu tun bleibt** — ein kleines Paket, keine 168 Urteile:

- `metadata.source` sagt, dass die Matrix **keine bewertende Rolle mehr trägt**, statt `llm_proposed_pending_review_v3` weiterzuschleppen. Das Label verspricht eine Prüfung, die nicht mehr kommt.
- Das leere `entries: []` verschwindet oder bekommt eine Erklärung.
- `docs/cib_role.md` sagt, warum die Datei noch da ist, obwohl sie nichts mehr entscheidet.

#### Der Rest ist erledigt (2026-08-31)

**Drei Handgriffe, kein Paket** — und alle drei betreffen, was die Datei über sich selbst *behauptet*, nicht ihre Werte:

- **`metadata.source` heißt jetzt `beleg_keine_bewertende_rolle`.** Vorher stand dort `llm_proposed_pending_review_v3`, und das war eine Zusage an den nächsten Leser, die niemand einlöst: Es kündigte eine fachliche Abnahme an, die seit P2.2 nicht mehr kommt — sie prüfte Werte, die nichts mehr entscheiden.
- **Die Notiz trägt die vier Messwerte**, auf denen die Abwahl steht, statt einer Provenienz-Warnung. Sie stehen damit *in* der Datei und nicht nur in einem Dokument daneben — wer sie öffnet, liest im ersten Satz, wozu sie noch da ist.
- **`entries` ist weg.** Eine durchgängig leere Liste neben den 168 Zellen; `CIBMatrix` führt sie als «Deprecated: flat entry list for backward compatibility», kein aktiver Lesepfad füllte oder wertete sie aus, und das Modell setzt sie ohnehin auf `[]`. Wer die Datei zum ersten Mal öffnete, sah zwei Strukturen und musste raten, welche die eigentliche ist.

**Der Erzeuger ist mitgeändert, und das war der eigentliche Punkt:** `scripts/rebuild_cib_frozen.py` schrieb beides. Nur die Datei zu korrigieren hätte genau bis zum nächsten Aufruf des Skripts gehalten. Zur Probe einmal neu gebaut — der Neubau schreibt nichts zurück.

**Was ausdrücklich *nicht* passiert ist:** Die Datei wurde **nicht gelöscht**. Sie trägt die vier Messwerte, auf denen die Leitentscheidung steht; wer sie entfernt, entfernt den Beleg dafür, warum die Rolle abgewählt wurde.

**Der Wächter:** sechs Zusagen in [`tests/test_cib_einachsigkeit.py`](../tests/test_cib_einachsigkeit.py) — dort, wo die vier Messwerte ohnehin liegen. Einer davon prüft den **Erzeuger** statt nur die Datei; und er prüft die *Zuweisung* von `source`, nicht das bloße Vorkommen des alten Labels: Die neue Notiz nennt es absichtlich, um zu erklären, warum es ersetzt wurde. Ein blankes «kommt nicht vor» wäre rot, obwohl alles stimmt — genau die Sorte Prüfung, die man später entnervt lockert.

**Fertig wenn** ✅ **(2026-08-31):** Die Datei behauptet nichts mehr über ihre eigene Zukunft, und wer sie öffnet, liest im ersten Absatz, dass sie ein Beleg ist und kein Werkzeug.

**Doku zieht mit:** `docs/cib_rationale.md`, `docs/handbuch/cib.md`, `docs/entscheidung_szenarienschicht_2026-08-29.md`.

### P2.4 — Das Alter prägt die Person ✅ erledigt 2026-08-31 (erste Fassung korrigiert)

**Befund:** `age` wird beim Sampling einmal gezogen und danach nie fortgeschrieben. Über einen langen Lauf bleibt die Bevölkerung eingefroren, während Preise, Regulierung und Werte sich bewegen — die Altersgruppen-Statistik beschreibt dauerhaft den Startzustand.

**Fundstelle:** [`src/population/population_sampler.py:173-229`](../src/population/population_sampler.py) (Sampling), Auswertung Zeile 436-444, Modell [`src/models/population_models.py:42`](../src/models/population_models.py).

#### Korrektur am 2026-08-31, noch am selben Tag

> **Die erste Fassung dieses Pakets hat die Frage falsch herum gestellt.** Sie stellte fest, dass `age` für das Verhalten **exakt** folgenlos ist, und behandelte das als *Begründung* dafür, nichts zu bauen. Das war der **Befund**, nicht die Rechtfertigung. Ein Achtzehnjähriger ist ein anderer Reisender als ein Siebzigjähriger — dass das Modell den Unterschied nicht kannte, war die Lücke, und die ist jetzt geschlossen.

**Was beim Nachmessen herauskam, war schlimmer als «age steht nicht im Nutzenterm»:** **Alle** Merkmale wurden unabhängig gezogen. Die Korrelation des Alters mit Einkommen, Zahlungsbereitschaft, Preisempfindlichkeit, Umweltbewusstsein und Substitutionsbereitschaft lag durchgängig unter **0,08** — reines Stichprobenrauschen. Ein 90-Jähriger hatte genauso wahrscheinlich ein hohes Einkommen und niedrige Preisempfindlichkeit wie ein 25-Jähriger. Die Bevölkerung war ein Beutel unkorrelierter Zahlen, kein Bild von Menschen.

**Die Gestaltungsentscheidung — und sie ist leicht falsch zu treffen:** Das Alter formt die Merkmale **beim Ziehen** (`AltersProfil` in `PropertiesConfig`) und steht **nicht** als Term in `booking_probability`. Alter verursacht keine Buchung; es wirkt über Einkommen, Lebensphase und Reiseanlass — und die stehen dort bereits. Ein zusätzlicher Alters-Term zählte doppelt, und die Nutzenfunktion ist ein Discrete-Choice-Modell über *entscheidungsrelevante Merkmale* (Ben-Akiva/Lerman 1985), nicht über Soziodemografie.

**Fünf Kanäle, Richtung belegt und Höhe gesetzt** — dieselbe Trennung wie bei den Buchungskoeffizienten (P2.1), und `docs/research/references.md` verlangt sie für das Alter ausdrücklich: «empirisch als erklärende Variable genutzt, **meist ohne universelle Formel**».

| Kanal | Form | Wirkung |
| --- | --- | --- |
| Einkommen | Glocke, Gipfel bei 50 | ±25 % um den Basiswert |
| Zahlungsbereitschaft | folgt dem Einkommen | dito |
| Preisempfindlichkeit | Kehrseite des Einkommens | +0,20 an den Rändern |
| Umweltbewusstsein | linear fallend | −0,020 je Jahrzehnt |
| Bahnbereitschaft | linear fallend | −0,015 je Jahrzehnt |

**Das Ergebnis, bei 140 EUR gemessen (Stand 2026-08-31):**

| Gruppe | Einkommen | Preisempf. | **Buchungsneigung** |
| --- | ---: | ---: | ---: |
| 18–25 | 0,871 | 0,705 | **25,2 %** |
| 26–35 | 1,026 | 0,659 | **47,8 %** |
| 36–50 | 1,175 | 0,604 | **57,8 %** |
| 51–65 | 1,150 | 0,632 | **54,7 %** |
| 66+ | 0,909 | 0,712 | **36,2 %** |

Der Glockenverlauf des Erwerbslebens — Menschen in der Lebensmitte fliegen am meisten. Das ist keine Kalibrierung, sondern die Folge der eingebauten Form; dass sie der Realität entspricht, ist das Argument für die Form.

> **Nachgemessen am 2026-09-03 (B7e des Audits), und eine Zeile stimmt nicht mehr.** Die Zahlen sind seit P2.9 (Altersverteilung aus Eurostat) und [P2.12](#p212--einkommen-wirkte-nur-als-schwelle--erledigt-2026-09-03) (Einkommen im Nutzen) gewandert; bei n = 5000 lauten sie **22,9 / 43,2 / 58,8 / 59,7 / 34,3 %**. **Die Aussage «die Lebensmitte fliegt am meisten» hält** — 36–65 gegen 22,9 % bei den Jüngsten und 34,3 % bei den Ältesten. **Die Rangfolge *innerhalb* der Mitte hält nicht:** 51–65 liegt heute leicht über 36–50 (59,7 gegen 58,8), und der Unterschied ist ohnehin Rauschen — die Glocke ist um den Gipfel bei 50 symmetrisch, beide Gruppen liegen gleich weit davon entfernt. Die Tabelle oben bleibt als Messung ihres Datums stehen; wer die Fein­struktur zitiert, zitiert Rauschen.

**Ein Nebenergebnis, auf das nicht hingebaut wurde und das deshalb zählt:** Die **Preiselastizität** des Modells verbesserte sich von **−1,83 auf −1,27**. Das Metaanalyse-Mittel bei Brons et al. (2002) liegt bei −1,146 mit Standardabweichung 0,619 — statt 1,1 Standardabweichungen sind es jetzt **0,2**. Auch die Spanne über plausible Preise schrumpfte von −0,58…−3,54 auf −0,46…−2,76 und liegt damit nicht mehr jenseits des niedrigsten aller 204 Schätzwerte. **Der Grund ist mechanisch:** Eine wirklich heterogene Bevölkerung kippt nicht mehr geschlossen über die Erschwinglichkeitsschwelle.

**Und ein Ergebnis, das schlechter wurde — hier, damit es nicht untergeht:** Der Backtest verliert auf der Nachfrageseite leicht (21,81 → **23,43** vor der Pandemie), die Preisseite bleibt (1,29 → **1,27**). **Nicht zurückgebaut:** Die Änderung ist durch den Mechanismus begründet, nicht durch die Punktzahl, und [P2.8](#p28--die-nachfrage-kann-nicht-wachsen--erledigt-2026-09-03-weg-a-2026-08-31) sagt bereits, dass die Nachfragelücke strukturell ist. Ein Modell zurückzudrehen, weil es nach einer Korrektur auf *einer* Kennzahl schlechter abschneidet, ist genau die Anpassung an den Backtest, gegen die dieses Projekt anschreibt.

**Was von der ersten Fassung gilt — mit neuer Begründung:** **Es gibt weiterhin keinen Alterungspfad.** Nicht mehr, weil das Alter folgenlos wäre, sondern weil echte Alterung hieße, alle abgeleiteten Merkmale je Tick neu zu bestimmen — aus einer Person würde eine andere — *und* festzulegen, wie viele Jahre ein Tick ist. Letzteres ist die Kalendersemantik, die [Invariante 5](../CLAUDE.md) ausschließt. Die Bevölkerung bleibt eine **wiederholte Querschnittserhebung**: Wächst sie, kommen frisch gezogene Personen dazu, und die Altersstruktur bleibt stabil.

**Daraus folgt eine Eigenschaft, die überrascht und richtig ist:** Eine *bestehende* Person nachträglich zu altern ändert ihr Verhalten nicht — ihr Einkommen wurde beim Ziehen festgelegt. `tests/test_alter_formt_die_person.py` hält genau das fest, damit es niemand für einen Fehler hält.

#### Nachtrag am selben Tag: die Gesellschaft altert, die Kohorte nicht (P2.4-D)

**Der zweite Einwand traf den wunden Punkt:** «Es kommt doch darauf an, wie viele Ticks man macht — evtl. möchte man Jahre, und dann verändert es sich doch.» Zwei Dinge sind daraus geworden.

**Erstens ein eigener Befund über die Tick-Dauer** ([P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31)): Sie ist bereits dreimal entschieden, um den Faktor 12 verschieden. Meine Begründung gegen Alterung stand also auf einer Invariante, die als Verhaltensaussage nicht hält.

**Zweitens die Messung, die zeigt, warum «einfach altern lassen» trotzdem falsch wäre:**

| | Altersmittel | Buchungsrate |
| --- | ---: | ---: |
| Tick 0 | 50,5 | 0,4818 |
| Tick 20 | 69,0 | 0,3985 (−17,3 %) |
| Tick 40 | 82,9 | **0,2526 (−47,6 %)** |

Eine mitalternde Kohorte ohne Nachwuchs stirbt sich zu Tode. Real altern Menschen zwar, aber es kommen junge nach und alte scheiden aus — die Altersstruktur verschiebt sich dadurch **langsam**.

**Umgesetzt ist deshalb die Verschiebung, nicht die Alterung:** `altersmittel_jahre` ist seit dem 2026-08-31 eine Systemgröße mit Verlauf, genau wie `income_index` seit P2.8. Wer neu in die Bevölkerung kommt, wird aus der Verteilung gezogen, die *dann* gilt. Standard ist der Eurostat-Wert 50,8; **ohne Verlauf bleibt die Gesellschaft stationär**, und das ist eine gültige Aussage statt eines Versehens.

**Die Größenordnung stimmt damit:** Neun Jahre höheres Altersmittel senken die Buchungsrate um **4,5 %** — ein Kompositionseffekt, kein Zusammenbruch. Ein Szenario «alternde Gesellschaft» ist damit rechenbar, ohne dass eine Person je einen Geburtstag hat.

**Ohne neuen Kontextparameter** (Invariante 1): Der Wert kommt aus `system_properties`, die `run_population_tick` ohnehin bekommt. Ein eigenes Argument mit Default hieße «irgendein Altersmittel» und wäre in jedem Tick dasselbe.

#### Korrektur noch am selben Tag: ohne Nachwuchs passiert nichts (P2.4-E)

> **P2.4-D war fehlerhaft ausgeliefert**, und der Hinweis kam wieder von außen: «Es werden ja auch immer wieder Menschen geboren, die sterben ja nicht aus.»

**Der Fehler:** `altersmittel_jahre` verschiebt die Verteilung, aus der **neue** Personen gezogen werden — und neue Personen entstanden nur, wenn die Bevölkerung **wuchs**. Bei gleichbleibender Größe lebten dieselben tausend Menschen ewig weiter. Gemessen: Über 30 Ticks blieb das Altersmittel bei **50,8**, während der Verlauf 60 verlangte. Die Vorgabe war **wirkungslos**.

**Warum der Wächter das nicht gefangen hat, und das ist die Lehre:** Er prüfte die **erste Ziehung** — die stimmte. Die Zusage lautete «eine Gesellschaft kann altern», geprüft war «eine Ziehung berücksichtigt das Altersmittel». *Ein Wächter, der den Mechanismus prüft statt die Zusage, ist grün und nutzlos.*

**Umgesetzt:** `erneuerungsrate` als Systemgröße — der Anteil der Bevölkerung, der je Tick ausgetauscht wird. Wer geht, geht **zufällig**; wer kommt, wird aus der Verteilung gezogen, die *jetzt* gilt. Damit nähert sich die Zusammensetzung der Vorgabe exponentiell an, mit der Rate als Geschwindigkeit.

**Der erste Anlauf lief dabei verkehrt herum, und das gehört festgehalten:** Er gewichtete das Ausscheiden mit dem Alter, weil «Alte sterben eher» realistischer aussieht. Gemessen zog die Bevölkerung damit von 50,8 auf **45,5**, während die Vorgabe 60 verlangte — wer die Ältesten entfernt und aus der vollen Verteilung nachzieht, verjüngt zwangsläufig. Dahinter steckt ein Denkfehler, der über die Funktion hinausgeht: **`altersmittel_jahre` ist ein Kompositionsziel, keine Sterbetafel.** Eine Ausscheide-Mechanik daraufzusetzen lässt zwei Modelle gegeneinander rechnen. Wer echte Geburten und Sterbefälle will, braucht ein demografisches Modell mit Eintritt bei 18 und Austritt nach Sterbetafel — und dann ist die Bevölkerungsgröße nicht mehr frei vorgebbar.

**Gemessen, Start 50,8, Ziel 60,0, Bevölkerung konstant:**

| Erneuerungsrate | Tick 20 | Tick 90 | Tick 130 |
| --- | ---: | ---: | ---: |
| 0,0 (Standard) | 50,8 | 50,8 | 50,8 |
| 0,05 je Tick | 55,6 | **60,0** | 60,0 |

**Und der Klemm-Wächter aus P2.9 hat dabei mitgeredet**, ungeplant: Ein Zielalter von 40 klemmt 12,5 % der Ziehungen an der Untergrenze 18 und scheiterte laut. Das ist richtig — eine *junge* Gesellschaft hat viele Minderjährige, die Bevölkerung des Modells besteht aber per Definition aus Erwachsenen. Die erlaubte Spanne von `altersmittel_jahre` ist deshalb **44 bis 64**, und diese Grenzen sind gemessen statt gemeint.

**Der Standard bleibt 0,0** — keine Erneuerung, also der Stand von vorher. Der Grund war zunächst, dass eine sinnvolle Rate an der **Tick-Dauer** hängt und die offen war. **Seit [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31) ist sie das nicht mehr** (2026-09-07): Ein Tick ist ein Monat, realistisch wären rund **0,0012** je Tick — ein Zwölftel der jährlichen 0,014. Der Standard bleibt trotzdem 0,0, jetzt aus dem Sachgrund: Eine stehende Gesellschaft ist eine gültige Aussage, und eine Erneuerung ohne Verlauf für `altersmittel_jahre` tauscht Personen gegen statistisch gleiche aus. Ein Rahmenszenario, das eine alternde Gesellschaft rechnen will, setzt **beides** — den Verlauf und die Rate.

**Der Wächter:** [`tests/test_alter_formt_die_person.py`](../tests/test_alter_formt_die_person.py), zweiundzwanzig Zusagen — darunter die, die vorher fehlte: dass eine Vorgabe **über mehrere Ticks** ankommt, gemessen gegen den Zustand ohne Erneuerung. Er ersetzt `test_bevoelkerung_altert_nicht.py`, dessen Prämisse mit dieser Korrektur entfallen ist.

<details>
<summary>Die erste Fassung vom selben Tag — als Beleg, wie die Frage falsch stand</summary>

#### Entschieden am 2026-08-31: kein Alterungspfad

> **Die Bevölkerung ist eine wiederholte Querschnittserhebung, keine Kohorte.** Jeder Tick zeigt «die Bevölkerung, wie sie ist» — nicht dieselben Personen, die älter werden. Das wird als **Grenze benannt**, nicht als Mechanik gebaut.

**Drei Messungen tragen die Entscheidung**, alle am 2026-08-31 nachgerechnet:

1. **`age` ist für das Verhalten inert — exakt.** Alle tausend Personen um zwanzig Jahre zu altern (Altersmittel 62,8 → 76,1) verändert die mittlere Buchungswahrscheinlichkeit um **0,00e+00**. Nicht «wenig»: `booking_probability` liest WTP, Einkommen, Umweltbewusstsein, Preissensitivität, Substitutionsbereitschaft und Sättigung — kein Alter. Und die Shift-Regeln erreichen es nicht; sie kennen genau drei Ziele.
2. **Die Verteilung ist stationär, nicht eingefroren.** Wächst die Bevölkerung von 1000 auf 1080, kommen 80 **frisch gezogene** Personen dazu — aus derselben Verteilung. Die Altersstruktur verschiebt sich dadurch um höchstens **0,39 Prozentpunkte** je Gruppe. «Die Statistik beschreibt dauerhaft den Startzustand» ist also die falsche Beschreibung des Befunds: Sie beschreibt eine *stabile Gesellschaft*, und das ist eine andere Aussage.
3. **Alterung hieße Kalenderzeit.** Eine Rate «Jahre je Tick» *ist* die Semantik, die [Invariante 5](../CLAUDE.md) ausschließt — egal ob als Property, als Kohortenwechsel oder als Anteilverschiebung. Man müsste eine harte Architektur-Invariante aufweichen, um eine Statistik zu bewegen, die in keine Rechnung eingeht.

**Punkt 1 ist der tragende, und er kehrt die Frage um:** Solange das Alter nichts beeinflusst, wäre ein Alterungspfad reine Dekoration — Aufwand und ein gebrochener Invariant für eine Zahl im Diagramm. Wer Alterung *will*, will in Wahrheit, dass **Alter das Verhalten beeinflusst**; das ist eine Modellierungsentscheidung mit eigenem Belegbedarf und nicht dieses Paket.

**Und ein Fund kam beim Entscheiden dazu, der es zusätzlich erledigt:** Die Altersverteilung ist nicht nur folgenlos, sie ist **falsch gezogen** — 41 % der Bevölkerung sind exakt 90 Jahre alt, geklemmt an der Obergrenze ([P2.9](#p29--die-altersverteilung-ist-an-die-wand-geklemmt--erledigt-2026-08-31)). Man würde also eine kaputte Verteilung sorgfältig altern lassen.

**Was stattdessen passiert ist:**

- Die Grenze steht im Handbuch (`grenzen.md`, `akteure.md`) — in der Sprache der Nutzer, nicht als Fußnote: Die Altersstatistik beschreibt die *Zusammensetzung*, nicht denselben Menschen über die Zeit.
- Ein Wächter hält die **Voraussetzung** der Entscheidung fest, nicht ihr Ergebnis: `tests/test_bevoelkerung_altert_nicht.py` (inzwischen gelöscht, ersetzt durch [`tests/test_alter_formt_die_person.py`](../tests/test_alter_formt_die_person.py)). Sobald `age` anfängt, Verhalten zu beeinflussen, fällt der tragende Grund weg — und dann gehört die Entscheidung neu auf den Tisch, statt stillschweigend weiterzugelten. **Ein rotes Ergebnis ist dort keine Panne, sondern genau diese Nachricht.**
- Ein Nebenbefund ist separat behoben: Ein unbekanntes Ziel einer `shift_rule` verschwand still — eine Regel auf `age` tat nichts, ein Tippfehler wie `price_sensitivty` ebenso. Beides scheitert jetzt laut, beim Laden und zur Laufzeit.

**Fertig wenn** ✅ **(2026-08-31):** Die Entscheidung ist getroffen, im Handbuch als Grenze benannt, und ein Wächter meldet, wenn ihre Voraussetzung entfällt.

</details>

**Fertig wenn** ✅ **(2026-08-31, korrigierte Fassung):** Das Alter beeinflusst nachweislich das Verhalten — gemessen an der Buchungsneigung je Altersgruppe, nicht an der Anwesenheit einer Formel; jeder Koeffizient trägt seine Herkunft mit der Trennung belegt/gesetzt; die Altersverteilung stammt aus Daten; und das Handbuch sagt, was das Modell mit dem Alter tut und was nicht.

**Doku zieht mit:** `docs/handbuch/akteure.md`, `docs/handbuch/grenzen.md`, `docs/handbuch/tick-und-lauf.md`.

### P2.9 — Die Altersverteilung ist an die Wand geklemmt ✅ erledigt 2026-08-31

**Befund:** **41 % der simulierten Bevölkerung sind exakt 90 Jahre alt.** Nicht ungefähr — exakt, weil 90 die Obergrenze ist und dort geklemmt wird. Das Altersmittel liegt bei **62,8**, der Median bei 71,5, und **53 % sind über 65**. Als Bild einer Bevölkerung, die Flugreisen nachfragt, ist das offensichtlich falsch.

**Ursache, gemessen:** `configs/properties.json` beschreibt `age` als `lognormal` mit `mean: 73.0, std_dev: 1.0`. `_sample_lognormal` bildet daraus `mu = log(73)` und `sigma = 1.0` — **`mean` wird also als Median der Lognormalen gelesen, nicht als ihr Mittelwert**, und `std_dev` als Sigma der *zugrundeliegenden Normalverteilung*. Eine Lognormal mit diesen Parametern hat den Median 73, den Mittelwert **120** und legt **41,8 %** ihrer Masse über 90. Genau dieser Anteil landet auf der Klemme.

**Fundstelle:** [`src/population/population_sampler.py:91`](../src/population/population_sampler.py) (`_sample_lognormal`), [`configs/properties.json`](../configs/properties.json) (`individual_properties`, `age`).

**Zwei Fehler, und sie sind zu trennen:**

1. **Die Klemmung ist still.** `np.clip` am Ende macht aus jeder zu breiten Verteilung eine mit einem Stapel am Rand — ohne Meldung. Das ist der mechanische Teil, und er betrifft **jede** Verteilung, nicht nur `age`: Wer `wtp_eur` ähnlich parametrisiert, bekommt dasselbe, ohne es zu merken.
2. **Die Parameter bedeuten nicht, was ihre Namen versprechen.** Ein Feld `mean` sollte den Mittelwert setzen. Das zu ändern verschiebt allerdings **jede** Lognormal-Verteilung der Config auf einen Schlag.

**Was zu tun ist:** Erst 1, dann 2 — und **nicht in einem Commit**. Die Klemmung laut zu machen ist eine reine Schranke ohne Modellentscheidung: Übersteigt der geklemmte Anteil eine Schwelle, ist die Verteilung falsch parametrisiert und der Lauf soll es sagen. Erst danach die Frage, was `mean` heißen soll — und die zieht eine dritte nach sich, die **einen Beleg braucht**: Welche Altersverteilung ist für europäische Flugreisende eigentlich richtig? Die heutige Angabe hat keine Quelle, und eine neue frei zu wählen wäre dieselbe handgesetzte Zahl wie vorher, nur eine hübschere.

**Warum es nicht dringend ist — und trotzdem eingeplant:** `age` beeinflusst **nichts** im Modell ([P2.4](#p24--das-alter-prägt-die-person--erledigt-2026-08-31-erste-fassung-korrigiert)). Kein Preis, keine Buchung, keine Faktorlage hängt daran. Der Schaden ist deshalb kein Rechenfehler, sondern ein **Vertrauensschaden**: Die Altersgruppen-Ansicht des Dashboards zeigt einem Fachprüfer eine Bevölkerung, die es nicht geben kann, und stellt damit alles daneben in Frage.

**Fallstrick:** Wer nur die Config repariert, ohne die Klemmung laut zu machen, behebt einen Fall und lässt den Mechanismus stehen. Die nächste Verteilung, die über ihre Grenze läuft, fällt wieder niemandem auf.

#### Erledigt am 2026-08-31, in der vorgesehenen Reihenfolge

**Zuerst die Schranke, dann die Zahl** — wie oben verlangt:

- `pruefe_verteilung` zieht vor dem Aufbau der Bevölkerung eine Stichprobe je Merkmal und weist eine Verteilung ab, die mehr als **10 %** ihrer Masse an eine Grenze klemmt (`KLEMM_DECKEL`). Sie läuft mit **eigenem Generator**, damit die Prüfziehung den Zufallsstrom des Laufs nicht verschiebt — sonst hinge die Bevölkerung daran, ob geprüft wurde. Der Wächter deckt **jedes** Merkmal ab, nicht nur `age`.
- Die Altersverteilung kommt aus **echten Daten**: Eurostat `demo_pjangroup`, EU-27, Stand 1.1.2023 — Mittelwert **50,8**, Standardabweichung **18,8**, begrenzt auf **18–90**. Untergrenze 18, weil ein Individuum hier eine Buchungsentscheidung trifft; Kinder buchen nicht. Geklemmt werden damit 6,0 % statt 41,8 %, gemessen liegen jetzt 1,6 % auf der Obergrenze statt 41 %. **Und 3,9 % auf der Untergrenze** (nachgetragen am 2026-09-03, B7f des Audits): Beziffert war bisher nur die obere Klemme, weil sie der Anlass war. Zusammen sind es **5,5 %** — deutlich unter dem `KLEMM_DECKEL` von 10 %, aber die Zahl gehört genannt, weil dieselbe Prüfung beide Ränder überwacht und ein Leser sonst denkt, es gehe nur um oben.
- **Bewusst die Gesamtbevölkerung und nicht die der Flugreisenden.** Wer davon fliegt, soll das Modell über Einkommen und Zahlungsbereitschaft ergeben ([P2.4](#p24--das-alter-prägt-die-person--erledigt-2026-08-31-erste-fassung-korrigiert)), statt es in die Ziehung vorwegzunehmen. Eine Verteilung der *Reisenden* hineinzuschreiben hieße, die Antwort vor die Rechnung zu stellen — derselbe Fehler, den P2.0 an der CIB-Schicht abgeräumt hat.
- `IndividualProperty.quelle` trägt die Herkunft, wie `BookingCoefficient` seit P2.1.

**Beim Beschaffen ist der bekannte Fallstrick wieder eingetreten**, und diesmal hat das Nachrechnen ihn gefangen: Für **2024** liefert Eurostat die Gruppen `Y30-34` und `Y45-49` **nicht** — die zurückgegebenen Gruppen summieren sich auf 370 von 449 Millionen. Wer einfach summiert, bekommt eine Verteilung ohne zwei Erwerbsalters-Gruppen und damit eine zu alte. Genommen ist deshalb **2023**, wo die Gruppen sich **exakt** auf `TOTAL` addieren. Dieselbe Lehre wie beim verschwundenen EEX-Jahrgang in P2.7: *Eine Summe gegen die Gesamtsumme zu halten kostet eine Zeile und fängt den stillen Fehler.*

**Was offen bleibt, kleiner als gedacht:** `mean` heißt bei `lognormal` weiterhin *Median* — die Falle steckt im Feldnamen. Sie ist jetzt im Docstring von `_sample_lognormal` benannt und durch den Klemm-Wächter entschärft: Eine Lognormal, die deswegen aus dem Ruder läuft, scheitert laut. Die Umbenennung selbst verschöbe **jede** Lognormal-Verteilung der Config auf einen Schlag und gehört deshalb nicht hier hinein.

**Fertig wenn** ✅ **(2026-08-31):** Eine Verteilung, die einen nennenswerten Teil ihrer Masse an eine Grenze klemmt, sagt es; die Altersverteilung trägt eine Quelle wie die Buchungskoeffizienten seit P2.1.

**Doku zieht mit:** `docs/handbuch/akteure.md`, `docs/handbuch/ref-config.md`, `CLAUDE.md` (Glossar, falls sich die Bedeutung von `mean` verschiebt).

### P2.5 — State Explorer: Grounding durchsetzen statt darum bitten ✅ erledigt 2026-08-31

**Befund (neu am 2026-08-26):** Der State Explorer ist im Glossar als "grounded Q&A ausschließlich über abgeschlossene Run-Daten — keine erfundenen Zahlen" beschrieben. Durchgesetzt wird davon nichts: `build_grounded_context_block` baut einen Kontextblock, `ask()` reicht ihn samt Frage ans LLM weiter und gibt die Antwort unverändert zurück. Ob die Antwort nur Zahlen aus diesem Block enthält, prüft niemand — die Zusage ist ein Prompt, keine Schranke. Dieselbe Klasse wie P2.1 und P2.2: ein Claim, den der Code nicht einlöst, nur an der Oberfläche, an der ein Kunde ihn zuerst ausprobiert.

**Fundstelle:** [`src/reporting/state_explorer.py:241`](../src/reporting/state_explorer.py) (`build_grounded_context_block`), [`:323-334`](../src/reporting/state_explorer.py) (`build_prompt`, `ask`), Ansicht in [`dashboard/web/views/explorer.py`](../dashboard/web/views/explorer.py).

**Was zu tun ist:** Nach dem LLM-Aufruf die Zahlen aus der Antwort ziehen und gegen die Zahlen im Kontextblock abgleichen. Was sich nicht wiederfindet, wird markiert oder die Antwort zurückgewiesen — welche der beiden Härten die richtige ist, ist eine Produktentscheidung und gehört ins Paket. Bis dahin die Formulierung im Glossar und im Handbuch abschwächen (siehe die Regel "Was der Code nicht tut, darf die Doku nicht behaupten").

#### Umgesetzt am 2026-08-31

**Die offene Produktentscheidung — markieren oder zurückweisen — ist gefallen: markieren.** Zurückweisen wäre die härtere Zusage und die falsche. Eine Antwort, die eine Prozentangabe korrekt ausrechnet, wäre damit unbrauchbar, obwohl sie stimmt; eine markierte Antwort lässt den Leser entscheiden und verschweigt nichts, was die Zurückweisung auch nicht täte.

**Was die Prüfung beantwortet, und was ausdrücklich nicht:** «Steht diese Zahl in den Laufdaten?» — **nicht** «ist diese Zahl richtig». Eine korrekt gerechnete Differenz («der Preis stieg um 12,50 Euro») steht nirgends in den Daten und wird markiert. Das ist gewollt: Ein Prüfer soll sehen, welche Zahl **abgelesen** und welche **gerechnet** ist. Ob die Rechnung stimmt, kann keine Textprüfung wissen, und der angehängte Vorbehalt behauptet es auch nicht.

**`ask` gibt seit P2.5 ein `Antwort`-Objekt zurück** (`text`, `unbelegt`, `geprueft`) statt einer Zeichenkette. `str()` hängt den Vorbehalt an — damit bleibt jede Oberfläche richtig, die die Antwort als Text behandelt, und verliert die Warnung nicht. Dashboard, Legacy-UI und CLI sind entsprechend nachgezogen.

**Fehlalarme sind hier teurer als übersehene Fälle**, und das hat den Zuschnitt bestimmt: Wer dreimal eine Markierung an einer offensichtlich richtigen Zahl sieht, liest die vierte nicht mehr. Deshalb gelten als belegt: gerundete Angaben («rund 140» zu 140,38), beide Dezimalschreibweisen, Tausendertrennung, und Prozentangaben gegen gespeicherte Anteile («48,2 %» zu 0,4818).

**Der wunde Punkt war die Zahlenzerlegung**, und der erste Anlauf lag dort falsch: Sein Muster für Tausendertrennung fraß die Nachkommastellen — `0.4818` wurde als `0.481` erkannt und zu **481** normalisiert. Eine Buchungsrate von 48 % galt damit als unbelegt, obwohl sie in den Daten stand: ein Fehlalarm auf der häufigsten Zahl des ganzen Modells. Trennzeichen sind mehrdeutig (deutsch Komma, englisch Punkt, in einer Antwort womöglich beides); entschieden wird jetzt nach der **Stellenzahl**, und der mehrdeutige Fall `1.080` ist als Tausenderlesart benannt statt stillschweigend gewählt.

**Am laufenden System geprüft**, nicht nur im Test: Eine Demo-Antwort wird nicht fälschlich markiert, und gegen einen echten Lauf mit zwei Ticks fängt die Prüfung sowohl den erfundenen Preis (`213,50`) als auch die erfundene Runde (`Tick 40`).

**Der Wächter:** [`tests/test_explorer_grounding.py`](../tests/test_explorer_grounding.py), 28 Zusagen. **Mehr davon prüfen die Ruhe der Prüfung als ihren Alarm** — acht Fälle, in denen nichts markiert werden darf, gegen drei, in denen etwas markiert werden muss. Dazu die Nachstellung des Zerlegungsfehlers und die Zusage, dass `ask` kein rohes `str` mehr zurückgibt: Fiele es darauf zurück, wäre die Prüfung weg und alles andere trotzdem grün.

#### Die Trennschärfe steht seit dem 2026-09-03 dabei (B7c)

Die Prüfung fragt «steht diese Zahl irgendwo in den Laufdaten» — **ohne Bezug zur Größe**. Das ist gewollt und im Docstring sauber gesagt; unsichtbar war die Folge: Je mehr Zahlen im Kontextblock stehen, desto eher findet sich für eine erfundene zufällig eine Entsprechung. Ein «belegt» aus einem Block mit dreißig Zahlen wiegt anders als eines aus einem mit dreihundert.

**Behoben nicht durch eine schärfere Prüfung, sondern durch eine ehrlichere Auskunft.** Eine Zuordnung von Zahl zu Größe wäre eine zweite Behauptung — sie müsste raten, worauf sich «140,38» im Satz bezieht, und läge damit genau dort falsch, wo es darauf ankommt. `Antwort.kontextzahlen` führt stattdessen mit, gegen **wie viele verschiedene** Zahlen geprüft wurde, und der angehängte Vorbehalt nennt beide Zahlen: «Geprüft wurden 2 Zahlen der Antwort gegen 6 verschiedene Zahlen der Laufdaten.» Die Grenze bleibt; sie steht jetzt dabei.

**Verschiedene, nicht alle** — sonst maße die Zahl die Länge des Blocks statt seiner Vielfalt, und die Vielfalt entscheidet, wie leicht ein Zufallstreffer fällt. **Und nur am Vorbehalt**, nicht unter jeder Antwort: Sonst stünde eine Fußnote unter jeder Auskunft und die Markierung, auf die es ankommt, ginge darin unter.

**Fertig wenn** ✅ **(2026-08-31, ergänzt 2026-09-03):** Eine Antwort mit einer nicht im Kontext belegten Zahl wird erkannt; Tests decken den belegten und den erfundenen Fall ab; und der Vorbehalt sagt, wie trennscharf die Prüfung an dieser Stelle überhaupt war.

**Doku zieht mit:** `docs/handbuch/abfrage.md`, `docs/handbuch/zahlen-und-sprache.md`, `CLAUDE.md` (Glossar "State Explorer").

### P2.6 — Ensemble-Läufe je Rahmenszenario ✅ erledigt 2026-08-31

> **Das Band steht jetzt auch im Bild.** `aggregate_runs` liefert die Perzentile (seit 2026-08-30), und **Aussage 1 zeichnet sie** (seit 2026-08-31): getönte Flächen hinter Preis- und Buchungslinie, dazu ein Satz, der sagt, was sie sind und was nicht.

**Der Befund war enger als gedacht — und schlimmer.** `run_multi` gab es, und es rechnete korrekt N Läufe. Was fehlte, war die Auswertung: `aggregate_runs` zählte **nur Buchhaltung** — wie viele Läufe, welche Seeds, wie viele Ereignisse. Über das, wofür man mehrere Läufe überhaupt rechnet, sagte es nichts. Ein Ensemble ohne Verteilung ist eine teure Art, denselben Punktwert mehrfach zu bekommen.

**Was umgesetzt ist:**

- `ensemble_baender` rechnet Perzentile je Tick über alle Läufe, für `booking_rate` und `ticket_price`. Sie hängen im `aggregate` und landen darüber in `multi_run_summary.json`.
- **Median plus 80-Prozent-Intervall, nicht Minimum und Maximum.** Die Ränder einer Stichprobe wandern mit jeder weiteren Wiederholung nach außen; ein min/max-Band sähe mit fünfzig Läufen breiter aus als mit zehn, ohne dass sich am Modell etwas geändert hätte.
- **Das Band ist so lang wie der kürzeste Lauf.** Sonst stünde am Ende ein Perzentil aus zwei statt fünfzig Werten — das sähe wie ein zusammenlaufendes Band aus und wäre nur eine dünner besetzte Stichprobe.
- Eine fehlende Messung (`booking_rate` ist optional) fällt **heraus**, statt als 0 in das Perzentil einzugehen. Eine fehlende Messung ist keine Messung von null.

**Gemessen am 2026-08-30** (20 Läufe, 12 Ticks, Standardrahmen):

> **Die Niveaus sind seit P2.4 und P2.8 andere** — nachgemessen am 2026-08-31 liegt die Buchungsrate in Tick 7 bei 0,3353 / 0,3520 / 0,3668 und der Ticketpreis in Tick 13 bei 146,20 / 147,73 / 149,55. **Die Bandbreiten sind es nicht**, und die sind die eigentliche Zusage: 0,0315 statt 0,032 und 3,34 € statt 3,36 €.

| Reihe | Tick | p10 | p50 | p90 | Bandbreite |
| --- | ---: | ---: | ---: | ---: | ---: |
| `booking_rate` | 7 | 0,3096 | 0,3215 | 0,3414 | 0,032 |
| `ticket_price` | 13 | 138,90 | 140,38 | 142,26 | 3,36 € |

**Der Laufzeit-Fallstrick ist entschärft — und zwar mit einer Zahl.** Der Plan verlangte, vor der Umsetzung zu messen, wie lange das dauert. Ein Lauf über 40 Ticks braucht **0,64 s** im Modus «Nur Zahlen» und **1,75 s** ohne Sprachmodell. Fünfzig Wiederholungen über acht Szenarien — 400 Läufe — sind damit **4,3 bzw. 11,7 Minuten**. Mit Sprachmodell wären es Stunden, und für die Streuung der Zahlen trägt es nichts bei: **Ein Ensemble rechnet ohne Modell**, und `compute_mode` sagt das im Artefakt.

**Der Wächter:** `tests/test_ensemble_band.py`, dreizehn Zusagen. Die tragende ist `test_es_ist_nicht_ueberall_eine_linie` — sie misst nicht, *dass* ein Band da ist, sondern dass es **Breite hat**. Ohne P2.1 wäre sie rot: Fünfzig Seeds hätten fünfzig identische Buchungsverläufe ergeben, und das Band hätte die Streuung des Bevölkerungs-Samplings gezeigt. Dazu die Gegenprobe: Ein **einzelner** Lauf muss alle drei Perzentile zusammenfallen lassen — sonst läge die Breite an der Rechnung statt an den Läufen.

#### Die Darstellung (2026-08-31)

**Die offene Frage war, welche der vier Aussagen das Band bekommt.** Antwort: **Aussage 1 — «Preis und Nachfrage»**, und zwar ohne Ermessensspielraum. `ENSEMBLE_REIHEN` wertet genau `ticket_price` und `booking_rate` aus, und das sind genau die beiden Größen dieser Ansicht. Für die übrigen drei gäbe es keine Daten; dort ein Band zu zeichnen hieße, eines zu erfinden.

**Gezeichnet wird das 10.–90.-Perzentil als Fläche hinter der Linie**, je Reihe in ihrer eigenen Farbe. Vier Entscheidungen dabei, jede aus einem Grund:

- **Die Fläche kommt zuerst in die Figur.** Plotly zeichnet in der Reihenfolge des Hinzufügens; darüber gelegt verschleierte sie genau das, was die Aussage trägt — den Median.
- **Die Linie bleibt der eine gewählte Lauf**, das Band ist der Hintergrund. Nicht umgekehrt: Wer einen Lauf ausgewählt hat, will ihn sehen, nicht seinen Ersatz.
- **Ein Einzellauf bekommt kein Band** — und ein «Ensemble» aus einem Lauf auch nicht. Dort fallen alle Perzentile zusammen (siehe `_perzentil`), die Fläche hätte die Breite null, und übrig bliebe eine Legende, die Streuung *behauptet*.
- **Das Band reicht nur so weit, wie es trägt** (`baender["ticks"]`), die Linie darf länger sein. Gestreckt liefe es am Ende auf Perzentile aus zwei statt fünfzig Werten hinaus.

**Der Fundort ist eine Ebene über dem Lauf:** Ein Ensemble legt seine Läufe als Unterverzeichnisse eines Batch-Ordners ab und die Zusammenfassung daneben. `_baender` liest `run_dir.parent / "multi_run_summary.json"`; fehlt sie, bleibt es bei der Linie — kein Fehlerfall, sondern der Normalfall.

**Die Farbe wird abgeleitet, nicht danebengestellt** (`theme.band_fill`). Plotly braucht für eine Fläche eine Farbe *mit* Alpha, die Tokens sind Hex ohne. Die Umrechnung an der Zeichenstelle zu machen hieße, dort einen Farbwert zu bilden — genau das, was Regel 4 verbietet. So ändert sich das Band mit, wenn sich `price` ändert.

**Ein Befund kam aus dem Browser, und nur von dort:** Die erste Fassung stellte die Zahl der Läufe in den Diagrammtitel und nannte die Bandspuren «Ticketpreis: 80 % der Läufe». Beides zusammen brach die waagerechte Legende auf **zwei Zeilen** (58 px statt 29) und schob sie in den Titel. Gemessen im laufenden Dashboard, nicht im Test — die Figur ist in beiden Fällen gültig, sie sieht nur falsch aus. Titel und Namen sind jetzt kurz, die Zahl der Läufe steht in der Notiz darüber, wo Platz dafür ist.

**Der Wächter:** `tests/test_ensemble_band.py` hat acht Zusagen dazubekommen — dass ein Ensemble sein Band bekommt und ein Einzellauf nicht, dass die Fläche hinter der Linie liegt, dass die Farbe aus den Tokens kommt und in beiden Modi verschieden ist, und dass das Band nicht über seine Reichweite hinaus gezeichnet wird. Er registriert die Plotly-Templates **selbst**: Sie hingen bis dahin an der Testreihenfolge (`test_web_theme.py` tat es nebenbei), und ein Test, der allein rot und im Verbund grün ist, ist keiner.

**Doku mitgezogen:** `docs/handbuch/vergleiche.md` (die Streuung wird jetzt ausgerechnet statt abgelesen — samt der Laufzeitmessung), `docs/handbuch/ref-ausgaben.md` (neuer Abschnitt «Läufe mit Wiederholungen»).


**Befund (neu am 2026-08-29):** Das Produkt liefert Punktwerte. «Yields fallen um 11 %» ist eine Behauptung; «Yields fallen um 8 bis 14 %» ist eine Aussage. Solange ein Rahmenszenario genau einen Lauf bedeutet, gibt es keine Bandbreite — und ohne Bandbreite keine Grundlage, auf der eine Strategieabteilung planen kann.

**Fundstelle:** `run_multi` in [`src/orchestration/simulation_runner.py`](../src/orchestration/simulation_runner.py) (existiert und wurde am 2026-08-27 begradigt: Die Folge beginnt bei `DEFAULT_SEED`, nicht mehr bei 0), [`src/orchestration/scenario_sweeps.py`](../src/orchestration/scenario_sweeps.py).

**Was zu tun ist:** Je Rahmenszenario eine Serie von Läufen mit `base_seed + index` rechnen und die Ergebnisse als **Perzentile** auswerten statt als Einzelverlauf. In den Ansichten aus P1.3 als Band darstellen, nicht als Linie. Die Zahl der Wiederholungen gehört in die Konfiguration, nicht in den Code.

**Vorbedingung:** [P2.1](#p21--buchungsmodell-echte-ziehung-statt-schwellwert--erledigt-2026-08-30). **Ohne echte Ziehung ist ein Ensemble sinnlos** — heute ist die Buchungsentscheidung deterministisch, fünfzig Seeds erzeugen dann fünfzig identische Verläufe der Buchungsrate. Wer P2.6 vor P2.1 baut, misst die Streuung des Bevölkerungs-Samplings und hält sie für die Unsicherheit des Modells.

**Fallstrick — Laufzeit:** Fünfzig Läufe je Szenario bei acht Szenarien sind 400 Läufe. Wie lange ein realistischer LLM-Lauf dauert, steht bis heute nirgends (siehe [«Was bewusst nicht in diesem Plan steht»](#was-bewusst-nicht-in-diesem-plan-steht)). Vor der Umsetzung einmal messen — sonst wird die Ensemble-Auswertung zu dem Feature, das im Demo nicht durchläuft. Ein Ensemble braucht die Narrative nicht; der Rechenmodus ohne Sprachmodell ist hier vermutlich der richtige, und dann sagt `compute_mode` das auch im Artefakt.

**Fertig wenn** ✅ **(2026-08-31):** Ein Rahmenszenario liefert ein Band statt einer Linie — als Zahlen *und* im Bild; bei gleichem `base_seed` ist es reproduzierbar; und ein Test zeigt, dass zwei Wiederholungen desselben Rahmens unterschiedliche Verläufe erzeugen — sonst misst das Ensemble nichts.

**Doku zieht mit:** `docs/handbuch/vergleiche.md` (der Schnitt gehört benannt — Läufe von davor und danach sind nicht vergleichbar), `docs/handbuch/ergebnisse-lesen.md`, `docs/handbuch/ref-ausgaben.md`, `README.md`.

### P2.7 — Backtest gegen 2015–2024 ✅ erledigt 2026-08-30

> **Das Modell ist zum ersten Mal an etwas gemessen, das nicht aus ihm selbst stammt — und das Ergebnis ist zweigeteilt, in zwei Richtungen.**
>
> **«Geeicht» stand hier bis zum 2026-09-03, und das war die falsche Vokabel** (D1 des Audits). Geeicht wurde nichts: **Kein einziger Koeffizient ist an diese Daten angepasst worden** — P2.1 hält das ausdrücklich fest («Keiner der acht Werte ist an Daten geprüft»), und der Absatz «Was der Backtest nicht belegt» weiter unten sagt es auch. Ein Fachprüfer liest «geeicht» als «kalibriert» und sucht danach die Schätzung, die es nicht gibt. Der Unterschied ist keine Wortklauberei, sondern genau die Trennung, auf der dieses Projekt sonst besteht — und die Formulierung ist von hier aus nach außen gewandert: Im Artefakt «Bilanz der Modellsubstanz» wurde sie zur **Überschrift**. Auf der **Preisseite** trifft es den realen Pfad vor der Pandemie auf **1,84 Indexpunkte** genau und verfehlt ihn danach um **38,4**. Auf der **Nachfrageseite** liegt es schon vor der Pandemie um **21,8** daneben — und zwar *verkehrt herum*: Es lässt die Nachfrage auf 86 fallen, wo real 126 stand. Beides ist gemessen, nicht geschätzt.

**Entschieden am 2026-08-30** (Haiko), auf Grundlage von [`vorschlag_backtest_daten_2026-08-30.md`](vorschlag_backtest_daten_2026-08-30.md): 2020/21 werden **mitgerechnet, aber nicht bewertet**; der EUA-Preis kommt über **EEX**.

**Die Daten liegen im Repo** (`configs/backtest/`), geholt von `scripts/backtest_daten_holen.py` — einmalig, nicht zur Laufzeit, dasselbe Muster wie bei den Schriften. Für einen Backtest ist das Einchecken keine Bequemlichkeit, sondern Bedingung: Eine später revidierte Reihe änderte sonst rückwirkend ein veröffentlichtes Ergebnis. `quellen.json` hält je Reihe URL, Abrufdatum, Zeilenzahl und Prüfsumme fest.

| Reihe | Monate | Quelle |
| --- | ---: | --- |
| `eua_auktionspreis` | 119 | EEX, Emission Spot Primary Market Auction Report — gemeinsame EU-Auktion allgemeiner Zertifikate |
| `brent_rohoel` | 120 | Europe Brent Spot FOB (EIA), über die FRED-Spiegelung bezogen |
| `hicp_flugreisen` | 120 | Eurostat `prc_hicp_midx`, COICOP `CP0733`, Basis 2015 = 100 — **Zielreihe Preis** |
| `fluggaeste` | 120 | Eurostat `avia_paoc`, `PAS_CRD`, EU27 — **Zielreihe Nachfrage** |

**Zwei Funde beim Beschaffen, beide der stillen Sorte:**

- **Ein ganzer Jahrgang verschwand lautlos.** Der erste Filter prüfte, ob die Auktionsbezeichnung auf «EU» endet — 2016 heißt sie `EU (TCAP)`. Zwölf Monate fielen heraus, und 107 statt 120 Monate über zehn Jahre fallen niemandem auf. `einordnen` scheitert jetzt bei einer **unbekannten** Bezeichnung laut, statt sie zu überspringen.
- **Die Januar-2021-Lücke ist echt.** Es fand keine gemeinsame EU-Auktion statt; der Kalender der vierten Handelsperiode begann im Februar. Sie wird **benannt, nicht gefüllt** — für die Eingabe in den Lauf wird fortgeschrieben, für die Auswertung nicht.

> **Diese Zahlen sind vom 2026-08-30 und beschreiben das Modell von damals.** P2.4 (Alter), P2.8 (Einkommen, Kapazität) und P2.8-B (Preisstrategie) haben es seither verändert; **die jeweils aktuellen Werte stehen in [`backtest_vorlauf.md`](backtest_vorlauf.md)**, das bei jedem Aufruf neu geschrieben wird. Jedes Paket unten führt seine eigene Vorher-Nachher-Messung.

**Das Ergebnis der Preisseite** (`ticket_price` gegen `hicp_flugreisen`; Index, Basis 2015 = 100, Jahresmittel):

| Jahr | Modell | Zielreihe | Abstand |
| --- | ---: | ---: | ---: |
| 2016 | 93,86 | 97,42 | −3,56 |
| 2017 | 107,78 | 102,64 | +5,14 |
| 2018 | 104,84 | 104,95 | −0,11 |
| 2019 | 106,62 | 107,00 | −0,38 |
| 2020 | 101,35 | 102,48 | −1,13 *(ungewertet)* |
| 2021 | 104,80 | 105,98 | −1,18 *(ungewertet)* |
| 2022 | 105,97 | 131,93 | −25,96 |
| 2023 | 101,17 | 144,57 | −43,40 |
| 2024 | 102,46 | 148,25 | −45,79 |

**2015–2019: mittlerer Abstand 1,84 Indexpunkte. 2022–2024: 38,38.** Das erste ist bemerkenswert für ein Modell, dessen Koeffizienten sämtlich handgesetzt sind — es wurde nie darauf angepasst. **Es ist aber kein Beleg**: Vier freie Jahre, und 2015 liegt durch die Indexbasis per Konstruktion auf null. Das zweite ist ein klarer Fehlschlag: Die realen Flugpreise sind seit 2022 um rund die Hälfte über das Niveau von 2015 gestiegen, das Modell steht bei +2 %.

**Die Kennzahl war beim ersten Anlauf falsch, und das ist die Lehre des Pakets.** Er verglich die **monatliche** Bewegungsrichtung und kam auf 44 % Treffer — unter dem Münzwurf. Das sah aus wie ein vernichtender Befund über das Modell und war einer über die Messung: Die Zielreihe schwankt saisonal um **40 Indexpunkte im Jahr**, das Modell um **12**, weil es keine Saison kennt. Der Monatsvergleich maß vor allem, ob das Modell eine Sommersaison hat. Verglichen wird jetzt auf **Jahresmitteln**; die Saisonkennzahl bleibt daneben stehen als das, was sie ist. Wieder dasselbe Muster: *Eine Messung findet, was wirklich dasteht — auch über sich selbst.*

**Das Ergebnis der Nachfrageseite** (`booking_rate` gegen `fluggaeste`):

| Jahr | Modell | Zielreihe | Abstand |
| --- | ---: | ---: | ---: |
| 2016 | 101,39 | 106,34 | −4,95 |
| 2017 | 84,12 | 114,54 | −30,42 |
| 2018 | 88,62 | 121,54 | −32,92 |
| 2019 | 85,77 | 126,28 | −40,51 |
| 2020 | 93,67 | 33,76 | +59,91 *(ungewertet)* |
| 2021 | 84,01 | 45,60 | +38,41 *(ungewertet)* |
| 2022 | 76,92 | 99,63 | −22,71 |
| 2023 | 80,29 | 118,70 | −38,41 |
| 2024 | 85,70 | 128,38 | −42,68 |

**2015–2019: 21,76. 2022–2024: 34,60.** Das ist nicht nur ungenauer als die Preisseite, es ist **eine andere Art von Fehler**: Die Preisseite trifft und bricht dann weg, die Nachfrageseite läuft von Anfang an in die **falsche Richtung**. Das Modell lässt die Buchungsrate bis 2019 auf 86 sinken; real stiegen die europäischen Fluggastzahlen auf 126.

**Zwei Gegenproben, damit daraus kein Messfehler wird:**

- **Quote gegen Zahl.** Die Zielreihe zählt Passagiere, `booking_rate` ist ein Anteil — der naheliegende Verdacht. Gegen `total_booked` gemessen wird es kaum besser: **17,56** statt 21,76 vor der Pandemie. Es ist also kein Artefakt der Bezugsgröße.
- **Beide Seiten aus einem Lauf.** `modellpfade()` liefert Preis und Nachfrage aus **demselben** Lauf. Zwei Läufe verglichen zwei verschiedene Welten, und die Nachfrage antwortete auf einen anderen Preis als den, der geprüft wird.

**Die Ursache ist gemessen und benannt** ([Befund unten](#befund-dem-modell-fehlt-jeder-nachfragetreiber-nach-oben-2026-08-31)): Dem Modell fehlt jeder Mechanismus, der Nachfrage wachsen lässt. Repariert wird das hier **nicht** — eine Modelländerung, die auf den Backtest hin gebaut würde, könnte er danach nicht mehr prüfen.

**Der Wächter:** `tests/test_backtest_vorlauf.py`, 22 Zusagen. Er hält **nicht das Ergebnis**, sondern die Eigenschaften der Messung: dass die Kalenderzuordnung nur im Backtest lebt und kein Datum ins Rahmenszenario gelangt (Invariante 5), dass jede Reihe ihre Herkunft trägt und eine ohne abgewiesen wird, dass 2020/21 in der Tabelle stehen und **nicht** in der Kennzahl, und dass der Ölpreis indexiert wird, der CO₂-Preis nicht.

**Die Reihenfolge war Absicht:** Erst die Preisseite, dann die Nachfrage — träfe schon der Preispfad die Größenordnung nicht, sägte die Nachfrageseite nichts mehr dazu, weil sie am Preis hängt. Sie tut es, und deshalb ist der Nachfragebefund aussagekräftig: Er liegt **nicht** daran, dass das Modell den Preis verfehlt.

**Was der Backtest nicht belegt**, ausdrücklich: Die 1,84 Indexpunkte der Preisseite sind bemerkenswert, aber kein Beweis — vier freie Jahre, und 2015 liegt durch die Indexbasis per Konstruktion auf null. Der Backtest sagt, **wo** das Modell trägt und wo nicht; er macht es nicht richtig.

#### Zwei Methodikbefunde, nachgetragen am 2026-09-03

> Beide stammen aus einem unabhängigen Audit. Sie gehören hierher, weil der Backtest die stärkste Aussage des Projekts trägt. **Der erste ist am selben Tag behoben, der zweite bleibt als Vorbehalt stehen.**

**Erstens: Das Basisjahr steckte in der Kennzahl — behoben am 2026-09-03.** `bewerten()` indexiert Modell **und** Zielreihe auf 2015 = 100; 2015 hat damit per Konstruktion den Abstand 0 und geht trotzdem in jeden Mittelwert ein:

| | bis 2026-09-03 (mit 2015) | seither (ohne 2015) |
| --- | ---: | ---: |
| Preis 2015–2019 | 3,09 | **3,87** |
| Preis, alle bewerteten Jahre | 10,66 | **12,18** |
| Nachfrage 2015–2019 | 18,13 | **22,66** |
| Nachfrage, alle bewerteten Jahre | 33,36 | **38,13** |

Ein Fünftel des Vorpandemie-Fensters war ein Datenpunkt, der **nicht anders ausfallen kann**. Der Vorbehalt oben nannte die Tautologie («2015 liegt durch die Indexbasis per Konstruktion auf null»), zog daraus aber keine Konsequenz für die Kennzahl — und die Ergebnistabelle zeigt die Jahre **2016–2024**, das Basisjahr also gar nicht. **Der veröffentlichte Wert war aus der veröffentlichten Tabelle nicht nachrechenbar**, und genau das prüft ein Fachprüfer zuerst nach.

**Umgesetzt:** Das Basisjahr steht in der Tabelle und **nicht** im Abstand; es trägt dort die Marke «Basis, Abstand per Konstruktion 0». Die vier Kennzahlen stehen seither auf **12,18 / 3,87** (Preis) und **38,13 / 22,66** (Nachfrage), nachgerechnet mit unverändertem Verfahren.

**Eine Unterscheidung ist dabei wichtig, und sie ist keine Spitzfindigkeit:** Tautologisch ist das **Niveau** im Basisjahr, nicht die **Bewegung** von dort zum Folgejahr. Beide Reihen bewegen sich zwischen 2015 und 2016 frei. Die Richtungskennzahl rechnet deshalb weiterhin über acht Werte und sieben Übergänge — sie steht unverändert bei 3/7 und 5/7 —, der Abstand über sieben Jahre. Zwei Marken statt einer: «Basis» ist eine Aussage über die *Messung*, «ungewertet» eine über das *Modell*; sie mit demselben Wort zu markieren hätte den ersten Fall als Modellschwäche gelesen.

**Gehalten von** zwei neuen Zusagen in `tests/test_backtest_vorlauf.py`: dass das Basisjahr in der Tabelle steht und nicht im Abstand — und **aus einem anderen Grund als 2020/21** —, und dass es sehr wohl in die Richtung zählt (sonst wären es sechs Übergänge statt sieben).

**Zweitens: Eingang und Ziel der Nachfrageseite stammen aus derselben Erhebung.** Seit P2.8 kommt `kapazitaet_index` aus Eurostat `avia_paoc`/`CAF_PAS` (Flüge) — die Zielreihe `fluggaeste` aus `avia_paoc`/`PAS_CRD` (Passagiere). Dieselbe Tabelle, und mechanisch verbunden: Passagiere = Flüge × Sitze × Auslastung. Die Doku benennt die *Näherung* sauber, **nicht** die Nähe von Eingang und Ziel. Folge: Der Nachfrage-Backtest misst ab 2022 überwiegend die Sitze-je-Flug-Lücke statt der Modellmechanik, und der Satz «ein Maßstab **außerhalb** seiner selbst» gilt für die Nachfrageseite nur noch eingeschränkt. **Beantwortet am 2026-09-03 — und die Antwort war nicht die erwartete.** Die Sorge ließ sich messen, statt sie zu beteuern: derselbe Lauf **ohne** die Kapazitätsreihe, sonst unverändertes Verfahren. Die Gegenprobe steht seither **im Bericht** und nicht in einer Fußnote, weil ein Vorbehalt, den man erst nachrechnen muss, nicht gelesen wird.

| Seite | Kennzahl | mit Kapazität | ohne |
| --- | --- | ---: | ---: |
| Preis | Abstand gesamt | **9,72** | 16,70 |
| Preis | 2016–2019 | **1,01** | 2,16 |
| Preis | Richtung | 5/7 | 5/7 |
| Nachfrage | Abstand gesamt | 36,36 | **28,65** |
| Nachfrage | 2016–2019 | 24,85 | **27,18** |
| Nachfrage | 2022–2024 | 51,71 | **30,61** |
| Nachfrage | Richtung | **5/7** | 1/7 |

**Ein Widerhall sähe anders aus.** Würde der Eingang die Übereinstimmung nur zurückwerfen, müsste der **Abstand** mit ihm kleiner sein. Auf der Nachfrageseite ist er **größer** (36,36 gegen 28,65) — das Modell folgt treu den *Flügen* und verfehlt damit die *Passagiere*, die stärker gewachsen sind. Die Zirkularität bläht die Übereinstimmung also **nicht** auf.

**Was der Eingang wirklich beiträgt, steht an zwei Stellen, die nicht zirkulär sein können:** an der **Richtung** der Nachfrage (5/7 gegen 1/7 — ohne die Kapazität trifft das Modell die Wendepunkte praktisch nie) und an der **Preisseite**, deren Zielreihe aus einer ganz anderen Quelle stammt (Eurostat `prc_hicp_midx`) und sich mit der Kapazität von 16,70 auf **9,72** verbessert.

**Der Vorbehalt bleibt trotzdem stehen, nur präziser gefasst:** Nicht die Zirkularität ist das Problem, sondern die **Sitze-gegen-Flüge-Lücke**. Eine Kapazitätsreihe, die Sitze zählt, veröffentlicht Eurostat auf dieser Ebene nicht — eine **Datenfrage**, keine Parameterfrage. Gehalten von `TestDieGegenprobeStehtImBericht`: dass die beiden Reihen wirklich aus derselben Tabelle stammen, dass der Bericht die Gegenprobe trägt, und dass sie wirklich rechnet statt denselben Lauf zweimal zu zeigen.

**Nebenbefund:** Die Begründung, 2020/21 nicht zu bewerten («das Modell hat für Reisebeschränkungen keinen Mechanismus»), ist seit P2.8 überholt — der Einbruch *wird* über die Kapazitätsreihe eingespeist. Die Entscheidung bleibt richtig, ihre Begründung gehört neu geschrieben.

Herleitung mit allen Messungen: [`audit_phase2_2026-09-03.md`](audit_phase2_2026-09-03.md), Abschnitte B3 und B4.

**Doku zieht mit:** `docs/backtest_vorlauf.md` (wird bei jedem Aufruf überschrieben), `pyproject.toml` (Extra `backtest`), `CLAUDE.md` (Architektur-Map, Dev-Workflow).


**Befund (neu am 2026-08-29):** Das Modell ist an nichts geeicht. Es gibt keinen Lauf, von dem sich sagen ließe, er habe je etwas Beobachtetes reproduziert — und das ist die Frage, die ein Fachprüfer beim Kunden **zuerst** stellt. Alle bisherigen Nachweise prüfen das Modell gegen sich selbst.

**Was zu tun ist:** Die tatsächlichen Verläufe 2015–2024 als exogenen Rahmen einspeisen — Kerosinpreis, ETS-Preis, Konjunktur, der Einbruch 2020 — und prüfen, ob die Simulation Richtung und Größenordnung der beobachteten europäischen Nachfrage und Preise trifft. Das Ergebnis wird veröffentlicht, **auch wenn es schlecht ausfällt**: Ein dokumentierter Fehlschlag mit benannter Abweichung ist mehr wert als ein ungeprüftes Modell, und er sagt, welche Mechanik als Nächstes dran ist.

**Vorbedingung:** [P2.0](#p20--die-rolle-umdrehen-rahmen-statt-urteil--erledigt-2026-08-30) — vor der Umdrehung gibt es keinen Weg, eine historische Außenwelt einzuspeisen, ohne zugleich den Endzustand vorzugeben. Damit wäre der Backtest zirkulär.

**Fallstrick — Invariante 5:** In Config, Checkpoint und Ausgabe steht kein Datum, und das bleibt so (seit [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31) ist ein Tick in der *Mechanik* ein Monat — an dieser Regel über Daten ändert das nichts). Der Backtest braucht eine **Abbildung** von Jahren auf Ticks, die in der Auswertung lebt, nicht im Modell. Wer stattdessen ein Datum in Config, Checkpoint oder Output einführt, bricht die Invariante für einen einmaligen Zweck.

**Zweiter Fallstrick — die Daten:** Kerosin- und ETS-Preise sind frei verfügbar, die europäische Nachfrage- und Yield-Seite nicht durchgängig. Welche Reihe die Zielgröße ist und woher sie kommt, gehört **vor** die Umsetzung; sonst wird das Kriterium nachträglich an die Daten angepasst, die sich beschaffen ließen.

**Ein Vorschlag dazu liegt seit dem 2026-08-30 vor** ([`vorschlag_backtest_daten_2026-08-30.md`](vorschlag_backtest_daten_2026-08-30.md)), geprüft statt aus dem Gedächtnis zitiert. Drei Punkte daraus gehören entschieden, bevor jemand anfängt:

- **Zielgrößen:** Eurostat `avia_paoc` (Fluggäste) und `prc_hicp_midx`/`CP0733` (Verbraucherpreisindex Flugreisen). Letzterer hat die Basis **2015 = 100** — genau der Fensteranfang.
- **Verglichen wird indexiert, nicht auf Euro-Niveau.** Der absolute Preis des Modells hängt an `base_price` und acht Koeffizienten, von denen seit P2.1 aktenkundig keiner geschätzt ist. Ein Niveauvergleich prüfte eine Genauigkeit, die das Modell nie behauptet hat. Prüfbar sind Richtung, Größenordnung und Wendepunkte.
- **2020 ist die eigentliche Entscheidung.** Der Einbruch war kein Preiseffekt, und das Modell hat für Reisebeschränkungen **keinen Mechanismus**. Ihn über `demand_growth_rate` einzuspeisen wäre wertlos — der Backtest bestätigte dann eine Eingabe. Empfohlen: 2020/21 mitrechnen, **unbewertet daneben stellen** und die Lücke benennen.

Drei Kostenindizes (`airport_fee`, `maintenance_cost_index`, `staff_cost_index`) bekommen bewusst **keine** Reihe — es gibt keine frei zugängliche in passender Auflösung, und ein gebastelter Hilfsindex sähe aus wie eine Datenquelle.

**Fertig wenn:** Ein reproduzierbarer Lauf gegen die historische Reihe existiert, die Abweichung ist je Zielgröße beziffert, und das Ergebnis steht mit Methode und Datenquelle in `docs/` — samt der Aussage, was es *nicht* belegt.

#### Befund: Dem Modell fehlt jeder Nachfragetreiber nach oben (2026-08-31)

**Der Backtest hat geliefert, wozu er gebaut wurde — er sagt, welche Mechanik als Nächstes dran ist.** Gemessen, nicht vermutet:

| | 2015 | 2017 | 2019 | 2024 |
| --- | ---: | ---: | ---: | ---: |
| Buchungsrate | 0,3465 | 0,2914 | 0,2971 | 0,2969 |
| Bevölkerung im Lauf | 1005 | 1068 | **1080** | **1080** |
| Fluggaeste real (Index) | 100 | 114,5 | 126,3 | 128,4 |

Die Buchungsrate fällt **nicht** — sie sinkt einmal zwischen 2015 und 2017 und liegt danach flach. Sie *wächst nur nicht*. Und die einzige Größe, über die die Nachfragemenge überhaupt wachsen könnte, ist `bevoelkerungsentwicklung`.

**Zwei getrennte Ursachen, beide in `configs/properties.json`:**

1. **Die Bevölkerungskurve endet bei Tick 30.** Sie ist eine `step_function` mit vier Stützpunkten (Tick 1, 10, 20, **30**), und `_resolve_step_function` hält danach still den letzten Wert. Der Backtest läuft 120 Ticks — **90 davon mit eingefrorener Bevölkerung**. Es ist die **einzige** Trajektorie im ganzen Modell, und ihr Horizont hängt an nichts: Schon der Standardlauf über 40 Ticks verbringt ein Viertel seiner Länge jenseits des letzten Stützpunkts. Das ist für eine Stufenfunktion korrektes Verhalten und deshalb unsichtbar — nichts sagt, dass die Vorgabe aufgebraucht ist.
2. **Selbst ungekürzt reichte sie nicht.** Von 1000 auf 1080 sind **+8 %** über die ganze Kurve; real stieg der europäische Luftverkehr 2015–2019 um **+26 %**. Der Rest des realen Wachstums kam aus Einkommen und real fallenden Ticketpreisen — dafür hat das Modell auf der Nachfrageseite keinen Kanal. `income_index` existiert, bewegt sich aber nicht mit.

**Warum das erst jetzt auffällt:** Solange nichts außerhalb des Modells als Maßstab danebenlag, war eine flache Nachfrage kein Widerspruch. Genau das ist der Zweck des Backtests, und es ist der erste Fund, den er ohne Zutun geliefert hat.

**Nicht repariert, und das mit Absicht.** Eine Nachfragemechanik, die auf diesen Backtest hin gebaut wird, kann er danach nicht mehr prüfen — er bestätigte dann seine eigene Eingabe. Der Fix gehört in ein eigenes Paket mit eigener Begründung, und der Backtest bleibt der Maßstab davor und danach.

**Gehalten von** `tests/test_nachfragetreiber.py`: Er misst den Ist-Stand — die Horizontlücke in Ticks und den Nachfragezuwachs des Modells — und schlägt an, wenn sich einer der beiden bewegt. Dasselbe Muster wie `test_faktoren_abgeleitet.py`: **Ein roter Lauf ist dort keine Panne, sondern die Nachricht, dass jemand die Nachfrageseite angefasst hat.**

> **Und genau das ist am 2026-09-07 passiert** ([P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31)). Der Wächter ist rot geworden, weil die Festlegung «ein Tick ist ein Monat» beide Ist-Stände oben bewegt hat. **Befund 1 ist damit erledigt** — die Kurve reicht bis Tick 120, kein Tick des Backtests rechnet mehr mit eingefrorener Bevölkerung. **Befund 2 ist schärfer geworden**: Aus +8 % werden +2,7 % über zehn Jahre, weil dieselbe Jahresrate jetzt in Monaten gerechnet wird. Am Backtest fünf von acht Kennzahlen verschlechtern sich, eine verbessert sich geringfügig, zwei bleiben gleich — **keine einzige spricht für die Änderung** — und das ist der Beleg, dass die Reihenfolge oben eingehalten wurde: erst die Mechanik richtig, dann messen.

**Doku zieht mit:** neues Kapitel unter `docs/`, `docs/handbuch/grenzen.md`, `README.md`, `CLAUDE.md` (falls eine neue Datenquelle in die Architektur-Map kommt).

### P2.10 — Ein Rahmenszenario, das die Angebotsseite wirklich benutzt ✅ erledigt 2026-09-03

**Befund:** Was P2.8, P2.8-B und P2.4-D/E gebaut haben, setzt **kein ausgeliefertes Szenario**. Nachgezählt über alle acht Dateien unter `configs/sweeps/` und über `configs/properties.json`:

| Größe | ausgeliefert | von einem Szenario gesetzt? |
| --- | --- | --- |
| `kapazitaet_index` | 1,0, **keine Regel** | **nein, in keiner Datei** |
| `strategie` | `auslastung` | **nein** |
| `erneuerungsrate` | 0,0 | **nein** |
| `altersmittel_jahre` | 50,8, konstant | **nein** |
| `income_index` | 1,0 + 2 Regeln | ja, alle vier Rahmen |

**Die Angebotsseite lebt damit ausschließlich im Backtest.** Für die vier ausgelieferten Weltbilder ist die Kapazität konstant — obwohl ihre Kohärenzbegründungen Nachfrageentwicklungen behaupten, die ohne Angebotsentwicklung nicht darstellbar sind. Das ist wörtlich der Befund von [P2.8](#p28--die-nachfrage-kann-nicht-wachsen--erledigt-2026-09-03-weg-a-2026-08-31), nur auf die eigenen Szenarien angewandt: Ein Rahmen, der Wachstum erzählt und die Kapazität festhält, erzählt eine Welt, die sein eigenes Modell für unmöglich hält.

**Was zu tun ist:** Mindestens ein Rahmenszenario bekommt einen begründeten Kapazitätspfad — und seine `kohaerenz` sagt, warum Angebot und Nachfrage in dieser Welt zusammengehören. Die Wahl der Strategie (`auslastung` oder `marge`) gehört ausdrücklich dazu; sie ist seit P2.8-B eine Aussage über die Welt und keine technische Einstellung.

**Vorbedingung:** [P2.8-B](#nachtrag-am-selben-tag-eine-methodik-ist-ein-bias-p28-b) muss zuerst wieder geschlossen sein. Solange die Kapazität unter `marge` nichts tut und die Rationierung die Abgewiesenen sättigt, würde ein Szenario mit Kapazitätspfad eine Wirkung behaupten, die es nicht gibt.

**Fallstrick:** Nicht auf den Backtest hin wählen. Welcher Kapazitätspfad zu «Business as Usual» gehört, entscheidet die Fachlage — dieselbe Regel wie beim Einkommenskanal in P2.8.

#### Erledigt am 2026-09-03 — und es sind alle vier geworden, nicht einer

**Warum alle vier:** Ein Rahmen, der die Kapazität offenlässt, rechnet nicht «ohne Annahme», sondern mit einer **unausgesprochenen** — nämlich unveränderter. Drei Welten mit stiller Konstante neben einer mit begründetem Pfad wären genau die Ungleichbehandlung, die ein Vergleich unlesbar macht.

**Ein Szenario kann seit P2.10 auch sagen, wie der Anbieter preist.** P2.8-B nannte die Strategie «eine Frage an das Szenario, nicht an das Modell» — nur konnte ein Szenario sie nicht stellen: Sie lebt in `market_rules[].effect`, und ein Sweep überschreibt nur Systemgrößen. Wer ein Weltbild mit gehaltener Marge ausliefern wollte, musste die ausgelieferte Konfiguration ändern — also **das Modell statt des Experiments**, Regel 7 der Oberfläche eine Ebene tiefer. `SweepConfig.preisstrategie` schließt das; `None` heißt «wie ausgeliefert», ein Tippfehler scheitert über `MarketFeedbackConfig` und nicht über eine zweite Prüfung.

**Die vier Pfade folgen je aus ihrer eigenen Storyline**, nicht aus dem Backtest — der rechnet diese Dateien ohnehin nicht:

| Rahmen | Kapazität | Strategie | Begründung in einem Satz |
| --- | --- | --- | --- |
| Business as Usual | 1,00 → 1,24 | `auslastung` | Ohne Kostenschock und ohne Beimischungspflicht gibt es keinen Grund, den Ausbau zu stoppen |
| CO₂-Verzögerung | 1,00 → 1,13 → 1,10 | `auslastung` | Erst wird weitergebaut, dann wird es teuer — die Verzögerung *ist* der Ausbau davor |
| Freiwillige Wende | 1,00 → 0,96 | `auslastung` | Knappes SAF verteuert jede zusätzliche Flotteneinheit, der Ausbau stockt |
| Transformationskonflikt | 1,00 → 0,80 | `marge` | Kapazität ist die erste Größe, die unter dreifachem Druck nachgibt |

**Gemessen, dass es ankommt** (letztes Viertel, mit gegen ohne Angebotsseite):

| Rahmen | Rate ohne → mit | Preis ohne → mit |
| --- | --- | --- |
| Business as Usual | 0,3024 → **0,3892** | 144,66 → 128,94 |
| CO₂-Verzögerung | 0,2484 → 0,2717 | 123,62 → 117,57 |
| Freiwillige Wende | 0,2915 → 0,2848 | 103,81 → 104,84 |
| Transformationskonflikt | 0,2585 → **0,0363** | 97,72 → **227,98** |

#### Eine Messung hat eine Wahl widerlegt, und das gehört festgehalten

**Für «Freiwillige Wende» war `marge` die naheliegende Strategie** — wer einen Beimischungsaufschlag trägt, gibt ihn weiter, statt Sitze mit Nachlässen zu füllen. Nachgerechnet fiel die Buchungsrate damit über 50 Ticks von 0,29 auf **0,08** und der Preis stieg von 104 auf **202**: **genau der Nachfrageeinbruch, den die These dieses Szenarios ausdrücklich ausschließt.** Gewählt ist deshalb `auslastung`, und der Grund steht in der Datei.

**Der Befund dahinter ist größer als die Wahl:** Das Modell kennt keinen Kanal, über den eine Wende bei gehaltener Marge *ohne* Nachfrageeinbruch gelänge — dafür bräuchte es fallende SAF-Kosten oder wachsende Einkommen, und beides steht in diesem Rahmen nicht. Das ist eine Grenze des Modells, kein Fehler des Szenarios, und sie ist in seinem `vorbehalt` benannt.

**Die Wächter:** `TestJederRahmenSagtEtwasUeberDasAngebot` (jeder Rahmen setzt einen Pfad, begründet ihn und nennt seine Strategie) und `TestDieAngebotsseiteKommtImLaufAn` — zwei Läufe desselben Rahmens, mit und ohne, gegen die Buchungsrate gehalten. **Gemessen und nicht gelesen**, dasselbe Verfahren wie P1.9-W0.2, das gezeigt hat, dass auf dem Sweep-Pfad ein einziges Feld ankam.

**Fertig wenn** ✅ **(2026-09-03):** Jeder Rahmen setzt `kapazitaet_index` mit Begründung und Quellen und sagt seine Preisstrategie; ein Wächter misst, dass die Größe im Lauf ankommt; und `docs/handbuch/vergleiche.md` nennt den Schnitt.

**Doku zieht mit:** `docs/handbuch/presets.md`, `docs/handbuch/vergleiche.md`, `CLAUDE.md` (Glossar «Rahmenszenario»).

### P2.11 — Zwei Quellen für dieselbe Marktkonstante ✅ erledigt 2026-09-03

**Befund:** `resolve_market_feedback_config` trägt sieben Literal-Rückfälle — `0.37`, `0.08`, `0.08`, `0.85`, `0.6`, `0.33` und seit P2.8-B `"auslastung"` — neben denselben Vorgabewerten in `MarketFeedbackConfig`. Zwei Quellen für denselben Wert, und sie laufen bereits auseinander: Der Code-Rückfall sagt `0.33`, `configs/properties.json` liefert `0.25`.

**Fundstelle:** [`src/market/market_feedback.py`](../src/market/market_feedback.py) (`resolve_market_feedback_config`), Gegenstück in [`src/models/property_models.py`](../src/models/property_models.py) (`MarketFeedbackConfig`).

**Das ist dieselbe Klasse, die zweimal schon abgeräumt wurde:** P1.9-W5.1 hat die Literal-Rückfälle aus den Feld-Renderern des Dashboards entfernt («Ein Feld ohne Wert wird leer gerendert, nicht mit einer erfundenen Zahl»), P2.1 dieselben aus `booking_probability`. Hier stehen sie weiter, und P2.8-B hat `strategie` in genau dieses Muster eingefügt, statt es aufzulösen.

**Und es löst einen dauerhaft roten Test mit auf:** `test_market_feedback.py::TestM413ConfigurablePrice::test_market_rules_resolve_marginal_cost_fraction` erwartet `0.33` und bekommt `0.25`. Der Test ist seit dem 2026-08-25 als «veraltete Erwartung» geführt — er ist in Wahrheit die Meldung, dass es zwei Quellen gibt. Zu entscheiden bleibt trotzdem, welcher Grenzkostenanteil fachlich stimmt; das ist eine eigene Frage und gehört nicht in denselben Commit wie die Auflösung.

**Erledigt am 2026-09-03.** `_FELDER` sagt, welche Felder eine Regel setzen darf und wie ihr Wert zu lesen ist; gesetzt wird nur, was die Regel **wirklich nennt**, alles andere füllt Pydantic aus `MarketFeedbackConfig`. **Entschieden ist 0,25** — die ausgelieferte Config gewinnt, sie war ohnehin der wirksame Wert, und jeder Lauf rechnet seit jeher damit. Keine Verhaltensänderung, kein Schnitt in `vergleiche.md`.

**Zwei Zusagen statt einer:** Der alte Test sagt jetzt 0,25 samt Begründung, warum er zwei Wochen rot stand. Dazu kommt `test_was_die_regel_nicht_nennt_kommt_aus_dem_modell` — eine Regel, die **nur** ihren Typ nennt, muss exakt die Vorgaben des Modells ergeben. Ohne diese Zusage könnte jemand die Literale wieder einsetzen, ohne dass etwas rot wird; sie stimmen ja heute größtenteils mit dem Modell überein, und genau daran ist `marginal_cost_fraction` auseinandergelaufen.

**Der dritte `--deselect` in der CI ist damit weg** — von drei auf zwei; die beiden verbliebenen sind die Ollama-Hänger und fallen mit [P4.2](#p42--suite-aufräumen-und-verlässlich-machen--erledigt-2026-09-11).

**Fertig wenn** ✅: Jeder Vorgabewert steht genau einmal, nämlich im Modell; der Test ist grün, und ein zweiter hält den Rückfall offen.

**Doku zieht mit:** `docs/handbuch/ref-config.md` (falls sich ein ausgelieferter Wert dabei ändert), `CLAUDE.md` (Dev-Workflow — die Liste der drei bekannten Ausnahmen wird um eine kürzer).

### P2.12 — Einkommen wirkte nur als Schwelle ✅ erledigt 2026-09-03

**Befund (B5 des Audits):** `income_factor` stand **ausschließlich** in der Erschwinglichkeitsschranke von `booking_probability` und **nicht im Nutzenterm**. Die Folge ist schwer zu übersehen, sobald man sie ausspricht: **Wer sich das Ticket leisten konnte, für den war Einkommen danach exakt folgenlos.** Ein Doppelverdiener und jemand knapp über der Grenze verspürten denselben Verzicht.

Die gemessene «Einkommenselastizität» von **+0,69** war damit kein Verhaltensparameter, sondern die Dichte der Zahlungsbereitschaft am aktuellen Preis — und sie fiel mit steigendem Einkommen. [P2.8](#p28--die-nachfrage-kann-nicht-wachsen--erledigt-2026-09-03-weg-a-2026-08-31) hatte den Kanal als «korrekt geformt» geführt und mit der Einkommenselastizität bei Brons et al. verglichen; das war ein Kategorienunterschied.

**Umgesetzt: der Preis wird an dem gemessen, was jemand hat.** `normalized_price / income_factor` statt `normalized_price` — dieselbe Ausgabe ist ein anderer Verzicht, je nachdem wovon sie abgeht. Das ist die **Budgetanteils-Form** und in der Nachfragetheorie der Regelfall.

**Und sie kostet keinen neuen Koeffizienten.** Das ist das stärkste Argument für diese Form gegenüber einem eigenen Einkommensterm: Einkommen wirkt über den Preiskanal, den es ohnehin gibt, statt über eine zweite gesetzte Zahl. Das Modell bekommt eine richtigere Mechanik, **ohne** dass die Liste der ungeeichten Werte länger wird.

**Gemessen** (5000 Personen, 140 EUR):

| | vorher | nachher |
| --- | ---: | ---: |
| Einkommenselastizität (+5 %) | +0,75 | **+1,02** |
| Einkommenselastizität (+40 %) | +0,48 | +0,71 |
| Preiselastizität 130 → 145 EUR | −1,30 | −1,24 |
| Preiselastizität 200 → 250 EUR | −2,80 | −2,63 |

**Über 1 am Rand, und zwar aus der Form statt aus einer Zahl.** Die Fachlage führt Luftverkehr als Luxusgut mit Einkommenselastizität über 1; das folgt hier aus der Budgetanteils-Form, nicht aus einem gesetzten Wert. Nebenbei rückt die Preiselastizität etwas näher an das Metaanalyse-Mittel von −1,146 — nicht angestrebt und deshalb erwähnenswert.

**Der Standard bewegt sich, anders als bei B2.** `ln(1) = 0` gab es hier nicht: `income_factor` streut auch bei `income_index = 1,0` über die Bevölkerung. Ein Standardlauf über 40 Ticks liefert **0,264167 / 120,13** statt 0,258704 / 118,85 — dieselbe Faktorlage, aber andere Zahlen. Das ist ein Schnitt in `docs/handbuch/vergleiche.md`.

**Der Backtest, mit unverändertem Verfahren:**

| | vor B5 | nach B5 |
| --- | ---: | ---: |
| **Preis** gesamt | 11,96 | **9,72** |
| Preis 2016–2019 | 3,23 | **1,01** |
| Preis 2022–2024 | 23,61 | **21,33** |
| Preis, Richtung | 4/7 | **5/7** |
| **Nachfrage** gesamt | 34,14 | 36,36 |
| Nachfrage 2016–2019 | 22,47 | 24,85 |
| Nachfrage 2022–2024 | 49,70 | 51,71 |
| Nachfrage, Richtung | **6/7** | 5/7 |

**Die Preisseite gewinnt deutlich — 1,01 Indexpunkte vor der Pandemie ist der beste Wert, den dieses Projekt je gemessen hat.** Die Nachfrageseite verliert leicht, und die Richtungstreffer tauschen die Seiten.

**Behalten wird es trotzdem, und der Grund ist der Mechanismus und nicht die Punktzahl** — dieselbe Entscheidung wie beim Altersprofil in [P2.4](#p24--das-alter-prägt-die-person--erledigt-2026-08-31-erste-fassung-korrigiert), das die Nachfrageseite ebenfalls verschlechtert hat. «Einkommen hat für jeden, der sich das Ticket leisten kann, exakt keine Wirkung» ist keine Modellierungsentscheidung, die jemand verteidigen würde; sie war ein Versehen. Ein Modell zurückzudrehen, weil es nach einer Korrektur auf *einer* Kennzahl schlechter abschneidet, ist die Anpassung an den Backtest, gegen die dieses Projekt anschreibt.

**Was ausdrücklich nicht mitskaliert:** der Substitutionsterm. Er sagt, wie attraktiv die Bahn **gegenüber** dem Flug ist — das hängt am Fahrpreis- und Zeitverhältnis, nicht am Budgetanteil. Ihn ebenfalls zu deflationieren hieße, das Einkommen zweimal durch denselben Nutzenterm zu schicken.

**Der Wächter:** `TestEinkommenWirktNichtNurAlsSchwelle` in `tests/test_buchung_zieht.py`, vier Zusagen. Die tragende ist die mit der **Kontrolle**: Zwei Personen, die sich das Ticket **beide** leisten können, entscheiden verschieden — ohne diese Bedingung misst der Test wieder nur die Erschwinglichkeit, also genau den Mechanismus, der schon vorher da war. Nachgestellt: Auf dem alten Stand fallen zwei der vier um.

**Fertig wenn** ✅ **(2026-09-03):** Einkommen wirkt auf jemanden, der sich das Ticket bereits leisten kann; die Elastizität liegt am Rand über 1 und folgt aus der Form statt aus einer gesetzten Zahl; der Backtest ist davor und danach mit unverändertem Verfahren gerechnet; und der Schnitt steht im Handbuch.

**Doku zieht mit:** `CLAUDE.md` (Glossar «Logit-Modell»), `docs/handbuch/kaufentscheidung.md`, `docs/handbuch/vergleiche.md`.

### P2.13 — F6 kippte in jedem Tick ✅ erledigt 2026-09-07 (neu 2026-09-07)

> **Der Anlass war eine Frage**, nicht ein Wächter: «Ergeben die Simulationen unter der Monatslesart noch Sinn?» Beim Nachmessen kam heraus, dass ein Faktor sich im Tick-Takt umentschied — und dass der Endzustand eines Laufs an der **Parität** seiner Tickzahl hing.

**Befund, gemessen an einem deterministischen Lauf über 120 Ticks:** 111 Faktorwechsel, davon **105 allein F6**, ab Tick 16 in jedem einzelnen Tick, im Takt F6.1 → F6.2 → F6.1. Der gesellschaftliche Wertewandel kippte monatlich.

**Der Schaden ist nicht das Flattern, sondern sein Ende.** Ein Lauf über 40 Ticks endete mit **F6.1**, einer über 41 mit **F6.2** — bei sonst identischer Konfiguration, verifiziert an zwei Läufen. Und genau diesen Endzustand lesen das Szenario-Narrativ und die CIB-Bewertung: Das Tripleset eines Laufs hing damit daran, ob seine Länge gerade oder ungerade war.

**Ursache: eine fehlende Zeile in `apply_factor_rules`.** Die Schleife läuft die Regeln nach Priorität ab und merkt sich in `updated_factors`, welcher Faktor schon entschieden ist. Diese Marke wurde nur gesetzt, wenn eine Regel den Zustand **änderte**. Traf die höchstpriorisierte Regel schon zu — ihr Ziel war bereits gesetzt —, sprang die Schleife weiter und überließ den Faktor der nächsten Regel, auch einer, die das Gegenteil verlangt:

| Regel | Bedingung | Ziel | Priorität |
| --- | --- | --- | ---: |
| `f6_flight_shaming_high_tax` | `carbon_tax_level` über 80 | F6.2 | **10** |
| `f6_tech_breakthrough_acceptance` | F3 ist F3.2 | F6.1 | **3** |

Ab Tick 16 treffen **beide dauerhaft** zu. Die Priorität hätte das entscheiden sollen; sie tat es nicht, weil die höhere Regel nach ihrem eigenen Erfolg aus dem Weg ging. **Die Priorität entscheidet also erst seit diesem Paket wirklich.**

**Fundstelle:** [`src/market/factor_dynamics.py`](../src/market/factor_dynamics.py) (`apply_factor_rules`).

**Warum es die Suite nicht gesehen hat:** Sie hat es nie gemessen. Nach dem Fix liefen alle 1669 Zusagen **unverändert** grün — kein einziger Test hielt das Verhalten fest, in keiner Richtung. `test_faktoren_abgeleitet.py` prüft, dass Faktoren ihre Startlage im ersten Tick vergessen, und ein Tick genügt dafür; über den ersten hinaus hat niemand geschaut.

**Der Wächter misst die Zusage, nicht die Regel:** [`tests/test_faktoren_flattern_nicht.py`](../tests/test_faktoren_flattern_nicht.py), sechs Zusagen. Der tragende Teil sucht **`A → B → A` in drei aufeinanderfolgenden Ticks** — die präzise Form des Befunds und nicht «hat sich oft geändert»: Ein Faktor *darf* zurückwechseln, wenn eine exogene Größe es hergibt (ein Rahmen nimmt die CO₂-Abgabe durchaus zurück). Was keine exogene Größe hergibt, ist ein Wechsel im Tick-Takt. Daneben zwei Zusagen am Mechanismus und eine Gegenprobe gegen **Stillstand**: Ein `updated_factors.add()` an der falschen Stelle machte aus dem Flattern einen eingefrorenen Faktor — auch falsch, und von der Zusage oben nicht zu unterscheiden.

**Der erste Anlauf des Wächters war selbst hohl**, und das gehört dazu: Die beiden Mechanismus-Zusagen liefen bei Tick 1, wo die ausgelieferte CO₂-Abgabe auf 50 steht — keine der gebauten Regeln traf zu, und «die niedrigere überschreibt nicht» war grün, weil überhaupt nichts geschah. Aufgefallen ist es nur, weil die Gegenprobe daneben fehlschlug, die *setzen* muss. Der Wächter prüft die Voraussetzung jetzt selbst. **Mutationsprobe:** Marke wieder entfernt, drei der sechs Zusagen rot.

**Was sich an den Zahlen ändert — und das ist ein größerer Schnitt als P3.8:**

| | vorher | nachher |
| --- | ---: | ---: |
| Standardlauf 40 Ticks, Buchungsrate | 0,267857 | **0,256944** |
| Standardlauf 40 Ticks, Preis | 116,59 | **119,95** |
| Faktorwechsel über 120 Ticks | 111 | **6** |
| «CO₂-Verzögerung», Endlage F6 | F6.1 | **F6.2** |
| «Freiwillige Wende», Endlage F6 | F6.1 | **F6.2** |
| «Freiwillige Wende», Preis | 106,25 | **107,15** |

«Business as Usual» und «Transformationskonflikt» bleiben unverändert: Bei BAU steht die Abgabe konstant auf 50 und damit unter der Schwelle von 60, dort gewinnt F6.1 zu Recht; beim Transformationskonflikt stand F6 schon auf F6.2.

**Der Backtest ist unverändert** (9,82 / 36,44), und der Grund ist erklärbar statt beruhigend: Seine historischen EUA-Preise liegen 2015–2019 zwischen 5 und 25 Euro, die Schwelle von 80 wird nie erreicht, ein SAF-Mandat gibt es dort nicht. Der Widerspruch tritt in diesem Fenster also gar nicht auf.

**Was ausdrücklich offen bleibt: die Modellfrage dahinter.** Die beiden Regeln sind ein echter fachlicher Widerspruch — ein Technologiedurchbruch *sollte* Flugscham plausibel dämpfen, und bei 200 EUR je Tonne sagt die Config trotzdem «Scham gewinnt». Die Priorität entscheidet das jetzt zuverlässig, aber sie **begründet** es nicht. Ob 10 gegen 3 die richtige Rangfolge ist, ist eine Frage an das Modell und nicht an die Engine; sie gehört zur Klasse der unbegründeten Matrixwerte (siehe die [Leitentscheidung zur Szenarienschicht](#leitentscheidung-die-szenarienschicht-2026-08-29)) und ist hier bewusst nicht mitentschieden.

**Fertig, gemessen:** `tests/test_faktoren_flattern_nicht.py` — sechs Zusagen, drei davon rot bei zurückgenommenem Fix. Suite 1669 grün. Vier Rahmen und Backtest neu gerechnet. **Doku ist mitgezogen:** `CLAUDE.md` (Invariante 6 um den Satz, wer bei Gleichstand entscheidet; Glossar «Faktoren F1–F7»), `docs/handbuch/faktoren.md`, `docs/handbuch/vergleiche.md` (dreizehnter Schnitt), `docs/audit_findings.md` (Befund entfernt, nicht abgehakt).

### P2.14 — Einmalige Verschiebungen laufen an den Anschlag 🟡 offen (neu 2026-09-11, aus P5.1)

> **Aus der Nachmessung von [P5.1](#p51--toter-code-und-irreführende-namen--erledigt-2026-09-11).** Die Frage war, ob das Population-Shift-Feature überhaupt lebt. Es lebt, und dabei fiel auf, wohin es läuft.

**Befund:** Alle neun `shift_rules` tragen `once=True` — keine addiert sich Monat für Monat. Aber mehrere wirken auf **dasselbe** Merkmal, und ihre Deltas summieren sich: auf die Preisempfindlichkeit bis zu **+0,29** (F1.2 +0,05, F4.2 +0,07, F7.2 +0,05, CO₂-Abgabe über 50 EUR +0,12). `apply_factor_shifts` klemmt mit `np.clip` bei 1,0, ohne es zu melden.

| Standardlauf, Seed 42 | Personen am oberen Anschlag der Preisempfindlichkeit |
| --- | ---: |
| nach 12 Ticks | 13 von 1000 |
| nach 40 Ticks | **274 von 1008** |
| nach 120 Ticks | **279 von 1027** |

**Ein erster Verdacht war falsch und gehört dazu:** Beim ersten Hinsehen standen die Merkmale nach 40 und nach 120 Ticks gleich, und das sah nach Regeln aus, die sich jeden Monat erneut addieren. Nachgeprüft trägt jede Regel `once=True`; gleich sind die Werte, weil alle einmaligen Verschiebungen früh gefeuert haben.

**Was offen ist — eine Modellfrage, kein Fix:** ob sich die Aufschläge summieren sollen, ob 1,0 die richtige Grenze ist oder eine Verschiebung relativ zum Abstand vom Rand wirken soll. **Zuerst zu messen:** ob der Anschlag die Buchungsrate überhaupt messbar bewegt — ohne diese Zahl ist jede Antwort Geschmack.

**Fundstelle:** [`src/population/population_sampler.py`](../src/population/population_sampler.py) (`apply_factor_shifts`), `configs/properties.json` (`shift_rules`).

**Fertig wenn:** Die Wirkung auf die Buchungsrate ist gemessen, und die Summe der Deltas ist entweder begrenzt oder in `configs/properties.json` begründet — und ein Wächter hält, wie viele Personen am Anschlag hängen dürfen.

**Doku zieht mit:** `CLAUDE.md` (Glossar, falls sich die Wirkung einer `shift_rule` ändert), `docs/handbuch/vergleiche.md` (falls sich Zahlen verschieben).

---

## Phase 3 — Engine-Härtung ✅ vollständig abgeschlossen am 2026-09-07

Fallen, die heute niemanden stören und beim nächsten Feature zuschlagen. Jedes Paket ist klein; zusammen entscheiden sie, ob die Engine trägt.

**Stand 2026-09-07: siebzehn Pakete erledigt, keines mehr offen — die Phase ist vollständig.** Alle drei aus der Arbeit entstandenen Pakete (P3.10, P3.11, P3.12) sind mit erledigt, und die zuletzt zurückgestellte Tickdauer (P3.8) ist am 2026-09-07 **entschieden und umgesetzt**: ein Tick ist ein Monat. **Der Grund für das Zurückstellen hat der Umsetzung nicht standgehalten** — die Sorge war, eine Umparametrisierung nehme dem Backtest seinen Prüfwert; tatsächlich blieb die Jahresrate jeder Größe unverändert (geändert wurde die Einheit), und am Backtest fünf von acht Kennzahlen verschlechtern sich, eine verbessert sich geringfügig, zwei bleiben gleich — **keine einzige spricht für die Änderung**. Genau das ist der Beleg, dass nicht auf ihn hin eingestellt wurde. Dabei kam ein **vierter** Widerspruch heraus, den der Wächter nicht gefunden hatte: `demand_growth_rate` trug «je Tick» in der Einheit und «jährlich» in der Beschreibung — aufgezinst 42,58 % im Jahr. **Am selben Tag ist die Phase vollständig geprüft worden** ([Audit](#audit-der-phase-3-2026-09-05--fünf-pakete-der-schwere-befund-ist-vorbestehend), Vollfassung in [`audit_phase3_2026-09-05.md`](audit_phase3_2026-09-05.md)): elf von zwölf Paketen halten nachgemessen, alle fünfzehn tragenden Wächter gehen rot, wenn man ihre Zusage bricht, **kein schwerer Befund, und keiner berührt die Zahlen eines Laufs.** Vier Ränder hielten nicht (P3.13 bis P3.16) und sind behoben, dazu der vorbestehende schwere Befund am Browser-Wächter (P3.17) und **alle fünf kleinen Befunde** (C1 bis C4 plus die erfundene Nutzermeldung). **Offen blieb aus diesem Audit nur die Klasse hinter P3.15** — [P4.4](#p44--ein-typprüfer-für-die-grenzen--erledigt-2026-09-11-neu-2026-09-05-aus-p315), seit dem 2026-09-11 erledigt: `mypy` prüft die Grenzen in der CI. Die Einschränkung gehört dazu: **das Audit ist nicht unabhängig** — dieselbe Sitzung hat gebaut und geprüft.

| Paket | Stand |
| --- | --- |
| [P3.7](#p37--titel-und-legende-teilen-sich-einen-rand--erledigt-2026-09-05-drei-versuche-verworfen) Legende unter der Zeichenfläche | ✅ erledigt |
| [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31) Tickdauer | ✅ erledigt 2026-09-07 — ein Tick ist ein Monat |
| [P3.1](#p31--system-properties-täuschen-keine-laufzeitwerte-mehr-vor--erledigt-2026-09-05) Laufzeitwerte in `when` | ✅ erledigt |
| [P3.2](#p32--checkpoint-version-wirklich-prüfen--erledigt-2026-09-05) Checkpoint-Version | ✅ erledigt |
| [P3.3](#p33--fehlermeldungen-die-auch-greifen--erledigt-2026-09-05) Fehlermeldungen | ✅ erledigt |
| [P3.4](#p34--llm-konfiguration-zentralisieren--erledigt-2026-09-05) LLM-Konfiguration | ✅ erledigt |
| [P3.5](#p35--stille-klemmungen-und-debug-ausgaben--erledigt-2026-09-05) Klemmungen und `print()` | ✅ erledigt |
| [P3.6](#p36--stabiler-vertrag-für-den-run-launcher--erledigt-2026-09-05) Launcher-Vertrag | ✅ erledigt |
| [P3.9](#p39--ein-klick-in-der-schrittfolge-kostet-zwei-sekunden--erledigt-2026-09-05-ursache-zweimal-korrigiert) Klickkosten | ✅ erledigt (Ursache zweimal korrigiert) |
| [P3.12](#p312--der-modell-bereich-lag-dauernd-im-dom--erledigt-2026-09-05) Modell-Bereich dauernd im DOM | ✅ erledigt (aus P3.9) |
| [P3.10](#p310--46-zeichenketten-die-die-konsole-nicht-schreiben-kann--erledigt-2026-09-05) Zeichensatz der Konsole | ✅ erledigt (aus P3.3) |
| [P3.11](#p311--die-lauf-argumente-sind-ein-simplenamespace--erledigt-2026-09-05) Lauf-Argumente ohne Form | ✅ erledigt (aus P3.6) |
| [P3.13](#p313--der-abgeschaffte-rückfall-lebt-eine-ebene-höher--erledigt-2026-09-05) Rückfall auf `llama3.2` | ✅ erledigt (aus dem Audit) |
| [P3.14](#p314--der-fehlerweg-braucht-keinen-puffer--erledigt-2026-09-05) Fehlerweg braucht `.buffer` | ✅ erledigt (aus dem Audit) |
| [P3.15](#p315--eine-signatur-die-ihrem-rumpf-widerspricht--erledigt-2026-09-05) Annotation gegen Rumpf | ✅ erledigt (aus dem Audit) |
| [P3.16](#p316--das-500-ms-kriterium-und-sein-deckel--erledigt-2026-09-05) 500 ms gegen einen Deckel von 900 | ✅ erledigt (aus dem Audit) |
| [P3.17](#p317--der-browser-wächter-ist-rot-und-niemand-läuft-ihn--erledigt-2026-09-06) Browser-Wächter rot, C5 zum zweiten Mal | ✅ erledigt 2026-09-06 (aus dem Audit, **vorbestehend**) |

**Die Lehre des Durchgangs, weil sie sich dreimal wiederholt hat: eine Prüfung, die nur so aussieht, ist teurer als keine.** P3.2 schrieb eine Versionsnummer, die niemand las. P3.3 hatte ein `try: pass`, dessen `except` nie feuern konnte. P3.4 prüfte ein `config.llm`, das kein Laufpfad benutzte. In allen drei Fällen war die *Absicht* im Code sichtbar und die *Wirkung* nicht — und niemandem fiel es auf, weil nichts rot war.

**Zweite Lehre, gegen die eigenen Wächter gerichtet:** Drei der neuen Zusagen sind beim ersten Anlauf an der **eigenen Prosa** gescheitert. Sie prüften Quelltext als Zeichenkette (`"except Exception" not in quelle`), und die Kommentare, die den alten Zustand erklären, zitieren ihn — `try: pass`, `except Exception`, `get_llm()`. Geprüft wird jetzt der Syntaxbaum. *Ein Wächter, den eine Erklärung über ihn selbst umlenken kann, ist keiner.*

**Dritte, aus P3.9:** Auch eine Messung kann das Falsche messen. `wait_for_function` pollt über `requestAnimationFrame`, das in einem unsichtbaren Tab gar nicht feuert — dieselbe Falle wie in P1.9-W5.3, und sie meldete 2,0 s, wo 1,1 s standen. Und die *vorherige* Messung dieses Pakets hatte den Statusherzschlag mitgezählt, den P1.6 eingeführt hatte.

**Vierte, aus dem Audit der Phase am selben Tag: ein Selbstaudit findet die Ränder, nicht die Mitte** — und es findet sie nur, wenn es ein Verfahren hat, das nicht von der eigenen Absicht abhängt. Die neun Befunde liegen ausnahmslos am Rand einer Zusage: eine Notlösung eine Ebene über ihrer Abschaffung, ein Ausweichpfad mit einer unausgesprochenen Voraussetzung, eine Signatur neben einem richtigen Rumpf. Was **nicht** gefunden wurde, ist eine falsche Mitte — und das ist genau die Aussage, für die ein Selbstaudit am wenigsten taugt. Was getragen hat, war die Mutationsprobe: fünfzehn Zusagen absichtlich gebrochen, fünfzehnmal rot. Was nicht getragen hat, war der erste Anlauf von sechs Messungen — der Prüfling war falsch, nicht der Prüfgegenstand, und in einem Fall (P3.6) hätte das eine ungeprüfte Zusage als geprüft gezählt, weil ein nicht gefundenes Suchmuster wie ein grünes Ergebnis aussieht. **Ein Prüfling, der nichts findet, muss sagen können, ob er gesucht hat.**

### P3.7 — Titel und Legende teilen sich einen Rand ✅ erledigt 2026-09-05 (drei Versuche verworfen)

**Befund:** In den Plotly-Diagrammen des Dashboards überlappen sich Titel und Legende. Beide leben im oberen Rand: Die Legende steht waagerecht bei `y=1.02` über der Zeichenfläche, der Titel im selben `margin.t=56`. Gemessen am laufenden System: Titel y 681–702, erster Legendeneintrag y 696–715 — **6 px Überschneidung**. Bei fünf Legendeneinträgen («Buchungsrate nach Profil-Segment») wird die Legende **105 px** hoch und deckt den Titel weitgehend zu.

**Fundstelle:** [`dashboard/web/theme.py`](../dashboard/web/theme.py), `_build_template` — `title` und `legend` im `go.Layout`.

**Gefunden beim Einzeichnen des Ensemble-Bandes** ([P2.6](#p26--ensemble-läufe-je-rahmenszenario--erledigt-2026-08-31)). Dessen erste Fassung verschlimmerte es (längerer Titel plus zwei weitere Legendeneinträge → zweizeilige Legende, 58 px), das ist zurückgenommen. Der **vorbestehende** Rest ist dieser Befund.

**Zwei Versuche sind gemessen und verworfen worden**, und das ist die eigentliche Auskunft dieses Pakets — wer es angeht, fängt nicht bei ihnen an:

1. **Größeres `margin.t` plus `title.y=1`** (56 → 92 px): behebt es für drei der vier Aussagen. Die vierte hat eine Legende, die auf 105 px umbricht, und läuft weiterhin in den Titel. **Ein fester Rand kann eine Legende variabler Höhe nicht auffangen** — das ist keine Frage der Zahl.
2. **`title.automargin=True`**, der dafür vorgesehene Plotly-Mechanismus: macht es **schlimmer**. Danach überlappten *beide* Diagramme der Aussage 3 statt einem. Der Titel zieht den Rand auf, die Legende sitzt aber relativ zur Zeichenfläche und wandert mit nach unten.

**Umgesetzt am 2026-09-05, und der Befund war größer als gemeldet:** Gemessen am laufenden System überschnitten sich Titel und Legende in **allen** vier Aussagen und **beiden** Modi — **12 Überschneidungen** über sechs Diagramme, 11 px im Regelfall und 21 px bei «Buchungsrate nach Profil-Segment». Der Plan nannte 6 px an einem Beispiel; die Zahl war zu klein, weil sie an einem Diagramm erhoben war.

**Die Legende steht jetzt unter der Zeichenfläche** (`yanchor="top"`, `y=-0.30`), der Titel hat den oberen Rand für sich. Zwei Zahlen tragen das, beide in [`dashboard/web/theme.py`](../dashboard/web/theme.py) als benannte Konstanten mit ihrer Herleitung: `LEGENDE_RAND` (48 px) und `LEGENDE_Y` (−0,30).

**Ein dritter Versuch ist dazugekommen und ebenfalls verworfen** — er sah nach der saubersten Lösung aus und ist es nicht:

3. **Legende am Container festnageln** (`yref="container"`, `y=0`, `yanchor="bottom"`): löst die Überlappung deterministisch, weil die Unterkante fest steht. Nimmt die Legende damit aber aus Plotlys Automargin heraus — der untere Rand muss dann den schlechtesten Fall abdecken. Gemessen 148 px, und das kostete im Regelfall **100 px Zeichenfläche** für eine 29 px hohe Legende (216 statt 316 px Zeichenhöhe bei 420 px Figurenhöhe). Bei 88 px lief die hohe Legende 21 px in die Achsenbeschriftung: **Plotly zieht den Rand für eine container-bezogene Legende nicht auf.** Mit Papierbezug tut es das.

**Der Fallstrick ist eingetreten, und der Wächter hat ihn gefunden**, nicht ein Blick aufs Bild: Bei `y=-0.22` war die Titel-Überlappung weg und die hohe Legende lag **5 px im Achsentitel** — eine Überlappung gegen die nächste getauscht. Bei −0,30 bleiben 8 bis 25 px Luft zum Achsentitel und 35 bis 52 px zur Achsenbeschriftung. Deshalb misst der Wächter **drei** Abstände, nicht einen.

**Nebenwirkung, bewusst behalten:** `automargin=True` auf beiden Achsen. Ohne es zieht Plotly den unteren Rand nicht auf, und die Legende landet außerhalb der Figur. Der Preis ist eine Zeichenfläche, die je nach Legendenhöhe unterschiedlich hoch ist — richtig so: Eine Figur mit fünf Reihen braucht mehr Beschriftungsfläche als eine mit zwei.

**Fertig, gemessen:** Kein Diagramm des Dashboards überlappt Titel und Legende — Teil 8 von [`tests/test_web_overflow.py`](../tests/test_web_overflow.py) misst alle vier Aussagen, alle fünf Bereiche, beide Modi und beide Breiten: **16 Zusagen, alle grün**. Dazu `test_the_legend_guard_would_notice_a_relapse`, der die Legende per `Plotly.relayout` an ihren alten Platz zurückschiebt und prüft, dass der Wächter das meldet — ein Wächter, der nie etwas sieht, könnte auch blind sein.

**Doku ist mitgezogen:** `CLAUDE.md` (Regel 4 des Dash-Abschnitts nennt jetzt auch die Layoutseite des Templates).

### P3.8 — Ein Tick ist ein Monat ✅ erledigt 2026-09-07 (neu 2026-08-31)

> **Der Anlass war eine Nutzerfrage**, und sie hat eine Invariante getroffen: «Es kommt doch darauf an, wie viele Ticks man macht — evtl. möchte man Jahre.» Beim Nachmessen kam heraus, dass die Frage schon beantwortet ist. Dreimal. Verschieden. **Am 2026-09-07 ist sie einmal beantwortet: ein Tick ist ein Monat.**

**Befund:** [Invariante 5](../CLAUDE.md) sagt «ein Tick ist ein Tick» — keine Kalendersemantik in Configs, Checkpoints oder Ausgaben. Als **Regel für Datenformate** ist das eingehalten: Nirgends steht ein Datum. Als Aussage über das **Modellverhalten** hält sie nicht. Eine Zeitskala verschwindet nicht dadurch, dass man sie nicht aufschreibt — jeder Mechanismus, der pro Tick etwas verändert, unterstellt eine.

| Mechanismus | plausibel, wenn ein Tick … | gemessen |
| --- | --- | --- |
| `bevoelkerungsentwicklung` | ein **Jahr** ist | +8 % über 29 Ticks = **+0,27 % p.a.** (EU-Realität); als Monate gelesen +3,24 % p.a. — das gibt es nirgends |
| Sättigung | ein **Monat** ist | Eine Reise ist nach ~3 Ticks «vergessen»; als Jahre gelesen wären das 3 Jahre zwischen zwei Familienflügen |
| Backtest (`reihen.tick_je_monat`) | ein **Monat** ist | Ausdrücklich, und er trifft damit den Preispfad auf 1,27 Indexpunkte |

**Faktor 12 auseinander.** Zwei Mechanismen sagen Monat, einer sagt Jahr.

**Warum das keine Formalie ist — gemessen:** Läse man einen Tick als Jahr und ließe die Kohorte mitaltern, fiele die Buchungsrate über einen 40-Tick-Lauf um **47,6 %**, und die Bevölkerung wäre am Ende im Schnitt **83** Jahre alt. Das wäre der größte Einzeleffekt im ganzen Modell — größer als Preis, CO₂-Abgabe und Einkommen zusammen.

**Fundstellen:** [`configs/properties.json`](../configs/properties.json) (`bevoelkerungsentwicklung`, `saturation_decay` je Segment), [`src/backtest/reihen.py`](../src/backtest/reihen.py) (`tick_je_monat`).

**Entschieden am 2026-08-31: erst messen, nicht festlegen.** Der Widerspruch ist dokumentiert und von [`tests/test_tickdauer_ist_uneinheitlich.py`](../tests/test_tickdauer_ist_uneinheitlich.py) festgehalten — sechs Zusagen, die je Mechanismus die implizite Zeitskala prüfen. **Ein rotes Ergebnis ist dort eine gute Nachricht**: Es heißt, jemand hat sie angeglichen, und dann gehört dieses Paket geschlossen.

**Was zu tun ist, wenn die Festlegung ansteht** — drei Wege, jeder mit Folgekosten:

1. **Ein Tick ist ein Monat.** Folgt zwei von drei Mechanismen. Dann ist die Bevölkerungskurve zu korrigieren, und ein Standardlauf über 40 Ticks deckt gut drei Jahre ab — Alterung wäre irrelevant.
2. **Ein Tick ist ein Jahr.** Passt zur Bevölkerungskurve und zum Produktversprechen «strategische Zukunftsplanung»; 40 Ticks sind dann 40 Jahre. Dafür ist die Sättigung neu zu parametrisieren, und der Backtest bräuchte eine andere Abbildung.
3. **Konfigurierbar** («Jahre je Tick» als Systemgröße). Ehrlichste Variante, bricht Invariante 5 ausdrücklich — und **jede** zeitabhängige Größe muss dann daran hängen, sonst ist der Widerspruch nur verschoben.

**Fallstrick:** Wer nur eine der drei Stellen anfasst, verschiebt den Widerspruch, statt ihn aufzulösen. Der Wächter misst deshalb alle drei zusammen.

**Zurückgestellt am 2026-09-05, mit Grund und nicht auf Sicht.** Beim Durchgang durch Phase 3 wurde die Festlegung Haiko vorgelegt — mit den drei Wegen und ihren Folgekosten. Entschieden war zunächst: **noch nicht festlegen.** Der Grund war nicht Aufwand, sondern Reihenfolge. Alle drei Wege verlangen eine Umparametrisierung, die der Backtest anschließend nicht mehr prüfen kann: Wer die Sättigung oder die Bevölkerungskurve auf eine gewählte Tickdauer einstellt, stellt genau die Größen ein, an denen P2.7 das Modell gegen 2015–2024 misst — und ein Modell, das den Vergleich besteht, weil es auf ihn hin eingestellt wurde, ist an nichts geprüft. Dieselbe Begründung, mit der P2.7 keine Eichung ist.

---

**Entschieden am 2026-09-07: Weg 1, ein Tick ist ein Monat.** Die Entscheidung ist Haikos; was hier steht, ist ihre Umsetzung und was dabei herauskam.

**Der Grund, aus dem zurückgestellt wurde, hält der Umsetzung nicht stand** — und das ist der wichtigste Satz dieses Abschnitts. Die Sorge war, eine Umparametrisierung nehme dem Backtest seinen Prüfwert. Sie tut es hier aus zwei Gründen nicht:

1. **Der Anker ist außen, nicht innen.** Geändert wurde die **Einheit**, nicht die Aussage über die Welt. Die Bevölkerungskurve behauptete als Jahre gelesen 0,2657 % p.a.; genau diese Jahresrate trägt sie weiterhin, nur in Monaten gerechnet. `demand_growth_rate` behauptete 3 % p.a.; auch die stehen weiter da. Kein Wert ist gewählt worden, weil er den Vergleich verbessert — ein eigener Wächter hält die Jahresrate gegen die von vorher.
2. **Der Backtest wird schlechter.** Fünf von acht Kennzahlen verschlechtern sich, eine verbessert sich geringfügig, zwei bleiben gleich — **keine einzige spricht für die Änderung**. Wäre hier auf ihn hin eingestellt worden, sähe das anders aus.

| Kennzahl | vorher | nachher |
| --- | ---: | ---: |
| Preis, Abstand gesamt | 9,72 | **9,82** |
| Preis, 2016–2019 | 1,01 | **1,15** |
| Preis, 2022–2024 | 21,33 | **21,37** |
| Preis, Richtung | 5/7 | 5/7 |
| Nachfrage, Abstand gesamt | 36,36 | **36,44** |
| Nachfrage, 2016–2019 | 24,85 | **25,04** |
| Nachfrage, 2022–2024 | 51,71 | 51,64 |
| Nachfrage, Richtung | 5/7 | 5/7 |

**Der Grund für die Verschlechterung ist derselbe Befund wie in P2.7:** Die Bevölkerungskurve wuchs um 8 % über eine Strecke, die als *Jahre* gemeint war. In Monaten sind es +2,7 % über zehn Jahre — dem Modell fehlt der Nachfragetreiber nach oben also **noch deutlicher** als vorher. Der Befund wird schärfer, nicht kleiner.

**Ein vierter Widerspruch kam bei der Umsetzung dazu, und er war der schärfste:** `demand_growth_rate` trug `unit: "fraction_per_tick"` und daneben die Beschreibung «Jaehrliche Wachstumsrate». **Das Feld widersprach sich selbst**, Einheit gegen Beschreibung — und gerechnet wurde die Einheit: `sync_demand_level` zinst den Wert Tick für Tick auf. 0,03 je Monat sind **42,58 % im Jahr**, über die 120 Ticks des Backtests der Faktor **34,7**. Der Wächter aus P3.8 hat ihn nicht gefunden, weil er die drei bekannten Mechanismen aufzählte statt sie zu suchen — genau der Fallstrick, den derselbe Abschnitt oben benennt.

**Was geändert wurde, und was ausdrücklich nicht:**

| Mechanismus | vorher | Lesart | Maßnahme |
| --- | --- | --- | --- |
| Sättigung (`booking_increase` / `saturation_decay`) | 2 bis 12 Ticks zwischen zwei Reisen | Monate ✅ | **unverändert** |
| Backtest (`reihen.tick_je_monat`) | zwölf Ticks je Jahr | Monate ✅ | **unverändert** |
| `fuel_price_change` = 0,005 je Tick | 6,17 % p.a. | Monate ✅ | unverändert, Einheit dokumentiert |
| `bevoelkerungsentwicklung` | +8 % über 29 Ticks | **Jahre** ❌ | Jahresstufen bis Tick 120, Jahresrate erhalten |
| `demand_growth_rate` = 0,03 je Tick | 42,58 % p.a. | **Jahre** ❌ | 0,0025 je Tick = 3,04 % p.a. |
| `erneuerungsrate` = 0,0 | Standard verwies auf das offene P3.8 | — | Begründung ersetzt, 0,0012 benannt |

**Der Horizont der Bevölkerungskurve ist mit erledigt** — die offene Restposition von [P2.8](#p28--die-nachfrage-kann-nicht-wachsen--erledigt-2026-09-03-weg-a-2026-08-31). Sie endete bei Tick 30, der Backtest rechnete **90 von 120** Ticks mit eingefrorener Bevölkerung. Jetzt reicht sie bis Tick 120, also zehn Jahre — und das ist genau das Fenster des Backtests. **Jahresstufen und kein Monatsraster**, weil Bevölkerungsstatistik jährlich erhoben wird; ein feineres Raster täuschte eine Genauigkeit vor, die die Quelle nicht hat. Innerhalb eines Standardlaufs liegen damit drei Stufen — ein gedeckter Horizont ohne jede Bewegung im Lauf wäre die halbe Lösung gewesen, und ein eigener Wächter prüft genau das.

**Der Wächter misst, statt zu lesen.** [`tests/test_ein_tick_ist_ein_monat.py`](../tests/test_ein_tick_ist_ein_monat.py) löst `test_tickdauer_ist_uneinheitlich.py` ab (gelöscht). Der alte hielt den Ist-Stand «die Skalen widersprechen sich noch» und ist rot geworden, als jemand sie anglich — genau wie sein Docstring angekündigt hatte. Der neue hält die Gegenrichtung, und sein tragender Teil sucht sich die Raten über ihre **Einheit** (`*_per_tick`) selbst: Zwölfmal aufgezinst muss jede eine plausible Jahresrate ergeben. Eine Textsuche nach «jährlich» wäre an den Erklärtexten hängen geblieben, die genau diesen Fall schildern — dieselbe Falle, in die die ersten Wächter von [P3.3](#p33--fehlermeldungen-die-auch-greifen--erledigt-2026-09-05) gelaufen sind. **Sechs Mutationen, sechsmal rot**, darunter die, die eine Jahresrate hinter einer anderen Einheit versteckt.

**Zwei Zusagen gehen über den heutigen Zustand hinaus**, weil sie sonst nichts sagen würden: dass die Kurve als *Jahre* gelesen jetzt **unplausibel** ist (sonst wäre der Wächter mit einer Kurve zufrieden, die beides zulässt), und dass ihre Jahresrate **die von vor P3.8** ist (sonst zöge unter dem Deckmantel einer Einheitenkorrektur eine Neuschätzung ein).

**Invariante 5 ist geschärft, nicht ersetzt.** «Ein Tick ist ein Tick» bleibt als Regel über **Daten** wortgleich stehen — in Config, Checkpoint und Ausgabe steht weiterhin kein Datum, und die Kalenderzuordnung lebt weiterhin nur im Backtest. Was danebentritt, ist die Antwort auf eine andere Frage: welche Zeitskala die **Mechanik** unterstellt. Beide gelten zusammen.

**Was ausdrücklich nicht entschieden ist: der Horizont der Rahmenszenarien.** Sie laufen 50 Ticks — als Monate gut vier Jahre — und lassen die CO₂-Abgabe binnen 20 Monaten von 50 auf 200 EUR steigen. Das ist keine Rate, sondern eine Erzählung über die Welt, und ihre Kohärenzbegründungen nennen dafür Quellen. Sie stillschweigend umzuskalieren hieße, vier Szenarien etwas anderes sagen zu lassen, ohne ihre Begründung anzufassen. Eingeplant als [P4.5](#p45--was-ein-rahmenszenario-über-die-zeit-behauptet--erledigt-2026-09-11-neu-2026-09-07).

**Nachtrag vom selben Tag: der erste Anlauf war unvollständig, und zwar an genau der Stelle, vor der dieses Paket warnt.** Auf die Frage, ob die Monatsrechnung *systemübergreifend* stimmt, kam die Messung: **Drei der vier ausgelieferten Rahmenszenarien überschrieben `demand_growth_rate` weiterhin mit ihrer Jahresrate** — `business_as_usual` 0,03 (**42,58 % p.a.**), `freiwillige_wende` 0,02 (26,82 %), `transformation_conflict` 0,01 (12,68 %). `co2_delayed` trug keine eigene Vorgabe und erbte still den korrigierten Wert.

**Der Wächter konnte es nicht finden, weil seine Ausnahme zu weit gefasst war.** Sein Docstring begründete, die Sweeps würden bewusst nicht geprüft: Deren Tick-Zahlen seien *Erzählungen* und keine Raten. Das stimmt für `active_from_tick` — und nicht für einen `baseline`-Wert einer Größe mit der Einheit `*_per_tick`. Das ist dieselbe Rate an einer zweiten Stelle. Exakt der **Fallstrick** oben: *Wer nur eine der Stellen anfasst, verschiebt den Widerspruch, statt ihn aufzulösen.*

**Der Schaden war nicht der einzelne Wert, sondern die Vergleichbarkeit.** Drei Rahmen rechneten in Jahren, einer in Monaten — und der Szenario-Vergleich stellt sie nebeneinander. Umgerechnet unter Erhalt der Jahresrate: 0,0025 (3 % p.a.), 0,00165 (2 %), 0,00083 (1 %).

**Gemessen über 50 Ticks je Szenario, vorher gegen nachher** — und das Ergebnis ist enger, als man erwarten würde:

| Rahmen | Nachfrageniveau vorher | nachher | Preis | Buchungsrate | Faktorlage |
| --- | ---: | ---: | --- | --- | --- |
| Business as Usual | 0,9141 | 0,8981 | unverändert | unverändert | unverändert |
| CO₂-Verzögerung | 0,6921 | 0,6921 | unverändert | unverändert | unverändert |
| Freiwillige Wende | 0,7959 | 0,7864 | unverändert | unverändert | unverändert |
| Transformationskonflikt | **1,2480** | **0,7909** | unverändert | unverändert | unverändert |

**Bewegt hat sich allein `demand_level`** — die Makrogröße, die neben der gerechneten Buchung mitläuft und in Faktorregeln und Agenten-Prompts eingeht. Preis, Buchungsrate und alle sieben Faktoren sind in allen vier gleich geblieben, weil keine Schwelle überschritten wurde. **Beim Transformationskonflikt geht die Korrektur in die Richtung, die zur Erzählung passt:** Ein Krisenszenario wies vorher ein Nachfrageniveau **über** dem Ausgangswert aus.

**Der Wächter deckt die Lücke jetzt** (`TestAuchDieRahmenszenarienRechnenInMonaten`, drei Zusagen): jede Ratenvorgabe eines Rahmens gegen dieselbe Obergrenze, plus die **Vergleichbarkeit** der vier untereinander. Die zweite ist nicht überflüssig — eine Mutation mit 12,68 % p.a. liegt *unter* der Obergrenze und wird allein von ihr gemeldet. **Stresstests bleiben ausgenommen**, und das ist die Unterscheidung aus P2.2: Ihre Verläufe sind auf Sichtbarkeit gebaut, nicht auf Plausibilität.

**Fertig, gemessen:** `tests/test_ein_tick_ist_ein_monat.py` — zwölf Zusagen über vier Mechanismen, dazu die Sperrklinke, dass der Wächter überhaupt etwas findet. Der Backtest ist neu gerechnet (`docs/backtest_vorlauf.md`), ein Standardlauf über 40 Ticks endet bei **0,267857 / 116,5883** statt 0,268519 / 116,4595 — ein Schnitt in `docs/handbuch/vergleiche.md`. **Doku ist mitgezogen:** `CLAUDE.md` (Invariante 5, Glossar «Tick» und `erneuerungsrate`, Testliste, P2.7-Befund), `docs/handbuch/tick-und-lauf.md`, `docs/handbuch/grenzen.md`, `docs/handbuch/vergleiche.md`, `docs/handbuch/ref-config.md`, `docs/audit_findings.md`.

### P3.1 — System-Properties täuschen keine Laufzeitwerte mehr vor ✅ erledigt 2026-09-05

**Befund:** Für Properties mit `source in {"runtime","computed"}` (z. B. `provider_markup`, `ticket_price`) liefert `resolve_system_properties` laut eigenem Docstring die statische Trajektorien-Baseline, nicht den Laufzeitwert. Folgenlos nur, solange keine ausgelieferte Regel diese IDs per `system_property`-Bedingung referenziert — eine neue Regel darauf würde still gegen eine veraltete Zahl prüfen.
**Fundstelle:** [`src/market/property_engine.py:127-136`](../src/market/property_engine.py).
**Was zu tun ist:** **Vorgabe (2026-08-26): den Zugriff hart ablehnen.** Eine unbekannte oder laufzeitgebundene Property in einer `when`-Bedingung wird ein Konfigurationsfehler, keine stille Baseline. Grund: Laufzeitwerte durchzureichen macht die Regelauswertung innerhalb eines Ticks reihenfolgeabhängig — `apply_factor_rules_at_tick_start` läuft **vor** der Preisberechnung in `environment_node._run_population_tick`, eine Regel auf `ticket_price` würde also je nach Einhängepunkt gegen den Preis von vorhin oder von jetzt prüfen. Das ist eine Modellentscheidung, keine Implementierungsdetailfrage, und sie gehört nicht nebenbei getroffen. Wer die Laufzeitwerte später wirklich braucht, führt sie mit einer bewussten Tick-Phase ein. Zusammen mit P0.4 erledigen — dieselbe Regelmechanik, und dort wird ohnehin festgelegt, dass unbekannte Bedingungstypen laut fehlschlagen.
**Umgesetzt am 2026-09-05, nicht zusammen mit P0.4** — der Plan hatte das vorgesehen, und es ist nicht passiert. P0.4 hat die *Namen* geprüft; eine Regel auf `ticket_price` kam durch, weil der Name ja stimmt. Der Befund lag also die ganze Zeit hinter einer grünen Prüfung.

**Das Vokabular liegt beim Mechanismus, nicht in der Validierung:** [`property_engine.darf_in_regel_stehen`](../src/market/property_engine.py) sagt, welche Quelle eine Bedingung lesen darf, und trägt die Begründung; `validation._validate_rule_property_names` prüft dagegen. Dieselbe Bauform wie `SHIFT_ZIELE` (P2.4) und `KNOWN_METRICS` (P0.4) — eine zweite Liste in der Validierung liefe beim nächsten `source`-Wert auseinander.

**Die Meldung sagt, was stattdessen geht.** Eine Abweisung ohne Ausweg ist eine Sackgasse: Den Preis des laufenden Ticks gibt es als `metric`, und der Text nennt ihn.

**Fertig, gemessen:** `tests/test_validation.py::TestEineRegelLiestKeinenLaufzeitwert` — sechs Zusagen. Darunter zwei, die über den Wortlaut hinausgehen: dass die alte Meldung («unbekannte Systemgröße») von der neuen **nicht verdeckt** wird, und dass die Menge der gesperrten Größen genau `{provider_markup, ticket_price}` ist — kommt eine dritte dazu, wird es rot, und dann gehört ein Blick darauf, ob `resolve_system_properties` für sie wirklich nur die Baseline liefert. **Doku ist mitgezogen:** `docs/handbuch/ref-config.md` (die Tabelle der Bezugsgrößen plus der Grund, warum der Laufzeitwert nicht durchgereicht wird).

### P3.2 — Checkpoint-Version wirklich prüfen ✅ erledigt 2026-09-05

**Befund:** `checkpoint_version` wird in jedes Checkpoint-Metadatum geschrieben (`= 2`), aber nirgends zurückgelesen — `CheckpointManager.load` ignoriert `payload["metadata"]` komplett. Das Feld täuscht eine Versionsprüfung vor, die es nicht gibt.
**Fundstelle:** [`src/orchestration/checkpoint_manager.py:26`](../src/orchestration/checkpoint_manager.py).
**Umgesetzt am 2026-09-05.** `load` prüft die Version, `CheckpointVersionError` sagt, welche Datei welche Version trägt und was zu tun ist. Eine Migration gibt es bewusst nicht — solange es *eine* Version gibt, wäre sie Code ohne Fall.

**Der Fall, den ein bequemes `.get(..., CHECKPOINT_VERSION)` verschluckt hätte:** ein Checkpoint **ohne** Metadatenblock. Die Metadaten gibt es erst seit Version 2, und `latest_checkpoint` findet die alten `round_*.json` weiterhin. Ein fehlendes Feld ist deshalb eine *fremde* Version und keine passende — es als aktuell zu behandeln wäre genau die stille Annahme, gegen die das Paket antritt.

**Die Zahl steht jetzt an einer Stelle** (`CHECKPOINT_VERSION`), und ein Test hält Schreiber und Leser zusammen. Vorher hätte niemand gemerkt, wenn `save` eine 3 geschrieben hätte.

**Fertig, gemessen:** `tests/test_checkpoint_manager.py::TestDieVersionWirdWirklichGeprueft` — fünf Zusagen, darunter der eigene Schreiber (eine Prüfung, die den eigenen Checkpoint abweist, wäre schlimmer als keine) und die *zukünftige* Version: Der Maßstab ist «nicht meine», nicht «älter als meine». **Doku ist mitgezogen:** `docs/handbuch/ref-ausgaben.md`.

### P3.3 — Fehlermeldungen, die auch greifen ✅ erledigt 2026-09-05

**Befund:** Zwei Stellen, an denen Fehlerbehandlung nur so aussieht: In `langgraph_workflow` steht ein `try: pass` mit `except`, das nie feuern kann — die beabsichtigte freundliche Meldung bei fehlendem `langgraph` bleibt aus, stattdessen kommt später ein roher `ImportError`. In `create_graph.py` verschluckt ein `except Exception: pass` auch den absichtlich re-raisten Graph-Build-Fehler, und das Skript schreibt trotzdem ein statisches `graph.json`.
**Fundstelle:** [`src/orchestration/langgraph_workflow.py:41-44`](../src/orchestration/langgraph_workflow.py), [`langgraph_studio/create_graph.py:16-24`](../langgraph_studio/create_graph.py).
**Dazugekommen aus der P0.1-Gegenprobe (2026-08-26): der dritte Fall ist die CLI.** Seit P0.3 weist ein Lauf mit kaputter Config sauber ab — im Dashboard als roter Kasten mit allen Befunden, auf der CLI als **roher Python-Traceback**. `main()` in [`src/run_simulation.py`](../src/run_simulation.py) lässt `ValidationError` einfach durchschlagen; wer `--temperature 99` tippt, sieht zwanzig Zeilen Stack, in denen die eigentliche Meldung untergeht, und bekommt keinen sprechenden Exit-Code. Die Prüfung ist richtig, ihre Darstellung nicht.

**Umgesetzt am 2026-09-05, alle drei Stellen.** Der echte `langgraph`-Import steht im `try` und **vor** `get_llm()` — die Reihenfolge entscheidet, ob der Nutzer «kein langgraph» oder «kein Ollama erreichbar» liest. `create_graph.py` reicht den Build-Fehler durch: kein `graph.json`, kein `Wrote …`. Und die CLI schreibt die Befunde als Liste auf `stderr` und endet mit **2**.

**Der Exit-Code ist 2 und nicht 1**, weil ein Aufrufer «deine Eingabe ist falsch» von «mir ist etwas kaputtgegangen» unterscheiden können soll, ohne die Meldung zu lesen — Skripte und CI tun genau das. Die 2 ist die Konvention, die `argparse` für denselben Fall schon benutzt.

**Was ausdrücklich *nicht* gefangen wird:** alles andere. Ein `KeyError` aus der Engine ist keine Nachricht an den Nutzer, sondern ein Befund für die Entwicklung, und der Stack ist dort die nützlichere Ausgabe. Ein `except Exception` in der Hülle wäre genau das Muster, das dieses Paket an zwei anderen Stellen abräumt — ein Test hält das über den Syntaxbaum fest. **Ein Traceback auf der CLI heißt seither: Programmfehler, nicht Eingabefehler**, und das steht auch so im Handbuch.

**Ein fehlendes `langgraph` ist kein kaputter Graph**, und nur das zweite ist ein Befund: Ohne das Paket schreibt `create_graph.py` die statische Topologie weiterhin — sie ist eine Beschreibung, keine Ausführung — sagt aber, dass sie ungeprüft ist.

**Zwei Funde nebenbei, beide aus der Umsetzung:**

1. **Der Fehlerweg konnte selbst scheitern.** Die Windows-Konsole dieses Projekts steht auf `cp1252`, und in `src/` stehen **46** Zeichenketten mit Zeichen, die dieser Zeichensatz nicht kennt (`→`, `≥`, `₂`, `Δ`, `β`, `✓`) — **gezählt ohne Docstrings**, weil ein Docstring nicht ausgegeben wird; alle Konstanten wären 55. Die Definition steht hier, weil die Zahl ohne sie nicht reproduziert (C1 des Audits). Kein heutiger Validierungsbefund enthält eines davon — ein einziges hätte die Liste durch einen `UnicodeEncodeError` ersetzt, also durch einen Traceback an genau der Stelle, an der dieses Paket eben einen weggeräumt hat. `_schreibe` schreibt deshalb notfalls mit `backslashreplace` (nicht `replace`: ein `≥` ist nachschlagbar, ein `?` ist verloren). Der weitere Umgang mit den 46 Stellen ist [P3.10](#p310--46-zeichenketten-die-die-konsole-nicht-schreiben-kann--erledigt-2026-09-05).
2. **Die eigenen Wächter fielen auf die eigene Prosa herein.** Der erste Anlauf prüfte mit Zeichenkettensuche (`"except Exception" not in quelle`), und **drei von drei** Zusagen schlugen an — an den Kommentaren und Docstrings, die den alten Zustand beschreiben und dabei `try: pass`, `except Exception` und `get_llm()` zitieren. Geprüft wird jetzt der Syntaxbaum. *Ein Wächter, den eine Erklärung über ihn selbst umlenken kann, ist keiner.*

**Fertig, gemessen:** `tests/test_fehlermeldungen_greifen.py` — zwölf Zusagen über alle drei Stellen. Die CLI wird als **eigener Prozess** gestartet: Nur so ist der Exit-Code echt, `main()` im selben Prozess prüfte einen Rückgabewert. **Doku ist mitgezogen:** `docs/handbuch/fehlerbilder.md` (zwei Abschnitte: die Liste auf der CLI und der fremde Zwischenstand aus P3.2), `README.md` (Exit-Codes).

### P3.4 — LLM-Konfiguration zentralisieren ✅ erledigt 2026-09-05

**Befund:** Modellname `"llama3.2"` steht in **10 Produktionsdateien** (nachgezählt am 2026-08-25, das Audit sprach von sieben Stellen), der Endpoint uneinheitlich als `http://localhost:11434` in sieben und `http://127.0.0.1:11434` in zwei Dateien. Bemerkenswert: die beim Dash-Umbau **neu** entstandenen Module `config_editor/compute_mode.py` und `config_editor/llm_pipeline.py` haben die Hartkodierung geerbt — das Finding wächst mit jedem Modul weiter.
**Fundstelle:** `src/run_simulation.py`, `src/llm/llm_client.py`, `src/models/state_models.py`, `src/orchestration/langgraph_adapter.py`, `dashboard/config_catalog.py`, `dashboard/llm_status.py`, `dashboard/run_browser.py`, `dashboard/run_launcher.py`, `dashboard/web/config_editor/compute_mode.py`, `dashboard/web/config_editor/llm_pipeline.py` (plus `tests/test_web_compute_mode.py`, `tests/test_web_layout.py`).
**Verschärft am 2026-08-26 (Fund aus der P0.3-Nachprüfung):** Es geht nicht nur um verstreute Defaults, sondern um ein Feld, das gar nichts tut. `state.config.llm` (`model`, `temperature`, `max_tokens`) wird von **keinem Laufpfad gelesen** — die einzigen Leser sind `langgraph_adapter.py` für die Studio-Schema-Defaults. Der echte Client entsteht aus `RunLaunchConfig` bzw. den CLI-Argumenten. Sichtbarster Beleg: `configs/simulation_config.json` führt `llm.model: "llama3"`, während überall sonst `"llama3.2"` steht — und niemandem fällt es auf, weil der Wert nirgends ankommt.

**Dazugekommen aus der Gegenprobe zu P0.4–P0.6 (2026-08-27): `OllamaConfig` liest keine einzige Umgebungsvariable.** Beim Nachstellen eines Sweeps gegen einen toten Endpunkt sollte `OLLAMA_BASE_URL=http://127.0.0.1:9` den Endpunkt umlenken — im Vorfall stand trotzdem `http://127.0.0.1:11434`. Grund: [`OllamaConfig`](../src/llm/llm_client.py) trägt reine Dataclass-Defaults; die Env-Übersetzung sitzt ausschließlich in `LocalOllama` (`studio_helpers.py`). Jeder Aufrufer, der `OllamaClient(OllamaConfig())` direkt baut — der Sweep-Pfad tut genau das — ignoriert `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TEMPERATURE` und `OLLAMA_MAX_TOKENS` stillschweigend. `OLLAMA_READ_TIMEOUT` und `OLLAMA_RETRIES` werden dagegen gelesen, aber erst im `call`. Die Variable zu setzen und nichts zu bewirken ist dieselbe Klasse von Problem wie die hartcodierten Defaults selbst. Gehört in dieses Paket.

**Dazugekommen aus der P0.1-Gegenprobe (2026-08-26): `get_llm()` wählt still den Mock.** P0.1 hat den stillen Mock **bei Fehlern** beseitigt — die Auswahl davor ist geblieben. [`studio_helpers.get_llm()`](../src/llm/studio_helpers.py) fällt am Ende seiner Kette kommentarlos auf `MockLLM()` zurück, wenn weder `OLLAMA_MODEL` noch `LLAMA_HTTP_URL` noch `LLAMA_TRANSFORMERS_MODEL` gesetzt ist. Zwei Aufrufer hängen noch daran: [`langgraph_workflow.py:48`](../src/orchestration/langgraph_workflow.py) (der Graph für LangGraph Studio) und [`run_scenario_generator/cli.py:33`](../src/reporting/run_scenario_generator/cli.py). Wer Studio ohne gesetzte Umgebung startet, bekommt erfundene Agenten-Antworten, ohne sie angefordert zu haben — kein `--mock-llm`, kein Hinweis, und nach der Definition aus Invariante 1 auch kein „Ausfall", weil nie ein Aufruf gescheitert ist. Der bewusste Mock (`--mock-llm`, «Ohne Sprachmodell») ist davon unberührt und richtig so.

**Umgesetzt am 2026-09-05 in drei Schritten**, weil es drei verschiedene Befunde in einem Paket waren.

**1 — Eine Quelle.** [`src/llm/defaults.py`](../src/llm/defaults.py) hält Modellname, Endpunkt, Temperatur und Antwortlänge; alle Stellen zeigen darauf, auch `configs/simulation_config.json`. **Der Endpunkt ist jetzt `127.0.0.1` und nicht `localhost`**, und das ist keine Kosmetik: `localhost` löst auf manchen Windows-Installationen zuerst nach `::1` auf, während Ollama nur auf IPv4 lauscht. **Und die Umgebungsvariablen liegen *in* der Quelle**: `OllamaConfig` liest sie selbst, per `default_factory` beim Bauen und nicht beim Importieren. Damit wirkt `OLLAMA_BASE_URL` auch für den Sweep-Pfad, der seinen Client direkt baut — der Befund vom 2026-08-27.

**2 — `state.config.llm` ist angeschlossen** (entschieden gegen «ersatzlos entfernen»). Je Oberfläche eine Ableitung — `llm_config_from_draft` und `_llm_config_from_args` —, sie füllt den Zustand, und der Client entsteht daraus: eine Quelle, zwei Leser. `LLMConfig` trägt dazu `base_url`, weil ein Modellname ohne Endpunkt den Lauf nur halb beschreibt. **Bei einem Lauf ohne Sprachmodell bleibt das Feld unberührt** — gerufen wird nichts, also beschreibt es nichts, und `compute_mode` sagt das im Artefakt.

**3 — Der Mock kommt nur auf Ansage.** `get_llm()` scheitert jetzt, wenn kein Backend konfiguriert ist, statt kommentarlos `MockLLM()` zu liefern; die Meldung nennt alle vier Wege hinaus, und **jede** getroffene Wahl steht als `INFO` im Log. Der Schalter dafür ist eine Umgebungsvariable (`AEROFORESIGHT_MOCK_LLM`) und **nicht** nur ein Parameter: Die beiden Aufrufer — der Studio-Graph und die Szenario-CLI — bauen `get_llm()` ohne Argumente, ein Parameter allein hätte niemanden erreicht.

**Drei Funde aus der Umsetzung, alle gemessen:**

1. **Jeder Befund stand danach doppelt da.** Solange die Sprachmodell-Werte den Zustand nicht erreichten, musste `validate_draft` sie eigens danebenprüfen; seit sie es tun, prüft `collect_state_errors` genau dieselben Werte — einmal als «config.llm: …» und einmal als «Technik: …». Die zweite Prüfung ist weg, und der Herkunftsort heißt jetzt **«Sprachmodell»** statt «config.llm»: Der Name eines Datenfelds ist kein Name für eine Einstellung, und jetzt liest *jede* Oberfläche diese Meldung.
2. **Ein leeres Modellfeld wurde stillschweigend zu `llama3.2`.** Der erste Anlauf von `llm_config_from_draft` schrieb `draft.model.strip() or DEFAULT_MODEL` — dieselbe erfundene Vorgabe, die [P1.9-W5.1](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28) im Dashboard abgeräumt hat. Aufgefallen ist es, weil die alte Doppelprüfung diesen Fall meldete und die neue nicht mehr.
3. **`base_url` wurde nie geprüft.** Ein Feld ohne Schema (`127.0.0.1:11434`) sieht richtig aus und ergibt einen Aufruf ohne Host: ein Verbindungsfehler mitten im Lauf, dem niemand die Ursache ansieht. Er wird jetzt beim Start gemeldet — und der **Wizard-Wächter** hat dabei gemeldet, dass das neue Feld in `FELD_SCHRITT` fehlte, sein Befund also auf «Prüfen & Starten» gelandet wäre statt an seinem Feld.

**Fertig, gemessen:** [`tests/test_llm_defaults.py`](../tests/test_llm_defaults.py) — 25 Zusagen in vier Gruppen. Der Wächter gegen eine zweite Quelle ist ein **AST-Durchlauf über `src/` und `dashboard/`** und keine Liste der neun Dateien: Genau so ist der Befund gewachsen — die beim Dash-Umbau neu entstandenen `config_editor`-Module haben die Hartkodierung *geerbt*, per Kopie, ohne dass jemand sie dort hingeschrieben hätte. Eine Aufzählung fängt den Rückfall an bekannter Stelle und übersieht das zehnte Modul. **Doku ist mitgezogen:** `README.md` (Umgebung, Exit-Codes, Backend-Auswahl), `langgraph_studio/.env.example`, `docs/handbuch/lauf-konfigurieren.md` (die Adresse in der Prüftabelle und der Absatz «Technik»).

### P3.5 — Stille Klemmungen und Debug-Ausgaben ✅ erledigt 2026-09-05

**Befund:** `threshold` und `max_contributions_per_agent` werden ohne Warnung auf einen Wunschbereich geklemmt — wer bewusst `threshold=1` setzt, bekommt stillschweigend 3. Dazu acht `print()`-Debugausgaben im Scheduler, die bei jedem Tick unbedingt laufen.
**Fundstelle:** [`src/agents/redebedarf_scheduler.py:73,75`](../src/agents/redebedarf_scheduler.py), [`src/agents/scheduler_node.py`](../src/agents/scheduler_node.py) (8 Vorkommen).
**Was zu tun ist:** Klemmung protokollieren oder als Konfigurationsfehler abweisen; `print()` durch `logging` mit Level-Guard ersetzen.
**Reihenfolge (2026-08-26):** **nicht vor P0.1.** Das Fortschritts-Log des Dashboards wird ausschließlich von `print()` gespeist (`run_launcher.py:397` leitet `stdout` in einen Tee um). Der Logging-Handler, der in denselben Tee schreibt, entsteht in P0.1; landet P3.5 vorher, verschwinden die Scheduler-Zeilen aus dem Live-Log, ohne dass jemand einen Fehler sieht.
**Umgesetzt am 2026-09-05, und aus «protokollieren» ist «abweisen» geworden.** Der Plan ließ beides zu; abgewiesen wird jetzt, weil ein geklemmter Wert eine Einstellung *annimmt* und mit einer anderen rechnet — dieselbe Bauform, die [P2.11](#p211--zwei-quellen-für-dieselbe-marktkonstante--erledigt-2026-09-03) bei den Marktkonstanten und P1.9-W5.1 im Dashboard abgeräumt hat. **Die Grenzen sind dieselben wie vorher**, geändert hat sich nur, dass sie etwas sagen; kein Aufrufer im Repo setzt die beiden Werte, das Abweisen bricht also nichts.

**Ein Fall kam dazu, den die Klemmung nicht kannte:** `threshold > max_score`. Die alte Klemmung fing nur nach unten ab — liegt die Schwelle über der Skala, kann kein Agent sie je überschreiten, und der Scheduler bliebe **dauerhaft stumm**. Das sah aus wie ein Lauf, in dem niemand Redebedarf hatte.

**Und die Grenzen stehen nicht mehr als Literale im Konstruktor.** `max(3, threshold)` stand neben `DEFAULT_THRESHOLD = 3`: Wer die Konstante geändert hätte, hätte die Klemmung unverändert gelassen — die zweite Quelle noch einmal, eine Ebene tiefer. Ein Test hält per AST fest, dass im Konstruktor nicht wieder geklemmt wird.

**Bei den acht `print()` war die Einteilung die Arbeit**, nicht der Kanal. «Auf stdout still» und «das Fortschritts-Log zeigt weiterhin, was es vorher zeigte» widersprechen sich, wenn man alles auf `debug` legt. Es sind daher drei Stufen: die **Sprechreihenfolge** bleibt `info` und steht damit weiter im Fortschrittsfenster (es hängt seit P0.1 über `progress_logging` an `logging`), die **Sicherheitsgrenze** wird eine `warning` — dass der Rest eines Ticks übersprungen wird, gehört gesehen —, der Rest ist `debug`.

**Die Reihenfolgeregel ist eingehalten** (nicht vor P0.1), und die tragende Zusage prüft genau sie: `test_das_fortschrittsfenster_sieht_die_reihenfolge` schickt die Zeile durch `progress_logging` — dieselbe Kette, die das Dashboard benutzt — statt nur zu prüfen, dass irgendwo geloggt wird.

**Fertig, gemessen:** [`tests/test_stille_klemmungen.py`](../tests/test_stille_klemmungen.py) — 17 Zusagen. **Doku ist mitgezogen:** `docs/handbuch/akteure.md` (eine Zeile je Runde statt acht, plus die Sicherheitsgrenze).

### P3.6 — Stabiler Vertrag für den Run-Launcher ✅ erledigt 2026-09-05

**Befund:** `run_launcher` importiert drei unterstrichs-präfixierte Funktionen aus `run_simulation` (`_build_run_args`, `_save_run_outputs`, `_write_multi_run_summary`). Kein stabiler Vertrag — ein Refactor der internen Helper bricht den Launcher unbemerkt.
**Fundstelle:** [`dashboard/run_launcher.py:168`](../dashboard/run_launcher.py).
**Umgesetzt am 2026-09-05.** Die drei Namen heißen ohne Unterstrich, stehen im `__all__` von [`src/run_simulation.py`](../src/run_simulation.py), und dessen **neuer Modul-Docstring** sagt, dass dieses Modul zwei Dinge ist: der Batch-Einstieg *und* das, was jeder Startpfad nach einem Lauf tut. Bis dahin gab es nur für das erste einen Namen — daher der Griff ins Innenleben.

**Die alten Namen sind weg, nicht daneben stehen geblieben.** Beide gleichzeitig zu führen wäre die schlechteste Variante: Der Launcher hinge weiter am alten, und niemand merkte es.

**Der Wächter musste in den Funktionsrumpf schauen**, und das ist die Lehre des Pakets: Der Import stand nicht im Dateikopf, sondern **mitten in `_run_body`** (`dashboard/run_launcher.py:179`). Ein Test, der die obersten Importzeilen liest — der naheliegende —, hätte ihn nie gefunden. [`tests/test_launcher_vertrag.py`](../tests/test_launcher_vertrag.py) läuft deshalb über den ganzen Syntaxbaum und prüft das mit einem eigenen Fall nach.

**Die andere Hälfte dieses Pakets war schon erledigt.** Beim Vorziehen am 2026-08-28 lautete die Begründung: Ohne eine Schnittstelle, die sagt, *was ein Startpfad entgegennimmt*, lässt sich W1.1 nicht mechanisch halten. Das leisten seit P1.9-W1.1 `scenario_sweeps.FESTLEGUNGEN` und `UNBEACHTET` (Invariante 7); übrig blieb die Namensfrage.

**Nicht gemacht, bewusst:** Die Lauf-Argumente sind weiterhin ein `SimpleNamespace`, den `run_launcher` an zwei Stellen von Hand baut, und die Artefakt-Schreiber lesen daraus mit `getattr(..., False)`. **Genau daraus ist der `mock_llm`-Fehler von P0.6 entstanden** — ein fehlendes Feld war von einem abgeschalteten nicht zu unterscheiden, und jeder Dashboard-Lauf «Ohne Sprachmodell» wurde als vollwertiger LLM-Lauf protokolliert. Ein typisiertes Modell an dieser Grenze wäre Invariante 4 und macht aus dem stillen Rückfall einen `TypeError`; es ist **ein eigenes Paket**, weil es die Artefakt-Schreiber mit anfasst und nicht nur den Import. Eingeplant als [P3.11](#p311--die-lauf-argumente-sind-ein-simplenamespace--erledigt-2026-09-05).

**Fertig, gemessen:** neun Zusagen. **Doku ist mitgezogen:** `CLAUDE.md` (Service-Layer-Absatz der Architektur-Map).

> **Vorgezogen am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--erledigt-2026-08-30-audit-2026-08-28)): Der fehlende Vertrag ist nicht nur ein Refactor-Risiko — er ist die Ursache dafür, dass der Assistent Felder erfragt, die der Sweep-Pfad still verwirft. Ohne eine öffentliche Schnittstelle, die sagt, **was ein Startpfad entgegennimmt**, lässt sich W1.1 nicht mechanisch halten.

### P3.11 — Die Lauf-Argumente sind ein `SimpleNamespace` ✅ erledigt 2026-09-05

> **Aus der Umsetzung von [P3.6](#p36--stabiler-vertrag-für-den-run-launcher--erledigt-2026-09-05).** Dessen Kriterium ist erfüllt — die Namen sind öffentlich —, aber der *Vertrag* ist weiterhin keiner: Er ist ein Namensraum ohne Form.

**Befund:** `save_run_outputs`, `build_run_args` und `save_run_metadata` bekommen ihre Lauf-Argumente als `argparse.Namespace` bzw. `types.SimpleNamespace` und lesen daraus mit `getattr(args, "feld", False)`. `dashboard/run_launcher.py` baut diesen Namensraum an **zwei** Stellen von Hand, mit je fünfzehn Feldern. Eine Struktur gibt es nicht: Kein Modell beschreibt, was ein Startpfad liefern muss, und ein fehlendes Feld ist von einem abgeschalteten nicht zu unterscheiden.

**Der Schaden ist eingetreten und dokumentiert, zweimal in derselben Datei.** `mock_llm` fehlte im handgebauten Namensraum, `save_run_metadata` fiel auf `False` zurück, und **jeder Dashboard-Lauf «Ohne Sprachmodell» wurde als vollwertiger LLM-Lauf protokolliert** — gefunden in der zweiten Gegenprobe zu P0.6. Der zweite Fall ist `llm_narrative`: Dort steht heute ein ausgeschriebenes `False` mit einem Kommentar, der erklärt, *warum* es ausgeschrieben dasteht («ein weggelassenes Feld ist von einem abgeschalteten nicht zu unterscheiden»). Dieser Kommentar ist der Befund.

**Fundstellen:** [`src/run_simulation.py`](../src/run_simulation.py) (`build_run_args`, `save_run_outputs`), [`dashboard/run_launcher.py`](../dashboard/run_launcher.py) (zwei handgebaute `SimpleNamespace`), [`src/reporting/output_writer/metadata.py`](../src/reporting/output_writer/metadata.py) und [`provenance.py`](../src/reporting/output_writer/provenance.py) (`getattr`-Rückfälle).

**Was zu tun ist:** Ein typisiertes Modell an dieser Grenze — **Invariante 4**, die für Agenten-Grenzen längst gilt und hier nicht. Aus dem stillen Rückfall wird damit ein `TypeError` beim Bauen: Wer ein Feld vergisst, erfährt es beim Start und nicht aus einem falschen Artefakt drei Wochen später. Die `getattr`-Rückfälle in den Schreibern fallen mit weg — sie sind nur da, weil der Namensraum formlos ist.

**Fallstrick:** Ein Feld, dessen Rückfall eine *Aussage* ist (`no_run_scenario` bei einem Pfad, der nie eines erzeugt), braucht einen Vorgabewert mit Begründung — dieselbe Unterscheidung wie `AUSNAHMEN` in `tests/test_cost_pressure_source.py`. Wer alles zur Pflicht macht, erzeugt fünfzehn Felder, die jeder Aufrufer stumpf ausschreibt, und gewinnt nichts.

**Umgesetzt am 2026-09-05.** [`models.run_models.RunArgs`](../src/models/run_models.py) mit `extra="forbid"`; alle vier Bauer liefern es (CLI, die zwei handgebauten des Dashboards, der Sweep-Pfad), und die Schreiber lesen Attribute statt zu raten.

**Die Trennlinie zwischen Pflicht und Vorgabe ist der Rechenmodus**, und das ist die eigentliche Entscheidung dieses Pakets. Pflicht ist, was in `compute_mode` einfließt — `mock_llm`, `deterministic_only`, `llm_narrative` —, denn ein falscher Wert *dort* lässt den Lauf im eigenen Artefakt etwas Falsches über sich behaupten, und genau das ist zweimal passiert. Alles andere beschreibt, was ein Lauf *nebenbei* tut (ein Protokoll schreiben, ein Szenario erzeugen); dort heißt ein ausgelassenes Feld ohne Zweideutigkeit «nein», und der Vorgabewert steht **nur im Modell**. Der Fallstrick des Pakets ist damit beantwortet, ohne fünfzehn Pflichtfelder zu erzeugen.

**Ein zweiter Verlust ist dabei aufgefallen, latent seit Langem:** `build_run_args` kopierte **`llm_narrative` gar nicht mit**. Nachgestellt vor der Änderung — aus `deterministic_with_llm_narrative` wurde beim Durchreichen `deterministic_only`. Kein Pfad erreicht die Kombination heute (das Dashboard setzt `False`, die CLI hat keinen Schalter, der Sweep-Pfad ruft `save_run_metadata` direkt), **die nächste Änderung hätte sie erreicht**. Dieselbe Auslassung wie bei `mock_llm`, nur ein Feld weiter.

**Wo ein Pfad ein Pflichtfeld strukturell nicht kennen kann, sagt er es ausdrücklich:** Die CLI hat keinen `--llm-narrative`-Schalter, weil nur der Sweep-Pfad den Hybridmodus erzeugt — sie setzt das Feld per `parser.set_defaults(llm_narrative=False)`, mit dem Grund daneben. Das ist ein Vorgabewert **als Aussage des Pfades**, nicht als Rückfall des Lesers, und damit genau die Unterscheidung, die der Fallstrick verlangt.

**Zwei Felder sind dabei verschwunden, weil sie niemand las:** `sweep` im Sweep-Pfad und `run_id`/`checkpoint_dir` in den beiden Namensräumen des Dashboards. `save_run_outputs` bekommt beides als eigenes Argument; im Namensraum reisten sie nur mit. `extra="forbid"` hat sie beim ersten Lauf gemeldet — der Vertrag findet totes Beiwerk, ohne dass jemand danach sucht.

**Ein Wächter musste dabei umgebaut werden, und er hatte es vorhergesagt.** `tests/test_provenienz_vollstaendig.py` suchte die Herkunftsfelder als `getattr(args, "x", …)` in den Schreibern — genau das, was P3.11 entfernt. Sein eigener Docstring nannte den Fall: «Entweder ist es weg, oder es wird jetzt anders gelesen — dann greift dieser Test ins Leere.» Er liest jetzt Attributzugriffe, sein Anker ist `mock_llm` statt des entfallenen `run_id`, und eine Zusage ist dazugekommen: dass die drei Felder des Rechenmodus **Pflicht** sind.

**Fertig, gemessen:** [`tests/test_lauf_argumente.py`](../tests/test_lauf_argumente.py) — 13 Zusagen. Darunter der AST-Durchlauf über die drei Schreiber (kein neues `getattr(args, …, default)`), der Nachweis, dass **jedes** Feld das Durchreichen übersteht (nicht nur das eine, das aufgefallen ist), und dass kein Startpfad wieder einen formlosen Namensraum baut. **Doku ist mitgezogen:** `CLAUDE.md` (Invariante 4 und die Architektur-Map).

### P3.10 — 46 Zeichenketten, die die Konsole nicht schreiben kann ✅ erledigt 2026-09-05

> **Gefunden beim Bau des Fehlerwegs von [P3.3](#p33--fehlermeldungen-die-auch-greifen--erledigt-2026-09-05)** — und das Prüfskript, das den Befund erhob, ist selbst daran gescheitert. Ehrlicher lässt sich ein Befund kaum belegen.

**Befund:** Die Windows-Konsole dieses Projekts steht auf **`cp1252`** (`sys.stdout.encoding` nachgemessen). In `src/` stehen **46** Zeichenketten — Laufzeittexte, keine Docstrings —, die Zeichen enthalten, die dieser Zeichensatz nicht kennt: `→` (28×), `₂` (8×), `≥`/`≤` (4×), dazu `Δ`, `β`, `≈`, `✓`, `⚠`. Jeder `print` und jede Log-Zeile mit einem dieser Zeichen wirft einen `UnicodeEncodeError`.

**Warum es heute meistens nicht auffällt:** Die betroffenen Texte gehen überwiegend in **Dateien**, und die werden mit `encoding="utf-8"` geschrieben — dort ist alles richtig. Getroffen wird nur, was wirklich auf die Konsole geht. Zwei Stellen sind dabei die heiklen: `rule_engine._OPERATOR_LABELS` (`≥`, `≤`) speist `describe_when`, und `agent_dependencies` trägt ein `→` in einem Meldungstext.

**Warum es trotzdem ein Befund ist:** Ein `UnicodeEncodeError` beim *Melden* verschluckt die Meldung. Innerhalb von `logging` wird er zu einem «--- Logging error ---» mit Stack statt der Zeile; in einem `print` reißt er den Aufruf ab. Das ist dieselbe Klasse wie P3.3 selbst — eine Ausgabe, auf die man sich verlässt, kann still oder laut verschwinden, und zwar genau dann, wenn man sie braucht.

**Fundstellen:** 46 Stellen über `src/` (Zeichenketten-Konstanten **ohne Docstrings** — alle wären 55); die Liste erzeugt ein AST-Durchlauf (Vorlage steht in der Umsetzung von P3.3). Die Zeichensatz-Grenze liegt in `sys.stdout.encoding`, nicht im Code.

**Was zu tun ist — und was nicht:** Nicht 46 Zeichenketten umschreiben. `→` in einem Erklärtext ist richtig, und `CO₂` ist der korrekte Name des Stoffs. Zu entscheiden ist die **Ausgabeseite**, und dafür gibt es zwei Wege:

1. **Die Stdio-Kodierung auf UTF-8 stellen** (`sys.stdout.reconfigure(encoding="utf-8")` im CLI-Einstieg, oder `PYTHONUTF8=1`). Löst die ganze Klasse mit einer Zeile. **Der Preis ist zu messen:** Eine `cp1252`-Konsole zeigt UTF-8-Bytes als Buchstabensalat, und das Fortschritts-Log des Dashboards liest denselben Strom (`run_launcher` leitet `stdout` in einen Tee um) — was dort ankommt, entscheidet über die Darstellung im Browser. **Nicht ohne diese Messung entscheiden.**
2. **Jede Ausgabestelle zeichensatzfest machen** (wie `_schreibe` in P3.3). Ehrlich und lokal, aber es sind viele Stellen, und die nächste vergisst es wieder.

**Fallstrick:** Wer Weg 1 wählt, prüft **beide** Enden — die Konsole *und* das Fortschritts-Log im Dashboard. Der Tee ist der Grund, warum P3.5 nicht vor P0.1 durfte; hier ist er es wieder.

**Fertig wenn:** Eine Meldung mit `≥` oder `CO₂` erreicht Konsole **und** Fortschritts-Log lesbar — gemessen an beiden Enden, nicht an einem. Der Wächter ist der AST-Durchlauf: Er zählt die Stellen und darf nach der Entscheidung entweder auf 0 stehen (Weg 1 macht ihn überflüssig) oder als Zähler bleiben.

---

**Umgesetzt am 2026-09-05 — und die Messung hat den Befundtext an zwei Stellen widerlegt.** Beides gehört hierher, weil es die Entscheidung getragen hat.

**Erstens: es ist kein Konsolenproblem.**

| `sys.stdout` ist … | `encoding` | `print("≥")` |
| --- | --- | --- |
| eine echte Konsole | `utf-8` (`_WindowsConsoleIO`) | läuft durch |
| umgeleitet (Datei, Pipe, CI, Dienst) | `cp1252` (`FileIO`) | `UnicodeEncodeError` |

Damit fällt der Einwand gegen **Weg 1** weg: Eine cp1252-Konsole, die UTF-8 als Buchstabensalat zeigte, gibt es nicht — wo cp1252 auftaucht, schreibt Python in eine Datei oder Pipe, und dort ist UTF-8 genau richtig. Der Fallstrick («beide Enden prüfen») bleibt richtig und ist eingelöst; die Sorge um die Darstellung war gegenstandslos.

**Zweitens, und unangenehmer: die Umstellung gab es schon — als Import-Seiteneffekt.** In `src/orchestration/scenario_sweeps.py` standen auf Modulebene zwei Zeilen:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

Sie änderten einen **prozessglobalen** Zustand, sobald jemand irgendetwas aus `src.orchestration` importierte — das Paket-`__init__` zieht das Sweep-Modul mit. Gemessen deckte das **7 von 11** Einstiegspunkten ab, ohne dass es irgendwo dokumentiert war: Der CLI-Lauf, das Dashboard und der State Explorer waren *zufällig* sicher; `create_graph.py`, `serve_graph.py` und `cib_visualizer.py` nicht. Und **`stderr` war nirgends gesichert** — dort landen die Logging-Fehler und die Befundliste einer kaputten Konfiguration (P3.3).

Das erklärt auch, warum der erste Ende-zu-Ende-Versuch «vorher» *nicht* scheiterte: Der Seiteneffekt hatte ihn gerettet. Der ehrliche Beweis läuft deshalb über `cib_visualizer` — einen Pfad, den er nicht deckte: **vorher `UnicodeEncodeError`, nachher durchgelaufen.**

**Was gilt:** `logging_setup.stdio_auf_utf8()` stellt `stdout` **und** `stderr`, jeder Einstiegspunkt ruft sie ausdrücklich, und der Seiteneffekt ist weg. Die 46 Zeichenketten bleiben, wie sie sind — `CO₂` ist der Name des Stoffs.

**Die Ausnahme ist der Ordner `scripts/`**, mit Grund: Die drei Helfer sind eigenständig, importieren sonst nichts aus `src` und tragen keine einzige Zeichenkette, die cp1252 nicht kann (gemessen). **Beim ersten Anlauf war die Kopplung drin und hat zwei von ihnen gebrochen** (`ModuleNotFoundError: No module named 'src'`) — daher die Ausnahme, und daher prüft der Wächter ihre Begründung nach, statt sie zu glauben.

**Ein Nebenbefund, vom Wächter selbst gefunden:** `langgraph_studio/__init__.py` trug ein **BOM**, an dem `ast.parse` scheitert (`invalid non-printable character U+FEFF`). Kein Ausgabe-, sondern ein Quelltext-Zeichensatz — aufgefallen, weil dieser Durchlauf als erster `langgraph_studio/` liest. Das BOM ist weg, und der Wächter liest `utf-8-sig`, damit das nächste ihn nicht umbringt.

**Fertig, gemessen:** [`tests/test_zeichensatz.py`](../tests/test_zeichensatz.py) — 14 Zusagen. Beide Enden (Strom *und* Fortschrittsfenster, letzteres **durch den Tee**, weil nur dort der Verlust auftrat), der Gegenbeweis ohne die Sicherung, `stderr`, die Idempotenz, ein Strom der sich weigert (er wird gemeldet, nicht verschluckt) — und zwei Zusagen gegen den Rückfall: kein Import stellt die Ausgabe wieder heimlich um, und die Umstellung steht an genau einer Stelle.

**Doku ist mitgezogen:** `CLAUDE.md` (Architektur-Map zu `logging_setup.py`, Dev-Workflow), `README.md` (Umleiten ist sicher).

---

### Audit der Phase 3 (2026-09-05) — fünf Pakete, der schwere Befund ist vorbestehend

Phase 3 ist am Tag ihres Abschlusses vollständig geprüft worden. Vollfassung:
[`audit_phase3_2026-09-05.md`](audit_phase3_2026-09-05.md).

**Die Einschränkung gehört an den Anfang, weil sie das Gewicht des Ergebnisses
bestimmt: dieses Audit ist nicht unabhängig.** Phase 2 hat jemand geprüft, der
sie nicht gebaut hat; hier fällt beides zusammen. Wer eine Zusage aufgeschrieben
hat, sucht nicht mit demselben Eifer nach ihrer Lücke — und er kennt die Stellen,
an denen er weggeschaut hat, nicht als Lücken, sondern als Entscheidungen.
Ersetzt wurde das durch **Verfahren statt Absicht**: jeder tragende Wächter
absichtlich kaputtgemacht und musste rot werden (**fünfzehn von fünfzehn**), jede
veröffentlichte Zahl neu erhoben statt nachgelesen, geprüft am laufenden System
statt am Quelltext, der die Zusage behauptet. **Sechs Messungen mussten ihren
ersten Anlauf verwerfen, weil der Prüfling falsch war** — das steht in der
Vollfassung jeweils dabei, weil ein Audit, das nur seine Treffer zeigt, seine
eigene Trefferquote überzeichnet.

**Was hält:** Elf von zwölf Paketen, und zwar nachgemessen und nicht gelesen —
die CLI wirklich mit zwei fremden Checkpointformen gestartet (beide abgewiesen,
Exitcode 2, kein Traceback), die LLM-Validierung in drei Varianten ausgelöst,
P3.1 an **allen drei** Regelarten geprüft, ein Dashboard-Lauf wirklich gerechnet
und sein `run_metadata.json` gelesen (`compute_mode: mock_llm` — die Zusage, an
der P3.11 hängt). **Kein Befund berührt die Zahlen eines Laufs.**

**Was nicht hält**, sind vier Ränder — und drei davon sind dieselbe Fehlerart wie
die Lehre der Phase selbst: eine Prüfung oder eine Zusage, die nur so aussieht.
**Der einzige schwere Befund kommt nicht aus Phase 3**, sondern ist ein
Rückfall aus Phase 2, den dieses Audit gefunden hat (P3.17):

| Paket | Befund | Schwere |
| --- | --- | --- |
| [P3.13](#p313--der-abgeschaffte-rückfall-lebt-eine-ebene-höher--erledigt-2026-09-05) | `draft_to_launch_config` erfindet `llama3.2` für ein leeres Modellfeld — der Rückfall, den P3.4 zwanzig Zeilen weiter abgeschafft hat | 🔶 **behoben** |
| [P3.14](#p314--der-fehlerweg-braucht-keinen-puffer--erledigt-2026-09-05) | `_schreibe` setzt `sys.stderr.buffer` voraus; ohne wird aus dem `UnicodeEncodeError` ein `AttributeError` — und alle drei Tests teilen die Annahme | 🔶 |
| [P3.15](#p315--eine-signatur-die-ihrem-rumpf-widerspricht--erledigt-2026-09-05) | `sweep_metadata_args` sagt `-> SimpleNamespace` und liefert `RunArgs`; `sweep_id` ist unbenutzt; der tote Import bleibt für `ruff` unsichtbar | 🔶 **behoben** |
| [P3.16](#p316--das-500-ms-kriterium-und-sein-deckel--erledigt-2026-09-05) | P3.9s Kriterium lautet 500 ms, sein Wächter deckelt bei 900 — ein Rückfall auf 800 bliebe grün | 🔶 **behoben** |
| [P3.17](#p317--der-browser-wächter-ist-rot-und-niemand-läuft-ihn--erledigt-2026-09-06) | Der Browser-Wächter ist **112 zu 6** rot — **vorbestehend**, auf `main` identisch nachgemessen. C5 des Phase-2-Audits gilt als behoben und ist es nicht, mit neuen Ursachen | ⛔ **behoben** |

Fünf kleine Befunde brauchten kein eigenes Paket, und **alle fünf sind am
2026-09-06 erledigt**: die Nutzermeldung, die `llama3.2` erfindet (mit P3.13), der
veraltete Docstring an der Klickmessung (mit P3.16), ein Doku-Verweis auf ein
Modul, das es nicht gibt (C4), die Zähldefinition hinter der «46» (C1) und die
klein geschriebene Kopfzeile der CLI (C2). Zwei davon waren **vorbestehend**.

**Zwei der fünf waren beim Anfassen größer als gemeldet**, und beide auf dieselbe
Weise — die gemeldete Kleinigkeit war ein Symptom:

* **C1** nannte eine ungenannte Zähldefinition. Nachgemessen reproduzierte
  **keine** der drei Zahlen, die den Modell-Bereich beschreiben (146 statt 168
  Bedienelemente, 1886 von 3364 statt 1404 von 2882 Knoten). Zwei davon waren
  *irgendwann* richtig und sind in eine Aussage über heute gewandert. Die Klasse
  ist [P4.3](#p43--doku-zahlen-mechanisch-halten--erledigt-2026-09-11), das dort jetzt drei konkrete
  Kandidaten hat.
* **C2** nannte einen kleingeschriebenen Wortlaut. Derselbe Text stand an **drei**
  Stellen wörtlich; dass sie identisch waren, war Zufall und kein Mechanismus. Es
  gibt jetzt `validation.BEFUND_KOPF` und einen Wächter über die eine Quelle —
  der Wortlaut selbst braucht keinen.

**Die Lehre über beide:** Ein 🔷 sagt etwas über die *Auswirkung*, nicht über die
*Tiefe*. Wer einen kleinen Befund behebt, ohne ihn nachzumessen, behebt das
Symptom.

**Der Prüfstand, damit die Zahlen nachschlagbar sind:** `pytest` ohne die zwei
dokumentierten Ollama-Hänger und ohne den Browser-Wächter — **1641 passed, 1
skipped, 2 deselected** in 2:17, kein Fehlschlag. Der Browser-Wächter separat:
**112 passed, 6 failed** in 22:17 (das ist P3.17). `ruff check .` und
`black --check .` grün über 250 Dateien. Keine Datei bleibt verändert: Die
Mutationsprobe schreibt in dreizehn Dateien und nimmt jede Änderung in einem
`finally` zurück, und ein Probelauf in `outputs/` ist entfernt — weil der
Höhen-Deckel an dessen Inhalt hängt.

---

### P3.13 — Der abgeschaffte Rückfall lebt eine Ebene höher ✅ erledigt 2026-09-05

**Fundstelle:** [`dashboard/run_launcher.py:144`](../dashboard/run_launcher.py),
dazu [`dashboard/web/config_editor/compute_mode.py:116`](../dashboard/web/config_editor/compute_mode.py).

**Befund.** P3.4 hat `draft.model.strip() or DEFAULT_MODEL` aus
`llm_config_from_draft` entfernt und mit einem Kommentar zum Befund erklärt —
«Ein leeres Modellfeld ist ein Befund und keine Gelegenheit, `llama3.2`
einzusetzen». Zwanzig Zeilen weiter steht dieselbe Zeile noch. Gemessen mit
geleertem Feld und `mock_llm=False`:

| Weg | `state.config.llm.model` | Befund der Validierung |
| --- | --- | --- |
| Preflight (`prepare_simulation_state(entwurf)`) | `''` | «Sprachmodell: Modellname darf nicht leer sein» |
| Lauf (`draft_to_launch_config` → `launch_config_to_draft`) | `'llama3.2'` | **keine** |

Der Rundlauf **wäscht** den erfundenen Wert: Danach ist er von einem eingetippten
nicht mehr zu unterscheiden. `_build_llm` trägt dazu den Docstring «der Client
aus **derselben** Ableitung, die auch den Zustand füllt» — die Ableitung ist
dieselbe, ihre **Eingabe** ist es nicht.

**Warum es zählt.** Der Preflight sagt etwas anderes als der Lauf, und das
Artefakt nennt ein Modell, das niemand gewählt hat. Dieselbe Klasse wie
P1.9-W5.1 (ein Literal als zweite Quelle für einen Vorgabewert) und P2.11 (zwei
Quellen für denselben Wert). **Praktisch abgeschirmt** ist es durch das Tor aus
P1.9-W2.2 — aber die Abschirmung liegt in der Oberfläche und nicht im
Service-Layer, den auch andere aufrufen.

**Fertig wenn:** Das `or DEFAULT_MODEL` ist weg, und ein Wächter in
`tests/test_llm_defaults.py` schickt **denselben** leeren Entwurf über beide Wege
und verlangt dasselbe Ergebnis. Die Nutzermeldung in `availability` sagt «kein
Modell eingestellt» statt einen Namen zu erfinden. **Nicht** in denselben Commit
gehört eine Änderung an der Reihenfolge oder am Tor — das wäre eine zweite
Änderung in derselben Zeile.

**Was gilt** (2026-09-05): `draft_to_launch_config` schreibt
`model=draft.model.strip()`, ohne `or`. Beide Wege führen bei leerem Feld auf
`''` und **beide** melden «Modellname darf nicht leer sein». `DEFAULT_MODEL`
bleibt der Vorgabewert des Feldes in `RunLaunchConfig` selbst — das ist eine
Quelle für einen unbenannten Startwert und nicht die Übersetzung eines leeren
Feldes.

**Zwei Wächter, und der zweite ist der wichtigere:** Der eine prüft den
gemeldeten Fall (derselbe leere Entwurf über Preflight und Lauf, gleicher Wert
*und* gleicher Befund). Der andere prüft den **Mechanismus** — die Rundreise
`draft_to_launch_config` → `launch_config_to_draft` muss auf den LLM-Feldern ein
**Festpunkt** sein. Genau dort kann ein `or DEFAULT_…` ein leeres Feld füllen,
ohne dass es auffällt: Der Wert *sieht* danach aus wie eine Eingabe. Geprüft
werden `model` **und** `base_url`; letzteres war nur deshalb heil, weil dort nie
jemand ein `or` geschrieben hat.

**Und der Befund hatte zwei Hälften in `availability`, nicht eine.** Die
gemeldete war der Modellname; zwei Zeilen darüber stand dasselbe für die
Adresse, und das war der **schlimmere** Fall: Bei leerem Feld wurde eine
*erfundene* Adresse angepingt, und deren Antwort entschied darüber, ob «Mit
Sprachmodell» als möglich angezeigt wird. Läuft dort zufällig ein Ollama, sagte
die Oberfläche «alle drei Modi stehen zur Verfügung» für einen Lauf, der keinen
Endpunkt hat. Beide sind weg, der Import von `defaults` ist damit fort — nicht
nur unbenutzt.

**Alle vier Zusagen sind mutationsgeprüft:** Jeder der beiden Rückfälle im
Launcher und jeder der beiden in `availability` wurde wieder eingesetzt, und
jedes Mal wurde es rot.

---

### P3.14 — Der Fehlerweg braucht keinen Puffer ✅ erledigt 2026-09-05

**Fundstelle:** [`src/run_simulation.py:556`](../src/run_simulation.py) (`_schreibe`),
[`tests/test_zeichensatz.py`](../tests/test_zeichensatz.py).

**Befund.** Der Ausweichpfad nach einem `UnicodeEncodeError` schreibt über
`sys.stderr.buffer`. Gemessen an zwei Strömen, die beide `cp1252` melden: mit
`.buffer` hält er, ohne `.buffer` wirft er `AttributeError` — ein Traceback an
genau der Stelle, an der P3.3 einen weggeräumt hat. **Und der Wächter teilt die
Annahme:** Alle drei Tests des Fehlerwegs lesen ihr Ergebnis über
`strom.buffer.getvalue()`, brauchen also einen Puffer und können den pufferlosen
Fall nicht sehen. Prüfling und Prüfer haben dieselbe Voraussetzung — die
Fehlerart, die diese Phase dreimal gefunden hat, hier in ihrem eigenen Wächter.

**Ehrlich eingegrenzt.** Es braucht drei Dinge gleichzeitig: einen
`stderr`-Wrapper ohne `.buffer`, ein Sonderzeichen im Befundtext und einen
`cp1252`-Strom. Heute leitet das Projekt `stderr` **nirgends** um, und
`stdio_auf_utf8()` läuft als erste Anweisung in `_main`. Der Pfad ist die Reserve
für genau den Fall, den sie offenlässt — ein Strom, der die Umstellung
verweigert; dafür warnt sie, statt zu scheitern. Genau dort greift er, und genau
dort fällt er um.

**Fertig wenn:** `getattr(sys.stderr, "buffer", None)`, und ohne Puffer geht die
ersetzte Zeichenkette durch `write`. Dazu ein vierter Test mit einem Strom
**ohne** `.buffer` — er ist der eigentliche Gegenstand des Pakets, nicht die zwei
Zeilen Code.

**Was gilt** (2026-09-05), und es ist einfacher als das Kriterium verlangte: Es
steht **kein** `getattr(..., "buffer", None)` dort, weil der Umweg über die
Bytes von Anfang an überflüssig war. `backslashreplace` ersetzt genau die
Zeichen, die die Kodierung *nicht* kann, durch ASCII-Escapes — was übrig bleibt,
ist per Konstruktion schreibbar. Zurückdekodiert geht es deshalb durch dieselbe
`print`-Zeile wie der Normalfall, und die Abhängigkeit ist nicht abgefangen,
sondern **weg**. Ein Zeichen, das die Konsole darstellen kann (`ö`, `—`), bleibt
dabei stehen; nur das Unschreibbare wird zu seiner nachschlagbaren Escape-Folge (`U+2265` als Text, nicht `?`). Auch `sys.stderr.flush()`
ist entfallen — der Normalfall flusht ebenfalls nicht, und es war eine zweite
Attributabhängigkeit derselben Art.

**Der vierte Test ist eine Parametrisierung über beide Bauformen** (mit und ohne
`.buffer`), damit der pufferlose Fall nicht wieder der ungeprüfte ist. Drei
Mutationen geprüft: alte Fassung zurück, `errors="replace"` statt
`backslashreplace`, Ausweichpfad ganz weg — dreimal rot.

> **Und dabei kam ein dritter Befund derselben Familie heraus, in diesem Paket
> selbst.** Der bestehende Test des Ausweichpfads hat seine Zusage **nie
> geprüft**: Er ersetzte `builtins.print` durch eine Fassung, die
> cp1252-Fehler wirft, ließ `sys.stderr` aber das Auffangobjekt von `capsys` —
> und dessen `encoding` ist **utf-8**. Der Ausweichpfad kodierte also nach
> utf-8, wo `backslashreplace` nichts zu ersetzen hat; geschrieben wurde das
> echte `≥`. Durchgegangen ist er über das zweite Glied seiner eigenen
> Bedingung (`assert "u2265" in ausgabe or "≥" in ausgabe`). **Nachgemessen**,
> nicht vermutet: Der alte Pfad schrieb `'… cost_pressure ≥ 0,8 …'`, `"u2265"`
> war nicht enthalten. Er ist ersetzt, nicht repariert — die Lehre steht als
> Kommentar an seiner Stelle: *Eine Attrappe, die an einer Stelle scheitert und
> an der anderen so tut, als sei alles in Ordnung, prüft die Verbindung
> dazwischen nicht.* Und eine `or`-verknüpfte Zusage prüft im Zweifel die
> lockerere Hälfte.

---

### P3.15 — Eine Signatur, die ihrem Rumpf widerspricht ✅ erledigt 2026-09-05

**Fundstelle:** [`src/orchestration/scenario_sweeps.py:232`](../src/orchestration/scenario_sweeps.py).

**Befund**, gemessen:

| Frage | Antwort |
| --- | --- |
| Rückgabe-Annotation | `SimpleNamespace` |
| tatsächliche Rückgabe | `RunArgs` |
| Parameter | `['sweep_id']`, davon im Rumpf benutzt: **keiner** |
| zwei verschiedene `sweep_id` ergeben | **identische** Argumente |
| `SimpleNamespace` erscheint in | Zeile 18 (Import) und 232 (Annotation) — sonst nirgends |

Drei Dinge auf einmal: Die Annotation sagt das Gegenteil des Rumpfs (P3.11 hat
den Rumpf umgestellt, die Signatur nicht); der Parameter wird ignoriert, seit
sein einziger Verwender `sweep=sweep_id` entfallen ist; und die falsche
Annotation hält den Import am Leben, weshalb `ruff` schweigt — **`ruff check .`
ist grün.**

**Warum es mehr ist als Kosmetik.** Invariante 4 verlangt Pydantic-Typisierung an
den Grenzen; ihre Durchsetzung hängt daran, dass die Typangabe stimmt. Hier sagt
sie einem Leser und jedem Werkzeug, es käme ein formloser Namensraum heraus — die
genaue Aussage, gegen die P3.11 angetreten ist. **Strukturelle Ursache: Das
Projekt hat keinen Typprüfer** (weder mypy noch pyright in `pyproject.toml` oder
der CI), und `ruff` prüft Annotationen nicht gegen `return`.

Der unbenutzte Parameter ist die schwächere Hälfte — es gibt im selben Zweig eine
Stelle, an der ein unbenutzter Parameter **richtig** ist: `model_editor.layout`
behält ihn bewusst und sagt im Docstring, warum. Hier steht kein solcher Satz,
und die Aufrufer übergeben eine Kennung in der Annahme, sie werde verwendet.

**Fertig wenn:** `-> RunArgs`, Import weg, und `sweep_id` benutzt oder
entfernt — mit einem Satz, welches von beidem gemeint ist. **Und die Klasse
getrennt davon:** ein Typprüfer über `src/models/` und die Grenzen, als eigenes
Paket in Phase 4. Die drei Zeilen zu reparieren behebt den Fall; ohne Prüfer ist
die nächste falsche Annotation genauso unsichtbar.

**Was gilt** (2026-09-05): `-> RunArgs`, der Import ist weg, und **`sweep_id` ist
entfernt** — nicht bewusst behalten. Der Unterschied zu
`model_editor.layout(draft)`, wo ein unbenutzter Parameter richtig ist: Dort
hielt ihn ein Aufrufer, dessen Zeile nicht zweimal geändert werden sollte. Hier
gab es sieben Aufrufstellen und keinen Grund; ein Parameter, der das Ergebnis
nicht ändern kann, ist dieselbe Lüge wie die Annotation, nur eine Klammer weiter.
Die Zugehörigkeit eines Laufs zu seinem Sweep steht im Ablageort und im
Rahmenszenario; wer sie im Artefakt will, gibt `RunArgs` ein Feld — `extra="forbid"`
erzwingt dann die bewusste Entscheidung.

**Der Wächter sucht die Erzeuger, statt sie aufzuzählen**
(`tests/test_lauf_argumente.py::TestJedeSignaturSagtWasSieLiefert`): ein
AST-Durchlauf über `src/` und `dashboard/` nach **jedem** `return`, das ein
`RunArgs` baut oder weitergibt — heute drei —, und dann muss die Signatur es
sagen. Dazu eine Messung statt einer Lektüre (`type(sweep_metadata_args()) is
RunArgs`) und die Zusage über den wirkungslosen Parameter. **Vier Mutationen
geprüft, viermal rot** — darunter eine Lüge an einem *zweiten* Erzeuger
(`build_run_args`), also greift er nicht nur an der gemeldeten Stelle.

**Nachtrag vom 2026-09-08 (aus P4.2): eine dieser vier Zusagen war selbst eine
Aufzählung.** `test_kein_parameter_ohne_wirkung` prüfte
`not signature().parameters` — also «gar kein Parameter». Sein eigener Docstring
sagte etwas anderes («nicht *der Parameter ist weg*, sondern … kein Argument, das
etwas ändern könnte»), und die Abkürzung stimmte nur, solange es keinen gab. Als
P4.2 `sweep_metadata_args` einen Parameter gab, **der wirkt**
(`llm_narrative` entscheidet über `compute_mode`), ging der Wächter rot — formal
richtig, sachlich falsch. Seine eigene Fehlermeldung nannte bereits die Auflösung:
«Wenn er wirkt, gehört ein Test daneben, der es zeigt.» Er legt jetzt jeden
booleschen Parameter um und verlangt, dass sich das Ergebnis ändert; ein
Parameter, für den sich keine Probe bilden lässt, macht ihn ebenfalls rot.
**Zwei Mutationen geprüft, zweimal rot** (Parameter wirkungslos gemacht; Schalter
im Rumpf zurückgenommen). **Dieselbe Lehre wie bei P3.8 und den
Kontextparametern:** Ein Wächter, der den heutigen Zustand *aufzählt*, meldet den
nächsten Fall auch dann, wenn er in Ordnung ist — und das ist teurer als es
aussieht, weil eine falsche Meldung dazu erzieht, den Wächter zu umgehen.

**Die Klasse blieb offen und bekam ein Paket, erledigt am 2026-09-11:**
[P4.4](#p44--ein-typprüfer-für-die-grenzen--erledigt-2026-09-11-neu-2026-09-05-aus-p315). Dieser
Wächter deckt **eine Familie** ab, weil genau die einen Schaden angerichtet hat;
für jede andere Grenze gilt die Lücke weiter. Zwölf Tage lang war `ruff check .`
grün, während die Annotation log — weil sie den Import am Leben hielt, den `ruff`
sonst gemeldet hätte.

---

### P3.16 — Das 500-ms-Kriterium und sein Deckel ✅ erledigt 2026-09-05

**Fundstelle:** [`tests/test_web_overflow.py:1732`](../tests/test_web_overflow.py)
(`SICHTBAR_MAX_MS`) und die Abnahmeklausel von
[P3.9](#p39--ein-klick-in-der-schrittfolge-kostet-zwei-sekunden--erledigt-2026-09-05-ursache-zweimal-korrigiert).

**Befund.** Die Klausel lautet «ein Klick kostet **unter 500 ms**, gemessen im
Browser über alle sechs Schritte — und die Zahl der Server-Aufrufe steht als Zahl
im Wächter». Die zweite Hälfte ist erfüllt (`KLICK_AUFRUFE_MAX = 7`, Sperrklinke
in beide Richtungen). Die erste ist **gemessen** erfüllt — 213 bis 487 ms — aber
der Wächter deckelt bei **900**, also fast dem Doppelten. Ein Rückfall auf 800 ms
bliebe grün, während der Plan das Kriterium als erfüllt führt.

**Die Begründung für 900 trägt** und steht im Code: Eine ausgelastete Maschine
misst anders, und dieser Wächter wird sonst rot, ohne dass sich etwas geändert
hat (bei drei parallelen Läufen brauchte er einmal 1:56 h — beim Schreiben dieses
Audits ist derselbe Effekt erneut aufgetreten). Was nicht trägt, ist die
Kombination aus dieser Grenze und einem ✅, das auf einer Einzelmessung steht.
Die Doku-Pflicht sagt es selbst: *wer eine Zusage aufstellt, baut den Wächter,
der sie misst — nicht die Zählung, die sie umgeht.*

**Zu entscheiden ist eines von beidem, nicht beides:**

* **(a)** Deckel auf 500, mit benannter Toleranz und einer Wiederholung bei Rot.
  Ehrlich gegenüber dem Kriterium, aber es verlagert das Problem: Ein Wächter,
  der auf einer belegten Maschine flackert, wird nicht mehr gelaufen — und
  genau daran ist C5 des Phase-2-Audits gestorben.
* **(b)** Im Plan festhalten, dass das Kriterium **einmal** erreicht wurde und
  die Sperrklinke bei 900 steht. Billiger, und es sagt die Wahrheit über den
  Schutzumfang.

**Empfehlung: (b).** Dazu gehört der veraltete Docstring an
`test_the_step_shows_up_in_reasonable_time` (er nennt noch 665–1426, die Zahlen
von vor P3.12) — in denselben Commit.

**Entschieden wurde (a) — mit einem Mittel, das die Empfehlung nicht kannte**
(2026-09-05). Der Einwand gegen (a) war richtig: Ein Wächter, der auf einer
belegten Maschine flackert, wird nicht mehr gelaufen. Nur folgt daraus nicht,
den **Maßstab** zu lockern, sondern das **Rauschen aus der Messung** zu nehmen.

**Was gilt:** `SICHTBAR_MAX_MS = 500` — die Zusage im Wortlaut. Gemessen wird
jeder Schritt **dreimal**, gewertet die **schnellste** Messung
(`MESSUNGEN_JE_SCHRITT`): Last kann eine Messung nur langsamer machen, nie
schneller, also schätzt das Minimum, was der *Code* kostet. Eine Regression
macht umgekehrt jede Messung langsam, auch die beste. Durchgelassen wird
`SICHTBAR_DECKEL_MS` = 500 + **10 % benannte Toleranz** = 550.

**Warum überhaupt noch eine Toleranz** — und das ist gemessen, nicht
vorsichtshalber: Zwei Durchgänge an derselben Codefassung, beide mit dem Minimum
aus drei Messungen, lieferten für «Prüfen & Starten» bei 1024 px **507** und
**476 ms**. Dieser Schritt liegt *auf* der Linie; ein Deckel von exakt 500 wäre
in jedem zweiten Lauf rot, ohne dass sich etwas geändert hat. Der Unterschied zu
den 900 von vorher ist trotzdem der Punkt: 900 war das **1,8-fache** der Zusage
und hätte genau die Regression durchgelassen, die P3.12 behoben hat.

**Zwischenstation, weil sie zum Ergebnis gehört:** Der erste Anlauf setzte 500
scharf und trug für Schritt 6 eine benannte Ausnahme (520 ms) nach dem Muster der
Einstiege in `test_zeichensatz.py`. Der zweite Durchgang misst 476 — und die
**Sperrklinke gegen verfallene Ausnahmen**, die derselbe Commit eingebaut hatte,
hat sie sofort als überholt gemeldet. Die Ausnahme ist deshalb wieder weg: Sie
hätte über dem Ist-Stand geschwebt, und genau das ist der Zustand, gegen den
dieses Paket antritt.

**Die Regression wird nachweislich weiter gefunden.** Mutationsprobe mit dem
echten Vor-P3.12-Zustand (`rumpf_fuer` liefert den Rumpf unabhängig vom Pfad):
**rot an beiden Breiten**, gemessen 606 bis 1489 ms — der Deckel von 550 hat
also Reserve nach beiden Seiten.

> **Und die erste Mutation war untauglich, was einen eigenen Merksatz wert ist.**
> Naheliegend war, `layout()` wieder eifrig zu füllen (`html.Div(body(draft), id=HOST)`) —
> genau die Mutation, mit der das Audit P3.12 geprüft hat. Sie ist **grün**
> geblieben: Der Routing-Callback `_model_editor` läuft unmittelbar nach dem
> ersten Zeichnen und **leert** den Wirt wieder, weil `rumpf_fuer` bei fremdem
> Pfad `[]` liefert. Für die *strukturelle* Zusage aus P3.12 ist diese Mutation
> richtig; für die *Kosten* reproduziert sie nichts. **Eine Mutation prüft, was
> sie ändert — nicht, was sie zu ändern vorgibt.**

**Der veraltete Docstring ist mit erledigt** (C3): Der Test heißt jetzt
`test_the_step_shows_up_within_the_agreed_budget` und nennt die Zahlen, die
gelten. **Und er kann nicht mehr aus dem falschen Grund grün werden:** Bleibt die
Mutationsmarke aus, ist `sichtbar_ms` gleich `None`; vorher wurden solche
Schritte übersprungen, und ein Durchlauf ohne eine einzige Messung galt als
bestanden. Der Test verlangt jetzt Messungen für jeden Schritt.

**Der Preis:** Die Klickmessung braucht 3:52 statt rund 1:20, der ganze
Browser-Wächter damit **28:05** statt 22:17 — nachgemessen am 2026-09-06, und
zwar mit einem parallel laufenden `pytest` daneben, also am oberen Rand.

---

### P3.17 — Der Browser-Wächter ist rot, und niemand läuft ihn ✅ erledigt 2026-09-06

**Nicht aus Phase 3** — auf `main` (`af71a3f`) in einem eigenen Arbeitsbaum
identisch nachgemessen, mit Prüfung über `__file__`, dass wirklich der
`main`-Code geladen war. Gefunden hat es das [Audit der Phase 3](#audit-der-phase-3-2026-09-05--fünf-pakete-der-schwere-befund-ist-vorbestehend),
und es ist dessen einziger schwerer Befund.

**Der Stand:** `tests/test_web_overflow.py` — **112 bestanden, 6 gescheitert** in
22:17.

| Test | Gemessen | Deckel |
| --- | --- | --- |
| `test_no_step_grew_beyond_its_ratchet` `[1280px]` | Schritt 1: **1,96** Schirme · Schritt 6: 1,70 | 1,34 · 1,45 |
| `test_no_step_grew_beyond_its_ratchet` `[1024px]` | Schritt 1: **2,03** Schirme · Schritt 6: 1,61 | 1,42 · 1,45 |
| `test_no_line_runs_longer_than_the_eye_can_follow` | **109** Zeichen in einem `LI` («docs/research/links.md — EU-ETS / Fit fo…»), **98** in einem `P` auf «Prüfen & Starten» («bei Tick 16. Danach hält er seinen letzt…») | 75 |
| `test_the_width_guard_would_notice_a_relapse` (×2) | scheitert an der **Vorbedingung** — er kann keinen Rückfall nachstellen, solange der Ist-Stand außerhalb liegt | — |

**Warum das mehr ist als ein rotes Feld.** Das Audit der Phase 2 hat genau diese
sechs als **C5** geführt, mit ⛔ bewertet und **noch am 2026-09-03 behoben** — der
Deckel steht seither auf nachgemessenen Werten, für Schritt 1 auf **1,34**;
`docs/audit_findings.md` führt C5 deshalb nicht mehr. Heute misst derselbe
Schritt **1,96**.

**Und die Ursachen sind neue.** C5s Zeilenbefund waren 89 Zeichen im Erklärtext
des `apply_custom_overrides`-Schalters. Die 109 Zeichen von heute stehen in einem
**Quellenverzeichnis**, die 98 in einem Satz über einen **Verlauf, der vor dem
Laufende aufhört** — beides Oberfläche, die am **selben 2026-09-03** dazukam: die
Kohärenzbegründungen mit ihren Quellen (P2.2/P2.10) und der Hinweis auf die
Horizontlücken. Der Fix wurde gemessen und **von späteren Commits desselben Tages
ungültig gemacht**; den 22-Minuten-Wächter hat danach niemand mehr gestartet.

**Damit ist C5s eigentlicher Befund zum zweiten Mal eingetreten** — und der
lautete nicht «der Deckel stimmt nicht», sondern: *Der Wächter ist opt-in,
überspringt sich schweigend, und die CI hat keinen Browser; die Zusagen sind
ungeprüft, ohne dass etwas rot wird.* Innerhalb einer Woche, am selben Wächter,
mit anderen Ursachen. **Wer nur die Deckel nachmisst, behebt den Fall und nicht
das Muster.**

**Zwei Teile, und der zweite ist der wichtigere:**

1. **Die vier Fehlschläge nachmessen und zuordnen.** Bei Schritt 6 ist die
   Laufhistorie in `outputs/` herauszurechnen — sie trägt 0,09 Schirme und ist ein
   eigener, schon erfasster Befund (der Deckel ist nicht zwischen Rechnern
   vergleichbar). Bei Schritt 1 ist der Zuwachs von 1,34 auf 1,96 zu erklären,
   bevor eine Zahl in `DECKEL` geht: Ein Deckel, der einen unerklärten Zuwachs
   festschreibt, ist wieder aus dem falschen Grund grün. Die beiden langen Zeilen
   brauchen ein Lesemaß an der Stelle, an der sie entstehen — nicht am Text.
2. **Entscheiden, wo dieser Wächter läuft.** Solange die Antwort «wer die
   Oberfläche anfasst, lässt ihn einmal laufen» lautet, ist sie zweimal
   widerlegt. Denkbar: ein eigener CI-Job mit Browser (nächtlich oder auf
   Anforderung, nicht in der Hauptstrecke — 22 Minuten), oder die gemessenen
   Zahlen als Pflichtangabe in der Commit-Message jeder Änderung an
   `dashboard/web/`. **Die Entscheidung gehört an Phase 4** (Testfundament) und
   ist dort der Anschluss an P4.2; hier steht sie, weil dieses Audit sie
   ausgelöst hat.

**Fertig wenn:** Der Wächter ist grün, jede geänderte Zahl in `DECKEL` trägt ihre
Begründung, und im Plan steht ein Satz darüber, **wo** er läuft — nicht, dass er
laufen sollte.

---

**Was gilt (2026-09-06).** Beide Teile sind umgesetzt, und der zweite ist der
wichtigere.

**Der Wächter ist grün: 118 bestanden, 0 gescheitert** in 28:05 — zum ersten Mal
seit dem 2026-08-30, also nach sieben Tagen. Die Zahl 118 ist dieselbe wie zuvor
(112 + 6); es sind keine Zusagen weggefallen, sie halten jetzt alle.

#### Teil 1 — die vier Fehlschläge, zugeordnet statt weggedeckelt

**Die beiden Zeilenlängen waren keine Textfrage, sondern ein zweites Lesemaß.**
Die 109 Zeichen standen in der Quellenliste der Kohärenzbegründung, die 98 im
Hinweis auf Verläufe, die vor dem Laufende aufhören. Beim Beheben kam der
eigentliche Befund heraus: **`ui.alert` hatte überhaupt kein Lesemaß** — jeder
Hinweis dieser Anwendung lief so weit wie seine Zone —, und `HINT` ebenso, was
die Verfügbarkeitsanzeige mit **106 Zeichen** auffliegen ließ (die Fehlermeldung
eines fremden Dienstes ist die längste Zeichenkette, die dort ankommen kann).
Beides ist an der **Komponente** behoben und nicht an der Aufrufstelle, aus
demselben Grund wie bei `ui.explainer` am 2026-09-03.

**Und dahinter lagen zwei konkurrierende Maße für dieselbe Regel.** Fünf Stellen
trugen Tailwinds `max-w-prose` — **65ch**, gemessen **88 Zeichen**, also 13 über
der Zusage; das Projekt hat für genau diese Zusage aber ein eigenes, daran
geeichtes Maß (`.af-mass { max-width: 53ch }`). Weil `max-w-prose` *aussah* wie
ein Lesemaß, hat niemand es nachgemessen. Dieselbe Klasse wie P2.11 und wie das
Farbfundament: **zwei Quellen für einen Wert, von denen nur eine stimmt.** Alle
fünf sind ersetzt, und `tests/test_web_theme.py` hält es fest — als **statischer**
AST-Durchlauf, damit die Prüfung in jeder CI läuft und nicht im opt-in-Wächter
liegt, dessen Ausfall der Anlass dieses Pakets ist.

**Die beiden Höhen sind eingetragen, nicht gesenkt** — und ihr Zuwachs ist
git-belegt zugeordnet. Nach der Messung von 1,34 haben genau zwei Commits in
diesen Rumpf geschrieben, beide ohne den Deckel mitzuziehen: `4a5417d` (A1) zeigt
die Kohärenzbegründung auch für die Standard-Ausgangslage, `976395d` (P2.8-Rest)
den Horizontlücken-Hinweis. Dazu 0,06 aus diesem Paket selbst, weil das Lesemaß
früher umbricht. Beide Zuwächse sind **gewollt**, also verlangt der Vertrag des
Wächters genau das: die neue Zahl eintragen und die Begründung dazu.

| | vorher | jetzt | wovon |
| --- | ---: | ---: | --- |
| Schritt 1, 1280 px | 1,34 | **2,02** | A1 (Kohärenzblock), P2.8-Rest, Lesemaß |
| Schritt 1, 1024 px | 1,42 | **2,10** | dieselben, schmaler bricht mehr um |
| Schritt 6, beide | 1,45 | **1,73** | Horizonthinweis, Lesemaß, **0,09 Laufhistorie** |

**Bei Schritt 6 ist die Laufhistorie eine Entscheidung**, nicht ein Restfehler:
Der Schritt zeigt eine Laufzeitschätzung, sobald vergleichbare Läufe in
`outputs/` liegen — gemessen 1,61 in einem frischen Arbeitsbaum gegen 1,70 mit
264 Läufen, an derselben Codefassung. Der Deckel gilt für den **bestückten** Fall;
wer frisch klont, misst niedriger, und die Sperrklinke gegen stilles Schrumpfen
lässt 0,25 zu. Die Alternative — die Schätzung aus der Messung herausnehmen —
hätte den Wächter für genau den Teil blind gemacht, den ein Nutzer im Alltag
sieht.

**Zwei Schirme sind kein guter Zustand**, und die Zahl steht als Ist-Stand da,
nicht als Freigabe. Ob die Kohärenzbegründung offen stehen muss oder ihre Quellen
genügen, ist eine **Produktfrage** — A1 hat sie bewusst offen gestellt, weil sie
unter Variante C die einzige Absicherung eines Rahmens ist. Sie gehört in ein
eigenes Paket und nicht in einen Wächter.

#### Teil 2 — wo der Wächter läuft

**Ein eigener Workflow:** [`.github/workflows/browser.yml`](../.github/workflows/browser.yml).
Drei Auslöser, und der mittlere ist der tragende:

* **`workflow_dispatch`** — von Hand, wann immer jemand die Zahlen sehen will.
* **`pull_request` mit Pfadfilter** auf `dashboard/web/**`,
  `aeroforesight-ai-landing-page/**` und die Datei des Wächters selbst.
* **nächtlich** als Netz für alles, was der Filter nicht sieht.

**Der Pfadfilter ist nachgezählt und nicht geraten:** Alle drei Rückfälle, die
diese Geschichte hat — P2.0-C, A1 und P2.8-Rest — haben `dashboard/web/**`
angefasst. Der Filter hätte also **jeden einzelnen** erwischt, ohne dass jemand
daran denken muss, und ohne die 25 Minuten in die Hauptstrecke zu hängen, wo sie
jeden Commit aufhielten.

**Warum das Netz trotzdem gebraucht wird:** Oberflächentext kann aus `src/`
kommen. Eine längere Validierungsmeldung landet in einem Hinweis, und Fall 3
berührte `src/orchestration/` mit — er wäre über den Filter erwischt worden, der
nächste vielleicht nicht.

**Zwei Dinge sind im Job ausdrücklich abgesichert**, weil sonst die Antwort auf
dieses Paket dasselbe Problem hätte wie der Zustand davor: `playwright install
--with-deps` holt die Systembibliotheken mit (ohne sie startet Chromium nicht,
der Wächter **überspringt sich** und der Job wäre grün, ohne etwas geprüft zu
haben), und `-ra` zeigt jeden Skip mit Grund.

**Ein Vorbehalt, offen benannt:** Die Deckel in `DECKEL` und die Klickdauern sind
unter **Windows** erhoben. Chromium rechnet sein Layout selbst und die Schriften
liegen im Repo, die Zahlen sollten also übertragbar sein — **geprüft ist das
nicht**, weil der erste Linux-Lauf einen Push braucht. Weicht er ab, ist die
Antwort ein Deckel **je Plattform** und nicht ein gelockerter für beide; der
Grund gehört dann in `DECKEL`. Das steht auch im Workflow, damit es der erste
Leser dort findet.

**Die Lehre, weil sie über das Paket hinausgeht:** *Eine Zusage, die von der
Sorgfalt des Einzelnen abhängt, ist keine.* Der Wächter war nie kaputt — er wurde
nicht gelaufen, dreimal in sechs Tagen, und jedes Mal hat es Tage gekostet, das
zu merken. Was ihn scharf macht, ist nicht ein besserer Test, sondern ein
Auslöser, an den niemand denken muss.

---

## Phase 4 — Testfundament

Über 500 Tests sind eine gute Grundlage, aber die Suite hat drei Eigenschaften, die beim Ausbau bremsen. (Die Zahl stand hier bis 2026-08-26 als "267" und in `CLAUDE.md` als "~330"; `pytest --collect-only` sammelt tatsächlich 506. Genau diese Drift ist der Anlass für P4.3.)

### P3.12 — Der Modell-Bereich lag dauernd im DOM ✅ erledigt 2026-09-05

> **Aus [P3.9](#p39--ein-klick-in-der-schrittfolge-kostet-zwei-sekunden--erledigt-2026-09-05-ursache-zweimal-korrigiert), und mit einer korrigierten Ursache.** P3.9 hatte richtig gemessen, dass die Wartezeit nicht in den Server-Rundläufen liegt — und daraus falsch geschlossen, sie liege im React-Vergleich des Baums aller fünf Bereiche und hänge damit an Regel 1 und Regel 6. Das CPU-Profil sagt etwas anderes.

**Befund:** Ein Klick in der Einrichten-Schrittfolge kostet rund eine Sekunde, und die Zeit liegt in **Dashs eigenem JavaScript**:

| Anteil | Zeit | Wo |
| ---: | ---: | --- |
| **71,6 %** | **1218 ms** | `dash_renderer` |
| 10,5 % | 179 ms | React-DOM |
| — | — | Plotly kommt gar nicht vor |

Darin `notifyNestedSubs`: Redux benachrichtigt bei **jeder** Callback-Antwort alle angeschlossenen Komponenten. Die Kosten hängen an deren **Zahl**, nicht an der Größe des sichtbaren Bereichs. Und der Modell-Bereich stellt **mehr als die Hälfte** aller Knoten (1886 von 3364, darunter 146 Bedienelemente — nachgemessen am 2026-09-06, Methode im Docstring von `model_editor.HOST`) — auch während jemand in der Schrittfolge arbeitete und ihn nie zu Gesicht bekam. **Die Zahlen standen hier bis zum 2026-09-06 als «168 Bedienelemente, 1404 der 2882 Knoten», und keine davon reproduzierte** (C1 des Audits): Sie stammten aus verschiedenen Messungen — 2882 − 1404 ergibt 1478 und nicht 1477, und daran fiel es auf. Die 168 beschreiben zudem die beiden Assistenten-Schritte **vor** P1.9-W3.1, nicht diesen Bereich.

**Fundstellen:** [`dashboard/web/pages/model_editor.py`](../dashboard/web/pages/model_editor.py) (`layout` baute den Rumpf eifrig), [`dashboard/web/config_editor/__init__.py`](../dashboard/web/config_editor/__init__.py) (`_model_editor` hing nur an `cfg-editor-refresh`).

**Umgesetzt am 2026-09-05.** Der Rumpf entsteht beim Aufsuchen und verschwindet beim Verlassen; `_model_editor` hört dafür zusätzlich auf den Pfad. Die Entscheidung selbst ist eine reine Funktion (`model_editor.rumpf_fuer`) — dieselbe Begründung wie bei `shell.active_route`: So ist sie ohne laufende App prüfbar, und der Callback bleibt eine Verdrahtung. Ein umhüllter Dash-Callback lässt sich von außen nicht aufrufen, und eine Entscheidung, die nur im Browser prüfbar ist, wird seltener geprüft.

| | vorher | nachher |
| --- | ---: | ---: |
| bis der Schritt im DOM steht | 665–1426 ms | **213–487 ms** |
| längste Browser-Aufgabe | 1144 ms | **271 ms** |
| `dash_renderer` im Profil | 1218 ms | **252 ms** |
| DOM-Knoten in der Schrittfolge | 3364 | **1477** |

**Damit ist das 500-ms-Kriterium von P3.9 erfüllt — ohne Regel 1 oder Regel 6 zu ändern.** Das ist der Kern dieses Pakets: Der Gewinn liegt gemessen zu rund 80 % in **einem** Bereich, und die beiden Regeln bleiben, wie sie sind.

**Warum das Weglassen hier erlaubt ist, obwohl Regel 6 es verbietet:** Weil der Rumpf **keine einzige feste ID** trägt. Alle neun Kennungen darin sind Muster (`cfg`, `cfg-bool`, `cfg-rule`, …), und ein Muster-Eingang mit `ALL` verträgt null Treffer von Haus aus. Regel 6 richtet sich gegen einen *fehlenden festen* `Input` — den gibt es hier nicht. Gemessen, nicht vermutet, und von `TestRegel6IstNichtBeruehrt` festgehalten: Wer dort eine feste ID einbaut, an der ein Callback hängt, erfährt es aus einem Test statt aus einer stillen Oberfläche.

**Zwei Wächter wären dabei lautlos hohl geworden**, und das ist der lehrreiche Teil: `test_web_wizard.py` prüft mit `_fields(model_editor.layout(draft))` die Regel 1 (kein Feld zweimal) und die Reichweite jeder schreibenden Schaltfläche (Regel 7). Mit leerem Rahmen verglichen sie eine **leere Menge** — der Regel-1-Test wäre für immer grün gewesen, ohne rot zu werden. Sie holen den Rumpf jetzt über `rumpf_fuer(...)`; der Pfad dafür kommt aus `model_editor.ROUTE`, damit eine Umbenennung nicht denselben Effekt hat.

**`prevent_initial_call` ist weggefallen**, mit Grund: Wer `/app/modell` direkt öffnet, muss den Bereich sehen. Der erste Aufruf entscheidet anhand des Pfads; auf einem anderen Bereich kostet er nichts.

**Fertig, gemessen:** [`tests/test_web_lazy_modell.py`](../tests/test_web_lazy_modell.py) (sieben Zusagen ohne Browser: die Entscheidung, der leere Rahmen, keine feste ID im Rumpf, die Statuszeile als Gegenbeweis, die Adresse aus einer Quelle) plus **Teil 10** von [`tests/test_web_overflow.py`](../tests/test_web_overflow.py) für die Verdrahtung (leer in drei Bereichen, gebaut beim Aufsuchen, gebaut per Tieflink, wieder abgebaut beim Verlassen, DOM unter 2000 Knoten). **Und die Sperrklinke von Teil 9 ist mitgezogen**: `SICHTBAR_MAX_MS` fällt von 2500 auf 900 — genau dafür schlägt sie in beide Richtungen an.

**Doku ist mitgezogen:** `CLAUDE.md` (Regel 1 mit ihrer Ausnahme, Regel 6 mit ihrem Umkehrschluss, der Vermerk zu den Klickkosten).

### P3.9 — Ein Klick in der Schrittfolge kostet zwei Sekunden ✅ erledigt 2026-09-05 (Ursache zweimal korrigiert)

> **Gemeldet von Haiko am laufenden System**, nachgemessen am selben Tag. Der Befund ist nicht «Python ist langsam» — die Rechnung dauert Millisekunden. Es sind die **Rundläufe**.

**Befund:** Ein Klick auf einen Schritt der Einrichten-Schrittfolge braucht **1,1 bis 2,9 Sekunden**, bis der neue Schritt steht. Gemessen im Browser über alle sechs Schritte:

| Schritt | Dauer | Server-Aufrufe |
| --- | ---: | ---: |
| Was soll gerechnet werden? | 2,04 s | 8 |
| Wie weit reicht der Lauf? | 1,92 s | 8 |
| Womit wird gerechnet? | 2,08 s | 10 |
| Lauf & Ablage | 2,60 s | 10 |
| Technik | 1,14 s | 6 |
| Prüfen & Starten | **2,95 s** | **16** |

**Die Ursache ist eine Kette, keine langsame Stelle.** Gegengeprüft, damit das nicht geraten ist:

- **Im Leerlauf passiert nichts.** In drei Sekunden ohne Klick: **null** Aufrufe. Alle zehn gehören zum Klick.
- **Die Prüfung ist es nicht.** `validate_draft` braucht **1,3 ms**, `build_initial_state` 1,8 ms. Der Verdacht in `CLAUDE.md` («baut jedes Mal den vollen `SimulationState` auf») trifft zu, ist aber folgenlos — er kostet Millisekunden.
- **Das Zeichnen ist es auch nicht.** `content()` braucht 0,3 bis 3 ms für die Schritte 1 bis 4 und **57,6 ms** für «Technik» — den teuersten. Zusammen mit Liste und Fußleiste unter 60 ms.
- **Der Server ist es nicht.** Ein Aufruf von `/app/_dash-dependencies` dauert **14 ms**, die Landingpage 16 ms.

**Was übrig bleibt: zehn Rundläufe, die einander auslösen.** Der Klick schreibt `wizard-step-store`; das löst den Render aus, der die Slots füllt, die den Entwurf schreiben, was Status, Zusammenfassung und Laufanzeige nachzieht. **`config-draft-store.data` steht dreimal in derselben Kette.** Ein Aufruf mit 28 Byte Antwort brauchte dabei 410 ms, der letzte bei «Prüfen & Starten» **4,8 Sekunden** — er wartete auf die fünfzehn davor.

**Fundstelle:** [`dashboard/web/config_editor/wizard.py:1062`](../dashboard/web/config_editor/wizard.py) (`_render` — neun Outputs in einem Callback, das ist schon zusammengefasst), plus die Callback-Kette über `config-draft-store`, `cfg-status`, `cfg-summary`, `run-summary`/`rail-summary` und die Laufanzeige.

**Was zu tun ist — und zuerst das, was *nicht* zu tun ist:** Nicht die einzelnen Callbacks schneller machen. Sie sind schon schnell. Die Zahl der Rundläufe muss sinken.

1. **Messen, welcher Aufruf welchen auslöst.** Die Kette oben ist aus den Ausgabe-Zielen rekonstruiert; wer sie kürzt, braucht sie vollständig. Dash liefert das über `dash.callback_context`.
2. **Die dreifache Schreibung von `config-draft-store` auflösen.** Ein Store, der sich innerhalb einer Klickfolge dreimal ändert, zieht alles dreimal nach. Wahrscheinlich reicht ein Schritt-Callback, der den Entwurf **nicht** anfasst — der Schritt ist keine Einstellung.
3. **Was den Schritt nicht betrifft, hört nicht auf ihn.** Laufstatus und Laufzusammenfassung ändern sich nicht dadurch, dass jemand einen Schritt öffnet.
4. **Erst danach über Zusammenfassen nachdenken.** `_render` bündelt bereits neun Outputs; weiter zu bündeln hilft nur, wenn die Kette kürzer ist.

**Fallstrick — die Messung gehört in den Browser.** Die Python-Zeiten sagen hier nichts: Alles Gemessene lag unter 60 ms, während der Nutzer zwei Sekunden wartet. Wer diese Arbeit ohne Browsermessung macht, optimiert die falsche Stelle. `tests/test_web_overflow.py` hat als einziger Test einen echten Browser — die Zählung der Rundläufe gehört dorthin.

**Zweiter Fallstrick — der Entwicklungsserver ist nicht der Grund.** Naheliegend, aber gemessen widerlegt: Ein Aufruf kostet 14 ms. Wer das Problem auf «Flask-Devserver» schiebt, wird auf dem Hetzner-Server dieselben zehn Rundläufe haben.

**Fertig wenn:** Ein Klick auf einen Schritt kostet **unter 500 ms**, gemessen im Browser über alle sechs Schritte — und die Zahl der ausgelösten Server-Aufrufe steht als Zahl im Wächter, nicht nur die Dauer. Eine Dauer allein wäre auf einer schnelleren Maschine grün, ohne dass sich etwas geändert hätte.

**Doku zieht mit:** `CLAUDE.md` (der Vermerk zu `_live` und `validate_draft` nennt einen Grund, der gemessen nicht trägt — 1,3 ms).

---

**Nachgemessen am 2026-09-05: die Kette ist gekürzt, die Ursache war eine andere.** Das ist der eigentliche Ertrag dieses Durchgangs — die Zählung oben stimmte, der Schluss daraus nicht.

**Was jetzt gilt** (alles im Browser gemessen, wie das Paket es verlangt):

| Größe | vorher | nachher |
| --- | ---: | ---: |
| Klickbedingte Server-Aufrufe je Schritt | 8–11 | **6–7** |
| ms, bis der neue Schritt im DOM steht | 759–1799 | 665–1426 |
| Längste Browser-Aufgabe je Klick | 1230 ms | 1144 ms |

**Die Rundläufe sind gesunken, die Wartezeit nicht** — weil sie nie dort lag. Jeder einzelne Serveraufruf dauert **16 bis 115 ms**; daneben steht **eine einzelne Aufgabe im Hauptthread des Browsers von 850 bis 1150 ms** (`PerformanceObserver`, `longtask`). Der JS-Heap der Seite ist **111 MiB**: Alle fünf Bereiche des Leitstands liegen gleichzeitig im DOM (Regel 6 — bedingt Sichtbares wird ausgeblendet, nicht weggelassen), und React vergleicht bei jedem Schrittwechsel diesen Baum. Die Antworten sind dabei klein (18–31 KiB) — es ist keine Datenmenge, sondern Rechenzeit im Browser.

**Behoben ist eine echte Fehlerursache, nur nicht die vermutete:** `_sync` schrieb bei **jedem Zeichnen** einen neuen Entwurf in den Store. Der Callback feuert nicht nur beim Tippen — sobald ein Schritt gezeichnet wird, melden seine Felder ihren *unveränderten* Wert, und ein neues Dict ist für Dash eine Änderung. Damit zog ein Klick, der keine Einstellung anfasst, Preflight, Feldfehler, Tor, Zusammenfassungen und Laufübersicht nach. Jetzt gibt `_sync` `no_update` zurück, wenn der berechnete Entwurf dem gespeicherten gleicht. **Ein Vergleich, keine Ausnahmeliste** — den Schrittwechsel als Sonderfall auszunehmen wäre eine zweite Stelle, die wissen muss, was ein Schritt ist, und die nächste Ursache käme von woanders.

**Zwei Prämissen des Befundtexts oben halten nicht mehr:**

1. **«Im Leerlauf passiert nichts: null Aufrufe»** — gemessen sind es rund **zwei pro Sekunde**, seit `pages/launch.py` den Laufzustand beim Server erfragt statt ihn aus der Sitzung abzuleiten (P1.6, Regel 5). Ein Wächter, der das nicht heraussortiert, misst den Herzschlag; `TAKTGEBER` in Teil 9 tut es.
2. **«1,14 bis 2,95 s»** — reproduziert wurden 0,76 bis 1,80 s. Die alte Messung enthielt vermutlich denselben Herzschlag.

**Und die Messung selbst hatte einen Fallstrick, der hier festgehalten gehört:** Der erste Anlauf nahm die Zeit mit `wait_for_function`. Dessen Voreinstellung pollt über `requestAnimationFrame`, und das feuert in einem Tab, den niemand sieht, **gar nicht** — dieselbe Falle wie bei P1.9-W5.3. Gemessen wurden damit 2,0 s, wo 1,1 s standen. Teil 9 nimmt die Zeit über einen `MutationObserver` **in der Seite**.

**Offen bleibt die Sekunde im Browser**, und sie ist kein Parameter, sondern die Bauform: Die fünf Bereiche liegen gleichzeitig im DOM, weil ein Eingabefeld nur an einer Stelle stehen darf (Regel 1) und bedingt Sichtbares ausgeblendet statt weggelassen wird (Regel 6). Wer sie angeht, fasst diese beiden Regeln an — **nicht** weitere Callbacks. Das ist eine eigene Entscheidung und gehört nicht nebenbei getroffen; die Zahlen dafür stehen jetzt hier.

**Gehalten von Teil 9 von [`tests/test_web_overflow.py`](../tests/test_web_overflow.py)** — sechs Zusagen über beide Breiten. Die Zahl der Aufrufe ist eine **Sperrklinke** (`KLICK_AUFRUFE_MAX = 7`) und schlägt in beide Richtungen an; die Dauer steht daneben.

---

**Abgeschlossen am 2026-09-05 — und die Ursache war ein zweites Mal eine andere.** Der Absatz darüber schloss aus «die Zeit liegt in *einer* Browser-Aufgabe», sie hänge an Regel 1 und Regel 6 und sei deshalb eine Architekturentscheidung. **Auch das war eine Schlussfolgerung, keine Messung.** Ein CPU-Profil des Klicks sagt: **71,6 % in `dash_renderer`**, 10,5 % in React, Plotly gar nicht. Dessen `notifyNestedSubs` benachrichtigt bei jeder Antwort alle angeschlossenen Komponenten — die Kosten hängen an ihrer **Zahl**, nicht am Baum des sichtbaren Bereichs. Der Modell-Bereich stellte davon knapp die Hälfte, ohne je sichtbar zu sein.

[P3.12](#p312--der-modell-bereich-lag-dauernd-im-dom--erledigt-2026-09-05) hängt ihn aus. **Damit ist das Kriterium erfüllt: 213 bis 487 ms** über alle sechs Schritte, längste Browser-Aufgabe 271 ms statt 1144 — und **keine der beiden Regeln musste angefasst werden**. Die Sperrklinke ist mitgezogen (`SICHTBAR_MAX_MS` 2500 → 900).

**Die Lehre dieses Pakets ist seine eigene Fehlerkette, dreimal derselbe Fehler:** Der Plan schloss von zehn Rundläufen auf deren Zahl als Ursache. Ich schloss von «nicht die Rundläufe» auf React und die beiden Regeln. Beide Male war die Messung richtig und die *Zuschreibung* falsch — bis ein Profil sagte, welcher Code die Zeit verbraucht. **Wer eine Wartezeit erklärt, ohne sie zu profilieren, benennt die Ursache, die er erwartet.**

### P4.1 — Gemeinsame Fixtures ✅ erledigt 2026-09-11

**Befund:** Kein `tests/conftest.py`; stattdessen 32 Vorkommen von `tempfile.mkdtemp(...)` mit `try/finally: shutil.rmtree(...)` über fünf Dateien, und `class MockLLM` vierfach near-identisch definiert.
**Fundstelle:** `tests/test_checkpoint_manager.py` (2), `test_dashboard_service.py` (9), `test_figure_generator.py` (4), `test_run_scenario_generator.py` (12), `test_state_explorer.py` (5); MockLLM in `test_agent_node.py`, `test_parallel_round.py`, `test_simulation_runner_e2e.py` (die vierte Kopie lag in `debug_run_sequential.py`, gelöscht mit P4.2).
**Was zu tun ist:** `conftest.py` mit einem MockLLM-Fixture anlegen, Temp-Verzeichnisse auf das eingebaute `tmp_path` umstellen.
**Fertig wenn:** Kein Test legt mehr manuell ein Temp-Verzeichnis an; MockLLM existiert einmal. **Doku:** `README.md` (Tests-Abschnitt).

**Beim Anfassen dazugekommen (2026-09-11): fünf handgemachte Umbiegungen, zwei davon leckten.** Beim Lesen der `mkdtemp`-Blöcke fiel in `test_dashboard_service.py` ein Test auf, der `catalog.CONFIGS_DIR` auf sein Temp-Verzeichnis setzte und **am Ende des `try`-Blocks** zurückstellte — nicht im `finally`, das das Verzeichnis gleich danach löschte. Über das Merkmal gesucht (Zuweisung an ein Attribut eines importierten Namens, dazu `setattr`/`delattr`) waren es **fünf** Stellen in vier Dateien: drei stellten korrekt im `finally` zurück, **zwei nicht** — `CONFIGS_DIR` und `SWEEPS_DIR`, beide in `test_dashboard_service.py`. Eine scheiternde Zusicherung dazwischen hätte das Attribut für jeden folgenden Test der Sitzung auf ein gelöschtes Verzeichnis zeigen lassen. Alle fünf nehmen jetzt `monkeypatch.setattr`, das auch nach einem Fehlschlag zurückstellt. Umgebaut mit Gegenprüfung gegen den Stand davor: Zusicherungen und Testnamen gleich, keine String-Konstante verschwunden. Wächter: `tests/test_testfundament.py::TestKeinTestBiegtEinModulVonHandUm`, Mutationsprobe rot mit Datei und Zeile. **Das ist der eigentliche Grund, `monkeypatch` und `tmp_path` statt Handarbeit zu nehmen** — nicht die Zeilenersparnis, von der der Befund sprach, sondern die Aufräumgarantie.

**Die Temp-Verzeichnisse sind umgestellt (2026-09-11) — 39 Stellen statt der genannten 32.** In sechs Dateien standen 36 `tempfile.mkdtemp` mit `try`/`finally: shutil.rmtree` (der Befund nannte 32 in fünf; `test_figure_generator.py` trug 8 statt 4), dazu zwei `TemporaryDirectory` in `test_save_final_narrative.py` — einer Datei, die als `unittest.TestCase` gar kein `tmp_path` bekommen konnte, erst P4.2 hat das möglich gemacht — und ein `tempfile.gettempdir()` in `test_state_explorer.py`, das ein **geteiltes** Systemverzeichnis als Beleg dafür nahm, dass ein Lauf nicht existiert. Alle nehmen jetzt `tmp_path`. **Umgebaut per Skript, das jede Stelle vorher strukturell vermessen hat** (alle 36 folgten demselben Muster, null Abweichungen) und hinterher gegen den Stand davor geprüft hat: In jeder Datei sind Testnamen und Zusicherungen gleich, **verschwunden sind ausschließlich die 36 `mkdtemp`-Präfixe**, hinzugekommen ist nichts — vor und nach `black`. Zeilen innerhalb mehrzeiliger Literale sind nicht umgerückt, bestimmt über die Positionen im Syntaxbaum. Verwaiste `shutil`- und `tempfile`-Importe sind entfernt. **Ein `conftest.py` war dafür nicht nötig** — `tmp_path` und `monkeypatch` sind eingebaut; «Was zu tun ist» sah ihn als Mittel vor, «Fertig wenn» verlangt ihn nicht. Wächter: `TestEinTestLegtKeinTempVerzeichnisVonHandAn`, gesucht wird der **Import** von `tempfile` und nicht die Funktion — eine Liste der Funktionen hätte genau die Lücke, aus der er kommt. **`MockLLM` ist ein Name für ein Ding (2026-09-11) — und das Kriterium ist bewusst anders erfüllt, als «Was zu tun ist» vorsah.** Der Befund sah «vierfach near-identisch» und schlug ein gemeinsames Fixture vor. Gemessen waren es **vier verschiedene Dinge unter einem Namen**: `src.llm.studio_helpers.MockLLM` antwortet absichtlich mit `NO_OP` und ohne Ereignisse; `test_agent_node.py` hielt einen Spion mit fester Antwort, der sich den Prompt merkt; `test_simulation_runner_e2e.py` und `test_parallel_round.py` antworten je Rolle mit Zustandsänderungen und Ereignissen — mit verschiedenem Inhalt und verschieden breitem Rollenabgleich. Die vierte Kopie im Debug-Skript war zeichengleich und ist mit ihm gelöscht. **Umbenannt nach Zweck** — `FesteAntwort`, `VorschlagendeAgenten`, `SprechendeAgenten` —, je mit einem Docstring, warum es nicht der Produkt-Mock ist. Kein Inhalt geändert; geprüft gegen den Stand davor: Testnamen und Zusicherungen gleich, an Strings nur die Docstrings dazu. **«MockLLM existiert einmal» gilt damit wörtlich** — als Name im Produkt.

**Ob die Doppel gebraucht werden, ist gemessen und nicht angenommen — und die Messung hat eine meiner Begründungen widerlegt.** Alle fünf Tests aus `test_parallel_round.py` und `test_simulation_runner_e2e.py` bleiben grün, wenn man ihnen den Produkt-Mock unterschiebt. Für `test_parallel_round.py` heißt das: Die Tests zählen, wer spricht, und hängen nicht am Inhalt — der erste Docstring der Klasse behauptete das Gegenteil und ist vor dem Commit berichtigt. **Für den e2e-Test heißt es etwas Ernsteres:** Er sichert zu, dass ein vorgeschlagener Faktorwechsel nicht ungeprüft durchkommt, und bleibt ohne jeden Vorschlag grün — **leer grün**. Er prüfte nur den Endzustand, nicht, dass etwas abgewiesen wurde. **Das war ein eigener Befund und ist behoben** (2026-09-11): Der Test prüft jetzt als **Vorbedingung**, dass der Regulator F2.2 wirklich vorgeschlagen hat. Gemessen bleibt der Vorschlag in `round_results` stehen und wird erst im Environment-Node über `validate_factor_proposals` abgewiesen — erst mit ihm sagt «F2 bleibt F2.1» etwas. **Mutationsprobe:** den Produkt-Mock untergeschoben → rot mit «Der Regulator hat F2.2 gar nicht vorgeschlagen … Gefundene Vorschläge: []». Dieselbe Falle wie beim ersten Anlauf des P2.13-Wächters: grün, weil nichts geschah.

Wächter: `TestKeineTestklasseVerschattetEinenProduktnamen` — jede in `tests/` definierte Klasse, deren Name auch in `src/` definiert ist; beim Einführen traf das genau `MockLLM` von 126 Namen.

**Abgeschlossen am 2026-09-11.** «Fertig wenn» hält: Kein Test legt ein Temp-Verzeichnis von Hand an, und `MockLLM` gibt es einmal. Die README nennt die sechs Regeln für neue Tests im Abschnitt «Tests». **Bewusst nicht mitgemacht:** Drei **private** Hilfsnamen sind innerhalb von `tests/` mehrfach vergeben (`_App` viermal, `_MitschreibendeApp` und `_StummesLLM` je zweimal). Sie verschatten nichts aus dem Produkt, und ob sie Kopien derselben Sache sind, ist nicht gemessen.

### P4.2 — Suite aufräumen und verlässlich machen ✅ erledigt 2026-09-11

**Befund:** Uneinheitlicher Stil (16 Dateien funktional, drei `unittest.TestCase` ohne technischen Grund), `sys.path.append` in drei Dateien seit der Paketstruktur überflüssig, und `debug_run_sequential.py` ist gar kein Test (null `test_*`-Funktionen, wird von pytest nicht eingesammelt) — täuscht Abdeckung vor.

**Verifiziert am 2026-08-25, zwei Korrekturen am bisherigen Bild:**

1. Die beiden Sweep-Tests **hängen** ohne Ollama, sie schlagen nicht fehl — ein Lauf brach nach über sieben Minuten ohne Ergebnis ab. Das blockiert jeden vollständigen Testlauf, nicht nur zwei Zeilen im Report.
2. `test_market_rules_resolve_marginal_cost_fraction` ist **kein Code-Bug**. Der Test erwartet `0.33` (den Default aus `market_feedback.py`, bis P0.4 `market_rules.py`), `configs/properties.json` liefert `0.25`, und die Auflösung arbeitet korrekt — der Config-Wert gewinnt, wie gewollt. Zu entscheiden ist nur, welcher Grenzkostenanteil fachlich stimmt.

**Fundstelle:** `tests/test_scenario_sweeps.py:119,205`, `tests/test_market_feedback.py:94`, `tests/debug_run_sequential.py`, `tests/test_parallel_round.py`, `tests/test_simulation_runner_e2e.py`, `tests/test_agent_node.py`, `tests/test_save_final_narrative.py`.

**Ergänzung am 2026-08-26 — die CI hängt mit drin:** [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) deselektiert bereits genau diese drei Tests. Der Kommentar dort nennt `test_market_rules_resolve_marginal_cost_fraction` weiterhin "a real pre-existing bug" — also genau die Fehlbewertung, die oben korrigiert wurde. Die drei `--deselect`-Zeilen sind der eigentliche Grund, warum das Problem so lange unbemerkt blieb, und sie verschwinden mit diesem Paket.

**Was zu tun ist:** Die Ollama-abhängigen Tests per `pytest.mark.skipif` auf einen erreichbaren Endpoint überspringen (Priorität — sie kosten heute jeden vollen lokalen Lauf). Beim Grenzkostenanteil fachlich entscheiden und Test **oder** Config nachziehen. Dann die drei `--deselect`-Zeilen aus der CI entfernen. Danach auf funktionalen Stil vereinheitlichen, `sys.path.append` entfernen, Debug-Skript in ein Werkzeug umwandeln oder löschen.

**Fallstrick (2026-08-26):** `skipif` allein reicht nicht. Die Tests hängen, weil `OllamaClient` mit Backoff wiederholt — eine Erreichbarkeitsprobe ohne kurzen expliziten Timeout hängt in einem gefilterten Netz selbst und verlagert das Problem nur von der Ausführung in die Sammlung. Die Probe braucht einen harten Timeout (etwa eine Sekunde) und muss auf Modulebene zwischengespeichert werden, damit sie nicht pro Test erneut läuft.

**Fertig wenn:** `pytest` läuft ohne lokales Ollama vollständig durch und ist grün, die CI startet ohne `--deselect` — keine "bekannten Fehler" mehr in `CLAUDE.md`. **Doku:** `CLAUDE.md` (Dev-Workflow), `README.md`, `.github/workflows/tests.yml`.

---

**Stufe 1 erledigt am 2026-09-08 — und der Befund oben war zu grob.** Die CI läuft ohne einen einzigen `--deselect`; `tests/test_packaging.py::test_ci_skips_exactly_the_documented_failures` erwartet jetzt die **leere Menge**.

**Was die Messung an Punkt 1 korrigiert:** «Die beiden Sweep-Tests hängen ohne Ollama» ist die Zusammenfassung **zweier** Fälle, die sich verschieden verhalten — und nur einer davon hängt.

| Lage des Endpunkts | Ausnahme | Verhalten | wo das vorkommt |
| --- | --- | --- | --- |
| niemand lauscht | `ConnectionError` (ein `RequestException`) | `OllamaClient` bricht **sofort** ab, 5 s Verbindungstimeout | jeder CI-Runner |
| nimmt an, antwortet nicht | `ReadTimeout` | dreimal wiederholt mit Verdopplung, bis zu **870 s je Aufruf** | Entwicklungsmaschine mit Ollama, Modell nicht geladen |

Nachgemessen am 2026-09-08 liefen beide Tests hier in **14,47 s** durch und waren **grün**. Für die CI war der Deselect also nie nötig — er hat zwei Wochen lang eine Zusage stillgelegt, die dort funktioniert hätte. Die ursprüngliche Beobachtung («über sieben Minuten ohne Ergebnis») stammt aus dem zweiten Fall und ist echt; nur die *Bedingung* stand falsch im Plan.

**Der vorgesehene Weg ist verworfen, mit Grund.** Ein `pytest.mark.skipif` auf einen erreichbaren Endpunkt hätte die einzige End-zu-Ende-Zusage über den Sweep-Pfad genau dort abgeschaltet, wo sie fast immer gebraucht wird — auf jedem Rechner und jedem Runner **ohne** Ollama, also praktisch immer. Und er hätte am Thema vorbeigezielt: Keiner der beiden Tests handelt vom Sprachmodell. Ein Sweep rechnet seine Ticks deterministisch (`dummy_llm` wird nie gerufen); befragt wird das Modell an genau **einer** Stelle, dem Abschlusstext.

**Stattdessen hat der Pfad den Schalter bekommen, den er als einziger nicht hatte:** `run_single_sweep(..., llm_narrative=False)` erzeugt den Abschlusstext aus dem deterministischen Template und baut keinen Client. Gemessen **14,47 s → 6,07 s**, und der 870-s-Fall ist strukturell weg statt kürzer. **Das Artefakt zieht mit** — `sweep_metadata_args(llm_narrative=False)` liefert `compute_mode: deterministic_only` statt `deterministic_with_llm_narrative`; ein Lauf ohne Sprachmodell darf nicht wie einer mit aussehen (dieselbe Klasse wie P3.11 und P3.13).

**Der Wächter misst den Griff zum Modell, nicht die Uhr.** `TestEinSweepOhneAbschlusstextFragtNiemanden` beobachtet, ob `OllamaClient` überhaupt **gebaut** wird — eine Zeitmessung ginge auf einer langsamen Maschine grundlos rot und bliebe grün, sobald irgendwo ein Ollama antwortet, also genau dann, wenn die Zusage nicht mehr geprüft wird. Die Gegenprobe daneben ist Pflicht: Ohne sie wäre die Klasse auch grün, wenn der Sweep das Modell gar nicht mehr erreichen *könnte*. **Mutationsprobe:** Schalter zurückgenommen, Wächter rot (`test_ohne_abschlusstext_wird_kein_client_gebaut`), Laufzeit der Datei 9,44 s → 17,69 s.

**Ein Wächter musste dafür geschärft werden, und das war ein eigener Befund** (eigener Commit): `test_kein_parameter_ohne_wirkung` aus P3.15 prüfte «gar kein Parameter» statt «kein Parameter ohne Wirkung» und meldete deshalb einen Parameter, der wirkt. Siehe den Nachtrag an [P3.15](#p315--eine-signatur-die-ihrem-rumpf-widerspricht--erledigt-2026-09-05).

**`debug_run_sequential.py` ist gelöscht** (2026-09-11), nicht in ein Werkzeug umgewandelt — und die Entscheidung stützt sich auf eine Messung, nicht auf den Befund: **Das Skript lief noch** (4,3 s). Kaputt war es also nicht. Gelöscht ist es, weil es nichts trug, was nicht schon geprüft wird: Aufbau und Mock sind eine **zeichengleiche Kopie** aus `test_simulation_runner_e2e.py`, dessen Zusage «ungeprüfte Faktorwechsel eines Sprachmodells kommen nicht durch» es nur ausdruckte statt zu prüfen; es rief die private Methode `_build_sequential_runner`; und außer Plan und Audit verwies nichts darauf. Ein Werkzeug gehört nach `scripts/`, und für den Blick auf einen Lauf gibt es den Smoke-Test aus dem Dev-Workflow. **Der Wächter dazu sucht das Merkmal statt der Datei** (`tests/test_testfundament.py::TestJedeDateiInTestsWirdAuchAusgefuehrt`): jede `.py` in `tests/`, die pytest nicht einsammelt — das Einsammelmuster liest er aus der Konfiguration, statt `test_` anzunehmen.

**Die `sys.path`-Eingriffe sind entfernt** (2026-09-11). Der Befund nannte drei Stellen mit `append`; es waren zwei `append` und ein `insert` in `test_scenario_sweeps.py`, der in keiner Liste stand (die vierte Stelle lag im gelöschten Debug-Skript). **Funktional wirkungslos — und damit irreführend.** Gemessen laufen die Tests ohne die Eingriffe grün, auch aus `/tmp` gestartet: Den Pfad legt pytest selbst an, weil `tests/` ein Paket ist und der Importmodus `prepend` das erste Verzeichnis darüber ohne `__init__.py` vor den Suchpfad legt; die CI installiert das Projekt gar nicht. Die Eingriffe behaupteten also eine Abhängigkeit, die es nicht gab, und verdeckten, woher `src` wirklich kommt. **Die Begründung des Befunds hielt dabei nicht ganz:** Nicht `testpaths` bewirkt es, sondern `tests/__init__.py`. **Und `pip install -e .` trägt nichts bei** — es legt `src/` selbst in den Suchpfad, nicht sein Elternverzeichnis; das ist ein eigener Befund. Wer eine Testdatei direkt als Skript startet, bekommt seither einen `ModuleNotFoundError` — das ging nur wegen des Eingriffs. **Der Wächter geht über den Syntaxbaum** (`TestKeinTestVerbiegtDenSuchpfad`), weil eine Textsuche falsch gewesen wäre — drei der sieben Treffer für `sys.path` in `tests/` standen in Docstrings und Kommentaren. `monkeypatch.syspath_prepend` bleibt erlaubt, weil pytest es zurücknimmt.

**Der Teststil ist umgestellt** (2026-09-11): Die drei `unittest.TestCase`-Dateien sind pytest-Funktionen — **19 Tests, 66 Zusicherungen**. **Nicht per Augenmaß:** Vor und nach jeder Datei sind die Menge der Testnamen, die Zahl der Zusicherungen und die Multimenge **aller** String-Konstanten verglichen; einziger Unterschied war `'__main__'` aus der entfernten `unittest.main()`-Zeile. Zeilen im Inneren mehrzeiliger Strings sind dafür bewusst nicht umgerückt — sonst hätte sich der Wortlaut der Mock-Antworten geändert. **Der Befund nannte den Stil «rein historisch, kein funktionales Problem», und das greift zu kurz:** Einer `TestCase`-Methode reicht pytest keine Fixtures herein, `tmp_path` eingeschlossen; `test_save_final_narrative.py` benutzte `tempfile.TemporaryDirectory()` — eine Form, die P4.1 nicht mitzählte. Wächter: `TestEinTestIstEineFunktionOderEineKlasseOhneUnittest`, über den Syntaxbaum und nur für das **Erben** — `unittest.mock` bleibt ein gewöhnliches Werkzeug.

**Abgeschlossen am 2026-09-11.** Das Kriterium hält: `pytest` läuft ohne lokales Ollama vollständig durch, die CI startet ohne `--deselect`, und CLAUDE.md führt keine «bekannten Fehler» mehr. **Nicht Teil des Kriteriums und deshalb hier nicht entschieden:** ob die Wahl «Ohne Sprachmodell» im Dashboard bis zum Abschlusstext eines **Vergleichs** durchschlagen soll. `run_all_sweeps` benutzt den Schalter aus Stufe 1 bewusst nicht — das ist eine Produktfrage und keine Testfrage, und `scenario_sweeps.SZENARIOTEXT_NUTZT_LLM` beschreibt weiterhin, was auf diesem Pfad passiert (Invariante 7).

### P4.3 — Doku-Zahlen mechanisch halten ✅ erledigt 2026-09-11

**Befund (neu am 2026-08-26):** Die Doku-Pflicht steht in `CLAUDE.md`, aber nichts prüft sie — und genau die Zahlen, die Vertrauen schaffen sollen, driften still ab. Zwei Fälle allein bei dieser Gegenprobe: die Testanzahl stand an drei Orten in drei Fassungen (Projektplan 267, `CLAUDE.md` "~330", tatsächlich 506), und der CI-Kommentar behauptete Wochen nach der Korrektur weiterhin einen "real pre-existing bug". Beides sind Aussagen, die ein Fachprüfer in einer Minute widerlegt.

**Fundstelle:** `CLAUDE.md` (Abschnitte Architektur-Map und Dev-Workflow), `docs/projektplan.md` (Phase 4), `.github/workflows/tests.yml`.

**Was zu tun ist:** Einen kleinen Test ergänzen, der die in der Doku genannten überprüfbaren Zahlen gegen die Realität hält — Testanzahl, Anzahl der CIB-Zellen, Anzahl der Editor-Tabs. Wo eine Zahl nicht stabil zu halten ist, gehört sie nicht in die Doku, sondern durch eine Größenordnung ersetzt.

**Nachtrag am 2026-09-06 (aus C1 des Phase-3-Audits): drei konkrete Kandidaten, und eine Lehre dazu.** Beim Beheben von C1 ist genau die Drift eingetreten, gegen die dieses Paket antritt — und zwar innerhalb **eines Tages**:

| in der Doku | tatsächlich | Methode |
| --- | --- | --- |
| «168 Bedienelemente» im Modell-Bereich | **146** | `#model-editor-host input, select, textarea` im Browser |
| «1404 der 2882 Knoten» | **1886** von **3364** | Teilbaum des Wirts bzw. `querySelectorAll('*')` bei 1280 px |
| «46 Zeichenketten» in `src/` | **46** ✓ | Zeichenketten-Konstanten **ohne** Docstrings (alle wären 55) |

**Die Lehre ist nicht «jemand war unsorgfältig», sondern struktureller:** Zwei der drei Zahlen waren *irgendwann* richtig. Die 168 beschrieben die beiden Assistenten-Schritte **vor** P1.9-W3.1 und sind dann in eine Aussage über den heutigen Bereich gewandert; die 1404/2882 stammten aus verschiedenen Messungen und widersprachen sich um einen Knoten (2882 − 1404 = 1478 gegen die genannten 1477). Die 46 hält — weil sie jetzt ihre **Zähldefinition** mitträgt.

**Daraus folgt für die Umsetzung:** Der Test hält nicht nur die Zahl, sondern verlangt die **Methode** daneben. Eine Zahl ohne sie ist nicht prüfbar und driftet unbemerkt: Bei der «46» kamen je nach Definition 0, 46, 45, 54 oder 55 heraus, und alle fünf wären mit demselben Satz vereinbar gewesen. Die browserseitigen Zahlen gehören dabei in den Browser-Wächter (er läuft seit P3.17 nächtlich), die statischen in die Hauptsuite.

**Fertig wenn:** Eine veraltete Zahl in `CLAUDE.md` lässt die Suite rot werden.

**Doku zieht mit:** `CLAUDE.md` (Doku-Pflicht um "prüfbare Zahlen gehören in einen Test" ergänzen).

---

**Erledigt am 2026-09-11 — als Register, und es hat beim Anlegen vier veraltete Aussagen gefunden.**

**Der Befund war eine Lücke, kein einzelner Fehler.** Nur `test_packaging.py` las CLAUDE.md, und zwar auf tote Anker und Modulpfade — **keine einzige Zahl** darin wurde gehalten. Tests hielten den Code (`len(wizard.STEPS) == 6`), aber nichts band die Doku an ihn: Wer die Schrittzahl ändert und den Test nachzieht, lässt «Sechs Schritte» in CLAUDE.md still veralten.

**Was das Register beim Anlegen fand** — jede Stelle war beim Schreiben richtig und wurde von dem Commit, der sie später änderte, nicht mitgezogen:

| Aussage | geschrieben | stimmt nicht mehr seit |
| --- | --- | --- |
| «**Acht** Zahlen» im Buchungsmodell (CLAUDE.md) | `49f5aa9` (P2.1, 2026-08-30) | `e2d8ec3` (B2, 2026-09-03): `verfuegbarkeit_gewicht` kam dazu — **neun** |
| «der höchste **2,02** (1024 px: 2,10)» (CLAUDE.md) | `a5e19ef` (P3.17, 2026-09-06) | `f909470` (2026-09-07): **2,09 / 2,17** |
| «die **vier** Viewport-Bereiche» (CLAUDE.md und zweimal im Docstring von `app.visibility`) | P1.6 (2026-08-28) | `d4ecb7f` (W3.1, 2026-08-29): **fünf** |
| «Alle **drei** Viewport-Bereiche» (Modul-Docstring von `app.py`) | `62c9c4a` (P1.5, 2026-08-28) | **fünf** |

Beim Berichtigen des Modul-Docstrings kam mehr zutage als die Zahl: Er nannte nur drei der fünf Bereiche beim Namen, sagte «die anderen vier Zonen bleiben stehen» auch für «Einrichten» und «Modell», die den Bildschirm allein bekommen, und «dauerhaft im Layout» gilt seit P3.12 für den Rumpf des Modell-Bereichs nicht mehr. Alles drei steht jetzt richtig da.

**Entschieden (Haiko, 2026-09-11): ein Register im Test, keine Markierung in der Doku.** `tests/test_doku_zahlen.py` führt je Zahl die Datei, den Satz als regulären Ausdruck mit genau einer Gruppe, die Messung und die **Zähldefinition** — die Lehre aus C1. Ein umformulierter Satz fällt auf, statt still den Bezug zu verlieren. **Eine automatische Suche wäre der bessere Wächter, wenn sie ginge; sie geht nicht:** Beim Durchsehen der Stellen mit Zahl und Hauptwort ohne Messwort in der Nähe war die Mehrheit Erzählung («der acht Stellen nannte», «zwölf Tage lang») — das wären Fehlalarme, und die erziehen dazu, einen Wächter zu überlesen. **Die Lücke, die bleibt:** Eine neu geschriebene Zahl ist erst gehalten, wenn jemand sie einträgt; dafür hat die Doku-Pflicht eine Zeile bekommen.

**Die Messungen benutzen dieselbe Zählung wie der Wächter, der den Code hält, wo es einen gibt** (`_wege` aus dem Assistenten-Test, `_ids` aus dem Lazy-Test, `MAX_ENTSCHEIDUNGEN`) — eine zweite Zählung daneben wäre eine zweite Quelle. **Die «46» ist jetzt reproduzierbar definiert:** Zeichenketten-**Knoten** in `src/`, die cp1252 nicht kodieren kann, ohne Docstrings; mit Docstrings sind es 55, als verschiedene Texte gezählt 23 — gemessen am Stand nach P3.10 und heute gleich.

**Bewusst nicht gehalten:**

* **Datierte Messungen.** «nachgemessen am 2026-09-06: 1886 von 3364 Knoten» ist Geschichte, und eine Geschichte, die mitwandert, erzählt nichts mehr. Die Browser-Zahlen zum Modell-Bereich bleiben deshalb, wo sie sind (entschieden, Haiko, 2026-09-11); die Regel dahinter — keine feste ID im Rumpf — hält `test_web_lazy_modell.py`.
* **«über 500 Tests».** Eine Größenordnung, und der Satz sagt selbst, dass die genaue Zahl nicht in die Doku gehört.
* **Die Beispiele aus «Was zu tun ist»:** Die CIB-Zellen hält `test_cib_einachsigkeit.py` bereits, Editor-Tabs gibt es seit P1.7 nicht mehr.
* **Dieser Plan.** Er ist Protokoll; seine Zahlen beschreiben, was zu einem Zeitpunkt galt.

**Mutationsproben am echten CLAUDE.md**, beide Male per Prüfsumme wiederhergestellt: «Neun Zahlen» zurück auf «Acht» → rot mit «gemessen: 9» und der Zähldefinition. «Sieben Regeln gelten hier» umformuliert → **die erste Fassung brach dort mit einem `ValueError` ab**, weil das Muster auch «Diese» an die Stelle der Zahl setzte; rot war es, aber als Traceback. Jetzt ist es ein Befund: «dort, wo die Zahl stehen sollte, steht «Diese»», und ein Selbsttest hält den Fall.

**«Fertig wenn» hält:** Eine veraltete Zahl in CLAUDE.md lässt die Suite rot werden — für jede eingetragene.

---

### P4.4 — Ein Typprüfer für die Grenzen ✅ erledigt 2026-09-11 (neu 2026-09-05, aus P3.15)

**Befund.** Das Projekt hat **keinen Typprüfer** — weder mypy noch pyright, nicht in
`pyproject.toml` und nicht in der CI. `ruff` prüft Stil und Importhygiene, aber
keine Typangabe gegen ein `return`. Aufgefallen ist die Lücke an einer Stelle, an
der sie etwas gekostet hat ([P3.15](#p315--eine-signatur-die-ihrem-rumpf-widerspricht--erledigt-2026-09-05)):
`sweep_metadata_args` war mit `-> SimpleNamespace` annotiert und lieferte
`RunArgs`. Zwölf Tage lang, in einer Datei, die zweimal angefasst wurde, und
`ruff check .` war die ganze Zeit grün — die falsche Annotation hielt den Import
am Leben, den `ruff` sonst gemeldet hätte.

**Warum das mehr ist als Kosmetik.** **Invariante 4** verlangt Pydantic-Typisierung
an allen Agenten-Grenzen; ihre Durchsetzung hängt daran, dass die Typangabe
stimmt. Eine Annotation, die lügt, ist genau die Aussage «hier ist es formlos» —
gegen die die Invariante antritt.

**Was P3.15 stattdessen gebaut hat, und warum es nicht reicht:**
`tests/test_lauf_argumente.py::TestJedeSignaturSagtWasSieLiefert` sucht am
Syntaxbaum jede Funktion, deren `return` ein `RunArgs` liefert, und verlangt, dass
die Signatur es sagt. Das ist ein Mechanismus und keine Liste (nachgeprüft: eine
Lüge an einem **zweiten** Erzeuger wird gemeldet) — aber es deckt **eine Familie**
ab, weil genau die einen Schaden angerichtet hat. Für jede andere Grenze gilt die
Lücke weiter.

**Was zu tun ist — und was ausdrücklich nicht.** Nicht das ganze Repo auf
`--strict` ziehen: In `src/reporting/` und `dashboard/web/` stehen bewusst
`object`- und `Any`-Signaturen (`build_run_args` nimmt `object`, weil auch das
Dashboard hineinbaut), und ein Prüfer, der hundert Meldungen wirft, wird
abgeschaltet statt gelesen — dieselbe Mechanik, an der der Browser-Wächter
gestorben ist (P3.17). Anzufangen ist bei den **Grenzen**: `src/models/`, dazu die
Module, die `RunArgs` und `SimulationState` erzeugen oder lesen. Eine Datei- oder
Paketliste, die wächst, statt eine Zahl, die niemand erreicht.

**Fertig wenn:** Eine Annotation, die ihrem `return` widerspricht, lässt einen
Befehl rot werden, der in der CI läuft — und der Umfang steht als Liste im
Werkzeug, nicht als Vorsatz in der Doku. Der AST-Wächter aus P3.15 bleibt
daneben: Er sagt etwas Fachliches («dieser Erzeuger gehört zu `RunArgs`»), was
ein Typprüfer nicht weiß.

**Doku zieht mit:** `CLAUDE.md` (Dev-Workflow — der Befehl gehört neben `ruff`
und `black`; Invariante 4 um den Satz, wer sie durchsetzt).

---

**Stufe 1 erledigt am 2026-09-11 — der Prüfer läuft, und die Liste ist angelegt.** Gewählt ist **mypy** (entschieden, Haiko): reines Python, keine zweite Werkzeugkette. Konfiguration in `pyproject.toml` (`[tool.mypy]`), Befehl `mypy`, in der CI ein eigener Schritt.

**Der erste Lauf über die Grenzen fand 23 Meldungen in 6 Dateien.** `config_loader.py`, `metadata.py` und `provenance.py` waren sauber. **Zwei Meldungen betreffen Verhalten**, der Rest waren Angaben, die nicht sagten, was der Code tut:

| Meldung | Einordnung |
| --- | --- |
| `save_run_outputs(llm: OllamaClient)` bekommt `MockLLM` | Angabe — dieselbe Klasse wie P3.15: Die Signatur behauptete mehr, als sie braucht; jetzt `LLMCallable` |
| `herkunft: Literal[…] = GERECHNET`, die Konstante ist `str` | Angabe — `Final` |
| `reihen` und `werte` als `float` statt `float \| None` | Angabe — die fehlende Messung reist bis zum Band mit und wird erst dort gefiltert; die schon vorhandene Angabe an `reihen` war zu eng |
| `StateGraph(dict)` gegen LangGraphs eigene Typen | gewollt — **eine** begründete Ausnahme statt einer je `add_node` |
| `int(draft.seed)` mit `seed: int \| None` | Angabe — `validate_draft` fängt den Fall vorher ab (P1.9-W1.6); `cast` mit Verweis |
| `on_progress` in der inneren Klasse, `redirect_stdout(_StdoutTee())`, eine doppelte Annotation | Angaben |
| `int(festgelegt[…])` auf `object` | Angabe — `cast` |
| **`coerce_payload`: `int(ticks)`, wobei `ticks` `None` sein kann** | **Verhalten** — `{"max_ticks": 0}` stürzte mit `TypeError` ab, `{"max_ticks": "abc", "rounds": 5}` mit `ValueError`, nachgestellt. ✅ **Behoben:** Genommen wird der erste Wert, der wirklich ein `int` ist (`tests/test_langgraph_adapter.py`) |
| **`dummy_llm` in `run_single_sweep` statt eines Objekts mit `.call()`** | **Verhalten**, gemessen kleiner als vermutet — im deterministischen Modus nie gerufen; ohne ihn hätte jeder Agentenaufruf einen sichtbaren Ausfall erzeugt, aber als `AttributeError`, der die falsche Ursache nennt. ✅ **Behoben:** `KeinSprachmodell` nennt die richtige (`tests/test_scenario_sweeps.py::TestDerSweepHatKeinSprachmodell`) |

**Die beiden Verhaltensbefunde bekommen je einen eigenen Commit**, und ihre Datei kommt erst dann in die Liste — die Liste, die wächst, wie das Paket es verlangt. **Stand nach Stufe 1:** 7 Einträge, 18 Quelldateien, `mypy` grün.

**Der erste Verhaltensbefund ist behoben** (`coerce_payload`). Die Bedingung prüfte «ist irgendeiner der drei Werte ein `int`», die Auswahl nahm aber den ersten *wahrheitswerten* — mit `0` fiel sie auf `None`, mit einem ungültigen ersten Wert verdeckte er den gültigen. Einen Test, der die Funktion aufruft, gab es nicht. **Mutationsprobe:** Der alte Rumpf gegen die neuen Tests → genau die beiden Befundtests rot (`TypeError`, `ValueError`), die übrigen sechs grün, und `mypy` meldet `arg-type` an derselben Zeile. **Stand:** 8 Einträge, 19 Quelldateien, `mypy` grün.

**Der zweite Verhaltensbefund ist behoben** (`dummy_llm`), und er war **kleiner als vermutet**. Gemessen: Im deterministischen Modus ruft kein Knoten das Sprachmodell (0 Aufrufe, 0 Ausfälle — die Umgebung hält es, ruft es aber nie). Ohne den Modus rufen es alle Agenten, und **schon die alte Funktion** hätte das sichtbar gemacht: 6 Ausfälle über zwei Ticks, der Lauf `degraded` — nur jeder mit `AttributeError: 'function' object has no attribute 'call'`, einer Meldung, die die falsche Ursache nennt. `KeinSprachmodell` erfüllt das Protokoll und nennt die richtige. **Die tragende Zusage des Tests ist nicht «er wirft»**, sondern «ein Sweep ruft ihn nie»: kein Ausfall im Endzustand eines echten Sweeps — mit Gegenprobe, dass ein Aufruf dort auffiele. **Stand:** 9 Einträge, 20 Quelldateien, `mypy` grün.

**Damit ist P4.4 erledigt.** Beide Hälften des Kriteriums sind gemessen, nicht abgelesen: Eine Rückgabeangabe, die ihrem `return` widerspricht, macht `mypy` rot (Mutationsprobe oben), und `mypy` läuft als eigener Schritt in der CI — gehalten von `tests/test_packaging.py::TestDerTypprueferLaeuftUeberEineListeDieWaechst`, das auch prüft, dass die Liste nicht leer ist und jede Zeile existiert. **Bewusst nicht Teil des Pakets:** der Rest von `src/` und `dashboard/web/`. Die Liste wächst weiter; ein Ziel wie «das ganze Repo» steht nirgends, weil es die Meldungsflut wäre, vor der das Paket gewarnt hat.

**Zwei Messungen haben die Konfiguration bestimmt.** `python_version = "3.12"`, weil numpys eigene Typdateien Syntax ab 3.12 benutzen und mypy mit 3.11 dort abbrach, *bevor* er etwas prüfte. Und **kein Pydantic-Plugin**: Mit und ohne kamen dieselben 23 Meldungen heraus — was nichts beiträgt, kommt nicht ins Werkzeug.

**Mutationsprobe — die Lüge aus P3.15, an einem zweiten Erzeuger:** `build_run_args(...) -> RunArgs` auf `-> dict[str, object]` gesetzt → rot mit `return-value` an der Signatur und fünf Folgefehlern bis in `dashboard/run_launcher.py`. **Der AST-Wächter aus P3.15 bleibt daneben:** Er weiß, *welche* Funktionen `RunArgs` erzeugen; mypy weiß, ob ihre Angaben stimmen.

**Dabei aufgefallen, eigener Befund:** `LLMCallable` ist in `src/` **siebenmal** definiert, jedes Mal dasselbe Protokoll. Kein Laufzeitfehler, aber dieselbe Klasse wie `MockLLM` in P4.1 — eingeplant unter P5.1.

### P4.5 — Was ein Rahmenszenario über die Zeit behauptet ✅ erledigt 2026-09-11 (neu 2026-09-07)

> **Aus [P3.8](#p38--ein-tick-ist-ein-monat--erledigt-2026-09-07-neu-2026-08-31).**
> Solange die Tick-Dauer offen war, ließ sich über den Zeithorizont eines
> Szenarios nichts sagen. Seit dem 2026-09-07 lässt es sich, und dann steht die
> Frage sofort da.

**Befund:** Ein Tick ist ein Monat. Die vier ausgelieferten Rahmenszenarien laufen
`max_ticks: 50` — **gut vier Jahre** — und erzählen darin Folgendes:

| Rahmen | erzählt | als Monate gelesen |
| --- | --- | --- |
| Freiwillige Wende | CO₂-Abgabe 50 → 120 → 200 EUR bei Tick 1 / 8 / 20 | 200 EUR nach **20 Monaten** |
| Transformationskonflikt | 50 → 90 → 180 → 250 EUR bis Tick 25 | 250 EUR nach gut **zwei Jahren** |
| CO₂-Verzögerung | «verzögert»: 120 EUR bei Tick 25, 200 bei Tick 40 | die *späte* Variante liegt bei **3,3 Jahren** |
| Business as Usual | konstant 50 EUR über 50 Ticks | ein Ausblick über **vier Jahre** |

**Das ist keine Rate, sondern eine Aussage über die Welt** — und deshalb ist sie
in P3.8 ausdrücklich *nicht* mitentschieden worden. Jedes dieser Szenarien trägt
seit [P2.2](#p22--die-szenarienschicht-endgültig-festlegen--entschieden-2026-08-31)
eine `kohaerenz`-Begründung mit **Quellen**; diese Quellen beschreiben
Dekarbonisierungspfade, die bis 2040 laufen. Die Tick-Zahlen still zu
verzwölffachen hieße, vier Szenarien etwas anderes sagen zu lassen, ohne ihre
Begründung anzufassen — genau die Trennung «Form belegt, Wert gesetzt», auf die
das Projekt sonst besteht.

**Und es trifft das Produktversprechen.** «Strategische Zukunftsplanung» und ein
Standardlauf über 40 Ticks = gut drei Jahre passen nicht ohne Weiteres zusammen.
Weg 2 aus P3.8 (ein Tick ist ein Jahr) war genau deshalb attraktiv; gewählt wurde
Weg 1, weil zwei von drei Mechanismen und der Backtest schon Monate rechneten.
**Der Preis der Wahl ist dieser Punkt**, und er gehört benannt statt weggelassen.

**Drei Wege, wie schon bei P3.8 — jeder mit Folgekosten:**

1. **Die Rahmen auf einen realistischen Kalender strecken** (`max_ticks` auf 120
   und jede Marke mit): zehn Jahre, wie der Backtest. Kostet einen Neulauf des
   Szenario-Vergleichs, und jede Kohärenzbegründung ist gegen ihre Quellen neu zu
   lesen. Läufe von davor sind mit späteren nicht vergleichbar.
2. **Die Rahmen als das lesen, was sie sind** — kurze, dichte Wirkungsketten —
   und das Produktversprechen entsprechend fassen. Kostet nichts am Code und
   verlangt eine ehrliche Formulierung auf der Landingpage.
3. **Beides trennen:** kurze Stresstests, lange Rahmen. Der Schnitt zwischen
   `art: "rahmen"` und `art: "stresstest"` liegt bereits, er müsste nur auch für
   den Horizont gelten.

**Fundstellen:** [`configs/sweeps/`](../configs/sweeps/) (vier Dateien mit
`art: "rahmen"`), [`configs/simulation_config.json`](../configs/simulation_config.json)
(`max_ticks: 40`).

**Nicht vorziehen, ohne zu entscheiden.** Wer nur `max_ticks` hochsetzt, hat
denselben Fehler gemacht wie der, der nur eine der drei Zeitskalen anfasste: Der
Widerspruch ist verschoben, nicht aufgelöst — die Marken innerhalb des Szenarios
lägen dann relativ noch früher.

**Fertig wenn:** Jeder ausgelieferte Rahmen sagt selbst, welche Kalenderspanne er
beschreibt, und seine Kohärenzbegründung deckt sie — nachgewiesen an
`tests/test_rahmen_traegt_begruendung.py`, nicht an einer Absichtserklärung.

**Doku zieht mit:** `docs/handbuch/presets.md`, `docs/handbuch/tick-und-lauf.md`,
`docs/handbuch/grenzen.md`, bei Weg 1 zusätzlich `docs/handbuch/vergleiche.md`
(neuer Schnitt) und `CLAUDE.md` (Glossar «Rahmenszenario»).

**Erledigt am 2026-09-11 — Weg 1: gestreckt auf 120 Ticks** (entschieden, Haiko). Jede Marke ist im selben Verhältnis mitgewandert (×2,4, Tick 1 bleibt der Start): Regeln, Rampendauern, Meilensteine. **Gestreckt ist die Zeitachse, nicht die Aussage** — und das ist gemessen, nicht angenommen (fester Startwert, deterministisch, vorher gegen nachher):

| Rahmen | Meilensteine | Endlage F1–F7 | Buchungsrate, letztes Viertel | Endpreis |
| --- | --- | --- | --- | --- |
| Business as Usual | 5/5 → 5/5 | gleich | 0,387 → 0,376 | 137 → 132 |
| CO₂-Verzögerung | 5/5 → 5/5 | gleich | 0,275 → 0,316 | 113 → 97 |
| Freiwillige Wende | 7/7 → 7/7 | gleich | 0,271 → 0,298 | 107 → 100 |
| Transformationskonflikt | 8/8 → 8/8 | gleich | 0,037 → **0,004** | 239 → **437** |

**Jede Kohärenzbegründung ist gegen ihre Quellen neu gelesen**, und an drei Stellen hat das mehr geändert als eine Tick-Zahl:

- **Business as Usual wird plausibler, nicht nur länger.** Sein Kapazitätspfad (+24 %) wuchs über 40 Monate — 6,7 % im Jahr, fast das Doppelte der 3,4 % aus 2015–2019, auf die er sich beruft. Gestreckt sind es 2,7 %.
- **Freiwillige Wende und CO₂-Verzögerung verglichen ihre Marken in Ticks mit der Standard-Ausgangslage** («früher als in der Basis, Tick 8/16», «um 10 Ticks verzögert»). Das trägt nicht mehr, weil der Standard 40 Ticks läuft; die Texte nennen jetzt Jahre und die Rechtsakte.
- **Transformationskonflikt hält seine drei ungünstigen Annahmen jetzt zehn statt vier Jahre**, und das Ergebnis ist praktisch der Stillstand des Marktes. Das steht in seinem Vorbehalt; **nachjustiert ist es nicht** — ein Belastungsfall, der auf ein gefälliges Ergebnis hin eingestellt wird, prüft nichts mehr.

**Dabei aufgefallen:** Die in zwei Vorbehalten zitierten Zahlen zu `marge` (0,29 → 0,08 / 104 → 202 und 0,26 → 0,04 / 98 → 228) stammten aus P2.10 und ließen sich **schon bei 50 Ticks nicht mehr nachrechnen** (gemessen 0,37 → 0,07 / 140 → 217 und 0,37 → 0,03 / 140 → 239) — P2.12, P3.8 und P2.13 haben die Zahlen seither bewegt, die Sätze nicht. Sie tragen jetzt die neue Messung **mit Datum**, weil eine datierte Messung Geschichte ist und eine undatierte eine Behauptung über heute.

**Nicht mitentschieden:** der Standardlauf. Er bleibt bei 40 Ticks, weil seine Länge für einen einzelnen Lauf eingestellt wird und nicht Teil eines Rahmens ist; die Standard-Ausgangslage sagt das in ihrem Vorbehalt.

**Gehalten von** `tests/test_rahmen_traegt_begruendung.py::TestJederRahmenSagtSeineSpanne`: Jeder Rahmen nennt im Vorbehalt seine Länge in Ticks und in Jahren, passend zu `max_ticks`; seine letzte Marke liegt in der zweiten Hälfte des Laufs; nichts liegt hinter dem Ende. Zwei Gegenproben daneben — nur die Länge gestreckt (die Warnung dieses Pakets) und eine Spanne, die nicht zur Länge passt.

### P4.6 — Die Installation macht `src` nicht importierbar ✅ erledigt 2026-09-11 (neu 2026-09-11, aus P4.2)

> **Aus [P4.2](#p42--suite-aufräumen-und-verlässlich-machen--erledigt-2026-09-11).** Beim Entfernen der `sys.path`-Eingriffe stand als Begründung zuerst «`src` ist über `pip install -e .` importierbar». Nachgemessen stimmte das nicht — und CLAUDE.md behauptete es an anderer Stelle schon länger.

**Befund:** `pip install -e .` legt über `__editable__.aeroforesight-0.1.0.pth` das Verzeichnis `src/` **selbst** in den Suchpfad, nicht sein Elternverzeichnis. `pyproject.toml` nennt keine Pakete; setuptools erkennt ein Verzeichnis namens `src` als übliches *src-Layout* und nimmt dessen **Inhalt** als Paketwurzel. Das Paket dieses Projekts heißt aber `src`.

| Messung (2026-09-11) | Ergebnis |
| --- | --- |
| `import src` aus `/tmp` mit dem venv-Python | scheitert |
| Namen, die aus `/tmp` als Top-Level-Modul nach `src/` auflösen | **16**, darunter `models`, `llm`, `agents`, `market` |
| davon wirklich importierbar | **5**: `reporting`, `prompts`, `legacy`, `run_simulation`, `logging_setup` |
| `src.models.state_models` gegen `models.state_models`, aus dem Repo importiert | **zwei Modulobjekte, zwei `SimulationState`-Klassen** |
| Installationsschritt der CI | keiner — `pip install -r requirements.txt` |

**Warum es heute trotzdem läuft:** `src` wird nur aus dem Repo-Wurzelverzeichnis importiert — `python -m src.…` legt das Arbeitsverzeichnis in den Suchpfad — oder unter pytest, das das Wurzelverzeichnis selbst davorlegt. Die Installation trägt nichts bei.

**Warum es trotzdem ein Befund ist:** Zwei Wege zu demselben Modul erzeugen zwei Klassen gleichen Namens, und `isinstance` schlägt über diese Grenze fehl. Heute importiert niemand über den zweiten Weg; verhindert wird es von nichts. Und die Distribution `aeroforesight` beansprucht generische Namen wie `models` und `llm` im ganzen venv — jede künftige Abhängigkeit mit einem solchen Top-Level-Paket kollidiert.

**Fundstellen:** [`pyproject.toml`](../pyproject.toml) (keine `[tool.setuptools]`-Angabe), die `.pth`-Datei im venv, [`Dockerfile`](../Dockerfile), [`.claude/launch.json`](../.claude/launch.json), [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) und `browser.yml`.

**Was zu tun ist — und was vorher zu messen ist:** Die naheliegende Korrektur ist eine ausdrückliche Paketangabe, sodass `src` als Paket installiert wird. **Nicht nebenbei:** Sie ändert, was in jedem venv, im Docker-Image und in der CI importierbar ist, und die fünf heute als Top-Level-Modul importierbaren Namen verschwinden damit. Zuerst messen, ob irgendein Pfad sie so benutzt.

**Fertig wenn:** Aus einem fremden Arbeitsverzeichnis gelingt `import src` mit dem venv-Python, und **kein** Name aus `src/` löst mehr als Top-Level-Modul auf — nachgewiesen an einem Test, der beides misst, nicht an der Paketangabe.

**Doku zieht mit:** `CLAUDE.md` (Dev-Workflow), `README.md` (Quickstart), `Dockerfile`.

---

**Erledigt am 2026-09-11, am selben Tag wie der Befund.** `pyproject.toml` nennt die Pakete jetzt ausdrücklich (`[tool.setuptools.packages.find]`, `include = ["src", "src.*"]`). setuptools installiert daraufhin keine `.pth`-Zeile mit dem Verzeichnis `src/` mehr, sondern einen **Finder, der genau das Paket `src` abbildet** — dazu `src.prompts` als Namensraum, weil dort nur Vorlagen liegen.

| gemessen aus `/tmp` | vorher | nachher |
| --- | --- | --- |
| `import src` | scheitert | **gelingt** |
| Namen aus `src/`, die als Top-Level-Modul nach `src/` auflösen | 16 | **0** |
| Wege zu `SimulationState` | zwei | **einer** |
| ungewollt sichtbar (`dashboard`, `tests`, `scripts`, `langgraph_studio`) | — | **nichts** |

**Was vorher zu messen war, hat die Sorge ausgeräumt:** Kein Pfad im Repo importiert einen der Top-Level-Namen ohne `src.` — durch das Verschwinden der fünf importierbaren Namen ist nichts gebrochen. Dockerfile, CI und `.claude/launch.json` installierten das Projekt gar nicht und arbeiten vom Wurzelverzeichnis aus; LangGraph Studio legt das Wurzelverzeichnis in allen vier Skripten selbst in den Suchpfad. **Das Dockerfile bleibt deshalb unverändert** — die Paketangabe betrifft es nicht.

**Die CI installiert das Projekt jetzt selbst** (`pip install -e . --no-deps` in `tests.yml`). Vorher tat sie es gar nicht, und ein Wächter, der die Installation misst, hätte dort nichts gemessen.

**Der Wächter** (`tests/test_packaging.py::TestDieInstallationLiefertDasPaketSrc`) misst in einem Unterprozess aus einem fremden Verzeichnis und ohne `PYTHONPATH`: Das Projekt ist installiert, `import src` gelingt, und kein Name aus `src/` löst nach `src/` auf. Die Namen liest er aus dem Verzeichnis, statt sie aufzuzählen — **und stolperte dabei zuerst selbst**: In `src/` liegt ein `aeroforesight.egg-info` aus der alten Installation (von Git ignoriert), und `find_spec("aeroforesight.egg-info")` bricht ab, statt «nicht da» zu sagen. Er nimmt jetzt nur Namen, die gültige Bezeichner sind. **Die Messung ist dieselbe wie beim Befund:** vorher 16 Namen, nachher keiner.

**Dabei aufgefallen und als eigener Befund behoben:** `build_scenario_prompt` lud seine Vorlage über `Path("src/prompts/run_scenario.md")`, also relativ zum Arbeitsverzeichnis, und fiel ohne jede Meldung auf einen Einzeiler zurück («Bitte erstelle 3 Szenarien …»), wenn sie dort nicht lag — das Sprachmodell bekam eine verkümmerte Anweisung, und niemand erfuhr es. Bisher kaum erreichbar, weil `src` nur aus dem Wurzelverzeichnis importierbar war; mit P4.6 geht das von überall. **Die Vorlage wird jetzt neben dem Code gesucht** (`VORLAGE` in `prompt.py`), und **der stille Rückfall ist weg**: Eine fehlende Vorlage scheitert laut, `generate_run_scenario` fängt das ab, nimmt das Template und hält den Vorfall fest (Invariante 1). Die Suche nach Geschwistern desselben Musters in `src/` fand keine weitere Stelle. Gehalten von `tests/test_run_scenario_generator.py::TestDieVorlageKommtVonNebenDemCode`; **Mutationsprobe:** Pfad zurück auf das Arbeitsverzeichnis → rot mit `FileNotFoundError`.

---

## Phase 5 — Altlasten entfernen

Erst nach Phase 1, damit beim UI-Umbau nichts wegfällt, das noch als Referenz dient.

### P5.1 — Toter Code und irreführende Namen ✅ erledigt 2026-09-11

**Befund:** Mehrere Konstrukte, die Funktionalität vortäuschen — **neu am 2026-09-07 der schwerste davon**: `src/run_simulation.py` deklariert `--sweep` samt Hilfetext «Overrides simulation parameters with sweep settings» und **liest `args.sweep` nirgends**. Ein Aufruf mit `--sweep` rechnet stumm den Standardlauf (gemessen: vier Rahmen, viermal 116,5883 / 0,267857, `rahmen: standard` im Artefakt, Exit-Code 0). Das verstößt gegen [Invariante 7](../CLAUDE.md) — ein Startpfad, der etwas verwirft, sagt es. **Die Entscheidung gehört dazu und ist kein Fix:** Entweder die CLI bekommt den Weg wirklich, oder der Schalter wird entfernt; `scenario_sweeps` hat ihn bereits, und ein zweiter Einstieg wäre eine zweite Quelle. Weiter: `initial_ticket_price` und `active_market_rule` (keine Referenz), `run_population_sampling` ("backward-compatible entry point", nirgends aufgerufen), `speech_plan.aborted` (Feld existiert nicht), der leere `pass`-Zweig in `_format_factors` mit hartcodiertem Agenten-String, der `state._population_updates`-Pfad — ein komplettes Population-Shift-Feature mit Modellen und Unit-Tests, das der Laufzeitpfad nie erzeugt — und (neu am 2026-08-26) der Parameter `current_tick` in `run_population_tick`, der entgegengenommen und im ganzen Funktionskörper nie benutzt wird. Letzterer ist der einzige der Liste, der **nicht** entfernt werden sollte: P2.1 braucht genau ihn, um pro Tick einen eigenen Zufallsstrom abzuleiten. Dazu die irreführende Paarung `compute_ticket_price` / `compose_ticket_price`: die erste berechnet **nicht** den Kundenpreis.
**Fundstelle:** [`src/market/market_feedback.py`](../src/market/market_feedback.py) (bis P0.4 `market_rules.py`), [`src/population/population_sampler.py:558`](../src/population/population_sampler.py), [`src/agents/scheduler_node.py:123`](../src/agents/scheduler_node.py), [`src/agents/agent_node.py:258-260`](../src/agents/agent_node.py), [`src/orchestration/environment_node.py:282-283`](../src/orchestration/environment_node.py), [`src/market/simulation_functions.py`](../src/market/simulation_functions.py).
**Was zu tun ist:** Pro Konstrukt entscheiden — entfernen oder anschließen. Beim Population-Shift-Feature ist die Frage produktinhaltlich (gehört es zu P1.3?), nicht technisch. Die zwei Preisfunktionen so benennen, dass die Rolle aus dem Namen hervorgeht.
**Fertig wenn:** Kein Modul mehr, das nur von seiner eigenen Definition oder einem Test am Leben gehalten wird. **Doku:** `CLAUDE.md` (Architektur-Map), `docs/handbuch/preisbildung.md`.

**Erledigt am 2026-09-11 — und die Liste war wieder unvollständig.** Die genannten Konstrukte, jedes vorher nachgemessen:

| Konstrukt | Ergebnis |
| --- | --- |
| `--sweep` in `run_simulation` | **entfernt** (entschieden, Haiko) — scheitert jetzt laut an argparse; ein Wächter meldet jeden Schalter, den seine CLI nicht liest (`tests/test_cli_schalter.py`) |
| `initial_ticket_price`, `active_market_rule`, `run_population_sampling` | entfernt, samt zwei Registereinträgen in `test_cost_pressure_source.py` |
| `speech_plan.aborted`, der leere `pass` in `_format_factors` | entfernt — unerreichbar bzw. wirkungslos |
| `_population_updates`, `PopulationShift`, `PopulationUpdateResult` | entfernt (entschieden, Haiko) — der Rest des LLM-Umweltagenten; **gemessen lebt das Feature selbst**: die deterministischen `shift_rules` greifen im Standardlauf in 26 von 40 Ticks |
| `compute_ticket_price` / `compose_ticket_price` | die erste heißt jetzt `compute_base_cost` — sie rechnet die Kostenschicht, nicht den Kundenpreis |
| `current_tick` in `run_population_tick` | **war schon erledigt** — seit P0.4 benutzt; die Liste war hier veraltet |
| `LLMCallable` siebenmal definiert (neu aus P4.4) | einmal in `src/llm/studio_helpers.py`; ein Wächter meldet jeden doppelten Klassennamen (`tests/test_ein_name_eine_klasse.py`) |

**Das Kriterium dann gemessen, nicht die Liste abgehakt:** über alle 500 Top-Level-Namen in `src/`. Es fand **elf weitere** — sieben ohne einen einzigen Verweis (entfernt) und vier, die nur Tests am Leben hielten: `property_value_changes_at_tick` (entfernt samt Test), `festlegung_fuer` (ein Umweg um `vorgegebene_felder`, entfernt), `load_population_config` (entfernt — **und die Tests prüften eine andere Auswahlregel als der Lauf**: `agent_type` statt der ID `consumer`; sie gehen jetzt den Laufzeitweg) und `factor_permission_entry` (**bleibt**, als Schreibseite der Berechtigungs-Grammatik, mit Begründung).

**Gehalten von** `tests/test_kein_toter_code.py`: Jeder Top-Level-Name in `src/` braucht einen Verweis außerhalb von Tests; Ausnahmen stehen mit Grund im Test, und eine überflüssige Ausnahme wird gemeldet. Heuristisch über Bezeichner — dynamisch Erreichbares gehört dort eingetragen.

### P5.2 — Legacy-Streamlit abnehmen und entfernen

**Befund:** `dashboard/legacy_streamlit/` hält zwei Doppelpaare am Leben (`app.py`/`app_researcher.py`, `config_ui.py`/`config_ui_researcher.py`), die inhaltlich auseinanderlaufen — u. a. eine nur dort gepflegte längere `_render_animation` und verlorene Guillemets in der Researcher-Variante. Drei Audit-Findings betreffen ausschließlich diesen Ordner und lösen sich mit ihm auf.
**Fundstelle:** [`dashboard/legacy_streamlit/`](../dashboard/legacy_streamlit/).
**Was zu tun ist:** Nach Abschluss von Phase 1 prüfen, ob die Dash-App alles abdeckt, was der Researcher-Modus konnte — insbesondere die zusätzlichen Plotly-Charts der Legacy-Animation. Dann das Paket löschen, samt Streamlit-Abhängigkeit und `.streamlit/`.

**Tor benannt (2026-08-26):** "Nach Abschluss von Phase 1" war bisher nicht entscheidbar, weil Phase 1 nur qualitative Kriterien hatte — und solange niemand sagen kann, wann das Tor aufgeht, bleibt `streamlit>=1.32` in `pyproject.toml`, in `requirements.txt` und in jeder CI-Installation. Konkret aufzuschreiben ist deshalb **vor** dem Löschen: welche Charts aus `_render_animation` der Researcher-Variante in der Dash-App vorhanden sein müssen. Diese Liste ist das Abnahmekriterium; ist sie abgehakt, fällt das Paket, unabhängig davon, ob P1.1 und P1.2 im Übrigen schon final sind.
**Fertig wenn:** Kein Streamlit mehr im Repo und in den Abhängigkeiten. **Doku:** `CLAUDE.md`, `README.md`, `dashboard/README.md`.

### P5.3 — `src/legacy/` entscheiden ✅ erledigt 2026-09-11

**Befund:** `cib_extractor_node.py` wird ausschließlich von `tests/test_cib_matrix.py` referenziert; kein Produktionspfad importiert `src/legacy/*`.
**Fundstelle:** bis zum 2026-09-11 das Modul cib_extractor_node.py im Paket `src/legacy/` — seither entfernt, siehe unten.
**Was zu tun ist:** Bewusst entscheiden — für Experimente behalten (dann dokumentieren, wofür) oder mitsamt Test entfernen. Berührt P2.2: falls die Extraktionslogik beim Impact-Balance-Umbau nützlich ist, vorher ansehen.
**Fertig wenn:** Entscheidung getroffen und im Code sichtbar. **Doku:** `CLAUDE.md` (Architektur-Map, `src/legacy/`-Zeile).

**Erledigt am 2026-09-11 — entfernt samt Kaskade** (entschieden, Haiko). Der Extraktor leitete die CIB-Matrix per Sprachmodell aus dem Event-Log her — genau das, was Invariante 3 ausschließt —, und die Rückfrage dieses Pakets («nützlich beim Impact-Balance-Umbau?») ist mit P2.2 entfallen: Variante C baut keine Impact Balance. **Mit ihm gingen, was nur er benutzte:** `CIBMatrixHistory`, `apply_delta_constraint` und das Feld `cib_history` in `SimulationState` und `PlaygroundState`. Aus `tests/test_cib_matrix.py` fielen die fünf Testklassen zu Extraktor, Antwort-Parser, Verlauf und Delta-Beschränkung; die Modell- und Visualisierungstests bleiben. **Ältere Checkpoints laden weiter** — `SimulationState` ignoriert unbekannte Felder, und `tests/test_checkpoint_manager.py` prüft es an einem Checkpoint mit `cib_history`. Die Checkpoint-Version bleibt deshalb bei 2.

---

## Phase 6 — B2B (noch nicht Scope)

Wird erst geplant, wenn Phase 1 steht: API-Layer, Mandantentrennung, Persistenz, Auth, Billing, produktionsscharfes Hetzner-Deployment. Der heutige `Dockerfile`/`docker-compose.yml` ist ein Ausgangspunkt, kein Deployment.

**"Phase 1 steht" heißt (festgelegt am 2026-08-26):** ~~P1.1 erfüllt sein Drei-Entscheidungen-Kriterium~~ ✅ (seit 2026-08-28, mechanisch geprüft), P1.2 beantwortet drei bis fünf benannte Fragen ohne stillen Teilstand, P1.3 trennt gerechnete von erzählten Zahlen im Datenschema, und P1.4 lädt keine externen Hosts mehr. Dasselbe Tor gilt für P5.2. Ohne diese vier Haken bleibt Phase 6 ungeplant — und Streamlit im Repo.

Eine Randnotiz fürs Marketing, kein Arbeitspaket: Der 10.000-Tick-Benchmark lief mit `dummy_llm`, dem Platzhalter, der seit P4.4 `KeinSprachmodell` heißt ([`scenario_sweeps.py`](../src/orchestration/scenario_sweeps.py)). Die Zahl stimmt, misst aber die deterministische Hälfte — nicht als "unsere KI simuliert 10k Ticks" verwenden.

---

## Abdeckung des Audits

Jeder Abschnitt aus [`audit_findings.md`](audit_findings.md) ist einem Paket zugeordnet. Kein Finding bleibt ungeplant.

| Audit-Abschnitt | Pakete |
| --- | --- |
| Faktoren / Modellsubstanz | ~~P0.2 (F7-Drift)~~ ✅, P2.0 (Rolle der Szenarienschicht), P2.1, P2.2, P2.3 (die übrigen 120 Zellen — hängt an P2.2), P2.4, P2.14 (einmalige Shift-Deltas summieren sich bis an den Anschlag — neu 2026-09-11) |
| Markt / Preisbildung | ~~P0.4 (Rule-Evaluatoren, `market_rules`)~~ ✅, ~~P0.5 (Berechtigungen)~~ ✅, ~~P0.7 (Kostendruck an zwei Stellen)~~ ✅, ~~P3.1 (Property-Baseline)~~ ✅, ~~P5.1 (toter Code, Preisfunktions-Namen)~~ ✅, ~~P2.13 (F6 kippte in jedem Tick)~~ ✅ |
| Agenten / Scheduling | ~~P0.1 (Silent-Fallback)~~ ✅, P1.3 (Szenario-Schlüssel), ~~P3.5 (Klemmung, `print`)~~ ✅, ~~P5.1 (`aborted`, `_format_factors`, `_population_updates`)~~ ✅ |
| Validierung / Checkpointing / Orchestrierung | ~~P0.3 (`validate_config`, `factor_ids`)~~ ✅, ~~P0.6 (Sweep-Pfad an P0.1 vorbei)~~ ✅, P2.1 (`_seed_runtime`), ~~P3.2 (Checkpoint-Version)~~ ✅, ~~P3.3 (leerer `try`, CLI-Traceback)~~ ✅, ~~P3.11 (Lauf-Argumente ohne typisierte Form)~~ ✅, P5.1 (`--sweep` deklariert und nie gelesen), P5.1 (`round_history`-Snapshot trägt den Endzustand) |
| LLM-Anbindung | ~~P0.1 (zwei Clients)~~ ✅, ~~P3.4 (hartcodierte Defaults, stille Mock-Auswahl in `get_llm()`)~~ ✅, ~~P5.1 (`LLMCallable` siebenmal definiert — neu 2026-09-11)~~ ✅ |
| Dashboard | P1.2 (Teilstand über den Glob-Fallback, Phantom-Runs in der Auswahl), ~~P3.6 (private Imports)~~ ✅, ~~P3.9 (Klickkosten)~~ ✅, ~~P3.12 (Modell-Bereich dauernd im DOM)~~ ✅, P5.2 (Legacy-Duplikate — erledigen sich mit dem Löschen), P1.2 (leere Ergebnis-Ansicht ohne Lauf — neu 2026-09-07) |
| LangGraph Studio | ~~P3.3~~ ✅ |
| Tests | P4.1, P4.2 (inkl. der hängenden Sweep-Tests, der veralteten Erwartung in `test_market_rules_resolve_marginal_cost_fraction` und der drei `--deselect`-Zeilen in der CI) |
| Sonstiges | ~~P3.10 (Zeichensatz der Konsole)~~ ✅, ~~P5.3 (`src/legacy/`)~~ ✅, ~~P4.6 (die Installation macht `src` nicht importierbar)~~ ✅ |
| **Landingpage** (neu 2026-08-26) | P1.4 (Formular-Endpunkt, Rechtstexte, CDN-Abhängigkeiten) |
| **Reproduzierbarkeit / Run-Artefakte** (neu 2026-08-26) | ~~P0.6 (Seed, Rechenmodus, Config-Hash in `run_metadata.json`)~~ ✅ |
| **Reporting / Grounding** (neu 2026-08-26) | P2.5 (State Explorer prüft seine eigenen Zahlen nicht) |
| **Doku-Konsistenz** (neu 2026-08-26) | ~~P4.3 (Zahlen in `CLAUDE.md` mechanisch halten)~~ ✅ — der Plan selbst ist Protokoll und wird nicht gehalten |
| **Einrichten-Assistent** (neu 2026-08-28) | P1.9 (Sweep-Pfad verwirft den Entwurf, Schreibzugriff auf `configs/` aus optionalen Schritten, Schritthöhe, Fortschritts- und Validierungslücken, Barrierefreiheit) |
| **Nachfrageseite** (neu 2026-08-31) | P2.8 (kein Nachfragetreiber nach oben; Trajektorien-Horizont endet vor dem Lauf) |
| **Szenarienschicht** (neu 2026-08-29) | P2.0 (Rolle umdrehen), P2.2 (Einachsigkeit, Tripleset aus zwei Polen), P2.3 (die vier Zellen mit falschem Vorzeichen), P2.6 (keine Bandbreite), P2.7 (an nichts geeicht) |

Die vier Zeilen von 2026-08-26 stammen nicht aus `audit_findings.md`, sondern aus der
Gegenprobe jenes Tages — sie sind dort nachgetragen, damit die Detailliste vollständig
bleibt. Für die Zeile von 2026-08-29 gilt dasselbe: Der Befund kam aus der
[Leitentscheidung](#leitentscheidung-die-szenarienschicht-2026-08-29) und ist in
`audit_findings.md` ergänzt.
