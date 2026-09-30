"""Jede Ansicht der Dash-App muss sich bauen lassen — auch aus Trümmern.

Ein Run-Verzeichnis kann unvollständig sein (abgebrochener Lauf, alter Run
ohne `timeseries/`). Streamlit hat solche Fälle mit einem Hinweis abgefangen;
diese Tests halten fest, dass die Dash-Ansichten das ebenfalls tun, statt eine
Exception bis in den Callback durchzureichen.
"""

from __future__ import annotations

import json

import pytest

from dashboard.run_browser import RunSummary
from dashboard.web import app as web_app
from dashboard.web import components as ui
from dashboard.web import config_editor
from dashboard.web.config_editor import _handle_action
from dashboard.web.files_route import resolve_within_outputs, run_file_url
from dashboard.web.pages import launch as launch_page
from dashboard.web.pages import runs as runs_page
from dashboard.web.state import draft_to_dict, initial_draft_dict
from dashboard.web.views import (
    animation,
    explorer,
    figures,
    files,
    narrative,
    overview,
    scenario,
)

VIEWS = [overview, scenario, narrative, animation, figures, files, explorer]


def _text(component) -> str:
    return str(component)


@pytest.fixture
def empty_run(tmp_path):
    """Ein Run-Verzeichnis ohne jedes Artefakt."""

    run_dir = tmp_path / "run_leer"
    run_dir.mkdir()
    return run_dir


@pytest.fixture
def minimal_run(tmp_path):
    """Ein Run mit Metadaten und Zeitreihen, aber ohne History und Figures."""

    run_dir = tmp_path / "run_minimal"
    (run_dir / "timeseries").mkdir(parents=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": 3,
                "ticks_max": 3,
                "total_events": 5,
                "model": "llama3.2",
                "market_enabled": True,
                "timestamp": "2026-08-22T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {"tick": 1, "booking_rate": 0.5, "ticket_price": 100.0},
                    {"tick": 2, "booking_rate": 0.4, "ticket_price": 105.0},
                    {"tick": 3, "booking_rate": 0.45, "ticket_price": 102.0},
                ]
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "price_history.json").write_text(
        json.dumps([{"round_number": t, "price": 100.0 + t} for t in (1, 2, 3)]),
        encoding="utf-8",
    )
    (run_dir / "final_narrative.md").write_text("# Bericht\n\nInhalt.", encoding="utf-8")
    (run_dir / "timeseries" / "properties.csv").write_text(
        "tick,carbon_tax_level,income_index,staff_cost_index\n1,50,1.0,1.0\n2,60,1.1,1.05\n",
        encoding="utf-8",
    )
    (run_dir / "timeseries" / "factors.csv").write_text(
        "tick,F1,F2\n1,F1.1,F2.1\n2,F1.2,F2.1\n", encoding="utf-8"
    )
    return run_dir


# --- Run-Ansichten ---------------------------------------------------------


@pytest.mark.parametrize("view", VIEWS, ids=lambda v: v.__name__.rsplit(".", 1)[-1])
def test_views_render_for_an_empty_run(view, empty_run):
    """Kein Artefakt da: es muss ein Hinweis kommen, keine Exception."""

    rendered = _text(view.render(empty_run, "run_leer"))

    assert rendered  # gerendert, nicht geworfen
    assert "Traceback" not in rendered


@pytest.mark.parametrize("view", VIEWS, ids=lambda v: v.__name__.rsplit(".", 1)[-1])
def test_views_render_for_a_minimal_run(view, minimal_run):
    assert _text(view.render(minimal_run, "run_minimal"))


def test_overview_shows_metrics_and_two_charts(minimal_run):
    rendered = _text(overview.render(minimal_run, "run_minimal"))

    assert "llama3.2" in rendered
    assert "Buchungsrate" in rendered
    assert "Ticketpreis" in rendered


def test_narrative_reports_a_missing_file(empty_run):
    assert "final_narrative.md" in _text(narrative.render(empty_run, "run_leer"))


def test_animation_reports_missing_history(empty_run):
    assert "individuals_history.csv" in _text(animation.render(empty_run, "run_leer"))


