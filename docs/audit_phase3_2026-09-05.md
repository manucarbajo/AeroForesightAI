# Audit der Phase 3 — Engine-Härtung

**Prüfung der eigenen Umsetzung · 2026-09-05 · Codestand `b46cafc` (`feat/phase-3-engine-haertung`)**

Geprüft wurde dasselbe wie bei [Phase 2](audit_phase2_2026-09-03.md), in derselben
Trennung: **hält jedes Paket seine eigene Zusage** (Teil A), und **hält die
Umsetzung einer Prüfung stand, die den Projektplan nicht als Maßstab nimmt**
(Teil B) — Korrektheit, Sinnhaftigkeit, Effizienz. Dazu Doku- und
Prozesskonformität (Teil C) und, als eigener Teil, das **Werkzeug**, mit dem
dieses Audit seine fehlende Unabhängigkeit ersetzt (Teil D).

## Vorbemerkung: dieses Audit ist nicht unabhängig

Phase 2 hat jemand geprüft, der sie nicht gebaut hat. Hier fällt beides
zusammen — dieselbe Sitzung, die die zwölf Pakete umgesetzt hat, prüft sie. Das
ist ein struktureller Mangel und keine Formalie: **Wer eine Zusage
aufgeschrieben hat, sucht nicht mit demselben Eifer nach ihrer Lücke**, und er
kennt die Stellen, an denen er beim Bauen weggeschaut hat, nicht als Lücken,
sondern als Entscheidungen.

Ersetzt lässt sich das nicht. Gemildert wurde es durch **Verfahren statt
Absicht**, auf drei Weisen, die von innen möglich sind:

1. **Jeder tragende Wächter wurde absichtlich kaputtgemacht** und musste rot
   werden — fünfzehn Mutationen, eine je Zusage (Teil D). Ein Wächter, der eine
   gebrochene Zusage nicht meldet, ist der teuerste Zustand: Er kostet Vertrauen,
   ohne Schutz zu liefern. Das ist die Lehre der Phase selbst, hier auf sie
   angewandt.
2. **Jede in die Doku geschriebene Zahl wurde ohne Rückgriff auf ihre Herkunft
   neu gemessen** — nicht nachgelesen, wie sie zustande kam, sondern von vorn
   erhoben.
3. **Geprüft wurde am laufenden System**, nicht am Quelltext, der die Zusage
   behauptet: die CLI wirklich mit einem fremden Checkpoint gestartet, ein
   Dashboard-Lauf wirklich gerechnet und sein Artefakt gelesen.

Was das **nicht** ersetzt: einen Prüfer, der die Absichten nicht kennt. Wer
diesem Dokument ein Gewicht gibt, gibt es dem Verfahren, nicht der
Selbsteinschätzung.

**Nachgemessen, nicht gelesen.** Jede Zahl unten stammt aus einem Skript im
Anhang. **Sechs Messungen mussten ihren ersten Anlauf verwerfen, weil der
Prüfling falsch war und nicht der Prüfgegenstand** — das steht jeweils dabei,
weil ein Audit, das nur seine Treffer zeigt, seine eigene Trefferquote
überzeichnet.

---

## Urteil in vier Sätzen

**Phase 3 hält, was sie zusagt, und ihre Zusagen sind prüfbar gebaut.** Elf von
zwölf Paketen sind umgesetzt, das zwölfte ist mit Grund zurückgestellt; alle
fünfzehn tragenden Wächter gehen rot, wenn man ihre Zusage bricht, und die
Ende-zu-Ende-Proben an CLI, Checkpoint und Dashboard-Artefakt bestätigen die
veröffentlichten Aussagen.

**Die Befunde aus Phase 3 sind alle von einer Sorte, und keiner ist ein
Rechenfehler:** eine abgeschaffte Notlösung, die eine Ebene über ihrer
Abschaffung weiterlebt (B1), ein Fehlerweg, der selbst noch scheitern kann (B2),
eine Signatur, die ihrem eigenen Rumpf widerspricht (B3), und ein Kriterium,
dessen Wächter fast das Doppelte durchlässt (B4) — **kein Befund berührt die
Zahlen eines Laufs**, nicht den Preis, nicht die Buchungsrate, nicht die
Faktorlage.

**Den einen schweren Befund hat Phase 3 nicht verursacht, sondern gefunden** (B6,
auf `main` identisch nachgemessen): Der Browser-Wächter ist mit **112 zu 6** rot,
das Audit der Phase 2 hat genau diese sechs Tests als C5 mit ⛔ geführt und am
2026-09-03 behoben — und Commits desselben Tages haben den Fix ungültig gemacht,
ohne dass es jemand sah. **C5s eigentlicher Befund ist damit zum zweiten Mal
eingetreten:** ein opt-in-Wächter, der sich schweigend überspringt, hält seine
Zusagen nicht.

**Was ausdrücklich nicht beanstandet wird:** dass drei Pakete ihre eigene erste
Ursachenzuschreibung verworfen haben, nachdem eine Messung widersprach — bei
P3.9/P3.12 zweimal hintereinander, das zweite Mal gegen einen Schluss, den diese
Sitzung selbst gezogen hatte.

---

## Prüfstand

| | |
| --- | --- |
| **Codestand** | `b46cafc`, Arbeitsbaum sauber, `.venv` nach Konvention |
| **Statisch** | vollständige Lektüre von `run_simulation.py`, `validation.py`, `logging_setup.py`, `checkpoint_manager.py`, `property_engine.py`, `llm/defaults.py`, `llm/studio_helpers.py`, `models/run_models.py`, `scenario_sweeps.py`, `dashboard/run_launcher.py`, `dashboard/config_catalog.py`, `web/pages/model_editor.py`, `web/config_editor/__init__.py`; alle sieben neuen Testdateien |
| **Dynamisch** | zehn Messskripte (Anhang): Mutationsprobe über fünfzehn Zusagen, Hohlheitsprobe über elf Testdateien, CLI gegen zwei fremde Checkpointformen, CLI-LLM-Validierung in drei Varianten, Preflight-gegen-Lauf-Divergenz, Checkpoint-Rundlauf, Dashboard-Lauf mit Artefaktlesung, Regelarten-Probe über drei Listen, Zeichensatz-Zählung in vier Definitionen, Ankerprobe über 491 Überschriften |
| **Suite** | `pytest` ohne die zwei dokumentierten Ollama-Hänger und ohne den Browser-Wächter: **1641 passed, 1 skipped, 2 deselected** in 2:17 — **kein Fehlschlag** |
| **Browser-Wächter** | `tests/test_web_overflow.py`: **112 passed, 6 failed** in 22:17. Die sechs sind **nicht aus Phase 3** — auf `main` (`af71a3f`) in einem eigenen Arbeitsbaum identisch nachgemessen. Sie sind trotzdem ein Befund → **B6** |
| **Linter** | `ruff check .` grün · `black --check .` grün (250 Dateien) |
| **Am Repo verändert** | keine Datei bleibt verändert. Die Mutationsprobe schreibt in dreizehn Dateien und nimmt jede Änderung in einem `finally` zurück; `git diff` ist danach leer. Ein Probelauf hat ein Verzeichnis in `outputs/` angelegt und wurde entfernt — weil der Höhen-Deckel des Browser-Wächters an dessen Inhalt hängt |

