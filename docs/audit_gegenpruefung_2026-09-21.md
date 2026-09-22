# Befundprotokoll der Gegenprüfung (Teil 1, 2 und 3) — 2026-09-21 und 2026-09-22

**Geprüfter Stand:** `4e94354` (Branch `chore/phase-5-p51-toter-code-pr`). **Plan:** [`pruefplan_gegenpruefung_2026-09-21.md`](pruefplan_gegenpruefung_2026-09-21.md).

**Das ist immer noch ein Zwischenstand.** Geprüft sind Block 0, 1 und 2 bis auf die unten genannten Lücken, aus Block 3 die Mutationsproben, P2.13, P3.2, der Backtest und (neu) sechs Tagesenden des Branches mit vollem `pytest`/`ruff`/`black`/`mypy`, aus Block 4 P4.5, aus Block 5 ein Durchgang durch alle acht Schritte, alle Bereiche, 375 px, den dunklen Modus und (neu) die Tastaturbedienung beim ersten Laden, aus Block 6 die Dateiverweise und die Schrittzahl in CLAUDE.md. **Nicht geprüft** ist alles unter [Was noch aussteht](#was-noch-aussteht). «Kein Blocker gefunden» heißt deshalb nur: keiner in dem, was gelaufen ist.

## Ergebnis in einem Satz

Ein Verstoß gegen das Commit-Regelwerk (`black` ist in den letzten elf Commits rot), zwei reproduzierbare Befunde am laufenden System (der Sprunglink ist beim ersten Laden nicht der erste Tab-Stopp; jeder Lauf zeigt «? Ticks» im Szenario-Narrativ wegen einer Schreibreihenfolge), zwei Fragen an Haiko, sonst hält, was die Commit-Messages zusagen — jede nachgemessene Zahl und jede Mutationsprobe hat gestimmt.

## Befunde

### Nachbesserung

**N1 — `black` ist seit `2e71011` rot, elf Commits lang.** Regel 2 des Commit-Regelwerks («jeder Commit für sich grün») ist damit verletzt.

- **Nachgewiesen:** `ruff check` und `black --check` über jeden der 147 Commits des Branches. `ruff` ist in allen grün. `black` ist es bis `8591d2f` und wird ab **`2e71011`** (2026-09-15, P7.13) rot, danach in jedem Commit bis zur Spitze.
- **Dateien:** `tests/test_rahmen_im_artefakt.py` (seit `2e71011`), `tests/test_web_pruefschritt.py` und `tests/test_web_rail.py` (seit `338dc41`, P7.5-U5.1).
- **Kein reiner Versionsunterschied:** `test_web_rail.py` enthält Zeilen über 100 Zeichen (`line-length = 100` in `pyproject.toml`), die jede `black`-Version umbrechen würde. Bei `test_rahmen_im_artefakt.py` (Klammerstil einer `assert`-Meldung) kann Versionsdrift mitspielen: `black` steht in `pyproject.toml` ohne Version im Extra `dev`, die Ergebnisse hängen also vom Installationszeitpunkt ab.
- **Warum es nicht früher auffiel:** Es gibt für diesen Branch weder einen PR noch einen CI-Lauf (`gh pr list`, `gh run list`: leer).
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

### Fragen an Haiko

**F1 — Im PR hält nichts mehr die Zusage «ein Klick unter 500 ms».** P3.16 hat den Deckel auf 500 ms (550 durchgelassen) gesetzt, P7.11 hat ihn am 2026-09-12 als gerissen gemessen (592 bis 687 ms), und seit 2026-09-13 läuft die Klickmessung nur noch nachts und von Hand (`-m leistung`, `browser.yml`). `CLAUDE.md` und der Workflow sagen das offen. Meine Nachmessung heute (`-m leistung`, ein Lauf, ruhige Maschine): **beide Breiten grün**. Das widerspricht «P7.11 offen» nicht, denn der Plan selbst nennt einen grünen Einzellauf keinen Beleg (Streuung rund 150 ms). Zu klären: Bleibt die Zusage «500 ms» im Text von CLAUDE.md stehen, solange sie im PR ungeprüft ist? Und soll P7.11 mit einer Messreihe (mehrere Läufe) geschlossen werden, weil sie heute grün ist?

**F2 — Ein Branch, zwei Phasen, kein PR.** Der Branch heißt nach P5.1, trägt aber auch P7.0 bis P7.5 und P7.13 (45 Dateien in `dashboard/web`). Phase 5 war schon einmal ohne PR auf `main` gelandet und wurde am 2026-09-11 zurückgenommen (PR #16). Vorschlag: Phase 5 (Löschungen, 21 Commits P5.1 bis P5.3) und Phase 7 (Oberfläche) als zwei PRs. Das ist auch die Voraussetzung dafür, dass `browser.yml` (Pfadfilter `dashboard/web/**`) für die Oberflächenarbeit überhaupt greift.

### Notizen

- **N-a — Die Zahl aus P2.12 ist Geschichte.** `CLAUDE.md` nennt für den Standardlauf über 40 Ticks «0,264167 / 120,13». Ein heutiger Lauf (`--mock-llm --rounds 40`, Seed 42) liefert **Buchungsrate 0,2569, Preis 119,95**. Der Unterschied kommt aus P3.8 (Tick = Monat, 2026-09-07); `docs/handbuch/vergleiche.md` führt das als zwölften Schnitt. Die Stelle in CLAUDE.md ist mit «seit dem 2026-09-03» datiert und damit als Messung ihres Datums lesbar, nur eben nicht mehr reproduzierbar.
- **N-b — Doppelte Commit-Titel** (`0b13606`/`597fc46`, `7d7e83f`/`9e6b576`) haben denselben Patch-Id: Sie sind das Neuaufsetzen der zurückgenommenen Phase-5-Commits auf den Stand nach dem Revert, kein Fehler.
- **N-c — `docs/audit_findings.md`** führt neben der Liste noch zahlreiche «Erledigt am …»-Absätze. Die Regel in CLAUDE.md lautet «Finding entfernen, nicht abhaken»; die Absätze dokumentieren erledigte Pakete und keine offenen Findings, ob sie dort bleiben sollen, ist eine Ordnungsfrage. Nicht weiter geprüft.
- **N-d — Editable-Installation:** Ein Entwicklungsrechner mit einer Installation von vor P4.6 (`pip install -e .` vor dem 2026-09-11) lässt `test_packaging.py::TestDieInstallationLiefertDasPaketSrc` rot werden. Nach `pip install -e ".[dev]"` grün. Umgebung, kein Befund am Branch.

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

## Was noch aussteht

- **Block 1.3 voll:** Nur `ruff` und `black` über alle Commits; `pytest` je Commit ist nicht gelaufen (rund fünf Stunden).
- **Block 3:** die Zahlen von P2.10, P2.11 und P2.12 einzeln nachmessen (P2.12 nur über die Mutationsprobe erreicht, nicht über den Standardlauf: der hat sich mit P3.8 verschoben); die übrigen elf Pakete des Phase-3-Audits (`audit_phase3_2026-09-05.md`) stichprobenartig — nur P3.2 ist nachgestellt.
- **Block 4:** ob das Zahlen-Register (`test_doku_zahlen.py`) vollständig ist (der Test ist grün, was er **nicht** erfasst, ist nicht gelesen).
- **Block 5:** einen Wert in «Modellannahmen» ändern und «Rückgängig» beim Szenariowechsel ausprobieren; Tastaturbedienung (Sprunglink, Fokus auf die Überschrift) von Hand; 1024 px; die 21 geänderten Handbuchdateien gegen die Oberfläche lesen; die Ergebnis-Ansichten mit einem Lauf (nur der Leitstand ist gesehen).
- **Block 6:** `CLAUDE.md` Satz für Satz gegen den Code (geprüft sind nur Dateiverweise und die Schrittzahl); `docs/projektplan.md` (Stand-Zeile und alle Erledigt-Marken) gegen Code und Tests; tote Anker.
- **Linux-Lauf** von `browser.yml`: Die Deckel sind unter Windows erhoben; ob sie auf Linux halten, ist ungeprüft.
