"""Der Rechenmodus: eine Auswahl, zwei Draft-Felder.

Die Oberfläche zeigt drei sich ausschließende Möglichkeiten, der Draft führt
weiterhin `mock_llm` und `deterministic_only`. Diese Übersetzung muss in beide
Richtungen stimmen — sonst startet ein Lauf in einem anderen Modus als
angezeigt.
"""

from __future__ import annotations

import pytest

from dashboard import llm_status
from dashboard.web.config_editor import compute_mode
from dashboard.web.state import draft_from_dict, initial_draft_dict


@pytest.mark.parametrize(
    ("mode", "mock", "deterministic"),
    [
        (compute_mode.WITH_LLM, False, False),
        (compute_mode.MOCK, True, False),
        (compute_mode.NUMBERS_ONLY, True, True),
    ],
)
def test_mode_maps_onto_the_two_fields(mode, mock, deterministic):
    draft = compute_mode.apply(initial_draft_dict(), mode)

    restored = draft_from_dict(draft)
    assert restored.mock_llm is mock
    assert restored.deterministic_only is deterministic


@pytest.mark.parametrize(
    "mode", [compute_mode.WITH_LLM, compute_mode.MOCK, compute_mode.NUMBERS_ONLY]
)
def test_round_trip_through_the_draft(mode):
    """Was gesetzt wurde, muss die Auswahl danach auch wieder anzeigen."""

    draft = compute_mode.apply(initial_draft_dict(), mode)

    assert compute_mode.of(draft) == mode


def test_the_selection_itself_is_not_stored():
    """`compute_mode` ist ein Bedienelement, kein Feld des Entwurfs."""

    draft = compute_mode.apply(initial_draft_dict(), compute_mode.MOCK)

    assert compute_mode.FIELD not in draft
    assert not hasattr(draft_from_dict(draft), compute_mode.FIELD)


def test_unknown_mode_leaves_the_draft_alone():
    before = initial_draft_dict()

    after = compute_mode.apply(dict(before), "gibt-es-nicht")

    assert after["mock_llm"] == before["mock_llm"]
    assert after["deterministic_only"] == before["deterministic_only"]


def test_every_option_is_reachable():
    values = {option["value"] for option in compute_mode.OPTIONS}

    assert values == {compute_mode.WITH_LLM, compute_mode.MOCK, compute_mode.NUMBERS_ONLY}


# --- Erreichbarkeit --------------------------------------------------------


def test_status_reports_an_unreachable_service():
    llm_status.reset_cache()

    # Port, auf dem nichts lauscht: die Abfrage muss zügig aufgeben.
    status = llm_status.check("http://127.0.0.1:59999")

    assert status.reachable is False
    assert status.detail
    assert status.models == ()


def test_status_needs_an_address():
    assert llm_status.check("").reachable is False


def test_model_matching_ignores_the_tag():
    """Ollama führt `llama3.2:latest`, angegeben wird `llama3.2`."""

    status = llm_status.OllamaStatus(
        base_url="x", reachable=True, models=("llama3.2:latest", "nomic-embed-text:latest")
    )

    assert status.has_model("llama3.2")
    assert status.has_model("llama3.2:latest")
    assert not status.has_model("mistral")
    assert not status.has_model("")


def test_availability_explains_a_missing_service(monkeypatch):
    monkeypatch.setattr(
        llm_status,
        "check",
        lambda url, **kw: llm_status.OllamaStatus(
            base_url=url, reachable=False, detail="Nicht erreichbar."
        ),
    )

    rendered = str(compute_mode.availability(initial_draft_dict()))

    assert "nicht erreichbar" in rendered.lower()


def test_availability_flags_a_missing_model(monkeypatch):
    monkeypatch.setattr(
        llm_status,
        "check",
        lambda url, **kw: llm_status.OllamaStatus(
            base_url=url, reachable=True, models=("mistral:latest",)
        ),
    )
    draft = initial_draft_dict()
    draft["model"] = "llama3.2"

    rendered = str(compute_mode.availability(draft))

    assert "llama3.2" in rendered
    assert "mistral:latest" in rendered


def test_availability_erfindet_kein_modell_fuer_ein_leeres_feld(monkeypatch):
    """P3.13: «kein Modell eingestellt» ist eine andere Aussage als «fehlt dort».

    Vorher stand hier `draft.get("model") or DEFAULT_MODEL`, und die Meldung
    nannte bei leerem Feld «llama3.2 fehlt dort» — ein Modell, das niemand
    eingestellt hat. Dieselbe Erfindung wie im Launcher (B1 des Audits), nur in
    einem Satz statt in einem Feld.
    """

    monkeypatch.setattr(
        llm_status,
        "check",
        lambda url, **kw: llm_status.OllamaStatus(
            base_url=url, reachable=True, models=("mistral:latest",)
        ),
    )
    draft = initial_draft_dict()
    draft["model"] = "   "

    rendered = str(compute_mode.availability(draft))

    assert "kein Modell eingestellt" in rendered
    assert "llama3.2" not in rendered, "Die Meldung nennt ein Modell, das nicht eingestellt ist"
    assert "mistral:latest" in rendered, "Was dort liegt, hilft beim Eintragen"


def test_availability_pingt_keine_erfundene_adresse_an(monkeypatch):
    """P3.13, die schlimmere Hälfte: eine erfundene Adresse beantwortet die falsche Frage.

    `llm_status.check` wurde mit `DEFAULT_BASE_URL` gerufen, wenn das Feld leer
    war — und ihr Ergebnis entschied darüber, ob «Mit Sprachmodell» als möglich
    angezeigt wird. Läuft dort zufällig ein Ollama, sagte die Oberfläche «alle
    drei Modi stehen zur Verfügung» für einen Lauf, der keinen Endpunkt hat.
    """

    gefragt: list[str] = []

    def _merke(url, **kw):
        gefragt.append(url)
        return llm_status.OllamaStatus(base_url=url, reachable=True, models=("mistral:latest",))

    monkeypatch.setattr(llm_status, "check", _merke)
    draft = initial_draft_dict()
    draft["base_url"] = ""

    rendered = str(compute_mode.availability(draft))

    assert gefragt == [], f"Es wurde trotzdem eine Adresse befragt: {gefragt}"
    assert "Keine Adresse" in rendered
