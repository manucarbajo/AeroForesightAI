"""Der Rechenmodus als eine Auswahl statt zweier verneinter Schalter.

Bisher standen dort zwei Kästchen, «Ohne Ollama rechnen» und «Ohne
Agenten-Dialog». Beide verneint, beide unabhängig — obwohl es in Wahrheit drei
sich ausschließende Möglichkeiten sind und eine der vier Kombinationen keinen
Sinn ergibt (ein Ollama-Client wird aufgebaut und dann nie gefragt).

Hier steht die Übersetzung zwischen der einen Auswahl und den beiden Feldern,
die der Draft weiterhin führt.
"""

from __future__ import annotations

from dash import html

from dashboard import llm_status
from dashboard.web import components as ui

#: Die Auswahl ist kein Draft-Feld; `config_editor._normalise` übersetzt sie
#: in `mock_llm` und `deterministic_only`.
FIELD = "compute_mode"
FIELD_ID = {"type": "cfg", "field": FIELD}

WITH_LLM = "llm"
MOCK = "mock"
NUMBERS_ONLY = "numbers"

OPTIONS = [
    {
        "label": "Mit Sprachmodell — Agenten deuten den Lauf in eigenen Worten",
        "value": WITH_LLM,
    },
    {
        "label": "Ohne Sprachmodell — Agenten-Texte sind Platzhalter (schnell)",
        "value": MOCK,
    },
    {
        "label": "Nur Zahlen — kein Agenten-Dialog, kürzeste Laufzeit",
        "value": NUMBERS_ONLY,
    },
]


def of(draft: dict) -> str:
    """Aus den beiden Draft-Feldern den Modus ableiten."""

    if draft.get("deterministic_only"):
        return NUMBERS_ONLY
    return MOCK if draft.get("mock_llm", True) else WITH_LLM


def apply(draft: dict, mode: str | None) -> dict:
    """Modus zurück in die beiden Felder schreiben."""

    if mode == WITH_LLM:
        draft["mock_llm"] = False
        draft["deterministic_only"] = False
    elif mode == NUMBERS_ONLY:
        draft["mock_llm"] = True
        draft["deterministic_only"] = True
    elif mode == MOCK:
        draft["mock_llm"] = True
        draft["deterministic_only"] = False
    draft.pop(FIELD, None)
    return draft


def availability(draft: dict) -> html.Div:
    """Anzeigen, ob «Mit Sprachmodell» überhaupt möglich ist.

    Ohne diese Zeile merkt man erst nach Minuten, dass Ollama nicht läuft —
    der Lauf bricht dann mitten in der Simulation ab.
    """

    base_url = draft.get("base_url") or "http://localhost:11434"
    model = draft.get("model") or "llama3.2"
    status = llm_status.check(base_url)

    if not status.reachable:
        return ui.status_dot(
            False,
            "Ollama ist nicht erreichbar",
            hint=f"{status.detail} Ohne laufenden Dienst funktionieren nur die beiden "
            f"unteren Modi. Adresse: {base_url}",
        )

    if not status.has_model(model):
        vorhanden = ", ".join(status.models) or "keine"
        return ui.status_dot(
            False,
            f"Ollama läuft, aber «{model}» fehlt dort",
            hint=f"Vorhanden: {vorhanden}. Modellnamen unter «Technik» anpassen "
            f"oder das Modell nachladen.",
        )

    return ui.status_dot(
        True,
        f"Ollama läuft, «{model}» ist einsatzbereit",
        hint="Alle drei Modi stehen zur Verfügung.",
    )
