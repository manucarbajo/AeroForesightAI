"""Jede Ansicht der Dash-App muss sich bauen lassen — auch aus Trümmern.

Ein Run-Verzeichnis kann unvollständig sein (abgebrochener Lauf, alter Run
ohne `timeseries/`). Streamlit hat solche Fälle mit einem Hinweis abgefangen;
diese Tests halten fest, dass die Dash-Ansichten das ebenfalls tun, statt eine
Exception bis in den Callback durchzureichen.
"""

from __future__ import annotations

import json

import pytest

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


# --- Config-Editor ---------------------------------------------------------


@pytest.mark.parametrize("mode", ["basis", "sweep", "custom"])
@pytest.mark.parametrize("tab", [value for _, value in config_editor.TABS])
def test_every_editor_tab_renders_in_every_scenario_mode(tab, mode):
    draft = initial_draft_dict()
    draft["scenario_mode"] = mode

    rendered = _text(config_editor.tab_layout(tab, draft))

    assert "konnte nicht aufgebaut werden" not in rendered


def test_sweep_mode_offers_the_preset_controls():
    draft = initial_draft_dict()
    draft["scenario_mode"] = "sweep"

    rendered = _text(config_editor.tab_layout("experiment", draft))

    assert "Szenario-Parameter übernehmen" in rendered
    assert "apply-sweep" in rendered


def test_macro_tab_offers_delete_for_an_inactive_property():
    draft = initial_draft_dict()
    prop_id = next(iter(draft["property_edits"]))
    draft["property_edits"][prop_id]["is_active"] = False

    rendered = _text(config_editor.tab_layout("macro", draft))

    assert "Property dauerhaft löschen" in rendered


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
    rendered = _text(launch_page.layout(initial_draft_dict()))

    assert "Simulation starten" in rendered
    assert "run-start" in rendered


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
