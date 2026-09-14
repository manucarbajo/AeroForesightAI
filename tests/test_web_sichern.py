"""Ein Speicherweg für Szenarien (P7.4-U4.5).

Das Kriterium des Pakets: **Genau eine Aktion löst `save_custom_sweep_preset`
aus.** Bis dahin waren es vier, mit drei Namensregeln, und keiner warnte vor dem
Überschreiben. Gesucht wird jeder Aufruf im Quelltext unter `dashboard/web/`,
nicht die vier bekannten Stellen — ein fünfter Weg fällt ohne Eintrag auf.
Dass sich der Dialog im Browser modal öffnet und den Namen fokussiert, misst der
Browser-Wächter (Marker `rueckfrage`).
"""

from __future__ import annotations

import ast
import json
from datetime import UTC, datetime
from pathlib import Path

from dash import dcc, html

from dashboard import config_catalog
from dashboard.web import app as web_app
from dashboard.web import shell
from dashboard.web.config_editor import sichern, wizard
from dashboard.web.state import initial_draft_dict

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"

#: Der Name der Funktion, die ein Szenario unter `configs/sweeps/` schreibt.
SCHREIBER = "save_custom_sweep_preset"


def _aufrufe(quelle: str) -> list[int]:
    """Zeilen, an denen `save_custom_sweep_preset` gerufen wird — als Name oder Attribut."""

    zeilen = []
    for knoten in ast.walk(ast.parse(quelle)):
        if not isinstance(knoten, ast.Call):
            continue
        ziel = knoten.func
        if (isinstance(ziel, ast.Name) and ziel.id == SCHREIBER) or (
            isinstance(ziel, ast.Attribute) and ziel.attr == SCHREIBER
        ):
            zeilen.append(knoten.lineno)
    return zeilen


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


class TestEsGibtEinenSpeicherweg:
    def test_exactly_one_call_writes_a_scenario(self):
        funde = [
            f"{pfad.relative_to(WEB_ROOT).as_posix()}:{zeile}"
            for pfad in sorted(WEB_ROOT.rglob("*.py"))
            for zeile in _aufrufe(pfad.read_text(encoding="utf-8"))
        ]

        assert len(funde) == 1, f"Aufrufe von `{SCHREIBER}` unter dashboard/web/: {funde}"
        assert funde[0].startswith("config_editor/sichern.py:"), funde

    def test_the_search_would_notice_a_second_way(self):
        zweiter = "from x import save_custom_sweep_preset\nsave_custom_sweep_preset(d, 'a')\n"
        als_attribut = "import x\nx.save_custom_sweep_preset(d, 'a')\n"

        assert _aufrufe(zweiter) == [2]
        assert _aufrufe(als_attribut) == [2]

    def test_the_old_ways_are_gone(self):
        """Zweiter Kopfzeilen-Knopf, Fußleiste und Klappe — keiner lebt als Kennung weiter."""

        assert not hasattr(shell, "ACTION_SNAPSHOT")
        assert not hasattr(wizard, "SAVE")
        gerendert = json.dumps(
            [str(wizard.content(initial_draft_dict(), i)) for i in range(len(wizard.STEPS))]
        )
        assert "save-preset" not in gerendert and "preset-name" not in gerendert

    def test_the_header_button_opens_the_dialog(self):
        karte = web_app.app.callback_map

        assert any(
            f"{sichern.DIALOG}.title" in schluessel
            and shell.ACTION_SAVE in json.dumps(eintrag["inputs"])
            for schluessel, eintrag in karte.items()
        )
        assert any(f"{sichern.NAME}.value" in schluessel for schluessel in karte)

    def test_the_layout_carries_the_dialog_once(self):
        treffer = [
            k for k in _walk(web_app.serve_layout()) if getattr(k, "id", None) == sichern.DIALOG
        ]

        assert len(treffer) == 1


class TestDerDialogWarntVorDemUeberschreiben:
    def test_an_existing_scenario_is_named_before_it_is_replaced(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_catalog, "SWEEPS_DIR", tmp_path)
        (tmp_path / "vorhanden.json").write_text("{}", encoding="utf-8")

        hinweis, gesperrt = sichern.pruefen("Vorhanden", zeitstempel=False)

        assert "vorhanden" in str(hinweis) and "ersetzt" in str(hinweis)
        assert not gesperrt

    def test_a_new_name_says_nothing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_catalog, "SWEEPS_DIR", tmp_path)

        assert sichern.pruefen("Neu", zeitstempel=False) == (None, False)

    def test_a_timestamp_never_replaces_the_named_one(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_catalog, "SWEEPS_DIR", tmp_path)
        (tmp_path / "vorhanden.json").write_text("{}", encoding="utf-8")

        assert sichern.pruefen("Vorhanden", zeitstempel=True) == (None, False)

    def test_without_a_name_nothing_can_be_saved(self):
        _, gesperrt = sichern.pruefen("   ", zeitstempel=False)

        assert gesperrt

    def test_the_timestamp_is_utc_in_the_form_of_a_run_id(self):
        jetzt = datetime(2026, 9, 14, 8, 30, 5, tzinfo=UTC)

        assert sichern.dateiname("probe", zeitstempel=True, jetzt=jetzt) == "probe_20260914T083005Z"


class TestDerVorschlag:
    def test_the_run_name_is_suggested(self):
        assert sichern.vorschlag({"simulation_name": "Freiwillige Wende lang"}) == (
            "Freiwillige Wende lang"
        )

    def test_the_default_name_is_not(self):
        vorgabe = str(config_catalog.load_config_file("simulation_config.json").get("name", ""))

        assert sichern.vorschlag({"simulation_name": vorgabe}) == sichern.OHNE_NAMEN
        assert sichern.vorschlag({}) == sichern.OHNE_NAMEN


class TestDerAufbau:
    def test_the_name_takes_the_focus_first(self):
        fokussierbar = (dcc.Input, dcc.Checklist, html.Button)
        erstes = next(k for k in _walk(sichern.dialog()) if isinstance(k, fokussierbar))

        assert getattr(erstes, "id", None) == sichern.NAME

    def test_cancel_comes_before_save_and_both_close_it(self):
        formulare = [k for k in _walk(sichern.dialog()) if isinstance(k, html.Form)]
        assert len(formulare) == 1 and formulare[0].method == "dialog"

        knoepfe = [k for k in _walk(formulare[0]) if isinstance(k, html.Button)]
        assert "Abbrechen" in str(knoepfe[0]) and knoepfe[1].id == sichern.BESTAETIGEN
        assert all(k.type == "submit" for k in knoepfe)

    def test_the_name_is_outside_the_form(self):
        formular = next(k for k in _walk(sichern.dialog()) if isinstance(k, html.Form))

        assert sichern.NAME not in {getattr(k, "id", None) for k in _walk(formular)}


class TestEinWortEineBedeutung:
    """«Zwischenstand» ist der Checkpoint eines Laufs — nicht eine Kopie mit Zeitstempel.

    P7.3-U3.4 hatte den zweiten Kopfzeilen-Knopf «Zwischenstand sichern» genannt,
    dasselbe Wort, das `checkpoint_interval` im Glossar trägt. Aufgefallen ist es beim
    Nachlesen. Gesucht wird das Wort im gezeichneten Dialog, nicht im Quelltext.
    """

    def test_the_dialog_does_not_borrow_the_checkpoint_word(self):
        from dashboard.web.config_editor import glossary

        assert "Zwischenstand" in glossary.get("checkpoint_interval").label
        assert "Zwischenstand" not in str(sichern.dialog())