@pytest.mark.parametrize("tab", [value for _, value in figures.TABS])
def test_every_figures_subtab_renders(tab, minimal_run):
    assert _text(figures._render_view(tab, minimal_run))


def test_runs_page_render_tab_survives_a_missing_directory(tmp_path):
    selection = {"run_id": "weg", "run_dir": str(tmp_path / "gibt-es-nicht")}

    assert "Laufverzeichnis fehlt" in _text(runs_page.render_tab("overview", selection))


def _summary(tmp_path, **overrides) -> RunSummary:
    fields = dict(
        run_id="run_test",
        run_dir=tmp_path,
        ticks_completed=3,
        ticks_max=3,
        total_events=5,
        model="llama3.2",
        timestamp="2026-08-26T00:00:00Z",
        has_narrative=False,
        has_tick_mechanics=False,
        has_run_scenario=False,
        scenario_title=None,
        scenario_summary=None,
    )
    fields.update(overrides)
    return RunSummary(**fields)


def test_degraded_run_is_flagged_above_every_tab(tmp_path):
    """P0.1: Der Banner sitzt im Kopf der Seite, nicht in einer einzelnen Ansicht."""

    rendered = _text(runs_page.lauf_kopf(_summary(tmp_path, degraded=True, llm_incident_count=3)))

    assert "beeinträchtigt" in rendered
    assert "3 Aufrufe" in rendered
    assert "llm_incidents.json" in rendered


def test_a_single_incident_is_phrased_in_the_singular(tmp_path):
    rendered = _text(runs_page.lauf_kopf(_summary(tmp_path, degraded=True, llm_incident_count=1)))

    assert "ein Aufruf" in rendered


def test_a_clean_run_gets_no_warning(tmp_path):
    rendered = _text(runs_page.lauf_kopf(_summary(tmp_path)))

    assert "beeinträchtigt" not in rendered


# --- Config-Editor ---------------------------------------------------------


@pytest.mark.parametrize("mode", ["basis", "sweep", "custom"])
@pytest.mark.parametrize("tab", [value for _, value in config_editor.TABS])
def test_every_editor_tab_renders_in_every_scenario_mode(tab, mode):
    draft = initial_draft_dict()
    draft["scenario_mode"] = mode

    rendered = _text(config_editor.tab_layout(tab, draft))

    assert "konnte nicht aufgebaut werden" not in rendered


def test_sweep_mode_offers_the_preset_controls():
    """Geprüft wird die Aktion, nicht ihre Beschriftung — Texte dürfen sich ändern.

    Seit P1.1 steht die Szenario-Auswahl im geführten Ablauf, nicht in einem Tab.
    """

    from dashboard.config_catalog import list_sweep_presets
    from dashboard.web.config_editor import start_flow

    presets = list_sweep_presets()
    if not presets:
        pytest.skip("Keine Sweep-Presets unter configs/sweeps/ vorhanden.")

    draft = initial_draft_dict()
    draft["scenario_mode"] = "sweep"
    draft["sweep_id"] = presets[0].id

    rendered = _text(start_flow.layout(draft))

    # «Werte übernehmen» ist mit P7.13-U13.3 entfallen: Es schrieb in
    # `property_edits`, und das erreicht keinen Lauf mehr.
    assert "'action': 'apply-sweep'" not in rendered
    assert "'field': 'scenario_choice'" in rendered


def test_macro_tab_offers_delete_for_an_inactive_property():
    draft = initial_draft_dict()
    prop_id = next(iter(draft["property_edits"]))
    draft["property_edits"][prop_id]["is_active"] = False

    rendered = _text(config_editor.tab_layout("macro", draft))

    assert f"'type': 'cfg-prop-delete', 'prop': '{prop_id}'" in rendered


