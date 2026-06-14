# Startet das Präsentations-Dashboard aus dem Repo-Root.
Set-Location (Split-Path $PSScriptRoot -Parent)
python -m streamlit run dashboard/app.py
