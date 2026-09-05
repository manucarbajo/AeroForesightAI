"""ConfigDraft ⇄ dict — der Ersatz für Streamlits ``st.session_state``.

Streamlit hielt den Entwurf als lebendes Dataclass-Objekt im Serverprozess.
Dash hält ihn stattdessen als JSON in einem ``dcc.Store`` im Browser: pro
Benutzer ein eigener Zustand, kein Server-Gedächtnis, und die App übersteht
einen Reload. Dafür muss der Draft verlustfrei durch JSON und zurück —
genau das kapselt dieses Modul.

Wichtig: `ConfigDraft` bleibt die einzige Wahrheit. Hier wird nichts
umgerechnet und nichts ergänzt, nur (de-)serialisiert.
"""

from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from typing import Any

from dashboard.config_catalog import (
    ConfigDraft,
    MarketFeedbackEditState,
    PopulationEditState,
    PropertyEditState,
    SaturationEditState,
    default_config_draft,
)

STORE_ID = "config-draft-store"


def draft_to_dict(draft: ConfigDraft) -> dict[str, Any]:
    """Draft in eine JSON-fähige Struktur überführen."""

    return asdict(draft)


def _build(cls: type, payload: Any) -> Any:
    """Dataclass aus einem Dict rekonstruieren, unbekannte Schlüssel ignorierend.

    Unbekannte Schlüssel entstehen, wenn ein Browser-Tab noch einen Draft aus
    einer älteren Programmversion im Store hält. Die stillschweigend fallen zu
    lassen ist freundlicher als ein TypeError mitten im Callback.
    """

    if not isinstance(payload, dict):
        return cls()
    known = {f.name for f in fields(cls)}
    return cls(**{k: v for k, v in payload.items() if k in known})


def draft_from_dict(payload: dict[str, Any] | None) -> ConfigDraft:
    """Draft aus dem Store zurückbauen; ohne Nutzlast den Standard-Draft."""

    if not payload:
        return default_config_draft()

    draft = default_config_draft()
    nested = {"property_edits", "population_edits", "saturation_edit", "market_feedback_edit"}
    known = {f.name for f in fields(ConfigDraft)}

    for key, value in payload.items():
        if key in known and key not in nested:
            setattr(draft, key, value)

    draft.property_edits = {
        str(pid): _build(PropertyEditState, item)
        for pid, item in (payload.get("property_edits") or {}).items()
    }
    draft.population_edits = [
        _build(PopulationEditState, item) for item in (payload.get("population_edits") or [])
    ]
    draft.saturation_edit = _build(SaturationEditState, payload.get("saturation_edit"))
    draft.market_feedback_edit = _build(
        MarketFeedbackEditState, payload.get("market_feedback_edit")
    )
    return draft


def initial_draft_dict() -> dict[str, Any]:
    """Startzustand des Stores — entspricht dem Streamlit-`init_config_draft`."""

    return draft_to_dict(default_config_draft())


def patch(payload: dict[str, Any] | None, **updates: Any) -> dict[str, Any]:
    """Flache Felder im Store-Dict ändern, ohne den Draft zu rekonstruieren.

    Der übliche Fall: ein Eingabefeld hat sich geändert. Ein Round-Trip durch
    `ConfigDraft` wäre dafür unnötig teuer.
    """

    data = dict(payload or initial_draft_dict())
    for key, value in updates.items():
        if is_dataclass(value):
            value = asdict(value)
        data[key] = value
    return data
