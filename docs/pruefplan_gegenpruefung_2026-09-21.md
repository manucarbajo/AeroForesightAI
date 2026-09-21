# Prüfplan: Gegenprüfung der Arbeit von Haiko seit dem 2026-09-02

**Angelegt:** 2026-09-21 · **Geprüfter Stand:** `4e94354` (Branch `chore/phase-5-p51-toter-code-pr`, 2026-09-16)

Dieser Plan legt fest, wie alles geprüft wird, was seit dem letzten Commit von Manuel (`aff7d63`, 2026-09-02) dazugekommen ist. **Er ist ein Prüfplan und kein Befundbericht:** Die Blöcke 1 bis 7 sind bei der Anlage noch nicht abgearbeitet. Nur Block 0 ist bereits einmal gelaufen (siehe [Grundlinie](#grundlinie-gemessen-am-2026-09-21)).

## Umfang

| Größe | Wert |
| --- | --- |
| Commits `aff7d63..4e94354` | 254, alle von Haiko Wiedenberg |
| Davon schon in `main` (PR #11 bis #15) | 107 |
| Davon nur im offenen Branch | 147 |
| Geänderte Dateien | 282 (+37 364 / −9 017 Zeilen) |
| Tests: neu / geändert / gelöscht | 55 / 53 / 3 |
| `dashboard/web` | 45 Dateien, +5 872 / −1 392 |
| `dashboard/legacy_streamlit` | 9 Dateien, −2 951 (entfernt) |
| Arbeitspakete im Verlauf | P2.x, P3.x, P4.x, P5.1 bis P5.3, P7.0 bis P7.5, P7.9, P7.11 bis P7.13 |

Die Zählungen stammen aus `git diff --shortstat` und `git log` über `aff7d63..4e94354` (Stand 2026-09-21).

## Was beim Zuschnitt auffällt

- **Der Branch ist für einen PR zu groß.** Er heißt nach P5.1, trägt aber auch die gesamte Oberflächen-Überarbeitung (P7.0 bis P7.5, P7.13). Vorschlag: in einen Phase-5- und einen Phase-7-PR teilen.
- **Phase 5 war schon einmal auf `main`** und wurde am 2026-09-11 zurückgenommen (PR #16), weil sie ohne Pull Request gelandet war. Der Branch bringt P5.1 und P5.3 wieder. Zwei Commits tragen deshalb denselben Titel (`0b13606` und `597fc46`, ebenso `7d7e83f` und `9e6b576`); zu klären ist, ob das absichtlich ein Neu-Aufsetzen ist.
- **Elf Commits ändern `src/` oder `dashboard/` ohne Test**, fünf davon auch ohne Doku (Regel 3 des Commit-Regelwerks): `3758c8a`, `3d81a6a`, `bfe7ddc`, `e782d8a`, `fe849c9`. Die übrigen sechs: `0b13606`, `597fc46`, `7d7e83f`, `9e6b576`, `b7c3a67`, `da96bba`.
- **Drei Tests sind gelöscht:** `test_environment_node.py`, `test_tickdauer_ist_uneinheitlich.py`, `debug_run_sequential.py`. Der zweite wurde bewusst durch `test_ein_tick_ist_ein_monat.py` abgelöst (P3.8). Bei den anderen beiden ist zu prüfen, ob der Schutz woanders weiterlebt.

## Grundlinie (gemessen am 2026-09-21)

Auf `4e94354`, frische Installation mit `pip install -e ".[dev]"`:

| Prüfung | Ergebnis |
| --- | --- |
| `ruff check .` | grün |
| `mypy` | grün (20 Dateien) |
| `pytest`, ohne `tests/test_web_overflow.py` | 2 930 bestanden, 3 übersprungen, 0 rot (2:03 min) |
| `black --check .` | **3 Dateien nicht formatiert:** `tests/test_web_pruefschritt.py`, `tests/test_rahmen_im_artefakt.py`, `tests/test_web_rail.py` |
| Browser-Wächter `tests/test_web_overflow.py` | **nicht gelaufen** (braucht Playwright, siehe Block 0) |

Eine ältere Editable-Installation (vor P4.6) lässt `tests/test_packaging.py::TestDieInstallationLiefertDasPaketSrc` rot werden. Das ist ein Umgebungsproblem und kein Befund am Branch; nach `pip install -e ".[dev]"` ist der Test grün.

## Vorgehen

Von billig und mechanisch zu teuer und urteilsabhängig. Die Blöcke 2, 3 und 5 sind unabhängig und lassen sich parallel vergeben. **Jeder Befund** kommt mit Fundstelle (Commit oder Datei:Zeile) und Beleg ins Protokoll (Block 7); «sieht richtig aus» ist kein Beleg.

### Block 0 — Grundlinie

1. Frischer Checkout, `pip install -e ".[dev,ui]"`, `python -m playwright install chromium`.
2. `ruff check .`, `black --check .`, `mypy`, `pytest -q` (Suite ohne Ausnahmeliste, seit P4.2).
3. `npm install && npm run build:css`, danach `git diff --exit-code dashboard/web/assets/00-tailwind.css`: Das eingecheckte Stylesheet muss dem Quelltext entsprechen.
4. `pytest tests/test_web_overflow.py` **allein** auf einer sonst ruhigen Maschine (laut Plan rund 8:36 min beim letzten Lauf; bei Last scheitert er an Timeouts, ohne dass es ein Befund wäre).
5. Den Linux-Lauf des Workflows `.github/workflows/browser.yml` abwarten: Die Deckel sind unter Windows erhoben, und ob sie sich übertragen, ist ungeprüft (CLAUDE.md, Dev-Workflow).

**Fertig wenn:** alle fünf grün, oder jede rote Zeile ist einem Befund zugeordnet.

### Block 1 — Prozess und Commit-Regeln

1. **Regel 3 (Test und Doku im selben Commit):** die elf Commits ohne Test einzeln durchgehen. Bei den fünf ohne Doku prüfen, ob die Message den Grund nennt (die Ausnahmeklausel).
2. **Regel 4 (Refactoring und Verhaltensänderung getrennt):** die 34 `refactor`-Commits stichprobenartig gegen ihren Diff lesen, besonders `refactor(sweeps)` und `refactor(config)` aus P5.1.
3. **Regel 2 (jeder Commit für sich grün):** `git rebase --exec "ruff check . && black --check . && pytest -q -x"` über die 147 Commits nur des Branchs, oder mindestens an den Paketgrenzen. `black` ist am Spitzenstand schon rot.
4. Die doppelten Titel klären (siehe oben) und den Branch-Zuschnitt entscheiden.

### Block 2 — Löschungen (Phase 5)

1. `dashboard/legacy_streamlit/` und `src/legacy/`: mit `grep` über Code, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, CI, `README.md` und `docs/handbuch/` nach übrig gebliebenen Verweisen suchen. `tests/test_launcher_vertrag.py` darf keinen alten Import mehr sehen.
2. Die «sieben Namen, auf die nichts verweist» und die Funktionen, die «nur ihr eigener Test am Leben hielt»: Kann sie ein dynamischer Zugriff erreichen (`getattr`, Namen als Zeichenkette in Config oder JSON)? Ein statisches `grep` findet das nicht.
3. **Verhaltensänderungen, die Nutzer treffen** — jeweils prüfen, ob README und `docs/handbuch/ref-ausgaben.md` bzw. `ref-config.md` mitgezogen sind:
   - `--sweep` ist weg (die CLI bricht ab, statt still den Standardlauf zu rechnen).
   - `round_history.json` zeigt jede Runde statt überall den Endzustand.
   - `compute_ticket_price` heißt jetzt `compute_base_cost`.
4. Die drei gelöschten Tests: Ist die jeweilige Zusage durch einen anderen Test gehalten? Nachweis per Mutation (Zusage brechen, Test muss rot werden).

### Block 3 — Engine-Zahlen (Phase 2 und 3)

Das riskanteste Stück, weil es Zahlen bewegt, die nach außen gehen.

1. **P2.10 bis P2.13:** Jede im Plan und in CLAUDE.md genannte Zahl selbst nachmessen, nicht gegen den Text vergleichen. Beispiele: Standardlauf 0,264167 / 120,13 (P2.12), F6 kippt in 105 von 111 Wechseln (P2.13).
2. **P2.12 fachlich:** Einkommen wirkt jetzt im Nutzen. Der Backtest wird auf der Nachfrageseite schlechter (22,47 → 24,85) und ist trotzdem «behalten wegen des Mechanismus». Das ist eine Modellentscheidung und gehört als Frage an Haiko ins Protokoll, nicht als Befund.
3. **Backtest:** `docs/backtest_vorlauf.md` neu erzeugen und mit dem eingecheckten Stand vergleichen.
4. **Mutationsprobe der tragenden Wächter:** Zusage brechen, Test muss rot werden.
   - `tests/test_faktoren_flattern_nicht.py`
   - `tests/test_ein_tick_ist_ein_monat.py`
   - `tests/test_buchung_zieht.py`
   - `tests/test_preisstrategie_ist_eine_wahl.py`
   - `tests/test_lauf_argumente.py`
5. **`docs/audit_phase3_2026-09-05.md`:** Jedes der zwölf Pakete stichprobenartig gegen den Code prüfen. Das Audit selbst nennt seine Einschränkung: Dieselbe Sitzung hat gebaut und geprüft, es ist **nicht unabhängig**.
6. **P3.8 (Tick = Monat):** Rahmenszenarien und Standard-Config auf Raten je Tick prüfen (`test_ein_tick_ist_ein_monat.py` misst das; hier gegenlesen, ob die Messung das Richtige findet).

### Block 4 — Testfundament, Typen, Register (Phase 4)

1. `tests/test_testfundament.py` und `tests/test_doku_zahlen.py`: Jeder Ankersatz aus CLAUDE.md und `dashboard/web/app.py` muss noch im Text stehen und die Messung ihn belegen. Das Register hält nur, was eingetragen ist; Zahlen ohne Eintrag sind ungeprüft.
2. `pyproject.toml`: Deckt die `mypy`-Dateiliste die Grenzen aus Invariante 4 (Modelle und Module, die `RunArgs`/`SimulationState` erzeugen oder lesen)?
3. **P4.5:** Sind die Rahmenszenarien auf 120 Ticks gestreckt, ohne dass eine Marke oder Endlage kippt? Ist jede Kohärenzbegründung gegen ihre Quelle neu gelesen?
4. **P4.6:** `pip install -e .` aus einem fremden Verzeichnis (der Test tut das; einmal von Hand gegenprüfen).

### Block 5 — Oberfläche (Phase 7)

Der größte Block. **Im laufenden Dashboard prüfen** (`python -m dashboard.web.app --port 8511`), nicht nur im Diff.

1. **P7.1 Gestaltungssystem:** Regel 4 (keine rohe Farbe, keine Tailwind-Farbklasse), Hell und Dunkel durchklicken; `tests/test_web_theme.py` gegenlesen.
2. **P7.2 Produktsprache:** Text ohne rohes Markdown, ohne Verweise auf entfallene Schritte, Browser-Titel nennt Marke und Bereich.
3. **P7.3 Rahmen und Navigation:** Sprunglink zuerst, Bereichsansage, Fokus auf die Überschrift, per Tastatur bedienbar (`tests/test_web_a11y.py`).
4. **P7.4 Einrichten und P7.13 Verläufe:**
   - Regel 7: nur der Modell-Editor schreibt in `configs/` (`TestNurDasModellSchreibtInsModell`).
   - «Modellannahmen» gilt je Lauf und ändert das Modell nicht.
   - Ein Szenariowechsel verwirft die Abweichungen, mit «Rückgängig».
   - Startwerte und Verläufe wirken nur gespeichert, mit Speicherweg.
5. **P7.5 Leitstand:** Faktorleiste ohne gekürzte Namen, Ereignisstreifen mit Legende, Veränderung als neutraler Pfeil, Sparklines mit Einheit.
6. **Regeln 1, 2 und 6 des Dashboards:** eine ID nur an einer Stelle; Werte fließen nur vom Feld in den Store; ein fehlender `Input` legt den Callback lahm. Die Ausnahme des Modell-Bereichs (P3.12) darf keine feste ID bekommen.
7. **Schmale Breite (375 px)** und die Browserkonsole auf `nonexistent object`-Meldungen.
8. **Handbuch:** die 21 geänderten Dateien unter `docs/handbuch/` gegen die neue Oberfläche lesen.
9. **Offen laut Plan:** P7.6 bis P7.10 und P7.11 (der Klick-Deckel ist gerissen). Prüfen, ob der Plan das ehrlich sagt und ob der Branch-Stand sich damit verträgt.

### Block 6 — Doku gegen Code

1. Die Tabelle «Doku-Pflicht» aus CLAUDE.md auf jeden Commit anwenden; die Lücken aus Block 1 sind der Anfang.
2. CLAUDE.md gegen den Code lesen. Jede Zahl darin ist eine Behauptung, die über den heutigen Stand spricht; datierte Messungen sind Geschichte und werden bewusst nicht gehalten.
3. `docs/projektplan.md`: Die Stand-Zeile und jede Erledigt-Marke gegen Code und Tests belegen. Auffällig ist P7.0, das als offen geführt wird, obwohl P7.1 bis P7.5 als erledigt gelten.
4. `docs/audit_findings.md`: Behobene Findings entfernt, neue ergänzt?
5. Tote Anker: Verweise in `docs/` und CLAUDE.md auf Überschriften, die es nicht mehr gibt (der Durchgang durch Phase 2 vom 2026-09-02, Commit `9a5f72c`, fand davon 19).

### Block 7 — Befundprotokoll

Ein Protokoll (neue Datei `docs/audit_gegenpruefung_<Datum>.md` nach Abschluss), jeder Befund in genau einer Klasse:

- **Blocker** — rot, falsche Zahl oder eine Doku, die etwas behauptet, was der Code nicht tut.
- **Nachbesserung** — Verstoß gegen eine Regel des Projekts, Verhalten ist aber richtig.
- **Frage an Haiko** — fachliche oder Produktentscheidung, kein Fehler.
- **Notiz** — nichts zu tun, aber festhaltenswert.

Dazu eine Empfehlung: ein PR oder zwei (Phase 5 und Phase 7), und was vor dem Merge passieren muss.

## Aufwand

Rund 14 bis 16 Stunden, davon Block 5 vier bis fünf, Block 3 drei, Block 2 und 6 je zwei.

## Was dieser Plan nicht abdeckt

- **`main` vor `aff7d63`:** nicht Teil der Prüfung.
- **Rechtstexte der Landingpage:** bekannte Restposition aus Phase 1, hier nicht bewertet.
- **Fachliche Richtigkeit der Modellannahmen** (Koeffizienten, Kohärenzbegründungen): Der Plan prüft, ob Zusage und Messung zusammenpassen, nicht ob die gesetzten Werte fachlich stimmen. Das bleibt Sache eines Fachprüfers.
