# Projektplan

**Stand:** 2026-08-28 — **Phase 0 ist abgeschlossen**, **P1.1 ist erledigt**, und darauf ist **P1.5** gefolgt: Das Dashboard ist jetzt ein **Leitstand** — ein Bildschirm mit fünf Zonen statt eines Stapels Seiten, mit umschaltbarem hellen und dunklen Design und einer Tick-Zeitleiste, die Szene, Kennzahlen und Verläufe gemeinsam führt ([Einzelheiten](#p15--leitstand-oberfläche--erledigt-2026-08-28)). Auch dort lag der eigentliche Fund unter der Oberfläche: Die Stile für Dashs eigene Komponenten griffen seit dem Sprung auf Dash 4 an **keiner einzigen Stelle** mehr — im hellen Modus unsichtbar, im dunklen ein violetter Regler mit schwarzer Beschriftung auf schwarzem Grund. Direkt darauf folgte **P1.6**, weil die Vermessung des Ergebnisses einen Rückschritt zeigte: Die linke Spalte war mit der hineingepressten Konfiguration **10,7 Bildschirme** hoch, und der Start-Knopf lag 6,1 Bildschirme tief — bei erfüllten Abnahmekriterien beider Vorgängerpakete. Einrichten und Beobachten sind jetzt getrennt, die Spalte ist ein Bedienfeld, und die Kriterien von P1.1 und P1.5 sind um eine Größe ergänzt, die **Erreichbarkeit** misst statt Anzahl ([Einzelheiten](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28)). Zu P1.1: «Simulation starten» führt jetzt in drei Entscheidungen zum Lauf ([Einzelheiten](#p11--simulation-starten-neu-bauen--erledigt-2026-08-28)). Dabei kam ein Fund heraus, der nicht in der Oberfläche lag: Ein gewähltes Szenario-Preset wurde im Dashboard **still von den Datei-Defaults überschrieben** — bei allen acht ausgelieferten Presets, ein Lauf «Business as Usual» rechnete mit steigender CO₂-Abgabe. Behoben, mit einem Wächter über jede Datei unter `configs/sweeps/`. Phase 0 im Übrigen unverändert und **sechsfach** gegengeprüft: Haikos Gegenprobe deckte 36 von 36 Zusagen mechanisch ab ([Einzelheiten](#gegenprobe-zu-p04p06-2026-08-27)), Manus zweite Runde am laufenden System fand drei Zusagen von P0.6, die im Artefakt nicht hielten — alle behoben ([Einzelheiten](#zweite-gegenprobe-zu-p06-manu-2026-08-27)) —, die dritte Runde hat seine Befunde nachgestellt und drei Lücken in den neuen Tests geschlossen ([Einzelheiten](#dritte-runde-manus-gegenprobe-nachgeprüft-haiko-2026-08-27)), die vierte hat die Phase als Ganzes geprüft (**im Code hält alles, fünf Lücken lagen in der Doku**, [Einzelheiten](#vierte-runde-phase-0-als-ganzes-geprüft-2026-08-27)), und die fünfte hat P0.7 gegengeprüft: Der Fix hält, ein Geschwister seines Musters lag noch in der Bevölkerungshälfte und ist mit behoben ([Einzelheiten](#fünfte-runde-p07-gegengeprüft-manu-2026-08-27)), und die sechste hat diese Verallgemeinerung gegengeprüft: Sie hält, zwei weitere Geschwister lagen in derselben Datei und sind mit behoben ([Einzelheiten](#sechste-runde-die-verallgemeinerung-gegengeprüft-haiko-2026-08-28)). P0.7 kam aus der Umsetzung von P0.4 dazu und ist ebenfalls erledigt; drei seiner eigenen Befundaussagen mussten dabei korrigiert werden. Offen aus P0.2: die fachliche Abnahme der 48 neu bewerteten Matrixzellen — die einzige offene Position der Phase Die drei Phase-1-Pakete sind **gegengeprüft** (Manu, 2026-08-28): Die tragenden Zusagen halten, drei Befunde lagen in der Darstellung — ein Schubladen-Knopf, dessen Versteck-Regel die Kaskade verlor und deshalb nie wirkte, sein Haltepunkt, der der falschen Zone gehörte, und ein Laufzustand, der nur die eigene Sitzung kannte; alle drei behoben ([Einzelheiten](#gegenprobe-zu-p11p15p16-manu-2026-08-28)). Daraus ist **P1.7** entstanden, und es ist erledigt: Der Ablauf **ist** jetzt die Oberfläche — Einrichten zuerst, der Lauf als eigener Bildschirm, das Einrichten als Schrittfolge hinter einem Einstieg mit drei Wegen statt einer Bildlaufstrecke ([Einzelheiten](#p17--der-ablauf-wird-die-oberfläche--erledigt-2026-08-28)). **Alle vier Stufen sind fertig** — zuletzt am 2026-08-28 der Einstieg mit den drei Wegen (Stufe C) und der mechanische Überlauf-Wächter (Stufe D). Beim Wächter kam die Entscheidung dazu, die der Plan offengelassen hatte: Playwright als **optionales** Extra, damit die CI ohne Browser grün bleibt und wer die Oberfläche anfasst ihn lokal scharf hat. Und er hat sich beim ersten Durchlauf selbst korrigiert — zwei weitere Phantome kamen zu den drei aus P1.8 dazu, darunter `scrollWidth` selbst: Ein ausgeschwebtes Kind zählt in den `scrollWidth` seines Vorfahren, und Dashs eigenes Dropdown ließ die Zeitleiste 145 px Überlauf melden, obwohl nichts zu sehen war. P1.7 ist gegengeprüft (Haiko, 2026-08-28): drei Befunde behoben — der Start aus der Schrittfolge wechselte den Bildschirm nicht, ein Widerspruch von 1,7 s zwischen Kopfzeile und Mitte, und ein Text, der auf einen aufgelösten Abschnitt zeigte; ein vierter Befund hat sich unter genauerer Messung aufgelöst und ist samt zurückgenommener Korrektur protokolliert ([Einzelheiten](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt)). Am **2026-08-28** ist der Einrichten-Assistent unabhängig auditiert worden — bewusst ohne die Abnahmekriterien dieses Plans als Maßstab, und genau dadurch hat das Audit gefunden, was die Kriterien durchgelassen haben: Auf dem Sweep-Pfad erreicht **genau ein** Feld des Entwurfs die Simulation, während der Preflight einen Lauf beschreibt, der so nicht stattfindet; fünf Bedienelemente in als *optional* gekennzeichneten Schritten schreiben ohne Rückfrage in `configs/properties.json`; und **kein einziger der acht Schritte passt auf einen Bildschirm** (1,13 bis 4,44), obwohl genau das die Zusage von P1.7 war. Daraus ist [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28) entstanden: **P1.1 und P1.7 sind wieder offen**, P1.5 bekommt ein Kriterium dazu, P1.8 schärft sein Verfahren nach, P1.3 und P3.6 werden vorgezogen ([Einzelheiten](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28), Vollfassung in [`wizard_audit_2026-08-28.md`](wizard_audit_2026-08-28.md)). Dieselbe Lehre wie bei P1.6, diesmal als Regel festgehalten: **Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung** — nachzulesen im [Commit-Regelwerk](#regelwerk-atomare-commits-ab-2026-08-28-verbindlich), das ab sofort für jede Änderung gilt. · **Leitentscheidung:** Erst Funktionalität und UI, dann B2B-Readiness. Ein Produkt, das im Demo unverständlich aussieht, wird nicht gekauft — egal wie sauber die Engine darunter ist.

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
- **`get_llm()` wählt weiterhin still den Mock**, wenn keine Umgebungsvariable gesetzt ist. Eingeplant in [P3.4](#p34--llm-konfiguration-zentralisieren).
- **Ein Config-Fehler auf der CLI kommt als roher Traceback.** Eingeplant in [P3.3](#p33--fehlermeldungen-die-auch-greifen).

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
> [P2.3](#p23--matrix-provenienz-herstellen) in einem Zug — zweimal durchgehen ist der teure
> Weg. P0.2 ist deshalb **kein kleines Umbenennungs-Paket**; wer es anfasst, plant die
> Zellendurchsicht mit ein.
>
> **Und eine Vorbedingung, die daraus folgt:** F7 wird in
> [P2.2](#p22--cib-impact-balance-kriterium-implementieren) pro Szenario als fixierter
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

*Der Einwand, der dazugehört.* CIB will endogene Deskriptoren, die einander beeinflussen. Geopolitik wirkt stark nach außen und wird kaum zurückbeeinflusst — die eingehende Spalte wird nach der Neubewertung dünn. Das ist beherrschbar, muss aber bewusst entschieden werden und **löst eine Vorbedingung in [P2.2](#p22--cib-impact-balance-kriterium-implementieren) aus**.

*Nebenbefund, unabhängig von der Entscheidung.* Die Zustandsbezeichnung "F7.1 Offene Märkte, Kooperation" **mischt beide Lesarten** — "offene Märkte" ist Marktsprache, "Kooperation" ist Politik. Das ist vermutlich die Bruchstelle, an der die Drift entstand. Unter Geopolitik müssten die Zustände etwa "Offene Lufträume, multilaterale Kooperation" und "Fragmentierung, Sperrungen, Konflikte" heißen; die Umbenennung gehört in dieses Paket.

**Was zu tun ist:** Entscheiden, welche Bedeutung F7 trägt. Dann Matrix, `factors.json`, Glossar und Handbuch auf **eine** Lesart ziehen. Danach ein Test, der Faktor-IDs und -Namen zwischen `factors.json` und `cib_frozen.json` mechanisch vergleicht, damit die Drift nicht wiederkommt.

**Abgrenzung zu P2.3 — abhängig von der Entscheidung:** Fällt sie auf **Marktstruktur**, ist hier nur umzubenennen und die 168 Einflusswerte bleiben unberührt; Phase 0 hängt dann nicht an einer Zellendurchsicht. Fällt sie auf **Geopolitische Stabilität** (die Empfehlung oben), sind alle 48 F7-Zellen neu zu bewerten — acht davon nachweislich falsch, der Rest unter einer anderen Bedeutung entstanden und damit nicht belastbar — dann gehört P2.3 für diese Zellen vorgezogen, weil zweimal durchgehen der teure Weg ist. In beiden Fällen bleibt der mechanische Namensabgleich zwischen `factors.json` und `cib_frozen.json` Teil dieses Pakets.

**Umsetzung nach der Entscheidung.** Beide Wege sind hier vollständig ausgeschrieben, damit nach dem einen fehlenden Satz nichts mehr zu klären ist.

*Variante A — **Geopolitische Stabilität*** (Haikos Position und Empfehlung dieser Auswertung):

1. `configs/factors.json`: Zustandsbezeichnungen entmischen — `F7.1` von „Offene Maerkte, Kooperation" auf „Offene Lufträume, multilaterale Kooperation", `F7.2` von „Fragmentierung, Konflikte" auf „Fragmentierung, Sperrungen, Konflikte". Name und Beschreibung bleiben.
2. `configs/cib_frozen.json`: `metadata.factors` auf „F7 Geopolitische Stabilität" ziehen, `metadata.note` nachführen — **und die 48 F7-Zellen neu bewerten**, weil die heutigen Werte eine Marktlogik kodieren. Für diese Zellen [P2.3](#p23--matrix-provenienz-herstellen) vorziehen: Begründung gleich mitschreiben statt zweimal durchgehen. Die Matrix bleibt eingefroren (Invariante 3).
3. [`scripts/rebuild_cib_frozen.py`](../scripts/rebuild_cib_frozen.py) mitziehen, damit ein Neubau dieselben Werte erzeugt.
4. `docs/cib_role.md`: die Active/Passive-Tabelle enthält F7-Scores, die aus den alten Zellen stammen — nach der Neubewertung neu rechnen. `docs/cib_rationale.md`: die Zeilen zu `f7_oil_stress` und `f7_open_markets` sprechen von „Marktfragmentierung" und „offene, integrierte Märkte" und müssen auf die geopolitische Lesart (Ölpreis als Indikator geopolitischer Spannung) umgeschrieben werden.
5. Test, der Faktor-IDs **und -Namen** zwischen `factors.json` und `cib_frozen.json` mechanisch vergleicht — damit die Drift nicht wiederkommt.
6. Die Vorbedingung in [P2.2](#p22--cib-impact-balance-kriterium-implementieren) festschreiben: F7 wird pro Szenario als fixierter Deskriptor behandelt.
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

**Offen und bewusst so markiert:** Die 48 Werte sind modellgeneriert und fachlich nicht abgenommen. `metadata.source` steht deshalb auf `llm_proposed_pending_review_v3`, und ein Test hält fest, dass das Label bleibt, solange die Durchsicht aussteht. Wer sie macht, ersetzt es.

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

Bewusst **nicht** hier behoben: dass `state.config.llm` von niemandem gelesen wird. Das gehört zu [P3.4](#p34--llm-konfiguration-zentralisieren).

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

**Nebenbefund, der sich mitauflöst:** `run_population_tick` nimmt bereits ein `current_tick`, das nirgends benutzt wird — in [P5.1](#p51--toter-code-und-irreführende-namen) als toter Parameter geführt. Es ist genau der Wert, den der gemeinsame Evaluator für `tick`-Bedingungen braucht. Das Audit sagt zu diesem Parameter bereits, er solle **nicht** entfernt werden, weil P2.1 ihn braucht — P0.4 macht ihn schlicht schon vorher benutzt, womit er aufhört, vestigiell zu sein. Der tote Code **in** `market_rules.py` (`initial_ticket_price`, `active_market_rule`) bleibt dagegen bei P5.1 und wird hier nicht vorgezogen.

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
- *Der Abdruck überlebt Checkpoint und Fortsetzen.* 30-Tick-Lauf mit Checkpoints: Der Startabdruck steht im Checkpoint, wird beim Fortsetzen nicht neu genommen, obwohl die Faktoren sich bewegt haben. Alte Checkpoints (ohne das Feld) laden weiterhin — sie bekommen beim Fortsetzen allerdings einen Abdruck aus bereits gelaufenem Zustand. Enger Randfall, gehört in die Zuständigkeit von [P3.2](#p32--checkpoint-version-wirklich-prüfen).
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

**Was daraus als Prüfmuster bleibt.** Die erste Gegenprobe hat für tote Modulpfade und Anker einen Wächter gebaut (`tests/test_packaging.py`). Punkt 1 und 2 sind dieselbe Drift eine Ebene höher — zwischen Plan, Audit und `CLAUDE.md` —, und dort greift kein Wächter. Bis [P4.3](#p43--doku-zahlen-mechanisch-halten) das mechanisch macht, gilt die Handregel: **Wer ein Paket auf ✅ setzt, geht im selben Zug durch `audit_findings.md` und die Backlog-Liste in `CLAUDE.md`.** Und Punkt 3 wiederholt die Lehre der ersten Runde wörtlich — eine Zusage über ein *Artefakt* ist nicht geprüft, solange nur die *Anzeige* geprüft ist.

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

**Zwei veraltete Zahlen mitgezogen:** Der Docstring des Wächters sprach von „allen vier Stellen … ein fünftes Mal", `CLAUDE.md` Invariante 1 ebenso — beide entstanden, als die Liste vier Einträge hatte, und wuchsen im selben Commit auf acht. Dieselbe Klasse wie die toten Modulpfade der ersten Runde, nur mit Zahlen. Bis [P4.3](#p43--doku-zahlen-mechanisch-halten) greift, ist die Handregel: **Wer eine Aufzählung erweitert, sucht ihre Anzahl im Fließtext.**

**Eine Zeile, die noch fehlt und nicht der Review gehört:** Die Angleichung von `run_multi` ist eine Modelländerung — das Audit hatte sie ausdrücklich als „kein Review-Fix" geführt. Die Begründung trägt und ist nachgerechnet, aber der Plan schreibt „entschieden wurde für Angleichen" im Passiv, während das Haus sonst zuschreibt (P0.2, P0.4). Wer sie getroffen hat, gehört dazu.

---

## Phase 1 — Funktionalität und UI (aktueller Schwerpunkt)

### P1.1 — "Simulation starten" neu bauen ✅ erledigt 2026-08-28

**Befund (korrigiert am 2026-08-26):** Der Start-Flow ist UX-seitig der schwächste Teil des Dashboards. Wer zum ersten Mal einen Lauf startet, versteht nicht, was er einstellt. Der Config-Editor ist mit rund 1.700 Zeilen über sechs Tabs zu tief, die Presets aus `configs/sweeps/` stehen nicht vorn, und die Erklärtexte in `config_editor/glossary.py` (401 Zeilen) stehen nicht dort, wo entschieden wird.

**Was hier nicht mehr gilt:** Die ursprüngliche Fassung nannte einen "blockierenden Wartezustand". Den gibt es nicht mehr — [`dashboard/web/runner.py`](../dashboard/web/runner.py) fährt den Lauf in einem Worker-Thread mit Queue, und [`pages/launch.py:37,147-182`](../dashboard/web/pages/launch.py) holt die Fortschrittszeilen per `dcc.Interval` ab. Fortschrittsanzeige ist erledigt und kein Teil dieses Pakets mehr.

**Fundstelle:** [`dashboard/web/pages/launch.py`](../dashboard/web/pages/launch.py), [`dashboard/web/config_editor/save_start.py`](../dashboard/web/config_editor/save_start.py), [`dashboard/web/runner.py`](../dashboard/web/runner.py), die sechs Editor-Tabs in [`dashboard/web/config_editor/`](../dashboard/web/config_editor/).

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

**Wieder geöffnet am 2026-08-28 — das ergänzte Kriterium reichte nicht.** Das Audit hat die zweite Größe geprüft, die P1.6 nachgetragen hat, und eine dritte gefunden, die keine der beiden misst: **Wirksamkeit.** «Höchstens drei Entscheidungen bis zum Start» zählt Entscheidungen — nicht, ob sie etwas bewirken. Auf dem Sweep-Pfad sind zwei der drei wirkungslos: `run_single_sweep` schreibt Rechenmodus und Seed fest, und vom Entwurf erreicht nur `rounds` den Lauf. Ein Kriterium, das Entscheidungen zählt, ist damit auf dieselbe Weise blind wie das, das Bildschirme nicht kannte. Aufgenommen in [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28) (Befund 1, Pakete W0.2 und W1.1).

**Doku zieht mit:** `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`.

### P1.2 — Ergebnisse und Plots refactoren

**Befund:** Die Ergebnisdarstellung überzeugt inhaltlich nicht — die Plots zeigen nicht das, was eine Strategieabteilung sehen will. Dazu ein Robustheitsproblem: Bricht die Figure-Erzeugung mittendrin ab, zeigt die nächste Ansicht den unvollständigen Satz ohne Hinweis.

**Mechanismus korrigiert am 2026-08-26:** Die ursprüngliche Fassung sprach von einem "teilweise befüllten `manifest.json`". Das kann nicht passieren: [`run_figures.py:48-68`](../src/reporting/figure_generator/run_figures.py) baut alle sechs Figures in **einem** Dict-Literal und schreibt das Manifest erst danach — bricht ein Plot ab, entsteht **gar kein** Manifest. Der stille Teilstand entsteht an zwei anderen Stellen: [`dashboard/run_browser.py:224-231`](../dashboard/run_browser.py) fällt bei fehlendem Manifest auf `base.glob("*.png")` zurück und zeigt die halb geschriebenen PNGs mit aus dem Dateinamen erzeugten Titeln; und ein **altes** Manifest aus einem früheren Lauf bleibt liegen und passt dann nicht mehr zu den frisch überschriebenen PNGs.

**Fundstelle:** [`dashboard/web/views/figures.py`](../dashboard/web/views/figures.py) (441 Zeilen), [`dashboard/web/views/animation.py`](../dashboard/web/views/animation.py), [`dashboard/web/views/overview.py`](../dashboard/web/views/overview.py), Erzeugung in [`src/reporting/figure_generator/run_figures.py`](../src/reporting/figure_generator/run_figures.py), Glob-Fallback in [`dashboard/run_browser.py:201-231`](../dashboard/run_browser.py) (`list_run_figures`).

**Was zu tun ist:** Zuerst festlegen, welche **drei bis fünf Aussagen** ein Lauf beantworten soll — dann die Plots dafür bauen und den Rest streichen. Ein durchgehendes Farb- und Achsensystem aus `theme.py` statt pro Figur eigener Entscheidungen. Das Tripleset (Trendfortsetzung / Strukturwende / Krisenkonflikt) vergleichbar nebeneinander, nicht in getrennten Tabs. Für den Teilstand: Figures in ein temporäres Verzeichnis schreiben und erst nach dem letzten Plot samt Manifest atomar an ihren Platz ziehen — dann gibt es nur ganz oder gar nicht. Den Glob-Fallback in `list_run_figures` entweder streichen oder das Ergebnis sichtbar als "ohne Manifest, Vollständigkeit unbekannt" kennzeichnen.

**Fertig wenn:** Ein Lauf lässt sich in einem Screenshot erklären; ein abgebrochener Figure-Lauf hinterlässt keinen stillen Teilstand — weder über den Glob-Fallback noch über ein stehengebliebenes Manifest.

**Doku zieht mit:** `docs/handbuch/ergebnisse.md`, `docs/handbuch/ergebnisse-lesen.md`, `docs/handbuch/vergleiche.md`, `docs/handbuch/ref-ausgaben.md`.

### P1.3 — Szenariogestaltung neu denken

**Befund:** Wie die drei Szenarien entstehen und was sie unterscheidet, ist im Produkt nicht nachvollziehbar. Zusätzlich liegen zwei ähnlich benannte Sammlungen im selben Metadaten-Dict: `scenario_candidates` (deterministisch aus dem `ScenarioDeriver`) und `scenarios` (LLM-Narrativ mit geklemmten, aber vom LLM erfundenen `influence`-Werten). Die Python/LLM-Grenze steht hier nur im Code-Kommentar, nicht im Datenschema.

**Fundstelle:** [`src/cib/scenario_agent_node.py:264,282`](../src/cib/scenario_agent_node.py), [`dashboard/web/views/scenario.py`](../dashboard/web/views/scenario.py), [`src/reporting/run_scenario_generator/`](../src/reporting/run_scenario_generator/).

**Was zu tun ist:** Die Grenze ins Datenschema ziehen: getrennte, eindeutig benannte Strukturen, LLM-Werte als solche markiert. In der UI sichtbar machen, welche Zahl gerechnet und welcher Satz erzählt ist.

**Fertig wenn:** Kein Konsument kann LLM-behauptete Einflusswerte mit echten Matrixwerten verwechseln.

**Doku zieht mit:** `docs/handbuch/zahlen-und-sprache.md`, `docs/handbuch/fragestellungen.md`, `docs/cib_role.md`.

> **Vorgezogen am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28)): Der Sweep-Pfad ist die Ursache der beiden kritischen Audit-Befunde — er verwirft alles außer `rounds` und überschreibt still die `max_ticks` jedes Presets. Diese Szenariogestaltung zu klären, **bevor** die Oberfläche darüber etwas behauptet, spart die doppelte Arbeit; W1.1 und W1.2 gehören fachlich hierher.

### P1.4 — Landingpage produktionsreif

**Befund (neu am 2026-08-26):** Die Landingpage kam in diesem Plan bisher nicht vor, obwohl Phase 1 "Funktionalität und UI" heißt und sie die einzige öffentlich sichtbare Oberfläche ist. [`docs/landingpage.md`](landingpage.md) führt drei offene Punkte, keiner davon war eingeplant:

1. **Das Demo-Formular geht ins Leere.** `demo-anfragen.html:151` hat `action="#"` — jede Anfrage über die Kontaktseite wird verworfen, ohne dass der Absender es merkt.
2. **Impressum, Datenschutz und AGB sind Platzhalter** mit `[…]`-Stellen und einem gelben Warnblock, der vor Veröffentlichung raus muss.
3. **Tailwind und Schriften kommen von CDNs** — auf der Landingpage (`index.html:7-9`) **und im Dashboard** (`dashboard/web/app.py:53-56`). Das widerspricht dem erklärten Deployment-Ziel Datenhoheit direkt: jeder Seitenaufruf meldet die IP des Betrachters an zwei fremde Hosts. Bei Google Fonts kommt die deutsche Rechtslage dazu.

**Fundstelle:** [`aeroforesight-ai-landing-page/`](../aeroforesight-ai-landing-page/) (5 Seiten, 1.928 Zeilen), [`dashboard/web/app.py:53-56`](../dashboard/web/app.py), [`dashboard/web/landing_route.py`](../dashboard/web/landing_route.py), [`docs/landingpage.md`](landingpage.md) (Abschnitt "Offene Punkte").

**Was zu tun ist:** Einen Endpunkt für das Demo-Formular anlegen (die Landingpage wird ohnehin von der Flask-App unter `landing_route.py` ausgeliefert — die Route gehört dorthin) samt Bestätigung für den Absender und einer Ablage, die niemand übersieht. Rechtstexte durch geprüfte Fassungen ersetzen und den Warnblock entfernen. Tailwind und die Schriften lokal ausliefern, für Landingpage und Dashboard in einem Zug, damit das Ergebnis nicht halb bleibt.

**Fertig wenn:** Ein Seitenaufruf erzeugt keine Anfrage an einen externen Host, keine `[…]`-Stelle und kein Warnblock ist mehr übrig, und eine abgeschickte Demo-Anfrage kommt nachweislich an.

**Doku zieht mit:** `docs/landingpage.md` ("Offene Punkte" leeren), `aeroforesight-ai-landing-page/DEPLOY.md`, `CLAUDE.md` (Deployment-Ziel, Datenhoheit).

### P1.5 — Leitstand-Oberfläche ✅ erledigt 2026-08-28

> **Abnahme ergänzt am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28)): Zonen, Theme und Zeitleiste tragen und werden **nicht** zurückgebaut. Den Kriterien fehlt aber eine Größe, die niemand geprüft hat — **Barrierefreiheit**. Gemessen: null `aria-live`-Regionen im gesamten Dokument, kein `aria-current`, keine Fokusführung beim Bereichswechsel. Nachzuziehen mit Paket W5.3.

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

**Offen und bewusst nicht hier erledigt:** Die PNG-Tafeln unter `figures/` werden von matplotlib hell gerendert und stehen im Dark Mode auf einer weißen Fläche wie ein aufgelegtes Blatt. Sie dunkel zu erzeugen gehört zu [P1.2](#p12--ergebnisse-und-plots-refactoren). Ebenso bleibt der Vorbehalt aus P1.1 bestehen und wiegt jetzt schwerer: Der Preflight baut bei jeder Änderung des Entwurfs den vollständigen `SimulationState` auf, und die Parameterspalte ist ab jetzt dauerhaft sichtbar — er wird also häufiger angestoßen als vorher. Für Phase 6 zu messen.

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

**Offen und bewusst nicht hier erledigt:** Der Bereich «Einrichten» ist bei 1280 px 7,3 Bildschirme lang. Das ist für eine Konfigurationsseite in Ordnung — sie wird gelesen, nicht überwacht —, aber die 90 Eingabefelder unter «Systemgrößen» sind ein eigener Fall für [P1.2](#p12--ergebnisse-und-plots-refactoren) oder ein späteres Paket. Ebenso unverändert: Der Preflight baut bei jeder Entwurfsänderung den vollen `SimulationState` auf.

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

> **Wieder geöffnet am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28)): Die tragende Zusage dieses Pakets — *eine Frage auf dem Schirm* — ist **nicht gehalten**. Gemessen bei 1280 × 720 braucht kein einziger der acht Schritte weniger als einen Bildschirm; Schritt 4 braucht 3,37 und trägt 104 Bedienelemente, Schritt 5 braucht 4,44. Abgenommen wurde «nur der offene Schritt steht im DOM» — das ist erfüllt und zählt Knoten statt Bildschirme. Dazu drei Wegführungsbefunde: übersprungene Schritte tragen ein Erledigt-Häkchen, «Weiter» garantiert nichts, und «Zurück» kehrt nicht dorthin zurück, wo man herkam. Der Fokus-Modus, die klebende Fußleiste und der Einstieg mit drei Wegen bleiben — sie haben sich bewährt.

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

**Der Wächter kam am 2026-08-28 nach — mit der Entscheidung, die er brauchte.** Playwright steht jetzt im Extra `ui`, nicht in `dev`: `tests/test_web_overflow.py` öffnet jede Ansicht in einem Kopflos-Browser, und ohne Paket oder ohne Browser überspringt er sich. Die CI bleibt damit ohne Browser grün — kein `--deselect`, ein `skip` mit Begründung; die Zeile dazu steht im Workflow. Gemessen werden zwei Breiten (1280 und 1024) über alle vier Bereiche, alle acht Schritte des Einrichtens und alle sechs Ergebnis-Ansichten, dazu die grobe Probe ohne Ausnahmen: Die Seite selbst darf sich nicht waagerecht schieben lassen. Laufzeit rund vier Minuten.

**Der Detektor war die eigentliche Arbeit — und er hat sich beim ersten scharfen Durchlauf selbst korrigiert.** Die drei Ausnahmen aus [P1.8](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt) waren richtig, aber nicht vollständig; zwei weitere kamen aus echten Fehlalarmen dazu:

- **SVG.** In den Plotly-Diagrammen meldete jede Achsenbeschriftung 4 bis 27 px Überlauf. `clientWidth` ist für SVG-Elemente nicht definiert und liefert 0 — die Differenz war die Textbreite selbst.
- **`scrollWidth` selbst.** Die Ausnahme «absichtlich Überstehendes» auf den *Kasten* anzuwenden genügt nicht: Ein ausgeschwebtes Kind zählt weiterhin in den `scrollWidth` seines Vorfahren. Dashs eigenes Dropdown legt ein 241 px breites, unsichtbares Fokusziel in einen 96 px breiten Wrapper; die Zeitleiste meldete daraufhin 145 px Überlauf, obwohl nichts zu sehen war und nichts verrutschte. Gemessen wird deshalb nicht `scrollWidth`, sondern die rechte Kante dessen, was wirklich **im Fluss** steht — die Kästen der Kinder und die Zeilen der Textknoten. **Eine Ausnahme, die nur den Kasten kennt und nicht seine Nachkommen, ist keine.**

Damit der Wächter nicht aus dem falschen Grund grün ist — die Lehre aus P1.8 —, erzeugt `test_the_detector_would_notice_a_relapse` einen echten Überlauf und alle fünf Phantome daneben und prüft beides. Zusätzlich am laufenden System gegengeprobt: Ein langer unzerbrechlicher Wert in einer Kachel, deren `min-width`-Schutz entfernt wurde, wird mit 542 px gemeldet — also genau die Form, mit der «Standard-Ausgangslage» seine Kachel gesprengt hat.

**Ergebnis des ersten vollständigen Durchlaufs: alle Ansichten bei null.**

**Offen — und bewusst woanders:**

- **Das Auswahlfeld «Art der Änderung» in den Regelzeilen** (Schritte 4 und 5) tritt 68 px aus seiner Spalte — der Optionstext «springt auf den Wert (set)» ist breiter als die Zelle. Ein Versuch mit `min-width: 0` auf Dashs Wrapper half nachweislich **nicht** und wurde wieder entfernt, statt als wirkungslose Regel stehenzubleiben. Vorbestehend; gehört zum Umfang der Regelzeilen und damit zu [P1.2](#p12--ergebnisse-und-plots-refactoren). **Der Wächter meldet ihn nicht** — Schritte 4 und 5 sind bei beiden Breiten auf null. Warum, ist nicht nachgemessen; naheliegend ist Ausnahme 1, weil Dashs Auswahlfeld seinen Text mit `overflow: hidden` abschneidet. Das ist keine Entwarnung, sondern die Grenze dieses Wächters: Abgeschnittener Text sieht schlecht aus, ohne den Nachbarn zu schieben. Wer P1.2 anfasst, sieht dort mit eigenen Augen nach.

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

**Verfahren nachgeschärft am 2026-08-28.** Das Ergebnis dieser Gegenprobe bleibt gültig — alle drei Befunde waren echt und sind behoben. Der **Prüfumfang** war zu eng: Geprüft wurden die drei gemeldeten Befunde und die Mechanik (keine doppelte ID, «Weiter» sichtbar, Scroll auf 0, Kontraste). **Gemessen wurde keine der Zusagen selbst.** «Eine Frage auf dem Schirm» steht als Zusage in `wizard.py` und in P1.7 — hätte die Gegenprobe die Höhe jedes Schritts in Bildschirmen genommen statt seinen waagerechten Überlauf, wäre Befund 3 aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28) hier aufgefallen und nicht erst zwei Tage später. Als Regel festgehalten: **Eine Gegenprobe prüft nicht die gemeldeten Befunde, sondern die zugesagten Größen** — die Befunde sind der Anlass, nicht der Umfang.

**Abgrenzung.** Die 90 Eingabefelder unter «Systemgrößen» werden hier **umsortiert, nicht reduziert** — ihre Menge ist ein eigener Fall und bleibt bei [P1.2](#p12--ergebnisse-und-plots-refactoren). Ebenso bleibt offen, dass der Preflight bei jeder Änderung den vollen `SimulationState` aufbaut.

**Umgesetzt am 2026-08-28, in drei Commits entlang der Stufen.** Vier Dinge, die dabei über den Plan hinausgingen — drei davon Fallen, die erst am laufenden System sichtbar wurden:

- **Ein fehlender `Input` legt den ganzen Callback lahm.** Dash führt ihn **gar nicht erst aus** und meldet nur in der Browserkonsole «A nonexistent object was used in an `Input`». «Direkt zum Start» wurde auf Schritt 1 nicht gerendert — und damit tat auch «Weiter» nichts, der Zähler blieb bei «Schritt 1 von 8». Bedingt sichtbare Bedienelemente werden seither **ausgeblendet, nicht weggelassen**; das ist jetzt die sechste Dashboard-Regel in `CLAUDE.md`. Aus demselben Grund stehen «Lauf starten» und «Als Szenario speichern» in der Navigationsleiste und nicht im letzten Schritt.
- **Ein klebendes Element braucht Spielraum in seinem Elternkasten.** «Weiter» trug `position: sticky` und lag trotzdem bei y=1381 in einem 900-px-Fenster — sein Wirt war exakt so hoch wie es selbst. Das Kleben sitzt jetzt am Wirt, dessen Eltern die volle Höhe haben; gemessen y=842, ohne Scrollen sichtbar.
- **`labelStyle` wirkt seit Dash 4 nicht mehr.** Der erste Versuch, den Haken auf einer Auswahlkarte mittig zu setzen, blieb folgenlos: Dash schreibt keinen Inline-Stil mehr aufs Label (`getAttribute("style")` ist `null`). Die Stildicts in `components.py` waren tot und sind entfernt — stehengeblieben wären sie eine Falle für den Nächsten. Dieselbe Klasse wie Dashs `--Dash-*`-Ebene in P1.5.
- **Der Fokus-Modus kam aus der Benutzung, nicht aus dem Plan.** Der Plan sagte nur «Schrittfolge»; am Bildschirm zeigte sich, dass daneben eine Szene läuft, die einen *anderen* Lauf zeigt, und links Stand-Zeilen stehen, die wiederholen, was man gerade einstellt. `af-shell--focus` blendet beim Einrichten Bedienfeld, Telemetrie und Zeitleiste aus.

**Am laufenden System durchgespielt:** alle acht Schritte vorwärts, Sprung über die Schrittliste, «Direkt zum Start» ab Schritt 3 nach Schritt 8, Start aus der Schrittfolge (Kopfzeile «Simulation läuft», Fortschrittsfenster «Tick 30 von 500»). Überlauf-Durchlauf je Schritt: Schritte 1–3 und 6 ohne Befund.

**Offen und benannt:** In den Regelzeilen (Schritte 4 und 5) tritt das Auswahlfeld «Art der Änderung» 68 px aus seiner Spalte — der Optionstext «springt auf den Wert (set)» ist breiter als die Zelle. Ein Versuch mit `min-width: 0` auf dem Dash-Wrapper half nachweislich **nicht** und ist wieder entfernt statt als wirkungslose Regel stehengelassen. Vorbestehend, gehört zum Umfang der Regelzeilen und damit zu [P1.2](#p12--ergebnisse-und-plots-refactoren).

**Doku zieht mit:** `CLAUDE.md` (Architektur-Map: neue Module und Routen; die Dashboard-Regeln um den Umgang mit der Schrittfolge ergänzen), `docs/handbuch/erste-simulation.md`, `docs/handbuch/lauf-starten.md`, `docs/handbuch/lauf-konfigurieren.md`, `docs/handbuch/presets.md`, `docs/handbuch/glossar.md` (Ladebildschirm, Fortschrittsfenster, Schrittfolge), `README.md` und `dashboard/README.md` (Routentabelle).

---

### P1.9 — Der Assistent richtet ein Experiment ein 🔴 offen (Audit 2026-08-28)

**Herkunft:** Unabhängiges Audit des Einrichten-Assistenten am 2026-08-28, gemessen an einer eigenen Instanz bei 1280 × 720 und gegengelesen im Code. Vollfassung mit allen Messwerten: [`wizard_audit_2026-08-28.md`](wizard_audit_2026-08-28.md). Das Audit hat die Abnahmekriterien dieses Plans **bewusst nicht** als Maßstab genommen, sondern eigene — und genau dadurch gefunden, was die Kriterien durchgelassen haben.

**Befund in einem Satz:** Der Assistent ist ein Modell-Editor mit einem Experiment-Assistenten davor. Weil beides in derselben Schrittfolge steht, kann er weder das eine ruhig noch das andere schnell.

**Die vier tragenden Befunde:**

1. **Der Assistent beschreibt einen Lauf, der nicht stattfindet** (kritisch). [`run_single_sweep`](../src/orchestration/scenario_sweeps.py) baut seinen Runner selbst und schreibt `deterministic_only=True`, `seed=SWEEP_SEED` und `checkpoint_interval=0` fest — und ruft trotzdem `OllamaClient` für den Szenario-Text. Vom Entwurf erreicht **genau ein** Feld den Sweep-Lauf: `rounds`, als `ticks_override` ([`run_launcher.py:209`](../dashboard/run_launcher.py)). Gemessen sagt Schritt 8 nach «Szenario-Vergleich starten» wörtlich: «ausgehend von der Standard-Ausgangslage aus `configs/`, ohne Sprachmodell; die Zahlen stimmen, die Agenten-Texte sind Platzhalter» — drei Aussagen, drei Mal falsch. Dazu sechs Kacheln, die den Entwurf zeigen statt den Lauf. **Das ist Invariante 1 auf der Oberfläche verletzt:** Was der Code nicht tut, darf die Oberfläche nicht behaupten — und die Oberfläche ist die Doku, die tatsächlich gelesen wird.
2. **Fünf Bedienelemente in «optionalen» Schritten schreiben ohne Rückfrage in `configs/properties.json`** (kritisch). «Entfernen» an einem Segment, «Größe dauerhaft löschen», «Als Standard speichern», «Bevölkerung als Standard speichern», «Größe anlegen» — alle in `_handle_action` ([`config_editor/__init__.py`](../dashboard/web/config_editor/__init__.py)), alle ohne Dialog, ohne Undo, ohne Sicherung. Die Wirkung reicht über den Lauf, die Sitzung und den Nutzer hinaus. Kein Bedienfehler, sondern ein Kategorienfehler.
3. **Kein einziger der acht Schritte passt auf einen Bildschirm** (hoch). Gemessen bei 1280 × 720, sichtbare Höhe 664 px: 2,15 / 1,13 / 1,18 / **3,37** / **4,44** / 2,42 / 2,21 / 1,20 Bildschirme. Schritt 4 trägt 104 Bedienelemente unter der Überschrift «Rahmenbedingungen — bereits sinnvoll vorbelegt», Schritt 5 deren 64. Die vier mittleren Schritte sind erkennbar die alten Reiter unter neuem Namen; ihre Modulköpfe sagen es selbst («Tab «Rahmenbedingungen»»).
4. **Die Schrittliste lügt, und «Weiter» garantiert nichts** (hoch). `_rail_entry` vergibt den Zustand rein nach Position — gemessen nach «Szenario-Vergleich starten»: `["done","done","done","done","done","done","done","current"]`, also sieben Häkchen für nie gesehene Schritte. `_navigate` prüft nichts, «Weiter» ist nie gesperrt, «Lauf starten» nur während eines Laufs. Ein Wizard unterscheidet sich von einer Reiterleiste dadurch, dass «Weiter» etwas garantiert.

**Die Kriterien waren grün — schon wieder.** P1.7 hat zugesagt: eine Frage auf dem Schirm. Abgenommen wurde: nur der offene Schritt steht im DOM. Das ist erfüllt und misst Knoten statt Bildschirme. **Es ist derselbe Fehlertyp, den P1.6 an P1.1 und P1.5 gefunden und ausdrücklich als Prüfmuster notiert hat** — ein Paket später, mit demselben Ergebnis. Zweimal derselbe Fehler ist kein Zufall mehr, sondern eine Lücke im Verfahren; daraus folgt Regel 7 des Commit-Regelwerks unten.

#### Was wieder aufgemacht wird

| Paket | Entscheidung | Begründung |
| --- | --- | --- |
| [P1.1](#p11--simulation-starten-neu-bauen--erledigt-2026-08-28) ✅ | **wieder öffnen** | «Drei Entscheidungen genügen» ist erfüllt und misst das Falsche: Auf dem Sweep-Pfad sind zwei der drei wirkungslos. Zählen ersetzt nicht Wirksamkeit. |
| [P1.5](#p15--leitstand-oberfläche--erledigt-2026-08-28) ✅ | **Abnahme ergänzen** | Zonen, Theme und Zeitleiste tragen. Es fehlt eine Barrierefreiheits-Größe in den Kriterien. Kein inhaltlicher Rückbau. |
| [P1.6](#p16--einrichten-und-beobachten-trennen--erledigt-2026-08-28) ✅ | **bleibt** | Das Prinzip trägt und ist die Grundlage für den Schnitt unten. |
| [P1.7](#p17--der-ablauf-wird-die-oberfläche--erledigt-2026-08-28) ✅ | **wieder öffnen** | «Eine Frage auf dem Schirm» ist nicht gehalten (Befund 3), dazu Befund 4 und die Handwerksbefunde. |
| [P1.8](#p18--gegenprobe-zu-p17-haiko-2026-08-28--erledigt) ✅ | **Verfahren nachschärfen** | Das Ergebnis bleibt gültig, der Prüfumfang war zu eng: Die Gegenprobe hat drei gemeldete Befunde geprüft, aber keine der Zusagen **gemessen**. Genau die Messung hätte Befund 3 gefunden. |
| [P1.3](#p13--szenariogestaltung-neu-denken) | **vorziehen** | Der Sweep-Pfad ist die Ursache der Befunde 1 und 2. Ihn kosmetisch zu reparieren, ohne die Szenariogestaltung zu klären, wäre doppelte Arbeit. |
| [P3.6](#p36--stabiler-vertrag-für-den-run-launcher) | **vorziehen** | Befund 1 ist im Kern ein fehlender Vertrag zwischen Assistent, Run-Launcher und Sweeps. Ohne ihn lässt sich die Zusage aus W1.3 nicht mechanisch halten. |

Unangetastet bleiben [P1.2](#p12--ergebnisse-und-plots-refactoren) und [P1.4](#p14--landingpage-produktionsreif) — sie liegen hinter diesem Schnitt.

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
| W0.1 ✅ | Höhenwächter je Schritt in `tests/test_web_overflow.py`, gemessen in Bildschirmen. | **Erledigt 2026-08-28.** Der Wächter hält den Ist-Stand je Breite und Schritt und schlägt an, sobald ein Schritt **wächst** — und ebenso, wenn einer um mehr als 0,25 Bildschirme **schrumpft**, ohne dass der Deckel mitgezogen wird. Deckel wird in W3.5 auf `ZIEL = 1.0` gesenkt. |
| W0.2 ✅ | Wirkungstest: welche Draft-Felder erreichen auf welchem Startpfad (Einzellauf, Wiederholungen, Sweep) tatsächlich die Simulation. | **Erledigt 2026-08-28** in `tests/test_web_wirkung.py`. «Wirksam» heißt dort: *es ändert, was bei der Simulation ankommt* — gemessen als Unterschied zwischen zwei Läufen desselben Pfads, einmal mit und einmal ohne das Feld. Eine Definition ohne Annahmen über den Code. |

**Zwei Befunde, die erst diese Messung ans Licht gebracht hat** — beide standen nicht im Audit, weil sie sich am Bildschirm nicht zeigen:

* **Der Startpreis geht unterwegs verloren.** `build_custom_sweep_from_draft` wertet `base_price` korrekt aus — es kommt dort nur nie an. `launch_from_draft` schickt den Entwurf durch `RunLaunchConfig`, und diese Datenklasse hat **kein solches Feld**; der Wert fällt auf der Rundreise `draft_to_launch_config` → `launch_config_to_draft` lautlos heraus. «Startpreis selbst festlegen» im Assistenten ist über das Dashboard **wirkungslos**, über die CLI nicht. Neues Paket **W1.5**.
* **`use_seed` ohne `seed` stürzt ab.** `draft_to_launch_config` rechnet `int(draft.seed)`, sobald der Schalter an ist — bei `seed = None` ein `TypeError` statt eines Prüfbefunds. Heute unerreichbar, und zwar aus dem schlechtesten denkbaren Grund: Befund A7 schreibt beim Anzeigen von Schritt 3 stillschweigend `seed = 42`, bevor jemand den Schalter finden kann. **W5.1 räumt A7 weg und macht diesen Absturz damit erreichbar** — wer W5.1 umsetzt, fasst diese Zeile mit an. Aufgenommen als **W1.6**.

**W1 — Der Assistent sagt die Wahrheit** (kritisch, zuerst).

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W1.1 ✅ | **Entschieden am 2026-08-28 (Haiko): der Pfad deklariert seine Fixierungen.** Nicht die andere Möglichkeit — ein Vergleich rechnet alle Szenarien unter gleichen Bedingungen, sonst vergleicht er sie nicht. Falsch war nie die Festlegung, sondern ihr Schweigen. | **Erledigt 2026-08-28.** `scenario_sweeps.FESTLEGUNGEN` (drei Werte, die der Sweep einsetzt) und `UNBEACHTET` (sieben Felder, die er ignoriert) sind **die Quelle des Verhaltens**: `run_single_sweep` liest seinen Runner daraus, statt Literale zu tragen. `tests/test_web_wirkung.py` schließt den Kreis in beide Richtungen — was verworfen wird, steht im Vertrag, und was im Vertrag steht, wird verworfen. Damit ist «still verworfen» mechanisch ausgeschlossen. **Was der Nutzer davon sieht, kommt mit W1.3.** |
| W1.2 | `ticks_override` nur setzen, wenn die Länge bewusst gewählt wurde; sonst gilt die `max_ticks` des Presets. | Ein Sweep läuft mit der Länge, die Schritt 1 nennt. |
| W1.3 | Der Preflight beschreibt den **tatsächlichen** Lauf: eigener Satz und eigene Kacheln je Startpfad; nichts Wirkungsloses wird als wirksam gezeigt. Die Texte dafür stehen seit W1.1 in `FESTLEGUNGEN`/`UNBEACHTET` — je Feld ein Satz in Klartext, aus **einer** Quelle. | Der Preflight enthält nur Aussagen, die W0.2 als wirksam ausweist; jedes vorgegebene Feld wird beim Vergleich als vorgegeben dargestellt, nicht als Wahl. **Dazu gehört der Satz, den der Vertrag nicht abdeckt:** Der Szenariotext am Ende jedes Sweeps entsteht mit `prefer_llm=True` — wer «ohne Sprachmodell» wählt, erreicht Ollama trotzdem (`SZENARIOTEXT_NUTZT_LLM`). |
| W1.4 | Der Weg «Szenario-Vergleich» führt nicht mehr an der Längenfrage vorbei — über den Schritt oder als bewusste Bestätigung im Preflight. | Kein Startpfad überspringt eine Frage, deren Antwort er verwendet. |
| W1.5 | `base_price` erreicht den Lauf auch über das Dashboard — entweder als Feld in `RunLaunchConfig` oder indem der Launcher den Entwurf gar nicht erst durch diese Rundreise schickt. | `TestDerStartpreisGehtUnterwegsVerloren` dreht sich um: Der Startpreis wirkt, und `ERWARTET` führt ihn. |
| W1.6 ✅ | `use_seed` ohne `seed` ergibt einen Prüfbefund, keinen `TypeError`. | **Erledigt 2026-08-28.** `validate_draft` prüft das **vor** dem Bauen des States und hängt den Befund ans Feld `seed`, wo man ihn beheben kann. Ein Test stellt zusätzlich nach, dass der Absturz ohne diese Prüfung wirklich stünde — eine Meldung allein belegt nicht, dass sie nötig war. Die Sperre für W5.1 ist damit weg. |

**W2 — Der Assistent lügt nicht über den Fortschritt.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W2.1 | Drei Zustände in der Schrittliste statt zwei: offen, besucht, übersprungen. Häkchen nur für tatsächlich Besuchtes. | Nach «Szenario-Vergleich» trägt kein übersprungener Schritt ein Häkchen. |
| W2.2 | Validierungstor: «Weiter» sperrt, solange der Schritt Blocker hat, mit Begründung am Feld; «Lauf starten» sperrt bei Befunden aus `validate_draft`, mit Sprungmarke zum betroffenen Schritt. | Ein ungültiger Wert kommt nicht am Schritt vorbei. |
| W2.3 | «Zurück» folgt einem Navigationsverlauf statt `current - 1`. | Aus Schritt 8, betreten über den Einstieg, führt «Zurück» auf den Einstieg — nicht auf «Technik». |

**W3 — Der Schnitt.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W3.1 | Modell-Editor als eigener Bereich; `macro` und `micro` ziehen dorthin um, im Verhalten unverändert. | Reiner Umzug, keine Verhaltensänderung — eigener Commit vor allem, was danach daran geändert wird (Regel 6). |
| W3.2 | Schreiben in `configs/` nur noch im Modell-Editor, nur mit Bestätigung, mit Anzeige der Reichweite («gilt ab sofort für alle Läufe»). | Kein Schreibpfad in `configs/` ist aus dem Assistenten erreichbar. |
| W3.3 | Die Faktorlage (sieben Auswahlen) bleibt als **eine** Frage im Assistenten — sie gehört zum Experiment, nicht zum Modell. | Ein Bildschirm, sieben Auswahlen. |
| W3.4 | Schritt 1: Presets als Kachelraster mit Kennzahl statt zehn gestapelter Radiokarten. | Unter 1,0 Bildschirm bei 1280 × 720. |
| W3.5 | Deckel in W0.1 auf 1,0 Bildschirm senken. | Der Wächter ist scharf, nicht dokumentierend. |

**W4 — Was ein Experiment ausmacht.**

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W4.1 | Lauf-Identität nach vorn: Name und Fragestellung mit Vorschlag, auf **jedem** Startpfad. | Kein Lauf trägt den Vorgabenamen, ohne dass jemand ihn gesehen hat. |
| W4.2 | Delta-Ansicht im Prüfschritt: «Was weicht vom Standard ab», je Zeile mit Sprung und Einzelrücknahme. | Jede Abweichung ist gelistet und einzeln rücknehmbar — nicht nur «alles zurücksetzen». |
| W4.3 | Laufzeitschätzung aus `run_metadata.json` vergangener Läufe, vor dem Start und als Restzeit während des Laufs. | Ein Spannenwert je Rechenmodus, kein Punktwert. **Damit fällt zugleich die offene Zeitfrage aus [«Was bewusst nicht in diesem Plan steht»](#was-bewusst-nicht-in-diesem-plan-steht)** — die geschätzten Angaben in `docs/handbuch/lauf-starten.md` bekommen eine gemessene Grundlage. |
| W4.4 | Reproduzierbarkeit vor dem Start: Seed, Codestand, Config-Fingerabdruck — dieselben Größen, die P0.6 danach schreibt. | Was `run_metadata.json` hinterher festhält, steht vorher auf dem Schirm. |
| W4.5 | `runner.cancel()` und ein Abbruch-Knopf im Ladebildschirm. `dashboard/web/runner.py` kennt heute `start`, `poll`, `progress`, `forget` — kein `cancel`. | Ein laufender Lauf lässt sich beenden, ohne den Prozess zu töten. |

**W5 — Handwerk.** W5.1 und W5.2 hängen an nichts und dürfen vorgezogen werden — sie beheben einen aktiv falschen Zustand.

| # | Was zu tun ist | Fertig wenn |
| --- | --- | --- |
| W5.1 | Render-Rückfälle schreiben nicht mehr in den Entwurf. Gemessen: Schritt 3 anzuzeigen schreibt `seed: null → 42`, weil `mode_step` das Feld mit `DEFAULT_SEED` rendert und `_sync` den gerenderten Wert zurückliest. Ein fehlender Wert wird als fehlend dargestellt, nicht als Literal erfunden. | AST-Wächter über `dashboard/web/`, analog `test_cost_pressure_source.py`: jeder Literal-Rückfall in einem Feld-Renderer wird gemeldet, Ausnahmen mit Begründung in einer `AUSNAHMEN`-Liste. **Der brisanteste Fall wartet schon:** `micro._FEEDBACK_FINE` hält `marginal_cost_fraction` mit Rückfall 0,33, während `configs/properties.json` 0,25 liefert — genau der Widerspruch, den `CLAUDE.md` unter [P4.2](#p42--suite-aufräumen-und-verlässlich-machen) als ungeklärt führt. |
| W5.2 | `touched()` vergleicht gegen den normalisierten Entwurf statt gegen den rohen. | Ohne Eingabe bleibt «Letzte Einstellungen weiterverwenden» gesperrt — auch nach einem Neuladen. Heute schaltet allein das Anzeigen von Schritt 3 den Weg frei, und der Session-Store trägt das über den Reload. |
| W5.3 | Barrierefreiheit: `aria-current="step"`, Live-Region für Schrittwechsel und Statusmeldungen, Fokus auf die Schrittüberschrift, `fieldset`/`legend` um jede Radiogruppe. Gemessen: **0** `aria-live`-Regionen im ganzen Dokument. | Ein Test über diese vier Größen; Ziel WCAG 2.1 AA für die Schrittfolge. Für Hochschul- und B2B-Beschaffung ist das kein Schönheitsfehler. |
| W5.4 | Breite je Schritt statt einer Breite für alles. Gemessen `240px 760px` bei 1040 px Zone — zu breit für Schritt 2 mit drei Feldern, zu schmal für Schritt 4 mit 104. | Kein Schritt unter 60 % oder über 100 % Spaltenausnutzung. |
| W5.5 | Mobil: Schrittliste als kompakter Fortschrittsbalken statt acht gestapelter Knöpfe, Fußleiste einzeilig (heute 133 px bei 375 px Breite). | Fußleiste unter 72 px bei 375 px Breite. |
| W5.6 | Gewichtung der drei Wege des Einstiegs nach Häufigkeit. | Fachurteil, keine Messung — bewusst als solches gekennzeichnet. |

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
3. **Jeder Commit ist für sich lauffähig und grün.** `pytest`, `ruff check .` und `black --check .` laufen vor jedem **Commit**, nicht erst vor dem Push.
4. **Jeder Verhaltens-Commit bringt seinen Test mit** — im selben Commit, nicht im nächsten. Ein nachgereichter Test prüft, was gebaut wurde, statt was zugesagt war.
5. **Doku im selben Commit** ([Doku-Pflicht](../CLAUDE.md#doku-pflicht)). Bleibt sie bewusst unverändert, steht der Grund in der Commit-Message.
6. **Refactoring und Verhaltensänderung nie im selben Commit.** W3.1 ist deshalb ein reiner Umzug; alles, was danach am Umgezogenen geändert wird, ist ein eigener Commit.
7. **Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung.** Wer «passt auf einen Bildschirm» zusagt, misst Bildschirme. Wer «drei Entscheidungen genügen» zusagt, misst, ob die drei wirken. Das ist die Lehre aus P1.6 **und** aus P1.9 — derselbe Fehler, zweimal, mit grünen Kriterien.
8. **Gepusht wird nicht automatisch.** Commits bleiben lokal, bis Haiko sie selbst pusht.

---

## Phase 2 — Modellsubstanz (Claims und Code in Deckung bringen)

Diese Punkte entscheiden, ob die wissenschaftlichen Aussagen einem Fachprüfer standhalten. Solange sie offen sind, gehören die Formulierungen in Pitch, README und Handbuch abgeschwächt.

### P2.1 — Buchungsmodell: echte Ziehung statt Schwellwert

**Befund:** Das "Logit-Modell" ist keines. Es wird `p = 1/(1+e^-u)` gerechnet und dann `p >= 0.5` geprüft — weil die Sigmoid monoton ist, ist das mathematisch identisch mit `u >= 0`. Der Logit-Teil tut nichts; es wird nie gegen die Wahrscheinlichkeit gezogen. Die Koeffizienten (`base_utility = 2.0`, `/100.0`, `*1.5`) sind handgesetzt, nicht geschätzt.

**Fundstelle:** [`src/population/population_sampler.py:355`](../src/population/population_sampler.py) (`_booking_probability`), Schwelle `DEFAULT_LOGIT_THRESHOLD = 0.5` in Zeile 23.

**Was zu tun ist:** Gegen die Wahrscheinlichkeit ziehen (`rng.random() < p`) mit einem aus dem Lauf-Seed abgeleiteten Strom, damit Reproduzierbarkeit erhalten bleibt. Koeffizienten nach `configs/properties.json` auslagern und ihre Herkunft dokumentieren — die Literatur liegt bereits in `docs/research/literature/` (Preiselastizitäten im Luftverkehr).

**Fallstrick (2026-08-26) — "mit dem Lauf-Seed" reicht nicht:** `evaluate_booking` bekommt heute **überhaupt keinen** RNG, und `run_population_tick` wird in jedem Tick mit demselben `state.config.seed` aufgerufen ([`environment_node.py:157`](../src/orchestration/environment_node.py)). Wer dort naiv `rng.random() < p` mit dem Lauf-Seed einbaut, zieht in jedem Tick dieselbe Zahlenfolge: es buchen immer dieselben Individuen, und die Buchungsrate wird zur Stufenfunktion. Reproduzierbar, aber falsch — und schwer zu bemerken, weil die Zahlen plausibel aussehen. Nötig ist ein Strom pro **(Lauf, Tick)**, z. B. `default_rng(SeedSequence([seed, tick]))`. Der Einstiegspunkt existiert schon: `run_population_tick` nimmt `current_tick` entgegen und **benutzt es nirgends** (einziges Vorkommen: die Signatur in Zeile 508).

**Zur Vorbedingung (richtiggestellt am 2026-08-26):** `_seed_runtime` ([`simulation_runner.py:269-281`](../src/orchestration/simulation_runner.py)) seedet das globale `np.random`, gezogen wird über `default_rng` — die Funktion ist also tatsächlich wirkungslos und gehört aufgeräumt. Die Reproduzierbarkeit des Samplers hängt aber **nicht** daran: `state.config.seed` wird explizit durchgereicht (`environment_node.py:157` → `run_population_tick` → `_rng`). Die frühere Formulierung, ohne diese Korrektur sei "die Reproduzierbarkeit mit dem ersten echten Zufall weg", trifft nicht zu. Das eigentliche Risiko ist der Fallstrick oben.

**Fertig wenn:** Buchungsentscheidungen sind stochastisch, unterscheiden sich zwischen Ticks, sind bei gleichem Seed reproduzierbar, und jeder Koeffizient hat eine benannte Quelle. Ein Test zeigt beides: gleicher Seed gleiches Ergebnis, aufeinanderfolgende Ticks unterschiedliche Ziehung.

**Doku zieht mit:** `docs/handbuch/kaufentscheidung.md`, `docs/handbuch/saettigung.md`, `README.md`, `CLAUDE.md` (Glossar "Logit-Modell").

### P2.2 — CIB: Impact-Balance-Kriterium implementieren

**Befund:** Die Konsistenzprüfung ist nicht der Weimer-Jehle-Algorithmus. Sie prüft einzelne Zellen gegen einen Schwellwert und summiert Konflikte. Das eigentliche CIB-Kriterium ist die **Impact Balance**: ein Szenario ist konsistent, wenn für jeden Faktor der gewählte Zustand die Summe der eingehenden Einflüsse maximiert. Diese Gleichgewichtsbedingung steht nirgends im Code.

**Fundstelle:** [`src/cib/scenario_consistency.py:99`](../src/cib/scenario_consistency.py) (`check_consistency`, `compute_consistency_score`).

**Was zu tun ist:** Impact-Balance als eigenständige Prüfung implementieren: pro Faktor die Einflusssumme je Zustand bilden, prüfen ob der gewählte Zustand das Maximum ist, Szenario nur dann konsistent nennen. Die bisherige Heuristik darf als zusätzlicher Score bleiben — aber unter eigenem Namen.

**Aufwand (geprüft am 2026-08-26):** kleiner als der Umfang dieses Pakets vermuten lässt. `derive_scenarios` iteriert bereits über alle 2^7 = 128 Kombinationen ([`scenario_consistency.py:209`](../src/cib/scenario_consistency.py)) — die Impact-Balance-Prüfung ist dort eine Ergänzung von rund zwanzig Zeilen innerhalb der bestehenden Schleife.

**Vorbedingung aus P0.2 — seit 2026-08-26 belegt, nicht mehr nur erwartet:** F7 wird als **Geopolitische Stabilität** geführt, und die Neubewertung der 48 Zellen hat den Passive-Score von 32 auf **19** gedrückt — mit Abstand der niedrigste aller sieben Faktoren. F7 ist damit messbar ein weitgehend exogener Faktor — er wirkt auf das System, wird aber kaum zurückbeeinflusst. Unter Impact Balance hieße das, dass sein Zustand nicht durch das Gleichgewicht bestimmt wird, sondern durch Annahme. Der saubere Umgang: F7 pro Szenario als **fixierten Deskriptor** behandeln und die Impact Balance über F1–F6 rechnen — CIB sieht das ausdrücklich vor. Faktisch ist F7 durch die Ölpreis-Regel heute schon ein exogener Schalter; die Methode zöge damit nur nach, was die Engine tut. Diese Festlegung gehört vor die Umsetzung.

**Fallstrick (2026-08-26) — vorher entscheiden, sonst bricht P1.3:** Echte Impact Balance liefert **null, eine oder viele** konsistente Konstellationen; die heutige Heuristik liefert immer eine sortierte Liste, aus der `top_n=3` gegriffen wird. Das Produktversprechen ist aber ein festes **Tripleset** (Trendfortsetzung / Strukturwende / Krisenkonflikt). Was passiert, wenn weniger als drei Szenarien das Kriterium erfüllen — oder gar keines —, muss **vor** der Umsetzung entschieden sein: entweder das Tripleset aufgeben und zeigen, was tatsächlich konsistent ist, oder die konsistenten Szenarien als solche kennzeichnen und den Rest sichtbar als "nächstbeste, nicht konsistent" danebenstellen. Ohne diese Entscheidung bricht P2.2 die Ergebnisdarstellung aus P1.3 und die Außendarstellung gleich mit.

**Fertig wenn:** Für ein bekanntes Referenzszenario stimmt das Ergebnis mit dem Impact-Balance-Kriterium überein; Tests decken konsistente und inkonsistente Fälle ab **und** den Fall "weniger als drei konsistente Szenarien".

**Doku zieht mit:** `docs/cib_role.md`, `docs/cib_rationale.md`, `docs/handbuch/cib.md`, `CLAUDE.md` (Glossar).

### P2.3 — Matrix-Provenienz herstellen

**Befund:** Alle 168 Zellen in `cib_frozen.json` haben ein leeres `reasoning`-Feld; `metadata.source` sagt `expert_defined_aviation_domain_v2` (Basis: Vorlesungsfolien, Experte = das Team selbst). Für einen Prototyp legitim — aber die Kalibrierung ist genau das Asset, das später verkauft wird.

**Fundstelle:** [`configs/cib_frozen.json`](../configs/cib_frozen.json), erzeugt von [`scripts/rebuild_cib_frozen.py`](../scripts/rebuild_cib_frozen.py).

**Zusätzlich (2026-08-26):** Neben dem befüllten `cells`-Dict liegt in derselben Datei ein zweites, durchgängig leeres `entries: []`. Eine unbenutzte Struktur mitten im eingefrorenen Asset — beim Durchgehen mit entfernen oder befüllen, je nachdem, wofür sie gedacht war.

**Was zu tun ist:** Pro Zelle eine Begründung und eine Quelle eintragen — beim Durchgehen fallen erfahrungsgemäß auch inhaltliche Fehler auf. Das Skript so erweitern, dass es leere `reasoning`-Felder als Fehler meldet statt sie zu erzeugen. Die Matrix bleibt eingefroren (Invariante 3). Sinnvoll gemeinsam mit P0.2 zu erledigen — beim Durchgehen der Zellen fällt die F7-Entscheidung ohnehin an.

**Fertig wenn:** Keine Zelle ohne Begründung; `metadata` nennt Methode und Bewertungsdatum.

**Doku zieht mit:** `docs/cib_rationale.md`, `docs/handbuch/cib.md`.

### P2.4 — Population altert nicht

**Befund:** `age` wird beim Sampling einmal gezogen und danach nie fortgeschrieben. Über einen langen Lauf bleibt die Bevölkerung eingefroren, während Preise, Regulierung und Werte sich bewegen — die Altersgruppen-Statistik beschreibt dauerhaft den Startzustand.

**Fundstelle:** [`src/population/population_sampler.py:173-229`](../src/population/population_sampler.py) (Sampling), Auswertung Zeile 436-444, Modell [`src/models/population_models.py:42`](../src/models/population_models.py).

**Was zu tun ist:** Klären, was ein Tick demografisch bedeuten soll — **ohne** Kalendersemantik einzuführen (Invariante 5). Optionen: Alterung als Property mit konfigurierbarer Rate, Kohortenwechsel bei definierten Tick-Abständen, oder bewusst dokumentieren, dass die Population statisch ist. Die dritte Option ist die billigste und für kurze Läufe vertretbar — dann muss sie aber im Handbuch stehen.

**Fertig wenn:** Entscheidung getroffen, im Code umgesetzt oder im Handbuch als Grenze benannt.

**Doku zieht mit:** `docs/handbuch/akteure.md`, `docs/handbuch/grenzen.md`, `docs/handbuch/tick-und-lauf.md`.

### P2.5 — State Explorer: Grounding durchsetzen statt darum bitten

**Befund (neu am 2026-08-26):** Der State Explorer ist im Glossar als "grounded Q&A ausschließlich über abgeschlossene Run-Daten — keine erfundenen Zahlen" beschrieben. Durchgesetzt wird davon nichts: `build_grounded_context_block` baut einen Kontextblock, `ask()` reicht ihn samt Frage ans LLM weiter und gibt die Antwort unverändert zurück. Ob die Antwort nur Zahlen aus diesem Block enthält, prüft niemand — die Zusage ist ein Prompt, keine Schranke. Dieselbe Klasse wie P2.1 und P2.2: ein Claim, den der Code nicht einlöst, nur an der Oberfläche, an der ein Kunde ihn zuerst ausprobiert.

**Fundstelle:** [`src/reporting/state_explorer.py:241`](../src/reporting/state_explorer.py) (`build_grounded_context_block`), [`:323-334`](../src/reporting/state_explorer.py) (`build_prompt`, `ask`), Ansicht in [`dashboard/web/views/explorer.py`](../dashboard/web/views/explorer.py).

**Was zu tun ist:** Nach dem LLM-Aufruf die Zahlen aus der Antwort ziehen und gegen die Zahlen im Kontextblock abgleichen. Was sich nicht wiederfindet, wird markiert oder die Antwort zurückgewiesen — welche der beiden Härten die richtige ist, ist eine Produktentscheidung und gehört ins Paket. Bis dahin die Formulierung im Glossar und im Handbuch abschwächen (siehe die Regel "Was der Code nicht tut, darf die Doku nicht behaupten").

**Fertig wenn:** Eine Antwort mit einer nicht im Kontext belegten Zahl wird erkannt; Tests decken den belegten und den erfundenen Fall ab.

**Doku zieht mit:** `docs/handbuch/abfrage.md`, `docs/handbuch/zahlen-und-sprache.md`, `CLAUDE.md` (Glossar "State Explorer").

---

## Phase 3 — Engine-Härtung

Fallen, die heute niemanden stören und beim nächsten Feature zuschlagen. Jedes Paket ist klein; zusammen entscheiden sie, ob die Engine trägt.

### P3.1 — System-Properties täuschen keine Laufzeitwerte mehr vor

**Befund:** Für Properties mit `source in {"runtime","computed"}` (z. B. `provider_markup`, `ticket_price`) liefert `resolve_system_properties` laut eigenem Docstring die statische Trajektorien-Baseline, nicht den Laufzeitwert. Folgenlos nur, solange keine ausgelieferte Regel diese IDs per `system_property`-Bedingung referenziert — eine neue Regel darauf würde still gegen eine veraltete Zahl prüfen.
**Fundstelle:** [`src/market/property_engine.py:127-136`](../src/market/property_engine.py).
**Was zu tun ist:** **Vorgabe (2026-08-26): den Zugriff hart ablehnen.** Eine unbekannte oder laufzeitgebundene Property in einer `when`-Bedingung wird ein Konfigurationsfehler, keine stille Baseline. Grund: Laufzeitwerte durchzureichen macht die Regelauswertung innerhalb eines Ticks reihenfolgeabhängig — `apply_factor_rules_at_tick_start` läuft **vor** der Preisberechnung in `environment_node._run_population_tick`, eine Regel auf `ticket_price` würde also je nach Einhängepunkt gegen den Preis von vorhin oder von jetzt prüfen. Das ist eine Modellentscheidung, keine Implementierungsdetailfrage, und sie gehört nicht nebenbei getroffen. Wer die Laufzeitwerte später wirklich braucht, führt sie mit einer bewussten Tick-Phase ein. Zusammen mit P0.4 erledigen — dieselbe Regelmechanik, und dort wird ohnehin festgelegt, dass unbekannte Bedingungstypen laut fehlschlagen.
**Fertig wenn:** Eine Regel, die `ticket_price` oder `provider_markup` per `system_property` referenziert, wird beim Laden mit klarer Meldung abgewiesen statt still gegen eine Baseline zu prüfen. **Doku:** `docs/handbuch/ref-config.md`.

### P3.2 — Checkpoint-Version wirklich prüfen

**Befund:** `checkpoint_version` wird in jedes Checkpoint-Metadatum geschrieben (`= 2`), aber nirgends zurückgelesen — `CheckpointManager.load` ignoriert `payload["metadata"]` komplett. Das Feld täuscht eine Versionsprüfung vor, die es nicht gibt.
**Fundstelle:** [`src/orchestration/checkpoint_manager.py:26`](../src/orchestration/checkpoint_manager.py).
**Was zu tun ist:** Beim Laden die Version prüfen und bei Mismatch klar abbrechen (Migration erst, wenn es eine zweite Version gibt).
**Fertig wenn:** Ein Checkpoint mit fremder Version wird mit verständlicher Meldung abgelehnt, Test dazu. **Doku:** `docs/handbuch/ref-ausgaben.md`.

### P3.3 — Fehlermeldungen, die auch greifen

**Befund:** Zwei Stellen, an denen Fehlerbehandlung nur so aussieht: In `langgraph_workflow` steht ein `try: pass` mit `except`, das nie feuern kann — die beabsichtigte freundliche Meldung bei fehlendem `langgraph` bleibt aus, stattdessen kommt später ein roher `ImportError`. In `create_graph.py` verschluckt ein `except Exception: pass` auch den absichtlich re-raisten Graph-Build-Fehler, und das Skript schreibt trotzdem ein statisches `graph.json`.
**Fundstelle:** [`src/orchestration/langgraph_workflow.py:41-44`](../src/orchestration/langgraph_workflow.py), [`langgraph_studio/create_graph.py:16-24`](../langgraph_studio/create_graph.py).
**Dazugekommen aus der P0.1-Gegenprobe (2026-08-26): der dritte Fall ist die CLI.** Seit P0.3 weist ein Lauf mit kaputter Config sauber ab — im Dashboard als roter Kasten mit allen Befunden, auf der CLI als **roher Python-Traceback**. `main()` in [`src/run_simulation.py`](../src/run_simulation.py) lässt `ValidationError` einfach durchschlagen; wer `--temperature 99` tippt, sieht zwanzig Zeilen Stack, in denen die eigentliche Meldung untergeht, und bekommt keinen sprechenden Exit-Code. Die Prüfung ist richtig, ihre Darstellung nicht.

**Was zu tun ist:** Echten Import in den `try`-Block ziehen; im Studio-Skript den Build-Fehler durchreichen statt ein irreführendes `graph.json` zu schreiben. `ValidationError` in `main()` abfangen und als Fehlerliste auf `stderr` ausgeben, mit Exit-Code ungleich 0 statt Traceback.
**Fertig wenn:** Fehlendes `langgraph` erzeugt die gemeinte Meldung; ein kaputter Graph-Build bricht sichtbar ab; eine kaputte Config auf der CLI erzeugt dieselbe lesbare Liste wie im Dashboard. **Doku:** `docs/handbuch/fehlerbilder.md`, `README.md` (CLI).

### P3.4 — LLM-Konfiguration zentralisieren

**Befund:** Modellname `"llama3.2"` steht in **10 Produktionsdateien** (nachgezählt am 2026-08-25, das Audit sprach von sieben Stellen), der Endpoint uneinheitlich als `http://localhost:11434` in sieben und `http://127.0.0.1:11434` in zwei Dateien. Bemerkenswert: die beim Dash-Umbau **neu** entstandenen Module `config_editor/compute_mode.py` und `config_editor/llm_pipeline.py` haben die Hartkodierung geerbt — das Finding wächst mit jedem Modul weiter.
**Fundstelle:** `src/run_simulation.py`, `src/llm/llm_client.py`, `src/models/state_models.py`, `src/orchestration/langgraph_adapter.py`, `dashboard/config_catalog.py`, `dashboard/llm_status.py`, `dashboard/run_browser.py`, `dashboard/run_launcher.py`, `dashboard/web/config_editor/compute_mode.py`, `dashboard/web/config_editor/llm_pipeline.py` (plus `tests/test_web_compute_mode.py`, `tests/test_web_layout.py`).
**Verschärft am 2026-08-26 (Fund aus der P0.3-Nachprüfung):** Es geht nicht nur um verstreute Defaults, sondern um ein Feld, das gar nichts tut. `state.config.llm` (`model`, `temperature`, `max_tokens`) wird von **keinem Laufpfad gelesen** — die einzigen Leser sind `langgraph_adapter.py` für die Studio-Schema-Defaults. Der echte Client entsteht aus `RunLaunchConfig` bzw. den CLI-Argumenten. Sichtbarster Beleg: `configs/simulation_config.json` führt `llm.model: "llama3"`, während überall sonst `"llama3.2"` steht — und niemandem fällt es auf, weil der Wert nirgends ankommt.

**Dazugekommen aus der Gegenprobe zu P0.4–P0.6 (2026-08-27): `OllamaConfig` liest keine einzige Umgebungsvariable.** Beim Nachstellen eines Sweeps gegen einen toten Endpunkt sollte `OLLAMA_BASE_URL=http://127.0.0.1:9` den Endpunkt umlenken — im Vorfall stand trotzdem `http://127.0.0.1:11434`. Grund: [`OllamaConfig`](../src/llm/llm_client.py) trägt reine Dataclass-Defaults; die Env-Übersetzung sitzt ausschließlich in `LocalOllama` (`studio_helpers.py`). Jeder Aufrufer, der `OllamaClient(OllamaConfig())` direkt baut — der Sweep-Pfad tut genau das — ignoriert `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TEMPERATURE` und `OLLAMA_MAX_TOKENS` stillschweigend. `OLLAMA_READ_TIMEOUT` und `OLLAMA_RETRIES` werden dagegen gelesen, aber erst im `call`. Die Variable zu setzen und nichts zu bewirken ist dieselbe Klasse von Problem wie die hartcodierten Defaults selbst. Gehört in dieses Paket.

**Dazugekommen aus der P0.1-Gegenprobe (2026-08-26): `get_llm()` wählt still den Mock.** P0.1 hat den stillen Mock **bei Fehlern** beseitigt — die Auswahl davor ist geblieben. [`studio_helpers.get_llm()`](../src/llm/studio_helpers.py) fällt am Ende seiner Kette kommentarlos auf `MockLLM()` zurück, wenn weder `OLLAMA_MODEL` noch `LLAMA_HTTP_URL` noch `LLAMA_TRANSFORMERS_MODEL` gesetzt ist. Zwei Aufrufer hängen noch daran: [`langgraph_workflow.py:48`](../src/orchestration/langgraph_workflow.py) (der Graph für LangGraph Studio) und [`run_scenario_generator/cli.py:33`](../src/reporting/run_scenario_generator/cli.py). Wer Studio ohne gesetzte Umgebung startet, bekommt erfundene Agenten-Antworten, ohne sie angefordert zu haben — kein `--mock-llm`, kein Hinweis, und nach der Definition aus Invariante 1 auch kein „Ausfall", weil nie ein Aufruf gescheitert ist. Der bewusste Mock (`--mock-llm`, «Ohne Sprachmodell») ist davon unberührt und richtig so.

**Was zu tun ist:** Eine Defaults-Quelle (Config plus `.env`-Override), alle Stellen darauf ziehen — und dabei `state.config.llm` entweder wirklich anschließen (Draft und CLI schreiben hinein, der Client liest daraus) oder ersatzlos entfernen. Halb stehenlassen ist die schlechteste der drei Möglichkeiten. Fällt mit der Client-Zusammenführung aus P0.1 zusammen. **Dazu die Backend-Auswahl entscheidbar machen:** `get_llm()` sagt über `logging`, welches Backend es gewählt hat, und der Griff zum Mock passiert nur auf ausdrückliche Ansage (Parameter oder Umgebungsvariable) statt als letzter Zweig einer `if`-Kette.
**Fertig wenn:** Ein Endpoint-Wechsel erfordert genau eine Änderung, und kein Codepfad rechnet mit dem Mock, ohne dass es jemand angefordert hat oder mindestens im Log steht. **Doku:** `README.md` (Umgebung), `docs/handbuch/ref-config.md`.

### P3.5 — Stille Klemmungen und Debug-Ausgaben

**Befund:** `threshold` und `max_contributions_per_agent` werden ohne Warnung auf einen Wunschbereich geklemmt — wer bewusst `threshold=1` setzt, bekommt stillschweigend 3. Dazu acht `print()`-Debugausgaben im Scheduler, die bei jedem Tick unbedingt laufen.
**Fundstelle:** [`src/agents/redebedarf_scheduler.py:73,75`](../src/agents/redebedarf_scheduler.py), [`src/agents/scheduler_node.py`](../src/agents/scheduler_node.py) (8 Vorkommen).
**Was zu tun ist:** Klemmung protokollieren oder als Konfigurationsfehler abweisen; `print()` durch `logging` mit Level-Guard ersetzen.
**Reihenfolge (2026-08-26):** **nicht vor P0.1.** Das Fortschritts-Log des Dashboards wird ausschließlich von `print()` gespeist (`run_launcher.py:397` leitet `stdout` in einen Tee um). Der Logging-Handler, der in denselben Tee schreibt, entsteht in P0.1; landet P3.5 vorher, verschwinden die Scheduler-Zeilen aus dem Live-Log, ohne dass jemand einen Fehler sieht.
**Fertig wenn:** Ein geklemmter Wert erzeugt eine sichtbare Warnung; ein normaler Lauf ist auf stdout still, und das Fortschritts-Log im Dashboard zeigt weiterhin, was es vorher zeigte. **Doku:** `docs/handbuch/ref-config.md`, `docs/handbuch/akteure.md`.

### P3.6 — Stabiler Vertrag für den Run-Launcher

**Befund:** `run_launcher` importiert drei unterstrichs-präfixierte Funktionen aus `run_simulation` (`_build_run_args`, `_save_run_outputs`, `_write_multi_run_summary`). Kein stabiler Vertrag — ein Refactor der internen Helper bricht den Launcher unbemerkt.
**Fundstelle:** [`dashboard/run_launcher.py:168`](../dashboard/run_launcher.py).
**Was zu tun ist:** Öffentliche Schnittstelle in `src/run_simulation.py` definieren und den Launcher darauf ziehen.
**Fertig wenn:** Kein Dashboard-Modul importiert mehr Unterstrich-Namen aus `src/`. **Doku:** `CLAUDE.md` (Architektur-Map, Service-Layer-Absatz).

> **Vorgezogen am 2026-08-28** (aus [P1.9](#p19--der-assistent-richtet-ein-experiment-ein--offen-audit-2026-08-28)): Der fehlende Vertrag ist nicht nur ein Refactor-Risiko — er ist die Ursache dafür, dass der Assistent Felder erfragt, die der Sweep-Pfad still verwirft. Ohne eine öffentliche Schnittstelle, die sagt, **was ein Startpfad entgegennimmt**, lässt sich W1.1 nicht mechanisch halten.

---

## Phase 4 — Testfundament

Über 500 Tests sind eine gute Grundlage, aber die Suite hat drei Eigenschaften, die beim Ausbau bremsen. (Die Zahl stand hier bis 2026-08-26 als "267" und in `CLAUDE.md` als "~330"; `pytest --collect-only` sammelt tatsächlich 506. Genau diese Drift ist der Anlass für P4.3.)

### P4.1 — Gemeinsame Fixtures

**Befund:** Kein `tests/conftest.py`; stattdessen 32 Vorkommen von `tempfile.mkdtemp(...)` mit `try/finally: shutil.rmtree(...)` über fünf Dateien, und `class MockLLM` vierfach near-identisch definiert.
**Fundstelle:** `tests/test_checkpoint_manager.py` (2), `test_dashboard_service.py` (9), `test_figure_generator.py` (4), `test_run_scenario_generator.py` (12), `test_state_explorer.py` (5); MockLLM in `test_agent_node.py`, `test_parallel_round.py`, `test_simulation_runner_e2e.py`, `debug_run_sequential.py`.
**Was zu tun ist:** `conftest.py` mit einem MockLLM-Fixture anlegen, Temp-Verzeichnisse auf das eingebaute `tmp_path` umstellen.
**Fertig wenn:** Kein Test legt mehr manuell ein Temp-Verzeichnis an; MockLLM existiert einmal. **Doku:** `README.md` (Tests-Abschnitt).

### P4.2 — Suite aufräumen und verlässlich machen

**Befund:** Uneinheitlicher Stil (16 Dateien funktional, drei `unittest.TestCase` ohne technischen Grund), `sys.path.append` in drei Dateien seit der Paketstruktur überflüssig, und `debug_run_sequential.py` ist gar kein Test (null `test_*`-Funktionen, wird von pytest nicht eingesammelt) — täuscht Abdeckung vor.

**Verifiziert am 2026-08-25, zwei Korrekturen am bisherigen Bild:**

1. Die beiden Sweep-Tests **hängen** ohne Ollama, sie schlagen nicht fehl — ein Lauf brach nach über sieben Minuten ohne Ergebnis ab. Das blockiert jeden vollständigen Testlauf, nicht nur zwei Zeilen im Report.
2. `test_market_rules_resolve_marginal_cost_fraction` ist **kein Code-Bug**. Der Test erwartet `0.33` (den Default aus `market_feedback.py`, bis P0.4 `market_rules.py`), `configs/properties.json` liefert `0.25`, und die Auflösung arbeitet korrekt — der Config-Wert gewinnt, wie gewollt. Zu entscheiden ist nur, welcher Grenzkostenanteil fachlich stimmt.

**Fundstelle:** `tests/test_scenario_sweeps.py:119,205`, `tests/test_market_feedback.py:94`, `tests/debug_run_sequential.py`, `tests/test_parallel_round.py`, `tests/test_simulation_runner_e2e.py`, `tests/test_agent_node.py`, `tests/test_save_final_narrative.py`.

**Ergänzung am 2026-08-26 — die CI hängt mit drin:** [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) deselektiert bereits genau diese drei Tests. Der Kommentar dort nennt `test_market_rules_resolve_marginal_cost_fraction` weiterhin "a real pre-existing bug" — also genau die Fehlbewertung, die oben korrigiert wurde. Die drei `--deselect`-Zeilen sind der eigentliche Grund, warum das Problem so lange unbemerkt blieb, und sie verschwinden mit diesem Paket.

**Was zu tun ist:** Die Ollama-abhängigen Tests per `pytest.mark.skipif` auf einen erreichbaren Endpoint überspringen (Priorität — sie kosten heute jeden vollen lokalen Lauf). Beim Grenzkostenanteil fachlich entscheiden und Test **oder** Config nachziehen. Dann die drei `--deselect`-Zeilen aus der CI entfernen. Danach auf funktionalen Stil vereinheitlichen, `sys.path.append` entfernen, Debug-Skript in ein Werkzeug umwandeln oder löschen.

**Fallstrick (2026-08-26):** `skipif` allein reicht nicht. Die Tests hängen, weil `OllamaClient` mit Backoff wiederholt — eine Erreichbarkeitsprobe ohne kurzen expliziten Timeout hängt in einem gefilterten Netz selbst und verlagert das Problem nur von der Ausführung in die Sammlung. Die Probe braucht einen harten Timeout (etwa eine Sekunde) und muss auf Modulebene zwischengespeichert werden, damit sie nicht pro Test erneut läuft.

**Fertig wenn:** `pytest` läuft ohne lokales Ollama vollständig durch und ist grün, die CI startet ohne `--deselect` — keine "bekannten Fehler" mehr in `CLAUDE.md`. **Doku:** `CLAUDE.md` (Dev-Workflow), `README.md`, `.github/workflows/tests.yml`.

### P4.3 — Doku-Zahlen mechanisch halten

**Befund (neu am 2026-08-26):** Die Doku-Pflicht steht in `CLAUDE.md`, aber nichts prüft sie — und genau die Zahlen, die Vertrauen schaffen sollen, driften still ab. Zwei Fälle allein bei dieser Gegenprobe: die Testanzahl stand an drei Orten in drei Fassungen (Projektplan 267, `CLAUDE.md` "~330", tatsächlich 506), und der CI-Kommentar behauptete Wochen nach der Korrektur weiterhin einen "real pre-existing bug". Beides sind Aussagen, die ein Fachprüfer in einer Minute widerlegt.

**Fundstelle:** `CLAUDE.md` (Abschnitte Architektur-Map und Dev-Workflow), `docs/projektplan.md` (Phase 4), `.github/workflows/tests.yml`.

**Was zu tun ist:** Einen kleinen Test ergänzen, der die in der Doku genannten überprüfbaren Zahlen gegen die Realität hält — Testanzahl, Anzahl der CIB-Zellen, Anzahl der Editor-Tabs. Wo eine Zahl nicht stabil zu halten ist, gehört sie nicht in die Doku, sondern durch eine Größenordnung ersetzt.

**Fertig wenn:** Eine veraltete Zahl in `CLAUDE.md` lässt die Suite rot werden.

**Doku zieht mit:** `CLAUDE.md` (Doku-Pflicht um "prüfbare Zahlen gehören in einen Test" ergänzen).

---

## Phase 5 — Altlasten entfernen

Erst nach Phase 1, damit beim UI-Umbau nichts wegfällt, das noch als Referenz dient.

### P5.1 — Toter Code und irreführende Namen

**Befund:** Mehrere Konstrukte, die Funktionalität vortäuschen: `initial_ticket_price` und `active_market_rule` (keine Referenz), `run_population_sampling` ("backward-compatible entry point", nirgends aufgerufen), `speech_plan.aborted` (Feld existiert nicht), der leere `pass`-Zweig in `_format_factors` mit hartcodiertem Agenten-String, der `state._population_updates`-Pfad — ein komplettes Population-Shift-Feature mit Modellen und Unit-Tests, das der Laufzeitpfad nie erzeugt — und (neu am 2026-08-26) der Parameter `current_tick` in `run_population_tick`, der entgegengenommen und im ganzen Funktionskörper nie benutzt wird. Letzterer ist der einzige der Liste, der **nicht** entfernt werden sollte: P2.1 braucht genau ihn, um pro Tick einen eigenen Zufallsstrom abzuleiten. Dazu die irreführende Paarung `compute_ticket_price` / `compose_ticket_price`: die erste berechnet **nicht** den Kundenpreis.
**Fundstelle:** [`src/market/market_feedback.py`](../src/market/market_feedback.py) (bis P0.4 `market_rules.py`), [`src/population/population_sampler.py:558`](../src/population/population_sampler.py), [`src/agents/scheduler_node.py:123`](../src/agents/scheduler_node.py), [`src/agents/agent_node.py:258-260`](../src/agents/agent_node.py), [`src/orchestration/environment_node.py:282-283`](../src/orchestration/environment_node.py), [`src/market/simulation_functions.py`](../src/market/simulation_functions.py).
**Was zu tun ist:** Pro Konstrukt entscheiden — entfernen oder anschließen. Beim Population-Shift-Feature ist die Frage produktinhaltlich (gehört es zu P1.3?), nicht technisch. Die zwei Preisfunktionen so benennen, dass die Rolle aus dem Namen hervorgeht.
**Fertig wenn:** Kein Modul mehr, das nur von seiner eigenen Definition oder einem Test am Leben gehalten wird. **Doku:** `CLAUDE.md` (Architektur-Map), `docs/handbuch/preisbildung.md`.

### P5.2 — Legacy-Streamlit abnehmen und entfernen

**Befund:** `dashboard/legacy_streamlit/` hält zwei Doppelpaare am Leben (`app.py`/`app_researcher.py`, `config_ui.py`/`config_ui_researcher.py`), die inhaltlich auseinanderlaufen — u. a. eine nur dort gepflegte längere `_render_animation` und verlorene Guillemets in der Researcher-Variante. Drei Audit-Findings betreffen ausschließlich diesen Ordner und lösen sich mit ihm auf.
**Fundstelle:** [`dashboard/legacy_streamlit/`](../dashboard/legacy_streamlit/).
**Was zu tun ist:** Nach Abschluss von Phase 1 prüfen, ob die Dash-App alles abdeckt, was der Researcher-Modus konnte — insbesondere die zusätzlichen Plotly-Charts der Legacy-Animation. Dann das Paket löschen, samt Streamlit-Abhängigkeit und `.streamlit/`.

**Tor benannt (2026-08-26):** "Nach Abschluss von Phase 1" war bisher nicht entscheidbar, weil Phase 1 nur qualitative Kriterien hatte — und solange niemand sagen kann, wann das Tor aufgeht, bleibt `streamlit>=1.32` in `pyproject.toml`, in `requirements.txt` und in jeder CI-Installation. Konkret aufzuschreiben ist deshalb **vor** dem Löschen: welche Charts aus `_render_animation` der Researcher-Variante in der Dash-App vorhanden sein müssen. Diese Liste ist das Abnahmekriterium; ist sie abgehakt, fällt das Paket, unabhängig davon, ob P1.1 und P1.2 im Übrigen schon final sind.
**Fertig wenn:** Kein Streamlit mehr im Repo und in den Abhängigkeiten. **Doku:** `CLAUDE.md`, `README.md`, `dashboard/README.md`.

### P5.3 — `src/legacy/` entscheiden

**Befund:** `cib_extractor_node.py` wird ausschließlich von `tests/test_cib_matrix.py` referenziert; kein Produktionspfad importiert `src/legacy/*`.
**Fundstelle:** [`src/legacy/cib_extractor_node.py`](../src/legacy/cib_extractor_node.py).
**Was zu tun ist:** Bewusst entscheiden — für Experimente behalten (dann dokumentieren, wofür) oder mitsamt Test entfernen. Berührt P2.2: falls die Extraktionslogik beim Impact-Balance-Umbau nützlich ist, vorher ansehen.
**Fertig wenn:** Entscheidung getroffen und im Code sichtbar. **Doku:** `CLAUDE.md` (Architektur-Map, `src/legacy/`-Zeile).

---

## Phase 6 — B2B (noch nicht Scope)

Wird erst geplant, wenn Phase 1 steht: API-Layer, Mandantentrennung, Persistenz, Auth, Billing, produktionsscharfes Hetzner-Deployment. Der heutige `Dockerfile`/`docker-compose.yml` ist ein Ausgangspunkt, kein Deployment.

**"Phase 1 steht" heißt (festgelegt am 2026-08-26):** ~~P1.1 erfüllt sein Drei-Entscheidungen-Kriterium~~ ✅ (seit 2026-08-28, mechanisch geprüft), P1.2 beantwortet drei bis fünf benannte Fragen ohne stillen Teilstand, P1.3 trennt gerechnete von erzählten Zahlen im Datenschema, und P1.4 lädt keine externen Hosts mehr. Dasselbe Tor gilt für P5.2. Ohne diese vier Haken bleibt Phase 6 ungeplant — und Streamlit im Repo.

Eine Randnotiz fürs Marketing, kein Arbeitspaket: Der 10.000-Tick-Benchmark lief mit `dummy_llm` ([`scenario_sweeps.py:200`](../src/orchestration/scenario_sweeps.py)). Die Zahl stimmt, misst aber die deterministische Hälfte — nicht als "unsere KI simuliert 10k Ticks" verwenden.

---

## Abdeckung des Audits

Jeder Abschnitt aus [`audit_findings.md`](audit_findings.md) ist einem Paket zugeordnet. Kein Finding bleibt ungeplant.

| Audit-Abschnitt | Pakete |
| --- | --- |
| Faktoren / Modellsubstanz | ~~P0.2 (F7-Drift)~~ ✅, P2.1, P2.2, P2.3 (die übrigen 120 Zellen), P2.4 |
| Markt / Preisbildung | ~~P0.4 (Rule-Evaluatoren, `market_rules`)~~ ✅, ~~P0.5 (Berechtigungen)~~ ✅, ~~P0.7 (Kostendruck an zwei Stellen)~~ ✅, P3.1 (Property-Baseline), P5.1 (toter Code, Preisfunktions-Namen) |
| Agenten / Scheduling | ~~P0.1 (Silent-Fallback)~~ ✅, P1.3 (Szenario-Schlüssel), P3.5 (Klemmung, `print`), P5.1 (`aborted`, `_format_factors`, `_population_updates`) |
| Validierung / Checkpointing / Orchestrierung | ~~P0.3 (`validate_config`, `factor_ids`)~~ ✅, ~~P0.6 (Sweep-Pfad an P0.1 vorbei)~~ ✅, P2.1 (`_seed_runtime`), P3.2 (Checkpoint-Version), P3.3 (leerer `try`, CLI-Traceback) |
| LLM-Anbindung | ~~P0.1 (zwei Clients)~~ ✅, P3.4 (hartcodierte Defaults, stille Mock-Auswahl in `get_llm()`) |
| Dashboard | P1.2 (Teilstand über den Glob-Fallback, Phantom-Runs in der Auswahl), P3.6 (private Imports), P5.2 (Legacy-Duplikate — erledigen sich mit dem Löschen) |
| LangGraph Studio | P3.3 |
| Tests | P4.1, P4.2 (inkl. der hängenden Sweep-Tests, der veralteten Erwartung in `test_market_rules_resolve_marginal_cost_fraction` und der drei `--deselect`-Zeilen in der CI) |
| Sonstiges | P5.3 |
| **Landingpage** (neu 2026-08-26) | P1.4 (Formular-Endpunkt, Rechtstexte, CDN-Abhängigkeiten) |
| **Reproduzierbarkeit / Run-Artefakte** (neu 2026-08-26) | ~~P0.6 (Seed, Rechenmodus, Config-Hash in `run_metadata.json`)~~ ✅ |
| **Reporting / Grounding** (neu 2026-08-26) | P2.5 (State Explorer prüft seine eigenen Zahlen nicht) |
| **Doku-Konsistenz** (neu 2026-08-26) | P4.3 (Zahlen in `CLAUDE.md` und diesem Plan mechanisch halten) |
| **Einrichten-Assistent** (neu 2026-08-28) | P1.9 (Sweep-Pfad verwirft den Entwurf, Schreibzugriff auf `configs/` aus optionalen Schritten, Schritthöhe, Fortschritts- und Validierungslücken, Barrierefreiheit) |

Die vier neuen Zeilen stammen nicht aus `audit_findings.md`, sondern aus der Gegenprobe vom
2026-08-26 — sie sind dort nachgetragen, damit die Detailliste vollständig bleibt.
