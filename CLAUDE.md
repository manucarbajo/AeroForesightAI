# AeroForesight AI

Hybride Multi-Agenten-Simulationsplattform für strategische Zukunftsplanung im europäischen Luftverkehr. Deterministische Massensimulation (Logit-Modelle für Mikro-Kaufentscheidungen, CIB-Konsistenzfilter nach Weimer-Jehle) liefert die Zahlen, generative KI liefert ausschließlich die narrative Ausdeutung. Drei Akteure — Consumer, Provider, Regulator — interagieren über einen tick-basierten LangGraph-Zustandsgraphen; jeder Lauf erzeugt ein Tripleset aus Trendfortsetzung, Strukturwende und Krisenkonflikt.

Details und Quickstart: [README.md](README.md). Was als Nächstes ansteht und in welcher Reihenfolge: [docs/projektplan.md](docs/projektplan.md).

## Doku-Pflicht

**Gilt für alle im Team und für jede Claude-Session.** Code ohne mitgezogene Doku gilt als nicht fertig. Ein `UserPromptSubmit`-Hook in [`.claude/settings.json`](.claude/settings.json) blendet diese Regel bei jedem Prompt ein, damit sie niemand überliest.

Im selben Commit mitpflegen:

| Wenn die Änderung … | … dann anpassen |
| --- | --- |
| Paketstruktur, Modulzuschnitt oder Datenfluss ändert | **CLAUDE.md** (Architektur-Map) |
| eine Invariante, Konvention oder ein Dev-Kommando betrifft | **CLAUDE.md** (Invarianten bzw. Dev-Workflow) |
| einen Begriff neu einführt oder seine Bedeutung verschiebt | **CLAUDE.md** (Domain-Glossar) + `docs/handbuch/glossar.md` |
| sichtbares Verhalten von Dashboard oder CLI ändert | passende Kapitel in `docs/handbuch/`, bei CLI zusätzlich `README.md` |
| Config-Felder oder Run-Artefakte ändert | `docs/handbuch/ref-config.md`, `docs/handbuch/ref-ausgaben.md` |
| ein Arbeitspaket aus dem Projektplan abschließt oder verschiebt | **`docs/projektplan.md`** (Stand-Zeile mitziehen) |
| verschiebt, welche Zahlen ein Lauf liefert | `docs/handbuch/vergleiche.md` (den Schnitt benennen — Läufe von davor und danach sind nicht vergleichbar) |
| einen Bug aus `docs/audit_findings.md` behebt | Finding dort entfernen, nicht abhaken |
| eine neue Schwachstelle findet, die nicht sofort gefixt wird | Finding in `docs/audit_findings.md` ergänzen |

Zwei Regeln dazu: Was der Code nicht tut, darf die Doku nicht behaupten — lieber die Formulierung abschwächen als eine Aussage stehen lassen, die ein Fachprüfer widerlegt. Und wenn eine Änderung eine dieser Zeilen auslöst, aber die Doku bewusst unverändert bleibt, gehört der Grund in die Commit-Message.

## Architektur-Map

`src/` ist die Kern-Engine (Paketname bewusst `src`, nicht umbenennen), nach fachlichen Paketen sortiert statt nach technischem Typ:

