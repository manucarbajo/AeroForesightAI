"""Der Reiter der Ergebnisse folgt einem Klick — nicht einem neu gezeichneten Knopf (P8-V6).

Im Abnahme-Durchgang am 2026-09-30 führte «Dateien des Laufs» in der Kopfzeile
zur Ansicht «Szenario» statt zu «Dateien»: Der Callback tauscht die Reiterleiste
aus, Dash meldet die eingefügten Knöpfe als Auslöser, und der Reiter-Callback
nahm den ersten davon — ohne dass jemand geklickt hätte.
"""

from __future__ import annotations

from dashboard.web.pages.runs import DEFAULT_TAB, reiter_nach_klick

DATEIEN = {"type": "runs-viewbar", "tab": "files"}
SZENARIO = {"type": "runs-viewbar", "tab": DEFAULT_TAB}


def test_ein_klick_wechselt_den_reiter():
    assert reiter_nach_klick(DATEIEN, 1, DEFAULT_TAB) == "files"


def test_ein_neu_eingefuegter_knopf_ist_kein_klick():
    """Der Befund: `n_clicks` ist `None`, der Auslöser trotzdem gesetzt."""

    assert reiter_nach_klick(SZENARIO, None, "files") is None
    assert reiter_nach_klick(SZENARIO, 0, "files") is None


def test_der_aktive_reiter_wird_nicht_neu_gesetzt():
    assert reiter_nach_klick(DATEIEN, 3, "files") is None


def test_ohne_ausloeser_passiert_nichts():
    assert reiter_nach_klick(None, 1, "files") is None
