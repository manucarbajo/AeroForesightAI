---
description: Gerüst für einen neuen LangGraph-Node in src/nodes/ anlegen
---

Lege einen neuen LangGraph-Node namens `$ARGUMENTS` unter `src/nodes/` an, nach dem Muster bestehender Nodes (z. B. `src/nodes/market_node.py`, `src/nodes/environment_node.py`):

1. Datei `src/nodes/<name>_node.py` mit einer Klasse `<Name>Node`, die eine `invoke(self, state: SimulationState) -> SimulationState`-Methode implementiert. `from __future__ import annotations` an den Anfang, Imports aus `src.models.*` für alle Datenstrukturen (keine rohen Dicts — siehe CLAUDE.md, Invariante 4).
2. Registriere den Node an der passenden Stelle im Graphen — prüfe `src/langgraph_workflow.py`, wie bestehende Nodes eingebunden werden, und frage nach, an welcher Position im Tick-Ablauf der neue Node einzuhängen ist, falls das nicht eindeutig ist.
3. Lege eine Testdatei `tests/test_<name>_node.py` an, orientiert an `tests/test_agent_node.py` oder `tests/test_environment_node.py`.
4. Formatiere mit `black .` und prüfe mit `ruff check .`, dann `pytest` gegen die volle Suite laufen lassen.

Halte dich strikt an die Architektur-Invarianten aus `CLAUDE.md`: Zahlen/Kennzahlen kommen aus Python, niemals vom LLM; Agenten-Grenzen nur über Pydantic-Modelle.
