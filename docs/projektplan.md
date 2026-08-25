# Projektplan

**Stand:** 2026-08-25 · **Leitentscheidung:** Erst Funktionalität und UI, dann B2B-Readiness. Ein Produkt, das im Demo unverständlich aussieht, wird nicht gekauft — egal wie sauber die Engine darunter ist.

Dieser Plan ist die verbindliche Reihenfolge der nächsten Schritte. **Alle Findings aus [`audit_findings.md`](audit_findings.md) sind hier eingeplant** — die Zeit der dokumentierten, aber unangefassten Baustellen ist vorbei. Das Audit bleibt die Detailliste mit Befund und Auswirkung; dieser Plan sagt, wann was drankommt. Die Zuordnung steht am Ende unter [Abdeckung](#abdeckung-des-audits).

> **Verifiziert am 2026-08-25:** Jedes Finding wurde vor der Aufnahme einzeln gegen den Codestand geprüft. **Keines hat sich stillschweigend erledigt.** Drei Korrekturen gegenüber dem Audit-Text: die Streamlit-Duplikate betreffen nur noch `dashboard/legacy_streamlit/` (P5.2), die hartcodierten LLM-Defaults sind von 7 auf 10 Produktionsdateien gewachsen (P3.4), und der als "echter Bug" geführte Testfehler ist eine veraltete Testerwartung, kein Code-Fehler (P4.2).

Gepflegt wird bei jeder abgeschlossenen Aufgabe (siehe [Doku-Pflicht in CLAUDE.md](../CLAUDE.md#doku-pflicht)). Jedes Arbeitspaket nennt **Befund**, **Fundstelle**, **Was zu tun ist**, **Fertig wenn** und **Doku, die mitzieht**. Ein behobenes Finding wird in `audit_findings.md` **entfernt**, nicht abgehakt.

## Was bewusst nicht in diesem Plan steht

- **API-Layer / Multi-Tenancy / Auth / Billing** — noch nicht im Scope (Phase 6).
- **Kundengespräche und Vertrieb** — läuft außerhalb des Repos.
- **IP-/Autorenschaftsfrage** — geklärt, kein Arbeitspaket mehr.

---

## Phase 0 — Vertrauens-Blocker (vor dem nächsten Demo)

Fünf Punkte, die das Kernversprechen "Zahlen aus Python, Narrativ vom LLM" direkt angreifen. Zwei davon produzieren still falsche Ergebnisse — die gehören nach vorn, nicht in eine Hygiene-Liste.

### P0.1 — Stiller LLM-Ausfall wird sichtbar

**Befund:** Fällt Ollama aus, erzeugt der Agent hartkodierte `NO_OP`-Einträge, der Studio-Client liefert stumm Mock-Antworten. Ein degradierter Lauf ist im Output von einem echten nicht unterscheidbar — nur ein `print()` auf stdout, nichts im `event_log`. Verschärfend: zwei unabhängige Ollama-Clients mit gegenteiliger Fehlerphilosophie, derselbe Ausfall verhält sich je nach aktivem Client einmal laut und einmal leise.

**Fundstelle:** [`src/agents/agent_node.py:50-80`](../src/agents/agent_node.py), [`src/llm/studio_helpers.py:153-161`](../src/llm/studio_helpers.py) (`LocalOllama.call`), [`src/llm/llm_client.py`](../src/llm/llm_client.py) (`OllamaClient`).

**Was zu tun ist:** Jeden Fallback über `logging` statt `print` melden; im Run-Artefakt ein Feld `degraded: true` plus Zähler der Fallback-Ticks in `run_metadata.json` schreiben; im Dashboard einen sichtbaren Warnbanner auf jedem Lauf, der degradiert lief. Die zwei Clients auf einen zusammenführen und die laute Philosophie (Retry mit Backoff, dann `RuntimeError`) zum Standard machen.

**Fertig wenn:** Ein Lauf mit abgeschaltetem Ollama ist im Dashboard auf den ersten Blick als degradiert erkennbar, und ein Test deckt das ab.

**Doku zieht mit:** `docs/handbuch/fehlerbilder.md`, `CLAUDE.md` (Invariante 1 um "Ausfall ist sichtbar" ergänzen).

### P0.2 — F7-Drift auflösen

**Befund:** Die eingefrorene Matrix wurde für **F7 Marktstruktur** bewertet, die Simulation läuft mit **F7 Geopolitische Stabilität**. Die Zustände passen semantisch zufällig (offen/fragmentiert), die Bedeutung nicht. Matrix, Config, Doku und Outputs widersprechen sich — bei einem Produkt, dessen Verkaufsargument Reproduzierbarkeit ist, ist das teuer.

**Fundstelle:** [`configs/factors.json`](../configs/factors.json) (F7 = "Geopolitische Stabilitaet") gegen [`configs/cib_frozen.json`](../configs/cib_frozen.json) (`metadata.note`, 168 Zellen inkl. `F*.*|F7.*`).

**Was zu tun ist:** Entscheiden, welche Bedeutung F7 trägt. Dann Matrix, `factors.json`, Glossar und Handbuch auf **eine** Lesart ziehen. Danach ein Test, der Faktor-IDs und -Namen zwischen `factors.json` und `cib_frozen.json` mechanisch vergleicht, damit die Drift nicht wiederkommt.

**Fertig wenn:** Faktorname in Config, Matrix, Doku und Run-Output identisch; Test grün.

**Doku zieht mit:** `docs/handbuch/faktoren.md`, `docs/cib_role.md`, `CLAUDE.md` (Glossar).

### P0.3 — `validate_config` implementieren

**Befund:** `validate_config` gibt bedingungslos `[]` zurück, wird aber von `validate_state` behandelt, als würde echt geprüft. Fehlerhafte Configs laufen unbemerkt durch.

**Fundstelle:** [`src/validation.py:54-55`](../src/validation.py); vestigieller Parameter `factor_ids` in `validate_agent` (Zeile 42-51) gleich mitnehmen.

**Was zu tun ist:** Pflichtfelder, Wertebereiche (`llm.temperature`, `max_ticks`, Seeds) und Referenz-Integrität prüfen — insbesondere, ob Agenten auf existierende Faktor-IDs verweisen (dafür ist `factor_ids` gedacht). Fehler als Liste zurückgeben, im Dashboard vor dem Start anzeigen.

**Fertig wenn:** Eine absichtlich kaputte Config wird beim Start mit klarer Meldung abgewiesen, Tests decken die Fälle ab.

**Doku zieht mit:** `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/fehlerbilder.md`.

### P0.4 — Regelauswertung vereinheitlichen

**Befund:** Die generische "when/effect"-Regelauswertung existiert **zweimal unabhängig** und ist bereits auseinandergelaufen: `factor_dynamics.rule_matches` kennt `tick`, `metric` und `system_property`, `population_sampler._rule_matches` nur exaktes `factor`-Matching und `system_property`. Eine `shift_rule` mit `at_least`- oder `tick`-Bedingung greift im Sampler **still nie** — kein Fehler, kein Hinweis, einfach kein Effekt. Das ist kein Stilproblem, das sind falsche Zahlen. Dazu: `market_rules.py` behandelt trotz generischem Namen nur einen einzigen hartcodierten Regeltyp (`booking_yield_feedback`).

**Fundstelle:** [`src/market/factor_dynamics.py:87`](../src/market/factor_dynamics.py) (`rule_matches`), [`src/population/population_sampler.py:243`](../src/population/population_sampler.py) (`_rule_matches`), [`src/market/market_rules.py`](../src/market/market_rules.py).

**Verifiziert am 2026-08-25:** `rule_matches` (Zeile 87) kennt `tick`, `metric`, `at_least` und `system_property` — `_rule_matches` (Zeile 243) nur `system_property`. Die Divergenz ist real und unverändert.

**Was zu tun ist:** Einen gemeinsamen Evaluator bauen, beide Aufrufer darauf ziehen. Unbekannte Bedingungstypen müssen **laut fehlschlagen** statt still `False` zurückzugeben — genau das hat die Divergenz so lange versteckt. `market_rules.py` entsprechend seinem tatsächlichen Inhalt benennen oder auflösen.

**Fertig wenn:** Dieselbe Regel liefert an beiden Aufrufstellen dasselbe Ergebnis; ein Test deckt `at_least` und `tick` im Sampler-Pfad ab.

**Doku zieht mit:** `docs/handbuch/ref-config.md`, `docs/handbuch/preisbildung.md`.

### P0.5 — Faktor-Berechtigungen aus einer Quelle

**Befund:** Zwei unabhängige Quellen für "welcher Agent darf welchen Faktor ändern": ein hartcodiertes Dict `AGENT_FACTOR_PERMISSIONS` und `may_propose` in `agent_profiles.json`. Beide stimmen heute überein, werden aber nicht mechanisch synchron gehalten — und die hartcodierte ist die durchsetzende. Eine neue Berechtigung in der JSON würde still ins Leere laufen. Das greift Invariante 2 direkt an.

**Fundstelle:** [`src/market/factor_dynamics.py:13`](../src/market/factor_dynamics.py), [`src/agents/agent_node.py`](../src/agents/agent_node.py), Durchsetzung in `environment_node._apply_state_changes`.

**Was zu tun ist:** Berechtigungen ausschließlich aus `configs/agent_profiles.json` ableiten, das Dict entfernen. Test, der eine in der JSON ergänzte Berechtigung end-to-end durchreicht.

**Fertig wenn:** `agent_profiles.json` ist die einzige Quelle; eine Änderung dort wirkt ohne Codeänderung.

**Doku zieht mit:** `docs/agent_profiles.md`, `CLAUDE.md` (Invariante 2).

---

## Phase 1 — Funktionalität und UI (aktueller Schwerpunkt)

### P1.1 — "Simulation starten" neu bauen

**Befund:** Der Start-Flow ist UX-seitig der schwächste Teil des Dashboards. Wer zum ersten Mal einen Lauf startet, versteht nicht, was er einstellt und was passiert.

**Fundstelle:** [`dashboard/web/pages/launch.py`](../dashboard/web/pages/launch.py), [`dashboard/web/config_editor/save_start.py`](../dashboard/web/config_editor/save_start.py), [`dashboard/web/runner.py`](../dashboard/web/runner.py), die sechs Editor-Tabs in [`dashboard/web/config_editor/`](../dashboard/web/config_editor/).

**Was zu tun ist:** Den Weg von "Preset wählen" bis "Lauf läuft" auf einen geführten Ablauf reduzieren, mit sichtbarem Fortschritt statt eines blockierenden Wartezustands. Presets nach vorn (`configs/sweeps/`), Expertenparameter dahinter. Erklärtexte aus `config_editor/glossary.py` dort zeigen, wo entschieden wird, nicht in einem eigenen Tab. Fehlermeldungen aus P0.3 direkt am Feld.

**Fertig wenn:** Jemand ohne Vorwissen startet einen sinnvollen Lauf ohne Rückfragen, und `test_web_layout.py` deckt den neuen Flow ab.

**Doku zieht mit:** `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`.

### P1.2 — Ergebnisse und Plots refactoren

**Befund:** Die Ergebnisdarstellung überzeugt inhaltlich nicht — die Plots zeigen nicht das, was eine Strategieabteilung sehen will. Dazu ein Robustheitsproblem: Bricht die Figure-Erzeugung mittendrin ab, bleibt ein teilweise befülltes `manifest.json` liegen, und die nächste Ansicht zeigt den unvollständigen Satz ohne Hinweis.

**Fundstelle:** [`dashboard/web/views/figures.py`](../dashboard/web/views/figures.py) (441 Zeilen), [`dashboard/web/views/animation.py`](../dashboard/web/views/animation.py), [`dashboard/web/views/overview.py`](../dashboard/web/views/overview.py), Erzeugung und Manifest in [`src/reporting/figure_generator/run_figures.py`](../src/reporting/figure_generator/run_figures.py).

**Was zu tun ist:** Zuerst festlegen, welche **drei bis fünf Aussagen** ein Lauf beantworten soll — dann die Plots dafür bauen und den Rest streichen. Ein durchgehendes Farb- und Achsensystem aus `theme.py` statt pro Figur eigener Entscheidungen. Das Tripleset (Trendfortsetzung / Strukturwende / Krisenkonflikt) vergleichbar nebeneinander, nicht in getrennten Tabs. Das Manifest erst schreiben, wenn alle Figures stehen, oder den Teilstand explizit als unvollständig kennzeichnen.

**Fertig wenn:** Ein Lauf lässt sich in einem Screenshot erklären; ein abgebrochener Figure-Lauf hinterlässt keinen stillen Teilstand.

**Doku zieht mit:** `docs/handbuch/ergebnisse.md`, `docs/handbuch/ergebnisse-lesen.md`, `docs/handbuch/vergleiche.md`, `docs/handbuch/ref-ausgaben.md`.

### P1.3 — Szenariogestaltung neu denken

**Befund:** Wie die drei Szenarien entstehen und was sie unterscheidet, ist im Produkt nicht nachvollziehbar. Zusätzlich liegen zwei ähnlich benannte Sammlungen im selben Metadaten-Dict: `scenario_candidates` (deterministisch aus dem `ScenarioDeriver`) und `scenarios` (LLM-Narrativ mit geklemmten, aber vom LLM erfundenen `influence`-Werten). Die Python/LLM-Grenze steht hier nur im Code-Kommentar, nicht im Datenschema.

**Fundstelle:** [`src/cib/scenario_agent_node.py:264,282`](../src/cib/scenario_agent_node.py), [`dashboard/web/views/scenario.py`](../dashboard/web/views/scenario.py), [`src/reporting/run_scenario_generator/`](../src/reporting/run_scenario_generator/).

**Was zu tun ist:** Die Grenze ins Datenschema ziehen: getrennte, eindeutig benannte Strukturen, LLM-Werte als solche markiert. In der UI sichtbar machen, welche Zahl gerechnet und welcher Satz erzählt ist.

**Fertig wenn:** Kein Konsument kann LLM-behauptete Einflusswerte mit echten Matrixwerten verwechseln.

**Doku zieht mit:** `docs/handbuch/zahlen-und-sprache.md`, `docs/handbuch/fragestellungen.md`, `docs/cib_role.md`.

---

## Phase 2 — Modellsubstanz (Claims und Code in Deckung bringen)

Diese Punkte entscheiden, ob die wissenschaftlichen Aussagen einem Fachprüfer standhalten. Solange sie offen sind, gehören die Formulierungen in Pitch, README und Handbuch abgeschwächt.

### P2.1 — Buchungsmodell: echte Ziehung statt Schwellwert

**Befund:** Das "Logit-Modell" ist keines. Es wird `p = 1/(1+e^-u)` gerechnet und dann `p >= 0.5` geprüft — weil die Sigmoid monoton ist, ist das mathematisch identisch mit `u >= 0`. Der Logit-Teil tut nichts; es wird nie gegen die Wahrscheinlichkeit gezogen. Die Koeffizienten (`base_utility = 2.0`, `/100.0`, `*1.5`) sind handgesetzt, nicht geschätzt.

**Fundstelle:** [`src/population/population_sampler.py:355`](../src/population/population_sampler.py) (`_booking_probability`), Schwelle `DEFAULT_LOGIT_THRESHOLD = 0.5` in Zeile 23.

**Was zu tun ist:** Gegen die Wahrscheinlichkeit ziehen (`rng.random() < p`) mit dem Lauf-Seed, damit Reproduzierbarkeit erhalten bleibt. Koeffizienten nach `configs/properties.json` auslagern und ihre Herkunft dokumentieren — die Literatur liegt bereits in `docs/research/literature/` (Preiselastizitäten im Luftverkehr). **Vorbedingung:** Der Seed-Pfad ist heute wirkungslos — `_seed_runtime` ([`simulation_runner.py:269-281`](../src/orchestration/simulation_runner.py)) seedet das globale `np.random`, gezogen wird über `default_rng`. Das muss vorher geradegezogen werden, sonst ist die Reproduzierbarkeit mit dem ersten echten Zufall weg.

**Fertig wenn:** Buchungsentscheidungen sind stochastisch, bei gleichem Seed reproduzierbar, und jeder Koeffizient hat eine benannte Quelle.

**Doku zieht mit:** `docs/handbuch/kaufentscheidung.md`, `docs/handbuch/saettigung.md`, `README.md`, `CLAUDE.md` (Glossar "Logit-Modell").

### P2.2 — CIB: Impact-Balance-Kriterium implementieren

**Befund:** Die Konsistenzprüfung ist nicht der Weimer-Jehle-Algorithmus. Sie prüft einzelne Zellen gegen einen Schwellwert und summiert Konflikte. Das eigentliche CIB-Kriterium ist die **Impact Balance**: ein Szenario ist konsistent, wenn für jeden Faktor der gewählte Zustand die Summe der eingehenden Einflüsse maximiert. Diese Gleichgewichtsbedingung steht nirgends im Code.

**Fundstelle:** [`src/cib/scenario_consistency.py:99`](../src/cib/scenario_consistency.py) (`check_consistency`, `compute_consistency_score`).

**Was zu tun ist:** Impact-Balance als eigenständige Prüfung implementieren: pro Faktor die Einflusssumme je Zustand bilden, prüfen ob der gewählte Zustand das Maximum ist, Szenario nur dann konsistent nennen. Die bisherige Heuristik darf als zusätzlicher Score bleiben — aber unter eigenem Namen.

**Fertig wenn:** Für ein bekanntes Referenzszenario stimmt das Ergebnis mit dem Impact-Balance-Kriterium überein; Tests decken konsistente und inkonsistente Fälle ab.

**Doku zieht mit:** `docs/cib_role.md`, `docs/cib_rationale.md`, `docs/handbuch/cib.md`, `CLAUDE.md` (Glossar).

### P2.3 — Matrix-Provenienz herstellen

**Befund:** Alle 168 Zellen in `cib_frozen.json` haben ein leeres `reasoning`-Feld; `metadata.source` sagt `expert_defined_aviation_domain_v2` (Basis: Vorlesungsfolien, Experte = das Team selbst). Für einen Prototyp legitim — aber die Kalibrierung ist genau das Asset, das später verkauft wird.

**Fundstelle:** [`configs/cib_frozen.json`](../configs/cib_frozen.json), erzeugt von [`scripts/rebuild_cib_frozen.py`](../scripts/rebuild_cib_frozen.py).

**Was zu tun ist:** Pro Zelle eine Begründung und eine Quelle eintragen — beim Durchgehen fallen erfahrungsgemäß auch inhaltliche Fehler auf. Das Skript so erweitern, dass es leere `reasoning`-Felder als Fehler meldet statt sie zu erzeugen. Die Matrix bleibt eingefroren (Invariante 3). Sinnvoll gemeinsam mit P0.2 zu erledigen — beim Durchgehen der Zellen fällt die F7-Entscheidung ohnehin an.

**Fertig wenn:** Keine Zelle ohne Begründung; `metadata` nennt Methode und Bewertungsdatum.

**Doku zieht mit:** `docs/cib_rationale.md`, `docs/handbuch/cib.md`.

### P2.4 — Population altert nicht

**Befund:** `age` wird beim Sampling einmal gezogen und danach nie fortgeschrieben. Über einen langen Lauf bleibt die Bevölkerung eingefroren, während Preise, Regulierung und Werte sich bewegen — die Altersgruppen-Statistik beschreibt dauerhaft den Startzustand.

**Fundstelle:** [`src/population/population_sampler.py:173-229`](../src/population/population_sampler.py) (Sampling), Auswertung Zeile 436-444, Modell [`src/models/population_models.py:42`](../src/models/population_models.py).

**Was zu tun ist:** Klären, was ein Tick demografisch bedeuten soll — **ohne** Kalendersemantik einzuführen (Invariante 5). Optionen: Alterung als Property mit konfigurierbarer Rate, Kohortenwechsel bei definierten Tick-Abständen, oder bewusst dokumentieren, dass die Population statisch ist. Die dritte Option ist die billigste und für kurze Läufe vertretbar — dann muss sie aber im Handbuch stehen.

**Fertig wenn:** Entscheidung getroffen, im Code umgesetzt oder im Handbuch als Grenze benannt.

**Doku zieht mit:** `docs/handbuch/akteure.md`, `docs/handbuch/grenzen.md`, `docs/handbuch/tick-und-lauf.md`.

---

## Phase 3 — Engine-Härtung

Fallen, die heute niemanden stören und beim nächsten Feature zuschlagen. Jedes Paket ist klein; zusammen entscheiden sie, ob die Engine trägt.

### P3.1 — System-Properties liefern Laufzeitwerte

**Befund:** Für Properties mit `source in {"runtime","computed"}` (z. B. `provider_markup`, `ticket_price`) liefert `resolve_system_properties` laut eigenem Docstring die statische Trajektorien-Baseline, nicht den Laufzeitwert. Folgenlos nur, solange keine ausgelieferte Regel diese IDs per `system_property`-Bedingung referenziert — eine neue Regel darauf würde still gegen eine veraltete Zahl prüfen.
**Fundstelle:** [`src/market/property_engine.py:127-136`](../src/market/property_engine.py).
**Was zu tun ist:** Laufzeitwert durchreichen, oder den Zugriff für diese Quellen hart ablehnen statt eine Baseline vorzutäuschen. Zusammen mit P0.4 erledigen — dieselbe Regelmechanik.
**Fertig wenn:** Eine Regel auf `ticket_price` prüft nachweislich gegen den echten Marktwert. **Doku:** `docs/handbuch/ref-config.md`.

### P3.2 — Checkpoint-Version wirklich prüfen

**Befund:** `checkpoint_version` wird in jedes Checkpoint-Metadatum geschrieben (`= 2`), aber nirgends zurückgelesen — `CheckpointManager.load` ignoriert `payload["metadata"]` komplett. Das Feld täuscht eine Versionsprüfung vor, die es nicht gibt.
**Fundstelle:** [`src/orchestration/checkpoint_manager.py:26`](../src/orchestration/checkpoint_manager.py).
**Was zu tun ist:** Beim Laden die Version prüfen und bei Mismatch klar abbrechen (Migration erst, wenn es eine zweite Version gibt).
**Fertig wenn:** Ein Checkpoint mit fremder Version wird mit verständlicher Meldung abgelehnt, Test dazu. **Doku:** `docs/handbuch/ref-ausgaben.md`.

### P3.3 — Fehlermeldungen, die auch greifen

**Befund:** Zwei Stellen, an denen Fehlerbehandlung nur so aussieht: In `langgraph_workflow` steht ein `try: pass` mit `except`, das nie feuern kann — die beabsichtigte freundliche Meldung bei fehlendem `langgraph` bleibt aus, stattdessen kommt später ein roher `ImportError`. In `create_graph.py` verschluckt ein `except Exception: pass` auch den absichtlich re-raisten Graph-Build-Fehler, und das Skript schreibt trotzdem ein statisches `graph.json`.
**Fundstelle:** [`src/orchestration/langgraph_workflow.py:41-44`](../src/orchestration/langgraph_workflow.py), [`langgraph_studio/create_graph.py:16-24`](../langgraph_studio/create_graph.py).
**Was zu tun ist:** Echten Import in den `try`-Block ziehen; im Studio-Skript den Build-Fehler durchreichen statt ein irreführendes `graph.json` zu schreiben.
**Fertig wenn:** Fehlendes `langgraph` erzeugt die gemeinte Meldung; ein kaputter Graph-Build bricht sichtbar ab. **Doku:** `docs/handbuch/fehlerbilder.md`.

### P3.4 — LLM-Konfiguration zentralisieren

**Befund:** Modellname `"llama3.2"` steht in **10 Produktionsdateien** (nachgezählt am 2026-08-25, das Audit sprach von sieben Stellen), der Endpoint uneinheitlich als `http://localhost:11434` in sieben und `http://127.0.0.1:11434` in zwei Dateien. Bemerkenswert: die beim Dash-Umbau **neu** entstandenen Module `config_editor/compute_mode.py` und `config_editor/llm_pipeline.py` haben die Hartkodierung geerbt — das Finding wächst mit jedem Modul weiter.
**Fundstelle:** `src/run_simulation.py`, `src/llm/llm_client.py`, `src/models/state_models.py`, `src/orchestration/langgraph_adapter.py`, `dashboard/config_catalog.py`, `dashboard/llm_status.py`, `dashboard/run_browser.py`, `dashboard/run_launcher.py`, `dashboard/web/config_editor/compute_mode.py`, `dashboard/web/config_editor/llm_pipeline.py` (plus `tests/test_web_compute_mode.py`, `tests/test_web_layout.py`).
**Was zu tun ist:** Eine Defaults-Quelle (Config plus `.env`-Override), alle Stellen darauf ziehen. Fällt mit der Client-Zusammenführung aus P0.1 zusammen.
**Fertig wenn:** Ein Endpoint-Wechsel erfordert genau eine Änderung. **Doku:** `README.md` (Umgebung), `docs/handbuch/ref-config.md`.

### P3.5 — Stille Klemmungen und Debug-Ausgaben

**Befund:** `threshold` und `max_contributions_per_agent` werden ohne Warnung auf einen Wunschbereich geklemmt — wer bewusst `threshold=1` setzt, bekommt stillschweigend 3. Dazu acht `print()`-Debugausgaben im Scheduler, die bei jedem Tick unbedingt laufen.
**Fundstelle:** [`src/agents/redebedarf_scheduler.py:73,75`](../src/agents/redebedarf_scheduler.py), [`src/agents/scheduler_node.py`](../src/agents/scheduler_node.py) (8 Vorkommen).
**Was zu tun ist:** Klemmung protokollieren oder als Konfigurationsfehler abweisen; `print()` durch `logging` mit Level-Guard ersetzen.
**Fertig wenn:** Ein geklemmter Wert erzeugt eine sichtbare Warnung; ein normaler Lauf ist auf stdout still. **Doku:** `docs/handbuch/ref-config.md`, `docs/handbuch/akteure.md`.

### P3.6 — Stabiler Vertrag für den Run-Launcher

**Befund:** `run_launcher` importiert drei unterstrichs-präfixierte Funktionen aus `run_simulation` (`_build_run_args`, `_save_run_outputs`, `_write_multi_run_summary`). Kein stabiler Vertrag — ein Refactor der internen Helper bricht den Launcher unbemerkt.
**Fundstelle:** [`dashboard/run_launcher.py:168`](../dashboard/run_launcher.py).
**Was zu tun ist:** Öffentliche Schnittstelle in `src/run_simulation.py` definieren und den Launcher darauf ziehen.
**Fertig wenn:** Kein Dashboard-Modul importiert mehr Unterstrich-Namen aus `src/`. **Doku:** `CLAUDE.md` (Architektur-Map, Service-Layer-Absatz).

---

## Phase 4 — Testfundament

267 Tests sind eine gute Grundlage, aber die Suite hat drei Eigenschaften, die beim Ausbau bremsen.

### P4.1 — Gemeinsame Fixtures

**Befund:** Kein `tests/conftest.py`; stattdessen 32 Vorkommen von `tempfile.mkdtemp(...)` mit `try/finally: shutil.rmtree(...)` über fünf Dateien, und `class MockLLM` vierfach near-identisch definiert.
**Fundstelle:** `tests/test_checkpoint_manager.py` (2), `test_dashboard_service.py` (9), `test_figure_generator.py` (4), `test_run_scenario_generator.py` (12), `test_state_explorer.py` (5); MockLLM in `test_agent_node.py`, `test_parallel_round.py`, `test_simulation_runner_e2e.py`, `debug_run_sequential.py`.
**Was zu tun ist:** `conftest.py` mit einem MockLLM-Fixture anlegen, Temp-Verzeichnisse auf das eingebaute `tmp_path` umstellen.
**Fertig wenn:** Kein Test legt mehr manuell ein Temp-Verzeichnis an; MockLLM existiert einmal. **Doku:** `README.md` (Tests-Abschnitt).

### P4.2 — Suite aufräumen und verlässlich machen

**Befund:** Uneinheitlicher Stil (16 Dateien funktional, drei `unittest.TestCase` ohne technischen Grund), `sys.path.append` in drei Dateien seit der Paketstruktur überflüssig, und `debug_run_sequential.py` ist gar kein Test (null `test_*`-Funktionen, wird von pytest nicht eingesammelt) — täuscht Abdeckung vor.

**Verifiziert am 2026-08-25, zwei Korrekturen am bisherigen Bild:**

1. Die beiden Sweep-Tests **hängen** ohne Ollama, sie schlagen nicht fehl — ein Lauf brach nach über sieben Minuten ohne Ergebnis ab. Das blockiert jeden vollständigen Testlauf, nicht nur zwei Zeilen im Report.
2. `test_market_rules_resolve_marginal_cost_fraction` ist **kein Code-Bug**. Der Test erwartet `0.33` (den Default aus `market_rules.py:45`), `configs/properties.json` liefert `0.25`, und die Auflösung arbeitet korrekt — der Config-Wert gewinnt, wie gewollt. Zu entscheiden ist nur, welcher Grenzkostenanteil fachlich stimmt.

**Fundstelle:** `tests/test_scenario_sweeps.py:119,205`, `tests/test_market_feedback.py:94`, `tests/debug_run_sequential.py`, `tests/test_parallel_round.py`, `tests/test_simulation_runner_e2e.py`, `tests/test_agent_node.py`, `tests/test_save_final_narrative.py`.

**Was zu tun ist:** Die Ollama-abhängigen Tests per `pytest.mark.skipif` auf einen erreichbaren Endpoint überspringen (Priorität — sie kosten heute jeden vollen Lauf). Beim Grenzkostenanteil fachlich entscheiden und Test **oder** Config nachziehen. Dann auf funktionalen Stil vereinheitlichen, `sys.path.append` entfernen, Debug-Skript in ein Werkzeug umwandeln oder löschen.

**Fertig wenn:** `pytest` läuft ohne lokales Ollama vollständig durch und ist grün — keine "bekannten Fehler" mehr in `CLAUDE.md`. **Doku:** `CLAUDE.md` (Dev-Workflow), `README.md`.

---

## Phase 5 — Altlasten entfernen

Erst nach Phase 1, damit beim UI-Umbau nichts wegfällt, das noch als Referenz dient.

### P5.1 — Toter Code und irreführende Namen

**Befund:** Mehrere Konstrukte, die Funktionalität vortäuschen: `initial_ticket_price` und `active_market_rule` (keine Referenz), `run_population_sampling` ("backward-compatible entry point", nirgends aufgerufen), `speech_plan.aborted` (Feld existiert nicht), der leere `pass`-Zweig in `_format_factors` mit hartcodiertem Agenten-String, und der `state._population_updates`-Pfad — ein komplettes Population-Shift-Feature mit Modellen und Unit-Tests, das der Laufzeitpfad nie erzeugt. Dazu die irreführende Paarung `compute_ticket_price` / `compose_ticket_price`: die erste berechnet **nicht** den Kundenpreis.
**Fundstelle:** [`src/market/market_rules.py`](../src/market/market_rules.py), [`src/population/population_sampler.py:558`](../src/population/population_sampler.py), [`src/agents/scheduler_node.py:123`](../src/agents/scheduler_node.py), [`src/agents/agent_node.py:258-260`](../src/agents/agent_node.py), [`src/orchestration/environment_node.py:282-283`](../src/orchestration/environment_node.py), [`src/market/simulation_functions.py`](../src/market/simulation_functions.py).
**Was zu tun ist:** Pro Konstrukt entscheiden — entfernen oder anschließen. Beim Population-Shift-Feature ist die Frage produktinhaltlich (gehört es zu P1.3?), nicht technisch. Die zwei Preisfunktionen so benennen, dass die Rolle aus dem Namen hervorgeht.
**Fertig wenn:** Kein Modul mehr, das nur von seiner eigenen Definition oder einem Test am Leben gehalten wird. **Doku:** `CLAUDE.md` (Architektur-Map), `docs/handbuch/preisbildung.md`.

### P5.2 — Legacy-Streamlit abnehmen und entfernen

**Befund:** `dashboard/legacy_streamlit/` hält zwei Doppelpaare am Leben (`app.py`/`app_researcher.py`, `config_ui.py`/`config_ui_researcher.py`), die inhaltlich auseinanderlaufen — u. a. eine nur dort gepflegte längere `_render_animation` und verlorene Guillemets in der Researcher-Variante. Drei Audit-Findings betreffen ausschließlich diesen Ordner und lösen sich mit ihm auf.
**Fundstelle:** [`dashboard/legacy_streamlit/`](../dashboard/legacy_streamlit/).
**Was zu tun ist:** Nach Abschluss von Phase 1 prüfen, ob die Dash-App alles abdeckt, was der Researcher-Modus konnte — insbesondere die zusätzlichen Plotly-Charts der Legacy-Animation. Dann das Paket löschen, samt Streamlit-Abhängigkeit und `.streamlit/`.
**Fertig wenn:** Kein Streamlit mehr im Repo und in den Abhängigkeiten. **Doku:** `CLAUDE.md`, `README.md`, `dashboard/README.md`.

### P5.3 — `src/legacy/` entscheiden

**Befund:** `cib_extractor_node.py` wird ausschließlich von `tests/test_cib_matrix.py` referenziert; kein Produktionspfad importiert `src/legacy/*`.
**Fundstelle:** [`src/legacy/cib_extractor_node.py`](../src/legacy/cib_extractor_node.py).
**Was zu tun ist:** Bewusst entscheiden — für Experimente behalten (dann dokumentieren, wofür) oder mitsamt Test entfernen. Berührt P2.2: falls die Extraktionslogik beim Impact-Balance-Umbau nützlich ist, vorher ansehen.
**Fertig wenn:** Entscheidung getroffen und im Code sichtbar. **Doku:** `CLAUDE.md` (Architektur-Map, `src/legacy/`-Zeile).

---

## Phase 6 — B2B (noch nicht Scope)

Wird erst geplant, wenn Phase 1 steht: API-Layer, Mandantentrennung, Persistenz, Auth, Billing, produktionsscharfes Hetzner-Deployment. Der heutige `Dockerfile`/`docker-compose.yml` ist ein Ausgangspunkt, kein Deployment.

Eine Randnotiz fürs Marketing, kein Arbeitspaket: Der 10.000-Tick-Benchmark lief mit `dummy_llm` ([`scenario_sweeps.py:200`](../src/orchestration/scenario_sweeps.py)). Die Zahl stimmt, misst aber die deterministische Hälfte — nicht als "unsere KI simuliert 10k Ticks" verwenden.

---

## Abdeckung des Audits

Jeder Abschnitt aus [`audit_findings.md`](audit_findings.md) ist einem Paket zugeordnet. Kein Finding bleibt ungeplant.

| Audit-Abschnitt | Pakete |
| --- | --- |
| Faktoren / Modellsubstanz | P0.2, P2.1, P2.2, P2.3, P2.4 |
| Markt / Preisbildung | P0.4 (Rule-Evaluatoren, `market_rules`), P0.5 (Berechtigungen), P3.1 (Property-Baseline), P5.1 (toter Code, Preisfunktions-Namen) |
| Agenten / Scheduling | P0.1 (Silent-Fallback), P1.3 (Szenario-Schlüssel), P3.5 (Klemmung, `print`), P5.1 (`aborted`, `_format_factors`, `_population_updates`) |
| Validierung / Checkpointing / Orchestrierung | P0.3 (`validate_config`, `factor_ids`), P2.1 (`_seed_runtime`), P3.2 (Checkpoint-Version), P3.3 (leerer `try`) |
| LLM-Anbindung | P0.1 (zwei Clients), P3.4 (hartcodierte Defaults) |
| Dashboard | P1.2 (Manifest-Teilstand), P3.6 (private Imports), P5.2 (Legacy-Duplikate — erledigen sich mit dem Löschen) |
| LangGraph Studio | P3.3 |
| Tests | P4.1, P4.2 (inkl. der hängenden Sweep-Tests und der veralteten Erwartung in `test_market_rules_resolve_marginal_cost_fraction`) |
| Sonstiges | P5.3 |
