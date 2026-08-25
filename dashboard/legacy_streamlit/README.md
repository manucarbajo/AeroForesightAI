# Legacy: Streamlit-Dashboard

Diese Oberfläche ist **abgelöst**. Aktiv ist die Plotly-Dash-App unter
[`../web/`](../web/) — siehe [`../README.md`](../README.md).

Das Paket bleibt vorerst lauffähig, damit sich altes und neues Dashboard während
der Migration direkt vergleichen lassen. Nach der Abnahme wird es zusammen mit
der `streamlit`-Abhängigkeit entfernt. **Bitte hier keine neuen Funktionen mehr
einbauen** — sie müssten sonst doppelt gepflegt werden.

## Start

```powershell
python -m streamlit run dashboard/legacy_streamlit/app.py --server.port=8513
python -m streamlit run dashboard/legacy_streamlit/app_researcher.py --server.port=8512
```

## Aufbau

| Datei | Rolle |
| --- | --- |
| `app.py` | Ops-Variante: PNG-Figures, 7-Tab-Config-Editor |
| `app_researcher.py` | Forschungs-Variante: Live-Plotly-Figures, 5-Tab-Config-Editor |
| `shared_views.py` | Gemeinsame Tabs, Session-State, Seiten-Setup |
| `config_ui.py` / `config_ui_researcher.py` | Die beiden Config-Editor-Layouts |
| `config_fields.py` | Config-Bausteine, die sich beide Editoren teilen |

Der Service-Layer (`dashboard/config_catalog.py`, `run_browser.py`,
`run_launcher.py`, `consistency_report.py`) ist **nicht** Teil dieses Legacy-Pakets
— er ist streamlit-frei und wird von der Dash-App weiterverwendet.
