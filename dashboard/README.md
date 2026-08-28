# Simulations-Leitstand

Web-Oberfläche für Präsentation und Analyse: Simulation starten, Ergebnisse
ansehen, Lauf per Chat abfragen. Gebaut mit **Plotly Dash**.

Seit P1.5 ist es ein **Leitstand**: ein Bildschirm, fünf Zonen, kein Blättern.

```text
+---------------------------------------------------------------+
| Kopfzeile - Name, Zustand, Lauf-Auswahl, Aktionen, Theme       |
+---------------+---------------------------+-------------------+
| Bedienfeld    | Viewport                  | Telemetrie        |
| (Stand,       | (Szene, Einrichten,       | (Kennzahlen,      |
|  Preflight,   |  Ergebnisse, Handbuch)    |  Verlaeufe,       |
|  Start)       +---------------------------+  Konsole)         |
|               | Zeitleiste                |                   |
+---------------+---------------------------+-------------------+
```

Kopfzeile und Zeitleiste bleiben stehen, die drei Zonen dazwischen rollen jede
für sich. Unter 1280 px weicht die Telemetrie in eine Schublade, unter 1024 px
auch die Parameterspalte, unter 768 px scrollt die Seite wieder normal.

## Start

```powershell
python -m dashboard.web.app --port 8511
```

| Adresse | Inhalt |
| --- | --- |
| `http://localhost:8511/` | Landingpage |
| `http://localhost:8511/app/` | Leitstand (Szene + Zeitleiste) |
| `http://localhost:8511/app/setup` | Einrichten (drei Entscheidungen + Editor) |
| `http://localhost:8511/app/runs` | Ergebnisse (die sieben Ansichten) |
| `http://localhost:8511/app/doku` | Handbuch |

Ein Server für beides. Die Landingpage (`aeroforesight-ai-landing-page/`) wird
als statisches HTML ausgeliefert, das Dashboard läuft darunter auf `/app/`.
Alle Verweise zwischen beiden sind relativ — es gibt keine fest verdrahtete
Adresse mehr, die fürs Deployment angefasst werden müsste.

## Aufbau

```
dashboard/
├── config_catalog.py       # ConfigDraft, Presets, Property-/Population-Persistenz
├── run_browser.py          # Runs, Dateien, Figures, Zeitreihen lesen
├── run_launcher.py         # Lauf ausführen (inkl. Fortschritts-Callback)
├── consistency_report.py   # Artefakt-Checks gegen die Ground Truth
├── web/                    # Plotly-Dash-Oberfläche  ← aktiv
└── legacy_streamlit/       # abgelöste Streamlit-UI  ← nur noch zum Vergleich
```

Die vier Module oben sind **oberflächenfrei** — sie enthalten keine Zeile
Dash und keine Zeile Streamlit. Beide Oberflächen setzen darauf auf, und
`tests/test_dashboard_service.py` testet sie unabhängig von der UI.

### `web/`

| Datei / Ordner | Rolle |
| --- | --- |
| `app.py` | Dash-Instanz, Stores, Routing, die Callbacks zwischen den Zonen |
| `shell.py` | der Rahmen: fünf Zonen, Kopfzeile, Theme-Umschalter, Schubladen |
| `theme.py` | Farbtokens (hell **und** dunkel) + die beiden Plotly-Templates |
| `status.py` | **eine** Ableitung des Anlagenzustands für Kopfzeile, Banner, Konsole |
| `run_data.py` | die Daten eines Laufs aus einer Hand — oder der Beispieldatensatz |
| `demo_run.py` | der Beispieldatensatz, wenn `outputs/` noch leer ist |
| `timeline.py` | die einzige Zeitachse: Tick-Regler, Abspielsteuerung, Ereignismarker |
| `components.py` | Karten, Kacheln, Buttons, Tabs, Akkordeons, Konsolenzeilen |
| `state.py` | `ConfigDraft` ⇄ `dcc.Store` |
| `runner.py` | Lauf im Hintergrund-Thread, Fortschritt über eine Queue |
| `files_route.py` | Flask-Route für PNGs und Downloads aus `outputs/` |
| `pages/` | `launch.py` (Bedienfeld links: Stand, Preflight, Start), `setup.py` (Einrichten), `runs.py` (Ergebnis-Ansichten), `docs.py` (Handbuch) |
| `pages/docs_reference.py` | Referenzkapitel, aus Glossar und `configs/` erzeugt |
| `views/` | die sieben Ergebnis-Ansichten plus `scene.py` (Viewport) und `telemetry.py` (rechte Zone) |
| `config_editor/` | der geführte Ablauf (`start_flow.py`) plus die vier Editor-Tabs |
| `config_editor/glossary.py` | **alle Erklärtexte an einer Stelle** — Beschriftung, Wirkung, technischer Feldname je Parameter |
| `assets/dashboard.css` | Styling für alles, was Tailwind-Utilities nicht erreichen |