---

## Teil A — Abgleich gegen den Projektplan

| Paket | Zusage gehalten? | Nachweis / Befund |
| --- | --- | --- |
| **P3.1** Laufzeitwerte in `when` | ✅ | An **allen drei** Regelarten gemessen abgewiesen (`factor_rules`, `shift_rules`, `regulatory_influences`), zwei gesperrte gegen 14 erlaubte Größen; das Vokabular liegt beim Mechanismus |
| **P3.2** Checkpoint-Version | ✅ | Rundlauf schreibt und liest Version 2; **beide** fremden Formen (keine Metadaten, Version 99) über die CLI abgewiesen, Exitcode 2, kein Traceback |
| **P3.3** Fehlermeldungen greifen | ✅ mit Befund | `try: pass` weg, CLI-Traceback weg, beides mutationsgeprüft — aber der Ausweichpfad des Schreibers kann selbst scheitern → **B2**; Kopfzeile → **C2** |
| **P3.4** LLM-Konfiguration aus einer Quelle | **teilweise**, als ✅ geführt | CLI-Validierung greift in drei Varianten; `state.config.llm` wird benutzt — aber der abgeschaffte Rückfall lebt eine Ebene höher weiter → **B1**, **B5a** |
| **P3.5** Stille Klemmungen, acht `print()` | ✅ | Vorher 8 `print()` im Scheduler (git-belegt), heute 0; Klemmung und `print` je mutationsgeprüft; der Wächter prüft zusätzlich **allgemein**, dass ein ganzer Lauf auf `stdout` still ist |
| **P3.6** Vertrag für den Launcher | ✅ | Über **alle** Wurzeln nachgezählt: `dashboard/`, `scripts/`, `langgraph_studio/` greifen an **keiner** Stelle in Unterstrich-Namen aus `src/`; nur Tests tun es, was zulässig ist |
| **P3.7** Legende unter der Zeichenfläche | ✅ | Teil 8 des Browser-Wächters ist **grün** — 16 Zusagen über vier Aussagen und beide Modi, im vollständigen Lauf mitgeprüft |
| **P3.8** Tickdauer | ⏸️ zurückgestellt mit Grund | Der Grund trägt: eine Festlegung verlangt die Umparametrisierung genau der Größen, an denen P2.7 misst. `tests/test_tickdauer_ist_uneinheitlich.py` hält den Befund |
| **P3.9** Klickkosten | ✅ mit Befund | Kette gekürzt und mutationsgeprüft; das Kriterium «unter 500 ms» ist gemessen erfüllt, aber sein Wächter deckelt bei 900 → **B4**, und der Docstring der Messung nennt noch die alten Zahlen → **C3** |
| **P3.10** Zeichensatz der Konsole | ✅ | Der Wächter zählt **jeden** `__main__`-Block auf und verlangt Sicherung oder einen begründeten Eintrag in `AUSNAHMEN`; 11 von 16 sichern, die 5 übrigen sind die drei dokumentierten `scripts/*` plus die abgelöste Streamlit-UI. Zahl der Zeichenketten → **C1** |
| **P3.11** Lauf-Argumente als Vertrag | ✅ mit Befund | `compute_mode` kommt am Artefakt richtig an (`mock_llm` in einem echt gerechneten Dashboard-Lauf); kein handgebauter Namensraum und kein `getattr(args, …)` mehr in den Schreibern — aber eine Signatur widerspricht ihrem Rumpf → **B3** |
| **P3.12** Modell-Bereich entsteht beim Aufsuchen | ✅ | Beide Zusagen mutationsgeprüft (eifriger Aufbau **und** feste ID im Rumpf gehen rot); die zwei zuvor hohl gewordenen Wächter zeigen wieder auf `rumpf_fuer(...)` |

**Kein Paket trägt ein ✅, dessen Kern nicht hält.** Die vier Befunde in dieser
Tabelle sitzen alle am Rand ihrer Zusage, nicht in ihrer Mitte — das ist der
Unterschied zu Phase 2, wo P2.8s tragende Zusage von den eigenen Zahlen
widerlegt wurde.

---

## Teil B — Unabhängige Prüfung

### B1 · Der abgeschaffte Rückfall lebt eine Ebene über seiner Abschaffung 🔶 **mittel, Zusage**

P3.4 hat in `config_catalog.llm_config_from_draft` einen Rückfall entfernt und
mit einem Kommentar versehen, der ihn ausdrücklich zum Befund erklärt:

> **Kein Rückfall auf einen Vorgabewert.** Ein leeres Modellfeld ist ein Befund
> und keine Gelegenheit, `llama3.2` einzusetzen […]

Zwanzig Zeilen weiter, in `dashboard/run_launcher.py:144`, steht er noch:

```python
model=draft.model.strip() or DEFAULT_MODEL,
```

**Gemessen** (Anhang 5), mit einem geleerten Modellfeld und `mock_llm = False`:

| Weg | `RunLaunchConfig.model` | `state.config.llm.model` | Befund der Validierung |
| --- | --- | --- | --- |
| **Preflight** (`start_flow` → `prepare_simulation_state(entwurf)`) | — | `''` | «Sprachmodell: Modellname darf nicht leer sein» |
| **Lauf** (`launch_from_draft` → `draft_to_launch_config` → zurück) | `'llama3.2'` | `'llama3.2'` | **keine** |

Der Rundlauf **wäscht** den erfundenen Wert: `draft_to_launch_config` setzt ihn,
`launch_config_to_draft` baut daraus wieder einen Entwurf, und der ist von einem
Entwurf, in dem jemand `llama3.2` eingetippt hat, nicht mehr zu unterscheiden.
`_build_llm` trägt dazu den Docstring «Der Client aus **derselben** Ableitung,
die auch den Zustand füllt» — die Ableitung ist dieselbe, ihre **Eingabe** ist es
nicht.

**Auswirkung.** Der Preflight sagt «Modellname darf nicht leer sein», und ein
Lauf, der trotzdem zustande kommt, rechnet mit `llama3.2` und schreibt diesen
Namen in `state.config.llm` und damit ins Artefakt. Das ist dieselbe Klasse wie
P1.9-W5.1 (ein Literal als zweite Quelle für einen Vorgabewert) und wie P2.11
(zwei Quellen für denselben Wert) — nur eine Ebene über der Stelle, an der P3.4
sie beseitigt hat. **Praktisch abgeschirmt** ist es heute durch das Tor aus
P1.9-W2.2, das «Lauf starten» bei jedem Befund sperrt; die Abschirmung liegt
aber in der Oberfläche und nicht im Service-Layer, den auch andere aufrufen.