def test_every_parameter_field_has_an_explanation():
    """Kein Eingabefeld ohne Klartext — das war der Anlass für das Glossar.

    Geprüft wird das Glossar selbst: Jeder Eintrag braucht Beschriftung und
    Wirkungsbeschreibung, und die Beschriftung darf nicht der rohe Feldname
    sein (dann wäre der Eintrag nur ein Platzhalter).
    """

    from dashboard.web.config_editor import glossary

    assert glossary.PARAMS, "Glossar ist leer"
    for path, param in glossary.PARAMS.items():
        assert param.label and not param.label.startswith(path.split(".")[-1]), path
        # Der Hinweis unter dem Feld ist eine Zeile — lang genug, um etwas zu
        # sagen, kurz genug, um beim Arbeiten nicht zu stoeren.
        assert 15 < len(param.short) <= 70, f"Kurzhinweis unpassend lang: {path}"
        assert param.full_label()

    documented = {path for group in glossary.GROUPS for path in group.paths}
    assert documented <= set(glossary.PARAMS), "Doku verweist auf unbekannte Parameter"


def test_overview_summarises_the_draft_in_plain_language():
    from dashboard.web.config_editor import start_flow as overview

    draft = initial_draft_dict()
    draft.update({"rounds": 12, "run_count": 3, "mock_llm": True, "deterministic_only": False})

    sentence = overview.summary_sentence(draft)

    assert "3 Läufe" in sentence
    assert "12 Ticks" in sentence
    assert "ohne Sprachmodell" in sentence


def _preflight(draft: dict) -> str:
    from dashboard.web.config_editor import start_flow

    return _text(start_flow.preflight(draft, start_flow.errors_for(draft)))


def test_control_panel_refuses_a_config_that_cannot_run():
    """P0.3: Fehler stehen im Preflight, bevor jemand auf Start drückt."""

    draft = initial_draft_dict()
    draft["use_seed"] = True
    draft["seed"] = -1

    assert "kann so nicht starten" in _preflight(draft)


def test_control_panel_stays_quiet_for_a_healthy_config():
    assert "kann so nicht starten" not in _preflight(initial_draft_dict())


def test_control_panel_warns_about_settings_that_surprise_later():
    draft = initial_draft_dict()
    draft["no_scenarios"] = True
    draft["apply_custom_overrides"] = False
    draft["scenario_mode"] = "basis"

    rendered = _preflight(draft)

    assert "Tab «Szenario» bleibt" in rendered
    assert "wirken in diesem Lauf nicht" in rendered


def test_a_preset_run_is_not_warned_about_ignored_own_values():
    """Im Preset-Modus gelten eigene Werte bewusst nicht — das ist keine Panne."""

    draft = initial_draft_dict()
    draft["scenario_mode"] = "sweep"
    draft["apply_custom_overrides"] = False

    assert "wirken in diesem Lauf nicht" not in _preflight(draft)


def test_reset_action_returns_the_default_draft():
    draft = initial_draft_dict()
    draft["rounds"] = 999

    data, message, kind = _handle_action({"type": "cfg-action", "action": "reset"}, draft, [])

    assert data["rounds"] != 999
    assert kind == "erfolg"
    assert message


def test_add_property_rejects_an_invalid_identifier():
    free = [{"id": {"type": "cfg-free", "name": "new-prop-id"}, "value": "nicht gültig!"}]

    _, message, kind = _handle_action(
        {"type": "cfg-action", "action": "add-property"}, initial_draft_dict(), free
    )

    assert kind == "warnung"
    assert "Python-Bezeichner" in message


def test_add_segment_rejects_a_duplicate():
    draft = initial_draft_dict()
    draft["population_edits"] = [{"id": "business", "type": "boolean"}]
    free = [{"id": {"type": "cfg-free", "name": "new-segment-id"}, "value": "business"}]

    _, message, kind = _handle_action({"type": "cfg-action", "action": "add-segment"}, draft, free)

    assert kind == "warnung"
    assert "existiert bereits" in message


# --- Seiten und App --------------------------------------------------------


def test_launch_page_builds_with_the_default_draft():
    """Das Bedienfeld traegt den Start und den Stand — seit P1.6 nicht mehr den Editor."""

    rendered = _text(launch_page.layout(initial_draft_dict()))

    assert "run-start" in rendered
    assert "Rechenmodus" in rendered, "der Stand des Entwurfs fehlt"


