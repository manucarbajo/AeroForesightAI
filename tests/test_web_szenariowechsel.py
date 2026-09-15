"""Ein Szenariowechsel verwirft die Abweichungen, mit «Rückgängig» (P7.13-U13.2 Teil 2).

Eine Abweichung ist der Unterschied zu **einem** Szenario; auf ein anderes
gelegt, hieße sie dort etwas anderes. Die Zusagen:

1. **Wechsel mit Abweichungen verwirft sie** — Verläufe und Preisstrategie.
2. **Ohne Wechsel oder ohne Abweichung bleibt alles**, wie es ist.
3. **«Rückgängig» stellt den Entwurf von vorher genau wieder her**, samt Szenario.
4. **Die Meldung nennt das alte Szenario** und trägt den Knopf.
"""

from __future__ import annotations

from dash import html

from dashboard.web import app as web_app
from dashboard.web import config_editor
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor import verlaeufe
from dashboard.web.state import RUECKNAHME_ID, initial_draft_dict

RUECKGAENGIG = c.action_id("reset-undo")


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


def _unter(szenario: str, **felder) -> dict:
    entwurf = initial_draft_dict()
    entwurf["scenario_mode"] = "sweep"
    entwurf["sweep_id"] = szenario
    entwurf.update(felder)
    return entwurf


_ABWEICHUNG = {
    "carbon_tax_level": {"property_id": "carbon_tax_level", "baseline": 77.0, "rules": []}
}


class TestEinWechselVerwirftDieAbweichungen:
    def test_switching_with_deviations_discards_them(self):
        vorher = _unter("business_as_usual", abweichungen=_ABWEICHUNG, preisstrategie="marge")
        nachher = {**vorher, "sweep_id": "freiwillige_wende"}

        neu, verworfen = verlaeufe.nach_szenariowechsel(vorher, nachher)

        assert verworfen is True
        assert neu["abweichungen"] == {}
        assert neu["preisstrategie"] is None
        assert neu["sweep_id"] == "freiwillige_wende"

    def test_switching_to_the_standard_counts_too(self):
        vorher = _unter("business_as_usual", abweichungen=_ABWEICHUNG)
        nachher = {**vorher, "scenario_mode": "basis"}

        _, verworfen = verlaeufe.nach_szenariowechsel(vorher, nachher)

        assert verworfen is True

    def test_without_deviations_nothing_happens(self):
        vorher = _unter("business_as_usual")
        nachher = {**vorher, "sweep_id": "freiwillige_wende"}

        neu, verworfen = verlaeufe.nach_szenariowechsel(vorher, nachher)

        assert verworfen is False
        assert neu is nachher

    def test_the_same_scenario_keeps_them(self):
        """Ein anderes Feld zu ändern ist kein Wechsel — die Abweichungen bleiben."""

        vorher = _unter("business_as_usual", abweichungen=_ABWEICHUNG)
        nachher = {**vorher, "rounds": 60}

        neu, verworfen = verlaeufe.nach_szenariowechsel(vorher, nachher)

        assert verworfen is False
        assert neu["abweichungen"] == _ABWEICHUNG


class TestRueckgaengigHoltSieZurueck:
    def test_undo_restores_the_draft_with_its_scenario(self):
        vorher = _unter("business_as_usual", abweichungen=_ABWEICHUNG, preisstrategie="marge")
        nachher, _ = verlaeufe.nach_szenariowechsel(
            vorher, {**vorher, "sweep_id": "freiwillige_wende"}
        )

        wieder, _, ton = config_editor._handle_action(
            RUECKGAENGIG, dict(nachher), [], ruecknahme=dict(vorher)
        )

        assert wieder == vorher
        assert ton == "erfolg"

    def test_the_message_names_the_old_scenario_and_offers_undo(self):
        vorher = _unter("business_as_usual", abweichungen=_ABWEICHUNG)

        meldung = config_editor._wechsel_meldung(vorher)

        assert "Business as Usual" in str(meldung)
        assert "business_as_usual" not in str(meldung), "Die Meldung nennt eine Kennung"
        assert any(getattr(k, "id", None) == RUECKGAENGIG for k in _walk(meldung))

    def test_the_sync_callback_keeps_the_draft_from_before(self):
        """Die Wahl kommt in `_sync` an — dort muss auch der Stand davor gemerkt werden.

        **Erkannt am Eingang, nicht nur an den Ausgängen**: Die erste Fassung suchte
        einen Callback, der Entwurf, Rücknahme und Meldung schreibt — und fand
        `_actions`, das alle drei ebenfalls schreibt. Die Gegenprobe, die `_sync` den
        Ausgang nahm, blieb deshalb grün. `_sync` ist der Callback, der die Werte
        **aller** Konfigurationsfelder liest — über das Muster `ALL`; `_llm_status`
        liest dagegen ein einzelnes Feld (den Rechenmodus) und zählt nicht.
        """

        sync = [
            schluessel
            for schluessel, eintrag in web_app.app.callback_map.items()
            if any(
                '"type":"cfg"' in e.get("id", "")
                and '"field":["ALL"]' in e.get("id", "")
                and e.get("property") == "value"
                for e in eintrag.get("inputs", [])
            )
        ]

        assert len(sync) == 1, "Gegen Blindheit: genau ein Callback liest die Konfigurationsfelder"
        assert RUECKNAHME_ID in sync[0]
        assert "cfg-status.children" in sync[0]

    def test_the_undo_button_exists_only_once_in_the_layout(self):
        """Vor jeder Meldung steht kein Knopf im Baum — die Kennung kommt nur mit ihr."""

        treffer = [
            k for k in _walk(web_app.serve_layout()) if getattr(k, "id", None) == RUECKGAENGIG
        ]

        assert treffer == []
        assert isinstance(config_editor._wechsel_meldung(_unter("business_as_usual")), html.Div)