- `src/agents/` — wer spricht wann, in welcher Reihenfolge, mit welchen Rechten (Agent-Node, Orchestrator, Scheduler, Redebedarf-Logik, `agent_dependencies.py`, `agent_permissions.py`). Die beiden letzten halten je ein Vokabular, gegen das `validation.py` prüft: die erlaubten `depends_on`-Werte und die Grammatik der Faktor-Berechtigungen
- `src/market/` — Preis-/Kosten-/Nachfrage-Mathematik und Faktor-Regeln (`market_feedback.py`, `simulation_functions.py`, `property_engine.py`, `factor_dynamics.py`, Market-Node). `market_feedback.py` hieß bis P0.4 `market_rules.py` — der Name versprach die generische Regelauswertung, behandelt aber genau einen Regeltyp (`booking_yield_feedback`) und löst im Übrigen Startwerte auf. Der **Config-Schlüssel** heißt weiterhin `market_rules`
- `src/population/` — Bevölkerungs-Sampling und Buchungs-Logit-Modell
- `src/cib/` — CIB-Konsistenzbewertung (`scenario_consistency.py`) plus die darauf aufbauende LLM-Szenario-Narrative-Schicht
- `src/orchestration/` — Tick-Loop, LangGraph-Wiring, Checkpointing, Szenario-Sweeps (`simulation_runner.py`, `langgraph_workflow.py`, `scenario_sweeps.py`, Environment-Node)
- `src/reporting/` — alles, was nach/während eines Laufs geschrieben oder dargestellt wird: `output_writer/` (darin seit P0.6 `provenance.py`: Seed, Rechenmodus, Config-Fingerabdruck und Codestand eines Laufs), `run_scenario_generator/`, `figure_generator/` (jeweils eigene Unterpakete), plus `protocol_generator.py`, `state_explorer.py`, `cib_visualizer.py`. **`config_fingerprint` ist eine Momentaufnahme — richtig ist allein der Aufrufzeitpunkt.** `SimulationRunner.run` nimmt sie vor dem ersten Tick und legt sie in `state.config_fingerprint` ab, `save_run_metadata` liest sie von dort. Am Ende genommen hasht sie den Lauf mit (`factors` trägt den Zustand jedes Deskriptors) — genau der Fehler, den die Gegenprobe am 2026-08-27 gefunden hat
- `src/llm/` — LLM-Backend-Auswahl und **der eine** Ollama-Client (`llm_client.OllamaClient`: Retry mit Backoff, dann `RuntimeError`). `studio_helpers.LocalOllama` ist nur noch die Env-Übersetzung davor; einen zweiten, still mockenden Client gibt es seit P0.1 nicht mehr
- `src/models/` — Pydantic-Datenmodelle (State, Events, Agenten, Population, Properties, CIB) — bewusst eine gemeinsame Schicht, nicht weiter aufgeteilt (fragile Import-Reihenfolge, siehe unten)
- `src/prompts/` — Prompt-Templates pro Agent (`consumer.md`, `provider.md`, `regulator.md`)
- `src/legacy/` — abgelöste Komponenten (z. B. `CIBExtractorNode`), nicht Teil der aktiven Pipeline
- `src/run_simulation.py`, `src/config_loader.py`, `src/validation.py`, `src/logging_setup.py`, `src/rule_engine.py` — bleiben bewusst Top-Level (CLI-Einstieg bzw. von mehreren Paketen genutzt). `rule_engine.py` ist seit P0.4 **die** Auswertung einer `when`-Klausel: Faktor-Regeln, Shift-Regeln der Bevölkerung und die Aktivierung der regulatorischen Kostentreiber laufen alle darüber. Vorher hatte jede der drei Stellen ihre eigene, unterschiedlich reiche Fassung, und keine meldete, was sie nicht verstand. In `validation.py` gibt es zwei Wege in dieselbe Prüfung: `collect_state_errors` sammelt und wirft nicht (für Oberflächen, die alle Befunde auf einmal zeigen wollen), `validate_state` wirft (für den Runner). Neue Prüfungen gehören hierher, **nicht** in Eingabefelder des Dashboards — die CLI und handgeschriebene Configs kommen sonst daran vorbei

Jedes Paket hat ein `__init__.py`, das die öffentliche API re-exportiert.

