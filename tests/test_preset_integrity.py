"""Ein gewähltes Preset gilt unvermischt — auf beiden Wegen dasselbe (P1.1).

Bis P1.1 wendete `prepare_simulation_state` erst das Preset an und legte danach
den Entwurf darüber. Weil `apply_custom_overrides` per Default an ist und der
Entwurf die Datei-Defaults aus `properties.json` mitführt, drehte die zweite
Runde die erste still zurück: «Business as Usual» verspricht eine konstante
CO₂-Abgabe von 50 und rechnete im Dashboard trotzdem mit dem Sprung auf 120 in
Tick 15 — also mit strenger Regulierung, dem Gegenteil dessen, wofür das
Szenario steht. Über die CLI (`run_single_sweep`) stimmte es; nur dieser Pfad
nicht.

Geprüft wird deshalb **jede** Datei unter `configs/sweeps/`, nicht eine Auswahl:
Eine gepflegte Liste fängt einen Rückfall an bekannter Stelle, nie ein Preset,
das später dazukommt. Dieselbe Lehre wie beim Kontextparameter-Sweep aus P0.7.
"""

from __future__ import annotations

import pytest

from dashboard.config_catalog import (
    SWEEPS_DIR,
    build_custom_sweep_from_draft,
    default_config_draft,
    list_sweep_presets,
    prepare_simulation_state,
)
from src.config_loader import build_initial_state
from src.orchestration.scenario_sweeps import apply_sweep_overrides, load_sweep_config

PRESET_IDS = [preset.id for preset in list_sweep_presets()]


def _fingerprint(state) -> dict:
    """Was ein Preset festlegt: Systemgrößen, Faktorlage, Startpreis.

    Die Uhr bleibt bewusst draußen — die Länge des Laufs ist im geführten
    Ablauf eine sichtbare Entscheidung und darf das Preset überstimmen.
    """

    return {
        "properties": {
            prop.id: prop.trajectory.model_dump(mode="json") if prop.trajectory else None
            for prop in state.properties.system_properties
        },
        "factors": {fid: factor.current_state for fid, factor in state.environment.factors.items()},
        "base_price": state.properties.price_model.base_price,
    }


def _as_the_cli_runs_it(preset_id: str) -> dict:
    return _fingerprint(
        apply_sweep_overrides(
            build_initial_state(), load_sweep_config(SWEEPS_DIR / f"{preset_id}.json")
        )
    )


def _as_the_dashboard_runs_it(preset_id: str) -> dict:
    draft = default_config_draft()
    draft.scenario_mode = "sweep"
    draft.sweep_id = preset_id
    return _fingerprint(prepare_simulation_state(draft))


@pytest.mark.skipif(not PRESET_IDS, reason="Keine Presets unter configs/sweeps/ vorhanden.")
@pytest.mark.parametrize("preset_id", PRESET_IDS)
def test_a_preset_reaches_the_run_unchanged(preset_id):
    """Dashboard und CLI müssen aus demselben Preset denselben Zustand bauen."""

    assert _as_the_dashboard_runs_it(preset_id) == _as_the_cli_runs_it(preset_id)


@pytest.mark.skipif(not PRESET_IDS, reason="Keine Presets unter configs/sweeps/ vorhanden.")
@pytest.mark.parametrize("preset_id", PRESET_IDS)
def test_the_length_stays_the_users_decision(preset_id):
    """Das Preset legt alles fest — außer, wie lange gerechnet wird."""

    draft = default_config_draft()
    draft.scenario_mode = "sweep"
    draft.sweep_id = preset_id
    draft.rounds = 7

    assert prepare_simulation_state(draft).clock.max_ticks == 7


def test_the_comparison_would_notice_the_old_behaviour():
    """Kontrolle: Der Vergleich oben prüft wirklich etwas.

    Nachgestellt wird der Stand vor P1.1 — Preset anwenden, dann den Entwurf
    darüberlegen. Findet dieser Test keinen Unterschied, wären die Tests oben
    wertlos, weil sie einen Fehler prüften, den es gar nicht geben kann.
    """

    if "business_as_usual" not in PRESET_IDS:
        pytest.skip("Preset «business_as_usual» ist nicht vorhanden.")

    draft = default_config_draft()
    state = apply_sweep_overrides(
        build_initial_state(), load_sweep_config(SWEEPS_DIR / "business_as_usual.json")
    )
    wie_frueher = _fingerprint(apply_sweep_overrides(state, build_custom_sweep_from_draft(draft)))

    assert wie_frueher != _as_the_cli_runs_it("business_as_usual")


def test_business_as_usual_keeps_its_carbon_tax_flat():
    """Der Befund selbst, in der Sprache des Szenarios.

    Das Preset trägt dazu einen eigenen Meilenstein («Kein CO₂-Anstieg bei Tick
    15»). Er war über das Dashboard verletzt, ohne dass irgendwo etwas rot wurde.
    """

    if "business_as_usual" not in PRESET_IDS:
        pytest.skip("Preset «business_as_usual» ist nicht vorhanden.")

    trajektorie = _as_the_dashboard_runs_it("business_as_usual")["properties"]["carbon_tax_level"]
    werte = {rule["effect"]["value"] for rule in trajektorie["rules"]}

    assert werte == {50.0}, f"CO₂-Abgabe springt trotz «Business as Usual»: {sorted(werte)}"
