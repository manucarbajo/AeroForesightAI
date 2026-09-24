"""Der Rechenmodus als eine Auswahl statt zweier verneinter Schalter.

Bisher standen dort zwei Kästchen, «Ohne Ollama rechnen» und «Ohne
Agenten-Dialog». Beide verneint, beide unabhängig — obwohl es in Wahrheit drei
sich ausschließende Möglichkeiten sind und eine der vier Kombinationen keinen
Sinn ergibt (ein Ollama-Client wird aufgebaut und dann nie gefragt).

Hier steht die Übersetzung zwischen der einen Auswahl und den beiden Feldern,
die der Draft weiterhin führt.

**Dieses Modul stellt dar, was eingestellt ist — es setzt nichts** (P3.13).
`DEFAULT_BASE_URL` und `DEFAULT_MODEL` wurden hier bis dahin importiert, um ein
leeres Feld zu ersetzen; der Import ist weg und nicht bloß unbenutzt.
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
        ui.status_dot("pruefen", "Ollama wird geprüft …"),
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

    **Ein leeres Feld wird gesagt, nicht ersetzt** (P3.13). Hier stand
    ``draft.get("model") or DEFAULT_MODEL`` und daneben dasselbe für die
    Adresse — bei leerem Feld nannte die Meldung damit «llama3.2 fehlt dort»,
    also ein Modell, das niemand eingestellt hat. Dieselbe Erfindung wie im
    Launcher, nur in einem Satz statt in einem Feld; und die Adresse war der
    schlimmere der beiden Fälle, weil dann eine **erfundene** Adresse
    angepingt wurde und ihr Ergebnis über den Modus entschied.
    """

    base_url = (draft.get("base_url") or "").strip()
    model = (draft.get("model") or "").strip()

    # Ohne Adresse gibt es nichts zu befragen — und eine erfundene zu befragen
    # beantwortet die falsche Frage.
    if not base_url:
        return ui.status_dot(
            "aus",
            "Keine Adresse für Ollama eingestellt",
            hint="Ohne Endpunkt lässt sich nicht prüfen, ob ein Sprachmodell "
            "erreichbar ist. Adresse unter «Technik» eintragen.",
        )

    status = llm_status.check(base_url)

    if not status.reachable:
        return ui.status_dot(
            "aus",
            "Ollama ist nicht erreichbar",
            hint=f"{status.detail} Ohne laufenden Dienst funktionieren nur die beiden "
            f"unteren Modi. Adresse: {base_url}",
        )

    # Der Dienst antwortet — welches Modell rechnen soll, steht aber nirgends.
    # Das ist eine andere Aussage als «das gewählte Modell fehlt», und der
    # Nutzer braucht sie, um zu wissen, wo er nachsieht.
    if not model:
        vorhanden = ", ".join(status.models) or "keine"
        return ui.status_dot(
            "aus",
            "Ollama läuft, aber es ist kein Modell eingestellt",
            hint=f"Vorhanden dort: {vorhanden}. Modellnamen unter «Technik» eintragen.",
        )

    if not status.has_model(model):
        vorhanden = ", ".join(status.models) or "keine"
        return ui.status_dot(
            "aus",
            f"Ollama läuft, aber «{model}» fehlt dort",
            hint=f"Vorhanden: {vorhanden}. Modellnamen unter «Technik» anpassen "
            f"oder das Modell nachladen.",
        )

    return ui.status_dot(
        "bereit",
        f"Ollama läuft, «{model}» ist einsatzbereit",
        hint="Alle drei Modi stehen zur Verfügung.",
    )
