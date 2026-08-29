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

#: Die Erreichbarkeits-Anzeige. Pattern-Matching-ID, weil sie nur in zwei von
#: sechs Tabs steht — ein Callback auf eine feste, gerade nicht vorhandene ID
#: quittiert Dash im Browser mit einem Fehler.
STATUS = "cfg-llm-status"


def status_id(slot: str) -> dict:
    return {"type": STATUS, "slot": slot}


def placeholder(slot: str) -> html.Div:
    """Steht im Layout, bis der Callback die Auskunft nachreicht."""

    return html.Div(
        ui.status_dot(False, "Ollama wird geprüft …"),
        id=status_id(slot),
    )


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


#: Dieselben drei Moeglichkeiten in zwei Worten. Das Bedienfeld hat fuer den
#: ganzen Satz keinen Platz, und ein abgeschnittener Satz ist schlechter als
#: eine kurze Bezeichnung.
SHORT_LABELS = {
    WITH_LLM: "Mit Sprachmodell",
    MOCK: "Ohne Sprachmodell",
    NUMBERS_ONLY: "Nur Zahlen",
}


def short_label(draft: dict) -> str:
    """Der Rechenmodus in zwei Worten."""

    return SHORT_LABELS.get(of(draft), "—")


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

    Wird aus einem Callback gerufen, nicht beim Aufbau des Tabs: Die Abfrage
    darf mehrere Sekunden dauern, und so lange soll niemand auf die Seite
    warten.
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
