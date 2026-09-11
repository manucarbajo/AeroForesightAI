"""`coerce_payload` übernimmt die Tickzahl aus einem LangGraph-Studio-Payload (2026-09-11).

**Gefunden hat den Fehler kein Test, sondern der Typprüfer** (P4.4): `int(ticks)`,
wobei `ticks` `None` sein konnte. Nachgestellt stürzte `{"max_ticks": 0}` mit
`TypeError` ab, und `{"max_ticks": "abc", "rounds": 5}` mit `ValueError`, obwohl
`rounds` gültig war. Die Bedingung prüfte «ist irgendeiner der drei Werte ein
`int`», die Auswahl nahm aber den ersten *wahrheitswerten*.

Einen Test, der `coerce_payload` aufruft, gab es bis dahin nicht — mittelbar läuft
die Funktion nur über `wrap_node` im LangGraph-Pfad, und dort nie mit diesen Werten.
"""

from __future__ import annotations

import pytest

from src.orchestration.langgraph_adapter import coerce_payload


def _ticks(payload: dict) -> object:
    return coerce_payload(payload)["clock"]["max_ticks"]


class TestDieTickzahlKommtAusDemErstenGanzzahligenWert:
    def test_null_ticks_stuerzen_nicht_ab(self):
        """Ob null Ticks zulässig sind, entscheidet die Validierung — nicht ein Absturz hier."""

        assert _ticks({"max_ticks": 0}) == 0

    def test_ein_ungueltiger_erster_wert_verdeckt_den_gueltigen_nicht(self):
        assert _ticks({"max_ticks": "abc", "rounds": 5}) == 5

    @pytest.mark.parametrize(
        ("payload", "erwartet"),
        [
            ({"max_ticks": 12}, 12),
            ({"max_rounds": 9}, 9),
            ({"rounds": 7}, 7),
            ({"max_ticks": 12, "max_rounds": 9, "rounds": 7}, 12),
            ({"max_rounds": 9, "rounds": 7}, 9),
        ],
    )
    def test_die_reihenfolge_bleibt(self, payload, erwartet):
        """`max_ticks` vor `max_rounds` vor `rounds` — wie vor der Korrektur."""

        assert _ticks(payload) == erwartet

    def test_ohne_ganzzahligen_wert_bleibt_der_standard(self):
        standard = coerce_payload({})["clock"]["max_ticks"]

        assert _ticks({"max_ticks": "abc"}) == standard
