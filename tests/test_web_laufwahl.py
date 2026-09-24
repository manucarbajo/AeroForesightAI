"""Der Lauf-Browser findet und wählt (P7.3-U3.3 Teil 3, D6).

Das Kriterium des Pakets: **Mit 388 Läufen findet eine Suche nach einem
Rahmennamen den jüngsten mit höchstens zwei Eingaben; Prüfläufe sind
standardmäßig ausgeblendet.** Zwei Eingaben sind der Klick auf den Öffner und
das Tippen; ob der Dialog sich wirklich öffnet und den Fokus ins Suchfeld legt,
misst der Browser-Wächter (Marker `laufwahl`). Hier steht, was ohne Browser
prüfbar ist: die Art eines Laufs, Suche und Filter, der Umfang der Liste, der
Aufbau des Dialogs und die Verdrahtung.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dash import dcc, html

from dashboard.config_catalog import rahmenszenarien
from dashboard.run_browser import RunSummary
from dashboard.web import app as web_app
from dashboard.web import lauf_wahl, shell
from dashboard.web.pages import runs as runs_page
from src.orchestration.scenario_sweeps import load_all_sweep_configs

#: Wie viele Läufe das Kriterium nennt — gemessen vom Audit am 2026-09-11.
LAEUFE = 388


def _lauf(
    run_id: str,
    *,
    rahmen: str | None = "Standard-Ausgangslage",
    rahmen_id: str | None = "standard",
    quelle: str | None = "standard",
    zeit: datetime | None = None,
    modus: str | None = "mock_llm",
    degraded: bool = False,
) -> RunSummary:
    return RunSummary(
        run_id=run_id,
        run_dir=Path(run_id),
        ticks_completed=40,
        ticks_max=40,
        total_events=0,
        model=None,
        timestamp=(zeit or datetime(2026, 9, 14, tzinfo=UTC)).isoformat(),
        has_narrative=False,
        has_tick_mechanics=True,
        has_run_scenario=False,
        scenario_title=None,
        scenario_summary=None,
        degraded=degraded,
        rahmen_name=rahmen,
        compute_mode=modus,
        rahmen_id=rahmen_id,
        rahmen_quelle=quelle,
    )


def _rahmen_ids() -> set[str]:
    return {rahmen.id for rahmen in rahmenszenarien()}


def _zeilen(laeufe: list[RunSummary]) -> list[lauf_wahl.Eintrag]:
    return lauf_wahl.eintraege(
        laeufe,
        rahmen_ids=_rahmen_ids(),
        bezeichnungen={
            lauf.run_id: runs_page.lauf_bezeichnung(lauf, vorgabe="") for lauf in laeufe
        },
    )


def _walk(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _walk(kind)
    elif kinder is not None and not isinstance(kinder, str):
        yield from _walk(kinder)


# --- Die Art eines Laufs -----------------------------------------------------


class TestDieArtEinesLaufs:
    def test_every_current_frame_is_no_test_run(self):
        """Gesucht über `rahmenszenarien`, nicht über die vier heutigen Namen."""

        rahmen = rahmenszenarien()
        assert rahmen, "Keine Rahmenszenarien gefunden — misst die Suche noch?"
        for eintrag in rahmen:
            lauf = _lauf(f"sweeps/sweep_{eintrag.id}", rahmen_id=eintrag.id, quelle="preset")
            assert lauf_wahl.lauf_art(lauf, _rahmen_ids()) == "vergleich", eintrag.id

    def test_every_stress_test_is_a_test_run(self):
        stresstests = [c for c in load_all_sweep_configs() if c.art == "stresstest"]
        assert stresstests, "Keine Stresstests gefunden — misst die Suche noch?"
        for eintrag in stresstests:
            lauf = _lauf(f"run_{eintrag.id}", rahmen_id=eintrag.id, quelle="preset")
            assert lauf_wahl.lauf_art(lauf, _rahmen_ids()) == "pruef", eintrag.id

    def test_a_frame_whose_file_is_gone_is_a_test_run(self):
        """Der Fall aus dem Bestand: «Short Test Sweep» hat keine Datei mehr."""

        lauf = _lauf("sweeps/sweep_test_short", rahmen_id="test_short", quelle="preset")

        assert lauf_wahl.lauf_art(lauf, _rahmen_ids()) == "pruef"

    def test_the_standard_and_own_values_are_single_runs(self):
        for quelle in ("standard", "eigen", None):
            lauf = _lauf("run_20260914T080000Z", rahmen_id="standard", quelle=quelle)
            assert lauf_wahl.lauf_art(lauf, _rahmen_ids()) == "einzellauf", quelle

    def test_a_repetition_is_one(self):
        lauf = _lauf("batch_20260914T080000Z/run_002")

        assert lauf_wahl.lauf_art(lauf, _rahmen_ids()) == "wiederholung"

    def test_every_art_has_a_name_and_a_filter(self):
        gefiltert = {option["value"] for option in lauf_wahl.FILTER_OPTIONEN}

        assert set(lauf_wahl.ARTEN) <= gefiltert
        assert lauf_wahl.OHNE_PRUEF in gefiltert


# --- Das Kriterium: finden mit zwei Eingaben ---------------------------------


def _bestand() -> list[RunSummary]:
    """388 Läufe, der jüngste zuerst — Einzelläufe, Rahmen, Vergleiche, Prüfläufe."""

    rahmen = rahmenszenarien()
    stresstests = [c for c in load_all_sweep_configs() if c.art == "stresstest"]
    beginn = datetime(2026, 9, 14, 12, tzinfo=UTC)
    laeufe: list[RunSummary] = []
    for i in range(LAEUFE):
        zeit = beginn - timedelta(hours=i)
        stempel = zeit.strftime("%Y%m%dT%H%M%SZ")
        art = i % 6
        if art == 0:
            laeufe.append(_lauf(f"run_{stempel}", zeit=zeit))
        elif art in (1, 2):
            r = rahmen[i % len(rahmen)]
            kennung = f"sweeps/sweep_{r.id}_{stempel}" if art == 2 else f"run_{stempel}"
            laeufe.append(_lauf(kennung, rahmen=r.name, rahmen_id=r.id, quelle="preset", zeit=zeit))
        elif art == 3:
            laeufe.append(_lauf(f"batch_{stempel}/run_00{i % 5 + 1}", zeit=zeit))
        elif art == 4:
            s = stresstests[i % len(stresstests)]
            laeufe.append(
                _lauf(f"run_{stempel}", rahmen=s.name, rahmen_id=s.id, quelle="preset", zeit=zeit)
            )
        else:
            laeufe.append(
                _lauf(
                    f"sweeps/sweep_test_short_{stempel}",
                    rahmen="Short Test Sweep",
                    rahmen_id="test_short",
                    quelle="preset",
                    zeit=zeit,
                )
            )
    return laeufe


class TestEineSucheFindetDenJuengsten:
    def test_a_frame_name_finds_its_newest_run_first(self):
        """Eine Eingabe im Suchfeld, der Filter unberührt: der jüngste Lauf steht oben."""

        laeufe = _bestand()
        zeilen = _zeilen(laeufe)

        for rahmen in rahmenszenarien():
            treffer = lauf_wahl.filtern(zeilen, suche=rahmen.name, art=None)
            juengster = next(lauf for lauf in laeufe if lauf.rahmen_id == rahmen.id)

            assert treffer, rahmen.name
            assert treffer[0].run_id == juengster.run_id, (rahmen.name, treffer[0].run_id)

    def test_part_of_a_name_and_any_case_is_enough(self):
        zeilen = _zeilen(_bestand())
        rahmen = rahmenszenarien()[0]
        wort = rahmen.name.split()[0]

        treffer = lauf_wahl.filtern(zeilen, suche=wort[: max(4, len(wort) - 2)].upper(), art=None)

        assert any(zeile.bezeichnung.startswith(rahmen.name) for zeile in treffer)

    def test_every_word_must_match(self):
        zeilen = _zeilen(_bestand())

        assert (
            lauf_wahl.filtern(zeilen, suche="Standard-Ausgangslage Szenario-Vergleich", art=None)
            == []
        )

    def test_test_runs_are_hidden_until_asked_for(self):
        zeilen = _zeilen(_bestand())

        standard = lauf_wahl.filtern(zeilen, suche="", art=None)
        pruef = lauf_wahl.filtern(zeilen, suche="", art="pruef")

        assert standard and all(zeile.art != "pruef" for zeile in standard)
        assert pruef and all(zeile.art == "pruef" for zeile in pruef)
        assert len(standard) + len(pruef) == LAEUFE

    def test_the_row_says_art_mode_and_state(self):
        zeile = _zeilen([_lauf("run_x", modus="llm", degraded=True)])[0]

        assert zeile.merkmale == "Einzellauf · Mit Sprachmodell · beeinträchtigt"


# --- Die Liste bleibt klein --------------------------------------------------


class TestDieListeBleibtKlein:
    def test_at_most_the_cap_is_drawn_and_the_rest_is_counted(self):
        treffer = lauf_wahl.filtern(_zeilen(_bestand()), suche="", art=None)
        baum = html.Div(lauf_wahl.liste(treffer))

        knoepfe = [k for k in _walk(baum) if isinstance(k, html.Button)]
        texte = str(baum)

        assert len(knoepfe) == lauf_wahl.LISTE_MAX
        assert str(len(treffer) - lauf_wahl.LISTE_MAX) in texte

    def test_every_row_closes_the_dialog_and_names_its_run(self):
        treffer = lauf_wahl.filtern(_zeilen(_bestand()), suche="", art=None)
        knoepfe = [
            k for k in _walk(html.Div(lauf_wahl.liste(treffer))) if isinstance(k, html.Button)
        ]

        for knopf in knoepfe:
            assert knopf.type == "submit"
            assert knopf.id["type"] == lauf_wahl.EINTRAG and knopf.id["run"]

    def test_nothing_found_says_so(self):
        baum = html.Div(lauf_wahl.liste([]))

        assert not [k for k in _walk(baum) if isinstance(k, html.Button)]
        assert "Kein Lauf passt" in str(baum)


# --- Der Dialog ----------------------------------------------------------------


class TestDerDialog:
    def test_the_search_takes_the_focus_first(self):
        """`showModal()` fokussiert das erste fokussierbare Element."""

        fokussierbar = (dcc.Input, dcc.RadioItems, html.Button)
        erstes = next(k for k in _walk(lauf_wahl.dialog()) if isinstance(k, fokussierbar))

        assert getattr(erstes, "id", None) == lauf_wahl.SUCHE

    def test_the_rows_sit_in_a_dialog_form_and_the_search_does_not(self):
        formulare = [k for k in _walk(lauf_wahl.dialog()) if isinstance(k, html.Form)]

        assert len(formulare) == 1 and formulare[0].method == "dialog"
        im_formular = {getattr(k, "id", None) for k in _walk(formulare[0])}
        assert lauf_wahl.LISTE in im_formular
        assert lauf_wahl.SUCHE not in im_formular and lauf_wahl.FILTER not in im_formular

    def test_test_runs_are_filtered_out_when_it_opens(self):
        filter_ = next(
            k for k in _walk(lauf_wahl.dialog()) if getattr(k, "id", None) == lauf_wahl.FILTER
        )

        assert filter_.value == lauf_wahl.OHNE_PRUEF


# --- Die Verdrahtung -----------------------------------------------------------


class TestDieAppIstVerdrahtet:
    def test_the_layout_carries_the_dialog_once(self):
        treffer = [
            k for k in _walk(web_app.serve_layout()) if getattr(k, "id", None) == lauf_wahl.DIALOG
        ]

        assert len(treffer) == 1

    def test_a_row_sets_the_selected_run(self):
        karte = web_app.app.callback_map

        assert any(
            "selected-run-store.data" in schluessel
            and lauf_wahl.EINTRAG in json.dumps(eintrag["inputs"])
            for schluessel, eintrag in karte.items()
        )

    def test_the_opener_names_the_selected_run(self):
        karte = web_app.app.callback_map

        assert any(f"{shell.LAUF_WAHL}.children" in schluessel for schluessel in karte)

    def test_no_callback_talks_to_the_old_select(self):
        assert "shell-run-select" not in json.dumps(
            {
                schluessel: eintrag["inputs"]
                for schluessel, eintrag in web_app.app.callback_map.items()
            }
        )
        assert not any("shell-run-select" in schluessel for schluessel in web_app.app.callback_map)
