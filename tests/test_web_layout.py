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

    assert "Run-Verzeichnis fehlt" in _text(runs_page.render_tab("overview", selection))


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

    rendered = _text(runs_page._meta(_summary(tmp_path, degraded=True, llm_incident_count=3)))

    assert "beeinträchtigt" in rendered
    assert "3 Aufrufe" in rendered
    assert "llm_incidents.json" in rendered


def test_a_single_incident_is_phrased_in_the_singular(tmp_path):
    rendered = _text(runs_page._meta(_summary(tmp_path, degraded=True, llm_incident_count=1)))

    assert "ein Aufruf" in rendered


def test_a_clean_run_gets_no_warning(tmp_path):
    rendered = _text(runs_page._meta(_summary(tmp_path)))

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

    assert "'action': 'apply-sweep'" in rendered
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
    assert kind == "success"
    assert message


def test_apply_sweep_action_takes_over_the_preset():
    from dashboard.config_catalog import list_sweep_presets

    presets = list_sweep_presets()
    if not presets:
        pytest.skip("Keine Sweep-Presets unter configs/sweeps/ vorhanden.")

    draft = initial_draft_dict()
    draft["sweep_id"] = presets[0].id

    data, message, kind = _handle_action({"type": "cfg-action", "action": "apply-sweep"}, draft, [])

    assert kind == "success"
    assert presets[0].name in message
    assert data["rounds"] == presets[0].max_ticks


def test_add_property_rejects_an_invalid_identifier():
    free = [{"id": {"type": "cfg-free", "name": "new-prop-id"}, "value": "nicht gültig!"}]

    _, message, kind = _handle_action(
        {"type": "cfg-action", "action": "add-property"}, initial_draft_dict(), free
    )

    assert kind == "warning"
    assert "Python-Bezeichner" in message


def test_add_segment_rejects_a_duplicate():
    draft = initial_draft_dict()
    draft["population_edits"] = [{"id": "business", "type": "boolean"}]
    free = [{"id": {"type": "cfg-free", "name": "new-segment-id"}, "value": "business"}]

    _, message, kind = _handle_action({"type": "cfg-action", "action": "add-segment"}, draft, free)

    assert kind == "warning"
    assert "existiert bereits" in message


def test_reload_factors_reads_the_configured_file():
    data, _, kind = _handle_action(
        {"type": "cfg-action", "action": "reload-factors"}, initial_draft_dict(), []
    )

    assert kind == "success"
    assert data["factor_states"]


# --- Seiten und App --------------------------------------------------------


def test_launch_page_builds_with_the_default_draft():
    """Das Bedienfeld traegt den Start und den Stand — seit P1.6 nicht mehr den Editor."""

    rendered = _text(launch_page.layout(initial_draft_dict()))

    assert "run-start" in rendered
    assert "Rechenmodus" in rendered, "der Stand des Entwurfs fehlt"


def test_the_setup_area_builds_with_the_default_draft():
    from dashboard.web.pages import setup as setup_page

    rendered = _text(setup_page.layout(initial_draft_dict()))

    assert "Lauf einrichten" in rendered
    assert "Alle Einstellungen" in rendered


def test_launch_summary_describes_the_draft():
    draft = initial_draft_dict()
    draft["rounds"] = 12
    draft["run_count"] = 3

    assert "Ticks: 12" in launch_page._summary(draft)
    assert "3 Läufe" in launch_page._summary(draft)

    draft["run_all_sweeps"] = True
    assert "alle Szenario-Presets" in launch_page._summary(draft)


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
    assert "Multi-Run" in _text(launch_page._result_message(multi))

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


def test_alert_renders_markdown_and_plain_children():
    assert _text(ui.alert("**fett**", "warning"))
    assert _text(ui.alert(ui.markdown("x"), "info"))


def test_draft_to_dict_is_json_serialisable():
    json.dumps(draft_to_dict(config_editor.default_config_draft()))