def test_the_setup_area_builds_with_the_default_draft():
    """Der Bereich «Einrichten» traegt die Schrittfolge.

    Bis P1.8 stand hier «Alle Einstellungen» — der Abschnitt, den P1.7 in die
    Schritte 4 bis 7 aufgeloest hat. Der Test blieb trotzdem gruen, weil die
    Zeichenkette zufaellig noch in der Beschriftung einer Preset-Karte stand.
    **Ein Waechter, der aus dem falschen Grund gruen ist, ist schlechter als
    keiner** — er wiegt in Sicherheit. Geprueft wird jetzt, was der Bereich
    wirklich zusagt: die Schrittfolge mit den optionalen Schritten.
    """

    from dashboard.web.config_editor import wizard
    from dashboard.web.pages import setup as setup_page

    rendered = _text(setup_page.layout(initial_draft_dict()))

    assert "Lauf einrichten" in rendered
    assert "af-wizard" in rendered, "die Schrittfolge fehlt"
    assert "optional" in rendered, "die ueberspringbaren Schritte sind nicht als solche benannt"
    # Sieben: acht bis P1.9-W3.1 (die beiden dichten Bereiche zogen ins
    # «Modell»), sieben mit der «Ausgangslage» aus W3.3, sechs seit P2.0-C
    # -- die Faktorlage ist keine Eingabe mehr, sie entsteht im Lauf --, und
    # sieben seit P7.13-U13.1 mit «Verlaeufe» und acht seit U13.5 mit
    # «Modellannahmen» (beide von Haiko entschieden am 2026-09-15). Die Zahl steht
    # hier bewusst als Zahl: Waechst die Schrittfolge, ist das eine Entscheidung
    # und keine Nebenwirkung.
    assert len(wizard.STEPS) == 8


def test_launch_summary_describes_the_draft():
    """Seit P7.5-U5.1 in den Stand-Zeilen — die Zeile unter dem Start-Knopf ist entfallen."""

    draft = initial_draft_dict()
    draft["rounds"] = 12
    draft["run_count"] = 3

    zeilen = str(launch_page.summary_rows(draft))
    assert "12 Ticks · 1 Jahr" in zeilen
    assert "3×" in zeilen

    # Beim Vergleich beschreiben die Zeilen **nicht** mehr den Entwurf, sondern
    # den Vergleich (P1.9-W1.3): Er nimmt vom Entwurf nichts entgegen, also darf
    # dort auch keine Länge und kein Szenario aus dem Entwurf stehen.
    draft["run_all_sweeps"] = True
    zeilen = str(launch_page.summary_rows(draft))
    assert "Vergleich" in zeilen
    assert "je Szenario" in zeilen
    assert "12 Ticks" not in zeilen, (
        "Die Zeilen nennen wieder die Länge aus dem Entwurf — die verwendet der "
        "Vergleich seit W1.2 nicht."
    )


def test_app_layout_and_callbacks_are_wired():
    layout = web_app.serve_layout()

    assert _text(layout)
    assert web_app.app.callback_map


def test_result_message_covers_all_three_outcomes():
    class _Result:
        run_id = "run_1"
        batch_id = "batch_1"
        ticks_completed = 5
        total_events = 9
        artifacts: dict = {}
        sweep_batch = False
        multi_run_batch = False
        sweep_summary_path = None
        child_run_ids: tuple = ()

    single = _Result()
    assert "run_1" in _text(launch_page._result_message(single))

    multi = _Result()
    multi.multi_run_batch = True
    multi.child_run_ids = ("run_1", "run_2")
    assert "Mehrfachlauf" in _text(launch_page._result_message(multi))

    sweep = _Result()
    sweep.sweep_batch = True
    sweep.child_run_ids = ("sweeps/sweep_a",)
    sweep.sweep_summary_path = "outputs/sweeps/sweep_summary.json"
    assert "Szenario-Vergleich" in _text(launch_page._result_message(sweep))


# --- Datei-Auslieferung ----------------------------------------------------


def test_run_file_url_refuses_paths_outside_of_outputs(tmp_path):
    outsider = tmp_path / "geheim.txt"
    outsider.write_text("x", encoding="utf-8")

    assert run_file_url(outsider) == ""


def test_resolve_within_outputs_blocks_traversal():
    with pytest.raises(ValueError):
        resolve_within_outputs("../../pyproject.toml")