**Warum es beim Bauen durchkam:** Ich habe `llm_config_from_draft` geschrieben
und dabei `draft_to_launch_config` gelesen — als Datenübergabe, nicht als
Ableitung. Die Zeile steht zwischen dreißig gleichförmigen Feldzuweisungen.

**Was zu tun ist:** `model=draft.model.strip()` — ohne `or`. Der Wächter dazu ist
kein neuer Test, sondern eine Erweiterung von `tests/test_llm_defaults.py`:
Derselbe leere Entwurf muss auf **beiden** Wegen denselben Modellnamen ergeben.

> **Behoben noch am 2026-09-05 (P3.13).** Und der Befund war größer als hier
> beschrieben: `availability` erfand nicht nur den Modellnamen (B5a), sondern
> zwei Zeilen darüber auch die **Adresse** — und das war der schlimmere Fall,
> weil dann eine erfundene Adresse angepingt wurde und ihr Ergebnis darüber
> entschied, ob «Mit Sprachmodell» als möglich angezeigt wird. Vier Rückfälle
> statt zwei, alle weg, alle vier mutationsgeprüft. Der tragende Wächter prüft
> nicht den Fall, sondern den **Mechanismus**: Die Rundreise
> `draft_to_launch_config` → `launch_config_to_draft` muss auf `model` **und**
> `base_url` ein Festpunkt sein — genau dort wäscht ein `or DEFAULT_…` einen
> erfundenen Wert zu etwas, das wie eine Eingabe aussieht.

### B2 · Der Fehlerweg kann selbst noch scheitern — und sein Wächter teilt die Annahme 🔶 **mittel, Fehlerweg**

P3.3 hat `_schreibe` gebaut, damit eine Befundliste auch dann erscheint, wenn die
Konsole `cp1252` spricht. Der Ausweichpfad lautet:

```python
except UnicodeEncodeError:
    kodierung = sys.stderr.encoding or "ascii"
    roh = zeile.encode(kodierung, errors="backslashreplace")
    sys.stderr.buffer.write(roh + b"\n")
```

Er setzt `sys.stderr.buffer` voraus. **Gemessen** (Anhang 6) an zwei Strömen, die
beide `cp1252` melden:

| Strom | Ergebnis |
| --- | --- |
| mit `.buffer` (wie eine echte Konsole) | hält, schreibt mit `backslashreplace` |
| ohne `.buffer` (wie ein vorgeschalteter Tee) | **`AttributeError: 'OhneBuffer' object has no attribute 'buffer'`** |

Aus dem `UnicodeEncodeError` wird ein `AttributeError` — ein Traceback an genau
der Stelle, an der dieses Paket einen weggeräumt hat. Der Docstring von
`_melde_befunde` sagt es selbst: *«Ein Fehlerweg, der selbst scheitern kann, ist
keiner.»*

**Und der Wächter teilt die Annahme.** Alle drei Tests des Fehlerwegs in
`tests/test_zeichensatz.py` lesen ihr Ergebnis über `strom.buffer.getvalue()` —
sie **brauchen** einen Puffer und können den pufferlosen Fall deshalb nicht
sehen. Das ist die Fehlerart, die diese Phase dreimal gefunden hat, hier in
ihrem eigenen Wächter: Prüfling und Prüfer haben dieselbe Voraussetzung.

**Auswirkung, ehrlich eingegrenzt.** Damit es zuschlägt, braucht es drei Dinge
gleichzeitig: einen `stderr`-Wrapper ohne `.buffer`, einen Befundtext mit einem
Zeichen außerhalb `cp1252`, und einen Strom, der `cp1252` spricht. Heute leitet
das Projekt `stderr` **nirgends** um (nachgezählt), und `stdio_auf_utf8()` läuft
als erste Anweisung in `_main`. Der Pfad ist also die Reserve für den Fall, den
`stdio_auf_utf8` ausdrücklich offenlässt: ein Strom, der die Umstellung
verweigert — dafür warnt sie, statt zu scheitern. Genau in diesem Fall greift der
Ausweichpfad, und genau dort kann er umfallen.

**Was zu tun ist:** `puffer = getattr(sys.stderr, "buffer", None)`, und ohne
Puffer die ersetzte Zeichenkette durch `write` schicken. Dazu ein vierter Test
mit einem Strom **ohne** `.buffer`.

> **Behoben noch am 2026-09-05 (P3.14) — und einfacher als hier vorgeschlagen.**
> Es steht **kein** `getattr(..., "buffer", None)` dort: Der Umweg über die Bytes
> war von Anfang an überflüssig. `backslashreplace` ersetzt genau die Zeichen,
> die die Kodierung nicht kann, durch ASCII-Escapes — was übrig bleibt, ist per
> Konstruktion schreibbar und geht durch dieselbe `print`-Zeile wie der
> Normalfall. Die Abhängigkeit ist nicht abgefangen, sondern weg; `flush()` als
> zweite Attributabhängigkeit ebenso.
>
> **Der Befund war größer als beschrieben.** Oben steht «alle drei Tests teilen
> die Annahme» — richtig ist etwas Schlimmeres: Der **eine** Test, der wirklich
> den Ausweichpfad anfasst (die drei in `test_zeichensatz.py` prüfen
> `stdio_auf_utf8`, nicht `_schreibe`), hat seine Zusage **nie** geprüft. Er
> ersetzte `builtins.print` durch eine cp1252-werfende Fassung, ließ `sys.stderr`
> aber das Auffangobjekt von `capsys`, dessen `encoding` **utf-8** ist — der
> Ausweichpfad kodierte also nach utf-8, wo `backslashreplace` nichts zu
> ersetzen hat. Nachgemessen geschrieben wurde `'… cost_pressure ≥ 0,8 …'`, und
> `"u2265"` war nicht enthalten; durchgegangen ist er über das zweite Glied
> seiner eigenen Bedingung (`assert "u2265" in ausgabe or "≥" in ausgabe`).
> Ersetzt durch eine Parametrisierung über beide Bauformen, drei Mutationen
> geprüft. **Zwei Lehren stehen als Kommentar an seiner Stelle:** Eine Attrappe,
> die an einer Stelle scheitert und an der anderen so tut, als sei alles in
> Ordnung, prüft die Verbindung dazwischen nicht — und eine `or`-verknüpfte
> Zusage prüft im Zweifel die lockerere Hälfte.

