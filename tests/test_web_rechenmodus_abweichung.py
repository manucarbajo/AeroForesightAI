"""Die Abweichungsliste nennt den gewählten Rechenmodus — nicht den Schalter dahinter (P8-V6).

Im Abnahme-Durchgang am 2026-09-30 stand im Prüfschritt nach der Wahl «Mit
Sprachmodell» unter «Was von der Auslieferung abweicht»: «Rechenmodus ‹Ohne
Sprachmodell›». Die Liste nannte das geänderte Feld (`mock_llm`) mit seinem
Namen, und der liest sich als das Gegenteil der Wahl.
"""

from __future__ import annotations

from dashboard.web.config_editor import delta
from dashboard.web.state import initial_draft_dict


def _entwurf(**felder) -> dict:
    return {**initial_draft_dict(), **felder}


def _modus(entwurf: dict) -> list[delta.Abweichung]:
    return [a for a in delta.unterschiede(entwurf) if a.was == "Rechenmodus"]


def test_mit_sprachmodell_heisst_in_der_liste_auch_so():
    (abweichung,) = _modus(_entwurf(mock_llm=False, deterministic_only=False))

    assert (abweichung.vorher, abweichung.jetzt) == ("Ohne Sprachmodell", "Mit Sprachmodell")


def test_nur_zahlen_ist_eine_abweichung_nicht_zwei():
    """Beide Schalter können abweichen — es bleibt eine Wahl."""

    (abweichung,) = _modus(_entwurf(mock_llm=False, deterministic_only=True))

    assert abweichung.jetzt == "Nur Zahlen"
    assert not any(
        a.feld in delta.RECHENMODUS_FELDER for a in delta.unterschiede(_entwurf(mock_llm=False))
    )


def test_der_ausgelieferte_modus_ist_keine_abweichung():
    assert _modus(initial_draft_dict()) == []


def test_zuruecknehmen_stellt_beide_schalter_zurueck():
    standard = initial_draft_dict()
    entwurf = delta.zuruecknehmen(
        _entwurf(mock_llm=False, deterministic_only=True), delta.RECHENMODUS
    )

    assert all(entwurf[feld] == standard[feld] for feld in delta.RECHENMODUS_FELDER)
    assert _modus(entwurf) == []
