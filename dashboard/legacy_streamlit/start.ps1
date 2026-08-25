# Startet das Präsentations-Dashboard aus dem Repo-Root.
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
python -m streamlit run dashboard/legacy_streamlit/app.py