- `dashboard/` — Präsentations-UI. Der oberflächenfreie Service-Layer liegt direkt darin (`config_catalog.py`, `run_browser.py`, `run_launcher.py`, `consistency_report.py`) und wird von beiden Oberflächen geteilt:
  - `dashboard/web/` — **aktive** Plotly-Dash-App. Seit P1.5 ein **Leitstand**: ein Bildschirm mit fünf Zonen (`shell.py`), kein Stapel Seiten. `app.py` (Einstieg, Stores, Routing), `shell.py` (Rahmen und Kopfzeile), `theme.py` (Farbtokens + Plotly-Templates hell/dunkel), `components.py`, `state.py` (`ConfigDraft` ⇄ `dcc.Store`), `runner.py` (Lauf im Hintergrund-Thread), `status.py` (**eine** Ableitung des Anlagenzustands für Kopfzeile, Banner und Konsole), `run_data.py` (die Daten eines Laufs aus einer Hand — oder der Beispieldatensatz), `demo_run.py` (ebenjener), `timeline.py` (Tick-Achse und Abspielsteuerung), `pages/` (`launch.py` — das Bedienfeld links, `setup.py` — der Bereich «Einrichten», `runs.py` — die Ergebnis-Ansichten, `docs.py` — Handbuch mit Kapitelregistry und Suche), `views/` (die sieben Run-Ansichten plus `scene.py` für den Viewport und `telemetry.py` für die rechte Zone), `config_editor/` (seit P1.1 der geführte Start-Ablauf in `start_flow.py` **plus** die vier Editor-Tabs dahinter; Erklärtexte gebündelt in `glossary.py`). Drei Regeln gelten hier:
    1. **Ein Eingabefeld darf nur an einer Stelle gerendert werden.** Der geführte Block und der aktive Tab liegen gleichzeitig im DOM, und eine doppelt vergebene Dash-ID ist ein Laufzeitfehler im Browser — `tests/test_web_start_flow.py` hält das fest.
    2. **Werte fließen nur in eine Richtung**, vom Feld in den Store. Ein Feld aus dem Store heraus zu setzen (etwa die Lauflänge beim Wechsel des Presets vorzubelegen) führt dieselbe Zahl an zwei Stellen — das Eingabefeld schreibt seinen alten Wert beim nächsten Abgleich zurück, und im Fenster steht eine andere Zahl als im Lauf. Die Zeitleiste ist keine Ausnahme davon: Ihr Regler *stellt* den `tick-store` dar, er hält keinen zweiten Wert.
    3. **Die linke Spalte trägt keine Eingabefelder** (seit P1.6). Sie ist Anzeige und Auslöser — was eingestellt ist, der Preflight, der Start —, kein Formular; die Felder leben im Bereich «Einrichten». Der Grund ist gemessen, nicht gefühlt: Mit dem Editor darin war die Spalte **10,7 Bildschirme** hoch, trug 752 Wörter und 122 Eingabefelder, und der Start-Knopf lag 6,1 Bildschirme tief. Die Abnahmekriterien von P1.1 (drei Entscheidungen) und P1.5 (fünf Zonen, kein Seiten-Scroll) waren dabei **beide erfüllt** — ein Kriterium, das die Anzahl misst, sagt nichts über die Erreichbarkeit. `tests/test_web_rail.py` deckelt jetzt den Umfang. **Einrichten und Beobachten sind zwei Betriebsarten**: Die eine braucht Fläche und Fließtext, die andere Dichte und Ruhe; sie in dieselbe Zone zu legen geht nur zulasten einer von beiden
    4. **Farbe kommt aus den Tokens, nirgends sonst her** (seit P1.5). Kein Modul schreibt eine Tailwind-Farbklasse (`bg-white`, `text-slate-600`) oder einen Hex-Wert; Tailwind liefert Layout, Abstand und Typografie, die Farbe kommt als `af-*`-Klasse aus `assets/dashboard.css` bzw. als semantische Rolle aus `theme.PALETTE`. Beide Seiten tragen dieselben Namen, einmal hell und einmal dunkel. Durchgesetzt wird das nicht von einer Liste, sondern von `tests/test_web_theme.py` — einem AST-Durchlauf über `dashboard/web/`, der jede Farbklasse und jeden rohen Farbwert meldet. Eine einzige übersehene reicht, um im Dark Mode eine weiße Fläche aufblitzen zu lassen. **Dashs eigene Komponenten** (Slider, Dropdown, Tabs) werden über ihre `--Dash-*`-Token-Ebene mitgefärbt, nicht über einzelne Selektoren — deren Klassennamen haben sich zwischen Dash 2 und Dash 4 bereits einmal vollständig geändert
  - `dashboard/legacy_streamlit/` — abgelöste Streamlit-UI, nur noch zum Vergleich lauffähig; **keine neuen Funktionen dort einbauen**
