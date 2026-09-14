"""«Prüfen & Starten» als Zusammenfassung in fester Reihenfolge (P7.4-U4.4).

Das Audit (E9): Der Schritt beantwortete seine eine Frage auf acht Blöcke
verteilt — Name, Satz, Horizont-Hinweis, Dauer, Herkunft, sechs Kacheln mit
Modellinterna, die Abweichungen erst ganz unten, dann ein Speicherhinweis. Gemessen
bei 1440 × 900 standen allein die Kacheln 260 px hoch.

**Was gilt:** was läuft (ein Satz) und wie lange, drei Werte, was abweicht, was zu
beachten ist — in dieser Reihenfolge. Modellinterna und Herkunft stehen hinter
«Technische Details»; ein Hinweis, der sich in einem Schritt beheben lässt, trägt
einen Knopf dorthin. Dass der Schritt dabei auf einen Bildschirm passt, misst der
Höhenwächter.

Verglichen wird ohne Groß- und Kleinschreibung: Eine Kachel setzt ihre
Beschriftung in Großbuchstaben («LÄNGE»).
"""

from __future__ import annotations

import json

from dash import html

from dashboard.web import app as web_app
from dashboard.web.config_editor import start_flow, wizard
from dashboard.web.state import initial_draft_dict

INTERNA = ("Ziel-Auslastung", "Segmente", "Aktive Systemgrößen")


def _walk(knoten, *, ohne_klappen: bool = False):
    if ohne_klappen and isinstance(knoten, html.Details):
        return
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind, ohne_klappen=ohne_klappen)
    elif kinder is not None:
        # Auch ein Text als einziges Kind: Der erste Anlauf ließ ihn aus und sah
        # dadurch keine einzige Kachelbeschriftung.
        yield from _walk(kinder, ohne_klappen=ohne_klappen)


def _texte(knoten, *, ohne_klappen: bool = False) -> list[str]:
    return [k.casefold() for k in _walk(knoten, ohne_klappen=ohne_klappen) if isinstance(k, str)]


def _enthaelt(texte: list[str], stueck: str) -> bool:
    return any(stueck.casefold() in t for t in texte)


def _position(texte: list[str], stueck: str) -> int:
    return next(i for i, t in enumerate(texte) if stueck.casefold() in t)


def _technische_details(baum) -> html.Details:
    return next(
        k
        for k in _walk(baum)
        if isinstance(k, html.Details) and _enthaelt(_texte(k), "Technische Details")
    )


def _pruefschritt(draft: dict | None = None):
    return wizard._final_step(draft or initial_draft_dict())


class TestDieReihenfolgeIstFest:
    def test_what_runs_values_deviations_notes_details(self):
        texte = _texte(_pruefschritt())

        reihe = [
            _position(texte, "Sie starten"),
            _position(texte, "Länge"),
            _position(texte, "ausgelieferten Werte"),
            _position(texte, "Technische Details"),
        ]

        assert reihe == sorted(reihe), reihe

    def test_notes_stand_between_deviations_and_details(self):
        entwurf = initial_draft_dict()
        entwurf["run_count"] = 2
        entwurf["use_seed"] = False
        texte = _texte(_pruefschritt(entwurf))

        hinweis = _position(texte, "Mehrere Wiederholungen")

        assert (
            _position(texte, "Zufallsstartwert") < hinweis < _position(texte, "Technische Details")
        )

    def test_the_save_hint_is_gone(self):
        """Gesichert wird oben rechts (U4.5); in der Zusammenfassung steht es nicht."""

        assert not _enthaelt(_texte(_pruefschritt()), "Als Szenario sichern")

    def test_the_guard_sees_the_tiles(self):
        """Gegen Blindheit: Ohne Kachelbeschriftung prüften die Zusagen darüber nichts."""

        assert _enthaelt(_texte(_pruefschritt()), "Wiederholungen")


class TestModellinternaStehenHinterTechnischenDetails:
    def test_internals_are_not_visible_before_opening(self):
        offen = _texte(_pruefschritt(), ohne_klappen=True)

        for wort in INTERNA:
            assert not _enthaelt(offen, wort), wort

    def test_they_and_the_provenance_are_one_click_away(self):
        details = _texte(_technische_details(_pruefschritt()))

        for wort in (*INTERNA, "Codestand", "Konfiguration"):
            assert _enthaelt(details, wort), wort

    def test_no_disclosure_inside_the_details(self):
        """Die Herkunft war selbst eine Klappe — in einer Klappe wäre das die Regelverletzung."""

        details = _technische_details(_pruefschritt())

        assert not [k for k in _walk(details) if isinstance(k, html.Details) and k is not details]

    def test_a_comparison_keeps_its_own_tiles(self):
        entwurf = initial_draft_dict()
        entwurf["run_all_sweeps"] = True
        offen = _texte(_pruefschritt(entwurf), ohne_klappen=True)

        assert _enthaelt(offen, "Rahmenszenarien")
        for wort in INTERNA:
            assert not _enthaelt(offen, wort), wort


class TestDasBedienfeldZeigtDieDreiWerte:
    def test_length_repetitions_and_seed(self):
        """So stand es seit Langem in «Die erste Simulation» — gezeigt wurde die Ziel-Auslastung."""

        schmal = _texte(start_flow.preflight(initial_draft_dict(), [], slot="rail", compact=True))

        for wort in ("Länge", "Wiederholungen", "Zufallsstartwert"):
            assert _enthaelt(schmal, wort), wort
        assert not _enthaelt(schmal, "Ziel-Auslastung")


class TestEinHinweisFuehrtZumSchritt:
    def _entwurf(self) -> dict:
        entwurf = initial_draft_dict()
        entwurf["run_count"] = 2
        entwurf["use_seed"] = False
        entwurf["no_scenarios"] = True
        return entwurf

    def test_each_fixable_note_carries_a_jump(self):
        kennungen = [getattr(k, "id", None) for k in _walk(_pruefschritt(self._entwurf()))]

        assert start_flow.sprung_id("modus") in kennungen
        assert start_flow.sprung_id("technik") in kennungen

    def test_every_jump_names_a_real_step(self):
        schluessel = {step.key for step in wizard.STEPS}
        spruenge = [
            k.id
            for k in _walk(_pruefschritt(self._entwurf()))
            if isinstance(getattr(k, "id", None), dict) and k.id.get("type") == start_flow.SPRUNG
        ]

        assert spruenge
        assert {sprung["schritt"] for sprung in spruenge} <= schluessel

    def test_the_rail_offers_no_jump(self):
        """Im Bedienfeld stünde man im Leitstand und schaltete einen unsichtbaren Schritt um."""

        schmal = start_flow.preflight(self._entwurf(), [], slot="rail", compact=True)

        assert not [
            k
            for k in _walk(schmal)
            if isinstance(getattr(k, "id", None), dict) and k.id.get("type") == start_flow.SPRUNG
        ]

    def test_the_navigation_listens(self):
        karte = web_app.app.callback_map

        assert any(
            wizard.STEP_STORE in schluessel and start_flow.SPRUNG in json.dumps(eintrag["inputs"])
            for schluessel, eintrag in karte.items()
        )