## Funktionen

| Zone / Bereich | Inhalt |
| --- | --- |
| **Kopfzeile** | Zustand der Anlage (bereit / läuft / beeinträchtigt / Demo, mit pulsierendem Punkt), Lauf-Auswahl für den ganzen Leitstand, Speichern / Snapshot / Exportieren, Theme-Umschalter |
| **Bedienfeld** | Was eingestellt ist (Szenario, Länge, Rechenmodus — je ein Verweis ins Einrichten), der Preflight, der Start-Knopf in einem klebenden Fuß. **Keine Eingabefelder** — `tests/test_web_rail.py` hält das fest |
| **Einrichten** | Der geführte Ablauf aus P1.1 — drei Entscheidungen, Presets als Kartenraster —, darunter vier Editor-Bereiche: **Rahmenbedingungen** (Faktoren F1–F7, Systemgrößen samt Regeln), **Nachfrage & Preisbildung** (Yield Management, Sättigung, Segmente, Verteilungen), **Lauf & Ablage** (Benennung, Mehrfachläufe, Config-Dateien, Preset sichern), **Technik** (Sprachmodell, Ausgaben) |
| **Viewport** | **Leitstand**: die Population zum gewählten Tick plus Faktorstreifen F1–F7 · **Einrichten** (siehe oben) · **Ergebnisse**: Szenario (Hauptansicht), Übersicht, Animation, Figures, Bericht, Abfrage, Dateien · **Handbuch** mit Kapitelnavigation und Volltextsuche |
| **Zeitleiste** | Tick-Regler über den Lauf, Play/Pause/Stop/Schritt, Tempo, Ereignismarker |
| **Telemetrie** | Kennzahlen des gewählten Ticks, dieselben Größen als Verlauf mit Positionsmarke, Konsole (Ereignisse, Modellausfälle, Lauffortschritt) |

### Aufbau des Config-Editors

Die Oberfläche richtet sich an **Anwender**, nicht an Modellbauer. Daraus
folgen drei Regeln, die für jeden neuen Parameter gelten:

1. **Beschriftung in der Sprache der Sache**, nicht des Codes. Aus
   «Logit-Penalty-Faktor» wird «Wirkung der Sättigung auf die Buchungsneigung».
2. **Jedes Feld erklärt seine Wirkung** — was sich am Ergebnis ändert und in
   welche Richtung. Die Texte stehen in `web/config_editor/glossary.py`, nicht
   verstreut in den Tab-Modulen.
3. **Pro Block steht vorn, was die Wirkung bestimmt.** Alles Übrige liegt in
   einem «Feinabstimmung»-Block darunter. Sichtbar sind dadurch beim Einstieg
   sechs Felder statt rund 160 — verborgen ist keines.

Im Editor steht je Feld nur eine Zeile. Die ausführliche Erklärung samt Einheit
und Config-Feldname steht im Handbuch; jeder Abschnitt des Editors verlinkt in
das passende Kapitel.

## Handbuch

Die Seite **Dokumentation** (`/doku`) ist als Nachschlagewerk aufgebaut:
Kapitelnavigation links, Text rechts, Volltextsuche, jede Zwischenüberschrift
verlinkbar über `/doku/<kapitel>`.

