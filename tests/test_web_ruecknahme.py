"""«Lauf & Ablage» aufgeräumt (P7.4-U4.3).

Zwei Zusagen des Pakets:

* **Zurücksetzen lässt sich mit einem Klick rückgängig machen.** Bis dahin hieß
  der Knopf «Auf Standard-Config zurücksetzen» und verwarf den ganzen Entwurf —
  ohne Rückfrage, ohne Weg zurück, in einem als optional markierten Schritt.
* **Der Schritt hat eine Überschriftebene.** Unter dem Schritttitel stand ein
  Abschnitt «Fragestellung» mit eigener Einleitung über einem Feld, das ebenfalls
  «Fragestellung» heißt.

Der zweite Speicherweg in diesem Schritt ist seit U4.5 fort
(`tests/test_web_sichern.py`).
"""

from __future__ import annotations

from dash import html, no_update

from dashboard.web import app as web_app
from dashboard.web import config_editor
from dashboard.web.config_editor import controls as c
from dashboard.web.config_editor import wizard
from dashboard.web.state import RUECKNAHME_ID, initial_draft_dict

ZURUECKSETZEN = c.action_id("reset")
RUECKGAENGIG = c.action_id("reset-undo")

UEBERSCHRIFTEN = (html.H1, html.H2, html.H3, html.H4, html.H5, html.H6)


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


def _rumpf(titel: str):
    """Der Rumpf des Schritts, dessen Überschrift *titel* ist — gesucht, nicht gezählt."""

    entwurf = initial_draft_dict()
    for index in range(len(wizard.STEPS)):
        inhalt = wizard.content(entwurf, index)
        kopf = next(k for k in _walk(inhalt) if isinstance(k, html.H1))
        if kopf.children == titel:
            return next(k for k in _walk(inhalt) if getattr(k, "id", None) == "wizard-body")
    raise AssertionError(f"Kein Schritt heißt «{titel}»")


class TestZuruecksetzenLaesstSichZuruecknehmen:
    def test_reset_then_undo_restores_the_draft_exactly(self):
        vorher = initial_draft_dict()
        vorher["rounds"] = 77
        vorher["simulation_description"] = "Probe"

        zurueck, _, _ = config_editor._handle_action(ZURUECKSETZEN, dict(vorher), [])
        gemerkt = config_editor._ruecknahme_nach(ZURUECKSETZEN, vorher, None)
        wieder, _, ton = config_editor._handle_action(RUECKGAENGIG, zurueck, [], ruecknahme=gemerkt)

        assert zurueck["rounds"] != 77
        assert wieder == vorher
        assert ton == "erfolg"

    def test_an_undo_is_used_up(self):
        """Sonst setzte ein zweiter Klick auf «Rückgängig» wieder zurück."""

        assert config_editor._ruecknahme_nach(RUECKGAENGIG, {"a": 1}, {"b": 2}) is None

    def test_other_actions_leave_what_was_kept(self):
        gemerkt = config_editor._ruecknahme_nach(c.action_id("suggest-name"), {}, {"b": 2})

        assert gemerkt is no_update

    def test_undo_without_anything_kept_changes_nothing(self):
        entwurf = initial_draft_dict()

        wieder, _, ton = config_editor._handle_action(
            RUECKGAENGIG, dict(entwurf), [], ruecknahme=None
        )

        assert wieder == entwurf
        assert ton == "info"

    def test_only_one_message_carries_the_undo_button(self):
        """Dieselbe Meldung geht an zwei Orte — zweimal dieselbe Kennung wäre ein Laufzeitfehler."""

        mit = config_editor._meldung(ZURUECKSETZEN, "x", "erfolg", knopf=True)
        ohne = config_editor._meldung(ZURUECKSETZEN, "x", "erfolg", knopf=False)

        assert any(getattr(k, "id", None) == RUECKGAENGIG for k in _walk(mit))
        assert not any(getattr(k, "id", None) == RUECKGAENGIG for k in _walk(ohne))

    def test_other_messages_offer_no_undo(self):
        meldung = config_editor._meldung(c.action_id("suggest-name"), "x", "erfolg", knopf=True)

        assert not any(getattr(k, "id", None) == RUECKGAENGIG for k in _walk(meldung))

    def test_the_app_keeps_the_draft_from_before(self):
        karte = web_app.app.callback_map
        treffer = [
            k for k in _walk(web_app.serve_layout()) if getattr(k, "id", None) == RUECKNAHME_ID
        ]

        assert any(f"{RUECKNAHME_ID}.data" in schluessel for schluessel in karte)
        assert len(treffer) == 1

    def test_the_button_says_it_can_be_undone(self):
        assert "rückgängig" in str(config_editor.reset_button()).lower()


class TestLaufUndAblageHatEineUeberschriftebene:
    def test_the_step_body_carries_no_heading(self):
        ueberschriften = [
            k for k in _walk(_rumpf("Lauf & Ablage")) if isinstance(k, UEBERSCHRIFTEN)
        ]

        assert not ueberschriften, [str(k.children) for k in ueberschriften]

    def test_the_search_would_notice_a_section(self):
        """Gegen die eigene Blindheit: «Technik» trägt einen Abschnitt mit Überschrift."""

        assert any(isinstance(k, UEBERSCHRIFTEN) for k in _walk(_rumpf("Technik")))