def test_run_file_url_builds_a_relative_route():
    from dashboard.run_browser import outputs_root

    target = outputs_root().resolve() / "run_x" / "figures" / "a.png"

    assert run_file_url(target) == "/run-file/run_x/figures/a.png"
    assert run_file_url(target, download=True).endswith("?download=1")


# --- Bausteine -------------------------------------------------------------


def test_hinweis_renders_markdown_and_plain_children():
    assert _text(ui.hinweis("**fett**", "warnung"))
    assert _text(ui.hinweis(ui.markdown("x"), "info"))


def test_draft_to_dict_is_json_serialisable():
    json.dumps(draft_to_dict(config_editor.default_config_draft()))


class TestDieErgebnisseBeantwortenVierFragen:
    """Der Schnitt der Ergebnisdarstellung folgt Fragen, nicht Datenquellen (P1.2).

    Bis zum 2026-08-30 waren es sechs Reiter nach Herkunft der Zeitreihen —
    «Yield & Markt», «Makro-Wirtschaft», «Airline-Kosten», «CIB-Faktoren» und so
    fort. Wer sie durchsah, bekam sechs Sammlungen von Kurven und keine Auskunft.
    """

    def test_exactly_four_statements_plus_the_export(self):
        from dashboard.web.views import figures

        aussagen = [(t, k) for t, k in figures.TABS if k != "png"]

        assert len(aussagen) == 4, (
            "Die Ergebnisdarstellung soll vier Fragen beantworten, gefunden: "
            f"{[t for t, _ in figures.TABS]}"
        )
        assert figures.TABS[-1][1] == "png", "Der Export steht am Ende, er ist keine Aussage"

    def test_every_statement_has_a_view(self):
        from dashboard.web.views import figures

        fehlend = [k for _, k in figures.TABS if k not in figures._VIEWS]

        assert not fehlend, f"Reiter ohne Ansicht: {fehlend}"

    def test_the_removed_views_stay_removed(self):
        """«Makro» und «CIB-Faktoren» zeigten Eingänge, keine Ergebnisse.

        Das Einkommen ist das, was man dem Lauf vorgibt; die sieben
        Faktor-Treppenlinien beantworten für sich genommen keine Frage. Sie sind
        Kontext an Aussage 4 geworden — dort unterscheiden sie die Szenarien.
        """

        from dashboard.web.views import figures

        assert not {"macro", "costs", "cib", "yield", "segments", "policies"} & set(
            figures._VIEWS
        ), "Ein Reiter der alten, nach Datenquelle geschnittenen Gliederung ist zurück"

    def test_a_lone_run_says_why_there_is_nothing_to_compare(self, tmp_path):
        """Aussage 4 braucht mehr als einen Lauf — und sagt das, statt leer zu sein."""

        from dashboard.web.views import figures

        run_dir = tmp_path / "run_allein"
        run_dir.mkdir()

        assert figures.sweep_geschwister(run_dir) == []
        gezeichnet = figures._view_szenarien(run_dir)
        text = str(gezeichnet)

        assert (
            "Szenario-Vergleich" in text
        ), "Ein einzelner Lauf bekommt keinen Hinweis, wie ein Vergleich entsteht"

    def test_sibling_scenario_runs_are_found(self, tmp_path):
        from dashboard.web.views import figures

        sweeps = tmp_path / "sweeps"
        for name in ("sweep_a", "sweep_b", "nicht_ein_sweep"):
            (sweeps / name).mkdir(parents=True)
            (sweeps / name / "run_metadata.json").write_text(
                json.dumps({"rahmen": {"id": name[-1], "quelle": "preset"}}), encoding="utf-8"
            )

        geschwister = figures.sweep_geschwister(sweeps / "sweep_a", {"a", "b"})

        assert [p.name for p in geschwister] == ["sweep_a", "sweep_b"]


# --- P5.2: Einzelsichten der Researcher-Variante ------------------------------------