- `aeroforesight-ai-landing-page/` — statische Landingpage. Wird von der Dash-App selbst ausgeliefert: Landingpage auf `/`, Dashboard auf `/app/` (`dashboard/web/landing_route.py`, Pfade in `dashboard/web/routing.py`). Ihre Design-Tokens (`design/color-tokens.json`) sind die Quelle für die **helle** Palette des Dashboards; die dunkle (`theme.INK`) hat keine Entsprechung auf der Landingpage, weil die dort nicht umschaltbar ist
- `langgraph_studio/` — interaktive Graph-Entwicklung (LangGraph Studio)
- `configs/` — Simulationskonfiguration (`simulation_config.json`, `properties.json`, `agents.json`, `agent_profiles.json`, `cib_frozen.json`, `sweeps/`)
- `tests/` — pytest-Suite (über 500 Tests; die genaue Zahl liefert `pytest --collect-only -q`, sie gehört bewusst nicht als feste Zahl in die Doku — siehe P4.3); `test_dashboard_service.py` deckt den Service-Layer ab, `test_web_state.py` die Draft-Serialisierung, `test_web_layout.py` jede Ansicht der Dash-App (auch mit unvollständigen Run-Verzeichnissen), `test_web_shell.py` die fünf Zonen und die eine Zeitachse, `test_web_theme.py` das Farbfundament beider Modi, `test_web_demo.py` den Beispieldatensatz, `test_web_rail.py` den Umfang des Bedienfelds
- `docs/handbuch/` — die geschriebenen Kapitel des Dashboard-Handbuchs (Markdown, vom Dashboard unter `/doku` gerendert); Referenzkapitel entstehen zur Laufzeit aus `configs/`
- `docs/` — technische Doku (CIB-Methodik, Agent-Profile, Szenario-Workflow) und `docs/audit_findings.md` (bekannte Bugs/Inkonsistenzen, bewusst nicht gefixt — bitte durchgehen und priorisieren); `docs/research/` — Fachliteratur

## Domain-Glossar