### B3 · `sweep_metadata_args` sagt `SimpleNamespace` und liefert `RunArgs` 🔶 **mittel, Vertrag**

P3.11 hat diese Funktion von einem Namensraum auf `RunArgs` umgestellt und dabei
das tote Feld `sweep` entfernt. Die Signatur ist mitgezogen worden — nicht.
**Gemessen** (Anhang 7):

| Frage | Antwort |
| --- | --- |
| Rückgabe-Annotation | `SimpleNamespace` |
| tatsächliche Rückgabe | `RunArgs` |
| Parameter | `['sweep_id']` |
| davon im Rumpf benutzt | **keiner** |
| `SimpleNamespace` erscheint in Zeile | 18 (Import) und 232 (Annotation) — sonst nirgends |
| zwei verschiedene `sweep_id` ergeben | **identische** Argumente |

Drei Dinge auf einmal: Die Annotation sagt das Gegenteil des Rumpfs; der
Parameter wird ignoriert, seit sein einziger Verwender (`sweep=sweep_id`)
entfallen ist; und die falsche Annotation hält den Import `from types import
SimpleNamespace` am Leben, weshalb `ruff` schweigt — **`ruff check .` ist grün**.

**Warum das mehr ist als Kosmetik.** Invariante 4 verlangt Pydantic-Typisierung
an den Grenzen; ihre Durchsetzung hängt daran, dass die Typangabe stimmt. Hier
sagt sie einem Leser und jedem Werkzeug, das Rückgabetypen auswertet, es käme ein
formloser Namensraum heraus — die genaue Aussage, gegen die P3.11 angetreten ist.
**Strukturelle Ursache:** Das Projekt hat keinen Typprüfer (nachgesehen:
`pyproject.toml` und die CI nennen weder mypy noch pyright), und `ruff` prüft
Annotationen nicht gegen `return`.

Der unbenutzte Parameter ist dabei die schwächere Hälfte des Befunds — es gibt im
selben Zweig eine Stelle, an der ein unbenutzter Parameter **richtig** ist:
`model_editor.layout(draft)` behält ihn bewusst und sagt im Docstring, warum.
Hier steht kein solcher Satz, und die Aufrufer übergeben eine Kennung in der
Annahme, sie werde verwendet.

**Was zu tun ist:** `-> RunArgs`, Import weg, und `sweep_id` entweder benutzen
oder entfernen — mit einem Satz dazu, welches von beidem gemeint ist. Und als
eigenes Paket: einen Typprüfer für `src/models/` und die Grenzen aufsetzen, sonst
ist dies der erste von vielen.