def _schreibe_historie(run_dir, *, mit_grenze: bool = True, personen: int = 200) -> None:
    """Eine Personen-Historie über zwei Ticks; die Grenze bewusst ≠ WTP × Einkommen."""

    spalten = [
        "tick",
        "id",
        "age",
        "wtp_eur",
        "environmental_awareness",
        "substitution_readiness",
        "price_sensitivity",
        "income_factor",
        "saturation_level",
        "booked",
    ]
    if mit_grenze:
        spalten.append("erschwinglichkeitsgrenze_eur")
    spalten.append("business")
    zeilen = [",".join(spalten)]
    for tick in (1, 2):
        for i in range(personen):
            wtp = 100.0 + i
            werte = [
                tick,
                i,
                20 + i % 60,
                wtp,
                round((i % 10) / 10, 2),
                0.5,
                round((i % 7) / 7, 3),
                1.0,
                0.0,
                i % 3 == 0,
            ]
            if mit_grenze:
                werte.append(round(wtp * 1.2, 2))
            werte.append(i % 4 == 0)
            zeilen.append(",".join(str(w) for w in werte))
    (run_dir / "individuals_history.csv").write_text("\n".join(zeilen) + "\n", encoding="utf-8")


@pytest.fixture
def history_run(minimal_run):
    _schreibe_historie(minimal_run)
    return minimal_run


class TestSurplusPulse:
    """P5.2 (2026-09-11): der erste übernommene Block der Researcher-Variante."""

    def test_der_block_erscheint(self, history_run):
        assert "Wer sich den Flug leisten kann" in _text(
            animation.render(history_run, "run_minimal")
        )

    def test_spielraum_ist_grenze_aus_der_historie_minus_ticketpreis(self, history_run):
        frame = animation.surplus_frame(animation.load_history(history_run))

        zeile = frame[(frame["tick"] == 1) & (frame["id"] == 5)].iloc[0]

        # Ticketpreis der Runde 1 im Fixture: 101.0; Grenze im Fixture: WTP x 1,2.
        assert zeile["spielraum_eur"] == pytest.approx(105.0 * 1.2 - 101.0)

    def test_die_stichprobe_ist_fest_und_begrenzt(self, history_run):
        frame = animation.load_history(history_run)

        erste = animation.stichprobe(frame)
        zweite = animation.stichprobe(frame)

        ids = set(erste["id"].unique())
        assert ids == set(zweite["id"].unique())
        assert len(ids) == animation.STICHPROBE
        assert all(set(erste[erste["tick"] == t]["id"]) == ids for t in (1, 2))

    def test_ohne_spalte_ein_hinweis(self, minimal_run):
        _schreibe_historie(minimal_run, mit_grenze=False)

        gerendert = _text(animation.render(minimal_run, "run_minimal"))

        assert "erschwinglichkeitsgrenze_eur" in gerendert
        assert "Wer sich den Flug leisten kann:" not in gerendert


class TestSaturationSwarm:
    """P5.2 (2026-09-11): Sättigung und Wiederkehr aus der Researcher-Variante."""

    def test_der_block_erscheint(self, history_run):
        assert "Sättigung: Reisebedarf" in _text(animation.render(history_run, "run_minimal"))

    def test_reisebedarf_ist_eins_minus_saettigung(self, history_run):
        frame = animation.load_history(history_run)
        frame.loc[frame["id"] == 7, "saturation_level"] = 0.6

        bedarf = animation.bedarf_frame(frame)

        assert bedarf.loc[bedarf["id"] == 7, "reisebedarf"].tolist() == pytest.approx([0.4, 0.4])
        assert bedarf.loc[bedarf["id"] == 8, "reisebedarf"].tolist() == pytest.approx([1.0, 1.0])

    def test_ohne_saettigung_ein_hinweis(self, history_run):
        import pandas as pd

        pfad = history_run / "individuals_history.csv"
        pd.read_csv(pfad).drop(columns=["saturation_level"]).to_csv(pfad, index=False)

        gerendert = _text(animation.render(history_run, "run_minimal"))

        assert "saturation_level" in gerendert
        assert "Sättigung: Reisebedarf" not in gerendert