Kapitel kommen aus zwei Quellen. Erklärende Texte liegen als Markdown unter
[`../docs/handbuch/`](../docs/handbuch/) und lassen sich ohne Python ändern.
Referenzkapitel — alle Einstellungen, Faktoren, Systemgrößen, Presets, Rechte
der Akteure — erzeugt `web/pages/docs_reference.py` aus dem Glossar und den
Dateien unter `configs/`; sie können dadurch nicht veralten.

`tests/test_web_docs.py` hält die Vollständigkeit fest: Eine neue Einstellung,
Systemgröße oder ein neues Preset ohne Eintrag im Handbuch lässt die Suite
fehlschlagen.

**Demo-Ablauf:** Run wählen → **Szenario** lesen → **Figures** → **Abfrage**
(Chat). Details: [`../docs/scenario_runs.md`](../docs/scenario_runs.md)

Run-Figures liegen unter `outputs/<run_id>/figures/` (6 PNGs + `manifest.json`),
sofern «Figures nach Lauf erzeugen» aktiv ist (Standard). Sie erscheinen in der
Ansicht **Figures** unter **PNG-Export**; im Dark Mode stehen sie auf einer
weißen Fläche wie ein aufgelegtes Blatt — matplotlib rendert sie hell, und
ehrlich dargestellt schlägt falsch eingefärbt (offen in P1.2). die sechs Live-Auswertungen daneben entstehen
direkt aus `outputs/<run_id>/timeseries/`. Sweep-Runs: `outputs/sweeps/sweep_<preset>/`.

## Gestaltung

**Farbe läuft über eine Token-Ebene, nirgends sonst.** Tailwind liefert Layout,
Abstand und Typografie; die Farbe kommt als semantische Rolle (`surface`,
`border`, `text-muted`, `accent`, …) aus `web/theme.py` — für alles, was Python
einfärbt — und unter denselben Namen als CSS-Variable aus
`web/assets/dashboard.css` für alles Übrige. Jede Rolle existiert **zweimal**,
hell und dunkel; `tests/test_web_theme.py` hält beide Seiten deckungsgleich und
meldet jede Tailwind-Farbklasse und jeden rohen Farbwert, der sich in ein Modul
unter `web/` verirrt. Eine einzige übersehene reicht, um im Dark Mode eine weiße
Fläche aufblitzen zu lassen.

Die **helle** Palette stammt aus
[`../aeroforesight-ai-landing-page/design/color-tokens.json`](../aeroforesight-ai-landing-page/design/color-tokens.json)
und ist mit der Landingpage abgeglichen — wird dort umgefärbt, ändert sich hier
eine Konstante. Die dunkle (`theme.INK`) hat dort keine Entsprechung, weil die
Landingpage nicht umschaltbar ist.

**Dashs eigene Komponenten** (Slider, Dropdown, Tabs) werden über ihre
`--Dash-*`-Token-Ebene mitgefärbt, nicht über einzelne Selektoren: Deren
Klassennamen haben sich zwischen Dash 2 (`rc-slider-*`, `Select-*`) und Dash 4
(`dash-slider-*`, `dash-dropdown-*`) vollständig geändert, und der alte Satz
Regeln griff dadurch an keiner einzigen Stelle mehr.

Die Wahl zwischen hell und dunkel liegt im `localStorage` des Browsers und wird
von einem kurzen Skript im `<head>` gesetzt, **bevor** die Seite zum ersten Mal
zeichnet — ein Dash-Callback käme dafür zu spät, und das helle Design blitzte
bei jedem Laden kurz auf.

Tailwind und die Schriften kommen wie auf der Landingpage über CDN. Für das
Deployment auf den eigenen Server müssen beide lokal ausgeliefert werden;
siehe [`../aeroforesight-ai-landing-page/DEPLOY.md`](../aeroforesight-ai-landing-page/DEPLOY.md).

## Legacy

`legacy_streamlit/` ist die abgelöste Streamlit-Oberfläche. Sie bleibt bis auf
Weiteres lauffähig, damit sich alt und neu direkt vergleichen lassen — siehe
[`legacy_streamlit/README.md`](legacy_streamlit/README.md). Neue Funktionen
gehören ausschließlich nach `web/`.

Projekt-README: [`../README.md`](../README.md)
