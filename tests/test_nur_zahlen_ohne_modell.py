"""«Nur Zahlen» fragt das Sprachmodell nicht (Befund vom 2026-10-01).

Der Abschlusstext beachtete den Rechenmodus (`prefer_llm=not deterministic_only`),
der Szenario-Knoten in `save_run_outputs` nicht: Er fragte das Modell auch in
einem reinen Zahlenlauf. Ohne Ollama stand der Lauf danach als beeinträchtigt da,
mit Ollama ein Modelltext unter `compute_mode: deterministic_only`. Gefunden beim
Drehbuch der Vorführung, am Pitch-Fall des Vorführbestands gemessen.
"""

from __future__ import annotations

import json
from pathlib import Path

from dashboard import run_launcher
from dashboard.run_launcher import RunLaunchConfig, launch_simulation
from src.cib.scenario_agent_node import ScenarioAgentNode


class _Mitschreiber:
    """Steht an der Stelle des Ollama-Clients und merkt sich jede Frage."""

    aufrufe: list[str] = []

    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def call(self, prompt: str) -> str:
        _Mitschreiber.aufrufe.append(prompt)
        raise ConnectionError("Ollama läuft nicht")


def test_ein_zahlenlauf_fragt_kein_modell_und_ist_nicht_beeintraechtigt(monkeypatch):
    _Mitschreiber.aufrufe = []
    monkeypatch.setattr(run_launcher, "OllamaClient", _Mitschreiber)

    ergebnis = launch_simulation(
        # «Nur Zahlen» im Dashboard: kein Platzhalter-Modell, aber deterministisch.
        RunLaunchConfig(rounds=2, mock_llm=False, deterministic_only=True, generate_figures=False)
    )
    metadaten = json.loads(
        (Path(ergebnis.run_dir) / "run_metadata.json").read_text(encoding="utf-8")
    )

    assert _Mitschreiber.aufrufe == [], f"{len(_Mitschreiber.aufrufe)} Aufrufe ans Modell"
    assert metadaten["compute_mode"] == "deterministic_only"
    assert metadaten.get("degraded") is False


def test_der_knoten_rechnet_ohne_zu_erzaehlen():
    """Die gerechneten Szenarien bleiben — nur der Text des Modells entfällt."""

    from dashboard.config_catalog import default_config_draft, prepare_simulation_state

    zustand = prepare_simulation_state(default_config_draft())
    assert zustand.cib_matrix is not None, "Ohne Matrix misst der Test ins Leere"
    _Mitschreiber.aufrufe = []

    ScenarioAgentNode(llm=_Mitschreiber(), erzaehlen=False).invoke(zustand)

    assert _Mitschreiber.aufrufe == []
    assert "gerechnete_szenarien" in zustand.cib_matrix.metadata
    assert zustand.llm_incidents == []