class TestMerkmalsSichten:
    """P5.2 (2026-09-11): die drei Merkmals-Streuungen der Researcher-Variante."""

    def test_alle_drei_bloecke_erscheinen(self, history_run):
        gerendert = _text(animation.render(history_run, "run_minimal"))

        for sicht in animation.MERKMALSICHTEN:
            assert sicht.titel in gerendert

    def test_jede_spalte_schreibt_der_lauf_wirklich(self, tmp_path):
        """Gemessen am echten Schreiber, nicht an einer Liste von Spaltennamen."""

        import csv
        import io

        from src.config_loader import load_properties_config
        from src.models.population_models import PopulationConfig
        from src.population.population_sampler import initialize_population
        from src.reporting.output_writer import append_individuals_history

        properties = load_properties_config()
        leute = initialize_population(
            properties, PopulationConfig(segments=[], total_population=5), seed=3
        )
        append_individuals_history(
            1, leute, koeffizienten=properties.booking_model, run_dir=tmp_path
        )
        kopf = next(
            csv.reader(
                io.StringIO((tmp_path / "individuals_history.csv").read_text(encoding="utf-8"))
            )
        )

        gelesen = {spalte for sicht in animation.MERKMALSICHTEN for spalte in (sicht.x, sicht.y)}
        gelesen |= {"saturation_level", "erschwinglichkeitsgrenze_eur", "wtp_eur", "booked"}
        assert gelesen <= set(kopf), f"Nicht geschrieben: {sorted(gelesen - set(kopf))}"

    def test_fehlt_eine_spalte_erscheint_ein_hinweis(self, history_run):
        import pandas as pd

        pfad = history_run / "individuals_history.csv"
        pd.read_csv(pfad).drop(columns=["income_factor"]).to_csv(pfad, index=False)

        gerendert = _text(animation.render(history_run, "run_minimal"))

        assert "`income_factor`" in gerendert


# --- Hashes hinter einer Klappe (P7.2-U2.3) -----------------------------------

from dash import html  # noqa: E402


def _text_ohne_klappen(knoten) -> str:
    """Sichtbarer Text, aber ohne alles, was in einer `html.Details` steckt.

    `_text` oben ist `str(...)` und zeigt den **ganzen** Baum — mit ihm wäre die
    Zusage «steht hinter einer Klappe» nicht messbar, weil der Inhalt der Klappe
    in der Zeichenkette ebenso auftaucht wie alles andere.
    """

    if knoten is None or isinstance(knoten, html.Details):
        return ""
    if isinstance(knoten, str):
        return knoten
    if isinstance(knoten, (list, tuple)):
        return " ".join(_text_ohne_klappen(k) for k in knoten)
    return _text_ohne_klappen(getattr(knoten, "children", None))


def _text_der_klappen(knoten) -> str:
    """Nur das, was in einer `html.Details` steht — Zusammenfassung eingeschlossen."""

    if knoten is None or isinstance(knoten, str):
        return ""
    if isinstance(knoten, (list, tuple)):
        return " ".join(_text_der_klappen(k) for k in knoten)
    if isinstance(knoten, html.Details):
        return _text(knoten)
    return _text_der_klappen(getattr(knoten, "children", None))


def _uebersicht_mit_herkunft(tmp_path):
    from dashboard.web.views import overview

    (tmp_path / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": 3,
                "ticks_max": 3,
                "compute_mode": "mock_llm",
                "seed": 42,
                "code_version": {"commit": "abcdef1234567890", "dirty": True},
                "config_fingerprint": {"properties": "0f1e2d", "agents": "9a8b7c"},
            }
        ),
        encoding="utf-8",
    )
    return overview.render(tmp_path, "run_probe")