> **Behoben noch am 2026-09-05 (P3.15).** `-> RunArgs`, Import weg, `sweep_id`
> **entfernt** statt behalten: Sieben Aufrufstellen und kein Grund — ein
> Parameter, der das Ergebnis nicht ändern kann, ist dieselbe Lüge wie die
> Annotation, nur eine Klammer weiter. Der Wächter sucht die Erzeuger, statt sie
> aufzuzählen (jedes `return`, das ein `RunArgs` liefert, muss es in der Signatur
> sagen); vier Mutationen geprüft, darunter eine Lüge an einem **zweiten**
> Erzeuger — er greift also nicht nur an der gemeldeten Stelle.
>
> **Die Klasse bleibt offen und hat ein Paket:**
> [P4.4](projektplan.md#p44--ein-typprüfer-für-die-grenzen--offen-neu-2026-09-05-aus-p315).
> Dieser Wächter deckt eine Familie ab, weil genau die einen Schaden angerichtet
> hat. Die Zahl, die das Ausmaß der Lücke beschreibt: **zwölf Tage** stand die
> Lüge in einer Datei, die zweimal angefasst wurde, und `ruff check .` war die
> ganze Zeit grün.

### B4 · Das 500-ms-Kriterium hat keinen Wächter auf seiner Höhe 🔶 **mittel, Verfahren**

P3.9s Abnahmeklausel lautet wörtlich:

> **Fertig wenn:** Ein Klick auf einen Schritt kostet **unter 500 ms**, gemessen
> im Browser über alle sechs Schritte — und die Zahl der ausgelösten
> Server-Aufrufe steht als Zahl im Wächter, nicht nur die Dauer.

Die zweite Hälfte ist erfüllt (`KLICK_AUFRUFE_MAX = 7`, mit Sperrklinke in beide
Richtungen). Die erste ist **gemessen** erfüllt — 213 bis 487 ms — aber der
Wächter, der sie hält, deckelt bei `SICHTBAR_MAX_MS = 900`, also fast dem
Doppelten. Ein Rückfall auf 800 ms bliebe grün, während der Plan «das
500-ms-Kriterium ist erfüllt» behauptet.

**Die Begründung für 900 trägt** und steht im Code: Eine ausgelastete Maschine
misst anders, und dieser Wächter wird sonst rot, ohne dass sich etwas geändert
hat. Was nicht trägt, ist die Kombination aus dieser Grenze und einem ✅, das
sich auf eine Einzelmessung stützt. Die Doku-Pflicht sagt dazu: *wer eine Zusage
aufstellt, die jemand später nachprüfen können soll, baut den Wächter, der sie
misst — nicht die Zählung, die sie umgeht.*

**Was zu tun ist**, eines von beidem, nicht beides: entweder den Deckel auf 500
mit einer benannten Toleranz und einer Wiederholung bei Rot, oder im Plan
festhalten, dass das Kriterium **einmal** erreicht wurde und die Sperrklinke bei
900 steht. Die zweite Variante ist ehrlicher und billiger.

### B6 · Der Browser-Wächter ist wieder rot — C5 gilt als behoben und ist es nicht ⛔ **schwer, vorbestehend**

**Nicht aus Phase 3, und das ist nachgemessen und nicht angenommen:** Derselbe
Testlauf in einem eigenen Arbeitsbaum auf `main` (`af71a3f`, mit dem `main`-Code
geladen — nachgeprüft über `__file__` der beiden Module) liefert dieselben Zahlen.
Trotzdem gehört er hierher, weil dieses Audit ihn gefunden hat und weil die
Doku etwas anderes behauptet.

**Der Stand.** 112 bestanden, 6 gescheitert in 22:17:

| Test | Gemessen | Deckel |
| --- | --- | --- |
| `test_no_step_grew_beyond_its_ratchet` `[1280px]` | Schritt 1: **1,96** Schirme · Schritt 6: 1,70 | 1,34 · 1,45 |
| `test_no_step_grew_beyond_its_ratchet` `[1024px]` | Schritt 1: **2,03** Schirme · Schritt 6: 1,61 | 1,42 · 1,45 |
| `test_no_line_runs_longer_than_the_eye_can_follow` `[1280px]` | **109** Zeichen in einem `LI` («docs/research/links.md — EU-ETS / Fit fo…») · **98** Zeichen in einem `P` auf «Prüfen & Starten» («bei Tick 16. Danach hält er seinen letzt…») | 75 |
| `test_the_width_guard_would_notice_a_relapse` `[1280px]`, `[1024px]` | `assert (96,7 >= 60,0 and 109 <= 75)` | — |

Der Selbsttest der Breite scheitert an seiner **Vorbedingung**: Er kann keinen
Rückfall nachstellen, solange der Ist-Stand schon außerhalb liegt.

**Warum das mehr ist als ein rotes Feld.** Das Audit der Phase 2 hat genau diese
sechs Tests als **C5** geführt, mit ⛔ bewertet, die Ursache benannt (P2.0-C hatte
einen Schritt entfernt und die Sperrklinke nicht mitgezogen) und **noch am
2026-09-03 behoben** — der Deckel steht seither auf nachgemessenen Werten, für
Schritt 1 auf **1,34**. `docs/audit_findings.md` führt C5 deshalb nicht mehr.
Heute misst derselbe Schritt **1,96**.

**Und die Ursachen sind neue.** C5s Zeilenlängen-Befund waren 89 Zeichen im
Erklärtext des `apply_custom_overrides`-Schalters. Die 109 Zeichen von heute
stehen in einem **Quellenverzeichnis** («docs/research/links.md — EU-ETS / Fit
for 55…»), die 98 in einem Satz über einen **Verlauf, der vor dem Laufende
aufhört** («bei Tick 16. Danach hält er seinen letzten Wert») — beides Oberfläche,
die am **selben 2026-09-03** dazugekommen ist: die Kohärenzbegründungen mit ihren
Quellen (P2.2/P2.10) und der Hinweis auf die Horizontlücken. Der Fix wurde also
gemessen und **von späteren Commits desselben Tages ungültig gemacht**, und
niemand hat den 22-Minuten-Wächter danach noch einmal gestartet.

**Damit ist C5s eigentlicher Befund zum zweiten Mal eingetreten** — und der
lautete nicht «der Deckel stimmt nicht», sondern: *Der Wächter ist opt-in,
überspringt sich schweigend, und die CI hat keinen Browser; die Zusagen sind
deshalb ungeprüft, ohne dass etwas rot wird.* Innerhalb einer Woche, am selben
Wächter, mit anderen Ursachen. Ein Deckel nachzumessen behebt den Fall; das
Muster behebt nur eine Antwort auf die Frage, **wo dieser Wächter läuft**.

**Was zu tun ist** → [P3.17](projektplan.md#p317--der-browser-wächter-ist-rot-und-niemand-läuft-ihn--offen-2026-09-05).
Zwei Teile, und der zweite ist der wichtigere: die vier konkreten Fehlschläge
nachmessen und zuordnen (Schritt 6 dabei um die Laufhistorie in `outputs/`
korrigieren — das ist ein eigener, schon erfasster Befund), und **entscheiden, wo
der Wächter läuft**, damit die dritte Wiederholung nicht kommt.

### B5 · Kleinere Befunde

**B5a · `availability` nennt ein Modell, das niemand eingestellt hat** 🔷 *behoben (P3.13) — und die Adresse tat es auch, siehe B1*
`dashboard/web/config_editor/compute_mode.py:116` liest
`draft.get("model") or DEFAULT_MODEL` und schreibt den Namen in eine
Nutzermeldung («Modell … nicht vorhanden»). Bei leerem Feld nennt der Preflight
damit `llama3.2` — dieselbe Erfindung wie **B1**, hier ohne Wirkung auf den Lauf,
aber in einem Satz, den jemand liest. Richtig wäre: sagen, dass kein Modell
eingestellt ist.

**B5b · Exitcode 2 teilt sich mit dem Usage-Fehler von argparse** 🔷 *kein
Befund, eine Beobachtung.* `EXIT_KONFIGURATION = 2`, und `argparse` beendet einen
unbekannten Schalter ebenfalls mit 2 (bei der Arbeit an diesem Audit selbst
ausgelöst, mit `--resume-from` statt `--resume`). Die Bedeutung ist in beiden
Fällen dieselbe — «der Aufruf war falsch» —, das README beschreibt 2 als
Konfigurationsfehler und deckt damit beides. Wer die Codes je feiner auflöst,
weiß es jetzt.

---

## Teil C — Doku, Wächter und Prozess

### C1 · «46 Zeichenketten» reproduziert nur unter einer ungenannten Zähldefinition 🔷

Der Plan (P3.3, P3.10) und der Docstring von `_melde_befunde` nennen **46**
Zeichenketten in `src/`, die eine `cp1252`-Konsole nicht schreiben kann.
Nachgezählt (Anhang 9):

| Zähldefinition | Zahl |
| --- | --- |
| alle Zeichenketten-Konstanten | **55** |
| **ohne Docstrings** | **46** |
| verschiedene Zeilen | 54 |
| verschiedene Zeilen ohne Docstrings | 45 |
| betroffene Dateien | 25 |

Die Zahl stimmt — unter «ohne Docstrings», was die sachlich richtige Definition
ist (ein Docstring wird nicht ausgegeben) und die der Text nicht nennt. Wer
nachzählt, bekommt 55 und hält die Doku für veraltet. **Ein Halbsatz genügt.**

Dazu zwei Nebenpunkte:

* Am Branchpunkt standen unter derselben Definition 44; Phase 3 hat zwei
  hinzugefügt. Die 46 war also zum Zeitpunkt des Schreibens richtig und ist es
  heute noch.
* Die Knotenzahlen aus P3.12 sind untereinander um eins verschoben: 2882 − 1404
  = 1478, die Tabelle nennt **1477**. Zwei Messungen an verschiedenen Momenten,
  kein Sachfehler — erwähnt, weil ein aufmerksamer Leser subtrahiert.

*Zur Ehrlichkeit dieser Messung:* Ihre ersten zwei Anläufe zählten falsch — der
erste nur `print`-Argumente (Ergebnis 0), der zweite alle Konstanten
einschließlich Docstrings (55). Erst die dritte Definition traf die des Plans.
Und der erste Anlauf ist über genau den Fehler gefallen, um den es hier geht: Er
lief als eigenes Skript, rief `stdio_auf_utf8()` nicht und brach mit einem
`UnicodeEncodeError` auf `Δ` ab.

### C2 · Die Kopfzeile der CLI ist klein geschrieben 🔷

Nebeneinander, aus zwei Läufen dieses Audits:

```
validierungsfehler:
  - CLI: Endpunkt 'localhost:11434' braucht ein Schema (http:// oder https://) …

Der Zwischenstand passt nicht zu dieser Fassung:
  - Checkpoint 'fremd.json' hat Version 99, dieser Code liest Version 2. …
```

Die Zeichenkette stammt aus `validation.py:661` und ist **älter als dieser
Zweig** — P3.3 hat sie nicht erfunden, sondern zur ersten Zeile befördert, die
ein CLI-Nutzer liest, direkt neben einen ordentlich gebauten deutschen Satz. In
einem Paket, dessen Gegenstand die Lesbarkeit von Fehlermeldungen ist, gehört sie
mitgezogen.

### C3 · Der Docstring der Klickmessung nennt die Zahlen von vor P3.12 🔷

In derselben Datei, 140 Zeilen auseinander:

* `SICHTBAR_MAX_MS` (Zeile 1716 ff.): «gemessen 213 bis 487 ms»
* `test_the_step_shows_up_in_reasonable_time` (Zeile 1855): «P3.9 nennt 500 ms;
  erreicht sind 665–1426.»

P3.12 hat den Kommentar an der Konstante nachgezogen und den an der Testmethode
stehen lassen. Der zweite ist der, den ein Leser zuerst trifft, und er sagt, das
Kriterium sei verfehlt.

### C4 · Ein Doku-Verweis zeigt auf ein Modul, das es nicht gibt 🔷 *vorbestehend*

Eine Ankerprobe über **491 Überschriften in 41 Markdown-Dateien** (Anhang 10)
findet genau einen kaputten Verweis: `docs/projektplan.md:651` verlinkt
`dashboard/web/config_editor/save_start.py` — die Datei existiert nicht (das
Verzeichnis hat 13 Module, keines heißt so). Der Verweis stand schon am
Branchpunkt; Phase 3 hat ihn nicht verursacht und nicht bemerkt. **Alle
Phase-3-Anker lösen auf.**

*Zur Ehrlichkeit dieser Messung:* Ihr erster Anlauf meldete zwei kaputte
Verweise. Der zweite war meiner — meine Slug-Regel strich den Unterstrich aus
`validate_config`, den GitHub behält.

### C5 · Die Findings-Liste ist regelkonform gepflegt ✅

`docs/audit_findings.md` führt die Abschnitte «Validierung / Checkpointing /
Orchestrierung» und «LLM-Anbindung» jetzt **leer** — die Findings sind entfernt
und nicht abgehakt, wie die Doku-Pflicht es verlangt. Kein Eintrag beschreibt
einen Zustand, den Phase 3 beseitigt hat.

---

## Teil D — Die Mutationsprobe

**Was dieses Audit anstelle von Unabhängigkeit hat.** Eine Zusage ist nicht
geprüft, weil ein grüner Test neben ihr steht — sie ist geprüft, wenn ein
**gebrochenes** Versprechen rot wird. Fünfzehn Mutationen, je eine tragende
Zusage, jede einzeln angewandt, der zugehörige Test gelaufen, die Änderung in
einem `finally` zurückgenommen:

| Mutation | Zusage | Ergebnis |
| --- | --- | --- |
| `darf_in_regel_stehen` gibt immer `True` | P3.1 Laufzeitwerte abgewiesen | **rot** |
| `_pruefe_version` nicht mehr gerufen | P3.2 Version wird geprüft | **rot** |
| echter Import durch `pass` ersetzt | P3.3 kein `try: pass` | **rot** |
| `except ValidationError` → `except SystemError` | P3.3 kein CLI-Traceback | **rot** |
| zweites Modell-Literal statt `DEFAULT_MODEL` | P3.4 eine Quelle | **rot** |
| `MockLLM()` vor dem `raise` | P3.4 kein stiller Mock | **rot** |
| `max(3, threshold)` statt `_im_bereich` | P3.5 keine stille Klemmung | **rot** |
| `print("MUTATION")` im Scheduler | P3.5 `logging` statt `print` | **rot** |
| `_melde_befunde` im Launcher importiert | P3.6 nur öffentliche Namen | **rot** |
| `llm_narrative` bekommt einen Vorgabewert | P3.11 Pflichtfeld | **rot** |
| `run_args_from` lässt `llm_narrative` fallen | P3.11 nichts fällt durch | **rot** |
| `stdio_auf_utf8()` aus einem Einstieg entfernt | P3.10 jeder Einstieg sichert | **rot** |
| Import-Seiteneffekt wiederhergestellt | P3.10 keine heimliche Umstellung | **rot** |
| Modell-Rumpf wird eifrig gebaut | P3.12 erst beim Aufsuchen | **rot** |
| feste ID in den Modell-Rumpf | P3.12 nur Muster-IDs (Regel 1) | **rot** |

**Fünfzehn von fünfzehn.** Kein Wächter ist hohl.

*Zur Ehrlichkeit dieser Messung:* Der P3.6-Lauf meldete beim ersten Anlauf
«Muster nicht gefunden» — mein Suchmuster erwartete einen umgebrochenen Import,
in der Datei steht er einzeilig. Aus dem Gedächtnis geschrieben statt aus der
Datei gelesen. Nachgezogen ist er rot.

**Dazu eine Hohlheitsprobe** über alle elf neuen und geänderten Testdateien: kein
`assert` mit einem Generator-Ausdruck, einer wahren Konstante, einem `or True`
oder einem Tupel — der Selbsttest des Durchlaufs erkannte 3 von 3 gepflanzten
Formen. Das ist die syntaktische Hälfte; die semantische — ein Wächter, dessen
Prüfling leer ist — deckt die Mutationsprobe ab, und genau diese Sorte war in
Phase 3 zweimal aufgetreten (die beiden Wächter, die nach P3.12 auf ein leeres
Layout zeigten).

---

## Teil E — Was ausdrücklich gut ist

**Die Ursachenzuschreibung wurde zweimal verworfen, weil eine Messung
widersprach.** P3.9 begann mit der Erklärung des Plans (die Rundläufe), maß sie
und verwarf sie; dann setzte diese Sitzung React über alle fünf Bereiche an die
Stelle, maß im CPU-Profil und verwarf auch das — `dash_renderer` mit 71,6 %. Wer
eine Latenz ohne Profil erklärt, nennt die Ursache, die er erwartet. Dass das
zweimal hintereinander protokolliert ist, samt der eigenen Fehldiagnose, ist mehr
wert als die 213 ms.

**Die Wächter sind Mechanismen, keine Listen.** Sechs der Zusagen dieser Phase
werden von AST-Durchläufen gehalten, die ihren Gegenstand **aufzählen** statt ihn
zu benennen: jeder `__main__`-Block, jeder Unterstrich-Import in `dashboard/`,
jeder `getattr(args, …)` in den Schreibern. Ein neuer Geschwisterfall fällt damit
auf, ohne dass ihn jemand einträgt — bei P3.6 saß der Befund genau dort, wo eine
Liste ihn nie gefunden hätte (ein Import mitten in einem Funktionsrumpf).

**Das Vokabular liegt beim Mechanismus, nicht in der Validierung.**
`darf_in_regel_stehen` steht in `property_engine`, wo die Auflösung passiert —
wie `SHIFT_ZIELE` und `KNOWN_METRICS`. Die Validierung wendet es an. Das ist die
Aufteilung, die P0.4 und P2.4 etabliert haben, konsequent weitergeführt.

**Zwei stumpf gewordene Wächter sind aufgefallen und wurden nachgezogen.** P3.12
hat das Modell-Layout geleert; zwei bestehende Prüfungen (Regel 1, Regel 7)
verglichen daraufhin leere Feldmengen und wären für immer grün gewesen. Dass das
beim Umsetzen bemerkt wurde und nicht in diesem Audit, ist das eigentliche
Qualitätssignal der Phase.

**Ein zurückgestelltes Paket mit tragendem Grund.** P3.8 wird nicht «später»
gemacht, sondern nicht jetzt — weil jede Festlegung der Tickdauer die Größen
umparametrisiert, an denen P2.7 misst, und dem Backtest damit seinen Prüfwert
nähme. Der Befund bleibt gemessen (`test_tickdauer_ist_uneinheitlich.py`), und
ein rotes Ergebnis dort ist eine gute Nachricht.

---

## Befunde nach Schwere

| | Befund | Ort | Auswirkung |
| --- | --- | --- | --- |
| ⛔ | **B6** Der Browser-Wächter ist wieder rot; C5 gilt als behoben | `tests/test_web_overflow.py` | **Vorbestehend, auf `main` identisch nachgemessen.** Schritt 1 der Schrittfolge ist 1,96 Schirme hoch gegen einen Deckel von 1,34, zwei Zeilen laufen 109 und 98 Zeichen gegen 75. Der Fix vom 2026-09-03 wurde von Commits desselben Tages ungültig gemacht — C5s eigentlicher Befund zum zweiten Mal |
| 🔶 | **B1** Der Rückfall auf `llama3.2` lebt eine Ebene höher — **behoben (P3.13)** | `dashboard/run_launcher.py:144` | Preflight und Lauf widersprechen sich bei leerem Modellfeld; das Artefakt nennt ein Modell, das niemand gewählt hat |
| 🔶 | **B2** Der Ausweichpfad des Schreibers braucht `.buffer` — **behoben (P3.14)** | `src/run_simulation.py:556` | Aus `UnicodeEncodeError` wird `AttributeError` — im Paket über Fehlerwege; alle drei Tests teilen die Annahme |
| 🔶 | **B3** Annotation widerspricht dem Rumpf — **behoben (P3.15)**, Klasse offen als P4.4 | `src/orchestration/scenario_sweeps.py:232` | `SimpleNamespace` statt `RunArgs`, `sweep_id` unbenutzt, toter Import bleibt für `ruff` unsichtbar |
| 🔶 | **B4** Das 500-ms-Kriterium hat keinen Wächter auf seiner Höhe | `tests/test_web_overflow.py:1732` | Ein Rückfall auf 800 ms bliebe grün, während der Plan das Kriterium als erfüllt führt |
| 🔷 | **B5a** `availability` nennt ein unkonfiguriertes Modell — **behoben (P3.13)** | `compute_mode.py:116` | Nutzermeldung erfindet `llama3.2` |
| 🔷 | **C1** «46» nur ohne Docstrings | Plan, `_melde_befunde` | Wer nachzählt, bekommt 55 |
| 🔷 | **C2** Kopfzeile klein geschrieben | `validation.py:661` | erste Zeile eines CLI-Fehlers; vorbestehend |
| 🔷 | **C3** Docstring nennt Zahlen von vor P3.12 | `test_web_overflow.py:1855` | sagt, das Kriterium sei verfehlt |
| 🔷 | **C4** Verweis auf `save_start.py` | `projektplan.md:651` | Datei existiert nicht; vorbestehend |

**Aus Phase 3 selbst: kein ⛔.** Zum Vergleich: Das Audit der Phase 2 fand drei
schwere Befunde in der Umsetzung, darunter einen Rechenfehler und eine tragende
Zusage, die von den eigenen Zahlen widerlegt wurde. Der eine ⛔ hier ist
**vorbestehend** und auf `main` nachgemessen — er ist ein Befund dieses Audits,
aber keiner *über* Phase 3.

---

## Empfehlung zur Reihenfolge

0. **B6 zuerst**, weil es das einzige ⛔ ist und weil jeder Tag ohne Antwort auf
   «wo läuft dieser Wächter» die dritte Wiederholung wahrscheinlicher macht. Der
   Fix der vier Fehlschläge ist Handarbeit von einer Stunde; die Entscheidung
   darüber ist wichtiger als der Fix.
1. **B1** danach, und in einem Commit mit seinem Wächter. Es ist der einzige
   Befund, der eine falsche Angabe in ein Artefakt schreiben kann, und der Fix
   ist ein gelöschtes `or DEFAULT_MODEL`. **B5a** gehört in denselben Zug — es
   ist dieselbe Erfindung, nur in einem Satz statt in einem Feld.
2. **B2** danach: zwei Zeilen und ein vierter Test. Klein, aber es ist der
   Fehlerweg, und Phase 3 hat sich selbst zum Maßstab gemacht, dass ein
   Fehlerweg nicht scheitern darf.
3. **B4** als Entscheidung, nicht als Arbeit: ein Satz im Plan oder ein engerer
   Deckel. Fünf Minuten, und danach stimmt das ✅ von P3.9 mit seinem Wächter
   überein.
4. **B3** zusammen mit einem eigenen kleinen Paket «Typprüfer für die Grenzen».
   Die drei Zeilen allein zu reparieren behebt den Fall und nicht die Klasse —
   ohne mypy oder pyright ist die nächste falsche Annotation genauso unsichtbar.
5. **C1 bis C4** in einem Doku-Commit, wenn ohnehin jemand an diesen Dateien
   ist. **C4** ist vorbestehend und gehört in `docs/audit_findings.md`, nicht in
   ein Phase-3-Paket.

**Nicht empfohlen:** P3.8 vorzuziehen. Der Grund für die Zurückstellung ist in
diesem Audit nachgeprüft und trägt.

---

## Anhang — die Messskripte

Alle Skripte laufen im aktivierten `.venv` aus dem Repo-Wurzelverzeichnis. Wo
Ausgabe mit Sonderzeichen entsteht, steht `sys.stdout.reconfigure(encoding="utf-8")`
am Anfang — ein Skript ist **kein** Einstiegspunkt im Sinne von P3.10 und ruft
`stdio_auf_utf8()` nicht; der erste Anlauf von Anhang 9 ist genau daran
gescheitert.

### 1 · Die Mutationsprobe (Teil D)

Der Kern: eine Liste aus (Datei, Suchmuster, Ersatz, Test). Jede Mutation wird
angewandt, ihr Test gelaufen, die Datei **immer** zurückgeschrieben.

```python
def lauf(befehl: str) -> int:
    return subprocess.run(
        rf".venv\Scripts\python.exe -m pytest {befehl} -q --no-header -x",
        shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).returncode

for name, datei, (alt, neu), test in MUTATIONEN:
    p = Path(datei)
    original = p.read_text(encoding="utf-8")
    if alt not in original:
        print(f"{name}: MUSTER NICHT GEFUNDEN")   # ein hohler Prüfling, kein Ergebnis
        continue
    p.write_text(original.replace(alt, neu, 1), encoding="utf-8")
    try:
        code = lauf(test)
    finally:
        p.write_text(original, encoding="utf-8")   # auch bei Abbruch
    print(f"{name}: {'entdeckt' if code else '!! UNENTDECKT'}")
```

**Zwei Dinge, die dabei zu beachten sind.** Erstens: Ein nicht gefundenes Muster
ist **kein** grünes Ergebnis, sondern ein kaputter Prüfling — es muss als solches
gemeldet werden, sonst zählt eine ungeprüfte Zusage als geprüft (genau das
passierte bei P3.6). Zweitens: `read_text`/`write_text` übersetzen unter Windows
Zeilenenden; bei `core.autocrlf=true` und durchgehend CRLF im Arbeitsbaum ist das
folgenlos, und `git diff --numstat` bestätigt es hinterher. **Nachprüfen, nicht
annehmen.**

### 2 · Hohle Zusagen (syntaktisch)

AST-Durchlauf über die elf neuen und geänderten Testdateien; gesucht werden
`assert` mit einem Generator-Ausdruck (immer wahr), einer wahren Konstante, einem
`or True` oder einem Tupel. Mit Selbsttest: drei solche Formen werden in einen
Wegwerf-Baum gepflanzt und müssen gefunden werden.

### 3 · Die CLI gegen zwei fremde Checkpointformen

```bash
python - <<'PY'
import json
json.dump({"clock": {"current_tick": 5}}, open("ohne_metadaten.json", "w"))
json.dump({"metadata": {"checkpoint_version": 99}}, open("fremd.json", "w"))
PY
python -m src.run_simulation --mock-llm --rounds 1 --quiet --resume ohne_metadaten.json; echo $?
python -m src.run_simulation --mock-llm --rounds 1 --quiet --resume fremd.json; echo $?
```

Erwartet und gemessen: eine Befundliste ohne Traceback, Exitcode **2**, und die
Meldung nennt die gelesene gegen die erwartete Version.

### 4 · Die CLI-Validierung der LLM-Angaben

```bash
python -m src.run_simulation --rounds 1 --quiet --model ""                 # leerer Name
python -m src.run_simulation --rounds 1 --quiet --base-url "localhost:11434"  # kein Schema
python -m src.run_simulation --rounds 1 --quiet --base-url ""              # leere Adresse
```

Drei Befunde, dreimal Exitcode 2, jeder mit dem Kontext «CLI:» davor.

### 5 · Preflight gegen Lauf (B1)

```python
draft = default_config_draft(); draft.mock_llm = False; draft.model = ""

state_pre = prepare_simulation_state(draft)                       # der Weg des Preflights
cfg = draft_to_launch_config(draft)                               # der Weg des Laufs
state_run = prepare_simulation_state(launch_config_to_draft(cfg))

print(state_pre.config.llm.model, "|", cfg.model, "|", state_run.config.llm.model)
print([b for b in collect_state_errors(state_pre) if "Sprachmodell" in b])
print([b for b in collect_state_errors(state_run) if "Sprachmodell" in b])
```

Ausgabe: `'' | 'llama3.2' | 'llama3.2'`, ein Befund gegen keinen.

### 6 · Der Fehlerweg an einem Strom ohne `.buffer` (B2)

```python
class OhneBuffer(io.TextIOBase):
    @property
    def encoding(self): return "cp1252"
    def write(self, s):
        s.encode("cp1252")          # wirft bei einem Sonderzeichen
        return len(s)

sys.stderr = OhneBuffer()
_melde_befunde("Probe:", ["Endpunkt braucht ein Schema ≥ http://"])
```

Gegenprobe mit derselben Klasse **plus** `buffer`-Eigenschaft: dann hält der Pfad.

### 7 · Annotation gegen Rumpf (B3)

```python
sig = inspect.signature(sweep_metadata_args)
print(sig.return_annotation, type(sweep_metadata_args("business_as_usual")).__name__)
# Parameter, die im Rumpf nicht als Name vorkommen:
knot = next(n for n in ast.walk(baum) if isinstance(n, ast.FunctionDef)
            and n.name == "sweep_metadata_args")
namen = {n.id for n in ast.walk(knot) if isinstance(n, ast.Name)}
print([a.arg for a in knot.args.args if a.arg not in namen])
```

### 8 · Ein Dashboard-Lauf und sein Artefakt (P3.11)

```python
draft = default_config_draft()
draft.mock_llm = True; draft.rounds = 1
draft.no_protocol = draft.no_scenarios = True; draft.generate_figures = False
ergebnis = launch_from_draft(draft)
meta = json.loads((Path(ergebnis.run_dir) / "run_metadata.json").read_text("utf-8"))
print(meta["compute_mode"], meta["seed"], meta["degraded"])
```

Ausgabe: `mock_llm 42 False`. **Das angelegte Verzeichnis danach entfernen** — der
Höhen-Deckel des Browser-Wächters hängt am Inhalt von `outputs/`.

### 9 · Die Zeichenketten außerhalb `cp1252` in vier Definitionen (C1)

AST-Durchlauf über `src/**/*.py`; je Konstante wird `value.encode("cp1252")`
versucht. Docstrings werden über `id()` des ersten `Expr` in Modul, Klasse und
Funktion erkannt und getrennt gezählt. Für den Vergleich mit dem Branchpunkt
liest derselbe Zähler die Dateien über `git show $(git merge-base HEAD main):…`.

### 10 · Die Ankerprobe (C4)

Sammelt aus allen Markdown-Dateien die Überschriften, bildet den GitHub-Slug und
hält jeden Markdown-Verweis mit `#`-Anker dagegen; Verweise ohne `#` werden als
Dateipfad geprüft.

```python
def slug(titel: str) -> str:
    s = re.sub(r"[`*\[\]()]", "", titel.strip().lower())   # Unterstrich BLEIBT
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")
```

Der Unterstrich ist der Punkt: Wer ihn mitstreicht, meldet jeden Anker mit einem
Bezeichner darin als kaputt — der erste Anlauf hat genau das getan.
