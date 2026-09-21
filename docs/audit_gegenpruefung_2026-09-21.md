# Befundprotokoll der Gegenprüfung (Teil 1) — 2026-09-21

**Geprüfter Stand:** `4e94354` (Branch `chore/phase-5-p51-toter-code-pr`). **Plan:** [`pruefplan_gegenpruefung_2026-09-21.md`](pruefplan_gegenpruefung_2026-09-21.md).

**Das ist ein Zwischenstand.** Geprüft sind Block 0, 1 und 2 vollständig bis auf die unten genannten Lücken, aus Block 3 die Mutationsproben und die Backtest-Zahlen, aus Block 5 ein Durchgang durch alle Bereiche im laufenden Dashboard. **Nicht geprüft** ist alles unter [Was noch aussteht](#was-noch-aussteht). «Kein Blocker gefunden» heißt deshalb nur: keiner in dem, was gelaufen ist.

## Ergebnis in einem Satz

Ein Verstoß gegen das Commit-Regelwerk (`black` ist in den letzten elf Commits rot), zwei Fragen an Haiko, sonst hält, was die Commit-Messages zusagen — jede nachgemessene Zahl und jede Mutationsprobe hat gestimmt.

## Befunde

### Nachbesserung

**N1 — `black` ist seit `2e71011` rot, elf Commits lang.** Regel 2 des Commit-Regelwerks («jeder Commit für sich grün») ist damit verletzt.

- **Nachgewiesen:** `ruff check` und `black --check` über jeden der 147 Commits des Branches. `ruff` ist in allen grün. `black` ist es bis `8591d2f` und wird ab **`2e71011`** (2026-09-15, P7.13) rot, danach in jedem Commit bis zur Spitze.
- **Dateien:** `tests/test_rahmen_im_artefakt.py` (seit `2e71011`), `tests/test_web_pruefschritt.py` und `tests/test_web_rail.py` (seit `338dc41`, P7.5-U5.1).
- **Kein reiner Versionsunterschied:** `test_web_rail.py` enthält Zeilen über 100 Zeichen (`line-length = 100` in `pyproject.toml`), die jede `black`-Version umbrechen würde. Bei `test_rahmen_im_artefakt.py` (Klammerstil einer `assert`-Meldung) kann Versionsdrift mitspielen: `black` steht in `pyproject.toml` ohne Version im Extra `dev`, die Ergebnisse hängen also vom Installationszeitpunkt ab.
- **Warum es nicht früher auffiel:** Es gibt für diesen Branch weder einen PR noch einen CI-Lauf (`gh pr list`, `gh run list`: leer).- **Vorschlag:** `black .` einmal laufen lassen und als eigenen `style`-Commit einspielen (Regel 4: keine Vermischung), und `black` im Extra `dev` auf eine Version festlegen, damit CI und Entwicklungsrechner dasselbe formatieren.

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

Alle sieben wurden erkannt, jeweils mit `git checkout` zurückgenommen (Arbeitsbaum danach sauber).

| Mutation | Wächter | Ergebnis |
| --- | --- | --- |
| Kopie in `environment_node` entfernt | `test_rundenhistorie.py` | 2 rot |
| Kopie in `agent_node` entfernt | `test_rundenhistorie.py` | 1 rot (der Syntaxbaum-Wächter) |
| Neuer, nie gelesener CLI-Schalter | `test_cli_schalter.py` | rot |
| P2.13 zurückgenommen (erfüllte Regel setzt keine Marke) | `test_faktoren_flattern_nicht.py` | 3 rot |
| `demand_growth_rate` wieder 0,03 je Tick | `test_ein_tick_ist_ein_monat.py` | 3 rot |
| Verfügbarkeitsnutzen auf 0 | `test_preisstrategie_ist_eine_wahl.py` | 1 rot |
| Einkommen wirkt wieder nur als Schwelle | `test_buchung_zieht.py` | 2 rot |

Die Probe für `test_lauf_argumente.py` steht noch aus (siehe unten).

## Was noch aussteht

- **Block 1.3 voll:** Nur `ruff` und `black` über alle Commits; `pytest` je Commit ist nicht gelaufen (rund fünf Stunden).
- **Block 3:** die Zahlen von P2.10, P2.11, P2.13 einzeln nachmessen (nur P3.8 und der Backtest sind nachgemessen); Stichprobe der zwölf Pakete aus `audit_phase3_2026-09-05.md`; die Mutationsprobe von `test_lauf_argumente.py`.
- **Block 4:** jeder Ankersatz aus CLAUDE.md gegen `test_doku_zahlen.py` (der Test ist grün, aber ob das Register vollständig ist, ist nicht gelesen); P4.5 (Rahmenszenarien gestreckt).
- **Block 5:** die Schrittfolge von Hand durchklicken (Regel 7, «Rückgängig», Verläufe, «Modellannahmen»), 375 px, Hell/Dunkel, Tastaturbedienung, die 21 geänderten Handbuchdateien gegen die Oberfläche lesen.
- **Block 6:** CLAUDE.md Satz für Satz gegen den Code; `docs/projektplan.md` (Stand-Zeile und alle Erledigt-Marken) gegen Code und Tests; tote Anker.
- **Linux-Lauf** von `browser.yml`: Die Deckel sind unter Windows erhoben; ob sie auf Linux halten, ist ungeprüft.