class TestTechnischeDetails:
    """Q6: Codestand und Konfigurations-Fingerabdruck standen offen in der Übersicht.

    Beides sind Hashes. Sie beantworten «ist das derselbe Lauf wie damals» und
    keine Frage, die man beim Lesen der Ergebnisse stellt — **weg dürfen sie
    trotzdem nicht**: Ein Lauf ohne nachvollziehbare Herkunft ist genau der
    Befund, den P0.6 abgeräumt hat.
    """

    def test_the_hashes_stand_behind_a_disclosure(self, tmp_path):
        gerendert = _uebersicht_mit_herkunft(tmp_path)

        offen = _text_ohne_klappen(gerendert)
        verborgen = _text_der_klappen(gerendert)

        assert "Technische Details" in verborgen
        assert "0f1e2d" in verborgen, "Der Fingerabdruck steht nicht in der Klappe"
        assert "abcdef12" in verborgen, "Der Codestand steht nicht in der Klappe"
        assert "0f1e2d" not in offen, "Der Fingerabdruck steht weiterhin offen"
        assert "abcdef12" not in offen, "Der Codestand steht weiterhin offen"

    def test_the_overview_still_answers_its_own_questions(self, tmp_path):
        """Rahmen, Rechenmodus und Seed bleiben offen — sie sind die Lesehilfe."""

        offen = _text_ohne_klappen(_uebersicht_mit_herkunft(tmp_path)).lower()

        # Die Kachel setzt ihre Beschriftung in Grossbuchstaben — geprueft wird,
        # was dasteht, nicht wie es gesetzt ist.
        assert "rechenmodus" in offen
        assert "seed" in offen
        assert "42" in offen

    def test_the_identifier_stands_behind_the_disclosure(self, tmp_path):
        """D6: Die Kennung ist ein Ablageort und steht bei den Hashes, nicht offen."""

        gerendert = _uebersicht_mit_herkunft(tmp_path)

        assert "run_probe" in _text_der_klappen(gerendert)
        assert "run_probe" not in _text_ohne_klappen(gerendert)

    def test_the_measurement_separates_inside_from_outside(self, tmp_path):
        """Gegen die eigene Blindheit: Die beiden Texte sind wirklich verschieden."""

        probe = html.Div(["draussen", html.Details([html.Summary("Titel"), "drinnen"])])

        assert "drinnen" not in _text_ohne_klappen(probe)
        assert "draussen" in _text_ohne_klappen(probe)
        assert "drinnen" in _text_der_klappen(probe)


class TestDerLaufKopf:
    """P7.3-U3.2: einmal, kompakt, im Leitstand und in «Ergebnisse».

    Unter «Ergebnisse» standen Datum, Ticks, Modell, Warnbanner und die
    Zusammenfassung des Szenarios über jeder der sieben Ansichten (R1), und die
    Zusammenfassung stand in «Szenario» ein zweites Mal. Im Leitstand stand der
    Name des gezeigten Laufs nirgends (Q5).
    """

    def test_one_line_names_the_run_and_how_it_was_computed(self, tmp_path):
        summary = _summary(tmp_path, rahmen_name="Business as Usual", compute_mode="mock_llm")

        text = _text(runs_page.lauf_kopf(summary))

        assert "Business as Usual" in text
        assert "Ohne Sprachmodell" in text
        assert "run_test" not in text, "Die Kennung gehört unter «Technische Details»"

    def test_the_warning_is_visible_and_only_its_explanation_folds(self, tmp_path):
        kopf = runs_page.lauf_kopf(_summary(tmp_path, degraded=True, llm_incident_count=2))

        assert "beeinträchtigt" in _text_ohne_klappen(kopf)
        assert "llm_incidents.json" in _text_der_klappen(kopf)
        assert "llm_incidents.json" not in _text_ohne_klappen(kopf)

    def test_the_scenario_summary_is_not_repeated(self, tmp_path):
        """R1: Sie steht in «Szenario» — über jeder Ansicht stand sie ein zweites Mal."""

        summary = _summary(tmp_path, scenario_summary="Drei explorative Pfade.")

        assert "Drei explorative Pfade" not in _text(runs_page.lauf_kopf(summary))

    def test_the_control_room_carries_the_run_header(self):
        assert runs_page.LAUF_KOPF_LEITSTAND in str(web_app.serve_layout())

    def test_one_callback_fills_both_headers(self):
        """Derselbe Auslöser, dieselbe Rechnung — kein zweiter Rundlauf je Laufwechsel."""

        schluessel = [k for k in web_app.app.callback_map if "runs-meta.children" in k]

        assert len(schluessel) == 1, schluessel
        assert f"{runs_page.LAUF_KOPF_LEITSTAND}.children" in schluessel[0]
