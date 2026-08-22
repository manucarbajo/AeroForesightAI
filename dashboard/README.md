# Simulations-Dashboard

Web-Oberfläche für Präsentation und Analyse: Simulation starten, Ergebnisse
ansehen, Run per Chat abfragen. Gebaut mit **Plotly Dash**, im Design der
Landingpage (`aeroforesight-ai-landing-page/`).

## Start

```powershell
python -m dashboard.web.app --port 8511
```

Browser: `http://localhost:8511` — dieselbe Adresse, auf die der Login-Button
der Landingpage zeigt.

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
| `app.py` | Dash-Instanz, Seitenrahmen, Routing, Stores |
| `theme.py` | Design-Tokens der Landingpage + Plotly-Template |
| `components.py` | Karten, Kacheln, Buttons, Tabs, Akkordeons |
| `state.py` | `ConfigDraft` ⇄ `dcc.Store` |
| `runner.py` | Lauf im Hintergrund-Thread, Fortschritt über eine Queue |
| `files_route.py` | Flask-Route für PNGs und Downloads aus `outputs/` |
| `pages/` | `launch.py` (Simulation starten), `runs.py` (Ergebnisse ansehen) |
| `views/` | die sieben Tabs des Run-Browsers |
| `config_editor/` | die fünf Tabs des Config-Editors |
| `assets/dashboard.css` | Styling für alles, was Tailwind-Utilities nicht erreichen |

## Funktionen

| Bereich | Inhalt |
| --- | --- |
| **Simulation starten** | Szenario-Modus (Standard/Preset/eigene Parameter), Ticks, Multi-Run, Config-Dateien, Faktoren F1–F7, System-Properties samt Regeln, Population und Verteilungen, Markt-Feedback, Sättigung, LLM- und Pipeline-Schalter, Preset speichern, Start mit Live-Log |
| **Ergebnisse ansehen** | **Szenario** (Hauptansicht), Übersicht, Animation, Figures, Bericht, Abfrage, Dateien |

**Demo-Ablauf:** Run wählen → **Szenario** lesen → **Figures** → **Abfrage**
(Chat). Details: [`../docs/scenario_runs.md`](../docs/scenario_runs.md)

Run-Figures liegen unter `outputs/<run_id>/figures/` (6 PNGs + `manifest.json`),
sofern «Figures nach Lauf erzeugen» aktiv ist (Standard). Sie erscheinen im Tab
**Figures** unter **PNG-Export**; die sechs Live-Auswertungen daneben entstehen
direkt aus `outputs/<run_id>/timeseries/`. Sweep-Runs: `outputs/sweeps/sweep_<preset>/`.

## Gestaltung

Farben, Schriften und Radien stammen aus
[`../aeroforesight-ai-landing-page/design/color-tokens.json`](../aeroforesight-ai-landing-page/design/color-tokens.json)
und stehen an genau einer Stelle im Code: `web/theme.py` (für Diagramme) bzw.
die Tailwind-Konfiguration in `web/app.py` (für die Oberfläche). Beide sind
mit der Landingpage abgeglichen — wird dort umgefärbt, ändert sich hier eine
Konstante.

Tailwind und die Schriften kommen wie auf der Landingpage über CDN. Für das
Deployment auf den eigenen Server müssen beide lokal ausgeliefert werden;
siehe [`../aeroforesight-ai-landing-page/DEPLOY.md`](../aeroforesight-ai-landing-page/DEPLOY.md).

## Legacy

`legacy_streamlit/` ist die abgelöste Streamlit-Oberfläche. Sie bleibt bis auf
Weiteres lauffähig, damit sich alt und neu direkt vergleichen lassen — siehe
[`legacy_streamlit/README.md`](legacy_streamlit/README.md). Neue Funktionen
gehören ausschließlich nach `web/`.

Projekt-README: [`../README.md`](../README.md)