- **Tick** — kleinste Simulationseinheit, hat **keine** Kalenderbedeutung (kein Quartal/Jahr). Uhr: `current_tick` / `max_ticks`.
- **CIB-Matrix** (Cross-Impact-Balance, Weimer-Jehle) — eingefrorene Referenzmatrix (`configs/cib_frozen.json`), bewertet die interne Konsistenz von Faktor-Konstellationen. **Stand heute** prüft `scenario_consistency.py` einzelne Zellen gegen einen Schwellwert und summiert Konflikte — das ist eine eigene Heuristik, nicht das Impact-Balance-Kriterium der Methode. Bis [P2.2](docs/projektplan.md) umgesetzt ist, nicht als "Algorithmus nach Weimer-Jehle" bezeichnen. Details: [`docs/cib_role.md`](docs/cib_role.md), [`docs/cib_rationale.md`](docs/cib_rationale.md).
- **Faktoren F1–F7** — Zustandsvariablen des soziotechnischen Systems (Mobilitätsnachfrage, Regulierung, Technologie/SAF, Wirtschaft, Alternativen, Gesellschaft, Geopolitik), je zwei Zustände (z. B. F1.1/F1.2). **F7 ist "Geopolitische Stabilität"** — entschieden am 2026-08-26, umgesetzt mit [P0.2](docs/projektplan.md#p02--f7-drift-auflösen). Die Drift ist damit weg: `configs/factors.json` und `configs/cib_frozen.json` tragen denselben Namen, und `tests/test_factor_naming.py` hält das fest. Die 48 F7-Zellen der Matrix wurden unter der neuen Lesart einzeln geprüft (19 geändert, 29 bestätigt) und tragen je eine Begründung. **Ein Vorbehalt bleibt:** Diese 48 Werte sind modellgeneriert und fachlich noch nicht abgenommen — `metadata.source` sagt das mit `llm_proposed_pending_review_v3`. Wer F7 nach außen verwendet, weiß das.
- **Logit-Modell** — mikroökonomisches Nutzenmodell für Kaufentscheidungen der simulierten Population. **Stand heute** ist es keine Logit-Ziehung: `_booking_probability` rechnet die Sigmoid und vergleicht sie gegen 0.5, was einer deterministischen Schwelle auf dem Nutzen entspricht (`src/population/population_sampler.py:355`). Die Formulierung nach außen entsprechend vorsichtig halten, bis [P2.1](docs/projektplan.md) umgesetzt ist.
- **Agent-Profile** (Consumer, Provider, Regulator) — informationsbeschränkte LLM-Agenten; erlaubte Beobachtungen/Outputs pro Rolle in `configs/agent_profiles.json`. Details: [`docs/agent_profiles.md`](docs/agent_profiles.md).
- **`when`-Klausel** — die Bedingung einer Regel (`factor_rules`, `shift_rules`, `regulatory_influences`). Bezugsgröße ist `factor` (+ `state`), `metric`, `system_property` oder die Kurzform `tick`; verglichen wird mit `above`, `below`, `at_least`, `at_most`, `eq` (`gte`/`lte` sind Altnamen). **Pro Klausel höchstens eine numerische Bezugsgröße** — sonst ließe sich ein Vergleich keiner davon zuordnen. Eine leere Klausel heißt "immer" und ist nur bei `regulatory_influences` zulässig. Vollständig: [`src/rule_engine.py`](src/rule_engine.py), Oberflächentext in `docs/handbuch/ref-config.md`.
- **Seed** — der Startwert der Zufallsziehung. Er wird **einmal** aufgelöst, in `SimulationRunner.run`, und steht danach in `state.config.seed`; die Konstante dafür ist `DEFAULT_SEED` in `src/models/state_models.py`. Nennt die Konfiguration keinen, gilt dieser Standardwert — ein Lauf ohne genannten Seed ist also **nicht** zufällig, sondern wiederholbar. Bis zur Gegenprobe am 2026-08-27 stand die 42 als Literal in `environment_node`: Der Lauf zog reproduzierbar, `run_metadata.json` schrieb `seed: null`, und der Editor nannte ihn «frei». Wer einen weiteren Rückfall braucht, benutzt die Konstante, nicht eine eigene Zahl. **Auch `run_multi` beginnt seine Folge dort** (seit 2026-08-27; vorher bei 0, weshalb derselbe Aufbau je nach Pfad andere Zahlen lieferte). Die Vielfalt der Wiederholungen kommt aus `base_seed + index`, nicht aus dem fehlenden Seed — die erste Wiederholung ist damit derselbe Lauf wie ein Einzellauf.
- **State Explorer** — Q&A über abgeschlossene Run-Daten (`tick_mechanics.json`, `price_history.json`, `event_log.json`). Das Modell bekommt ausschließlich diese Daten als Kontext. **Stand heute** wird die Antwort danach *nicht* gegen den Kontext geprüft — die Zusage "keine erfundenen Zahlen" ist eine Prompt-Anweisung, keine Schranke. Bis [P2.5](docs/projektplan.md) umgesetzt ist, entsprechend vorsichtig formulieren.

## Harte Architektur-Invarianten

Diese Prinzipien sind der eigentliche USP des Produkts (Schutz vor LLM-Halluzination) und dürfen nie aufgeweicht werden:

1. **Zahlen kommen immer aus Python, nie vom LLM.** Preise, Booking-Raten, Faktorzustände etc. werden deterministisch berechnet (`src/market/simulation_functions.py`, `src/market/market_feedback.py`, `src/market/factor_dynamics.py`, `src/rule_engine.py`).
   **Und es ist überall dieselbe Zahl.** `compute_cost_pressure` und `compute_market_metrics` verlangen seit P0.7 `factors` und `system_properties` als **Pflichtangabe**. Sie waren optional, und zwei Aufrufer hatten sie vergessen — der Environment-Node und die Vorschau im Agenten-Prompt. Beide bekamen still einen Kostendruck ohne die bedingten regulatorischen Kostentreiber; dem Agenten wurde damit im ersten Tick eine andere Zahl gezeigt, als die Simulation benutzte. Wer wirklich keinen Kontext hat, schreibt `factors={}` — eine Aussage statt eines Versehens. **Dieselbe Regel gilt für den Tick-Kontext der Bevölkerung:** `apply_factor_shifts` und `run_population_tick` verlangen `tick`/`current_tick` und `metrics` ebenso ohne Default — `tick=0` hieß "es gibt keinen Tick" und schaltete jede `tick`- und `metric`-Regel still ab. Die Regel gilt für **jeden** Parameter, der Tick-Kontext trägt. Durchgesetzt wird sie nicht von einer Liste, sondern von `tests/test_cost_pressure_source.py::TestKeinKontextparameterEntgehtDemSweep` — einem AST-Durchlauf über `src/`, der jeden solchen Parameter mit Default meldet. Eine handgepflegte Aufzählung fängt nur einen Rückfall auf bekannten Stellen, nie einen übersehenen Geschwisterfall: Genau daran ist der erste Anlauf gescheitert, der acht Stellen nannte und zwei weitere in derselben Datei übersah (`evaluate_booking` und `aggregate_population_stats` setzten still `0.6`/`1.0` an die Stelle der konfigurierten Sättigung). Wer einen Default braucht, weil sein Rückfall aus lebendem Zustand kommt statt aus einer erfundenen Konstante, trägt ihn mit Begründung in `AUSNAHMEN` ein. LLM-Agenten liefern ausschließlich Narrative/Events, nie Kennzahlen.
   **Und ein Ausfall ist sichtbar.** Kein Codepfad darf eine erfundene Antwort an die Stelle einer echten setzen, ohne das festzuhalten. Fällt ein LLM-Aufruf **innerhalb eines Laufs** aus (Agenten, Szenario-Node, Lauf-Szenario), wird er über `logging` gemeldet, landet als `LLMIncident` in `state.llm_incidents`, wird nach `llm_incidents.json` geschrieben und markiert den Lauf in `run_metadata.json` als `degraded` — das Dashboard zeigt ihn dann mit Warnbanner. Ein bewusster Mock-Lauf (`--mock-llm`) ist **kein** Ausfall und wird nicht so markiert — er ist seit P0.6 aber als solcher erkennbar: `run_metadata.json` hält `compute_mode` fest, und das Dashboard sagt es im Tab «Übersicht». Ein Lauf ohne Sprachmodell darf nicht wie ein vollwertiger aussehen. Aufrufe **außerhalb** eines Laufs — heute nur der State Explorer — haben keinen `SimulationState` und schreiben kein Artefakt; sie scheitern laut, ihre eigene Zusage bekommt [P2.5](docs/projektplan.md). Wer einen neuen LLM-Aufrufer innerhalb eines Laufs baut, hängt ihn an diese Kette an.
2. **Agenten dürfen nur vorschlagen, was ihr Profil erlaubt.** Regulator darf F2/F6 vorschlagen, Provider/Consumer nur Events. Nicht ohne Rücksprache erweitern.
   **Eine Quelle, eine Prüfung** (seit P0.5): Die Berechtigung steht ausschließlich in `configs/agent_profiles.json` (`may_propose: ["factor_state F2", …]`), das hartcodierte `AGENT_FACTOR_PERMISSIONS` ist weg. Geprüft wird sie nur in `src/agents/agent_permissions.may_propose_factor` — der Parser in `agent_node` und die Durchsetzung in `factor_dynamics.validate_factor_proposals` rufen dieselbe Funktion. Wer eine dritte Prüfstelle baut, stellt den Zustand wieder her, den P0.5 abgeräumt hat. **Ohne Profil ist nichts erlaubt** — und weil `config_loader` bei fehlender `agent_profiles.json` still keines vergibt, weist `validation.py` seit dem 2026-08-27 einen Agenten ohne Profil ab. Sonst schaltet ein fehlender Dateiname diese Invariante lautlos ab.
3. **Die CIB-Matrix ist bewusst eingefroren** (`"frozen": true`). Sie darf sich nicht aus Simulationsläufen ableiten — sonst wird der Maßstab aus dem Messobjekt gewonnen (zirkulär).
4. **Pydantic-Typisierung an allen Agenten-Grenzen** — jede Cross-Boundary-Datenstruktur ist ein typisiertes Modell in `src/models/`, keine rohen Dicts.
5. **Ein Tick ist ein Tick** — keine Kalender-/Datumssemantik in Configs, Checkpoints oder Outputs einführen.
6. **Eine `when`-Klausel wird an genau einer Stelle ausgewertet** (`src/rule_engine.py`, seit P0.4). Wer eine neue Regelart einführt, ruft `rule_matches` — er schreibt keine eigene Auswertung. Und was nicht auswertbar ist, schlägt **laut** fehl: unbekannte Bedingung, Vergleich ohne Bezugsgröße, `factor` ohne `state`. Ein still zurückgegebenes `False` hat die Divergenz zwischen den drei früheren Evaluatoren jahrelang unsichtbar gehalten. Namen (Metriken, Systemgrößen) prüft `validation.py` beim Laden, weil "Wert nicht da" zur Laufzeit ein normaler Zustand ist.

## Dev-Workflow

**Immer im venv arbeiten — und zwar in `.venv` im Repo-Wurzelverzeichnis.** Kein globales Python, kein anders benanntes Verzeichnis. Der Ordner ist in `.gitignore`, jede und jeder legt ihn lokal selbst an:

```powershell
py -3.12 -m venv .venv          # oder eine neuere 3.x; pyproject verlangt >= 3.11
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Alle folgenden Befehle setzen ein **aktiviertes** venv voraus:

```powershell
pytest                    # volle Test-Suite
ruff check .               # Linting
black --check .            # Formatierung prüfen (black . zum Formatieren)

python -m src.run_simulation --mock-llm --rounds 1 --quiet   # Smoke-Test ohne Ollama
python -m dashboard.web.app --port 8511                       # Landingpage auf /, Dashboard auf /app/
python -m streamlit run dashboard/legacy_streamlit/app_researcher.py --server.port=8512   # Legacy-Vergleich
```

Ohne Aktivierung liegen `pytest`, `ruff` und `black` nicht auf dem PATH — dann entweder aktivieren oder direkt aufrufen: `.\.venv\Scripts\ruff.exe check .`. Ein `python`, das nicht aus `.venv` kommt, findet das Paket `src` nicht, weil `pip install -e` nur ins venv geschrieben hat.

**Warum das eine Konvention und keine Empfehlung ist:** [`.claude/launch.json`](.claude/launch.json) startet das Dashboard über `.venv/Scripts/python.exe`. Diese relative Angabe funktioniert auf jedem Rechner — aber nur, wenn das venv wirklich `.venv` heißt und dort liegt. Bis 2026-08-26 stand dort ein absoluter Pfad in ein fremdes Benutzerverzeichnis; das Dashboard ließ sich damit auf keinem anderen Rechner starten. Die Datei bleibt deshalb bewusst **versioniert** und gehört nicht in `.gitignore`: eine relative Angabe ist für alle richtig, eine ignorierte Datei müsste jede und jeder neu erfinden.

`black` + `ruff` vor jedem Commit laufen lassen (CI in `.github/workflows/tests.yml` prüft beides plus Tests).

Drei Tests brauchen Aufmerksamkeit (Stand 2026-08-26, verifiziert). **Alle drei sind in [`.github/workflows/tests.yml`](.github/workflows/tests.yml) per `--deselect` ausgeklammert** — die CI ist deshalb grün, ein lokaler `pytest`-Lauf ohne Ollama ist es nicht. Die drei Zeilen fallen mit [P4.2](docs/projektplan.md):

- `test_run_single_sweep_short` und `test_sweep_base_price_override_raises_ticket_price` (`tests/test_scenario_sweeps.py`) **hängen** ohne lokalen Ollama minutenlang, statt sauber zu skippen — nicht einfach "bekannte Fehler". Behebung in P4.2.
- `test_market_rules_resolve_marginal_cost_fraction` (`tests/test_market_feedback.py::TestM413ConfigurablePrice`) ist **kein Code-Bug**: der Test erwartet den Default `0.33`, `configs/properties.json` liefert `0.25`, die Auflösung in `market_feedback.py` arbeitet korrekt. Zu klären ist nur, welcher Wert fachlich stimmt — dann Test oder Config nachziehen.

Import-Reihenfolge in `src/models/__init__.py` ist bewusst nicht alphabetisch (löst einen circular import zwischen `state_models` und `event_models`) — Kommentar dort beachten, nicht von Formattern umsortieren lassen.

## Deployment-Ziel

Hetzner Cloud Server mit lokal laufendem Ollama (Datenhoheit, keine externen LLM-Calls für sensible B2B-Daten). `Dockerfile`/`docker-compose.yml` sind ein Ausgangspunkt, noch nicht produktionsscharf.

## Backlog

**[docs/projektplan.md](docs/projektplan.md) ist die verbindliche Reihenfolge** — dort steht, was wann drankommt, mit Fundstelle und Abnahmekriterium pro Paket. Nichts davon ungefragt vorziehen, aber auch nichts mehr als "bekannt und bewusst offen" abtun: seit 2026-08-25 ist **jedes** Finding aus `docs/audit_findings.md` einem Arbeitspaket zugeordnet (Zuordnungstabelle am Ende des Plans).

- **Phase 0 — abgeschlossen** (Vertrauens-Blocker vor dem nächsten Demo): sichtbarer LLM-Ausfall (P0.1 ✅), F7-Drift (P0.2 ✅), `validate_config` (P0.3 ✅), die **drei** auseinandergelaufenen Rule-Evaluatoren (P0.4 ✅ — der dritte, in `simulation_functions`, stand weder im Plan noch im Audit und kam erst bei der Gegenprobe dazu), Faktor-Berechtigungen aus einer Quelle (P0.5 ✅), ein Run-Artefakt, das Seed und Rechenmodus überhaupt festhält (P0.6 ✅), und der Kostendruck aus einer Quelle (P0.7 ✅ — kam aus der Umsetzung von P0.4 dazu).
  **Offen aus P0.2:** Die 48 neu bewerteten Matrixzellen brauchen noch eine fachliche Abnahme. Bis dahin trägt `cib_frozen.json` die Quelle `llm_proposed_pending_review_v3`; wer sie durchgeht, ersetzt das Label. Es ist die einzige offene Position der Phase.
- **Phase 1** — aktueller Schwerpunkt: Start-Flow (P1.1 ✅ — geführter Ablauf mit drei Entscheidungen, Presets vorn; dabei kam heraus, dass ein gewähltes Preset im Dashboard **still von den Datei-Defaults überschrieben** wurde, bei allen acht ausgelieferten Presets), Leitstand-Oberfläche (P1.5 ✅ — fünf Zonen auf einem Bildschirm, Light/Dark, Tick-Zeitleiste; dabei kam heraus, dass die Stile für Dashs eigene Komponenten seit dem Sprung auf Dash 4 an **keiner einzigen Stelle** mehr griffen), Einrichten und Beobachten getrennt (P1.6 ✅ — die Konfiguration aus der 336-px-Spalte in einen eigenen Bereich; die Spalte fiel von 10,7 auf 1,4 Bildschirme, der Start-Knopf von 6,1 Bildschirmen Tiefe auf sichtbar), Ergebnisdarstellung, Szenariogestaltung, Landingpage produktionsreif.
- **Phase 2** — Modellsubstanz: echte Ziehung im Buchungsmodell, Impact-Balance, Matrix-Provenienz, Alterung der Population, Grounding des State Explorers.
- **Phasen 3–5** — Engine-Härtung, Testfundament, Altlasten (inkl. Entfernen von `dashboard/legacy_streamlit/`).
- **Phase 6** — API-Layer und Multi-Tenant-B2B: bewusst noch nicht im Scope. Das Tor dorthin ist in Phase 6 des Plans benannt; es hängt an vier abgehakten Phase-1-Paketen, nicht an einem Gefühl.

Drei Fallstricke aus der Gegenprobe vom 2026-08-26, die beim Anfassen der betroffenen Pakete zuerst zu lesen sind: **P3.5 nicht vor P0.1** (das Fortschritts-Log des Dashboards hängt an `print()`), **P2.1 braucht einen Zufallsstrom pro Tick** (sonst buchen in jedem Tick dieselben Individuen), und **P2.2 braucht vorher eine Entscheidung**, was gilt, wenn die Impact Balance weniger als drei konsistente Szenarien liefert.

`docs/audit_findings.md` bleibt die Detailliste (Befund, Auswirkung, Fundstelle). Behobene Findings dort **entfernen**, neu gefundene ergänzen und im Projektplan einplanen.
