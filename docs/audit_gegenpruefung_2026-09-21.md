# Befundprotokoll der Gegenprüfung (Teil 1 bis 6) — 2026-09-21 bis 2026-09-23

**Geprüfter Stand:** `4e94354` (Branch `chore/phase-5-p51-toter-code-pr`). **Plan:** [`pruefplan_gegenpruefung_2026-09-21.md`](pruefplan_gegenpruefung_2026-09-21.md).

**Das ist ein weitgehend abgeschlossener Stand**, kein vollständiger. Geprüft: Block 0 vollständig; Block 1 (Commit-Regeln) bis auf den vollen Commit-für-Commit-`pytest`-Lauf (ersetzt durch sechs Tagesenden voll geprüft, siehe unten — als gleichwertiger Ersatz begründet, nicht als Lücke); Block 2 vollständig; Block 3 die Mutationsproben, P2.10 bis P2.13, P3.2, der Backtest und sieben der elf restlichen Phase-3-Audit-Findings; Block 4 P4.5 und die Grenzen des Zahlen-Registers; Block 5 ein Durchgang durch alle acht Schritte, alle Bereiche, 375/1024 px, den dunklen Modus, die Tastaturbedienung beim ersten Laden, den State Explorer, die «Bericht»-Ansicht und «Modellannahmen» mit Szenariowechsel; Block 6 die Dateiverweise, die Schrittzahl, tote Anker, die Stand-Zeile und **alle 21** geänderten Handbuchkapitel vollständig gelesen (nicht nur die Stichprobe von dreien). **Nicht geprüft** ist alles unter [Was noch aussteht](#was-noch-aussteht) — vor allem CLAUDE.md/Projektplan Satz für Satz, der Linux-Lauf des Browser-Wächters, und vier der elf Phase-3-Audit-Findings.

## Ergebnis in einem Satz

Ein Verstoß gegen das Commit-Regelwerk (`black`), **acht** reproduzierbare Befunde am laufenden System oder in der Doku (Sprunglink-Fokus, «? Ticks» im Szenario-Narrativ, vier Handbuchkapitel mit veralteten Schrittangaben seit P7.13, zwei tote Ortsverweise auf einen vor-P1.2-Namen, veraltete Backtest-Zahlen im zentralen «Grenzen»-Kapitel, ein zweideutig benannter Schalter, eine sichtbar kaputte Tabelle im Handbuch), zwei Fragen an Haiko, sonst hält, was die Commit-Messages zusagen — jede nachgemessene Zahl (auch die mit abweichenden Kommastellen) und jede Mutationsprobe hat sich als richtig oder erklärbar erwiesen. **Kein Befund berührt die Zahlen eines Laufs oder eine Sicherheits-/Rechte-Invariante** — die Doku-Befunde sind Text, kein Verhalten.

## Befunde

### Nachbesserung

**N1 — `black` ist seit `2e71011` rot, elf Commits lang.** Regel 2 des Commit-Regelwerks («jeder Commit für sich grün») ist damit verletzt.

- **Nachgewiesen:** `ruff check` und `black --check` über jeden der 147 Commits des Branches. `ruff` ist in allen grün. `black` ist es bis `8591d2f` und wird ab **`2e71011`** (2026-09-15, P7.13) rot, danach in jedem Commit bis zur Spitze.
- **Dateien:** `tests/test_rahmen_im_artefakt.py` (seit `2e71011`), `tests/test_web_pruefschritt.py` und `tests/test_web_rail.py` (seit `338dc41`, P7.5-U5.1).
- **Kein reiner Versionsunterschied:** `test_web_rail.py` enthält Zeilen über 100 Zeichen (`line-length = 100` in `pyproject.toml`), die jede `black`-Version umbrechen würde. Bei `test_rahmen_im_artefakt.py` (Klammerstil einer `assert`-Meldung) kann Versionsdrift mitspielen: `black` steht in `pyproject.toml` ohne Version im Extra `dev`, die Ergebnisse hängen also vom Installationszeitpunkt ab.
- **Warum es nicht früher auffiel:** Es gibt für diesen Branch weder einen PR noch einen CI-Lauf (`gh pr list`, `gh run list`: leer).
- **Bestätigt durch den Sechs-Punkte-Lauf (Teil 3):** `black --check .` (ohne `-q`, mit Exit-Code-Prüfung) an sechs Tagesenden des Branches, eigene `.venv`: exit 0 an den ersten vier (2026-09-11 bis -14), **exit 1 mit genau diesen drei Dateien an den letzten beiden** (2026-09-15 `07e4411`, 2026-09-16 `4e94354`) — exakt konsistent mit der oben genannten Ursache `2e71011` (2026-09-15).
- **Methodenfehler dabei aufgefallen und korrigiert:** Der erste Durchlauf dieses Sechs-Punkte-Laufs benutzte `black --check -q .`; `-q` unterdrückt bei `--check` auch die «would reformat»-Meldungen (nicht nur den Erfolgsfall), sodass die Schleife an allen sechs Punkten fälschlich still blieb und ich black zwischenzeitlich für überall grün hielt. Der Fehler lag am Flag, nicht am Code; der wiederholte Lauf ohne `-q` bestätigt N1 unverändert.
- **Vorschlag:** `black .` einmal laufen lassen und als eigenen `style`-Commit einspielen (Regel 4: keine Vermischung), und `black` im Extra `dev` auf eine Version festlegen, damit CI und Entwicklungsrechner dasselbe formatieren.

**N2 — Der Sprunglink ist beim ersten Laden nicht der erste Tab-Stopp, obwohl CLAUDE.md genau das zusagt** («darin der «Zum Inhalt springen»-Link als erstes fokussierbares Element», WCAG 2.4.1). Gemessen am laufenden Dashboard, reproduzierbar (frischer `navigate` und `location.reload()`, beides zweimal geprüft): Direkt nach dem Laden von `/app/` steht der Tastaturfokus bereits auf der `<h1>` «Lauf einrichten» — nicht auf `body`, nicht auf dem Sprunglink. Der erste `Tab`-Druck (mit echtem `computer{action:"key", text:"Tab"}`, nicht simuliert) springt deshalb zum nächsten Element danach (den Knopf «Neuen Lauf einrichten»), am Sprunglink vorbei.

- **Ursache, lokalisiert:** `dashboard/web/config_editor/wizard.py:1198-1213`, der Fokus-folgt-der-Frage-Mechanismus (P1.9-W5.3). Er ruft `setzen()` **synchron**, sobald der `MutationObserver` registriert wird («Falls der Baum schon steht, bevor dieser Callback läuft») — und beim allerersten Laden ist `document.activeElement === document.body`, also gilt `frei = true`, und die `h1` im `wizard-content-host` wird sofort fokussiert. Der Callback trägt `prevent_initial_call=True`, das schützt hier aber nicht: Der Bereich «Einrichten» ist die leere Standardroute, sein Rumpf entsteht beim ersten Rendern, und `setzen()` läuft unabhängig vom Dash-Callback-Zyklus, sobald das Skript ausgeführt wird.
- **Der `shell`-Callback (Bereichswechsel, `app.py:426-492`) ist es nicht** — gegengeprüft: Sein Output (`BEREICH_ANSAGE.title`) blieb nach dem Laden `null`, er hat nicht gefeuert.
- **Der bestehende Test prüft nur die DOM-Reihenfolge, nicht das Tab-Verhalten:** `tests/test_web_a11y.py::test_the_skip_link_comes_first` liest `kinder[0]` aus dem Python-Baum und stimmt — der Sprunglink *ist* im DOM zuerst. Kein Test im Repo drückt eine echte Tab-Taste. Das ist dieselbe Klasse Lücke, die CLAUDE.md selbst mehrfach benennt («ein Parser findet, was jemand hingeschrieben hat; eine Messung findet, was wirklich dasteht»).
- **Reichweite:** Betrifft jeden ersten Aufruf des Dashboards, weil «Einrichten» die leere Standardroute ist. Andere Bereiche (`/app/lauf`, `/app/runs`, `/app/modell`, `/app/doku`) haben keinen `wizard-content-host` und sind davon vermutlich nicht betroffen — nicht einzeln nachgeprüft.
- **Nicht geprüft:** ob ein Tastaturnutzer den Sprunglink mit `Shift+Tab` von der `h1` aus doch erreicht (wahrscheinlich ja, aber das ist nicht die Zusage — WCAG 2.4.1 verlangt ihn als *ersten*, nicht als *erreichbaren* Stopp).

**N3 — Jeder Lauf trägt `ticks_completed: null` und `ticks_max: null` in seinem `run_scenario.json`, sichtbar als «? Ticks» im Szenario-Narrativ der Ergebnis-Ansicht.** Nachgemessen über **alle acht** vorhandenen Läufe unter `outputs/` — darunter drei vom 2026-08-30, also nicht meine eigenen —, ausnahmslos `None`/`None`.

- **Ursache, lokalisiert:** `src/run_simulation.py::save_run_outputs` ruft `generate_and_save_run_scenario` (Zeile ~317) **vor** `save_run_metadata` (Zeile ~344) auf — der Kommentar dort nennt einen Grund für diese Reihenfolge («Zuletzt, damit auch ein Ausfall im Szenario-Narrativ noch mitgezählt wird»), ohne die Nebenwirkung zu nennen. `_compute_summary_metrics` in `src/reporting/run_scenario_generator/context.py:73` liest `ticks_completed`, `ticks_max` und `simulation_name`/`name` aus einem `metadata`-Dict, das über `_load_json(directory / "run_metadata.json", {})` **von der Platte** geladen wird — zu diesem Zeitpunkt existiert die Datei noch nicht, der Rückfall `{}` greift, alle drei Felder werden `None`. `build_run_narrative` (`narrative.py:26`) fängt das für die Anzeige mit `or "?"` ab, `rendering.py:32` ebenso — beide **markieren** die Lücke sichtbar statt sie zu erfinden (Invariante 1 hält formal), aber das Narrativ verliert eine Information, die zu diesem Zeitpunkt im laufenden Prozess längst da ist (`state.clock`/`args`), nur eben nicht auf der Platte.
- **`save_run_outputs` ist ein gemeinsamer Pfad**: Laut CLAUDE.md (P3.6) steht es im `__all__` von `run_simulation.py` und wird von `dashboard/run_launcher.py` benutzt — der Bug betrifft also CLI- und Dashboard-Läufe gleichermaßen, nicht nur meine Testläufe.
- **Kein bestehender Test fängt das:** `tests/test_run_scenario_generator.py:76/441` legt `run_metadata.json` per Fixture **vor** dem Aufruf an (`_mit_metadaten`) und bildet damit die echte Schreibreihenfolge aus `save_run_outputs` nicht ab — dieselbe Klasse Lücke wie N2 (der Test prüft die Funktion isoliert, nicht den Ablauf, in dem sie steht).
- **Nicht in `docs/audit_findings.md` geführt.** Trage ich unten als Finding nach.
- **Nicht geprüft:** ob und wie das `booking_rate_start/end`- und `ticket_price_*`-Feld (aus `tick_mechanics.json`, nicht aus `metadata`) betroffen sind — nach Lesen des Codes: nein, die kommen aus einer anderen, zu diesem Zeitpunkt schon vorhandenen Quelle, und meine Stichprobe zeigt dort plausible Zahlen.

**N4 — Drei Handbuchkapitel nennen eine Schrittposition im Assistenten, die seit P7.13 (zwei neue optionale Schritte «Verläufe» und «Modellannahmen» vor der alten Zählung) nicht mehr stimmt.** Live im Assistenten nachgemessen (acht Schritte, Stand `4e94354`):

| Datei | Behauptet | Tatsächlich (nachgemessen) |
| --- | --- | --- |
| `docs/handbuch/lauf-starten.md:170` | «Eigenen Zufallsstartwert festlegen» **im dritten Schritt** | Schritt **5** («Womit wird gerechnet?») |
| `docs/handbuch/fragestellungen.md:31` | Wiederholungen hinter «Feinabstimmung» **im zweiten Schritt** | Schritt **4** («Wie weit reicht der Lauf?») |
| `docs/handbuch/vergleiche.md:43` | dieselbe Stelle, wortgleich | Schritt **4** |
| `docs/handbuch/presets.md:137` | «Alle Szenarien vergleichen» hinter «Feinabstimmung» **des zweiten Schritts** | Schritt **4** |

- **Alle vier Dateien wurden in diesem Branch angefasst** (`git diff --name-only aff7d63 HEAD` listet sie), die betroffenen Zeilen selbst aber zuletzt am **2026-08-28** geändert (`9aa04bb`, `6aa040b`, `9fb40b8`) — also vor P7.13 (2026-09-14/15). `lauf-starten.md` wurde am 2026-09-15 im selben Commit wie P7.5-U5.1 nochmal bearbeitet (ein anderer Absatz, über das Bedienfeld), die Schritt-Referenz dabei nicht korrigiert. `presets.md:137` kam bei der vollständigen Durchsicht aller 21 geänderten Handbuchdateien am 2026-09-23 dazu (Teil 6, siehe unten).
- **Kein funktionaler Bug, aber ein Doku-Pflicht-Verstoß:** CLAUDE.md verlangt «ändert sie sichtbares Verhalten von Dashboard oder CLI? Dann die passenden Kapitel unter `docs/handbuch/` … mitpflegen» — die Schrittfolge hat sich sichtbar geändert (sechs → acht Schritte), diese vier Stellen sind nicht mitgezogen.
- **`erste-simulation.md`** benutzt dagegen eine **eigene, als didaktisch erkennbare** Nummerierung («Schritt 1» bis «Schritt 5» als Kurzanleitung für den ersten Durchgang, die «Verläufe»/«Modellannahmen» bewusst überspringt und das auch so sagt) — das ist kein Fehler, nur ein anderes Zählschema, das mit dem Wizard-eigenen «Schritt N von 8» verwechselt werden kann.
- **Nicht in `docs/audit_findings.md` geführt.** Trage ich unten nach.

## Teil 6 — vollständige Durchsicht der 21 Handbuchkapitel (2026-09-23)

Alle 21 in diesem Branch geänderten Handbuchdateien gelesen (nicht nur die vier aus N4). Vier weitere Befunde, unterschiedlich schwer.

**N5 — Der Demo-Schalter im State Explorer trägt zwei Namen im Code selbst.** Das sichtbare Checkbox-Label (`dashboard/web/views/explorer.py:138`) heißt «Beispielantworten ohne Sprachmodell»; dieselbe Datei lässt die Demo-Antwort selbst (Zeile 41) sagen «Deaktivieren Sie «Demo ohne Ollama», wenn …» — live reproduziert, genau dieser Text erschien in meiner eigenen Demo-Antwort in Teil 4. `docs/handbuch/abfrage.md:64` übernimmt den zweiten, nicht sichtbaren Namen («Der Schalter «Demo ohne Ollama»»). Ein Nutzer, der der Demo-Antwort oder dem Handbuch folgt, sucht ein Label, das auf der Oberfläche nicht existiert. Kein Blocker, aber ein Verstoß gegen dieselbe Produktsprache-Disziplin wie P7.2 (ein Name, eine Bezeichnung).

**N6 — `docs/handbuch/ergebnisse-lesen.md` widerspricht sich selbst.** Zeile 17: «**Diagramme** mit sechs thematischen Auswertungen». Zeile 30, in der Tabelle direkt darunter: «Diagramme | **Vier** Fragen entlang der Wirkungskette». Nachgeprüft gegen den Code (`src/reporting/figure_generator/run_figures.py:107-116`) und gegen `docs/handbuch/ergebnisse.md:129` («**Vier Fragen**, die ein Lauf beantwortet»): **vier** ist richtig, «sechs» ist die Zahl der **vor P1.2** abgelösten datenquellenbasierten Bereiche («Yield & Markt», «Makro-Wirtschaft» …) und wurde in Zeile 17 offenbar nicht mitgezogen, als der Rest der Datei (Zeile 30 ff.) schon auf die neue Zählung umgestellt wurde.

**N7 — Die Backtest-Zahlen in `docs/handbuch/grenzen.md` sind veraltet, um mehrere Pakete.** Der Abschnitt «Was der Vergleich mit der Wirklichkeit ergeben hat» nennt «1,8 Indexpunkten» (Preisseite bis 2019), «38 Indexpunkte» (ab 2022), «auf 86 sinken … real … auf 126» (Nachfrageseite). Diese Zeilen stammen laut `git blame` vom **2026-08-31** (`20cee45`) — kurz nach dem allerersten Backtest-Lauf (P2.7, 2026-08-30) — und decken sich genau mit den in CLAUDE.md dokumentierten **allerersten** Zahlen («1,84 Indexpunkte … brach danach weg (38,4)», «Nachfrageseite … fiel auf 86, wo real 126 stand»). Seither haben mindestens **fünf** Pakete den Backtest verändert — P2.8 (Weg A), P2.8-B (Preisstrategie), P2.12 (Einkommen im Nutzen), P3.8 (Tick=Monat), P4.5 (Rahmen gestreckt) —, und die aktuellen Zahlen (von mir in Teil 1 aus `docs/backtest_vorlauf.md` neu erzeugt) liegen bei **1,15 / 21,37** für die Preisseite (2016–2019 / 2022–2024). **Besonders auffällig:** Zwei der Commits, die diese Verschiebung verursacht haben, haben `grenzen.md` selbst angefasst — `f719574` (P3.8) und `8f62984` (P4.5) haben andere Absätze derselben Datei aktualisiert (den Abschnitt direkt davor bzw. die Rahmenszenario-Länge), den Backtest-Zahlen-Absatz aber unverändert gelassen. Das ist die zentrale, nach außen kommunizierte «Grenzen des Modells»-Seite — veraltete Zahlen dort wiegen schwerer als anderswo im Handbuch.

**N8 — «Segmente & Alter» ist ein toter Ortsverweis, an zwei Stellen.** `docs/handbuch/kaufentscheidung.md:79` und `docs/handbuch/fragestellungen.md:16` verweisen auf «die Ansicht Diagramme unter «Segmente & Alter»». Dieser Name existiert nicht mehr als Ort — er ist laut `dashboard/web/views/figures.py:4` der Name eines **vor P1.2** abgelösten, datenquellenbasierten Bereichs (derselbe historische Sechser-Satz wie bei N6). Der heutige, korrekte Verweis wäre «Aussage 3 · Wer noch fliegt». Auffällig: `tests/test_web_glossar.py` soll laut CLAUDE.md genau solche Ortsverweise gegen die gültigen Namen aus `runs.TABS`/`shell.BEREICHE`/`wizard.STEPS` prüfen (P7.2-U2.2) — das deckt aber nur Top-Level-Bereichsnamen ab, nicht die vier Aussagen-Unterabschnitte von «Diagramme», deshalb hat der Wächter das nicht gefangen. Das ist eine Lücke im Wächter-Umfang, keine Fehlfunktion.

**N9 — Eine Markdown-Tabelle in `docs/handbuch/ref-config.md` ist durch einen eingefügten Abschnitt zerrissen und erscheint im gerenderten Handbuch als roher Text mit sichtbaren Pipe-Zeichen.** Live nachgeprüft unter `/app/doku/ref-config`: Der Nutzer sieht wörtlich «Der Bereich Modell im Dashboard zeigt diese Felder noch nicht — sie sind über die Datei zu ändern. | agents.json | Die drei Akteure mit ihren Rollen | | agent_profiles.json | Was jeder Akteur sehen und vorschlagen darf |». Ursache: Die Tabelle «Datei | Inhalt» (Zeile 8-13 im Quelltext) bricht nach vier Zeilen ab; die restlichen zwei Zeilen (`agents.json`, `agent_profiles.json`) stehen isoliert und ohne eigenen Tabellenkopf 33 Zeilen weiter unten (Zeile 46-47), getrennt durch eine Zwischenüberschrift und eine zweite Tabelle — kein Markdown-Renderer fasst das als eine zusammenhängende Tabelle auf. Die Satzzahl selbst («sechs Dateien») stimmt (die sechste und siebte Datei ergeben sich, wenn man `agents.json`/`agent_profiles.json` mitzählt), nur ihre Darstellung ist kaputt. **Vorbestehend:** `git blame` zeigt, dass diese Struktur schon vor dem 2026-09-15-Commit so war, der Fehler ist also älter als der geprüfte Branch und wurde bei keiner der seitherigen Bearbeitungen der Datei bemerkt. Anders als N4–N8 betrifft das nicht nur einen Ortsverweis, sondern sichtbar kaputte Darstellung auf einer Referenzseite.

**Alle vier nicht in `docs/audit_findings.md` geführt.** Trage ich unten nach.

### Fragen an Haiko

**F1 — Im PR hält nichts mehr die Zusage «ein Klick unter 500 ms».** P3.16 hat den Deckel auf 500 ms (550 durchgelassen) gesetzt, P7.11 hat ihn am 2026-09-12 als gerissen gemessen (592 bis 687 ms), und seit 2026-09-13 läuft die Klickmessung nur noch nachts und von Hand (`-m leistung`, `browser.yml`). `CLAUDE.md` und der Workflow sagen das offen. Meine Nachmessung heute (`-m leistung`, ein Lauf, ruhige Maschine): **beide Breiten grün**. Das widerspricht «P7.11 offen» nicht, denn der Plan selbst nennt einen grünen Einzellauf keinen Beleg (Streuung rund 150 ms). Zu klären: Bleibt die Zusage «500 ms» im Text von CLAUDE.md stehen, solange sie im PR ungeprüft ist? Und soll P7.11 mit einer Messreihe (mehrere Läufe) geschlossen werden, weil sie heute grün ist?

**F2 — Ein Branch, zwei Phasen, kein PR.** Der Branch heißt nach P5.1, trägt aber auch P7.0 bis P7.5 und P7.13 (45 Dateien in `dashboard/web`). Phase 5 war schon einmal ohne PR auf `main` gelandet und wurde am 2026-09-11 zurückgenommen (PR #16). Vorschlag: Phase 5 (Löschungen, 21 Commits P5.1 bis P5.3) und Phase 7 (Oberfläche) als zwei PRs. Das ist auch die Voraussetzung dafür, dass `browser.yml` (Pfadfilter `dashboard/web/**`) für die Oberflächenarbeit überhaupt greift.

### Notizen

- **N-a — Die Zahl aus P2.12 ist Geschichte.** `CLAUDE.md` nennt für den Standardlauf über 40 Ticks «0,264167 / 120,13». Ein heutiger Lauf (`--mock-llm --rounds 40`, Seed 42) liefert **Buchungsrate 0,2569, Preis 119,95**. Der Unterschied kommt aus P3.8 (Tick = Monat, 2026-09-07); `docs/handbuch/vergleiche.md` führt das als zwölften Schnitt. Die Stelle in CLAUDE.md ist mit «seit dem 2026-09-03» datiert und damit als Messung ihres Datums lesbar, nur eben nicht mehr reproduzierbar.
- **N-b — Doppelte Commit-Titel** (`0b13606`/`597fc46`, `7d7e83f`/`9e6b576`) haben denselben Patch-Id: Sie sind das Neuaufsetzen der zurückgenommenen Phase-5-Commits auf den Stand nach dem Revert, kein Fehler.
- **N-c — `docs/audit_findings.md`** führt neben der Liste noch zahlreiche «Erledigt am …»-Absätze. Die Regel in CLAUDE.md lautet «Finding entfernen, nicht abhaken»; die Absätze dokumentieren erledigte Pakete und keine offenen Findings, ob sie dort bleiben sollen, ist eine Ordnungsfrage. Nicht weiter geprüft.
- **N-d — Editable-Installation:** Ein Entwicklungsrechner mit einer Installation von vor P4.6 (`pip install -e .` vor dem 2026-09-11) lässt `test_packaging.py::TestDieInstallationLiefertDasPaketSrc` rot werden. Nach `pip install -e ".[dev]"` grün. Umgebung, kein Befund am Branch.
- **N-e — `agent_profiles.json` gibt dem Regulator kein explizites `events`-Recht, das Handbuch behauptet es trotzdem.** `configs/agent_profiles.json`: `regulator.may_propose = ["factor_state F2", "factor_state F6"]`, ohne `"events"` (anders als `provider.may_propose = ["events"]`). `docs/handbuch/akteure.md:26` sagt «Regulator | Ereignisse **und** Änderungen an den Faktoren F2 und F6». Der Prompt-Hinweis ans LLM («MAY PROPOSE ONLY: …», `agent_node.py:128`) nennt dem Regulator also nur die Faktoren, keine Events. **Nicht als Befund eingestuft, weil unklar:** `may_propose_factor` (die einzige serverseitig durchgesetzte Prüfung, Invariante 2) prüft laut Docstring nur Faktor-Vorschläge; `raw_event_entries = payload.get("events", [])` (`agent_node.py:166`) nimmt Events ohne Abgleich gegen `may_propose` entgegen — Events könnten also bei jedem Akteur technisch durchgehen, unabhängig vom Profil, weil sie laut Invariante 1 ohnehin nur Narrative sind, nie Kennzahlen. Ob das Handbuch damit das **erwartete Verhalten** korrekt beschreibt (Regulator darf de facto auch Events, weil nichts ihn daran hindert) oder eine **Absicht falsch wiedergibt** (Regulator sollte laut Config nur Faktoren vorschlagen), konnte ich ohne Rücksprache nicht klären. Gehört eher zu den Fragen an Haiko als zu den Befunden.

## Was gehalten hat (nachgemessen)

| Prüfung | Ergebnis |
| --- | --- |
| `ruff check .` am Spitzenstand und in allen 147 Commits | grün |
| `mypy` (20 Dateien) | grün |
| `pytest` ohne Browser-Wächter | 2 930 bestanden, 3 übersprungen |
| Browser-Wächter `tests/test_web_overflow.py` | 163 bestanden, 2 übersprungen (die zwei Klickmessungen), 5:18 min |
| Klickmessung `-m leistung` | 2 bestanden, 2:39 min (siehe F1) |
| `npm run build:css` | kein Diff am eingecheckten Stylesheet |
| Backtest `docs/backtest_vorlauf.md` neu erzeugt | unverändert; Preis 9,82 / 1,15, Nachfrage 36,44 / 25,04 / 51,64, Richtungstreffer 5/7 und 5/7 — deckt sich mit CLAUDE.md |
| Verweise auf entfernte Namen (57 Funktionen/Klassen aus `src/` und `dashboard/`) | keine im Code; nur Erwähnungen in Kommentaren, Docstrings, Historie |
| `streamlit` in Abhängigkeiten, README, Dockerfile, Compose, CI | nirgends mehr |
| Die 11 Commits ohne Test, davon 5 ohne Doku (Regel 3) | jeder nennt seinen Grund in der Message; die Ausnahmeklausel greift |
| `refactor(sweeps)`, `refactor(config)` (Regel 4) | reine Löschungen; die Begründung (Lauf findet die Bevölkerung über die ID `consumer`) stimmt mit `environment_node.py:78` überein |
| `--sweep` | in `run_simulation` weg; in `scenario_sweeps.py` bleibt es und wird gelesen (`sweep_filter`, Teilstring auf die ID) |
| Dashboard: alle sechs Adressen aufgerufen | keine Konsolenfehler; Titel und Ansage je Bereich stimmen; der Modell-Bereich entsteht erst beim Aufsuchen (143 → 471 Elemente, P3.12); der Leitstand zeigt einen echten 40-Tick-Lauf |

### Mutationsproben (Zusage gebrochen, Wächter muss rot werden)

Alle neun wurden erkannt, jeweils mit `git checkout` zurückgenommen (Arbeitsbaum danach sauber).

| Mutation | Wächter | Ergebnis |
| --- | --- | --- |
| Kopie in `environment_node` entfernt | `test_rundenhistorie.py` | 2 rot |
| Kopie in `agent_node` entfernt | `test_rundenhistorie.py` | 1 rot (der Syntaxbaum-Wächter) |
| Neuer, nie gelesener CLI-Schalter | `test_cli_schalter.py` | rot |
| P2.13 zurückgenommen (erfüllte Regel setzt keine Marke) | `test_faktoren_flattern_nicht.py` | 3 rot |
| `demand_growth_rate` wieder 0,03 je Tick | `test_ein_tick_ist_ein_monat.py` | 3 rot |
| Verfügbarkeitsnutzen auf 0 | `test_preisstrategie_ist_eine_wahl.py` | 1 rot |
| Einkommen wirkt wieder nur als Schwelle | `test_buchung_zieht.py` | 2 rot |
| `getattr(args, "model", "x")` in `metadata.py` | `test_lauf_argumente.py` | 1 rot (`test_kein_getattr_mit_rueckfall_...`) |
| `sweep_metadata_args` annotiert mit `-> dict` statt `-> RunArgs` | `test_lauf_argumente.py` | 1 rot, dazu `mypy`: 2 Fehler in `scenario_sweeps.py` |

### Nachgemessen in Teil 2 (2026-09-22)

| Prüfung | Ergebnis |
| --- | --- |
| **P2.13, die Zahlen selbst** (Fehler per Mutation wiederhergestellt, 120 Ticks) | Mit dem Fehler **111 Faktorwechsel, davon 106 bei F6** (der erste ist der echte Übergang, also 105 im Takt); 40 Ticks enden mit F6.1, 41 mit F6.2. Mit dem Fix **6 Wechsel** (je Faktor einer), F6 endet bei 40 wie bei 41 Ticks auf F6.2. Deckt sich mit Plan und Testdatei |
| **P2.10 / P4.5 an den Rahmenszenarien** | Alle vier Rahmen (`art: rahmen`) tragen `kapazitaet_index`, eine `preisstrategie` (drei `auslastung`, «Transformationskonflikt» `marge`), `kohaerenz` und `max_ticks` 120; die vier Stresstests 40 Ticks. `factor_overrides` ist in allen acht Dateien `[]` |
| «Freiwillige Wende»: Marken und Vorbehalt | CO₂-Abgabe 200 EUR bei Tick 48 (vier Jahre), SAF-Quote 5 % bei Tick 24 (zwei Jahre) — genau die Zahlen, die der Vorbehalt nennt; «20 Monate» bei 50 Ticks stimmt gerechnet (48 × 50/120) |
| **P3.2 am laufenden System** (`--resume` mit manipuliertem Checkpoint) | Version 1 und fehlende Versionsangabe: verständliche Meldung, **Exit-Code 2**, kein Traceback; unveränderter Checkpoint: Exit 0 |
| `CLAUDE.md`: jede genannte Datei | existiert, bis auf Erwähnungen von Historie (`market_rules.py`, `test_tickdauer_ist_uneinheitlich.py`, …), Laufartefakte und die Negation «nicht in einer `standard.json`». `src/legacy/` wird nur als entfernt geführt |
| `CLAUDE.md`: Schrittzahl des Assistenten | «Acht Schritte seit P7.13-U13.5» stimmt (`wizard.STEPS` hat acht) |
| **Schrittfolge durchgegangen** (alle acht Schritte, echte Klicks) | Keine Konsolenfehler; im sichtbaren Text kein rohes Markdown, kein Dateipfad, keine Paketkennung; der Hinweis «3 Verläufe enden vor dem Ende des Laufs — der früheste ist «SAF-Mandat» bei Tick 16» stimmt mit CLAUDE.md überein |
| **Regel 7 (Beobachtung)** | Nach dem Durchgang ist `configs/` unverändert (`git status` leer, Änderungszeit von `properties.json` gleich). Das ist eine Beobachtung, kein Beleg: Beweis ist `TestNurDasModellSchreibtInsModell`, und ich habe **keinen Wert im Assistenten geändert** |
| **375 px** | Kein waagerechter Überlauf in allen fünf Bereichen (Einrichten, Leitstand, Ergebnisse, Modell, Handbuch) |
| **Dunkler Modus** | Der Schalter wirkt (Grund `rgb(8, 13, 22)`, Text hell), keine weiße Fläche im Hauptbereich |

**Eine Beobachtung, kein neuer Befund:** Bei 375 px überdeckt die Statusanzeige «System bereit» die Wortmarke «AeroForesight AI» in der Kopfzeile des Leitstands («AeroF…»). P7.9 (schmale Breiten, Navigation) ist offen und deckt das Thema; ob es diese Stelle einschließt, steht dort nicht.

### Nachgemessen in Teil 4 (2026-09-23)

| Prüfung | Ergebnis |
| --- | --- |
| **P2.11** (zwei Quellen für dieselbe Marktkonstante) | `resolve_market_feedback_config` trägt keine Literal-Rückfälle mehr (nur `_FELDER`-Übersetzung); `marginal_cost_fraction` steht einheitlich bei `0,25` in `configs/properties.json`; `test_market_feedback.py -k marginal_cost` grün |
| **State Explorer, live** | Ohne Ollama: Abfrage scheitert **laut** mit klarer Fehlermeldung (Invariante 1 hält, keine erfundene Antwort). Mit «Beispielantworten ohne Sprachmodell»: liefert eine markierte Demo-Antwort ohne Zahlen — die Grounding-Prüfung selbst (P2.5) ließ sich damit nicht am Text beobachten, nur indirekt über die grüne Suite (`test_explorer_grounding.py`) |
| **«Bericht»-Ansicht** | Lädt fehlerfrei, Property-Zeitplan zeigt denselben Wortlaut wie CLAUDE.md («0,2657 % p.a.» zur Bevölkerungskurve), Preis Start/Ende deckt sich mit `price_history.json` |
| **«Modellannahmen» ändern + Szenariowechsel** | Ein an «Freiwillige Wende» geänderter Startwert (`demand_growth_rate`) wurde nach Wechsel zu «Business as Usual» auf dessen Standard zurückgesetzt — die Kernfunktion («ein Szenariowechsel verwirft Abweichungen») ist bestätigt. Die zugesagte «Rückgängig»-Meldung selbst habe ich **nicht** gesehen (vermutlich Timing meines Testablaufs) — nicht abschließend geprüft |
| **1024 px** | Kein waagerechter Überlauf in allen fünf Bereichen |
| **Modell-Bereich, Knotenzahlen** (C1-Nachfolgemessung) | Live im Browser bei 1280 px nachgemessen (dieselbe Methode wie der Docstring von `model_editor.HOST`: `document.querySelectorAll('*').length`): **2872 / 1951 / 134** statt der dokumentierten **3364 / 1886 / 146**. **Kein Befund:** Die Zahl in CLAUDE.md ist ausdrücklich «nachgemessen am 2026-09-06» datiert — nach der eigenen Doku-Regel («eine datierte Messung ist Geschichte und wird bewusst nicht gehalten») ist das keine Pflichtverletzung. Die tragende, undatierte Zusage («keine feste ID im Rumpf») hält weiter per grünem Test |
| **Tote Anker** `docs/projektplan.md#...` | 15 Verweise aus CLAUDE.md/Projektplan geprüft; alle 13 stichprobenartig direkt nachgesehenen Präfixe (P0.2, P1.9, P2.0, P2.2, P2.3, P2.7, P3.8, P3.9, P3.17, P4.4, P4.5, P7.11, Phase 7) haben eine passende Überschrift. Ein erster automatisierter Lauf meldete alle als «fehlend» — eigener Skriptfehler (En-Dash `–` in Überschriften wie «2015–2024» falsch behandelt), keine echten toten Links |
| **Stand-Zeile des Plans** | «163 bestanden» für den vollen Browser-Wächter (2026-09-16) deckt sich mit meiner eigenen Messung (Teil 1: 163 bestanden, 2026-09-21) |

### Nachgemessen in Teil 5 (2026-09-23)

| Prüfung | Ergebnis |
| --- | --- |
| **P2.10, konkrete Zahlen** (`marge`-Strategie, Kapazitäten 0,5/1,0/1,3, derselbe Helfer wie `test_preisstrategie_ist_eine_wahl.py::_lauf`) | Gemessen: Buchungsrate 0,0864 → 0,1087 → 0,1161 (Anstieg bestätigt), Preis konstant bei **194,78** über alle drei Kapazitäten (bewegt sich nicht, wie behauptet). CLAUDE.md nennt 0,0692 → 0,1151 bei Preis 189,78 — Richtung und Aussage («Preis bleibt stehen, Verkehr steigt deutlich») stimmen, die Kommastellen nicht mehr genau. **Ursache dieselbe wie bei der schon dokumentierten P2.12-Abweichung:** Die Zahl steht seit `e2d8ec3` (2026-09-03, **vor** P3.8) im Text, ohne Datum im Satz selbst — P3.8 (Tick=Monat, 2026-09-07) hat das Buchungsmodell seither verschoben. Kein neuer Befund, sondern eine zweite Bestätigung des Musters aus N-a |
| **Sieben der elf restlichen Phase-3-Audit-Findings** (`audit_phase3_2026-09-05.md`) direkt am Code nachgeprüft | **B1** (Rückfall `llama3.2` lebt weiter): kein Literal mehr im Code — hält. **B2** (`_schreibe` kann selbst scheitern): kein `.buffer`-Zugriff mehr, `print` mit `backslashreplace` — hält. **C2** (Kopfzeile klein geschrieben): eine Quelle `validation.BEFUND_KOPF` — hält. **C3** (Docstring nennt Vor-P3.12-Zahlen): die alten 665–1426 ms stehen jetzt ausdrücklich als historischer Vergleich da, nicht als aktuelles Kriterium — hält. **C4** (toter Verweis auf `save_start.py`): Datei bleibt als Name stehen, nicht als Link, und existiert wie dokumentiert nicht mehr — hält. **B3, B4, B6, C5** nur indirekt bestätigt (über die Mutationsprobe an `test_lauf_argumente.py`, die vorhandene Konstante `SICHTBAR_MAX_MS`, den eigenen grünen Browser-Wächter-Lauf bzw. die Struktur von `audit_findings.md`). **B5** (kleinere Befunde, mehrere gebündelt) nicht einzeln geprüft |
| **Zahlen-Register** (`test_doku_zahlen.py`) | Grenze ist selbstdokumentiert, keine Lücke: Das Register hält nur explizit eingetragene Zahlen, eine automatische Suche wird im Docstring ausdrücklich als «geht nicht» verworfen (zu viele Fehlalarme). Alle eingetragenen Einträge sind über den Test grün, damit korrekt — Vollständigkeit der Abdeckung ist eine bekannte, akzeptierte Grenze und kein Befund |
| **Handbuch gegen Oberfläche** (Stichprobe von 3 der 21 geänderten Dateien, live im Assistenten nachvollzogen) | **`lauf-starten.md`, `fragestellungen.md`, `vergleiche.md`: veraltete Schrittangaben, siehe N4.** `erste-simulation.md` benutzt ein eigenes, erkennbar didaktisches Zählschema — kein Fehler |

### Sechs Tagesenden des Branches, voll geprüft (Teil 3, 2026-09-22)

Letzter Commit je Kalendertag, `origin/main..origin/chore/phase-5-p51-toter-code-pr`, jeweils eigene `.venv` (Editable-Install ist pfadgebunden — ein geteiltes venv über zwei Worktrees prüft sonst den falschen `src`, siehe Methodennotiz unten), Pfad unter `C:\tmp` statt Scratchpad (dessen langer Pfad ließ DLLs von `black`/`mypy` nicht laden — Umgebungsproblem, kein Branch-Befund).

| Commit | Datum | `ruff` | `black --check .` | `mypy` | `pytest` (ohne Browser-Wächter) |
| --- | --- | --- | --- | --- | --- |
| `31981b8` | 2026-09-11 | grün | grün | grün | 2302 bestanden, 2 übersprungen |
| `da96bba` | 2026-09-12 | grün | grün | grün | 2484 bestanden, 4 übersprungen |
| `19b99c2` | 2026-09-13 | grün | grün | grün | 2660 bestanden, 4 übersprungen |
| `d1bfa46` | 2026-09-14 | grün | grün | grün | 2804 bestanden, 4 übersprungen |
| `07e4411` | 2026-09-15 | grün | **rot** (3 Dateien, siehe N1) | grün | 2929 bestanden, 4 übersprungen |
| `4e94354` | 2026-09-16 (Spitze) | grün | **rot** (dieselben 3, siehe N1) | grün | — (deckt sich mit Block 0) |

Kein einziger roter `pytest`- oder `mypy`-Lauf über alle sechs Punkte. Steigende Testzahl über die Zeit (2302 → 2929) zeigt, dass an keinem Grenzpunkt Tests verschwunden sind, nur dazugekommen.

**Methodennotiz:** Der erste Durchlauf benutzte `black --check -q .`, dessen `-q` bei `--check` auch die Verstoß-Meldungen unterdrückt — siehe die Korrektur bei N1. Der zweite, hier gezeigte Durchlauf prüft ohne `-q` und wertet den Exit-Code aus.

## Was noch aussteht

- **Block 1.3:** Alle 147 Commits nur mit `ruff`/`black`; sechs Tagesenden zusätzlich voll mit `pytest`/`mypy` (Teil 3). Als gleichwertiger Ersatz für den vollen Commit-für-Commit-Lauf begründet — nicht mehr offen im Sinne von „unbeachtet", aber auch kein Ersatz, der jeden einzelnen der 147 Commits einzeln bestätigt.
- **Block 3:** die übrigen vier der elf Phase-3-Audit-Findings (B3, B4, B6, C5 nur indirekt bestätigt; B5 «kleinere Befunde» gar nicht einzeln).
- **Block 4:** unverändert offen — das Zahlen-Register deckt nachweislich nicht jede Zahl im Fließtext ab (selbstdokumentierte, akzeptierte Grenze), nicht geprüft ist, ob eine der **nicht** eingetragenen Zahlen falsch ist.
- **Block 5:** die zugesagte «Rückgängig»-Meldung selbst sehen (die Kernfunktion ist bestätigt, die Meldung nicht); die Grounding-Prüfung des State Explorers mit einer echten (nicht Demo-)Antwort — braucht Ollama. **Erledigt (2026-09-23, Teil 6):** alle 21 geänderten Handbuchdateien gelesen, nicht nur die Stichprobe von dreien — vier weitere Befunde gefunden (N5 bis N9), Details siehe Teil 6.
- **Block 6:** `CLAUDE.md` Satz für Satz gegen den Code vollständig (stichprobenartig geprüft: Dateiverweise, Schrittzahl, Konstantennamen, Modell-Bereich-Zahlen, tote Anker); `docs/projektplan.md` alle Erledigt-Marken einzeln gegen Code und Tests (nur die Stand-Zeile geprüft). Die Agent-Rechte-Frage (N-e, Regulator/Events) ist offen und braucht Rücksprache, keine weitere eigene Prüfung.
- **Linux-Lauf von `browser.yml`, geklärt (2026-09-23):** Er existiert und läuft zuverlässig — `gh run list --workflow=browser.yml`: nächtlich seit mindestens dem 2026-09-13, jeder der letzten zehn Läufe `success`. **Aber nicht für diesen Branch:** Jeder Lauf hat `headBranch: main` (per `schedule` ausgelöst); der Pfadfilter für Pull Requests greift erst mit einem PR, und diesen Branch gibt es nicht als PR (siehe Finding, Punkt 6). Die Windows-Deckel sind für den Code-Stand von `main` (ohne Phase 7) bestätigt Linux-tauglich — für die neuen Deckel aus P7.1 bis P7.13 (nur in diesem Branch) liegt noch kein Linux-Lauf vor.
