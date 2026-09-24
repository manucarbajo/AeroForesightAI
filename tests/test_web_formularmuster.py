"""Formularmuster in Einrichten: gesperrte Felder mit Grund, drei Zustände der Ollama-Prüfung (P7.4-U4.2).

Das Kriterium des Pakets: **Bei «Nur Zahlen» sind Modellname, Adresse,
Kreativität und Antwortlänge `disabled` und tragen einen Grund.**

Welche Felder das sind, steht nicht hier, sondern kommt aus der Messung:
`NUR_MIT_SPRACHMODELL` in `tests/test_web_wirkung.py` hält die Felder fest, die nur
wirken, wenn wirklich ein Sprachmodell gebaut wird. Ändert sich die Messung, zieht
diese Zusage mit — ein fünftes Feld dort wäre hier sofort gemeldet.

**Und auch «Ohne Sprachmodell» und der Szenario-Vergleich sperren**, gemessen am
selben Ort: Unter `mock_llm` bewegen die vier nichts, und der Vergleich übernimmt
vom Entwurf gar nichts (`ERWARTET[SWEEP]` ist leer).
"""

from __future__ import annotations

import pytest
from dash import dcc, html

from dashboard.web import components as ui
from dashboard.web.config_editor import compute_mode, llm_pipeline
from dashboard.web.state import initial_draft_dict
from tests.test_web_wirkung import NUR_MIT_SPRACHMODELL


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


def _entwurf(modus: str, *, vergleich: bool = False) -> dict:
    entwurf = compute_mode.apply(initial_draft_dict(), modus)
    entwurf["run_all_sweeps"] = vergleich
    return entwurf


def _felder(baum) -> dict[str, tuple[object, str]]:
    """Feldname → (Eingabe, Text des Feldrahmens) für jede Eingabe mit Konfigurations-ID."""

    gefunden: dict[str, tuple[object, str]] = {}
    for rahmen in _walk(baum):
        if not isinstance(rahmen, html.Div):
            continue
        for kind in _walk(rahmen):
            kennung = getattr(kind, "id", None)
            if (
                isinstance(kind, (dcc.Input, dcc.Slider))
                and isinstance(kennung, dict)
                and kennung.get("field") in NUR_MIT_SPRACHMODELL
                and kennung["field"] not in gefunden
                and rahmen.children is not None
                and isinstance(rahmen.children, list)
                and any(isinstance(k, html.Label) for k in rahmen.children)
            ):
                gefunden[kennung["field"]] = (kind, str(rahmen))
    return gefunden


class TestFelderOhneWirkungSindGesperrt:
    def test_the_search_finds_every_field_that_needs_a_model(self):
        """Gegen die eigene Blindheit: alle vier stehen im Schritt «Technik»."""

        assert set(_felder(llm_pipeline.layout(_entwurf(compute_mode.WITH_LLM)))) == set(
            NUR_MIT_SPRACHMODELL
        )

    @pytest.mark.parametrize("modus", [compute_mode.NUMBERS_ONLY, compute_mode.MOCK])
    def test_without_a_model_they_are_disabled_and_say_why(self, modus):
        grund = llm_pipeline.sperrgrund(_entwurf(modus))
        felder = _felder(llm_pipeline.layout(_entwurf(modus)))

        assert grund and compute_mode.SHORT_LABELS[modus] in grund
        for feld, (eingabe, rahmen) in felder.items():
            assert eingabe.disabled is True, feld
            assert grund in rahmen, feld

    def test_with_a_model_they_are_free(self):
        entwurf = _entwurf(compute_mode.WITH_LLM)

        assert llm_pipeline.sperrgrund(entwurf) is None
        for feld, (eingabe, _) in _felder(llm_pipeline.layout(entwurf)).items():
            assert not getattr(eingabe, "disabled", False), feld

    def test_a_comparison_takes_none_of_them(self):
        entwurf = _entwurf(compute_mode.WITH_LLM, vergleich=True)
        grund = llm_pipeline.sperrgrund(entwurf)

        assert grund and "Szenario-Vergleich" in grund
        for feld, (eingabe, rahmen) in _felder(llm_pipeline.layout(entwurf)).items():
            assert eingabe.disabled is True and grund in rahmen, feld

    def test_the_slider_shows_its_value_only_while_it_is_moved(self):
        """E8: Der Tooltip des Schiebereglers stand dauerhaft eingeblendet über dem Feld."""

        schieber = [
            k
            for k in _walk(llm_pipeline.layout(_entwurf(compute_mode.WITH_LLM)))
            if isinstance(k, dcc.Slider)
        ]

        assert schieber
        assert all(not (k.tooltip or {}).get("always_visible") for k in schieber)


class TestDieOllamaPruefungHatDreiZustaende:
    def test_while_checking_it_does_not_look_unreachable(self):
        wartet = str(compute_mode.placeholder("start"))

        assert "af-status__dot--pruefen" in wartet
        assert "af-status__dot--aus" not in wartet

    def test_no_address_is_off(self):
        entwurf = initial_draft_dict()
        entwurf["base_url"] = ""

        assert "af-status__dot--aus" in str(compute_mode.availability(entwurf))

    @pytest.mark.parametrize("zustand", ["bereit", "pruefen", "aus"])
    def test_each_state_has_its_own_class(self, zustand):
        assert f"af-status__dot--{zustand}" in str(ui.status_dot(zustand, "Probe"))

    def test_an_unknown_state_fails_loudly(self):
        with pytest.raises(ValueError, match="Zustand"):
            ui.status_dot("vielleicht", "Probe")
